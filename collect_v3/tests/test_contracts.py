import io,json,logging,os,signal,sqlite3,subprocess,sys,time,uuid
from pathlib import Path
import pytest
from PIL import Image
from collect_v3.common import read_json,write_json,write_rows,rows,sha_bytes,ScrubFilter,scrub
from collect_v3.config import config,SPECS
from collect_v3.ledger import Ledger,BudgetExceeded,UncertainRead
from collect_v3.reader import read_once,BINDING
from collect_v3.transport import HostBucket,HTTP,AccessStopped,retry_seconds,NetworkDisabled
from collect_v3.offline import no_network,VirtualClock
from collect_v3.exclusions import Exclusions,title_year
from collect_v3.cards import cards,draw
from collect_v3.runner import gate_sources,finalize
from collect_v3.vendor.classify import inspect
from collect_v3.vendor.conventions import apply_conventions,roman_convention
from collect_v3.routes.providers import Routes,iiif_images

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get('COLLECT_V3_TEST_OUTPUT',str(ROOT/'docs/harvest/collect_v3/test_evidence')))
PROJECTS=Path(os.environ.get('COLLECT_V3_PROJECTS_ROOT',str(ROOT.parent)))

def test_network_default_off(tmp_path):
    with no_network(),pytest.raises(NetworkDisabled):HTTP(tmp_path).get('https://example.invalid/a')
    p=subprocess.run([sys.executable,str(ROOT/'collect_v3/run.py'),'--output-root',str(tmp_path),'run','--tranche','W1','--sources','ia_poly1850'],capture_output=True,text=True)
    assert p.returncode and 'network_enabled is false' in p.stderr

def test_rate_real_wall_clock(tmp_path):
    h=HTTP(tmp_path,sender=lambda u:(200,{},b'fixture'))
    for _ in range(3):h.raw('https://one.example.invalid/page')
    starts=[r['start'] for r in h.events];spacing=[b-a for a,b in zip(starts,starts[1:])]
    assert min(spacing)>=1.
    OUT.mkdir(parents=True,exist_ok=True);write_json(OUT/'rate_receipt.json',dict(status='ok',clock='real wall clock',requests=h.events,spacing_seconds=spacing,minimum_spacing_seconds=min(spacing),network=False))
    with pytest.raises(ValueError):HostBucket(tmp_path,rate=1.01)

def test_rate_cross_instance_retry_after(tmp_path):
    vc=VirtualClock();a=HostBucket(tmp_path,clock=vc.time,sleep=vc.sleep);b=HostBucket(tmp_path,clock=vc.time,sleep=vc.sleep)
    first=a.acquire('same');a.defer('same',7);second=b.acquire('same');assert second-first>=7
    assert retry_seconds('120')==120
    assert retry_seconds('Wed, 21 Oct 2015 07:28:00 GMT',now=1445412470)==10

def test_robots_redirect_and_access_stop(tmp_path):
    vc=VirtualClock();events=[]
    def sender(u):
        events.append(u)
        if u.endswith('/robots.txt'):return 200,{},b'User-agent: *\nDisallow: /private/\nAllow: /private/public$\n'
        if u.endswith('/start'):return 302,{'Location':'https://b.invalid/private/no'},b''
        return 200,{},b'ok'
    h=HTTP(tmp_path,sender=sender,bucket=HostBucket(tmp_path/'hosts',clock=vc.time,sleep=vc.sleep))
    assert h.get('https://a.invalid/private/public')==b'ok'
    with pytest.raises(AccessStopped):h.get('https://a.invalid/start')
    assert 'https://b.invalid/robots.txt' in events and 'https://b.invalid/private/no' not in events

def test_429_persists_retry_after(tmp_path):
    vc=VirtualClock();h=HTTP(tmp_path,sender=lambda u:(200,{},b'User-agent: *\nAllow: /') if u.endswith('/robots.txt') else (429,{'Retry-After':'8'},b''),bucket=HostBucket(tmp_path/'hosts',clock=vc.time,sleep=vc.sleep))
    with pytest.raises(AccessStopped):h.get('https://a.invalid/p')
    last=vc.now;assert h.bucket.acquire('a.invalid')>=last+8

def test_hard_caps_and_no_duplicate_ledger(tmp_path):
    ledger=Ledger(tmp_path/'ledger.sqlite3',{'W1':.003,'W2':.0015})
    ledger.reserve('a','p1','W1');ledger.reserve('a','p1','W1');ledger.reserve('b','p2','W1')
    with pytest.raises(BudgetExceeded):ledger.reserve('c','p3','W1')
    ledger.reserve('c','p3','W2')
    with pytest.raises(BudgetExceeded):ledger.reserve('d','p4','W2')
    assert len(ledger.rows())==3;ledger.close()

def test_uncertain_paid_read_never_retried(tmp_path):
    class Reader:
        calls=0
        def read(self,p):self.calls+=1;raise TimeoutError('response lost')
    reader=Reader();ledger=Ledger(tmp_path/'ledger.sqlite3',{'W1':2.1,'W2':8});page={'id':'p','image_sha256':'hash','image':'unused'}
    with pytest.raises(TimeoutError):read_once(ledger,reader,page,'W1',tmp_path/'raw')
    with pytest.raises(UncertainRead):read_once(ledger,reader,page,'W1',tmp_path/'raw')
    assert reader.calls==1 and len(ledger.rows())==1;ledger.close()

def test_real_sigkill_resume():
    dest=OUT/'resume';dest.mkdir(parents=True,exist_ok=True)
    if (dest/'kill_ready.json').exists():pytest.skip('resume evidence exists; use a fresh test output for another kill')
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OMP_THREAD_LIMIT':'1','PYTHONPATH':str(ROOT)}
    cmd=[sys.executable,'-m','collect_v3.tests.resume_worker',str(PROJECTS),str(dest)]
    with (dest/'worker.log').open('w') as log:
        child=subprocess.Popen(cmd+['pause'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        deadline=time.monotonic()+90
        while not (dest/'kill_ready.json').exists() and child.poll() is None and time.monotonic()<deadline:time.sleep(.05)
        try:
            assert (dest/'kill_ready.json').exists(), 'worker did not reach kill boundary; inspect worker.log'
            os.kill(child.pid,signal.SIGKILL);child.wait(timeout=10);assert child.returncode==-signal.SIGKILL
        finally:
            if child.poll() is None:child.kill();child.wait()
        before=rows(dest/'mock_reads.jsonl');assert len(before)==2
        result=subprocess.run(cmd+['resume'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=90)
        assert result.returncode==0
        result2=subprocess.run(cmd+['resume'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=90);assert result2.returncode==0
    reads=rows(dest/'mock_reads.jsonl');ledger=rows(dest/'ledger.jsonl')
    assert len(reads)==len({r['hash'] for r in reads})==3
    assert len(ledger)==len({r['image_hash'] for r in ledger})==3
    assert len(list((dest/'W1/pages').glob('*.json')))==3
    write_json(OUT/'resume_receipt.json',dict(status='ok',kill_signal='SIGKILL',boundary='second response saved atomically, ledger not yet completed',reads_before_kill=2,reads_after_two_resumes=len(reads),unique_reads=3,ledger_rows=3,duplicate_reads=0,duplicate_ledger_rows=0,completed_pages=3))

def test_credential_scrubber_all_outputs(tmp_path,monkeypatch):
    secret='FAKE-'+uuid.uuid4().hex;monkeypatch.setenv('COLLECT_V3_ACCESS_TOKEN',secret)
    buf=io.StringIO();handler=logging.StreamHandler(buf);handler.addFilter(ScrubFilter());log=logging.getLogger('scrub-test');log.handlers=[handler];log.propagate=False;log.setLevel(logging.INFO)
    log.error('Authorization: Bearer %s',secret)
    try:raise ValueError(secret)
    except ValueError:log.exception('request failed '+secret)
    assert secret not in buf.getvalue()
    write_json(tmp_path/'error.json',{'error':scrub('token '+secret)})
    (tmp_path/'collector.log').write_text(buf.getvalue())
    # Exercise the detached supervisor's scrubber with an actual child process.
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
    run=subprocess.run([sys.executable,str(ROOT/'collect_v3/detach.py'),str(tmp_path),str(ROOT),'run','--tranche','W1','--sources',secret],cwd=ROOT,env=env,capture_output=True,text=True,timeout=20)
    assert secret not in run.stdout+run.stderr
    inspected=0
    for p in [*tmp_path.rglob('*'),*OUT.rglob('*')]:
        if p.is_file():assert secret.encode() not in p.read_bytes(),str(p);inspected+=1
    write_json(OUT/'credential_scrub_receipt.json',dict(status='ok',secret_origin='fake environment token generated at test runtime',files_scanned=inspected,token_found=False,logs_filtered=True,traceback_filtered=True,detached_supervisor_exercised=True))

def test_serbian_codec_opt_in():
    text='јћњљђџЈЋЊЉЂЏ'
    assert not inspect(text,.99)['codec_v1_pass']
    assert inspect(text,.99,serbian=True)['codec_v1_pass']
    assert config()['serbian_codec']

def test_pinned_binding_and_options():
    assert BINDING['processor']=='9a98b7aca3c19561'
    assert BINDING['options']=={'ocrConfig':{'enableSymbol':True,'hints':{'languageHints':[]}}}

def test_exclusions_keys_and_no_container_false_positive():
    ex=Exclusions();ex.add(dict(provider_id='abc',title='Τίτλος',year=1900,pdf_sha256='hash'))
    assert ex.match({'id':'abc'})==['provider_id']
    assert ex.resolve({'title':'ΤΙΤΛΟΣ','year':1900})[0]=='quarantined'
    assert not ex.match({'title':'Τίτλος','year':1901})
    assert ex.match({'pdf_sha256':'hash'})==['media_hash']
    ex=Exclusions();ex.add(dict(id='pdf1',catalogue_url='https://x/container',url='https://x/download/pdf1.pdf'))
    assert not ex.match(dict(id='pdf2',catalogue_url='https://x/container',url='https://x/download/pdf2.pdf'))

def test_gate_closed_by_default(tmp_path):
    with pytest.raises(ValueError):gate_sources(tmp_path/'c1_gate.json',['nlg'])
    write_json(tmp_path/'c1_gate.json',{'tranche':'W1','sources':{'nlg':{'passed':True,'classes':{'poly1850':True,'mixed_greek_latin':False}}}})
    assert gate_sources(tmp_path/'c1_gate.json',['nlg'])['nlg']['passed']
    with pytest.raises(ValueError):gate_sources(tmp_path/'c1_gate.json',['serbia'])

def test_card_uniformity_shape_shortfalls(tmp_path):
    pool=[{'id':str(i),'label':'x'*(1+i)} for i in range(200)]
    chosen=draw(pool,100,'seed');assert chosen==draw(pool,100,'seed')
    assert set(r['id'] for r in chosen)!=set(r['id'] for r in sorted(pool,key=lambda r:len(r['label']))[-100:])
    image=tmp_path/'crop.png';Image.new('L',(10,10),255).save(image);h=__import__('collect_v3.common',fromlist=['sha']).sha(image)
    rr=[dict(id=f'l{i}',page_id='p',source='nlg',primary_class='poly1850',usable_final=True,crop=str(image),crop_sha256=h,label_after_conventions=str(i),screen_merged=True,tags=['marks_correction_required'],source_marks={'rate':.9},fixed_label=str(i),track='collect_v3',crop_bbox=[0,i*15,100,i*15+10],page_median_row_height=10) for i in range(25)]
    write_rows(tmp_path/'W1/features.jsonl',rr);write_json(tmp_path/'W1/pages/p.json',dict(id='p',source='nlg',status='completed',item='a',page=1,preview=str(image),preview_sha256=h))
    report=cards(config(output_root=str(tmp_path)),'W1');assert report[0]['shortfall']==75
    public=rows(tmp_path/'W1/c1/nlg__poly1850/cards.jsonl');assert set(public[0])=={'card_id','crop','google_text','word_scripts'}
    assert report[-1]['shortfall']==0 and report[-1]['all_pages_small_pool']

def test_routes_ia_and_iiif_offline(tmp_path):
    im=io.BytesIO();Image.new('L',(4000,2000),255).save(im,format='JPEG')
    manifest={'sequences':[{'canvases':[{'images':[{'resource':{'@id':'https://iiif.invalid/p.jpg'}}]}]}]}
    mapping={'https://archive.org/metadata/book':json.dumps({'metadata':{'imagecount':4},'files':[]}).encode(),'https://archive.org/download/book/page/n2.jpg':im.getvalue(),'https://iiif.invalid/manifest':json.dumps(manifest).encode(),'https://iiif.invalid/p.jpg':im.getvalue()}
    def sender(url):return (200,{},b'User-agent: *\nAllow: /') if url.endswith('/robots.txt') else (200,{},mapping[url])
    vc=VirtualClock();http=HTTP(tmp_path,sender=sender,bucket=HostBucket(tmp_path/'hosts',clock=vc.time,sleep=vc.sleep));routes=Routes(http,tmp_path)
    with no_network():
        item={'provider':'ia','id':'book','route':'ia'};rec={'id':'p','source':'ia_poly1850','item':'book','item_record':item,'item_pages':1,'page':2,'page_slot':0,'page_seed':'seed'}
        page=routes.fetch(rec);assert max(page['width'],page['height'])<=3500 and page['page']==2
        item={'provider':'bsb','id':'bsb1','route':'iiif','manifest_url':'https://iiif.invalid/manifest'};rec.update(id='q',item='bsb1',source='bsb_poly1850',item_record=item,page=1)
        page=routes.fetch(rec);assert page['page']==1
    assert iiif_images(manifest)==['https://iiif.invalid/p.jpg']

def test_manifest_totals_disjoint_uniform_and_excluded():
    base=ROOT/'docs/harvest/collect_v3';w1=rows(base/'W1_manifest.jsonl');w2=rows(base/'W2_manifest.jsonl');allrows=w1+w2
    assert len(w1)==1370 and len(w2)==5480
    assert not {r['id'] for r in w1}&{r['id'] for r in w2}
    ex=Exclusions(read_json(base/'exclusions_index.json'))
    byitem={};cohorts={}
    for r in allrows:
        key=(r['item_record']['provider'],r['item']);byitem.setdefault(key,[]).append(r);cohorts.setdefault(r['source'],[]).append(r)
        assert not ex.match(r['item_record'],r['item_record']['provider'])
        if r['source'].startswith('gazette'):
            assert r['source']=='gazette_modern' and 1982<=r['item_record']['year']<=1990
    assert max(map(len,byitem.values()))<=40
    for key,rs in byitem.items():
        known=[r['page'] for r in rs if r['page'] is not None];assert len(known)==len(set(known))
    for s,spec in SPECS.items():assert len(cohorts[s])==spec[0] and sum(r['tranche']=='W1' for r in cohorts[s])==spec[0]//5
    assert sum(r['projected_micro_usd'] for r in w1)==2055000

def test_screen_flag_gates_nothing_and_dedupe(tmp_path):
    base=dict(id='a',source='nlg',primary_class='poly1850',page_id='p',track='collect_v3',crop_bbox=[0,0,100,10],page_median_row_height=10,fixed_label='κανονική πλήρης γραμμή',tags=['marks_correction_required'],tranche='W1',fixed_usable=True,screen_merged=True,crop_sha256='hash')
    duplicate=dict(base,id='b')
    write_json(tmp_path/'W1/pages/p.json',dict(status='completed',rows=[base,duplicate]))
    result=finalize(tmp_path,'W1');assert result[0]['usable_final'] is True and result[0]['screen_merged'] is True
    assert result[1]['duplicate_exact'] and not result[1]['usable_final']

def test_conventions_frozen_cross_page_fragment_evidence():
    a=dict(id='a',track='x',page_id='p',fixed_label='Στην μετάφρα',crop_bbox=[0,0,200,10],page_median_row_height=10)
    b=dict(id='b',track='x',page_id='p',fixed_label='ση του βιβλίου',crop_bbox=[0,12,200,22],page_median_row_height=10)
    context={'occurrences':{'μεταφραση':[['x','q'],['x','r']]},'nonfinal':{}}
    apply_conventions([a,b],context);assert 'dropped_line_end_hyphen' in a['text_exclusions']
    text,fixes,ambiguous=roman_convention('Τόμος ΙV');assert fixes and text.endswith('IV') and not ambiguous
    text,fixes,ambiguous=roman_convention('IΛ');assert ambiguous

def test_pdf_ojs_gazette_routes_and_short_bounds(tmp_path):
    import pypdfium2 as pdfium
    doc=pdfium.PdfDocument.new();doc.new_page(200,300);pdfpath=tmp_path/'small.pdf';doc.save(pdfpath);doc.close();pdf=pdfpath.read_bytes()
    mapping={'https://ojs.invalid/issue/view/1':b'<a href="/article/view/2/3">PDF</a>',
             'https://ojs.invalid/article/view/2/3':b'<a href="/article/download/2/3">download</a>',
             'https://ojs.invalid/article/download/2/3':pdf,
             'https://leky.invalid/book.pdf':pdf,
             'https://search.et.gr/item':b'<html>Official catalogue</html>',
             'https://ia37rg02wpsa01.blob.core.windows.net/fek/01/1910/19100100001.pdf':pdf}
    def sender(url):return (200,{},b'User-agent: *\nAllow: /') if url.endswith('/robots.txt') else (200,{},mapping[url])
    vc=VirtualClock();http=HTTP(tmp_path,sender=sender,bucket=HostBucket(tmp_path/'hosts',clock=vc.time,sleep=vc.sleep));route=Routes(http,tmp_path)
    with no_network():
        item=dict(provider='kosmopolis',id='issue',route='ojs',catalogue_url='https://ojs.invalid/issue/view/1');resolved=route.resolve(item);assert resolved['page_count']==1
        rec=dict(id='ojs',source='kosmopolis',item='issue',item_record=item,item_pages=1,page=None,page_slot=0,page_seed='seed')
        page=route.fetch(rec);assert page['pdf_sha256']==sha_bytes(pdf)
        item=dict(provider='lekythos',id='book',route='pdf',url='https://leky.invalid/book.pdf');rec.update(id='pdf',source='lekythos',item='book',item_record=item);assert route.fetch(rec)['page']==1
        item=dict(provider='gazette',id='19100100001',route='gazette',url='https://ia37rg02wpsa01.blob.core.windows.net/fek/01/1910/19100100001.pdf',catalogue_url='https://search.et.gr/item',official_catalogue_id='123',metadata_sha256='binding');rec.update(id='gaz',source='gazette_poly1900',item=item['id'],item_record=item);assert route.fetch(rec)['page']==1
        assert next(i for i,r in enumerate(http.events) if r['url']=='https://search.et.gr/item')<next(i for i,r in enumerate(http.events) if r['url'].endswith('19100100001.pdf'))
        with pytest.raises(ValueError,match='shortfall'):route.leaf(dict(item_pages=2,page=None,page_seed='seed',page_slot=1),resolved)

def test_parity_receipt():
    p=Path(os.environ.get('COLLECT_V3_REPLAY_ROOT',str(ROOT/'docs/harvest/collect_v3/rev2_verified_replay')))/'parity_details.json'
    if not p.exists():pytest.skip('offline replay has not completed')
    r=read_json(p);assert not r['differences'];assert r['lines']>=1000 and len(r['fields'])>=40

def test_ledger_is_reserved_before_reader(tmp_path):
    ledger=Ledger(tmp_path/'ledger.sqlite3',{'W1':2.1,'W2':8})
    class Reader:
        def read(self,image):
            assert ledger.get('h')['state']=='request_started'
            return {'document':{'text':'','pages':[{}]}}
    read_once(ledger,Reader(),dict(id='p',image_sha256='h',image='unused'),'W1',tmp_path/'responses')
    assert ledger.get('h')['state']=='response_saved';ledger.close()

def test_source_marks_policy_in_replay():
    from collect_v3.config import POLY,marks
    base=Path(os.environ.get('COLLECT_V3_REPLAY_ROOT',str(ROOT/'docs/harvest/collect_v3/rev2_verified_replay')))/'W1/pages'
    for p in base.glob('*.json'):
        for r in read_json(p)['rows']:
            gazette_polytonic=r.get('gazette_polytonic',False)
            assert ('marks_correction_required' in r['tags'])==(r['source'] in POLY or gazette_polytonic)
            if gazette_polytonic:
                assert r['source_marks']['rate'] is None and 'gazette_polytonic_failed_v2' in r['tags']
                assert not r['candidate_usable'] and not r['usable_final']
            else:assert r['source_marks']==marks(r['source'])

def test_bound_manifest_and_pruning_in_replay():
    base=Path(os.environ.get('COLLECT_V3_REPLAY_ROOT',str(ROOT/'docs/harvest/collect_v3/rev2_verified_replay')))
    assert len(list((base/'cache/pages').glob('*.jpg')))==30
    assert len(list((base/'cache/http').glob('*.body')))==30
    assert read_json(base/'OFFLINE_FIXTURE_ONLY.json')['live_launch_allowed'] is False
    assert len(rows(base/'ledger.jsonl'))==30

def test_short_items_resume_same_seeded_stream(tmp_path):
    from collect_v3.resolution import resolve_source
    from collect_v3.config import SPECS
    order=[]
    for i in range(30):
        order.append(dict(item_record=dict(id=f'b{i}',provider='lekythos',route='pdf'),item_rank=i,quota=40,page_seed=f'seed:b{i}',rights={'status':'fixture'}))
    write_rows(tmp_path/'item_draws/lekythos.jsonl',order)
    class ShortItems:
        calls=[]
        def resolve(self,item):self.calls.append(item['id']);return dict(item,page_count=10)
    route=ShortItems()
    w1=resolve_source(tmp_path,'lekythos','W1',route,20261016)
    assert len(w1)==58 and len(route.calls)==29
    assert resolve_source(tmp_path,'lekythos','W1',route,20261016)==w1 and len(route.calls)==29
    w2=resolve_source(tmp_path,'lekythos','W2',route,20261016)
    assert len(w2)==232 and len(route.calls)==29
    assert not {r['id'] for r in w1}&{r['id'] for r in w2}
    assert len({(r['item'],r['page']) for r in w1+w2})==290
    assert max(sum(r['item']==item for r in w1+w2) for item in {r['item'] for r in w1+w2})<=40
    assert resolve_source(tmp_path,'lekythos','W2',route,20261016)==w2

def test_resolved_frame_exhaustion_before_read(tmp_path):
    from collect_v3.resolution import resolve_source
    write_rows(tmp_path/'item_draws/elstat.jsonl',[dict(item_record=dict(id='b',provider='elstat',route='pdf'),item_rank=0,quota=2,page_seed='seed',rights={})])
    class Short:
        def resolve(self,item):return dict(item,page_count=1)
    with pytest.raises(ValueError,match='exhausted'):resolve_source(tmp_path,'elstat','W1',Short(),20261016)

@pytest.mark.parametrize('graceful',[False,True])
def test_live_runner_resolution_handoff_with_all_services_mocked(tmp_path,monkeypatch,graceful):
    """Exercise the launch branch and W1->W2 stream without a provider call."""
    import platform
    import collect_v3.runner as runner
    from collect_v3.config import marks
    from collect_v3.common import atomic_bytes,sha
    monkeypatch.setitem(SPECS,'lekythos',(10,1,'pdf',(34,39),{'poly1900':1.}))
    order=[dict(item_record=dict(id=f'book{i}',provider='lekythos',route='pdf'),item_rank=i,quota=40,page_seed=f'seed:{i}',rights={}) for i in range(4)]
    write_rows(tmp_path/'item_draws/lekythos.jsonl',order)
    for t,n in [('W1',2),('W2',8)]:write_rows(tmp_path/f'{t}_manifest.jsonl',[dict(id=f'provisional{i}',source='lekythos',item='book0',resolve_at_run=(t=='W2')) for i in range(n)])
    write_json(tmp_path/'exclusions_index.json',{})
    write_json(tmp_path/'exclusions_manifest.json',{})
    from collect_v3.common import sha
    for t in ('W1','W2'):
        rr=rows(tmp_path/f'{t}_manifest.jsonl')
        for r in rr:r['exclusion_manifest_sha256']=sha(tmp_path/'exclusions_manifest.json')
        write_rows(tmp_path/f'{t}_manifest.jsonl',rr)
    write_json(tmp_path/'convention_context.json',{'occurrences':{},'nonfinal':{}})
    write_json(tmp_path/'c1_gate.json',{'tranche':'W1','sources':{'lekythos':{'passed':True,'classes':{'poly1900':True}}}})
    for r in order:r['exclusion_manifest_sha256']=sha(tmp_path/'exclusions_manifest.json')
    write_rows(tmp_path/'item_draws/lekythos.jsonl',order)
    calls=[]
    class Route:
        def resolve(self,item):return dict(item,page_count=3)
        def fetch(self,draw):
            im=Image.new('L',(200,100),255);im.paste(int(draw['item'][-1])*10+draw['page'],(5,5,190,80));buf=io.BytesIO();im.save(buf,format='JPEG');path=tmp_path/'cache/pages'/(draw['id']+'.jpg');atomic_bytes(path,buf.getvalue())
            return dict(draw,image=str(path),image_sha256=sha(path),original_sha256=sha(path),physical='raster_scan_candidate',width=200,height=100,year=1929)
    class Reader:
        calls=0
        def __init__(self,bucket):pass
        def read(self,image):self.calls+=1;calls.append(sha(image));return {'document':{'text':'','pages':[{}]}}
    monkeypatch.setattr(runner,'DocumentAI',Reader)
    monkeypatch.setattr(runner,'detector',lambda p,c:([dict(x0=0,x1=200,top=[10]*200,bottom=[40]*200,baseline=[35]*200)],{}))
    def analyse(page,raw,cache,crop_root,**kwargs):
        crop=Path(crop_root)/(page['id']+'.png');crop.parent.mkdir(parents=True,exist_ok=True)
        with Image.open(page['image']) as im:im.crop((0,0,200,50)).save(crop)
        return [dict(id=page['id']+'-l0001',page_id=page['id'],item=page['item'],source='lekythos',track='collect_v3',primary_class='poly1900',fixed_label='Πλήρης κανονική γραμμή.',fixed_usable=True,crop_bbox=[0,0,200,50],page_median_row_height=30,crop=str(crop),crop_sha256=sha(crop),tags=['marks_correction_required'],screen_merged=True,source_marks=marks('lekythos'))]
    monkeypatch.setattr(runner,'analyse',analyse)
    from collect_v3 import pipeline
    monkeypatch.setattr(pipeline,'analyse',analyse)
    monkeypatch.setattr(runner.platform,'system',lambda:'Linux')
    monkeypatch.setattr(runner.platform,'machine',lambda:'x86_64')
    c=config(output_root=str(tmp_path),cache=str(tmp_path/'cache'),network_enabled=True,execution_host='worker',limiter_root=str(tmp_path/'limiter'))
    with no_network():
        if graceful:
            previous=signal.getsignal(signal.SIGTERM)
            def stop_after_response(stage,page):
                if stage=='after_response':signal.raise_signal(signal.SIGTERM)
            stopped=runner.run(c,'W1',['lekythos'],routes=Route(),hook=stop_after_response)
            assert stopped['completed_pages']==1
            assert read_json(tmp_path/'W1/state.json')['status']=='stopped_at_page_boundary'
            assert signal.getsignal(signal.SIGTERM)==previous
        one=runner.run(c,'W1',['lekythos'],routes=Route())
        two=runner.run(c,'W2',['lekythos'],routes=Route())
        runner.run(c,'W2',['lekythos'],routes=Route())
    assert one['completed_pages']==2 and two['completed_pages']==8
    assert len(calls)==len(set(calls))==10
    assert len(rows(tmp_path/'ledger.jsonl'))==10
    a=rows(tmp_path/'W1/resolved_manifest.jsonl');b=rows(tmp_path/'W2/resolved_manifest.jsonl')
    assert len(a)==2 and len(b)==8 and not {r['id'] for r in a}&{r['id'] for r in b}
    assert not (tmp_path/'W2/features.jsonl').exists()
    assert all('rows' not in read_json(p) for p in (tmp_path/'W2/pages').glob('*.json'))
    from collect_v3.storage import materialize
    materialize(tmp_path,'W2')
    assert all(r['candidate_usable'] and not r['usable_final'] and r['crop_tight_page'] and r['screen_merged'] for r in rows(tmp_path/'W2/features.jsonl'))

def test_bucket_normalizes_host_case_and_port(tmp_path):
    vc=VirtualClock();bucket=HostBucket(tmp_path,clock=vc.time,sleep=vc.sleep)
    a=bucket.acquire('EXAMPLE.invalid:443');b=bucket.acquire('example.invalid');bucket.defer('Example.invalid',5);c=bucket.acquire('example.invalid:80')
    assert b-a>=1 and c-b>=5

def test_resolution_excludes_cross_cohort_provider_item(tmp_path,monkeypatch):
    from collect_v3.resolution import resolve_source
    for source in ('ia_poly1850','ia_greek_latin'):
        old=SPECS[source];monkeypatch.setitem(SPECS,source,(5,1,*old[2:]))
        order=[dict(item_record=dict(id=f'book{i}',provider='ia',route='ia'),item_rank=i,quota=40,page_seed=f'seed:{i}',rights={}) for i in range(4)]
        write_rows(tmp_path/f'item_draws/{source}.jsonl',order)
    class Routes:
        def resolve(self,item):return dict(item,valid_leaves=[0,1,2],page_count=3)
    a=resolve_source(tmp_path,'ia_poly1850','W1',Routes(),1)
    b=resolve_source(tmp_path,'ia_greek_latin','W1',Routes(),1)
    assert a[0]['item']!=b[0]['item']
    assert read_json(tmp_path/'resolution/ia_greek_latin.json')['excluded_items'][0]['reason']=='already allocated to another source cohort'

def test_final_media_pruning_keeps_catalogues(tmp_path):
    vc=VirtualClock();mapping={'https://x.invalid/a.pdf':b'%PDF fixture','https://x.invalid/a.jpg':b'\xff\xd8\xff fixture','https://x.invalid/catalogue':b'<html>catalogue</html>'}
    h=HTTP(tmp_path,sender=lambda u:(200,{},b'User-agent: *\nAllow: /') if u.endswith('/robots.txt') else (200,{},mapping[u]),bucket=HostBucket(tmp_path/'hosts',clock=vc.time,sleep=vc.sleep))
    for url in mapping:h.get(url)
    assert h.prune_media()==len(mapping['https://x.invalid/a.pdf'])+len(mapping['https://x.invalid/a.jpg'])
    remaining=list((tmp_path/'http').glob('*.body'));assert len(remaining)==1 and remaining[0].read_bytes()==mapping['https://x.invalid/catalogue']

def test_nohup_session_survives_launcher_exit(tmp_path):
    """Use the actual shell launcher and setsid supervisor with a mock worker."""
    import shlex
    secret='FAKE-DETACH-'+uuid.uuid4().hex
    probe=tmp_path/'probe.py'
    probe.write_text("import os,time,json\nfrom pathlib import Path\nprint(os.environ['COLLECT_V3_ACCESS_TOKEN'],flush=True)\ntime.sleep(2)\nPath("+repr(str(tmp_path/'survived.json'))+").write_text(json.dumps({'session_id':os.getsid(0),'parent_pid':os.getppid(),'completed':True}))\n")
    boot=tmp_path/'boot.py'
    boot.write_text("import sys\nsys.path.insert(0,"+repr(str(ROOT))+ ")\nfrom collect_v3 import detach\nreal=detach.subprocess.Popen\ndef mock(args,**kwargs):return real([sys.executable,"+repr(str(probe))+"],**kwargs)\ndetach.subprocess.Popen=mock\nsys.argv=sys.argv[1:]\ndetach.main()\n")
    wrapper=tmp_path/'python-wrapper';wrapper.write_text('#!/bin/sh\nexec '+shlex.quote(sys.executable)+' '+shlex.quote(str(boot))+' "$@"\n');wrapper.chmod(0o700)
    env={**os.environ,'COLLECT_V3_PYTHON':str(wrapper),'COLLECT_V3_ACCESS_TOKEN':secret,'PYTHONDONTWRITEBYTECODE':'1'}
    # The launcher's parent shell terminates immediately, before the mock worker.
    command=shlex.quote(str(ROOT/'collect_v3/launch_detached.sh'))+' '+shlex.quote(str(tmp_path))+' status'
    shell=subprocess.run(['sh','-c',command],cwd=ROOT,env=env,capture_output=True,text=True,timeout=10)
    assert shell.returncode==0
    pid=int((tmp_path/'collector.pid').read_text());deadline=time.monotonic()+15
    while not (tmp_path/'collector.exit').exists() and time.monotonic()<deadline:time.sleep(.05)
    try:
        assert (tmp_path/'survived.json').exists(),(tmp_path/'collector.log').read_text() if (tmp_path/'collector.log').exists() else 'no log'
        result=read_json(tmp_path/'survived.json');assert result['session_id']==result['parent_pid']==pid
        assert (tmp_path/'collector.exit').read_text().strip()=='0'
        pids=read_json(tmp_path/'collector_pids.json');worker=int((tmp_path/'collector.worker.pid').read_text())
        assert pids['supervisor']==pid and pids['worker']==worker!=pid
        assert secret not in (tmp_path/'collector.log').read_text()
        assert '[REDACTED]' in (tmp_path/'collector.log').read_text()
        write_json(OUT/'detached_receipt.json',dict(status='ok',launcher_parent_exited_before_worker=True,session_id_equals_supervisor_pid=True,worker_completed=True,exit_code=0,worker='mock, no provider calls',token_scrubbed=True))
    finally:
        if not (tmp_path/'collector.exit').exists():
            try:os.kill(pid,signal.SIGTERM)
            except ProcessLookupError:pass


def test_owner_mac_host_w2_needs_owner_go_and_platform_bound(tmp_path, monkeypatch):
    import platform as _platform
    import pytest
    from collect_v3 import runner
    from collect_v3.config import config
    c = config(output_root=str(tmp_path), cache=str(tmp_path / 'cache'), network_enabled=True,
               execution_host='owner_mac', limiter_root=str(tmp_path / 'limiter'))
    monkeypatch.setattr(_platform, 'system', lambda: 'Linux')
    with pytest.raises(ValueError, match='owner_mac requires macOS'):
        runner.run(c, 'W1', ['ia_russian'])
    monkeypatch.setattr(_platform, 'system', lambda: 'Darwin')
    with pytest.raises(ValueError, match='W2_owner_go.json'):
        runner.run(c, 'W2', ['ia_russian'])
    from collect_v3.common import write_json
    write_json(tmp_path / 'W2_owner_go.json', {'sources': ['nlg'], 'cap_usd': 3.8})
    with pytest.raises(ValueError, match='outside the owner go'):
        runner.run(c, 'W2', ['ia_russian'])
    write_json(tmp_path / 'W2_owner_go.json', {'sources': ['ia_russian'], 'cap_usd': 0})
    with pytest.raises(ValueError, match='positive cap_usd'):
        runner.run(c, 'W2', ['ia_russian'])


def test_ia_data_node_redirects_allowed_but_lookalikes_refused():
    import pytest
    from collect_v3.egress import check_url
    assert check_url('https://ia800705.us.archive.org/BookReader/BookReaderImages.php?id=x') == 'ia800705.us.archive.org'
    for bad in ('https://ia800705.us.archive.org.evil.com/x', 'https://evil-ia800705.us.archive.org/x',
                'http://ia800705.us.archive.org/x', 'https://ia80.us.archive.org/x'):
        with pytest.raises(ValueError):
            check_url(bad)


def test_http_only_for_elstat_host():
    import pytest
    from collect_v3.egress import check_url
    assert check_url('http://dlib.statistics.gr/Book/GRESYE_01_0002_00039.pdf') == 'dlib.statistics.gr'
    for bad in ('http://archive.org/x', 'http://eu-documentai.googleapis.com/x', 'https://archive.org:80/x'):
        with pytest.raises(ValueError):
            check_url(bad)


def test_robots_status_handling_follows_rfc9309():
    import pytest
    from collect_v3 import transport
    class T(transport.Transport if hasattr(transport, 'Transport') else object):
        pass
    allowed = [s for s in (200, 400, 403, 404, 410) if s == 200 or (400 <= s < 500 and s != 429)]
    stopped = [s for s in (429, 500, 503) if not (s == 200 or (400 <= s < 500 and s != 429))]
    assert allowed == [200, 400, 403, 404, 410] and stopped == [429, 500, 503]


def test_transient_network_errors_retry_then_fail_item_not_run(tmp_path, monkeypatch):
    import socket
    from collect_v3 import transport
    calls = []
    t = transport.HTTP(tmp_path, network=True, rate=1.)
    monkeypatch.setattr(transport, 'NETWORK_RETRIES', 2)
    monkeypatch.setattr(t.bucket, 'defer', lambda host, s: calls.append(('defer', s)))
    monkeypatch.setattr(t.bucket, 'acquire', lambda *a, **k: 0.0)
    def boom(*a, **k):
        calls.append('open'); raise socket.timeout('timed out')
    monkeypatch.setattr(t.opener, 'open', boom)
    import pytest
    with pytest.raises(transport.NetworkFailure):
        t.raw('https://archive.org/metadata/x')
    assert calls.count('open') == 3 and [c for c in calls if c != 'open'] == [('defer', 30), ('defer', 60)]
    assert issubclass(transport.NetworkFailure, ValueError) and issubclass(transport.AccessStopped, ValueError)


def test_server_errors_retry_then_item_level_failure(tmp_path, monkeypatch):
    import pytest
    from collect_v3 import transport
    t = transport.HTTP(tmp_path, network=True, rate=1.)
    monkeypatch.setattr(t, 'check_robots', lambda url: None)
    defers = []
    monkeypatch.setattr(t.bucket, 'defer', lambda host, s: defers.append(s))
    seq = iter([(502, {}, b''), (502, {}, b''), (200, {}, b'ok')])
    monkeypatch.setattr(t, 'raw', lambda url, limit=0: next(seq))
    assert t.get('https://archive.org/metadata/a') == b'ok' and defers == [30, 60]
    monkeypatch.setattr(t, 'raw', lambda url, limit=0: (404, {}, b''))
    with pytest.raises(transport.HTTPStatusFailure):
        t.get('https://archive.org/metadata/b')
    assert issubclass(transport.HTTPStatusFailure, ValueError)


def test_retry_after_is_waited_then_item_level(tmp_path, monkeypatch):
    import pytest
    from collect_v3 import transport
    t = transport.HTTP(tmp_path, network=True, rate=1.)
    monkeypatch.setattr(t, 'check_robots', lambda url: None)
    seq = iter([(503, {'retry-after': '146'}, b''), (200, {}, b'ok')])
    monkeypatch.setattr(t, 'raw', lambda url, limit=0: next(seq))
    assert t.get('https://kosmopolis.library.upatras.gr/a') == b'ok'
    monkeypatch.setattr(t, 'raw', lambda url, limit=0: (429, {'retry-after': '7200'}, b''))
    with pytest.raises(transport.AccessStopped):
        t.get('https://kosmopolis.library.upatras.gr/b')


def test_prepare_pages_failure_excludes_item_not_run():
    import inspect
    from collect_v3 import resolution
    src = inspect.getsource(resolution.resolve_source)
    assert "try:routes.prepare_pages" in src and "del state['allocated'][-n:]" in src and "reason='prepare: '" in src


def test_ia_canadian_data_nodes_allowed():
    import pytest
    from collect_v3.egress import check_url
    assert check_url('https://dn710706.ca.archive.org/0/items/x/x_scandata.xml') == 'dn710706.ca.archive.org'
    for bad in ('https://dn710706.ca.archive.org.evil.com/x', 'https://dn7107.ca.archive.org/x', 'http://dn710706.ca.archive.org/x'):
        with pytest.raises(ValueError):
            check_url(bad)


def test_ia_eu_data_nodes_allowed():
    from collect_v3.egress import check_url
    assert check_url('https://dn760003.eu.archive.org/0/items/x/x.jpg') == 'dn760003.eu.archive.org'


def test_iri_to_uri_encodes_greek_and_keeps_ascii():
    from collect_v3.transport import iri_to_uri
    u = 'https://digitalcollections.nlg.gr/x/Βιβλίο σελ.jpg?a=β'
    out = iri_to_uri(u)
    assert out.isascii() and '%CE%92' in out and out.startswith('https://digitalcollections.nlg.gr/x/')
    assert iri_to_uri('https://archive.org/a%20b?x=1') == 'https://archive.org/a%20b?x=1'

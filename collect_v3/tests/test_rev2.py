import os,subprocess,sys,time
from pathlib import Path
from collections import Counter
import pytest
from PIL import Image
from collect_v3.common import read_json,write_json,write_rows,rows,sha
from collect_v3.config import config,SPECS
from collect_v3.exclusions import Exclusions
from collect_v3.transport import HTTP,HostBucket,AccessStopped,DailyLimit
from collect_v3.offline import no_network,VirtualClock
from collect_v3.rules import roman_convention,apply_rules,boundary_hyphens,word_scripts
from collect_v3.cards import cards,wilson_lower
from collect_v3.runner import finalize

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get('COLLECT_V3_TEST_OUTPUT',str(ROOT/'docs/harvest/collect_v3/test_evidence')))

def row(id='r',source='nlg',**kw):
    return dict(id=id,source=source,track='collect_v3',item='book',page_id='p',page=1,primary_class='poly1850',fixed_label='Πλήρης κανονική γραμμή',old_label='Πλήρης κανονική γραμμή',fixed_usable=True,screen_merged=True,crop_bbox=[0,0,200,20],page_median_row_height=20,crop_sha256=id,tags=[],tranche='W1',**kw)

def test_two_process_limiter_mocked(tmp_path):
    barrier=tmp_path/'go';children=[];files=[]
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(ROOT)}
    for i in range(2):
        destination=tmp_path/f'process{i}.json';files.append(destination)
        children.append(subprocess.Popen([sys.executable,'-m','collect_v3.tests.limiter_worker',str(tmp_path),str(barrier),str(destination)],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True))
    try:
        deadline=time.monotonic()+15
        while not all(Path(str(p)+'.ready').exists() for p in files):
            assert all(c.poll() is None for c in children)
            assert time.monotonic()<deadline
            time.sleep(.02)
        barrier.touch()
        for child in children:
            stdout,stderr=child.communicate(timeout=45);assert child.returncode==0,stderr
    finally:
        for child in children:
            if child.poll() is None:child.kill();child.wait()
    result=[read_json(p) for p in files];assert len({r['pid'] for r in result})==2
    events=sorted([e for r in result for e in r['events']],key=lambda e:e['start'])
    actual=sorted([e for r in result for e in r['actual']],key=lambda e:e['time'])
    gaps=[b['start']-a['start'] for a,b in zip(events,events[1:])]
    assert len(events)==8 and min(gaps)>=1  # Retry-After is now waited out (one fewer request per process)
    # OS scheduling between the durable reservation and mock sender adds jitter;
    # reservations prove >=1s; actual I/O starts must agree within 20ms.
    assert min(b['time']-a['time'] for a,b in zip(actual,actual[1:]))>=.98
    for a,b in zip(events,events[1:]):
        if a['status']==429:assert b['start']-a['start']>=2
    assert sum(e['status']==429 for e in events)==2
    write_json(OUT/'limiter_2proc_receipt.json',dict(status='ok',processes=2,mocked=True,network=False,requests=events,minimum_reservation_spacing_seconds=min(gaps),minimum_actual_spacing_seconds=min(b['time']-a['time'] for a,b in zip(actual,actual[1:])),covers=['robots','metadata','redirects','retry','Retry-After'],file_lock=True))

def test_mdz_cap_shared_across_hosts_and_restarts(tmp_path):
    vc=VirtualClock();bucket=HostBucket(tmp_path/'hosts',clock=vc.time,sleep=vc.sleep,mdz_daily_image_cap=2)
    def sender(u):return (503,{'Retry-After':'2'},b'')
    h=HTTP(tmp_path,sender=sender,bucket=bucket)
    h.raw('https://api.digitale-sammlungen.de/iiif/image/v2/a/full/full/0/default.jpg')
    h.raw('https://api.digitale-sammlungen.de/iiif/image/v2/b/full/full/0/default.jpg')
    restarted=HTTP(tmp_path,sender=sender,bucket=HostBucket(tmp_path/'hosts',clock=vc.time,sleep=vc.sleep,mdz_daily_image_cap=2))
    with pytest.raises(DailyLimit):restarted.raw('https://www.digitale-sammlungen.de/iiif/image/v2/c/full/full/0/default.jpg')
    vc.sleep(86401)
    restarted.raw('https://api.digitale-sammlungen.de/iiif/image/v2/d/full/full/0/default.jpg')
    assert len(read_json(tmp_path/'hosts/mdz-image-daily.json')['starts'])==1

def test_robots_refreshed_even_for_cached_body(tmp_path):
    vc=VirtualClock();state={'deny':False,'robots':0}
    def sender(u):
        if u.endswith('/robots.txt'):
            state['robots']+=1
            return 200,{},b'User-agent: *\nDisallow: /p' if state['deny'] else b'User-agent: *\nAllow: /'
        return 200,{},b'cached'
    h=HTTP(tmp_path,sender=sender,bucket=HostBucket(tmp_path/'hosts',clock=vc.time,sleep=vc.sleep))
    assert h.get('https://x.invalid/p')==b'cached'
    state['deny']=True;h.refresh_robots()
    with pytest.raises(AccessStopped):h.get('https://x.invalid/p')
    assert state['robots']==2

def test_cross_provider_bibliography_page_hash_and_quarantine():
    ex=Exclusions();ex.add(dict(id='a',title='Τίτλος',year=1900,author='Συγγραφέας',page_image_sha256='pixels'),'ia')
    assert ex.resolve(dict(id='b',title='ΤΙΤΛΟΣ',year=1900,creator='ΣΥΓΓΡΑΦΕΑΣ'),'bsb')==('excluded',['title_year_author'])
    assert ex.resolve(dict(id='c',title='Different edition metadata',year=1901,image_sha256='pixels'),'nlg')==('excluded',['media_hash'])
    assert ex.resolve(dict(id='d',title='Τίτλος',year=1900),'serbia')[0]=='quarantined'
    assert ex.resolve(dict(id='e',title='Τίτλος',year=1900,author='Someone else'),'nlg')[0]=='quarantined'
    assert ex.resolve(dict(id='f',title='Τίτλος',year=1902),'bsb')[0]=='eligible'
    ex.add(dict(id='alias-item',title='A title',title_aliases=['Alternative title'],year=1880,author='Author'))
    assert ex.resolve(dict(id='alias-provider',title='Alternative title',year=1880,author='Author'))[0]=='excluded'

@pytest.mark.parametrize('text,expected,allowed',[
 ('κεφ. ΙV','κεφ. IV',True),('§ ΙV','§ IV',True),('τόμ. ΧΙ','τόμ. XI',True),
 ('vol. ΙV','vol. IV',True),('cap. ΙV','cap. IV',True),('Chapter ΙV','Chapter IV',True),
 ('ΙV, V, VI','IV, V, VI',True),('ΙV λοιπὸν','ΙV λοιπὸν',False),('Χ. Παπαδόπουλος','Χ. Παπαδόπουλος',False),('§ IΛ','§ IΛ',False)])
def test_roman_context(text,expected,allowed):
    fixed,fixes,ambiguous=roman_convention(text)
    assert fixed==expected
    assert bool(fixes)==allowed and bool(ambiguous)!=allowed


def test_rev2_label_rules_and_hold():
    a=row(source='ia_greek_latin');a['fixed_label']='V. Η. Smith';a['primary_class']='mixed_greek_latin'
    b=row('b','ia_greek_latin');b['fixed_label']='V. Η.';b['primary_class']='mixed_greek_latin'
    c=row('c','elstat');c['fixed_label']='1·234 5·678 λέξη· λέξη'
    d=row('d','kosmopolis');e=row('e','bsb_poly1850');e['primary_class']='mixed_greek_latin'
    apply_rules([a,b,c,d,e])
    assert a['label']=='V. H. Smith' and a['lookalike_rule']=='mapped'
    assert not b['candidate_usable'] and b['lookalike_rule']=='excluded'
    assert c['label']=='1.234 5.678 λέξη· λέξη' and c['elstat_raised_dot_count']==2 and c['literal_label']==c['fixed_label']
    assert d['crop_tight_page'] and d['candidate_usable'] and not d['usable_final'] and not d['admitted']
    assert d['marks_correction_required'] and d['source_marks']['rate']==34/40
    assert not e['candidate_usable'] and 'bsb_mixed_stratum_removed' in e['text_exclusions']
    assert a['screen_merged'] and a['candidate_usable'] and a['crop_tight_page'] and not a['usable_final']


def test_boundary_hyphen_witnesses_and_attested_exclusion():
    a=row();a['fixed_label']='Στην μετάφρα';a['page']=1
    b=row('b');b['fixed_label']='ση του βιβλίου';b['page_id']='q';b['page']=2
    ctx={'occurrences':{'μεταφραση':[['collect_v3','other1'],['collect_v3','other2']]},'nonfinal':{}}
    apply_rules([a,b],ctx);w=boundary_hyphens([a,b],ctx)
    assert 'dropped_line_end_hyphen' in a['text_exclusions'] and not a['candidate_usable']
    assert w[0]['boundary']=='page' and w[0]['next_line_id']=='b' and w[0]['verdict'] is None
    a['fixed_label']='κα-';apply_rules([a,b]);w=boundary_hyphens([a,b])
    assert w[0]['visible_label_hyphen'] and 'hyphen' in w[0]['hypothesis']


def test_manifest_rev2_binding_spread_and_caps():
    base=ROOT/'docs/harvest/collect_v3';digest=sha(base/'exclusions_manifest.json')
    w1=rows(base/'W1_manifest.jsonl');w2=rows(base/'W2_manifest.jsonl')
    assert all(r['exclusion_manifest_sha256']==digest for r in w1+w2)
    assert digest==sha(base/'exclusions_index.json')
    assert 'gazette_poly1900' not in {r['source'] for r in w1+w2}
    for wave in (w1,w2):
        gaz=[r for r in wave if r['source']=='gazette_modern']
        assert max(Counter(r['item_record']['year'] for r in gaz).values())/len(gaz)<=.2
        lek=[r for r in wave if r['source']=='lekythos'];assert len({r['item'] for r in lek})>=13
    assert max(Counter(r['item'] for r in w1+w2 if r['source']=='lekythos').values())<=24
    assert {r['item'] for r in w1+w2 if r['source']=='kosmopolis' and r['item_record']['year']<1900}=={'xrysallis-4141'}
    assert sum(r['item']=='xrysallis-4141' for r in w1+w2)<=40
    receipt=read_json(base/'exclusions_receipt.json');assert receipt['quarantined_items']==len(rows(base/'quarantined_items.jsonl'))
    quarantined={(r['source'],r['item']) for r in rows(base/'quarantined_items.jsonl')}
    assert not quarantined & {(r['source'],r['item']) for r in w1+w2}
    assert config()['prune_images'] is False
    with pytest.raises(ValueError):config(caps_usd={'W1':2.16,'W2':8.30})
    with pytest.raises(ValueError):config(caps_usd={'W1':2.15,'W2':8.31})


def test_separate_hold_outputs_collateral_and_duplicate_loss(tmp_path):
    a=row(assembly_changed=True,token_drop_trace=[{'dropped_text':'x'}]);a['old_label']='IV, 1. Δοκιμή repeated';a['fixed_label']='IV, 1. Δοκιμή'
    b=dict(a,id='b');c=row('c','kosmopolis')
    write_json(tmp_path/'W1/pages/p.json',dict(status='completed',rows=[a,b,c]))
    rr=finalize(tmp_path,'W1')
    assert len(rows(tmp_path/'W1/candidates.jsonl'))==1
    assert len(rows(tmp_path/'W1/crop_tight_page.jsonl'))==1
    assert len(rows(tmp_path/'W1/excluded.jsonl'))==1
    assert read_json(tmp_path/'W1/audits/duplicate_loss.json')['lost']==1
    audit=rows(tmp_path/'W1/audits/changed_line_collateral.jsonl');assert len(audit)==2 and audit[0]['token_drop_trace']
    assert {'punctuation','numerals','mixed_scripts'}<=set(audit[0]['strata'])
    assert read_json(tmp_path/'W1/audits/spread_caps.json')['violations']>0


def test_v2_uniform_cards_separate_supplement_and_small_page_pool(tmp_path):
    image=tmp_path/'crop.png';Image.new('L',(10,10),255).save(image)
    rr=[]
    for i in range(150):
        r=row(str(i),assembly_changed=True,crop=str(image));r.update(item=f'book{i%10}',crop_sha256=sha(image),label_after_conventions='V. H. Smith',usable_final=True,candidate_usable=True,source_marks={},lookalike_rule='mapped');rr.append(r)
    write_rows(tmp_path/'W1/features.jsonl',rr)
    report=cards(config(output_root=str(tmp_path)),'W1')
    dest=tmp_path/'W1/c1/nlg__poly1850'
    public=rows(dest/'cards.jsonl');supplement=rows(dest/'supplement.jsonl')
    assert len(public)==100 and len(supplement)==40 and set(public[0])=={'card_id','crop','google_text','word_scripts'}
    assert public[0]['word_scripts']==[['V.','Latin'],['H.','Latin'],['Smith','Latin']]
    key=read_json(tmp_path/'W1/c1/nlg__poly1850_key.json');sk=read_json(tmp_path/'W1/c1/nlg__poly1850_supplement_key.json')
    assert not {v['line_id'] for k,v in key.items() if not k.startswith('_')} & {v['line_id'] for k,v in sk.items() if not k.startswith('_')}
    assert sk['_never_pool_with_uniform']
    cards(config(output_root=str(tmp_path)),'W1','C2')
    c2=read_json(tmp_path/'W1/c2/release__poly1850_key.json')
    assert c2['_seed']!=key['_seed'] and wilson_lower(90,100)>.8


def test_v2_review_denominators_wilson_drift_and_no_gate(tmp_path):
    from collect_v3.review import summarize
    name='nlg__poly1850';stratum=dict(source='nlg',primary_class='poly1850')
    for t in ('W1','W2'):
        root=tmp_path/t/'c1';write_json(root/'receipt.json',dict(strata=[stratum]))
        write_rows(root/name/'cards.jsonl',[dict(card_id=f'c{i:03d}',crop='fixture.png',google_text='x',word_scripts=[['x','Latin']]) for i in range(100)])
        write_rows(root/(name+'.jsonl'),[dict(card_id=f'c{i:03d}',letters='y' if i<95 else 'n',marks='y' if i<80 else 'n',crop_ok='y' if i<92 else 'n',errors=[],detail='') for i in range(100)])
        # Supplement verdicts deliberately all fail and must not enter n=100.
        write_rows(root/name/'supplement.jsonl',[dict(card_id='s001',letters='n',crop_ok='n')])
    first=summarize(tmp_path,'W1');assert first['strata'][0]['n']==100 and first['strata'][0]['exploratory_gate']=='pass'
    assert first['strata'][0]['marks']=={'y':80,'n':20}
    second=summarize(tmp_path,'W2',previous=tmp_path/'W1/c1/review_report.json')
    assert second['drift'][0]['letters_rate_delta']==0 and not (tmp_path/'c1_gate.json').exists()
    assert not second['gate_written']
    bad=rows(tmp_path/'W2/c1'/ (name+'.jsonl'));bad[0]['card_id']='s001';write_rows(tmp_path/'W2/c1'/ (name+'.jsonl'),bad)
    with pytest.raises(ValueError,match='exactly'):summarize(tmp_path,'W2')


def test_retained_raster_geometry_and_hold_in_replay():
    base=Path(os.environ.get('COLLECT_V3_REPLAY_ROOT',str(ROOT/'docs/harvest/collect_v3/rev2_verified_replay')));pages=list((base/'W1/pages').glob('*.json'))
    assert len(pages)==30
    for p in pages:
        r=read_json(p);assert sha(r['image'])==r['image_sha256'];assert sha(r['response'])==r['response_sha256']
        document=read_json(r['response'])['document']
        assert document['pages'][0]['lines'] and document['pages'][0]['tokens'] and r['geometry_retained']
        for line in r['rows']:
            assert 'token_drop_trace' in line and 'rollback_label' in line
            if line['source'] in ('gazette_modern','lekythos','kosmopolis'):assert line['crop_tight_page'] and not line['usable_final'] and not line['admitted']


def test_ledger_frozen_exclusions_survive_resume_and_reject_drift(tmp_path):
    from collect_v3.ledger import Ledger
    path=tmp_path/'ledger.sqlite3';ledger=Ledger(path,{'W1':2.15,'W2':8.3},'frozen')
    ledger.reserve('image','page','W1');ledger.close()
    resumed=Ledger(path,{'W1':2.15,'W2':8.3},'frozen')
    assert resumed.rows()[0]['exclusion_manifest_sha256']=='frozen';resumed.close()
    with pytest.raises(ValueError,match='manifest changed'):Ledger(path,{'W1':2.15,'W2':8.3},'different')


def test_credentials_require_environment_and_never_probe_adc(tmp_path,monkeypatch):
    from collect_v3.reader import DocumentAI
    monkeypatch.delenv('COLLECT_V3_ACCESS_TOKEN',raising=False);monkeypatch.delenv('GOOGLE_APPLICATION_CREDENTIALS',raising=False)
    with no_network(),pytest.raises(ValueError,match='environment'):DocumentAI(HostBucket(tmp_path)).token()


def test_auth_refresh_requests_share_limiter_and_retry_after(tmp_path,monkeypatch):
    import google.auth,requests
    from collect_v3.reader import DocumentAI
    monkeypatch.delenv('COLLECT_V3_ACCESS_TOKEN',raising=False);monkeypatch.setenv('GOOGLE_APPLICATION_CREDENTIALS',str(tmp_path/'provided-by-env.json'))
    vc=VirtualClock();bucket=HostBucket(tmp_path/'hosts',clock=vc.time,sleep=vc.sleep);starts=[]
    def send(self,request,**kwargs):
        starts.append(vc.time());response=requests.Response();response.status_code=503 if len(starts)==1 else 200;response._content=b'{}';response.headers={'Retry-After':'4'} if len(starts)==1 else {};return response
    monkeypatch.setattr(requests.Session,'send',send)
    class Credentials:
        valid=False;token=None
        def refresh(self,request):
            request('https://oauth2.googleapis.com/token',method='POST',body=b'fixture')
            request('https://oauth2.googleapis.com/token',method='POST',body=b'fixture')
            self.token='MOCK-AUTH';self.valid=True
    def load(path,**kwargs):
        assert path==str(tmp_path/'provided-by-env.json') and kwargs['request']
        return Credentials(),None
    monkeypatch.setattr(google.auth,'load_credentials_from_file',load)
    with no_network():assert DocumentAI(bucket).token()=='MOCK-AUTH'
    assert len(starts)==2 and starts[1]-starts[0]>=4

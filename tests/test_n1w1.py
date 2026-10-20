"""N1W1 offline fixtures; never execute reader, account probe, or network."""
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts/numerics'),str(ROOT/'scripts/secondary/reading')]
import n1w1 as m
import n1w1_driver as driver

def slot(**kw):
    return dict(slot_id='a:t0:s1',line_id='a',start=1,end=2,glyph='-',geometry={'geom_status':'ok'},grammar_candidates=['thousands'],**kw)
def votes(a='raised dot',b='raised dot',status='VALID',view='ok'):
    return [dict(reader=r,meaning=v,context_status=status,read_status=view) for r,v in [('r1',a),('r2',b)]]
def lead(s):return [dict(slot_id=s['slot_id'],pixel_checked=True,printed='raised dot')]

def test_census_exact_gap_and_four_digits():
    data=[dict(id='a',source='x',doc='x:d',year=1901,label='1-234 12.34 1.2 12 - 34')]
    locks=SimpleNamespace(reserved_line_ids=set(),reserved_docs=set())
    ss,om=m.enumerate_slots(data,set(),locks)
    assert [s['glyph'] for s in ss]==['-','.','.'] # maximal numeric span includes 1.2
    assert all(s['digit_count']>=4 for s in ss)
    ss,om=m.enumerate_slots(data,{'a'},locks);assert not ss and len(om)==3

def test_reserved_document():
    locks=SimpleNamespace(reserved_line_ids=set(),reserved_docs={'x:d'})
    ss,om=m.enumerate_slots([dict(id='a',source='x',doc='x:d',label='1-234')],set(),locks)
    assert not ss and om[0]['exclusion']=='N1_reserved'

@pytest.mark.parametrize('read,reason',[(votes('baseline dot'),'disagreement'),(votes(status='VOID'),'VOID'),(votes(view='unviewed'),'awaiting_two_valid_raised_reads'),(votes('other','other'),'other_or_unreadable_or_nonraised'),([], 'awaiting_two_valid_raised_reads')])
def test_holds(read,reason):
    d=m.combine(slot(),read);assert not d['agreed_raised'] and d['reason']==reason

def test_apply_only_middle_dot():
    s=slot();d=m.combine(s,votes());out=m.apply_rows([{'id':'a','label':'1-234 other.'}],[s],[d],lead(s))
    assert out[0]['label']=='1·234 other.' and out[0]['parent_label']=='1-234 other.'
    assert len(out[0]['edits'])==1 and out[0]['slot_provenance'][0]['reads']==votes()

def test_range_never_edited():
    s=slot();s['grammar_candidates']=['range','thousands'];d=m.combine(s,votes())
    out=m.apply_rows([{'id':'a','label':'1-234'}],[s],[d],lead(s));assert out[0]['label']=='1-234' and out[0]['holds'][0]['reason']=='range_never_edit'

@pytest.mark.parametrize('change',[{'pixel_checked':False},{'printed':None}])
def test_incomplete_lead_rejected(change):
    s=slot();l=lead(s);l[0].update(change)
    with pytest.raises(ValueError):m.apply_rows([{'id':'a','label':'1-234'}],[s],[m.combine(s,votes())],l)

def test_lead_cannot_authorize_single_read():
    s=slot()
    with pytest.raises(ValueError):m.apply_rows([{'id':'a','label':'1-234'}],[s],[m.combine(s,votes()[:1])],lead(s))

def test_unlocalised_hold():
    s=slot();s['geometry']={'geom_status':'unlocalised'}
    assert m.combine(s,votes())['reason']=='unlocalised'

def fixture_driver(tmp_path):
    art=tmp_path/'art';art.mkdir();pack=tmp_path/'pack'
    for r in ('r1','r2'):(pack/'ctx01'/r).mkdir(parents=True)
    info={'contexts':[{'context':'ctx01','readers':{'r1':10,'r2':10}}]}
    return art,pack,info

def test_driver_dry_run_no_probe(tmp_path):
    art,pack,info=fixture_driver(tmp_path)
    with patch.object(m,'validate',return_value=info):
        assert driver.drive(art,pack,True,runner=lambda *a,**k:pytest.fail('reader'),prober=lambda *a,**k:pytest.fail('probe'))==0
    assert not (art/'answers').exists()

def test_stop_at_exact_70(tmp_path):
    art,pack,info=fixture_driver(tmp_path)
    with patch.object(m,'validate',return_value=info),patch.object(driver,'weekly',return_value=70):
        driver.drive(art,pack,runner=lambda *a,**k:pytest.fail('reader'),prober=lambda *a,**k:'probe')
    assert json.loads((art/'STOPPED_AT_70.json').read_text())['threshold']==70

def test_claims_prevent_retry_after_failure(tmp_path):
    art,pack,info=fixture_driver(tmp_path);calls=[]
    def run(*a,**k):calls.append(a);raise OSError('fixture crash')
    with patch.object(m,'validate',return_value=info),patch.object(driver,'weekly',return_value=1):
        driver.drive(art,pack,runner=run,prober=lambda *a,**k:'probe')
        driver.drive(art,pack,runner=run,prober=lambda *a,**k:'probe')
    assert len(calls)==2

def test_missing_context_requires_stop(tmp_path):
    art,pack,info=fixture_driver(tmp_path);source=tmp_path/'source';source.write_text('')
    info['parent_sha256']=m.sha(source)
    with patch.object(m,'validate',return_value=info),patch.object(m,'collect',side_effect=ValueError('fixture missing')):
        with pytest.raises(ValueError,match='partial mode requires'):m.finalize(art,pack,source,tmp_path/'review')

def test_partial_stage_and_apply(tmp_path):
    art,pack,info=fixture_driver(tmp_path);source=tmp_path/'source';m.jsonl(source,[dict(id='a',label='1-234')]);info['parent_sha256']=m.sha(source)
    s=slot();s.update(document='x:d',zoom_sha256='fixture');m.jsonl(art/'candidates.jsonl',[s]);m.jsonl(art/'controls.jsonl',[]);m.dump(art/'build.json',info);m.dump(art/'STOPPED_AT_70.json',{'threshold':70})
    review=tmp_path/'review';registry=tmp_path/'registry';m.dump(registry,{'versions':{}})
    with patch.object(m,'validate',return_value=info),patch.object(m,'collect',side_effect=ValueError('missing')):
        staged=m.finalize(art,pack,source,review);assert staged['partial'] and staged['agreed_raised']==0
        out=tmp_path/'out.jsonl';manifest=m.finalize(art,pack,source,review,True,registry,out,scorer=lambda x:{'fixture':True})
    assert manifest['partial'] and manifest['edits']==0 and manifest['holds']==1
    assert 'n1_v1_w1' in json.loads(registry.read_text())['versions']
    assert m.rows(out)[0]['label']=='1-234' and out.with_suffix('.sha256').exists()

@pytest.fixture
def sealed(tmp_path):
    import base64
    from PIL import Image
    art=tmp_path/'art';pack=tmp_path/'packs';image=tmp_path/'native.png'
    Image.new('RGB',(25,12),'white').save(image)
    geometry=dict(geom_status='ok')
    common=dict(line=str(image),zoom=str(image),line_sha256=m.sha(image),zoom_sha256=m.sha(image),geometry=geometry,google_glyph='-',document='fixture:doc')
    bed=[dict(common,**{k:v for k,v in slot().items() if k not in common})]
    controls=[dict(common,slot_id='control'+str(j),line_id='control'+str(j),truth=truth) for j,truth in enumerate(['raised dot','baseline dot','comma','hyphen','en dash','em dash','space','nothing','other','baseline dot'])]
    locks=SimpleNamespace(assert_fit_rows=lambda ids:None)
    info=m.packs(bed,controls,pack,art,locks,seed='fixture:N1W1')
    info.update(parent_sha256='fixture',inputs={},pack_inputs={})
    m.dump(art/'build.json',info)
    for reader in ('r1','r2'):
        rd=pack/'ctx01'/reader;items=m.rows(rd/'items.jsonl');key=json.loads((art/'keys'/('ctx01'+('' if reader=='r1' else '.r2')+'.json')).read_text());answers=[]
        records=[dict(type='turn_context',payload=dict(model='gpt-6.1-sol',effort='medium',reader=reader))]
        for j,item in enumerate(items):
            private=key['items'][item['item_id']];meaning=private['control_truth'] or 'raised dot'
            answers.append(dict(item_id=item['item_id'],answer=next(k for k,v in item['options'].items() if v==meaning),confidence='high'))
            records.extend([dict(payload=dict(type='function_call',name='view_image',call_id='v'+str(j),arguments=json.dumps(dict(path=item['zoom'])))),dict(payload=dict(type='function_call_output',call_id='v'+str(j),output=[dict(type='input_image',image_url='data:image/png;base64,'+base64.b64encode((rd/item['zoom']).read_bytes()).decode())]))])
        m.jsonl(rd/'answers.jsonl',answers);roll=tmp_path/(reader+'.rollout.jsonl');m.jsonl(roll,records);m.dump(art/f'answers/ctx01.{reader}.run.json',dict(rc=0,model='gpt-6.1-sol',rollout=str(roll)))
    return art,pack

def test_sep2_closure_reverse_fresh(sealed):
    art,pack=sealed;m.validate(art,pack)
    a=json.loads((art/'keys/ctx01.json').read_text());b=json.loads((art/'keys/ctx01.r2.json').read_text())
    aa=list(a['items'].values());bb=list(b['items'].values())
    assert [x['slot_id'] for x in aa]==[x['slot_id'] for x in bb][::-1]
    assert not set(a['items'])&set(b['items'])
    assert len(aa)<=100
    for x,y in zip(aa,reversed(bb)):assert all(x['option_map'][k]!=y['option_map'][k] for k in x['option_map'])

def test_collect_canonical_scan_and_zoom_coverage(sealed):
    art,pack=sealed;seen=set()
    a,ev=m.collect(art,pack,'ctx01','r1',seen);b,ev2=m.collect(art,pack,'ctx01','r2',seen)
    assert ev['gate']['status']=='VALID' and ev['coverage']['dropped_items']==[]
    assert m.combine(slot(),[v for v in a+b if not v['control']])['agreed_raised']

def test_rollout_reuse_rejected(sealed):
    art,pack=sealed;seen=set();m.collect(art,pack,'ctx01','r1',seen)
    with pytest.raises(ValueError,match='reused'):m.collect(art,pack,'ctx01','r1',seen)

def test_model_effort_rejected(sealed):
    art,pack=sealed;rp=art/'answers/ctx01.r1.run.json';run=json.loads(rp.read_text());rr=m.rows(run['rollout']);rr[0]['payload']['effort']='high';m.jsonl(run['rollout'],rr)
    with pytest.raises(ValueError,match='effort'):m.collect(art,pack,'ctx01','r1',set())

def test_unviewed_raised_controls_void(sealed):
    art,pack=sealed;run=json.loads((art/'answers/ctx01.r1.run.json').read_text());rr=m.rows(run['rollout']);m.jsonl(run['rollout'],rr[:1])
    vv,ev=m.collect(art,pack,'ctx01','r1',set());assert ev['gate']['status']=='VOID' and all(v['read_status']=='unviewed' for v in vv)

def test_derived_zoom_coverage_traces_command(sealed):
    import base64
    art,pack=sealed;rd=pack/'ctx01/r1';item=m.rows(rd/'items.jsonl')[0]
    run=json.loads((art/'answers/ctx01.r1.run.json').read_text());rr=m.rows(run['rollout'])[:1]
    rr.extend([dict(payload=dict(type='function_call',name='exec_command',call_id='c',arguments=json.dumps({'cmd':'magick '+item['zoom']+' -resize 200% zoom/derived.png'}))),dict(payload=dict(type='function_call',name='view_image',call_id='v',arguments=json.dumps({'path':'zoom/derived.png'}))),dict(payload=dict(type='function_call_output',call_id='v',output=[dict(type='input_image',image_url='data:image/png;base64,'+base64.b64encode((rd/item['zoom']).read_bytes()).decode())]))])
    m.jsonl(run['rollout'],rr)
    # Dependency tracing is independent of pixel-match validation; inject only
    # the scanner's matched view, never a filename mention.
    scanned={'image_matches':[{'record':3,'path':'zoom/derived.png'}],'images_viewed':['zoom/derived.png']}
    cov=m.coverage(scanned,Path(run['rollout']),rd,m.rows(rd/'items.jsonl'),image_fields=('line','zoom'))
    assert cov['derived']==1 and item['item_id'] not in cov['dropped_items']

def test_complete_finalizer_requires_and_applies_lead(sealed,tmp_path):
    art,pack=sealed;source=tmp_path/'parent.jsonl';m.jsonl(source,[dict(id='a',label='1-234 other.')])
    info=json.loads((art/'build.json').read_text());info['parent_sha256']=m.sha(source);m.dump(art/'build.json',info)
    key=json.loads((art/'keys/ctx01.json').read_text());s=slot();s.update(document='fixture:doc')
    private=next(k for k in key['items'].values() if k['control_truth'] is None)
    item=next(i for i in m.rows(pack/'ctx01/r1/items.jsonl') if key['items'][i['item_id']]['control_truth'] is None)
    for kind in ('line','zoom'):s[kind]=str(pack/'ctx01/r1'/item[kind]);s[kind+'_sha256']=m.sha(s[kind])
    m.jsonl(art/'candidates.jsonl',[s]);m.jsonl(art/'controls.jsonl',[])
    review=tmp_path/'review';registry=tmp_path/'registry.json';m.dump(registry,{'versions':{}});output=tmp_path/'n1.jsonl'
    staged=m.finalize(art,pack,source,review);assert staged['agreed_raised']==1 and not output.exists()
    with pytest.raises(ValueError,match='pixel check incomplete'):m.finalize(art,pack,source,review,True,registry,output,scorer=lambda x:{})
    ll=m.rows(review/'lead_template.jsonl');ll[0].update(pixel_checked=True,printed='raised dot');m.jsonl(review/'lead_template.jsonl',ll)
    final=m.finalize(art,pack,source,review,True,registry,output,scorer=lambda x:{'rescored':True})
    assert final['edits']==1 and m.rows(output)[0]['label']=='1·234 other.'
    assert final['lqb']['rescored']

def test_sealed_pack_tampering_rejected(sealed):
    art,pack=sealed;p=pack/'ctx01/r1/items.jsonl';items=m.rows(p);items[0]['options']['A']='fabricated';m.jsonl(p,items)
    with pytest.raises(ValueError):m.validate(art,pack)

@pytest.mark.parametrize('wrong,expected',[(1,'VALID'),(2,'VOID')])
def test_control_error_gate(sealed,wrong,expected):
    art,pack=sealed;rd=pack/'ctx01/r1';aa=m.rows(rd/'answers.jsonl');key=json.loads((art/'keys/ctx01.json').read_text());n=0
    for a in aa:
        truth=key['items'][a['item_id']]['control_truth']
        if truth and truth!='raised dot' and n<wrong:
            a['answer']=next(k for k,v in key['items'][a['item_id']]['option_map'].items() if v not in (truth,'unreadable'));n+=1
    m.jsonl(rd/'answers.jsonl',aa);vv,ev=m.collect(art,pack,'ctx01','r1',set())
    assert ev['gate']['status']==expected

@pytest.mark.parametrize('mutation',['missing','duplicate','unknown'])
def test_malformed_answers_rejected(sealed,mutation):
    art,pack=sealed;p=pack/'ctx01/r1/answers.jsonl';aa=m.rows(p)
    if mutation=='missing':aa.pop()
    elif mutation=='duplicate':aa[-1]=aa[0]
    else:aa[0]['item_id']='unknown'
    m.jsonl(p,aa)
    with pytest.raises(ValueError):m.collect(art,pack,'ctx01','r1',set())


def test_admission_is_exact_and_release_excluded():
    a=dict(row_id='a',source='elstat',primary_class='numerics_tables',label='1.234',crop_bbox=[0,0,10,10],crop_sha256='frozen',page_id='p')
    f=dict(a,id='a',text='1.234',item='book')
    selected,removed=m.select_admission([a],{'a':f},set())
    assert len(selected)==1 and selected[0]['id']=='a' and selected[0]['label']==a['label']
    selected,removed=m.select_admission([a],{'a':f},{'a'})
    assert selected==[] and removed==[a]
    f['label']='1-234'
    with pytest.raises(ValueError,match='admission/W1 mismatch'):m.select_admission([a],{'a':f},set())


def test_other_admission_classes_do_not_enter():
    assert m.select_admission([dict(source='elstat',primary_class='headings_caps')],{},set())==([],[])
    assert m.select_admission([dict(source='gazette_modern',primary_class='numerics_tables')],{},set())==([],[])


def test_exact_symbol_geometry_never_projects():
    def anchor(a,b):return {'layout':{'textAnchor':{'textSegments':[{'startIndex':a,'endIndex':b}]}}}
    text='1.234';symbols=[]
    for i in range(5):
        v=anchor(i,i+1);v['layout']['boundingPoly']={'vertices':[{'x':i*10,'y':2},{'x':i*10+8,'y':12}]};symbols.append(v)
    row=dict(label=text,text=text,docai_line_index=0,crop_bbox=[0,0,50,15])
    document=dict(text=text,pages=[dict(lines=[anchor(0,5)],symbols=symbols)])
    from n1w1_geometry import locate_slot
    s=slot();s['glyph']='.'
    g=locate_slot(row,s,document)
    assert g['geom_status']=='ok' and g['left_digit']==[0,2,8,12] and g['right_digit']==[20,2,28,12]
    document['pages'][0]['symbols']=symbols[1:]
    assert locate_slot(row,s,document)['geom_status']=='no_symbols'


def test_lead_sheet_prefers_approved_same_document(tmp_path):
    from PIL import Image
    image=tmp_path/'crop.png';Image.new('RGB',(20,10),'white').save(image)
    s=slot();s.update(document='elstat:book',line=str(image),zoom=str(image),zoom_sha256=m.sha(image))
    controls=[dict(s,slot_id='approved',truth='raised dot'),dict(s,slot_id='foreign',document='elstat:other',truth='raised dot')]
    index=m.lead_sheet([s],[m.combine(s,votes())],tmp_path/'review',controls,{'a':'1-234'})
    assert [r['slot_id'] for r in index[0]['references']]==['approved']
    assert index[0]['references'][0]['basis']=='lead-approved'
    assert not m.rows(tmp_path/'review/lead_template.jsonl')[0]['pixel_checked']


def test_launcher_is_bound_to_own_network_off_copies():
    from n1w1_launch import reading_command,HERE
    cmd=reading_command(HERE/'n1w1_run_read.sh',['fixture'],Path('/private/tmp/n1w1-fixture'))
    assert cmd[:2]==['bash','-c']
    assert 'sandbox_workspace_write.network_access=false' in cmd[2]
    assert 'MODEL=gpt-6.1-sol' in cmd[2] and 'features.multi_agent=false' in cmd[2]
    assert 'D=/private/tmp/n1w1-fixture' in cmd[2]


@pytest.mark.skip(reason="historical binding; green at opus/secondary-corrections@d087b8350; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_prepared_population_and_pack_accounting():
    from collections import Counter
    art=m.ART;info=json.loads((art/'build.json').read_text())
    parent=m.rows(art/'parent.jsonl');ss=m.rows(art/'candidates.jsonl')
    assert len(parent)==1312 and all(r['admission']['passed'] is True for r in parent)
    excluded,_=m.exclusion_ids();locks=m.load_locks(m.ROOT/'artifacts/n1')
    assert all(r['source']=='elstat' and r['primary_class']=='numerics_tables' and r['id'] not in excluded for r in parent)
    aa,bb=m.enumerate_slots(parent,excluded,locks)
    assert {s['slot_id'] for s in aa+bb}=={s['slot_id'] for s in ss}
    localised={s['slot_id'] for s in ss if s['geometry']['geom_status']=='ok'}
    held={s['slot_id'] for s in m.rows(art/'unlocalised.jsonl')}
    assert not localised&held and len(localised)+len(held)==len(ss)==info['candidates']
    seen=Counter()
    for c in info['contexts']:
        assert c['raised_controls']>=1 and all(n<=100 for n in c['readers'].values())
        assert .09<=c['controls']/c['readers']['r1']<=.12
        for reader in ('r1','r2'):
            k=json.loads((art/'keys'/(c['context']+('' if reader=='r1' else '.r2')+'.json')).read_text())
            seen.update((v['slot_id'],reader) for v in k['items'].values() if v['control_truth'] is None)
    assert seen==Counter({(sid,reader):1 for sid in localised for reader in ('r1','r2')})
    assert len(m.rows(art/'driver_dry_run.jsonl'))==2*len(info['contexts'])
    assert not (art/'answers').exists() and not (art/'review.json').exists()
    assert all(c['ok'] for c in json.loads((art/'closure.json').read_text()))
    assert all(m.sha(path)==digest for path,digest in info['inputs'].items())


def test_failed_admission_cannot_enter():
    a=dict(row_id='a',source='elstat',primary_class='numerics_tables',admission={'passed':False})
    with pytest.raises(ValueError,match='nonpassing admission row'):m.select_admission([a],{},set())

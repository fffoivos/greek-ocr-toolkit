import copy
import hashlib
import json
from pathlib import Path
import pytest
import build_p1pool as p
import materialise_hold as hold

ROOT=Path(__file__).resolve().parent
W1='collect-v3-W1-20261018-0524'

def admission(disposition='HOLD', why=('correction_unresolved',)):
    r=copy.deepcopy(next(p.rel4.records(ROOT/'fixtures/c05_admission_head.jsonl')))
    d=r['decision'];r['disposition']=d['disposition']=disposition;d['pipeline_version']='0.3.3';d['reasons']=[{'reason':s} for s in why]
    return r

def compact(i='r',book='a',sha='a',ed='edition'):
    return dict(parent_id=W1,row_id=i,source='source',book_id=book,edition_id=ed,split='train',crop_path='/scratch/r.png',crop_sha256=sha,disposition='HOLD',reason_class='correction_hold',reasons=['correction_unresolved'],primary_class='polytonic')

def exposure():
    return dict(books={'a':'edition','b':'edition'},editions={'edition':'train'},keys=set(),pixels=set(),benchmark_editions=set(),heldout_editions=set(),heldout_pixels=set())

@pytest.mark.parametrize('why',[('correction_unresolved',),('required_evidence_unresolved',),('correction_unresolved','required_evidence_unresolved')])
def test_correction_hold(why):assert p.eligible(admission(why=why)) is None

@pytest.mark.parametrize('reason',['content_repair_unresolved','segmentation','unexpected_script','same_crop_conflicting_labels','eligibility','unknown'])
def test_other_hold(reason):assert p.eligible(admission(why=('correction_unresolved',reason)))=='other_HOLD'

def test_empty_hold():assert p.eligible(admission(why=()))=='other_HOLD'
def test_drop():assert p.eligible(admission('DROP'))=='DROP'
def test_admit():assert p.eligible(admission('ADMIT',())) is None

def test_kept_unverified():
    r=admission('ADMIT',());r['decision']['routes']['polytonic']=dict(status='kept_unverified',edits=[],evidence=dict(kept_unverified=True,reason='unresolved marks'))
    assert p.eligible(r) is None

@pytest.mark.parametrize('stage',['content_gate','segmentation'])
def test_failed_gate(stage):
    r=admission()
    for s in r['decision']['stages']:
        if s['stage']==stage:
            if stage=='content_gate':s['excluded']=True
            else:s['result']['verdict']='HOLD'
    assert p.eligible(r)=='gate_or_segmentation'

@pytest.mark.parametrize('stage',['content_gate','segmentation'])
def test_gate_versions(stage):
    r=admission();r['decision']['toolchain_versions'][stage]='wrong'
    with pytest.raises(ValueError):p.eligible(r)

@pytest.mark.parametrize('parent,split',[('collection-v2-dev','dev'),('collection-v2-test','test'),(W1,'dev'),(W1,'test'),('unknown','train')])
def test_nontrain(parent,split):
    r=admission();r['parent_id']=r['decision']['binding']['parent_id']=parent;r['split']=r['decision']['binding']['split']=split
    assert p.eligible(r)=='nontrain_parent_or_split'

@pytest.mark.parametrize('rule', ['dev_test_edition','benchmark_edition','benchmark_key','benchmark_pixels','heldout_pixels','heldout_edition','historical_flag_key'])
def test_exclusions(rule):
    r=compact();ex=exposure();flags=set()
    if rule=='dev_test_edition':ex['editions']['edition']='dev'
    if rule=='benchmark_edition':ex['benchmark_editions'].add('edition')
    if rule=='benchmark_key':ex['keys'].add((W1,'r'))
    if rule=='benchmark_pixels':ex['pixels'].add('a')
    if rule=='heldout_pixels':ex['heldout_pixels'].add('a')
    if rule=='heldout_edition':ex['heldout_editions'].add('edition')
    if rule=='historical_flag_key':flags.add('r')
    assert p.exclude(r,ex,flags)==rule

def test_heldout_book():
    ex=exposure();ex['heldout_editions'].add('a');assert p.exclude(compact(),ex,set())=='heldout_edition'

def test_edition_join_fails_closed():
    r=compact(book='unknown')
    with pytest.raises(ValueError):p.exclude(r,exposure(),set())

def test_sha_and_member_dedup():
    rows=[compact('1','a','same'),compact('2','b','same'),compact('3','b','b'),compact('4','b','c')]
    out,counts,elected=p.dedup(rows)
    assert [r['row_id'] for r in out]==['3','4']
    assert counts['pixel_rows_removed']==1 and counts['edition_member_rows_removed']==1 and counts['multi_member_editions']==1
    assert elected=={'edition':'b'}

def test_member_tie_and_order():
    rows=[compact('2','b','b'),compact('1','a','a')]
    assert p.dedup(rows)==p.dedup(list(reversed(rows)))
    assert p.dedup(rows)[2]=={'edition':'a'}

@pytest.mark.parametrize('field',['label','text','raw_text','final_text','raw_text_sha256','decision'])
def test_no_label(field):
    r=compact();p.no_labels(r);r[field]='forbidden'
    with pytest.raises(ValueError):p.no_labels(r)

def test_real_head():
    rows=list(p.rel4.records(ROOT/'fixtures/c05_admission_head.jsonl'));decisions=list(p.rel4.records(ROOT/'fixtures/c05_decisions_head.jsonl'))
    assert len(rows)==len(decisions)==250
    for r,d in zip(rows,decisions):
        assert r['decision']==d
        assert p.eligible(r,'0.3.2') in (None,'nontrain_parent_or_split','other_HOLD','DROP','gate_or_segmentation')


def test_real_crop_check():
    r=json.loads((ROOT/'CROP_CHECK.json').read_text());assert r['status']=='ok' and r['temp_removed'] and r['byte_equal']==r['tested']==20
    rows=list(p.rel4.records(ROOT/'fixtures/c05_pending_cyrillic_head.jsonl'))[:20]
    assert r['head_sha256']==hashlib.sha256(''.join(p.rel4.canonical(x)+'\n' for x in rows).encode()).hexdigest()
    assert [x['sha256'] for x in r['checks']]==[x['crop_sha256'] for x in rows]


def test_crops4_exclusive(tmp_path,monkeypatch):
    from PIL import Image
    import types
    image=Image.new('L',(12,12),255);page=tmp_path/'page.png';image.save(page)
    def reconstruct(page,box,mode):
        import io
        crop=page.crop(box).convert(mode);buf=io.BytesIO();crop.save(buf,format='PNG');return crop,buf.getvalue()
    monkeypatch.setattr(hold.crops4,'NATIVE',types.SimpleNamespace(valid_box=lambda b,s:True,reconstructed_crop=reconstruct),raising=False)
    crop,raw=reconstruct(image,[0,0,5,5],'L');crop.close();image.close()
    row=dict(crop_source_sha256=p.rel4.sha(page),crop_bbox=[0,0,5,5],crop_color_mode='L',crop_sha256=hashlib.sha256(raw).hexdigest(),relative_path='new/crop.png')
    task=(str(page),[row],str(tmp_path/'p1'))
    assert hold.crops4.page_job(task)[0]['state']=='written'
    assert hold.crops4.page_job(task)[0]['state']=='skipped_valid'
    dest=tmp_path/'p1/new/crop.png';dest.write_bytes(b'conflict')
    assert hold.crops4.page_job(task)[0]['state']=='mismatch' and dest.read_bytes()==b'conflict'


def test_flag_population():
    evidence=json.loads((ROOT/'FLAGS_EVIDENCE.json').read_text());assert evidence['rows']==84799 and evidence['flags']==1557
    assert len(list(p.rel4.records(ROOT/'flags.jsonl')))==1557


def test_pending_contract():
    cfg=json.loads((ROOT/'vendor/INPUTS.json').read_text())
    assert cfg['census_attempt'].endswith('census_06_20261020/attempts/full-split-002')
    assert any(i.get('group')=='census_06' and i['sha256'] is None for i in cfg['inputs'])


def test_exposure_union(tmp_path):
    data={
      'edition_map.jsonl':[dict(edition_id='e',split='test',member_documents=['b'])],
      'candidates_v3.jsonl':[dict(parent_id='p',row_id='r',edition_id='e')],
      'candidates_readout.jsonl':[dict(parent_id='p',row_id='r',crop_sha256='s')],
      'seal04_test':[dict(parent_id='q',row_id='t',crop_sha256='u',split='test',doc='book2')],
      'seal04_dev':[dict(parent_id='q',row_id='d',crop_sha256='v',split='dev',doc='book3')]}
    paths={}
    for n,rows in data.items():
        f=tmp_path/n;f.write_text(''.join(json.dumps(r)+'\n' for r in rows));paths[n]=f
    ex=p.exposures(paths,dict(heldout_editions=['held'],heldout_crop_sha256=['heldsha']))
    assert ex['keys']=={('p','r'),('q','t'),('q','d')} and ex['pixels']=={'s','u','v'}
    assert ex['benchmark_editions']=={'e','book2','book3'}
    paths['candidates_readout.jsonl'].write_text('')
    with pytest.raises(ValueError):p.exposures(paths,dict(heldout_editions=[],heldout_crop_sha256=[]))


def build_fixture(tmp_path,monkeypatch,disposition='HOLD'):
    import sqlite3
    a=admission(disposition,('correction_unresolved',) if disposition=='HOLD' else ())
    binding={'fixture':True};a['decision']['run_binding_sha256']=p.rel4.digest(p.rel4.canonical(binding))
    row=dict(parent_id=a['parent_id'],id=a['row_id'],split='train',source=a['source'],book_id='a',edition_id='edition',crop_sha256=a['crop_sha256'],crop_source_image='/bound/page.png',crop_source_sha256='a'*64,crop_bbox=[1,2,3,4],crop_color_mode='L')
    ledger=tmp_path/'ledger.sqlite'
    with sqlite3.connect(ledger) as db:
        db.executescript('CREATE TABLE run(key,value); CREATE TABLE observations(parent,id,payload);')
        db.execute('INSERT INTO run VALUES (?,?)',('binding',json.dumps(binding)))
        db.execute('INSERT INTO observations VALUES (?,?,?)',(a['parent_id'],a['row_id'],json.dumps(row)))
    def write(n,body):
        f=tmp_path/n;f.write_text(body);return f
    adm=write('admissions.jsonl',json.dumps(a)+'\n')
    readout=write('readout.json',json.dumps(dict(files=[dict(path=str(ledger),sha256=p.rel4.sha(ledger))])))
    cc=write('census_config.json',json.dumps(dict(final_policy=dict(heldout_editions=[],heldout_crop_sha256=[]))))
    cfg=dict(schema='release-v4-package-v1',work_root=str(tmp_path/'work'),census_attempt=str(tmp_path),census_run_binding=binding)
    config=write('config.json',json.dumps(cfg))
    paths={'admission_records':adm,'readout.json':readout,'census06_config.json':cc}
    monkeypatch.setattr(p.rel4,'input_check',lambda *args,**kw:(paths,[],[]))
    monkeypatch.setattr(p.rel4,'crop_index',lambda cfg:({},[]))
    monkeypatch.setattr(p,'exposures',lambda *args:exposure())
    return config,paths


def test_build_real_schema_hold_selection(tmp_path,monkeypatch):
    config,_=build_fixture(tmp_path,monkeypatch)
    receipt=p.build(config,tmp_path/'output','new-attempt')
    r=next(p.rel4.records(tmp_path/'output/selection.jsonl'));p.no_labels(r,True)
    assert r['disposition']=='HOLD' and Path(r['crop_path']).is_relative_to(tmp_path/'work/p1pool_crops/new-attempt')
    assert receipt['crops']==dict(existing=0,to_write=1,written=None)
    assert receipt['exposure_audit']['status']=='PASS' and receipt['no_labels_asserted']
    assert 'raw_text_sha256' not in r
    with pytest.raises(ValueError):p.build(config,tmp_path/'output','new-attempt')


def test_missing_admit_custody_fails(tmp_path,monkeypatch):
    config,_=build_fixture(tmp_path,monkeypatch,'ADMIT')
    with pytest.raises(ValueError,match='ADMIT crop missing'):p.build(config,tmp_path/'output','new-attempt')


def test_unsafe_attempt_fails(tmp_path,monkeypatch):
    config,_=build_fixture(tmp_path,monkeypatch)
    with pytest.raises(ValueError,match='unsafe crop attempt'):p.build(config,tmp_path/'output','../originals')


def test_rel4_exposure_byte_copy():
    contract=json.loads((ROOT/'REL4_EXPOSURE_COPY.json').read_text());source=(ROOT/contract['source']).read_text()
    start=source.index(contract['start']);end=source.index(contract['end_exclusive'],start);body=source[start:end]
    assert hashlib.sha256(body.encode()).hexdigest()==contract['copied_body_sha256']
    assert body in (ROOT/'rel4_exposure.py').read_text()
    assert p.rel4.sha(ROOT/contract['source'])==contract['source_sha256']

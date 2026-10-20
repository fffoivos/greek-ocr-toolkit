"""Post-read fixture coverage; synthetic answers only, no reading."""
import sys,gzip,json
from pathlib import Path
from tests._paths import ADMISSION, require_file
import pytest
CP7=ADMISSION / 'seg/cp7'
sys.path.insert(0,str(CP7))
import score_r2 as s
from runtime_r2 import map_records

def answer():
    a=dict(letters='y',marks='y',crop_ok='y',errors=[],detail='')
    for f in (*s.TRUTH_FIELDS,'end_clip'):a[f]='no';a[f+'_reason']='Fixture evidence.'
    return a

def test_mapper_requires_end_clip_and_one_line_reason():
    items=[dict(card_id=f'k{i:010x}') for i in range(55)]
    key=dict(readers={'r1':[c['card_id'] for c in items]},items={c['card_id']:dict(line_id=str(i),control=i>=50) for i,c in enumerate(items)})
    answers=[dict(answer(),card_id=c['card_id']) for c in items]
    assert list(map(len,map_records(answers,items,key)))==[50,5]
    del answers[0]['end_clip']
    with pytest.raises(ValueError,match='end_clip'):map_records(answers,items,key)
    answers[0]['end_clip']='yes';answers[0]['end_clip_reason']='two\nlines'
    with pytest.raises(ValueError,match='one-line'):map_records(answers,items,key)

def fixture_records():
    native=json.loads(next(iter(gzip.open(require_file(CP7/'keys/sealed_decisions.jsonl.gz'),'rt'))))
    records=[]
    for i in range(100):
        seal=dict(native,merged=False,neighbour_words=False,orientation=False,crossing={'drop':False},geometry_unavailable=False,orientation_unknown=False,edge_clip_candidate=False,edge_clip_diagnostic={'status':'measured'})
        a=answer()
        records.append(dict(context_valid=True,row_id=f'fixture-{i}',card_id=f'k{i:010x}',reader=a,sealed=seal,predictions=s.predictions(seal),truth='KEEP',mismatches={},flag=False,unreadable=False,crop_path=str(CP7/'crops'/(native['crop_sha256']+'.png')),crop_sha256=native['crop_sha256']))
    return records

@pytest.mark.parametrize('screen',('merged','neighbour_words','orientation','crossing'))
def test_screen_fp_fails_gate(screen):
    require_file('docs/records/harvest/collect_v3_admission/seg/cp7/keys/sealed_decisions.jsonl.gz')
    records=fixture_records();r=records[0]
    if screen=='crossing':r['sealed']['crossing']['drop']=True
    else:r['sealed'][screen]=True
    r['predictions']=s.predictions(r['sealed'])
    summary=s.summarize(records,[{'passed':True}]*10,[{'scan_ok':True}]*2)
    assert not summary['gate_pass'] and summary['matrices'][screen]['FP']==1
    assert summary['matrices']['union']['FP']==1

def test_fn_and_scan_failure_fail_gate():
    require_file('docs/records/harvest/collect_v3_admission/seg/cp7/keys/sealed_decisions.jsonl.gz')
    records=fixture_records();records[0]['reader']['neighbour_whole_word']='yes'
    summary=s.summarize(records,[{'passed':True}]*10,[{'scan_ok':True}]*2)
    assert not summary['gate_pass'] and summary['matrices']['union']['FN']==1
    records[0]['reader']['neighbour_whole_word']='no'
    assert not s.summarize(records,[{'passed':True}]*10,[{'scan_ok':False}]*2)['gate_pass']

def test_known_clip_outputs_and_contact_sheet(tmp_path,monkeypatch):
    require_file('docs/records/harvest/collect_v3_admission/seg/cp7/keys/sealed_decisions.jsonl.gz')
    records=fixture_records();r=records[0];r['reader']['end_clip']='yes'
    r['sealed']['edge_clip_candidate']=True
    controls=[{'passed':True}]*10;summary=s.summarize(records,controls,[{'scan_ok':True}]*2)
    assert summary['gate_pass'] and summary['end_clip']['total']==1
    monkeypatch.setattr(s,'R2',tmp_path)
    s.write_outputs(records,controls,summary)
    sheet=(tmp_path/'ADJUDICATION_SHEET.md').read_text()
    assert 'fixture-0' in sheet and r['reader']['end_clip_reason'] in sheet
    contacts=json.loads((tmp_path/'contact_sheets.json').read_text())
    assert contacts[0]['rows']==['fixture-0']
    from PIL import Image
    with Image.open(tmp_path/contacts[0]['path']) as im:im.load();assert list(im.size)==contacts[0]['size']

@pytest.mark.skip(reason="historical binding; green at opus/seg-census@c034b3fb9; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_standalone_launcher_preflight_from_unrelated_directory(tmp_path):
    import subprocess,os
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONPATH',None)
    result=subprocess.run([sys.executable,'-B',str(CP7/'runtime_r2.py'),'verify'],cwd=tmp_path,env=env,capture_output=True,text=True)
    assert result.returncode==0,result.stderr

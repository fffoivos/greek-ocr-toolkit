"""Scoring semantics and fixed-input CP7b accounting; no new reader or detector."""
import gzip
import importlib.util
import json
import sys
from pathlib import Path
from greekocr.ops.data_root import input_path as _data_input
from tests._paths import ADMISSION, require_file
import pytest

CP7 = ADMISSION / 'seg/cp7'
sys.path.insert(0,str(CP7))
spec=importlib.util.spec_from_file_location('cp7b_score',CP7/'score_cp7b.py')
score=importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)

@pytest.mark.parametrize('field',score.RUBRIC)
def test_each_owner_rubric_bit_is_drop(field):
    answer={f:'no' for f in score.RUBRIC}
    assert not score.truth(answer)
    answer[field]='yes'
    assert score.truth(answer)

def test_confusion_direction_and_zero_denominators():
    m=score.matrix([(True,True),(True,False),(False,True),(False,False)])
    assert m==dict(TP=1,FP=1,FN=1,TN=1,precision=.5,recall=.5)
    assert score.matrix([(False,False)])['recall'] is None
    assert score.matrix([(False,True)])['precision'] is None

def test_unknown_axis_is_not_a_standalone_drop():
    seal=dict(screen_drop=True,merged=None,neighbour_words=None,orientation=None,
              geometry_unavailable=True,crossing={'drop':None})
    assert score.predictions(seal)==dict(union=True,merged=False,neighbour_words=False,
              orientation=False,geometry_unavailable=True,crossing=False)

def test_control_miss_excludes_whole_context():
    record=dict(context_valid=False,truth='DROP',reader={'rotated':'yes'},
                sealed={'orientation_unknown':True,'geometry_unavailable':True},
                predictions={f:False for f in score.SCREENS},row_id='void',mismatches={},flag=False,unreadable=False)
    s=score.summarize([record],[{'passed':False}],[{'context':'void','valid':False}])
    assert s['scored']==0 and s['void_contexts']==['void']
    assert s['matrices']['union']['TP']==s['matrices']['union']['FN']==0
    assert s['rotated']['total']==0

def test_flags_do_not_change_segmentation_truth():
    a=dict(letters='n',marks='y',crop_ok='n',errors=['crop_clipped'],detail='test')
    a.update({f:'no' for f in score.RUBRIC})
    assert score.flags(a) and not score.truth(a)

@pytest.fixture(scope='module')
def artifacts():
    return [json.loads(l) for l in gzip.open(require_file(CP7/'scored_cp7b.jsonl.gz'),'rt')]

def test_fresh_results_independently_recounted(artifacts):
    s=json.loads((_data_input(CP7/'score_summary_cp7b.json')).read_text())
    assert len(artifacts)==len({r['row_id'] for r in artifacts})==100
    assert s['controls_passed']==10 and s['void_contexts']==[]
    for screen in score.SCREENS:
        tp=fp=fn=tn=0
        for r in artifacts:
            yes=any(r['reader'][f]=='yes' for f in score.RUBRIC)
            drop=r['predictions'][screen]
            tp+=int(drop and yes);fp+=int(drop and not yes)
            fn+=int(not drop and yes);tn+=int(not drop and not yes)
        assert [s['matrices'][screen][f] for f in ('TP','FP','FN','TN')]==[tp,fp,fn,tn]
    assert [s['matrices']['union'][f] for f in ('TP','FP','FN','TN')]==[4,2,4,90]
    assert s['rotated']['admitted']==0 and s['rotated']['total']==4

def test_adjudication_coverage_and_original_crop_bytes(artifacts):
    s=json.loads((_data_input(CP7/'score_summary_cp7b.json')).read_text())
    text=(_data_input(CP7/'ADJUDICATION_SHEET.md')).read_text()
    wanted={r['row_id'] for r in artifacts if r['mismatches'] or r['flag'] or r['unreadable']}
    assert wanted==set(s['adjudication_ids']) and len(wanted)==28
    for r in artifacts:
        assert score.sha(r['crop_path'])==r['crop_sha256']
        if r['row_id'] in wanted:
            assert f"## {r['row_id']}\n" in text and r['crop_path'] in text
            for f in score.RUBRIC:assert r['reader'][f+'_reason'] in text
    assert s['orientation_unknown']['total']==21 and s['orientation_unknown']['reader_drop']==1
    assert s['geometry_unavailable']['total']==2 and s['geometry_unavailable']['reader_drop']==0

def test_contact_sheet_complete_at_most_thirty_and_decodes():
    require_file('docs/records/harvest/collect_v3_admission/seg/cp7/ADJUDICATION_SHEET.png')
    from PIL import Image
    sheets=json.loads((_data_input(CP7/'contact_sheets_cp7b.json')).read_text())
    summary=json.loads((_data_input(CP7/'score_summary_cp7b.json')).read_text())
    ids=[]
    for sheet in sheets:
        assert 0<len(sheet['rows'])<=30
        ids+=sheet['rows']
        with Image.open(_data_input(CP7/sheet['path'])) as im:
            im.load();assert list(im.size)==sheet['size']
    assert ids==summary['adjudication_ids']

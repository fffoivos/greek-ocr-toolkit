"""CP7 carried M1/M2 regressions and offline pack contracts."""
import copy
import importlib.util
import json
from pathlib import Path
from tests._paths import ADMISSION, SOL_READING
import pytest
from greekocr.harvest.admission import evaluate, non_segmentation_eligibility
from greekocr.harvest.seg_qualification import composed_requirements

@pytest.mark.parametrize('record,rule', [
    (dict(source='bsb_poly1850',label='ἑλληνικὸς λόγος',confidence=.88),'low_confidence'),
    (dict(source='archive_b24878935',wave='cyrillic',script_class='cyrillic',label='Это чистая русская строка coco'),'lookalike_only_word'),
    (dict(source='bsb_poly1850',label='ἑλληνικὸς λόγος',bbox=[0,0,100,18],page_median_line_height=10),'tall_box'),
])
def test_review_counterexamples(record,rule):
    result=evaluate(record)
    composition=non_segmentation_eligibility(result['checks'])
    assert rule in composition['rejections'] and not composition['passed']
    assert rule in result['failed_rules']

@pytest.mark.parametrize('height,rejected',[(17,False),(17.001,True)])
def test_height_boundary(height,rejected):
    r=evaluate(dict(source='bsb_poly1850',label='ἑλληνικὸς λόγος',bbox=[0,0,100,height],page_median_line_height=10))
    assert ('tall_box' in non_segmentation_eligibility(r['checks'])['rejections']) is rejected


def test_composition_includes_future_nonseg_rule():
    assert not non_segmentation_eligibility({'new_content_rule':'fail','geometry_unavailable':'fail'})['passed']
    assert non_segmentation_eligibility({'low_confidence':'n/a','tall_box':'n/a','geometry_unavailable':'fail'})['passed']


def union_fixture():
    return ({'k':'keep','d':'drop'}, {'k':dict(drop=False,geometry_unavailable=False,verified_keep=False,orientation_status='orientation_unknown'),
            'd':dict(drop=True,geometry_unavailable=False)},
            {r:dict(status='measured',drop=False) for r in ('k','d')})


def test_orientation_unknown_only_allowed():
    assert all(composed_requirements(*union_fixture()).values())

@pytest.mark.parametrize('failure',['unresolved','keep_loss','missing_separator','corrupt_separator','missing_case'])
def test_m2_incomplete_union_never_passes(failure):
    truth,union,crossing=union_fixture()
    if failure=='unresolved':union['k']['drop']=None
    if failure=='keep_loss':union['k']['drop']=True
    if failure=='missing_case':del union['k']
    if failure=='missing_separator':del crossing['k']
    if failure=='corrupt_separator':crossing['k']=dict(status='unavailable',drop=None,reason='corrupt_separator_inventory')
    assert not all(composed_requirements(truth,union,crossing).values())


def test_cp4c_policy_drop_is_not_detection():
    truth,union,crossing=union_fixture()
    union['d'].update(geometry_unavailable=True,measured_drop=None)
    crossing['d']=dict(status='unavailable',drop=None)
    assert all(composed_requirements(truth,union,crossing).values())

CP7=SEG=ADMISSION / 'seg/cp7'
import sys
sys.path.insert(0,str(CP7))
import cp7_common as cp7
import runtime as cp7_runtime


def fake_row(n,**changes):
    return dict(id=f'row{n:04}',source='bsb_poly1850',primary_class='poly1850',candidate_usable=True,**changes)


def test_deterministic_uniform_selection():
    pool=[fake_row(i) for i in range(200)]
    assert cp7.select(pool)==cp7.select(list(reversed(pool)))
    import random
    assert cp7.select(pool)==random.Random('seg-cp7:fresh100').sample(sorted(pool,key=lambda r:r['id']),100)
    assert len({r['id'] for r in cp7.select(pool)})==100


def test_fresh_locked_exclusions_but_screen_rejected_eligible():
    pool=[fake_row(i,screen_merged=True,rotated_crop=True) for i in range(105)]
    actual=cp7.population(pool,{'row0000','row0001'},{'row0002','row0003','row0004'})
    assert len(actual)==100
    assert all(r['screen_merged'] and r['rotated_crop'] for r in cp7.select(actual))

@pytest.mark.parametrize('wave',['W1','W2'])
def test_gazette_prescreen_included(wave):
    row=dict(id='gaz',source='gazette_modern',primary_class='modern_scanned',candidate_usable=True,
        gazette_stratum='measured_1986_1990',tranche=wave,screen_merged=True)
    assert cp7.included(row)
    assert not cp7.included(dict(row,gazette_stratum='other'))

@pytest.mark.parametrize('bucket',['primary','secondary'])
def test_weekly_limit_exact_window(bucket):
    assert cp7_runtime.limit(f'limit_id=codex {bucket}=77.9%/10080m reset x')==77.9
    with pytest.raises(ValueError):cp7_runtime.limit(f'limit_id=codex {bucket}=78%/10080m reset x')
    with pytest.raises(ValueError):cp7_runtime.limit('limit_id=codex primary=20%/300m reset x')


def test_canonical_scanner_and_verbatim_prompt():
    assert cp7.sha(CP7/'tools/scan_rollout.py')==cp7.SCANNER
    assert (CP7/'prompts/bsb.md').read_bytes()==(SOL_READING/'prompts/bsb.md').read_bytes()
    for sentence in ['the important thing is that really there are no full words showing from the top or bottom line, and that we use the tools we have already built for it, and that we also avoid badly segmented horizontal ones as well',
        'In general there has been at least a whole word from one of the other lines to show for it to be even worth considering for filtration']:
        assert sentence in (CP7/'prompts/segcp7_crop_rubric.md').read_text()


def synthetic_mapping():
    items=[dict(card_id='k'+f'{i:010x}') for i in range(55)]
    key=dict(readers={'r1':[r['card_id'] for r in items]},items={r['card_id']:dict(control=i>=50,line_id=f'line{i}') for i,r in enumerate(items)})
    answers=[]
    for item in items:
        a=dict(item,letters='y',marks='na',crop_ok='y',errors=[],detail='')
        for f in cp7_runtime.RUBRIC:a[f]='no';a[f+'_reason']='Synthetic mapping fixture.'
        answers.append(a)
    return answers,items,key


def test_answer_mapping_prepared_two_contexts():
    for _ in range(2):
        mapped,controls=cp7_runtime.map_records(*synthetic_mapping())
        assert len(mapped)==50 and len(controls)==5
        assert [r['line_id'] for r in mapped]==[f'line{i}' for i in range(50)]

@pytest.mark.parametrize('mutation',['missing','duplicate','order','missing_rubric','missing_reason'])
def test_mapping_rejects_incomplete_answers(mutation):
    answers,items,key=synthetic_mapping()
    if mutation=='missing':answers.pop()
    if mutation=='duplicate':answers[-1]=answers[0]
    if mutation=='order':answers.reverse()
    if mutation=='missing_rubric':del answers[0]['multi_line']
    if mutation=='missing_reason':answers[0]['rotated_reason']=''
    with pytest.raises(ValueError):cp7_runtime.map_records(answers,items,key)

@pytest.mark.parametrize('corrupt',[False,True])
def test_actual_missing_corrupt_separator_blocks_acceptance(tmp_path,monkeypatch,corrupt):
    from greekocr.harvest import separator_inventory as sep
    monkeypatch.setattr(sep,'binding',lambda page: {'frozen':'test'})
    if corrupt:
        cp7.dump(tmp_path/'receipt.json',dict(binding={'frozen':'test'},inventory_sha256='0'*64))
        cp7.dump(tmp_path/'inventory.json',dict(binding={'frozen':'test'},boundaries=[]))
    truth,union,crossings=union_fixture()
    try:sep.load({},tmp_path)
    except (ValueError,OSError) as error:crossings['k']=dict(status='unavailable',drop=None,reason=str(error))
    assert not composed_requirements(truth,union,crossings)['separator_coverage']

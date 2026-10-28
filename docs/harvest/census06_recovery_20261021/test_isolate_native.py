"""The diagnostic must not silently lose its matched controls or I/O timings."""
import copy, hashlib, pathlib, sys
import pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from isolate_native import matched_items, measure_row


def item(parent, rid, failed=False):
    return dict(observation=dict(parent_id=parent, id=rid), decision=dict(disposition='INFRA_ERROR' if failed else 'ADMIT', stages=[] if failed else [dict(stage='segmentation',result={})]))


def test_matching_rejects_missing_wrong_mix_unsuccessful_and_overlapping_controls():
    errors = [item('a','0',True), item('b','1',True)]
    controls = [item('a','2'), item('b','3')]
    v = dict(errors=errors, succeeded_controls=controls)
    assert [g for g,r in matched_items(v)] == ['former_error','succeeded_control','succeeded_control','former_error']
    for bad in [[], [item('a','2'),item('a','3')], [item('a','2',True),item('b','3')], [item('a','0'),item('b','3')]]:
        with pytest.raises(AssertionError): matched_items(dict(v,succeeded_controls=bad))
    bad=copy.deepcopy(controls);bad[0]['decision']['stages']=[]
    with pytest.raises(AssertionError): matched_items(dict(v,succeeded_controls=bad))


def test_separate_crop_and_native_timing_and_cohort(tmp_path):
    crop=tmp_path/'crop';crop.write_bytes(b'pixels')
    row=dict(parent_id='a',id='0',crop_path=str(crop),crop_sha256=hashlib.sha256(b'pixels').hexdigest(),raw_text='abc',book_id='book')
    class Worker:
        process=None
        def __call__(self, observed):
            assert observed is row
            return dict(verdict='KEEP')
    ticks=iter([0,2,10,13])
    r=measure_row(('succeeded_control',dict(observation=row,decision_insertion_position=2)),Worker(),1,clock=lambda:next(ticks))
    assert r['crop_read_seconds']==2 and r['native_seconds']==3
    assert r['cohort']=='succeeded_control' and r['status']=='PASS' and r['crop_bytes']==6
    row['crop_sha256']='0'*64
    r=measure_row(('former_error',dict(observation=row,decision_insertion_position=2)),Worker(),1)
    assert 'crop_read_error' in r # A native PASS cannot hide a crop identity failure.

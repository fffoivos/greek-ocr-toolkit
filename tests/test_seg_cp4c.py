"""Coordinator CP4c rulings: policy loss stays distinct from measurement."""
import json

import numpy as np
import pytest

from greekocr.harvest import geometry_observations as g
from greekocr.harvest.admission import evaluate, evaluate_rows, compose_segmentation_decision
from test_seg_cp2 import cached, bound_case, load
from test_seg_cp3 import invalidate_first_row


def test_inconsistent_planes_fail_closed(cached):
    row, measurement = bound_case(cached)
    # Keep the receipt/hash internally consistent, but invalidate the planes.
    path = cached[1]/'labels.npz'
    with np.load(path) as archive:
        labels = archive['labels'].copy()
    labels[0, 0] = 99
    np.savez_compressed(path, labels=labels)
    receipt_path = cached[1]/'receipt.json'
    receipt = json.loads(receipt_path.read_text())
    receipt['labels_sha256'] = g.sha(path)
    receipt_path.write_text(json.dumps(receipt))
    result = list(evaluate_rows([row], run_root=cached[3], neighbour_cache=cached[1].parent))[0]
    assert result['checks']['geometry_unavailable'] == 'fail'
    assert result['geometry_status'] == 'unavailable' and not result['passed']
    # A stale unqualified observation cannot bypass the binding check either.
    measurement['decision_status'] = 'unqualified_cp2'
    assert evaluate(row, neighbour_measurement=measurement)['failed_rules'] == ['geometry_unavailable']


def test_inverted_target_fail_closed(cached):
    invalidate_first_row(cached)
    page = load(cached)
    measurement = g.observe_crop(page, [0,0,100,30], target_row_id='row-00000')
    row, _ = bound_case_for_invalid_target(cached)
    result = evaluate(row, neighbour_measurement=measurement)
    assert measurement['reason'] == 'invalid_geometry'
    assert result['failed_rules'] == ['geometry_unavailable']
    assert result['status'] == 'fail' and not result['passed']


def bound_case_for_invalid_target(cached):
    row = dict(label='ἑλληνικὸς πλήρης λόγος', source='bsb_poly1850', primary_class='poly1850',
               page_id='page', row_id='crop', image_sha256=g.sha(cached[0]),
               crop_source_image=str(cached[0]), crop_bbox=[0,0,100,30], geometry_row_id='row-00000')
    return row, None


def test_valid_geometry_unaffected(cached):
    row, measurement = bound_case(cached)
    result = evaluate(row, neighbour_measurement=measurement)
    assert result['checks']['geometry_unavailable'] == 'pass'
    assert result['failed_rules'] == [] and result['rules_passed']
    assert result['status'] == 'unresolved' and not result['passed']  # qualification unchanged


@pytest.mark.parametrize('reason', ['ambiguous_target', 'missing_target', 'missing_or_ambiguous_target', 'unsupported_target'])
def test_unresolved_target_is_policy_loss(reason):
    result = compose_segmentation_decision(dict(status='unresolved', reason=reason, union_drop=None))
    assert result == dict(geometry_unavailable=True, drop=True)


def test_unresolved_letters_are_not_unavailable_or_verified_keep():
    assert compose_segmentation_decision(dict(status='unresolved', reason='ambiguous_letters_or_extent',
                                               union_drop=None)) == dict(geometry_unavailable=False, drop=None)


def test_composed_policy_drop_preserves_unavailable_measurement():
    observation = dict(status='unavailable', reason='invalid_source_frame_or_labels', union_drop=None)
    assert compose_segmentation_decision(observation) == dict(geometry_unavailable=True, drop=True)
    assert observation['status'] == 'unavailable' and observation['union_drop'] is None


def test_composed_valid_keep_unaffected():
    assert compose_segmentation_decision(dict(status='measured', union_drop=False)) == dict(
        geometry_unavailable=False, drop=False)

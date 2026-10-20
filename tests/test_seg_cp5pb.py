"""CP5pb diagnostic mechanics and frozen native replay regressions.

No drop rule is qualified: the ruled round fails and remains diagnostic only.
"""
import json
from pathlib import Path
from tests._paths import ADMISSION, evidence_params, require_file
import sys
import numpy as np
import pytest

SEG = ADMISSION / 'seg'
sys.path.insert(0, str(SEG))
import calibrate_cp5pb as m


def target():
    return dict(x0=0, xheight=10., meanline=np.full(100, 20.), baseline=np.full(100, 30.))


@pytest.mark.parametrize('box,role,expected', [
    ([85,20,95,30], 'letter', True),  # cut last body
    ([80,20,90,30], 'letter', False), # touching
    ([88,23,93,29], 'letter', True),  # letter-scale stop
    ([5,20,15,30], 'letter', True),   # first letter
    ([85,40,95,50], 'letter', False), # neighbour outside target band
    ([85,20,95,30], 'mark', False),
    ([85,20,95,30], 'noise', False),
    ([85,20,95,24], 'letter', False), # below half x-height
    ([85,15,95,25], 'letter', True),  # exactly half band overlap
    ([85,14,95,24], 'letter', False),
])
def test_component_mechanics(box, role, expected):
    assert bool(m.component_hits([dict(box=box, role=role)], [10,10,90,60], target())) == expected


def test_strict_tolerance_and_non_gating_counts():
    rows = [dict(row_id='nlg--fixture', status='measured', max_xh=.5),
            dict(row_id='nlg--missing', status='unavailable', max_xh=None)]
    out = m.replay_counts(rows, .5)['nlg']['non_clip']
    assert out == dict(total=2, measured=1, unavailable=1, edge_clip_candidate=0)
    assert m.replay_counts(rows, .49)['nlg']['non_clip']['edge_clip_candidate'] == 1


def test_shared_parent_h2_resolves_child_at_edge():
    from test_seg_cp4 import short_page, observe
    p=short_page(4); r=p['rows'][1]; ids=r['component_ids']
    p['labels'][np.isin(p['labels'],ids)]=0
    for cid,x in zip(ids[:2],[10,20]): p['labels'][20:30,x:x+6]=cid
    p['labels'][20:30,40:46]=ids[2]; p['labels'][20:30,48:54]=ids[2]
    p['labels'][24:25,46:48]=ids[2]; p['labels'][17:20,51:58]=ids[2]
    p['ink'][:]=p['labels']>0
    p['rows'][1]=p['ownership'].prepare_row(
        {k:v for k,v in r.items() if not k.startswith('_')},p['ink'],p['labels'])
    o=observe(p,[38,10,56,70])
    letters=[l for row in o['rows'] for g in row['groups'] for l in g['letters']]
    assert all(l['resolved'] and l['shared_parent_split'] for l in letters)
    t=target()
    assert not m.component_hits(letters,[38,10,46,60],t)
    assert m.component_hits(letters,[38,10,47,60],t)[0]['overflow_px'] == 11


def saved_cases(path):
    report = json.loads(path.read_text())
    return [r for r in report['rows'] if r['row_id'] in m.prior.CLIPS]+report['owner_keeps']

CASES = evidence_params(SEG/'CP5pb_calibration.json', saved_cases, ids=lambda r:r['row_id'])


@pytest.mark.parametrize('row', CASES)
def test_frozen_regression(row):
    hits=m.component_hits(row['examined_extents'], row['crop_box'], row['target_guides'])
    expected=max((h['overflow_px'] for h in hits), default=0)
    assert expected == row['max_px']
    if row['row_id'] in m.prior.CLIPS:
        assert bool(expected) == ('73f0e4003296ba2e' in row['row_id'])
    else:
        assert expected == 0


def test_failed_gate_and_unavailable_accounting():
    REPORT = json.loads(require_file(SEG/'CP5pb_calibration.json').read_text())
    assert REPORT['status']=='stopped->diagnostic' and REPORT['gating'] is False
    assert not any(c['passes'] for c in REPORT['curve_xh']+REPORT['curve_px'])
    assert len(REPORT['rows'])==100 and len(REPORT['owner_keeps'])==22
    assert len(REPORT['geometry_unavailable'])==2
    counts=REPORT['replay_counts']
    assert sum(c['edge_clip_candidate'] for s in counts.values() for c in s.values())==1
    assert sum(c['unavailable'] for s in counts.values() for c in s.values())==2

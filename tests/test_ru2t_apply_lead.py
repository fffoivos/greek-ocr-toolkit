"""Offline lead application regressions; no image inspection or reader invocation."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/secondary'))
import ru2t_apply_lead as f


def fixture():
    decisions = [dict(row_id=f'row-{n}', offset=0, google='ь',
                      decision='hold' if n < 6 else 'edit_hard' if n < 26 else 'keep_soft',
                      reason='original', reads={'r1': {'call': 'ъ'}, 'r3': {'call': 'ь'}})
                 for n in range(36)]
    items = [dict(d, cell=n+1, set='review' if n < 6 else 'audit',
                  sheet='review_001.png' if n < 6 else 'audit_001.png', sheet_cell=n+1)
             for n, d in enumerate(decisions)]
    return decisions, dict(cells=36, items=items)


def test_lead_labels_holds_and_reader_custody():
    ds, index = fixture()
    before = deepcopy(ds)
    changed, records = f.apply_lead(ds, index)
    out, _ = f.m.apply_version([{'id': d['row_id'], 'label': 'ь'} for d in ds], changed)
    assert [r['label'] for r in out[:6]] == ['ь', 'ь', 'ъ', 'ь', 'ъ', 'ъ']
    assert [(r['id'], r['holds']) for r in out if r['status'] == 'hold'] == [
        ('row-1', [{'offset': 0, 'reason': 'hold_yat'}]),
        ('row-3', [{'offset': 0, 'reason': 'hold_uncertain'}])]
    assert ds == before
    assert all(d['reads'] == old['reads'] for d, old in zip(changed, before))
    assert Counter(d['basis'] for d in changed if d['decision'] == 'edit_hard') == {'lead_ruling': 3, 'two_reads': 20}
    assert Counter(r['decision'] for r in records if r['status'] == 'lead_audit_confirmed') == {'edit_hard': 20, 'keep_soft': 10}


@pytest.mark.parametrize('corruption', ['duplicate', 'offset', 'missing_review', 'audit_decision', 'extra_hold'])
def test_sheet_corruption_fails_closed(corruption):
    ds, index = fixture()
    if corruption == 'duplicate':
        index['items'][1] = deepcopy(index['items'][0])
    elif corruption == 'offset':
        index['items'][0]['offset'] = 99
    elif corruption == 'missing_review':
        index['items'].pop(0)
        index['cells'] -= 1
    elif corruption == 'audit_decision':
        index['items'][6]['decision'] = 'keep_soft'
    else:
        ds.append(dict(row_id='unreviewed', offset=0, decision='hold'))
    with pytest.raises(ValueError):
        f.apply_lead(ds, index)

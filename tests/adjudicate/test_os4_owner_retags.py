"""OS4 evidence, exact OS3 continuity, and single-document placement."""
import copy

import pytest

from scripts.review.retag_owner_sheets_os4 import (
    DEST, NAMES, OUT, OWNER, apply, heading, read, supported,
)


def test_os4_only_classification_and_placement_changed():
    receipt = read(OUT/'os4_retag_audit.json')
    assert receipt['owner_retags'] == 4
    assert receipt['audit_retags'] == 14
    assert receipt['doc_ids_identical']
    assert {c['card'] for c in receipt['changes'] if c['kind'] == 'owner'} == set(OWNER)
    before = [read(DEST/'inputs'/f'os3_{name}.json') for name in NAMES]
    replay = copy.deepcopy(before)
    assert apply(replay) == receipt['changes']
    for name, old, expected in zip(NAMES, before, replay):
        actual = read(DEST/name/'spec.json')
        # OS4 remains an exact prefix; the separately tested OS5 group is additive.
        actual['groups'] = [g for g in actual['groups'] if g['id'] != 'r2a_not_adopted']
        actual['lines'] = [c for c in actual['lines'] if c['group'] != 'r2a_not_adopted']
        assert actual['groups'] == expected['groups']
        assert actual['lines'] == expected['lines']
        assert [c['line_id'] for c in old['lines']] == [c['line_id'] for c in actual['lines']]
        assert [c['doc_id'] for c in old['lines']] == [c['doc_id'] for c in actual['lines']]
        for prev, card in zip(old['lines'], actual['lines']):
            assert {k:v for k,v in prev.items() if k not in ('tags','group')} == {
                k:v for k,v in card.items() if k not in ('tags','group')}


@pytest.mark.parametrize('lid', sorted(OWNER))
def test_os4_owner_verdicts_and_placements(lid):
    s = read(DEST/NAMES[0]/'spec.json')
    c = next(c for c in s['lines'] if c['line_id'] == lid)
    g = next(g for g in s['groups'] if g['id'] == c['group'])
    assert heading(g) == OWNER[lid]
    assert supported(heading(g), c)
    assert OWNER[lid] in {t['text'] for t in c['tags']}
    if lid.startswith('ia_'):
        assert c['fault_codes'] == ['wrong_mark']
        assert all('Latin' not in t['text'] for t in c['tags'])
    else:
        assert {'crop_clipped', 'wrong_mark', 'punctuation'} == set(c['fault_codes'])
        for name in NAMES:
            sheet = read(DEST/name/'spec.json')
            card = next(c for c in sheet['lines'] if c['line_id'] == lid)
            assert 'mark error' in {t['text'] for t in card['tags']}


def test_os4_entire_failure_sheet_has_individual_support():
    s = read(DEST/NAMES[0]/'spec.json')
    groups = {g['id']:g for g in s['groups']}
    assert all(supported(heading(groups[c['group']]), c) for c in s['lines'] if c['group'] != 'r2a_not_adopted')
    for g in s['groups']:
        if 'dash' in heading(g):
            assert 'tag only, no track' in g['header']
    report = (DEST/'OS2_REPORT.md').read_text().split('## OS4:', 1)[1]
    for change in read(OUT/'os4_retag_audit.json')['changes']:
        assert change['card'] in report
        assert change['evidence'].replace('|','&#124;') in report

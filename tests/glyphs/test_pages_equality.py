"""The compatibility gate must never exempt delivered geometry or refusals."""
from copy import deepcopy
import pytest

from scripts.pages.check_q3b_equality import ALLOWLIST, compare


@pytest.mark.parametrize('family,path', [(family, path) for family, fields in ALLOWLIST.items() for path in fields])
def test_only_declared_metadata_paths_are_exempt(family, path):
    def nest(value):
        for part in reversed(path.removeprefix('$.').split('.')):
            if part.endswith('[]'):
                value = {part[:-2]: [value]}
            else:
                value = {part: value}
        return value
    result = compare(nest('old'), nest('new'), family)
    assert result['equal']
    assert len(result['metadata_differences']) == 1


@pytest.mark.parametrize('family,original,changed', [
    ('structure', {'boundaries': [{'proposal_id': 'p1'}]}, {'boundaries': [{'proposal_id': 'p2'}]}),
    ('structure', {'rows': [{'joinable': False}]}, {'rows': [{'joinable': True}]}),
    ('structure', {'rows': [{'joinable': False}]}, {'rows': [{}]}),
    ('structure', {'rejected_boundaries': [{'reason': 'unsafe'}]}, {'rejected_boundaries': [{'reason': 'safe'}]}),
    ('structure', {'crossing_evidence': [{'piece_indices': [1]}]}, {'crossing_evidence': [{'piece_indices': [2]}]}),
    ('rows', {'blocked_rows': [{'reason': 'crossing'}]}, {'blocked_rows': []}),
    ('rows', {'complete': False}, {'complete': True}),
    ('cells', {'page_size': [100.0, 200.0]}, {'page_size': [300.0, 600.0]}),
    ('stats', {'summary': {'value': 0.3}}, {'summary': {'value': 0.1 + 0.2}}),
    ('stats', {'summary': {'value': -0.0}}, {'summary': {'value': 0.0}}),
    ('stats', {'summary': {'value': 1}}, {'summary': {'value': True}}),
    ('stats', {'summary': {'units': 'a'}}, {'summary': {'units': 'b'}}),
    ('lines', [1, 2], [2, 1]),
])
def test_behavioural_changes_fail(family, original, changed):
    assert not compare(original, changed, family)['equal']


def test_metadata_comparison_never_mutates_inputs():
    before = {'provenance': {'hash': 'old'}, 'rows': [{'joinable': False}]}
    after = {'rows': [{'joinable': False}]}
    saved = deepcopy(before), deepcopy(after)
    assert compare(before, after, 'structure')['equal']
    assert (before, after) == saved

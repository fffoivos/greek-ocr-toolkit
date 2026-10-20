"""L1 release safety: HOLD, original labels, scope and paired controls."""
import copy
import json
from pathlib import Path
import pytest

from scripts.labelfix.clariden.l1_common import overlay, release, rows, write_rows, sha256, hold_reason
from scripts.labelfix.clariden.r1_common import check_disjointness

BINDING = dict(detector='s6', r1_sha256='r1', policy_sha256='policy',
               code_commit='code', detector_commit='efdf5756')


def record(identifier='one', label='α', script='greek_poly'):
    return dict(id=identifier, label=label, script_class=script, wave='round1', source='anemi', doc='round1:a')


def runtime(identifier='one', proposal='ά', recogniser='α', holds=None):
    mode = dict(text=proposal, slots=[], hold_slots=holds or [])
    return dict(id=identifier, recogniser_text=recogniser, detector=dict(text=proposal),
                modes={'PRESENCE': mode, 'FULL': copy.deepcopy(mode)})


def test_status_and_original_hash():
    r = record()
    frozen = copy.deepcopy(r)
    corrected = overlay(r, runtime(), 'presence', BINDING)
    assert corrected['status'] == 'corrected' and corrected['label'] == 'ά'
    assert corrected['changes'][0]['to'] == '\u0301'
    assert corrected['changes'][0]['letter'] == 'α'
    assert corrected['changes'][0]['evidence']['agreement'] == 'presence'
    kept = overlay(r, runtime(proposal='α'), 'presence', BINDING)
    assert kept['status'] == 'unchanged' and kept['label'] == r['label']
    # Preserve the original normalization/bytes when marks do not change.
    decomposed = record(label='α\u0301')
    assert overlay(decomposed, runtime(proposal='ά'), 'presence', BINDING)['label'] == 'α\u0301'
    assert r == frozen and len(corrected['original_label_sha256']) == 64
    compound = overlay(record(label='ἀ'), runtime(proposal='ἄ'), 'full', BINDING)
    assert compound['changes'][0]['letter'] == 'α'


@pytest.mark.parametrize('detail,reason', [
    ('mark_kind_disagreement', 'kind_disagreement'),
    ('mark_set_disagreement', 'kind_disagreement'),
    ('K1:C2:impossible_by_rule', 'k1_flag'),
    ('detector_localisation_unknown', 'localisation_unknown'),
    ('r1_unscored:bad_span', 'localisation_unknown'),
    ('r1_unsupported_letter', 'recogniser_letter_problem')])
def test_hold_status_drops_label(detail, reason):
    actual = overlay(record(), runtime(holds=[dict(start=0, base='α', reasons=[detail])]), 'full', BINDING)
    assert actual['status'] == 'hold' and 'label' not in actual
    assert actual['hold_slots'][0]['reason'] == reason


def test_letter_problem_and_print_punctuation():
    assert overlay(record(), runtime(recogniser='β'), 'presence', BINDING)['status'] == 'hold'
    assert overlay(record(), runtime(proposal='β'), 'presence', BINDING)['status'] == 'hold'
    actual = overlay(record(), runtime(proposal='“α’'), 'presence', BINDING)
    assert actual['status'] == 'corrected' and actual['label'] == '“α’'


def test_monotonic_and_other_scripts_are_out_of_scope():
    for script in ('greek_mono', 'latin', 'cyrillic', 'greek_latin_cs'):
        actual = overlay(record(script=script), None, 'full', BINDING)
        assert actual['status'] == 'out_of_scope' and 'label' not in actual


def test_planted_exclusion_document_and_line_overlap():
    selected = [record()]
    exclusions = dict(sets=dict(heldout=dict(documents=['elsewhere'], line_ids=['elsewhere'])))
    assert check_disjointness(selected, exclusions)['heldout']['line_count'] == 0
    exclusions['sets']['heldout']['documents'] = ['round1:a:human']
    with pytest.raises(ValueError, match='overlap'):
        check_disjointness(selected, exclusions)
    exclusions['sets']['heldout']['documents'] = []
    exclusions['sets']['heldout']['line_ids'] = ['one-human']
    with pytest.raises(ValueError, match='overlap'):
        check_disjointness(selected, exclusions)


def test_ctrl_subset_sets_and_original_source_untouched(tmp_path):
    selected = [record('a'), record('b', 'έ'), record('c')]
    selection, source, rt = [tmp_path / name for name in ('selection.jsonl', 'source.jsonl', 'runtime.jsonl')]
    write_rows(selection, selected)
    write_rows(source, selected + [record('mono', script='greek_mono')])
    a, b, c = runtime('a'), runtime('b', 'έ', 'ε'), runtime('c')
    c['modes']['FULL']['hold_slots'] = [dict(start=0, base='α', reasons=['mark_set_disagreement'])]
    write_rows(rt, [a, b, c])
    before = source.read_bytes()
    receipt = dict(exclusions={'held': {'line_count': 0, 'document_count': 0}}, out_of_scope={'count': 1},
                   r0_policy='outside input documents', input_documents_sha256='docs')
    release(selection, [rt], tmp_path / 'out', BINDING, source, receipt)
    assert before == source.read_bytes()
    for variant, n in [('presence', 3), ('full', 2)]:
        out = tmp_path / 'out'
        kept = {r['line_id'] for r in rows(out / f'overlay_{variant}.jsonl.gz') if r['status'] in ('corrected', 'unchanged')}
        controls = list(rows(out / f'ctrl_subset_{variant}.jsonl.gz'))
        assert {r['line_id'] for r in controls} == kept and len(kept) == n
        assert all(r['label'] == next(s['label'] for s in selected if s['id'] == r['line_id']) for r in controls)
        manifest = json.loads((out / f'release_{variant}.json').read_text())
        assert manifest['source_sha256'] == sha256(source)
        assert manifest['coverage_per_source']['anemi']['kept'] == n
        ctrl = json.loads((out / f'release_ctrl_subset_{variant}.json').read_text())
        assert ctrl['kept_line_ids_sha256'] == manifest['kept_line_ids_sha256']

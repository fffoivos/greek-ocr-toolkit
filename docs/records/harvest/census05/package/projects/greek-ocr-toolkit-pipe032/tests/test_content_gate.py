"""Owner content gate 0.3; synthetic fixtures, no readers or native work."""
import json
from pathlib import Path
from tests._paths import require_file, run_record
import sqlite3

import pytest

from test_line_pipeline import row, engine, segment, expected, answer, census_config, run
from greekocr.harvest.line_pipeline_parallel import NativePool, Observation

ARTIFACTS = Path(__file__).resolve().parents[1] / 'docs/harvest/line_pipeline/gate03'


def forbidden(*args):
    raise AssertionError('excluded row reached a downstream tool')


@pytest.mark.parametrize('text,disposition,reasons', [
    ('日', 'HOLD', ['unexpected_script']),
    ('Αθηνa', 'DROP', ['mixed_script_word', 'unexpected_script']),
    ('Αθηνa 日', 'DROP', ['mixed_script_word', 'unexpected_script']),
])
@pytest.mark.parametrize('crop_status', ['bound', 'unavailable'])
def test_exclusions_precede_crop_identity_and_segmentation(text, disposition, reasons, crop_status):
    d = engine(segmenter=forbidden, corrector=forbidden).evaluate(row(text, crop_identity_status=crop_status))
    assert d['disposition'] == disposition
    assert [r['reason'] for r in d['reasons']] == reasons
    assert len(d['stages']) == 1
    assert d['stages'][0]['excluded'] == reasons[0]
    assert all(r['status'] == 'not_run_due_to_prior_exclusion' for r in d['routes'].values())
    if disposition == 'HOLD':
        assert d['reasons'][0] == dict(reason='unexpected_script', scripts=['other'], script_counts={'other': 1}, characters=['日'])
    else:
        assert d['reasons'][0] == dict(reason='mixed_script_word', words=['Αθηνa'])


def test_mixed_word_drops_even_when_both_scripts_expected():
    d = engine(expected(scripts=['greek', 'latin']), segmenter=forbidden, corrector=forbidden).evaluate(row('Αθηνa'))
    assert d['disposition'] == 'DROP'
    assert d['reasons'] == [dict(reason='mixed_script_word', words=['Αθηνa'])]


def test_codec_mark_keeps_segmentation_and_content_repair():
    calls = []
    def observe(r):
        calls.append('segmentation')
        return segment(r)
    def correct(r, t, e):
        calls.append(t)
        return answer(r, t, 'λόγος καὶ γράμματα')
    d = engine(segmenter=observe, corrector=correct).evaluate(row('λόγος καὶ γράμματα\u0307'))
    assert [i['reason'] for i in d['stages'][0]['suspicious']] == ['unexpected_character']
    assert calls[0] == 'segmentation' and 'content_repair' in calls
    assert d['routes']['content_repair']['status'] == 'applied'
    assert d['disposition'] == 'ADMIT'


def test_clear_row_matches_pre_change_output_exactly():
    before = json.loads((ARTIFACTS / 'clear-before.json').read_text())
    assert before['pipeline_version'] == '0.3'
    before['pipeline_version'] = '0.3.2'
    assert engine().evaluate(row()) == before


@pytest.mark.parametrize('text,disposition', [('日', 'HOLD'), ('Αθηνa', 'DROP')])
def test_census_prepare_returns_empty_observation_without_cache(tmp_path, monkeypatch, text, disposition):
    # Intercept the existing coordinator callback, then retain actual pool behavior.
    original = NativePool.ordered
    observed = []
    def ordered(self, rows, prepare):
        def check(r):
            result = prepare(r)
            observed.append(result)
            assert result == Observation()
            return result
        yield from original(self, rows, check)
    monkeypatch.setattr(NativePool, 'ordered', ordered)
    config = census_config(tmp_path, [row(text)])
    config['native_workers'] = 4
    result = run(config, tmp_path / 'run', execute=True, segmenter_factory=forbidden)
    assert result['dispositions'][disposition] == 1 and observed == [Observation()]
    runtime = json.loads((tmp_path / 'run/runtime.json').read_text())
    assert runtime['native_attempts'] == runtime['cached_measurements'] == 0
    with sqlite3.connect(tmp_path / 'run/ledger.sqlite') as db:
        assert db.execute('SELECT count(*) FROM measurements').fetchone()[0] == 0


from greekocr.harvest.line_pipeline import numeric_text, final_eligibility, inventory


@pytest.mark.parametrize('text,role,bbox,reason', [
    ('αβγδεζηθι', 'prose', [0, 0, 700, 100], 'short_line'),
    ('ΑΒΓ', 'headings_caps', [0, 0, 700, 100], 'short_line'),
    ('Α.', 'prose', [0, 0, 600, 100], 'single_character_cell'),
    ('7', 'prose', [0, 0, 100, 600], 'single_character_cell'),
    ('1', 'prose', [0, 0, 700, 100], 'numeric_shape'),
    ('αβγδεζηθικ', 'prose', None, 'cell_status_unresolved'),
])
def test_length_exclusions_never_segment(text, role, bbox, reason):
    r = row(text, crop_bbox=bbox, content_role=role, crop_identity_status='unavailable')
    d = engine(segmenter=forbidden, corrector=forbidden).evaluate(r)
    assert d['disposition'] == ('HOLD' if bbox is None else 'DROP')
    assert d['reasons'][0]['reason'] == reason
    assert d['stages'][0]['excluded'] == reason and len(d['stages']) == 1
    assert all(v['status'] == 'not_run_due_to_prior_exclusion' for v in d['routes'].values())
    if reason == 'short_line':
        assert d['reasons'] == [dict(reason=reason, role=role, letters=len(text), minimum=4 if role == 'headings_caps' else 10)]
    elif reason == 'numeric_shape':
        assert d['reasons'] == [dict(reason=reason, alnum=1, detail='<=1 letter-or-digit')]
    elif reason == 'single_character_cell':
        assert d['reasons'] == [dict(reason=reason, alnum=1, A=6)]


@pytest.mark.parametrize('text,role,aspect', [
    ('αβγδεζηθικ', 'prose', 7), ('ΑΒΓΔ', 'headings_caps', 7),
    ('ΑΒ', 'prose', 6), ('1.234', 'prose', 7),
    ('XIV', 'prose', 7), ('12', 'prose', 7), ('12', 'numerics_tables', 7),
])
def test_length_passes_gate_and_final_is_idempotent(text, role, aspect):
    calls = []
    r = row(text, crop_bbox=[0, 0, 100 * aspect, 100], content_role=role)
    declaration = expected(scripts=['greek', 'latin'])
    e = engine(declaration, segmenter=lambda r: (calls.append(r['id']) or segment(r)))
    d = e.evaluate(r)
    assert calls == ['r1'] and 'excluded' not in d['stages'][0]
    issues = final_eligibility(r, text, inventory(text, e.codec), declaration, e.codec, {})
    assert not any(i['reason'] == 'short_line' for i in issues)
    assert issues == final_eligibility(r, text, inventory(text, e.codec), declaration, e.codec, {})


@pytest.mark.parametrize('text,bbox,disposition', [
    ('αβγδεζηθι', [0, 0, 700, 100], 'DROP'),
    ('Α.', [0, 0, 100, 100], 'DROP'),
    ('1', [0, 0, 700, 100], 'DROP'),
    ('λόγος', None, 'HOLD'),
])
def test_prepare_skips_new_exclusions(tmp_path, monkeypatch, text, bbox, disposition):
    # Reuse the part-1 assertion of empty Observation, no native/cache activity.
    original_config = census_config
    def config(path, rows):
        return original_config(path, [dict(r, crop_bbox=bbox) for r in rows])
    monkeypatch.setitem(globals(), 'census_config', config)
    test_census_prepare_returns_empty_observation_without_cache(tmp_path, monkeypatch, text, disposition)


def test_numeric_grammar_parity_all_four_sets():
    import runpy
    module = run_record(str(ARTIFACTS / 'part2_analysis.py'))
    for name in ('SAMPLES', 'INPUTS', 'TYPOLOGY'):
        module[name] = require_file(module[name])
    output_type = run_record(str(module['COMMON']))['output_type']
    rows = [r for group in module['sets']().values() for r in group]
    assert len(rows) == 1705
    assert all(numeric_text(r['raw_text']) == (output_type(r['raw_text']) == 'numeric') for r in rows)


def test_bound_crop_dimensions_and_rotation_free_boundary(tmp_path):
    from PIL import Image
    from greekocr.harvest.line_pipeline import crop_aspect
    p = tmp_path / 'bound.png'
    Image.new('L', (100, 600)).save(p)
    r = row('ΑΒ', crop_bbox=None, crop_path=str(p))
    assert crop_aspect(r) == 6
    assert engine().evaluate(r)['disposition'] == 'ADMIT'
    r.pop('crop_path')
    assert engine(segmenter=forbidden).evaluate(r)['reasons'] == [dict(reason='cell_status_unresolved')]


@pytest.mark.parametrize('text', ['Α\u0301.', '١ %'])
def test_marks_punctuation_and_spaces_do_not_increase_alnum(text):
    d = engine(segmenter=forbidden).evaluate(row(text, crop_bbox=[0, 0, 100, 100]))
    assert d['reasons'] == [dict(reason='single_character_cell', alnum=1, A=1)]


def test_role_precedence_and_raw_inventory_are_shared_with_final():
    r = row('ΑΒΓ', crop_bbox=[0, 0, 700, 100], content_role='numerics_tables')
    declaration = expected(content_role='headings_caps')
    e = engine(declaration, segmenter=forbidden)
    d = e.evaluate(r)
    assert d['reasons'] == [dict(reason='short_line', role='headings_caps', letters=3, minimum=4)]
    # A later label cannot rescue a raw short line.
    final = 'αβγδεζηθικ'
    assert d['reasons'][0] in final_eligibility(r, final, inventory(final, e.codec), declaration, e.codec, {})


@pytest.mark.parametrize('text,role', [
    ('ΑΒ', 'prose'), ('(Α+Γ)', 'prose'),
    ('12', 'prose'), ('12', 'numerics_tables'),
    ('fr. 91', 'numerics_tables'),
])
@pytest.mark.parametrize('bbox', [[0, 0, 600, 100], [0, 0, 100, 600]])
def test_admitted_cells_have_no_final_length_or_shape_rejection(text, role, bbox):
    calls = []
    r = row(text, content_role=role, crop_bbox=bbox)
    declaration = expected(scripts=['greek', 'latin'])
    def keep_segment(r):
        calls.append('segmentation')
        return segment(r)
    def keep_correction(r, tool, e):
        calls.append(tool)
        return answer(r, tool)
    e = engine(declaration, corrector=keep_correction, segmenter=keep_segment)
    d = e.evaluate(r)
    assert calls[0] == 'segmentation'
    assert 'excluded' not in d['stages'][0]
    assert d['disposition'] == 'ADMIT' and d['final_text'] == text
    assert final_eligibility(r, text, inventory(text, e.codec), declaration, e.codec, {}) == []


@pytest.mark.parametrize('extra,policy,reason', [
    ({'confidence': .5}, {}, 'low_confidence'),
    ({'ctc_output_steps': 1}, {}, 'ctc_infeasible'),
    ({}, {'require_ctc_steps': True}, 'ctc_steps_unavailable'),
    ({}, {'heldout_editions': ['edition']}, 'heldout_edition'),
])
def test_cell_exemption_keeps_final_nonlength_checks(extra, policy, reason):
    r = row('ΑΒ', crop_bbox=[0, 0, 100, 20], **extra)
    d = engine(policy=policy).evaluate(r)
    assert 'excluded' not in d['stages'][0]
    assert [i['reason'] for i in d['reasons']] == [reason]

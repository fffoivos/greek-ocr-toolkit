"""Owner content gate 0.3; synthetic fixtures, no readers or native work."""
import json
from pathlib import Path
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
    assert engine().evaluate(row()) == json.loads((ARTIFACTS / 'clear-before.json').read_text())


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

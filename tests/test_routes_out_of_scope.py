"""PIPE032 release scope: offline fixtures; no readers or native crops."""
import json
from pathlib import Path
import pytest

from test_line_pipeline import row, expected, answer, segment, VERSIONS, census_config
from greekocr.harvest import admission as adm
from greekocr.harvest import line_pipeline as lp
from greekocr.harvest import line_pipeline_census as census


def pipeline(scope, corrector=lambda *args: None, declaration=None):
    return lp.Pipeline(adm.load_codec(), VERSIONS,
        {'books': {'book': declaration or expected()}}, {}, segment, corrector, scope)


def forbidden(*args, **kwargs):
    raise AssertionError('out-of-scope correction was consulted')


def test_polytonic_scope_bypasses_corrector_and_automatic(monkeypatch):
    monkeypatch.setattr(lp, 'automatic_result', forbidden)
    r = row()
    d = pipeline(['polytonic'], forbidden).evaluate(r)
    assert d['disposition'] == 'ADMIT' and d['final_text'] == r['raw_text']
    assert d['routes']['polytonic'] == dict(tool='polytonic', status='not_applied_out_of_scope',
        edits=[], reason='route out of scope for this release', release_scope=['polytonic'])
    assert 'not_applied_out_of_scope' not in lp.SUCCESS
    assert not d['edits']


def test_empty_scope_missing_result_still_holds():
    d = pipeline([]).evaluate(row())
    assert d['disposition'] == 'HOLD'
    assert d['reasons'] == [dict(reason='correction_unresolved', tool='polytonic', status='required_evidence_unresolved')]
    assert d['routes']['polytonic']['reason'] == 'missing qualified tool result'


def test_missing_in_scope_numerics_still_holds():
    calls = []
    def missing(r, t, e):
        calls.append(t)
    d = pipeline(['polytonic'], missing).evaluate(row('λόγος καὶ γράμματα 1.234'))
    assert calls == ['numerics']
    assert d['disposition'] == 'HOLD'
    assert d['reasons'] == [dict(reason='correction_unresolved', tool='numerics', status='required_evidence_unresolved')]
    assert d['routes']['numerics']['reason'] == 'missing qualified tool result'
    assert d['routes']['polytonic']['status'] == 'not_applied_out_of_scope'


def test_cyrillic_edit_applied_with_polytonic_out_of_scope():
    r = row('λόγος будуть καὶ γράμματα')
    declaration = expected(scripts=['greek', 'cyrillic'], languages=['Greek', 'Russian'],
        orthographies={'cyrillic': 'historical_russian'})
    calls = []
    def correct(r, t, e):
        calls.append(t)
        return answer(r, t, r['raw_text'].replace('будуть', 'будутъ'))
    d = pipeline(['polytonic'], correct, declaration).evaluate(r)
    assert calls == ['cyrillic']
    assert d['disposition'] == 'ADMIT' and d['final_text'] == 'λόγος будутъ καὶ γράμματα'
    assert d['routes']['polytonic']['status'] == 'not_applied_out_of_scope'
    assert {t for edit in d['edits'] for t in edit['tools']} == {'cyrillic'}


@pytest.mark.parametrize('scope', [['content_repair'], ['unknown_tool']])
def test_invalid_scope_rejected_at_config_load(tmp_path, scope):
    # Rejected even before preflight can touch any config input.
    with pytest.raises(ValueError, match='routes_out_of_scope'):
        census.run({'routes_out_of_scope': scope}, tmp_path / 'never-created')
    assert not (tmp_path / 'never-created').exists()


def test_export_and_summary_and_binding(tmp_path, monkeypatch):
    monkeypatch.setattr(census.ArtifactCorrector, '__call__', forbidden)
    r = row()
    config = census_config(tmp_path, [r, dict(row('日'), id='gate')])
    Path(config['metadata']).write_text(lp.canonical({'books': {'book': expected()}}))
    config['routes_out_of_scope'] = ['polytonic']
    out = tmp_path / 'scoped'
    summary = census.run(config, out, execute=True, segmenter_factory=lambda: segment)
    admissions = {r['row_id']: r for r in map(json.loads, (out / 'admission_records.jsonl').read_text().splitlines())}
    assert admissions['r1']['pass'] and admissions['r1']['label'] == r['raw_text']
    assert admissions['r1']['corrections_not_applied'] == ['polytonic']
    assert admissions['r1']['decision']['routes']['polytonic']['status'] == 'not_applied_out_of_scope'
    assert admissions['gate']['corrections_not_applied'] == []
    assert summary['corrections_not_applied'] == {'polytonic': {'ADMIT': 1}}
    # Keep all other inputs identical; only scope changes the binding.
    monkeypatch.setattr(census.ArtifactCorrector, '__call__', lambda *args: None)
    config['routes_out_of_scope'] = []
    empty = census.run(config, tmp_path / 'empty', execute=True, segmenter_factory=lambda: segment)
    assert empty['run_binding_sha256'] != summary['run_binding_sha256']
    assert empty['dispositions']['HOLD'] == 2


@pytest.mark.parametrize('text', ['日', 'Αθηνa', 'α'])
def test_gate_exclusion_keeps_prior_exclusion_routes(text):
    p = pipeline(['polytonic'], forbidden)
    p.segmenter = forbidden
    d = p.evaluate(row(text))
    assert d['disposition'] in {'HOLD', 'DROP'}
    assert all(r['status'] == 'not_run_due_to_prior_exclusion' for r in d['routes'].values())


def test_out_of_scope_candidate_does_not_require_recheck():
    r = row('λόγος1.234 καὶ γράμματα')
    def correct(r, t, e):
        assert t == 'numerics'
        return answer(r, t, r['raw_text'].replace('1.234', '1·234'))
    d = pipeline(['polytonic'], correct).evaluate(r)
    assert d['disposition'] == 'ADMIT'
    assert d['final_text'] == 'λόγος1·234 καὶ γράμματα'
    assert d['routes']['polytonic']['status'] == 'not_applied_out_of_scope'


def test_out_of_scope_route_is_not_a_content_repair_resolver(monkeypatch):
    # Synthetic residual-character issue cleared by the qualified Cyrillic edit.
    original = lp.content_issues
    def issues(text, inv, expected, codec):
        return original(text, inv, expected, codec) + ([dict(reason='fixture_character_issue')] if 'ь' in text else [])
    monkeypatch.setattr(lp, 'content_issues', issues)
    r = row('λόγος будуть καὶ γράμματα')
    declaration = expected(scripts=['greek', 'cyrillic'], languages=['Greek', 'Russian'],
        orthographies={'cyrillic': 'historical_russian'})
    def correct(r, t, e):
        assert t in ('content_repair', 'cyrillic')
        return None if t == 'content_repair' else answer(r, t, r['raw_text'].replace('будуть', 'будутъ'))
    d = pipeline(['polytonic'], correct, declaration).evaluate(r)
    assert d['disposition'] == 'ADMIT'
    assert d['routes']['content_repair']['evidence']['resolved_by'] == ['cyrillic']

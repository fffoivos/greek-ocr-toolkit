"""SF6c packaging sums, exhaustive NFD edits, aliases and deletion zero gate."""
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.labelfix.clariden import l1r2_changes as d, l1c_census as c, l1r_recompose_ext as r
from tests.labelfix.test_l1r import fixture


@pytest.mark.parametrize('sign', ['\u0374', '\u0384', '\u02b9', "'"])
def test_keraia_deletion_not_elision(sign):
    x = d.diff_line('Ι' + sign, 'Ι', 'Ι')
    assert x['single_source_deletions_by_class'] == {'numeral_keraia': 1}
    assert not x['real_mark_correction_line']


@pytest.mark.parametrize('old,new', [('μ᾿ αὐτά', "μ' αὐτά"), ('᾿στὸν', "'στὸν"), ('᾽στὸν', 'ʼστὸν')])
def test_final_and_initial_alias_is_not_correction(old, new):
    x = d.diff_line(old, new, new)
    assert x['elision_alias'] == 1
    assert x['real_mark_change_edits'] == 0
    assert not any(x[m] for m in d.METRICS)


@pytest.mark.parametrize('quote', ['“', '«', '„', '"', '‘'])
def test_opening_quote_single_source_deletion(quote):
    x = d.diff_line(quote + 'λόγος', 'λόγος', 'λόγος')
    assert x['single_source_deletions_by_class'] == {'quote': 1}


def test_combining_edits_and_alias_are_separate():
    x = d.diff_line('᾿στὸν', "'στόν", "'στόν")
    assert x['real_mark_correction_line'] and x['real_mark_change_edits'] == 2
    assert x['elision_alias'] == 1
    assert x['single_source_deletions_by_class']['combining_mark'] == 1
    assert x['insertions_by_class']['combining_mark'] == 1


def test_consensus_deleted_and_single_source_elision_are_distinct():
    x = d.diff_line('μ᾿ αὐτά', 'μ αὐτά', "μ' αὐτά")
    assert x['consensus_elision_deleted'] == 1
    assert x['shared_deletions_by_class']['elision_apostrophe'] == 1
    assert not x['any_single_source_deletion']
    x = d.diff_line('μ᾿ αὐτά', 'μ αὐτά', 'μ αὐτά')
    assert x['consensus_elision_deleted'] == 0
    assert x['single_source_deletions_by_class']['elision_apostrophe'] == 1


def test_spacing_breathing_is_not_initial_alias():
    x = d.diff_line('᾿Αλλά', 'Ἀλλά', 'Ἀλλά')
    assert x['elision_alias'] == 0 and x['real_mark_correction_line']
    assert x['deletions_by_class']['other_mark'] == 1


def test_unaligned_source_fails_instead_of_guessing():
    with pytest.raises(ValueError, match='unaligned'):
        d.diff_line('ἄλφα', 'ἀλφα', 'βῆτα')


def test_line_dedup_examples_and_share_counts():
    b = d.empty()
    row = dict(line_id='id', status='corrected')
    x = d.diff_line('Ι\u02b9 “λόγος', 'Ι λογος', 'Ι λογος')
    d.add(b, row, x)
    assert b['corrected_status_lines'] == b['real_mark_correction_lines'] == 1
    assert b['corrected_lines_with_any_single_source_deletion'] == 1
    assert b['single_source_deletions_by_class']['numeral_keraia']['lines'] == 1
    assert b['single_source_deletions_by_class']['quote']['example_ids'] == ['id']


def test_multishard_manifest_census_and_alias_aggregation(tmp_path):
    args = fixture(tmp_path)
    out = tmp_path / 'out'
    r.recompose(**args, out=out, workers=2)
    manifests = [r.load(p) for p in sorted((out / 'shards').glob('*/release/release_presence.json'))]
    merged = r.load(out / 'release/release_presence.json')
    assert merged['release'] == 'v2-corrected-presence-sf6'
    for i, m in enumerate(manifests):
        # Deliberately nonuniform aliases expose first-shard-only aggregation.
        m['alias_only'] = i + 2
        m['coverage_per_wave']['wave1c']['alias_only'] = i + 2
        m['coverage_per_source']['test']['alias_only'] = i + 2
        p = out / 'shards' / f'shard-{i:05d}' / 'release/release_presence.json'
        r.write_json(p, m)
    # Existing aggregate remains immutable; exercise merge into a fresh location.
    import shutil
    other = tmp_path / 'merge'
    shutil.copytree(out / 'shards', other / 'shards')
    shutil.copyfile(out / 'input_verification.json', other / 'input_verification.json')
    shards = [r.load(p) for p in sorted((other / 'shards').glob('*/receipt.json'))]
    r.merge_shards(other, shards, args['selection'], list(r.rows(args['selection'])), r.VARIANTS)
    merged = r.load(other / 'release/release_presence.json')
    assert merged['alias_only'] == 5
    assert merged['coverage_per_wave']['wave1c']['alias_only'] == 5
    assert merged['coverage_per_source']['test']['alias_only'] == 5
    assert merged['elision_census']['aligned_lines'] == 2
    assert merged['elision_census_released']['both_deleted'] == 0


def test_sf6_census_integrity_restart_and_zero_gate(tmp_path, monkeypatch):
    args = fixture(tmp_path)
    out = tmp_path / 'release'
    r.recompose(**args, out=out, workers=1)
    verification, _, _ = c.verify_inputs(out)
    assert verification['policy']['schema'] == 'sf6-release-v1'
    census = tmp_path / 'census'
    receipt = d.census(out, census, workers=1)
    assert receipt['complete'] and receipt['consensus_elision_deleted'] == 0
    assert d.census(out, census, workers=1)['complete']
    p = next((census / 'partials').glob('*/counts.json'))
    p.write_text('{}')
    with pytest.raises(ValueError, match='partial'):
        d.census(out, census, workers=1)
    payload = out / 'release/overlay_presence.jsonl.gz'
    payload.write_bytes(payload.read_bytes() + b'corrupt')
    with pytest.raises(ValueError, match='SHA-256'):
        d.census(out, tmp_path / 'bad', workers=1)


def test_consensus_zero_gate_retains_incomplete_receipt(tmp_path, monkeypatch):
    args = fixture(tmp_path)
    root = tmp_path / 'release'
    r.recompose(**args, out=root, workers=1)
    real_diff = d.diff_line
    def deleted(*args):
        result = real_diff(*args)
        result['consensus_elision_deleted'] = 1
        return result
    # Thread executor keeps the deliberate synthetic violation inside this test.
    monkeypatch.setattr(d, 'ProcessPoolExecutor', d.ThreadPoolExecutor)
    monkeypatch.setattr(d, 'diff_line', deleted)
    out = tmp_path / 'census'
    with pytest.raises(ValueError, match='consensus elision deletion'):
        d.census(root, out, workers=1)
    assert c.load(out / 'receipt.json')['complete'] is False
    assert c.load(out / 'CHANGES.json')['consensus_elision_deleted'] > 0


@pytest.mark.parametrize('text', ["'Λόγος", "'Ἀλφα", "'αὐτό"])
def test_unpaired_ascii_opening_quote_before_capital_or_vowel(text):
    x = d.diff_line(text, text[1:], text[1:])
    assert x['single_source_deletions_by_class'] == {'quote': 1}

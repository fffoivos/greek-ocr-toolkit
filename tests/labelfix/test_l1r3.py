"""SF6c packaging: exact HOLD classes, applied MOVE and real audit population."""
from copy import deepcopy
import json

import pytest

from scripts.labelfix.clariden import l1c_census as c, l1r2_changes as d, l1r3_evidence as ev
from scripts.labelfix.clariden import l1r_recompose_ext as r
from tests.labelfix.test_l1r import fixture
from tests.labelfix.test_sf6 import rich


def held_row():
    kinds = ['mark', 'mark', 'quote']
    return dict(line_id='held', status='hold',
                deletion_checks=[dict(category=k, allowed=False, reason=d.SF6_PREFIX+k) for k in kinds],
                hold_slots=[dict(detail=d.SF6_PREFIX+k) for k in kinds])


def test_sf6_classes_deduplicate_lines_but_count_each_blocked_atom():
    b = d.empty(); d.add(b, held_row(), None)
    assert b['sf6_deletion_held_lines'] == 1
    assert b['sf6_deletion_holds_by_class']['mark'] == dict(lines=1, checks=2, example_ids=['held'])
    assert b['sf6_deletion_holds_by_class']['quote']['lines'] == 1
    merged = d.empty(); d.merge_bucket(merged, b); d.merge_bucket(merged, b)
    assert merged['sf6_deletion_held_lines'] == 2
    assert merged['sf6_deletion_holds_by_class']['mark'] == dict(lines=2, checks=4, example_ids=['held'])


@pytest.mark.parametrize('defect', ['released', 'missing_check', 'missing_reason', 'unknown_class'])
def test_sf6_census_rejects_inconsistent_saved_deletion_checks(defect):
    row = held_row()
    if defect == 'released': row['status'] = 'corrected'
    elif defect == 'missing_check': row['deletion_checks'].pop()
    elif defect == 'missing_reason': row['hold_slots'].pop()
    else:
        row['deletion_checks'][0]['category'] = 'unknown'
        row['hold_slots'][0]['detail'] = d.SF6_PREFIX+'unknown'
    with pytest.raises(ValueError, match='SF6'):
        d.add(d.empty(), row, None)


def test_move_count_applies_only_to_actual_release():
    row = dict(line_id='move', status='hold',
               deletion_checks=[dict(category='mark', operation='MOVE', allowed=True, reason=None)])
    b = d.empty(); d.add(b, row, None)
    assert b['sf6_move_proposal_lines'] == 1 and b['sf6_move_exceptions_applied'] == 0
    row['status'] = 'corrected'; d.add(b, row, d.diff_line('᾿Α', 'Ἀ', 'Ἀ'))
    assert b['sf6_move_proposal_lines'] == 2
    assert b['sf6_move_exceptions_applied'] == b['sf6_move_lines_applied'] == 1
    assert b['real_mark_correction_lines'] == 1


def test_two_shard_real_mark_list_is_exact_and_hash_bound(tmp_path):
    args = fixture(tmp_path); root = tmp_path/'release'; out = tmp_path/'census'
    r.recompose(**args, out=root, workers=2)
    receipt = d.census(root, out, workers=2)
    population = list(c.rows(out/d.AUDIT_LIST))
    assert population == [dict(line_id=lid, wave='wave1c', mode='ENSEMBLE_AB') for lid in ('x', 'y')]
    assert receipt['outputs'][d.AUDIT_LIST] == c.sha256(out/d.AUDIT_LIST)
    counts = c.load(out/'CHANGES.json')
    assert counts['real_mark_correction_list_rows'] == 2
    for mode in c.MODES:
        assert counts['modes'][mode]['overall']['real_mark_correction_lines'] == (2 if mode == 'ENSEMBLE_AB' else 0)
    assert d.census(root, out, workers=1)['complete']
    path = next((out/'partials').glob('*/'+d.AUDIT_LIST))
    path.write_text('')
    with pytest.raises(ValueError, match='partial'):
        d.census(root, out, workers=1)


@pytest.mark.parametrize('state', ['missing', 'null', 'true', 'scored'])
def test_availability_scans_explicit_scores_and_regions_without_defaults(tmp_path, state):
    rt = rich('δ')
    if state == 'missing':
        for key in ev.FIELDS: rt.pop(key, None)
    elif state == 'null': rt['recognition_confidence'] = None
    elif state == 'true': rt['recognition_confidence'] = True
    from scripts.labelfix.clariden.r1_common import write_rows
    write_rows(tmp_path/'shard-00000-combined.jsonl.gz', [rt])
    before = deepcopy(rt); summary = ev.scan(tmp_path)
    assert rt == before
    assert summary['counts']['lines'] == summary['counts']['slots'] == 1
    assert summary['counts']['explicit_score_lines'] == (state == 'scored')
    assert summary['counts'].get('sf6c_certified_slots', 0) == (state == 'scored')
    assert summary['counts']['regional_evidence_lines'] == (state != 'missing')
    if state == 'missing': assert summary['confidence_states'] == {'missing_key': 1}


def test_evidence_inventory_rejects_unbounded_job_stage(tmp_path):
    with pytest.raises(ValueError, match='900'):
        ev.audit([tmp_path], tmp_path/'out.json', seconds=901, selection=tmp_path/'selection.jsonl')


@pytest.mark.parametrize('value,state,certified', [
    (None, 'null', False), (True, 'invalid', False), ('0.9', 'invalid', False),
    (float('nan'), 'invalid', False), (-.1, 'invalid', False), (1.1, 'invalid', False),
    (0, 'explicit', False), (.5, 'explicit', False), (.50001, 'explicit', True), (1, 'explicit', True)])
def test_confidence_states_and_exact_sf6c_floor(value, state, certified):
    rt = rich('δ'); rt['recognition_confidence'] = value
    counts, observed = ev.observe(rt)
    assert observed == state
    assert counts[f'recognition_confidence_{state}_lines'] == 1
    assert counts[f'recognition_confidence_{state}_slots'] == 1
    assert counts['sf6c_certified_slots'] == certified


@pytest.mark.parametrize('defect', ['null', 'invalid', 'empty', 'wrong_provenance', 'outside_window', 'width_mismatch'])
def test_inventory_counts_regional_fields_but_uses_frozen_certification(defect):
    rt = rich('δ')
    if defect == 'null': rt['recognition_evidence'] = None; rt['image_width'] = None
    elif defect == 'invalid': rt['recognition_evidence'] = ['bad']; rt['image_width'] = True
    elif defect == 'empty': rt['recognition_evidence']['regions'] = []
    elif defect == 'wrong_provenance': rt['recognition_evidence']['provenance'] = 'invented'
    elif defect == 'outside_window': rt['recognition_evidence']['regions'][0]['window'] = [0, 1]
    else: rt['image_width'] = 999
    counts, state = ev.observe(rt)
    assert state == 'explicit' and counts['explicit_score_slots'] == 1
    assert counts['sf6c_certified_slots'] == 0
    assert counts['regional_evidence_slots'] == (defect in ('wrong_provenance', 'outside_window', 'width_mismatch'))
    if defect in ('null', 'invalid'):
        assert counts[f'recognition_evidence_{defect}_lines'] == 1
        assert counts[f'image_width_{defect}_slots'] == 1


def test_inventory_per_wave_uses_selected_ids_and_checks_full_population(tmp_path):
    from scripts.labelfix.clariden.r1_common import write_rows
    absent, scored = rich('δ'), rich('α')
    absent['id'], scored['id'] = 'a', 'b'
    for key in ev.FIELDS: absent.pop(key)
    path = tmp_path/'shard-00000-combined.jsonl.gz'
    write_rows(path, [absent, scored])
    waves = {'a': 'round1', 'b': 'round2'}
    result = ev.scan(tmp_path, waves, {str(path): c.sha256(path)})
    assert result['counts']['lines'] == result['counts']['slots'] == 2
    assert result['per_wave']['round1']['confidence_states'] == {'missing_key': 1}
    assert result['per_wave']['round1']['counts']['sf6c_certified_slots'] == 0
    assert result['per_wave']['round2']['counts']['sf6c_certified_slots'] == 1
    with pytest.raises(ValueError, match='SHA-256'):
        ev.scan(tmp_path, waves, {str(path): 'bad'})
    with pytest.raises(ValueError, match='population'):
        ev.scan(tmp_path, {**waves, 'c': 'round3'})
    write_rows(path, [absent, absent])
    with pytest.raises(ValueError, match='duplicate'):
        ev.scan(tmp_path, waves)


def test_job2_inventory_runs_first_and_is_bound_to_combined_receipt(tmp_path, monkeypatch):
    from scripts.labelfix.clariden import l1r2_census as job2
    args = fixture(tmp_path); root = tmp_path/'release'; out = tmp_path/'census'
    r.recompose(**args, out=root, workers=1)
    config = tmp_path/'config.json'
    c.atomic_json(config, {k: str(v) for k, v in args.items()})
    monkeypatch.delenv('SLURM_JOB_ID', raising=False)
    with pytest.raises(ValueError, match='Slurm allocation'):
        job2.run(root, out, workers=1, config=config)
    assert not out.exists()
    monkeypatch.setenv('SLURM_JOB_ID', '123')
    result = job2.run(root, out, workers=1, config=config)
    evidence = c.load(out/'evidence_availability.json')
    assert len(evidence['sources']) == 2
    for source in evidence['sources']:
        assert source['counts']['lines'] == 2
        assert source['per_wave']['wave1c']['counts']['lines'] == 2
        assert source['counts']['sf6c_certified_slots'] == 0
    assert result['outputs']['evidence_availability.json'] == c.sha256(out/'evidence_availability.json')
    assert result['complete'] and result['config_sha256'] == c.sha256(config)
    # A changed raw input fails the inventory before either downstream census.
    raw = args['ensemble_run']/'shard-00000-combined.jsonl.gz'
    raw.write_bytes(raw.read_bytes() + b'bad')
    other = tmp_path/'failed'
    with pytest.raises((ValueError, OSError, EOFError)):
        job2.run(root, other, workers=1, config=config)
    assert not other.exists()


@pytest.mark.parametrize('key,value', [('recognition_confidence', None),
    ('recognition_evidence', {'scored': False}), ('image_width', 100)])
def test_recompose_preserves_missing_optional_evidence_instead_of_defaulting(tmp_path, key, value):
    from scripts.labelfix.clariden.r1_common import write_rows
    args = fixture(tmp_path); peer = args['ensemble_run']
    payload = peer/'shard-00000-combined.jsonl.gz'
    records = list(c.rows(payload)); assert key not in records[0]
    records[0][key] = value; write_rows(payload, records)
    partial = peer/'shard-00000-receipt.json'
    receipt = c.load(partial); receipt['output_sha256'] = c.sha256(payload)
    c.atomic_json(partial, receipt)
    top = peer/'r1e_receipt.json'; receipt = c.load(top)
    receipt['shards'][0]['receipt_sha256'] = c.sha256(partial); c.atomic_json(top, receipt)
    out = tmp_path/'out'
    with pytest.raises(ValueError, match='historical evidence changed: '+key):
        r.recompose(**args, out=out, workers=1)
    assert not (out/'receipt.json').exists() and not (out/'release').exists()

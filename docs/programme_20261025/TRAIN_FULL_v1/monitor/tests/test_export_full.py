"""Local-only exporter checks, including the coordinator's captured smoke tree."""
import ast
import builtins
import csv
import datetime
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / 'export_full.py'
REPO = SCRIPT.parents[4]
SMOKE = REPO / 'out/TRAIN_FULL_v1/receipts_stage_c_sel_smoke/smoke_tree/runs'
SPEC = importlib.util.spec_from_file_location('export_full', str(SCRIPT))
exporter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(exporter)


def read_csv(out, name):
    with (out / name).open(newline='') as stream:
        return list(csv.DictReader(stream))


def put_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + '\n')


def loss(step=2, draws=512):
    return {'step': step, 'drawn_lines': draws, 'train_loss_at_step': 2.5,
            'checkpoint': {'sha256': 'checkpoint-file-sha'},
            'instruments': {name: {'ctc_loss': 1.25} for name in exporter.PANELS}}


def evaluation(step=2):
    instruments = {}
    # Unequal denominators make an arithmetic average observably wrong.
    for name, edits, units, rows in [('harvest_dev', 1, 10, 2), ('seal04_dev', 9, 30, 3),
                                    ('harvest_test', 100, 100, 20), ('seal04_test', 80, 100, 15)]:
        instruments[name] = {'rows': rows, 'score': {'cer': {
            'nfd_atom': {'edits': edits, 'reference_units': units, 'rate': edits / units},
            'nfc_char': {'rate': 0.2}, 'diacritic_insensitive': {'rate': 0.15}},
            'exact_line_rate': 0.4}}
    return {'step': step, 'instruments': instruments}


def test_smoke_counts_values_and_read_only(tmp_path, monkeypatch):
    assert SMOKE.is_dir(), 'coordinator smoke-tree input is required'
    before = {str(p): (p.stat().st_mtime_ns, p.stat().st_size,
                       hashlib.sha256(p.read_bytes()).hexdigest())
              for p in SMOKE.rglob('*') if p.is_file()}
    opened = []
    original_builtin, original_io, original_os = builtins.open, io.open, os.open

    def in_runs(path):
        if isinstance(path, int):
            return False
        resolved = Path(os.fsdecode(path)).resolve()
        return resolved == SMOKE or SMOKE in resolved.parents

    def check_mode(path, mode):
        if in_runs(path):
            opened.append(str(path))
            assert not any(flag in mode for flag in ('w', 'a', 'x', '+'))

    def builtin_open(path, mode='r', *args, **kwargs):
        check_mode(path, mode)
        return original_builtin(path, mode, *args, **kwargs)

    def io_open(path, mode='r', *args, **kwargs):
        check_mode(path, mode)
        return original_io(path, mode, *args, **kwargs)

    def os_open(path, flags, *args, **kwargs):
        if in_runs(path):
            opened.append(str(path))
            assert flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND) == 0
        return original_os(path, flags, *args, **kwargs)

    def guard_mutation(original):
        def guarded(*args, **kwargs):
            for path in args[:2]:
                if isinstance(path, (str, bytes, os.PathLike)):
                    assert not in_runs(path), 'mutation inside runs: %s' % path
            return original(*args, **kwargs)
        return guarded

    monkeypatch.setattr(builtins, 'open', builtin_open)
    monkeypatch.setattr(io, 'open', io_open)
    monkeypatch.setattr(os, 'open', os_open)
    for name in ('replace', 'rename', 'unlink', 'remove', 'mkdir', 'rmdir', 'utime', 'link', 'symlink', 'chmod'):
        monkeypatch.setattr(os, name, guard_mutation(getattr(os, name)))
    out = tmp_path / 'csv'
    assert exporter.main(['--runs', str(SMOKE), '--out', str(out)]) == 0
    assert opened
    losses = read_csv(out, 'full_loss.csv')
    cers = read_csv(out, 'full_cer.csv')
    statuses = read_csv(out, 'full_status.csv')
    assert (len(losses), len(cers), len(statuses)) == (144, 30, 6)
    for status in statuses:
        name = status['run']
        lane_loss = [r for r in losses if r['run'] == name]
        lane_cer = [r for r in cers if r['run'] == name]
        assert len(lane_loss) == 24
        assert len(lane_cer) == 5
        assert {r['instrument'] for r in lane_cer} == set(exporter.PANELS) | {'pooled_dev'}
        assert status['width'] == str(exporter.named_width(name))
        assert status['loss_points_done'] == status['loss_points_total'] == '24'
        assert status['total_updates'] == status['latest_step'] == '48'
        assert status['total_drawn_lines'] == status['latest_drawn_lines']
        assert status['pct_complete'] == '100.0'
        assert status['cer_evals_done'] == '1'
        assert status['epoch_rows'] == status['last_epoch'] == '2'
        assert status['val_cer'] == '1.000000'
        assert status['complete'] == 'true'
        assert status['segment_trace_rows'] == '48'
        assert status['segment_count'] == ('2' if name.endswith('requeue') else '1')
        assert status['yield_count'] == ('1' if name.endswith('requeue') else '0')
        assert status['last_update_utc'].endswith('Z')
        assert all(r['drawn_lines'] == status['latest_drawn_lines'] for r in lane_cer)
        first = json.loads((SMOKE / name / 'loss_eval/step-000000002.json').read_text())
        assert float(lane_loss[0]['train_loss_at_step']) == first['train_loss_at_step']
        assert lane_loss[0]['checkpoint_sha256'] == first['checkpoint']['sha256']
        for panel in exporter.PANELS:
            assert float(lane_loss[0][panel + '_loss']) == first['instruments'][panel]['ctc_loss']
        assert next(r for r in lane_cer if r['instrument'] == 'pooled_dev')['rows'] == '16787'
    after = {str(p): (p.stat().st_mtime_ns, p.stat().st_size,
                      hashlib.sha256(p.read_bytes()).hexdigest())
             for p in SMOKE.rglob('*') if p.is_file()}
    assert before == after


def test_pooling_draw_matching_and_loss_mtime(tmp_path):
    runs, out = tmp_path / 'runs', tmp_path / 'out'
    lane = runs / 'w1-full'
    point = lane / 'loss_eval/step-000000002.json'
    put_json(point, loss())
    os.utime(str(point), (1700000000, 1700000000))
    put_json(lane / 'eval/step-000000002.json', evaluation())
    put_json(lane / 'eval/step-000000004.json', evaluation(4))
    put_json(lane / 'eval/step-000000006.json', evaluation(6))
    put_json(lane / 'LIVE.json', {'step': 4, 'drawn_lines': 1024})
    # Epoch CSV is ahead of LIVE; do not attach its draws to a different step.
    (lane / 'train_log.csv').write_text('epoch,step,val_cer\n1,6,0.25\n2,8,')
    exporter.export(runs, out)
    cers = read_csv(out, 'full_cer.csv')
    pool = next(r for r in cers if r['instrument'] == 'pooled_dev')
    assert float(pool['nfd_atom_cer']) == 0.25
    assert pool['rows'] == '5'
    assert pool['nfc_char_cer'] == pool['exact_line_rate'] == ''
    for row in cers:
        assert row['drawn_lines'] == {'2': '512', '4': '1024', '6': ''}[row['step']]
    status = read_csv(out, 'full_status.csv')[0]
    assert status['total_drawn_lines'] == '12691632'
    assert status['total_updates'] == '49584'
    assert status['loss_points_total'] == '254'
    assert status['latest_step'] == '6'
    assert status['latest_drawn_lines'] == status['pct_complete'] == ''
    assert status['epoch_rows'] == status['last_epoch'] == '1'
    assert status['val_cer'] == '0.25'
    expected = datetime.datetime.fromtimestamp(1700000000, datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
    assert status['last_update_utc'] == expected


def test_torn_json_journal_dedup_and_cadence(tmp_path, monkeypatch):
    runs, out = tmp_path / 'runs', tmp_path / 'out'
    lane = runs / 'w2-full'
    lane.mkdir(parents=True)
    (lane / 'loss_eval.jsonl').write_bytes(
        (json.dumps(loss()) + '\n' + json.dumps(loss()) + '\n' + '{"step":').encode('utf-8'))
    put_json(lane / 'LOSS_CADENCE.json', {'points': [{'step': 2, 'drawn_lines': 512}],
              'count': 24, 'total_updates': 48, 'total_drawn_lines': 12288})
    put_json(lane / 'eval/step-000000002.json', evaluation())
    (lane / 'LIVE.json').write_text('{')
    (lane / 'SEGMENT_TRACE.json').write_text('{')
    (lane / 'eval/step-000000003.json').write_text('{')
    # Simulate replacement between the first and second JSON reads.
    original = exporter.json.load
    attempts = []

    def transient(stream):
        if str(stream.name).endswith('LOSS_CADENCE.json'):
            attempts.append(stream.name)
            if len(attempts) == 1:
                raise ValueError('concurrent replacement')
        return original(stream)

    monkeypatch.setattr(exporter.json, 'load', transient)
    assert exporter.export(runs, out) == (1, 5, 1)
    assert len(attempts) == 2
    assert read_csv(out, 'full_cer.csv')[0]['drawn_lines'] == '512'
    status = read_csv(out, 'full_status.csv')[0]
    assert status['loss_points_total'] == '24'
    assert status['total_updates'] == '48'
    assert status['complete'] == 'false'


def test_pending_plan_configs_and_full_defaults(tmp_path):
    runs, out = tmp_path / 'runs', tmp_path / 'out'
    put_json(tmp_path / 'PLAN.json', {'runs': [
        {'name': 'w1-full'}, {'name': 'w1.5-full'}, {'name': 'w2-full'}]})
    # Config is usable before the runs directory exists; cadence takes over later.
    put_json(tmp_path / 'configs/w1-full.json', {'total_updates': 12345})
    assert exporter.export(runs, out) == (0, 0, 3)
    statuses = read_csv(out, 'full_status.csv')
    assert [r['total_updates'] for r in statuses] == ['12345', '49584', '198312']
    for row in statuses:
        assert row['total_drawn_lines'] == '12691632'
        assert row['loss_points_total'] == '254'
        assert row['latest_step'] == row['latest_drawn_lines'] == '0'
        assert row['complete'] == 'false'
        assert row['last_update_utc'] == ''
    assert not runs.exists()


@pytest.mark.parametrize('nested', [False, True])
def test_reject_output_inside_run_tree_including_symlinks(tmp_path, nested):
    runs = tmp_path / 'runs'
    lane = runs / 'w1-full'
    lane.mkdir(parents=True)
    target = lane / 'dashboard' if nested else runs
    alias = tmp_path / 'alias'
    alias.symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError, match='outside --runs'):
        exporter.export(runs, alias)
    assert not (runs / 'full_loss.csv').exists()
    assert not (lane / 'dashboard').exists()


def test_atomic_csv_replacements(tmp_path, monkeypatch):
    runs, out = tmp_path / 'runs', tmp_path / 'out'
    (runs / 'w1-full').mkdir(parents=True)
    out.mkdir()
    (out / 'full_loss.csv').write_text('previous snapshot\n')
    original = os.replace
    replacements = []

    def replace(source, destination):
        source, destination = Path(source), Path(destination)
        assert source.parent == destination.parent == out
        assert source.name.endswith('.tmp')
        assert source.read_text().startswith('run,width,')
        if destination.name == 'full_loss.csv':
            assert destination.read_text() == 'previous snapshot\n'
        replacements.append(destination.name)
        return original(str(source), str(destination))

    monkeypatch.setattr(os, 'replace', replace)
    exporter.export(runs, out)
    assert replacements == ['full_loss.csv', 'full_cer.csv', 'full_status.csv']
    assert sorted(p.name for p in out.iterdir()) == sorted(replacements)


def test_reject_output_inside_externally_linked_run(tmp_path):
    runs = tmp_path / 'runs'
    runs.mkdir()
    actual_lane = tmp_path / 'actual_lane'
    actual_lane.mkdir()
    (runs / 'w1-full').symlink_to(actual_lane, target_is_directory=True)
    with pytest.raises(ValueError, match='outside --runs'):
        exporter.export(runs, actual_lane / 'csv')
    assert not (actual_lane / 'csv').exists()


def test_cli_and_python36_syntax(tmp_path):
    if sys.version_info >= (3, 8):
        ast.parse(SCRIPT.read_text(), feature_version=(3, 6))
    process = subprocess.run([sys.executable, '-B', str(SCRIPT), '--runs', str(SMOKE),
                              '--out', str(tmp_path / 'csv')],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    assert process.returncode == 0, process.stderr
    assert '144 loss rows, 30 CER rows, 6 status rows' in process.stdout

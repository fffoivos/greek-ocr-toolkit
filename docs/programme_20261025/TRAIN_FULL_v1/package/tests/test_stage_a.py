"""Offline measurements/requeue rehearsal; never represents CUDA throughput."""
import copy
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(PKG / 'vendor'))
from common import atomic, read, sha, spec
import stage_a as a
from stage_a_probe import binding, measure, train_rows
from test_package import mock_runtime


def point(tmp_path, width=1., workers=6, batch=64, status='OK', rate=100., stall=.01):
    return dict(binding=binding(tmp_path / 'runtime.json', width, batch, workers, 30, 300),
        status=status, lines_per_second=rate, loader_stall_share=stall,
        started_unix=width * 1000 + workers + batch * 2, ended_unix=width * 1000 + workers + batch * 2 + 1,
        gpu_uuid='gpu-%g-%d' % (width, workers), cuda_visible_devices='0',
        cpu_affinity=list(range(int(width * 1000 + workers * 24), int(width * 1000 + workers * 24) + 24)))


def test_batch_choice_requires_material_gain_and_stops_at_oom(tmp_path):
    atomic(tmp_path / 'runtime.json', {})
    points = [point(tmp_path, batch=b, rate=r) for b, r in zip(a.BATCHES, (100, 104, 108, 110, 109))]
    assert a.choose(points)[0]['binding']['batch'] == 256
    points[2]['status'] = 'OOM'
    assert a.choose(points)[0]['binding']['batch'] == 64
    points[0]['status'] = 'OOM'
    with pytest.raises(ValueError, match='no feasible'):
        a.choose(points)
    assert not a.needs_workers([point(tmp_path, stall=.099)])
    assert a.needs_workers([point(tmp_path, stall=.1)])


def test_train_inputs_never_open_test_or_dev_and_keep_half_synthetic(tmp_path):
    runtime = mock_runtime(tmp_path)
    rr = read(runtime)
    for name in ('validation', 'seal04_dev', 'seal04_test', 'harvest_dev', 'harvest_test'):
        rr['pools'][name] = dict(files=[dict(path='DO-NOT-OPEN')], rows=999)
    rows = train_rows(rr)
    assert len(rows) == 4096 and len([r for r in rows if r['_component'] == 0]) == 2048
    assert {r['split'] for r in rows} == {'train'}
    rr['components'][0]['fraction'] = .4
    rr['components'][1]['fraction'] = .6
    with pytest.raises(ValueError, match='mixture'):
        train_rows(rr)


def test_cpu_toy_measurement_uses_real_preprocessing_ctc_update_and_telemetry_schema(tmp_path, monkeypatch):
    import torch
    from train import train as t
    runtime = mock_runtime(tmp_path)
    t._runtime()
    class Toy(torch.nn.Module):
        def __init__(self, n):
            super().__init__()
            self.weight = torch.nn.Parameter(torch.zeros(n))
        def forward(self, x):
            return self.weight.expand(len(x), x.shape[-1] // 4, -1).log_softmax(-1)
    monkeypatch.setattr(t, 'build_arm', lambda head, arch, codec, **kw: Toy(codec.n_classes))
    result = measure(runtime, 1., 64, 0, 2, 3, fixture=True)
    assert result['status'] == 'OK' and result['drawn_lines'] == 192
    assert result['lines_per_second'] > 0 and len(result['samples']) == 3
    assert result['capacity_probe']['rows'] == 64 and result['ctc_health']['batches'] == 6
    assert result['gpu_uuid'] == 'MOCK-GPU' and result['telemetry'] == []


def test_lane_requeue_reuses_completed_points_and_keeps_failed_intents(tmp_path, monkeypatch):
    atomic(tmp_path / 'runtime.json', {})
    monkeypatch.setenv('SLURM_JOB_ID', '123')
    monkeypatch.setenv('SLURM_RESTART_COUNT', '0')
    calls = []
    def run(cmd, **kwargs):
        batch = int(cmd[cmd.index('--batch') + 1])
        calls.append(batch)
        if batch == 256 and len(calls) == 3:
            return SimpleNamespace(returncode=137)
        r = point(tmp_path, batch=batch, status='OOM' if batch == 512 else 'OK')
        atomic(cmd[cmd.index('--out') + 1], r)
        return SimpleNamespace(returncode=0)
    with pytest.raises(RuntimeError, match='probe failed'):
        a.lane(tmp_path / 'runtime.json', tmp_path, 1., 6, runner=run)
    first = (tmp_path / 'w1-workers6-b64.json').read_bytes()
    monkeypatch.setenv('SLURM_RESTART_COUNT', '1')
    rr = a.lane(tmp_path / 'runtime.json', tmp_path, 1., 6, runner=run)
    assert calls == [64, 128, 256, 256, 512] and rr[-1]['status'] == 'OOM'
    assert (tmp_path / 'w1-workers6-b64.json').read_bytes() == first
    assert (tmp_path / 'attempts/w1-workers6-b256-123-0/INTENT.json').exists()
    assert (tmp_path / 'attempts/w1-workers6-b256-123-1/RESULT.json').exists()
    atomic(tmp_path / 'runtime.json', dict(changed=True))
    with pytest.raises(ValueError, match='binding changed'):
        a.lane(tmp_path / 'runtime.json', tmp_path, 1., 6, runner=run)


def test_isolation_refuses_concurrent_shared_gpu_or_cpus(tmp_path):
    atomic(tmp_path / 'runtime.json', {})
    first = point(tmp_path)
    second = dict(first, gpu_uuid='other', cpu_affinity=list(range(24)))
    assert a.check_isolation([first, second])['status'] == 'PASS'
    with pytest.raises(ValueError, match='overlapping'):
        a.check_isolation([first, dict(second, gpu_uuid=first['gpu_uuid'])])
    with pytest.raises(ValueError, match='overlapping'):
        a.check_isolation([first, dict(second, cpu_affinity=first['cpu_affinity'])])


def test_mocked_node_e2e_uses_four_isolated_steps_then_conditional_workers_and_readout(tmp_path, monkeypatch):
    import verify
    runtime = tmp_path / 'runtime.json'
    atomic(runtime, dict(train_rows=793227, package_sha256='mock'))
    monkeypatch.setattr(verify, 'data_package_matches', lambda *args: True)
    commands = []
    class Process:
        def __init__(self, cmd):
            commands.append(cmd)
            width = float(cmd[cmd.index('--width') + 1])
            workers = int(cmd[cmd.index('--workers') + 1])
            for b in a.BATCHES:
                rate = b * (1.07 if workers == 12 else 1)
                r = point(tmp_path, width=width, workers=workers, batch=b, rate=rate,
                          stall=.2 if width == 2. else .01)
                atomic(tmp_path / (a.point_name(width, workers, b) + '.json'), r)
        def wait(self):
            return 0
        def poll(self):
            return 0
    monkeypatch.setattr(a.subprocess, 'Popen', Process)
    report = a.node(runtime, tmp_path)
    assert len(commands) == 5
    assert all('--gpus-per-node=1' in c and '--gpus-per-task=1' in c and '--cpus-per-task=24' in c
               and '--cpu-bind=cores' in c and '--gpu-bind=single:1' in c for c in commands)
    assert report['isolation']['status'] == 'PASS'
    assert report['checkpoints_kept'] == 0 and report['eval_instruments_opened'] == 0
    assert [s['workers'] for s in report['selections']] == [12, 6, 12]
    assert [s['study_updates'] for s in report['selections']] == [1240] * 3
    assert all(s['study_target_draws'] == 1269164 for s in report['selections'])
    assert read(tmp_path / 'STAGE_A.json')['status'] == 'MEASURED'


def test_worker_only_cuda_oom_is_a_feasibility_result(tmp_path, monkeypatch):
    import torch
    import stage_a_probe as probe
    atomic(tmp_path / 'runtime.json', {})
    output = tmp_path / 'result.json'
    monkeypatch.setattr(sys, 'argv', ['stage_a_probe.py', '--runtime', str(tmp_path / 'runtime.json'),
        '--out', str(output), '--width', '1', '--batch', '64', '--workers', '6'])
    def oom(*args, **kwargs):
        raise torch.cuda.OutOfMemoryError('test OOM')
    monkeypatch.setattr(probe, 'measure', oom)
    probe.main()
    assert read(output)['status'] == 'OOM'
    def fail(*args, **kwargs):
        raise ValueError('data integrity error')
    monkeypatch.setattr(probe, 'measure', fail)
    monkeypatch.setattr(sys, 'argv', [
        'stage_a_probe.py', '--runtime', str(tmp_path / 'runtime.json'), '--out', str(tmp_path / 'other.json'),
        '--width', '1', '--batch', '64', '--workers', '6'])
    with pytest.raises(ValueError, match='integrity'):
        probe.main()
    assert not (tmp_path / 'other.json').exists()


def test_slurm_stage_a_has_four_gpus_no_relative_time_parser_and_no_checkpoint_io():
    script = (PKG / 'stage_a.sbatch').read_text()
    for flag in ('--gpus-per-node=4', '--cpus-per-task=96', '--requeue', '--partition=preemptable'):
        assert flag in script
    assert not any(word in script for word in ('squeue', 'sacct', 'date -d', 'scontrol'))
    subprocess.run(['bash', '-n', str(PKG / 'stage_a.sbatch')], check=True)
    probe = (PKG / 'stage_a_probe.py').read_text()
    assert 'torch.save' not in probe and 'torch.load' not in probe and 'evaluate(' not in probe

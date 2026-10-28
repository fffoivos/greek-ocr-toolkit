"""Multi-node allocation evidence, including the real non-fixture collector."""
import copy
import os
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
from common import atomic, read, sha, spec
import stage_b as b
from stage_b_trial import physical_host, recover_allocations


def allocation(host='nid001', gpu='GPU-1', cpus=None, start=100., end=200.):
    return dict(physical_host=host, gpu_uuid=gpu,
        cpu_affinity=list(range(24)) if cpus is None else cpus,
        cuda_visible_devices='0', started_unix=start, ended_unix=end,
        job_id='123', restart_count=0, fixture=False)


def evidence(tmp_path, *allocations):
    # One trial/group each: same CPU numbers across groups is the real H1 case.
    groups = []
    for i, r in enumerate(allocations):
        out = tmp_path / ('trial-%d' % i)
        atomic(out / 'ALLOCATION_1.json', r)
        groups.append([dict(output=str(out))])
    return dict(groups=groups)


def test_distinct_hosts_can_reuse_cpu_numbers_and_visible_device_index(tmp_path):
    p = evidence(tmp_path, allocation(), allocation(host='nid002', gpu='GPU-2'))
    result = b.isolation(p)
    assert result['status'] == 'PASS'
    assert result['physical_hosts'] == ['nid001', 'nid002']
    assert result['allocations'] == 2


def test_same_host_cpu_collision_across_different_jobs_is_refused(tmp_path):
    p = evidence(tmp_path, allocation(), dict(allocation(gpu='GPU-2'), job_id='456'))
    with pytest.raises(ValueError, match='overlapping CPU'):
        b.isolation(p)


@pytest.mark.parametrize('host', ['nid001', 'nid002'])
def test_gpu_uuid_collision_is_global_even_across_different_hosts(tmp_path, host):
    p = evidence(tmp_path, allocation(), allocation(host=host, cpus=list(range(24, 48))))
    with pytest.raises(ValueError, match='overlapping GPU'):
        b.isolation(p)


def test_same_host_disjoint_cpus_and_gpus_pass(tmp_path):
    p = evidence(tmp_path, allocation(), allocation(gpu='GPU-2', cpus=list(range(24, 48))))
    assert b.isolation(p)['status'] == 'PASS'


@pytest.mark.parametrize('start', [200., 201.])
def test_sequential_allocations_can_reuse_all_hardware(tmp_path, start):
    p = evidence(tmp_path, allocation(), allocation(start=start, end=300.))
    assert b.isolation(p)['status'] == 'PASS'


@pytest.mark.parametrize('field', ['physical_host', 'gpu_uuid', 'cuda_visible_devices', 'cpu_affinity'])
def test_missing_attestation_is_refused(tmp_path, field):
    a = allocation()
    del a[field]
    with pytest.raises(ValueError, match='attestation'):
        b.isolation(evidence(tmp_path, a))


@pytest.mark.parametrize('start,end', [(200., 100.), (float('nan'), 200.), (100., float('inf'))])
def test_invalid_interval_is_refused(tmp_path, start, end):
    # Write ordinary evidence then patch only this test's decoded timestamps.
    p = evidence(tmp_path, allocation())
    import stage_b
    original_read = stage_b.read
    from unittest.mock import patch
    with patch.object(stage_b, 'read', side_effect=lambda path: dict(original_read(path), started_unix=start, ended_unix=end)):
        with pytest.raises(ValueError, match='interval'):
            b.isolation(p)


def test_host_attestation_uses_kernel_not_inherited_slurm_or_hostname(monkeypatch):
    monkeypatch.setenv('HOSTNAME', 'wrong')
    monkeypatch.setenv('SLURMD_NODENAME', 'wrong')
    monkeypatch.setattr(os, 'uname', lambda: SimpleNamespace(nodename='nid-physical'))
    assert physical_host() == 'nid-physical'


@pytest.mark.parametrize('new_host,collision', [('nid001', True), ('nid002', False)])
def test_recovered_allocation_keeps_original_host_and_participates_in_collisions(tmp_path, monkeypatch, new_host, collision):
    old = allocation(end=200.)
    del old['ended_unix']  # SIGKILL before the finally receipt
    p = evidence(tmp_path, old, allocation(host=new_host, gpu='GPU-2', start=150., end=250.))
    out = Path(p['groups'][0][0]['output'])
    path = out / 'ALLOCATION_1.json'
    before = path.read_bytes()
    monkeypatch.setattr(os, 'uname', lambda: SimpleNamespace(nodename='nid003'))
    recover_allocations(out, '123', 1, 200.)
    witness_path = out / 'RECOVERED_ALLOCATION_1.json'
    w = read(witness_path)
    assert path.read_bytes() == before
    assert w['prior'] == spec(path)
    assert (w['prior_physical_host'], w['next_physical_host']) == ('nid001', 'nid003')
    if collision:
        with pytest.raises(ValueError, match='overlapping CPU'):
            b.isolation(p)
    else:
        assert b.isolation(p)['status'] == 'PASS'
    w['prior_physical_host'] = 'nid-forged'
    atomic(witness_path, w)
    with pytest.raises(ValueError, match='recovery physical host'):
        b.isolation(p)


def test_recovered_gpu_collision_is_global_and_prior_sha_is_checked(tmp_path):
    old = allocation()
    del old['ended_unix']
    p = evidence(tmp_path, old, allocation(host='nid002', start=150., end=250.))
    out = Path(p['groups'][0][0]['output'])
    recover_allocations(out, '123', 1, 200.)
    with pytest.raises(ValueError, match='overlapping GPU'):
        b.isolation(p)
    changed = dict(old, physical_host='nid-changed')
    atomic(out / 'ALLOCATION_1.json', changed)
    with pytest.raises(ValueError, match='recovery binding changed'):
        b.isolation(p)


def test_missing_prior_host_cannot_be_invented_during_recovery(tmp_path):
    old = allocation()
    del old['ended_unix'], old['physical_host']
    p = evidence(tmp_path, old)
    out = Path(p['groups'][0][0]['output'])
    with pytest.raises(ValueError, match='missing prior physical host'):
        recover_allocations(out, '123', 1, 200.)
    assert not (out / 'RECOVERED_ALLOCATION_1.json').exists()


def test_production_collector_checks_multihost_isolation_without_fixture_or_mocks(tmp_path):
    # Synthetic failure receipts exercise the actual checked_plan -> isolation ->
    # collect path without loading/training a model or bypassing any checker.
    p = evidence(tmp_path, allocation(), allocation(host='nid002', gpu='GPU-2'))
    runtime, stage_a = tmp_path / 'runtime.json', tmp_path / 'STAGE_A.json'
    atomic(runtime, {})
    atomic(stage_a, {})
    p.update(fixture=False, payload_sha256=sha(PKG / 'PAYLOAD.json'),
        runtime=spec(runtime), stage_a=spec(stage_a),
        points=spec(PKG / 'study/lr_trials.jsonl'), space=spec(PKG / 'study/lr_space.json'))
    for i, group in enumerate(p['groups']):
        t = group[0]
        trial = b.make_trial(runtime, 1., b.points()[i])
        assert trial['fixture'] is False
        path = tmp_path / ('trial-%d.json' % i)
        atomic(path, trial)
        t['config'] = spec(path)
        atomic(Path(t['output']) / 'FAILURE_1.json', dict(error='synthetic infeasible trial'))
    path = tmp_path / 'PLAN.json'
    atomic(path, p)
    result = b.collect(path)  # fixture=False default, actual verify/checked_plan
    assert len(result[1.]) == 2
    assert read(tmp_path / 'ISOLATION.json')['status'] == 'PASS'
    assert all(r['status'] == 'failed' and r['val_error'] is None for r in result[1.])
    # Same-host collision is still refused on exactly this production entrypoint.
    a = Path(p['groups'][1][0]['output']) / 'ALLOCATION_1.json'
    atomic(a, allocation(gpu='GPU-2'))
    with pytest.raises(ValueError, match='overlapping CPU'):
        b.collect(path)

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
from common import atomic, bound, read, sha, spec
from test_package import mock_runtime
import stage_b as b


def env(restart=0):
    return dict(os.environ, SLURM_JOB_ID='98765', SLURM_RESTART_COUNT=str(restart),
        OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1',
        PYTHONDONTWRITEBYTECODE='1', S1_TRACE='1')


def spawn(trial, out, extra=None):
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'process.log').open('a') as log:
        return subprocess.Popen([sys.executable, '-B', str(PKG / 'tests/stage_b_mock_worker.py'),
            '--trial', str(trial), '--out', str(out)], stdout=log, stderr=log,
            env={**env(), **(extra or {})})


def stage_a_fixture(runtime, path):
    atomic(path, dict(status='MEASURED', isolation=dict(status='PASS'),
        binding=dict(runtime=spec(runtime)), selections=[dict(width_mult=w, batch=bs, workers=workers,
            lines_per_second=b.RATES[w]) for w, (bs, workers) in b.ADOPTED.items()]))
    return path


def test_frozen_points_reproduce_exact_skill_output_and_unscaled_control():
    result = subprocess.run([sys.executable, '-B', str(PKG / 'study/quasi_random.py'),
        str(PKG / 'study/lr_space.json'), '--trials', '16', '--seed', '20261025'],
        check=True, capture_output=True, text=True)
    generated = [json.loads(x) for x in result.stdout.splitlines()]
    frozen = [json.loads(x) for x in (PKG / 'study/lr_trials.jsonl').read_text().splitlines()]
    assert generated == frozen
    control = b.points()[-1]
    assert (control['learning_rate'], control['beta1'], control['weight_decay']) == (1e-4, .9, .05)


def test_horizon_is_same_draws_per_width_exact_half_and_26_points(tmp_path):
    runtime = mock_runtime(tmp_path)
    r = read(runtime)
    r['train_rows'] = 793227
    atomic(runtime, r)
    expected = {1.: 4958, 1.5: 4958, 2.: 19831}
    for w in b.ADOPTED:
        t = b.make_trial(runtime, w, b.points()[0])
        assert t['target_drawn_lines'] == 1269164
        assert t['target_drawn_lines'] % 2 == 0
        assert t['total_updates'] == expected[w]
        assert t['parameters']['epochs'] == 1
        assert t['parameters']['seed'] == 0
        assert t['instruments'] == ['seal04_dev', 'harvest_dev']
        assert len(range(50000, t['target_drawn_lines'] + 1, 50000)) + 1 == 26


def test_plan_has_51_independent_claims_13_groups_and_refuses_stage_a_changes(tmp_path):
    runtime = mock_runtime(tmp_path)
    a = stage_a_fixture(runtime, tmp_path / 'STAGE_A.json')
    p = b.build(runtime, a, tmp_path / 'study', fixture=True)
    assert len(p['groups']) == 13
    assert [len(g) for g in p['groups']] == [4] * 12 + [3]
    assert len({x['output'] for g in p['groups'] for x in g}) == 51
    for g in p['groups']:
        for x in g:
            assert read(bound(x['config']))['fixture']
    assert b.build(runtime, a, tmp_path / 'study', fixture=True) == p
    changed = read(a)
    changed['selections'][0]['batch'] = 512
    atomic(a, changed)
    with pytest.raises(ValueError, match='adopted'):
        b.build(runtime, a, tmp_path / 'other', fixture=True)


def test_pooled_cer_is_reference_units_weighted_not_average_of_rates():
    from stage_b_trial import pooled
    result = pooled(dict(seal04_dev=dict(score=dict(cer=dict(nfd_atom=dict(edits=1, reference_units=2)))),
                        harvest_dev=dict(score=dict(cer=dict(nfd_atom=dict(edits=9, reference_units=100))))))
    assert result['rate'] == 10 / 102
    assert result['rate'] != (.5 + .09) / 2


def test_beta1_default_and_validation():
    sys.path.insert(0, str(PKG / 'vendor'))
    from train import train as trainer
    assert trainer.parse_args(['--selftest']).beta1 == .9
    assert trainer.parse_args(['--selftest', '--beta1', '.97']).beta1 == .97
    for v in ('1', '-.1', 'nan'):
        with pytest.raises(SystemExit):
            trainer.parse_args(['--selftest', '--beta1', v])


def digest_state(path):
    import torch
    from train import train as trainer
    from compare import FIELDS
    trainer._runtime()
    ck = torch.load(path / 'segment.pt', map_location='cpu', weights_only=False)
    assert ck['state_sha256'] == trainer.checkpoint_state_sha256(ck)
    return trainer.checkpoint_state_sha256({k: ck[k] for k in FIELDS}), ck


def test_offline_four_lane_node_requeue_dev_only_and_collection(tmp_path, monkeypatch):
    runtime = mock_runtime(tmp_path)
    r = read(runtime)
    # Poison ALL non-study eval files: loading even one fails the rehearsal.
    for name in ('validation', 'seal04_test', 'harvest_test'):
        for f in r['pools'][name]['files']:
            f['path'] = str(tmp_path / 'FORBIDDEN_TEST_POOL')
    atomic(runtime, r)
    a = stage_a_fixture(runtime, tmp_path / 'STAGE_A.json')
    folder = tmp_path / 'smoke'
    p = b.build(runtime, a, folder, smoke=True, fixture=True)
    monkeypatch.setattr(b, 'checked_plan', lambda path: read(path))
    calls = []
    restart = [0]
    logs = []
    def popen(cmd):
        calls.append(cmd)
        trial = cmd[cmd.index('--trial')+1]
        out = Path(cmd[cmd.index('--out')+1])
        log = (out / ('mock-%d.log' % restart[0])).open('a')
        logs.append(log)
        return subprocess.Popen([sys.executable, '-B', str(PKG / 'tests/stage_b_mock_worker.py'),
            '--trial', trial, '--out', str(out)], env=env(restart[0]), stdout=log, stderr=log)
    boundary_before = os.environ.get('TF_B_ALLOCATION_BOUNDARY')
    assert b.node(folder / 'PLAN.json', 0, popen=popen) == 75
    assert os.environ.get('TF_B_ALLOCATION_BOUNDARY') == boundary_before
    for log in logs:
        log.close()
    completed = folder / 'runs/control/COMPLETE.json'
    before = completed.read_bytes()
    restart[0] = 1
    assert b.node(folder / 'PLAN.json', 0, popen=popen) == 0
    for log in logs:
        log.close()
    assert completed.read_bytes() == before
    assert len(calls) == 8
    assert all('--exclusive' in c and '--exact' in c and '--gpu-bind=single:1' in c
               and '--cpus-per-task=24' in c and '--cpu-bind=cores' in c for c in calls)
    left, x = digest_state(folder / 'runs/control')
    right, y = digest_state(folder / 'runs/requeue')
    assert left == right
    assert x['opt']['param_groups'][0]['betas'] == (.9, .999)
    from loss_journal import records
    for name in ('control', 'requeue', 'w1.5', 'w2'):
        run = folder / 'runs' / name
        entries, torn = records(run / 'loss_eval.jsonl')
        assert torn is None and [e['step'] for e in entries] == [2, 4, 6, 8]
        assert all(set(e['instruments']) == {'seal04_dev', 'harvest_dev'} for e in entries)
    result = b.collect(folder / 'PLAN.json', fixture=True)
    assert len(result[1.]) == 2 and all(r['status'] == 'ok' for rr in result.values() for r in rr)
    analyzed = subprocess.run([sys.executable, '-B', str(PKG / 'study/analyze_study.py'),
        str(folder / 'w1/results.jsonl'), '--space', str(PKG / 'study/lr_space.json'),
        '--objective', 'val_error'], capture_output=True, text=True)
    assert analyzed.returncode == 0 and '2 feasible' in analyzed.stdout
    atomic(tmp_path / 'REHEARSAL_STAGE_B.json', dict(status='PASS', mock=True,
        continuation='BIT_IDENTICAL', forced_yield=read(folder / 'runs/requeue/FORCED_YIELD.json'),
        four_subprocesses=True, real_S1_update_and_CTC=True, test_pools_poisoned=True,
        instruments=['seal04_dev', 'harvest_dev'], objective='pooled nfd_atom CER', analyze_study='PASS'))


@pytest.mark.parametrize('width', [1., 1.5, 2.])
def test_hard_kill_resume_with_nondefault_optimizer_and_no_test_access(tmp_path, width):
    runtime = mock_runtime(tmp_path)
    trial = b.make_trial(runtime, width, b.points()[3], smoke=True, fixture=True)
    trial['loss_every_drawn_lines'] = trial['parameters']['bs'] * 2
    file = tmp_path / 'trial.json'
    atomic(file, trial)
    control, split = tmp_path / 'control', tmp_path / 'split'
    c = spawn(file, control)
    assert c.wait(timeout=50) == 0, (control / 'process.log').read_text()
    c = spawn(file, split, {'TRAIN_FULL_TEST_PAUSE_LOSS_STEP': '4'})
    deadline = time.monotonic() + 40
    while not (split / 'TEST_PAUSED.json').exists() and c.poll() is None and time.monotonic() < deadline:
        time.sleep(.05)
    if not (split / 'TEST_PAUSED.json').exists():
        c.kill(); c.wait(timeout=5)
        pytest.fail((split / 'process.log').read_text())
    os.kill(c.pid, signal.SIGKILL)
    c.wait(timeout=5)
    prefix = (split / 'loss_eval.jsonl').read_bytes()
    c = spawn(file, split, {'SLURM_RESTART_COUNT': '1'})
    assert c.wait(timeout=50) == 0, (split / 'process.log').read_text()
    assert (split / 'loss_eval.jsonl').read_bytes().startswith(prefix)
    left, ck = digest_state(control)
    assert left == digest_state(split)[0]
    assert ck['opt']['param_groups'][0]['betas'] == (trial['parameters']['beta1'], .999)
    # A changed optimizer setting cannot adopt the old trial claim/state.
    trial['parameters']['beta1'] = .81
    atomic(file, trial)
    c = spawn(file, split)
    assert c.wait(timeout=50) != 0
    assert 'claim changed' in (split / 'process.log').read_text()


def test_submit_requires_current_smoke_and_focused_review(tmp_path, monkeypatch):
    payload = sha(PKG / 'PAYLOAD.json')
    plan = tmp_path / 'PLAN.json'
    atomic(plan, dict(payload_sha256=payload, runtime=dict(sha256='data'),
        groups=[[dict()] * 4, [dict()] * 3]))
    monkeypatch.setattr(b, 'checked_plan', lambda path: read(path))
    smoke = tmp_path / 'SMOKE.json'
    review = tmp_path / 'ASTRA.json'
    atomic(smoke, dict(status='BIT_IDENTICAL', mock=False, package_sha256=payload, runtime_sha256='data'))
    atomic(review, dict(status='PASS', package_sha256=payload, plan_sha256=sha(plan), smoke_sha256=sha(smoke)))
    calls = []
    def command(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout='12345;clariden\n')
    b.submit(plan, review, smoke, command=command)
    assert len(calls) == 4
    assert all('--test-only' in c for c in calls[:2])
    assert '--gpus-per-node=3' in calls[-1] and '--cpus-per-task=72' in calls[-1]
    assert not any('afterok' in x for c in calls for x in c)
    b.submit(plan, review, smoke, command=command)
    assert len(calls) == 4  # no duplicate submissions
    atomic(review, dict(status='PASS', package_sha256='old'))
    with pytest.raises(ValueError, match='focused Astra'):
        b.submit(plan, review, smoke, command=command)


def test_b2_fresh_seed_claims_and_spread_adoption(tmp_path, monkeypatch):
    runtime = mock_runtime(tmp_path)
    stage_a = stage_a_fixture(runtime, tmp_path / 'STAGE_A.json')
    parent = tmp_path / 'parent'
    p = b.build(runtime, stage_a, parent, fixture=True)
    grouped = {}
    for width in b.ADOPTED:
        entries = [t for g in p['groups'] for t in g
                   if read(t['config']['path'])['parameters']['width_mult'] == width]
        grouped[width] = [dict(trial_id=read(t['config']['path'])['trial_id'], width_mult=width,
            status='ok', val_error=.1 if i == 0 else .2,
            trial=t['config'], **{key: read(t['config']['path'])['parameters'][name]
                for key, name in [('learning_rate', 'lr'), ('beta1', 'beta1'), ('weight_decay', 'wd')]})
            for i, t in enumerate(entries)]
    monkeypatch.setattr(b, 'checked_plan', lambda path: read(path))
    monkeypatch.setattr(b, 'collect', lambda path: grouped)
    b2 = b.seeds(parent / 'PLAN.json', tmp_path / 'b2')
    assert [len(g) for g in b2['groups']] == [4, 4, 1]
    configs = [read(t['config']['path']) for g in b2['groups'] for t in g]
    assert all({c['parameters']['seed'] for c in configs if c['parameters']['width_mult'] == w} == {0, 1, 2}
               for w in b.ADOPTED)
    reruns = {w: [dict(seed=s, val_error=.1 + .005*s, status='ok') for s in (0, 1, 2)] for w in b.ADOPTED}
    monkeypatch.setattr(b, 'collect', lambda path: reruns if Path(path).parent.name == 'b2' else grouped)
    b.adoption(tmp_path / 'b2/PLAN.json', tmp_path / 'ADOPTION.json')
    result = read(tmp_path / 'ADOPTION.json')
    assert not result['stage_c_launched']
    assert all(r['adoption_rule_met'] for r in result['results'])
    reruns[1.][2]['val_error'] = .4
    b.adoption(tmp_path / 'b2/PLAN.json', tmp_path / 'ADOPTION.json')
    assert not read(tmp_path / 'ADOPTION.json')['results'][0]['adoption_rule_met']


def test_abrupt_allocation_receipt_recovery_preserves_original_and_isolation(tmp_path):
    from stage_b_trial import recover_allocations
    out = tmp_path / 'trial'
    out.mkdir()
    path = out / 'ALLOCATION_123_0_1.json'
    atomic(path, dict(job_id='123', restart_count=0, started_unix=10.,
        physical_host='nid-original',
        gpu_uuid='GPU-original', cpu_affinity=list(range(24)), cuda_visible_devices='0'))
    original = path.read_bytes()
    recover_allocations(out, '123', 1, 20.)
    assert path.read_bytes() == original
    assert b.isolation(dict(groups=[[dict(output=str(out))]]))['status'] == 'PASS'
    witness = out / ('RECOVERED_' + path.name)
    old_witness = witness.read_bytes()
    assert read(witness)['prior_physical_host'] == 'nid-original'
    assert read(witness)['next_physical_host'] == os.uname().nodename
    recover_allocations(out, '124', 0, 30.)
    assert witness.read_bytes() == old_witness


def test_unfinished_same_allocation_is_not_silently_closed(tmp_path):
    from stage_b_trial import recover_allocations
    atomic(tmp_path / 'ALLOCATION_123_0_1.json', dict(job_id='123', restart_count=0, started_unix=10.))
    with pytest.raises(ValueError, match='same-allocation'):
        recover_allocations(tmp_path, '123', 0, 20.)

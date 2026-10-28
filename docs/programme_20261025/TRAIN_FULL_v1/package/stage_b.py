"""Stage B plan, four-lane scheduler entry, collection, smoke and B2 setup.

No scheduler command is invoked except in the explicit owner-run node/submit
commands. Plans and each trial claim are immutable; retries retain all attempts.
"""
import argparse
import fcntl
import json
import math
import os
from pathlib import Path
import signal
import statistics
import subprocess
import sys
import time

from common import atomic, bound, read, rows, sha, spec

ROOT = Path(__file__).resolve().parent
ADOPTED = {1.: (256, 6), 1.5: (256, 6), 2.: (64, 6)}
RATES = {1.: 425.8, 1.5: 368.4, 2.: 309.8}  # coordinator receipt; plan reads measured JSON


def immutable(path, value):
    if Path(path).exists():
        if read(path) != value:
            raise ValueError('immutable binding changed: ' + str(path))
    else:
        atomic(path, value)


def points():
    pp = list(rows(ROOT / 'study/lr_trials.jsonl'))
    if len(pp) != 16 or [p['trial_id'] for p in pp] != list(range(16)):
        raise ValueError('16 frozen Halton points required')
    return [dict(p, trial_id='h%02d' % p['trial_id']) for p in pp] + [dict(
        trial_id='control', learning_rate=1e-4, beta1=.9, weight_decay=.05, sampler='S1_unscaled')]


def make_trial(runtime, width, point, *, smoke=False, seed=0, fixture=False):
    rt = read(runtime)
    bs, workers = ADOPTED[width]
    # Round 10% upward to a whole real+synthetic pair, retaining exact 1/2.
    target = 2 * math.ceil(8 * rt.get('train_rows', 8) / 10)
    target = bs * 40 if smoke else target
    if fixture:
        target = bs * 8
    total = math.ceil(target / bs)
    return dict(schema='TRAIN_FULL-stage-B-trial-v1', runtime=spec(runtime),
        payload_sha256=sha(ROOT / 'PAYLOAD.json'), trial_id=point['trial_id'],
        parameters=dict(width_mult=width, bs=bs, workers=workers, lr=point['learning_rate'],
            beta1=point['beta1'], wd=point['weight_decay'], seed=seed, epochs=1, epoch_rows=target),
        total_updates=total, target_drawn_lines=target,
        loss_every_drawn_lines=bs * (2 if fixture else 8) if smoke else 50000,
        instruments=['seal04_dev', 'harvest_dev'], final_objective='pooled nfd_atom CER',
        test_policy='NO test loading/evaluation/selection',
        smoke=smoke, fixture=fixture)


def build(runtime, stage_a, out, *, smoke=False, fixture=False):
    if not fixture:
        from verify import verify, data_package_matches
        verify()
        if not data_package_matches(read(runtime).get('package_sha256'), runtime):
            raise ValueError('foreign prepared data')
    a = read(stage_a)
    if a['status'] != 'MEASURED' or a['isolation']['status'] != 'PASS':
        raise ValueError('measured Stage A isolation PASS required')
    if a['binding']['runtime']['sha256'] != sha(runtime):
        raise ValueError('Stage A data differs')
    selections = {r['width_mult']: r for r in a['selections']}
    if set(selections) != set(ADOPTED) or any(
        (selections[w]['batch'], selections[w]['workers']) != ADOPTED[w] for w in ADOPTED):
        raise ValueError('Stage A adopted batch/workers changed')
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'PLAN.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        plans = []
        if smoke:
            control = points()[-1]
            for name, width, forced in [('control', 1., None), ('requeue', 1., 12),
                                        ('w1.5', 1.5, None), ('w2', 2., None)]:
                t = make_trial(runtime, width, dict(control, trial_id=name), smoke=True, fixture=fixture)
                if forced:
                    t['force_requeue_step'] = 3 if fixture else forced
                path = out / 'trials' / (name + '.json')
                immutable(path, t)
                plans.append(dict(config=spec(path), output=str(out / 'runs' / name)))
        else:
            for width in ADOPTED:
                for point in points():
                    t = make_trial(runtime, width, point, fixture=fixture)
                    name = 'w%g-%s' % (width, point['trial_id'])
                    path = out / 'trials' / (name + '.json')
                    immutable(path, t)
                    plans.append(dict(config=spec(path), output=str(out / 'runs' / name)))
        plan = dict(schema='TRAIN_FULL-stage-B-plan-v1', payload_sha256=sha(ROOT / 'PAYLOAD.json'),
            runtime=spec(runtime), stage_a=spec(stage_a), smoke=smoke, fixture=fixture,
            groups=[plans[i:i+4] for i in range(0, len(plans), 4)], selections=a['selections'],
            points=spec(ROOT / 'study/lr_trials.jsonl'), space=spec(ROOT / 'study/lr_space.json'),
            resource_policy='four independent GPUs; one GPU + 24 disjoint CPUs + 6 workers/trial')
        immutable(out / 'PLAN.json', plan)
    return plan


def checked_plan(path):
    from verify import verify
    verify()
    p = read(path)
    if p['fixture'] or p['payload_sha256'] != sha(ROOT / 'PAYLOAD.json'):
        raise ValueError('foreign/fixture study plan')
    for s in (p['runtime'], p['stage_a'], p['points'], p['space']):
        bound(s)
    for group in p['groups']:
        for t in group:
            bound(t['config'])
    return p


def node(plan_path, group, *, popen=subprocess.Popen):
    p = checked_plan(plan_path)
    g = p['groups'][group]
    controls = Path(plan_path).parent / 'node-controls'
    controls.mkdir(exist_ok=True)
    with (controls / ('group-%03d.lock' % group)).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Before ANY new lane starts, bound the end of a previous Slurm
        # allocation that was killed before its final attestation could publish.
        previous_boundary = os.environ.get('TF_B_ALLOCATION_BOUNDARY')
        os.environ['TF_B_ALLOCATION_BOUNDARY'] = str(time.time())
        processes = []
        def warning(*_):
            # srun forwards TERM to the Python process; Segment commits at an
            # optimizer boundary. Keep waiting for durable writes/eval finishes.
            for proc in processes:
                if proc.poll() is None:
                    proc.send_signal(signal.SIGTERM)
        old = signal.signal(signal.SIGTERM, warning)
        try:
            for t in g:
                Path(t['output']).mkdir(parents=True, exist_ok=True)
                cmd = ['srun', '--exclusive', '--exact', '--nodes=1', '--ntasks=1',
                    '--gpus-per-node=1', '--gpus-per-task=1', '--cpus-per-task=24',
                    '--cpu-bind=cores', '--gpu-bind=single:1', '--open-mode=append',
                    '--output=' + str(Path(t['output']) / 'srun-%j.log'),
                    sys.executable, '-B', str(ROOT / 'stage_b_trial.py'),
                    '--trial', str(bound(t['config'])), '--out', t['output']]
                processes.append(popen(cmd))
            codes = [x.wait() for x in processes]
        finally:
            signal.signal(signal.SIGTERM, old)
            for proc in processes:
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait()
            if previous_boundary is None:
                os.environ.pop('TF_B_ALLOCATION_BOUNDARY', None)
            else:
                os.environ['TF_B_ALLOCATION_BOUNDARY'] = previous_boundary
        if any(c not in (0, 75) for c in codes):
            raise RuntimeError('trial failure; inspect retained per-trial log/FAILURE: ' + str(codes))
        return 75 if 75 in codes else 0


def submit(plan_path, review_path, smoke_report, *, command=subprocess.run):
    p = checked_plan(plan_path)
    review, smoke = read(review_path), read(smoke_report)
    if (review.get('status') != 'PASS' or review.get('plan_sha256') != sha(plan_path)
            or review.get('package_sha256') != p['payload_sha256']
            or review.get('smoke_sha256') != sha(smoke_report)
            or smoke.get('status') != 'BIT_IDENTICAL' or smoke.get('mock') is not False
            or smoke.get('package_sha256') != p['payload_sha256']
            or smoke.get('runtime_sha256') != p['runtime']['sha256']):
        raise ValueError('focused Astra PASS binding this plan + CUDA smoke required')
    controls = Path(plan_path).parent / 'submit-controls'
    controls.mkdir(exist_ok=True)
    # Dry check all requested groups before submitting any. Completed/purged
    # predecessors are irrelevant: all groups are independent, no dependencies.
    with (controls / 'SUBMIT.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        commands = []
        for i, group in enumerate(p['groups']):
            cmd = ['sbatch', '--parsable', '--export=ALL', '--gpus-per-node=%d' % len(group),
                '--cpus-per-task=%d' % (24 * len(group)),
                '--output=' + str(controls / ('group-%03d-%%j.log' % i)),
                str(ROOT / 'stage_b.sbatch'), str(Path(plan_path).resolve()), str(i)]
            commands.append(cmd)
            if not (controls / ('group-%03d.json' % i)).exists():
                command([*cmd[:1], '--test-only', *cmd[1:]], check=True, text=True, capture_output=True)
        for i, cmd in enumerate(commands):
            receipt = controls / ('group-%03d.json' % i)
            if receipt.exists():
                r = read(receipt)
                if r['plan_sha256'] != sha(plan_path) or r['command'] != cmd:
                    raise ValueError('submission claim changed')
                print(r['job_id'])
                continue
            intent = controls / ('group-%03d.INTENT.json' % i)
            if intent.exists():
                raise ValueError('submission intent without receipt: reconcile scheduler; never double-submit')
            atomic(intent, dict(command=cmd, plan_sha256=sha(plan_path)))
            done = command(cmd, check=True, text=True, capture_output=True)
            job = done.stdout.strip().split(';')[0]
            if not job.isdigit():
                raise ValueError('unparseable job id; retain intent and reconcile')
            atomic(receipt, dict(job_id=job, plan_sha256=sha(plan_path), command=cmd,
                                review=spec(review_path), smoke=spec(smoke_report)))
            print(job)


def collect(plan_path, *, fixture=False):
    from stage_b_trial import pooled, validate_complete
    p = read(plan_path) if fixture else checked_plan(plan_path)
    out = Path(plan_path).parent
    if not fixture:
        atomic(out / 'ISOLATION.json', isolation(p))
    grouped = {}
    for group in p['groups']:
        for t in group:
            trial, folder = read(bound(t['config'])), Path(t['output'])
            par = trial['parameters']
            r = dict(trial_id=trial['trial_id'], seed=par['seed'], width_mult=par['width_mult'],
                batch_size=par['bs'], learning_rate=par['lr'], beta1=par['beta1'], weight_decay=par['wd'],
                max_steps=trial['total_updates'], objective_policy='FINAL dev CER only; no retrospective checkpoint selection',
                trial=spec(bound(t['config'])))
            if (folder / 'COMPLETE.json').exists():
                c = validate_complete(folder, trial)
                final = read(bound(c['evaluations'][0]))
                objective = pooled(final['instruments'])
                if objective != c['pooled_dev']:
                    raise ValueError('objective changed')
                import csv
                with (folder / 'train_log.csv').open() as f:
                    log = list(csv.DictReader(f))[-1]
                r.update(status='ok', val_error=objective['rate'], pooled_dev=objective,
                    dev_metrics=final['instruments'], final_step=trial['total_updates'],
                    train_loss=float(log['train_loss']), complete=spec(folder / 'COMPLETE.json'))
            else:
                failures = [read(v) for v in sorted(folder.glob('FAILURE_*.json'))]
                if not failures:
                    raise ValueError('trial pending/interrupted without a final result: ' + str(folder))
                # Infeasible/failed objectives remain null, never a fake bad CER.
                r.update(status='failed', val_error=None, failures=failures)
            grouped.setdefault(par['width_mult'], []).append(r)
    for w, rr in grouped.items():
        target = out / ('w%g' % w) / 'results.jsonl'
        target.parent.mkdir(exist_ok=True)
        tmp = target.with_suffix('.jsonl.tmp')
        tmp.write_text(''.join(json.dumps(r, sort_keys=True, allow_nan=False) + '\n' for r in rr))
        tmp.replace(target)
    return grouped


def isolation(plan):
    """CPU numbers are host-local; GPU UUIDs are globally unique.

    Every attempt participates, including killed attempts whose original intent
    is bound by a separate recovery witness. Endpoint equality is nonoverlap.
    Stage A's historical single-node checker/report is left unchanged.
    """
    active = []
    for group in plan['groups']:
        for t in group:
            for path in Path(t['output']).glob('ALLOCATION_*.json'):
                r = read(path)
                if 'ended_unix' not in r:
                    recovery = Path(t['output']) / ('RECOVERED_' + path.name)
                    witness = read(recovery)
                    if witness['prior'] != spec(path):
                        raise ValueError('allocation recovery binding changed')
                    if (not witness.get('next_physical_host') or not r.get('physical_host')
                            or witness.get('prior_physical_host') != r['physical_host']):
                        raise ValueError('allocation recovery physical host changed/missing')
                    r['ended_unix'] = witness['ended_upper_bound_unix']
                active.append(r)
    if not active:
        raise ValueError('no lane attestations')
    for i, a in enumerate(active):
        if (not a.get('physical_host') or not a.get('cuda_visible_devices')
                or not a.get('gpu_uuid') or len(a.get('cpu_affinity', [])) < 24):
            raise ValueError('missing per-lane physical host/GPU/CPU attestation')
        if not (math.isfinite(a['started_unix']) and math.isfinite(a['ended_unix'])
                and a['started_unix'] <= a['ended_unix']):
            raise ValueError('invalid allocation interval')
        for b in active[:i]:
            if max(a['started_unix'], b['started_unix']) < min(a['ended_unix'], b['ended_unix']):
                if a['gpu_uuid'] == b['gpu_uuid']:
                    raise ValueError('overlapping GPU assignments')
                if (a['physical_host'] == b['physical_host']
                        and set(a['cpu_affinity']) & set(b['cpu_affinity'])):
                    raise ValueError('overlapping CPU assignments on physical host')
    return dict(status='PASS', allocations=len(active),
        physical_hosts=sorted({a['physical_host'] for a in active}),
        scope='global GPU UUID + same-physical-host CPU affinity during overlapping intervals; shared storage contention remains measured')


def smoke_readout(plan_path, out):
    p = checked_plan(plan_path)
    if not p['smoke'] or len(p['groups']) != 1 or len(p['groups'][0]) != 4:
        raise ValueError('four-lane smoke required')
    from compare import FIELDS
    from stage_b_trial import validate_complete
    sys.path.insert(0, str(ROOT / 'vendor'))
    from train import train as trainer
    trainer._runtime()
    torch = trainer.torch
    trials = {read(t['config']['path'])['trial_id']: t for t in p['groups'][0]}
    checkpoints = []
    for name in ('control', 'requeue'):
        t = trials[name]
        validate_complete(t['output'], read(bound(t['config'])))
        ck = torch.load(Path(t['output']) / 'segment.pt', map_location='cpu', weights_only=False)
        if ck['state_sha256'] != trainer.checkpoint_state_sha256(ck):
            raise ValueError('invalid smoke checkpoint digest')
        checkpoints.append(ck)
    if any(ck['binding']['device'] != 'cuda' or ck['binding']['workers'] != 6 for ck in checkpoints):
        raise ValueError('smoke CUDA/six-worker profile changed')
    if trainer.checkpoint_state_sha256({k: checkpoints[0][k] for k in FIELDS}) != trainer.checkpoint_state_sha256(
            {k: checkpoints[1][k] for k in FIELDS}):
        raise ValueError('smoke continuation not BIT_IDENTICAL')
    resumed = Path(trials['requeue']['output'])
    yielded = read(resumed / 'FORCED_YIELD.json')
    y = torch.load(bound(yielded['checkpoint']), map_location='cpu', weights_only=False)
    if y['global_step'] != 12 or yielded['step'] != 12 or y['state_sha256'] != trainer.checkpoint_state_sha256(y):
        raise ValueError('forced step-12 yield not durable')
    allocations = [read(f) for f in resumed.glob('ALLOCATION_*.json')]
    if not any(r['job_id'] == yielded['job_id'] and r['restart_count'] > yielded['restart_count'] for r in allocations):
        raise ValueError('actual Slurm requeue evidence missing')
    left, right = (read(Path(trials[n]['output']) / 'COMPLETE.json') for n in ('control', 'requeue'))
    if left['binding']['loss_plan'] != right['binding']['loss_plan'] or left['binding']['loss_plan']['steps'] != [8, 16, 24, 32, 40]:
        raise ValueError('five loss points must straddle forced requeue')
    for step in (8, 16, 24, 32, 40):
        results = [read(Path(trials[n]['output']) / 'loss_eval' / ('step-%09d.json' % step))
                   for n in ('control', 'requeue')]
        if any(results[0][k] != results[1][k] for k in ('step', 'drawn_lines', 'thresholds', 'model_sha256', 'instruments')):
            raise ValueError('smoke loss differs across requeue')
    if read(bound(left['evaluations'][0]))['instruments'] != read(bound(right['evaluations'][0]))['instruments']:
        raise ValueError('final dev CER differs')
    costs = []
    for name in ('control', 'w1.5', 'w2'):
        t = trials[name]
        c = validate_complete(t['output'], read(bound(t['config'])))
        timings = [read(f) for f in Path(t['output']).glob('BATCH_TIMING_*.json')]
        if not timings or not sum(r['samples'] for r in timings):
            raise ValueError('smoke update timing missing')
        update = sum(r['seconds'] for r in timings) / sum(r['samples'] for r in timings)
        losses = [read(bound(s))['elapsed_seconds'] for s in c['loss_evaluations']]
        full = read(bound(c['evaluations'][0]))['elapsed_seconds']
        width = read(bound(t['config']))['parameters']['width_mult']
        sel = next(s for s in p['selections'] if s['width_mult'] == width)
        target = 2 * math.ceil(8 * read(bound(p['runtime']))['train_rows'] / 10)
        train_seconds = target / sel['lines_per_second']
        loss_seconds = 26 * max(losses)
        ratio = (loss_seconds + full) / train_seconds
        costs.append(dict(width_mult=width, mean_smoke_update_seconds=update,
            loss_eval_seconds_mean=statistics.mean(losses), loss_eval_seconds_max=max(losses),
            final_dev_cer_seconds=full, trial_training_seconds_stage_a=train_seconds,
            trial_eval_seconds=loss_seconds + full, trial_loss_evals=26,
            projected_eval_over_training=ratio, exceeds_25_percent=ratio > .25,
            study17_GPU_hours=17 * (train_seconds + loss_seconds + full) / 3600,
            seed3_GPU_hours=3 * (train_seconds + loss_seconds + full) / 3600,
            options_if_over_25_percent=['retain full dev cadence and budget measured overhead',
                'owner may choose a larger loss cadence in a separately bound plan',
                'optimize the identical full-coverage loss evaluator and requalify; never silently subsample']))
    atomic(out, dict(status='BIT_IDENTICAL', mock=False, plan=spec(plan_path),
        package_sha256=p['payload_sha256'], runtime_sha256=p['runtime']['sha256'],
        compared_fields=list(FIELDS), forced_yield=yielded, loss_steps=[8, 16, 24, 32, 40],
        completions={name: spec(Path(t['output']) / 'COMPLETE.json') for name, t in trials.items()},
        restart_allocations=allocations,
        isolation=isolation(p), costs=costs, test_instruments_opened=0,
        cost_limitations='40-update smoke; startup/storage/requeue/epoch-final legacy CER overhead additional; Stage A rates are projections'))


def seeds(plan_path, out):
    """B2: fresh seed 0/1/2 runs of each width's best final dev point."""
    p = checked_plan(plan_path)
    grouped = collect(plan_path)
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    plans, selected = [], []
    for w in ADOPTED:
        rr = grouped[w]
        ok = [r for r in rr if r['status'] == 'ok']
        if not ok:
            raise ValueError('no feasible trial for width')
        best = min(ok, key=lambda r: r['val_error'])
        selected.append(best)
        original = read(bound(best['trial']))
        for seed in (0, 1, 2):
            t = json.loads(json.dumps(original))
            t['parameters']['seed'] = seed
            path = out / 'trials' / ('w%g-best-s%d.json' % (w, seed))
            immutable(path, t)
            plans.append(dict(config=spec(path), output=str(out / 'runs' / ('w%g-best-s%d' % (w, seed)))))
    b2 = dict(p, groups=[plans[i:i+4] for i in range(0, len(plans), 4)], parent_study=spec(plan_path),
              selected=selected, b2=True)
    immutable(out / 'PLAN.json', b2)
    return b2


def adoption(plan_path, out):
    p = checked_plan(plan_path)
    if not p.get('b2'):
        raise ValueError('B2 seed plan required')
    parent_path = bound(p['parent_study'])
    parent, reruns = collect(parent_path), collect(plan_path)
    from study.analyze_study import unit
    space = read(ROOT / 'study/lr_space.json')
    result = []
    for width in ADOPTED:
        selected = next(r for r in p['selected'] if r['width_mult'] == width)
        control = next(r for r in parent[width] if r['trial_id'] == 'control')
        rr = reruns[width]
        if len(rr) != 3 or {r['seed'] for r in rr} != {0, 1, 2} or any(r['status'] != 'ok' for r in rr):
            raise ValueError('three complete best-point seed reruns required')
        if control['status'] != 'ok':
            raise ValueError('complete S1 control required')
        values = [r['val_error'] for r in rr]
        spread = max(values) - min(values)
        gain = control['val_error'] - selected['val_error']
        edges = {name: unit(selected[name], spec_) for name, spec_ in space.items()
                 if unit(selected[name], spec_) <= .1 or unit(selected[name], spec_) >= .9}
        result.append(dict(width_mult=width, best_trial=selected['trial_id'],
            control_seed0=control['val_error'], best_study_seed0=selected['val_error'],
            seeds={str(r['seed']): r['val_error'] for r in rr}, seed_spread_max_minus_min=spread,
            best_seed_mean=statistics.mean(values), improvement_over_control=gain,
            adoption_rule_met=gain > spread, boundary_unit_positions=edges,
            selected_parameters=read(bound(selected['trial']))['parameters'],
            caveat='best-point seed spread only; incumbent and study variance unmeasured; short schedule does not validate full-length schedule'))
    atomic(out, dict(results=result, b2_plan=spec(plan_path), parent_plan=spec(parent_path),
        stage_c_launched=False, policy='rule diagnostics only; inspect infeasibility/boundaries/curves and focused Astra before Stage C'))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('plan', 'node', 'submit', 'collect', 'smoke-readout', 'seeds', 'adoption'))
    p.add_argument('--runtime')
    p.add_argument('--stage-a')
    p.add_argument('--out')
    p.add_argument('--smoke', action='store_true')
    p.add_argument('--plan')
    p.add_argument('--group', type=int)
    p.add_argument('--review')
    p.add_argument('--smoke-report')
    a = p.parse_args()
    if a.command == 'plan':
        build(a.runtime, a.stage_a, a.out, smoke=a.smoke)
    elif a.command == 'node':
        raise SystemExit(node(a.plan, a.group))
    elif a.command == 'submit':
        submit(a.plan, a.review, a.smoke_report)
    elif a.command == 'collect':
        collect(a.plan)
    elif a.command == 'smoke-readout':
        smoke_readout(a.plan, a.out)
    elif a.command == 'seeds':
        seeds(a.plan, a.out)
    else:
        adoption(a.plan, a.out)

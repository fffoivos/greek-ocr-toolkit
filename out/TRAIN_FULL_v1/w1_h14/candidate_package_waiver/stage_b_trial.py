"""One SHA-bound, dev-only trial using S1 updates and full-state continuation."""
import argparse
import copy
import fcntl
import os
from pathlib import Path
import shutil
import sys
import time

from common import atomic, bound, read, sha, spec

ROOT = Path(__file__).resolve().parent
DEV = ('seal04_dev', 'harvest_dev')


def pooled(instruments):
    """Micro-average CER: sum edits / sum reference units, literal NFD atoms."""
    scores = [instruments[n]['score']['cer']['nfd_atom'] for n in DEV]
    units = sum(s['reference_units'] for s in scores)
    if units <= 0:
        raise ValueError('empty dev reference denominator')
    edits = sum(s['edits'] for s in scores)
    return dict(edits=edits, reference_units=units, rate=edits / units,
                mode='nfd_atom', pooling='sum edits / sum reference units across both dev panels')


def execute(trial, output, *, fixture=False, installer=None):
    import run
    from loss_cadence import plan
    from loss_journal import records
    from verify import verify, data_package_matches
    if not fixture:
        verify()
    runtime_path = bound(trial['runtime'])
    rt = read(runtime_path)
    if bool(rt.get('mock')) != fixture or trial['fixture'] != fixture:
        raise ValueError('fixture/production mismatch')
    if trial['payload_sha256'] != sha(ROOT / 'PAYLOAD.json'):
        raise ValueError('trial payload changed')
    if not fixture and not data_package_matches(rt.get('package_sha256'), runtime_path):
        raise ValueError('foreign prepared data')
    trainer, runtime = (installer or run.install)(runtime_path, study=True)
    trainer._runtime()
    torch = trainer.torch
    if not fixture:
        from stage_a_probe import THREAD_KEYS
        if (str(torch.__version__) != '2.11.0+cu128' or torch.version.cuda != '12.8'
                or torch.backends.cudnn.version() != 91900
                or torch.cuda.get_device_name(0) != 'NVIDIA GH200 120GB'):
            raise ValueError('S1 CUDA runtime changed')
        if torch.cuda.device_count() != 1 or not os.environ.get('CUDA_VISIBLE_DEVICES'):
            raise ValueError('exactly one pinned GPU required')
        if len(os.sched_getaffinity(0)) < 24 or any(os.environ.get(k) != '1' for k in THREAD_KEYS):
            raise ValueError('24 CPUs/GPU and native thread limits required')
    opts = copy.deepcopy(read(ROOT / 'recipe.json')['parameters'])
    opts.update(trial['parameters'])
    opts.update(mix=str(runtime_path), val_mix=str(runtime_path),
        codec=str(ROOT / 'vendor/codec/v2.1.json'), out_dir=str(Path(output).resolve()))
    if fixture:
        opts.update(device='cpu', workers=0, pin_memory=False)
    argv = []
    for k, v in opts.items():
        if v is True:
            argv.append('--' + k.replace('_', '-'))
        elif v is not False and v is not None:
            argv.extend(['--' + k.replace('_', '-'), str(v)])
    args = trainer.parse_args(argv)
    args.full_smoke = trial['smoke']
    args.full_every = trial['total_updates']  # final dev CER only; never tests
    args.loss_plan = plan(trainer, runtime, trainer.full_pools, args.epochs, args.epoch_rows,
                          args.bs, trial['loss_every_drawn_lines'])
    if args.loss_plan['total_updates'] != trial['total_updates']:
        raise ValueError('actual sampler horizon changed')
    trainer.PATIENCE = args.epochs + 1
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    binding = dict(trial=trial, loss_plan=args.loss_plan, evaluation_steps=[trial['total_updates']])
    target = output / 'RUN_BINDING.json'
    if target.exists() and read(target) != binding:
        raise ValueError('run binding changed')
    atomic(target, binding)
    atomic(output / 'LOSS_CADENCE.json', args.loss_plan)
    status = trainer.train(args)
    if status:
        return status
    ck = torch.load(output / 'segment.pt', map_location='cpu', weights_only=False)
    if ck['global_step'] != trial['total_updates'] or ck['draw_position'] != args.epoch_rows:
        raise ValueError('incomplete trial horizon')
    events, torn = records(output / 'loss_eval.jsonl')
    if torn is not None or [v['step'] for v in events] != args.loss_plan['steps']:
        raise ValueError('missing/duplicate loss point')
    for event, point in zip(events, args.loss_plan['points']):
        result = read(bound(event['record']))
        if (result['drawn_lines'] != point['drawn_lines'] or set(result['instruments']) != set(DEV)
                or any(result['instruments'][n]['rows'] != len(trainer.full_pools[n]) for n in DEV)):
            raise ValueError('loss point draw/coverage mismatch')
    final_path = output / 'eval' / ('step-%09d.json' % trial['total_updates'])
    final = read(final_path)
    if set(final['instruments']) != set(DEV):
        raise ValueError('study opened a non-dev instrument')
    objective = pooled(final['instruments'])
    atomic(output / 'COMPLETE.json', dict(binding=binding, checkpoint=spec(output / 'segment.pt'),
        evaluations=[spec(final_path)], loss_journal=spec(output / 'loss_eval.jsonl'),
        loss_evaluations=[e['record'] for e in events], pooled_dev=objective,
        state_sha256=ck['state_sha256'], package_sha256=trial['payload_sha256'],
        mock=fixture, test_instruments_opened=0))
    return 0


def validate_complete(output, trial):
    c = read(Path(output) / 'COMPLETE.json')
    if c['binding']['trial'] != trial or c['test_instruments_opened'] != 0:
        raise ValueError('completed trial binding changed')
    for s in [c['checkpoint'], c['loss_journal'], *c['evaluations'], *c['loss_evaluations']]:
        bound(s)
    return c


def physical_host():
    """Kernel node identity, independent of job IDs and inherited shell values."""
    host = os.uname().nodename
    if not host or host != host.strip():
        raise ValueError('missing physical host identity')
    return host


def recover_allocations(output, job, restart, boundary):
    """Retain killed intents, witness their end before a NEW allocation starts.

    Slurm tears down old steps before a requeue/retry allocation. The node
    controller records its boundary before launching any new GPU lane. A
    same-allocation orphan is refused, never assigned a fabricated end time.
    """
    for path in Path(output).glob('ALLOCATION_*.json'):
        old = read(path)
        recovery = Path(output) / ('RECOVERED_' + path.name)
        if 'ended_unix' in old or recovery.exists():
            continue
        if (old['job_id'] == job and old['restart_count'] >= restart) or boundary < old['started_unix']:
            raise ValueError('unfinished same-allocation claim; reconcile before retry')
        if not old.get('physical_host'):
            raise ValueError('missing prior physical host identity; cannot recover')
        atomic(recovery, dict(prior=spec(path), ended_upper_bound_unix=boundary,
            prior_physical_host=old['physical_host'], next_physical_host=physical_host(),
            next_job_id=job, next_restart_count=restart,
            basis='new Slurm allocation; old steps torn down before controller starts new lanes'))


def lane(trial_path, output, *, fixture=False, installer=None):
    trial = read(trial_path)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'RUN.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        claim = output / 'CLAIM.json'
        if claim.exists() and read(claim) != trial:
            raise ValueError('trial claim changed')
        if not claim.exists():
            atomic(claim, trial)
        job, restart = os.environ['SLURM_JOB_ID'], os.environ.get('SLURM_RESTART_COUNT', '0')
        if not fixture and 'TF_B_ALLOCATION_BOUNDARY' not in os.environ:
            raise ValueError('trial must run through its node controller')
        recover_allocations(output, job, int(restart),
                            float(os.environ.get('TF_B_ALLOCATION_BOUNDARY', time.time())))
        if (output / 'COMPLETE.json').exists():
            validate_complete(output, trial)
            return 0
        attempt = output / ('ALLOCATION_%s_%s_%d.json' % (job, restart, time.time_ns()))
        started = time.time()
        info = dict(trial=spec(trial_path), job_id=job, restart_count=int(restart),
            physical_host=physical_host(), physical_host_source='os.uname().nodename',
            started_unix=started, fixture=fixture, cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),
            cpu_affinity=sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else [])
        if not fixture:
            # Attest before training so SIGKILL cannot discard GPU identity.
            import torch
            from stage_a_probe import gpu_uuid
            if torch.cuda.device_count() != 1 or not os.environ.get('CUDA_VISIBLE_DEVICES'):
                raise ValueError('exactly one pinned GPU required')
            torch.empty(1, device='cuda')
            info['gpu_uuid'] = gpu_uuid()
        atomic(attempt, info)
        forced = trial.get('force_requeue_step')
        if forced and not (output / 'FORCED_YIELD.json').exists():
            os.environ['S1_FORCE_SPLIT_STEP'] = str(forced)
        else:
            os.environ.pop('S1_FORCE_SPLIT_STEP', None)
        os.environ['S1_TRACE'] = '1' if trial['smoke'] else '0'
        try:
            status = execute(trial, output, fixture=fixture, installer=installer)
            if status == 75:
                path = output / 'yields' / ('%s-%s-%d.pt' % (job, restart, time.time_ns()))
                path.parent.mkdir(exist_ok=True)
                shutil.copyfile(output / 'segment.pt', path)
                yielded = dict(checkpoint=spec(path), job_id=job, restart_count=int(restart))
                atomic(output / ('YIELD_%d.json' % time.time_ns()), yielded)
                if forced and not (output / 'FORCED_YIELD.json').exists():
                    # A preemption before the requested point must not consume
                    # the deliberate requeue gate.
                    import torch
                    ck = torch.load(path, map_location='cpu', weights_only=False)
                    if ck['global_step'] == forced:
                        atomic(output / 'FORCED_YIELD.json', dict(**yielded, step=forced))
            info['exit_code'] = status
            return status
        except Exception as e:
            atomic(output / ('FAILURE_%d.json' % time.time_ns()),
                   dict(trial=trial, error_type=type(e).__name__, error=str(e)))
            info['exit_code'] = 1
            raise
        finally:
            info['ended_unix'] = time.time()
            if not fixture:
                from stage_a_probe import gpu_uuid
                try:
                    info['gpu_uuid'] = gpu_uuid()
                except Exception as e:
                    info['attestation_error'] = str(e)
            atomic(attempt, info)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--trial', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    raise SystemExit(lane(a.trial, a.out))

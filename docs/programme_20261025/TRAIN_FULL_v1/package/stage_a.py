"""Owner-run Stage A node driver, lane runner and offline readout.

Each lane is a separate srun step with one GPU/24 disjoint CPUs. Only complete
SHA-bound point results are reused after requeue. No training state is retained.
"""
import argparse
import fcntl
import os
from pathlib import Path
import subprocess
import sys

from common import atomic, bound, read, sha, spec
from stage_a_probe import binding

ROOT = Path(__file__).resolve().parent
BATCHES = (64, 128, 256, 512, 1024)
WIDTHS = (1., 1.5, 2.)


def point_name(width, workers, batch):
    return 'w%g-workers%d-b%d' % (width, workers, batch)


def lane(runtime, out, width, workers, *, runner=subprocess.run):
    out = Path(out)
    result = []
    lane_id = 'w%g-workers%d' % (width, workers)
    with (out / (lane_id + '.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for batch in BATCHES:
            name = point_name(width, workers, batch)
            target = out / (name + '.json')
            expected = binding(runtime, width, batch, workers, 30, 300)
            if target.exists():
                record = read(target)
                if record['binding'] != expected or record['status'] not in ('OK', 'OOM'):
                    raise ValueError('completed point binding changed: ' + name)
            else:
                # Every invocation keeps its logs/intent, including killed attempts.
                attempt = out / 'attempts' / (name + '-%s-%s' %
                    (os.environ['SLURM_JOB_ID'], os.environ.get('SLURM_RESTART_COUNT', '0')))
                attempt.mkdir(parents=True, exist_ok=False)
                atomic(attempt / 'INTENT.json', expected)
                with (attempt / 'probe.log').open('x') as log:
                    process = runner([sys.executable, '-B', str(ROOT / 'stage_a_probe.py'),
                        '--runtime', str(runtime), '--out', str(attempt / 'RESULT.json'),
                        '--width', str(width), '--batch', str(batch), '--workers', str(workers)],
                        stdout=log, stderr=subprocess.STDOUT)
                if process.returncode:
                    raise RuntimeError('probe failed (not an OOM result); inspect ' + str(attempt))
                record = read(attempt / 'RESULT.json')
                if record['binding'] != expected or record['status'] not in ('OK', 'OOM'):
                    raise ValueError('point worker returned wrong identity/status')
                atomic(target, record)
            result.append(record)
            if record['status'] == 'OOM':
                break
    return result


def choose(points, gain=.05):
    """Largest measured batch clearing 5% over the last accepted throughput."""
    selected, decisions = None, []
    for p in sorted(points, key=lambda p: p['binding']['batch']):
        if p['status'] == 'OOM':
            break
        rate = p['lines_per_second']
        accepted = selected is None or rate >= selected['lines_per_second'] * (1 + gain)
        decisions.append(dict(batch=p['binding']['batch'], lines_per_second=rate, accepted=accepted))
        if accepted:
            selected = p
    if selected is None:
        raise ValueError('batch64 has no feasible measurement')
    return selected, decisions


def needs_workers(points):
    return any(p['status'] == 'OK' and p['loader_stall_share'] >= .10 for p in points)


def check_isolation(points):
    active = [p for p in points if p['status'] == 'OK']
    for i, a in enumerate(active):
        if not a['cuda_visible_devices'] or not a['gpu_uuid'] or len(a['cpu_affinity']) < 24:
            raise ValueError('missing per-lane GPU/CPU attestation')
        for b in active[i+1:]:
            if max(a['started_unix'], b['started_unix']) < min(a['ended_unix'], b['ended_unix']):
                if a['gpu_uuid'] == b['gpu_uuid'] or set(a['cpu_affinity']) & set(b['cpu_affinity']):
                    raise ValueError('overlapping GPU/CPU assignments')
    return dict(status='PASS', scope='GPU UUID + CPU affinity overlap; shared node/storage contention remains measured')


def summarize(out):
    out = Path(out)
    run = read(out / 'STUDY_BINDING.json')
    for s in (run['runtime'], run['payload']):
        bound(s)
    points = [read(p) for p in sorted(out.glob('w*-workers*-b*.json'))]
    if not points or any(p['binding']['payload_sha256'] != run['payload']['sha256']
                         or p['binding']['runtime'] != run['runtime'] for p in points):
        raise ValueError('foreign/missing measurement')
    selections = []
    for width in WIDTHS:
        candidates = []
        baseline = [p for p in points if p['binding']['width_mult'] == width and p['binding']['workers'] == 6]
        require12 = width == 1. or needs_workers(baseline)
        for workers in ((6, 12) if require12 else (6,)):
            pp = [p for p in points if p['binding']['width_mult'] == width and p['binding']['workers'] == workers]
            pp.sort(key=lambda p: p['binding']['batch'])
            batches = [p['binding']['batch'] for p in pp]
            if (not batches or tuple(batches) != BATCHES[:len(batches)]
                    or (len(batches) < 5 and pp[-1]['status'] != 'OOM')
                    or any(p['status'] != 'OK' for p in pp[:-1])):
                raise ValueError('incomplete width/worker sweep')
            best, decisions = choose(pp)
            candidates.append((best, decisions))
        best, decisions = candidates[0]
        if len(candidates) > 1 and candidates[1][0]['lines_per_second'] >= best['lines_per_second'] * 1.05:
            best, decisions = candidates[1]
        b, rate = best['binding']['batch'], best['lines_per_second']
        train_draws = 16 * read(bound(run['runtime']))['train_rows']
        trial_draws = (train_draws + 9) // 10
        selections.append(dict(width_mult=width, batch=b, workers=best['binding']['workers'],
            lines_per_second=rate, batch_decisions=decisions,
            worker_comparisons=[dict(workers=p['binding']['workers'], batch=p['binding']['batch'],
                                    lines_per_second=p['lines_per_second']) for p, _ in candidates],
            full_updates=8 * ((train_draws // 8 + b - 1) // b),
            study_updates=(trial_draws + b - 1) // b, study_target_draws=trial_draws,
            study17_training_GPU_hours=17 * trial_draws / rate / 3600,
            seed3_training_GPU_hours=3 * trial_draws / rate / 3600,
            full_training_GPU_hours=train_draws / rate / 3600,
            best_point=point_name(width, best['binding']['workers'], b)))
    report = dict(schema='TRAIN_FULL-stage-A-v1', status='MEASURED', binding=run,
        selections=selections, points=points, isolation=check_isolation(points),
        rule='5% lines/s gain over last accepted smaller batch; 12 workers only adopted for >=5% gain',
        cost_scope='training only: add measured dev loss/CER, startup, requeue and scheduler reservation overhead before Stage B launch',
        checkpoints_kept=0, eval_instruments_opened=0)
    atomic(out / 'STAGE_A.json', report)
    for r in selections:
        print('x%g | batch %d | workers %d | %.1f lines/s | B17 %.2f GPU-h | C %.2f GPU-h (training only)' %
            (r['width_mult'], r['batch'], r['workers'], r['lines_per_second'],
             r['study17_training_GPU_hours'], r['full_training_GPU_hours']))
    return report


def node(runtime, out):
    from verify import verify, data_package_matches
    verify()
    if not data_package_matches(read(runtime).get('package_sha256'), runtime):
        raise ValueError('foreign prepared data')
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'NODE.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        identity = dict(runtime=spec(runtime), payload=spec(ROOT / 'PAYLOAD.json'),
                        widths=WIDTHS, batches=BATCHES, warmup=30, timed_updates=300,
                        workers=[6, 12], gpu_lanes=4, cpus_per_lane=24)
        # JSON round-trip normalizes tuple/list values before identity comparison.
        import json
        identity = json.loads(json.dumps(identity))
        path = out / 'STUDY_BINDING.json'
        if path.exists() and read(path) != identity:
            raise ValueError('Stage A run identity changed')
        if not path.exists():
            atomic(path, identity)

        def wave(lanes):
            processes = []
            try:
                for width, workers in lanes:
                    cmd = ['srun', '--exclusive', '--exact', '--nodes=1', '--ntasks=1',
                        '--gpus-per-node=1', '--gpus-per-task=1', '--cpus-per-task=24', '--cpu-bind=cores', '--gpu-bind=single:1',
                        sys.executable, '-B', str(ROOT / 'stage_a.py'), 'lane', '--runtime', str(runtime),
                        '--out', str(out), '--width', str(width), '--workers', str(workers)]
                    processes.append(subprocess.Popen(cmd))
                codes = [p.wait() for p in processes]
                if any(codes):
                    raise RuntimeError('Stage A lane failed: ' + str(codes))
            finally:
                for p in processes:
                    if p.poll() is None:
                        p.terminate()
                        p.wait()
        wave([(1., 6), (1.5, 6), (2., 6), (1., 12)])
        extra = []
        for width in (1.5, 2.):
            pp = [read(p) for p in out.glob('w%g-workers6-b*.json' % width)]
            if needs_workers(pp):
                extra.append((width, 12))
        if extra:
            wave(extra)
        return summarize(out)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('node', 'lane', 'readout'))
    p.add_argument('--runtime')
    p.add_argument('--out', required=True)
    p.add_argument('--width', type=float, choices=WIDTHS)
    p.add_argument('--workers', type=int, choices=(6, 12))
    a = p.parse_args()
    if a.command == 'readout':
        summarize(a.out)
    elif a.command == 'node':
        node(a.runtime, a.out)
    else:
        lane(a.runtime, a.out, a.width, a.workers)

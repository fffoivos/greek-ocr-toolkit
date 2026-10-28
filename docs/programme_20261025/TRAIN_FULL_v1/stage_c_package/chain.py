"""OWNER ONLY scheduler driver. Never invoked by offline preparation/tests.

No SSH. Operates from the owner's Clariden shell. Completed predecessor IDs are
authenticated by sacct then omitted from dependencies, including purged IDs.
"""
import argparse
import os
from pathlib import Path
import subprocess

from common import atomic, read, sha, spec

ROOT = Path(__file__).resolve().parent


def dependency(job, sacct_text):
    records = [line.split('|') for line in sacct_text.strip().splitlines() if line.strip()]
    parent = [r for r in records if r[0] == str(job)]
    if len(parent) != 1 or len(parent[0]) != 4:
        raise ValueError('missing/ambiguous sacct parent proof')
    _, state, exit_code, elapsed = parent[0]
    if not elapsed.isdecimal():
        raise ValueError('missing elapsed accounting')
    if state == 'COMPLETED' and exit_code == '0:0':
        return None
    if state in ('PENDING', 'RUNNING', 'REQUEUED', 'REQUEUE_FED'):
        return 'afterok:' + str(job)
    raise ValueError('predecessor failed/unknown: ' + state + '/' + exit_code)


def submit(args, command=subprocess.run):
    from verify import verify
    verify()
    output = Path(args.out).resolve()
    controls = Path(args.controls).resolve()
    controls.mkdir(parents=True, exist_ok=True)
    claim = controls / ('submit-%03d.json' % args.segment)
    intent = controls / ('intent-%03d.json' % args.segment)
    if claim.exists() or intent.exists():
        raise ValueError('existing submission/intent; inspect accounting, never resubmit blindly')
    if (output / 'COMPLETE.json').exists():
        raise ValueError('run is already complete; no continuation allocation needed')
    if args.mode == 'train':
        from verify import package_matches
        # These are concrete signed-off evidence files supplied by the coordinator.
        review = read(args.review)
        if review.get('verdict') != 'PASS' or review.get('package_sha256') != sha(ROOT / 'PAYLOAD.json'):
            raise ValueError('Astra package/tests/smoke review missing or for another package')
        from common import bound
        bound(review['smoke_identity'])
        identity = read(review['smoke_identity']['path'])
        if identity['status'] != 'BIT_IDENTICAL' or identity.get('mock') is not False:
            raise ValueError('smoke identity missing')
        if (review.get('runtime_sha256') != sha(args.runtime)
                or identity.get('runtime_sha256') != sha(args.runtime)
                or not package_matches(identity.get('package_sha256'))):
            raise ValueError('review/smoke applies to another data population or package')
        if not args.owner_go:
            raise ValueError('owner launch go required')
    dep = None
    if args.prior:
        proof = command(['sacct', '-X', '-n', '-P', '-j', str(args.prior),
            '--format=JobIDRaw,State,ExitCode,ElapsedRaw'], check=True, capture_output=True, text=True).stdout
        dep = dependency(args.prior, proof)
        atomic(controls / ('prior-%03d.json' % args.segment), dict(job_id=args.prior, sacct=proof, dependency=dep))
        if dep is None:
            prior_output = read(output / 'SEGMENT_YIELD.json') if not (output / 'COMPLETE.json').exists() else None
            if prior_output and prior_output['job_id'] != str(args.prior):
                raise ValueError('yield is not from the authenticated predecessor')
            if prior_output:
                from common import bound
                bound(prior_output['checkpoint'])
    duration = '01:20:00' if args.mode.startswith('smoke') else '12:00:00'
    env = {**os.environ, 'TF_PACKAGE': str(ROOT), 'TF_RUNTIME': str(Path(args.runtime).resolve()),
           'TF_OUTPUT': str(output), 'TF_MODE': args.mode}
    argv = ['sbatch', '--parsable', '--time=' + duration,
            '--output=' + str(controls / ('slurm-%03d-%%j.log' % args.segment))]
    if dep:
        argv.append('--dependency=' + dep)
    argv.append(str(ROOT / 'job.sbatch'))
    # Exact same options on dry check and actual submit.
    command([*argv[:-1], '--test-only', argv[-1]], env=env, check=True, capture_output=True, text=True)
    binding = dict(argv=argv, runtime=spec(args.runtime), package=spec(ROOT / 'PAYLOAD.json'),
                   mode=args.mode, owner_go=bool(args.owner_go), prior=args.prior)
    import json
    with intent.open('x') as stream:
        json.dump(binding, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    result = command(argv, env=env, check=True, capture_output=True, text=True)
    job = result.stdout.strip().split(';')[0]
    if not job.isdecimal():
        raise ValueError('ambiguous sbatch response; retain intent and inspect sacct')
    atomic(claim, dict(**binding, job_id=job, response=result.stdout))
    return job


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--runtime', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--controls', required=True)
    p.add_argument('--segment', type=int, default=1)
    p.add_argument('--prior')
    p.add_argument('--mode', choices=('train', 'smoke-control', 'smoke-requeue'), required=True)
    p.add_argument('--review')
    p.add_argument('--owner-go', action='store_true')
    a = p.parse_args()
    if a.mode == 'train' and not a.review:
        p.error('--review is required for production')
    print(submit(a))

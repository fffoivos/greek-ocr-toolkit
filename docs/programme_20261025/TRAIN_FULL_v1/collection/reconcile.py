#!/usr/bin/env python3
"""Owner-run Slurm evidence adapter; the sealed Stage B payload stays unchanged.

Only recovery upper bounds receive an in-memory overlay, and only after unique
parent/restart/host/step matching. Original files and scientific result logic are
never rewritten. No fixture=True path exists here.
"""
import argparse
from contextlib import contextmanager
import hashlib
import importlib
import itertools
import json
import math
from pathlib import Path
import re
import subprocess
import sys

PAYLOAD_SHA = '3c9e5d5f4fb8702e394b340fe1cc2e02e3b4247556b4fd93c0ed2d1acc2cf4e8'
STUDY_SHA = '01cc2ae0bb09d2b61d3b6a7fc15627366d3a131e385efe30028e82cb81903f38'
SACCT_FIELDS = ['JobIDRaw', 'JobID', 'State', 'ExitCode', 'Start', 'End',
                'ElapsedRaw', 'NodeList', 'Restarts', 'ReqTRES', 'AllocTRES']
TERMINAL = {'COMPLETED', 'CANCELLED', 'FAILED', 'NODE_FAIL', 'PREEMPTED',
            'TIMEOUT', 'OUT_OF_MEMORY', 'BOOT_FAIL', 'DEADLINE', 'REVOKED',
            'REQUEUED'}  # closed historical allocation in sacct -D, not a live end


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def file_spec(path, original=None):
    path = Path(path)
    return dict(path=str(original or path.resolve()), sha256=sha(path), bytes=path.stat().st_size)


def check_spec(path, expected):
    if file_spec(path, expected['path']) != expected:
        raise ValueError('evidence SHA/bytes/path mismatch: ' + str(path))


def load_package(package):
    package = Path(package).resolve()
    if sha(package / 'PAYLOAD.json') != PAYLOAD_SHA:
        raise ValueError('unrecognized sealed Stage B payload')
    # CLI starts in a fresh process; do not silently reuse another package import.
    for name in ('common', 'verify', 'stage_b', 'stage_b_trial'):
        module = sys.modules.get(name)
        if module is not None and Path(module.__file__).resolve().parent != package:
            raise ValueError('foreign imported package module: ' + name)
    sys.path.insert(0, str(package))
    b = importlib.import_module('stage_b')
    importlib.import_module('verify').verify()
    return b


def authenticate(b, plan_path, expected_plan_sha, evidence=None):
    plan_path = Path(plan_path).resolve()
    if sha(plan_path) != expected_plan_sha:
        raise ValueError('plan SHA mismatch')
    p = read(plan_path)
    if (p.get('fixture') is not False or p.get('smoke') is not False
            or p['payload_sha256'] != PAYLOAD_SHA):
        raise ValueError('foreign/fixture/smoke plan')
    if evidence is None:
        return b.checked_plan(plan_path)  # full live input/trial authentication
    # Offline copies preserve original remote paths in all specs. Only the
    # copied trials/points/space/payload are available; no data custody claim.
    if expected_plan_sha != STUDY_SHA:
        raise ValueError('offline mode is restricted to the copied Stage B study')
    for key, name in [('points', 'lr_trials.jsonl'), ('space', 'lr_space.json')]:
        check_spec(b.ROOT / 'study' / name, p[key])
    trials = Path(plan_path).parent / 'trials'
    for group in p['groups']:
        for t in group:
            check_spec(trials / Path(t['config']['path']).name, t['config'])
    return p


def accounting(path, expected_sha):
    if sha(path) != expected_sha:
        raise ValueError('sacct capture SHA mismatch')
    records = []
    for number, line in enumerate(Path(path).read_text().splitlines(), 1):
        fields = line.split('|')
        if len(fields) != len(SACCT_FIELDS):
            raise ValueError('sacct schema mismatch on line %d' % number)
        r = dict(zip(SACCT_FIELDS, fields))
        for key in ('Start', 'End', 'ElapsedRaw'):
            if not re.fullmatch(r'[0-9]+', r[key]):
                raise ValueError('sacct requires epoch seconds: line %d %s' % (number, key))
            r[key] = int(r[key])
        if r['Start'] <= 0 or r['End'] < r['Start'] or r['ElapsedRaw'] != r['End'] - r['Start']:
            raise ValueError('invalid sacct interval: line %d' % number)
        if r['State'].split()[0] not in TERMINAL:
            raise ValueError('nonterminal accounting: line %d' % number)
        r['capture_line'] = number
        records.append(r)
    if not records:
        raise ValueError('empty sacct capture')
    return records


def measured_step(a, records):
    """No nearest timestamp, restart ordinal inference, or guessed duration.

    Restarts is provided on the parent job, not on step rows. Join via the
    parent with that exact restart/host and its start interval. Python starts
    inside its srun step, rather than at the integer-second step start. Require
    a UNIQUE containing numeric single-GPU step within that parent allocation.
    Record the start offset; there is no fuzzy/nearest-match fallback.
    """
    parents = [r for r in records if r['JobIDRaw'] == a['job_id']
               and r['Restarts'] == str(a['restart_count'])
               and r['NodeList'] == a['physical_host']
               and r['Start'] <= a['started_unix'] <= r['End']]
    if len(parents) != 1:
        raise ValueError('parent job/restart/host match is not unique (%d)' % len(parents))
    parent = parents[0]
    steps = [r for r in records
             if re.fullmatch(re.escape(a['job_id']) + r'\.[0-9]+', r['JobIDRaw'])
             and r['NodeList'] == a['physical_host']
             and parent['Start'] <= r['Start'] <= a['started_unix'] <= r['End']
             and r['Start'] <= parent['End']]
    if len(steps) != 1:
        raise ValueError('lane step/start match is not unique (%d)' % len(steps))
    step = steps[0]
    tres = dict(part.split('=', 1) for part in step['AllocTRES'].split(',') if '=' in part)
    if tres.get('gres/gpu') != '1' or tres.get('cpu') != '24':
        raise ValueError('matched step is not a 24-CPU/single-GPU lane')
    return dict(parent=parent, step=step,
                allocation_start_minus_step_start_seconds=a['started_unix'] - step['Start'])


def conflicts(active):
    result = []
    for a, b in itertools.combinations(active, 2):
        start = max(a['record']['started_unix'], b['record']['started_unix'])
        end = min(a['record']['ended_unix'], b['record']['ended_unix'])
        if start >= end:
            continue
        aa, bb = a['record'], b['record']
        kinds = []
        if aa['gpu_uuid'] == bb['gpu_uuid']:
            kinds.append('GPU_GLOBAL')
        cpus = sorted(set(aa['cpu_affinity']) & set(bb['cpu_affinity']))
        if aa['physical_host'] == bb['physical_host'] and cpus:
            kinds.append('CPU_SAME_HOST')
        if kinds:
            result.append(dict(kinds=kinds, left=a['allocation'], right=b['allocation'],
                left_host=aa['physical_host'], right_host=bb['physical_host'],
                left_gpu=aa['gpu_uuid'], right_gpu=bb['gpu_uuid'],
                shared_cpus=cpus if aa['physical_host'] == bb['physical_host'] else [],
                overlap_start_unix=start, overlap_end_unix=end, overlap_seconds=end-start))
    return result


def count_conflicts(pairs):
    return dict(pairs=len(pairs), gpu=sum('GPU_GLOBAL' in p['kinds'] for p in pairs),
                same_host_cpu=sum('CPU_SAME_HOST' in p['kinds'] for p in pairs))


def reconcile(b, p, plan_path, sacct, expected_sacct_sha, *, evidence=None):
    records = accounting(sacct, expected_sacct_sha)
    active, original, matches, inventory, overlay, used_steps = [], [], [], [], {}, set()
    for group in p['groups']:
        for t in group:
            remote = Path(t['output'])
            folder = Path(evidence) / 'allocations' / remote.name if evidence else remote
            paths = sorted(folder.glob('ALLOCATION_*.json'))
            if not paths:
                raise ValueError('missing lane attestations: ' + str(folder))
            for path in paths:
                a = read(path)
                remote_path = remote / path.name
                sp = file_spec(path, remote_path)
                inventory.append(sp)
                if (a.get('fixture') is not False or a.get('trial') != t['config']
                        or not a.get('physical_host') or not a.get('gpu_uuid')
                        or not a.get('cuda_visible_devices') or len(a.get('cpu_affinity', [])) < 24
                        or not math.isfinite(a['started_unix'])):
                    raise ValueError('invalid allocation identity/attestation: ' + str(path))
                end = a.get('ended_unix')
                if end is None:
                    recovery = path.with_name('RECOVERED_' + path.name)
                    w = read(recovery)
                    if (w['prior'] != sp or w.get('prior_physical_host') != a['physical_host']
                            or not w.get('next_physical_host')):
                        raise ValueError('recovery binding/host mismatch: ' + str(recovery))
                    if (w['next_job_id'] == a['job_id'] and w['next_restart_count'] <= a['restart_count']):
                        raise ValueError('recovery is not a later allocation: ' + str(recovery))
                    upper = w['ended_upper_bound_unix']
                    if not math.isfinite(upper) or upper < a['started_unix']:
                        raise ValueError('invalid recovery upper bound: ' + str(recovery))
                    try:
                        match = measured_step(a, records)
                    except ValueError as error:
                        raise ValueError(str(path) + ': ' + str(error)) from error
                    step_line = match['step']['capture_line']
                    if step_line in used_steps:
                        raise ValueError('two recovered allocations claim the same Slurm step')
                    used_steps.add(step_line)
                    end = min(upper, match['step']['End'])
                    rsp = file_spec(recovery, remote / recovery.name)
                    inventory.append(rsp)
                    matches.append(dict(allocation=sp, recovery=rsp,
                        original_upper_bound_unix=upper, measured_step_end_unix=match['step']['End'],
                        effective_end_unix=end, **match))
                    # The original checker will still validate prior SHA and
                    # both physical hosts. Overlay just its end-bound field.
                    overlay[str(recovery.resolve())] = dict(w, ended_upper_bound_unix=end)
                    original.append(dict(allocation=sp, record=dict(a, ended_unix=upper)))
                else:
                    original.append(dict(allocation=sp, record=a))
                if not math.isfinite(end) or end < a['started_unix']:
                    raise ValueError('invalid effective allocation interval: ' + str(path))
                active.append(dict(allocation=sp, record=dict(a, ended_unix=end)))
    before, after = conflicts(original), conflicts(active)
    report = dict(schema='TRAIN_FULL-stage-B-sacct-reconciliation-v1',
        status='PASS' if not after else 'FAIL',
        mode='offline copied evidence' if evidence else 'live authenticated plan and inputs',
        payload=file_spec(b.ROOT / 'PAYLOAD.json'), plan=file_spec(plan_path),
        tool=file_spec(__file__), sacct=file_spec(sacct), sacct_fields=SACCT_FIELDS,
        allocations=len(active), recovered_allocations=len(matches), inventory=inventory,
        matches=matches, before=count_conflicts(before), after=count_conflicts(after),
        before_conflicts=before, remaining_conflicts=after,
        policy='unique parent job+restart+host and containing numeric single-GPU step; effective end=min(original upper bound, measured step End); no nearest-time or synthetic end',
        limitations='sacct seconds resolution; original allocation start/end clocks retained; copied-data audit does not validate remote completion/checkpoint/result bytes')
    if not after:
        # Execute the original sealed checker as well; it retains global GPU
        # and same-physical-host CPU checks, including endpoint handling.
        check_plan = p
        if evidence:
            check_plan = dict(p, groups=[[dict(t, output=str(Path(evidence) / 'allocations' / Path(t['output']).name))
                                         for t in group] for group in p['groups']])
            # Original recovery specs name remote paths. For the offline
            # checker only, spec() returns that original path after rehashing.
        original_read, original_spec = b.read, b.spec
        def overlay_read(path):
            return overlay.get(str(Path(path).resolve()), None) or original_read(path)
        def offline_spec(path):
            actual = original_spec(path)
            remote_spec = next((s for s in inventory if Path(s['path']).name == Path(path).name
                                and Path(s['path']).parent.name == Path(path).parent.name), None)
            if remote_spec is None or (actual['sha256'], actual['bytes']) != (remote_spec['sha256'], remote_spec['bytes']):
                raise ValueError('offline original spec mismatch')
            return remote_spec
        try:
            b.read = overlay_read
            if evidence:
                b.spec = offline_spec
            # Access saved original even while a collection adapter is active.
            checker = getattr(b, '_sacct_original_isolation', b.isolation)
            report['sealed_checker'] = checker(check_plan)
        finally:
            b.read, b.spec = original_read, original_spec
    return report


@contextmanager
def collection_adapter(b, reports, expected_sacct_sha, sacct, report_path):
    """All sealed collect calls, including internal seeds/adoption calls, pass here."""
    original = b.isolation
    b._sacct_original_isolation = original
    def isolation(plan):
        # Only explicitly authenticated plans may use reconciled evidence.
        matching = [(path, p) for path, p in reports.items() if p == plan]
        if len(matching) != 1:
            raise ValueError('collector requested an unauthenticated plan')
        path, _ = matching[0]
        report = reconcile(b, plan, path, sacct, expected_sacct_sha)
        target = Path(report_path)
        if len(reports) > 1:
            target = target.with_name(target.stem + '-' + sha(path)[:16] + target.suffix)
        b.atomic(target, report)
        if report['status'] != 'PASS':
            raise ValueError('remaining allocation overlap: ' + json.dumps(report['remaining_conflicts'], sort_keys=True))
        return dict(report['sealed_checker'], reconciliation=b.spec(target))
    b.isolation = isolation
    try:
        yield
    finally:
        b.isolation = original
        del b._sacct_original_isolation


def submit_b2(b, plan_path, review, smoke, *, command=subprocess.run):
    """Retain sealed submit gates/claims plus the exact effective time override."""
    p = b.checked_plan(plan_path)
    trials = [read(b.bound(t['config'])) for group in p['groups'] for t in group]
    if (not p.get('b2') or len(trials) != 9 or len(p['groups']) != 3
            or {(t['parameters']['width_mult'], t['parameters']['seed']) for t in trials}
               != set(itertools.product((1., 1.5, 2.), (0, 1, 2)))):
        raise ValueError('nine-run B2 plan required')
    controls = Path(plan_path).parent / 'submit-controls'
    for i in range(len(p['groups'])):
        receipt = controls / ('group-%03d.json' % i)
        if receipt.exists():
            r = read(receipt)
            effective = read(controls / 'time-override' / ('group-%03d.json' % i))
            if (effective['sealed_command'] != r['command'] or effective['job_id'] != r['job_id']
                    or effective['plan'] != b.spec(plan_path)
                    or effective['effective_command'] != [r['command'][0], '--time=08:00:00', *r['command'][1:]]):
                raise ValueError('effective time-override receipt differs')
    def override(cmd, **kwargs):
        if cmd[0] != 'sbatch' or any(c.startswith('--time') for c in cmd):
            raise ValueError('unexpected submission command/time option')
        actual = [cmd[0], '--time=08:00:00', *cmd[1:]]
        if '--test-only' in cmd:
            return command(actual, **kwargs)
        group = int(cmd[-1])
        base = Path(plan_path).parent / 'submit-controls' / 'time-override'
        intent = base / ('group-%03d.INTENT.json' % group)
        receipt = base / ('group-%03d.json' % group)
        if intent.exists() or receipt.exists():
            raise ValueError('existing effective submission claim; reconcile before retry')
        binding = dict(sealed_command=cmd, effective_command=actual, time='08:00:00',
            plan=b.spec(plan_path), review=b.spec(review), smoke=b.spec(smoke), tool=b.spec(__file__))
        b.atomic(intent, binding)
        result = command(actual, **kwargs)
        job = result.stdout.strip().split(';')[0]
        if not job.isdigit():
            raise ValueError('unparseable job id; retain both intents and reconcile')
        b.atomic(receipt, dict(binding, job_id=job))
        return result
    b.submit(plan_path, review, smoke, command=override)
    # Reruns skip submitted groups through the original sealed receipts. Prove
    # each skipped group also has matching durable effective-command evidence.
    for i in range(len(p['groups'])):
        controls = Path(plan_path).parent / 'submit-controls'
        r = read(controls / ('group-%03d.json' % i))
        effective = read(controls / 'time-override' / ('group-%03d.json' % i))
        if (effective['sealed_command'] != r['command'] or effective['job_id'] != r['job_id']
                or effective['plan'] != b.spec(plan_path)
                or effective['effective_command'] != [r['command'][0], '--time=08:00:00', *r['command'][1:]]):
            raise ValueError('effective time-override receipt differs')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('audit', 'collect', 'seeds', 'adoption', 'submit-b2'))
    parser.add_argument('--package', required=True)
    parser.add_argument('--plan', required=True)
    parser.add_argument('--plan-sha', default=STUDY_SHA)
    parser.add_argument('--sacct')
    parser.add_argument('--sacct-sha')
    parser.add_argument('--report')
    parser.add_argument('--evidence', help='offline copied allocation directory; audit only')
    parser.add_argument('--out')
    parser.add_argument('--review')
    parser.add_argument('--smoke-report')
    args = parser.parse_args()
    if args.evidence and args.command != 'audit':
        parser.error('copied evidence is audit-only, never collection/selection/submission')
    b = load_package(args.package)
    p = authenticate(b, args.plan, args.plan_sha, args.evidence)
    if args.command == 'submit-b2':
        if not args.review or not args.smoke_report:
            parser.error('submit-b2 needs review and smoke-report')
        submit_b2(b, args.plan, args.review, args.smoke_report)
        return
    if not args.sacct or not args.sacct_sha or not args.report:
        parser.error('accounting path, independently checked SHA, and report are required')
    if args.command == 'audit':
        report = reconcile(b, p, args.plan, args.sacct, args.sacct_sha, evidence=args.evidence)
        b.atomic(args.report, report)
        print(json.dumps({k: report[k] for k in ('status', 'allocations', 'recovered_allocations', 'before', 'after')}, sort_keys=True))
        if report['status'] != 'PASS':
            raise ValueError('remaining allocation overlap: ' + json.dumps(report['remaining_conflicts'], sort_keys=True))
        return
    plans = {str(Path(args.plan).resolve()): p}
    if args.command == 'adoption':
        parent = b.bound(p['parent_study'])
        plans[str(parent.resolve())] = authenticate(b, parent, STUDY_SHA)
    with collection_adapter(b, plans, args.sacct_sha, args.sacct, args.report):
        if args.command == 'collect':
            b.collect(args.plan)  # production default, with original result validation
        elif args.command == 'seeds':
            if not args.out:
                parser.error('seeds requires out')
            b.seeds(args.plan, args.out)  # original seeds() internally calls collect()
        else:
            if not args.out:
                parser.error('adoption requires out')
            b.adoption(args.plan, args.out)


if __name__ == '__main__':
    main()

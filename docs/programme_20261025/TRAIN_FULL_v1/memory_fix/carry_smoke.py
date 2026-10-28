"""Carry actual C smoke evidence across ONLY the explicit 110G Slurm request.

Coordinator-run, outside the sealed payload. Never writes the old package/attempt,
changes a PLAN, submits a job, or fabricates CUDA measurements. The old sealed
readout revalidates the completed six-job smoke into a fresh evidence directory.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

OLD_SHA = '8b228d6e138151f498b7f8ea948c516ecac0fdae65a5602000ca27d530585d4c'
NEW_SHA = '515b7d86f5f5758be544e401ae06720e67db8b311e38ef6bcff22c649db5bf8d'
MEMORY_BYTES = 110 * 1024**3


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def spec(path):
    path = Path(path).resolve()
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))


def bound(item):
    path = Path(item['path'])
    if spec(path) != item:
        raise ValueError('evidence binding mismatch: ' + str(path))
    return path


def seal(root, expected):
    root = Path(root).resolve()
    if sha(root/'PAYLOAD.json') != expected:
        raise ValueError('unrecognized payload')
    payload = read(root/'PAYLOAD.json')
    for name, item in payload['files'].items():
        path = root/name
        if not path.resolve().is_relative_to(root):
            raise ValueError('escaping payload path')
        if path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
            raise ValueError('payload mismatch: ' + name)
    return payload


def delta(old, new):
    before, after = seal(old, OLD_SHA), seal(new, NEW_SHA)
    if before.keys() != after.keys() or any(before[k] != after[k] for k in before if k != 'files'):
        raise ValueError('payload metadata changed')
    names = set(before['files']) | set(after['files'])
    changed = sorted(n for n in names if before['files'].get(n) != after['files'].get(n))
    if changed != ['stage_c.sbatch']:
        raise ValueError('change exceeds memory-only request: ' + repr(changed))
    text = (Path(old)/'stage_c.sbatch').read_bytes()
    anchor = b'#SBATCH --cpus-per-task=24\n'
    if text.count(anchor) != 1 or (Path(new)/'stage_c.sbatch').read_bytes() != text.replace(
            anchor, anchor + b'#SBATCH --mem=110G\n'):
        raise ValueError('shell diff exceeds exact 110G directive')
    return dict(old_payload=spec(Path(old)/'PAYLOAD.json'), new_payload=spec(Path(new)/'PAYLOAD.json'),
                changed=changed, diff='+#SBATCH --mem=110G', numerical_files='ALL byte-identical')


def rss_bytes(value):
    match = re.fullmatch(r'(\d+(?:\.\d+)?)([KMGTPE]?)(?:[iI]?[bB])?', value.strip(), re.I)
    if not match:
        raise ValueError('unmeasured MaxRSS: ' + repr(value))
    return float(match[1]) * 1024**('KMGTPE'.index(match[2].upper())+1 if match[2] else 0)


def memory_report(plan, capture, expected_sha):
    if sha(capture) != expected_sha:
        raise ValueError('RSS capture SHA mismatch')
    rows = []
    # sacct -D -n -P: JobIDRaw,JobID,State,NodeList,MaxRSS,MaxRSSTask,
    # MaxRSSNode,ReqMem,AllocTRES,NTasks. Kept separate from 11-field isolation.
    for number, line in enumerate(Path(capture).read_text().splitlines(), 1):
        fields = [f.strip() for f in line.split('|')]
        if len(fields) != 10:
            raise ValueError('RSS capture schema mismatch')
        if fields[2].split()[0] not in {'COMPLETED', 'CANCELLED', 'FAILED', 'NODE_FAIL',
                'PREEMPTED', 'TIMEOUT', 'REQUEUED', 'OUT_OF_MEMORY'}:
            raise ValueError('RSS capture contains nonterminal allocation')
        rows.append((number, fields))
    costs = []
    for entry in plan['runs']:
        config = read(bound(entry['config']))
        if config['parameters']['workers'] != 6:
            raise ValueError('six-worker profile changed')
        allocations = [read(f) for f in Path(entry['output']).glob('ALLOCATION_*.json')]
        ids = {a['job_id']+'.'+a['step_id'] for a in allocations}
        measured = [(n, fields, rss_bytes(fields[4])) for n, fields in rows
                    if fields[0] in ids and fields[4] and fields[9] == '1']
        if not measured:
            raise ValueError('no measured single-task lane MaxRSS for '+entry['name'])
        n, fields, peak = max(measured, key=lambda x: x[2])
        if peak >= MEMORY_BYTES:
            raise ValueError('measured RSS reaches/exceeds 110G: '+entry['name'])
        costs.append(dict(run=entry['name'], max_reported_rss_bytes=peak,
                          requested_bytes=MEMORY_BYTES, headroom_bytes=MEMORY_BYTES-peak,
                          capture_line=n, job_step=fields[0], host=fields[3], workers=6))
    if len(costs) != 6:
        raise ValueError('six completed smoke lanes required')
    return dict(capture=spec(capture), per_lane=costs,
        request='110G per 1-GPU job; four requests = 440G <= reported 450G node memory',
        limitation='Slurm sampled single-task MaxRSS; verify site cgroup/child accounting includes all six workers. '
                   'This is measured under the old unlimited allocation, not a 110G capacity test. '
                   'GPU HBM is separate; shared-node throughput remains unmeasured.')


def carry(old, new, smoke_plan, full_plan, capture, capture_sha, rss, rss_sha, out):
    proof = delta(old, new)
    out = Path(out).resolve()
    # Never create evidence inside the immutable old deployment or its attempt.
    old_plan = Path(smoke_plan).resolve()
    if out.is_relative_to(Path(old).resolve()) or out.is_relative_to(old_plan.parent.parent):
        raise ValueError('output must be outside the old deployment/attempt')
    out.mkdir(parents=True, exist_ok=False)
    checked = 'import stage_c,sys; stage_c.checked(sys.argv[1])'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    subprocess.run([sys.executable, '-B', '-c', checked, str(Path(full_plan).resolve())],
                   cwd=str(new), env=env, check=True)
    p = read(full_plan)
    if p['smoke'] or p['fixture'] or len(p['runs']) != 3:
        raise ValueError('fresh production full PLAN required')
    report_path = out/'ORIGINAL_SMOKE_IDENTITY.json'
    subprocess.run([sys.executable, '-B', str(Path(old).resolve()/'stage_c.py'), 'smoke-readout',
        '--plan', str(old_plan), '--sacct', str(Path(capture).resolve()), '--sacct-sha', capture_sha,
        '--out', str(report_path)], env=env, check=True)
    smoke = read(report_path)
    if (smoke['status'] != 'BIT_IDENTICAL' or smoke['mock'] is not False
            or smoke['package_sha256'] != OLD_SHA or smoke['runtime_sha256'] != p['runtime']['sha256']):
        raise ValueError('original CUDA identity/runtime mismatch')
    bound(smoke['plan'])
    if Path(smoke['plan']['path']) != old_plan or smoke['isolation']['status'] != 'PASS':
        raise ValueError('original smoke/Slurm isolation mismatch')
    proof.update(original_smoke=spec(report_path), new_full_plan=spec(full_plan),
                 memory=memory_report(read(old_plan), rss, rss_sha),
                 helper=spec(__file__), qualification='Original real-TERM CUDA identity carried across only Slurm memory request; '
                 '110G capacity/sharing not CUDA-tested; review measured RSS/headroom and child accounting before launch')
    # Do not relabel the original evidence. The derived report names its source
    # and compatibility proof; the sealed submit gate can bind this new file.
    smoke['source_package_sha256'] = smoke['package_sha256']
    smoke['package_sha256'] = NEW_SHA
    smoke['memory_only_compatibility'] = proof
    target = out/'SMOKE_COMPATIBLE.json'
    with target.open('x') as f:
        json.dump(smoke, f, sort_keys=True, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(target)
    return target


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('old', 'new', 'smoke-plan', 'full-plan', 'capture', 'capture-sha', 'rss', 'rss-sha', 'out'):
        parser.add_argument('--'+key, required=True)
    a = parser.parse_args()
    carry(a.old, a.new, a.smoke_plan, a.full_plan, a.capture, a.capture_sha, a.rss, a.rss_sha, a.out)

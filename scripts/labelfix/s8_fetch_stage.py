"""Build S8a3's bound payload; optionally deploy and sbatch --test-only.

Coordination only: never submits a job, runs extraction, or refreshes a cert.
Only the clariden SSH alias is reachable through this helper.
"""
from greekocr.ops.data_root import input_path as _data_input
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import time

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'docs/records/labelfix/spellcheck/S8_DEV/evidence'
BASE = '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017'
JOB = BASE + '/s8_dev_extract/job'
AUTH = ('permission denied', 'certificate', 'authentication', 'host key verification',
        'remote host identification has changed', 'sign_and_send_pubkey: signing failed')
TRANSIENT = ('timed out', 'timeout', 'connection reset', 'connection closed', 'broken pipe',
             'connection refused', 'no route to host', 'network is unreachable',
             'kex_exchange_identification', 'banner exchange', 'read from socket')


def digest(path):
    return hashlib.sha256(_data_input(path).read_bytes()).hexdigest()


def build(destination):
    preflight = json.loads((EVIDENCE / 'S8a3/remote_preflight.json').read_text())['metadata']
    request = json.loads((EVIDENCE / 'S8a3/request.json').read_text())
    fingerprint = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
    if fingerprint != preflight['request_sha256']:
        raise ValueError('local request differs from verified remote request')
    cache = EVIDENCE / 'dev_c1_alignments.json.gz'
    config = dict(base=BASE, out=BASE + '/s8_dev_extract', request_sha256=fingerprint,
                  expected_ids=600, expected_BE_shards=preflight['BE_shards'],
                  workers=32, budget_seconds=1050, local_alignment_cache=JOB + '/dev_c1_alignments.json.gz',
                  local_alignment_sha256=digest(cache))
    files = ['scripts/labelfix/s8_fetch_l1m.py', 'scripts/labelfix/s8_fetch_job.py',
             'scripts/labelfix/clariden/s8_fetch_job.sbatch']
    for name in files:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    shutil.copyfile(cache, destination / cache.name)
    (destination / 'job_config.json').write_text(json.dumps(config, indent=2, sort_keys=True) + '\n')
    files += [cache.name, 'job_config.json']
    manifest = destination / 'S8F_DEPLOY_SHA256.txt'
    manifest.write_text(''.join('{}  {}\n'.format(digest(destination / name), name) for name in sorted(files)))
    return manifest


def transport(script, log):
    records = []
    for attempt in range(1, 4):
        started = time.monotonic()
        try:
            proc = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15',
                                   '-o', 'ServerAliveInterval=10', '-o', 'ServerAliveCountMax=2',
                                   '-o', 'StrictHostKeyChecking=yes', 'clariden', 'bash -s'],
                                  input=script.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
            rc, stdout, stderr = proc.returncode, proc.stdout.decode(errors='replace'), proc.stderr.decode(errors='replace')
        except subprocess.TimeoutExpired as exc:
            rc = 124
            stdout = (exc.stdout or b'').decode(errors='replace')
            stderr = (exc.stderr or b'').decode(errors='replace') + '\nlocal transport timeout'
        records.append(dict(attempt=attempt, seconds=time.monotonic() - started,
                            returncode=rc, stdout=stdout, stderr=stderr))
        log.write_text(json.dumps(records, indent=2) + '\n')
        print(json.dumps(records[-1]), flush=True)
        if any(word in stderr.lower() for word in AUTH):
            raise SystemExit('STOP: authentication/certificate error; never refresh or retry')
        if rc == 0:
            return records[-1]
        if attempt == 3 or rc not in (124, 255) or not any(word in stderr.lower() for word in TRANSIENT):
            raise SystemExit('STOP: remote preparation failed; inspect ' + str(log))
        time.sleep((5, 15)[attempt - 1])


def deploy_script(bundle, manifest_sha):
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode='w:gz') as stream:
        names = [line.split('  ', 1)[1] for line in (bundle / 'S8F_DEPLOY_SHA256.txt').read_text().splitlines()]
        for name in names + ['S8F_DEPLOY_SHA256.txt']:
            stream.add(str(bundle / name), arcname=name, recursive=False)
    encoded = base64.b64encode(archive.getvalue()).decode()
    # Remote Python only reads metadata, verifies/stages small job files and
    # syntax-compiles them in memory. It never imports or invokes extraction.
    code = r'''
import ast,base64,gzip,hashlib,io,json,pathlib,tarfile
out=pathlib.Path('OUT'); job=out/'job'
assert job.resolve()==out.resolve()/'job', 'STOP: symlinked job directory'
request=json.loads((out/'request.json').read_text())
checkpoint=json.loads(gzip.decompress((out/'partial.json.gz').read_bytes()))
fingerprint=hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest()
assert fingerprint==checkpoint['request_sha256']=='REQUEST_SHA', 'STOP: request SHA mismatch'
before={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ('request.json','partial.json.gz')}
archive=tarfile.open(fileobj=io.BytesIO(base64.b64decode('ARCHIVE')),mode='r:gz')
job.mkdir(exist_ok=True)
for member in archive.getmembers():
    relative=pathlib.PurePosixPath(member.name)
    assert member.isfile() and not relative.is_absolute() and '..' not in relative.parts
    path=job/member.name
    assert path.resolve()==job.resolve()/relative, 'STOP: symlink in deployment path'
    raw=archive.extractfile(member).read()
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_bytes()==raw:continue
    tmp=path.with_name(path.name+'.deploy-tmp');tmp.write_bytes(raw);tmp.replace(path)
manifest=job/'S8F_DEPLOY_SHA256.txt'
assert hashlib.sha256(manifest.read_bytes()).hexdigest()=='MANIFEST_SHA'
for line in manifest.read_text().splitlines():
    expected,name=line.split('  ',1)
    assert hashlib.sha256((job/name).read_bytes()).hexdigest()==expected,name
    if name.endswith('.py'):compile((job/name).read_text(),str(job/name),'exec')
assert before=={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in before}
print(json.dumps(dict(deploy_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),request_sha256=fingerprint,
                     protected_inputs_sha256=before,BE_done=len(checkpoint['BE_done']),runtime=len(checkpoint['runtime']),
                     alignment_input_bytes={p.name:p.stat().st_size for p in (out.parent/'output_3679313/alignment').glob('worker_*.jsonl.gz')}),sort_keys=True))
'''
    config = json.loads((bundle / 'job_config.json').read_text())
    code = code.replace('OUT', BASE + '/s8_dev_extract').replace('REQUEST_SHA', config['request_sha256'])
    code = code.replace('MANIFEST_SHA', manifest_sha).replace('ARCHIVE', encoded)
    return "set -euo pipefail\npython3 - <<'S8F_STAGE_PY'\n" + code + "\nS8F_STAGE_PY\n" + r'''
S8F_JOB='JOB'
cd "$S8F_JOB"
sha256sum --check S8F_DEPLOY_SHA256.txt
bash -n scripts/labelfix/clariden/s8_fetch_job.sbatch
S8F_PROTECTED_BEFORE="$(sha256sum ../request.json ../partial.json.gz)"
sbatch --test-only --uenv-passthrough=ignore --chdir="$S8F_JOB" "$S8F_JOB/scripts/labelfix/clariden/s8_fetch_job.sbatch"
[[ "$(sha256sum ../request.json ../partial.json.gz)" == "$S8F_PROTECTED_BEFORE" ]]
sha256sum S8F_DEPLOY_SHA256.txt
'''.replace("'JOB'", repr(JOB))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--deploy-test-only', action='store_true')
    parser.add_argument('--log', type=Path)
    args = parser.parse_args()
    manifest = build(args.bundle)
    print('local manifest sha256: ' + digest(manifest), flush=True)
    if args.deploy_test_only:
        if args.log is None:
            parser.error('--log is required for deployment')
        transport(deploy_script(args.bundle, digest(manifest)), args.log)


if __name__ == '__main__':
    main()

"""Deploy the prepared package, verify hashes and sbatch --test-only. Never submits.

Stops on any authentication/certificate failure; only transient SSH transport
errors are retried (up to three retries, exponential backoff). All local artifacts
are inside this worktree. Never refreshes a certificate.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import tarfile
import time
from scripts.labelfix.clariden.r1_common import sha256, write_json

ROOT='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017'
SSH=['ssh','-o','BatchMode=yes','-o','ConnectTimeout=20','-o','StrictHostKeyChecking=yes','-o','ControlMaster=no','-o','ControlPath=none','clariden']
SCP=['scp','-o','BatchMode=yes','-o','ConnectTimeout=20','-o','StrictHostKeyChecking=yes','-o','ControlMaster=no','-o','ControlPath=none']
EV=Path('docs/records/labelfix/spellcheck/R2/evidence')


def remote(cmd):
    for attempt in range(4):
        result=subprocess.run(cmd,text=True,capture_output=True)
        if result.returncode==0:return result
        message=result.stderr.lower()
        if any(s in message for s in ('permission denied','certificate invalid','certificate has expired','authentication failed','sign_and_send_pubkey','too many authentication')):
            raise RuntimeError('AUTH/CERT ERROR: STOP; never refresh: '+result.stderr)
        transient=any(s in message for s in ('connection timed out','connection reset','connection closed','operation timed out','connection refused','broken pipe','no route to host'))
        if not transient or attempt==3:raise RuntimeError(result.stdout+result.stderr)
        time.sleep(2**(attempt+1))


def deploy():
    now=dt.datetime.now(dt.timezone(dt.timedelta(hours=3)))
    if now.date()!=dt.date(2026,10,17) or (now.hour,now.minute)>=(17,30):raise RuntimeError('deployment cutoff: finish local; deployment pending')
    files=set()
    for folder in ('greekocr','scripts/labelfix','tests/labelfix'):
        files.update(p for p in Path(folder).rglob('*.py') if '__pycache__' not in str(p))
    files.update(Path('greekocr/_vendor/codec').glob('*.json'))
    files.update(Path('artifacts/labelfix_r1/binding').glob('*.json'))
    files.update(Path('tests/labelfix/fixtures/r2').glob('*.json'))
    files.update(Path('tests/labelfix/fixtures/r2').glob('*.gz'))
    files.update([Path('scripts/labelfix/clariden/r2_job.sbatch'),Path('config/r2_job.json'),
        Path('docs/records/labelfix/spellcheck/R2/INPUT_FORMATS.md'),Path('docs/records/labelfix/spellcheck/R2/truth_overlay_v0.json'),
        Path('docs/records/labelfix/spellcheck/R2/truth_overlay_v1.json'),EV/'external_hashes.json'])
    cfg=json.loads(Path('config/r2_job.json').read_text())
    for key in ('line_list','roles'):
        if cfg.get(key): files.add(Path(cfg[key]))
    files.update([Path('artifacts/labelfix_r2/population/counts.json'),Path('artifacts/labelfix_r2/population/crop_staging.json')])
    ordered=sorted(files);manifest=Path('R2_DEPLOY_SHA256.txt')
    manifest.write_text(''.join(sha256(p)+'  '+str(p)+'\n' for p in ordered))
    listing=Path('docs/records/labelfix/spellcheck/R2/R2_DEPLOY_FILES.txt');listing.write_text('\n'.join(map(str,ordered))+'\n')
    archive=Path('artifacts/labelfix_r2/r2_deploy.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for p in [*ordered,manifest]:tar.add(p,arcname=str(p),recursive=False)
    remote([*SSH,f'mkdir -p {ROOT}/logs'])
    remote([*SCP,str(archive),f'clariden:{ROOT}/r2_deploy.tar.gz'])
    remote([*SSH,f'cd {ROOT} && tar -xzf r2_deploy.tar.gz && sha256sum --check R2_DEPLOY_SHA256.txt'])
    check=remote([*SSH,f'cd {ROOT} && sha256sum --check R2_DEPLOY_SHA256.txt'])
    (EV/'remote_sha_check.txt').write_text(check.stdout)
    if sum(line.endswith(': OK') for line in check.stdout.splitlines())!=len(ordered):raise RuntimeError('incomplete remote sha verification')
    # Import/config checks only on the login node: no images, model loading, or data extraction.
    code="import json; from greekocr.labelfix.release_gate import policy_binding; c=json.load(open('config/r2_job.json')); assert c['policy']==policy_binding(); from scripts.labelfix.clariden import r2_run; print(json.dumps(r2_run.validate(c,False)))"
    import_check=remote([*SSH,f"cd {ROOT} && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python -B -c \"{code}\""])
    (EV/'remote_import_check.txt').write_text(import_check.stdout+import_check.stderr)
    result=remote([*SSH,f"cd {ROOT} && sbatch --test-only --time={cfg['forecast']['requested_minutes']} scripts/labelfix/clariden/r2_job.sbatch"])
    (EV/'sbatch_test_only.txt').write_text(result.stdout+result.stderr)
    write_json(EV/'deploy_receipt.json',dict(target=ROOT,files=len(ordered),verified=len(ordered),
        archive_sha256=sha256(archive),manifest_sha256=sha256(manifest),
        test_only=dict(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr),
        imports=import_check.stdout,population=cfg['forecast']['population_lines'],submitted=False,certificate_refreshed=False,
        timestamp=now.isoformat()))
    Path('docs/records/labelfix/spellcheck/R2/R2_DEPLOY_SHA256.txt').write_bytes(manifest.read_bytes())
    print(json.dumps(dict(verified=len(ordered),total=len(ordered),test_only=result.returncode)))

if __name__=='__main__':deploy()

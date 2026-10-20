"""GC1 staging/dry-run/deploy/SHA/test-only. No submit code or Git writes."""
import datetime as dt
import json
from pathlib import Path
import shlex
import subprocess
import time
from scripts.labelfix.clariden.r1_common import sha256
from scripts.labelfix.clariden.sf7_recompose import receipt

EV=Path('docs/records/labelfix/spellcheck/SF7_evidence')
ROOT='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_20261017'
SSH=['ssh','-o','BatchMode=yes','-o','ConnectTimeout=20','-o','ConnectionAttempts=1',
     '-o','ServerAliveInterval=15','-o','ServerAliveCountMax=2','clariden']


def remote(command, name, payload=None, timeout=300):
    for attempt in range(1,4):
        p=subprocess.run([*SSH,command],input=payload,capture_output=True,timeout=timeout)
        text=p.stdout.decode(errors='replace')+p.stderr.decode(errors='replace')
        (EV/(name+f'_attempt{attempt}.log')).write_text(command+'\n'+text+f'\nEXIT_CODE={p.returncode}\n')
        if p.returncode==0:return p.stdout
        if any(s in text.lower() for s in ('permission denied','certificate','authentication failed','sign_and_send_pubkey')):
            raise RuntimeError('authentication/certificate failure: STOP; no refresh')
        if p.returncode!=255 or attempt==3:raise RuntimeError(name+' failed: '+text[-2000:])
        time.sleep(2**attempt)


def deploy():
    # Local certificate inspection never changes or refreshes credentials.
    cert=subprocess.run(['ssh-keygen','-Lf',str(Path.home()/'.ssh/cscs-key-cert.pub')],capture_output=True,text=True,check=True)
    (EV/'certificate.txt').write_text(cert.stdout+cert.stderr)
    stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    stage=ROOT+'/predeploy/'+stamp
    archive=Path('artifacts/labelfix_sf7/deploy.tar').read_bytes()
    remote(f'mkdir -p {shlex.quote(stage)} && tar -xf - -C {shlex.quote(stage)}','stage_transfer',archive)
    remote(f'cd {shlex.quote(stage)} && sha256sum --check SF7_DEPLOY_SHA256.txt','stage_sha')
    dry=stage+'/dryrun_2000'
    remote(f'cd {shlex.quote(stage)} && CUDA_VISIBLE_DEVICES="" bash scripts/labelfix/clariden/sf7_job.sbatch --dry-run --out {shlex.quote(dry)}','real_input_dryrun',timeout=300)
    # Verify both composed streams/controls and complete final receipt in place.
    code="""import json,gzip,hashlib,pathlib
p=pathlib.Path(%r); r=json.loads((p/'receipt.json').read_text())
assert r['complete'] and r['dry_run'] and r['lines']==2000
for name,h in r['outputs'].items(): assert hashlib.sha256((p/name).read_bytes()).hexdigest()==h
for v in 'AB':
 rows=[json.loads(x) for x in gzip.open(p/'release'/f'overlay_{v}.jsonl.gz','rt')]
 assert len(rows)==2000 and len({x['line_id'] for x in rows})==2000
 assert all(x['policy']=='sf7-release-v1' and x['variant']==v and 'rule_traces' in x for x in rows)
print(json.dumps(r))
""" % dry
    command=f'/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python -B -c {shlex.quote(code)}'
    result=remote(command,'dryrun_readback');data=json.loads(result)
    receipt(EV/'real_input_dryrun_receipt.json',data)
    # Only a successful real-input composition is promoted to the final root.
    remote(f'mkdir -p {ROOT}/logs && tar -xf - -C {ROOT}','deploy_transfer',archive)
    remote(f'cd {ROOT} && sha256sum --check SF7_DEPLOY_SHA256.txt','remote_sha')
    envelope=remote(f'cd {ROOT} && sha256sum SF7_DEPLOY_SHA256.txt','manifest_sha').decode().split()[0]
    if envelope!=sha256('SF7_DEPLOY_SHA256.txt'):raise ValueError('manifest envelope differs')
    result=remote(f'cd {ROOT} && sbatch --test-only scripts/labelfix/clariden/sf7_job.sbatch','test_only')
    receipt(EV/'deploy_receipt.json',dict(remote_root=ROOT,predeploy_root=stage,
        files=len(Path('SF7_DEPLOY_SHA256.txt').read_text().splitlines()),
        manifest_sha256=envelope,all_remote_sha_match=True,dry_run_exit=0,dry_run_lines=2000,
        dry_run_seconds=data['elapsed_seconds'],test_only_exit=0,submitted=False,certificate_refreshed=False))
    print(result.decode())


if __name__=='__main__':deploy()

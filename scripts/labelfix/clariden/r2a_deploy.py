"""R2a package build/deploy/SHA/test-only. Never submits or refreshes certificates."""
import argparse
import datetime as dt
import json
from pathlib import Path
import shlex
import subprocess
from scripts.labelfix.clariden.r1_common import rows,sha256
from scripts.labelfix.clariden.r2_util import atomic_json as write_json
from scripts.labelfix.clariden.r2_deploy import remote,SSH
from scripts.labelfix.clariden.r2a_prepare import ROOT,INPUT

EV=Path('docs/records/labelfix/spellcheck/R2/evidence/r2a')
SHA=Path('R2A_DEPLOY_SHA256.txt');FILES=Path('R2A_DEPLOY_FILES.txt')
VERIFY=Path.home()/'Projects/greek-page-ocr-wave1e/scripts/ops/verify_deploy.py'


def build():
    cfg=json.loads(Path('config/r2a_job.json').read_text())
    files={Path(s) for s in Path('docs/records/labelfix/spellcheck/R2/R2_DEPLOY_FILES.txt').read_text().splitlines() if s}
    files.update(Path('scripts/labelfix/clariden').glob('r2a*'))
    files.update(Path('artifacts/r2a_manifest').glob('*'))
    files.add(Path('docs/records/labelfix/spellcheck/R2/B6_RESOLVE_REPORT.md'))
    files.update([Path('config/r2a_job.json'),Path('tests/labelfix/test_r2a_package.py'),Path('artifacts/r2a_manifest/receipt.json'),INPUT/'custody.json'])
    for p in cfg['sha256']:
        if not Path(p).is_absolute():files.add(Path(p))
    for key in ('native','witness','dev'):
        for r in rows(cfg[key]):files.add(Path(r['crop']).relative_to(ROOT))
    missing=[str(p) for p in files if not p.is_file()]
    if missing:raise ValueError('missing package files: '+repr(missing))
    files={p for p in files if '__pycache__' not in str(p)}
    # Both deploy scripts and the readback validator accompany the runtime.
    files.add(Path('scripts/labelfix/r2_readback_verify.py'))
    files.add(FILES); ordered=sorted(files)
    FILES.write_text(''.join(str(p)+'\n' for p in ordered))
    SHA.write_text(''.join(sha256(p)+'  '+str(p)+'\n' for p in ordered))
    # No index writes. Record every exact deployed path absent/different in HEAD.
    needed=[]
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    handoff=[EV/'VERIFY_CMD.sh',Path('docs/records/labelfix/spellcheck/R2/R2A_PACKAGE_REPORT.md'),*EV.glob('r2j3*'),*EV.glob('r2j4*'),EV/'old_pool_duplicates.json',EV/'dryrun_stageAB.txt',EV/'package_receipt.json',EV/'deploy_receipt.json',EV/'remote_sha.txt',EV/'remote_manifest_sha.txt',EV/'test_only.txt',EV/'rsync.txt',EV/'certificate.txt']
    for p in ordered+[SHA]+[p for p in handoff if p.exists()]:
        r=subprocess.run(['git','show',f'{head}:{p}'],capture_output=True)
        import hashlib
        if r.returncode or hashlib.sha256(r.stdout).hexdigest()!=sha256(p):needed.append(str(p))
    EV.mkdir(parents=True,exist_ok=True)
    needed=sorted(set(needed+[str(EV/'LEAD_COMMIT_PATHS.txt'),str(EV/'package_receipt.json')]))
    (EV/'LEAD_COMMIT_PATHS.txt').write_text('\n'.join(needed)+'\n')
    write_json(EV/'package_receipt.json',dict(files=len(ordered),bytes=sum(p.stat().st_size for p in ordered),
        sha_file_sha256=sha256(SHA),file_list_sha256=sha256(FILES),lead_commit_paths=len(needed),head=head,
        every_payload_hashed=True,sha_manifest_envelope='sha_file_sha256 in this receipt',submitted=False))
    print(json.dumps(dict(files=len(ordered),lead_commit_paths=len(needed))))


def deploy():
    cfg=json.loads(Path('config/r2a_job.json').read_text())
    if cfg.get('readiness',{}).get('native_width_decision_pending'):
        raise RuntimeError('STOP: supplied R2a slot fails frozen width gate; coordinator clarification pending')
    expiry=dt.datetime(2026,10,17,16,18,tzinfo=dt.timezone.utc)
    if dt.datetime.now(dt.timezone.utc)>=expiry:raise RuntimeError('CERT EXPIRED: STOP; never refresh')
    # Read validity locally. Never creates or refreshes a certificate.
    cert=subprocess.run(['ssh-keygen','-Lf',str(Path.home()/'.ssh/cscs-key-cert.pub')],capture_output=True,text=True,check=True)
    (EV/'certificate.txt').write_text(cert.stdout+cert.stderr)
    remote([*SSH,f'mkdir -p {ROOT}/logs'])
    ssh=shlex.join(SSH[:-1])
    transfer=remote(['rsync','-a','--files-from='+str(FILES),'-e',ssh,'./',f'clariden:{ROOT}/'])
    (EV/'rsync.txt').write_text(transfer.stdout+transfer.stderr)
    remote(['rsync','-a','-e',ssh,str(SHA),f'clariden:{ROOT}/'])
    check=remote([*SSH,f'cd {ROOT} && sha256sum --check {SHA}'])
    (EV/'remote_sha.txt').write_text(check.stdout+check.stderr)
    count=len(FILES.read_text().splitlines());matched=sum(s.endswith(': OK') for s in check.stdout.splitlines())
    if count!=matched:raise RuntimeError('incomplete remote SHA comparison')
    # Hash the SHA manifest separately so its envelope is also checked.
    envelope=remote([*SSH,f'cd {ROOT} && sha256sum {SHA}'])
    if envelope.stdout.split()[0]!=sha256(SHA):raise RuntimeError('SHA manifest envelope differs')
    (EV/'remote_manifest_sha.txt').write_text(envelope.stdout)
    verify_dry_run()
    check=remote([*SSH,f'cd {ROOT} && sbatch --test-only --time=81 scripts/labelfix/clariden/r2a_job.sbatch'])
    (EV/'test_only.txt').write_text(check.stdout+check.stderr)
    write_json(EV/'deploy_receipt.json',dict(remote_root=str(ROOT),files=count,matched=matched,
        sha_file_sha256=sha256(SHA),test_only=dict(returncode=check.returncode,stdout=check.stdout,stderr=check.stderr),
        submitted=False,certificate_refreshed=False,timestamp=dt.datetime.now(dt.timezone.utc).isoformat()))
    print(json.dumps(dict(files=count,sha_match=matched,test_only=check.returncode,submitted=False)))

def verify_dry_run():
    """Real A+B, login CPU only; no allocation or training. Part of deploy verification."""
    stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out=f'{ROOT}/dryrun/r2j4_{stamp}'
    cmd=f'cd {ROOT} && CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH={ROOT} /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python -B -u scripts/labelfix/clariden/r2a_run.py --config config/r2a_job.json --out {out} --dry-run-ab --dry-run-witness-alignments {ROOT}/failed_output_3682401/B/witness_alignments.jsonl.gz'
    result=remote([*SSH,cmd])
    (EV/'dryrun_stageAB.txt').write_text(cmd+'\n'+result.stdout+result.stderr+'\nEXIT_CODE=0\n')
    receipt=remote([*SSH,f'cat {out}/B/overlay_receipt.json {out}/dryrun_receipt.json'])
    (EV/'r2j4_real_receipts.txt').write_text(receipt.stdout)
    print('REAL_INPUT_AB_DRY_RUN exit 0',flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--deploy',action='store_true');ap.add_argument('--verify-dry-run',action='store_true');a=ap.parse_args()
    if a.verify_dry_run:verify_dry_run()
    elif a.deploy:deploy()
    else:build()

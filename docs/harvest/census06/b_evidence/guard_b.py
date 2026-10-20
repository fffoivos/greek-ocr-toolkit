"""Read-only guard for the lead's explicit B commit list; does not stage or commit."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[4];D=R/'docs/harvest/census06';S=R.parent/'greek-ocr-toolkit-census06-verify'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
paths=(D/'B_COMMIT_PATHS.txt').read_text().splitlines();assert len(paths)==len(set(paths))
seal='docs/harvest/census06/B_COMMIT_SHA256SUMS'
entries=[line.split('  ',1) for line in (R/seal).read_text().splitlines()]
assert set(paths)=={p for _,p in entries}|{seal}
for h,p in entries:
 q=Path(p);assert not q.is_absolute() and '..' not in q.parts
 assert p.startswith('docs/harvest/census06/') and (R/p).is_file() and not (R/p).is_symlink()
 assert sha(R/p)==h,p
for line in (S/'docs/harvest/census06/DEPLOY_SHA256SUMS').read_text().splitlines():
 h,p=line.split('  ',1);assert sha(R/p)==h,p
assert subprocess.check_output(['git','--no-optional-locks','-C',str(S),'rev-parse','HEAD']).decode().strip()=='cf1db4dd48690544f4a88c208a082a0af4e5a4f7'
assert not subprocess.check_output(['git','--no-optional-locks','-C',str(S),'status','--porcelain'])
for kind in ['regression','parity','census','readout']:
 r=json.loads((D/'b_evidence'/('verify-'+kind+'.json')).read_text());assert r['verdict']=='VERIFY_OK';assert not r['steps']['local']['allowed_untracked'];assert r['job_submitted'] is False
assert all(not (D/p).exists() for p in ['033-regression-tmp','baseline-regression-tmp','test-tmp'])
print('B_COMMIT_GUARD_OK',len(paths),'exact paths; payload unchanged; clean lead worktree; no Git writes')

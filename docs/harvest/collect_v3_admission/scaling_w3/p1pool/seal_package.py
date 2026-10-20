"""Local sealing only. No network, git mutation or submission."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
GENERATED={'PACKAGE_FILES.json','PACKAGE_ID','DEPLOY_SHA256SUMS','DEPLOY_PATHS.txt','DEPLOY_READBACK.json','COMMIT_LIST.json','COMMIT_LIST.md','verify.log'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def files():
    return sorted(f for f in ROOT.rglob('*') if f.is_file() and '__pycache__' not in f.parts and '.pytest_cache' not in f.parts and 'pytest-basetemp' not in f.parts and f.relative_to(ROOT).parts[0] not in GENERATED)
if __name__=='__main__':
    entries={str(f.relative_to(ROOT)):sha(f) for f in files()}
    (ROOT/'PACKAGE_FILES.json').write_text(json.dumps(entries,indent=2,sort_keys=True)+'\n')
    names=sorted(list(entries)+['PACKAGE_FILES.json'])
    sums=''.join(sha(ROOT/n)+'  '+n+'\n' for n in names)
    (ROOT/'DEPLOY_SHA256SUMS').write_text(sums)
    ident=sha(ROOT/'DEPLOY_SHA256SUMS');(ROOT/'PACKAGE_ID').write_text(ident+'\n')
    names+=['DEPLOY_SHA256SUMS','PACKAGE_ID','DEPLOY_PATHS.txt','COMMIT_LIST.json','COMMIT_LIST.md']
    (ROOT/'DEPLOY_PATHS.txt').write_text('\n'.join(sorted(names))+'\n')
    prefix=str(ROOT.relative_to(Path.cwd()))
    commit={prefix+'/'+n:sha(ROOT/n) for n in names if n not in ('COMMIT_LIST.json','COMMIT_LIST.md')}
    brief='docs/briefs/P1POOL_unlabelled_pool.md';commit[brief]=sha(Path(brief))
    (ROOT/'COMMIT_LIST.json').write_text(json.dumps(commit,indent=2,sort_keys=True)+'\n')
    (ROOT/'COMMIT_LIST.md').write_text('# Guarded commit list\n\nNo git add or git commit was run. Before staging, run `python3 '+prefix+'/guard_commit.py`. Stage only the exact paths in COMMIT_LIST.json plus COMMIT_LIST.json and COMMIT_LIST.md themselves. DEPLOY_READBACK.json and verify.log may be included only after their successful readback is reviewed. Do not stage concurrent census06, c2, g_audit or unrelated changes.\n')
    print(ident[:8])

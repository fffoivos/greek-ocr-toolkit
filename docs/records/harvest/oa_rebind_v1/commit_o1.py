"""Owner-side guarded commit after managed shared-index denial. Never pushes."""
import hashlib,json,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
PREFIX=str(BASE.relative_to(ROOT))+'/'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def main():
    receipt=json.loads((BASE/'receipts/commit-inputs.json').read_text())
    if git('rev-parse','HEAD')!=receipt['head']:raise SystemExit('HEAD changed; review and refresh the commit receipt before staging.')
    if git('branch','--show-current')!=receipt['branch']:raise SystemExit('Branch changed; refusing to stage.')
    files={p['path']:p for p in receipt['files']}
    actual={str(p.relative_to(ROOT)) for p in BASE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='commit-inputs.json'}
    if actual!=set(files):raise SystemExit('Audit file set changed; refusing to stage.')
    for name,entry in files.items():
        p=ROOT/name
        if not name.startswith(PREFIX) or p.is_symlink():raise SystemExit('Path escaped audit scope: '+name)
        b=p.read_bytes()
        if len(b)!=entry['bytes'] or hashlib.sha256(b).hexdigest()!=entry['sha256']:raise SystemExit('Audit file changed: '+name)
    staged=git('diff','--cached','--name-only').splitlines()
    if any(not p.startswith(PREFIX) for p in staged):raise SystemExit('Unrelated staged paths exist; refusing to stage or commit.')
    if '--check' in sys.argv:
        print(f'Validated {len(files)} audit files; HEAD/branch unchanged; no staging or commit performed.')
        return
    subprocess.run(['git','add','--',PREFIX.rstrip('/')],cwd=ROOT,check=True)
    expected=set(files)|{str((BASE/'receipts/commit-inputs.json').relative_to(ROOT))}
    staged=set(git('diff','--cached','--name-only').splitlines())
    if staged!=expected:raise SystemExit('Staged file set differs from the source-bound audit; refusing to commit.')
    subprocess.run(['git','commit','-m','Audit wave-4 Open Archives provenance and correction bindings'],cwd=ROOT,check=True)
    print('Committed '+git('rev-parse','HEAD')+'; no push performed.')
if __name__=='__main__':main()

"""Owner-side guarded O2 commit helper. Validates all artifacts; never pushes."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
PREFIX=str(BASE.relative_to(ROOT))+'/'
RECEIPT=BASE/'receipts/commit-inputs.json'

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return dict(bytes=path.stat().st_size,sha256=h.hexdigest())

def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def check():
    receipt=json.loads(RECEIPT.read_text())
    if git('rev-parse','HEAD')!=receipt['head']:raise SystemExit('HEAD changed; review and refresh the O2 receipt before committing.')
    if git('branch','--show-current')!=receipt['branch']:raise SystemExit('Branch changed; refusing to stage.')
    files={e['path']:e for e in receipt['files']}
    actual={str(p.relative_to(ROOT)) for p in BASE.rglob('*') if p.is_file() and p!=RECEIPT}
    if actual!=set(files):raise SystemExit('O2 file set changed; refusing to stage.')
    for name,e in files.items():
        p=ROOT/name
        if not name.startswith(PREFIX) or p.is_symlink() or not p.resolve().is_relative_to(BASE):raise SystemExit('Path escaped O2 scope: '+name)
        if digest(p)!={k:e[k] for k in ['bytes','sha256']}:raise SystemExit('O2 output changed: '+name)
    # Recheck the source snapshots. This includes the immutable release inputs,
    # exact page witnesses, pinned link table and original O1 download receipts.
    checked=set()
    for name in ['duplicate-inputs.json','release-inputs.json','candidate-local-inputs.json']:
        for e in json.loads((BASE/'receipts'/name).read_text()):
            if e['path'] in checked:continue
            p=Path(e['path'])
            if digest(p)!={k:e[k] for k in ['bytes','sha256']}:raise SystemExit('Audit source changed: '+str(p))
            checked.add(e['path'])
    validation=json.loads((BASE/'receipts/validation.json').read_text())
    if not validation['passed']:raise SystemExit('Release readback did not pass.')
    release=json.loads((BASE/'v2_meta1/receipt.json').read_text())
    if not release['passed'] or any(release[k] for k in ['lines_added','lines_dropped','lines_moved','labels_changed','ids_changed','admission_decisions_changed']):raise SystemExit('Not a metadata-only release.')
    staged=git('diff','--cached','--name-only').splitlines()
    if any(not p.startswith(PREFIX) for p in staged):raise SystemExit('Unrelated staged paths exist; refusing to stage or commit.')
    return files,checked

def main():
    files,sources=check()
    if '--check' in sys.argv:
        print(f'Validated {len(files)} O2 outputs and {len(sources)} unchanged source files; HEAD/branch unchanged; no staging or commit performed.')
        return
    subprocess.run(['git','add','--',PREFIX.rstrip('/')],cwd=ROOT,check=True)
    expected=set(files)|{str(RECEIPT.relative_to(ROOT))}
    staged=set(git('diff','--cached','--name-only').splitlines())
    if staged!=expected:raise SystemExit('Staged set differs from the source-bound O2 receipt; refusing to commit.')
    subprocess.run(['git','commit','-m','Release collection v2-meta1 metadata rebind and audit cross-split edition keys'],cwd=ROOT,check=True)
    print('Committed '+git('rev-parse','HEAD')+'; no push performed.')

if __name__=='__main__':main()

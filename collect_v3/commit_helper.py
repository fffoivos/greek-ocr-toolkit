#!/usr/bin/env python3
"""Validate W1d delivery; optionally stage/commit enumerated, nonignored files once."""
import argparse,subprocess,sys
from pathlib import Path
if __package__ in (None,''):sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collect_v3.common import read_json,write_json,sha,scrub
ROOT=Path(__file__).resolve().parents[1]
BASE='76c3cc9a6dd8cfa993b9ee2d0187f03479ffdf37'
W1C_BASE='217ddf24'
SCOPE=('collect_v3/','worker/','docs/harvest/collect_v3/')


def git(*args,input=None,root=None):
    return subprocess.run(['git',*args],cwd=root or ROOT,capture_output=True,text=True,input=input)


def checked(*args):
    result=git(*args)
    if result.returncode:raise RuntimeError(scrub(result.stderr.strip()))
    return result.stdout.strip()


def nonignored(paths,root=None):
    """--no-index also excludes previously tracked files now covered by ignores."""
    result=git('check-ignore','--no-index','-z','--stdin',input='\0'.join(paths)+'\0',root=root)
    if result.returncode not in (0,1):raise RuntimeError(scrub(result.stderr))
    ignored=set(result.stdout.rstrip('\0').split('\0')) if result.stdout else set()
    return [name for name in paths if name not in ignored],sorted(ignored)


def recovery_patch(paths,destination,root=None,base=BASE):
    """No index writes: include tracked changes and explicitly enumerated new files."""
    root=Path(root or ROOT);paths,ignored=nonignored(paths,root=root)
    tracked=git('ls-files','-z','--',*paths,root=root)
    if tracked.returncode:raise RuntimeError(scrub(tracked.stderr))
    tracked=set(tracked.stdout.rstrip('\0').split('\0')) if tracked.stdout else set()
    patch=''
    if tracked:
        diff=git('diff','--binary',base,'--',*sorted(tracked),root=root)
        if diff.returncode:raise RuntimeError(scrub(diff.stderr))
        patch=diff.stdout
    for name in paths:
        if name in tracked:continue
        addition=git('diff','--no-index','--binary','--','/dev/null',name,root=root)
        if addition.returncode not in (0,1):raise RuntimeError(scrub(addition.stderr))
        patch+=addition.stdout
    from collect_v3.common import atomic_bytes
    atomic_bytes(destination,patch.encode())
    return dict(path=str(destination),sha256=sha(destination),base=base,ignored_excluded=ignored)


def main(commit=False):
    if checked('branch','--show-current')!='sol/collect-v3':raise ValueError('wrong branch')
    if git('merge-base','--is-ancestor',W1C_BASE,'HEAD').returncode:raise ValueError('W1c base missing')
    if checked('rev-parse','HEAD')!=BASE:raise ValueError('HEAD changed; review before rebasing this guarded commit')
    if checked('diff','--cached','--name-only'):raise ValueError('other staged work; preserve it')
    manifest=read_json(ROOT/'docs/harvest/collect_v3/build_manifest.json')
    paths=list(manifest['sha256'])+['docs/harvest/collect_v3/build_manifest.json']
    for name in paths:
        path=Path(name)
        if not (name=='.gitignore' or name.startswith(SCOPE)) or path.is_absolute() or '..' in path.parts:raise ValueError('path outside build scope')
    paths,ignored=nonignored(paths)
    for name in paths:
        if name=='docs/harvest/collect_v3/build_manifest.json':continue
        digest=manifest['sha256'][name];path=Path(name)
        p=ROOT/path
        if p.is_symlink() or not p.is_file() or sha(p)!=digest:raise ValueError('build file changed: '+name)
    if not paths:raise ValueError('empty build')
    if not commit:
        print(f'validated {len(paths)} nonignored files; excluded {len(ignored)} ignored paths; branch/base/hashes match');return 0
    receipt=ROOT/'docs/harvest/collect_v3/W1d_commit_status.json'
    staged=git('add','--',*paths)
    if staged.returncode:
        patch=recovery_patch(paths,ROOT/'worker/handoff/W1d.patch')
        write_json(receipt,dict(committed=False,staged=False,reason=scrub(staged.stderr.strip()),ignored_excluded=ignored,guarded_helper='collect_v3/commit_helper.py --commit',retry_attempted=False,recovery_patch=patch));print('Git staging unavailable; source-bound recovery patch retained.',file=sys.stderr);return 2
    actual=set(checked('diff','--cached','--name-only').splitlines())
    if actual-set(paths):raise ValueError('unexpected staged files; commit refused')
    result=git('commit','-m','W1d: rebalance BSB/IA and prepare offline-qualified Linux worker')
    if result.returncode:
        write_json(receipt,dict(committed=False,staged=True,reason=scrub(result.stderr.strip()),retry_attempted=False));return 2
    head=checked('rev-parse','HEAD');write_json(receipt,dict(committed=True,commit=head,ignored_excluded=ignored));print(head);return 0

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--commit',action='store_true');a=p.parse_args()
    try:sys.exit(main(a.commit))
    except Exception as e:print(f'{type(e).__name__}: {scrub(e)}',file=sys.stderr);sys.exit(1)

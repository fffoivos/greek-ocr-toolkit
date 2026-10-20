"""Hash-bound T6f/T6f2 commit list. Default is read-only; --commit is for the coordinator.

No alternate index and no retry after a Git write failure. Ignores work/ crops.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
HEAD='1a85772173ccae3853a7568319e31729fdfe6127'
MANIFEST=BASE/'commit-inputs.json'


def git(*args,check=True,stdin=None):
    return subprocess.run(['git',*args],cwd=ROOT,input=stdin,capture_output=True,check=check)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate():
    assert git('rev-parse','HEAD').stdout.decode().strip()==HEAD, 'HEAD changed'
    assert git('branch','--show-current').stdout.decode().strip()=='sol/recut-v1'
    assert not git('diff','--cached','--name-only').stdout.strip(), 'index must start empty'
    m=json.loads(MANIFEST.read_text())
    assert m['base_HEAD']==HEAD and m['branch']=='sol/recut-v1'
    paths=[]
    for r in m['files']:
        p=ROOT/r['path']
        assert p.resolve().is_relative_to(BASE) and not p.is_symlink()
        assert '/work/' not in str(p) and sha(p)==r['sha256'],str(p)
        paths.append(r['path'])
    paths.append(str(MANIFEST.relative_to(ROOT)))
    assert len(set(paths))==len(paths)
    ignored=git('check-ignore','--no-index','-z','--stdin',check=False,stdin=b''.join(p.encode()+b'\0' for p in paths))
    assert ignored.returncode in (0,1) and not ignored.stdout,'ignored path in commit list'
    return m,paths


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--commit',action='store_true');a=p.parse_args()
    m,paths=validate()
    if not a.commit:
        print('CHECK PASS:',len(paths),'hash-bound files, expected HEAD/branch, empty index, no ignored paths')
    else:
        # A failure is terminal. This helper neither retries nor changes indexes.
        git('add','--',*paths)
        staged=set(git('diff','--cached','--name-only').stdout.decode().splitlines())
        assert staged==set(paths),'unexpected staged set'
        git('diff','--cached','--check')
        r=git('commit','-m',m['message'])
        print(r.stdout.decode())

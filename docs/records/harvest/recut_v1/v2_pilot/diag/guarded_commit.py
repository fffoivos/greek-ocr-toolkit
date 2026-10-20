"""T6c1b source-bound commit, adapted from masking/guarded_commit.py.

Only diag/**, ignored paths excluded, exact HEAD/branch, empty index, no force,
no retry and no alternate index. Receipts and manifest stay inside diag/.
"""
from __future__ import annotations
import os
import sys
sys.dont_write_bytecode=True
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[4]
MANIFEST=BASE/'commit-inputs.json'
STATUS=BASE/'COMMIT_STATUS.json'
EXPECTED_HEAD='616e4ad83162ecb727ceccc642c5f03ea34a078b'
EXCLUDE={MANIFEST,STATUS,BASE/'commit.log'}


def git(*args,check=True,stdin=None):
    return subprocess.run(['git',*args],cwd=ROOT,input=stdin,capture_output=True,check=check,
                          env=os.environ|{'GIT_TERMINAL_PROMPT':'0','GIT_OPTIONAL_LOCKS':'0'})


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n')


def ignored(paths):
    r=git('check-ignore','--no-index','-z','--stdin',check=False,
          stdin=b''.join(p.encode()+b'\0' for p in paths))
    if r.returncode not in (0,1):
        raise RuntimeError(r.stderr.decode())
    return {p.decode() for p in r.stdout.split(b'\0') if p}


def allowed(path):
    p=ROOT/path
    return p.resolve().is_relative_to(BASE) and not p.is_symlink() and p not in EXCLUDE


def guards():
    if os.getpriority(os.PRIO_PROCESS,0)<15:
        raise RuntimeError('require actual nice >=15')
    if git('branch','--show-current').stdout.decode().strip()!='sol/recut-v1':
        raise RuntimeError('wrong branch')
    if git('rev-parse','HEAD').stdout.decode().strip()!=EXPECTED_HEAD:
        raise RuntimeError('unexpected starting HEAD')
    if git('diff','--cached','--name-only').stdout.strip():
        raise RuntimeError('unrelated staged content')
    if STATUS.exists() and json.loads(STATUS.read_text()).get('status')=='commit_blocked':
        raise RuntimeError('previous Git failure is terminal; no retry')


def prepare():
    guards()
    candidates=sorted(str(p.relative_to(ROOT)) for p in BASE.rglob('*') if p.is_file() and p not in EXCLUDE)
    excluded=ignored(candidates)
    paths=[p for p in candidates if p not in excluded]
    if any(not allowed(p) for p in paths):
        raise RuntimeError('path escapes diag scope')
    if not (BASE/'validation.json').exists() or not json.loads((BASE/'validation.json').read_text())['passed']:
        raise RuntimeError('completed artifact validation required')
    write(MANIFEST,dict(schema='t6c1b-guarded-commit-1',base_HEAD=EXPECTED_HEAD,branch='sol/recut-v1',
                        files=[dict(path=p,sha256=digest(ROOT/p)) for p in paths],
                        ignored_paths_excluded=len(excluded),scope=str(BASE.relative_to(ROOT))+'/**',
                        message='harvest: diagnose T6c1 matching failures and verify opt-in overlap parity'))
    print('Prepared',len(paths),'files; excluded',len(excluded),'ignored paths')


def validate():
    guards();manifest=json.loads(MANIFEST.read_text())
    if manifest['base_HEAD']!=EXPECTED_HEAD:
        raise RuntimeError('manifest HEAD changed')
    paths=[r['path'] for r in manifest['files']]
    if ignored(paths+[str(MANIFEST.relative_to(ROOT))]):
        raise RuntimeError('ignored path in manifest')
    current={str(p.relative_to(ROOT)) for p in BASE.rglob('*') if p.is_file() and p not in EXCLUDE}
    current-=ignored(sorted(current))
    if current!=set(paths):
        raise RuntimeError('diagnostic file set changed after prepare')
    for row in manifest['files']:
        if not allowed(row['path']) or digest(ROOT/row['path'])!=row['sha256']:
            raise RuntimeError('scope/hash changed: '+row['path'])
    return manifest,paths+[str(MANIFEST.relative_to(ROOT))]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--check-only',action='store_true');args=parser.parse_args()
    if args.prepare:
        prepare();return
    manifest,paths=validate()
    if args.check_only:
        print('Validated',len(paths),'paths; exact HEAD/branch, empty index, no ignored files');return
    try:
        git('add','--',*paths)
        if set(git('diff','--cached','--name-only').stdout.decode().splitlines())!=set(paths):
            raise RuntimeError('staged paths differ from manifest')
        git('diff','--cached','--check')
        result=git('commit','-m',manifest['message'])
        head=git('rev-parse','HEAD').stdout.decode().strip()
        write(STATUS,dict(status='committed',commit=head,manifest_sha256=digest(MANIFEST)))
        print(result.stdout.decode());print(head)
    except (subprocess.CalledProcessError,RuntimeError) as exc:
        message=(exc.stderr or exc.stdout or b'').decode(errors='replace') if isinstance(exc,subprocess.CalledProcessError) else str(exc)
        write(STATUS,dict(status='commit_blocked',reason=message,base_HEAD=EXPECTED_HEAD,
                          retry_attempted=False,alternate_index_used=False,manifest_sha256=digest(MANIFEST)))
        print(message,file=sys.stderr);raise SystemExit(1)


if __name__=='__main__':
    main()

"""Source-bound T6a commit helper; excludes all git-ignored paths, never forces.

--prepare writes a manifest, --check-only validates it, no flag commits it.
An index permission failure is terminal: no retry and no alternate index.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
MANIFEST=BASE/'commit-inputs.json'
STATUS=BASE/'COMMIT_STATUS.json'
EXPECTED_HEAD='66a186a91bfa58086460708f9b87017efd60d622'
EXPLICIT=('greekocr/glyphs/vertical_recut.py','tests/glyphs/test_vertical_recut.py')


def git(*args,check=True,stdin=None):
    return subprocess.run(['git',*args],cwd=ROOT,input=stdin,capture_output=True,check=check)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ignored(paths):
    result=git('check-ignore','--no-index','-z','--stdin',check=False,
               stdin=b''.join(p.encode()+b'\0' for p in paths))
    if result.returncode not in (0,1):raise RuntimeError(result.stderr.decode())
    return {p.decode() for p in result.stdout.split(b'\0') if p}


def allowed(path):
    value=Path(path)
    target=(ROOT/value).resolve()
    return (path in EXPLICIT or target.is_relative_to(BASE.resolve())) and not (ROOT/value).is_symlink()


def guards():
    if git('branch','--show-current').stdout.decode().strip()!='sol/recut-v1':raise RuntimeError('wrong branch')
    head=git('rev-parse','HEAD').stdout.decode().strip()
    if head!=EXPECTED_HEAD:raise RuntimeError('unexpected starting HEAD')
    if git('diff','--cached','--name-only').stdout.strip():raise RuntimeError('unrelated staged content')
    return head


def prepare():
    head=guards()
    candidates=[str(p.relative_to(ROOT)) for p in BASE.rglob('*') if p.is_file() and p!=MANIFEST]
    candidates.extend(EXPLICIT)
    excluded=ignored(candidates)
    paths=sorted(set(candidates)-excluded)
    if any(not allowed(p) for p in paths):raise RuntimeError('path escapes T6a scope')
    manifest=dict(schema='t6a-guarded-commit-1',base_HEAD=head,branch='sol/recut-v1',
        files=[dict(path=p,sha256=digest(ROOT/p)) for p in paths],
        ignored_paths_excluded=len(excluded),scope=list(EXPLICIT)+[str(BASE.relative_to(ROOT))+'/**'],
        message='glyphs: add opt-in vertical crop tightening and frozen F2 harm audit')
    MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n')
    print('Prepared',len(paths),'files; excluded',len(excluded),'git-ignored paths')


def validate():
    head=guards();manifest=json.loads(MANIFEST.read_text())
    if head!=manifest['base_HEAD']:raise RuntimeError('source HEAD changed')
    paths=[r['path'] for r in manifest['files']]
    paths.append(str(MANIFEST.relative_to(ROOT)))
    if ignored(paths):raise RuntimeError('manifest contains git-ignored path')
    for row in manifest['files']:
        if not allowed(row['path']) or digest(ROOT/row['path'])!=row['sha256']:
            raise RuntimeError('scope/hash changed: '+row['path'])
    return manifest,paths


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--check-only',action='store_true');args=parser.parse_args()
    if args.prepare:prepare();return
    manifest,paths=validate()
    if args.check_only:
        print('Validated',len(paths),'files; exact HEAD/branch, empty index, no ignored paths');return
    try:
        git('add','--',*paths)
        staged=set(git('diff','--cached','--name-only').stdout.decode().splitlines())
        if staged!=set(paths):raise RuntimeError('staged paths differ from manifest')
        git('diff','--cached','--check')
        result=git('commit','-m',manifest['message'])
        head=git('rev-parse','HEAD').stdout.decode().strip()
        STATUS.write_text(json.dumps(dict(status='committed',commit=head,manifest_sha256=digest(MANIFEST)),indent=2)+'\n')
        print(result.stdout.decode());print(head)
    except subprocess.CalledProcessError as exc:
        message=(exc.stderr or exc.stdout).decode(errors='replace')
        STATUS.write_text(json.dumps(dict(status='commit_blocked',action=exc.cmd,
            reason=message,base_HEAD=manifest['base_HEAD'],manifest_sha256=digest(MANIFEST),
            retry_attempted=False,alternate_index_used=False),indent=2)+'\n')
        print(message,file=sys.stderr);raise SystemExit(exc.returncode)


if __name__=='__main__':main()

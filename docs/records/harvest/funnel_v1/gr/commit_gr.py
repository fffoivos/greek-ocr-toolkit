"""Guarded owner-side commit after the managed worker's index.lock refusal.

Run from the existing worktree in a shell with normal Git metadata write access.
Checks the branch, base HEAD, clean staging area and every handoff file digest.
Never pushes, downloads, or stages bulk media.
"""
from pathlib import Path
import hashlib,json,subprocess,sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
def git(*args,check=True):return subprocess.run(['git',*args],cwd=ROOT,text=True,capture_output=True,check=check)
def main():
    manifest=json.loads((BASE/'receipts/commit-inputs.json').read_text())
    if git('branch','--show-current').stdout.strip()!='sol/funnel-gr':raise SystemExit('Refuse: expected branch sol/funnel-gr')
    if git('rev-parse','HEAD').stdout.strip()!=manifest['base_HEAD']:raise SystemExit('Refuse: base HEAD changed; review/rebuild handoff first')
    if git('diff','--cached','--name-only').stdout.strip():raise SystemExit('Refuse: staging area already contains changes')
    paths=[]
    for r in manifest['files']:
        p=ROOT/r['path']
        if not p.resolve().is_relative_to(BASE.resolve()):raise SystemExit('Refuse: path outside this handoff')
        if '/bulk/' in '/'+r['path'] and p.name!='.gitignore':raise SystemExit('Refuse: bulk payload in commit')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:raise SystemExit('Refuse: changed file '+r['path'])
        paths.append(r['path'])
    paths.append(str((BASE/'receipts/commit-inputs.json').relative_to(ROOT)))
    if '--check-only' in sys.argv:
        print('Validated handoff:',len(paths),'files; branch and base HEAD match; staging area empty')
        return
    git('add','--',*paths)
    staged=set(git('diff','--cached','--name-only').stdout.splitlines())
    if staged!=set(paths):raise SystemExit('Refuse: staged paths differ from validated handoff manifest')
    git('diff','--cached','--check')
    result=git('commit','-m','docs: verify Greek institutional OCR funnels')
    print(result.stdout)
    print(git('rev-parse','HEAD').stdout.strip())

if __name__=='__main__':main()

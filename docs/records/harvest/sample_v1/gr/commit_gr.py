"""Commit the reviewed F2 bundle only, after validating its source-bound manifest."""
from pathlib import Path
import hashlib,json,subprocess,sys
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
def git(*args):return subprocess.run(['git',*args],cwd=ROOT,text=True,capture_output=True,check=True)
def main():
 manifest=json.loads((BASE/'receipts/commit-inputs.json').read_text())
 if git('branch','--show-current').stdout.strip()!='sol/funnel-gr':raise SystemExit('Refuse: branch is not sol/funnel-gr')
 if git('rev-parse','HEAD').stdout.strip()!=manifest['base_HEAD']:raise SystemExit('Refuse: base HEAD changed; rebuild/review handoff first')
 if git('diff','--cached','--name-only').stdout.strip():raise SystemExit('Refuse: staging area is not empty')
 paths=[]
 for r in manifest['files']:
  p=ROOT/r['path']
  if not p.resolve().is_relative_to(BASE.resolve()):raise SystemExit('Refuse: path outside F2 output')
  if any(x in p.relative_to(BASE).parts for x in ['bulk','cache','blind_pages','contact_sheets','crops','docai','parsed']):raise SystemExit('Refuse: bulk/image/provider response path')
  if p.suffix.lower() in ['.jpg','.png','.pdf','.jpeg','.tif','.tiff']:raise SystemExit('Refuse: image/PDF payload')
  if hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:raise SystemExit('Refuse: changed handoff file '+r['path'])
  paths.append(r['path'])
 paths.append(str((BASE/'receipts/commit-inputs.json').relative_to(ROOT)))
 if '--check-only' in sys.argv:print('Validated',len(paths),'files; correct branch/base HEAD and empty staging area');return
 pathspec=BASE/'bulk/commit-paths.nul';pathspec.parent.mkdir(exist_ok=True);pathspec.write_bytes(b''.join(p.encode()+b'\0' for p in paths))
 git('add','--pathspec-from-file='+str(pathspec),'--pathspec-file-nul')
 if set(git('diff','--cached','--name-only').stdout.splitlines())!=set(paths):raise SystemExit('Refuse: staged paths differ from reviewed file manifest')
 git('diff','--cached','--check')
 print(git('commit','-m','docs: sample Greek scan sources and audit Document AI yield').stdout)
 print(git('rev-parse','HEAD').stdout.strip())
if __name__=='__main__':main()

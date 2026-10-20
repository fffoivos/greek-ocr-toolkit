"""Review/stage only this exact gallery; refuses unrelated staged paths or drift."""
import argparse, hashlib, json, subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--commit',action='store_true');a=p.parse_args()
out=Path(__file__).resolve().parent;root=out.parents[3];prefix=str(out.relative_to(root))+'/'
m=json.loads((out/'commit-list.json').read_text())
for r in m['files']:
 f=root/r['path'];assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'],f
pngs=list(out.glob('*.png'));assert sum(x.stat().st_size for x in pngs)<6_000_000
staged=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=root).decode().split('\0');assert all(not x or x.startswith(prefix) for x in staged),'Unrelated staged paths'
print(f"Verified {len(m['files'])} bound files and PNG byte cap")
if a.commit:
 paths=[r['path'] for r in m['files']]+[str((out/'commit-list.json').relative_to(root))]
 subprocess.run(['git','add','-f','--',*paths],cwd=root,check=True)
 actual=set(filter(None,subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=root).decode().split('\0')))
 assert actual==set(paths),'Staged set differs from exact gallery list'
 subprocess.run(['git','commit','-m','docs: add SG1 Google segmentation failure gallery','--',*paths],cwd=root,check=True)

"""Read-only repoint check: selected tree diff AND SHA256 for every source blob."""
import argparse,hashlib,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[2];S='3b4090bf9b15d2d2cac53ee55161e936157ec0e5'
def main():
 p=argparse.ArgumentParser();p.add_argument('--revision',required=True);a=p.parse_args()
 entries=[line.split('  ',1) for line in (D/'PROJECTS_SHA256').read_text().splitlines()]
 subprocess.run(['git','-C',str(R),'diff','--quiet',S,a.revision,'--',*[path for h,path in entries]],check=True)
 for expected,path in entries:
  data=subprocess.check_output(['git','-C',str(R),'show',a.revision+':'+path]);actual=hashlib.sha256(data).hexdigest()
  if actual!=expected:raise SystemExit('REBUILD REQUIRED: '+path)
 print('PROJECTS_SHA256 PASS:',len(entries),'source paths at',a.revision)
if __name__=='__main__':main()

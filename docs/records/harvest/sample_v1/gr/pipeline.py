"""Sequential checks/read/audit per completed source; independent source stages."""
from f2lib import *
import subprocess,os
if __name__=='__main__':
 name=sys.argv[1]
 while not (BASE/f'pages_{name}.jsonl').exists():time.sleep(5)
 for stage in ['machine','read','analyse']:
  logfile=BASE/f'{stage}-{name}-pipeline.log'
  with logfile.open('w') as log:
   p=subprocess.run([sys.executable,str(BASE/'process.py'),stage,name],stdout=log,stderr=subprocess.STDOUT,cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT),'OMP_THREAD_LIMIT':'1'})
  if p.returncode:raise RuntimeError(stage+' failed; see '+str(logfile))
  print(name,stage,'complete',flush=True)
 write(BASE/'receipts'/f'pipeline-{name}.json',dict(source=name,finished_at=stamp(),pages_manifest_sha256=sha(BASE/f'pages_{name}.jsonl')))

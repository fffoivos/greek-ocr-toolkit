"""Wait for corrected catalogue frame, then run its sample and P1 stages."""
from f2lib import *
import subprocess,os
if __name__=='__main__':
 while True:
  p=BASE/'receipts/census-elstat.json';d=json.loads(p.read_text()) if p.exists() else {}
  if '/Mag/' in d.get('method','') and d.get('N',0)>68:break
  time.sleep(5)
 for script,args in [('sample.py',['elstat']),('pipeline.py',['elstat'])]:
  with (BASE/('corrected-'+script+'.log')).open('w') as log:
   result=subprocess.run([sys.executable,str(BASE/script),*args],cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT)},stdout=log,stderr=subprocess.STDOUT)
  if result.returncode:raise RuntimeError(script+' failed')
 print('corrected ELSTAT sample and pipeline complete',flush=True)

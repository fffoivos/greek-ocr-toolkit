"""Bounded Phase 0 page launcher; each page gets a fresh offline process."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import time

p=argparse.ArgumentParser()
p.add_argument('--adapter',type=Path,required=True)
p.add_argument('--code',type=Path,required=True)
p.add_argument('--harvest',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
p.add_argument('--workers',type=int,default=2)
a=p.parse_args()
assert 1<=a.workers<=3
pages=json.loads((a.out/'selection.json').read_text())
for name in ('pages','page-lines','crops','logs','tmp'):
    (a.out/name).mkdir(exist_ok=False)
start=time.monotonic()


def worker(i):
    with (a.out/'logs'/f'{i:04d}.log').open('xb') as log:
        r=subprocess.run(['nice','-n','15',sys.executable,'-B',str(a.adapter),'--code',str(a.code),
                          '--harvest',str(a.harvest),'--out',str(a.out),'--worker',str(i)],
                         stdout=log,stderr=subprocess.STDOUT)
    return dict(page=i,exit_code=r.returncode)


with ThreadPoolExecutor(max_workers=a.workers) as pool:
    results=list(pool.map(worker,range(len(pages))))
summary=dict(pages=len(pages),crops=sum(len(p['lines']) for p in pages),workers=a.workers,
             wall_seconds=time.monotonic()-start,results=results,ok=all(r['exit_code']==0 for r in results))
(a.out/'execution.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary),flush=True)
sys.exit(0 if summary['ok'] else 1)

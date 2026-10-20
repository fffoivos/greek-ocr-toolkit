"""Read/hash existing native crops. Writes only the requested R2 evidence file."""
import argparse
import hashlib
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')

def probe(r):
    if r['pool']=='W1':return dict(line_id=r['line_id'],found=None)
    tail=r['crop'].split('docs/harvest/harvest_big/',1)[1].replace('/crops/','/',1)
    candidates=[ROOT/'collection_v2/crops'/tail,ROOT/'greek-ocr-toolkit'/r['crop']]
    for p in candidates:
        if p.is_file():
            h=hashlib.sha256(p.read_bytes()).hexdigest()
            if h==r['sha256']:return dict(line_id=r['line_id'],found=str(p),sha256=h)
    return dict(line_id=r['line_id'],found=None)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('inventory');ap.add_argument('out');a=ap.parse_args()
    records=[json.loads(x) for x in Path(a.inventory).read_text().splitlines()]
    with ThreadPoolExecutor(8) as pool:result=list(pool.map(probe,records))
    Path(a.out).write_text(''.join(json.dumps(r)+'\n' for r in result))
    print(json.dumps(dict(lines=len(result),found=sum(bool(r['found']) for r in result))))

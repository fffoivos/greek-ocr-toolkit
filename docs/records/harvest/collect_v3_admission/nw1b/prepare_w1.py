"""Offline, page-resumable W1 measurements after the owner calibration gate."""
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',PYTHONDONTWRITEBYTECODE='1')
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
import json
from concurrent.futures import ProcessPoolExecutor
from greekocr.harvest.neighbour_words import page_measurements
from calibrate import require_qualification
BASE=Path(__file__).resolve().parent

def offline(event,args):
    if event in ('socket.connect','socket.getaddrinfo','socket.bind','socket.sendto'):
        raise PermissionError('NW1b network OFF')
sys.addaudithook(offline)

def worker(rows):
    page_measurements(rows)
    return rows[0]['page_id']

def main():
    require_qualification(BASE/'calibration.json')
    prior=json.loads((BASE/'w1_before.json').read_text())
    groups={}
    with Path(prior['receipt']['input_path']).open() as stream:
        for line in stream:
            row=json.loads(line);groups.setdefault(row['page_id'],[]).append(row)
    with ProcessPoolExecutor(max_workers=3) as pool:
        for i,page in enumerate(pool.map(worker,groups.values()),1):
            print(f'{i}/{len(groups)} W1 pages; {page}',flush=True)


if __name__ == '__main__':
    main()

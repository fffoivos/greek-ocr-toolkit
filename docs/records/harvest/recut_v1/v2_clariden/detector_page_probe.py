"""One-page default T6c2 detector run, offline and without optional model paths."""
import os
import sys
sys.dont_write_bytecode = True
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[name] = '1'
os.environ['HF_HUB_OFFLINE'] = os.environ['TRANSFORMERS_OFFLINE'] = '1'

import argparse
import hashlib
import json
from pathlib import Path
import resource
import socket
import time

p = argparse.ArgumentParser()
p.add_argument('--code', type=Path, required=True)
p.add_argument('--page', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
a.out.mkdir(parents=True, exist_ok=False)


def audit(event, values):
    if event in ('socket.connect', 'socket.getaddrinfo', 'socket.bind', 'socket.sendto'):
        raise PermissionError('T6f detector network OFF')
    if event == 'open' and values[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
        if not isinstance(values[0], int) and os.fsdecode(values[0]) != os.devnull:
            assert Path(os.fsdecode(values[0])).resolve().is_relative_to(a.out.resolve()), values[0]


sys.addaudithook(audit)
sys.path.insert(0, str(a.code))
import cv2
cv2.setNumThreads(0)
from PIL import Image
from greekocr.pages import process_page

t = time.monotonic()
with Image.open(a.page) as opened:
    native = opened.copy()
analysis = process_page(native)
rows = json.dumps(analysis.rows, sort_keys=True, allow_nan=False, separators=(',', ':')).encode()
(a.out / 'rows.json').write_bytes(rows)
r = dict(host=socket.gethostname(), code_tree_sha='63c640a3aa4abe08d200258cf24d235dfa4a1625',
         page_sha256=hashlib.sha256(a.page.read_bytes()).hexdigest(), rows_sha256=hashlib.sha256(rows).hexdigest(),
         rows=len(analysis.rows), seconds=time.monotonic()-t, nice=os.getpriority(os.PRIO_PROCESS,0),
         peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024))
(a.out / 'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))

"""Run a CN1 measurement entry point with network and recognizer guards."""
import json
import os
from pathlib import Path
import runpy
import socket
import sys
import time
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[key]='1'
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',PYTHONDONTWRITEBYTECODE='1')
from greekocr.labelfix.ctc_align import Recognizer
calls=[]
def forbidden(*args,**kwargs):
    calls.append('network_or_recognizer')
    raise RuntimeError('CN1 forbids network access and recognizer inference')
socket.socket.connect=forbidden
socket.socket.connect_ex=forbidden
socket.create_connection=forbidden
Recognizer.__init__=forbidden
Recognizer.align_batch=forbidden
Recognizer.align_paths=forbidden
receipt=Path(sys.argv[1]); module=sys.argv[2]; args=sys.argv[3:]
sys.argv=[module]+args
started=time.monotonic()
try:
    runpy.run_module(module,run_name='__main__')
finally:
    receipt.write_text(json.dumps(dict(module=module,arguments=args,elapsed_seconds=time.monotonic()-started,forbidden_calls=calls,network_connect_guard=True,recognizer_guard=True),ensure_ascii=False,indent=2)+'\n')

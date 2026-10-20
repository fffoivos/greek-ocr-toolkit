"""Offline import gate; writes only its named receipt below the T6f workdir."""
import os
import sys
sys.dont_write_bytecode = True
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
os.environ['HF_HUB_OFFLINE'] = os.environ['TRANSFORMERS_OFFLINE'] = '1'

import argparse
import hashlib
import importlib
import importlib.metadata
import json
from pathlib import Path
import platform
import socket
import traceback

W = Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/recut_1d_20261017')
p = argparse.ArgumentParser()
p.add_argument('--code', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
args = p.parse_args()
assert args.out.resolve().is_relative_to(W) and args.code.resolve().is_relative_to(W)


def audit(event, values):
    if event in ('socket.connect', 'socket.getaddrinfo', 'socket.bind', 'socket.sendto'):
        raise PermissionError('T6f detector network OFF')
    if event == 'open' and values[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
        if not isinstance(values[0], int) and os.fsdecode(values[0]) != os.devnull:
            assert Path(os.fsdecode(values[0])).resolve().is_relative_to(W), values[0]


sys.addaudithook(audit)
sys.path.insert(0, str(args.code))
result = dict(host=socket.gethostname(), architecture=platform.machine(), python=sys.version,
              executable=sys.executable, code_tree_sha='63c640a3aa4abe08d200258cf24d235dfa4a1625',
              nice=os.getpriority(os.PRIO_PROCESS, 0), packages={}, imports={}, model_files=[])
result['lock'] = sorted((d.metadata['Name'], d.version) for d in importlib.metadata.distributions())
for module in ('numpy', 'PIL', 'scipy', 'cv2', 'greekocr.pages', 'greekocr.glyphs.foreign_ink'):
    try:
        m = importlib.import_module(module)
        result['imports'][module] = dict(ok=True, file=m.__file__, version=getattr(m, '__version__', None))
    except Exception as exc:
        result['imports'][module] = dict(ok=False, error=repr(exc), traceback=traceback.format_exc())
for package in ('numpy', 'Pillow', 'scipy', 'opencv-python-headless', 'opencv-python'):
    try:
        d = importlib.metadata.distribution(package)
        record = d.read_text('RECORD')
        result['packages'][package] = dict(version=d.version,
            RECORD_sha256=hashlib.sha256(record.encode()).hexdigest() if record else None)
    except importlib.metadata.PackageNotFoundError:
        result['packages'][package] = None
result['source_files'] = []
for name, module in sorted(sys.modules.items()):
    file = getattr(module, '__file__', None)
    if name.startswith('greekocr') and file:
        path = Path(file)
        assert path.resolve().is_relative_to(args.code.resolve()), str(path)
        result['source_files'].append(dict(module=name, path=str(path.relative_to(args.code)),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
result['ok'] = all(r['ok'] for r in result['imports'].values())
args.out.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
sys.exit(0 if result['ok'] else 1)

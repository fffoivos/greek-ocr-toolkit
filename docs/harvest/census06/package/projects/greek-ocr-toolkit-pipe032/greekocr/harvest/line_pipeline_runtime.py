"""Bind the loaded native software, including the crop-producing PNG codec."""
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys


THREAD_KEYS = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')


def file_identity(path):
    path = Path(path).resolve(strict=True)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return dict(path=str(path), sha256=h.hexdigest())


def capture(executables):
    from PIL import Image, features
    import cv2
    import scipy.ndimage
    cv2.setNumThreads(0)
    modules = [importlib.import_module(name) for name in
        ('PIL._imaging', 'numpy._core._multiarray_umath', 'scipy.ndimage._nd_image')]
    compiled = [file_identity(module.__file__) for module in modules]
    compiled.extend(file_identity(p) for p in sorted(Path(cv2.__file__).parent.glob('*.so')))
    preload = [file_identity(p) for p in os.environ.get('LD_PRELOAD', '').replace(':', ' ').split()]
    loaded = set()
    if Path('/proc/self/maps').is_file():
        for line in Path('/proc/self/maps').read_text().splitlines():
            path = line.split()[-1]
            if path.startswith('/') and Path(path).name.startswith(('libz.so', 'libjpeg', 'libpng')):
                loaded.add(path)
    return dict(schema='ocr-native-runtime-v1', python=platform.python_version(), architecture=platform.machine(),
        python_binary=file_identity(sys.executable), executables={k:file_identity(v) for k,v in sorted(executables.items())},
        packages={n:importlib.metadata.version(n) for n in ('numpy','Pillow','scipy','opencv-python-headless')},
        codecs={name:features.version(name) for name in ('zlib','libjpeg_turbo','zlib_ng')},
        compiled_modules=compiled, loaded_codecs=[file_identity(p) for p in sorted(loaded)], preload=preload,
        threads={key:os.environ.get(key) for key in THREAD_KEYS}, opencv_threads=cv2.getNumThreads())


def validate(path, executables=None):
    expected = json.loads(Path(path).read_text())
    actual = capture(executables if executables is not None else {k:v['path'] for k,v in expected['executables'].items()})
    if actual != expected:
        changed = sorted(k for k in set(actual)|set(expected) if actual.get(k)!=expected.get(k))
        raise ValueError('native runtime changed: '+', '.join(changed))
    if any(v!='1' for v in actual['threads'].values()) or actual['opencv_threads']!=1:
        raise ValueError('native runtime requires single-threaded child libraries')
    return file_identity(path)['sha256']

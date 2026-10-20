"""T6f2 environment-only retry: copy venv_l1, pin numpy, verify all other bytes.

Run on Clariden via SSH. All writes, pip downloads and temporary files stay in W.
The frozen masking adapter and its imports are never edited by this helper.
"""
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import time

E = Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
W = E / 'recut_1d_20261017'
SOURCE = E / 'venv_l1'
COPY = W / 'venv_np246'
R = W / 't6f2'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def snapshot(root):
    rows = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            p = Path(directory) / name
            key = str(p.relative_to(root))
            if p.is_symlink():
                rows[key] = {'link': os.readlink(p)}
            elif p.is_file():
                rows[key] = {'sha256': sha(p), 'bytes': p.stat().st_size}
    return rows


def fingerprint(rows):
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def numpy_path(key):
    return key.startswith(('lib/python3.12/site-packages/numpy/',
                           'lib/python3.12/site-packages/numpy.libs/',
                           'lib/python3.12/site-packages/numpy-')) or key in ('bin/f2py', 'bin/numpy-config')


def main():
    assert W.is_dir() and SOURCE.is_dir() and not COPY.exists()
    R.mkdir(exist_ok=True)
    (R / 'tmp').mkdir(exist_ok=True)
    wheel_dir = R / 'wheels'
    wheel_dir.mkdir(exist_ok=False)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(R / 'tmp'),
               PIP_DISABLE_PIP_VERSION_CHECK='1', PIP_NO_CACHE_DIR='1',
               OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')

    def run(argv, log):
        print(json.dumps({'command': [str(x) for x in argv], 'host': socket.gethostname()}), flush=True)
        result = subprocess.run([str(x) for x in argv], env=env, capture_output=True)
        (R / log).write_bytes(result.stdout + result.stderr)
        if result.returncode:
            print((result.stdout + result.stderr).decode(errors='replace'), flush=True)
        result.check_returncode()
        return result.stdout

    started = time.time()
    before = snapshot(SOURCE)
    print('Shared venv fingerprint: ' + fingerprint(before), flush=True)
    source_lock = run([SOURCE / 'bin/python', '-B', '-m', 'pip', 'freeze'], 'source_freeze.log')
    (R / 'venv_l1.before.lock').write_bytes(source_lock)
    run(['cp', '-a', '--reflink=auto', SOURCE, COPY], 'copy.log')
    copied = snapshot(COPY)
    assert copied == before, 'venv copy differs before install'
    assert all('link' not in v or not v['link'].startswith(str(SOURCE)) for v in copied.values())
    identity = run([COPY / 'bin/python', '-B', '-c',
                    'import sys,json;print(json.dumps(dict(prefix=sys.prefix,executable=sys.executable)))'],
                   'copy_identity.json')
    assert json.loads(identity)['prefix'] == str(COPY)
    run([COPY / 'bin/python', '-B', '-m', 'pip', 'download', '--no-cache-dir',
         '--only-binary=:all:', '--no-deps', '--dest', wheel_dir, 'numpy==2.4.6'], 'wheel_download.log')
    wheels = list(wheel_dir.glob('numpy-2.4.6-*.whl'))
    assert len(wheels) == 1
    wheel = wheels[0]
    wheel_hash = sha(wheel)
    (W / 'numpy_np246_wheel.sha256').write_text(wheel_hash + '  ' + str(wheel.relative_to(W)) + '\n')
    run([COPY / 'bin/python', '-B', '-m', 'pip', 'install', '--no-cache-dir', '--no-index',
         '--no-deps', '--force-reinstall', wheel], 'wheel_install.log')
    lock = run([COPY / 'bin/python', '-B', '-m', 'pip', 'freeze'], 'copy_freeze.log')
    (W / 'venv_np246.lock').write_bytes(lock)
    assert set(source_lock.decode().splitlines()) - set(lock.decode().splitlines()) == {'numpy==2.5.4'}
    assert set(lock.decode().splitlines()) - set(source_lock.decode().splitlines()) == {'numpy==2.4.6'}
    pinned = snapshot(COPY)
    different = [k for k in sorted(before.keys() | pinned.keys()) if before.get(k) != pinned.get(k)]
    assert different and all(numpy_path(k) for k in different), different
    shared_after = snapshot(SOURCE)
    assert shared_after == before, 'shared venv changed'
    after_lock = run([SOURCE / 'bin/python', '-B', '-m', 'pip', 'freeze'], 'source_after_freeze.log')
    assert after_lock == source_lock
    (R / 'venv_l1.after.lock').write_bytes(after_lock)
    imports = json.loads(run([COPY / 'bin/python', '-B', '-c',
        'import sys,json,numpy,PIL,scipy,cv2;from PIL import features;'
        'print(json.dumps(dict(prefix=sys.prefix,numpy=numpy.__version__,numpy_file=numpy.__file__,'
        'pillow=PIL.__version__,scipy=scipy.__version__,cv2=cv2.__version__,'
        'pillow_zlib=features.version_codec("zlib"))))'], 'pinned_imports.json'))
    assert imports['numpy'] == '2.4.6' and imports['numpy_file'].startswith(str(COPY) + '/')
    receipt = dict(schema='t6f2-verified-venv-copy-1', ok=True, host=socket.gethostname(),
        source=str(SOURCE), copy=str(COPY), numpy_pin='2.4.6', imports=imports,
        source_files=len(before), source_bytes=sum(x.get('bytes', 0) for x in before.values()),
        shared_before_sha256=fingerprint(before), shared_after_sha256=fingerprint(shared_after),
        copy_before_sha256=fingerprint(copied), copy_after_sha256=fingerprint(pinned),
        non_numpy_changed=[], numpy_changed_paths=different,
        source_lock_sha256=sha(R / 'venv_l1.before.lock'), lock_sha256=sha(W / 'venv_np246.lock'),
        wheel=str(wheel), wheel_sha256=wheel_hash, copy_uses_no_shared_venv_links=True,
        shared_venv_unchanged=True, elapsed_seconds=time.time()-started)
    (R / 'venv_verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'numpy_changed_paths'}), flush=True)


if __name__ == '__main__':
    main()

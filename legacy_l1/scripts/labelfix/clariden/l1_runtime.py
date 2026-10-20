"""Provision/verify the coordinator-authorised isolated L1 runtime; never submit."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def file_list(root):
    """Bind sorted names, modes, sizes, mtimes and symlink targets, without writes."""
    records = []
    for p in sorted(root.rglob('*')):
        s = p.lstat()
        records.append([str(p.relative_to(root)), s.st_mode, s.st_size, s.st_mtime_ns,
                        os.readlink(p) if p.is_symlink() else None])
    return ''.join(json.dumps(r, separators=(',', ':')) + '\n' for r in records)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--verify', action='store_true')
    a = ap.parse_args()
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    source, target = a.root / 'venv', a.root / 'venv_l1'
    receipt_path = a.out / 'L1_runtime_receipt.json'
    if a.verify:
        receipt = json.loads(receipt_path.read_text())
        assert hashlib.sha256(file_list(source).encode()).hexdigest() == receipt['e3_file_list_before_sha256'], 'E3 venv file list changed'
        for line in (a.out / 'L1_scipy_SHA256.txt').read_text().splitlines():
            sha, name = line.split('  ', 1)
            assert digest(target / name) == sha, 'SciPy changed: ' + name
        print('L1_RUNTIME_VERIFIED', flush=True)
        return
    a.out.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise SystemExit('STOP: venv_l1 already exists; do not overwrite it')
    before = file_list(source)
    (a.out / 'L1_E3_file_list_before.jsonl').write_text(before)
    started = time.monotonic()
    subprocess.run(['cp', '-a', str(source), str(target)], check=True)
    # cp creates independent regular files; never follow a symlink while patching.
    for p in [target / 'pyvenv.cfg', *(target / 'bin').iterdir()]:
        if p.is_symlink() or not p.is_file() or p.stat().st_size > 1024 * 1024:
            continue
        data = p.read_bytes()
        if b'\0' not in data and str(source).encode() in data:
            p.write_bytes(data.replace(str(source).encode(), str(target).encode()))
    python = str(target / 'bin/python')
    result = subprocess.run([python, '-m', 'pip', 'install', '--no-deps', 'scipy==1.17.1'],
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (a.out / 'L1_pip_install.log').write_text(result.stdout)
    print(result.stdout, flush=True)
    after = file_list(source)
    (a.out / 'L1_E3_file_list_after.jsonl').write_text(after)
    unchanged = before == after
    assert unchanged, 'STOP: E3 venv file list changed'
    if result.returncode:
        raise SystemExit('STOP: pinned pip install failed; no proxy, alternate index or retry')
    info = subprocess.check_output([python, '-c',
        'import json,sys,scipy,scipy.ndimage,torch,numpy,PIL; '
        'print(json.dumps(dict(base_interpreter=sys._base_executable,executable=sys.executable,'
        'prefix=sys.prefix,scipy=scipy.__version__,torch=torch.__version__,numpy=numpy.__version__,'
        'pillow=PIL.__version__,scipy_path=scipy.__path__[0])))'], text=True)
    info = json.loads(info)
    assert info['scipy'] == '1.17.1' and info['prefix'] == str(target)
    freeze = subprocess.check_output([python, '-m', 'pip', 'freeze'], text=True)
    (a.out / 'L1_pip_freeze.txt').write_text(freeze)
    scipy_files = sorted(p for p in Path(info['scipy_path']).rglob('*') if p.is_file())
    manifest = ''.join(f'{digest(p)}  {p.relative_to(target)}\n' for p in scipy_files)
    # Bind bundled numerical libraries and distribution metadata too.
    site = Path(info['scipy_path']).parent
    for extra in [site / 'scipy.libs', site / 'scipy-1.17.1.dist-info']:
        for p in sorted(extra.rglob('*')):
            if p.is_file():
                manifest += f'{digest(p)}  {p.relative_to(target)}\n'
    (a.out / 'L1_scipy_SHA256.txt').write_text(manifest)
    receipt = dict(schema='l1-runtime-v1', source_venv=str(source), venv=str(target), **info,
        pip_freeze=freeze.splitlines(), installed_only=['scipy==1.17.1'], pip_no_deps=True,
        e3_file_list_definition='sorted relative name, lstat mode, size, mtime_ns, symlink target',
        e3_file_list_before_sha256=hashlib.sha256(before.encode()).hexdigest(),
        e3_file_list_after_sha256=hashlib.sha256(after.encode()).hexdigest(), e3_venv_unchanged=unchanged,
        scipy_manifest_sha256=digest(a.out / 'L1_scipy_SHA256.txt'), scipy_files=len(scipy_files),
        elapsed_seconds=time.monotonic()-started,
        step_runtime='alignment, detector, R1 and composition all use venv_l1; E3 venv never modified')
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()

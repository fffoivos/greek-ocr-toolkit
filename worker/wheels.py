#!/usr/bin/env python3
"""Seal/verify the pre-staged Linux wheelhouse; no package-index access."""
import argparse,hashlib,json,sys
from pathlib import Path
try:
    from packaging.utils import parse_wheel_filename,canonicalize_name
    from packaging.tags import sys_tags
except ImportError:
    from pip._vendor.packaging.utils import parse_wheel_filename,canonicalize_name
    from pip._vendor.packaging.tags import sys_tags
ROOT=Path(__file__).resolve().parent

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(root,seal=False):
    root=Path(root);lock=ROOT/'requirements.lock'
    pins=dict(line.strip().split('==') for line in lock.read_text().splitlines() if line and not line.startswith('#'))
    wheels=sorted(root.glob('*.whl'));found={};tags=set(sys_tags())
    for path in wheels:
        if path.is_symlink():raise ValueError('symlink wheel refused')
        name,version,_,wtags=parse_wheel_filename(path.name);name=canonicalize_name(name)
        if name not in pins or str(version)!=pins[name] or not wtags & tags:raise ValueError('unlocked/incompatible wheel: '+path.name)
        if name in found:raise ValueError('duplicate wheel: '+name)
        found[name]=path
    if set(found)!=set(pins):raise ValueError('missing pinned target wheels: '+', '.join(sorted(set(pins)-set(found))))
    receipt=dict(lock_sha256=digest(lock),sha256={p.name:digest(p) for p in wheels})
    manifest=root/'SHA256.json'
    if seal:manifest.write_text(json.dumps(receipt,indent=2)+'\n')
    elif not manifest.exists() or json.loads(manifest.read_text())!=receipt:raise ValueError('wheelhouse checksum/lock mismatch; seal verified target artifacts first')
    return len(wheels)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seal',action='store_true');p.add_argument('root',nargs='?',default=str(ROOT/'wheelhouse'));a=p.parse_args()
    try:print('verified wheels:',verify(a.root,a.seal))
    except Exception as e:print(str(e),file=sys.stderr);sys.exit(1)

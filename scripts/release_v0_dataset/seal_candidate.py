#!/usr/bin/env python3
"""Seal candidate C before drilling. Self-inventory is deliberately excluded."""
import argparse
import json
from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = 'scripts.release_v0_dataset'
from .common import CAP, atomic_json, info, safe_path, verify_file


def inventory(root):
    root = Path(root).resolve()
    paths = sorted(root.rglob('*'))
    if any(p.is_symlink() for p in paths):
        raise ValueError('candidate contains symlink')
    files = [info(p, root) for p in paths if p.is_file() and p.relative_to(root).as_posix() != 'C_MANIFEST.json']
    if any(e['bytes'] > CAP for e in files):
        raise ValueError('closed candidate file exceeds cap')
    if any(e['path'].endswith('.partial') for e in files):
        raise ValueError('candidate contains partial file')
    return files


def verify(root):
    root = Path(root).resolve()
    manifest = json.loads((root / 'C_MANIFEST.json').read_text())
    if manifest['files'] != inventory(root):
        raise ValueError('sealed candidate C changed')
    return manifest


def seal(root):
    root = Path(root).resolve()
    path = root / 'C_MANIFEST.json'
    if path.exists():
        return verify(root)
    manifest = {'schema': 'sealed-candidate-C-v1', 'files': inventory(root)}
    atomic_json(path, manifest)
    return manifest


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('--verify', action='store_true')
    args = p.parse_args(argv)
    value = verify(args.root) if args.verify else seal(args.root)
    print(json.dumps({'sealed': True, 'files': len(value['files'])}))
    return 0


if __name__ == '__main__':
    sys.exit(main())

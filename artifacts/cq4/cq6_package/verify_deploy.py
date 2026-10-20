"""Verify staged bytes without mutation; status admission is a separate strict gate."""
import argparse
import hashlib
import json
from pathlib import Path

def verify(root):
    expected=[]
    for line in (root/'DEPLOY_SHA256.txt').read_text().splitlines():
        digest, rel=line.split('  ',1)
        p=Path(rel)
        if p.is_absolute() or '..' in p.parts:
            raise ValueError('unsafe deploy path')
        if not (root/p).resolve().is_relative_to(root.resolve()):
            raise ValueError('deploy symlink escapes package')
        if hashlib.sha256((root/p).read_bytes()).hexdigest()!=digest:
            raise ValueError('hash mismatch: '+rel)
        expected.append(rel)
    if expected!=(root/'DEPLOY_FILES.txt').read_text().splitlines():
        raise ValueError('deploy list/hash list mismatch')
    actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()
            and p.name not in ('DEPLOY_FILES.txt','DEPLOY_SHA256.txt') and '__pycache__' not in p.parts}
    if actual!=set(expected):
        raise ValueError('unlisted or missing package files')
    return len(expected)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    ap.add_argument('--require-ready',action='store_true')
    args=ap.parse_args()
    n=verify(args.root)
    print(f'HASH_CLOSURE_PASS {n} files')
    r=json.loads((args.root/'assembly_receipt.json').read_text())
    if args.require_ready:
        if r['status']!='ready' or not r['training_ready'] or not r['deployable']:
            raise SystemExit('STOP: '+r['reason'])
        if r['capital_slice']!={'negative':800,'positive':500}:
            raise SystemExit('STOP: exact capital quota unmet')
    print('STATUS '+r['status'])

if __name__=='__main__':
    main()

#!/usr/bin/env python3
"""Read-only checks; inputs mode never hashes or parses multi-GB inputs."""
import argparse
import ast
import json
from pathlib import Path
import subprocess
import build_release_v3 as b


def package(root):
    expected=[]
    for line in (root/'DEPLOY_SHA256SUMS').read_text().splitlines():
        h,n=line.split('  ',1)
        p=Path(n)
        b.require(not p.is_absolute() and '..' not in p.parts,'unsafe package path')
        b.require((root/p).is_file() and b.sha(root/p)==h,'package sha mismatch: '+n)
        expected.append(n)
    b.require(expected==(root/'DEPLOY_PATHS.txt').read_text().splitlines(),'deploy lists disagree')
    for p in root.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    for n in ('VERIFY.sh','submit_release_v3.sh','release_v3.sbatch'):
        subprocess.run(['bash','-n',str(root/n)],check=True)
    print(b.canonical(dict(mode='package',status='ok',files=len(expected))))


def inputs(config):
    root,cfg=b.load_config(config)
    for item in cfg['inputs']:
        if item['kind']=='small':
            b.require(b.resolve(root,item['path']).stat().st_size < 64*1024*1024,'small input exceeds light-check limit')
    _,receipts,pending=b.input_check(root,cfg,light=True)
    result=dict(mode='inputs',status='pending' if pending else 'ok',ready=len(receipts),total=len(cfg['inputs'])+len(cfg['crops']),pending=pending,checks=receipts,
                large_input_policy='existence and size only; batch builder hashes full files')
    print(b.canonical(result))
    return 2 if pending else 0


def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['package','inputs']);p.add_argument('--config',type=Path)
    a=p.parse_args();root=Path(__file__).resolve().parent
    if a.mode=='package':package(root);return 0
    return inputs(a.config or root/'INPUTS.json')

if __name__=='__main__':raise SystemExit(main())

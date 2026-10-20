#!/usr/bin/env python3
"""Copy only hash-bound portable planning inputs to a fresh/resumable run root."""
import shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collect_v3.common import read_json,sha
from worker.runtime import ROOT,settings

def prepare(out):
    out=Path(out).resolve();source=ROOT/'docs/harvest/collect_v3'
    if out==source or out.is_relative_to(ROOT/'worker/fixtures'):raise ValueError('separate production output root required')
    for name,digest in read_json(ROOT/'worker/planned_inputs.json')['sha256'].items():
        src=source/name;dst=out/name
        if src.is_symlink() or sha(src)!=digest:raise ValueError('shipped planning input changed: '+name)
        if dst.exists():
            if dst.is_symlink() or sha(dst)!=digest:raise ValueError('run planning input changed; preserve it: '+name)
        else:
            dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    return out

if __name__=='__main__':print('planning inputs ready:',prepare(settings()['output_root']))

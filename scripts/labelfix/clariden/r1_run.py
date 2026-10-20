"""Exact shared mock/Slurm entry point. This program NEVER submits jobs."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from scripts.labelfix.clariden.r1_common import ARMS, SEED, rows, sha256, write_json


def command(script,*args):
    cmd=[sys.executable,'-u',f'scripts/labelfix/clariden/{script}.py',*map(str,args)]
    print('ENTRYPOINT '+json.dumps(cmd),flush=True)
    subprocess.run(cmd,check=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mock',action='store_true');ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--crop-root',type=Path,required=True);ap.add_argument('--layout',default='e3',choices=['e3','toolkit'])
    ap.add_argument('--selection',type=Path,default=Path('.cache/labelfix/clariden/C1_selection.jsonl'))
    ap.add_argument('--alignments',type=Path,default=Path('.cache/labelfix/clariden/C1_alignments.jsonl.gz'))
    ap.add_argument('--binding',type=Path,default=Path('artifacts/labelfix_r1/binding'))
    ap.add_argument('--heldout',type=Path,default=Path('artifacts/labelfix_r1/heldout_font'))
    ap.add_argument('--owner-alignments',type=Path,default=Path('.cache/labelfix/align_s0.jsonl'))
    ap.add_argument('--epochs',type=int,default=15);ap.add_argument('--workers',type=int,default=16)
    ap.add_argument('--source-commit',default='TRACK_LEAD_FILL_SOURCE_COMMIT')
    ap.add_argument('--seed',type=int,default=SEED);ap.add_argument('--sampler-seed',type=int,default=SEED)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    selected=a.binding/'mock_selection.jsonl' if a.mock else a.selection
    if a.mock and len(list(rows(selected)))!=192:raise ValueError('mock requires exactly 192 C1 crops')
    command('r1_extract','--selection',selected,'--full-selection',a.selection,'--alignments',a.alignments,
            '--out',a.out/'data','--crop-root',a.crop_root,'--layout',a.layout,'--mode','c1',
            '--exclusions',a.binding/'exclusions.json','--split-path',a.binding/'document_split.json',
            '--workers',2 if a.mock else a.workers)
    owner=None
    if not a.mock:
        owner=a.out/'owner_extra'
        command('r1_extract','--selection',a.binding/'owner_extra_lines.jsonl.gz','--alignments',a.owner_alignments,
                '--out',owner,'--crop-root',a.crop_root,'--layout',a.layout,'--mode','owner','--workers',a.workers)
    template=['# R1 results (awaiting print-truth scoring)','',
              'No validation or held-out mark quality is claimed by a DONE marker.',
              'Run r1_score.py locally after retrieving predictions and extraction receipts.',
              'Tables: scored slots; all frozen S4 slots with unscored=none; fused; capitals; exact classes; per-book; owner checks.',
              '', '| metric | S4 | S5 | A | B | C | D | E |','|---|---|---|---|---|---|---|---|']
    (a.out/'RESULT.md').write_text('\n'.join(template)+'\n')
    write_json(a.out/'run_binding.json',dict(schema='r1-five-arm-binding-v1',source_commit=a.source_commit,
        parameters=dict(arms=ARMS,epochs=a.epochs,seed=a.seed,sampler_seed=a.sampler_seed,gpu_schedule={'0':['A','E'],'1':['B'],'2':['C'],'3':['D']},
                        mock=a.mock,steps_per_arm=50 if a.mock else None),
        file_sha256={str(p):sha256(p) for p in sorted(Path('scripts/labelfix/clariden').glob('r1_*')) if p.is_file()},
        extraction_receipt_sha256=sha256(a.out/'data/extraction_receipt.json')))
    def cmd(arm,gpu):
        args=[sys.executable,'-u','scripts/labelfix/clariden/r1_train.py','--data',str(a.out/'data'),
              '--heldout',str(a.heldout),'--out',str(a.out/arm),'--arm',arm,'--device','cpu' if a.mock else f'cuda:{gpu}',
              '--epochs',str(a.epochs),'--batch-size','16' if a.mock else '512','--workers','0' if a.mock else '4',
              '--threads','4' if a.mock else '8','--source-commit',a.source_commit,'--seed',str(a.seed),'--sampler-seed',str(a.sampler_seed)]
        if a.mock:args+=['--steps','50']
        if owner:args+=['--owner-extra',str(owner)]
        return args
    if a.mock:
        for arm in ARMS:
            print('TRAIN_ENTRYPOINT '+json.dumps(cmd(arm,0)),flush=True);subprocess.run(cmd(arm,0),check=True)
        command('r1_score','--runs',a.out,'--heldout',a.heldout,'--out',a.out/'score','--mock','--baseline','S4=docs/records/labelfix/spellcheck/S4_lines.jsonl.gz')
    else:
        # All children inherit all four Slurm-allocated GPUs. Each uses one logical GPU.
        children={arm:subprocess.Popen(cmd(arm,gpu)) for arm,gpu in [('A',0),('B',1),('C',2),('D',3)]}
        failures={}
        for arm in ('A','B','C','D'):
            rc=children[arm].wait()
            if rc:failures[arm]=rc
            if arm=='A':children['E']=subprocess.Popen(cmd('E',0))
        rc=children['E'].wait()
        if rc:failures['E']=rc
        if failures:raise RuntimeError('training failures '+json.dumps(failures))
    receipts={arm:json.loads((a.out/arm/'training_receipt.json').read_text()) for arm in ARMS}
    write_json(a.out/'run_receipt.json',dict(mock=a.mock,elapsed_seconds=time.monotonic()-started,arms=receipts))
    print('R1_MOCK_DONE' if a.mock else 'R1_JOB_DONE',flush=True)


if __name__=='__main__':main()

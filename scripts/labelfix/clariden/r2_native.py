"""Extract native manifest windows from the teacher job's recogniser alignments.

Runs inside the R2 Clariden job, or explicitly bounded Mac mock only. No new
alignment, no label agreement gate. Manifest supplies the printed four-head targets.
"""
from pathlib import Path
import os
import time
from scripts.labelfix.clariden.r1_common import rows, write_rows, verify_receipt
from scripts.labelfix.clariden.r1_extract import extract


def native_pool(line_list,teacher_directory,out,crop_root,layout='e3',mock=False):
    if not mock and not os.environ.get('SLURM_JOB_ID'): raise ValueError('native extraction requires Clariden job')
    out=Path(out)
    if (out/'extraction_receipt.json').exists(): return verify_receipt(out)
    if out.exists(): out.rename(out.with_name(out.name+f'.interrupted.{time.time_ns()}'))
    selected=list(rows(line_list))
    if mock and len(selected)>64: raise ValueError('Mac line limit exceeded')
    if any(r['role']!='train' for r in selected): raise ValueError('native supervision contains validation reserve')
    out=Path(out);prep=out.with_name(out.name+'-inputs');prep.mkdir(parents=True,exist_ok=True)
    wanted={r['line_id'] for r in selected};aligned={}
    for p in Path(teacher_directory).glob('chunk-*-alignments.jsonl.gz'):
        for r in rows(p):
            if r['line_id'] in wanted: aligned[r['line_id']]=r
    if set(aligned)!=wanted: raise ValueError('missing teacher recogniser alignment')
    records=[dict(id=r['line_id'],doc=r['doc'],crop=r['crop'],recogniser_text=aligned[r['line_id']]['alignment']['prediction']) for r in selected]
    write_rows(prep/'selection.jsonl',records)
    write_rows(prep/'alignments.jsonl',[dict(crop=r['crop'],alignment=aligned[r['line_id']]['alignment']) for r in selected])
    return extract(prep/'selection.jsonl',prep/'alignments.jsonl',out,crop_root,layout,mode='heldout',workers=1 if mock else 8)

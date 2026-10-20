"""Build production draw contexts without selecting, correcting, or reading lines.

Input JSONL: line_id, source, class, label (corrected draw label), source_crop,
source_sha256. Supply the draw's primary class verbatim; LF1 never chooses it.
"""
import argparse
import json
from pathlib import Path
import random
from build import pack, SEED
from lf1 import BASE, sha, rows, dump

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('draw',type=Path)
    p.add_argument('--output-roster',type=Path)
    p.add_argument('--context-prefix',default='candidate')
    a=p.parse_args()
    # Avoid overwriting the delivered dry-run contexts/keys/manifest roster.
    output=a.output_roster or BASE/'candidate_contexts.json'
    if output.exists():raise FileExistsError('candidate roster already exists')
    bed=rows(a.draw);ids=[r['line_id'] for r in bed]
    if len(set(ids))!=len(ids):raise ValueError('duplicate draw line_id')
    for r in bed:
        for k in ('line_id','source','class','label','source_crop','source_sha256'):
            if not isinstance(r.get(k),str):raise ValueError('missing string field '+k)
        if sha(r['source_crop'])!=r['source_sha256']:raise ValueError('draw crop hash differs')
    pool=json.loads((BASE/'keys/control_pool.json').read_text())
    if set(ids)&{c['source_line_id'] for c in pool}:
        raise ValueError('draw overlaps frozen controls; supply a disjoint control pool (HANDOVER section 4)')
    random.Random(SEED).shuffle(bed)
    # 50+6 preserves the dry-run control fraction and includes all fault controls.
    contexts=[pack(a.context_prefix+str(n//50+1).zfill(5),bed[n:n+50],pool) for n in range(0,len(bed),50)]
    dump(output,contexts)
    dump(BASE/'receipts'/(output.stem+'_build.json') if a.output_roster else BASE/'receipts/candidate_build.json',dict(draw=str(a.draw),draw_sha256=sha(a.draw),
         contexts=contexts,seed=SEED,labels='copied verbatim; no reads',control_pool_sha256=sha(BASE/'keys/control_pool.json')))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Print verified wave-2/S1 path + SHA arguments. No writes or submission."""
import argparse
import json
from pathlib import Path
import build_release_v4 as b


def handoff(receipt):
    receipt=Path(receipt).resolve();r=json.loads(receipt.read_text())
    b.require(r['status']=='ok' and r['counts']['missing_crop_new_admits']==0, 'release not ready')
    args={}
    for n in ('release_v4_admission.jsonl','corrections_registry.json','release_v4_sf7_edits.jsonl'):
        args[n]=dict(path=str(receipt.parent/n),sha256=r['outputs'][n]['sha256'])
    for n in ('CURRENT.json','summary.json','admission_records','admitted_train'):
        args['census06_'+n]=r['admission_receipt_chain'][n]
    for n,spec in args.items():
        b.require(b.sha(spec['path'])==spec['sha256'], 'handoff SHA mismatch: '+n)
    args['RELEASE_V4_RECEIPT.json']=dict(path=str(receipt),sha256=b.sha(receipt))
    return args


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--receipt',type=Path,required=True)
    print(json.dumps(handoff(p.parse_args().receipt),indent=2,sort_keys=True))

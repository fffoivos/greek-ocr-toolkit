"""Read-only staged-crop inventory verification. No decoding, training or allocation."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import time
from scripts.labelfix.clariden.r1_common import crop_key,crop_path,rows,sha256,write_json


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--selection',type=Path,required=True);ap.add_argument('--inventory',type=Path,required=True)
    ap.add_argument('--crop-root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--extra-selection',type=Path);ap.add_argument('--workers',type=int,default=8)
    a=ap.parse_args();started=time.monotonic()
    selected={crop_key(r['crop']) for r in rows(a.selection)};inventory=list(rows(a.inventory))
    keys=[crop_key(r['crop']) for r in inventory]
    if len(selected)!=91469 or len(set(keys))!=len(keys) or selected!=set(keys):raise ValueError('C1 inventory does not cover exactly the selected 91469 crops')
    def check(r):
        p=crop_path(r['crop'],a.crop_root,'e3')
        if not p.is_file():return dict(crop=r['crop'],error='missing')
        if p.stat().st_size!=r['bytes']:return dict(crop=r['crop'],error='bytes mismatch')
        if sha256(p)!=r['sha256']:return dict(crop=r['crop'],error='sha256 mismatch')
        return None
    with ThreadPoolExecutor(a.workers) as pool:errors=[e for e in pool.map(check,inventory) if e]
    extra=list(rows(a.extra_selection)) if a.extra_selection else []
    missing_extra=[r['crop'] for r in extra if not crop_path(r['crop'],a.crop_root,'e3').is_file()]
    receipt=dict(schema='r1-crop-deployment-v1',selected=len(selected),inventory=len(inventory),
                 present_and_sha256_match=len(inventory)-len(errors),errors=errors,bytes=sum(r['bytes'] for r in inventory),
                 selection_sha256=sha256(a.selection),inventory_sha256=sha256(a.inventory),
                 owner_extra_inference_only=len(extra),owner_extra_missing=missing_extra,
                 image_decodes=0,ctc_forward_passes=0,elapsed_seconds=time.monotonic()-started)
    write_json(a.out,receipt);print(json.dumps(receipt),flush=True)
    if errors or missing_extra:raise ValueError('staged-crop verification failed')


if __name__=='__main__':main()

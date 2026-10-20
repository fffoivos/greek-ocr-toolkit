#!/usr/bin/env python3
"""Explicit selection wrapper around byte-pinned CROPS4 page_job (no originals writes)."""
import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path
import sys
import build_p1pool as p
import materialise_crops as crops4


def run(selection, code, workers=8):
    selection=Path(selection);base=selection.parent
    receipt_path=base/'P1POOL_RECEIPT.json';receipt=json.loads(receipt_path.read_text())
    p.rel4.require(receipt['status']=='selected_pending_crops','selection not pending')
    p.rel4.require(p.rel4.sha(selection)==receipt['output_shas']['selection.jsonl'],'selection sha drift')
    cfgref=receipt['rel4_config'];p.rel4.require(p.rel4.sha(cfgref['path'])==cfgref['sha256'],'REL4 config changed')
    config_root,config=p.rel4.load_config(cfgref['path']);_,_,pending=p.rel4.input_check(config_root,config)
    p.rel4.require(not pending,'production input pending')
    p.rel4.require(Path(code).resolve()==Path(config['crops4c']['context']['census_code']).resolve(),'crop code differs from bound census')
    p.rel4.require(p.rel4.sha(os.environ['CENSUS_MANIFEST'])==config['crops4c']['census_manifest']['sha256'],'census manifest differs from binding')
    p.rel4.require(p.rel4.sha(os.environ['LD_PRELOAD'])==config['crops4c']['context']['codec_preload_sha256'],'PNG runtime drift')
    p.rel4.require(p.rel4.sha(sys.executable)==config['crops4c']['context']['interpreter_sha256'],'interpreter drift')
    module=crops4.load_code(Path(code))
    p.rel4.require(p.rel4.sha(module.__file__)=='e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7','reconstruction module drift')
    root=Path(receipt['crop_root']);work=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
    p.rel4.require(root.parent==work/'p1pool_crops','unsafe crop root')
    p.rel4.require(not root.exists(),'crop attempt must be new')
    root.mkdir(parents=True)
    rows=list(p.rel4.records(selection));groups=defaultdict(list);existing=0;written=0
    for r in rows:
        p.no_labels(r,True);image=Path(r['crop_path'])
        if 'crop_source_image' not in r:
            p.rel4.require(image.is_file() and p.rel4.sha(image)==r['crop_sha256'],'existing crop drift');existing+=1;continue
        p.rel4.require(r['disposition']=='HOLD' and image.is_relative_to(root),'unsafe HOLD destination')
        rr=dict(r,id=r['row_id'],relative_path=str(image.relative_to(root)))
        groups[r['crop_source_image']].append(rr)
    tasks=((page,rr,str(root)) for page,rr in groups.items())
    with ProcessPoolExecutor(max_workers=workers,initializer=crops4.init_worker,initargs=(str(code),)) as pool:
        for results in pool.map(crops4.page_job,tasks,chunksize=1):
            for result in results:
                p.rel4.require(result['state'] in ('written','skipped_valid'),'crop failure: '+str(result))
                written+=result['state']=='written';existing+=result['state']=='skipped_valid'
    manifest=base/'p1pool.jsonl'
    # Exclusive output creation; all paths and bytes checked after worker completion.
    with manifest.open('x') as stream:
        for r in rows:
            image=Path(r['crop_path']);p.rel4.require(image.is_file() and p.rel4.sha(image)==r['crop_sha256'],'final crop mismatch')
            clean={k:v for k,v in r.items() if k not in p.RECON};p.no_labels(clean)
            stream.write(p.rel4.canonical(clean)+'\n')
    p.rel4.require(p.rel4.sha(selection)==receipt['output_shas']['selection.jsonl'],'selection changed')
    cfg=receipt['rel4_config'];p.rel4.require(p.rel4.sha(cfg['path'])==cfg['sha256'],'REL4 config changed')
    config_root,config=p.rel4.load_config(cfg['path']);p.rel4.input_check(config_root,config)
    receipt.update(status='ok',crops=dict(existing=existing,written=written,total=len(rows)),reconstruction_sha256=p.rel4.sha(module.__file__))
    receipt['output_shas']['p1pool.jsonl']=p.rel4.sha(manifest)
    p.rel4.write_json(receipt_path,receipt)
    return receipt

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--selection',type=Path,required=True);a.add_argument('--census-code',type=Path,required=True);a.add_argument('--workers',type=int,default=8);v=a.parse_args();print(p.rel4.canonical(run(v.selection,v.census_code,v.workers)['crops']))

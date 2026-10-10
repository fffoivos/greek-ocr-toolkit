"""Fresh full-dependency geometry/Q8 benchmarks and detector-format exports."""
import argparse,json,hashlib
from time import perf_counter
import cv2
import numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT
from ..shared.detector import Detector,postprocess
from ..shared.geometry_pipeline import run
from ..shared.review import detector_record
from ..shared.timing import dump,append
from .reference import DEST


def sources():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'prototypes/fast_lines/shared').glob('geometry*.py')}


def measure(repeat):
    cv2.setNumThreads(1);out=DEST/'round4/runtime';out.mkdir(exist_ok=True,parents=True);fp=out/f'repeat-{repeat}.jsonl'
    if fp.exists():raise FileExistsError(fp)
    hashes=sources();detector=Detector();rows=manifest()['pages'];rows=rows if repeat%2 else rows[::-1]
    dump(out/f'repeat-{repeat}.meta.json',dict(source=hashes,startup_s=detector.startup_s,
        definition='Fresh decode and detector, then one Q8 plus native contour geometry and conditional original-pixel fragments; all dependencies included. Single-thread warm session.'))
    for j,r in enumerate(rows):
        t=perf_counter();gray=cv2.imread(str(ROOT/r['path']),0);decode=perf_counter()-t
        t=perf_counter();pm,meta=detector.infer(gray);items=postprocess(pm,r['image_size']);baseline=perf_counter()-t
        if not r['parked']:a=run(gray,pm,items)
        else:a=dict(items=items,prior=items,joins=[],added_s=0,fragment_s=0,scout_s=0,geometry_s=0,separator_s=0)
        old=json.loads((DEST/'corrections-v6'/(r['page']+'.json')).read_text())['items']
        study=json.loads((DEST/'round4/fragments-v5'/(r['page']+'.json')).read_text())['items']
        polys=lambda qs:[q['polygon'] for q in qs]
        record=dict(page=r['page'],group=r['group'],repeat=repeat,decode_s=decode,baseline_s=baseline,
            **{k:a[k] for k in ['added_s','fragment_s','scout_s','geometry_s','separator_s']},
            total_s=decode+baseline+a['added_s'],joins=len(a['joins']),baseline_equal=polys(items)==polys(get_baseline(r)),
            prior_equal=polys(a['prior'])==polys(old),study_equal=polys(a['items'])==polys(study))
        append(fp,record)
        if repeat==1:
            final=detector_record(r,a['items'],record['total_s']);final['timing']=record
            dump(out/'detector'/(r['page']+'.json'),final)
        if not all(record[k] for k in ['baseline_equal','prior_equal','study_equal']):print('MISMATCH',record,flush=True)
        if (j+1)%20==0:print('runtime',repeat,j+1,flush=True)
    assert sources()==hashes,'runtime source changed during run'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repeat',type=int,required=True);a=p.parse_args();measure(a.repeat)

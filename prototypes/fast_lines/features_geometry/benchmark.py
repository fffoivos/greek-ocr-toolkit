"""Repeated fresh, single-thread end-to-end timings; no cached maps in the timer."""
import argparse,json,platform,random
from time import perf_counter
import cv2
import numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT,MODEL,digest
from ..shared.detector import Detector,postprocess
from ..shared.geometry_feature_correct import run
from ..layout_barriers.fast import run as q8
from ..shared.review import detector_record
from ..shared.timing import dump,append,summary
from .reference import DEST


def sources():
    paths=list((ROOT/'prototypes/fast_lines/shared').glob('*.py'))
    paths+=list((ROOT/'prototypes/fast_lines/features_geometry').glob('*.py'))
    paths+=[ROOT/'prototypes/fast_lines/layout_barriers/fast.py']
    return {str(p.relative_to(ROOT)):digest(p) for p in sorted(paths)}


def polygons(items):
    return [q['polygon'] for q in items]


def measure(rows,repeat):
    cv2.setNumThreads(1);out=DEST/'benchmark-v6';out.mkdir(parents=True,exist_ok=True)
    filename=out/f'repeat-{repeat}.jsonl'
    if filename.exists():raise FileExistsError('Use a new repeat number; raw runs are immutable')
    source=sources();d=Detector()
    dump(out/f'repeat-{repeat}.meta.json',dict(source=source,model_sha256=digest(MODEL),
        python=platform.python_version(),platform=platform.platform(),opencv=cv2.__version__,
        startup_s=d.startup_s,threads=1,version=6,
        definition='Decode, fresh preprocess/inference/postprocess, then full Q8+geometry stack. Warm session; no warmup page. IO review excluded. Independent Q8 comparator alternates order.'))
    rows=list(rows);random.Random(713+repeat).shuffle(rows)
    for j,r in enumerate(rows):
        start=perf_counter();gray=cv2.imread(str(ROOT/r['path']),0);decode=perf_counter()-start
        start=perf_counter();pm,meta=d.infer(gray);items=postprocess(pm,r['image_size']);baseline=perf_counter()-start
        if r['parked']:
            result=dict(items=items,added_s=0.,scout_s=0.,geometry_s=0.,separator_s=0.,geometry_changes=[],witness=dict(trigger=False))
            q8_s=stack_s=0.
        else:
            # Each comparator includes its own scout and every dependency.
            if j%2==0:
                start=perf_counter();q8(gray,items);q8_s=perf_counter()-start
            start=perf_counter();result=run(gray,pm,items,6);stack_s=perf_counter()-start
            if j%2:
                start=perf_counter();q8(gray,items);q8_s=perf_counter()-start
        cached=get_baseline(r)
        exported=json.loads((DEST/'corrections-v6'/(r['page']+'.json')).read_text())
        record=dict(page=r['page'],group=r['group'],direction=r['direction'],repeat=repeat,order=j,
            image_sha256=r['sha256'],decode_s=decode,baseline_s=baseline,stack_s=stack_s,
            q8_s=q8_s,increment_s=stack_s-q8_s,total_s=decode+baseline+stack_s,
            scout_s=result['scout_s'],geometry_s=result['geometry_s'],separator_s=result['separator_s'],
            triggered=result['witness']['trigger'],geometry_changes=len(result['geometry_changes']),
            baseline_matches=polygons(items)==polygons(cached),
            study_matches=polygons(result['items'])==polygons(exported['items']),detector=meta)
        append(filename,record)
        if repeat==1:
            final=detector_record(r,result['items'],record['total_s'])
            final['timing']=dict(decode_s=decode,baseline_s=baseline,correction_s=stack_s,
                receipt=str(filename.relative_to(ROOT)),repeat=repeat)
            dump(DEST/'detector'/ (r['page']+'.json'),final)
        if (j+1)%20==0:print('fresh timing',repeat,j+1,len(rows),flush=True)
    assert sources()==source,'Source changed during measurement'
    print('complete fresh timing',repeat,len(rows),flush=True)


def summarize():
    out=DEST/'benchmark-v6';records=[]
    for p in sorted(out.glob('repeat-*.jsonl')):records.extend(json.loads(s) for s in p.read_text().splitlines())
    data={}
    for group in sorted({r['group'] for r in records}):
        subset=[r for r in records if r['group']==group]
        data[group]={k:summary([r[k]*1000 for r in subset]) for k in
            ('decode_s','baseline_s','stack_s','q8_s','increment_s','total_s','scout_s','geometry_s','separator_s')}
    dump(out/'summary.json',dict(units='ms',groups=data,records=len(records),
        baseline_matches=all(r['baseline_matches'] for r in records),study_matches=all(r['study_matches'] for r in records)))
    print(json.dumps(data,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repeat',type=int);p.add_argument('--groups',nargs='*');p.add_argument('--summary',action='store_true');a=p.parse_args()
    if a.summary:summarize()
    else:
        rows=manifest()['pages']
        if a.groups:rows=[r for r in rows if r['group'] in a.groups]
        measure(rows,a.repeat)

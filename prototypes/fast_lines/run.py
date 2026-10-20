"""Manifest-driven Q7 runner. Run from the worktree with the supplied interpreter."""
import argparse,importlib,json,random,time,hashlib
from pathlib import Path
import cv2,numpy as np
from prototypes.fast_lines.shared.manifest import ROOT,OUT,MODEL,build,load,digest
from prototypes.fast_lines.shared.detector import Detector,postprocess,DEFAULT
from prototypes.fast_lines.shared.timing import dump,append,Registry,summary,key
from prototypes.fast_lines.shared import references,review

SHARED=OUT/'shared'; CACHE=SHARED/'cache'; MANIFEST=SHARED/'manifest.json'

def fingerprint(names):
    return key(*[digest(ROOT/'prototypes/fast_lines'/n) for n in names])

def baseline(rows,manifest):
    CACHE.mkdir(parents=True,exist_ok=True); d=Detector(); registry=Registry(SHARED/'registry')
    dump(SHARED/'startup.json',dict(seconds=d.startup_s,threads=1,provider='CPUExecutionProvider',model=manifest['model_sha256']))
    gray=cv2.imread(str(ROOT/rows[0]['path']),0); start=time.perf_counter(); d.infer(gray)
    dump(SHARED/'warmup.json',dict(page=rows[0]['page'],seconds=time.perf_counter()-start,excluded_from_timings=True))
    order=list(rows); random.Random(20261010).shuffle(order)
    source=fingerprint(['shared/detector.py','shared/paddle_db.py'])
    for nr,row in enumerate(order):
        page=row['page']; dest=CACHE/page
        with registry.claim('E00',row['sha256'],dict(DEFAULT,model=manifest['model_sha256'],long_side=960),source) as event:
            if event is None:
                if not dest.with_suffix('.json').exists(): raise RuntimeError('receipt exists but artifact missing')
                continue
            timings=[]
            for repeat in range(1 if row['parked'] else 3):
                wall=time.perf_counter(); t=time.perf_counter(); gray=cv2.imread(str(ROOT/row['path']),0); decode=time.perf_counter()-t
                pm,meta=d.infer(gray); t=time.perf_counter(); items=postprocess(pm,row['image_size']); post=time.perf_counter()-t
                timings.append(dict(page=page,group=row['group'],parked=row['parked'],repeat=repeat,decode_s=decode,postprocess_s=post,**meta,
                                    compute_s=meta['preprocess_s']+meta['inference_s']+post,wall_s=time.perf_counter()-wall,event=event['id']))
            np.save(dest.with_suffix('.npy'),pm)
            data=dict(items=items,timings=timings,status='orientation parked' if row['parked'] else 'baseline',map_file=str(dest.with_suffix('.npy').relative_to(ROOT)))
            dump(dest.with_suffix('.json'),data)
            review.write_result(SHARED/'baseline',row,gray,data,float(np.median([t['compute_s'] for t in timings])))
            for timing in timings: append(SHARED/'baseline_timings.jsonl',timing)
            # Cache comparison is diagnostic; old outputs are not a reference.
            old=ROOT/'.astra/fast_lines/detectors/paddle_PP-OCRv6_small_det_cpu'/f'{page}.json'
            if old.exists():
                cached=json.loads(old.read_text()); event['cached_count']=len(cached['items']); event['new_count']=len(items)
            event['page']=page
        print('baseline',nr+1,len(rows),page,len(items),flush=True)
    review.gallery(SHARED/'baseline',rows,'Q7 common small-detector baseline')

def reference_run(rows):
    registry=Registry(SHARED/'registry'); source=fingerprint(['shared/references.py','shared/image_evidence.py','shared/geometry.py','shared/review.py'])
    for nr,row in enumerate(rows):
        with registry.claim('ER',row['sha256'],dict(ours=row['ours_sha256'],dense_samples=[81,81],scale=1600),source) as event:
            if event is None: continue
            gray=cv2.imread(str(ROOT/row['path']),0); base=json.loads((CACHE/f"{row['page']}.json").read_text())
            references.build(gray,base['items'],row,SHARED/'references'); event['page']=row['page']
        print('reference',nr+1,len(rows),row['page'],flush=True)

def main():
    cv2.setNumThreads(1)
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['manifest','baseline','references','prototype','compose','perturb','report'])
    parser.add_argument('--approach'); parser.add_argument('--phase',type=int,default=1); parser.add_argument('--limit',type=int); parser.add_argument('--pages',nargs='*')
    args=parser.parse_args()
    if args.command=='manifest': dump(MANIFEST,build()); print(MANIFEST); return
    manifest=load(MANIFEST); rows=manifest['pages']
    if args.pages: rows=[r for r in rows if r['page'] in args.pages]
    if args.limit: rows=rows[:args.limit]
    if args.command=='baseline': baseline(rows,manifest)
    elif args.command=='references': reference_run(rows)
    else:
        from prototypes.fast_lines import workflow
        getattr(workflow,args.command)(rows,args)

if __name__=='__main__': main()

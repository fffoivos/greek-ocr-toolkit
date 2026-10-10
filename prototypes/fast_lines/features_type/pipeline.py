"""Auditable all-cohort corrections and fresh, repeated dependency-inclusive timing."""
import argparse,json,shutil,hashlib,html
from time import perf_counter
from pathlib import Path
import cv2,numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT,digest,MODEL
from ..shared.type_recovery import run
from ..shared.detector import Detector,postprocess
from ..shared.review import save_image,detector_record
from ..shared.geometry import mask,roi
from ..shared.contracts import bbox
from ..shared.timing import dump
from .reference import DEST,label


def source():
    files=sorted((ROOT/'prototypes/fast_lines/shared').glob('type_*.py'))+[Path(__file__)]
    return hashlib.sha256(''.join(digest(p) for p in files).encode()).hexdigest()[:12],files


def draw(gray,before,after):
    sc=min(1.,1500/gray.shape[1]);g=cv2.resize(gray,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA);im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
    old=mask(before,g.shape,(gray.shape[1],gray.shape[0]));new=mask(after,g.shape,(gray.shape[1],gray.shape[0]));ink=g<200
    im[(old>0)&(new==0)&ink]=(30,30,220);im[(new>0)&(old==0)&ink]=(30,175,30)
    for q in before:
        if not q.get('discounted'):cv2.polylines(im,[np.rint(np.asarray(q['polygon'])*sc).astype(np.int32)],True,(160,160,160),1)
    for q in after:
        if q not in before:cv2.polylines(im,[np.rint(np.asarray(q['polygon'])*sc).astype(np.int32)],True,(35,155,35),1)
    return im


def study(rows,version):
    key,files=source();dest=DEST/f'corrections-v{version}-{key}';dest.mkdir(parents=True,exist_ok=True)
    snapshots=dest/'source';snapshots.mkdir(exist_ok=True)
    for f in files:shutil.copyfile(f,snapshots/f.name)
    d=Detector();ledger=[];tiles=[]
    for row in rows:
        p=row['page'];f=dest/(p+'.json')
        if f.exists():continue
        g=cv2.imread(str(ROOT/row['path']),0);before=get_baseline(row)
        result=run(g,before,d,version=version) if not row['parked'] else dict(items=before,added=[],added_s=0,parked=True)
        dump(f,detector_record(row,result['items'],result['added_s']))
        evidence={k:v for k,v in result.items() if k!='items'}
        # Full separator items duplicate the result; retain the decisions/cuts only.
        for k in ['separator','final_separator']:
            if evidence.get(k):evidence[k]={a:b for a,b in evidence[k].items() if a!='items'}
        evidence.update(page=p,group=row['group'],direction=row['direction'],input_sha256=row['sha256'],seconds_scope='additional stack after cached baseline; benchmark supplies full detector time')
        dump(dest/(p+'.evidence.json'),evidence)
        im=draw(g,before,result['items']);save_image(dest/(p+'.jpg'),label(im,p+' | detector grey; added green; removed ink red'))
        for k,q in enumerate(result['added']):
            bb=bbox(q);h=(bb[3]-bb[1])/2;a,t,b,c=roi([bb[0]-h,bb[1]-h,bb[2]+h,bb[3]+h],g.shape)
            raw=cv2.cvtColor(g[t:c,a:b],cv2.COLOR_GRAY2BGR);out=raw.copy();cv2.polylines(out,[np.rint(np.asarray(q['polygon'])-[a,t]).astype(np.int32)],True,(20,150,20),2)
            tile=np.vstack([raw,out]);sc=min(1.,1050/tile.shape[1]);tile=cv2.resize(tile,None,fx=sc,fy=sc)
            tiles.append(label(tile,p+f' addition {k} raw/after'));ledger.append(dict(page=p,addition=k,board=(len(tiles)-1)//4))
        print(p,len(result['added']),round(result['added_s'],3),flush=True)
    for i in range(0,len(tiles),4):save_image(dest/f'changes-{i//4:02d}.jpg',np.vstack(tiles[i:i+4]))
    dump(dest/'change-review-index.json',ledger);dump(DEST/'active-corrections.json',dict(directory=str(dest.relative_to(ROOT)),version=version,source=key))
    return dest


def bench(rows,version,repeat):
    key,_=source();dest=DEST/f'benchmark-v{version}-{key}';dest.mkdir(parents=True,exist_ok=True);d=Detector();out=[]
    for row in rows:
        t=perf_counter();g=cv2.imread(str(ROOT/row['path']),0);decode=perf_counter()-t
        t=perf_counter();pm,meta=d.infer(g);items=postprocess(pm,row['image_size']);base=perf_counter()-t
        r=run(g,items,d,version=version) if not row['parked'] else dict(items=items,added=[],added_s=0,type_s=0,scout_s=0,correction_s=0)
        rec=dict(page=row['page'],group=row['group'],direction=row['direction'],repeat=repeat,decode_s=decode,detector_s=base,
                 type_s=r['type_s'],scout_s=r['scout_s'],correction_s=r['correction_s'],stack_added_s=r['added_s'],total_s=base+r['added_s'],
                 additions=len(r['added']),unchanged=r['items']==items,source=key,startup_s=d.startup_s,**meta)
        dump(dest/(row['page']+f'.r{repeat}.json'),rec);out.append(rec)
    print(json.dumps(dict(n=len(out),repeat=repeat,type_median_ms=float(np.median([x['type_s'] for x in out])*1000),max_ms=max(x['type_s'] for x in out)*1000)),flush=True)
    dump(DEST/'active-benchmark.json',dict(directory=str(dest.relative_to(ROOT)),version=version,source=key))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['study','bench']);p.add_argument('--version',type=int,default=1);p.add_argument('--offset',type=int,default=0);p.add_argument('--limit',type=int,default=195);p.add_argument('--group');p.add_argument('--repeat',type=int,default=1);a=p.parse_args();cv2.setNumThreads(1)
    rows=[r for r in manifest()['pages'] if not a.group or r['group']==a.group][a.offset:a.offset+a.limit]
    if a.action=='study':study(rows,a.version)
    else:bench(rows,a.version,a.repeat)

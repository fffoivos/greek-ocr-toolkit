"""Full-cohort exported corrections and dependency-inclusive repeated timings."""
import argparse,json,hashlib,shutil
from pathlib import Path
from time import perf_counter
import cv2,numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT,digest
from ..shared.type_extended import run
from ..shared.detector import Detector,postprocess
from ..shared.review import detector_record,save_image
from ..shared.timing import dump
from ..shared.geometry import roi
from ..shared.contracts import bbox
from .pipeline import draw
from .reference import DEST,label


def source():
    files=sorted((ROOT/'prototypes/fast_lines/shared').glob('type_*.py'))+[Path(__file__)];return hashlib.sha256(''.join(digest(p) for p in files).encode()).hexdigest()[:12],files


def run_study(rows,repeat):
    key,files=source();dest=DEST/f'round4-final-{key}';dest.mkdir(exist_ok=True);snap=dest/'source';snap.mkdir(exist_ok=True)
    for p in files:shutil.copyfile(p,snap/p.name)
    detector=Detector();tiles=[];ledger=[];stats=[]
    for row in rows:
        p=row['page'];t=perf_counter();g=cv2.imread(str(ROOT/row['path']),0);decode=perf_counter()-t
        t=perf_counter();pm,meta=detector.infer(g);items=postprocess(pm,row['image_size']);base=perf_counter()-t
        assert items==get_baseline(row),p+' baseline changed'
        r=run(g,items,detector) if not row['parked'] else dict(items=items,added=[],new_added=[],type_s=0,added_s=0,scout_s=0,correction_s=0)
        record=detector_record(row,r['items'],base+r['added_s']);f=dest/(p+'.json')
        if repeat>1 and f.exists():assert record['items']==json.loads(f.read_text())['items'],p+' final differs'
        dump(f,record)
        if repeat==1:
            dump(dest/(p+'.evidence.json'),{k:v for k,v in r.items() if k!='items'})
            save_image(dest/(p+'.jpg'),label(draw(g,items,r['items']),p+' round4 | grey detector; green added; red removed ink'))
            for i,q in enumerate(r['new_added']):
                a,t,b,c=bbox(q);h=(c-t)/2;a,t,b,c=roi([a-h,t-h,b+h,c+h],g.shape);raw=cv2.cvtColor(g[t:c,a:b],cv2.COLOR_GRAY2BGR);im=raw.copy();cv2.polylines(im,[np.rint(np.asarray(q['polygon'])-[a,t]).astype(np.int32)],True,(30,150,30),2)
                tile=np.vstack([raw,im]);sc=min(1,1050/tile.shape[1]);tiles.append(label(cv2.resize(tile,None,fx=sc,fy=sc),p+f' new{i} raw/after'));ledger.append(dict(page=p,addition=i,board=(len(tiles)-1)//4))
        rec=dict(page=p,group=row['group'],direction=row['direction'],repeat=repeat,decode_s=decode,detector_s=base,type_s=r['type_s'],stack_added_s=r['added_s'],total_s=base+r['added_s'],scout_s=r['scout_s'],correction_s=r['correction_s'],added=len(r['added']),new=len(r['new_added']),source=key,exact_baseline=True,final_sha256=hashlib.sha256(json.dumps(record['items'],sort_keys=True).encode()).hexdigest())
        dump(dest/(p+f'.r{repeat}.json'),rec);stats.append(rec)
        print(p,len(r['added']),len(r['new_added']),round(r['type_s']*1000,1),flush=True)
    for i in range(0,len(tiles),4):save_image(dest/f'new-{i//4:02d}.jpg',np.vstack(tiles[i:i+4]))
    if ledger:dump(dest/'new-review.json',ledger)
    dump(DEST/'active-final4.json',dict(directory=str(dest.relative_to(ROOT)),source=key))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repeat',type=int,default=1);p.add_argument('--offset',type=int,default=0);p.add_argument('--limit',type=int,default=195);a=p.parse_args();cv2.setNumThreads(1);run_study(manifest()['pages'][a.offset:a.offset+a.limit],a.repeat)

"""Experimental recovery from explicitly rendered uncertain grid intervals."""
import argparse,json,hashlib
from time import perf_counter
from pathlib import Path
import cv2,numpy as np
from ..round2 import manifest,get_baseline
from ..layout_barriers.fast import run as separators
from ..shared.manifest import ROOT,digest
from ..shared.type_grid_edges import analyze
from ..shared.type_context import recover
from ..shared.type_ink_motif_gate import inspect as motif
from ..shared.type_recovery import run as previous
from ..shared.type_table_extent import analyze as extents
from ..shared.detector import Detector,postprocess
from ..shared.review import detector_record,save_image
from ..shared.geometry import height_proxy,roi
from ..shared.contracts import bbox,rect
from ..shared.timing import dump
from .reference import DEST,label
from .pipeline import draw


def run(gray,items,detector,*,version=1):
    start=perf_counter();old=previous(gray,items,detector,version=4);t=perf_counter();current=old['items'];evidence=analyze(gray,current,route='heuristic',version=2)
    veto=[];motifs=[];table=None
    for i,s in enumerate(evidence['slots']):
        if not s['supported'] or s['owned_fraction']>=.25:continue
        q=dict(polygon=rect([s['x0'],s['y']-.8*s['height'],s['x1'],s['y']+.8*s['height']]))
        r,_=motif(gray,q,s['height']);motifs.append(dict(slot=i,**r))
        if r['drop']:veto.append(q)
    extra=recover(gray,current,detector,excluded_regions=veto,lattice_evidence=evidence,version=4)
    final=separators(gray,current+extra['added']) if extra['added'] else dict(items=current)
    end=perf_counter()
    return dict(items=final['items'],added=old['added']+extra['added'],new_added=extra['added'],previous=old,extension={k:v for k,v in extra.items() if k!='items'},motifs=motifs,extension_s=end-t,seconds=end-start,type_s=old['type_s']+end-t,version=version)


def study(rows,version):
    sources=sorted((ROOT/'prototypes/fast_lines/shared').glob('type_*.py'))+[Path(__file__)];key=hashlib.sha256(''.join(digest(p) for p in sources).encode()).hexdigest()[:12]
    dest=DEST/f'round4-recovery-v{version}-{key}';dest.mkdir(exist_ok=True);d=Detector();tiles=[];summary=[]
    for row in rows:
        g=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row);out=run(g,items,d,version=version)
        dump(dest/(row['page']+'.json'),detector_record(row,out['items'],out['seconds']))
        dump(dest/(row['page']+'.evidence.json'),{k:v for k,v in out.items() if k!='items'})
        save_image(dest/(row['page']+'.jpg'),label(draw(g,items,out['items']),row['page']+' added green, detector grey'))
        for i,q in enumerate(out['new_added']):
            x0,y0,x1,y1=bbox(q);h=(y1-y0)/2;a,t,b,c=roi([x0-h,y0-h,x1+h,y1+h],g.shape);raw=cv2.cvtColor(g[t:c,a:b],cv2.COLOR_GRAY2BGR);im=raw.copy();cv2.polylines(im,[np.rint(np.asarray(q['polygon'])-[a,t]).astype(np.int32)],True,(30,160,30),2)
            z=np.vstack([raw,im]);scale=min(1,1050/z.shape[1]);tiles.append(label(cv2.resize(z,None,fx=scale,fy=scale),row['page']+f' new{i} raw/after'))
        summary.append(dict(page=row['page'],new=len(out['new_added']),total=len(out['added']),extension_s=out['extension_s']))
        print(row['page'],len(out['new_added']),round(out['extension_s']*1000,1),flush=True)
    for i in range(0,len(tiles),4):save_image(dest/f'new-{i//4:02d}.jpg',np.vstack(tiles[i:i+4]))
    dump(dest/'summary.json',summary);dump(DEST/'active-recover4.json',dict(directory=str(dest.relative_to(ROOT)),version=version))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--version',type=int,default=1);a=p.parse_args();cv2.setNumThreads(1)
    study([r for r in manifest()['pages'] if r['direction']=='ours_more' or r['group']=='agreement'],a.version)

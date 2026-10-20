"""Optional feature costs, distinct from the timed conditional correction stack."""
import argparse,cv2
from time import perf_counter
from ..round2 import manifest,get_baseline,ROOT
from ..shared.contracts import bbox
from ..shared.geometry import height_proxy
from ..shared.ink_strokes import measure,heuristic
from ..shared.ink_images import render,heuristic as image_heuristic
from ..shared.ink_ownership import analyze
from ..shared.timing import dump
from .study import DEST,ANCHORS


def run(start,count,repeat):
    cv2.setNumThreads(1);wanted=set(ANCHORS)|{'an-ef481610a820-p000150','s2-31f40cef90235c91b023-p00001','s2-77d1bd63d5babbe0df73-p00001','s2-200e977f2dab5291c42c-p00035'}
    rows=[r for r in manifest()['pages'] if r['page'] in wanted][start:start+count];records=[]
    for row in rows:
        gray=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row);h=height_proxy(items,row['image_size']);out=dict(page=row['page'],repeat=repeat)
        calls={'strokes_slow':lambda:[measure(gray,bbox(q),h) for q in items],
               'strokes_r1':lambda:[measure(gray,bbox(q),h,samples=32) for q in items],
               'strokes_r2':lambda:[heuristic(gray,bbox(q),h) for q in items],
               'images_slow':lambda:render(gray,h,samples=24),'images_r1':lambda:render(gray,h,samples=8),'images_r2':lambda:image_heuristic(gray,h)}
        for name,fn in calls.items():t=perf_counter();fn();out[name]=perf_counter()-t
        for route in ('dense','explicit','sampled'):
            t=perf_counter();analyze(gray,items,route=route);out['ownership_'+route]=perf_counter()-t
        records.append(out)
    dest=DEST/'diagnostic-timing';dest.mkdir(exist_ok=True);path=dest/f'{repeat}-{start}.json'
    assert not path.exists();dump(path,dict(rows=records,meaning='cached original small boxes, fresh feature computation; diagnostic only; detector and decode excluded'))
    print('diagnostic timing',repeat,start,len(rows),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=0);ap.add_argument('--count',type=int,default=4);ap.add_argument('--repeat',type=int,default=0);a=ap.parse_args();run(a.start,a.count,a.repeat)

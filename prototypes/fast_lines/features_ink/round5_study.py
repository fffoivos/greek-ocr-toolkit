"""Owner-scoped explicit studies, immutable version destinations; no held-out input."""
import argparse,json,cv2,numpy as np
from pathlib import Path
from time import perf_counter
from ..round2 import ROOT,manifest,get_baseline
from ..shared.geometry import height_proxy
from ..shared.ink_ownership import analyze
from ..shared.ink_seal import render
from ..shared.timing import dump

DEST=ROOT/'.astra/fast_lines/out/round5/ink'
REVIEW=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r4')


def study(version,limit=195,offset=0):
    cv2.setNumThreads(1);out=DEST/version;out.mkdir(parents=True,exist_ok=True)
    for row in manifest()['pages'][offset:offset+limit]:
        p=row['page'];target=out/(p+'.json')
        if target.exists():raise RuntimeError('Already studied '+p)
        gray=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row);own=analyze(gray,items);h=own['height'];records={}
        for route in ('slow','explicit','heuristic'):
            v=render(gray,items,h,route=route,detail=True,candidate_indices=[i for i in own['weak_indices'] if i not in own['suppress_indices']]);records[route]=v
            s=min(1.,1400/gray.shape[0]);im=cv2.cvtColor(cv2.resize(gray,None,fx=s,fy=s),cv2.COLOR_GRAY2BGR)
            for j,r in enumerate(v['rings']):
                for name,color in [('outer',(0,120,0)),('inner',(255,120,0))]:
                    q=r[name];xy=np.round(np.array(q['path'])*s).astype('int32');cv2.polylines(im,[xy],True,color,1)
                    raw=q.pop('raw');cv2.imwrite(str(out/f'{p}.{route}.{j}.{name}.jpg'),raw)
            for i in v['candidates']:
                poly=np.round(np.array(items[i]['polygon'])*s).astype('int32');cv2.polylines(im,[poly],True,(255,0,200),1)
            for i in v['suppress_indices']:
                poly=np.round(np.array(items[i]['polygon'])*s).astype('int32');cv2.polylines(im,[poly],True,(0,0,255),2)
            if v['candidates']:cv2.imwrite(str(out/f'{p}.{route}.jpg'),im)
        dump(target,dict(page=p,height=h,weak_candidates=own['weak_indices'],routes=records))
        if records['slow']['candidates']:print(p,[(r,len(v['rings']),v['suppress_indices'],round(v['seconds']*1000,1)) for r,v in records.items()],flush=True)


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('version');a.add_argument('--limit',type=int,default=195);a.add_argument('--offset',type=int,default=0);args=a.parse_args();study(args.version,args.limit,args.offset)

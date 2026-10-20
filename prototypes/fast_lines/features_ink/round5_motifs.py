"""Three-route separated-component study; all accepted crops retained for review."""
import argparse,json,cv2,numpy as np
from ..round2 import ROOT,manifest,get_baseline
from ..shared.geometry import height_proxy
from ..shared.contracts import bbox
from ..shared.ink_discrete_motifs import inspect,scout
from ..shared.ink_motif_gate import inspect as spatial
from ..shared.timing import dump
from .round5_study import DEST


def run(version,offset,limit):
    cv2.setNumThreads(1);out=DEST/version;out.mkdir(parents=True,exist_ok=True)
    for row in manifest()['pages'][offset:offset+limit]:
        p=row['page'];target=out/f'{p}.json'
        if target.exists():raise RuntimeError('Existing experiment '+p)
        gray=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row);h=height_proxy(items,row['image_size']);records=[]
        for i,item in enumerate(items):
            if not scout(gray,item,h):continue
            rs={}
            for route in ('slow','explicit','heuristic'):
                v=inspect(gray,item,h,route=route,detail=True);raw=v.pop('raw');labels=v.pop('labels');mask=v.pop('mask')
                if v['groups'] and not v['vertical']:
                    m,_=spatial(gray,item,h,diagnostic=True,samples=h if route=='slow' else 16 if route=='explicit' else 8)
                    v['spatial']={k:m[k] for k in ('drop','coverage','remaining_glyphs','matches','template') if k in m};v['drop']=m['drop']
                rs[route]=v
                if v['groups'] or v['drop']:
                    im=cv2.cvtColor(raw,cv2.COLOR_GRAY2BGR)
                    for box in v['matches']:cv2.rectangle(im,tuple(box[:2]),tuple(box[2:]),(0,180,0),1)
                    for q in v['unexplained']:
                        x,y,w,ch,_=q;cv2.rectangle(im,(x,y),(x+w,y+ch),(0,0,255),1)
                    cv2.imwrite(str(out/f'{p}.{i}.{route}.jpg'),im)
            records.append(dict(line=i,routes=rs))
            if any(v['drop'] for v in rs.values()):print(p,i,{r:v['drop'] for r,v in rs.items()},flush=True)
        dump(target,dict(page=p,nominated=len(records),records=records))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('version');ap.add_argument('--offset',type=int,default=0);ap.add_argument('--limit',type=int,default=195);a=ap.parse_args();run(a.version,a.offset,a.limit)

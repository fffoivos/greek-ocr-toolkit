"""Compact review sheets, with a page/line ledger for every fragment hypothesis."""
import json
import cv2
import numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT
from ..shared.geometry import roi
from ..shared.contracts import bbox
from ..shared.review import atlas,save_image
from ..shared.timing import dump
from .reference import DEST,line


def run():
    out=DEST/'round4/review';out.mkdir(parents=True,exist_ok=True);rows=manifest()['pages'];ledger=[];tiles=[]
    for j,r in enumerate(rows):
        if j%12==0:
            cells=[]
            for rr in rows[j:j+12]:
                p=rr['page'];cells.append((p,cv2.imread(str(DEST/'round4/body-slow-v7'/(p+'.jpg')))))
            atlas(cells,out/f'pages-{j//12:02d}.jpg',columns=3,cell_width=450)
        p=r['page'];body=json.loads((DEST/'round4/body-slow-v7'/(p+'.json')).read_text());pairs=body.get('fragment_witness',{}).get('paths',[])
        if not pairs:continue
        gray=cv2.imread(str(ROOT/r['path']),0);items=get_baseline(r);h=body['height'];byid={q['line']:q for q in body['lines']}
        for pair in pairs:
            q=byid.get(pair['line'])
            if not q:continue
            a=np.array(bbox(items[pair['line']]));b=np.array(bbox(items[pair['fragment']]));bb=np.r_[np.minimum(a[:2],b[:2]),np.maximum(a[2:],b[2:])]
            x0,y0,x1,y1=roi(bb+[-h,-h,h,h],gray.shape);raw=cv2.cvtColor(gray[y0:y1,x0:x1],cv2.COLOR_GRAY2BGR);draw=raw.copy()
            path=np.array(q['path'])-[x0,y0];seen=q['observed']
            for k in range(1,len(path)):
                if seen[k]&seen[k-1]:line(draw,path[k-1:k+1],(30,170,20),2)
            line(draw,np.array(pair['path'])-[x0,y0],(190,30,180),1)
            alt=next((z for z in q['alternatives'] if z['fragment']==pair['fragment']),{})
            tile=np.vstack([raw,draw]);scale=min(1,1400/tile.shape[1]);tile=cv2.resize(tile,None,fx=scale,fy=scale);panel=np.full((tile.shape[0]+28,1400,3),255,np.uint8);panel[28:,:tile.shape[1]]=tile
            label=f"{p} {pair['line']}+{pair['fragment']} native agree={alt.get('agrees')} | slow green / tangent purple"
            cv2.putText(panel,label,(5,19),cv2.FONT_HERSHEY_SIMPLEX,.44,(0,0,0),1)
            ledger.append(dict(page=p,line=pair['line'],fragment=pair['fragment'],sheet=len(tiles)//4,native_agrees=alt.get('agrees')));tiles.append(panel)
    for j in range(0,len(tiles),4):save_image(out/f'pairs-{j//4:02d}.jpg',np.vstack(tiles[j:j+4]))
    dump(out/'ledger.json',ledger)

if __name__=='__main__':
    cv2.setNumThreads(1);run()

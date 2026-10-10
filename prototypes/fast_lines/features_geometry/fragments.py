"""Original-ink fragment join study; all proposals retain reviewable ancestry."""
import argparse,json
import cv2
import numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT
from ..shared.geometry_fragment_correct import run
from ..shared.timing import dump
from ..shared.review import detector_record,save_image
from ..shared.geometry import roi
from ..shared.contracts import bbox
from .reference import DEST,save
from .correction import changes,overlay


def study(rows,version=1):
    out=DEST/f'round4/fragments-v{version}';out.mkdir(parents=True,exist_ok=True);summary=[]
    for r in rows:
        p=r['page'];gray=cv2.imread(str(ROOT/r['path']),0);original=get_baseline(r)
        prior=json.loads((DEST/'corrections-v6'/(p+'.json')).read_text())['items']
        rendering=json.loads((DEST/'round4/body-slow-v7'/(p+'.json')).read_text())
        result=run(gray,original,prior,rendering=rendering) if not r['parked'] else dict(items=prior,joins=[],decisions=[],seconds=0)
        delta=changes(original,result['items']);im=overlay(gray,original,result['items'],delta)
        save(out/(p+'.jpg'),im,p+' | R3+Q8 and two-ended fragment experiment; new green / old grey')
        dump(out/(p+'.json'),detector_record(r,result['items'],result['seconds']))
        dump(out/(p+'.evidence.json'),{k:v for k,v in result.items() if k!='items'})
        tiles=[];h=rendering.get('height',1)
        for join in result['joins']:
            poly=np.asarray(join['polygon']);x0,y0,x1,y1=roi([*poly.min(0)-h,*poly.max(0)+h],gray.shape)
            raw=cv2.cvtColor(gray[y0:y1,x0:x1],cv2.COLOR_GRAY2BGR);draw=im[y0:y1,x0:x1]
            tile=np.vstack([raw,draw]);scale=min(1,1400/tile.shape[1]);tile=cv2.resize(tile,None,fx=scale,fy=scale)
            panel=np.full((tile.shape[0]+25,1400,3),255,np.uint8);panel[25:,:tile.shape[1]]=tile
            cv2.putText(panel,'sources '+str(join['source_ids'])+' raw / joined',(5,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1);tiles.append(panel)
        for j in range(0,len(tiles),5):save_image(out/(p+f'.detail-{j//5:02d}.jpg'),np.vstack(tiles[j:j+5]))
        summary.append(dict(page=p,group=r['group'],joins=len(result['joins']),source_ids=[q['source_ids'] for q in result['joins']]))
        if result['joins']:print(p,summary[-1]['source_ids'],flush=True)
    dump(out/'summary.json',summary)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pages',nargs='*');p.add_argument('--version',type=int,default=1);a=p.parse_args();cv2.setNumThreads(1)
    rows=manifest()['pages']
    if a.pages:rows=[r for r in rows if r['page'] in a.pages]
    study(rows,a.version)

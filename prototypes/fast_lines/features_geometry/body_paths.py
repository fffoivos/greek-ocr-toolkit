"""R4 original body/contact rendering before curled-end corrections."""
import argparse,json
import cv2
import numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT,digest
from ..shared.timing import dump
from ..shared.review import save_image
from ..shared.geometry import roi
from ..shared.geometry_contacts import render_contacts
from .reference import DEST,save,line


def draw(gray,items,result):
    im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
    for q in items:cv2.polylines(im,[np.rint(q['polygon']).astype(np.int32)],True,(175,175,175),1)
    for c in result['components']:
        a,b,z,d=np.rint(c['bbox']).astype(int);cv2.rectangle(im,(a,b),(z,d),(200,160,30),1)
    for q in result['lines']:
        if result.get('version',1)>=3:
            points=np.asarray(q['path']);observed=np.asarray(q['observed'])
            for j in range(1,len(points)):
                if observed[j] and observed[j-1]:line(im,points[j-1:j+1],(30,170,30),2)
        else:line(im,q['path'],(30,170,30),2)
        p=np.asarray(q['path']);x,y=p[len(p)//2]
        cv2.putText(im,str(q['line']),(int(x),int(y)),cv2.FONT_HERSHEY_SIMPLEX,.5,(150,0,160),1)
    return im


def run(rows,route,version,details=True):
    out=DEST/f'round4/body-{route}-v{version}';out.mkdir(parents=True,exist_ok=True)
    for r in rows:
        p=r['page'];fp=out/(p+'.json')
        if fp.exists():continue
        gray=cv2.imread(str(ROOT/r['path']),0);items=get_baseline(r)
        a=render_contacts(gray,items,route,version) if not r['parked'] else dict(lines=[],components=[],seconds=0)
        a.update(page=p,image_sha256=r['sha256'])
        dump(fp,a);im=draw(gray,items,a);save(out/(p+'.jpg'),im,p+' | ink components cyan / support paths green / old grey')
        if version>=4:
            overlay=im.copy()
            for q in a.get('fragment_witness',{}).get('paths',[]):line(overlay,q['path'],(180,30,180),2)
            save(out/(p+'.route2.jpg'),overlay,p+' | R2 tangent continuation purple vs original-ink path green')
        if not details:continue
        tiles=[]
        for q in a['lines']:
            path=np.asarray(q['path']);h=a['height']
            x0,y0,x1,y1=roi([path[:,0].min(),path[:,1].min()-2*h,path[:,0].max(),path[:,1].max()+2*h],gray.shape)
            raw=cv2.cvtColor(gray[y0:y1,x0:x1],cv2.COLOR_GRAY2BGR)
            panel=np.vstack([raw,im[y0:y1,x0:x1]])
            scale=min(1,1400/panel.shape[1]);panel=cv2.resize(panel,None,fx=scale,fy=scale)
            tile=np.full((panel.shape[0]+25,1400,3),255,np.uint8);tile[25:,:panel.shape[1]]=panel
            cv2.putText(tile,f"source{q['line']} raw above / contacts+path below",(6,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
            tiles.append(tile)
        for j in range(0,len(tiles),6):save_image(out/(p+f'.detail-{j//6:02d}.jpg'),np.vstack(tiles[j:j+6]))
        print(p,len(a['lines']),round(a['seconds'],3),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pages',nargs='*');p.add_argument('--route',default='slow');p.add_argument('--version',type=int,default=1);p.add_argument('--no-details',action='store_true');a=p.parse_args()
    cv2.setNumThreads(1);rows=manifest()['pages']
    if a.pages:rows=[r for r in rows if r['page'] in a.pages]
    run(rows,a.route,a.version,not a.no_details)

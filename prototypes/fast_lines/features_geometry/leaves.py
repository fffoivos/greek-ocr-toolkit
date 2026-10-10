"""Physical leaf-seam study: ink continuation AND scanned outer-edge contact.

A sustained dark feature is not by itself a fold. Render boundary evidence
separately from whitespace; none of these hypotheses yet changes a detector.
"""
import argparse,json
from time import perf_counter
import cv2
import numpy as np
from scipy.signal import find_peaks
from ..round2 import manifest,get_baseline
from ..shared.geometry import height_proxy,quantize
from ..shared.image_evidence import components
from ..shared.manifest import ROOT
from ..shared.timing import dump
from .reference import DEST,save,line
from .leaf_paths import trace as trace_seams


def render(gray,height,route='slow',version=1):
    start=perf_counter();H,W=gray.shape
    scale=min(1,8/height) if route=='explicit_fast' else 1
    g=cv2.resize(gray,(quantize(W*scale),quantize(H*scale)),interpolation=cv2.INTER_AREA) if scale<1 else gray
    sy,sx=g.shape[0]/H,g.shape[1]/W;h=height*sy
    paper=float(np.percentile(g,90));dark=(g<paper*.65).astype(np.uint8)
    sustained=cv2.morphologyEx(dark,cv2.MORPH_OPEN,np.ones((quantize(2*h),1),np.uint8))
    widened=cv2.dilate(sustained,np.ones((1,quantize(.4*h)),np.uint8))
    connected=cv2.morphologyEx(widened,cv2.MORPH_CLOSE,np.ones((quantize(4*h),1),np.uint8))
    if version>=2:connected=cv2.morphologyEx(connected,cv2.MORPH_OPEN,np.ones((quantize(.5*len(g)),1),np.uint8))
    _,stats,_=components(connected);records=[]
    for x,y,w,hh,area in stats:
        cx=x+w/2
        if hh<.5*len(g) or not .2*g.shape[1]<cx<.8*g.shape[1] or w>4*h:continue
        yy=np.arange(y,min(y+hh,len(g)));a=max(0,x-quantize(h));b=min(g.shape[1],x+w+quantize(h))
        strip=cv2.boxFilter(dark[:,a:b].astype(np.float32),cv2.CV_32F,(quantize(.25*h),quantize(2*h)))
        xx=np.argmax(strip[yy],axis=1)+a
        points=np.c_[xx/sx,yy/sy];step=max(1,quantize(h/2));points=points[::step]
        # A real page contour must independently support BOTH image-margin ends.
        flank=max(1,quantize(3*h));xl=max(0,int(cx-flank));xr=min(g.shape[1],int(cx+flank))
        bands=max(1,int(.1*len(g)))
        top=float(dark[:bands,xl:xr].mean());bottom=float(dark[-bands:,xl:xr].mean())
        near_top=y<.12*len(g);near_bottom=y+hh>.88*len(g)
        edge_contacts=[]
        for end in (y,min(y+hh,len(g)-1)):
            ya=max(0,int(end-2*h));yb=min(len(g),int(end+2*h)+1)
            side_profiles=[]
            for xa,xb in [(cx-8*h,cx-2*h),(cx+2*h,cx+8*h)]:
                xa=max(0,int(xa));xb=min(g.shape[1],int(xb))
                if xb>xa:
                    support=dark[ya:yb,xa:xb].mean(1);idx=int(np.argmax(support))
                    side_profiles.append(dict(point=[float(cx/sx),float((ya+idx)/sy)],strength=float(support[idx])))
            edge_contacts.append(side_profiles)
        if version>=2:
            near_top=y<.15*len(g);near_bottom=y+hh>.8*len(g)
            top=max([z['strength'] for z in edge_contacts[0]] or [0]);bottom=max([z['strength'] for z in edge_contacts[1]] or [0])
        records.append(dict(edge_contacts=edge_contacts,bbox=[x/sx,y/sy,(x+w)/sx,(y+hh)/sy],path=points.tolist(),
            top_dark=top,bottom_dark=bottom,outer_contact=bool(near_top and near_bottom and top>(.5 if version>=2 else .05) and bottom>(.5 if version>=2 else .05)),
            warning='A seam hypothesis, not a proven physical leaf boundary.'))
    if version>=3:records=trace_seams(dark,height,sx,sy,version)
    if version>=5:
        # Render topology of the paper, independently of line boxes and dark-path score.
        sealed=cv2.dilate(dark,np.ones((quantize(.2*h)|1,quantize(.2*h)|1),np.uint8))
        n,labels,pstats,centres=cv2.connectedComponentsWithStats(1-sealed,8)
        for seam in records:
            points=np.array(seam['path'])*[sx,sy];core=(points[:,1]>.2*len(g))&(points[:,1]<.8*len(g));points=points[core]
            areas=[];ids=[]
            for side in (-1,1):
                xx=np.clip(np.rint(points[:,0]+side*2*h).astype(int),0,g.shape[1]-1);yy=np.clip(np.rint(points[:,1]).astype(int),0,len(g)-1)
                hits=labels[yy,xx];hits=hits[hits>0]
                ident=int(np.bincount(hits).argmax()) if len(hits) else 0;ids.append(ident)
                areas.append(dict(id=ident,area_fraction=float(pstats[ident,4]/g.size) if ident else 0.,
                    bbox=(pstats[ident,:4]/[sx,sy,sx,sy]).tolist() if ident else None))
            seam['paper_sides']=areas
            seam['two_paper_regions']=bool(ids[0]!=ids[1] and all(z['area_fraction']>.12 for z in areas))
            seam['outer_contact_before_paper']=seam['outer_contact']
            seam['outer_contact']=seam['outer_contact'] and seam['two_paper_regions']
    # R2: lower quantile over horizontal bands asks for recurring darkness.
    bands=np.array_split(dark,24,axis=0);profiles=np.array([b.mean(0) for b in bands])
    score=np.quantile(profiles,.25,axis=0);peaks,_=find_peaks(score,height=.2,distance=max(1,quantize(2*h)))
    heuristic=[dict(x=float(x/sx),score=float(score[x])) for x in peaks if .2*g.shape[1]<x<.8*g.shape[1]]
    return dict(route=route,version=version,height=height,seams=records,heuristic=heuristic,seconds=perf_counter()-start)


def run(rows,version=1):
    out=DEST/f'round4/leaves-v{version}';out.mkdir(parents=True,exist_ok=True)
    for r in rows:
        gray=cv2.imread(str(ROOT/r['path']),0);items=get_baseline(r);h=height_proxy(items,r['image_size'])
        slow=render(gray,h,version=version);fast=render(gray,h,'explicit_fast',version)
        im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
        for q in slow['seams']:
            line(im,q['path'],(30,170,20) if q['outer_contact'] else (0,155,235),4)
            if version>=4:
                for point,density in zip(q['path'],q.get('flank_density',[])):
                    if density>=.08:cv2.circle(im,tuple(np.rint(point).astype(int)),3,(30,30,210),-1)
            for end in q.get('edge_contacts',[]):
                for z in end:
                    if z['strength']>.5:cv2.circle(im,tuple(np.rint(z['point']).astype(int)),10,(200,100,20),3)
            a,b,c,d=np.rint(q['bbox']).astype(int);cv2.rectangle(im,(a,b),(c,d),(0,155,235),1)
        save(out/(r['page']+'.slow.jpg'),im,r['page']+' | native seam amber / outer contact green; NOT certified leaves')
        for q in fast['seams']:line(im,q['path'],(200,30,180),2)
        save(out/(r['page']+'.route1.jpg'),im,r['page']+' | native vs reduced seam purple')
        for q in slow['heuristic']:line(im,[[q['x'],0],[q['x'],gray.shape[0]-1]],(220,130,0),1)
        save(out/(r['page']+'.route2.jpg'),im,r['page']+' | column recurrence cyan vs native seam')
        dump(out/(r['page']+'.json'),dict(page=r['page'],slow=slow,fast=fast,parked=r['parked']))
        if slow['seams']:print(r['page'],[(q['outer_contact'],q['bbox']) for q in slow['seams']],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pages',nargs='*');p.add_argument('--version',type=int,default=1);a=p.parse_args();cv2.setNumThreads(1)
    rows=manifest()['pages']
    if a.pages:rows=[r for r in rows if r['page'] in a.pages]
    run(rows,a.version)

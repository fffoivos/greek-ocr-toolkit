"""Paragraph-initial ownership: native component plus the first adjacent row.

A large letter beside two rows belongs to the first adjacent row, not whichever
row has just been recovered. Neither component size nor darkness names a font.
"""
from time import perf_counter
import cv2
import numpy as np
import pyclipper
from .geometry import roi, mask
from .contracts import bbox
from .type_context import overlaps_exclusion


def render(gray,item,items,height,*,route='slow',excluded_regions=()):
    start=perf_counter();p=np.asarray(item['polygon']);bb=bbox(item);h=height
    a,t,b,d=roi([bb[0]-4*h,bb[1]-3*h,bb[0]+2*h,bb[3]+h],gray.shape)
    step=1. if route=='slow' else max(1.,h/(12 if route=='explicit' else 5))
    g=cv2.resize(gray[t:d,a:b],(max(1,round((b-a)/step)),max(1,round((d-t)/step))),interpolation=cv2.INTER_AREA)
    sx=(b-a)/g.shape[1];sy=(d-t)/g.shape[0];hh=h/step;k=max(1,round(3*hh))|1
    paper=cv2.morphologyEx(g,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8))
    ink=((paper.astype(np.float32)-g)>.18*np.maximum(paper,1)).astype(np.uint8)
    _,labels,stats,centres=cv2.connectedComponentsWithStats(ink,8);candidates=[]
    for i,(x,y,w,dh,area) in enumerate(stats[1:],1):
        if not (1.3*hh<dh<3.5*hh and .4*hh<w<2.8*hh and area>.25*hh*hh):continue
        box=[a+x*sx,t+y*sy,a+(x+w)*sx,t+(y+dh)*sy];cx,cy=centres[i]*[sx,sy]+[a,t]
        reason='first adjacent row'
        sampling_margin=0. if route=='slow' else 2*max(sx,sy)
        if box[0]>=bb[0] or not -.5*h-sampling_margin<bb[0]-box[2]<1.2*h+sampling_margin:reason='not beside row start'
        elif not bb[1]-.6*h<box[3]<bb[3]+.4*h:reason='bottom does not meet row'
        elif box[1]>bb[1]-.6*h:reason='ordinary body height'
        elif overlaps_exclusion([[box[0],box[1]],[box[2],box[1]],[box[2],box[3]],[box[0],box[3]]],excluded_regions):reason='excluded footprint'
        else:
            for old in items:
                if old is item or old['polygon']==item['polygon']:continue
                ob=bbox(old);oy=(ob[1]+ob[3])/2
                if box[1]-.25*h<oy<min(box[3],(bb[1]+bb[3])/2)-.35*h and ob[0]<box[2]+4*h and ob[2]>box[2]+h:
                    reason='earlier adjacent row owns initial';break
                if cv2.pointPolygonTest(np.asarray(old['polygon'],np.float32),(float(cx),float(cy)),False)>=0:
                    reason='existing item owns initial';break
        candidates.append(dict(bbox=list(map(float,box)),reason=reason,accepted=reason=='first adjacent row'))
    return dict(candidates=candidates,crop=[a,t,b,d],height=h,route=route,seconds=perf_counter()-start)


def complete(gray,item,items,height,*,excluded_regions=()):
    # Fast explicit rendering nominates; original pixels must independently agree.
    fast=render(gray,item,items,height,route='explicit',excluded_regions=excluded_regions)
    if not any(c['accepted'] for c in fast['candidates']):return item,dict(fast=fast,native=None,changed=False)
    native=render(gray,item,items,height,route='slow',excluded_regions=excluded_regions)
    accepted=[c for c in native['candidates'] if c['accepted']]
    if not accepted:return item,dict(fast=fast,native=native,changed=False)
    # Exact vector union keeps the old polygon. Raster-envelope simplification
    # previously lost two dark edge pixels on the reviewed E control.
    old=bbox(item);pad=.15*height;paths=[item['polygon']]
    for c in accepted:
        x0,y0,x1,y1=c['bbox']
        paths.append([[x0-pad,y0-pad],[x1+pad,y0-pad],[x1+pad,y1+pad],[x0-pad,y1+pad]])
        # A short shoulder joins a whitespace gap beside the first body row.
        left=min(x1,old[0])-pad;right=max(x1,old[0]+height)
        top=max(old[1],y1-height);bottom=min(old[3],y1+pad)
        if bottom>top:paths.append([[left,top],[right,top],[right,bottom],[left,bottom]])
    precision=256.;clip=pyclipper.Pyclipper()
    scaled=[np.rint(np.asarray(p)*precision).astype(np.int64).tolist() for p in paths]
    scaled=[p if pyclipper.Orientation(p) else p[::-1] for p in scaled]
    clip.AddPaths(scaled,pyclipper.PT_SUBJECT,True)
    union=clip.Execute(pyclipper.CT_UNION,pyclipper.PFT_NONZERO,pyclipper.PFT_NONZERO)
    if len(union)!=1:return item,dict(fast=fast,native=native,changed=False,reason='disconnected initial remains unknown')
    poly=(np.asarray(union[0])/precision).tolist()
    if overlaps_exclusion(poly,excluded_regions):return item,dict(fast=fast,native=native,changed=False,reason='envelope crosses exclusion')
    return dict(item,polygon=poly,initial_completed=True),dict(fast=fast,native=native,changed=True)

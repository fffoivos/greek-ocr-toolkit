"""Two explicit views of unruled separation; original-pixel verification required.

R1 measures persistent white corridors beside character-scale ink. R2 nominates
recurring gaps between detector endpoints. These are layout evidence, not a
claim of physical-leaf identity. Printed-rule correction remains Q8's module.
"""
from time import perf_counter
import cv2
import numpy as np
from .geometry import quantize, height_proxy
from .contracts import bbox


def pixel_corridors(gray,height,version=2):
    h=height;H,W=gray.shape
    paper=cv2.boxFilter(gray,cv2.CV_32F,(quantize(4*h)|1,quantize(4*h)|1))
    ink=(paper-gray>255*.06).astype(np.uint8)
    integral=cv2.integral(ink,sdepth=cv2.CV_32S)
    _,labels,stats,_=cv2.connectedComponentsWithStats(ink,8)
    valid=((stats[:,3]>=.2*h)&(stats[:,3]<=2.5*h)&(stats[:,2]<=4*h)&(stats[:,4]>=.035*h*h));valid[0]=False
    support_integral=cv2.integral(valid[labels].astype(np.uint8),sdepth=cv2.CV_32S)
    bands=[]
    for y0 in range(0,H,quantize(6*h)):
        y1=min(H,y0+quantize(12*h))
        if y1-y0<6*h:continue
        density=np.diff(integral[y1]-integral[y0])/(y1-y0)
        support=np.diff(support_integral[y1]-support_integral[y0])/(y1-y0)
        edges=np.diff(np.r_[False,density<.008,False].astype(int))
        for a,b in zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)):
            if b-a<1.5*h or a<6*h or b>W-6*h:continue
            left=support[max(0,a-quantize(6*h)):a];right=support[b:min(W,b+quantize(6*h))]
            if min(left.mean(),right.mean())<.025:continue
            bands.append(dict(bbox=[a,y0,b,y1],width_h=float((b-a)/h)))
    return bands


def route1(gray,items):
    t=perf_counter();H,W=gray.shape;h=height_proxy(items,(W,H))
    scale=min(1.,8/h,1200/max(H,W));w,z=quantize(W*scale),quantize(H*scale)
    # Area sampling is a dependency, included in the returned measured time.
    small=cv2.resize(gray,(w,z),interpolation=cv2.INTER_AREA);sx=w/W;sy=z/H
    bands=pixel_corridors(small,h*sy)
    for b in bands:b['bbox']=(np.asarray(b['bbox'])/[sx,sy,sx,sy]).tolist()
    return dict(corridors=bands,height=h,seconds=perf_counter()-t)


def route2(items,size):
    t=perf_counter();h=height_proxy(items,size);b=np.asarray([bbox(q) for q in items]).reshape(-1,4)
    gaps=[]
    for i,a in enumerate(b):
        same=(np.minimum(a[3],b[:,3])-np.maximum(a[1],b[:,1]))>.5*np.minimum(a[3]-a[1],b[:,3]-b[:,1])
        js=np.flatnonzero(same&(b[:,0]>a[2]+1.5*h)&(b[:,0]<a[2]+12*h))
        if not len(js):continue
        j=int(js[np.argmin(b[js,0])]);gaps.append(dict(x0=float(a[2]),x1=float(b[j,0]),y=float((a[1]+a[3]+b[j,1]+b[j,3])/4),pair=[i,j]))
    corridors=[]
    for g in gaps:
        mates=[v for v in gaps if abs(v['y']-g['y'])<6*h and min(v['x1'],g['x1'])-max(v['x0'],g['x0'])>h]
        if len(mates)<3:continue
        a=max(v['x0'] for v in mates);z=min(v['x1'] for v in mates)
        if z-a<h:continue
        rect=[a,min(v['y'] for v in mates),z,max(v['y'] for v in mates)]
        if rect[3]-rect[1]<3*h:continue
        if any(np.max(abs(np.asarray(c['bbox'])-rect))<h for c in corridors):continue
        corridors.append(dict(bbox=rect,pairs=[v['pair'] for v in mates]))
    return dict(corridors=corridors,height=h,seconds=perf_counter()-t)

"""Explicit connected area ink; a proposal protection hint, not a rectangle eraser."""
import cv2
import numpy as np
from .geometry import quantize
from .image_evidence import components


def render(gray,height,*,samples=24):
    s=min(1.,samples/height,1800/max(gray.shape))
    raw=cv2.resize(gray,None,fx=s,fy=s,interpolation=cv2.INTER_AREA);h=height*s
    k=quantize(3*h)|1
    paper=cv2.morphologyEx(raw,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8)).astype(np.float32)
    c=np.maximum(0,paper-raw)/np.maximum(paper,1)
    ref=float(np.percentile(c,98))
    # Quantisation and paper-noise floor; grey-page texture must not become ink.
    bright=raw[raw>=np.percentile(raw,75)].astype(float)
    noise=float(1.4826*np.median(abs(bright-np.median(bright)))/255) if len(bright) else 0.
    cutoff=max(3/255,3*noise,.20*ref)
    binary=(c>cutoff).astype(np.uint8)
    step=quantize(.35*h)|1
    joined=cv2.morphologyEx(binary,cv2.MORPH_CLOSE,np.ones((step,step),np.uint8))
    labels,stats,_=components(joined);support=np.zeros_like(binary);regions=[]
    for i,(x,y,w,hh,a) in enumerate(stats):
        if w<4*h or hh<3*h or a<6*h*h:continue
        component=labels[y:y+hh,x:x+w]==i+1
        ink=binary[y:y+hh,x:x+w]>0
        selected=component&ink
        support[y:y+hh,x:x+w][selected]=1
        regions.append(dict(bbox=[float(x/s),float(y/s),float((x+w)/s),float((y+hh)/s)],
                            area_h2=float(a/h**2),ink_pixels=int(selected.sum()),kind='area-ink; text overlap unresolved'))
    return dict(regions=regions,scale=s,mask=support,raw=raw,cutoff=cutoff,
                interpretation='large connected ink, including pictures, initials, stamps, rules and touching text')


def heuristic(gray,height):
    """Route 2: dense occupied rows/columns in coarse tiles, independent of CC."""
    s=min(1,8/height,1000/max(gray.shape));raw=cv2.resize(gray,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
    h=height*s;k=quantize(3*h)|1
    paper=cv2.morphologyEx(raw,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8)).astype(np.float32)
    c=np.maximum(0,paper-raw)/np.maximum(paper,1);ref=float(np.percentile(c,98))
    binary=c>max(3/255,.20*ref);out=np.zeros(raw.shape,np.uint8);step=quantize(3*h)
    for y in range(0,raw.shape[0],step):
        for x in range(0,raw.shape[1],step):
            b=binary[y:y+step,x:x+step]
            if b.mean()>.12 and b.any(0).mean()>.90 and b.any(1).mean()>.95:out[y:y+step,x:x+step][b]=1
    return dict(mask=out,scale=s,raw=raw)

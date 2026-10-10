"""Contrast-independent stroke measurements. No readability or cause labels.

The scale is a body-height proxy supplied by the caller, not a measured font.
Relative thresholds separate attenuation from changes of stroke topology.
"""
import cv2
import numpy as np
from .geometry import roi, quantize
from .image_evidence import components, stroke_features


def measure(gray, box, height, *, samples=None, levels=(.35, .50, .70), maps=False):
    x0,y0,x1,y1=roi(box,gray.shape)
    pad=quantize(height)
    xa,ya,xb,yb=max(0,x0-pad),max(0,y0-pad),min(gray.shape[1],x1+pad),min(gray.shape[0],y1+pad)
    raw=gray[ya:yb,xa:xb]
    s=min(1.,samples/height) if samples else 1.
    if s<1: raw=cv2.resize(raw,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
    h=height*s
    k=quantize(2*h)|1
    paper=cv2.morphologyEx(raw,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8))
    contrast=np.maximum(0,paper.astype(np.float32)-raw)/np.maximum(paper,1)
    xx,yy=quantize((x0-xa)*s),quantize((y0-ya)*s)
    if x0==xa:xx=0
    if y0==ya:yy=0
    ww,hh=quantize((x1-x0)*s),quantize((y1-y0)*s)
    raw=raw[yy:yy+hh,xx:xx+ww];contrast=contrast[yy:yy+hh,xx:xx+ww]
    if not contrast.size:return dict(box=[x0,y0,x1,y1],contrast=0.,thresholds=[],height=height)
    depth=float(np.percentile(contrast,98))
    gx=cv2.Sobel(contrast,cv2.CV_32F,1,0,ksize=3)/8
    gy=cv2.Sobel(contrast,cv2.CV_32F,0,1,ksize=3)/8
    mag=cv2.magnitude(gx,gy)
    out=[]; visual=[]
    for level in levels:
        b=(contrast>max(1/255,level*depth)).astype(np.uint8)
        labels,stats,_=components(b)
        stroke=stroke_features(b)
        d=stroke['distance'];ridge=(d>0)&(d>=cv2.dilate(d,np.ones((3,3),np.uint8)))
        widths=2*d[ridge]/max(h,1e-6)
        boundary=(b>0)&(cv2.erode(b,np.ones((3,3),np.uint8))==0)
        sharp=float(np.median(mag[boundary])/max(depth,1e-6)*h) if boundary.any() else 0.
        body=[q for q in stats if .35*h<=q[3]<=1.8*h and .12*h<=q[2]<=1.6*h]
        fragments=[q for q in stats if q[4]>.003*h*h and q[3]<.35*h]
        out.append(dict(level=level,width_h=float(np.median(widths)) if len(widths) else 0.,
            width_q90_h=float(np.percentile(widths,90)) if len(widths) else 0.,
            components=len(stats),bodies=len(body),small_fragments=len(fragments),
            fragments_per_h=float(len(fragments)/max(raw.shape[1]/h,1)),
            holes=stroke['holes'],holes_per_h=float(stroke['holes']/max(raw.shape[1]/h,1)),
            fill=float(b.mean()),edge_h=sharp,readability='unknown'))
        if maps:visual.append(dict(binary=b,distance=d,skeleton=stroke['skeleton']))
    record=dict(box=[x0,y0,x1,y1],contrast=depth,height=height,scale=s,thresholds=out,
                interpretation='attenuation, stroke width and topology are independent axes')
    if maps:record.update(raw=raw,contrast_map=contrast,maps=visual)
    return record


def heuristic(gray, box, height,*,maps=False):
    """Route 2: area/perimeter width and fragment/counter counts at one level."""
    x0,y0,x1,y1=roi(box,gray.shape);raw=gray[y0:y1,x0:x1]
    if not raw.size:return dict(width_h=0.,fragments_per_h=0.,holes_per_h=0.)
    s=min(1.,12/height);raw=cv2.resize(raw,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
    h=height*s;k=quantize(2*h)|1
    paper=cv2.morphologyEx(raw,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8)).astype(np.float32)
    c=np.maximum(0,paper-raw)/np.maximum(paper,1)
    b=(c>max(1/255,.5*float(np.percentile(c,98)))).astype(np.uint8)
    # Four-direction Crofton perimeter reduces axis bias. It estimates a
    # continuous boundary, unlike counting all boundary pixel centres.
    padded=np.pad(b.astype(np.int16),1)
    hv=np.abs(np.diff(padded,axis=0)).sum()+np.abs(np.diff(padded,axis=1)).sum()
    diag=np.abs(padded[1:,1:]-padded[:-1,:-1]).sum()+np.abs(padded[1:,:-1]-padded[:-1,1:]).sum()
    perimeter=np.pi/8*(hv+diag/np.sqrt(2))
    _,stats,_=components(b)
    cs,hi=cv2.findContours(b,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    holes=sum(q[3]>=0 for q in hi[0]) if hi is not None else 0
    out=dict(width_h=float(2*b.sum()/max(perimeter,1)/h),
        fragments_per_h=float(sum(q[4]>.003*h*h and q[3]<.35*h for q in stats)/max(raw.shape[1]/h,1)),
        holes_per_h=float(holes/max(raw.shape[1]/h,1)),readability='unknown')
    if maps:out.update(binary=b,raw=raw,scale=s)
    return out

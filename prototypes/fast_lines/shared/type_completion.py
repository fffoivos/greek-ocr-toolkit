"""Original-pixel completion reused from stopped 0b052af missed_crop.

Only component ownership and envelope completion; no old recovery decisions.
"""
import cv2
import numpy as np
from .geometry import roi,mask,line_axis

def snap_components(gray, q, height, items=()):
    """Complete intersected strokes without manufacturing baseline semantics."""
    p=np.asarray(q['polygon'],float); lo=p.min(0); hi=p.max(0)
    a,b,c,d=roi([lo[0]-3*height,lo[1]-2*height,hi[0]+height,hi[1]+height],gray.shape)
    g=gray[b:d,a:c]; k=max(1,round(3*height))|1
    paper=cv2.morphologyEx(g,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8))
    ink=((paper.astype(float)-g)>.18*np.maximum(paper,1)).astype(np.uint8)
    n,labels,st,centres=cv2.connectedComponentsWithStats(ink,8)
    covered=np.zeros_like(ink); cv2.fillPoly(covered,[np.rint(p-[a,b]).astype(np.int32)],1)
    overlap=np.bincount(labels.ravel(),weights=covered.ravel(),minlength=n)
    left_columns=covered[:,max(0,int(lo[0]-a)):min(covered.shape[1],int(lo[0]-a+height))]
    local_bottom=float(np.flatnonzero(left_columns.any(1)).max()+b) if left_columns.any() else hi[1]
    shifted=[dict(q,polygon=(np.asarray(q['polygon'])-[a,b]).tolist()) for q in items]
    original=mask(shifted,g.shape,(c-a,d-b)) if items else np.zeros_like(ink)
    old_owned=np.bincount(labels.ravel(),weights=original.ravel(),minlength=n)
    expanded=covered.copy()
    axes=[]
    for item in items:
        op=np.asarray(item['polygon']);low=op.min(0);high=op.max(0)
        if low[0]<c and high[0]>a and low[1]<d and high[1]>b:
            axes.append((low[0],high[0],line_axis(item)))
    for i in range(1,n):
        x,y,w,h,area=st[i]
        # A body must principally belong to this polygon. Small detached marks
        # may intersect its edge, but touching a neighbour's descender is not
        # ownership of that neighbour's whole body.
        intersects=(.1 if h<.45*height else .5)<overlap[i]/area<1 and old_owned[i]/area<.5
        # An underboxed neighbour may expose most of a character. Ink overlap
        # alone must not reassign that whole character to the recovered row.
        cx,cy=centres[i]+[a,b];col=min(covered.shape[1]-1,max(0,round(cx-a)))
        yy=np.flatnonzero(covered[:,col])
        if len(yy):
            distance=abs(cy-(yy[0]+yy[-1])/2-b)
            if any(l<=cx<=r and abs(cy-cf[0]-cf[1]*cx)<distance for l,r,cf in axes):
                intersects=False
        # A detached large initial may belong to the preceding row. Geometry
        # alone cannot assign it; complete only intersected components.
        if intersects and .15*height<h<3.5*height and w<3*height:
            expanded[y:y+h,x:x+w][labels[y:y+h,x:x+w]==i]=1
    if np.any(expanded!=covered):
        # Dense raster envelope keeps every original polygon pixel. Sampling every
        # column prevents the sparse-vertex shrinkage observed in M3.
        xs=np.flatnonzero(expanded.any(0)); ys=np.arange(expanded.shape[0])[:,None]
        top=np.where(expanded[:,xs],ys,expanded.shape[0]).min(0)
        bottom=np.where(expanded[:,xs],ys,-1).max(0)
        p=np.vstack((np.c_[xs+a,top+b],np.c_[xs[::-1]+a,bottom[::-1]+b]))
        p=cv2.approxPolyDP(p.astype(np.float32),.02*height,True).reshape(-1,2).astype(float)
    return dict(q,polygon=p.tolist())

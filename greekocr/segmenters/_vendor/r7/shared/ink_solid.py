"""Native solid-mass evidence, separate from faintness.

A compact isolated mark is non-text only when its interior disk is wider than
ordinary strokes and half a letter body. A thin initial, hole, or nearby text
keeps the mark unknown. The renderer returns the disk and boundary explicitly.
"""
from typing import NamedTuple
from time import perf_counter
import cv2,numpy as np
from .geometry import roi

class SolidInk(NamedTuple):
    indices: np.ndarray
    disks: np.ndarray  # [N,3] native x,y,r of inscribed disk
    seconds: float


def candidates(polygons,height):
    """Route 2: geometry-only nomination, not permission to remove anything.

    Bounds and isolation are in measured letter heights. Returns [N,4] bounds
    and candidate indices; circles/initials may be nominated and need the native
    interior-disk/counter test.
    """
    h=float(height)
    if not np.isfinite(h) or h<=0:raise ValueError('positive finite letter height required')
    if len(polygons)==0:return np.empty((0,4)),np.empty(0,int)
    if len({len(p) for p in polygons})==1:
        pp=np.asarray(polygons,float);bb=np.concatenate([pp.min(1),pp.max(1)],axis=1)
    else:bb=np.asarray([[*np.min(p,axis=0),*np.max(p,axis=0)] for p in polygons],float).reshape(-1,4)
    if not len(bb):return bb,np.empty(0,int)
    wh=bb[:,2:]-bb[:,:2];found=[]
    for i in np.flatnonzero((wh.max(1)<2*h)&(wh.min(1)>h/2)):
        b=bb[i];dx=np.maximum(0,np.maximum(bb[:,0]-b[2],b[0]-bb[:,2]));dy=np.maximum(0,np.maximum(bb[:,1]-b[3],b[1]-bb[:,3]));distance=np.hypot(dx,dy);distance[i]=np.inf
        if distance.min()>=2*h:found.append(i)
    return bb,np.array(found,int)

def render(gray,polygons,height):
    start=perf_counter();h=float(height);bb,indices=candidates(polygons,h);found=[];disks=[]
    for i in indices:
        b=bb[i]
        a,y,c,d=roi(b,gray.shape);raw=gray[y:d,a:c]
        if not raw.size:continue
        scale=1.;small=raw
        level=cv2.threshold(small,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[0];m=(small<=level).astype(np.uint8)
        # Padding is essential: an all-black ROI must have a finite disk.
        dt=cv2.distanceTransform(np.pad(m,1),cv2.DIST_L2,5)[1:-1,1:-1];j,k=np.unravel_index(dt.argmax(),dt.shape);r=float(dt[j,k]/scale)
        if r<h/4:continue
        cs,hier=cv2.findContours(m,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
        if hier is not None and np.any(hier[0,:,3]>=0):continue
        # A filled mass must have no long stroke appendage. Tiny ragged-edge
        # ridge maxima are not strokes; use the enclosing disk of the same
        # connected component as its interior disk.
        _,lab=cv2.connectedComponents(m,8);yy,xx=np.where(lab==lab[j,k])
        if len(xx)==0 or np.hypot(xx-k,yy-j).max()/scale>2*r:continue
        found.append(i);disks.append([a+k/scale,y+j/scale,r])
    return SolidInk(np.asarray(found,int),np.asarray(disks,float).reshape(-1,3),perf_counter()-start)

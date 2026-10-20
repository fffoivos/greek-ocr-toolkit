"""Spatial repeated frame units. No page-edge location certifies non-text.

The native route records components in two parallel recurrent side chains and
an orthogonal chain joining them.
Exclusions contain measured border units only, never the enclosed text area.
"""
from typing import NamedTuple
from time import perf_counter
import cv2
import numpy as np
from .geometry import roi
from .ink_photometry import percentiles8

class FrameInk(NamedTuple):
    units: np.ndarray  # [N,4] float native half-open unit bounds
    sides: np.ndarray  # [S,4] float recurrent-chain corridors
    seconds: float
    bands: tuple = ()  # each [V,2], narrow measured frame corridor


def candidates(polygons,height):
    if len(polygons)==0:return np.empty((0,4))
    if len({len(p) for p in polygons})==1:
        pp=np.asarray(polygons,float);b=np.concatenate([pp.min(1),pp.max(1)],axis=1)
    else:b=np.asarray([[*np.min(p,axis=0),*np.max(p,axis=0)] for p in polygons],float).reshape(-1,4)
    if not len(b):return np.empty((0,4))
    long=np.flatnonzero(b[:,3]-b[:,1]>8*height)
    if not len(long):return np.empty((0,4))
    thin=np.array([min(cv2.minAreaRect(np.asarray(polygons[i],np.float32))[1])<2*height for i in long])
    tall=b[long];vv=tall[thin|((tall[:,3]-tall[:,1])>8*(tall[:,2]-tall[:,0]))]
    if not len(vv):return vv
    compact=b[(b[:,2]-b[:,0]<2*height)&(b[:,3]-b[:,1]<3*height)]
    extra=[]
    for a in compact:
        nearby=compact[abs((compact[:,0]+compact[:,2]-a[0]-a[2])/2)<height/2]
        if len(nearby)>=4 and nearby[:,3].max()-nearby[:,1].min()>8*height:
            extra.append([nearby[:,0].min(),nearby[:,1].min(),nearby[:,2].max(),nearby[:,3].max()])
    return np.vstack([vv,np.array(extra).reshape(-1,4)])


def chain(gray,b,h,axis):
    a,y,c,d=roi(b,gray.shape);scale=1.
    raw=cv2.resize(gray[y:d,a:c],None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA);hh=h*scale
    paper,ink=percentiles8(raw,[90,10]);mask=(raw<(paper+ink)/2).astype(np.uint8)
    _,lab,st,ct=cv2.connectedComponentsWithStats(mask,8);records=[];tiles=[];binary=[];distances=[];widths=[]
    for k,(x,z,w,t,area) in enumerate(st[1:],1):
        if not (.4*hh<min(w,t) and max(w,t)<2.5*hh and area>.08*hh*hh):continue
        if x==0 or z==0 or x+w>=raw.shape[1] or z+t>=raw.shape[0]:continue
        tile=cv2.resize((lab[z:z+t,x:x+w]==k).astype(np.float32),(24,24),interpolation=cv2.INTER_AREA).ravel()
        bm=(tile.reshape(24,24)>.5).astype(np.uint8);dd=cv2.distanceTransform(np.pad(bm,1),cv2.DIST_L2,3)[1:-1,1:-1];rr=(dd>0)&(dd>=cv2.dilate(dd,np.ones((3,3),np.uint8)))
        binary.append(bm.ravel().astype(np.float32));distances.append(cv2.distanceTransform(1-bm,cv2.DIST_L2,3).ravel());widths.append(float(np.median(dd[rr])) if rr.any() else 0.)
        tile-=tile.mean();tile/=max(np.linalg.norm(tile),1e-6)
        records.append([a+x/scale,y+z/scale,a+(x+w)/scale,y+(z+t)/scale]);tiles.append(tile)
    if len(records)<4:return np.empty((0,4))
    boxes=np.array(records);centers=(boxes[:,:2]+boxes[:,2:])/2;v=np.array(tiles,np.float32);sim=cv2.gemm(v,v,1,None,0,flags=cv2.GEMM_2_T)
    dims=boxes[:,2:]-boxes[:,:2];near=np.max(abs(dims[:,None]-dims[None,:]),2)<h/2
    aligned=abs(centers[:,None,1-axis]-centers[None,:,1-axis])<h/2
    bm=np.array(binary,np.float32);dm=np.array(distances,np.float32)
    error=cv2.gemm(dm,bm,1,None,0,flags=cv2.GEMM_2_T)/np.maximum(bm.sum(1)[None,:],1)
    matched=(sim>.75)|(np.maximum(error,error.T)<=np.minimum(np.array(widths)[:,None],np.array(widths)[None,:])/2)
    recurrent=matched&near&aligned;selected=np.flatnonzero(recurrent.sum(1)>=4)
    if len(selected)<4:return np.empty((0,4))
    coef=np.polyfit(centers[selected,axis],centers[selected,1-axis],1)
    sequence=selected[abs(centers[selected,1-axis]-np.polyval(coef,centers[selected,axis]))<h/2]
    order=sequence[np.argsort(centers[sequence,axis])];gaps=np.diff(centers[order,axis]);period=np.median(gaps)
    # Missing/damaged individual units may interrupt chains, not create a bridge.
    cuts=np.r_[0,np.flatnonzero((np.minimum(abs(gaps-period),abs(gaps-2*period))>h/2)|(boxes[order[1:],axis]-boxes[order[:-1],axis+2]>h/2))+1,len(order)];runs=[order[i:j] for i,j in zip(cuts[:-1],cuts[1:]) if j-i>=4]
    return boxes[np.concatenate(runs)] if runs else np.empty((0,4))


def render(gray,polygons,height):
    start=perf_counter();h=float(height);vv=candidates(polygons,h);empty=np.empty((0,4))
    if not len(vv):return FrameInk(empty,empty,perf_counter()-start)
    # Consolidate fragments of the same side before observing native units.
    records=[]
    for b in sorted(vv.tolist()):
        if any(abs((b[0]+b[2])/2-(q[0]+q[2])/2)<h for q,_ in records):continue
        z=[b[0]-.5*h,0,b[2]+.5*h,gray.shape[0]];uu=chain(gray,z,h,1)
        if len(uu)>=8 and uu[:,3].max()-uu[:,1].min()>8*h:records.append((z,uu))
    sides=[];units=[];bands=[]
    for i,(a,aa) in enumerate(records):
      for b,bb in records[i+1:]:
        if abs((a[0]+a[2]-b[0]-b[2])/2)<8*h:continue
        top=min(aa[:,1].min(),bb[:,1].min());bottom=max(aa[:,3].max(),bb[:,3].max())
        if bottom-top<8*h:continue
        x0=min(aa[:,0].min(),bb[:,0].min());x1=max(aa[:,2].max(),bb[:,2].max());cross=[]
        for y in (top,bottom):
            uu=chain(gray,[x0-h,y-2*h,x1+h,y+2*h],h,0)
            if len(uu)>=4 and uu[:,2].max()-uu[:,0].min()>8*h:cross.append(uu)
        if cross:
            units.extend([aa,bb,*cross]);sides.extend([a,b])
            ys=[np.median((u[:,1]+u[:,3])/2) for u in cross];yl=(min(top,*ys),max(bottom,*ys));xl=(min(np.median((aa[:,0]+aa[:,2])/2),np.median((bb[:,0]+bb[:,2])/2)),max(np.median((aa[:,0]+aa[:,2])/2),np.median((bb[:,0]+bb[:,2])/2)))
            bands.extend([trace(gray,aa,1,yl,h),trace(gray,bb,1,yl,h),*[trace(gray,u,0,xl,h) for u in cross]])
    return FrameInk(np.unique(np.concatenate(units),axis=0) if units else empty,np.array(sides).reshape(-1,4),perf_counter()-start,tuple(bands))


def trace(gray,units,axis,limits,height):
    """Observe native transverse ink inside the recurrent-unit corridor.

    Only an orthogonal witnessed side supplies an endpoint; the interior of the
    frame is never sampled. This corridor is decision evidence: exclude_whole
    still requires every observed body in a segment to belong to the frame.
    """
    u=np.asarray(units);major=(u[:,axis]+u[:,axis+2])/2;minor=(u[:,1-axis]+u[:,3-axis])/2;order=np.argsort(major);major=major[order];minor=minor[order]
    slope=np.polyfit(major,minor,1);ts=np.arange(max(0,int(np.floor(limits[0]))),min(gray.shape[1-axis],int(np.ceil(limits[1]))+1))
    centers=np.interp(ts,major,minor);outside=(ts<major.min())|(ts>major.max());centers[outside]=np.polyval(slope,ts[outside])
    half=np.median(u[:,3-axis]-u[:,1-axis])/2+height/20
    lo=[];hi=[]
    for t,c in zip(ts,centers):
        l=max(0,int(np.floor(c-half)));r=min(gray.shape[axis],int(np.ceil(c+half))+1);v=gray[l:r,t] if axis==0 else gray[t,l:r]
        if not len(v):lo.append(c-half);hi.append(c+half);continue
        hit=np.flatnonzero(v<(float(v.max())+float(v.min()))/2)
        lo.append(l+hit.min()-1 if len(hit) else c-half);hi.append(l+hit.max()+2 if len(hit) else c+half)
    # Native ragged edges are not simplified through the ink.
    a=np.c_[ts,lo] if axis==0 else np.c_[lo,ts];b=np.c_[ts,hi] if axis==0 else np.c_[hi,ts]
    return np.vstack([a,b[::-1]])

def exclude_whole(gray,items,field,height):
    """Conservative whole-segment adapter; mixed segments remain unchanged.

    Recurrent perimeter units must own every observed letter-sized body. No
    clipping, body-only residual filtering or frame-interior exclusion occurs.
    This deliberately leaves mixed border/text boxes for later segmentation.
    """
    from shapely.geometry import Polygon,Point
    from shapely.ops import unary_union
    from .ink_faintness import components
    if not field.bands:return dict(items=items,removed=[],exclusions=[])
    mask=unary_union([Polygon(p).buffer(0) for p in field.bands]);kept=[];removed=[]
    for i,q in enumerate(items):
        poly=Polygon(np.asarray(q['polygon'],float))
        if not poly.intersects(mask):kept.append(q);continue
        bodies=[g for g in components(gray,q,height,route='localized') if g['body']]
        if bodies and all(mask.covers(Point((g['bbox'][0]+g['bbox'][2])/2,(g['bbox'][1]+g['bbox'][3])/2)) for g in bodies):removed.append(i)
        else:kept.append(q)
    return dict(items=kept,removed=removed,exclusions=[dict(items[i],removal='recurrent frame') for i in removed])

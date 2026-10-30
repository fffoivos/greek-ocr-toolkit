"""Local type pitch/phase, actual ink, and empty slots. No page-name inputs.

A type lattice nominates; it cannot decide foreground ownership. Entire absent
blocks, irregular poetry and severe curl remain explicitly outside its support.
"""
from time import perf_counter
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from .contracts import bbox,rect
from .geometry import height_proxy,line_axis,roi
from .type_profiles import mode,measure_line


def blocks(items,size):
    h=height_proxy(items,size);b=np.asarray([bbox(q) for q in items],float).reshape(-1,4)
    axes=np.asarray([line_axis(q) for q in items]).reshape(-1,2)
    heights=np.asarray([min(cv2.minAreaRect(np.asarray(q['polygon'],np.float32))[1])*.5 for q in items])
    centres=b[:,[0,1]]*.5+b[:,[2,3]]*.5 if len(b) else np.empty((0,2))
    groups=[]
    for i in np.argsort(centres[:,1]):
        if b[i,2]-b[i,0]<8*heights[i]:continue
        match=None
        for g in groups:
            j=g['members'][-1];ov=min(b[i,2],b[j,2])-max(b[i,0],b[j,0])
            if (ov>.65*min(b[i,2]-b[i,0],b[j,2]-b[j,0]) and
                abs(centres[i,0]-centres[j,0])<.3*max(b[i,2]-b[i,0],b[j,2]-b[j,0]) and
                .6<heights[i]/max(heights[j],1e-6)<1.67 and
                centres[i,1]-centres[j,1]<8*max(heights[i],heights[j])):
                match=g;break
        if match is None:groups.append(dict(members=[int(i)]))
        else:match['members'].append(int(i))
    out=[]
    for g in groups:
        ids=np.array(g['members']);height=float(np.median(heights[ids]))
        if len(ids)<4:continue
        a=float(np.quantile(b[ids,0],.15));d=float(np.quantile(b[ids,2],.85));xm=(a+d)/2
        slope=float(np.median(axes[ids,1]));ys=axes[ids,0]+axes[ids,1]*xm
        order=np.argsort(ys);ys=ys[order];ids=ids[order]
        keep=np.r_[True,np.diff(ys)>.6*height];ys=ys[keep];ids=ids[keep]
        diffs=np.diff(ys);ok=diffs[(diffs>height)&(diffs<5*height)]
        pitch,count=mode(ok,height)
        if pitch is None or count<2:continue
        phase=float(ys[0]);index=np.rint((ys-phase)/pitch)
        residual=(ys-phase)-index*pitch
        out.append(dict(id=len(out),members=ids.tolist(),height=height,pitch=pitch,phase=phase,
            x0=a,x1=d,xref=xm,slope=slope,centres=ys.tolist(),residual_xh=(residual/height).tolist(),
            y0=float(ys[0]),y1=float(ys[-1]),source='local detector axes; not semantic baselines'))
    return out


def gaps(blocks,items,version=1):
    bounds=np.asarray([bbox(q) for q in items],float).reshape(-1,4)
    slots=[]
    for b in blocks:
        h=b['height'];p=b['pitch'];ys=b['centres']
        for k,(a,d) in enumerate(zip(ys[:-1],ys[1:])):
            n=int(round((d-a)/p))
            if n<2 or n>4 or abs((d-a)-n*p)>.4*h:continue
            for j in range(1,n):
                cy=a+j*(d-a)/n;x0=b['x0'];x1=b['x1']
                # Existing short headings also own a slot; do not mistake missing
                # long boxes for missing lines. This tests all input items.
                owned=np.flatnonzero((bounds[:,0]<x1)&(bounds[:,2]>x0)&
                       (abs((bounds[:,1]+bounds[:,3])/2-cy)<.65*h))
                if len(owned):continue
                slots.append(dict(block=b['id'],y=cy,height=h,pitch=p,slope=b['slope'],x0=x0,x1=x1,xref=b['xref'],
                                  neighbours=[b['members'][k],b['members'][k+1]],status='slot with no box'))
    return slots


def raw_rows(gray,block,*,samples=None):
    """Dense explicit whole-block row projection; includes every ink ridge."""
    h=block['height'];step=1. if samples is None else max(1.,h/samples)
    xs=np.arange(max(0,block['x0']),min(gray.shape[1],block['x1']),step,dtype=np.float32)
    yy=np.arange(max(0,block['y0']-h),min(gray.shape[0],block['y1']+h),step,dtype=np.float32)
    mx=np.broadcast_to(xs,(len(yy),len(xs))).copy()
    my=yy[:,None]+block['slope']*(xs[None,:]-block['xref'])
    patch=cv2.remap(gray,mx,my.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=255)
    k=max(1,int(3*h/step))|1
    paper=cv2.morphologyEx(patch,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8));ink=(paper.astype(float)-patch)/np.maximum(paper,1)>.18
    density=gaussian_filter1d(ink.mean(1),max(.5,.12*h/step))
    peaks,_=find_peaks(density,prominence=max(.025,float(density.max())*.14),distance=max(1,int(h/step)))
    return dict(y=yy.tolist(),density=density.tolist(),peaks=[float(yy[i]) for i in peaks],
                rows=[dict(y=float(yy[i]),support=float(density[i])) for i in peaks])


def inspect_slot(gray,slot,items,*,dense=False,version=1):
    h=slot['height'];x0=slot['x0'];x1=slot['x1'];y=slot['y'];slope=slot['slope'];xm=slot['xref']
    step=1. if dense else max(1.,h/12)
    xs=np.arange(max(0,x0),min(gray.shape[1],x1),step,dtype=np.float32)
    offsets=np.arange(-.8*h,.8*h+step,step,dtype=np.float32)
    mx=np.broadcast_to(xs,(len(offsets),len(xs))).copy()
    my=(y+slope*(xs[None,:]-xm)+offsets[:,None]).astype(np.float32)
    patch=cv2.remap(gray,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=255)
    k=max(1,int(3*h/step))|1;paper=cv2.morphologyEx(patch,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8))
    ink=((paper.astype(np.float32)-patch)/np.maximum(paper,1)>.18).astype(np.uint8)
    n,labels,s,c=cv2.connectedComponentsWithStats(ink,8);s=s[1:];c=c[1:];bh=h/step
    ii=np.flatnonzero((s[:,3]>.45*bh)&(s[:,3]<1.6*bh)&(s[:,2]>.1*bh)&(s[:,2]<3*bh)&(s[:,4]>.06*bh*bh))
    points=[];boxes=[]
    for i in ii:
        cx=float(xs[0]+c[i,0]*step);cy=float(y+slope*(cx-xm)+offsets[0]+c[i,1]*step)
        points.append([cx,cy]);a,t,w,d,_=s[i];gx=float(xs[0]+a*step);off=float(offsets[0]+t*step)
        boxes.append([gx,float(y+slope*(gx-xm)+off),gx+w*step,float(y+slope*(gx-xm)+off+d*step)])
    if len(points)>=5:
        p=np.asarray(points);z=p[:,1]-slope*(p[:,0]-xm);res=float(np.quantile(abs(z-np.median(z)),.9)/h)
        span=float(np.ptp(p[:,0])/h)
    else:res=None;span=0
    contact_support=0;contact_residual=None
    if len(points)>=5:
        st=s[ii];bottom=st[:,1]+st[:,3];base,contact_support=mode(bottom,bh)
        near=abs(bottom-base)<.25*bh
        contact_residual=float(np.quantile(abs(bottom[near]-base),.9)/bh) if near.any() else None
    supported=len(points)>=5 and span>=5 and (res<.3 if version<2 else contact_support>=5 and contact_support>=len(points)*.5)
    if version>=2 and supported:
        # Record the actually measured body centre, not an ideal grid position.
        centres=np.asarray(points);slot=dict(slot,measured_y=float(np.median(centres[:,1]-slope*(centres[:,0]-xm))))
    owned=point_ownership(points,items) if version>=3 else []
    return dict(slot,owned_centres=owned,owned_fraction=float(np.mean(owned)) if owned else 0.,components=boxes,body_centres=points,bodies=len(points),residual_xh=res,span_xh=span,
                contact_support=contact_support,contact_residual_xh=contact_residual,supported=bool(supported),source='original body ink' if dense else '12 samples/body component witness')


def analyze(gray,items,*,route='heuristic',version=1):
    start=perf_counter();bb=blocks(items,(gray.shape[1],gray.shape[0]));ss=gaps(bb,items,version)
    evidence=[inspect_slot(gray,s,items,dense=route=='slow',version=version) for s in ss]
    rows=[dict(block=b['id'],**raw_rows(gray,b,samples=None if route=='slow' else 12)) for b in bb] if route!='heuristic' else []
    return dict(blocks=bb,slots=evidence,raw_rows=rows,seconds=perf_counter()-start,route=route,
                caveat='grid membership does not identify front ink; no line without measured support')


def point_ownership(points,items):
    """Geometric ownership at measured body centres; no photometric front claim."""
    polygons=[np.asarray(q['polygon'],np.float32) for q in items if not q.get('discounted')]
    pts=[tuple(map(float,xy)) for xy in points]
    if not polygons:return [False for _ in pts]
    if len(pts)<8:
        return [any(cv2.pointPolygonTest(p,xy,False)>=0 for p in polygons) for xy in pts]
    # Bounds are only an exact negative test. Batch the point census before
    # asking the unchanged float32 OpenCV predicate about each possible hit.
    xy=np.asarray(pts,np.float32);owned=np.zeros(len(pts),bool)
    for p in polygons:
        lo=p.min(0);hi=p.max(0)
        ids=np.flatnonzero(~owned & (xy[:,0]>=lo[0]) & (xy[:,0]<=hi[0]) & (xy[:,1]>=lo[1]) & (xy[:,1]<=hi[1]))
        for i in ids:owned[i]=cv2.pointPolygonTest(p,pts[i],False)>=0
    return owned.tolist()

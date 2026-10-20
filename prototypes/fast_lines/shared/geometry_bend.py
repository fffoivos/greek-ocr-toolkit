"""Column bend observations. No page ownership partition or detector rerun.

All coordinates are native pixels; boxes are [N,4], paths [N,2]. The common
field has cubic x and quadratic y terms. Row intercepts are nuisance variables,
not free per-row bends. Photometry is deliberately absent from this scout.
"""
from typing import NamedTuple
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks


class Bend(NamedTuple):
    bounds: np.ndarray
    coefficients: np.ndarray
    height: float
    pitch: float
    phases: np.ndarray
    side: int                 # -1 left, +1 right, 0 flat/unknown
    support: np.ndarray       # coherent row phases


from .geometry_regions import columns


def basis(x,y,bounds):
    a,b,c,d=bounds;u=(np.asarray(x)-(a+c)/2)/max(1,(c-a)/2);v=(np.asarray(y)-(b+d)/2)/max(1,(d-b)/2)
    left=np.minimum(u+.4,0)**3;right=np.maximum(u-.4,0)**3
    return np.stack([u,u*v,u*v*v,left,left*v,left*v*v,right,right*v,right*v*v],axis=-1)


def offset(field,x,y):return basis(x,y,field.bounds)@field.coefficients


def phase(field,x,y):
    z=np.asarray(y,dtype=float).copy()
    for _ in range(3):z=np.asarray(y)-offset(field,x,z)
    return z


def _fit(bounds,paths,h):
    # Each path contributes equally regardless of its length. Robust residuals
    # reject ridge switches rather than fitting their row jump as curvature.
    refs=np.array([np.median(p[:,1]) for p in paths]);coef=np.zeros(9)
    for _ in range(5):
        A=[];Y=[];weights=[]
        for p,y in zip(paths,refs):
            m=basis(p[:,0],np.full(len(p),y),bounds);z=p[:,1]
            A.append(m-m.mean(0));Y.append(z-z.mean());weights.extend([1/len(p)]*len(p))
        A=np.concatenate(A);Y=np.concatenate(Y);res=Y-A@coef
        w=np.sqrt(np.asarray(weights)*np.minimum(1.,h/4/np.maximum(abs(res),1e-8)))
        coef=np.linalg.lstsq(A*w[:,None],Y*w,rcond=1e-6)[0]
        refs=np.array([np.median(p[:,1]-basis(p[:,0],np.full(len(p),y),bounds)@coef) for p,y in zip(paths,refs)])
    return coef,refs


def scout(pm,boxes,size,edge,rules=(),gray=None):
    """Map-ridge-only nomination, after columns and their own affine fit."""
    h=edge['height'];regions=columns(pm,boxes,size,h,rules,gray);out=[]
    measured,_=bodies(gray,h,12) if gray is not None and edge.get('trigger',False) else (np.empty((0,4)),None)
    for bounds in regions:
        paths=[];seen=set();a,b,c,d=bounds
        local=measured[(measured[:,0]>=a)&(measured[:,2]<=c)]
        bh=float(np.median(local[:,3]-local[:,1])) if len(local) else h
        for rec in edge['records']:
            if rec['line'] in seen:continue
            p=np.asarray(rec['path']);bb=boxes[rec['line']]
            if not (a<=np.mean(bb[[0,2]])<c) or bb[0]<a-h or bb[2]>c+h:continue
            p=p[(p[:,0]>=max(a,bb[0]-2*h))&(p[:,0]<=min(c,bb[2]+2*h))]
            if len(p)<7 or np.ptp(p[:,0])<8*h:continue
            # A branch discontinuity is not one row ridge.
            if np.any(abs(np.diff(p[:,1]))>h):continue
            seen.add(rec['line']);paths.append(p)
        if len(paths)<3:
            out.append(Bend(bounds,np.zeros(9),h,2*h,np.empty(0),0,np.empty(0)));continue
        # Text support, not the outer sheet margins, defines x normalisation.
        bounds=np.array([max(a,min(p[:,0].min() for p in paths)-h),b,min(c,max(p[:,0].max() for p in paths)+h),d])
        coef,refs=_fit(bounds,paths,h)
        ordered=np.sort(refs);delta=np.diff(ordered);usable=delta[(delta>h)&(delta<4*h)];pitch=float(np.median(usable)) if len(usable) else 2*h
        f=Bend(bounds,coef,h,pitch,ordered,0,np.empty(0));signs=[];support=[]
        slopes=[];mid=(bounds[0]+bounds[2])/2;span=bounds[2]-bounds[0]
        for p in paths:
            inner=abs(p[:,0]-mid)<span/4
            if inner.sum()>=3:slopes.append(np.polyfit(p[inner,0]-mid,p[inner,1],1)[0])
        affine=float(np.median(slopes)) if slopes else 0.
        for p,y in sorted(zip(paths,refs),key=lambda q:q[1]):
            inner=abs(p[:,0]-mid)<span/4
            if inner.sum()<3:
                signs.append((0,0));support.append(y);continue
            residual=p[:,1]-affine*(p[:,0]-mid)
            residual-=np.median(residual[inner]);residual=gaussian_filter1d(residual,1.)
            left=residual[p[:,0]<bounds[0]+span/4];right=residual[p[:,0]>bounds[2]-span/4]
            ends=[float(np.median(v[:3] if side<0 else v[-3:])) if len(v)>=3 else 0. for v,side in ((left,-1),(right,1))]
            side=-1 if abs(ends[0])>abs(ends[1]) else 1;dev=ends[0] if side<0 else ends[1]
            end=left if side<0 else right
            monotone=len(end)>=3 and (np.all(np.diff(end)>=-bh/8) or np.all(np.diff(end)<=bh/8))
            signs.append((side,int(np.sign(dev))) if abs(dev)>.35*bh and monotone else (0,0));support.append(y)
        ids=[]
        for i in range(2,len(signs)):
            if signs[i][0] and signs[i]==signs[i-1]==signs[i-2] and support[i]-support[i-2]<3*pitch:ids.extend([i-2,i-1,i])
        ids=np.unique(ids).astype(int);side=signs[ids[0]][0] if len(ids) else 0
        out.append(f._replace(side=side,support=np.array(support)[ids]))
    return out


def bodies(gray,h,target=12):
    """Reduced geometry-only census; normal ink is a separate native contract.

    First measure the modal component body height, then sample at 12 pixels per
    measured body, not 12 per detector height. Native route uses target=None.
    """
    scale=min(1.,(target or h)/h)
    def census(scale):
        raw=cv2.resize(gray,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA) if scale<1 else gray
        k=max(3,round(2*h*scale)|1);paper=cv2.morphologyEx(raw,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8))
        ink=cv2.threshold(cv2.subtract(paper,raw),0,1,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        _,labels,st,c=cv2.connectedComponentsWithStats(ink,8)
        bb=np.c_[st[:,0],st[:,1],st[:,0]+st[:,2],st[:,1]+st[:,3]]/scale
        ok=(st[:,3]/scale>h/3)&(st[:,3]/scale<2*h)&(st[:,2]/scale>h/12)&(st[:,2]/scale<3*h)&(st[:,4]/scale**2>h*h/40);ok[0]=False
        return bb[ok],c[ok]/scale,labels,st,ok
    bb,cc,*_=census(scale)
    bh=float(np.median(bb[:,3]-bb[:,1])) if len(bb) else h
    if target and scale<1 and bh*scale<target*.9:
        scale=min(1.,target/bh);bb,cc,*_=census(scale)
    return bb,cc


def place(field,bb,cc):
    """Rows are peaks of observed letter phase, never pitch extrapolations."""
    a,b,c,d=field.bounds;ok=(cc[:,0]>=a)&(cc[:,0]<c)&(cc[:,1]>=b)&(cc[:,1]<d)
    bb=bb[ok];cc=cc[ok]
    if len(bb)<3:return field,np.empty((0,4)),np.empty(0,int)
    heights=bb[:,3]-bb[:,1];h=float(np.median(heights));keep=(heights>=2*h/3)&(heights<2*h);bb=bb[keep];cc=cc[keep]
    z=phase(field,cc[:,0],cc[:,1]);step=max(1,h/8);hist=np.zeros(int(d/step)+2);np.add.at(hist,np.clip(np.rint(z/step).astype(int),0,len(hist)-1),1)
    hist=gaussian_filter1d(hist,max(1,h/4/step));peaks,_=find_peaks(hist,distance=max(1,round(1.2*h/step)),height=3/(max(1,h/4/step)*2.51))
    phases=peaks*step;delta=np.diff(phases);delta=delta[(delta>h)&(delta<4*h)];pitch=float(np.median(delta)) if len(delta) else field.pitch
    ids=np.argmin(abs(z[:,None]-phases),axis=1) if len(phases) else np.full(len(z),-1)
    if len(phases):
        # Body-centre registration refines the SAME low-order column field.
        # Independent row constants are fixed from the profile, never bends.
        for _ in range(4):
            ids=np.argmin(abs(z[:,None]-phases),axis=1);good=abs(z-phases[ids])<h/2
            A=basis(cc[good,0],phases[ids[good]],field.bounds);Y=cc[good,1]-phases[ids[good]]
            res=Y-A@field.coefficients;w=np.sqrt(np.minimum(1.,h/6/np.maximum(abs(res),1e-9)))
            coef=np.linalg.lstsq(A*w[:,None],Y*w,rcond=1e-6)[0]
            field=field._replace(coefficients=coef);z=phase(field,cc[:,0],cc[:,1])
        ids=np.argmin(abs(z[:,None]-phases),axis=1);ids[abs(z-phases[ids])>h/2]=-1
    return field._replace(height=h,pitch=pitch,phases=phases),bb,ids

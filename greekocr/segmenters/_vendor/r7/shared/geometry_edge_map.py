"""Fast edge-strip rendering from Paddle's already charged probability map.

The sampled outer third extends beyond the box by another third. An interior
straight tangent is compared with continuing row support; neighboring endpoints
must agree. Native page-field observations must confirm every nomination.
"""
from time import perf_counter
import cv2,numpy as np
from .geometry import height_proxy,line_axis
from .contracts import bbox


def scout(pm,items,size):
    start=perf_counter();h=height_proxy(items,size);W,H=size;ah,aw=pm.shape;records=[]
    for i,q in enumerate(items):
        a,b,c,d=bbox(q);w=c-a
        if w<12*h or d-b>w or q.get('discounted'):continue
        axis=line_axis(q);mid=(a+c)/2;offsets=np.linspace(-4*h,4*h,65)
        xs=np.linspace(max(0,a-w/3),min(W-1,c+w/3),max(9,round(5*w/(3*h))+1));ys=axis[0]+axis[1]*xs
        mx=np.broadcast_to(xs[None,:]*aw/W,(len(offsets),len(xs))).astype(np.float32);my=((ys[None,:]+offsets[:,None])*ah/H).astype(np.float32)
        sample=cv2.remap(pm,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT);anchor=int(np.argmin(abs(xs-mid)))
        # A narrow peak rendering is intentionally cheap and lossy. At a row
        # switch it may abstain or nominate; it cannot authorize a correction.
        allowed=abs(offsets)<h
        ids=np.argmax(np.where(allowed[:,None],sample,-1),axis=0)
        strength=sample[ids,np.arange(len(xs))]
        # .3 is the existing Paddle map binarization probability, not a pixel
        # distance or calibrated correctness probability. All distances use h.
        positions=ys+offsets[ids];positions[strength<.3]=np.nan
        inner=np.isfinite(positions)&(xs>a+w/3)&(xs<c-w/3)
        if inner.sum()<4:continue
        xx=(xs[inner]-mid)/h;yy=positions[inner]/h;dx=xx-xx.mean();slope=float(np.dot(dx,yy-yy.mean())/max(1e-9,np.dot(dx,dx)));coef=[float(yy.mean()-slope*xx.mean()),slope]
        for side,select in [('left',np.isfinite(positions)&(xs<a+w/3)),('right',np.isfinite(positions)&(xs>c-w/3))]:
            ids=np.flatnonzero(select)
            if len(ids)<3:continue
            residual=positions[ids]/h-np.polynomial.polynomial.polyval((xs[ids]-mid)/h,coef)
            smooth=np.convolve(residual,np.ones(3)/3,mode='valid');j=int(np.argmax(abs(smooth)));end=ids[j:j+3];ex=float(xs[end].mean());ey=float(positions[end].mean());dev=float(smooth[j])
            records.append(dict(line=i,side=side,inner=[mid,float(coef[0]*h)],edge=[ex,ey],window=[max(0,a-w/3) if side=='left' else c-w/3,b-4*h,a+w/3 if side=='left' else min(W,c+w/3),d+4*h],inner_slope=float(coef[1]),edge_slope=0.,path=np.c_[xs[np.isfinite(positions)],positions[np.isfinite(positions)]].tolist(),deviation_h=dev,candidate=bool(abs(dev)>.35)))
    nominated=[]
    for r in records:
        near=[q for q in records if q['candidate'] and q['side']==r['side'] and abs(q['edge'][0]-r['edge'][0])<6*h and abs(q['edge'][1]-r['edge'][1])<8*h and q['deviation_h']*r['deviation_h']>0]
        r['neighbours']=[q['line'] for q in near if q is not r];r['coherent']=r['candidate'] and len(near)>=3
        if r['coherent']:nominated.append(r['line'])
    return dict(height=h,route='map heuristic',records=records,nominated=sorted(set(nominated)),trigger=bool(nominated),seconds=perf_counter()-start)

"""Dense seam continuation; returns visible darkness and outline contacts apart."""
import cv2
import numpy as np
from scipy.signal import find_peaks
from ..shared.geometry import quantize


def trace(dark,height,sx,sy,version=3):
    h=height*sy;H,W=dark.shape
    density=cv2.boxFilter(dark.astype(np.float32),cv2.CV_32F,(quantize(.3*h),quantize(h)))
    profile=np.quantile(np.array([b.mean(0) for b in np.array_split(dark,24)]),.25,axis=0)
    peaks,_=find_peaks(profile,height=.1,distance=max(1,quantize(2*h)))
    records=[]
    for seed in peaks:
        if not .2*W<seed<.8*W:continue
        ys=np.arange(0,H,max(1,quantize(.5*h)));xs=np.full(len(ys),float(seed));observed=np.zeros(len(ys),bool)
        anchor=len(ys)//2
        for direction in (-1,1):
            previous=float(seed)
            for j in range(anchor,len(ys) if direction==1 else -1,direction):
                a=max(0,int(previous-h));b=min(W,int(previous+h)+1)
                score=density[ys[j],a:b];ix=np.arange(a,b)
                # Follow a physical ridge locally. Reward cannot buy a jump >h.
                objective=score-.15*abs(ix-previous)/h
                x=int(ix[np.argmax(objective)]);observed[j]=density[ys[j],x]>.1
                xs[j]=x;previous=x
        if observed.mean()<.5:continue
        keep=np.flatnonzero(observed);lo,hi=int(keep[0]),int(keep[-1]);edge_contacts=[]
        for j in (lo,hi):
            cx=xs[j];end=ys[j];ya=max(0,int(end-2*h));yb=min(H,int(end+2*h)+1);contacts=[]
            for xa,xb in [(cx-8*h,cx-2*h),(cx+2*h,cx+8*h)]:
                xa=max(0,int(xa));xb=min(W,int(xb))
                if xb>xa:
                    p=dark[ya:yb,xa:xb].mean(1);idx=int(np.argmax(p))
                    contacts.append(dict(point=[float(cx/sx),float((ya+idx)/sy)],strength=float(p[idx])))
            edge_contacts.append(contacts)
        offsets=np.r_[np.linspace(-2*h,-h,9),np.linspace(h,2*h,9)]
        mx=(xs[:,None]+offsets[None,:]).astype(np.float32);my=np.broadcast_to(ys[:,None],mx.shape).astype(np.float32)
        flank=cv2.remap(dark,mx,my,cv2.INTER_NEAREST,borderMode=cv2.BORDER_REPLICATE).mean(1)
        interior=(ys>.1*H)&(ys<.9*H)&observed
        isolation=float((flank[interior]<.08).mean()) if interior.any() else 0.
        outer=bool(ys[lo]<.15*H and ys[hi]>.8*H and all(max([z['strength'] for z in e] or [0])>.5 for e in edge_contacts))
        if version>=4:outer=outer and isolation>.85
        records.append(dict(isolation=isolation,flank_density=flank[lo:hi+1].tolist(),path=np.c_[xs[lo:hi+1]/sx,ys[lo:hi+1]/sy].tolist(),observed=observed[lo:hi+1].tolist(),
            bbox=[float(xs[lo:hi+1].min()/sx),float(ys[lo]/sy),float(xs[lo:hi+1].max()/sx),float(ys[hi]/sy)],
            edge_contacts=edge_contacts,outer_contact=outer,warning='Recurring darkness plus edge contact is not proof of two physical leaves.'))
    return records

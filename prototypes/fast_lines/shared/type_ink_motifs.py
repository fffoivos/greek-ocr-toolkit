# Snapshot from track B round4; see features_type/reuse_round4.json.
"""Explicit strip repetition and connected support, independent of ownership."""
import cv2,numpy as np
from scipy.signal import find_peaks
from .geometry import roi,quantize,line_axis
from .image_evidence import components


def strip(gray,item,height,*,samples=16):
    from .contracts import bbox
    b=bbox(item);axis=line_axis(item)
    scale=min(1.,samples/height);w=quantize((b[2]-b[0])*scale);h=quantize((b[3]-b[1])*scale)
    xs=np.linspace(b[0],b[2],w,dtype=np.float32)
    offsets=(np.arange(h,dtype=np.float32)-(h-1)/2)/scale
    mx=np.broadcast_to(xs[None],(h,w));my=axis[0]+axis[1]*xs[None]+offsets[:,None]
    raw=cv2.remap(gray,mx,my.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
    return raw,scale


def inspect(gray,item,height):
    raw,s=strip(gray,item,height)
    h=height*s
    if raw.shape[1]<5*h:return dict(repeat=0.,connected=0.,lag_h=0.),raw
    a=(255-raw.astype(np.float32))/255
    a-=np.mean(a,axis=1,keepdims=True)
    start=quantize(.7*h);stop=min(quantize(8*h),a.shape[1]//4)
    vals=[]
    for lag in range(start,stop):
        left,right=a[:,:-lag],a[:,lag:]
        vals.append(float(np.sum(left*right)/max(np.linalg.norm(left)*np.linalg.norm(right),1e-6)))
    if len(vals)<3:return dict(repeat=0.,connected=0.,lag_h=0.),raw
    peaks,_=find_peaks(vals,prominence=.04)
    if not len(peaks):return dict(repeat=0.,connected=0.,lag_h=0.),raw
    best=int(max(peaks,key=lambda j:vals[j]));lag=best+start
    paper,core=np.percentile(raw,[90,10]);binary=(raw<paper-.5*(paper-core)).astype(np.uint8)
    _,stats,_=components(binary)
    connected=max((q[2]/raw.shape[1] for q in stats),default=0.)
    # Local agreement checks that one repeated patch does not dominate a prose strip.
    local=[]
    for x in range(0,a.shape[1]-2*lag,lag):
        l,r=a[:,x:x+lag],a[:,x+lag:x+2*lag]
        local.append(float(np.sum(l*r)/max(np.linalg.norm(l)*np.linalg.norm(r),1e-6)))
    return dict(repeat=vals[best],lag_h=lag/h,lag=lag/s,connected=connected,
                local=local,peaks=[dict(lag_h=(j+start)/h,correlation=vals[j]) for j in peaks]),raw

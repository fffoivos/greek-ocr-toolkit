"""S3: coordinate/sampling operators, not a second line detector."""
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from .contracts import bbox
from .geometry_memo import entry

def quantize(length): return max(1,int(round(length)))

def roi(b,shape):
    h,w=shape[:2]; x0,y0,x1,y1=b
    return [max(0,min(w-1,int(np.floor(x0)))),max(0,min(h-1,int(np.floor(y0)))),
            max(1,min(w,int(np.ceil(x1)))),max(1,min(h,int(np.ceil(y1))))]

def mask(items,shape,page_size):
    h,w=shape; pw,ph=page_size; out=np.zeros(shape,np.uint8)
    for q in items:
        if q.get('discounted'): continue
        p=np.rint(np.asarray(q['polygon'])*[w/pw,h/ph]).astype(np.int32)
        cv2.fillPoly(out,[p],1)
    return out

def robust_fit(x,y,degree=1):
    x,y=np.asarray(x,float),np.asarray(y,float)
    degree=min(degree,max(0,len(x)-1)); weights=np.ones(len(x))
    for _ in range(4):
        coef=np.polynomial.polynomial.polyfit(x,y,degree,w=weights)
        r=y-np.polynomial.polynomial.polyval(x,coef); scale=max(1e-6,1.4826*np.median(abs(r-np.median(r))))
        weights=np.minimum(1,1.5*scale/np.maximum(abs(r),1e-6))
    return coef

def minor_height(item):
    cache=entry(item['polygon'])
    if cache is not None and 'minor_height' in cache:return cache['minor_height']
    value=min(cv2.minAreaRect(np.asarray(item['polygon'],np.float32))[1])
    if cache is not None:cache['minor_height']=value
    return value

def height_proxy(items,size):
    hs=[minor_height(q) for q in items]
    h=float(np.median(hs)) if hs else min(size)/100
    return max(min(size)/1000,h*.5) # provisional, NOT measured xheight

def line_axis(item):
    cache=entry(item['polygon'])
    if cache is not None and 'axis' in cache:return cache['axis'].copy()
    p=np.asarray(item['polygon'],np.float32); b=bbox(item)
    left=p[np.argsort(p[:,0])[:2]].mean(0); right=p[np.argsort(p[:,0])[-2:]].mean(0)
    if right[0]-left[0]<1e-6:out=np.array([b[1]+(b[3]-b[1])/2,0.])
    else:
        slope=(right[1]-left[1])/(right[0]-left[0]);out=np.array([left[1]-slope*left[0],slope])
    if cache is not None:cache['axis']=out
    return out.copy()

def sample_strip(array,item,page_size,height,nx=41,ny=41,extend=1.):
    b=bbox(item); axis=line_axis(item); W,H=page_size; ah,aw=array.shape
    xs=np.linspace(max(0,b[0]-extend*height),min(W-1,b[2]+extend*height),nx)
    offsets=np.linspace(-1.5*height,1.5*height,ny)
    ys=axis[0]+axis[1]*xs
    mx=np.broadcast_to(xs[None,:]*aw/W,(ny,nx)).astype(np.float32)
    my=((ys[None,:]+offsets[:,None])*ah/H).astype(np.float32)
    strip=cv2.remap(array.astype(np.float32),mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    return strip,xs,ys,offsets

def peak_track(strip, offsets):
    smooth=gaussian_filter1d(strip,1.,axis=0)
    ids=np.argmax(smooth,axis=0)
    return offsets[ids],smooth[ids,np.arange(len(ids))]

def continuous_path(strip,step=2):
    """Max-sum path with bounded vertical steps; returns indices and alternative peaks."""
    a=np.asarray(strip,float); h,w=a.shape
    v=a[:,0].copy(); back=np.zeros((h,w),np.int16)
    for x in range(1,w):
        choices=np.stack([np.roll(v,k)-.08*abs(k) for k in range(-step,step+1)])
        for j,k in enumerate(range(-step,step+1)):
            if k>0: choices[j,:k]=-1e9
            elif k<0: choices[j,k:]=-1e9
        best=choices.argmax(0); v=choices[best,np.arange(h)]+a[:,x]
        back[:,x]=np.arange(h)-(best-step)
    path=np.empty(w,int); path[-1]=v.argmax()
    for x in range(w-1,0,-1): path[x-1]=back[path[x],x]
    return path

def ribbon(xs,ys,height):
    return np.vstack([np.c_[xs,ys-height/2],np.c_[xs[::-1],ys[::-1]+height/2]]).tolist()

def pitch_candidates(profile,height):
    p=np.asarray(profile,float); p=p-p.mean(); c=np.correlate(p,p,mode='full')[len(p)-1:]
    if not len(c) or c[0]<=0: return []
    c/=c[0]; peaks,_=find_peaks(c,distance=quantize(height*.5))
    peaks=[k for k in peaks if height<=k<=6*height]
    return [dict(pitch=float(k),correlation=float(c[k])) for k in sorted(peaks,key=lambda i:-c[i])[:3]]

def comparison(path, reference, height):
    x,y=np.asarray(path).T; rx,ry=np.asarray(reference).T
    err=abs(y-np.interp(x,rx,ry))/max(height,1e-6)
    return dict(median_h=float(np.median(err)),max_h=float(err.max()),samples=err.tolist())

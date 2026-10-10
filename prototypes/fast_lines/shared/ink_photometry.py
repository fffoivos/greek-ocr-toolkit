"""Reusable tone and glyph-shape operators, adapted from stopped 8e5c522.

No ownership labels here. Components are observed fragments, not known characters."""
import cv2
import numpy as np
from .geometry import roi, quantize
from .image_evidence import components


def percentiles8(patch, qs):
    """Exact NumPy linear percentiles for a nonempty uint8 sampled patch."""
    counts=np.bincount(patch.ravel(),minlength=256).cumsum()
    ranks=np.asarray(qs,dtype=float)*(patch.size-1)/100
    lo=np.floor(ranks).astype(int);hi=np.ceil(ranks).astype(int)
    a=np.searchsorted(counts,lo,side='right');b=np.searchsorted(counts,hi,side='right')
    return a+(b-a)*(ranks-lo)


def tones(gray, box, lows=(2,10)):
    x0,y0,x1,y1=roi(box,gray.shape)
    patch=gray[y0:y1:max(1,(y1-y0)//24),x0:x1:max(1,(x1-x0)//192)]
    if not patch.size: return np.zeros(len(lows))
    values=percentiles8(patch,[*lows,90]);hi=values[-1]
    return (hi-values[:-1])/max(hi,1)


def tone(gray, box, low=10):
    return float(tones(gray,box,(low,))[0])


def glyphs(gray, box, height, threshold=.70, limit=64):
    x0,y0,x1,y1=roi(box,gray.shape)
    raw=gray[y0:y1,x0:x1]
    if not raw.size: return []
    paper=float(np.percentile(raw,90)); depth=paper-float(np.percentile(raw,10))
    if depth<1: return []
    binary=(raw < paper-threshold*depth).astype(np.uint8)
    labels,stats,_=components(binary)
    found=[]
    for j,(x,y,w,h,area) in enumerate(stats):
        if not (.35*height<h<1.8*height and .12*height<w<1.6*height): continue
        if area < .055*height*height or x==0 or y==0 or x+w>=raw.shape[1] or y+h>=raw.shape[0]: continue
        patch=(labels[y:y+h,x:x+w]==j+1).astype(np.float32)
        scale=18/max(h,w); sw,sh=quantize(w*scale),quantize(h*scale)
        patch=cv2.resize(patch,(sw,sh),interpolation=cv2.INTER_AREA)
        tile=np.zeros((22,22),np.float32); tx=(22-sw)//2; ty=(22-sh)//2
        tile[ty:ty+sh,tx:tx+sw]=patch
        tile=cv2.GaussianBlur(tile,(3,3),.6)
        v=tile.ravel(); v=v-v.mean(); v=v/max(np.linalg.norm(v),1e-6)
        found.append(dict(bbox=[int(x+x0),int(y+y0),int(x+x0+w),int(y+y0+h)], vector=v, tile=tile,
                          aspect=float(w/h), height=float(h)))
    if len(found)>limit:
        found=[found[i] for i in np.linspace(0,len(found)-1,limit).astype(int)]
    return found


def match_glyphs(query, atlas):
    if not query or not atlas: return []
    a=np.array([g['vector'] for g in atlas],np.float32)
    q=np.array([g['vector'] for g in query],np.float32)
    qr=q.reshape(-1,22,22)[:,:,::-1].reshape(-1,484).copy()
    # OpenCV GEMM obeys cv2's thread setting, avoiding an unbounded BLAS pool.
    direct=cv2.gemm(q,a,1,None,0,flags=cv2.GEMM_2_T)
    reflected=cv2.gemm(qr,a,1,None,0,flags=cv2.GEMM_2_T)
    # Compare shapes at compatible aspect ratio; do not stretch one glyph to another.
    compatible=np.abs(np.log(np.array([g['aspect'] for g in query])[:,None]/np.array([g['aspect'] for g in atlas])[None,:]))<.22
    direct[~compatible]=-1;reflected[~compatible]=-1
    di=direct.argmax(1);ri=reflected.argmax(1)
    return [dict(bbox=g['bbox'],direct=float(direct[i,di[i]]),reflected=float(reflected[i,ri[i]]),
                 margin=float(reflected[i,ri[i]]-direct[i,di[i]]),direct_id=int(di[i]),reflected_id=int(ri[i])) for i,g in enumerate(query)]


def motif(gray, box, height):
    x0,y0,x1,y1=roi(box,gray.shape)
    raw=gray[y0:y1,x0:x1]
    if not raw.size or raw.shape[1]<4*height: return dict(repeat=0.,lag_h=0.)
    s=min(1.,12/height)
    patch=cv2.resize(raw,None,fx=s,fy=s,interpolation=cv2.INTER_AREA).astype(np.float32)
    patch=patch.mean(0); patch=patch-patch.mean()
    values=[]
    for lag in range(quantize(.35*height*s),min(quantize(4*height*s),len(patch)//4)):
        a,b=patch[:-lag],patch[lag:]
        v=float(a@b/max(np.linalg.norm(a)*np.linalg.norm(b),1e-6))
        values.append((v,lag))
    if not values: return dict(repeat=0.,lag_h=0.)
    v,lag=max(values)
    return dict(repeat=v,lag_h=lag/(height*s),lag=lag/s,bbox=list(box))

"""Repeated observed shapes, not recognized letters or named fonts.

Original components retain their locations and sizes. Matching normalizes scale
isotropically, never stretches aspect ratio, and keeps alternate exemplars.
"""
from time import perf_counter
import cv2,numpy as np
from .geometry import roi,height_proxy
from .contracts import bbox


def tile(ink,side):
    h,w=ink.shape;s=(side-4)/max(h,w);ww=max(1,round(w*s));hh=max(1,round(h*s))
    out=np.zeros((side,side),np.float32);x=(side-ww)//2;y=(side-hh)//2
    out[y:y+hh,x:x+ww]=cv2.resize(ink.astype(np.float32),(ww,hh),interpolation=cv2.INTER_AREA)
    return out


def extract(gray,items,*,version=1):
    start=perf_counter();out=[]
    for line,q in enumerate(items):
        h=height_proxy([q],(gray.shape[1],gray.shape[0]));a,t,b,d=roi(bbox(q),gray.shape);g=gray[t:d,a:b]
        if not g.size:continue
        paper=float(np.percentile(g,90));depth=paper-float(np.percentile(g,10))
        if depth<1:continue
        ink=(g<paper-.7*depth).astype(np.uint8);_,lab,ss,cc=cv2.connectedComponentsWithStats(ink,8)
        for k,(x,y,w,hh,area) in enumerate(ss[1:],1):
            if not(.35*h<hh<1.8*h and .12*h<w<1.6*h and area>.055*h*h):continue
            if x==0 or y==0 or x+w>=g.shape[1] or y+hh>=g.shape[0]:continue
            if version>=2 and (hh<.55*h or w<.25*h):continue
            raw=(lab[y:y+hh,x:x+w]==k).astype(np.uint8)
            box=[int(a+x),int(t+y),int(a+x+w),int(t+y+hh)]
            if version>=2:
                duplicate=None
                for old in out:
                    z=old['bbox'];ov=max(0,min(box[2],z[2])-max(box[0],z[0]))*max(0,min(box[3],z[3])-max(box[1],z[1]))
                    if ov>.75*max(w*hh,(z[2]-z[0])*(z[3]-z[1])):duplicate=old;break
                if duplicate is not None:
                    duplicate['owners'].append(line);continue
            out.append(dict(line=line,owners=[line],bbox=box,height=int(hh),aspect=float(w/hh),ink=raw,
                            size_page=float(hh/gray.shape[1]),area=int(area),proxy=h))
    return out,perf_counter()-start


def vectors(glyphs,side=24,profile=False):
    vv=[]
    for g in glyphs:
        z=tile(g['ink'],side)
        if profile:z=np.r_[z.mean(0),z.mean(1)]
        else:z=cv2.GaussianBlur(z,(3,3),.6).ravel()
        z=z-z.mean();z=z/max(np.linalg.norm(z),1e-6);vv.append(z)
    return np.asarray(vv,np.float32)


def witnesses(query,atlas,*,route='slow',same_page=False,version=1):
    start=perf_counter()
    if not query or not atlas:return dict(pairs=[],seconds=perf_counter()-start)
    side=64 if route=='slow' else 24 if route=='explicit' else 8
    qv=vectors(query,side,route=='heuristic');av=vectors(atlas,side,route=='heuristic')
    # The costly explicit shape inner products are intentionally offline; no
    # scalar font classifier or atlas search runs on a clean page.
    scores=cv2.gemm(qv,av,1,None,0,flags=cv2.GEMM_2_T)
    compatible=np.abs(np.log(np.array([q['aspect'] for q in query])[:,None]/np.array([a['aspect'] for a in atlas])[None,:]))<.18
    if same_page:
        compatible&=np.array([q['line'] for q in query])[:,None]!=np.array([a['line'] for a in atlas])[None,:]
        if version>=2:
            compatible&=np.array([[not set(q['owners'])&set(a['owners']) for a in atlas] for q in query])
    scores[~compatible]=-1;pairs=[]
    for i,g in enumerate(query):
        ids=np.argsort(-scores[i])[:3]
        if scores[i,ids[0]]<.65:continue
        alt=[]
        for j in ids:
            if scores[i,j]<.65:continue
            value=float(scores[i,j]);a=atlas[j]
            # Near-solid sticks/dots cannot establish a shared font. Require
            # internal shape variation and three distinct forms downstream.
            informative=min(g['aspect'],a['aspect'])>.25
            if version>=2:
                informative=informative and min(g['area']/(g['ink'].size),a['area']/(a['ink'].size))<.75
            alt.append(dict(atlas=int(j),similarity=value,size_ratio=float(g['height']/a['height']),informative=bool(informative)))
        if alt:pairs.append(dict(query=i,alternatives=alt))
    return dict(pairs=pairs,seconds=perf_counter()-start,route=route,semantics='observed repeated shapes; not character or font identity')


def sample(glyphs,per_line=8):
    out=[]
    for line in sorted(set(g['line'] for g in glyphs)):
        group=[g for g in glyphs if g['line']==line]
        out.extend(group[i] for i in np.unique(np.linspace(0,len(group)-1,min(per_line,len(group))).astype(int)))
    return out

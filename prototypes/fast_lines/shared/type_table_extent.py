"""Table extent from repeated terminal dot runs, with every row witness retained.

A leader run alone is punctuation. Several rows with aligned terminal edges and
letter-scale row pitch establish a regional table hypothesis, never a text eraser.
"""
from time import perf_counter
import cv2,numpy as np
from .geometry import height_proxy,roi,line_axis
from .contracts import bbox
from .type_dot_runs import chains


def analyze(gray,items,*,route='slow',version=1):
    start=perf_counter();height=height_proxy(items,(gray.shape[1],gray.shape[0]));rows=[]
    for i,q in enumerate(items):
        a,t,b,d=roi(bbox(q),gray.shape);original=[a,t,b,d];h=height_proxy([q],(gray.shape[1],gray.shape[0]))
        if b-a<5*h:continue
        if version>=4:a,t,b,d=roi([a-.7*h,t-.6*h,b+.7*h,d+.6*h],gray.shape)
        g=gray[t:d,a:b];factor=1 if route=='slow' else max(1,h/(20 if route=='explicit' else 8))
        if factor>1:g=cv2.resize(g,(max(1,round(g.shape[1]/factor)),max(1,round(g.shape[0]/factor))),interpolation=cv2.INTER_AREA)
        sy=(d-t)/g.shape[0];sx=(b-a)/g.shape[1];hh=h/sy
        k=max(1,round(3*hh))|1;paper=cv2.morphologyEx(g,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8))
        depth=paper.astype(float)-g;floor=.18*np.maximum(paper,1)
        if version>=5:floor=np.maximum(floor,.5*np.percentile(depth,95))
        ink=(depth>floor).astype(np.uint8)
        _,lab,s,c=cv2.connectedComponentsWithStats(ink,8);s=s[1:];c=c[1:]
        good=(s[:,2]<.65*hh)&(s[:,3]<.65*hh)&(s[:,2]>.06*hh)&(s[:,3]>.06*hh)&(s[:,4]>.012*hh*hh)
        if version>=3:
            # Dots are compact complete components near the body-bottom, not
            # clipped letters or the upper accent rail of ordinary prose.
            good&=(s[:,1]>0)&(s[:,1]+s[:,3]<g.shape[0])&(s[:,2]<.5*hh)&(s[:,3]<.5*hh)
            good&=(s[:,2]>.55*s[:,3])&(s[:,3]>.55*s[:,2])&(c[:,1]>(sum(original[1::2])*.5-t)/sy-.2*hh)
            if version>=4:good&=(c[:,1]<(original[3]+.2*h-t)/sy)
        dot_ink=np.isin(lab,np.flatnonzero(good)+1)
        def purity(chain):
            pp=pts[chain];x0=max(0,round((pp[:,0].min()-a-.25*h)/sx));x1=min(g.shape[1],round((pp[:,0].max()-a+.25*h)/sx))
            y0=max(0,round((pp[:,1].min()-t-.7*h)/sy));y1=min(g.shape[0],round((pp[:,1].max()-t+.7*h)/sy))
            total=ink[y0:y1,x0:x1].sum()
            return float(dot_ink[y0:y1,x0:x1].sum()/max(total,1))
        pts=c[good]*[sx,sy]+[a,t]
        if len(pts)<3:continue
        axis=line_axis(q);pts=pts[np.argsort(pts[:,0])];best=[]
        for u,v,chain,pitch in chains(pts,axis[1],h,pitch_max=3,vertical=.22,horizontal=.25,lookahead=4,min_remaining=3,missing=version>=2):
            if len(chain)>len(best) and (version<2 or purity(chain)>.7):best=chain
        if len(best)<3:continue
        cc=pts[best]
        if np.ptp(cc[:,0])<2*h:continue
        # Keep every dot and terminal witness; do not extrapolate a page label.
        rows.append(dict(item=i,bbox=original,points=cc.tolist(),height=h,y=float(np.median(cc[:,1])),right=float(original[2]),span_h=float(np.ptp(cc[:,0])/h),dot_purity=purity(best)))
    bounds=np.asarray([bbox(q) for q in items],float).reshape(-1,4);yc=(bounds[:,1]+bounds[:,3])/2
    groups=[]
    for r in sorted(rows,key=lambda r:r['y']):
        match=None
        for g in groups:
            last=g[-1];h=max(r['height'],last['height'])
            continuous=0<r['y']-last['y']<4*h
            if version>=6 and 0<r['y']-last['y']<12*h:
                x0=max(r['bbox'][0],last['bbox'][0]);x1=min(r['bbox'][2],last['bbox'][2])
                bridge=yc[(yc>last['y'])&(yc<r['y'])&(bounds[:,0]<x1)&(bounds[:,2]>x0)]
                continuous=np.max(np.diff(np.sort(np.r_[last['y'],bridge,r['y']])))<4*h
            if abs(r['right']-np.median([z['right'] for z in g]))<1.5*h and continuous:
                match=g;break
        if match is None:groups.append([r])
        else:match.append(r)
    regions=[]
    for group in groups:
        if len(group)<3:continue
        boxes=np.array([r['bbox'] for r in group]);ids=[r['item'] for r in group]
        box=[float(boxes[:,0].min()),float(boxes[:,1].min()),float(boxes[:,2].max()),float(boxes[:,3].max())]
        if version>=6:
            ids=np.flatnonzero((yc>=box[1])&(yc<=box[3])&(bounds[:,0]>=box[0]-height)&(bounds[:,2]<=box[2]+height)).tolist()
        regions.append(dict(bbox=box,cells=ids,rows=group,status='protect',source='terminal dot runs and aligned row endings'))
    return dict(regions=regions,rows=rows,height=height,seconds=perf_counter()-start,route=route,protected_indices=sorted({i for r in regions for i in r['cells']}))

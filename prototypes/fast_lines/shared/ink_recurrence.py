"""Render local four-copy spatial recurrence without enumerating templates.

Only a nomination: the full repeated-template and residual-letter witness still
owns an ornament decision. Local normalized correlation separates shape from tone.
"""
import cv2,numpy as np
from .ink_repeat_field import context,field
from .contracts import bbox
from .ink_photometry import percentiles8


def render(gray,item,height,*,samples=8,detail=False,route='explicit'):
    raw,s=context(gray,item,height,samples=samples);h=height*s
    paper,core=percentiles8(raw,[90,10]);a=np.clip((paper-raw.astype(np.float32))/max(float(paper-core),1),0,1)
    wh=max(2,round(.5*h));ww=max(3,round(h));kernel=(ww,wh)
    mean=cv2.boxFilter(a,-1,kernel,normalize=True);var=np.maximum(cv2.boxFilter(a*a,-1,kernel,normalize=True)-mean*mean,0)
    b=bbox(item);left=max(0,b[0]-6*height);t0=round((b[0]-left)*s);t1=min(raw.shape[1],round((b[2]-left)*s))
    union=np.zeros(a.shape,np.uint8);records=[];best=None;best_support=union.copy()
    lags=range(max(2,round(.7*h)),min(round(8*h),a.shape[1]//3))
    if route=='heuristic':
        peaks=sorted(field(raw,h)['peaks'],key=lambda p:-p['correlation'])[:5]
        selected={round(p['lag_h']*h)+j for p in peaks for j in (-1,0,1)}
        lags=[lag for lag in lags if lag in selected]
    elif route!='explicit':raise ValueError(route)
    for lag in lags:
        w=a.shape[1]-lag;peak=np.zeros((a.shape[0],w),np.float32)
        for dy in range(-max(1,round(.125*h)),max(1,round(.125*h))+1):
            y0=max(0,-dy);y1=min(a.shape[0],a.shape[0]-dy)
            l=a[y0:y1,:w];r=a[y0+dy:y1+dy,lag:]
            cross=cv2.boxFilter(l*r,-1,kernel,normalize=True)
            den=np.sqrt(var[y0:y1,:w]*var[y0+dy:y1+dy,lag:])
            ncc=(cross-mean[y0:y1,:w]*mean[y0+dy:y1+dy,lag:])/np.maximum(den,1e-5)
            ncc[den<.0225]=0
            # Reflected box-filter borders have no matching observed patch.
            ncc[:wh//2+1]=0;ncc[-wh//2-1:]=0;ncc[:,:ww//2+1]=0;ncc[:,-ww//2-1:]=0
            peak[y0:y1]=np.maximum(peak[y0:y1],ncc)
        pair=np.zeros(a.shape,np.uint8);pair[:,:w]=peak>=.75
        chain=pair.copy()
        for _ in range(2):
            nearby=cv2.dilate(chain,np.ones((3,3),np.uint8));nxt=np.zeros_like(chain);nxt[:,:-lag]=nearby[:,lag:];chain=pair&nxt
        support=chain.copy()
        for n in (1,2,3):support[:,n*lag:]|=chain[:,:-n*lag]
        support=cv2.dilate(support,np.ones((wh,ww),np.uint8))
        cov=float((a*support)[:,t0:t1].sum()/max(a[:,t0:t1].sum(),1))
        xs=np.flatnonzero(support.any(0));span=float((xs[-1]-xs[0]+1)/a.shape[1]) if len(xs) else 0.
        rec=dict(lag_h=lag/h,coverage=cov,span=span)
        if best is None or cov>best['coverage']:best=rec;best_support=support.copy()
        records.append(rec);union|=support
    best=best or dict(lag_h=0.,coverage=0.,span=0.)
    out=dict(best=best,nominate=best['coverage']>=.25 and best['span']>=.5,route=route,lags=len(lags))
    if detail:out.update(raw=raw,support=best_support,all_period_support=union,records=records,scale=s,target=[t0,t1])
    return out

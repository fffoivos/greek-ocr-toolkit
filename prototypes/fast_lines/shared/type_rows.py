"""Explicit physical rows inside a localization, including joined ink.

Contact guides are geometric envelopes, not semantic script baselines. Multiple
well-supported rows make a single-height answer ambiguous rather than averaged.
"""
from time import perf_counter
import cv2,numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from .type_profiles import strip,mode
from .contracts import bbox


def render(gray,item,*,route='slow',version=1):
    start=perf_counter();samples=None if route=='slow' else 24 if route=='explicit' else 8
    patch,x,dy,axis,prior,step=strip(gray,item,samples);h=prior/step
    k=max(1,round(3*h))|1;paper=cv2.morphologyEx(patch,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8))
    ink=((paper.astype(np.float32)-patch)>.18*np.maximum(paper,1)).astype(np.uint8)
    _,lab,s,c=cv2.connectedComponentsWithStats(ink,8);s=s[1:];c=c[1:]
    good=(s[:,3]>.22*h)&(s[:,3]<1.8*h)&(s[:,2]>.10*h)&(s[:,2]<6*h)&(s[:,4]>.025*h*h)
    if version>=3:good&=(s[:,1]>0)&(s[:,1]+s[:,3]<ink.shape[0])
    estimates=s[good,3];body,_=mode(estimates,h,weights=np.minimum(s[good,4],h*h))
    body=h if body is None else body
    row_scale=min(body,h) if version>=2 else body
    density=gaussian_filter1d(ink.mean(1).astype(float),max(.5,.10*row_scale))
    peaks,_=find_peaks(density,prominence=max(.015,float(density.max())*.15),distance=max(1,round(.8*row_scale)))
    bands=[]
    for j,peak in enumerate(peaks):
        top=0 if j==0 else int(peaks[j-1]+np.argmin(density[peaks[j-1]:peak+1]))
        bottom=len(dy)-1 if j+1==len(peaks) else int(peak+np.argmin(density[peak:peaks[j+1]+1]))
        eligible=good&(c[:,1]>top)&(c[:,1]<bottom)
        if version>=3:eligible&=(s[:,1]>=top)&(s[:,1]+s[:,3]<=bottom+1)
        ids=np.flatnonzero(eligible);contacts=s[ids,1]+s[ids,3]
        base,bc=mode(contacts,body);roof,tc=mode(s[ids,1],body)
        if base is None:base=peak+body*.5
        if roof is None:roof=peak-body*.5
        # V2 requires both contacts from the SAME component population. Two
        # contact modes across different rows cannot manufacture a tall body.
        if version>=2:
            consistent=ids[(abs(contacts-base)<.25*body)&(s[ids,3]>.5*body)]
            rr,rc=mode(s[consistent,1],body)
            if rr is not None:roof=rr;tc=rc
        support=len(ids);span=float(np.ptp(c[ids,0])*step/prior) if support else 0.
        points=[];marks=[]
        for i in np.flatnonzero((c[:,1]>top)&(c[:,1]<bottom)):
            sx,sy,w,hh,area=s[i];gx=float(x[0]+sx*step);gy=float(axis[0]+axis[1]*gx+dy[0]+sy*step)
            q=dict(bbox=[gx,gy,gx+w*step,gy+hh*step],role='body' if i in ids else 'mark',area=int(area)*step*step)
            (points if i in ids else marks).append(q)
        joined=bool(support and np.mean(s[ids,2]>(1.6*s[ids,3] if version>=2 else 1.5*body))>.25)
        if version>=3 and support:
            joined=bool(s[ids[s[ids,2]>1.6*s[ids,3]],4].sum()>.4*s[ids,4].sum())
        centre=float(dy[peak]);within=abs(centre)<.9*prior
        supported=support>=5 and span>=5 and bc>=3 and tc>=3 and roof<base
        if version>=2:supported=supported and .5*body<base-roof<1.5*body
        if joined:
            # Connected words need envelope evidence, not fictitious characters.
            supported=support>=2 and span>=5
        paths={};xs=[];lo=[];hi=[]
        envelope=ink
        if version>=3:
            selected=np.flatnonzero((c[:,1]>top)&(c[:,1]<bottom)&(s[:,1]>0)&(s[:,1]+s[:,3]<ink.shape[0]))+1
            envelope=np.isin(lab,selected).astype(np.uint8)
        for a in range(0,ink.shape[1],max(1,round(body))):
            cut=envelope[top:bottom+1,a:min(ink.shape[1],a+max(1,round(2*body)))];yy=np.repeat(np.arange(top,bottom+1),cut.sum(1).astype(int))
            if len(yy)<.1*body*body:continue
            xs.append(float(x[min(len(x)-1,a+round(body/2))]));lo.append(float(dy[0]+np.quantile(yy,.15)*step));hi.append(float(dy[0]+np.quantile(yy,.85)*step))
        for key,v in [('mass_top',lo),('mass_bottom',hi)]:paths[key]=[[xx,float(axis[0]+axis[1]*xx+yy)] for xx,yy in zip(xs,v)]
        bounds=[float(x[0]),float(axis[0]+axis[1]*x[0]+dy[top]),float(x[-1]),float(axis[0]+axis[1]*x[-1]+dy[bottom])]
        bands.append(dict(centre=centre,body_height=float((base-roof)*step),component_mode=float(body*step),supported=bool(supported),within_box=bool(within),joined=joined,
            support=support,contacts=[int(tc),int(bc)],span=span,body_top=float(dy[0]+roof*step),body_bottom=float(dy[0]+base*step),components=points,marks=marks,paths=paths,bbox=bounds))
    active=[b for b in bands if b['supported'] and b['within_box']]
    return dict(bands=bands,axis=axis.tolist(),prior=prior,ambiguous=len(active)!=1,body_height=active[0]['body_height'] if len(active)==1 and not active[0]['joined'] else None,
        joined=any(b['joined'] for b in active),baseline=None,seconds=perf_counter()-start,route=route,semantics='multiple row contacts / joined mass envelopes, not script baselines')

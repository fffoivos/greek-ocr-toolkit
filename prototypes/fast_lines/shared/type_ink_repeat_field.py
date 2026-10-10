# Snapshot from track B round4; see features_type/reuse_round4.json.
"""Spatial displacement rendering: recurrent ink at (horizontal, vertical) lag.

This is a nomination witness, not an ornament classifier. Its input is the
original page and a detector polygon; no named-page constants or learned labels.
"""
import cv2,numpy as np
from scipy.signal import find_peaks
from .type_ink_motifs import strip
from .geometry import line_axis,quantize
from .contracts import bbox


def context(gray,item,height,*,samples=8):
    b=bbox(item);axis=line_axis(item);left=max(0,b[0]-6*height);right=min(gray.shape[1]-1,b[2]+6*height)
    half=(b[3]-b[1])/2
    expanded=dict(polygon=[[left,axis[0]+axis[1]*left-half],[right,axis[0]+axis[1]*right-half],
                           [right,axis[0]+axis[1]*right+half],[left,axis[0]+axis[1]*left+half]])
    return strip(gray,expanded,height,samples=samples)


def field(raw,height,*,detail=False):
    a=(255-raw.astype(np.float32))/255
    a-=a.mean(1,keepdims=True)
    h,w=a.shape;lo=quantize(.7*height);hi=min(quantize(8*height),w//3)
    dymax=min(quantize(.65*height),(h-1)//2)
    if hi<=lo or dymax<1:return dict(repeat=0.,lag_h=0.,dy_h=0.,peaks=[],local=[])
    size=(cv2.getOptimalDFTSize(2*w),cv2.getOptimalDFTSize(2*h))
    padded=np.zeros((size[1],size[0]),np.float32);padded[:h,:w]=a
    fft=cv2.dft(padded,flags=cv2.DFT_COMPLEX_OUTPUT)
    corr=cv2.idft(cv2.mulSpectrums(fft,fft,0,conjB=True),flags=cv2.DFT_REAL_OUTPUT|cv2.DFT_SCALE)
    energy=cv2.integral(a*a)
    def rect(y0,x0,y1,x1):return energy[y1,x1]-energy[y0,x1]-energy[y1,x0]+energy[y0,x0]
    lags=np.arange(lo,hi);dys=np.arange(-dymax,dymax+1);values=[]
    for dy in dys:
        y0=max(0,-dy);y1=min(h,h-dy)
        den=np.sqrt(np.maximum(rect(y0,0,y1,w-lags)*rect(y0+dy,lags,y1+dy,w),1e-12))
        values.append(corr[dy%corr.shape[0],lags]/den)
    values=np.asarray(values);profile=values.max(0);jj=values.argmax(0)
    peaks,_=find_peaks(profile,prominence=.04)
    if not len(peaks):
        out=dict(repeat=0.,lag_h=0.,dy_h=0.,peaks=[],local=[])
        if detail:out.update(field=values,lags_h=lags/height,dys_h=dys/height)
        return out
    best=int(max(peaks,key=lambda i:profile[i]));lag=int(lags[best]);dy=int(dys[jj[best]])
    local=[];y0=max(0,-dy);y1=min(h,h-dy)
    for x in range(0,w-2*lag,lag):
        l=a[y0:y1,x:x+lag];r=a[y0+dy:y1+dy,x+lag:x+2*lag]
        local.append(float(np.sum(l*r)/max(np.linalg.norm(l)*np.linalg.norm(r),1e-6)))
    out=dict(repeat=float(profile[best]),lag_h=lag/height,dy_h=dy/height,local=local,
             peaks=[dict(lag_h=float(lags[i]/height),dy_h=float(dys[jj[i]]/height),correlation=float(profile[i])) for i in peaks])
    if detail:out.update(field=values,lags_h=lags/height,dys_h=dys/height)
    return out


def bands(gray,item,height,*,samples=8,detail=False):
    """Render recurrent horizontal subbands; adjacent decoration need not repeat."""
    raw,s=context(gray,item,height,samples=samples);h=height*s;records=[]
    b=bbox(item);left=max(0,b[0]-6*height);t0=round((b[0]-left)*s);t1=round((b[2]-left)*s)
    paper,core=np.percentile(raw,[90,10]);ink=np.maximum(0,paper-raw.astype(float));target=ink[:,t0:t1];mass=max(float(target.sum()),1.)
    for factor in (.5,1.,1.5):
        bh=min(raw.shape[0],quantize(factor*h))
        for top in np.unique(np.linspace(0,raw.shape[0]-bh,4).astype(int)):
            r=field(raw[top:top+bh],h,detail=detail)
            good=[x>=.5 for x in r['local']];run=best=0
            for q in good:run=run+1 if q else 0;best=max(best,run)
            r.update(top_h=float(top/h),band_h=float(bh/h),consecutive=best,
                     target_share=float(target[top:top+bh].sum()/mass))
            records.append(r)
    best=max(records,key=lambda r:((r['consecutive']>=3 and r['repeat']>=.25)*r['target_share'],r['repeat']))
    out=dict(best=best,bands=records,nominate=best['consecutive']>=3 and best['repeat']>=.25 and best['target_share']>=.25)
    if detail:out.update(raw=raw,scale=s)
    return out


def analyze(gray,item,height,*,samples=8,detail=False):
    raw,s=context(gray,item,height,samples=samples);out=field(raw,height*s,detail=detail)
    # Route2: projection correlation discards vertical positions completely.
    p=(255-raw.astype(np.float32)).mean(0);p-=p.mean();vals=[]
    for lag in range(quantize(.7*height*s),min(quantize(8*height*s),len(p)//3)):
        l,r=p[:-lag],p[lag:];vals.append(float(l@r/max(np.linalg.norm(l)*np.linalg.norm(r),1e-6)))
    out['projection_repeat']=max(vals,default=0.)
    if detail:out.update(raw=raw,scale=s)
    return out


def template_specs(gray,item,height,*,samples=8):
    """Use the rendered displacement peaks to place bounded spatial witnesses."""
    product=bands(gray,item,height,samples=samples,detail=True);raw=product['raw'];h=height*product['scale']
    eligible=[r for r in product['bands'] if r['consecutive']>=3 and r['repeat']>=.25 and r['target_share']>=.15]
    eligible=sorted(eligible,key=lambda r:-r['target_share']*r['repeat'])[:3];specs=set()
    for r in eligible:
        top=round(r['top_h']*h);th=round(r['band_h']*h)
        for peak in sorted(r['peaks'],key=lambda p:-p['correlation'])[:2]:
            for multiple in (1.,2.):
                tw=quantize(peak['lag_h']*h*multiple)
                if raw.shape[1]<4*tw:continue
                for x in np.unique(np.linspace(0,raw.shape[1]-tw,3).astype(int)):specs.add((int(x),top,tw,th))
    return sorted(specs),dict(nominate=bool(specs),templates=len(specs),best={k:v for k,v in product['best'].items() if k not in ('field','lags_h','dys_h')})

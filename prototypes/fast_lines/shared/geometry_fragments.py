"""Fast endpoint/tangent hypotheses for curled fragments, never joins by itself."""
from time import perf_counter
import numpy as np
from .contracts import bbox
from .geometry import height_proxy,line_axis


def candidates(items,size):
    t=perf_counter();h=height_proxy(items,size)
    bounds=np.asarray([bbox(q) for q in items]).reshape(-1,4)
    axes=np.asarray([line_axis(q) for q in items]).reshape(-1,2)
    long=np.flatnonzero(bounds[:,2]-bounds[:,0]>=16*h)
    short=np.flatnonzero((bounds[:,2]-bounds[:,0]>1.5*h)&(bounds[:,2]-bounds[:,0]<12*h)&(abs(axes[:,1])>.08))
    pairs=[]
    for i in long:
        b=bounds[i];a,s=axes[i]
        for j in short:
            f=bounds[j];fa,fs=axes[j]
            side=1 if (f[0]+f[2])>(b[0]+b[2]) else -1
            gap=f[0]-b[2] if side==1 else b[0]-f[2]
            if not -h<gap<4*h:continue
            edge=b[2] if side==1 else b[0]
            mismatch=abs((fa+fs*edge)-(a+s*edge))/h
            if mismatch>.85:continue
            if side*(fs-s)*((fa+fs*((f[0]+f[2])/2))-(a+s*((f[0]+f[2])/2)))<0:continue
            pairs.append(dict(line=int(i),fragment=int(j),side=side,gap_h=float(gap/h),tangent_mismatch_h=float(mismatch)))
    # Ambiguity is a property of the fragment, not an excuse to take the nearest.
    for p in pairs:p['owners']=sum(q['fragment']==p['fragment'] for q in pairs)
    return dict(height=h,pairs=pairs,seconds=perf_counter()-t,trigger=bool(pairs))


def hermite(items,pair,height):
    main=items[pair['line']];frag=items[pair['fragment']]
    b=bbox(main);f=bbox(frag);a,s=line_axis(main);fa,fs=line_axis(frag)
    if pair['side']==1:
        xa=b[0]+.7*(b[2]-b[0]);xb=(f[0]+f[2])/2
        xs=np.linspace(b[0],f[2],65)
    else:
        xa=b[2]-.7*(b[2]-b[0]);xb=(f[0]+f[2])/2
        xs=np.linspace(f[0],b[2],65)
    ya=a+s*xa;yb=fa+fs*xb;t=np.clip((xs-xa)/(xb-xa),0,1);dx=xb-xa
    yy=(2*t**3-3*t**2+1)*ya+(t**3-2*t**2+t)*dx*s+(-2*t**3+3*t**2)*yb+(t**3-t**2)*dx*fs
    before=(xs-xa)/(xb-xa)<0;after=(xs-xa)/(xb-xa)>1
    yy[before]=a+s*xs[before];yy[after]=fa+fs*xs[after]
    return np.c_[xs,yy].tolist()

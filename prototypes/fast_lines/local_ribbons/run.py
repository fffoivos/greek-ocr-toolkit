"""A03: sparse witnesses, then local learned-map paths with endpoint search."""
import numpy as np
from scipy.signal import find_peaks
from ..shared.geometry import sample_strip,peak_track,continuous_path,robust_fit,ribbon,bbox,comparison
from ..shared.contracts import result

def run(ctx,phase=3):
    output=[]; witnesses=[]; paths=[]; changes=[]; evaluations=[]
    layout=ctx.get('layout_barriers'); barrier=layout.get('barriers',[])
    refs={r['id']:r for r in ctx.reference.get('lines',[])}
    for i,item in enumerate(ctx.items):
        b=bbox(item); h=max(ctx.height*.5,min((b[3]-b[1])*.5,ctx.height*2))
        strip,x,y,o=sample_strip(ctx.pm,item,ctx.size,h,nx=17,ny=31,extend=1.)
        offset,support=peak_track(strip,o); valid=support>.2; mids=(np.arange(17)>=4)&(np.arange(17)<=12)&valid
        coef=robust_fit(x[mids]/ctx.size[0],offset[mids]) if mids.sum()>=3 else np.array([0.])
        residual=offset-np.polynomial.polynomial.polyval(x/ctx.size[0],coef)
        edge=np.r_[np.arange(4),np.arange(13,17)]; bend=float(np.max(abs(residual[edge][valid[edge]]))/h) if valid[edge].any() else 0.
        multiple=sum(len(find_peaks(strip[:,j],height=.3,distance=6)[0])>1 for j in range(17))
        outside=((x<b[0])|(x>b[2])) & valid
        nomination=(bend>.22 or multiple>=4 or outside.sum()>=2) and b[2]-b[0]>4*h
        witness=dict(line=i,bbox=b,bend_h=bend,multiple_profiles=multiple,outside_support=int(outside.sum()),trigger=bool(nomination))
        witnesses.append(witness)
        if not nomination or phase==1 or layout.get('table'):
            output.append(item); continue
        dense,x,y,o=sample_strip(ctx.pm,item,ctx.size,h,nx=81,ny=61,extend=1.)
        ids=continuous_path(dense); values=dense[ids,np.arange(len(ids))]; keep=values>.2
        if keep.sum()<5: output.append(item); continue
        a,z=np.flatnonzero(keep)[[0,-1]]; xx=x[a:z+1]; yy=y[a:z+1]+o[ids[a:z+1]]
        # Barriers cap endpoints; ambiguous two-ridge strips remain unchanged.
        if multiple>=4:
            witness['abstain']='persistent second ridge'; output.append(item); continue
        crossing=any(b[0]<((q['bbox'][0]+q['bbox'][2])/2)<b[2] and q['bbox'][1]<b[1]<q['bbox'][3] for q in barrier)
        if crossing:
            witness['abstain']='layout barrier crossing'; output.append(item); continue
        # Do not shrink the original horizontal support based only on map dropout.
        old_inside=(xx>=b[0])&(xx<=b[2])
        if old_inside.sum()<2: output.append(item); continue
        pol=ribbon(xx,yy,b[3]-b[1]); path=np.c_[xx,yy].tolist()
        output.append(dict(item,polygon=pol,baseline=None,centreline=path,source_ids=[i],provenance='map path; guide baseline unidentified'))
        paths.append(path); changes.append(dict(line=i,bbox=b,endpoint_delta_h=[float((xx[0]-b[0])/h),float((xx[-1]-b[2])/h)]))
        if i in refs: evaluations.append(dict(line=i,**comparison(path,refs[i]['path'],h)))
    return result(output,witnesses=witnesses,changes=changes,paths=paths,comparisons=evaluations,
                  regions=[q for q in witnesses if q['trigger']],status='retained local candidates; ambiguous multi-ridges abstain')

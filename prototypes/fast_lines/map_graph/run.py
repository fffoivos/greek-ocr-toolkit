"""A11: regional map topology; consumes the A06 request corpus."""
import numpy as np
from scipy.signal import find_peaks
from ..shared.geometry import roi,quantize,continuous_path,ribbon
from ..shared.contracts import result,deduplicate

def run(ctx,phase=3):
    requests=ctx.get('residual_ledger').get('requests',[]); candidates=[]; records=[]; paths=[]
    H,W=ctx.pm.shape; pw,ph=ctx.size; h=ctx.height*H/ph
    barriers=ctx.get('layout_barriers').get('barriers',[])
    for request in requests:
        b=request['bbox']; x0,y0,x1,y1=roi(np.asarray(b)*[W/pw,H/ph,W/pw,H/ph],ctx.pm.shape)
        strip=ctx.pm[y0:y1,x0:x1].copy(); cuts=[0,strip.shape[1]]
        for bar in barriers:
            bx0,by0,bx1,by1=bar['bbox']; bx=int((bx0+bx1)/2*W/pw)-x0
            if 0<bx<strip.shape[1] and by0<b[3] and by1>b[1]:
                strip[:,bx]=0; cuts.append(bx)
        if strip.shape[1]<2 or strip.shape[0]<3: continue
        peaks,_=find_peaks(strip.mean(1),height=.12,distance=quantize(h))
        made=0
        for peak in peaks:
            lo=max(0,peak-quantize(.6*h)); hi=min(strip.shape[0],peak+quantize(.6*h)+1)
            sub=strip[lo:hi]; ids=continuous_path(sub); values=sub[ids,np.arange(sub.shape[1])]; keep=values>.2
            if keep.sum()<3*h: continue
            ordered=sorted(set(cuts))
            for left,right in zip(ordered,ordered[1:]):
                supported=np.flatnonzero(keep[left:right])+left
                if len(supported)<3*h: continue
                start,stop=supported[[0,-1]]
                xs=(np.arange(start,stop+1)+x0)*pw/W; ys=(ids[start:stop+1]+lo+y0)*ph/H
                path=np.c_[xs,ys].tolist(); paths.append(path)
                candidates.append(dict(polygon=ribbon(xs,ys,ctx.height*1.5),baseline=None,score=None,centreline=path,
                    provenance='regional learned-map candidate; unknown ownership',source_ids=[request['id']]))
                made+=1
        records.append(dict(request=request['id'],bbox=b,paths=made,map_peak=float(strip.max()),status='map-blind -> A12/A09' if not made else 'candidate paths'))
    kept,conflicts=deduplicate(ctx.items,candidates)
    return result(kept,paths=paths,regions=[r for r in records if r['paths']],requests=records,
        conflicts=conflicts,candidates=candidates,status='regional candidates; seam conflicts retained in ledger',new_candidates=len(kept)-len(ctx.items))

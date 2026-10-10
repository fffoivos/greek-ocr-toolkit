"""A06: unexplained support and frozen, common fallback requests; no line detector."""
import cv2,numpy as np
from ..shared.geometry import mask,quantize
from ..shared.image_evidence import components
from ..shared.contracts import result,RegionRequest,merge_requests,overlap

def run(ctx,phase=3):
    e=ctx.ev; h=e.body; envelope=mask(ctx.items,e.shape,ctx.size)
    map_support=cv2.resize((ctx.pm>.2).astype(np.uint8),(e.shape[1],e.shape[0]),interpolation=cv2.INTER_NEAREST)
    support=cv2.dilate(map_support,np.ones((quantize(.5*h),quantize(.5*h)),np.uint8))*envelope
    unexplained=e.ink*(1-support); outside=e.ink*(1-envelope)
    for q in ctx.get('layout_barriers').get('rules',[]):
        b=q['bbox']; x0,y0,x1,y1=np.rint(np.asarray(b)*[e.sx,e.sy,e.sx,e.sy]).astype(int)
        unexplained[max(0,y0):y1+1,max(0,x0):x1+1]=0
    grouped=cv2.morphologyEx(unexplained,cv2.MORPH_CLOSE,np.ones((quantize(.2*h),quantize(1.5*h)),np.uint8))
    _,stats,_=components(grouped); requests=[]; suppressed=[]; candidates=[]
    motifs=ctx.get('image_motifs').get('regions',[])
    for i,(x,y,w,rh,a) in enumerate(stats):
        if w<1.5*h or rh<.25*h or rh>4*h or a<.2*h*h: continue
        b=[max(0,(x-h)/e.sx),max(0,(y-h)/e.sy),min(ctx.size[0],(x+w+h)/e.sx),min(ctx.size[1],(y+rh+h)/e.sy)]
        inside=float(envelope[y:y+rh,x:x+w].mean()); reason='support gap inside envelope' if inside>.5 else 'off-rhythm / outside envelope'
        region=dict(bbox=b,reason=reason,parts_area=int(a),ownership='unknown')
        veto=[m for m in motifs if m['suppress_new'] and overlap(b,m['bbox'])>.7*(b[2]-b[0])*(b[3]-b[1])]
        if veto: suppressed.append(dict(region,reason='A08 texture veto; raw crop remains reviewable')); continue
        candidates.append(region); requests.append(RegionRequest(f'residual-{i}',b,'missing or endpoint',[reason],dependencies=['A02','A05','A08','S2']))
    # Rhythm gaps nominate only where residual ink exists; never invent a line slot.
    for grid in ctx.get('sheet_lattice').get('grids',[]):
        centres=sorted(grid['centres']); pitches=grid['pitch_candidates']
        if not pitches: continue
        pitch=pitches[0]['pitch']/e.sy
        for a,b in zip(centres,centres[1:]):
            if 1.6*pitch<b-a<3.5*pitch:
                for r in requests:
                    if a<sum(r.bbox[1::2])/2<b: r.derivation.append('rhythm-gap witness')
    merged=merge_requests(requests)
    return result(ctx.items,requests=merged,regions=candidates,suppressed=suppressed,
                  support_unexplained_pixels=int(unexplained.sum()),envelope_unexplained_pixels=int(outside.sum()),
                  status='frozen requests, not accepted missing lines',counts=dict(raw_candidates=len(candidates)+len(suppressed),suppressed=len(suppressed),requests=len(merged)))

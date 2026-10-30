"""Sparse longitudinal contrast strips: nomination only, never removal."""
from time import perf_counter
import numpy as np
from .geometry import roi
from .contracts import bbox


def render(gray,items,height):
    start=perf_counter();boxes=np.array([roi(bbox(q),gray.shape) for q in items],float).reshape(-1,4)
    if not len(boxes):return dict(regions=[],reference={},candidate_indices=[],seconds=perf_counter()-start)
    widths=boxes[:,2]-boxes[:,0];heights=boxes[:,3]-boxes[:,1]
    n=np.maximum(1,np.ceil(widths/height).astype(int));owner=np.repeat(np.arange(len(items)),n)
    first=np.repeat(np.cumsum(n)-n,n);tile=np.arange(n.sum())-first
    # Same native samples as v1, batched across the page. Each longitudinal
    # block is one height proxy, each has eight by eight point samples.
    xx=(boxes[owner,0,None]+(tile[:,None]*8+np.arange(8))*((widths[owner,None]-1)/np.maximum(n[owner,None]*8-1,1))).astype(int)
    yy=(boxes[owner,1,None]+heights[owner,None]/4+np.arange(8)*(heights[owner,None]/2-1)/7).astype(int)
    xx[tile==n[owner]-1,-1]=(boxes[owner[tile==n[owner]-1],2]-1).astype(int)
    xx=np.clip(xx,0,gray.shape[1]-1);yy=np.clip(yy,0,gray.shape[0]-1)
    pix=gray[yy[:,:,None],xx[:,None,:]]
    dark=pix.min((1,2)).astype(float);light=pix.max((1,2)).astype(float)
    cores=(light-dark)/np.maximum(light,1);grid=np.full((len(items),int(n.max())),np.nan);grid[owner,tile]=cores
    values=np.nanmedian(grid,axis=1);upper=values[values>=np.median(values)]
    ref=float(np.median(upper));spread=1.4826*float(np.median(np.abs(values-ref)));boundary=max(0.,ref-3*spread)
    # Three adjacent letter-height blocks corroborate a longitudinal run.
    # This is nomination only; individual native components decide removals.
    normal=grid>=boundary;runs=np.any(normal[:,:-2]&normal[:,1:-1]&normal[:,2:],axis=1)
    candidates=(boundary>0)&(values<boundary)&~runs&(widths>0)&(heights>0)
    rows=[dict(line=i,cores=grid[i,:n[i]].tolist(),core=float(values[i]),normal_run=bool(runs[i]),candidate=bool(candidates[i])) for i in range(len(items))]
    return dict(regions=rows,reference=dict(core=ref,spread=spread,boundary=boundary),candidate_indices=np.flatnonzero(candidates).tolist(),seconds=perf_counter()-start)

"""Third heuristic cycle: spatial occupancy and observed counters, not marginals alone."""
from time import perf_counter
import cv2,numpy as np
from ..shared.type_identity import tile


def features(glyphs):
    vectors=[];holes=[]
    for g in glyphs:
        z=tile(g['ink'],16);small=cv2.resize(z,(4,4),interpolation=cv2.INTER_AREA)
        v=np.r_[small.ravel(),cv2.resize(z,(8,8),interpolation=cv2.INTER_AREA).mean(0),cv2.resize(z,(8,8),interpolation=cv2.INTER_AREA).mean(1)]
        v-=v.mean();v/=max(np.linalg.norm(v),1e-6);vectors.append(v)
        contours,hierarchy=cv2.findContours((z>.5).astype(np.uint8),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
        holes.append(0 if hierarchy is None else sum(int(h[3]>=0) for h in hierarchy[0]))
    return np.asarray(vectors,np.float32),np.asarray(holes)


def heuristic(query,atlas,same_page=False):
    start=perf_counter();q,qh=features(query);a,ah=features(atlas)
    if not len(q) or not len(a):return dict(pairs=[],seconds=perf_counter()-start,route='heuristic')
    score=cv2.gemm(q,a,1,None,0,flags=cv2.GEMM_2_T);score-=.2*np.minimum(abs(qh[:,None]-ah[None,:]),2)
    compatible=np.abs(np.log(np.array([g['aspect'] for g in query])[:,None]/np.array([g['aspect'] for g in atlas])[None,:]))<.18
    if same_page:compatible&=np.array([[not set(g['owners'])&set(h['owners']) for h in atlas] for g in query])
    score[~compatible]=-1;out=[]
    for i,g in enumerate(query):
        alts=[]
        for j in np.argsort(-score[i])[:3]:
            if score[i,j]<.65:continue
            alts.append(dict(atlas=int(j),similarity=float(score[i,j]),size_ratio=g['height']/atlas[j]['height'],informative=bool(g['aspect']>.25),counter_difference=int(qh[i]-ah[j])))
        if alts:out.append(dict(query=i,alternatives=alts))
    return dict(pairs=out,seconds=perf_counter()-start,route='heuristic',semantics='spatial occupancy plus observed counters; print damage can change counters')

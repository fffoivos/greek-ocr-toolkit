"""Ordered periodic dot chains shared by terminal and regional leader evidence.

This is geometry only. The two callers retain their independent photometry,
row purity and table acceptance rules. Batched edges preserve the original
first-successor choice, seed order, strict inequalities and missing-dot policy.
"""
import numpy as np


def chains(points,slope,height,*,pitch_max,vertical,horizontal,lookahead,min_remaining,missing=False):
    p=np.asarray(points);n=len(p)
    if n<min_remaining:return
    ii,jj=np.indices((n,n));dx=p[None,:,0]-p[:,None,0];dy=p[None,:,1]-p[:,None,1]-slope*dx
    seeds=(ii<n-min_remaining+1)&(jj>ii)&(jj<=ii+lookahead)&(dx>.35*height)&(dx<pitch_max*height)&(abs(dy)<=vertical*height)
    si,sj=np.nonzero(seeds);pitches=dx[si,sj]
    steps=2 if missing else 1
    edges=(jj>ii)&(dx<pitch_max*height*(steps+horizontal))&(abs(dy)<vertical*height)
    ei,ej=np.nonzero(edges);ex=dx[ei,ej]
    # Batches bound temporary memory independently of scan size; this is not
    # a geometric parameter or a limit on the number of candidate chains.
    for first in range(0,len(si),32):
        pitch=pitches[first:first+32];delta=ex[None,:]
        if missing:
            multiple=np.rint(delta/pitch[:,None]);valid=(multiple>=1)&(multiple<=2)&(abs(delta-multiple*pitch[:,None])<horizontal*pitch[:,None])
        else:valid=abs(delta-pitch[:,None])<horizontal*pitch[:,None]
        a,b=np.nonzero(valid);nexts=np.full((len(pitch),n),n,int)
        np.minimum.at(nexts,(a,ei[b]),ej[b])
        for k in range(len(pitch)):
            u,v=int(si[first+k]),int(sj[first+k]);chain=[u,v];last=v
            while nexts[k,last]<n:
                last=int(nexts[k,last]);chain.append(last)
            yield u,v,chain,float(pitch[k])

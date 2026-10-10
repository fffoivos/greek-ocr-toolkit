"""Optional feature B correction candidate, composed after Q8 separators.

No full-page stroke census or image mask is required to remove a supported
mirrored band or repeated ornament. Other feature renderings remain callable
diagnostics and do not silently become runtime dependencies.
"""
from time import perf_counter
from ..shared.ink_ownership import analyze
from ..shared.ink_motif_gate import inspect,coarse_scout
from ..layout_barriers.fast import run as separators


def ink_run(gray,items,*,detail=False):
    t=perf_counter();own=analyze(gray,items,detail=detail)
    back=set(own['suppress_indices'])
    h=own['height'];motifs=[];removed=set(back);motif_scout_s=0.;motif_refine_s=0.;nominated=0
    for i,item in enumerate(items):
        if i in back:continue
        t0=perf_counter();scouted=coarse_scout(gray,item,h);motif_scout_s+=perf_counter()-t0
        nominated+=bool(scouted)
        t0=perf_counter();m,_=inspect(gray,item,h,scouted=scouted);motif_refine_s+=perf_counter()-t0
        if detail or m['drop']:motifs.append(dict(line=i,**m))
        if m['drop']:removed.add(i)
    return dict(items=[q for i,q in enumerate(items) if i not in removed],removed=sorted(removed),
                ownership=own,motifs=motifs,ink_s=perf_counter()-t,
                scout_s=own['scout_s']+motif_scout_s,
                refinement_s=own['seconds']-own['scout_s']+motif_refine_s,
                motif_nominated=nominated)


def run(gray,items,*,detail=False):
    t=perf_counter();r2=separators(gray,items);out=ink_run(gray,r2['items'],detail=detail)
    out.update(r2=r2,added_s=perf_counter()-t)
    return out

"""Optional feature B correction candidate, composed after Q8 separators.

No full-page stroke census or image mask is required to remove a supported
mirrored band or repeated ornament. Other feature renderings remain callable
diagnostics and do not silently become runtime dependencies.
"""
from time import perf_counter
from .ink_ownership import analyze
from .ink_motif_gate import inspect,coarse_scout
from ..shared.contracts import bbox
from ..layout_barriers.fast import run as separators


def ink_run(gray,items,*,detail=False,height=None,ownership_evidence=None):
    """Run after separators. Supplied height must retain height_proxy semantics.

    Optional ownership_evidence must come from the same pixels and exact current
    item rectangles. Bounds/scale are checked; pixel identity is caller-owned.
    Reused computation is not charged again; its original timing stays in evidence.
    """
    t=perf_counter();reused=ownership_evidence is not None
    if reused:
        own=ownership_evidence
        if own.get('image_size')!=[gray.shape[1],gray.shape[0]] or [r['bbox'] for r in own['regions']]!=[bbox(q) for q in items]:
            raise ValueError('ownership evidence is not bound to these item rectangles/image size')
        if height is not None and own['height']!=height:raise ValueError('ownership evidence has a different height')
    else:own=analyze(gray,items,detail=detail,height=height)
    back=set(own['suppress_indices'])
    h=own['height'];motifs=[];removed=set(back);motif_scout_s=0.;motif_refine_s=0.;nominated=0;costs=[]
    for i,item in enumerate(items):
        if i in back:continue
        t0=perf_counter();scouted=coarse_scout(gray,item,h);scout_s=perf_counter()-t0;motif_scout_s+=scout_s
        nominated+=bool(scouted)
        t0=perf_counter();m,_=inspect(gray,item,h,scouted=scouted);refine_s=perf_counter()-t0;motif_refine_s+=refine_s
        costs.append(dict(line=i,coarse_s=scout_s,refine_s=refine_s,nominated=bool(scouted),reason=m['reason']))
        if detail or m['drop']:motifs.append(dict(line=i,**m))
        if m['drop']:removed.add(i)
    return dict(items=[q for i,q in enumerate(items) if i not in removed],removed=sorted(removed),
                ownership=own,motifs=motifs,ink_s=perf_counter()-t,
                scout_s=(0. if reused else own['scout_s'])+motif_scout_s,
                refinement_s=(0. if reused else own['seconds']-own['scout_s'])+motif_refine_s,
                motif_nominated=nominated,motif_costs=costs,ownership_reused=reused)


def run(gray,items,*,detail=False):
    t=perf_counter();r2=separators(gray,items);out=ink_run(gray,r2['items'],detail=detail)
    out.update(r2=r2,added_s=perf_counter()-t)
    return out

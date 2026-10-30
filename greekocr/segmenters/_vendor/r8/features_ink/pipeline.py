"""Optional feature B correction candidate, composed after Q8 separators.

No full-page stroke census or image mask is required to remove a supported
mirrored band or repeated ornament. Other feature renderings remain callable
diagnostics and do not silently become runtime dependencies.
"""
from time import perf_counter
from ..shared.ink_ownership import analyze
from ..shared.ink_motif_gate import inspect,coarse_scout
from ..shared.contracts import bbox
from ..shared.ink_seal import render as seal_render
from ..shared.ink_solid import render as solid_render
from ..shared.ink_discrete_motifs import scout as discrete_scout, verify as discrete_verify, layout_candidates
from ..layout_barriers.fast import run as separators


def ink_run(gray,items,*,detail=False,height=None,ownership_evidence=None,tone_samples=None,glyph_output=None):
    """Run after separators. Supplied height must retain height_proxy semantics.

    Optional ownership_evidence must come from the same pixels and exact current
    item rectangles. Bounds/scale are checked; pixel identity is caller-owned.
    Reused computation is not charged again; its original timing stays in evidence.
    """
    t=perf_counter();reused=ownership_evidence is not None
    if reused:
        own=ownership_evidence
        if own.get('version')!='B5':raise ValueError('ownership evidence uses a different source policy')
        if own.get('image_size')!=[gray.shape[1],gray.shape[0]] or [r['bbox'] for r in own['regions']]!=[bbox(q) for q in items]:
            raise ValueError('ownership evidence is not bound to these item rectangles/image size')
        if height is not None and own['height']!=height:raise ValueError('ownership evidence has a different height')
    else:own=analyze(gray,items,detail=detail,height=height,tone_samples=tone_samples,glyph_output=glyph_output)
    back=set(own['suppress_indices'])
    h=own['height'];seal=seal_render(gray,items,h,route='explicit',candidate_indices=[i for i in own['weak_indices'] if i not in back])
    seals=set(seal['suppress_indices']);reasons={i:'back print' for i in back};reasons.update({i:'seal rim' for i in seals})
    motifs=[];removed=set(back)|seals;motif_scout_s=0.;motif_refine_s=0.;nominated=0;costs=[]
    for i,item in enumerate(items):
        if i in removed:continue
        t0=perf_counter();scouted=coarse_scout(gray,item,h);scout_s=perf_counter()-t0;motif_scout_s+=scout_s
        nominated+=bool(scouted)
        t0=perf_counter();m,_=inspect(gray,item,h,scouted=scouted);refine_s=perf_counter()-t0;motif_refine_s+=refine_s
        costs.append(dict(line=i,coarse_s=scout_s,refine_s=refine_s,nominated=bool(scouted),reason=m['reason']))
        if detail or m['drop']:motifs.append(dict(line=i,**m))
        if m['drop']:removed.add(i);reasons[i]='ornament'
    # Compact isolated masses use their own native stroke/counter evidence.
    # Faintness and the frame interior are not non-text certificates.
    solid=solid_render(gray,[q['polygon'] for q in items],h)
    for i in solid.indices:
        if int(i) not in removed:removed.add(int(i));reasons[int(i)]='solid ink mass'
    extra_refine=0.;extra=[];t0=perf_counter()
    layout=layout_candidates(items,h);extra_scout=perf_counter()-t0
    for nominee in layout:
        i=nominee['line'];item=items[i]
        if i in removed:continue
        t0=perf_counter();extra_nomination=discrete_scout(gray,item,h);extra_scout+=perf_counter()-t0
        if not extra_nomination:continue
        t0=perf_counter();m=discrete_verify(gray,item,h,scouted=True)
        elapsed=perf_counter()-t0;extra_refine+=elapsed
        extra.append(dict(line=i,layout=nominee,seconds=elapsed,**m))
        if m['drop']:removed.add(i);reasons[i]='ornament'
    return dict(items=[q for i,q in enumerate(items) if i not in removed],removed=sorted(removed),
                ownership=own,motifs=motifs,seals=seal,solid=dict(indices=solid.indices.tolist(),disks=solid.disks.tolist(),seconds=solid.seconds),discrete=extra,removal_reasons=reasons,seal_s=seal['seconds'],discrete_scout_s=extra_scout,discrete_refinement_s=extra_refine,ink_s=perf_counter()-t,
                scout_s=(0. if reused else own['scout_s'])+motif_scout_s+seal['scout_s']+extra_scout,
                refinement_s=(0. if reused else own['seconds']-own['scout_s'])+motif_refine_s+seal['seconds']-seal['scout_s']+extra_refine+solid.seconds,
                motif_nominated=nominated,motif_costs=costs,ownership_reused=reused)


def run(gray,items,*,detail=False):
    t=perf_counter();r2=separators(gray,items);out=ink_run(gray,r2['items'],detail=detail)
    out.update(r2=r2,added_s=perf_counter()-t)
    return out

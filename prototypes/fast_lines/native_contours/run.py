"""A01 owns all fixed-map DB control studies."""
from time import perf_counter
from ...fast_lines.shared.detector import postprocess,VARIANTS
from ...fast_lines.shared.contracts import result

def run(ctx,phase=3):
    names=('quad','poly') if phase==1 else tuple(VARIANTS)
    variants={}; times={}; traces={}
    for name in names:
        t=perf_counter(); items,genealogy=postprocess(ctx.pm,ctx.size,VARIANTS[name],genealogy=True)
        times[name]=perf_counter()-t; variants[name]=items; traces[name]=genealogy
    return result(variants['poly'],variants=variants,variant_seconds=times,genealogy=traces,
                  regions=[],status='native poly candidate; no ownership claim',selected='poly',
                  counts={k:len(v) for k,v in variants.items()})

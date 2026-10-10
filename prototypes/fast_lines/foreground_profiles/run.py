"""A05: contrast, normalised edge and persistence witnesses; ownership can abstain."""
import numpy as np
from ..shared.image_evidence import profile_features
from ..shared.contracts import bbox,result

def run(ctx,phase=3):
    e=ctx.ev; gx,gy=e.gradients; records=[]; refs={q['id']:q for q in ctx.reference.get('lines',[])}
    for i,item in enumerate(ctx.items):
        b=bbox(item); a=e.crop(e.contrast,b); x=e.crop(gx,b); y=e.crop(gy,b); p=e.crop(e.persistence,b)
        # Sparse physical profiles stand against the independently dense 1600-pixel reference.
        feat=profile_features(a[::3,::3],x[::3,::3],y[::3,::3],p[::3,::3])
        records.append(dict(line=i,bbox=b,features=feat))
    median={k:float(np.median([r['features'][k] for r in records])) if records else 0 for k in ('contrast','edge','persistence')}
    for r in records:
        f=r['features']; c=f['contrast']/max(median['contrast'],1e-6); ed=f['edge']/max(median['edge'],1e-6)
        r.update(contrast_only=c<.55,edge_only=ed<.65,combined=c<.55 and ed<.65,
                 ownership='unknown',reason='one raster does not identify source layer')
        if r['line'] in refs:
            dense=refs[r['line']]['features']; r['dense_difference']={k:f[k]-dense[k] for k in dense}
    grids=ctx.get('sheet_lattice').get('grids',[])
    return result(ctx.items,lines=records,relative_reference=median,competing_grids=grids,
                  regions=[r for r in records if r['combined']],status='unknown ownership retained; pale and sharp ghost counterexamples not deleted',
                  counts=dict(contrast=sum(r['contrast_only'] for r in records),edge=sum(r['edge_only'] for r in records),combined=sum(r['combined'] for r in records)))

"""A09: sole owner of larger-input and scale/unbend crop inference."""
from time import perf_counter
import cv2,numpy as np
from ..shared.detector import postprocess,VARIANTS
from ..shared.geometry import roi
from ..shared.contracts import result,deduplicate

def field_shift(ctx,x,y):
    shift=np.zeros_like(x,dtype=np.float32)
    for f in ctx.get('sheet_lattice').get('fields',[]):
        if 'coef' not in f: continue
        a,b,c,d=f['bbox']; in_block=(x>=a)&(x<c)&(y>=b)&(y<d)
        value=np.polynomial.polynomial.polyval((x-a)/max(c-a,1),f['coef'])*f['height']
        shift[in_block]=value[in_block]
    return shift

def run(ctx,phase=3):
    if ctx.detector is None: raise ValueError('shared detector required')
    t=perf_counter(); pm,meta=ctx.detector.infer(ctx.gray,1440); full=postprocess(pm,ctx.size,VARIANTS['poly']); full_s=perf_counter()-t
    requests=ctx.get('residual_ledger').get('requests',[])
    # Bounded diagnostic budget; explicitly list unscheduled requests. No page/category lookup.
    eligible=sorted(requests,key=lambda r:-(r['bbox'][2]-r['bbox'][0])*(r['bbox'][3]-r['bbox'][1]))
    chosen=eligible[:3]; records=[]; variants={name:[] for name in ('scale','unbend','combined')}
    for request in chosen:
        x0,y0,x1,y1=roi(request['bbox'],ctx.gray.shape); crop=ctx.gray[y0:y1,x0:x1]
        if not crop.size: continue
        xs,ys=np.meshgrid(np.arange(crop.shape[1],dtype=np.float32)+x0,np.arange(crop.shape[0],dtype=np.float32)+y0)
        shift=field_shift(ctx,xs,ys)
        flat=cv2.remap(ctx.gray,xs,ys+shift,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=255)
        for name in variants:
            image=crop if name=='scale' else flat
            long_side=960 if name in ('scale','combined') else max(32,round(max(crop.shape)*960/max(ctx.gray.shape)/32)*32)
            t=perf_counter(); mp,mt=ctx.detector.infer(image,long_side); lines=postprocess(mp,(crop.shape[1],crop.shape[0]),VARIANTS['poly'])
            for q in lines:
                poly=np.asarray(q['polygon'],float)+[x0,y0]
                if name!='scale': poly[:,1]+=field_shift(ctx,poly[:,0].astype(np.float32),poly[:,1].astype(np.float32))
                q['polygon']=poly.tolist(); q['source_ids']=[request['id']]; q['provenance']=f'{name} crop; inherited score'
            variants[name]+=lines
            records.append(dict(request=request['id'],bbox=[x0,y0,x1,y1],variant=name,seconds=perf_counter()-t,**mt,
                max_shift=float(abs(shift).max()),items=len(lines),remap='original x=crop x+x0, original y=crop y+y0+shared field'))
    retained,conflicts=deduplicate(ctx.items,variants['combined'])
    return result(retained,full_page=full,full_page_seconds=full_s,full_page_meta=meta,variants=variants,calls=records,
        regions=[dict(bbox=r['bbox']) for r in chosen],unprocessed_requests=[r['id'] for r in eligible[3:]],conflicts=conflicts,
        new_candidates=len(retained)-len(ctx.items),status='bounded crop candidates; unscheduled requests remain unresolved')

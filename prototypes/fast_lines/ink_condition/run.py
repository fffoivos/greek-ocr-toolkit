"""A10 owns condition inference; stroke operators are shared with A12."""
import numpy as np
from ..shared.image_evidence import stroke_features,components
from ..shared.contracts import bbox,result

def run(ctx,phase=3):
    e=ctx.ev; families=ctx.get('font_guides').get('lines',[]); fam={q['line']:q['family'] for q in families}; samples=[]
    for i,item in enumerate(ctx.items):
        b=bbox(item); binary=e.crop(e.persistence>=2,b).astype(np.uint8)
        if not binary.size or not binary.any(): continue
        st=stroke_features(binary); _,stats,_=components(binary); widths=2*st['distance'][st['skeleton']>0]/max(e.body,1e-6)
        samples.append(dict(line=i,bbox=b,family=fam.get(i),contrast=float(np.mean(e.crop(e.contrast,b)[binary>0])),
            width_h=float(np.median(widths)) if len(widths) else 0.,width_iqr_h=float(np.ptp(np.percentile(widths,[25,75]))) if len(widths) else 0.,
            components=len(stats),endpoint_density=float(st['endpoints'].sum()/max(binary.sum(),1)),holes=st['holes'],readability='unknown'))
    for q in samples:
        peers=[r for r in samples if r['family']==q['family']]
        width=np.median([r['width_h'] for r in peers]); ends=np.median([r['endpoint_density'] for r in peers])
        q['family_relative_width']=q['width_h']/max(float(width),1e-6)
        q['hypothesis']='filled-or-native-weight' if q['family_relative_width']>1.6 else ('fragmented-or-detached-marks' if q['endpoint_density']>1.8*max(float(ends),1e-6) else 'unknown')
        q['smooth_width_h']=float(np.median([r['width_h'] for r in peers if abs(r['bbox'][1]-q['bbox'][1])<12*ctx.height] or [q['width_h']]))
    return result(ctx.items,samples=samples,regions=[q for q in samples if q['hypothesis']!='unknown'],status='independent axes; no automatic readability or restoration')

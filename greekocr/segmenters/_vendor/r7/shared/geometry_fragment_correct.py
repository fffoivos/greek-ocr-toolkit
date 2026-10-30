"""Join curled detector fragments only after two-ended native-ink agreement.

Keeps the entire old polygon envelopes. This repairs a fragmented curved end,
not a fully missing line, and does not claim an exact typographic baseline.
Original source indices survive removals/splits; ambiguous alternatives abstain.
"""
from collections import Counter
from time import perf_counter
import cv2
import numpy as np
from .contracts import bbox
from .geometry import roi,quantize
from .geometry_contacts import render_contacts
from .geometry_fragments import candidates
from .geometry_joinbarriers import inspect as inspect_rules


def envelope(items,shape,path=None,height=None):
    """Union old polygons with the measured body bridge; preserve old pixels."""
    points=np.concatenate([np.asarray(q['polygon']) for q in items])
    x0,y0,x1,y1=roi([*points.min(0)-2,*points.max(0)+2],shape)
    old=np.zeros((y1-y0,x1-x0),np.uint8)
    for q in items:cv2.fillPoly(old,[np.rint(np.asarray(q['polygon'])-[x0,y0]).astype(np.int32)],1)
    support=old.copy()
    if path is not None:
        p=np.asarray(path);inside=(p[:,0]>=points[:,0].min())&(p[:,0]<=points[:,0].max());p=p[inside]
        bridge=np.vstack([p-[0,.65*height],(p+[0,.65*height])[::-1]])
        cv2.fillPoly(support,[np.rint(bridge-[x0,y0]).astype(np.int32)],1)
    xx=np.flatnonzero(support.any(0));top=np.argmax(support[:,xx],axis=0);bottom=len(old)-1-np.argmax(support[::-1,xx],axis=0)
    xs=np.arange(xx[0],xx[-1]+1)
    upper=np.floor(np.interp(xs,xx,top));lower=np.ceil(np.interp(xs,xx,bottom))
    polygon=np.vstack([np.c_[xs,upper],np.c_[xs[::-1],lower[::-1]]])+[x0,y0]
    polygon=cv2.approxPolyDP(polygon.astype(np.float32),.25,True).reshape(-1,2)
    new=np.zeros_like(old);cv2.fillPoly(new,[np.rint(polygon-[x0,y0]).astype(np.int32)],1)
    return polygon.tolist(),old,new,(x0,y0,x1,y1)


def run(gray,original_items,items=None,*,witness=None,rendering=None,forbidden_regions=(),field_cache=None,local_filter=False):
    """Conditional correction. `items` must carry stable original `source_ids`.

    Omitting items means the unmodified original list. Precomputed witness and
    rendering costs belong to the caller, as recorded in reused flags.
    """
    start=perf_counter();size=(gray.shape[1],gray.shape[0])
    if items is None:items=[dict(q,source_ids=[i]) for i,q in enumerate(original_items)]
    if any('source_ids' not in q for q in items):raise ValueError('current items require original source_ids')
    if any(any(i<0 or i>=len(original_items) for i in q['source_ids']) for q in items):raise ValueError('source index out of range')
    counts=Counter(i for q in items for i in q['source_ids'])
    eligible={q['source_ids'][0]:j for j,q in enumerate(items) if not q.get('page_field') and len(q['source_ids'])==1 and counts[q['source_ids'][0]]==1}
    reused=dict(witness=witness is not None,rendering=rendering is not None)
    witness=candidates(original_items,size) if witness is None else witness
    pairs=[q for q in witness['pairs'] if q['line'] in eligible and q['fragment'] in eligible]
    decisions=[];joins=[];output=list(items)
    if pairs:
        selected={q['line'] for q in pairs}
        rendering=render_contacts(gray,original_items,'explicit_fast',7,selected,field_cache=field_cache,local_filter=local_filter) if rendering is None else rendering
        lines={q['line']:q for q in rendering['lines']};valid=[]
        # Resolve ownership against ALL original hypotheses, even a removed
        # alternative. Removal cannot make an ambiguous fragment suddenly safe.
        for pair in witness['pairs']:
            q=lines.get(pair['line']);a=next((a for a in q['alternatives'] if a['fragment']==pair['fragment']),None) if q else None
            if a and a['agrees']:valid.append(pair)
        nowners=Counter(q['fragment'] for q in valid)
        groups={}
        for p in pairs:
            q=lines[p['line']];a=next((a for a in q['alternatives'] if a['fragment']==p['fragment']),None)
            reason='two-ended native ink disagrees'
            if a and a['agrees']:
                # Untraced alternative owners also prevent a join.
                all_traced=all(z['line'] in lines for z in witness['pairs'] if z['fragment']==p['fragment'])
                if nowners[p['fragment']]!=1 or not all_traced:reason='ambiguous original ownership'
                else:
                    f=bbox(original_items[p['fragment']]);x=(f[0]+f[2])/2
                    path=np.asarray(a['path']);j=int(np.argmin(abs(path[:,0]-x)))
                    if not a['observed'][j] or not f[1] <= path[j,1] <= f[3]:reason='fragment has no localized body contact'
                    else:groups.setdefault(p['line'],[]).append(p['fragment']);reason='candidate'
            decisions.append(dict(line=p['line'],fragment=p['fragment'],reason=reason,
                                  overlap_h=a['overlap_h'] if a else 0,error_p90_h=a['error_p90_h'] if a else None))
        used=set();replacements={};h=witness['height']
        for main,fragments in groups.items():
            ids=[main]+sorted(set(fragments));indices=[eligible[i] for i in ids]
            if used.intersection(indices):continue
            selected_items=[items[j] for j in indices]
            polygon,old,new,(x0,y0,x1,y1)=envelope(selected_items,gray.shape,lines[main]['path'],h)
            reason=None
            barriers=inspect_rules(gray,polygon,h)
            gaps=[]
            ordered=sorted((bbox(q) for q in selected_items),key=lambda b:b[0])
            for left,right in zip(ordered,ordered[1:]):
                if right[0]>left[2]:gaps.append((left[2],right[0]))
            blocking=[z for z in barriers if z['rule'] is not None or any(
                lo<(z['candidate']['bbox'][0]+z['candidate']['bbox'][2])/2<hi for lo,hi in gaps)]
            if blocking:reason='regional printed-rule ownership unresolved'
            if np.any((old>0)&(new==0)):reason='old pixel lost'
            crop=gray[y0:y1,x0:x1];paper=cv2.boxFilter(crop,cv2.CV_32F,(quantize(3*h)|1,quantize(3*h)|1))
            ink=paper-crop>255*.06;extra=(new>0)&(old==0)
            for j,q in enumerate(items):
                if j in indices:continue
                b=bbox(q)
                if b[2]<x0 or b[0]>x1 or b[3]<y0 or b[1]>y1:continue
                other=np.zeros_like(old);cv2.fillPoly(other,[np.rint(np.asarray(q['polygon'])-[x0,y0]).astype(np.int32)],1)
                if np.any(extra&ink&(other>0)):reason='new envelope meets neighboring owned ink';break
            for region in forbidden_regions:
                b=region.get('bbox',bbox(region) if 'polygon' in region else None)
                if b is None:raise ValueError('forbidden region requires bbox or polygon')
                xx0=max(0,int(np.floor(b[0]-x0)));yy0=max(0,int(np.floor(b[1]-y0)))
                xx1=min(old.shape[1],int(np.ceil(b[2]-x0)));yy1=min(old.shape[0],int(np.ceil(b[3]-y0)))
                if xx1>xx0 and yy1>yy0 and extra[yy0:yy1,xx0:xx1].any():reason='new envelope enters rejected region';break
            if reason:
                decisions.append(dict(source_ids=ids,reason=reason,barriers=barriers));continue
            q=dict(items[eligible[main]],polygon=polygon,baseline=None,source_ids=ids,
                   centreline=lines[main]['path'],provenance='two-ended original-ink fragment envelope')
            replacements[eligible[main]]=q;used.update(indices)
            joins.append(dict(source_ids=ids,polygon=polygon,reason='two-ended original ink agrees; old pixels retained'))
        output=[replacements[j] if j in replacements else q for j,q in enumerate(items) if j not in used or j in replacements]
    return dict(items=output,joins=joins,decisions=decisions,seconds=perf_counter()-start,
                witness=witness,reused=reused)

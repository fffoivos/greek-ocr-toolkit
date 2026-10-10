"""Bracketed type-grid gaps → body ink → regional small-detector confirmation.

No statistical page classifier, reference lines, book/page names, or PDF text.
The typography census is deliberately NOT on the clean-page path. Table evidence
protects nominations; it never rewrites existing detector table cells.
"""
from time import perf_counter
import cv2
import numpy as np
from .type_lattice import analyze as lattice, point_ownership, inspect_slot
from .type_tables import analyze as tables
from .type_ink_ownership import analyze as ownership
from .type_completion import snap_components
from .type_barriers import protect
from .geometry import roi,mask
from .contracts import bbox
from .detector import postprocess,VARIANTS
from ..layout_barriers.fast import run as separators


def ink_ownership(gray,polygon,items,h):
    a,t,b,d=roi(bbox(dict(polygon=polygon)),gray.shape)
    g=gray[t:d,a:b];k=max(1,round(3*h))|1
    paper=cv2.morphologyEx(g,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8))
    ink=(paper.astype(float)-g)>.18*np.maximum(paper,1)
    candidate=mask([dict(polygon=(np.asarray(polygon)-[a,t]).tolist())],g.shape,(b-a,d-t))>0
    old=mask([dict(q,polygon=(np.asarray(q['polygon'])-[a,t]).tolist()) for q in items],g.shape,(b-a,d-t))>0
    support=ink&candidate
    return float(old[support].mean()) if support.any() else 1.


def run(gray,items,detector,*,version=1,skip_initial_separator=False,
        final_separators=True,grid_items=None,lattice_evidence=None,excluded_regions=()):
    """Recover using current ownership and an optional distinct grid view.

    `grid_items` has one quadrilateral per current item in exactly the same order.
    It estimates pitch only; actual `items` own ink, including curved ribbons.
    `excluded_regions` are rejected polygons/items (or [x0,y0,x1,y1] rectangles).
    Precomputed lattice must describe this same grid/current pair; its cost is
    caller-owned. The stack can skip both Q8 calls and apply its shared separator.
    """
    start=perf_counter();sep=None if skip_initial_separator else separators(gray,items)
    current=list(items if sep is None else sep['items']);after_sep=perf_counter()
    if grid_items is not None and len(grid_items)!=len(current):
        raise ValueError('grid_items must correspond one-to-one to current items')
    if lattice_evidence is None and grid_items is not None:
        from .type_lattice import blocks,gaps
        bb=blocks(grid_items,(gray.shape[1],gray.shape[0]))
        evidence=dict(blocks=bb,slots=[inspect_slot(gray,s,current,version=3) for s in gaps(bb,current)],raw_rows=[],route='heuristic',grid_view=True)
    else:evidence=lattice_evidence if lattice_evidence is not None else lattice(gray,current,route='heuristic',version=3)
    from .type_context import excluded,overlaps_exclusion
    rejected=excluded(excluded_regions)
    scout_end=perf_counter();runnable=[(i,s) for i,s in enumerate(evidence['slots']) if s['supported'] and s['owned_fraction']<.25]
    decisions=[];calls=[];added=[];table=None;layers=None;dense_checks=[]
    permitted=[]
    for idx,s in runnable:
        if any(point_ownership(s['body_centres'],rejected)):
            decisions.append(dict(slot=idx,reason='previously rejected region owns candidate ink'))
        else:permitted.append((idx,s))
    runnable=permitted
    if version>=4:
        confirmed=[]
        for idx,s in runnable:
            dense=inspect_slot(gray,s,current,dense=True,version=3);dense_checks.append(dict(slot=idx,evidence=dense))
            if dense['supported'] and dense['owned_fraction']<.25:confirmed.append((idx,dense))
            else:decisions.append(dict(slot=idx,reason='original-pixel contact or ownership disagrees'))
        runnable=confirmed
    if runnable:
        table=tables(gray,current,route='explicit',version=5 if version>=3 else 4)
        if version>=2:
            regions=[[s['x0'],s['y']-s['height'],s['x1'],s['y']+s['height']] for _,s in runnable]
            layers=ownership(gray,current,regions,detail=True)
    back_slots={runnable[j][0] for j in layers['suppress_indices']} if layers else set()
    for idx,s in runnable:
        h=s['height'];y=s.get('measured_y',s['y']);xm=s['xref']
        if idx in back_slots:
            decisions.append(dict(slot=idx,reason='independent reflected glyph evidence'));continue
        # Preserve uncertain aligned-cell hypotheses as well as confirmed rules.
        if any(r['bbox'][1]-h<y<r['bbox'][3]+h and r['bbox'][0]<s['x1'] and r['bbox'][2]>s['x0'] for r in table['regions']):
            decisions.append(dict(slot=idx,reason='regional table protection'));continue
        neighbours=[bbox(current[j]) for j in s['neighbours']]
        left=min([s['x0']]+[b[0] for b in neighbours]);right=max([s['x1']]+[b[2] for b in neighbours])
        a,t,b,d=roi([left-2*h,y-4*h-abs(s['slope'])*(right-left),right+2*h,y+4*h+abs(s['slope'])*(right-left)],gray.shape)
        crop=gray[t:d,a:b];side=min(960,max(32,round(max(crop.shape)*16/h/32)*32))
        pm,meta=detector.infer(crop,side);proposed=postprocess(pm,(b-a,d-t),VARIANTS['poly']);calls.append(dict(slot=idx,crop=[a,t,b,d],**meta))
        seeds=np.asarray(s['body_centres'],float)
        confirmed=False
        for q in proposed:
            p=np.asarray(q['polygon'],float)+[a,t]
            inside=np.asarray(point_ownership(seeds,[dict(polygon=p.tolist())]))
            if inside.sum()<5 or inside.mean()<.6:continue
            why='accept';owned=ink_ownership(gray,p,current+added,h)
            if overlaps_exclusion(p,rejected):why='overlaps previously rejected region'
            elif owned>=.25:why='existing ink ownership'
            elif p[:,0].min()<a+.15*h or p[:,0].max()>b-.15*h:why='crop edge truncation'
            else:
                # A regional line may not collect a second, separately boxed row.
                axes=np.asarray([bbox(z) for z in current+added],float).reshape(-1,4)
                centre=(axes[:,:2]+axes[:,2:])/2
                enclosed=point_ownership(centre,[dict(polygon=p.tolist())])
                if any(enclosed):why='contains existing line centre'
            decisions.append(dict(slot=idx,reason=why,owned_ink_fraction=owned,bbox=bbox(dict(polygon=p))))
            if why=='accept':
                q=dict(q,polygon=p.tolist(),baseline=None,provenance='type pitch gap + measured unowned body ink + regional Paddle',type_slot=idx)
                if version>=2:q=snap_components(gray,q,h,current+added)
                if overlaps_exclusion(q['polygon'],rejected):
                    decisions.append(dict(slot=idx,reason='completion overlaps previously rejected region'));continue
                pieces,barriers=protect(gray,q,h) if version>=3 else ([q],[])
                decisions.extend(dict(r,slot=idx,stage='regional separator protection') for r in barriers)
                added.extend(pieces);confirmed=bool(pieces)
        if not confirmed:decisions.append(dict(slot=idx,reason='no safe regional confirmation'))
    # Run Q8 on the combined items only when something was added. Its own grid
    # and bilateral clear-paper guards still apply to a new crossing polygon.
    final=separators(gray,current+added) if added and final_separators else None
    end=perf_counter()
    return dict(items=final['items'] if final else current+added,added=added,lattice=evidence,tables=table,ownership=layers,dense_checks=dense_checks,calls=calls,decisions=decisions,
                separator=sep,final_separator=final,type_s=end-after_sep,scout_s=scout_end-after_sep,correction_s=end-scout_end,
                added_s=end-start,version=version)

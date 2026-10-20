"""Offline same-call native input adapter. The i2 live consumer was withdrawn after returned-page/final-raster failures; this file is never imported by Stack."""
from types import SimpleNamespace
import numpy as np
from greekocr.glyphs.components import _xheight,_ransac_line,_fit_curve
from greekocr.pages import font


def measure(ctx,record):
    labels=ctx['labels'];stats=ctx['stats'];gray=ctx['gray'];width=labels.shape[1];models=[];receipts=[];components=[]
    for bi,k in enumerate(ctx['body_labels']):
        x,y,w,h,area=stats[k];at=labels[y:y+h,x:x+w]==k
        components.append([x,y,x+w,y+h,area,k,float(np.median(gray[y:y+h,x:x+w][at]))])
    table=np.asarray(components,float).reshape(-1,7);lookup={int(q[5]):q for q in table}
    for t,track in enumerate(record['tracks']):
        axis=ctx['tracks'][t]
        ids=[k for b,k in enumerate(ctx['body_labels']) if ctx['body_tracks'][b]==[t]
             and axis[0,0]<=ctx['centres'][k,0]<=axis[-1,0]
             and stats[k,0]>0 and stats[k,1]>0
             and stats[k,0]+stats[k,2]<labels.shape[1] and stats[k,1]+stats[k,3]<labels.shape[0]]
        receipt=dict(track=t,component_ids=ids,status='unknown',held_out='all detached marks; no disputed mark used for fitting')
        receipts.append(receipt)
        if len(ids)<font.MIN_BODY_SUPPORT:receipt['first_failure']='too few complete uniquely row-bound native bodies';continue
        rows=np.asarray([lookup[k] for k in ids]);initial=_xheight(rows[:,3]-rows[:,1]);receipt['initial_xheight']=initial;receipt['initial_scale_provenance']='conditional original _line_geometry free-component height mode; not final measured x-height'
        if initial<=0:receipt['first_failure']='no initial support';continue
        height=rows[:,3]-rows[:,1];w=rows[:,2]-rows[:,0];eligible=(w>=.3*initial)&(w<=1.8*initial)&(height>=.6*initial)&(height<=1.4*initial)&(rows[:,4]>=.08*initial**2)
        seeds=rows[eligible];xs=(seeds[:,0]+seeds[:,2])/2;ys=seeds[:,3]
        if len(seeds)<font.MIN_BODY_SUPPORT:receipt['first_failure']='too few original bottom-contact seed candidates';continue
        inlier=_ransac_line(xs,ys,.15*initial+1,np.random.default_rng(0));contacts=seeds[inlier]
        if len(contacts)<font.MIN_BODY_SUPPORT:receipt['first_failure']='too few agreeing bottom contacts';continue
        x0=int(np.ceil(((contacts[:,0]+contacts[:,2])/2).min()));x1=int(np.floor(((contacts[:,0]+contacts[:,2])/2).max()))+1
        if x1<=x0:receipt['first_failure']='empty observed contact domain';continue
        baseline,_=_fit_curve(xs[inlier],ys[inlier],width)
        receipt['initial_contacts']=[dict(label=int(q[5]),x=float((q[0]+q[2])/2),bottom=float(q[3])) for q in contacts];receipt['initial_contact_x_range']=[x0,x1]
        # Font evidence interpolates within line.x0:x1. Do not silently clamp
        # classes from components outside this observed baseline support.
        receipt['observed_native_body_ids']=ids
        ids=[k for k in ids if x0<=(lookup[k][0]+lookup[k][2])/2<x1]
        receipt['component_ids']=ids
        line=SimpleNamespace(x0=x0,x1=x1,baseline=baseline[x0:x1].copy(),xheight=initial,component_ids=tuple(ids),support=len(contacts),discounted=None)
        models.append((t,line,receipt))
    # Same-call compatible local row context, conditional; no page-scale claim.
    context=float(np.median([line.xheight for t,line,r in models])) if models else 0
    page=SimpleNamespace(labels=labels,components=table,xheight=context)
    for t,line,r in models:
        counts,points=font.evidence(page,line,_lookup=lookup);r['body_only_classes']=counts;r['body_only_contacts']=points
    if models:font.fit_guides(page,[line for t,line,r in models],_lookup=lookup)
    for t,line,r in models:
        r['contact_component_ids']={name:[dict(x=float(x),y=float(y),native_labels=[int(k) for k in line.component_ids if (lookup[k][0]+lookup[k][2])/2==x]) for x,y in points] for name,points in line.guide_samples.items()}
        r.update(classes=line.ink_classes,contacts=line.guide_samples,residuals=line.guide_residuals,borrowed=list(line.borrowed),xheight=line.xheight,finite_x=[line.x0,line.x1],geometry_source=line.geometry_source,guide_arrays={k:getattr(line,k).tolist() for k in font.GUIDES},initial_page_context=dict(value=context,provenance='conditional same-call row seed context; not global measured page font'),donors=[dict(track=n,size_ratio=other.xheight/line.xheight,compatible=font.BORROW_MIN_SIZE_RATIO<=other.xheight/line.xheight<=font.BORROW_MAX_SIZE_RATIO) for n,other,_ in models if n!=t])
        if 'baseline' in line.borrowed or 'meanline' in line.borrowed:r['first_failure']='baseline or meanline unsupported/borrowed';continue
        if not line.ink_classes['body_on_baseline'] or not (line.ink_classes['body_with_descender'] or line.ink_classes['tall_body']):r['first_failure']='small-body versus tall/descender class distinction unobserved';continue
        if line.guide_residuals['baseline']['p90']>font.GUIDE_INLIER_RESIDUAL_XH or line.guide_residuals['meanline']['p90']>font.GUIDE_INLIER_RESIDUAL_XH:r['first_failure']='class contact residual exceeds original inlier contract';continue
        r['status']='body guides observed; accent support conditional'
    return receipts


def choose(ctx,guides,label,*,legacy_bodies=None):
    """One row/class hypothesis using measured bands and original glyph reach."""
    from greekocr.glyphs.components import NEIGHBOUR_GAP_ABOVE,NEIGHBOUR_GAP_BELOW
    from greekocr.pages.lines import MARK_BODY_HORIZONTAL_REACH_XH,MARK_BODY_VERTICAL_REACH_XH
    x,y,w,h,area=ctx['stats'][label];cx,cy=ctx['centres'][label];options=[];protective=[]
    if legacy_bodies is not None and len(legacy_bodies)==1:
        old_tracks=ctx['body_tracks'][legacy_bodies[0]]
        old=next((g for g in guides if old_tracks==[g['track']]),None)
        if old is None or old['status']=='unknown' or not old['finite_x'][0]<=cx<old['finite_x'][1]:
            return None,dict(component=int(label),accepted=False,first_failure='existing singleton row lacks measured bands; competing class cannot be excluded',options=[],protective=[])
    for g in guides:
        if g['status']=='unknown' or 'guide_arrays' not in g:continue
        a,c=g['finite_x']
        if not a<=cx<c:continue
        def value(name):return float(np.interp(cx,np.arange(a,c),g['guide_arrays'][name]))
        xh=g['xheight'];base=value('baseline');mean=value('meanline')
        nearby=[]
        for b,k in enumerate(ctx['body_labels']):
            if ctx['body_tracks'][b]!=[g['track']] or k not in g['component_ids']:continue
            bx,by,bw,bh,_=ctx['stats'][k];dx=max(x-bx-bw,bx-x-w,0);dy=max(y-by-bh,by-y-h,0)
            if dx<=MARK_BODY_HORIZONTAL_REACH_XH*xh and dy<=MARK_BODY_VERTICAL_REACH_XH*xh:nearby.append((2*dx+dy,b,k))
        if not nearby:continue
        # Original glyph role contract: below-baseline/neighbouring marks are
        # not reinterpreted as upper accents. This scope does not certify a
        # below-mark class; it only keeps that interpretation protective.
        if y<=base+NEIGHBOUR_GAP_BELOW*xh and cy>=base-.1*xh:
            protective.append(dict(track=g['track'],reason='within original below-baseline/punctuation neighbourhood; unconverted class'))
        if not (cy<mean+.1*xh and y+h>=mean-NEIGHBOUR_GAP_ABOVE*xh):continue
        if not value('accent_top')<=cy<=value('accent_bottom'):continue
        donors=[];heights=[]
        for donor in guides:
            if donor['status']=='unknown' or 'guide_arrays' not in donor:continue
            da,dc=donor['finite_x'];ratio=donor['xheight']/xh
            if not (da<=cx<dc and font.BORROW_MIN_SIZE_RATIO<=ratio<=font.BORROW_MAX_SIZE_RATIO):continue
            tops=donor['contacts']['accent_top'];bottoms=dict(donor['contacts']['accent_bottom'])
            observed=[bot-t for xx,t in tops if (bot:=bottoms.get(xx)) is not None]
            if observed:
                donors.append(dict(track=donor['track'],size_ratio=ratio,contacts=len(observed),observed_x=[min(q[0] for q in tops),max(q[0] for q in tops)]));heights.extend(v/ratio for v in observed)
        if not heights or h<min(heights):continue  # observed class extent, no invented speck floor
        score,b,k=min(nearby)
        options.append(dict(track=g['track'],body=b,label=k,class_hypothesis='mark_above',baseline=base,meanline=mean,accent_band=[value('accent_top'),value('accent_bottom')],borrowed=g['borrowed'],donors=donors,class_extent_min=float(min(heights)),body_reach_score=float(score)))
    receipt=dict(component=int(label),options=options,protective=protective,accepted=False,first_failure=None)
    if len(options)!=1 or protective:receipt['first_failure']='guide/class hypotheses unresolved or conflicting';return None,receipt
    receipt['accepted']=True;receipt['owner']=options[0]
    return [options[0]['body']],receipt

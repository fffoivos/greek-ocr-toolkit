"""Explicit field-local complete support and class-contact experiment.

Not imported by the accepted Stack. Component completion is independent of
residual permission; conditional font classification is not ground truth.
"""
from types import SimpleNamespace
from time import perf_counter
import cv2
import numpy as np
from greekocr.glyphs.components import _line_geometry
from greekocr.pages.font import evidence
from ..shared import observations as obs
from ..shared.geometry import roi


def complete_field(gray, request, height):
    """Follow components out of an engineering ROI using complete operator halo.

    Closing has two radius-(k//2) passes. The inner mask is cropped only after
    both; selected components touching its edge enlarge the measurement domain.
    Page-edge contacts remain incomplete. No mask grants ownership.
    """
    start=perf_counter();k=max(1,round(3*height))|1;halo=k-1
    requested=np.asarray(roi(request,gray.shape));region=requested.copy();passes=[]
    while True:
        a,t,b,d=map(int,region);outer=np.array(roi([a-halo,t-halo,b+halo,d+halo],gray.shape));x,y,z,w=outer
        ink=obs.ink(gray[y:w,x:z],k,method='closing',threshold=.18,arithmetic='relative')
        native=ink[t-y:d-y,a-x:b-x].copy();_,labels,stats,centres=obs.components(native)
        l,u,r,v=requested;selected=np.unique(labels[u-t:v-t,l-a:r-a]);selected=selected[selected>0]
        edges=np.zeros(4,bool)
        if len(selected):
            bounds=stats[selected,:4];edges=np.array([(bounds[:,0]==0).any(),(bounds[:,1]==0).any(),(bounds[:,0]+bounds[:,2]==b-a).any(),(bounds[:,1]+bounds[:,3]==d-t).any()])
        enlarged=np.array(roi([a-halo*edges[0],t-halo*edges[1],b+halo*edges[2],d+halo*edges[3]],gray.shape))
        passes.append(dict(region=region.tolist(),operator_roi=outer.tolist(),pixels=int(ink.size),selected_components=len(selected)))
        if np.array_equal(enlarged,region):break
        region=enlarged
    edge_ids=np.flatnonzero((stats[:,0]==0)|(stats[:,1]==0)|(stats[:,0]+stats[:,2]==native.shape[1])|(stats[:,1]+stats[:,3]==native.shape[0]));edge_ids=edge_ids[edge_ids>0]
    na,nt,nb,nd=requested
    nomination=obs.ink(gray[nt:nd,na:nb],k,method='closing',threshold=.18,arithmetic='relative')
    _,nomination_labels,nomination_stats,_=obs.components(nomination)
    return dict(incomplete_component_ids=edge_ids.tolist(),nomination_labels=nomination_labels,nomination_stats=nomination_stats,origin=[a,t],bounds=region.tolist(),requested=requested.tolist(),mask=native,labels=labels,stats=stats,centres=centres,selected=selected,passes=passes,seconds=perf_counter()-start,window=k)


def measure_chain(gray, row, bodies, prepared, *, font_prior=None):
    """Candidate paired contacts on complete components, with full provenance.

    The starting crop fit has its own unvalidated component-class assumptions.
    Pairing top/bottom of the same component avoids extrapolated-guide height,
    but does not magically identify a small letter. Review negatives explicitly.
    """
    x,y=prepared['origin'];labels=prepared['labels'];stats=prepared['stats'];ids=[];mapping=[]
    for i in row['components']:
        a,t,b,d=map(int,bodies[i]['bbox']);l,u,r,v=roi([a-x,t-y,b-x,d-y],labels.shape)
        na,nt,_,_=prepared['requested'];ns=prepared['nomination_stats'];nb=np.c_[ns[:,0]+na,ns[:,1]+nt,ns[:,0]+ns[:,2]+na,ns[:,1]+ns[:,3]+nt]
        match=np.flatnonzero(np.all(nb==[a,t,b,d],axis=1))
        seed=np.isin(prepared['nomination_labels'][t-nt:d-nt,a-na:b-na],match) if len(match) else np.zeros((d-t,b-a),bool)
        found=np.unique(labels[u:v,l:r][seed]);found=found[found>0];ids.extend(found.tolist());mapping.append(dict(nomination=i,nomination_label_ids=match.tolist(),measurement_ids=found.tolist()))
    ids=sorted(set(ids));bounds=stats[ids,:4].copy() if ids else np.empty((0,4),int)
    if not ids:return dict(status='unknown',body_height_px=None,reason='no complete mapped support',mapping=mapping)
    bounds[:,2:]+=bounds[:,:2];bounds+=np.array([x,y,x,y]);h=row['height']
    l,u,r,v=roi([bounds[:,0].min()-h,bounds[:,1].min()-h,bounds[:,2].max()+h,bounds[:,3].max()+h],gray.shape)
    # Reuse the field mask; do not binarise each chain with a different border.
    l=max(l,x);u=max(u,y);r=min(r,prepared['bounds'][2]);v=min(v,prepared['bounds'][3]);crop=gray[u:v,l:r]
    support=prepared['mask'][u-y:v-y,l-x:r-x].astype(bool)
    path=np.asarray(row['path']);focus=(float(np.median(path[:,1])-u-h/2),float(np.median(path[:,1])-u+h/2))
    fit=_line_geometry(crop,xh_prior=None,focus=focus,ink=support)
    components=[];component_ids={}
    for c in fit.components:
        if c.role!='letter':continue
        full=np.unique(labels[u-y+c.y0:u-y+c.y1,l-x+c.x0:l-x+c.x1][fit.labels[c.y0:c.y1,c.x0:c.x1]==c.index]);full=full[full>0]
        component_ids[c.index]=full.tolist()
        if len(full) and set(full).issubset(ids):components.append(c)
    arr=np.array([[c.x0,c.y0,c.x1,c.y1,c.area,c.index,0] for c in components]).reshape(-1,7)
    line=SimpleNamespace(xheight=fit.band.xh,baseline=fit.band.bottom,x0=0,x1=r-l,component_ids=np.array([c.index for c in components]))
    p=SimpleNamespace(labels=fit.labels,components=arr,xheight=fit.band.xh if font_prior is None else font_prior)
    classes,contacts=evidence(p,line);pairs=[]
    for c in components:
        cx=(c.x0+c.x1)/2
        top=[q[1] for q in contacts['meanline'] if q[0]==cx];bottom=[q[1] for q in contacts['baseline'] if q[0]==cx]
        if top and bottom and not c.touches:
            full=np.unique(labels[u-y+c.y0:u-y+c.y1,l-x+c.x0:l-x+c.x1][fit.labels[c.y0:c.y1,c.x0:c.x1]==c.index]);full=full[full>0]
            pairs.append(dict(crop_component=int(c.index),field_component_ids=full.tolist(),x=cx+l,top=top[0]+u,bottom=bottom[0]+u,height=bottom[0]-top[0]))
    value=float(np.median([q['height'] for q in pairs])) if pairs else None
    return dict(status='candidate' if pairs else 'unknown',body_height_px=value,reason='paired conditional small-body contacts; class identity not certified',crop=[l,u,r,v],mapping=mapping,crop_to_native_ids=component_ids,selected_crop_ids=[int(c.index) for c in components],complete_bounds=bounds.tolist(),incomplete_mapped_ids=sorted(set(ids)&set(prepared['incomplete_component_ids'])),font_prior=font_prior,font_prior_semantics='offline pixel preparation prior, conditional not a compatible donor',starting_scale=fit.band.xh,starting_scale_source=fit.band.xh_source,capital_adjusted_scale=line.xheight,starting_baseline=(fit.band.bottom+u).tolist(),classes=classes,contacts=contacts,pairs=pairs,spatial_validity=[min(q['x'] for q in pairs),max(q['x'] for q in pairs)] if pairs else None)

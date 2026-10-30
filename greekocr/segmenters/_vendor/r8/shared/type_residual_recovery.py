"""Conditional missing-row recovery from explicit body contacts.

The scout is deliberately weaker than the native witness. Native contact chains,
regional Paddle localization, and independent exclusion/ownership checks must
agree. A front/unknown classification alone never certifies recovery.
"""
from time import perf_counter
import cv2
import numpy as np
from .type_residual import ink_scout, render
from .geometry import roi, line_axis
from .contracts import bbox, merge_requests
from .type_lattice import point_ownership
from .type_context import excluded, overlaps_exclusion, grid_view
from .type_completion import snap_components, complete_request
from .type_barriers import protect
from .ink_ownership import analyze as ownership
from .ink_motif_gate import inspect as motif
from .ink_recurrence import render as recurrence
from .detector import postprocess, VARIANTS
from .type_contact_band import narrow
from .type_tables import box_grid, analyze as table_render
from .geometry_joinbarriers import inspect as rule_contacts
from ..layout_barriers.fast import clip_polygon


def axis_context(items):
    """Immutable geometry view for this recovery call's existing polygons."""
    view=grid_view(items)
    return [(bbox(q),line_axis(q)) for q in view]


def competing_axis(q,items,height,margin=0.,*,context=None):
    """Test existing rows in the shared x interval, not just a global centroid."""
    a=bbox(q);polygon=np.asarray(q['polygon'],np.float32)
    for b,axis in axis_context(items) if context is None else context:
        left=max(a[0],b[0]);right=min(a[2],b[2])
        if right-left<height:continue
        x=(left+right)/2
        distance=cv2.pointPolygonTest(polygon,(float(x),float(axis[0]+axis[1]*x)),True)
        if distance>=-margin*height:return True
    return False


def supported_extent(q):
    """Keep the regional envelope, restricting x only when its ends are unsafe."""
    left,right=q['type_support_bounds'];p=clip_polygon(q['polygon'],0.,left,-1)
    p=clip_polygon(p,0.,right,1) if len(p)>=3 else []
    return dict(q,polygon=p) if len(p)>=3 else None


def requests(scout, shape):
    h=scout['height'];out=[]
    for i,r in enumerate(scout['regions']):
        a,t,b,d=r['bbox']
        out.append(dict(id=str(i),bbox=roi([a-2*h,t-2*h,b+2*h,d+2*h],shape),
                        derivation=[i],dependencies=[]))
    return merge_requests(out)


def field(gray,items,request,height,excluded_regions,version=2):
    a,t,b,d=map(int,request['bbox'])
    def shift(qq):return [dict(q,polygon=(np.asarray(q['polygon'])-[a,t]).tolist()) for q in qq]
    r=render(gray[t:d,a:b],shift(items),height=height,route='slow',version=version,
             excluded_regions=shift(excluded_regions))
    for q in r['bodies']:
        q['bbox']=(np.array(q['bbox'])+[a,t,a,t]).tolist()
        q['centre']=(np.array(q['centre'])+[a,t]).tolist()
    for q in r['rows']:
        q['path']=(np.array(q['path'])+[a,t]).tolist()
        q['bbox']=(np.array(q['bbox'])+[a,t,a,t]).tolist()
    return r


def piece_support(piece,points,added,height):
    """Evidence on one side of a separator never authorizes the other side."""
    seeds=np.asarray(points,float).reshape(-1,2)
    here=np.array(point_ownership(seeds,[piece]),bool) & ~np.array(point_ownership(seeds,added),bool)
    return bool(here.sum()>=5 and np.ptp(seeds[here,0])>=4*height)


def candidate_motif(gray,item,page_height):
    """B's existing four-copy scout nominates its unchanged full verifier."""
    rec=recurrence(gray,item,page_height,route='heuristic')
    result=(motif(gray,item,page_height,diagnostic=True)[0] if rec['nominate'] else
            dict(drop=False,reason='spatial recurrence absent; ornament ownership unknown'))
    return dict(result,recurrence=rec)


def recover(gray,items,detector,*,excluded_regions=(),version=11,scout_evidence=None,column_evidence=None,tone_samples=None,glyph_samples=(),complete_rows=True,retain_support=False):
    start=perf_counter();rejected=excluded(excluded_regions)
    sc=ink_scout(gray,items,excluded_regions=rejected,version=5) if scout_evidence is None else scout_evidence
    scout_end=perf_counter();table=None;axes=axis_context(items)
    centres_existing=[((np.asarray(b)[:2]+np.asarray(b)[2:])/2).tolist() for b in map(bbox,items)]
    if version>=6 and sc['regions'] and box_grid(items,sc['height'],3)[0]:
        table=table_render(gray,items,route='explicit',version=5)
        rejected=rejected+excluded([r['bbox'] for r in table['regions'] if r['status']=='protect'])
    reqs=requests(sc,gray.shape);fields=[];calls=[];decisions=[];proposals=[]
    for ri,req in enumerate(reqs):
        data=field(gray,items,req,sc['height'],rejected,version=4 if version>=9 else 2);fields.append(data)
        eligible=[]
        for row_id,r in enumerate(data['rows']):
            free=[i for i in r['free'] if not data['bodies'][i]['interior_owned']] if version>=9 else ([i for i in r['free'] if not data['bodies'][i]['touched']] if version>=8 else r['free'])
            if len(free)<5:continue
            points=np.array([data['bodies'][i]['centre'] for i in free])
            if np.ptp(points[:,0])<4*r['height']:continue
            if version==7 and sum(data['bodies'][i]['touched'] for i in free)>=3:
                decisions.append(dict(request=ri,reason='existing polygons already touch a body chain',body_indices=free));continue
            eligible.append(dict(r,free=free,row_id=row_id))
        if not eligible:continue
        a,t,b,d=map(int,req['bbox']);local_h=float(np.median([r['height'] for r in eligible]))
        crop=gray[t:d,a:b];side=min(960,max(32,round(max(crop.shape)*16/local_h/32)*32))
        pm,meta=detector.infer(crop,side);found=postprocess(pm,(b-a,d-t),VARIANTS['poly'])
        calls.append(dict(request=ri,crop=req['bbox'],height=local_h,**meta))
        centres=[q['centre'] for q in data['bodies']]
        for q in found:
            p=np.asarray(q['polygon'])+[a,t];inside=np.array(point_ownership(centres,[dict(polygon=p.tolist())]))
            support=[]
            for row in eligible:
                free=[i for i in row['free'] if inside[i]]
                if len(free)>=5 and np.ptp(np.array([centres[i] for i in free])[:,0])>=4*row['height']:
                    support.append((row,free))
            if not support:continue
            q=dict(q,polygon=p.tolist(),baseline=None,provenance='native unowned body contacts + regional Paddle',type_residual=ri)
            if version>=11 and complete_rows:q['type_support_chains']=[dict(row=r['row_id'],components=r['components'],observed=ids) for r,ids in support]
            if version>=8:q['type_witness_points']=[centres[i] for i in sorted({i for _,ids in support for i in ids})]
            if version>=4:
                body_ids=(sorted({i for _,ids in support for i in ids}) if version==4 else
                          [i for i,z in enumerate(data['bodies']) if inside[i] and not z['owned'] and not z['rejected']])
                boxes=np.array([data['bodies'][i]['bbox'] for i in body_ids])
                left=float(boxes[:,0].min())-.5*local_h;right=float(boxes[:,2].max())+.5*local_h
                q=dict(q,type_support_bounds=[left,right])
                unsafe=(overlaps_exclusion(p,rejected) or competing_axis(q,items,local_h,context=axes) or
                        p[:,0].min()<a+.15*local_h or p[:,0].max()>b-.15*local_h)
                if version==4 or unsafe:
                    q=supported_extent(q)
                    if q is None:continue
                    p=np.asarray(q['polygon'])
            if version==2:
                for row,free in support:
                    narrowed,ev=narrow(q,row,data,items)
                    decisions.append(dict(request=ri,bbox=bbox(q),**ev))
                    if narrowed is not None and not overlaps_exclusion(narrowed['polygon'],rejected):proposals.append((narrowed,row['height']))
                continue
            why='candidate'
            if version>=6 and min(cv2.minAreaRect(p.astype(np.float32))[1])>3.5*local_h:why='localization holds more than one body band'
            elif overlaps_exclusion(p,rejected):why='excluded footprint'
            elif version<3 and any(inside[i] and z['owned'] for i,z in enumerate(data['bodies'])):why='contains existing body centre'
            elif version>=3 and any(point_ownership(centres_existing,[q])):why='contains existing line centre'
            elif version>=4 and competing_axis(q,items,local_h,margin=.5 if version>=6 else 0.,context=axes):why='existing row in shared x interval'
            elif p[:,0].min()<a+.15*local_h or p[:,0].max()>b-.15*local_h:why='crop edge'
            decisions.append(dict(request=ri,reason=why,bbox=bbox(q)))
            if why=='candidate':proposals.append((q,local_h))
    layers=None;motifs=[];added=[]
    if proposals:
        layers=ownership(gray,items,regions=[bbox(q) for q,_ in proposals],detail=True,tone_samples=tone_samples,glyph_samples=glyph_samples)
    for j,(q,h) in enumerate(proposals):
        if j in layers['suppress_indices']:
            decisions.append(dict(proposal=j,reason='independent reflected glyph evidence'));continue
        if version>=6 and j in layers['suspects']:
            decisions.append(dict(proposal=j,reason='weak layer has no recovery certificate'));continue
        # B's interface uses the page box proxy, not native component height.
        # A confirmed C nomination pays for the full spatial witness; its
        # ordinary-shape/unknown result still cannot certify text.
        if version>=11:m=candidate_motif(gray,q,sc['height'])
        else:m,_=motif(gray,q,sc['height'] if version>=10 else h,diagnostic=version>=10)
        motifs.append(dict(proposal=j,**m))
        if m['drop']:
            decisions.append(dict(proposal=j,reason='repeated ornament'));continue
        if (overlaps_exclusion(q['polygon'],added) if version<3 else
            any(point_ownership([((np.array(bbox(z))[:2]+np.array(bbox(z))[2:])/2).tolist() for z in added],[q]))):
            decisions.append(dict(proposal=j,reason='already recovered region'));continue
        if version<2:q=snap_components(gray,q,h,items+added)
        if overlaps_exclusion(q['polygon'],rejected):
            decisions.append(dict(proposal=j,reason='completion crosses exclusion'));continue
        column_parts=[q]
        if column_evidence is not None:
            from .geometry_columns import apply as apply_columns
            split=apply_columns(column_parts,column_evidence);column_parts=split['items']
            decisions.extend(dict(proposal=j,stage='shared column certificate',**x) for x in split['changes'])
        pieces=[];barriers=[]
        for part in column_parts:
            pp,bb=protect(gray,part,h);pieces.extend(pp);barriers.extend(bb)
        if not pieces and version>=5:
            clipped=supported_extent(q)
            if clipped is not None and clipped['polygon']!=q['polygon'] and not overlaps_exclusion(clipped['polygon'],rejected):
                pieces,extra=protect(gray,clipped,h)
                barriers+=extra
        decisions.extend(dict(proposal=j,stage='regional separator',**x) for x in barriers)
        if version>=8:
            for piece in pieces:
                if not piece_support(piece,q['type_witness_points'],added,h):
                    decisions.append(dict(proposal=j,reason='separator piece has no independent unowned body chain',bbox=bbox(piece)));continue
                if competing_axis(piece,items+added,h,margin=.5,context=axes+axis_context(added)):
                    decisions.append(dict(proposal=j,reason='separator piece competes with existing row',bbox=bbox(piece)));continue
                if version>=10:
                    b=bbox(piece)
                    unresolved=[r for r in rule_contacts(gray,piece['polygon'],h)
                                if b[0]+.5*h<(r['candidate']['bbox'][0]+r['candidate']['bbox'][2])/2<b[2]-.5*h]
                    if unresolved:
                        decisions.append(dict(proposal=j,reason='interior sustained rule remains unresolved',bbox=b,contacts=unresolved));continue
                added.append(piece)
        else:added.extend(pieces)
    completion=[]
    if version>=11 and complete_rows:
        for ri,req in enumerate(reqs):
            indices=[i for i,q in enumerate(added) if q['type_residual']==ri]
            if not indices:continue
            completed,record=complete_request(gray,[added[i] for i in indices],sc['height'],fields[ri],req,items,column_evidence=column_evidence,retain_support=retain_support)
            record['request']=ri;completion.append(record)
            changed=[k for k,(old,new) in enumerate(zip([added[i] for i in indices],completed)) if old['polygon']!=new['polygon']]
            if changed:
                fixed=list(added)
                for k in changed:fixed[indices[k]]=completed[k]
                # Geometry invalidates the earlier source and motif observations.
                fresh=ownership(gray,items,regions=[bbox(completed[k]) for k in changed],detail=True,tone_samples=tone_samples,glyph_samples=glyph_samples)
                fixed_axes=axes+axis_context(fixed)
                accepted_changes=[];failed_changes=set()
                for pos,k in enumerate(changed):
                    q=completed[k];h=next(c['height'] for c in calls if c['request']==ri)
                    # Exact decision view: retain every vertex, share only its
                    # immutable conversion and bounds within this geometry.
                    decision=dict(q,polygon=np.asarray(q['polygon'],float));bounds=bbox(decision)
                    why=None
                    if pos in fresh['suppress_indices'] or pos in fresh['suspects']:why='new source support unknown'
                    elif candidate_motif(gray,decision,sc['height'])['drop']:why='completed ornament'
                    elif overlaps_exclusion(decision['polygon'],rejected):why='completed exclusion'
                    elif competing_axis(decision,(),h,margin=.5,context=[v for ix,v in enumerate(fixed_axes) if ix!=len(items)+indices[k]]):why='completed neighbour conflict'
                    elif any(bounds[0]+.5*h<(r['candidate']['bbox'][0]+r['candidate']['bbox'][2])/2<bounds[2]-.5*h for r in rule_contacts(gray,decision['polygon'],h)):why='completed interior rule unresolved'
                    if why:
                        next(r for r in record['records'] if r['piece']==k)['status']='unknown: '+why
                        failed_changes.add(k)
                    else:accepted_changes.append(k)
                paired={r['piece']:r['row'] for r in record['records'] if 'row' in r}
                row_to_piece={v:k for k,v in paired.items()}
                # A refusal on either member refuses the existing connected seam
                # transaction. No new source/quality vote is introduced.
                while True:
                    linked=set(failed_changes)
                    for k in changed:
                        for seam in completed[k].get('shared_separators',[]):
                            ps={row_to_piece[r] for r in seam['rows'] if r in row_to_piece}
                            if ps & failed_changes:linked|=ps
                    if linked==failed_changes:break
                    failed_changes=linked
                for k in accepted_changes:
                    if k not in failed_changes:added[indices[k]]=completed[k]
                    else:next(r for r in record['records'] if r['piece']==k)['status']='unknown: paired neighbour refresh refused'
    end=perf_counter()
    return dict(**({'completion':completion} if complete_rows else {}),items=list(items)+added,added=added,scout=sc,requests=reqs,fields=fields,calls=calls,
                decisions=decisions,ownership=layers,motifs=motifs,tables=table,seconds=end-start,
                scout_s=scout_end-start,correction_s=end-scout_end,version=version)

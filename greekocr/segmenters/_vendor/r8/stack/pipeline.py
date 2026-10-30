"""Single image-file to final line entry point, warm reusable Paddle session."""
from pathlib import Path
from time import perf_counter
import cv2
from ..shared.detector import Detector, postprocess
from ..shared.geometry_memo import page_geometry
from ..layout_barriers.fast import scout, correct
from ..features_ink.pipeline import ink_run
from .geometry import run as geometry_run, cuts as geometry_cuts
from ..shared.type_extended import recover
from ..shared.geometry_envelopes import correct as smooth_envelopes
from ..shared.ink_faintness import analyze as relative_faintness
from ..shared.ink_footprints import Footprints
from ..shared.ink_photometry import sample_boxes
from ..shared.contracts import bbox
from ..shared.ink_frame_field import render as frame_render,exclude_whole as frame_exclude
from ..shared.geometry_rows import analyze as split_rows
from ..shared.geometry_edge_map import scout as edge_scout
from ..shared.geometry_field_detector import run as field_proposals
from ..shared.geometry_field_selection import apply as field_replace
from ..shared.stack_ownership import reconcile as reconcile_rows
from ..shared.geometry_bands import tessellate



class Stack:
    def __init__(self, *, image_threads=2, bend=False, final_export=False):
        self.bend=bend;self.final_export=final_export
        # Request only: macOS GCD does not honor a positive worker cap.
        # Receipts record getNumThreads(); ONNX has separate single-thread settings.
        cv2.setNumThreads(image_threads)
        self.detector=Detector()
        self.startup_s=self.detector.startup_s

    def __call__(self, path, *, parked=False):
        start=perf_counter();gray=cv2.imread(str(Path(path)),cv2.IMREAD_GRAYSCALE)
        if gray is None:raise ValueError(f'Cannot decode image: {path}')
        decode_s=perf_counter()-start;t=perf_counter()
        pm,meta=self.detector.infer(gray);original=postprocess(pm,(gray.shape[1],gray.shape[0]))
        detector_s=perf_counter()-t;t=perf_counter()
        evidence=compose(gray,pm,original,self.detector,use_bend=self.bend,use_final_export=self.final_export) if not parked else dict(items=original,parked=True,counts={},stages={})
        correction_s=perf_counter()-t
        return dict(evidence,original=original,image_size=[gray.shape[1],gray.shape[0]],timing=dict(
            decode_s=decode_s,detector_s=detector_s,correction_s=correction_s,
            paddle_file_s=decode_s+detector_s,total_s=perf_counter()-start,
            startup_s=self.startup_s,image_threads=cv2.getNumThreads(),**meta))


@page_geometry
def compose(gray,pm,original,detector,*,use_bend=False,use_final_export=False):
    start=perf_counter();stages={};field_cache={};field_labels={}
    witness,primitive=scout(gray,original)
    stages['rule_scout_s']=perf_counter()-start;t=perf_counter()
    q8=correct(gray,original,witness,primitive) if witness['candidates'] else dict(items=original,changes=[],rules=[],decisions=[],protected_rules=[])
    stages['q8_correction_s']=perf_counter()-t
    # The source ledger is separate from mutable positional indices.
    cut_sources={c['line'] for c in q8['changes']};index=0;current=[]
    for i,q in enumerate(original):
        if i in cut_sources:
            pieces=next(c['new'] for c in q8['changes'] if c['line']==i)
            for _ in pieces:
                current.append(dict(q8['items'][index],source_ids=[i]));index+=1
        else:
            current.append(dict(q8['items'][index],source_ids=[i]));index+=1
    t=perf_counter();tone_samples=sample_boxes(gray,[bbox(q) for q in current]);tone_s=perf_counter()-t
    glyph_samples=[]  # Native components/fixed tiles; later census/height decisions stay fresh.
    ink=ink_run(gray,current,height=witness['height'] if not q8['changes'] else None,tone_samples=tone_samples,glyph_output=glyph_samples)
    ink['scout_s']+=tone_s;ink['ink_s']+=tone_s
    ink['ownership']['scout_s']+=tone_s;ink['ownership']['seconds']+=tone_s
    removed=[dict(current[i],removal=ink['removal_reasons'][i]) for i in ink['removed']]
    stages['ink_s']=perf_counter()-t;stages['solid_s']=ink.get('solid',{}).get('seconds',0.);stages['seal_s']=ink['seal_s'];stages['discrete_scout_s']=ink['discrete_scout_s'];stages['discrete_refinement_s']=ink['discrete_refinement_s'];stages['ink_scout_s']=ink['scout_s'];stages['ink_refinement_s']=ink['refinement_s']
    t=perf_counter();edge=edge_scout(pm,original,gray.shape[::-1]);stages['edge_scout_s']=perf_counter()-t
    page_field=dict(scout=edge,proposal=None,replacement=None,early_replacement=None,early=False);columns=None;geometry_input=ink['items'];proposal=None;separated=None;early_polygons=None
    bend_evidence=None
    if edge['trigger']:
        # Cheap printed boundaries establish source ownership before the field.
        # All expensive per-line paths below then see field-owned rows and abstain.
        t=perf_counter();separated=geometry_cuts(gray,original,geometry_input,witness,primitive);columns=separated['columns'];geometry_input=separated['items'];stages['field_cuts_s']=perf_counter()-t
        if not use_bend:
            t=perf_counter();proposal=field_proposals(gray,original,detector,column_evidence=columns,excluded_regions=removed,field_cache=field_cache);stages['field_proposal_s']=perf_counter()-t
            page_field['proposal']=proposal;page_field['early']=True
            t=perf_counter();replacement=field_replace(gray,geometry_input,proposal,forbidden_regions=removed,column_evidence=columns,prepared=field_cache.get('prepared'),label_cache=field_labels);stages['field_early_replace_s']=perf_counter()-t
            geometry_input=replacement['items'];early_polygons=[q['polygon'] for q in geometry_input];page_field['early_replacement']={k:v for k,v in replacement.items() if k!='items'}
    if use_bend:
        import numpy as np
        from ..shared.geometry_bend import scout as bend_scout
        from ..shared.geometry_bend_edits import run as bend_edits
        t=perf_counter();fields=bend_scout(pm,np.array([bbox(q) for q in original]).reshape(-1,4),gray.shape[::-1],edge,(columns or {}).get('rules',[]),gray=gray);stages['bend_scout_s']=perf_counter()-t
        t=perf_counter();bend_evidence=bend_edits(gray,geometry_input,fields,excluded=removed,witness=witness,primitive=primitive,columns=columns)
        geometry_input=bend_evidence.pop('items');stages['bend_edits_s']=perf_counter()-t
    t=perf_counter();geo=geometry_run(gray,pm,original,geometry_input,witness,primitive,forbidden_regions=removed,field_cache=field_cache,columns=columns,separated=separated)
    stages['geometry_all_s']=perf_counter()-t
    stages.update({k:geo[k] for k in ('scout_s','geometry_s','curved_s','fragment_s','column_s')})
    t=perf_counter();typ=recover(gray,geo['items'],detector,excluded_regions=removed,column_evidence=geo['columns'],tone_samples=tone_samples,glyph_samples=glyph_samples,retain_support=use_final_export)
    stages['type_s']=perf_counter()-t;stages['type_scout_s']=typ['scout_s'];stages['type_correction_s']=typ['correction_s']
    t=perf_counter();shapes=smooth_envelopes(gray,pm,typ['items'],original,scout=geo['witness'],forbidden_regions=removed,map_bands=geo.get('map_bands'),column_evidence=geo.get('columns'),field_cache=field_cache)
    stages['shape_s']=perf_counter()-t
    # R6 A judges the actual final OCR segment, after all cuts/recoveries.
    # Its exclusions are exact final polygons, never stamp disks or rectangles.
    t=perf_counter();footprint_ledger=Footprints();judged_tokens=footprint_ledger.stamp_all(shapes['items']);stages['ink_identity_s']=perf_counter()-t
    t=perf_counter();faint=relative_faintness(gray,shapes['items'],ownership_evidence=ink['ownership'])
    faint_ids=set(faint['suppress_indices'])
    removed.extend(dict(q,removal='relative faintness') for i,q in enumerate(shapes['items']) if i in faint_ids)
    final=[q for i,q in enumerate(shapes['items']) if i not in faint_ids]
    stages['faint_s']=perf_counter()-t;stages['faint_scout_s']=faint['scout_s']
    # R6 B retains accepted row identities. Certified whole-component children
    # may extend their parent, but cannot restore removed/owned native support.
    # Every changed extent refreshes its source/motif/rule decisions below.
    if proposal is not None and proposal['items'] and [q['polygon'] for q in final]!=early_polygons:
        t=perf_counter();replacement=field_replace(gray,final,proposal,forbidden_regions=removed,column_evidence=geo['columns'],prepared=field_cache.get('prepared'),label_cache=field_labels);stages['field_replace_s']=perf_counter()-t
        final=replacement['items'];page_field['replacement']={k:v for k,v in replacement.items() if k!='items'}
    def refresh_children(index,parent,polygons,h,current_pool):
        from ..shared.ink_ownership import analyze as source_ownership
        from ..shared.type_residual_recovery import candidate_motif,rule_contacts
        candidates=[dict(parent,polygon=p,baseline=None) for p in polygons]
        for q in candidates:q.pop('centreline',None)
        pool=[]
        for q in current_pool:pool.extend(candidates if q is parent else [q])
        # Fresh census and B5 anchors/M35 glyph pool on changed footprints.
        fresh=source_ownership(gray,pool,regions=[bbox(q) for q in candidates],detail=True,
                               tone_samples=tone_samples,glyph_samples=glyph_samples)
        motifs=[candidate_motif(gray,q,h) for q in candidates]
        contacts=[rule_contacts(gray,q['polygon'],h) for q in candidates]
        reasons=[]
        for k,q in enumerate(candidates):
            bounds=bbox(q)
            if k in fresh['suppress_indices'] or k in fresh['suspects']:reasons.append('source support unknown')
            elif motifs[k]['drop']:reasons.append('ornament')
            elif any(bounds[0]+.5*h<(r['candidate']['bbox'][0]+r['candidate']['bbox'][2])/2<bounds[2]-.5*h for r in contacts[k]):reasons.append('interior rule unresolved')
            else:reasons.append(None)
        return dict(accepted=not any(reasons),reasons=reasons,ownership=fresh,motifs=motifs,rules=contacts)
    t=perf_counter();rows=split_rows(gray,final,forbidden_regions=removed,refresh=refresh_children,retain_support=use_final_export);final=rows['items']
    stages['rows_s']=perf_counter()-t;stages['rows_scout_s']=rows['scout_s'];stages['rows_native_s']=rows['native_s']
    t=perf_counter();native_context={};ownership=reconcile_rows(gray,final,prepared_output=native_context if use_final_export else None);final=ownership['items'];stages['row_ownership_s']=perf_counter()-t
    # Recheck changed field/partition polygons on their actual final footprints.
    # Unchanged rows retain the earlier A decision; calibration still uses all.
    t=perf_counter();selected=footprint_ledger.changed_indices(final,judged_tokens);stages['ink_identity_s']+=perf_counter()-t
    t=perf_counter();final_faint=relative_faintness(gray,final,selected_indices=selected) if selected else None
    if final_faint:
        later=set(final_faint['suppress_indices'])
        removed.extend(dict(q,removal='relative faintness') for i,q in enumerate(final) if i in later)
        final=[q for i,q in enumerate(final) if i not in later]
    stages['final_faint_s']=perf_counter()-t
    t=perf_counter();frame=frame_render(gray,[q['polygon'] for q in original],ink['ownership']['height']);framed=frame_exclude(gray,final,frame,ink['ownership']['height'])
    final=framed['items'];removed.extend(framed['exclusions']);stages['frame_s']=perf_counter()-t
    def refresh_export(pool,changed):
        from ..shared.geometry_final_support import identity
        from ..shared.ink_ownership import analyze as source_ownership
        from ..shared.type_residual_recovery import candidate_motif,rule_contacts
        # No polygon-based calibration cache is frozen across changed crops.
        # The existing source decision receives the current pooled geometry.
        candidates=[pool[i] for i in changed]
        fresh=source_ownership(gray,pool,regions=[bbox(q) for q in candidates],detail=True)
        h=native_context.get('height',ink['ownership']['height'])
        # Geometry alone is not new ornament/frame evidence. New native
        # content invokes those dependencies; redistribution refreshes source.
        novel=[k for k,q in enumerate(candidates) if q.get('_content_change',{}).get('new_observed_components')]
        motifs={k:candidate_motif(gray,candidates[k],h) for k in novel}
        contacts={k:rule_contacts(gray,candidates[k]['polygon'],h) for k in novel}
        source_reasons=[('back source' if k in fresh['suppress_indices'] else ('new source unresolved' if k in novel and k in fresh['suspects'] else None)) for k in range(len(candidates))]
        for k in novel:
            if motifs[k]['drop']:source_reasons[k]='ornament'
            elif contacts[k]:source_reasons[k]='new rule contact unresolved'
        # Calibration receives content geometry, not the new export envelope.
        refreshed_faint=relative_faintness(gray,pool,selected_indices=set(changed))
        refreshed_frame=frame_exclude(gray,[candidates[k] for k in novel],frame,ink['ownership']['height']) if novel else dict(removed=[])
        refused={changed[k] for k,v in enumerate(source_reasons) if v}|set(refreshed_faint['suppress_indices'])|{changed[novel[k]] for k in refreshed_frame['removed']}
        return dict(accepted=not refused,refused_indices=sorted(refused),
                    input_identities={str(i):identity(pool[i]) for i in changed},source_reasons=source_reasons,
                    ownership=fresh,motifs=motifs,rules=contacts,faint=refreshed_faint,frame_removed=refreshed_frame['removed'],
                    callbacks=dict(source=1,faintness=1,motif=len(novel),rules=len(novel),frame=int(bool(novel))),input_kind='owned-component content bounding geometry; no final background envelope',numeric_input_reuse=False)
    t=perf_counter();bands=(tessellate(gray,final,prepared=native_context,columns=geo['columns'],excluded=removed,refresh=refresh_export)
                           if use_final_export else dict(items=final,migrated=[],disabled=True,seconds=0.))
    final=bands['items'];stages['final_bands_s']=perf_counter()-t
    if bands['migrated']:selected.update(footprint_ledger.changed_indices(final,judged_tokens))
    identity_receipt=dict(judged=sorted(judged_tokens),final=[q.pop('ink_token',None) for q in final],changed=sorted(selected))
    for q in removed:q.pop('ink_token',None)
    # Page-local selected-pixel receipts are inputs, never serialized arrays.
    for q in final+removed+typ['added']+typ.get('new_added',[])+(typ.get('residual') or {}).get('added',[]):q.pop('_selected_pixel_support',None)
    counts=dict(q8=len(q8['changes']),back=len(ink['ownership']['suppress_indices']),
                ornaments=sum(q['removal']=='ornament' for q in removed),blobs=sum(q['removal']=='solid ink mass' for q in removed),frames=sum(q['removal']=='recurrent frame' for q in removed),seals=sum(q['removal']=='seal rim' for q in removed),geometry=len(geo['changes']),
                curved=len((geo['curved'] or {}).get('applied',[])),joins=len(geo['fragments']['joins']),
                joined_reduction=geo['joined_reduction'],added=len(typ['added']),
                columns=len(geo['columns']['changes']),smooth=len(shapes['changes']),faint=len(faint_ids)+len((final_faint or {}).get('suppress_indices',[])),rows=len(rows['changes']),page_field=sum(q.get('page_field',False) for q in final),row_duplicates=len(ownership['changes']))
    return dict(items=final,final_bands={k:v for k,v in bands.items() if k!='items'},bend=bend_evidence,ink_footprints=identity_receipt,frame=dict(units=frame.units.tolist(),sides=frame.sides.tolist(),removed=framed['removed']),final_faint=final_faint,page_field=page_field,row_ownership={k:v for k,v in ownership.items() if k!='items'},rows={k:v for k,v in rows.items() if k!='items'},faint=faint,removed=removed,added=typ['added'],counts=counts,stages=stages,
                shapes={k:v for k,v in shapes.items() if k!='items'},
                q8={k:v for k,v in q8.items() if k!='items'},geometry={k:v for k,v in geo.items() if k!='items'},
                ink={k:v for k,v in ink.items() if k!='items'},type={k:v for k,v in typ.items() if k!='items'},seconds=perf_counter()-start)

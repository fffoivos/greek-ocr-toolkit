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
from ..shared.ink_frame_field import render as frame_render,exclude_whole as frame_exclude
from ..shared.geometry_rows import analyze as split_rows
from ..shared.geometry_edge_map import scout as edge_scout
from ..shared.geometry_field_detector import run as field_proposals
from ..shared.geometry_field_selection import apply as field_replace
from ..shared.stack_ownership import reconcile as reconcile_rows



class Stack:
    def __init__(self, *, image_threads=2, bend=False):
        self.bend=bend
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
        evidence=compose(gray,pm,original,self.detector,use_bend=self.bend) if not parked else dict(items=original,parked=True,counts={},stages={})
        correction_s=perf_counter()-t
        return dict(evidence,original=original,image_size=[gray.shape[1],gray.shape[0]],timing=dict(
            decode_s=decode_s,detector_s=detector_s,correction_s=correction_s,
            paddle_file_s=decode_s+detector_s,total_s=perf_counter()-start,
            startup_s=self.startup_s,image_threads=cv2.getNumThreads(),**meta))


@page_geometry
def compose(gray,pm,original,detector,*,use_bend=False):
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
    t=perf_counter();ink=ink_run(gray,current,height=witness['height'] if not q8['changes'] else None)
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
        from ..shared.contracts import bbox
        from ..shared.geometry_bend import scout as bend_scout
        from ..shared.geometry_bend_edits import run as bend_edits
        t=perf_counter();fields=bend_scout(pm,np.array([bbox(q) for q in original]).reshape(-1,4),gray.shape[::-1],edge,(columns or {}).get('rules',[]),gray=gray);stages['bend_scout_s']=perf_counter()-t
        t=perf_counter();bend_evidence=bend_edits(gray,geometry_input,fields,excluded=removed,witness=witness,primitive=primitive,columns=columns)
        geometry_input=bend_evidence.pop('items');stages['bend_edits_s']=perf_counter()-t
    t=perf_counter();geo=geometry_run(gray,pm,original,geometry_input,witness,primitive,forbidden_regions=removed,field_cache=field_cache,columns=columns,separated=separated)
    stages['geometry_all_s']=perf_counter()-t
    stages.update({k:geo[k] for k in ('scout_s','geometry_s','curved_s','fragment_s','column_s')})
    t=perf_counter();typ=recover(gray,geo['items'],detector,excluded_regions=removed,column_evidence=geo['columns'])
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
    # R6 B partitions surviving OCR segments. It neither expands a segment nor
    # restores any of A's exact removed polygons. Task C can replace these
    # provisional per-segment partitions using the retained parent ledger.
    if proposal is not None and proposal['items'] and [q['polygon'] for q in final]!=early_polygons:
        t=perf_counter();replacement=field_replace(gray,final,proposal,forbidden_regions=removed,column_evidence=geo['columns'],prepared=field_cache.get('prepared'),label_cache=field_labels);stages['field_replace_s']=perf_counter()-t
        final=replacement['items'];page_field['replacement']={k:v for k,v in replacement.items() if k!='items'}
    t=perf_counter();rows=split_rows(gray,final);final=rows['items']
    stages['rows_s']=perf_counter()-t;stages['rows_scout_s']=rows['scout_s'];stages['rows_native_s']=rows['native_s']
    t=perf_counter();ownership=reconcile_rows(gray,final);final=ownership['items'];stages['row_ownership_s']=perf_counter()-t
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
    identity_receipt=dict(judged=sorted(judged_tokens),final=[q.pop('ink_token',None) for q in final],changed=sorted(selected))
    for q in removed:q.pop('ink_token',None)
    counts=dict(q8=len(q8['changes']),back=len(ink['ownership']['suppress_indices']),
                ornaments=sum(q['removal']=='ornament' for q in removed),blobs=sum(q['removal']=='solid ink mass' for q in removed),frames=sum(q['removal']=='recurrent frame' for q in removed),seals=sum(q['removal']=='seal rim' for q in removed),geometry=len(geo['changes']),
                curved=len((geo['curved'] or {}).get('applied',[])),joins=len(geo['fragments']['joins']),
                joined_reduction=geo['joined_reduction'],added=len(typ['added']),
                columns=len(geo['columns']['changes']),smooth=len(shapes['changes']),faint=len(faint_ids)+len((final_faint or {}).get('suppress_indices',[])),rows=len(rows['changes']),page_field=sum(q.get('page_field',False) for q in final),row_duplicates=len(ownership['changes']))
    return dict(items=final,bend=bend_evidence,ink_footprints=identity_receipt,frame=dict(units=frame.units.tolist(),sides=frame.sides.tolist(),removed=framed['removed']),final_faint=final_faint,page_field=page_field,row_ownership={k:v for k,v in ownership.items() if k!='items'},rows={k:v for k,v in rows.items() if k!='items'},faint=faint,removed=removed,added=typ['added'],counts=counts,stages=stages,
                shapes={k:v for k,v in shapes.items() if k!='items'},
                q8={k:v for k,v in q8.items() if k!='items'},geometry={k:v for k,v in geo.items() if k!='items'},
                ink={k:v for k,v in ink.items() if k!='items'},type={k:v for k,v in typ.items() if k!='items'},seconds=perf_counter()-start)

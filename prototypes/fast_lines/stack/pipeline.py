"""Single image-file to final line entry point, warm reusable Paddle session."""
from pathlib import Path
from inspect import signature
from time import perf_counter
import cv2
from ..shared.detector import Detector, postprocess
from ..layout_barriers.fast import scout, correct
from ..features_ink.pipeline import ink_run
from .geometry import run as geometry_run
from ..shared.type_extended import recover
from ..shared.geometry_envelopes import correct as smooth_envelopes

# R5 C accepts this certificate. Keep the geometry branch executable with the
# merged R4 C module until the coordinator merges the independent R5 C changes.
_TYPE_ACCEPTS_COLUMNS='column_evidence' in signature(recover).parameters


class Stack:
    def __init__(self):
        cv2.setNumThreads(1)
        self.detector=Detector()
        self.startup_s=self.detector.startup_s

    def __call__(self, path, *, parked=False):
        start=perf_counter();gray=cv2.imread(str(Path(path)),cv2.IMREAD_GRAYSCALE)
        if gray is None:raise ValueError(f'Cannot decode image: {path}')
        decode_s=perf_counter()-start;t=perf_counter()
        pm,meta=self.detector.infer(gray);original=postprocess(pm,(gray.shape[1],gray.shape[0]))
        detector_s=perf_counter()-t;t=perf_counter()
        evidence=compose(gray,pm,original,self.detector) if not parked else dict(items=original,parked=True,counts={},stages={})
        correction_s=perf_counter()-t
        return dict(evidence,original=original,image_size=[gray.shape[1],gray.shape[0]],timing=dict(
            decode_s=decode_s,detector_s=detector_s,correction_s=correction_s,
            paddle_file_s=decode_s+detector_s,total_s=perf_counter()-start,
            startup_s=self.startup_s,**meta))


def compose(gray,pm,original,detector):
    start=perf_counter();stages={}
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
    removed=[dict(current[i],removal='back print' if i in ink['ownership']['suppress_indices'] else 'ornament') for i in ink['removed']]
    stages['ink_s']=perf_counter()-t;stages['ink_scout_s']=ink['scout_s'];stages['ink_refinement_s']=ink['refinement_s']
    t=perf_counter();geo=geometry_run(gray,pm,original,ink['items'],witness,primitive,forbidden_regions=removed)
    stages['geometry_all_s']=perf_counter()-t
    stages.update({k:geo[k] for k in ('scout_s','geometry_s','curved_s','fragment_s','column_s')})
    type_kwargs={'column_evidence':geo['columns']} if _TYPE_ACCEPTS_COLUMNS else {}
    t=perf_counter();typ=recover(gray,geo['items'],detector,excluded_regions=removed,**type_kwargs)
    stages['type_s']=perf_counter()-t;stages['type_scout_s']=typ['scout_s'];stages['type_correction_s']=typ['correction_s']
    t=perf_counter();shapes=smooth_envelopes(gray,pm,typ['items'],original,scout=geo['witness'],forbidden_regions=removed,map_bands=geo.get('map_bands'),column_evidence=geo.get('columns'))
    stages['shape_s']=perf_counter()-t
    counts=dict(q8=len(q8['changes']),back=len(ink['ownership']['suppress_indices']),
                ornaments=len(removed)-len(ink['ownership']['suppress_indices']),geometry=len(geo['changes']),
                curved=len((geo['curved'] or {}).get('applied',[])),joins=len(geo['fragments']['joins']),
                joined_reduction=geo['joined_reduction'],added=len(typ['added']),
                columns=len(geo['columns']['changes']),smooth=len(shapes['changes']))
    return dict(items=shapes['items'],removed=removed,added=typ['added'],counts=counts,stages=stages,
                shapes={k:v for k,v in shapes.items() if k!='items'},
                q8={k:v for k,v in q8.items() if k!='items'},geometry={k:v for k,v in geo.items() if k!='items'},
                ink={k:v for k,v in ink.items() if k!='items'},type={k:v for k,v in typ.items() if k!='items'},seconds=perf_counter()-start)

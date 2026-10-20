"""Offline compose-stage traces; no runtime imports of this instrument."""
import argparse,hashlib,json
from pathlib import Path
from functools import wraps
import numpy as np
from ..shared import detector
from ..stack import pipeline as sp


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clean(v):
    if isinstance(v,np.ndarray):return v.tolist()
    if isinstance(v,np.generic):return v.item()
    if isinstance(v,dict):return {str(k):clean(x) for k,x in v.items() if not str(k).startswith('_')}
    if isinstance(v,(list,tuple)):return [clean(x) for x in v]
    return v

def dump(p,v):Path(p).write_text(json.dumps(clean(v),ensure_ascii=False)+'\n')

def run(inputs,out,pages=()):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    inputs=Path(inputs);rows=json.loads(inputs.read_text())['pages'];records=[];events=[]
    selected=[r for r in rows if not pages or r['page'] in pages]
    originals={}
    indices={'ink_run':1,'geometry_cuts':2,'field_proposals':1,'field_replace':1,
             'geometry_run':3,'recover':1,'smooth_envelopes':2,'relative_faintness':1,
             'split_rows':1,'reconcile_rows':1,'frame_exclude':1}
    def wrap(name,fn,index):
        @wraps(fn)
        def call(*a,**kw):
            before=clean(a[index]);result=fn(*a,**kw)
            events.append(dict(stage=name,input=before,result=clean(result)))
            return result
        return call
    for name,index in indices.items():
        originals[name]=getattr(sp,name);setattr(sp,name,wrap(name,originals[name],index))
    old_model=detector.MODEL
    detector.MODEL=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/onnx/PP-OCRv6_small_det.onnx')
    try:
        stack=sp.Stack()
        for row in selected:
            assert digest(row['path'])==row['sha256'];events.clear()
            result=stack(row['path'],parked=row.get('parked',False))
            dump(out/(row['page']+'.json'),result)
            dump(out/(row['page']+'.trace.json'),events)
            records.append(dict(page=row['page'],input_sha256=row['sha256'],items=len(result['items']),counts=result['counts'],timing=result['timing']))
            print(row['page'],len(result['items']),result['counts'],flush=True)
        root=Path(__file__).resolve().parents[3]
        sources={str(p.relative_to(root)):digest(p) for p in sorted((root/'prototypes/fast_lines').rglob('*.py')) if '/evidence/' not in str(p) and not p.name.startswith('test_')}
        dump(out/'receipt.json',dict(inputs_sha256=digest(inputs),sources=sources,model_sha256=digest(detector.MODEL),pages=records,scope='Offline traced actual compose calls. Timing includes serialization; not performance. Native gray and original Paddle are unmodified.'))
    finally:
        detector.MODEL=old_model
        for name,fn in originals.items():setattr(sp,name,fn)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('out');p.add_argument('pages',nargs='*');a=p.parse_args();run(a.inputs,a.out,a.pages)

"""Source-bound CURL development trace; sequential existing Stack callers only."""
import argparse, hashlib, json, os
from pathlib import Path

os.environ.update({k: '1' for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS')})
import cv2
import numpy as np
from ..shared import detector as dm
from ..stack import pipeline as pipe
from ..shared.review import overlay, save_image
from ..shared.geometry_bands import crop_mask
from ..shared.geometry import roi
from ..shared.contracts import bbox

ROOT = Path(__file__).resolve().parents[3]
FL = Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines')
OUT = ROOT / '.astra/fast_lines/out/round8/R8-CURL-03-i1'
PRIOR = ROOT / '.astra/fast_lines/out/round8/R8-GEOM-04-i3'
SLOW = Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-model/.astra/fast_lines/out/round8/R8-01/slow')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def clean(x):
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, np.generic): return x.item()
    if isinstance(x, dict): return {str(k): clean(v) for k,v in x.items() if k not in ('_source','_labels','_selected_pixel_support')}
    if isinstance(x, (tuple,list,set)): return [clean(v) for v in x]
    return x

def dump(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(clean(x),ensure_ascii=False,indent=1)+'\n')

def inputs():
    return json.loads((ROOT/'.astra/fast_lines/out/round8/R8-01b/inputs-208.json').read_text())['pages']

def freeze():
    curl=json.loads((FL/'cases/cases.json').read_text())['d_curl']
    labels={}
    for category,ids in curl.items():
        for p in ids: labels.setdefault(p,[]).append(category)
    old=json.loads((PRIOR/'GEOM04_I2_COHORT.json').read_text())
    for row in old['pages']:
        p=row if isinstance(row,str) else row['page']
        labels.setdefault(p,[]).append('geom04_exact12')
    for p in ('s2-831443dc5e6f1ccfbaf5-p00020','s2-831443dc5e6f1ccfbaf5-p00039'):
        labels.setdefault(p,[]).append('table_leader')
    pages=[]
    for row in inputs():
        if row['page'] not in labels: continue
        p=row['page']; assert sha(row['path'])==row['sha256']
        export=PRIOR/'default208'/f'{p}.json'; evidence=PRIOR/'default208'/f'{p}.evidence.json'
        pages.append(dict(row,categories=labels[p],exposure='development-retest',caller='Stack(final_export=False)',export=str(export),export_sha256=sha(export),evidence=str(evidence),evidence_sha256=sha(evidence),slow_files={str(q.relative_to(SLOW)):sha(q) for q in (SLOW/p).rglob('*') if q.is_file()}))
    assert {q['page'] for q in pages}==set(labels),set(labels)-{q['page'] for q in pages}
    source={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'prototypes/fast_lines').rglob('*.py')}
    dump(OUT/'CURL03_COHORT.json',dict(head='7be0d7012d9d8cf1245aef914b4187653d7b686d',pages=pages,curl=curl,source=source,previous_manifest_sha256=sha(PRIOR/'GEOM04_I2_COHORT.json'),cases_sha256=sha(FL/'cases/cases.json'),check_sha256=sha(FL/'review_r8/R8-GEOM-04-i3_check.md')))
    print('frozen',len(pages),flush=True)

def run(mode, ids, withdrawn=False):
    global dm,pipe
    temporary=None
    if withdrawn:
        import importlib,tempfile
        from .r8_curl_experiment import consumers
        temporary=tempfile.TemporaryDirectory()
        envelopes,_=consumers(Path(temporary.name))
        name=envelopes.__name__.rsplit('.shared',1)[0]
        dm=importlib.import_module(name+'.shared.detector')
        pipe=importlib.import_module(name+'.stack.pipeline')
    dm.MODEL=FL/'onnx/PP-OCRv6_small_det.onnx'
    stack=pipe.Stack(image_threads=0); assert cv2.getNumThreads()==1
    directory=OUT/mode
    if directory.exists() and any(directory.iterdir()):
        raise FileExistsError('Preserve the frozen evidence; choose a fresh --output directory')
    directory.mkdir(parents=True,exist_ok=True)
    stages={};originals={}
    if mode.endswith('trace'):
        for name in ('edge_scout','geometry_cuts','field_proposals','field_replace','geometry_run','recover','smooth_envelopes','relative_faintness','split_rows','reconcile_rows','frame_exclude'):
            fn=getattr(pipe,name);originals[name]=fn
            def wrapped(*args,_fn=fn,_name=name,**kw):
                if _name=='smooth_envelopes':kw['detail']=True
                r=_fn(*args,**kw);stages.setdefault(_name,[]).append(clean(r));return r
            setattr(pipe,name,wrapped)
    from time import perf_counter
    records=[]
    for row in inputs():
        if ids and row['page'] not in ids:continue
        assert not (FL.parent/'METER_STOP').exists();assert sha(row['path'])==row['sha256']
        stages.clear();gray=cv2.imread(row['path'],0);t=perf_counter()
        pm,meta=stack.detector.infer(gray);detector_s=perf_counter()-t;original=dm.postprocess(pm,gray.shape[::-1]);t=perf_counter()
        r=pipe.compose(gray,pm,original,stack.detector) if not row.get('parked') else dict(items=original,parked=True,stages={})
        elapsed=perf_counter()-t
        dump(directory/f'{row["page"]}.json',dict(items=r['items'],page=row['page'],image_size=row['image_size']))
        dump(directory/f'{row["page"]}.evidence.json',{k:v for k,v in r.items() if k!='items'})
        if mode.endswith('trace'):
            dump(directory/f'{row["page"]}.callers.json',stages)
            np.savez_compressed(directory/f'{row["page"]}.initial.npz',pm=pm)
            dump(directory/f'{row["page"]}.initial.json',dict(items=original,meta=meta,native_origin=[0,0],native_scale=[1,1],map_scale=[pm.shape[1]/gray.shape[1],pm.shape[0]/gray.shape[0]],pixel_centres='OpenCV integer centres; legacy DB coordinate mapping'))
            cv2.imwrite(str(directory/f'{row["page"]}.overlay.png'),overlay(gray,r['items'],width=1600))
            strips=directory/row['page'];strips.mkdir(exist_ok=True)
            for i,q in enumerate(r['items']):
                x,y,z,w=roi(bbox(q),gray.shape);raw=gray[y:w,x:z];mask=crop_mask(raw.shape,q,(x,y))
                cv2.imwrite(str(strips/f'{i:03d}.png'),np.where(mask,raw,255))
        records.append(dict(page=row['page'],correction_s=elapsed,detector_s=detector_s,total_s=elapsed+detector_s,stages=r['stages']))
        dump(directory/'RECEIPT.json',dict(records=records,source={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'prototypes/fast_lines').rglob('*.py')},opencv=cv2.getNumThreads(),model_sha256=sha(dm.MODEL)))
        print(mode,len(records),row['page'],len(r['items']),round(elapsed,3),flush=True)
    for name,fn in originals.items():setattr(pipe,name,fn)
    if temporary is not None:temporary.cleanup()

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('freeze','trace'));ap.add_argument('pages',nargs='*')
    ap.add_argument('--output',type=Path);ap.add_argument('--withdrawn',action='store_true',help='explicit offline replay of the archived rejected diff')
    a=ap.parse_args()
    if a.output is not None:OUT=a.output
    if a.mode=='freeze':
        if (OUT/'CURL03_COHORT.json').exists():raise FileExistsError('Choose a fresh --output directory')
        freeze()
    else:run(a.mode,a.pages,a.withdrawn)

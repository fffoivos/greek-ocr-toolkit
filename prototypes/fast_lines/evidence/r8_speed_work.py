"""Offline per-invocation work census; never imported by Stack or timed runs."""
import hashlib,json,sys
from collections import Counter
from pathlib import Path
import numpy as np


def run(source,out,pages):
    source=Path(source).resolve();out=Path(out);out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(source))
    from prototypes.fast_lines.shared import detector,ink_photometry
    from prototypes.fast_lines.stack import Stack
    from prototypes.fast_lines.shared.review import detector_record
    import cv2
    root=Path.cwd();manifest=root/'.astra/fast_lines/out/round8/R8-01b/inputs-208.json'
    inputs=json.loads(manifest.read_text())['pages']
    if pages==['--development208']:
        assert len(inputs)==208
        pages=[r['page'] for r in inputs]
    missing=set(pages)-{r['page'] for r in inputs}
    if missing:raise ValueError(f'Not in pinned development manifest: {sorted(missing)}')
    detector.MODEL=root.parent/'greek-ocr-toolkit-astra-lines4/.astra/fast_lines/onnx/PP-OCRv6_small_det.onnx'
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
    counts=Counter();events=[];inferences=[];templates={};actual=detector.Detector.infer
    def infer(self,gray,long_side=960):
        key=dict(shape=list(gray.shape),dtype=str(gray.dtype),pixels_sha256=hashlib.sha256(gray.tobytes()).hexdigest(),long_side=long_side)
        caller=sys._getframe(1)
        result=actual(self,gray,long_side)
        inferences.append(dict(input=key,caller=Path(caller.f_code.co_filename).name+':'+caller.f_code.co_name,
            tensor=result[1]['tensor'],tensor_values=int(np.prod(result[1]['tensor'])),map_sha256=hashlib.sha256(result[0].tobytes()).hexdigest()))
        return result
    detector.Detector.infer=infer
    originals={}
    for name in ('resize','GaussianBlur','boxFilter','connectedComponentsWithStats','morphologyEx','remap'):
        fn=getattr(cv2,name);originals[name]=fn
        def kernel(*a,_name=name,_fn=fn,**kw):
            caller=sys._getframe(1);stage=Path(caller.f_code.co_filename).name+':'+caller.f_code.co_name
            counts[_name+'.calls']+=1;counts[_name+'.input_pixels']+=a[0].size
            if _name in ('resize','GaussianBlur') and caller.f_code.co_name in ('glyphs','normalized_glyph'):
                counts['glyph_'+_name+'.calls']+=1;counts['glyph_'+_name+'.input_pixels']+=a[0].size
            return _fn(*a,**kw)
        setattr(cv2,name,kernel)
    def profile(frame,event,arg):
        if event!='return':return
        filename=Path(frame.f_code.co_filename).name;name=frame.f_code.co_name;v=frame.f_locals
        if filename=='geometry_page_field.py' and name=='shifts_many':
            before=v['before'];refine=frame.f_back.f_code.co_name=='render'
            supplied=refine and 'energy' in frame.f_code.co_varnames
            counts['field.correlation_calls']+=1
            counts['field.template_energy_elements']+=0 if supplied else before.size
            if refine:
                arr=before.base if before.base is not None else before
                if id(arr) not in templates:
                    templates[id(arr)]=arr
                    counts['field.template_energy_elements']+=before.shape[-2]*before.shape[-1]
            counts['field.lag_observations']+=int(np.prod(v['after'].shape))
        elif filename=='geometry_field_detector.py' and name=='native_bands' and 'owner' in v:
            n=len(v['rows']);k=len(v['owner'])
            counts['field.owner_group_visits']+=k if 'grouped' in v else n*k
            counts['field.distance_elements']+=v['dist'].size
            counts['field.full_distance_sorts']+=int('grouped' not in v and n>1)
            counts['field.two_distance_partitions']+=int('grouped' in v and n>1)
            events.append(dict(kind='native_bands',crop_shape=list(v['crop'].shape),rows=n,owned_components=k))
        elif filename=='geometry_rows.py' and name=='valley_path' and frame.f_back.f_code.co_name=='separate_bands':
            counts['field.gap_cost_elements']+=v['cost'].size
            counts['field.gap_solver_elements']+=v['a'].size
            counts['field.gap_calls']+=1
            events.append(dict(kind='gap',cost_shape=list(v['cost'].shape),solver_shape=list(v['a'].shape)))
        elif filename=='ink_photometry.py' and name=='glyph_atlas':
            counts['ink.atlas_builds']+=1;counts['ink.atlas_array_bytes']+=v['vectors'].nbytes+v['aspects'].nbytes
        elif filename=='ink_photometry.py' and name=='match_glyphs' and 'a' in v:
            counts['ink.match_requests']+=1
        elif filename=='ink_photometry.py' and name=='glyphs' and v.get('labels') is not None:
            counts['ink.glyph_requests']+=1
            x0,y0,x1,y1=[v[q] for q in ('x0','y0','x1','y1')];height=v['height'];stats=v['stats']
            x,y,w,h,area=stats.T
            selected=(.35*height<h)&(h<1.8*height)&(.12*height<w)&(w<1.6*height)&(area>=.055*height*height)&(x!=0)&(y!=0)&(x+w<x1-x0)&(y+h<y1-y0)
            counts['ink.selected_components_before_limit']+=int(selected.sum())
            if 'normalized' in v:
                counts['ink.owned_tile_vector_copy_bytes']+=int(selected.sum())*22*22*4*2
                counts['ink.max_single_roi_retained_tile_bytes']=max(counts['ink.max_single_roi_retained_tile_bytes'],len(v['normalized'])*22*22*4*2)
    records=[]
    try:
        stack=Stack()
        for row in inputs:
            if row['page'] not in pages:continue
            assert sha(row['path'])==row['sha256'];counts.clear();events.clear();inferences.clear();templates.clear()
            sys.setprofile(profile)
            try:result=stack(row['path'],parked=row.get('parked',False))
            finally:sys.setprofile(None)
            old=json.loads((root/'.astra/fast_lines/out/round8/R8-03-i1/runtime'/f"{row['page']}.json").read_text())
            assert detector_record(row,result['items'],0)['items']==old['items']
            seen={};duplicates=[]
            for i,q in enumerate(inferences):
                key=json.dumps(q['input'],sort_keys=True)
                if key in seen:duplicates.append([seen[key],i])
                else:seen[key]=i
            rec=dict(page=row['page'],input_sha256=row['sha256'],counts=dict(counts),events=events.copy(),
                inferences=inferences.copy(),duplicate_inference_requests=duplicates,export_exact=True,
                warning='Instrumented work only, clocks excluded; scan formulas tied to this source and live frame inputs.')
            dump(out/f"{row['page']}.json",rec);records.append(rec);print(row['page'],'work counted',flush=True)
    finally:
        sys.setprofile(None);detector.Detector.infer=actual
        for name,fn in originals.items():setattr(cv2,name,fn)
    sources={str(p.relative_to(source)):sha(p) for p in sorted((source/'prototypes/fast_lines').rglob('*.py')) if '/evidence/' not in str(p) and not p.name.startswith('test_')}
    dump(out/'receipt.json',dict(source=str(source),sources=sources,input_sha256=sha(manifest),model_sha256=sha(detector.MODEL),
        opencv_threads=cv2.getNumThreads(),pages=[r['page'] for r in records],scope='One invocation at a time, no cross-page cache or replay'))


if __name__=='__main__':run(sys.argv[1],sys.argv[2],sys.argv[3:])

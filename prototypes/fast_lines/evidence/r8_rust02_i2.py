"""Fixed-population current-route profile; no candidate or physical mutation.

Run sequentially as a module. cProfile self-Python is an UPPER bound on
interpreted work: NumPy ufuncs without c_call events stay unresolved in it.
Separate top-level stage profiles never overlap. Raw pstats preserve call edges.
"""
import os
os.environ.update({k:'1' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')})
os.environ['FAST_LINES_FIELD_BACKEND']='python'
import argparse, copy, cProfile, hashlib, json, pstats, time
from pathlib import Path
import cv2
import numpy as np
from .r8_curl_trace import ROOT, FL, dump, sha, inputs, clean
from .r8_rust02 import sanitize
O=ROOT/'.astra/fast_lines/out/round8/R8-RUST-02-i2'
OLD=O.parent/'R8-RUST-02-i1'
STAGES=('scout','correct','ink_run','edge_scout','geometry_cuts','field_proposals','field_replace','geometry_run','recover','smooth_envelopes','relative_faintness','split_rows','reconcile_rows','frame_render','frame_exclude','sample_boxes')

def freeze():
    path=OLD/'TIMING_PER_PAGE.json'
    assert sha(path)=='e1cca6567df9f8cd9635b26d2f051212802c8ab060bafc0ba2f93fe3306b92c6'
    selected=sorted((r for r in json.loads(path.read_text()) if not r['appendix'] and r['arm_medians_s']['H']['correction_s']>1),key=lambda r:r['page'])
    assert len(selected)==len({r['page'] for r in selected})==27
    byid={r['page']:r for r in inputs()}
    source={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'prototypes/fast_lines').rglob('*.py') if 'test' not in p.name and '/evidence/' not in str(p)}
    data=dict(head='f852ab4cb330fcedce06cb7e4af0a7aa696780c7',runtime='55607147cee021c6c1027ec3b2b7552abd0ce321',timing_sha256=sha(path),input_manifest_sha256=sha(ROOT/'.astra/fast_lines/out/round8/R8-01b/inputs-208.json'),source=source,pages=[dict(byid[r['page']],original_timing=r) for r in selected])
    if (O/'SLOW27.json').exists():assert json.loads((O/'SLOW27.json').read_text())==data
    else:dump(O/'SLOW27.json',data)
    dump(O/'PROFILE_PLAN.json',dict(population='frozen27; no private/owner inputs',backend='python',final_export=False,bend=False,warmups=1,uninstrumented_passes=2,profile_passes=2,order='one full warmup page; all27 uninstrumented then all27 stage-cProfile, repeated twice',threads=dict(opencv_request=0,opencv_receipt=1,onnx_intra=1,onnx_inter=1,environment=1),attribution='nonoverlapping direct compose stage call profiles; Python self sums are conservative upper bounds including untraced ufuncs; builtin self separate; shared children attributed to actual stage invocation; no inclusive sums',gate='one coherent stage/boundary >=25% interpreted corrections pooled27; reject if even conservative upper bound below25%',uncertainty='two profile runs and two uninstrumented totals, plus stage-specific scale to uninstrumented boundary clocks; retain raw inflated upper bound too',clock='perf_counter; attribution clocks not speed evidence',guard='METER_STOP checked before each page; launch meter15%, end unknown'))

def stats(profile):
    s=pstats.Stats(profile);rows=[]
    for (file,line,name),(cc,nc,tt,ct,callers) in s.stats.items():
        rows.append(dict(file=file,line=line,function=name,primitive_calls=cc,calls=nc,self_s=tt,inclusive_s=ct,kind='python_upper' if file!='~' else 'builtin_or_unresolved',callers=[dict(file=k[0],line=k[1],function=k[2],values=v) for k,v in callers.items()]))
    return dict(python_upper_s=sum(r['self_s'] for r in rows if r['kind']=='python_upper'),builtin_or_unresolved_s=sum(r['self_s'] for r in rows if r['kind']!='python_upper'),self_sum_s=sum(r['self_s'] for r in rows),functions=sorted(rows,key=lambda r:-r['self_s']))

def profile():
    from ..shared import detector as dm
    from ..stack import pipeline as pipe
    from .. import rust_field
    assert rust_field.BACKEND=='python'
    dm.MODEL=FL/'onnx/PP-OCRv6_small_det.onnx';start=time.perf_counter();stack=pipe.Stack(image_threads=0)
    opts=stack.detector.session.get_session_options()
    dump(O/'PROFILE_BACKEND.json',dict(import_session_s=time.perf_counter()-start,opencv_requested=0,opencv_observed=cv2.getNumThreads(),onnx_intra=opts.intra_op_num_threads,onnx_inter=opts.inter_op_num_threads,onnx_mode=str(opts.execution_mode),providers=stack.detector.session.get_providers(),backend=rust_field.BACKEND))
    pages=json.loads((O/'SLOW27.json').read_text())['pages'];assert not (O/'PROFILE_RAW.json').exists()
    stack(pages[0]['path'])
    raw=[];originals={k:getattr(pipe,k) for k in STAGES}
    for repetition in range(2):
        for instrumented in (False,True):
            for row in pages:
                assert not (FL.parent/'METER_STOP').exists();assert sha(row['path'])==row['sha256']
                stage_records=[]
                for name,fn in originals.items():
                    def wrapped(*args,_name=name,_fn=fn,**kwargs):
                        p=cProfile.Profile() if instrumented else None;t=time.perf_counter()
                        if p:r=p.runcall(_fn,*args,**kwargs)
                        else:r=_fn(*args,**kwargs)
                        elapsed=time.perf_counter()-t
                        entry=dict(stage=_name,elapsed_s=elapsed)
                        if p:
                            path=O/'pstats'/f'{row["page"]}-{repetition}-{_name}-{len(stage_records)}.pstats';path.parent.mkdir(parents=True,exist_ok=True);p.dump_stats(str(path));entry.update(stats(p));entry['pstats']=str(path.relative_to(O))
                        stage_records.append(entry);return r
                    setattr(pipe,name,wrapped)
                before=dict(rust_field.COUNTERS);r=stack(row['path']);after=dict(rust_field.COUNTERS)
                # Compare final exports with archived H from the same initial route.
                expected=json.loads((OLD/'same-input/H'/(row['page']+'.json')).read_text())['items']
                assert clean(r['items'])==expected
                entry=dict(page=row['page'],repetition=repetition,instrumented=instrumented,timing=r['timing'],stages=r['stages'],backend={k:after[k]-before[k] for k in after},profiles=stage_records,final_exact=True)
                raw.append(entry);dump(O/'PROFILE_RAW.json',raw)
                print('profile',repetition,instrumented,row['page'],round(r['timing']['correction_s'],3),flush=True)
    for name,fn in originals.items():setattr(pipe,name,fn)

def census():
    from ..shared import detector as dm
    from ..stack import pipeline as pipe
    from .. import rust_field
    dm.MODEL=FL/'onnx/PP-OCRv6_small_det.onnx';stack=pipe.Stack(image_threads=0)
    pages=json.loads((O/'SLOW27.json').read_text())['pages'];records=[]
    for row in pages:
        assert not (FL.parent/'METER_STOP').exists();assert sha(row['path'])==row['sha256']
        gray=cv2.imread(row['path'],0);pm,_=stack.detector.infer(gray);initial=dm.postprocess(pm,gray.shape[::-1])
        prior=json.loads((OLD/'same-input/H'/(row['page']+'.json')).read_text())
        initial_sha=hashlib.sha256(json.dumps(clean(initial),sort_keys=True).encode()).hexdigest();map_sha=hashlib.sha256(pm.tobytes()).hexdigest()
        assert initial_sha==prior['initial_sha256'] and map_sha==prior['map_sha256']
        p=cProfile.Profile();before=dict(rust_field.COUNTERS)
        r=p.runcall(pipe.compose,gray,pm,initial,stack.detector)
        path=O/'census-pstats'/(row['page']+'.pstats');path.parent.mkdir(parents=True,exist_ok=True);p.dump_stats(str(path))
        assert clean(r['items'])==prior['items']
        record=dict(page=row['page'],initial_sha256=initial_sha,map_sha256=map_sha,backend={k:rust_field.COUNTERS[k]-before[k] for k in before},pstats=str(path.relative_to(O)),**stats(p))
        records.append(record);dump(O/'OPERATION_CENSUS.json',records)
        print('census',row['page'],flush=True)

def clocks():
    """Plain integrated Stack, no additional wrappers/profiler inside clocks."""
    from ..shared import detector as dm
    from ..stack import pipeline as pipe
    from .. import rust_field
    assert rust_field.BACKEND=='python' and pipe.field_proposals.__name__=='run'
    dm.MODEL=FL/'onnx/PP-OCRv6_small_det.onnx';stack=pipe.Stack(image_threads=0)
    pages=json.loads((O/'SLOW27.json').read_text())['pages'];records=[]
    assert not (O/'PURE_CLOCK_RAW.json').exists()
    dump(O/'PURE_CLOCK_PLAN.json',dict(warmup_pages=1,passes=2,order='all sorted fixed27 sequential in each pass',backend='python',extra_wrappers=False,profiler=False,threads='same request0/receipt1; ONNX sequential1/1; environment1',purpose='strict uninstrumented correction denominator; earlier PROFILE_RAW no-profiler passes retained as lightweight stage-clock measurements; no candidate or speed claim',drift='retain both complete passes; no invalid/slow-page exclusion or best-pass selection'))
    stack(pages[0]['path'])
    for repetition in range(2):
        for row in pages:
            assert not (FL.parent/'METER_STOP').exists();assert sha(row['path'])==row['sha256']
            before=dict(rust_field.COUNTERS);r=stack(row['path']);after=dict(rust_field.COUNTERS)
            expected=json.loads((OLD/'same-input/H'/(row['page']+'.json')).read_text())['items']
            assert clean(r['items'])==expected
            records.append(dict(page=row['page'],repetition=repetition,timing=r['timing'],stages=r['stages'],backend={k:after[k]-before[k] for k in before},final_exact=True,extra_wrappers=False))
            dump(O/'PURE_CLOCK_RAW.json',records);print('plain-clock',repetition,row['page'],round(r['timing']['correction_s'],3),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','profile','census','clocks']);a=p.parse_args();globals()[a.action]()

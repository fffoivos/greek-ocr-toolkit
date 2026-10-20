"""R8-RUST-02 sequential source-bound development capture/replay/clock runner.

No private input, background work or production mutation. Run as a module.
"""
import argparse
import copy
import hashlib
import importlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import sys
import time

os.environ.update({k:'1' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')})
import cv2
import numpy as np
from .r8_curl_trace import FL, ROOT, clean, dump, inputs, sha

O = ROOT/'.astra/fast_lines/out/round8/R8-RUST-02-i1'
FIX = ROOT/'prototypes/fast_lines/rust_field/fixtures'


def package(name, source, backend='python'):
    setup_start=time.perf_counter()
    os.environ['FAST_LINES_FIELD_BACKEND'] = backend
    os.environ['FAST_LINES_FIELD_LIBRARY'] = str(ROOT/'prototypes/fast_lines/rust_field/target/release/libfast_lines_field.dylib')
    path = source/'prototypes/fast_lines'
    spec = importlib.util.spec_from_file_location(name, path/'__init__.py', submodule_search_locations=[str(path)])
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    dm = importlib.import_module(name+'.shared.detector')
    dm.MODEL = FL/'onnx/PP-OCRv6_small_det.onnx'
    pipe = importlib.import_module(name+'.stack.pipeline')
    gf=importlib.import_module(name+'.shared.geometry_page_field')
    if source==O/'H':
        # Entry counters only; no timers/callbacks or numerical changes.
        text=inspect.getsource(gf.render);target='            # Each column keeps'
        assert text.count(target)==1
        gf._rust02_counters=dict(python=0,rust=0,fallback=0,prepared=0,copied_bytes=0)
        text=text.replace(target,"            _rust02_counters['python']+=1\n"+target)
        exec(compile(text,gf.__file__,'exec'),gf.__dict__)
        gf._rust02_render_source=text
        importlib.import_module(name+'.shared.geometry_field_detector').render=gf.render
    stack=pipe.Stack(image_threads=0)
    setup_records=O/'SETUP.json'
    entries=json.loads(setup_records.read_text()) if setup_records.exists() else []
    opts=stack.detector.session.get_session_options()
    entries.append(dict(package=name,source=str(source),backend=backend,import_and_session_s=time.perf_counter()-setup_start,session_s=stack.startup_s,opencv_requested=0,opencv_observed=cv2.getNumThreads(),onnx_intra=opts.intra_op_num_threads,onnx_inter=opts.inter_op_num_threads,onnx_mode=str(opts.execution_mode),providers=stack.detector.session.get_providers()))
    dump(setup_records,entries)
    return dm, pipe, stack


def counter(name):
    mod = sys.modules.get(name+'.rust_field')
    if mod:return dict(mod.COUNTERS)
    gf=sys.modules.get(name+'.shared.geometry_page_field')
    return dict(gf._rust02_counters) if gf and hasattr(gf,'_rust02_counters') else dict(python=0,rust=0,fallback=0,prepared=0,copied_bytes=0)


def difference(a,b):
    return {k:b[k]-a[k] for k in b}


def allpages():
    return inputs()+json.loads((O/'OWNER22_FROZEN.json').read_text())['pages']


def sanitize(value):
    value = clean(value)
    if isinstance(value,dict):
        return {k:sanitize(v) for k,v in value.items() if k not in ('seconds','stages','timing') and not k.endswith('_s')}
    if isinstance(value,list):return [sanitize(v) for v in value]
    return value


def capture():
    """Commit real numeric arrays and prepared render consumers, never owner pixels."""
    FIX.mkdir(parents=True,exist_ok=True)
    dm,pipe,stack=package('capture_h',O/'H')
    gf=importlib.import_module('capture_h.shared.geometry_page_field')
    selected=[p for p in inputs() if p['page'] in (
        's2-86865c33eef5932c013b-p00005','s2-49598b2e848ab1f0ee1e-p00001',
        's2-3229200bf47ca465a42d-p00005','an-c8b96a901917-p000036',
        'an-466cffad2cba-p000323','s2-23a70964fda83cb7aeb1-p00003')]
    manifests=[]
    for row in selected:
        assert sha(row['path'])==row['sha256']
        gray=cv2.imread(row['path'],0);pm,_=stack.detector.infer(gray);items=dm.postprocess(pm,gray.shape[::-1])
        preparations=[];original=gf.prepare
        def prepare(*a,**kw):
            r=original(*a,**kw);preparations.append(r);return r
        gf.prepare=prepare
        captures=[]
        def observe(frame,event,arg):
            if event=='call' and frame.f_code.co_name=='shifts_many' and frame.f_code.co_filename==gf.__file__:
                v=frame.f_locals
                # First left, last outward right, first/last refinement batch.
                captures.append({k:np.array(v[k],copy=True) for k in ['before','moved','columns','profiles','ys','lag','lengths'] } | ({} if v['energy'] is None else {'energy':np.array(v['energy'],copy=True)}))
        sys.setprofile(observe)
        try:r=gf.render(gray,items,route='slow')
        finally:sys.setprofile(None);gf.prepare=original
        if not captures:continue
        ids=sorted(set([0,len(captures)//2,len(captures)-1,next((i for i,c in enumerate(captures) if len(c['columns'])>1),0)]))
        for i in ids:
            c=captures[i];p=FIX/(row['page']+f'-batch{i:03d}.npz');np.savez_compressed(p,**c)
            manifests.append(dict(file=p.name,sha256=sha(p),page=row['page'],native_sha256=row['sha256'],batch=i,shape=list(c['moved'].shape),columns=c['columns'].tolist(),lengths=c['lengths'].tolist()))
        source=preparations[0]
        p=FIX/(row['page']+'-render.npz');unique=[]
        for entry in captures:
            if not any(np.array_equal(entry['profiles'],q) for q in unique):unique.append(entry['profiles'])
        np.savez_compressed(p,**{f'profiles{i}':q for i,q in enumerate(unique)})
        dump(FIX/(row['page']+'-render.json'),dict(page=row['page'],gray_shape=list(gray.shape),items=items,source={k:v for k,v in source.items() if k in ('components','scale')},expected=sanitize(r),prepared_profiles_sha256=sha(p),native_sha256=row['sha256']))
        print('capture',row['page'],len(captures),flush=True)
    assert len(manifests)>=12
    dump(FIX/'manifest.json',dict(source='H checkpoint',schema='CONTRACT.md',batches=manifests,capture_kind='standalone actual native-page render(route=slow); may bypass runtime edge gate; speed replay uses only actual integrated live calls'))


def boundary():
    """Explicit paired replay at every real H batch; not a production dual route."""
    from ..rust_field import Batch, shifts_python
    dm,pipe,stack=package('boundary_h',O/'H')
    gf=importlib.import_module('boundary_h.shared.geometry_page_field')
    source=gf._rust02_render_source;needle='        def shifts_many('
    assert source.count(needle)==1
    source=source.replace(needle,'        @_rust02_replay\n'+needle)
    records=[];contexts={};page=None;setup=[]
    plan=dict(warmup_per_batch=1,pairs_per_batch=7,order='Python/Rust on even pair; Rust/Python on odd',inputs='immutable actual H render batch; wrapper copies included; per-field profile preparation timed separately',population='all208+separate22, live route only',timer='perf_counter_ns',callbacks=0)
    dump(O/'BOUNDARY_PLAN.json',plan)
    def decorate(fn):
        def replay(before,moved,columns,energy=None):
            v=inspect.getclosurevars(fn).nonlocals
            ident=id(v['profiles'])
            if ident not in contexts:
                t=time.perf_counter_ns();ctx=Batch(v['profiles'],v['ys'],v['lag'],v['lengths'],backend='rust');elapsed=(time.perf_counter_ns()-t)/1e9
                contexts[ident]=ctx;setup.append(dict(page=page,seconds=elapsed,bytes=ctx.native_profiles.nbytes+ctx.native_ys.nbytes+ctx.native_lag.nbytes+ctx.native_lengths.nbytes))
            ctx=contexts[ident]
            expected=fn(before,moved,columns,energy);actual=ctx.shifts_many(before,moved,columns,energy,diagnostic=True)
            exact=all(np.array_equal(a.view(np.uint64),b.view(np.uint64)) for a,b in zip(expected,actual[:2]))
            oracle=shifts_python(before,moved,columns,v['profiles'],v['ys'],v['lag'],v['lengths'],energy,diagnostic=True)
            oracle_exact=all(np.array_equal(a.view(np.uint64),b.view(np.uint64)) for a,b in zip(expected,oracle[:2]))
            score_exact=np.array_equal(actual[2].view(np.uint64),oracle[2].view(np.uint64))
            raw=[]
            for pair in range(7):
                times={}
                for key in ('HR' if pair%2==0 else 'RH'):
                    t=time.perf_counter_ns()
                    if key=='H':fn(before,moved,columns,energy)
                    else:ctx.shifts_many(before,moved,columns,energy)
                    times[key]=(time.perf_counter_ns()-t)/1e9
                raw.append(times)
            records.append(dict(page=page,shape=list(moved.shape),columns=list(map(int,columns)),exact=exact,oracle_exact=oracle_exact,score_exact=score_exact,raw=raw))
            return expected
        return replay
    gf._rust02_replay=decorate
    exec(compile(source,gf.__file__,'exec'),gf.__dict__)
    importlib.import_module('boundary_h.shared.geometry_field_detector').render=gf.render
    for row in allpages():
        assert not (FL.parent/'METER_STOP').exists()
        page=row['page'];contexts.clear()
        result=stack(row['path'],parked=row.get('parked',False))
        expected=json.loads((O/'same-input/H'/(page+'.json')).read_text())['items']
        assert clean(result['items'])==expected
        dump(O/'BOUNDARY_RAW.json',dict(plan=plan,records=records,field_setup=setup))
        print('boundary',page,len(records),flush=True)
    assert all(r['exact'] and r['oracle_exact'] and r['score_exact'] for r in records)


def sameinput():
    arms={k:package('same_'+k,O/'H' if k=='H' else ROOT,'python' if k=='H' else 'rust') for k in ['H','R']}
    ledger=[]
    for i,row in enumerate(allpages()):
        assert not (FL.parent/'METER_STOP').exists()
        assert sha(row['path'])==row['sha256']
        gray=cv2.imread(row['path'],0);dm,pipe,st=arms['H'];pm,meta=st.detector.infer(gray);initial=dm.postprocess(pm,gray.shape[::-1]);original_hash=hashlib.sha256(json.dumps(clean(initial),sort_keys=True).encode()).hexdigest();map_hash=hashlib.sha256(pm.tobytes()).hexdigest()
        results={};stats={}
        for key,(dm,pipe,st) in arms.items():
            before=counter('same_'+key);t=time.perf_counter()
            r=pipe.compose(gray,pm,initial,st.detector) if not row.get('parked') else dict(items=initial,parked=True,stages={})
            elapsed=time.perf_counter()-t
            results[key]=r;stats[key]=dict(correction_s=elapsed,stages=r['stages'],backend=difference(before,counter('same_'+key)))
            directory=O/'same-input'/key
            dump(directory/(row['page']+'.json'),dict(items=r['items'],page=row['page'],initial_sha256=original_hash,map_sha256=map_hash))
            dump(directory/(row['page']+'.evidence.json'),{k:v for k,v in r.items() if k!='items'})
        assert original_hash==hashlib.sha256(json.dumps(clean(initial),sort_keys=True).encode()).hexdigest()
        assert map_hash==hashlib.sha256(pm.tobytes()).hexdigest()
        final_equal=clean(results['H']['items'])==clean(results['R']['items'])
        intermediate_equal=sanitize(results['H'])==sanitize(results['R'])
        # Whole page, every actual strip and actual-mask coverage for each arm locally.
        # Equal polygons imply identical masks but rasterize independently as well.
        from ..shared.geometry_bands import crop_mask
        from ..shared.geometry import roi
        from ..shared.contracts import bbox
        from ..shared.review import overlay
        mask_equal=True
        for key in arms:
            d=O/'rasters'/key/row['page'];d.mkdir(parents=True,exist_ok=True)
            coverage=np.zeros(gray.shape,np.uint16)
            cv2.imwrite(str(d/'page.png'),overlay(gray,results[key]['items'],width=1200))
            for j,q in enumerate(results[key]['items']):
                a,b,c,z=roi(bbox(q),gray.shape);raw=gray[b:z,a:c];mask=crop_mask(raw.shape,q,(a,b))
                coverage[b:z,a:c]+=(mask>0)
                cv2.imwrite(str(d/f'{j:03d}.png'),np.where(mask,raw,255))
            np.savez_compressed(d/'coverage.npz',coverage=coverage)
            if key=='H':old=coverage
            else:mask_equal=np.array_equal(old,coverage)
        entry=dict(page=row['page'],appendix=i>=208,final_equal=final_equal,intermediate_equal=intermediate_equal,coverage_equal=mask_equal,rows=len(results['R']['items']),stats=stats)
        # Bound H to previous hardening208 exports too.
        if i<208:
            prior=json.loads((O.parent/'R8-CURL-03-i3/candidate208-same-input'/(row['page']+'.json')).read_text())
            entry['H_prior_equal']=clean(results['H']['items'])==prior['items']
        ledger.append(entry);dump(O/'SAME_INPUT_LEDGER.json',ledger)
        print('same',i+1,row['page'],final_equal,intermediate_equal,stats['R']['backend'],flush=True)
    assert len(ledger)==230


def benchmark():
    # Declare fixed repetitions/orders/drift before any measured samples.
    plan=dict(repetitions_per_order=2,orders=['HR','RH'],population='all208 plus separate22, no-call pages included',warmup='two affected pages once each per arm',opencv_requested=0,opencv_expected=1,onnx='CPU sequential intra/inter1',drift='order block invalid if aggregate unchanged primary detector differs >5% between arms; retain all samples; no automatic replacement',setup='compilation/import/session setup separate; warmed file decode through final',no_parallelism=True)
    dump(O/'TIMING_PLAN.json',plan)
    arms={k:package('clock_'+k,O/'H' if k=='H' else ROOT,'python' if k=='H' else 'rust') for k in ['H','R']}
    rows=allpages()
    for key,(_,_,st) in arms.items():
        for page in ['s2-86865c33eef5932c013b-p00005','s2-49598b2e848ab1f0ee1e-p00001']:
            st(next(r['path'] for r in rows if r['page']==page))
    raw=[]
    for repetition in range(2):
        for order in ['HR','RH']:
            for i,row in enumerate(rows if order=='HR' else rows[::-1]):
                assert not (FL.parent/'METER_STOP').exists()
                records={}
                for key in order:
                    before=counter('clock_'+key);t=time.perf_counter();r=arms[key][2](row['path'],parked=row.get('parked',False));wall=time.perf_counter()-t
                    expected=json.loads((O/'same-input'/key/(row['page']+'.json')).read_text())['items']
                    old_evidence=json.loads((O/'same-input'/key/(row['page']+'.evidence.json')).read_text())
                    core={k:v for k,v in r.items() if k not in ('items','original','image_size','timing')}
                    if row.get('parked'):core.pop('counts',None)
                    records[key]=dict(timing=r['timing'],stages=r['stages'],wall_s=wall,export_equal=clean(r['items'])==expected,intermediate_equal=sanitize(core)==sanitize(old_evidence),backend=difference(before,counter('clock_'+key)))
                raw.append(dict(repetition=repetition,order=order,page=row['page'],appendix=row['page'].startswith('owner-'),records=records))
                if i%10==0:dump(O/'TIMING_RAW.json',dict(plan=plan,records=raw));print('clock',repetition,order,i+1,flush=True)
            dump(O/'TIMING_RAW.json',dict(plan=plan,records=raw))
    print('clock complete',flush=True)


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['capture','sameinput','benchmark','boundary']);args=a.parse_args()
    globals()[args.mode]()

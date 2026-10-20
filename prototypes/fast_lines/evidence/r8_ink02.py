"""Sequential INK02 development qualification; no runtime importer or private data."""
import os
os.environ.update({k:'1' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')})
import argparse,hashlib,importlib,importlib.util,json,sys,time
from collections import Counter
from pathlib import Path
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'.astra/fast_lines/out/round8/R8-INK-02-i1'
FL=ROOT.parent/'greek-ocr-toolkit-astra-lines4/.astra/fast_lines'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clean(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items() if k not in ('_source','_labels','_selected_pixel_support')}
    if isinstance(x,(tuple,list)):return [clean(v) for v in x]
    return x
def sanitize(x):
    x=clean(x)
    if isinstance(x,dict):return {k:sanitize(v) for k,v in x.items() if k not in ('seconds','timing','stages') and not k.endswith('_s')}
    if isinstance(x,list):return [sanitize(v) for v in x]
    return x
def dump(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(clean(v),ensure_ascii=False,indent=1)+'\n')
def sources(root):
    return {str(p.relative_to(root)):sha(p) for p in (root/'prototypes/fast_lines').rglob('*.py') if '/evidence/' not in str(p) and not p.name.startswith('test_')}
def package(name,source):
    path=source/'prototypes/fast_lines';spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
    dm=importlib.import_module(name+'.shared.detector');dm.MODEL=FL/'onnx/PP-OCRv6_small_det.onnx'
    pipe=importlib.import_module(name+'.stack.pipeline');stack=pipe.Stack(image_threads=0)
    return dict(name=name,source=source,dm=dm,pipe=pipe,stack=stack)
def load():
    c=json.loads((OUT/'INK02_COHORT.json').read_text());assert c['denominator']==208
    return c

def masks(arm,items,shape):
    gb=importlib.import_module(arm['name']+'.shared.geometry_bands');geo=importlib.import_module(arm['name']+'.shared.geometry');co=importlib.import_module(arm['name']+'.shared.contracts')
    records=[];coverage=np.zeros(shape,np.uint16)
    for q in items:
        a,b,c,d=geo.roi(co.bbox(q),shape);m=gb.crop_mask((d-b,c-a),q,(a,b));coverage[b:d,a:c]+=m.astype(np.uint16)
        records.append(dict(roi=[a,b,c,d],sha256=hashlib.sha256(m.tobytes()).hexdigest()))
    return records,hashlib.sha256(coverage.tobytes()).hexdigest()

class Capture:
    def __init__(self,arm):
        self.arm=arm;self.calls=[];self.active=None;self.restores=[];name=arm['name']
        own=importlib.import_module(name+'.shared.ink_ownership');self.own=own
        original=own.analyze
        def analyze(gray,items,regions=None,**kw):
            caller=sys._getframe(1);rec=dict(caller=Path(caller.f_code.co_filename).name+':'+caller.f_code.co_name+':'+str(caller.f_lineno),coordinate_frame='native full page',index_space='requested regions',counts=Counter(),atlases=[],matches=[],glyphs=[])
            self.active=rec
            try:r=original(gray,items,regions,**dict(kw,detail=True))
            finally:self.active=None
            rec['result']=sanitize(r);rec['counts']=dict(rec['counts']);self.calls.append(rec)
            # A separate dense observation, never a runtime provider or truth label.
            if r['atlas_glyphs']:
                dense=original(gray,items,regions,**dict(kw,detail=True,route='dense'))
                rec['dense']=sanitize(dense);rec['dense_decision_disagreements']=[i for i,(a,b) in enumerate(zip(r['regions'],dense['regions'])) if (a['ownership'],a['front_votes'],a['back_votes'])!=(b['ownership'],b['front_votes'],b['back_votes'])]
                rec['witness_panels']=self.panels(gray,r,dense,len(self.calls)-1)
            if not kw.get('detail',False):
                for row in r['regions']:
                    row.pop('matches',None);row.pop('witnesses',None)
            return r
        for suffix,attr in [('features_ink.pipeline','analyze'),('shared.type_recovery','ownership'),('shared.type_residual_recovery','ownership')]:
            module=importlib.import_module(name+'.'+suffix);self.replace(module,attr,analyze)
        factory=own.glyph_atlas
        def prepare(raw):
            atlas=factory(raw)
            if self.active is not None:
                vectors,aspects=(atlas.vectors,atlas.aspects) if hasattr(atlas,'vectors') else atlas
                self.active['counts']['atlas_builds']+=1
                self.active['atlases'].append(dict(vectors_sha256=hashlib.sha256(vectors.tobytes()).hexdigest(),aspects_sha256=hashlib.sha256(aspects.tobytes()).hexdigest(),shape=list(vectors.shape),vector_dtype=str(vectors.dtype),aspect_dtype=str(aspects.dtype),exemplars=[dict(bbox=g['bbox'],line=g.get('line')) for g in raw]))
            return atlas
        self.replace(own,'glyph_atlas',prepare)
        matcher=own.match_glyphs
        def match(query,atlas,**kw):
            r=matcher(query,atlas,**kw)
            if self.active is not None:self.active['counts']['match_requests']+=1;self.active['matches'].append(clean(r))
            return r
        self.replace(own,'match_glyphs',match)
        glyph=own.glyphs
        def glyphs(*a,**kw):
            r=glyph(*a,**kw)
            if self.active is not None:
                self.active['counts']['glyph_requests']+=1
                self.active['glyphs'].append(dict(bbox=list(a[1]),height=float(a[2]),limit=kw.get('limit',64),selected=len(r),vectors_sha256=hashlib.sha256(np.array([g['vector'] for g in r],np.float32).tobytes()).hexdigest(),aspects_sha256=hashlib.sha256(np.array([g['aspect'] for g in r]).tobytes()).hexdigest(),bboxes=[g['bbox'] for g in r]))
            return r
        self.replace(own,'glyphs',glyphs)
        for attr in ['connectedComponentsWithStats','resize']:
            fn=getattr(cv2,attr)
            def kernel(*a,_name=attr,_fn=fn,**kw):
                if self.active is not None:self.active['counts'][_name]+=1;self.active['counts'][_name+'_input_pixels']+=a[0].size
                return _fn(*a,**kw)
            self.replace(cv2,attr,kernel)
    def replace(self,obj,attr,value):self.restores.append((obj,attr,getattr(obj,attr)));setattr(obj,attr,value)
    def close(self):
        for obj,attr,value in reversed(self.restores):setattr(obj,attr,value)
    def panels(self,gray,explicit,dense,call):
        panels=[]
        # At most one genuine witness for each direct/reflected/unknown query class per call.
        for label in ['front','back','unknown']:
            rows=[(i,r) for i,r in enumerate(explicit['regions']) if r['ownership']==label and r.get('matches')]
            if not rows:continue
            i,r=rows[0];m=(r.get('witnesses') or r['matches'])[0];j=m['reflected_id'] if m['margin']>0 else m['direct_id']
            exemplar=self.calls[-1]['atlases'][0]['exemplars'][j]['bbox'];tiles=[]
            for box in [m['bbox'],exemplar]:
                a,b,c,d=map(int,box);p=gray[b:d,a:c];tile=np.full((110,220),255,np.uint8);h,w=p.shape;tile[4:4+min(h,106),4:4+min(w,216)]=p[:106,:216];tiles.append(tile)
            path=OUT/'witnesses'/f'{self.page}.{self.arm["name"]}.call{call}.{label}.png';path.parent.mkdir(exist_ok=True);cv2.imwrite(str(path),np.hstack(tiles))
            panels.append(dict(file=str(path.relative_to(OUT)),region=i,classification=label,query_bbox=m['bbox'],exemplar_bbox=exemplar,match=m,dense_region=dense['regions'][i],interpretation='native unresized query left and actual scored exemplar right; source identity unvalidated'))
        return panels

def qualify(base):
    c=load();arms={k:package('ink02'+k,base if k=='B' else ROOT) for k in ['B','C']};records=[];cohort=set(c['cohort_pages']);appendix=c['owner22_separate']
    receipt=OUT/'PARITY208.json'
    if receipt.exists():
        previous=json.loads(receipt.read_text())
        assert previous['candidate_source']==sources(ROOT) and previous['baseline_source']==sources(base)
        assert previous['cohort_sha256']==sha(OUT/'INK02_COHORT.json')
        records=previous['records']
    # No appendix atlas consumers in frozen evidence; retain explicit separate zero-call receipt.
    assert all(not any(q['atlas_glyphs'] for q in r['calls']) for r in appendix)
    dump(OUT/'OWNER22_APPLICABILITY.json',dict(pages=appendix,changed_atlas_consumers=0,reason='none in saved accepted-H observations; unchanged non-atlas runtime dependencies; no appendix atlas rerun required'))
    for n,row in enumerate(c['pages']):
        assert not (FL.parent/'METER_STOP').exists();assert sha(row['path'])==row['sha256'];assert sha(row['evidence'])==row['evidence_sha256']
        if n<len(records):assert records[n]['page']==row['page'];continue
        p=row['page'];gray=cv2.imread(row['path'],0);gray.flags.writeable=False;results={};calls={}
        for k in (['B','C'] if p in cohort else ['C']):
            cap=Capture(arms[k]);cap.page=p
            try:r=arms[k]['stack'](row['path'],parked=row.get('parked',False))
            finally:cap.close()
            calls[k]=cap.calls;results[k]=r
        old=json.loads(Path(row['export']).read_text())['items'];saved=json.loads(Path(row['evidence']).read_text());r=results['C']
        assert clean(r['items'])==old,p+' export'
        saved_core={k:v for k,v in saved.items() if k not in ('page','group','reference')}
        current_core={k:v for k,v in r.items() if k not in ('items','image_size','original')}
        if row.get('parked'):assert current_core.pop('counts')=={}
        assert sanitize(current_core)==sanitize(saved_core),p+' non-clock decisions'
        cm,cc=masks(arms['C'],r['items'],gray.shape);bm,bc=masks(arms['B'],old,gray.shape);assert cm==bm and cc==bc
        if 'B' in results:
            assert sanitize(results['B'])==sanitize(r),p+' fresh baseline'
            # Timers and panel arm filenames differ; compare all numerical and native reference inputs.
            def core(calls):return [{k:v for k,v in call.items() if k not in ('witness_panels','caller')} for call in calls]
            assert core(calls['B'])==core(calls['C']),p+' B5 observations'
        for call in calls['C']:assert call['counts'].get('atlas_builds',0)==int(call['result']['atlas_glyphs']>0)
        dump(OUT/'calls'/(p+'.json'),calls);dump(OUT/'candidate208'/(p+'.json'),dict(items=r['items'],removed=r.get('removed'),masks=cm,coverage_sha256=cc))
        rec=dict(page=p,roles=row['roles'],callers=[dict(caller=q['caller'],counts=q['counts'],atlas_glyphs=q['result']['atlas_glyphs'],anchors=q['result']['anchors'],suspects=q['result']['suspects'],suppress_indices=q['result']['suppress_indices'],decisions=[z['ownership'] for z in q['result']['regions']],dense_decision_disagreements=q.get('dense_decision_disagreements',[])) for q in calls['C']],fresh_baseline=p in cohort,all_nonclock_decisions_equal=True,actual_masks_equal=True,coverage_equal=True,items=len(r['items']),descriptive_timing=r['timing'])
        records.append(rec);dump(OUT/'PARITY208.json',dict(records=records,candidate_source=sources(ROOT),baseline_source=sources(base),cohort_sha256=sha(OUT/'INK02_COHORT.json'),model_sha256=sha(FL/'onnx/PP-OCRv6_small_det.onnx')))
        print(n+1,p,'exact',flush=True)

def timing(base):
    c=load();rows=[r for r in c['pages'] if r['roles']];arms={k:package('ink02time'+k,base if k=='B' else ROOT) for k in ['B','C']}
    plan=dict(repetitions_per_order=2,orders=['BC','CB'],pages=[r['page'] for r in rows],warmup='0ce9 and 93f8 once per arm',opencv_request=0,opencv_observed=cv2.getNumThreads(),onnx='CPU sequential 1/1',drift_rule='order block invalid if pooled unchanged detector time differs >5%; no automatic replacement',source=sources(ROOT),baseline_source=sources(base),quiet='coordinator supplied quiet MacBook window; sequential only')
    dump(OUT/'TIMING_PLAN.json',plan)
    for k in arms:
        for row in rows:
            if '0ce9' in row['page'] or '93f8' in row['page']:arms[k]['stack'](row['path'])
    raw=[]
    for order in plan['orders']:
        for rep in range(2):
            for row in rows if order=='BC' else rows[::-1]:
                assert not (FL.parent/'METER_STOP').exists();assert sha(row['path'])==row['sha256'];pair={}
                for k in order:
                    r=arms[k]['stack'](row['path'],parked=row.get('parked',False));assert clean(r['items'])==json.loads(Path(row['export']).read_text())['items'];pair[k]=dict(timing=r['timing'],stages=r['stages'])
                raw.append(dict(order=order,rep=rep,page=row['page'],roles=row['roles'],arms=pair));dump(OUT/'TIMING_RAW.json',raw)
            print('timing',order,rep,'complete',flush=True)
    blocks=[]
    for order in plan['orders']:
        rs=[r for r in raw if r['order']==order];dt={k:sum(r['arms'][k]['timing']['detector_s'] for r in rs) for k in arms};drift=dt['C']/dt['B']-1
        blocks.append(dict(order=order,detector_sum_s=dt,detector_drift_fraction=drift,valid=abs(drift)<=.05,median_delta_ms={key:float(np.median([(r['arms']['C']['timing'][key]-r['arms']['B']['timing'][key])*1000 for r in rs])) for key in ['correction_s','total_s']},affected_ink_stage_median_delta_ms=float(np.median([(r['arms']['C']['stages']['ink_s']-r['arms']['B']['stages']['ink_s'])*1000 for r in rs if 'atlas-active' in r['roles']]))))
    per=[]
    for row in rows:
        rs=[r for r in raw if r['page']==row['page']];stats=[]
        for order in plan['orders']:
            subset=[r for r in rs if r['order']==order];stats.append(dict(order=order,delta_ms={key:float(np.median([(r['arms']['C']['timing'][key]-r['arms']['B']['timing'][key])*1000 for r in subset])) for key in ['correction_s','detector_s','total_s']},ink_delta_ms=float(np.median([(r['arms']['C']['stages']['ink_s']-r['arms']['B']['stages']['ink_s'])*1000 for r in subset]))))
        per.append(dict(page=row['page'],roles=row['roles'],orders=stats))
    dump(OUT/'TIMING_SUMMARY.json',dict(blocks=blocks,pages=per,no_speed_claim=True));print(blocks,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['qualify','timing']);p.add_argument('--baseline',type=Path,required=True);a=p.parse_args();globals()[a.action](a.baseline)

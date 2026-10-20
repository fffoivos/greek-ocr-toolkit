"""Final-source parity/caller/work receipts, separate from uninstrumented clocks."""
import os
os.environ.update({k:'1' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')})
import argparse,hashlib,importlib,json,sys
from collections import Counter
from pathlib import Path
import cv2,numpy as np
from .r8_ink02 import ROOT,FL,clean,sanitize,dump,sha,sources,package,masks
from .r8_ink02_i2 import O,I
class Capture:
    def __init__(self,arm):
        self.arm=arm;self.calls=[];self.active=None;self.restores=[];name=arm['name']
        own=importlib.import_module(name+'.shared.ink_ownership');self.own=own
        original=own.analyze
        def analyze(gray,items,regions=None,**kw):
            caller=sys._getframe(1);rec=dict(caller=Path(caller.f_code.co_filename).name+':'+caller.f_code.co_name+':'+str(caller.f_lineno),coordinate_frame='native full page',index_space='requested regions',counts=Counter(),atlases=[],matches=[],glyphs=[])
            rec.update(pool=clean(items),requested_regions=clean([__import__('importlib').import_module(name+'.shared.contracts').bbox(q) for q in items] if regions is None else regions),explicit_regions=regions is not None,route=kw.get('route','explicit'))
            self.active=rec
            try:r=original(gray,items,regions,**dict(kw,detail=True))
            finally:self.active=None
            rec['result']=sanitize(r);rec['counts']=dict(rec['counts']);self.calls.append(rec)
            if not kw.get('detail',False):
                for row in r['regions']:
                    row.pop('matches',None);row.pop('witnesses',None)
            return r
        for suffix,attr in [('features_ink.pipeline','analyze'),('shared.type_recovery','ownership'),('shared.type_residual_recovery','ownership')]:
            module=importlib.import_module(name+'.'+suffix);self.replace(module,attr,analyze)
        self.replace(own,'analyze',analyze)
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

class FullCapture(Capture):
    def __init__(self,arm):
        super().__init__(arm);self.faint_calls=[];self.faint_active=None;name=arm['name']
        faint=importlib.import_module(name+'.shared.ink_faintness');old=arm['pipe'].relative_faintness
        def relative(gray,items,**kw):
            f=sys._getframe(1);rec=dict(caller=Path(f.f_code.co_filename).name+':'+f.f_code.co_name+':'+str(f.f_lineno),pool=clean(items),selected_indices=clean(sorted(kw['selected_indices'])) if kw.get('selected_indices') is not None else None,supplied_height=kw.get('height'),counts=Counter(),components=[])
            self.faint_active=rec
            try:r=old(gray,items,**dict(kw,detail=True))
            finally:self.faint_active=None
            rec['result']=sanitize(r);rec['counts']=dict(rec['counts']);self.faint_calls.append(rec)
            if not kw.get('detail',False) and 'calibration' in r:r=dict(r,calibration=[dict(line=q['line'],bbox=q['bbox']) for q in r['calibration']])
            return r
        self.replace(arm['pipe'],'relative_faintness',relative)
        fn=faint.components
        def components(gray,item,height,**kw):
            r=fn(gray,item,height,**kw)
            if self.faint_active is not None:
                self.faint_active['counts']['component_requests']+=1
                self.faint_active['components'].append(dict(item=clean(item),height=height,route=kw.get('route','slow'),result=clean(r)))
            return r
        self.replace(faint,'components',components)
        scout=importlib.import_module(name+'.shared.ink_faint_scout');fn_scout=scout.render
        def scout_render(*a,**kw):
            if self.faint_active is not None:self.faint_active['counts']['scout_builds']+=1
            return fn_scout(*a,**kw)
        self.replace(scout,'render',scout_render)
        for attr in ['connectedComponentsWithStats','resize']:
            fn_kernel=getattr(cv2,attr)
            def kernel(*a,_name=attr,_fn=fn_kernel,**kw):
                if self.faint_active is not None:self.faint_active['counts'][_name]+=1;self.faint_active['counts'][_name+'_input_pixels']+=a[0].size
                return _fn(*a,**kw)
            self.replace(cv2,attr,kernel)

def core(calls):return [{k:v for k,v in q.items() if k!='caller'} for q in calls]

def qualify(base):
    c=json.loads((I/'INK02_COHORT.json').read_text());assert c['denominator']==208
    arms={k:package('ink02i2'+k,base if k=='B' else ROOT) for k in ['B','C']};records=[];receipt=O/'PARITY208.json'
    if receipt.exists():
        old=json.loads(receipt.read_text());assert old['candidate_source']==sources(ROOT) and old['baseline_source']==sources(base);records=old['records']
    for n,row in enumerate(c['pages']):
        if n<len(records):assert records[n]['page']==row['page'];continue
        assert not (FL.parent/'METER_STOP').exists();assert sha(row['path'])==row['sha256'];assert sha(row['evidence'])==row['evidence_sha256']
        p=row['page'];gray=cv2.imread(row['path'],0);results={};calls={};faint={}
        for k in (['B','C'] if p in c['cohort_pages'] else ['C']):
            cap=FullCapture(arms[k])
            try:r=arms[k]['stack'](row['path'],parked=row.get('parked',False))
            finally:cap.close()
            results[k]=r;calls[k]=cap.calls;faint[k]=cap.faint_calls
        accepted=json.loads((I/'candidate208'/(p+'.json')).read_text());r=results['C'];assert clean(r['items'])==accepted['items'];assert clean(r.get('removed'))==accepted['removed']
        saved=json.loads(Path(row['evidence']).read_text());saved_core={k:v for k,v in saved.items() if k not in ('page','group','reference')};current={k:v for k,v in r.items() if k not in ('items','image_size','original')}
        if row.get('parked'):assert current.pop('counts')=={}
        assert sanitize(current)==sanitize(saved_core),p+' nonclock'
        cm,cc=masks(arms['C'],r['items'],gray.shape);assert cm==accepted['masks'] and cc==accepted['coverage_sha256']
        if 'B' in results:
            assert sanitize(results['B'])==sanitize(r);assert core(calls['B'])==core(calls['C']),p+' B5';assert core(faint['B'])==core(faint['C']),p+' M35'
        for call in calls['C']:assert call['counts'].get('atlas_builds',0)==int(call['result']['atlas_glyphs']>0)
        dump(O/'qualified_calls'/(p+'.json'),dict(B5=calls,M35=faint));dump(O/'candidate208'/(p+'.json'),dict(items=r['items'],removed=r.get('removed'),masks=cm,coverage_sha256=cc))
        records.append(dict(page=p,roles=row['roles'],B5_calls=[dict(caller=q['caller'],pool_sha256=hashlib.sha256(json.dumps(q['pool'],sort_keys=True).encode()).hexdigest(),requested_regions=q['requested_regions'],counts=q['counts'],atlas_glyphs=q['result']['atlas_glyphs'],anchors=q['result']['anchors'],suspects=q['result']['suspects']) for q in calls['C']],M35_calls=[dict(caller=q['caller'],pool_size=len(q['pool']),counts=q['counts'],suppress_indices=q['result']['suppress_indices']) for q in faint['C']],fresh_baseline=p in c['cohort_pages'],all_nonclock_decisions_equal=True,actual_masks_equal=True,coverage_equal=True,items=len(r['items']),descriptive_timing=r['timing']))
        dump(receipt,dict(records=records,candidate_source=sources(ROOT),baseline_source=sources(base),accepted_runtime='603fbf1076019a2aa15406f94d7415e7a595bf41',cohort_sha256=sha(I/'INK02_COHORT.json'),model_sha256=sha(FL/'onnx/PP-OCRv6_small_det.onnx'),exceptions=[]))
        print(n+1,p,'exact B5',len(calls['C']),'M35',len(faint['C']),flush=True)
    assert all(not any(q['atlas_glyphs'] for q in r['calls']) for r in c['owner22_separate'])
    dump(O/'OWNER22_APPLICABILITY.json',dict(pages=c['owner22_separate'],changed_atlas_consumers=0,source=sources(ROOT),reason='saved accepted-H owner22 observations contain no active atlas; no factory/matcher reached, unchanged dependencies; separate denominator preserved'))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);args=p.parse_args();qualify(args.baseline)

"""Native per-removal M35 audit on the pinned development population only."""
import os
os.environ.update({k:'1' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')})
import argparse,copy,hashlib,inspect,json,sys
from collections import defaultdict
from pathlib import Path
import cv2,numpy as np
from .r8_ink02 import ROOT,FL,clean,dump,sha,sanitize,sources
from ..shared import ink_faintness as faint,ink_ownership as own,detector as dm
from ..shared.geometry import roi
from ..shared.contracts import bbox
from ..shared.geometry_bands import crop_mask
from ..stack import pipeline as sp
O=ROOT/'.astra/fast_lines/out/round8/R8-INK-02-i2'
I=ROOT/'.astra/fast_lines/out/round8/R8-INK-02-i1'

def identity(q,shape):
    a,b,c,d=roi(bbox(q),shape);m=crop_mask((d-b,c-a),q,(a,b))
    return dict(roi=[a,b,c,d],mask_sha256=hashlib.sha256(m.tobytes()).hexdigest(),mask_pixels=int(m.sum()),polygon_sha256=hashlib.sha256(json.dumps(clean(q['polygon']),sort_keys=True).encode()).hexdigest())
def ikey(q,shape):return json.dumps(identity(q,shape),sort_keys=True)
def freeze():
    assert not (O/'M35_REMOVALS_INITIAL.json').exists()
    cohort=json.loads((I/'INK02_COHORT.json').read_text());rows=[];groups=defaultdict(list)
    for row in cohort['pages']:
        path=I/'candidate208'/(row['page']+'.json');d=json.loads(path.read_text());shape=row['image_size'][::-1]
        for index,q in enumerate(d.get('removed') or []):
            if q['removal']!='relative faintness':continue
            geometry=identity(q,shape);key=row['page']+':'+str(index)+':'+json.dumps(geometry,sort_keys=True)
            stable='M35-'+hashlib.sha256(key.encode()).hexdigest()[:16]
            r=dict(id=stable,page=row['page'],input_sha256=row['sha256'],path=row['path'],image_size=row['image_size'],removal_index=index,item=q,geometry=geometry,accepted_evidence=str(path),accepted_evidence_sha256=sha(path),originating_call='pending current-source capture; no interpretation before binding')
            rows.append(r);groups[row['page']+':'+json.dumps({k:v for k,v in geometry.items() if k!='polygon_sha256'},sort_keys=True)].append(stable)
    assert len(rows)==153 and len({r['page'] for r in rows})==34
    data=dict(head='901cb400e97971585ea06c59dfa8c0354351e21a',accepted_runtime='603fbf1076019a2aa15406f94d7415e7a595bf41',denominator_pages=208,audit_pages=34,removal_records=153,cohort_sha256=sha(I/'INK02_COHORT.json'),source=sources(ROOT),records=rows,equal_mask_groups=[g for g in groups.values() if len(g)>1],multiplicity='all final removal records retained, including equal masks; observations are not additional removals')
    dump(O/'M35_REMOVALS_INITIAL.json',data);print('frozen',len(rows),'equal mask groups',data['equal_mask_groups'],flush=True)

def capture():
    frozen=json.loads((O/'M35_REMOVALS_INITIAL.json').read_text());assert sources(ROOT)==frozen['source']
    dm.MODEL=FL/'onnx/PP-OCRv6_small_det.onnx';stack=sp.Stack(image_threads=0)
    cohort=json.loads((I/'INK02_COHORT.json').read_text());pages={r['page']:r for r in cohort['pages']};records=[];callers=[]
    for page in sorted({r['page'] for r in frozen['records']}):
        row=pages[page];assert sha(row['path'])==row['sha256'];assert not (FL.parent/'METER_STOP').exists()
        active=None;calls=[];b5=[];component_calls=[];original=sp.relative_faintness
        def relative(gray,items,**kw):
            nonlocal active
            gray.flags.writeable=False;caller=sys._getframe(1)
            active=dict(id=f'{page}:M35:{len(calls)}',caller=caller.f_code.co_name,caller_line=caller.f_lineno,pool=clean(items),selected_indices=clean(sorted(kw['selected_indices'])) if kw.get('selected_indices') is not None else None,supplied_height=kw.get('height'),image_sha256=row['sha256'],image_frame='original native uint8, scale1, no exclusions filled',component_observations=[])
            try:r=original(gray,items,**dict(kw,detail=True));active['result']=clean(r);calls.append(active)
            finally:active=None
            if not kw.get('detail',False) and 'calibration' in r:r=dict(r,calibration=[dict(line=q['line'],bbox=q['bbox']) for q in r['calibration']])
            return r
        def profile(frame,event,arg):
            if event!='return':return
            name=frame.f_code.co_name;file=Path(frame.f_code.co_filename).name;v=frame.f_locals
            if file=='ink_faintness.py' and name=='components' and active is not None:
                q=clean(v['item']);ident=identity(q,tuple(row['image_size'][::-1]));index=len(active['component_observations'])
                name=f'{page}.call{len(calls)}.component{index:03}.npz';dest=O/'fast_native'/name;dest.parent.mkdir(exist_ok=True)
                np.savez_compressed(dest,origin=[v['a'],v['b']],ink=v['ink'],mask=v['mask'])
                active['component_observations'].append(dict(item=q,geometry=ident,height=v['height'],route=v['route'],components=clean(arg),paper_range=[float(v['paper'].min()),float(v['paper'].max())],paper_sha256=hashlib.sha256(v['paper'].tobytes()).hexdigest(),ink_sha256=hashlib.sha256(v['ink'].tobytes()).hexdigest(),threshold=v['threshold'],noise_DN=v['noise'],origin=[v['a'],v['b']],native_support=str(dest.relative_to(O)),input_raw_sha256=hashlib.sha256(v['raw'].tobytes()).hexdigest()))
            elif file=='ink_faintness.py' and name=='analyze' and active is not None:
                active['height']=arg['height'];active['scout_order']=v.get('ordered',[]);active['sampled_indices']=v.get('ids',[]);active['samples']=[dict(line=i,item=clean(q),same_pool_object=q is v['items'][i],geometry=identity(q,tuple(row['image_size'][::-1]))) for i,q in v.get('samples',[])]
            elif file=='ink_ownership.py' and name=='analyze':
                caller=frame.f_back
                b5.append(dict(id=f'{page}:B5:{len(b5)}',caller=Path(caller.f_code.co_filename).name+':'+caller.f_code.co_name+':'+str(caller.f_lineno),pool=clean(v['items']),requested_regions=clean(v['requested']),explicit_regions=v['regions'] is not None,route=v['route'],result=clean(arg),index_space='requested regions',coordinate_frame='original native full page'))
        sp.relative_faintness=relative;sys.setprofile(profile)
        try:result=stack(row['path'],parked=row.get('parked',False))
        finally:sys.setprofile(None);sp.relative_faintness=original
        accepted=json.loads((I/'candidate208'/(page+'.json')).read_text());assert clean(result['items'])==accepted['items'];assert clean(result['removed'])==accepted['removed']
        matched=[];available=[r for r in frozen['records'] if r['page']==page];used=set()
        for call in calls:
            for index in call['result']['suppress_indices']:
                q=call['pool'][index];key=ikey(q,tuple(row['image_size'][::-1]));choices=[r for r in available if r['id'] not in used and ikey(r['item'],tuple(row['image_size'][::-1]))==key and r['item'].get('source_ids')==q.get('source_ids')]
                assert choices,(page,call['id'],index);r=dict(choices[0]);used.add(r['id']);r.update(originating_call=call['id'],originating_stage='post smooth_envelopes shapes' if len(matched)==0 and call is calls[0] else ('changed post split/reconcile footprints' if call['selected_indices'] is not None else 'post smooth_envelopes shapes'),pool_index=index,pool_size=len(call['pool']),selected_indices=call['selected_indices'],height=call['height'],actual_item=q,call_evidence=f'calls/{page}.json');matched.append(r)
        assert used=={r['id'] for r in available},(page,len(used),len(available))
        dump(O/'calls'/(page+'.json'),dict(page=page,input=row,calls=calls,live_B5=b5,final_items=clean(result['items']),removed=clean(result['removed']),actual_call_count=len(b5)))
        records.extend(matched);callers.extend([dict(page=page,**{k:c[k] for k in ['id','caller','requested_regions','route','index_space','coordinate_frame']},pool_sha256=hashlib.sha256(json.dumps(c['pool'],sort_keys=True).encode()).hexdigest(),atlas_glyphs=c['result']['atlas_glyphs']) for c in b5]);dump(O/'CAPTURE_PROGRESS.json',dict(pages_completed=sorted({r['page'] for r in records}),records=len(records),source=sources(ROOT)))
        print('capture',page,len(matched),'calls',len(calls),len(b5),flush=True)
    assert len(records)==153;frozen['records']=sorted(records,key=lambda r:(r['page'],r['removal_index']));dump(O/'M35_REMOVALS.json',frozen);dump(O/'LIVE_CALLERS34.json',callers)

def observed(gray,q,height,route):
    evidence={}
    def profile(frame,event,arg):
        if event=='return' and frame.f_code.co_name=='components' and Path(frame.f_code.co_filename).name=='ink_faintness.py':
            v=frame.f_locals;evidence.update(origin=[v['a'],v['b']],ink=v['ink'].copy(),mask=v['mask'].copy(),paper_sha256=hashlib.sha256(v['paper'].tobytes()).hexdigest(),paper_range=[float(v['paper'].min()),float(v['paper'].max())],threshold=v['threshold'],noise_DN=v['noise'],input_raw_sha256=hashlib.sha256(v['raw'].tobytes()).hexdigest())
    sys.setprofile(profile)
    try:r=faint.components(gray,q,height,route=route)
    finally:sys.setprofile(None)
    return r,evidence

def strip(gray,q,h):
    a,b,c,d=roi(bbox(q),gray.shape);pad=round(h*1.8);a=max(0,a-pad);b=max(0,b-pad);c=min(gray.shape[1],c+pad);d=min(gray.shape[0],d+pad);raw=gray[b:d,a:c];m=crop_mask(raw.shape,q,(a,b));return [a,b,c,d],raw,m

def diagnostic():
    frozen=json.loads((O/'M35_REMOVALS.json').read_text());allcases=[];summary=[]
    for page in sorted({r['page'] for r in frozen['records']}):
        assert not (FL.parent/'METER_STOP').exists();records=[r for r in frozen['records'] if r['page']==page];data=json.loads((O/'calls'/(page+'.json')).read_text());row=data['input'];assert sha(row['path'])==row['sha256'];gray=cv2.imread(row['path'],0);gray.flags.writeable=False
        final_coverage=np.zeros(gray.shape,np.uint16)
        for q in data['final_items']:
            a,b,c,d=roi(bbox(q),gray.shape);final_coverage[b:d,a:c]+=crop_mask((d-b,c-a),q,(a,b)).astype(np.uint16)
        for call in data['calls']:
            selected=[r for r in records if r['originating_call']==call['id']]
            if not selected:continue
            # One diagnostic census/atlas for all this invocation's removed ROIs.
            diagnostic=own.analyze(gray,call['pool'],regions=[bbox(r['actual_item']) for r in selected],detail=True)
            samples=[]
            for sample in call['samples']:
                cs,obs=observed(gray,sample['item'],call['height'],'slow');samples.append(dict(sample=sample,components=cs,observation={k:v for k,v in obs.items() if k not in ['ink','mask']}))
            slow_same_strips_ref=faint.reference(samples)
            call['slow_same_strips']=samples;call['slow_same_strips_reference']=slow_same_strips_ref;call['offline_B5']=clean(diagnostic)
            per=[]
            for j,r in enumerate(selected):
                q=r['actual_item'];index=r['pool_index'];fast=next(z for z in call['result']['regions'] if z['line']==index);slow_cs,slow_obs=observed(gray,q,call['height'],'slow');slow_native=[dict(components=copy.deepcopy(slow_cs))];faint.classify(slow_native,call['result']['reference']);slow_new_ref=[dict(components=copy.deepcopy(slow_cs))];faint.classify(slow_new_ref,slow_same_strips_ref)
                fast_obs=next(z for z in call['component_observations'] if z['geometry']==identity(q,gray.shape));native=np.load(O/fast_obs['native_support']);assert list(native['origin'])==slow_obs['origin'];inkdiff=int(np.count_nonzero(native['ink']!=slow_obs['ink']));maskdiff=int(np.count_nonzero(native['mask']!=slow_obs['mask']))
                bounds,raw,m=strip(gray,q,call['height']);a,b,c,d=bounds;covered=final_coverage[b:d,a:c]>0;missing=(m>0)&~covered
                live=[]
                for b5 in data['live_B5']:
                    for k,box in enumerate(b5['requested_regions']):
                        if list(roi(box,gray.shape))==list(roi(bbox(q),gray.shape)):
                            live.append(dict(call_id=b5['id'],caller=b5['caller'],requested_index=k,result=b5['result']['regions'][k],same_native_roi=True,polygon_mask_binding='B5 samples rectangle; exact M35 polygon/mask not consumed'))
                record=dict(r,fast_region=fast,fast_observation=fast_obs,slow_components=slow_cs,slow_observation={k:v for k,v in slow_obs.items() if k not in ['ink','mask']},same_reference_slow=slow_native[0],slow_strips_reference_region=slow_new_ref[0],ink_different_pixels=inkdiff,mask_different_pixels=maskdiff,components_fields_exact=clean(slow_cs)==[{k:v for k,v in z.items() if k in slow_cs[0]} for z in fast['components']] if slow_cs else not fast['components'],live_B5=live,offline_B5=clean(diagnostic['regions'][j]),offline_B5_requested_index=j,offline_B5_call=call['id']+':diagnostic',offline_B5_scope='one offline analyze on responsible current item pool, requested removed bbox ROIs; not consumed by runtime',coverage=dict(mask_pixels=int(m.sum()),mask_pixels_still_in_final=int(((m>0)&covered).sum()),missing_mask_pixels=int(missing.sum()),raw_lt200_missing=int(((raw<200)&missing).sum()),raw_lt200_retained=int(((raw<200)&(m>0)&covered).sum()),audit_threshold='raw<200 diagnostic only, not runtime or certified text'),context_roi=bounds)
                per.append(record);allcases.append(record)
            call['audit_records']=per
        dump(O/'audit'/(page+'.json'),data);summary.append(dict(page=page,records=len(records),conflicts=[r['id'] for r in allcases if r['page']==page and r['offline_B5']['ownership']=='front'],observation_disagreements=[r['id'] for r in allcases if r['page']==page and (r['ink_different_pixels'] or r['same_reference_slow']['drop']!=r['fast_region']['drop'])]));dump(O/'AUDIT_PROGRESS.json',summary);print('diagnostic',page,len(records),summary[-1],flush=True)
    dump(O/'OBSERVATION_COMPARISON.json',allcases)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','capture','diagnostic']);a=p.parse_args();globals()[a.action]()

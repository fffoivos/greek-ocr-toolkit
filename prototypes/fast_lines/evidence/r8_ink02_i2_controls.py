"""Actual pre-removal control pools and offline full-census slow observations."""
import copy,json,sys
from pathlib import Path
import cv2,numpy as np
from .r8_ink02_i2 import O,I,FL,ROOT,dump,sha,clean,sanitize,sources,sp,dm,faint,own,bbox,roi,crop_mask

def controls():
 c=json.loads((I/'INK02_COHORT.json').read_text());rows=[r for r in c['pages'] if r['roles'] and any(k in r['page'] for k in ['8686', '1be6','3229200','4959','93f8'])]
 # Exact inventory resolution, not shortened IDs as authority.
 rows=[r for r in rows if ('1be6' not in r['page'] or r['page'].endswith('p000215')) and ('8686' not in r['page'] or r['page'].endswith(('p00005','p00007','p00026'))) and ('3229' not in r['page'] or r['page'].endswith('p00002')) and ('4959' not in r['page'] or r['page'].endswith('p00005')) and ('93f8' not in r['page'] or r['page'].endswith('p00001'))]
 assert len(rows)==7,[(r['page'],r['roles']) for r in rows]
 dm.MODEL=FL/'onnx/PP-OCRv6_small_det.onnx';stack=sp.Stack(image_threads=0);out=[]
 for row in rows:
  assert sha(row['path'])==row['sha256'];calls=[];b5=[];active=None;original=sp.relative_faintness
  def relative(gray,items,**kw):
   nonlocal active
   gray.flags.writeable=False;caller=sys._getframe(1);active=dict(id=f"{row['page']}:M35:{len(calls)}",caller=caller.f_code.co_name,caller_line=caller.f_lineno,pool=clean(items),selected_indices=clean(sorted(kw['selected_indices'])) if kw.get('selected_indices') is not None else None,supplied_height=kw.get('height'))
   try:r=original(gray,items,**dict(kw,detail=True));active['result']=clean(r);calls.append(active)
   finally:active=None
   if not kw.get('detail',False) and 'calibration' in r:r=dict(r,calibration=[dict(line=q['line'],bbox=q['bbox']) for q in r['calibration']])
   return r
  def profile(frame,event,arg):
   if event!='return':return
   v=frame.f_locals;file=Path(frame.f_code.co_filename).name
   if file=='ink_faintness.py' and frame.f_code.co_name=='analyze' and active is not None:
    active.update(height=arg['height'],scout_order=v.get('ordered',[]),sampled_indices=v.get('ids',[]),samples=[dict(line=i,item=clean(q),same_pool_object=q is v['items'][i]) for i,q in v.get('samples',[])])
   elif file=='ink_ownership.py' and frame.f_code.co_name=='analyze':
    f=frame.f_back;b5.append(dict(id=f"{row['page']}:B5:{len(b5)}",caller=Path(f.f_code.co_filename).name+':'+f.f_code.co_name+':'+str(f.f_lineno),pool=clean(v['items']),requested_regions=clean(v['requested']),route=v['route'],result=clean(arg)))
  sp.relative_faintness=relative;sys.setprofile(profile)
  try:r=stack(row['path'],parked=row.get('parked',False))
  finally:sys.setprofile(None);sp.relative_faintness=original
  accepted=json.loads((I/'candidate208'/(row['page']+'.json')).read_text());assert clean(r['items'])==accepted['items'];assert clean(r['removed'])==accepted['removed']
  data=dict(page=row['page'],input=row,calls=calls,live_B5=b5,final_items=clean(r['items']),removed=clean(r['removed']),source=sources(ROOT));dump(O/'controls_calls'/(row['page']+'.json'),data);out.append(dict(page=row['page'],calls=len(calls),B5_calls=len(b5)));print('control capture',out[-1],flush=True)
 dump(O/'CONTROL_CALLS_INDEX.json',out)

def slow_whole():
 # Declared selection before observing full-census classifications. Include the
 # conflict, both back decisions, suspected symmetric initials/table, blank,
 # changed-footprint gap, stamp and retained faint/current-front controls.
 plan=dict(removal_panel_controls=[7,49,64,72,86,90,109,151],retained_control_prefixes=['1be6','31f40','8686'],scope='one render slow on responsible actual complete pool; all-row reference differs from eight-strip reference; offline only')
 dump(O/'SLOW_WHOLE_PLAN.json',plan);cases=json.loads((O/'OBSERVATION_COMPARISON.json').read_text());selected={cases[n-1]['originating_call'] for n in plan['removal_panel_controls']};todo=[]
 files=list((O/'audit').glob('*.json'))+list((O/'controls_calls').glob('*.json'))
 seen=set()
 for path in files:
  data=json.loads(path.read_text());p=data['page']
  for call in data['calls']:
   retained=any(k in p for k in plan['retained_control_prefixes']) and call is data['calls'][0]
   if call['id'] not in selected and not retained:continue
   if call['id'] in seen:continue
   seen.add(call['id']);todo.append((path,data,call))
 out=[]
 for path,data,call in todo:
  assert not (FL.parent/'METER_STOP').exists();gray=cv2.imread(data['input']['path'],0);gray.flags.writeable=False;assert sha(data['input']['path'])==data['input']['sha256']
  slow=faint.render(gray,call['pool'],height=call['height'],route='slow');fast=call['result'];by={r['line']:r for r in slow['regions']};comp=[]
  for r in fast['regions']:comp.append(dict(pool_index=r['line'],fast=r,slow=by[r['line']],same_drop=r['drop']==by[r['line']]['drop']))
  freshB5=own.analyze(gray,call['pool'],detail=True) if any(k in data['page'] for k in ['1be6','31f40','8686']) else None
  dest=O/'slow_whole'/(call['id'].replace(':','.')+'.json');dump(dest,dict(page=data['page'],input=data['input'],call_id=call['id'],pool=call['pool'],selected_indices=call['selected_indices'],height=call['height'],fast_sampled_indices=call['sampled_indices'],fast_reference=fast['reference'],slow=slow,comparison=comp,offline_B5=freshB5,scope='actual full current pool, original native uint8; slow all-row versus fast eight actual polygon strips; not a source ground truth'))
  summary=dict(page=data['page'],call_id=call['id'],pool_size=len(call['pool']),fast_reference=fast['reference'],slow_reference=slow['reference'],compared_fast_nominees=len(comp),changed_drops=[q['pool_index'] for q in comp if not q['same_drop']],slow_suppress_indices=slow['suppress_indices'],file=str(dest.relative_to(O)));out.append(summary);dump(O/'SLOW_WHOLE_COMPARISON.json',out);print('slow whole',data['page'],call['id'],len(comp),summary['changed_drops'],flush=True)
if __name__=='__main__':globals()[sys.argv[1]]()

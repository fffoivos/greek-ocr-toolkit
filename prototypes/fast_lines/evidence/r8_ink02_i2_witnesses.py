"""Native qualified glyph pairs and retained-control support; offline only."""
import json,hashlib
from pathlib import Path
import cv2,numpy as np
from .r8_ink02_i2 import O,I,ROOT,FL,dump,sha,clean,own,faint,bbox,roi,crop_mask,strip
from .r8_ink02_i2_panels import stack,label_image,bar,enhance

def run():
 cases=json.loads((O/'OBSERVATION_COMPARISON.json').read_text());index=[]
 for r in cases:
  if r['offline_B5']['ownership'] not in ['front','back']:continue
  data=json.loads((O/'audit'/(r['page']+'.json')).read_text());gray=cv2.imread(data['input']['path'],0);images=[];pairs=[]
  for n,m in enumerate(r['offline_B5']['witnesses']):
   orientation='reflected' if m['margin']>0 else 'direct';ex=r['offline_atlas']['exemplars'][m[orientation+'_id']];assert list(ex['bbox'])==m['exemplar']
   a,b,c,d=m['bbox'];x,y,z,w=ex['bbox'];q=gray[b:d,a:c];e=gray[y:w,x:z]
   images.extend([bar(900,f"{r['id']} vote{n} {orientation} score={m[orientation]:.6f} margin={m['margin']:.6f} scored_id={m[orientation+'_id']}"),label_image(q,'ORIGINAL query native 4x',4),label_image(e,'ORIGINAL actual scored exemplar native 4x',4)])
   if orientation=='reflected':images.append(label_image(q[:,::-1],'REFLECTED query display aid only, native pixels unchanged',4))
   pairs.append(dict(match=m,exemplar=ex))
  path=O/'qualified_witnesses'/f"{r['panel_index']:03}.png";path.parent.mkdir(exist_ok=True);cv2.imwrite(str(path),stack(images));index.append(dict(id=r['id'],panel_index=r['panel_index'],file=str(path.relative_to(O)),pairs=pairs,scope='all qualified votes, same one-build diagnostic atlas; ordinary/reflected shape, not leaf certification'))
 dump(O/'QUALIFIED_WITNESS_INDEX.json',index)
 cohort=json.loads((I/'INK02_COHORT.json').read_text());by={r['page']:r for r in cohort['pages']};controls=[]
 # Whole original native page and exact final crop masks, including duplicate coverage.
 selections=[]
 for key in ['1be6','31f40']:
  page=next(p for p in by if key in p and p.endswith('p000215' if key=='1be6' else 'p00001'))
  path=O/('controls_calls' if key=='1be6' else 'calls')/(page+'.json');data=json.loads(path.read_text());call=data['calls'][0];h=call['height'];scout=call['result']['scout']['regions']
  ids=sorted([i for i,q in enumerate(call['pool']) if i not in call['result']['suppress_indices'] and bbox(q)[2]-bbox(q)[0]>8*h],key=lambda i:scout[i]['core'])[:3]
  selections.extend((page,call,i,call['pool'][i],f'{key} retained faint-front control {j}',None) for j,i in enumerate(ids))
 page=next(p for p in by if '8686' in p and p.endswith('p00005'));data=json.loads((O/'controls_calls'/(page+'.json')).read_text());call=data['calls'][0]
 selections.extend([(page,call,56,call['pool'][56],'ἀποξήρανσίν retained current row',None),(page,call,None,dict(polygon=[[1776,1074],[1779,1074],[1779,1078],[1776,1078]]),'ἐξόδων breathing retained negative control',[1776,1074,1780,1079])])
 for n,(page,call,pool_i,q,label,inclusive) in enumerate(selections):
  row=by[page];assert sha(row['path'])==row['sha256'];gray=cv2.imread(row['path'],0);gray.flags.writeable=False;final=json.loads((I/'candidate208'/(page+'.json')).read_text())['items'];coverage=np.zeros(gray.shape,np.uint16)
  for item in final:
   a,b,c,d=roi(bbox(item),gray.shape);coverage[b:d,a:c]+=crop_mask((d-b,c-a),item,(a,b))
  bounds,raw,m=strip(gray,q,call['height']);a,b,c,d=bounds;cover=coverage[b:d,a:c]>0;display=cv2.cvtColor(raw,cv2.COLOR_GRAY2BGR);display[(m>0)&cover,1]=np.minimum(display[(m>0)&cover,1].astype(np.uint16)+30,255);cv2.drawContours(display,cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0],-1,(0,0,255),1)
  offline=own.analyze(gray,call['pool'],regions=[bbox(q)],height=call['height'],detail=True)
  same=next((r for r in call['result']['regions'] if r['line']==pool_i),None) if pool_i is not None else None
  cs=faint.components(gray,q,call['height'],route='slow');ref=call['result']['reference'];under_ref=[dict(components=cs)]
  if ref:faint.classify(under_ref,ref)
  panels=[bar(max(900,raw.shape[1]),f'{n:02} {page} {label} | ORIGINAL native surrounding rows'),label_image(raw,'ORIGINAL native, 1x',1),label_image(enhance(raw),'ENHANCED display only',1),label_image(display,'Red control mask; green tint final retained support, exact crop masks',1)]
  if label.startswith('ἀποξήρανσίν'):
   panels.append(label_image(gray[1555:1702,1644:1939],'ORIGINAL word neighbourhood native 2x; display window includes adjacent rows',2))
  dest=O/'retained_controls'/f'{n:02}.png';dest.parent.mkdir(exist_ok=True);cv2.imwrite(str(dest),stack(panels))
  record=dict(page=page,label=label,input_sha256=row['sha256'],call_id=call['id'],pool_index=pool_i,pool_size=len(call['pool']),supplied_height=call['height'],item=q,control_rectangle=pool_i is None,context_roi=bounds,fast_nominee=same,fast_reference=ref,slow_same_reference=under_ref[0],offline_B5=offline,mask_pixels=int(m.sum()),selected_pixels_retained=int(((m>0)&cover).sum()),selected_raw_lt200_retained=int(((raw<200)&(m>0)&cover).sum()),selected_raw_lt200_missing=int(((raw<200)&(m>0)&~cover).sum()),file=str(dest.relative_to(O)),control_policy='owner/checked retained-front negative control, not newly source-certified by B5; window includes paper and incidental support')
  if inclusive:
   x,y,z,w=inclusive;record['inclusive_native_pixel_rectangle']=inclusive;record['rectangle_pixels']=int((w-y)*(z-x));record['rectangle_retained_pixels']=int((coverage[y:w,x:z]>0).sum());record['strip_membership']=[]
   for i,item in enumerate(final):
    aa,bb,cc,dd=roi(bbox(item),gray.shape)
    if aa>z-1 or cc<=x or bb>w-1 or dd<=y:continue
    mask=crop_mask((dd-bb,cc-aa),item,(aa,bb));win=mask[max(y-bb,0):w-bb,max(x-aa,0):z-aa];record['strip_membership'].append(dict(strip_index=i,pixels=int(win.sum())))
   assert record['rectangle_retained_pixels']==20
   assert next(r['pixels'] for r in record['strip_membership'] if r['strip_index']==33)==20
   record['strip_numbering']='checker and frozen item list zero-based indices, not source IDs or one-based crop labels'
   assert all(r['pixels']==0 for r in record['strip_membership'] if r['strip_index']==35)
  controls.append(record)
 dump(O/'RETAINED_CONTROLS.json',controls)
if __name__=='__main__':run()

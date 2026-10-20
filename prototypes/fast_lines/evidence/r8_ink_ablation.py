"""Offline M20 removal counterfactual. No replacement calibration or runtime import."""
import json,sys
from pathlib import Path
import cv2,numpy as np
from ..shared import geometry_feature_correct as fc,geometry_context as gc,detector
from ..stack import Stack
from ..shared.timing import dump
from .r8_ink_support import BASE,OUT
FL=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines')

def union(items,shape):
 mask=np.zeros(shape,np.uint8)
 for q in items:cv2.fillPoly(mask,[np.rint(q['polygon']).astype(np.int32)],1)
 return mask>0

def run():
 rows=json.loads((BASE.parent/'R8-01b/inputs-208.json').read_text())['pages'];pilot=json.loads(Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-model/.astra/fast_lines/out/round8/R8-01/inputs.json').read_text())['pages'];names={r['page'] for r in pilot}
 out=OUT/'retention-ablation';out.mkdir(parents=True,exist_ok=False);detector.MODEL=FL/'onnx/PP-OCRv6_small_det.onnx';stack=Stack();orig=fc.retention_ink;records=[];calls=[]
 def absent(gray,item,h):
  p=orig(gray,item,h);calls.append(dict(bounds=p[1],height=h,native_pixels=int(p[3].sum())));z=np.zeros_like(p[3]);z.flags.writeable=False;return (*p[:3],z)
 fc.retention_ink=absent;gc.retention_ink=absent
 try:
  for row in rows:
   if row['page'] not in names:continue
   calls.clear();p=row['page'];g=cv2.imread(row['path'],0);r=stack(row['path'],parked=row.get('parked',False));base=json.loads((BASE/'runtime'/f'{p}.json').read_text())['items'];e=json.loads((BASE/'runtime'/f'{p}.evidence.json').read_text());old=union(base,g.shape);new=union(r['items'],g.shape);lost=old&~new&(g<200);added=new&~old&(g<200)
   rec=dict(page=p,equal=r['items']==base,lost_pixels=int(lost.sum()),new_pixels=int(added.sum()),retention_calls=list(calls),old_removed=e.get('removed',[]),new_removed=r.get('removed',[]),old_counts=e.get('counts'),new_counts=r.get('counts'),crops=[])
   if not rec['equal']:
    n,lab,stats,_=cv2.connectedComponentsWithStats(cv2.dilate(lost.astype(np.uint8),np.ones((5,5),np.uint8)),8)
    for j,(x,y,w,h,area) in enumerate(stats[1:],1):
     if not np.any(lost[y:y+h,x:x+w]):continue
     a,b,c,d=max(0,x-30),max(0,y-30),min(g.shape[1],x+w+30),min(g.shape[0],y+h+30)
     raw=cv2.cvtColor(g[b:d,a:c],cv2.COLOR_GRAY2BGR);view=raw.copy();view[lost[b:d,a:c]]=(0,0,255);view[added[b:d,a:c]]=(0,180,0)
     name=f'{p}.{j}.jpg';cv2.imwrite(str(out/name),np.hstack([raw,view]));rec['crops'].append(dict(image=name,bbox=[a,b,c,d],lost=int(lost[b:d,a:c].sum())))
    dump(out/f'{p}.json',r)
   records.append(rec);print(p,rec['equal'],rec['lost_pixels'],rec['new_pixels'],flush=True)
 finally:fc.retention_ink=orig;gc.retention_ink=orig
 dump(out/'results.json',records)
if __name__=='__main__':run()

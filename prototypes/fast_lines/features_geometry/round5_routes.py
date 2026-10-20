import json,cv2,numpy as np
from pathlib import Path
from prototypes.fast_lines.features_geometry.round5_data import rows,load,DEST
from prototypes.fast_lines.shared.geometry_envelopes import guided
from prototypes.fast_lines.shared.geometry_columns import native_crossings
from prototypes.fast_lines.shared.timing import dump
cv2.setNumThreads(1)
out=DEST/'routes-v5';out.mkdir(exist_ok=True)
for row in rows():
 p=row['page'];dst=out/(p+'.json')
 if dst.exists():raise RuntimeError(dst)
 g,o,pm=load(row);native=json.load(open(DEST/'shapes-v5-slow'/(p+'.json')))
 records={r['line']:r for r in native['lines']};r1=guided(g,pm,o['items'],o['original'],'explicit',5);r2=guided(g,pm,o['items'],o['original'],'heuristic',5)
 rr=[]
 for a in r1['lines']:
  b=next((r for r in r2['lines'] if r['line']==a['line']),None);n=records[a['line']]
  rec=dict(line=a['line'],r1_exact_polygon=a.get('polygon')==n.get('polygon'),r1_exact_contacts=a['contacts']==n['contacts'],r1_ambiguity=a['ambiguous']==n['ambiguous'],r2_ambiguity=None if b is None else b['ambiguous'])
  if b and a.get('polygon') and b.get('polygon'):
   pa=np.array(a['polygon']);pb=np.array(b['polygon']);na=len(pa)//2;nb=len(pb)//2;x=pa[:na,0];rec['r2_boundary_max_h']=float(max(np.max(abs(pa[:na,1]-np.interp(x,pb[:nb,0],pb[:nb,1]))),np.max(abs(pa[na:,1][::-1]-np.interp(x,pb[:nb,0],pb[nb:,1][::-1]))))/native['height'])
  rr.append(rec)
 col=json.load(open(DEST/'columns-v4'/(p+'.json')));cc=[]
 for k,r in enumerate(col['rules']):
  if 'rule' not in r:continue
  fast=native_crossings(g,r['rule'],col['height'],'explicit');cc.append(dict(rule=k,r1_exact=fast==r['native'],explicit_accept=r['accepted'],r2_accept=r['endpoints']['accepted'] and len(r['intersections'])<3))
 for label,route in [('r1',r1),('r2',r2)]:
  im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
  for r in native['lines']:
   if r.get('polygon'):cv2.polylines(im,[np.rint(r['polygon']).astype(np.int32)],True,(0,150,0),2)
  for r in route['lines']:
   if r.get('polygon'):cv2.polylines(im,[np.rint(r['polygon']).astype(np.int32)],True,(210,80,0) if label=='r1' else (180,0,180),1)
  sc=min(1,1600/im.shape[1]);cv2.imwrite(str(out/(p+'.'+label+'.jpg')),cv2.resize(im,None,fx=sc,fy=sc))
 im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
 for c in cc:
  r=col['rules'][c['rule']];color=(0,150,0) if c['explicit_accept'] else (0,0,210);cv2.polylines(im,[np.rint(r['rule']['path']).astype(np.int32)],False,color,4)
  if c['r2_accept']:cv2.polylines(im,[np.rint(r['rule']['path']).astype(np.int32)],False,(180,0,180),2)
 sc=min(1,1600/im.shape[1]);cv2.imwrite(str(out/(p+'.columns.jpg')),cv2.resize(im,None,fx=sc,fy=sc))
 dump(dst,dict(lines=rr,columns=cc,r1=r1,r2=r2));print(p,len(rr),sum(not r['r1_exact_polygon'] for r in rr),flush=True)

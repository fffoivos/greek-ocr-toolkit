"""Source-bound native ink audit on historical owner supports; no runtime import."""
import json,sys,importlib.util,hashlib
from pathlib import Path
import cv2,numpy as np
from ..shared import ink_ownership as ownership,ink_faintness as faint
from ..shared.ink_photometry import glyphs,match_glyphs,glyph_atlas
from ..shared.contracts import bbox
from ..shared.geometry import height_proxy
from ..shared.timing import dump
from .r8_ink_support import BASE,OUT,capture
ROOT=Path.cwd();FL=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines')
MANIFEST=BASE.parent/'R8-01b/inputs-208.json'
CASES={'an-ef481610a820-p000150':[3],'an-ef481610a820-p000151':[9,10,29,30],'s2-44b5cf9e0d680b361091-p00005':[123],'s2-93f8070059f938bda524-p00001':[1,5,89,117,126,127],'s2-86865c33eef5932c013b-p00026':[9,40],'s2-0ce9d1025b3f23c7119e-p00001':[4,16]}

def run():
 out=OUT/'source-audit';out.mkdir(parents=True,exist_ok=False)
 spec=importlib.util.spec_from_file_location('historical_order',FL/'review_r6/reading_order.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 from ..stack import pipeline as sp
 from ..shared import detector,type_recovery,type_residual_recovery
 detector.MODEL=FL/'onnx/PP-OCRv6_small_det.onnx';stack=sp.Stack();allrecords=[]
 for row in json.loads(MANIFEST.read_text())['pages']:
  p=row['page']
  if p not in CASES:continue
  g=cv2.imread(row['path'],0);calls=[];current=[];oldf=sp.relative_faintness;oldink=sp.ink_run;oldtype=type_recovery.ownership;oldres=type_residual_recovery.ownership
  def ink(gray,items,**kw):
   current.extend(items);r=oldink(gray,items,**kw);calls.append(dict(stage='post-Q8 ink_run',items=items,result=r));return r
  def native(gray,items,**kw):
   r=oldf(gray,items,detail=True,**kw);calls.append(dict(stage='faintness',items=items,result=r));return r
  def typ(gray,items,regions=None,**kw):
   r=oldtype(gray,items,regions,**kw);calls.append(dict(stage='type ownership',items=items,result=r));return r
  sp.ink_run=ink;sp.relative_faintness=native;type_recovery.ownership=typ;type_residual_recovery.ownership=typ
  try:r=stack(row['path'])
  finally:sp.ink_run=oldink;sp.relative_faintness=oldf;type_recovery.ownership=oldtype;type_residual_recovery.ownership=oldres
  assert r['items']==json.loads((BASE/'runtime'/f'{p}.json').read_text())['items'],p
  old=json.loads((ROOT/'.astra/fast_lines/out/round7/T3_ink/before'/f'{p}.json').read_text())['items'];ordered=mod.reading_order(old);qs=[ordered[i-1] for i in CASES[p]]
  h=height_proxy(current,g.shape[::-1]);dense=ownership.analyze(g,current,[bbox(q) for q in qs],detail=True,route='dense',height=h)
  early=faint.analyze(g,current,detail=True,require_reference=True);late=faint.analyze(g,r['items'],detail=True,require_reference=True);slow=faint.render(g,r['items'],height=late['height'],route='slow')
  atlas=[]
  for i in dense['anchors']:
   for gl in glyphs(g,bbox(current[i]),h,limit=256):atlas.append(dict(gl,line=i))
  atlas=glyph_atlas(atlas)
  records=[]
  for idx,(num,q) in enumerate(zip(CASES[p],qs)):
   matches=match_glyphs(glyphs(g,bbox(q),h,limit=256),atlas) if atlas else []
   force=dict(front=sum(m['direct']>=.80 and m['margin']<=-.08 for m in matches),back=sum(m['reflected']>=.80 and m['margin']>=.08 for m in matches),matches=matches)
   regions=[]
   for route in ('slow','localized'):
    cs,l=capture(faint.components,g,q,late['height'],route=route)
    z=dict(components=cs);faint.classify([z],late['reference']);regions.append(dict(route=route,**z))
    a,b,c,d=l['a'],l['b'],l['c'],l['d'];raw=cv2.cvtColor(g[b:d,a:c],cv2.COLOR_GRAY2BGR);view=raw.copy()
    for co in cs:
     x,y,x1,y1=np.rint(np.array(co['bbox'])-[a,b,a,b]).astype(int);cv2.rectangle(view,(x,y),(x1,y1),(0,0,255) if co['faint'] else (0,180,0),1)
    cv2.polylines(view,[np.rint(np.asarray(q['polygon'])-[a,b]).astype(np.int32)],True,(255,0,0),1)
    cv2.imwrite(str(out/f'{p}.{num}.{route}.jpg'),np.hstack([raw,view]))
    np.savez_compressed(out/f'{p}.{num}.{route}.npz',origin=[a,b],support=l['ink'],labels=l['lab'],paper=l['paper'],core_contrast=l['core_contrast'],polygon=q['polygon'])
   records.append(dict(number=num,polygon=q['polygon'],source_ids=q.get('source_ids'),dense_source=dense['regions'][idx],forced_glyphs=force,routes=regions))
  rec=dict(page=p,input=row,baseline_source_sha256=hashlib.sha256((BASE/'runtime/source.json').read_bytes()).hexdigest(),historical_source='R7 T3 before (R6); review_r6/reading_order.py',actual_calls=calls,early_reference=early['reference'],current_reference=late['reference'],dense_reference=slow['reference'],dense_suppress=slow['suppress_indices'],sparse_suppress=late['suppress_indices'],records=records,final_removed=r['removed'])
  dump(out/f'{p}.json',rec);allrecords.append(dict(page=p,cases=len(qs),early_boundary=early['reference']['boundary'],late_boundary=late['reference']['boundary'],dense_boundary=slow['reference']['boundary'],sources=[dict(number=z['number'],ownership=z['dense_source']['ownership'],votes=z['forced_glyphs']['front'],back=z['forced_glyphs']['back'],drop=z['routes'][1]['drop']) for z in records]));print(allrecords[-1],flush=True)
 dump(out/'summary.json',allrecords)
if __name__=='__main__':run()

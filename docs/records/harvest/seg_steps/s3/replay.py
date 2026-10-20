"""Offline S3 replay; reuse S1 input, context, timeout and scoring workflow."""
from pathlib import Path
import importlib.util,sys,json,signal,time,hashlib
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('s2_replay',D.parent/'s2/replay.py');s2=importlib.util.module_from_spec(spec);spec.loader.exec_module(s2)
s1=s2.s1
read,dump,write,sha=s1.read,s1.dump,s1.write,s1.sha
NativeSegmenter=s1.NativeSegmenter
import numpy as np
from greekocr.harvest.predictor_path import predictor_binary
from collections import Counter

def worker(old=False):
 versions=json.loads((D/'baseline/docs/harvest/line_pipeline/tool_versions.json' if old else R/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 w=NativeSegmenter(versions,predictor_binary())
 if old:
  spec=importlib.util.spec_from_file_location('s2_crop_tools',D/'baseline/greekocr/harvest/filtering_assets/crop-tools.py');w.crop_tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(w.crop_tools)
  original=w.crop_tools.features_from_observation
  w.crop_tools.features_from_observation=lambda **kw:original(**{k:v for k,v in kw.items() if k not in ('base_curve','base_is_straight')})
 return w

def metrics(z):
 e=z['evidence'];b=e['box_evidence'];rf=b.get('row_frame');pred=b.get('prediction')
 return dict(long_side=rf['length'] if rf else None,short_side=rf['height'] if rf else None,
  ratio=(e['characters']+1)/(pred['expected']+1) if pred else None,
  padding=e['padding_evidence'].get('total_padding_line_heights'),verdict=z['verdict'])

def capture(w,store):
 orig=w.crop_tools.line_inventory
 def wrapped(g,lines,components,angle):
  main=next((l for l in lines if l.side=='main'),None)
  store.update(g=g,main=main,components=components,angle=angle)
  return orig(g,lines,components,angle)
 w.crop_tools.line_inventory=wrapped

def curve_info(c):
 g,main=c['g'],c['main'];base=main.base if main else None
 if base is None:return dict(available=False,straight=False)
 lo,hi=main.x0,main.x1
 x=np.arange(lo,hi+1);y=base[lo:hi+1];slope=(y[-1]-y[0])/max(1,hi-lo)
 normal_deviation=np.abs(y-(y[0]+slope*(x-lo)))/np.hypot(1,slope)
 return dict(available=True,detector_degree=g.band.degree,straight=g.band.curve_is_straight if g.band.curve_is_straight is not None else g.band.degree!=2,
  support=[lo,hi],max_chord_deviation_px=float(normal_deviation.max()),
  baseline_range_px=float(np.ptp(y)))

def preflight():
 rows=s1.inputs();assert rows==read(D.parent/'s2/inputs.jsonl');write(D/'inputs.jsonl',rows)
 saved=read(D.parent/'s2/replay.jsonl');assert len(saved)==len(rows)==1288
 old=worker(True);new=worker();c={};capture(old,c);checks=Counter();records=[]
 signal.signal(signal.SIGALRM,s1.timeout);start=time.monotonic()
 try:
  for i,(inp,previous) in enumerate(zip(rows,saved),1):
   s2.context(old,inp);signal.alarm(120);z=old(inp['row']);signal.alarm(0)
   assert s2.norm(z)==s2.norm(previous['after']),(inp['line_id'],'S2 drift')
   info=curve_info(c);g=c['g'];yy,xx=np.nonzero(g.ink)
   args=dict(width=g.width,height=g.height,components=c['components'],ink_box=[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1] if len(xx) else None,ink_pixels=int(g.ink.sum()),xheight=float(g.band.xh),xheight_source=g.band.xh_source,support_count=g.band.n_support,chars=s1.character_count(inp['row']['raw_text']),labels=g.labels,angle_deg=c['angle'])
   if info['straight']:
    a=old.crop_tools.features_from_observation(**args)
    b=new.crop_tools.features_from_observation(**args,base_curve=c['main'].base,base_is_straight=info['straight'])
    assert a==b,(inp['line_id'],'straight feature drift')
    checks['straight_feature_identity']+=1
   info.update(cohort=inp['cohort'],line_id=inp['line_id'])
   records.append(dict(previous,curve=info))
   if i%100==0:print('identity preflight',i,flush=True)
  write(D/'preflight.jsonl',records);dump(D/'preflight_receipt.json',dict(checks=checks,rows=len(rows),elapsed_seconds=time.monotonic()-start))
 finally:signal.alarm(0);old.close();new.close()

def run():
 pre=read(D/'preflight.jsonl');assert len(pre)==1288
 w=worker();checks=Counter();curves=[];straight=[];c={};capture(w,c)
 signal.signal(signal.SIGALRM,s1.timeout);start=time.monotonic()
 try:
  with (D/'replay.jsonl').open('w') as f:
   for i,r in enumerate(pre,1):
    s2.context(w,r);signal.alarm(120);z=w(r['row']);signal.alarm(0)
    info=curve_info(c);assert all(info[k]==r['curve'][k] for k in info)
    before=r['after'];m0,m1=metrics(before),metrics(z)
    if info['straight']:
     assert s2.norm(before)==s2.norm(z),(r['line_id'],'straight replay drift')
     encoded=lambda a:json.dumps(a,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
     assert encoded(before['evidence'])==encoded(z['evidence'])
     straight.append(dict(cohort=r['cohort'],line_id=r['line_id'],evidence_sha256=hashlib.sha256(encoded(z['evidence'])).hexdigest()))
     checks['straight_byte_identical']+=1
    assert before['evidence']['gate']==z['evidence']['gate']
    changed=m0!=m1
    delta={k:(m1[k]-m0[k] if m0[k] is not None and m1[k] is not None else None) for k in ('long_side','short_side','ratio','padding')}
    curves.append(dict(r['curve'],measurement_changed=changed,before=m0,after=m1,delta=delta,ambiguous_foot_pixels=z['evidence']['box_evidence'].get('row_frame',{}).get('ambiguous_foot_pixels',0)))
    rec=dict(r,before=before,after=z,verdict_s3=z['verdict']);f.write(json.dumps(rec,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n');f.flush()
    if i%100==0:print('S3 replay',i,flush=True)
  write(D/'curvature.jsonl',curves);write(D/'straight_readback.jsonl',straight)
  dump(D/'replay_receipt.json',dict(rows=len(pre),checks=checks,elapsed_seconds=time.monotonic()-start,network='OFF via unchanged S1 audit hook',readers=0))
 finally:signal.alarm(0);w.close()
if __name__=='__main__':
 if sys.argv[1]=='preflight':preflight()
 else:run()

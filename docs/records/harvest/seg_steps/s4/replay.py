"""Offline S4: unchanged S1 inputs, contexts, native adapter, timeout and scoring."""
from pathlib import Path
import importlib.util,sys,json,signal,time,hashlib
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('s3_replay',D.parent/'s3/replay.py');s3=importlib.util.module_from_spec(spec);spec.loader.exec_module(s3)
s2,s1=s3.s2,s3.s1
read,dump,write,sha=s1.read,s1.dump,s1.write,s1.sha
from greekocr.harvest.line_pipeline_native import NativeSegmenter,JsonService
from greekocr.harvest.predictor_path import predictor_binary
from PIL import Image
from collections import Counter
BASE=R.parent/'greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1';SS=BASE/'small_segments'

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def worker(version='s4'):
 v=json.loads((R/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 if version=='s4':return NativeSegmenter(v,predictor_binary())
 m=module('greekocr.harvest.s4_baseline_native',D/'baseline/greekocr/harvest/line_pipeline_native.py')
 # The baseline adapter imports sibling assets by __file__; use actual read-only
 # assets for normal initialization, then replace policy/crop tools explicitly.
 m.ASSETS=R/'greekocr/harvest/filtering_assets'
 v['segmentation']['version']='0.9-s3' if version=='s3' else '0.8'
 w=m.NativeSegmenter(v,predictor_binary())
 w.service.close();w.service=JsonService(['node',str(D/'baseline/greekocr/harvest/filtering_assets/service.mjs')])
 w.policy_sha=sha(D/'baseline/greekocr/harvest/filtering_assets/segmentation-policy.js')
 p=D/'baseline/greekocr/harvest/filtering_assets/crop-tools.py' if version=='s3' else D.parent/'s1/baseline/greekocr/harvest/filtering_assets/crop-tools.py'
 w.crop_tools=module('baseline_crop_'+version,p)
 if version=='08':
  original=w.crop_tools.features_from_observation
  w.crop_tools.features_from_observation=lambda **kw:original(**{k:v for k,v in kw.items() if k not in ('base_curve','base_is_straight')})
 return w

def norm(z):
 return s2.norm(z)

def canonical(z):return json.dumps(z,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()

def measure(w,inp):
 # Additional measurements are diagnostics even for blocked gates; no fabricated
 # Stage B evidence is inserted into a blocked tool result.
 c={};s3.capture(w,c);s2.context(w,inp);signal.alarm(120)
 try:z=w(inp['row'])
 finally:signal.alarm(0)
 g,cs,main=c['g'],c['components'],c['main']
 f=w.crop_tools.features_from_observation(width=g.width,height=g.height,components=cs,ink_box=None,ink_pixels=int(g.ink.sum()),xheight=float(g.band.xh),xheight_source=g.band.xh_source,support_count=g.band.n_support,chars=s1.character_count(inp['row']['raw_text']),labels=g.labels,angle_deg=c['angle'],base_curve=main.base if main is not None else None,base_is_straight=g.band.curve_is_straight if g.band.curve_is_straight is not None else g.band.degree!=2) if s1.character_count(inp['row']['raw_text'])<=8 and max(g.width,g.height)/min(g.width,g.height)<=6 else dict(candidate_text_box=z['evidence']['box_evidence'].get('bbox'),row_frame_text_box=z['evidence']['box_evidence'].get('row_frame'))
 return z,dict(s3_box=f['candidate_text_box'],s3_frame=f['row_frame_text_box'],all_box=all_box(cs),processed_width=g.width,processed_height=g.height,has_main=main is not None,component_count=len(cs))

def all_box(cs):
 if not cs:return None
 return [min(c['bbox'][0] for c in cs),min(c['bbox'][1] for c in cs),max(c['bbox'][2] for c in cs),max(c['bbox'][3] for c in cs)]

def run():
 rows=s1.inputs();assert rows==read(D.parent/'s3/inputs.jsonl');write(D/'inputs.jsonl',rows)
 saved=read(D.parent/'s3/replay.jsonl');a,b=worker('s3'),worker();checks=Counter();start=time.monotonic()
 existing=read(D/'replay.jsonl') if (D/'replay.jsonl').exists() else []
 for r in existing:
  z=r['after'];answer=b.service.call(dict(operation='decide',policy_sha256=b.policy_sha,evidence=z['evidence']))
  assert (answer['verdict'],answer['reason'])==(z['verdict'],z['reason'])
  z['policy_sha256']=b.policy_sha
  if not r['small']:assert canonical(norm(r['before']))==canonical(norm(z))
 write(D/'replay.jsonl',existing)
 for r in existing:
  checks['fresh_s3_matches_saved']+=1
  if not r['small']:checks['non_small_byte_identical']+=1
 signal.signal(signal.SIGALRM,s1.timeout)
 # Capture once; measure() below restores it to prevent recursive wrappers.
 try:
  with (D/'replay.jsonl').open('a') as out:
   for i,(inp,previous) in enumerate(zip(rows,saved),1):
    if i<=len(existing):continue
    orig=a.crop_tools.line_inventory
    old,geometry=measure(a,inp);a.crop_tools.line_inventory=orig
    assert s2.norm(old)==s2.norm(previous['after']),(inp['line_id'],'S3 drift')
    s2.context(b,inp);signal.alarm(120);new=b(inp['row']);signal.alarm(0)
    with Image.open(inp['row']['crop_path']) as im:width,height=im.size
    chars=s1.character_count(inp['row']['raw_text']);small=b.crop_tools.is_small_segment(chars,width,height)
    if not small:
     assert canonical(norm(old))==canonical(norm(new)),(inp['line_id'],'non-small drift')
     assert canonical(old['evidence'])==canonical(new['evidence'])
     checks['non_small_byte_identical']+=1
    checks['fresh_s3_matches_saved']+=1
    rec=dict(previous,before=old,after=new,verdict_s4=new['verdict'],chars=chars,A=max(width,height)/min(width,height),small=small,geometry=geometry)
    out.write(json.dumps(rec,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n');out.flush()
    if i%100==0:print('S4 replay',i,flush=True)
  dump(D/'replay_receipt.json',dict(rows=len(rows),checks=checks,elapsed_seconds=time.monotonic()-start,network='OFF via S1 audit hook',readers=0))
 finally:signal.alarm(0);a.close();b.close()

def typology():
 rows=read(SS/'samples.jsonl');assert len(rows)==437
 workers={v:worker(v) for v in ('08','s3','s4')};signal.signal(signal.SIGALRM,s1.timeout)
 try:
  with (D/'typology_replay.jsonl').open('w') as out:
   for i,m in enumerate(rows,1):
    p=SS/'crops'/f"{m['line_id']}.png";assert sha(p)==m['crop_sha256']
    row=dict(id=m['line_id'],parent_id='small-segment-typology',split='unassigned',crop_path=str(p),crop_sha256=m['crop_sha256'],raw_text=m['text'],script_class=m.get('script_class','pooled'),primary_class=m.get('primary_class'))
    inp=dict(cohort='typology',line_id=m['line_id'],row=row);zs={}
    for v,w in workers.items():
     orig=w.crop_tools.line_inventory
     if v=='s3':zs[v],geo=measure(w,inp);w.crop_tools.line_inventory=orig
     else:s2.context(w,inp);signal.alarm(120);zs[v]=w(row);signal.alarm(0)
    with Image.open(p) as im:width,height=im.size
    chars=s1.character_count(row['raw_text'])
    rec=dict(inp,manifest=m,versions=zs,geometry=geo,chars=chars,A=max(width,height)/min(width,height),small=workers['s4'].crop_tools.is_small_segment(chars,width,height))
    out.write(json.dumps(rec,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n');out.flush()
    if i%50==0:print('typology',i,flush=True)
 finally:
  signal.alarm(0)
  for w in workers.values():w.close()

if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='typology':typology()
 else:run()

"""S2 local native replay. S1 input/scoring/context workflow is imported unchanged."""
from pathlib import Path
import importlib.util,sys,json,signal,time,os
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('s1_replay',D.parent/'s1/replay.py');s1=importlib.util.module_from_spec(spec);spec.loader.exec_module(s1)
from PIL import Image
from collections import Counter
read,dump,write,sha=s1.read,s1.dump,s1.write,s1.sha
NativeSegmenter=s1.NativeSegmenter

def norm(o):
 if isinstance(o,dict):return {k:norm(v) for k,v in o.items() if k not in ('seconds','tool_version')}
 if isinstance(o,list):return [norm(v) for v in o]
 return o

def workers():
 versions=json.loads((R/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 oldv=json.loads((D/'baseline/docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 predictor=R/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict'
 a=NativeSegmenter(oldv,predictor);b=NativeSegmenter(versions,predictor)
 spec=importlib.util.spec_from_file_location('crop_tools_s1',D/'baseline/greekocr/harvest/filtering_assets/crop-tools.py');a.crop_tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(a.crop_tools)
 return a,b

def context(worker,inp):
 if inp['cohort']=='calibration':worker.context=lambda r,*args:contexts.get(r['id'],dict(status='unavailable',reason='no saved calibration source context'))
 else:worker.context=NativeSegmenter.context.__get__(worker)

contexts={r['id']:r for r in json.loads((s1.SITE/'qa/word-tolerance/context-evidence.json').read_text())['rows']}

def run():
 rows=s1.inputs();assert rows==read(D.parent/'s1/inputs.jsonl');write(D/'inputs.jsonl',rows)
 saved={(r['cohort'],r['line_id']):r for r in read(D.parent/'s1/replay.jsonl')}
 a,b=workers();start=time.monotonic();checks=Counter()
 signal.signal(signal.SIGALRM,s1.timeout)
 try:
  with (D/'replay.jsonl').open('w') as f:
   for i,inp in enumerate(rows,1):
    for w in (a,b):context(w,inp)
    signal.alarm(120);old=a(inp['row']);new=b(inp['row']);signal.alarm(0)
    previous=saved[inp['cohort'],inp['line_id']]
    assert norm(old)==norm(previous['after']),(inp['line_id'],'S1 drift')
    checks['s1_native_matches_saved']+=1
    with Image.open(inp['row']['crop_path']) as im:width,height=im.size
    if height<=width:
     assert norm(old)==norm(new),(inp['line_id'],'horizontal drift')
     checks['horizontal_byte_identical_evidence_and_verdict']+=1
    rec=dict(inp,before=old,after=new,baseline_08=previous['before'],width=width,height=height,turned=height>width,verdict_08=previous['verdict_08'],verdict_s1=old['verdict'],verdict_s2=new['verdict'])
    f.write(json.dumps(rec,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n');f.flush()
    if i%25==0:print(f'{i}/1288',flush=True)
 finally:signal.alarm(0);a.close();b.close()
 dump(D/'replay_receipt.json',dict(rows=len(rows),elapsed_seconds=time.monotonic()-start,checks=dict(checks),network='OFF via S1 audit hook',readers=0))
if __name__=='__main__':run()

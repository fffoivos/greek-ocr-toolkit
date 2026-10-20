"""Train case on exactly the already decoded S4 C1 inventory, offline."""
import os
for k in ('VECLIB_MAXIMUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):os.environ[k]='1'
import json,gzip,time,random
from collections import Counter
from pathlib import Path
from PIL import Image
from greekocr.labelfix import ink as I,case as C,markshape as M
from greekocr.labelfix.candidates import pair_tokens
from greekocr.labelfix.text import nfd,clusters
from greekocr.labelfix.ctc_align import Alignment
from greekocr.labelfix.validate import load_three_way,DEV_BOOKS
R=Path(__file__).resolve().parents[2];O=R/'docs/records/labelfix/spellcheck'
def main():
 start=time.monotonic();inventory=set(json.loads((O/'S4_training.json').read_text())['decoded']);assert len(inventory)<=10000
 selection={r['crop']:r for r in map(json.loads,(R/'.cache/labelfix/clariden/C1_selection.jsonl').read_text().splitlines()) if r['crop'] in inventory}
 excluded={l['doc'] for l in load_three_way(0)}-set(DEV_BOOKS)
 assert all(r['doc'] not in excluded and r['split']=='train' for r in selection.values())
 samples=[];opened=0
 with gzip.open(R/'.cache/labelfix/clariden/C1_alignments.jsonl.gz','rt') as f:
  for raw in f:
   r=json.loads(raw)
   if r['crop'] not in inventory:continue
   meta=selection[r['crop']];al=Alignment.from_record(r['alignment'])
   with Image.open(R.parent/'greek-ocr-toolkit'/r['crop']) as im:ci=I.analyse(im)
   opened+=1
   for g,m in pair_tokens(nfd(meta['label']),nfd(al.prediction)):
    if m is None:continue
    gc=clusters(g.core);mc=clusters(m.core)
    if len(gc)!=len(mc):continue
    for a,b in zip(gc,mc):
     if a.base!=b.base or not a.base.isalpha():continue
     sp=al.span(m.core_start+b.start);hits=[(I._overlap(sp.x0,sp.x1,c.x0,c.x1),c) for c in ci.components if c.role=='letter']
     hits.sort(key=lambda x:x[0],reverse=True)
     if not hits or hits[0][0]<=0 or len(hits)>1 and hits[1][0]>=.7*hits[0][0]:continue
     c=hits[0][1]
     samples.append(dict(line_id=meta['id'],doc=meta['doc'],label=C.label(a.base),x=C.features(ci,c)))
   if opened%1000==0:print('case harvest',opened,len(samples),round(time.monotonic()-start),flush=True)
 rng=random.Random(20261016);rng.shuffle(samples);used=Counter();fit=[];cal=[]
 for s in samples:
  if int.from_bytes(s['line_id'].encode()[-4:],'little')%7==0:cal.append(s);continue
  if used[s['label']]<10000:fit.append(s);used[s['label']]+=1
 model=M.fit_mlp([s['x'] for s in fit],[s['label'] for s in fit],sorted(used),hidden=48,epochs=50,seed=20261016)
 model.meta=dict(iteration='S5',fit_counts=dict(used),fit_docs=sorted({s['doc'] for s in fit}),decoded_crops=opened,pixel_only=True)
 model.save(R/'docs/records/labelfix/case_model_S5.json')
 with gzip.open(O/'S5_case_samples.jsonl.gz','wt') as f:
  for s in samples:f.write(json.dumps(s)+'\n')
 preds=model.probs([s['x'] for s in cal]).argmax(1) if cal else []
 receipt=dict(model.meta,calibration_n=len(cal),calibration_accuracy=sum(model.classes[p]==s['label'] for p,s in zip(preds,cal))/max(len(cal),1),elapsed_seconds=time.monotonic()-start,network=False,ctc_forward_passes=0,cpu_only=True)
 (O/'S5_case_training.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['fit_counts'],receipt['calibration_accuracy'],receipt['elapsed_seconds'],flush=True)
if __name__=='__main__':main()

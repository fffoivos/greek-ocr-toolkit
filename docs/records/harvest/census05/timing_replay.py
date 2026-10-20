"""Supplement missing per-row timing fields with paired local native timings.

Not a parity rerun: retained attempt-3 parity remains the qualification evidence.
No readers, no network. Times measure only segmentation on identical replay rows.
"""
import gzip,hashlib,importlib.util,json,os,signal,sys,time
from collections import defaultdict
from pathlib import Path
D=Path(__file__).resolve().parent;P=D/'package/projects/greek-ocr-toolkit-pipe032'
sys.path[:0]=[str(P),str(P/'tests')]
from tests._paths import install_record_loader
restore=install_record_loader()
from greekocr.harvest.line_pipeline_native import NativeSegmenter
spec=importlib.util.spec_from_file_location('timing_s4',P/'docs/records/harvest/seg_steps/s4/replay.py');s4=importlib.util.module_from_spec(spec);spec.loader.exec_module(s4)
def main():
 source=json.loads((D/'parity/source_receipt.json').read_text());records=[]
 for c in source['chunks']:
  for line in gzip.decompress((D/'parity'/c['path']).read_bytes()).splitlines():
   r=json.loads(line)
   if r['cohort'] in ['segeval1','calibration']:records.append(r)
 contexts=json.loads((P.parent/'ocr-review-sites-20261018/qa/word-tolerance/context-evidence.json').read_text())['rows'];contexts={r['id']:r for r in contexts}
 workers={name:s4.worker(tag) for name,tag in [('0.8','08'),('s4','s3'),('seg10','s4')]}
 # S4 code differs from SEG10 only by the policy band, using committed S4 assets.
 # Use its policy file from the S5 baseline, captured unchanged separately.
 workers['s4'].close()
 # The saved S4 replay has no per-row timers. Comparison relevant to forecast is
 # SEG10 vs the same rows at 0.8; do not call S3 an S4 timing.
 del workers['s4']
 samples=[]
 signal.signal(signal.SIGALRM,lambda *a: (_ for _ in ()).throw(TimeoutError('120-second row bound')))
 try:
  for i,r in enumerate(records,1):
   sample=dict(cohort=r['cohort'],id=r['line_id'],seconds={})
   for name,w in workers.items():
    w.context=(lambda row,*args:contexts.get(row['id'],dict(status='unavailable',reason='no saved calibration source context'))) if r['cohort']=='calibration' else NativeSegmenter.context.__get__(w)
    signal.alarm(120);start=time.monotonic();w(r['row']);sample['seconds'][name]=time.monotonic()-start;signal.alarm(0)
   samples.append(sample)
   if i%100==0:print('timing',i,flush=True)
 finally:
  signal.alarm(0)
  for w in workers.values():w.close()
 totals={k:sum(r['seconds'][k] for r in samples) for k in workers};ratio=totals['seg10']/totals['0.8'];seconds=6559*ratio
 (D/'timing_rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in samples))
 result=dict(rows=len(samples),source='paired local supplement; committed S4 and SEG10 replays contain aggregate times only',totals=totals,ratio=ratio,baseline_seconds=6559,estimate_seconds=seconds,estimate_hhmm='%02d:%02d'%(seconds//3600,seconds%3600//60),budget_seconds=14400,margin_seconds=14400-seconds,limitation='same-row segmentation ratio applied to census_03 whole-job time; Mac timing, not Clariden qualification; no per-row S4 timing existed',native_images=len(samples)*2,readers=0)
 (D/'runtime_estimate.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()

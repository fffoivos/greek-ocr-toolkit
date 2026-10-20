"""Native packaged replay against the hash-checked SEG10 expectation; no readers."""
import gzip, hashlib, json, os, signal, sys, time
from collections import Counter
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[2];P=D/'package/projects/greek-ocr-toolkit-pipe032'
sys.path.insert(0,str(P));os.environ.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
def offline(event,args):
 if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo'):raise RuntimeError('network OFF')
sys.addaudithook(offline)
from greekocr.harvest.line_pipeline_native import NativeSegmenter,file_sha

def main():
 receipt=json.loads((D/'parity/source_receipt.json').read_text());raw=b''
 for chunk in receipt['chunks']:
  p=D/'parity'/chunk['path'];assert file_sha(p)==chunk['sha256'];raw+=gzip.decompress(p.read_bytes())
 assert hashlib.sha256(raw).hexdigest()==receipt['sha256']
 all_rows=[json.loads(s) for s in raw.splitlines()];inputs=[r for r in all_rows if r['cohort'] in ('segeval1','calibration')]
 assert len(inputs)==1038
 contexts={r['id']:r for r in json.loads((R.parent/'ocr-review-sites-20261018/qa/word-tolerance/context-evidence.json').read_text())['rows']}
 predictor=R.parent/'greek-ocr-toolkit-main-next/scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict'
 assert file_sha(predictor)=='d2fe37a51f92f0b2d3416d4ca4917214ee0a354ab21e9ee80e664304ddce9adb'
 versions=json.loads((P/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 w=NativeSegmenter(versions,predictor);counts=Counter();actual=[];start=time.monotonic()
 def timeout(*args):raise TimeoutError('inherited 120-second row bound')
 signal.signal(signal.SIGALRM,timeout)
 try:
  for i,r in enumerate(inputs,1):
   row=r['row'];assert file_sha(row['crop_path'])==row['crop_sha256']
   w.context=(lambda row,*args:contexts.get(row['id'],dict(status='unavailable',reason='no saved calibration source context'))) if r['cohort']=='calibration' else NativeSegmenter.context.__get__(w)
   signal.alarm(120);answer=w(row);signal.alarm(0)
   assert answer['tool_version']=='0.13'
   for key in ('verdict','reason'):assert answer[key].encode()==r['after'][key].encode(),(r['line_id'],key,answer[key],r['after'][key])
   counts[r['cohort']]+=1;actual.append(dict(cohort=r['cohort'],row=row,segmentation=answer))
   if i%100==0:print('native',i,'/1038',flush=True)
 finally:signal.alarm(0);w.close()
 assert counts==dict(segeval1=150,calibration=888)
 with (D/'parity/native_results.jsonl.gz').open('wb') as stream:
  with gzip.GzipFile(fileobj=stream,mode='wb',filename='',mtime=0) as f:
   for r in actual:f.write((json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n').encode())
 result=dict(status='PASS',counts=dict(counts),verdict_and_reason_exact=True,compared_row_for_row=True,
  expectation_sha256=receipt['sha256'],route=receipt['route'],segmentation_version='0.13',segmentation_label='0.9-s5',
  policy_sha256=w.policy_sha,predictor_sha256=file_sha(predictor),elapsed_seconds=time.monotonic()-start,
  native_images=1038,readers=0,network=False)
 (D/'native_parity_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

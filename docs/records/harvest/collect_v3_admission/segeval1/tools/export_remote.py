"""Run via ssh clariden python3 -, read-only: reduce the immutable published export."""
import json,hashlib,gzip,sys,os
from pathlib import Path
base=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_02/census')
receipt=json.loads((base/'CURRENT.json').read_text())
p=(base/'decisions.jsonl').resolve()
h=hashlib.sha256(); count=0
out=gzip.GzipFile(fileobj=sys.stdout.buffer,mode='wb',mtime=0)
def emit(x):out.write((json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n').encode())
emit({'_provenance':{'current':receipt,'resolved_export':str(p)}})
with p.open('rb') as f:
 before=os.fstat(f.fileno())
 for line in f:
  h.update(line); r=json.loads(line); count+=1
  stages=[s['result'] for s in r.get('stages',[]) if s['stage']=='segmentation']
  if not stages:
   emit({'row_id':r['binding']['id'],'parent_id':r['binding']['parent_id'],'not_evaluated':True});continue
  assert len(stages)==1
  s=stages[0]
  emit(dict(row_id=r['binding']['id'],parent_id=r['binding']['parent_id'],crop_sha256=r['binding']['crop_sha256'],segmentation={k:v for k,v in s.items() if k not in ('evidence','frame')},pipeline_disposition=r['disposition'],run_binding_sha256=r['run_binding_sha256'],toolchain_digest=r['toolchain_digest']))
 after=os.fstat(f.fileno())
assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
assert json.loads((base/'CURRENT.json').read_text())==receipt
emit({'_receipt':{'export_sha256':h.hexdigest(),'rows':count,'bytes':before.st_size,'mtime_ns':before.st_mtime_ns}})
out.close()

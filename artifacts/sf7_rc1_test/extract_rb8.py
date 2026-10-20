"""Read-only compact witnesses from full remote files, emitted as a gzip stream."""
import json,gzip,pathlib,sys,hashlib
ROOT=pathlib.Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_test_20261019');RUN=ROOT/'output_3702849'
def rows(p):
 with (gzip.open if str(p).endswith('.gz') else open)(p,'rt',encoding='utf8') as f:
  for l in f:
   if l.strip():yield json.loads(l)
with gzip.GzipFile(fileobj=sys.stdout.buffer,mode='wb',mtime=0) as out:
 def emit(t,s,r):out.write((json.dumps(dict(type=t,split=s,**r),ensure_ascii=False)+'\n').encode())
 cfg=json.loads((ROOT/'config/tr2_job.json').read_text())
 for s,c in cfg['splits'].items():
  b=RUN/s;ids=set()
  for r in rows(b/'selection.jsonl'):
   assert r['id'] not in ids;ids.add(r['id']);emit('selection',s,{'id':r['id'],'label':r['label']})
  for r in rows(pathlib.Path(c['source'])):
   if r['id'] in ids:emit('raw',s,{'id':r['id'],'label':r['label']})
  for r in rows(b/'sf7/release/overlay_A.jsonl.gz'):
   emit('overlay',s,{k:r[k] for k in ('line_id','status','original_label_sha256','label') if k in r})
  for r in rows(b/'sf7/release/ctrl_subset_A.jsonl.gz'):emit('control',s,{'line_id':r['line_id']})

"""Read-only original parent metadata; PNG bytes are fetched only after sealing."""
import sys,json,gzip,hashlib
from pathlib import Path
base=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/collection_v2')
out=gzip.GzipFile(fileobj=sys.stdout.buffer,mode='wb',mtime=0)
for split in ['train','dev','test']:
 p=base/f'import_real_v2_{split}.jsonl';h=hashlib.sha256();n=0
 for line in p.open('rb'):
  h.update(line);r=json.loads(line);n+=1
  parts=Path(r['crop']).parts
  assert parts[:5]==('docs','harvest','harvest_big',r['wave'],'crops') and len(parts)==7
  r['remote_crop']=str(base/'crops'/r['wave']/parts[-2]/parts[-1]);r['parent_id']='collection-v2-'+split
  out.write((json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n').encode())
 out.write((json.dumps({'_parent_receipt':dict(path=str(p),sha256=h.hexdigest(),rows=n)})+'\n').encode())
out.close()

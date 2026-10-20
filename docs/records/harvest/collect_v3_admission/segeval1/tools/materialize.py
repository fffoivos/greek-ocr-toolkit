"""Only native work: byte-exact regeneration of the sealed 150 crops."""
import json,hashlib,sys,subprocess
from pathlib import Path
D=Path(__file__).resolve().parents[1]; P=D.parents[3].parent
sys.path.insert(0,str(P/'greek-ocr-toolkit-sol-collect'))
from collect_v3.storage import ensure_crop
import PIL
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((D/'draw_receipt.json').read_text())
assert sha(D/'keys/sealed_decisions.jsonl')==receipt['seal_sha256']
assert not (D/'crops_manifest.jsonl').exists()
(D/'crops').mkdir(exist_ok=True)
manifest=[];failed=[]
for line in (D/'keys/selected_features.jsonl').read_text().splitlines():
 r=json.loads(line);p=D/'crops'/(r['row_id']+'.png')
 try:
  if r.get('remote_crop'):
   # Existing original-v2 crop bytes are the immutable source, not a new render.
   data=subprocess.check_output(['ssh','clariden','cat',r['remote_crop']],timeout=60)
   assert hashlib.sha256(data).hexdigest()==r['crop_sha256']
   p.write_bytes(data)
  ensure_crop(dict(r,crop=str(p)))
  assert sha(p)==r['crop_sha256']
  manifest.append(dict(row_id=r['row_id'],path=str(p.relative_to(D)),sha256=sha(p),bytes=p.stat().st_size))
 except Exception as e:
  failed.append(dict(row_id=r['row_id'],error=str(e)))
 print(f'{len(manifest)+len(failed)}/150 materialised',flush=True)
(D/'crop_failures.json').write_text(json.dumps(failed,indent=2)+'\n')
if failed:raise SystemExit('Crop failures: seal replacement decisions from candidate order before producing replacement images')
(D/'crops_manifest.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in manifest))
(D/'materialization_receipt.json').write_text(json.dumps(dict(count=len(manifest),seal_sha256=receipt['seal_sha256'],manifest_sha256=sha(D/'crops_manifest.jsonl'),pillow=PIL.__version__,python=sys.executable,storage_sha256=sha(P/'greek-ocr-toolkit-sol-collect/collect_v3/storage.py')),indent=2)+'\n')

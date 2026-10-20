"""Rehash standing and regenerated input custody; no source checkout writes."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;BASE=D.parents[2].parent/'greek-ocr-toolkit-segcensus/docs/harvest/census05'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
audit=json.loads((BASE/'input_audit.json').read_text());receipt=[]
for e in audit['parents']+[audit['metadata'],audit['split']]:
 assert sha(e['path'])==e['sha256'];receipt.append(dict(path=e['path'],sha256=e['sha256'],bytes=Path(e['path']).stat().st_size))
for e in json.loads((D/'INPUTS.json').read_text()):
 if e['kind']=='regenerated_numerics':
  assert sha(e['local_path'])==e['sha256'] and sha(e['archive_path'])==e['archive_sha256']
  receipt.append(dict(path=e['local_path'],sha256=e['sha256'],bytes=e['bytes'],archive=e['archive_path'],archive_sha256=e['archive_sha256']))
(D/'input_custody.json').write_text(json.dumps(dict(status='PASS',inputs=receipt,cyrillic='five census05 release shas checked and full-loaded in corrections/report.json'),indent=2)+'\n')
print(len(receipt),'inputs hash checked')

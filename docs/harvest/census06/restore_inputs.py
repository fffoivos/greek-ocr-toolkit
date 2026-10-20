"""Restore ignored numerics files from the recorded archives, without overwriting."""
from pathlib import Path
import gzip,hashlib,json,shutil
D=Path(__file__).resolve().parent
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for r in json.loads((D/'INPUTS.json').read_text()):
 if r['kind']!='regenerated_numerics':continue
 archive=D/'corrections/archives'/Path(r['archive_path']).name
 target=D/'corrections'/Path(r['local_path']).name
 if target.exists():assert sha(target)==r['sha256'];continue
 assert sha(archive)==r['archive_sha256']
 with gzip.open(archive,'rb') as src,target.open('xb') as dst:shutil.copyfileobj(src,dst)
 assert sha(target)==r['sha256']

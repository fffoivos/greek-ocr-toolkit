"""Restore the exact regenerated ledgers from committed compressed chunks."""
import gzip,hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent

def main():
    for item in json.loads((D/'corrections/archive_receipt.json').read_text()):
        target=D/'corrections'/Path(item['local_path']).name
        if target.exists():
            with target.open('rb') as f: actual=hashlib.file_digest(f,'sha256').hexdigest()
            if actual!=item['sha256']:raise ValueError('existing input hash mismatch: '+str(target))
            continue
        with target.open('xb') as out:
            for c in item['chunks']:
                data=(D/c['path']).read_bytes()
                if hashlib.sha256(data).hexdigest()!=c['sha256']:raise ValueError('chunk SHA mismatch')
                out.write(gzip.decompress(data))
        with target.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==item['sha256']
if __name__=='__main__':main()

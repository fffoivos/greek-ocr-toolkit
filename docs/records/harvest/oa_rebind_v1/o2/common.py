"""O2 local, read-only input helpers. All generated files stay beside this module."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
MAIN = ROOT.parent / 'greek-ocr-toolkit'
HARVEST = MAIN / 'docs/harvest'
COL = HARVEST / 'collection'
O1 = OUT.parent
SPLITS = ('train', 'dev', 'test')
WAVES = ('round1','vouli','round2','parliament','openarchives','mixed','cyrillic','wikisource')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def fingerprint(path):
    path = Path(path)
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return dict(path=str(path), bytes=path.stat().st_size, sha256=h.hexdigest())

def dump(name, obj):
    path = OUT / name
    assert path.is_relative_to(OUT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n')

def jsonl(path):
    with Path(path).open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def write_jsonl(name, rows):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, allow_nan=False)+'\n')

def identity(r):
    if r.get('wave') and r.get('book_key'):
        return r['wave'], r['book_key']
    if r.get('wave'):
        if r.get('id'):
            return r['wave'], r['id'].split('-p', 1)[0]
        crop = r.get('crop') or r.get('crop_path')
        if crop:
            return r['wave'], Path(crop).parent.name
    if r.get('doc'):
        w, k = r['doc'].split(':', 1)
        return w, k.split('-p', 1)[0]
    return None

class Inputs:
    def __init__(self):
        self.entries = {}
    def add(self, path):
        path = Path(path).resolve()
        if str(path) not in self.entries:
            self.entries[str(path)] = fingerprint(path)
        return path
    def load(self, path):
        return json.loads(self.add(path).read_text())
    def rows(self, path):
        return jsonl(self.add(path))
    def finish(self, name):
        for path, old in self.entries.items():
            assert fingerprint(path) == old, ('input changed', path)
        dump(name, list(self.entries.values()))

"""Durable, secret-safe local storage primitives."""
from __future__ import annotations
import contextlib, fcntl, gzip, hashlib, json, logging, os, re, tempfile
from pathlib import Path

TOKEN_ENV = 'COLLECT_V3_ACCESS_TOKEN'

def scrub(value):
    text = str(value)
    for name, secret in os.environ.items():
        if secret and (name in (TOKEN_ENV,'GOOGLE_APPLICATION_CREDENTIALS') or any(x in name.upper() for x in ('TOKEN', 'PASSWORD', 'SECRET', 'API_KEY'))):
            text = text.replace(secret, '[REDACTED]')
    text = re.sub(r'(?i)(bearer\s+)[^\s"\',}]+', r'\1[REDACTED]', text)
    text = re.sub(r'(?i)(access_token|refresh_token|private_key|authorization)(["\s:=]+)[^\s,}]+', r'\1\2[REDACTED]', text)
    return text

class ScrubFilter(logging.Filter):
    def filter(self, record):
        record.msg = scrub(record.getMessage()); record.args = ()
        if record.exc_info:
            record.msg += ' [exception details suppressed]'; record.exc_info = None; record.exc_text = None
        return True

def dumps(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'))

def atomic_bytes(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.'+path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
        d = os.open(path.parent, os.O_RDONLY)
        try: os.fsync(d)
        finally: os.close(d)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def write_json(path, value): atomic_bytes(path, (dumps(value)+'\n').encode())
def write_rows(path, rows): atomic_bytes(path, ''.join(dumps(r)+'\n' for r in rows).encode())
def write_rows_gz(path, values):
    import io
    buffer=io.BytesIO()
    with gzip.GzipFile(fileobj=buffer,mode='wb',mtime=0) as f:
        for r in values:f.write((dumps(r)+'\n').encode())
    atomic_bytes(path,buffer.getvalue())

def read_json(path): return json.loads(Path(path).read_text())
def iter_rows(path):
    path = Path(path)
    if not path.exists() and Path(str(path)+'.gz').exists(): path = Path(str(path)+'.gz')
    if not path.exists(): return
    with (gzip.open(path, 'rt') if path.suffix == '.gz' else path.open()) as f:
        for line in f:
            if line.strip(): yield json.loads(line)
def rows(path): return list(iter_rows(path))
def sha_bytes(data): return hashlib.sha256(data).hexdigest()
def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for data in iter(lambda:f.read(1024*1024), b''): h.update(data)
    return h.hexdigest()

@contextlib.contextmanager
def lock(path, blocking=True):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as f:
        fcntl.flock(f, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
        yield

def disk_bytes(path): return sum(p.stat().st_size for p in Path(path).rglob('*') if p.is_file())

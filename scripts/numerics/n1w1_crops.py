"""Offline continuation of N1-C; never builds packs or classifies ink."""
import hashlib
import json
import platform
import random
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/n1'
SCRATCH = Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad')
COLLECT = Path.home() / 'Projects/greek-ocr-toolkit-sol-collect'
COLLECT_PY = COLLECT / '.venv/bin/python'
RUN = Path.home() / 'Projects/collect-v3-data/run'
GROUPS = [('thousands_dot',24),('decimal_comma',24),('range_dash',24),('inner_dash',12),('empty',12)]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def rows(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]

def write(path, value, jsonl=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # All persistent products are new; restart must use a fresh reviewed output.
    with path.open('x') as f:
        f.write(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in value) if jsonl else json.dumps(value,indent=2,ensure_ascii=False)+'\n')

def interpreter():
    import PIL
    import zlib
    return dict(executable=sys.executable, version=sys.version, machine=platform.machine(), pillow=PIL.__version__,zlib=zlib.ZLIB_VERSION,flags=str(sys.flags))

def regenerate(request, result):
    """Runs only in collector Python; the original row is never passed to ensure_crop."""
    sys.path.insert(0,str(COLLECT))
    from n1w1_storage import ensure_crop
    records=[]
    for row in rows(request):
        copied=dict(row,crop=str(SCRATCH/'n1_cache/crops'/(row['crop_sha256']+'.png')))
        try:
            crop=ensure_crop(copied)
            if sha(crop)!=row['crop_sha256']: raise ValueError('crop hash mismatch after ensure_crop')
            records.append(dict(line_id=row['id'],crop=str(crop),crop_sha256=sha(crop),crop_unavailable=False))
        except (ValueError,OSError) as exc:
            records.append(dict(line_id=row['id'],crop_unavailable=True,crop_error=str(exc)))
    write(result,dict(interpreter=interpreter(),records=records))


if __name__=="__main__":regenerate(Path(sys.argv[1]),Path(sys.argv[2]))

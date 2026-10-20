"""PREPARED ONLY. Owner approval required before running this fallback.

Its sole input is a literal REQUESTS list appended by a local runner. It reads
existing pages and streams exact hash-bound PNG bytes; no remote writes.
This file is deliberately not called by any delivered script.
"""
import base64
import hashlib
import io
import json
from pathlib import Path


def stream_crops(requests):
    from PIL import Image
    for r in requests:
        try:
            source = Path(r['source_page'])
            assert str(source).startswith('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/')
            with source.open('rb') as f:
                assert hashlib.file_digest(f, 'sha256').hexdigest() == r['source_sha256']
            with Image.open(source) as page:
                x0, y0, x1, y1 = r['bbox']
                assert 0 <= x0 < x1 <= page.width and 0 <= y0 < y1 <= page.height
                crop = page.convert(r['color_mode']).crop(r['bbox'])
                out = io.BytesIO()
                crop.save(out, format='PNG', compress_level=3)
            raw = out.getvalue()
            assert hashlib.sha256(raw).hexdigest() == r['crop_sha256']
            print(json.dumps(dict(row_id=r['row_id'], sha256=r['crop_sha256'],
                                  png_base64=base64.b64encode(raw).decode())), flush=True)
        except Exception as exc:
            print(json.dumps(dict(row_id=r['row_id'], error=type(exc).__name__ + ': ' + str(exc))), flush=True)

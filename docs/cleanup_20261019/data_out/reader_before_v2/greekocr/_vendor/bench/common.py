from __future__ import annotations
import hashlib
import json
import unicodedata as ud
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 'real-lines/o1-v1'


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_rows(path):
    with Path(path).open(encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def write_rows(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def script(c):
    from greekocr.harvest.text_primitives import unicode_letter_script
    return unicode_letter_script(c)


def features(text):
    letters = [c for c in text if c.isalpha()]
    scripts = {script(c) for c in letters}
    return dict(polytonic=any(0x1F00 <= ord(c) <= 0x1FFF for c in text),
                mixed_script=len(scripts) > 1, scripts=sorted(scripts),
                latin_share=sum(script(c) == 'latin' for c in letters) / max(1, len(letters)),
                non_ascii_latin=any(ord(c) > 127 and script(c) == 'latin' for c in text),
                digits_share=sum(c.isdigit() for c in text) / max(1, len(text)),
                length=len(text), words=len(text.split()), short_line=len(text.split()) < 3)

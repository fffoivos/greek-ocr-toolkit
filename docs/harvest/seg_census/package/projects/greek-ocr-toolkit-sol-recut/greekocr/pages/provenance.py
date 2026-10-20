"""Implementation identity for reproducible page review runs."""
import hashlib
from pathlib import Path


def implementation_sha256() -> str:
    root = Path(__file__).resolve().parents[2]
    sources = sorted((root / 'greekocr/pages').glob('*.py'))
    sources += [root / 'greekocr/glyphs' / name for name in (
        'components.py', 'baseline.py', 'letters.py', 'ink.py', 'columns.py')]
    return hashlib.sha256(b''.join(p.read_bytes() for p in sources)).hexdigest()

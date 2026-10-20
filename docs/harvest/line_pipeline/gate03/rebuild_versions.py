"""Reproduce the build with explicit read-only inputs absent in this worktree."""
from pathlib import Path
import hashlib
import json
import runpy
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
SOURCES = ROOT.parent / 'greek-ocr-toolkit-sol-recut'
HERE = Path(__file__).resolve().parent
original = Path.read_bytes
fallbacks = json.loads((HERE / 'version-build-fallbacks.json').read_text())
allowed = {item['requested']: item for item in fallbacks}


def read(path):
    if str(path) in allowed and not path.exists():
        item = allowed[str(path)]
        raw = original(SOURCES / path.relative_to(ROOT))
        assert hashlib.sha256(raw).hexdigest() == item['sha256']
        return raw
    return original(path)


module = runpy.run_path(str(ROOT / 'scripts/harvest/build_filter_versions.py'))
with patch.object(Path, 'read_bytes', read):
    result = module['build']()
(ROOT / 'docs/harvest/line_pipeline/tool_versions.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')

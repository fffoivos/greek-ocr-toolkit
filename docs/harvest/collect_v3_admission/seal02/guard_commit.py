#!/usr/bin/env python3
"""Check the exact SEAL02 handoff paths and hashes. Does not stage or commit."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
for line in (R/'DEPLOY_SHA256SUMS').read_text().splitlines():
    digest,name=line.split('  ',1)
    assert not Path(name).is_absolute() and '..' not in Path(name).parts
    assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,name
manifest=json.loads((R/'COMMIT_LIST.json').read_text())
for name,digest in manifest['sha256'].items():
    assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,name
print('GUARDED_COMMIT_LIST_OK',len(manifest['paths']),'paths; no git writes')

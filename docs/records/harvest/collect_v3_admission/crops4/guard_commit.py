#!/usr/bin/env python3
"""Validate the explicit CROPS4 commit allowlist; never stage or commit."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

B = Path(__file__).resolve().parent
ROOT = B.parents[3]
LIST = B / 'COMMIT_LIST.json'
record = json.loads(LIST.read_text())
allowed = set(record['files'])
actual = {str(p.relative_to(ROOT)) for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
actual.update({'docs/briefs/CROPS4C_bind_census06.md',
               'docs/harvest/collect_v3_admission/CROPS4C_RECEIPT.md'})
assert actual == allowed, 'scope changed: ' + repr(actual.symmetric_difference(allowed))
for name, expected in record['files'].items():
    path = ROOT / name
    assert not path.is_symlink(), 'symlink in commit scope: ' + name
    if expected is None:
        assert path == LIST, 'only the allowlist itself may omit a self hash'
    else:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, 'hash drift: ' + name
staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=ROOT).decode().split('\0')
assert not (set(staged) - {''} - allowed), 'unrelated paths already staged'
print('GUARD_OK ' + str(len(allowed)) + ' paths; no staging or commit performed')
print('git add -- ' + ' '.join(shlex.quote(n) for n in sorted(allowed)))

"""Enumerate release evidence and missing commit members without changing Git metadata."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGES = ('docs/programme_20261025/TRAIN_FULL_v1/stage_c_package',
            'out/TRAIN_FULL_v1/w1_h14/candidate_package_waiver')
LEDGER = 'docs/programme_20261025/TRAIN_FULL_v1/EXECUTION_STATE.md'


def model_paths(value):
    if isinstance(value, dict):
        if isinstance(value.get('path'), str) and not value['path'].startswith('/'):
            yield value['path']
        for item in value.values():
            yield from model_paths(item)
    elif isinstance(value, list):
        for item in value:
            yield from model_paths(item)


def required_paths(root):
    paths = set(model_paths(json.loads((root/'MODELS.json').read_text()))) | {LEDGER}
    for package in PACKAGES:
        payload = root/package/'PAYLOAD.json'
        paths.add(payload.relative_to(root).as_posix())
        for name, binding in json.loads(payload.read_text())['files'].items():
            if PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts:
                raise ValueError('unsafe sealed member')
            member = root/package/name
            data = member.read_bytes()
            if len(data) != binding['bytes'] or hashlib.sha256(data).hexdigest() != binding['sha256']:
                raise ValueError('sealed member mismatch: '+str(member))
            paths.add(member.relative_to(root).as_posix())
    # All byte-identity table rows and explicit repository files cited by the register/plan.
    for document in ('VERSIONS.md', 'docs/programme_20261028/RELEASE_v0/PLAN.md'):
        text = (root/document).read_text()
        for name in re.findall(r'`([^`\n]+)`', text):
            name = name.split('#')[0]
            if not Path(name).is_absolute() and (root/name).is_file():
                paths.add(name)
    return paths


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', default='HEAD')
    args = parser.parse_args(argv)
    # read-only object query; no staging, checkout, refs or index changes
    committed = set(subprocess.check_output(['git', 'ls-tree', '-rz', '--name-only', args.commit], cwd=ROOT).decode().split('\0'))
    paths = required_paths(ROOT)
    HERE.joinpath('EVIDENCE_PATHS.txt').write_text(''.join(p+'\n' for p in sorted(paths)))
    missing = sorted({p for p in paths if p not in committed} | {LEDGER})
    # Changed evidence is also named: coordinator must commit the actual cited bytes.
    HERE.joinpath('REQUIRED_EVIDENCE.txt').write_text(''.join(p+'\n' for p in missing))
    print(f'evidence={len(paths)} required_for_coordinator={len(missing)}')


if __name__ == '__main__':
    main()

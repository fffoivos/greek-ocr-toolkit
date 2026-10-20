"""Restore local archived test inputs without changing tool or receipt bytes.

These generated artifacts are prerequisites, not new repository source files.
The archive is the existing cleanup worktree's artifacts directory.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--build-runtime', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    receipt = []

    def restore(source, target, content=None):
        content = source.read_bytes() if content is None else content
        digest = hashlib.sha256(content).hexdigest()
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise ValueError(f'existing fixture differs: {target}')
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        receipt.append(dict(source=str(source), path=str(target.relative_to(root)),
                            bytes=len(content), sha256=digest))

    trees = ('cleanup_sr1', 'cleanup_step4', 'owner_sheets/v2/recovered_crops')
    files = ('owner_sheets/v2/failure_modes_per_class.html',
             'owner_sheets/v2/segmentation_failures.html')
    for name in trees:
        source = args.archive / name
        if not source.is_dir():
            raise FileNotFoundError(source)
        for path in sorted(source.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                restore(path, root/'artifacts'/name/path.relative_to(source))
    for name in files:
        restore(args.archive/name, root/'artifacts'/name)

    target = root/'docs/records/harvest/collect_v3_admission/seg/CP5_verification.json'
    source = target.with_suffix('.json.gz')
    content = gzip.decompress(source.read_bytes())
    assert hashlib.sha256(content).hexdigest() == 'cc5131461ce6fa43a5f5be67fe74a5638b5d7226145dee2883ab1632c6a26731'
    restore(source, target, content)

    if args.build_runtime:
        cargo = shutil.which('cargo')
        if cargo is None:
            raise RuntimeError('cargo unavailable; native segmentation fixtures need the Rust predictor')
        manifest = root/'scripts/harvest/filter_runtime/Cargo.toml'
        for profile in (['--release'], []):
            subprocess.run([cargo, 'build', *profile, '--offline', '--manifest-path', str(manifest)], check=True)

    destination = root/'docs/cleanup_20261019/TEST_FIXTURE_RECEIPT.json'
    destination.write_text(json.dumps(dict(generated_inputs=receipt), indent=2)+'\n')
    print(f'verified {len(receipt)} generated fixtures; receipt: {destination}')


if __name__ == '__main__':
    main()

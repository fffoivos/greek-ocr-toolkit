"""Manifest every excluded bulk smoke receipt, including gitignored files; no deletion."""
from pathlib import Path
import argparse
import hashlib
import os

try:
    from .inventory import is_bulk, write_tsv
except ImportError:
    from inventory import is_bulk, write_tsv


def receipt_manifest(root):
    root = Path(root).resolve(); rows = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d != '.git' and not (Path(directory)/d).is_symlink())
        for name in sorted(files):
            p = Path(directory)/name
            relative = p.relative_to(root).as_posix()
            if not is_bulk(relative):
                continue
            if p.is_symlink():
                data = os.fsencode(os.readlink(p)); digest = hashlib.sha256(data).hexdigest(); size = len(data)
            else:
                h = hashlib.sha256()
                with p.open('rb') as f:
                    for block in iter(lambda: f.read(1 << 20), b''):
                        h.update(block)
                digest = h.hexdigest(); size = p.stat().st_size
            rows.append(dict(path=relative, bytes=size, sha256=digest))
    return sorted(rows, key=lambda r: r['path'])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('BULK_RECEIPT_MANIFEST.tsv'))
    args = parser.parse_args(argv)
    rows = receipt_manifest(args.root)
    write_tsv(args.output, rows, ['path', 'bytes', 'sha256'])
    print(f'bulk_receipt_files={len(rows)} bytes={sum(r["bytes"] for r in rows)}')


if __name__ == '__main__':
    main()

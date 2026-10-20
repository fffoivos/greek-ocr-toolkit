"""Load CLEAN4L2 documentation aliases without editing the installed package.

Tests and repository scripts share this companion to CLEAN4L3's resolver map.
Historical receipts and mirrored bulk data keep their original path identities.
"""
from __future__ import annotations

import csv
import sys

# Support the documented direct invocation from an uninstalled checkout.
if __name__ == "__main__":
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
from pathlib import Path

from greekocr.ops import data_root

ROOT = Path(__file__).resolve().parents[1]
ALIAS_MAP = ROOT / 'docs/cleanup_20261019/LAYOUT_ALIASES_2.tsv'

with ALIAS_MAP.open(newline='') as stream:
    EXTRA_MOVES = tuple((row['old'], row['new'])
                        for row in csv.DictReader(stream, delimiter='\t'))

# The resolver consults this table at call time. Install once per interpreter;
# Sort by both identities so a broad reverse alias (such as the former draft A
# directory) cannot hide a newly relocated reference file beneath that home.
data_root._LAYOUT_MOVES = tuple(sorted(
    dict((*data_root._LAYOUT_MOVES, *EXTRA_MOVES)).items(),
    key=lambda pair: max(map(len, pair)), reverse=True))
MOVES = data_root._LAYOUT_MOVES


def relocated(path):
    """Map a local historical path, retaining explicit other-checkout paths."""
    original = Path(path)
    prefix = ROOT if original.is_absolute() else Path()
    if original.is_absolute():
        try:
            relative = original.relative_to(ROOT).as_posix()
        except ValueError:
            return original
    else:
        relative = original.as_posix()
    for old, new in MOVES:
        if relative == old or relative.startswith(old + '/'):
            return prefix / (new + relative[len(old):])
    return original


def check_git_aliases():
    """Exercise every alias in a minimal checkout made only from HEAD blobs.

    One real tracked descendant per directory alias is sufficient to test its
    prefix mapping. Receipt-only aliases use their real external counterpart.
    Untracked/ignored files from the working tree cannot satisfy this check.
    """
    import json
    import os
    import subprocess
    import tarfile
    import tempfile

    def git(*args):
        return subprocess.check_output(['git', '-C', str(ROOT), *args])

    tracked = git('ls-tree', '-r', '--name-only', 'HEAD').decode().splitlines()
    receipts = {}
    for name in tracked:
        if name.startswith(str(data_root.RECEIPTS) + '/receipt_') and name.endswith('.tsv'):
            for row in csv.DictReader(git('show', 'HEAD:' + name).decode().splitlines(), delimiter='\t'):
                receipts[row['path']] = row
    selected = {p for p in tracked if p.startswith('greekocr/ops/') and p.endswith('.py')}
    selected.update(('greekocr/__init__.py', 'scripts/layout_paths.py',
                     'docs/cleanup_20261019/LAYOUT_ALIASES_2.tsv'))
    selected.update(p for p in tracked if p.startswith(str(data_root.RECEIPTS) + '/'))
    cases = []
    for old, new in MOVES:
        witness = next((p for p in tracked if p == new or p.startswith(new + '/')), None)
        if witness:
            selected.add(witness)
            cases.append((old + witness[len(new):], witness))
        else:
            witness = next((p for p in receipts if p == old or p.startswith(old + '/')
                            or p == new or p.startswith(new + '/')), None)
            if witness is None:
                raise AssertionError(f'Alias has no Git or receipt witness: {old} -> {new}')
            counterpart = new + witness[len(old):] if witness.startswith(old) else old + witness[len(new):]
            cases.append((witness, counterpart))
    with tempfile.TemporaryDirectory(prefix='clean6-git-aliases-') as directory:
        checkout = Path(directory)
        archive = checkout / 'head.tar'
        with archive.open('wb') as stream:
            subprocess.run(['git', '-C', str(ROOT), 'archive', 'HEAD', *sorted(selected)],
                           stdout=stream, check=True)
        with tarfile.open(archive) as bundle:
            bundle.extractall(checkout)  # Trusted paths selected from this repository's Git tree.
        code = ("import json; from greekocr.ops.data_root import resolve; "
                "from scripts.layout_paths import MOVES; "
                "cases=json.loads(__import__('sys').argv[1]); "
                "assert len(cases)==len(MOVES), (len(cases),len(MOVES)); "
                "[(resolve(a),resolve(b)) for a,b in cases]; "

                "print(f'Git-only alias check: {len(cases)} rows resolved; 0 missing')")
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(checkout))
        subprocess.run([sys.executable, '-c', code, json.dumps(cases)], cwd=checkout,
                       env=env, check=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', required=True)
    parser.parse_args()
    check_git_aliases()

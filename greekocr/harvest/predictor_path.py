"""Resolve the frozen predictor without writing build products to the checkout."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

_ROOT = Path(__file__).resolve().parents[2]
_RUNTIME = _ROOT / 'scripts/harvest/filter_runtime'
_BINARY = 'greekocr-frozen-font-predict'


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _executable(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


def predictor_binary(profile: str = 'debug') -> Path:
    """Use explicit binary, scratch build, then legacy target; otherwise build.

    GREEK_OCR_BUILD_DIR is a Cargo target directory. The default target directory
    is a per-user cache keyed by Cargo.lock. A missing predictor builds both
    profiles offline with the lockfile, recording their identities in scratch.
    An invalid explicit override is an error, rather than a fallback.
    """
    if profile not in ('debug', 'release'):
        raise ValueError("predictor profile must be 'debug' or 'release'")
    explicit = os.environ.get('GREEK_OCR_PREDICTOR')
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not _executable(path):
            raise RuntimeError(f'GREEK_OCR_PREDICTOR is not an executable file: {path}')
        return path

    lock_sha = _sha(_RUNTIME / 'Cargo.lock')
    cache = Path.home() / ('Library/Caches' if sys.platform == 'darwin' else '.cache')
    scratch = Path(os.environ.get('GREEK_OCR_BUILD_DIR') or
                   cache / 'greek-ocr-toolkit/filter_runtime' / lock_sha).expanduser().resolve()
    binary = scratch / profile / _BINARY
    legacy = _RUNTIME / 'target' / profile / _BINARY
    for path in (binary, legacy):
        if _executable(path):
            return path

    options = (f'Set GREEK_OCR_PREDICTOR to an existing executable; provide a build '
               f'under GREEK_OCR_BUILD_DIR ({binary}); or provide the in-repo '
               f'target build ({legacy}).')
    cargo = shutil.which('cargo')
    if cargo is None:
        raise RuntimeError(f'Frozen predictor is missing and cargo is unavailable. {options}')
    scratch.mkdir(parents=True, exist_ok=True)
    try:
        for mode in ('debug', 'release'):
            command = [cargo, 'build', '--offline', '--locked', '--target-dir', str(scratch)]
            if mode == 'release':
                command.append('--release')
            subprocess.run(command, cwd=_RUNTIME, check=True, capture_output=True, text=True)
        rustc = subprocess.run(['rustc', '--version'], check=True, capture_output=True,
                               text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        raise RuntimeError(f'Offline locked predictor build failed: {detail}\n{options}') from exc
    receipt = dict(cargo_lock_sha256=lock_sha, rustc_version=rustc,
                   binaries={mode: dict(path=str(scratch / mode / _BINARY),
                                        sha256=_sha(scratch / mode / _BINARY))
                             for mode in ('debug', 'release')})
    temporary = scratch / f'.BUILD_RECEIPT.{os.getpid()}.json'
    temporary.write_text(json.dumps(receipt, indent=2) + '\n')
    temporary.replace(scratch / 'BUILD_RECEIPT.json')
    return binary

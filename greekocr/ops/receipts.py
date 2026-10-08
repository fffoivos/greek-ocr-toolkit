"""File identity and atomic JSON receipts."""
from __future__ import annotations
from pathlib import Path
from typing import Mapping
from greekocr.types import PathLike, Record
from greekocr._vendor.train.mix import sha256 as _sha256
from greekocr._vendor.bench.e1_common import atomic_json as _atomic_json
__all__ = ['file_sha256', 'verify_files', 'write_receipt']

def file_sha256(path: PathLike) -> str:
    return _sha256(path)


def verify_files(binding: Mapping[str, str]) -> None:
    for name, expected in binding.items():
        if file_sha256(name) != expected: raise ValueError('bound file changed: ' + name)


def write_receipt(path: PathLike, receipt: Record) -> None:
    _atomic_json(Path(path), receipt)

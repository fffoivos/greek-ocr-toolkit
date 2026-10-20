"""Offline text-layer extraction; missing layers stay flagged."""
from __future__ import annotations
from typing import Sequence
from pathlib import Path
from greekocr.types import PathLike, Record
__all__ = ['extract_lines']

def extract_lines(sources: PathLike, partition: PathLike, out: PathLike, *,
                  pages: Sequence[int] | None = None, seed: int = 20261007) -> Record:
    """Extract reviewed PDF/DjVu sources; API page indices are zero-based."""
    from greekocr._vendor.bench.o4b_textlayer_lines import extract
    return extract(Path(sources), Path(partition), Path(out), pages, seed)

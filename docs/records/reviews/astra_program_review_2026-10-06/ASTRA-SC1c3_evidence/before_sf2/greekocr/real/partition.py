"""Reviewed canonical works and compulsory exposure exclusions."""
from __future__ import annotations
from typing import Mapping, Sequence
from pathlib import Path
from greekocr.types import PathLike, Record
from greekocr._vendor.bench import o4b_common as _common
from greekocr._vendor.bench.o4b_partition import build as _build
__all__ = ['DocumentPartition', 'resolve_exclusions', 'build_partition']

class DocumentPartition:
    def __init__(self, manifest: PathLike, seed: int = 20261007) -> None:
        self._partition = _common.Partition(Path(manifest), seed)
        self.binding: Record = self._partition.binding

    def assign(self, document: str, sha256: str | None = None) -> tuple[str, str | None]:
        """Return canonical work and split; excluded works get None."""
        return self._partition.assign(document, sha256)


def resolve_exclusions(documents: Mapping[str, str], identities: Sequence[str]) -> list[str]:
    """Resolve every known alias; unknown exposure identities are errors."""
    return _common.resolve_exclusions(documents, identities)


def build_partition(o5: PathLike, c1: PathLike, document_map: PathLike, out: PathLike,
                    *, reviewed: bool = False) -> Record:
    return _build(Path(o5), Path(c1), Path(document_map), Path(out), reviewed)

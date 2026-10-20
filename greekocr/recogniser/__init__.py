"""Phase 1 recogniser API over frozen implementations."""
from __future__ import annotations
from collections.abc import Iterable
from pathlib import Path

from .api import Recogniser, Reading, load
from .alignment import Alignment, align, transfer, confidence_matches
from .cache import AlignmentCache, crop_key
from .guard import forbid_forward


def run_shard(crops: Iterable[str | Path], recogniser: Recogniser,
              cache_path: str | Path, *, bs: int = 16) -> dict[str, Alignment]:
    """Run one caller-selected shard and persist canonical records with provenance."""
    return AlignmentCache(cache_path, recogniser).get(crops, bs=bs)


__all__ = ['load', 'Recogniser', 'Reading', 'Alignment', 'align', 'transfer',
           'confidence_matches', 'AlignmentCache', 'crop_key', 'run_shard', 'forbid_forward']

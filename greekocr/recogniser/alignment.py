"""Adapters over the frozen CTC implementation; no alignment logic is copied."""
from __future__ import annotations
from collections.abc import Sequence
from typing import Any, TYPE_CHECKING

from copy import deepcopy
import math
import numpy as np
from greekocr.labelfix import ctc_align as ctc
from greekocr.labelfix.text import clusters, nfd

if TYPE_CHECKING:
    from .api import Reading

__all__ = ['Alignment', 'align', 'transfer', 'confidence_matches']


class Alignment(ctc.Alignment):
    def slots(self) -> list[dict[str, Any]]:
        """One slot per existing text cluster, retaining the frozen span geometry."""
        return [dict(start=c.start, base=c.base, marks=c.marks,
                     spans=self.spans[c.start:c.end],
                     evidence=dict(window=list(self.window(c.start, c.end))))
                for c in clusters(self.prediction)]

    def evidence(self, slots: Sequence[dict[str, Any]], image_width: int) -> dict[str, Any]:
        return self.recognition_evidence(slots, image_width)


def wrap(alignment):
    # Preserve unrounded first-pass spans; cache alone deliberately round-trips.
    out = Alignment(**{k: getattr(alignment, k) for k in ctc.Alignment.__dataclass_fields__})
    if getattr(alignment, 'transferred', False):
        out.transferred = True
    return out


def align(reading: Reading) -> Alignment:
    if reading.alignment is None:
        raise ValueError(f'{reading.profile} does not expose frame alignment')
    return reading.alignment


def transfer(alignment_or_record: ctc.Alignment | dict[str, Any], new_text: str) -> Alignment:
    """NFD, discard frame scores, flag even identity transfers; return Alignment.

    Unlike ctc.transfer_alignment, identity transfer makes a detached flagged copy.
    Unlike r1_common.transfer_record, frames and their prediction hash are discarded.
    Geometry/nearest-neighbour assignment still delegates to the frozen function.
    """
    old = (ctc.Alignment.from_record(alignment_or_record) if isinstance(alignment_or_record, dict)
           else alignment_or_record)
    out = wrap(deepcopy(ctc.transfer_alignment(nfd(new_text), old)))
    out.frame_confidences = None
    out.transferred = True
    return out


def confidence_matches(frames: Sequence[float] | np.ndarray | None,
                       confidence: float | None) -> bool:
    """Float32-origin frame means, with absolute tolerance 1e-6 (no relative tolerance)."""
    if frames is None or confidence is None:
        return False
    values = np.asarray(frames, dtype=np.float64)
    return bool(values.ndim == 1 and values.size and np.isfinite(values).all()
                and ((0 <= values) & (values <= 1)).all()
                and math.isfinite(confidence) and 0 <= confidence <= 1
                and math.isclose(float(values.mean()), confidence, rel_tol=0, abs_tol=1e-6))

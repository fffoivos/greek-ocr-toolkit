"""Per-letter ink state: one signed variable. < 0 the letter is not fully written (broken into pieces, or faint);
> 0 it ran into its neighbours (several letters in one blob: over-inking or touching type); 0 intact.

    broken  : −0.5 for 2 middle-region pieces, −1 for 3 or more             (letters.letter_boxes, owner rule)
    faint   : −0.5 when the letter's ink contrast is under FAINT × the line's typical letter contrast
    merged  : +0.5 when cut out of a 2-letter blob, +1 for 3 or more
The most negative of broken/faint wins; merged applies only to intact letters. Measurements use the middle region.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
from numpy.typing import NDArray

from greekocr.glyphs.components import LineGlyphs
from greekocr.glyphs.letters import LetterBox, letter_boxes

__all__ = ['FAINT', 'InkProfile', 'LetterInk', 'ink_profile']

FAINT = .5


@dataclass(frozen=True)
class LetterInk:
    x0: int
    x1: int
    y0: int
    y1: int
    score: float
    pieces: int
    merged: int
    contrast: float      # letter ink contrast / line reference (1 = typical)
    state: str           # intact | broken | faint | merged


@dataclass(frozen=True)
class InkProfile:
    letters: tuple[LetterInk, ...]
    column: NDArray[np.float64]      # per column score over letter extents; NaN between letters
    reference_contrast: float


def _contrast(glyphs: LineGlyphs, box: LetterBox) -> float:
    xs = np.arange(box.x0, box.x1)
    sub = np.isin(glyphs.labels[:, box.x0:box.x1], box.components)
    rows = np.arange(glyphs.height)[:, None]
    mid = sub & (rows >= glyphs.band.top[xs][None, :]) & (rows < glyphs.band.bottom[xs][None, :])
    vals = glyphs.gray[:, box.x0:box.x1][mid if mid.any() else sub]
    return glyphs.paper - float(np.median(vals)) if vals.size else 0.0


def ink_profile(glyphs: LineGlyphs, boxes: list[LetterBox] | None = None, *,
                reference_contrast: float | None = None) -> InkProfile:
    boxes = boxes if boxes is not None else letter_boxes(glyphs)
    contrasts = [_contrast(glyphs, b) for b in boxes]
    ref = reference_contrast if reference_contrast is not None else (float(np.median(contrasts)) if contrasts else 1.0)
    col = np.full(glyphs.width, np.nan)
    out = []
    for b, c in zip(boxes, contrasts):
        rel = c / ref if ref > 0 else 1.0
        broken = -.5 if b.pieces == 2 else (-1.0 if b.pieces >= 3 else 0.0)
        faint = -.5 if rel < FAINT else 0.0
        neg = min(broken, faint)
        if neg < 0:
            score, state = neg, 'broken' if broken <= faint else 'faint'
        elif b.merged > 1:
            score, state = (.5 if b.merged == 2 else 1.0), 'merged'
        else:
            score, state = 0.0, 'intact'
        out.append(LetterInk(b.x0, b.x1, b.y0, b.y1, score, b.pieces, b.merged, round(rel, 3), state))
        col[b.x0:b.x1] = score
    return InkProfile(tuple(out), col, ref)

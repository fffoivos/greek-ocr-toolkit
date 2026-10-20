"""Lines API (owner 8 Oct 16:40): separate the text lines of a crop and straighten each one.

separate_lines(crop) → one LineImage per text line found: per column segment, the main line and every neighbour line
whose letter bodies are at least `min_visible` inside the crop. Each line image is straightened along its own fitted
baseline (skew and bends removed) and normalised in height from its four guide lines, with a mask of the rows that
fall outside the crop (what the crop cut off, top and bottom, per column).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray
from PIL import Image

from greekocr.glyphs.baseline import GuideLines, text_lines
from greekocr.glyphs.columns import column_segments
from greekocr.glyphs.components import binarise

__all__ = ['LineImage', 'ABOVE', 'BELOW', 'separate_lines', 'straighten', 'straighten_edges']

ABOVE, BELOW = 1.9, 1.0      # output extent above / below the baseline, in x-heights: tall letters + accents; tails


@dataclass
class LineImage:
    image: Image.Image                # straightened line, baseline at row `baseline_row`
    missing: NDArray[np.bool_]        # same shape: True where the source row lay outside the crop
    baseline_row: int
    xh: float
    x0: int                           # columns of the source crop this line covers
    x1: int
    segment: int                      # column segment index (0 = leftmost)
    side: str                         # 'main' | 'above' | 'below'
    shift_xh: float                   # offset from the segment's main baseline
    visible: float                    # mean fraction of the letter body inside the crop
    top_cut: NDArray[np.float64]      # per output column: fraction of the letter body (mean line → baseline) above the crop top
    bottom_cut: NDArray[np.float64]   # per output column: fraction of the letter body below the crop bottom


def straighten(gray: NDArray[np.float64], base: NDArray[np.float64], xh: float, *, paper: float,
               above: float = ABOVE, below: float = BELOW) -> tuple[NDArray[np.float64], NDArray[np.bool_], int]:
    """Resample every column so the baseline lands on one row; linear interpolation along each column.
    The returned mask marks output pixels whose source lay outside the crop (either edge); see straighten_edges."""
    h, w = gray.shape
    up, down = int(round(above * xh)), int(round(below * xh))
    out_h = up + down
    rows = np.arange(out_h, dtype=np.float64) - up                 # offsets from the baseline
    src = base[None, :] + rows[:, None]                            # source row per output pixel
    missing = (src < 0) | (src > h - 1)
    s0 = np.clip(np.floor(src).astype(int), 0, h - 1)
    s1 = np.clip(s0 + 1, 0, h - 1)
    f = np.clip(src - s0, 0, 1)
    cols = np.arange(w)[None, :]
    out = gray[s0, cols] * (1 - f) + gray[s1, cols] * f
    out[missing] = paper
    return out, missing, up


def straighten_edges(base: NDArray[np.float64], xh: float, height: int, *, above: float = ABOVE,
                     below: float = BELOW) -> tuple[NDArray[np.bool_], NDArray[np.bool_]]:
    """Directional masks of the straightened grid: source above the crop top / below the crop bottom (CP-G3 F2)."""
    up, down = int(round(above * xh)), int(round(below * xh))
    src = base[None, :] + (np.arange(up + down, dtype=np.float64) - up)[:, None]
    return src < 0, src > height - 1


def separate_lines(crop: Image.Image | NDArray[Any], *, min_visible: float = .5, tight: bool = True,
                   margin: float = .2, level_deg: float = 0.0, **kw: Any) -> list[LineImage]:
    """One straightened image per text line. Recogniser-facing default: tight=True, margin=0.2 x-heights — the image is
    cropped to its own ink ± margin after straightening. level_deg > 0 shifts (does not resample) baselines within
    level_deg of level — NOT qualified (CP-G4 F5: changes E1 readings on 10/40 level strips), so off by default.
    Calibration (docs/records/glyphs/GLYPHS_CALIBRATION.md, 240 strips, two readers): E1 median NFD CER on level lines
    0.028 → 0.028, on 1–5° lines 0.188–0.860 → 0.028–0.042; a fixed-height paper pad (tight=False, for display) cost
    level lines 0.028 → 0.069."""
    img = crop if isinstance(crop, Image.Image) else Image.fromarray(np.asarray(crop).astype(np.uint8))
    out: list[LineImage] = []
    for k, seg in enumerate(column_segments(img, **kw)):
        g = seg.glyphs
        if g is None:
            continue
        xh = g.band.xh
        for L in text_lines(g):
            if L.side != 'main' and L.visible < min_visible:
                continue
            x0, x1 = (0, g.width) if L.side == 'main' else (max(0, L.x0 - int(xh)), min(g.width, L.x1 + int(xh)))
            gray = g.gray[:, x0:x1]
            base_line = L.base[x0:x1]
            if level_deg > 0 and np.degrees(np.arctan(abs(float(np.ptp(base_line))) / max(1, x1 - x0))) < level_deg:
                base_line = np.full_like(base_line, round(float(np.median(base_line))))   # level: shift only
            arr, missing, up = straighten(gray, base_line, xh, paper=g.paper)
            above_top, below_bottom = straighten_edges(base_line, xh, g.height)
            body = slice(up - int(round(xh)), up)                       # mean line → baseline rows
            top_cut, bottom_cut = above_top[body].mean(axis=0), below_bottom[body].mean(axis=0)   # source damage: before
            if tight:                                                   # any output cropping (CP-G4 F1)
                ink = binarise(arr) & ~missing
                rows = np.nonzero(ink.any(axis=1))[0]
                if rows.size:
                    t0 = max(0, int(rows[0] - margin * xh)); t1 = min(arr.shape[0], int(rows[-1] + 1 + margin * xh))
                    arr, missing = arr[t0:t1], missing[t0:t1]
                    up -= t0
            out.append(LineImage(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'L'), missing, up, xh,
                                 seg.x0 + x0, seg.x0 + x1, k, L.side, L.shift_xh, L.visible,
                                 top_cut, bottom_cut))
    return out

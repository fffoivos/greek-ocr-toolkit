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


def separate_lines(crop: Image.Image | NDArray[Any], *, min_visible: float = .5, **kw: Any) -> list[LineImage]:
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
            arr, missing, up = straighten(gray, L.base[x0:x1], xh, paper=g.paper)
            above_top, below_bottom = straighten_edges(L.base[x0:x1], xh, g.height)
            body = slice(up - int(round(xh)), up)                       # mean line → baseline rows
            out.append(LineImage(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'L'), missing, up, xh,
                                 seg.x0 + x0, seg.x0 + x1, k, L.side, L.shift_xh, L.visible,
                                 above_top[body].mean(axis=0), below_bottom[body].mean(axis=0)))
    return out

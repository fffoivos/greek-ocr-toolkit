"""The page-lines algorithm, literally (docs/PAGE_LINES_ALGORITHM.md, owner 8 Oct 19:10).

page_lines(page, boxes) → every text line on the page with its outermost boundary: a top and a bottom curve over its
full extent, overlapping no other line.

1. every box's line(s) are fitted (a box may hold more than one: columns side by side, lines stacked);
2. each line's neighbours up / down / left / right are linked;
3. each line's baseline curve is followed (inside its box from the fit, beyond it letter by letter);
4. the page's font gives the four font lines (top, mean, base, bottom) as heights above / below the baseline;
5. the four font lines follow each line's curve;
6. at every column the boundary with a neighbour is the middle between the facing font lines;
7. lines are extended as far as their ink continues: stop at the page edge, a rule or shading, or a very large gap.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray
from PIL import Image
from scipy import ndimage as ndi

from greekocr.glyphs.components import EIGHT, binarise, to_gray
from greekocr.glyphs.recut import LineFit, RULE_ASPECT, RULE_HEIGHT, _walk, fit_box

__all__ = ['PageTextLine', 'page_lines']

THIN = .8          # a box lower than this × the median box height is fitted in a taller window ...
WINDOW = 1.5       # ... of this many median box heights
SAME = .5          # left / right neighbours: baselines within this many x-heights


@dataclass
class PageTextLine:
    box: int                           # step 1: the text-layer box it came from ...
    column: int                        # ... its column inside the box
    kind: str                          # 'main' (the box's line) | 'split' (another line inside the box)
    x0: int                            # page columns of the line after step 7
    x1: int
    base: NDArray[np.float64]          # baseline row per column x0..x1-1 (step 3)
    top: NDArray[np.float64]           # outermost boundary, per column (steps 5–6)
    bottom: NDArray[np.float64]
    xh: float
    links: dict[str, int | None] = field(default_factory=dict)   # step 1: up / down / left / right (indices)
    stops: tuple[str, str] = ('box', 'box')                      # step 7: why it stopped left / right


def _fits(gray: NDArray[np.float64], boxes: list[tuple[int, int, int, int]]) -> list[LineFit]:
    mh = float(np.median([b[3] - b[1] for b in boxes])) if boxes else 0.0
    out = []
    for i, b in enumerate(boxes):
        rows = None
        if mh and b[3] - b[1] < THIN * mh:
            c = (b[1] + b[3]) / 2
            rows = (max(0, int(c - WINDOW * mh / 2)), min(gray.shape[0], int(c + WINDOW * mh / 2)))
        out.extend(fit_box(gray, b, None, box_index=i, splits=True, fit_rows=rows))
    # a 'split' line that is another box's line (or a piece of its own box's curved line) is not a new line
    mains = [f for f in out if f.kind == 'main']
    kept = list(mains)
    for f in out:
        if f.kind == 'main':
            continue
        xs = np.arange(f.x0, f.x1, dtype=np.float64)
        if not any(min(g.x1, f.x1) - max(g.x0, f.x0) > 0 and
                   np.median(np.abs(g.base_at(xs) - f.base)) < SAME * f.xh for g in kept):
            kept.append(f)
    return kept


def page_lines(page: Image.Image | NDArray[Any], boxes: list[tuple[int, int, int, int]], *,
               margin: float = .25) -> list[PageTextLine]:
    gray = to_gray(page) if isinstance(page, Image.Image) else np.asarray(page, np.float64)
    H, W = gray.shape
    fits = _fits(gray, boxes)                                            # step 1
    if not fits:
        return []
    xh = float(np.median([f.xh for f in fits]))                          # step 4: the page's font
    up = float(np.median([f.up / f.xh for f in fits])) * xh              # baseline → top font line
    down = float(np.median([f.down / f.xh for f in fits])) * xh          # baseline → bottom font line
    rise = float(np.median([f.rise / f.xh for f in fits])) * xh          # baseline → mean line

    # step 7 (and 3 beyond the box): follow each line's ink sideways
    lab, _ = ndi.label(binarise(gray), structure=EIGHT)
    objs = ndi.find_objects(lab)
    rules = [(sl[1].start, sl[1].stop) for sl in objs if sl is not None
             and sl[0].stop - sl[0].start >= RULE_HEIGHT * xh
             and sl[1].stop - sl[1].start <= RULE_ASPECT * (sl[0].stop - sl[0].start)]
    lines = []
    for f in fits:
        step = max(1, int(xh))
        seed = [(float(x), float(b)) for x, b in zip(np.arange(f.x0, f.x1)[::step], f.base[::step])]
        y0, y1 = int(f.base.min() - up - 1.5 * xh), int(f.base.max() + down + 1.5 * xh)
        near = [sl for sl in objs if sl is not None and sl[0].stop > y0 and sl[0].start < y1]
        x0, sl_, pl = _walk(near, f.x0, -1, xh, rise, rules, seed[:6], (y0, y1)) if f.open_left else (f.x0, 'box', seed[:6])
        x1, sr_, pr = _walk(near, f.x1, +1, xh, rise, rules, seed[-6:], (y0, y1)) if f.open_right else (f.x1, 'box', seed[-6:])
        x0, x1 = int(max(0, x0)), int(min(W, x1))
        xs = np.arange(x0, x1, dtype=np.float64)
        base = f.base_at(xs)
        for pts, side in ((pl, -1), (pr, 1)):                            # the walked letters' baseline beyond the box
            ext = [p for p in pts if (p[0] < f.x0 if side < 0 else p[0] >= f.x1)]
            if ext:
                anchor = (float(f.x0), float(f.base[0])) if side < 0 else (float(f.x1 - 1), float(f.base[-1]))
                px = np.array([anchor[0]] + [p[0] for p in ext]); py = np.array([anchor[1]] + [p[1] for p in ext])
                o = np.argsort(px)
                sel = (xs < f.x0) if side < 0 else (xs >= f.x1)
                base[sel] = np.interp(xs[sel], px[o], py[o])
        lines.append(PageTextLine(f.box_index, f.segment, f.kind, x0, x1, base, base - up - margin * xh,
                                  base + down + margin * xh, xh, stops=(sl_, sr_)))

    def base_at(L: PageTextLine, xs: NDArray[np.float64]) -> NDArray[np.float64]:
        xr = np.arange(L.x0, L.x1, dtype=np.float64)
        return np.interp(xs, xr, L.base)                                 # flat continuation beyond its ends

    # step 1: neighbours. up / down: the nearest line overlapping in x, 1.2–4.5 x-heights away; left / right: the
    # nearest line on the same baseline beside it
    for i, L in enumerate(lines):
        xs = np.arange(L.x0, L.x1, dtype=np.float64)
        for key, sign in (('up', -1), ('down', 1)):
            best = None
            for j, M in enumerate(lines):
                lo, hi = max(L.x0, M.x0), min(L.x1, M.x1)
                if j == i or hi <= lo:
                    continue
                d = float(np.median(base_at(M, xs[(xs >= lo) & (xs < hi)]) - L.base[(xs >= lo) & (xs < hi)]))
                if 1.2 * xh <= sign * d <= 4.5 * xh and (best is None or abs(d) < best[0]):
                    best = (abs(d), j)
            L.links[key] = None if best is None else best[1]
        for key, sign in (('left', -1), ('right', 1)):
            best = None
            for j, M in enumerate(lines):
                if j == i:
                    continue
                gap = (M.x0 - L.x1) if sign > 0 else (L.x0 - M.x1)
                edge = float(L.x1 - 1 if sign > 0 else L.x0)
                if gap < -xh or abs(float(base_at(M, np.array([edge]))[0]) - L.base[-1 if sign > 0 else 0]) > SAME * xh:
                    continue
                if best is None or gap < best[0]:
                    best = (gap, j)
            L.links[key] = None if best is None else best[1]

    # left / right neighbours meet halfway across the gap between them (or halfway across their overlap)
    def trim(A: PageTextLine, a: int, b: int) -> None:
        A.base, A.top, A.bottom = A.base[a - A.x0:b - A.x0], A.top[a - A.x0:b - A.x0], A.bottom[a - A.x0:b - A.x0]
        A.x0, A.x1 = a, b
    for L in lines:
        if L.links.get('right') is None:
            continue
        M = lines[L.links['right']]
        if L.x1 > M.x0:                                                  # overlapping: split the overlap evenly
            mid = (max(L.x0, M.x0) + min(L.x1, M.x1)) // 2
            trim(L, L.x0, mid); trim(M, mid, M.x1)
            L.stops, M.stops = (L.stops[0], 'neighbour'), ('neighbour', M.stops[1])

    # step 6: at every column, the boundary with the neighbour above / below is the middle between the facing font
    # lines (this line's top and the upper line's bottom; this line's bottom and the lower line's top)
    for L in lines:
        xs = np.arange(L.x0, L.x1, dtype=np.float64)
        if L.links.get('up') is not None:
            M = lines[L.links['up']]
            L.top = (L.base - up + base_at(M, xs) + down) / 2
        if L.links.get('down') is not None:
            M = lines[L.links['down']]
            L.bottom = (L.base + down + base_at(M, xs) - up) / 2
    return lines

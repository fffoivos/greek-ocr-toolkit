"""Fix the line geometry of a whole page from its text-layer boxes (owner 8 Oct 18:05–18:40).

fix_page(page, boxes) — one whole-page operation, four steps:
  1. take the page and every text-layer box on it; fit each box's line (four guide lines, curved baseline);
  2. find boxes holding too many lines (a second full line inside, a column rule or a wide unaligned gap) and break
     them into one segment per line; a line already owned by another box is not duplicated;
  3. find where each line is cut off by its box: its own ink continuing past the box's top, bottom, left or right
     edge on the page (measured, not guessed from the crop);
  4. follow the direction of the cut-off: the boundary follows the line's own curve / skew (top and bottom guide lines
     ± margin, bounded by the neighbouring lines' fitted lines — the boxes are used collaboratively: Voronoi of the
     lines' letter-body centre curves, ink assigned per component by its centroid; see _voronoi_keep), and extends
     left / right letter by letter until the page edge, a gap wider than GAP_STOP x-heights, or a column rule.
Lines that are not cut off and share their box with nothing keep their box unchanged.

Lines on a page share their spacing and letter size: page medians are the fallback where a line's own estimate is
missing or off. Output per line: the page region it occupies and a straightened image (the line's baseline made level,
cropped to its own ink ± margin) for OCR.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray
from PIL import Image
from scipy import ndimage as ndi

from greekocr.glyphs.baseline import text_lines
from greekocr.glyphs.columns import column_segments
from greekocr.glyphs.components import EIGHT, binarise, to_gray
from greekocr.glyphs.lines_api import straighten

__all__ = ['LineFit', 'PageLine', 'Recut', 'fit_box', 'fix_page', 'recut_lines', 'recut_page']

GAP_STOP = 3.0        # blank gap (x-heights) that ends the line: word spaces reach p99 1.9 on 444 real crops
RULE_HEIGHT = 2.5     # a vertical rule is at least this many x-heights tall ...
RULE_ASPECT = .15     # ... and at most this wide relative to its height
BASE_TOL = .25        # a letter bottom refits the baseline when within this of the prediction (descenders excluded)
K_LOCAL = 6           # letters in the local baseline fit while walking
SEAM_BIAS = .02       # seam cost per pixel of distance from the mid-gap row (ink costs 1 per pixel crossed)
WINDOW = 4.2          # x-heights above / below the baseline in the straightened working window
SAME_LINE = .5        # a split line within this many x-heights of another box's line is that box's line
THIN_BOX = .8         # a box lower than this × the page's median box height is too thin to fit its line in ...
FIT_WINDOW = 1.5      # ... so its line is fitted in a window this many median box heights tall, centred on it
NEAR_BOXES = 3.5      # with `only`: boxes within this many median box heights (and overlapping in x) are fitted too
LOST_MIN = .15        # a side is cut off when the line's own ink beyond it exceeds this × x-height² pixels


@dataclass
class LineFit:
    """One text line fitted on a text-layer box, in page coordinates."""
    x0: int
    x1: int
    base: NDArray[np.float64]          # baseline row per column x0..x1-1
    xh: float
    rise: float                        # baseline → mean line (pixels)
    up: float                          # baseline → ascender line
    down: float                        # baseline → descender line
    box: tuple[int, int, int, int]
    box_index: int = -1
    kind: str = 'main'                 # 'main' (the box's own line) | 'split' (another full line inside the box)
    segment: int = 0                   # column segment of the box
    n_segments: int = 1
    open_left: bool = True             # the line reaches the box's left / right edge (may continue beyond it)
    open_right: bool = True

    def base_at(self, xs: NDArray[np.float64]) -> NDArray[np.float64]:
        """Baseline at page columns xs; linear continuation with the end slopes beyond the fitted range."""
        xr = np.arange(self.x0, self.x1, dtype=np.float64)
        n = max(2, min(len(xr), int(3 * self.xh)))
        sl = np.polyfit(xr[:n], self.base[:n], 1)[0] if len(xr) >= 2 else 0.0
        sr = np.polyfit(xr[-n:], self.base[-n:], 1)[0] if len(xr) >= 2 else 0.0
        out = np.interp(xs, xr, self.base)
        out = np.where(xs < self.x0, self.base[0] + sl * (xs - self.x0), out)
        return np.where(xs >= self.x1, self.base[-1] + sr * (xs - (self.x1 - 1)), out)


@dataclass
class Recut:
    image: Image.Image                # straightened line, cropped to its own ink ± margin
    mode: str
    x0: int                           # page columns covered
    x1: int
    y0: int                           # page rows spanned by the region
    y1: int
    base: NDArray[np.float64]         # page baseline row per column x0..x1-1
    xh: float
    stop_left: str                    # 'box' (not extended) | 'page_edge' (line ends) | 'gap' | 'rule' | 'edge' (shading)
    stop_right: str
    added_left: int                   # columns added beyond the box
    added_right: int
    added_top: int                    # rows of the region above / below the box
    added_bottom: int
    segment: int
    notes: list[str] = field(default_factory=list)
    erased: NDArray[np.bool_] | None = None    # page pixels the output shows (its region); name kept for callers
    pitch_xh: float | None = None
    up: float = 0.0
    down: float = 0.0

    @property
    def region(self) -> NDArray[np.bool_] | None:
        return self.erased


@dataclass
class PageLine:
    """A line of the page after fix_page."""
    box_index: int                    # text-layer box it came from
    kind: str                         # 'main' | 'split'
    segment: int                      # column segment within the box
    n_segments: int
    cut: dict[str, int]               # own ink pixels beyond the box per side: top / bottom / left / right
    cut_sides: list[str]              # sides over LOST_MIN × x-height²
    fixed: bool                       # boundary changed (cut off, split, or sharing its box)
    reason: list[str]
    recut: Recut                      # region + straightened image (also for unchanged lines)
    box_image: Image.Image | None     # the original box crop, kept as output for unchanged lines


def _walk(objs: list, start_x: float, direction: int, xh: float, rise_mean: float, rules: list[tuple[int, int]],
          seed: list[tuple[float, float]], window: tuple[int, int] = (-1, -1)) -> tuple[float, str, list[tuple[float, float]]]:
    """Follow the line from start_x outward letter by letter. Returns (new edge x, stop reason, baseline points).
    Stops at non-text: a component taller than 3.2 x-heights or filling the whole walking window top to bottom (page-edge
    shading, gutter shadow, stains) ends the line there ('edge')."""
    pts = list(seed)
    edge = start_x
    cand = []
    for sl in objs:
        if sl is None:
            continue
        cx0, cx1, cy0, cy1 = sl[1].start, sl[1].stop, sl[0].start, sl[0].stop
        if (direction > 0 and cx1 <= start_x) or (direction < 0 and cx0 >= start_x):
            continue
        cand.append((cx0, cx1, cy0, cy1))
    cand.sort(key=lambda c: c[0] if direction > 0 else -c[1])

    def predict(x: float) -> float:
        near = sorted(pts, key=lambda p: abs(p[0] - x))[:K_LOCAL]
        xs, ys = np.array([p[0] for p in near]), np.array([p[1] for p in near])
        if len(near) >= 2 and np.ptp(xs) > 0:
            c = np.polyfit(xs, ys, 1)
            if abs(c[0]) < .25:
                return float(np.polyval(c, x))
        return float(np.median(ys))

    for cx0, cx1, cy0, cy1 in cand:
        near_x = cx0 if direction > 0 else cx1
        b = predict((cx0 + cx1) / 2)
        m = b - rise_mean
        ov = min(cy1, b) - max(cy0, m)                         # overlap with the letter-body band (mean → base)
        if ov < min(.5 * xh, .7 * (cy1 - cy0)):                 # letters span the body; dots and commas sit in it;
            continue                                           # neighbours' tails and accents barely touch it
        for r0, r1 in rules:                                   # a rule between the edge and this component
            if (direction > 0 and edge <= r0 <= near_x) or (direction < 0 and near_x <= r1 <= edge):
                return edge, 'rule', pts
        if cy1 - cy0 > 2.6 * xh and (cx1 - cx0) < RULE_ASPECT * (cy1 - cy0):
            return edge, 'rule', pts
        if cy1 - cy0 > 3.2 * xh or (cy0 <= window[0] + 1 and cy1 >= window[1] - 1):
            return edge, 'edge', pts
        gap = (near_x - edge) * direction
        if (cy1 - cy0) < .3 * xh and gap > xh:                 # dots and specks extend the line only next to it
            continue
        if gap > GAP_STOP * xh:
            return edge, 'gap', pts
        edge = max(edge, cx1) if direction > 0 else min(edge, cx0)
        if abs(cy1 - b) <= BASE_TOL * xh + 1 and (cy1 - cy0) >= .5 * xh:
            pts.append(((cx0 + cx1) / 2, float(cy1)))
    return edge, 'page_edge', pts      # no more line ink before the page edge: stop at the last letter


def _seam(ink: NDArray[np.bool_], lo: NDArray[np.int64] | int, hi: NDArray[np.int64] | int,
          mid: NDArray[np.float64] | float) -> NDArray[np.int64]:
    """Minimum-ink path left → right (one row step per column) inside per-column bounds lo..hi, biased toward `mid`."""
    h, w = ink.shape
    lo = np.clip(np.broadcast_to(np.asarray(lo, np.int64), (w,)), 0, h - 1)
    hi = np.clip(np.broadcast_to(np.asarray(hi, np.int64), (w,)), 0, h - 1)
    hi = np.maximum(hi, lo)
    mid = np.broadcast_to(np.asarray(mid, np.float64), (w,))
    rows = np.arange(h)[:, None]
    cost = ink.astype(np.float64) + SEAM_BIAS * np.abs(rows - mid[None, :])
    cost[(rows < lo[None, :]) | (rows > hi[None, :])] = np.inf
    acc = cost[:, 0].copy()
    back = np.zeros(cost.shape, np.int8)
    for c in range(1, w):
        upv = np.r_[np.inf, acc[:-1]]
        dnv = np.r_[acc[1:], np.inf]
        stack = np.vstack([upv, acc, dnv])
        k = stack.argmin(axis=0)
        acc = stack[k, np.arange(h)] + cost[:, c]
        back[:, c] = k - 1
    if not np.isfinite(acc).any():                          # bounds jump more than one row per column: fall back
        return np.round((lo + hi) / 2).astype(np.int64)
    path = np.empty(w, np.int64)
    r = int(np.argmin(acc))
    for c in range(w - 1, -1, -1):
        path[c] = r
        r = int(np.clip(r + int(back[r, c]), 0, h - 1))
    return path


def _voronoi_keep(ink: NDArray[np.bool_], miss: NDArray[np.bool_], c0: float, c_up: NDArray[np.float64],
                  c_dn: NDArray[np.float64], rise: float) -> NDArray[np.bool_]:
    """Pixels of this line in a window straightened along it (owner 8 Oct 18:58: "the curve and the distance from the
    centroid of the letters should define the region"). Voronoi of the lines' letter-body centre curves: the region is
    everything nearer this line's centre (row c0) than the neighbours' (c_up / c_dn per column) — between two lines,
    the midline of their centre curves. Ink is assigned per connected component: a component goes whole to the line
    whose centre is nearest its centroid (accents and tall tops across the midline stay with their line; tails belong
    to their letter). Only a component touching two lines' letter bodies is cut at the midline."""
    h, w = ink.shape
    rows = np.arange(h)[:, None]
    m_up, m_dn = (c0 + c_up) / 2, (c0 + c_dn) / 2
    band = (rows > m_up[None, :]) & (rows < m_dn[None, :]) & ~miss
    keep = band.copy()
    lab, n = ndi.label(ink, structure=EIGHT)
    if n == 0:
        return keep
    half = rise / 2
    for i, sl in enumerate(ndi.find_objects(lab), start=1):
        if sl is None:
            continue
        m = lab[sl] == i
        rr, cc = np.nonzero(m)
        rr = rr + sl[0].start; cc = cc + sl[1].start
        cy = rr.mean()
        d_own = abs(cy - c0)
        d_up = abs(cy - c_up[cc].mean())
        d_dn = abs(cy - c_dn[cc].mean())
        in_own = ((rr >= c0 - half) & (rr <= c0 + half)).any()
        if d_own <= min(d_up, d_dn):                        # ours: keep whole, unless it touches a neighbour's body
            touch = ((rr <= c_up[cc] + half) | (rr >= c_dn[cc] - half)).any()
            if not touch:
                keep[rr, cc] = True
        else:                                               # a neighbour's: drop, unless it touches our body
            if not in_own:
                keep[rr, cc] = False
    return keep


def _guide_offsets(L: Any) -> tuple[float, float, float]:
    """(rise, up, down) in pixels from a GuideLines' curves over its evidence range."""
    s = slice(L.x0, max(L.x0 + 1, L.x1))
    return (float(np.median((L.base - L.mean)[s])), float(np.median((L.base - L.ascender)[s])),
            float(np.median((L.descender - L.base)[s])))


def _body_in_box(L: Any, rise: float, y0: int, y1: int, x0: int, x1: int) -> float:
    """Mean fraction of a line's letter body (baseline − rise → baseline) inside rows y0..y1, over columns x0..x1."""
    if x1 <= x0 or rise <= 0:
        return 0.0
    b = np.asarray(L.base[x0:x1], np.float64)
    top = b - rise
    ov = np.clip(np.minimum(b, y1) - np.maximum(top, y0), 0, None)
    return float((ov / rise).mean())


def fit_box(gray: NDArray[np.float64], box: tuple[int, int, int, int], xh_prior: float | None = None, *,
            box_index: int = -1, splits: bool = True, fit_rows: tuple[int, int] | None = None) -> list[LineFit]:
    """Step 1–2 for one box: the box's own line per column segment ('main'), and — when `splits` — every other full
    line found inside the box ('split': letter bodies at least half inside, as report.n_full_lines counts them).
    fit_rows: fit in these page rows instead of the box's own (a box too thin to fit its line in: the line is then
    the one whose letter bodies overlap the box most, and only lines with ≥ half their bodies inside the box split)."""
    bx0, by0, bx1, by1 = box
    wy0, wy1 = fit_rows if fit_rows else (by0, by1)
    crop = Image.fromarray(np.clip(gray[wy0:wy1, bx0:bx1], 0, 255).astype(np.uint8), 'L')
    segs = column_segments(crop, **({'xh_prior': xh_prior} if xh_prior else {}))
    out = []
    for k, seg in enumerate(segs):
        g = seg.glyphs
        if g is None:
            continue
        lines = text_lines(g)
        if fit_rows:
            scored = []
            for L in lines:
                rise, _, _ = _guide_offsets(L)
                ex0, ex1 = (0, g.width) if L.side == 'main' else (L.x0, L.x1)
                scored.append((_body_in_box(L, rise, by0 - wy0, by1 - wy0, ex0, ex1), L))
            own = max(scored, key=lambda t: t[0])
            chosen = [(own[1], 'main')] + [(L, 'split') for f, L in scored
                                            if L is not own[1] and f >= .5 and L.x1 - L.x0 >= 2 * g.band.xh]
        else:
            chosen = [(L, 'main' if L.side == 'main' else 'split') for L in lines
                      if L.side == 'main' or (splits and L.visible >= .5 and L.x1 - L.x0 >= 2 * g.band.xh)]
        for L, kind in chosen:
            if kind == 'split' and not splits:
                continue
            rise, up, down = _guide_offsets(L)
            if kind == 'main':
                lx0, lx1, base = seg.x0, seg.x1, L.base
            else:                                              # its evidence range only
                lx0, lx1, base = seg.x0 + L.x0, seg.x0 + L.x1, L.base[L.x0:L.x1]
            out.append(LineFit(bx0 + lx0, bx0 + lx1, np.asarray(base, np.float64) + wy0, g.band.xh, rise, up, down,
                               box, box_index, kind, k, len(segs),
                               open_left=(lx0 <= int(g.band.xh)) if kind != 'main' else seg.x0 == 0,
                               open_right=(lx1 >= (bx1 - bx0) - int(g.band.xh)) if kind != 'main'
                               else bx0 + seg.x1 >= bx1))
    return out


def _neighbour(fits: list[LineFit], xs: NDArray[np.float64], base: NDArray[np.float64], xh: float,
               side: int) -> tuple[LineFit, NDArray[np.float64]] | None:
    """The nearest fitted line on `side` (−1 above, +1 below) whose x-range overlaps this one by ≥ 2 x-heights, with
    its baseline offset per column (inside its range from its own fit; outside, its median offset: shared geometry)."""
    best = None
    for f in fits:
        lo, hi = max(f.x0, int(xs[0])), min(f.x1, int(xs[-1]) + 1)
        if hi - lo < 2 * xh:
            continue
        sel = (xs >= lo) & (xs < hi)
        off = f.base_at(xs[sel]) - base[sel]
        med = float(np.median(off))
        if not (1.2 * xh <= side * med <= 4.5 * xh):
            continue
        if best is None or abs(med) < abs(best[2]):
            inside = (xs >= f.x0) & (xs < f.x1)
            best = (f, np.where(inside, f.base_at(xs) - base, med), med)
    return None if best is None else (best[0], best[1])


def _line_pitch(ink: NDArray[np.bool_], base_row: int, xh: float, rise: float) -> tuple[float | None, bool, bool]:
    """Fallback without neighbouring boxes: line pitch from the autocorrelation of the row-ink profile of the window
    straightened along this line (the first peak beyond 1.4 x-heights), and per side whether a neighbour's letter
    bodies sit there (density ≥ a third of this line's body)."""
    prof = ink.mean(axis=1).astype(np.float64)
    r = max(1, int(round(rise)))
    own = prof[max(0, base_row - r):base_row].mean() if base_row > 0 else 0.0
    if own <= 0:
        return None, False, False
    x = prof - prof.mean()
    ac = np.correlate(x, x, mode='full')[len(x) - 1:]
    ac = ac / (ac[0] if ac[0] > 0 else 1)
    lo, hi = int(1.4 * xh), min(len(ac) - 2, int(4.0 * xh))
    peaks = [k for k in range(max(1, lo), hi) if ac[k] >= ac[k - 1] and ac[k] >= ac[k + 1] and ac[k] > .1]
    if not peaks:
        return None, False, False
    P = float(peaks[0])
    up, dn = _sides_at(ink, base_row, xh, rise, P)
    return P, up, dn


def _sides_at(ink: NDArray[np.bool_], base_row: int, xh: float, rise: float, P: float) -> tuple[bool, bool]:
    prof = ink.mean(axis=1).astype(np.float64)
    r = max(1, int(round(rise)))
    own = prof[max(0, base_row - r):base_row].mean() if base_row > 0 else 0.0

    def dens(sign: int) -> float:
        best = 0.0
        for d in range(-int(.25 * xh), int(.25 * xh) + 1):
            b = int(round(base_row + sign * P)) + d
            if b - r >= 0 and b <= len(prof):
                best = max(best, float(prof[b - r:b].mean()))
        return best
    return (own > 0 and dens(-1) >= own / 3), (own > 0 and dens(1) >= own / 3)


def _recut_fit(gray: NDArray[np.float64], f: LineFit, *, neighbours: list[LineFit] | None = None,
               pitch_xh: float | None = None, page_xh: float | None = None, mode: str = 'curve',
               margin: float = .25, extend: bool = True, isolate: bool = True, separator: str = 'voronoi') -> Recut:
    """Step 4 for one fitted line: follow its geometry on the page (walk left / right; top and bottom guide lines ±
    margin, bounded by the neighbours' fitted lines by minimum-ink seams)."""
    H, W = gray.shape
    bx0, by0, bx1, by1 = f.box
    xh, rise, up, down = f.xh, f.rise, f.up, f.down
    notes: list[str] = []
    if page_xh and abs(xh / page_xh - 1) > .25:              # lines on a page share their letter size
        k = page_xh / xh
        notes.append(f'own x-height {xh:.1f} px off the page median {page_xh:.1f}: page value used')
        xh, rise, up, down = page_xh, rise * k, up * k, down * k
    xs_seg = np.arange(f.x0, f.x1, dtype=np.float64)
    step = max(1, int(xh))
    seed = [(float(x), float(b)) for x, b in zip(xs_seg[::step], f.base[::step])]
    stop_l = stop_r = 'box'
    new_x0, new_x1 = f.x0, f.x1
    pts_l, pts_r = seed[:K_LOCAL], seed[-K_LOCAL:]
    if extend and (f.open_left or f.open_right):
        ry0 = max(0, int(f.base.min() - up - 1.5 * xh))
        ry1 = min(H, int(f.base.max() + down + 1.5 * xh))
        lab, _ = ndi.label(binarise(gray[ry0:ry1]), structure=EIGHT)
        objs = [None if sl is None else (slice(sl[0].start + ry0, sl[0].stop + ry0), sl[1])
                for sl in ndi.find_objects(lab)]
        rules = [(sl[1].start, sl[1].stop) for sl in objs if sl is not None
                 and sl[0].stop - sl[0].start >= RULE_HEIGHT * xh
                 and sl[1].stop - sl[1].start <= RULE_ASPECT * (sl[0].stop - sl[0].start)]
        if f.open_left:
            new_x0, stop_l, pts_l = _walk(objs, f.x0, -1, xh, rise, rules, pts_l, (ry0, ry1))
        if f.open_right:
            new_x1, stop_r, pts_r = _walk(objs, f.x1, +1, xh, rise, rules, pts_r, (ry0, ry1))
        new_x0, new_x1 = int(max(0, new_x0)), int(min(W, new_x1))
    xs = np.arange(new_x0, new_x1, dtype=np.float64)
    base = np.interp(xs, xs_seg, f.base)
    for pts, side in ((pts_l, -1), (pts_r, 1)):              # beyond the box: the walked letters' baseline points
        ext = [p for p in pts if (p[0] < f.x0 if side < 0 else p[0] >= f.x1)]
        if not ext:
            continue
        anchor = (float(f.x0), float(f.base[0])) if side < 0 else (float(f.x1 - 1), float(f.base[-1]))
        px = np.array([anchor[0]] + [p[0] for p in ext])
        py = np.array([anchor[1]] + [p[1] for p in ext])
        o = np.argsort(px)
        sel = (xs < f.x0) if side < 0 else (xs >= f.x1)
        base[sel] = np.interp(xs[sel], px[o], py[o])
    a = int(round(margin * xh))
    paper = float(np.percentile(gray[by0:by1, bx0:bx1], 90))
    # a tall window straightened along this line: the neighbours share its geometry, so they come out straight too
    S, miss, br = straighten(gray[:, new_x0:new_x1], base, xh, paper=paper, above=WINDOW, below=WINDOW)
    sink = binarise(S) & ~miss
    seams = {}
    centre: dict[int, NDArray[np.float64]] = {}           # neighbour letter-body centre rows per column, per side
    P0, has_up, has_dn = (None, False, False)
    for side in (-1, 1):
        nb = _neighbour(neighbours, xs, base, xh, side) if (isolate and neighbours) else None
        if nb is not None:        # the neighbour's own fitted line bounds this one (boxes used collaboratively)
            g, off = nb
            if side < 0:          # between the line above's baseline and this line's mean line
                lo = np.round(br + off + .05 * xh).astype(np.int64)
                hi = np.full(len(off), int(br - rise - .05 * xh))
            else:                 # between this line's baseline and the line below's mean line
                lo = np.full(len(off), int(br + .05 * xh))
                hi = np.round(br + off - g.rise - .05 * g.xh).astype(np.int64)
            seams[side] = _seam(sink, lo, hi, (lo + hi) / 2)
            centre[side] = br + off - g.rise / 2
            notes.append(f"{'above' if side < 0 else 'below'}: neighbour line at {np.median(off) / xh:+.2f} x-heights")
            continue
        if isolate and P0 is None:
            if pitch_xh is not None:
                P0 = pitch_xh * xh
                has_up, has_dn = _sides_at(sink, br, xh, rise, P0)
            else:
                P0, has_up, has_dn = _line_pitch(sink, br, xh, rise)
        P = P0 if (has_up if side < 0 else has_dn) else None
        if P is None:             # nothing there: the guide band (a virtual neighbour whose midline is the band edge)
            lim = br - int(round(up)) - a if side < 0 else br + int(round(down)) + a
            seams[side] = np.full(S.shape[1], lim)
            centre[side] = np.full(S.shape[1], 2.0 * lim - (br - rise / 2))
            continue
        if side < 0:
            lo, hi = int(br - P + .05 * xh), int(br - rise - .05 * xh)
        else:
            lo, hi = int(br + .05 * xh), int(br + P - rise - .05 * xh)
        seams[side] = _seam(sink, lo, hi, (lo + hi) / 2)
        centre[side] = np.full(S.shape[1], br + side * P - rise / 2)
        notes.append(f"{'above' if side < 0 else 'below'}: page pitch {P / xh:.2f} x-heights")
    rows = np.arange(S.shape[0])[:, None]
    if separator == 'voronoi':
        keep = _voronoi_keep(sink, miss, br - rise / 2, centre[-1], centre[1], rise)
    else:
        keep = (rows > seams[-1][None, :]) & (rows < seams[1][None, :]) & ~miss
    S2 = np.where(keep, S, paper)
    rr = np.nonzero((binarise(S2) & keep).any(axis=1))[0]
    t0 = max(0, int(rr[0] - a)) if rr.size else 0
    t1 = min(S.shape[0], int(rr[-1] + 1 + a)) if rr.size else S.shape[0]
    region = np.zeros(gray.shape, bool)
    for c in range(S.shape[1]):
        ks = np.nonzero(keep[t0:t1, c])[0] + t0
        if ks.size:
            region[np.clip(np.round(base[c] + ks - br).astype(int), 0, H - 1), new_x0 + c] = True
    ys_r = np.nonzero(region.any(axis=1))[0]
    y0, y1 = (int(ys_r.min()), int(ys_r.max()) + 1) if ys_r.size else (by0, by1)
    if mode == 'box':
        win = gray[y0:y1, new_x0:new_x1].copy()
        win[~region[y0:y1, new_x0:new_x1]] = paper
        img = Image.fromarray(np.clip(win, 0, 255).astype(np.uint8), 'L')
    else:
        img = Image.fromarray(np.clip(S2[t0:t1], 0, 255).astype(np.uint8), 'L')
    return Recut(img, mode, new_x0, new_x1, y0, y1, base, xh, stop_l, stop_r, f.x0 - new_x0, new_x1 - f.x1,
                 max(0, by0 - y0), max(0, y1 - by1), f.segment, notes, region,
                 None if P0 is None else P0 / xh, up + a, down + a)


def _page_fits(gray: NDArray[np.float64], boxes: list[tuple[int, int, int, int]], *, xh_prior: float | None = None,
               splits: bool = True, use: set[int] | None = None) -> tuple[list[LineFit], float | None, float | None, list[str]]:
    """Steps 1–2 for the page: fit every box (or the boxes in `use`), keep split lines no other box owns, page letter
    size and pitch."""
    hs = [b[3] - b[1] for b in boxes]
    mh = float(np.median(hs)) if hs else 0.0

    def rows_for(b: tuple[int, int, int, int]) -> tuple[int, int] | None:
        if not mh or b[3] - b[1] >= THIN_BOX * mh:
            return None
        c = (b[1] + b[3]) / 2                                # a box too thin to fit its line in: fit in a window
        return max(0, int(c - FIT_WINDOW * mh / 2)), min(gray.shape[0], int(c + FIT_WINDOW * mh / 2))
    fits = [f for i, b in enumerate(boxes) if use is None or i in use
            for f in fit_box(gray, b, xh_prior, box_index=i, splits=splits, fit_rows=rows_for(b))]
    mains = [f for f in fits if f.kind == 'main']
    log = []
    kept = list(mains)
    for f in fits:
        if f.kind != 'split':
            continue
        xs = np.arange(f.x0, f.x1, dtype=np.float64)
        owned = False
        for g in kept:                     # any main line (its own box's included: pieces of a curved line) or split
            lo, hi = max(f.x0, g.x0), min(f.x1, g.x1)
            if hi - lo >= 2 * f.xh and np.median(np.abs(g.base_at(xs[(xs >= lo) & (xs < hi)])
                                                        - f.base[(xs >= lo) & (xs < hi)])) < SAME_LINE * f.xh:
                owned = True
                break
        if not owned:
            kept.append(f)
            log.append(f'box {f.box_index}: second line inside with no box of its own → split')
    page_xh = float(np.median([f.xh for f in kept])) if len(kept) >= 3 else None
    if page_xh:
        for f in kept:                                       # off-size fits take the page letter size
            if abs(f.xh / page_xh - 1) > .25:
                k = page_xh / f.xh
                f.xh, f.rise, f.up, f.down = page_xh, f.rise * k, f.up * k, f.down * k
    offs = []
    for f in kept:
        nb = _neighbour([g for g in kept if g is not f], np.arange(f.x0, f.x1, dtype=np.float64), f.base, f.xh, 1)
        if nb is not None:
            offs.append(float(np.median(nb[1])) / f.xh)
    pitch = float(np.median(offs)) if len(offs) >= 3 else None
    return kept, page_xh, pitch, log


def fix_page(page: Image.Image | NDArray[Any], boxes: list[tuple[int, int, int, int]], *,
             only: set[int] | None = None, xh_prior: float | None = None, margin: float = .25,
             mode: str = 'curve', separator: str = 'voronoi') -> list[PageLine]:
    """The whole-page operation (module docstring): every text-layer box of a page in, every text line out.
    `only`: indices of the boxes whose lines to return (all boxes are still fitted and bound their neighbours)."""
    gray = to_gray(page) if isinstance(page, Image.Image) else np.asarray(page, np.float64)
    use = None
    if only is not None:                                   # fit only the targets and the boxes that can bound them
        hs = [b[3] - b[1] for b in boxes]
        reach = NEAR_BOXES * float(np.median(hs)) if hs else 0.0
        use = set(only)
        for i in only:
            tx0, ty0, tx1, ty1 = boxes[i]
            for j, (x0, y0, x1, y1) in enumerate(boxes):
                if min(x1, tx1) > max(x0, tx0) and abs((y0 + y1) / 2 - (ty0 + ty1) / 2) <= reach:
                    use.add(j)
    fits, page_xh, pitch, log = _page_fits(gray, boxes, xh_prior=xh_prior, use=use)
    per_box: dict[int, list[LineFit]] = {}
    for f in fits:
        per_box.setdefault(f.box_index, []).append(f)
    out = []
    for f in fits:
        if only is not None and f.box_index not in only:
            continue
        rc = _recut_fit(gray, f, neighbours=[g for g in fits if g is not f], pitch_xh=pitch, page_xh=page_xh,
                        mode=mode, margin=margin, separator=separator)
        bx0, by0, bx1, by1 = f.box
        own = binarise(gray[rc.y0:rc.y1, rc.x0:rc.x1]) & rc.region[rc.y0:rc.y1, rc.x0:rc.x1]
        ys, xs = np.nonzero(own)
        ys, xs = ys + rc.y0, xs + rc.x0
        cut = dict(top=int((ys < by0).sum()), bottom=int((ys >= by1).sum()),
                   left=int((xs < bx0).sum()), right=int((xs >= bx1).sum()))
        sides = [s for s, v in cut.items() if v > LOST_MIN * rc.xh ** 2]
        reason = []
        if f.kind == 'split':
            reason.append('second line inside another box')
        if len(per_box.get(f.box_index, [])) > 1:
            reason.append(f'box holds {len(per_box[f.box_index])} line segments')
        if sides:
            reason.append('cut off: ' + ', '.join(sides))
        fixed = bool(reason)
        box_img = None if fixed else Image.fromarray(np.clip(gray[by0:by1, bx0:bx1], 0, 255).astype(np.uint8), 'L')
        rc.notes.extend(log if f.kind == 'split' else [])
        out.append(PageLine(f.box_index, f.kind, f.segment, f.n_segments, cut, sides, fixed, reason, rc, box_img))
    return out


def recut_lines(page: Image.Image | NDArray[Any], box: tuple[int, int, int, int], *, mode: str = 'curve',
                margin: float = .25, extend: bool = True, isolate: bool = True, xh_prior: float | None = None,
                neighbours: list[LineFit] | None = None, pitch_xh: float | None = None,
                page_xh: float | None = None) -> list[Recut]:
    """One box on its own: one Recut per column segment's main line (no page context unless `neighbours` given)."""
    gray = to_gray(page) if isinstance(page, Image.Image) else np.asarray(page, np.float64)
    return [_recut_fit(gray, f, neighbours=neighbours, pitch_xh=pitch_xh, page_xh=page_xh, mode=mode, margin=margin,
                       extend=extend, isolate=isolate)
            for f in fit_box(gray, box, xh_prior, splits=False)]


def recut_page(page: Image.Image | NDArray[Any], boxes: list[tuple[int, int, int, int]], *,
               only: set[int] | None = None, **kw: Any) -> list[list[Recut]]:
    """Per box, the Recuts of its lines from fix_page (main lines first, then split lines)."""
    lines = fix_page(page, boxes, only=only, **{k: v for k, v in kw.items() if k in ('xh_prior', 'margin', 'mode', 'separator')})
    out: list[list[Recut]] = [[] for _ in boxes]
    for pl in sorted(lines, key=lambda p: (p.kind != 'main', p.segment)):
        out[pl.box_index].append(pl.recut)
    return out

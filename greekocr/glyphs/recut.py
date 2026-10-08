"""Recut lines from their PAGE along the geometry fitted on their text-layer boxes (owner 8 Oct 18:05–18:25).

Entry point: recut_page(page, boxes) — all text-layer boxes of a page; every box is fitted first and each line is
bounded by its neighbours' own fitted lines ("use these boundaries collaboratively"); lines on a page share their
spacing and letter size (consensus fallbacks). recut_lines(page, box) recuts one line on its own.

The crop (a text-layer box) only says where to look. On the crop we fit the line's four guide lines; on the page we
  1. follow the baseline curve outward, letter by letter, beyond the crop's left/right edges, and stop at the page
     edge, at a blank gap wider than GAP_STOP x-heights, or at a vertical rule (column boundary);
  2. cut vertically so the top (ascender) and bottom (descender) guide lines fit, either
       mode='curve': straightened along the baseline, band = guide lines ± margin, or
       mode='box'  : the axis-aligned box from the highest top line to the lowest bottom line ± margin.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = ['LineFit', 'Recut', 'fit_box', 'recut_lines', 'recut_page']

import numpy as np
from numpy.typing import NDArray
from PIL import Image
from scipy import ndimage as ndi

from greekocr.glyphs.columns import column_segments
from greekocr.glyphs.components import EIGHT, binarise, to_gray
from greekocr.glyphs.baseline import text_lines
from greekocr.glyphs.lines_api import straighten

GAP_STOP = 3.0        # blank gap (x-heights) that ends the line: word spaces reach p99 1.9 on 444 real crops
RULE_HEIGHT = 2.5     # a vertical rule is at least this many x-heights tall ...
RULE_ASPECT = .15     # ... and at most this wide relative to its height
BAND_TOL = .35        # a letter continues the line when its body overlaps [mean − tol, base + tol] x-heights
BASE_TOL = .25        # a letter bottom refits the baseline when within this of the prediction (descenders excluded)
K_LOCAL = 6           # letters in the local baseline fit while walking


@dataclass
class Recut:
    image: Image.Image
    mode: str
    x0: int                          # page columns covered
    x1: int
    y0: int                          # page rows of the cut (box mode; curve mode: bounding rows of the band)
    y1: int
    base: NDArray[np.float64]        # page baseline row per column x0..x1-1
    xh: float
    stop_left: str                   # 'crop' (not extended: segment interior) | 'page_edge' | 'gap' | 'rule'
    stop_right: str
    added_left: int                  # columns added beyond the crop
    added_right: int
    added_top: int                   # rows added above / below the crop box (box mode extent)
    added_bottom: int
    segment: int
    notes: list[str] = field(default_factory=list)
    erased: NDArray[np.bool_] | None = None   # page pixels the output shows (its region)
    pitch_xh: float | None = None              # line pitch used for the seams, in x-heights
    up: float = 0.0                            # baseline → band top / bottom, pixels (incl. margin)
    down: float = 0.0


def _walk(ink_lab: NDArray[np.int32], objs: list, base0: tuple[float, float], start_x: float, direction: int,
          xh: float, rise_mean: float, page_w: int, rules: list[tuple[int, int]],
          seed: list[tuple[float, float]]) -> tuple[float, str, list[tuple[float, float]]]:
    """Walk from start_x outward. Returns (new edge x, stop reason, accepted baseline points)."""
    pts = list(seed)
    edge = start_x
    cand = []
    for i, sl in enumerate(objs, start=1):
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
        gap = (near_x - edge) * direction
        small = (cy1 - cy0) < .3 * xh
        if small and gap > xh:                                 # dots and specks extend the line only next to it
            continue
        if gap > GAP_STOP * xh:
            return edge, 'gap', pts
        edge = max(edge, cx1) if direction > 0 else min(edge, cx0)
        if abs(cy1 - b) <= BASE_TOL * xh + 1 and (cy1 - cy0) >= .5 * xh:
            pts.append(((cx0 + cx1) / 2, float(cy1)))
    return edge, 'page_edge', pts      # no more line ink before the page edge: stop at the last letter


SEAM_BIAS = .02      # cost per pixel of distance from the mid-gap row (ink costs 1 per pixel crossed)


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
    acc = cost[:, 0].copy(); back = np.zeros(cost.shape, np.int8)
    for c in range(1, w):
        upv = np.r_[np.inf, acc[:-1]]; dnv = np.r_[acc[1:], np.inf]
        stack = np.vstack([upv, acc, dnv]); k = stack.argmin(axis=0)
        acc = stack[k, np.arange(h)] + cost[:, c]; back[:, c] = k - 1
    if not np.isfinite(acc).any():                          # bounds jump more than one row per column: fall back
        return np.round((lo + hi) / 2).astype(np.int64)
    path = np.empty(w, np.int64); r = int(np.argmin(acc))
    for c in range(w - 1, -1, -1):
        path[c] = r; r = int(np.clip(r + back[r, c], 0, h - 1))
    return path


@dataclass
class LineFit:
    """A line fitted on its own text-layer box, in page coordinates."""
    x0: int
    x1: int
    base: NDArray[np.float64]          # baseline row per column x0..x1-1
    xh: float
    rise: float                        # baseline → mean line (pixels)
    up: float                          # baseline → ascender line
    down: float                        # baseline → descender line
    box: tuple[int, int, int, int]

    def base_at(self, xs: NDArray[np.float64]) -> NDArray[np.float64]:
        """Baseline at page columns xs; linear continuation with the end slopes beyond the fitted range."""
        xr = np.arange(self.x0, self.x1, dtype=np.float64)
        n = max(2, min(len(xr), int(3 * self.xh)))
        sl = np.polyfit(xr[:n], self.base[:n], 1)[0] if len(xr) >= 2 else 0.0
        sr = np.polyfit(xr[-n:], self.base[-n:], 1)[0] if len(xr) >= 2 else 0.0
        out = np.interp(xs, xr, self.base)
        out = np.where(xs < self.x0, self.base[0] + sl * (xs - self.x0), out)
        return np.where(xs >= self.x1, self.base[-1] + sr * (xs - (self.x1 - 1)), out)


def fit_box(gray: NDArray[np.float64], box: tuple[int, int, int, int], xh_prior: float | None = None) -> list[LineFit]:
    """Fit the main line of every column segment of page[box]; page coordinates."""
    bx0, by0, bx1, by1 = box
    crop = Image.fromarray(np.clip(gray[by0:by1, bx0:bx1], 0, 255).astype(np.uint8), 'L')
    out = []
    for seg in column_segments(crop, **({'xh_prior': xh_prior} if xh_prior else {})):
        g = seg.glyphs
        if g is None:
            continue
        main = [L for L in text_lines(g) if L.side == 'main']
        if not main:
            continue
        L = main[0]
        out.append(LineFit(bx0 + seg.x0, bx0 + seg.x1, L.base + by0, g.band.xh,
                           float(np.median(L.base - L.mean)), float(np.median(L.base - L.ascender)),
                           float(np.median(L.descender - L.base)), box))
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
            full = np.where(inside, f.base_at(xs) - base, med)
            best = (f, full, med)
    return None if best is None else (best[0], best[1])


def _line_pitch(ink: NDArray[np.bool_], base_row: int, xh: float, rise: float) -> tuple[float | None, bool, bool]:
    """Line pitch from the autocorrelation of the row-ink profile of a window straightened along this line (lines on a
    page repeat at one spacing): the first autocorrelation peak beyond 1.4 x-heights. Then, per side, whether a
    neighbour's letter bodies sit there (density ≥ a third of this line's body, best within ±0.25 x-heights)."""
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

    def side_density(sign: int) -> float:
        best = 0.0
        for d in range(-int(.25 * xh), int(.25 * xh) + 1):
            b = int(round(base_row + sign * P)) + d
            if b - r >= 0 and b <= len(prof):
                best = max(best, float(prof[b - r:b].mean()))
        return best
    return P, side_density(-1) >= own / 3, side_density(1) >= own / 3


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


def recut_page(page: Image.Image | NDArray[Any], boxes: list[tuple[int, int, int, int]], **kw: Any) -> list[list[Recut]]:
    """Recut every line of a page collaboratively: every text-layer box is fitted first; each line is then bounded by
    its neighbours' own fitted lines (seams between their baselines and this line's mean line, and vice versa). Sides
    with no neighbouring box fall back to the page's line pitch (median of adjacent fitted lines: lines on a page share
    their spacing), checked against the ink."""
    gray = to_gray(page) if isinstance(page, Image.Image) else np.asarray(page, np.float64)
    fits = [fit_box(gray, b, kw.get('xh_prior')) for b in boxes]
    flat = [f for fs in fits for f in fs]
    offs = []
    for f in flat:
        xs = np.arange(f.x0, f.x1, dtype=np.float64)
        nb = _neighbour([g for g in flat if g is not f], xs, f.base, f.xh, 1)
        if nb is not None:
            offs.append(float(np.median(nb[1])) / f.xh)
    pitch = float(np.median(offs)) if len(offs) >= 3 else None
    page_xh = float(np.median([f.xh for f in flat])) if len(flat) >= 3 else None
    for f in flat:                                           # neighbours with an off-size fit take the page size too
        if page_xh and abs(f.xh / page_xh - 1) > .25:
            k = page_xh / f.xh
            f.xh, f.rise, f.up, f.down = page_xh, f.rise * k, f.up * k, f.down * k
    out = []
    for b, fs in zip(boxes, fits):
        others = [f for f in flat if f.box != b]
        out.append(recut_lines(gray, b, neighbours=others, pitch_xh=pitch, page_xh=page_xh, **kw))
    return out


def recut_lines(page: Image.Image | NDArray[Any], box: tuple[int, int, int, int], *, mode: str = 'curve',
                margin: float = .25, extend: bool = True, isolate: bool = True,
                xh_prior: float | None = None, pitch_xh: float | None = None,
                neighbours: list[LineFit] | None = None, page_xh: float | None = None) -> list[Recut]:
    """One Recut per column segment's main line of the crop page[box] (x0, y0, x1, y1, exclusive ends)."""
    gray = to_gray(page) if isinstance(page, Image.Image) else np.asarray(page, np.float64)
    H, W = gray.shape
    bx0, by0, bx1, by1 = box
    crop = Image.fromarray(np.clip(gray[by0:by1, bx0:bx1], 0, 255).astype(np.uint8), 'L')
    kw = {'xh_prior': xh_prior} if xh_prior else {}
    segs = column_segments(crop, **kw)
    out: list[Recut] = []
    for k, seg in enumerate(segs):
        g = seg.glyphs
        if g is None:
            continue
        main = [L for L in text_lines(g) if L.side == 'main']
        if not main:
            continue
        L = main[0]
        xh = g.band.xh
        # guide offsets relative to the baseline, from the crop fit
        up = float(np.median(L.base - L.ascender)); rise = float(np.median(L.base - L.mean))
        down = float(np.median(L.descender - L.base))
        notes: list[str] = []
        if page_xh and abs(xh / page_xh - 1) > .25:          # lines on a page share their letter size
            f = page_xh / xh
            notes.append(f'own x-height {xh:.1f} px off the page median {page_xh:.1f}: page value used')
            xh, up, rise, down = page_xh, up * f, rise * f, down * f
        sx0, sx1 = bx0 + seg.x0, bx0 + seg.x1                  # segment columns on the page
        base_page = L.base + by0                               # per column of the segment
        xs_seg = np.arange(sx0, sx1, dtype=np.float64)
        seed = [(float(x), float(b)) for x, b in zip(xs_seg[::max(1, int(xh))], base_page[::max(1, int(xh))])]
        stop_l = stop_r = 'crop'
        new_x0, new_x1 = sx0, sx1
        pts_l, pts_r = seed[:K_LOCAL], seed[-K_LOCAL:]
        if extend:
            # page band to walk in: rows around the line, extrapolated generously
            ry0 = max(0, int(base_page.min() - up - 1.5 * xh)); ry1 = min(H, int(base_page.max() + down + 1.5 * xh))
            band = gray[ry0:ry1]
            ink = binarise(band)
            lab, _ = ndi.label(ink, structure=EIGHT)
            objs = ndi.find_objects(lab)
            objs_page = [None if sl is None else (slice(sl[0].start + ry0, sl[0].stop + ry0), sl[1]) for sl in objs]
            rules = []
            for sl in objs_page:
                if sl is None:
                    continue
                hgt, wid = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
                if hgt >= RULE_HEIGHT * xh and wid <= RULE_ASPECT * hgt:
                    rules.append((sl[1].start, sl[1].stop))
            # only the outer segments extend outward through the crop edge
            if k == 0 and seg.x0 == 0:
                new_x0, stop_l, pts_l = _walk(lab, objs_page, (0, 0), sx0, -1, xh, rise, W, rules, pts_l)
            if k == len(segs) - 1 and bx0 + seg.x1 >= bx1:
                new_x1, stop_r, pts_r = _walk(lab, objs_page, (0, 0), sx1, +1, xh, rise, W, rules, pts_r)
            new_x0, new_x1 = int(max(0, new_x0)), int(min(W, new_x1))
        # full page baseline over new_x0..new_x1: crop fit inside, walked points outside (linear between / beyond)
        xs = np.arange(new_x0, new_x1, dtype=np.float64)
        base = np.interp(xs, xs_seg, base_page)
        for pts, side in ((pts_l, -1), (pts_r, 1)):
            ext = [p for p in pts if (p[0] < sx0 if side < 0 else p[0] >= sx1)]
            if not ext:
                continue
            anchor = (float(sx0), float(base_page[0])) if side < 0 else (float(sx1 - 1), float(base_page[-1]))
            px = np.array([anchor[0]] + [p[0] for p in ext]); py = np.array([anchor[1]] + [p[1] for p in ext])
            o = np.argsort(px); px, py = px[o], py[o]
            sel = (xs < sx0) if side < 0 else (xs >= sx1)
            base[sel] = np.interp(xs[sel], px, py)              # flat beyond the last walked letter
        a = int(round(margin * xh))
        paper = float(np.percentile(gray[by0:by1, bx0:bx1], 90))
        # tall window straightened along this line: neighbours share its geometry, so they come out straight too
        A, B = 4.2, 4.2
        S, miss, br = straighten(gray[:, new_x0:new_x1], base, xh, paper=paper, above=A, below=B)
        sink = binarise(S) & ~miss
        top_lim = br - int(round(up)) - a                       # guide band (no neighbour)
        bot_lim = br + int(round(down)) + a
        seams = {}
        P0, has_up, has_dn = _line_pitch(sink, br, xh, rise) if isolate else (None, False, False)
        if isolate and pitch_xh is not None:                   # page consensus: lines on a page share their spacing
            P0 = pitch_xh * xh
            has_up, has_dn = _sides_at(sink, br, xh, rise, P0)
        for side in (-1, 1):
            nb = _neighbour(neighbours, xs, base, xh, side) if (isolate and neighbours) else None
            if nb is not None:        # the neighbour's own fitted line bounds this one (collaborative boundaries)
                f, off = nb
                if side < 0:          # between the line above's baseline and this line's mean line
                    lo = np.round(br + off + .05 * xh).astype(np.int64); hi = np.full(len(off), int(br - rise - .05 * xh))
                else:                 # between this line's baseline and the line below's mean line
                    lo = np.full(len(off), int(br + .05 * xh)); hi = np.round(br + off - f.rise - .05 * f.xh).astype(np.int64)
                seams[side] = _seam(sink, lo, hi, (lo + hi) / 2)
                notes.append(f"{'above' if side < 0 else 'below'}: neighbour box at {np.median(off) / xh:+.2f} x-heights")
                continue
            P = P0 if (has_up if side < 0 else has_dn) else None
            if P is None:
                seams[side] = np.full(S.shape[1], top_lim if side < 0 else bot_lim)
                continue
            if side < 0:     # between the line above's baseline and this line's mean line
                lo, hi = int(br - P + .05 * xh), int(br - rise - .05 * xh)
            else:            # between this line's baseline and the line below's mean line
                lo, hi = int(br + .05 * xh), int(br + P - rise - .05 * xh)
            seams[side] = _seam(sink, lo, hi, (lo + hi) / 2)
            notes.append(f"neighbour {'above' if side < 0 else 'below'} at {P / xh:.2f} x-heights")
        rows = np.arange(S.shape[0])[:, None]
        keep = (rows > seams[-1][None, :]) & (rows < seams[1][None, :]) & ~miss
        S2 = np.where(keep, S, paper)
        ink2 = binarise(S2) & keep
        rr = np.nonzero(ink2.any(axis=1))[0]
        t0 = max(0, int(rr[0] - a)) if rr.size else 0; t1 = min(S.shape[0], int(rr[-1] + 1 + a)) if rr.size else S.shape[0]
        # page-coordinate region that the output shows (for evaluation and for mapping back)
        region = np.zeros(gray.shape, bool)
        for c in range(S.shape[1]):
            ks = np.nonzero(keep[t0:t1, c])[0] + t0
            if ks.size:
                ys = np.clip(np.round(base[c] + ks - br).astype(int), 0, H - 1)
                region[ys, new_x0 + c] = True
        erased = np.zeros(gray.shape, bool)
        if mode == 'box':
            ys_r, xs_r = np.nonzero(region)
            y0, y1 = (int(ys_r.min()), int(ys_r.max()) + 1) if ys_r.size else (by0, by1)
            win = gray[y0:y1, new_x0:new_x1].copy(); win[~region[y0:y1, new_x0:new_x1]] = paper
            img = Image.fromarray(np.clip(win, 0, 255).astype(np.uint8), 'L')
        else:
            img = Image.fromarray(np.clip(S2[t0:t1], 0, 255).astype(np.uint8), 'L')
            ys_r = np.nonzero(region.any(axis=1))[0]
            y0, y1 = (int(ys_r.min()), int(ys_r.max()) + 1) if ys_r.size else (by0, by1)
        erased = region   # (field reused: page pixels the output shows)
        pitch_found = None if P0 is None else P0 / xh
        out.append(Recut(img, mode, new_x0, new_x1, y0, y1, base, xh, stop_l, stop_r, sx0 - new_x0, new_x1 - sx1,
                         max(0, by0 - y0), max(0, y1 - by1), k, notes, erased, pitch_found, up + a, down + a))
    return out

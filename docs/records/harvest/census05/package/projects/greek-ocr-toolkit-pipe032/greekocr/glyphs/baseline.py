"""Skew line (the underline), trail, boundary crossings and cut-off points of a line crop, from its letter band.

Conventions: image rows grow downwards. `angle_deg` > 0 means the line rises to the right on the page image;
`trail_px` = baseline row at the right end minus the left end (> 0 trails down, < 0 trails up).
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from numpy.typing import NDArray

from greekocr.glyphs.components import LineGlyphs, _fit_curve, _ransac_line
from greekocr.glyphs.letters import LetterBox, letter_boxes

__all__ = ['DOUBLE_RATIO', 'Crossing', 'CutLetter', 'CutSpan', 'GuideLines', 'SecondLine', 'SkewLine', 'second_line', 'skew_line', 'text_lines']

# A second text line inside the crop: its band's letter support ≥ DOUBLE_RATIO × the main band's. Set on the 44
# o4d_lines fixtures against the implementer's provisional labels (7 double: 0.27–0.61; 20 single: ≤ 0.22) and
# checked on rendered two-line crops (docs/records/glyphs/GLYPHS_PLAN.md).
DOUBLE_RATIO = .25
DOUBLE_BODIES = 0   # body count is reported but not gated: a second line cut by the crop has none (fixture line22)


@dataclass(frozen=True)
class Crossing:
    x: float
    line: str      # 'baseline' | 'meanline'
    edge: str      # 'top' | 'bottom'
    meaning: str   # human-readable


@dataclass(frozen=True)
class CutSpan:
    x0: int
    x1: int        # exclusive
    edge: str      # 'top' | 'bottom'
    min_visible: float   # smallest visible fraction of the letter body in the span (0 = body entirely outside)


@dataclass(frozen=True)
class CutLetter:
    x0: int
    x1: int
    edge: str          # 'top' | 'bottom'
    body_cut: float    # fraction of the letter body (x-height band) outside the crop at this letter
    touches: bool      # the letter's ink reaches the crop edge


@dataclass(frozen=True)
class SecondLine:
    support: int
    ratio: float          # support / main band support
    bodies: int           # letters whose body is ≥ 60 % visible on the second band
    offset_xh: float      # median vertical offset from the main baseline, in x-heights (+ below)
    visible: float        # mean fraction of its letter body inside the crop over its supported x-range
    coverage: float       # supported x-range / crop width
    baseline: NDArray[np.float64]


def second_line(glyphs: LineGlyphs) -> SecondLine | None:
    """Fit a band to the ink the main band does not explain (outside its body ± 0.3 x-heights)."""
    xh, h, w = glyphs.band.xh, glyphs.height, glyphs.width
    t1, b1 = glyphs.band.top, glyphs.band.bottom
    px, py = [], []
    for c in glyphs.components:
        if c.role == 'rule' or c.area < .08 * xh * xh or not (.3 * xh <= c.w <= 1.8 * xh):
            continue
        i = int(np.clip(c.cx, 0, w - 1))
        if t1[i] - .3 * xh <= (c.y0 + c.y1) / 2 <= b1[i] + .3 * xh:
            continue
        touch = set(c.touches)
        if 'bottom' not in touch and ('top' in touch or .6 * xh <= c.h <= 1.4 * xh):
            px.append(c.cx); py.append(float(c.y1))
        if 'top' not in touch and ('bottom' in touch or .6 * xh <= c.h <= 1.4 * xh):
            px.append(c.cx); py.append(float(c.y0) + xh)
    if len(px) < 4:
        return None
    bx, by = np.array(px), np.array(py)
    inl = _ransac_line(bx, by, .15 * xh + 1, np.random.default_rng(0))
    if inl.sum() < 4:
        return None
    curve, _ = _fit_curve(bx[inl], by[inl], w)
    lo, hi = int(bx[inl].min()), int(bx[inl].max()) + 1
    vis = np.clip(np.minimum(curve, h) - np.maximum(curve - xh, 0), 0, xh) / xh
    # visible letter bodies on the second band: components covering ≥ 0.6 of its middle region (tips do not)
    bodies = 0
    for c in glyphs.components:
        if c.role in ('mark', 'rule') or c.w > 2 * xh:
            continue
        i = int(np.clip(c.cx, 0, w - 1))
        if min(c.y1, curve[i]) - max(c.y0, curve[i] - xh) >= .6 * xh:
            bodies += 1
    return SecondLine(int(inl.sum()), round(int(inl.sum()) / max(1, glyphs.band.n_support), 3), bodies,
                      round(float(np.median(curve - b1)) / xh, 2), round(float(vis[lo:hi].mean()), 3),
                      round((hi - lo) / w, 3), curve)


@dataclass(frozen=True)
class SkewLine:
    angle_deg: float
    trail_px: float
    degree: int
    baseline: NDArray[np.float64]
    meanline: NDArray[np.float64]
    visible: NDArray[np.float64]     # per column: fraction of the letter body inside the crop, 0..1
    support_x: tuple[float, float]
    n_support: int
    residual_px: float | None        # median |support − fit|; None without support
    xh: float
    xh_source: str
    crossings: tuple[Crossing, ...]
    cut_spans: tuple[CutSpan, ...]
    cut_letters: tuple[CutLetter, ...]
    second: SecondLine | None = None

    @property
    def double_line(self) -> bool:
        return self.second is not None and self.second.ratio >= DOUBLE_RATIO and self.second.bodies >= DOUBLE_BODIES

    @property
    def confidence(self) -> str:
        if self.residual_px is None:
            return 'low'
        if self.n_support >= 15 and self.residual_px <= .12 * self.xh and self.xh_source != 'letter_width':
            return 'high'
        return 'medium' if self.n_support >= 6 else 'low'


def _crossings(y: NDArray[np.float64], level: float, line: str, edge: str) -> list[Crossing]:
    out = []
    above = y < level
    for i in np.nonzero(above[1:] != above[:-1])[0]:
        # linear interpolation between columns i and i+1
        x = i + (level - y[i]) / (y[i + 1] - y[i]) if y[i + 1] != y[i] else float(i)
        entering = (edge == 'top' and not above[i + 1]) or (edge == 'bottom' and above[i + 1])
        part = 'top of the letters' if line == 'meanline' else 'whole letter body'
        verb = 'enters the crop' if entering else 'leaves the crop'
        out.append(Crossing(float(x), line, edge, f'{part} {verb} through the {edge} edge'))
    return out


def _spans(mask: NDArray[np.bool_], visible: NDArray[np.float64], edge: str, min_len: int) -> list[CutSpan]:
    out = []
    padded = np.concatenate([[False], mask, [False]])
    edges = np.nonzero(padded[1:] != padded[:-1])[0]
    for a, b in zip(edges[::2], edges[1::2]):
        if b - a >= min_len:
            out.append(CutSpan(int(a), int(b), edge, round(float(visible[a:b].min()), 3)))
    return out


def skew_line(glyphs: LineGlyphs, boxes: list[LetterBox] | None = None) -> SkewLine:
    band, h, w = glyphs.band, glyphs.height, glyphs.width
    base, mean = band.bottom, band.top
    sx = np.array([p[0] for p in band.support], float)
    sy = np.array([p[1] for p in band.support], float)
    if len(sx) >= 2 and np.ptp(sx) > 0:
        slope = float(np.polyfit(sx, sy, 1)[0])
        resid = float(np.median(np.abs(sy - base[np.clip(sx.astype(int), 0, w - 1)])))
    else:
        slope, resid = float((base[-1] - base[0]) / max(w - 1, 1)), None
    visible = np.clip(np.minimum(base, h) - np.maximum(mean, 0), 0, None) / band.xh
    visible = np.clip(visible, 0, 1)
    crossings = (_crossings(mean, 0.0, 'meanline', 'top') + _crossings(base, 0.0, 'baseline', 'top')
                 + _crossings(base, float(h), 'baseline', 'bottom') + _crossings(mean, float(h), 'meanline', 'bottom'))
    crossings.sort(key=lambda c: c.x)
    min_len = max(2, int(.3 * band.xh))
    cut_top = (mean < -.1 * band.xh) & (visible < .95)
    cut_bottom = (base > h + .1 * band.xh) & (visible < .95)
    spans = _spans(cut_top, visible, 'top', min_len) + _spans(cut_bottom, visible, 'bottom', min_len)
    spans.sort(key=lambda s: s.x0)
    cut_letters = []
    for b in boxes if boxes is not None else letter_boxes(glyphs):
        cx = int(np.clip((b.x0 + b.x1) // 2, 0, w - 1))
        top_cut = float(np.clip(-mean[cx] / band.xh, 0, 1))
        bot_cut = float(np.clip((base[cx] - h) / band.xh, 0, 1))
        if b.y0 == 0 or top_cut > .1:
            cut_letters.append(CutLetter(b.x0, b.x1, 'top', round(top_cut, 3), b.y0 == 0))
        if b.y1 == h or bot_cut > .1:
            cut_letters.append(CutLetter(b.x0, b.x1, 'bottom', round(bot_cut, 3), b.y1 == h))
    return SkewLine(angle_deg=round(-math.degrees(math.atan(slope)), 3), trail_px=round(float(base[-1] - base[0]), 2),
                    degree=band.degree, baseline=base, meanline=mean, visible=visible,
                    support_x=(float(sx.min()), float(sx.max())) if len(sx) else (0.0, 0.0), n_support=band.n_support,
                    residual_px=None if resid is None else round(resid, 2), xh=band.xh, xh_source=band.xh_source, crossings=tuple(crossings),
                    cut_spans=tuple(spans), cut_letters=tuple(cut_letters), second=second_line(glyphs))


# ---------------------------------------------------------------------------------------------------------------
# Four guide lines for every text line in the crop (owner, 8 Oct 16:00): top of tall letters, mean line (top of the
# short letters), baseline, bottom of hanging letters. Neighbour lines are often cut to their accents or letter
# edges; they borrow the main line's shape and letter height (lines on a page are near-parallel and share one type
# size) and only their vertical shift is estimated, by votes: each kind of fragment points at one guide line.
# ---------------------------------------------------------------------------------------------------------------

RISE, DROP = .51, .57     # median rise of tall letters / drop of hanging letters on 213 real lines (x-heights)
ACCENT_GAP = .1           # accents sit ~0.1 x-heights above the mean line (rendered evidence, CP-G1 mark gaps)
# Search limits (disclosed, CP-G2 F4): neighbours within ±LINE_RANGE x-heights of the main baseline, at most
# max_per_side lines per side, at least LINE_SEPARATION apart (real line pitch here ≈ 2.2–2.7 x-heights), each supported
# by ≥ MIN_PIECES distinct ink pieces (two paper specks must not invent a line, CP-G2 F3).
LINE_RANGE, LINE_SEPARATION, MIN_PIECES = 6.0, 1.8, 3
LINE_MIN = 1.7    # nearer than this is the main line's own ink (real pitch ≥ 2.2 x-heights; tips misplace by ≤ 0.5)


@dataclass(frozen=True)
class GuideLines:
    side: str                         # 'main' | 'above' | 'below'
    shift_xh: float                   # vertical offset from the main baseline, in x-heights (0 for main)
    ascender: NDArray[np.float64]     # per column rows
    mean: NDArray[np.float64]
    base: NDArray[np.float64]
    descender: NDArray[np.float64]
    x0: int                           # columns with evidence for this line
    x1: int
    votes: float                      # weight of the fragments that placed it (main: support points)
    visible: float                    # mean fraction of its letter body inside the crop over x0..x1


def _rise_drop(glyphs: LineGlyphs) -> tuple[float, float]:
    xh = glyphs.band.xh
    r, d = [], []
    for c in glyphs.components:
        if c.role != 'letter' or {'top', 'bottom'} & set(c.touches):
            continue
        t, b = glyphs.band.at(c.cx)
        if (t - c.y0) / xh > .25:
            r.append((t - c.y0) / xh)
        if (c.y1 - b) / xh > .25:
            d.append((c.y1 - b) / xh)
    return (float(np.median(r)) if len(r) >= 3 else RISE), (float(np.median(d)) if len(d) >= 3 else DROP)


def text_lines(glyphs: LineGlyphs, *, max_per_side: int = 3) -> list[GuideLines]:
    """The main line and every neighbour line (above / below), each with its four guide lines."""
    xh, w, h = glyphs.band.xh, glyphs.width, glyphs.height
    B, M = glyphs.band.bottom, glyphs.band.top
    rise, drop = _rise_drop(glyphs)

    def make(side: str, shift: float, x0: int, x1: int, votes: float) -> GuideLines:
        base = B + shift
        vis = np.clip(np.minimum(base, h) - np.maximum(base - xh, 0), 0, xh) / xh
        return GuideLines(side, round(shift / xh, 3), base - (1 + rise) * xh, base - xh, base, base + drop * xh,
                          x0, x1, round(votes, 1), round(float(vis[x0:x1 + 1].mean()), 3))

    sx = [p[0] for p in glyphs.band.support]
    out = [make('main', 0.0, int(min(sx)) if sx else 0, int(max(sx)) if sx else w - 1, float(glyphs.band.n_support))]
    votes: list[tuple[float, float, float, int]] = []      # (shift rows, x, weight, component index)
    for c in glyphs.components:
        if c.role == 'rule' or c.area < 6:
            continue
        i = int(np.clip(c.cx, 0, w - 1))
        if M[i] - .6 * xh <= (c.y0 + c.y1) / 2 <= B[i] + .6 * xh:
            continue                                   # the main line itself
        small = c.h < .5 * xh and c.w < .8 * xh
        if c.y0 > 0:     # a free top: the mean line, or the top of a tall letter
            votes += [(c.y0 - M[i], c.cx, 1.0, c.index), (c.y0 - (M[i] - rise * xh), c.cx, .6, c.index)]
        if c.y1 < h:     # a free bottom: the baseline, a hanging letter's bottom, or an accent just above the mean line
            votes += [(c.y1 - B[i], c.cx, 1.0, c.index), (c.y1 - (B[i] + drop * xh), c.cx, .6, c.index)]
            if small:
                votes.append((c.y1 - (M[i] - ACCENT_GAP * xh), c.cx, .8, c.index))
    for side, lo, hi in (('above', -LINE_RANGE, -LINE_MIN), ('below', LINE_MIN, LINE_RANGE)):
        v = [t for t in votes if lo * xh <= t[0] <= hi * xh]
        accepted = 0
        for _ in range(4 * max_per_side):              # rejected peaks are skipped, not the end of the search (CP-G2)
            if accepted >= max_per_side or len(v) < 3:
                break
            s = np.array([t[0] for t in v]); wt = np.array([t[2] for t in v])
            hist, edges = np.histogram(s, bins=np.arange(lo * xh, hi * xh + 1, .1 * xh), weights=wt)
            hist = np.convolve(hist, [.25, .5, 1, .5, .25], mode='same')
            k = int(np.argmax(hist))
            near = np.abs(s - (edges[k] + edges[k + 1]) / 2) <= .25 * xh
            pieces = {t[3] for t, n in zip(v, near) if n}
            if wt[near].sum() < 3 or len(pieces) < MIN_PIECES:
                v = [t for t, n in zip(v, near) if not n]      # too little independent support: drop this peak only
                continue
            shift = float(np.average(s[near], weights=wt[near]))
            xs = np.array([t[1] for t, n in zip(v, near) if n])
            out.append(make(side, shift, int(xs.min()), int(xs.max()), float(wt[near].sum())))
            accepted += 1
            v = [t for t in v if abs(t[0] - shift) > LINE_SEPARATION * xh]
    return out

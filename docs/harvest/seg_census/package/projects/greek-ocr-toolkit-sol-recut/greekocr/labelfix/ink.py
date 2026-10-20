"""Ink evidence for a disputed vowel: mark blobs above and below it, from the crop pixels.

Reuses `greekocr.glyphs.components.line_glyphs` (the same component extraction and band
fit that `pages/lines.py` consumes through `_line_geometry`): Sauvola ink mask, 8-connected
components with roles (letter / mark / punct / ...), and the letter band (mean line and
baseline as functions of x) with its x-height.

The vowel's horizontal extent is taken from the ink, not from the CTC frames: the CTC span
only selects the letter component (the one it overlaps most), whose bounding box becomes the
vowel body. CTC spikes sit left of the printed glyph and accents on leaning print overhang the
vowel's right edge, so frame positions alone would miss them.

Two kinds of mark evidence are gathered inside an x window:

  detached   components the glyph pass labelled `mark` (above a letter) or small `punct`
             blobs below the baseline (iota subscript candidates);
  attached   ink above the mean line that belongs to a `letter` component (an accent fused
             to its vowel in heavy print): the component's pixels above meanline - 0.15 xh are
             re-labelled and counted as blobs. Ascenders of neighbouring letters are excluded by
             requiring the blob centre inside the vowel's own span.

Every blob is reported with its bounding box, area, the principal-axis angle (degrees,
image coordinates: negative = rises to the right like an acute, positive = falls to the
right like a grave) and its elongation, so the decision can be audited on the crop.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from ..glyphs.components import line_glyphs

EIGHT = np.ones((3, 3), bool)
GRID = 8
ATTACH_SLICE_XH = -0.05    # slice attached marks from just above the mean line (vowels have no ascender)
MIN_BLOB_AREA = 3
MAX_MARK_HEIGHT_XH = 0.9   # taller blobs above the body are ascenders/neighbours, not marks
MAX_MARK_WIDTH_XH = 1.2
SUBSCRIPT_MAX_W_XH = 0.6
SUBSCRIPT_MAX_H_XH = 0.6
OBLIQUE_MIN_ELONGATION = 1.4
OBLIQUE_MIN_DEG, OBLIQUE_MAX_DEG = 15.0, 80.0


@dataclass
class Blob:
    x0: int
    y0: int
    x1: int
    y1: int
    area: int
    source: str          # 'detached' | 'attached'
    angle_deg: float     # principal axis angle, image coords (see module doc)
    elongation: float    # sqrt(l1/l2) of the covariance eigenvalues (1 = round)
    darkness: float = 0.0   # median gray of the blob (0 = black)
    faint: bool = False     # lighter than the faint cut (paper - 0.45 * (paper - letter ink))
    touches_border: bool = False
    hook: float = 0.0       # (mean x of the middle rows - mean x of the top+bottom rows) / width: ')' > 0, '(' < 0
    skew: float = 0.0       # third standardised moment of x: where the mass sits inside the box
    top_heavy: float = 0.0  # (mass in the upper half - lower half) / area
    grid: tuple = ()        # GRID x GRID occupancy of the blob's bounding box (shape thumbnail), row-major

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def cy(self) -> float:
        return (self.y0 + self.y1) / 2

    @property
    def w(self) -> int:
        return self.x1 - self.x0

    @property
    def h(self) -> int:
        return self.y1 - self.y0

    def to_record(self) -> dict:
        return dict(bbox=[self.x0, self.y0, self.x1, self.y1], area=self.area, source=self.source,
                    angle_deg=round(self.angle_deg, 1), elongation=round(self.elongation, 2),
                    darkness=round(self.darkness, 1), faint=self.faint, touches_border=self.touches_border,
                    hook=round(self.hook, 3), skew=round(self.skew, 3), top_heavy=round(self.top_heavy, 3))


def principal_axis(ys: np.ndarray, xs: np.ndarray) -> tuple[float, float]:
    """(angle in degrees, elongation). Angle of the major axis vs the x axis in image coordinates."""
    if len(xs) < 3:
        return 0.0, 1.0
    x = xs - xs.mean()
    y = ys - ys.mean()
    cxx, cyy, cxy = float((x * x).mean()), float((y * y).mean()), float((x * y).mean())
    tr, det = cxx + cyy, cxx * cyy - cxy * cxy
    disc = max(tr * tr / 4 - det, 0.0)
    l1, l2 = tr / 2 + math.sqrt(disc), max(tr / 2 - math.sqrt(disc), 1e-6)
    angle = 0.5 * math.degrees(math.atan2(2 * cxy, cxx - cyy))
    return angle, math.sqrt(l1 / l2)


@dataclass
class CropInk:
    """Per-crop analysis shared by all candidates of a line."""
    gray: np.ndarray
    ink: np.ndarray
    labels: np.ndarray
    xh: float
    top: np.ndarray        # mean line per column
    bottom: np.ndarray     # baseline per column
    components: list
    paper: float
    width: int = 0
    height: int = 0
    ink_level: float = 0.0   # median gray of letter pixels

    @property
    def faint_cut(self) -> float:
        return self.paper - 0.45 * (self.paper - self.ink_level)

    def band(self, x: float) -> tuple[float, float]:
        i = min(max(int(round(x)), 0), len(self.top) - 1)
        return float(self.top[i]), float(self.bottom[i])


def analyse(image: Image.Image) -> CropInk:
    g = line_glyphs(image)
    return CropInk(g.gray, g.ink, g.labels, float(g.band.xh), np.asarray(g.band.top), np.asarray(g.band.bottom),
                   list(g.components), float(g.paper), g.width, g.height, float(g.ink_level))


def _blob(mask: np.ndarray, oy: int, ox: int, source: str, ink: 'CropInk | None' = None) -> Blob:
    ys, xs = np.nonzero(mask)
    ang, el = principal_axis(ys.astype(float), xs.astype(float))
    b = Blob(int(xs.min()) + ox, int(ys.min()) + oy, int(xs.max()) + ox + 1, int(ys.max()) + oy + 1,
             int(mask.sum()), source, ang, el)
    h = int(ys.max() - ys.min()) + 1
    w = int(xs.max() - xs.min()) + 1
    sub = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(float)
    gy = np.minimum((np.arange(h) * GRID) // h, GRID - 1)
    gx = np.minimum((np.arange(w) * GRID) // w, GRID - 1)
    g = np.zeros((GRID, GRID))
    cnt = np.zeros((GRID, GRID))
    np.add.at(g, (gy[:, None].repeat(w, 1), gx[None, :].repeat(h, 0)), sub)
    np.add.at(cnt, (gy[:, None].repeat(w, 1), gx[None, :].repeat(h, 0)), 1.0)
    b.grid = tuple((g / np.maximum(cnt, 1)).ravel().round(3).tolist())
    if h >= 3 and w >= 2:
        yr = (ys - ys.min()) / max(h - 1, 1)
        ends = (yr <= 0.25) | (yr >= 0.75)
        mid = ~ends
        if ends.any() and mid.any():
            b.hook = float((xs[mid].mean() - xs[ends].mean()) / w)
        sd = xs.std()
        if sd > 0:
            b.skew = float(((xs - xs.mean()) ** 3).mean() / sd ** 3)
        b.top_heavy = float(((yr < 0.5).sum() - (yr >= 0.5).sum()) / len(ys))
    if ink is not None:
        b.darkness = float(np.median(ink.gray[ys + oy, xs + ox]))
        b.faint = b.darkness > ink.faint_cut
        b.touches_border = b.y0 == 0 or b.y1 >= ink.height or b.x0 == 0 or b.x1 >= ink.width
    return b


def _overlap(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))


@dataclass
class MarkEvidence:
    above: list = field(default_factory=list)   # blobs above the vowel body
    below: list = field(default_factory=list)   # small detached blobs under the baseline
    window: tuple = (0.0, 0.0)
    xh: float = 0.0
    meanline: float = 0.0
    baseline: float = 0.0
    body: tuple = (0.0, 0.0)                    # the vowel body's x extent after snapping to ink
    body_source: str = ''                       # 'letter' (snapped) | 'merged' | 'ctc'
    n_letters_in_span: int = 0                  # letter components overlapping the CTC span
    neighbour_marks: int = 0                    # mark blobs in the search window but outside the body
    clipped_top: bool = False                   # ink touches the crop's top edge inside the window
    clipped_bottom: bool = False

    @property
    def n_above(self) -> int:
        return len(self.above)

    def obliques(self) -> list:
        return [b for b in self.above if b.elongation >= OBLIQUE_MIN_ELONGATION
                and OBLIQUE_MIN_DEG <= abs(b.angle_deg) <= OBLIQUE_MAX_DEG]

    def to_record(self) -> dict:
        return dict(window=[round(self.window[0], 1), round(self.window[1], 1)], xh=round(self.xh, 2),
                    meanline=round(self.meanline, 1), baseline=round(self.baseline, 1),
                    body=[round(self.body[0], 1), round(self.body[1], 1)], body_source=self.body_source,
                    n_letters_in_span=self.n_letters_in_span, neighbour_marks=self.neighbour_marks,
                    clipped_top=self.clipped_top, clipped_bottom=self.clipped_bottom,
                    above=[b.to_record() for b in self.above], below=[b.to_record() for b in self.below])


def snap_body(ink: CropInk, bx0: float, bx1: float) -> tuple[float, float, str, int]:
    """The vowel body's x extent: the letter component the CTC span overlaps most.

    Returns (x0, x1, source, n_letters): `n_letters` counts letter components that overlap the
    CTC span by at least 30 % of its width AND at least two thirds of the best overlap; more
    than one means the frames straddle two letters and the localisation is uncertain.
    """
    xh = ink.xh
    best, best_ov = None, 0.0
    overlaps = []
    for c in ink.components:
        if c.role != 'letter':
            continue
        ov = _overlap(bx0, bx1, c.x0, c.x1)
        overlaps.append(ov)
        if ov > best_ov:
            best, best_ov = c, ov
    if best is None or best_ov <= 0:
        return bx0 - 0.1 * xh, bx1 + 0.4 * xh, 'ctc', 0
    n = sum(1 for ov in overlaps if ov >= 0.3 * max(1.0, bx1 - bx0) and ov >= best_ov / 1.5)
    if best.w <= 1.6 * xh:
        return float(best.x0), float(best.x1), 'letter', n
    return max(float(best.x0), bx0 - 0.2 * xh), min(float(best.x1), bx1 + 0.5 * xh), 'merged', n


def mark_evidence(ink: CropInk, x0: float, x1: float, *, core_x0: float | None = None,
                  core_x1: float | None = None) -> MarkEvidence:
    """Mark blobs for the vowel whose CTC span is [core_x0, core_x1) (default: the window).

    The body extent is snapped to ink (`snap_body`); blobs must have their centre inside
    [body_x0 - 0.1 xh, body_x1 + 0.2 xh] so a neighbour's accent or ascender is not credited
    to this vowel. `x0..x1` only bounds the component search.
    """
    xh = ink.xh
    c0 = x0 if core_x0 is None else core_x0
    c1 = x1 if core_x1 is None else core_x1
    b0, b1, bsrc, n_letters = snap_body(ink, c0, c1)
    lo, hi = b0 - 0.1 * xh, b1 + 0.2 * xh
    x0, x1 = min(x0, b0 - 0.5 * xh), max(x1, b1 + 0.5 * xh)
    top, base = ink.band((b0 + b1) / 2)
    ev = MarkEvidence([], [], (x0, x1), xh, top, base, (b0, b1), bsrc, n_letters)
    wx0, wx1 = int(max(0, math.floor(lo))), int(min(ink.width, math.ceil(hi)))
    if wx1 > wx0:
        ev.clipped_top = bool(ink.ink[0, wx0:wx1].any())
        ev.clipped_bottom = bool(ink.ink[-1, wx0:wx1].any())
    for c in ink.components:
        if c.x1 <= x0 or c.x0 >= x1:
            continue
        cx = (c.x0 + c.x1) / 2
        inside = lo <= cx <= hi
        if c.role == 'mark' and c.y1 <= top + 0.35 * xh:
            if not inside:
                ev.neighbour_marks += 1
                continue
            if c.h <= MAX_MARK_HEIGHT_XH * xh and c.w <= MAX_MARK_WIDTH_XH * xh:
                sub = ink.labels[c.y0:c.y1, c.x0:c.x1] == c.index
                ev.above.append(_blob(sub, c.y0, c.x0, 'detached', ink))
        elif c.role in ('mark', 'punct', 'fragment') and c.y0 >= base - 0.25 * xh and inside:
            if c.w <= SUBSCRIPT_MAX_W_XH * xh and c.h <= SUBSCRIPT_MAX_H_XH * xh and c.y0 <= base + 0.6 * xh:
                sub = ink.labels[c.y0:c.y1, c.x0:c.x1] == c.index
                ev.below.append(_blob(sub, c.y0, c.x0, 'detached', ink))
        elif c.role in ('letter', 'large') and c.y0 < top - ATTACH_SLICE_XH * xh:
            # attached mark: ink of this letter component above the slice row, inside the window
            cut = int(math.floor(top - ATTACH_SLICE_XH * xh))
            if cut <= c.y0:
                continue
            ax0, ax1 = int(max(c.x0, math.floor(lo))), int(min(c.x1, math.ceil(hi)))
            if ax1 <= ax0:
                continue
            sub = ink.labels[c.y0:cut, ax0:ax1] == c.index
            if not sub.any():
                continue
            lab, n = ndi.label(sub, structure=EIGHT)
            for k, sl in enumerate(ndi.find_objects(lab), 1):
                if sl is None:
                    continue
                m = lab[sl] == k
                if m.sum() < MIN_BLOB_AREA:
                    continue
                b = _blob(m, c.y0 + sl[0].start, ax0 + sl[1].start, 'attached', ink)
                if not (lo <= b.cx <= hi):
                    continue
                if b.h > MAX_MARK_HEIGHT_XH * xh or b.w > MAX_MARK_WIDTH_XH * xh:
                    continue
                # a thin vertical blob reaching the cut row is an ascender (λ δ θ β ζ ξ), not a
                # mark -- only possible when the component merges several letters; a snapped
                # single vowel has no ascender
                if bsrc == 'merged' and b.y1 >= cut and b.w <= 0.25 * xh and b.h >= 0.45 * xh \
                        and abs(b.angle_deg) > 70:
                    continue
                # the sliver of a round vowel's own top (overshoot above the mean line)
                if b.y1 >= cut and b.h <= max(2, 0.1 * xh):
                    continue
                ev.above.append(b)
    ev.above.sort(key=lambda b: b.x0)
    ev.below.sort(key=lambda b: b.x0)
    return ev


def dialytika_shape(ev: MarkEvidence) -> bool:
    """Two small blobs side by side at the same height."""
    a = ev.above
    if len(a) != 2:
        return False
    p, q = a
    xh = ev.xh
    small = all(b.area <= 0.2 * xh * xh and b.h <= 0.4 * xh and b.w <= 0.45 * xh for b in (p, q))
    gap = q.x0 - p.x1
    return small and -0.05 * xh <= gap <= 0.5 * xh and abs(p.cy - q.cy) <= 0.2 * xh


def slope_sign(blob: Blob) -> str | None:
    """'acute' if the stroke rises to the right, 'grave' if it falls, None if not oblique."""
    if blob.elongation < OBLIQUE_MIN_ELONGATION or not (OBLIQUE_MIN_DEG <= abs(blob.angle_deg) <= OBLIQUE_MAX_DEG):
        return None
    return 'acute' if blob.angle_deg < 0 else 'grave'

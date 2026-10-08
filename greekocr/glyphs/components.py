"""Reference-free glyph components of a line crop: binarisation, the line's own letter band, per-component descriptors.

Everything is measured from the crop's pixels; no reader, text layer or model is consulted. Units are pixels unless a field
says it is normalised by the line's x-height (`xh`), which is estimated from the crop's own complete letters.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray
from PIL import Image
from scipy import ndimage as ndi

__all__ = ['Band', 'Component', 'LineGlyphs', 'binarise', 'line_glyphs', 'to_gray']

EIGHT = np.ones((3, 3), dtype=bool)
# Bend tracking (8 Oct, after the owner's line04 report): keep the bending curve only if its p90 residual is below
# SEL_RATIO × the straight line's on the same tracked evidence and the straight residual exceeds SEL_FLOOR x-heights.
# Rendered bent lines (seed 41, 100 bent + 100 straight): lines with any column > 0.25 xh off 84 % → 45 %, straight unchanged.
SEL_RATIO, SEL_FLOOR = .85, .06
# Gap between a small component and the letter body, in x-heights, beyond which it belongs to a neighbouring line.
# Calibrated on rendered polytonic lines with neighbour intrusions (31 fonts, 250 lines): accents above sit 0.02–0.19
# (p5–p95) above the mean line, neighbour ink ≥ 0.63; iota subscripts ≤ 0.12 below the baseline (p75), neighbours ≥ 0.36.
NEIGHBOUR_GAP_ABOVE = .40
NEIGHBOUR_GAP_BELOW = .30
# x-height / typical letter-component width; fallback for crops with < 4 complete letters (see XH_PER_WIDTH note).
XH_PER_WIDTH = 1.39  # median over 443 real crops with ≥ 15 support points (p25 1.25, p75 1.49), 8 Oct


def to_gray(crop: Image.Image | NDArray[Any]) -> NDArray[np.float64]:
    """Grayscale float array in [0, 255], ink dark."""
    if isinstance(crop, Image.Image):
        return np.asarray(crop.convert('L'), dtype=np.float64)
    arr = np.asarray(crop, dtype=np.float64)
    return arr.mean(axis=2) if arr.ndim == 3 else arr


def _otsu(values: NDArray[np.float64]) -> float:
    hist, edges = np.histogram(values, bins=256, range=(0, 256))
    p = hist / max(hist.sum(), 1)
    omega, mu = np.cumsum(p), np.cumsum(p * (edges[:-1] + .5))
    between = (mu[-1] * omega - mu) ** 2 / np.maximum(omega * (1 - omega), 1e-12)
    return float(edges[int(np.argmax(between))] + .5)


def _noise_sigma(gray: NDArray[np.float64], paper: float) -> float:
    """Robust spread of the paper: MAD of the pixels lighter than the paper median's lower shoulder."""
    bright = gray[gray >= paper - 25]
    return float(1.4826 * np.median(np.abs(bright - np.median(bright)))) if bright.size else 5.0


SOFT_EDGE = .22   # boundary sharpness below which a large faint blob is shading, not print


def _edge_sharpness(gray: NDArray[np.float64], mask: NDArray[np.bool_], *, paper: float,
                    exclude: NDArray[np.bool_] | None = None) -> float:
    """Median gradient magnitude on a blob's boundary divided by its contrast to the crop's paper level. Boundary
    pixels on the crop border (no outside) or near `exclude` (strong ink: letters printed inside a shadow) do not count."""
    ys, xs = np.nonzero(mask)
    y0, y1, x0, x1 = max(0, ys.min() - 4), ys.max() + 5, max(0, xs.min() - 4), xs.max() + 5
    g, m = gray[y0:y1, x0:x1], mask[y0:y1, x0:x1]
    mag = np.hypot(ndi.sobel(g, 1), ndi.sobel(g, 0)) / 8
    edge = m & ~ndi.binary_erosion(m, border_value=1)          # border_value=1: the crop border is not an edge
    if exclude is not None:
        edge &= ~ndi.binary_dilation(exclude[y0:y1, x0:x1], iterations=4)
    contrast = max(1.0, paper - float(np.median(g[m])))
    return float(np.median(mag[edge])) / contrast if edge.any() else 1.0


def binarise(gray: NDArray[np.float64], *, window: int | None = None, k: float = .2) -> NDArray[np.bool_]:
    """Ink mask = Sauvola local threshold (window ≈ crop height) AND a loose global floor, PLUS faint components.

    Sauvola misses uniformly faint print (a letter of gray 195 on paper 235 vanishes entirely). Faint components are
    connected regions darker than paper − max(4·σ_paper, 15 % of the paper–ink range) that contain no Sauvola ink at
    all; they are added whole, so a faint letter is detected (and its lightness measured) instead of disappearing.
    """
    h = gray.shape[0]
    window = window or max(15, (h // 2) * 2 + 1)
    mean = ndi.uniform_filter(gray, window, mode='reflect')
    sq = ndi.uniform_filter(gray * gray, window, mode='reflect')
    std = np.sqrt(np.maximum(sq - mean * mean, 0))
    local = gray < mean * (1 + k * (std / 128 - 1))
    paper = float(np.percentile(gray, 90))
    dark = float(np.percentile(gray, 1))
    floor = gray < paper - max(12.0, .12 * (paper - dark))
    ink = local & floor
    strong = ink.copy()
    faint = gray < paper - max(4 * _noise_sigma(gray, paper), .15 * (paper - dark), 10.0)
    # faint ink is added where it stands apart from strong ink: whole faint components with no strong ink, and faint
    # regions more than 2 px from strong ink (a faint letter body attached to one dark stroke; CP-G1c2 F4). The 2 px
    # margin keeps the blur halo of dark strokes out, so dark letters do not thicken or merge.
    far = faint & ~ndi.binary_dilation(ink, iterations=2)
    lab, n = ndi.label(faint, structure=EIGHT)
    if n:
        has_ink = np.zeros(n + 1, bool)
        has_ink[np.unique(lab[ink])] = True
        sizes = np.bincount(lab.ravel(), minlength=n + 1)
        add = ~has_ink & (sizes >= 12)
        add[0] = False
        ink |= add[lab]
    flab, fn = ndi.label(far & ~ink, structure=EIGHT)
    if fn:
        sizes = np.bincount(flab.ravel(), minlength=fn + 1)
        keep = sizes >= 24
        keep[0] = False
        ink |= keep[flab]
    # faint ink must be letter-like, not a shading patch. A faint-only blob is dropped when it is large (short side
    # ≥ 30 % of the crop height), thick (2 × max distance-to-edge ≥ 40 % of the CROP height) AND soft-edged: printed ink
    # steps from paper to ink within a pixel or two (boundary sharpness ≈ 0.36 on blurred renders, thin to very heavy),
    # a shadow fades in (owner's page-edge shadow 0.14). Heavily over-inked faint capitals are kept (CP-G3c2).
    # Owner 8 Oct: a page-edge shadow (73 px thick in a 136 px crop) had become a 'letter'. CP-G3 F1: a stroke reference
    # let dark specks delete faint letters; CP-G3c2: thickness relative to the blob's own short side deleted faint BOLD
    # letters (bold Ε, Ι) in tight crops — strokes stay well under 40 % of the crop height even in bold type.
    if (ink & ~strong).any():
        dt = ndi.distance_transform_edt(ink)
        alab, an = ndi.label(ink, structure=EIGHT)
        has_strong = np.zeros(an + 1, bool)
        has_strong[np.unique(alab[strong])] = True
        drop = np.zeros(an + 1, bool)
        for i, sl in enumerate(ndi.find_objects(alab), start=1):
            if sl is None or has_strong[i]:
                continue
            short = min(sl[0].stop - sl[0].start, sl[1].stop - sl[1].start)
            thick = 2 * float(dt[sl][alab[sl] == i].max())
            if short >= .3 * h and thick >= .4 * h:
                drop[i] = _edge_sharpness(gray, alab == i, paper=paper, exclude=strong) < SOFT_EDGE
        ink &= ~drop[alab]
    return ink


@dataclass(frozen=True)
class Band:
    """The letter band as functions of x: top = mean line, bottom = baseline (row coordinates, may lie outside the crop)."""
    top: NDArray[np.float64]
    bottom: NDArray[np.float64]
    xh: float
    n_support: int
    support: tuple[tuple[float, float, str], ...] = ()   # (x, implied baseline y, 'bottom' | 'top') inliers
    degree: int = 1                                      # 1 straight, 2 curved
    xh_source: str = 'free_letters'                      # free_letters | substantial_letters | letter_width | prior

    def at(self, x: float) -> tuple[float, float]:
        i = int(np.clip(round(x), 0, len(self.top) - 1))
        return float(self.top[i]), float(self.bottom[i])


@dataclass(frozen=True)
class Component:
    """One 8-connected ink component. `rel_*` fields are normalised by the line x-height."""
    index: int
    x0: int
    y0: int
    x1: int  # exclusive
    y1: int  # exclusive
    area: int
    holes: int
    hole_area: int
    stroke: float          # median ridge width (2 × distance-transform ridge), px
    darkness: float        # median gray of the component's pixels (0 = black)
    fill: float            # area / bbox area
    touches: tuple[str, ...]  # crop borders the component touches
    rel_h: float = 0.0
    rel_w: float = 0.0
    rel_cy: float = 0.0    # centre offset from band centre, in x-heights (+ = below)
    role: str = 'letter'   # letter | mark | fragment | large | rule

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def w(self) -> int:
        return self.x1 - self.x0

    @property
    def h(self) -> int:
        return self.y1 - self.y0


@dataclass
class LineGlyphs:
    gray: NDArray[np.float64]
    ink: NDArray[np.bool_]
    labels: NDArray[np.int32]
    components: list[Component]
    band: Band
    paper: float
    ink_level: float           # median gray of letter pixels
    stroke: float              # median letter stroke width
    letter_w: float            # median letter component width
    dt: NDArray[np.float64] = field(repr=False)

    @property
    def width(self) -> int:
        return int(self.gray.shape[1])

    @property
    def height(self) -> int:
        return int(self.gray.shape[0])


def _ridge(dt: NDArray[np.float64]) -> NDArray[np.bool_]:
    return (dt > 0) & (dt >= ndi.maximum_filter(dt, size=3))


def _xheight(heights: NDArray[np.float64]) -> float:
    """Mode of component heights (body letters dominate Greek prose): the height with most neighbours within ±12 %."""
    if not len(heights):
        return 0.0
    hs = np.sort(heights)
    counts = [np.sum((hs >= v * .88) & (hs <= v * 1.12)) for v in hs]
    best = hs[np.asarray(counts) >= .9 * max(counts)]
    return float(np.median(best))


def _ransac_line(xs: NDArray[np.float64], ys: NDArray[np.float64], tol: float,
                 rng: np.random.Generator) -> NDArray[np.bool_]:
    """Inliers of the best straight line through (xs, ys); deterministic given rng."""
    n = len(xs)
    best = np.ones(n, bool)
    if n < 3:
        return best
    best_n = -1
    pairs = rng.integers(0, n, size=(min(200, n * n), 2))
    for i, j in pairs:
        if xs[i] == xs[j]:
            continue
        slope = (ys[j] - ys[i]) / (xs[j] - xs[i])
        if abs(slope) > .2:   # > 11°: not a text line
            continue
        res = np.abs(ys - (ys[i] + slope * (xs - xs[i])))
        inl = res <= tol
        if inl.sum() > best_n:
            best_n, best = int(inl.sum()), inl
    return best


def _fit_curve(xs: NDArray[np.float64], ys: NDArray[np.float64], width: int) -> tuple[NDArray[np.float64], int]:
    """Straight fit, or quadratic when it clearly fits better (curl near the spine); returns values on 0..width-1."""
    grid = np.arange(width, dtype=np.float64)
    if len(xs) < 2:
        return np.full(width, float(np.median(ys)) if len(ys) else 0.0), 0
    lin = np.polyfit(xs, ys, 1)
    deg, coef = 1, lin
    if len(xs) >= 12 and np.ptp(xs) > .4 * width:
        quad = np.polyfit(xs, ys, 2)
        mad_l = np.median(np.abs(ys - np.polyval(lin, xs)))
        mad_q = np.median(np.abs(ys - np.polyval(quad, xs)))
        if mad_q < .75 * mad_l and np.ptp(np.polyval(quad, grid) - np.polyval(lin, grid)) > 1.5:
            deg, coef = 2, quad
    return np.polyval(coef, grid), deg


def _track(xs: NDArray[np.float64], ys: NDArray[np.float64], inl: NDArray[np.bool_], xh: float,
           k: int = 6) -> NDArray[np.bool_]:
    """Extend the inlier set outward, letter by letter: a point joins when it lies within tolerance of the local line
    through its k nearest accepted neighbours on the side it is approached from. Follows gradual bends and end curl
    while ascender tops and descender bottoms (≥ 0.4 x-height off) stay out."""
    acc = inl.copy()
    tol = .25 * xh + 1
    order = np.argsort(xs)
    changed = True
    while changed:
        changed = False
        ax = xs[acc]
        if len(ax) < 2:
            break
        lo, hi = ax.min(), ax.max()
        for direction in (-1, 1):
            cand = [i for i in order if not acc[i] and (xs[i] < lo if direction < 0 else xs[i] > hi)]
            cand.sort(key=lambda i: abs(xs[i] - (lo if direction < 0 else hi)))
            for i in cand:
                idx = np.nonzero(acc)[0]
                near = idx[np.argsort(np.abs(xs[idx] - xs[i]))[:k]]
                if len(near) >= 2 and np.ptp(xs[near]) > 0:
                    c = np.polyfit(xs[near], ys[near], 1)
                    if abs(c[0]) > .25:
                        c = np.array([0.0, np.median(ys[near])])
                else:
                    c = np.array([0.0, np.median(ys[near])])
                if abs(ys[i] - np.polyval(c, xs[i])) <= tol:
                    acc[i] = True; changed = True
                elif abs(xs[i] - xs[near].mean()) > 6 * xh:
                    break     # a gap of several letters without agreement: stop tracking on this side
    return acc


def _smooth_curve(xs: NDArray[np.float64], ys: NDArray[np.float64], width: int, xh: float) -> tuple[NDArray[np.float64], int]:
    """Locally weighted linear fit (tricube, bandwidth 5 x-heights) evaluated on every column; linear extrapolation
    with the end tangents beyond the supported range. Returns (curve, 1 if ~straight else 2)."""
    grid = np.arange(width, dtype=np.float64)
    if len(xs) < 3:
        return _fit_curve(xs, ys, width)
    bw = 5 * xh
    lo, hi = xs.min(), xs.max()
    knots = np.linspace(lo, hi, max(2, int((hi - lo) / (xh / 2)) + 1))
    vals = []
    for kx in knots:
        d = np.abs(xs - kx) / bw
        wgt = np.clip(1 - d ** 3, 0, None) ** 3
        if (wgt > 0).sum() < 3:
            d = np.abs(xs - kx); near = np.argsort(d)[:4]; wgt = np.zeros_like(xs); wgt[near] = 1
        W = wgt.sum(); mx = (wgt * xs).sum() / W; my = (wgt * ys).sum() / W
        vx = (wgt * (xs - mx) ** 2).sum()
        b = (wgt * (xs - mx) * (ys - my)).sum() / vx if vx > 0 else 0.0
        vals.append(my + b * (kx - mx))
    vals = np.array(vals)
    curve = np.interp(grid, knots, vals)
    # end tangents for extrapolation
    def tangent(sel):
        if sel.sum() >= 2 and np.ptp(xs[sel]) > 0:
            return np.polyfit(xs[sel], ys[sel], 1)[0]
        return 0.0
    sl_lo = tangent(xs <= lo + 3 * xh); sl_hi = tangent(xs >= hi - 3 * xh)
    curve = np.where(grid < lo, vals[0] + sl_lo * (grid - lo), curve)
    curve = np.where(grid > hi, vals[-1] + sl_hi * (grid - hi), curve)
    lin = np.polyval(np.polyfit(xs, ys, 1), grid)
    sup = (grid >= lo) & (grid <= hi)
    return curve, (2 if np.abs(curve - lin)[sup].max() > 1.5 else 1)


def line_glyphs(crop: Image.Image | NDArray[Any], *, seed: int = 0, xh_prior: float | None = None) -> LineGlyphs:
    """Components with descriptors and roles plus the letter band they define. CPU, a few ms for a 1500×80 strip.

    Roles: letter (body letter or a letter's main part), mark (accent / breathing / diaeresis above a letter, iota
    subscript below one), punct (small ink not attached to a letter: comma, full stop, ano teleia, apostrophe),
    fragment (small piece inside the band, typically a broken letter), neighbour (ink of the adjacent text lines),
    rule (long thin stroke), large (blob far bigger than a letter: stain, ornament, merged block).
    """
    gray = to_gray(crop)
    h, w = gray.shape
    ink = binarise(gray)
    labels, n = ndi.label(ink, structure=EIGHT)
    dt = ndi.distance_transform_edt(ink)
    ridge = _ridge(dt)
    paper = float(np.median(gray[~ink])) if (~ink).any() else 255.0
    raw: list[dict[str, Any]] = []
    for i, sl in enumerate(ndi.find_objects(labels), start=1):
        if sl is None:
            continue
        sub = labels[sl] == i
        area = int(sub.sum())
        if area < 3:
            continue
        filled = ndi.binary_fill_holes(sub)
        hl, hn = ndi.label(filled & ~sub)
        sizes = np.bincount(hl.ravel())[1:] if hn else np.zeros(0, int)
        rid = dt[sl][sub & ridge[sl]]
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        touches = tuple(name for name, hit in (('top', y0 == 0), ('bottom', y1 == h), ('left', x0 == 0), ('right', x1 == w))
                        if hit)
        raw.append(dict(index=i, x0=x0, y0=y0, x1=x1, y1=y1, area=area, holes=int((sizes >= 2).sum()),
                        hole_area=int(sizes[sizes >= 2].sum()), stroke=float(2 * np.median(rid)) if rid.size else 1.0,
                        darkness=float(np.median(gray[sl][sub])), fill=area / float((y1 - y0) * (x1 - x0)),
                        touches=touches))
    # faint-only blobs (smudges, bleed-through, faint letters) never drive the letter height or the band: those come
    # from clearly inked letters; faint ink inside the band is still read as letters later
    faint_cut = paper - .45 * (paper - (float(np.median(gray[ink])) if ink.any() else paper))
    raw_all, raw = raw, [r for r in raw if r['darkness'] <= faint_cut]
    free = [r for r in raw if not ({'top', 'bottom'} & set(r['touches'])) and r['area'] >= 12]
    xh = _xheight(np.array([r['y1'] - r['y0'] for r in free], float))
    xh_source = 'free_letters'
    if free:
        # broken (faint) letters flood the count mode with piece heights; the mode over substantial components
        # resists that. Rendered lines (200, 31 fonts): plain mode median |error| 7.1 %; switch only on fragmentation.
        p90 = float(np.percentile([r['area'] for r in free], 90))
        sub = _xheight(np.array([r['y1'] - r['y0'] for r in free if r['area'] >= .25 * p90], float))
        if sub > 1.5 * xh:
            xh, xh_source = sub, 'substantial_letters'
    if xh_prior:
        xh, xh_source = float(xh_prior), 'prior'
    elif len([r for r in free if r['area'] >= .15 * xh * xh]) < 4:
        # too few complete letters (heavily clipped crop): width-based estimate, x-height ≈ XH_PER_WIDTH × letter width
        wide = [r['x1'] - r['x0'] for r in raw if r['area'] >= 12 and r['x1'] - r['x0'] >= 4]
        xh, xh_source = (XH_PER_WIDTH * _xheight(np.array(wide, float)) if wide else h / 3), 'letter_width'
    xh = max(xh, 3.0)
    # baseline evidence: a free bottom gives the baseline; a free top gives baseline = top + x-height. Clipped letters
    # still contribute their visible edge, so a crop cut through the letters keeps its band. Body letters dominate
    # Greek prose, so ascender tops / descender bottoms are outliers for the robust fit.
    px, py, pk = [], [], []
    for r in raw:
        rw, rh = r['x1'] - r['x0'], r['y1'] - r['y0']
        if not (.3 * xh <= rw <= 1.8 * xh) or r['area'] < .08 * xh * xh:
            continue
        touch = set(r['touches'])
        cx = (r['x0'] + r['x1']) / 2
        if 'bottom' not in touch and ('top' in touch or .6 * xh <= rh <= 1.4 * xh):
            px.append(cx); py.append(float(r['y1'])); pk.append('bottom')
        if 'top' not in touch and ('bottom' in touch or .6 * xh <= rh <= 1.4 * xh):
            px.append(cx); py.append(float(r['y0']) + xh); pk.append('top')
    bx, by = np.array(px, float), np.array(py, float)
    rng = np.random.default_rng(seed)
    inl = _ransac_line(bx, by, .15 * xh + 1, rng) if len(bx) else np.zeros(0, bool)
    bottom, deg = _fit_curve(bx[inl], by[inl], w) if inl.any() else (np.full(w, min(h - 1.0, h * .7)), 0)
    # grow: evidence close to the current curve joins it, so the fit can follow a gradual trail or end curl
    for _ in range(4):
        if not len(bx):
            break
        res = np.abs(by - bottom[np.clip(bx.astype(int), 0, w - 1)])
        grown = res <= .22 * xh + 1
        if grown.sum() < 2 or np.array_equal(grown, inl):
            break
        inl = grown
        bottom, deg = _fit_curve(bx[inl], by[inl], w)
    if inl.sum() >= 3:
        tracked = _track(bx, by, inl, xh)
        if tracked.sum() > inl.sum():
            # model selection on the tracked evidence: the bending curve must clearly beat a straight line
            sx, sy = bx[tracked], by[tracked]
            curve, cdeg = _smooth_curve(sx, sy, w, xh)
            lin = np.polyfit(sx, sy, 1)
            r_lin = np.abs(sy - np.polyval(lin, sx)); r_cur = np.abs(sy - curve[np.clip(sx.astype(int), 0, w - 1)])
            if np.percentile(r_cur, 90) < SEL_RATIO * np.percentile(r_lin, 90) and np.percentile(r_lin, 90) > SEL_FLOOR * xh:
                inl, bottom, deg = tracked, curve, cdeg
            elif (r_lin <= .22 * xh + 1).all():
                inl, bottom, deg = tracked, np.polyval(lin, np.arange(w, dtype=np.float64)), 1
    support = tuple((float(x), float(y), k) for x, y, k, i in zip(bx, by, pk, inl) if i)
    top = bottom - xh

    def band(cx: float) -> tuple[float, float]:
        i = int(np.clip(cx, 0, w - 1))
        return float(top[i]), float(bottom[i])

    roles: dict[int, str] = {}
    raw = raw_all   # every component gets a role, faint ones included
    # pass 1: big / letter-like components
    for r in raw:
        rh, rw = (r['y1'] - r['y0']) / xh, (r['x1'] - r['x0']) / xh
        t, b = band((r['x0'] + r['x1']) / 2)
        ov = max(0.0, min(r['y1'], b) - max(r['y0'], t)) / max(1.0, min(r['y1'] - r['y0'], xh))
        touch_tb = bool({'top', 'bottom'} & set(r['touches']))
        if (rw > 6 and rh < .5) or (rh > 3 and rw < .5):
            roles[r['index']] = 'rule'
        elif touch_tb and ov < .3 and (rh >= .8 or r['y1'] < t - NEIGHBOUR_GAP_ABOVE * xh
                                       or r['y0'] > b + NEIGHBOUR_GAP_BELOW * xh):
            roles[r['index']] = 'neighbour'   # small border-touching ink near the band is decided in pass 2
        elif rh > 2.6 or rw > 6 or r['area'] > 6 * xh * xh:
            roles[r['index']] = 'large'
        elif ov >= .5 and rh >= .5:
            roles[r['index']] = 'letter'
    letters = [r for r in raw if roles.get(r['index']) == 'letter']

    def letter_under(r: dict[str, Any], above: bool) -> bool:
        cx = (r['x0'] + r['x1']) / 2
        for q in letters:
            if q['x0'] - .15 * xh <= cx <= q['x1'] + .15 * xh:
                gap = q['y0'] - r['y1'] if above else r['y0'] - q['y1']
                if gap < .9 * xh:
                    return True
        return False

    # pass 2: small components, by position relative to the band and to the letters
    for r in raw:
        if r['index'] in roles:
            continue
        t, b = band((r['x0'] + r['x1']) / 2)
        cy = (r['y0'] + r['y1']) / 2
        if cy < t + .1 * xh:             # above the body
            if r['y1'] < t - NEIGHBOUR_GAP_ABOVE * xh:
                roles[r['index']] = 'neighbour'
            else:
                roles[r['index']] = 'mark' if letter_under(r, above=True) else 'punct'
        elif cy > b - .1 * xh:           # at or below the baseline
            if r['y0'] > b + NEIGHBOUR_GAP_BELOW * xh:
                roles[r['index']] = 'neighbour'
            elif r['y0'] >= b - .2 * xh and letter_under(r, above=False) and (r['x1'] - r['x0']) < .6 * xh:
                roles[r['index']] = 'mark'   # iota subscript
            else:
                roles[r['index']] = 'punct'
        else:                            # inside the band
            small = r['area'] < .12 * xh * xh and (r['y1'] - r['y0']) < .45 * xh
            if small:
                roles[r['index']] = 'punct' if not any(q['x0'] <= r['x0'] and r['x1'] <= q['x1'] for q in letters) \
                    and cy > t + .25 * xh else 'fragment'
            else:
                roles[r['index']] = 'fragment' if (r['y1'] - r['y0']) < .5 * xh else 'letter'
    comps: list[Component] = []
    for r in raw:
        t, b = band((r['x0'] + r['x1']) / 2)
        comps.append(Component(**r, rel_h=(r['y1'] - r['y0']) / xh, rel_w=(r['x1'] - r['x0']) / xh,
                               rel_cy=((r['y0'] + r['y1']) / 2 - (t + b) / 2) / xh, role=roles[r['index']]))
    lets = [c for c in comps if c.role == 'letter']
    stroke = float(np.median([c.stroke for c in lets])) if lets else 1.0
    ink_level = float(np.median(gray[ink])) if ink.any() else paper
    letter_w = _xheight(np.array([c.w for c in lets], float)) if lets else xh
    return LineGlyphs(gray=gray, ink=ink, labels=labels, components=comps, band=Band(top, bottom, xh, len(support), support, deg, xh_source),
                      paper=paper, ink_level=ink_level, stroke=stroke, letter_w=letter_w, dt=dt)

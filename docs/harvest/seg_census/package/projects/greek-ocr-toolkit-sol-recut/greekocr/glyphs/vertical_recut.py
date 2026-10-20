"""Opt-in native vertical tightening of existing Google crops; no row creation.

All coordinates are half-open native pixels. Stable guide evidence is fitted on
``guide_box`` (the original source geometry), never on a previous recut. Output
is a literal rectangle inside ``crop_box``; callers own publication/admission.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Any, Sequence

import numpy as np
from PIL import Image

from .components import to_gray
from .recut import fit_box


@dataclass(frozen=True)
class TightenParams:
    top_margin_xh: float = .2
    bottom_margin_xh: float = .2
    neighbour_center_clearance_xh: float = .5
    max_own_pixels_lost: int = 0
    version: str = 'vertical-tighten-1'

    def __post_init__(self):
        values = (self.top_margin_xh, self.bottom_margin_xh,
                  self.neighbour_center_clearance_xh)
        if not all(math.isfinite(v) and v >= 0 for v in values):
            raise ValueError('margins and clearance must be finite and nonnegative')
        if self.max_own_pixels_lost != 0:
            raise ValueError('this version requires zero supplied own-component loss')

    def canonical(self) -> bytes:
        return json.dumps(asdict(self), sort_keys=True, separators=(',', ':'),
                          allow_nan=False).encode()

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical()).hexdigest()


@dataclass(frozen=True)
class FontBand:
    """Own-line guide samples on native X, independent of the mutable crop."""
    x0: int
    x1: int
    xheight: float
    top: Any
    bottom: Any
    baseline: Any
    meanline: Any
    source: str = 'supplied-own-guides'


@dataclass(frozen=True)
class Tightened:
    old_box: tuple[int, int, int, int]
    new_box: tuple[int, int, int, int]
    proposed_box: tuple[int, int, int, int]
    params_sha256: str
    status: str
    xheight: float | None
    own_pixels: int | None
    proposed_own_pixels_lost: int | None
    neighbour_top: float | None = None
    neighbour_bottom: float | None = None

    @property
    def changed(self) -> bool:
        return self.old_box != self.new_box


def band_from_record(row: dict) -> FontBand:
    """Reuse a page-runtime six-guide record without fitting or segmentation."""
    return FontBand(int(row['x0']), int(row['x1']), float(row['xheight']),
                    np.minimum(row['font_top'], row['accent_top']), row['font_bottom'],
                    row['baseline'], row['meanline'], 'saved-page-font-guides')


def fit_font_band(page: Image.Image | np.ndarray, guide_box: Sequence[int]) -> FontBand | None:
    """Existing crop fitter only, with split emission disabled; one envelope."""
    fits = fit_box(to_gray(page), tuple(map(int, guide_box)), splits=False)
    if not fits:
        return None
    # Multiple horizontal font segments still form exactly one original crop.
    a, b = min(f.x0 for f in fits), max(f.x1 for f in fits)
    xs = np.arange(a, b)
    top, bottom, base, mean = (np.full(b-a, np.nan) for _ in range(4))
    for f in fits:
        sl = slice(f.x0-a, f.x1-a)
        bs = f.base_at(xs[sl])
        top[sl], bottom[sl] = bs-f.up, bs+f.down
        base[sl], mean[sl] = bs, bs-f.rise
    valid = np.isfinite(base)
    if not valid.any():
        return None
    for curve in (top, bottom, base, mean):
        curve[~valid] = np.interp(xs[~valid], xs[valid], curve[valid])
    return FontBand(a, b, float(np.median([f.xh for f in fits])),
                    top, bottom, base, mean, 'existing-fit_box-splits_false')


def tighten_box(crop_box: Sequence[int], band: FontBand | None,
                neighbour_tokens: Sequence[Sequence[float]], *,
                params: TightenParams = TightenParams(),
                own_pixels: tuple[np.ndarray, np.ndarray] | None = None) -> Tightened:
    """Intersect own font band, adjacent token edges, and original rectangle.

    ``neighbour_tokens`` excludes this Google line's tokens; tokens in other
    columns and same-row fragments cannot clip the crop. ``own_pixels`` is
    (native y, native x) assigned-component evidence, not all foreground.
    A conflict or missing/invalid guide returns the original unchanged.
    """
    old = tuple(map(int, crop_box))
    x0, y0, x1, y1 = old
    if x1 <= x0 or y1 <= y0 or min(old) < 0:
        raise ValueError('invalid original crop')
    status, proposed, nt, nb, xh = 'no_font_band', old, None, None, None
    total, lost = None, None
    if band is not None:
        xh = float(band.xheight)
        curves = [np.asarray(c, dtype=float) for c in
                  (band.top, band.bottom, band.baseline, band.meanline)]
        valid = (math.isfinite(xh) and xh > 0 and band.x1 > band.x0 and
                 all(c.shape == (band.x1-band.x0,) and np.isfinite(c).all() for c in curves))
        if valid:
            a, b = max(x0, band.x0), min(x1, band.x1)
            if b > a:
                sl = slice(a-band.x0, b-band.x0)
                top, bottom, baseline, mean = [c[sl] for c in curves]
                cy = float(np.median((baseline+mean)/2))
                lo = float(top.min()) - params.top_margin_xh*xh
                hi = float(bottom.max()) + params.bottom_margin_xh*xh
                above, below = [], []
                for box in neighbour_tokens:
                    tx0, ty0, tx1, ty1 = map(float, box)
                    if not np.isfinite(box).all() or tx1 <= tx0 or ty1 <= ty0:
                        raise ValueError('invalid neighbour token')
                    if min(x1, tx1) <= max(x0, tx0):
                        continue
                    tc = (ty0+ty1)/2
                    if tc < cy-params.neighbour_center_clearance_xh*xh:
                        above.append(ty1)
                    elif tc > cy+params.neighbour_center_clearance_xh*xh:
                        below.append(ty0)
                nt, nb = (max(above) if above else None), (min(below) if below else None)
                # Token clipping rounds inward: every neighbour token stays out.
                t = max(y0, math.floor(lo), math.ceil(nt) if nt is not None else y0)
                u = min(y1, math.ceil(hi), math.floor(nb) if nb is not None else y1)
                if t < u and t <= float(mean.min()) and u >= float(baseline.max()):
                    proposed = (x0, t, x1, u)
                    status = 'tightened' if proposed != old else 'unchanged'
                else:
                    status = 'conflicting_neighbour_or_band'
            else:
                status = 'no_horizontal_guide_overlap'
        else:
            status = 'invalid_font_band'
    if own_pixels is not None:
        yy, xx = map(np.asarray, own_pixels)
        if yy.shape != xx.shape:
            raise ValueError('own component coordinate shapes differ')
        was = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
        total = int(was.sum())
        lost = int((was & ((yy < proposed[1]) | (yy >= proposed[3]))).sum())
        if lost > params.max_own_pixels_lost:
            return Tightened(old, old, proposed, params.sha256, 'own_ink_guard', xh,
                             total, lost, nt, nb)
    return Tightened(old, proposed, proposed, params.sha256, status, xh, total, lost, nt, nb)


def tighten_page(page: Image.Image, lines: Sequence[dict], *,
                 params: TightenParams = TightenParams()) -> list[Tightened]:
    """Any page with native Google geometry; no cache/provider/source dependency.

    Records contain stable ``guide_box``, ``crop_bbox``, and native ``tokens``.
    Optional ``band`` and ``own_pixels`` reuse existing page-fit/ownership data.
    No I/O, admission, row creation, horizontal change, or resampling occurs.
    """
    out = []
    for i, line in enumerate(lines):
        box = line['crop_bbox']
        if not (0 <= box[0] < box[2] <= page.width and 0 <= box[1] < box[3] <= page.height):
            raise ValueError('crop outside native page')
        band = line.get('band')
        if band is None:
            band = fit_font_band(page, line['guide_box'])
        neighbours = [t for j, other in enumerate(lines) if j != i for t in other['tokens']]
        out.append(tighten_box(box, band, neighbours, params=params,
                               own_pixels=line.get('own_pixels')))
    return out

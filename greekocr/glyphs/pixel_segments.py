"""Pixel-only rough regions: graphical stops, persistent gutters, then row valleys.

The boxes are seeds, not OCR crops. A valley need not exist between two curled
lines, so a box can deliberately contain several lines. Lengths below are in
estimated letter heights (or fractions of the page), never a document's pixels.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray
from PIL import Image
from scipy import ndimage as ndi

from .components import EIGHT, _xheight, binarise, to_gray


@dataclass
class PixelPage:
    gray: NDArray
    ink: NDArray
    labels: NDArray
    components: NDArray   # x0, y0, x1, y1, area, label, darkness
    barriers: NDArray
    gutters: list[tuple[int, int, int, int]]
    boxes: list[tuple[int, int, int, int]]
    xheight: float


def _runs(mask):
    edges = np.diff(np.r_[False, mask, False].astype(np.int8))
    return [(int(a), int(b)) for a, b in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1))]


def _gray(page: Image.Image | NDArray[Any]) -> NDArray:
    arr = np.asarray(page) if not isinstance(page, Image.Image) else np.asarray(page.convert('L'))
    if arr.ndim not in (2, 3) or (arr.ndim == 3 and arr.shape[2] not in (3, 4)) or not arr.size:
        raise ValueError('page must be a nonempty grayscale or RGB image')
    gray = to_gray(page)
    if not np.isfinite(gray).all() or gray.min() < 0 or gray.max() > 255:
        raise ValueError('page pixels must be finite and in [0,255] or [0,1]')
    if gray.max() <= 1:
        gray = gray * 255
    return gray


def _records(gray, labels):
    sizes = np.bincount(labels.ravel())
    rows = []
    for k, sl in enumerate(ndi.find_objects(labels), 1):
        if sl is None or sizes[k] < 3:
            continue
        y, x = sl
        rows.append((x.start, y.start, x.stop, y.stop, sizes[k], k,
                     float(np.median(gray[sl][labels[sl] == k]))))
    return np.asarray(rows, float).reshape(-1, 7)


def _rule_mask(ink, xh):
    """Opening along several near-vertical directions, at a letter-scaled size.

    Work at ~8 px/x-height. Shearing makes even a tilted table frame vertical;
    opening separates its vertical rules from its horizontal bars and letters.
    The conservative dilation covers rounding and the original rule thickness.
    """
    scale = min(1., 8 / xh)
    # Max pooling preserves thin rules that nearest-neighbour decimation loses.
    pooled = ndi.maximum_filter(ink, max(1, int(np.ceil(1 / scale))))
    small = ndi.zoom(pooled.astype(np.uint8), scale, order=0).astype(bool)
    h, w = small.shape
    rows, cols = np.arange(h)[:, None], np.arange(w)[None, :]
    length = max(3, round(4 * xh * scale))
    result = np.zeros_like(small)
    for slope in np.linspace(-.16, .16, 9):
        shift = np.rint(slope * (rows - h / 2)).astype(int)
        xx = cols + shift
        sheared = small[rows, np.clip(xx, 0, w - 1)] & (xx >= 0) & (xx < w)
        joined = ndi.maximum_filter1d(sheared, max(1, round(.15 * xh * scale)), axis=0)
        opened = ndi.maximum_filter1d(ndi.minimum_filter1d(joined, length, axis=0), length, axis=0)
        back = cols - shift
        result |= opened[rows, np.clip(back, 0, w - 1)] & (back >= 0) & (back < w)
    result = ndi.maximum_filter(result, max(1, round(.25 * xh * scale)) | 1)
    ys = np.minimum((np.arange(ink.shape[0]) * scale).astype(int), h - 1)
    xs = np.minimum((np.arange(ink.shape[1]) * scale).astype(int), w - 1)
    return result[ys[:, None], xs]


def _gaps(mask, xh, *, persistent=True):
    """Blank vertical lanes; repeated interline evidence distinguishes word gaps."""
    h, w = mask.shape
    col = ndi.uniform_filter1d(mask.sum(axis=0).astype(float), max(1, round(.3 * xh)))
    if not col.any():
        return []
    low = col <= max(.5, .035 * np.percentile(col[col > 0], 85))
    gaps = []
    for a, b in _runs(low):
        if a == 0 or b == w or b - a < (1.8 if persistent else 10) * xh:
            continue
        left = mask[:, max(0, a - round(12 * xh)):a]
        right = mask[:, b:min(w, b + round(12 * xh))]
        if not left.any() or not right.any():
            continue
        ly, ry = np.flatnonzero(left.any(axis=1)), np.flatnonzero(right.any(axis=1))
        # At least two vertically separated lines on BOTH sides. A single
        # justified line can have a large word space without becoming columns.
        repeated = min(np.ptp(ly), np.ptp(ry)) > 3 * xh
        if repeated or b - a >= 10 * xh:
            gaps.append((int(a), int(b)))
    return gaps


def prepare_pixels(page: Image.Image | NDArray[Any]) -> PixelPage:
    gray = _gray(page)
    h, w = gray.shape
    if np.ptp(gray) < 1:
        z = np.zeros(gray.shape, bool)
        return PixelPage(gray, z, z.astype(int), np.empty((0, 7)), z, [], [], 3.)
    ink = binarise(gray, window=max(15, round(.04 * min(h, w))) | 1)
    labels, _ = ndi.label(ink, structure=EIGHT)
    cc = _records(gray, labels)
    if not len(cc):
        return PixelPage(gray, ink, labels, cc, np.zeros_like(ink), [], [], 3.)
    heights, widths = cc[:, 3] - cc[:, 1], cc[:, 2] - cc[:, 0]
    sel = ((heights >= .002 * h) & (heights <= .1 * h)
           & (widths >= .001 * w) & (widths < .12 * w))
    substantial = cc[sel]
    if len(substantial):
        substantial = substantial[substantial[:, 4] >= .15 * np.percentile(substantial[:, 4], 90)]
    xh = max(3., _xheight(substantial[:, 3] - substantial[:, 1]) if len(substantial) else min(h, w) / 100)
    barriers = _rule_mask(ink, xh)
    # Whole connected graphics are removed BEFORE projection (the original
    # segmenter's frame/border rejection); enclosed table text is not removed.
    graphics = (heights > 4 * xh) | (widths > 14 * xh) | (cc[:, 4] > 18 * xh * xh)
    keep = np.ones(labels.max() + 1, bool); keep[0] = False
    keep[cc[graphics, 5].astype(int)] = False
    keep[cc[cc[:, 4] < max(3, .012 * xh * xh), 5].astype(int)] = False
    clean = keep[labels] & ~barriers
    for q in cc[graphics]:
        a, t, b, bot = q[:4].astype(int)
        hh, ww = bot - t, b - a
        fill = q[4] / (hh * ww)
        # Filled illustrations / ornaments, and compact circular stamp frames.
        # A page/table frame is sparse and much larger than this stamp test.
        illustration = min(hh, ww) > 5 * xh and fill > .18
        compact_frame = min(hh, ww) > 5 * xh and max(hh, ww) < 18 * xh and .65 < ww / hh < 1.5
        if illustration or compact_frame:
            clean[t:bot, a:b] = False
    labels, _ = ndi.label(clean, structure=EIGHT)
    cc = _records(gray, labels)
    if not len(cc):
        return PixelPage(gray, clean, labels, cc, barriers, [], [], xh)

    # Coarse horizontal zones, snapped to row valleys. Within each, rules and
    # persistent whitespace establish columns. A zone may contain many lines.
    profile = ndi.uniform_filter1d(clean.sum(axis=1).astype(float), max(1, round(.25 * xh)))
    zones = [0]
    while zones[-1] + 18 * xh < h:
        a = round(zones[-1] + 12 * xh); b = min(h, round(zones[-1] + 22 * xh))
        zones.append(a + int(np.argmin(profile[a:b])))
    zones.append(h)
    boxes, gutters = [], []
    for y0, y1 in zip(zones[:-1], zones[1:]):
        band = clean[y0:y1]
        local = cc[(cc[:, 1] >= y0) & (cc[:, 3] <= y1) & (cc[:, 4] > .07 * xh * xh)]
        local_xh = xh
        if len(local) >= 8:
            measured = _xheight(local[:, 3] - local[:, 1])
            if .45 * xh < measured < 2 * xh:
                local_xh = measured
        # Rules need only span the occupied rows of a table zone, not 80% of
        # the entire page (the crop rule test's known limitation).
        stop = barriers[y0:y1].sum(axis=0) >= min(3 * xh, .35 * (y1 - y0))
        gaps = _gaps(band, local_xh)
        cuts = np.zeros(w, bool)
        for a, b in _runs(stop):
            cuts[a:b] = True
        for a, b in gaps:
            cuts[a:b] = True
            gutters.append((a, y0, b, y1))
        for a, b in _runs(~cuts):
            sub = band[:, a:b]
            if not sub.any():
                continue
            sm = ndi.uniform_filter1d(sub.sum(axis=1).astype(float), max(1, round(.25 * xh)))
            # Deep row valleys only: do not pretend a curled multi-line region
            # is already a single line. The crop fitter resolves it next.
            active = sm > max(.5, .045 * float(sm.max()))
            active = ndi.maximum_filter1d(active, max(1, round(.4 * xh)))
            for t, bot in _runs(active):
                ys, xs = np.nonzero(sub[t:bot])
                if not len(xs) or len(xs) < .15 * xh * xh:
                    continue
                boxes.append((a + int(xs.min()), y0 + t, a + int(xs.max()) + 1, y0 + bot))
    return PixelPage(gray, clean, labels, cc, barriers, gutters, boxes, xh)

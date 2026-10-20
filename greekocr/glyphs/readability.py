"""Readability and OCR relevance of a line crop (owner 8 Oct 16:40), from the glyph tools' measurements and limits
calibrated on synthetic strips read by an OCR model (CLLG; docs/records/glyphs/GLYPHS_CALIBRATION.md).

Per column segment the main line is judged; along x, each column is over a limit when:
  accent_cut  > LIMITS['accent_cut']   share of the accent / tall-letter zone (ascender line → mean line) cut by the top
  top_cut     > LIMITS['top_cut']      share of the letter body cut by the top edge
  tail_cut    > LIMITS['tail_cut']     share of the tail zone (baseline → hanging bottom) cut by the bottom edge
  bottom_cut  > LIMITS['bottom_cut']   share of the letter body cut by the bottom edge
Line-level: |skew| > LIMITS['skew_deg'], ink contrast < LIMITS['contrast'], broken share > LIMITS['broken'],
merged share > LIMITS['merged']. Target: clear when one main line dominates its column and the crop holds one column.
verdict: readable (nothing over a limit), partly (some x-ranges over), unreadable (≥ UNREADABLE_SHARE of the width over).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from PIL import Image

from greekocr.glyphs.baseline import skew_line, text_lines
from greekocr.glyphs.columns import column_segments
from greekocr.glyphs.ink import ink_profile
from greekocr.glyphs.letters import letter_boxes

__all__ = ['LIMITS', 'READER_LIMITS', 'Readability', 'readability']

# Limits from 1,760 synthetic strips (40 base texts × 44 conditions) read by two OCR models (docs/records/glyphs/GLYPHS_CALIBRATION.md,
# 8 Oct). Rule: the first measured bin whose median CER leaves the reader's clean band. Provenance per value (CP-G4 F4):
#   cllg accent_cut .3, top_cut .05, bottom_cut .1  — measured crossings (adverse bins rest on ~6 base texts: thin)
#   cllg tail_cut None — no measured tail bin left the band (0.6–1.0 bins: median NFC .032–.047); no limit established
#   cllg skew_deg 4.0  — POLICY: 3° in band, 5° at the band edge (NFC .050, NFD .041); 4° was not tested
#   e1   — none established: its clean band (median .22 + 2 × IQR .41) is inflated by the renderer's ±2° skew, so no
#          condition leaves it; E1 must be re-measured on level controls before any E1 limit exists.
# None = no limit: the quantity is still measured and reported but never flags. Measured on crop-edge geometry as
# calib_measure.py computes it (support-averaged per strip); production applies them per x-position (CP-G4 F3: not
# yet the same measurement — the page recut replaces crop-edge guessing with what the crop actually lost).
READER_LIMITS: dict[str, dict[str, float | None]] = {
    'cllg': {'accent_cut': .3, 'top_cut': .05, 'tail_cut': None, 'bottom_cut': .1, 'skew_deg': 4.0},
    'e1':   {'accent_cut': None, 'top_cut': None, 'tail_cut': None, 'bottom_cut': None, 'skew_deg': None},
}
LIMITS = READER_LIMITS['cllg']
UNREADABLE_SHARE = .5   # POLICY, not calibrated against OCR outcomes (CP-G4 F3)


@dataclass
class Readability:
    verdict: str                                  # readable | partly | unreadable
    target: str                                   # clear | ambiguous
    reasons: list[str] = field(default_factory=list)
    spans: list[dict[str, Any]] = field(default_factory=list)    # {segment, x0, x1, reason, worst}
    measures: dict[str, Any] = field(default_factory=dict)


def _spans(mask: np.ndarray, values: np.ndarray, reason: str, seg: int, x_off: int, min_len: int) -> list[dict]:
    out, padded = [], np.concatenate([[False], mask, [False]])
    edges = np.nonzero(padded[1:] != padded[:-1])[0]
    for a, b in zip(edges[::2], edges[1::2]):
        if b - a >= min_len:
            out.append(dict(segment=seg, x0=int(x_off + a), x1=int(x_off + b), reason=reason, worst=round(float(values[a:b].max()), 3)))
    return out


def readability(crop: Image.Image, *, xh_prior: float | None = None, limits: dict[str, float | None] = LIMITS) -> Readability:
    """Verdict and reasons for one crop under a reader's limits (READER_LIMITS['cllg'] by default)."""
    kw = {'xh_prior': xh_prior} if xh_prior else {}
    segs = [s for s in column_segments(crop, **kw) if s.glyphs is not None]
    reasons, spans, measures = [], [], {'segments': []}
    over_cols = total_cols = 0
    full_lines = 0
    for k, sg in enumerate(segs):
        g = sg.glyphs; h, w, xh = g.height, g.width, g.band.xh
        lines = text_lines(g); main = lines[0]
        full_lines += 1 + sum(1 for l in lines[1:] if l.visible >= .5)
        prof = {
            'accent_cut': np.clip((0 - main.ascender) / np.maximum(main.mean - main.ascender, 1), 0, 1),
            'top_cut': np.clip(-main.mean / xh, 0, 1),
            'tail_cut': np.clip((main.descender - h) / np.maximum(main.descender - main.base, 1), 0, 1),
            'bottom_cut': np.clip((main.base - h) / xh, 0, 1),
        }
        # a zone only counts as cut where the line's own ink reaches that crop edge (a tight crop that ends just
        # above the tallest ink loses nothing even if the estimated guide line lies outside it)
        from scipy import ndimage as ndi
        own = [c for c in g.components if c.role not in ('neighbour', 'rule')]
        touch_top = np.zeros(w, bool); touch_bot = np.zeros(w, bool)
        for c in own:
            if c.y0 == 0: touch_top[c.x0:c.x1] = True
            if c.y1 == h: touch_bot[c.x0:c.x1] = True
        near = max(1, int(.5 * xh))
        touch_top = ndi.binary_dilation(touch_top, iterations=near); touch_bot = ndi.binary_dilation(touch_bot, iterations=near)
        for key in ('accent_cut', 'top_cut'):
            prof[key] = np.where(touch_top, prof[key], 0.0)
        for key in ('tail_cut', 'bottom_cut'):
            prof[key] = np.where(touch_bot, prof[key], 0.0)
        lo, hi = main.x0, main.x1 + 1
        bad = np.zeros(w, bool)
        for key, arr in prof.items():
            if limits.get(key) is None:
                continue
            m = np.zeros(w, bool); m[lo:hi] = arr[lo:hi] > limits[key]
            spans += _spans(m, arr, key, k, sg.x0, max(2, int(.5 * xh)))
            bad |= m
        boxes = letter_boxes(g); sk = skew_line(g, boxes); ink = ink_profile(g, boxes)
        n = max(1, len(ink.letters))
        seg_m = dict(x0=sg.x0, x1=sg.x1, xh=xh, skew=sk.angle_deg, contrast=float(g.paper - g.ink_level),
                     broken=sum(l.state == 'broken' for l in ink.letters) / n,
                     merged=sum(l.state == 'merged' for l in ink.letters) / n,
                     **{f'{key}_mean': float(arr[lo:hi].mean()) for key, arr in prof.items()})
        measures['segments'].append(seg_m)
        line_bad = []
        if limits.get('skew_deg') is not None and abs(sk.angle_deg) > limits['skew_deg']: line_bad.append(f'skew {sk.angle_deg:+.1f}°')
        if not ink.letters: line_bad.append('no letters found')
        if line_bad:
            bad[lo:hi] = True
            reasons += [f'column {k + 1}: ' + r if len(segs) > 1 else r for r in line_bad]
        over_cols += int(bad[lo:hi].sum()); total_cols += hi - lo
    for key in ('accent_cut', 'top_cut', 'tail_cut', 'bottom_cut'):
        if any(s['reason'] == key for s in spans):
            reasons.append({'accent_cut': 'accents / tall letters cut at the top', 'top_cut': 'letter bodies cut at the top',
                            'tail_cut': 'tails cut at the bottom', 'bottom_cut': 'letter bodies cut at the bottom'}[key])
    share = over_cols / max(1, total_cols)
    verdict = 'readable' if share == 0 else ('unreadable' if share >= UNREADABLE_SHARE else 'partly')
    target = 'clear' if len(segs) <= 1 and full_lines <= 1 else 'ambiguous'
    if len(segs) > 1: reasons.append(f'{len(segs)} columns in the crop')
    if full_lines > len(segs): reasons.append(f'{full_lines} full text lines in the crop')
    measures['over_share'] = round(share, 3)
    return Readability(verdict, target, reasons, spans, measures)

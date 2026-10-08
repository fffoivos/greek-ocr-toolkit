"""Column segments: a crop that spans two print columns is cut at the vertical rule between them, and each segment is
measured on its own (owner 8 Oct: extend a line within a column, never align two columns that do not share a line)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray
from PIL import Image
from scipy import ndimage as ndi

from greekocr.glyphs.components import EIGHT, LineGlyphs, binarise, line_glyphs, to_gray
from greekocr.glyphs.letters import letter_boxes

__all__ = ['Segment', 'column_rules', 'column_segments', 'GAP_CUT', 'ALIGN_TOL']

RULE_HEIGHT = .8      # a column rule spans ≥ 80 % of the crop height
RULE_ASPECT = .12     # and is at most this wide relative to its height
RULE_OVER_LETTERS = 1.5   # and at least this many times the 90th-percentile component height
MIN_SEGMENT = 1.2     # segments narrower than this many crop heights are merged into their neighbour
GAP_CUT = 3.0         # a blank gap wider than this many x-heights is a candidate cut (word spaces: p99 1.9, 444 crops)
ALIGN_TOL = .25       # the two sides are one line when their baselines meet within this many x-heights
SOFT_MIN = 6.0        # a soft cut needs ≥ SOFT_MIN x-heights of text and ≥ 6 support points on each side


@dataclass
class Segment:
    x0: int
    x1: int
    glyphs: LineGlyphs | None      # None when the segment holds no measurable line


def column_rules(crop: Image.Image | NDArray[Any]) -> list[tuple[int, int]]:
    """x-ranges of vertical rules: tall thin ink spanning most of the crop height."""
    gray = to_gray(crop)
    h = gray.shape[0]
    ink = binarise(gray)
    lab, n = ndi.label(ink, structure=EIGHT)
    boxes = [sl for sl in ndi.find_objects(lab) if sl is not None]
    def candidate(sl) -> bool:
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        return hh >= RULE_HEIGHT * h and ww <= RULE_ASPECT * hh
    # the letter-height reference excludes the rule candidates themselves (CP-G3 F6: with sparse text a rule vetoed itself)
    heights = np.array([sl[0].stop - sl[0].start for sl in boxes
                        if not candidate(sl) and (sl[0].stop - sl[0].start) * (sl[1].stop - sl[1].start) >= 12])
    # a rule is clearly taller than the letters around it (in a short crop, letters cut by both edges span it too)
    tall_letter = float(np.percentile(heights, 90)) if heights.size else 0.0
    out = []
    for sl in boxes:
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if hh >= RULE_HEIGHT * h and ww <= RULE_ASPECT * hh and hh >= RULE_OVER_LETTERS * tall_letter:
            out.append((sl[1].start, sl[1].stop))
    return sorted(out)


def column_segments(crop: Image.Image | NDArray[Any], **kw: Any) -> list[Segment]:
    """Cut at rules; each segment gets its own line_glyphs (own band, skew, bends, guide lines)."""
    img = crop if isinstance(crop, Image.Image) else Image.fromarray(np.asarray(crop).astype(np.uint8))
    w, h = img.size
    cuts = [0]
    for a, b in column_rules(img):
        cuts += [a, b]
    cuts.append(w)
    spans = [(cuts[i], cuts[i + 1]) for i in range(0, len(cuts), 2)]
    merged: list[list[int]] = []
    for a, b in spans:
        if merged and (b - a < MIN_SEGMENT * h or merged[-1][1] - merged[-1][0] < MIN_SEGMENT * h):
            merged[-1][1] = b          # too narrow to hold a line on its own: keep with its neighbour
        else:
            merged.append([a, b])
    # soft cuts: very wide blank gaps; kept only when the two sides do not continue one line. Gap widths are in
    # x-heights, so they need a trustworthy x-height: a crop too clipped to measure its own (and given no prior) gets
    # no soft cuts (the owner's example crop: x-height 9 px measured vs ~21-26 px real would cut it in four)
    probe = line_glyphs(img, **kw)
    xh = probe.band.xh
    boxes = letter_boxes(probe)
    clipped = sum(b.y0 == 0 or b.y1 == h for b in boxes) / max(1, len(boxes))
    prior = kw.get('xh_prior')
    has_prior = prior is not None and np.isfinite(prior) and prior > 0      # by value (CP-G3 F5: None counted as a prior)
    trusted = has_prior or (probe.band.n_support >= 8 and clipped < .35)
    cols = np.zeros(w, bool)
    for c in probe.components:
        if c.role in ('letter', 'fragment', 'punct', 'mark', 'large'):
            cols[c.x0:c.x1] = True
    soft: list[tuple[int, int]] = []
    on = np.nonzero(cols)[0]
    if on.size and trusted:
        run_start = None
        for x in range(int(on[0]), int(on[-1]) + 1):
            if not cols[x] and run_start is None:
                run_start = x
            elif cols[x] and run_start is not None:
                if x - run_start > GAP_CUT * xh:
                    soft.append((run_start, x))
                run_start = None
    def split(spans_in, cut):
        out = []
        for a, b in spans_in:
            if a < cut[0] and cut[1] < b:
                out += [[a, cut[0]], [cut[1], b]]
            else:
                out.append([a, b])
        return out
    for cut in soft:
        trial = split(merged, cut)
        left = next((sp for sp in trial if sp[1] == cut[0]), None)
        right = next((sp for sp in trial if sp[0] == cut[1]), None)
        if left is None or right is None:
            continue          # the gap borders a rule or the crop edge: nothing to decide
        try:
            gl = line_glyphs(img.crop((left[0], 0, left[1], h)), xh_prior=xh)
            gr = line_glyphs(img.crop((right[0], 0, right[1], h)), xh_prior=xh)
        except Exception:
            continue
        # extrapolate both baselines to the middle of the gap and compare
        ml = gl.band.bottom[-1] + (gl.band.bottom[-1] - gl.band.bottom[max(0, gl.width - int(3 * xh))]) / (3 * xh) * (cut[1] - cut[0]) / 2
        mr = gr.band.bottom[0] - (gr.band.bottom[min(gr.width - 1, int(3 * xh))] - gr.band.bottom[0]) / (3 * xh) * (cut[1] - cut[0]) / 2
        wide = min(left[1] - left[0], right[1] - right[0]) >= SOFT_MIN * xh
        if wide and abs(ml - mr) > ALIGN_TOL * xh and gl.band.n_support >= 6 and gr.band.n_support >= 6:
            merged = trial
    segs = []
    for a, b in merged:
        sub = img.crop((a, 0, b, h))
        try:
            g = line_glyphs(sub, **kw)
        except Exception:      # an empty strip
            g = None
        segs.append(Segment(a, b, g))
    # columns of one crop share one type size: a segment whose x-height disagrees by > 25 % with the best-supported
    # segment (e.g. a speaker name in capitals) is refitted with that x-height as its prior
    fitted = [s for s in segs if s.glyphs is not None]
    if len(fitted) > 1 and not has_prior:
        ref = max(fitted, key=lambda s: s.glyphs.band.n_support).glyphs.band.xh
        for s in fitted:
            if abs(s.glyphs.band.xh / ref - 1) > .25:
                s.glyphs = line_glyphs(img.crop((s.x0, 0, s.x1, h)), xh_prior=ref, **kw)
    return segs

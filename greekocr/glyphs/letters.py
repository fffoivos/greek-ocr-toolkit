"""Rough letters: groups of ink pieces in the middle region (between mean line and baseline), merged blobs split.

Owner rule (8 Oct): an intact Greek letter is one connected piece in the middle region (accents, breathings and iota
subscript lie outside it), and adjacent letters do not share ink columns there. Pieces are labelled AFTER restricting
the ink to the per-column middle region, so a join above or below the band cannot hide a break (CP-G1c2 F3).
  rule 1  pieces sharing ≥ SHARE of the narrower piece's columns are one (broken) letter. Rendered upright type:
          0.04 % of 16,540 adjacent letter pairs share any middle-region column (0.00 % by ≥ 2); blur and skew make
          neighbours graze by 1–2 px, hence a proportion rather than any overlap;
  rule 2  pieces split by a vertical gap (a round letter broken into two arcs): gap ≤ MAX_GAP x-heights, union no
          wider than MERGE_WIDTH typical letters, and not both complete letters.
A single piece wider than MERGED_WIDTH typical letters holds several letters run together: it is cut at its thinnest
columns when a thin bridge exists; otherwise it stays one box marked merged and unresolved (CP-G1c2 F5).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import ndimage as ndi

from greekocr.glyphs.components import EIGHT, LineGlyphs

__all__ = ['LetterBox', 'letter_boxes', 'middle_mask', 'SHARE', 'MAX_GAP', 'MERGE_WIDTH', 'MERGED_WIDTH']

SHARE, MAX_GAP, MERGE_WIDTH = .3, .3, 1.15
MIN_MID, COMPLETE = .2, .8         # a piece must span MIN_MID x-heights of the middle region; COMPLETE spans it
MERGED_WIDTH, BRIDGE = 1.5, .45    # merged: ≥ MERGED_WIDTH typical letters wide; cut where a column holds ≤ BRIDGE × median
UNRESOLVED_WIDTH = 1.8             # without a bridge, only a blob this wide is called merged (ω, μ, Μ are wide letters)
PATCH_THICKNESS = 1.2              # ink thicker than this (x-heights) is a patch, not a stroke (over-inked strokes stay < 1)
LINE_HEIGHT = 2.6                  # tallest single letter + its accent, in x-heights; taller ink is not a letter


@dataclass(frozen=True)
class LetterBox:
    x0: int
    y0: int
    x1: int
    y1: int
    components: tuple[int, ...]   # component indices of its ink
    pieces: int                   # middle-region pieces (1 = intact)
    merged: int                   # >1: this many letters run together in one blob (touching / over-inked)
    resolved: bool = True         # False: a merged blob that could not be cut into its letters

    @property
    def w(self) -> int:
        return self.x1 - self.x0

    @property
    def split(self) -> bool:
        return self.merged > 1 and self.resolved


def middle_mask(glyphs: LineGlyphs) -> np.ndarray:
    rows = np.arange(glyphs.height)[:, None]
    return (rows >= glyphs.band.top[None, :]) & (rows < glyphs.band.bottom[None, :])


def _cuts(cols: np.ndarray, k: int, min_gap: int) -> list[int]:
    smooth = ndi.uniform_filter1d(cols.astype(float), 3)
    cand = [i for i in range(min_gap, len(cols) - min_gap) if smooth[i] <= smooth[i - 1] and smooth[i] <= smooth[i + 1]]
    cand.sort(key=lambda i: smooth[i])
    chosen: list[int] = []
    for i in cand:
        if all(abs(i - j) >= min_gap for j in chosen):
            chosen.append(i)
        if len(chosen) == k - 1:
            break
    return sorted(chosen)


def letter_boxes(glyphs: LineGlyphs) -> list[LetterBox]:
    xh = glyphs.band.xh
    # a letter belongs to one line: ink taller than a whole line (tall-letter top to hanging-letter bottom, ≈ 2.1 x-heights)
    # or thicker than a letter is high (a patch) is not a letter (stain, shading, rule, several lines) and never becomes a piece
    stroke = glyphs.stroke if glyphs.stroke > 0 else 4.0
    thick = {c.index: float(2 * glyphs.dt[c.y0:c.y1, c.x0:c.x1][glyphs.labels[c.y0:c.y1, c.x0:c.x1] == c.index].max())
             for c in glyphs.components}
    eligible = [c.index for c in glyphs.components if c.role not in ('mark', 'neighbour', 'rule')
                and c.h <= LINE_HEIGHT * xh and thick[c.index] <= PATCH_THICKNESS * xh]
    mid_ink = np.isin(glyphs.labels, eligible) & middle_mask(glyphs)
    plab, n = ndi.label(mid_ink, structure=EIGHT)
    info = []
    for i, sl in enumerate(ndi.find_objects(plab), start=1):
        if sl is None:
            continue
        m = plab[sl] == i
        area = int(m.sum())
        rows = np.nonzero(m.any(axis=1))[0]
        span = float(rows[-1] - rows[0] + 1)
        if area < .02 * xh * xh or span < MIN_MID * xh:
            continue
        cols = set((np.nonzero(m.any(axis=0))[0] + sl[1].start).tolist())
        parent = int(np.bincount(glyphs.labels[sl][m]).argmax())
        info.append(dict(id=i, sl=sl, x0=sl[1].start, x1=sl[1].stop, cols=cols, span=span, parent=parent))
    info.sort(key=lambda d: d['x0'])
    singles = [d['x1'] - d['x0'] for d in info if d['span'] >= COMPLETE * xh and d['x1'] - d['x0'] <= 2 * xh]
    ref = float(np.median(singles)) if singles else max(glyphs.letter_w, 2.0)

    def full(d: dict) -> bool:
        return d['span'] >= COMPLETE * xh and d['x1'] - d['x0'] >= .6 * ref

    groups: list[dict] = []
    for d in info:
        if groups:
            G = groups[-1]
            share = max(len(p['cols'] & d['cols']) / max(1, min(len(p['cols']), len(d['cols']))) for p in G['p'])
            gap = d['x0'] - G['x1']
            width = max(G['x1'], d['x1']) - G['x0']
            near = gap <= MAX_GAP * xh and width <= MERGE_WIDTH * ref and not (full(d) and any(full(p) for p in G['p']))
            if share >= SHARE or near:
                G['p'].append(d); G['x1'] = max(G['x1'], d['x1'])
                continue
        groups.append(dict(x0=d['x0'], x1=d['x1'], p=[d]))
    gaps = [b['x0'] - a['x1'] for a, b in zip(groups, groups[1:]) if 0 <= b['x0'] - a['x1'] < .5 * xh]
    gap = float(np.median(gaps)) if gaps else 0.0

    top_limit = glyphs.band.top - .9 * xh          # above: tall letters (~0.5) and their accents
    bottom_limit = glyphs.band.bottom + .9 * xh    # below: hanging letters (~0.6) and iota subscript

    def extent(parents: tuple[int, ...], x0: int, x1: int) -> tuple[int, int]:
        """Rows of the letter's ink, clipped to its own line: a letter box never leaves its line."""
        lo = int(max(0, np.floor(top_limit[x0:x1].min()))); hi = int(min(glyphs.height, np.ceil(bottom_limit[x0:x1].max())))
        rows = np.nonzero(np.isin(glyphs.labels[lo:hi, x0:x1], parents).any(axis=1))[0]
        return (lo + int(rows[0]), lo + int(rows[-1]) + 1) if rows.size else (lo, hi)

    out: list[LetterBox] = []
    for G in groups:
        parents = tuple(sorted({d['parent'] for d in G['p']}))
        width = G['x1'] - G['x0']
        k = int(round((width + gap) / (ref + gap)))
        if len(G['p']) == 1 and width >= MERGED_WIDTH * ref and k >= 2:
            d = G['p'][0]
            m = plab[d['sl']] == d['id']
            cols = m.sum(axis=0)
            cuts = _cuts(cols, k, max(2, int(.45 * ref)))
            if cuts and min(cols[i] for i in cuts) <= BRIDGE * float(np.median(cols[cols > 0])):
                edges = [0, *cuts, len(cols)]
                for a, b in zip(edges, edges[1:]):
                    y0, y1 = extent(parents, d['x0'] + a, d['x0'] + b)
                    out.append(LetterBox(d['x0'] + a, y0, d['x0'] + b, y1, parents, 1, len(edges) - 1, True))
                continue
                continue
            if width >= UNRESOLVED_WIDTH * ref:
                y0, y1 = extent(parents, G['x0'], G['x1'])
                out.append(LetterBox(G['x0'], y0, G['x1'], y1, parents, 1, k, False))
                continue
        y0, y1 = extent(parents, G['x0'], G['x1'])
        out.append(LetterBox(G['x0'], y0, G['x1'], y1, parents, len(G['p']), 1))
    return out

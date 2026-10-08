"""Rough letters: groups of ink pieces in the middle region (between mean line and baseline), merged blobs split.

Owner rule (8 Oct): an intact Greek letter is one connected piece in the middle region (accents, breathings and iota
subscript lie outside it), and adjacent letters do not share ink columns there. So:
  rule 1  pieces sharing ≥ SHARE of the narrower piece's middle-region columns are one (broken) letter. Rendered
          upright type: 0.04 % of 16,540 adjacent letter pairs share any middle-region column (0.00 % by ≥ 2); blur
          and skew make neighbours graze by 1–2 px, hence a proportion rather than any overlap;
  rule 2  pieces split by a vertical gap (a round letter broken into two arcs): gap ≤ MAX_GAP x-heights, union no
          wider than MERGE_WIDTH typical letters, and not both complete letters.
A single blob wider than one letter pitch is cut back into letters at its thinnest columns (touching / over-inked).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import ndimage as ndi

from greekocr.glyphs.components import Component, LineGlyphs

__all__ = ['LetterBox', 'letter_boxes', 'SHARE', 'MAX_GAP', 'MERGE_WIDTH']

SHARE, MAX_GAP, MERGE_WIDTH = .3, .3, 1.15
MIN_MID, COMPLETE = .2, .8   # a piece must reach MIN_MID x-heights into the middle region; COMPLETE spans it
MERGED_WIDTH, BRIDGE = 1.5, .45   # a merged blob: ≥ MERGED_WIDTH typical letters wide with a thin bridge


@dataclass(frozen=True)
class LetterBox:
    x0: int
    y0: int
    x1: int
    y1: int
    components: tuple[int, ...]   # component indices of its pieces
    pieces: int                   # middle-region pieces (1 = intact)
    merged: int                   # >1: cut out of one blob that held this many letters (touching / over-inked)

    @property
    def w(self) -> int:
        return self.x1 - self.x0

    @property
    def split(self) -> bool:
        return self.merged > 1


def _mid(glyphs: LineGlyphs, c: Component) -> tuple[set[int], int, float]:
    """Middle-region columns with ink, ink pixel count there, and vertical span covered (px)."""
    sub = glyphs.labels[c.y0:c.y1, c.x0:c.x1] == c.index
    xs = np.arange(c.x0, c.x1)
    rows = np.arange(c.y0, c.y1)[:, None]
    inside = sub & (rows >= glyphs.band.top[xs][None, :]) & (rows < glyphs.band.bottom[xs][None, :])
    r = np.nonzero(inside.any(axis=1))[0]
    return set(xs[inside.any(axis=0)].tolist()), int(inside.sum()), float(r[-1] - r[0] + 1) if r.size else 0.0


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
    info = []
    for c in glyphs.components:
        if c.role in ('mark', 'neighbour', 'rule'):
            continue
        cols, n, span = _mid(glyphs, c)
        if n == 0 or span < MIN_MID * xh or c.area < .02 * xh * xh:
            continue
        info.append(dict(c=c, cols=cols, span=span))
    info.sort(key=lambda d: d['c'].x0)
    singles = [d['c'].w for d in info if d['span'] >= COMPLETE * xh and d['c'].w <= 2 * xh]
    ref = float(np.median(singles)) if singles else max(glyphs.letter_w, 2.0)

    def full(d: dict) -> bool:
        return d['span'] >= COMPLETE * xh and d['c'].w >= .6 * ref

    groups: list[dict] = []
    for d in info:
        if groups:
            G = groups[-1]
            share = max(len(p['cols'] & d['cols']) / max(1, min(len(p['cols']), len(d['cols']))) for p in G['p'])
            gap = d['c'].x0 - G['x1']
            width = max(G['x1'], d['c'].x1) - G['x0']
            near = gap <= MAX_GAP * xh and width <= MERGE_WIDTH * ref and not (full(d) and any(full(p) for p in G['p']))
            if share >= SHARE or near:
                G['p'].append(d); G['x1'] = max(G['x1'], d['c'].x1)
                continue
        groups.append(dict(x0=d['c'].x0, x1=d['c'].x1, p=[d]))
    # intra-word gap between neighbouring letters: k merged letters span k·width + (k−1)·gap
    gaps = [b['x0'] - a['x1'] for a, b in zip(groups, groups[1:]) if 0 <= b['x0'] - a['x1'] < .5 * xh]
    gap = float(np.median(gaps)) if gaps else 0.0
    out: list[LetterBox] = []
    for G in groups:
        comps = [p['c'] for p in G['p']]
        y0, y1 = min(c.y0 for c in comps), max(c.y1 for c in comps)
        ids = tuple(c.index for c in comps)
        width = G['x1'] - G['x0']
        k = int(round((width + gap) / (ref + gap)))
        c = comps[0]
        mask = glyphs.labels[c.y0:c.y1, c.x0:c.x1] == c.index if len(comps) == 1 else None
        cuts = _cuts(mask.sum(axis=0), k, max(2, int(.45 * ref))) if mask is not None and k >= 2 else []
        cols = mask.sum(axis=0) if mask is not None else None
        # a merged blob must also show a thin bridge: some cut column carries ≤ BRIDGE × the blob's median column ink
        bridged = bool(cuts) and min(cols[i] for i in cuts) <= BRIDGE * float(np.median(cols[cols > 0]))
        if mask is not None and c.role != 'large' and width >= MERGED_WIDTH * ref and k >= 2 and bridged:
            edges = [0, *cuts, c.w]
            parts = []
            for a, b in zip(edges, edges[1:]):
                rows = np.nonzero(mask[:, a:b].any(axis=1))[0]
                if rows.size:
                    parts.append((c.x0 + a, c.y0 + int(rows[0]), c.x0 + b, c.y0 + int(rows[-1]) + 1))
            for x0, py0, x1, py1 in parts:
                out.append(LetterBox(x0, py0, x1, py1, ids, 1, len(parts)))
        else:
            out.append(LetterBox(G['x0'], y0, G['x1'], y1, ids, len(comps), 1))
    return out

"""Score the glyph model against rendered truth. Every rate is over independently enumerated TRUTH objects, so things
the detector loses count as misses (CP-G1 F1):

- marks:      each truth mark (connected MARK pixels, ≥ 4 px) is found when ≥ 30 % of its pixels lie in components the
              model calls 'mark'; `marks_detected` = any of its pixels is ink at all (detection coverage).
- neighbour:  NEIGHBOUR truth pixels that are ink: share inside components called 'neighbour'.
- letters:    each reliable truth letter is one / split / merged / lost against the model's letter boxes.
- fused:      a missed truth mark whose pixels sit in a letter blob > 3× its size (accent touching its letter).
- merged:     a truth letter is merged when its main ink blob also carries another truth letter's pixels.
- broken:     a truth letter is broken when its own ink (its pixels, grown 1 px) forms ≥ 2 sizeable middle-region
              pieces; predicted broken when its letter box has ≥ 2 pieces.
Component classification (the conditional confusion) is kept as a separate diagnostic. IGNORE truth is excluded.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

import numpy as np
from scipy import ndimage as ndi

from greekocr.glyphs.components import EIGHT, LineGlyphs, line_glyphs
from greekocr.glyphs.letters import LetterBox, letter_boxes
from greekocr.glyphs.synthetic import IGNORE, LETTER, MARK, NEIGHBOUR, PUNCT, Rendered

__all__ = ['GlyphScore', 'score_rendered', 'summarise']

TRUTH_NAMES = {0: 'noise', LETTER: 'letter', MARK: 'mark', PUNCT: 'punct', NEIGHBOUR: 'neighbour', IGNORE: 'ignore'}


@dataclass
class GlyphScore:
    confusion: Counter = field(default_factory=Counter)   # (truth, predicted role) -> components (diagnostic)
    letters: Counter = field(default_factory=Counter)     # one / split / merged / lost per truth letter
    marks: Counter = field(default_factory=Counter)       # total / detected / found
    neighbour_px: Counter = field(default_factory=Counter)
    broken: Counter = field(default_factory=Counter)      # tp / fp / fn / tn per truth letter
    merged: Counter = field(default_factory=Counter)      # tp / fp / fn / tn per truth letter
    n_lines: int = 0

    def add(self, other: 'GlyphScore') -> None:
        for name in ('confusion', 'letters', 'marks', 'neighbour_px', 'broken', 'merged'):
            getattr(self, name).update(getattr(other, name))
        self.n_lines += other.n_lines


def _blob_truth(glyphs: LineGlyphs, truth: np.ndarray) -> dict[int, int]:
    grown = np.zeros_like(truth)
    for cls in (NEIGHBOUR, IGNORE, MARK, PUNCT, LETTER):  # letters last: they win overlaps
        grown[ndi.binary_dilation(truth == cls, iterations=2)] = cls
    out: dict[int, int] = {}
    for c in glyphs.components:
        votes = grown[c.y0:c.y1, c.x0:c.x1][glyphs.labels[c.y0:c.y1, c.x0:c.x1] == c.index]
        counts = np.bincount(votes, minlength=6)
        out[c.index] = int(np.argmax(counts[1:]) + 1) if counts[1:].any() else 0
    return out


def score_rendered(sample: Rendered, glyphs: LineGlyphs | None = None,
                   boxes: list[LetterBox] | None = None) -> GlyphScore:
    g = glyphs or line_glyphs(sample.image)
    boxes = boxes if boxes is not None else letter_boxes(g)
    s = GlyphScore(n_lines=1)
    xh = g.band.xh
    bt = _blob_truth(g, sample.truth)
    roles = {c.index: c.role for c in g.components}
    areas = {c.index: c.area for c in g.components}
    for c in g.components:
        if bt[c.index] != IGNORE:
            s.confusion[(TRUTH_NAMES[bt[c.index]], c.role)] += 1
    # marks, enumerated from truth
    lab, n = ndi.label(sample.truth == MARK, structure=EIGHT)
    near = ndi.binary_dilation(g.ink, iterations=1)
    mark_comp = np.isin(g.labels, [i for i, r in roles.items() if r == 'mark'])
    for i, sl in enumerate(ndi.find_objects(lab), start=1):
        m = lab[sl] == i
        if m.sum() < 4:
            continue
        s.marks['total'] += 1
        s.marks['detected'] += bool((near[sl] & m).any())
        found = (ndi.binary_dilation(m, iterations=1) & mark_comp[sl]).sum() >= .3 * m.sum()
        s.marks['found'] += found
        if not found:
            hit = g.labels[sl][m]
            hit = hit[hit > 0]
            if hit.size:
                c = int(np.bincount(hit).argmax())
                if roles.get(c) in ('letter', 'large', 'fragment') and areas.get(c, 0) > 3 * m.sum():
                    s.marks['fused'] += 1     # the accent touches its letter: one blob (heavy ink / blur)
    # neighbour ink, per pixel
    nb = (sample.truth == NEIGHBOUR) & g.ink
    s.neighbour_px['total'] += int(nb.sum())
    s.neighbour_px['called_neighbour'] += int((nb & np.isin(g.labels, [i for i, r in roles.items() if r == 'neighbour'])).sum())
    # letters and broken letters, per reliable truth letter
    box_of = np.zeros(g.labels.shape, np.int32)
    for k, b in enumerate(boxes, start=1):
        box_of[b.y0:b.y1, b.x0:b.x1][np.isin(g.labels[b.y0:b.y1, b.x0:b.x1], b.components)] = k
    rows = np.arange(g.height)[:, None]
    mid = (rows >= g.band.top[None, :]) & (rows < g.band.bottom[None, :])
    owners: Counter = Counter()
    per_glyph = []
    for k, gl in enumerate(sample.glyphs):
        if gl.kind != LETTER or not gl.reliable or gl.box is None:
            continue
        own = ndi.binary_dilation(sample.glyph_ids == k + 1, iterations=1) & g.ink
        if own.sum() < .05 * xh * xh:
            s.letters['lost'] += 1
            continue
        hits = Counter(box_of[own & (box_of > 0)].tolist())
        hits = {b for b, v in hits.items() if v >= .25 * own.sum()}
        owners.update(hits)
        per_glyph.append((k, own, hits))
    for k, own, hits in per_glyph:
        if not hits:
            s.letters['lost'] += 1
        elif any(owners[b] > 1 for b in hits):
            s.letters['merged'] += 1
        elif len(hits) > 1:
            s.letters['split'] += 1
        else:
            s.letters['one'] += 1
        pl, pn = ndi.label(own & mid, structure=EIGHT)
        sizes = np.bincount(pl.ravel())[1:] if pn else np.zeros(0, int)
        truth_broken = int((sizes >= .02 * xh * xh).sum()) >= 2
        pred_broken = any(boxes[b - 1].pieces >= 2 for b in hits)
        s.broken['tp' if truth_broken and pred_broken else 'fn' if truth_broken else 'fp' if pred_broken else 'tn'] += 1
        # merged: the letter's main ink component also carries ≥ .05 xh² of another truth letter's pixels
        comp_ids = np.bincount(g.labels[own], minlength=1)
        comp_ids[0] = 0
        main = int(comp_ids.argmax())
        others = np.bincount(sample.glyph_ids[(g.labels == main) & ~own].ravel())[1:] if main else np.zeros(0)
        truth_merged = bool((others >= .05 * xh * xh).any())
        pred_merged = any(boxes[b - 1].merged > 1 for b in hits)
        s.merged['tp' if truth_merged and pred_merged else 'fn' if truth_merged else 'fp' if pred_merged else 'tn'] += 1
    return s


def summarise(score: GlyphScore) -> dict[str, object]:
    def rate(a: float, b: float) -> float | None:
        return round(a / b, 4) if b else None
    conf, mk, br = score.confusion, score.marks, score.broken
    pred_mark = sum(v for (_, r), v in conf.items() if r == 'mark')
    n_letters = sum(score.letters.values())
    return dict(
        lines=score.n_lines,
        marks_total=mk['total'],
        marks_found=rate(mk['found'], mk['total']),
        marks_detected=rate(mk['detected'], mk['total']),
        marks_fused_into_letter=rate(mk['fused'], mk['total']),
        marks_found_of_separate=rate(mk['found'], mk['total'] - mk['fused']),
        mark_component_precision=rate(conf[('mark', 'mark')], pred_mark),
        neighbour_pixels_called_neighbour=rate(score.neighbour_px['called_neighbour'], score.neighbour_px['total']),
        letter_detection={k: round(v / n_letters, 4) for k, v in sorted(score.letters.items())} if n_letters else {},
        broken_recall=rate(br['tp'], br['tp'] + br['fn']),
        broken_precision=rate(br['tp'], br['tp'] + br['fp']),
        broken_counts=dict(br),
        merged_recall=rate(score.merged['tp'], score.merged['tp'] + score.merged['fn']),
        merged_precision=rate(score.merged['tp'], score.merged['tp'] + score.merged['fp']),
        confusion={f'{t}->{r}': v for (t, r), v in sorted(conf.items())},
    )

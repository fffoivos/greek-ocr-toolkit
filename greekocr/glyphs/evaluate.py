"""Score the glyph model against rendered truth. Truth is derived from the renderer alone — its letter-id map, true
baseline and x-height, and the noise-free degraded image thresholded midway between its paper and ink tones
(`oracle_ink`) — never from the detector's ink mask, band or components (CP-G1c2 F1). Every rate is over truth objects:

- marks:      each visible truth mark (MARK pixels inked in the oracle image, ≥ 4 px) is found when ≥ 30 % of it lies
              in components called 'mark'; fused = missed and inside a letter blob > 3× its size.
- neighbour:  visible NEIGHBOUR truth pixels: share inside components called 'neighbour' (detection recall), and the
              same among pixels the detector inked (classification only).
- letters:    each reliable truth letter is one / split / merged / lost against the letter boxes.
- states:     each reliable truth letter has a true state from the renderer: vanished when < .05 xh² of it is
              visible in the oracle image; otherwise from the PHYSICAL PRINT (clean ink after injected defects, before
              blur/gain/noise) inside the TRUE middle region — broken (≥ 2 pieces ≥ .02 xh²), merged (its printed blob
              carries another letter), else intact. (A midpoint threshold of the blurred image cuts hairlines and made
              17 % of undamaged letters 'broken', so it is used for visibility only.) — and a predicted state from the boxes overlapping it (under = broken|faint, merged,
              intact, or missed when no box covers it). Box votes use only pixels inside the box bounds (CP-G1c2 F6).
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

__all__ = ['STATE_TRUTHS', 'GlyphScore', 'score_rendered', 'summarise']

TRUTH_NAMES = {0: 'noise', LETTER: 'letter', MARK: 'mark', PUNCT: 'punct', NEIGHBOUR: 'neighbour', IGNORE: 'ignore'}


@dataclass
class GlyphScore:
    confusion: Counter = field(default_factory=Counter)   # (truth, predicted role) -> components (diagnostic)
    letters: Counter = field(default_factory=Counter)     # one / split / merged / lost per truth letter
    marks: Counter = field(default_factory=Counter)       # total / detected / found
    neighbour_px: Counter = field(default_factory=Counter)
    states: Counter = field(default_factory=Counter)      # (true state, predicted state) per truth letter
    n_lines: int = 0

    def add(self, other: 'GlyphScore') -> None:
        for name in ('confusion', 'letters', 'marks', 'neighbour_px', 'states'):
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


def _box_map(g: LineGlyphs, boxes: list[LetterBox]) -> np.ndarray:
    """Per pixel: 1 + index of the letter box owning it (its components' ink inside its own bounds)."""
    box_of = np.zeros(g.labels.shape, np.int32)
    for k, b in enumerate(boxes, start=1):
        box_of[b.y0:b.y1, b.x0:b.x1][np.isin(g.labels[b.y0:b.y1, b.x0:b.x1], b.components)] = k
    return box_of


STATE_TRUTHS = ('print', 'visible')


def score_rendered(sample: Rendered, glyphs: LineGlyphs | None = None,
                   boxes: list[LetterBox] | None = None, *, state_truth: str = 'print') -> GlyphScore:
    """state_truth: 'print' = the physical print (clean ink after defects); 'visible' = ink at least a quarter of the
    way from paper to ink tone in the noise-free scan (letters touching or broken as a reader sees them)."""
    if state_truth not in STATE_TRUTHS:
        raise ValueError(state_truth)
    from greekocr.glyphs.ink import ink_profile
    g = glyphs or line_glyphs(sample.image)
    boxes = boxes if boxes is not None else letter_boxes(g)
    states = [l.state for l in ink_profile(g, boxes).letters]
    s = GlyphScore(n_lines=1)
    xh = float(sample.xh)
    oracle = sample.oracle_ink if sample.oracle_ink is not None else sample.truth > 0
    bt = _blob_truth(g, sample.truth)
    roles = {c.index: c.role for c in g.components}
    areas = {c.index: c.area for c in g.components}
    for c in g.components:
        if bt[c.index] != IGNORE:
            s.confusion[(TRUTH_NAMES[bt[c.index]], c.role)] += 1
    # marks, enumerated from truth (visible in the oracle image)
    lab, n = ndi.label((sample.truth == MARK) & oracle, structure=EIGHT)
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
                    s.marks['fused'] += 1
    # neighbour ink: detection recall over all visible truth pixels, and classification among detected ones
    nb = (sample.truth == NEIGHBOUR) & oracle
    called = np.isin(g.labels, [i for i, r in roles.items() if r == 'neighbour'])
    s.neighbour_px['total'] += int(nb.sum())
    s.neighbour_px['called_neighbour'] += int((nb & called).sum())
    s.neighbour_px['detected'] += int((nb & g.ink).sum())
    s.neighbour_px['detected_called'] += int((nb & g.ink & called).sum())
    # letters: true states from the renderer, predicted states from the boxes
    box_of = _box_map(g, boxes)
    rows = np.arange(g.height)[:, None]
    true_mid = (rows >= sample.base_truth[None, :] - xh) & (rows < sample.base_truth[None, :])
    printed = sample.print_ink if state_truth == 'print' and sample.print_ink is not None else sample.visible(.25)
    olab, _ = ndi.label(printed, structure=EIGHT)
    gid_grown = {}
    owners: Counter = Counter()
    per_glyph = []
    for k, gl in enumerate(sample.glyphs):
        if gl.kind != LETTER or not gl.reliable or gl.box is None:
            continue
        own_ids = ndi.binary_dilation(sample.glyph_ids == k + 1, iterations=1)
        gid_grown[k] = own_ids
        own = own_ids & oracle
        if own.sum() < .05 * xh * xh:
            per_glyph.append((k, own_ids, set(), 'vanished'))
            continue
        phys = own_ids & printed
        pl, pn = ndi.label(phys & true_mid, structure=EIGHT)
        sizes = np.bincount(pl.ravel())[1:] if pn else np.zeros(0, int)
        truth_state = 'broken' if int((sizes >= .02 * xh * xh).sum()) >= 2 else 'intact'
        blob = int(np.bincount(olab[phys]).argmax()) if phys.any() else 0
        others = sample.glyph_ids[(olab == blob) & ~own_ids]
        others = np.bincount(others[others > 0])
        if truth_state == 'intact' and blob and (others >= .02 * xh * xh).any():
            truth_state = 'merged'
        votes = Counter(box_of[own & (box_of > 0)].tolist())
        hits = {b for b, v in votes.items() if v >= .25 * own.sum()}
        owners.update(hits)
        per_glyph.append((k, own_ids, hits, truth_state))
    for k, own_ids, hits, truth_state in per_glyph:
        if truth_state != 'vanished':
            if not hits:
                s.letters['lost'] += 1
            elif any(owners[b] > 1 for b in hits):
                s.letters['merged'] += 1
            elif len(hits) > 1:
                s.letters['split'] += 1
            else:
                s.letters['one'] += 1
        pred = [states[b - 1] for b in hits]
        p = 'missed' if not pred else 'under' if any(x in ('broken', 'faint') for x in pred) \
            else 'merged' if 'merged' in pred else 'intact'
        s.states[(truth_state, p)] += 1
    return s


def summarise(score: GlyphScore) -> dict[str, object]:
    def rate(a: float, b: float) -> float | None:
        return round(a / b, 4) if b else None
    conf, mk, st, nb = score.confusion, score.marks, score.states, score.neighbour_px
    pred_mark = sum(v for (_, r), v in conf.items() if r == 'mark')
    n_letters = sum(score.letters.values())
    def tot(truth=None, pred=None) -> int:
        return sum(v for (t, p), v in st.items() if (truth is None or t in truth) and (pred is None or p in pred))
    return dict(
        lines=score.n_lines,
        marks_total=mk['total'],
        marks_found=rate(mk['found'], mk['total']),
        marks_detected=rate(mk['detected'], mk['total']),
        marks_fused_into_letter=rate(mk['fused'], mk['total']),
        marks_found_of_separate=rate(mk['found'], mk['total'] - mk['fused']),
        mark_component_precision=rate(conf[('mark', 'mark')], pred_mark),
        neighbour_recall=rate(nb['called_neighbour'], nb['total']),
        neighbour_detected=rate(nb['detected'], nb['total']),
        neighbour_classified_of_detected=rate(nb['detected_called'], nb['detected']),
        letter_detection={k: round(v / n_letters, 4) for k, v in sorted(score.letters.items())} if n_letters else {},
        letters_true=tot(), letters_missed=tot(pred={'missed'}),
        broken_recall=rate(tot({'broken'}, {'under'}), tot({'broken'})),
        under_precision=rate(tot({'broken'}, {'under'}), tot(pred={'under'})),
        merged_recall=rate(tot({'merged'}, {'merged'}), tot({'merged'})),
        merged_precision=rate(tot({'merged'}, {'merged'}), tot(pred={'merged'})),
        vanished=tot({'vanished'}),
        state_confusion={f'{t}->{p}': v for (t, p), v in sorted(st.items())},
        confusion={f'{t}->{r}': v for (t, r), v in sorted(conf.items())},
    )

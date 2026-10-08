"""Neighbour-line placement (four-line model) vs the renderer's true neighbour baselines. Seed 71.
Honest matching (CP-G2 F2): a predicted neighbour matches a true one on the same side when the median |baseline error|
over the main line's columns is ≤ MATCH x-heights; one-to-one, greedy by error. A true neighbour is present when
≥ 30 px of its ink is visible (quarter-contrast). Reported: recall over present lines, precision over all predictions,
unmatched predictions (false lines), and placement error over matches. Usage: neighbour_eval.py DIR [N]"""
import random, sys
import numpy as np
from common import setup, render
from greekocr.glyphs.components import line_glyphs
from greekocr.glyphs.baseline import text_lines
from greekocr.glyphs.synthetic import NEIGHBOUR, LETTER
DIR = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 200
MATCH = .5
fonts, texts = setup(DIR)
rng = random.Random(71); tp = fn = fp = pred_n = present_n = matched_absent = 0; errs = []
for i in range(N):
    r = render(rng, fonts, texts, 7000 + i, neighbours_p=1.0)
    g = line_glyphs(r.image); L = [l for l in text_lines(g) if l.side != 'main']
    cols = np.nonzero((r.truth == LETTER).any(axis=0))[0]; span = slice(int(cols[0]), int(cols[-1]) + 1)
    vis = (r.truth == NEIGHBOUR) & r.visible(.25)
    rows = np.arange(r.image.height)[:, None]; mid = r.base_truth - r.xh / 2
    truths = []
    for side, tb in r.other_base_truth:
        own = vis & ((rows > mid[None, :]) if side > 0 else (rows < mid[None, :]))
        truths.append(('below' if side > 0 else 'above', tb, own.sum() >= 30))
    pairs = sorted((float(np.median(np.abs(p.base[span] - tb[span]))) / r.xh, pi, ti)
                   for pi, p in enumerate(L) for ti, (side, tb, _) in enumerate(truths) if p.side == side)
    used_p, used_t = set(), set()
    for e, pi, ti in pairs:
        if e <= MATCH and pi not in used_p and ti not in used_t:
            used_p.add(pi); used_t.add(ti)
            if truths[ti][2]:
                tp += 1; errs.append(e)
            else:
                matched_absent += 1          # placed a neighbour whose visible ink is under the presence bar
    pred_n += len(L); present_n += sum(t[2] for t in truths)
    fn += sum(1 for ti, t in enumerate(truths) if t[2] and ti not in used_t)
    fp += sum(1 for pi in range(len(L)) if pi not in used_p)
e = np.array(errs)
print('present true neighbours %d, predictions %d | matched %d (recall %.3f), missed %d, unmatched predictions (false lines) %d (precision %.3f), matched to a barely visible line %d'
      % (present_n, pred_n, tp, tp / max(1, present_n), fn, fp, (tp + matched_absent) / max(1, pred_n), matched_absent))
print('placement error over matches (x-heights): median %.3f p75 %.3f p90 %.3f | within 0.25: %.3f of matches, %.3f of present lines'
      % (np.median(e), np.percentile(e, 75), np.percentile(e, 90), (e <= .25).mean(), (e <= .25).sum() / max(1, present_n)))

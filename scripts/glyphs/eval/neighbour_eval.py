"""Neighbour-line placement (four-line model) vs the renderer's true neighbour baselines. Seed 71.
A neighbour counts as present when ≥ 30 px of its ink is visible in the crop. Usage: neighbour_eval.py DIR [N]"""
import random, sys
import numpy as np
from common import setup, render
from greekocr.glyphs.components import line_glyphs
from greekocr.glyphs.baseline import text_lines
from greekocr.glyphs.synthetic import NEIGHBOUR, LETTER
DIR = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 200
fonts, texts = setup(DIR)
rng = random.Random(71); found = missed = false = 0; errs = []
for i in range(N):
    r = render(rng, fonts, texts, 7000 + i, neighbours_p=1.0)
    g = line_glyphs(r.image); L = text_lines(g)
    cols = np.nonzero((r.truth == LETTER).any(axis=0))[0]; span = slice(int(cols[0]), int(cols[-1]) + 1)
    vis = (r.truth == NEIGHBOUR) & r.visible(.25)
    mid = (r.base_truth - r.xh / 2)
    for side, tb in r.other_base_truth:
        rows = np.arange(r.image.height)[:, None]
        own = vis & ((rows > mid[None, :]) if side > 0 else (rows < mid[None, :]))
        present = own.sum() >= 30
        pred = [l for l in L if l.side == ('below' if side > 0 else 'above')]
        if present and pred:
            found += 1
            best = min(pred, key=lambda l: abs(np.median(l.base[span] - tb[span])))
            errs.append(float(np.median(np.abs(best.base[span] - tb[span]))) / r.xh)
        elif present:
            missed += 1
    for l in L:
        if l.side != 'main' and not any(((side > 0) == (l.side == 'below')) for side, _ in r.other_base_truth):
            false += 1
e = np.array(errs)
print('present neighbours found %d / %d (missed %d); placement error (median |baseline error| per line, x-heights): median %.3f p75 %.3f p90 %.3f; share within 0.25 xh: %.3f; within 0.5 xh: %.3f'
      % (found, found + missed, missed, np.median(e), np.percentile(e, 75), np.percentile(e, 90), (e <= .25).mean(), (e <= .5).mean()))

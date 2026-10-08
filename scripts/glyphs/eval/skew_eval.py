"""Skew angle and per-column baseline error vs render truth: straight lines and bent lines. Usage: skew_eval.py DIR [N]"""
import random, sys
import numpy as np
from common import setup, render
from greekocr.glyphs.components import line_glyphs
from greekocr.glyphs.baseline import skew_line
from greekocr.glyphs.synthetic import LETTER
DIR = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 200
fonts, texts = setup(DIR)
rng = random.Random(31); ang = []; conf = []; colerr = {'straight': [], 'bent': []}
for i in range(N):
    bent = i % 2 == 1
    bend = (rng.choice(['left', 'right']), rng.choice([-1, 1]) * rng.uniform(.4, 1.5), rng.uniform(.15, .4)) if bent else None
    r = render(rng, fonts, texts, 500 + i, neighbours_p=.6, bend=bend)
    g = line_glyphs(r.image)
    cols = np.nonzero((r.truth == LETTER).any(axis=0))[0]; span = slice(int(cols[0]), int(cols[-1]) + 1)
    e = np.abs(g.band.bottom[span] - r.base_truth[span]) / g.band.xh
    colerr['bent' if bent else 'straight'].append((float(e.max()), float((e > .25).mean())))
    if not bent:
        sk = skew_line(g); ang.append(sk.angle_deg - r.skew_deg); conf.append(sk.confidence)
e = np.abs(ang)
print('straight lines: skew |error| deg median %.3f p90 %.3f p99 %.3f max %.3f; share > 0.25°: %.3f (n=%d)' % (np.median(e), np.percentile(e, 90), np.percentile(e, 99), e.max(), (e > .25).mean(), len(e)))
hi = np.array([c == 'high' for c in conf])
print('  high-confidence fits only (%d of %d): median %.3f p90 %.3f p99 %.3f max %.3f; share > 0.25°: %.3f' % (hi.sum(), len(e), np.median(e[hi]), np.percentile(e[hi], 90), np.percentile(e[hi], 99), e[hi].max(), (e[hi] > .25).mean()))
print('  low/medium-confidence fits: |error| values', np.round(np.sort(e[~hi]), 2).tolist())
for k, v in colerr.items():
    a = np.array(v)
    print(k, 'baseline per-line max error (x-heights): median %.3f p90 %.3f | lines with any column > 0.25 xh: %.3f | columns > 0.25 xh: %.4f' % (np.median(a[:, 0]), np.percentile(a[:, 0], 90), (a[:, 1] > 0).mean(), a[:, 1].mean()))

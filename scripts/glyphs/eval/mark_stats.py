"""Uncensored calibration evidence for NEIGHBOUR_GAP_ABOVE / _BELOW (CP-G1 F7): every small component outside the
body is a candidate regardless of its predicted role; gap = distance from the body (x-heights). Seed 5."""
import random, sys
import numpy as np
from common import setup, render
from greekocr.glyphs.components import line_glyphs
from greekocr.glyphs.evaluate import _blob_truth, TRUTH_NAMES
DIR = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 250
fonts, texts = setup(DIR)
rng = random.Random(5); rows = []
for i in range(N):
    r = render(rng, fonts, texts, i, neighbours_p=1.0)
    g = line_glyphs(r.image); bt = _blob_truth(g, r.truth); xh = g.band.xh
    for c in g.components:
        if c.rel_h >= .8 or c.area >= .35 * xh * xh:
            continue
        t, b = g.band.at(c.cx); cy = (c.y0 + c.y1) / 2
        if cy < t + .1 * xh:
            rows.append(('above', TRUTH_NAMES[bt[c.index]], (t - c.y1) / xh))
        elif cy > b - .1 * xh:
            rows.append(('below', TRUTH_NAMES[bt[c.index]], (c.y0 - b) / xh))
q = lambda v: np.round(np.percentile(v, [1, 5, 25, 50, 75, 95, 99]), 2).tolist()
for side in ('above', 'below'):
    for cls in ('mark', 'punct', 'neighbour', 'letter'):
        v = [x[2] for x in rows if x[0] == side and x[1] == cls]
        if v: print(side, cls, len(v), 'gap p1/5/25/50/75/95/99', q(v))
    own = np.array([x[2] for x in rows if x[0] == side and x[1] in ('mark', 'punct', 'letter')])
    nbr = np.array([x[2] for x in rows if x[0] == side and x[1] == 'neighbour'])
    print(side, 'threshold sweep: (thr, own-line ink called neighbour, neighbour ink kept as own)')
    for thr in (.2, .25, .3, .35, .4, .45, .5, .6):
        print('   %.2f  %.4f  %.4f' % (thr, (own > thr).mean(), (nbr <= thr).mean()))

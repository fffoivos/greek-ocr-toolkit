"""Double-line flag on rendered crops: half with a full second line, half single with neighbour tips. Seed 61."""
import random, sys
from common import setup, render
from greekocr.glyphs.components import line_glyphs
from greekocr.glyphs.baseline import skew_line
DIR = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 200
fonts, texts = setup(DIR)
rng = random.Random(61); c = {'tp': 0, 'fn': 0, 'fp': 0, 'tn': 0}; ratios = {True: [], False: []}
for i in range(N):
    two = i % 2 == 0
    r = render(rng, fonts, texts, 6000 + i, neighbours_p=0 if two else 1.0, second_p=1.0 if two else 0.0)
    s = skew_line(line_glyphs(r.image))
    ratios[two].append(s.second.ratio if s.second else 0.0)
    c[('tp' if s.double_line else 'fn') if two else ('fp' if s.double_line else 'tn')] += 1
import numpy as np
print(c, 'recall %.3f precision %.3f' % (c['tp'] / max(1, c['tp'] + c['fn']), c['tp'] / max(1, c['tp'] + c['fp'])))
for k, v in ratios.items():
    print('two lines' if k else 'one line ', 'support ratio p5/p50/p95', np.round(np.percentile(v, [5, 50, 95]), 3))

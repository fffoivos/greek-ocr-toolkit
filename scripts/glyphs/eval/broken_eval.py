"""Broken / faint / merged letters vs truth with injected defects located per pixel (CP-G1 F3). Seed 2.
Usage: broken_eval.py DIR [N]"""
import json, random, sys
import numpy as np
from common import setup, render
from greekocr.glyphs.components import line_glyphs
from greekocr.glyphs.letters import letter_boxes
from greekocr.glyphs.ink import ink_profile
from greekocr.glyphs.evaluate import GlyphScore, score_rendered, summarise
from greekocr.glyphs.synthetic import DEFECTS, LETTER
DIR = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 150
fonts, texts = setup(DIR)
names = {v: k for k, v in DEFECTS.items()}
rng = random.Random(2); total = GlyphScore(); by_kind = {}
for i in range(N):
    a = rng.uniform(0, .6)
    defects = [(a, a + rng.uniform(.15, .35), rng.choice(list(DEFECTS)), rng.uniform(.4, 1))] if rng.random() < .8 else []
    r = render(rng, fonts, texts, 2000 + i, neighbours_p=.5, ink_defects=defects)
    g = line_glyphs(r.image); boxes = letter_boxes(g); prof = ink_profile(g, boxes)
    total.add(score_rendered(r, g, boxes))
    # per letter box: the defect kind under its own truth-letter pixels (majority), and its predicted state
    for L, b in zip(prof.letters, boxes):
        own = np.isin(g.labels, b.components) & (r.truth == LETTER)
        k = r.defect_kind[own]
        kind = names.get(int(np.bincount(k).argmax()), 'none') if k.size and (k > 0).mean() > .5 else ('none' if k.size and (k > 0).mean() < .1 else 'mixed')
        by_kind.setdefault(kind, []).append(L.state)
S = summarise(total)
print(json.dumps({k: S[k] for k in ('broken_recall', 'broken_precision', 'broken_counts', 'letter_detection', 'marks_found')}))
print('predicted state per letter box, by the injected defect under it:')
for kind, states in sorted(by_kind.items()):
    v = np.array(states)
    print('  %-6s n=%5d  broken %.3f  faint %.3f  merged %.3f  intact %.3f' % (kind, len(v), *(np.mean(v == s) for s in ('broken', 'faint', 'merged', 'intact'))))

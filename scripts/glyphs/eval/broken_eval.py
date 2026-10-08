"""Letter ink states vs renderer-only truth (CP-G1c2 F1), with injected defects; per-defect breakdown uses only each
box's own pixels inside its bounds (CP-G1c2 F6). Seed 2. Usage: broken_eval.py DIR [N]"""
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
rng = random.Random(2); total = GlyphScore(); vis = GlyphScore(); by_kind = {}
for i in range(N):
    a = rng.uniform(0, .6)
    defects = [(a, a + rng.uniform(.15, .35), rng.choice(list(DEFECTS)), rng.uniform(.4, 1))] if rng.random() < .8 else []
    r = render(rng, fonts, texts, 2000 + i, neighbours_p=.5, ink_defects=defects)
    g = line_glyphs(r.image); boxes = letter_boxes(g); prof = ink_profile(g, boxes)
    total.add(score_rendered(r, g, boxes)); vis.add(score_rendered(r, g, boxes, state_truth='visible'))
    for L, b in zip(prof.letters, boxes):
        own = np.zeros(g.labels.shape, bool)
        own[b.y0:b.y1, b.x0:b.x1] = np.isin(g.labels[b.y0:b.y1, b.x0:b.x1], b.components)
        own &= r.truth == LETTER
        k = r.defect_kind[own]
        if not k.size:
            continue
        share = (k > 0).mean()
        kind = names[int(np.bincount(k[k > 0]).argmax())] if share > .5 else ('none' if share < .1 else 'mixed')
        by_kind.setdefault(kind, []).append(L.state)
S = summarise(total)
print(json.dumps({k: S[k] for k in ('letters_true', 'letters_missed', 'vanished', 'broken_recall', 'under_precision',
                                     'merged_recall', 'merged_precision', 'neighbour_recall', 'letter_detection')}))
print('state confusion (true->predicted):', S['state_confusion'])
V = summarise(vis)
print('letter states vs VISIBLE truth:', json.dumps({k: V[k] for k in ('broken_recall', 'under_precision', 'merged_recall', 'merged_precision', 'state_confusion')}))
print('predicted state per letter box, by the injected defect under its own pixels:')
for kind, states in sorted(by_kind.items()):
    v = np.array(states)
    print('  %-6s n=%5d  broken %.3f  faint %.3f  merged %.3f  intact %.3f' % (kind, len(v), *(np.mean(v == s) for s in ('broken', 'faint', 'merged', 'intact'))))

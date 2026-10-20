"""Letters / marks / neighbours / letter states vs renderer-only truth. Usage: eval_glyphs.py DIR N SEED P_NEIGHBOURS"""
import json, random, sys
from common import setup, render
from greekocr.glyphs.evaluate import GlyphScore, score_rendered, summarise
DIR, N, SEED, PNB = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
fonts, texts = setup(DIR)
rng, total, vis = random.Random(SEED), GlyphScore(), GlyphScore()
for i in range(N):
    r = render(rng, fonts, texts, SEED * 1000 + i, neighbours_p=PNB)
    total.add(score_rendered(r)); vis.add(score_rendered(r, state_truth='visible'))
S = summarise(total); C = S.pop('confusion')
print(json.dumps(S)); print('component confusion (diagnostic):', C)
V = summarise(vis)
print('letter states vs VISIBLE truth:', json.dumps({k: V[k] for k in ('broken_recall', 'under_precision', 'merged_recall', 'merged_precision', 'state_confusion')}))

"""Letters / marks / neighbours / rough letter boxes, truth-enumerated. Usage: eval_glyphs.py DIR N SEED P_NEIGHBOURS"""
import json, random, sys
from common import setup, render
from greekocr.glyphs.evaluate import GlyphScore, score_rendered, summarise
DIR, N, SEED, PNB = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
fonts, texts = setup(DIR)
rng, total = random.Random(SEED), GlyphScore()
for i in range(N):
    total.add(score_rendered(render(rng, fonts, texts, SEED * 1000 + i, neighbours_p=PNB)))
S = summarise(total); C = S.pop('confusion')
print(json.dumps(S)); print('component confusion (diagnostic):', C)

"""Capitals (owner 8 Oct: be careful with them; speaker names in capitals open many lines in the minutes).
Renders lines that open with a capitalised speaker-style word ('ΠΕΤΡΙΔΗΣ. ' + text) and all-capitals lines, and
measures: capitals wrongly called merged / broken, letter boxes on capitals, baseline error. Seed 81.
Usage: capitals_eval.py DIR [N]"""
import random, sys, unicodedata as ud
import numpy as np
from common import setup, pick_text
from greekocr.glyphs.components import line_glyphs
from greekocr.glyphs.evaluate import GlyphScore, score_rendered, summarise
from greekocr.glyphs.letters import letter_boxes
from greekocr.glyphs.ink import ink_profile
from greekocr.glyphs.synthetic import render_truth_line, LETTER
DIR = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 120
fonts, texts = setup(DIR)
plain = lambda t: ''.join(ch for ch in ud.normalize('NFD', t) if not ud.combining(ch))
from scipy import ndimage as ndi
rng = random.Random(81); caps_states = []; caps_rows = []; base_err = {'speaker': [], 'allcaps': []}; total = GlyphScore()
for i in range(N):
    font = rng.choice(fonts); t = pick_text(rng, texts, font)
    words = [w for w in plain(t).split() if w.isalpha() and len(w) >= 5]
    if not words:
        continue
    kind = 'allcaps' if i % 3 == 2 else 'speaker'
    if kind == 'speaker':
        line = rng.choice(words).upper() + '. ' + t[:55]
    else:
        line = ' '.join(plain(t).upper().split()[:7])
    r = render_truth_line(line, font, size=rng.randint(26, 46), rng=random.Random(8000 + i))
    g = line_glyphs(r.image); boxes = letter_boxes(g); prof = ink_profile(g, boxes)
    total.add(score_rendered(r, g, boxes))
    cols = np.nonzero((r.truth == LETTER).any(axis=0))[0]; span = slice(int(cols[0]), int(cols[-1]) + 1)
    base_err[kind].append(float(np.median(np.abs(g.band.bottom[span] - r.base_truth[span]))) / r.xh)
    for k, gl in enumerate(r.glyphs):
        if gl.kind != LETTER or not gl.char.isupper() or gl.box is None:
            continue
        own = r.glyph_ids == k + 1
        hits = [L for L, b in zip(prof.letters, boxes) if (np.isin(g.labels[b.y0:b.y1, b.x0:b.x1], b.components) & own[b.y0:b.y1, b.x0:b.x1]).sum() > .25 * own.sum()]
        st = hits[0].state if len(hits) == 1 else ('split' if len(hits) > 1 else 'missed')
        caps_states.append(st)
        vis = r.visible(.25); lab, _ = ndi.label(vis, structure=np.ones((3, 3)))
        mine = ndi.binary_dilation(own, iterations=1) & vis
        touching = False
        if mine.any():
            blob = int(np.bincount(lab[mine]).argmax())
            others = r.glyph_ids[(lab == blob) & ~ndi.binary_dilation(own, iterations=1)]
            touching = bool((np.bincount(others[others > 0]) >= .02 * r.xh * r.xh).any()) if (others > 0).any() else False
        caps_rows.append((kind, st, touching))
cs = np.array(caps_states)
for kind in ('speaker', 'allcaps'):
    rows = [r_ for r_ in caps_rows if r_[0] == kind]
    m = [r_ for r_ in rows if r_[1] == 'merged']
    print(kind, 'capitals', len(rows), 'called merged', len(m), '(of which visibly touching a neighbour: %d)' % sum(r_[2] for r_ in m),
          '| visibly touching overall', sum(r_[2] for r_ in rows))
print('capital letters scored:', len(cs), {s: round(float((cs == s).mean()), 3) for s in ('intact', 'merged', 'broken', 'faint', 'split', 'missed')})
for k, v in base_err.items():
    v = np.array(v); print(k, 'lines', len(v), 'median |baseline error| (x-heights): median %.3f p90 %.3f' % (np.median(v), np.percentile(v, 90)))
S = summarise(total); print('all letters on these lines:', {k: S[k] for k in ('letter_detection', 'merged_precision', 'under_precision')})

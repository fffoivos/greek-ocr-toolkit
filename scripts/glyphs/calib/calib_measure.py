"""Measure the glyph tools' readability quantities on every calibration strip → measurements.jsonl."""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from greekocr.glyphs.components import line_glyphs
from greekocr.glyphs.baseline import skew_line, text_lines
from greekocr.glyphs.letters import letter_boxes
from greekocr.glyphs.ink import ink_profile
from greekocr.glyphs.report import needs_prior
D = Path(sys.argv[1])
rows = [json.loads(l) for l in open(D / 'manifest.jsonl')]
with open(D / 'measurements.jsonl', 'w') as out:
    for r in rows:
        im = Image.open(D / r['crop_path'])
        rec = dict(line_id=r['line_id'])
        try:
            g = line_glyphs(im)
            if needs_prior(g):                      # as on real pages: a clipped crop borrows the document x-height
                g = line_glyphs(im, xh_prior=r['xh'])
            boxes = letter_boxes(g); sk = skew_line(g, boxes); ink = ink_profile(g, boxes)
            h, xh = g.height, g.band.xh
            lo, hi = int(sk.support_x[0]), int(sk.support_x[1]) + 1
            top = np.clip(-g.band.top[lo:hi] / xh, 0, 1)                 # body fraction above the crop top
            bot = np.clip((g.band.bottom[lo:hi] - h) / xh, 0, 1)         # body fraction below the crop bottom
            main = text_lines(g)[0]
            asc, mean_, base_, desc = main.ascender[lo:hi], main.mean[lo:hi], main.base[lo:hi], main.descender[lo:hi]
            acc = np.clip((0 - asc) / np.maximum(mean_ - asc, 1), 0, 1)    # accent / tall-letter zone above the crop top
            tail = np.clip((desc - h) / np.maximum(desc - base_, 1), 0, 1) # tail zone below the crop bottom
            n = max(1, len(ink.letters))
            rec.update(xh=xh, xh_source=g.band.xh_source, angle=sk.angle_deg, confidence=sk.confidence,
                       top_cut=float(top.mean()), bottom_cut=float(bot.mean()), accent_cut=float(acc.mean()), tail_cut=float(tail.mean()), visible=float(sk.visible[lo:hi].mean()),
                       n_letters=len(ink.letters), broken=sum(l.state == 'broken' for l in ink.letters) / n,
                       faint=sum(l.state == 'faint' for l in ink.letters) / n, merged=sum(l.state == 'merged' for l in ink.letters) / n,
                       contrast=float(np.median([l.contrast for l in ink.letters])) if ink.letters else None,
                       ink_contrast=float(g.paper - g.ink_level), lines=len(text_lines(g)))
        except Exception as e:
            rec['error'] = repr(e)
        out.write(json.dumps(rec) + '\n')
print('measured', len(rows))

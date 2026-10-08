"""Per input segment of a page: the crop tools' underline (before) and the page detector's lines inside the segment
(after), as two images of the same crop. Usage: compare_segments_page.py PAGE.png BOXES.json LINES.json OUT.json"""
import base64, io, json, sys, time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from greekocr.glyphs.columns import column_segments                         # noqa: E402
from greekocr.glyphs.components import line_glyphs                          # noqa: E402
from greekocr.glyphs.report import needs_prior                              # noqa: E402

page = Image.open(sys.argv[1]).convert('L'); rows = json.load(open(sys.argv[2]))
lines = json.load(open(sys.argv[3])); out = Path(sys.argv[4])
COL = [(214, 39, 40), (31, 119, 180), (44, 160, 44), (148, 103, 189), (217, 95, 2)]
crops = [page.crop(tuple(r['box'])) for r in rows]
own = [line_glyphs(c).band.xh for c in crops if c.height > 20]
prior = float(np.median(own)) if own else None


def jpg(im, w=1100, q=58):
    if im.width > w:
        im = im.resize((w, max(1, round(im.height * w / im.width))), Image.LANCZOS)
    b = io.BytesIO(); im.convert('RGB').save(b, 'JPEG', quality=q, optimize=True)
    return base64.b64encode(b.getvalue()).decode(), im.width, im.height


cards = []
for i, (r, crop) in enumerate(zip(rows, crops)):
    x0, y0, x1, y1 = r['box']
    pad = int(.6 * (y1 - y0))                       # a little context above and below the segment
    win = (x0, max(0, y0 - pad), x1, min(page.height, y1 + pad))
    # before: the crop tools on the segment (as on the review pages)
    before = page.crop(win).convert('RGB'); d = ImageDraw.Draw(before)
    d.rectangle((0, y0 - win[1], x1 - x0 - 1, y1 - win[1] - 1), outline=(150, 150, 150), width=1)
    kw = {'xh_prior': prior} if prior and needs_prior(line_glyphs(crop)) else {}
    nb = 0
    for s in column_segments(crop, **kw):
        if s.glyphs is None:
            continue
        b = s.glyphs.band.bottom
        d.line([(s.x0 + x, y0 - win[1] + float(b[x]) + 2) for x in range(0, len(b), 3)], fill=COL[nb % 5], width=3); nb += 1
    # after: every detected line that passes through the segment's rows and columns
    after = page.crop(win).convert('RGB'); d = ImageDraw.Draw(after)
    d.rectangle((0, y0 - win[1], x1 - x0 - 1, y1 - win[1] - 1), outline=(150, 150, 150), width=1)
    na = 0
    for L in lines:
        lx0, lx1 = L['x0'], L['x1']
        if lx1 <= x0 or lx0 >= x1:
            continue
        base = np.asarray(L['baseline'], float); xs = np.linspace(lx0, lx1 - 1, len(base))
        inside = (xs >= x0) & (xs < x1) & (base >= y0) & (base <= y1)
        if not inside.any():
            continue
        sel = (xs >= x0 - 1) & (xs < x1 + 1)
        d.line([(float(x - x0), float(y - win[1]) + 2) for x, y in zip(xs[sel], base[sel])], fill=COL[na % 5], width=3); na += 1
    b1, w1, h1 = jpg(before); b2, w2, h2 = jpg(after)
    cards.append(dict(id=r['line_id'], box=r['box'], text=r.get('text', ''), n_before=nb, n_after=na,
                      before=b1, after=b2, w=w1, h=h1))
json.dump(dict(page=Path(sys.argv[1]).stem, built=time.strftime('%Y-%m-%d %H:%M'), cards=cards), open(out, 'w'), ensure_ascii=False)
print(Path(sys.argv[1]).stem, len(cards), 'segments;', sum(c['n_after'] > 1 for c in cards), 'with >1 detected line;',
      sum(c['n_after'] == 0 for c in cards), 'with none')

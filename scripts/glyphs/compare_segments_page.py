"""Per input segment of a page, as two images of the same crop: before = the crop tools' main line and every neighbour
line per column segment; after = every page-detector line that touches the segment. Each line is drawn with its four
font lines (top, mean, base, bottom) in one colour, the baseline thicker. Usage: compare_segments_page.py PAGE.png BOXES.json LINES.json OUT.json"""
import base64, io, json, sys, time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from greekocr.glyphs.baseline import text_lines                            # noqa: E402
from greekocr.glyphs.columns import column_segments                         # noqa: E402
from greekocr.glyphs.components import line_glyphs                          # noqa: E402
from greekocr.glyphs.report import needs_prior                              # noqa: E402

page = Image.open(sys.argv[1]).convert('L'); rows = json.load(open(sys.argv[2]))
lines = json.load(open(sys.argv[3])); out = Path(sys.argv[4])
COL = [(214, 39, 40), (31, 119, 180), (44, 160, 44), (148, 103, 189), (217, 95, 2)]
crops = [page.crop(tuple(r['box'])) for r in rows]
own = [line_glyphs(c).band.xh for c in crops if c.height > 20]
prior = float(np.median(own)) if own else None


def four(d, xs, curves, dy, col):
    """The four font lines of one line: thin top / mean / bottom, thick baseline."""
    for k, ys in enumerate(curves):
        d.line([(float(x), float(y) + dy) for x, y in zip(xs, ys)], fill=col, width=4 if k == 2 else 1)


def jpg(im, w=1400, q=62):
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
    for seg in column_segments(crop, **kw):
        if seg.glyphs is None:
            continue
        for g in text_lines(seg.glyphs):
            xs = np.arange(g.x0, g.x1 + 1, 3)
            four(d, seg.x0 + xs, [g.ascender[xs], g.mean[xs], g.base[xs], g.descender[xs]], y0 - win[1], COL[nb % 5]); nb += 1
    # after: every detected line that passes through the segment's rows and columns
    after = page.crop(win).convert('RGB'); d = ImageDraw.Draw(after)
    d.rectangle((0, y0 - win[1], x1 - x0 - 1, y1 - win[1] - 1), outline=(150, 150, 150), width=1)
    na = 0
    for L in lines:
        if L['x1'] <= x0 or L['x0'] >= x1:
            continue
        base = np.asarray(L['baseline'], float); mean = np.asarray(L['meanline'], float)
        xs = np.linspace(L['x0'], L['x1'] - 1, len(base))
        inx = (xs >= x0) & (xs < x1)
        if not (inx & (base > y0) & (mean < y1)).any():          # its letter body must touch the segment
            continue
        four(d, xs[inx][::3] - x0, [np.asarray(L[k], float)[inx][::3] for k in ('font_top', 'meanline', 'baseline', 'font_bottom')],
             -win[1], COL[na % 5]); na += 1
    b1, w1, h1 = jpg(before); b2, w2, h2 = jpg(after)
    cards.append(dict(id=r['line_id'], box=r['box'], text=r.get('text', ''), n_before=nb, n_after=na,
                      before=b1, after=b2, w=w1, h=h1))
json.dump(dict(page=Path(sys.argv[1]).stem, built=time.strftime('%Y-%m-%d %H:%M'), cards=cards), open(out, 'w'), ensure_ascii=False)
print(Path(sys.argv[1]).stem, len(cards), 'segments;', sum(c['n_after'] > 1 for c in cards), 'with >1 detected line;',
      sum(c['n_after'] == 0 for c in cards), 'with none')

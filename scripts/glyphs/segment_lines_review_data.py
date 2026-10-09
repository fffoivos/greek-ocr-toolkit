"""Review data for a page segmenter + line detector, one card per segment, for pages_review.html (plain cards): the
segment (grey outline) and every line that came from it — its final region as a light band, its six guide lines —
then each line straightened and normalised as the
recogniser reads it. Usage: segment_lines_review_data.py PAGE.png SEGMENTS.json LINES.json OUT.json [--overview LINES.jpg]"""
import base64, io, json, sys, time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

page_path = Path(sys.argv[1]); segs, lines = json.load(open(sys.argv[2])), json.load(open(sys.argv[3])); out = Path(sys.argv[4])
OVERVIEW = Path(sys.argv[sys.argv.index('--overview') + 1]) if '--overview' in sys.argv else None
page = Image.open(page_path).convert('L'); GRAY = np.asarray(page, np.float64); H, W = GRAY.shape
COL = [(204, 44, 58), (26, 118, 180), (25, 143, 92), (159, 65, 178), (214, 120, 0)]
XH = 20


def b64(im, q=60):
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True); return base64.b64encode(b.getvalue()).decode()


def unroll(L):
    s = XH / L['xheight']; w = max(1, int(np.ceil((L['x1'] - L['x0']) * s)))
    grid = np.arange(L['x0'], L['x1'])
    xs = np.clip(L['x0'] + (np.arange(w) + .5) / s - .5, L['x0'], L['x1'] - 1)
    local_xh = np.interp(xs, grid, np.asarray(L['baseline']) - np.asarray(L['meanline']))
    yy = np.interp(xs, grid, L['baseline'])[None, :] + ((np.arange(4 * XH) - 2.5 * XH) / XH)[:, None] * local_xh
    strip = ndi.map_coordinates(GRAY, [yy, np.broadcast_to(xs, yy.shape)], order=1, mode='constant', cval=255)
    strip[(yy < np.interp(xs, grid, L['top'])) | (yy >= np.interp(xs, grid, L['bottom']))] = 255
    return dict(png=b64(Image.fromarray(np.clip(strip, 0, 255).astype(np.uint8)), 55), w=w, h=4 * XH)


cards = []
for j, sg in enumerate(segs):
    own = [(i, L) for i, L in enumerate(lines) if j in L.get('segment_indices', [])]
    x0, y0, x1, y1 = sg['box']
    for _, L in own:                                   # the crop holds the segment and its lines' letters (font lines ± ½ x-height)
        x0, x1 = min(x0, L['x0']), max(x1, L['x1'])
        y0 = min(y0, int(np.min(L.get('accent_top', L['font_top'])) - .5 * L['xheight']))
        y1 = max(y1, int(np.ceil(np.max(L['font_bottom']) + .5 * L['xheight'])))
    x0, y0, x1, y1 = max(0, x0 - 6), max(0, y0 - 6), min(W, x1 + 6), min(H, y1 + 6)
    im = page.crop((x0, y0, x1, y1)).convert('RGB')
    band = Image.new('RGBA', im.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
    for n, (_, L) in enumerate(own):
        xs = np.arange(L['x0'], L['x1']) - x0
        poly = list(zip(xs[::3].tolist(), (np.asarray(L['top'])[::3] - y0).tolist())) + \
               list(zip(xs[::3][::-1].tolist(), (np.asarray(L['bottom'])[::3][::-1] - y0).tolist()))
        if len(poly) > 2:
            bd.polygon(poly, fill=COL[n % 5] + (34,))
    im = Image.alpha_composite(im.convert('RGBA'), band).convert('RGB'); d = ImageDraw.Draw(im)
    d.rectangle((sg['box'][0] - x0, sg['box'][1] - y0, sg['box'][2] - x0 - 1, sg['box'][3] - y0 - 1), outline=(120, 120, 120), width=1)
    for n, (i, L) in enumerate(own):
        xs = (np.arange(L['x0'], L['x1']) - x0)[::3].tolist()
        guides = dict(baseline=(220, 30, 30), meanline=(0, 110, 235), font_top=(0, 150, 90),
                      font_bottom=(150, 40, 190), accent_bottom=(230, 120, 0), accent_top=(20, 170, 180))
        for key, color in guides.items():
            if key not in L:  # Existing round-2 files remain reviewable.
                continue
            points = list(zip(xs, (np.asarray(L[key])[::3] - y0).tolist()))
            if key.startswith('accent'):
                for start in range(0, len(points) - 1, 4):
                    d.line(points[start:start + 2], fill=color, width=2)
            elif len(points) > 1:
                d.line(points, fill=color, width=3 if key == 'baseline' else 1)
        d.text((L['x0'] - x0, L['baseline'][0] - L['xheight'] - y0),
               str(i) + (' [discounted]' if L.get('discounted') else ''), fill='black')
    if im.width > 1600:
        im = im.resize((1600, max(1, round(im.height * 1600 / im.width))), Image.LANCZOS)
    cards.append(dict(id=sg['line_id'], section='pixel', plain=b64(im), width=im.width, height=im.height,
                      label=f"segment x {sg['box'][0]}–{sg['box'][2]}, y {sg['box'][1]}–{sg['box'][3]}",
                      n_lines=len(own), n_active=sum(not L.get('discounted') for _, L in own),
                      n_discounted=sum(bool(L.get('discounted')) for _, L in own),
                      unrolled=[dict(i=i, discounted=L.get('discounted'), **unroll(L)) for i, L in own]))
D = dict(built=time.strftime('%Y-%m-%d %H:%M'), mode='page', reviews=True, page=page_path.stem, pool=len(cards), lines=cards,
         lede=("Every segment the pixel segmenter found, in reading order. Each card: the segment (grey outline) and every line "
               "that came from it — its region as a light band; baseline red, mean blue, capital green, descender purple, "
               "and accent guides dashed orange/cyan. Each candidate is then straightened from the original pixels. "
               "Candidates labelled D are discounted and excluded from OCR; their reason appears on the label."))
if OVERVIEW:
    ov = Image.open(OVERVIEW); w = min(1400, ov.width); ov = ov.resize((w, round(ov.height * w / ov.width)), Image.LANCZOS)
    D.update(overview=b64(ov.convert('RGB'), 62), overview_w=ov.width, overview_h=ov.height,
             overview_caption='the whole page with every detected line (one band per line). The segments follow below.')
json.dump(D, open(out, 'w'), ensure_ascii=False)
print(page_path.stem, len(cards), 'segments;', sum(c['n_lines'] == 0 for c in cards), 'without a line;',
      sum(c['n_lines'] > 1 for c in cards), 'with several lines')

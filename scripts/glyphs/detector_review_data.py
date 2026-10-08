"""Review data for a page detector's lines, in the format of build_page_review_data.py, so that pages_review.html
draws them exactly like the crop tools' cards: for every input segment, the detector's lines that touch it (each with
its four font lines; the best-covering line per detector column is 'main', the others are neighbours or 'piece' when
level with the main line), with the reviewed crop-tools record kept as `prev` (drawn as "before" above it).
Usage: detector_review_data.py REVIEW.json BOXES.json LINES.json OUT.json [--overview LINES.jpg]"""
import base64, io, json, math, sys, time
from pathlib import Path

import numpy as np
from PIL import Image

review, boxes, lines = (json.load(open(p)) for p in sys.argv[1:4])
out = Path(sys.argv[4])
OVERVIEW = Path(sys.argv[sys.argv.index('--overview') + 1]) if '--overview' in sys.argv else None
box_of = {b['line_id']: b['box'] for b in boxes}
KEYS = (('font_top', 'ascender'), ('meanline', 'mean'), ('baseline', 'base'), ('font_bottom', 'descender'))


def sample(v, step):
    idx = list(range(0, len(v), step)) + [len(v) - 1]
    return [round(float(v[i]), 2) for i in idx]


def after_record(r):
    bx0, by0, bx1, by1 = box_of[r['id']]
    W, H, step = r['width'], r['height'], r['step']
    xs = np.arange(W) + bx0
    touching = []
    for L in lines:
        n = len(L['baseline']); lx = np.linspace(L['x0'], L['x1'] - 1, n)
        inx = (lx >= bx0) & (lx < bx1)
        base, mean = np.asarray(L['baseline'], float), np.asarray(L['meanline'], float)
        body = np.clip(np.minimum(base, by1) - np.maximum(mean, by0), 0, None)[inx]
        if not inx.any() or not (body > 0).any():
            continue
        loc = {new: np.interp(xs, lx, np.asarray(L[old], float)) - by0 for old, new in KEYS}   # full crop width, clamped
        x0, x1 = int(max(L['x0'], bx0) - bx0), int(min(L['x1'] - 1, bx1 - 1) - bx0)
        touching.append(dict(L=L, loc=loc, x0=x0, x1=x1, cover=float(body.sum()), xh=float(L['xheight'])))
    segs = []
    for col in sorted({t['L']['column'] for t in touching}, key=lambda c: min(t['x0'] for t in touching if t['L']['column'] == c)):
        group = [t for t in touching if t['L']['column'] == col]
        off = min(t['x0'] for t in group); Ws = max(t['x1'] for t in group) - off + 1
        main = max(group, key=lambda t: t['cover'])
        xh = main['xh']; mb = main['loc']['base']
        vis = np.clip(np.minimum(mb, H) - np.maximum(mb - xh, 0), 0, xh) / xh
        recs = []
        for t in sorted(group, key=lambda t: float(np.median(t['loc']['base'][t['x0']:t['x1'] + 1]))):
            sl = slice(off, off + Ws)
            shift = float(np.median((t['loc']['base'] - mb)[t['x0']:t['x1'] + 1])) / xh
            side = 'main' if t is main else ('piece' if abs(shift) < .8 else 'above' if shift < 0 else 'below')
            v = float(vis[t['x0']:t['x1'] + 1].mean()) if t is main else float(
                (np.clip(np.minimum(t['loc']['base'], H) - np.maximum(t['loc']['base'] - xh, 0), 0, xh) / xh)[t['x0']:t['x1'] + 1].mean())
            recs.append(dict(side=side, shift_xh=round(shift, 2), x0=t['x0'] - off, x1=t['x1'] - off, votes=t['L'].get('support', 0),
                             visible=round(v, 3), kind='main' if side == 'main' else ('full' if v >= .5 else 'edges'),
                             **{k: sample(t['loc'][k][sl], step) for k in ('ascender', 'mean', 'base', 'descender')}))
        b = mb[main['x0']:main['x1'] + 1]
        ang = -math.degrees(math.atan2(float(b[-1] - b[0]), max(1, len(b) - 1)))
        straight = np.linspace(b[0], b[-1], len(b))
        letters = [dict(l, x0=l['x0'] - off, x1=l['x1'] - off) for l in r.get('letters', []) if off <= (l['x0'] + l['x1']) / 2 < off + Ws]
        segs.append(dict(x_offset=off, width=Ws, baseline=sample(mb[off:off + Ws], step), meanline=sample(main['loc']['mean'][off:off + Ws], step),
                         visible=sample(vis[off:off + Ws], step), support_x=[main['x0'] - off, main['x1'] - off], lines=recs,
                         letters=letters, marks=[], cut_spans=[], cut_letters=[], crossings=[], n_support=main['L'].get('support', 0),
                         xh=round(xh, 1), angle_deg=round(ang, 2), trail_px=round(float(b[0] - b[-1]), 1),
                         degree=2 if float(np.abs(b - straight).max()) > 1.5 else 1))
    kinds = [l['kind'] for s in segs for l in s['lines']]
    m = max(segs, key=lambda s: s['n_support'] * 0 + s['width']) if segs else None
    rec = dict(r, segments=segs or [dict(x_offset=0, width=W, baseline=[], meanline=[], visible=[], support_x=[0, 0], lines=[], letters=[],
                                         marks=[], cut_spans=[], cut_letters=[], crossings=[])],
               n_columns=max(1, len(segs)), n_lines=len(kinds), n_full_lines=kinds.count('main') + kinds.count('full'),
               n_edge_lines=kinds.count('edges'), cut_spans=[], cut_letters=[], prior=None, xh_source='page_detector', confidence='page',
               n_support=m['n_support'] if m else 0, xh=m['xh'] if m else r['xh'], angle_deg=m['angle_deg'] if m else 0,
               trail_px=m['trail_px'] if m else 0, degree=m['degree'] if m else 1, prev={k: v for k, v in r.items() if k != 'prev'})
    rec['n_pieces'] = sum(l['side'] == 'piece' for s in segs for l in s['lines'])
    return rec


D = review
D['lines'] = [after_record(r) for r in review['lines']]
D['built'] = time.strftime('%Y-%m-%d %H:%M')
D['lede'] = ("Each segment twice: before = the crop tools you reviewed; after = Astra's page detector (lines found from the pixels "
             "alone, the segment only selects which lines to show). Same drawing: underline, mean line, dotted top and bottom font "
             "lines; neighbour lines in the second colour, labelled; 'piece' = a second line level with the main one (one printed line "
             "broken in two).")
if OVERVIEW:
    ov = Image.open(OVERVIEW); w = min(1400, ov.width); ov = ov.resize((w, round(ov.height * w / ov.width)), Image.LANCZOS)
    b = io.BytesIO(); ov.convert('RGB').save(b, 'JPEG', quality=62, optimize=True)
    D.update(overview=base64.b64encode(b.getvalue()).decode(), overview_w=ov.width, overview_h=ov.height,
             overview_caption='the whole page with every line the page detector found (one colour band per line). The segments follow below.')
json.dump(D, open(out, 'w'), ensure_ascii=False, allow_nan=False)
print(out.stem, len(D['lines']), 'segments;', sum(r['n_pieces'] > 0 for r in D['lines']), 'with a broken line piece')

"""Tessellation experiment: the first 3 body lines of each column of one page (owner 8 Oct 19:40).
Procedure: (1) boxes in; (2) fit each box's line and its four font lines; (3) forget the boxes: one shared curve s(x)
per column + a shift c_i per line, fitted jointly on the letters; font heights measured on the three lines' ink;
(4) boundaries = middle of facing font lines (outer ones: a virtual neighbour one pitch away); extent = the line's ink.
Usage: tess.py PAGE.png BOXES.json OUT_PREFIX"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from greekocr.glyphs.components import EIGHT, binarise                      # noqa: E402
from greekocr.glyphs.recut import fit_box                                   # noqa: E402

page = Image.open(sys.argv[1]).convert('L'); gray = np.asarray(page, np.float64)
rows = json.load(open(sys.argv[2])); out = sys.argv[3]
H, W = gray.shape
boxes = [tuple(r['box']) for r in rows]

# column split: the vertical rule = the column with the most ink over the page's middle rows, near the centre
ink = binarise(gray)
lo, hi = int(.35 * W), int(.65 * W)
band = ink[int(.05 * H):int(.95 * H), lo:hi]
runs = np.zeros(hi - lo, int)                       # the rule = the longest unbroken vertical run of ink
for j in range(hi - lo):
    col = band[:, j].astype(np.int8)
    if col.any():
        edges = np.diff(np.r_[0, col, 0]); st, en = np.nonzero(edges == 1)[0], np.nonzero(edges == -1)[0]
        runs[j] = int((en - st).max())
rule_x = lo + int(np.argmax(runs))
rw = np.nonzero(runs > .5 * runs.max())[0]          # its width
rule_l, rule_r = lo + int(rw.min()), lo + int(rw.max())
cols = {'left': (0, rule_l), 'right': (rule_l, W)}     # extents come from each line's letters; the rule is no letter
pick = {
    'left': sorted((i for i, b in enumerate(boxes) if b[0] < 300), key=lambda i: boxes[i][1])[:3],     # body lines start at the left margin
    'right': sorted((i for i, b in enumerate(boxes) if rule_x - 120 < b[0] < rule_x + 200), key=lambda i: boxes[i][1])[:3]}


def lowess(x, y, grid, bw):
    """Locally weighted linear fit (tricube), evaluated on grid."""
    out = np.empty(len(grid))
    for k, g in enumerate(grid):
        w = np.clip(1 - (np.abs(x - g) / bw) ** 3, 0, None) ** 3
        if w.sum() < 1e-6:
            j = np.argsort(np.abs(x - g))[:5]; w = np.zeros_like(x); w[j] = 1
        A = np.vstack([np.ones_like(x), x - g]).T * np.sqrt(w)[:, None]
        sol, *_ = np.linalg.lstsq(A, y * np.sqrt(w), rcond=None)
        out[k] = sol[0]
    return out


print("rule", rule_l, rule_r, "pick", pick)
report = {}
for name, idx in pick.items():
    c0, c1 = cols[name]
    # (2) fit each box's line
    def in_column(fs):              # a box may span both columns: take its line segment inside this column
        return max(fs, key=lambda f: min(f.x1, c1) - max(f.x0, c0))
    fits = [in_column(fit_box(gray, boxes[i], None, box_index=i, splits=False)) for i in idx]
    xh = float(np.median([f.xh for f in fits]))
    # (3) forget the boxes: shared curve + shifts, on the letters of the region
    y0 = int(min(f.base.min() for f in fits) - 3.5 * xh); y1 = int(max(f.base.max() for f in fits) + 2.5 * xh)
    reg = binarise(gray[y0:y1, c0:c1]); lab, n = ndi.label(reg, structure=EIGHT)
    comps = []
    for k, sl in enumerate(ndi.find_objects(lab), start=1):
        if sl is None: continue
        m = lab[sl] == k
        if m.sum() < 6: continue
        rr, cc = np.nonzero(m)
        comps.append(dict(x=c0 + sl[1].start + cc.mean(), x0=c0 + sl[1].start, x1=c0 + sl[1].stop,
                          top=y0 + sl[0].start, bot=y0 + sl[0].stop - 1, cy=y0 + sl[0].start + rr.mean(), n=int(m.sum())))
    grid = np.arange(c0, c1, dtype=np.float64)
    mid = fits[1]
    s = np.interp(grid, np.arange(mid.x0, mid.x1), mid.base)            # start: the middle line's curve
    c = np.array([float(np.median(np.interp(np.arange(f.x0, f.x1), grid, s) * 0 + f.base - np.interp(np.arange(f.x0, f.x1), grid, s))) for f in fits])
    for it in range(6):
        sx = lambda x: np.interp(x, grid, s)
        px, py, li = [], [], []
        for q in comps:
            h = q['bot'] - q['top'] + 1
            if h < .5 * xh or h > 2.4 * xh: continue
            d = np.array([q['bot'] - (sx(q['x']) + ci) for ci in c])
            i = int(np.argmin(np.abs(d)))
            if abs(d[i]) <= .3 * xh:                                     # sits on line i's baseline
                px.append(q['x']); py.append(q['bot'] - c[i]); li.append(i)
        px, py, li = np.array(px), np.array(py), np.array(li)
        inside = (grid >= px.min()) & (grid <= px.max())
        s_in = lowess(px, py, grid[inside], 8 * xh)
        slope = np.polyfit(px, py, 1)[0]                                 # the column's overall slant
        s = np.empty_like(grid)
        s[inside] = s_in
        gi = np.nonzero(inside)[0]
        s[:gi[0]] = s_in[0] + slope * (grid[:gi[0]] - grid[gi[0]])
        s[gi[-1] + 1:] = s_in[-1] + slope * (grid[gi[-1] + 1:] - grid[gi[-1]])
        c = np.array([float(np.median(py[li == i] + c[i] - np.interp(px[li == i], grid, s))) if (li == i).any() else c[i] for i in range(3)])
    sx = lambda x: np.interp(x, grid, s)
    # assign every component to the line whose letter-body centre is nearest its centroid
    rise = xh
    P0 = float(np.mean(np.diff(c)))
    centres = np.concatenate([[c[0] - P0], c, [c[2] + P0]])
    for q in comps:
        k = int(np.argmin([abs(q['cy'] - (sx(q['x']) + ci - rise / 2)) for ci in centres]))
        q['line'] = k - 1 if 1 <= k <= 3 else -1                        # -1: a line outside the three
    # four font lines, measured on the three lines' ink (page font): top = how far characters reach above the
    # baseline, bottom = how far below
    own = [q for q in comps if q['line'] >= 0 and q['n'] >= 10]
    tops = [sx(q['x']) + c[q['line']] - q['top'] for q in own]
    bots = [q['bot'] - (sx(q['x']) + c[q['line']]) for q in own]
    up, down = float(np.percentile(tops, 98)), float(np.percentile(bots, 98))
    P = float(np.mean(np.diff(c)))
    cc_ = np.concatenate([[c[0] - P], c, [c[2] + P]])                   # virtual neighbours outside the three
    bounds = [s + ((cc_[k] + down) + (cc_[k + 1] - up)) / 2 for k in range(4)]   # boundary k: between line k-1 and k
    # extent: the line's own ink along the curve (inside the column)
    ext = []
    letters = lambda i: [q for q in comps if q['line'] == i and q['n'] >= 10 and q['bot'] - q['top'] <= 2.6 * xh
                         and q['x1'] - q['x0'] <= 4 * xh and q['x0'] > c0 + 2 and q['x1'] < c1 - 2]
    for i in range(3):
        xs = [q['x0'] for q in letters(i)] + [q['x1'] for q in letters(i)]
        ext.append((int(max(c0, min(xs) - .3 * xh)), int(min(c1, max(xs) + .3 * xh))))
    # metrics: centring (ink margins to the line's own boundaries) and overflow
    met = []
    for i in range(3):
        mine = [q for q in comps if q['line'] == i and q['n'] >= 10]
        tm = np.array([q['top'] - np.interp(q['x'], grid, bounds[i]) for q in mine])
        bm = np.array([np.interp(q['x'], grid, bounds[i + 1]) - q['bot'] for q in mine])
        met.append(dict(top_margin_px=round(float(np.percentile(tm, 2)), 1), bottom_margin_px=round(float(np.percentile(bm, 2)), 1),
                        crossing_top=int((tm < 0).sum()), crossing_bottom=int((bm < 0).sum()), n=len(mine)))
    report[name] = dict(boxes=[rows[i]['line_id'] for i in idx], xh=round(xh, 1), pitch_px=round(P, 1), up_px=round(up, 1),
                        down_px=round(down, 1), shifts=[round(float(v), 1) for v in c], curve_range_px=round(float(np.ptp(s)), 1), lines=met)
    # draw
    X0, X1 = c0, c1; Y0 = int(min(bounds[0]) - 1.2 * xh); Y1 = int(max(bounds[3]) + 1.2 * xh)
    im = page.crop((X0, Y0, X1, Y1)).convert('RGB'); ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    COL = [(214, 39, 40), (31, 119, 180), (44, 160, 44)]
    for i in range(3):
        a, b = ext[i]
        xs = np.arange(a, b)
        topc = np.interp(xs, grid, bounds[i]) - Y0; botc = np.interp(xs, grid, bounds[i + 1]) - Y0
        poly = [(int(x - X0), float(t)) for x, t in zip(xs[::3], topc[::3])] + [(int(x - X0), float(v)) for x, v in zip(xs[::-3], botc[::-3])]
        d.polygon(poly, fill=COL[i] + (45,))
        base = np.interp(xs, grid, s) + c[i] - Y0
        for off, wdt, alpha in ((0, 2, 230), (-rise, 1, 170), (-up, 1, 120), (down, 1, 120)):
            pts = [(int(x - X0), float(v + off)) for x, v in zip(xs[::3], base[::3])]
            if off == 0:
                d.line(pts, fill=COL[i] + (alpha,), width=wdt)
            else:
                for k in range(0, len(pts) - 4, 8):
                    d.line(pts[k:k + 4], fill=COL[i] + (alpha,), width=wdt)
    for k in range(4):                                                   # the boundaries
        lo = min(ext[max(0, k - 1)][0], ext[min(2, k)][0]); hi = max(ext[max(0, k - 1)][1], ext[min(2, k)][1])
        xs = np.arange(lo, hi)
        d.line([(int(x - X0), float(np.interp(x, grid, bounds[k]) - Y0)) for x in xs[::3]], fill=(0, 0, 0, 255), width=2)
    im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB')
    im.save(f'{out}_{name}.png')
json.dump(report, open(f'{out}.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(report, indent=1, ensure_ascii=False))

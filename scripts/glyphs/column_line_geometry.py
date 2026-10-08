"""Per column of one page: every line's own baseline (fitted alone, on its letters), then compare across lines:
skew angle, straightness (departure from a straight line through the line's central part), where curving starts, and
the shape of the curve once skew is removed. Usage: line_geometry.py PAGE.png BOXES.json OUT_PREFIX"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from greekocr.glyphs.components import EIGHT, binarise                      # noqa: E402
from greekocr.glyphs.recut import fit_box                                   # noqa: E402

page = Image.open(sys.argv[1]).convert('L'); gray = np.asarray(page, np.float64)
rows = json.load(open(sys.argv[2])); out = sys.argv[3]
H, W = gray.shape
boxes = [tuple(r['box']) for r in rows]
ink = binarise(gray)

# the column rule: the longest unbroken vertical run of ink near the centre
lo, hi = int(.35 * W), int(.65 * W)
band = ink[int(.05 * H):int(.95 * H), lo:hi]
runs = np.zeros(hi - lo, int)
for j in range(hi - lo):
    col = band[:, j].astype(np.int8)
    if col.any():
        e = np.diff(np.r_[0, col, 0]); runs[j] = int((np.nonzero(e == -1)[0] - np.nonzero(e == 1)[0]).max())
rule = lo + int(np.argmax(runs))
COLS = {'left': (0, rule), 'right': (rule, W)}

# letters of the page
lab, _ = ndi.label(ink, structure=EIGHT)
comps = []
for k, sl in enumerate(ndi.find_objects(lab), start=1):
    if sl is None: continue
    h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
    if h < 8 or h > 80 or w > 120: continue
    comps.append((sl[1].start + w / 2, sl[0].stop - 1, h, sl[1].start, sl[1].stop))
comps = np.array(comps)          # x centre, bottom row, height, x0, x1


def smooth_curve(x, y, grid, step, lam=30.0):
    """Penalised piecewise-linear fit (P-spline): control points every `step` px, penalty on second differences
    (bending). Stable at the ends; no jumps."""
    knots = np.arange(grid[0], grid[-1] + step, step)
    def basis(v):
        B = np.zeros((len(v), len(knots)))
        k = np.clip(((v - knots[0]) // step).astype(int), 0, len(knots) - 2)
        t = (v - knots[k]) / step
        B[np.arange(len(v)), k] = 1 - t; B[np.arange(len(v)), k + 1] = t
        return B
    B = basis(x); D = np.diff(np.eye(len(knots)), 2, axis=0)
    a = np.linalg.solve(B.T @ B + lam * D.T @ D + 1e-6 * np.eye(len(knots)), B.T @ y)
    return basis(grid) @ a


def lowess(x, y, grid, bw):
    outv = np.empty(len(grid))
    for k, g in enumerate(grid):
        w = np.clip(1 - (np.abs(x - g) / bw) ** 3, 0, None) ** 3
        if (w > .05).sum() < 6:                            # too few letters nearby: the 8 nearest, equally weighted
            j = np.argsort(np.abs(x - g))[:8]; w = np.zeros_like(x); w[j] = 1
        A = np.vstack([np.ones_like(x), x - g]).T * np.sqrt(w)[:, None]
        sol, *_ = np.linalg.lstsq(A, y * np.sqrt(w), rcond=None); outv[k] = sol[0]
    return outv


# 1. coordinates for all lines: every box's line per column segment (boxes may span both columns)
fits = [f for i, b in enumerate(boxes) for f in fit_box(gray, b, None, box_index=i, splits=False)]
xh = float(np.median([f.xh for f in fits]))
report, curves, failed = {}, {}, {}
for name, (c0, c1) in COLS.items():
    lines = []
    for f in fits:
        a, b = max(f.x0, c0), min(f.x1, c1)
        if b - a < .5 * (c1 - c0) * .9:                                   # body lines only (half the column or more)
            continue
        if any(abs(np.median(f.base) - np.median(g['init'])) < .5 * xh for g in lines):
            continue                                                       # the same line seen by two boxes
        xs = np.arange(a, b, dtype=np.float64)
        lines.append(dict(box=rows[f.box_index]['line_id'][-6:], init=np.interp(xs, np.arange(f.x0, f.x1), f.base), xs=xs))
    lines.sort(key=lambda L: float(np.median(L['init'])))
    res = []
    for L in lines:
        # 2. each line on its own: letters sitting on its baseline, own smooth curve
        base = L['init']; xs = L['xs']
        for it in range(3):
            sel = (comps[:, 0] >= xs[0]) & (comps[:, 0] < xs[-1]) & (comps[:, 2] >= .5 * xh) & (comps[:, 2] <= 2.4 * xh)
            cx, cb = comps[sel, 0], comps[sel, 1]
            d = cb - np.interp(cx, xs, base)
            ok = np.abs(d) <= .3 * xh
            if ok.sum() < 8: break
            px, py = cx[ok], cb[ok]
            grid = xs[(xs >= px.min()) & (xs <= px.max())]
            base_g = smooth_curve(px, py, grid, xh)
            base = np.interp(xs, grid, base_g)
        gx = grid; gy = base_g
        if ok.sum() < 15 or np.abs(np.diff(gy)).max() > 2 or abs(np.polyfit(gx, gy, 1)[0]) > .1:
            failed.setdefault(name, []).append((L['box'], int(ok.sum()), round(float(np.abs(np.diff(gy)).max()), 1), round(float(np.degrees(np.arctan(np.polyfit(gx, gy, 1)[0]))), 1))); continue
        if any(abs(float(np.median(gy)) - R['y']) < .5 * xh for R in res):
            continue                                                       # the same line seen by two boxes
        # skew from the line's central 60 %; straightness = departure from that straight line
        n = len(gx); mid = slice(int(.2 * n), int(.8 * n))
        k, c = np.polyfit(gx[mid], gy[mid], 1)
        dev = gy - (k * gx + c)
        thr = 4.0                                                          # px (~0.16 x-heights)
        bad = np.abs(dev) > thr
        onset_l = float(gx[np.nonzero(bad[:n // 2])[0].max()]) if bad[:n // 2].any() else None   # curving starts left of here
        onset_r = float(gx[n // 2 + np.nonzero(bad[n // 2:])[0].min()]) if bad[n // 2:].any() else None
        res.append(dict(box=L['box'], y=round(float(np.median(gy))), x0=int(gx[0]), x1=int(gx[-1]), n_letters=int(len(px)),
                        skew_deg=round(float(np.degrees(np.arctan(k))), 3), max_dev_px=round(float(np.abs(dev).max()), 1),
                        rms_dev_px=round(float(np.sqrt((dev ** 2).mean())), 1),
                        dev_left_end_px=round(float(dev[:max(1, n // 20)].mean()), 1), dev_right_end_px=round(float(dev[-max(1, n // 20):].mean()), 1),
                        curve_starts_left_at_x=onset_l, curve_starts_right_at_x=onset_r))
        curves.setdefault(name, []).append((gx, dev))
    # 3. shape similarity: every line's deviation (skew removed) on a common grid vs the column's median shape
    G = np.arange(c0, c1, 4, dtype=np.float64)
    M = np.full((len(curves.get(name, [])), len(G)), np.nan)
    for r_, (gx, dev) in enumerate(curves.get(name, [])):
        inside = (G >= gx[0]) & (G <= gx[-1]); M[r_, inside] = np.interp(G[inside], gx, dev)
    med = np.nanmedian(M, axis=0)
    for r_, R in enumerate(res):
        v = ~np.isnan(M[r_]) & ~np.isnan(med)
        R['shape_rms_vs_column_px'] = round(float(np.sqrt(np.nanmean((M[r_, v] - med[v]) ** 2))), 1)
        a_, b_ = M[r_, v], med[v]
        R['shape_corr_vs_column'] = round(float(np.corrcoef(a_, b_)[0, 1]), 2) if a_.std() > .5 and b_.std() > .5 else None
    sk = np.array([R['skew_deg'] for R in res]); md = np.array([R['max_dev_px'] for R in res])
    onl = [R['curve_starts_left_at_x'] for R in res if R['curve_starts_left_at_x'] is not None]
    onr = [R['curve_starts_right_at_x'] for R in res if R['curve_starts_right_at_x'] is not None]
    report[name] = dict(column_x=[c0, c1], n_lines=len(res), xh=xh, failed=failed.get(name, []),
                        skew_deg=dict(median=round(float(np.median(sk)), 3), p10=round(float(np.percentile(sk, 10)), 3), p90=round(float(np.percentile(sk, 90)), 3), sd=round(float(sk.std()), 3)),
                        straight_lines=int((md <= 4).sum()), curved_lines=int((md > 4).sum()),
                        curving_starts_left=dict(n=len(onl), median_x=round(float(np.median(onl))) if onl else None, iqr_px=round(float(np.subtract(*np.percentile(onl, [75, 25])))) if onl else None),
                        curving_starts_right=dict(n=len(onr), median_x=round(float(np.median(onr))) if onr else None, iqr_px=round(float(np.subtract(*np.percentile(onr, [75, 25])))) if onr else None),
                        shape_rms_vs_column_px=dict(median=round(float(np.median([R['shape_rms_vs_column_px'] for R in res])), 1), max=max(R['shape_rms_vs_column_px'] for R in res)),
                        column_shape_px=[round(float(v), 1) if not np.isnan(v) else None for v in med[::10]],
                        lines=res)
    report[name]['_grid'] = G.tolist(); report[name]['_M'] = [[None if np.isnan(v) else round(float(v), 1) for v in row] for row in M]
json.dump(report, open(f'{out}.json', 'w'))
for name, R in report.items():
    print(f"== {name} column x {R['column_x']}: {R['n_lines']} lines; fit failed: {R['failed']}")
    print('  skew deg: median', R['skew_deg']['median'], 'p10–p90', R['skew_deg']['p10'], '–', R['skew_deg']['p90'], 'sd', R['skew_deg']['sd'])
    print('  straight (max departure ≤ 4 px):', R['straight_lines'], ' curved:', R['curved_lines'])
    print('  curving starts on the left at x: n', R['curving_starts_left']['n'], 'median', R['curving_starts_left']['median_x'], 'IQR', R['curving_starts_left']['iqr_px'])
    print('  curving starts on the right at x: n', R['curving_starts_right']['n'], 'median', R['curving_starts_right']['median_x'], 'IQR', R['curving_starts_right']['iqr_px'])
    print('  shape vs the column median shape (rms px): median', R['shape_rms_vs_column_px']['median'], 'max', R['shape_rms_vs_column_px']['max'])
    for L in R['lines']:
        print('   ', L['box'], 'y', L['y'], 'x', L['x0'], L['x1'], 'skew', L['skew_deg'], 'maxdev', L['max_dev_px'], 'ends', L['dev_left_end_px'], L['dev_right_end_px'],
              'onset', L['curve_starts_left_at_x'], L['curve_starts_right_at_x'], 'shape rms', L['shape_rms_vs_column_px'], 'corr', L['shape_corr_vs_column'])

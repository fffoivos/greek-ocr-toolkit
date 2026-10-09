"""Class-conditioned font evidence and a robust shared-shape six-guide fit.

This module knows pixel components, not OCR characters or document names.
Coordinates increase down the page. Missing classes borrow font ratios and
are never presented as measured contacts.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

GUIDES = ('baseline', 'meanline', 'font_top', 'font_bottom', 'accent_bottom', 'accent_top')
CLASSES = ('body_on_baseline', 'body_with_descender', 'tall_body', 'mark_above',
           'mark_below', 'punctuation', 'not_text')
DEFAULTS = dict(baseline=0., meanline=-1., font_top=-1.5, font_bottom=.5,
                accent_bottom=-1.25, accent_top=-1.85)


def evidence(p, line):
    """Assign marks to bodies and gather contacts from their own ink class."""
    lookup = {int(q[5]): q for q in p.components}
    q = np.array([lookup[k] for k in line.component_ids]).reshape(-1, 7)
    counts = dict.fromkeys(CLASSES, 0)
    points = {k: [] for k in GUIDES}
    xh = line.xheight
    if not len(q):
        return counts, points
    x = (q[:, 0] + q[:, 2]) / 2
    base = np.interp(x, np.arange(line.x0, line.x1), line.baseline)
    heights = q[:, 3] - q[:, 1]
    bodies = (heights >= .6*xh) & (q[:, 4] >= .09*xh*xh) & (q[:, 2]-q[:, 0] < 3*xh)
    # Uniform tall type has no observed small-letter band. Do not pretend its
    # capital tops measure an x-height. A page-font prior supplies that guide.
    bh = heights[bodies]
    capitals = (len(bh) >= 3 and np.percentile(bh, 85)-np.percentile(bh, 15) < .18*xh
                and np.median(bh) > 1.3*p.xheight)
    if capitals:
        line.xheight = xh = float(np.median(bh)/1.5)
    for i, row in enumerate(q):
        a, t, b, bot, area, label, _ = row
        cx, bs = x[i], base[i]
        if not bodies[i]:
            options = []
            for n in np.flatnonzero(bodies):
                dx = max(a-q[n, 2], q[n, 0]-b, 0)
                dy = max(t-q[n, 3], q[n, 1]-bot, 0)
                if dx <= .45*xh and dy < .8*xh:
                    options.append((2*dx+dy, n))
            owner = min(options)[1] if options else None
            if owner is not None and bot < base[owner]-.8*xh:
                # A breathing to the LEFT of a capital belongs to that capital,
                # not the upper small-letter accent band.
                pre_cap = b <= q[owner, 0]+.15*xh and base[owner]-q[owner, 1] > 1.25*xh
                counts['mark_above'] += 1
                if not pre_cap:
                    points['accent_top'].append((cx, t))
                    points['accent_bottom'].append((cx, bot))
            elif owner is not None and t >= base[owner]-.1*xh:
                counts['mark_below'] += 1
                points['font_bottom'].append((cx, bot))
            else:
                counts['punctuation'] += 1
            continue
        if heights[i] > 2.8*xh or area > 4*xh*xh:
            counts['not_text'] += 1
            continue
        # Separate a fused accent at a thin neck above the body. Restrict the
        # search to just above the mean line; never split a letter's stem.
        body_top = t
        if 1.2*xh < bs-t < 2.3*xh and b-a > .3*xh:
            aa, tt, bb, dd = row[:4].astype(int)
            mask = p.labels[tt:dd, aa:bb] == int(label)
            widths = mask.sum(axis=1)
            lo, hi = max(1, round(bs-1.4*xh)-tt), min(len(widths)-1, round(bs-.95*xh)-tt)
            if hi > lo:
                neck = lo + int(np.argmin(widths[lo:hi]))
                above = int(mask[:neck].sum())
                if 0 < widths[neck] <= .22*max(1, widths.max()) and .015*xh*xh < above < .3*area:
                    body_top = tt + neck + 1
                    counts['mark_above'] += 1
                    points['accent_top'].append((cx, t))
                    points['accent_bottom'].append((cx, tt+neck))
        depth, rise = (bot-bs)/xh, (bs-body_top)/xh
        tall = capitals or rise > 1.24
        desc = depth > .22
        counts['tall_body' if tall else 'body_with_descender' if desc else 'body_on_baseline'] += 1
        if -.35 < depth < .22:
            points['baseline'].append((cx, bot))
        elif .22 <= depth < 1.3:
            points['font_bottom'].append((cx, bot))
        if .6 < rise < 2.3:
            points['font_top' if tall else 'meanline'].append((cx, body_top))
    return counts, points


def _smooth_samples(xs, ys, grid, xh):
    """Robust local linear regression; limited extrapolation at curled ends."""
    knots = np.linspace(grid[0], grid[-1], max(2, round(len(grid)/xh)+1))
    values = []
    for gx in knots:
        dx = (xs-gx)/xh
        weight = np.maximum(0, 1-(abs(dx)/4)**3)**3
        if np.count_nonzero(weight > .01) < 3:
            weight = np.exp(-.5*(dx/4)**2)
        design = np.column_stack((np.ones(len(xs)), dx))
        coef = np.zeros(2)
        for _ in range(3):
            residual = ys-design@coef
            robust = np.minimum(1., .15*xh/np.maximum(abs(residual), 1e-8))
            ww = weight*robust
            coef = np.linalg.solve(design.T@(ww[:, None]*design)+np.diag([1e-8, .1]), design.T@(ww*ys))
        values.append(coef[0])
    return ndi.gaussian_filter1d(np.interp(grid, knots, values), max(1., .4*xh))


def fit_guides(p, lines):
    """Alternate one smooth shape and six robust class offsets per line.

    Reliable neighbouring lines regularise the shape inherited from the crop
    fits. Sparse lines retain that shared geometry and fit only their offsets.
    """
    evidence_rows = [evidence(p, line) for line in lines]
    ratios = []
    for line, (counts, points) in zip(lines, evidence_rows):
        offsets = {}
        grid = np.arange(line.x0, line.x1)
        for name, pts in points.items():
            if pts:
                xy = np.array(pts)
                offsets[name] = float(np.median(xy[:, 1]-np.interp(xy[:, 0], grid, line.baseline)) / line.xheight)
        ratios.append(offsets)
    for i, (line, (counts, points)) in enumerate(zip(lines, evidence_rows)):
        xh = line.xheight
        grid = np.arange(line.x0, line.x1)
        shape = line.baseline.copy()
        offsets, borrowed = {}, []
        for name in GUIDES:
            if name in ratios[i]:
                offsets[name] = ratios[i][name]*xh
            else:
                peers = [r[name] for n, r in zip(lines, ratios)
                         if .8 <= n.xheight/xh <= 1.25 and name in r and n.discounted is None]
                offsets[name] = (float(np.median(peers)) if peers else DEFAULTS[name])*xh
                borrowed.append(name)
        supported = sum(len(v) for v in points.values())
        if supported >= 12 and line.support >= 8:
            for _ in range(3):
                px, residual = [], []
                for name, pts in points.items():
                    if not pts:
                        continue
                    xy = np.array(pts)
                    delta = xy[:, 1]-np.interp(xy[:, 0], grid, shape)
                    offsets[name] = float(np.median(delta))
                    good = abs(delta-offsets[name]) < .4*xh
                    px.extend(xy[good, 0]); residual.extend(delta[good]-offsets[name])
                if len(px) >= 8:
                    correction = _smooth_samples(np.array(px), np.array(residual), grid, xh)
                    shape += np.clip(correction, -.25*xh, .25*xh)
        # The baseline anchors the gauge of the common shape.
        shape += offsets['baseline']
        offsets = {k: v-offsets['baseline'] for k, v in offsets.items()}
        # Reject impossible class offsets as evidence, then borrow explicitly.
        bounds = dict(meanline=(-1.25, -.65), font_top=(-2.2, -1.05),
                      font_bottom=(.08, 1.2), accent_bottom=(-2.3, -1.05), accent_top=(-2.8, -1.1))
        for name, (lo, hi) in bounds.items():
            if not lo*xh <= offsets[name] <= hi*xh:
                offsets[name] = DEFAULTS[name]*xh
                if name not in borrowed:
                    borrowed.append(name)
        offsets['font_top'] = min(offsets['font_top'], offsets['meanline'])
        offsets['accent_top'] = min(offsets['accent_top'], offsets['font_top'], offsets['accent_bottom']-.1*xh)
        offsets['accent_bottom'] = min(offsets['accent_bottom'], offsets['meanline']-.05*xh)
        # Constant x-height remains the API reference; the per-pixel mean line
        # admits gradual foreshortening only when small-letter evidence spans it.
        scale = np.ones(len(grid))
        small = np.array(points['meanline']).reshape(-1, 2)
        if len(small) >= 12 and np.ptp(small[:, 0]) > 8*xh:
            observed = (np.interp(small[:, 0], grid, shape)-small[:, 1])/max(1., -offsets['meanline'])
            if np.percentile(observed, 90)-np.percentile(observed, 10) > .2:
                change = _smooth_samples(small[:, 0], (observed-1)*xh, grid, 2*xh)/xh
                scale = 1+np.clip(change, -.15, .15)
        for name in GUIDES:
            setattr(line, name, shape+offsets[name]*scale)
        line.xheight = float(np.median(line.baseline-line.meanline))
        line.borrowed = tuple(borrowed)
        line.ink_classes = counts
        line.guide_samples = points
        line.guide_residuals = {}
        for name, pts in points.items():
            if pts:
                xy = np.array(pts)
                residual = abs(xy[:, 1]-np.interp(xy[:, 0], grid, getattr(line, name)))/line.xheight
                line.guide_residuals[name] = dict(count=len(pts), median=float(np.median(residual)),
                                                p90=float(np.percentile(residual, 90)), maximum=float(residual.max()))
            else:
                line.guide_residuals[name] = dict(count=0, median=None, p90=None, maximum=None)
        line.geometry_source = 'joint-classes' if supported >= 12 and line.support >= 8 else 'borrowed'

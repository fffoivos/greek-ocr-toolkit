"""Class-conditioned font evidence and a robust shared-shape six-guide fit.

This module knows pixel components, not OCR characters or document names.
Coordinates increase down the page. Missing classes borrow font ratios and
are never presented as measured contacts.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi


BODY_MIN_HEIGHT_XH = 0.6  # x-heights: body evidence must span most of the small-letter band.
BODY_MIN_AREA_XH2 = 0.09  # square x-heights: detached specks do not support a body guide.
BODY_MAX_WIDTH_XH = 3  # x-heights: wider blobs cannot give an individual-body top contact.
CAPITAL_HEIGHT_SPREAD_XH = 0.18  # x-heights: a narrow height spread supports uniform capital type.
CAPITAL_MIN_PAGE_SIZE_RATIO = 1.3  # dimensionless size ratio: separate all-capital height from the page body size.
CAPITAL_HEIGHT_XH = 1.5  # x-heights: default capital height when no small bodies are observed.
MARK_HORIZONTAL_REACH_XH = 0.45  # x-heights: attach a nearby mark without crossing to the next body.
MARK_VERTICAL_REACH_XH = 0.8  # x-heights: allow detached breathings and accents above their bodies.
UPPER_MARK_MIN_RISE_XH = 0.8  # x-heights above baseline: upper marks must clear the body band.
PRECAP_MARK_OVERLAP_XH = 0.15  # x-heights: identify a breathing preceding a capital rather than above it.
PRECAP_MIN_RISE_XH = 1.25  # x-heights above baseline: require capital-sized support for a preceding mark.
LOWER_MARK_BASELINE_SLACK_XH = 0.1  # x-heights: allow a lower mark to touch the baseline.
TEXT_MAX_HEIGHT_XH = 2.8  # x-heights: reject components beyond a body plus accents and descender.
TEXT_MAX_AREA_XH2 = 4  # square x-heights: large solid components are not single-letter guide evidence.
FUSED_MARK_MIN_RISE_XH = 1.2  # x-heights: only inspect potential fused accents above the ordinary body.
FUSED_MARK_MIN_WIDTH_XH = 0.3  # x-heights: a narrow stem is insufficient evidence for a fused accent.
FUSED_NECK_SEARCH_TOP_XH = 1.4  # x-heights: start the neck search above the meanline, below very high accents.
FUSED_NECK_SEARCH_BOTTOM_XH = 0.95  # x-heights: stop the neck search close to the meanline, protecting body stems.
FUSED_NECK_MAX_WIDTH_RATIO = 0.22  # dimensionless width ratio: require a narrow connection before separating an accent.
FUSED_MARK_MIN_AREA_XH2 = 0.015  # square x-heights: a detached upper pixel speck is not a fused mark.
TALL_BODY_MIN_RISE_XH = 1.24  # x-heights: tall bodies exceed the observed small-letter band.
DESCENDER_MIN_DEPTH_XH = 0.22  # x-heights below baseline: tolerate contact noise before declaring a descender.
BASELINE_CONTACT_RISE_XH = 0.35  # x-heights: a slightly raised bottom can still support the baseline.
DESCENDER_MAX_DEPTH_XH = 1.3  # x-heights: exclude lower neighbouring text from descender evidence.
LOCAL_FIT_RADIUS_XH = 4  # x-heights: local guide regression follows curvature over a short word.
MIN_LOCAL_WEIGHT = 0.01  # dimensionless weight: ignore negligible distant samples when counting support.
ROBUST_RESIDUAL_XH = 0.15  # x-heights: downweight contacts inconsistent with the shared guide shape.
SOLVE_EPSILON = 1e-08  # dimensionless numerical ridge: keep degenerate local regression solvable.
SLOPE_RIDGE = 0.1  # dimensionless normal-matrix ridge: restrain unsupported local slopes.
GUIDE_SMOOTH_XH = 0.4  # x-heights: smooth sub-letter noise in the interpolated guide correction.
BORROW_MIN_SIZE_RATIO = 0.8  # dimensionless size ratio: borrow offsets only from comparable nearby type sizes.
MIN_GUIDE_CONTACTS = 12  # contact count: enough independent class samples to refine shared geometry.
MIN_BODY_SUPPORT = 8  # body count: prevent a few table digits from defining a new guide shape.
GUIDE_INLIER_RESIDUAL_XH = 0.4  # x-heights: reject outlying class contacts before shape correction.
MAX_GUIDE_CORRECTION_XH = 0.25  # x-heights per iteration: cap a guide correction relative to the crop fit.
MIN_ACCENT_BAND_XH = 0.1  # x-heights: retain positive thickness for the default upper accent band.
ACCENT_BODY_CLEARANCE_XH = 0.05  # x-heights: keep an upper accent guide above the body meanline.
SCALE_MIN_SPAN_XH = 8  # x-heights: foreshortening needs small-letter evidence across a word span.
SCALE_MIN_SPREAD = 0.2  # dimensionless relative height spread: do not fit foreshortening to measurement noise.
MAX_LOCAL_SIZE_CHANGE = 0.15  # dimensionless height ratio: bound local foreshortening relative to the line reference.
FUSED_MARK_MAX_RISE_XH = 2.3  # x-heights: cap a fused body/mark extent before it becomes neighbouring text.
FUSED_MARK_MAX_AREA_SHARE = 0.3  # dimensionless area share: a fused mark must be smaller than its body.
BORROW_MAX_SIZE_RATIO = 1.25  # dimensionless size ratio: borrow offsets only from comparable nearby type sizes.

GUIDES = ('baseline', 'meanline', 'font_top', 'font_bottom', 'accent_bottom', 'accent_top')
CLASSES = ('body_on_baseline', 'body_with_descender', 'tall_body', 'mark_above',
           'mark_below', 'punctuation', 'not_text')
# Signed x-height offsets from baseline; fallback geometry when a class has no local contacts.
DEFAULTS = dict(baseline=0., meanline=-1., font_top=-1.5, font_bottom=.5,
                accent_bottom=-1.25, accent_top=-1.85)


GAUSSIAN_EXPONENT_FACTOR = 0.5  # dimensionless Gaussian coefficient: use a standard squared-distance contact kernel.
MEANLINE_MAX_RISE_XH = 1.25  # x-heights above baseline: cap an unsupported meanline extrapolation.
FONT_TOP_MAX_RISE_XH = 2.2  # x-heights above baseline: bound a sparse capital/ascender guide.
FONT_BOTTOM_MIN_DROP_XH = 0.08  # x-heights below baseline: retain a small descender allowance.
ACCENT_BOTTOM_MAX_RISE_XH = 2.3  # x-heights above baseline: bound the lower guide of a sparse accent band.
ACCENT_TOP_MAX_RISE_XH = 2.8  # x-heights above baseline: prevent an unsupported accent guide from reaching another row.
MEANLINE_MIN_RISE_XH = 0.65  # x-heights above baseline: prevent the meanline collapsing onto the baseline.
FONT_TOP_MIN_RISE_XH = 1.05  # x-heights above baseline: capital/ascender guide stays above the body meanline.
FONT_BOTTOM_MAX_DROP_XH = 1.2  # x-heights below baseline: bound unsupported descender extrapolation.
ACCENT_BOTTOM_MIN_RISE_XH = 1.05  # x-heights above baseline: accent lower guide stays above the body band.
ACCENT_TOP_MIN_RISE_XH = 1.1  # x-heights above baseline: accent upper guide stays above the meanline.

LOCAL_SIZE_SMOOTHING_XH = 2  # x-heights: smooth local body-size changes across neighboring letters.

def evidence(p, line, *, _lookup=None):
    """Assign marks to bodies and gather contacts from their own ink class."""
    lookup = {int(q[5]): q for q in p.components} if _lookup is None else _lookup
    q = np.array([lookup[k] for k in line.component_ids]).reshape(-1, 7)
    counts = dict.fromkeys(CLASSES, 0)
    points = {k: [] for k in GUIDES}
    xh = line.xheight
    if not len(q):
        return counts, points
    x = (q[:, 0] + q[:, 2]) / 2
    base = np.interp(x, np.arange(line.x0, line.x1), line.baseline)
    heights = q[:, 3] - q[:, 1]
    bodies = (heights >= BODY_MIN_HEIGHT_XH*xh) & (q[:, 4] >= BODY_MIN_AREA_XH2*xh*xh) & (q[:, 2]-q[:, 0] < BODY_MAX_WIDTH_XH*xh)
    # Uniform tall type has no observed small-letter band. Do not pretend its
    # capital tops measure an x-height. A page-font prior supplies that guide.
    bh = heights[bodies]
    capitals = (len(bh) >= 3 and np.percentile(bh, 85)-np.percentile(bh, 15) < CAPITAL_HEIGHT_SPREAD_XH*xh
                and np.median(bh) > CAPITAL_MIN_PAGE_SIZE_RATIO*p.xheight)
    if capitals:
        line.xheight = xh = float(np.median(bh)/CAPITAL_HEIGHT_XH)
    for i, row in enumerate(q):
        a, t, b, bot, area, label, _ = row
        cx, bs = x[i], base[i]
        if not bodies[i]:
            options = []
            for n in np.flatnonzero(bodies):
                dx = max(a-q[n, 2], q[n, 0]-b, 0)
                dy = max(t-q[n, 3], q[n, 1]-bot, 0)
                if dx <= MARK_HORIZONTAL_REACH_XH*xh and dy < MARK_VERTICAL_REACH_XH*xh:
                    options.append((2*dx+dy, n))
            owner = min(options)[1] if options else None
            if owner is not None and bot < base[owner]-UPPER_MARK_MIN_RISE_XH*xh:
                # A breathing to the LEFT of a capital belongs to that capital,
                # not the upper small-letter accent band.
                pre_cap = b <= q[owner, 0]+PRECAP_MARK_OVERLAP_XH*xh and base[owner]-q[owner, 1] > PRECAP_MIN_RISE_XH*xh
                counts['mark_above'] += 1
                if not pre_cap:
                    points['accent_top'].append((cx, t))
                    points['accent_bottom'].append((cx, bot))
            elif owner is not None and t >= base[owner]-LOWER_MARK_BASELINE_SLACK_XH*xh:
                counts['mark_below'] += 1
                points['font_bottom'].append((cx, bot))
            else:
                counts['punctuation'] += 1
            continue
        if heights[i] > TEXT_MAX_HEIGHT_XH*xh or area > TEXT_MAX_AREA_XH2*xh*xh:
            counts['not_text'] += 1
            continue
        # Separate a fused accent at a thin neck above the body. Restrict the
        # search to just above the mean line; never split a letter's stem.
        body_top = t
        if FUSED_MARK_MIN_RISE_XH*xh < bs-t < FUSED_MARK_MAX_RISE_XH*xh and b-a > FUSED_MARK_MIN_WIDTH_XH*xh:
            aa, tt, bb, dd = row[:4].astype(int)
            mask = p.labels[tt:dd, aa:bb] == int(label)
            widths = mask.sum(axis=1)
            lo, hi = max(1, round(bs-FUSED_NECK_SEARCH_TOP_XH*xh)-tt), min(len(widths)-1, round(bs-FUSED_NECK_SEARCH_BOTTOM_XH*xh)-tt)
            if hi > lo:
                neck = lo + int(np.argmin(widths[lo:hi]))
                above = int(mask[:neck].sum())
                if 0 < widths[neck] <= FUSED_NECK_MAX_WIDTH_RATIO*max(1, widths.max()) and FUSED_MARK_MIN_AREA_XH2*xh*xh < above < FUSED_MARK_MAX_AREA_SHARE*area:
                    body_top = tt + neck + 1
                    counts['mark_above'] += 1
                    points['accent_top'].append((cx, t))
                    points['accent_bottom'].append((cx, tt+neck))
        depth, rise = (bot-bs)/xh, (bs-body_top)/xh
        tall = capitals or rise > TALL_BODY_MIN_RISE_XH
        desc = depth > DESCENDER_MIN_DEPTH_XH
        counts['tall_body' if tall else 'body_with_descender' if desc else 'body_on_baseline'] += 1
        if -BASELINE_CONTACT_RISE_XH < depth < DESCENDER_MIN_DEPTH_XH:
            points['baseline'].append((cx, bot))
        elif DESCENDER_MIN_DEPTH_XH <= depth < DESCENDER_MAX_DEPTH_XH:
            points['font_bottom'].append((cx, bot))
        if BODY_MIN_HEIGHT_XH < rise < FUSED_MARK_MAX_RISE_XH:
            points['font_top' if tall else 'meanline'].append((cx, body_top))
    return counts, points


def _smooth_samples(xs, ys, grid, xh):
    """Robust local linear regression; limited extrapolation at curled ends."""
    knots = np.linspace(grid[0], grid[-1], max(2, round(len(grid)/xh)+1))
    values = []
    for gx in knots:
        dx = (xs-gx)/xh
        weight = np.maximum(0, 1-(abs(dx)/LOCAL_FIT_RADIUS_XH)**3)**3
        if np.count_nonzero(weight > MIN_LOCAL_WEIGHT) < 3:
            weight = np.exp(-GAUSSIAN_EXPONENT_FACTOR*(dx/LOCAL_FIT_RADIUS_XH)**2)
        design = np.column_stack((np.ones(len(xs)), dx))
        coef = np.zeros(2)
        for _ in range(3):
            residual = ys-design@coef
            robust = np.minimum(1., ROBUST_RESIDUAL_XH*xh/np.maximum(abs(residual), SOLVE_EPSILON))
            ww = weight*robust
            coef = np.linalg.solve(design.T@(ww[:, None]*design)+np.diag([SOLVE_EPSILON, SLOPE_RIDGE]), design.T@(ww*ys))
        values.append(coef[0])
    return ndi.gaussian_filter1d(np.interp(grid, knots, values), max(1., GUIDE_SMOOTH_XH*xh))


def fit_guides(p, lines, *, _lookup=None):
    """Alternate one smooth shape and six robust class offsets per line.

    Reliable neighbouring lines regularise the shape inherited from the crop
    fits. Sparse lines retain that shared geometry and fit only their offsets.
    """
    lookup = {int(q[5]): q for q in p.components} if _lookup is None else _lookup
    evidence_rows = [evidence(p, line, _lookup=lookup) for line in lines]
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
                         if BORROW_MIN_SIZE_RATIO <= n.xheight/xh <= BORROW_MAX_SIZE_RATIO and name in r and n.discounted is None]
                offsets[name] = (float(np.median(peers)) if peers else DEFAULTS[name])*xh
                borrowed.append(name)
        supported = sum(len(v) for v in points.values())
        if supported >= MIN_GUIDE_CONTACTS and line.support >= MIN_BODY_SUPPORT:
            for _ in range(3):
                px, residual = [], []
                for name, pts in points.items():
                    if not pts:
                        continue
                    xy = np.array(pts)
                    delta = xy[:, 1]-np.interp(xy[:, 0], grid, shape)
                    offsets[name] = float(np.median(delta))
                    good = abs(delta-offsets[name]) < GUIDE_INLIER_RESIDUAL_XH*xh
                    px.extend(xy[good, 0]); residual.extend(delta[good]-offsets[name])
                if len(px) >= MIN_BODY_SUPPORT:
                    correction = _smooth_samples(np.array(px), np.array(residual), grid, xh)
                    shape += np.clip(correction, -MAX_GUIDE_CORRECTION_XH*xh, MAX_GUIDE_CORRECTION_XH*xh)
        # The baseline anchors the gauge of the common shape.
        shape += offsets['baseline']
        offsets = {k: v-offsets['baseline'] for k, v in offsets.items()}
        # Reject impossible class offsets as evidence, then borrow explicitly.
        # Signed x-height plausibility limits reject impossible class offsets before explicit borrowing.
        bounds = dict(meanline=(-MEANLINE_MAX_RISE_XH, -MEANLINE_MIN_RISE_XH), font_top=(-FONT_TOP_MAX_RISE_XH, -FONT_TOP_MIN_RISE_XH),
                      font_bottom=(FONT_BOTTOM_MIN_DROP_XH, FONT_BOTTOM_MAX_DROP_XH), accent_bottom=(-ACCENT_BOTTOM_MAX_RISE_XH, -ACCENT_BOTTOM_MIN_RISE_XH), accent_top=(-ACCENT_TOP_MAX_RISE_XH, -ACCENT_TOP_MIN_RISE_XH))
        for name, (lo, hi) in bounds.items():
            if not lo*xh <= offsets[name] <= hi*xh:
                offsets[name] = DEFAULTS[name]*xh
                if name not in borrowed:
                    borrowed.append(name)
        offsets['font_top'] = min(offsets['font_top'], offsets['meanline'])
        offsets['accent_top'] = min(offsets['accent_top'], offsets['font_top'], offsets['accent_bottom']-MIN_ACCENT_BAND_XH*xh)
        offsets['accent_bottom'] = min(offsets['accent_bottom'], offsets['meanline']-ACCENT_BODY_CLEARANCE_XH*xh)
        # Constant x-height remains the API reference; the per-pixel mean line
        # admits gradual foreshortening only when small-letter evidence spans it.
        scale = np.ones(len(grid))
        small = np.array(points['meanline']).reshape(-1, 2)
        if len(small) >= MIN_GUIDE_CONTACTS and np.ptp(small[:, 0]) > SCALE_MIN_SPAN_XH*xh:
            observed = (np.interp(small[:, 0], grid, shape)-small[:, 1])/max(1., -offsets['meanline'])
            if np.percentile(observed, 90)-np.percentile(observed, 10) > SCALE_MIN_SPREAD:
                change = _smooth_samples(small[:, 0], (observed-1)*xh, grid, LOCAL_SIZE_SMOOTHING_XH*xh)/xh
                scale = 1+np.clip(change, -MAX_LOCAL_SIZE_CHANGE, MAX_LOCAL_SIZE_CHANGE)
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
        line.geometry_source = 'joint-classes' if supported >= MIN_GUIDE_CONTACTS and line.support >= MIN_BODY_SUPPORT else 'borrowed'

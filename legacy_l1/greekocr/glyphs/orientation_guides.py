"""Two readings through the existing class-conditioned six-guide fitter.

No data-dependent calibration lives here. Rules and their typographic rationale
were recorded in PAGE_LINES_ROUND4_ORIENTATION_GUIDES_20261009.md before testing.
The sampling budget is shared by both readings, never selected by their scores.
"""
from __future__ import annotations

from collections import Counter
from types import SimpleNamespace

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

from .components import line_glyphs
from .page_font import GUIDES, fit_guides
from .page_text_lines import LineSegment

MAX_LINES = 12
WINDOW_WIDTH_XH = 32
WINDOW_HALF_HEIGHT_XH = 3
CONTACT_TOLERANCE_XH = .15
MIN_BASELINE_CONTACTS = 12
MIN_MARKS = 3
MARK_SUPERMAJORITY = 3
MIN_VARIABLE_BODIES = 3


def _windows(gray, mask, height):
    """Symmetric ink-support sampling, before either polarity has been fitted."""
    _, _, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    q = stats[1:]
    if not len(q):
        return []
    h = max(3., float(height))
    bodies = q[(q[:, 3] >= .6*h) & (q[:, 3] <= 2.8*h) &
               (q[:, 2] < 3*h) & (q[:, 4] >= .09*h*h)]
    if not len(bodies):
        return []
    profile = np.zeros(gray.shape[0])
    for x, y, w, hh, area in bodies:
        profile[y:y+hh] += area/hh
    smooth = gaussian_filter1d(profile, max(1., .3*h))
    peaks, _ = find_peaks(np.r_[0, smooth, 0], distance=max(1, round(1.5*h)))
    peaks = peaks-1
    peaks = sorted(peaks, key=lambda y: (-smooth[y], y))[:MAX_LINES]
    windows = []
    for y in peaks:
        own = bodies[abs(bodies[:, 1]+bodies[:, 3]/2-y) < h]
        if len(own) < 3:
            continue
        along = np.zeros(gray.shape[1])
        for x, _, w, _, area in own:
            along[x:x+w] += area/w
        width = min(len(along), max(1, round(WINDOW_WIDTH_XH*h)))
        # Centre a fixed-width window on maximal body support, before fitting.
        sums = np.convolve(along, np.ones(width), 'valid')
        x0 = int(np.argmax(sums)); x1 = x0+width
        t = max(0, int(y-WINDOW_HALF_HEIGHT_XH*h))
        b = min(gray.shape[0], int(y+WINDOW_HALF_HEIGHT_XH*h)+1)
        windows.append((x0, t, x1, b, float(y-t)))
    return windows


def _line_fit(gray, centre, height):
    """Use the detector's crop band and page_font.fit_guides, without new proxies."""
    g = line_glyphs(gray,
                    focus=(centre-.25*height, centre+1.25*height))
    height = g.band.xh
    base = g.band.bottom.copy()
    rows = []
    for c in g.components:
        x = int(np.clip(c.cx, 0, len(base)-1))
        # Same body/mark ownership envelope as the detector; neighbour lines do
        # not become extra accent observations in this sampled line.
        if c.role in ('rule', 'large', 'neighbour'):
            continue
        if not base[x]-2.8*height <= (c.y0+c.y1)/2 <= base[x]+1.3*height:
            continue
        rows.append((c.x0, c.y0, c.x1, c.y1, c.area, c.index, c.darkness))
    components = np.asarray(rows, float).reshape(-1, 7)
    p = SimpleNamespace(components=components, labels=g.labels, xheight=height)
    line = LineSegment(0, gray.shape[1], base, base-1.5*height, base-height,
                       base+.5*height, base-2.8*height, base+1.3*height, height,
                       support=g.band.n_support,
                       component_ids=tuple(components[:, 5].astype(int)))
    fit_guides(p, [line])
    return line


def _reading(samples, half_turn, height):
    counts = Counter(); contacts = Counter(); residual_sum = Counter()
    ratios = {k: [] for k in GUIDES if k != 'baseline'}
    rows = []; above = below = 0
    for gray, centre, box in samples:
        if half_turn:
            gray = np.rot90(gray, 2).copy()
            centre = gray.shape[0]-1-centre
        line = _line_fit(gray, centre, height)
        counts.update(line.ink_classes)
        for name, value in line.guide_residuals.items():
            # Model-imputed coordinates are not measurements.
            if name not in line.borrowed:
                n = value['count']; contacts[name] += n
                if n:
                    xy = np.asarray(line.guide_samples[name])
                    residual = abs(xy[:, 1]-np.interp(xy[:, 0], np.arange(line.x1), getattr(line, name)))/line.xheight
                    residual_sum[name] += float(residual.sum())
                    if name != 'baseline':
                        ratios[name].append(float(np.median((getattr(line, name)-line.baseline)/line.xheight)))
        nmark = 0
        if 'accent_top' not in line.borrowed and 'accent_bottom' not in line.borrowed:
            tops = np.asarray(line.guide_samples['accent_top']).reshape(-1, 2)
            bottoms = np.asarray(line.guide_samples['accent_bottom']).reshape(-1, 2)
            for top, bot in zip(tops, bottoms):
                x = top[0]; grid = np.arange(line.x1)
                rt = abs(top[1]-np.interp(x, grid, line.accent_top))/line.xheight
                rb = abs(bot[1]-np.interp(x, grid, line.accent_bottom))/line.xheight
                if max(rt, rb) <= CONTACT_TOLERANCE_XH:
                    nmark += 1
        above += nmark
        below += line.ink_classes.get('mark_below', 0)
        rows.append(dict(box=box, xheight=line.xheight, classes=line.ink_classes,
                         contacts=line.guide_residuals, borrowed=list(line.borrowed),
                         measured_accents=nmark,
                         ratios={k:float(np.median((getattr(line,k)-line.baseline)/line.xheight)) for k in ratios}))
    residuals = {k:residual_sum[k]/contacts[k] if contacts[k] else None for k in GUIDES}
    proportions = {k:dict(median=float(np.median(v)), spread=float(np.ptp(v)), lines=len(v))
                   for k,v in ratios.items() if v}
    # A class assignment is not a measured font proportion. Count variable
    # bodies only when their own fitted guide has observed, tight contacts.
    # This excludes ragged punctuation/digit edges merely labelled 'tall'.
    variable = sum(contacts[name] for name in ('font_top', 'font_bottom')
                   if residuals[name] is not None and residuals[name] <= CONTACT_TOLERANCE_XH)
    baseline_ok = contacts['baseline'] >= MIN_BASELINE_CONTACTS and residuals['baseline'] <= CONTACT_TOLERANCE_XH
    strong = (baseline_ok and variable >= MIN_VARIABLE_BODIES and above >= MIN_MARKS and
              above >= MARK_SUPERMAJORITY*max(1, below))
    close = baseline_ok and variable >= MIN_VARIABLE_BODIES and above > below
    return dict(lines=rows, class_counts=dict(counts), contacts=dict(contacts),
                residuals_xh=residuals, proportions=proportions, accent_above=above,
                mark_below=below, net_marks=above-below, variable_bodies=variable,
                strong=bool(strong), close=bool(close))


def compare_guides(gray, mask, height, axis_angle, *, font_reference=None):
    """Fit identical sampled ink in both readings; return evidence and decision."""
    gray = np.rot90(gray, axis_angle//90).copy()
    mask = np.rot90(mask, axis_angle//90).copy()
    windows = _windows(gray, mask, height)
    samples = [(gray[t:b, x:r], cy, [x,t,r,b]) for x,t,r,b,cy in windows]
    readings = [_reading(samples, half, height) for half in (False, True)]
    for i,r in enumerate(readings):
        r['orientation_cw'] = (axis_angle+180*i)%360
        r['font_disagreements'] = []
        for name, ref in (font_reference or {}).items():
            if name in r['proportions']:
                own = r['proportions'][name]
                if abs(own['median']-ref['median']) > max(CONTACT_TOLERANCE_XH, ref['spread'], own['spread']):
                    r['font_disagreements'].append(name)
    accepted = []; close = []
    for i,r in enumerate(readings):
        other = readings[1-i]
        base = r['residuals_xh']['baseline']
        opposite = other['residuals_xh']['baseline']
        not_worse = base is not None and (opposite is None or base <= opposite+CONTACT_TOLERANCE_XH)
        gap = r['net_marks']-other['net_marks']
        if r['strong'] and gap >= MIN_MARKS and not_worse:
            accepted.append(i)
        if r['close'] and gap > 0 and not_worse and not r['font_disagreements']:
            close.append(i)
    winner = accepted[0] if len(accepted)==1 else None
    close_angle = readings[close[0]]['orientation_cw'] if len(close)==1 else None
    return dict(method='page_font.fit_guides-two-readings', readings=readings,
                sampled_lines=len(samples), sample_budget=MAX_LINES,
                orientation_cw=readings[winner]['orientation_cw'] if winner is not None else None,
                close_candidate=close_angle,
                margin_marks=abs(readings[0]['net_marks']-readings[1]['net_marks']))

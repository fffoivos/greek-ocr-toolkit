"""Descriptive glyph, page, book and corpus statistics over immutable Q1 geometry.

Definitions and a-priori thresholds: docs/reviews/PAGE_LINES_Q2_STATISTICS.md.
Candidate provenance is measured evidence, never a trained or confirmed label.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

from ..glyphs.components import Band, EIGHT, _hole_sizes, _line_geometry
from ..glyphs.ink import ink_profile
from ..glyphs.letters import letter_boxes
from .pixels import _gray

__all__ = ['page_statistics', 'book_statistics', 'corpus_statistics',
           'write_statistics', 'render_glyph_statistics', 'render_book_statistics']

RATIO_EPSILON = 1e-09  # dimensionless ratio floor: avoid division by zero for degenerate measured extents.
NORMAL_MAD_SCALE = 1.4826  # dimensionless Gaussian calibration: express bright-paper MAD as noise sigma.
FIT_FOCUS_XH = 0.25  # x-heights: constrain the crop fitter around the supplied Q1 baseline.
FALLBACK_XHEIGHT_PAGE_DIVISOR = 100  # page short-side units per x-height: retain Q2's scale fallback when no active lines exist.

SCHEMA_VERSION = 1
# Fixed BEFORE the evaluation; photometric ratios and typographic lengths.
THRESHOLDS = dict(font_size_ratio=1.25, tall_rise_xh=1.24, descender_depth_xh=.22,
    mark_dx_xh=.45, mark_dy_xh=.8, aligned_residual_xh=.22,
    show_contrast_ratio=.5, blurred_edge_ratio=.65, off_line_residual_xh=.35,
    letter_min_height_xh=.3, letter_max_height_xh=2.8, letter_max_width_xh=3.,
    stamp_min_width_xh=3., stamp_min_height_xh=2.8, stamp_contrast_ratio=.85,
    color_spread=.10, rule_aspect=10., thick_stroke_ratio=1.75, thick_fill=.65,
    paper_pad_xh=.5, residual_paper_grid_xh=4., residual_noise_sigma=4.,
    residual_contrast_fraction=.15, residual_min_gray=10., residual_area_xh2=.02,
    owned_halo_xh=.08)


COMPONENT_MAX_HEIGHT_XH = 2.8  # x-heights: tall connected regions remain residual evidence, not individual bodies.
COMPONENT_MAX_WIDTH_XH = 6  # x-heights: very wide connected regions cannot be measured as a single body.
BODY_MIN_OVERLAP = 0.5  # dimensionless body-band overlap: require substantial support for a letter body.
BODY_MIN_HEIGHT_XH = 0.5  # x-heights: distinguish bodies from detached marks and punctuation.
UPPER_MARK_OFFSET_XH = 0.8  # x-heights above baseline: detached upper marks sit above most of the body band.
LOWER_MARK_OFFSET_XH = 0.1  # x-heights above baseline: lower punctuation is close to or below the baseline.
ATTACHED_MARK_MAX_HEIGHT_XH = 0.8  # x-heights: large components should not be absorbed as detached marks.
LOOSE_MARK_MAX_HEIGHT_XH = 0.6  # x-heights: a nearby small component remains separate mark/punctuation evidence.
LOOSE_MARK_TOP_REACH_XH = 0.4  # x-heights: preserve marks just above the visible ink envelope.
LOOSE_MARK_BOTTOM_REACH_XH = 0.3  # x-heights: preserve punctuation just below the baseline.
PLOT_MIN_BODY_SIZE_PAGE = 0.01  # fraction of page width: keep a useful scale when the body-size plot has no samples.
PLOT_HEADROOM = 1.15  # dimensionless plot scale: leave room above the largest body-size sample.

def _distribution(values):
    a = np.asarray([x for x in values if x is not None and np.isfinite(x)], float)
    if not len(a):
        return dict(n=0, median=None, p10=None, p90=None, mean=None, std=None)
    p10, p90 = np.percentile(a, [10, 90])
    return dict(n=len(a), median=float(np.median(a)), p10=float(p10),
                p90=float(p90), mean=float(a.mean()), std=float(a.std()))


def _median(values):
    a = np.asarray([x for x in values if x is not None and np.isfinite(x)], float)
    return float(np.median(a)) if len(a) else None


def _ratio(a, b):
    return float(a / b) if a is not None and b is not None and b > 0 else None


def _size_groups(values):
    """Complete-span clusters; membership never changes earlier observations."""
    groups = []
    for key, value in sorted(values, key=lambda kv: (kv[1], str(kv[0]))):
        if not groups or value > groups[-1]['minimum'] * THRESHOLDS['font_size_ratio']:
            groups.append(dict(id=f'font-{len(groups):02d}', minimum=value, values=[], keys=[]))
        groups[-1]['keys'].append(key)
        groups[-1]['values'].append(value)
    mapping = {k: g['id'] for g in groups for k in g['keys']}
    return mapping, [dict(id=g['id'], size_page_width=_distribution(g['values']),
                          members=len(g['keys'])) for g in groups]


def _body_class(box, baseline, xh):
    rise, depth = (baseline-box[1])/xh, (box[3]-baseline)/xh
    kind = 'tall' if rise > THRESHOLDS['tall_rise_xh'] else (
        'descender' if depth > THRESHOLDS['descender_depth_xh'] else 'body')
    return kind, rise, depth


def _curve(line, name, x):
    # Unit-spaced source samples: only the two bracketing values contribute.
    values = line[name]
    i = max(0, min(len(values)-1, int(np.floor(x))-line['x0']))
    if i == len(values)-1:
        return float(values[i])
    left = line['x0'] + i
    return float(np.interp(x, (left, left+1), values[i:i+2]))


def _line_residual(box, line):
    """Distance to nearest legal top or bottom guide, in the assigned x-height."""
    cx = (box[0]+box[2])/2
    return min(
        abs(box[1]-_curve(line, 'meanline', cx)), abs(box[1]-_curve(line, 'font_top', cx)),
        abs(box[3]-_curve(line, 'baseline', cx)), abs(box[3]-_curve(line, 'font_bottom', cx))) / line['xheight']


def _measure(gray, rgb, box, mask, xh, page_paper):
    """Measure only supplied ink pixels; no pixels from neighbouring letters."""
    a, t, b, d = box
    pad = max(1, round(THRESHOLDS['paper_pad_xh']*xh))
    aa, tt, bb, dd = max(0, a-pad), max(0, t-pad), min(gray.shape[1], b+pad), min(gray.shape[0], d+pad)
    patch = gray[tt:dd, aa:bb]
    ring = np.ones(patch.shape, bool)
    ring[t-tt:d-tt, a-aa:b-aa] = False
    paper = float(np.percentile(patch[ring], 90)) if ring.any() else page_paper
    vals = gray[t:d, a:b][mask]
    ink = float(np.median(vals))
    delta = max(0., paper-ink)
    # A padded mask provides the outside sample on all non-page boundaries.
    pmask = np.zeros(patch.shape, bool)
    pmask[t-tt:d-tt, a-aa:b-aa] = mask
    boundary = pmask & ~ndi.binary_erosion(pmask)
    boundary[[0, -1], :] = False
    boundary[:, [0, -1]] = False
    mag = np.hypot(ndi.sobel(patch, 0), ndi.sobel(patch, 1))/8
    edge = float(np.median(mag[boundary]))*xh/max(delta, 1.) if boundary.any() else None
    distance = ndi.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
    ridge = (distance > 0) & (distance >= ndi.maximum_filter(distance, 3))
    stroke = 2*float(np.median(distance[ridge])) if ridge.any() else 0.
    holes = _hole_sizes(mask)
    n_holes = len(holes)
    hole_area = int(holes.sum())
    color = None
    if rgb is not None:
        pixels = rgb[t:d, a:b][mask].astype(float)
        color = float(np.median(pixels.max(axis=1)-pixels.min(axis=1))/255)
    return dict(ink_pixels=int(mask.sum()), ink_gray=ink, darkness=1-ink/255,
        paper_gray=paper, contrast_absolute=delta/255, contrast_local=delta/max(paper, 1),
        edge_sharpness=edge, color_spread=color, color_available=rgb is not None,
        height_xh=(d-t)/xh, width_xh=(b-a)/xh, stroke_width_px=stroke, stroke_width_xh=stroke/xh,
        fill=float(mask.mean()), holes=int(n_holes), hole_area=hole_area,
        hole_fraction=hole_area / mask.size)


def _reference(rows):
    aligned = [r for r in rows if r['entity_kind'] == 'letter_body' and
               r['line_residual_xh'] is not None and r['line_residual_xh'] <= THRESHOLDS['aligned_residual_xh']]
    halfway = _median([r['contrast_local'] for r in aligned])
    seed = [r for r in aligned if r['contrast_local'] >= halfway] if halfway is not None else []
    return dict(contrast_absolute=_median([r['contrast_absolute'] for r in seed]),
                edge_sharpness=_median([r['edge_sharpness'] for r in seed]),
                stroke_width_xh=_median([r['stroke_width_xh'] for r in seed]),
                aligned_bodies=len(aligned), support=len(seed), method='aligned-upper-half-local-contrast')


def _provenance(row, reference):
    contrast = _ratio(row['contrast_absolute'], reference['contrast_absolute'])
    edge = _ratio(row['edge_sharpness'], reference['edge_sharpness'])
    off = row['line_index'] is None or row['line_residual_xh'] > THRESHOLDS['off_line_residual_xh']
    faint = contrast is not None and contrast < THRESHOLDS['show_contrast_ratio']
    blurred = edge is not None and edge < THRESHOLDS['blurred_edge_ratio']
    letter_like = (THRESHOLDS['letter_min_height_xh'] <= row['height_xh'] <= THRESHOLDS['letter_max_height_xh']
                   and row['width_xh'] <= THRESHOLDS['letter_max_width_xh'])
    color = row['color_spread'] is not None and row['color_spread'] > THRESHOLDS['color_spread']
    w, h = row['width_xh'], row['height_xh']
    rule = max(w, h)/max(min(w, h), RATIO_EPSILON) >= THRESHOLDS['rule_aspect']
    large = w >= THRESHOLDS['stamp_min_width_xh'] and h >= THRESHOLDS['stamp_min_height_xh']
    atypical = contrast is not None and contrast < THRESHOLDS['stamp_contrast_ratio']
    show = faint and letter_like and (off or blurred)
    stamp = off and (color or (row['entity_kind'] == 'residual_ink' and large and not rule and atypical))
    front = row['line_index'] is not None and row['ink_class'] != 'not_text' and contrast is not None and contrast >= THRESHOLDS['show_contrast_ratio'] and not show and not stamp
    return dict(contrast_ratio=contrast, edge_ratio=edge, front_text=bool(front),
                show_through_candidate=bool(show), stamp_watermark_candidate=bool(stamp),
                non_text=bool((row['line_index'] is None and not show and not stamp) or row['ink_class'] == 'not_text'),
                faint=bool(faint), blurred=bool(blurred), line_inconsistent=bool(off),
                letter_like=bool(letter_like), colored=bool(color), large_blob=bool(large), rule_like=bool(rule),
                mirrored=None)


def _summary(rows):
    bodies = [r for r in rows if r['entity_kind'] == 'letter_body']
    n = len(bodies)
    area = sum(r['ink_pixels'] for r in rows)
    states = Counter(r['coverage_state'] for r in bodies)
    candidates = {}
    for flag in ('front_text', 'show_through_candidate', 'stamp_watermark_candidate', 'non_text'):
        selected = [r for r in rows if r[flag]]
        pixels = sum(r['ink_pixels'] for r in selected)
        candidates[flag] = dict(rows=len(selected), ink_pixels=pixels, ink_share=_ratio(pixels, area))
    readable = [r for r in bodies if r['edge_ratio'] is not None]
    score = [float(r['coverage_state'] == 'intact')*r['contrast_local']*min(1., r['edge_ratio']) for r in readable]
    agreement = Counter(f"{r['legacy_coverage_state']}->{r['coverage_state']}" for r in bodies)
    matched = sum(r['legacy_coverage_state'] == r['coverage_state'] for r in bodies)
    measures = ('height_xh', 'body_height_xh', 'width_xh', 'stroke_width_xh', 'xheight_page_width',
                'darkness', 'contrast_absolute', 'contrast_local', 'contrast_ratio', 'edge_sharpness',
                'edge_ratio', 'fill', 'hole_fraction')
    return dict(rows=len(rows), letter_bodies=n, ink_pixels=area,
        entity_counts=dict(Counter(r['entity_kind'] for r in rows)),
        ink_classes=dict(Counter(r['ink_class'] for r in rows)),
        distributions={k: _distribution([r.get(k) for r in bodies]) for k in measures},
        font_groups=dict(Counter(r['font_group'] for r in bodies)),
        coverage_counts={s: states[s] for s in ('under_inked', 'over_inked', 'intact')},
        coverage_shares={s: _ratio(states[s], n) for s in ('under_inked', 'over_inked', 'intact')},
        candidates=candidates, unresolved_merged=sum(not r['resolved'] for r in bodies),
        legacy_agreement=dict(compared=n, matched=matched, fraction=_ratio(matched, n), confusion=dict(agreement)),
        readability_proxy=100*float(np.mean(score)) if score else None,
        readability_support=len(score), readability_factors=dict(
            intact_share=_ratio(states['intact'], n),
            mean_local_contrast=_mean([r['contrast_local'] for r in readable]),
            mean_edge_factor=_mean([min(1., r['edge_ratio']) for r in readable])))


def _mean(values):
    return float(np.mean(values)) if values else None


def _aggregates(rows, lines, structure):
    result = {}
    # The same ordered rows often form both a printed line and a row, or a
    # single column and page side. All provenance is fixed before this call.
    summaries = {}
    def summary(value):
        key = tuple(map(id, value))
        if key not in summaries:
            summaries[key] = _summary(value)
        return deepcopy(summaries[key])
    specifications = dict(lines=('line_index',), rows=('page_side', 'column_id', 'row_id'),
                          columns=('page_side', 'column_id'), page_sides=('page_side',))
    for name, keys in specifications.items():
        groups = defaultdict(list)
        for row in rows:
            if row[keys[-1]] is not None:
                groups[tuple(row[k] for k in keys)].append(row)
        # Include active Q1 groups with no measurable ink, so absence is visible.
        for index, line in enumerate(lines):
            if not line.get('discounted'):
                address = dict(line, line_index=index)
                groups.setdefault(tuple(address[k] for k in keys), [])
        if name == 'page_sides':
            for side in (structure or {}).get('pages', []):
                groups.setdefault((side['page_side'],), [])
        result[name] = [dict(address=dict(zip(keys, key)), **summary(value))
                        for key, value in sorted(groups.items(), key=lambda kv: str(kv[0]))]
        nearby = defaultdict(list)
        for row in rows:
            if row['line_index'] is not None:
                continue
            if name == 'columns':
                key = (row['page_side'], row['spatial_column_id'])
            elif name in ('lines', 'rows') and row['nearest_line_index'] is not None:
                index = row['nearest_line_index']
                address = dict(lines[index], line_index=index)
                key = tuple(address[k] for k in keys)
            else:
                continue
            nearby[key].append(row)
        for group in result[name]:
            key = tuple(group['address'][k] for k in keys)
            if name != 'page_sides':
                group['nearby_unassigned_ink'] = summary(nearby[key])
    return result


def _side(box, structure):
    cx, cy = (box[0]+box[2])/2, (box[1]+box[3])/2
    for side in (structure or {}).get('pages', []):
        polygon = np.asarray(side['polygon'], np.float32)
        if cv2.pointPolygonTest(polygon, (float(cx), float(cy)), False) >= 0:
            return side['page_side']
    return 'single' if not structure else None


def _spatial_column(box, side, structure):
    """Spatial membership is evidence, not an invented printed-line address."""
    cx, cy = (box[0]+box[2])/2, (box[1]+box[3])/2
    matches = []
    for column in (structure or {}).get('columns', []):
        if column['page_side'] != side:
            continue
        bounds = []
        for name in ('left_boundary', 'right_boundary'):
            path = np.asarray(column[name]['path'], float)
            path = path[np.argsort(path[:, 1])]
            if not path[0, 1] <= cy <= path[-1, 1]:
                break
            bounds.append(float(np.interp(cy, path[:, 1], path[:, 0])))
        if len(bounds) == 2 and bounds[0] <= cx < bounds[1]:
            matches.append(column['id'])
    return matches[0] if len(matches) == 1 else None


def _residual_paper(gray, xh):
    step = max(1, round(THRESHOLDS['residual_paper_grid_xh']*xh))
    h, w = gray.shape
    ys, xs = np.arange(0, h, step), np.arange(0, w, step)
    levels = np.array([[np.percentile(gray[y:min(y+step, h), x:min(x+step, w)], 90)
                        for x in xs] for y in ys], dtype=np.float32)
    return cv2.resize(levels, (w, h), interpolation=cv2.INTER_LINEAR)


def _line_rows(gray, rgb, line, index, page_key, book_id, page_paper, owned):
    xh = line['xheight']
    a, b = int(line['x0']), int(line['x1'])
    t = max(0, int(np.floor(min(line['top']))))
    d = min(gray.shape[0], int(np.ceil(max(line['bottom'])))+1)
    if b <= a or d <= t:
        return []
    # Original component stroke/hole descriptors are unused: final entity
    # masks are measured independently below after ownership and mark joins.
    g = _line_geometry(gray[t:d, a:b], xh_prior=xh,
                    focus=(float(np.median(line['baseline']))-t-FIT_FOCUS_XH*xh,
                           float(np.median(line['baseline']))-t+FIT_FOCUS_XH*xh))
    top, base = np.asarray(line['meanline'])-t, np.asarray(line['baseline'])-t
    g.band = Band(top, base, xh, int(line.get('support', 0)), xh_source='Q1')
    yy = np.arange(t, d)[:, None]
    keep = (yy >= np.asarray(line['top'])[None, :]) & (yy < np.asarray(line['bottom'])[None, :])
    g.ink &= keep & ~owned[t:d, a:b]
    g.labels = np.where(g.ink, g.labels, 0)
    # Re-evaluate eligibility against the supplied band, without refitting Q1.
    components = []
    for c in g.components:
        sub = g.labels[c.y0:c.y1, c.x0:c.x1] == c.index
        if not sub.any():
            continue
        cx = min(max(int(c.cx), 0), len(base)-1)
        overlap = max(0., min(c.y1, base[cx])-max(c.y0, top[cx]))/max(1., min(c.h, xh))
        role = c.role
        if c.role == 'rule':
            role = 'rule'
        elif c.h > COMPONENT_MAX_HEIGHT_XH*xh or c.w > COMPONENT_MAX_WIDTH_XH*xh:
            role = 'large'
        elif overlap >= BODY_MIN_OVERLAP and c.h >= BODY_MIN_HEIGHT_XH*xh:
            role = 'letter'
        elif c.y1 < top[cx] or c.y0 >= base[cx]:
            role = 'mark'
        elif role in ('neighbour', 'mark'):
            role = 'fragment'
        components.append(replace(c, role=role))
    g.components = components
    boxes = letter_boxes(g)
    profile = ink_profile(g, boxes)
    masks = []
    taken = np.zeros(g.ink.shape, bool)
    for box in boxes:
        m = np.zeros(g.ink.shape, bool)
        m[box.y0:box.y1, box.x0:box.x1] = np.isin(
            g.labels[box.y0:box.y1, box.x0:box.x1], box.components)
        masks.append(m)
        taken |= m
    marks = [[] for _ in boxes]
    leftovers = []
    for c in components:
        sl = np.s_[c.y0:c.y1, c.x0:c.x1]
        m = (g.labels[sl] == c.index) & ~taken[sl]
        if not m.any() or c.role in ('rule', 'large'):
            continue
        options = []
        bs = float(np.interp(c.cx, np.arange(len(base)), base))
        kind = 'mark_above' if c.y1 < bs-UPPER_MARK_OFFSET_XH*xh else ('mark_below' if c.y0 >= bs-LOWER_MARK_OFFSET_XH*xh else None)
        for j, body in enumerate(boxes):
            dx = max(c.x0-body.x1, body.x0-c.x1, 0)
            dy = max(c.y0-body.y1, body.y0-c.y1, 0)
            if kind and c.h < ATTACHED_MARK_MAX_HEIGHT_XH*xh and dx <= THRESHOLDS['mark_dx_xh']*xh and dy < THRESHOLDS['mark_dy_xh']*xh:
                options.append((2*dx+dy, j, kind))
        if options:
            _, j, kind = min(options)
            masks[j][sl] |= m
            taken[sl] |= m
            marks[j].append(dict(ink_class=kind, box=[a+c.x0, t+c.y0, a+c.x1, t+c.y1],
                                 component_id=c.index, ink_pixels=int(m.sum())))
        else:
            # Keep punctuation/marks on the established envelope; larger and
            # off-band ink goes through the page residual pass, without an address.
            cx = min(max(int(c.cx), 0), len(base)-1)
            if c.h <= LOOSE_MARK_MAX_HEIGHT_XH*xh and top[cx]-LOOSE_MARK_TOP_REACH_XH*xh <= (c.y0+c.y1)/2 <= base[cx]+LOOSE_MARK_BOTTOM_REACH_XH*xh:
                full = np.zeros(g.ink.shape, bool)
                full[sl] = m
                leftovers.append((full, 'orphan_mark' if c.role == 'mark' else 'punctuation', c))
    rows = []
    entries = [(m, 'letter_body', j) for j, m in enumerate(masks)] + leftovers
    for m, entity, source in entries:
        # The body/mark boxes bound all set pixels. Avoid scanning a complete
        # line-sized mask again for each glyph; retain row-major pixel order.
        bounds = boxes[source] if entity == 'letter_body' else source
        left, top_edge, right, bottom_edge = bounds.x0, bounds.y0, bounds.x1, bounds.y1
        if entity == 'letter_body':
            for mark in marks[source]:
                ma, mt, mb, md = mark['box']
                left, top_edge = min(left, ma-a), min(top_edge, mt-t)
                right, bottom_edge = max(right, mb-a), max(bottom_edge, md-t)
        ys, xs = np.nonzero(m[top_edge:bottom_edge, left:right])
        ys, xs = ys+top_edge, xs+left
        if not len(xs):
            continue
        box = [a+int(xs.min()), t+int(ys.min()), a+int(xs.max())+1, t+int(ys.max())+1]
        local = m[ys.min():ys.max()+1, xs.min():xs.max()+1]
        own = owned[box[1]:box[3], box[0]:box[2]]
        local = local & ~own
        if not local.any():
            continue
        own |= local
        row = dict(page_key=page_key, book_id=book_id, line_index=index,
            line_id=f'{page_key}:line-{index:05d}', page_side=line['page_side'],
            column_id=line['column_id'], spatial_column_id=line['column_id'], row_id=line['row_id'], block_id=line.get('block_id'),
            piece_index=line.get('piece_index'), box=box, entity_kind=entity,
            xheight_px=xh, xheight_page_width=xh/gray.shape[1], xheight_source='Q1_line',
            nearest_line_index=index, attached_marks=[], body_height_xh=None, body_width_xh=None,
            coverage_state=None, legacy_state=None, legacy_coverage_state=None, legacy_score=None,
            legacy_contrast_ratio=None, pieces=None, merged=None, resolved=True,
            rise_xh=None, depth_xh=None, thickened=False, stroke_ratio_line=None)
        row.update(_measure(gray, rgb, box, local, xh, page_paper))
        if entity == 'letter_body':
            body, ink = boxes[source], profile.letters[source]
            body_box = [a+body.x0, t+body.y0, a+body.x1, t+body.y1]
            bs = _curve(line, 'baseline', (body_box[0]+body_box[2])/2)
            kind, rise, depth = _body_class(body_box, bs, xh)
            legacy = {'broken': 'under_inked', 'faint': 'under_inked', 'merged': 'over_inked', 'intact': 'intact'}[ink.state]
            row.update(body_box=body_box, body_height_xh=(body.y1-body.y0)/xh,
                body_width_xh=(body.x1-body.x0)/xh, ink_class=kind, rise_xh=rise, depth_xh=depth,
                line_residual_xh=_line_residual(body_box, line), attached_marks=marks[source],
                legacy_state=ink.state, legacy_coverage_state=legacy, coverage_state=legacy,
                legacy_score=ink.score, legacy_contrast_ratio=ink.contrast,
                pieces=body.pieces, merged=body.merged, resolved=body.resolved)
        else:
            bs = _curve(line, 'baseline', (box[0]+box[2])/2)
            row.update(body_box=None, line_residual_xh=_line_residual(box, line),
                       ink_class=('mark_above' if box[3] < bs-UPPER_MARK_OFFSET_XH*xh else 'mark_below')
                       if entity == 'orphan_mark' else 'punctuation')
        rows.append(row)
    typical = _median([r['stroke_width_xh'] for r in rows if r['entity_kind'] == 'letter_body'])
    for r in rows:
        r['stroke_ratio_line'] = _ratio(r['stroke_width_xh'], typical)
        thick = r['stroke_ratio_line'] is not None and r['stroke_ratio_line'] >= THRESHOLDS['thick_stroke_ratio'] and r['fill'] >= THRESHOLDS['thick_fill']
        r['thickened'] = bool(thick)
        if r['coverage_state'] == 'intact' and thick:
            r['coverage_state'] = 'over_inked'
    return rows


def page_statistics(image: Image.Image | np.ndarray, lines: Sequence[dict[str, Any]], *,
                    page_key: str, book_id: str | None = None,
                    structure: dict[str, Any] | None = None) -> dict[str, Any]:
    """Measure a page using Q1 line records, returning `glyphs` and JSON-ready `stats`; inputs are never mutated."""
    gray = _gray(image)
    h, w = gray.shape
    source_array = np.asarray(image)
    rgb = source_array[:, :, :3] if source_array.ndim == 3 and source_array.shape[2] >= 3 else None
    if rgb is not None and rgb.max() <= 1:
        rgb = rgb*255
    active = [(i, l) for i, l in enumerate(lines) if not l.get('discounted')]
    for _, line in active:
        for k in ('page_side', 'column_id', 'row_id'):
            if k not in line:
                raise ValueError(f'Q1 address missing {k}')
        a, b, xh = line['x0'], line['x1'], line['xheight']
        if not 0 <= a < b <= w or not np.isfinite(xh) or xh <= 0:
            raise ValueError('Invalid Q1 extent or x-height')
        for k in ('top', 'bottom', 'meanline', 'baseline', 'font_top', 'font_bottom'):
            if len(line[k]) != b-a or not np.isfinite(line[k]).all():
                raise ValueError(f'Invalid Q1 curve {k}')
    xh = float(np.median([l['xheight'] for _, l in active])) if active else max(1., min(h, w)/FALLBACK_XHEIGHT_PAGE_DIVISOR)
    paper = float(np.percentile(gray, 90))
    owned = np.zeros(gray.shape, bool)
    rows = []
    for i, line in active:
        rows.extend(_line_rows(gray, rgb, line, i, page_key, book_id, paper, owned))
    reference = _reference(rows)
    # A photometric residual pass includes ink that Q1 legitimately discounted.
    paper_map = _residual_paper(gray, xh)
    samples = gray[::max(1, round(xh)), ::max(1, round(xh))].ravel()
    bright = samples[samples >= np.percentile(samples, 75)]
    sigma = float(NORMAL_MAD_SCALE*np.median(abs(bright-np.median(bright))))
    delta = max(THRESHOLDS['residual_min_gray'], THRESHOLDS['residual_noise_sigma']*sigma,
                THRESHOLDS['residual_contrast_fraction']*(reference['contrast_absolute'] or 0)*255)
    halo = max(1, round(THRESHOLDS['owned_halo_xh']*xh))
    occupied = cv2.dilate(owned.astype(np.uint8), np.ones((2*halo+1, 2*halo+1), np.uint8)).astype(bool)
    residual = (gray < paper_map-delta) & ~occupied
    labels, _ = ndi.label(residual, structure=EIGHT)
    # Spatial nearest-line evidence does not become an address.
    points, point_lines = [], []
    for i, line in active:
        for x in range(line['x0'], line['x1'], max(1, round(line['xheight']))):
            points.append((x, _curve(line, 'baseline', x)-line['xheight']/2))
            point_lines.append(i)
    tree = cKDTree(points) if points else None
    dropped_pixels = 0
    for ci, sl in enumerate(ndi.find_objects(labels), 1):
        if sl is None:
            continue
        mask = labels[sl] == ci
        if mask.sum() < THRESHOLDS['residual_area_xh2']*xh*xh:
            dropped_pixels += int(mask.sum())
            continue
        y, x = sl
        box = [x.start, y.start, x.stop, y.stop]
        near = point_lines[tree.query(((x.start+x.stop)/2, (y.start+y.stop)/2))[1]] if tree else None
        residual_value = _line_residual(box, lines[near]) if near is not None else None
        row = dict(page_key=page_key, book_id=book_id, line_index=None, line_id=None,
            page_side=_side(box, structure), column_id=None, row_id=None, block_id=None, piece_index=None,
            box=box, body_box=None, entity_kind='residual_ink', ink_class='not_text',
            xheight_px=xh, xheight_page_width=xh/w, xheight_source='page_median' if active else 'page_width_fallback',
            nearest_line_index=near, line_residual_xh=residual_value, attached_marks=[],
            body_height_xh=None, body_width_xh=None, rise_xh=None, depth_xh=None,
            coverage_state=None, legacy_state=None, legacy_coverage_state=None, legacy_score=None,
            legacy_contrast_ratio=None, pieces=None, merged=None, resolved=True, thickened=False,
            stroke_ratio_line=None)
        row['spatial_column_id'] = _spatial_column(box, row['page_side'], structure)
        row.update(_measure(gray, rgb, box, mask, xh, paper))
        rows.append(row)
    font_map, fonts = _size_groups([(i, l['xheight']/w) for i, l in active])
    weights = Counter(font_map[r['line_index']] for r in rows if r['entity_kind'] == 'letter_body')
    dominant = sorted(weights, key=lambda k: (-weights[k], k))[0] if weights else None
    for font in fonts:
        font['letter_bodies'] = weights[font['id']]
        font['role'] = 'body' if font['id'] == dominant else ('smaller' if dominant and font['id'] < dominant else 'larger')
    for i, row in enumerate(rows):
        row['glyph_id'] = f'{page_key}:glyph-{i:06d}'
        row['font_group'] = font_map.get(row['line_index'])
        row['font_role'] = next((f['role'] for f in fonts if f['id'] == row['font_group']), None)
        row.update(_provenance(row, reference))
    stats = dict(schema_version=SCHEMA_VERSION, page_key=page_key, book_id=book_id,
        image_size=[w, h], units='source pixels; sizes also in Q1 x-heights',
        geometry_sha256=hashlib.sha256(json.dumps(list(lines), sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
        thresholds=dict(THRESHOLDS), reference=reference, font_groups=fonts,
        active_lines=len(active), discounted_lines=len(lines)-len(active),
        residual_detection=dict(noise_sigma_gray=sigma, minimum_contrast_gray=delta, reference_xheight_px=xh,
            small_component_pixels_excluded=dropped_pixels, owned_ink_pixels=int(owned.sum()),
            detected_residual_pixels=int(residual.sum()), halo_xh=THRESHOLDS['owned_halo_xh']),
        summary=_summary(rows), **_aggregates(rows, lines, structure))
    return dict(glyphs=rows, stats=stats)


def _stability(values):
    d = _distribution(values)
    return dict(**d, cv=_ratio(d['std'], d['mean']) if d['n'] >= 2 else None,
                relative_p90_p10=_ratio(d['p90']-d['p10'], d['median']) if d['n'] >= 2 else None)


def book_statistics(pages: Sequence[dict[str, Any]], *, book_id: str) -> dict[str, Any]:
    """Return book aggregates and copied page tables enriched with independent, leave-one-page-out references."""
    keys = [p['stats']['page_key'] for p in pages]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate pages would bias book statistics')
    if any(p['stats']['book_id'] != book_id for p in pages):
        raise ValueError('Book identity mismatch')
    values = [(r['glyph_id'], r['xheight_page_width']) for p in pages for r in p['glyphs'] if r['entity_kind'] == 'letter_body']
    font_map, fonts = _size_groups(values)
    dominant = max(fonts, key=lambda f: f['members'])['id'] if fonts else None
    for font in fonts:
        font['letter_bodies'] = font['members']
        font['role'] = 'body' if font['id'] == dominant else ('smaller' if font['id'] < dominant else 'larger')
    font_roles = {f['id']: f['role'] for f in fonts}
    enriched = []
    for page in pages:
        key = page['stats']['page_key']
        others = [p['stats'] for p in pages if p['stats']['page_key'] != key and p['stats']['reference']['support'] > 0]
        reference = {name: _median([p['reference'][name] for p in others]) for name in ('contrast_absolute', 'edge_sharpness', 'stroke_width_xh')}
        reference.update(method='leave-one-page-out-median-of-pages', pages=[p['page_key'] for p in others], support_pages=len(others))
        rows = []
        for original in page['glyphs']:
            row = dict(original)
            evidence = _provenance(row, reference)
            row['book_font_group'] = font_map.get(row['glyph_id'])
            row['book_font_role'] = font_roles.get(row['book_font_group'])
            for name, val in evidence.items():
                row[f'book_{name}'] = val if others else None
            rows.append(row)
        stats = dict(page['stats'], book_reference=reference)
        stats['book_candidate_amounts'] = {
            flag: dict(rows=sum(r[f'book_{flag}'] is True for r in rows),
                       ink_pixels=sum(r['ink_pixels'] for r in rows if r[f'book_{flag}'] is True)) if others else None
            for flag in ('show_through_candidate', 'stamp_watermark_candidate')}
        enriched.append(dict(glyphs=rows, stats=stats))
    flat = [r for p in enriched for r in p['glyphs']]
    per_page = []
    for p in enriched:
        s, rr = p['stats'], p['glyphs']
        bodies = [r for r in rr if r['entity_kind'] == 'letter_body']
        weights = Counter(r['book_font_group'] for r in bodies)
        body_group = next((f for f in s['font_groups'] if f['role'] == 'body'), None)
        per_page.append(dict(page_key=s['page_key'], letter_bodies=len(bodies),
            body_size_page_width=body_group['size_page_width']['median'] if body_group else None,
            contrast=s['reference']['contrast_absolute'], sharpness=s['reference']['edge_sharpness'],
            darkness=s['summary']['distributions']['darkness']['median'],
            readability_proxy=s['summary']['readability_proxy'],
            **s['summary']['coverage_shares'],
            show_through_share=s['summary']['candidates']['show_through_candidate']['ink_share'],
            stamp_share=s['summary']['candidates']['stamp_watermark_candidate']['ink_share'],
            font_shares={f['id']: _ratio(weights[f['id']], len(bodies)) for f in fonts}))
    measures = ('body_size_page_width', 'contrast', 'sharpness', 'darkness', 'under_inked',
                'over_inked', 'intact', 'show_through_share', 'stamp_share', 'readability_proxy')
    summary = _summary(flat)
    summary['font_groups'] = dict(Counter(r['book_font_group'] for r in flat if r['entity_kind'] == 'letter_body'))
    summary['glyph_weighted_readability_proxy'] = summary['readability_proxy']
    summary['readability_proxy'] = _mean([p['readability_proxy'] for p in per_page if p['readability_proxy'] is not None])
    stats = dict(schema_version=SCHEMA_VERSION, book_id=book_id, pages=len(pages), page_keys=keys,
        thresholds=dict(THRESHOLDS), summary=summary, font_groups=fonts, per_page=per_page,
        stability={m: _stability([p[m] for p in per_page]) for m in measures},
        font_share_stability={f['id']: _stability([p['font_shares'][f['id']] for p in per_page]) for f in fonts})
    return dict(pages=enriched, stats=stats)


def corpus_statistics(pages: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Return the page summary table and explicitly page- and glyph-weighted descriptive readability scores."""
    table = []
    for page in pages:
        s = page.get('stats', page)
        v = s['summary']
        table.append(dict(page_key=s['page_key'], book_id=s['book_id'],
            letters=v['letter_bodies'], residual_rows=v['entity_counts'].get('residual_ink', 0),
            readability_proxy=v['readability_proxy'], readability_support=v['readability_support'],
            darkness=v['distributions']['darkness']['median'],
            **v['coverage_shares'],
            show_through_ink_share=v['candidates']['show_through_candidate']['ink_share'],
            stamp_ink_share=v['candidates']['stamp_watermark_candidate']['ink_share'],
            legacy_compared=v['legacy_agreement']['compared'], legacy_matched=v['legacy_agreement']['matched']))
    keys = [r['page_key'] for r in table]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate pages would bias corpus statistics')
    valid = [r for r in table if r['readability_proxy'] is not None]
    return dict(schema_version=SCHEMA_VERSION, pages=len(table), books=len(set(r['book_id'] for r in table if r['book_id'] is not None)),
        letter_bodies=sum(r['letters'] for r in table),
        readability_proxy=_mean([r['readability_proxy'] for r in valid]),
        glyph_weighted_readability_proxy=_ratio(sum(r['readability_proxy']*r['readability_support'] for r in valid), sum(r['readability_support'] for r in valid)),
        table=table)


def _write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n')


def write_statistics(result: dict[str, Any], directory: str | Path) -> dict[str, str]:
    """Write a page's glyph Parquet (JSONL without pyarrow) and stats JSON; never write Q1 geometry."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    key = result['stats']['page_key']
    if Path(key).name != key or key in ('', '.', '..'):
        raise ValueError('page_key must be a filename stem')
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        path = directory/f'{key}.glyphs.jsonl'
        path.write_text(''.join(json.dumps(r, ensure_ascii=False, allow_nan=False)+'\n' for r in result['glyphs']))
    else:
        path = directory/f'{key}.glyphs.parquet'
        # JSON for nested evidence makes the table usable across Arrow versions
        # and avoids null-only struct schemas on pages with no attached marks.
        string_fields = ('page_key book_id glyph_id line_id page_side column_id spatial_column_id row_id block_id '
                         'entity_kind ink_class xheight_source coverage_state legacy_state legacy_coverage_state '
                         'font_group font_role book_font_group book_font_role attached_marks').split()
        int_fields = 'line_index piece_index nearest_line_index ink_pixels holes hole_area pieces merged'.split()
        bool_fields = ('color_available resolved thickened front_text show_through_candidate stamp_watermark_candidate '
                       'non_text faint blurred line_inconsistent letter_like colored large_blob rule_like mirrored').split()
        float_fields = ('xheight_px xheight_page_width body_height_xh body_width_xh legacy_score legacy_contrast_ratio '
                        'rise_xh depth_xh stroke_ratio_line ink_gray darkness paper_gray contrast_absolute contrast_local '
                        'edge_sharpness color_spread height_xh width_xh stroke_width_px stroke_width_xh fill hole_fraction '
                        'line_residual_xh contrast_ratio edge_ratio book_contrast_ratio book_edge_ratio').split()
        book_bools = ['book_'+k for k in bool_fields if k not in ('color_available', 'resolved', 'thickened')]
        schema = pa.schema([(k, pa.string()) for k in string_fields] +
                           [(k, pa.int64()) for k in int_fields] +
                           [(k, pa.bool_()) for k in bool_fields+book_bools] +
                           [(k, pa.float64()) for k in float_fields] +
                           [(k, pa.list_(pa.int64())) for k in ('box', 'body_box')])
        records = [{**r, 'attached_marks': json.dumps(r['attached_marks'], ensure_ascii=False)} for r in result['glyphs']]
        unknown = set().union(*(r.keys() for r in records)) - set(schema.names) if records else set()
        if unknown:
            raise ValueError(f'Undeclared glyph fields: {sorted(unknown)}')
        table = pa.Table.from_pylist(records, schema=schema)
        metadata = dict(table.schema.metadata or {})
        metadata[b'greekocr.statistics'] = json.dumps(dict(schema_version=SCHEMA_VERSION, nested_json=['attached_marks'],
                                                          thresholds=THRESHOLDS)).encode()
        pq.write_table(table.replace_schema_metadata(metadata), path, compression='zstd')
    stats_path = directory/f'{key}.stats.json'
    _write_json(stats_path, dict(result['stats'], glyph_table=path.name))
    return dict(glyphs=str(path), stats=str(stats_path))


def render_glyph_statistics(image: Image.Image, result: dict[str, Any]) -> Image.Image:
    """Return a source-size glyph overlay: green intact, orange under, red over, cyan show-through, violet stamp."""
    canvas = image.convert('RGBA')
    overlay = Image.new('RGBA', canvas.size)
    draw = ImageDraw.Draw(overlay)
    colors = dict(intact=(0, 145, 70), under_inked=(240, 135, 0), over_inked=(220, 35, 35))
    for r in result['glyphs']:
        if r['coverage_state'] in colors:
            a, t, b, d = r['box']
            col = colors[r['coverage_state']]
            draw.rectangle((a, t, b-1, d-1), fill=col+(28,), outline=col+(200,), width=1)
        for flag, color in [('show_through_candidate', (0, 150, 230, 230)), ('stamp_watermark_candidate', (170, 40, 210, 240))]:
            if r[flag]:
                a, t, b, d = r['box']
                draw.rectangle((a, t, b-1, d-1), outline=color, width=2)
    rendered = Image.alpha_composite(canvas, overlay).convert('RGB')
    # Legend is outside the source image, so no printed ink is hidden.
    sheet = Image.new('RGB', (max(rendered.width, 680), rendered.height+38), 'white')
    sheet.paste(rendered, (0, 38))
    ImageDraw.Draw(sheet).text((8, 10), 'Intact: green | Under: orange | Over: red | Show-through candidate: cyan | Stamp candidate: violet', fill='black')
    return sheet


def render_book_statistics(stats: dict[str, Any]) -> Image.Image:
    """Draw per-page size, contrast, coverage, candidate ink and readability traces with explicit scales."""
    pages = stats['per_page']
    panels = [('Body xheight / page width', 'body_size_page_width'), ('Front contrast (0-1)', 'contrast'),
              ('Intact letter share (0-1)', 'intact'), ('Show-through ink share (0-1)', 'show_through_share'),
              ('Stamp candidate ink share (0-1)', 'stamp_share'), ('Readability proxy (0-100)', 'readability_proxy')]
    image = Image.new('RGB', (1200, 980), 'white')
    draw = ImageDraw.Draw(image)
    draw.text((20, 15), f"Book {stats['book_id']} | {len(pages)} pages | descriptive measurements, not OCR accuracy", fill='black')
    colors = [(20, 110, 190), (50, 130, 80), (180, 70, 30), (80, 90, 150)]
    for k, (title, field) in enumerate(panels):
        left, top = 70+(k % 2)*580, 70+(k//2)*245
        right, bottom = left+485, top+165
        vals = [p[field] for p in pages]
        finite = [v for v in vals if v is not None]
        ymax = 100 if field == 'readability_proxy' else (1 if field != 'body_size_page_width' else max(finite+[PLOT_MIN_BODY_SIZE_PAGE])*PLOT_HEADROOM)
        draw.text((left, top-25), title, fill='black')
        for frac in (0, .5, 1):
            y = bottom-frac*(bottom-top)
            draw.line((left, y, right, y), fill=(210, 210, 210))
            draw.text((left-55, y-5), f'{frac*ymax:.4g}', fill='black')
        pts = []
        for i, v in enumerate(vals):
            x = left+(right-left)*(i+.5)/max(1, len(pages))
            draw.text((x-5, bottom+8), str(i+1), fill='black')
            if v is not None:
                y = bottom-v/ymax*(bottom-top)
                pts.append((x, y))
                draw.ellipse((x-4, y-4, x+4, y+4), fill=colors[k % len(colors)])
        if len(pts) > 1:
            draw.line(pts, fill=colors[k % len(colors)], width=2)
    for i, p in enumerate(pages):
        draw.text((20+(i % 2)*590, 825+(i//2)*25), f"{i+1}: {p['page_key']}", fill='black')
    return image

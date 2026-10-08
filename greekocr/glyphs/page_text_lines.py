"""Pixels → rough segments → crop-tool fits → shared geometry → OCR strips.

See docs/PAGE_LINES_ALGORITHM.md. Text-layer boxes are optional provenance
hints only: supplying them cannot change detection or the geometry. The mature
crop fitter (including its end-bend scorer) remains the line evidence engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

from .baseline import text_lines
from .components import _xheight, line_glyphs
from .pixel_segments import PixelPage, _gray, _runs, prepare_pixels

__all__ = ['LineSegment', 'PageSegmentation', 'page_line_segments', 'segment_page', 'extract_line_image']

CURVES = ('baseline', 'font_top', 'meanline', 'font_bottom', 'top', 'bottom')


@dataclass
class LineSegment:
    """One printed line; all curves use page pixel coordinates, x1 exclusive."""
    x0: int
    x1: int
    baseline: NDArray[np.float64]
    font_top: NDArray[np.float64]
    meanline: NDArray[np.float64]
    font_bottom: NDArray[np.float64]
    top: NDArray[np.float64]
    bottom: NDArray[np.float64]
    xheight: float
    column: int = 0
    segment_indices: tuple[int, ...] = ()
    hint_indices: tuple[int, ...] = ()
    segment_positions: tuple[tuple[int, int, int], ...] = ()
    neighbours: dict = field(default_factory=dict)
    support: int = 0
    geometry_source: str = 'crop-pooled'
    component_ids: tuple[int, ...] = field(default=(), repr=False)

    def unroll(self, page: Image.Image | NDArray[Any], *, xheight: int = 32) -> Image.Image:
        """Return a grayscale strip with meanline at 1.5 and baseline at 2.5 x-heights."""
        return extract_line_image(page, self, xheight=xheight)

    def to_record(self) -> dict:
        """JSON-ready review record, including the once-built neighbour graph."""
        row = {k: np.round(getattr(self, k), 3).tolist() for k in CURVES}
        row.update(x0=self.x0, x1=self.x1, xheight=self.xheight, column=self.column,
                   segment_indices=list(self.segment_indices), hint_indices=list(self.hint_indices),
                   segment_positions=[list(p) for p in self.segment_positions], support=self.support,
                   geometry_source=self.geometry_source,
                   neighbours={k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in self.neighbours.items()})
        return row


@dataclass
class PageSegmentation:
    """Final lines and their pixel-segment provenance, with measurable diagnostics."""
    lines: list[LineSegment]
    segments: list[tuple[int, int, int, int]]
    xheight: float
    diagnostics: dict
    pixels: PixelPage = field(repr=False)


def _blocked(p: PixelPage, x0, x1, base, xh):
    a, b = max(0, int(x0)), min(p.gray.shape[1], int(x1))
    if b <= a:
        return False
    x = np.arange(a, b)
    y = np.broadcast_to(base, (len(x),)) - .5 * xh
    for dy in (-.45 * xh, 0, .45 * xh):
        rows = np.clip(np.rint(y + dy).astype(int), 0, p.gray.shape[0] - 1)
        if p.barriers[rows, x].any():
            return True
    for l, t, r, bot in p.gutters:
        if a < r and b > l and t <= np.median(y) < bot:
            return True
    return False


def _discover(p: PixelPage):
    """Peel all main bands in each rough region using the existing crop tools."""
    cc = p.components
    h, w = p.gray.shape
    models = []
    for si, (a, t, b, bot) in enumerate(p.boxes):
        t0, t1 = max(0, int(t - 1.5 * p.xheight)), min(h, int(bot + 1.5 * p.xheight))
        paper = float(np.percentile(p.gray[t0:t1, a:b], 90))
        local = cc[(cc[:, 0] >= a) & (cc[:, 2] <= b) & (cc[:, 1] >= t) & (cc[:, 3] <= bot)]
        useful = local[(local[:, 4] > .08 * p.xheight ** 2) & (local[:, 3] - local[:, 1] > .45 * p.xheight)]
        # Preserve the crop tools' photometry: replacing grey paper with white
        # makes bleed-through look like strong print. Freeze a local contrast
        # reference before peeling, so leftovers cannot promote themselves to
        # new lines when the main text has been removed. Faint ink remains in
        # the page component map and can attach to the established paths later.
        ink_level = float(np.percentile(useful[:, 6], 35)) if len(useful) else paper
        strong_ids = cc[cc[:, 6] <= paper - .45 * (paper - ink_level), 5]
        mask = p.ink[t0:t1, a:b] & np.isin(p.labels[t0:t1, a:b], strong_ids)
        sub = np.where(mask, p.gray[t0:t1, a:b], paper)
        xh = p.xheight
        if len(useful) >= 3:
            measured = _xheight(useful[:, 3] - useful[:, 1])
            if .65 * xh <= measured <= 3 * xh:
                xh = measured
        if b - a < 3 * xh and len(useful):
            # A one/two-character cell cannot determine orientation. Keep its
            # baseline contacts, and defer its shape to the shared page fit.
            groups = []
            for q in sorted(useful, key=lambda q: q[3]):
                if not groups or q[3] - groups[-1][-1][3] > .75 * xh:
                    groups.append([])
                groups[-1].append(q)
            for group in groups:
                q = np.array(group)
                base = float(np.median(q[:, 3]))
                ids = set(q[:, 5].astype(int))
                models.append(dict(a=a, b=b, base=np.full(b - a, base), xh=xh,
                                   up=1.5 * xh, down=.5 * xh, ids=ids,
                                   body_ids=ids.copy(), segments={si},
                                   support=np.column_stack(((q[:, 0] + q[:, 2]) / 2, q[:, 3])),
                                   cy=base - xh / 2, column=0))
            continue
        for _ in range(max(2, int((t1 - t0) / (.8 * xh)) + 1)):
            if (sub < paper - 1).sum() < .12 * xh * xh:
                break
            profile = ndi.uniform_filter1d((sub < paper - 1).sum(axis=1).astype(float), max(1, round(.5 * xh)))
            peak = float(np.argmax(profile)) + .4 * xh
            g = line_glyphs(sub, xh_prior=xh, focus=(peak - .7 * xh, peak + .7 * xh))
            guides = text_lines(g)
            body = [c for c in g.components if c.role == 'letter' and c.h >= .45 * xh
                    and c.area >= .065 * xh * xh and c.w <= 6 * xh]
            if not body:
                break
            own = []
            for c in g.components:
                base = g.band.bottom[int(np.clip(c.cx, 0, g.width - 1))]
                near = abs((c.y0 + c.y1) / 2 - (base - xh / 2))
                if c.h <= 2.6 * xh and c.w <= 8 * xh and near < (.85 if c.h >= .5 * xh else 1.2) * xh:
                    own.append(c)
            ids, body_ids = set(), set()
            for c in own:
                sl = np.s_[c.y0:c.y1, c.x0:c.x1]
                labs = p.labels[t0 + c.y0:t0 + c.y1, a + c.x0:a + c.x1][g.labels[sl] == c.index]
                ids.update(int(k) for k in np.unique(labs) if k)
                if c in body:
                    body_ids.update(int(k) for k in np.unique(labs) if k)
                sub[sl][g.labels[sl] == c.index] = paper
            if not body_ids:
                continue
            q = cc[np.isin(cc[:, 5], list(body_ids))]
            cy = float(np.median((q[:, 1] + q[:, 3]) / 2))
            # Expanded windows see neighbours too. Only seed-owned bands enter
            # here; all surviving neighbouring pixels remain for their seed.
            if not t - .3 * xh <= cy < bot + .3 * xh:
                continue
            support = np.array([(a + x, t0 + y) for x, y, _ in g.band.support], float).reshape(-1, 2)
            guide = guides[0]
            qa, qb = max(a, int(q[:, 0].min())), min(b, int(q[:, 2].max()))
            models.append(dict(a=qa, b=qb, base=g.band.bottom[qa - a:qb - a] + t0, xh=xh,
                               up=float(np.median(guide.base - guide.ascender)),
                               down=float(np.median(guide.descender - guide.base)),
                               ids=ids, body_ids=body_ids, segments={si}, support=support,
                               cy=cy, column=0))
    return models


def _reject_residual_bands(models):
    """A few leftover ascenders cannot invent another line beside a full one.

    A short cell/last line is retained at its own vertical level. Unlike a
    minimum line width, this test does not reject legitimate short text.
    """
    strong = [m for m in models if len(m['support']) >= 8 and len(m['body_ids']) >= 4]
    out = []
    for m in models:
        if not len(m['support']) and m['b'] - m['a'] > 4 * m['xh']:
            continue
        if strong:
            conflict = False
            for n in strong:
                if n is m or len(m['support']) >= .4 * len(n['support']):
                    continue
                a, b = max(m['a'], n['a']), min(m['b'], n['b'])
                if b <= a:
                    continue
                grid = np.linspace(a, b - 1, 5)
                delta = np.median(abs(_at(m, grid) - _at(n, grid)))
                if delta < 1.6 * min(m['xh'], n['xh']):
                    conflict = True; break
            if conflict:
                continue
        out.append(m)
    return out


def _at(m, xs):
    xs = np.asarray(xs)
    grid = np.arange(m['a'], m['b'])
    out = np.interp(xs, grid, m['base'])
    if len(grid) > 1:
        n = min(len(grid), max(2, round(3 * m['xh'])))
        sl = np.clip((m['base'][n - 1] - m['base'][0]) / (n - 1), -.3, .3)
        sr = np.clip((m['base'][-1] - m['base'][-n]) / (n - 1), -.3, .3)
        out = np.where(xs < grid[0], m['base'][0] + sl * (xs - grid[0]), out)
        out = np.where(xs > grid[-1], m['base'][-1] + sr * (xs - grid[-1]), out)
    return out


def _merge(p, models):
    """Duplicate seeds and aligned pieces unite, up to a REAL column stop."""
    models.sort(key=lambda m: (m['cy'], m['a']))
    out = []
    for m in models:
        target = None
        for n in out:
            xh = min(m['xh'], n['xh'])
            overlap = min(m['b'], n['b']) - max(m['a'], n['a'])
            shared = len(m['body_ids'] & n['body_ids']) / max(1, min(len(m['body_ids']), len(n['body_ids'])))
            if shared > .4:
                target = n; break
            if abs(m['cy'] - n['cy']) > 5 * xh or overlap < -10 * xh:
                continue
            if overlap > 0:
                # Do not unite two fitted columns simply because one seed was
                # wide: the baseline agreement must hold without a rule.
                mid = np.arange(max(m['a'], n['a']), min(m['b'], n['b']))
                if _blocked(p, mid[0], mid[-1] + 1, _at(m, mid), xh):
                    continue
                xs = np.linspace(max(m['a'], n['a']), min(m['b'], n['b']) - 1, 5)
            else:
                xs = np.array([(max(m['a'], n['a']) + min(m['b'], n['b'])) / 2])
            if np.max(np.abs(_at(m, xs) - _at(n, xs))) > .45 * xh:
                continue
            a, b = min(m['b'], n['b']), max(m['a'], n['a'])
            if b > a and _blocked(p, a, b, _at(m, np.arange(a, b)), xh):
                continue
            target = n; break
        if target is None:
            out.append(m)
            continue
        n = target
        n['ids'] |= m['ids']; n['body_ids'] |= m['body_ids']; n['segments'] |= m['segments']
        # Select the tested curve with the strongest support, rather than
        # fitting a new letter grouping to the fragments.
        best = m if len(m['support']) > len(n['support']) else n
        a, b = min(n['a'], m['a']), max(n['b'], m['b'])
        base = _at(best, np.arange(a, b))
        n['support'] = np.unique(np.vstack((n['support'], m['support'])), axis=0)
        n['a'], n['b'], n['base'] = a, b, base
        n['cy'] = float(np.median(base) - n['xh'] / 2)
    return out


def _lanes(models):
    """Column addresses by substantial overlap, without a narrow-cell merge."""
    spans = []
    for m in sorted(models, key=lambda m: (m['a'], -m['b'])):
        a, b = m['a'], m['b']
        found = None
        for k, (l, r) in enumerate(spans):
            if min(r, b) - max(l, a) > .55 * min(r - l, b - a):
                found = k; break
        if found is None:
            found = len(spans); spans.append((a, b))
        m['column'] = found


def _pool_geometry(models):
    """Local shared column warp + per-line vertical shift; sparse cells borrow."""
    reliable = [m for m in models if len(m['support']) >= 8 and m['b'] - m['a'] >= 8 * m['xh']]
    slopes = [np.median(np.diff(m['base'])) for m in reliable]
    page_slope = float(np.median(slopes)) if slopes else 0.
    new = []
    for m in models:
        grid = np.arange(m['a'], m['b'])
        anchor = float(np.median(m['support'][:, 0])) if len(m['support']) else (m['a'] + m['b']) / 2
        nearby = [n for n in reliable if n['column'] == m['column'] and abs(n['cy'] - m['cy']) < 14 * m['xh']]
        if not nearby:
            nearby = sorted([n for n in reliable if n['column'] == m['column']], key=lambda n: abs(n['cy'] - m['cy']))[:4]
        if nearby:
            # Alternating offsets align all baseline contacts to one curve.
            # Only contacts agreed with by the crop fit enter this shared fit.
            px, py, pypos = [], [], []
            for n in nearby:
                s = n['support']
                ok = abs(s[:, 1] - _at(n, s[:, 0])) < .3 * n['xh']
                px.extend(s[ok, 0] - m['a'])
                py.extend(s[ok, 1] - float(_at(n, anchor)))
                pypos.extend(np.full(ok.sum(), (n['cy'] - m['cy']) / m['xh']))
            if len(px) >= 4:
                # A local linear surface in page y allows gradual skew drift.
                # It still pools the letters; it does not fit sparse cells.
                px, py, pypos = np.array(px), np.array(py), np.array(pypos)
                knots = np.linspace(0, len(grid) - 1, max(2, int(len(grid) / m['xh']) + 1))
                values = []
                for gx in knots:
                    dx = (px - gx) / m['xh']
                    weight = np.clip(1 - (abs(dx) / 6) ** 3, 0, None) ** 3 * np.exp(-.5 * (pypos / 8) ** 2)
                    if (weight > .01).sum() < 4:
                        near = np.argsort(abs(dx))[:8]
                        weight = np.zeros_like(px); weight[near] = 1
                    design = np.column_stack((np.ones_like(dx), dx, pypos, dx * pypos))
                    ridge = np.diag([1e-8, .02, .2, .2])
                    coef = np.linalg.solve(design.T @ (design * weight[:, None]) + ridge,
                                           design.T @ (weight * py))
                    values.append(coef[0])
                shape = np.interp(np.arange(len(grid)), knots, values)
            else:
                shape = page_slope * (grid - anchor)
        else:
            # The short row-number column may have no long line at all.
            peers = sorted(reliable, key=lambda n: abs(n['cy'] - m['cy']))[:6]
            slope = float(np.median([np.median(np.diff(n['base'])) for n in peers])) if peers else page_slope
            shape = slope * (grid - anchor)
        s = m['support']
        shift = float(np.median(s[:, 1] - np.interp(s[:, 0], grid, shape))) if len(s) else float(np.median(m['base'] - shape))
        new.append(shape + shift)
    for m, base in zip(models, new):
        m['base'] = base


def _assign(p, models):
    """Follow the final paths through ALL text pixels, independent of seed boxes."""
    assigned = np.full(len(p.components), -1, int)
    # Components are never assigned by text-layer text or its rectangles.
    for qi, q in enumerate(p.components):
        a, t, b, bot, area = q[:5]
        cx, cy = (a + b) / 2, (t + bot) / 2
        best = None
        for j, m in enumerate(models):
            xh = m['xh']
            gap = max(m['a'] - b, a - m['b'], 0)
            small = bot - t < .55 * xh or area < .08 * xh * xh
            if small and gap > xh:
                continue
            if gap > 10 * xh or abs(cy - m['cy']) > 6 * xh or bot - t > 3.2 * xh or b - a > 12 * xh:
                continue
            base = float(_at(m, cx))
            distance = abs(cy - (base - xh / 2))
            if distance > 1.25 * xh:
                continue
            # A body must actually enter the mean-to-baseline band. Small marks
            # attach by proximity; they cannot invent a baseline of their own.
            if bot - t >= .6 * xh and min(bot, base + .2 * xh) - max(t, base - 1.1 * xh) < .25 * xh:
                continue
            if gap and _blocked(p, min(cx, np.clip(cx, m['a'], m['b'] - 1)),
                                max(cx, np.clip(cx, m['a'], m['b'] - 1)) + 1,
                                base, xh):
                continue
            score = distance / xh + .025 * gap / xh
            # Retain detached marks from the tested crop classifier on ties.
            if int(q[5]) in m['ids']:
                score -= .12
            if best is None or score < best[0]:
                best = (score, j)
        if best is not None:
            assigned[qi] = best[1]
    # Detached accents/subscripts follow the nearest physical letter, not the
    # nearest line centre. The latter sends high accents to the previous line.
    q = p.components
    body = np.flatnonzero((q[:, 3] - q[:, 1] >= .55 * p.xheight)
                         & (q[:, 4] >= .08 * p.xheight ** 2) & (assigned >= 0))
    if len(body):
        centres = (q[:, :2] + q[:, 2:4]) / 2
        tree = cKDTree(centres[body])
        for k in np.flatnonzero(q[:, 3] - q[:, 1] < .55 * p.xheight):
            _, near = tree.query(centres[k], k=min(12, len(body)))
            options = []
            for n in body[np.atleast_1d(near)]:
                j = assigned[n]; xh = models[j]['xh']
                dx = max(q[k, 0] - q[n, 2], q[n, 0] - q[k, 2], 0)
                dy = max(q[k, 1] - q[n, 3], q[n, 1] - q[k, 3], 0)
                if dx <= .3 * xh and dy <= .6 * xh:
                    options.append((2 * dx + dy, int(j)))
            if options:
                assigned[k] = min(options)[1]
    return [np.flatnonzero(assigned == j).tolist() for j in range(len(models))]


def _make_lines(p, models, owners, hints):
    lines = []
    # Pool measured font offsets among comparable type sizes. Actual ink
    # extrema include accents and capitals, which are not x-height samples.
    ups, downs = [], []
    for m, ids in zip(models, owners):
        q = p.components[ids]
        if not len(q):
            ups.append([]); downs.append([]); continue
        base = _at(m, (q[:, 0] + q[:, 2]) / 2)
        ups.append(((base - q[:, 1]) / m['xh']).tolist())
        downs.append(((q[:, 3] - base) / m['xh']).tolist())
    for i, (m, ids) in enumerate(zip(models, owners)):
        if not ids:
            continue
        q = p.components[ids]
        xh = m['xh']
        bodies = q[(q[:, 3] - q[:, 1] >= .5 * xh) & (q[:, 4] >= .08 * xh * xh)]
        if not len(bodies):
            continue
        a, b = int(q[:, 0].min()), int(q[:, 2].max())
        grid = np.arange(a, b)
        base = _at(m, grid)
        up = [v for j, n in enumerate(models) if .8 <= n['xh'] / xh <= 1.25 for v in ups[j] if .5 < v < 2.5]
        down = [v for j, n in enumerate(models) if .8 <= n['xh'] / xh <= 1.25 for v in downs[j] if -.3 < v < 1.2]
        topoff = max(1., float(np.percentile(up, 98)) if up else m['up'] / xh) * xh
        botoff = max(.05, float(np.percentile(down, 98)) if down else m['down'] / xh) * xh
        # Stop on the final curve, including the whole font band. No subsequent
        # geometry operation can extend across a detected rule / gutter.
        safe = np.ones(len(grid), bool)
        for dy in np.linspace(-topoff, botoff, max(3, round((topoff + botoff) / max(1, .2 * xh)))):
            y = np.clip(np.rint(base + dy).astype(int), 0, p.gray.shape[0] - 1)
            safe &= ~p.barriers[y, grid]
        for l, t, r, bot in p.gutters:
            safe &= ~((grid >= l) & (grid < r) & (base - xh / 2 >= t) & (base - xh / 2 < bot))
        for l, r in _runs(safe):
            part = q[(q[:, 0] + q[:, 2] >= 2 * (a + l)) & (q[:, 0] + q[:, 2] < 2 * (a + r))]
            if not len(part):
                continue
            aa, bb = int(max(a + l, int(part[:, 0].min()))), int(min(a + r, int(part[:, 2].max())))
            if bb <= aa:
                continue
            bs = base[aa - a:bb - a].copy()
            hint_ids = tuple(j for j, (x0, y0, x1, y1) in enumerate(hints)
                             if np.any(((part[:, 0] + part[:, 2]) / 2 >= x0) & ((part[:, 0] + part[:, 2]) / 2 < x1)
                                       & ((part[:, 1] + part[:, 3]) / 2 >= y0) & ((part[:, 1] + part[:, 3]) / 2 < y1)))
            # Pixel provenance is read from final owned components; the initial
            # discovery seed remains included when an extended piece moved out.
            segments = set(m['segments'])
            for j, (x0, y0, x1, y1) in enumerate(p.boxes):
                if np.any(((part[:, 0] + part[:, 2]) / 2 >= x0) & ((part[:, 0] + part[:, 2]) / 2 < x1)
                          & ((part[:, 1] + part[:, 3]) / 2 >= y0) & ((part[:, 1] + part[:, 3]) / 2 < y1)):
                    segments.add(j)
            lines.append(LineSegment(aa, bb, bs, bs - topoff, bs - xh, bs + botoff,
                                     np.maximum(0, bs - topoff - .4 * xh),
                                     np.minimum(p.gray.shape[0], bs + botoff + .4 * xh), xh,
                                     column=m['column'], segment_indices=tuple(sorted(segments)),
                                     hint_indices=hint_ids, support=len(m['support']),
                                     geometry_source='crop-pooled' if len(m['support']) >= 8 else 'borrowed',
                                     component_ids=tuple(part[:, 5].astype(int))))
    return lines


def _refine_bottom_contacts(p, models, owners):
    """Joint second fit on actual bottoms; capital tops are not mean lines.

    The crop fits establish line identity. Within that identity, the local
    mode of bottom residuals excludes descenders. Pool those real contacts
    again with a shared warp and per-line shifts, as in the six-line experiment.
    """
    for m, ids in zip(models, owners):
        q = p.components[ids]; xh = m['xh']
        if len(q) < 8:
            continue
        keep = ((q[:, 3] - q[:, 1] > .6 * xh) & (q[:, 3] - q[:, 1] < 2 * xh)
                & (q[:, 2] - q[:, 0] > .2 * xh) & (q[:, 2] - q[:, 0] < 2.5 * xh)
                & (q[:, 4] > .08 * xh * xh))
        q = q[keep]
        x, y = (q[:, 0] + q[:, 2]) / 2, q[:, 3]
        residual = y - _at(m, x)
        near = abs(residual) < .65 * xh
        x, y, residual = x[near], y[near], residual[near]
        if len(x) < 8:
            continue
        density = np.maximum(0, 1 - (abs(residual[:, None] - residual[None, :]) / (.18 * xh)) ** 2)
        accepted = []
        for cx, value in zip(x, residual):
            weight = np.maximum(0, 1 - (abs(x - cx) / (6 * xh)) ** 2)
            mode = residual[np.argmax((density * weight[None, :]).sum(axis=1))]
            accepted.append(abs(value - mode) < .2 * xh)
        accepted = np.array(accepted)
        if accepted.sum() >= 8:
            m['support'] = np.column_stack((x[accepted], y[accepted]))
    _pool_geometry(models)


def _boundaries(lines, height, width):
    """One sweep builds neighbour addresses; facing font lines define ONE seam."""
    starts, ends = {}, {}
    for i, line in enumerate(lines):
        starts.setdefault(line.x0, []).append(i); ends.setdefault(line.x1, []).append(i)
        line.neighbours = {k: np.full(line.x1 - line.x0, -1, int) for k in ('above', 'below')}
        line.neighbours.update(left=None, right=None)
    active = set()
    for x in range(width):
        active.difference_update(ends.get(x, ())); active.update(starts.get(x, ()))
        order = sorted(active, key=lambda i: lines[i].baseline[x - lines[i].x0] - lines[i].xheight / 2)
        for i, j in zip(order[:-1], order[1:]):
            a, b = lines[i], lines[j]
            ai, bi = x - a.x0, x - b.x0
            a.neighbours['below'][ai], b.neighbours['above'][bi] = j, i
    for a in lines:
        for j in np.unique(a.neighbours['below']):
            if j < 0:
                continue
            b = lines[j]
            ai = np.flatnonzero(a.neighbours['below'] == j); bi = ai + a.x0 - b.x0
            seam = np.clip((a.font_bottom[ai] + b.font_top[bi]) / 2, 0, height)
            a.bottom[ai], b.top[bi] = seam, seam
    for i, a in enumerate(lines):
        for side in ('left', 'right'):
            choices = []
            for j, b in enumerate(lines):
                gap = a.x0 - b.x1 if side == 'left' else b.x0 - a.x1
                if j != i and gap >= 0 and abs(np.median(a.baseline) - np.median(b.baseline)) < .6 * max(a.xheight, b.xheight):
                    choices.append((gap, j))
            if choices:
                a.neighbours[side] = min(choices)[1]


def _coalesce_lines(p, lines):
    """Extend final same-level pieces across word space after pixel assignment.

    This second opportunity matters when pooling corrected the original seed's
    tilt. It uses final geometry and the page's stops, never the seed boxes.
    """
    lines = sorted(lines, key=lambda l: l.x0)
    for i, a in enumerate(lines):
        if a is None:
            continue
        for j in range(i + 1, len(lines)):
            b = lines[j]
            if b is None:
                continue
            gap = b.x0 - a.x1
            if gap < 0 or gap > 10 * max(a.xheight, b.xheight):
                continue
            if not .8 <= b.xheight / a.xheight <= 1.25:
                continue
            if abs(a.baseline[-1] - b.baseline[0]) > .5 * min(a.xheight, b.xheight):
                continue
            middle = np.linspace(a.baseline[-1], b.baseline[0], gap + 2)[1:-1]
            if any(_blocked(p, a.x1, b.x0, middle + dy * a.xheight, a.xheight) for dy in (-.5, 0, .5)):
                continue
            xh = a.xheight if a.support >= b.support else b.xheight
            up = max(float(np.median(a.baseline - a.font_top)), float(np.median(b.baseline - b.font_top)))
            down = max(float(np.median(a.font_bottom - a.baseline)), float(np.median(b.font_bottom - b.baseline)))
            for name in CURVES:
                av, bv = getattr(a, name), getattr(b, name)
                bridge = np.linspace(av[-1], bv[0], gap + 2)[1:-1]
                setattr(a, name, np.r_[av, bridge, bv])
            a.x1 = b.x1
            a.xheight = xh
            a.font_top, a.meanline, a.font_bottom = a.baseline - up, a.baseline - xh, a.baseline + down
            a.top = np.maximum(0, a.font_top - .4 * xh)
            a.bottom = np.minimum(p.gray.shape[0], a.font_bottom + .4 * xh)
            a.segment_indices = tuple(sorted(set(a.segment_indices) | set(b.segment_indices)))
            a.hint_indices = tuple(sorted(set(a.hint_indices) | set(b.hint_indices)))
            a.component_ids = tuple(sorted(set(a.component_ids) | set(b.component_ids)))
            a.support += b.support
            lines[j] = None
    return [line for line in lines if line is not None]


def _addresses(lines, boxes):
    for j in range(len(boxes)):
        owned = [l for l in lines if j in l.segment_indices]
        owned.sort(key=lambda l: (float(np.median(l.baseline)), l.x0))
        row, peers = -1, []
        for line in owned:
            if not peers or abs(np.median(line.baseline) - np.median(peers[-1].baseline)) > .7 * line.xheight:
                row += 1; peers = []
            peers.append(line)
            line.segment_positions += ((j, row, len(peers) - 1),)


def _reading_order(lines):
    """Recursive whitespace order: spanning headings, then separate columns."""
    if len(lines) < 2:
        return lines
    xh = float(np.median([l.xheight for l in lines]))
    for axis in ('y', 'x'):
        intervals = sorted((float(l.font_top.min()), float(l.font_bottom.max())) if axis == 'y'
                           else (l.x0, l.x1) for l in lines)
        right = intervals[0][1]; gaps = []
        for a, b in intervals[1:]:
            if a - right > .8 * xh:
                gaps.append((a - right, (a + right) / 2))
            right = max(right, b)
        if gaps:
            split = max(gaps)[1]
            first = [l for l in lines if (float(l.font_bottom.max()) if axis == 'y' else l.x1) <= split]
            second = [l for l in lines if (float(l.font_top.min()) if axis == 'y' else l.x0) >= split]
            if first and second and len(first) + len(second) == len(lines):
                return _reading_order(first) + _reading_order(second)
    return sorted(lines, key=lambda l: (l.column, float(np.median(l.baseline)), l.x0))


def _diagnostics(p, lines):
    cuts, foreign, crossings, overlaps, broken = [], [], [], [], []
    strip_edges, boundary_cuts, invalid = [], [], []
    owned_ink, clipped_ink = 0, 0
    threshold = float(np.percentile(p.gray[p.ink], 75)) if p.ink.any() else 128
    cc_by_id = {int(q[5]): q for q in p.components}
    owners = {k: i for i, line in enumerate(lines) for k in line.component_ids}
    for i, line in enumerate(lines):
        x = np.arange(line.x0, line.x1)
        clipped = False; contaminated = False
        if not np.isfinite(line.top).all() or not np.isfinite(line.bottom).all() or np.any(line.top >= line.bottom):
            invalid.append(i)
        # Check original components against the actual curved boundary, BEFORE
        # whitening / resampling. A padded strip alone can hide a clipped glyph.
        for k in line.component_ids:
            q = cc_by_id[k]; a, t, b, bot = q[:4].astype(int)
            a, b = max(a, line.x0), min(b, line.x1)
            yy, xx = np.nonzero(p.labels[t:bot, a:b] == k)
            if not len(xx):
                continue
            yy, ix = yy + t, xx + a - line.x0
            outside = ((yy < line.top[ix]) | (yy >= line.bottom[ix])
                       | (yy - line.baseline[ix] < -2.5 * line.xheight)
                       | (yy - line.baseline[ix] >= 1.5 * line.xheight))
            clipped |= bool(outside.any())
            owned_ink += len(yy); clipped_ink += int(outside.sum())
        if clipped:
            boundary_cuts.append(i)
        strip = np.asarray(_extract(p.gray, line, 32))
        # Dark edge pixels are a second, independent check of the delivered strip.
        edge_touch = bool((strip[0] <= threshold).any() or (strip[-1] <= threshold).any())
        if edge_touch:
            strip_edges.append(i)
        clipped |= edge_touch
        if clipped:
            cuts.append(i)
        lo, hi = max(0, int(np.floor(line.top.min()))), min(p.gray.shape[0], int(np.ceil(line.bottom.max())))
        region = p.labels[lo:hi, line.x0:line.x1]
        ys = np.arange(lo, hi)[:, None]
        inside = (ys >= line.top) & (ys < line.bottom)
        for k in np.unique(region[inside]):
            if k and k in owners and owners[k] != i:
                contaminated = True; break
        if contaminated:
            foreign.append(i)
        if _blocked(p, line.x0, line.x1, line.baseline, line.xheight):
            crossings.append(i)
        for j in range(i + 1, len(lines)):
            b = lines[j]
            lo, hi = max(line.x0, b.x0), min(line.x1, b.x1)
            if hi > lo:
                ai, bi = slice(lo - line.x0, hi - line.x0), slice(lo - b.x0, hi - b.x0)
                if np.any(np.minimum(line.bottom[ai], b.bottom[bi]) - np.maximum(line.top[ai], b.top[bi]) > 1e-8):
                    overlaps.append([i, j])
                continue
            left, right = (line, b) if line.x0 < b.x0 else (b, line)
            gap = right.x0 - left.x1
            if gap > 10 * max(left.xheight, right.xheight):
                continue
            if abs(left.baseline[-1] - right.baseline[0]) > .5 * min(left.xheight, right.xheight):
                continue
            if not _blocked(p, left.x1, right.x0, float((left.baseline[-1] + right.baseline[0]) / 2), left.xheight):
                broken.append([i, j])
    multi = sum(sum(j in line.segment_indices for line in lines) > 1 for j in range(len(p.boxes)))
    return dict(pixel_segments=len(p.boxes), final_lines=len(lines), multi_line_segments=multi,
                cut_ink_lines=len(cuts), foreign_ink_lines=len(foreign), rule_gutter_crossings=len(crossings),
                boundary_overlaps=len(overlaps), broken_line_pairs=len(broken),
                cut_line_indices=cuts, foreign_line_indices=foreign, crossing_line_indices=crossings,
                overlap_pairs=overlaps, broken_pairs=broken,
                strip_edge_touch_lines=len(strip_edges), strip_edge_indices=strip_edges,
                source_boundary_cut_lines=len(boundary_cuts), invalid_boundary_lines=invalid,
                assigned_ink_pixels=owned_ink, cut_assigned_ink_pixels=clipped_ink,
                assigned_ink_retained_fraction=1 - clipped_ink / max(1, owned_ink),
                unassigned_body_components=int(sum(int(q[5]) not in owners and q[3] - q[1] >= .55 * p.xheight
                                                   and q[4] >= .08 * p.xheight ** 2 for q in p.components)),
                measurement='Pixel/component diagnostics; ownership is inferred, not independent ground truth.')


def segment_page(page: Image.Image | NDArray[Any], hints: Sequence[Sequence[float]] | None = None) -> PageSegmentation:
    """Analyse pixels and return rough segments, final lines, and diagnostic counts."""
    boxes = np.asarray([] if hints is None else hints, float)
    if boxes.size and (boxes.ndim != 2 or boxes.shape[1] != 4 or not np.isfinite(boxes).all()
                       or np.any(boxes[:, 2:] <= boxes[:, :2])):
        raise ValueError('hints must be finite positive-area (x0,y0,x1,y1) boxes')
    boxes = boxes.reshape(-1, 4)
    p = prepare_pixels(page)
    models = _reject_residual_bands(_merge(p, _discover(p)))
    _lanes(models)
    _pool_geometry(models)
    # Pooling can align formerly isolated seed pieces; join again before owning
    # the page ink. A word gap never gets a separate final line by itself.
    models = _merge(p, models)
    owners = _assign(p, models)
    _refine_bottom_contacts(p, models, owners)
    owners = _assign(p, models)
    lines = _make_lines(p, models, owners, boxes)
    lines = _coalesce_lines(p, lines)
    lines = _reading_order(lines)
    _boundaries(lines, *p.gray.shape)
    _addresses(lines, p.boxes)
    return PageSegmentation(lines, p.boxes, p.xheight, _diagnostics(p, lines), p)


def page_line_segments(page: Image.Image | NDArray[Any], hints: Sequence[Sequence[float]] | None = None) -> list[LineSegment]:
    """Return one curved segment per detected printed line, starting from pixels."""
    return segment_page(page, hints=hints).lines


def extract_line_image(page: Image.Image | NDArray[Any], line: LineSegment, *, xheight: int = 32) -> Image.Image:
    """Unroll raw pixels within the tessellated boundary at a fixed x-height position."""
    if not isinstance(xheight, (int, np.integer)) or xheight <= 0:
        raise ValueError('xheight must be a positive integer')
    return _extract(_gray(page), line, xheight)


def _extract(gray, line, xheight):
    scale = xheight / line.xheight
    width = max(1, int(np.ceil((line.x1 - line.x0) * scale)))
    # Centre-aligned resampling avoids shrinking away the first/last column.
    xs = line.x0 + (np.arange(width) + .5) / scale - .5
    xs = np.clip(xs, line.x0, line.x1 - 1)
    grid = np.arange(line.x0, line.x1)
    base = np.interp(xs, grid, line.baseline)
    offsets = (np.arange(4 * xheight) - 2.5 * xheight) / scale
    yy = base[None, :] + offsets[:, None]
    xx = np.broadcast_to(xs, yy.shape)
    strip = ndi.map_coordinates(gray, [yy, xx], order=1, mode='constant', cval=255)
    top, bottom = np.interp(xs, grid, line.top), np.interp(xs, grid, line.bottom)
    strip[(yy < top) | (yy >= bottom)] = 255
    return Image.fromarray(np.clip(strip, 0, 255).astype(np.uint8))

"""Pixels → rough segments → crop-tool fits → shared geometry → OCR strips.

See docs/PAGE_LINES_ALGORITHM.md. Text-layer boxes are optional provenance
hints only: supplying them cannot change detection or the geometry. The mature
crop fitter (including its end-bend scorer) remains the line evidence engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import copy
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

from ..glyphs.baseline import text_lines
from .font import fit_guides
from ..glyphs.components import _xheight, _line_geometry, _stable_peel_ink
from .pixels import PixelPage, _gray, _runs, prepare_pixels

__all__ = ['LineSegment', 'PageSegmentation', 'page_line_segments', 'segment_page', 'extract_line_image']

ACCENT_TOP_XH = 1.85  # x-heights above baseline: leave room for a high detached accent.
ACCENT_BOTTOM_XH = 1.25  # x-heights above baseline: lower edge of the default accent band.
SEED_CONTEXT_XH = 1.5  # x-heights: give the crop fitter context on both sides of each seed.
SEED_BODY_AREA_XH2 = 0.08  # square x-heights: exclude specks when seeding a text band.
SEED_BODY_HEIGHT_XH = 0.45  # x-heights: require a substantial body before fitting a band.
BODY_AREA_XH2 = 0.065  # square x-heights: preserve small bodies while rejecting specks.
MODEL_END_FIT_XH = 3  # x-heights: estimate endpoint slope from nearby baseline contacts.
LINE_END_FIT_XH = 3  # x-heights: extend final guides using their local endpoint slope.
MODEL_END_MAX_SLOPE = 0.3  # page y units per x unit: cap extrapolation of a seed baseline.
LINE_END_MAX_SLOPE = 0.35  # page y units per x unit: cap final-guide extrapolation at a line end.
STRIP_HEIGHT_XH = 4  # output x-heights: fixed recognition-strip canvas height.
STRIP_BASELINE_XH = 2.5  # output x-heights: align every delivered baseline on the same strip row.

BARRIER_BODY_CENTRE_XH = 0.5  # x-heights above baseline: sample the middle of the body band.
BARRIER_BODY_RADIUS_XH = 0.45  # x-heights: inspect the body band on both sides of its centre.
SEED_MIN_CONTRAST_SHARE = 0.45  # dimensionless contrast share: freeze a strong-ink reference before peeling.
SIZE_MIN_CONTRAST_SHARE = 0.7  # dimensionless contrast share: estimate size from stronger letter bodies.
SEED_MIN_SIZE_RATIO = 0.65  # x-heights per page x-height: reject implausibly small local size estimates.
SEED_MAX_SIZE_RATIO = 5  # x-heights per page x-height: permit headings in the same rough region.
SHORT_CELL_BASELINE_SLACK_XH = 0.75  # x-heights: group contacts conservatively when a short cell cannot establish slope.
INITIAL_TOP_XH = 1.5  # x-heights above baseline: initialize the capital guide before class fitting.
INITIAL_BOTTOM_XH = 0.5  # x-heights below baseline: initialize the lower guide before class fitting.
SEED_MIN_PITCH_XH = 0.8  # x-heights: bound peeling iterations by available vertical room.
SEED_MIN_REMAINING_AREA_XH2 = 0.12  # square x-heights: stop peeling when only scattered ink remains.
SEED_PROFILE_WINDOW_XH = 0.5  # x-heights: smooth body-scale holes in the vertical ink profile.
SEED_PEAK_OFFSET_XH = 0.4  # x-heights below a profile peak: place the initial body focus.
SEED_FOCUS_RADIUS_XH = 0.7  # x-heights: give the crop fitter a local band around the ink peak.
SEED_COMPONENT_HEIGHT_XH = 2.6  # x-heights: allow marks and ascenders but exclude tall graphics.
SEED_COMPONENT_WIDTH_XH = 8  # x-heights: allow connected short words in the seed band.
SEED_BODY_DISTANCE_XH = 0.85  # x-heights: attach full-height bodies only near the fitted path.
SEED_MARK_HEIGHT_XH = 0.5  # x-heights: smaller components use the detached-mark distance.
SEED_MARK_DISTANCE_XH = 1.2  # x-heights: preserve accents above the fitted body band.
SEED_REGION_PADDING_XH = 0.3  # x-heights: permit a seed centre just outside a rough region.
RECOVERY_MIN_HEIGHT_XH = 0.7  # x-heights: recover substantial missed bodies rather than marks.
RECOVERY_MAX_HEIGHT_XH = 3.5  # x-heights: reject tall residual graphics from body recovery.
RECOVERY_MAX_WIDTH_XH = 3  # x-heights: keep missed bodies local in horizontal extent.
RECOVERY_MIN_AREA_XH2 = 0.12  # square x-heights: require body-scale evidence for a recovered seed.
RECOVERY_BASELINE_SLACK_XH = 0.35  # x-heights: recover only groups with agreeing lower contacts.
WEAK_SEED_SUPPORT_SHARE = 0.4  # dimensionless support share: let a stronger peer resolve a weak seed.
WEAK_SEED_VERTICAL_REACH_XH = 1.6  # x-heights: compare weak seeds only to nearby baseline bands.
DUPLICATE_COMPONENT_SHARE = 0.4  # dimensionless component share: repeated ownership identifies a duplicate seed.
MERGE_BASELINE_SLACK_XH = 0.45  # x-heights: merge only seed curves that agree across the overlap.
COLUMN_OVERLAP_SHARE = 0.55  # dimensionless overlap share: assign rough regions to the predominant column.
POOLED_CONTACT_SLACK_XH = 0.3  # x-heights: use contacts agreeing with their original local fit.
GAUSSIAN_EXPONENT_FACTOR = 0.5  # dimensionless Gaussian coefficient: retain the standard squared-distance kernel.
POOLED_MIN_WEIGHT = 0.01  # dimensionless fit weight: count contacts with meaningful local influence.
POOLED_INTERCEPT_RIDGE = 1e-08  # dimensionless normalized fit penalty: stabilize a near-singular intercept solve.
POOLED_SLOPE_RIDGE = 0.02  # dimensionless normalized fit penalty: constrain local slope without flattening curl.
POOLED_CURVATURE_RIDGE = 0.2  # dimensionless normalized fit penalty: suppress unsupported higher-order curvature.
FAINT_CONTRAST_SHARE = 0.6  # dimensionless contrast share: classify faint candidates relative to page text ink.
ASSIGN_BODY_HEIGHT_XH = 0.55  # x-heights: distinguish full bodies from detached marks.
ASSIGN_BODY_AREA_XH2 = 0.08  # square x-heights: distinguish body ink from small marks.
ASSIGN_HORIZONTAL_REACH_XH = 10  # x-heights: avoid borrowing a remote component into a line.
ASSIGN_VERTICAL_REACH_XH = 6  # x-heights: bound the search around each model centre.
ASSIGN_MAX_HEIGHT_XH = 3.2  # x-heights: reject tall graphics before assigning ink to text.
ASSIGN_MAX_WIDTH_XH = 12  # x-heights: reject long graphics before assigning ink to text.
ASSIGN_MAX_DISTANCE_XH = 1.25  # x-heights: require nearby body-band evidence.
ASSIGN_OVERLAP_BODY_HEIGHT_XH = 0.6  # x-heights: large bodies must intersect the expected body band.
ASSIGN_BAND_BOTTOM_XH = 0.2  # x-heights below baseline: allow short descenders in ownership scoring.
ASSIGN_BAND_TOP_XH = 1.1  # x-heights above baseline: include a small allowance above the meanline.
ASSIGN_MIN_BODY_OVERLAP_XH = 0.25  # x-heights: require a substantial intersection with the expected body band.
ASSIGN_HORIZONTAL_COST = 0.025  # dimensionless distance weight: break similar vertical matches by locality.
ASSIGN_SEED_BONUS = 0.12  # dimensionless score: favor the seed that already supported a component.
MARK_BODY_HORIZONTAL_REACH_XH = 0.3  # x-heights: attach detached marks to a nearby owned body.
MARK_BODY_VERTICAL_REACH_XH = 0.6  # x-heights: keep detached marks within their body neighbourhood.
FINAL_BODY_HEIGHT_XH = 0.5  # x-heights: require body-sized ink when refining a final line.
FINAL_TOP_SEARCH_XH = 1.9  # x-heights above baseline: search for high accents in the final ribbon.
FINAL_BOTTOM_SEARCH_XH = 0.6  # x-heights below baseline: retain lower marks in the final ribbon.
FINAL_SEARCH_STEP_XH = 0.2  # x-heights: sample the ribbon finely enough to observe detached marks.
FINAL_INITIAL_PADDING_XH = 0.4  # x-heights: initialize the outer envelope before fitting guides.
ANCHOR_MIN_HEIGHT_XH = 0.6  # x-heights: refine guides using substantial letter bodies.
ANCHOR_MAX_HEIGHT_XH = 2  # x-heights: omit tall combined components from local anchor fitting.
ANCHOR_MIN_WIDTH_XH = 0.2  # x-heights: omit narrow strokes from local anchor fitting.
ANCHOR_MAX_WIDTH_XH = 2.5  # x-heights: omit wide ligatures from local anchor fitting.
ANCHOR_RESIDUAL_LIMIT_XH = 0.65  # x-heights: restrict candidate guide contacts to the current band.
ANCHOR_MODE_RADIUS_XH = 0.18  # x-heights: estimate the densest local contact offset.
ANCHOR_ACCEPT_RADIUS_XH = 0.2  # x-heights: accept contacts close to the fitted modal offset.
DISCOUNT_MIN_CONTRAST_SHARE = 0.62  # dimensionless contrast share: retain faint candidates in data with a reason.
FAINT_BODY_MAX_HEIGHT_XH = 2.6  # x-heights: estimate faintness from plausible body components.
FAINT_BODY_MAX_WIDTH_XH = 3  # x-heights: exclude wide connected graphics from faintness evidence.
FAINT_BODY_MIN_AREA_XH2 = 0.07  # square x-heights: omit specks from the faint-body reference.
FAINT_LIGHT_CONTRAST_SHARE = 0.6  # dimensionless contrast share: a faint cluster must remain below strong print.
FAINT_DARK_CONTRAST_SHARE = 0.75  # dimensionless contrast share: the comparison cluster must contain strong print.
FAINT_CLUSTER_CONTRAST_RATIO = 0.5  # dimensionless contrast ratio: require separation between faint and dark clusters.
GRAPHIC_MAX_BODY_SHARE = 0.2  # dimensionless component share: repeated non-body marks suggest a graphic band.
GRAPHIC_MAX_SUPPORT_SHARE = 0.25  # dimensionless component share: graphic discounting needs little crop-fit support.
PATTERN_MAX_VARIATION = 0.12  # dimensionless coefficient of variation: detect near-identical repeated marks.
PATTERN_MIN_FILL = 0.68  # dimensionless occupied area share: dense repeated marks are poor text evidence.
PATTERN_MIN_WIDTH_XH = 0.6  # x-heights: do not discount ordinary narrow punctuation as a graphic pattern.
DISCOUNT_NEIGHBOUR_SLACK_XH = 0.5  # x-heights: associate nearby candidates within the same baseline band.
ENVELOPE_GUIDE_PADDING_XH = 0.3  # x-heights: protect antialiased ink outside fitted font/accent guides.
ENVELOPE_INK_PADDING_XH = 0.15  # x-heights: preserve observed ink at the final envelope edge.
ENVELOPE_MIN_RISE_XH = 1.95  # x-heights: retain the expected high-accent headroom.
ENVELOPE_MIN_DROP_XH = 0.65  # x-heights: retain lower punctuation even with sparse support.
SEAM_NEIGHBOUR_REACH_XH = 4.5  # x-heights: compute seams only between nearby rows.
SEAM_GUIDE_CLEARANCE_XH = 0.05  # x-heights: leave a narrow corridor between neighboring body guides.
PIXEL_EDGE_HALF_STEP = 0.5  # source pixel units: convert a component edge to its half-open pixel boundary.
SEAM_FILTER_RADIUS_XH = 0.35  # x-heights: remove narrow seam excursions around ink.
SEAM_SMOOTHING_XH = 0.15  # x-heights: smooth the seam without flattening local curl.
LATERAL_BASELINE_SLACK_XH = 0.6  # x-heights: identify neighbours belonging to the same printed row.
JOIN_MIN_SIZE_RATIO = 0.8  # dimensionless x-height ratio: join pieces only at compatible type sizes.
JOIN_MAX_SIZE_RATIO = 1.25  # dimensionless x-height ratio: symmetric upper bound for compatible type sizes.
JOIN_BASELINE_SLACK_XH = 0.5  # x-heights: join facing endpoints only when their baseline contacts agree.
JOIN_BARRIER_OFFSET_XH = 0.5  # x-heights: inspect parallel paths before joining across a gap.
JOIN_ENVELOPE_PADDING_XH = 0.4  # x-heights: preserve ink headroom when extending a joined line.
ROW_GROUP_BASELINE_SLACK_XH = 0.7  # x-heights: retain local row identity while following curved contacts.
HINT_OVERLAP_SHARE = 0.55  # dimensionless horizontal share: attach optional hints only to a predominant line.
RIBBON_SPLIT_GAP_XH = 0.8  # x-heights: preserve meaningful gaps between recovered line pieces.
STRIP_INK_TOP_XH = 2.5  # x-heights above baseline: reject remote ink from a recognition strip.
STRIP_INK_BOTTOM_XH = 1.5  # x-heights below baseline: reject remote ink from a recognition strip.
GEOMETRY_COMPARISON_EPSILON_PX = 1e-08  # source pixel units: ignore numerical residue in envelope diagnostics.
PITCH_MIN_XH = 1.5  # x-heights: skip within-row distances when estimating line spacing.
PITCH_DEFAULT_XH = 2.5  # x-heights: use a conservative spacing when no row pair is measurable.
PITCH_MIN_SEPARATION_SHARE = 0.5  # dimensionless pitch share: identify unusually close overlapping baseline bands.
UNASSIGNED_MAX_HEIGHT_XH = 2.5  # x-heights: audit plausible unassigned bodies instead of tall graphics.
UNASSIGNED_MAX_AREA_XH2 = 4  # square x-heights: audit plausible body ink rather than large blobs.

CURVES = ('baseline', 'font_top', 'meanline', 'font_bottom', 'accent_bottom', 'accent_top', 'top', 'bottom')


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

    accent_bottom: NDArray | None = field(default=None, repr=False)
    accent_top: NDArray | None = field(default=None, repr=False)
    borrowed: tuple[str, ...] = ()
    ink_classes: dict = field(default_factory=dict)
    contrast: float = 1.
    discounted: str | None = None
    guide_residuals: dict = field(default_factory=dict)
    guide_samples: dict = field(default_factory=dict, repr=False)
    address: dict = field(default_factory=dict)
    row_source: str | None = None

    def __post_init__(self):
        if self.accent_top is None:
            self.accent_top = self.baseline - ACCENT_TOP_XH * self.xheight
        if self.accent_bottom is None:
            self.accent_bottom = self.baseline - ACCENT_BOTTOM_XH * self.xheight

    def unroll(self, page: Image.Image | NDArray[Any], *, xheight: int = 32) -> Image.Image:
        """Return a grayscale strip with meanline at 1.5 and baseline at 2.5 x-heights."""
        return extract_line_image(page, self, xheight=xheight)

    def to_record(self) -> dict:
        """JSON-ready review record, including the once-built neighbour graph."""
        row = {k: np.round(getattr(self, k), 3).tolist() for k in CURVES}
        row.update(x0=self.x0, x1=self.x1, xheight=self.xheight, column=self.column,
                   segment_indices=list(self.segment_indices), hint_indices=list(self.hint_indices),
                   segment_positions=[list(p) for p in self.segment_positions], support=self.support,
                   geometry_source=self.geometry_source, borrowed=list(self.borrowed),
                   ink_classes=self.ink_classes, contrast=round(self.contrast, 4), discounted=self.discounted,
                   guide_residuals=self.guide_residuals,
                   neighbours={k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in self.neighbours.items()})
        row.update(self.address)
        if self.row_source is not None:
            row['row_source'] = self.row_source
        return row


@dataclass
class PageSegmentation:
    """Final lines and their pixel-segment provenance, with measurable diagnostics."""
    lines: list[LineSegment]
    segments: list[tuple[int, int, int, int]]
    xheight: float
    diagnostics: dict
    pixels: PixelPage = field(repr=False)
    structure: dict = field(default_factory=dict)


WIDE_GUTTER_XH = 2  # x-heights: only wide finite gutters block the full body band.
SHORT_CELL_WIDTH_XH = 3  # x-heights: very short cells cannot establish their own orientation.
SEED_BODY_WIDTH_XH = 6  # x-heights: allow connected bodies without accepting a long graphic.
RECOVERY_HORIZONTAL_REACH_XH = 8  # x-heights: recover body groups using local horizontal support.
UNSUPPORTED_SEED_WIDTH_XH = 4  # x-heights: a broad unsupported seed needs stronger evidence.
SEED_MERGE_VERTICAL_REACH_XH = 5  # x-heights: compare seed curves only within nearby bands.
SEED_MERGE_HORIZONTAL_REACH_XH = 10  # x-heights: prevent merging remote seed fragments.
RELIABLE_SEED_WIDTH_XH = 8  # x-heights: shared shape fits need a substantial observed baseline span.
SHARED_FIT_VERTICAL_REACH_XH = 14  # x-heights: borrow shape only within a local column neighbourhood.
ANCHOR_HORIZONTAL_REACH_XH = 6  # x-heights: limit the influence of a refined guide contact.
FAINT_CLUSTER_MIN_SPAN_XH = 2  # x-heights: faint/dark clusters each need a useful horizontal span.
UNSUPPORTED_LINE_WIDTH_XH = 5  # x-heights: broad lines with too few supporting contacts remain discounted.
GRAPHIC_LINE_WIDTH_XH = 10  # x-heights: compare long graphic candidates against neighboring text bands.
JOIN_MAX_GAP_XH = 10  # x-heights: do not bridge a remote horizontal gap between pieces.

POOLED_HORIZONTAL_RADIUS_XH = 6  # x-heights: local shape pooling follows a short horizontal text span.
POOLED_VERTICAL_RADIUS_XH = 8  # x-heights: neighboring rows contribute less as vertical distance increases.


def _blocked(p: PixelPage, x0, x1, base, xh):
    a, b = max(0, int(x0)), min(p.gray.shape[1], int(x1))
    if b <= a:
        return False
    x = np.arange(a, b)
    y = np.broadcast_to(base, (len(x),)) - BARRIER_BODY_CENTRE_XH * xh
    for dy in (-BARRIER_BODY_RADIUS_XH * xh, 0, BARRIER_BODY_RADIUS_XH * xh):
        rows = np.clip(np.rint(y + dy).astype(int), 0, p.gray.shape[0] - 1)
        if p.barriers[rows, x].any():
            return True
    for l, t, r, bot in p.gutters:
        if (bot-t == p.gray.shape[0] or r-l > WIDE_GUTTER_XH*xh) and a < r and b > l and t <= np.median(y) < bot:
            return True
    return False


def _discover(p: PixelPage):
    """Peel all main bands in each rough region using the existing crop tools."""
    cc = p.components
    component_ids = cc[:, 5].astype(int)
    component_cache = {}
    h, w = p.gray.shape
    models = []
    for si, (a, t, b, bot) in enumerate(p.boxes):
        t0, t1 = max(0, int(t - SEED_CONTEXT_XH * p.xheight)), min(h, int(bot + SEED_CONTEXT_XH * p.xheight))
        paper = float(np.percentile(p.gray[t0:t1, a:b], 90))
        local = cc[(cc[:, 0] >= a) & (cc[:, 2] <= b) & (cc[:, 1] >= t) & (cc[:, 3] <= bot)]
        useful = local[(local[:, 4] > SEED_BODY_AREA_XH2 * p.xheight ** 2) & (local[:, 3] - local[:, 1] > SEED_BODY_HEIGHT_XH * p.xheight)]
        # Preserve the crop tools' photometry: replacing grey paper with white
        # makes bleed-through look like strong print. Freeze a local contrast
        # reference before peeling, so leftovers cannot promote themselves to
        # new lines when the main text has been removed. Faint ink remains in
        # the page component map and can attach to the established paths later.
        ink_level = float(np.percentile(useful[:, 6], 35)) if len(useful) else paper
        strong_ids = component_ids[cc[:, 6] <= paper - SEED_MIN_CONTRAST_SHARE * (paper - ink_level)]
        mask = p.ink[t0:t1, a:b] & np.isin(p.labels[t0:t1, a:b], strong_ids)
        sub = np.where(mask, p.gray[t0:t1, a:b], paper)
        xh = p.xheight
        size_ink = useful[useful[:, 6] <= paper-SIZE_MIN_CONTRAST_SHARE*(paper-ink_level)]
        if len(size_ink) >= 1:
            measured = _xheight(size_ink[:, 3] - size_ink[:, 1])
            if SEED_MIN_SIZE_RATIO * xh <= measured <= SEED_MAX_SIZE_RATIO * xh:
                xh = measured
        if b - a < SHORT_CELL_WIDTH_XH * xh and len(useful):
            # A one/two-character cell cannot determine orientation. Keep its
            # baseline contacts, and defer its shape to the shared page fit.
            groups = []
            for q in sorted(useful, key=lambda q: q[3]):
                if not groups or q[3] - groups[-1][-1][3] > SHORT_CELL_BASELINE_SLACK_XH * xh:
                    groups.append([])
                groups[-1].append(q)
            for group in groups:
                q = np.array(group)
                base = float(np.median(q[:, 3]))
                ids = set(q[:, 5].astype(int))
                models.append(dict(a=a, b=b, base=np.full(b - a, base), xh=xh,
                                   up=INITIAL_TOP_XH * xh, down=INITIAL_BOTTOM_XH * xh, ids=ids,
                                   body_ids=ids.copy(), segments={si},
                                   support=np.column_stack(((q[:, 0] + q[:, 2]) / 2, q[:, 3])),
                                   cy=base - xh / 2, column=0))
            continue
        stable_ink = _stable_peel_ink(sub, paper)
        for _ in range(max(2, int((t1 - t0) / (SEED_MIN_PITCH_XH * xh)) + 1)):
            if (sub < paper - 1).sum() < SEED_MIN_REMAINING_AREA_XH2 * xh * xh:
                break
            profile = ndi.uniform_filter1d((sub < paper - 1).sum(axis=1).astype(float), max(1, round(SEED_PROFILE_WINDOW_XH * xh)))
            peak = float(np.argmax(profile)) + SEED_PEAK_OFFSET_XH * xh
            g = _line_geometry(sub, xh_prior=xh, focus=(peak - SEED_FOCUS_RADIUS_XH * xh, peak + SEED_FOCUS_RADIUS_XH * xh),
                            component_cache=component_cache, ink=sub < paper if stable_ink else None)
            guides = text_lines(g, max_per_side=0)
            body = [c for c in g.components if c.role == 'letter' and c.h >= SEED_BODY_HEIGHT_XH * xh
                    and c.area >= BODY_AREA_XH2 * xh * xh and c.w <= SEED_BODY_WIDTH_XH * xh]
            if not body:
                break
            own = []
            for c in g.components:
                base = g.band.bottom[min(max(int(c.cx), 0), g.width - 1)]
                near = abs((c.y0 + c.y1) / 2 - (base - xh / 2))
                if c.h <= SEED_COMPONENT_HEIGHT_XH * xh and c.w <= SEED_COMPONENT_WIDTH_XH * xh and near < (SEED_BODY_DISTANCE_XH if c.h >= SEED_MARK_HEIGHT_XH * xh else SEED_MARK_DISTANCE_XH) * xh:
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
                break
            q = cc[np.isin(component_ids, list(body_ids))]
            cy = float(np.median((q[:, 1] + q[:, 3]) / 2))
            # Expanded windows see neighbours too. Only seed-owned bands enter
            # here; all surviving neighbouring pixels remain for their seed.
            if not t - SEED_REGION_PADDING_XH * xh <= cy < bot + SEED_REGION_PADDING_XH * xh:
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


def _recover_bodies(p, models):
    """Recover body rows left by crop peeling (including all-capital heads).

    Crop focus may select the body paragraph repeatedly and leave its taller
    running head untouched. Independent bottom-contact groups seed those rows.
    Nothing is recovered from OCR hints.
    """
    used = set().union(*(m['body_ids'] for m in models)) if models else set()
    q = p.components
    pending = q[(~np.isin(q[:, 5], list(used))) & (q[:, 3]-q[:, 1] > RECOVERY_MIN_HEIGHT_XH*p.xheight)
                & (q[:, RECOVERY_MAX_WIDTH_XH]-q[:, 1] < RECOVERY_MAX_HEIGHT_XH*p.xheight) & (q[:, 2]-q[:, 0] < RECOVERY_MAX_WIDTH_XH*p.xheight)
                & (q[:, 4] > RECOVERY_MIN_AREA_XH2*p.xheight**2)]
    groups = []
    for row in sorted(pending, key=lambda q: q[3]):
        choices = [g for g in groups if abs(row[3]-np.median(np.array(g)[:, 3])) < RECOVERY_BASELINE_SLACK_XH*p.xheight
                   and min(abs(row[0]-r[2]) for r in g) < RECOVERY_HORIZONTAL_REACH_XH*max(p.xheight, row[3]-row[1])]
        if choices:
            choices[-1].append(row)
        else:
            groups.append([row])
    for rows in groups:
        q = np.array(rows)
        if len(q) < 3:
            continue
        xh = float(np.median(q[:, 3]-q[:, 1]))
        a, b = int(q[:, 0].min()), int(q[:, 2].max())
        base = float(np.median(q[:, 3]))
        if _blocked(p, a, b, base, xh):
            continue
        segments = {i for i, (l,t,r,bot) in enumerate(p.boxes)
                    if a < r and b > l and t <= np.median(q[:, 1:4:2]) <= bot}
        if not segments:
            continue
        support = np.column_stack(((q[:, 0]+q[:, 2])/2, q[:, 3]))
        ids = set(q[:, 5].astype(int))
        models.append(dict(a=a, b=b, base=np.full(b-a, base), xh=xh, up=INITIAL_TOP_XH*xh, down=INITIAL_BOTTOM_XH*xh,
                           ids=ids, body_ids=ids.copy(), segments=segments, support=support,
                           cy=base-xh/2, column=0))
    return models


def _reject_residual_bands(models):
    """A few leftover ascenders cannot invent another line beside a full one.

    A short cell/last line is retained at its own vertical level. Unlike a
    minimum line width, this test does not reject legitimate short text.
    """
    strong = [m for m in models if len(m['support']) >= 8 and len(m['body_ids']) >= 4]
    out = []
    for m in models:
        if not len(m['support']) and m['b'] - m['a'] > UNSUPPORTED_SEED_WIDTH_XH * m['xh']:
            continue
        if strong:
            conflict = False
            for n in strong:
                if n is m or len(m['support']) >= WEAK_SEED_SUPPORT_SHARE * len(n['support']):
                    continue
                a, b = max(m['a'], n['a']), min(m['b'], n['b'])
                if b <= a:
                    continue
                grid = np.linspace(a, b - 1, 5)
                delta = np.median(abs(_at(m, grid) - _at(n, grid)))
                if delta < WEAK_SEED_VERTICAL_REACH_XH * min(m['xh'], n['xh']):
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
        n = min(len(grid), max(2, round(MODEL_END_FIT_XH * m['xh'])))
        sl = np.clip((m['base'][n - 1] - m['base'][0]) / (n - 1), -MODEL_END_MAX_SLOPE, MODEL_END_MAX_SLOPE)
        sr = np.clip((m['base'][-1] - m['base'][-n]) / (n - 1), -MODEL_END_MAX_SLOPE, MODEL_END_MAX_SLOPE)
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
            if shared > DUPLICATE_COMPONENT_SHARE:
                target = n; break
            if abs(m['cy'] - n['cy']) > SEED_MERGE_VERTICAL_REACH_XH * xh or overlap < -SEED_MERGE_HORIZONTAL_REACH_XH * xh:
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
            if np.max(np.abs(_at(m, xs) - _at(n, xs))) > MERGE_BASELINE_SLACK_XH * xh:
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
            if min(r, b) - max(l, a) > COLUMN_OVERLAP_SHARE * min(r - l, b - a):
                found = k; break
        if found is None:
            found = len(spans); spans.append((a, b))
        m['column'] = found


def _pool_geometry(models):
    """Local shared column warp + per-line vertical shift; sparse cells borrow."""
    reliable = [m for m in models if len(m['support']) >= 8 and m['b'] - m['a'] >= RELIABLE_SEED_WIDTH_XH * m['xh'] and not m.get('faint', False)]
    slopes = [np.median(np.diff(m['base'])) for m in reliable]
    page_slope = float(np.median(slopes)) if slopes else 0.
    contacts = {}
    for n in reliable:
        support = n['support']
        ok = abs(support[:, 1] - _at(n, support[:, 0])) < POOLED_CONTACT_SLACK_XH * n['xh']
        contacts[id(n)] = support[ok]
    ridge = np.diag([POOLED_INTERCEPT_RIDGE, POOLED_SLOPE_RIDGE, POOLED_CURVATURE_RIDGE, POOLED_CURVATURE_RIDGE])
    new = []
    for m in models:
        grid = np.arange(m['a'], m['b'])
        anchor = float(np.median(m['support'][:, 0])) if len(m['support']) else (m['a'] + m['b']) / 2
        nearby = [n for n in reliable if n['column'] == m['column'] and abs(n['cy'] - m['cy']) < SHARED_FIT_VERTICAL_REACH_XH * m['xh']]
        if not nearby:
            nearby = sorted([n for n in reliable if n['column'] == m['column']], key=lambda n: abs(n['cy'] - m['cy']))[:4]
        if nearby:
            # Alternating offsets align all baseline contacts to one curve.
            # Only contacts agreed with by the crop fit enter this shared fit.
            px, py, pypos = [], [], []
            for n in nearby:
                s = contacts[id(n)]
                px.extend(s[:, 0] - m['a'])
                py.extend(s[:, 1] - float(_at(n, anchor)))
                pypos.extend(np.full(len(s), (n['cy'] - m['cy']) / m['xh']))
            if len(px) >= 4:
                # A local linear surface in page y allows gradual skew drift.
                # It still pools the letters; it does not fit sparse cells.
                px, py, pypos = np.array(px), np.array(py), np.array(pypos)
                knots = np.linspace(0, len(grid) - 1, max(2, int(len(grid) / m['xh']) + 1))
                values = []
                vertical_weight = np.exp(-GAUSSIAN_EXPONENT_FACTOR * (pypos / POOLED_VERTICAL_RADIUS_XH) ** 2)
                for gx in knots:
                    dx = (px - gx) / m['xh']
                    weight = np.clip(1 - (abs(dx) / POOLED_HORIZONTAL_RADIUS_XH) ** 3, 0, None) ** 3 * vertical_weight
                    if (weight > POOLED_MIN_WEIGHT).sum() < 4:
                        near = np.argsort(abs(dx))[:8]
                        weight = np.zeros_like(px); weight[near] = 1
                    design = np.column_stack((np.ones_like(dx), dx, pypos, dx * pypos))
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
    paper = float(np.percentile(p.gray, 90))
    reference = float(np.percentile(p.components[:, 6], 25)) if len(p.components) else paper
    faint_level = paper-FAINT_CONTRAST_SHARE*(paper-reference)
    q = p.components
    a, t, b, bot, area = q[:, :5].T
    cx, cy = (a + b) / 2, (t + bot) / 2
    best = np.full(len(q), np.inf)
    for j, m in enumerate(models):
        xh = m['xh']
        gap = np.maximum(np.maximum(m['a'] - b, a - m['b']), 0)
        small = (bot - t < ASSIGN_BODY_HEIGHT_XH * xh) | (area < ASSIGN_BODY_AREA_XH2 * xh * xh)
        eligible = (~((q[:, 6] > faint_level) & (not m.get('faint', False)))
                    & ~(small & (gap > xh))
                    & (gap <= ASSIGN_HORIZONTAL_REACH_XH * xh)
                    & (abs(cy - m['cy']) <= ASSIGN_VERTICAL_REACH_XH * xh)
                    & (bot - t <= ASSIGN_MAX_HEIGHT_XH * xh)
                    & (b - a <= ASSIGN_MAX_WIDTH_XH * xh))
        ids = np.flatnonzero(eligible)
        base = _at(m, cx[ids])
        distance = abs(cy[ids] - (base - xh / 2))
        overlap = np.minimum(bot[ids], base + ASSIGN_BAND_BOTTOM_XH * xh) - np.maximum(t[ids], base - ASSIGN_BAND_TOP_XH * xh)
        keep = ((distance <= ASSIGN_MAX_DISTANCE_XH * xh)
                & ~((bot[ids] - t[ids] >= ASSIGN_OVERLAP_BODY_HEIGHT_XH * xh)
                    & (overlap < ASSIGN_MIN_BODY_OVERLAP_XH * xh)))
        ids, base, distance = ids[keep], base[keep], distance[keep]
        score = distance / xh + ASSIGN_HORIZONTAL_COST * gap[ids] / xh
        score -= np.isin(q[ids, 5], list(m['ids'])) * ASSIGN_SEED_BONUS
        # Preserve model order and strict tie-breaking. Within a seed extent
        # _blocked samples one column; evaluate those identical three pixels in
        # a batch. Components outside the extent keep the full corridor test.
        keep = score < best[ids]
        ids, base, score = ids[keep], base[keep], score[keep]
        edge = np.clip(cx[ids], m['a'], m['b'] - 1)
        internal = cx[ids] == edge
        blocked = np.zeros(len(ids), bool)
        at = np.flatnonzero(internal)
        columns = cx[ids[at]].astype(int)
        y = base[at] - BARRIER_BODY_CENTRE_XH * xh
        for dy in (-BARRIER_BODY_RADIUS_XH * xh, 0, BARRIER_BODY_RADIUS_XH * xh):
            rows = np.clip(np.rint(y + dy).astype(int), 0, p.gray.shape[0] - 1)
            blocked[at] |= p.barriers[rows, columns]
        for l, t0, r, bottom in p.gutters:
            if bottom-t0 == p.gray.shape[0] or r-l > WIDE_GUTTER_XH*xh:
                blocked[at] |= (columns < r) & (columns+1 > l) & (t0 <= y) & (y < bottom)
        for k in np.flatnonzero(~internal):
            qi = ids[k]
            blocked[k] = _blocked(p, min(cx[qi], edge[k]), max(cx[qi], edge[k]) + 1, float(base[k]), xh)
        keep = ~blocked
        best[ids[keep]], assigned[ids[keep]] = score[keep], j
    # Detached accents/subscripts follow the nearest physical letter, not the
    # nearest line centre. The latter sends high accents to the previous line.
    q = p.components
    body = np.flatnonzero((q[:, 3] - q[:, 1] >= ASSIGN_BODY_HEIGHT_XH * p.xheight)
                         & (q[:, 4] >= SEED_BODY_AREA_XH2 * p.xheight ** 2) & (assigned >= 0))
    if len(body):
        centres = (q[:, :2] + q[:, 2:4]) / 2
        tree = cKDTree(centres[body])
        for k in np.flatnonzero(q[:, 3] - q[:, 1] < ASSIGN_BODY_HEIGHT_XH * p.xheight):
            _, near = tree.query(centres[k], k=min(12, len(body)))
            options = []
            for n in body[np.atleast_1d(near)]:
                j = assigned[n]; xh = models[j]['xh']
                if q[k, 6] > faint_level and not models[j].get('faint', False):
                    continue
                dx = max(q[k, 0] - q[n, 2], q[n, 0] - q[k, 2], 0)
                dy = max(q[k, 1] - q[n, 3], q[n, 1] - q[k, 3], 0)
                if dx <= MARK_BODY_HORIZONTAL_REACH_XH * xh and dy <= MARK_BODY_VERTICAL_REACH_XH * xh:
                    options.append((2 * dx + dy, int(j)))
            if options:
                assigned[k] = min(options)[1]
    return [np.flatnonzero(assigned == j).tolist() for j in range(len(models))]


def _make_lines(p, models, owners, hints):
    lines = []
    for i, (m, ids) in enumerate(zip(models, owners)):
        if not ids:
            continue
        q = p.components[ids]
        xh = m['xh']
        bodies = q[(q[:, 3] - q[:, 1] >= FINAL_BODY_HEIGHT_XH * xh) & (q[:, 4] >= ASSIGN_BODY_AREA_XH2 * xh * xh)]
        if not len(bodies):
            continue
        a, b = int(q[:, 0].min()), int(q[:, 2].max())
        grid = np.arange(a, b)
        base = _at(m, grid)
        topoff, botoff = FINAL_TOP_SEARCH_XH*xh, FINAL_BOTTOM_SEARCH_XH*xh
        # Stop on the final curve, including the whole font band. No subsequent
        # geometry operation can extend across a detected rule / gutter.
        safe = np.ones(len(grid), bool)
        for dy in np.linspace(-topoff, botoff, max(3, round((topoff + botoff) / max(1, FINAL_SEARCH_STEP_XH * xh)))):
            y = np.clip(np.rint(base + dy).astype(int), 0, p.gray.shape[0] - 1)
            safe &= ~p.barriers[y, grid]
        for l, t, r, bot in p.gutters:
            if bot-t < p.gray.shape[0] and r-l <= WIDE_GUTTER_XH*xh:
                continue
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
                                     np.maximum(0, bs - topoff - FINAL_INITIAL_PADDING_XH * xh),
                                     np.minimum(p.gray.shape[0], bs + botoff + FINAL_INITIAL_PADDING_XH * xh), xh,
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
        keep = ((q[:, 3] - q[:, 1] > ANCHOR_MIN_HEIGHT_XH * xh) & (q[:, 3] - q[:, 1] < ANCHOR_MAX_HEIGHT_XH * xh)
                & (q[:, 2] - q[:, 0] > ANCHOR_MIN_WIDTH_XH * xh) & (q[:, 2] - q[:, 0] < ANCHOR_MAX_WIDTH_XH * xh)
                & (q[:, 4] > ASSIGN_BODY_AREA_XH2 * xh * xh))
        q = q[keep]
        x, y = (q[:, 0] + q[:, 2]) / 2, q[:, 3]
        residual = y - _at(m, x)
        near = abs(residual) < ANCHOR_RESIDUAL_LIMIT_XH * xh
        x, y, residual = x[near], y[near], residual[near]
        if len(x) < 8:
            continue
        density = np.maximum(0, 1 - (abs(residual[:, None] - residual[None, :]) / (ANCHOR_MODE_RADIUS_XH * xh)) ** 2)
        accepted = []
        for cx, value in zip(x, residual):
            weight = np.maximum(0, 1 - (abs(x - cx) / (ANCHOR_HORIZONTAL_REACH_XH * xh)) ** 2)
            mode = residual[np.argmax((density * weight[None, :]).sum(axis=1))]
            accepted.append(abs(value - mode) < ANCHOR_ACCEPT_RADIUS_XH * xh)
        accepted = np.array(accepted)
        if accepted.sum() >= 8:
            m['support'] = np.column_stack((x[accepted], y[accepted]))
    _pool_geometry(models)


def _line_contrast(p, lines):
    """Darkest fifth of owned ink, relative to page print AND local paper."""
    values = []
    for line in lines:
        y0 = max(0, int(line.top.min()-line.xheight))
        y1 = min(p.gray.shape[0], int(line.bottom.max()+line.xheight))
        region = p.gray[y0:y1, line.x0:line.x1]
        mask = np.isin(p.labels[y0:y1, line.x0:line.x1], line.component_ids)
        ink = region[mask]
        paper = float(np.percentile(region, 90)) if region.size else 255.
        darkness = float(np.percentile(ink, 10)) if ink.size else paper
        values.append(max(0., paper-darkness))
    strong = [v for v, line in zip(values, lines) if line.support >= 8]
    reference = float(np.percentile(strong or values or [1], 70))
    for line, contrast in zip(lines, values):
        line.contrast = contrast/max(1., reference)
        if line.contrast < DISCOUNT_MIN_CONTRAST_SHARE:
            line.discounted = 'faint ink relative to page text and local paper'


def _split_contrast_runs(p, lines):
    """Separate a coherent faint tail from dark text before contrast scoring.

    Use letter-sized components, not detached marks. A spatial change must
    explain two internally consistent groups with a large photometric gap;
    isolated light letters and uniformly faded lines are left intact.
    """
    rows=[]
    for line in lines:
        q=p.components[np.isin(p.components[:,5],line.component_ids)]
        xh=line.xheight
        body=q[(q[:,3]-q[:,1]>ASSIGN_BODY_HEIGHT_XH*xh)&(q[:,3]-q[:,1]<FAINT_BODY_MAX_HEIGHT_XH*xh)
               &(q[:,2]-q[:,0]<FAINT_BODY_MAX_WIDTH_XH*xh)&(q[:,4]>FAINT_BODY_MIN_AREA_XH2*xh*xh)]
        if len(body)<6:
            rows.append(line);continue
        body=body[np.argsort(body[:,0])]
        top=max(0,int(line.top.min()-xh));bottom=min(p.gray.shape[0],int(line.bottom.max()+xh))
        paper=float(np.percentile(p.gray[top:bottom,line.x0:line.x1],90))
        contrast=np.maximum(0,paper-body[:,6])
        strong=float(np.percentile(contrast,85))
        proposals=[]
        for split in range(3,len(body)-2):
            left,right=body[:split],body[split:]
            if min(np.ptp(left[:,0]),np.ptp(right[:,0]))<FAINT_CLUSTER_MIN_SPAN_XH*xh:
                continue
            a,b=contrast[:split],contrast[split:]
            dark,light=(a,b) if np.median(a)>np.median(b) else (b,a)
            if (np.percentile(light,80)<FAINT_LIGHT_CONTRAST_SHARE*strong and np.percentile(dark,20)>FAINT_DARK_CONTRAST_SHARE*strong
                    and np.median(light)<FAINT_CLUSTER_CONTRAST_RATIO*np.median(dark)):
                # Do not cut through a connected letter or ligature.
                l,r=float(left[:,2].max()),float(right[:,0].min())
                if l<=r:
                    error=float(np.abs(a-np.median(a)).sum()+np.abs(b-np.median(b)).sum())
                    proposals.append((error,(l+r)/2))
        if not proposals:
            rows.append(line);continue
        cut=min(proposals)[1]
        for own in (q[(q[:,0]+q[:,2])/2<cut],q[(q[:,0]+q[:,2])/2>=cut]):
            if not len(own):continue
            a,b=max(line.x0,int(own[:,0].min())),min(line.x1,int(own[:,2].max()))
            if b<=a:continue
            part=copy.copy(line);part.x0=a;part.x1=b
            for name in CURVES:setattr(part,name,getattr(line,name)[a-line.x0:b-line.x0].copy())
            part.component_ids=tuple(own[:,5].astype(int))
            part.support=min(line.support,len(own))
            rows.append(part)
    return rows


def _discount_nontext(p, lines):
    """Reject unsupported punctuation bands and repeated solid non-letter ink.

    Repetition alone is not a veto: rows of digits and letter-spaced headings
    have both repeated shapes and regular spacing. Require either almost no
    letter evidence or a dense, uniform run without typographic variation.
    """
    for line in lines:
        counts = line.ink_classes
        bodies = sum(counts.get(k, 0) for k in
                     ('body_on_baseline', 'body_with_descender', 'tall_body'))
        total = sum(counts.values())
        reason = None
        if not bodies:
            reason = 'no letter bodies'
        elif (total >= 12 and bodies < GRAPHIC_MAX_BODY_SHARE*total and line.support < GRAPHIC_MAX_SUPPORT_SHARE*total
              and not counts.get('mark_above', 0)):
            reason = 'non-text: almost no letter bodies in component band'
        elif line.support < 3 and line.x1-line.x0 > UNSUPPORTED_LINE_WIDTH_XH*line.xheight:
            reason = 'non-text: incoherent component band'
        q = p.components[np.isin(p.components[:,5], line.component_ids)]
        if len(q) >= 10 and not counts.get('mark_above',0):
            q = q[np.argsort(q[:,0])]
            wh = q[:,2:4]-q[:,:2]
            fill = q[:,4]/np.prod(wh,axis=1)
            pitch = np.diff((q[:,0]+q[:,2])/2)
            regular = all(np.std(v)/max(1.,np.mean(v)) < PATTERN_MAX_VARIATION
                          for v in (wh[:,0],wh[:,1],pitch))
            if regular and np.median(fill) > PATTERN_MIN_FILL and np.median(wh[:,0]) > PATTERN_MIN_WIDTH_XH*line.xheight:
                reason = 'non-text: repeated dense non-letter shapes'
        if reason:
            line.discounted = line.discounted or reason
    bands = [l for l in lines if l.discounted and 'non-text' in l.discounted
             and l.x1-l.x0 > GRAPHIC_LINE_WIDTH_XH*l.xheight]
    for line in lines:
        if line.discounted or sum(line.ink_classes.get(k,0) for k in
                ('body_on_baseline','body_with_descender','tall_body')) > 2:
            continue
        for band in bands:
            gap=max(line.x0-band.x1,band.x0-line.x1,0)
            if gap < line.xheight and abs(np.median(line.baseline)-np.median(band.baseline)) < DISCOUNT_NEIGHBOUR_SLACK_XH*line.xheight:
                line.discounted='non-text: fragment of unsupported ornament band'
                break


def _extended(line, name, xs):
    values = getattr(line, name)
    grid = np.arange(line.x0, line.x1)
    n = min(len(grid)-1, max(1, round(LINE_END_FIT_XH*line.xheight)))
    out = np.interp(xs, grid, values)
    if n:
        left = np.clip((values[n]-values[0])/n, -LINE_END_MAX_SLOPE, LINE_END_MAX_SLOPE)
        right = np.clip((values[-1]-values[-1-n])/n, -LINE_END_MAX_SLOPE, LINE_END_MAX_SLOPE)
        out = np.where(xs < line.x0, values[0]+left*(xs-line.x0), out)
        out = np.where(xs >= line.x1, values[-1]+right*(xs-line.x1+1), out)
    return out


def _boundaries(lines, height, width, pixels=None):
    """Stable column neighbours, smooth shared seams and local ink ownership.

    Seams extend through a short neighbour's ends: a neighbour disappearing at
    one x no longer produces a vertical spike. Distant paragraphs/pictures do
    not enlarge the ordinary font margin.
    """
    lookup = {int(q[5]): q for q in pixels.components} if pixels is not None else {}
    for line in lines:
        line.neighbours = {k: np.full(line.x1-line.x0, -1, int) for k in ('above', 'below')}
        line.neighbours.update(left=None, right=None)
        xh = line.xheight
        line.top = np.maximum(0, np.minimum(line.accent_top, line.font_top)-ENVELOPE_GUIDE_PADDING_XH*xh)
        line.bottom = np.minimum(height, line.font_bottom+ENVELOPE_GUIDE_PADDING_XH*xh)
        # Ink envelope follows the shape, with a smooth margin; extrema affect
        # the region only, never the font guides.
        rises, drops = [], []
        for k in line.component_ids:
            q = lookup.get(k)
            if q is None:
                continue
            bs = float(np.interp((q[0]+q[2])/2, np.arange(line.x0,line.x1), line.baseline))
            rises.append(bs-q[1]); drops.append(q[3]-bs)
        if rises:
            line.top = np.maximum(0, line.baseline-max(max(rises)+ENVELOPE_INK_PADDING_XH*xh, ENVELOPE_MIN_RISE_XH*xh))
            line.bottom = np.minimum(height, line.baseline+max(max(drops)+ENVELOPE_INK_PADDING_XH*xh, ENVELOPE_MIN_DROP_XH*xh))
    active = [i for i,l in enumerate(lines) if l.discounted is None]
    pairs = set()
    for i in active:
        a = lines[i]
        choices = []
        for j in active:
            if i == j:
                continue
            b = lines[j]
            lo, hi = max(a.x0,b.x0), min(a.x1,b.x1)
            if hi <= lo:
                continue
            xs = np.linspace(lo, hi-1, 5)
            delta = np.median(_extended(b, 'baseline', xs)-_extended(a, 'baseline', xs))
            if 0 < delta < SEAM_NEIGHBOUR_REACH_XH*max(a.xheight,b.xheight):
                choices.append((delta,j))
        if choices:
            pairs.update((i,j) for _,j in choices)
    seams_above = {i: [] for i in active}
    seams_below = {i: [] for i in active}
    for i,j in sorted(pairs, key=lambda ij: np.median(lines[ij[0]].baseline)):
        a,b = lines[i],lines[j]
        lo,hi = min(a.x0,b.x0),max(a.x1,b.x1)
        xs = np.arange(lo,hi)
        overlap = np.arange(max(a.x0,b.x0),min(a.x1,b.x1))
        def extend(line, name):
            other = b if line is a else a
            value = _extended(line,name,xs)
            shift = np.median(_extended(line,name,overlap)-_extended(other,'baseline',overlap))
            return np.where((xs<line.x0)|(xs>=line.x1),_extended(other,'baseline',xs)+shift,value)
        seam = (extend(a,'font_bottom')+extend(b,'accent_top'))/2
        # Smoothly route around the owned component extents where feasible.
        lower = extend(a,'baseline')+SEAM_GUIDE_CLEARANCE_XH*a.xheight
        upper = extend(b,'meanline')-SEAM_GUIDE_CLEARANCE_XH*b.xheight
        for line, edge, target in ((a,3,lower),(b,1,upper)):
            for k in line.component_ids:
                q = lookup.get(k)
                if q is None:
                    continue
                aa,bb=max(lo,int(q[0])),min(hi,int(q[2]))
                if bb<=aa:
                    continue
                sl=slice(aa-lo,bb-lo)
                if edge==3:
                    target[sl]=np.maximum(target[sl],q[edge]+PIXEL_EDGE_HALF_STEP)
                else:
                    target[sl]=np.minimum(target[sl],q[edge]-PIXEL_EDGE_HALF_STEP)
        radius=max(1,round(SEAM_FILTER_RADIUS_XH*min(a.xheight,b.xheight)))
        lower=ndi.gaussian_filter1d(ndi.maximum_filter1d(lower,2*radius+1),radius)
        upper=ndi.gaussian_filter1d(ndi.minimum_filter1d(upper,2*radius+1),radius)
        feasible=lower<=upper
        seam=np.where(feasible,np.maximum(lower,np.minimum(upper,seam)),(lower+upper)/2)
        seam=ndi.gaussian_filter1d(seam,max(1.,SEAM_SMOOTHING_XH*min(a.xheight,b.xheight)))
        ai=slice(a.x0-lo,a.x1-lo); bi=slice(b.x0-lo,b.x1-lo)
        # Only neighbours close enough to meet need a seam. Applying it to both
        # sides keeps the non-overlap invariant, including short final lines.
        seams_below[i].append(seam[ai]); seams_above[j].append(seam[bi])
        left,right=max(a.x0,b.x0),min(a.x1,b.x1)
        if right>left:
            a.neighbours['below'][left-a.x0:right-a.x0]=j
            b.neighbours['above'][left-b.x0:right-b.x0]=i
    for i in active:
        if seams_below[i]:
            lines[i].bottom = np.clip(np.min(seams_below[i],axis=0),0,height)
        if seams_above[i]:
            lines[i].top = np.clip(np.max(seams_above[i],axis=0),0,height)
    # The serialized addresses name the nearest actually present neighbour,
    # even where a short line's extent ends. Geometry above remains smooth.
    for line in lines:
        line.neighbours['above'].fill(-1); line.neighbours['below'].fill(-1)
    starts,ends={},{}
    for i in active:
        starts.setdefault(lines[i].x0,[]).append(i)
        ends.setdefault(lines[i].x1,[]).append(i)
    present=set()
    for x in range(width):
        present.difference_update(ends.get(x,())); present.update(starts.get(x,()))
        order=sorted(present,key=lambda i:lines[i].baseline[x-lines[i].x0])
        for i,j in zip(order,order[1:]):
            if (i,j) in pairs:
                lines[i].neighbours['below'][x-lines[i].x0]=j
                lines[j].neighbours['above'][x-lines[j].x0]=i
    # Discounted records are diagnostics, not tessellation neighbours or OCR.
    for i,a in enumerate(lines):
        for side in ('left','right'):
            choices=[]
            for j,b in enumerate(lines):
                gap=a.x0-b.x1 if side=='left' else b.x0-a.x1
                if j!=i and gap>=0 and abs(np.median(a.baseline)-np.median(b.baseline))<LATERAL_BASELINE_SLACK_XH*max(a.xheight,b.xheight):
                    choices.append((gap,j))
            if choices:
                a.neighbours[side]=min(choices)[1]


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
            if gap < 0 or gap > JOIN_MAX_GAP_XH * max(a.xheight, b.xheight):
                continue
            if not JOIN_MIN_SIZE_RATIO <= b.xheight / a.xheight <= JOIN_MAX_SIZE_RATIO:
                continue
            if abs(a.baseline[-1] - b.baseline[0]) > JOIN_BASELINE_SLACK_XH * min(a.xheight, b.xheight):
                continue
            middle = np.linspace(a.baseline[-1], b.baseline[0], gap + 2)[1:-1]
            if any(_blocked(p, a.x1, b.x0, middle + dy * a.xheight, a.xheight) for dy in (-JOIN_BARRIER_OFFSET_XH, 0, JOIN_BARRIER_OFFSET_XH)):
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
            a.top = np.maximum(0, a.font_top - JOIN_ENVELOPE_PADDING_XH * xh)
            a.bottom = np.minimum(p.gray.shape[0], a.font_bottom + JOIN_ENVELOPE_PADDING_XH * xh)
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
            if not peers or abs(np.median(line.baseline) - np.median(peers[-1].baseline)) > ROW_GROUP_BASELINE_SLACK_XH * line.xheight:
                row += 1; peers = []
            peers.append(line)
            line.segment_positions += ((j, row, len(peers) - 1),)


def _final_columns(lines):
    """Address final extents, widest text first, so indents do not invent lanes.

    Discovery seed lanes can differ on either side of a drop capital. Once
    those seeds have been forgotten, the full paragraph establishes the lane
    for its short/indented lines. Page stops already bound every final extent.
    """
    spans=[]
    assigned={}
    for i in sorted(range(len(lines)),key=lambda i:(lines[i].discounted is not None,
                                                  -(lines[i].x1-lines[i].x0))):
        line=lines[i]
        options=[]
        for j,(a,b) in enumerate(spans):
            overlap=min(b,line.x1)-max(a,line.x0)
            if overlap>HINT_OVERLAP_SHARE*min(b-a,line.x1-line.x0):
                options.append((overlap,j))
        if options:
            j=max(options)[1]
        else:
            j=len(spans);spans.append((line.x0,line.x1))
        assigned[i]=j
    order={j:k for k,j in enumerate(sorted(range(len(spans)),key=lambda j:spans[j][0]))}
    for i,line in enumerate(lines):
        line.column=order[assigned[i]]


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
            if a - right > RIBBON_SPLIT_GAP_XH * xh:
                gaps.append((a - right, (a + right) / 2))
            right = max(right, b)
        if gaps:
            split = max(gaps)[1]
            first = [l for l in lines if (float(l.font_bottom.max()) if axis == 'y' else l.x1) <= split]
            second = [l for l in lines if (float(l.font_top.min()) if axis == 'y' else l.x0) >= split]
            if first and second and len(first) + len(second) == len(lines):
                return _reading_order(first) + _reading_order(second)
    return sorted(lines, key=lambda l: (l.column, float(np.median(l.baseline)), l.x0))


def _diagnostic_pairs(lines):
    """Conservative broad phase for the existing overlap/lateral pair checks.

    A pair is omitted only when scalar bounds prove the original predicate
    false. Remaining indices keep their original order; curves and barrier
    predicates are still tested below, without approximations.
    """
    ids = np.array([i for i, line in enumerate(lines) if line.discounted is None], int)
    active = [lines[i] for i in ids]
    left = np.array([l.x0 for l in active])
    right = np.array([l.x1 for l in active])
    top = np.array([np.min(l.top) for l in active])
    bottom = np.array([np.max(l.bottom) for l in active])
    xh = np.array([l.xheight for l in active])
    start = np.array([l.baseline[0] for l in active])
    end = np.array([l.baseline[-1] for l in active])
    pairs = {}
    for k, i in enumerate(ids):
        overlap = np.minimum(right[k], right) - np.maximum(left[k], left)
        height = np.minimum(bottom[k], bottom) - np.maximum(top[k], top)
        # Negated rejection retains non-finite candidates for the old checks.
        vertical = ~(height <= GEOMETRY_COMPARISON_EPSILON_PX)
        gap = np.maximum(left[k], left) - np.minimum(right[k], right)
        delta = np.where(left[k] < left, abs(end[k]-start), abs(end-start[k]))
        lateral = (~(gap > JOIN_MAX_GAP_XH*np.maximum(xh[k], xh))
                   & ~(delta > JOIN_BASELINE_SLACK_XH*np.minimum(xh[k], xh)))
        pairs[int(i)] = ids[(ids > i) & np.where(overlap > 0, vertical, lateral)]
    return pairs


def _diagnostics(p, lines):
    cuts, foreign, crossings, overlaps, broken = [], [], [], [], []
    strip_edges, boundary_cuts, invalid = [], [], []
    owned_ink, clipped_ink = 0, 0
    threshold = float(np.percentile(p.gray[p.ink], 75)) if p.ink.any() else 128
    cc_by_id = {int(q[5]): q for q in p.components}
    pairs = _diagnostic_pairs(lines)
    owners = {k: i for i, line in enumerate(lines) if line.discounted is None for k in line.component_ids}
    for i, line in enumerate(lines):
        if line.discounted is not None:
            continue
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
                       | (yy - line.baseline[ix] < -STRIP_INK_TOP_XH * (line.baseline[ix]-line.meanline[ix]))
                       | (yy - line.baseline[ix] >= STRIP_INK_BOTTOM_XH * (line.baseline[ix]-line.meanline[ix])))
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
        for j in pairs[i]:
            j = int(j)
            b = lines[j]
            if b.discounted is not None:
                continue
            lo, hi = max(line.x0, b.x0), min(line.x1, b.x1)
            if hi > lo:
                ai, bi = slice(lo - line.x0, hi - line.x0), slice(lo - b.x0, hi - b.x0)
                if np.any(np.minimum(line.bottom[ai], b.bottom[bi]) - np.maximum(line.top[ai], b.top[bi]) > GEOMETRY_COMPARISON_EPSILON_PX):
                    overlaps.append([i, j])
                continue
            left, right = (line, b) if line.x0 < b.x0 else (b, line)
            gap = right.x0 - left.x1
            if gap > JOIN_MAX_GAP_XH * max(left.xheight, right.xheight):
                continue
            if abs(left.baseline[-1] - right.baseline[0]) > JOIN_BASELINE_SLACK_XH * min(left.xheight, right.xheight):
                continue
            if not _blocked(p, left.x1, right.x0, float((left.baseline[-1] + right.baseline[0]) / 2), left.xheight):
                broken.append([i, j])
    multi = sum(sum(j in line.segment_indices for line in lines) > 1 for j in range(len(p.boxes)))
    active = [(i,l) for i,l in enumerate(lines) if l.discounted is None]
    no_bodies = [i for i,l in active if not sum(l.ink_classes.get(k,0) for k in
                                              ('body_on_baseline','body_with_descender','tall_body'))]
    close_pairs = []
    for column in sorted({l.column for _,l in active}):
        rows = sorted([(i,l) for i,l in active if l.column==column], key=lambda r: np.median(r[1].baseline))
        spacings = [np.median(b.baseline)-np.median(a.baseline) for (_,a),(_,b) in zip(rows,rows[1:])
                    if max(a.x0,b.x0)<min(a.x1,b.x1)]
        pitch = float(np.median([v for v in spacings if v>PITCH_MIN_XH*p.xheight])) if any(v>PITCH_MIN_XH*p.xheight for v in spacings) else PITCH_DEFAULT_XH*p.xheight
        for (i,a),(j,b) in zip(rows,rows[1:]):
            if max(a.x0,b.x0)<min(a.x1,b.x1) and np.median(b.baseline)-np.median(a.baseline)<PITCH_MIN_SEPARATION_SHARE*pitch:
                close_pairs.append([i,j])
    jumps = [dict(line=i, top=float(np.max(abs(np.diff(l.top)),initial=0)/l.xheight),
                  bottom=float(np.max(abs(np.diff(l.bottom)),initial=0)/l.xheight)) for i,l in active]
    unassigned = [q for q in p.components if int(q[5]) not in owners and ASSIGN_BODY_HEIGHT_XH*p.xheight<=q[3]-q[1]<=UNASSIGNED_MAX_HEIGHT_XH*p.xheight
                  and ASSIGN_BODY_AREA_XH2*p.xheight**2<=q[UNASSIGNED_MAX_AREA_XH2]<=UNASSIGNED_MAX_AREA_XH2*p.xheight**2]
    nontext_hits=[]
    for i,l in active:
        if any(l.x0<b and l.x1>a and t<np.median(l.baseline)<bot for a,t,b,bot in p.nontext_boxes):
            nontext_hits.append(i)
    seam_gaps=[]
    for i,l in active:
        for j in np.unique(l.neighbours['below']):
            if j<0:
                continue
            xs=np.flatnonzero(l.neighbours['below']==j)
            lower=lines[j]
            delta=lower.top[xs+l.x0-lower.x0]-l.bottom[xs]
            if np.max(delta,initial=0)>GEOMETRY_COMPARISON_EPSILON_PX:
                seam_gaps.append(dict(above=i,below=int(j),maximum_xh=float(delta.max()/l.xheight)))
    checks = {
        '1_font_and_accent_lines': dict(per_line=[dict(line=i, borrowed=list(l.borrowed), distances=l.guide_residuals) for i,l in enumerate(lines)],
                                       borrowed_lines=sum(bool(l.borrowed) for _,l in active)),
        '2_extra_lines': dict(no_body_lines=no_bodies, close_pairs=close_pairs),
        '3_cutoffs': dict(lines=cuts, source_boundary_lines=boundary_cuts, strip_edge_lines=strip_edges),
        '4_faint_detections': dict(discounted=sum(l.discounted is not None for l in lines),
                                   per_line=[dict(line=i,contrast=l.contrast,discounted=l.discounted) for i,l in enumerate(lines)]),
        '5_smoothness': dict(per_line=jumps, maximum=max([max(v['top'],v['bottom']) for v in jumps]+[0.])),
        '6_column_crossings': dict(lines=crossings, full_height_boundaries=[list(g) for g in p.gutters if g[1]==0 and g[3]==p.gray.shape[0]],
                                  all_boundaries=[list(g) for g in p.gutters], continued_rules=p.column_boundaries),
        '7_missed_text': dict(unassigned_text_size_components=len(unassigned), unassigned_text_size_ink=int(sum(q[4] for q in unassigned)),
                              rule_mask_fraction=float(p.barriers.mean())),
        '8_nontext_ink': dict(candidate_lines_on_detected_graphics=nontext_hits, detected_graphics=[list(map(int,b)) for b in p.nontext_boxes],
                             stamp_truncation='Requires visual review; no independent stamp/text labels'),
        '9_headings': dict(possible_broken_pairs=broken),
        '10_existing_checks': dict(foreign_lines=foreign, overlap_pairs=overlaps, broken_pairs=broken, seam_gaps=seam_gaps),
    }
    return dict(checks=checks, active_lines=len(active), discounted_lines=len(lines)-len(active), pixel_segments=len(p.boxes), final_lines=len(lines), multi_line_segments=multi,
                cut_ink_lines=len(cuts), foreign_ink_lines=len(foreign), rule_gutter_crossings=len(crossings),
                boundary_overlaps=len(overlaps), broken_line_pairs=len(broken),
                cut_line_indices=cuts, foreign_line_indices=foreign, crossing_line_indices=crossings,
                overlap_pairs=overlaps, broken_pairs=broken,
                strip_edge_touch_lines=len(strip_edges), strip_edge_indices=strip_edges,
                source_boundary_cut_lines=len(boundary_cuts), invalid_boundary_lines=invalid,
                assigned_ink_pixels=owned_ink, cut_assigned_ink_pixels=clipped_ink,
                assigned_ink_retained_fraction=1 - clipped_ink / max(1, owned_ink),
                unassigned_body_components=int(sum(int(q[5]) not in owners and q[3] - q[1] >= ASSIGN_BODY_HEIGHT_XH * p.xheight
                                                   and q[4] >= SEED_BODY_AREA_XH2 * p.xheight ** 2 for q in p.components)),
                measurement='Pixel/component diagnostics; ownership is inferred, not independent ground truth.')


def segment_page(page: Image.Image | NDArray[Any], hints: Sequence[Sequence[float]] | None = None) -> PageSegmentation:
    """Analyse pixels and return rough segments, final lines, and diagnostic counts."""
    boxes = np.asarray([] if hints is None else hints, float)
    if boxes.size and (boxes.ndim != 2 or boxes.shape[1] != 4 or not np.isfinite(boxes).all()
                       or np.any(boxes[:, 2:] <= boxes[:, :2])):
        raise ValueError('hints must be finite positive-area (x0,y0,x1,y1) boxes')
    boxes = boxes.reshape(-1, 4)
    p = prepare_pixels(page)
    models = _reject_residual_bands(_merge(p, _recover_bodies(p, _discover(p))))
    reference = float(np.percentile(p.components[:, 6], 25)) if len(p.components) else 0
    paper = float(np.percentile(p.gray, 90))
    for m in models:
        own = p.components[np.isin(p.components[:, 5], list(m['body_ids']))]
        m['faint'] = bool(len(own) and paper-np.median(own[:, 6]) < FAINT_CONTRAST_SHARE*(paper-reference))
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
    lines = _split_contrast_runs(p, lines)
    _line_contrast(p, lines)
    fit_guides(p, lines)
    _discount_nontext(p, lines)
    _final_columns(lines)
    lines = _reading_order(lines)
    _boundaries(lines, *p.gray.shape, pixels=p)
    _addresses(lines, p.boxes)
    result = PageSegmentation(lines, p.boxes, p.xheight, _diagnostics(p, lines), p)
    from .structure import _attach_structure
    _attach_structure(result)
    return result


def page_line_segments(page: Image.Image | NDArray[Any], hints: Sequence[Sequence[float]] | None = None) -> list[LineSegment]:
    """Return one curved segment per detected printed line, starting from pixels."""
    return [line for line in segment_page(page, hints=hints).lines if line.discounted is None]


def extract_line_image(page: Image.Image | NDArray[Any], line: LineSegment, *, xheight: int = 32) -> Image.Image:
    """Unroll raw pixels within the tessellated boundary at a fixed x-height position."""
    if not isinstance(xheight, (int, np.integer)) or xheight <= 0:
        raise ValueError('xheight must be a positive integer')
    return _extract(_gray(page), line, xheight)


def _extract(gray, line, xheight):
    scale = xheight / line.xheight
    width = max(1, int(np.ceil((line.x1 - line.x0) * scale)))
    # Centre-aligned resampling avoids shrinking away the first/last column.
    xs = line.x0 + (np.arange(width) + PIXEL_EDGE_HALF_STEP) / scale - PIXEL_EDGE_HALF_STEP
    xs = np.clip(xs, line.x0, line.x1 - 1)
    grid = np.arange(line.x0, line.x1)
    base = np.interp(xs, grid, line.baseline)
    local_xh = np.interp(xs, grid, line.baseline-line.meanline)
    offsets = (np.arange(STRIP_HEIGHT_XH*xheight)-STRIP_BASELINE_XH*xheight)/xheight
    yy = base[None, :] + offsets[:, None]*local_xh[None, :]
    xx = np.broadcast_to(xs, yy.shape)
    strip = ndi.map_coordinates(gray, [yy, xx], order=1, mode='constant', cval=255)
    top, bottom = np.interp(xs, grid, line.top), np.interp(xs, grid, line.bottom)
    strip[(yy < top) | (yy >= bottom)] = 255
    return Image.fromarray(np.clip(strip, 0, 255).astype(np.uint8))

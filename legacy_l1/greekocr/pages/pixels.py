"""Pixel-only rough regions: graphical stops, persistent gutters, then row valleys.

The boxes are seeds, not OCR crops. A valley need not exist between two curled
lines, so a box can deliberately contain several lines. Lengths below are in
estimated letter heights (or fractions of the page), never a document's pixels.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray
from PIL import Image
from scipy import ndimage as ndi

from ..glyphs.components import EIGHT, _xheight, binarise, to_gray


BINARIZE_WINDOW_PAGE = 0.04  # fraction of shorter page dimension: local paper estimation window.
RULE_SAMPLE_XHEIGHT_PX = 8  # sample pixels per x-height: keep thin rule search independent of scan resolution.
RULE_MAX_SLOPE = 0.12  # page x units per y unit: search near-vertical separators.
CONTINUATION_SLOPE_SAMPLES = 81  # dimensionless samples: resolve long collinear thin rule fragments.
RULE_CLOSE_XH = 0.12  # x-heights: bridge small rule gaps and retain their observed width.
RULE_MAX_WIDTH_XH = 0.55  # x-heights: a wider component can be a glyph or shadow, not a thin rule.
GUTTER_MIN_WIDTH_XH = 1.8  # x-heights: repeated whitespace must exceed an ordinary character gap.
ROW_SIGNAL_ENERGY_FLOOR = 1e-06  # dimensionless normalized ink energy: do not correlate a flat profile.
MIN_XHEIGHT_PIXELS = 3.0  # sample pixels per x-height: numerical floor when no body can be measured.
BINARIZE_MIN_PIXELS = 15  # source pixel samples: minimum odd local-threshold window for small images.
RULE_SLOPE_SAMPLES = 9  # dimensionless samples: cover the coarse rule-opening slope interval.

RULE_MIN_FILL = 0.5  # dimensionless occupied share: thin rule candidates need substantial original ink.
RULE_FRAGMENT_MIN_HEIGHT_XH = 2  # x-heights: exclude short stems before linking separator fragments.
RULE_FRAGMENT_MAX_ASPECT = 0.18  # page x units per y unit: reject broad fragments from straight-rule fitting.
RULE_INTERCEPT_STEP_XH = 0.5  # x-heights: quantize candidate separator intercepts without losing thin fragments.
RULE_INTERCEPT_REACH_XH = 0.75  # x-heights: link fragments around a proposed straight path.
RULE_MIN_COVERAGE_PAGE = 0.3  # fraction of page height: require sustained fragment support.
RULE_MIN_EXTENT_PAGE = 0.5  # fraction of page height: a continued rule must span a substantial page extent.
RULE_MAX_RADIUS_XH = 0.25  # x-heights: cap the corridor used to reconnect a thin rule.
RULE_MIN_CONTINUATION_SUPPORT = 0.5  # dimensionless path share: protect ink-supported continuations only.
HOUGH_HALF_TURN_STEPS = 1800  # angular samples per half-turn: resolve a long thin separator.
HOUGH_ANGULAR_DRIFT_XH = 0.2  # x-heights per page height: bound the end drift of a Hough angular bin.
HOUGH_MIN_LENGTH_XH = 12  # x-heights: suppress individual glyphs and short decorative strokes.
HOUGH_MIN_LENGTH_PAGE = 0.1  # fraction of page height: require a meaningful long-rule candidate.
HOUGH_MAX_GAP_XH = 0.8  # x-heights: bridge local damage in a long printed separator.
RULE_INK_SEARCH_RADIUS_XH = 0.6  # x-heights: inspect original pixels around a proposed separator.
RULE_INK_MAX_WIDTH_XH = 0.65  # x-heights: reject broad letter/graphic ink in the rule corridor.
RULE_MIN_NARROW_SHARE = 0.75  # dimensionless path share: most of a separator must contain narrow ink.
RULE_RADIUS_PADDING_XH = 0.08  # x-heights: preserve antialiased rule edges in the stop mask.
RULE_MIN_PATH_SUPPORT = 0.85  # dimensionless path share: rule stops require continuous original ink.
RULE_MIN_LOCAL_SUPPORT = 0.75  # dimensionless window share: retain sustained sections of a damaged rule.
GUTTER_PROFILE_WINDOW_XH = 0.25  # x-heights: suppress individual-stroke fluctuations before finding whitespace.
GUTTER_INK_COUNT_FLOOR = 0.5  # source pixel-count units: tolerate an isolated antialiased pixel in a blank lane.
GUTTER_MAX_LOCAL_INK_SHARE = 0.24  # dimensionless projection share: a gutter is sparse relative to its band.
GUTTER_VOTE_SMOOTHING_XH = 0.3  # x-heights: consolidate repeated whitespace observations across rows.
GUTTER_MIN_BAND_SHARE = 0.67  # dimensionless band share: require whitespace in most observed rows.
GUTTER_RULE_SUPPORT_PAGE = 0.35  # fraction of page height: retain long barriers as gutter candidates.
GUTTER_NONRULE_MIN_WIDTH_XH = 1.5  # x-heights: whitespace alone needs a wider stop than a printed rule.
GUTTER_MIN_SIDE_INK_SHARE = 0.2  # dimensionless ink share: require meaningful text on each side of a gutter.
GUTTER_INSET_XH = 0.15  # x-heights: test interior whitespace away from adjacent ink.
GAP_PROFILE_WINDOW_XH = 0.3  # x-heights: smooth letter-scale holes before searching local gaps.
GAP_MAX_INK_SHARE = 0.035  # dimensionless projection share: local gaps must be close to blank.
GAP_ROW_CLOSE_XH = 0.6  # x-heights: connect within-body gaps before counting repeated rows.
GAP_ROW_MIN_HEIGHT_XH = 0.5  # x-heights: require substantial text-height evidence beside a gap.
PITCH_PEAK_RADIUS_XH = 0.4  # x-heights: compare candidate autocorrelation peaks with their neighbourhood.
PITCH_FINE_SMOOTHING_XH = 0.15  # x-heights: remove pixel noise from the row profile.
PITCH_COARSE_SMOOTHING_XH = 3  # x-heights: subtract slow page shading before estimating pitch.
PITCH_MIN_XH = 1.5  # x-heights: avoid treating a glyph's own width as row spacing.
PITCH_MAX_XH = 5  # x-heights: constrain the search to neighboring printed rows.
PITCH_MIN_CORRELATION = 0.35  # dimensionless autocorrelation: require repeated vertical structure.
PITCH_MIN_PROMINENCE = 0.12  # dimensionless correlation difference: reject broad or weak local peaks.
BODY_MIN_HEIGHT_PAGE = 0.002  # fraction of page height: remove tiny specks from the type-size estimate.
BODY_MAX_HEIGHT_PAGE = 0.1  # fraction of page height: exclude large graphics from type-size estimation.
BODY_MIN_WIDTH_PAGE = 0.001  # fraction of page width: exclude very narrow sampling artifacts.
BODY_MAX_WIDTH_PAGE = 0.12  # fraction of page width: exclude long frame strokes from type-size estimation.
BODY_MIN_RELATIVE_AREA = 0.15  # dimensionless area share: estimate text ink from substantial components.
STRONG_MIN_CONTRAST_SHARE = 0.55  # dimensionless contrast share: separate strong print from faint residual ink.
FAINT_CLEARANCE_XH = 0.08  # x-heights: do not call antialiased strong-ink fringes separate faint components.
LETTER_MAX_HEIGHT_XH = 4.5  # x-heights: allow marked connected bodies while excluding tall graphics.
LETTER_MIN_WIDTH_XH = 0.35  # x-heights: avoid treating very thin rules as letter-shaped evidence.
LETTER_MAX_WIDTH_XH = 5  # x-heights: preserve short connected words in the letter-shape mask.
LETTER_MAX_AREA_XH2 = 8  # square x-heights: exclude dense illustration components.
COMPONENT_MIN_AREA_XH2 = 0.012  # square x-heights: remove specks before seed grouping.
DARK_MIN_CONTRAST_SHARE = 0.5  # dimensionless contrast share: assess illustrations from meaningful dark ink.
GRAPHIC_CANDIDATE_HEIGHT_XH = 2.5  # x-heights: small components remain available to the text fitter.
GRAPHIC_CANDIDATE_WIDTH_XH = 12  # x-heights: short connected words remain available to the text fitter.
GRAPHIC_MIN_DIMENSION_XH = 3  # x-heights: a dense graphic must exceed an individual body in both axes.
GRAPHIC_MIN_WIDTH_XH = 5  # x-heights: preserve ordinary narrow text components.
GRAPHIC_MIN_FILL = 0.12  # dimensionless occupied area share: reject only substantial dense graphics.
WIDE_GRAPHIC_MIN_WIDTH_XH = 12  # x-heights: wider illustrations may use a lower occupancy threshold.
WIDE_GRAPHIC_MIN_HEIGHT_XH = 2.5  # x-heights: preserve thin horizontal text bands.
WIDE_GRAPHIC_MIN_FILL = 0.09  # dimensionless occupied area share: detect broad sparse illustrations.
LARGE_GRAPHIC_MIN_WIDTH_XH = 20  # x-heights: analyze broad regions separately for text-like rows.
LARGE_GRAPHIC_MIN_HEIGHT_XH = 12  # x-heights: require multiple row heights before the broad-region check.
LARGE_GRAPHIC_MIN_FILL = 0.01  # dimensionless occupied area share: ignore almost-empty large boxes.
GRAPHIC_PROFILE_WINDOW_XH = 0.3  # x-heights: measure sustained row-level graphic ink.
GRAPHIC_PROFILE_MIN_FILL = 0.1  # dimensionless mean row occupancy: require sustained broad ink.
GRAPHIC_MAX_STRAIGHT_SHARE = 0.5  # dimensionless row share: retain regions with substantial straight text-row evidence.
PAGE_TEXT_MIN_HEIGHT_PAGE = 0.7  # fraction of page height: protect large page-spanning text components.
PAGE_TEXT_MIN_WIDTH_PAGE = 0.35  # fraction of page width: recognize broad page-spanning text components.
ILLUSTRATION_CONTEXT_XH = 2.5  # x-heights: inspect neighboring body context around a graphic candidate.
CONTEXT_MIN_ROW_INK_SHARE = 0.025  # dimensionless row-width share: count substantial nearby text ink.
CONTEXT_ROW_CLOSE_XH = 0.8  # x-heights: merge body holes before counting nearby text rows.
RULE_BROAD_INK_WIDTH_XH = 0.65  # x-heights: exclude wide letter ink from proposed separator evidence.
PROTECTED_BODY_HEIGHT_XH = 0.6  # x-heights: prevent clear letter bodies from being erased as rules.
PROTECTED_BODY_AREA_XH2 = 0.08  # square x-heights: protect body-scale ink rather than detached specks.
ROW_PROFILE_WINDOW_XH = 0.25  # x-heights: smooth body-scale projection noise before seeding rows.
LEFT_EDGE_REGION_PAGE = 0.2  # fraction of page width: apply edge-shadow logic only near the left margin.
LEFT_SHADOW_EDGE_PAGE = 0.04  # fraction of page width: a left shadow must touch the scan edge.
SHADOW_MIN_HEIGHT_PAGE = 0.45  # fraction of page height: shadows are long vertical page-edge components.
RIGHT_EDGE_REGION_PAGE = 0.8  # fraction of page width: apply edge-shadow logic only near the right margin.
RIGHT_SHADOW_EDGE_PAGE = 0.96  # fraction of page width: a right shadow must touch the scan edge.
LOCAL_BODY_MIN_AREA_XH2 = 0.07  # square x-heights: estimate local type size from substantial components.
LOCAL_MIN_SIZE_RATIO = 0.45  # x-heights per page x-height: permit smaller local text while excluding specks.
LOCAL_MAX_SIZE_RATIO = 2  # x-heights per page x-height: reject unstable local size estimates.
REGION_RULE_SUPPORT_SHARE = 0.35  # dimensionless region-height share: stop local seeds at sustained barriers.
ROW_INK_COUNT_FLOOR = 0.5  # source pixel-count units: require more than negligible projected ink.
ROW_MIN_PEAK_SHARE = 0.045  # dimensionless projection share: retain weak rows relative to the regional peak.
ROW_ACTIVE_CLOSE_XH = 0.4  # x-heights: fill small gaps in an active vertical text band.
ROW_MIN_AREA_XH2 = 0.15  # square x-heights: do not seed a row from isolated scattered ink.

@dataclass
class PixelPage:
    gray: NDArray
    ink: NDArray
    labels: NDArray
    components: NDArray   # x0, y0, x1, y1, area, label, darkness
    barriers: NDArray
    gutters: list[tuple[int, int, int, int]]
    boxes: list[tuple[int, int, int, int]]
    xheight: float
    nontext_boxes: list = field(default_factory=list)
    column_boundaries: list = field(default_factory=list)
    original_ink: NDArray | None = field(default=None, repr=False)
    original_rules: NDArray | None = field(default=None, repr=False)


RULE_MIN_LENGTH_XH = 3  # x-heights: reject individual short stems from the opened rule mask.
RULE_MIN_ASPECT = 10  # page height per width: separators must be long and thin.
RULE_DUPLICATE_DISTANCE_XH = 2  # x-heights: nearby fragment fits represent the same rule.
RULE_REFIT_MIN_SPAN_XH = 2  # x-heights: slope refinement needs a nontrivial support span.
HOUGH_VOTE_LENGTH_XH = 10  # x-heights: require sustained Hough votes for a long separator.
RULE_EXTENT_SLACK_XH = 2  # x-heights: combine nearly overlapping observations of a finite rule.
RULE_SUPPORT_WINDOW_XH = 4  # x-heights: require sustained local support before extending a rule.
GUTTER_BAND_HEIGHT_XH = 8  # x-heights: collect whitespace votes over several text rows.
GUTTER_MIN_BAND_AREA_XH2 = 2  # square x-heights: a nearly empty band supplies no reliable gutter evidence.
GUTTER_SIDE_CONTEXT_XH = 15  # x-heights: inspect meaningful text context beside a persistent gutter.
GUTTER_MIN_SIDE_AREA_XH2 = 8  # square x-heights: require substantial text ink on both sides of a gutter.
GAP_SIDE_CONTEXT_XH = 12  # x-heights: inspect repeated local rows on each side of a gap.
GAP_MIN_ROW_SPAN_XH = 3  # x-heights: multiple row evidence must span a meaningful vertical extent.
GAP_WIDE_WIDTH_XH = 10  # x-heights: a very wide empty interval is a stop without repeated-row evidence.
PITCH_MIN_HEIGHT_XH = 9  # x-heights: pitch estimation needs several visible rows.
PITCH_MIN_WIDTH_XH = 3  # x-heights: pitch estimation needs a meaningful horizontal text span.
PITCH_WINDOW_STEP_XH = 6  # x-heights: limit overlap of neighboring pitch windows.
PAPER_ESTIMATION_WINDOW_XH = 2  # x-heights: estimate paper from the vicinity of letter bodies.
GRAPHIC_HEIGHT_XH = 4  # x-heights: mark tall non-body components for graphic inspection.
GRAPHIC_WIDTH_XH = 14  # x-heights: inspect very wide connected components as possible graphics.
GRAPHIC_AREA_XH2 = 18  # square x-heights: dense large components need graphic checks.
MOTIF_MAX_HEIGHT_XH = 6  # x-heights: group local decorative components with compatible size.
MOTIF_CONTEXT_XH = 3  # x-heights: include adjacent text context around repeated motifs.
ZONE_MIN_REMAINDER_XH = 18  # x-heights: avoid a short final region when splitting long page bands.
ZONE_SEARCH_START_XH = 12  # x-heights: begin searching for a regional split after several rows.
ZONE_SEARCH_END_XH = 22  # x-heights: cap regional seed height without prescribing a page-specific break.
REGION_RULE_SUPPORT_XH = 3  # x-heights: sustained local barrier ink must stop a seed region.

def _runs(mask):
    mask = np.asarray(mask)
    if mask.dtype == np.bool_ and mask.ndim == 1:
        padded = np.empty(len(mask)+2, bool)
        padded[0] = padded[-1] = False
        padded[1:-1] = mask
        edges = np.flatnonzero(padded[1:] != padded[:-1])
        return [(int(a), int(b)) for a, b in zip(edges[::2], edges[1::2])]
    edges = np.diff(np.r_[False, mask, False].astype(np.int8))
    return [(int(a), int(b)) for a, b in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1))]


def _gray(page: Image.Image | NDArray[Any]) -> NDArray:
    arr = np.asarray(page) if not isinstance(page, Image.Image) else np.asarray(page.convert('L'))
    if arr.ndim not in (2, 3) or (arr.ndim == 3 and arr.shape[2] not in (3, 4)) or not arr.size:
        raise ValueError('page must be a nonempty grayscale or RGB image')
    gray = to_gray(page)
    if not np.isfinite(gray).all() or gray.min() < 0 or gray.max() > 255:
        raise ValueError('page pixels must be finite and in [0,255] or [0,1]')
    if gray.max() <= 1:
        gray = gray * 255
    return gray


def _records(gray, labels):
    sizes = np.bincount(labels.ravel())
    rows = []
    for k, sl in enumerate(ndi.find_objects(labels), 1):
        if sl is None or sizes[k] < 3:
            continue
        y, x = sl
        rows.append((x.start, y.start, x.stop, y.stop, sizes[k], k,
                     float(np.median(gray[sl][labels[sl] == k]))))
    return np.asarray(rows, float).reshape(-1, 7)


def _rect_morphology(mask, shape, *, closing=False):
    """The ndimage rectangular opening/closing with its exact even-size origins."""
    kernel = np.ones(shape, np.uint8)
    source = np.asarray(mask, dtype=np.uint8)
    h, w = shape
    def erode(value):
        return cv2.erode(value, kernel, anchor=(w//2, h//2),
                         borderType=cv2.BORDER_CONSTANT, borderValue=0)
    def dilate(value):
        return cv2.dilate(value, kernel, anchor=((w-1)//2, (h-1)//2),
                          borderType=cv2.BORDER_CONSTANT, borderValue=0)
    return (erode(dilate(source)) if closing else dilate(erode(source))).astype(bool)


def _rule_mask(ink, xh):
    """Thin straight strokes only; close short breaks before testing length.

    Reject wide opened components instead of turning their entire bounding
    rectangle into a stop. In particular, a shadow, stamp or curled letter
    margin is not a rule. The same test works at every page resolution.
    """
    scale = min(1., RULE_SAMPLE_XHEIGHT_PX / xh)
    pooled = ndi.maximum_filter(ink, max(1, int(np.ceil(1 / scale))))
    small = ndi.zoom(pooled.astype(np.uint8), scale, order=0).astype(bool)
    h, w = small.shape
    unit = xh * scale
    rows, cols = np.arange(h)[:, None], np.arange(w)[None, :]
    result = np.zeros_like(small)
    for slope in np.linspace(-RULE_MAX_SLOPE, RULE_MAX_SLOPE, RULE_SLOPE_SAMPLES):
        shift = np.rint(slope * (rows - h / 2)).astype(int)
        xx = cols + shift
        shear = small[rows, np.clip(xx, 0, w - 1)] & (xx >= 0) & (xx < w)
        joined = _rect_morphology(shear, (max(1, round(RULE_CLOSE_XH * unit)), 1), closing=True)
        opened = _rect_morphology(joined, (max(3, round(RULE_MIN_LENGTH_XH * unit)), 1))
        labels, _ = ndi.label(opened)
        thin = np.zeros_like(opened)
        for k, sl in enumerate(ndi.find_objects(labels), 1):
            if sl is None:
                continue
            y, x = sl
            hh, ww = y.stop - y.start, x.stop - x.start
            if ww > RULE_MAX_WIDTH_XH * unit or hh < RULE_MIN_LENGTH_XH * unit or hh < RULE_MIN_ASPECT * ww:
                continue
            if shear[sl].mean() < RULE_MIN_FILL:
                continue
            thin[sl] |= labels[sl] == k
        back = cols - shift
        result |= thin[rows, np.clip(back, 0, w - 1)] & (back >= 0) & (back < w)
    result = ndi.maximum_filter(result, max(1, round(RULE_CLOSE_XH * unit)) | 1)
    ys = np.minimum((np.arange(ink.shape[0]) * scale).astype(int), h - 1)
    xs = np.minimum((np.arange(ink.shape[1]) * scale).astype(int), w - 1)
    return result[ys[:, None], xs]


def _continue_rules(barriers, xh, evidence=None, protected=None):
    """Fit collinear thin pieces in page coordinates, including tilted rules."""
    h,w=barriers.shape
    labels,_=ndi.label(barriers)
    pieces=[]
    for sl in ndi.find_objects(labels):
        if sl is None:
            continue
        y,x=sl
        if y.stop-y.start >= RULE_FRAGMENT_MIN_HEIGHT_XH*xh and x.stop-x.start < max(xh,RULE_FRAGMENT_MAX_ASPECT*(y.stop-y.start)):
            pieces.append(((x.start+x.stop)/2,(y.start+y.stop)/2,y.start,y.stop,x.stop-x.start))
    if not pieces:
        return []
    q=np.array(pieces)
    proposals=[]
    step=max(1.,RULE_INTERCEPT_STEP_XH*xh)
    for slope in np.linspace(-RULE_MAX_SLOPE,RULE_MAX_SLOPE,CONTINUATION_SLOPE_SAMPLES):
        intercept=q[:,0]-slope*(q[:,1]-h/2)
        bins=np.floor(intercept/step).astype(int)
        for bucket in np.unique(bins):
            near=(abs(intercept-(bucket+.5)*step)<RULE_INTERCEPT_REACH_XH*xh)
            own=q[near]
            covered=np.zeros(h,bool)
            for row in own:
                covered[int(row[2]):int(row[3])]=True
            if covered.sum()<RULE_MIN_COVERAGE_PAGE*h or np.ptp(own[:,1])+np.max(own[:,3]-own[:,2])<RULE_MIN_EXTENT_PAGE*h:
                continue
            centre=float(np.median(intercept[near]))
            proposals.append((int(covered.sum()),slope,centre,near))
    result=[]
    for score,slope,centre,near in sorted(proposals,key=lambda v:-v[0]):
        if any(abs(centre-r['centre'])<RULE_DUPLICATE_DISTANCE_XH*xh for r in result):
            continue
        own=q[near]
        if len(own)>=3 and np.ptp(own[:,1])>RULE_MIN_COVERAGE_PAGE*h:
            slope,intercept=np.polyfit(own[:,1]-h/2,own[:,0],1,w=np.sqrt(own[:,3]-own[:,2]))
            centre=float(intercept)
        elif len(own):
            longest=own[np.argmax(own[:,3]-own[:,2])]
            a,b=max(0,int(longest[0]-longest[4]/2)),min(w,int(longest[0]+longest[4]/2)+1)
            t,bot=int(longest[2]),int(longest[3])
            yy,xx=np.nonzero(barriers[t:bot,a:b])
            if len(yy)>2 and np.ptp(yy)>RULE_REFIT_MIN_SPAN_XH*xh:
                slope,centre=np.polyfit(yy+t-h/2,xx+a,1)
        path=centre+slope*(np.arange(h)-h/2)
        radius=max(1.,min(RULE_MAX_RADIUS_XH*xh,float(np.median(own[:,4]))/2))
        top, bottom = 0, h
        intrudes = protected is None
        if protected is not None and len(protected):
            mid = (protected[:,1]+protected[:,3])/2
            px = centre+slope*(mid-h/2)
            intrudes = np.count_nonzero((px > protected[:,0]) & (px < protected[:,2])) >= 3
        if evidence is not None and intrudes:
            # A fitted direction is a proposal, not permission to extend a
            # binding edge through curled letters. Verify support in the
            # original ink, including the spaces between detected fragments.
            rows = np.arange(h)
            support = np.zeros(h, bool)
            for dx in range(-int(np.ceil(radius)), int(np.ceil(radius))+1):
                xx = np.rint(path+dx).astype(int)
                ok = (xx >= 0) & (xx < w)
                support[ok] |= evidence[rows[ok], xx[ok]]
            if support.mean() < RULE_MIN_CONTINUATION_SUPPORT:
                continue
        for dy in range(-int(np.ceil(radius)),int(np.ceil(radius))+1):
            xx=np.rint(path+dy).astype(int); ok=(xx>=0)&(xx<w)
            ok &= (np.arange(h)>=top)&(np.arange(h)<bottom)
            barriers[np.flatnonzero(ok),xx[ok]]=True
        result.append(dict(kind='continued_rule', centre=centre, slope=float(slope),
                           radius=radius, top=top, bottom=bottom, support_rows=score))
    return result


def _direct_rules(ink, xh, existing):
    """Find long oblique strokes without relying on axis-aligned openings.

    The angular resolution is finer than one stroke width over the page.
    Original-resolution row support rejects chance alignments of letter stems.
    These are column stops only over the measured stroke, not page orientation.
    """
    import cv2
    h,w = ink.shape
    scale = min(1., RULE_SAMPLE_XHEIGHT_PX/xh)
    small = ndi.zoom(ndi.maximum_filter(ink, max(1, int(np.ceil(1/scale))))
                     .astype(np.uint8), scale, order=0)
    paths = cv2.HoughLinesP(small, 1, min(np.pi/HOUGH_HALF_TURN_STEPS, HOUGH_ANGULAR_DRIFT_XH*xh/h),
                           threshold=max(2, round(HOUGH_VOTE_LENGTH_XH*xh*scale)),
                           minLineLength=max(HOUGH_MIN_LENGTH_XH*xh, HOUGH_MIN_LENGTH_PAGE*h)*scale,
                           maxLineGap=HOUGH_MAX_GAP_XH*xh*scale)
    if paths is None:
        return []
    found=[]
    for x0,y0,x1,y1 in sorted(paths.reshape(-1,4), key=lambda v:-abs(int(v[3])-int(v[1]))):
        x0,y0,x1,y1 = np.array([x0,y0,x1,y1],float)/scale
        if abs(y1-y0)<HOUGH_MIN_LENGTH_XH*xh or abs(x1-x0)>RULE_MAX_SLOPE*abs(y1-y0):
            continue
        slope=(x1-x0)/(y1-y0);centre=x0+slope*(h/2-y0)
        if any(abs(centre-r['centre'])<xh and min(y0,y1)>=r['top']-RULE_EXTENT_SLACK_XH*xh
               and max(y0,y1)<=r['bottom']+RULE_EXTENT_SLACK_XH*xh for r in existing+found):
            continue
        top,bottom=max(0,round(min(y0,y1))),min(h,round(max(y0,y1))+1)
        yy=np.arange(h);path=centre+slope*(yy-h/2)
        # Refine the Hough quantisation using original-resolution contacts.
        offsets=np.arange(-round(RULE_INK_SEARCH_RADIUS_XH*xh),round(RULE_INK_SEARCH_RADIUS_XH*xh)+1)
        xx=np.rint(path[:,None]+offsets).astype(int)
        sample=ink[yy[:,None],np.clip(xx,0,w-1)] & (xx>=0) & (xx<w)
        count=sample.sum(axis=1)
        own=(count>0)&(count<RULE_INK_MAX_WIDTH_XH*xh)&(yy>=top)&(yy<bottom)
        if own.sum()<RULE_MIN_NARROW_SHARE*(bottom-top):
            continue
        contacts=(sample*xx).sum(axis=1)/np.maximum(1,count)
        slope,centre=np.polyfit(yy[own]-h/2,contacts[own],1)
        # Extend the *evidence* search before fitting the whole stroke. A
        # quantised partial Hough segment otherwise misses its far endpoint.
        for _ in range(2):
            xx=np.rint(centre+slope*(yy[:,None]-h/2)+offsets).astype(int)
            sample=ink[yy[:,None],np.clip(xx,0,w-1)] & (xx>=0) & (xx<w)
            count=sample.sum(axis=1)
            own=(count>0)&(count<RULE_INK_MAX_WIDTH_XH*xh)&(yy>=top-RULE_EXTENT_SLACK_XH*xh)&(yy<bottom+RULE_EXTENT_SLACK_XH*xh)
            contacts=(sample*xx).sum(axis=1)/np.maximum(1,count)
            slope,centre=np.polyfit(yy[own]-h/2,contacts[own],1)
        path=centre+slope*(yy-h/2)
        radius=max(1.,float(np.percentile(count[own],75))/2+RULE_RADIUS_PADDING_XH*xh)
        hits=np.zeros(len(yy),bool)
        for dx in range(-int(np.ceil(radius)),int(np.ceil(radius))+1):
            xx=np.rint(path+dx).astype(int);ok=(xx>=0)&(xx<w)
            hits[ok] |= ink[yy[ok],xx[ok]]
        if hits[top:bottom].mean()<RULE_MIN_PATH_SUPPORT:
            continue
        supported=ndi.uniform_filter1d(hits.astype(float),max(1,round(RULE_SUPPORT_WINDOW_XH*xh)))>RULE_MIN_LOCAL_SUPPORT
        spans=[(a,b) for a,b in _runs(supported) if a<=.5*(top+bottom)<b]
        if spans:
            top,bottom=spans[0]
        found.append(dict(kind='direct_rule',centre=float(centre),slope=float(slope),
                          radius=radius,top=top,bottom=bottom,support_rows=int(hits.sum())))
    return found


def _structural_gutters(clean, barriers, xh):
    """Vote across the page, so a missing rule dash cannot open a column.

    Whitespace must recur in most occupied horizontal bands, with text on
    both sides. A letter gap confined to a heading never earns this vote.
    """
    h, w = clean.shape
    bands = []
    for y in range(0, h, max(1, round(GUTTER_BAND_HEIGHT_XH * xh))):
        band = clean[y:min(h, y + round(GUTTER_BAND_HEIGHT_XH * xh))]
        if band.sum() > GUTTER_MIN_BAND_AREA_XH2 * xh * xh:
            bands.append(band)
    if len(bands) < 3:
        return []
    votes = np.zeros(w)
    for band in bands:
        col = ndi.uniform_filter1d(band.sum(axis=0).astype(float), max(1, round(GUTTER_PROFILE_WINDOW_XH * xh)))
        level = np.percentile(col[col > 0], 75) if np.any(col > 0) else 1
        votes += col < max(GUTTER_INK_COUNT_FLOOR, GUTTER_MAX_LOCAL_INK_SHARE * level)
    lanes = ndi.gaussian_filter1d(votes, max(1., GUTTER_VOTE_SMOOTHING_XH*xh)) >= GUTTER_MIN_BAND_SHARE * len(bands)
    # The rule vote covers its full text height, including short missing dashes.
    rules = barriers.sum(axis=0) > GUTTER_RULE_SUPPORT_PAGE * h
    gutters = []
    for a, b in _runs(lanes | rules):
        is_rule = rules[a:b].any()
        # Persistence across the page, rather than a large local word gap,
        # supplies the column evidence. A one-x-height lane can separate two
        # densely set columns; requiring 1.5 erased such boundaries.
        if a == 0 or b == w or (not is_rule and b-a < xh):
            continue
        left = clean[:, max(0, a-round(GUTTER_SIDE_CONTEXT_XH*xh)):a]
        right = clean[:, b:min(w, b+round(GUTTER_SIDE_CONTEXT_XH*xh))]
        if left.sum() < GUTTER_MIN_SIDE_AREA_XH2*xh*xh or right.sum() < GUTTER_MIN_SIDE_AREA_XH2*xh*xh:
            continue
        if not is_rule and b-a < GUTTER_NONRULE_MIN_WIDTH_XH*xh:
            # Narrow whitespace needs two substantial text blocks, not a
            # repeated indent or a short prefix at the edge of a paragraph.
            # Wider established gutters and printed rules need no such vote.
            if min(clean[:,:a].sum(),clean[:,b:].sum()) < GUTTER_MIN_SIDE_INK_SHARE*clean.sum():
                continue
            inset=max(1,round(GUTTER_INSET_XH*xh))
            a,b=a+inset,b-inset
            if b<=a:
                continue
        gutters.append((a, 0, b, h))
    return gutters


def _gaps(mask, xh):
    """Blank vertical lanes; repeated interline evidence distinguishes word gaps."""
    h, w = mask.shape
    col = ndi.uniform_filter1d(mask.sum(axis=0).astype(float), max(1, round(GAP_PROFILE_WINDOW_XH * xh)))
    if not col.any():
        return []
    low = col <= max(GUTTER_INK_COUNT_FLOOR, GAP_MAX_INK_SHARE * np.percentile(col[col > 0], 85))
    gaps = []
    for a, b in _runs(low):
        if a == 0 or b == w or b - a < GUTTER_MIN_WIDTH_XH * xh:
            continue
        left = mask[:, max(0, a - round(GAP_SIDE_CONTEXT_XH * xh)):a]
        right = mask[:, b:min(w, b + round(GAP_SIDE_CONTEXT_XH * xh))]
        if not left.any() or not right.any():
            continue
        ly, ry = np.flatnonzero(left.any(axis=1)), np.flatnonzero(right.any(axis=1))
        # At least two vertically separated lines on BOTH sides. A single
        # justified line can have a large word space without becoming columns.
        def row_count(block):
            occupied = ndi.maximum_filter1d(block.any(axis=1), max(1,round(GAP_ROW_CLOSE_XH*xh)))
            return sum(bot-top > GAP_ROW_MIN_HEIGHT_XH*xh for top,bot in _runs(occupied))
        repeated = min(np.ptp(ly), np.ptp(ry)) > GAP_MIN_ROW_SPAN_XH*xh and min(row_count(left), row_count(right)) >= 2
        if repeated or b - a >= GAP_WIDE_WIDTH_XH * xh:
            gaps.append((int(a), int(b)))
    return gaps


def _repeated_text_rows(mask, xh):
    """Protect a connected table/frame containing repeated printed rows.

    Different columns may have different row phases, so test overlapping
    horizontal strips as well as the whole region. A broad lighting gradient
    or engraving texture has no prominent peak at a printed line pitch.
    """
    h,w=mask.shape
    if h<PITCH_MIN_HEIGHT_XH*xh or w<PITCH_MIN_WIDTH_XH*xh:
        return False
    step=max(1,round(max(PITCH_WINDOW_STEP_XH*xh,w/3)))
    spans=[(0,w)]+[(a,min(w,a+step)) for a in range(0,w-step//2,max(1,step//2))]
    radius=max(1,round(PITCH_PEAK_RADIUS_XH*xh))
    for a,b in spans:
        profile=mask[:,a:b].mean(axis=1)
        signal=ndi.gaussian_filter1d(profile,max(1.,PITCH_FINE_SMOOTHING_XH*xh))-ndi.gaussian_filter1d(profile,PITCH_COARSE_SMOOTHING_XH*xh)
        if np.dot(signal,signal)<ROW_SIGNAL_ENERGY_FLOOR:
            continue
        correlation=np.correlate(signal,signal,'full')[h-1:]
        correlation/=correlation[0]
        for lag in range(max(radius+1,round(PITCH_MIN_XH*xh)),min(round(PITCH_MAX_XH*xh),h//6)):
            if (correlation[lag]>PITCH_MIN_CORRELATION and correlation[lag]>correlation[lag-1]
                    and correlation[lag]>correlation[lag+1]
                    and correlation[lag]-max(correlation[lag-radius],correlation[lag+radius])>PITCH_MIN_PROMINENCE):
                return True
    return False


def prepare_pixels(page: Image.Image | NDArray[Any]) -> PixelPage:
    gray = _gray(page)
    h, w = gray.shape
    if np.ptp(gray) < 1:
        z = np.zeros(gray.shape, bool)
        return PixelPage(gray, z, z.astype(int), np.empty((0, 7)), z, [], [], MIN_XHEIGHT_PIXELS, original_ink=z)
    ink = binarise(gray, window=max(BINARIZE_MIN_PIXELS, round(BINARIZE_WINDOW_PAGE * min(h, w))) | 1)
    labels, _ = ndi.label(ink, structure=EIGHT)
    cc = _records(gray, labels)
    if not len(cc):
        return PixelPage(gray, ink, labels, cc, np.zeros_like(ink), [], [], MIN_XHEIGHT_PIXELS, original_ink=ink)
    heights, widths = cc[:, 3] - cc[:, 1], cc[:, 2] - cc[:, 0]
    sel = ((heights >= BODY_MIN_HEIGHT_PAGE * h) & (heights <= BODY_MAX_HEIGHT_PAGE * h)
           & (widths >= BODY_MIN_WIDTH_PAGE * w) & (widths < BODY_MAX_WIDTH_PAGE * w))
    original_components = cc.copy()
    original_labels = labels.copy()
    substantial = cc[sel]
    if len(substantial):
        substantial = substantial[substantial[:, 4] >= BODY_MIN_RELATIVE_AREA * np.percentile(substantial[:, 4], 90)]
    xh = max(MIN_XHEIGHT_PIXELS, _xheight(substantial[:, 3] - substantial[:, 1]) if len(substantial) else min(h, w) / 100)
    # Separate dark print from much fainter overlays BEFORE connected-component
    # labelling. Otherwise a stamp ring glues many genuine letters into a graphic.
    background = ndi.maximum_filter(gray, size=max(3, round(PAPER_ESTIMATION_WINDOW_XH * xh)))
    contrast = background - gray
    text_contrast = float(np.percentile(contrast[ink], 70))
    strong = ink & (contrast >= STRONG_MIN_CONTRAST_SHARE * text_contrast)
    faint = ink & ~strong & ~ndi.binary_dilation(strong, structure=EIGHT, iterations=max(1, round(FAINT_CLEARANCE_XH*xh)))
    labels, count = ndi.label(strong, structure=EIGHT)
    faint_labels, _ = ndi.label(faint, structure=EIGHT)
    labels = np.where(faint_labels, faint_labels + count, labels)
    cc = _records(gray, labels)
    heights, widths = cc[:, 3] - cc[:, 1], cc[:, 2] - cc[:, 0]
    # A long stem INSIDE a letter is still a letter. Mask only rule candidates,
    # not strokes from connected components of plausible display type.
    letter_shape = (heights <= LETTER_MAX_HEIGHT_XH*xh) & (widths > LETTER_MIN_WIDTH_XH*xh) & (widths < LETTER_MAX_WIDTH_XH*xh) & (cc[:,4] < LETTER_MAX_AREA_XH2*xh*xh)
    rule_ids = np.ones(labels.max()+1, bool)
    rule_ids[cc[letter_shape,5].astype(int)] = False
    barriers = _rule_mask(strong & rule_ids[labels], xh)
    raw_rules = _rule_mask(ink & rule_ids[labels], xh)
    # Whole connected graphics are removed BEFORE projection (the original
    # segmenter's frame/border rejection); enclosed table text is not removed.
    graphics = (heights > GRAPHIC_HEIGHT_XH * xh) | (widths > GRAPHIC_WIDTH_XH * xh) | (cc[:, 4] > GRAPHIC_AREA_XH2 * xh * xh)
    for i in np.flatnonzero(graphics):
        a,t,b,bot=cc[i,:4].astype(int)
        if _repeated_text_rows(ink[t:bot,a:b],xh):
            graphics[i]=False
    keep = np.ones(labels.max() + 1, bool); keep[0] = False
    keep[cc[graphics, 5].astype(int)] = False
    keep[cc[cc[:, 4] < max(3, COMPONENT_MIN_AREA_XH2 * xh * xh), 5].astype(int)] = False
    clean = keep[labels] & ~barriers
    nontext = []
    paper = float(np.percentile(gray,90))
    text_ink = float(np.percentile(substantial[:,6],25)) if len(substantial) else float(np.percentile(gray[ink],25))
    dark_limit = paper-DARK_MIN_CONTRAST_SHARE*(paper-text_ink)
    for q in original_components:
        if q[3]-q[1] < GRAPHIC_CANDIDATE_HEIGHT_XH*xh and q[2]-q[0] < GRAPHIC_CANDIDATE_WIDTH_XH*xh:
            continue
        a, t, b, bot = q[:4].astype(int)
        hh, ww = bot - t, b - a
        fill = q[4] / (hh * ww)
        # Filled illustrations / ornaments, and compact circular stamp frames.
        # A page/table frame is sparse and much larger than this stamp test.
        illustration = ((min(hh,ww)>GRAPHIC_MIN_DIMENSION_XH*xh and ww>GRAPHIC_MIN_WIDTH_XH*xh and fill>GRAPHIC_MIN_FILL)
                        or (ww>WIDE_GRAPHIC_MIN_WIDTH_XH*xh and hh>WIDE_GRAPHIC_MIN_HEIGHT_XH*xh and fill>WIDE_GRAPHIC_MIN_FILL))
        if ww>LARGE_GRAPHIC_MIN_WIDTH_XH*xh and hh>LARGE_GRAPHIC_MIN_HEIGHT_XH*xh and fill>LARGE_GRAPHIC_MIN_FILL:
            profile = ndi.uniform_filter1d(ink[t:bot,a:b].mean(axis=1),max(1,round(GRAPHIC_PROFILE_WINDOW_XH*xh)))
            # Engravings have texture throughout their framed height; rows of
            # text/table cells retain repeated low-ink interline valleys.
            component = original_labels[t:bot,a:b] == int(q[5])
            long_vertical = _rect_morphology(component, (max(3,round(RULE_SUPPORT_WINDOW_XH*xh)),1))
            long_horizontal = _rect_morphology(component, (1,max(3,round(RULE_SUPPORT_WINDOW_XH*xh))))
            straight_fraction = np.count_nonzero(long_vertical|long_horizontal)/max(1,component.sum())
            illustration |= profile.mean()>GRAPHIC_PROFILE_MIN_FILL and straight_fraction<GRAPHIC_MAX_STRAIGHT_SHARE
        # A frame around most of a page or facing leaf is not an illustration
        # just because the text inside it is dense.
        illustration &= not (hh>PAGE_TEXT_MIN_HEIGHT_PAGE*h and ww>PAGE_TEXT_MIN_WIDTH_PAGE*w)
        if illustration and _repeated_text_rows(ink[t:bot,a:b],xh):
            illustration=False
        if illustration and q[6] <= dark_limit:
            clean[t:bot, a:b] = False
            nontext.append((a, t, b, bot))
            barriers[t:bot,a:b] = False
            raw_rules[t:bot,a:b] = False
    # Repeated large motifs form one ornament band. Include nearby border
    # strokes only while their row gaps stay below a letter height; a separated
    # caption/heading terminates the band.
    motif_boxes = nontext.copy()
    for a,t,b,bot in motif_boxes:
        peers=[r for r in motif_boxes if abs((r[1]+r[3]-t-bot)/2)<RULE_DUPLICATE_DISTANCE_XH*xh
               and r[3]-r[1]<MOTIF_MAX_HEIGHT_XH*xh]
        if len(peers)<3:
            continue
        left=max(0,int(min(r[0] for r in peers)-ILLUSTRATION_CONTEXT_XH*xh))
        right=min(w,int(max(r[2] for r in peers)+ILLUSTRATION_CONTEXT_XH*xh))
        top=max(0,int(min(r[1] for r in peers)-MOTIF_CONTEXT_XH*xh))
        bottom=min(h,int(max(r[3] for r in peers)+MOTIF_CONTEXT_XH*xh))
        rows=ink[top:bottom,left:right].sum(axis=1)>CONTEXT_MIN_ROW_INK_SHARE*(right-left)
        rows=ndi.binary_closing(rows,structure=np.ones(max(1,round(CONTEXT_ROW_CLOSE_XH*xh))))
        middle=(t+bot)/2
        for start,end in _runs(rows):
            if top+start<=middle<top+end:
                region=(left,top+start,right,top+end)
                if region not in nontext:
                    nontext.append(region)
                    clean[region[1]:region[3],left:right]=False
                    barriers[region[1]:region[3],left:right]=False
                    raw_rules[region[1]:region[3],left:right]=False
    evidence = strong & rule_ids[labels]
    # Binding shadows can have a straight edge, but not a thin stroke. Test
    # the complete horizontal ink run before trusting its edge as a rule.
    broad = _rect_morphology(evidence, (1,max(2,round(RULE_BROAD_INK_WIDTH_XH*xh))))
    evidence &= ~broad
    for a,t,b,bot in nontext:
        evidence[t:bot,a:b] = False
    protected=cc[letter_shape & (heights>PROTECTED_BODY_HEIGHT_XH*xh) & (cc[:,4]>PROTECTED_BODY_AREA_XH2*xh*xh)]
    boundaries = _continue_rules(raw_rules, xh, evidence, protected)
    established=_structural_gutters(clean,barriers,xh)
    additions=_direct_rules(evidence, xh, boundaries)
    boundaries += [r for r in additions if not any(a<=r['centre']<=b for a,_,b,_ in established)]
    for boundary in boundaries:
        yy=np.arange(h)
        path=boundary['centre']+boundary['slope']*(yy-h/2)
        for dx in range(-int(np.ceil(boundary['radius'])),int(np.ceil(boundary['radius']))+1):
            xx=np.rint(path+dx).astype(int);ok=(xx>=0)&(xx<w)
            ok &= (yy>=boundary['top'])&(yy<boundary['bottom'])
            barriers[yy[ok],xx[ok]]=True
    clean &= ~barriers
    labels, _ = ndi.label(clean, structure=EIGHT)
    cc = _records(gray, labels)
    if not len(cc):
        return PixelPage(gray, clean, labels, cc, barriers, [], [], xh, nontext, boundaries, original_ink=ink)

    # Coarse horizontal zones, snapped to row valleys. Within each, rules and
    # persistent whitespace establish columns. A zone may contain many lines.
    profile = ndi.uniform_filter1d(clean.sum(axis=1).astype(float), max(1, round(ROW_PROFILE_WINDOW_XH * xh)))
    zones = [0]
    while zones[-1] + ZONE_MIN_REMAINDER_XH * xh < h:
        a = round(zones[-1] + ZONE_SEARCH_START_XH * xh); b = min(h, round(zones[-1] + ZONE_SEARCH_END_XH * xh))
        zones.append(a + int(np.argmin(profile[a:b])))
    zones.append(h)
    boxes = []
    gutters = _structural_gutters(clean, barriers, xh)
    structure = gutters.copy()
    # A tall scan-edge component plus a persistent inside gutter identifies
    # stacked book edges. It cannot erase a normal text column by darkness alone.
    for a, _, b, _ in structure:
        if a < LEFT_EDGE_REGION_PAGE*w and any(q[0] < LEFT_SHADOW_EDGE_PAGE*w and q[2] < LEFT_EDGE_REGION_PAGE*w and q[3]-q[1] > SHADOW_MIN_HEIGHT_PAGE*h for q in original_components):
            clean[:, :a] = False
            nontext.append((0, 0, a, h))
        if b > RIGHT_EDGE_REGION_PAGE*w and any(q[2] > RIGHT_SHADOW_EDGE_PAGE*w and q[0] > RIGHT_EDGE_REGION_PAGE*w and q[3]-q[1] > SHADOW_MIN_HEIGHT_PAGE*h for q in original_components):
            clean[:, b:] = False
            nontext.append((b, 0, w, h))
    for y0, y1 in zip(zones[:-1], zones[1:]):
        band = clean[y0:y1]
        local = cc[(cc[:, 1] >= y0) & (cc[:, 3] <= y1) & (cc[:, 4] > LOCAL_BODY_MIN_AREA_XH2 * xh * xh)]
        local_xh = xh
        if len(local) >= 8:
            measured = _xheight(local[:, 3] - local[:, 1])
            if LOCAL_MIN_SIZE_RATIO * xh < measured < LOCAL_MAX_SIZE_RATIO * xh:
                local_xh = measured
        # Rules need only span the occupied rows of a table zone, not 80% of
        # the entire page (the crop rule test's known limitation).
        stop = barriers[y0:y1].sum(axis=0) >= min(REGION_RULE_SUPPORT_XH * xh, REGION_RULE_SUPPORT_SHARE * (y1 - y0))
        gaps = _gaps(band, local_xh)
        cuts = np.zeros(w, bool)
        for a, _, b, _ in structure:
            cuts[a:b] = True
        for a, b in _runs(stop):
            cuts[a:b] = True
        for a, b in gaps:
            cuts[a:b] = True
            gutters.append((a, y0, b, y1))
        for a, b in _runs(~cuts):
            sub = band[:, a:b]
            if not sub.any():
                continue
            sm = ndi.uniform_filter1d(sub.sum(axis=1).astype(float), max(1, round(ROW_PROFILE_WINDOW_XH * xh)))
            # Deep row valleys only: do not pretend a curled multi-line region
            # is already a single line. The crop fitter resolves it next.
            active = sm > max(ROW_INK_COUNT_FLOOR, ROW_MIN_PEAK_SHARE * float(sm.max()))
            active = ndi.maximum_filter1d(active, max(1, round(ROW_ACTIVE_CLOSE_XH * xh)))
            for t, bot in _runs(active):
                ys, xs = np.nonzero(sub[t:bot])
                if not len(xs) or len(xs) < ROW_MIN_AREA_XH2 * xh * xh:
                    continue
                boxes.append((a + int(xs.min()), y0 + t, a + int(xs.max()) + 1, y0 + bot))
    return PixelPage(gray, clean, labels, cc, barriers, gutters, boxes, xh, nontext, boundaries, original_ink=ink)

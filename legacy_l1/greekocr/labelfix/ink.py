"""Ink evidence for a disputed vowel: mark blobs above and below it, from the crop pixels.

Reuses `greekocr.glyphs.components.line_glyphs` (the same component extraction and band
fit that `pages/lines.py` consumes through `_line_geometry`): Sauvola ink mask, 8-connected
components with roles (letter / mark / punct / ...), and the letter band (mean line and
baseline as functions of x) with its x-height.

Whole-line reading supplies font-scaled CTC regions, including partitions of fused
components and unions of disconnected strokes. Scalar callers retain component snapping.
CTC spikes sit left of the printed glyph and accents on leaning print overhang the
vowel's right edge, so frame positions alone would miss them.

Two kinds of mark evidence are gathered inside an x window:

  detached   components the glyph pass labelled `mark` (above a letter) or small `punct`
             blobs below the baseline (iota subscript candidates);
  attached   a vowel's upper lobe separated at the font meanline; other components
             require a narrow neck. Rejected ascender slices remain diagnostics.
  below      detached dark vertical wedges close to the left half of the vowel body;
             border ink, punctuation dots and connected letter descenders are excluded.

The optional base_letter supplies a base character, never a printed-mark label;
only alpha/eta/omega can host an iota subscript.

Every blob is reported with its bounding box, area, the principal-axis angle (degrees,
image coordinates: negative = rises to the right like an acute, positive = falls to the
right like a grave) and its elongation, so the decision can be audited on the crop.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from ..glyphs.components import line_glyphs

EIGHT = np.ones((3, 3), bool)
GRID = 8
ATTACH_SLICE_XH = -0.05    # slice attached marks from just above the mean line (vowels have no ascender)
MIN_BLOB_AREA = 3
MAX_MARK_HEIGHT_XH = 0.9   # taller blobs above the body are ascenders/neighbours, not marks
MAX_MARK_WIDTH_XH = 1.2
SUBSCRIPT_MAX_W_XH = 0.6
SUBSCRIPT_MAX_H_XH = 0.6
OBLIQUE_MIN_ELONGATION = 1.4
OBLIQUE_MIN_DEG, OBLIQUE_MAX_DEG = 15.0, 80.0


@dataclass
class Blob:
    x0: int
    y0: int
    x1: int
    y1: int
    area: int
    source: str          # 'detached' | 'attached'
    angle_deg: float     # principal axis angle, image coords (see module doc)
    elongation: float    # sqrt(l1/l2) of the covariance eigenvalues (1 = round)
    darkness: float = 0.0   # median gray of the blob (0 = black)
    faint: bool = False     # lighter than the faint cut (paper - 0.45 * (paper - letter ink))
    touches_border: bool = False
    hook: float = 0.0       # (mean x of the middle rows - mean x of the top+bottom rows) / width: ')' > 0, '(' < 0
    skew: float = 0.0       # third standardised moment of x: where the mass sits inside the box
    top_heavy: float = 0.0  # (mass in the upper half - lower half) / area
    grid: tuple = ()        # GRID x GRID occupancy of the blob's bounding box (shape thumbnail), row-major

    source_ids: tuple = ()
    mask: np.ndarray | None = field(default=None, repr=False, compare=False)

    def pixel_keys(self):
        if self.mask is None:
            raise ValueError('blob has no source pixel mask')
        ys,xs=np.nonzero(self.mask)
        return frozenset(zip((ys+self.y0).tolist(),(xs+self.x0).tolist()))

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def cy(self) -> float:
        return (self.y0 + self.y1) / 2

    @property
    def w(self) -> int:
        return self.x1 - self.x0

    @property
    def h(self) -> int:
        return self.y1 - self.y0

    def to_record(self) -> dict:
        return dict(bbox=[self.x0, self.y0, self.x1, self.y1], area=self.area, source=self.source,
                    angle_deg=round(self.angle_deg, 1), elongation=round(self.elongation, 2),
                    darkness=round(self.darkness, 1), faint=self.faint, touches_border=self.touches_border,
                    hook=round(self.hook, 3), skew=round(self.skew, 3), top_heavy=round(self.top_heavy, 3), source_ids=list(self.source_ids),
                    pixel_runs=pixel_runs(self.mask) if self.mask is not None else None)


def pixel_runs(mask):
    """Lossless local row runs, half-open, for serialized native-pixel custody."""
    out=[]
    for y,row in enumerate(mask):
        edges=np.diff(np.r_[False,row,False].astype(int))
        out.extend([y,int(a),int(b)] for a,b in zip(np.where(edges==1)[0],np.where(edges==-1)[0]))
    return out


def blob_from_pixels(ink,pixels,source):
    ys,xs=zip(*pixels);y0,y1=min(ys),max(ys)+1;x0,x1=min(xs),max(xs)+1
    mask=np.zeros((y1-y0,x1-x0),bool)
    mask[np.array(ys)-y0,np.array(xs)-x0]=True
    return _blob(mask,y0,x0,source,ink)


def component_mask(ink,c):
    """Exact region membership, including every parent of a virtual union."""
    if getattr(c,'mask',None) is not None:
        return c.mask
    return np.isin(ink.labels[c.y0:c.y1,c.x0:c.x1],getattr(c,'component_ids',(c.index,)))


def principal_axis(ys: np.ndarray, xs: np.ndarray) -> tuple[float, float]:
    """(angle in degrees, elongation). Angle of the major axis vs the x axis in image coordinates."""
    if len(xs) < 3:
        return 0.0, 1.0
    x = xs - xs.mean()
    y = ys - ys.mean()
    cxx, cyy, cxy = float((x * x).mean()), float((y * y).mean()), float((x * y).mean())
    tr, det = cxx + cyy, cxx * cyy - cxy * cxy
    disc = max(tr * tr / 4 - det, 0.0)
    l1, l2 = tr / 2 + math.sqrt(disc), max(tr / 2 - math.sqrt(disc), 1e-6)
    angle = 0.5 * math.degrees(math.atan2(2 * cxy, cxx - cyy))
    return angle, math.sqrt(l1 / l2)


@dataclass
class CropInk:
    """Per-crop analysis shared by all candidates of a line."""
    gray: np.ndarray
    ink: np.ndarray
    labels: np.ndarray
    xh: float
    top: np.ndarray        # mean line per column
    bottom: np.ndarray     # baseline per column
    components: list
    paper: float
    width: int = 0
    height: int = 0
    ink_level: float = 0.0   # median gray of letter pixels
    case_info: dict = field(default_factory=dict)
    word_bands: dict = field(default_factory=dict)

    @property
    def faint_cut(self) -> float:
        return self.paper - 0.45 * (self.paper - self.ink_level)

    def band(self, x: float) -> tuple[float, float]:
        i = min(max(int(round(x)), 0), len(self.top) - 1)
        return float(self.top[i]), float(self.bottom[i])


def analyse(image: Image.Image) -> CropInk:
    g = line_glyphs(image)
    xh=float(g.band.xh)
    top=np.asarray(g.band.top)
    bottom=np.asarray(g.band.bottom)
    # Heavy joined accents can dominate the glyph pass's height estimate.
    # Complete short bodies provide an independent, pixel-only lower mode.
    bodies=[c.h for c in g.components if c.role=='letter' and .45*xh <= c.h <= 1.15*xh
            and abs(c.y1-float(bottom[min(int(c.cx),g.width-1)])) <= .25*xh]
    if len(bodies)>=5:
        body_h=float(np.quantile(bodies,.30))
        if body_h < .8*xh:
            xh=body_h
            top=bottom-xh
    return CropInk(g.gray, g.ink, g.labels, xh, top, bottom,
                   list(g.components), float(g.paper), g.width, g.height, float(g.ink_level))


def _blob(mask: np.ndarray, oy: int, ox: int, source: str, ink: 'CropInk | None' = None) -> Blob:
    ys, xs = np.nonzero(mask)
    ang, el = principal_axis(ys.astype(float), xs.astype(float))
    b = Blob(int(xs.min()) + ox, int(ys.min()) + oy, int(xs.max()) + ox + 1, int(ys.max()) + oy + 1,
             int(mask.sum()), source, ang, el)
    h = int(ys.max() - ys.min()) + 1
    w = int(xs.max() - xs.min()) + 1
    sub = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(float)
    gy = np.minimum((np.arange(h) * GRID) // h, GRID - 1)
    gx = np.minimum((np.arange(w) * GRID) // w, GRID - 1)
    g = np.zeros((GRID, GRID))
    cnt = np.zeros((GRID, GRID))
    np.add.at(g, (gy[:, None].repeat(w, 1), gx[None, :].repeat(h, 0)), sub)
    np.add.at(cnt, (gy[:, None].repeat(w, 1), gx[None, :].repeat(h, 0)), 1.0)
    b.mask = sub.astype(bool)
    b.mask.setflags(write=False)
    if ink is not None:
        b.source_ids=tuple(int(i) for i in np.unique(ink.labels[ys+oy,xs+ox]) if i>0)
    b.grid = tuple((g / np.maximum(cnt, 1)).ravel().round(3).tolist())
    if h >= 3 and w >= 2:
        yr = (ys - ys.min()) / max(h - 1, 1)
        ends = (yr <= 0.25) | (yr >= 0.75)
        mid = ~ends
        if ends.any() and mid.any():
            b.hook = float((xs[mid].mean() - xs[ends].mean()) / w)
        sd = xs.std()
        if sd > 0:
            b.skew = float(((xs - xs.mean()) ** 3).mean() / sd ** 3)
        b.top_heavy = float(((yr < 0.5).sum() - (yr >= 0.5).sum()) / len(ys))
    if ink is not None:
        b.darkness = float(np.median(ink.gray[ys + oy, xs + ox]))
        b.faint = b.darkness > ink.faint_cut
        b.touches_border = b.y0 == 0 or b.y1 >= ink.height or b.x0 == 0 or b.x1 >= ink.width
    return b


def _overlap(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))


@dataclass
class MarkEvidence:
    above: list = field(default_factory=list)   # blobs above the vowel body
    below: list = field(default_factory=list)   # small detached blobs under the baseline
    window: tuple = (0.0, 0.0)
    xh: float = 0.0
    meanline: float = 0.0
    baseline: float = 0.0
    body: tuple = (0.0, 0.0)                    # the vowel body's x extent after snapping to ink
    body_source: str = ''                       # 'letter' (snapped) | 'merged' | 'ctc'
    n_letters_in_span: int = 0                  # letter components overlapping the CTC span
    neighbour_marks: int = 0                    # mark blobs in the search window but outside the body
    clipped_top: bool = False                   # ink touches the crop's top edge inside the window
    clipped_bottom: bool = False
    diagnostics: list = field(default_factory=list)  # rejected attached ascender ink
    apostrophes: list = field(default_factory=list)
    case_class: str = ''
    band_source: str = 'line'

    @property
    def n_above(self) -> int:
        return len(self.above)

    def obliques(self) -> list:
        return [b for b in self.above if b.elongation >= OBLIQUE_MIN_ELONGATION
                and OBLIQUE_MIN_DEG <= abs(b.angle_deg) <= OBLIQUE_MAX_DEG]

    def to_record(self) -> dict:
        return dict(window=[round(self.window[0], 1), round(self.window[1], 1)], xh=round(self.xh, 2),
                    meanline=round(self.meanline, 1), baseline=round(self.baseline, 1),
                    body=[round(self.body[0], 1), round(self.body[1], 1)], body_source=self.body_source,
                    n_letters_in_span=self.n_letters_in_span, neighbour_marks=self.neighbour_marks,
                    clipped_top=self.clipped_top, clipped_bottom=self.clipped_bottom,
                    above=[b.to_record() for b in self.above], below=[b.to_record() for b in self.below],
                    diagnostics=[b.to_record() for b in self.diagnostics],
                    apostrophes=[b.to_record() for b in self.apostrophes],
                    case_class=self.case_class, band_source=self.band_source)


def snap_body(ink: CropInk, bx0: float, bx1: float, *, vowel: bool = False) -> tuple[float, float, str, int]:
    """The vowel body's x extent: the letter component the CTC span overlaps most.

    Returns (x0, x1, source, n_letters): `n_letters` counts letter components that overlap the
    CTC span by at least 30 % of its width AND at least two thirds of the best overlap; more
    than one means the frames straddle two letters and the localisation is uncertain.
    """
    xh = ink.xh
    best, best_ov = None, 0.0
    overlaps = []
    hits = []
    for c in ink.components:
        if c.role != 'letter':
            continue
        ov = _overlap(bx0, bx1, c.x0, c.x1)
        overlaps.append(ov)
        if ov > 0:
            hits.append(c)
        if ov > best_ov:
            best, best_ov = c, ov
    if best is None or best_ov <= 0:
        return bx0 - 0.1 * xh, bx1 + 0.4 * xh, 'ctc', 0
    # A printed vowel may have two disconnected strokes. CTC locates the
    # entire body; do not throw away the second stroke (and its overlying mark).
    if vowel and len(hits) == 2:
        a, b = sorted(hits, key=lambda c: c.x0)
        if b.x1 - a.x0 <= 1.6*xh:
            return float(a.x0), float(b.x1), 'letter', 1
    n = sum(1 for ov in overlaps if ov >= 0.3 * max(1.0, bx1 - bx0) and ov >= best_ov / 1.5)
    if best.w <= 1.6 * xh:
        return float(best.x0), float(best.x1), 'letter', n
    return max(float(best.x0), bx0 - 0.2 * xh), min(float(best.x1), bx1 + 0.5 * xh), 'merged', n


def mark_evidence(ink: CropInk, x0: float, x1: float, *, core_x0: float | None = None,
                  core_x1: float | None = None, base_letter: str | None = None,
                  certified_body: tuple[float, float] | None = None,
                  letter_region: dict | None = None) -> MarkEvidence:
    """Mark blobs for the vowel whose CTC span is [core_x0, core_x1) (default: the window).

    The body extent is snapped to ink (`snap_body`); blobs must have their centre inside
    [body_x0 - 0.1 xh, body_x1 + 0.2 xh] so a neighbour's accent or ascender is not credited
    to this vowel. `x0..x1` only bounds the component search. A certified_body
    supplied by whole-line character ownership bypasses component re-snapping.
    """
    xh = ink.xh
    c0 = x0 if core_x0 is None else core_x0
    c1 = x1 if core_x1 is None else core_x1
    vowel = base_letter.lower() in 'αεηιουω' if base_letter else False
    mark_bearer = vowel or bool(base_letter and base_letter.lower()=='ρ')
    if certified_body is None:
        b0, b1, bsrc, n_letters = snap_body(ink, c0, c1, vowel=vowel and core_x0 is not None)
    else:
        # Whole-line ownership has already checked all recogniser characters.
        # Re-snapping overlapping boxes could otherwise merge the neighbouring
        # consonant back into a certified vowel (e.g. printed ζι).
        b0,b1 = certified_body
        bsrc,n_letters = 'letter',1
    lo, hi = b0 - 0.1 * xh, b1 + 0.2 * xh
    x0, x1 = min(x0, b0 - 0.5 * xh), max(x1, b1 + 0.5 * xh)
    top, base = ink.band((b0 + b1) / 2)
    ev = MarkEvidence([], [], (x0, x1), xh, top, base, (b0, b1), bsrc, n_letters)
    bodies = [c for c in ink.components if c.role == 'letter'
              and _overlap(c.x0, c.x1, b0, b1) >= .8*c.w]
    from .case import classify
    for body in bodies:
        if body.index not in ink.case_info:
            ink.case_info[body.index]=classify(ink,body,base_letter)
    owner=max(bodies,key=lambda c:_overlap(c.x0,c.x1,b0,b1),default=None)
    info=ink.case_info.get(owner.index,{}) if owner is not None else {}
    if letter_region is not None:
        owner=letter_region['component']
        bodies=[owner] if letter_region.get('component_ids') else []
        info=letter_region
    capital=info.get('case_class')=='capital'
    band=letter_region.get('height_band',{}) if letter_region is not None else ink.word_bands.get(owner.index,{}) if owner is not None else {}
    if band:
        xh=float(band['xh']);top=base-xh
        ev.xh=xh;ev.meanline=top;ev.band_source=band['source']
    ev.case_class=info.get('case_class','')
    if capital and owner is not None:
        top=float(owner.y0);ev.meanline=top;ev.band_source='capital_height'
    # A capital's top is letter ink, never a joined vowel accent slice.
    # Its detached marks are printed in the preceding gap instead.
    preposed = []
    for body in bodies:
        if capital:
            preposed.extend(capital_left_marks(ink, body))
    wx0, wx1 = int(max(0, math.floor(lo))), int(min(ink.width, math.ceil(hi)))
    if wx1 > wx0:
        ev.clipped_top = bool(ink.ink[0, wx0:wx1].any())
        ev.clipped_bottom = bool(ink.ink[-1, wx0:wx1].any())
    region_ids=set(letter_region.get('component_ids',[])) if letter_region is not None else set()
    for original in ink.components:
        c=original
        own_region=letter_region is not None and c.index in region_ids
        if own_region:
            # Virtual glyphs share native labels, but each owns only its CTC /
            # font partition. Never re-expand a fused component to full width.
            from types import SimpleNamespace
            a,b=letter_region['region_bounds']
            left,right=max(c.x0,a),min(c.x1,b)
            if right<=left:continue
            c=SimpleNamespace(**{k:getattr(original,k) for k in ('index','y0','y1','h','role','darkness')},
                              x0=left,x1=right,w=right-left,cx=(left+right)/2)
        if c.x1 <= x0 or c.x0 >= x1:
            continue
        cx = (c.x0 + c.x1) / 2
        inside = lo <= cx <= hi
        if c.role == 'mark' and c.y0 < top - .08*xh and c.y1 <= top + .15 * xh:
            if not inside:
                ev.neighbour_marks += 1
                continue
            if c.h <= MAX_MARK_HEIGHT_XH * xh and c.w <= MAX_MARK_WIDTH_XH * xh:
                sub = component_mask(ink,c)
                b = _blob(sub, c.y0, c.x0, 'detached', ink)
                if not faint_letter(c, ink) and not punctuation_dot(c, ink, excluded_stems=region_ids if mark_bearer else ()) and not _reserved_for_capital(ink, c, b1):
                    ev.above.append(b)
        elif c.role in ('mark', 'punct', 'fragment') and c.y0 >= base - 0.2 * xh and inside:
            sub = component_mask(ink,c)
            b = _blob(sub, c.y0, c.x0, 'detached', ink)
            if (base_letter is None or base_letter.lower() in ('α', 'η', 'ω')) and not punctuation_dot(c, ink, below=True) and subscript_shape(b, ev, ink):
                ev.below.append(b)
        elif c.role in ('letter', 'large') and c.y0 < top - 0.1 * xh:
            case=ink.case_info.get(c.index,{}).get('case_class')
            if (capital and (c in bodies or own_region)) or (case in ('lowercase_ascender','lowercase_descender') and not (mark_bearer and (c in bodies or own_region))):
                continue
            own_vowel = mark_bearer and (own_region or _overlap(c.x0,c.x1,b0,b1) >= .8*c.w)
            # Partition the LETTER body, not its upper lobe. A single accent
            # crossing a fused-letter boundary stays one native upper CC and
            # whole-line ownership credits its full box to one character.
            mark_source=original if own_region and own_vowel else c
            blobs, rejected = vowel_marks(ink, mark_source, top) if own_vowel else attached_marks(ink, c, top)
            ev.above.extend(b for b in blobs if lo <= b.cx <= hi)
            ev.diagnostics.extend(b for b in rejected if lo <= b.cx <= hi)
        # The same local rule applies to a wedge touching its vowel. Only the
        # below-baseline tail is measured, never the entire letter/descender.
        if base_letter in ('α','η','ω') and c.role in ('letter','large') and b0 <= c.cx <= b1 and c.y1 > base:
            cut = max(c.y0, int(math.ceil(base)))
            if cut < c.y1:
                tail = component_mask(ink,c)[cut-c.y0:]
                lab, _ = ndi.label(tail, structure=EIGHT)
                for k, sl in enumerate(ndi.find_objects(lab), 1):
                    if sl is None:
                        continue
                    b = _blob(lab[sl] == k, cut+sl[0].start, c.x0+sl[1].start, 'attached', ink)
                    if subscript_shape(b, ev, ink):
                        ev.below.append(b)
    ev.above.extend(preposed)
    # The glyph pass can call an upper arch neighbouring-line ink. A lower,
    # already accepted mark anchors recovery; top-edge fragments never qualify.
    for c in ink.components:
        if c.role != 'neighbour' or c.y0 <= 0 or c.y1 >= ink.height:
            continue
        if not (b0 <= c.cx <= b1 and top-1.3*xh <= c.y0
                and c.h <= .9*xh and c.w <= 1.2*xh):
            continue
        if not any(b0 <= b.cx <= b1 and (c.y0+c.y1)/2 < b.cy and c.y1 <= b.cy
                   and b.y0-c.y1 <= .5*xh
                   and _overlap(c.x0,c.x1,b.x0,b.x1) >= .5*min(c.w,b.w)
                   for b in ev.above):
            continue
        b = _blob(component_mask(ink,c),c.y0,c.x0,'stacked',ink)
        if b.area >= MIN_BLOB_AREA and not b.faint:
            ev.above.append(b)
    ev.above = list({b.pixel_keys(): b for b in ev.above}.values())
    if letter_region is not None:
        # A half-open box may end at floor(meanline), never inside the body.
        # Capital side marks are outside its horizontal body and have their
        # separate S5 vertical side zone. Subscripts start at ceil(baseline).
        overhead_top=min(top,ink.band((b0+b1)/2)[0])
        ev.above=[q for b in ev.above if (q:=zone_blob(ink,b,upper=overhead_top) if b.source!='preposed' else b) is not None]
        ev.below=[q for b in ev.below if (q:=zone_blob(ink,b,lower=base)) is not None]
    ev.above.sort(key=lambda b: b.x0)
    ev.below.sort(key=lambda b: b.x0)
    # Input bases locate the body; consonants cannot own Greek vowel marks.
    # Preserve their ink as diagnostics (rho can carry a breathing).
    if base_letter and base_letter.lower() not in 'αεηιουωρ':
        ev.diagnostics.extend(ev.above)
        ev.above=[]
    return ev


def zone_blob(ink, blob, *, upper=None, lower=None):
    """Intersect evidence with its physical zone, preserving the native label."""
    if blob.mask is None:
        raise ValueError('cannot clip evidence without its source mask')
    mask=blob.mask.copy()
    yy=np.arange(blob.y0,blob.y1)[:,None]
    for boundary,is_upper in ((upper,True),(lower,False)):
        if boundary is None:continue
        values=np.asarray(boundary)
        values=values if values.ndim==0 else values[blob.x0:blob.x1][None,:]
        mask &= yy < np.floor(values) if is_upper else yy >= np.ceil(values)
    if np.array_equal(mask,blob.mask):return blob
    if mask.sum()<MIN_BLOB_AREA:return None
    q=_blob(mask,blob.y0,blob.x0,blob.source,ink)
    assert q.area<=blob.area and q.pixel_keys()<=blob.pixel_keys()
    return q if q.h>=max(2,.12*ink.xh) else None


def capital_left_marks(ink, body):
    """Detached upper-left ink bounded by the preceding letter's right edge.

    This never reaches into the preceding word's last letter. Geometry only:
    naming the breathing/accent remains the mark classifier's responsibility.
    """
    xh = ink.xh
    left = max((c.x1 for c in ink.components if c.role == 'letter'
                and c.x1 <= body.x0 and c.index != body.index), default=0)
    out = []
    for c in ink.components:
        if c.role not in ('mark','punct','fragment') or not (left <= c.x0 and c.x1 <= body.x0):
            continue
        if not (body.y0-.35*xh <= c.y0 and c.y1 <= body.y0+.6*body.h
                and .1*xh <= c.h <= .9*xh and c.w <= 1.2*xh):
            continue
        b = _blob(component_mask(ink,c),c.y0,c.x0,'preposed',ink)
        if b.area >= MIN_BLOB_AREA and not b.faint and not b.touches_border:
            out.append(b)
    # Marks form a compact group next to the capital. A distant opening quote
    # or preceding word's overhang must not join that group across whitespace.
    group = []
    right = body.x0
    for b in sorted(out, key=lambda b: b.x1, reverse=True):
        if right-b.x1 > (.65*xh if not group else .25*xh):
            break
        group.append(b)
        right = b.x0
    return sorted(group, key=lambda b: b.x0)


def _reserved_for_capital(ink, mark, right):
    """Keep a following capital's left-gap mark out of this letter's window."""
    nxt = min((c for c in ink.components if c.role == 'letter' and c.x0 >= right),
              key=lambda c:c.x0, default=None)
    if nxt is not None and nxt.index not in ink.case_info:
        from .case import classify
        ink.case_info[nxt.index]=classify(ink,nxt)
    return bool(nxt is not None and ink.case_info[nxt.index]['case_class']=='capital'
                and any((b.x0,b.y0,b.x1,b.y1) == (mark.x0,mark.y0,mark.x1,mark.y1)
                        for b in capital_left_marks(ink,nxt)))


def faint_letter(c, ink):
    top, base = ink.band(c.cx)
    return (c.h >= .8 * ink.xh and c.y1 >= top + .6 * ink.xh
            and c.y0 <= base and c.darkness > ink.faint_cut)


def punctuation_dot(c, ink, *, below=False, excluded_stems=()):
    """Baseline punctuation and a dot aligned with a punctuation stem, in either direction."""
    top, base = ink.band(c.cx)
    if not below and c.role == 'punct' and c.y0 >= top + .55 * ink.xh:
        return True
    if c.w > .4 * ink.xh or c.h > .4 * ink.xh:
        return False
    for stem in ink.components:
        if stem.index in excluded_stems:
            continue
        if stem.index == c.index or stem.h < .55 * ink.xh or stem.w > .65 * ink.xh:
            continue
        if below and stem.role != 'punct' and not (stem.w <= .3*ink.xh and stem.h >= 2.5*stem.w):
            continue
        if abs(stem.cx - c.cx) > .25 * ink.xh and _overlap(stem.x0, stem.x1, c.x0, c.x1) < .25 * min(stem.w, c.w):
            continue
        gap = max(stem.y0 - c.y1, c.y0 - stem.y1)
        if 0 <= gap <= .45 * ink.xh and stem.y1 >= top + .65 * ink.xh:
            return True
    return False


def subscript_shape(b, ev, ink):
    """Vowel-relative short stroke/wedge, detached or touching the body.

    Cut-off ink is separately recorded as clipped_bottom, not proof of absence.
    Size/darkness reject specks; a nearby crossing letter rejects descender ink.
    """
    xh = ev.xh
    if not (not b.touches_border and not b.faint
            and .008*xh*xh <= b.area <= .30*xh*xh
            and .25*xh <= b.h <= .9*xh and b.w <= .6*xh and b.h >= .85*b.w
            and ev.baseline - .2*xh <= b.y0 <= ev.baseline + .35*xh
            and ev.body[0] - .3*xh <= b.cx <= min(ev.body[1]+.3*xh, sum(ev.body)/2+.3*xh)):
        return False
    # Eta's own right-hand descending stem is not a subscript. A touching
    # wedge must emerge under the left half, independently of horizontal slack
    # allowed for detached, leaning print.
    if b.source == 'attached' and b.cx > sum(ev.body)/2-.05*xh:
        return False
    for c in ink.components:
        if c.role not in ('letter','large') or _overlap(c.x0,c.x1,*ev.body) >= .8*c.w:
            continue
        if c.y0 < ev.baseline-.4*xh and c.y1 > ev.baseline+.1*xh and c.x0-.1*xh <= b.cx <= c.x1+.1*xh:
            return False
    return True


def vowel_marks(ink, c, top):
    """Vowels have no ascender: retain joined top lobes without a neck veto.

    The locator supplies only the base letter. Mark identity still comes from
    pixels/classifier, and ordinary round-body overshoot is excluded by height.
    """
    # A complete body shorter than the local x-height cannot contain an
    # attached top mark. This also guards against a bad/low fitted mean line.
    if c.h <= 1.15*ink.xh:
        return [], []
    cut = min(c.y1, int(math.floor(top)))
    if cut <= c.y0:
        return [], []
    mask = component_mask(ink,c)[:cut-c.y0]
    lab, _ = ndi.label(mask, structure=EIGHT)
    out = []
    for k, sl in enumerate(ndi.find_objects(lab), 1):
        if sl is None:
            continue
        b = _blob(lab[sl] == k, c.y0+sl[0].start,c.x0+sl[1].start,'attached',ink)
        if b.area >= MIN_BLOB_AREA and max(2,.12*ink.xh) < b.h <= .9*ink.xh and b.w <= 1.2*ink.xh:
            out.append(b)
    return out, []


def attached_marks(ink, c, top):
    """Separate a top lobe only at a narrow local cross-section (neck).

    Row cross-sections sum the column ink masses. Removing the neck must leave
    the main body no higher than meanline - .3 xh. All rejected lobes are diagnostic.
    """
    xh = ink.xh
    mask = component_mask(ink,c)
    cut = min(mask.shape[0], max(0, int(top + .05*xh) - c.y0))
    diag = [_blob(mask[:cut], c.y0, c.x0, 'ascender', ink)] if cut and mask[:cut].any() else []
    mass = mask.sum(axis=1)
    lo = max(1, int(top - .35*xh) - c.y0)
    hi = min(len(mass)-2, int(top + .15*xh) - c.y0)
    for y in sorted(range(lo, hi+1), key=lambda i: mass[i]):
        upper, lower = mask[:y], mask[y+1:]
        if not upper.any() or not lower.any() or mass[y] == 0:
            continue
        if mass[y] > max(1, .1*xh) or mass[y] > .30*min(mass[:y].max(), mass[y+1:].max()):
            continue
        if mass[y] > mass[y-1] or mass[y] > mass[y+1]:
            continue
        # Main-body ink outside the neck cannot extend above the allowed overshoot.
        if c.y0 + y + 1 < top - .3*xh:
            continue
        b = _blob(upper, c.y0, c.x0, 'attached', ink)
        if b.area >= MIN_BLOB_AREA and .12*xh <= b.h <= .9*xh and b.w <= .8*xh:
            return [b], []
    return [], diag


def apostrophe_candidates(ink, letters):
    """Geometric elision signs after an input-text word-final consonant.

    `letters` supplies (component, base, word_final) from locator-only mapping.
    A sign must be detached, at meanline height, between words; no vowel under it.
    Returns slot-index -> blobs; the recogniser supplies no mark reading.
    """
    out = {}
    for i, (body, base, final) in enumerate(letters):
        if not final or base.lower() not in 'δτρθπ':
            continue
        top, _ = ink.band(body.cx)
        nxt = letters[i+1][0].x0 if i+1 < len(letters) else ink.width
        for c in ink.components:
            if c.role not in ('mark', 'punct', 'fragment') or c.x0 < body.x1 - .1*ink.xh:
                continue
            if not (body.x1 <= c.cx < nxt and c.cx-body.x1 <= .65*ink.xh):
                continue
            if not (.10*ink.xh <= c.h <= .8*ink.xh and c.w <= .6*ink.xh
                    and top-1.1*ink.xh <= c.y0 and c.y1 <= top+.25*ink.xh):
                continue
            b = _blob(component_mask(ink,c),c.y0,c.x0,'apostrophe',ink)
            if b.area >= MIN_BLOB_AREA and not b.faint:
                out.setdefault(i, []).append(b)
    return out


def opening_quote_candidates(ink, first_body, reserved=()):
    """Detached line-initial quote ink, separate from a capital's own marks.

    Single curved opening signs occur in these editions. Ambiguous leading
    apostrophe/quote semantics remain a flag; the pixels are not vowel marks.
    """
    top, _ = ink.band(first_body.cx)
    used = {(b.x0,b.y0,b.x1,b.y1) for b in reserved}
    out = []
    for c in ink.components:
        if c.role not in ('punct','mark','fragment') or c.x1 >= first_body.x0:
            continue
        if (c.x0,c.y0,c.x1,c.y1) in used:
            continue
        if not (.2*ink.xh <= c.h <= .9*ink.xh and .12*ink.xh <= c.w <= .8*ink.xh
                and top-1.2*ink.xh <= c.y0 and c.y1 <= top+.25*ink.xh):
            continue
        b = _blob(component_mask(ink,c),c.y0,c.x0,'opening_quote',ink)
        if not b.faint and not b.touches_border:
            out.append(b)
    return out


def dialytika_shape(ev: MarkEvidence) -> bool:
    """Two small blobs side by side at the same height."""
    a = ev.above
    if len(a) != 2:
        return False
    p, q = a
    xh = ev.xh
    small = all(b.area <= 0.2 * xh * xh and b.h <= 0.4 * xh and b.w <= 0.45 * xh for b in (p, q))
    gap = q.x0 - p.x1
    return small and -0.05 * xh <= gap <= 0.5 * xh and abs(p.cy - q.cy) <= 0.2 * xh


def slope_sign(blob: Blob) -> str | None:
    """'acute' if the stroke rises to the right, 'grave' if it falls, None if not oblique."""
    if blob.elongation < OBLIQUE_MIN_ELONGATION or not (OBLIQUE_MIN_DEG <= abs(blob.angle_deg) <= OBLIQUE_MAX_DEG):
        return None
    return 'acute' if blob.angle_deg < 0 else 'grave'

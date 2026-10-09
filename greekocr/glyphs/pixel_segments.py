"""Pixel-only rough regions: graphical stops, persistent gutters, then row valleys.

The boxes are seeds, not OCR crops. A valley need not exist between two curled
lines, so a box can deliberately contain several lines. Lengths below are in
estimated letter heights (or fractions of the page), never a document's pixels.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray
from PIL import Image
from scipy import ndimage as ndi

from .components import EIGHT, _xheight, binarise, to_gray


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


def _runs(mask):
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


def _rule_mask(ink, xh):
    """Thin straight strokes only; close short breaks before testing length.

    Reject wide opened components instead of turning their entire bounding
    rectangle into a stop. In particular, a shadow, stamp or curled letter
    margin is not a rule. The same test works at every page resolution.
    """
    scale = min(1., 8 / xh)
    pooled = ndi.maximum_filter(ink, max(1, int(np.ceil(1 / scale))))
    small = ndi.zoom(pooled.astype(np.uint8), scale, order=0).astype(bool)
    h, w = small.shape
    unit = xh * scale
    rows, cols = np.arange(h)[:, None], np.arange(w)[None, :]
    result = np.zeros_like(small)
    for slope in np.linspace(-.12, .12, 9):
        shift = np.rint(slope * (rows - h / 2)).astype(int)
        xx = cols + shift
        shear = small[rows, np.clip(xx, 0, w - 1)] & (xx >= 0) & (xx < w)
        joined = ndi.binary_closing(shear, structure=np.ones((max(1, round(.12 * unit)), 1)))
        opened = ndi.binary_opening(joined, structure=np.ones((max(3, round(3 * unit)), 1)))
        labels, _ = ndi.label(opened)
        thin = np.zeros_like(opened)
        for k, sl in enumerate(ndi.find_objects(labels), 1):
            if sl is None:
                continue
            y, x = sl
            hh, ww = y.stop - y.start, x.stop - x.start
            if ww > .55 * unit or hh < 3 * unit or hh < 10 * ww:
                continue
            if shear[sl].mean() < .5:
                continue
            thin[sl] |= labels[sl] == k
        back = cols - shift
        result |= thin[rows, np.clip(back, 0, w - 1)] & (back >= 0) & (back < w)
    result = ndi.maximum_filter(result, max(1, round(.12 * unit)) | 1)
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
        if y.stop-y.start >= 2*xh and x.stop-x.start < max(xh,.18*(y.stop-y.start)):
            pieces.append(((x.start+x.stop)/2,(y.start+y.stop)/2,y.start,y.stop,x.stop-x.start))
    if not pieces:
        return []
    q=np.array(pieces)
    proposals=[]
    step=max(1.,.5*xh)
    for slope in np.linspace(-.12,.12,81):
        intercept=q[:,0]-slope*(q[:,1]-h/2)
        bins=np.floor(intercept/step).astype(int)
        for bucket in np.unique(bins):
            near=(abs(intercept-(bucket+.5)*step)<.75*xh)
            own=q[near]
            covered=np.zeros(h,bool)
            for row in own:
                covered[int(row[2]):int(row[3])]=True
            if covered.sum()<.3*h or np.ptp(own[:,1])+np.max(own[:,3]-own[:,2])<.5*h:
                continue
            centre=float(np.median(intercept[near]))
            proposals.append((int(covered.sum()),slope,centre,near))
    result=[]
    for score,slope,centre,near in sorted(proposals,key=lambda v:-v[0]):
        if any(abs(centre-r['centre'])<2*xh for r in result):
            continue
        own=q[near]
        if len(own)>=3 and np.ptp(own[:,1])>.3*h:
            slope,intercept=np.polyfit(own[:,1]-h/2,own[:,0],1,w=np.sqrt(own[:,3]-own[:,2]))
            centre=float(intercept)
        elif len(own):
            longest=own[np.argmax(own[:,3]-own[:,2])]
            a,b=max(0,int(longest[0]-longest[4]/2)),min(w,int(longest[0]+longest[4]/2)+1)
            t,bot=int(longest[2]),int(longest[3])
            yy,xx=np.nonzero(barriers[t:bot,a:b])
            if len(yy)>2 and np.ptp(yy)>2*xh:
                slope,centre=np.polyfit(yy+t-h/2,xx+a,1)
        path=centre+slope*(np.arange(h)-h/2)
        radius=max(1.,min(.25*xh,float(np.median(own[:,4]))/2))
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
            if support.mean() < .5:
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
    scale = min(1., 8/xh)
    small = ndi.zoom(ndi.maximum_filter(ink, max(1, int(np.ceil(1/scale))))
                     .astype(np.uint8), scale, order=0)
    paths = cv2.HoughLinesP(small, 1, min(np.pi/1800, .2*xh/h),
                           threshold=max(2, round(10*xh*scale)),
                           minLineLength=max(12*xh, .1*h)*scale,
                           maxLineGap=.8*xh*scale)
    if paths is None:
        return []
    found=[]
    for x0,y0,x1,y1 in sorted(paths.reshape(-1,4), key=lambda v:-abs(int(v[3])-int(v[1]))):
        x0,y0,x1,y1 = np.array([x0,y0,x1,y1],float)/scale
        if abs(y1-y0)<12*xh or abs(x1-x0)>.12*abs(y1-y0):
            continue
        slope=(x1-x0)/(y1-y0);centre=x0+slope*(h/2-y0)
        if any(abs(centre-r['centre'])<xh and min(y0,y1)>=r['top']-2*xh
               and max(y0,y1)<=r['bottom']+2*xh for r in existing+found):
            continue
        top,bottom=max(0,round(min(y0,y1))),min(h,round(max(y0,y1))+1)
        yy=np.arange(h);path=centre+slope*(yy-h/2)
        # Refine the Hough quantisation using original-resolution contacts.
        offsets=np.arange(-round(.6*xh),round(.6*xh)+1)
        xx=np.rint(path[:,None]+offsets).astype(int)
        sample=ink[yy[:,None],np.clip(xx,0,w-1)] & (xx>=0) & (xx<w)
        count=sample.sum(axis=1)
        own=(count>0)&(count<.65*xh)&(yy>=top)&(yy<bottom)
        if own.sum()<.75*(bottom-top):
            continue
        contacts=(sample*xx).sum(axis=1)/np.maximum(1,count)
        slope,centre=np.polyfit(yy[own]-h/2,contacts[own],1)
        # Extend the *evidence* search before fitting the whole stroke. A
        # quantised partial Hough segment otherwise misses its far endpoint.
        for _ in range(2):
            xx=np.rint(centre+slope*(yy[:,None]-h/2)+offsets).astype(int)
            sample=ink[yy[:,None],np.clip(xx,0,w-1)] & (xx>=0) & (xx<w)
            count=sample.sum(axis=1)
            own=(count>0)&(count<.65*xh)&(yy>=top-2*xh)&(yy<bottom+2*xh)
            contacts=(sample*xx).sum(axis=1)/np.maximum(1,count)
            slope,centre=np.polyfit(yy[own]-h/2,contacts[own],1)
        path=centre+slope*(yy-h/2)
        radius=max(1.,float(np.percentile(count[own],75))/2+.08*xh)
        hits=np.zeros(len(yy),bool)
        for dx in range(-int(np.ceil(radius)),int(np.ceil(radius))+1):
            xx=np.rint(path+dx).astype(int);ok=(xx>=0)&(xx<w)
            hits[ok] |= ink[yy[ok],xx[ok]]
        if hits[top:bottom].mean()<.85:
            continue
        supported=ndi.uniform_filter1d(hits.astype(float),max(1,round(4*xh)))>.75
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
    for y in range(0, h, max(1, round(8 * xh))):
        band = clean[y:min(h, y + round(8 * xh))]
        if band.sum() > 2 * xh * xh:
            bands.append(band)
    if len(bands) < 3:
        return []
    votes = np.zeros(w)
    for band in bands:
        col = ndi.uniform_filter1d(band.sum(axis=0).astype(float), max(1, round(.25 * xh)))
        level = np.percentile(col[col > 0], 75) if np.any(col > 0) else 1
        votes += col < max(.5, .24 * level)
    lanes = ndi.gaussian_filter1d(votes, max(1., .3*xh)) >= .67 * len(bands)
    # The rule vote covers its full text height, including short missing dashes.
    rules = barriers.sum(axis=0) > .35 * h
    gutters = []
    for a, b in _runs(lanes | rules):
        is_rule = rules[a:b].any()
        # Persistence across the page, rather than a large local word gap,
        # supplies the column evidence. A one-x-height lane can separate two
        # densely set columns; requiring 1.5 erased such boundaries.
        if a == 0 or b == w or (not is_rule and b-a < xh):
            continue
        left = clean[:, max(0, a-round(15*xh)):a]
        right = clean[:, b:min(w, b+round(15*xh))]
        if left.sum() < 8*xh*xh or right.sum() < 8*xh*xh:
            continue
        if not is_rule and b-a < 1.5*xh:
            # Narrow whitespace needs two substantial text blocks, not a
            # repeated indent or a short prefix at the edge of a paragraph.
            # Wider established gutters and printed rules need no such vote.
            if min(clean[:,:a].sum(),clean[:,b:].sum()) < .2*clean.sum():
                continue
            inset=max(1,round(.15*xh))
            a,b=a+inset,b-inset
            if b<=a:
                continue
        gutters.append((a, 0, b, h))
    return gutters


def _gaps(mask, xh, *, persistent=True):
    """Blank vertical lanes; repeated interline evidence distinguishes word gaps."""
    h, w = mask.shape
    col = ndi.uniform_filter1d(mask.sum(axis=0).astype(float), max(1, round(.3 * xh)))
    if not col.any():
        return []
    low = col <= max(.5, .035 * np.percentile(col[col > 0], 85))
    gaps = []
    for a, b in _runs(low):
        if a == 0 or b == w or b - a < (1.8 if persistent else 10) * xh:
            continue
        left = mask[:, max(0, a - round(12 * xh)):a]
        right = mask[:, b:min(w, b + round(12 * xh))]
        if not left.any() or not right.any():
            continue
        ly, ry = np.flatnonzero(left.any(axis=1)), np.flatnonzero(right.any(axis=1))
        # At least two vertically separated lines on BOTH sides. A single
        # justified line can have a large word space without becoming columns.
        def row_count(block):
            occupied = ndi.maximum_filter1d(block.any(axis=1), max(1,round(.6*xh)))
            return sum(bot-top > .5*xh for top,bot in _runs(occupied))
        repeated = min(np.ptp(ly), np.ptp(ry)) > 3*xh and min(row_count(left), row_count(right)) >= 2
        if repeated or b - a >= 10 * xh:
            gaps.append((int(a), int(b)))
    return gaps


def _repeated_text_rows(mask, xh):
    """Protect a connected table/frame containing repeated printed rows.

    Different columns may have different row phases, so test overlapping
    horizontal strips as well as the whole region. A broad lighting gradient
    or engraving texture has no prominent peak at a printed line pitch.
    """
    h,w=mask.shape
    if h<9*xh or w<3*xh:
        return False
    step=max(1,round(max(6*xh,w/3)))
    spans=[(0,w)]+[(a,min(w,a+step)) for a in range(0,w-step//2,max(1,step//2))]
    radius=max(1,round(.4*xh))
    for a,b in spans:
        profile=mask[:,a:b].mean(axis=1)
        signal=ndi.gaussian_filter1d(profile,max(1.,.15*xh))-ndi.gaussian_filter1d(profile,3*xh)
        if np.dot(signal,signal)<1e-6:
            continue
        correlation=np.correlate(signal,signal,'full')[h-1:]
        correlation/=correlation[0]
        for lag in range(max(radius+1,round(1.5*xh)),min(round(5*xh),h//6)):
            if (correlation[lag]>.35 and correlation[lag]>correlation[lag-1]
                    and correlation[lag]>correlation[lag+1]
                    and correlation[lag]-max(correlation[lag-radius],correlation[lag+radius])>.12):
                return True
    return False


def prepare_pixels(page: Image.Image | NDArray[Any]) -> PixelPage:
    gray = _gray(page)
    h, w = gray.shape
    if np.ptp(gray) < 1:
        z = np.zeros(gray.shape, bool)
        return PixelPage(gray, z, z.astype(int), np.empty((0, 7)), z, [], [], 3.)
    ink = binarise(gray, window=max(15, round(.04 * min(h, w))) | 1)
    labels, _ = ndi.label(ink, structure=EIGHT)
    cc = _records(gray, labels)
    if not len(cc):
        return PixelPage(gray, ink, labels, cc, np.zeros_like(ink), [], [], 3.)
    heights, widths = cc[:, 3] - cc[:, 1], cc[:, 2] - cc[:, 0]
    sel = ((heights >= .002 * h) & (heights <= .1 * h)
           & (widths >= .001 * w) & (widths < .12 * w))
    original_components = cc.copy()
    original_labels = labels.copy()
    substantial = cc[sel]
    if len(substantial):
        substantial = substantial[substantial[:, 4] >= .15 * np.percentile(substantial[:, 4], 90)]
    xh = max(3., _xheight(substantial[:, 3] - substantial[:, 1]) if len(substantial) else min(h, w) / 100)
    # Separate dark print from much fainter overlays BEFORE connected-component
    # labelling. Otherwise a stamp ring glues many genuine letters into a graphic.
    background = ndi.maximum_filter(gray, size=max(3, round(2 * xh)))
    contrast = background - gray
    text_contrast = float(np.percentile(contrast[ink], 70))
    strong = ink & (contrast >= .55 * text_contrast)
    faint = ink & ~strong & ~ndi.binary_dilation(strong, structure=EIGHT, iterations=max(1, round(.08*xh)))
    labels, count = ndi.label(strong, structure=EIGHT)
    faint_labels, _ = ndi.label(faint, structure=EIGHT)
    labels = np.where(faint_labels, faint_labels + count, labels)
    cc = _records(gray, labels)
    heights, widths = cc[:, 3] - cc[:, 1], cc[:, 2] - cc[:, 0]
    # A long stem INSIDE a letter is still a letter. Mask only rule candidates,
    # not strokes from connected components of plausible display type.
    letter_shape = (heights <= 4.5*xh) & (widths > .35*xh) & (widths < 5*xh) & (cc[:,4] < 8*xh*xh)
    rule_ids = np.ones(labels.max()+1, bool)
    rule_ids[cc[letter_shape,5].astype(int)] = False
    barriers = _rule_mask(strong & rule_ids[labels], xh)
    raw_rules = _rule_mask(ink & rule_ids[labels], xh)
    # Whole connected graphics are removed BEFORE projection (the original
    # segmenter's frame/border rejection); enclosed table text is not removed.
    graphics = (heights > 4 * xh) | (widths > 14 * xh) | (cc[:, 4] > 18 * xh * xh)
    for i in np.flatnonzero(graphics):
        a,t,b,bot=cc[i,:4].astype(int)
        if _repeated_text_rows(ink[t:bot,a:b],xh):
            graphics[i]=False
    keep = np.ones(labels.max() + 1, bool); keep[0] = False
    keep[cc[graphics, 5].astype(int)] = False
    keep[cc[cc[:, 4] < max(3, .012 * xh * xh), 5].astype(int)] = False
    clean = keep[labels] & ~barriers
    nontext = []
    paper = float(np.percentile(gray,90))
    text_ink = float(np.percentile(substantial[:,6],25)) if len(substantial) else float(np.percentile(gray[ink],25))
    dark_limit = paper-.5*(paper-text_ink)
    for q in original_components:
        if q[3]-q[1] < 2.5*xh and q[2]-q[0] < 12*xh:
            continue
        a, t, b, bot = q[:4].astype(int)
        hh, ww = bot - t, b - a
        fill = q[4] / (hh * ww)
        # Filled illustrations / ornaments, and compact circular stamp frames.
        # A page/table frame is sparse and much larger than this stamp test.
        illustration = ((min(hh,ww)>3*xh and ww>5*xh and fill>.12)
                        or (ww>12*xh and hh>2.5*xh and fill>.09))
        if ww>20*xh and hh>12*xh and fill>.01:
            profile = ndi.uniform_filter1d(ink[t:bot,a:b].mean(axis=1),max(1,round(.3*xh)))
            # Engravings have texture throughout their framed height; rows of
            # text/table cells retain repeated low-ink interline valleys.
            component = original_labels[t:bot,a:b] == int(q[5])
            long_vertical = ndi.binary_opening(component, structure=np.ones((max(3,round(4*xh)),1)))
            long_horizontal = ndi.binary_opening(component, structure=np.ones((1,max(3,round(4*xh)))))
            straight_fraction = np.count_nonzero(long_vertical|long_horizontal)/max(1,component.sum())
            illustration |= profile.mean()>.1 and straight_fraction<.5
        # A frame around most of a page or facing leaf is not an illustration
        # just because the text inside it is dense.
        illustration &= not (hh>.7*h and ww>.35*w)
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
        peers=[r for r in motif_boxes if abs((r[1]+r[3]-t-bot)/2)<2*xh
               and r[3]-r[1]<6*xh]
        if len(peers)<3:
            continue
        left=max(0,int(min(r[0] for r in peers)-2.5*xh))
        right=min(w,int(max(r[2] for r in peers)+2.5*xh))
        top=max(0,int(min(r[1] for r in peers)-3*xh))
        bottom=min(h,int(max(r[3] for r in peers)+3*xh))
        rows=ink[top:bottom,left:right].sum(axis=1)>.025*(right-left)
        rows=ndi.binary_closing(rows,structure=np.ones(max(1,round(.8*xh))))
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
    broad = ndi.binary_opening(evidence, structure=np.ones((1,max(2,round(.65*xh)))))
    evidence &= ~broad
    for a,t,b,bot in nontext:
        evidence[t:bot,a:b] = False
    protected=cc[letter_shape & (heights>.6*xh) & (cc[:,4]>.08*xh*xh)]
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
        return PixelPage(gray, clean, labels, cc, barriers, [], [], xh, nontext, boundaries)

    # Coarse horizontal zones, snapped to row valleys. Within each, rules and
    # persistent whitespace establish columns. A zone may contain many lines.
    profile = ndi.uniform_filter1d(clean.sum(axis=1).astype(float), max(1, round(.25 * xh)))
    zones = [0]
    while zones[-1] + 18 * xh < h:
        a = round(zones[-1] + 12 * xh); b = min(h, round(zones[-1] + 22 * xh))
        zones.append(a + int(np.argmin(profile[a:b])))
    zones.append(h)
    boxes = []
    gutters = _structural_gutters(clean, barriers, xh)
    structure = gutters.copy()
    # A tall scan-edge component plus a persistent inside gutter identifies
    # stacked book edges. It cannot erase a normal text column by darkness alone.
    for a, _, b, _ in structure:
        if a < .2*w and any(q[0] < .04*w and q[2] < .2*w and q[3]-q[1] > .45*h for q in original_components):
            clean[:, :a] = False
            nontext.append((0, 0, a, h))
        if b > .8*w and any(q[2] > .96*w and q[0] > .8*w and q[3]-q[1] > .45*h for q in original_components):
            clean[:, b:] = False
            nontext.append((b, 0, w, h))
    for y0, y1 in zip(zones[:-1], zones[1:]):
        band = clean[y0:y1]
        local = cc[(cc[:, 1] >= y0) & (cc[:, 3] <= y1) & (cc[:, 4] > .07 * xh * xh)]
        local_xh = xh
        if len(local) >= 8:
            measured = _xheight(local[:, 3] - local[:, 1])
            if .45 * xh < measured < 2 * xh:
                local_xh = measured
        # Rules need only span the occupied rows of a table zone, not 80% of
        # the entire page (the crop rule test's known limitation).
        stop = barriers[y0:y1].sum(axis=0) >= min(3 * xh, .35 * (y1 - y0))
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
            sm = ndi.uniform_filter1d(sub.sum(axis=1).astype(float), max(1, round(.25 * xh)))
            # Deep row valleys only: do not pretend a curled multi-line region
            # is already a single line. The crop fitter resolves it next.
            active = sm > max(.5, .045 * float(sm.max()))
            active = ndi.maximum_filter1d(active, max(1, round(.4 * xh)))
            for t, bot in _runs(active):
                ys, xs = np.nonzero(sub[t:bot])
                if not len(xs) or len(xs) < .15 * xh * xh:
                    continue
                boxes.append((a + int(xs.min()), y0 + t, a + int(xs.max()) + 1, y0 + bot))
    return PixelPage(gray, clean, labels, cc, barriers, gutters, boxes, xh, nontext, boundaries)

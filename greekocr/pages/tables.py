"""Table delivery from pixels, with locally bounded rules and whitespace.

Layout regions are image-model proposals, never PDF text or evaluation labels.
The ordinary page fitter remains unchanged outside those regions. Inside a table
we remove strokes before labelling components, rather than rejecting a connected
frame together with the letters touching it. Final pieces are recognised
separately; text is never divided in proportion to a box's width.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import copy
import math
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray
from PIL import Image
from scipy import ndimage as ndi

from ..glyphs.components import EIGHT, _xheight, binarise
from .pixels import PixelPage, _gray, _records, _runs, _rule_mask
from .lines import CURVES, LineSegment, PageSegmentation, segment_page

__all__ = ['TextPiece', 'table_text_pieces', 'recognition_pieces', 'prepare_delivery']


RULE_SAMPLE_XHEIGHT_PX = 8  # sample pixels per x-height: normalize Hough work without assuming scan DPI.
HOUGH_HALF_TURN_STEPS = 1800  # angular samples per half-turn: resolve a thin rule over a long table edge.
RULE_VOTE_LENGTH_XH = 4  # x-heights of votes: require sustained line support before treating ink as a rule.
PREFIX_MIN_HEIGHT_XH = 8  # x-heights: refit only a substantial prose prefix above the first table.
RULE_MIN_LENGTH_XH = 8  # x-heights: a table stroke must exceed individual-glyph extents.
RULE_MAX_GAP_XH = 0.3  # x-heights: bridge short printed-rule breaks, not large unprinted intervals.
RULE_MAX_SLOPE = 0.12  # page minor-axis units per major-axis unit: retain near-axis table strokes.
RULE_MASK_WIDTH_XH = 0.16  # x-heights: remove the observed narrow table stroke before component labeling.
BINARIZE_WINDOW_PAGE = 0.04  # fraction of shorter page dimension: use the inherited local-paper threshold window.
MIN_XHEIGHT_PIXELS = 3.0  # sample pixels per x-height: floor when a table has no usable letter evidence.
FALLBACK_XHEIGHT_PAGE_DIVISOR = 100  # page short-side units per x-height: retain Q2's scale fallback when no bodies exist.
MIN_BODY_HEIGHT_PAGE = 0.002  # fraction of page height: ignore very small components when estimating type size.
MAX_BODY_HEIGHT_PAGE = 0.1  # fraction of page height: exclude large frame components from the type-size estimate.
MIN_BODY_WIDTH_PAGE = 0.0005  # fraction of page width: avoid numerical specks in the type-size estimate.
MAX_BODY_WIDTH_PAGE = 0.12  # fraction of page width: a page-spanning rule is not an individual body.
MIN_BODY_AREA_PAGE = 2e-06  # fraction of page area: reject tiny specks before estimating table type size.
COMPONENT_MAX_HEIGHT_XH = 3.5  # x-heights: keep bodies with marks after removing rules, excluding tall graphics.
COMPONENT_MAX_WIDTH_XH = 12  # x-heights: permit connected short words but exclude long surviving frame strokes.
COMPONENT_MIN_AREA_XH2 = 0.008  # square x-heights: retain detached accents after rule removal.
VERTICAL_RULE_MIN_HEIGHT_XH = 1.9  # x-heights: a very narrow tall remnant is still a rule.
RULE_REMNANT_MAX_WIDTH_XH = 0.25  # x-heights: narrow residual horizontal/vertical strokes are not letters.
GUTTER_INK_CLEARANCE_XH = 0.1  # x-heights: protect nearby letter pixels when adding a whitespace stop.
GUTTER_WINDOW_HEIGHT_XH = 12  # x-heights: collect repeated row evidence within a local table block.
GUTTER_WINDOW_STEP_XH = 6  # x-heights: overlap local table windows to retain finite gutter extents.
GUTTER_MAX_INK_SHARE = 0.08  # dimensionless projection ratio: gutter candidates must be nearly blank.
GUTTER_MIN_WIDTH_XH = 0.25  # x-heights: ignore sub-stroke whitespace slits.
GUTTER_SIDE_CONTEXT_XH = 5  # x-heights: require nearby text on both sides of a local gutter.
ROW_CLOSE_GAP_XH = 0.25  # x-heights: connect within-body holes before counting repeated rows.
ROW_MIN_HEIGHT_XH = 0.5  # x-heights: a repeated text row must span a substantial body height.
ROW_MIN_BODY_AREA_XH2 = 0.05  # square x-heights: row seeds require body-sized ink rather than punctuation.
ROW_LOCAL_BASELINE_SLACK_XH = 0.48  # x-heights: nearby contacts may follow skew while adjacent rows remain separate.
ROW_LOCAL_REACH_XH = 15  # x-heights: baseline agreement must have local horizontal support.
ROW_GROUP_BASELINE_SLACK_XH = 0.7  # x-heights: cap drift from a row group median while allowing curved contacts.
ROW_HORIZONTAL_COST = 0.01  # dimensionless distance weight: prefer baseline agreement with a small locality tie-break.
MARK_HORIZONTAL_REACH_XH = 0.6  # x-heights: detached marks travel only with a nearby established body.
MARK_TOP_REACH_XH = 1.05  # x-heights: allow an accent above the body without reaching the preceding row.
MARK_BOTTOM_REACH_XH = 0.35  # x-heights: retain nearby lower marks and punctuation with their body row.
MARK_VERTICAL_COST = 0.1  # dimensionless distance weight: use vertical distance to break horizontal mark-owner ties.
PIECE_SPLIT_GAP_XH = 0.55  # x-heights: split at conservative word gaps before independent recognition.
INITIAL_FONT_TOP_XH = 1.5  # x-heights above baseline: seed the capital guide before fitting observed classes.
INITIAL_FONT_BOTTOM_XH = 0.3  # x-heights below baseline: seed the descender guide before class fitting.
PIECE_INK_PADDING_XH = 0.08  # x-heights: preserve antialiased ink at the recovered piece envelope.
MIN_BORDER_PIECE_WIDTH_XH = 0.5  # x-heights: avoid creating a sub-glyph remainder at a table boundary.
FALLBACK_MAX_RULE_SLOPE = 0.08  # page x units per y unit: the conservative fallback requires a nearly vertical divider.
FALLBACK_CENTRE_MIN_PAGE = 0.3  # fraction of page width: fallback table dividers must be central, not scan-edge shadows.
FALLBACK_RULE_RADIUS_XH = 0.2  # x-heights: inspect a narrow corridor around the fallback divider.
FALLBACK_START_MIN_PAGE = 0.15  # fraction of page height: fallback is for a later-starting block after prose.
FALLBACK_MAX_RULE_WIDTH_XH = 1.5  # x-heights: reject a broad separator corridor as a table rule.
FALLBACK_PROSE_CORRIDOR_XH = 0.35  # x-heights: test whether preceding text actually crosses the proposed divider.
FALLBACK_PROSE_MIN_INK_XH = 0.12  # x-heights of row ink: count substantial prose across the proposed divider.
FALLBACK_PROSE_CLOSE_XH = 0.2  # x-heights: close tiny intra-body gaps before counting prose rows.
FALLBACK_PROSE_MAX_HEIGHT_XH = 2.5  # x-heights: a crossing prose band must not be a large graphic.
FALLBACK_REGION_PADDING_XH = 0.3  # x-heights: retain boundary ink at the recovered fallback table region.
FALLBACK_CENTRE_MAX_PAGE = 0.7  # fraction of page width: upper edge of the central-divider fallback search.

@dataclass
class TextPiece:
    """A recognition crop and its tight TOPLEFT envelope in original pixels."""
    box: tuple[int, int, int, int]
    line_index: int
    line: LineSegment
    table_id: str | None = None
    cell_id: str | None = None
    address: dict = field(default_factory=dict)

    def to_record(self, index: int, image_size: Sequence[int], page_size: Sequence[float]) -> dict:
        """Serialize pixel and page-unit boxes using the actual image/page ratios."""
        sx, sy = page_size[0] / image_size[0], page_size[1] / image_size[1]
        a, t, b, bot = self.box
        return dict(index=index, box_pixels=list(self.box),
                    box_page=[a*sx, t*sy, b*sx, bot*sy], coord_origin='TOPLEFT',
                    line_index=self.line_index, table_id=self.table_id, cell_id=self.cell_id,
                    cell_id_kind='detector_piece_group' if self.cell_id else None, **self.address)


HORIZONTAL_RULE_MIN_WIDTH_XH = 2  # x-heights: a wide narrow remnant is a horizontal rule rather than a letter.
FALLBACK_EARLY_RULE_REACH_XH = 2  # x-heights: reject fallback dividers already present beside preceding prose.
FALLBACK_PROSE_SIDE_REACH_XH = 3  # x-heights: require prose extending on both sides of the proposed divider.
FALLBACK_SUPPORT_WIDTH_XH = 3  # x-heights: divider evidence needs text pieces wider than an isolated body.
FALLBACK_DUPLICATE_START_XH = 2  # x-heights: merge near-duplicate starts of the same fallback region.
PARTITION_MIN_GAP_XH = 2  # x-heights: partition table pieces only at a substantial blank interval.

BINARIZE_MIN_PIXELS = 15  # source pixel samples: minimum odd paper-estimation window on small images.


def rule_ink(ink, xh):
    """Both directions, at their observed extent; never extrapolate a rule."""
    import cv2
    scale=min(1.,RULE_SAMPLE_XHEIGHT_PX/xh)
    small=cv2.resize(ink.astype('uint8'),None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
    unit=xh*scale
    paths=cv2.HoughLinesP(small,1,np.pi/HOUGH_HALF_TURN_STEPS,threshold=max(2,round(RULE_VOTE_LENGTH_XH*unit)),
                          minLineLength=RULE_MIN_LENGTH_XH*unit,maxLineGap=RULE_MAX_GAP_XH*unit)
    mask=np.zeros_like(ink,dtype='uint8')
    if paths is not None:
        for x0,y0,x1,y1 in paths.reshape(-1,4):
            dx,dy=abs(x1-x0),abs(y1-y0)
            if min(dx,dy)>RULE_MAX_SLOPE*max(dx,dy):
                continue
            pts=[round(v/scale) for v in (x0,y0,x1,y1)]
            cv2.line(mask,tuple(pts[:2]),tuple(pts[2:]),1,max(1,round(RULE_MASK_WIDTH_XH*xh)))
    # Intersections and heavy double frames may be wider than one Hough path.
    return mask.astype(bool) | _rule_mask(ink,xh) | _rule_mask(ink.T,xh).T


def table_pixels(page, xheight=None):
    """Keep letter components inside and touching a frame, removing only strokes."""
    gray = _gray(page)
    h, w = gray.shape
    ink = binarise(gray, window=max(BINARIZE_MIN_PIXELS, round(BINARIZE_WINDOW_PAGE*min(h,w))) | 1)
    labels, _ = ndi.label(ink, EIGHT)
    cc = _records(gray, labels)
    if not len(cc):
        return PixelPage(gray, ink, labels, cc, np.zeros_like(ink), [], [], xheight or MIN_XHEIGHT_PIXELS)
    heights, widths = cc[:,3]-cc[:,1], cc[:,2]-cc[:,0]
    plausible = cc[(heights > MIN_BODY_HEIGHT_PAGE*h) & (heights < MAX_BODY_HEIGHT_PAGE*h) & (widths > MIN_BODY_WIDTH_PAGE*w)
                   & (widths < MAX_BODY_WIDTH_PAGE*w) & (cc[:,4] > MIN_BODY_AREA_PAGE*h*w)]
    xh = max(MIN_XHEIGHT_PIXELS, _xheight(plausible[:,3]-plausible[:,1]) if len(plausible) else xheight or min(h,w)/FALLBACK_XHEIGHT_PAGE_DIVISOR)
    rules = rule_ink(ink, xh)
    clean = ink & ~rules
    labels, _ = ndi.label(clean, EIGHT)
    cc = _records(gray, labels)
    # This rejection acts AFTER rule removal and only on the component itself.
    # It never clears the bounding rectangle of an outer frame.
    keep = np.zeros(labels.max()+1, bool)
    if len(cc):
        good = ((cc[:,3]-cc[:,1] <= COMPONENT_MAX_HEIGHT_XH*xh) & (cc[:,2]-cc[:,0] <= COMPONENT_MAX_WIDTH_XH*xh)
                & (cc[:,4] >= COMPONENT_MIN_AREA_XH2*xh*xh))
        good &= ~(((cc[:,3]-cc[:,1])>VERTICAL_RULE_MIN_HEIGHT_XH*xh) & ((cc[:,2]-cc[:,0])<RULE_REMNANT_MAX_WIDTH_XH*xh))
        good &= ~(((cc[:,2]-cc[:,0])>HORIZONTAL_RULE_MIN_WIDTH_XH*xh) & ((cc[:,3]-cc[:,1])<RULE_REMNANT_MAX_WIDTH_XH*xh))
        keep[cc[good,5].astype(int)] = True
    clean &= keep[labels]
    labels, _ = ndi.label(clean, EIGHT)
    cc = _records(gray, labels)
    gutters = _local_gutters(clean, xh)
    stops = rules.copy()
    for a,t,b,bot in gutters:
        # A repeated lane supplies a split only where this row is actually
        # empty. It must not cut a spanning header or erase any letter pixels.
        stops[t:bot,a:b] |= ~ndi.maximum_filter(clean[t:bot,a:b], size=(1,max(1,round(GUTTER_INK_CLEARANCE_XH*xh))))
    return PixelPage(gray, clean, labels, cc, stops, gutters, [], xh)


def _local_gutters(ink, xh):
    """Narrow aligned gaps supported by three rows, within overlapping blocks."""
    h,w=ink.shape;found=[]
    depth=max(1,round(GUTTER_WINDOW_HEIGHT_XH*xh));step=max(1,round(GUTTER_WINDOW_STEP_XH*xh))
    for t in range(0,h,step):
        bot=min(h,t+depth);band=ink[t:bot]
        profile=band.sum(axis=0)
        if not profile.any():continue
        low=profile<=GUTTER_MAX_INK_SHARE*np.percentile(profile[profile>0],75)
        for a,b in _runs(low):
            if a==0 or b==w or b-a<GUTTER_MIN_WIDTH_XH*xh:continue
            sides=[band[:,max(0,a-round(GUTTER_SIDE_CONTEXT_XH*xh)):a],band[:,b:min(w,b+round(GUTTER_SIDE_CONTEXT_XH*xh))]]
            counts=[]
            for side in sides:
                rows=ndi.binary_closing(side.any(axis=1),structure=np.ones(max(1,round(ROW_CLOSE_GAP_XH*xh))))
                counts.append(sum(e-s>ROW_MIN_HEIGHT_XH*xh for s,e in _runs(rows)))
            if min(counts)>=3:found.append((a,t,b,bot))
    return found


def _row_groups(cc, xh):
    """Bottom contacts seed rows; detached accents/punctuation join their bodies."""
    bodies = cc[(cc[:,3]-cc[:,1] >= ROW_MIN_HEIGHT_XH*xh) & (cc[:,4] >= ROW_MIN_BODY_AREA_XH2*xh*xh)]
    groups = []
    for q in sorted(bodies, key=lambda q:q[3]):
        # A neighbour's local baseline accommodates scan skew without merging
        # adjacent rows. A broad page-wide median does not follow curvature.
        candidates = []
        for i,g in enumerate(groups):
            nearest = min(g, key=lambda r:abs((r[0]+r[2]-q[0]-q[2])/2))
            dx = max(0, q[0]-nearest[2], nearest[0]-q[2])
            dy = abs(q[3]-nearest[3])
            if dy <= ROW_LOCAL_BASELINE_SLACK_XH*xh and dx < ROW_LOCAL_REACH_XH*xh and abs(q[3]-np.median(np.array(g)[:,3]))<ROW_GROUP_BASELINE_SLACK_XH*xh:
                candidates.append((dy+ROW_HORIZONTAL_COST*dx, i))
        if candidates:
            groups[min(candidates)[1]].append(q)
        else:
            groups.append([q])
    used = {int(q[5]) for g in groups for q in g}
    for q in cc:
        if int(q[5]) in used:
            continue
        options=[]
        for i,g in enumerate(groups):
            for r in g:
                dx=max(0,q[0]-r[2],r[0]-q[2])
                if dx>MARK_HORIZONTAL_REACH_XH*xh:
                    continue
                if r[1]-MARK_TOP_REACH_XH*xh <= (q[1]+q[3])/2 <= r[3]+MARK_BOTTOM_REACH_XH*xh:
                    options.append((dx+abs(q[3]-r[3])*MARK_VERTICAL_COST,i))
        if options:
            groups[min(options)[1]].append(q)
    return groups


def split_group(group, barriers, xh):
    """Split at rules or conservative word gaps, before recognition.

    Gutters need no full-page vote: a word gap is a safe split even when no
    table column continues above or below this row. Accents travel with bodies.
    """
    pieces=[]
    for q in sorted(group, key=lambda q:q[0]):
        if not pieces:
            pieces.append([q]); continue
        g=np.array(pieces[-1]); right=g[:,2].max()
        a,b=int(min(right,q[0])),int(max(right,q[0]))
        t=max(0,int(max(g[:,1].min(),q[1])))
        bot=min(barriers.shape[0],int(min(g[:,3].max(),q[3])))
        blocked = b>a and bot>t and barriers[t:bot,a:b].any()
        if q[0]-right > PIECE_SPLIT_GAP_XH*xh or blocked:
            pieces.append([q])
        else:
            pieces[-1].append(q)
    return pieces


def _line_from_group(group, p, dx, dy, table_index):
    from .font import fit_guides
    q=np.array(group)
    a,t,b,bot=[int(v) for v in (q[:,0].min(),q[:,1].min(),q[:,2].max(),q[:,3].max())]
    body=q[(q[:,3]-q[:,1])>=ROW_MIN_HEIGHT_XH*p.xheight]
    if not len(body):
        return None
    xs=(body[:,0]+body[:,2])/2
    base=np.interp(np.arange(a,b),xs[np.argsort(xs)],body[np.argsort(xs),3])
    base=ndi.gaussian_filter1d(base,max(1.,p.xheight))
    xh=p.xheight
    line=LineSegment(a,b,base,base-INITIAL_FONT_TOP_XH*xh,base-xh,base+INITIAL_FONT_BOTTOM_XH*xh,
                     np.full(b-a,max(0,t-PIECE_INK_PADDING_XH*xh)),np.full(b-a,min(p.gray.shape[0],bot+PIECE_INK_PADDING_XH*xh)),xh,
                     column=table_index+1,support=len(body),geometry_source='table-pixel-piece',
                     component_ids=tuple(q[:,5].astype(int)),
                     neighbours=dict(above=np.full(b-a,-1),below=np.full(b-a,-1)))
    fit_guides(p,[line])
    # Preserve the observed ink including diacritics; no neighbour seam can
    # extend this piece into a different row or a rule.
    for name in CURVES:
        setattr(line,name,getattr(line,name)+dy)
    line.x0+=dx;line.x1+=dx
    line.component_ids=()  # local labels must not alias page component IDs
    return line,(a+dx,t+dy,b+dx,bot+dy)


def table_text_pieces(page: Image.Image | NDArray[Any], region: Sequence[float],
                      table_id: str = 'table-0', table_index: int = 0) -> list[TextPiece]:
    """Return pixel-derived within-row pieces for an image-layout table region."""
    gray=_gray(page);h,w=gray.shape
    a,t,b,bot=[int(v) for v in (max(0,math.floor(region[0])),max(0,math.floor(region[1])),
                              min(w,math.ceil(region[2])),min(h,math.ceil(region[3])))]
    if b<=a or bot<=t:
        raise ValueError('table region must have positive area inside the page')
    p=table_pixels(gray[t:bot,a:b])
    pieces=[]
    for row_index,row in enumerate(_row_groups(p.components,p.xheight)):
        for group in split_group(row,p.barriers,p.xheight):
            built=_line_from_group(group,p,a,t,table_index)
            if built is not None:
                line,box=built
                line.row_source=f'{table_id}:component-row-{row_index}'
                pieces.append(TextPiece(box,-1,line,table_id))
    pieces.sort(key=lambda s:(round(float(np.median(s.line.baseline))/p.xheight),s.box[0]))
    for i,piece in enumerate(pieces):
        # Provisional geometry group, NOT a claim of TableFormer row/column ID.
        piece.cell_id=f'{table_id}:piece-{i}'
    return pieces


def line_piece(line, index, image_size):
    w,h=image_size
    a,b=max(0,line.x0),min(w,line.x1)
    t=max(0,int(np.floor(line.top.min())))
    bot=min(h,int(np.ceil(line.bottom.max())))
    return TextPiece((a,t,b,bot),index,line)


def detector_pieces(page, lines, table_regions=()):
    """Replace table-intersecting lines with recovered table pieces.

    A region is (id, TOPLEFT pixel box). The normal line fitter is retained for
    everything outside layout's image-derived tables. Border lines are split
    geometrically, then recognised independently, never by string slicing.
    """
    gray=_gray(page);h,w=gray.shape
    regions=[(str(i),tuple(map(float,b))) for i,b in table_regions]
    result=[]
    for li,line in enumerate(lines):
        if line.discounted is not None:
            continue
        piece=line_piece(line,li,(w,h))
        pending=[piece]
        for _,(a,t,b,bot) in regions:
            rest=[]
            for old in pending:
                x0,y0,x1,y1=old.box
                if max(x0,a)>=min(x1,b) or max(y0,t)>=min(y1,bot):
                    rest.append(old);continue
                # Existing curves above/below the table remain untouched. For
                # a row entering its side, keep only outside horizontal parts.
                mid=float(np.median(old.line.baseline)-.5*old.line.xheight)
                if not t<=mid<bot:
                    rest.append(old);continue
                for left,right in [(x0,min(x1,math.floor(a))),(max(x0,math.ceil(b)),x1)]:
                    if right-left < MIN_BORDER_PIECE_WIDTH_XH*line.xheight:
                        continue
                    sl=slice(left-old.line.x0,right-old.line.x0)
                    part=copy.copy(old.line);part.x0=left;part.x1=right
                    for name in CURVES:setattr(part,name,getattr(old.line,name)[sl].copy())
                    part.neighbours={k:(np.asarray(v)[sl].copy() if np.ndim(v) else v)
                                     for k,v in old.line.neighbours.items()}
                    rest.append(line_piece(part,li,(w,h)))
            pending=rest
        result.extend(pending)
    for ti,(tid,region) in enumerate(regions):
        result.extend(table_text_pieces(gray,region,tid,ti))
    return result


def supplemental_regions(page, lines):
    """Find a later-starting ruled block overlooked by image layout.

    This deliberately conservative fallback requires a central vertical divider,
    at least eight letter heights long, with text on both sides and a preceding
    full-width paragraph. It does not extend that divider into the paragraph.
    """
    active=[l for l in lines if l.discounted is None]
    if not active:return []
    gray=_gray(page);h,w=gray.shape;xh=float(np.median([l.xheight for l in active]))
    ink=binarise(gray,window=max(BINARIZE_MIN_PIXELS,round(BINARIZE_WINDOW_PAGE*min(h,w)))|1)
    import cv2
    paths=cv2.HoughLinesP(ink.astype('uint8'),1,np.pi/HOUGH_HALF_TURN_STEPS,threshold=max(2,round(RULE_VOTE_LENGTH_XH*xh)),
                         minLineLength=RULE_MIN_LENGTH_XH*xh,maxLineGap=RULE_MAX_GAP_XH*xh)
    if paths is None:return []
    clusters=[]
    for x0,y0,x1,y1 in paths.reshape(-1,4):
        if abs(x1-x0)>FALLBACK_MAX_RULE_SLOPE*abs(y1-y0):continue
        mid=(x0+x1)/2
        if not FALLBACK_CENTRE_MIN_PAGE*w<mid<FALLBACK_CENTRE_MAX_PAGE*w:continue
        peers=[g for g in clusters if abs(mid-np.median([q[0] for q in g]))<xh]
        q=(mid,min(y0,y1),max(y0,y1))
        if peers:peers[0].append(q)
        else:clusters.append([q])
    candidates=[]
    spans=[]
    for group in clusters:
        mid=np.median([q[0] for q in group]);rows=np.zeros(h,bool)
        for _,t,bot in group:rows[int(t):int(bot)+1]=True
        rows=ndi.binary_closing(rows,structure=np.ones(max(1,round(xh))))
        spans.extend((mid,t,bot) for t,bot in _runs(rows))
    for mid,t,bot in spans:
        a,b=mid-FALLBACK_RULE_RADIUS_XH*xh,mid+FALLBACK_RULE_RADIUS_XH*xh
        if not (FALLBACK_CENTRE_MIN_PAGE*w<mid<FALLBACK_CENTRE_MAX_PAGE*w and t>FALLBACK_START_MIN_PAGE*h and bot-t>RULE_MIN_LENGTH_XH*xh and b-a<FALLBACK_MAX_RULE_WIDTH_XH*xh):continue
        # A broken full-height prose divider is not a later-starting table.
        # Require several body rows through the proposed boundary above it;
        # a centred running head alone cannot establish a full-width paragraph.
        stripe=ink[:int(t),max(0,int(mid-FALLBACK_PROSE_CORRIDOR_XH*xh)):min(w,int(mid+FALLBACK_PROSE_CORRIDOR_XH*xh))]
        occupied=ndi.binary_closing(stripe.sum(axis=1)>FALLBACK_PROSE_MIN_INK_XH*xh,
                                    structure=np.ones(max(1,round(FALLBACK_PROSE_CLOSE_XH*xh))))
        crossing_rows=[(s,e) for s,e in _runs(occupied) if ROW_MIN_HEIGHT_XH*xh<e-s<FALLBACK_PROSE_MAX_HEIGHT_XH*xh]
        if len(crossing_rows)<3:continue
        if any(q[1]<FALLBACK_START_MIN_PAGE*h for group in clusters for q in group if abs(q[0]-mid)<FALLBACK_EARLY_RULE_REACH_XH*xh):continue
        beside=[l for l in active if t<np.median(l.baseline)<bot]
        if sum(l.x1<mid for l in beside)<3 or sum(l.x0>mid for l in beside)<3:continue
        above=[l for l in active if np.median(l.baseline)<t]
        if not any(l.x0<mid-FALLBACK_PROSE_SIDE_REACH_XH*xh for l in above) or not any(l.x1>mid+FALLBACK_PROSE_SIDE_REACH_XH*xh for l in above):continue
        supported=[l for l in beside if l.x1-l.x0>FALLBACK_SUPPORT_WIDTH_XH*xh]
        if not supported:continue
        left=min(l.x0 for l in supported);right=max(l.x1 for l in supported)
        region=(max(0,left-FALLBACK_REGION_PADDING_XH*xh),max(0,t-xh),min(w,right+FALLBACK_REGION_PADDING_XH*xh),min(h,bot+FALLBACK_REGION_PADDING_XH*xh))
        if any(abs(t-r[1])<FALLBACK_DUPLICATE_START_XH*xh for _,r in candidates):continue
        candidates.append((f'pixel-table-{len(candidates)}',region))
    # One interrupted prose rule is insufficient evidence for a table; require
    # repeated, separated blocks for this fallback. Heron's table proposals do
    # not need this restriction.
    return candidates if len(candidates)>=2 else []


def recognition_pieces(page: Image.Image | NDArray[Any], lines: list[LineSegment],
                       table_regions: Sequence[tuple[str, Sequence[float]]] = (), *,
                       supplement: bool = True) -> tuple[list[TextPiece], list, PageSegmentation | None]:
    """Shared delivery path for the plugin and offline review harness."""
    regions=list(table_regions)
    if supplement and not regions:
        regions=supplemental_regions(page,lines)
    prefix=None
    source=lines
    if regions and lines:
        first=min(b[1] for _,b in regions)
        xh=float(np.median([l.xheight for l in lines]))
        if first>PREFIX_MIN_HEIGHT_XH*xh:
            prefix=segment_page(_gray(page)[:int(first)])
            source=[l for l in lines if np.median(l.baseline)>=int(first)]+prefix.lines
        # A sentence BETWEEN table blocks must not inherit either divider.
        # Merge overlapping region extents first (e.g. facing table leaves).
        for top,bottom in _interior_bands(regions, xh):
            band=segment_page(_gray(page)[top:bottom])
            for line in band.lines:
                for curve in CURVES:setattr(line,curve,getattr(line,curve)+top)
                line.component_ids=()
            source=[l for l in source if not top<=np.median(l.baseline)<bottom]+band.lines
    return detector_pieces(page,source,regions),regions,prefix


def _interior_bands(regions, xh):
    extents=[]
    for _,box in sorted(regions,key=lambda r:r[1][1]):
        top,bottom=math.floor(box[1]),math.ceil(box[3])
        if extents and top<=extents[-1][1]:extents[-1][1]=max(extents[-1][1],bottom)
        else:extents.append([top,bottom])
    return [(a[1],b[0]) for a,b in zip(extents,extents[1:]) if b[0]-a[1]>PARTITION_MIN_GAP_XH*xh]


def prepare_delivery(page: Image.Image | NDArray[Any], result: PageSegmentation,
                     table_regions: Sequence[tuple[str, Sequence[float]]] = (), *,
                     supplement: bool = True) -> tuple[PageSegmentation, list[TextPiece], list]:
    """Attach table recovery to a normal segmentation, retaining audit candidates.

    Returns (addressed segmentation, recognition pieces, regions).
    With no proposals, original line geometry is retained and piece addresses
    are attached to the original segmentation.
    """
    from .lines import _diagnostics, _addresses
    from .structure import _attach_structure, _table_structure
    pieces,regions,prefix=recognition_pieces(page,result.lines,table_regions,supplement=supplement)
    if not regions:
        pieces=detector_pieces(page,result.lines)
        _attach_structure(result,pieces)
        return result,pieces,regions
    gray=result.pixels.gray;h,w=gray.shape
    if prefix is not None:stop=prefix.pixels.gray.shape[0]
    lines=[]
    # Retain superseded candidates and their reasons, never render them.
    for old in result.lines:
        line=copy.deepcopy(old)
        if line.discounted is None:
            line.discounted='superseded by bounded table/prose delivery'
        line.neighbours={k:np.full(line.x1-line.x0,-1) for k in ('above','below')}
        lines.append(line)
    for piece in pieces:
        piece.line=copy.deepcopy(piece.line)
        piece.line_index=len(lines)
        piece.line.neighbours={k:np.full(piece.line.x1-piece.line.x0,-1) for k in ('above','below')}
        lines.append(piece.line)
    p=copy.copy(result.pixels)
    p.ink=p.ink.copy();p.barriers=p.barriers.copy()
    if prefix is not None:
        p.ink[:stop]=prefix.pixels.ink;p.barriers[:stop]=prefix.pixels.barriers
    from .pixels import prepare_pixels
    xh=float(np.median([l.xheight for l in result.lines]))
    for top,bottom in _interior_bands(regions,xh):
        local=prepare_pixels(gray[top:bottom])
        p.ink[top:bottom]=local.ink;p.barriers[top:bottom]=local.barriers
    for _,box in regions:
        a,t,b,bot=map(int,(max(0,np.floor(box[0])),max(0,np.floor(box[1])),min(w,np.ceil(box[2])),min(h,np.ceil(box[3]))))
        local=table_pixels(gray[t:bot,a:b])
        p.ink[t:bot,a:b]=local.ink;p.barriers[t:bot,a:b]=local.barriers
    p.labels,_=ndi.label(p.ink,EIGHT);p.components=_records(gray,p.labels)
    # Source/component diagnostics refer to the *new* mask, including recovered
    # text, rather than silently measuring the old mask that deleted a column.
    ownership={i:[] for i in range(len(lines))}
    for q in p.components:
        candidates=[]
        for piece in pieces:
            a,t,b,bot=piece.box
            area=max(0,min(b,q[2])-max(a,q[0]))*max(0,min(bot,q[3])-max(t,q[1]))
            if area>0:candidates.append((area,piece.line_index))
        if candidates:ownership[max(candidates)[1]].append(int(q[5]))
    for i,line in enumerate(lines):line.component_ids=tuple(ownership[i])
    p.gutters=[];p.column_boundaries=[]
    p.nontext_boxes=[box for box in p.nontext_boxes if not any(
        max(box[0],r[0])<min(box[2],r[2]) and max(box[1],r[1])<min(box[3],r[3]) for _,r in regions)]
    p.boxes=[tuple(map(int,s.box)) for s in pieces]
    _addresses(lines,p.boxes)
    diagnostics=_diagnostics(p,lines)
    diagnostics['table_delivery']=dict(regions=[dict(id=i,box_pixels=list(b)) for i,b in regions],
        pieces=len(pieces),table_pieces=sum(p.table_id is not None for p in pieces),
        prefix_refitted=prefix is not None)
    delivered=PageSegmentation(lines,p.boxes,result.xheight,diagnostics,p)
    _,boundaries=_table_structure(gray,regions)
    _attach_structure(delivered,pieces,boundaries=boundaries)
    return delivered,pieces,regions

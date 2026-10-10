"""Local upright fitting with ordered words and parametric page-space guides.

The horizontal fitter is intentionally an unchanged primitive. Each invocation
has an explicit local frame; no vertical curve is misrepresented as page y(x).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
import copy
from typing import Any, Sequence
from time import perf_counter

import numpy as np
from PIL import Image, ImageOps

from .orientation import (Orientation, QuarterTurn, _Recognizer, canonical_word_crop,
                          discover_directions, measure_orientation, recognizer_polarity)
from .page_text_lines import CURVES, segment_page
from .pixel_segments import _runs
from .table_lines import prepare_delivery

__all__ = ['OrientedWord', 'OrientedPage', 'oriented_page']


@dataclass
class OrientedWord:
    """A separately recognizable word and its local guides, in a reversible frame."""
    index: int
    group_id: str
    line_index: int
    box: tuple
    frame: QuarterTurn
    orientation: Orientation
    guides: dict
    crop: Image.Image = field(repr=False)
    text: str = ''
    recognition_confidence: float | None = None
    table_id: str | None = None
    cell_id: str | None = None

    def to_record(self, image_size: Sequence[int], page_size: Sequence[float] | None = None) -> dict:
        """Serialize original-frame corners, local guides and separate confidences."""
        page_size = page_size or image_size
        scale = np.array(page_size)/np.array(image_size)
        corners = self.frame.rectangle(self.box)
        envelope = [*corners.min(0), *corners.max(0)]
        return dict(index=self.index,word_id=f'w{self.index:06d}',group_id=self.group_id,line_index=self.line_index,
                    text=self.text,from_ocr=True,text_direction='left_to_right',
                    recognition_confidence=self.recognition_confidence,
                    **self.orientation.to_record(),box_pixels=envelope,
                    box_page=(np.array(envelope)*np.tile(scale,2)).tolist(),
                    corners_pixels=corners.tolist(),corners_page=(corners*scale).tolist(),
                    coord_origin='TOPLEFT',local_box=list(self.box),
                    local_to_pixels=np.linalg.inv(self.frame.matrix).tolist(),
                    local_to_page=(np.diag([*scale,1.])@np.linalg.inv(self.frame.matrix)).tolist(),
                    geometry_orientation_cw=self.frame.orientation_cw,
                    geometry_is_hypothesis=self.orientation.orientation_cw is None,
                    guides_local=self.guides,
                    guides_pixels={k:self.frame.points(v,inverse=True).tolist() for k,v in self.guides.items()},
                    guides_page={k:(self.frame.points(v,inverse=True)*scale).tolist() for k,v in self.guides.items()},
                    geometry_units=dict(local='crop pixels',pixels='current input raster pixels',page='current page units'),
                    table_id=self.table_id,cell_id=self.cell_id)


@dataclass
class OrientedPage:
    """Legacy horizontal records plus independent local-frame words and evidence."""
    words: list[OrientedWord]
    dominant: Orientation
    proposals: list[dict]
    groups: list[dict]
    segmentation: object
    pieces: list
    orientation_seconds: float = 0.


def _word_boxes(image, piece, gray=None):
    """Split only at empty ink gaps inside an already boundary-safe text piece."""
    import cv2
    a,t,b,bot = piece.box
    a,t,b,bot = max(0,a),max(0,t),min(image.width,b),min(image.height,bot)
    if b <= a or bot <= t:
        return []
    gray = np.asarray(image) if gray is None else gray
    _, ink = cv2.threshold(gray[t:bot,a:b],0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    xh = piece.line.xheight
    occupied = (ink > 0).any(0)
    gaps = [(s,e) for s,e in _runs(~occupied) if e-s >= .35*xh and s > 0 and e < b-a]
    bounds = [0]+[(s+e)//2 for s,e in gaps]+[b-a]
    out = []
    for s,e in zip(bounds,bounds[1:]):
        yy,xx = np.nonzero(ink[:,s:e])
        if not len(xx):
            continue
        # Partition the parent rectangle instead of re-thresholding its ink
        # envelope. A faint accent or cell fragment may be below this word-gap
        # threshold while still being part of the accepted detector delivery.
        out.append((a+s,t,a+e,bot))
    return out


def _fit_group(image, frame, decision, gid, regions, start, *, segmentation=None, pieces=None, supplement=True):
    local = frame.image(image)
    mapped_regions = []
    for key, box in regions:
        points = frame.rectangle(box,inverse=False)
        mapped_regions.append((key,[*points.min(0),*points.max(0)]))
    if segmentation is None:
        segmentation = segment_page(local)
        segmentation,pieces,_ = prepare_delivery(local,segmentation,mapped_regions,supplement=supplement)
    words = []; gray = np.asarray(local)
    for piece in pieces:
        if piece.line.discounted is not None:
            continue
        # Boundary-safe table pieces are already the part-1 delivery contract.
        # Re-splitting/tightening them lost accents and token ownership in part 3.
        boxes = [piece.box] if piece.table_id is not None else _word_boxes(local,piece,gray)
        for box in boxes:
            x0,_,x1,_ = box
            xs = np.arange(max(x0,piece.line.x0),min(x1,piece.line.x1))
            # Keep curve endpoints and scale-relative samples; interpolation is
            # defined in the local frame, not by sorting inverse-mapped x values.
            if not len(xs):
                continue
            ix = np.unique(np.r_[np.arange(0,len(xs),max(1,round(.25*piece.line.xheight))),len(xs)-1])
            xx = xs[ix]; off = xx-piece.line.x0
            guides = {k:np.c_[xx,getattr(piece.line,k)[off]].tolist() for k in CURVES}
            ori = replace(decision,evidence={**decision.evidence,'inherited_from':gid,'source':'line/block-neighbours'})
            words.append(OrientedWord(start+len(words),gid,piece.line_index,box,frame,ori,guides,
                                      canonical_word_crop(local.crop(box)),table_id=piece.table_id,cell_id=piece.cell_id))
    return words,segmentation,pieces


def oriented_page(image: Image.Image, table_regions: Sequence[tuple[str, Sequence[float]]] = (), *,
                  recognizer: _Recognizer | None = None, use_osd: bool = False,
                  segmentation: Any = None, pieces: list | None = None,
                  dominant: Orientation | None = None, discover: bool = True,
                  supplement: bool = True) -> OrientedPage:
    """Discover directions, normalize groups, fit, split and inverse-map words.

    Passing a precomputed segmentation reuses only the unchanged upright base;
    local discovery still precedes all newly normalized fits. Unknown polarity
    retains both readings and records the geometry's working hypothesis.
    """
    image = image.convert('L')
    orientation_started = perf_counter()
    proposals = discover_directions(image) if discover else []
    from .orientation_regions import page_regions
    if dominant is None:
        dominant = measure_orientation(image,use_osd=use_osd,unit='page')
    dominant, region_rows, proposals = page_regions(image, proposals=proposals, dominant=dominant, use_osd=use_osd)
    orientation_seconds = perf_counter()-orientation_started
    working = dominant.orientation_cw
    if working is None:
        working = 90 if dominant.axis == 'vertical' else 0
    frame = QuarterTurn(*image.size,working)
    # Existing part-two records can only be reused in the very same pixel frame.
    if working != 0:
        segmentation = pieces = None
    words,result,pieces = _fit_group(image,frame,dominant,'page',table_regions,0,
                                    segmentation=segmentation,pieces=pieces,supplement=supplement)
    groups = [dict(id='page',box=[0,0,*image.size],frame=frame.matrix.tolist(),**dominant.to_record())]
    # Pixel-detected tables have the same boundary-safe delivery contract as
    # layout-supplied tables. Their pieces are in the main fit's local frame;
    # pool their envelopes and map back before checking local proposals.
    protected_tables = list(table_regions)
    declared = {tid for tid,_ in table_regions}
    detected = {}
    for piece in pieces:
        if piece.table_id is not None and piece.table_id not in declared:
            detected.setdefault(piece.table_id,[]).append(frame.rectangle(piece.box))
    for tid,rectangles in detected.items():
        corners = np.concatenate(rectangles)
        protected_tables.append((tid,[*corners.min(0),*corners.max(0)]))
    normalized_tables = set()
    table_decisions = {}
    for region in region_rows[1:]:
        decision = region['decision']
        box = tuple(map(int, (np.floor(region['box'][0]), np.floor(region['box'][1]),
                              np.ceil(region['box'][2]), np.ceil(region['box'][3]))))
        def inherit_existing():
            for word in words:
                centre = word.frame.rectangle(word.box).mean(0)
                if box[0] <= centre[0] <= box[2] and box[1] <= centre[1] <= box[3]:
                    word.group_id = region['id']
                    word.orientation = replace(decision, evidence={**decision.evidence, 'inherited_from':region['id']})
        if decision.orientation_cw == working or (decision.orientation_cw is None and decision.axis == dominant.axis):
            # Keep the established geometry, including table boundaries. A
            # sparse or third-direction region keeps unknown on its words too.
            inherit_existing()
            groups.append(dict(id=region['id'],box=list(box),frame=frame.matrix.tolist(),**decision.to_record()))
            continue
        # Layout has already established table bounds. Only normalize a table
        # as a whole: local chains must never erase its boundary-safe delivery.
        local_tables = []
        for tid,b in protected_tables:
            if max(box[0],b[0]) < min(box[2],b[2]) and max(box[1],b[1]) < min(box[3],b[3]):
                if tid in normalized_tables:
                    break
                table_key = (tid, *b)
                if table_key not in table_decisions:
                    table_orientation_started = perf_counter()
                    table_decisions[table_key] = measure_orientation(image.crop(b), use_osd=use_osd)
                    orientation_seconds += perf_counter()-table_orientation_started
                table_decision = table_decisions[table_key]
                if table_decision.orientation_cw is None or table_decision.orientation_cw == working:
                    break
                # The entire table's guide fit must agree; one perpendicular
                # header does not authorize turning the surrounding digits.
                if table_decision.orientation_cw != decision.orientation_cw:
                    break
                decision = table_decision
                box = tuple(map(int,b)); local_tables = [(tid,b)]
                normalized_tables.add(tid)
                break
        else:
            tid = None
        if tid is not None and not local_tables:
            # A header cannot change a preserved table piece's crop frame.
            decision = replace(decision, orientation_cw=None, polarity_confidence=0.,
                               evidence={**decision.evidence, 'unapplied_candidate':decision.orientation_cw,
                                         'polarity_source':'table-local-reading-unresolved'})
            inherit_existing()
            groups.append(dict(id=region['id'], box=list(box), delivery='table-region-preserved', **decision.to_record()))
            continue
        local_angle = decision.orientation_cw
        if local_angle is None:
            local_angle = 90 if decision.axis == 'vertical' else 0
        crop = image.crop(box)
        pad = max(1,round(5*region['xheight']))
        crop = ImageOps.expand(crop,border=pad,fill=int(np.percentile(np.asarray(crop),90)))
        local_frame = QuarterTurn(crop.width,crop.height,local_angle,(box[0]-pad,box[1]-pad))
        local_words,_,_ = _fit_group(crop,local_frame,decision,region['id'],local_tables,0,supplement=supplement)
        if not local_words:
            decision = replace(decision, orientation_cw=None, polarity_confidence=0.,
                               evidence={**decision.evidence, 'unapplied_candidate':decision.orientation_cw,
                                         'polarity_source':'no-local-lines'})
            inherit_existing()
            groups.append(dict(id=region['id'], box=list(box), delivery='no-local-lines', **decision.to_record()))
            continue
        def outside(w):
            centre = w.frame.rectangle(w.box).mean(0)
            return not (box[0] <= centre[0] <= box[2] and box[1] <= centre[1] <= box[3])
        words = [w for w in words if outside(w)]+local_words
        groups.append(dict(id=region['id'],box=list(box),frame=local_frame.matrix.tolist(),**decision.to_record()))
    for i,w in enumerate(words):
        w.index = i
    return OrientedPage(words,dominant,proposals,groups,result,pieces,orientation_seconds)

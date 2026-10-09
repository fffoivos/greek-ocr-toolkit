"""Local upright fitting with ordered words and parametric page-space guides.

The horizontal fitter is intentionally an unchanged primitive. Each invocation
has an explicit local frame; no vertical curve is misrepresented as page y(x).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
import copy
from typing import Any, Sequence

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
        out.append((a+s+int(xx.min()),t+int(yy.min()),a+s+int(xx.max())+1,t+int(yy.max())+1))
    return out


def _fit_group(image, frame, decision, gid, regions, start, *, segmentation=None, pieces=None):
    local = frame.image(image)
    mapped_regions = []
    for key, box in regions:
        points = frame.rectangle(box,inverse=False)
        mapped_regions.append((key,[*points.min(0),*points.max(0)]))
    if segmentation is None:
        segmentation = segment_page(local)
        segmentation,pieces,_ = prepare_delivery(local,segmentation,mapped_regions)
    words = []; gray = np.asarray(local)
    for piece in pieces:
        if piece.line.discounted is not None:
            continue
        for box in _word_boxes(local,piece,gray):
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
                  recognizer: _Recognizer | None = None, use_osd: bool = True,
                  segmentation: Any = None, pieces: list | None = None,
                  dominant: Orientation | None = None, discover: bool = True) -> OrientedPage:
    """Discover directions, normalize groups, fit, split and inverse-map words.

    Passing a precomputed segmentation reuses only the unchanged upright base;
    local discovery still precedes all newly normalized fits. Unknown polarity
    retains both readings and records the geometry's working hypothesis.
    """
    image = image.convert('L')
    proposals = discover_directions(image) if discover else []
    dominant = dominant or measure_orientation(image,use_osd=use_osd,unit='page')
    working = dominant.orientation_cw
    if working is None:
        working = 90 if dominant.axis == 'vertical' else 0
    frame = QuarterTurn(*image.size,working)
    # Existing part-two records can only be reused in the very same pixel frame.
    if working != 0:
        segmentation = pieces = None
    words,result,pieces = _fit_group(image,frame,dominant,'page',table_regions,0,
                                    segmentation=segmentation,pieces=pieces)
    groups = [dict(id='page',box=[0,0,*image.size],frame=frame.matrix.tolist(),**dominant.to_record())]
    # Same-axis proposals remain eligible for 180-degree disagreement as well
    # as perpendicular writing. A dominant block is a prior, not a veto.
    accepted_boxes = []
    for proposal in proposals:
        if proposal['axis_confidence'] < .6:
            continue
        box = tuple(map(int,(np.floor(proposal['box'][0]),np.floor(proposal['box'][1]),
                             np.ceil(proposal['box'][2]),np.ceil(proposal['box'][3]))))
        if any(max(box[0],b[0])<min(box[2],b[2]) and max(box[1],b[1])<min(box[3],b[3]) for b in accepted_boxes):
            continue
        crop = image.crop(box)
        decision = measure_orientation(crop,use_osd=use_osd,unit='word' if proposal['components'] < 16 else 'line')
        if decision.orientation_cw is None and recognizer is not None:
            decision = recognizer_polarity(crop,decision,recognizer)
        if decision.orientation_cw is None and decision.axis == dominant.axis and dominant.orientation_cw is not None:
            # The line belongs to a coherent, same-axis block. Preserve the
            # unresolved direct readings as evidence when inheriting polarity.
            decision = replace(decision,orientation_cw=dominant.orientation_cw,
                               polarity_confidence=dominant.polarity_confidence,
                               evidence={**decision.evidence,'polarity_source':'block-neighbours','inherited_from':'page'})
        if decision.orientation_cw is None:
            proposal['decision'] = decision.to_record()
            # A secure perpendicular axis still deserves a local horizontal
            # fit. Its polarity remains unknown, including numeric folios.
            if decision.axis == ('vertical' if working%180 else 'horizontal') or proposal['axis_confidence'] < .9:
                continue
        if decision.orientation_cw == working:
            # Attach direct line evidence to contained words without refitting
            # or changing any guide on an already upright region.
            covered = np.zeros((box[3]-box[1],box[2]-box[0]),bool)
            for w in words:
                centre = w.frame.rectangle(w.box).mean(0)
                if box[0] <= centre[0] <= box[2] and box[1] <= centre[1] <= box[3]:
                    w.orientation = replace(decision,evidence={**decision.evidence,'inherited_from':'local-chain'})
                    corners = w.frame.rectangle(w.box);lo = np.floor(corners.min(0)).astype(int);hi = np.ceil(corners.max(0)).astype(int)
                    covered[max(0,lo[1]-box[1]):min(covered.shape[0],hi[1]-box[1]),
                            max(0,lo[0]-box[0]):min(covered.shape[1],hi[0]-box[0])] = True
            import cv2
            _, ink = cv2.threshold(np.asarray(crop),0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
            if np.count_nonzero((ink>0)&covered)/max(1,np.count_nonzero(ink)) >= .8:
                continue
        local_angle = decision.orientation_cw
        if local_angle is None:
            local_angle = 90 if decision.axis == 'vertical' else 0
        # The page fitter's body filter needs page-like context. Give an isolated
        # chain five body heights of paper on each side, without moving ink in
        # the returned source frame. Photometry is normalized only in this crop.
        g = np.asarray(crop,dtype=float);paper=float(np.percentile(g,90));dark=float(np.percentile(g,2))
        crop = Image.fromarray(np.clip((g-dark)/max(1.,paper-dark)*255,0,255).astype('uint8'))
        pad = max(1,round(5*proposal['xheight']))
        crop = ImageOps.expand(crop,border=pad,fill=255)
        local_frame = QuarterTurn(crop.width,crop.height,local_angle,(box[0]-pad,box[1]-pad))
        # _fit_group rotates a crop but the inverse maps via its page offset.
        local_words,_,_ = _fit_group(crop,local_frame,decision,f'local-{len(groups)}',[],0)
        if not local_words:
            continue
        def outside(w):
            centre = w.frame.rectangle(w.box).mean(0)
            return not (box[0] <= centre[0] <= box[2] and box[1] <= centre[1] <= box[3])
        words = [w for w in words if outside(w)]+local_words
        groups.append(dict(id=f'local-{len(groups)}',box=list(box),frame=local_frame.matrix.tolist(),**decision.to_record()))
        accepted_boxes.append(box)
    for i,w in enumerate(words):
        w.index = i
    return OrientedPage(words,dominant,proposals,groups,result,pieces)

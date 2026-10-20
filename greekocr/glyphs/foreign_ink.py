"""Opt-in native foreign-ink masking using recut's existing ownership rule.

No fitting, segmentation, expansion, raster resampling, or input mutation.
Curves must come from the same detector at training and deployment. Ownership
is inferred; caller qualification remains necessary, especially detached marks.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from typing import Any, Mapping, Sequence

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from .components import EIGHT, binarise, to_gray
from .lines_api import straighten
from .recut import LineFit, WINDOW, _neighbour, _voronoi_keep

__all__ = ['MaskPage', 'MaskedCrop', 'prepare_mask_page', 'mask_foreign_ink', 'mask_detected_line']

PARAMETERS = dict(version='foreign-ink-voronoi-1', ownership='_voronoi_keep unchanged',
    context_xh=WINDOW, grid='reversible nearest-integer centre translation',
    neighbours='_neighbour unchanged; absent side infinite', ring_inner_px=1,
    ring_outer_px=3, ring_ink_exclusion='all binarise foreground',
    fill='per-channel page-ring median; round to native uint8',
    spread='per-channel ring p90-p10', ownership_tolerances=None)


@dataclass
class MaskPage:
    image: Image.Image
    pixels: np.ndarray
    ink: np.ndarray
    labels: np.ndarray
    objects: list
    fills: dict = field(default_factory=dict, repr=False)


@dataclass
class MaskedCrop:
    image: Image.Image
    mask: np.ndarray
    record: dict


def prepare_mask_page(page: Image.Image | np.ndarray) -> MaskPage:
    """Share page observations between calls; exactly the same as raw-page use."""
    image = page.copy() if isinstance(page, Image.Image) else Image.fromarray(np.asarray(page))
    if image.mode not in ('L', 'RGB', 'RGBA'):
        raise ValueError('native uint8 L, RGB or RGBA page required')
    pixels = np.asarray(image)
    ink = binarise(to_gray(image))
    labels, _ = ndi.label(ink, structure=EIGHT)
    return MaskPage(image, pixels, ink, labels, ndi.find_objects(labels))


def _centre_fit(line: Any) -> LineFit:
    if isinstance(line, Mapping):
        x0, x1, xh = line['x0'], line['x1'], line['xheight']
        base, mean = np.asarray(line['baseline']), np.asarray(line['meanline'])
    else:
        x0, x1, xh = line.x0, line.x1, line.xheight
        base, mean = np.asarray(line.baseline), np.asarray(line.meanline)
    if (not isinstance(x0, (int, np.integer)) or not isinstance(x1, (int, np.integer))
            or x1 <= x0 or base.shape != (x1-x0,) or mean.shape != base.shape
            or not np.isfinite(base).all() or not np.isfinite(mean).all()
            or not np.isfinite(xh) or xh <= 0 or np.any(base <= mean)):
        raise ValueError('finite positive own body curves required')
    rise = float(np.median(base-mean))
    # Existing LineFit sampler; its base carries the body centre in this adapter.
    return LineFit(int(x0), int(x1), (base+mean)/2, float(xh), rise, rise, 0, (x0,0,x1,1))


def _foreign_mask(ink: np.ndarray, line: LineFit, neighbours: list[LineFit], box: tuple) -> np.ndarray:
    x0, y0, x1, y1 = box
    a, b = max(0,min(x0,line.x0)), min(ink.shape[1],max(x1,line.x1))
    xs = np.arange(a,b,dtype=float)
    centre = line.base_at(xs)
    rounded = np.rint(centre)
    # Observe the original rectangle and the existing recut working context.
    radius = max(1,int(np.ceil(WINDOW*line.xh)),int(np.ceil(np.max(rounded-y0))),
                 int(np.ceil(np.max(y1-rounded))))
    straight, miss, br = straighten(ink[:,a:b].astype(float),rounded,1,paper=0,
                                    above=radius,below=radius+1)
    curves = []
    for side in (-1,1):
        nb = _neighbour(neighbours,xs,centre,line.xh,side)
        curves.append(np.full(len(xs),side*np.inf) if nb is None
                      else br+centre+nb[1]-rounded)
    keep = _voronoi_keep(straight.astype(bool)&~miss,miss,float(br),curves[0],curves[1],line.rise)
    cols = np.arange(x0,x1)-a
    rows = np.arange(y0,y1)[:,None]-rounded[cols].astype(int)[None,:]+br
    return ink[y0:y1,x0:x1]&~keep[rows,cols[None,:]]


def _ring(page: MaskPage, label: int) -> dict:
    if label in page.fills:
        return page.fills[label]
    sy, sx = page.objects[label-1]
    y0,y1 = max(0,sy.start-3), min(page.ink.shape[0],sy.stop+3)
    x0,x1 = max(0,sx.start-3), min(page.ink.shape[1],sx.stop+3)
    component = page.labels[y0:y1,x0:x1] == label
    ring = (ndi.binary_dilation(component,structure=EIGHT,iterations=3)
            & ~ndi.binary_dilation(component,structure=EIGHT,iterations=1)
            & ~page.ink[y0:y1,x0:x1])
    values = page.pixels[y0:y1,x0:x1][ring]
    if values.size:
        median = np.median(values,axis=0)
        spread = np.percentile(values,90,axis=0)-np.percentile(values,10,axis=0)
        result = dict(ring_pixels=int(ring.sum()),ring_median=np.asarray(median).tolist(),
                      ring_spread=np.asarray(spread).tolist(),
                      fill=np.clip(np.rint(median),0,255).astype(np.uint8).tolist())
    else:
        result = dict(ring_pixels=0,ring_median=None,ring_spread=None,fill=None)
    page.fills[label] = result
    return result


def mask_foreign_ink(page: MaskPage | Image.Image | np.ndarray, line: Any,
                     neighbours: Sequence[Any], crop_box: Sequence[int]) -> MaskedCrop:
    """Paint only foreign foreground pixels inside the unchanged native rectangle.

    `line` and `neighbours` are runtime LineSegments or exact baseline/meanline
    records in page coordinates. Including `line` in neighbours is harmless.
    Empty background rings abstain per component; no flat-white fallback.
    """
    prepared = page if isinstance(page,MaskPage) else prepare_mask_page(page)
    if len(crop_box)!=4 or any(not isinstance(v,(int,np.integer)) for v in crop_box):
        raise ValueError('integer native crop rectangle required')
    box = tuple(map(int,crop_box)); x0,y0,x1,y1 = box
    if not (0<=x0<x1<=prepared.image.width and 0<=y0<y1<=prepared.image.height):
        raise ValueError('crop must lie inside page')
    own = _centre_fit(line)
    others = [_centre_fit(n) for n in neighbours if n is not line]
    mask = _foreign_mask(prepared.ink,own,others,box)
    labels = prepared.labels[y0:y1,x0:x1]
    pixels = prepared.pixels[y0:y1,x0:x1].copy()
    fills = []
    proposed = int(mask.sum())
    for label in np.unique(labels[mask]):
        selected = mask & (labels==label)
        statistic = _ring(prepared,int(label))
        fills.append(dict(component_id=int(label),masked_pixels=int(selected.sum()),**statistic))
        if statistic['fill'] is None:
            mask[selected] = False
        else:
            pixels[selected] = statistic['fill']
    applied = [r for r in fills if r['fill'] is not None]
    record = dict(crop_box=list(box),masked_pixel_count=int(mask.sum()),
        proposed_masked_pixel_count=proposed,masked_component_count=len(applied),
        ring_median=np.median([r['ring_median'] for r in applied],axis=0).tolist() if applied else None,
        ring_spread=np.median([r['ring_spread'] for r in applied],axis=0).tolist() if applied else None,
        crop_ring_summary='unweighted median across component ring statistics',
        fills=fills,empty_ring_abstentions=len(fills)-len(applied),
        mask_sha256=hashlib.sha256(mask.tobytes()).hexdigest(),
        changed=bool(np.any(pixels!=prepared.pixels[y0:y1,x0:x1])),
        native_changed_pixels=int(np.any(pixels!=prepared.pixels[y0:y1,x0:x1],axis=2).sum())
            if pixels.ndim==3 else int((pixels!=prepared.pixels[y0:y1,x0:x1]).sum()))
    return MaskedCrop(Image.fromarray(pixels),mask,record)


def mask_detected_line(page: MaskPage | Image.Image | np.ndarray, line: Any,
                       neighbours: Sequence[Any], crop_box: Sequence[int] | None=None) -> MaskedCrop:
    """Inference adapter at the native TextPiece boundary; no detector rerun.

    In GlossapiOcrModel._detect pass piece.line, analysis.segmentation.lines,
    piece.box. For default detector envelopes the exact existing line_piece
    supplies the box. The same function handles original training rectangles.
    """
    if crop_box is None:
        from greekocr.pages.tables import line_piece
        size = page.image.size if isinstance(page,MaskPage) else (page.size if isinstance(page,Image.Image)
                                                                else np.asarray(page).shape[1::-1])
        crop_box = line_piece(line,0,size).box
    return mask_foreign_ink(page,line,neighbours,crop_box)

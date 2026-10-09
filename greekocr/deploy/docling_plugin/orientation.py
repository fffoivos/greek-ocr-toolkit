"""Docling 2.135 frame adapters: before layout and at TableFormer V1.

Use OrientationPdfPipeline as the converter's pipeline_cls. Installing only the
OCR entry point cannot correct the pixels already consumed by layout.
"""
from __future__ import annotations

import copy
from collections import Counter
from types import SimpleNamespace
from time import perf_counter

import numpy as np
from docling.datamodel.base_models import LayoutPrediction, TableStructurePrediction
from docling.models.base_ocr_model import _empty_segmented_page
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling_core.types.doc import BoundingBox, CoordOrigin, DocItemLabel, Size
from docling_core.types.doc.page import BoundingRectangle
from docling_core.types.doc.items.table.table_data import Orientation as TableOrientation

from greekocr.glyphs.orientation import QuarterTurn, discover_directions, measure_orientation

__all__ = ['NormalizedPageBackend', 'PageOrientationAdapter', 'OrientedTableAdapter', 'OrientationPdfPipeline']


def _rect(points):
    return BoundingRectangle(**{f'r_{axis}{i}':float(p[j]) for i,p in enumerate(points)
                                for j,axis in enumerate(('x','y'))},coord_origin=CoordOrigin.TOPLEFT)


def _box(box, frame, *, inverse=False):
    p = frame.rectangle((box.l,box.t,box.r,box.b),inverse=inverse)
    l,t = p.min(0); r,b = p.max(0)
    return BoundingBox(l=l,t=t,r=r,b=b,coord_origin=CoordOrigin.TOPLEFT)


class NormalizedPageBackend:
    """Wrap an already metadata-rotated backend with one coherent current frame."""
    def __init__(self, backend, orientation_cw):
        self.source = backend
        source_size = backend.get_size()
        self.frame = QuarterTurn(source_size.width,source_size.height,orientation_cw)
        self.size = Size(width=self.frame.size[0],height=self.frame.size[1])
        self._parsed = None

    def __getattr__(self, name):
        return getattr(self.source,name)

    def get_size(self):
        return self.size

    def get_page_image(self, scale=1., cropbox=None):
        image = self.frame.image(self.source.get_page_image(scale=scale))
        if cropbox is not None:
            box = cropbox.to_top_left_origin(page_height=self.size.height)
            # Actual ratios handle renderer dimension rounding independently.
            sx,sy = image.width/self.size.width,image.height/self.size.height
            image = image.crop((box.l*sx,box.t*sy,box.r*sx,box.b*sy))
        return image

    def get_segmented_page(self):
        if self._parsed is None:
            self._parsed = _empty_segmented_page(SimpleNamespace(size=self.size))
            source = self.source.get_segmented_page()
            if source is not None:
                for attr in ('textline_cells','word_cells','char_cells'):
                    cells = copy.deepcopy(getattr(source,attr))
                    for c in cells:
                        rect = c.rect.to_top_left_origin(self.frame.height) if c.rect.coord_origin != CoordOrigin.TOPLEFT else c.rect
                        c.rect = _rect(self.frame.points(rect.to_polygon()))
                    setattr(self._parsed,attr,cells)
                for attr in ('has_lines','has_words','has_chars'):
                    setattr(self._parsed,attr,getattr(source,attr))
        return self._parsed

    def get_bitmap_rects(self, scale=1.):
        return [_box(b.to_top_left_origin(page_height=self.frame.height),self.frame).scaled(scale)
                for b in self.source.get_bitmap_rects(scale=1.)]

    def get_text_in_rect(self, bbox):
        return self.source.get_text_in_rect(_box(bbox.to_top_left_origin(page_height=self.size.height),self.frame,inverse=True))

    def get_shape_lines(self):
        # This adapter requires pixel detector OCR. Shape-derived reading-order
        # separators cannot safely retain the source backend's coordinate frame.
        return []

    def get_connected_shape_bounding_boxes(self):
        return []


class PageOrientationAdapter:
    """Normalize eligible uniform raster pages BEFORE preprocessing and layout."""
    def __init__(self, preprocessing, *, decide=None, eligible=None):
        self.preprocessing = preprocessing
        self.decide = decide or (lambda im:measure_orientation(im,use_osd=False,unit='page'))
        self.eligible = eligible or (lambda conv,page:True)
        self.records = []

    def __call__(self, conv_res, page_batch):
        for page in page_batch:
            backend = page._backend
            if backend is None or not backend.is_valid() or not self.eligible(conv_res,page):
                yield from self.preprocessing(conv_res,[page]); continue
            if isinstance(backend,NormalizedPageBackend):
                yield from self.preprocessing(conv_res,[page]); continue
            image = backend.get_page_image(scale=2.)
            orientation_started = perf_counter()
            decision = self.decide(image)
            proposals = discover_directions(image)
            from greekocr.glyphs.orientation_regions import page_regions
            _, regions, _ = page_regions(image, proposals=proposals, dominant=decision)
            blocks = [{k:v for k,v in r.items() if k != 'decision'} | r['decision'].to_record() for r in regions[1:]]
            # A cross-line neighbour vote is not a minority region. Also retain
            # a real opposite reading on the same axis (e.g. an inverted label).
            mixed = any(p['axis'] != decision.axis or p['orientation_cw'] not in (None, decision.orientation_cw)
                        for p in blocks)
            # Incomplete proposals supplied by an external adapter cannot
            # certify uniformity; retain the conservative adapter contract.
            if any('box' not in p for p in proposals):
                mixed = any(p['axis'] != decision.axis for p in proposals)
            angle = decision.orientation_cw
            applied = angle in (90,180,270) and not mixed
            if applied:
                page._backend = NormalizedPageBackend(backend,angle)
                page.size = page._backend.get_size()
                page._image_cache = {}
                page.parsed_page = None
            frame = QuarterTurn(backend.get_size().width,backend.get_size().height,angle if applied else 0)
            self.records.append(dict(page_no=page.page_no,applied=applied,mixed=mixed,regions=blocks,
                                     orientation_seconds=perf_counter()-orientation_started,
                                     source_to_page=frame.matrix.tolist(),**decision.to_record()))
            yield from self.preprocessing(conv_res,[page])


class OrientedTableAdapter:
    """Run V1 with matching upright pixels/tokens; map cells back, retain indices."""
    def __init__(self, model):
        if not hasattr(model,'predict_tables'):
            raise TypeError('orientation adapter requires TableFormer V1 predict_tables')
        self.model = model
        self.records = []

    def __getattr__(self, name):
        return getattr(self.model,name)

    def predict_tables(self, conv_res, pages):
        predictions = []
        for page in pages:
            output = TableStructurePrediction()
            clusters = getattr(page.predictions.layout,'clusters',[])
            for cluster in clusters:
                if cluster.label not in (DocItemLabel.TABLE,DocItemLabel.DOCUMENT_INDEX):
                    continue
                votes = Counter()
                known = getattr(page._backend,'_greekocr_word_orientations',None) if getattr(page,'_backend',None) is not None else None
                for c in cluster.cells:
                    if known is not None and known.get(c.index) is None:
                        continue
                    cw = (-c.rect.angle_360)%360
                    if cw in (0,90,180,270):
                        votes[cw] += max(1,len(c.text.strip()))
                angle, support = votes.most_common(1)[0] if votes else (0,0)
                if support/max(1,sum(votes.values())) < .75:
                    angle = 0
                frame = QuarterTurn(page.size.width,page.size.height,angle)
                size = Size(width=frame.size[0],height=frame.size[1])
                local = copy.deepcopy(cluster)
                local.bbox = _box(cluster.bbox.to_top_left_origin(page_height=page.size.height),frame)
                for c in local.cells:
                    rect = c.rect.to_top_left_origin(page.size.height) if c.rect.coord_origin != CoordOrigin.TOPLEFT else c.rect
                    c.rect = _rect(frame.points(rect.to_polygon()))
                # Backend words are intentionally empty: our OCR cluster cells
                # own the table, regardless of stale native backend text.
                parsed = _empty_segmented_page(SimpleNamespace(size=size))
                view = SimpleNamespace(page_no=page.page_no,size=size,
                    _backend=SimpleNamespace(is_valid=lambda:True,get_segmented_page=lambda:parsed,
                                             get_text_in_rect=lambda box:''),
                    predictions=SimpleNamespace(layout=LayoutPrediction(clusters=[local]),tablestructure=None),
                    get_image=lambda scale,frame=frame,page=page:frame.image(page.get_image(scale=scale)))
                pred = self.model.predict_tables(conv_res,[view])[0]
                if cluster.id not in pred.table_map:
                    continue
                table = pred.table_map[cluster.id]
                for cell in table.table_cells:
                    if cell.bbox is not None:
                        cell.bbox = _box(cell.bbox.to_top_left_origin(page_height=size.height),frame,inverse=True)
                table.cluster = cluster
                table.orientation = TableOrientation(f'rot_{(-angle)%360}')
                output.table_map[cluster.id] = table
                self.records.append(dict(page_no=page.page_no,table_id=cluster.id,orientation_cw=angle,
                                         votes=dict(votes),source_to_local=frame.matrix.tolist(),
                                         rows=table.num_rows,columns=table.num_cols))
            page.predictions.tablestructure = output
            predictions.append(output)
        return predictions

    def __call__(self, conv_res, page_batch):
        pages = list(page_batch)
        if not self.model.enabled:
            yield from pages; return
        self.predict_tables(conv_res,pages)
        yield from pages


class OrientationPdfPipeline(StandardPdfPipeline):
    """Standard pipeline with normalization before layout and a rotated V1 stage."""
    def __init__(self, pipeline_options):
        super().__init__(pipeline_options)
        from .options import GlossapiOcrOptions
        opts = pipeline_options.ocr_options
        if not isinstance(opts,GlossapiOcrOptions) or opts.recognition_mode != 'oriented':
            raise ValueError('OrientationPdfPipeline requires Glossapi oriented OCR')
        def eligible(conv,page):
            return opts.replace_policy == 'all' or page.page_no in self.ocr_model.routes.get(conv.input.file.name,set())
        self.preprocessing_model = PageOrientationAdapter(self.preprocessing_model,eligible=eligible)
        self.table_model = OrientedTableAdapter(self.table_model)

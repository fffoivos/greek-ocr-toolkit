"""Replace routed text after image layout and before layout cell assignment."""
from __future__ import annotations

import json
import logging
import math
from collections import Counter
from pathlib import Path
from time import perf_counter

import numpy as np
from docling.models.base_ocr_model import BaseOcrModel
from docling_core.types.doc import BoundingBox, CoordOrigin
from docling_core.types.doc.page import BoundingRectangle, TextCell

from .options import GlossapiOcrOptions
from .recognizer.ckpt_io import sha256_file
from .recognizer.strips import extract_strip

_log = logging.getLogger(__name__)

# Frozen sidecar scans have 0..49 chars (numbers/captions); the shortest
# garbage-text page has 66. This coverage heuristic is not a body detector.
RASTER_BODY_CHAR_LIMIT = 50
RASTER_BODY_IMAGE_RATIO = 0.5


class GlossapiOcrModel(BaseOcrModel):
    def __init__(self, *, enabled, artifacts_path, options, accelerator_options):
        super().__init__(enabled=enabled, artifacts_path=artifacts_path,
                         options=options, accelerator_options=accelerator_options)
        self.routes: dict[str, set[int]] = {}
        self.route_metrics: dict[str, dict[int, dict]] = {}
        self.unsupported_counts: Counter = Counter()
        self.call_log: list[dict] = []
        self.recognizer = None
        self.segmenter = None
        if not enabled:
            return
        if options.routing_sidecar is not None:
            for line in options.routing_sidecar.read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                filename = row.get("filename") or Path(row["path"]).name
                # Sidecars may reference repaired_pdfs; the stable filename binds
                # them to original inputs. Conflicting duplicate filenames fail closed.
                pages = {int(p["page"]) for p in row["pages"]
                         if p["page_needs_ocr"] is True}
                metrics = {int(p["page"]): p for p in row["pages"]}
                if filename in self.routes and (self.routes[filename] != pages or
                                               self.route_metrics[filename] != metrics):
                    raise ValueError(f"conflicting routing rows for {filename}")
                self.routes[filename] = pages
                self.route_metrics[filename] = metrics

    @classmethod
    def get_options_type(cls):
        return GlossapiOcrOptions

    def _get_recognizer(self):
        if self.recognizer is None:
            from .recognizer.inference import Recognizer

            opts = self.options
            import os
            import torch
            if torch.device(opts.device).type == 'mps':
                if not torch.backends.mps.is_available():
                    raise RuntimeError('MPS recognizer required but unavailable; CPU fallback forbidden')
                if os.environ.get('PYTORCH_ENABLE_MPS_FALLBACK') == '1':
                    raise RuntimeError('MPS CPU fallback must be disabled')
            checkpoint = opts.release_dir or opts.checkpoint
            if checkpoint is None:
                from .assets import fetch_model
                checkpoint, self.model_acquisition = fetch_model(
                    repo_id=opts.model_repo, variant=opts.model_variant,
                    revision=opts.model_revision, manifest_sha256=opts.model_manifest_sha256)
            if opts.config_sha256 is not None:
                if sha256_file(str(checkpoint/'config.json')) != opts.config_sha256:
                    raise ValueError('OCR config sha256 mismatch')
            pinned_weights = checkpoint/'model.safetensors' if checkpoint.is_dir() else checkpoint
            if opts.checkpoint_sha256 is not None:
                if sha256_file(str(pinned_weights)) != opts.checkpoint_sha256:
                    raise ValueError("OCR checkpoint sha256 mismatch")
                # A .pt pin must not silently resolve to different sibling weights.
                if checkpoint.suffix == ".pt" and checkpoint.with_suffix(".safetensors").exists():
                    raise ValueError("pinned .pt has a safetensors sibling; pin that artifact explicitly")
            self.recognizer = Recognizer(str(checkpoint), str(opts.codec) if opts.codec else None, opts.device)
            if any(p.device.type != torch.device(opts.device).type for p in self.recognizer.model.parameters()):
                raise RuntimeError('recognizer parameters are not on the requested device')
        return self.recognizer

    def _record(self, record):
        self.call_log.append(record)
        if record["status"] == "unsupported":
            self.unsupported_counts[record["reason"]] += 1
            _log.warning("OCR unsupported: %s page %s: %s",
                         record["filename"], record["page"], record["reason"])
        if self.options.call_log is not None:
            self.options.call_log.parent.mkdir(parents=True, exist_ok=True)
            with self.options.call_log.open("a", encoding="utf-8") as fp:
                fp.write(json.dumps(record, ensure_ascii=False) + "\n")

    @staticmethod
    def _install(cells, page):
        # Equivalent to BaseOcrModel.post_process_cells under full replacement,
        # restricted to THIS page; never mutate the pipeline's global OCR option.
        targets = [page.parsed_page]
        backend = getattr(page, '_backend', None)
        if backend is not None:
            cached = backend.get_segmented_page()
            if cached is not None and cached is not targets[0]:
                targets.append(cached)
        for parsed in targets:
            parsed.textline_cells = cells
            parsed.has_lines = bool(cells)
            # V1 selects ALL backend words over our lines if even one remains.
            # Prior OCR words are just as stale as native PDF words.
            parsed.word_cells = []
            parsed.char_cells = []
            parsed.has_words = parsed.has_chars = False

    def _detect(self, page, record):
        from greekocr.pages import process_page
        from greekocr.pages.lines import extract_line_image
        from greekocr.pages.layout import docling_regions

        parsed = page.parsed_page
        if parsed is None:
            record['reason'] = 'no_parsed_page'
            return
        source = list(parsed.textline_cells)
        record['source_line_count'] = len(source)
        scale = self.options.crop_scale
        start = perf_counter()
        image = page.get_image(scale=scale)
        record['timings_s']['render'] = perf_counter() - start
        if image is None:
            record['reason'] = 'no_page_image'
            return
        # Renderers may round dimensions or return a raster at another scale.
        # Use measured ratios, not the requested scale or a strip coordinate.
        sx = image.width / getattr(page.size, 'width', image.width / scale)
        sy = image.height / page.size.height
        layout = getattr(getattr(page, 'predictions', None), 'layout', None)
        size = (image.width/sx, image.height/sy)
        options = self.options.page_options()
        regions = docling_regions(layout, image.size, size) if options.tables else None
        start = perf_counter()
        try:
            analysis = process_page(image, options=options, table_regions=regions, page_size=size,
                                    page_key=f"{Path(record.get('filename', 'page')).stem}-p{record.get('page', 1):05d}")
        except ValueError as error:
            if str(error) != 'invalid_line_geometry':
                raise
            record['reason'] = 'invalid_line_geometry'
            return
        record['timings_s']['detect'] = perf_counter() - start
        pieces = analysis.pieces
        if options.join_lines:
            from greekocr.pages.delivery import joined_text_pieces
            pieces = joined_text_pieces(analysis)
        if analysis.statistics is not None:
            record['statistics'] = analysis.statistics['stats']
        if analysis.files:
            record['page_files'] = analysis.files
        strips, rects = [], []
        start = perf_counter()
        for piece in pieces:
            line = piece.line
            crop = np.asarray(extract_line_image(image, line), dtype=np.float32) / 255.
            # A one-digit table cell is valid text. The recognizer's minimum
            # width is a tensor contract, not a reason to drop narrow glyphs.
            minimum = math.ceil(crop.shape[0] / 6)
            if crop.shape[1] < minimum:
                pad = minimum - crop.shape[1]
                crop = np.pad(crop, ((0, 0), (pad//2, pad-pad//2)), constant_values=1.)
            strip = extract_strip(crop, (0, 0, crop.shape[1], crop.shape[0]))
            if strip is None:
                record['reason'] = 'invalid_line_crop'
                return
            strips.append(strip)
            # Docling's cell is a rectangle; retain the curve in the detector
            # output, and give layout a tight envelope of its visible font band.
            l, t, r, b = piece.box
            rects.append(BoundingRectangle.from_bounding_box(BoundingBox(
                l=l / sx, t=t / sy, r=r / sx, b=b / sy,
                coord_origin=CoordOrigin.TOPLEFT)))
        record['timings_s']['crop'] = perf_counter() - start
        predictions = []
        if strips:
            start = perf_counter()
            recognizer = self._get_recognizer()
            record['timings_s']['recognizer_setup'] = perf_counter() - start
            start = perf_counter()
            predictions = recognizer.recognize(strips)
            record['timings_s']['recognise'] = perf_counter() - start
            if len(predictions) != len(pieces):
                raise ValueError('recognizer returned a different number of lines')
        ours = [TextCell(index=i, from_ocr=True, rect=rect, text=text, orig=text, confidence=confidence)
                for i, (rect, (text, confidence)) in enumerate(zip(rects, predictions))]
        self._install(ours, page)
        record.update(status='replaced', installed=True, output_line_count=len(ours),
                      recognition_performed=bool(strips),
                      lines=[dict(rect=c.rect.model_dump(mode='json'), text=c.text, confidence=c.confidence,
                                  line_index=p.line_index, table_id=p.table_id, cell_id=p.cell_id,
                                  geometry_source=p.line.geometry_source) for c, p in zip(ours, pieces)])

    def _detect_oriented(self, page, record):
        from greekocr.pages import process_page
        from greekocr.pages.layout import docling_regions
        from greekocr.glyphs.orientation import _recognition_strip
        from docling_core.types.doc.page import TextDirection

        if page.parsed_page is None:
            record['reason'] = 'no_parsed_page'
            return
        start = perf_counter()
        image = page.get_image(scale=self.options.crop_scale)
        if image is None:
            record['reason'] = 'no_page_image'
            return
        sx, sy = image.width/page.size.width, image.height/page.size.height
        layout = getattr(page.predictions,'layout',None)
        options = self.options.page_options()
        regions = docling_regions(layout, image.size, (page.size.width, page.size.height), oriented=True) if options.tables else None
        recognizer = self._get_recognizer()
        analysis = process_page(image, options=options, table_regions=regions,
                                page_size=(page.size.width, page.size.height), recognizer=recognizer,
                                page_key=f"{Path(record.get('filename', 'page')).stem}-p{record.get('page', 1):05d}")
        result = analysis.orientation
        if analysis.statistics is not None:
            record['statistics'] = analysis.statistics['stats']
        strips = []
        for w in result.words:
            strip = _recognition_strip(w.crop)
            if strip is None:
                raise ValueError('invalid oriented word crop')
            strips.append(strip)
        predictions = recognizer.recognize(strips) if strips else []
        if len(predictions) != len(result.words):
            raise ValueError('recognizer returned a different number of words')
        ours, records = [], []
        for w,(text,confidence) in zip(result.words,predictions):
            w.text,w.recognition_confidence = text,confidence
            r = w.to_record(image.size,(page.size.width,page.size.height))
            rect = BoundingRectangle(**{f'r_{axis}{i}':p[j] for i,p in enumerate(r['corners_page'])
                                        for j,axis in enumerate(('x','y'))},coord_origin=CoordOrigin.TOPLEFT)
            ours.append(TextCell(index=w.index,from_ocr=True,rect=rect,text=text,orig=text,
                                 confidence=confidence,text_direction=TextDirection.LEFT_TO_RIGHT))
            records.append(r)
        if options.outputs.directory is not None and 'orientation' in options.outputs.files:
            from greekocr.pages.options import OutputOptions
            from greekocr.pages.outputs import write_page
            analysis.files.update(write_page(analysis, image, OutputOptions(options.outputs.directory, frozenset({'orientation'}))))
        if analysis.files:
            record['page_files'] = analysis.files
        self._install(ours,page)
        if getattr(page,'_backend',None) is not None:
            page._backend._greekocr_word_orientations = {w.index:w.orientation.orientation_cw for w in result.words}
        record.update(status='replaced',installed=True,output_line_count=len(ours),
                      output_word_count=len(ours),recognition_performed=bool(strips),
                      dominant_orientation=result.dominant.to_record(),groups=result.groups,
                      proposals=result.proposals,words=records,
                      frame=dict(image_size=list(image.size),page_size=[page.size.width,page.size.height],
                                 image_to_page=[[1/sx,0,0],[0,1/sy,0],[0,0,1]],
                                 source_to_page=getattr(getattr(page._backend,'frame',None),'matrix',np.eye(3)).tolist()
                                 if getattr(page,'_backend',None) is not None else np.eye(3).tolist()))
        record['timings_s']['orientation'] = result.orientation_seconds
        record['timings_s']['oriented_detect_and_recognize'] = perf_counter()-start

    def _filter_legacy(self, page, record):
        """Post-filter the installed legacy cells without changing their route."""
        rules = self.options.segmenter_rules
        if not any(rules.get(key, False) for key in ('spirals', 'spiral_holes', 'ornaments')):
            return
        if not record.get('installed'):
            return
        from greekocr.segmenters import Line
        from greekocr.segmenters.filters import (drop_binding_and_ornaments,
                                                 drop_templates_after_recognition)
        start = perf_counter()
        image = page.get_image(scale=self.options.crop_scale).convert('RGB')
        sx, sy = image.width/page.size.width, image.height/page.size.height
        cells = list(page.parsed_page.textline_cells)
        lines = []
        for i, cell in enumerate(cells):
            polygon = [[getattr(cell.rect, f'r_x{j}')*sx,
                        (page.size.height-getattr(cell.rect, f'r_y{j}')
                         if cell.rect.coord_origin == CoordOrigin.BOTTOMLEFT else
                         getattr(cell.rect, f'r_y{j}'))*sy] for j in range(4)]
            points = np.asarray(polygon)
            lines.append(Line(str(i), polygon, (*points.min(0), *points.max(0)),
                              None, 'kept', None))
        drop_binding_and_ornaments(lines, np.asarray(image), spirals=rules.get('spirals', False),
                                   spiral_holes=False, ornaments=False)
        drop_templates_after_recognition(lines, np.asarray(image), [c.text for c in cells],
            spiral_holes=rules.get('spiral_holes', False), ornaments=rules.get('ornaments', False),
            hole_seeds=self.options.hole_seeds, ornament_seeds=self.options.ornament_seeds)
        kept = [i for i, line in enumerate(lines) if line.status == 'kept']
        self._install([cells[i] for i in kept], page)
        for key in ('lines', 'words'):
            if key in record:
                record[key] = [record[key][i] for i in kept]
        record['output_line_count'] = len(kept)
        if 'output_word_count' in record:
            record['output_word_count'] = len(kept)
            backend = getattr(page, '_backend', None)
            if backend is not None and hasattr(backend, '_greekocr_word_orientations'):
                indices = {cells[i].index for i in kept}
                backend._greekocr_word_orientations = {
                    k: v for k, v in backend._greekocr_word_orientations.items() if k in indices}
        record['filter_rows'] = [dict(id=line.id, polygon=line.polygon, bbox=list(line.bbox),
                                     recognised_text=cell.text, status=line.status,
                                     reason=line.reason, **line.extras) for line, cell in zip(lines, cells)]
        record['timings_s']['filter'] = perf_counter()-start

    def __call__(self, conv_res, page_batch):
        if not self.enabled:
            yield from page_batch
            return
        filename = conv_res.input.file.name
        for page in page_batch:
            replace = (self.options.replace_policy == "all" or
                       page.page_no in self.routes.get(filename, set()))
            if not replace:
                yield page
                continue
            record = {"filename": filename, "page": page.page_no,
                      # Docling 2.81 uses force_full_page_ocr; newer releases
                      # expose mode. Logging must support both option schemas.
                      "mode": getattr(self.options, "mode", None),
                      "force_full_page_ocr": getattr(self.options, "force_full_page_ocr", None),
                      "recognition_mode": self.options.recognition_mode,
                      "crop_scale": self.options.crop_scale,
                      "status": "unsupported", "timings_s": {}}
            if self.options.segmenter != 'pixel_slow':
                from .segmenter import detect_segmenter
                detect_segmenter(self, page, record)
                self._record(record)
                yield page
                continue
            if self.options.recognition_mode in ("detector", "oriented"):
                if self.options.recognition_mode == 'oriented':
                    self._detect_oriented(page, record)
                else:
                    self._detect(page, record)
                self._filter_legacy(page, record)
                self._record(record)
                yield page
                continue
            parsed = page.parsed_page
            if parsed is None or not parsed.textline_cells:
                record.update(reason="no_textlayer_lines", source_line_count=0)
                self._record(record)
                yield page
                continue
            assert parsed.has_lines, "textline cells present but has_lines=False"
            source = list(parsed.textline_cells)
            record["source_line_count"] = len(source)
            metrics = self.route_metrics.get(filename, {}).get(page.page_no, {})
            # Prefer the routing sidecar's original text-layer measurement. Older
            # minimal routing files retain native-line behavior without scan evidence.
            chars = metrics.get("chars", sum(len(c.text.strip()) for c in source))
            raster_body = (chars < RASTER_BODY_CHAR_LIMIT and
                           (metrics.get("decision") == "scanned_page" or
                            (metrics.get("image_area_ratio") or 0) >= RASTER_BODY_IMAGE_RATIO))
            record["body_support"] = dict(
                textlayer_chars=chars, chars_source="sidecar" if "chars" in metrics else "native_lines",
                decision=metrics.get("decision"), image_area_ratio=metrics.get("image_area_ratio"),
                char_limit=RASTER_BODY_CHAR_LIMIT, image_ratio_threshold=RASTER_BODY_IMAGE_RATIO)
            start = perf_counter()
            recognizer = self._get_recognizer()
            record["timings_s"]["recognizer_setup"] = perf_counter() - start
            start = perf_counter()
            image = page.get_image(scale=self.options.crop_scale)
            record["timings_s"]["render"] = perf_counter() - start
            if image is None:
                record["reason"] = "no_page_image"
                self._record(record)
                yield page
                continue
            start = perf_counter()
            gray = np.asarray(image.convert("L"), dtype=np.float32) / 255.0
            strips = []
            for cell in source:
                bb = cell.rect.to_bounding_box().to_top_left_origin(page_height=page.size.height)
                l, t, r, b = bb.scaled(self.options.crop_scale).as_tuple()
                strip = extract_strip(gray, (math.floor(l), math.floor(t), math.ceil(r), math.ceil(b)))
                if strip is None:
                    break
                strips.append(strip)
            record["timings_s"]["crop"] = perf_counter() - start
            if len(strips) != len(source):
                # Preserve the whole page if one cell cannot satisfy the crop contract.
                record["reason"] = "invalid_line_crop"
                self._record(record)
                yield page
                continue
            start = perf_counter()
            predictions = recognizer.recognize(strips)
            record["timings_s"]["recognise"] = perf_counter() - start
            assert len(predictions) == len(source)
            ours = [TextCell(index=i, from_ocr=True, rect=cell.rect,
                             text=text, orig=text, confidence=confidence)
                    for i, (cell, (text, confidence)) in enumerate(zip(source, predictions))]
            if raster_body:
                # Recognize and log existing furniture, but do not claim to recover
                # the raster body or replace its native cells with footer OCR.
                record.update(reason="raster_body", installed=False)
            else:
                self._install(ours, page)
                record.update(status="replaced", installed=True)
            record.update(output_line_count=len(ours), recognition_performed=True)
            if self.options.call_log is not None:
                record["lines"] = [{"source_rect": old.rect.model_dump(mode="json"),
                                    "rect": new.rect.model_dump(mode="json"),
                                    "source_text": old.text, "text": new.text,
                                    "confidence": new.confidence, "from_ocr": new.from_ocr}
                                   for old, new in zip(source, ours)]
            self._filter_legacy(page, record)
            self._record(record)
            yield page

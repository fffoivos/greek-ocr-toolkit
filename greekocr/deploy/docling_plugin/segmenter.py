"""Segmenter adapter. R8 is the plugin default; pixel remains an explicit route.

Docling supplies page layout, not line segmentation. No layout is passed to R8.
"""
from __future__ import annotations

import io
import math
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np
from PIL import Image
from docling_core.types.doc import BoundingBox, CoordOrigin
from docling_core.types.doc.page import BoundingRectangle, TextCell

from .recognizer.strips import extract_strip


class ClockedDetector:
    """Measure recovery inference too, leaving native detector math untouched."""
    def __init__(self, inner):
        self.inner = inner
        self.calls = []

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def run(self, outputs, feed):
        start = perf_counter()
        value = self.inner.run(outputs, feed)
        self.calls.append(dict(seconds=perf_counter()-start,
                               shape=list(next(iter(feed.values())).shape),
                               backend_metrics=dict(getattr(self.inner, 'last_call_metrics', {}))))
        return value


def native_crop(gray, line):
    """Raw-pixel part of round6_rows_export.ocr_crop; R8 ownership mask + 4px."""
    from greekocr.segmenters._vendor.r8.shared.geometry import roi
    from greekocr.segmenters._vendor.r8.shared.geometry_bands import crop_mask
    polygon = np.asarray(line.polygon)
    a, b, c, d = roi([*list(polygon.min(0)-4), *list(polygon.max(0)+4)], gray.shape)
    crop = gray[b:d, a:c].copy()
    crop[crop_mask(crop.shape, line.extras, [a, b]) == 0] = 255
    return Image.fromarray(crop)


def _sprite(crops, path):
    if not crops:
        return []
    image = Image.new('L', (max(c.width for c in crops), sum(c.height+4 for c in crops)), 255)
    boxes, y = [], 0
    for crop in crops:
        image.paste(crop, (0, y))
        boxes.append([0, y, crop.width, y+crop.height])
        y += crop.height+4
    image.save(path, quality=80, optimize=True)
    return boxes


def detect_segmenter(plugin, page, record):
    from greekocr.segmenters import get
    from greekocr.segmenters.filters import drop_binding_and_ornaments, drop_templates_after_recognition

    begin = perf_counter()
    opts = plugin.options
    if page.parsed_page is None:
        record['reason'] = 'no_parsed_page'
        return
    record['source_line_count'] = len(page.parsed_page.textline_cells)
    start = perf_counter()
    image = page.get_image(scale=opts.crop_scale)
    record['timings_s']['render'] = perf_counter()-start
    if image is None:
        record['reason'] = 'no_page_image'
        return
    image = image.convert('RGB')
    size = (page.size.width, page.size.height)
    sx, sy = image.width/size[0], image.height/size[1]
    record['frame'] = dict(image_size=list(image.size), page_size=list(size), scale_xy=[sx, sy])
    fast = opts.segmenter != 'pixel_slow'
    filter_keys = ('spirals', 'spiral_holes', 'ornaments')
    rules = dict(opts.segmenter_rules)
    # Separate clocks without changing the segmenter/filter algorithms.
    for key in filter_keys:
        rules[key] = False
    start = perf_counter()
    if plugin.segmenter is None:
        kwargs = dict(preset=opts.segmenter_preset, rules=rules)
        if fast:
            kwargs.update(detector=opts.segmenter_detector, detector_device=opts.detector_device,
                          image_threads=0)
        plugin.segmenter = get(opts.segmenter, **kwargs)
        if fast:
            detector = plugin.segmenter.core.detector
            detector.session = ClockedDetector(detector.session)
    record['timings_s']['segmenter_setup'] = perf_counter()-start
    if fast:
        plugin.segmenter.core.detector.session.calls.clear()
    start = perf_counter()
    result = plugin.segmenter.segment(np.asarray(image), page_size=size)
    record['timings_s']['segmentation'] = perf_counter()-start
    record['segmenter_timings_s'] = result.timings
    record['timings_s']['detector'] = result.timings.get('detector_s', 0.)
    record['timings_s']['r8_correction'] = result.timings.get('correction_s', 0.)
    record['segmenter'] = opts.segmenter
    if fast:
        detector = plugin.segmenter
        calls = detector.core.detector.session.calls
        recovery_s = sum(call['seconds'] for call in calls[1:])
        # Native correction includes recovery inference. Separate those clocks
        # here, retaining the original nested clocks under segmenter_timings_s.
        record['timings_s']['detector'] += recovery_s
        record['timings_s']['r8_correction'] = max(0., record['timings_s']['r8_correction']-recovery_s)
        record['timings_s']['detector_inference'] = sum(call['seconds'] for call in calls)
        record['detector'] = dict(path=str(detector.model_path),
                                  sha256=__import__('hashlib').sha256(detector.model_path.read_bytes()).hexdigest(),
                                  requested_device=opts.detector_device,
                                  providers=detector.core.detector.session.get_providers(),
                                  calls=list(calls))
    original_order = ([line for line in result.lines if line.status == 'kept'] +
                      [line for line in result.lines if line.status == 'dropped'])
    start = perf_counter()
    # Geometric spirals need no transcription. Template rules must wait for
    # recognized text: F1 protects candidates containing >=2 Unicode letters.
    drop_binding_and_ornaments(result, np.asarray(image),
        spirals=opts.segmenter_rules.get('spirals', False), spiral_holes=False, ornaments=False)
    record['timings_s']['filter'] = perf_counter()-start
    kept = [line for line in result.lines if line.status == 'kept']
    dropped = [line for line in result.lines if line.status == 'dropped']
    start = perf_counter()
    # Preserve Stack/direct-run grayscale decoding, including OpenCV rounding.
    encoded = io.BytesIO()
    image.save(encoded, format='PNG')
    gray = cv2.imdecode(np.frombuffer(encoded.getvalue(), np.uint8), cv2.IMREAD_GRAYSCALE)
    crops, strips = [], []
    for line in kept:
        if fast:
            crop = native_crop(gray, line)
        else:
            from greekocr.pages.lines import extract_line_image
            # The unjoined pixel adapter preserves native segmentation indices.
            raw = result.extras['native']
            if raw.options.join_lines:
                from types import SimpleNamespace
                native = SimpleNamespace(**{k: np.asarray(v) if isinstance(v, list) else v
                                            for k, v in line.extras.items()})
            else:
                native = raw.segmentation.lines[line.extras['native_index']]
            crop = extract_line_image(image, native)
        crops.append(crop)
        array = np.asarray(crop, dtype=np.float32)/255.
        minimum = math.ceil(array.shape[0]/6)
        if array.shape[1] < minimum:
            pad = minimum-array.shape[1]
            array = np.pad(array, ((0, 0), (pad//2, pad-pad//2)), constant_values=1.)
        strip = extract_strip(array, (0, 0, array.shape[1], array.shape[0]))
        if strip is None:
            raise ValueError('invalid_line_crop')
        strips.append(strip)
    record['timings_s']['crop'] = perf_counter()-start
    predictions = []
    if strips:
        start = perf_counter()
        recognizer = plugin._get_recognizer()
        record['timings_s']['recognizer_setup'] = perf_counter()-start
        import torch
        if torch.device(opts.device).type == 'mps':
            torch.mps.synchronize()
        start = perf_counter()
        predictions = recognizer.recognize(strips)
        if torch.device(opts.device).type == 'mps':
            torch.mps.synchronize()
        record['timings_s']['recognition'] = perf_counter()-start
    else:
        record['timings_s']['recognition'] = 0.
    if len(predictions) != len(kept):
        raise ValueError('recognizer returned a different number of lines')
    recognized = {line.id: (crop, prediction) for line, crop, prediction in zip(kept, crops, predictions)}
    for line, (text, score) in zip(kept, predictions):
        line.extras['recognised_text'] = text
    start = perf_counter()
    drop_templates_after_recognition(result, np.asarray(image),
        [recognized[line.id][1][0] if line.id in recognized else None for line in result.lines],
        spiral_holes=opts.segmenter_rules.get('spiral_holes', False),
        ornaments=opts.segmenter_rules.get('ornaments', False),
        ornament_seeds=opts.ornament_seeds, hole_seeds=opts.hole_seeds)
    record['timings_s']['filter'] += perf_counter()-start
    kept = [line for line in result.lines if line.status == 'kept']
    crops = [recognized[line.id][0] for line in kept]
    predictions = [recognized[line.id][1] for line in kept]
    ours, lines = [], []
    for i, (line, (text, score)) in enumerate(zip(kept, predictions)):
        l, t, r, b = line.bbox
        rect = BoundingRectangle.from_bounding_box(BoundingBox(
            l=l/sx, t=t/sy, r=r/sx, b=b/sy, coord_origin=CoordOrigin.TOPLEFT))
        ours.append(TextCell(index=i, from_ocr=True, rect=rect, text=text, orig=text, confidence=score))
        lines.append(dict(text=text, confidence=score, rect=rect.model_dump(mode='json'),
                          line_index=line.extras['native_index'], table_id=None, cell_id=None,
                          geometry_source=opts.segmenter))
    plugin._install(ours, page)
    record.update(status='replaced', installed=True, output_line_count=len(ours),
                  recognition_performed=bool(strips), lines=lines)
    if opts.call_log is not None:
        # Persist exact plugin raster/crops; the runner never re-renders/re-runs OCR.
        root = opts.call_log.parent
        review = root/'review'
        review.mkdir(parents=True, exist_ok=True)
        n = record['page']
        boxes = _sprite(crops, review/f'crops-{n}.jpg')
        thumb = image.copy()
        thumb.thumbnail((2000, 2000))
        thumb.save(review/f'page-{n}.jpg', quality=85, optimize=True)
        rows = []
        kept_index = {line.id: i for i, line in enumerate(kept)}
        for line in original_order:
            number = len(rows)+1
            active = line.status == 'kept'
            i = kept_index.get(line.id)
            text, score = recognized[line.id][1] if line.id in recognized else ('', None)
            rows.append(dict(page=n, line_number=number, reading_order=number if active else None,
                source_line_index=line.extras['native_index'], segmenter_line_id=line.id,
                polygon=line.polygon, bbox=list(line.bbox), recognised_text=text, score=score,
                score_kind='mean timestep maximum softmax; uncalibrated', status=line.status,
                drop_reason=line.reason, geometry_source=opts.segmenter,
                crop_file=f'review/crops-{n}.jpg' if active else None,
                crop_bbox=boxes[i] if active else None,
                filter=line.extras.get('filter'), filter_score=line.extras.get('filter_score')))
        record['direct_rows'] = rows
    record['timings_s']['total'] = perf_counter()-begin

"""Thin adapters: no geometry fitting, stage suppression or parameter tuning here."""
from __future__ import annotations

import importlib
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from types import SimpleNamespace

import numpy as np

from .types import Line, SegmentationResult, SegmenterInfo

_BASE = ('numpy', 'Pillow', 'scipy', 'opencv-python-headless')
_INFOS = (
    SegmenterInfo('pixel_slow', 1, 'none (deterministic pixels)', _BASE,
                  'executable physical reference; known errors'),
    SegmenterInfo('paddle_small_heuristics_r7', 2, 'PP-OCRv6_small_det',
                  _BASE + ('onnxruntime', 'pyclipper', 'shapely', 'huggingface_hub'), 'historical R7 52cee3b'),
    SegmenterInfo('paddle_small_heuristics_r8', 3, 'PP-OCRv6_small_det',
                  _BASE + ('onnxruntime', 'pyclipper', 'shapely', 'huggingface_hub'), 'R8 046bd52; partial goals'),
)
_FILTER_RULES = dict(spirals=False, spiral_holes=False, ornaments=False)
_PIXEL_RULES = dict(tables=False, orientation=False, join_lines=False, **_FILTER_RULES)
# These are existing opt-in experiments, not a promise of improved curled pages.
_FAST_RULES = dict(bend=False, **_FILTER_RULES)
_PRESETS = ('born_digital', 'clean_scan', 'degraded_scan')


def available() -> list[SegmenterInfo]:
    """Return algorithm status, not a claim that local dependencies/assets exist."""
    return list(_INFOS)


def _rules(defaults, preset, overrides):
    if preset not in _PRESETS:
        raise ValueError(f'Unknown preset {preset!r}; choose {_PRESETS}')
    result = dict(defaults)
    for name, value in (overrides or {}).items():
        if name not in defaults:
            raise ValueError(f'Unknown/surgically inseparable rule: {name}')
        if type(value) is not bool:
            raise TypeError(f'rules[{name!r}] must be bool')
        result[name] = value
    return result


def _filter_options(rules, ornament_seeds, hole_seeds, ornament_threshold, hole_threshold):
    options = {name: rules[name] for name in _FILTER_RULES}
    options.update(ornament_seeds=tuple(ornament_seeds), hole_seeds=tuple(hole_seeds))
    if options['ornaments'] and not ornament_seeds:
        raise ValueError('ornaments requires ornament_seeds')
    if options['spiral_holes'] and not hole_seeds:
        raise ValueError('spiral_holes requires hole_seeds')
    if ornament_threshold is not None:
        options['ornament_threshold'] = ornament_threshold
    if hole_threshold is not None:
        options['hole_threshold'] = hole_threshold
    return options


def _filtered(result, page_image, options):
    if options['spirals']:
        from .filters import drop_binding_and_ornaments
        drop_binding_and_ornaments(result, page_image, spirals=True,
                                   spiral_holes=False, ornaments=False)
    return result


def _image(image, page_size):
    if not isinstance(image, np.ndarray) or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError('page_image must be an H×W×3 RGB numpy array')
    if image.dtype != np.uint8 or not image.shape[0] or not image.shape[1]:
        raise ValueError('page_image must be nonempty uint8 RGB (0–255)')
    size = (image.shape[1], image.shape[0])
    extent = tuple(page_size) if page_size is not None else size
    if len(extent) != 2 or not np.isfinite(extent).all() or min(extent) <= 0:
        raise ValueError('page_size must contain two positive finite dimensions')
    return size, extent


def _line(identity, polygon, baseline, status, reason, extras):
    p = np.asarray(polygon, dtype=float)
    return Line(identity, p.tolist(), (*p.min(axis=0), *p.max(axis=0)),
                baseline, status, reason, extras)


def _pixel_lines(raw):
    out = []
    # process_page establishes reading_order and stable row/column addresses.
    records = (raw.delivery + [r for r in raw.lines if r['discounted'] is not None]
               if raw.options.join_lines else raw.lines)
    for i, record in enumerate(records):
        x = np.linspace(record['x0'], record['x1'], len(record['top']))
        polygon = np.vstack([np.c_[x, record['top']],
                             np.c_[x[::-1], record['bottom'][::-1]]])
        baseline = np.c_[x, record['baseline']].tolist()
        reason = record['discounted']
        out.append(_line(f'pixel-{i:05d}', polygon, baseline,
                         'dropped' if reason is not None else 'kept', reason,
                         dict(record, native_index=i)))
    return sorted(out, key=lambda line: (line.extras.get('reading_order', 0),
                                        line.extras['native_index']))


def _fast_lines(raw):
    out = []
    for status, items in [('kept', raw['items']), ('dropped', raw.get('removed', []))]:
        for i, record in enumerate(items):
            out.append(_line(f'{status}-{i:05d}', record['polygon'],
                             record.get('baseline'), status,
                             record.get('removal') if status == 'dropped' else None,
                             dict(record, native_index=i)))
    # Reuse the existing pixel segmenter's recursive whitespace delivery order.
    # Bbox edges/centre here are ordering proxies, not measured font guides or
    # a fabricated baseline in the exported line. No polygon is changed.
    from greekocr.pages.lines import _reading_order
    proxies = [SimpleNamespace(
        line=line, x0=line.bbox[0], x1=line.bbox[2],
        font_top=np.array([line.bbox[1]]),
        font_bottom=np.array([line.bbox[3]]),
        baseline=np.array([(line.bbox[1] + line.bbox[3]) / 2]),
        xheight=line.bbox[3] - line.bbox[1], column=0) for line in out]
    return [proxy.line for proxy in _reading_order(proxies)]


class _Pixel:
    def __init__(self, info, *, preset='clean_scan', rules=None, recognizer=None,
                 ornament_seeds=(), hole_seeds=(), ornament_threshold=None, hole_threshold=None):
        self.info = info
        self.rules = _rules(_PIXEL_RULES, preset, rules)
        self.recognizer = recognizer
        self.filter_options = _filter_options(self.rules, ornament_seeds, hole_seeds,
                                              ornament_threshold, hole_threshold)

    def segment(self, page_image, *, page_size=None, layout=None):
        from greekocr.pages import PageOptions, process_page
        size, extent = _image(page_image, page_size)
        start = perf_counter()
        options = PageOptions(**{k: self.rules[k] for k in
                                 ('tables', 'orientation', 'join_lines')})
        raw = process_page(page_image, options=options, page_size=extent,
                           table_regions=layout, recognizer=self.recognizer)
        lines = _pixel_lines(raw)
        result = SegmentationResult(self.info.name, lines, size, extent,
                                  {'total_s': perf_counter() - start},
                                  {'native': raw, 'rules': dict(self.rules),
                                   'delivery': raw.delivery})
        return _filtered(result, page_image, self.filter_options)


def _model_path(detector, model_path):
    models = dict(small='PP-OCRv6_small_det.onnx',
                  medium='PP-OCRv6_medium_det.onnx',
                  mobile='PP-OCRv5_mobile_det.onnx')
    if detector not in models:
        raise ValueError('detector must be small, medium or mobile; server has no verified ONNX copy')
    if model_path is not None:
        path = Path(model_path).expanduser()
    else:
        directory = os.environ.get('GREEKOCR_SEGMENTER_MODEL_DIR')
        if directory:
            path = Path(directory).expanduser() / models[detector]
        elif detector == 'small':
            from .assets import fetch_small_detector
            return fetch_small_detector()
        else:
            raise ValueError(f'{detector} requires an explicit model_path or GREEKOCR_SEGMENTER_MODEL_DIR')
    if not path.is_file():
        raise FileNotFoundError(f'{path}: explicit detector override does not exist')
    return path


class _Fast:
    def __init__(self, info, *, detector='small', model_path=None,
                 preset='clean_scan', rules=None, image_threads=2,
                 detector_device='cpu', coreml_cache=None, ornament_seeds=(), hole_seeds=(),
                 ornament_threshold=None, hole_threshold=None):
        import cv2
        from .backends import make_session
        if detector_device not in ('cpu', 'coreml'):
            raise ValueError('detector_device must be cpu or coreml; MPS detector was removed; use coreml for GPU')
        self.detector_device = detector_device
        self.info = info
        defaults = dict(_FAST_RULES)
        if info.generation == 3:
            defaults['final_export'] = False
        self.rules = _rules(defaults, preset, rules)
        self.filter_options = _filter_options(self.rules, ornament_seeds, hole_seeds,
                                              ornament_threshold, hole_threshold)
        self.detector_model = detector
        self.model_path = _model_path(detector, model_path)
        prefix = f'greekocr.segmenters._vendor.r{7 if info.generation == 2 else 8}'
        pipeline = importlib.import_module(prefix + '.stack.pipeline')
        detector_module = importlib.import_module(prefix + '.shared.detector')
        # Same constructor operations as Stack/Detector, with explicit path
        # injection instead of modifying either module's global MODEL.
        cv2.setNumThreads(image_threads)
        core = pipeline.Stack.__new__(pipeline.Stack)
        core.bend = self.rules['bend']
        if info.generation == 3:
            core.final_export = self.rules['final_export']
        start = perf_counter()
        native_detector = detector_module.Detector.__new__(detector_module.Detector)
        native_detector.session = make_session(self.model_path, detector_device, coreml_cache)
        native_detector.name = native_detector.session.get_inputs()[0].name
        native_detector.startup_s = perf_counter() - start
        core.detector = native_detector
        core.startup_s = native_detector.startup_s
        self.core = core

    def segment(self, page_image, *, page_size=None, layout=None):
        from PIL import Image
        size, extent = _image(page_image, page_size)
        if layout is not None:
            raise ValueError('The fast stack has no external layout input')
        start = perf_counter()
        # Preserve Stack's exact OpenCV file decoding, including its grayscale
        # rounding. PNG is lossless; scratch is removed even on core failure.
        with TemporaryDirectory(prefix='greekocr-segment-') as temporary:
            path = Path(temporary) / 'page.png'
            Image.fromarray(page_image).save(path)
            raw = self.core(path)
        result = SegmentationResult(self.info.name, _fast_lines(raw), size, extent,
                                  dict(raw['timing'], wrapper_total_s=perf_counter()-start),
                                  {'native': raw, 'rules': dict(self.rules),
                                   'detector': self.detector_model,
                                   'detector_device': self.detector_device,
                                   'model_path': str(self.model_path),
                                   'reading_order': 'pages.lines._reading_order with bbox proxies; native indices preserved'})
        return _filtered(result, page_image, self.filter_options)


def get(name, **options):
    """Construct a reusable adapter; unknown options/rules fail explicitly."""
    for info in _INFOS:
        if name == info.name:
            return (_Pixel if info.generation == 1 else _Fast)(info, **options)
    raise ValueError(f'Unknown segmenter {name!r}; choose {[i.name for i in _INFOS]}')

"""Opt-in binding/ornament filters. Coordinates and height limits are source pixels.

Mutates status/reason only; preserves every line, its geometry, text and identity.
Seeds are caller-owned PNG crops, never bundled model assets. Saved-output callers
may supply a crop-provider callable instead of a page raster (no re-render/OCR).
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import math

import cv2
import numpy as np
from PIL import Image

ORNAMENT_THRESHOLD = 0.66
HOLE_THRESHOLD = 0.52
FILTER_RULES = dict(spirals=False, spiral_holes=False, ornaments=False)
SCALES = tuple(np.linspace(.75, 1.25, 11))
FIXED_HEIGHT = 48


def _get(line, name, default=None):
    return line.get(name, default) if isinstance(line, dict) else getattr(line, name, default)


def _text(line):
    text = _get(line, 'recognised_text')
    if text is None:
        text = _get(line, 'extras', {}).get('recognised_text')
    return text  # None means pre-recognition: no lexical claim can be made.


def _binary(image):
    if isinstance(image, Image.Image):
        gray = np.asarray(image.convert('L'))
    else:
        gray = np.asarray(image)
        if gray.ndim == 3:
            gray = cv2.cvtColor(gray, cv2.COLOR_RGB2GRAY)
    if gray.size == 0:
        raise ValueError('empty filter crop')
    ink = cv2.threshold(gray.astype(np.uint8), 0, 1,
                        cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    y, x = np.nonzero(ink)
    return ink[y.min():y.max()+1, x.min():x.max()+1] if len(x) else np.zeros((1, 1), np.uint8)


@lru_cache(maxsize=128)
def _seed(path, mtime_ns, size):
    with Image.open(path) as image:
        return _binary(image)


def _load_seeds(paths):
    result = []
    for path in paths:
        path = Path(path).expanduser().resolve()
        stat = path.stat()
        result.append((str(path), _seed(str(path), stat.st_mtime_ns, stat.st_size)))
    return result


def _ncc(candidate, seed):
    """Otsu/ink-trimmed NCC at seed aspect, height 48, eleven .75..1.25 scales.

    The matching canvas has the seed's aspect; ink is resized isotropically,
    with zero-ink padding, so that digits are not warped into fleurons. The
    candidate can translate within the canvas; the full seed must fit.
    """
    if not candidate.any() or not seed.any():
        return 0.
    h = FIXED_HEIGHT
    w = max(2, round(h * seed.shape[1] / seed.shape[0]))
    template = cv2.resize(seed, (w, h), interpolation=cv2.INTER_NEAREST).astype(np.float32)
    if template.std() == 0:
        return 0.
    best = 0.
    for scale in SCALES:
        width = max(2, round(h * candidate.shape[1] / candidate.shape[0] * scale))
        resized = cv2.resize(candidate, (width, round(h * scale)),
                             interpolation=cv2.INTER_NEAREST).astype(np.float32)
        canvas = np.zeros((max(resized.shape[0], h) + h//2,
                           max(resized.shape[1], w) + max(2, w//2)), np.float32)
        y = (canvas.shape[0] - resized.shape[0]) // 2
        x = (canvas.shape[1] - resized.shape[1]) // 2
        canvas[y:y+resized.shape[0], x:x+resized.shape[1]] = resized
        best = max(best, float(cv2.matchTemplate(canvas, template, cv2.TM_CCOEFF_NORMED).max()))
    return min(1., best)


def template_score(image, seeds):
    """Return max NCC and winning seed path; useful for independent diagnostics."""
    candidate = _binary(image)
    scores = [(_ncc(candidate, ink), path) for path, ink in _load_seeds(seeds)]
    return max(scores, default=(0., None), key=lambda pair: pair[0])


def line_crop(page_image, line):
    """Source bbox + 4px context, polygon masked; no recognition strip resizing."""
    if callable(page_image):
        return page_image(line)
    gray = np.asarray(page_image)
    if gray.ndim == 3:
        gray = cv2.cvtColor(gray, cv2.COLOR_RGB2GRAY)
    # Reuse the current R8 raster operator, including export-region ownership.
    from ._vendor.r8.shared.geometry import roi
    from ._vendor.r8.shared.geometry_bands import crop_mask
    bbox = _get(line, 'bbox')
    a, b, c, d = roi([bbox[0]-4, bbox[1]-4, bbox[2]+4, bbox[3]+4], gray.shape)
    crop = gray[b:d, a:c].copy()
    item = dict(_get(line, 'extras', {}))
    item.setdefault('polygon', _get(line, 'polygon'))
    mask = crop_mask(crop.shape, item, [a, b])
    crop[mask == 0] = 255
    return crop


def _record(line, evidence, reason=None, score=None):
    if isinstance(line, dict):
        line['filter'] = evidence
        if reason:
            line.update(status='dropped', drop_reason=reason, filter_score=score)
    else:
        line.extras['filter'] = evidence
        if reason:
            line.status, line.reason = 'dropped', reason
            line.extras['filter_score'] = score


def _apply_filters(result_or_lines, page_image, *, texts=None, spirals=True,
                               spiral_holes=True, ornaments=True,
                               ornament_seeds=(), hole_seeds=(),
                               ornament_threshold=ORNAMENT_THRESHOLD,
                               hole_threshold=HOLE_THRESHOLD):
    for threshold in (ornament_threshold, hole_threshold):
        if not math.isfinite(threshold) or not 0 <= threshold <= 1:
            raise ValueError('NCC thresholds must be finite in [0, 1]')
    if ornaments and not ornament_seeds:
        raise ValueError('ornaments requires ornament_seeds PNG paths')
    if spiral_holes and not hole_seeds:
        raise ValueError('spiral_holes requires hole_seeds PNG paths')
    ornament_templates = _load_seeds(ornament_seeds) if ornaments else []
    hole_templates = _load_seeds(hole_seeds) if spiral_holes else []
    lines = result_or_lines.lines if hasattr(result_or_lines, 'lines') else result_or_lines
    if ornaments or spiral_holes:
        if texts is None or len(texts) != len(lines):
            raise ValueError('template filters require a transcription for every candidate')
        for line, text in zip(lines, texts):
            if _get(line, 'status') == 'kept' and not isinstance(text, str):
                raise ValueError('template filters require a transcription for every candidate')
    for index, line in enumerate(lines):
        if _get(line, 'status') != 'kept':
            continue
        left, top, right, bottom = _get(line, 'bbox')
        width, height = right-left, bottom-top
        if spirals and height >= 250 and height >= 3*width:
            _record(line, dict(rule='spiral', score=height/max(width, 1e-12),
                               score_kind='source bbox height / width', height=height, width=width),
                    'spiral', height/max(width, 1e-12))
            continue
        if not (ornaments or spiral_holes):
            continue
        text = texts[index]
        if sum(c.isalpha() for c in text) >= 2:
            _record(line, dict(excluded='at least 2 Unicode letters', text_available=True))
            continue
        ink = _binary(line_crop(page_image, line))
        evidence = dict(text_available=text is not None, score_kind='max Otsu ink-trimmed NCC',
                        fixed_height=FIXED_HEIGHT, scales=list(SCALES))
        for key, templates, threshold in [('spiral_holes', hole_templates, hole_threshold),
                                          ('ornament', ornament_templates, ornament_threshold)]:
            if templates:
                score, seed = max(((_ncc(ink, template), path) for path, template in templates),
                                  key=lambda pair: pair[0])
                evidence[key] = dict(score=score, seed=seed, threshold=threshold)
        reason = next((key for key in ('spiral_holes', 'ornament')
                       if key in evidence and evidence[key]['score'] >= evidence[key]['threshold']), None)
        _record(line, evidence, reason, evidence[reason]['score'] if reason else None)
    return result_or_lines


def drop_templates_after_recognition(result_or_lines, page_image, texts, *,
                                     spiral_holes=True, ornaments=True,
                                     ornament_seeds=(), hole_seeds=(),
                                     ornament_threshold=ORNAMENT_THRESHOLD,
                                     hole_threshold=HOLE_THRESHOLD):
    """Filter templates using transcriptions aligned with every input line.

    A string (including an empty transcription) is required for each kept
    candidate; missing text raises before any line is changed. Lines containing
    at least two Unicode letters are always kept. Existing drops are untouched.
    """
    return _apply_filters(result_or_lines, page_image, texts=texts, spirals=False,
                          spiral_holes=spiral_holes, ornaments=ornaments,
                          ornament_seeds=ornament_seeds, hole_seeds=hole_seeds,
                          ornament_threshold=ornament_threshold, hole_threshold=hole_threshold)


def drop_binding_and_ornaments(result_or_lines, page_image, *, spirals=True,
                               spiral_holes=True, ornaments=True,
                               ornament_seeds=(), hole_seeds=(),
                               ornament_threshold=ORNAMENT_THRESHOLD,
                               hole_threshold=HOLE_THRESHOLD):
    """Compatibility postprocessor; template rules require recognised_text.

    Geometric spirals need no text. Missing template transcriptions raise;
    use drop_templates_after_recognition to supply them explicitly.
    Preserves identities, geometry, text and existing drops.
    """
    lines = result_or_lines.lines if hasattr(result_or_lines, 'lines') else result_or_lines
    texts = [_text(line) for line in lines] if spiral_holes or ornaments else None
    return _apply_filters(result_or_lines, page_image, texts=texts, spirals=spirals,
                          spiral_holes=spiral_holes, ornaments=ornaments,
                          ornament_seeds=ornament_seeds, hole_seeds=hole_seeds,
                          ornament_threshold=ornament_threshold, hole_threshold=hole_threshold)

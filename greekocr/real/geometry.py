"""Deterministic, CPU-only local line rectification; no label repair or OCR."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
import math
from typing import Any, Literal, Mapping, Sequence, TypeAlias

import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageFilter
from scipy import ndimage

Box: TypeAlias = tuple[float, float, float, float]
PixelBox: TypeAlias = tuple[int, int, int, int]
Profile: TypeAlias = Literal['scan', 'born_digital']
GEOMETRY_POLICY = 'o4d-local-line-geometry-v1'

# Pixel thresholds are for the staged ~200 dpi parliament strips, not DPI invariant.
SCAN_MAX_CURL_PX = 48.0  # More than a typical line height needs G3/page review.
SCAN_MIN_INK_COVERAGE = 0.015  # Allow faded scans, reject nearly empty strips.
SCAN_MAX_INK_COVERAGE = 0.55  # Reject solid rules, inverted/filled crops.
MIN_COMPONENT_AREA = 3  # Same noise floor as the preserved character-ink check.
DEFAULT_PAD = 16  # Bounded search for clipped terminal glyphs and accents.
STRIP_MARGIN_PX = 2  # Rounding room above accents and below descenders.
BASELINE_CLUSTER_TOLERANCE = 0.55  # In units of estimated body height.
INK_DARK_FLOOR = 80  # Retain dense strokes even where local averaging is dark.
INK_MAX_GRAY = 220  # Exclude near-white scan background.
INK_MIN_LOCAL_CONTRAST = 12  # Retain faded ink above paper texture contrast.
BACKGROUND_RADIUS_PX = 15  # Local paper estimate at this fixture scale.
HYPHEN_MIN_ASPECT = 2.0
HYPHEN_MAX_HEIGHT_RATIO = 0.45
HYPHEN_MIN_WIDTH_RATIO = 0.15
HYPHEN_MAX_WIDTH_RATIO = 1.25
HYPHEN_CENTER_TOLERANCE = 0.35
HYPHEN_MAX_GAP_RATIO = 1.50

__all__ = ['Component', 'BaselineCurve', 'GeometryDiagnostics', 'Admission',
           'LineCrop', 'TextLayerBox', 'ink_components', 'refine_line',
           'split_multiline', 'scan_admission', 'hyphen_at_line_end',
           'refine_page_lines']


@dataclass(frozen=True)
class Component:
    """An 8-connected ink component in top-origin, half-open page pixels."""
    id: int
    box: PixelBox
    area: int
    center_x: float
    center_y: float


@dataclass(frozen=True)
class BaselineCurve:
    """y = c2*t*t + c1*t + c0, t=(page_x-x_origin)/x_scale."""
    c2: float
    c1: float
    c0: float
    x_origin: float
    x_scale: float

    def evaluate(self, x: float) -> float:
        """Evaluate a page-space baseline at a page-space horizontal position."""
        t = (x - self.x_origin) / self.x_scale
        return float((self.c2 * t + self.c1) * t + self.c0)


@dataclass(frozen=True)
class GeometryDiagnostics:
    """Output-strip geometry plus the unchanged input candidate's legacy evidence."""
    n_baselines: int
    source_n_baselines: int
    curl_amplitude_px: float
    x_height_px: float
    ink_coverage: float
    blank_ink: bool
    ink_pixels: int
    retained_ink_fraction: float
    horizontal_extension_px: tuple[int, int]
    source_boundary_ink: tuple[str, ...]
    hyphen_missing_in_label: bool | None = None
    legacy: Mapping[str, Any] = field(default_factory=dict)
    policy: str = GEOMETRY_POLICY
    search_boundary_ink: tuple[str, ...] = ()


@dataclass(frozen=True)
class Admission:
    """Geometry decision, named policy thresholds and diagnostic evidence."""
    admitted: bool
    profile: Profile
    reject_reasons: tuple[str, ...]
    thresholds: Mapping[str, float]
    diagnostics: Mapping[str, Any]

    def receipt(self) -> dict[str, Any]:
        """Return a JSON-serializable policy receipt; admission is never human gold."""
        return asdict(self)


@dataclass(frozen=True)
class LineCrop:
    """Rectified grayscale strip and page-space provenance; text stays provisional."""
    image: Image.Image
    source_box: PixelBox
    search_box: PixelBox
    refined_box: PixelBox
    curve: BaselineCurve
    kept_components: tuple[Component, ...]
    dropped_components: tuple[Component, ...]
    diagnostics: GeometryDiagnostics
    ascent: int
    descent: int
    input_index: int | None = None
    split_index: int = 0
    text: str | None = None
    source_text: str | None = None
    parent_box: PixelBox | None = None
    text_assignment_required: bool = False

    def receipt(self) -> dict[str, Any]:
        """Return deterministic geometry metadata, excluding raster image bytes."""
        return {name: asdict(value) if hasattr(value, '__dataclass_fields__') else value
                for name, value in self.__dict__.items()
                if name not in ('image', 'kept_components', 'dropped_components')} | {
                    'kept_components': [asdict(c) for c in self.kept_components],
                    'dropped_components': [asdict(c) for c in self.dropped_components]}


@dataclass(frozen=True)
class TextLayerBox:
    """A pixel line box, raw label and optional original vendored admission row."""
    box: Box
    text: str | None = None
    legacy: Mapping[str, Any] | None = None


def _box(box: Sequence[float], size: tuple[int, int] | None = None) -> PixelBox:
    if len(box) != 4 or not all(math.isfinite(v) for v in box):
        raise ValueError('box must contain four finite pixel coordinates')
    x0, y0, x1, y1 = box
    if x1 <= x0 or y1 <= y0:
        raise ValueError('box must have positive width and height')
    result = (math.floor(x0), math.floor(y0), math.ceil(x1), math.ceil(y1))
    if size is not None:
        w, h = size
        result = (max(0, result[0]), max(0, result[1]),
                  min(w, result[2]), min(h, result[3]))
        if result[2] <= result[0] or result[3] <= result[1]:
            raise ValueError('box is outside the image')
    return result


def _ink(image: Image.Image) -> NDArray[np.bool_]:
    gray = image.convert('L')
    a = np.asarray(gray, dtype=np.int16)
    background = np.asarray(gray.filter(ImageFilter.BoxBlur(BACKGROUND_RADIUS_PX)), dtype=np.int16)
    # Local contrast removes grey paper/shadows; the dark floor retains dense strokes.
    return (a < INK_DARK_FLOOR) | ((a < INK_MAX_GRAY) & (background - a >= INK_MIN_LOCAL_CONTRAST))


def _components(image: Image.Image, box: PixelBox) -> tuple[
        NDArray[np.int32], tuple[Component, ...]]:
    labels, count = ndimage.label(_ink(image), structure=np.ones((3, 3)))
    areas = np.bincount(labels.ravel(), minlength=count + 1)
    slices = ndimage.find_objects(labels)
    xoff, yoff = box[:2]
    result = []
    for ident, sl in enumerate(slices, 1):
        if sl is None or areas[ident] < MIN_COMPONENT_AREA:
            continue
        ys, xs = sl
        yy, xx = np.nonzero(labels[sl] == ident)
        result.append(Component(ident, (xoff+xs.start, yoff+ys.start,
                                       xoff+xs.stop, yoff+ys.stop),
                                int(areas[ident]), float(xx.mean()+xs.start+xoff),
                                float(yy.mean()+ys.start+yoff)))
    return labels, tuple(result)


def ink_components(page_image: Image.Image, box: Box | None = None) -> tuple[Component, ...]:
    """Measure significant ink in a pixel box (or the whole locally staged image)."""
    region = _box(box if box is not None else (0, 0, *page_image.size), page_image.size)
    return _components(page_image.crop(region), region)[1]


def _fit(xs: NDArray[np.float64], ys: NDArray[np.float64], *,
         robust: bool = True) -> BaselineCurve:
    origin = float((xs.min() + xs.max()) / 2)
    scale = max(1.0, float(np.ptp(xs)) / 2)
    t = (xs - origin) / scale
    degree = min(2, len(np.unique(xs)) - 1)
    design = np.column_stack([t**i for i in range(degree+1)])
    weights = np.ones(len(xs))
    coeff = np.linalg.lstsq(design, ys, rcond=None)[0]
    if robust:
        for _ in range(12):
            residual = ys - design @ coeff
            sigma = max(1.0, 1.4826*float(np.median(np.abs(residual-np.median(residual)))))
            weights = np.minimum(1.0, 1.345*sigma / np.maximum(np.abs(residual), 1e-8))
            root = np.sqrt(weights)
            coeff = np.linalg.lstsq(design*root[:, None], ys*root, rcond=None)[0]
    padded = np.pad(coeff, (0, 3-len(coeff)))
    return BaselineCurve(float(padded[2]), float(padded[1]), float(padded[0]), origin, scale)


def _values(curve: BaselineCurve, xs: NDArray[np.float64]) -> NDArray[np.float64]:
    t = (xs - curve.x_origin) / curve.x_scale
    return (curve.c2*t + curve.c1)*t + curve.c0


def _height(components: Sequence[Component]) -> float:
    candidates = sorted((c for c in components if c.area >= 12
                         and (c.box[2]-c.box[0]) / max(1, c.box[3]-c.box[1]) < 3),
                        key=lambda c: c.box[3]-c.box[1])
    if not candidates:
        return 4.0
    # Area weighting prevents faded fragments/accents from dominating the estimate.
    weights = np.cumsum([min(500, c.area) for c in candidates])
    selected = candidates[int(np.searchsorted(weights, .60*weights[-1]))]
    return max(4.0, float(selected.box[3]-selected.box[1]))


def _clusters(components: Sequence[Component]) -> tuple[
        list[tuple[BaselineCurve, tuple[Component, ...]]], float]:
    height = _height(components)
    body = [c for c in components if c.box[3]-c.box[1] >= .45*height
            and c.area >= max(5, .06*height**2)
            and c.box[2]-c.box[0] < 5*height
            and c.box[3]-c.box[1] < 2.5*height]
    if not body:
        return [], height
    xs = np.array([c.center_x for c in body])
    ys = np.array([c.center_y for c in body])
    available = np.ones(len(body), dtype=bool)
    curves = []
    rng = np.random.default_rng(0)  # Local seed; never consume caller RNG state.
    tolerance = BASELINE_CLUSTER_TOLERANCE*height
    for _ in range(4):
        indices = np.flatnonzero(available)
        minimum = max(3, math.ceil(.08*len(body)))
        if len(indices) < minimum:
            break
        candidates = [_fit(xs[indices], ys[indices])]
        for _ in range(160):
            sample = rng.choice(indices, 3, replace=False)
            if np.ptp(xs[sample]) < .4*max(1, np.ptp(xs[indices])):
                continue
            trial = _fit(xs[sample], ys[sample], robust=False)
            if abs(trial.c2) <= .75*height and np.ptp(_values(trial, xs[indices])) <= 3*height:
                candidates.append(trial)
        def separate(candidate: BaselineCurve) -> bool:
            support = available & (np.abs(ys-_values(candidate, xs)) <= tolerance)
            if support.sum() < minimum or abs(candidate.c2) > .75*height:
                return False
            for prior in curves:
                delta = _values(candidate, xs[support])-_values(prior, xs[support])
                if max(np.mean(delta >= .90*height), np.mean(delta <= -.90*height)) < .90:
                    return False
            return True
        candidates = [c for c in candidates if separate(c)]
        if not candidates:
            break
        best = max(candidates, key=lambda c: (
            int(np.count_nonzero(available & (np.abs(ys-_values(c, xs)) <= tolerance))),
            -float(np.median(np.abs(ys[indices]-_values(c, xs[indices]))))))
        support = available & (np.abs(ys-_values(best, xs)) <= tolerance)
        if support.sum() < minimum:
            break
        fitted = _fit(xs[support], ys[support])
        support = available & (np.abs(ys-_values(fitted, xs)) <= tolerance)
        if support.sum() < minimum:
            break
        curves.append(_fit(xs[support], ys[support]))
        available[support] = False
    if not curves:
        curves = [_fit(xs, ys)]
    middle = float(np.median(xs))
    curves.sort(key=lambda c: c.evaluate(middle))
    groups: list[list[Component]] = [[] for _ in curves]
    for component in components:
        # Long rules and tall gutter strokes never become glyph/baseline support.
        w, h = component.box[2]-component.box[0], component.box[3]-component.box[1]
        if w > 5*height or h > 2.5*height:
            continue
        distances = [abs(component.center_y-c.evaluate(component.center_x)) for c in curves]
        nearest = int(np.argmin(distances))
        if distances[nearest] <= .90*height:
            groups[nearest].append(component)
    return [(c, tuple(g)) for c, g in zip(curves, groups) if g], height


def split_multiline(box: Box, components: Sequence[Component]) -> list[PixelBox]:
    """Split supported baseline clusters inside a box; never assign label substrings."""
    original = _box(box)
    clusters, _ = _clusters(components)
    middle = (original[0]+original[2])/2
    clusters = [(curve, group) for curve, group in clusters
                if original[1] <= curve.evaluate(middle) < original[3]]
    if len(clusters) <= 1:
        return [original]
    return [(min(c.box[0] for c in group), min(c.box[1] for c in group),
             max(c.box[2] for c in group), max(c.box[3] for c in group))
            for _, group in clusters]


def _legacy(image: Image.Image, box: PixelBox) -> dict[str, Any]:
    from greekocr._vendor.bench.admission import char_ink_diagnostics, ink_diagnostics
    crop = image.crop(box)
    # No character coordinates were supplied: expose their absence, never invent them.
    row: dict[str, Any] = dict(text='', bbox_pixel=list(box), invalid_char_geometry=True)
    row.update(ink_diagnostics(crop, (0, 0, *crop.size)))
    row.update(char_ink_diagnostics(crop, []))
    return row


def refine_line(page_image: Image.Image, box: Box, *, pad: int = DEFAULT_PAD) -> LineCrop:
    """Select one baseline, fit glyph bottoms robustly and sample a curved ink strip."""
    if isinstance(pad, bool) or not isinstance(pad, int) or pad < 0:
        raise ValueError('pad must be a nonnegative integer')
    source = _box(box, page_image.size)
    x0, y0, x1, y1 = source
    search = _box((x0-pad, y0-pad, x1+pad, y1+pad), page_image.size)
    gray = page_image.convert('L')
    local = gray.crop(search)
    labels, components = _components(local, search)
    clusters, height = _clusters(components)
    legacy = _legacy(gray, source)
    if not clusters:
        curve = BaselineCurve(0, 0, float(y1-1), float(x0), max(1.0, x1-x0))
        diag = GeometryDiagnostics(0, 0, 0.0, height, 0.0, True, 0, 0.0,
                                   (0, 0), (), legacy=legacy)
        return LineCrop(Image.new('L', (x1-x0, y1-y0), 255), source, search, source,
                        curve, (), components, diag, y1-y0-1, 0)
    # Prefer body ink actually inside the requested box, then proximity to its centre.
    def score(cluster: tuple[BaselineCurve, tuple[Component, ...]]) -> tuple[float, float]:
        center_curve, group = cluster
        inside = sum(c.area for c in group if x0 <= c.center_x < x1 and y0 <= c.center_y < y1)
        return float(inside), -abs(center_curve.evaluate((x0+x1)/2)-(y0+y1)/2)
    _, kept = max(clusters, key=score)
    kept_ids = {c.id for c in kept}
    dropped = tuple(c for c in components if c.id not in kept_ids)
    body = [c for c in kept if c.box[3]-c.box[1] >= .60*height and c.area >= .06*height**2]
    if not body:
        body = list(kept)
    curve = _fit(np.array([c.center_x for c in body]),
                 np.array([float(c.box[3]-1) for c in body]))
    selected = np.isin(labels, list(kept_ids))
    yy, xx = np.nonzero(selected)
    page_x = xx.astype(float)+search[0]
    page_y = yy+search[1]
    baselines = np.rint(_values(curve, page_x)).astype(int)
    ascent = max(0, int(np.max(baselines-page_y)))+STRIP_MARGIN_PX
    descent = max(0, int(np.max(page_y-baselines)))+STRIP_MARGIN_PX
    left = max(0, min(x0, min(c.box[0] for c in kept)-STRIP_MARGIN_PX))
    right = min(gray.width, max(x1, max(c.box[2] for c in kept)+STRIP_MARGIN_PX))
    columns = np.arange(left, right, dtype=float)
    column_baselines = np.rint(_values(curve, columns)).astype(int)
    rows = column_baselines[None, :]+np.arange(-ascent, descent+1)[:, None]
    local_rows = rows-search[1]
    local_columns = columns.astype(int)-search[0]
    valid = ((local_rows >= 0) & (local_rows < local.height)
             & (local_columns[None, :] >= 0) & (local_columns[None, :] < local.width))
    safe_rows = np.clip(local_rows, 0, local.height-1)
    safe_columns = np.clip(local_columns, 0, local.width-1)[None, :]
    # Mask dropped components while retaining grayscale intensity of selected ink.
    mask = selected[safe_rows, safe_columns] & valid
    pixels = np.full(rows.shape, 255, dtype=np.uint8)
    pixels[mask] = np.asarray(local)[safe_rows, safe_columns][mask]
    strip = Image.fromarray(pixels)
    boundary = []
    for name, condition in [('left', np.any(page_x == 0)), ('right', np.any(page_x == gray.width-1)),
                            ('top', np.any(page_y == 0)), ('bottom', np.any(page_y == gray.height-1))]:
        if condition:
            boundary.append(name)
    search_boundary = tuple(name for name, condition in [
        ('left', np.any(xx == 0)), ('right', np.any(xx == local.width-1)),
        ('top', np.any(yy == 0)), ('bottom', np.any(yy == local.height-1))] if condition)
    coverage = float(mask.mean())
    diag = GeometryDiagnostics(1, len(clusters), float(np.ptp(_values(curve, columns))),
                               height, coverage, not bool(mask.any()), int(mask.sum()),
                               float(mask.sum()/len(xx)), (x0-left, right-x1),
                               tuple(boundary), legacy=legacy, search_boundary_ink=search_boundary)
    refined = (left, max(0, int(rows.min())), right, min(gray.height, int(rows.max())+1))
    return LineCrop(strip, source, search, refined, curve, kept, dropped, diag, ascent, descent)


def scan_admission(diagnostics: GeometryDiagnostics | Mapping[str, Any], *,
                   profile: Profile = 'scan') -> Admission:
    """Gate rectified scan geometry or replay the complete unchanged vendored rule."""
    if profile not in ('scan', 'born_digital'):
        raise ValueError('profile must be scan or born_digital')
    values = asdict(diagnostics) if isinstance(diagnostics, GeometryDiagnostics) else dict(diagnostics)
    if profile == 'born_digital':
        from greekocr._vendor.bench.admission import admit
        row = dict(values.get('legacy', values))
        if 'text' not in row or 'bbox_pixel' not in row:
            raise ValueError('born_digital requires original text and bbox_pixel evidence')
        result = admit(row)
        return Admission(bool(result['admitted']), profile, tuple(result['reject_reasons']),
                         {'ink_bbox_error_max': .25, 'crop_height_min': 8.0,
                          'crop_height_max': 120.0, 'aspect_ratio_min': 2.0}, values)
    thresholds = {'curl_amplitude_px_max': SCAN_MAX_CURL_PX,
                  'ink_coverage_min': SCAN_MIN_INK_COVERAGE,
                  'ink_coverage_max': SCAN_MAX_INK_COVERAGE,
                  'n_baselines_required': 1.0}
    reasons = []
    if values['n_baselines'] != 1:
        reasons.append('multiline_ink' if values['n_baselines'] > 1 else 'no_baseline')
    curl, coverage = values['curl_amplitude_px'], values['ink_coverage']
    if not math.isfinite(curl) or curl < 0 or curl > SCAN_MAX_CURL_PX:
        reasons.append('excessive_curl')
    if not math.isfinite(coverage) or not SCAN_MIN_INK_COVERAGE <= coverage <= SCAN_MAX_INK_COVERAGE:
        reasons.append('ink_coverage')
    if values['blank_ink']:
        reasons.append('blank_ink')
    # Explicit cross-column evidence remains a reject: G1 cannot assign columns.
    legacy = values.get('legacy', values)
    pdf_box = legacy.get('bbox_pdf')
    gutters = legacy.get('column_candidate_gutters_pdf', []) + legacy.get('column_gutters_pdf', [])
    spanning = legacy.get('spanning_gutters_pdf', [])
    if legacy.get('cross_column', False) or bool(pdf_box and any(
            pdf_box[0] < g[0] and pdf_box[2] > g[1] and g not in spanning for g in gutters)):
        reasons.append('cross_column')
    return Admission(not reasons, profile, tuple(reasons), thresholds, values)


def hyphen_at_line_end(crop: LineCrop | Image.Image, text: str) -> bool:
    """Flag a terminal dash after a body glyph when the raw label lacks a hyphen."""
    if text.rstrip().endswith(('-', '\u00ad', '\u2010', '\u2011')):
        return False
    image = crop.image if isinstance(crop, LineCrop) else crop
    components = ink_components(image)
    height = crop.diagnostics.x_height_px if isinstance(crop, LineCrop) else _height(components)
    glyphs = [c for c in components if c.box[3]-c.box[1] >= .5*height
              and c.area >= .06*height**2 and c.box[2]-c.box[0] < 5*height]
    if not glyphs:
        return False
    last = max(glyphs, key=lambda c: c.box[2])
    for c in components:
        w, h = c.box[2]-c.box[0], c.box[3]-c.box[1]
        gap = c.box[0]-last.box[2]
        if (0 <= gap <= HYPHEN_MAX_GAP_RATIO*height and w/h >= HYPHEN_MIN_ASPECT
                and HYPHEN_MIN_WIDTH_RATIO*height <= w <= HYPHEN_MAX_WIDTH_RATIO*height
                and h <= HYPHEN_MAX_HEIGHT_RATIO*height
                and abs(c.center_y-last.center_y) <= HYPHEN_CENTER_TOLERANCE*height):
            return True
    return False


def refine_page_lines(pdf_page_image: Image.Image,
                      text_layer_boxes: Sequence[TextLayerBox | Box | Mapping[str, Any]], *,
                      pad: int = DEFAULT_PAD) -> list[LineCrop]:
    """Refine pixel boxes in input order; split labels are withheld for caller assignment."""
    results = []
    for index, entry in enumerate(text_layer_boxes):
        if isinstance(entry, TextLayerBox):
            candidate = entry
        elif isinstance(entry, Mapping):
            recorded = entry.get('legacy')
            if recorded is None and any(key in entry for key in ('ink_bbox_error', 'unexplained_ink',
                                                                 'invalid_char_geometry', 'cross_column')):
                recorded = entry
            candidate = TextLayerBox(tuple(entry['bbox_pixel']), entry.get('text'), recorded)  # type: ignore[arg-type]
        else:
            candidate = TextLayerBox(entry)
        first = refine_line(pdf_page_image, candidate.box, pad=pad)
        boxes = split_multiline(candidate.box, first.kept_components+first.dropped_components)
        for split_index, box in enumerate(boxes):
            line = first if len(boxes) == 1 else refine_line(pdf_page_image, box, pad=pad)
            text = candidate.text if len(boxes) == 1 else None
            legacy = dict(candidate.legacy) if candidate.legacy is not None else dict(first.diagnostics.legacy)
            if candidate.text is not None:
                legacy['text'] = candidate.text
            diag = replace(line.diagnostics, legacy=legacy,
                           hyphen_missing_in_label=hyphen_at_line_end(line, text) if text is not None else None)
            results.append(replace(line, diagnostics=diag, input_index=index, split_index=split_index,
                                   text=text, source_text=candidate.text, parent_box=first.source_box,
                                   text_assignment_required=len(boxes) > 1))
    return results

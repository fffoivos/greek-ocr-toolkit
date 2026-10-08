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
GeometryPolicy: TypeAlias = Literal['v1', 'v2', 'v3']
GEOMETRY_POLICY = 'o4d-local-line-geometry-v3'

# Pixel thresholds are for the staged ~200 dpi parliament strips, not DPI invariant.
SCAN_MAX_CURL_PX = 48.0  # More than a typical line height needs G3/page review.
SCAN_MIN_INK_COVERAGE = 0.015  # Allow faded scans, reject nearly empty strips.
SCAN_MAX_INK_COVERAGE = 0.55  # Reject solid rules, inverted/filled crops.
MIN_COMPONENT_AREA = 3  # Same noise floor as the preserved character-ink check.
DEFAULT_PAD = 16  # Bounded search for clipped terminal glyphs and accents.
STRIP_MARGIN_PX = 2  # Rounding room above accents and below descenders.
BASELINE_CLUSTER_TOLERANCE = 0.35  # Separate nearby body tracks before assigning marks.
BAND_ASCENT_RATIO = 1.9  # Capitals and stacked breathing/accent marks.
BAND_DESCENT_RATIO = 0.6
INK_MASS_MAX_GRAY = 220  # Dark-pixel census, independent of component membership.
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
           'refine_page_lines', 'crop_quality']


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
    selected_cluster_index: int | None = None
    baseline_clusters: tuple[Mapping[str, Any], ...] = ()
    cluster_selection: str = 'baseline mean y nearest original box vertical centre'
    band_ascent_px: float = 0.0
    band_descent_px: float = 0.0
    diacritic_component_ids: tuple[int, ...] = ()
    band_ink_original: int = 0
    band_ink_refined: int = 0
    diacritic_ink_original: int = 0
    diacritic_ink_refined: int = 0
    band_ink_retained_fraction: float = 1.0
    diacritic_ink_retained_fraction: float = 1.0
    resampling: str = 'integer per-column row shift (nearest-neighbour)'
    source_box: PixelBox | None = None
    strip_x_origin: int | None = None
    strip_baseline_px: int | None = None
    baseline_curve: BaselineCurve | None = None
    rectified: bool = True


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


def _clusters(components: Sequence[Component], *,
              tolerance_ratio: float = BASELINE_CLUSTER_TOLERANCE) -> tuple[
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
    tolerance = tolerance_ratio*height
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


def _baseline(group: Sequence[Component], height: float) -> BaselineCurve:
    """Fit body bottoms only; detached marks must not move the target baseline."""
    body = [c for c in group if c.box[3]-c.box[1] >= .60*height
            and c.area >= .06*height**2]
    if not body:
        body = list(group)
    return _fit(np.array([c.center_x for c in body]),
                np.array([float(c.box[3]-1) for c in body]))


def _overlaps_band(component: Component, curve: BaselineCurve, height: float) -> bool:
    xs = np.arange(component.box[0], component.box[2], dtype=float)
    baseline = _values(curve, xs)
    return bool(np.any((component.box[1] <= baseline+BAND_DESCENT_RATIO*height)
                       & (component.box[3] > baseline-BAND_ASCENT_RATIO*height)))


def _diacritics(components: Sequence[Component], body: Sequence[Component],
                curve: BaselineCurve, height: float) -> set[int]:
    """Protect detached small marks above and horizontally over kept body ink."""
    return {c.id for c in components
            if c.box[3]-c.box[1] < .60*height and c.box[2]-c.box[0] <= 1.25*height
            and c.area < .60*height**2
            and c.box[3] <= curve.evaluate(c.center_x)-height+STRIP_MARGIN_PX
            and any(c.box[0] < b.box[2] and c.box[2] > b.box[0] for b in body)}


def refine_line(page_image: Image.Image, box: Box, *, pad: int = DEFAULT_PAD,
                policy: GeometryPolicy = 'v3') -> LineCrop:
    """Rectify a local line; v1/v2 preserve historical crop behavior for comparison."""
    if isinstance(pad, bool) or not isinstance(pad, int) or pad < 0:
        raise ValueError('pad must be a nonnegative integer')
    if policy not in ('v1', 'v2', 'v3'):
        raise ValueError('policy must be v1, v2 or v3')
    policy_name = f'o4d-local-line-geometry-{policy}'
    source = _box(box, page_image.size)
    x0, y0, x1, y1 = source
    search = _box((x0-pad, y0-pad, x1+pad, y1+pad), page_image.size)
    gray = page_image.convert('L')
    local = gray.crop(search)
    labels, components = _components(local, search)
    clusters, height = _clusters(components, tolerance_ratio=.55 if policy == 'v1' else BASELINE_CLUSTER_TOLERANCE)
    legacy = _legacy(gray, source)
    if not clusters:
        curve = BaselineCurve(0, 0, float(y1-1), float(x0), max(1.0, x1-x0))
        original = gray.crop(source)
        if policy == 'v1':
            original = Image.new('L', original.size, 255)
        ink = _ink(original)
        diag = GeometryDiagnostics(0, 0, 0.0, height, float(ink.mean()), not bool(ink.any()),
                                   int(ink.sum()), 1.0,
                                   (0, 0), (), legacy=legacy, policy=policy_name,
                                   source_box=source, strip_x_origin=x0,
                                   strip_baseline_px=y1-y0-1, baseline_curve=curve, rectified=False)
        return LineCrop(original, source, search, source, curve,
                        components if policy != 'v1' else (),
                        () if policy != 'v1' else components, diag, y1-y0-1, 0)
    columns_in_box = np.arange(x0, x1, dtype=float)
    baselines = [_baseline(group, height) for _, group in clusters]
    means = [float(_values(c, columns_in_box).mean()) for c in baselines]
    center = (y0+y1)/2
    target = min(range(len(clusters)), key=lambda i: (abs(means[i]-center), i))
    if policy == 'v1':
        target = max(range(len(clusters)), key=lambda i: (
            sum(c.area for c in clusters[i][1] if x0 <= c.center_x < x1 and y0 <= c.center_y < y1),
            -abs(clusters[i][0].evaluate((x0+x1)/2)-center)))
    curve = baselines[target]
    cluster_diagnostics = tuple(dict(index=i, curve=asdict(baselines[i]), mean_y=means[i],
                                    distance_to_box_center_px=abs(means[i]-center),
                                    component_ids=[c.id for c in group],
                                    support_ink_pixels=sum(c.area for c in group), selected=i == target)
                                for i, (_, group) in enumerate(clusters))
    other_ids = {c.id for i, (_, group) in enumerate(clusters) if i != target for c in group}
    overlapping = tuple(c for c in components if _overlaps_band(c, curve, height))
    body = [c for c in overlapping if c.box[3]-c.box[1] >= .60*height
            and c.area >= .06*height**2 and c.box[2]-c.box[0] < 5*height]
    diacritic_ids = _diacritics(components, body, curve, height)
    protected_ids = {c.id for c in overlapping} | diacritic_ids
    dropped = tuple(c for c in components if c.id in other_ids and c.id not in protected_ids)
    # The band/mark keep rule takes precedence over neighbour assignment in v3.
    # V2 already used this combination; keep its selectable raster behavior.
    if policy == 'v1':
        target_ids = {c.id for c in clusters[target][1]}
        dropped = tuple(c for c in components if c.id not in target_ids)
        diacritic_ids = set()
    dropped_ids = {c.id for c in dropped}
    kept = tuple(c for c in components if c.id not in dropped_ids)
    dropped_mask = np.isin(labels, list(dropped_ids))
    selected = _ink(local) & ~dropped_mask
    if policy == 'v1':
        selected = np.isin(labels, [c.id for c in kept])
    yy, xx = np.nonzero(selected)
    page_x = xx.astype(float)+search[0]
    page_y = yy+search[1]
    baselines = np.rint(_values(curve, page_x)).astype(int)
    ascent = max(math.ceil(BAND_ASCENT_RATIO*height) if policy != 'v1' else 0,
                 int(np.max(baselines-page_y)), 0)+STRIP_MARGIN_PX
    descent = max(math.ceil(BAND_DESCENT_RATIO*height) if policy != 'v1' else 0,
                  int(np.max(page_y-baselines)), 0)+STRIP_MARGIN_PX
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
    # Copy source intensities (including light edges and paper), with integer shifts.
    # Only explicitly dropped neighbour components become white in v2/v3.
    copy_mask = ~dropped_mask[safe_rows, safe_columns] & valid
    mask = selected[safe_rows, safe_columns] & valid
    if policy == 'v1':
        copy_mask = mask
    pixels = np.full(rows.shape, 255, dtype=np.uint8)
    pixels[copy_mask] = np.asarray(local)[safe_rows, safe_columns][copy_mask]
    strip = Image.fromarray(pixels)
    # Compare the original box in page coordinates to exactly those same pixels
    # in rectified coordinates, using the unrounded curve to define both zones.
    source_columns = np.arange(x0, x1, dtype=float)
    source_baseline = _values(curve, source_columns)[None, :]
    source_rows = np.arange(y0, y1)[:, None]
    band = ((source_rows >= source_baseline-BAND_ASCENT_RATIO*height)
            & (source_rows <= source_baseline+BAND_DESCENT_RATIO*height))
    marks = band & (source_rows < source_baseline-height)
    original_dark = np.asarray(gray.crop(source)) < INK_MASS_MAX_GRAY
    output_rows = source_rows-np.rint(source_baseline).astype(int)+ascent
    output_columns = np.arange(x0-left, x1-left)[None, :]
    in_strip = (output_rows >= 0) & (output_rows < pixels.shape[0])
    refined_dark = (pixels[np.clip(output_rows, 0, pixels.shape[0]-1), output_columns]
                    < INK_MASS_MAX_GRAY) & in_strip
    band_old, band_new = int((original_dark & band).sum()), int((refined_dark & band).sum())
    marks_old, marks_new = int((original_dark & marks).sum()), int((refined_dark & marks).sum())
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
                               tuple(boundary), legacy=legacy, policy=policy_name, search_boundary_ink=search_boundary,
                               selected_cluster_index=target, baseline_clusters=cluster_diagnostics,
                               band_ascent_px=BAND_ASCENT_RATIO*height,
                               band_descent_px=BAND_DESCENT_RATIO*height,
                               diacritic_component_ids=tuple(sorted(diacritic_ids)),
                               band_ink_original=band_old, band_ink_refined=band_new,
                               diacritic_ink_original=marks_old, diacritic_ink_refined=marks_new,
                               band_ink_retained_fraction=band_new/band_old if band_old else 1.0,
                               diacritic_ink_retained_fraction=marks_new/marks_old if marks_old else 1.0,
                               cluster_selection=('largest in-box support, then nearest centre' if policy == 'v1'
                                                  else 'baseline mean y nearest original box vertical centre'),
                               source_box=source, strip_x_origin=left,
                               strip_baseline_px=ascent, baseline_curve=curve)
    refined = (left, max(0, int(rows.min())), right, min(gray.height, int(rows.max())+1))
    return LineCrop(strip, source, search, refined, curve, kept, dropped, diag, ascent, descent)


def _appearance(pixels: NDArray[np.uint8]) -> tuple[float, float]:
    """Ink/paper contrast and Laplacian variance (higher means sharper)."""
    values = pixels.astype(float)
    dark = values[values < INK_MASS_MAX_GRAY]
    contrast = (max(0.0, float(np.percentile(values, 95))-float(dark.mean()))/255
                if dark.size else 0.0)
    sharpness = float(ndimage.laplace(values, mode='nearest').var())
    return contrast, sharpness


def _residual_curl(image: Image.Image, expected_baseline: float,
                   width: int) -> float | None:
    components = ink_components(image)
    clusters, height = _clusters(components)
    if not clusters:
        return None
    columns = np.arange(width, dtype=float)
    curves = [_baseline(group, height) for _, group in clusters]
    curve = min(curves, key=lambda c: abs(float(_values(c, columns).mean())-expected_baseline))
    return float(np.ptp(_values(curve, columns)))


def crop_quality(original_crop: Image.Image, refined_crop: Image.Image,
                 diagnostics: GeometryDiagnostics | Mapping[str, Any]) -> dict[str, Any]:
    """Measure pixel-only crop signals using recorded page-to-strip geometry.

    Accept a GeometryDiagnostics, its serialized dict, or a LineCrop receipt.
    Reader hooks, if present in the mapping, are passed through as finite numbers:
    reader_confidence is mean character log probability; inter_reader_agreement
    is reader-to-reader CER (zero means agreement). Neither uses a text layer.
    """
    values = asdict(diagnostics) if isinstance(diagnostics, GeometryDiagnostics) else dict(diagnostics)
    geometry = dict(values.get('diagnostics', values))
    source_box = geometry.get('source_box', values.get('source_box'))
    curve_data = geometry.get('baseline_curve', values.get('curve'))
    left = geometry.get('strip_x_origin')
    ascent = geometry.get('strip_baseline_px', values.get('ascent'))
    if source_box is None or curve_data is None or left is None or ascent is None:
        raise ValueError('crop_quality requires source_box, baseline_curve, strip_x_origin and strip_baseline_px')
    source = _box(source_box)
    if original_crop.size != (source[2]-source[0], source[3]-source[1]):
        raise ValueError('original crop size must match source_box at the same pixel resolution')
    curve = curve_data if isinstance(curve_data, BaselineCurve) else BaselineCurve(**curve_data)
    height = float(geometry.get('line_band_height_px', geometry['x_height_px']))
    if height <= 0 or not math.isfinite(height):
        raise ValueError('x_height_px must be finite and positive')
    rectified = geometry.get('rectified', True)
    shared_left = max(source[0], left)
    shared_right = min(source[2], left+refined_crop.width)
    if shared_right <= shared_left:
        raise ValueError('crops must share a horizontal pixel range')
    columns = np.arange(shared_left, shared_right, dtype=float)
    baseline = _values(curve, columns)[None, :]
    band_curve_data = geometry.get('line_band_curve', curve_data)
    band_curve = band_curve_data if isinstance(band_curve_data, BaselineCurve) else BaselineCurve(**band_curve_data)
    band_baseline = _values(band_curve, columns)[None, :]
    rows = np.arange(source[1], source[3])[:, None]
    band = ((rows >= band_baseline-BAND_ASCENT_RATIO*height)
            & (rows <= band_baseline+BAND_DESCENT_RATIO*height))
    zones = {'diacritic': band & (rows < band_baseline-height),
             'body': band & (rows >= band_baseline-height), 'neighbour': ~band}
    original = np.asarray(original_crop.convert('L'))[:, shared_left-source[0]:shared_right-source[0]]
    output = np.asarray(refined_crop.convert('L'))
    output_rows = rows-np.rint(baseline).astype(int)+ascent if rectified else rows-source[1]
    output_columns = np.arange(shared_left-left, shared_right-left)[None, :]
    valid = (output_rows >= 0) & (output_rows < refined_crop.height)
    mapped = output[np.clip(output_rows, 0, refined_crop.height-1), output_columns]
    old_dark = original < INK_MASS_MAX_GRAY
    new_dark = (mapped < INK_MASS_MAX_GRAY) & valid
    counts = {name: {'original': int((old_dark & zone).sum()),
                     'refined': int((new_dark & zone).sum()),
                     'removed': int((old_dark & ~new_dark & zone).sum())}
              for name, zone in zones.items()}
    result: dict[str, Any] = {
        f'{zone}_ink_retained': counts[zone]['refined']/counts[zone]['original']
        if counts[zone]['original'] else 1.0 for zone in ('diacritic', 'body')}
    neighbour = counts['neighbour']
    # No neighbour evidence is unavailable, not perfect removal.
    result['neighbour_ink_removed'] = (neighbour['removed']/neighbour['original']
                                       if neighbour['original'] else None)
    result.update(clipped_left=bool(np.any(output[:, 0] < INK_MASS_MAX_GRAY)),
                  clipped_right=bool(np.any(output[:, -1] < INK_MASS_MAX_GRAY)),
                  ink_counts=counts, shared_x_range=[shared_left, shared_right],
                  dark_pixel_threshold=INK_MASS_MAX_GRAY)
    shared_output = output[:, shared_left-left:shared_right-left]
    old_contrast, old_blur = _appearance(original)
    new_contrast, new_blur = _appearance(shared_output)
    result.update(contrast_original=old_contrast, contrast_refined=new_contrast,
                  contrast_delta=new_contrast-old_contrast,
                  blur_original=old_blur, blur_refined=new_blur, blur_delta=new_blur-old_blur,
                  blur_measure='Laplacian variance; higher means sharper; affected by ink density/padding')
    expected = (float((band_baseline-np.rint(baseline)+ascent).mean()) if rectified
                else float(band_baseline.mean())-source[1])
    result['curl_residual_px'] = _residual_curl(Image.fromarray(shared_output), expected, len(columns))
    for hook in ('reader_confidence', 'inter_reader_agreement'):
        value = values.get(hook, geometry.get(hook))
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                                  or not math.isfinite(value)):
            raise ValueError(f'{hook} must be a finite number or None')
        result[hook] = value
    return result


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
                      pad: int = DEFAULT_PAD, policy: GeometryPolicy = 'v3') -> list[LineCrop]:
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
        first = refine_line(pdf_page_image, candidate.box, pad=pad, policy=policy)
        boxes = split_multiline(candidate.box, first.kept_components+first.dropped_components)
        for split_index, box in enumerate(boxes):
            line = first if len(boxes) == 1 else refine_line(pdf_page_image, box, pad=pad, policy=policy)
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

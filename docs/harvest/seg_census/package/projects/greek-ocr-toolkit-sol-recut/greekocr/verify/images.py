"""CPU crop diagnostics and spatial readability proxies (no OCR, no reference text)."""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from functools import lru_cache
import io
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.signal import find_peaks
from greekocr.real.geometry import _components, _height, _fit, _values, _ink

Crop = Image.Image | np.ndarray | str | Path
__all__ = ['ImageChecks', 'Profile', 'image_checks', 'readability_profile', 'render_overlay']

PROFILE_FIELDS = ('visible_fraction', 'clip_top', 'clip_bottom', 'baseline_offset',
                  'local_contrast', 'blur', 'obstruction', 'neighbour')
ANOMALY_FIELDS = ('skew_abs', 'trail_abs', 'clip_fraction', 'laplacian_log',
                  'stroke_cv', 'contrast', 'obstruction', 'crowding', 'ink_coverage')


@dataclass(frozen=True)
class ImageChecks:
    """Line summaries. Units, sign conventions and provisional thresholds: docs/VERIFY.md."""
    width_px: int
    height_px: int
    skew_deg: float
    trail: str
    trail_amplitude_px: float
    trail_signed_px: float
    edge_touch: dict[str, bool]
    edge_ink_fraction: dict[str, float]
    clarity: dict[str, float]
    obstruction_score: float
    bleed_through_proxy: float
    crowding: float
    residual_anomaly_score: float | None
    ink_coverage: float
    glyph_height_px: float
    baseline_count: int
    clipped_fraction: float
    unreadable_fraction: float
    empty: bool
    analysis_scale: float = 1.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Profile:
    """Per-column functions; half-open segments and 16x64 quality, 1=good/0=bad.

    Arrays have length width, bins always 64; white spaces with no glyph evidence are
    neutral (visible_fraction=1), except an entirely empty crop (all quality=0).
    visible_fraction estimates vertical glyph support relative to complete local
    letters; it cannot prove completeness of unseen glyphs or removed whole words.
    """
    width_px: int
    height_px: int
    visible_fraction: np.ndarray
    clip_top: np.ndarray
    clip_bottom: np.ndarray
    baseline_offset: np.ndarray
    local_contrast: np.ndarray
    blur: np.ndarray
    obstruction: np.ndarray
    neighbour: np.ndarray
    readability: np.ndarray
    bins: dict[str, np.ndarray]
    quality_map: np.ndarray
    segments: tuple[dict, ...]
    expected_band: np.ndarray
    summaries: ImageChecks
    threshold: float = .55
    spatial_features: dict[str, np.ndarray] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        def convert(value):
            if isinstance(value, np.ndarray):
                return value.tolist()
            if isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}
            if isinstance(value, (tuple, list)):
                return [convert(v) for v in value]
            return value
        return convert(asdict(self))


def _load(crop: Crop) -> Image.Image:
    if isinstance(crop, (str, Path)):
        with Image.open(crop) as image:
            image.load()
            return _load(image)
    if isinstance(crop, np.ndarray):
        a = np.asarray(crop)
        if a.size == 0 or a.ndim not in (2, 3) or not np.isfinite(a).all():
            raise ValueError('crop must be a finite, nonempty raster')
        if a.dtype == np.bool_:
            a = a.astype(np.uint8)*255
        elif a.dtype != np.uint8:
            if a.min() < 0 or a.max() > 1:
                raise ValueError('floating crop values must be normalized to [0,1]')
            a = np.rint(a*255).astype(np.uint8)
        crop = Image.fromarray(a)
    if not isinstance(crop, Image.Image) or min(crop.size) < 1:
        raise ValueError('crop must be an image, path or raster')
    if 'A' in crop.getbands() or crop.mode == 'P' and 'transparency' in crop.info:
        rgba = crop.convert('RGBA')
        crop = Image.alpha_composite(Image.new('RGBA', rgba.size, 'white'), rgba)
    return crop.convert('L')


def _bins(values: np.ndarray, count: int = 64) -> np.ndarray:
    # Area-weighted downsampling works even for widths <64; doesn't drop edge pixels.
    w = values.shape[-1]
    bounds = np.linspace(0, w, count+1)
    cumulative = np.r_[0., np.cumsum(values)]
    sampled = np.interp(bounds, np.arange(w+1), cumulative)
    return np.diff(sampled)/(w/count)


def _segments(readability: np.ndarray, threshold: float) -> tuple[dict, ...]:
    bad = readability < threshold
    labels, n = ndi.label(bad)
    regions = ndi.find_objects(labels)
    return tuple({'x0': r[0].start, 'x1': r[0].stop,
                  'intensity': float(1-readability[r[0]].mean()),
                  'min_readability': float(readability[r[0]].min())}
                 for r in regions if r is not None)


@lru_cache(maxsize=1)
def _reference() -> dict | None:
    path = Path(__file__).with_name('sample_distribution.json')
    return json.loads(path.read_text()) if path.exists() else None


def feature_vector(checks: ImageChecks) -> np.ndarray:
    return np.array([abs(checks.skew_deg), abs(checks.trail_signed_px)/max(1, checks.glyph_height_px),
                     checks.clipped_fraction, math.log1p(checks.clarity['laplacian_variance']),
                     checks.clarity['stroke_width_cv'], checks.clarity['contrast_p10_p90'],
                     checks.obstruction_score, checks.crowding, checks.ink_coverage])


def _local_anomaly(spatial: dict, values: dict, coverage: np.ndarray,
                   glyph_height: float) -> np.ndarray | None:
    reference = _reference()
    if reference is None:
        return None
    win = max(3, int(glyph_height*1.5)|1)
    local_clip = ndi.uniform_filter1d(np.maximum(values['clip_top'],values['clip_bottom']),win)
    vector = np.array([np.abs(spatial['skew_deg']), np.abs(values['baseline_offset'])/max(1,glyph_height),
                       local_clip, np.log1p(spatial['laplacian_variance']), spatial['stroke_width_cv'],
                       values['local_contrast'], values['obstruction'], values['neighbour'],
                       ndi.uniform_filter1d(coverage,win)])
    return np.sqrt(np.mean(((vector-np.array(reference['center'])[:,None])/
                            np.array(reference['scale'])[:,None])**2,axis=0))


def _profile_native(crop, *, threshold: float = .55) -> Profile:
    """Measure local ink geometry once; mean runtime target <20 ms for fixture strips.

    Uses geometry's identical contrast-gated 8-connected components, glyph-height
    estimate and robust baseline curve. Omits geometry's expensive page RANSAC.
    """
    if not 0 < threshold < 1:
        raise ValueError('threshold must be in (0,1)')
    image = _load(crop)
    gray = np.asarray(image, dtype=np.float32)
    h, w = gray.shape
    labels, components = _components(image, (0, 0, w, h))
    mask = labels > 0
    # Suppress sub-3px texture exactly as geometry's component noise floor.
    areas = np.bincount(labels.ravel())
    significant = areas >= 3
    significant[0] = False
    mask = significant[labels]
    glyph_height = _height(components)
    win = max(3, int(round(glyph_height*1.5)) | 1)
    smooth = lambda a: ndi.uniform_filter1d(np.asarray(a, dtype=float), win, mode='nearest')
    ink_columns = mask.any(axis=0)
    body = [c for c in components if c.area >= max(5, .04*glyph_height**2)
            and c.box[3]-c.box[1] >= .35*glyph_height
            and c.box[2]-c.box[0] < 5*glyph_height
            and c.box[3]-c.box[1] < 2.5*glyph_height]
    complete = [c for c in body if c.box[1] > 0 and c.box[3] < h
                and c.box[3]-c.box[1] >= .6*glyph_height]
    if len(complete) >= 4:
        # Clipped fragments otherwise bias geometry's height estimate downward.
        # Tall complete glyphs within this same crop supply the missing body band.
        glyph_height = max(glyph_height, float(np.quantile(
            [c.box[3]-c.box[1] for c in complete], .75)))
    # Estimate from sufficiently tall, complete glyphs where available; fallback is
    # identifiable crop evidence rather than an assumed font or supplied OCR text.
    support = complete if len(complete) >= 4 else body
    row_profile = ndi.gaussian_filter1d(mask.sum(axis=1).astype(float), max(1, glyph_height*.10))
    peaks, props = find_peaks(row_profile, distance=max(2, int(glyph_height*.65)),
                             prominence=max(1, float(row_profile.max())*.22))
    baseline_count = max(1, len(peaks)) if body else 0
    if support:
        centers = np.array([c.center_y for c in support])
        # Select the dominant band closest to the crop centre; avoid a neighbour
        # moving the baseline. The retained ink in other bands still enters crowding.
        candidates = sorted(support, key=lambda c: abs(c.center_y-h/2))
        anchor = candidates[0].center_y
        selected = [c for c in support if abs(c.center_y-anchor) < glyph_height*.85]
        curve = _fit(np.array([c.center_x for c in selected]),
                     np.array([float(c.box[3]-1) for c in selected]))
        baseline = _values(curve, np.arange(w, dtype=float))
        # Restrict extrapolation to physical, observable crop heights.
        baseline = np.clip(baseline, -glyph_height, h+glyph_height)
    else:
        baseline = np.full(w, h/2)
    band_top = baseline-glyph_height+1
    band_bottom = baseline+1
    expected_band = np.stack([band_top, band_bottom])
    offset = baseline - np.median(baseline)
    q = max(1, int(math.ceil(.15*w)))
    signed = float(np.median(baseline[-q:])-np.median(baseline[:q]))
    slope = signed/max(1, w-q)
    skew = math.degrees(math.atan(slope))

    # Assign each glyph footprint its vertical-support fraction. Detached accents
    # do not masquerade as full bodies. Smooth within about one glyph neighbourhood
    # and bridge ordinary inter-letter gaps without labelling whitespace unreadable.
    span = np.zeros(w)
    evidence = np.zeros(w)
    clip_top = mask[0].astype(float)
    clip_bottom = mask[-1].astype(float)
    # Short clipped fragments still count as glyph support. They are deliberately
    # excluded from baseline fitting above, but must not become neutral whitespace.
    visible_parts = [c for c in components if c.area >= 5
                     and c.box[2]-c.box[0] < 5*glyph_height
                     and c.box[3]-c.box[1] < 2.5*glyph_height
                     and band_top[min(w-1, int(c.center_x))]+.10*glyph_height <= c.center_y
                     <= band_bottom[min(w-1, int(c.center_x))]+.35*glyph_height]
    for c in visible_parts:
        x0, y0, x1, y1 = c.box
        ratio = min(1., (y1-y0)/glyph_height)
        span[x0:x1] = np.maximum(span[x0:x1], ratio)
        evidence[x0:x1] = 1
    expanded = ndi.maximum_filter1d(evidence, win, mode='nearest') > 0
    denominator = smooth(evidence)
    visible = np.divide(smooth(span), denominator, out=np.ones(w), where=denominator>0)
    visible[~expanded] = 1
    # At edges, completeness cannot exceed the supported fraction of the inferred
    # body band, even if a connected fragment happens to have normal component size.
    vertical_room = np.clip(np.minimum(h, band_bottom)-np.maximum(0, band_top), 0, glyph_height)/glyph_height
    clipping = np.maximum(smooth(clip_top), smooth(clip_bottom))
    visible = np.where(clipping > .06, np.minimum(visible, vertical_room), visible)

    lap = ndi.laplace(gray)
    lapvar = float(np.var(lap))
    paper = np.asarray(image.filter(__import__('PIL.ImageFilter', fromlist=['BoxBlur']).BoxBlur(15)), dtype=float)
    ink_strength = np.maximum(paper-gray, 0)
    column_ink = mask.sum(axis=0).astype(float)
    local_contrast = np.divide(smooth((ink_strength*mask).sum(axis=0)), smooth(column_ink),
                               out=np.zeros(w), where=smooth(column_ink)>0) / 255
    local_energy = np.divide(smooth((lap*lap*mask).sum(axis=0)), smooth(column_ink),
                             out=np.zeros(w), where=smooth(column_ink)>0)
    # Laplacian energy normalized by local ink contrast; resolution-dependent proxy.
    sharpness = np.sqrt(local_energy)/np.maximum(local_contrast*255, 1)
    blur = np.clip(1-sharpness/1.2, 0, 1)
    blur[~expanded] = 0
    distance = ndi.distance_transform_edt(mask)
    ridge = mask & (distance >= ndi.maximum_filter(distance, size=3))
    widths = 2*distance[ridge]
    stroke_width = float(np.median(widths)) if widths.size else 0.
    stroke_cv = float(np.std(widths)/max(1, np.mean(widths))) if widths.size else 0.
    ridge_count = smooth(ridge.sum(axis=0))
    stroke_by_x = np.divide(smooth((2*distance*ridge).sum(axis=0)), ridge_count,
                            out=np.zeros(w), where=ridge_count>0)
    width_sq = np.divide(smooth((4*distance**2*ridge).sum(axis=0)), ridge_count,
                         out=np.zeros(w), where=ridge_count>0)
    stroke_cv_by_x = np.sqrt(np.maximum(width_sq-stroke_by_x**2,0))/np.maximum(stroke_by_x,1)
    p10, p90 = np.percentile(gray, [10, 90])

    foreign_ids = []
    for c in components:
        x0, y0, x1, y1 = c.box
        cw, ch = x1-x0, y1-y0
        solidity = c.area/max(1, cw*ch)
        long_rule = (cw > 5*glyph_height and ch < .35*glyph_height) or (ch > 2.5*glyph_height and cw < .4*glyph_height)
        giant_blob = c.area > 4*glyph_height**2 and (solidity > .65 or cw/ch > 6 or ch/cw > 4)
        irregular = c.area > 2*glyph_height**2 and solidity < .12
        if long_rule or giant_blob or irregular:
            foreign_ids.append(c.id)
    foreign_lookup = np.zeros(len(areas), dtype=bool)
    foreign_lookup[foreign_ids] = True
    foreign = foreign_lookup[labels]
    # Faint ink spatially aligned to horizontally mirrored strong ink is only a
    # bleed-through proxy. Dilating strong strokes prevents counting antialiasing.
    strong_halo = ndi.maximum_filter(mask, size=5)
    faint = (gray > 150) & (ink_strength >= 4) & (ink_strength < 18) & ~strong_halo
    mirrored = ndi.maximum_filter(mask[:, ::-1], size=3)
    bleed = faint & mirrored
    bleed_proxy = float(bleed.sum()/max(1, mask.sum()))
    foreign_density = (foreign | bleed).sum(axis=0)/max(1, glyph_height)
    obstruction = np.clip(smooth(foreign_density), 0, 1)
    margin = max(1, int(math.ceil(.2*h)))
    # Count out-of-band margin ink as neighbour evidence, not intended glyphs that
    # rise/fall toward a border. Keep the raw margin fraction as a separate summary.
    yy = np.arange(h)[:, None]
    margin_mask = (yy < margin) | (yy >= h-margin)
    outside = (yy < band_top[None, :]-glyph_height*.25) | (yy >= band_bottom[None, :]+glyph_height*.25)
    neighbour = np.clip(smooth((mask & margin_mask & outside).sum(axis=0)/(2*margin)), 0, 1)
    crowding = float(neighbour.mean())

    # Clip alone is an observation, not a proof of unreadability. Lost vertical
    # support drives quality strongly; contrast, blur and foreign ink add penalties.
    quality = np.clip(visible - .22*blur - .30*np.clip((.12-local_contrast)/.12, 0, 1)*expanded
                      - .65*obstruction - .55*neighbour, 0, 1)
    empty = not mask.any()
    if empty:
        visible[:] = 0
        quality[:] = 0
    bins = {name: _bins(value) for name, value in {
        'visible_fraction': visible, 'clip_top': clip_top, 'clip_bottom': clip_bottom,
        'baseline_offset': offset, 'local_contrast': local_contrast, 'blur': blur,
        'obstruction': obstruction, 'neighbour': neighbour, 'readability': quality}.items()}
    # Row-dependent intensity: put clip/foreign/neighbour deficits where observed;
    # missing body support spans the local expected glyph band.
    in_band = (yy >= band_top[None, :]) & (yy < band_bottom[None, :])
    q2d = 1-(1-quality[None, :])*in_band
    q2d = np.minimum(q2d, 1-.8*foreign)
    q2d[0] = np.minimum(q2d[0], 1-.7*clip_top)
    q2d[-1] = np.minimum(q2d[-1], 1-.7*clip_bottom)
    if empty:
        q2d[:] = 0
    quality_map = np.asarray(Image.fromarray(q2d.astype(np.float32), mode='F').resize((64, 16), Image.Resampling.BOX))
    edge_fraction = dict(top=float(mask[0].mean()), bottom=float(mask[-1].mean()),
                         left=float(mask[:, 0].mean()), right=float(mask[:, -1].mean()))
    checks = ImageChecks(w, h, skew, 'down' if signed > 2 else 'up' if signed < -2 else 'flat',
                         abs(signed), signed, {k: v>0 for k,v in edge_fraction.items()}, edge_fraction,
                         dict(laplacian_variance=lapvar, stroke_width_px=stroke_width,
                              stroke_width_cv=stroke_cv, contrast_p10_p90=float((p90-p10)/255),
                              local_contrast_p10=float(np.percentile(local_contrast[expanded], 10)) if expanded.any() else 0.,
                              local_contrast_p90=float(np.percentile(local_contrast[expanded], 90)) if expanded.any() else 0.,
                              blur_mean=float(blur[expanded].mean()) if expanded.any() else 1.),
                         float(obstruction.mean()), bleed_proxy, crowding, None,
                         float(mask.mean()), glyph_height, baseline_count,
                         float((clipping > .06).mean()), float((quality < threshold).mean()), empty)
    reference = _reference()
    if reference:
        v = feature_vector(checks)
        anomaly = float(np.sqrt(np.mean(((v-np.array(reference['center']))/np.array(reference['scale']))**2)))
        checks = ImageChecks(**(checks.to_dict() | {'residual_anomaly_score': anomaly}))
    spatial = {'stroke_width_px': stroke_by_x, 'stroke_width_cv': stroke_cv_by_x,
               'laplacian_variance': np.maximum(smooth((lap*lap).mean(axis=0))-
                                               smooth(lap.mean(axis=0))**2,0),
               'skew_deg': np.degrees(np.arctan(np.gradient(baseline))) if w>1 else np.zeros(w),
               'bleed_through_proxy': smooth(bleed.sum(axis=0)/max(1,glyph_height)),
               'cut_left': np.r_[float(mask[:,0].mean()),np.zeros(w-1)],
               'cut_right': np.r_[np.zeros(w-1),float(mask[:,-1].mean())]}
    local_anomaly = _local_anomaly(spatial, dict(clip_top=clip_top,clip_bottom=clip_bottom,
        baseline_offset=offset,local_contrast=local_contrast,obstruction=obstruction,neighbour=neighbour),
        mask.mean(axis=0),glyph_height)
    if local_anomaly is not None:
        spatial['residual_anomaly_score'] = local_anomaly
    bins.update({name:_bins(value) for name,value in spatial.items()})
    return Profile(w, h, visible, clip_top, clip_bottom, offset, local_contrast, blur,
                   obstruction, neighbour, quality, bins, quality_map,
                   _segments(quality, threshold), expected_band, checks, threshold, spatial)


def readability_profile(crop: Crop, *, threshold: float = .55) -> Profile:
    """Bounded analysis grid, native border checks, original-coordinate functions.

    Crops over 64,000 pixels are uniformly reduced with BOX sampling. Scalar
    lengths/baseline offsets are restored to original pixels; the Laplacian and
    edge ink are measured at native resolution. analysis_scale exposes reduction.
    This bounds CPU cost on the 3040x193 sample without concealing border clipping.
    """
    image = _load(crop)
    w, h = image.size
    scale = min(1., math.sqrt(64_000/(w*h)))
    if scale == 1:
        return _profile_native(image, threshold=threshold)
    aw, ah = max(1, int(w*scale)), max(1, int(h*scale))
    # Integer rounding creates slightly different axes; use their exact scales.
    sx, sy = aw/w, ah/h
    native = _profile_native(image.resize((aw, ah), Image.Resampling.BOX), threshold=threshold)
    positions = (np.arange(w)+.5)*sx-.5
    expand = lambda values: np.interp(positions, np.arange(aw), values)
    values = {name: expand(getattr(native, name)) for name in PROFILE_FIELDS}
    values['baseline_offset'] /= sy
    mask = _ink(image)
    values['clip_top'] = mask[0].astype(float)
    values['clip_bottom'] = mask[-1].astype(float)
    readability = expand(native.readability)
    edge_fraction = dict(top=float(mask[0].mean()), bottom=float(mask[-1].mean()),
                         left=float(mask[:, 0].mean()), right=float(mask[:, -1].mean()))
    q = max(1, math.ceil(.15*w))
    signed = float(np.median(values['baseline_offset'][-q:])-np.median(values['baseline_offset'][:q]))
    glyph_height = native.summaries.glyph_height_px/sy
    clip = ndi.uniform_filter1d(np.maximum(values['clip_top'], values['clip_bottom']),
                               max(3, int(glyph_height*1.5)|1), mode='nearest')
    lap = ndi.laplace(np.asarray(image,dtype=np.float32))
    clarity = native.summaries.clarity | {
        'laplacian_variance': float(np.var(lap)),
        'stroke_width_px': native.summaries.clarity['stroke_width_px']/sy}
    checks = ImageChecks(**(native.summaries.to_dict() | {
        'width_px': w, 'height_px': h, 'skew_deg': math.degrees(math.atan(signed/max(1,w-q))),
        'trail_signed_px': signed, 'trail_amplitude_px': abs(signed),
        'trail': 'down' if signed>2 else 'up' if signed < -2 else 'flat',
        'edge_touch': {k:v>0 for k,v in edge_fraction.items()}, 'edge_ink_fraction': edge_fraction,
        'clarity': clarity, 'glyph_height_px': glyph_height, 'ink_coverage': float(mask.mean()),
        'clipped_fraction': float((clip>.06).mean()),
        'unreadable_fraction': float((readability<threshold).mean()), 'analysis_scale': min(sx,sy)}))
    reference = _reference()
    if reference:
        anomaly = float(np.sqrt(np.mean(((feature_vector(checks)-np.array(reference['center']))/
                                        np.array(reference['scale']))**2)))
        checks = ImageChecks(**(checks.to_dict() | {'residual_anomaly_score': anomaly}))
    bins = {name:_bins(value) for name,value in values.items()}
    bins['readability'] = _bins(readability)
    spatial = {name:expand(value) for name,value in native.spatial_features.items()}
    spatial['stroke_width_px'] /= sy
    spatial['skew_deg'] = np.degrees(np.arctan(np.gradient(values['baseline_offset']))) if w>1 else np.zeros(w)
    spatial['cut_left'] = np.r_[edge_fraction['left'],np.zeros(w-1)]
    spatial['cut_right'] = np.r_[np.zeros(w-1),edge_fraction['right']]
    win = max(3,int(glyph_height*1.5)|1)
    spatial['laplacian_variance'] = np.maximum(
        ndi.uniform_filter1d((lap*lap).mean(axis=0),win)-ndi.uniform_filter1d(lap.mean(axis=0),win)**2,0)
    local_anomaly = _local_anomaly(spatial, values, mask.mean(axis=0),glyph_height)
    if local_anomaly is not None:
        spatial['residual_anomaly_score'] = local_anomaly
    bins.update({name:_bins(value) for name,value in spatial.items()})
    qmap = native.quality_map.copy()
    qmap[0] = np.minimum(qmap[0], 1-.7*bins['clip_top'])
    qmap[-1] = np.minimum(qmap[-1], 1-.7*bins['clip_bottom'])
    band = np.stack([expand(row)/sy for row in native.expected_band])
    return Profile(w, h, **values, readability=readability, bins=bins, quality_map=qmap,
                   segments=_segments(readability, threshold), expected_band=band,
                   summaries=checks, threshold=threshold, spatial_features=spatial)


def image_checks(crop: Crop) -> ImageChecks:
    """Return the scalar summaries of readability_profile, using the same analysis."""
    return readability_profile(crop).summaries


def render_overlay(crop: Crop, profile: Profile) -> bytes:
    """Return PNG bytes: raster, translucent 2-D defects and half-open red segments."""
    image = _load(crop).convert('RGB')
    if image.size != (profile.width_px, profile.height_px):
        raise ValueError('profile dimensions do not match crop')
    defect = (1-profile.quality_map).clip(0, 1)
    rgba = np.zeros((16, 64, 4), dtype=np.uint8)
    rgba[:, :, 0] = 255
    rgba[:, :, 1] = 45
    rgba[:, :, 3] = np.rint(defect*130).astype(np.uint8)
    heat = Image.fromarray(rgba).resize(image.size, Image.Resampling.NEAREST)
    overlay = Image.alpha_composite(image.convert('RGBA'), heat)
    draw = ImageDraw.Draw(overlay)
    for segment in profile.segments:
        draw.rectangle((segment['x0'], 0, segment['x1']-1, image.height-1), outline=(220, 0, 0, 255), width=1)
    stream = io.BytesIO()
    overlay.convert('RGB').save(stream, format='PNG')
    return stream.getvalue()

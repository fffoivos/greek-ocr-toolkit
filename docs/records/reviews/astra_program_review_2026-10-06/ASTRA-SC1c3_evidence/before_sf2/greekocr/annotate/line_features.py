"""Deterministic pixel and Unicode measurements; no OCR or model imports."""
from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
import math
import re
from typing import Any, Mapping, Iterable
import unicodedata as ud

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from greekocr._vendor.bench.o4b_common import tag
from greekocr.types import PathLike

__all__ = ['LineFeatures', 'line_features', 'load_lexicon']

POLY_MARKS = frozenset('\u0313\u0314\u0342\u0345\u0300\u0304\u0306')


class _Lexicon(frozenset):
    """Normalization marker so streaming annotation does not refold the whole lexicon per line."""


@dataclass(frozen=True)
class LineFeatures:
    """JSON-ready measurements; definitions and missing-value rules in LINE_METADATA.md."""
    height_px: int
    width_px: int
    aspect: float
    ink_coverage: float
    background_level: float
    background_rgb: tuple[float, float, float] | None
    background_cast: tuple[float, float, float] | None
    contrast: float | None
    local_contrast_p10: float | None
    local_contrast_p90: float | None
    stroke_width_px: float | None
    xheight_px: float | None
    capheight_ratio: float | None
    polarity: str
    blur: float
    noise: int
    curl_px: float | None
    skew_deg: float | None
    clipped_edges: tuple[str, ...] | None
    n_chars: int | None
    n_words: int | None
    n_letters: int | None
    script_class: str | None
    polytonic_mark_density: float | None
    digit_ratio: float | None
    punct_ratio: float | None
    upper_ratio: float | None
    language_guess: str | None
    lexicon_validity: float | None
    bg_type: str
    font: str | None = None
    font_style: str | None = None
    severity: int | None = None
    applied_ops: tuple[str, ...] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return only built-in finite values, suitable for json.dumps(allow_nan=False)."""
        return asdict(self)


def _image(image: Image.Image | np.ndarray | PathLike) -> tuple[np.ndarray, np.ndarray | None]:
    if isinstance(image, (str, Path)):
        with Image.open(image) as opened:
            opened.load()
            return _image(opened)
    if isinstance(image, Image.Image):
        if 'A' in image.getbands() or image.mode == 'P' and 'transparency' in image.info:
            rgba = image.convert('RGBA')
            image = Image.alpha_composite(Image.new('RGBA', rgba.size, 'white'), rgba).convert('RGB')
        elif image.mode not in ('L', 'RGB', 'F', 'I', 'I;16', '1'):
            image = image.convert('RGB')
        image = np.asarray(image)
    values = np.asarray(image)
    if values.ndim not in (2, 3) or 0 in values.shape or values.ndim == 3 and values.shape[2] not in (3, 4):
        raise ValueError('image must be a nonempty grayscale, RGB or RGBA raster')
    if values.dtype == np.uint8:
        values = values.astype(float) / 255.0
    elif values.dtype == np.bool_:
        values = values.astype(float)
    else:
        values = values.astype(float)
        if not np.isfinite(values).all() or values.min() < 0 or values.max() > 1:
            raise ValueError('non-uint8 image values must be finite and normalized to [0, 1]')
    if values.ndim == 3:
        rgb = values[:, :, :3]
        if values.shape[2] == 4:
            rgb = rgb * values[:, :, 3:] + 1 - values[:, :, 3:]
        return rgb @ np.array([.299, .587, .114]), rgb
    return values, None


def _otsu(gray: np.ndarray) -> float:
    hist, edges = np.histogram(gray, bins=256, range=(0, 1))
    levels = (edges[:-1] + edges[1:]) / 2
    weight = np.cumsum(hist).astype(float)
    mean = np.cumsum(hist * levels)
    denominator = weight * (weight[-1] - weight)
    score = np.divide((mean[-1] * weight - mean * weight[-1]) ** 2, denominator,
                      out=np.zeros_like(weight), where=denominator > 0)
    return float(edges[int(np.argmax(score)) + 1])


def _pixels(image: Image.Image | np.ndarray | PathLike) -> tuple[np.ndarray, np.ndarray | None, np.ndarray, np.ndarray, str]:
    gray, rgb = _image(image)
    border = np.concatenate((gray[0], gray[-1], gray[:, 0], gray[:, -1]))
    threshold = _otsu(gray)
    light = float(np.median(border)) < threshold
    polarity = 'light_on_dark' if light else 'dark_on_light'
    work = 1 - gray if light else gray
    # Closing estimates local paper without a full page. Contrast gating avoids
    # labeling an unprinted smooth gradient as a half-solid line.
    paper = ndi.grey_closing(work, size=(min(31, gray.shape[0]), min(31, gray.shape[1])))
    local = np.maximum(paper - work, 0)
    mask = (work < _otsu(work)) & (local >= 2 / 255)
    curvature = max((float(np.max(np.abs(np.diff(work, n=2, axis=axis))))
                     for axis in (0, 1) if work.shape[axis] >= 3), default=0.)
    # Closing's reflected boundary can produce a false dark edge on a smooth
    # ramp. An affine/quantized-affine empty strip has no supported glyph edge.
    if float(np.ptp(work)) < 2 / 255 or min(work.shape) >= 3 and curvature <= 1 / 255 + 1e-12:
        mask[:] = False
    return gray, rgb, mask, local, polarity


def _mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Mapping):
        return dict(value)
    raise TypeError('geometry must be a geometry dataclass or mapping')


def _geometry(geometry: Any) -> tuple[float | None, float | None, tuple[str, ...] | None]:
    outer = _mapping(geometry)
    diag = _mapping(outer.get('diagnostics', outer))
    curl = diag.get('curl_px', diag.get('curl_amplitude_px'))
    skew = diag.get('skew_deg')
    curve = _mapping(outer.get('curve', diag.get('baseline_curve')))
    if skew is None and curve and curve.get('x_scale', 0) > 0:
        # Slope at the curve's x_origin; same page-space definition as T2.
        skew = math.degrees(math.atan(curve['c1'] / curve['x_scale']))
    edges = diag.get('clipped_edges', diag.get('source_boundary_ink'))
    if isinstance(edges, str):
        edges = [edges]
    edges = tuple(sorted(set(edges))) if edges is not None else None
    for name, number in [('curl', curl), ('skew', skew)]:
        if number is not None and (isinstance(number, bool) or not math.isfinite(float(number))):
            raise ValueError(f'{name} diagnostic must be finite')
    return (float(curl) if curl is not None else None,
            float(skew) if skew is not None else None, edges)


def _word_key(word: str) -> str:
    return ''.join(c for c in ud.normalize('NFD', word.casefold()) if not ud.category(c).startswith('M')).replace('ς', 'σ')


def _words(text: str) -> list[str]:
    return re.findall(r'[^\W\d_]+', ud.normalize('NFC', text), flags=re.UNICODE)


def load_lexicon(lexicon: PathLike | Iterable[str]) -> frozenset[str]:
    """Read UTF-8 words (one per line; # comments), folding accents, case and final sigma."""
    if isinstance(lexicon, _Lexicon):
        return lexicon
    lines = Path(lexicon).read_text(encoding='utf-8-sig').splitlines() if isinstance(lexicon, (str, Path)) else lexicon
    return _Lexicon(_word_key(word.strip()) for word in lines if word.strip() and not word.lstrip().startswith('#'))


def _greek(char: str) -> bool:
    return char.isalpha() and ('GREEK' in ud.name(char, ''))


def _text(text: str | None, lexicon: frozenset[str] | None) -> dict[str, Any]:
    names = ('n_chars', 'n_words', 'n_letters', 'script_class', 'polytonic_mark_density', 'digit_ratio',
             'punct_ratio', 'upper_ratio', 'language_guess', 'lexicon_validity')
    if text is None:
        return dict.fromkeys(names)
    if not isinstance(text, str):
        raise TypeError('text must be str or None')
    nfc = ud.normalize('NFC', text)
    nfd = ud.normalize('NFD', text)
    visible = [c for c in nfc if not c.isspace() and not ud.category(c).startswith('M')]
    letters = [c for c in nfc if c.isalpha()]
    greek_letters = [c for c in nfd if _greek(c)]
    poly = 0
    previous = ''
    for c in nfd:
        if ud.category(c).startswith('M'):
            poly += int(_greek(previous) and c in POLY_MARKS)
        else:
            previous = c
    words = _words(nfc)
    language = 'other'
    if greek_letters and len(greek_letters) >= .5 * len(letters):
        # Historical modern Greek can also be polytonic; grc is only a rule guess.
        language = 'grc' if poly else 'el'
    elif letters and sum('LATIN' in ud.name(c, '') for c in letters) >= .8 * len(letters):
        keys = {_word_key(w) for w in words}
        french = {'le', 'la', 'les', 'des', 'une', 'dans', 'pour', 'avec', 'est', 'et', 'du', 'sur'}
        english = {'the', 'a', 'an', 'and', 'of', 'in', 'is', 'to', 'for', 'with', 'this', 'that'}
        fr, en = len(keys & french), len(keys & english)
        if fr > en or fr == en == 0 and any(c in nfc.casefold() for c in 'àâçéèêëîïôùûüœ'):
            language = 'fr'
        elif en:
            language = 'en'
    greek_words = [w for w in words if all(_greek(c) for c in ud.normalize('NFD', w) if c.isalpha())]
    validity = None if lexicon is None or not greek_words else sum(_word_key(w) in lexicon for w in greek_words) / len(greek_words)
    return dict(n_chars=len(nfc), n_words=len(words), n_letters=len(letters), script_class=tag(text),
                polytonic_mark_density=poly / len(greek_letters) if greek_letters else 0.0,
                digit_ratio=sum(c.isdigit() for c in visible) / len(visible) if visible else 0.0,
                punct_ratio=sum(ud.category(c).startswith('P') for c in visible) / len(visible) if visible else 0.0,
                upper_ratio=sum(c.isupper() for c in letters) / len(letters) if letters else 0.0,
                language_guess=language, lexicon_validity=validity)


def line_features(image: Image.Image | np.ndarray | PathLike, text: str | None = None, *,
                  geometry: Any = None, lexicon: PathLike | Iterable[str] | None = None) -> LineFeatures:
    """Measure a line at its native scale; optional geometry/Greek lexicon never changes pixels."""
    gray, rgb, mask, local, polarity = _pixels(image)
    height, width = gray.shape
    paper = ~mask
    background = float(np.median(gray[paper])) if paper.any() else float(np.median(gray))
    background_rgb = tuple(float(v) for v in np.median(rgb[paper], axis=0)) if rgb is not None and paper.any() else None
    cast = tuple(v - sum(background_rgb) / 3 for v in background_rgb) if background_rgb is not None else None
    contrast = abs(background - float(np.median(gray[mask]))) if mask.any() and paper.any() else None
    p10, p90 = (float(v) for v in np.quantile(local[mask], [.1, .9])) if mask.any() else (None, None)
    labels, _ = ndi.label(mask, structure=np.ones((3, 3)))
    areas = np.bincount(labels.ravel())[1:]
    noise = int(np.count_nonzero(areas <= 3))
    bodies = []
    for area, slices in zip(areas, ndi.find_objects(labels)):
        if slices is None:
            continue
        ch, cw = slices[0].stop - slices[0].start, slices[1].stop - slices[1].start
        if area >= 4 and cw / ch < 8:
            bodies.append(ch)
    if bodies:
        large = np.quantile(bodies, .9)
        bodies = [h for h in bodies if h >= .4 * large]
    xheight = float(np.median(bodies)) if bodies else None
    capratio = float(np.quantile(bodies, .9) / xheight) if xheight else None
    # Ridge pixels avoid the boundary-heavy bias of the median of all ink pixels.
    distance = ndi.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
    ridge = mask & (distance == ndi.maximum_filter(distance, size=3))
    stroke = float(2 * np.median(distance[ridge])) if ridge.any() else None
    # Background-only planar fit separates smooth illumination from paper texture.
    yy, xx = np.indices(gray.shape)
    step = max(1, int(math.sqrt(gray.size / 4096)))
    sample = paper[::step, ::step]
    coords = np.column_stack((np.ones(sample.sum()), xx[::step, ::step][sample] / width,
                              yy[::step, ::step][sample] / height))
    if len(coords) >= 3:
        values = gray[::step, ::step][sample]
        fit, *_ = np.linalg.lstsq(coords, values, rcond=None)
        residual = float(np.std(values - coords @ fit))
        span = abs(float(fit[1])) + abs(float(fit[2]))
        bg_type = 'textured' if residual > .025 else 'gradient' if span > .04 else 'flat'
    else:
        bg_type = 'flat'
    curl, skew, clipped = _geometry(geometry)
    lex = load_lexicon(lexicon) if lexicon is not None else None
    return LineFeatures(height, width, width / height, float(mask.mean()), background, background_rgb, cast,
                        contrast, p10, p90, stroke, xheight, capratio, polarity,
                        float(np.var(ndi.laplace(gray, mode='reflect'))), noise, curl, skew, clipped,
                        **_text(text, lex), bg_type=bg_type)

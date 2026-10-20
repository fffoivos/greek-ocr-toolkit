"""Small CPU nearest-centroid font classifier; importing it never imports torch."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from greekocr.annotate._records import iter_records, record_image
from greekocr.annotate.line_features import _pixels
from greekocr.types import PathLike

__all__ = ['FontEstimate', 'font_estimate', 'font_style', 'train_font_classifier']

FONT_STYLES = frozenset({'didot_greek_19c', 'modern_serif', 'sans', 'mono', 'script/other'})
MODEL_SCHEMA = 'greekocr-font-centroid-v1'
DESCRIPTOR_SIZE = 260


@dataclass(frozen=True)
class FontEstimate:
    """Predicted factory font id/style, uncalibrated distance/margin and model provenance."""
    font: str | None
    font_style: str | None
    distance: float | None
    margin: float | None
    model_id: str | None
    fixture_only: bool

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable prediction record."""
        return asdict(self)


def font_style(font: str | None, styles: Mapping[str, str] | None = None) -> str | None:
    """Map known factory font ids to shared styles; unidentified/real fonts stay unset."""
    if not font or font.casefold() in ('real', 'unknown', 'none'):
        return None
    if styles is not None and font in styles:
        style = styles[font]
        if style not in FONT_STYLES:
            raise ValueError(f'unknown font style: {style}')
        return style
    name = font.casefold()
    if any(s in name for s in ('didot', 'oldstandard', 'old-standard')):
        return 'didot_greek_19c'
    if any(s in name for s in ('mono', 'courier', 'typewriter')):
        return 'mono'
    if any(s in name for s in ('sans', 'arial', 'helvetica', 'roboto')):
        return 'sans'
    if any(s in name for s in ('serif', 'times', 'georgia', 'cambria', 'baskerville', 'garamond')):
        return 'modern_serif'
    return 'script/other'


def _descriptor(image: Image.Image | np.ndarray | PathLike) -> np.ndarray | None:
    _, _, mask, _, _ = _pixels(image)
    yy, xx = np.nonzero(mask)
    if len(xx) < 4:
        return None
    band = mask[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
    pooled = np.asarray(Image.fromarray(band.astype(np.uint8) * 255).resize((32, 8), Image.Resampling.BOX), dtype=float) / 255
    labels, _ = ndi.label(band)
    heights, widths = [], []
    for slices in ndi.find_objects(labels):
        if slices is not None:
            heights.append(slices[0].stop - slices[0].start)
            widths.append(slices[1].stop - slices[1].start)
    extras = [float(band.mean()), float(np.median(widths) / max(1, np.median(heights))),
              float(np.std(widths) / max(1, np.mean(widths))), float(np.std(heights) / max(1, np.mean(heights)))]
    return np.concatenate((pooled.ravel(), extras))


def _model(model: PathLike | Mapping[str, Any]) -> dict[str, Any]:
    data = json.loads(Path(model).read_text(encoding='utf-8')) if isinstance(model, (str, Path)) else dict(model)
    if data.get('schema') != MODEL_SCHEMA or data.get('descriptor_size') != DESCRIPTOR_SIZE:
        raise ValueError('unsupported font model schema/descriptor')
    families = data.get('families', [])
    if not families or len(set(families)) != len(families) or any(not isinstance(f, str) or not f for f in families):
        raise ValueError('font model needs unique font family ids')
    centroids = np.asarray(data.get('centroids'), dtype=float)
    if centroids.shape != (len(families), DESCRIPTOR_SIZE) or not np.isfinite(centroids).all():
        raise ValueError('font model centroids must have finite descriptor dimensions')
    if any(data.get('styles', {}).get(f) not in FONT_STYLES for f in families):
        raise ValueError('font model needs a supported style for every family')
    radii = np.asarray(data.get('radii'), dtype=float)
    if radii.shape != (len(families),) or not np.isfinite(radii).all() or np.any(radii <= 0):
        raise ValueError('font model needs finite positive radii')
    return data


def font_estimate(image: Image.Image | np.ndarray | PathLike, *,
                  model: PathLike | Mapping[str, Any] | None = None) -> FontEstimate:
    """Predict using an explicit local model; absent model/blank/outside support abstains."""
    if model is None:
        return FontEstimate(None, None, None, None, None, False)
    data = _model(model)
    descriptor = _descriptor(image)
    model_id, fixture = data.get('model_id'), bool(data.get('fixture_only', False))
    if descriptor is None:
        return FontEstimate(None, None, None, None, model_id, fixture)
    distances = np.sqrt(np.mean((np.asarray(data['centroids']) - descriptor) ** 2, axis=1))
    order = np.argsort(distances, kind='stable')
    index = int(order[0])
    distance = float(distances[index])
    margin = float(distances[order[1]] - distance) if len(order) > 1 else None
    family = data['families'][index] if distance <= data['radii'][index] else None
    return FontEstimate(family, data['styles'][family] if family else None, distance, margin, model_id, fixture)


def train_font_classifier(shards: PathLike, out_model: PathLike, *,
                          styles: Mapping[str, str] | None = None, max_lines: int | None = None) -> dict[str, Any]:
    """Fit streaming font centroids from known synthetic fonts, entirely in numpy on CPU."""
    if max_lines is not None and max_lines < 1:
        raise ValueError('max_lines must be positive')
    output = Path(out_model)
    if output.exists():
        raise FileExistsError(output)
    sums: dict[str, np.ndarray] = {}
    squares: dict[str, float] = {}
    counts: dict[str, int] = {}
    for row, root in iter_records(Path(shards)):
        family = row.get('font')
        if not isinstance(family, str) or font_style(family, styles) is None:
            raise ValueError('font training requires a known synthetic font on every row')
        image, _ = record_image(row, root)
        descriptor = _descriptor(image)
        if descriptor is None:
            continue
        sums[family] = sums.get(family, np.zeros(DESCRIPTOR_SIZE)) + descriptor
        squares[family] = squares.get(family, 0.0) + float(np.mean(descriptor ** 2))
        counts[family] = counts.get(family, 0) + 1
        if max_lines is not None and sum(counts.values()) >= max_lines:
            break
    if not counts:
        raise ValueError('no nonblank synthetic lines for font fitting')
    families = sorted(counts)
    centroids = [sums[f] / counts[f] for f in families]
    # Three within-family RMS standard deviations, with a small floor. This is
    # support detection, not a calibrated posterior or a real-scan qualification.
    radii = [max(.05, 3 * np.sqrt(max(0., squares[f] / counts[f] - float(np.mean(c ** 2)))))
             for f, c in zip(families, centroids)]
    data = dict(schema=MODEL_SCHEMA, model_id=output.name, fixture_only=False,
                descriptor_size=DESCRIPTOR_SIZE, families=families,
                styles={f: font_style(f, styles) for f in families}, counts=counts,
                centroids=[c.tolist() for c in centroids], radii=radii,
                training_source=str(Path(shards).resolve()), algorithm='nearest centroid / RMS distance')
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + '\n')
    return data

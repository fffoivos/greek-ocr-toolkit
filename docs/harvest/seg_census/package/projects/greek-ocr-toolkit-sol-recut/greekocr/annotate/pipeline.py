"""Atomic metadata sidecars and comparable real/synthetic supply reports."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import replace
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any, Iterable, Mapping

import numpy as np

from greekocr.annotate._records import iter_records, record_image, record_text
from greekocr.annotate.font import FONT_STYLES, FontEstimate, font_estimate, font_style
from greekocr.annotate.line_features import line_features, load_lexicon
from greekocr.annotate.sources import source_metadata
from greekocr._vendor.bench.line_categories import categories
from greekocr.types import PathLike

__all__ = ['annotate_records', 'distribution_report']

ANNOTATION_SCHEMA = 'greekocr-line-metadata-v1'
NUMERIC = ('height_px', 'width_px', 'aspect', 'ink_coverage', 'background_level',
           'contrast', 'local_contrast_p10', 'local_contrast_p90', 'stroke_width_px', 'xheight_px',
           'capheight_ratio', 'blur', 'noise', 'curl_px', 'skew_deg', 'n_chars', 'n_words', 'n_letters',
           'polytonic_mark_density', 'digit_ratio', 'punct_ratio', 'upper_ratio', 'lexicon_validity', 'severity')
CATEGORICAL = ('polarity', 'clipped_edges', 'script_class', 'language_guess', 'bg_type', 'font', 'font_style', 'applied_ops')


def _load_catalogue(catalogue: Any) -> Any:
    if not isinstance(catalogue, (str, Path)):
        return catalogue
    path = Path(catalogue)
    if path.suffix == '.jsonl':
        return [row for row, _ in iter_records(path)]
    return json.loads(path.read_text(encoding='utf-8'))


def _annotate(row: dict[str, Any], root: Path, catalogue: Any, lexicon: Any, font_model: Any) -> dict[str, Any]:
    image, path = record_image(row, root)
    text = record_text(row)
    geometry = row.get('geometry', row.get('diagnostics'))
    if geometry is None and any(k in row for k in ('curve', 'curl_px', 'curl_amplitude_px', 'source_boundary_ink')):
        geometry = row
    measured = line_features(image, text, geometry=geometry, lexicon=lexicon)
    family = row.get('font')
    known_font = isinstance(family, str) and font_style(family) is not None
    styles = dict(font_model.get('styles', {})) if isinstance(font_model, Mapping) else {}
    if row.get('font_style') in FONT_STYLES and known_font:
        styles[family] = row['font_style']
    estimate = (FontEstimate(family, font_style(family, styles), None, None, 'record.font', False)
                if known_font else font_estimate(image, model=font_model))
    # Real imports encode unmeasured defaults. Retain those in the input row,
    # but never promote their severity=0/bg_type=flat into measured evidence.
    imported_real = isinstance(family, str) and family.casefold() == 'real'
    severity = row.get('severity') if not imported_real else None
    if severity is not None and (isinstance(severity, bool) or not isinstance(severity, int) or not 0 <= severity <= 3):
        raise ValueError('factory severity must be an integer in [0, 3]')
    ops = row.get('applied_ops')
    if ops is not None and (not isinstance(ops, (list, tuple)) or any(not isinstance(op, str) for op in ops)):
        raise ValueError('applied_ops must be a list of operation names or null')
    bg_type = row.get('bg_type') if not imported_real else None
    if bg_type is not None and bg_type not in ('flat', 'gradient', 'textured'):
        raise ValueError('factory bg_type must be flat, gradient or textured')
    measured = replace(measured, font=estimate.font, font_style=estimate.font_style, severity=severity,
                       applied_ops=tuple(ops) if ops is not None else None, bg_type=bg_type or measured.bg_type)
    result = dict(row)
    # Parquet's binary raster has no JSON representation. Reports read it in
    # memory; metadata exports omit it and retain its exact raster hash instead.
    if result.get('image_png') is not None:
        import hashlib
        import base64
        payload = result.pop('image_png')
        payload = base64.b64decode(payload, validate=True) if isinstance(payload, str) else payload
        result['image_png_sha256'] = hashlib.sha256(payload).hexdigest()
    if path is not None:
        result['crop_path'] = str(path)
    result.update(annotation_schema=ANNOTATION_SCHEMA, line_features=measured.to_dict(),
                  source_metadata=source_metadata(row, catalogue), font_estimate=estimate.to_dict(),
                  line_categories=categories(dict(row, text=text or '', width=image.width)))
    return result


def annotate_records(records_jsonl: PathLike, out_jsonl: PathLike, *, catalogue: Any = None,
                     lexicon: PathLike | Iterable[str] | None = None,
                     font_model: PathLike | Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Stream records into a new atomic JSONL sidecar; preserve labels, provenance and admission."""
    source, output = Path(records_jsonl).resolve(), Path(out_jsonl).resolve()
    if source == output or source.is_dir() and output.is_relative_to(source):
        raise ValueError('annotation output must be separate from its input')
    if output.exists():
        raise FileExistsError(output)
    catalogue = _load_catalogue(catalogue)
    words = load_lexicon(lexicon) if lexicon is not None else None
    model = _load_catalogue(font_model)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    count = 0
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=output.parent,
                                         prefix=f'.{output.name}.', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            for row, root in iter_records(source):
                result = _annotate(row, root, catalogue, words, model)
                stream.write(json.dumps(result, ensure_ascii=False, allow_nan=False) + '\n')
                count += 1
            stream.flush()
            os.fsync(stream.fileno())
        # Atomic creation with no replacement even if another writer won a race.
        os.link(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return dict(schema=ANNOTATION_SCHEMA, records=count, input=str(source), output=str(output))


def _report_values(row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    features = row['line_features']
    numbers = {name: features.get(name) for name in NUMERIC}
    for field in ('background_rgb', 'background_cast'):
        values = features.get(field)
        for index, channel in enumerate('rgb'):
            numbers[f'{field}.{channel}'] = values[index] if values is not None else None
    labels = {name: features.get(name) for name in CATEGORICAL}
    source = row.get('source_metadata', {})
    numbers['year'] = source.get('year')
    labels.update({name: source.get(name) for name in ('year_basis', 'collection', 'doc_type', 'licence', 'licence_tier', 'tier', 'page_position')})
    labels['line_categories'] = row.get('line_categories')
    estimate = row.get('font_estimate', {})
    numbers.update({f'font_estimate.{name}': estimate.get(name) for name in ('distance', 'margin')})
    labels['font_estimate.model_id'] = estimate.get('model_id')
    labels['font_estimate.fixture_only'] = estimate.get('fixture_only')
    return numbers, labels


def _cell(value: Any) -> str:
    return str(value).replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')


def distribution_report(out_jsonl: PathLike, *, catalogue: Any = None,
                        lexicon: PathLike | Iterable[str] | None = None,
                        font_model: PathLike | Mapping[str, Any] | None = None) -> str:
    """Report all numeric quantiles/histograms and categorical counts per source, including unknowns."""
    groups: dict[str, dict[str, Any]] = {}
    catalogue = _load_catalogue(catalogue)
    words = load_lexicon(lexicon) if lexicon is not None else None
    model = _load_catalogue(font_model)
    for row, root in iter_records(Path(out_jsonl)):
        if 'line_features' not in row:
            row = _annotate(row, root, catalogue, words, model)
        name = str(row.get('source_dataset') or row.get('source') or 'unknown')
        group = groups.setdefault(name, dict(n=0, numbers=defaultdict(list), missing=Counter(), labels=defaultdict(Counter)))
        group['n'] += 1
        numbers, labels = _report_values(row)
        for key, value in numbers.items():
            if value is None:
                group['missing'][key] += 1
            elif isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f'non-finite/non-numeric feature: {key}')
            else:
                group['numbers'][key].append(value)
            group['numbers'][key]  # retain all-missing columns
        for key, value in labels.items():
            values = list(value) if isinstance(value, (list, tuple)) else [value]
            if not values:
                values = ['<empty>']
            for item in set(json.dumps(v, ensure_ascii=False, sort_keys=True) if isinstance(v, dict) else str(v) if v is not None else '<unknown>' for v in values):
                group['labels'][key][item] += 1
    lines = ['# Line metadata distribution', '',
             f'Schema: `{ANNOTATION_SCHEMA}`. Records: {sum(g["n"] for g in groups.values())}.', '',
             'All numeric features include missing counts, p0/p10/p25/p50/p75/p90/p100, and ten equal-width histogram bins. '
             'Constant values use one bin. Lists count each member once per line; empty and unknown are distinct. '
             'Pixel measurements are at native scale. Fetch years and rule/model guesses retain their provenance.', '']
    if not groups:
        lines += ['No records.', '']
    for name, group in sorted(groups.items()):
        lines += [f'## Source: {_cell(name)} ({group["n"]} lines)', '',
                  '| Numeric feature | n | missing | p0 | p10 | p25 | p50 | p75 | p90 | p100 |',
                  '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
        histograms = []
        for key, values in sorted(group['numbers'].items()):
            quantiles = np.quantile(values, [0, .1, .25, .5, .75, .9, 1]) if values else [None] * 7
            lines.append('| ' + ' | '.join([key, str(len(values)), str(group['missing'][key])] +
                                          [f'{v:.6g}' if v is not None else '—' for v in quantiles]) + ' |')
            if values:
                if min(values) == max(values):
                    histogram = f'[{values[0]:.6g}]: {len(values)}'
                else:
                    counts, edges = np.histogram(values, bins=10)
                    histogram = '; '.join(f'[{a:.6g}, {b:.6g}{"]" if i == 9 else ")"}: {n}'
                                          for i, (a, b, n) in enumerate(zip(edges[:-1], edges[1:], counts)))
            else:
                histogram = '<unknown>'
            histograms.append(f'| {key} | {histogram} |')
        lines += ['', '| Numeric feature | Histogram (interval: count) |', '| --- | --- |'] + histograms
        lines += ['', '| Categorical feature | Value | Lines |', '| --- | --- | ---: |']
        for key, counts in sorted(group['labels'].items()):
            for value, n in sorted(counts.items()):
                lines.append(f'| {key} | {_cell(value)} | {n} |')
        lines.append('')
    return '\n'.join(lines)

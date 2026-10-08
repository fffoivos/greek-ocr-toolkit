"""Reference-free crop comparison with explicit local readers and blind choices."""
from __future__ import annotations

from dataclasses import asdict, replace
import csv
import hashlib
import html
from itertools import combinations
import json
import math
from pathlib import Path
import random
import statistics
from typing import Any, Callable, Mapping, Sequence
import unicodedata

from PIL import Image

from greekocr.ops.receipts import file_sha256
from greekocr.real.geometry import DEFAULT_PAD, GEOMETRY_POLICY, crop_quality, refine_line
from greekocr.score import edit_distance
from greekocr.types import PathLike

__all__ = ['evaluate_geometry', 'inter_reader_cer']
EvaluationReader = Callable[[Path], str | Mapping[str, Any]]
POLICIES = ('original', 'v1', 'v2', 'v3')


def inter_reader_cer(first: str, second: str) -> float:
    """Symmetric NFD codepoint CER, distance / max(lengths, 1); zero is agreement."""
    a, b = unicodedata.normalize('NFD', first), unicodedata.normalize('NFD', second)
    return edit_distance(a, b)/max(1, len(a), len(b))


def _reading(raw: str | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(raw, str):
        raw = {'text': raw}
    if not isinstance(raw, Mapping) or not isinstance(raw.get('text'), str):
        raise TypeError('reader must return text or a mapping with string text')
    result = dict(text=raw['text'], mean_confidence=raw.get('mean_confidence'),
                  min_confidence=raw.get('min_confidence'),
                  mean_log_probability=raw.get('mean_log_probability', raw.get('reader_confidence')))
    probabilities = raw.get('character_confidences')
    if probabilities is not None:
        if not isinstance(probabilities, (list, tuple)):
            raise TypeError('character_confidences must be a sequence of probabilities')
        if any(isinstance(p, bool) or not isinstance(p, (float, int)) or not math.isfinite(p)
               or not 0 <= p <= 1 for p in probabilities):
            raise ValueError('character_confidences must be finite probabilities in [0, 1]')
        result.update(character_confidences=list(probabilities),
                      mean_confidence=statistics.mean(probabilities) if probabilities else None,
                      min_confidence=min(probabilities) if probabilities else None,
                      mean_log_probability=statistics.mean(math.log(max(p, 1e-300)) for p in probabilities)
                      if probabilities else None)
    for key in ('mean_confidence', 'min_confidence', 'mean_log_probability'):
        value = result[key]
        if value is not None and (isinstance(value, bool) or not isinstance(value, (float, int))
                or not math.isfinite(value) or value > (0 if key == 'mean_log_probability' else 1)
                or (key != 'mean_log_probability' and value < 0)):
            raise ValueError(f'invalid reader {key}')
    return result


def _mean(values: Sequence[float | None]) -> float | None:
    present = [v for v in values if v is not None]
    return statistics.mean(present) if present else None


def _page_path(row: Mapping[str, Any], base: Path, pages: Path | Mapping[str, PathLike] | None) -> Path:
    name = row.get('page_image_path', row.get('page_image'))
    if isinstance(pages, Mapping):
        key = str(row.get('page_id', name))
        if key not in pages:
            raise ValueError(f'page-images manifest has no page {key}')
        return (base/Path(pages[key])).resolve()
    if name is not None:
        path = Path(name)
        if path.is_absolute():
            return path
        if pages is not None:
            candidate = pages/path
            if candidate.is_file():
                return candidate.resolve()
            # A manifest may include its old pages/ prefix; avoid recursive search.
            return (pages/path.name).resolve()
        return (base/path).resolve()
    if pages is not None and row.get('page_id') is not None:
        key = str(row['page_id'])
        if Path(key).name != key:
            raise ValueError('page_id must be a filename or simple identifier')
        return (pages/(key if Path(key).suffix else key+'.png')).resolve()
    raise ValueError('each row requires page_image_path or page_id with --page-images')


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def _blind_page(destination: Path, lines: Sequence[Mapping[str, Any]]) -> None:
    sections = []
    for line in lines:
        index = line['line_index']
        choices = ''.join(
            f'<label><input type="radio" name="line{index}" value="{c["choice"]}"> '
            f'{c["choice"]}<img src="{html.escape(c["crop_path"], quote=True)}" alt="Choice {c["choice"]}"></label>'
            for c in line['choices'])
        sections.append(f'<section><h2>Line {index+1}</h2>{choices}</section>')
    destination.joinpath('ab.html').write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        '<title>Blind crop comparison</title><style>body{font:16px system-ui;margin:2rem;background:#eee}'
        'section{background:white;padding:1rem;margin:1rem 0}label{display:block;margin:1rem 0}'
        'img{display:block;max-width:100%;height:auto;margin-top:.5rem}</style>'
        '<h1>Blind crop comparison</h1><p>Select the clearest complete line, including its accents. '
        'The order is shuffled independently for each line.</p><button id="save">Download choices</button>'
        + ''.join(sections)
        + '<script>document.getElementById("save").onclick=()=>{const choices=[...document.querySelectorAll('
        '\'input:checked\')].map(e=>({line_index:Number(e.name.slice(4)),choice:e.value}));'
        'const url=URL.createObjectURL(new Blob([JSON.stringify({choices},null,2)],{type:"application/json"}));'
        'const a=document.createElement("a");a.href=url;a.download="blind_choices.json";a.click();'
        'setTimeout(()=>URL.revokeObjectURL(url),1000)};</script></html>\n', encoding='utf-8')


def evaluate_geometry(records: PathLike | Sequence[Mapping[str, Any]], *,
                      page_images: PathLike | Mapping[str, PathLike] | None = None,
                      policies: Sequence[str] = POLICIES,
                      readers: Mapping[str, EvaluationReader], out: PathLike,
                      pad: int = DEFAULT_PAD, blind_seed: int = 0) -> dict[str, Any]:
    """Save every policy crop, pixel/reader evidence, summaries and a blind A/B page.

    Rows require unique line_id and bbox_pixel. Page paths use the records parent
    or page_images directory/JSON mapping; crop_path is optional and must have
    the box's pixel dimensions. Text/layer fields are unscored diagnostics only.
    Readers are caller-supplied independent local callables. Failures are retained
    per line/policy/reader, never turned into zero CER or perfect confidence.
    """
    if not policies or len(set(policies)) != len(policies) or any(p not in POLICIES for p in policies):
        raise ValueError('policies must be unique choices from original,v1,v2,v3')
    if not readers or any(not isinstance(n, str) or not n or not callable(r) for n, r in readers.items()):
        raise TypeError('readers must map nonempty names to crop callables')
    if isinstance(pad, bool) or not isinstance(pad, int) or pad < 0:
        raise ValueError('pad must be a nonnegative integer')
    if isinstance(blind_seed, bool) or not isinstance(blind_seed, int):
        raise ValueError('blind_seed must be an integer')
    manifest = Path(records).resolve() if isinstance(records, (str, Path)) else None
    base = manifest.parent if manifest is not None else Path.cwd()
    rows = ([json.loads(s) for s in manifest.read_text(encoding='utf-8').splitlines() if s.strip()]
            if manifest is not None else list(records))
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping) or not {'line_id', 'bbox_pixel'} <= row.keys():
            raise ValueError('each evaluation row requires line_id and bbox_pixel')
        if not isinstance(row['line_id'], str) or not row['line_id'] or row['line_id'] in seen:
            raise ValueError('line_id must be a unique nonempty string')
        seen.add(row['line_id'])
    pages: Path | Mapping[str, PathLike] | None = None
    pages_manifest = None
    if isinstance(page_images, Mapping):
        pages = page_images
    elif page_images is not None:
        pages = Path(page_images).resolve()
        if pages.is_file() and pages.suffix.lower() == '.json':
            pages_manifest = pages
            data = json.loads(pages.read_text(encoding='utf-8'))
            if not isinstance(data, dict) or any(not isinstance(v, str) for v in data.values()):
                raise ValueError('page-images JSON must map page identifiers to image paths')
            pages = {k: str((pages.parent/v).resolve()) for k, v in data.items()}
        elif not pages.is_dir():
            raise ValueError('page-images must be an existing directory or JSON mapping')
    destination = Path(out)
    destination.mkdir(parents=True, exist_ok=False)
    destination.joinpath('crops').mkdir()
    destination.joinpath('ab_crops').mkdir()
    results, blind, mapping = [], [], []
    for index, row in enumerate(rows):
        result: dict[str, Any] = dict(line_id=row['line_id'], bbox_pixel=row['bbox_pixel'], policies={})
        # Custody of source strings without treating another OCR's output as truth.
        layers = {k: row[k] for k in ('text', 'layer', 'text_layer') if k in row}
        if layers:
            result['text_layer_diagnostic'] = dict(status='another OCR; never a reference', raw=layers)
        try:
            page_path = _page_path(row, base, pages)
            with Image.open(page_path) as source:
                page = source.convert('L')
            anchor = refine_line(page, row['bbox_pixel'], pad=pad, policy='v3')
            original_path = (base/row['crop_path']).resolve() if row.get('crop_path') else None
            if original_path is None:
                original = page.crop(anchor.source_box)
            else:
                with Image.open(original_path) as source:
                    original = source.convert('L')
            if original.size != (anchor.source_box[2]-anchor.source_box[0], anchor.source_box[3]-anchor.source_box[1]):
                raise ValueError('original crop size must match bbox_pixel at the page resolution')
            result.update(page_image_path=str(page_path), page_sha256=file_sha256(page_path),
                          original_crop_sha256=file_sha256(original_path) if original_path else None,
                          original_raster_sha256=hashlib.sha256(original.tobytes()).hexdigest())
        except Exception as error:
            result['error'] = dict(type=type(error).__name__, message=str(error))
            results.append(result)
            continue
        for policy in policies:
            evaluated: dict[str, Any] = dict(readers={})
            result['policies'][policy] = evaluated
            try:
                if policy == 'original':
                    image = original
                    diagnostics = replace(anchor.diagnostics, strip_x_origin=anchor.source_box[0],
                                          rectified=False, policy='original')
                    geometry = asdict(diagnostics)
                else:
                    line = anchor if policy == 'v3' else refine_line(page, row['bbox_pixel'], pad=pad, policy=policy)
                    image, diagnostics, geometry = line.image, line.diagnostics, line.receipt()
                name = f'crops/line{index:05d}_{policy}.png'
                image.save(destination/name)
                quality_geometry = asdict(diagnostics) | {'line_band_curve': asdict(anchor.curve),
                    'line_band_height_px': anchor.diagnostics.x_height_px}
                evaluated.update(crop_path=name, crop_sha256=file_sha256(destination/name), geometry=geometry,
                                 quality_geometry=quality_geometry,
                                 pixels=crop_quality(original, image, quality_geometry))
            except Exception as error:
                evaluated['error'] = dict(type=type(error).__name__, message=str(error))
                continue
            for name, reader in readers.items():
                try:
                    evaluated['readers'][name] = _reading(reader(destination/evaluated['crop_path']))
                except Exception as error:
                    evaluated['readers'][name] = dict(error=dict(type=type(error).__name__, message=str(error)))
            successful = {n: r for n, r in evaluated['readers'].items() if 'error' not in r}
            pairs = [dict(readers=[a, b], cer=inter_reader_cer(successful[a]['text'], successful[b]['text']))
                     for a, b in combinations(successful, 2)]
            evaluated['reader_pairs'] = pairs
            evaluated['pixels']['reader_confidence'] = _mean([r['mean_log_probability'] for r in successful.values()])
            evaluated['pixels']['inter_reader_agreement'] = _mean([p['cer'] for p in pairs])
        results.append(result)
        available = [p for p in policies if 'crop_path' in result['policies'][p]]
        # Local RNG, seeded per line; row order and the caller's RNG have no effect.
        seed = hashlib.sha256(f'{blind_seed}:{row["line_id"]}'.encode('utf-8')).digest()
        random.Random(seed).shuffle(available)
        choices, key = [], {}
        for number, policy in enumerate(available):
            letter = chr(ord('A')+number)
            name = f'ab_crops/line{index:05d}_{letter}.png'
            (destination/name).write_bytes((destination/result['policies'][policy]['crop_path']).read_bytes())
            choices.append(dict(choice=letter, crop_path=name))
            key[letter] = policy
        blind.append(dict(line_index=index, line_id=row['line_id'], choices=choices))
        mapping.append(dict(line_index=index, line_id=row['line_id'], policy_by_choice=key))
    summary = {}
    for policy in policies:
        crops = [r['policies'][policy] for r in results if policy in r['policies'] and 'pixels' in r['policies'][policy]]
        pixels = [c['pixels'] for c in crops]
        readings = [reading for c in crops for reading in c['readers'].values() if 'error' not in reading]
        confidences = [r['mean_log_probability'] for r in readings if r['mean_log_probability'] is not None]
        agreements = [p['inter_reader_agreement'] for p in pixels if p['inter_reader_agreement'] is not None]
        summary[policy] = dict(lines=len(rows), evaluated=len(crops), crop_errors=len(rows)-len(crops),
            reader_errors=sum('error' in r for c in crops for r in c['readers'].values()),
            confidence_samples=len(confidences), agreement_samples=len(agreements),
            mean_reader_confidence=_mean(confidences), mean_inter_reader_agreement=_mean(agreements),
            diacritic_ink_retained=_mean([p['diacritic_ink_retained'] for p in pixels]),
            body_ink_retained=_mean([p['body_ink_retained'] for p in pixels]),
            neighbour_ink_removed=_mean([p['neighbour_ink_removed'] for p in pixels]),
            clipping_rate=_mean([float(p['clipped_left'] or p['clipped_right']) for p in pixels]),
            by_reader={name: dict(mean_reader_confidence=_mean([
                c['readers'][name]['mean_log_probability'] for c in crops if 'error' not in c['readers'][name]]))
                       for name in readers})
    receipt = dict(schema='o4d-reference-free-evaluation-v1', geometry_policy=GEOMETRY_POLICY,
        input_sha256=file_sha256(manifest) if manifest else None,
        page_images_sha256=file_sha256(pages_manifest) if pages_manifest else None,
        policies=list(policies), readers=list(readers), pad=pad, blind_seed=blind_seed,
        reader_bindings={name: dict(getattr(reader, '__self__', reader).binding)
                         for name, reader in readers.items() if hasattr(getattr(reader, '__self__', reader), 'binding')},
        signals=dict(reader_confidence='mean per-character natural log probability; zero probabilities floored at 1e-300',
                     inter_reader_agreement='symmetric NFD codepoint CER = edit distance / max(lengths, 1); lower is better',
                     text_layer='unscored diagnostic only; never a reference',
                     missing='null; errors excluded from means; sample counts reported'), summary=summary, rows=results)
    _write_json(destination/'receipt.json', receipt)
    _write_json(destination/'ab_pairs.json', dict(schema='blind-crop-pairs-v1', lines=blind))
    _write_json(destination/'ab_mapping.json', dict(schema='blind-crop-mapping-v1', seed=blind_seed, lines=mapping))
    _blind_page(destination, blind)
    fields = ['policy', 'evaluated', 'mean_reader_confidence', 'mean_inter_reader_agreement',
              'diacritic_ink_retained', 'body_ink_retained', 'neighbour_ink_removed', 'clipping_rate',
              'confidence_samples', 'agreement_samples', 'reader_errors', 'crop_errors']
    table = [dict(policy=p, **{k: summary[p][k] for k in fields[1:]}) for p in policies]
    with (destination/'summary.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(table)
    markdown = ['| '+' | '.join(fields)+' |', '| '+' | '.join(['---']*len(fields))+' |']
    markdown += ['| '+' | '.join('unavailable' if row[k] is None else str(row[k]) for k in fields)+' |' for row in table]
    (destination/'summary.md').write_text('\n'.join(markdown)+'\n', encoding='utf-8')
    return receipt

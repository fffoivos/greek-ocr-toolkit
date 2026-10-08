"""Historical text-layer agreement replay; diagnostic only, never an accuracy gate."""
from __future__ import annotations

from dataclasses import replace
import difflib
import json
from pathlib import Path
import statistics
from tempfile import TemporaryDirectory
from typing import Any, Mapping, Sequence
import unicodedata

from PIL import Image

from greekocr.ops.receipts import file_sha256
from greekocr.real.geometry import (
    DEFAULT_PAD, GEOMETRY_POLICY, hyphen_at_line_end, refine_line,
    scan_admission, split_multiline,
)
from greekocr.score import strict_cer
from greekocr.types import CropReader, PathLike

__all__ = ['comparison_scores', 'summarize_measurements', 'measure_geometry']


def comparison_scores(text: str, old: str, new: str) -> dict[str, Any]:
    """Replay historical layer-agreement diagnostics, never reference accuracy.

    SequenceMatcher's opcode cost is not minimum Levenshtein distance. Both are
    reported, with whitespace left intact for CER and stripped only for exacts.
    Raw reader strings and the source text remain unchanged in the result.
    """
    reference = unicodedata.normalize('NFD', text)
    scores: dict[str, Any] = dict(layer=text, old=old, new=new)
    for name, prediction in (('old', old), ('new', new)):
        normalized = unicodedata.normalize('NFD', prediction)
        matcher = difflib.SequenceMatcher(None, reference, normalized, autojunk=False)
        edits = sum(max(i1-i0, j1-j0) for tag, i0, i1, j0, j1 in matcher.get_opcodes()
                    if tag != 'equal')
        scores[f'cer_{name}'] = edits/max(1, len(reference))
        scores[f'levenshtein_cer_{name}'] = strict_cer(reference, normalized)
        scores[f'exact_{name}'] = reference.strip() == normalized.strip()
    return scores


def summarize_measurements(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Aggregate successfully scored pairs; errors never count as improvements."""
    scored = [r for r in rows if 'error' not in r]
    def mean(key: str, subset: Sequence[Mapping[str, Any]] = scored) -> float | None:
        return statistics.mean(r[key] for r in subset) if subset else None
    def median(key: str) -> float | None:
        return statistics.median(r[key] for r in scored) if scored else None
    tiers = sorted({r['tier'] for r in rows if r.get('tier') is not None})
    by_tier = {}
    for tier in tiers:
        subset = [r for r in scored if r.get('tier') == tier]
        by_tier[tier] = dict(n=sum(r.get('tier') == tier for r in rows), scored=len(subset),
                             exact_old=sum(r['exact_old'] for r in subset),
                             exact_new=sum(r['exact_new'] for r in subset),
                             cer_old=mean('cer_old', subset), cer_new=mean('cer_new', subset))
    return dict(
        n=len(rows), scored=len(scored), errors=len(rows)-len(scored),
        cer_old_mean=mean('cer_old'), cer_new_mean=mean('cer_new'),
        cer_old_median=median('cer_old'), cer_new_median=median('cer_new'),
        levenshtein_cer_old_mean=mean('levenshtein_cer_old'),
        levenshtein_cer_new_mean=mean('levenshtein_cer_new'),
        exact_old=sum(r['exact_old'] for r in scored), exact_new=sum(r['exact_new'] for r in scored),
        admitted=sum(r.get('admitted', False) for r in scored),
        improved=sum(r['cer_new'] < r['cer_old'] for r in scored),
        worsened=sum(r['cer_new'] > r['cer_old'] for r in scored),
        unchanged=sum(r['cer_new'] == r['cer_old'] for r in scored),
        multi_baseline=sum(r.get('split_count', 1) > 1 for r in scored),
        source_multi_baseline=sum(r.get('source_n_baselines', 0) > 1 for r in scored),
        hyphen_flags=sum(r.get('hyphen_flag', False) for r in scored),
        by_tier=by_tier,
    )


def measure_geometry(lines: PathLike | Sequence[Mapping[str, Any]], reader: CropReader, *,
                     out: PathLike | None = None, pad: int = DEFAULT_PAD,
                     reader_name: str | None = None) -> dict[str, Any]:
    """Read each original path and its refined PNG with a caller-supplied reader.

    JSONL rows require line_id, crop_path, bbox_pixel, page_image_path and text;
    paths are relative to the JSONL's parent. Sequence paths are relative to cwd.
    Optional tier is aggregated. Only one selected line is scored against the
    unsplit label; detected split boxes are reported without assigning text.
    A new output directory retains crops and receipt.json. Without out, PNGs
    live in a temporary directory for the duration of the callable invocations.
    Per-line image/reader failures are recorded and later lines still run.
    """
    if not callable(reader):
        raise TypeError('reader must be callable: reader(Path) -> str')
    if isinstance(pad, bool) or not isinstance(pad, int) or pad < 0:
        raise ValueError('pad must be a nonnegative integer')
    manifest = Path(lines).resolve() if isinstance(lines, (str, Path)) else None
    if manifest is not None:
        records = [json.loads(s) for s in manifest.read_text(encoding='utf-8').splitlines() if s.strip()]
        base = manifest.parent
    else:
        records = list(lines)
        base = Path.cwd()
    required = {'line_id', 'crop_path', 'bbox_pixel', 'page_image_path', 'text'}
    seen = set()
    for row in records:
        if not isinstance(row, Mapping) or not required <= row.keys():
            raise ValueError(f'each measurement row requires {sorted(required)}')
        if not isinstance(row['line_id'], str) or not row['line_id'] or row['line_id'] in seen:
            raise ValueError('measurement line_id must be a unique nonempty string')
        if not isinstance(row['text'], str):
            raise TypeError('measurement text must be a string')
        seen.add(row['line_id'])
    # Importing/loading a reader is the caller's explicit action, never implicit OCR.
    name = reader_name or f'{getattr(reader, "__module__", type(reader).__module__)}:' \
        f'{getattr(reader, "__qualname__", type(reader).__qualname__)}'
    with TemporaryDirectory(prefix='greekocr-geometry-measure-') as temp:
        destination = Path(out) if out is not None else Path(temp)
        if out is not None:
            destination.mkdir(parents=True, exist_ok=False)
        results = []
        cached_path: Path | None = None
        cached_page: Image.Image | None = None
        for index, row in enumerate(records):
            result = dict(line_id=row['line_id'], tier=row.get('tier'), text=row['text'],
                          bbox_pixel=row['bbox_pixel'])
            try:
                original_path = (base/row['crop_path']).resolve()
                page_path = (base/row['page_image_path']).resolve()
                result.update(crop_path=str(original_path), page_image_path=str(page_path),
                              crop_sha256=file_sha256(original_path), page_sha256=file_sha256(page_path))
                if page_path != cached_path:
                    with Image.open(page_path) as source:
                        cached_page = source.convert('L')
                    cached_path = page_path
                line = refine_line(cached_page, row['bbox_pixel'], pad=pad)
                line = replace(line, text=row['text'], source_text=row['text'],
                               diagnostics=replace(line.diagnostics,
                                   hyphen_missing_in_label=hyphen_at_line_end(line, row['text'])))
                splits = split_multiline(row['bbox_pixel'], line.kept_components+line.dropped_components)
                refined_name = f'line{index:05d}.png'
                refined_path = destination/refined_name
                line.image.save(refined_path)
                result.update(refined_crop_path=refined_name if out is not None else None,
                              refined_crop_sha256=file_sha256(refined_path), geometry=line.receipt(),
                              admitted=scan_admission(line.diagnostics).admitted,
                              n_baselines=line.diagnostics.n_baselines,
                              source_n_baselines=line.diagnostics.source_n_baselines,
                              split_count=len(splits), split_boxes=splits,
                              curl=line.diagnostics.curl_amplitude_px,
                              hyphen_flag=line.diagnostics.hyphen_missing_in_label)
                old, new = reader(original_path), reader(refined_path)
                if not isinstance(old, str) or not isinstance(new, str):
                    raise TypeError('reader must return a string for each crop')
                result.update(comparison_scores(row['text'], old, new))
            except Exception as error:
                result['error'] = dict(type=type(error).__name__, message=str(error))
            results.append(result)
        receipt = dict(schema='o4d-geometry-measure-v1', geometry_policy=GEOMETRY_POLICY,
                       input_sha256=file_sha256(manifest) if manifest is not None else None,
                       reader=name, pad=pad,
                       diagnostic_only=True, text_layer_status='another OCR; never a reference or adoption gate',
                       scoring=dict(cer='NFD SequenceMatcher opcode cost / reference length; autojunk=False',
                                    levenshtein_cer='NFD minimum unit-cost codepoint edit distance / reference length',
                                    exact='NFD equality after stripping leading/trailing whitespace',
                                    split_labels='score selected track only; split text remains unassigned',
                                    errors='excluded from all score means and success counts'),
                       summary=summarize_measurements(results), rows=results)
        if out is not None:
            (destination/'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2,
                                                             allow_nan=False)+'\n', encoding='utf-8')
        return receipt

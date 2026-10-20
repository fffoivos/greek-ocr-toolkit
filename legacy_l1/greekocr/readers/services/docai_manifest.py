"""Freeze local crop bytes and distinguish supplied gold from diagnostic text."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Sequence

COHORTS = ('polytondb_gold300', 'o4d_lines', 'borndigital100', 'o4d_sample400')
DEFAULT_COHORTS = COHORTS[:3]
__all__ = ['build_manifest', 'build_polytondb_manifest', 'build_o4d_manifest',
           'build_borndigital_manifest', 'load_manifest']


def _rows(path: Path) -> list[dict]:
    if path.suffix == '.jsonl':
        return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    value = json.loads(path.read_text(encoding='utf-8'))
    return value['lines'] if isinstance(value, dict) else value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _crop(root: Path, row: dict, subdir: str) -> Path:
    # Fixture indices retain worker paths. Rebase to the fixture, never that old worker.
    name = Path(row.get('file') or row['crop_path']).name
    path = (root / subdir / name).resolve()
    if not path.is_file():
        raise ValueError(f'missing fixture crop: {path}')
    if row.get('crop_sha256') and _sha(path) != row['crop_sha256']:
        raise ValueError(f'fixture crop hash mismatch: {path}')
    return path


def _entry(root: Path, row: dict, subdir: str, cohort: str, gold: str | None,
           diagnostics: dict) -> dict:
    crop = _crop(root, row, subdir)
    return dict(crop_path=str(crop), crop_sha256=_sha(crop), line_id=row['line_id'],
                cohort=cohort, gold_text=gold, diagnostics=diagnostics,
                script_class=row.get('script_class', 'other'),
                provenance=dict(fixture=str(root.resolve()), source_record=row))


def build_polytondb_manifest(root: str | Path) -> list[dict]:
    root = Path(root)
    gold = _rows(root / 'gold.jsonl')
    if len(gold) != 300:
        raise ValueError('Polyton-DB requires the exact frozen 300-line gold fixture')
    diagnostics = {}
    for field, filename in [('cllg_text', 'cllg.predictions.jsonl'),
                            ('ours_text', 'f50_s0.predictions.jsonl')]:
        path = root / filename
        diagnostics[field] = {r['line_id']: r for r in _rows(path)} if path.is_file() else {}
    result = []
    for row in gold:
        if row.get('label_tier') != 'gold':
            raise ValueError('Polyton-DB record is not gold')
        texts = dict(layer_text=None, cllg_text=None, ours_text=None)
        for field, predictions in diagnostics.items():
            prediction = predictions.get(row['line_id'])
            if prediction and prediction.get('crop_sha256') == row.get('crop_sha256'):
                texts[field] = prediction['prediction']
        result.append(_entry(root, row, 'imported_gold/crops', 'polytondb_gold300', row['text'], texts))
    return result


def build_o4d_manifest(root: str | Path, *, sample: bool = False) -> list[dict]:
    root = Path(root)
    cohort, subdir = ('o4d_sample400', 'crops') if sample else ('o4d_lines', '')
    return [_entry(root, row, subdir, cohort, None,
                   dict(layer_text=row.get('layer_text', row.get('layer')),
                        cllg_text=row.get('cllg_text', row.get('cllg')),
                        ours_text=row.get('ours_text')))
            for row in _rows(root / 'index.json')]


def build_borndigital_manifest(root: str | Path) -> list[dict]:
    root = Path(root)
    result = []
    for row in _rows(root / 'index.json'):
        # Only explicit gold_text is gold: do not promote layer/text fields.
        diagnostics = dict(row.get('diagnostics') or {})
        for field in ('layer_text', 'cllg_text', 'ours_text'):
            diagnostics.setdefault(field, row.get(field))
        result.append(_entry(root, row, 'crops', 'borndigital100', row.get('gold_text'), diagnostics))
    return result


def build_manifest(fixtures_root: str | Path, out: str | Path, *,
                   cohorts: Sequence[str] = DEFAULT_COHORTS) -> dict:
    root, out = Path(fixtures_root), Path(out)
    if not cohorts or len(set(cohorts)) != len(cohorts) or set(cohorts) - set(COHORTS):
        raise ValueError('choose distinct supported fixture cohorts: ' + ', '.join(COHORTS))
    builders = dict(polytondb_gold300=build_polytondb_manifest, o4d_lines=build_o4d_manifest,
                    borndigital100=build_borndigital_manifest,
                    o4d_sample400=lambda path: build_o4d_manifest(path, sample=True))
    rows, counts, unavailable = [], {}, []
    for cohort in cohorts:
        directory = root / cohort
        if cohort == 'borndigital100' and not (directory / 'index.json').is_file():
            unavailable.append(cohort)
            continue
        entries = builders[cohort](directory)
        rows.extend(entries)
        counts[cohort] = len(entries)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x', encoding='utf-8') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')
    return dict(manifest=str(out.resolve()), lines=len(rows), cohorts=counts,
                unavailable=unavailable, sha256=_sha(out))


def load_manifest(path: str | Path) -> list[dict]:
    path = Path(path).resolve()
    rows, seen = _rows(path), set()
    if not rows:
        raise ValueError('manifest must contain at least one line')
    for number, row in enumerate(rows, 1):
        for field in ('crop_path', 'line_id', 'cohort'):
            if not isinstance(row.get(field), str) or not row[field]:
                raise ValueError(f'manifest row {number}: {field} must be a nonempty string')
        key = (row['cohort'], row['line_id'])
        if key in seen:
            raise ValueError(f'duplicate manifest line: {key}')
        seen.add(key)
        if row.get('gold_text') is not None and not isinstance(row['gold_text'], str):
            raise ValueError(f'manifest row {number}: gold_text must be text or null')
        row.setdefault('gold_text', None)
        diagnostics = row.get('diagnostics')
        if not isinstance(diagnostics, dict):
            raise ValueError(f'manifest row {number}: diagnostics must be an object')
        for field in ('layer_text', 'cllg_text', 'ours_text'):
            if diagnostics.get(field) is not None and not isinstance(diagnostics[field], str):
                raise ValueError(f'manifest row {number}: {field} must be text or null')
            diagnostics.setdefault(field, None)
        crop = Path(row['crop_path'])
        if not crop.is_absolute():
            crop = path.parent / crop
        crop = crop.resolve()
        actual = _sha(crop)
        if row.get('crop_sha256') and row['crop_sha256'] != actual:
            raise ValueError(f'manifest crop hash mismatch: {crop}')
        row.update(crop_path=str(crop), crop_sha256=actual)
    return rows

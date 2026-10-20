"""Offline defect threshold evaluation; VLM labels are provisional, not human gold."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Iterable
import numpy as np
from .images import ANOMALY_FIELDS, feature_vector, ImageChecks
from .judges import DEFECTS

# metric, comparison direction, provisional threshold
RULES = {
    'skew': ('skew_abs', 'ge', 1.0),
    'trails_up': ('trail_up', 'ge', 2.0),
    'trails_down': ('trail_down', 'ge', 2.0),
    'touches_top': ('top_fraction', 'gt', 0.),
    'touches_bottom': ('bottom_fraction', 'gt', 0.),
    'cut_left': ('left_fraction', 'gt', 0.),
    'cut_right': ('right_fraction', 'gt', 0.),
    'blurred': ('blur_mean', 'ge', .6),
    'low_contrast': ('local_contrast', 'le', .15),
    'obstructed': ('obstruction', 'ge', .02),
    'neighbour_intrusion': ('crowding', 'ge', .05),
    'two_lines': ('baseline_count', 'ge', 2.),
    'empty': ('ink_coverage', 'le', .003),
}


def _metrics(row: dict) -> dict:
    c = row.get('checks', row)
    return {'skew_abs': abs(c['skew_deg']), 'trail_up': -c['trail_signed_px'],
            'trail_down': c['trail_signed_px'],
            **{f'{k}_fraction': v for k,v in c['edge_ink_fraction'].items()},
            'blur_mean': c['clarity']['blur_mean'],
            'local_contrast': c['clarity']['local_contrast_p10'],
            'obstruction': c['obstruction_score'], 'crowding': c['crowding'],
            'baseline_count': c['baseline_count'], 'ink_coverage': c['ink_coverage']}


def _predict(value: float, direction: str, threshold: float) -> bool:
    return value >= threshold if direction == 'ge' else value > threshold if direction == 'gt' else value <= threshold


def confusion(truth: Iterable[bool], predictions: Iterable[bool]) -> dict:
    pairs = list(zip(truth, predictions, strict=True))
    tp = sum(t and p for t,p in pairs)
    fp = sum(not t and p for t,p in pairs)
    fn = sum(t and not p for t,p in pairs)
    tn = sum(not t and not p for t,p in pairs)
    return {'n': len(pairs), 'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
            'precision': tp/(tp+fp) if tp+fp else None,
            'recall': tp/(tp+fn) if tp+fn else None,
            'f1': 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None}


def _key(row: dict) -> str:
    return row.get('crop_sha256') or row.get('crop', '')


def _source(row: dict) -> str:
    name = row.get('line_id', Path(row.get('crop', '')).stem)
    return name.split('-p')[0]


def fit_distribution(rows: Iterable[dict], output: str | Path) -> dict:
    """Fit robust medians/MADs on unique rasters; no readings or judge labels used."""
    unique = {_key(r): r for r in rows}
    if not unique:
        raise ValueError('sample distribution requires image checks')
    vectors = np.array([feature_vector(ImageChecks(**r['checks'])) for r in unique.values()])
    center = np.median(vectors, axis=0)
    floor = np.array([.25, .2, .05, .3, .1, .05, .02, .1, .03])
    scale = np.maximum(floor, 1.4826*np.median(np.abs(vectors-center), axis=0))
    result = {'schema': 'greekocr.verify.distribution.v1', 'features': list(ANOMALY_FIELDS),
              'center': center.tolist(), 'scale': scale.tolist(), 'n': len(unique),
              'sample_digest': hashlib.sha256('\n'.join(sorted(unique)).encode()).hexdigest(),
              'method': 'diagonal robust standardized RMS; in-sample diagnostic, not a rejection probability'}
    Path(output).write_text(json.dumps(result, indent=2)+'\n')
    from .images import _reference
    if Path(output).resolve() == Path(__file__).with_name('sample_distribution.json').resolve():
        _reference.cache_clear()
    return result


def _fmt(value) -> str:
    return '—' if value is None else f'{value:.3f}' if isinstance(value, float) else str(value)


def calibrate(cheap_rows: Iterable[dict], vlm_rows: Iterable[dict], *,
              owner_notes: dict | list | None = None,
              output: str | Path = 'docs/verify/CALIBRATION.md') -> dict:
    """Evaluate default rules and fit source-separated thresholds when labels exist.

    Empty/missing judge rows are excluded, never converted into negatives. Duplicated
    rasters are counted once. Threshold fitting needs both classes in the training
    split; held-out scores use a deterministic SHA256 source-document split.
    """
    cheap = {_key(r): r for r in cheap_rows}
    labelled = {_key(r): r for r in vlm_rows if r.get('judgement') is not None
                and r['judgement'].get('readable') in ('yes', 'partly', 'no')}
    keys = sorted(cheap.keys() & labelled.keys())
    unsupported = sorted({d for key in keys for d in labelled[key]['judgement']['defects']} - RULES.keys())
    others = sorted({labelled[key]['judgement']['other_text'] for key in keys
                     if 'other' in labelled[key]['judgement']['defects'] and labelled[key]['judgement']['other_text']})
    train = [k for k in keys if int(hashlib.sha256(_source(cheap[k]).encode()).hexdigest()[:8],16)%5 != 0]
    held = [k for k in keys if k not in train]
    report = {'schema': 'greekocr.verify.calibration.v1', 'unique_images': len(cheap),
              'labelled_images': len(keys), 'unlabelled_images': len(cheap)-len(keys),
              'training_n': len(train), 'held_out_n': len(held),
              'unsupported_defects': unsupported, 'other_features_not_detected': others,
              'owner_notes_available': len(owner_notes or {}), 'defects': {}}
    def compare(defect, subset, threshold):
        metric, direction, _ = RULES[defect]
        return confusion([defect in labelled[k]['judgement']['defects'] for k in subset],
                         [_predict(_metrics(cheap[k])[metric], direction, threshold) for k in subset])
    for defect, (metric, direction, default) in RULES.items():
        suggested = default
        fitted = False
        truths = [defect in labelled[k]['judgement']['defects'] for k in train]
        if truths and any(truths) and not all(truths):
            values = sorted(set(_metrics(cheap[k])[metric] for k in train))
            # Bound fitting work; training-only quantiles + the provisional threshold.
            candidates = sorted(set(np.quantile(values, np.linspace(0, 1, min(65, len(values)))).tolist()+[default]))
            suggested = max(candidates, key=lambda v: ((compare(defect, train, v)['f1'] or 0), -abs(v-default)))
            fitted = True
        report['defects'][defect] = {'metric': metric, 'direction': direction, 'default_threshold': default,
                                     'suggested_threshold': suggested, 'fitted': fitted,
                                     'default_all': compare(defect, keys, default),
                                     'fitted_train': compare(defect, train, suggested),
                                     'held_out': compare(defect, held, suggested)}
    # Owner annotations are separate human evidence and can only be compared when
    # they explicitly provide defects and a resolvable file/line id.
    entries = ([dict(file=k, **v) if isinstance(v, dict) else dict(file=k, note=v)
                for k,v in owner_notes.items()] if isinstance(owner_notes, dict) else owner_notes or [])
    owner_pairs = []
    for note in entries:
        if not isinstance(note, dict) or not isinstance(note.get('defects'), list):
            continue
        target = note.get('file', note.get('line_id', ''))
        matching = [r for r in cheap.values() if Path(r.get('crop','')).name == target or r.get('line_id') == target]
        if len(matching) == 1:
            owner_pairs.append((matching[0], note))
    report['owner_notes_comparable'] = len(owner_pairs)
    report['owner_confusion'] = {
        d: confusion([d in n['defects'] for _,n in owner_pairs],
                     [_predict(_metrics(r)[m], direction, threshold) for r,_ in owner_pairs])
        for d,(m,direction,threshold) in RULES.items()}
    lines = ['# Readability calibration', '',
             'Raster checks and Greek reading checks are independent. The PDF text layer is another OCR and is never a reference or calibration target.', '',
             f"Unique rasters: {len(cheap)}. Available VLM labels: {len(keys)}. Unlabelled: {len(cheap)-len(keys)}.",
             f"Source-separated training / held-out counts: {len(train)} / {len(held)}.", '',
             'VLM labels are provisional observations. Precision/recall below describe agreement with that judge, not verified accuracy against human gold.', '',
             '## Default threshold confusion tables', '',
             '| Defect | Metric / threshold | TP | FP | FN | TN | Precision | Recall | F1 |',
             '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for d,row in report['defects'].items():
        c = row['default_all']
        lines.append(f"| {d} | {row['metric']} {row['direction']} {_fmt(row['default_threshold'])} | " +
                     ' | '.join(_fmt(c[k]) for k in ('tp','fp','fn','tn','precision','recall','f1'))+' |')
    lines += ['', '## Suggested thresholds and held-out agreement', '',
              '| Defect | Suggested threshold | Fitted | Held-out TP / FP / FN / TN | Precision | Recall |',
              '|---|---:|---|---|---:|---:|']
    for d,row in report['defects'].items():
        c=row['held_out']
        lines.append(f"| {d} | {_fmt(row['suggested_threshold'])} | {row['fitted']} | " +
                     ' / '.join(str(c[k]) for k in ('tp','fp','fn','tn')) +
                     f" | {_fmt(c['precision'])} | {_fmt(c['recall'])} |")
    if not keys:
        lines += ['', '**No empirical calibration is available:** the judge returned no labels. All displayed thresholds remain provisional; N=0 tables contain no observations, and undefined precision/recall are shown as dashes. These are not evidence of zero defects or high accuracy.']
    lines += ['', '## Owner notes', '',
              f"Available notes: {report['owner_notes_available']}; comparable explicit defect labels: {len(owner_pairs)}. The task expected seven notes."]
    if not owner_notes:
        lines += ['The supplied `tests/fixtures/o4d_lines/index.json` has `owner_notes: {}`. No human annotations were invented.']
    lines += ['', '| Defect | TP | FP | FN | TN | Precision | Recall |', '|---|---:|---:|---:|---:|---:|---:|']
    for d,c in report['owner_confusion'].items():
        lines.append(f'| {d} | '+' | '.join(_fmt(c[k]) for k in ('tp','fp','fn','tn','precision','recall'))+' |')
    lines += ['', '## Other features not yet detected', '',
              'Unsupported named VLM categories: '+(', '.join(unsupported) or 'none observed (no labels)' if not keys else ', '.join(unsupported) or 'none')+'.']
    lines.extend('- '+x.replace('\n',' ') for x in others)
    lines += ['', 'Cheap features cannot establish semantic legibility, font familiarity, merged character identities, missing complete words, or whether faint mirrored ink truly came from the page reverse. Edge ink alone does not prove terminal clipping; the two-line row-profile proxy needs empirical validation.', '',
              '## Method', '',
              'Defaults are fixed before judging. Fit thresholds maximize training F1 among at most 65 quantiles; metrics on held-out source documents use the fitted value. A defect lacking both training classes is left at its default. Source split: SHA256(document id) modulo 5 equals 0 for held-out. Duplicate raster SHA256s are excluded. Readings, layer OCR and tier/CER fields never enter fitting.', '']
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines), encoding='utf-8')
    path.with_suffix('.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
    return report

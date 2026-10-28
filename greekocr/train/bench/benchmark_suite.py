"""Model-independent scoring of immutable OCR panels; no inference or training.

Historical reference provenance stays explicit. Candidate labels cannot silently
become ground truth. Missing/failed predictions count against fixed denominators.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import unicodedata as ud
from greekocr.train.bench.common import read_rows, sha256, write_json
from greekocr.train.bench.score import aggregate, load_sealed

VERSION = 'ocr-benchmark-suite/0.1'


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def load_suite(path):
    path = Path(path)
    suite = json.loads(path.read_text())
    if suite.get('schema') != 'ocr-benchmark-suite-v1': raise ValueError('unknown suite schema')
    for name, entry in suite['panels'].items():
        target = path.parent / entry['path']
        if sha256(target) != entry['sha256']: raise ValueError('changed reference panel: '+name)
    return suite


def read_panel(suite_path, name, *, verify_images=True):
    suite = load_suite(suite_path)
    panel = suite['panels'][name]
    if not panel.get('scorable'): raise ValueError('candidate/unreviewed panel cannot be scored: '+name)
    path = Path(suite_path).parent / panel['path']
    if panel.get('reference_kind') == 'new_locked_verified':
        # Existing seals can explicitly be machine-agreement-only. They bind
        # bytes, not complete literal/work/exposure certification. Until that
        # full release gate is implemented, v0.1 cannot promote one to new gold.
        raise ValueError('new locked gold is disabled in v0.1: complete reference/work/exposure gate required')
    else:
        rows = list(read_rows(path))
    if len(rows) != panel['rows'] or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('reference count/ID mismatch')
    for row in rows:
        if not isinstance(row.get('text'), str) or not row['text']: raise ValueError('missing literal reference')
        if verify_images:
            crop = Path(row['crop_path'])
            if not crop.is_absolute(): crop = path.parent / crop
            if sha256(crop) != row['crop_sha256']: raise ValueError('changed benchmark pixels: '+row['id'])
    return suite, panel, rows


def prediction_map(records, expected):
    out = {}
    for record in records:
        identifier = record.get('id', record.get('line_id'))
        if not isinstance(identifier, str): raise ValueError('prediction missing ID')
        if 'id' in record and 'line_id' in record and record['id'] != record['line_id']:
            raise ValueError('conflicting prediction ID aliases')
        if identifier in out: raise ValueError('duplicate prediction ID: '+identifier)
        if identifier not in expected: raise ValueError('unknown prediction ID: '+identifier)
        hyp = record.get('hyp', record.get('prediction'))
        if 'hyp' in record and 'prediction' in record and record['hyp'] != record['prediction']:
            raise ValueError('conflicting prediction text aliases')
        failed = bool(record.get('error')) or record.get('status') in {'error','failed','unsupported','timeout'}
        if not failed and not isinstance(hyp, str): raise ValueError('invalid prediction text: '+identifier)
        out[identifier] = ('', 'failed') if failed else (hyp, 'predicted')
    return out


def audit_model(rows, model):
    """Unknown training/work identity is diagnostic, never a held-out pass."""
    audit = model.get('training_audit', {})
    excluded = set(audit.get('training_works', [])) | set(audit.get('tuning_works', []))
    crop_exposure = set(audit.get('exposed_crop_sha256', []))
    overlaps, unknown, selection_exposed = [], [], []
    for row in rows:
        if row.get('global_holdout_status') != 'verified' or row.get('development_exposures'):
            selection_exposed.append(row['id'])
        work = row.get('canonical_work')
        if row['crop_sha256'] in crop_exposure: overlaps.append(row['id'])
        elif not work or row.get('work_identity_status') != 'reviewed': unknown.append(row['id'])
        elif work in excluded: overlaps.append(row['id'])
    complete = audit.get('complete') is True and bool(audit.get('evidence'))
    return dict(status='heldout' if complete and not overlaps and not unknown and not selection_exposed else 'diagnostic_only',
                complete_training_audit=complete,exposed_rows=len(overlaps),unknown_work_rows=len(unknown),
                selection_or_holdout_status_unresolved=len(selection_exposed),
                exposed_ids=overlaps,unknown_ids=unknown,selection_or_unknown_ids=selection_exposed)


def sum_metrics(items):
    """Sum the existing scorer's integer sufficient statistics exactly.

    Score each line once; overlapping strata must not repeat quadratic Unicode
    alignment work. This changes runtime, never a metric or denominator.
    """
    items=list(items);lines=sum(x['lines'] for x in items)
    result=dict(lines=lines,cer={})
    for mode in ('nfc_char','nfd_atom','diacritic_insensitive'):
        edits=sum(x['cer'][mode]['edits'] for x in items)
        units=sum(x['cer'][mode]['reference_units'] for x in items)
        result['cer'][mode]=dict(edits=edits,reference_units=units,rate=edits/units if units else None)
    edits=sum(x['wer']['edits'] for x in items);words=sum(x['wer']['reference_words'] for x in items)
    exact=sum(x['exact_lines'] for x in items)
    confusion={k:sum(x['script_confusion'][k] for x in items) for k in ('cross_script_substitutions','aligned_letter_pairs','reference_letters')}
    confusion['rate']=confusion['cross_script_substitutions']/confusion['aligned_letter_pairs'] if confusion['aligned_letter_pairs'] else None
    result.update(wer=dict(edits=edits,reference_words=words,rate=edits/words if words else None),
                  exact_lines=exact,exact_line_rate=exact/lines if lines else None,script_confusion=confusion)
    return result


def score_panel(suite_path, name, prediction_path, model, *, verify_images=True):
    for field in ('id','model_revision','decoder','preprocessing','runtime'):
        if not model.get(field): raise ValueError('model manifest missing '+field)
    suite, panel, rows = read_panel(suite_path, name, verify_images=verify_images)
    predictions = prediction_map(read_rows(prediction_path), {r['id'] for r in rows})
    pairs, coverage = [], Counter()
    for row in rows:
        hyp, state = predictions.get(row['id'], ('','missing'))
        coverage[state] += 1
        pairs.append((row,hyp))
    primary, facets, books, measured = defaultdict(list), defaultdict(list), defaultdict(list), []
    for row, hyp in pairs:
        metric=aggregate([(row,hyp)]);measured.append(metric)
        primary[row.get('primary','unresolved')].append(metric)
        books[row.get('doc','unknown')].append(metric)
        for facet in row.get('facets',[]): facets[facet].append(metric)
    primary_results = {k:sum_metrics(v) for k,v in sorted(primary.items())}
    required = set(suite['taxonomy']['primary_targets'])
    missing = sorted(required-set(primary_results))
    fixed_macro = None
    if not missing:
        fixed_macro = sum(primary_results[k]['cer']['nfd_atom']['rate'] for k in required)/len(required)
    return dict(schema='ocr-benchmark-score-v1',metric_version=VERSION,panel=name,
        score_status='complete_predictions' if not coverage['failed'] and not coverage['missing'] else 'failure_inclusive_incomplete_predictions',
        reference_kind=panel['reference_kind'],comparison_claim=panel['comparison_claim'],
        reference_sha256=panel['sha256'],suite_sha256=sha256(suite_path),
        predictions_sha256=sha256(prediction_path),model=model,
        reference_rows=len(rows),coverage={k:coverage[k] for k in ('predicted','failed','missing')},
        failure_policy='Every missing/error/unsupported read scores as empty text; no row or character exclusion.',
        overall=sum_metrics(measured),by_primary=primary_results,
        by_facet={k:sum_metrics(v) for k,v in sorted(facets.items())},
        by_book={k:sum_metrics(v) for k,v in sorted(books.items())},
        fixed_class_macro_nfd_cer=fixed_macro,missing_primary_cells=missing,
        heldout_audit=audit_model(rows,model),
        codec_coverage=codec_coverage(rows,model),
        notes=['No aggregate across reference-source panels. Facets overlap.',
               'Literal per-codepoint NFD decomposition preserves emitted combining-mark order.',
               'Historical references are not a fresh selection-blind final test.'])


def codec_coverage(rows,model):
    atoms=model.get('codec_atoms')
    if atoms is None:return dict(status='unknown',reference_rows=len(rows),rows_excluded=0)
    allowed=set(atoms);counts=Counter();bad_rows=0
    for row in rows:
        bad=Counter(c for c in ''.join(ud.normalize('NFD',ch) for ch in row['text']) if c not in allowed)
        bad_rows+=bool(bad);counts.update(bad)
    return dict(status='inventoried',reference_rows=len(rows),unsupported_reference_rows=bad_rows,
                unsupported_atom_occurrences=dict(counts),rows_excluded=0)


def score_segmentation(reference, predictions):
    """Uncertain ground truth remains visible; uncertain model calls drop safely."""
    refs = list(reference)
    if len({r['id'] for r in refs}) != len(refs): raise ValueError('duplicate segmentation reference')
    pred = {}
    for row in predictions:
        if row['id'] in pred: raise ValueError('duplicate segmentation prediction')
        if row['id'] not in {r['id'] for r in refs}: raise ValueError('unknown segmentation prediction')
        if row['verdict'] not in {'KEEP','DROP','UNCERTAIN'}: raise ValueError('invalid segmentation verdict')
        pred[row['id']] = row['verdict']
    matrix = {t:{p:0 for p in ('KEEP','DROP')} for t in ('KEEP','DROP')}
    unresolved = uncertain_calls = missing = 0
    for row in refs:
        truth = row.get('reference_verdict')
        if truth not in {'KEEP','DROP'}: unresolved += 1; continue
        call = pred.get(row['id'])
        if call is None: missing += 1
        if call == 'UNCERTAIN': uncertain_calls += 1
        matrix[truth]['KEEP' if call == 'KEEP' else 'DROP'] += 1
    return dict(rows=len(refs),scored=sum(sum(r.values()) for r in matrix.values()),
                unresolved_reference=unresolved,uncertain_predictions=uncertain_calls,
                missing_predictions=missing,confusion_matrix=matrix,
                prediction_policy='UNCERTAIN or missing means operational DROP; ground-truth uncertainty is unscored.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('suite', type=Path); ap.add_argument('--panel', required=True)
    ap.add_argument('--predictions', type=Path, required=True)
    ap.add_argument('--model', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    result = score_panel(args.suite,args.panel,args.predictions,json.loads(args.model.read_text()))
    write_json(args.out,result)
    print(canonical(dict(panel=args.panel,reference_rows=result['reference_rows'],coverage=result['coverage'],
                         score_status=result['score_status'],strict_nfd_cer=result['overall']['cer']['nfd_atom']['rate'],heldout=result['heldout_audit']['status'])))


if __name__ == '__main__': main()

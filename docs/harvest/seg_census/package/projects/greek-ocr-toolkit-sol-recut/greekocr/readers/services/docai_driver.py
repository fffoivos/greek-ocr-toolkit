"""Gold-scored and separately labelled diagnostic commercial-OCR crop runs."""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from itertools import combinations
import json
import math
import os
from pathlib import Path
import statistics
import unicodedata

from greekocr.score import score_readings, strict_cer
from .docai_manifest import COHORTS, DEFAULT_COHORTS, build_manifest, load_manifest
from .google_docai import DEFAULT_VERSION, PRICE_PER_PAGE_USD, DocAIReader, _atomic_json, _lock, _sha

__all__ = ['run_manifest', 'summarize_run']


def _metrics(rows: list[dict], reference: str = 'gold_text') -> dict | None:
    if not rows:
        return None
    scores = score_readings([dict(text=r[reference], prediction=r['prediction'], cohort=r['cohort'],
                                  script_class=r.get('script_class', 'other'), crop_path=r['crop_path'])
                             for r in rows])
    return {field: scores[field] for field in ('overall', 'marks', 'mark_f1', 'greek_to_latin_homoglyphs')}


def _determinism(rows: list[dict]) -> dict:
    groups = {}
    for row in rows:
        if row['status'] == 'ok':
            groups.setdefault((row['cohort'], row['line_id']), []).append(row)
    pairs = [pair for group in groups.values() for pair in combinations(group, 2)]
    # Both orientations, averaged: CER is directional and repeats have no gold side.
    cer = [0.5 * (strict_cer(unicodedata.normalize('NFD', a['prediction']),
                             unicodedata.normalize('NFD', b['prediction'])) +
                  strict_cer(unicodedata.normalize('NFD', b['prediction']),
                             unicodedata.normalize('NFD', a['prediction']))) for a, b in pairs]
    return dict(pairs=len(pairs), fraction_identical=sum(a['prediction'] == b['prediction'] for a, b in pairs) / len(pairs)
                if pairs else None, mean_cer_between_repeats=statistics.mean(cer) if cer else None,
                definition='all successful within-line pairs; exact raw-text identity; mean bidirectional NFD CER')


def summarize_run(manifest: list[dict], predictions: list[dict], ledger: list[dict], repeat: int) -> dict:
    cohorts = {}
    for cohort in sorted({r['cohort'] for r in manifest}):
        inputs = [r for r in manifest if r['cohort'] == cohort]
        outputs = [r for r in predictions if r['cohort'] == cohort]
        passes = []
        for pass_index in range(1, repeat + 1):
            success = [r for r in outputs if r['pass'] == pass_index and r['status'] == 'ok']
            gold = [r for r in success if r['gold_text'] is not None]
            diagnostics = {}
            for field in ('cllg_text', 'layer_text', 'ours_text'):
                twins = [dict(r, diagnostic_text=r['diagnostics'][field]) for r in success
                         if r['diagnostics'].get(field) is not None]
                metrics = _metrics(twins, 'diagnostic_text')
                diagnostics[field] = dict(lines=len(twins), nfd_cer_agreement=metrics['overall'] if metrics else None,
                                          interpretation='DIAGNOSTICS only; agreement is not accuracy')
            passes.append(dict(pass_index=pass_index, successful=len(success), missing=len(inputs) - len(success),
                               gold_scored=len(gold), gold_expected=sum(r['gold_text'] is not None for r in inputs),
                               gold_metrics=_metrics(gold), diagnostics=diagnostics,
                               line_count_histogram=dict(Counter(r['line_count'] for r in success)),
                               line_count_anomalies=[dict(line_id=r['line_id'], lines=r['line_count'])
                                                     for r in success if r['line_count'] != 1]))
        cohorts[cohort] = dict(lines=len(inputs), gold_lines=sum(r['gold_text'] is not None for r in inputs),
                               passes=passes, determinism=_determinism(outputs))
    calls = [r for r in ledger if not r['cached']]
    latencies = sorted(r['latency_s'] for r in calls if r['status'] == 'ok')
    successful_pages = sum(r['pages_billed'] or 0 for r in calls)
    unknown = sum(r['pages_billed'] is None for r in calls)
    return dict(schema='docai-run-v1', normalization='NFD on both sides; no trimming or whitespace folding',
                repeat=repeat, cohorts=cohorts, determinism=_determinism(predictions),
                failures=[dict(cohort=r['cohort'], line_id=r['line_id'], pass_index=r['pass'], error=r['error'])
                          for r in predictions if r['status'] != 'ok'],
                latency=dict(successful_calls=len(latencies), mean_s=statistics.mean(latencies) if latencies else None,
                             p50_s=statistics.median(latencies) if latencies else None,
                             p95_s=latencies[math.ceil(.95 * len(latencies)) - 1] if latencies else None),
                cost=dict(attempted_calls=len(calls), cache_hits=sum(r['cached'] for r in ledger),
                          pages_billed=successful_pages, failed_billing_unknown=unknown,
                          price_per_page_usd=PRICE_PER_PAGE_USD,
                          estimated_usd=successful_pages * PRICE_PER_PAGE_USD,
                          conservative_attempt_estimate_usd=(successful_pages + unknown) * PRICE_PER_PAGE_USD,
                          basis='one crop = one page; planning estimate, not invoice; failed billing unknown'))


def _table(headers, rows) -> list[str]:
    def cell(value):
        text = 'NA' if value is None else f'{value:.6f}' if isinstance(value, float) else str(value)
        return text.replace('|', '\\|').replace('\n', ' ')
    return ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |',
            *['| ' + ' | '.join(cell(v) for v in row) + ' |' for row in rows], '']


def _report(summary: dict) -> str:
    md = ['# Document AI crop run', '',
          'Gold metrics use only supplied gold_text. Polyton-DB 300 is true gold. Missing readings are NA.',
          'All returned text, including trailing LF and neighbour lines, is retained for strict NFD scoring.',
          'Owner 44 and sample 400 have no gold in the fixture builders. Their reader/layer agreement is DIAGNOSTICS only.',
          'Born-digital gold retains the supplied source provenance; a text-layer source is not proof of human review.', '',
          '## Binding', '', '```json', json.dumps(summary['binding'], ensure_ascii=False, sort_keys=True, indent=2), '```', '',
          'Manifest SHA-256: `' + summary['manifest_sha256'] + '`', '', '## Gold metrics by cohort and pass', '']
    md += _table(['cohort', 'pass', 'gold scored/expected', 'missing', 'strict NFD CER', 'edits',
                  'reference atoms', 'mark F1', 'Greek→Latin homoglyphs'],
                 [(name, p['pass_index'], f"{p['gold_scored']}/{p['gold_expected']}", p['missing'],
                   *([p['gold_metrics']['overall'][k] for k in ('cer', 'edits', 'ref_len')]
                     if p['gold_metrics'] else [None] * 3),
                   p['gold_metrics']['mark_f1'] if p['gold_metrics'] else None,
                   p['gold_metrics']['greek_to_latin_homoglyphs'] if p['gold_metrics'] else None)
                  for name, cohort in summary['cohorts'].items() for p in cohort['passes']])
    md += ['## Diacritics versus gold', ''] + _table(
        ['cohort', 'pass', 'mark', 'precision', 'recall', 'F1', 'TP', 'FP', 'FN'],
        [(name, p['pass_index'], mark, *(m[k] for k in ('precision', 'recall', 'f1', 'tp', 'fp', 'fn')))
         for name, cohort in summary['cohorts'].items() for p in cohort['passes'] if p['gold_metrics']
         for mark, m in p['gold_metrics']['marks'].items()])
    md += ['## DIAGNOSTICS — agreement, never accuracy', '',
           'CER treats the named diagnostic text as the reference and preserves whitespace.', ''] + _table(
        ['cohort', 'pass', 'comparison', 'paired lines', 'NFD CER agreement'],
        [(name, p['pass_index'], field, d['lines'], d['nfd_cer_agreement']['cer'] if d['nfd_cer_agreement'] else None)
         for name, cohort in summary['cohorts'].items() for p in cohort['passes']
         for field, d in p['diagnostics'].items()])
    md += ['## Line counts', '', 'A terminal newline does not add a line; internal blank lines count. Expected: one line per crop.', '']
    md += _table(['cohort', 'pass', 'line-count histogram', 'anomalies'],
                 [(name, p['pass_index'], p['line_count_histogram'], len(p['line_count_anomalies']))
                  for name, cohort in summary['cohorts'].items() for p in cohort['passes']])
    md += _table(['cohort', 'pass', 'line ID', 'returned lines'],
                 [(name, p['pass_index'], a['line_id'], a['lines']) for name, cohort in summary['cohorts'].items()
                  for p in cohort['passes'] for a in p['line_count_anomalies']])
    md += ['## Determinism', '', summary['determinism']['definition'],
           'Repeat > 1 forces fresh calls in every pass. Failed readings do not form pairs.', '']
    md += _table(['cohort', 'successful pairs', 'fraction identical', 'mean CER between repeats'],
                 [(name, d['pairs'], d['fraction_identical'], d['mean_cer_between_repeats'])
                  for name, d in [('ALL', summary['determinism']),
                                  *[(name, c['determinism']) for name, c in summary['cohorts'].items()]]])
    md += ['## Latency and cost ledger', '', 'Successful fresh HTTP wall time excludes ADC setup and local writes. Cache hits are excluded.', '']
    md += _table(['successful fresh calls', 'mean seconds', 'p50 seconds', 'p95 seconds'],
                 [tuple(summary['latency'][k] for k in ('successful_calls', 'mean_s', 'p50_s', 'p95_s'))])
    md += ['```json', json.dumps(summary['cost'], indent=2), '```', '',
           'Run ledger: `ledger.jsonl`. Cumulative reader ledger: `receipts/ledger.jsonl`.',
           'Raw service confidence is evidence, not a calibrated probability of correct diacritics.', '', '## Failures', '']
    md += _table(['cohort', 'pass', 'line ID', 'error'],
                 [(r['cohort'], r['pass_index'], r['line_id'], r['error']) for r in summary['failures']])
    return '\n'.join(md) + '\n'


def run_manifest(manifest: str | Path, out: str | Path, *, reader: DocAIReader | None = None,
                 fresh: bool = False, repeat: int = 1, concurrency: int = 4,
                 max_cost_usd: float = 10.0, **reader_options: object) -> dict:
    if any(isinstance(n, bool) or not isinstance(n, int) or n < 1 for n in (repeat, concurrency)):
        raise ValueError('repeat and concurrency must be positive integers')
    rows = load_manifest(manifest)
    if not math.isfinite(max_cost_usd) or max_cost_usd <= 0:
        raise ValueError('max-cost-usd must be finite and positive')
    if len(rows) * repeat * PRICE_PER_PAGE_USD > max_cost_usd:
        raise ValueError('worst-case crop-page cost exceeds max-cost-usd; no calls made')
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    reader = reader or DocAIReader(receipts_dir=out / 'receipts', **reader_options)
    with _lock(out / 'run.lock'):
        ledger_start = reader.ledger_path.stat().st_size if reader.ledger_path.is_file() else 0
        frozen_path = out / 'manifest.jsonl'
        manifest_sha = _sha(Path(manifest).read_bytes())
        frozen_path.write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in rows), encoding='utf-8')
        predictions = []
        with (out / 'predictions.jsonl').open('w', encoding='utf-8') as stream:
            for pass_index in range(1, repeat + 1):
                def read_one(row):
                    result = dict(row, **{'pass': pass_index})
                    try:
                        reading = reader.read(row['crop_path'], fresh=fresh or repeat > 1,
                                              expected_sha256=row['crop_sha256'])
                        result.update(asdict(reading), prediction=reading.text, line_count=len(reading.lines), status='ok')
                    except Exception as error:
                        result.update(prediction=None, status='error', error=str(error))
                    return result
                with ThreadPoolExecutor(max_workers=concurrency) as pool:
                    for prediction in pool.map(read_one, rows):
                        predictions.append(prediction)
                        stream.write(json.dumps(prediction, ensure_ascii=False, sort_keys=True) + '\n')
                        stream.flush()
        ledger = []
        if reader.ledger_path.is_file():
            with reader.ledger_path.open('rb') as stream:
                stream.seek(ledger_start)
                ledger = [json.loads(line) for line in stream if line.strip()]
        (out / 'ledger.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in ledger), encoding='utf-8')
        summary = summarize_run(rows, predictions, ledger, repeat)
        summary.update(binding=reader.binding(), manifest_sha256=manifest_sha,
                       frozen_manifest_sha256=_sha(frozen_path.read_bytes()),
                       complete=not summary['failures'], paths=dict(predictions=str(out / 'predictions.jsonl'),
                       report=str(out / 'REPORT.md'), ledger=str(out / 'ledger.jsonl')))
        _atomic_json(out / 'summary.json', summary)
        (out / 'REPORT.md').write_text(_report(summary), encoding='utf-8')
    return summary


def add_parser(commands) -> None:
    readers = commands.add_parser('readers', help='explicit reader service operations')
    services = readers.add_subparsers(dest='reader_service', required=True)
    docai = services.add_parser('docai', help='receipt-bound Google Document AI REST reader')
    actions = docai.add_subparsers(dest='docai_action', required=True)
    builder = actions.add_parser('manifest', help='build a frozen local fixture manifest; no network')
    builder.add_argument('--fixtures-root', type=Path, default=Path('tests/fixtures'))
    builder.add_argument('--cohorts', nargs='+', choices=COHORTS, default=DEFAULT_COHORTS)
    builder.add_argument('--out', type=Path, required=True)
    runner = actions.add_parser('run', help='submit crop pages, retaining raw responses and diagnostics')
    runner.add_argument('--manifest', type=Path, required=True)
    runner.add_argument('--out', type=Path, required=True)
    runner.add_argument('--fresh', action='store_true')
    runner.add_argument('--repeat', type=int, default=1, help='number of passes; >1 bypasses cache in every pass')
    runner.add_argument('--concurrency', type=int, default=4)
    runner.add_argument('--project', default=os.getenv('GOOGLE_CLOUD_PROJECT', 'ocr-ground-truth-20261008'))
    runner.add_argument('--location', default=os.getenv('DOCUMENTAI_LOCATION', 'eu'))
    runner.add_argument('--processor-id', default=os.getenv('DOCUMENTAI_PROCESSOR_ID', '9a98b7aca3c19561'))
    runner.add_argument('--version', default=os.getenv('DOCUMENTAI_PROCESSOR_VERSION', DEFAULT_VERSION))
    runner.add_argument('--user-project', default=os.getenv('GOOGLE_CLOUD_QUOTA_PROJECT'))
    runner.add_argument('--language-hints', nargs='*', default=['el'])
    runner.add_argument('--no-symbols', action='store_true')
    runner.add_argument('--timeout', type=float, default=60.0)
    runner.add_argument('--max-cost-usd', type=float, default=10.0)


def run(args: argparse.Namespace) -> dict:
    if args.docai_action == 'manifest':
        return build_manifest(args.fixtures_root, args.out, cohorts=args.cohorts)
    return run_manifest(args.manifest, args.out, fresh=args.fresh, repeat=args.repeat,
                        concurrency=args.concurrency, max_cost_usd=args.max_cost_usd,
                        project=args.project, location=args.location, processor_id=args.processor_id,
                        version=args.version, user_project=args.user_project,
                        language_hints=args.language_hints, enable_symbol=not args.no_symbols, timeout=args.timeout)

#!/usr/bin/env python3
"""Offline T19 DocAI line records, assignments, combined corpus and report."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics

from greekocr.harvest.page_reads import _response_geometry
from greekocr.harvest.round1_reads import letter_count, symbol_confidences
from greekocr.harvest.readers import atomic, read_jsonl
from scripts.harvest.round1_reads import sha
from scripts.harvest.round1_reads_rest import REPO, ROOT, OUT, BULK, GOOGLE, D1
from scripts.harvest.montage_controls import git_state, audit_git

SOURCES = ['scripts/harvest/round1_reads_rest.py', 'scripts/harvest/build_round1_reads_rest.py',
           'scripts/harvest/compile_page_reads.py', 'scripts/harvest/validate_round1_reads_rest.py',
           'tests/test_round1_reads_rest.py', 'tests/test_compile_page_reads.py',
           'greekocr/harvest/readers.py', 'greekocr/readers/services/google_docai.py',
           'greekocr/harvest/round1_reads.py', 'greekocr/harvest/page_reads.py']


def flag_rows(rows):
    """Tall uses counted-line median; missing confidence is not a low score."""
    heights = [r['bbox'][3]-r['bbox'][1] for r in rows if r['counted']]
    median = statistics.median(heights) if heights else None
    result = []
    for row in rows:
        flags = set(row.get('flags', [])) - {'short_line', 'tall_box', 'low_confidence'}
        if not row['counted']:
            flags.add('short_line')
        if median is not None and row['bbox'][3]-row['bbox'][1] > 1.7*median:
            flags.add('tall_box')
        if row['confidence'] is not None and row['confidence'] < .89:
            flags.add('low_confidence')
        result.append(dict(row, flags=sorted(flags)))
    return result, median


def read_docai(page, plan):
    parsed_path = GOOGLE / 'parsed/docai' / (page['image_sha256']+'.json')
    value = json.loads(parsed_path.read_text())
    if value['status'] != 'ok':
        return None, dict(status=value['status'], error_class=value.get('error_class'), parsed_path=str(parsed_path.relative_to(REPO)))
    if value['binding'] != plan['binding'] or value['image_sha256'] != sha(REPO / page['image']):
        raise ValueError('cached page response changed: '+page['id'])
    raw_path = Path(value['raw_json_path'])
    cache_path = raw_path.parent / 'cache.json'
    cache = json.loads(cache_path.read_text())
    if (cache['raw_sha256'] != sha(raw_path) or cache['crop_sha256'] != page['image_sha256']
            or cache['binding'] != plan['binding'] or cache['receipt_id'] != value['receipt_id']):
        raise ValueError('raw cache/receipt binding changed')
    return json.loads(raw_path.read_text()), dict(engine='docai', raw_json_path=str(raw_path.relative_to(REPO)),
            raw_sha256=sha(raw_path), cache_path=str(cache_path.relative_to(REPO)), cache_sha256=sha(cache_path),
            parsed_path=str(parsed_path.relative_to(REPO)), parsed_sha256=sha(parsed_path),
            receipt_id=value['receipt_id'], binding=value['binding'], status=value['status'])


def make_rows(page, document, geometry):
    docai = [line for line in geometry['lines'] if line['source'] == 'lines']
    if len(docai) != len(document['pages'][0].get('lines', [])):
        raise ValueError('DocAI line lacks usable geometry')
    custody = symbol_confidences(document)
    rows = []
    for i, (line, conf) in enumerate(zip(docai, custody)):
        text = line['text'].strip()
        letters = letter_count(text)
        counted = letters >= 3
        rows.append(dict(id=f"{page['id']}-l{i+1:04d}", page_id=page['id'], page=page['page'],
                    book=page['book'], book_key=page['key'], year=page['year'], decade=page['decade'], origin=page['origin'],
                    line_number=i+1, docai_index=i, bbox=line['bbox'], image=page['image'], image_sha256=page['image_sha256'],
                    docai_text=text, docai_raw_text=line['text'], vision_text=None, tier=None, label=text if counted else None,
                    counted=counted, letter_count=letters, confidence=conf['mean'], min_confidence=conf['minimum'],
                    symbol_count=len(conf['symbol_indices']), symbol_confidences=conf['symbol_confidences'], symbol_indices=conf['symbol_indices'],
                    confidence_scope='DocAI symbols fully contained in line text anchors',
                    flags=['docai_transform_inverse'] if geometry['coordinate_frame']['converted'] else [],
                    docai_layout_confidence=line.get('confidence')))
    rows, median = flag_rows(rows)
    return rows, docai, custody, median


def cohort_summary(pages, records):
    counted = [r for r in records if r['counted']]
    symbols = [c for r in counted for c in r['symbol_confidences']]
    return dict(pages=len(pages), lines=len(records), counted=len(counted), short_lines=len(records)-len(counted),
                tall=sum('tall_box' in r['flags'] for r in records),
                low_confidence=sum('low_confidence' in r['flags'] for r in records),
                counted_tall=sum('tall_box' in r['flags'] for r in counted),
                counted_low_confidence=sum('low_confidence' in r['flags'] for r in counted),
                mean_confidence=statistics.mean(symbols) if symbols else None,
                symbol_count=sum(r['symbol_count'] for r in counted), confidence_symbol_count=len(symbols))


def evaluate(plan, *, write=False):
    records, audits = [], []
    for page in plan['pages']:
        raw, receipt = read_docai(page, plan)
        rows, geometry, docai, custody, median = [], None, [], [], None
        error = None
        if raw is not None:
            try:
                geometry = _response_geometry('docai', raw, (page['width'], page['height']))
                rows, docai, custody, median = make_rows(page, raw['document'], geometry)
            except ValueError as exc:
                error = str(exc)
        document = raw['document'] if raw else {}
        assignment = dict(schema='t19-page-assignment-1', page=page, readers={'docai': receipt},
                          coordinate_frames={'docai': geometry['coordinate_frame']} if geometry else {},
                          docai_lines=docai, docai_symbol_custody=custody, median_counted_line_height=median,
                          empty_docai_read=raw is not None and not document.get('text', '').strip(),
                          no_docai_line_layouts=raw is not None and not document.get('pages', [{}])[0].get('lines'),
                          lost_page=raw is None or error is not None, geometry_error=error, records=rows)
        path = OUT / 'assignments' / (page['id']+'.json')
        if write:
            atomic(path, assignment)
        elif assignment != json.loads(path.read_text()):
            raise AssertionError('assignment replay mismatch: '+page['id'])
        records.extend(rows)
        audits.append(dict(page_id=page['id'], **cohort_summary([page], rows),
                           lost_page=assignment['lost_page'], geometry_error=error,
                           empty_docai_read=assignment['empty_docai_read'],
                           no_docai_line_layouts=assignment['no_docai_line_layouts'],
                           transformed=bool(geometry and geometry['coordinate_frame']['converted']),
                           coordinate_frame=geometry['coordinate_frame'] if geometry else None))
    summary = dict(schema='t19-docai-only-summary-1', overall=cohort_summary(plan['pages'], records),
                   by_decade={}, by_book={}, by_origin={}, pages=audits,
                   lost_pages=sum(p['lost_page'] for p in audits),
                   empty_pages=sum(p['empty_docai_read'] for p in audits),
                   no_line_pages=sum(p['no_docai_line_layouts'] for p in audits),
                   transformed_pages=sum(p['transformed'] for p in audits))
    for field, target in [('decade', 'by_decade'), ('book', 'by_book'), ('origin', 'by_origin')]:
        page_groups, row_groups = defaultdict(list), defaultdict(list)
        for p in plan['pages']:
            page_groups[str(p[field])].append(p)
        for r in records:
            row_groups[str(r[field])].append(r)
        for key, pages in page_groups.items():
            value = cohort_summary(pages, row_groups[key])
            if field == 'book':
                value.update({k: pages[0][k] for k in ('key', 'title', 'year', 'decade', 'origin')})
            summary[target][key] = value
    return records, summary


def write_jsonl(path, rows):
    path = Path(path)
    temporary = path.with_suffix('.jsonl.tmp')
    with temporary.open('w') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False)+'\n')
    temporary.replace(path)


def build(plan):
    for path, expected in plan['inputs'].items():
        if sha(REPO / path) != expected:
            raise ValueError('frozen input changed: '+path)
    records, summary = evaluate(plan, write=True)
    write_jsonl(OUT / 'records.jsonl', records)
    atomic(OUT / 'summary.json', summary)
    def combined():
        for row in read_jsonl(D1):
            yield dict(row, read_batch='d1')
        for row in records:
            yield dict(row, read_batch='rest')
    write_jsonl(ROOT / 'records_all.jsonl', combined())
    print(json.dumps(summary['overall']))
    return records, summary


def publish(plan):
    """Publish evidence after reads, compilation, offline tests and replay."""
    summary = json.loads((OUT / 'summary.json').read_text())
    cost = json.loads((OUT / 'cost_receipt.json').read_text())
    validation = json.loads((OUT / 'validation.json').read_text())
    if not validation['success']:
        raise ValueError('offline validation has not succeeded')
    import xml.etree.ElementTree as ET
    suites = ET.parse(OUT / 'tests.xml').getroot()
    tests = sum(int(s.get('tests', 0)) for s in suites.iter('testsuite'))
    if any(int(s.get(k, 0)) for s in suites.iter('testsuite') for k in ('failures', 'errors', 'skipped')):
        raise ValueError('tests did not all pass')
    git_audit = audit_git(json.loads((OUT / 'git_before.json').read_text()), git_state())
    atomic(OUT / 'git_audit.json', git_audit)
    failures = [p for p in summary['pages'] if p['lost_page'] or p['empty_docai_read'] or p['no_docai_line_layouts']]
    transforms = [p for p in summary['pages'] if p['transformed']]
    atomic(OUT / 'failure_examples.json', dict(failures=failures, transforms=transforms))
    total = summary['overall']
    lines = ['# T19 — remaining round-1 page reads', '',
             f"Read **{total['pages']:,} pages**, producing **{total['lines']:,} DocAI line layouts**, **{total['counted']:,} counted lines**, **{total['tall']:,} tall boxes** and **{total['low_confidence']:,} low-confidence lines**. DocAI only; zero new Vision calls. All 343 d1 pages were excluded before reading. The scope is 517 accepted T16 pages in 1890–1930 plus all 672 accepted rescued pages, across {len(summary['by_book'])} books.", '',
             'Line records follow provider line order. Text anchors own the symbols; mean/min confidence uses only nonmissing symbol scores, and symbol count includes every anchored symbol. Counted lines contain at least three Unicode letters; short lines remain in the records with null labels. Every counted rest line has `label=docai_text`, `vision_text=null`, `tier=null`. No Vision attachment or agreement fields are added.', '',
             'Flags: `short_line` means fewer than three letters; `tall_box` means native height strictly greater than 1.7 times the page median counted-line height; `low_confidence` means nonmissing mean symbol confidence strictly below 0.89. Tall and low totals include short lines. Cohort mean confidence is symbol-weighted over counted lines. Reported DocAI transforms are composed and inverted on polygon vertices using T15 before native boxes are formed.', '',
             '| Decade | Pages | Lines | Counted | Tall | Low confidence | Mean confidence |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    def metrics(v):
        mean = f"{v['mean_confidence']:.6f}" if v['mean_confidence'] is not None else '—'
        return f"{v['pages']} | {v['lines']} | {v['counted']} | {v['tall']} | {v['low_confidence']} | {mean}"
    for decade, value in sorted(summary['by_decade'].items()):
        lines.append(f'| {decade}s | {metrics(value)} |')
    lines += ['', f"Cost: **{cost['calls_reserved']} reserved DocAI page calls; USD {cost['cost_usd']:.4f} (USD {cost['cost_usd']:.2f} rounded)**, below the USD 3.00 cap. Conservative list-price accounting uses [Google's published Enterprise OCR rate](https://cloud.google.com/products/document-ai/pricing), verified 14 October 2026, without subtracting any free allowance. This is the receipt-bound estimate, not a billing-invoice readback. T19 has its own `google/budget_rest.jsonl` ledger; T17's 686-call ledger remains byte-identical. Reservations precede network requests under image locks; ambiguous prior attempts are refused, and automatic retries are disabled.", '',
              f"Failures: **{summary['lost_pages']} lost pages**, **{summary['empty_pages']} empty reads**, **{summary['no_line_pages']} pages without line layouts**. **{summary['transformed_pages']} pages report image transforms**; all are mapped through the recorded inverse. [Failure and transform details](reads_rest/failure_examples.json) include every affected page.", '',
              'Compiled JPEGs: [rest folder](../harvest_big/round1/reads_rest_compiled/) and regenerated [d1 folder](../harvest_big/round1/reads_d1_compiled/). The reusable [builder](../../../scripts/harvest/compile_page_reads.py) accepts any records file, with optional `--plan` to include empty pages. Each native-size white right panel reproduces the approved discrete lower-quartile fitted type size (sorted index `n//4`), capped initially at 0.95 times median counted height; overflowing lines shrink individually. The approved 9–80 px font limits and 5% width tolerance are preserved. Green boxes, red tall boxes/text below 0.89, numbered sides, 40 px margins/gap, grey rule, JPEG q85. No line crops are cut.', '',
              'Three d1 pages were checked against the pre-existing JPEGs and independently replayed original builder, including tall and low-confidence examples. [Layout equivalence](reads_rest/layout_equivalence.json) records byte hashes, canvas sizes, exact text positions and font sizes. [Visual QA](reads_rest/visual_qa.json) records inspected examples. d1 records remain unchanged; [records_all.jsonl](records_all.jsonl) adds only `read_batch=d1|rest` to the concatenated records.', '',
              'The inspected rescued pages include provider-detected watermark text and transformed axis-aligned boxes that overlap neighbouring printed rows. These provider layouts and their text are retained in provider order. A tall flag is the specified height proxy; the page reader does not remove watermarks or guarantee one physical printed row per layout.', '',
              f"Validation: **{tests} offline tests passed**. [Tests](reads_rest/tests.xml), [complete offline replay](reads_rest/validation.json), [summary](reads_rest/summary.json), [plan](reads_rest/plan.json), [cost](reads_rest/cost_receipt.json), [receipt](reads_rest/receipt.json), [file/hash inventory](reads_rest/inventory.json), [Git metadata audit](reads_rest/git_audit.json). No Git commands or `.git` writes were performed. Owner accuracy review remains separate from provider reads and sample visual checks.", '',
              'A [completed cached rerun](reads_rest/resume_check.json) covered all 1,189 pages with **zero new reservations, zero new DocAI adapter receipts and zero Vision calls**. Both budgets and provider adapter ledgers remained byte-identical across the rerun.', '',
              '| Book | Origin | Pages | Lines | Counted | Tall | Low confidence | Mean confidence |',
              '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for value in sorted(summary['by_book'].values(), key=lambda v: (v['decade'], v['year'], v['key'])):
        title = value['title'].replace('|', '\\|').replace('\n', ' ')
        lines.append(f"| {value['year']} {title} (`{value['key'][:6]}`) | {value['origin']} | {metrics(value)} |")
    last = f"T19: done | pages: {total['pages']} | lines: {total['lines']} | counted: {total['counted']} | tall: {total['tall']} | low_conf: {total['low_confidence']} | calls: {cost['calls_reserved']} | usd: {cost['cost_usd']:.2f} | tests: {tests} passed"
    lines += ['', last]
    (ROOT / 'READS_REST.md').write_text('\n'.join(lines)+'\n')
    artifacts = [ROOT / 'READS_REST.md', ROOT / 'records_all.jsonl', *[OUT / f for f in ('plan.json', 'records.jsonl', 'summary.json', 'cost_receipt.json', 'validation.json', 'layout_equivalence.json', 'visual_qa.json', 'tests.xml', 'git_audit.json', 'resume_check.json', 'failure_examples.json')]]
    receipt = dict(schema='t19-docai-only-receipt-1', generated_utc=datetime.now(timezone.utc).isoformat(),
                   inputs=plan['inputs'], totals=total, cost=cost, tests_passed=tests,
                   failures={k: summary[k] for k in ('lost_pages', 'empty_pages', 'no_line_pages', 'transformed_pages')},
                   validation=validation, sources={p: sha(REPO / p) for p in SOURCES},
                   artifacts={str(p.relative_to(REPO)): sha(p) for p in artifacts})
    atomic(OUT / 'receipt.json', receipt)
    inventory_section = ['<!-- T19:begin -->', '## T19 remaining round-1 DocAI reads (14 October 2026)', '',
                         f"**{total['pages']} unread accepted pages; {total['lines']} provider lines; {total['counted']} counted; {total['tall']} tall; {total['low_confidence']} low confidence.** 517 T16 pages in 1890–1930 plus all 672 rescue pages. DocAI only, {cost['calls_reserved']} unique uncached page receipts; USD {cost['cost_usd']:.4f} conservative list-price cost against USD 3.00. No retries, crop reads, Vision calls or Git mutations.", '',
                         'Artifacts: [READS_REST.md](harvest/round1/READS_REST.md), [records](harvest/round1/reads_rest/records.jsonl), [combined d1/rest records](harvest/round1/records_all.jsonl), [per-page assignments](harvest/round1/reads_rest/assignments/), [summary](harvest/round1/reads_rest/summary.json), [receipt](harvest/round1/reads_rest/receipt.json), [raw/cache/file hashes](harvest/round1/reads_rest/inventory.json), [cost receipt](harvest/round1/reads_rest/cost_receipt.json), [failures/transforms](harvest/round1/reads_rest/failure_examples.json). Raw responses remain under ignored `docs/harvest/harvest_big/round1/google/`.', '',
                         'The reusable `scripts/harvest/compile_page_reads.py` rebuilds the approved native-page diptychs from any records file. Every rest page is in ignored `reads_rest_compiled/<decade>s/[RESCUED_]<year>_<title40>_<id6>/pNNNN.jpg`; all 343 d1 JPEGs were regenerated. [Three-page byte/layout equivalence](harvest/round1/reads_rest/layout_equivalence.json) confirms exact original JPEG bytes and zero text-position delta, including tall/low-confidence examples. [Sample visual QA](harvest/round1/reads_rest/visual_qa.json) is separate from owner accuracy review.', '',
                         f"**{tests} offline tests passed**. [Replay validation](harvest/round1/reads_rest/validation.json) reconciles the entire scope, assignments, raw/cache bindings, unique provider receipts, preserved d1 fields, batch tags and all compiled hashes/dimensions/text positions. T17 records, shared budget and Vision adapter ledger remain byte-identical. [Git metadata audit](harvest/round1/reads_rest/git_audit.json) records any concurrent activity; this task made no `.git` writes.", '',
                         '| Source file | Purpose | SHA-256 |', '| --- | --- | --- |']
    for source in SOURCES[:6]:
        inventory_section.append(f'| `{source}` | T19 offline records, explicit reader controls, rendering or validation | `{sha(REPO / source)}` |')
    inventory_section += ['', '<!-- T19:end -->']
    inventory_path = REPO / 'docs/INVENTORY.md'
    text = inventory_path.read_text()
    start, end = '<!-- T19:begin -->', '<!-- T19:end -->'
    if start in text:
        a, remainder = text.split(start, 1)
        _, b = remainder.split(end, 1)
        text = a + '\n'.join(inventory_section) + b
    else:
        text += '\n\n' + '\n'.join(inventory_section) + '\n'
    inventory_path.write_text(text)
    paths = set(artifacts + [OUT / 'receipt.json', inventory_path])
    # Publication stdout can still be appended after the inventory is written.
    # Exclude that active log, alongside the inventory's own recursive digest.
    excluded = {'inventory.json', 'publish.log'}
    paths.update(p for p in OUT.rglob('*') if p.is_file() and p.name not in excluded)
    paths.update(REPO / p for p in SOURCES)
    paths.update(REPO / p for p in plan['inputs'])
    for folder in ('reads_rest_compiled', 'reads_d1_compiled', 'reads_rest_layout_reference'):
        paths.update(p for p in (BULK / folder).rglob('*') if p.is_file())
    for page in plan['pages']:
        assignment = json.loads((OUT / 'assignments' / (page['id']+'.json')).read_text())
        r = assignment['readers']['docai']
        paths.update(REPO / r[k] for k in ('raw_json_path', 'cache_path', 'parsed_path') if r.get(k))
        paths.add(REPO / page['image'])
    paths.update(p for p in [GOOGLE / 'budget_rest.jsonl', GOOGLE / 'budget_rest.state.json',
                            GOOGLE / 'docai/ledger.jsonl', GOOGLE / 'budget.jsonl',
                            GOOGLE / 'vision/adapter_receipts/ledger.jsonl'] if p.exists())
    inventory = dict(schema='t19-file-hash-inventory-1', file_count=len(paths), excluded_self_mutating_files=sorted(excluded),
                     files=[dict(path=str(p.relative_to(REPO)), bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(paths)])
    atomic(OUT / 'inventory.json', inventory)
    print(last)
    return receipt

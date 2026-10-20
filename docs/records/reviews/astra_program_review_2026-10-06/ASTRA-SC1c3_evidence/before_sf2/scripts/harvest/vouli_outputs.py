"""Offline records, admission/crops, complete validation and publication for T21."""
from __future__ import annotations

from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import io
import json
import multiprocessing
from pathlib import Path
import random
import xml.etree.ElementTree as ET

from PIL import Image

from scripts.harvest.vouli import (REPO, OUT, BULK, GOOGLE, SOURCE, ADMISSION_SHA,
    admission, sha, relative, atomic, read_jsonl, write_jsonl, make_rows,
    cohort_summary, _response_geometry, contact_sheets, stats, compiler,
    select_holdout, select_pages, round1, VouliReaders)

REASONS = admission.REASONS + ('crop_geometry',)


def raw_read(page, plan):
    parsed_path = GOOGLE / 'parsed/docai' / (page['image_sha256'] + '.json')
    parsed = json.loads(parsed_path.read_text())
    if parsed['status'] != 'ok':
        raise ValueError('unsuccessful parsed read: ' + page['id'])
    if parsed['binding'] != plan['binding'] or parsed['image_sha256'] != sha(REPO / page['image']):
        raise ValueError('parsed image/binding changed')
    raw_path = Path(parsed['raw_json_path'])
    cache_path = raw_path.parent / 'cache.json'
    cache = json.loads(cache_path.read_text())
    if (cache['raw_sha256'] != sha(raw_path) or cache['crop_sha256'] != page['image_sha256']
        or cache['binding'] != plan['binding'] or cache['receipt_id'] != parsed['receipt_id']):
        raise ValueError('raw response custody changed')
    return json.loads(raw_path.read_text()), dict(status='ok', receipt_id=parsed['receipt_id'],
        raw_json_path=relative(raw_path), raw_sha256=sha(raw_path),
        cache_path=relative(cache_path), cache_sha256=sha(cache_path),
        parsed_path=relative(parsed_path), parsed_sha256=sha(parsed_path))


def read_records(plan, write=False):
    records, audits = [], []
    for i, page in enumerate(plan['pages'], 1):
        raw, receipt = raw_read(page, plan)
        geometry, rows, docai, custody, median, error = None, [], [], [], None, None
        try:
            geometry = _response_geometry('docai', raw, (page['width'], page['height']))
            rows, docai, custody, median = make_rows(page, raw['document'], geometry)
        except ValueError as exc:
            # T19 retains the successful raw response and reports a lost page;
            # an unusable coordinate frame must never fabricate native boxes.
            error = str(exc)
        for r in rows:
            r.update(source=SOURCE, licence=page['licence'], source_url=page['source_url'],
                     attribution=page['attribution'], read_batch='vouli')
        assignment = dict(schema='t21-page-assignment-1', page=page, reader=receipt,
            coordinate_frame=geometry['coordinate_frame'] if geometry else None, docai_lines=docai,
            docai_symbol_custody=custody, median_counted_line_height=median,
            lost_page=error is not None, geometry_error=error, records=rows)
        path = OUT / 'assignments' / (page['id'] + '.json')
        if write:
            atomic(path, assignment)
        elif assignment != json.loads(path.read_text()):
            raise AssertionError('assignment replay changed: ' + page['id'])
        records.extend(rows)
        audits.append(dict(page_id=page['id'], **cohort_summary([page], rows),
            empty=not raw['document'].get('text', '').strip(),
            no_line_layouts=not raw['document'].get('pages', [{}])[0].get('lines'),
            lost_page=error is not None, geometry_error=error,
            transformed=bool(geometry and geometry['coordinate_frame']['converted']),
            coordinate_frame=geometry['coordinate_frame'] if geometry else None, receipt=receipt))
        if i % 100 == 0:
            print(f'records replay {i}/{len(plan["pages"])}', flush=True)
    return records, dict(schema='t21-read-summary-1', overall=cohort_summary(plan['pages'], records),
        pages=audits, empty_pages=sum(p['empty'] for p in audits),
        no_line_pages=sum(p['no_line_layouts'] for p in audits),
        transformed_pages=sum(p['transformed'] for p in audits), lost_pages=sum(p['lost_page'] for p in audits))


def admit_records(records, held, round1_records):
    """Reuse T20 rules unchanged, then O5 against both waves' hold-out labels."""
    quality = admission.page_quality(records)
    splits = {b['book_key']: b['split'] for b in held}
    candidates, rejected = [], []
    for r in records:
        good, cls, reasons, label = admission.admit(dict(r, bad_page=quality[r['page_id']]['bad_page']))
        if good:
            candidates.append(dict(id=r['id'], page_id=r['page_id'], book_key=r['book_key'],
                year=r['year'], decade=r['decade'], split=splits.get(r['book_key'], 'train'),
                script_class=cls, label=label, has_spacing_mark=admission.has_spacing_mark(label),
                confidence=r['confidence'], bbox=r['bbox'], source=SOURCE, licence=r['licence'],
                source_url=r['source_url'], attribution=r['attribution'], read_batch='vouli',
                docai_text=r['docai_text']))
        else:
            rejected.append(dict(id=r['id'], reasons=reasons, docai_text=r['docai_text']))
    # External held-out labels participate in the exact same T20 pure O5 function.
    external = [dict(r) for r in round1_records if r['split'] in ('dev', 'test')]
    kept, o5 = admission.apply_holdout_labels(candidates + external)
    kept = [r for r in kept if r['source'] == SOURCE]
    rejected.extend(o5)
    wave_labels = {r['label'] for r in kept if r['split'] in ('dev', 'test')}
    # Do not rewrite frozen round 1. Its newly colliding train rows are excluded
    # in the combined-training overlay that downstream consumers must use.
    round1_exclusions = [dict(id=r['id'], source=r['source'], reason='label_in_holdout',
        label=r['label']) for r in round1_records if r['split'] == 'train'
        and admission.normalize_label(r['label']) in wave_labels]
    return kept, sorted(rejected, key=lambda r: r['id']), quality, len(candidates), round1_exclusions


def apply_source_cap(admitted, round1_records, round1_exclusions):
    """Separate collection-mix policy: at most 40% Vouli in polytonic train.

    Preserve all quality-admitted crops and classes. Excess train lines receive
    pool exclusions, not invented failures of the unchanged admission module.
    """
    excluded = {r['id'] for r in round1_exclusions}
    other = [r for r in round1_records if r['split'] == 'train'
             and r['script_class'] == 'greek_poly' and r['id'] not in excluded]
    wave = [r for r in admitted if r['split'] == 'train' and r['script_class'] == 'greek_poly']
    # v / (v + r) <= 2/5 is exactly 3*v <= 2*r.
    maximum = 2 * len(other) // 3
    chosen = sorted(wave, key=lambda r: sha_seed(r['id']))[:maximum]
    chosen_ids = {r['id'] for r in chosen}
    cap_exclusions = [dict(id=r['id'], source=SOURCE, reason='per_source_cap', label=r['label'])
                      for r in wave if r['id'] not in chosen_ids]
    remaining = min(len(wave), maximum)
    return cap_exclusions, dict(limit=.4, round1_poly_train=len(other),
        vouli_poly_train_admitted=len(wave), combined_poly_train_admitted=len(other) + len(wave),
        admitted_share=len(wave) / (len(other) + len(wave)) if other or wave else 0,
        vouli_poly_train_pool=remaining, combined_poly_train_pool=len(other) + remaining,
        pool_share=remaining / (len(other) + remaining) if other or remaining else 0,
        excluded=len(cap_exclusions), passed=3 * remaining <= 2 * len(other),
        policy='quality-admitted rows retained; train_pool.jsonl applies O5 overlay and seeded source-cap exclusions')


def sha_seed(ident):
    import hashlib
    return hashlib.sha256(f'20261015:{ident}'.encode()).hexdigest()


def compiled_path(page):
    title = compiler.slug(page['title']) or 'untitled'
    year = page['year'] if page['year'] is not None else 'unknown'
    return Path(f"{year}_{title}_{page['key'][:6]}") / f"p{page['page']:04d}.jpg"


def pool_entry(row):
    return dict({k: row[k] for k in ('id', 'source', 'script_class', 'label', 'crop_path',
        'crop_sha256', 'book_key', 'read_batch', 'licence')}, split='train',
        admission_record_file='docs/harvest/vouli/admitted.jsonl' if row['source'] == SOURCE
        else 'docs/harvest/round1/admitted.jsonl')


def plan_crops(records, admitted, page_sizes):
    """An uncuttable native box is an extraction failure, not a repaired rule.

    Quality-admitted hold-out labels remain reserved by O5 even when their crop
    cannot be extracted. Nothing in the frozen T20 module is changed.
    """
    pages, candidates = defaultdict(list), {r['id'] for r in admitted}
    for r in records:
        pages[r['page_id']].append(r)
    geometry, failures, rejected = {}, [], []
    for pid, rows in pages.items():
        neighbours = admission.spatial_neighbours(rows)
        for r in rows:
            if r['id'] not in candidates:
                continue
            try:
                geometry[r['id']] = admission.crop_geometry(r['bbox'], *neighbours[r['id']], page_sizes[pid])
            except ValueError as exc:
                failures.append(dict(id=r['id'], page_id=pid, bbox=r['bbox'],
                    neighbours=neighbours[r['id']], page_size=page_sizes[pid], error=str(exc)))
                rejected.append(dict(id=r['id'], reasons=['crop_geometry'], docai_text=r['docai_text']))
    kept = [r for r in admitted if r['id'] in geometry]
    return kept, rejected, failures, geometry


def build(plan):
    records, read_summary = read_records(plan, write=True)
    write_jsonl(OUT / 'records.jsonl', records)
    atomic(OUT / 'read_summary.json', read_summary)
    held = json.loads((OUT / 'holdout_books.json').read_text())
    old = read_jsonl(round1.OUT / 'admitted.jsonl')
    admitted, rejected, quality, before, old_exclusions = admit_records(records, held, old)
    sizes = {p['id']: (p['width'], p['height']) for p in plan['pages']}
    admitted, crop_rejected, crop_failures, geometries = plan_crops(records, admitted, sizes)
    rejected = sorted(rejected + crop_rejected, key=lambda r: r['id'])
    atomic(OUT / 'crop_failures.json', crop_failures)
    cap_exclusions, cap = apply_source_cap(admitted, old, old_exclusions)
    excluded_ids = {r['id'] for r in old_exclusions + cap_exclusions}
    pool = [pool_entry(r)
            for r in old if r['split'] == 'train' and r['id'] not in excluded_ids]
    pages, kept = defaultdict(list), {r['id']: r for r in admitted}
    for r in records:
        pages[r['page_id']].append(r)
    widths, heights = [], []
    for i, (pid, rows) in enumerate(pages.items(), 1):
        selected = [r for r in rows if r['id'] in kept]
        if not selected:
            continue
        if sha(REPO / rows[0]['image']) != rows[0]['image_sha256']:
            raise ValueError('crop page changed')
        with Image.open(REPO / rows[0]['image']) as image:
            if image.mode != 'L':
                raise ValueError('native grayscale required')
            image.load()
            for r in selected:
                a = kept[r['id']]
                bounds, trimmed = geometries[r['id']]
                crop = image.crop(tuple(bounds))
                path = BULK / 'crops' / r['book_key'] / f"p{r['page']:06d}-l{r['line_number']:04d}.png"
                path.parent.mkdir(parents=True, exist_ok=True)
                stream = io.BytesIO()
                crop.save(stream, format='PNG', compress_level=3)
                data = stream.getvalue()
                import hashlib
                digest = hashlib.sha256(data).hexdigest()
                if not path.exists() or sha(path) != digest:
                    path.write_bytes(data)
                a.update(crop_path=relative(path), crop_sha256=digest, crop_width=crop.width,
                         crop_height=crop.height, crop_bbox=bounds, trimmed=trimmed,
                         train_pool_eligible=a['split'] == 'train' and a['id'] not in excluded_ids)
                a.pop('docai_text')
                widths.append(crop.width)
                heights.append(crop.height)
                if a['train_pool_eligible']:
                    pool.append(pool_entry(a))
        if i % 100 == 0:
            print(f'crops {i}/{len(pages)}; {len(widths)} written', flush=True)
    sheets = contact_sheets(REPO, admitted, BULK / 'admission_sheet')
    reasons = Counter(reason for r in rejected for reason in r['reasons'])
    summary = dict(schema='t21-admission-1', input_lines=len(records), pages=len(pages),
        admitted_before_o5=before, admitted=len(admitted), rejected=len(rejected), crops=len(admitted),
        trimmed=sum(r['trimmed'] for r in admitted),
        has_spacing_mark=sum(r['has_spacing_mark'] for r in admitted),
        per_reason={r: reasons[r] for r in REASONS},
        per_split=dict(Counter(r['split'] for r in admitted)),
        per_class={c: sum(r['script_class'] == c for r in admitted) for c in admission.CLASSES},
        per_class_split={c: {s: sum(r['script_class'] == c and r['split'] == s for r in admitted)
                           for s in ('train', 'dev', 'test')} for c in admission.CLASSES},
        per_decade={str(d): dict(Counter(r['split'] for r in admitted if r['decade'] == d))
                    for d in sorted({r['decade'] for r in records}, key=lambda d: -1 if d is None else d)},
        label_in_holdout=reasons['label_in_holdout'],
        crop_failures=len(crop_failures),
        bad_pages=[dict(page_id=pid, **q) for pid, q in quality.items() if q['bad_page']],
        contact_sheets=sheets, crop_size_stats=dict(width=stats(widths), height=stats(heights)),
        holdout_policy=dict(seed=20261015, books=16, dev=4, test=12,
                            selection='uniform seeded draw from sorted 107 books before reads'),
        per_source_cap=cap, round1_train_label_exclusions=len(old_exclusions),
        train_pool_vouli=sum(r['source'] == SOURCE for r in pool),
        train_pool_total=len(pool), admission_module_sha256=ADMISSION_SHA)
    write_jsonl(OUT / 'admitted.jsonl', admitted)
    write_jsonl(OUT / 'rejected.jsonl', rejected)
    write_jsonl(OUT / 'train_pool_exclusions.jsonl', old_exclusions + cap_exclusions)
    write_jsonl(OUT / 'train_pool.jsonl', pool)
    atomic(OUT / 'admission_summary.json', summary)
    compiled = compiler.compile_records(OUT / 'records.jsonl', BULK / 'compiled',
        pages=plan['pages'], books={}, path_builder=compiled_path, workers=3)
    # The fixed 0.89 cut is not the bottom five percent of every new wave.
    (BULK / 'compiled/README.txt').write_text(compiler.README.replace(' (the weakest 5%)', ''))
    print(json.dumps(dict(lines=len(records), admitted=len(admitted), compiled=compiled['page_count'], cap=cap)), flush=True)
    return summary


def validate_compiled_task(task):
    import hashlib
    p, rows, entry = task
    assert entry['path'] == str(compiled_path(p))
    path = BULK / 'compiled' / entry['path']
    assert sha(path) == entry['jpeg_sha256']
    with Image.open(REPO / p['image']) as image:
        canvas, layout = compiler.render_page(image, rows)
    assert hashlib.sha256(canvas.tobytes()).hexdigest() == entry['raster_sha256']
    assert all(entry[k] == v for k, v in layout.items())
    with Image.open(path) as im:
        assert im.size == canvas.size
    return p['id']


def validate(plan):
    """All raw/parsed responses, line decisions, crops/pixels and compiled pages."""
    books = json.loads((OUT / 'books.json').read_text())
    manifest = json.loads((OUT / 'manifest.json').read_text())
    held = json.loads((OUT / 'holdout_books.json').read_text())
    assert held == select_holdout(books)
    assert json.loads((OUT / 'gate_equivalence.json').read_text())['passed']
    assert Counter(b['split'] for b in held) == {'dev': 4, 'test': 12}
    assert len(books) == 107 and len(manifest) == sum(b['page_count'] for b in books) == 1126
    assert plan['pages'] == select_pages(manifest, plan['already_read_hashes'])
    for b in books:
        assert sha(REPO / b['pdf']) == b['book']
        assert {p['page'] for p in manifest if p['book'] == b['book']} == set(range(1, b['page_count'] + 1))
    limits = json.loads((round1.OUT / 'selection.json').read_text())['quality_limits']
    for p in manifest:
        assert sha(REPO / p['image']) == p['image_sha256'] == p['gate']['image_sha256']
        g = p['gate']
        assert g['gate_source_sha256'] == round1.GATE_SHA
        flags, ratio = round1.quality_flags(g['features'], g['suppression_reasons'], g['lines'], limits)
        assert flags == g['supplemental_quality_flags'] and ratio == g['faint_suppression_share']
        assert g['flags'] == g['pilot_gate']['flags'] + flags
        assert g['accepted'] == (g['pilot_gate']['accepted'] and not flags)
        with Image.open(REPO / p['image']) as im:
            assert im.format == 'PNG' and im.mode == 'L' and im.size == (p['width'], p['height'])
    budget = read_jsonl(GOOGLE / 'budget.jsonl')
    ledger = read_jsonl(GOOGLE / 'docai/ledger.jsonl')
    assert len(budget) == len({r['key'] for r in budget}) == plan['max_calls']
    assert {r['key'] for r in budget} == {p['image_sha256'] for p in plan['pages']}
    assert all(r['engine'] == 'docai' and r['micro_usd'] == 1500 for r in budget)
    assert all(r['status'] == 'ok' and not r['cached'] for r in ledger)
    assert len(ledger) == len({r['crop_sha256'] for r in ledger}) == len(budget)
    assert len(budget) * 1500 <= 2_500_000
    cost = json.loads((OUT / 'cost_receipt.json').read_text())
    assert cost['calls_reserved'] == len(budget) and cost['cost_usd'] == len(budget) * .0015
    assert json.loads((GOOGLE / 'budget.state.json').read_text())['calls'] == len(budget)
    records, read_summary = read_records(plan)
    assert records == read_jsonl(OUT / 'records.jsonl')
    assert read_summary == json.loads((OUT / 'read_summary.json').read_text())
    old = read_jsonl(round1.OUT / 'admitted.jsonl')
    expected, rejected, quality, before, old_exclusions = admit_records(records, held, old)
    sizes = {p['id']: (p['width'], p['height']) for p in plan['pages']}
    expected, crop_rejected, crop_failures, geometries = plan_crops(records, expected, sizes)
    rejected = sorted(rejected + crop_rejected, key=lambda r: r['id'])
    # JSON encodes tuples as lists; canonical round-trip reconciles the receipt.
    assert json.loads(json.dumps(crop_failures)) == json.loads((OUT / 'crop_failures.json').read_text())
    cap_exclusions, cap = apply_source_cap(expected, old, old_exclusions)
    actual = read_jsonl(OUT / 'admitted.jsonl')
    assert rejected == read_jsonl(OUT / 'rejected.jsonl')
    assert len(actual) + len(rejected) == len(records)
    assert len({r['id'] for r in records}) == len(records)
    assert [r['id'] for r in actual] == [r['id'] for r in expected]
    actual_map = {r['id']: r for r in actual}
    for a, e in zip(actual, expected):
        assert all(a[k] == v for k, v in e.items() if k != 'docai_text')
    pool = read_jsonl(OUT / 'train_pool.jsonl')
    exclusions = old_exclusions + cap_exclusions
    assert exclusions == read_jsonl(OUT / 'train_pool_exclusions.jsonl')
    excluded_ids = {r['id'] for r in exclusions}
    train_rows = [r for r in old + actual if r['split'] == 'train' and r['id'] not in excluded_ids]
    assert {r['id'] for r in pool} == {r['id'] for r in train_rows}
    assert pool == [pool_entry(r) for r in train_rows]
    held_labels = {r['label'] for r in old + actual if r['split'] in ('dev', 'test')}
    assert not held_labels & {r['label'] for r in pool}
    assert cap['passed'] and cap['pool_share'] <= .4
    summary = json.loads((OUT / 'admission_summary.json').read_text())
    assert summary['per_source_cap'] == cap
    assert summary['per_class_split'] == {c: {s: sum(r['script_class'] == c and r['split'] == s for r in actual)
        for s in ('train', 'dev', 'test')} for c in admission.CLASSES}
    assert summary['per_reason'] == {reason: sum(reason in r['reasons'] for r in rejected) for reason in REASONS}
    pages = defaultdict(list)
    for r in records:
        pages[r['page_id']].append(r)
    crops = 0
    for i, (pid, rows) in enumerate(pages.items(), 1):
        neighbours = admission.spatial_neighbours(rows)
        with Image.open(REPO / rows[0]['image']) as page:
            page.load()
            for r in rows:
                if r['id'] not in actual_map:
                    continue
                a = actual_map[r['id']]
                bounds, trimmed = admission.crop_geometry(r['bbox'], *neighbours[r['id']], page.size)
                assert bounds == a['crop_bbox'] and trimmed == a['trimmed']
                assert sha(REPO / a['crop_path']) == a['crop_sha256']
                assert Path(a['crop_path']).parent.name == r['book_key']
                assert Path(a['crop_path']).name == f"p{r['page']:06d}-l{r['line_number']:04d}.png"
                with Image.open(REPO / a['crop_path']) as crop:
                    assert crop.mode == 'L' and crop.format == 'PNG'
                    assert crop.size == (a['crop_width'], a['crop_height'])
                    assert crop.tobytes() == page.crop(tuple(bounds)).tobytes()
                assert a['train_pool_eligible'] == (a['split'] == 'train' and a['id'] not in excluded_ids)
                crops += 1
        if i % 100 == 0:
            print(f'validated {i}/{len(pages)} pages, {crops} native crops', flush=True)
    assert crops == len(actual) == summary['crops']
    compiled = json.loads((BULK / 'compiled/compile_receipt.json').read_text())
    assert compiled['builder_sha256'] == sha(Path(compiler.__file__))
    assert compiled['records_sha256'] == sha(OUT / 'records.jsonl')
    assert len(compiled['pages']) == plan['page_count']
    compiled_map = {r['page_id']: r for r in compiled['pages']}
    # Replay every final compiled raster; JPEG bytes/dimensions are checked too.
    tasks = [(p, pages.get(p['id'], []), compiled_map[p['id']]) for p in plan['pages']]
    with ProcessPoolExecutor(max_workers=3, mp_context=multiprocessing.get_context('spawn')) as process_pool:
        for i, _ in enumerate(process_pool.map(validate_compiled_task, tasks, chunksize=1), 1):
            if i % 100 == 0:
                print(f'validated compiled {i}/{plan["page_count"]}', flush=True)
    for cls, sheet in summary['contact_sheets'].items():
        assert sha(REPO / sheet['path']) == sheet['sha256']
        assert len(sheet['ids']) == len(set(sheet['ids'])) == min(60, summary['per_class'][cls])
        assert all(actual_map[ident]['script_class'] == cls for ident in sheet['ids'])
        with Image.open(REPO / sheet['path']) as im:
            im.load()
            assert im.size == (sheet['width'], sheet['height'])
    assert sha(REPO / 'greekocr/harvest/admission.py') == ADMISSION_SHA
    before_hashes = {relative(p): sha(p) for p in (GOOGLE / 'budget.jsonl', GOOGLE / 'budget.state.json', GOOGLE / 'docai/ledger.jsonl')}
    readers = VouliReaders(plan)
    def forbidden(*args, **kwargs):
        raise AssertionError('offline cache replay must not invoke a provider')
    readers.docai.read = forbidden
    for p in plan['pages']:
        assert readers.call('docai', REPO / p['image'])['status'] == 'ok'
    after_hashes = {p: sha(REPO / p) for p in before_hashes}
    assert before_hashes == after_hashes
    atomic(OUT / 'resume_check.json', dict(pages_replayed=plan['page_count'], new_calls=0,
        new_reservations=0, provider_method_forbidden=True, unchanged_ledger_hashes=before_hashes))
    result = dict(schema='t21-validation-1', passed=True, pages_rendered=len(manifest),
        pages_read=len(plan['pages']), unique_calls=len(budget), lines=len(records), admitted=len(actual),
        crops_checked=crops, native_pixels_checked=crops, compiled_rasters_replayed=len(compiled['pages']),
        train_holdout_equal_labels=0, holdout_books=16, per_source_cap=cap)
    atomic(OUT / 'validation.json', result)
    print(json.dumps(result), flush=True)
    return result


def publish(plan):
    from zoneinfo import ZoneInfo
    validation = json.loads((OUT / 'validation.json').read_text())
    assert validation['passed']
    suites = list(ET.parse(OUT / 'tests.xml').getroot().iter('testsuite'))
    assert suites and not any(int(s.get(k, 0)) for s in suites for k in ('failures', 'errors', 'skipped'))
    tests = sum(int(s.get('tests', 0)) for s in suites)
    summary = json.loads((OUT / 'admission_summary.json').read_text())
    reads = json.loads((OUT / 'read_summary.json').read_text())
    cost = json.loads((OUT / 'cost_receipt.json').read_text())
    books = json.loads((OUT / 'books.json').read_text())
    manifest = json.loads((OUT / 'manifest.json').read_text())
    records = read_jsonl(OUT / 'records.jsonl')
    bybook = defaultdict(list)
    for r in records:
        bybook[r['book_key']].append(r)
    admitted = read_jsonl(OUT / 'admitted.jsonl')
    admitted_books = Counter(r['book_key'] for r in admitted)
    held = {r['book_key']: r['split'] for r in json.loads((OUT / 'holdout_books.json').read_text())}
    gate_reasons = Counter(f for p in manifest for f in p['gate']['flags'])
    failures = dict(read_failures=[dict(page_id=p['page_id'], error=p['geometry_error'])
                                  for p in reads['pages'] if p['lost_page']],
        empty_pages=[p['page_id'] for p in reads['pages'] if p['empty']],
        no_line_pages=[p['page_id'] for p in reads['pages'] if p['no_line_layouts']],
        transforms=[dict(page_id=p['page_id'], coordinate_frame=p['coordinate_frame'])
                    for p in reads['pages'] if p['transformed']], bad_pages=summary['bad_pages'],
        crop_failures=json.loads((OUT / 'crop_failures.json').read_text()))
    atomic(OUT / 'failures.json', failures)
    before = json.loads((OUT / 'git_before.json').read_text())
    after = round1.git_snapshot()
    main_paths = ('HEAD', 'index', 'refs/heads/main', 'packed-refs',
                  'logs/HEAD', 'logs/refs/heads/main', 'config')
    git_audit = dict(unchanged=before == after,
        main_worktree_unchanged=all(before.get(p) == after.get(p) for p in main_paths),
        main_metadata={p: dict(before=before.get(p), after=after.get(p)) for p in main_paths},
        changed=[p for p in sorted(set(before) | set(after)) if before.get(p) != after.get(p)],
        note='No Git mutation commands issued. Shared .git also contains other worktrees and their branch/object activity; main bookkeeping is compared separately.')
    atomic(OUT / 'git_audit.json', git_audit)
    cap = summary['per_source_cap']
    years = [b['year'] for b in books if b['year'] is not None]
    splits = summary['per_split']
    last = (f"T21: done | pages: {plan['pages_rendered']}/{plan['pages_accepted']}/{plan['page_count']} | "
            f"lines: {summary['input_lines']} | admitted: {summary['admitted']} | poly: {summary['per_class']['greek_poly']} | "
            f"train: {splits.get('train', 0)} | dev: {splits.get('dev', 0)} | test: {splits.get('test', 0)} | "
            f"usd: {cost['cost_usd']:.2f} | tests: {tests} passed")
    lines = ['# T21 — Wave 1 Vouli page reads and admitted crops', '',
        f"**{plan['pages_rendered']:,} pages rendered; {plan['pages_accepted']:,} accepted and "
        f"{plan['pages_rendered'] - plan['pages_accepted']:,} rejected by the page gate; "
        f"{plan['page_count']:,} page records read using {plan['max_calls']:,} unique image calls. {len(records):,} DocAI lines; "
        f"{summary['admitted']:,} admitted; {summary['rejected']:,} rejected; {summary['crops']:,} native grey PNG crops.**", '',
        f"All 107 receipted PDFs were processed, every page from 1 through each book's recorded count. "
        f"The input is broader than the brief's 1850s description: recorded years span **{min(years)}–{max(years)}**, "
        f"with **{sum(b['year'] is None for b in books)} undated books**. Actual years and nulls are preserved; "
        f"`source={SOURCE}` is the requested batch identifier, not a verified date assertion. "
        "CC-BY-4.0, each source URL and each attribution come unchanged from local sources.json; source sites were not fetched.", '',
        'Rendering: pypdfium2, scale 200/72, grayscale L PNG, compress_level=1, identical to round 1. '
        f"Frozen pilot gate SHA-256 `{round1.GATE_SHA}`; the original exported stack and model hashes accompany every page. "
        'Photometric guards call the unchanged round-1 feature definitions and quality_flags with selection.json limits. '
        'Two-page spreads have no extra rejection or splitting rule; an accepted spread is one full-page DocAI request. '
        'No owner-look filter was applied, as authorized on 15 October.', '',
        f"{len(plan['shared_image_groups'])} shared-image groups occur across accepted PDF pages. "
        "Each identical image SHA has one response, reused offline under each book/page identity with its own metadata. "
        "The groups are listed in plan.json; no shared page image is read or billed twice.", '',
        'Quality limits: `' + json.dumps(plan['quality_limits']) + '`', '',
        '| Page-gate flag | Pages (overlapping) |', '| --- | ---: |']
    lines += [f'| {reason} | {n:,} |' for reason, n in sorted(gate_reasons.items())]
    lines += ['', 'DocAI uses the T19 project, EU processor, pinned version, Greek hint, symbol option and ADC binding. '
        'Line layouts remain in provider order; T15 composes and inverts reported transforms before native bboxes are formed. '
        'Mean/min confidence uses symbols fully contained in each line anchor. Reader flags retain T19 semantics: '
        '<3 letters for short_line; height >1.7 × counted-line median for tall_box; mean <0.89 for low_confidence. '
        'The separate unchanged T20 admission step requires ≥10 letters and applies every rule including bad_page.', '',
        '| Class | Train admitted | Dev | Test | Total |', '| --- | ---: | ---: | ---: | ---: |']
    for cls in admission.CLASSES:
        c = summary['per_class_split'][cls]
        lines.append(f"| {cls} | {c['train']:,} | {c['dev']:,} | {c['test']:,} | {summary['per_class'][cls]:,} |")
    lines += [f"| **Total** | **{splits.get('train', 0):,}** | **{splits.get('dev', 0):,}** | **{splits.get('test', 0):,}** | **{summary['admitted']:,}** |", '',
        '| Admission rejection reason | Lines (overlapping) |', '| --- | ---: |']
    lines += [f'| {reason} | {n:,} |' for reason, n in summary['per_reason'].items()]
    lines += ['', f"Hold-out: 16 of 107 books (14.95%), seeded draw 20261015 from sorted full input scope, frozen before reads: "
        f"12 test / 4 dev. O5 removed **{summary['label_in_holdout']:,}** new train lines equal to round-1 or Vouli dev/test labels. "
        f"The new hold-out also matches **{summary['round1_train_label_exclusions']:,}** old round-1 train rows: "
        "[train_pool_exclusions.jsonl](train_pool_exclusions.jsonl) excludes these from the combined pool without rewriting the frozen round-1 artifacts. "
        "[train_pool.jsonl](train_pool.jsonl) is the combined training input for this wave; all equal hold-out labels are absent.", '',
        f"**Per-source cap:** before source balancing, Vouli supplies {cap['vouli_poly_train_admitted']:,} / "
        f"{cap['combined_poly_train_admitted']:,} = **{cap['admitted_share']:.2%}** of admitted polytonic train lines after the cross-wave O5 overlay. "
        f"The combined training pool retains {cap['vouli_poly_train_pool']:,} Vouli / {cap['combined_poly_train_pool']:,} total "
        f"= **{cap['pool_share']:.2%}**, satisfying ≤40%. {cap['excluded']:,} quality-admitted Vouli train lines "
        "are excluded only from the pool by a seeded per-source draw; their admitted records and crops remain available. "
        f"`train_pool_eligible` makes this distinction explicit. The pool contains {summary['train_pool_vouli']:,} Vouli lines "
        f"across classes and {summary['train_pool_total']:,} total lines. No training or shard import was launched.", '',
        f"Cost: **{cost['calls_reserved']:,} reserved DocAI calls; USD {cost['cost_usd']:.4f} "
        f"(USD {cost['cost_usd']:.2f} rounded), below USD 2.50**. Same T19 USD 1.50/1,000-page estimate; "
        "no free allowance deducted. This is a reservation estimate, not invoice readback. "
        "The budget ledger is `docs/harvest/harvest_big/vouli/google/budget.jsonl`; every image SHA occurs once. "
        "Reservations precede requests under hash locks; ambiguous attempts cannot retry. Zero Vision calls. "
        "[Offline cache replay](resume_check.json) invoked every successful cache with the provider method forbidden and changed no ledger hashes.", '',
        f"Failures: **{reads['lost_pages']} lost pages**, **{reads['empty_pages']} empty reads**, "
        f"**{reads['no_line_pages']} pages without line layouts**; **{reads['transformed_pages']} transformed pages** "
        f"were inverse-mapped. Admission excludes all lines on **{len(summary['bad_pages'])} bad pages**. "
        f"**{summary['crop_failures']} additional quality-admitted lines cannot be cropped by the unchanged T20 rule** "
        "and are rejected as `crop_geometry`; [crop_failures.json](crop_failures.json) records their native boxes, "
        "neighbours and exception. Hold-out labels from these lines remain conservatively reserved against train. "
        "[failures.json](failures.json) lists every empty/no-line page, transform and bad-page decision. "
        "Page-gate rejects are recorded, not read failures. Native DocAI layouts can still cross physical rows or contain incorrect text; "
        "the automatic checks and complete compiled pages support the owner's later review, not a human transcription guarantee.", '',
        "[Sample visual QA](visual_qa.json) records a concrete retained error: "
        "`0271e3cae771-p000001-l0031` repeats the opening word and adds a partial repeated word "
        "absent from the visible printed row, yet its mean confidence is 0.952862 and it passes the unchanged T20 gates before O5. "
        "Low-confidence hallucinated text elsewhere on the sampled page is rejected. The same page prints a July 1849 session "
        "inside a book whose supplied metadata year is 1850; per-book metadata does not certify every printed page's date.", '',
        "The inspected mono-class sample `3e08dd4de36e-p000018-l0036` includes the upper arc of the next printed row "
        "at its lower left edge. It follows the requested native bbox, overlap threshold and padding exactly. "
        "Pixel parity and the fixed trim rule therefore do not prove single-row glyph ownership; "
        "the example is retained for the owner's after-the-fact crop review.", '',
        f"Crops: T20 spatial neighbours, >15% overlap midpoint trim, then in-page 4 px horizontal / 2 px vertical padding; "
        f"{summary['trimmed']:,} trimmed. {summary['has_spacing_mark']} labels retain standalone spacing marks. "
        "All crop hashes, dimensions, trim geometry and native source pixels were verified. "
        "Contact sheets use the unchanged T20 sheet builder: 60 random unique admitted crops per populated class, "
        "or all available when fewer than 60, with explicit empty sheets for empty classes.", '',
        "Every read page has an approved-format compiled JPEG under `compiled/<actual-year-or-unknown>_<title40>_<sha6>/pNNNN.jpg`. "
        "The reusable compile_page_reads.py raster builder retains the original fonts, quartile font fit, text positions, "
        "colours, 40 px margins/gap, grey rule and JPEG q85. Only optional output naming and independent page workers were added. "
        "Validation replayed every final compiled raster, text position, JPEG hash and dimension.", '',
        f"**{tests} offline tests passed.** [Full validation](validation.json), [tests](tests.xml), [plan](plan.json), "
        "[book/page counts](books.json), [page gates](manifest.json), [records](records.jsonl), "
        "[admitted](admitted.jsonl), [rejected](rejected.jsonl), [hold-out](holdout_books.json), "
        "[summary](admission_summary.json), [cost](cost_receipt.json), [inventory](inventory.json), "
        "[original gate equivalence](gate_equivalence.json), "
        "[Git audit](git_audit.json). The T20 admission module remains byte-identical. "
        f"Main worktree HEAD, index, main ref/logs, packed refs and config unchanged from the pre-render snapshot: "
        f"**{git_audit['main_worktree_unchanged']}**. The shared .git snapshot also records "
        f"{len(git_audit['changed'])} changed paths, including other worktrees' branch/log/index and object records. "
        "This task issued no Git mutation commands; the complete before/after main-bookkeeping hashes and shared changes are in the audit.", '',
        '| Book (actual metadata) | Year | Split | Rendered | Gate accepted / read | Lines | Admitted |',
        '| --- | ---: | --- | ---: | ---: | ---: | ---: |']
    for b in books:
        title = b['title'].replace('|', '\\|').replace('\n', ' ')
        n = sum(p['harvest_accepted'] for p in manifest if p['key'] == b['key'])
        lines.append(f"| [{title}]({b['source_url']}) (`{b['key']}`) | {b['year'] if b['year'] is not None else 'unknown'} | "
                     f"{held.get(b['key'], 'train')} | {b['page_count']} | {n} | {len(bybook[b['key']])} | {admitted_books[b['key']]} |")
    lines += ['', last]
    (OUT / 'READS.md').write_text('\n'.join(lines) + '\n')
    state_path = REPO / 'docs/harvest/collection/EXECUTION_STATE.md'
    state = state_path.read_text()
    now = datetime.now(ZoneInfo('Europe/Athens')).strftime('%Y-%m-%d %H:%M')
    old_row = next(s for s in state.splitlines() if s.startswith('| 1 Vouli |'))
    state = state.replace(old_row, f"| 1 Vouli | T21 | complete | 2026-10-15 00:53 | {now} | "
        f"{plan['pages_rendered']} / {plan['pages_accepted']} / {plan['page_count']} | {summary['admitted']} | {cost['cost_usd']:.4f} |")
    section = ['## Wave 1', '',
        f"T21 completed {now} Athens: 107 books; {plan['pages_rendered']} pages rendered at 200 dpi grey; "
        f"{plan['pages_accepted']} gate accepted / {plan['page_count']} read once with Document AI; "
        f"{len(records)} lines, {summary['admitted']} admitted, {summary['rejected']} rejected and {summary['crops']} native crops. "
        f"USD {cost['cost_usd']:.4f} reserved (cap 2.50); zero Vision calls. {tests} offline tests passed.", '',
        f"Recorded book years span 1824–1916 plus 11 undated, despite the brief's 1850s description; all 107 inputs retain supplied metadata. "
        "Seed 20261015: 16 held-out books, 12 test / 4 dev. O5 checks both waves' hold-out labels. "
        f"Split line totals: train {splits.get('train', 0)}, dev {splits.get('dev', 0)}, test {splits.get('test', 0)}; "
        f"polytonic {summary['per_class']['greek_poly']}.", '',
        f"Polytonic source share: admitted {cap['admitted_share']:.2%}; effective combined train pool "
        f"{cap['pool_share']:.2%} ({cap['vouli_poly_train_pool']} Vouli / {cap['combined_poly_train_pool']} total), cap ≤40%. "
        f"Use [train_pool.jsonl](../vouli/train_pool.jsonl): it applies {summary['round1_train_label_exclusions']} reverse O5 "
        f"round-1 exclusions and {cap['excluded']} Vouli source-cap exclusions while retaining all admitted crops.", '',
        f"{plan['page_count']} compiled read pages and five class sheets; all crop pixels and compiled rasters validated. "
        f"Failures: {reads['lost_pages']} lost / {reads['empty_pages']} empty / {reads['no_line_pages']} no-line reads; "
        f"{len(summary['bad_pages'])} bad pages excluded at admission; {summary['crop_failures']} uncuttable crop geometries rejected. "
        "[Report](../vouli/READS.md), [summary](../vouli/admission_summary.json), "
        "[validation](../vouli/validation.json), [inventory](../vouli/inventory.json).", '', last]
    tail = ''
    if '\n## Wave 1\n' in state:
        state, previous_section = state.split('\n## Wave 1\n', 1)
        next_heading = previous_section.find('\n## ')
        if next_heading >= 0:
            tail = previous_section[next_heading:]
    state_path.write_text(state.rstrip() + '\n\n' + '\n'.join(section) + '\n' + tail)
    inventory_path = REPO / 'docs/INVENTORY.md'
    text = inventory_path.read_text()
    section = '\n'.join(['<!-- T21:begin -->', '## T21 — Vouli Wave 1 (15 October 2026)', '',
        f"{plan['pages_rendered']} pages rendered / {plan['pages_accepted']} accepted / {plan['page_count']} read; "
        f"{len(records)} DocAI lines; {summary['admitted']} admitted crops; USD {cost['cost_usd']:.4f}; {tests} offline tests passed.", '',
        'Entrypoints: `python -m scripts.harvest.vouli render-gate|run|build|validate|publish`; only `run` uses the network. '
        'Reader is DocAI only, unchanged T19 binding, at-most-once image SHA ledger, USD 2.50 ceiling. '
        'The unchanged `greekocr/harvest/admission.py` handles all T20 line rules. '
        'The combined training pool applies cross-wave hold-out exclusions and the ≤40% polytonic-source cap.', '',
        '[Report](harvest/vouli/READS.md), [records](harvest/vouli/records.jsonl), [admitted](harvest/vouli/admitted.jsonl), '
        '[rejected](harvest/vouli/rejected.jsonl), [summary](harvest/vouli/admission_summary.json), '
        '[books/page counts](harvest/vouli/books.json), [hold-outs](harvest/vouli/holdout_books.json), '
        '[training pool](harvest/vouli/train_pool.jsonl), [training exclusions](harvest/vouli/train_pool_exclusions.jsonl), '
        '[validation](harvest/vouli/validation.json), [tests](harvest/vouli/tests.xml), '
        '[complete file/hash inventory](harvest/vouli/inventory.json). '
        'Bulk PDF, rendered page, Google raw/cache, crop, compiled JPEG and sheet files remain under ignored '
        '`docs/harvest/harvest_big/vouli/`.', '', '<!-- T21:end -->'])
    if '<!-- T21:begin -->' in text:
        a, rest = text.split('<!-- T21:begin -->', 1)
        _, b = rest.split('<!-- T21:end -->', 1)
        text = a + section + b
    else:
        text += '\n\n' + section + '\n'
    inventory_path.write_text(text)
    source_paths = [Path(__file__), REPO / 'scripts/harvest/vouli.py', Path(compiler.__file__),
        REPO / 'greekocr/harvest/admission.py', REPO / 'tests/test_vouli.py',
        REPO / 'greekocr/harvest/readers.py', REPO / 'greekocr/readers/services/google_docai.py',
        REPO / 'scripts/harvest/round1.py', REPO / 'scripts/harvest/build_round1_reads_rest.py',
        REPO / 'scripts/harvest/admit_round1.py', REPO / 'scripts/harvest/round1_reads.py',
        REPO / 'greekocr/harvest/pipeline.py', REPO / 'greekocr/harvest/page_reads.py',
        REPO / 'greekocr/harvest/round1_reads.py',
        *[REPO / 'tests' / name for name in ('test_harvest_admission.py', 'test_round1_admission_outputs.py',
            'test_round1_reads_rest.py', 'test_compile_page_reads.py', 'test_harvest_round1.py', 'test_docai.py')],
        round1.OUT / 'pilot_core.py', REPO / 'docs/briefs/T20_line_admission_crops.md',
        REPO / 'docs/briefs/T19_round1_reads_rest.md', REPO / 'docs/harvest/COLLECTION_PLAN_v1.md']
    paths = {p for p in OUT.rglob('*') if p.is_file() and p.name != 'inventory.json'}
    paths.update(p for p in BULK.rglob('*') if p.is_file())
    paths.update(source_paths + [state_path, inventory_path, round1.OUT / 'admitted.jsonl', round1.OUT / 'holdout_books.json'])
    paths.update(REPO / p for p in plan['inputs'])
    inventory = dict(schema='t21-file-hash-inventory-1', generated_utc=datetime.now(timezone.utc).isoformat(),
        file_count=len(paths), excluded_self='docs/harvest/vouli/inventory.json',
        files=[dict(path=relative(p), bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(paths)])
    atomic(OUT / 'inventory.json', inventory)
    print(last, flush=True)
    return inventory

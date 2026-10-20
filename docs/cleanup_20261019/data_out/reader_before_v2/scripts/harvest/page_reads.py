#!/usr/bin/env python3
"""T15: --prepare is offline; --run authorizes only 253 native-page pairs.

No flag rebuilds evidence exclusively from saved page responses. No crop calls,
automatic retries, production changes, or .git writes. Cost ceiling USD 2.00.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import statistics
import sys

from PIL import Image, ImageDraw
import pypdfium2 as pdfium

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from greekocr.harvest.montage import compare_nfd, response_lines, response_symbols
from greekocr.harvest.montage_controls import letters_marks
from greekocr.harvest.page_reads import assign_page_lines, assign_page_symbols, page_summary, build_blind_review, _response_geometry
from greekocr.harvest.readers import Readers, atomic, read_jsonl
from scripts.harvest.montage_controls import git_state, audit_git

RECORDS = REPO.parent / 'glossapi-ocr-local/experiments/ocr_program_review_20261006/harvest_big/pilot_t13c/pilot_v1/records.jsonl'
OUT = REPO / 'docs/harvest/page_reads_v1'
BULK = REPO / 'docs/harvest/harvest_big/page_reads_v1'
ENGINES = ('vision', 'docai')
SOURCES = ('greekocr/harvest/page_reads.py', 'scripts/harvest/page_reads.py',
           'scripts/harvest/validate_page_reads.py', 'tests/test_page_reads.py',
           'greekocr/harvest/core.py', 'greekocr/harvest/montage.py',
           'greekocr/harvest/montage_controls.py', 'greekocr/harvest/readers.py',
           'greekocr/readers/services/google_docai.py', 'greekocr/readers/services/google_vision.py',
           'scripts/generate_api_docs.py', 'docs/API.md')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def frozen(path, value):
    if path.exists() and json.loads(path.read_text()) != value:
        raise ValueError('frozen evidence changed: ' + str(path))
    if not path.exists():
        atomic(path, value)


def relocated(path, root):
    path = Path(path)
    if path.exists():
        return path.resolve()
    suffix = str(path).split('/harvest_big/', 1)[1]
    candidate = root / suffix
    if not candidate.exists():
        raise FileNotFoundError(candidate)
    return candidate.resolve()


def preflight(records_path=RECORDS):
    OUT.mkdir(parents=True, exist_ok=True)
    if not (OUT / 'git_before.json').exists():
        atomic(OUT / 'git_before.json', git_state())
    records_path = records_path.resolve()
    all_rows = read_jsonl(records_path)
    rows = sorted((r for r in all_rows if r.get('sampled')), key=lambda r: r['id'])
    sampling_path = REPO / 'docs/harvest/pilot_v1/sampling.json'
    sampling = json.loads(sampling_path.read_text())
    if len(rows) != 500 or {r['id'] for r in rows} != set(sampling['ids']):
        raise ValueError('must use exactly the frozen 500 sampled pilot lines')
    pilot_bulk = records_path.parent.parent / 'harvest_big'
    baselines, snapshots, bindings = {}, [], {}
    groups = defaultdict(list)
    for row in rows:
        groups[row['page_id']].append(row)
        crop = records_path.parent.parent / 'pilot_review_images' / (row['id'] + '.straight.png')
        crop_hash = sha(crop)
        row['straight_crop'] = str(crop.resolve())
        single = {}
        with Image.open(crop) as image:
            size = image.size
        for engine in ENGINES:
            value = row['readers'][engine]
            if value['status'] != 'ok' or value['image_sha256'] != crop_hash:
                raise ValueError('changed crop or failed baseline')
            if engine in bindings and bindings[engine] != value['binding']:
                raise ValueError('mixed pilot reader settings')
            bindings[engine] = value['binding']
            raw_path = records_path.parent / 'google' / value['raw_json_path'].split('/google/', 1)[1]
            raw_hash = sha(raw_path)
            cache_path = raw_path.parent / 'cache.json' if engine == 'docai' else records_path.parent / 'google/vision/responses' / (crop_hash + '.json')
            cache = json.loads(cache_path.read_text())
            if cache['raw_sha256'] != raw_hash or cache['crop_sha256'] != crop_hash or cache['binding'] != value['binding']:
                raise ValueError('cached raw/receipt binding mismatch')
            symbols = response_symbols(engine, json.loads(raw_path.read_text()), size)
            confidences = [s['confidence'] for s in symbols if s.get('confidence') is not None]
            mean = statistics.mean(confidences) if confidences else None
            if mean is not None and abs(mean - value['mean_confidence']) > 1e-7:
                raise ValueError('cached symbol mean differs from record')
            single[engine] = dict(text=value['text'], raw_text=value['raw_text'], rejected=value['rejected'],
                status=value['status'], symbols=symbols, raw_json_path=str(raw_path.resolve()), raw_sha256=raw_hash,
                cache_path=str(cache_path.resolve()), cache_sha256=sha(cache_path), mean_symbol_confidence=mean,
                symbol_count=len(confidences), receipt_id=value['receipt_id'], binding=value['binding'])
        baselines[row['id']] = single
        snapshots.append(dict(id=row['id'], page_id=row['page_id'], decade=row['decade'], page_class=row['page_class'],
            polygon=row['polygon'], bbox=row['bbox'], crop=str(crop.resolve()), crop_sha256=crop_hash,
            readers={e: {k: v for k, v in single[e].items() if k != 'symbols'} for e in ENGINES}))
    if 2 * len(groups) > 600 or .003 * len(groups) > 2:
        raise ValueError('page plan exceeds authorized ceiling')
    manifest = []
    for index, (ident, targets) in enumerate(sorted(groups.items()), 1):
        metadata_path = records_path.parent / 'pages' / (ident + '.json')
        metadata = json.loads(metadata_path.read_text())
        provenance = targets[0]['provenance']
        if any((r['provenance']['dpi'], r['provenance']['render_scale'], r['provenance']['grayscale']) != (200, 200 / 72, True) for r in targets):
            raise ValueError('unexpected pilot rendering parameters')
        pdf_path = relocated(metadata['page']['pdf'], pilot_bulk)
        pdf_hash = sha(pdf_path)
        if pdf_hash != metadata['page']['fetch_receipt']['sha256'] or any(pdf_hash != r['provenance']['pdf_sha256'] for r in targets):
            raise ValueError('PDF does not match pilot/fetch hashes')
        native = relocated(provenance['page_image'], pilot_bulk)
        image_path = BULK / 'images' / (ident + '.png')
        image_path.parent.mkdir(parents=True, exist_ok=True)
        with pdfium.PdfDocument(pdf_path) as document, closing(document[metadata['page']['pdf_page_index']]) as page:
            bitmap = page.render(scale=200 / 72, grayscale=True)
            image = bitmap.to_pil().copy().convert('L')
            bitmap.close()
            stream = io.BytesIO()
            image.save(stream, format='PNG', compress_level=1)
        data = stream.getvalue()
        image_hash = hashlib.sha256(data).hexdigest()
        if image_hash != sha(native):
            raise ValueError('page rendering differs from archived native pilot PNG: ' + ident)
        if image_path.exists() and sha(image_path) != image_hash:
            raise ValueError('existing page image changed')
        if not image_path.exists():
            image_path.write_bytes(data)
        # Pilot stores PDF hash and renderer parameters, not a PNG hash. We also
        # require byte-identical re-render against every surviving native PNG.
        manifest.append(dict(id=ident, image=str(image_path.resolve()), image_sha256=image_hash,
            width=image.width, height=image.height, png_bytes=len(data), mode='L', dpi=200, render_scale=200 / 72,
            grayscale=True, straighten=False, png_compress_level=1, renderer='pypdfium2',
            renderer_version=str(pdfium.PYPDFIUM_INFO), pdfium_version=str(pdfium.PDFIUM_INFO),
            pdf=str(pdf_path), pdf_sha256=pdf_hash, pdf_page_index=metadata['page']['pdf_page_index'],
            pilot_page_json=str(metadata_path), pilot_page_json_sha256=sha(metadata_path),
            pilot_native_png=str(native), pilot_native_png_sha256=image_hash, native_png_byte_identical=True,
            sampled_ids=[r['id'] for r in targets], decade=targets[0]['decade'], page_class=targets[0]['page_class']))
        if index % 50 == 0:
            print(f'render verified {index}/{len(groups)}', flush=True)
    if len({m['image_sha256'] for m in manifest}) != len(manifest):
        raise ValueError('distinct pilot pages share an image hash; review call plan')
    sample = dict(schema='greekocr-page-read-sample-1', records=str(records_path), records_sha256=sha(records_path),
        sampling=str(sampling_path), sampling_sha256=sha(sampling_path), lines=500, pages=len(manifest), bindings=bindings, crops=snapshots)
    frozen(OUT / 'sample.json', sample)
    frozen(OUT / 'manifest.json', manifest)
    plan = dict(pages=len(manifest), lines=500, max_calls=2 * len(manifest), max_cost_usd=.003 * len(manifest),
                cap_usd=2., price_per_page_per_reader_usd=.0015, crop_calls=0, automatic_retries=False)
    frozen(OUT / 'plan.json', plan)
    # Correct the source paths solely in our in-memory copy for context generation.
    crops = {r['id']: r['straight_crop'] for r in rows}
    for r in all_rows:
        if r['id'] in crops:
            r['straight_crop'] = crops[r['id']]
    return rows, all_rows, baselines, manifest, sample, plan


def load_pair(page, sample):
    result = {}
    for engine in ENGINES:
        path = BULK / 'google/parsed' / engine / (page['image_sha256'] + '.json')
        value = json.loads(path.read_text())
        if value['status'] != 'ok' or value['binding'] != sample['bindings'][engine] or value['image_sha256'] != sha(page['image']):
            raise ValueError('page response failed or binding/image mismatch')
        result[engine] = value
    return result


def run_readers(manifest, sample, plan):
    readers = Readers(BULK / 'google', cap=2, project=sample['bindings']['vision']['user_project'],
                      processor=sample['bindings']['docai']['processor'])
    readers.budget.max_calls = plan['max_calls']
    if any(getattr(readers, e).binding() != sample['bindings'][e] for e in ENGINES):
        raise ValueError('new reader settings differ from pilot')
    iterator = iter(manifest)

    def call(page):
        if sha(page['image']) != page['image_sha256']:
            raise ValueError('page changed before call')
        result = readers.pair(page['image'])
        if any(value['status'] != 'ok' for value in result.values()):
            raise RuntimeError('reserved page request failed; no automatic retry: ' + json.dumps({e: v.get('error_class', v['status']) for e, v in result.items()}))
        return page['id']

    try:
        # Bounded submissions: on a failure no further pages are scheduled.
        with ThreadPoolExecutor(max_workers=3) as pool:
            pending = {pool.submit(call, page) for page in [next(iterator) for _ in range(min(3, len(manifest)))]}
            completed = 0
            while pending:
                done, pending = wait(pending, return_when=FIRST_COMPLETED)
                for future in done:
                    ident = future.result()
                    completed += 1
                    print(f'read {completed}/{len(manifest)} {ident}', flush=True)
                    page = next(iterator, None)
                    if page is not None:
                        pending.add(pool.submit(call, page))
    finally:
        atomic(OUT / 'cost_receipt.json', readers.budget.receipt())


def evaluate(rows, baselines, manifest, sample, write=True):
    by_page = defaultdict(list)
    for row in rows:
        by_page[row['page_id']].append(row)
    comparisons, page_audits = [], []
    for page in manifest:
        pair = load_pair(page, sample)
        targets = by_page[page['id']]
        for engine, value in pair.items():
            raw_path = Path(value['raw_json_path'])
            raw = json.loads(raw_path.read_text())
            size = (page['width'], page['height'])
            geometry = _response_geometry(engine, raw, size)
            lines = assign_page_lines(geometry['lines'], targets)
            symbols = assign_page_symbols(geometry['symbols'], targets)
            assignment = dict(page_id=page['id'], reader=engine, page_sha256=page['image_sha256'],
                raw_json_path=str(raw_path), raw_sha256=sha(raw_path), binding=value['binding'],
                line_assignment=lines, symbol_assignment=symbols, coordinate_frame=geometry['coordinate_frame'])
            if write:
                atomic(OUT / 'assignments' / (page['id'] + '.' + engine + '.json'), assignment)
            else:
                assert assignment == json.loads((OUT / 'assignments' / (page['id'] + '.' + engine + '.json')).read_text())
            page_audits.append(dict(page_id=page['id'], engine=engine, raw_json_path=str(raw_path), raw_sha256=sha(raw_path),
                receipt_id=value['receipt_id'], merged_boxes=lines['merged_box_count'], unassigned_boxes=lines['unassigned_box_count']))
            for row in targets:
                crop, assigned = baselines[row['id']][engine], lines['targets'][row['id']]
                cs, ps = crop['symbols'], symbols['targets'][row['id']]
                def mean(items):
                    values = [s['confidence'] for s in items if s.get('confidence') is not None]
                    return statistics.mean(values) if values else None
                comparisons.append(dict(id=row['id'], page_id=page['id'], engine=engine, decade=row['decade'], page_class=row['page_class'],
                    crop_text=crop['text'], page_text=assigned['text'], crop_rejected=crop['rejected'], page_rejected=assigned['rejected'],
                    crop_status=crop['status'], page_status=value['status'], crop_symbols=cs, page_symbols=ps,
                    crop_mean_symbol_confidence=mean(cs), page_mean_symbol_confidence=mean(ps),
                    crop_raw_sha256=crop['raw_sha256'], page_raw_sha256=sha(raw_path), page_sha256=page['image_sha256'],
                    **{flag: assigned[flag] for flag in ('merged', 'lost', 'split', 'rejected', 'assigned_line_count', 'flags')},
                    **compare_nfd(crop['text'], assigned['text']), letters_marks_identical=letters_marks(crop['text']) == letters_marks(assigned['text'])))
    comparisons.sort(key=lambda r: (r['id'], r['engine']))
    summary = dict(overall=page_summary(comparisons), by_decade={}, by_page_class={},
                   page_box_counts={e: {k: sum(r[k] for r in page_audits if r['engine'] == e) for k in ('merged_boxes', 'unassigned_boxes')} for e in ENGINES})
    for field in ('decade', 'page_class'):
        for value in sorted({r[field] for r in comparisons}):
            summary['by_' + field][str(value)] = page_summary([r for r in comparisons if r[field] == value])
    if write:
        path = OUT / 'comparisons.jsonl'
        temporary = path.with_suffix('.tmp')
        temporary.write_text(''.join(json.dumps(r, ensure_ascii=False, allow_nan=False) + '\n' for r in comparisons))
        temporary.replace(path)
        atomic(OUT / 'summary.json', summary)
        atomic(OUT / 'page_response_receipts.json', page_audits)
    return comparisons, summary


def failure_evidence(rows, manifest, blind_key):
    """Native review-only overlays; never submitted to either reader."""
    pages = {p['id']: p for p in manifest}
    crops = {c['id']: c for c in json.loads((OUT / 'sample.json').read_text())['crops']}
    blind_ids = {c['id'] for c in blind_key['cards'] + blind_key['most_changed']}
    examples, merge_diagnostics = [], {e: Counter() for e in ENGINES}
    for page in manifest:
        for engine in ENGINES:
            assignment = json.loads((OUT / 'assignments' / (page['id'] + '.' + engine + '.json')).read_text())
            for returned in assignment['line_assignment']['lines']:
                if returned['status'] == 'merged':
                    qualified = sum(o['height_fraction'] + 1e-12 >= .70 and o['horizontal_fraction'] + 1e-12 >= .50 for o in returned['overlaps'].values())
                    merge_diagnostics[engine]['touching_' + ('2plus' if qualified >= 2 else str(qualified)) + '_qualified_targets'] += 1
    for engine in ENGINES:
        for flag in ('merged', 'lost', 'split'):
            candidates = [r for r in rows if r['engine'] == engine and r[flag]]
            candidates = [r for r in candidates if r['id'] not in blind_ids] or candidates
            if flag == 'lost':
                candidates = [r for r in candidates if not r['merged']] or candidates
            if not candidates:
                continue
            row = candidates[0]
            path = OUT / 'assignments' / (row['page_id'] + '.' + engine + '.json')
            assignment = json.loads(path.read_text())
            result = assignment['line_assignment']['targets'][row['id']]
            if result['merged_line_indices'] and flag == 'merged':
                returned = [assignment['line_assignment']['lines'][i] for i in result['merged_line_indices']]
            else:
                returned = [r for r in assignment['line_assignment']['lines'] if row['id'] in r['overlaps']]
            crop = crops[row['id']]
            box = crop['bbox']
            region = [max(0, int(box[0]) - 24), max(0, int(box[1]) - 70),
                      min(pages[row['page_id']]['width'], int(box[2]) + 24),
                      min(pages[row['page_id']]['height'], int(box[3]) + 70)]
            with Image.open(pages[row['page_id']]['image']) as native:
                image = native.crop(tuple(region)).convert('RGB')
            draw = ImageDraw.Draw(image)
            related_ids = {row['id']} | {ident for r in returned for ident in r['overlaps']}
            for ident in related_ids:
                points = [(x - region[0], y - region[1]) for x, y in crops[ident]['polygon']]
                draw.line(points + points[:1], fill='#00864c' if ident == row['id'] else '#e09600', width=2)
            for item in returned:
                x0, y0, x1, y1 = item['line']['bbox']
                draw.rectangle((x0 - region[0], y0 - region[1], x1 - region[0], y1 - region[1]), outline='#d12635', width=2)
            filename = engine + '-' + flag + '.png'
            image_path = OUT / 'failure_images' / filename
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(image_path)
            examples.append(dict(engine=engine, flag=flag, id=row['id'], page_id=row['page_id'], region_box=region,
                image='failure_images/' + filename, crop_text=row['crop_text'], page_text=row['page_text'],
                merged=row['merged'], lost=row['lost'], split=row['split'], assigned_line_count=row['assigned_line_count'],
                flags=row['flags'], returned_boxes=returned, assignment=str(path.relative_to(OUT))))
    value = dict(examples=examples, merged_box_diagnostics={e: dict(c) for e, c in merge_diagnostics.items()},
        legend='green: target polygon; amber: other sampled polygon; red: returned line rectangle; review-only overlay, never read by OCR')
    atomic(OUT / 'failure_examples.json', value)
    return value


def write_report(summary, receipt, blind_key):
    s = summary['overall']
    v, d = (s['readers'][e] for e in ENGINES)
    crop, page = s['harvest']['crop'], s['harvest']['page']
    lines = ['# T15 — Native real-page reads', '',
        f"**253 pages, 500 frozen sampled lines, 506 successful calls.** Page vs crop exact NFD identity: Vision **{v['exact_pct']:.1f}%**, DocAI **{d['exact_pct']:.1f}%**. Strict cross-reader tier-1 yield moves from **{crop['tier1_exact_pct']:.1f}%** in crop mode to **{page['tier1_exact_pct']:.1f}%** in page mode.", '',
        'These measurements describe transcription preservation, mapping and harvest yield; they do not establish which reading is accurate. [Blind owner review](page_reads_v1/blind_review.html) contains 30 changed lines and 10 largest changes with native context. The separate blind key is deliberately unlinked from that page.', '',
        '## Preservation and confidence', '',
        '| Cohort | Reader | Lines | Exact NFD | Letters+marks | Merged | Lost | Split | Rejected | Crop symbol mean (n) | Page symbol mean (n) |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    cohorts = [('ALL', summary['overall'])] + [('decade ' + k, v) for k, v in summary['by_decade'].items()] + list(summary['by_page_class'].items())
    for label, cohort in cohorts:
        for engine in ENGINES:
            r = cohort['readers'][engine]
            def confidence(mode):
                mean = r[mode + '_mean_symbol_confidence']
                return ('—' if mean is None else f'{mean:.6f}') + f" ({r[mode + '_symbol_count']})"
            lines.append(f"| {label} | {engine} | {r['lines']} | {r['exact_pct']:.1f}% ({r['identical']}) | {r['letters_marks_pct']:.1f}% ({r['letters_marks_identical']}) | {r['merged']} | {r['lost']} | {r['split']} | {r['rejected']} | {confidence('crop')} | {confidence('page')} |")
    lines += ['', 'All 500 lines stay in the identity denominators, including mapping failures and the 13 originally rejected crop pairs. Exact comparison is NFD on the cleaned readings, preserving internal whitespace and glyphs. Letters+marks uses the unchanged T14b apostrophe-unification helper, retains case and combining marks, and ignores punctuation, numbers and word boundaries. Empty==empty is possible in preservation but never earns HARVEST agreement.', '',
        'Symbol means weight every reported assigned symbol equally; counts differ with transcription and geometry. Page symbols use the same polygon rule independently of line assignment, so their confidence can remain measurable for a merged/lost line. These means are not accuracy estimates or paired symbol calibration.', '',
        '## HARVEST yield on the same lines', '',
        '| Cohort | Mode | Lines | Usable pairs | Tier-1 strict exact | Letters agree | Pilot tier-1 including substitutions |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for label, cohort in cohorts:
        for mode in ('crop', 'page'):
            h = cohort['harvest'][mode]
            lines.append(f"| {label} | {mode} | {h['lines']} | {h['usable_pairs']} | {h['tier1_exact_pct']:.1f}% ({h['tier1_exact']}) | {h['letters_agree_pct']:.1f}% ({h['letters_agree']}) | {h['pilot_tier1_pct']:.1f}% ({h['pilot_tier1']}) |")
    lines += ['', 'HARVEST denominators include every line. Agreement requires two service-OK, nonempty, non-rejected readings. Strict tier-1 is exact NFD equality as requested; letters agree is the T14b letters+marks equality. The additional pilot tier-1 column runs the original `core.tier` rule with whitespace normalization and only its documented substitutions. This avoids silently conflating strict equality, punctuation-free agreement and pilot substitution acceptance. Pilot whitespace-exact counts are also retained in summary.json.', '',
        '## Rendering, mapping and custody', '',
        'The supplied PDFs and native PNGs were relocated into the external pilot archive. Read-only resolution uses their `/harvest_big/` suffix; resolved paths and hashes are in [manifest.json](page_reads_v1/manifest.json). All 253 PDFs match their recorded SHA-256 fetch receipts and sampled-record PDF hashes. All 253 re-rendered PNGs are byte-identical to archived native pilot PNGs. Pilot page JSON records PDF hashes and render parameters, but no independent PNG hash; the surviving native PNG is the additional byte-identity check. Renderer: pypdfium2 5.14.0 / PDFium 156.0.8076.0; scale 200/72, grayscale L, PNG compress_level=1, PDF page index 0. No straightening, scaling, cropping or synthetic layout is applied to submitted pages.', '',
        'DocAI line layout boxes (paragraph fallback only if no lines) and Vision symbol-break line unions are extracted by the unchanged T14 helpers. Coordinates are in the original rendered page pixels. Targets are exactly the sampled polygons on each page; unsampled returned lines remain unassigned. For a returned rectangle and target polygon, horizontal overlap must be ≥50% of the shorter projected width. Vertical overlap is the mean height of the returned box inside the polygon band over their shared x span: exact polygon clipping integrates sloped bands, divided by shared width and returned box height. Width outside the polygon does not dilute this height fraction. The threshold is ≥70%. Edge-only contact has zero overlap. Any returned box with positive polygon intersection with two sampled targets marks every touched target merged, even when only one meets the thresholds; no merged box is assigned or guessed. Zero uniquely assigned boxes is lost; ≥2 is split. Flags are independent. Side-by-side pieces use the unchanged pilot list-return rule in x order; stacked/obstructed readings retain rejection. Each of the 506 [assignment files](page_reads_v1/assignments/) includes all returned boxes, overlaps, symbols, withheld boxes, raw-response hash and target results.', '',
        'DocAI returned one page in a deskewed frame (2097×1545 pixels versus submitted 2017×1430), with a recorded affine transform. Its reported polygon vertices are mapped back through the inverse matrix before forming native-page line/symbol rectangles. The other 252 DocAI pages have matching native dimensions and no transforms. Every assignment records native/returned dimensions, conversion status and inverse matrix; transformed pieces also retain their reported bbox. No image or raw response is changed. This uses the [Document AI recorded image transforms](https://docs.cloud.google.com/document-ai/docs/reference/rest/v1/Document#Page), and the one-page inverse was checked against native ink with a review overlay. Eight offline cases cover float32/float64 matrices, normalized-only vertices, transform composition, singular/nonfinite refusal and frame mismatch without a transform.', '',
        'Mapping cannot detect merges involving only an unsampled neighbor. This is a stated limit of the sampled-target rule; the blind context panels expose neighboring physical rows. The sample covers body_1column and body_2column pages only, and is book-balanced rather than a population sample.', '',
        'Same pilot reader bindings: Vision DOCUMENT_TEXT_DETECTION, el+grc, provider default unpinned; DocAI EU processor 9a98b7aca3c19561, pretrained-ocr-v2.1-2024-08-07, el, symbols enabled. The previous single-crop controls were deterministic, but time-separated cached baselines and an unpinned Vision model remain a limitation.', '',
        '## Failure examples', '']
    examples = json.loads((OUT / 'failure_examples.json').read_text())
    lines += ['Merged is the requested conservative **box-touch flag**, not proof that a provider transcribed two physical lines as one. This distinction matters on genuine pages: a correct-looking line rectangle can touch the padded polygon of its neighbor, and the axis-aligned box of a rotated watermark can touch multiple sampled polygons. Both are withheld by the specified rule.', '',
        '| Reader | Merged boxes | No target meets both thresholds | One qualified target + another touch | ≥2 qualified targets |',
        '| --- | ---: | ---: | ---: | ---: |']
    for engine in ENGINES:
        m = examples['merged_box_diagnostics'][engine]
        lines.append(f"| {engine} | {summary['page_box_counts'][engine]['merged_boxes']} | {m.get('touching_0_qualified_targets',0)} | {m.get('touching_1_qualified_targets',0)} | {m.get('touching_2plus_qualified_targets',0)} |")
    lines += ['', 'Review overlays use green for the target polygon, amber for other sampled polygons, and red for returned line rectangles. They are never sent to OCR. Failure examples are selected outside the blind cards; lost examples preferentially have no merge flag.', '']
    for r in examples['examples']:
        overlaps = [{ident: {'height': round(o['height_fraction'],4), 'horizontal': round(o['horizontal_fraction'],4)} for ident,o in returned['overlaps'].items()} for returned in r['returned_boxes'][:1]]
        lines.append(f"- {r['engine']} {r['flag']}: `{r['id']}`; assigned boxes={r['assigned_line_count']}; flags={r['flags']}; [native geometry overlay](page_reads_v1/{r['image']}), [raw-bound mapping](page_reads_v1/{r['assignment']}). First returned-box overlaps={overlaps}. Crop={json.dumps(r['crop_text'], ensure_ascii=False)}; page={json.dumps(r['page_text'], ensure_ascii=False)}.")
    lines += ['', '## Cost and verdict', '',
        f"**{receipt['calls_reserved']} reserved calls, USD {receipt['cost_usd']:.4f} conservative list-price receipt, cap USD 2.00.** 253 successful calls per reader; zero crop calls and zero retries. Rate USD 0.0015 per page/image, checked 13 October 2026 against [Vision pricing](https://cloud.google.com/vision/pricing) and [Document AI pricing](https://cloud.google.com/products/document-ai/pricing). Free monthly allowances are not deducted; this is not a billing invoice. [Persistent cost receipt](page_reads_v1/cost_receipt.json). Raw responses, adapter receipts, reservations and page images are under ignored `docs/harvest/harvest_big/page_reads_v1/`.", '',
        'Reservations precede network I/O under locks; all attempts stay reserved, including ambiguous failures. Successful responses are reused; failed/interrupted reservations are never automatically retried. The exact 506-call ceiling is stricter than the requested ≤600. Three pages may be in flight; DocAI starts share the T14 rate lock. Offline rebuild and validation make no service calls and need no ADC.', '',
        f"For this sparse sample, page mode uses 253 vs 500 calls per reader: **49.4% fewer calls**, USD 0.759 vs USD 1.500 for both readers. Per 1,000 sampled lines: USD 0.759 per reader / USD 1.518 combined vs crop USD 1.500 / USD 3.000. Reading every eligible line on these pages could amortize page costs further; that coverage was not measured.", '',
        f"**Measured substitution verdict:** page mode changes {100-v['exact_pct']:.1f}% of Vision readings and {100-d['exact_pct']:.1f}% of DocAI readings, with merged/lost {v['merged']}/{v['lost']} and {d['merged']}/{d['lost']}. It therefore {'meets' if min(v['exact_pct'],d['exact_pct']) >=97 and not any(r[k] for r in (v,d) for k in ('merged','lost')) else 'does not meet'} the earlier ≥97% preservation / zero merged-lost gate for a drop-in crop substitute. Strict tier-1 yield changes by {page['tier1_exact_pct']-crop['tier1_exact_pct']:+.1f} percentage points; letters-agreement yield changes by {page['letters_agree_pct']-crop['letters_agree_pct']:+.1f} points. Its usability as an accuracy-changing harvest alternative remains for the owner's blind check. Agreement alone cannot establish correctness.", '',
        '## Blind review and validation', '',
        f"Exactly 10 Vision-only, 10 DocAI-only and 10 both-changed lines selected from candidate pools {blind_key['candidates']}; stable sorted IDs, seed 15, shuffled card order and independent reader A/B order. The HTML contains inlined native straight crops, escaped readings and local downloadable choices, with no key/source/stratum labels. The top ten are ranked by summed NFD edit count (ties by ID), each with a separate native page region ±2 detected rows in the same column; context coordinates and row IDs are only in blind_key.json. The review is a purposive change sample, not a random accuracy estimate.", '',
        'Offline tests cover polygon slopes and horizontal overlap, exact threshold boundaries, edge contact, merged/lost/split independence, side-by-side joins, rejected stacked pieces, symbol assignment, empty/rejected HARVEST pairs, blinded stratification, deterministic independent A/B order, HTML escaping and inlined context. [Test receipt](page_reads_v1/tests.xml), [offline replay](page_reads_v1/validation.json), [source/data inventory](page_reads_v1/inventory.json), [Git metadata audit](page_reads_v1/git_audit.json). Replay verifies every assignment, metric, baseline/raw/cache hash, reservation and review card. Browser layout QA status is recorded separately in gallery_qa.json.', '']
    (REPO / 'docs/harvest/PAGE_READS_v1.md').write_text('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--prepare', action='store_true')
    group.add_argument('--run', action='store_true')
    args = parser.parse_args()
    rows, all_rows, baselines, manifest, sample, plan = preflight()
    print(json.dumps(plan), flush=True)
    if args.prepare:
        return
    if args.run:
        run_readers(manifest, sample, plan)
    comparisons, summary = evaluate(rows, baselines, manifest, sample)
    page, key = build_blind_review(comparisons, all_rows, manifest)
    (OUT / 'blind_review.html').write_text(page)
    atomic(OUT / 'blind_key.json', key)
    failure_evidence(comparisons, manifest, key)
    receipt = json.loads((OUT / 'cost_receipt.json').read_text())
    write_report(summary, receipt, key)
    atomic(OUT / 'git_audit.json', audit_git(json.loads((OUT / 'git_before.json').read_text()), git_state()))
    atomic(OUT / 'receipt.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), pages=len(manifest), lines=500,
        source_sha256={name: sha(REPO / name) for name in SOURCES if (REPO / name).exists()},
        cost=receipt, crop_calls=0, successful_page_calls=2 * len(manifest),
        artifact_sha256={name: sha(OUT / name) for name in ('sample.json', 'manifest.json', 'summary.json', 'comparisons.jsonl', 'blind_review.html', 'blind_key.json', 'failure_examples.json', 'page_response_receipts.json')}))
    print(json.dumps(summary['overall'], ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()

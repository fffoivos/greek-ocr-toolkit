#!/usr/bin/env python3
"""Offline T17 records, all-page Finder overlays and median-yield HTML reviews."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from greekocr.harvest.core import list_return
from greekocr.harvest.page_reads import _response_geometry
from greekocr.harvest.round1_reads import (attach_vision, line_tier, letter_count,
    symbol_confidences, cohort_summary, median_page, book_folder, numbered_image, page_text, review_html)
from greekocr.harvest.readers import atomic, read_jsonl
from scripts.harvest.round1_reads import REPO, ROOT, OUT, BULK, GOOGLE, ENGINES, DECADES, sha
from scripts.harvest.montage_controls import git_state, audit_git

SOURCES = ['greekocr/harvest/round1_reads.py', 'scripts/harvest/round1_reads.py',
           'scripts/harvest/build_round1_reads.py', 'scripts/harvest/validate_round1_reads.py',
           'tests/test_round1_reads.py', 'greekocr/harvest/page_reads.py', 'greekocr/harvest/montage_controls.py',
           'greekocr/harvest/core.py', 'greekocr/harvest/readers.py',
           'greekocr/readers/services/google_vision.py', 'greekocr/readers/services/google_docai.py']


def read_pair(page, plan):
    result = {}
    for engine in ENGINES:
        path = GOOGLE / 'parsed' / engine / (page['image_sha256']+'.json')
        value = json.loads(path.read_text())
        if value['status'] != 'ok' or value['binding'] != plan['bindings'][engine] or value['image_sha256'] != sha(REPO / page['image']):
            raise ValueError('missing, failed or changed cached page response: '+page['id'])
        raw_path = Path(value['raw_json_path'])
        cache_path = raw_path.parent/'cache.json' if engine == 'docai' else GOOGLE/'vision/responses'/(page['image_sha256']+'.json')
        cache = json.loads(cache_path.read_text())
        if (cache['raw_sha256'] != sha(raw_path) or cache['crop_sha256'] != page['image_sha256']
                or cache['binding'] != plan['bindings'][engine] or cache['receipt_id'] != value['receipt_id']):
            raise ValueError('raw cache/receipt binding changed')
        result[engine] = dict(raw=json.loads(raw_path.read_text()), receipt=dict(engine=engine,
            raw_json_path=str(raw_path.relative_to(REPO)), raw_sha256=sha(raw_path),
            cache_path=str(cache_path.relative_to(REPO)), cache_sha256=sha(cache_path),
            receipt_id=value['receipt_id'], binding=value['binding'], status=value['status']))
    return result


def evaluate(plan, *, write=False):
    records, audits = [], []
    for index, page in enumerate(plan['pages'], 1):
        pair = read_pair(page, plan)
        geometries = {e: _response_geometry(e, v['raw'], (page['width'], page['height'])) for e, v in pair.items()}
        docai = [l for l in geometries['docai']['lines'] if l['source'] == 'lines']
        vision = geometries['vision']['lines']
        document = pair['docai']['raw']['document']
        if len(docai) != len(document['pages'][0].get('lines', [])):
            raise ValueError('DocAI line missing usable geometry: '+page['id'])
        confidences = symbol_confidences(document)
        attachment = attach_vision(docai, vision)
        rows = []
        for i, (d, v, c) in enumerate(zip(docai, attachment['results'], confidences)):
            parsed_d = list_return([d])
            dt, vt = d['text'].strip(), v['text']
            counted = letter_count(dt) >= 3
            flags = list(v['flags']) + ['docai_'+f for f in parsed_d['flags']]
            if not counted:
                flags.append('short_line_excluded')
            if geometries['docai']['coordinate_frame']['converted']:
                flags.append('docai_transform_inverse')
            row = dict(id=f"{page['id']}-l{i+1:04d}", page_id=page['id'], page=page['page'],
                       book=page['book'], book_key=page['key'], year=page['year'], decade=page['decade'],
                       line_number=i+1, docai_index=i, bbox=d['bbox'], image=page['image'], image_sha256=page['image_sha256'],
                       docai_text=dt, vision_text=vt, docai_raw_text=d['text'],
                       **line_tier(dt, vt, usable=v['usable'] and not parsed_d['rejected']),
                       counted=counted, letter_count=letter_count(dt), confidence=c['mean'],
                       min_confidence=c['minimum'], symbol_count=c['symbol_count'], symbol_confidences=c['symbol_confidences'],
                       symbol_indices=c['symbol_indices'], confidence_scope='DocAI symbols fully contained in line text anchors',
                       attachment_method=v['method'], vision_indices=v['vision_indices'], alignment=v['alignment'],
                       flags=sorted(set(flags)), docai_layout_confidence=d.get('confidence'))
            rows.append(row)
        assignment = dict(schema='t17-page-assignment-1', page=page,
                          readers={e: v['receipt'] for e, v in pair.items()},
                          coordinate_frames={e: g['coordinate_frame'] for e, g in geometries.items()},
                          docai_lines=docai, vision_lines=vision, vision_attachment=attachment,
                          docai_symbol_custody=confidences,
                          empty_docai_read=not bool(document.get('text', '').strip()),
                          empty_vision_read=not bool(pair['vision']['raw'].get('responses', [{}])[0].get('fullTextAnnotation', {}).get('text', '').strip()),
                          no_docai_line_layouts=not bool(docai), records=rows)
        filename = OUT/'assignments'/(page['id']+'.json')
        if write:
            atomic(filename, assignment)
        elif assignment != json.loads(filename.read_text()):
            raise AssertionError('assignment replay mismatch: '+page['id'])
        records.extend(rows)
        audits.append(dict(page_id=page['id'], **cohort_summary([page], rows),
                          empty_docai_read=assignment['empty_docai_read'], empty_vision_read=assignment['empty_vision_read'],
                          no_docai_line_layouts=assignment['no_docai_line_layouts'],
                          transformed=geometries['docai']['coordinate_frame']['converted'],
                          coordinate_frame=geometries['docai']['coordinate_frame'],
                          readers=assignment['readers'], unassigned_vision_lines=len(attachment['unassigned_vision_indices'])))
        if index % 50 == 0:
            print(f'offline page {index}/{plan["page_count"]}', flush=True)
    summary = dict(schema='t17-round1-summary-1', overall=cohort_summary(plan['pages'], records), by_decade={}, by_book={},
                   by_page=audits, confidence_scope='symbol-weighted over counted DocAI lines; not an accuracy estimate',
                   short_line_policy='retain every layout; exclude fewer than 3 letters from counts/yield/confidence',
                   fallback_policy='T15 overlap first; nearby mutual unique L/M similarity >=.75 with .10 margins',
                   review_status='prepared; owner review pending')
    for decade in DECADES:
        pages = [p for p in plan['pages'] if p['decade'] == decade]
        summary['by_decade'][str(decade)] = cohort_summary(pages, [r for r in records if r['decade'] == decade])
    for book in sorted({p['book'] for p in plan['pages']}):
        pages = [p for p in plan['pages'] if p['book'] == book]
        summary['by_book'][book] = dict(key=pages[0]['key'], title=pages[0]['title'], year=pages[0]['year'], decade=pages[0]['decade'],
                                       **cohort_summary(pages, [r for r in records if r['book'] == book]))
    return records, summary


def reviews(plan, records):
    metadata = dict(books=[], pages=[], median_rule='lower middle after sorting label-yield percentage, page number, ID',
                    native_overlays='all native-size pages; numbered green DocAI AABBs; no line crops',
                    html_images='downscaled to <=1200x1600; WebP quality 86; inline base64')
    for p in plan['pages']:
        rows = [r for r in records if r['page_id'] == p['id']]
        folder = BULK/'reads_d1_look'/str(p['decade'])/book_folder(p)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder/f"p{p['page']:04d}.png"
        numbered_image(REPO/p['image'], rows).save(path)
        path.with_suffix('.txt').write_text(page_text(p, rows), encoding='utf-8')
        metadata['pages'].append(dict(page_id=p['id'], image=str(path.relative_to(REPO)), text=str(path.with_suffix('.txt').relative_to(REPO)), lines=len(rows)))
    for decade in DECADES:
        selected = []
        for book in sorted({p['book'] for p in plan['pages'] if p['decade'] == decade}, key=lambda b: (summary_book(plan, b)['year'], summary_book(plan, b)['title'], b)):
            pages = [p for p in plan['pages'] if p['book'] == book]
            rows = [r for r in records if r['book'] == book]
            p = median_page(pages, rows)
            picked = [r for r in rows if r['page_id'] == p['id']]
            selected.append((p, picked, REPO/p['image']))
            metadata['books'].append(dict(book=book, decade=decade, page_id=p['id'], page=p['page'],
                                           label_yield_pct=cohort_summary([p], picked)['label_yield_pct']))
        (OUT/f'review_{decade}.html').write_text(review_html(decade, selected), encoding='utf-8')
    atomic(OUT/'review_selection.json', metadata)


def summary_book(plan, book):
    return next(p for p in plan['pages'] if p['book'] == book)


def report(plan, records, summary, cost):
    o = summary['overall']
    suites = ET.parse(OUT/'tests.xml').getroot().findall('testsuite') if (OUT/'tests.xml').exists() else []
    tests_passed = sum(int(s.attrib['tests'])-int(s.attrib.get('failures',0))-int(s.attrib.get('errors',0))-int(s.attrib.get('skipped',0)) for s in suites)
    lines = ['# T17 — Round-1 page harvest, 1860–1880', '',
             f"**{o['pages']} accepted pages; {len(summary['by_book'])} books; {o['lines']} counted DocAI lines; {o['label_yield_pct']:.2f}% provisional label yield.** All {o['records']} layouts are retained, including {o['short_lines']} with fewer than three letters.", '',
             'Only `harvest_accepted=true` pages of books whose selection decade is 1860, 1870 or 1880 were submitted. Owner approved these three decades in Finder on 14 October 2026. No 1890–1930 reads, line crops or crop-reader calls. Page inputs are the unchanged manifest-bound 200 DPI grayscale PNGs.', '',
             '## Yield', '', '| Decade | Pages | Lines | Tier 1 | Tier 2 | Tier 3 | Labels | Yield | DocAI symbol mean |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for name, c in list(summary['by_decade'].items())+[('ALL', o)]:
        mean = '—' if c['mean_confidence'] is None else f"{c['mean_confidence']:.6f}"
        lines.append(f"| {name} | {c['pages']} | {c['lines']} | {c['tier1']} | {c['tier2']} | {c['tier3']} | {c['labels']} | {c['label_yield_pct']:.2f}% | {mean} |")
    lines += ['', '| Year / book | Pages | Lines | Tier 1 | Tier 2 | Tier 3 | Yield | Symbol mean |', '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for b, c in sorted(summary['by_book'].items(), key=lambda x: (x[1]['decade'], x[1]['year'], x[1]['title'])):
        title = c['title'].replace('|', '\\|').replace('\n', ' ')
        mean = '—' if c['mean_confidence'] is None else f"{c['mean_confidence']:.6f}"
        lines.append(f"| {c['year']} {title} (`{c['key']}`) | {c['pages']} | {c['lines']} | {c['tier1']} | {c['tier2']} | {c['tier3']} | {c['label_yield_pct']:.2f}% | {mean} |")
    lines += ['', '## Rules and custody', '',
              'The line set is exactly Document AI line layouts, in provider order, numbered from 1 on each page. Paragraph fallback is never counted as a line. Native bboxes use the unchanged T15 inverse-transform helper, applying recorded matrices to polygon vertices before forming AABBs. Every assignment retains the coordinate frame, inverse, reported boxes when transformed, raw/cache hashes, bindings and receipt IDs.', '',
              'Vision uses symbol-break line unions. T15 geometry requires >=70% returned-box height inside the DocAI rectangular band and >=50% shorter-width overlap. Any positive touch of two bands is withheld as ambiguous. Side-by-side pieces use the unchanged pilot list-return helper in x order; stacked, obstructed and foreign-script pieces retain rejection. Raw readings remain visible. Nearby ambiguous boxes may be resolved by a mutual unique text alignment: T14b letters+marks SequenceMatcher >=.75, with >=.10 margin over both competing DocAI and Vision candidates, and at least three letters. Fallback never shares or splits a Vision line. Unresolved matches stay tier 3.', '',
              'Tier 1 is exact NFD equality of cleaned readings (outer line whitespace stripped; internal whitespace, glyphs and case preserved). Tier 2 requires equality of letters+marks after the unchanged T14b spacing-apostrophe unification. Both use the DocAI reading as the label. Tier 3 includes disagreements, empty readings and rejected attachments, with no label. No edit-distance or rare-glyph substitution promotion is applied. DocAI symbol confidences are linked by full containment in the original line text anchors, independent of AABB overlaps. Means weight every reported symbol in counted lines equally.', '',
              f"Counted attachments: `{o['attachment_counts']}`. Geometry supplies {o['geometry_only_labels']} labels; text fallback supplies {o['fallback_labels']}. Text-based selection can increase agreement yield, so the methods and their separate label counts are exposed. Agreement and service confidence do not establish transcription accuracy.", '',
              '## Owner review', '',
              '[1860s](reads_d1/review_1860.html) · [1870s](reads_d1/review_1870.html) · [1880s](reads_d1/review_1880.html). Each book contributes its lower median-yield page (yield-sorted, page/ID tie-breaks), with numbered green DocAI boxes on the left and numbered tier-colored readings on the right. Tier 2 folds the Vision reading; tier 3 shows both. HTML is self-contained with downscaled inline images. The Finder folder has every page at native dimensions plus its numbered UTF-8 text: `docs/harvest/harvest_big/round1/reads_d1_look/<decade>/<year>_<title>_<id>/pNNNN.{png,txt}`. Owner reading/accuracy review remains pending.', '',
              '## Failures and transforms', '']
    audits = summary['by_page']
    lines += [f"Lost pages: {plan['page_count']-len(audits)}. Empty DocAI reads: {sum(p['empty_docai_read'] for p in audits)}; empty Vision reads: {sum(p['empty_vision_read'] for p in audits)}; pages without DocAI line layouts: {sum(p['no_docai_line_layouts'] for p in audits)}. Transformed DocAI pages: {sum(p['transformed'] for p in audits)}. Unresolved counted Vision attachments: {o['attachment_counts'].get('unresolved', 0)}.", '']
    examples = dict(lost_pages=[], empty_reads=[p for p in audits if p['empty_docai_read'] or p['empty_vision_read'] or p['no_docai_line_layouts']],
                    transforms=[p for p in audits if p['transformed']],
                    unresolved=[{k:r[k] for k in ('id','page_id','bbox','docai_text','vision_text','flags')} for r in records if r['counted'] and r['attachment_method']=='unresolved'][:8],
                    disagreements=[{k:r[k] for k in ('id','page_id','docai_text','vision_text','attachment_method','flags')} for r in records if r['counted'] and r['tier']==3 and r['attachment_method']!='unresolved'][:8])
    atomic(OUT/'failure_examples.json', examples)
    for p in examples['transforms']:
        lines.append(f"- Transform `{p['page_id']}`: native {p['coordinate_frame']['native_size']}, reported {p['coordinate_frame']['returned_size']}; recorded inverse retained in its assignment.")
    for r in examples['unresolved'][:3]+examples['disagreements'][:3]:
        lines.append(f"- `{r['id']}`: DocAI {json.dumps(r['docai_text'],ensure_ascii=False)}; Vision {json.dumps(r['vision_text'],ensure_ascii=False)}; flags `{r['flags']}`.")
    lines += ['', '[Complete failure examples](reads_d1/failure_examples.json); [per-page raw-bound assignments](reads_d1/assignments/). Empty or lost pages have no invented lines. Failed or interrupted reservations are never retried.', '',
              '## Cost and checks', '',
              f"**{cost['calls_reserved']} reserved calls; USD {cost['cost_usd']:.4f} conservative list-price receipt; USD 2.00 cap.** {cost['calls_by_engine']}; zero retries and zero crop calls. Each native page has one call per reader. Reservations precede I/O under locks and survive interruption. Successful cached responses are reused on rebuild. Pricing checked 14 October 2026: USD .0015 per page/image for [Vision](https://cloud.google.com/vision/pricing) and [Document AI](https://cloud.google.com/products/document-ai/pricing). Monthly free allowances are not deducted; this is not a billing invoice. [Cost receipt](reads_d1/cost_receipt.json).", '',
              'Readers are unchanged from T15: Vision DOCUMENT_TEXT_DETECTION, el+grc, unpinned provider default; DocAI EU processor 9a98b7aca3c19561, pretrained-ocr-v2.1-2024-08-07, el, symbols enabled. At most three page pairs run concurrently; the established DocAI start-rate lock is reused.', '',
              f'{tests_passed} offline tests passed, including 33 new T17 cases and existing T15, T16 and Google-reader contracts. These cover strict tiers, mark/case/empty handling, accepted-decade scope, ambiguous and unique attachments, side-by-side/rejected stacked pieces, mutual alignment ties, symbol-anchor confidence custody, short-line denominators, median-page selection, review escaping, inline images and numbering. [Tests](reads_d1/tests.xml), [independent offline replay](reads_d1/validation.json), [visual QA](reads_d1/gallery_qa.json), [receipt](reads_d1/receipt.json), [file/hash inventory](reads_d1/inventory.json), [Git audit](reads_d1/git_audit.json). T17 invokes no Git commands and writes no `.git` files.', '',
              'Three native review overlays (one per decade, including a facing-page spread) were visually inspected. Every numbered overlay and text file is independently regenerated during validation, and all 33 inline images and HTML contents are verified. Browser-rendered desktop/narrow layout remains unverified: automatic approval review rejected Firefox inspection with “Computer Use was not approved to use Firefox”; the local Playwright Chromium executable is absent. No browser inspection is claimed.', '',
              'The Git metadata audit observed concurrent main-branch/index/reflog changes. The main reflog records separate round-1 rescue commits and the T18 brief during this task. These changes are preserved; T17’s selection/manifest hashes remain unchanged. No Git state was staged, committed or restored by T17.']
    (ROOT/'READS_D1.md').write_text('\n'.join(lines)+'\n')


def seal(plan, summary):
    audit = audit_git(json.loads((OUT/'git_before.json').read_text()), git_state())
    atomic(OUT/'git_audit.json', audit)
    artifacts = [p for p in OUT.rglob('*') if p.is_file() and p.name not in ('receipt.json','inventory.json','read.log')]
    atomic(OUT/'receipt.json', dict(schema='t17-receipt-1', timestamp=datetime.now(timezone.utc).isoformat(),
           status='completed page reads and review preparation; owner accuracy review pending',
           scope=dict(decades=list(DECADES), pages=plan['page_count'], books=len(summary['by_book']), accepted_only=True),
           plan_sha256=sha(OUT/'plan.json'), inputs={str(ROOT.relative_to(REPO)/n):sha(ROOT/n) for n in ('selection.json','manifest.json')},
           source_sha256={s:sha(REPO/s) for s in SOURCES if (REPO/s).exists()},
           artifacts_sha256={str(p.relative_to(OUT)):sha(p) for p in sorted(artifacts)},
           report_sha256=sha(ROOT/'READS_D1.md'), cost=json.loads((OUT/'cost_receipt.json').read_text()),
           automatic_retries=0, crop_calls=0, line_crops=0, git_writes_performed=False, git=audit))
    paths = list(OUT.rglob('*'))+list(GOOGLE.rglob('*'))+list((BULK/'reads_d1_look').rglob('*'))+[ROOT/'READS_D1.md', REPO/'docs/INVENTORY.md']+[REPO/s for s in SOURCES]
    atomic(OUT/'inventory.json', dict(schema='t17-file-inventory-1', files=[dict(path=str(p.relative_to(REPO)), bytes=p.stat().st_size, sha256=sha(p))
           for p in sorted(set(paths)) if p.is_file() and p.name != 'inventory.json' and '__pycache__' not in p.parts and not p.name.endswith('.lock')]))


def build(plan):
    records, summary = evaluate(plan, write=True)
    temporary = OUT/'records.jsonl.tmp'
    temporary.write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in records))
    temporary.replace(OUT/'records.jsonl')
    atomic(OUT/'summary.json', summary)
    reviews(plan, records)
    cost = json.loads((OUT/'cost_receipt.json').read_text())
    report(plan, records, summary, cost)
    seal(plan, summary)
    print(json.dumps(summary['overall'], ensure_ascii=False), flush=True)

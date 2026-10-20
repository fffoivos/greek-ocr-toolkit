"""Reproduce the descriptive Q2 audit from measured tables and preselected original-image regions."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw
from scipy.stats import mannwhitneyu

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from greekocr.glyphs.statistics import book_statistics, corpus_statistics, render_book_statistics, _distribution
from scripts.glyphs.build_statistics import read_page


def region_rows(rows, region, size, *, bodies=False):
    w, h = size
    return [r for r in rows if (not bodies or r['entity_kind'] == 'letter_body') and
            region[0]*w <= (r['box'][0]+r['box'][2])/2 < region[2]*w and
            region[1]*h <= (r['box'][1]+r['box'][3])/2 < region[3]*h]


def region_summary(rows):
    fields = ('darkness', 'contrast_absolute', 'contrast_local', 'contrast_ratio', 'edge_sharpness',
              'edge_ratio', 'book_contrast_ratio', 'book_edge_ratio')
    result = dict(rows=len(rows), ink_pixels=sum(r['ink_pixels'] for r in rows),
        entities=dict(Counter(r['entity_kind'] for r in rows)),
        measures={f: _distribution([r.get(f) for r in rows]) for f in fields})
    for prefix in ('', 'book_'):
        for flag in ('front_text', 'show_through_candidate', 'stamp_watermark_candidate'):
            values = [r.get(prefix+flag) for r in rows]
            result[prefix+flag] = dict(available=sum(v is not None for v in values), flagged=sum(v is True for v in values))
    return result


def separation(a, b, name):
    a = [r[name] for r in a if r.get(name) is not None]
    b = [r[name] for r in b if r.get(name) is not None]
    if not a or not b:
        return dict(candidate_rows=len(a), text_rows=len(b), median_gap=None, faint_ranking_auc=None,
                    candidate_below_half=None, text_below_half=None)
    return dict(candidate_rows=len(a), text_rows=len(b),
        median_gap=float(np.median(b)-np.median(a)),
        faint_ranking_auc=float(1-mannwhitneyu(a, b, alternative='two-sided').statistic/(len(a)*len(b))),
        candidate_below_half=float(np.mean(np.array(a)<.5)), text_below_half=float(np.mean(np.array(b)<.5)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('.astra/out'))
    parser.add_argument('--regions', type=Path, default=Path('docs/records/reviews/PAGE_LINES_Q2_OWNER_REGIONS.json'))
    args = parser.parse_args()
    cases = []
    for case in json.loads(args.regions.read_text())['cases']:
        p = read_page(args.out, case['page_key'])
        faint = region_rows(p['glyphs'], case['region'], p['stats']['image_size'])
        text = region_rows(p['glyphs'], case['text'], p['stats']['image_size'], bodies=True)
        cases.append(dict(**case, region_ink=region_summary(faint), text_ink=region_summary(text),
            separation_page=separation(faint, text, 'contrast_ratio'),
            separation_book=separation(faint, text, 'book_contrast_ratio'),
            book_reference=p['stats']['book_reference']))
        # Rectangles display the sampling design on original pixels, not a inferred truth mask.
        with Image.open(p['stats']['source_image']) as im:
            im = im.convert('RGB')
            draw = ImageDraw.Draw(im)
            w, h = im.size
            for name, color in [('region', (180, 20, 200)), ('text', (0, 140, 60))]:
                a, t, b, d = case[name]
                draw.rectangle((a*w, t*h, b*w, d*h), outline=color, width=max(2, round(w/600)))
            im.thumbnail((1000, 1400))
            im.save(args.out/f"{case['page_key']}.stats-regions.jpg", quality=92)
    # The requested 41-page cohort is audited separately from the combined 95-page reference pool.
    selection = json.loads(Path('.astra/book_pages/selection.json').read_text())['pages']
    groups = defaultdict(list)
    for row in selection:
        groups[row['book']].append(row['page'])
    book_results = []
    cohort_stats = []
    book_dir = args.out/'book_pages'/'books'
    book_dir.mkdir(parents=True, exist_ok=True)
    for book, keys in sorted(groups.items()):
        measured = [read_page(args.out/'book_pages', key) for key in keys]
        result = book_statistics(measured, book_id=book)
        book_results.append(result['stats'])
        cohort_stats.extend(p['stats'] for p in result['pages'])
        (book_dir/f'{book}.stats.json').write_text(json.dumps(result['stats'], indent=2, allow_nan=False)+'\n')
        render_book_statistics(result['stats']).save(book_dir/f'{book}.summary.jpg', quality=93)
    corpus41 = corpus_statistics(cohort_stats)
    (args.out/'book_pages'/'corpus.stats.json').write_text(json.dumps(corpus41, indent=2, allow_nan=False)+'\n')
    import csv
    with (args.out/'book_pages'/'corpus.summary.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(corpus41['table'][0]))
        writer.writeheader(); writer.writerows(corpus41['table'])
    frozen = json.loads(Path('.astra/q2-q1-before.json').read_text())
    changed = [p for p, sha in frozen.items() if not Path(p).exists() or hashlib.sha256(Path(p).read_bytes()).hexdigest() != sha]
    protected = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for suffix in ('lines.json', 'cells.json', 'structure.json', 'segments.json')
                 for p in sorted((args.out/'book_pages').glob('*.'+suffix))}
    book_before = json.loads(Path('.astra/q2-book-q1-before.json').read_text())
    book_changed = [p for p, sha in book_before.items() if protected.get(p) != sha]
    artifact_counts = Counter()
    failures = []
    first_schema = None
    implementation_sha = hashlib.sha256(Path('greekocr/glyphs/statistics.py').read_bytes()).hexdigest()
    import pyarrow.parquet as pq
    for directory, inputs in ((args.out, Path('.astra/pages')), (args.out/'book_pages', Path('.astra/book_pages'))):
        for raster in sorted(inputs.glob('*.png')):
            key = raster.stem
            source = directory/f'{key}.lines.json'
            page = read_page(directory, key)
            q1 = json.loads(source.read_text())
            if page['stats']['implementation_sha256'] != implementation_sha:
                failures.append([key, 'stale statistics implementation'])
            if page['stats']['lines_file_sha256'] != hashlib.sha256(source.read_bytes()).hexdigest():
                failures.append([key, 'changed source geometry'])
            original = Path(page['stats']['source_image'])
            if page['stats']['source_sha256'] != hashlib.sha256(original.read_bytes()).hexdigest():
                failures.append([key, 'changed source image'])
            width, height = page['stats']['image_size']
            seen = set()
            for row in page['glyphs']:
                if row['glyph_id'] in seen:
                    failures.append([key, 'duplicate glyph_id'])
                seen.add(row['glyph_id'])
                a, t, b, d = row['box']
                if not (0 <= a < b <= width and 0 <= t < d <= height):
                    failures.append([key, 'out-of-image glyph box'])
                i = row['line_index']
                if i is not None and (q1[i].get('discounted') or any(row[k] != q1[i][k] for k in ('page_side', 'column_id', 'row_id'))):
                    failures.append([key, 'Q1 address mismatch'])
                if i is None and any(row[k] is not None for k in ('line_id', 'column_id', 'row_id')):
                    failures.append([key, 'invented residual address'])
            detection = page['stats']['residual_detection']
            expected_pixels = detection['owned_ink_pixels'] + detection['detected_residual_pixels'] - detection['small_component_pixels_excluded']
            if sum(r['ink_pixels'] for r in page['glyphs']) != expected_pixels:
                failures.append([key, 'ink pixel accounting mismatch'])
            if len(page['glyphs']) != page['stats']['summary']['rows']:
                failures.append([key, 'table/summary count mismatch'])
            image = directory/f'{key}.glyphs.jpg'
            with Image.open(image) as im:
                if im.size != (max(width, 680), height+38):
                    failures.append([key, 'incorrect overlay dimensions'])
                im.verify()
            schema = pq.read_schema(directory/page['stats']['glyph_table'])
            if first_schema is None:
                first_schema = schema
            elif schema != first_schema:
                failures.append([key, 'inconsistent Parquet schema'])
            artifact_counts['pages'] += 1
            artifact_counts['glyph_rows'] += len(page['glyphs'])
            artifact_counts['letter_bodies'] += page['stats']['summary']['letter_bodies']
    tests = None
    if Path('.astra/q2-tests.xml').exists():
        root = ET.parse('.astra/q2-tests.xml').getroot()
        suites = root.findall('testsuite')
        tests = {k: sum(int(s.get(k, 0)) for s in suites) for k in ('tests', 'failures', 'errors', 'skipped')}
        tests['passed'] = tests['tests']-tests['failures']-tests['errors']-tests['skipped']
    report = dict(owner_cases=cases, book_cohort_41=book_results, corpus_41=corpus41,
        corpus_95=json.loads((args.out/'corpus.stats.json').read_text()),
        q1_preservation=dict(files=len(frozen), unchanged=len(frozen)-len(changed), changed=changed),
        new_book_q1_hashes=protected,
        book_q1_preservation=dict(files=len(book_before), unchanged=len(book_before)-len(book_changed), changed=book_changed),
        artifact_audit=dict(counts=dict(artifact_counts), failures=failures), tests=tests)
    Path('docs/records/reviews/PAGE_LINES_Q2_STATISTICS.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print('preservation', report['q1_preservation'], 'book preservation', report['book_q1_preservation'], 'artifacts', report['artifact_audit'], 'tests', tests)
    for b in book_results:
        print('book', b['book_id'], 'pages', b['pages'], 'letters', b['summary']['letter_bodies'],
              'size CV', b['stability']['body_size_page_width']['cv'], 'contrast CV', b['stability']['contrast']['cv'])
    for c in cases:
        print('case', c['page_key'], 'ink rows', c['region_ink']['rows'], 'text', c['text_ink']['rows'],
              'contrast', c['region_ink']['measures']['contrast_ratio']['median'],
              'page AUC', c['separation_page']['faint_ranking_auc'], 'book AUC', c['separation_book']['faint_ranking_auc'])

    if changed or book_changed or failures:
        raise SystemExit('Mandatory geometry/artifact audit failed; see machine report')


if __name__ == '__main__':
    main()

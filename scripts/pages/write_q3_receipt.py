"""Bundle the completed Q3 comparisons and every observed difference for review."""
from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from greekocr.ops.data_root import input_path as _data_input
from scripts.pages.check_stage_equivalence import MODULES, normalise


def sha(path):
    return hashlib.sha256(_data_input(path).read_bytes()).hexdigest()


def main():
    directory = ROOT / '.astra/q3-equality'
    pages = json.loads((directory / 'summary.json').read_text())
    books = json.loads((directory / 'books-summary.json').read_text())
    assert Counter(r['cohort'] for r in pages['pages']) == {'development': 54, 'book': 41}
    suite = ET.parse(ROOT / '.astra/q3-final-tests.xml').getroot().find('testsuite')
    tests = {key: int(suite.get(key)) for key in ('tests', 'failures', 'errors', 'skipped')}
    tests['passed'] = tests['tests'] - tests['failures'] - tests['errors'] - tests['skipped']
    tests['seconds'] = float(suite.get('time'))
    tests['families'] = {}
    for family in ('initial_batches', 'curl', 'orientation', 'pages_api', 'docling'):
        cases = [case for case in suite.findall('testcase') if family in case.get('classname', '')]
        tests['families'][family] = dict(tests=len(cases),
            failures=sum(case.find('failure') is not None or case.find('error') is not None for case in cases),
            skipped=sum(case.find('skipped') is not None for case in cases))
    tests['skips'] = [dict(test=case.get('classname') + '.' + case.get('name'),
                         reason=case.find('skipped').get('message'))
                      for case in suite.findall('testcase') if case.find('skipped') is not None]
    tests['receipt_sha256'] = sha(ROOT / '.astra/q3-final-tests.xml')
    equivalence = []
    for old, new in MODULES.items():
        before = subprocess.check_output(['git', 'show', f'10eda96:greekocr/glyphs/{old}.py'], cwd=ROOT).decode()
        path = ROOT / f'greekocr/pages/{new}.py'
        a, b = normalise(before), normalise(path.read_text())
        equivalence.append(dict(old=f'greekocr/glyphs/{old}.py', new=str(path.relative_to(ROOT)),
            equivalent=a == b, normalized_ast_sha256=hashlib.sha256(b.encode()).hexdigest(), source_sha256=sha(path)))
    failures = {}
    counts = Counter()
    for report in (pages, books):
        for kind in ('runtime_differences', 'frozen_differences'):
            for item in report[kind]:
                if 'file' not in item:
                    continue
                path = Path(item['file'])
                details = json.loads(path.read_text())
                failures[path.name] = details
                item['file'] = path.name
                counts[kind + ':' + item['field']] += len(details)
    for page in pages['pages']:
        for kind in ('runtime_differences', 'frozen_differences'):
            for item in page[kind]:
                if 'file' in item:
                    item['file'] = Path(item['file']).name
    destination = ROOT / 'docs/records/reviews'
    diff_path = destination / 'PAGE_LINES_Q3_DIFFERENCES.json.gz'
    buffer = io.BytesIO()
    with gzip.GzipFile(filename='', mode='wb', fileobj=buffer, mtime=0) as stream:
        stream.write(json.dumps(failures, ensure_ascii=False, sort_keys=True, indent=2).encode())
    diff_path.write_bytes(buffer.getvalue())
    protection = json.loads((ROOT / '.astra/q3-protected-main.json').read_text())
    for row in protection['crop_files']:
        before = subprocess.check_output(['git', 'show', f"10eda96:{row['path']}"], cwd=ROOT)
        assert (ROOT / row['path']).read_bytes() == before, row['path']
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    for row in protection['incoming_main']:
        before = subprocess.check_output(['git', 'show', f"main:{row['path']}"], cwd=ROOT)
        assert (ROOT / row['path']).read_bytes() == before, row['path']
    source_snapshot = json.loads((ROOT / '.astra/q3-frozen-source-hashes.json').read_text())
    tested_sources = json.loads((ROOT / '.astra/q3-tested-source-hashes.json').read_text())
    formatting = json.loads((ROOT / '.astra/q3-post-test-formatting.json').read_text())
    changes = {row['path']:row for row in formatting}
    for name, expected_sha in source_snapshot.items():
        assert sha(ROOT / name) == expected_sha, f'Source changed after final test snapshot: {name}'
        if tested_sources[name] != expected_sha:
            row=changes[name]
            assert row['ast_identical'] and row['before_sha256']==tested_sources[name] and row['after_sha256']==expected_sha
    report = dict(status='NOT DONE', reference_commit=pages['reference_commit'],
        open_requirements=['Exact frozen-output equality is not achieved.',
                           'Default API page units are source pixels; equality comparisons explicitly supply the old raster/3 page size.',
                           'Partial historical joined-row envelopes are not reproduced.',
                           'Some support-count, percentile and plotting literals remain inline.',
                           'Frozen review image identity and full plugin-output identity are not certified.',
                           'Sixteen existing web-render tests could not run without Chromium.',
                           'The sandbox blocked the commit and main ancestry merge.'],
        methodology=dict(runtime='Exact JSON values, glyph Parquet rows, delivered crop pixel hashes; no tolerance.',
            page_units='Comparison calls explicitly pass raster width/3 and height/3; the API default is source-pixel page units.',
            options='Actual default/table API executions with statistics; all three join outcomes composed over each exact geometry; 16 synthetic option combinations.',
            frozen='Lines, structure, cells, enriched page statistics, glyph Parquet rows, book/corpus JSON.',
            limits=['Frozen review images, historical checks/segments/partial-row envelopes and archived orientation receipts are not certified identical.',
                    'Development execution began before mechanical parameter naming finished; final normalized stage ASTs and final full tests are recorded separately.',
                    'The old plugin used an active-line delivery list. Its conversion to the canonical page delivery has contract-test coverage, not a full 95-page plugin-output identity proof.']),
        tests=tests, stage_equivalence=equivalence, pages=pages, books=books,
        difference_counts=dict(counts), difference_bundle=dict(file=diff_path.name, sha256=sha(diff_path), entries=len(failures)),
        protected_files=protection['crop_files'], incoming_main_files=protection['incoming_main'],
        cached_layout_smoke=json.loads((ROOT / '.astra/q3-layout-smoke.json').read_text()),
        synthetic_review_images=json.loads((ROOT / '.astra/q3-render-check.json').read_text()),
        historical_joining=dict(api_behavior='Unsafe joining raises; partial archived row envelopes are not reproduced.',
            cohorts=json.loads((ROOT / '.astra/q3-joined-row-coverage.json').read_text())),
        final_source_sha256=source_snapshot, tested_source_sha256=tested_sources,
        post_test_formatting_only=formatting,
        git=dict(branch=subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
            head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            main=subprocess.check_output(['git', 'rev-parse', 'main'], cwd=ROOT, text=True).strip(),
            main_is_ancestor=subprocess.run(['git', 'merge-base', '--is-ancestor', 'main', 'HEAD'], cwd=ROOT).returncode == 0,
            commit=None, block='Sandbox refused ORIG_HEAD.lock and index.lock in the shared worktree metadata.'))
    path = destination / 'PAGE_LINES_Q3_EQUALITY.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(report=str(path.relative_to(ROOT)), tests=tests['passed'],
        runtime_page_differences=len(pages['runtime_differences']),
        runtime_book_differences=len(books['runtime_differences']),
        frozen_page_files=len(pages['frozen_differences']), frozen_statistics_files=len(books['frozen_differences']),
        difference_values=sum(counts.values())), indent=2))


if __name__ == '__main__':
    main()

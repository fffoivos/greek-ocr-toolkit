"""Bundle the complete Q3b gate without discarding any non-allowlisted failure."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.pages.check_q3b_equality import ALLOWLIST


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    directory = ROOT / '.astra/q3b-equality'
    pages = json.loads((directory/'summary.json').read_text())
    books = json.loads((directory/'books-summary.json').read_text())
    tests_path = ROOT / '.astra/q3b-final-tests.xml'
    tests = ET.parse(tests_path).getroot()
    suites = list(tests.iter('testsuite'))
    test_counts = {k: sum(int(s.get(k, 0)) for s in suites) for k in ('tests', 'failures', 'errors', 'skipped')}
    test_counts['passed'] = test_counts['tests'] - sum(test_counts[k] for k in ('failures', 'errors', 'skipped'))
    test_counts['sha256'] = sha(tests_path)
    source_manifest = json.loads((directory/'source-manifest.json').read_text())
    assert all(sha(ROOT/path) == identity for path, identity in source_manifest.items()), 'Validated source changed'
    assert pages['allowlist'] == ALLOWLIST
    assert Counter(r['cohort'] for r in pages['pages']) == {'development': 54, 'book': 41}
    assert len({r['page_key'] for r in pages['pages']}) == 95
    assert pages['api_calls'] == 1520
    assert pages['crops'] == 32144, 'Incomplete delivered-crop coverage'
    fields = Counter()
    failures = {}
    metadata = {}
    blocked = {}
    frozen_hashes = {}
    for row in pages['pages']:
        key = row['page_key']
        frozen = ROOT / '.astra/out_after_Q2' / ('book_pages' if row['cohort']=='book' else '')
        source_stats = json.loads((frozen/f'{key}.stats.json').read_text())
        assert source_stats['source_sha256'] == row['source_sha256'], f'Frozen source identity mismatch: {key}'
        for name, equal in row['checks'].items():
            group = name if name.startswith('frozen.') else 'runtime.' + name.rsplit('.', 1)[-1]
            fields[group+'.total'] += 1
            fields[group+'.passed'] += equal
        for item in row['failures']:
            failures[f"{key}:{item['check']}"] = item['differences']
        for item in row['metadata']:
            metadata[f"{key}:{item['check']}"] = item['differences']
        for family in ('lines','structure','cells','rows','segments','checks','stats','glyphs'):
            file = frozen / f"{key}.{family}.{'parquet' if family=='glyphs' else 'json'}"
            if file.exists():
                identity = sha(file)
                frozen_hashes[str(file.relative_to(ROOT))] = identity
                if row['cohort'] == 'development' and family in ('rows', 'structure'):
                    original = ROOT / '.astra/out_after_Q1b' / file.name
                    assert sha(original) == identity, f'Q1b snapshot changed: {file.name}'
                    frozen_hashes[str(original.relative_to(ROOT))] = identity
        if row['cohort'] == 'development':
            expected = json.loads((frozen/f'{key}.rows.json').read_text())
            if expected['blocked_rows']:
                blocked[key] = dict(expected=len(expected['blocked_rows']), actual=row['blocked_rows'],
                                    envelope_equal=row['checks']['frozen.rows'])
    assert len(blocked) == 5 and sum(r['expected'] for r in blocked.values()) == 127
    assert all(r['expected'] == r['actual'] and r['envelope_equal'] for r in blocked.values())
    for family in ('lines', 'structure', 'cells', 'segments', 'checks'):
        assert fields[f'frozen.{family}.total'] == 95, f'Incomplete frozen {family} coverage'
    assert fields['frozen.rows.total'] == 54
    assert fields['runtime.joining.total'] == 1520
    assert fields['runtime.crop_pixels.total'] == 190
    assert fields['runtime.parquet_rows.total'] == 190
    assert len(books['books']) == 168
    assert len(books['frozen_checks']) == 190
    for cohort, count in (('', 54), ('book_pages', 6)):
        frozen = ROOT / '.astra/out_after_Q2' / cohort
        paths = list((frozen / 'books').glob('*.stats.json'))
        assert len(paths) == count
        for path in [*paths, frozen / 'corpus.stats.json']:
            frozen_hashes[str(path.relative_to(ROOT))] = sha(path)
    for item in books['frozen_differences']:
        failures[Path(item['file']).name] = json.loads(Path(item['file']).read_text())
    for item in books['metadata']:
        metadata[item['page_key']+':frozen.stats'] = item['differences']
    all_equal = not failures and books['runtime_equal'] and not test_counts['failures'] and not test_counts['errors']
    receipt = dict(status='DONE' if all_equal else 'NOT DONE', allowlist=ALLOWLIST,
        frame='page_size=(image.width / 3, image.height / 3); default remains source pixels',
        pages=95, development_pages=54, book_pages=41, api_calls=pages['api_calls'],
        option_matrix=dict(tables=[False,True], statistics=[False,True], joining=['off','default','rows','pieces']),
        orientation=False, discounted='keep', strict_geometry=False,
        stage_cache='Per-page complete-input memoization with independent copies; current-run computation only.',
        crops=pages['crops'], comparisons=dict(fields), partial_rows=blocked,
        q1b_original_files_byte_identical_to_q2=108,
        book_variants=books['books'], book_runtime_equal=books['runtime_equal'], book_frozen_equal=books['frozen_equal'],
        book_frozen_checks=books['frozen_checks'], tests=test_counts,
        failing_comparisons=len(failures), difference_counts=dict(Counter(re.sub(r'\[\d+\]', '[]',d['path']) for ds in failures.values() for d in ds)),
        metadata_difference_counts=dict(Counter(re.sub(r'\[\d+\]', '[]',d['path']) for ds in metadata.values() for d in ds)),
        reference_commit=pages['reference_commit'], implementation_source_hashes=source_manifest,
        tool_hashes={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),ROOT/'scripts/pages/check_q3b_books.py']},
        frozen_input_hashes=frozen_hashes,
        layout_input_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'.astra/layout').glob('*.json'))},
        book_selection_sha256=sha(ROOT/'.astra/book_pages/selection.json'),
        page_receipts={r['page_key']:sha(directory/(r['page_key']+'.json')) for r in pages['pages']},
        book_receipt_sha256=sha(directory/'books-summary.json'))
    destination = ROOT/'docs/reviews'
    (destination/'PAGE_LINES_Q3B_EQUALITY.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
    with (destination/'PAGE_LINES_Q3B_DIFFERENCES.json.gz').open('wb') as file:
        with gzip.GzipFile(fileobj=file,mode='wb',mtime=0) as stream:
            stream.write(json.dumps(dict(failures=failures,allowed_metadata=metadata),sort_keys=True,allow_nan=False).encode())
    print(json.dumps(dict(status=receipt['status'],failing_comparisons=len(failures),tests=test_counts,
                          differences=receipt['difference_counts']),indent=2))
    return int(not all_equal)


if __name__ == '__main__':
    raise SystemExit(main())

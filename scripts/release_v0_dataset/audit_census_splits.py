"""Read-only streaming census/registry audit; JSON result on stdout, progress on stderr.

May be piped to the pinned remote Python over SSH: no files or databases are written.
Prepared joins use exact original line IDs, never crop hashes or fuzzy identities.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import resource
import sys
import time


def leakage(occurrences, role_ids):
    def test_split(value):
        return value == 'test' or str(value).endswith('_test')
    return dict(
        heldout_registry_in_prepared_train=[r for r in occurrences if r['role'] == 'train' and r['split'] != 'train'],
        source_heldout_in_prepared_train=[r for r in occurrences if r['role'] == 'train' and
                                        (test_split(r['source_split']) or r['source_split'] == 'dev')],
        registry_test_in_selection_pool=[r for r in occurrences if test_split(r['split']) and r['role'] == 'dev'],
        train_eval_exact_id_overlap=sorted(set(role_ids.get('train', ())) &
            (set(role_ids.get('dev', ())) | set(role_ids.get('test', ())) | set(role_ids.get('reference', ())))))


def audit(lock_path, code_root, target):
    sys.path.insert(0, str(code_root))
    import pyarrow as pa
    import pyarrow.parquet as pq
    pa.set_cpu_count(1)
    pa.set_io_thread_count(1)
    from scripts.release_v0_dataset.book_bridge import BookBridge
    from scripts.release_v0_dataset.common import canonical, row_key, sha

    lock = json.loads(Path(lock_path).read_text())
    census = next(s for s in lock['inputs'] if s['adapter'] == 'census')
    registry = next(s for s in lock['inputs'] if s['name'] == lock['book_bridge']['registry_input'])
    entry = registry['files'][0]
    assert sha(entry['path']) == entry['sha256'] == lock['book_bridge']['registry_sha256']
    bridge = BookBridge(pq.read_table(entry['path']).to_pylist())
    matrix, statuses, dispositions = Counter(), Counter(), Counter()
    conflicts, target_record = {}, None
    by_book = Counter()
    files = []
    started = time.monotonic()
    total = 0
    for entry in census['files']:
        h = hashlib.sha256()
        with open(entry['path'], 'rb') as stream:
            for ordinal, line in enumerate(stream):
                h.update(line)
                if not line.strip():
                    continue
                row = json.loads(line)
                binding = row['binding']
                key = row_key(binding['parent_id'], binding['id'])
                match = bridge.match(row, 'census')
                statuses[match['status']] += 1
                book = bridge.books.get(match['book_id'], {})
                source_split, split = binding.get('split'), book.get('split')
                matrix[canonical([source_split, split])] += 1
                detail = dict(row_key=key, parent_id=binding['parent_id'], row_id=binding['id'],
                              source_split=source_split, split=split, book_id=match['book_id'],
                              disposition=row.get('disposition'), ordinal=ordinal)
                if source_split != split and match['status'] == 'match':
                    if binding['id'] in conflicts:
                        raise ValueError('ambiguous original census ID: ' + binding['id'])
                    conflicts[binding['id']] = detail
                    dispositions[str(row.get('disposition'))] += 1
                    by_book[match['book_id']] += 1
                if key == target:
                    target_record = {**detail, 'binding': binding, 'reasons': row.get('reasons'),
                                     'match': match, 'registry_record': book}
                total += 1
                if total % 100000 == 0:
                    print(f'census rows={total} conflicts={len(conflicts)} seconds={time.monotonic()-started:.1f}', file=sys.stderr, flush=True)
        assert h.hexdigest() == entry['sha256'], 'census hash changed'
        files.append({**entry, 'verified_sha256': h.hexdigest()})
    prepared, occurrences, role_ids = {}, [], defaultdict(set)
    for source in lock['inputs']:
        if source['adapter'] != 'prepared' or source.get('synthetic'):
            continue
        counts = Counter()
        for entry in source['files']:
            for batch in pq.ParquetFile(entry['path']).iter_batches(columns=['line_id', 'split'], batch_size=8192, use_threads=False):
                for row in batch.to_pylist():
                    counts['rows'] += 1
                    lid = row['line_id']
                    if lid in conflicts:
                        counts['conflicting_census_occurrences'] += 1
                        role_ids[source['role']].add(lid)
                        occurrences.append({**conflicts[lid], 'pool': source['pool'], 'role': source['role'],
                                            'prepared_split': row['split']})
        prepared[source['name']] = dict(counts, role=source['role'], pool=source['pool'])
        print('prepared ' + source['name'] + ' ' + str(dict(counts)), file=sys.stderr, flush=True)
    return dict(read_only=True, census_files=files, registry=registry['files'][0],
                lock_path=str(lock_path), code_root=str(code_root), rows=total,
                bridge_statuses=dict(statuses), split_matrix=dict(matrix),
                conflicting_rows=len(conflicts), conflicting_dispositions=dict(dispositions),
                conflicts_by_book=dict(by_book), target=target_record, prepared=prepared,
                conflicting_prepared_occurrences=occurrences,
                **leakage(occurrences, role_ids),
                elapsed_seconds=time.monotonic()-started,
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-lock', type=Path, required=True)
    parser.add_argument('--code-root', type=Path, required=True)
    parser.add_argument('--target', default='00006c0c788df3c4785208faa1dd1fb42b0785c7c660306a2117504e03afba53')
    args = parser.parse_args()
    print(json.dumps(audit(args.input_lock, args.code_root, args.target), ensure_ascii=False, indent=2))

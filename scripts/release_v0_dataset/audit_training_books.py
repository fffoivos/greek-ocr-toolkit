"""Read-only P2i full prepared005/book audit, suitable for SSH python -B -c.

Streams native metadata and only prepared line_id/split columns. No remote
temporary files, image reads, database writes, scheduler or network clients.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import resource
import sys
import time


def audit(lock_path, code_root, target):
    sys.path.insert(0, str(code_root))
    import pyarrow as pa
    import pyarrow.parquet as pq
    from scripts.release_v0_dataset.book_bridge import BookBridge, metadata
    from scripts.release_v0_dataset.common import canonical, row_key, sha
    pa.set_cpu_count(1)
    pa.set_io_thread_count(1)
    started = time.monotonic()
    lock = json.loads(Path(lock_path).read_text())
    registry = next(s for s in lock['inputs'] if s['name'] == lock['book_bridge']['registry_input'])['files'][0]
    assert sha(registry['path']) == registry['sha256'] == lock['book_bridge']['registry_sha256']
    bridge = BookBridge(pq.read_table(registry['path']).to_pylist())
    # Exact native trainer ID mapping; harvest prefixes alone are not enough.
    native, native_files, target_record = {}, [], None
    for source in lock['inputs']:
        if source['name'] != 'harvest':
            continue
        for entry in source['files']:
            h = hashlib.sha256()
            count = 0
            with open(entry['path'], 'rb') as stream:
                for ordinal, line in enumerate(stream):
                    h.update(line)
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    lid = 'harvest:' + row['wave'] + ':' + str(row.get('row_id', row.get('id')))
                    match = bridge.match(metadata(row, 'harvest'), 'harvest')
                    value = (match['book_id'], match['status'], row.get('canonical_book_id'), row.get('book_id'))
                    assert lid not in native or native[lid] == value, 'ambiguous native ID'
                    native[lid] = value
                    key = row_key('harvest:' + row['wave'], row.get('row_id', row.get('id')))
                    if key == target:
                        target_record = dict(row_key=key, trainer_line_id=lid, book_id=match['book_id'],
                            match=match, native_source=source['name'], native_ordinal=ordinal,
                            source_split=row.get('split'), source_title=(row.get('provenance') or {}).get('source_title'))
                    count += 1
                    if count % 100000 == 0:
                        print('native harvest rows=' + str(count), file=sys.stderr, flush=True)
            assert h.hexdigest() == entry['sha256'], 'native metadata SHA changed'
            native_files.append(dict(**entry, rows=count, verified_sha256=h.hexdigest()))
    train, tests, prepared, target_occurrences = Counter(), Counter(), {}, []
    statuses, affected_status, affected_population = Counter(), Counter(), Counter()
    affected_books, train_ids, eval_ids = Counter(), set(), set()
    all_train_books = Counter()
    native_train_books, native_test_books, native_missing = set(), Counter(), Counter()
    for source in lock['inputs']:
        if source['adapter'] != 'prepared' or source.get('synthetic'):
            continue
        counts, metadata_hash = Counter(), hashlib.sha256()
        for entry in source['files']:
            for batch in pq.ParquetFile(entry['path']).iter_batches(columns=['line_id', 'split'], batch_size=8192, use_threads=False):
                for ordinal_row in batch.to_pylist():
                    lid = ordinal_row['line_id']
                    metadata_hash.update((canonical(ordinal_row) + '\n').encode())
                    population = 'harvest' if lid.startswith('harvest:') else 'v4'
                    if population == 'harvest':
                        assert lid in native, 'prepared harvest ID absent from full metadata: ' + lid
                        bid, status, native_canonical, native_book = native[lid]
                        native_keys = {('canonical_book_id', native_canonical), ('book_id', native_book)}
                        native_keys = {k for k in native_keys if k[1] is not None}
                    else:
                        # Exact original-ID mapping, followed by the registry's declared prefix rule.
                        match = bridge.match({'row_id': lid}, 'v4')
                        bid, status = match['book_id'], match['status']
                        native_keys = set()
                    book = bridge.books.get(bid, {})
                    role, pool = source['role'], source['pool']
                    counts['rows'] += 1
                    counts[population] += 1
                    counts['book_' + status] += 1
                    if role == 'train':
                        native_train_books.update(native_keys)
                        if population == 'harvest' and not native_keys:
                            native_missing[role] += 1
                        train_ids.add(lid)
                        train[population, pool] += 1
                        statuses[status] += 1
                        if bid:
                            all_train_books[bid] += 1
                        split = book.get('split')
                        heldout = split in ('dev', 'test', 'hold_out') or str(split).startswith('seal04_')
                        if bid and (heldout or book.get('exportable') is False):
                            affected_population[population, pool] += 1
                            affected_status[split, book.get('assignment_status'), book.get('exportable'), book.get('harvest_protection')] += 1
                            affected_books[bid] += 1
                    elif role in ('dev', 'test', 'reference'):
                        eval_ids.add(lid)
                    if role == 'test':
                        tests[pool, bid, status] += 1
                        for ns, value in native_keys:
                            native_test_books[pool, ns, value] += 1
                        if population == 'harvest' and not native_keys:
                            native_missing[role] += 1
                    if target_record and lid == target_record['trainer_line_id']:
                        target_occurrences.append(dict(source=source['name'], pool=pool, role=role, prepared_split=ordinal_row['split']))
        prepared[source['name']] = dict(counts, pool=source['pool'], role=source['role'],
            metadata_sha256=metadata_hash.hexdigest(), files=source['files'],
            file_verification='metadata columns read; pinned whole-file hashes retained, not rehashed')
        print(source['name'] + ' ' + str(dict(counts)), file=sys.stderr, flush=True)
    totals = Counter()
    overlap = defaultdict(Counter)
    test_matches = Counter()
    for (pool, bid, status), count in tests.items():
        totals[pool] += count
        test_matches[pool, status] += count
        if bid and bid in all_train_books:
            overlap[bid][pool] += count
    books = []
    for bid in sorted(set(affected_books) | set(overlap)):
        book = bridge.books[bid]
        books.append(dict(book=book, affected_train_rows=affected_books[bid],
            all_train_rows=all_train_books[bid], test_rows=dict(overlap[bid]),
            test_split_shares={p: n / totals[p] for p, n in overlap[bid].items()}))
    test_affected = Counter()
    for counts in overlap.values():
        test_affected.update(counts)
    adopted = Path(registry['path']).with_name('ADOPTED_SPLIT.json')
    adopted_info = dict(path=str(adopted), sha256=sha(adopted), record=json.loads(adopted.read_text())) if adopted.exists() else None
    return dict(read_only=True, full_population=True, input_lock=dict(path=str(lock_path), sha256=sha(lock_path)),
        registry=dict(**registry, verified_sha256=sha(registry['path'])), adopted_split=adopted_info,
        native_files=native_files, prepared=prepared, target=target_record,
        target_book=bridge.books.get((target_record or {}).get('book_id')), target_prepared_occurrences=target_occurrences,
        train_rows=sum(train.values()), train_book_match_status=dict(statuses),
        affected_train_rows=sum(affected_books.values()),
        train_by_population_pool={canonical(k): v for k, v in train.items()},
        affected_by_population_pool={canonical(k): v for k, v in affected_population.items()},
        affected_by_registry_status={canonical(k): v for k, v in affected_status.items()},
        affected_by_book=dict(affected_books), books=books,
        test_split_rows=dict(totals), test_book_match_status={canonical(k): v for k, v in test_matches.items()},
        affected_test_rows=sum(test_affected.values()), affected_test_by_split=dict(test_affected),
        affected_test_split_shares={p: test_affected[p] / n for p, n in totals.items()},
        exact_train_eval_id_overlap=sorted(train_ids & eval_ids),
        native_harvest_book_train_test_overlap={canonical(k): n for k, n in native_test_books.items()
            if (k[1], k[2]) in native_train_books}, native_harvest_book_identity_missing=dict(native_missing),
        elapsed_seconds=time.monotonic()-started, peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-lock', type=Path, required=True)
    parser.add_argument('--code-root', type=Path, required=True)
    parser.add_argument('--target', default='03a75ee99f113e3fe2c5793ac465bb208db03e27e720473cc79a059cf0d45366')
    args = parser.parse_args()
    print(json.dumps(audit(args.input_lock, args.code_root, args.target), ensure_ascii=False, indent=2))

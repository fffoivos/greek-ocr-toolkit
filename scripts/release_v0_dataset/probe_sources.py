#!/usr/bin/env python3
"""Offline source inventory. No images are read from Parquet or emitted.

Sampling is explicitly incomplete; --full streams metadata, never decodes images.
All indexes, difference lists and receipts live below --output-dir.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import fnmatch
import gzip
import hashlib
import itertools
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import time

sys.dont_write_bytecode = True
KEY_COLUMNS = {
    'id', 'line_id', 'parent_id', 'row_id', 'row_key', 'page_id', 'box_id',
    'crop_id', 'book_id', 'canonical_book_id', 'edition_id', 'source_doc_id',
    'source_dataset', 'wave', 'release', 'split', 'crop_sha256',
    'source_crop_sha256', 'training_image_sha256', 'image_sha256',
}
BINARY_NAMES = {'image', 'image_png', 'trainer_image', 'content', 'bytes', 'data'}
SOURCE_COLUMNS = KEY_COLUMNS | set(('provider source item edition volume source_title title year page '
    'page_number page_number_convention catalogue_url manifest_url source_url source_record_sha256 '
    'source_record_locator crop_bbox bbox polygon_px polygon_norm box_kind segmenter segmenter_run_id '
    'emitted_index reading_order top_index coordinate_frame frame_status text gt_nfc gt_nfd '
    'label_ids codec_version label_version label_sha256 raw_text raw_text_sha256 corrections_applied '
    'correction_route_statuses source_book_id source_split assignment_status book_registry_sha256 '
    'harvest_protection lqb_row release_excluded_row decision decision_reasons primary_class '
    'trained_in pool trainer_line_id width height').split())
AUTH_VARS = ('HF_TOKEN', 'HUGGING_FACE_HUB_TOKEN', 'HUGGINGFACEHUB_API_TOKEN',
             'HUGGINGFACE_API_KEY', 'GOOGLE_APPLICATION_CREDENTIALS', 'AWS_SECRET_ACCESS_KEY')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), default=str)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str) + '\n')


def offline():
    # Do not inspect values, access token stores, import Hub clients or authenticate.
    if any(os.environ.get(name) for name in AUTH_VARS):
        raise ValueError('credential-free probe: unset authentication environment variables first')
    os.environ.update(HF_HUB_OFFLINE='1', HF_DATASETS_OFFLINE='1',
                      OMP_NUM_THREADS='1', ARROW_NUM_THREADS='1')


def named_path(value):
    name, sep, path = value.partition('=')
    if not sep or not re.fullmatch(r'[A-Za-z0-9_-]+', name):
        raise ValueError('expected unique NAME=/local/path (safe NAME)')
    return name, Path(path).expanduser().absolute()


def prepare_output(output, roots):
    output = output.expanduser().resolve()
    for root in roots:
        root = root.resolve()
        if output == root or root in output.parents or output in root.parents:
            raise ValueError('output and source roots must not overlap')
    # Fresh directory prevents accidental replacement of prior receipts/indexes.
    output.mkdir(parents=True, exist_ok=False)
    return output


def files(root, on_error=None):
    """Do not follow directory or file symlinks outside the declared source root."""
    if root.is_file() and not root.is_symlink():
        yield root
    elif root.is_dir() and not root.is_symlink():
        def failed(exc):
            if on_error is None:
                raise exc
            on_error(exc)
        for directory, dirs, names in os.walk(root, followlinks=False, onerror=failed):
            dirs[:] = sorted(d for d in dirs if not Path(directory, d).is_symlink())
            for name in sorted(names):
                yield Path(directory, name)


def open_text(path):
    return gzip.open(path, 'rt', encoding='utf-8') if path.suffix == '.gz' else path.open(encoding='utf-8')


def kind(path):
    name = path.name.lower()
    if name.endswith('.parquet'):
        return 'parquet'
    if name.endswith(('.jsonl', '.jsonl.gz', '.ndjson')):
        return 'jsonl'
    if name.endswith(('.json', '.json.gz')):
        return 'json'
    return 'stat_only'


def json_records(path, prefix='', kv=False):
    """ijson avoids loading 133 MB build_info or large JSON metadata maps.

    prefix uses ijson notation: item for root arrays, rows.item for arrays in
    objects. --json-map streams one mapping entry as {_map_key,_map_value}.
    No source paths discovered inside records are automatically opened.
    """
    if not prefix and not kv and (path.stat().st_size > 32_000_000 or path.suffix == '.gz'):
        raise RuntimeError('large/compressed JSON requires an explicit --json-array/--json-map selector')
    try:
        import ijson
    except ImportError:
        if path.stat().st_size > 32_000_000 or path.suffix == '.gz':
            raise RuntimeError('ijson required for large/compressed JSON; not scanned')
        with open_text(path) as stream:
            value = json.load(stream)
        for part in filter(None, prefix.split('.')):
            if part == 'item':
                if not isinstance(value, list):
                    raise ValueError('JSON prefix item requires an array')
                break
            value = value[part]
        if not prefix and isinstance(value, list) and not kv:
            raise ValueError('root JSON arrays require --json-array SOURCE|GLOB|item')
        if kv:
            for key, val in value.items():
                yield {'_map_key': key, '_map_value': val}
        elif isinstance(value, list):
            yield from value
        else:
            yield value
        return
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rb') as stream:
        if kv:
            for key, val in ijson.kvitems(stream, prefix):
                yield {'_map_key': key, '_map_value': val}
        else:
            yield from ijson.items(stream, prefix)


def parquet_info(path):
    import pyarrow as pa
    import pyarrow.parquet as pq
    pa.set_cpu_count(1)
    pa.set_io_thread_count(1)
    pf = pq.ParquetFile(path)
    return pf, {f.name: str(f.type) for f in pf.schema_arrow}


def records(path, columns=None, prefix='', kv=False):
    typ = kind(path)
    if typ == 'parquet':
        pf, schema = parquet_info(path)
        # Only explicit metadata columns. Nested binary/image fields cannot be
        # accidentally projected by a wildcard.
        selected = sorted(set(SOURCE_COLUMNS if columns is None else columns) & set(schema) - BINARY_NAMES)
        if not selected:
            return
        for batch in pf.iter_batches(batch_size=512, columns=selected, use_threads=False):
            yield from batch.to_pylist()
    elif typ == 'jsonl':
        with open_text(path) as stream:
            for number, line in enumerate(stream, 1):
                if line.strip():
                    value = json.loads(line)
                    if not isinstance(value, dict):
                        raise ValueError(f'JSONL row {number} is not an object')
                    yield value
    elif typ == 'json':
        yield from json_records(path, prefix, kv)


def key_values(row):
    """Candidate joins preserve types and namespaces, never join on text."""
    for col in KEY_COLUMNS | {'_map_key'}:
        val = row.get(col)
        if isinstance(val, (str, int)) and not isinstance(val, bool):
            yield col, canonical(val)
    if row.get('parent_id') is not None and row.get('row_id') is not None:
        yield 'parent_row', canonical([row['parent_id'], row['row_id']])
    lid = row.get('line_id')
    if isinstance(lid, str) and lid.startswith('harvest:') and len(lid.split(':', 2)) == 3:
        _, wave, original = lid.split(':', 2)
        yield 'harvest_wave_id', canonical([wave, original])
        yield 'harvest_original_id', canonical(original)
    if row.get('wave') is not None and row.get('id') is not None:
        yield 'harvest_wave_id', canonical([row['wave'], row['id']])
    ident = row.get('line_id', row.get('id', row.get('row_id')))
    if isinstance(ident, str):
        if row.get('wave') is not None and not ident.startswith('harvest:'):
            ident = f"harvest:{row['wave']}:{ident}"
        yield 'trainer_id_candidate', canonical(ident)
        if not ident.startswith('harvest:'):
            yield 'nonharvest_id_candidate', canonical(ident)


def field_type(value):
    if value is None:
        return 'null'
    if isinstance(value, bytes):
        return 'binary'
    return type(value).__name__


def discover_paths(row):
    """Only return locator-like strings; never record arbitrary scalar values."""
    if isinstance(row, dict):
        for key, value in row.items():
            if key in BINARY_NAMES:
                continue
            if isinstance(value, str) and (value.startswith(('/iopsstor/', '/capstor/'))
                                           or value.endswith(('.parquet', '/mix.json'))):
                yield value
            elif isinstance(value, (dict, list)):
                yield from discover_paths(value)
    elif isinstance(row, list):
        for value in row:
            yield from discover_paths(value)
    elif isinstance(row, str) and row.startswith(('/iopsstor/', '/capstor/')):
        yield row


class KeyIndex:
    def __init__(self, output):
        self.db = sqlite3.connect(output / 'keys.sqlite')
        self.db.execute('PRAGMA journal_mode=MEMORY')
        # Comparisons may involve millions of keys. Place SQLite spill below
        # output too, rather than using an implicit system temporary directory.
        self.db.execute('PRAGMA temp_store=FILE')
        escaped_output = str(output).replace("'", "''")
        self.db.execute(f"PRAGMA temp_store_directory='{escaped_output}'")
        self.db.execute('PRAGMA cache_size=-16384')
        self.db.execute('CREATE TABLE keys(source TEXT,file TEXT,family TEXT,value TEXT,n INTEGER, '
                        'PRIMARY KEY(source,file,family,value)) WITHOUT ROWID')
        self.pending = []

    def add(self, source, file, row):
        for family, value in key_values(row):
            self.pending.append((source, file, family, value))
        if len(self.pending) >= 4096:
            self.flush()

    def flush(self):
        self.db.executemany('INSERT INTO keys VALUES(?,?,?,?,1) ON CONFLICT(source,file,family,value) '
                            'DO UPDATE SET n=n+1', self.pending)
        self.pending.clear()
        self.db.commit()

    def compare(self, name, left, right, output, complete):
        self.flush()
        for view, selector in [('lhs', left), ('rhs', right)]:
            source, pattern, family = selector
            # Paths use SQLite GLOB (same * syntax as file inventory selectors).
            self.db.execute(f'DROP TABLE IF EXISTS {view}')
            self.db.execute(f'CREATE TABLE {view} AS SELECT value,sum(n) n FROM keys '
                            'WHERE source=? AND file GLOB ? AND family=? GROUP BY value',
                            (source, pattern, family))
            self.db.execute(f'CREATE UNIQUE INDEX {view}_value ON {view}(value)')
        result = {'name': name, 'left': left, 'right': right,
                  'status': 'complete_key_scan' if complete else 'INCOMPLETE_candidate_overlap_only'}
        for view in ('lhs', 'rhs'):
            result[view] = dict(zip(('distinct', 'observations', 'duplicate_keys'),
                self.db.execute(f'SELECT count(*),coalesce(sum(n),0),coalesce(sum(n>1),0) FROM {view}').fetchone()))
        if result['lhs']['observations'] == 0 or result['rhs']['observations'] == 0:
            result['status'] = 'INCOMPLETE_no_observed_keys_on_one_or_both_sides'
        result['intersection'] = self.db.execute('SELECT count(*) FROM lhs JOIN rhs USING(value)').fetchone()[0]
        for side, other in [('lhs', 'rhs'), ('rhs', 'lhs')]:
            count = 0
            path = output / f'{name}.{side}_only.jsonl'
            with path.open('w') as stream:
                for value, n in self.db.execute(f'SELECT a.value,a.n FROM {side} a LEFT JOIN {other} b '
                                               'USING(value) WHERE b.value IS NULL ORDER BY a.value'):
                    stream.write(canonical({'key': json.loads(value), 'observations': n}) + '\n')
                    count += 1
            result[f'{side}_only'] = {'keys': count, 'path': path.name, 'sha256': sha(path)}
        return result


def inventory_source(name, root, output, index, full=False, max_rows=1000, selectors=()):
    started = time.monotonic()
    report = {'name': name, 'root': str(root), 'exists': root.exists(), 'files': 0,
              'bytes': 0, 'tables': [], 'errors': [], 'symlinks_skipped': 0,
              'scan_mode': 'full_metadata' if full else 'sample', 'discovered_paths': []}
    locators = set()
    with (output / f'{name}.files.jsonl').open('w') as listing:
        for path in files(root, on_error=lambda exc: report['errors'].append(
                {'path': str(exc.filename), 'error': f'{type(exc).__name__}: directory unreadable'})):
            rel = path.name if root.is_file() else path.relative_to(root).as_posix()
            if path.is_symlink():
                report['symlinks_skipped'] += 1
                listing.write(canonical({'path': rel, 'kind': 'symlink_skipped'}) + '\n')
                continue
            stat = path.stat()
            entry = {'path': rel, 'bytes': stat.st_size, 'kind': kind(path)}
            listing.write(canonical(entry) + '\n')
            report['files'] += 1
            report['bytes'] += stat.st_size
            if kind(path) == 'stat_only':
                continue
            table = dict(entry, rows_scanned=0, row_count=None, complete=False,
                         schema={}, key_columns=[], sample_keys=[], column_coverage={})
            schema_types = defaultdict(set)
            selected = [(pat, prefix, kv) for src, pat, prefix, kv in selectors
                        if src == name and fnmatch.fnmatchcase(rel, pat)]
            prefix, kv = selected[0][1:] if selected else ('', False)
            table['json_prefix'], table['json_map'] = prefix, kv
            try:
                if kind(path) == 'parquet':
                    pf, table['schema'] = parquet_info(path)
                    table['row_count'] = pf.metadata.num_rows
                iterator = records(path, prefix=prefix, kv=kv)
                # An extra metadata row establishes whether a small sample ended
                # naturally; image columns are never fetched.
                for row in iterator if full else itertools.islice(iterator, max_rows + 1):
                    if not full and table['rows_scanned'] == max_rows:
                        break
                    if not isinstance(row, dict):
                        raise ValueError('JSON selection must yield objects; use --json-map or --json-array')
                    table['rows_scanned'] += 1
                    if kind(path) != 'parquet':
                        for col, val in row.items():
                            schema_types[col].add(field_type(val))
                    for col, val in row.items():
                        coverage = table['column_coverage'].setdefault(col, {'present': 0, 'nonnull': 0})
                        coverage['present'] += 1
                        coverage['nonnull'] += int(val is not None)
                    index.add(name, rel, row)
                    if len(table['sample_keys']) < 5:
                        table['sample_keys'].append({col: val for col, val in row.items()
                            if col in KEY_COLUMNS | {'_map_key'} and isinstance(val, (str, int))
                            and len(str(val)) < 1024})
                    locators.update(discover_paths(row))
                else:
                    table['complete'] = True
                if kind(path) == 'parquet' and table['rows_scanned'] != table['row_count']:
                    table['complete'] = False
                    if table['rows_scanned'] == 0:
                        table['not_scanned_reason'] = 'no selected metadata columns; footer schema/count only'
                if kind(path) != 'parquet':
                    table['schema'] = {col: sorted(types) for col, types in sorted(schema_types.items())}
                    if table['complete']:
                        table['row_count'] = table['rows_scanned']
                table['key_columns'] = sorted(set(table['schema']) & KEY_COLUMNS)
                table['schema_scope'] = 'footer' if kind(path) == 'parquet' else ('all_selected_records' if table['complete'] else 'sample')
                if path.stat().st_size != stat.st_size or path.stat().st_mtime_ns != stat.st_mtime_ns:
                    raise ValueError('source changed during scan')
            except Exception as exc:
                table['complete'] = False
                table['error'] = f'{type(exc).__name__}: {exc}'
                report['errors'].append({'path': rel, 'error': table['error']})
            report['tables'].append(table)
    index.flush()
    report['discovered_paths'] = sorted(locators)
    report['elapsed_seconds'] = round(time.monotonic() - started, 3)
    report['complete_metadata_scan'] = bool(report['exists'] and report['tables']) and not report['errors'] and all(t['complete'] for t in report['tables'])
    report['limitations'] = ['stat bytes are not byte verification', 'Parquet binary columns never read',
        'candidate key overlaps are not proven identity; inspect duplicate counts and namespace',
        'JSON objects count as one record unless an explicit array/map selector is supplied',
        'discovered paths are locators only; pass them explicitly as sources in a later run']
    write_json(output / f'{name}.inventory.json', report)
    return report


def parse_selector(value, kv):
    source, pattern, prefix = value.split('|', 2)
    return source, pattern, prefix, kv


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', action='append', required=True, help='NAME=/local/root (repeat)')
    parser.add_argument('--output-dir', required=True, type=Path, help='new, disjoint directory')
    parser.add_argument('--full', action='store_true', help='stream all selected metadata (CPU job for census)')
    parser.add_argument('--max-rows', type=int, default=1000, help='sample rows per file; no effect with --full')
    parser.add_argument('--json-array', action='append', default=[], help='SOURCE|GLOB|ijson.prefix.item')
    parser.add_argument('--json-map', action='append', default=[], help='SOURCE|GLOB|ijson.prefix; map keys retained')
    parser.add_argument('--compare', action='append', default=[],
        help='NAME=LEFT_SOURCE|GLOB|KEY_FAMILY|RIGHT_SOURCE|GLOB|KEY_FAMILY')
    args = parser.parse_args(argv)
    offline()
    sources = [named_path(x) for x in args.source]
    if len(dict(sources)) != len(sources) or args.max_rows <= 0:
        parser.error('source names must be unique; max-rows must be positive')
    output = prepare_output(args.output_dir, [p for _, p in sources])
    selectors = [parse_selector(x, False) for x in args.json_array] + [parse_selector(x, True) for x in args.json_map]
    index = KeyIndex(output)
    try:
        reports = [inventory_source(n, p, output, index, args.full, args.max_rows, selectors) for n, p in sources]
        comparisons = []
        for value in args.compare:
            name, spec = value.split('=', 1)
            if not re.fullmatch(r'[A-Za-z0-9_-]+', name):
                raise ValueError('invalid comparison name')
            fields = spec.split('|')
            if len(fields) != 6 or fields[0] not in dict(sources) or fields[3] not in dict(sources):
                raise ValueError('comparison needs six fields and declared sources')
            matched = [t for r in reports for t in r['tables']
                       if (r['name'] == fields[0] and fnmatch.fnmatchcase(t['path'], fields[1]))
                       or (r['name'] == fields[3] and fnmatch.fnmatchcase(t['path'], fields[4]))]
            left_tables = [t for r in reports if r['name'] == fields[0] for t in r['tables']
                           if fnmatch.fnmatchcase(t['path'], fields[1])]
            right_tables = [t for r in reports if r['name'] == fields[3] for t in r['tables']
                            if fnmatch.fnmatchcase(t['path'], fields[4])]
            complete = args.full and bool(left_tables) and bool(right_tables) and all(t['complete'] for t in matched)
            comparisons.append(index.compare(name, fields[:3], fields[3:], output, complete))
            comparisons[-1]['matched_left_tables'] = len(left_tables)
            comparisons[-1]['matched_right_tables'] = len(right_tables)
        receipt = {'schema': 'release-v0-source-probe-1', 'script_sha256': sha(__file__),
                   'python_version': sys.version.split()[0],
                   'sources': [{'name': r['name'], 'files': r['files'], 'bytes': r['bytes'],
                                'complete_metadata_scan': r['complete_metadata_scan']} for r in reports],
                   'comparisons': comparisons, 'network_used': False, 'parquet_image_payloads_read': False}
        write_json(output / 'PROBE_RECEIPT.json', receipt)
    finally:
        index.db.close()
    return 2 if any(r['errors'] or not r['exists'] for r in reports) else 0


if __name__ == '__main__':
    raise SystemExit(main())

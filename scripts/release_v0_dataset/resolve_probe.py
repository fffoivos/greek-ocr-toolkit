#!/usr/bin/env python3
"""Read-only Clariden resolver: metadata schemas, nested selectors and candidate joins.

No source writes, credentials, network or image decoding. Only original_crops
reads recorded image files to verify their recorded hashes; no image bytes are emitted.
Only --output-dir is written. Defaults inspect the pinned local release sources;
--plan permits explicit source/selector overrides. Embedded paths are followed
only by the original_crops custody census.
Candidate key equality is evidence for review, never an automatic identity ruling.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import json
import multiprocessing
import os
from pathlib import Path
import queue
import re
import signal
import sqlite3
import sys
import time

sys.dont_write_bytecode = True
# Slurm --export=NONE can discard the wrapper's exported PYTHONPATH. Resolve
# the same private library directory here as well, before spawning readers.
DEFAULT_PYLIB = '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0/pylib'
library_path = str(Path(os.environ.get('REL0_DATASET_PYLIB', DEFAULT_PYLIB)).resolve())
if Path(library_path).is_dir() and library_path not in sys.path:
    # Preserve an explicit PYTHONPATH's precedence; this is a fallback path.
    sys.path.append(library_path)
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = 'scripts.release_v0_dataset'
from .probe_sources import canonical, files, kind, open_text, prepare_output, write_json
from .common import offline, sha
from .book_bridge import BookBridge, metadata, new_coverage, count_coverage
from .original_crops import (CropIndex, FileChecks, CROP_FIELDS, crop_metadata,
                             new_counts, count_result, verify as verify_original)
from .validation_originals import ValidationOriginals

ITEMS = {
    'v4_bridge': ['census', 'v4', 'crops4', 's1', 'old', 'pages', 'boxes', 'observations', 'objects', 'mac'],
    'logical_pages': ['pages', 'observations', 'boxes'],
    'page_frames': ['outcomes', 'observations', 'boxes'],
    'segmenter_page_results': ['outcomes', 'boxes', 'objects', 'observations'],
    'seal04': ['seal', 'census', 's1'],
    'validation_bridge': ['validation', 'census', 's1', 'v4'],
    'row_instruments': ['canonical_registry', 'canonical_instruments', 'book_sources', 's1', 'v4', 'old', 'census', 'harvest', 'seal_original', 'validation', 'synthetic'],
    'book_bridge': ['canonical_registry', 'canonical_instruments', 'book_sources', 's1', 'v4', 'old', 'census', 'harvest', 'seal_original', 'validation', 'synthetic'],
    'harvest_provenance': ['harvest'],
    'original_crops': ['s1', 'v4', 'old', 'census', 'harvest', 'seal_original', 'validation_originals', 'validation'],
    'original_assets': ['crops4', 's1', 'config', 'mac'],
    'raw_segmenter': ['boxes'],
}
# Exact field names are preserved in reports. Aliases below only nominate keys
# to compare; they do not manufacture page ids or strip a line-id namespace.
KEY_NAMES = set(('parent_id row_id row_key line_id trainer_line_id box_id page_id '
    'source_page_id page_object_id page_object_ids_json source_object_id raw_page_index '
    'book_id canonical_book_id edition_id crop_sha256 page_image_sha256 image_sha256 '
    'relative_path crop_relative_path file_name id').split())
BLOCKED = re.compile(r'^(?:image(?:_?bytes|_png|content)?|trainer_image|bytes|content|data|'
                     r'raw_response|response_payload|raw_google_payload|'
                     r'pixels|thumbnail|base64|b64|content_bytes)$', re.I)
REQUESTED_FIELDS = ('catalogue_url', 'manifest_url', 'source_url', 'edition', 'volume',
                    'page_number_convention', 'row_instrument_roles', 's1_asset_relocations',
                    'dimension', 'dimension_json', 'transform', 'transforms', 'coordinate_frame',
                    'detectedLanguages', 'languageCode', 'language', 'emitted_index', 'reading_order')


def default_plan(book_registry_dir=None):
    """Explicit metadata paths, with a separate original-crop source override."""
    spec = json.loads(Path(__file__).with_name('specs').joinpath('source-spec-001.json').read_text())
    sources = {s['name']: s for s in spec['inputs']}
    staging = '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0/sources/hf_archive/staging-v4'
    def selected(name, *names):
        return {**sources[names[0]], 'name': name, 'patterns': [p for n in names for p in sources[n]['patterns']]}
    registry = Path(book_registry_dir or Path(__file__).resolve().parents[2] / 'docs/programme_20261019/registry/book_registry/v2')
    plan = {'sources': [
        {'name': 'canonical_registry', 'patterns': [str(registry / 'book_registry.parquet')],
         'expected_sha256': sources['canonical_books']['expected_sha256']},
        {'name': 'canonical_instruments', 'patterns': [str(registry / 'row_instruments.parquet')],
         'expected_sha256': sources['canonical_instruments']['expected_sha256']},
        {'name': 'book_sources', 'patterns': [str(Path(__file__).with_name('specs') / 'book-sources-v2.jsonl')],
         'expected_sha256': sources['canonical_book_sources']['expected_sha256']},
        selected('synthetic', 'a12_train', 'a12_val', 'a12_reserved'),
        selected('seal_original', 'seal04_original'),
        selected('census', 'census_g2'), selected('v4', 'v4_admissions'),
        selected('crops4', 'crops4_relations'), selected('s1', 's1'),
        selected('old', 'old0', 'old1'), selected('validation', 'prepared_validation'),
        selected('validation_originals', 'validation_originals'),
        selected('harvest', 'harvest'),
        {'name': 'pages', 'patterns': [staging + '/pages/pages.parquet']},
        {'name': 'boxes', 'patterns': [staging + '/provenance/mac/google_boxes/*/*.parquet']},
        {'name': 'outcomes', 'patterns': [staging + '/provenance/mac/*_page_results.parquet']},
        {'name': 'observations', 'patterns': [staging + '/provenance/mac/w_page_observations.parquet']},
        {'name': 'objects', 'patterns': [staging + '/provenance/mac/source_objects.parquet']},
        {'name': 'mac', 'patterns': [staging + '/manifests/mac-artifacts.json',
                                  staging + '/manifests/mac-selection/SOURCE_MANIFEST.json']},
        {'name': 'config', 'patterns': [
            '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-005-genn/data.json',
            '/capstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/mix1_runs/MIX1D-8d25940f-export-001/shared/real/build_info.json',
            '/capstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/mix1_runs/MIX1D-8d25940f-export-001/shared/real_mix.json',
            '/capstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/mix1_runs/MIX1D-8d25940f-export-001/shared/records.jsonl',
            '/capstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/s1_run01/w2_ref_364871/node_binding.json']},
        {'name': 'seal', 'patterns': ['/capstor/scratch/cscs/fffoivos/greek-ocr-e3/benchmark_0.2/seal04/']},
    ]}
    plan['crop_roots'] = spec.get('crop_roots', [])
    # These denominators are measured selections in the frozen source spec.
    counts = spec['population_counts']
    for source in plan['sources']:
        if source['name'] == 'census':
            source['original_crops_source'] = {'expected_rows': counts['census_g2']}
    return plan


class BudgetExpired(Exception):
    pass


class ReaderDependencyError(ImportError):
    pass


def require_ijson():
    try:
        import ijson
    except ImportError as exc:
        raise ReaderDependencyError(
            f'ijson required at startup; no sources scanned: {exc}; '
            f'python={sys.executable}, cwd={os.getcwd()}, '
            f'PYTHONPATH={os.environ.get("PYTHONPATH")!r}, sys.path={sys.path!r}') from exc
    return ijson


def reader_entry(source, messages, import_path, reader):
    # Spawn normally copies sys.path already. Pass the resolved parent path
    # explicitly so private libraries never depend on child startup flags/cwd.
    sys.path[:] = import_path
    try:
        ijson = require_ijson()
    except ReaderDependencyError as exc:
        messages.put(('fatal', str(exc), None))
        messages.put(('done', None, None))
        return
    messages.put(('runtime', {
        'python': sys.executable, 'sys_path': list(sys.path),
        'pythonpath': os.environ.get('PYTHONPATH'), 'cwd': os.getcwd(),
        'ijson_file': str(ijson.__file__), 'ijson_version': getattr(ijson, '__version__', None),
        'ijson_backend': getattr(ijson, 'backend', None),
        'dont_write_bytecode': sys.dont_write_bytecode,
        'isolated': sys.flags.isolated, 'ignore_environment': sys.flags.ignore_environment,
    }, None))
    if source is None:
        messages.put(('done', None, None))
    else:
        reader(source, messages)


class BudgetCursor(sqlite3.Cursor):
    """Translate interrupts at execute *and* fetch/iteration boundaries."""
    def bounded(method):
        def call(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except sqlite3.OperationalError as exc:
                if str(exc) == 'interrupted':
                    raise BudgetExpired('SQLite deadline exhausted; query interrupted') from exc
                raise
        return call

    execute = bounded(sqlite3.Cursor.execute)
    fetchone = bounded(sqlite3.Cursor.fetchone)
    fetchall = bounded(sqlite3.Cursor.fetchall)
    __next__ = bounded(sqlite3.Cursor.__next__)


class BudgetConnection(sqlite3.Connection):
    def execute(self, sql, parameters=()):
        if hasattr(self, 'budget_check'):
            self.budget_check()
        return self.cursor(factory=BudgetCursor).execute(sql, parameters)


def read_source(source, messages):
    """A disposable reader isolates Arrow/ijson and filesystem calls from timers.

    Only this process opens inputs. It owns no SQLite connection. Bounded queues
    keep read-ahead small; the coordinator can terminate a C-level stalled read.
    """
    cache_db = None
    if source.get('crop_file_cache'):
        cache_db = sqlite3.connect(source['crop_file_cache'])
    file_checks = FileChecks(cache_db) if cache_db is not None else None
    try:
        for path, error in source_paths(source):
            if error:
                messages.put(('error', error, None))
                continue
            f = {'path': str(path), 'bytes': path.stat().st_size, 'rows_scanned': 0,
                 'complete': False, 'samples': []}
            if source.get('verify_original_crops') or source.get('validation_original_metadata') or source['name'] in ('canonical_registry', 'canonical_instruments', 'book_sources'):
                f['sha256'] = sha(path)
                if source.get('expected_sha256') and f['sha256'] != source['expected_sha256']:
                    raise ValueError('book bridge metadata SHA256 mismatch: ' + str(path))
            messages.put(('file', dict(f), None))
            batch = []
            try:
                for original in rows(path, f, source.get('json_selector'), source):
                    if source.get('book_metadata_only') and isinstance(original, dict):
                        original = metadata(original, source['book_population'])
                    value = clean(crop_metadata(original, source) if source.get('crop_metadata_only') else original)
                    if source.get('verify_original_crops'):
                        value['_original_crop_probe'] = verify_original(original, {**source, '_path': str(path)}, file_checks=file_checks)
                    batch.append(value)
                    if len(batch) == 512:
                        if cache_db is not None:
                            cache_db.commit()
                        messages.put(('rows', dict(f), batch))
                        batch = []
                if batch:
                    if cache_db is not None:
                        cache_db.commit()
                    messages.put(('rows', dict(f), batch))
                messages.put(('end', dict(f), None))
            except (OSError, ValueError, RuntimeError) as exc:
                if batch:
                    messages.put(('rows', dict(f), batch))
                messages.put(('error', str(path) + ': ' + str(exc), dict(f)))
    except Exception as exc:
        messages.put(('error', str(exc), None))
    finally:
        if cache_db is not None:
            cache_db.commit()
            cache_db.close()
        messages.put(('done', None, None))


def metadata_type(typ):
    """Reject nested binary columns too, before asking Arrow to read a batch."""
    import pyarrow as pa
    if pa.types.is_binary(typ) or pa.types.is_large_binary(typ) or pa.types.is_fixed_size_binary(typ):
        return False
    if pa.types.is_struct(typ):
        return all(metadata_type(f.type) and not BLOCKED.fullmatch(f.name) for f in typ)
    if pa.types.is_list(typ) or pa.types.is_large_list(typ) or pa.types.is_fixed_size_list(typ):
        return metadata_type(typ.value_type)
    if pa.types.is_map(typ):
        return metadata_type(typ.key_type) and metadata_type(typ.item_type)
    return True


def clean(value):
    """Parse nested JSON strings for selectors; remove all byte payloads."""
    if isinstance(value, (bytes, bytearray, memoryview)):
        return None
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items() if not BLOCKED.fullmatch(str(k))}
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, str) and value.lstrip().startswith(('{', '[')):
        try:
            return clean(json.loads(value))
        except ValueError:
            pass
    return value


def flatten(value, prefix=''):
    """[] marks array elements; coverage counts rows, not repeated elements."""
    if prefix:
        yield prefix, value
    if isinstance(value, dict):
        for k, v in value.items():
            yield from flatten(v, prefix + '.' + k if prefix else k)
    elif isinstance(value, list):
        for v in value:
            yield from flatten(v, prefix + '[]')


def sample(value):
    if isinstance(value, dict):
        return {k: sample(v) for k, v in list(value.items())[:60]}
    if isinstance(value, list):
        return [sample(v) for v in value[:5]]
    if isinstance(value, str) and len(value) > 400:
        return value[:400] + ' [truncated]'
    return value


def json_stream(path, selector=None):
    # ijson handles suites/maps without materialising whole documents. Default
    # top-level objects preserve config/relocations contents and nested paths.
    ijson = require_ijson()
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rb') as stream:
        if selector is not None:
            yield from ijson.items(stream, selector)
            return
        first = stream.read(4096).lstrip()[:1]
        stream.seek(0)
        if first == b'[':
            yield from ijson.items(stream, 'item')
        else:
            # Stream top-level entries separately: no unbounded root object.
            for key, value in ijson.kvitems(stream, ''):
                yield {key: value}


def rows(path, report, selector=None, source=None):
    typ = kind(path)
    if typ == 'parquet':
        import pyarrow.parquet as pq
        pf = pq.ParquetFile(path)
        report['schema'] = {f.name: str(f.type) for f in pf.schema_arrow}
        columns = [f.name for f in pf.schema_arrow if not BLOCKED.fullmatch(f.name) and metadata_type(f.type)]
        if (source or {}).get('crop_metadata_only'):
            wanted = set(CROP_FIELDS) | {v.split('.')[0] for v in source.get('fields', {}).values()}
            columns = [f.name for f in pf.schema_arrow if f.name in wanted and metadata_type(f.type)]
        if (source or {}).get('image_storage') == 'embedded_hf_parquet':
            # The sole binary-projection exception. Verify before cleaning/IPC.
            image = source.get('fields', {}).get('image', 'image').split('.')[0]
            if image in pf.schema_arrow.names and image not in columns:
                columns.append(image)
        report['projected_columns'] = columns
        report['row_count'] = pf.metadata.num_rows
        for batch in pf.iter_batches(batch_size=512, columns=columns, use_threads=False):
            yield from batch.to_pylist()
    elif typ == 'jsonl':
        with open_text(path) as stream:
            for line in stream:
                if line.strip():
                    yield json.loads(line)
    elif typ == 'json':
        report['json_selector'] = selector
        report['record_unit'] = 'selected array element' if selector else 'root array element or top-level object entry'
        yield from json_stream(path, selector)


def source_paths(source):
    import glob
    seen = set()
    for pattern in source['patterns']:
        matched = sorted(glob.glob(pattern, recursive=True))
        if not matched:
            yield None, 'no matches: ' + pattern
        for name in matched:
            root = Path(name)
            for path in files(root):
                if path.is_symlink() or kind(path) == 'stat_only' or '.cache' in path.parts:
                    continue
                if path.resolve() in seen:
                    continue
                seen.add(path.resolve())
                yield path, None


class Probe:
    def __init__(self, plan, output, seconds=4800, samples=3, items=None,
                 reporting_seconds=600):
        self.items = list(ITEMS if items is None else items)
        needed = set().union(*(set(ITEMS[i]) for i in self.items))
        self.plan = {**plan, 'sources': [s for s in plan['sources'] if s['name'] in needed]}
        self.bridge_inputs = {}
        self.bridge_engine = None
        self.bridge_special = bool(set(self.items) & {'book_bridge', 'row_instruments'})
        self.bridge_populations = {'s1': 's1', 'v4': 'v4', 'old': 'old', 'census': 'census',
            'harvest': 'harvest', 'seal_original': 'seal04', 'validation': 'validation', 'synthetic': 'synthetic'}
        if self.bridge_special:
            priority = {'canonical_registry': 0, 'canonical_instruments': 1, 'book_sources': 2}
            self.plan['sources'].sort(key=lambda s: priority.get(s['name'], 3))
            if set(self.items) <= {'book_bridge', 'row_instruments'}:
                self.plan['sources'] = [{**s, 'book_metadata_only': True,
                    'book_population': self.bridge_populations[s['name']]} if s['name'] in self.bridge_populations else s
                    for s in self.plan['sources']]
        if 'original_crops' in self.items:
            crop_only = self.items == ['original_crops']
            self.plan['sources'] = [{**s, **s.get('original_crops_source', {}),
                'verify_original_crops': True, 'crop_metadata_only': crop_only,
                'defer_original_mapping': s['name'] == 'census',
                'original_population': self.bridge_populations[s['name']],
                'crop_file_cache': str(Path(output) / 'crop-files.sqlite')}
                if s['name'] in self.bridge_populations else s for s in self.plan['sources']]
            priority = {n: i for i, n in enumerate(ITEMS['original_crops'])}
            if crop_only:
                self.plan['sources'].sort(key=lambda s: priority.get(s['name'], len(priority)))
            else:
                self.plan['sources'].sort(key=lambda s: {
                    'canonical_registry': 0, 'canonical_instruments': 1,
                    'book_sources': 2, 'validation_originals': 3}.get(s['name'], 4))
        self.original_counts, self.original_queries_complete = {}, False
        self.original_files_hashed = 0
        self.crop_root_report = dict(complete=not bool(plan.get('crop_roots')), index_size=0, files=0, roots={})
        self.validation_coverage = dict(rows=0, exact=0, unmatched=0, ambiguous=0, fields={})
        self.output, self.samples = Path(output), samples
        self.started = time.monotonic()
        self.deadline = self.started + seconds
        self.scan_deadline = self.started + max(0, seconds) * .7
        self.active_deadline = self.deadline
        self.reporting_seconds = reporting_seconds
        self.total_deadline = self.deadline + reporting_seconds
        self.db = sqlite3.connect(self.output / 'keys.sqlite', timeout=0, factory=BudgetConnection)
        # Interrupted writes must be rollback-safe; journal_mode=OFF can corrupt
        # an index if a deadline interrupts a B-tree mutation.
        self.db.executescript('''PRAGMA journal_mode=WAL;
          PRAGMA synchronous=NORMAL;
          CREATE TABLE keys(s TEXT, field TEXT, k TEXT, n INTEGER, PRIMARY KEY(s,field,k)) WITHOUT ROWID;
          CREATE TABLE links(s TEXT, record INTEGER, field TEXT, k TEXT);
        ''')
        self.crop_cache_db = sqlite3.connect(self.output / 'crop-files.sqlite') if 'original_crops' in self.items else None
        self.file_checks = FileChecks(self.crop_cache_db) if self.crop_cache_db is not None else None
        if self.crop_cache_db is not None:
            self.crop_cache_db.commit()
        self.crops = CropIndex(self.db, self.file_checks)
        self.validation_originals = ValidationOriginals(self.db)
        self.db.set_progress_handler(lambda: int(time.monotonic() >= self.active_deadline), 1000)
        self.db.budget_check = self.check
        self.reports = {}
        self.link_index_ready = False
        self.cost = {'key_entries_attempted': 0, 'link_rows_attempted': 0,
                     'link_policy': 'only s1.row_id and s1.parent_id+row_id for v4_bridge',
                     'table_bytes': {}, 'table_bytes_complete': False}

    def check(self):
        if time.monotonic() >= self.active_deadline:
            raise BudgetExpired('metadata/query budget exhausted; counts are partial')

    def progress(self, phase, **values):
        stamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(stamp, phase, *(f'{k}={v}' for k, v in values.items()), file=sys.stderr, flush=True)

    def source_progress(self, event, result, started):
        elapsed = max(time.monotonic() - started, 1e-9)
        self.progress('source_' + event, source=result['name'], rows=result['rows_scanned'],
                      rows_per_second=f"{result['rows_scanned'] / elapsed:.1f}",
                      db_bytes=self.db_bytes(),
                      elapsed_seconds=f'{elapsed:.3f}', complete=result['complete'])

    def db_bytes(self):
        return sum(p.stat().st_size for p in self.output.glob('keys.sqlite*') if p.is_file())

    def source_events(self, source, *, startup=False):
        # Spawn, rather than fork, so Arrow and SQLite state is never inherited.
        ctx = multiprocessing.get_context('spawn')
        messages = ctx.Queue(maxsize=2)
        worker = ctx.Process(target=reader_entry,
                             args=(source, messages, list(sys.path), read_source), daemon=True)
        worker.start()
        try:
            while True:
                if not startup:
                    self.check()
                try:
                    timeout = .2 if startup else min(.2, max(.001, self.active_deadline - time.monotonic()))
                    event = messages.get(timeout=timeout)
                except queue.Empty:
                    if not worker.is_alive():
                        raise RuntimeError(f'metadata reader exited without completion: {worker.exitcode}')
                    continue
                if event[0] == 'done':
                    break
                if event[0] == 'fatal':
                    raise ReaderDependencyError(event[1])
                if event[0] == 'runtime':
                    self.reader_runtime = event[1]
                    continue
                yield event
        finally:
            if worker.is_alive():
                worker.terminate()
            worker.join(timeout=.05)
            if worker.is_alive():
                worker.kill()
                worker.join(timeout=.05)
            messages.cancel_join_thread()
            messages.close()

    def bridge_state(self):
        return tuple((n, self.reports.get(n, {}).get('rows_scanned', 0),
                      self.reports.get(n, {}).get('complete', False),
                      tuple(f.get('sha256') for f in self.reports.get(n, {}).get('files', [])))
                     for n in ('canonical_registry', 'canonical_instruments', 'book_sources'))

    def bridge(self):
        if self.bridge_engine is None:
            def digest(name):
                files = self.reports.get(name, {}).get('files', [])
                return files[0].get('sha256') if len(files) == 1 else None
            self.bridge_engine = BookBridge(self.bridge_inputs.get('canonical_registry', []),
                self.bridge_inputs.get('canonical_instruments', []), self.bridge_inputs.get('book_sources', []),
                digest('canonical_registry'), digest('canonical_instruments'))
        return self.bridge_engine

    def bridge_observe(self, name, value):
        if name not in self.reports:
            return  # index() is also used independently by SQL fixture tests.
        if name in ('canonical_registry', 'canonical_instruments', 'book_sources'):
            self.bridge_inputs[name].append(value)
            self.bridge_engine = None
        elif name in self.bridge_populations:
            population = self.bridge_populations[name]
            row = metadata(value, population)
            engine = self.bridge()
            match = engine.match(row, population)
            resolved = engine.resolve(row, population, match)
            result = self.reports[name]
            result['book_bridge_input_state'] = self.bridge_state()
            count_coverage(result['book_bridge_coverage'], resolved,
                           engine.memberships(row, population), match)

    def index(self, name, record, value):
        if self.bridge_special:
            self.bridge_observe(name, value)
            if set(self.items) <= {'book_bridge', 'row_instruments'}:
                return
        entries = set()
        def visit(obj, prefix=''):
            if isinstance(obj, dict):
                # A tuple is only formed from fields in the same object.
                for names in [('parent_id', 'row_id'), ('parent_id', 'id'), ('source_object_id', 'raw_page_index')]:
                    if all(obj.get(k) is not None for k in names):
                        field = prefix + '+'.join(names)
                        entries.add((field, canonical([obj[k] for k in names])))
                for k, v in obj.items():
                    field = prefix + k
                    if k in KEY_NAMES and v is not None and not isinstance(v, dict):
                        for part in v if isinstance(v, list) else [v]:
                            if isinstance(part, (str, int)):
                                entries.add((field + ('[]' if isinstance(v, list) else ''), canonical(part)))
                    visit(v, field + '.')
            elif isinstance(obj, list):
                for v in obj:
                    visit(v, prefix + '[].')
        visit(value)
        if value.get('disposition') == 'ADMIT' and (value.get('binding') or {}).get('split') == 'train':
            entries.update(('admitted_train.' + field, key) for field, key in list(entries)
                           if field.startswith('binding.'))
        for field, key in entries:
            self.db.execute('INSERT INTO keys VALUES(?,?,?,1) ON CONFLICT(s,field,k) DO UPDATE SET n=n+1', (name, field, key))
            self.cost['key_entries_attempted'] += 1
            if 'v4_bridge' in self.items and name == 's1' and field in ('row_id', 'parent_id+row_id'):
                self.db.execute('INSERT INTO links VALUES(?,?,?,?)', (name, record, field, key))
                self.cost['link_rows_attempted'] += 1

    def scan(self, source):
        name = source['name']
        restarting = name in self.reports
        result = {'name': name, 'files': [], 'rows_scanned': 0, 'complete': True, 'errors': [],
                  'nested_field_coverage': {}, 'coverage_per_wave': {}, 'nested_examples': {},
                  'budget_exhausted': False}
        self.reports[name] = result
        if source.get('verify_original_crops'):
            result['original_crops'] = new_counts()
            result['distinct_files_hashed'] = 0
            if source.get('hf_pin'):
                result['hf_pin'] = source['hf_pin']
            if name == 'validation':
                self.validation_coverage = dict(rows=0, exact=0, unmatched=0, ambiguous=0, fields={})
        if self.bridge_special:
            if name in ('canonical_registry', 'canonical_instruments', 'book_sources'):
                self.bridge_inputs[name] = []
                self.bridge_engine = None
            elif name in self.bridge_populations:
                result['book_bridge_coverage'] = new_coverage()
                result['book_bridge_input_state'] = self.bridge_state()
        coverage, wave_counts, wave_rows = defaultdict(Counter), defaultdict(Counter), Counter()
        requested, requested_paths = defaultdict(Counter), defaultdict(set)
        started = time.monotonic()
        keys_before = self.cost['key_entries_attempted']
        links_before = self.cost['link_rows_attempted']
        result['budget_seconds'] = max(0, self.active_deadline - started)
        result['key_coverage'] = []
        result['key_coverage_complete'] = False
        self.source_progress('start', result, started)
        events = None
        try:
            if restarting:
                # Discard every prior key/link and restart record numbering and
                # all in-memory coverage. Attempt costs remain cumulative.
                self.db.rollback()
                self.db.execute('DELETE FROM keys WHERE s=?', (name,))
                self.db.execute('DELETE FROM links WHERE s=?', (name,))
                self.crops.clear(name)
                self.validation_originals.clear(name)
                self.db.commit()
            events = self.source_events(source)
            for event, info, batch in events:
                self.check()
                if event == 'error':
                    result['errors'].append(info)
                    result['complete'] = False
                    if batch is not None:
                        f.update({k: v for k, v in batch.items()
                                  if k not in ('rows_scanned', 'samples', 'complete')})
                elif event == 'file':
                    f = info
                    result['files'].append(f)
                else:
                    # Preserve footer/schema updates without replacing scanned
                    # row counts or samples owned by the coordinator.
                    f.update({k: v for k, v in info.items() if k not in ('rows_scanned', 'samples', 'complete')})
                    if event == 'end':
                        f['complete'] = True
                    elif event == 'rows':
                        for original in batch:
                            self.check()
                            value = original
                            if not isinstance(value, dict):
                                value = {'value': value}
                            result['rows_scanned'] += 1; f['rows_scanned'] += 1
                            if source.get('validation_original_metadata'):
                                self.validation_originals.observe(value, name,
                                    canonical([f['path'], f['rows_scanned'] - 1]), f.get('sha256'))
                                if result['rows_scanned'] % 4096 == 0:
                                    self.db.commit()
                                continue
                            if source.get('verify_original_crops'):
                                custody = value.pop('_original_crop_probe')
                                if source['name'] == 'validation':
                                    value = self.validation_originals.enrich(value)
                                    self.validation_coverage['rows'] += 1
                                    self.validation_coverage[value['validation_original_join']] += 1
                                    for field in value.get('validation_original_provenance', {}).get('filled_fields', []):
                                        fields = self.validation_coverage['fields']
                                        fields[field] = fields.get(field, 0) + 1
                                    custody = verify_original(value, source, file_checks=self.file_checks)
                                    custody['validation_original_join'] = value['validation_original_join']
                                    custody['validation_original_provenance'] = value.get('validation_original_provenance')
                                c = result['original_crops']
                                count_result(c, custody)
                                result['distinct_files_hashed'] += bool(custody.get('file_exists') and
                                    not custody.get('file_check_reused'))
                                self.crops.observe(value, source, canonical([f['path'], f['rows_scanned'] - 1]), custody)
                                if source.get('crop_metadata_only'):
                                    if result['rows_scanned'] % 4096 == 0:
                                        self.db.commit()
                                    if result['rows_scanned'] % 100_000 == 0:
                                        self.source_progress('progress', result, started)
                                    continue
                            flat = defaultdict(list)
                            for field, v in flatten(value):
                                flat[field].append(v)
                            for field, values in flat.items():
                                coverage[field]['present_rows'] += 1
                                coverage[field]['nonnull_rows'] += any(v is not None for v in values)
                                for typ in {type(v).__name__ for v in values}:
                                    coverage[field]['type:' + typ] += 1
                                # Even when panels/provenance occur late in a JSON
                                # document, retain selector-specific review examples.
                                if self.samples and field not in result['nested_examples']:
                                    result['nested_examples'][field] = sample(values[0])
                            wave = str(value.get('wave', '<no wave>'))
                            wave_rows[wave] += 1
                            wave_counts[wave].update(field for field, vs in flat.items() if any(v is not None for v in vs))
                            found = set()
                            for field, values in flat.items():
                                leaf = field.rsplit('.', 1)[-1].removesuffix('[]')
                                if leaf in REQUESTED_FIELDS:
                                    requested_paths[leaf].add(field)
                                    if any(v is not None for v in values):
                                        found.add(leaf)
                            requested[wave].update(found)
                            if len(f['samples']) < self.samples:
                                f['samples'].append(sample(value))
                            self.index(name, result['rows_scanned'], value)
                            if result['rows_scanned'] % 4096 == 0:
                                self.db.commit()
                            if result['rows_scanned'] % 100_000 == 0:
                                self.source_progress('progress', result, started)
        except (BudgetExpired, OSError, ValueError, RuntimeError) as exc:
            result['complete'] = False
            result['budget_exhausted'] = isinstance(exc, BudgetExpired)
            result['errors'].append(str(exc))
        finally:
            if events is not None:
                events.close()
        try:
            self.check()
            self.db.commit()
            self.progress('key_coverage', source=name, event='start')
            result['key_coverage'] = [dict(zip(('selector', 'distinct_keys', 'occurrences', 'duplicate_keys'), r)) for r in
                self.db.execute('SELECT field,COUNT(*),SUM(n),SUM(n>1) FROM keys WHERE s=? GROUP BY field', (name,))]
            result['key_coverage_complete'] = True
            self.progress('key_coverage', source=name, event='end')
        except BudgetExpired as exc:
            self.db.rollback()
            result['complete'] = False
            result['budget_exhausted'] = True
            result['errors'].append(str(exc))
            self.progress('key_coverage', source=name, event='interrupted')
        result['nested_field_coverage'] = dict(coverage)
        result['observed_schema'] = {field: sorted(k[5:] for k in counts if k.startswith('type:'))
                                     for field, counts in coverage.items()}
        result['coverage_per_wave'] = {w: {'rows': wave_rows[w], 'nonnull_rows': dict(c)} for w, c in wave_counts.items()}
        result['requested_field_coverage'] = {w: {'rows': wave_rows[w], 'fields': {
            field: {'nonnull_rows': requested[w][field], 'missing_rows': wave_rows[w] - requested[w][field],
                    'observed_selectors': sorted(requested_paths[field])} for field in REQUESTED_FIELDS}}
            for w in wave_rows}
        if not result['files']:
            result['complete'] = False
            result['errors'].append('no metadata files selected')
        if (source.get('verify_original_crops') or source.get('validation_original_metadata')) and source.get('expected_rows') is not None:
            result['expected_rows'] = source['expected_rows']
            if result['complete'] and result['rows_scanned'] != source['expected_rows']:
                result['complete'] = False
                result['errors'].append('original crop population count differs from selected denominator')
        result['elapsed_seconds'] = time.monotonic() - started
        result['index_cost'] = {
            'key_entries_attempted': self.cost['key_entries_attempted'] - keys_before,
            'link_rows_attempted': self.cost['link_rows_attempted'] - links_before,
            'distinct_keys': sum(r['distinct_keys'] for r in result['key_coverage']),
            'counts_complete': result['complete'],
            'qualification': 'attempts include any interrupted/rolled-back final chunk; '
                             'distinct keys unavailable if key_coverage_complete is false'}
        self.source_progress('end', result, started)
        return result

    def scan_pass(self, source, deadline):
        name = source['name']
        passes = list(self.reports.get(name, {}).get('passes', []))
        started = time.monotonic()
        self.set_deadline(deadline)
        try:
            self.scan(source)
        except BudgetExpired as exc:
            partial = self.reports.setdefault(name, {
                'name': name, 'files': [], 'rows_scanned': 0, 'errors': []})
            partial.update(complete=False, budget_exhausted=True)
            partial['errors'].append(str(exc))
            partial.setdefault('key_coverage', [])
            self.source_progress('end', partial, started)
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
        result = self.reports[name]
        passes.append({'pass': len(passes) + 1, 'budget_seconds': max(0, deadline - started),
                       'elapsed_seconds': time.monotonic() - started,
                       'rows_scanned': result['rows_scanned'], 'complete': result['complete'],
                       'budget_exhausted': result['budget_exhausted'],
                       'errors': list(result['errors']), 'index_cost': result.get('index_cost', {})})
        result['passes'] = passes
        result['elapsed_seconds'] = sum(p['elapsed_seconds'] for p in passes)

    def compare(self, left, lf, right, rf):
        counts = self.db.execute('''SELECT COUNT(*),COALESCE(SUM(l.n),0),COALESCE(SUM(r.n),0),
          COALESCE(SUM(r.n>1),0) FROM keys l JOIN keys r ON r.s=? AND r.field=? AND r.k=l.k
          WHERE l.s=? AND l.field=?''', (right, rf, left, lf)).fetchone()
        ltotal = self.db.execute('SELECT COUNT(*),COALESCE(SUM(n),0) FROM keys WHERE s=? AND field=?', (left, lf)).fetchone()
        rtotal = self.db.execute('SELECT COUNT(*),COALESCE(SUM(n),0) FROM keys WHERE s=? AND field=?', (right, rf)).fetchone()
        return {'left': left, 'left_selector': lf, 'right': right, 'right_selector': rf,
                'left_distinct': ltotal[0], 'right_distinct': rtotal[0], 'matched_distinct': counts[0],
                'left_only_distinct': ltotal[0] - counts[0], 'right_only_distinct': rtotal[0] - counts[0],
                'left_occurrences': ltotal[1], 'matched_left_occurrences': counts[1],
                'right_occurrences': rtotal[1], 'matched_right_occurrences': counts[2],
                'ambiguous_right_keys': counts[3],
                'counts_complete': self.reports[left]['complete'] and self.reports[right]['complete'],
                'qualification': 'candidate equality only; inspect namespace, collisions and row semantics'}

    @staticmethod
    def family(selector):
        tail = selector.rsplit('.', 1)[-1].removesuffix('[]')
        return {'source_page_id': 'page_id', 'trainer_line_id': 'row_alias',
                'row_id': 'row_alias', 'line_id': 'row_alias', 'id': 'row_alias',
                'parent_id+id': 'parent_id+row_id',
                'page_object_ids_json': 'page_object_id', 'page_image_sha256': 'image_sha256',
                'crop_relative_path': 'relative_path'}.get(tail, tail)

    def candidates(self, names, result=None):
        fields = {n: [r['selector'] for r in self.reports[n]['key_coverage']] for n in names}
        # Preserve completed comparisons when a later query is interrupted.
        if result is None:
            result = []
        for i, left in enumerate(names):
            for right in names[i + 1:]:
                for lf in fields[left]:
                    for rf in fields[right]:
                        if self.family(lf) == self.family(rf):
                            self.check()
                            result.append(self.compare(left, lf, right, rf))
        return result

    def old_reconciliation(self):
        """Directional candidate via S1 tuples and exact old line-id equality.

        Refuse a definitive reconciliation when one bare row id names several
        parent tuples. This diagnostic never rewrites the historical-null spec.
        """
        needed = {'census', 's1', 'old'}
        if not needed <= self.reports.keys():
            return {'complete': False, 'reason': 'missing census/s1/old sources'}
        self.check()
        if not self.link_index_ready:
            # Bulk insert only the two reconciliation selectors, then index
            # both lookup directions. Comparisons use keys, never links.
            self.progress('reconciliation', event='link_indexes')
            self.db.execute('CREATE INDEX link_key ON links(s,field,k)')
            self.db.execute('CREATE INDEX link_record ON links(s,record,field,k)')
            self.link_index_ready = True
        self.db.execute('''CREATE TEMP TABLE old_tuples AS SELECT DISTINCT t.k FROM links a
          JOIN keys o ON o.s='old' AND o.field='line_id' AND o.k=a.k
          JOIN links t ON t.s=a.s AND t.record=a.record AND t.field='parent_id+row_id'
          WHERE a.s='s1' AND a.field='row_id' ''')
        self.db.execute('CREATE UNIQUE INDEX old_tuple_key ON old_tuples(k)')
        census_field = 'admitted_train.binding.parent_id+id'
        c = self.db.execute('SELECT COUNT(*) FROM keys WHERE s=? AND field=?', ('census', census_field)).fetchone()[0]
        old = self.db.execute('SELECT COUNT(*) FROM old_tuples').fetchone()[0]
        matched = self.db.execute('''SELECT COUNT(*) FROM keys c JOIN old_tuples o ON o.k=c.k
          WHERE c.s='census' AND c.field=?''', (census_field,)).fetchone()[0]
        ambiguous = self.db.execute('''SELECT COUNT(*) FROM (SELECT a.k FROM links a
          JOIN links t ON t.s=a.s AND t.record=a.record AND t.field='parent_id+row_id'
          WHERE a.s='s1' AND a.field='row_id' GROUP BY a.k HAVING COUNT(DISTINCT t.k)>1)''').fetchone()[0]
        unmapped = self.db.execute('''SELECT COUNT(*) FROM keys o WHERE o.s='old' AND o.field='line_id'
          AND NOT EXISTS(SELECT 1 FROM keys s WHERE s.s='s1' AND s.field='row_id' AND s.k=o.k)''').fetchone()[0]
        complete = all(self.reports[n]['complete'] for n in needed)
        selectors = {'census': census_field, 's1': 'parent_id+row_id', 'old': 'line_id'}
        present = {n: any(r['selector'] == field for r in self.reports[n]['key_coverage'])
                   for n, field in selectors.items()}
        return {'complete': complete, 'census_selector': census_field,
                'old_tuple_bridge': 'old.line_id = s1.row_id; s1.(parent_id,row_id)',
                'census_admitted_train_tuples': c, 'old_union_mapped_tuples': old,
                'census_only': c - matched, 'old_only': old - matched,
                'ambiguous_s1_row_ids': ambiguous, 'unmapped_old_line_ids': unmapped,
                'selectors_present': present,
                'usable_candidate_bridge': complete and all(present.values()) and not ambiguous and not unmapped,
                'qualification': 'candidate bridge; inspect ambiguity, missing selectors and namespace before accepting seven-key direction'}

    def set_deadline(self, deadline):
        self.active_deadline = min(deadline, self.total_deadline)
        if self.timer_active:
            remaining = self.active_deadline - time.monotonic()
            signal.setitimer(signal.ITIMER_REAL, remaining if remaining > 0 else 0)

    def item_report(self, item, joins=None, queries_complete=False, reconciliation=None):
        names = [n for n in ITEMS[item] if n in self.reports]
        missing = sorted(set(ITEMS[item]) - set(names))
        complete = (queries_complete and not missing and
                    all(self.reports[n]['complete'] for n in names))
        if item == 'v4_bridge':
            reconciliation = reconciliation or {'complete': False, 'reason': 'not run within budget'}
            complete = complete and reconciliation['complete']
        report = {'item_id': item, 'complete': complete, 'complete_metadata_scan': complete,
                  'missing_sources': missing, 'sources': {n: self.reports[n] for n in names},
                  'candidate_joins': joins or [], 'candidate_joins_complete': queries_complete,
                  'resolved': False,
                  'limitations': ['No image bytes read or emitted; Parquet schemas are footer metadata.',
                      'Missing selectors have zero observed coverage; sampled rows are truncated.',
                      'All counts refer to scanned records; partial/error sources never certify coverage.',
                      'No tuple is derived by splitting a bare line_id or by equality of crop bounds.',
                      'Source paths embedded in records are reported only, never followed.',
                      'Coordinator must choose typed joins after review; metadata scan alone is not resolution.']}
        if item in ('book_bridge', 'row_instruments'):
            populations = {self.bridge_populations[n]: self.reports[n].get('book_bridge_coverage', new_coverage())
                           for n in names if n in self.bridge_populations}
            stable = all(self.reports[n].get('book_bridge_input_state') == self.bridge_state()
                         for n in names if n in self.bridge_populations)
            report.update(populations=populations, complete=complete and stable,
                          complete_metadata_scan=complete and stable, registry_inputs_stable=stable,
                          decision='pending_resolve: book_bridge',
                          bridge_rule='Exact typed alias equality; registry.prefix for book identity only; '
                                      'instruments use exact original line IDs. Union all book candidates; >1 is ambiguous.',
                          population_unit='source observations; populations overlap; old is the two pinned shards',
                          limitations=['No image bytes read; source values remain literal, never URL templates.',
                                       'Counts are partial unless every input scan is complete and registry inputs are stable.',
                                       'No inference from factory IDs or crop paths; no prefix instrument membership.'])
        if item == 'original_crops':
            complete = complete and self.original_queries_complete
            population_status = {}
            for name in ITEMS[item]:
                if name not in self.bridge_populations:
                    continue
                pop = self.bridge_populations[name]
                source = self.reports.get(name, {})
                counts = self.original_counts.get(pop, {})
                done = bool(self.original_queries_complete and source.get('complete') and
                            counts.get('rows') == source.get('rows_scanned'))
                population_status[pop] = dict(counts_complete=done,
                    status='resolved' if done and counts['custody_established'] == counts['rows']
                           else 'pending_resolve: original_crops',
                    expected_rows=source.get('expected_rows'))
            unresolved = [p for p, c in population_status.items() if c['status'] != 'resolved']
            report.update(complete=complete, complete_metadata_scan=complete,
                populations=self.original_counts,
                decision='resolved' if complete and not unresolved else 'pending_resolve: original_crops',
                pending_populations=unresolved, population_status=population_status,
                resolved=complete and not unresolved, counts_complete=complete,
                population_unit='ALL selected source rows; overlapping populations; no admission/split filter',
                distinct_files_hashed=self.original_files_hashed,
                content_index=self.crop_root_report, validation_originals=self.validation_coverage,
                census_expected_rows=592466,
                limitations=['Recorded files hashed once per distinct path in this run; trainer payloads excluded.',
                    'Harvest Image.bytes read from pinned HF parquet; Image.path and file_name never opened.',
                    'Missing harvest hashes use flagged HF pin plus per-row byte SHA256, not recorded-hash equality.',
                    'Declared crop roots are fully hashed once; only recorded SHA256 equality supplies index custody.',
                    'Seal04 paths resolve against each panel directory; validation joins exact admitted id to line_id.',
                    'Census reuses verified crop_sha256 identity; hash equality does not manufacture a row identity.',
                    'recorded_path counts usable recorded paths; unresolved relative strings count only as recorded_locator.',
                    'Relative paths require the declared spec root and its evidence.',
                    'Counts remain partial unless every source and the mapping census complete.',
                    'Per-row hashes, exact mapping keys and flagged custody remain in keys.sqlite.'])
        if item == 'v4_bridge':
            report['census_old_reconciliation'] = reconciliation
        return report

    def atomic_json(self, path, report):
        temporary = path.with_suffix(path.suffix + '.tmp')
        try:
            write_json(temporary, report)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)

    def write_reports(self, reports):
        # No SQL here, including counts or dbstat. Reports are memory snapshots.
        self.progress('write', event='start')
        summary = []
        for item, report in reports.items():
            self.atomic_json(self.output / (item + '.json'), report)
            summary.append({'item': item, 'complete': report['complete'],
                            'sources': len(report['sources']),
                            'rows_scanned': sum(r['rows_scanned'] for r in report['sources'].values()),
                            'candidate_joins': len(report['candidate_joins'])})
        self.cost['db_bytes'] = self.db_bytes()
        self.cost['rows_scanned'] = sum(r['rows_scanned'] for r in self.reports.values())
        self.cost['distinct_keys'] = sum(k['distinct_keys'] for r in self.reports.values()
                                         for k in r.get('key_coverage', []))
        self.cost['distinct_keys_complete'] = all(r.get('key_coverage_complete', False)
                                                  for r in self.reports.values())
        self.atomic_json(self.output / 'SUMMARY.json', {
            'items': summary, 'complete': all(r['complete'] for r in summary),
            'elapsed_seconds': time.monotonic() - self.started,
            'probe_sha256': __import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest(),
            'reader_runtime': getattr(self, 'reader_runtime', None),
            'parent_sys_path': list(sys.path),
            'plan': self.plan, 'cost': self.cost,
            'budget': {'work_seconds': self.deadline - self.started,
                       'reporting_allowance_seconds': self.reporting_seconds,
                       'policy': '70% for scans including coverage: first pass shares time equally among '
                                 'remaining sources, then budget-exhausted sources restart with all remaining '
                                 'scan time, replacing prior rows/keys; passes retain attempt costs; '
                                 '30% reserved for item queries, shared equally '
                                 'among remaining items; reporting performs no SQL'},
            'qualification': 'read-only metadata evidence; coordinator review required'})
        table = '| Item | Complete scan | Sources | Scanned records | Candidate joins |\n|---|---|---:|---:|---:|\n'
        for r in summary:
            table += f"| {r['item']} | {r['complete']} | {r['sources']} | {r['rows_scanned']} | {r['candidate_joins']} |\n"
        temporary = self.output / 'SUMMARY.md.tmp'
        try:
            temporary.write_text(table)
            temporary.replace(self.output / 'SUMMARY.md')
        finally:
            temporary.unlink(missing_ok=True)
        self.progress('write', event='end')
        return summary

    def run(self):
        # Check both interpreters before even the first source is enumerated.
        # Imports are startup work, as are the module's Arrow imports above.
        require_ijson()
        for _ in Probe.source_events(self, None, startup=True):
            pass
        self.timer_active = False
        # Durable conservative fallbacks precede every scan/query. Atomic final
        # writes preserve these if reporting itself exhausts its allowance.
        reports = {item: self.item_report(item) for item in self.items}
        summary = self.write_reports(reports)
        previous = signal.getsignal(signal.SIGALRM)
        previous_timer = signal.getitimer(signal.ITIMER_REAL)
        def alarm(signum, frame):
            raise BudgetExpired('phase deadline exhausted; interrupted Python processing')
        signal.signal(signal.SIGALRM, alarm)
        self.timer_active = True
        try:
            if 'original_crops' in self.items and self.plan.get('crop_roots'):
                self.set_deadline(self.scan_deadline)
                self.file_checks.build(self.plan['crop_roots'], self.check,
                    lambda **kw: self.progress('crop_index', **kw), self.crop_root_report)
            self.progress('scan', event='start', sources=len(self.plan['sources']))
            for i, source in enumerate(self.plan['sources']):
                now = time.monotonic()
                share = max(0, self.scan_deadline - now) / (len(self.plan['sources']) - i)
                # Expired/zero shares still produce a named incomplete source.
                self.scan_pass(source, now + share)
            for source in self.plan['sources']:
                result = self.reports[source['name']]
                if (not result['complete'] and result['budget_exhausted']
                        and time.monotonic() < self.scan_deadline):
                    self.scan_pass(source, self.scan_deadline)
            self.progress('scan', event='end')
            for i, item in enumerate(self.items):
                joins, queries_complete, reconciliation = [], False, None
                now = time.monotonic()
                self.set_deadline(now + max(0, self.deadline - now) / (len(self.items) - i))
                names = [n for n in ITEMS[item] if n in self.reports]
                self.progress('candidates', item=item, event='start')
                try:
                    self.check()
                    if item == 'original_crops':
                        self.original_counts = {}
                        self.crops.coverage(self.check, lambda **kw: self.progress('original_crops_progress', **kw),
                                            populations=self.original_counts)
                        # Count the actual shared cache, including read-ahead
                        # from an interrupted/restarted source pass.
                        cache_path = self.output / 'crop-files.sqlite'
                        if cache_path.exists():
                            cache = sqlite3.connect(cache_path, timeout=0, factory=BudgetConnection)
                            try:
                                cache.budget_check = self.check
                                cache.set_progress_handler(lambda: int(time.monotonic() >= self.active_deadline), 1000)
                                self.original_files_hashed = cache.execute('SELECT COUNT(*) FROM crop_file_checks').fetchone()[0]
                            finally:
                                cache.close()
                        self.original_queries_complete = self.crop_root_report['complete']
                    elif item not in ('book_bridge', 'row_instruments'):
                        joins = self.candidates(names, joins)
                    queries_complete = True
                    self.progress('candidates', item=item, event='end', joins=len(joins))
                    if item == 'v4_bridge':
                        self.progress('reconciliation', item=item, event='start')
                        reconciliation = self.old_reconciliation()
                        self.progress('reconciliation', item=item, event='end')
                except BudgetExpired as exc:
                    self.progress('queries', item=item, event='interrupted', reason=str(exc))
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                reports[item] = self.item_report(item, joins, queries_complete, reconciliation)
            self.set_deadline(self.deadline)
            try:
                self.check()
                self.progress('cost', event='start')
                self.cost['table_bytes'] = dict(self.db.execute('SELECT name,SUM(pgsize) FROM dbstat GROUP BY name'))
                self.cost['table_bytes_complete'] = True
                self.progress('cost', event='end')
            except (BudgetExpired, sqlite3.OperationalError) as exc:
                self.cost['table_bytes_reason'] = str(exc)
        except BudgetExpired as exc:
            self.progress('work', event='interrupted', reason=str(exc))
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            # Never extend work to spend the reporting allowance on queries.
            # Freeze SQL at the work deadline even while Python writes reports.
            self.active_deadline = self.deadline
            self.db.set_progress_handler(lambda: 1, 1)
            signal.setitimer(signal.ITIMER_REAL, max(.000001, self.total_deadline - time.monotonic()))
            try:
                # Refresh partial source evidence even if work was interrupted
                # before the per-item loop could construct its snapshots.
                for item, report in reports.items():
                    reports[item] = self.item_report(item, report['candidate_joins'],
                        report['candidate_joins_complete'], report.get('census_old_reconciliation'))
                summary = self.write_reports(reports)
            except BudgetExpired:
                self.progress('write', event='allowance_exhausted',
                              fallback='durable partial item JSONs and SUMMARY retained')
                summary = json.loads((self.output / 'SUMMARY.json').read_text())['items']
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                self.timer_active = False
                signal.signal(signal.SIGALRM, previous)
                signal.setitimer(signal.ITIMER_REAL, *previous_timer)
        return summary


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, help='explicit JSON sources [{name,patterns,json_selector?}]')
    p.add_argument('--output-dir', required=True, type=Path)
    p.add_argument('--book-registry-dir', type=Path, help='coordinator-copied v2 directory with book_registry.parquet and row_instruments.parquet')
    p.add_argument('--budget-seconds', type=int, default=4800, help='metadata/comparison budget, at most 80 min')
    p.add_argument('--samples', type=int, default=3)
    p.add_argument('--items', help='comma-separated item ids (default: all)')
    p.add_argument('--reporting-seconds', type=float, default=600,
                   help='SQL-free reporting allowance after work deadline, >0 and at most 600 s')
    args = p.parse_args(argv)
    if not 1 <= args.budget_seconds <= 4800 or not 0 <= args.samples <= 10:
        p.error('budget must be 1..4800 seconds; samples 0..10')
    if not 0 < args.reporting_seconds <= 600:
        p.error('reporting-seconds must be >0 and <=600')
    items = list(ITEMS) if args.items is None else [i.strip() for i in args.items.split(',')]
    if not items or len(items) != len(set(items)) or any(i not in ITEMS for i in items):
        p.error('--items requires distinct known item ids: ' + ','.join(ITEMS))
    offline()
    require_ijson()
    plan = json.loads(args.plan.read_text()) if args.plan else default_plan(args.book_registry_dir)
    if args.plan and args.book_registry_dir:
        replacements = {'canonical_registry': 'book_registry.parquet', 'canonical_instruments': 'row_instruments.parquet'}
        plan['sources'] = [s for s in plan['sources'] if s['name'] not in replacements] + [
            {'name': n, 'patterns': [str(args.book_registry_dir / f)]} for n, f in replacements.items()]
    names = [s['name'] for s in plan['sources']]
    if len(names) != len(set(names)) or not set(names) <= set().union(*map(set, ITEMS.values())):
        p.error('sources must have distinct known names')
    needed = set().union(*(set(ITEMS[i]) for i in items))
    plan = {**plan, 'sources': [s for s in plan['sources'] if s['name'] in needed]}
    # Check the literal prefix of every selected glob, including nonexistent roots.
    roots = [Path(re.split(r'[*?\[]', pat, maxsplit=1)[0]).parent if re.search(r'[*?\[]', pat) else Path(pat)
             for s in plan['sources'] for pat in
             ({**s, **s.get('original_crops_source', {})} if 'original_crops' in items else s)['patterns']]
    if 'original_crops' in items:
        roots.extend(Path(root['path']) for root in plan.get('crop_roots', []))
    output = prepare_output(args.output_dir, roots)
    probe = Probe(plan, output, args.budget_seconds, args.samples, items, args.reporting_seconds)
    try:
        result = probe.run()
    finally:
        probe.db.close()
        if probe.crop_cache_db is not None:
            probe.crop_cache_db.close()
    print((output / 'SUMMARY.md').read_text())
    return 0 if all(r['complete'] for r in result) else 2


if __name__ == '__main__':
    sys.exit(main())

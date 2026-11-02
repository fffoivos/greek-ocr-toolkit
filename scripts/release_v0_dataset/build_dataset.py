#!/usr/bin/env python3
"""Build a release from an explicit, hash-locked local source selection.

Run as a script or module. No network, Hub, scheduler submission, git or GPU API.
See COMMANDS.md for the source-spec and lock contract.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import closing
import gzip
import itertools
import json
import math
import os
from pathlib import Path
import platform
import re
import sqlite3
import sys
import time
import tempfile
import unicodedata as ud

sys.dont_write_bytecode = True
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = 'scripts.release_v0_dataset'
from .common import (Assets, CAP, TARGET, PINS, SOURCE_FIELDS, SYNTHETIC_MATCH_FIELDS, TABLES, VERSION, Shards,
                     atomic_json, canonical, digest, dimensions, get, info, mapped,
                     offline, parallel_info, pending_resolvers, records, row_key, safe_path, sanitize, sha, verify_file, synthetic_match_group)
from .cursors import positioned_records
from .progress import Progress
from . import layered, card
from .deadline import Deadline, BuildPaused, atomic_boundary, active_deadline
from .relations import (ENTITIES, check_partners, contextual, diagnostic, failure, origin, source_record)
from .features import Features, FEATURE_VERSION
from .original_crops import CropIndex, eligible as crop_eligible, build_file_index, custody_kind, hash_mismatch
from .original_inputs import OriginalPayloads
from .validation_originals import ValidationOriginals, FIELDS as VALIDATION_ORIGINAL_FIELDS
from .book_bridge import BookBridge, metadata, original_ids, new_coverage, count_coverage
from .write_bindings import SOURCE_BINDINGS, WriteBindings, native_page_fields, source_values
from . import book_id_policy

DEFAULT_KEYS = {'pages': ['page_id'], 'page_images': ['page_object_id'],
                'page_frames': ['page_frame_id'], 'boxes': ['box_id'],
                'segmenter_page_results': ['segmenter_run_id', 'page_id'],
                'rows': ['row_key'], 'label_versions': ['label_version_id'],
                'row_features': ['row_key', 'label_variant', 'feature_version'],
                'row_instruments': ['row_key', 'kind', 'list_name', 'list_sha256'],
                'references': ['reference_id'], 'book_registry': ['book_id'],
                'book_sources': ['book_id', 'source_locator'],
                'training_membership': ['membership_id'],
                'synthetic': ['factory_build_id', 'split', 'source_shard', 'source_ordinal']}

HISTORICAL_UNKNOWNS = {
    'a12.font_file_sha256', 'a12.text_origin_locator', 'a12.text_origin_sha256',
    'a12.historical_generator_code_sha256', 'a12.historical_generator_binary_sha256',
    'a12.per_line_seed', 'a12.operation_parameters',
    'census_old_seven_key_reconciliation', 'audit.removal_and_repeat_witnesses',
    'joins.rows_to_boxes_pages_books',
    'tables.pages', 'tables.page_frames', 'tables.segmenter_page_results',
}

HISTORICAL_TABLE_BINDINGS = {name: 'tables.' + name for name in
                             ('pages', 'page_frames', 'segmenter_page_results', 'row_instruments')}


def validate_spec(spec_path):
    """Validate structure without opening source paths; pending joins remain explicit.

    Historical unknowns are non-blocking metadata, never executable selectors.
    Full relation/identity checks still run in read_lock and acceptance.
    """
    import jsonschema
    spec = json.loads(Path(spec_path).read_text())
    schema = json.loads(Path(__file__).with_name('specs').joinpath('SOURCE_SPEC.schema.json').read_text())
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(spec),
                    key=lambda e: str(list(e.absolute_path)))
    if errors:
        raise ValueError('source spec: ' + '; '.join(
            '.'.join(map(str, e.absolute_path)) + ': ' + e.message for e in errors))
    for entry in spec.get('unresolved_bindings', []):
        if entry.get('historical_unknown') and entry['field'] not in HISTORICAL_UNKNOWNS:
            raise ValueError('historical_unknown is not allowed for ' + entry['field'])
        if entry.get('status') == 'pending_resolve: original_crops' and entry['field'] != 'assets.original_crops':
            raise ValueError('original crop pending status on unrelated binding')
    for source in spec['inputs']:
        if source.get('image_root') and (not Path(source['image_root']).is_absolute() or not source.get('image_root_evidence')):
            raise ValueError('original crop root needs an absolute path and evidence: ' + source['name'])
        crop_source = source.get('original_crops_source', {})
        if crop_source and crop_source['hf_pin']['revision'] != spec['hf_pins']['harvest-20261025']:
            raise ValueError('original harvest crop source must use the pinned HF revision')
    for root in spec.get('crop_roots', []):
        if not Path(root['path']).is_absolute() or not root.get('evidence'):
            raise ValueError('crop index root needs an absolute path and evidence')
    root_names = [r['name'] for r in spec.get('crop_roots', [])]
    if len(set(root_names)) != len(root_names):
        raise ValueError('duplicate crop root name')
    names = [s['name'] for s in spec['inputs']]
    if len(set(names)) != len(names):
        raise ValueError('duplicate source name')
    if spec.get('book_bridge'):
        binding = spec['book_bridge']
        for name, table in (('registry_input', 'book_registry'), ('instruments_input', 'row_instruments'),
                            ('sources_input', 'book_sources')):
            selected = next((s for s in spec['inputs'] if s['name'] == binding[name]), {})
            if selected.get('adapter') != 'table' or selected.get('table') != table:
                raise ValueError('book bridge needs selected table ' + table)
    keysets = {s['keyset'] for s in spec['inputs'] if s.get('keyset')}
    keysets.update(spec.get('keyset_unions', {}))
    for bridge in spec.get('keyset_bridges', []):
        if bridge['name'] in keysets or not {bridge['left'], bridge['right']} <= keysets:
            raise ValueError('keyset bridge needs existing sources and a fresh output: ' + bridge['name'])
        keysets.add(bridge['name'])
    return spec


def expand(patterns, base):
    import glob
    result = []
    for pattern in patterns:
        p = Path(pattern)
        found = sorted(glob.glob(str(p if p.is_absolute() else base / p), recursive=True))
        if not found:
            raise ValueError('source pattern has no matches: ' + pattern)
        for name in found:
            path = Path(name).absolute()
            if path.is_symlink() or not path.is_file():
                raise ValueError('input must be a regular non-symlink file: ' + name)
            result.append(path)
    if len(result) != len(set(result)):
        raise ValueError('overlapping patterns select the same input twice')
    return result


def freeze(spec_path, dest):
    """A separate CPU preparation step, never invents source globs or selectors."""
    spec_path = Path(spec_path).resolve()
    spec = validate_spec(spec_path)
    if Path(dest).exists():
        raise ValueError('lock output must be fresh')
    spec['schema'] = VERSION
    spec['source_spec'] = info(spec_path)
    names = set()
    for source in spec['inputs']:
        if source['name'] in names:
            raise ValueError('duplicate source name')
        names.add(source['name'])
        source['files'] = [info(p) for p in expand(source.pop('patterns'), spec_path.parent)]
        if source.get('original_crops_source'):
            payload = source['original_crops_source']
            payload['files'] = [info(p) for p in expand(payload.pop('patterns'), spec_path.parent)]
        if source.get('book_bridge_metadata') and (len(source['files']) != 1 or
                source['files'][0]['sha256'] != source['expected_sha256']):
            raise ValueError('book bridge metadata SHA256 mismatch: ' + source['name'])
        if source.get('validation_original_metadata') and source.get('expected_sha256') and (
                len(source['files']) != 1 or source['files'][0]['sha256'] != source['expected_sha256']):
            raise ValueError('validation original metadata SHA256 mismatch: ' + source['name'])
    for adapter in spec.get('label_variant_adapters', []):
        adapter['files'] = [info(p) for p in expand(adapter.pop('patterns'), spec_path.parent)]
    spec['assets'] = [info(p) for p in expand(spec.get('assets', []), spec_path.parent)]
    for key in ('codec', 'scripts'):
        path = Path(spec['features'][key])
        spec['features'][key] = info(path if path.is_absolute() else spec_path.parent / path)
        expected = spec['features'].get(key + '_sha256')
        if expected and spec['features'][key]['sha256'] != expected:
            raise ValueError('feature SHA256 mismatch: ' + key)
    cache_path = Path(dest).resolve().with_name(Path(dest).name + '.crop-index.sqlite')
    if spec.get('crop_roots') and cache_path.exists():
        raise ValueError('crop index output must be fresh: ' + str(cache_path))
    with tempfile.TemporaryDirectory(prefix='rel0-freeze-crops-') as scratch:
        with sqlite3.connect(Path(scratch) / 'index.sqlite') as db:
            _, report = build_file_index(db, spec.get('crop_roots', []), require_pins=False)
            for root in spec.get('crop_roots', []):
                measured = report['roots'][root['name']]['index']
                if root.get('index'):
                    if root['index']['sha256'] != measured['sha256']:
                        raise ValueError('crop root index digest/count mismatch: ' + root['name'])
                    WriteBindings({}, None).coverage('crop root index digest/count mismatch: ' + root['name'],
                                                    measured['files'], root['index']['files'], exact=True)
                root['index'] = measured
            if spec.get('crop_roots'):
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                partial = cache_path.with_suffix('.sqlite.partial')
                with closing(sqlite3.connect(partial)) as cached:
                    db.backup(cached)
                partial.replace(cache_path)
                spec['crop_index_cache'] = {**info(cache_path), 'version': 1}
    atomic_json(dest, sanitize(spec))
    return spec


def read_lock(path, smoke=None):
    lock = json.loads(Path(path).read_text())
    if lock.get('schema') != VERSION:
        raise ValueError('unsupported input lock schema')
    if not re.fullmatch(r'v0\.\d+', lock['dataset_version']):
        raise ValueError('dataset_version must be v0.n')
    if lock.get('hf_pins') != PINS:
        raise ValueError('both full archive commits must match the release pins')
    if len(lock.get('models', [])) != 3 or len(set(lock['models'])) != 3:
        raise ValueError('supply the three distinct v0 model ids')
    if lock['features']['unicode_version'] != ud.unidata_version:
        raise ValueError('Unicode version mismatch')
    for source in lock['inputs']:
        if not source['files']:
            raise ValueError('empty source selection: ' + source['name'])
    if not smoke:
        adapters = {s['adapter'] for s in lock['inputs']}
        needed = {'census', 's1', 'harvest', 'prepared', 'synthetic', 'evidence'}
        if not needed <= adapters:
            raise ValueError('missing source adapters: ' + ','.join(sorted(needed - adapters)))
        targets = {s.get('table') for s in lock['inputs']}
        # S4h permits only explicitly recorded, non-blocking historical nulls.
        # This admits a build with published gaps, not independent acceptance.
        historical = {e['field'] for e in lock.get('unresolved_bindings', [])
                      if e.get('historical_unknown') and e.get('value') is None
                      and e.get('blocks_freeze') is False and e.get('blocks_smoke') is False}
        targets |= {table for table, field in HISTORICAL_TABLE_BINDINGS.items() if field in historical}
        if not {'pages', 'boxes', 'page_frames', 'segmenter_page_results', 'book_registry',
                'references', 'row_instruments'} <= targets:
            raise ValueError('all source relations must be explicitly selected in the source spec')
        if not lock.get('reconciliations') or not lock.get('expected_counts'):
            raise ValueError('full release needs keyed reconciliations and expected counts')
    return lock


class Store:
    def __init__(self, path, validate=None, resolve_book_conflict=None):
        self.validate = validate
        self.resolve_book_conflict = resolve_book_conflict
        self.db = sqlite3.connect(path)
        deadline = active_deadline.get()
        if deadline is not None:
            self.db.set_progress_handler(deadline.interrupt_sql, 10000)
        self.db.executescript('''
          PRAGMA journal_mode=WAL;
          PRAGMA synchronous=NORMAL;
          PRAGMA cache_size=-131072;
          PRAGMA temp_store=FILE;
          PRAGMA wal_autocheckpoint=16384;
          CREATE TABLE IF NOT EXISTS ingest_cursor(stage TEXT PRIMARY KEY,ordinal INTEGER,byte_offset INTEGER,books TEXT);
          CREATE TABLE IF NOT EXISTS records(t TEXT,k TEXT,j TEXT,page TEXT,PRIMARY KEY(t,k));
          CREATE TABLE IF NOT EXISTS payloads(h TEXT PRIMARY KEY,b BLOB,w INTEGER,height INTEGER);
          CREATE TABLE IF NOT EXISTS aliases(alias TEXT PRIMARY KEY,k TEXT);
          CREATE TABLE IF NOT EXISTS keysets(s TEXT,k TEXT,j TEXT,PRIMARY KEY(s,k));
          CREATE TABLE IF NOT EXISTS done(stage TEXT PRIMARY KEY,binding TEXT);
          CREATE TABLE IF NOT EXISTS source_witness(s TEXT,k TEXT,t TEXT,j TEXT,PRIMARY KEY(s,k,t));
          CREATE TABLE IF NOT EXISTS smoke_skips(s TEXT,a TEXT,t TEXT,k TEXT,target TEXT,partner TEXT,PRIMARY KEY(s,a,t,k,target,partner));
          CREATE INDEX IF NOT EXISTS records_page ON records(t,page,k);
          CREATE INDEX IF NOT EXISTS records_labels_producer ON records(json_extract(j,'$.producer'),json_extract(j,'$.producer_version'),k) WHERE t='label_versions';
          CREATE INDEX IF NOT EXISTS records_row ON records(t,json_extract(j,'$.row_key'));
          CREATE TABLE IF NOT EXISTS label_projection_exclusions(file TEXT,k TEXT,variant TEXT,non_null INTEGER,PRIMARY KEY(file,k,variant));
          CREATE INDEX IF NOT EXISTS records_member_match ON records(t,json_extract(j,'$.synthetic_match_group')) WHERE t='training_membership';
          CREATE INDEX IF NOT EXISTS records_synthetic_match ON records(t,json_extract(j,'$.synthetic_match_group')) WHERE t='synthetic';
          CREATE INDEX IF NOT EXISTS records_synthetic_match_ordered ON records(t,json_extract(j,'$.synthetic_match_group'),k) WHERE t='synthetic';
          CREATE INDEX IF NOT EXISTS records_synthetic_collision ON records(t,json_extract(j,'$.legacy_key_group')) WHERE t='synthetic';
          CREATE TABLE IF NOT EXISTS book_observations(s TEXT, locator TEXT, population TEXT,
            original_id TEXT, row_key TEXT, j TEXT, match_json TEXT, PRIMARY KEY(s,locator));
          CREATE INDEX IF NOT EXISTS book_observations_row ON book_observations(row_key);
        ''')

    def put(self, table, value, keys=None, merge=False, replace=False):
        if self.validate:
            self.validate(table, value)
        keys = keys or DEFAULT_KEYS[table]
        values = [value.get(k) for k in keys]
        if any(v is None for v in values):
            raise failure(f'missing {table} key {keys}: {str(values)[:160]}')
        key = canonical(values)
        encoded = canonical(value)
        old = self.db.execute('SELECT j FROM records WHERE t=? AND k=?', (table, key)).fetchone()
        if old and old[0] != encoded and not replace:
            if not merge:
                raise failure(f'duplicate/conflicting {table} key: {key[:160]}')
            prior = json.loads(old[0])
            resolution = None
            for k in ('row_key', 'parent_id', 'row_id', 'page_id', 'book_id', 'split', 'crop_sha256'):
                if prior.get(k) is not None and value.get(k) is not None and prior[k] != value[k]:
                    if k == 'book_id' and table == 'rows' and self.resolve_book_conflict:
                        resolution = self.resolve_book_conflict(prior, value)
                        if resolution:
                            continue
                    raise failure(f'conflicting {table}.{k}: {key[:160]}')
            prior.update({k: v for k, v in value.items() if v is not None})
            if resolution:
                prior.update(resolution)
            value = prior
            encoded = canonical(value)
        if self.validate:
            self.validate(table, value)
        from .progress import active
        progress = active.get()
        if progress is not None:
            progress.rows += 1
            progress.bytes += len(encoded.encode())
        self.db.execute('INSERT OR REPLACE INTO records VALUES(?,?,?,?)',
                        (table, key, encoded, str(value.get('page_id') or '')))
        return value

    def by_key(self, table, key):
        v = self.db.execute('SELECT j FROM records WHERE t=? AND k=?', (table, canonical(key))).fetchone()
        return json.loads(v[0]) if v else None

    def rows(self, table, by_page=True):
        for key, record in self.db.execute('SELECT k,j FROM records WHERE t=? ORDER BY ' + ('page,k' if by_page else 'k'), (table,)):
            yield key, json.loads(record)

    def alias(self, alias, key):
        prior = self.db.execute('SELECT k FROM aliases WHERE alias=?', (alias,)).fetchone()
        if prior and prior[0] != key:
            raise failure('ambiguous trainer identity: ' + alias[:160])
        self.db.execute('INSERT OR IGNORE INTO aliases VALUES(?,?)', (alias, key))

    def resolve(self, row):
        if row.get('row_key'):
            return row['row_key']
        if row.get('parent_id') is not None and row.get('row_id') is not None:
            return row_key(row['parent_id'], row['row_id'])
        alias = row.get('trainer_line_id', row.get('line_id'))
        v = self.db.execute('SELECT k FROM aliases WHERE alias=?', (alias,)).fetchone()
        if not v:
            raise failure('unresolved original row identity: ' + str(alias)[:160])
        return v[0]

    def key(self, name, key, detail):
        before = self.db.execute('SELECT j FROM keysets WHERE s=? AND k=?', (name, key)).fetchone()
        if before:
            raise failure('duplicate selected key in ' + name + ': ' + key)
        self.db.execute('INSERT INTO keysets VALUES(?,?,?)', (name, key, canonical(detail)))

    def witness(self, source, table, key, detail):
        self.db.execute('INSERT INTO source_witness VALUES(?,?,?,?)', (source, key, table, canonical(detail)))


class Builder:
    def __init__(self, lock, out, work, smoke=None, cap=CAP, target=TARGET, resume=False):
        self.lock, self.out, self.work, self.smoke = lock, Path(out).resolve(), Path(work).resolve(), smoke
        self.cap, self.target = cap, target
        paths = [Path(f['path']).resolve() for s in lock['inputs'] for f in s['files']]
        paths += [Path(f['path']).resolve() for s in lock['inputs']
                  for f in s.get('original_crops_source', {}).get('files', [])]
        paths += [Path(r['path']).resolve() for r in lock.get('crop_roots', [])]
        if lock.get('crop_index_cache'):
            paths.append(Path(lock['crop_index_cache']['path']).resolve())
        paths += [Path(f['path']).resolve() for a in lock.get('label_variant_adapters', []) for f in a['files']]
        paths += [Path(f['path']).resolve() for f in lock['assets']]
        paths += [Path(lock['features'][k]['path']).resolve() for k in ('codec', 'scripts')]
        for root in (self.out, self.work):
            if any(root == p or root in p.parents or p in root.parents for p in paths):
                raise ValueError('output/work overlaps input')
        if self.out == self.work or self.out in self.work.parents or self.work in self.out.parents:
            raise ValueError('public output and private work must be disjoint')
        code = {p.name: sha(p) for p in Path(__file__).parent.glob('*.py')}
        self.binding = digest(canonical({'lock': lock, 'code': code, 'smoke': smoke, 'cap': cap, 'target': target}))
        if resume:
            if json.loads((self.work / 'BINDING.json').read_text())['binding'] != self.binding:
                raise ValueError('resume binding changed; use a new out/work')
        else:
            if self.out.exists() or self.work.exists():
                raise ValueError('fresh out and work required (or use --resume)')
            self.out.mkdir(parents=True)
            self.work.mkdir(parents=True)
            atomic_json(self.work / 'BINDING.json', {'binding': self.binding, 'code': code})
        self.policy = WriteBindings(lock, smoke)
        self.store = Store(self.work / 'joins.sqlite', self.validate_write,
                           lambda prior, value: book_id_policy.resolve(prior, value, self.lock))
        self.assets = Assets(lock)
        try:
            with Progress('index') as index_progress:
                self.file_checks, self.crop_root_report = build_file_index(self.store.db, lock.get('crop_roots', []),
                                                                          cache=lock.get('crop_index_cache'))
            self.crops = CropIndex(self.store.db, self.file_checks)
            self.original_inputs = OriginalPayloads(self.store.db, self.file_checks, self.policy)
            self.current_original = None
            for k in ('codec', 'scripts'):
                verify_file(lock['features'][k])
            self.features = Features(lock['features']['codec']['path'], lock['features']['scripts']['path'],
                                     lock['features']['unicode_version'])
        except BaseException:
            self.store.db.close()
            raise
        self.timings = []
        self.build_info = {}
        self.smoke_books = defaultdict(set)
        self.deadline = active_deadline.get() or Deadline()
        self.store.db.execute("CREATE TABLE IF NOT EXISTS resume_units(stage TEXT PRIMARY KEY, ordinal INTEGER, state TEXT)")

    def units(self, stage, iterator, state=None):
        """Commit cursor and mutations together; replay only uncommitted units."""
        if self.store.db.execute('SELECT 1 FROM done WHERE stage=?', (stage,)).fetchone():
            return
        saved = self.store.db.execute('SELECT ordinal,state FROM resume_units WHERE stage=?', (stage,)).fetchone()
        start = saved[0] if saved else 0
        if state is not None and saved:
            def restore(template, value):
                if isinstance(template, Counter):
                    return Counter(value)
                if isinstance(template, dict):
                    return {k: restore(template.get(k), v) for k, v in value.items()}
                return value
            restored = restore(state, json.loads(saved[1]))
            state.clear()
            state.update(restored)
        batch = self.lock.get('_test_unit_rows', 1000)
        count = start
        for n, value in enumerate(iterator):
            if n < start:
                continue
            self.deadline.check()
            yield value
            count = n + 1
            if count % batch == 0:
                with atomic_boundary():
                    self.store.db.execute('INSERT OR REPLACE INTO resume_units VALUES(?,?,?)',
                                          (stage, count, canonical(state or {})))
                    self.store.db.commit()
                self.transaction_boundary(stage, count)
        with atomic_boundary():
            self.store.db.execute('INSERT OR REPLACE INTO resume_units VALUES(?,?,?)',
                                  (stage, count, canonical(state or {})))
            self.store.db.execute('INSERT OR REPLACE INTO done VALUES(?,?)', (stage, self.binding))
            self.store.db.commit()
        self.transaction_boundary(stage, count)
        self.deadline.check()

    def checkpoint(self, stage, action):
        if not self.store.db.execute('SELECT 1 FROM done WHERE stage=?', (stage,)).fetchone():
            self.deadline.check()
            with self.store.db:
                action()
                self.store.db.execute('INSERT OR REPLACE INTO done VALUES(?,?)', (stage, self.binding))
            self.transaction_boundary(stage, 1)
            self.deadline.check()

    def validate_write(self, table, row, final=False, count=False):
        source, adapter = origin(self.lock, row, table)
        key = [row.get(k) for k in DEFAULT_KEYS.get(table, ('key',))]
        with diagnostic(source, adapter, key):
            return self.policy.validate(table, row, final=final, count=count)

    def native_fields(self, row, source, table, original=None):
        native_page_fields(row, source, original)
        # Adapter input is native evidence. The store/export interface below
        # accepts release FKs only and rejects a missed conversion immediately.
        for field, binding in self.policy.columns(table).items():
            if field in ('page_id', 'box_id', 'page_frame_id', 'segmenter_run_id',
                         'book_id', 'canonical_book_id') and self.policy.status(binding) == 'historical_unknown':
                if row.get(field) is not None:
                    if field != 'page_id':
                        row['source_' + field] = row[field]
                row[field] = None
        return row

    def observe_bindings(self, original, row, source, locator):
        self.current_original = None
        if crop_eligible(source):
            result = self.original_inputs.verify(original, {**source, '_locator': locator}, keep_bytes=True)
            binary = result.pop('bytes', None)
            if binary is not None:
                self.store_original_payload(result, binary)
            self.crops.observe(original, source, locator, result)
            self.current_original = (locator, result)
        native = native_page_fields(dict(row), source, original)
        self.store.put('native_page_observations', {
            'key': source['name'] + ':' + locator, 'source': source['name'],
            'population': source.get('book_population', source['name']),
            'source_locator': locator, **{f: native.get(f) for f in
                ('source_page_id', 'source_page_namespace', 'source_page_references_json', 'page')}}, keys=['key'])
        for binding, entry in self.policy.entries.items():
            if binding not in SOURCE_BINDINGS:
                continue
            if (entry.get('value') or {}).get('input') != source['name']:
                continue
            values = dict(source_values(entry, original, row))
            for field, value in values.items():
                self.policy.value(binding, 'source.' + source['name'] + '.' + field, value, count=False)
            self.store.put('binding_observations', {'key': binding + ':' + locator,
                'binding': binding, 'values': values}, keys=['key'])

    def store_original_payload(self, result, binary):
        if result['hash_match']:
            actual = digest(binary)
            if actual != result['recorded_sha256']:
                raise ValueError(hash_mismatch(result['recorded_sha256'], actual, custody_kind(result),
                    result.get('resolved_path') or canonical(result.get('payload_input'))))
            self.store.db.execute('INSERT OR IGNORE INTO payloads VALUES(?,?,?,?)',
                (result['recorded_sha256'], binary, result['width'], result['height']))

    def unloaded(self, source, adapter, table, key, target=None, partner=None):
        if not self.smoke:
            raise ValueError(f'target missing [source={source} adapter={adapter} key={str(key)[:160]}]')
        self.store.db.execute('INSERT OR IGNORE INTO smoke_skips VALUES(?,?,?,?,?,?)',
                              (source, adapter, table, canonical(key), target or table,
                               canonical(key if partner is None else partner)))

    def smoke_unloaded_targets(self):
        counts = defaultdict(dict)
        for source, adapter, count in self.store.db.execute(
                'SELECT s,a,COUNT(*) FROM smoke_skips GROUP BY s,a ORDER BY s,a'):
            counts[source][adapter] = count
        return dict(counts)

    def row_target(self, row, source):
        # An absent alias is a sample miss; an absent identity is malformed.
        identity = row.get('trainer_line_id', row.get('line_id'))
        try:
            key = self.store.resolve(row)
        except ValueError:
            if not self.smoke or identity is None:
                raise
            self.unloaded(source['name'], source['adapter'], 'rows', identity)
            return None
        if self.store.by_key('rows', [key]) is None:
            self.unloaded(source['name'], source['adapter'], 'rows', key)
            return None
        return key

    def partner_lookup(self, table, key):
        if table == 'synthetic_group_count':
            count = self.store.db.execute("SELECT COUNT(*) FROM records WHERE t='synthetic' AND json_extract(j,'$.synthetic_match_group')=?",
                                          (key[0],)).fetchone()[0]
            return count if count >= key[1] else None
        if table == 'synthetic_group':
            return self.store.db.execute("SELECT 1 FROM records WHERE t='synthetic' AND json_extract(j,'$.synthetic_match_group')=?",
                                         key).fetchone()
        if table == 'real':
            row = self.store.by_key('rows', key)
            return row if row and row.get('release') else None
        return self.store.by_key(table, key)

    def check_relations(self, entities=True):
        # Relations may precede partners. Check after all ingestion, repeating
        # when omitted relations themselves have dependants.
        changed = True
        while changed:
            changed = False
            for table in TABLES + ('decisions',):
                # Full entity/provenance acceptance remains the independent
                # gate (including its explicitly recorded historical gaps).
                if table in ENTITIES and (not entities or not self.smoke):
                    continue
                for key, row in self.store.rows(table, by_page=False):
                    source, adapter = origin(self.lock, row, table)
                    with diagnostic(source, adapter, key):
                        valid = check_partners(table, row, self.partner_lookup, self.smoke,
                            lambda target, partner: self.unloaded(source, adapter, table, key, target, partner),
                            recorded_only=table in ENTITIES, binding_policy=self.policy)
                    if not valid and table not in ENTITIES:
                        self.store.db.execute('DELETE FROM records WHERE t=? AND k=?', (table, key))
                        changed = True

    def image(self, row, source, field='image', locator=None):
        if source['adapter'] == 'prepared' and field != 'trainer_image':
            raise ValueError('prepared payload must be read as trainer_image')
        selector = source.get('fields', {}).get(field, field)
        value = get(row, selector)
        if field == 'trainer_image' and value is None:
            selector = source.get('fields', {}).get('image', 'image')
            value = get(row, selector)
        if value is None:
            selector = 'image_png' if row.get('image_png') is not None else 'image_bytes'
            value = row.get('image_png', row.get('image_bytes'))
        byte_source = f'{locator or source.get("_path")} field={selector}'
        custody = 'trainer_image' if field == 'trainer_image' else 'embedded_original'
        if isinstance(value, dict):
            if value.get('bytes') is not None:
                value = value['bytes']
            elif value.get('path'):
                byte_source = self.relocate(value['path'], source)
                custody = 'trainer_image' if field == 'trainer_image' else 'recorded_path'
                value = self.assets.payload(byte_source)
            else:
                value = None
        if value is None and field == 'image':
            path = next((get(row, source.get('fields', {}).get(k, k)) for k in
                         ('crop_path', 'file_name', 'image_path') if get(row, source.get('fields', {}).get(k, k))), None)
            if path:
                relocated = self.relocate(path, source)
                byte_source, custody = relocated, 'recorded_path'
                if str(Path(relocated).resolve()) not in self.assets.files and source.get('missing_image_reason'):
                    return None
                value = self.assets.payload(relocated, row.get('image_member'))
        if value is None:
            return None
        if not isinstance(value, bytes):
            raise ValueError('image must be original binary or a locked asset locator')
        width, height = dimensions(value)
        h = digest(value)
        hash_field = 'crop_sha256' if field == 'image' else 'training_image_sha256'
        expected = get(row, source.get('fields', {}).get(hash_field, hash_field))
        if expected and expected != h:
            raise ValueError(hash_mismatch(expected, h, custody, byte_source,
                'trainer image hash mismatch' if field == 'trainer_image' else 'original image hash mismatch'))
        self.store.db.execute('INSERT OR IGNORE INTO payloads VALUES(?,?,?,?)', (h, value, width, height))
        return h, width, height

    def relocate(self, path, source):
        for old, new in source.get('path_rewrites', {}).items():
            if path == old or path.startswith(old.rstrip('/') + '/'):
                return new + path[len(old):]
        p = Path(path)
        return str(p if p.is_absolute() else Path(source.get('image_root', '.')) / p)

    def accept_smoke(self, row, source):
        if not self.smoke or source['adapter'] not in ('row', 's1', 'harvest', 'census'):
            return True
        book = row.get('book_id') or row.get('edition_id') or row.get('source_doc_id')
        if book is None:
            # Inputs without bibliography still get a strict bounded key sample.
            book = row.get('row_id') or row.get('id') or get(row, 'binding.id')
        seen = self.smoke_books[source['name']]
        if book not in seen and len(seen) >= self.smoke:
            return False
        seen.add(book)
        return True

    @source_record
    def real(self, original, source, locator):
        r = self.native_fields(mapped(original, source), source, 'rows', original)
        adapter = source['adapter']
        if adapter == 'census':
            r['release'] = r.get('release') or 'census06_g2'
            r['census_generation'] = source.get('census_generation', 'g2-e310b8ef84cc4763b036fd0abfc0295d')
            r.setdefault('parent_id', get(original, 'binding.parent_id'))
            r.setdefault('row_id', get(original, 'binding.id'))
            r.setdefault('split', get(original, 'binding.split'))
            r.setdefault('crop_sha256', get(original, 'binding.crop_sha256'))
            r.setdefault('text', r.get('final_text'))
            r.setdefault('decision', r.get('disposition'))
            r.setdefault('decision_reasons', r.get('reasons'))
            r['census_disposition'] = r['decision']
            r['census_reasons'] = r['decision_reasons']
            r['correction_route_statuses_json'] = r.get('routes')
            r['corrections_applied_json'] = r.get('edits')
        if adapter == 's1':
            r.setdefault('text', r.get('label'))
            r['release'] = r.get('release') or 'v4'
        if source.get('book_population') == 'v4':
            r['release'] = r.get('release') or 'v4'
        if adapter == 'harvest':
            r.setdefault('row_id', r.get('id'))
            if 'parent_id' not in r:
                r['parent_id'] = 'harvest:' + r['wave']
                r['identity_origin'] = 'release wave namespace; original census parent not supplied'
            r['release'] = r.get('release') or 'harvest-20261025'
            r['trainer_line_id'] = 'harvest:' + r['wave'] + ':' + str(r['row_id'])
        key = row_key(r.get('parent_id'), r.get('row_id'))
        if r.get('row_key') and r['row_key'] != key:
            raise ValueError('source row_key differs from canonical parent/row hash')
        r.update(row_key=key, source_locator=locator, source_sha256=source['_sha256'])
        self.observe_book(original, source, locator, key)
        previous = self.store.by_key('rows', [key]) or {}
        r['source_page_references_json'] = list({canonical(ref): ref for ref in
            previous.get('source_page_references_json', []) + r['source_page_references_json']}.values())
        if previous.get('release') and not r.get('release'):
            r['release'] = previous['release']
        r['original_id'] = r.get('id')
        original_id = (str(r['wave']) + ':' if r.get('wave') else '') + str(r['row_id'])
        r['id'] = f"{r.get('release', source['name'])}:{original_id}"
        r.setdefault('raw_text', r.get('label_raw'))
        r.setdefault('text', r.get('label_corrected', r.get('label', r.get('final_text'))))
        r.setdefault('decision', r.get('disposition', r.get('census_disposition', previous.get('decision', 'not_harvested'))))
        r.setdefault('decision_reasons', r.get('reasons', r.get('reason_codes', previous.get('decision_reasons', ['not_in_census']))))
        r['source_record_json'] = sanitize(r.get('source_record', r.get('provenance')) or previous.get('source_record_json', {}))
        r['source_record_locator'] = {'index': 'manifests/CONFIGS.json', 'config': 'rows',
                                     'key': {'row_key': key}, 'field': 'source_record_json'}
        source_record = r['source_record_json']
        if isinstance(source_record, str):
            source_record = json.loads(source_record)
        for field in SOURCE_FIELDS:
            r.setdefault(field, source_record.get(field) if isinstance(source_record, dict) else None)
        if r.get('source_record_sha256') is None and source_record:
            r['source_record_sha256'] = digest(canonical(source_record))
            r['source_record_hash_basis'] = 'sanitized public record, canonical JSON'
        r['source_missing_reasons_json'] = {field: {'reason': 'not recorded in selected pinned source',
                                                   'searched': locator} for field in SOURCE_FIELDS if r.get(field) is None}
        custody = (self.current_original[1] if self.current_original and self.current_original[0] == locator
                   else self.original_inputs.verify(original, source))
        if not custody['hash_match'] and previous.get('original_crop_custody', {}).get('hash_match'):
            custody = previous['original_crop_custody']
        r['original_crop_custody'] = custody
        r['original_custody'] = custody_kind(custody)
        image = ((custody['recorded_sha256'], custody['width'], custody['height'])
                 if custody['hash_match'] else None)
        if image:
            r['crop_sha256'], r['width'], r['height'] = image
            r['crop_missing_reason'] = None
        else:
            r['width'] = r['height'] = None
            r['crop_missing_reason'] = custody['reason']
        r['crop_availability_status'] = 'verified_by_hash' if image else custody['reason']
        r['crops_json'] = r.get('crops_json', r.get('crops', [])) or []
        if isinstance(r['crops_json'], str):
            r['crops_json'] = json.loads(r['crops_json'])
        if image:
            r['crops_json'].append({'crop_id': r.get('crop_id'), 'variant': 'source', 'sha256': image[0],
                'width': image[1], 'height': image[2], 'source_locator': locator,
                'payload_locator': {'index': 'manifests/CONFIGS.json', 'config': 'crops',
                                    'key': {'crop_sha256': image[0]}, 'field': 'image'}})
        elif r.get('crop_sha256'):
            r['crops_json'].append({'crop_id': r.get('crop_id'), 'variant': 'source', 'sha256': r['crop_sha256'],
                                   'availability_status': 'missing', 'missing_reason': r['crop_missing_reason']})
        # Retain distinct producer/variant records when another source contributes metadata.
        r['crops_json'] = (previous.get('crops_json') or []) + r['crops_json']
        for label_variant, text in ((source.get('label_variant', 'raw' if adapter == 'row' else adapter), r.get('text')),
                                    ('raw', r.get('raw_text'))):
            if text is not None:
                self.label(key, label_variant, text, source, locator,
                           {'raw_text_field': source.get('fields', {}).get('raw_text'),
                            'correction_bindings': r.get('corrections_applied_json'),
                            'route_statuses': r.get('correction_route_statuses_json')})
        if adapter == 'harvest' and r.get('raw_text') is None:
            self.label(key, 'raw', None, source, locator,
                {'reason': 'raw recovery adapter value unavailable; see P1 coverage', 'route_status': 'unknown',
                 'raw_text_field': source.get('fields', {}).get('raw_text'),
                 'correction_bindings': r.get('corrections_applied_json'),
                 'route_statuses': r.get('correction_route_statuses_json')})
        if r.get('text') is not None:
            r.update(label_sha256=digest(r['text']), label_version=source.get('label_variant', adapter))
        if r.get('raw_text') is not None:
            r['raw_text_sha256'] = digest(r['raw_text'])
        if not source.get('select_label', True) and previous:
            for field in ('text', 'label_sha256', 'label_version'):
                r[field] = previous.get(field)
        r.setdefault('trained_in', [])
        r = self.store.put('rows', sanitize(r), merge=True)
        if adapter in ('s1', 'harvest') or source.get('trainer_alias'):
            self.store.alias(r.get('trainer_line_id') or str(r['row_id']), key)
        if source.get('keyset') and all(get(r, k) == v for k, v in source.get('keyset_where', {}).items()):
            keyset_key = get(r, source['keyset_key']) if source.get('keyset_key') else r['trainer_line_id'] if adapter == 'harvest' else r['row_id']
            self.store.key(source['keyset'], str(keyset_key),
                           {'row_key': key, 'crop_sha256': r.get('crop_sha256'), 'label_sha256': r.get('label_sha256')})
        self.store.witness(source['name'], 'rows', key, {k: r.get(k) for k in
                           ('row_key', 'parent_id', 'row_id', 'decision', 'decision_reasons', 'crop_sha256')})
        if adapter == 'census' or source.get('record_decision'):
            self.store.put('decisions', {'key': source['name'] + ':' + key, 'row_key': key,
                                        'record': sanitize(original), 'source_locator': locator,
                                        'source_sha256': source['_sha256']}, keys=['key'])

    def label(self, key, variant, text, source, locator, extra=None):
        version = source.get('producer_version', source['name'])
        label = {'row_key': key, 'label_variant': variant, 'producer_version': version,
                 'text': text, 'text_sha256': digest(text) if text is not None else None, 'source_locator': locator,
                 'source_sha256': source['_sha256'], **(extra or {})}
        label['label_version_id'] = digest(canonical([key, variant, version]))
        label.setdefault('producer', source.get('producer', source['name']))
        label.setdefault('before_sha256', None)
        label.setdefault('route_status', 'observed')
        label.setdefault('normalization', 'source text unchanged')
        label.setdefault('reason', None if text is not None else 'text absent from selected source')
        if text is not None:
            label.setdefault('gt_nfc', ud.normalize('NFC', text))
            label.setdefault('gt_nfd', ud.normalize('NFD', text))
        self.store.put('label_versions', label)

    @source_record
    def prepared(self, original, source, locator, ordinal):
        r = mapped(original, source)
        pool = source['pool']
        role = source['role']
        synthetic = source.get('synthetic', False)
        image = self.image(original, source, field='trainer_image', locator=locator)
        if image is None:
            raise ValueError('prepared payload is missing')
        h, trainer_width, trainer_height = image
        lid = r['line_id']
        if synthetic:
            build = source['factory_build_id']
            r.setdefault('reuse_index', 0)
            match_group = synthetic_match_group(r, h, build)
            candidates = [json.loads(j) for j, in self.store.db.execute(
                "SELECT j FROM records INDEXED BY records_synthetic_match_ordered WHERE t='synthetic' AND json_extract(j,'$.synthetic_match_group')=? ORDER BY k",
                (match_group,))]
            if not candidates:
                if self.smoke:
                    self.unloaded(source['name'], source['adapter'], 'synthetic_group', locator)
                    return
                raise ValueError('prepared synthetic has no exact A12 payload/attribute match: ' + locator)
            if self.smoke:
                consumed = self.store.db.execute("""SELECT COUNT(*) FROM records WHERE t='training_membership'
                    AND json_extract(j,'$.synthetic_match_group')=? AND json_extract(j,'$.model_id')=?
                    AND json_extract(j,'$.role')=? AND json_extract(j,'$.pool')=? AND json_extract(j,'$.variant')=?""",
                    (match_group, self.lock['models'][0], role, pool, source.get('variant', 'prepared005'))).fetchone()[0]
                if consumed >= len(candidates):
                    # Native identical occurrences may be beyond the sampled
                    # extent. Full mode still verifies the exact multiset.
                    self.unloaded(source['name'], source['adapter'], 'synthetic_occurrence', locator)
                    return
            # Indistinguishable observations establish multiset membership only.
            # Never invent which native position a prepared row came from.
            target = candidates[0] if len(candidates) == 1 else None
            key = None
        else:
            key = self.row_target(r, source)
            if key is None:
                return
            target = self.store.by_key('rows', [key])
            if original.get('validation_original_join') == 'exact':
                filled = []
                for field in (*VALIDATION_ORIGINAL_FIELDS, 'crop_bbox'):
                    if target.get(field) is None and original.get(field) is not None:
                        target[field] = original[field]
                        filled.append(field)
                provenance = original['validation_original_provenance']
                target['validation_original_provenance'] = {**provenance,
                    'filled_fields': [f for f in provenance['filled_fields'] if f in filled]}
                refs = native_page_fields({}, source, original)['source_page_references_json']
                target.setdefault('source_page_references_json', []).extend(
                    ref for ref in refs if ref not in target['source_page_references_json'])
                self.native_fields(target, source, 'rows', original)
            self.observe_book(original, source, locator, key)
            descriptor = {'pool': pool, 'trainer_line_id': lid, 'variant': source.get('variant', 'prepared005'),
                          'image_sha256': h, 'width': trainer_width, 'height': trainer_height,
                          **{k: r.get(k) for k in ('gt_nfc', 'gt_nfd', 'label_ids', 'codec_version')}}
            target.setdefault('trainer_variants', []).append(descriptor)
            if role == 'train' or target.get('training_image_sha256') is None:
                target.update(training_image_sha256=h, trainer_image_sha256=h, pool=pool, trainer_line_id=lid,
                              gt_nfc=r.get('gt_nfc'), gt_nfd=r.get('gt_nfd'), label_ids=r.get('label_ids'),
                              codec_version=r.get('codec_version'), evaluation_role=selection_role(pool))
            target.setdefault('crops_json', []).append({'variant': source.get('variant', 'prepared005'),
                'sha256': h, 'width': trainer_width, 'height': trainer_height, 'source_locator': locator,
                'payload_locator': {'index': 'manifests/CONFIGS.json', 'config': 'training_membership',
                                    'key': {'row_key': key, 'pool': pool}, 'field': 'payload_locator'}})
            self.label(key, 'trained', r['gt_nfc'], source, locator,
                       {k: r.get(k) for k in ('gt_nfc', 'gt_nfd', 'label_ids', 'codec_version')})
            if source.get('keyset'):
                suffix = 'harvest' if lid.startswith('harvest:') else 'v4'
                self.store.key(source['keyset'] + '_' + suffix, lid,
                               {'row_key': key, 'image_sha256': h, 'label_sha256': digest(r['gt_nfc'])})
        train_models = self.lock['models'] if role == 'train' else []
        if target is not None:
            target['trained_in'] = sorted(set(target.get('trained_in', [])) | set(train_models))
            self.store.put('synthetic' if synthetic else 'rows', target, merge=True)
        for model in self.lock['models']:
            membership = {'model_id': model, 'role': role, 'pool': pool, 'trainer_line_id': lid,
                          'variant': source.get('variant', 'prepared005'), 'row_key': key,
                          'factory_build_id': source.get('factory_build_id') if synthetic else None,
                          'reuse_index': r.get('reuse_index', 0), 'image_sha256': h,
                          'label_sha256': digest(r['gt_nfc']), 'available': True, 'eligible': role == 'train',
                          'drawn': None, 'selection': role == 'dev', 'evaluation': role in ('dev', 'test'),
                          'selection_role': selection_role(pool), 'draw_count': None,
                          'draw_status': 'prepared005 train population' if role == 'train' else 'selection/evaluation input',
                          'source_shard': source['_path'], 'source_sha256': source['_sha256'], 'source_ordinal': ordinal,
                          'image_variant': source.get('variant', 'prepared005'),
                          'label_variant': 'trained',
                          'payload_locator': {'pool': pool, 'source_shard_sha256': source['_sha256'], 'row_ordinal': ordinal, 'field': 'image_png'},
                          'pool_order': source['_pool_offset'] + ordinal,
                          'run_binding_sha256': self.lock.get('run_bindings', {}).get(model),
                          'sampler_json': self.lock.get('sampler'),
                          **{k: r.get(k) for k in ('gt_nfc', 'gt_nfd', 'label_ids', 'codec_version')}}
            if synthetic:
                membership.update(synthetic_key=target['synthetic_key'] if target else None,
                    synthetic_match_group=match_group, synthetic_candidate_count=len(candidates),
                    synthetic_mapping_status='unique_exact' if target else 'ambiguous_identical_observations')
                identity = ['prepared-position-v1', model, role, pool, membership['variant'],
                            build, source['_path'], ordinal]
            else:
                identity = [membership[k] for k in ('model_id', 'role', 'pool', 'trainer_line_id', 'variant')]
            membership['membership_id'] = digest(canonical(identity))
            if synthetic and self.store.by_key('training_membership', [membership['membership_id']]) is not None:
                raise ValueError('prepared synthetic position selected twice: ' + locator)
            self.store.put('training_membership', membership)
            self.store.witness(source['name'], 'training_membership', membership['membership_id'], membership)

    @source_record
    def synth(self, original, source, locator, ordinal):
        r = self.native_fields(mapped(original, source), source, 'synthetic', original)
        evidence = self.build_info[source['build_evidence']]
        build, build_sha = evidence['record'], evidence['sha256']
        r.update(factory_build_id=source['factory_build_id'], source_build=source['source_build'],
                 source_locator=locator, source_sha256=source['_sha256'])
        r.setdefault('reuse_index', 0)
        r.update(source_shard=source['_path'], source_ordinal=ordinal)
        r['synthetic_key'] = canonical([r[k] for k in DEFAULT_KEYS['synthetic']])
        r['legacy_key_group'] = digest(canonical([r['factory_build_id'], r['line_id'], r['reuse_index']]))
        r['text'] = r['gt_nfc']
        if ud.normalize('NFC', r['text']) != r['text']:
            raise ValueError('synthetic gt_nfc is not NFC; refusing to mutate source label')
        image = self.image(original, source)
        if image is None:
            raise ValueError('synthetic payload missing')
        r['synthetic_match_group'] = synthetic_match_group(r, image[0], r['factory_build_id'])
        r['synthetic_native_attributes_json'] = {k: r.get(k) for k in SYNTHETIC_MATCH_FIELDS}
        r['image_sha256'], r['width'], r['height'] = image
        r['n_ops'] = len(r['applied_ops'])
        if r['severity'] not in (0, 1, 2, 3):
            raise ValueError('invalid synthetic severity')
        fonts = {f['stem']: f for f in build.get('fonts', [])}
        font = fonts.get(r.get('font'), {})
        r.setdefault('font_sha16', font.get('sha16'))
        r.setdefault('font_file_sha256', font.get('sha256'))
        for k in ('recipe_sha256', 'recipe_effective_sha256', 'generator_code_sha256', 'generator_binary_sha256'):
            r.setdefault(k, build.get(k))
        r.setdefault('recipe_name', source.get('recipe_name', build.get('recipe_name')))
        r.setdefault('trained_in', [])
        unknown = {}
        required = ('text_source_locator text_sha256 font_file_sha256 generator_code_sha256 '
                    'generator_binary_sha256 recipe_name recipe_sha256 recipe_effective_sha256').split()
        for k in required:
            r.setdefault(k, None)
            if r[k] is None:
                unknown[k] = {'reason': 'not recorded in selected historical build evidence',
                              'search_receipt': {'path': evidence['path'], 'sha256': build_sha},
                              'probe_receipts': self.lock.get('probe_receipts', [])}
        # Build seed is retained in BUILD, never represented as a per-line seed.
        for k in ('per_line_seed', 'operation_parameters'):
            if r.get(k) is None:
                unknown[k] = {'reason': 'not retained per line by the historical factory',
                              'search_receipt': {'path': evidence['path'], 'sha256': build_sha}}
        r['historical_unknown_fields_json'] = unknown
        r['historical_unknown_fields'] = unknown
        r['provenance_completeness'] = 'partial' if unknown else 'complete'
        r['provenance_computed_json'] = ['image_sha256', 'width', 'height', 'n_ops', 'provenance_completeness']
        r['provenance_recovered_json'] = [k for k in sanitize(original) if k not in ('image_png', 'image')]
        if self.store.by_key('synthetic', [r[k] for k in DEFAULT_KEYS['synthetic']]) is not None:
            raise ValueError('synthetic native position selected twice: ' + locator)
        self.store.put('synthetic', sanitize(r))
        key = r['synthetic_key']
        self.observe_book(original, source, locator, 'synthetic:' + key)
        self.store.witness(source['name'], 'synthetic', key,
                           {k: r.get(k) for k in ('synthetic_key', 'factory_build_id', 'line_id', 'reuse_index', 'split',
                                                 'image_sha256', 'gt_nfc', 'gt_nfd', 'label_ids', 'codec_version')})

    def ingest(self):
        self.policy = WriteBindings(self.lock, self.smoke)
        validation_originals = ValidationOriginals(self.store.db)
        sources = sorted(self.lock['inputs'], key=lambda s: (s.get('priority', {'evidence': 0, 'census': 10,
                         'row': 20, 's1': 30, 'harvest': 30, 'synthetic': 40, 'prepared': 60}.get(s['adapter'], 50)), s['name']))
        for source in sources:
            with self.store.db:
                self.original_inputs.load(self.lock, source, self.smoke, self.store_original_payload, self.deadline.check)
            offset = 0
            for file_index, entry in enumerate(source['files']):
                if self.smoke and not self.lock.get('_measure') and source['adapter'] in ('synthetic', 'prepared') and file_index > 0:
                    continue
                if self.smoke and not self.lock.get('_measure') and source.get('table') == 'page_images' and file_index > 0:
                    continue
                with diagnostic(source['name'], source['adapter'], entry['path']):
                    with Progress('hash:' + source['name'], entry['bytes']) as hashing:
                        verify_file(entry)
                        hashing.bytes = entry['bytes']
                    source = {**source, '_sha256': entry['sha256'], '_path': entry['path'], '_pool_offset': offset}
                    stage = 'ingest:' + source['name'] + ':' + str(file_index)
                    if source['adapter'] == 'evidence':
                        if entry['bytes'] > 32_000_000:
                            raise ValueError('large evidence requires explicit table/keyset selector, not whole-object evidence')
                        record = sanitize(json.loads(Path(entry['path']).read_text()))
                        self.build_info[source['name']] = {'record': record, 'sha256': entry['sha256'], 'path': entry['path']}
                    if self.store.db.execute('SELECT 1 FROM done WHERE stage=?', (stage,)).fetchone():
                        if entry['path'].endswith('.parquet'):
                            import pyarrow.parquet as pq
                            offset += pq.ParquetFile(entry['path']).metadata.num_rows
                        continue
                    saved = self.store.db.execute('SELECT ordinal,byte_offset,books FROM ingest_cursor WHERE stage=?', (stage,)).fetchone()
                    count, position = (saved[0], saved[1]) if saved else (0, 0)
                    if saved:
                        self.smoke_books[source['name']] = set(json.loads(saved[2]))
                    batch_rows = self.lock.get('transaction_rows', 50000)
                    if batch_rows < 50000 and not self.lock.get('_test_transaction_rows'):
                        raise ValueError('transaction_rows must be at least 50000')
                    total_file_rows = self.file_rows(entry)
                    with Progress(stage, entry['bytes']) as progress:
                        progress.rows, progress.bytes = count, position
                        try:
                            for ordinal, original, position in positioned_records(entry['path'], source, count, position):
                                if self.smoke and not source.get('book_bridge_metadata') and not source.get('validation_original_metadata') and ordinal >= self.smoke * self.lock.get('smoke_rows_per_source', 512):
                                    break
                                self.deadline.check()
                                self.ingest_record(original, source, entry, ordinal, validation_originals)
                                count = ordinal + 1
                                progress.rows = count
                                progress.bytes = position or int(entry['bytes'] * count / max(count, total_file_rows))
                                if count % batch_rows == 0:
                                    self.store.db.execute('INSERT OR REPLACE INTO ingest_cursor VALUES(?,?,?,?)',
                                        (stage, count, position, canonical(sorted(self.smoke_books[source['name']], key=str))))
                                    self.store.db.commit()
                                    self.transaction_boundary(stage, count)
                            self.store.db.execute('INSERT INTO done VALUES(?,?)', (stage, self.binding))
                            self.store.db.execute('DELETE FROM ingest_cursor WHERE stage=?', (stage,))
                            self.store.db.commit()
                            self.transaction_boundary(stage, count)
                            self.deadline.check()
                        except BaseException:
                            self.store.db.rollback()
                            raise
                        offset += count

    def transaction_boundary(self, stage, ordinal):
        """Durable boundary and fault-injection hook for equivalence tests."""
        self.deadline.check()

    @staticmethod
    def file_rows(entry):
        if entry['path'].endswith('.parquet'):
            import pyarrow.parquet as pq
            return pq.ParquetFile(entry['path']).metadata.num_rows
        return 0

    def ingest_record(self, original, source, entry, ordinal, validation_originals):
        if source.get('validation_original_metadata'):
            validation_originals.observe(original, source['name'],
                canonical({'path': entry['path'], 'ordinal': ordinal}), entry['sha256'])
            return
        if source.get('book_population') == 'validation':
            original = validation_originals.enrich(original)
        r = mapped(original, source)
        if not source.get('book_bridge_metadata') and not self.accept_smoke(r, source):
            return
        locator = canonical({'path': entry['path'], 'ordinal': ordinal, 'sha256': entry['sha256']})
        identity = {k: r.get(k) for k in ('row_key', 'parent_id', 'row_id', 'line_id', 'book_id', 'page_id') if r.get(k) is not None}
        with diagnostic(source['name'], source['adapter'], identity or locator):
            adapter = source['adapter']
            self.observe_bindings(original, r, source, locator)
            if adapter in ('row', 's1', 'harvest', 'census'):
                self.real(original, source, locator)
            elif adapter == 'synthetic':
                self.synth(original, source, locator, ordinal)
            elif adapter == 'prepared':
                self.prepared(original, source, locator, ordinal)
            elif adapter == 'keyset':
                key = str(get(r, source['key_field']))
                if key == 'None':
                    raise ValueError('missing keyset key')
                self.store.key(source['keyset'], key, sanitize(r))
                self.observe_book(original, source, locator)
            elif adapter == 'decision':
                self.store.put('decisions', {'key': locator, 'record': sanitize(original),
                               'source_locator': locator, 'source_sha256': entry['sha256']}, keys=['key'])
            elif adapter == 'row_patch':
                r = self.native_fields(r, source, 'rows', original)
                key = self.row_target(r, source)
                if key is None:
                    return
                previous = self.store.by_key('rows', [key])
                r['source_page_references_json'] = list({canonical(ref): ref for ref in
                    previous.get('source_page_references_json', []) + r['source_page_references_json']}.values())
                previous.update({k: v for k, v in r.items() if v is not None})
                self.store.put('rows', previous, merge=True)
            elif adapter == 'table':
                table = source['table']
                if table == 'label_versions':
                    r.setdefault('producer', source['name'])
                r = self.native_fields(r, source, table, original)
                r.update(source_locator=locator, source_sha256=entry['sha256'])
                if table == 'row_instruments' and source.get('exact_original_ids'):
                    # Portable relation contains original IDs, not release row keys.
                    r['declaration_locator'] = source.get('declaration')
                    self.store.put('raw_row_instruments', sanitize(r),
                        ['row_id', 'kind', 'list_name', 'list_sha256'])
                    return
                keys = source.get('keys', DEFAULT_KEYS[table])
                if any(r.get(k) is None for k in keys if k != 'row_key'):
                    raise ValueError(f'missing {table} key {keys}')
                if (table in ('row_instruments', 'references', 'label_versions', 'row_features')
                    or table == 'training_membership' and not r.get('synthetic_match_group')) and not r.get('row_key'):
                    r['row_key'] = self.row_target(r, source)
                    if r['row_key'] is None:
                        return
                if table == 'page_images':
                    image = self.image(original, source)
                    if image is None:
                        raise ValueError('missing page raster')
                    r['image_sha256'], r['width'], r['height'] = image
                self.store.put(table, sanitize(r), source.get('keys'))
                keys = source.get('keys', DEFAULT_KEYS[table])
                self.store.witness(source['name'], table, canonical([r[k] for k in keys]),
                                   {k: r.get(k) for k in keys + ['split', 'status']})
            elif adapter != 'evidence':
                raise ValueError('unknown source adapter: ' + adapter)

    def import_label_variants(self):
        stage = 'label-adapters'
        if self.store.db.execute('SELECT 1 FROM done WHERE stage=?', (stage,)).fetchone():
            return
        with self.store.db:
            for source in self.lock.get('label_variant_adapters', []):
                for entry in source['files']:
                    verify_file(entry)
                    unit_stage = 'labels:' + source['name'] + ':' + entry['sha256']
                    for row in self.units(unit_stage, layered.adapter_rows([entry['path']])):
                        projected = layered.publication_label(row)
                        if projected is None:
                            self.store.db.execute('INSERT OR IGNORE INTO label_projection_exclusions VALUES(?,?,?,?)',
                                (entry['sha256'], row['row_key'], row['label_variant'], row['text'] is not None))
                            continue
                        row = projected
                        target = self.store.by_key('rows', [row['row_key']])
                        if not target:
                            if self.smoke:
                                self.unloaded(source['name'], 'label_variant_adapter', 'label_versions', [row['row_key']], 'rows', [row['row_key']])
                                continue
                            raise ValueError('label adapter unknown row_key: ' + row['row_key'])
                        if row['label_variant'] == 'raw' and row['text'] is not None:
                            if not target.get('raw_text_sha256') or target['raw_text_sha256'] != row['text_sha256']:
                                raise ValueError('raw adapter differs from recorded raw_text_sha256')
                            if not row.get('source_locator') or not row.get('source_sha256'):
                                raise ValueError('raw adapter needs identity-bound source_locator/source_sha256 from P1')
                            binding = row.get('row_source_locator')
                            if binding != target.get('source_locator'):
                                raise ValueError('raw adapter recorded row locator mismatch')
                        self.label(row['row_key'], row['label_variant'], row['text'],
                            {**source, '_sha256': entry['sha256']}, row.get('source_locator'), row)
            self.store.db.execute('INSERT INTO done VALUES(?,?)', (stage, self.binding))

    def finalize_synthetic_identity(self):
        # File-transaction ingestion makes these group counts restart-safe.
        self.store.db.execute("""UPDATE records SET j=json_set(j,
            '$.key_collision_size', (SELECT COUNT(*) FROM records AS other
                WHERE other.t='synthetic' AND json_extract(other.j,'$.legacy_key_group')=json_extract(records.j,'$.legacy_key_group')),
            '$.key_collision_group', CASE WHEN (SELECT COUNT(*) FROM records AS other
                WHERE other.t='synthetic' AND json_extract(other.j,'$.legacy_key_group')=json_extract(records.j,'$.legacy_key_group')) > 1
                THEN json_extract(j,'$.legacy_key_group') ELSE NULL END)
            WHERE t='synthetic'""")
        groups = self.store.db.execute("""SELECT json_extract(j,'$.synthetic_match_group'),
            json_extract(j,'$.model_id'), json_extract(j,'$.role'), json_extract(j,'$.pool'),
            json_extract(j,'$.variant'), COUNT(*), native.n FROM records JOIN
            (SELECT json_extract(j,'$.synthetic_match_group') AS g, COUNT(*) AS n FROM records
                WHERE t='synthetic' GROUP BY 1) AS native
            ON json_extract(j,'$.synthetic_match_group')=native.g WHERE t='training_membership'
            GROUP BY 1,2,3,4,5 HAVING COUNT(*)>native.n OR native.n>1""").fetchall()
        for group, model, role, pool, variant, consumed, available in groups:
            if consumed > available:
                member = json.loads(self.store.db.execute(
                    "SELECT j FROM records WHERE t='training_membership' AND json_extract(j,'$.synthetic_match_group')=? LIMIT 1",
                    (group,)).fetchone()[0])
                source, adapter = origin(self.lock, member, 'training_membership')
                raise ValueError(f'prepared synthetic multiplicity exceeds A12: {consumed} > {available} '
                                 f'[source={source} adapter={adapter} key={group[:160]}]')
            if role != 'train' or consumed != available:
                continue
            candidates = [json.loads(j) for j, in self.store.db.execute(
                "SELECT j FROM records WHERE t='synthetic' AND json_extract(j,'$.synthetic_match_group')=?", (group,))]
            for row in candidates:
                row['trained_in'] = sorted(set(row.get('trained_in', [])) | {model})
                self.store.put('synthetic', row, merge=True)
        if not self.smoke:
            selections = {(s['factory_build_id'], s['pool'], s.get('variant', 'prepared005'))
                          for s in self.lock['inputs'] if s.get('synthetic') and s.get('role') == 'train'}
            for build, pool, variant in sorted(selections):
                native = dict(self.store.db.execute("""SELECT json_extract(j,'$.synthetic_match_group'), COUNT(*)
                    FROM records WHERE t='synthetic' AND json_extract(j,'$.factory_build_id')=?
                    AND json_extract(j,'$.split')='train' GROUP BY 1""", (build,)))
                for model in self.lock['models']:
                    consumed = dict(self.store.db.execute("""SELECT json_extract(j,'$.synthetic_match_group'), COUNT(*)
                        FROM records WHERE t='training_membership' AND json_extract(j,'$.factory_build_id')=?
                        AND json_extract(j,'$.role')='train' AND json_extract(j,'$.pool')=?
                        AND json_extract(j,'$.variant')=? AND json_extract(j,'$.model_id')=? GROUP BY 1""",
                        (build, pool, variant, model)))
                    missing = sum(max(n - consumed.get(g, 0), 0) for g, n in native.items())
                    extra = sum(max(n - native.get(g, 0), 0) for g, n in consumed.items())
                    if missing or extra:
                        selected = next(s for s in self.lock['inputs'] if s.get('synthetic') and s.get('role') == 'train'
                            and (s['factory_build_id'], s['pool'], s.get('variant', 'prepared005')) == (build, pool, variant))
                        offending = next(g for g in sorted(native.keys() | consumed.keys()) if native.get(g, 0) != consumed.get(g, 0))
                        raise ValueError(f'prepared synthetic train multiset differs from A12: {model}/{pool}/{variant}: '
                                         f"{missing} native occurrences missing, {extra} extra prepared occurrences; no pairing inferred "
                                         f"[source={selected['name']} adapter=prepared key={offending[:160]}]")

    def derive(self):
        if self.store.db.execute("SELECT 1 FROM done WHERE stage='derive'").fetchone():
            return
        def phase(name, action):
            with Progress(name) as progress:
                action()
            self.timings.append({**progress.result, 'diagnostic_only': True})
        def rows_phase(stage, iterator):
            count = 0
            with Progress(stage) as progress:
                for value in self.units(stage, iterator):
                    yield value
                    count += 1
            self.timings.append({**progress.result, 'diagnostic_only': True,
                'input_rows': count, 'input_rows_per_second': count / progress.result['elapsed_seconds']})
        phase('derive:relations-before', lambda: self.checkpoint('derive:relations-before', lambda: self.check_relations(entities=False)))
        phase('derive:synthetic-identity', lambda: self.checkpoint('derive:synthetic-identity', self.finalize_synthetic_identity))
        with self.store.db:
            for union, members in self.lock.get('keyset_unions', {}).items():
                for member in members:
                    self.store.db.execute('INSERT OR IGNORE INTO keysets SELECT ?,k,j FROM keysets WHERE s=?', (union, member))
            phase('derive:keysets', self.bridge_keysets)
            phase('derive:joins', self.apply_joins)
            if self.lock.get('book_bridge'):
                phase('derive:book-bridge', self.apply_book_bridge)
            self.checkpoint('derive:relations-after', self.check_relations)
            self.crops.load_smoke_targets(self.lock, self.smoke)
            for source, loc, target in self.crops.smoke_witnesses():
                self.unloaded(source, 'original_crops', 'original_crops', [source, loc],
                              'original_crops', [target['source'], target['locator']])
            for _, row in rows_phase('derive:rows', self.store.rows('rows', by_page=False)):
                custody = self.crops.resolve(['tuple:' + row['row_key']],
                    row.get('original_crop_custody') or {'recorded_sha256': row.get('crop_sha256'),
                        'hash_match': False, 'reason': 'no_recorded_path'})
                row['original_crop_custody'] = custody
                row['original_custody'] = custody_kind(custody)
                row['crop_availability_status'] = 'verified_by_hash' if custody['hash_match'] else custody['reason']
                row['crop_missing_reason'] = custody['reason']
                row['width'] = custody.get('width') if custody['hash_match'] else None
                row['height'] = custody.get('height') if custody['hash_match'] else None
                if custody['hash_match']:
                    row['crop_sha256'] = custody['recorded_sha256']
                if not self.smoke and row.get('trained_in') and (not row.get('training_image_sha256') or
                        not self.payload(row['training_image_sha256'])):
                    raise failure('trained real row lacks trainer_image/training_image_sha256: ' + row['row_key'])
                box = self.store.by_key('boxes', [row.get('box_id')]) if row.get('box_id') else None
                if box:
                    for dest, src in {'polygon_px': 'polygon_px', 'polygon_norm': 'polygon_norm',
                        'coordinate_frame': 'coordinate_frame', 'frame_status': 'frame_status',
                        'segmenter': 'segmenter', 'segmenter_run_id': 'segmenter_run_id',
                        'box_kind': 'geometry_kind', 'emitted_index': 'emitted_item_index',
                        'reading_order': 'reading_order', 'top_index': 'line_index_from_top',
                        'provider_languages': 'detected_languages', 'language_scope': 'language_scope',
                        'ocr_confidence': 'confidence', 'ocr_confidence_scope': 'confidence_scope'}.items():
                        row.setdefault(dest, box.get(src))
                registry = self.store.by_key('book_registry', [row.get('book_id')]) if row.get('book_id') else None
                if registry:
                    for k in ('assignment_status', 'harvest_protection'):
                        row.setdefault(k, registry.get(k))
                    row.setdefault('canonical_book_id', registry.get('canonical_book_id', registry['book_id']))
                    row.setdefault('book_registry_sha256', registry.get('source_sha256'))
                self.resolve_split(row, registry)
                for instrument_json, in self.store.db.execute("SELECT j FROM records WHERE t='row_instruments' AND json_extract(j,'$.row_key')=?", (row['row_key'],)):
                    instrument = json.loads(instrument_json)
                    if instrument.get('row_key') == row['row_key'] and instrument['kind'] in ('lqb_row', 'release_excluded_row'):
                        row[instrument['kind']] = True
                if row.get('text') is not None:
                    feature = self.features.compute(row['text'], row, row.get('label_version', 'selected'))
                    row.update({k: v for k, v in feature.items() if k not in ('row_key', 'label_variant')})
                if not self.lock.get('book_bridge'):
                    row['source_missing_reasons_json'] = {field: {'reason': 'not recorded in selected pinned sources',
                                                                  'searched': row.get('source_locator')}
                                                         for field in SOURCE_FIELDS if row.get(field) is None}
                for field in ('corrections_applied', 'correction_route_statuses', 'source_record', 'source_missing_reasons'):
                    row[field] = row.get(field + '_json')
                row.update(feature_version=FEATURE_VERSION, pixel_variant='original_image')
                # This complete derived row includes explicit null source_split
                # and may replace an unresolved native split with reasoned unknown.
                self.store.put('rows', row, replace=True)
            for _, row in rows_phase('derive:release-labels', self.store.rows('rows')):
                self.label(row['row_key'], 'release', row.get('text'),
                    {'name': 'release', 'producer_version': self.lock['dataset_version'],
                     '_sha256': row.get('source_sha256')}, row.get('source_locator'),
                    {**{k: row.get(k) for k in ('gt_nfc', 'gt_nfd', 'label_ids', 'codec_version') if row.get(k) is not None},
                     'raw_text_field': row.get('raw_text_field'),
                     'correction_bindings': row.get('corrections_applied_json'),
                     'route_statuses': row.get('correction_route_statuses_json'),
                     'normalization': row.get('normalization', 'source text unchanged')})
            for _, label in rows_phase('derive:features', self.store.rows('label_versions')):
                row = self.store.by_key('rows', [label['row_key']])
                if label['text'] is None:
                    continue
                feature = self.features.compute(label['text'], row, label['label_version_id'])
                feature['label_version_id'] = label['label_version_id']
                feature['label_variant_name'] = label['label_variant']
                self.store.put('row_features', feature)
            for _, reference in rows_phase('derive:references', self.store.rows('references')):
                membership = {k: reference.get(k) for k in ('row_key', 'image_variant', 'label_variant',
                    'payload_locator', 'image_sha256', 'source_locator', 'source_sha256', 'split',
                    'diagnostic_only', 'exposure_notes', 'label_sha256')}
                membership.update(membership_id=digest(canonical(['reference-image', reference['reference_id']])),
                    reference_id=reference['reference_id'], membership_kind='reference_image', model_id=None,
                    role='reference', draw_count=None, drawn=None,
                    missing_reasons={k: 'not recorded in the pinned reference membership'
                        for k in ('image_sha256', 'payload_locator', 'image_variant') if membership.get(k) is None})
                self.store.put('training_membership', membership)
            self.store.db.execute('INSERT INTO done VALUES(?,?)', ('derive', self.binding))

    def resolve_split(self, row, registry):
        """Materialize the assignment before export, retaining its evidence.

        Prepared factory split labels are not dataset assignments (in particular,
        reserved does not distinguish dev/test). Only their declared roles can
        resolve a row with no native or registry assignment.
        """
        source, adapter = origin(self.lock, row, 'rows')
        with diagnostic(source, adapter, [row['row_key']]):
            native = row.get('source_split', row.get('split'))
            row.setdefault('source_split', native)
            book_split = registry.get('split') if registry else None
            roles = [r[0] for r in self.store.db.execute("""SELECT DISTINCT json_extract(j,'$.role')
                FROM records WHERE t='training_membership' AND json_extract(j,'$.row_key')=?
                ORDER BY 1""", (row['row_key'],))]
            evidence = {'source_split': native, 'book_id': row.get('book_id'),
                        'registry_split': book_split, 'prepared_roles': roles,
                        'registry_sha256': row.get('book_registry_sha256')}
            def assigned(value):
                return isinstance(value, str) and bool(value) and value != 'unknown' and not value.startswith('unassigned')
            if assigned(book_split):
                split, reason = book_split, 'pinned book registry assignment'
            elif registry:
                split, reason = 'unknown', 'pinned book registry has no resolved assignment'
                evidence['unassigned_reason'] = registry.get('unassigned_reason')
            elif assigned(native):
                split, reason = native, 'explicit native row assignment'
            else:
                assigned_roles = sorted(set(roles) & {'train', 'dev', 'test'})
                if len(assigned_roles) == 1:
                    split, reason = assigned_roles[0], 'exact prepared membership role'
                else:
                    split = 'unknown'
                    reason = ('conflicting prepared membership roles' if assigned_roles else
                              'no native, resolved registry or assigning prepared membership')
            # HF_REPO_SPEC canonical assignment rule (inherited by CROSSWALK):
            # source-row disagreements are diagnostics, not registry conflicts.
            conflict = assigned(native) and assigned(book_split) and native != book_split
            row.update(split=split, split_reason=reason, split_conflict=conflict,
                       split_resolution_json={**evidence, 'split': split, 'reason': reason,
                                              'source_registry_conflict': conflict})

    def observe_book(self, original, source, locator, key=None):
        population = source.get('book_population')
        if not self.lock.get('book_bridge') or not population:
            return
        row = metadata(original, population)
        ids = original_ids(row, population)
        if population == 'seal04' and original.get('parent_id') is not None and ids:
            key = row_key(original['parent_id'], ids[0])
        self.store.db.execute('INSERT INTO book_observations VALUES(?,?,?,?,?,?,NULL)',
            (source['name'], locator, population, ids[0] if ids else None, key, canonical(row)))

    def apply_book_bridge(self):
        def records_for(table):
            return [r for _, r in self.store.rows(table)]
        def input_hash(name):
            files = next(s['files'] for s in self.lock['inputs'] if s['name'] == name)
            if len(files) != 1:
                raise ValueError('book bridge requires one pinned file for ' + name)
            return files[0]['sha256']
        binding = self.lock['book_bridge']
        if input_hash(binding['registry_input']) != binding['registry_sha256'] or input_hash(binding['instruments_input']) != binding['row_instruments_sha256']:
            raise ValueError('book bridge lock registry/instrument SHA256 mismatch')
        engine = BookBridge(records_for('book_registry'), records_for('raw_row_instruments'),
            records_for('book_sources'), input_hash(binding['registry_input']),
            input_hash(binding['instruments_input']))
        coverage = {p: new_coverage() for p in binding['populations']}
        # Old factory rows have exact original IDs; the S4h unique S1 keyset
        # supplies their tuple. No crop hash or prefix supplies a row tuple.
        self.store.db.execute('''UPDATE book_observations SET row_key=(
            SELECT json_extract(j,'$.row_key') FROM keysets
            WHERE s='s1' AND k=book_observations.original_id)
            WHERE population='old' AND row_key IS NULL''')
        for source, locator, population, key, record in self.units('book:observations', self.store.db.execute(
                'SELECT s,locator,population,row_key,j FROM book_observations ORDER BY s,locator'), coverage):
            row = json.loads(record)
            match = engine.match(row, population)
            resolved = engine.resolve(row, population, match)
            members = engine.memberships(row, population)
            count_coverage(coverage[population], resolved, members, match)
            self.store.db.execute('UPDATE book_observations SET match_json=? WHERE s=? AND locator=?',
                                  (canonical(match), source, locator))
            if not key and population == 'old' and members:
                self.unloaded(source, 'book_bridge', 'row_instruments', locator)
            if key and not key.startswith('synthetic:'):
                if members and self.store.by_key('rows', [key]) is None:
                    self.unloaded(source, 'book_bridge', 'row_instruments', key)
                    continue
                for instrument in members:
                    self.store.put('row_instruments', {**instrument, 'row_key': key})
        saved = self.store.db.execute("SELECT state FROM resume_units WHERE stage='book:observations'").fetchone()
        if saved:
            coverage = json.loads(saved[0])
        for table in ('rows', 'synthetic'):
            for key, row in self.units('book:resolved:' + table, self.store.rows(table, by_page=False)):
                target = 'synthetic:' + key if table == 'synthetic' else row['row_key']
                originals = list(self.store.db.execute(
                    'SELECT s,locator,population,match_json FROM book_observations WHERE row_key=?', (target,)))
                observations = [json.loads(m) for _, _, _, m in originals]
                candidates = sorted({b for m in observations for b in m['candidates']})
                status = ('match' if len(candidates) == 1 else 'ambiguous' if candidates else
                          'unmatched' if any(m['typed_keys'] for m in observations) else 'no_key')
                match = {'book_id': candidates[0] if status == 'match' else None,
                         'status': status, 'candidates': candidates,
                         'matches': [hit for m in observations for hit in m['matches']],
                         'observations': [{'source': s, 'locator': loc, 'population': pop,
                                           'typed_matches': json.loads(m)['matches']}
                                          for s, loc, pop, m in originals]}
                population = 'synthetic' if table == 'synthetic' else 's1'
                resolved = engine.resolve(row, population, match)
                # Preserve native book keys visibly; nulls below must overwrite
                # native noncanonical book_id values, including on ambiguity.
                row['source_book_id'] = row.get('book_id')
                row['source_canonical_book_id'] = row.get('canonical_book_id')
                row['source_native_record_json'] = row.get('source_record_json')
                row.update(resolved)
                book = engine.books.get(row['book_id'], {})
                for field in ('assignment_status', 'harvest_protection'):
                    row[field] = book.get(field)
                self.store.put(table, row, replace=True)
        for population, values in coverage.items():
            self.store.put('book_bridge_coverage', {'population': population, **values}, keys=['population'])

    def bridge_keysets(self):
        """Map exact native key equality to an already recorded tuple row_key.

        The right keyset enforces uniqueness at insertion. No ID parsing,
        crop/hash comparison or embedded path lookup participates in this bridge.
        """
        for bridge in self.lock.get('keyset_bridges', []):
            counts = dict(matched=0, missing=0)
            for key, detail in self.units('bridge:' + bridge['name'], self.store.db.execute('''
                    SELECT l.k,r.j FROM keysets l LEFT JOIN keysets r ON r.s=? AND r.k=l.k
                    WHERE l.s=? ORDER BY l.k''', (bridge['right'], bridge['left'])), counts):
                value = json.loads(detail) if detail is not None else None
                if not value or not value.get('row_key'):
                    if self.smoke and value is None:
                        # Independently bounded source samples need not overlap.
                        # Retain the missing count, never invent the parent tuple.
                        counts['missing'] += 1
                        source = next((s['name'] for s in self.lock['inputs'] if s.get('keyset') == bridge['left']), bridge['left'])
                        self.unloaded(source, 'keyset_bridge', bridge['name'], key)
                        continue
                    raise ValueError(f"unmapped original tuple in keyset bridge [source={bridge['left']} adapter=keyset_bridge key={key[:160]}]")
                self.store.key(bridge['name'], value['row_key'],
                               {**value, 'native_key': key, 'bridge': bridge['name']})
                counts['matched'] += 1
            saved = self.store.db.execute('SELECT state FROM resume_units WHERE stage=?', ('bridge:' + bridge['name'],)).fetchone()
            if saved:
                counts = json.loads(saved[0])
            self.store.put('keyset_bridge_coverage', {'name': bridge['name'], 'matched': counts['matched'],
                           'left_only': counts['missing'], 'smoke': self.smoke}, keys=['name'])

    def apply_joins(self):
        """Explicit typed joins. Every non-nullable join requires one match."""
        for join in self.lock.get('joins', []):
            target, source = join['target'], join['source']
            paths = list(join['on'].values())
            if not all(re.fullmatch(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*', path) for path in paths):
                raise ValueError('invalid explicit join column path')
            expressions = ["json_extract(j,'$." + path + "')" for path in paths]
            self.store.db.execute('CREATE INDEX IF NOT EXISTS join_' + digest(canonical(paths))[:16] +
                                  ' ON records(t,' + ','.join(expressions) + ')')
            for _, row in self.units('join:' + digest(canonical(join)), self.store.rows(target, by_page=False)):
                values = [get(row, k) for k in join['on']]
                clauses = ' AND '.join(expression + '=?' for expression in expressions)
                params = [source] + values
                matches = list(self.store.db.execute('SELECT j FROM records WHERE t=? AND ' + clauses, params)) if all(v is not None for v in values) else []
                if len(matches) != 1:
                    available = self.store.db.execute('SELECT 1 FROM records WHERE t=? LIMIT 1', (source,)).fetchone()
                    declared = not available or all(self.store.db.execute(
                        "SELECT 1 FROM records WHERE t=? AND json_type(j,?) IS NOT NULL LIMIT 1",
                        (source, '$.' + path)).fetchone() for path in paths)
                    if not matches and self.smoke and declared and all(v is not None for v in values):
                        self.unloaded(origin(self.lock, row, target)[0], 'explicit_join', target, values)
                        continue
                    if not join.get('nullable_reason'):
                        raise ValueError(f"unresolved/ambiguous explicit join: {join['name']} [source={source} adapter=explicit_join key={str(values)[:160]}]")
                    row.setdefault('unresolved_joins', {})[join['name']] = {'reason': join['nullable_reason'], 'matches': len(matches)}
                else:
                    match = json.loads(matches[0][0])
                    for destination, origin_field in join['fields'].items():
                        if row.get(destination) is not None and row[destination] != get(match, origin_field):
                            raise ValueError(f"join would replace conflicting source field: {destination} [source={source} adapter=explicit_join key={str(values)[:160]}]")
                        row[destination] = get(match, origin_field)
                self.store.put(target, row, merge=True)

    def payload(self, h):
        if not h:
            return None
        found = self.store.db.execute('SELECT b FROM payloads WHERE h=?', (h,)).fetchone()
        return {'bytes': found[0], 'path': None} if found else None

    def original_payload(self, row):
        custody = row.get('original_crop_custody') or {}
        return self.payload(row.get('crop_sha256')) if custody.get('hash_match') else None

    def export_table(self, table, output_name=None, split=None):
        name = output_name or table
        directory = ('registry/book_registry' if name == 'book_registry' else
                     f'data/{name}/{split}' if name in ('real', 'synthetic') else 'tables/' + name)
        stage = 'export:' + directory
        receipt_path = self.work / (digest(stage) + '.json')
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            for f in receipt['files']:
                verify_file({**f, 'path': str(safe_path(self.out, f['path']))})
            return receipt['files']
        writer = Shards(self.out, name, directory, self.cap, self.target, self.work / 'batches', stream_resume=True)
        exported = 0
        skip = writer.committed_rows
        for key, r in self.store.rows(table):
            if split is not None:
                if not isinstance(r.get('split'), str) or not r['split']:
                    raise failure('export row lacks an explicit split')
                if r['split'] != split:
                    continue
            if name == 'real' and not r.get('release'):
                continue
            exported += 1
            if exported <= skip:
                continue
            self.deadline.check()
            if name in ('real', 'synthetic', 'page_images'):
                r['image'] = (self.original_payload(r) if name == 'real' else self.payload(r.get('image_sha256')))
                if name == 'real':
                    r['trainer_image'] = self.payload(r.get('training_image_sha256'))
                    r['trainer_variants'] = [{**v, 'image': self.payload(v['image_sha256'])}
                                             for v in r.get('trainer_variants', [])]
            source, adapter = origin(self.lock, r, table)
            with diagnostic(source, adapter, key):
                self.policy.validate(name, r, final=True)
                writer.add(r)
        files = writer.close()
        with atomic_boundary():
            if len(files) == 1 and name not in ('real', 'synthetic', 'page_images'):
                old = self.out / files[0]['path']
                singleton = self.out / ('registry/book_registry.parquet' if name == 'book_registry' else f'tables/{name}.parquet')
                old.replace(singleton)
                old.parent.rmdir()
                files = [{**info(singleton, self.out), 'rows': files[0]['rows']}]
            atomic_json(receipt_path, {'binding': self.binding, 'files': files})
        self.transaction_boundary(stage, sum(f['rows'] for f in files))
        return files

    def json_parts(self, relative, iterator):
        """Record streams are split on actual closed gzip sizes too."""
        paths, buffer, weight = [], [], 0
        def emit(rows):
            p = self.out / relative / f'part-{len(paths):06d}.jsonl.gz'
            p.parent.mkdir(parents=True, exist_ok=True)
            temp = p.with_name(p.name + '.partial')
            with temp.open('wb') as raw:
                with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0, filename='') as f:
                    for row in rows:
                        f.write((canonical(sanitize(row)) + '\n').encode())
            if temp.stat().st_size > self.cap:
                temp.unlink()
                if len(rows) < 2:
                    raise ValueError('single JSON record exceeds cap')
                middle = len(rows) // 2
                emit(rows[:middle])
                emit(rows[middle:])
            else:
                temp.replace(p)
                paths.append(info(p, self.out))
        for row in iterator:
            size = len(canonical(sanitize(row)).encode()) + 1
            if buffer and (weight + size > min(self.target, 8_000_000)):
                emit(buffer)
                buffer, weight = [], 0
            buffer.append(row)
            weight += size
        if buffer:
            emit(buffer)
        if relative == 'decisions' and len(paths) == 1:
            old = self.out / paths[0]['path']
            singleton = self.out / 'decisions/decisions.jsonl.gz'
            old.replace(singleton)
            paths = [info(singleton, self.out)]
        return paths

    def reconcile(self):
        report = []
        for check in self.lock.get('reconciliations', []):
            left, right = check['left'], check['right']
            def difference(a, b):
                return self.store.db.execute('SELECT k FROM keysets WHERE s=? EXCEPT SELECT k FROM keysets WHERE s=? ORDER BY k', (a, b))
            counts = {}
            for direction, a, b in (('left_only', left, right), ('right_only', right, left)):
                count = self.store.db.execute('SELECT COUNT(*) FROM (SELECT k FROM keysets WHERE s=? EXCEPT SELECT k FROM keysets WHERE s=?)', (a, b)).fetchone()[0]
                paths = self.json_parts('manifests/reconciliation/' + check['name'] + '/' + direction,
                                        ({'key': k, 'detail': json.loads(self.store.db.execute('SELECT j FROM keysets WHERE s=? AND k=?', (a, k)).fetchone()[0])} for k, in difference(a, b)))
                counts[direction] = {'count': count, 'parts': paths}
            totals = {side: self.store.db.execute('SELECT COUNT(*) FROM keysets WHERE s=?', (which,)).fetchone()[0]
                      for side, which in (('left', left), ('right', right))}
            passed = all([self.policy.coverage('reconciliation.' + check['name'] + '.' + d,
                         counts[d]['count'], check[d], comparable=False, enforce=False)
                         for d in ('left_only', 'right_only')]) and all(totals[s] > 0 for s in totals)
            report.append({**check, 'observed': counts, 'totals': totals, 'passed': passed})
        atomic_json(self.out / 'manifests/RECONCILIATION.json', {'smoke': self.smoke, 'checks': report})
        self.json_parts('manifests/keysets', ({'set': s, 'key': k, 'detail': json.loads(j)} for s, k, j in
                        self.store.db.execute('SELECT s,k,j FROM keysets ORDER BY s,k')))
        self.json_parts('manifests/source_keys', ({'source': s, 'key': k, 'table': t, 'expected': json.loads(j)} for s, k, t, j in
                        self.store.db.execute('SELECT s,k,t,j FROM source_witness ORDER BY s,k,t')))
        return all(r['passed'] for r in report)

    def synthetic_identity_coverage(self):
        splits = {}
        for split, total, collisions, groups in self.store.db.execute("""SELECT json_extract(j,'$.split'),
                COUNT(*), SUM(CASE WHEN json_extract(j,'$.key_collision_size')>1 THEN 1 ELSE 0 END),
                COUNT(DISTINCT json_extract(j,'$.key_collision_group')) FROM records
                WHERE t='synthetic' GROUP BY 1"""):
            splits[split] = {'rows': total, 'collision_rows': collisions, 'collision_groups': groups}
        membership = []
        for model, role, pool, variant, total, unique, ambiguous, groups in self.store.db.execute("""SELECT
                json_extract(j,'$.model_id'), json_extract(j,'$.role'), json_extract(j,'$.pool'),
                json_extract(j,'$.variant'), COUNT(*),
                SUM(CASE WHEN json_extract(j,'$.synthetic_key') IS NOT NULL THEN 1 ELSE 0 END),
                SUM(CASE WHEN json_extract(j,'$.synthetic_key') IS NULL THEN 1 ELSE 0 END),
                COUNT(DISTINCT CASE WHEN json_extract(j,'$.synthetic_key') IS NULL
                    THEN json_extract(j,'$.synthetic_match_group') END) FROM records
                WHERE t='training_membership' AND json_extract(j,'$.synthetic_match_group') IS NOT NULL
                GROUP BY 1,2,3,4"""):
            membership.append({'model_id': model, 'role': role, 'pool': pool, 'variant': variant,
                'rows': total, 'unique_exact_rows': unique, 'ambiguous_rows': ambiguous, 'ambiguous_groups': groups})
        collision_types = Counter()
        for variants, in self.store.db.execute("""SELECT COUNT(DISTINCT json_extract(j,'$.synthetic_match_group'))
                FROM records WHERE t='synthetic' GROUP BY json_extract(j,'$.legacy_key_group') HAVING COUNT(*)>1"""):
            collision_types['identical_observation_groups' if variants == 1 else 'differing_observation_groups'] += 1
        return {'release_key': DEFAULT_KEYS['synthetic'], 'ordinal_base': 0,
            'collision_key': ['factory_build_id', 'line_id', 'reuse_index'],
            'splits': splits,
            'collision_groups': self.store.db.execute("""SELECT COUNT(DISTINCT json_extract(j,'$.key_collision_group'))
                FROM records WHERE t='synthetic'""").fetchone()[0],
            'collision_rows': sum(s['collision_rows'] for s in splits.values()),
            'collision_types': {k: collision_types[k] for k in ('identical_observation_groups', 'differing_observation_groups')},
            'training_membership': membership,
            'ambiguous_handling': 'Every prepared position retained. Null synthetic_key joins all exact candidates via synthetic_match_group; no historical pairing inferred. trained_in marks the whole group only when consumed multiplicity equals A12 multiplicity.'}

    def summaries(self):
        coverage = defaultdict(lambda: {'rows': 0, 'fields': Counter(), 'missing_reasons': Counter()})
        distributions = defaultdict(lambda: defaultdict(Counter))
        for _, row in self.store.rows('rows'):
            group = canonical([row.get('release', 'census'), row.get('wave'), row.get('source'), row.get('provider')])
            coverage[group]['rows'] += 1
            for field in SOURCE_FIELDS:
                if row.get(field) is not None:
                    coverage[group]['fields'][field] += 1
                else:
                    coverage[group]['missing_reasons'][field] += 1
        for _, row in self.store.rows('synthetic'):
            split = row['split']
            for field in ('severity', 'script_class', 'font', 'polarity', 'bg_type', 'source_dataset', 'reuse_index', 'n_ops'):
                distributions[split][field][str(row.get(field))] += 1
            distributions[split]['applied_ops'].update(row['applied_ops'])
        native_pages = defaultdict(lambda: {'rows': 0, 'source_page_id': 0, 'source_page_id_null': 0,
                                            'page': 0, 'page_null': 0, 'namespaces': Counter()})
        for _, row in self.store.rows('native_page_observations'):
            counts = native_pages[row['population'] + ':' + row['source']]
            counts['rows'] += 1
            counts['source_page_id'] += row.get('source_page_id') is not None
            counts['source_page_id_null'] += row.get('source_page_id') is None
            counts['page'] += row.get('page') is not None
            counts['page_null'] += row.get('page') is None
            if row.get('source_page_namespace'):
                counts['namespaces'][row['source_page_namespace']] += 1
        self.json_parts('manifests/native_pages', (r for _, r in self.store.rows('native_page_observations')
                       if r.get('source_page_id') is not None or r.get('page') is not None))
        self.policy.nulls.clear()
        fields = defaultdict(Counter)
        for table in TABLES + ('synthetic', 'real'):
            for _, row in self.store.rows('rows' if table == 'real' else table):
                if table == 'real':
                    if not row.get('release'):
                        continue
                    row['image'] = self.original_payload(row)
                    row['trainer_image'] = self.payload(row.get('training_image_sha256'))
                self.validate_write(table, row, final=True, count=True)
                for field, binding in self.policy.columns(table).items():
                    fields[binding + ':' + table + '.' + field]['nonnull' if row.get(field) is not None else 'null'] += 1
                if table == 'real' and 'assets.original_crops' in self.policy.entries:
                    fields['assets.original_crops:real.image']['nonnull' if row.get('image') else 'null'] += 1
        source_counts = {binding: {field: Counter() for field in entry.get('coverage', {})}
            for binding, entry in self.policy.entries.items()
            if binding in SOURCE_BINDINGS and (entry.get('value') or {}).get('input')}
        for _, observation in self.store.rows('binding_observations'):
            for field, value in observation['values'].items():
                source_counts[observation['binding']][field]['nonnull_rows' if value is not None else 'missing_rows'] += 1
                source = self.policy.entries[observation['binding']]['value']['input']
                self.policy.value(observation['binding'], 'source.' + source + '.' + field, value)
        for binding, observed in source_counts.items():
            for field, counts in observed.items():
                expected = self.policy.entries[binding]['coverage'][field]
                for kind in ('nonnull_rows', 'missing_rows'):
                    self.policy.coverage(binding + '.source.' + field + '.' + kind, counts[kind], expected[kind],
                                         selected=sum(counts.values()), total=expected['nonnull_rows'] + expected['missing_rows'])
        original_coverage = self.crops.coverage()
        self.policy.original_coverage(original_coverage)
        def image_hash(key):
            row = self.store.by_key('rows', [key])
            if not row or not row.get('release'):
                return None
            payload = self.original_payload(row)
            return (digest(payload['bytes']) if payload else None,)
        original_binding = self.policy.entries.get('assets.original_crops', {})
        published_images = self.crops.published_counts(image_hash, smoke=bool(self.smoke),
            populations=original_binding.get('coverage', {}),
            allow_unselected={s['name'] for s in self.lock['inputs'] if s['adapter'] in ('keyset', 'prepared')})
        self.policy.original_published_coverage(published_images, original_coverage)
        from .accept_layers import binding_coverage, raw_coverage
        atomic_json(self.out / 'manifests/COVERAGE.json', {
            'book_id_resolution': book_id_policy.coverage(r for _, r in self.store.rows('rows')),
            'split_resolution': {
                'authority': 'pinned book registry; source disagreements retained as diagnostics',
                'conflicts': [{'source_split': native, 'split': split, 'rows': count}
                    for native, split, count in self.store.db.execute("""SELECT
                        json_extract(j,'$.source_split'),json_extract(j,'$.split'),COUNT(*)
                        FROM records WHERE t='rows' AND json_extract(j,'$.split_conflict')=1
                        GROUP BY 1,2 ORDER BY 1,2""")]},
            'label_publication_projection': {
                'lock': self.lock.get('label_publication_projection'),
                'consumer_excluded_variants': {v: {'rows': n, 'non_null_texts': texts}
                    for v, n, texts in self.store.db.execute(
                        'SELECT variant,COUNT(*),SUM(non_null) FROM label_projection_exclusions GROUP BY variant')},
                'route_text': 'null with recorded status and reason'},
            'unresolved_binding_consequences': binding_coverage(self), 'raw_text': raw_coverage(self),
            'populations': coverage, 'smoke': self.smoke,
            'original_crops': {'populations': original_coverage,
                'published_images': published_images, 'root_index': self.crop_root_report,
                'measured_probe': {'populations': original_binding.get('coverage', {}),
                    'source_report': original_binding.get('source_report'),
                    'source_report_sha256': original_binding.get('source_report_sha256'),
                    'content_index': original_binding.get('content_index'),
                    'validation_originals': original_binding.get('validation_originals')},
                'unit': 'selected source observations; exact S1/v4 mappings; populations overlap',
                'complete': not bool(self.smoke), 'decision': self.policy.status('assets.original_crops')},
            'native_pages': {'populations': native_pages,
                'unit': 'selected source observations; overlapping populations; not distinct release rows',
                'records': 'manifests/native_pages'},
            'binding_writes': {**self.policy.report(), 'field_coverage': fields, 'source_coverage': source_counts},
            'smoke_unloaded_targets': self.smoke_unloaded_targets(),
            'synthetic_identity': self.synthetic_identity_coverage(),
            'book_bridge': {'decision': self.lock.get('book_bridge', {}).get('decision'),
                'populations': {e['population']: e for _, e in self.store.rows('book_bridge_coverage')},
                'measured_probe': {
                    'populations': self.lock.get('book_bridge', {}).get('coverage', {}),
                    'evidence': self.lock.get('book_bridge', {}).get('evidence', {}),
                    'measurement': self.lock.get('book_bridge', {}).get('measurement', {}),
                    'qualification': 'retained complete probe; separate from this build, including smoke'},
                'source_projection': self.lock.get('book_bridge', {}).get('source_projection', {}),
                'unit': 'source observations; populations overlap; not disjoint release-row counts'},
            'historical_unknowns': [e for e in self.lock.get('unresolved_bindings', [])
                                    if e.get('historical_unknown')],
            'pending_resolver_bindings': pending_resolvers(self.lock),
            'partial_bindings': self.lock.get('partial_bindings', []),
            'resolved_bindings': self.lock.get('resolved_bindings', []),
            'keyset_bridge_coverage': [e for _, e in self.store.rows('keyset_bridge_coverage')],
        })
        configured = {name: e['record'].get('recipe', {}) for name, e in self.build_info.items()
                      if 'recipe' in e['record']}
        atomic_json(self.out / 'synthetic/RECIPE.json', {'configured': configured,
                    'configured_per_split': {split: configured for split in distributions},
                    'realised_per_split': distributions, 'smoke': self.smoke,
                    'note': 'Configured probabilities and observed counts have separate denominators; operations are ordered per line.'})
        for name, evidence in self.build_info.items():
            self.json_parts('synthetic/BUILD/' + name, [evidence])
        op_source = next((e['record'] for e in self.build_info.values() if 'map' in e['record'] and 'files' in e['record']), {})
        lines = ['# Applied operations', '', op_source.get('binding', 'No historical implementation map supplied.'), '',
                 '| Operation (variants retained) | Function | Source SHA256 |', '| --- | --- | --- |']
        observed = sorted({op for fields in distributions.values() for op in fields['applied_ops']})
        for op in observed:
            entry = op_source.get('map', {}).get(op, op_source.get('map', {}).get('crop:*', {}) if op.startswith('crop:') else {})
            lines.append(f"| {op} | {entry.get('file', 'UNMAPPED')}:{entry.get('function', '')} | {entry.get('source_sha256', '')} |")
        (self.out / 'synthetic/OPS.md').write_text('\n'.join(lines) + '\n')
        return distributions

    @contextual
    def run(self):
        started = time.monotonic()
        with Progress('ingest') as progress:
            self.ingest()
        self.timings.append(progress.result)
        final = self.work / 'FINAL.json'
        if final.exists():
            saved = json.loads(final.read_text())
            for f in saved['files']:
                verify_file({**f, 'path': str(safe_path(self.out, f['path']))})
            return json.loads((self.out / 'manifests/BUILD_RECEIPT.json').read_text())
        self.import_label_variants()
        with Progress('derive') as progress:
            self.derive()
        self.timings.append(progress.result)
        # Hash bytes count repeated closed-file readbacks, not SQL/image work.
        # A byte-derived ETA here misrepresented the quadratic label join.
        with Progress('export') as progress:
            configs, boundaries = layered.export(self)
        self.timings.append(progress.result)
        # These finishing passes together exceed one debug window on P2i rates.
        # Retain each completed pass, so a pause in summaries never repeats the
        # already closed evidence/reconciliation pass.
        self.store.db.execute('CREATE TABLE IF NOT EXISTS finish_steps(stage TEXT PRIMARY KEY,j TEXT)')
        def finish(stage, action):
            saved = self.store.db.execute('SELECT j FROM finish_steps WHERE stage=?', (stage,)).fetchone()
            if saved:
                value = json.loads(saved[0])
            else:
                self.deadline.check()
                with Progress(stage) as progress:
                    result = action()
                value = {'result': result, 'timing': progress.result}
                with atomic_boundary():
                    self.store.db.execute('INSERT INTO finish_steps VALUES(?,?)', (stage, canonical(value)))
                    self.store.db.commit()
                self.transaction_boundary('finish:' + stage, 1)
                self.deadline.check()
            self.timings.append(value['timing'])
            return value['result']
        def evidence():
            self.json_parts('decisions', (v for _, v in self.store.rows('decisions')))
            self.json_parts('manifests/smoke_unloaded_targets', (
                {'source': s, 'adapter': a, 'table': t, 'key': k, 'target': target, 'partner': partner}
                for s, a, t, k, target, partner in self.store.db.execute(
                    'SELECT * FROM smoke_skips ORDER BY s,a,t,k')))
            return self.reconcile()
        keyed_ok = finish('evidence-reconciliation', evidence)
        distributions = finish('summaries', self.summaries)
        public_lock = sanitize(self.lock)
        atomic_json(self.out / 'manifests/INPUT_LOCK.json', public_lock)
        atomic_json(self.out / 'manifests/FEATURE_INPUTS.json', {
            'codec': sanitize(json.loads(Path(self.lock['features']['codec']['path']).read_text())),
            'script_ranges': self.features.ranges, 'unicode_version': ud.unidata_version,
            'sources': self.lock['features']})
        atomic_json(self.out / 'manifests/CONFIGS.json', configs)
        counts = {t: self.store.db.execute('SELECT COUNT(*) FROM records WHERE t=?', (t,)).fetchone()[0]
                  for t in TABLES + ('synthetic',)}
        import hashlib
        logical_keys = {}
        for table in TABLES + ('synthetic',):
            h = hashlib.sha256()
            for k, in self.store.db.execute('SELECT k FROM records WHERE t=? ORDER BY k', (table,)):
                h.update((k + '\n').encode())
            logical_keys[table] = h.hexdigest()
        receipt = {'schema': VERSION, 'binding': self.binding, 'mode': 'smoke' if self.smoke else 'full',
                   'smoke': self.smoke, 'counts': counts,
                   'crop_index_reused': self.file_checks.index_reused,
                   'smoke_unloaded_targets': self.smoke_unloaded_targets(), 'key_reconciliation_passed': keyed_ok,
                   'elapsed_seconds': None, 'timing_evidence': 'private work/STAGES.json; excluded for deterministic resume bytes', 'environment': {'python': platform.python_version(),
                   'unicode': ud.unidata_version, 'sqlite': sqlite3.sqlite_version},
                   'code': json.loads((self.work / 'BINDING.json').read_text())['code'],
                   'producing_commit': self.lock.get('release_code_commit'),
                   'acceptance': 'pending independent accept_dataset.py; fixture/smoke is not release acceptance'}
        atomic_json(self.out / 'manifests/BUILD_RECEIPT.json', receipt)
        if self.lock.get('trained_identity'):
            atomic_json(self.out / 'manifests/A1.json', sanitize(self.lock['trained_identity']))
        write_card(self.out / 'README.md', self.lock, configs, distributions, self.smoke)
        from .release_tree import GITATTRIBUTES, inventory as release_inventory, retained_public
        frozen = self.lock.get('frozen_trained', {})
        (self.out / '.gitattributes').write_text(GITATTRIBUTES)
        atomic_json(self.out / 'manifests/RELEASE_TREE.json', release_inventory(frozen))
        (self.out / 'UPDATING.md').write_text(Path(__file__).with_name('UPDATING.md').read_text())
        (self.out / 'manifests/UPDATES.jsonl').touch()
        if not keyed_ok and not self.smoke:
            raise ValueError('key reconciliation failed; findings retained without complete manifest')
        with Progress('manifest-hash') as progress:
            inventory = list(parallel_info((p for p in sorted(self.out.rglob('*')) if p.is_file()
                         and not p.relative_to(self.out).as_posix().startswith(('data/real/', 'data/synthetic/train/'))
                         and p.relative_to(self.out).as_posix() not in ('manifests/MANIFEST.json', 'manifests/SHA256SUMS')), self.out))
            if any(f['bytes'] > self.cap for f in inventory):
                raise ValueError('closed public file exceeds cap')
            atomic_json(self.out / 'manifests/MANIFEST.json', {'schema': VERSION, 'binding': self.binding,
                        'file_cap': self.cap, 'files': inventory, 'configs': configs, 'counts': counts,
                        'logical_key_sha256': logical_keys, 'layout': 'layered-v1',
                        'immutable_crop_shards': boundaries, 'frozen_trained': frozen,
                        'retained_public': retained_public(frozen)})
            checksums = inventory + [info(self.out / 'manifests/MANIFEST.json', self.out)]
            text = ''.join(f"{f['sha256']}  {f['path']}\n" for f in sorted(checksums, key=lambda f: f['path']))
            if len(text.encode()) > self.cap:
                raise ValueError('SHA256SUMS exceeds cap; source selection needs a checksum-parts index')
            (self.out / 'manifests/SHA256SUMS').write_text(text)
        self.timings.append(progress.result)
        atomic_json(self.work / 'STAGES.json', self.timings)
        atomic_json(final, {'binding': self.binding,
                           'files': list(parallel_info((p for p in sorted(self.out.rglob('*')) if p.is_file()), self.out))})
        return receipt


def selection_role(pool):
    return {'seal04_dev': 'checkpoint_selection_and_stage_b_hyperparameters',
            'harvest_dev': 'stage_b_hyperparameters', 'seal04_test': 'report_only',
            'harvest_test': 'report_only', 'validation': 'validation_reference'}.get(pool, 'training')


def source_card(lock):
    binding = lock.get('book_bridge', {})
    if not any(binding.get('coverage', {}).values()):
        return ('## Source\n\nNo complete population source-coverage probe is bound to this build. '
                'See COVERAGE.json for observed fields and missing reasons.\n\n')
    text = ('## Source\n\n'
            'The table gives non-null source fields per population from the retained complete book/source probe, '
            'not counts from this build. Populations overlap and must not be summed as release lines; '
            'a bounded smoke does not reproduce these full scans. Provider and item are measured separately, '
            'not as an unmeasured joint fraction. Exact counts and null reasons for canonical book IDs and '
            'every source field are in COVERAGE.json `book_bridge.measured_probe.populations`; '
            '`book_bridge.populations` reports this build separately.\n\n'
            '| Population | Lines | Book ID | Provider | Item | source_url | catalogue_url |\n'
            '| --- | ---: | ---: | ---: | ---: | ---: | ---: |\n')
    for population in binding.get('populations', []):
        counts = binding.get('coverage', {}).get(population)
        if counts is None:
            text += f'| {population} | unknown | unknown | unknown | unknown | unknown | unknown |\n'
            continue
        rows = counts['rows']
        cells = []
        for field in ('book_id', 'provider', 'item', 'source_url', 'catalogue_url'):
            present = counts['source_fields'][field]['nonnull']
            fraction = f'{100 * present / rows:.2f}%' if rows else 'N/A'
            cells.append(f'{present:,}/{rows:,} ({fraction})')
        text += f'| {population} | {rows:,} | ' + ' | '.join(cells) + ' |\n'
    text += '\n' + '\n\n'.join(binding.get('source_projection', {}).values()) + '\n\n'
    for overlay in binding.get('coverage_overlays', []):
        text += (f"Validation source coverage overlay: {overlay['basis']} "
                 f"Evidence: `{overlay['report']}`; SHA256 `{overlay['sha256']}`.\n\n")
    for evidence in binding.get('evidence', {}).values():
        text += f"Probe evidence: `{evidence['path']}`; SHA256 `{evidence['sha256']}`.\n\n"
    return text


def original_images_card(lock):
    entry = next((e for group in ('resolved_bindings', 'partial_bindings', 'unresolved_bindings')
                  for e in lock.get(group, []) if e['field'] == 'assets.original_crops'), {})
    text = ('## Images\n\n`image` contains verified original bytes; width, height and aspect '
            'come from that image. Missing originals have null image/dimensions and an exact custody reason. '
            '`trainer_image` retains prepared bytes independently.\n\n')
    if entry.get('coverage'):
        text += ('Complete source measurement (overlapping populations, not distinct release rows; '
                 'not this build):\n\n| Population | Status | Verified originals | Missing reason/count |\n'
                 '| --- | --- | ---: | --- |\n')
        for pop, counts in entry['coverage'].items():
            reasons = ', '.join(f'{k}: {v:,}' for k, v in counts['reasons'].items() if v) or 'none'
            text += (f"| {pop} | {counts['status']} | {counts['custody_established']:,}/{counts['rows']:,} "
                     f'| {reasons} |\n')
        text += ('\n`no_recorded_path` means no matching original crop under any declared root. '
                 'COVERAGE.json `original_crops.measured_probe` retains this measurement and report identity; '
                 '`original_crops.populations` reports actual build observations separately.\n\n')
    return text


def write_card(path, lock, configs, distributions, smoke):
    # JSON is valid YAML; emitting front matter this way avoids a YAML dependency.
    yaml = ['---', 'pretty_name: "Greek OCR lines ' + lock['dataset_version'] + '"',
            'language: [el, grc, la, en, ru, sr]', 'configs:']
    for name in [n for n in ('real', 'synthetic') if n in configs] + sorted(set(configs) - {'real', 'synthetic'}):
        yaml += ['  - config_name: ' + name]
        if name == ('real' if 'real' in configs else 'lines'):
            yaml += ['    default: true']
        yaml += ['    data_files:']
        for split, paths in configs[name].items():
            yaml += ['      - split: ' + split, '        path: ' + json.dumps(paths)]
    text = '\n'.join(yaml) + '\n---\n\n# Greek OCR lines ' + lock['dataset_version'] + '\n\n'
    text += ('**Bounded smoke build; incomplete populations.**\n\n' if smoke else '')
    text += card.introduction(lock['dataset_version'], configs)
    text += card.exactness(path.parent) + card.training()
    text += ('Native page references use `source_page_id` and `source_page_namespace`, with all retained '
             'references in `source_page_references_json`; these fields do not join to `pages`. '
             'The `page` source field retains an explicitly recorded page number; identifiers and indices '
             'are never parsed into page numbers. COVERAGE.json `native_pages.populations` counts native '
             'IDs and page numbers by selected source/population; `manifests/native_pages` retains observation evidence. '
             'Historical logical-page/frame/run FKs remain null with `binding_missing_reasons_json`; '
             '`binding_writes` counts governed fields, null reasons and partial source coverage.\n\n'
             'Synthetic origin, ordered operations and font_sha16 are recovered fields. Image hash/dimensions and n_ops are computed. '
             'A font prefix is never a full SHA256. Historical nulls have search receipts. A12 train/val/reserved are one identified build; '
             'old_synth is a separate build and is not merged by recipe nickname. Source/effective recipes and build evidence are in '
             'synthetic/BUILD; operation implementations are in synthetic/OPS.md.\n\n'
             'Each synthetic observation has a `synthetic_key`: canonical JSON '
             '`[factory_build_id, split, source_shard, source_ordinal]`, with a full locked shard path and zero-based ordinal. '
             'Every observation is retained, including identical rows. `line_id` and `reuse_index` are attributes; '
             '`key_collision_group` and `key_collision_size` expose their repeated legacy keys. '
             'See COVERAGE.json `synthetic_identity` for per-split collision and prepared membership counts. '
             'Join synthetic training_membership by `synthetic_key` when present. For indistinguishable candidates, '
             'that key is null: join all candidates by `synthetic_match_group`; `synthetic_candidate_count` and '
             '`synthetic_mapping_status` describe the ambiguity. Every prepared position has its own membership_id. '
             'No historical one-to-one pairing is inferred; full train multiset equality is checked.\n\n')
    text += card.joins(lock['dataset_version']) + card.raw_labels(path.parent)
    text += source_card(lock) + original_images_card(lock)
    text += ('## Configured and realised generator distributions\n\n'
             'Configured probabilities: synthetic/RECIPE.json `configured`. Realised counts are measured independently per split:\n\n'
             '| Split | Field | Observed counts |\n| --- | --- | --- |\n')
    for split, fields in sorted(distributions.items()):
        for field, counts in sorted(fields.items()):
            text += f'| {split} | {field} | {canonical(counts)} |\n'
    text += '\nComponent versions: ' + canonical(lock.get('component_versions', {})) + '\n\n'
    text += ('## Known gaps\n\n'
             '- Per-line operation parameters/seeds were not retained: issue **#TBD-generator-provenance**.\n'
             '- Full historical font SHA and precise text-origin locators can be unavailable: issue **#TBD-synthetic-origin**.\n'
             '- Source bibliography/frame/identity coverage findings: issue **#TBD-source-coverage**; see COVERAGE and input search receipts.\n'
             'Issue placeholders are replaced by the coordinator after checkpoint triage.\n')
    for entry in lock.get('unresolved_bindings', []):
        status = 'historical_unknown; non-blocking' if entry.get('historical_unknown') else 'pending resolver'
        text += f"- `{entry['field']}` = null ({status}): {entry['reason']} Evidence: {entry['evidence']}."
        if entry.get('resolve_probe'):
            text += ' Probe item: `' + entry['resolve_probe'] + '`.'
        text += '\n'
    for entry in lock.get('partial_bindings', []):
        measured = ('See the Source table and COVERAGE.json `book_bridge.measured_probe.populations`'
                    if entry['field'] == 'bibliography.book_bridge' else canonical(entry['coverage']))
        text += (f"- `{entry['field']}` = partial (non-blocking): {entry['reason']} "
                 f"Measured coverage: {measured}. Evidence: {entry['evidence']}.\n")
    path.write_text(text)


def plan(lock):
    inputs = sum(f['bytes'] for s in lock['inputs'] for f in s['files'])
    assets = sum(f['bytes'] for f in lock['assets'])
    rows = Counter()
    for s in lock['inputs']:
        for f in s['files']:
            if f['path'].endswith('.parquet'):
                import pyarrow.parquet as pq
                rows[s.get('table', s['adapter'])] += pq.ParquetFile(f['path']).metadata.num_rows
    estimates = {table: {'bytes': int(lock.get('estimates', {}).get('bytes_per_table', {}).get(table, rows[table] * 2048)),
                          'basis': 'supplied measurement' if table in lock.get('estimates', {}).get('bytes_per_table', {}) else
                          'Parquet footer rows × 2048 metadata bytes; unknown JSONL rows are not included'} for table in TABLES}
    estimates['real'] = {'bytes': assets + inputs, 'basis': 'upper envelope before overlap/dedup; source + trainer payloads'}
    estimates['synthetic'] = {'bytes': sum(f['bytes'] for s in lock['inputs'] if s['adapter'] == 'synthetic' for f in s['files']),
                              'basis': 'selected A12 source shard bytes'}
    total = sum(v['bytes'] for v in estimates.values())
    throughput = lock.get('estimates', {}).get('aggregate_mb_per_cpu_second', 20)
    return {'input_bytes': inputs, 'asset_bytes': assets, 'bytes_per_table': estimates,
            'estimated_public_bytes': total, 'estimated_files': sum(max(1, math.ceil(v['bytes'] / TARGET)) for v in estimates.values()) + 32,
            'estimated_cpu_hours': (3 * (inputs + assets) + total) / (throughput * 1_000_000 * 3600),
            'cpu_basis': f'{throughput} MB/CPU-second assumed aggregate hash/join/write rate; replace using bounded Clariden smoke timing',
            'scratch_bytes_build_plus_readback': 3 * total + inputs + assets,
            'qualification': 'sizing estimate, not a qualified allocation or completion prediction'}


def bound_lock(args, p):
    lock = read_lock(args.input_lock, args.smoke)
    from .build_locks import validate_frozen, validate_labels
    if args.frozen_manifest:
        frozen = json.loads(args.frozen_manifest.read_text())
        if frozen.get('schema') == 'hfd-frozen-trained-v1':
            if not args.a1_report:
                p.error('P2c frozen lock requires --a1-report')
            validate_frozen(frozen, args.a1_report)
        lock['frozen_trained'] = frozen
    if args.a1_report:
        lock['trained_identity'] = card.validate_a1(json.loads(args.a1_report.read_text()))
    if args.label_variant_lock:
        variant_lock = json.loads(args.label_variant_lock.read_text())
        if variant_lock.get('schema') == 'hfd-labels-v1':
            validate_labels(variant_lock, args.smoke)
        lock['label_variant_lock'] = info(args.label_variant_lock)
        lock['label_variant_adapters'] = variant_lock['label_variant_adapters']
        lock['raw_text_responses'] = variant_lock['raw_text_responses']
        lock['label_publication_projection'] = variant_lock.get('publication_projection')
    return lock


@contextual
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--validate-spec', type=Path, help='validate source-spec structure without source I/O')
    p.add_argument('--freeze', type=Path, help='explicit source spec → full file/hash lock')
    p.add_argument('--lock-out', type=Path)
    p.add_argument('--input-lock', type=Path)
    p.add_argument('--out', type=Path)
    p.add_argument('--work', type=Path)
    p.add_argument('--smoke', type=int)
    p.add_argument('--resume', action='store_true')
    p.add_argument('--independent-readback', action='store_true', help='finish resumable acceptance before chain completion')
    p.add_argument('--deadline-seconds', type=float, help='clean pause/rollback after this allocation budget')
    p.add_argument('--plan', action='store_true')
    p.add_argument('--measure', action='store_true', help='fresh 2 percent real slice rehearsal of every large input')
    p.add_argument('--frozen-manifest', type=Path, help='A1 exact frozen trained inventory and configs')
    p.add_argument('--a1-report', type=Path, help='PASS A1.json for measured card counts and frozen-view provenance')
    p.add_argument('--label-variant-lock', type=Path, help='P1 hash-locked label_variant_adapters + raw_text_responses')
    p.add_argument('--file-cap', type=int, default=CAP)
    p.add_argument('--target-bytes', type=int, default=TARGET)
    args = p.parse_args(argv)
    offline()
    if args.validate_spec:
        document = validate_spec(args.validate_spec)
        print(canonical({'valid': True, 'dataset_version': document['dataset_version'],
                         'historical_unknowns': sum(bool(e.get('historical_unknown')) for e in document.get('unresolved_bindings', [])),
                         'partial_bindings': len(document.get('partial_bindings', [])),
                         'resolved_bindings': len(document.get('resolved_bindings', [])),
                         'pending_resolver_bindings': len(pending_resolvers(document)),
                         'pending_resolver_populations': {e['field']: e['value']['pending_populations']
                             for e in pending_resolvers(document) if (e.get('value') or {}).get('pending_populations')},
                         'qualification': 'structure only; freeze hashes local inputs; full joins still required'}))
        return 0
    if args.freeze:
        if not args.lock_out:
            p.error('--freeze requires --lock-out')
        with Progress('freeze-input-hashing'):
            freeze(args.freeze, args.lock_out)
        print('input lock written: ' + str(args.lock_out))
        return 0
    if not args.input_lock:
        p.error('--input-lock is required')
    if not 0 < args.target_bytes <= args.file_cap <= CAP or args.smoke is not None and args.smoke <= 0:
        p.error('invalid cap/target/smoke')
    if args.measure or args.plan:
        lock = bound_lock(args, p)
    if args.measure:
        if not args.out or args.resume:
            p.error('--measure requires fresh --out and no --resume')
        from .measure import measure
        result = measure(lock, args.out)
        return 0 if result['projected_full_hours'] is not None else 2
    if args.plan:
        print(json.dumps(plan(lock), indent=2))
        return 0
    if not args.out:
        p.error('--out is required')
    if args.deadline_seconds is not None and args.deadline_seconds <= 0:
        p.error('--deadline-seconds must be positive')
    work = args.work or args.out.with_name(args.out.name + '.work')
    builder = None
    deadline = Deadline(args.deadline_seconds)
    status = 'FAILED'
    try:
        with deadline:
            lock = bound_lock(args, p)
            builder = Builder(lock, args.out, work, args.smoke, args.file_cap, args.target_bytes, args.resume)
            if args.deadline_seconds:
                builder.deadline = deadline
                builder.store.db.set_progress_handler(deadline.interrupt_sql, 10000)
            builder.require_readback = args.independent_readback
            receipt = builder.run()
            if args.independent_readback:
                from .accept_dataset import Acceptance
                scratch = builder.work / 'readback'
                verifier = Acceptance(builder.out, scratch, input_lock=builder.out / 'manifests/INPUT_LOCK.json',
                                      allow_smoke=bool(args.smoke), resume=(scratch / 'accept.sqlite').exists(),
                                      validation_mode='external-cache')
                try:
                    verifier.db.set_progress_handler(deadline.interrupt_sql, 10000)
                    with Progress('independent-readback'):
                        report = verifier.run()
                    atomic_json(builder.work / 'READBACK.json', report)
                finally:
                    verifier.db.set_progress_handler(None, 0)
                    verifier.db.rollback()
                    verifier.db.close()
            print(canonical(receipt))
            status = 'COMPLETE'
    except (BuildPaused, sqlite3.OperationalError):
        if not deadline.expired:
            raise
        status = 'PAUSED'
    finally:
        if builder is not None:
            if args.deadline_seconds:
                builder.store.db.set_progress_handler(None, 0)
                builder.store.db.rollback()
                # Only these writers' uncommitted temporary files are removed.
                for root in (builder.out, builder.work):
                    for path in root.rglob('*.partial'):
                        path.unlink()
                from .chain_status import write_status
                write_status(builder, status)
            builder.store.db.close()
        elif args.deadline_seconds and Path(work).exists():
            atomic_json(Path(work) / 'RUN_STATUS.json', dict(status=status, progress=None, job_id=os.environ.get('SLURM_JOB_ID')))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError) as exc:
        print('build failed: ' + str(exc), file=sys.stderr)
        sys.exit(2)

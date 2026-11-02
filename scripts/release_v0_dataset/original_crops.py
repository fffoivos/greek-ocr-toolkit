"""Original crop custody through recorded bytes/hashes and exact S4h keys.

Hash identity reuses byte verification, never row identity. Bare IDs are never
split, paths never guessed, and prepared trainer bytes are never originals.
"""
import json
import hashlib
import os
import sqlite3
from contextlib import closing
from pathlib import Path

from .accept_bindings import BindingPolicy
from .common import canonical, digest, dimensions, get, mapped, row_key, verify_file

REASONS = ('missing_file', 'hash_mismatch', 'no_recorded_path',
           'no_recorded_hash', 'no_embedded_bytes')
CROP_FIELDS = ('parent_id', 'row_id', 'row_key', 'line_id', 'trainer_line_id',
               'id', 'wave', 'crop_sha256', 'image_sha256', 'binding',
               'crop_path', 'crop_relative_path', 'file_name', 'image_path')
CROP_FIELDS += ('source_url', 'attribution', 'year', 'page_id', 'bbox', 'crop_bbox',
                'book_key', 'crop_width', 'crop_height')


def hash_mismatch(expected, actual, custody, byte_source, label='original image hash mismatch'):
    return (f'{label}: expected={expected} actual={actual} '
            f'custody={custody} bytes_source={byte_source}')


def root_files(root, onerror):
    for directory, dirs, names in os.walk(root, onerror=onerror, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not (Path(directory) / d).is_symlink())
        for name in sorted(names):
            path = Path(directory) / name
            if not path.is_symlink() and path.is_file():
                yield path.resolve()


def file_stamp(path):
    stat = path.stat()
    return [str(path), stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_dev, stat.st_ino]


def root_snapshot(root):
    """Cheap change detection for a pinned byte index; never a new byte hash."""
    errors = []
    h = hashlib.sha256()
    for path in root_files(root, lambda exc: errors.append(str(exc))):
        h.update((canonical(file_stamp(path)) + '\n').encode())
    return h.hexdigest() if root.is_dir() and not errors else None


def population(source):
    return source.get('original_population', source.get('book_population', source['name']))


def eligible(source):
    return (source.get('adapter') in ('row', 's1', 'harvest', 'census') or
            source.get('book_population') in ('old', 'seal04', 'validation') or
            bool(source.get('original_population')))


def crop_metadata(original, source):
    """Keep custody selectors only, before IPC/recursive metadata indexing."""
    names = set(CROP_FIELDS) | {v.split('.')[0] for v in source.get('fields', {}).values()}
    return {k: v for k, v in original.items() if k in names}


def identity(original, source):
    row = mapped(crop_metadata(original, source), source)
    parent = row.get('parent_id', get(original, 'binding.parent_id'))
    ident = row.get('row_id', get(original, 'binding.id'))
    if population(source) == 'seal04':
        ident = ident if ident is not None else row.get('id')
    if source.get('adapter') == 'harvest':
        parent = parent or 'harvest:' + str(row.get('wave'))
        ident = ident if ident is not None else row.get('id')
    keys = []
    if parent is not None and ident is not None:
        keys.append('tuple:' + row_key(parent, ident))
    elif row.get('row_key'):
        keys.append('tuple:' + row['row_key'])
    for value in (row.get('trainer_line_id'), row.get('line_id'), ident):
        if value is not None and 'id:' + str(value) not in keys:
            keys.append('id:' + str(value))
    return keys


class FileChecks:
    """One measured read per distinct recorded file, across spawned readers.

    A builder may import the freeze's hash-pinned index after checking the full
    root metadata snapshot. Selected payload bytes are still hashed on read.
    """
    def __init__(self, db):
        self.db = db
        db.execute('CREATE TABLE IF NOT EXISTS crop_file_checks(path TEXT PRIMARY KEY, result TEXT) WITHOUT ROWID')
        db.executescript('''CREATE TABLE IF NOT EXISTS crop_root_files(
            root TEXT, path TEXT, hash TEXT, PRIMARY KEY(root,path)) WITHOUT ROWID;
            CREATE INDEX IF NOT EXISTS crop_root_hash ON crop_root_files(hash,path);
            CREATE TABLE IF NOT EXISTS crop_root_snapshots(
                root TEXT PRIMARY KEY, snapshot TEXT, report TEXT) WITHOUT ROWID;''')
        self.index_reused = False

    def build(self, roots, check=lambda: None, progress=lambda **kw: None, report=None):
        """Measure every regular file under evidenced roots, once per real path.

        A fresh resolver owns this database. Symlinks are not traversed, and
        neither filenames nor historic path strings participate in identity.
        """
        report = report if report is not None else {}
        report.update(complete=False, index_size=0, files=0, roots={})
        for declared in roots:
            root = Path(declared['path'])
            if not root.is_absolute() or not declared.get('evidence'):
                raise ValueError('crop index root needs an absolute path and evidence')
            root = root.resolve()
            counts = dict(path=str(root), evidence=declared['evidence'], files=0,
                          unique_hashes=0, complete=False, errors=[])
            report['roots'][declared['name']] = counts
            if not root.is_dir():
                counts['errors'].append('missing crop root')
                continue
            def onerror(exc):
                counts['errors'].append(str(exc))
            snapshot = hashlib.sha256()
            for path in root_files(root, onerror):
                check()
                try:
                    stamp = file_stamp(path)
                    measured = self.read(path)
                    if file_stamp(path) != stamp:
                        raise OSError('crop file changed during indexing: ' + str(path))
                except OSError as exc:
                    counts['errors'].append(str(exc))
                    continue
                snapshot.update((canonical(stamp) + '\n').encode())
                self.db.execute('INSERT OR IGNORE INTO crop_root_files VALUES(?,?,?)',
                                (str(root), str(path), measured['measured_sha256']))
                counts['files'] += 1
                if counts['files'] % 10000 == 0:
                    self.db.commit()
                    progress(root=declared['name'], files=counts['files'])
            counts['unique_hashes'] = self.db.execute(
                'SELECT COUNT(DISTINCT hash) FROM crop_root_files WHERE root=?', (str(root),)).fetchone()[0]
            h = hashlib.sha256()
            for pair in self.db.execute('SELECT hash,path FROM crop_root_files WHERE root=? ORDER BY hash,path',
                                        (str(root),)):
                h.update((canonical(pair) + '\n').encode())
            counts['index'] = {'files': counts['files'], 'sha256': h.hexdigest()}
            counts['complete'] = not counts['errors']
            self.db.execute('INSERT OR REPLACE INTO crop_root_snapshots VALUES(?,?,?)',
                            (str(root), snapshot.hexdigest(), canonical(counts)))
            self.db.commit()
        report['files'], report['index_size'] = self.db.execute(
            'SELECT COUNT(DISTINCT path),COUNT(DISTINCT hash) FROM crop_root_files').fetchone()
        report['complete'] = all(c['complete'] for c in report['roots'].values())
        return report

    def by_hash(self, expected, keep_bytes=False):
        found = self.db.execute('''SELECT f.root,f.path,c.result FROM crop_root_files f
            JOIN crop_file_checks c ON c.path=f.path WHERE f.hash=? ORDER BY f.path,f.root LIMIT 1''',
            (expected,)).fetchone()
        if found:
            result = {**json.loads(found[2]), 'resolved_path': found[1],
                    'index_root': found[0], 'file_check_reused': True,
                    'via_index': True, 'file_exists': True, 'hash_match': True,
                    'original_custody': 'index',
                    'custody_established': True, 'custody_basis': 'recorded_sha256_in_declared_root_index',
                    'reason': None}
            if keep_bytes:
                binary = Path(found[1]).read_bytes()
                actual = digest(binary)
                if actual != expected:
                    raise ValueError(hash_mismatch(expected, actual, 'index', found[1],
                                                    'crop index file hash mismatch'))
                result['bytes'] = binary
            return result

    def read(self, path):
        found = self.db.execute('SELECT result FROM crop_file_checks WHERE path=?', (str(path),)).fetchone()
        if found:
            return {**json.loads(found[0]), 'file_check_reused': True}
        value = path.read_bytes()
        try:
            width, height = dimensions(value)
        except ValueError:
            # Every file is indexed by bytes; ancillary non-images have no
            # dimensions and must not prevent measuring the declared root.
            width = height = None
        result = dict(measured_sha256=digest(value), width=width, height=height)
        self.db.execute('INSERT INTO crop_file_checks VALUES(?,?)', (str(path), canonical(result)))
        return {**result, 'file_check_reused': False}


def reuse_file_index(checks, roots, cache):
    """Trust only a freeze-pinned sidecar with matching roots and stat snapshots."""
    verify_file(cache)
    if cache.get('version') != 1:
        raise ValueError('unsupported frozen crop index version')
    with closing(sqlite3.connect(Path(cache['path']).resolve().as_uri() + '?mode=ro', uri=True)) as frozen:
        states = {root: (snapshot, json.loads(report)) for root, snapshot, report in
                  frozen.execute('SELECT root,snapshot,report FROM crop_root_snapshots')}
    if set(states) != {str(Path(r['path']).resolve()) for r in roots}:
        raise ValueError('frozen crop index roots differ from lock')
    report = dict(complete=True, index_size=0, files=0, roots={})
    for root in roots:
        path = Path(root['path']).resolve()
        snapshot, counts = states[str(path)]
        expected = root.get('index', {})
        if counts['index']['sha256'] != expected.get('sha256') or counts['evidence'] != root['evidence']:
            raise ValueError('frozen crop root index digest/count mismatch: ' + root['name'])
        BindingPolicy({}, False).coverage('frozen crop root index digest/count mismatch: ' + root['name'],
                                         counts['index']['files'], expected.get('files'), exact=True)
        if root_snapshot(path) != snapshot:
            return None  # Changed metadata: measure bytes again and compare the frozen root digest.
        report['roots'][root['name']] = counts
    db = checks.db
    db.execute('ATTACH DATABASE ? AS frozen_crop_index',
               (str(Path(cache['path']).resolve()),))
    try:
        for table in ('crop_file_checks', 'crop_root_files', 'crop_root_snapshots'):
            db.execute(f'INSERT INTO {table} SELECT * FROM frozen_crop_index.{table}')
        db.commit()
    finally:
        db.execute('DETACH DATABASE frozen_crop_index')
    report['files'], report['index_size'] = db.execute(
        'SELECT COUNT(DISTINCT path),COUNT(DISTINCT hash) FROM crop_root_files').fetchone()
    checks.index_reused = True
    return report


def build_file_index(db, roots, require_pins=True, cache=None):
    """Reuse the pinned freeze index when unchanged; old locks rebuild from bytes."""
    checks = FileChecks(db)
    db.execute('DELETE FROM crop_root_files')
    db.execute('DELETE FROM crop_file_checks')
    db.execute('DELETE FROM crop_root_snapshots')
    report = reuse_file_index(checks, roots, cache) if cache and require_pins else None
    if report is None:
        report = checks.build(roots)
    if not report['complete']:
        raise ValueError('incomplete crop root index: ' + canonical(report))
    for root in roots:
        measured = report['roots'][root['name']]['index']
        if require_pins:
            expected = root.get('index', {})
            if expected.get('sha256') != measured['sha256']:
                raise ValueError('crop root index digest/count mismatch: ' + root['name'])
            BindingPolicy({}, False).coverage('crop root index digest/count mismatch: ' + root['name'],
                                             measured['files'], expected.get('files'), exact=True)
    return checks, report


def custody_kind(custody):
    if not custody.get('hash_match'):
        return None
    return custody.get('original_custody') or ('embedded_original' if custody.get('embedded_original') else
        'recorded_path' if custody.get('recorded_path') else 'index' if custody.get('via_index') else None)


def verify(original, source, keep_bytes=False, file_checks=None):
    row = crop_metadata(original, source)
    expected = get(original, source.get('fields', {}).get('crop_sha256', 'crop_sha256'))
    prepared = source.get('adapter') == 'prepared'
    expected = expected or get(original, 'binding.crop_sha256') or (None if prepared else row.get('image_sha256'))
    result = {'recorded_sha256': expected, 'recorded_path': None,
              'population': population(source), 'file_exists': False,
              'hash_match': False, 'reason': 'no_recorded_path'}
    value = get(original, source.get('fields', {}).get('image', 'image'))
    if value is None:
        value = original.get('image_png', original.get('image_bytes'))
    if source.get('adapter') in ('prepared', 'keyset'):
        value = None
    path = None
    if isinstance(value, dict):
        path, value = value.get('path'), value.get('bytes')
    for field in ('crop_path', 'crop_relative_path', 'file_name', 'image_path'):
        candidate = get(original, source.get('fields', {}).get(field, field))
        if candidate is None and source.get('adapter') == 'census':
            candidate = get(original, 'binding.' + field)
        if candidate:
            path = candidate
            break
    result['recorded_locator'] = str(path) if path else None
    result['input_no_recorded_path'] = not bool(path)
    image_hash = None if prepared else get(original, source.get('fields', {}).get('image_sha256', 'image_sha256'))
    if expected and image_hash and expected != image_hash:
        return {**result, 'reason': 'hash_mismatch', 'detail': hash_mismatch(expected, image_hash,
            'recorded_hash', source.get('_locator') or source.get('_path'),
            'recorded crop/image SHA256 disagree')}
    indexed = file_checks.by_hash(expected) if file_checks is not None and expected else None
    def index_payload():
        return file_checks.by_hash(expected, keep_bytes=True) if keep_bytes else indexed
    def fallback():
        return {**result, **index_payload()} if indexed and result['reason'] != 'hash_mismatch' else result
    if source.get('defer_original_mapping'):
        return result
    embedded_only = source.get('image_storage') == 'embedded_hf_parquet'
    if embedded_only:
        # HF Image.path is descriptive; the original payload is Image.bytes.
        path = None
        if not isinstance(value, bytes):
            result['reason'] = 'no_embedded_bytes'
            return result
    binary = None
    if path:
        p = Path(path)
        if not p.is_absolute():
            root_path = source.get('image_root')
            if source.get('image_path_base') == 'source_file_directory' and source.get('_path'):
                root_path = str(Path(source['_path']).parent)
            if not root_path or not source.get('image_root_evidence'):
                result['detail'] = 'relative locator has no declared root with evidence'
                return fallback()
            if not Path(root_path).is_absolute():
                raise ValueError('original crop root must be absolute')
            root = Path(root_path).resolve()
            p = (root / p).resolve()
            if not p.is_relative_to(root):
                raise ValueError('original crop relative path escapes declared root')
            result.update(root=str(root), root_evidence=source['image_root_evidence'])
        p = p.resolve()
        result.update(recorded_path=str(path), resolved_path=str(p))
        try:
            if file_checks is not None and not keep_bytes:
                result.update(file_checks.read(p))
            else:
                binary = p.read_bytes()
        except (FileNotFoundError, NotADirectoryError, IsADirectoryError, PermissionError):
            result['reason'] = 'missing_file'
            return fallback()
        result['file_exists'] = True
    elif isinstance(value, bytes):
        result['embedded_original'] = True
        binary = value
    else:
        return fallback()
    if binary is not None:
        result['measured_sha256'] = digest(binary)
        result['width'], result['height'] = dimensions(binary)
    if not expected:
        result.update(reason='no_recorded_hash', detail='row carries no recorded image hash')
        if embedded_only and source.get('hf_pin'):
            result.update(custody_established=True, hf_pin=source['hf_pin'],
                custody_basis='hf_pin_and_row_byte_sha256', recorded_hash_absent=True)
        return result
    if result['measured_sha256'] != expected:
        result['reason'] = 'hash_mismatch'
        result['detail'] = hash_mismatch(expected, result['measured_sha256'],
            'embedded_original' if result.get('embedded_original') else 'recorded_path',
            result.get('resolved_path') or source.get('_locator') or source.get('_path'))
        if indexed:
            return {**result, **index_payload(), 'recorded_path_mismatch': True,
                    'recorded_path_measured_sha256': result['measured_sha256']}
        return result
    result.update(hash_match=True, custody_established=True, reason=None,
                  custody_basis='recorded_sha256',
                  original_custody='embedded_original' if result.get('embedded_original') else 'recorded_path')
    if indexed:
        result['via_index'] = True
        result['index_root'] = indexed['index_root']
    if source.get('hf_pin'):
        result['hf_pin'] = source['hf_pin']
    if keep_bytes:
        result['bytes'] = binary
    return result


def new_counts():
    return dict(rows=0, recorded_path=0, recorded_locator=0, files_exist=0,
        hashes_match=0, mapped_rows=0, embedded_original=0, recorded_hash=0,
        custody_established=0, hf_pin_byte_sha256=0, reused_verification=0,
        custody_via_index=0, no_recorded_path_rows=0, no_recorded_path_via_index=0,
        previous_no_recorded_path=0, previous_no_recorded_path_resolved_via_index=0,
        recorded_path_mismatch=0, smoke_unloaded_target=0,
        reasons={r: 0 for r in REASONS})


def count_result(counts, result):
    counts['rows'] += 1
    for dest, field in (('recorded_path', 'recorded_path'), ('recorded_locator', 'recorded_locator'),
            ('files_exist', 'file_exists'), ('hashes_match', 'hash_match'),
            ('embedded_original', 'embedded_original'), ('recorded_hash', 'recorded_sha256'),
            ('custody_established', 'custody_established')):
        counts[dest] += bool(result.get(field))
    counts['mapped_rows'] += 'mapping' in result
    counts['hf_pin_byte_sha256'] += result.get('custody_basis') == 'hf_pin_and_row_byte_sha256'
    counts['reused_verification'] += bool(result.get('mapping') or result.get('file_check_reused'))
    counts['custody_via_index'] += bool(result.get('via_index'))
    counts['recorded_path_mismatch'] += bool(result.get('recorded_path_mismatch'))
    counts['no_recorded_path_rows'] += bool(result.get('input_no_recorded_path'))
    counts['no_recorded_path_via_index'] += bool(result.get('via_index') and result.get('input_no_recorded_path'))
    if not result['hash_match']:
        if result['reason'] == 'smoke_unloaded_target':
            counts['smoke_unloaded_target'] += 1
        else:
            counts['reasons'][result['reason']] += 1


class CropIndex:
    """Disk-backed exact keys and measured hash identities, shared with builds."""
    def __init__(self, db, file_checks=None):
        self.db = db
        self.file_checks = file_checks
        db.executescript('''CREATE TABLE IF NOT EXISTS original_crop_observations(
            source TEXT, locator TEXT, population TEXT, keys_json TEXT, result_json TEXT,
            anchor INTEGER, PRIMARY KEY(source,locator)) WITHOUT ROWID;
            CREATE TABLE IF NOT EXISTS original_crop_keys(
            identity TEXT, source TEXT, locator TEXT, PRIMARY KEY(identity,source,locator)) WITHOUT ROWID;
            CREATE TABLE IF NOT EXISTS original_crop_hashes(
            hash TEXT, source TEXT, locator TEXT, PRIMARY KEY(hash,source,locator)) WITHOUT ROWID;
            CREATE TABLE IF NOT EXISTS original_crop_unloaded(
            source TEXT, locator TEXT, population TEXT, keys_json TEXT, result_json TEXT,
            anchor INTEGER, PRIMARY KEY(source,locator)) WITHOUT ROWID;''')

    def load_smoke_targets(self, lock, smoke):
        """Witness exact omitted partners using pinned metadata, never their bytes.

        Keep only keys/hashes needed by unresolved selected observations. Census
        is visited before anchors so an omitted census tuple can expose the
        next S1/v4 key. These records never enter selected/population counts.
        """
        if not smoke:
            return
        from .original_inputs import selected_records
        wanted, hashes, selected = set(), set(), set()
        needs_census = False
        for source, loc, _, keys, raw, _ in self.db.execute('SELECT * FROM original_crop_observations'):
            selected.add((source, loc))
            keys, raw = json.loads(keys), json.loads(raw)
            result = self.resolve(keys, raw)
            if result.get('hash_match') or result.get('reason') == 'hash_mismatch':
                continue
            wanted.update(keys)
            needs_census |= result.get('population') in ('seal04', 'validation')
            if result.get('population') == 'census' and result.get('recorded_sha256'):
                hashes.add(result['recorded_sha256'])
        if not wanted and not hashes:
            return
        self.db.execute('''CREATE INDEX IF NOT EXISTS original_crop_unloaded_hash
            ON original_crop_unloaded(json_extract(result_json,'$.recorded_sha256'))''')
        sources = [s for s in lock['inputs'] if eligible(s) and
                   (s.get('adapter') == 's1' or population(s) in ('s1', 'v4') or
                    needs_census and population(s) == 'census')]
        for source in sorted(sources, key=lambda s: population(s) != 'census'):
            # Project parquet metadata rather than decoding embedded originals.
            scan = dict(source)
            for entry in source['files']:
                if Path(entry['path']).suffix == '.parquet':
                    import pyarrow.parquet as pq
                    names = {'parent_id', 'row_id', 'row_key', 'line_id', 'trainer_line_id',
                             'id', 'wave', 'crop_sha256', 'image_sha256', 'binding'}
                    selectors = names | {v for k, v in source.get('fields', {}).items() if k in names}
                    available = set(pq.ParquetFile(entry['path']).schema_arrow.names)
                    scan['columns'] = sorted(n for n in selectors if n.split('.')[0] in available)
                scan['files'] = [entry]
                for file, ordinal, original in selected_records(lock, scan):
                    loc = canonical({'path': file['path'], 'ordinal': ordinal, 'sha256': file['sha256']})
                    if (source['name'], loc) in selected:
                        continue
                    keys = identity(original, source)
                    row = crop_metadata(original, source)
                    expected = (get(original, source.get('fields', {}).get('crop_sha256', 'crop_sha256')) or
                                get(original, 'binding.crop_sha256') or row.get('image_sha256'))
                    if not expected or not (wanted.intersection(keys) or expected in hashes):
                        continue
                    pop = population(source)
                    target = {'source': source['name'], 'locator': loc, 'keys': keys,
                              'recorded_sha256': expected}
                    result = dict(recorded_sha256=expected, hash_match=False,
                                  population=pop, reason='smoke_unloaded_target', smoke_target=target)
                    self.db.execute('INSERT OR REPLACE INTO original_crop_unloaded VALUES(?,?,?,?,?,?)',
                        (source['name'], loc, pop, canonical(keys), canonical(result), int(pop != 'census')))
                    for key in keys:
                        self.db.execute('INSERT OR REPLACE INTO original_crop_keys VALUES(?,?,?)',
                                        (key, source['name'], loc))
                    if pop == 'census':
                        wanted.update(keys)

    def smoke_witnesses(self):
        for source, loc, _, keys, raw, _ in self.db.execute('SELECT * FROM original_crop_observations ORDER BY source,locator'):
            result = self.resolve(json.loads(keys), json.loads(raw))
            if result.get('reason') == 'smoke_unloaded_target':
                yield source, loc, result['smoke_target']

    def clear(self, source):
        for table in ('original_crop_keys', 'original_crop_hashes', 'original_crop_observations'):
            self.db.execute('DELETE FROM ' + table + ' WHERE source=?', (source,))

    def observe(self, original, source, locator, result):
        keys = identity(original, source)
        anchor = source.get('adapter') == 's1' or population(source) in ('s1', 'v4')
        self.db.execute('INSERT OR REPLACE INTO original_crop_observations VALUES(?,?,?,?,?,?)',
            (source['name'], locator, population(source), canonical(keys), canonical(result), anchor))
        for key in keys:
            self.db.execute('INSERT OR REPLACE INTO original_crop_keys VALUES(?,?,?)',
                            (key, source['name'], locator))
        if result.get('hash_match'):
            self.db.execute('INSERT OR REPLACE INTO original_crop_hashes VALUES(?,?,?)',
                            (result['measured_sha256'], source['name'], locator))

    def candidates(self, keys, census=False):
        exact = [key for key in keys if key.startswith('tuple:')]
        for key in exact or keys:
            candidates = self.db.execute('''SELECT o.keys_json,o.result_json,o.source,o.locator
                FROM original_crop_keys k JOIN (SELECT * FROM original_crop_observations
                    UNION ALL SELECT * FROM original_crop_unloaded) o
                ON o.source=k.source AND o.locator=k.locator WHERE k.identity=? AND ''' +
                ("o.population='census'" if census else 'o.anchor=1'), (key,)).fetchall()
            tuples = {k for raw, *_ in candidates for k in json.loads(raw) if k.startswith('tuple:')}
            if len(tuples) == 1:
                yield key, candidates

    def mapped_result(self, keys, result, census=False, use_index=True):
        for key, candidates in self.candidates(keys, census):
            values = []
            for raw_keys, raw, source, loc in candidates:
                candidate = json.loads(raw)
                if census:
                    candidate = self.resolve(json.loads(raw_keys), candidate, census=False, use_index=use_index)
                values.append((candidate, source, loc))
            hashes = {r.get('recorded_sha256') for r, _, _ in values}
            if len(hashes) != 1 or None in hashes:
                continue
            expected = result.get('recorded_sha256') or result.get('measured_sha256')
            if expected and expected not in hashes:
                return {**result, 'reason': 'hash_mismatch', 'detail': hash_mismatch(expected,
                    next(iter(hashes)), custody_kind(candidate), loc, 'exact mapping recorded hashes disagree')}
            verified = [(r, s, loc) for r, s, loc in values if r.get('hash_match')]
            if verified:
                r, source, loc = sorted(verified, key=lambda v: (v[1], v[2]))[0]
                return {**r, 'input_no_recorded_path': result.get('input_no_recorded_path'),
                        'mapping': {'identity': key, 'source': source, 'locator': loc,
                        'via': r.get('mapping'), 'hash_rechecked': r['measured_sha256'] == r['recorded_sha256']}}
            unloaded = [(r, s, loc) for r, s, loc in values if r.get('reason') == 'smoke_unloaded_target']
            if unloaded:
                r, source, loc = sorted(unloaded, key=lambda v: (v[1], v[2]))[0]
                return {**result, 'reason': 'smoke_unloaded_target', 'smoke_target': r['smoke_target']}
        return None

    def resolve(self, keys, result, census=None, use_index=True):
        if result.get('hash_match') or result.get('embedded_original') or result.get('reason') == 'hash_mismatch':
            return result
        if result.get('reason') == 'smoke_unloaded_target':
            return result
        if use_index and self.file_checks is not None and result.get('recorded_sha256'):
            indexed = self.file_checks.by_hash(result['recorded_sha256'])
            if indexed:
                return {**result, **indexed}
        pop = result.get('population')
        if census is None and pop in ('seal04', 'validation'):
            # S4h requires census membership first, even if an S1 ID also exists.
            return self.mapped_result(keys, result, census=True, use_index=use_index) or result
        resolved = self.mapped_result(keys, result, use_index=use_index)
        if resolved:
            return resolved
        if pop == 'census' and result.get('recorded_sha256'):
            # Reuse verified bytes by crop hash. This does not invent a row FK.
            found = self.db.execute('''SELECT o.result_json,o.source,o.locator FROM original_crop_hashes h
                JOIN original_crop_observations o ON o.source=h.source AND o.locator=h.locator
                WHERE h.hash=? AND o.anchor=1 ORDER BY o.source,o.locator LIMIT 1''',
                (result['recorded_sha256'],)).fetchone()
            if found:
                r, source, loc = json.loads(found[0]), found[1], found[2]
                if r['measured_sha256'] == result['recorded_sha256']:
                    return {**r, 'input_no_recorded_path': result.get('input_no_recorded_path'),
                        'mapping': {'identity': 'crop_sha256:' + result['recorded_sha256'],
                        'source': source, 'locator': loc, 'hash_rechecked': True}}
            unloaded = self.db.execute('''SELECT result_json FROM original_crop_unloaded
                WHERE anchor=1 AND json_extract(result_json,'$.recorded_sha256')=?
                ORDER BY source,locator LIMIT 1''', (result['recorded_sha256'],)).fetchone()
            if unloaded:
                return {**result, 'reason': 'smoke_unloaded_target',
                        'smoke_target': json.loads(unloaded[0])['smoke_target']}
        return result

    def coverage(self, check=lambda: None, progress=lambda **kw: None, populations=None):
        populations = {} if populations is None else populations
        for source, loc, pop, keys, raw, _ in self.db.execute('SELECT * FROM original_crop_observations ORDER BY source,locator'):
            check()
            keys, raw = json.loads(keys), json.loads(raw)
            result = self.resolve(keys, raw)
            c = populations.setdefault(pop, new_counts())
            count_result(c, result)
            if pop == 'census':
                previous = self.resolve(keys, raw, use_index=False)
                if previous.get('reason') == 'no_recorded_path' and not previous.get('custody_established'):
                    c['previous_no_recorded_path'] += 1
                    c['previous_no_recorded_path_resolved_via_index'] += bool(result.get('via_index'))
            if c['rows'] % 10000 == 0:
                progress(population=pop, **{k: v for k, v in c.items() if k != 'reasons'})
        return populations

    def published_counts(self, image_hash, smoke=False, populations=(), allow_unselected=()):
        """Count images in source-observation units, using exact tuples/ID joins.

        Equal hashes never identify rows. Populations overlap, so a public row
        may contribute to multiple population counts, exactly as in S4r.
        image_hash returns None for an absent public row, or (hash_or_null,).
        """
        counts = {}
        for source, pop, keys, raw in self.db.execute(
                'SELECT source,population,keys_json,result_json FROM original_crop_observations ORDER BY source,locator'):
            if pop not in populations:
                continue
            keys = json.loads(keys)
            result = self.resolve(keys, json.loads(raw))
            tuples = {k[6:] for k in keys if k.startswith('tuple:')}
            if not tuples:
                for census in ((True, False) if pop in ('seal04', 'validation') else (False,)):
                    for _, candidates in self.candidates(keys, census=census):
                        tuples.update(k[6:] for raw_keys, *_ in candidates
                                      for k in json.loads(raw_keys) if k.startswith('tuple:'))
                    if tuples:
                        break
            public = image_hash(next(iter(tuples))) if len(tuples) == 1 else None
            c = counts.setdefault(pop, dict(rows=0, images=0, null=0, unselected=0))
            c['rows'] += 1
            if public is None:
                if not smoke or source not in allow_unselected:
                    raise ValueError('original population has no unique published row: ' + pop + ':' + canonical(keys))
                c['unselected'] += 1
                continue
            expected = result.get('recorded_sha256') if result.get('hash_match') else None
            if public[0] != expected:
                raise ValueError('published original population image hash/count differs: ' + pop + ':' + canonical(keys))
            c['images' if public[0] else 'null'] += 1
            if result.get('reason') == 'smoke_unloaded_target':
                c['smoke_unloaded_target'] = c.get('smoke_unloaded_target', 0) + 1
        return counts

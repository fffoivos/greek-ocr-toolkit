"""Pinned original payload inputs and bounded source selection, without row inference."""
import json
import sqlite3

from .common import canonical, get, mapped, records, verify_file
from .original_crops import custody_kind, hash_mismatch, identity, verify


def selected_records(lock, source, smoke=None, verify_entry=verify_file):
    """Replay the builder's source prefix and identity-bucket selection."""
    books = set()
    for file_index, entry in enumerate(source['files']):
        if smoke and not lock.get('_measure') and file_index and (source['adapter'] in ('prepared', 'synthetic') or
                                    source.get('table') == 'page_images'):
            continue
        verify_entry(entry)
        for ordinal, original in enumerate(records(entry['path'], source)):
            if smoke and not source.get('book_bridge_metadata') and not source.get('validation_original_metadata') and (
                    ordinal >= smoke * lock.get('smoke_rows_per_source', 512)):
                break
            row = mapped(original, source)
            if smoke and source['adapter'] in ('row', 's1', 'harvest', 'census'):
                book = row.get('book_id') or row.get('edition_id') or row.get('source_doc_id')
                if book is None:
                    book = row.get('row_id') or row.get('id') or get(row, 'binding.id')
                if book not in books and len(books) >= smoke:
                    continue
                books.add(book)
            yield entry, ordinal, original


def tuple_identity(original, source):
    keys = [k for k in identity(original, source) if k.startswith('tuple:')]
    if len(keys) != 1:
        raise ValueError('original payload requires an exact original tuple: ' + source['name'])
    return keys[0]


class OriginalPayloads:
    def __init__(self, db, file_checks, policy=None):
        self.db, self.file_checks = db, file_checks
        self.policy = policy
        db.execute('''CREATE TABLE IF NOT EXISTS original_payload_inputs(
            source TEXT, identity TEXT, result TEXT, PRIMARY KEY(source,identity)) WITHOUT ROWID''')

    def load(self, lock, source, smoke=None, sink=lambda result, binary: None, check=lambda: None, verify_entry=verify_file):
        from .cursors import positioned_records
        from .progress import Progress
        override = source.get('original_crops_source')
        if not override:
            return
        self.db.execute('CREATE TABLE IF NOT EXISTS original_payload_cursor(source TEXT,path TEXT,ordinal INTEGER,position INTEGER,done INTEGER,PRIMARY KEY(source,path))')
        payload_source = {**source, **override}
        wanted = ({tuple_identity(row, source) for _, _, row in selected_records(lock, source, smoke, verify_entry=verify_entry)}
                  if smoke else None)
        found = {key for key, in self.db.execute('SELECT identity FROM original_payload_inputs WHERE source=?', (source['name'],))} if wanted is not None else set()
        scanned = 0
        for entry in override['files']:
            with Progress('hash:original:' + source['name'], entry['bytes']) as progress:
                verify_entry(entry)
                progress.bytes = entry['bytes']
            saved = self.db.execute('SELECT ordinal,position,done FROM original_payload_cursor WHERE source=? AND path=?', (source['name'], entry['path'])).fetchone()
            ordinal, position = (saved[0], saved[1]) if saved else (0, 0)
            if saved and saved[2]:
                scanned += ordinal
                continue
            if wanted is not None and found >= wanted:
                break
            with Progress('original:' + source['name'], entry['bytes']) as progress:
                count = ordinal
                try:
                    for ordinal, original, position in positioned_records(entry['path'], payload_source, ordinal, position):
                        count = ordinal + 1
                        key = tuple_identity(original, payload_source)
                        if wanted is None or key in wanted:
                            locator = canonical({'path': entry['path'], 'ordinal': ordinal, 'sha256': entry['sha256']})
                            result = verify(original, {**payload_source, '_locator': locator},
                                            keep_bytes=True, file_checks=self.file_checks)
                            binary = result.pop('bytes', None)
                            if not result['hash_match'] or binary is None:
                                raise ValueError('original payload input lacks recorded-hash custody: ' + key +
                                                 '; ' + result.get('detail', str(result['reason'])))
                            result['payload_input'] = {'path': entry['path'], 'sha256': entry['sha256'], 'ordinal': ordinal,
                                                       'identity': key}
                            try:
                                self.db.execute('INSERT INTO original_payload_inputs VALUES(?,?,?)',
                                                (source['name'], key, canonical(result)))
                            except sqlite3.IntegrityError as exc:
                                raise ValueError('duplicate original payload tuple: ' + key) from exc
                            sink(result, binary)
                            if wanted is not None:
                                found.add(key)
                        progress.rows, progress.bytes = count, position
                        if count % 50000 == 0:
                            self.db.execute('INSERT OR REPLACE INTO original_payload_cursor VALUES(?,?,?,?,0)',
                                (source['name'], entry['path'], count, position))
                            self.db.commit()
                            check()
                        if wanted is not None and found >= wanted:
                            break
                    self.db.execute('INSERT OR REPLACE INTO original_payload_cursor VALUES(?,?,?,?,1)',
                        (source['name'], entry['path'], count, position))
                    self.db.commit()
                    check()
                except BaseException:
                    self.db.rollback()
                    raise
                scanned += count
            if wanted is not None and found >= wanted:
                break
        if wanted is not None and not found >= wanted:
            raise ValueError('selected native harvest tuple missing from original payload input')
        from .accept_bindings import BindingPolicy
        policy = self.policy if self.policy is not None else BindingPolicy(lock, smoke)
        policy.coverage('original payload input row count.' + source['name'], scanned,
                        override['expected_rows'], comparable=False)

    def verify(self, original, source, keep_bytes=False):
        if not source.get('original_crops_source'):
            return verify(original, source, keep_bytes=keep_bytes, file_checks=self.file_checks)
        key = tuple_identity(original, source)
        found = self.db.execute('SELECT result FROM original_payload_inputs WHERE source=? AND identity=?',
                                (source['name'], key)).fetchone()
        if not found:
            raise ValueError('native tuple missing from pinned original payload input: ' + key)
        result = json.loads(found[0])
        # Reconciliation uses the native recorded hash, never a filename or
        # positional zip of metadata and parquet rows.
        expected = get(original, source.get('fields', {}).get('crop_sha256', 'crop_sha256'))
        image_hash = get(original, source.get('fields', {}).get('image_sha256', 'image_sha256'))
        expected = expected or get(original, 'binding.crop_sha256') or image_hash
        if expected and image_hash and expected != image_hash:
            raise ValueError(hash_mismatch(expected, image_hash, 'recorded_hash',
                source.get('_locator') or source.get('_path'), 'native crop/image recorded hash mismatch: ' + key))
        if expected != result['recorded_sha256']:
            raise ValueError(hash_mismatch(expected, result['measured_sha256'], custody_kind(result),
                canonical(result['payload_input']), 'native/original payload recorded hash mismatch: ' + key))
        return result

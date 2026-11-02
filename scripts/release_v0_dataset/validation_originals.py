"""Exact validation line_id -> admitted id evidence; no locator reconstruction."""
import json

from .common import canonical

FIELDS = ('crop_sha256', 'crop_path', 'source_url', 'attribution', 'year',
          'page_id', 'bbox', 'crop_width', 'crop_height', 'book_key')


class ValidationOriginals:
    def __init__(self, db):
        self.db = db
        db.execute('''CREATE TABLE IF NOT EXISTS validation_originals(
            id TEXT, source TEXT, locator TEXT, record TEXT,
            PRIMARY KEY(id,source,locator)) WITHOUT ROWID''')

    def clear(self, source):
        self.db.execute('DELETE FROM validation_originals WHERE source=?', (source,))

    def observe(self, row, source, locator, sha256):
        if row.get('id') is None:
            raise ValueError('validation original metadata lacks exact id')
        record = {k: row[k] for k in FIELDS if row.get(k) is not None}
        record['provenance'] = dict(input=source, locator=locator, input_sha256=sha256,
            join='prepared_validation.line_id = admitted_all_v2.id (exact)',
            selectors={k: k for k in record})
        self.db.execute('INSERT OR REPLACE INTO validation_originals VALUES(?,?,?,?)',
                        (canonical(row['id']), source, locator, canonical(record)))

    def enrich(self, row):
        found = self.db.execute('SELECT record FROM validation_originals WHERE id=?',
                               (canonical(row.get('line_id')),)).fetchall()
        if len(found) != 1:
            return {**row, 'validation_original_join': 'ambiguous' if found else 'unmatched'}
        record = json.loads(found[0][0])
        provenance = {**record.pop('provenance'), 'id': row['line_id']}
        result = dict(row)
        filled = []
        for field, value in record.items():
            if result.get(field) is None:
                result[field] = value
                filled.append(field)
        result.update(validation_original_join='exact', validation_original_provenance={
            **provenance, 'filled_fields': filled, 'recorded_fields': record})
        if result.get('crop_bbox') is None and result.get('bbox') is not None:
            result['crop_bbox'] = result['bbox']
        return result

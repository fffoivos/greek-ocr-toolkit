"""Conservative catalogue joins and page-space source metadata."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
import re
from typing import Any

from greekocr.annotate.line_features import _mapping
from greekocr.types import Record

__all__ = ['source_metadata']

DOC_TYPES = frozenset({'proceedings', 'gazette', 'book', 'newspaper', 'web', 'born_digital_article'})


def _catalogue_entry(record: Mapping[str, Any], catalogue: Any) -> dict[str, Any]:
    if catalogue is None:
        return {}
    identities = [record.get(k) for k in ('source_doc_id', 'document_id', 'identifier', 'id')]
    identities = [str(value) for value in identities if value is not None]
    source = record.get('source_dataset', record.get('source'))
    if isinstance(catalogue, Mapping):
        if 'documents' in catalogue:
            return _catalogue_entry(record, catalogue['documents'])
        if 'records' in catalogue:
            return _catalogue_entry(record, catalogue['records'])
        for identity in identities:
            scoped = catalogue.get(f'{source}:{identity}')
            entry = scoped if scoped is not None else catalogue.get(identity)
            if isinstance(entry, Mapping) and (source is None or entry.get('source_dataset', entry.get('source', source)) == source):
                return dict(entry)
        # Also allow a single identified catalogue record.
        if (any(str(catalogue.get(k)) in identities for k in ('source_doc_id', 'document_id', 'identifier', 'id'))
                and (source is None or catalogue.get('source_dataset', catalogue.get('source', source)) == source)):
            return dict(catalogue)
        return {}
    if isinstance(catalogue, Sequence) and not isinstance(catalogue, (str, bytes)):
        matches = [entry for entry in catalogue if isinstance(entry, Mapping)
                   and any(str(entry.get(k)) in identities for k in ('source_doc_id', 'document_id', 'identifier', 'id'))
                   and (source is None or entry.get('source_dataset', entry.get('source', source)) == source)]
        if len(matches) > 1:
            raise ValueError('ambiguous catalogue identity; use source-qualified keys')
        return dict(matches[0]) if matches else {}
    raise TypeError('catalogue must be an identity mapping or a list of records')


def _values(value: Any) -> list[Any]:
    if isinstance(value, Mapping):
        return _values(value.get('value'))
    if isinstance(value, (list, tuple)):
        return [v for item in value for v in _values(item)]
    return [] if value is None else [value]


def _year(value: Any) -> int | None:
    years = set()
    for item in _values(value):
        if isinstance(item, bool):
            continue
        found = re.findall(r'(?<!\d)([12]\d{3})(?!\d)', str(item))
        years.update(int(y) for y in found)
    # Ranges and conflicting catalogue dates stay unresolved.
    return next(iter(years)) if len(years) == 1 else None


def _first(*values: Any) -> Any:
    return next((v for v in values if v is not None and v != '' and v != []), None)


def _position(record: Mapping[str, Any]) -> str | None:
    geometry = _mapping(record.get('geometry'))
    box = _first(record.get('bbox_pixel'), geometry.get('source_box'), record.get('source_box'))
    if box is None or not isinstance(box, (list, tuple)) or len(box) != 4:
        return None
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in box):
        return None
    if box[0] < 0 or box[1] < 0 or box[2] <= box[0] or box[3] <= box[1]:
        return None
    height = _first(record.get('page_height_px'), geometry.get('page_height_px'))
    size = _first(record.get('page_size_px'), geometry.get('page_size_px'))
    if height is None and isinstance(size, (list, tuple)) and len(size) == 2:
        height = size[1]
    if not isinstance(height, (int, float)) or isinstance(height, bool) or not math.isfinite(height) or height <= 0 or box[3] > height:
        return None
    center = (box[1] + box[3]) / 2 / height
    if center < .1:
        return 'header'
    if center > .9:
        return 'footer'
    column = _first(record.get('column_index'), geometry.get('column_index'))
    if isinstance(column, int) and not isinstance(column, bool) and column >= 0:
        return f'column_{column}'
    return 'body'


def source_metadata(record: Mapping[str, Any], catalogue: Any = None) -> Record:
    """Join by document identity; preserve unknown rights and distinguish fetch from publication years."""
    entry = _catalogue_entry(record, catalogue)
    source = _first(record.get('source_dataset'), record.get('source'), entry.get('source_dataset'), entry.get('source'))
    kind = str(source or '').casefold()
    metadata = _mapping(entry.get('metadata'))
    local = _mapping(record.get('metadata'))
    year = basis = None
    fields = ('year', 'parliament_year', 'anemi_year', 'publication_year', 'date',
              'dcterms.created.from', 'dc.date.issued', 'publication_date_displayed', 'Date of publication')
    for prefix, values in [('catalogue', entry), ('catalogue.metadata', metadata), ('record', record), ('record.metadata', local)]:
        for field in fields:
            if field in values:
                parsed = _year(values[field])
                if parsed is not None:
                    year, basis = parsed, f'{prefix}.{field}'
                    break
        if year is not None:
            break
    doc_type = _first(record.get('doc_type'), entry.get('doc_type'), metadata.get('doc_type'))
    if doc_type is not None and doc_type not in DOC_TYPES:
        doc_type = None
    if doc_type is None:
        if any(word in kind for word in ('gazette', 'fek', 'εφημερίδα κυβερνήσεως')):
            doc_type = 'gazette'
        elif any(word in kind for word in ('parliament', 'vouli')):
            doc_type = 'proceedings'
        elif any(word in kind for word in ('newspaper', 'news-')):
            doc_type = 'newspaper'
        elif kind in ('ia', 'archive', 'internet_archive', 'anemi', 'gutenberg'):
            doc_type = 'book'
        elif kind in ('web', 'gov', 'eur-lex', 'wikisource', 'mastodon') or kind.startswith('wikipedia'):
            doc_type = 'web'
    if record.get('born_digital') is True or entry.get('born_digital') is True:
        if doc_type in (None, 'web'):
            doc_type = 'born_digital_article'
    if year is None and doc_type in ('web', 'born_digital_article'):
        fetched = _first(entry.get('fetched_at'), record.get('fetched_at'))
        year = _year(fetched)
        basis = 'fetched_at' if year is not None else None
    return dict(year=year, year_basis=basis,
                collection=_first(record.get('collection'), entry.get('collection'), metadata.get('collection'), metadata.get('lpgr.Collection')),
                doc_type=doc_type,
                licence=_first(record.get('licence'), record.get('license'), entry.get('licence'), entry.get('license'), metadata.get('licenseurl')),
                licence_tier=_first(record.get('licence_tier'), entry.get('licence_tier')),
                tier=_first(record.get('label_tier'), record.get('tier'), entry.get('label_tier'), entry.get('tier')),
                page_position=_position(record))

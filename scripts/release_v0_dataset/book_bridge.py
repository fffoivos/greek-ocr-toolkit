"""Typed v2 book identity and exact original-line instruments, shared by probe/build.

No file discovery, URL templates, image access, title matching or fuzzy matching.
The prefix and URL normalizations below reproduce build_book_registry.py:48-49,
76-84, 101-106, 115-125. Hashes are compared literally to recorded aliases;
we do not manufacture a hash namespace or hash an undocumented field.
"""
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from .common import SOURCE_FIELDS, canonical, get, digest

BRIDGE_FIELDS = tuple(dict.fromkeys(['book_id', 'canonical_book_id'] + SOURCE_FIELDS))
POPULATIONS = ('s1', 'v4', 'old', 'census', 'harvest', 'seal04', 'validation', 'synthetic')
FIELD_NAMESPACES = {
    'edition_id': ('edition_id', 'seal04_edition_hash', 'line_id_prefix'),
    'book_id': ('v2_book_id', 'edition_id', 'line_id_prefix'),
    'canonical_book_id': ('v2_book_id', 'edition_id', 'line_id_prefix'),
    'source_doc_id': ('v2_book_id', 'edition_id', 'line_id_prefix'),
    'doc': ('v2_book_id', 'edition_id', 'line_id_prefix'),
    'book_key': ('line_id_prefix',),
    'pdf_sha256': ('pdf_sha256',), 'full_pdf_sha256': ('pdf_sha256',),
    'ia_identifier': ('ia_identifier',), 'nlg_catalogue': ('nlg_catalogue',),
}
LINE_FIELDS = {
    's1': ('row_id',), 'census': ('binding.id', 'row_id'),
    'v4': ('row_id',), 'old': ('line_id',),
    'harvest': ('row_id', 'id'), 'seal04': ('id', 'row_id'),
    # S4h established exact validation.line_id = census.binding.id, no parsing.
    'validation': ('line_id',), 'synthetic': ('original_line_id',),
}

ADOPTION_BUNDLE = Path(__file__).with_name('specs') / 'book-registry-adoption-v2.json'


def adopted_registry(lock, bundle=None):
    """Resolve the byte-preserved v2 proposal through already locked authority.

    The adoption names the gzip JSONL hash, not the parquet hash. Both original
    documents are carried verbatim so their lock hashes and that connection can
    be checked offline. No registry fields or historical memberships are edited.
    An unbound, changed or unrelated adoption supplies no exception.
    """
    bundle = json.loads(ADOPTION_BUNDLE.read_text()) if bundle is None else bundle
    evidence = {e['path']: e['sha256'] for e in lock.get('evidence_files', [])}
    for name in ('ADOPTED_SPLIT.json', 'SHA256SUMS'):
        document = bundle[name]
        if evidence.get(document['path']) != digest(document['text']):
            return None
    adoption = json.loads(bundle['ADOPTED_SPLIT.json']['text'])
    checksums = dict((name.lstrip('*'), value) for value, name in
                     (line.split(maxsplit=1) for line in bundle['SHA256SUMS']['text'].splitlines() if line.strip()))
    binding = lock.get('book_bridge', {})
    sources = [s for s in lock['inputs'] if s['name'] == binding.get('registry_input') or
               (not binding and s.get('table') == 'book_registry')]
    registry_sha = checksums.get('book_registry.parquet')
    if (adoption.get('status') != 'ADOPTED' or adoption.get('adopted_registry_version') != 'v2' or
            adoption.get('adopted_book_registry_sha256') != checksums.get('book_registry.jsonl.gz') or
            checksums.get('ADOPTED_SPLIT.json') != digest(bundle['ADOPTED_SPLIT.json']['text']) or
            not registry_sha or len(sources) != 1 or len(sources[0]['files']) != 1 or
            sources[0]['files'][0]['sha256'] != registry_sha or
            (binding and binding.get('registry_sha256') != registry_sha)):
        return None
    return {'registry_sha256': registry_sha, 'split_proposal_sha256': adoption['split_proposal_sha256']}


def adopted_train_assignment(book, authority):
    """Only this adopted proposal's TRAIN assignment supersedes its stale flag."""
    return bool(authority and book.get('split') == 'train' and not book.get('conflict') and
        book.get('assignment_status') == 'proposed_not_adopted' and
        book.get('source_sha256') == authority['registry_sha256'] and
        any(a.get('scope') == 'book' and a.get('split') == 'train' and not a.get('superseded_by') and
            any(p.get('sha256') == authority['split_proposal_sha256'] for p in a.get('provenance', []))
            for a in book.get('assignments', [])))


def prefix(value):
    return re.sub(r'(?:--s\d+|--p\d+|--n\d+|-p\d+).*$', '', str(value))


def source_url(value):
    if not isinstance(value, str):
        return None
    if value.startswith('/metadata/'):
        value = 'https://anemi.lib.uoc.gr' + value  # registry builder:78-79
    if not value.startswith(('http://', 'https://')):
        return value
    u = urlsplit(value)
    return u.netloc.lower() + unquote(u.path).rstrip('/') + ('?' + u.query if u.query else '')


def original_ids(row, population):
    # Each adapter declares its original-ID selector. Factory IDs have no rule
    # here except validation's previously measured exact census mapping.
    if row.get('original_line_id'):
        return [str(row['original_line_id'])]
    for field in LINE_FIELDS.get(population, ('row_id',)):
        value = get(row, field)
        if isinstance(value, (str, int)) and str(value):
            return [str(value)]
    return []


def metadata(row, population):
    """Retain only book/source evidence, never labels, raster payloads or paths."""
    fields = set(FIELD_NAMESPACES) | set(SOURCE_FIELDS) | {
        'title', 'provider_item_id', 'original_line_id', 'source_dataset',
        'attribution', 'validation_original_provenance'}
    result = {k: row[k] for k in fields if row.get(k) is not None}
    for field in LINE_FIELDS[population]:
        value = get(row, field)
        if value is not None:
            if field == 'binding.id':
                result['binding'] = {'id': value}
            else:
                result[field] = value
    provenance = row.get('provenance') or row.get('source_record_json') or {}
    if isinstance(provenance, str):
        try:
            provenance = json.loads(provenance)
        except ValueError:
            provenance = {}
    if isinstance(provenance, dict):
        links = provenance.get('public_links', {})
        if isinstance(links, dict):
            for field in ('catalogue_url', 'manifest_url', 'source_url'):
                if links.get(field) is not None:
                    result.setdefault(field, links[field])
    return result


class BookBridge:
    def __init__(self, books=(), instruments=(), sources=(), registry_sha256=None,
                 instruments_sha256=None):
        self.books, self.aliases = {}, defaultdict(set)
        self.instruments, self.sources = defaultdict(list), defaultdict(list)
        self._bibliography = {}
        self.registry_sha256 = registry_sha256
        self.instruments_sha256 = instruments_sha256
        for book in books:
            self.books[book['book_id']] = book
            for alias in book.get('aliases') or []:
                self.aliases[alias['namespace'], str(alias['value'])].add(book['book_id'])
        for instrument in instruments:
            self.instruments[str(instrument['row_id'])].append(instrument)
        for source in sources:
            # Portable sourcing records are valid only for their pinned registry.
            if source.get('registry_sha256') != registry_sha256:
                raise ValueError('book sourcing record registry SHA mismatch')
            if source['book_id'] not in self.books:
                raise ValueError('book sourcing record absent from registry')
            self.sources[source['book_id']].append(source)

    def keys(self, row, population):
        keys = set()
        def add(field, namespace, value):
            if isinstance(value, (str, int)) and str(value):
                keys.add((field, namespace, str(value)))
        for field, namespaces in FIELD_NAMESPACES.items():
            for ns in namespaces:
                add(field, ns, row.get(field))
        for lid in original_ids(row, population):
            # Exact equality to a declared book alias, never startswith().
            add('original_line_id -> registry.prefix', 'line_id_prefix', prefix(lid))
        for field in ('source_url', 'manifest_url'):
            if row.get(field):
                add(field + ' -> registry.url', 'source_url', source_url(row[field]))
        provider = row.get('provider')
        if provider:
            for field in ('item', 'provider_item_id'):
                add(field, 'provider_item:' + str(provider), row.get(field))
        return sorted(keys)

    def match(self, row, population):
        keys = self.keys(row, population)
        hits = [(field, ns, value, sorted(self.aliases[ns, value]))
                for field, ns, value in keys if (ns, value) in self.aliases]
        books = sorted({bid for _, _, _, bids in hits for bid in bids})
        status = 'match' if len(books) == 1 else 'ambiguous' if books else 'unmatched' if keys else 'no_key'
        return {'status': status, 'book_id': books[0] if status == 'match' else None,
                'candidates': books, 'matches': hits, 'typed_keys': len(keys)}

    def bibliography(self, bid):
        if bid in self._bibliography:
            return self._bibliography[bid]
        candidates = defaultdict(dict)
        def offer(field, value, origin):
            if value is not None and value != '':
                candidates[field].setdefault(canonical(value), {'value': value, 'evidence': []})['evidence'].append(origin)
        for alias in self.books[bid].get('aliases') or []:
            ns, value = alias['namespace'], alias['value']
            origin = {'registry_sha256': self.registry_sha256, 'alias': alias}
            if ns.startswith('provider_item:') and ns != 'provider_item:unknown':
                offer('provider', ns.split(':', 1)[1], origin)
                offer('item', value, origin)
            elif ns == 'catalogue_reference':
                offer('catalogue_reference', value, origin)
                if value.startswith(('https://', 'http://')):
                    offer('catalogue_url', value, origin)
            elif ns == 'source_url':
                offer('source_url', value, origin)
        source_ids = []
        for record in self.sources[bid]:
            source_id = record.get('source_record_id') or digest(canonical({
                k: v for k, v in record.items() if k not in ('source_locator', 'source_sha256')}))
            source_ids.append(source_id)
            for field, value in record.get('fields', {}).items():
                if field not in ('page', 'page_number_convention'):
                    offer(field, value, {'table': 'book_sources', 'source_record_id': source_id, 'field': field})
        # Prefer retained, fully spelled URLs to their scheme-less registry
        # aliases only when the registry's own normalization is exactly equal.
        choices = candidates.get('source_url', {})
        spelled = [c['value'] for c in choices.values() if str(c['value']).startswith(('https://', 'http://'))]
        for url in spelled:
            choices.pop(canonical(source_url(url)), None)
        values, reasons, evidence = {}, {}, {}
        for field, choices in candidates.items():
            if len(choices) == 1:
                choice = next(iter(choices.values()))
                values[field] = choice['value']
                evidence[field] = choice['evidence']
            else:
                reasons[field] = 'multiple recorded book source values; inspect book_source_candidates_json'
        record = {'book_id': bid, 'registry_sha256': self.registry_sha256,
                  'sourcing_record_ids': sorted(set(source_ids)),
                  'registry_table': 'registry/book_registry.parquet', 'sourcing_table': 'tables/book_sources.parquet'}
        self._bibliography[bid] = (values, reasons, evidence, candidates, record)
        return self._bibliography[bid]

    def resolve(self, row, population, match=None):
        row = metadata(row, population)
        match = match or self.match(row, population)
        bid = match['book_id']
        values = {f: None for f in BRIDGE_FIELDS}
        reasons, evidence, candidates, source_record = {}, {}, {}, {}
        if bid:
            base, nulls, origins, candidates, source_record = self.bibliography(bid)
            values.update(base, book_id=bid, canonical_book_id=bid)
            reasons, evidence = dict(nulls), dict(origins)
            evidence['book_id'] = {'registry_sha256': self.registry_sha256, 'typed_matches': match['matches'],
                                   'source_observations': match.get('observations')}
        # Book ambiguity nulls the book, not independently recorded row metadata.
        for field in SOURCE_FIELDS:
            if row.get(field) is not None:
                values[field] = row[field]
                evidence[field] = {'selector': field, 'scope': 'native row'}
                admitted = row.get('validation_original_provenance')
                if admitted and field in admitted.get('filled_fields', []):
                    evidence[field] = {**admitted, 'selector': field, 'scope': 'exact admitted id join'}
                reasons.pop(field, None)
        if values.get('source_title') is None and row.get('title'):
            values['source_title'] = row['title']
            evidence['source_title'] = {'selector': 'title', 'scope': 'native row'}
            reasons.pop('source_title', None)
        if bid or any(row.get(f) is not None for f in SOURCE_FIELDS) or row.get('validation_original_provenance'):
            if not bid:
                source_record = {'book_bridge_status': match['status'],
                                 'native_source_fields': {f: row[f] for f in SOURCE_FIELDS if row.get(f) is not None}}
            source_record = {**source_record, 'native_source_record_sha256': row.get('source_record_sha256')}
            if row.get('validation_original_provenance'):
                source_record['validation_original'] = row['validation_original_provenance']
            values['source_record_sha256'] = digest(canonical(source_record))
            evidence['source_record_sha256'] = {'basis': 'canonical JSON of source_record_json'}
        for field in BRIDGE_FIELDS:
            if values[field] is None:
                reasons.setdefault(field, ('book identity ' + match['status']) if not bid else
                                   'not recorded for this exact row/book in registry or hash-bound sourcing records')
        instruments = self.memberships(row, population)
        original_known = bool(original_ids(row, population))
        return {**values, 'book_registry_sha256': self.registry_sha256,
                'book_bridge_status': match['status'], 'book_bridge_candidates_json': match['candidates'],
                'book_bridge_evidence_json': evidence,
                'book_source_candidates_json': candidates,
                'source_record_json': source_record,
                'source_record_hash_basis': 'canonical JSON of source_record_json',
                'source_missing_reasons_json': {f: {'reason': r} for f, r in reasons.items()},
                'row_instruments_sha256': self.instruments_sha256,
                'row_instrument_status': 'exact_original_id' if original_known else 'original_id_unknown',
                'row_instrument_missing_reason': None if original_known else 'no explicit original line mapping',
                'lqb_row': any(i['kind'] == 'lqb' for i in instruments) if original_known else None,
                'release_excluded_row': any(i['kind'] == 'release_exclusion' for i in instruments) if original_known else None}

    def memberships(self, row, population):
        return [i for lid in original_ids(row, population) for i in self.instruments.get(lid, [])]


def new_coverage():
    return {'rows': 0, 'match': 0, 'no_key': 0, 'unmatched': 0, 'ambiguous': 0,
            'source_fields': {f: {'nonnull': 0, 'null': 0, 'null_reasons': Counter()} for f in BRIDGE_FIELDS},
            'instrument_rows': 0, 'instrument_memberships': 0, 'lqb_row': 0,
            'release_excluded_row': 0, 'instrument_original_id_unknown': 0, 'match_paths': Counter()}


def count_coverage(coverage, resolved, memberships=(), match=None):
    coverage['rows'] += 1
    coverage[resolved['book_bridge_status']] += 1
    for field, counts in coverage['source_fields'].items():
        present = resolved.get(field) is not None
        counts['nonnull' if present else 'null'] += 1
        if not present:
            counts['null_reasons'][resolved['source_missing_reasons_json'][field]['reason']] += 1
    coverage['instrument_rows'] += bool(memberships)
    coverage['instrument_memberships'] += len(memberships)
    coverage['instrument_original_id_unknown'] += resolved['row_instrument_status'] == 'original_id_unknown'
    for flag in ('lqb_row', 'release_excluded_row'):
        coverage[flag] += bool(resolved[flag])
    for field, ns, _, _ in (match or {}).get('matches', []):
        coverage['match_paths'][field + ' -> ' + ns] += 1

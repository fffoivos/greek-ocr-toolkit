"""Wave 3 pure selection and public DSpace ORIGINAL-PDF resolution.

The item -> bundles -> bitstreams traversal follows o4c_discover_parliament.py.
No credentials, OCR, or network work happens on import.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import random
import re
import unicodedata
from urllib.parse import urlencode, urlsplit

from .round1 import positions, replacement_candidates

BASE = 'https://digitallibrary.parliament.gr/records/api'
YEARS = tuple(range(1975, 2001))
SEED = 20263
MAX_PDF = 250_000_000
MONTHS = ('ΙΑΝΟΥΑΡΙ', 'ΦΕΒΡΟΥΑΡΙ', 'ΜΑΡΤΙ', 'ΑΠΡΙΛΙ', 'ΜΑΙ', 'ΙΟΥΝΙ',
          'ΙΟΥΛΙ', 'ΑΥΓΟΥΣΤ', 'ΣΕΠΤΕΜΒΡΙ', 'ΟΚΤΩΒΡΙ', 'ΝΟΕΜΒΡΙ', 'ΔΕΚΕΜΒΡΙ')


def rights_raw(row):
    value = row.get('rights', {})
    value = value.get('raw', []) if isinstance(value, dict) else value
    return [value] if isinstance(value, str) else list(value or [])


def eligible(row):
    raw = ' '.join(rights_raw(row)).upper()
    year = row.get('year')
    return (row.get('collection') == 'ΠΡΑΚΤΙΚΑ ΒΟΥΛΗΣ'
            and type(year) is int and year in YEARS
            and 'CC BY 4.0' in raw and not re.search(r'\b(?:NC|ND)\b|NONCOMMERCIAL|NODERIVATIVES', raw))


def session_date(row):
    title = ''.join(c for c in unicodedata.normalize('NFD', row['title'].upper())
                    if not unicodedata.combining(c))
    for match in re.finditer(r'(\d{1,2})\s+([Α-Ω]+)\s+(19\d{2}|2000)', title):
        day, month, year = match.groups()
        if int(year) == row['year']:
            for i, name in enumerate(MONTHS, 1):
                if month.startswith(name):
                    return i, int(day)
    return 13, 32


def candidate_slots(rows, seed=SEED):
    """Four chronological strata/year, seeded draws plus same-stratum backups.

    Empty years stay explicit; no silent reallocation to other years. Candidates
    are disjoint across slots so an oversized/short PDF cannot repeat elsewhere.
    """
    grouped = defaultdict(list)
    seen = set()
    for row in rows:
        if eligible(row):
            if row['document_id'] in seen:
                raise ValueError('duplicate catalogue UUID')
            seen.add(row['document_id'])
            grouped[row['year']].append(row)
    rng, slots = random.Random(seed), []
    for year in YEARS:
        ordered = sorted(grouped[year], key=lambda r: (session_date(r), r['title'], r['document_id']))
        for stratum in range(4):
            pool = ordered[len(ordered)*stratum//4:len(ordered)*(stratum+1)//4]
            rng.shuffle(pool)
            slots.append(dict(year=year, stratum=stratum, candidates=pool))
    return slots


def holdout(books, seed=20261015):
    """Sixteen distinct years spread over chronological bins; 12 test/4 dev.

    A year can contribute at most one book. Works with missing catalogue years
    while recording the actual available-year scope.
    """
    groups = defaultdict(list)
    for b in sorted(books, key=lambda b: b['key']):
        groups[b['year']].append(b)
    if len({b['key'] for b in books}) != len(books):
        raise ValueError('duplicate book key')
    years = sorted(groups)
    if len(years) < 16:
        raise ValueError('need sixteen represented years for stratified hold-out')
    rng, chosen = random.Random(seed), []
    for i in range(16):
        year = rng.choice(years[len(years)*i//16:len(years)*(i+1)//16])
        chosen.append(rng.choice(groups[year]))
    dev = set(rng.sample(range(16), 4))
    return sorted([dict(book_key=b['key'], uuid=b['book'], title=b['title'],
                        year=b['year'], decade=b['decade'],
                        split='dev' if i in dev else 'test')
                   for i, b in enumerate(chosen)], key=lambda b: b['book_key'])


def page_spread(total, book, seed=SEED):
    return positions(total, 12, seed=seed, book=book)


def neighbours(page, total, reserved=()):
    # Original attempt and at most two neighbouring retries, never beyond 95%.
    return replacement_candidates(page, total, reserved=reserved)


def local_url(url):
    url = url.replace('https://sylloges.parliament.gr/records/api', BASE)
    p = urlsplit(url)
    if p.scheme != 'https' or p.netloc != 'digitallibrary.parliament.gr':
        raise ValueError('DSpace URL outside authorized host')
    return url


def paginate(client, url, key):
    page = 0
    while True:
        result = client.json(url + '?' + urlencode(dict(size=100, page=page)))
        yield from result.get('_embedded', {}).get(key, [])
        page += 1
        if page >= result.get('page', {}).get('totalPages', 1):
            break


def original_pdfs(bundle, bitstreams):
    if bundle.get('name') != 'ORIGINAL':
        return []
    return [dict(uuid=f['uuid'], bundle_uuid=bundle['uuid'], name=f['name'],
                 url=local_url(f['_links']['content']['href']), size=f.get('sizeBytes'),
                 checksum=f.get('checkSum')) for f in bitstreams
            if f.get('name', '').lower().endswith('.pdf')]


def resolve_pdf(client, uuid):
    files = []
    for bundle in paginate(client, BASE + '/core/items/' + uuid + '/bundles', 'bundles'):
        if bundle.get('name') == 'ORIGINAL':
            bits = list(paginate(client, BASE + '/core/bundles/' + bundle['uuid'] + '/bitstreams', 'bitstreams'))
            files.extend(original_pdfs(bundle, bits))
    if not files:
        raise ValueError('no ORIGINAL PDF')
    # Same largest-file rule as O4c; never select TEXT/thumbnail or DjVu.
    return sorted(files, key=lambda f: (-(f['size'] or 0), f['uuid']))[0]


def parse_item(item):
    metadata = item.get('metadata', {})
    def vals(k):
        return [x['value'] for x in metadata.get(k, [])]
    date = (vals('dcterms.created.from') or vals('dc.date.issued') or [''])[0]
    found = re.search(r'\b(19\d{2}|2000)\b', date)
    return dict(document_id=item['uuid'], title=(vals('dc.title') or [item.get('name', '')])[0],
                record_url=(vals('dc.identifier.uri') or [''])[0],
                year=int(found[0]) if found else None,
                rights={'raw': vals('dc.rights') + vals('dc.rights.uri')},
                collection=(vals('lpgr.Collection') or [None])[0],
                metadata_url=BASE + '/core/items/' + item['uuid'])

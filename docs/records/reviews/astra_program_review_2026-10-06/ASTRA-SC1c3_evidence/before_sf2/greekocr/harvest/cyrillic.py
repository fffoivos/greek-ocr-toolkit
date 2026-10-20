"""T26 pure source selection, page sampling and additional page-language gate."""
from __future__ import annotations
import hashlib
import random
from . import admission
from .round1 import positions, replacement_candidates

SEED = 20266
HOLDOUT_SEED = 20261015
MAX_BYTES = 300_000_000


def candidates(rows):
    selected = [r for r in rows if r.get('source') == 'archive' and r.get('estimated_cyrillic_lines', 0) > 0]
    if len(selected) != 13 or len({r['document_id'] for r in selected}) != 13:
        raise ValueError('exact thirteen-item scope required')
    for r in selected:
        if not r['rights']['compatible'] or r['rights']['family'] not in ('public-domain', 'CC-BY'):
            raise ValueError('incompatible rights')
        if r['print_review']['status'] != 'verified-target-sample':
            raise ValueError('unverified printed sample')
    return sorted(selected, key=lambda r:r['document_id'])


def media(row):
    files = [f for f in row['scan_files'] if f['name'].lower().endswith('.pdf') and 0 < int(f['size']) <= MAX_BYTES]
    if not files:
        return dict(kind='page_images', url=None, bytes=None)
    chosen = min(files, key=lambda f:(f['url'] != row['download_url'], not f['name'].endswith('_text.pdf'), int(f['size'])))
    return dict(kind='pdf', url=chosen['url'], bytes=int(chosen['size']))


def key(identifier):
    return hashlib.sha256(('archive_'+identifier).encode()).hexdigest()[:8]


def sample(total, book):
    picks = positions(total, 45, seed=SEED, book=book)
    reserved = {p['page'] for p in picks}
    return [dict(p, candidates=replacement_candidates(p['page'], total, reserved=reserved-{p['page']})) for p in picks]


def holdout(books):
    if len(books) != 13 or len({b['key'] for b in books}) != 13:
        raise ValueError('thirteen unique books required')
    chosen = random.Random(HOLDOUT_SEED).sample(sorted(books,key=lambda b:b['key']), 3)
    return sorted([dict(book_key=b['key'], book=b['book'], title=b['title'], year=b['year'],
                        decade=b['decade'], split='test' if i<2 else 'dev') for i,b in enumerate(chosen)], key=lambda b:b['book_key'])


def page_script(text):
    counts = admission.inventory(text)
    letters, cyr = counts['letter_count'], counts['cyrillic_letters']
    # Integer comparison makes the inclusive 70% boundary exact. Empty pages fail.
    return dict(letters=letters, cyrillic_letters=cyr, cyrillic_share=cyr/letters if letters else None,
                not_cyrillic_page=not letters or 10*cyr < 7*letters)


def admit(record, quality, script):
    good, cls, reasons, label = admission.admit(dict(record,bad_page=quality['bad_page']))
    if script['not_cyrillic_page']:
        reasons = reasons+['not_cyrillic_page']
    return good and not reasons, cls if not reasons else None, reasons, label

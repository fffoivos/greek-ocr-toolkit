"""T25 offline selection policy. No service clients and no admission changes."""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import math
import random
import re

from .round1 import base, positions, replacement_candidates
from .openarchives import canonical_url, extract_year, metadata, urls

SEED = 20265
HOLDOUT_SEED = 20261015
TITLE_PATTERN = r'λεξικ|γραμματικ|περιοδικ|επετηρ|δελτιον|γαλλ|αγγλ|γερμ|ιταλ|λατιν|διαλογ|μεθοδος'


def title_matches(title):
    return bool(re.search(TITLE_PATTERN, base(title or '')))


def anemi_eligible(row, excluded):
    if row.get('document_id') in excluded:
        return False, 'previous_book'
    year = row.get('year')
    if not isinstance(year, int) or isinstance(year, bool) or not 1860 <= year <= 1935:
        return False, 'year'
    if not title_matches(row.get('title')):
        return False, 'title'
    if not row.get('download_url'):
        return False, 'no_pdf'
    return True, None


def anemi_draw(candidates, count=40, seed=SEED):
    ordered = sorted(candidates, key=lambda r:r['book'])
    if len({r['book'] for r in ordered}) != len(ordered) or len(ordered) < count:
        raise ValueError('insufficient distinct Anemi candidates')
    return random.Random(seed).sample(ordered, count)


def repository_candidate(row):
    """Use the retained direct source link even when the T24 join was absent.

    Wave 5 specifies OCR-routed scans and 20-50% Latin, not Wave 4's >=80%
    Greek or null-incompatible mojibake test. Preserve that distinction.
    """
    pipe, src = row['pipeline_metadata'], row['source_metadata']
    latin = pipe.get('latin_percentage')
    if pipe.get('ocr_success') is not True or not isinstance(latin, (float,int)) or not 20 <= latin <= 50:
        raise ValueError('not a retained scanned mixed candidate')
    direct = row.get('pdf_url') or next(iter(urls(src.get('pdf_links_json'))), None)
    if not direct:
        raise ValueError('no_direct_link')
    # Seven distinct pages in the final 12% require at least 51 pages.
    total = pipe.get('page_count')
    if not isinstance(total, (int,float)) or int(total)-math.floor(.88*int(total)) < 7:
        raise ValueError('too_few_bibliography_pages')
    meta = metadata(src.get('metadata_json'))
    year, year_receipt = extract_year(meta)
    slug = row['collection_slug']
    ident = hashlib.sha256((slug+'\n'+canonical_url(direct)).encode()).hexdigest()
    title = next((str(meta[k]) for k in ('Τίτλος','Title','title','dc.title') if meta.get(k)), src.get('filename',ident))
    rights = {k:v for k,v in meta.items() if any(s in base(k) for s in ('δικαιωμ','rights','licen'))}
    return dict(book=ident,key=ident[:8],id6=ident[:6],title=title,year=year,
        decade=year//10*10 if year else None,year_receipt=year_receipt,part='B',
        collection_slug=slug,pdf_url=direct,source_url=row.get('source_url') or direct,
        source='openarchives_mixed_'+slug,origin='openarchives',
        attribution=slug+'; '+title,licence='per-repository (recorded, unverified)',
        recorded_rights=rights,metadata_row=row['metadata_row'],pipeline_metadata=pipe,
        source_metadata=src,external_status_200=row.get('external_status_200',False),
        join_method=row.get('join_method'),declared_pages=int(total))


def repository_order(candidates, seed=SEED):
    """Seeded round-robin reserves: failed repositories cannot dominate."""
    groups = defaultdict(list)
    seen = set()
    for r in sorted(candidates,key=lambda r:r['book']):
        canonical = canonical_url(r['pdf_url'])
        if canonical not in seen:
            groups[r['collection_slug']].append(r)
            seen.add(canonical)
    rng = random.Random(seed)
    slugs = sorted(groups)
    rng.shuffle(slugs)
    for rows in groups.values():
        rng.shuffle(rows)
    return [groups[s][i] for i in range(max(map(len,groups.values()),default=0))
            for s in slugs if i < len(groups[s])]


def repository_positions(total, book='', seed=SEED):
    """7 pages strictly in the last 12%, plus 3 at 40/50/60%.

    ceil(.88*N) would admit a page outside the final 12% for noninteger
    boundaries. The first permitted page is floor(.88*N)+1.
    """
    if total < 1:
        raise ValueError('positive page count required')
    lo = math.floor(.88*total)+1
    if total-lo+1 < 7:
        raise ValueError('too_few_bibliography_pages')
    tail = [round(lo+(total-lo)*i/6) for i in range(7)]
    middle = [round(total*f) for f in (.4,.5,.6)]
    if len(set(tail+middle)) != 10:
        raise ValueError('not ten distinct pages')
    plans = []
    reserved = set(tail+middle)
    for number in middle+tail:
        region = 'last12' if number in tail else 'middle'
        upper = total if region=='last12' else math.floor(.65*total)
        candidates = [p for p in range(number,min(number+2,upper)+1)
                      if p==number or p not in reserved]
        plans.append(dict(page=number,region=region,candidates=candidates))
    return sorted(plans,key=lambda p:p['page'])


def spread_positions(total, count, book, seed=SEED):
    plans = positions(total,count,seed=seed,book=book)
    reserved = {p['page'] for p in plans}
    return [dict(p,region='spread',candidates=replacement_candidates(p['page'],total,
        reserved=reserved-{p['page']})) for p in plans]


def select_holdout(books, seed=HOLDOUT_SEED, *, dev_counts=None):
    """Ceil 15% per part; largest-remainder 3:1; singleton is test-only.

    A partial acquisition may supply the final dev apportionment explicitly.
    For 40/40/1 sources, 13 held sources become 10 test / 3 dev: A 4/2,
    B 5/1, C 1/0. The fractional tie between A and B is resolved by part name.
    """
    groups = defaultdict(list)
    keys = [b['key'] for b in books]
    if len(keys) != len(set(keys)):
        raise ValueError('duplicate source key')
    for b in books:
        groups[b['part']].append(b)
    counts = {part:math.ceil(.15*len(rows)) for part,rows in groups.items()}
    if dev_counts is None:
        dev_counts = {part:(count//4 if count>1 else 0) for part,count in counts.items()}
        target = int(math.floor(sum(counts.values())/4+.5))
        spare = target-sum(dev_counts.values())
        order = sorted((p for p in counts if counts[p]>1),key=lambda p:(-(counts[p]/4-counts[p]//4),p))
        for part in order[:spare]:dev_counts[part] += 1
    held = []
    for part, rows in sorted(groups.items()):
        rng = random.Random(seed)
        count = counts[part]
        chosen = rng.sample(sorted(rows,key=lambda b:b['key']),count)
        dev = dev_counts[part]
        for i,b in enumerate(chosen):
            held.append(dict(book_key=b['key'],book=b['book'],part=part,title=b['title'],
                year=b['year'],decade=b['decade'],split='dev' if i<dev else 'test'))
    return sorted(held,key=lambda b:(b['part'],b['book_key']))

"""T24c pipeline-metadata selection and document-disjoint sampling.

Offline on import. URLs are joined after HTML/percent decoding, with queries
retained: two bitstreams must never be equated by basename or handle alone.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import html
import json
import math
from pathlib import Path
import random
import re
import statistics
import unicodedata
from urllib.parse import unquote, urlsplit, urlunsplit

SEED = 20264
MAX_PDF = 200_000_000
LICENCE = 'per-repository (recorded, unverified)'


def urls(value):
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (ValueError, TypeError):
            return [value] if value.startswith(('https://', 'http://')) else []
        if isinstance(value, str):
            return [value] if value.startswith(('https://', 'http://')) else []
    return [v for v in (value or []) if isinstance(v, str) and v.startswith(('https://', 'http://'))] if isinstance(value, list) else []


def canonical_url(url):
    p = urlsplit(html.unescape(url.strip()))
    # Decode only unreserved ASCII and UTF-8 characters; keep reserved escapes
    # (%2F, %26, %3F, etc.) so URL components do not acquire new boundaries.
    def decode(part):
        part = re.sub(r'%[0-9a-fA-F]{2}', lambda m:m[0].upper(), part)
        protected = {}
        for i, token in enumerate(sorted(set(re.findall(r'%[0-9A-F]{2}',part)))):
            if chr(int(token[1:],16)) in ':/?#[]@!$&\'()*+,;=%':
                marker = f'__reserved_url_{i}__'
                protected[marker] = token
                part = part.replace(token, marker)
        part = unicodedata.normalize('NFC', unquote(part))
        for marker, token in protected.items():
            part = part.replace(marker, token)
        return part
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), decode(p.path), decode(p.query), ''))


def metadata(value):
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return {}
    return value if isinstance(value, dict) else {}


def extract_year(meta):
    """Prefer publication chronology to repository accession/availability dates.

    No year is inferred from title, filename or creator life dates. Preserve
    the exact chosen key/value to make metadata dates reviewable.
    """
    meta = metadata(meta)
    candidates = []
    for k, v in meta.items():
        key = unicodedata.normalize('NFD', k.lower())
        key = ''.join(c for c in key if not unicodedata.combining(c))
        if not any(s in key for s in ('date', 'year', 'ημερομην', 'χρονολογ', 'ετος')):
            continue
        if any(s in key for s in ('accession', 'available', 'modified', 'καταχωρ', 'εισαγωγ')):
            continue
        priority = (0 if any(s in key for s in ('χρονολογ', 'issued', 'publication', 'year', 'ετος')) else 1)
        for year in re.findall(r'(?<!\d)(?:1[5-9]\d{2}|20[0-2]\d)(?!\d)', str(v)):
            candidates.append((priority, k, int(year), v))
    if not candidates:
        return None, None
    _, key, year, value = sorted(candidates, key=lambda c: (c[0], c[1], c[2]))[0]
    return year, dict(key=key, value=value)


def document_type(value):
    v = str(value or '').lower()
    if any(w in v for w in ('thesis', 'dissertation', 'διατριβ', 'διπλωμα', 'πτυχια', 'μεταπτυχ')):
        return 'thesis'
    if any(w in v for w in ('article', 'άρθρ', 'αρθρ')):
        return 'article'
    if any(w in v for w in ('book', 'βιβλί', 'βιβλι', 'monograph')):
        return 'book'
    return 'other'


class LinkIndex:
    def __init__(self, rows):
        self.rows = rows
        self.by_url, self.by_edm, self.status_by_url = defaultdict(list), defaultdict(list), defaultdict(list)
        for i, row in enumerate(rows):
            for url in set(canonical_url(u) for u in urls(row.get('pdf_links_json'))):
                self.by_url[(row['collection_slug'], url)].append(i)
                self.status_by_url[url].append(i)
            if row.get('edm_url'):
                self.by_edm[canonical_url(row['edm_url'])].append(i)

    def join(self, row):
        src, pipe = row.get('source_metadata', {}), row.get('pipeline_metadata', {})
        matches = set()
        for url in urls(src.get('pdf_links_json')):
            matches.update(self.by_url.get((src.get('collection_slug'), canonical_url(url)), []))
        method = 'collection_url'
        if not matches:
            method = 'edm_url'
            for field in (row.get('edm_url'), src.get('edm_url'), pipe.get('url')):
                if isinstance(field, str) and field.startswith(('http://', 'https://')):
                    matches.update(self.by_edm.get(canonical_url(field), []))
        result = sorted(matches, key=lambda i: (self.rows[i].get('status_code') != 200,
                                               self.rows[i].get('edm_url', ''), i))
        return result, method if result else None


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def base_filters(pipe):
    return (
        ('download_success', pipe.get('download_success') is True),
        ('ocr_success', pipe.get('ocr_success') is True),
        ('filter_ok', pipe.get('filter') == 'ok'),
        ('is_empty_false', pipe.get('is_empty') is False),
        ('percentage_greek_ge80', finite(pipe.get('percentage_greek')) and pipe['percentage_greek'] >= 80),
        ('mojibake_zero', pipe.get('mojibake_badness_score') is None or (finite(pipe.get('mojibake_badness_score')) and pipe['mojibake_badness_score'] == 0)),
        ('pages_20_600', finite(pipe.get('page_count')) and 20 <= pipe['page_count'] <= 600),
        ('finite_greek_badness', pipe.get('greek_badness_score') is None or finite(pipe.get('greek_badness_score'))),
    )


def describe(row, ext, number, method, match_count):
    src, pipe = row['source_metadata'], row['pipeline_metadata']
    meta = metadata(src.get('metadata_json'))
    year, year_receipt = extract_year(meta)
    src_urls = urls(src.get('pdf_links_json'))
    ext_urls = urls(ext.get('pdf_links_json'))
    shared = [u for u in ext_urls if canonical_url(u) in {canonical_url(v) for v in src_urls}]
    direct = src_urls
    if not direct:
        raise ValueError('joined document has no direct PDF URL')
    url = html.unescape(direct[0])
    ident = hashlib.sha256((src['collection_slug']+'\n'+canonical_url(url)).encode()).hexdigest()
    title = next((str(meta[k]) for k in ('Τίτλος', 'Title', 'title', 'dc.title') if meta.get(k)), src.get('filename', ident))
    return dict(book=ident, key=ident[:8], title=title, collection_slug=src['collection_slug'],
        year=year, decade=year//10*10 if year is not None else None, year_receipt=year_receipt,
        type=document_type(src.get('type')), type_raw=src.get('type'),
        pdf_url=url, source_url=ext.get('external_link') or src.get('external_link') or url,
        source_url_basis='external_link' if ext.get('external_link') or src.get('external_link') else 'direct PDF (external_link absent)',
        earlier_status_code=ext.get('status_code'), external_row=ext,
        source_metadata=src, pipeline_metadata=pipe, metadata_row=number,
        join_method=method, join_match_count=match_count,
        licence=LICENCE, source='openarchives_'+src['collection_slug'], origin='openarchives',
        attribution=src['collection_slug']+'; '+title)


def build_pool(parquet, jsonl):
    import pyarrow.parquet as pq
    parquet, jsonl = Path(parquet), Path(jsonl)
    if not jsonl.exists() or list(jsonl.parent.glob('doc_metadata*.partial')):
        raise RuntimeError('final metadata not ready; poll every 120 seconds')
    index = LinkIndex(pq.read_table(parquet).to_pylist())
    counts = Counter({k:0 for k in ('metadata_rows','joined_metadata_rows','scanned_metadata_rows',
        'joined_scanned_rows','multiple_external_matches','external_status_200','duplicate_document_rows',
        'wave5_scanned_latin_20_50',*(name for name,_ in base_filters({})))})
    methods, repositories, unmatched, matched_ext = Counter(), Counter(), Counter(), set()
    scanned_scores, marginal, chars = Counter(), Counter(), []
    preliminary, wave5, seen = [], [], set()
    for number, line in enumerate(jsonl.open(), 1):
        row = json.loads(line)
        src, pipe = row.get('source_metadata', {}), row.get('pipeline_metadata', {})
        counts['metadata_rows'] += 1
        # Informational URL lookup only, across collections too: metadata owns
        # the repository and direct URL. No EDM/filename fallback or status gate.
        matches = sorted({i for u in urls(src.get('pdf_links_json'))
                          for i in index.status_by_url.get(canonical_url(u), [])})
        method = 'url_informational' if matches else None
        if matches:
            counts['joined_metadata_rows'] += 1
            counts['multiple_external_matches'] += len(matches)>1
            methods[method] += 1
            matched_ext.update(matches)
        else:
            unmatched[src.get('collection_slug', 'unknown')] += 1
        if pipe.get('ocr_success') is True:
            counts['scanned_metadata_rows'] += 1
            counts['joined_scanned_rows'] += bool(matches)
            score=pipe.get('mojibake_badness_score')
            scanned_scores['null' if score is None else str(score)] += 1
            for name, passed in base_filters(pipe):
                if passed:
                    marginal[name] += 1
        latin = pipe.get('latin_percentage')
        w5 = pipe.get('ocr_success') is True and finite(latin) and 20 <= latin <= 50
        passes = True
        for name, passed in base_filters(pipe):
            passes = passes and passed
            if passes:
                counts[name] += 1
        ext = index.rows[matches[0]] if matches else None
        status_ok = ext is not None and ext.get('status_code') == 200
        if passes and status_ok:
            counts['external_status_200'] += 1
        passes = passes and bool(urls(src.get('pdf_links_json')))
        counts['direct_pdf_url'] += passes
        if not (passes or w5):
            continue
        if w5:
            counts['wave5_scanned_latin_20_50'] += 1
            # Retain every requested scanned mixed candidate, including unmatched
            # rows, without imposing the incompatible >=80% Greek constraint.
            if ext is not None and urls(ext.get('pdf_links_json')):
                mixed = describe(row, ext, number, method, len(matches))
            else:
                mixed = dict(metadata_row=number, source_metadata=src, pipeline_metadata=pipe,
                             collection_slug=src.get('collection_slug'), join_method=method)
            mixed['external_status_200'] = status_ok
            wave5.append(mixed)
        if passes:
            candidate = describe(row, ext or {}, number, method, len(matches))
            if candidate['book'] in seen:
                counts['duplicate_document_rows'] += 1
                continue
            seen.add(candidate['book'])
            preliminary.append(candidate)
    measured = [r['pipeline_metadata']['greek_badness_score'] for r in preliminary
                if finite(r['pipeline_metadata'].get('greek_badness_score'))]
    median = statistics.median(measured) if measured else None
    pool = [r for r in preliminary if r['pipeline_metadata'].get('greek_badness_score') is None
            or r['pipeline_metadata']['greek_badness_score'] <= median]
    counts['unique_pre_median_documents'] = len(preliminary)
    counts['greek_badness_le_median'] = len(pool)
    for r in pool:
        repositories[r['collection_slug']] += 1
        p=r['pipeline_metadata']
        if finite(p.get('char_count_no_comments')):
            chars.append(p['char_count_no_comments']/p['page_count'])
    with_year = sum(r['year'] is not None for r in pool)
    receipt = dict(schema='t24c-pool-1', counts=dict(counts), external_rows=len(index.rows),
        external_rows_joined=len(matched_ext), join_methods=dict(methods),
        join_coverage=counts['joined_metadata_rows']/counts['metadata_rows'],
        scanned_join_coverage=counts['joined_scanned_rows']/counts['scanned_metadata_rows'] if counts['scanned_metadata_rows'] else 0,
        scanned_mojibake_score_inventory=dict(scanned_scores),
        marginal_scanned_filter_passes=dict(marginal),
        unmatched_per_repository=dict(unmatched), pool_per_repository=dict(repositories),
        median_greek_badness=median,
        median_basis='finite measured scores only, unique pipeline documents satisfying all other filters; URL lookup/status never controls eligibility (T24c)',
        measured_greek_badness_documents=len(measured),
        null_score_policy='null mojibake passes; null Greek badness passes and is excluded from median; non-null nonfinite values fail',
        pool_with_year=with_year, pool_year_share=with_year/len(pool) if pool else None,
        pool_decades=dict(Counter(str(r['decade']) for r in pool)),
        pool_types=dict(Counter(r['type'] for r in pool)),
        characters_per_page=dict(min=min(chars) if chars else None, median=statistics.median(chars) if chars else None,
                                 max=max(chars) if chars else None),
        capacity_at_10_per_repository=sum(min(n,10) for n in repositories.values()),
        wave5_count=len(wave5), wave5_policy='all ocr_success true, latin_percentage 20-50 inclusive; other qualities recorded, not filtered')
    return pool, wave5, receipt


def stratified_draw(rows, count=173, seed=SEED, per_repository=10):
    """Round-robin repositories, then least-used type/decade strata, seeded ties.

    Cap applies to the entire overdraw, so every successful prefix obeys it.
    Known decades remain literal (including any outside 1980-2019); null dates
    have an explicit stratum. No undocumented date/character-count filter.
    """
    groups = defaultdict(lambda: defaultdict(list))
    seen = set()
    for row in sorted(rows, key=lambda r:r['book']):
        if row['book'] in seen:
            raise ValueError('duplicate document identity')
        seen.add(row['book'])
        groups[row['collection_slug']][(row['type'],str(row['decade']))].append(row)
    rng, used, strata_used, result = random.Random(seed), Counter(), Counter(), []
    for repo in sorted(groups):
        for stratum in sorted(groups[repo]):
            rng.shuffle(groups[repo][stratum])
    while len(result) < count:
        repos = [r for r in sorted(groups) if used[r]<per_repository and any(groups[r].values())]
        if not repos:
            break
        minimum = min(used[r] for r in repos)
        repos = [r for r in repos if used[r]==minimum]
        rng.shuffle(repos)
        for repo in repos:
            strata = [s for s in sorted(groups[repo]) if groups[repo][s]]
            n = min(strata_used[repo,s] for s in strata)
            stratum = rng.choice([s for s in strata if strata_used[repo,s]==n])
            result.append(groups[repo][stratum].pop())
            strata_used[repo,stratum] += 1
            used[repo] += 1
            if len(result) == count:
                break
    return result


def holdout(books, seed=20261015, count=20, dev=5):
    """Repository-stratified whole-document draw, frozen before paid reads."""
    if not 0 <= dev <= count or len({b['key'] for b in books}) != len(books):
        raise ValueError('invalid holdout counts or duplicate document key')
    chosen = stratified_draw(books, count, seed, per_repository=count)
    if len(chosen) != count:
        raise ValueError('insufficient distinct documents for fixed holdout')
    rng = random.Random(seed)
    dev_keys = {b['key'] for b in rng.sample(chosen, dev)}
    return sorted([dict(book_key=b['key'], document_id=b['book'], title=b['title'],
        year=b['year'], decade=b['decade'], collection_slug=b['collection_slug'],
        split='dev' if b['key'] in dev_keys else 'test') for b in chosen], key=lambda b:b['book_key'])


def capped_draw(rows, target=130, count=173, seed=SEED):
    """Raise the cap only when it cannot fill the requested successful sample."""
    repos = Counter(r['collection_slug'] for r in rows)
    cap = next((c for c in (10, 20, 30) if sum(min(n,c) for n in repos.values()) >= target), 30)
    return stratified_draw(rows, count, seed, cap), cap

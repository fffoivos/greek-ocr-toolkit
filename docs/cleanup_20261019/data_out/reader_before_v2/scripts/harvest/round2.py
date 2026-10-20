"""T22: seeded Anemi selection, bounded receipted fetch/gate and DocAI reads.

Only fetch-gate, read-watch and run use network. Credentials stay in the env.
The T16 acquisition adapter retains upstream transport, login and page receipts.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import copy
from datetime import datetime, timezone
import json
import multiprocessing
import os
from pathlib import Path
import random
import re
import shutil
import time
from urllib.parse import urlsplit

from PIL import Image

from scripts.harvest import round1, vouli
from scripts.harvest.round1_reads import frozen
from greekocr.harvest.round1 import base, positions, replacement_candidates
from greekocr.harvest.pipeline import FrozenStack
from greekocr.harvest.readers import atomic, read_jsonl

REPO = round1.ROOT
OUT = REPO / 'docs/harvest/round2'
BULK = REPO / 'docs/harvest/harvest_big/round2'
GOOGLE = BULK / 'google'
CATALOGUE = round1.UPSTREAM / 'docs/evidence/o4c/anemi.jsonl'
EARLY = Path('/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/node_backup_20261008/e2-assets/anemi')
CAP = 1.50
SOURCE = 'anemi_round2'
SEED = 20262
ADMISSION_SHA = vouli.ADMISSION_SHA
sha, relative = vouli.sha, vouli.relative
DECADES = tuple(range(1860, 1940, 10))
PLACE_PATTERNS = {
    'Athens': r'αθην|ath[eè]nes|athens', 'Constantinople': r'κωνσταντινουπολ|constantinop',
    'Smyrna': r'σμυρν|smyrn', 'Syros': r'συρ[ωο]|ερμουπολ', 'Patras': r'πατραι|πατρων|πατρας',
    'Alexandria': r'αλεξανδρει|alexandri', 'Leipzig': r'λειψι|leipzig',
    'Vienna': r'βιενν|vienn|wien', 'Paris': r'παρισι|paris', 'Venice': r'βενετι|ενετιη|venez|venice',
    'Corfu': r'κερκυρ|corfu', 'Trieste': r'τριεστ|trieste', 'Ermoupoli': r'ερμουπολ',
    'Thessaloniki': r'θεσσαλονικ|thessaloni', 'Ioannina': r'ιωαννιν',
}


def place_hints(text):
    text = base(text)
    return sorted(k for k, pattern in PLACE_PATTERNS.items() if re.search(pattern, text))


def fields(row, name):
    value = row.get('metadata_fields_displayed', {}).get(name, [])
    return [value] if isinstance(value, str) else value


def eligible(row, excluded):
    if row['document_id'] in excluded:
        return False, 'previous_book'
    year, pages = row.get('year'), row.get('pages')
    if not isinstance(year, int) or not 1860 <= year <= 1935:
        return False, 'year'
    languages = row.get('language', [])
    if isinstance(languages, str):
        languages = [languages]
    codes = set(languages) | set(row.get('catalogue_languages', []))
    if not codes & {'gre', 'grc', 'Greek, Modern (1453-)', 'Greek, Ancient (to 1453)'}:
        return False, 'language'
    if not row.get('download_url') or not isinstance(pages, int) or pages < 60:
        return False, 'pdf_or_pages'
    if row.get('catalogue_materials') != ['010']:
        return False, 'not_monograph'
    title = base(row.get('title', ''))
    main = title.split(' / ')[0]
    greek = sum('α' <= c <= 'ω' for c in main)
    latin = sum('a' <= c <= 'z' for c in main)
    if greek < 8 or latin > greek / 2:
        return False, 'plainly_foreign_title'
    if re.search(r'λεξικ|γραμματικ|diction|gramma|lexico|λεξιλογ|συνωνυμ|συντακτικ|μετρικ|ορθογραφ|ετυμολογ|εκμαθησ|μεθοδος.*γλωσσ', main):
        return False, 'wave5_dictionary_grammar'
    if re.search(r'επετηρι|^ημερολογιο|^περιοδικ|^journal|^revue', main):
        return False, 'wave5_periodical'
    return True, None


def early_exclusions():
    ids, inputs = set(), {}
    for path in sorted(EARLY.glob('records/*/receipts.jsonl')):
        rows = read_jsonl(path)
        saved = [r for r in rows if r.get('state') == 'saved']
        if saved:
            ids.update(r['record_id'] for r in saved)
            inputs[str(path)] = sha(path)
    if len(ids) != 57:
        raise ValueError('expected exactly 57 previously fetched early-print books')
    return ids, inputs


def draw_books(candidates, place_counts, publisher_counts, seed=SEED):
    """Seeded weighted draw without replacement, six per decade plus two sevens."""
    rng = random.Random(seed)
    extra = set(rng.sample(list(DECADES), 2))
    selected, quotas = [], {d: 6 + int(d in extra) for d in DECADES}
    for decade in DECADES:
        pool = sorted((b for b in candidates if b['decade'] == decade), key=lambda b: b['book'])
        if len(pool) < quotas[decade]:
            raise ValueError(f'insufficient eligible books in {decade}s')
        scored = []
        for b in pool:
            places = b['place_hints']
            publishers = b['publishers']
            weight = 1 + (2 / (1 + sum(place_counts[p] for p in places)) if places else 0)
            weight += 2 / (1 + sum(publisher_counts[p] for p in publishers)) if publishers else 0
            score = rng.random() ** (1 / weight)
            scored.append((score, b['book'], dict(b, draw_weight=weight, draw_score=score)))
        selected.extend(b for _, _, b in sorted(scored, reverse=True)[:quotas[decade]])
    return sorted(selected, key=lambda b: (b['decade'], b['title'], b['book'])), quotas


def select_holdout(books, seed=20261015):
    rng = random.Random(seed)
    if len(books) != 50 or len({b['key'] for b in books}) != 50:
        raise ValueError('hold-out requires fifty distinct books')
    chosen = [rng.choice(sorted((b for b in books if b['decade'] == d), key=lambda b: b['key']))
              for d in DECADES]
    rng.shuffle(chosen)
    return sorted([dict(book_key=b['key'], book=b['book'], title=b['title'], year=b['year'],
                        decade=b['decade'], split='dev' if i < 2 else 'test')
                   for i, b in enumerate(chosen)], key=lambda b: b['book_key'])


def selection():
    vouli.check_frozen()
    OUT.mkdir(parents=True, exist_ok=True)
    if not (OUT / 'git_before.json').exists():
        atomic(OUT / 'git_before.json', round1.git_snapshot())
    rows = read_jsonl(CATALOGUE)
    if len(rows) != 7841 or sum(bool(r.get('download_url')) for r in rows) != 6531:
        raise ValueError('catalogue scope changed')
    prior = json.loads((round1.OUT / 'selection.json').read_text())
    early, early_inputs = early_exclusions()
    old_ids = {b['book'] for b in prior['books']}
    if len(old_ids) != 150:
        raise ValueError('round-1 exclusion scope changed')
    excluded = old_ids | early
    byid = {r['document_id']: r for r in rows}
    place_counts = Counter(p for b in prior['books'] for p in place_hints(b['title']))
    publisher_counts = Counter(base(p).strip(' ,.:') for b in prior['books']
                               for p in fields(byid.get(b['book'], {}), 'Publisher Name'))
    fm = round1.fetch_module()
    candidates, removals = [], Counter()
    for row in rows:
        ok, reason = eligible(row, excluded)
        if not ok:
            removals[reason] += 1
            continue
        plans = fm.build_plan([row])
        if not plans or plans[0]['pages'] is None or plans[0]['pages'] < 60:
            removals['invalid_volume_plan'] += 1
            continue
        cat = plans[0]
        if any(urlsplit(v['source_pdf_url']).netloc != 'anemi.lib.uoc.gr' or not v['viewer_url'] for v in cat['volumes']):
            removals['no_anemi_viewer'] += 1
            continue
        key = fm.record_key(row['document_id'])
        candidates.append(dict(book=row['document_id'], key=key, id6=key[:6], title=row['title'],
            year=row['year'], decade=row['year'] // 10 * 10, pages=cat['pages'],
            catalogue_pages=row['pages'], catalogue=cat, allocation=13,
            place_hints=place_hints(' '.join(fields(row, 'Place of publication'))) or place_hints(row['title']),
            place_basis='metadata' if fields(row, 'Place of publication') else 'title mention proxy',
            publishers=[base(p).strip(' ,.:') for p in fields(row, 'Publisher Name')],
            source_url=row['record_url'], attribution='Anemi Digital Library, University of Crete',
            licence='anemi-research-internal', source=SOURCE, origin='anemi'))
    books, quotas = draw_books(candidates, place_counts, publisher_counts)
    if len({b['id6'] for b in books}) != 50:
        raise ValueError('six-character crop directory collision')
    for i, b in enumerate(books, 1):
        b['catalogue']['rank'] = i
        pos = positions(b['pages'], 13, seed=SEED, book=b['book'])
        reserved = {p['page'] for p in pos}
        b['positions'] = [dict(p, candidates=replacement_candidates(p['page'], b['pages'], reserved=reserved - {p['page']})) for p in pos]
    inputs = {str(CATALOGUE): sha(CATALOGUE), relative(round1.OUT / 'selection.json'): sha(round1.OUT / 'selection.json'), **early_inputs}
    result = dict(schema='t22-selection-1', seed=SEED, books=books, quotas=quotas,
        eligible_per_decade=dict(Counter(b['decade'] for b in candidates)), excluded_round1=sorted(old_ids),
        excluded_early=sorted(early), excluded_early_basis='57 source-bound saved-page receipt files in archived E2 assets',
        round1_title_place_hints=dict(place_counts), round1_publishers=dict(publisher_counts),
        rejected_candidates=dict(removals), quality_limits=prior['quality_limits'], inputs=inputs,
        fetcher_upstream_sha256=sha(round1.UPSTREAM / 'scripts/fetch/o4b_anemi_pages.py'),
        fetcher_t16_adapter_sha256=sha(REPO / 'scripts/harvest/_anemi_round1_fetcher.py'))
    frozen(OUT / 'selection.json', json.loads(json.dumps(result)))
    frozen(OUT / 'books.json', books)
    frozen(OUT / 'holdout_books.json', select_holdout(books))
    held = {b['book_key']: b['split'] for b in select_holdout(books)}
    lines = ['# T22 round 2 selection', '',
        '50 new Greek monographs, 1860–1935, source-listed PDF and at least 60 declared pages. Seed 20262. '
        'All 150 round-1 books and the 57 early-print books with saved-page receipts are excluded. '
        'Catalogue language/material codes and title checks are selection evidence; printed language is checked after reading.', '',
        'Six books per decade, with two seeded decades receiving seven. Weighted seeded draws without replacement prefer '
        'places/publishers less represented in round 1. Weight = 1 + 2/(1 + prior place mentions) for known places '
        '+ 2/(1 + prior publisher count) for known publishers. Missing fields receive no diversity bonus. '
        'Place names in titles are proxies: they can describe a subject rather than a printing location. '
        'Round-1 counts use all 150 selection titles, including removed books; publisher counts use available catalogue detail fields.', '',
        '| Round-1 title place hint | Books mentioning |', '|---|---:|']
    lines += [f'| {p} | {n} |' for p, n in place_counts.most_common()]
    lines += ['', f"Titles without a recognized place: {sum(not place_hints(b['title']) for b in prior['books'])}/150. "
        f"Known publisher entries: {sum(publisher_counts.values())}/150; counts: `{json.dumps(dict(publisher_counts), ensure_ascii=False)}`.", '',
        '| Decade | Eligible | Selected | Planned pages |', '|---|---:|---:|---:|']
    lines += [f'| {d}s | {result["eligible_per_decade"][d]} | {quotas[d]} | {13 * quotas[d]} |' for d in DECADES]
    lines += ['', '13 evenly spaced 8–95% positions/book; seeded forward offsets 0–2. Each failed slot may try '
        'only the next two physical neighbours, excluding other reserved positions and the 95% boundary. '
        'No unbounded replacement search. Gate and photometric guards are unchanged T16. '
        '650 accepted pages is the target; exhausted slots are reported explicitly. '
        'Hold-out seed 20261015 picks one book per decade before reads, then shuffles to 6 test / 2 dev.', '',
        '| Decade | Year | ID | Title | Declared pages | Place hint (basis) | Publisher | Weight | Split | Planned pages |',
        '|---|---:|---|---|---:|---|---|---:|---|---|']
    for b in books:
        title = b['title'].replace('|', '\\|').replace('\n', ' ')
        lines.append(f"| {b['decade']}s | {b['year']} | {b['id6']} | [{title}]({b['source_url']}) | {b['pages']} | "
            f"{', '.join(b['place_hints']) or 'unknown'} ({b['place_basis']}) | {', '.join(b['publishers']) or 'unknown'} | "
            f"{b['draw_weight']:.3f} | {held.get(b['key'], 'train')} | {', '.join(str(p['page']) for p in b['positions'])} |")
    (OUT / 'SELECTION.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(dict(books=50, planned_pages=650, quotas=quotas, eligible=result['eligible_per_decade'], prior_places=place_counts)), flush=True)
    return result


def gate_worker_init(limits):
    global STACK, GATE, LIMITS
    import onnxruntime as ort
    ort.disable_telemetry_events()
    STACK, GATE, LIMITS = FrozenStack(round1.PILOT / 'pilot/_stack_52cee3b'), round1.load_gate(), limits


def paths(book, number):
    volume, local = round1.locate(book, number)
    pdf = BULK / 'records' / book['key'] / volume['volume_id'] / f'page-{local:06d}.pdf'
    return volume, local, pdf, BULK / 'images' / f"{book['key']}-{number:06d}.png"


def gate_task(task):
    book, number, receipt = task
    volume, local, pdf, image = paths(book, number)
    image.parent.mkdir(parents=True, exist_ok=True)
    g = round1.gate_pdf(pdf, image, STACK, GATE, LIMITS)
    with Image.open(image) as im:
        width, height = im.size
    page = {k: book[k] for k in ('book', 'key', 'id6', 'title', 'year', 'decade', 'source_url', 'attribution', 'licence', 'source', 'origin')}
    page.update(id=f"{book['key']}-p{number:06d}", page=number, volume=volume['volume_id'], volume_page=local,
        pdf=relative(pdf), pdf_sha256=sha(pdf), image=relative(image), image_sha256=g['image_sha256'],
        width=width, height=height, dpi=200, grayscale=True, read_batch='round2', gate=g,
        fetch_receipt=receipt, harvest_accepted=g['accepted'])
    atomic(OUT / 'gates' / (page['id'] + '.json'), page)
    return page


def replay_slots(books, gates, failed):
    slots, used = [], defaultdict(set)
    for b in books:
        for pos in b['positions']:
            chain, accepted = [], None
            for n in pos['candidates']:
                key = f"{b['key']}:{n}"
                if n in used[b['book']]:
                    chain.append(dict(page=n, state='skipped', reasons=['already_attempted_by_another_slot']))
                    continue
                if key in failed:
                    used[b['book']].add(n)
                    chain.append(dict(page=n, state='fetch_failed', reasons=['fetch_failed']))
                elif key in gates:
                    p = gates[key]
                    used[b['book']].add(n)
                    chain.append(dict(page=n, state='accepted' if p['harvest_accepted'] else 'rejected', reasons=p['gate']['flags']))
                    if p['harvest_accepted']:
                        accepted = n
                        break
                else:
                    break
            slots.append(dict(book=b['book'], key=b['key'], original_page=pos['page'],
                candidate_pages=pos['candidates'], chain=chain, accepted_page=accepted))
    return slots, used


def fetch_gate():
    vouli.check_frozen()
    data = json.loads((OUT / 'selection.json').read_text())
    for name, digest in data['inputs'].items():
        if sha(REPO / name) != digest:
            raise ValueError('selection input changed')
    books, fm = data['books'], round1.fetch_module()
    http_root = BULK / 'anemi_http'
    http_root.mkdir(parents=True, exist_ok=True)
    prior_rate = round1.BIG / 'anemi_http/rate_state.json'
    if not (http_root / 'rate_state.json').exists():
        shutil.copyfile(prior_rate, http_root / 'rate_state.json')
    class PoliteAnemi(fm.AnemiHTTP):
        def _raw(self, url, limit, range_header=None, depth=0):
            if urlsplit(url).scheme != 'https' or urlsplit(url).netloc != 'anemi.lib.uoc.gr':
                raise fm.ProbeError('T22 restricts acquisition to Anemi HTTPS')
            policy_path = http_root / 'backoff.json'
            policy = json.loads(policy_path.read_text()) if policy_path.exists() else {}
            time.sleep(max(0, policy.get('not_before', 0) - time.time()))
            self.interval = max(self.interval, policy.get('interval', 2))
            result = super()._raw(url, limit, range_header, depth)
            if result[0]['status'] in (429, 503):
                n = policy.get('throttles', 0) + 1
                cooldown = min(600, 60 * 2 ** (n - 1))
                atomic(policy_path, dict(interval=min(30, max(4, self.interval * 2)), not_before=time.time()+cooldown, throttles=n))
                print(f'T22 throttle {result[0]["status"]}; cooldown {cooldown}s', flush=True)
            return result
    client = PoliteAnemi(interval=2, root=http_root)
    authenticated = False
    def login(http):
        nonlocal authenticated
        if not authenticated:
            fm.authenticate(http)
            authenticated = True
    def fetch_book(book, numbers):
        remaining, summaries, page_failures, transport_failures = list(numbers), [], {}, 0
        directory = BULK / 'records' / book['key']
        while remaining:
            recs = round1.stage_records([book], {book['book']: remaining})
            summary = fm.fetch_wave(recs, wave=1, max_pages=1950, max_bytes=1_500_000_000,
                dest=BULK, http_root=http_root, http_factory=lambda **kwargs:client,
                login=login, emit=lambda value:None, page_range='explicit')
            summaries.append(summary)
            receipts = fm.latest_receipts(directory)
            next_numbers = []
            for n in remaining:
                volume, local, _, _ = paths(book, n)
                receipt = receipts.get((volume['volume_id'], local-1), {})
                if fm.valid_receipt(receipt, directory, book['catalogue'], volume, local-1):
                    continue
                if receipt.get('state') == 'failed':
                    page_failures[f"{book['key']}:{n}"] = dict(book=book['book'], page=n,
                        receipt=receipt, errors=summary['errors'], stop_reason=summary['stop_reason'])
                else:
                    next_numbers.append(n)
            if next_numbers == remaining:
                transport_failures += 1
                if transport_failures >= 3:
                    raise RuntimeError('Anemi transport/authentication failed three times before page acquisition; no unattempted pages marked failed')
                client.interval = max(client.interval, 4)
                time.sleep(15 * transport_failures)
            else:
                transport_failures = 0
            remaining = next_numbers
        return dict(invocations=summaries, page_failures=page_failures)
    gates = {}
    for f in sorted((OUT / 'gates').glob('*.json')):
        p = json.loads(f.read_text())
        if sha(REPO / p['pdf']) != p['pdf_sha256'] or sha(REPO / p['image']) != p['image_sha256']:
            raise ValueError('resume PDF/image changed')
        gates[f"{p['key']}:{p['page']}"] = p
    failure_path, state_path = OUT / 'fetch_failures.json', OUT / 'run_state.json'
    failed = json.loads(failure_path.read_text()) if failure_path.exists() else {}
    state = json.loads(state_path.read_text()) if state_path.exists() else dict(started_at=datetime.now(timezone.utc).isoformat(), stages=[], elapsed_seconds=0)
    start = time.perf_counter()
    def checkpoint():
        slots, used = replay_slots(books, gates, failed)
        manifest = sorted(gates.values(), key=lambda p: (p['book'], p['page']))
        atomic(OUT / 'slots.json', slots)
        atomic(OUT / 'manifest.json', manifest)
        accepted = sum(s['accepted_page'] is not None for s in slots)
        summary = dict(books=50, target=650, fetched=len(gates), accepted=accepted, shortfall=650-accepted,
            replacements=sum(s['accepted_page'] is not None and s['accepted_page'] != s['original_page'] for s in slots),
            fetch_failures=len(failed), gate_flags=dict(Counter(f for p in manifest for f in p['gate']['flags'])),
            per_book={b['key']:dict(fetched=sum(p['key']==b['key'] for p in manifest),
                accepted=sum(s['key']==b['key'] and s['accepted_page'] is not None for s in slots)) for b in books})
        atomic(OUT / 'fetch_summary.json', summary)
        return slots, used
    with ProcessPoolExecutor(max_workers=3, mp_context=multiprocessing.get_context('spawn'),
            initializer=gate_worker_init, initargs=(data['quality_limits'],)) as gate_pool, ThreadPoolExecutor(max_workers=1) as network:
        for stage in range(3):
            slots, used = checkpoint()
            wanted = defaultdict(list)
            for s in slots:
                if s['accepted_page'] is not None:
                    continue
                consumed = {c['page'] for c in s['chain']}
                n = next((n for n in s['candidate_pages'] if n not in consumed and n not in used[s['book']]), None)
                if n is not None:
                    wanted[s['book']].append(n)
                    used[s['book']].add(n)
            if not wanted:
                break
            # One fetcher invocation per book allows a dead volume to consume only
            # its bounded slot attempts while the other selected books progress.
            pending = {}
            for b in books:
                numbers = wanted.get(b['book'], [])
                if not numbers:
                    continue
                future = network.submit(fetch_book, b, numbers)
                submitted = set()
                while not future.done() or len(submitted) < len(numbers):
                    receipts = fm.latest_receipts(BULK / 'records' / b['key'])
                    for n in numbers:
                        if n in submitted:
                            continue
                        volume, local, pdf, _ = paths(b, n)
                        receipt = receipts.get((volume['volume_id'], local-1), {})
                        if fm.valid_receipt(receipt, BULK / 'records' / b['key'], b['catalogue'], volume, local-1):
                            pending[gate_pool.submit(gate_task, (b, n, receipt))] = (b, n)
                            submitted.add(n)
                    for done in [f for f in pending if f.done()]:
                        p = done.result()
                        gates[f"{p['key']}:{p['page']}"] = p
                        del pending[done]
                    if future.done():
                        summary = future.result()
                        failed.update(summary['page_failures'])
                        for n in numbers:
                            if n not in submitted:
                                key = f"{b['key']}:{n}"
                                if key not in failed:
                                    raise ValueError('unattempted page has no fetch failure receipt')
                                submitted.add(n)
                        break
                    time.sleep(.25)
                summary = future.result()
                failed.update(summary['page_failures'])
                state['stages'].append(dict(stage=stage, book=b['key'], requested=numbers, fetch_summary=summary))
                atomic(failure_path, failed)
                slots, _ = checkpoint()
                atomic(state_path, state)
                print(f"fetch/gate stage={stage} book={b['id6']} fetched={len(gates)} accepted={sum(s['accepted_page'] is not None for s in slots)}/650 failures={len(failed)}", flush=True)
            for f in pending:
                p = f.result()
                gates[f"{p['key']}:{p['page']}"] = p
            checkpoint()
    state.update(complete=True, finished_at=datetime.now(timezone.utc).isoformat(), elapsed_seconds=state['elapsed_seconds']+time.perf_counter()-start,
        gate_seconds=sum(p['gate']['seconds'] for p in gates.values()))
    atomic(state_path, state)
    checkpoint()
    prepare_reads()


def prepare_reads():
    data = json.loads((OUT / 'selection.json').read_text())
    manifest, slots = [json.loads((OUT / name).read_text()) for name in ('manifest.json', 'slots.json')]
    chosen = {(s['key'], s['accepted_page']) for s in slots if s['accepted_page'] is not None}
    pages = [p for p in manifest if (p['key'], p['page']) in chosen]
    if {p['id'] for p in pages} != {p['id'] for p in manifest if p['harvest_accepted']}:
        raise ValueError('a gate-accepted page is outside the permanent slot scope')
    old_hashes = previous_page_hashes()
    if old_hashes & {p['image_sha256'] for p in pages}:
        raise ValueError('selected page already read in previous wave; stop before any re-read')
    unique = vouli.unique_call_pages(pages)
    reserved = {r['key'] for r in read_jsonl(GOOGLE / 'budget.jsonl')}
    if not reserved <= {p['image_sha256'] for p in pages}:
        raise ValueError('an earlier accepted-snapshot read is outside the final slot scope')
    if len(unique) * .0015 > CAP:
        raise ValueError('read plan exceeds USD 1.50')
    inputs = {relative(OUT / n): sha(OUT / n) for n in ('selection.json', 'books.json', 'manifest.json', 'slots.json', 'holdout_books.json')}
    for n in ('docs/harvest/round1/admitted.jsonl', 'docs/harvest/vouli/admitted.jsonl'):
        inputs[n] = sha(REPO / n)
    shared = defaultdict(list)
    for p in pages:
        shared[p['image_sha256']].append(p['id'])
    plan = dict(schema='t22-read-plan-1', binding=json.loads((round1.OUT / 'reads_d1/plan.json').read_text())['bindings']['docai'],
        pages=pages, page_count=len(pages), pages_fetched=len(manifest), pages_accepted=len(pages),
        max_calls=len(unique), max_cost_usd=len(unique)*.0015, cap_usd=CAP,
        shared_image_groups={k:v for k,v in shared.items() if len(v)>1}, inputs=inputs,
        gate_sha256=round1.GATE_SHA, quality_limits=data['quality_limits'], admission_sha256=ADMISSION_SHA,
        automatic_retries=False, vision_calls=0, owner_approval='T22, 15 Oct; read every accepted page; no owner look')
    frozen(OUT / 'plan.json', plan)
    print(json.dumps({k:plan[k] for k in ('pages_fetched','pages_accepted','max_calls','max_cost_usd')}), flush=True)
    return plan


class Round2Readers(vouli.VouliReaders):
    def __init__(self, plan, root=GOOGLE):
        super().__init__(plan, root=root)


def previous_page_hashes():
    """Include every earlier planned page, even one with no line records."""
    return {p['image_sha256'] for name in ('round1/reads_d1/plan.json',
        'round1/reads_rest/plan.json','vouli/plan.json')
        for p in json.loads((REPO/'docs/harvest'/name).read_text())['pages']}


def load_plan():
    vouli.check_frozen()
    plan = json.loads((OUT / 'plan.json').read_text())
    for name, digest in plan['inputs'].items():
        if sha(REPO / name) != digest:
            raise ValueError('frozen round2 input changed: ' + name)
    return plan


def run(plan):
    # Reuse the T21 implementation with explicit batch-local roots. Its reader
    # has no Vision instance, and verifies reservations/provider attempts/caches.
    old_google, old_out, old_readers = vouli.GOOGLE, vouli.OUT, vouli.VouliReaders
    try:
        vouli.GOOGLE, vouli.OUT = GOOGLE, OUT
        vouli.VouliReaders = lambda p: Round2Readers(p)
        vouli.run(plan)
    finally:
        vouli.GOOGLE, vouli.OUT, vouli.VouliReaders = old_google, old_out, old_readers


def read_watch():
    """Overlap reads of permanent accepted slots with the serial Anemi fetch.

    Each batch is frozen separately. All batches share the final image-SHA
    locks/budget; the final plan and validation must cover every reservation.
    """
    vouli.check_frozen()
    previous_hashes = previous_page_hashes()
    binding = json.loads((round1.OUT/'reads_d1/plan.json').read_text())['bindings']['docai']
    immutable = {relative(OUT/n):sha(OUT/n) for n in ('selection.json','books.json','holdout_books.json')}
    snapshot_dir = OUT/'read_snapshots'
    snapshot_dir.mkdir(exist_ok=True)
    while True:
        if any(sha(REPO/name)!=digest for name,digest in immutable.items()):
            raise ValueError('immutable selection/hold-out changed during acquisition')
        manifest = json.loads((OUT/'manifest.json').read_text())
        slots = json.loads((OUT/'slots.json').read_text())
        chosen = {(s['key'],s['accepted_page']) for s in slots if s['accepted_page'] is not None}
        reserved = {r['key'] for r in read_jsonl(GOOGLE/'budget.jsonl')}
        pages = [p for p in manifest if (p['key'],p['page']) in chosen and p['image_sha256'] not in reserved]
        complete = json.loads((OUT/'run_state.json').read_text()).get('complete',False)
        if previous_hashes & {p['image_sha256'] for p in pages}:
            raise ValueError('accepted snapshot was already read in an earlier wave')
        if len(pages)>=40 or (complete and pages):
            index = 1+max((int(p.stem) for p in snapshot_dir.glob('*.json') if p.stem.isdigit()),default=0)
            plan = dict(schema='t22-accepted-snapshot-1',binding=binding,pages=pages,cap_usd=CAP,max_calls=650,
                scope='permanently accepted slots only; final plan covers every reserved image hash',
                inputs=immutable,vision_calls=0,automatic_retries=False)
            frozen(snapshot_dir/f'{index:03d}.json',plan)
            print(f'frozen accepted snapshot {index:03d}: {len(pages)} pages',flush=True)
            run(plan)
        elif complete:
            print('all final accepted pages have reserved cached reads',flush=True)
            return
        else:
            time.sleep(20)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['select','fetch-gate','plan','read-watch','run','build','validate','publish'])
    mode = parser.parse_args().mode
    if mode == 'select':
        selection()
    elif mode == 'fetch-gate':
        fetch_gate()
    elif mode == 'plan':
        prepare_reads()
    elif mode == 'run':
        run(load_plan())
    elif mode == 'read-watch':
        read_watch()
    else:
        from scripts.harvest import round2_outputs
        getattr(round2_outputs, mode)(load_plan())


if __name__ == '__main__':
    main()

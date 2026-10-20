"""T27 robots-aware, cached Wikimedia collection. No Git writes or Vision calls."""
from __future__ import annotations

import hashlib
import fcntl
import json
from pathlib import Path
import time
import re
from email.utils import parsedate_to_datetime
import uuid
from urllib.parse import quote, urljoin, urlsplit, unquote
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/harvest/wikisource'
BULK = ROOT / 'docs/harvest/harvest_big/wikisource'
UA = 'GreekOCRToolkit-T27/1.0 (noncommercial OCR research)'
IMAGE_HOSTS = {'upload.wikimedia.org', 'thumb.wikimedia.org'}
HOSTS = {'el.wikisource.org', 'ru.wikisource.org', 'commons.wikimedia.org'} | IMAGE_HOSTS


class WikimediaHTTP:
    """One sequential client; >=1 second between every request, including redirects.

    Every redirect gets an independent robots check. Cached responses are bound
    to their body hash. A robots denial is evidence, never a network request.
    """
    def __init__(self, root=BULK / 'http', session=None, clock=time.time, sleep=time.sleep):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.session = session or requests.Session()
        self.session.headers['User-Agent'] = UA
        self.clock, self.sleep = clock, sleep
        self.state = self.root / 'rate.json'
        self.last = json.loads(self.state.read_text())['last'] if self.state.exists() else self.clock()

    def allowed(self, url):
        host = urlsplit(url).hostname
        if host not in HOSTS or urlsplit(url).scheme != 'https':
            raise ValueError('outside T27 network scope: ' + url)
        path = self.root / (host + '.robots.txt')
        if not path.exists():
            data, receipt = self.get('https://' + host + '/robots.txt', robots=True)
            if receipt['status'] != 200:
                raise ValueError('robots unavailable; fail closed')
            path.write_bytes(data)
        parser = RobotFileParser()
        parser.parse(path.read_text(encoding='utf-8-sig').splitlines())
        return parser.can_fetch(UA, url)

    def event(self, value):
        with (self.root / 'events.jsonl').open('a') as f:
            f.write(json.dumps(value, ensure_ascii=False) + '\n')

    def get(self, url, *, robots=False, redirects=0, refresh=False, image=False):
        host = urlsplit(url).hostname
        if host not in HOSTS or urlsplit(url).scheme != 'https':
            raise ValueError('outside T27 network scope: ' + url)
        if not robots and not self.allowed(url):
            self.event(dict(url=url, status='robots_disallowed', time=self.clock(), user_agent=UA))
            raise PermissionError('robots disallows ' + url)
        key = hashlib.sha256(url.encode()).hexdigest()
        meta, body = self.root / (key + '.json'), self.root / (key + '.html')
        # Retain every failed response. A retry must reach the server rather
        # than replay the first cached 429; successful responses remain cached.
        if refresh and meta.exists():
            key += '.' + uuid.uuid4().hex
            meta, body = self.root / (key + '.json'), self.root / (key + '.html')
        if meta.exists() and body.exists():
            receipt = json.loads(meta.read_text()); data = body.read_bytes()
            if hashlib.sha256(data).hexdigest() != receipt['sha256']:
                raise ValueError('HTTP cache changed')
        else:
            with (self.root / 'request.lock').open('a') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                state = json.loads(self.state.read_text()) if self.state.exists() else {}
                self.last = max(self.last, state.get('last', 0))
                delay = max(0, 1.05 - (self.clock() - self.last))
                if image:
                    delay = max(delay, 3.05 - (self.clock() - state.get('image_last', 0)))
                self.sleep(delay)
                started = self.clock()
                self.last = started
                state['last'] = started
                if image:
                    state['image_last'] = started
                self.state.write_text(json.dumps(state))
                try:
                    r = self.session.get(url, timeout=60, allow_redirects=False)
                except requests.RequestException as exc:
                    # A transport failure consumes an image attempt too.
                    # Never persist exception text that may contain secrets.
                    from types import SimpleNamespace
                    r = SimpleNamespace(status_code=599, content=b'', headers={},
                                        error_class=type(exc).__name__)
            data = r.content
            receipt = dict(url=url, status=r.status_code, headers=dict(r.headers),
                           sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
                           started_at=started, user_agent=UA, image_request=image,
                           body_path=str(body.relative_to(ROOT)) if body.is_relative_to(ROOT) else str(body))
            if getattr(r, 'error_class', None):
                receipt['error_class'] = r.error_class
            body.write_bytes(data); meta.write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
            self.event(receipt)
        if receipt['status'] in (301, 302, 303, 307, 308):
            if redirects >= 5:
                raise ValueError('redirect limit')
            target = urljoin(url, next(v for k, v in receipt['headers'].items() if k.lower() == 'location'))
            return self.get(target, redirects=redirects + 1, refresh=refresh, image=image)
        return data, receipt

    def page(self, lang, title):
        url = 'https://' + lang + '.wikisource.org/wiki/' + quote(title.replace(' ', '_'), safe='/:')
        data, receipt = self.get(url)
        return BeautifulSoup(data, 'html.parser'), receipt


def links(soup, base):
    return [(a.get_text(' ', strip=True), unquote(urljoin(base, a['href'])))
            for a in soup.select('#mw-content-text a[href]')]


def index_metadata(soup, url, lang):
    fields = {}
    for tr in soup.select('#mw-content-text tr'):
        cells = tr.find_all(['th', 'td'], recursive=False)
        if len(cells) == 2:
            fields[cells[0].get_text(' ', strip=True)] = cells[1].get_text(' ', strip=True)
    years = re.findall(r'\b(1[789]\d{2})\b', fields.get('Έτος', fields.get('Год', '')))
    year = int(years[0]) if len(set(years)) == 1 else None
    pages = []
    for a in soup.select('.prp-index-pagelist a[href]'):
        quality = next((int(c[-1]) for c in a.get('class', []) if re.fullmatch('quality[0-4]', c)), None)
        if quality is not None and quality >= (3 if lang == 'el' else 4):
            purl = urljoin(url, a['href'])
            pages.append(dict(page=int(purl.rsplit('/', 1)[1]), url=purl, quality=quality))
    image = next((i.get('src') for i in soup.select('#mw-content-text img[src]')
                  if '/commons/thumb/' in i['src'] and re.search(r'\.(djvu|pdf)/', i['src'], re.I)), None)
    return dict(lang=lang, index_url=url, title=fields.get('Τίτλος', fields.get('Название', '')),
                year=year, fields=fields, eligible_pages=pages, thumbnail=image)


def discover():
    from greekocr.harvest.readers import atomic
    http = WikimediaHTTP()
    categories = {'el': ['Κατηγορία:Μεταγραφές που έχουν εγκριθεί', 'Κατηγορία:Μεταγραφές που έχουν ελεγχθεί',
                         'Κατηγορία:Μεταγραφές που δεν έχουν ελεγχθεί', 'Κατηγορία:Μεταγραφές με αρχείο που χρειάζεται έλεγχο'],
                  'ru': ['Категория:Индекс - Закончено', 'Категория:Индекс - Нужно проверить']}
    candidates, selected, audits = {}, [], []
    for lang in ['el', 'ru']:
        prefix = 'Μεταγραφή:' if lang == 'el' else 'Индекс:'
        urls = []
        for cat in categories[lang]:
            soup, receipt = http.page(lang, cat)
            for _, url in links(soup, receipt['url']):
                title = url.split('/wiki/')[-1]
                if title.startswith(prefix) and re.search(r'\.(djvu|pdf)$', title, re.I) and url not in urls:
                    # Clearly dated out-of-period items cannot qualify. Unknown
                    # titles still get their edition year from the index itself.
                    dates = [int(y) for y in re.findall(r'(?<!\d)(1[5-9]\d{2}|20\d{2})(?!\d)', title)]
                    if dates and not any(1850 <= y <= 1935 for y in dates):
                        continue
                    urls.append(url)
        candidates[lang] = urls
        atomic(OUT / 'discovery_candidates.json', candidates)
        for url in urls:
            if sum(b['lang'] == lang for b in selected) >= (20 if lang == 'el' else 10):
                break
            soup, receipt = http.page(lang, url.split('/wiki/')[1])
            b = index_metadata(soup, receipt['url'], lang)
            reasons = []
            if b['year'] is None or not 1850 <= b['year'] <= 1935:
                reasons.append('edition_year')
            if len(b['eligible_pages']) < (15 if lang == 'el' else 10):
                reasons.append('insufficient_proofread_pages')
            if not b['thumbnail']:
                reasons.append('no_commons_scan')
            if not reasons:
                # The Commons description is separately frozen, including the
                # actual PD statement. Index status alone is never a licence.
                filename = unquote(b['thumbnail'].split('/commons/thumb/')[1].split('/')[2])
                commons = 'https://commons.wikimedia.org/wiki/File:' + quote(filename, safe=':')
                data, cr = http.get(commons)
                cs = BeautifulSoup(data, 'html.parser')
                rights = cs.select_one('#Licensing') or cs.select_one('#license')
                pd = cs.select_one('a[href*="creativecommons.org/publicdomain/mark"]')
                templates = sorted({n['id'] for n in cs.select('[id]') if n['id'].startswith(('PD-', 'Cc-'))})
                if cr['status'] != 200 or not pd:
                    reasons.append('public_domain_statement_unverified')
                else:
                    b.update(scan_file=filename, commons_url=commons, commons_receipt=cr,
                             licence='Public domain (Commons Public Domain Mark 1.0); ' + ', '.join(templates),
                             licence_url=pd['href'], key=hashlib.sha256((lang + ':' + filename).encode()).hexdigest()[:8],
                             index_receipt=receipt)
                    selected.append(b)
            audits.append(dict(index_url=url, lang=lang, year=b['year'], eligible_pages=len(b['eligible_pages']), reasons=reasons))
            atomic(OUT / 'discovery_audit.json', audits)
            atomic(OUT / 'source_books.json', selected)
            print(f"{lang} {len([x for x in selected if x['lang']==lang])}: {b['year']} {len(b['eligible_pages'])} {b['title'][:55]} {reasons}", flush=True)
    return selected


def freeze_selection():
    import random
    from greekocr.harvest import wikisource as policy
    from greekocr.harvest.readers import atomic
    from scripts.harvest.round1_reads import frozen
    from scripts.harvest import vouli, round1
    vouli.check_frozen()
    books = json.loads((OUT / 'source_books.json').read_text())
    if [sum(b['lang'] == lang for b in books) for lang in ('el', 'ru')] != [20, 10]:
        raise ValueError('T27 requires exactly 20 Greek and 10 Russian selected works')
    pages = []
    for b in books:
        rng = random.Random('20261015:' + b['key'])
        eligible = sorted(b['eligible_pages'], key=lambda p: p['page'])
        count = 15 if b['lang'] == 'el' else 10
        # Spread a seeded draw through the eligible source pages; never select
        # from OCR content or OCR confidence.
        chosen = sorted(rng.sample(eligible, count), key=lambda p: p['page'])
        for p in chosen:
            pages.append(dict(p, id=f"{b['key']}-p{p['page']:06d}", key=b['key'], book=b['index_url'],
                lang=b['lang'], title=b['title'], year=b['year'], decade=b['year'] // 10 * 10,
                origin='wikisource', source='wikisource_' + b['lang'],
                source_url=p['url'], licence=b['licence'], licence_url=b['licence_url'],
                attribution=b['title'] + '; Wikisource proofread contributors; Commons scan ' + b['scan_file'],
                human_transcription_licence='CC-BY-SA-4.0 (Wikisource contributor text)',
                scan_file=b['scan_file'], index_url=b['index_url'], thumbnail=b['thumbnail'],
                volume=None, volume_page=p['page'], read_batch='wikisource', train_pool_eligible=False))
    frozen(OUT / 'selected_pages.json', pages)
    frozen(OUT / 'holdout_books.json', policy.splits(books))
    frozen(OUT / 'selection.json', dict(schema='t27-selection-1', seed=20261015, books=books,
        page_count=400, pages_by_language={'el': 300, 'ru': 100}, discovery='HTML fallback: robots denies standard API',
        gate_sha256=round1.GATE_SHA, admission_sha256=vouli.ADMISSION_SHA,
        quality_limits=json.loads((round1.OUT / 'selection.json').read_text())['quality_limits'],
        train_allowed=False, cap_usd=.80, docai_max_cost_usd=.60,
        source_books_sha256=vouli.sha(OUT / 'source_books.json')))
    return pages


def transcribe():
    from greekocr.harvest import wikisource as policy
    from greekocr.harvest.readers import atomic
    http = WikimediaHTTP()
    pages = freeze_selection()
    for i, p in enumerate(pages, 1):
        saved = OUT / 'transcriptions' / (p['id'] + '.json')
        if not saved.exists():
            data, receipt = http.get(p['url'] + '?action=raw')
            if receipt['status'] != 200:
                raise RuntimeError('transcription fetch failed: ' + str(receipt['status']))
            text = data.decode('utf-8')
            parsed = policy.strip_wikitext(text)
            if parsed['proofread_level'] is None or parsed['proofread_level'] < (3 if p['lang'] == 'el' else 4):
                raise ValueError('live proofread level changed: ' + p['id'])
            raw = BULK / 'wikitext' / (p['id'] + '.txt')
            raw.parent.mkdir(parents=True, exist_ok=True)
            raw.write_bytes(data)
            atomic(saved, dict(page=p, raw_path=str(raw.relative_to(ROOT)), receipt=receipt, **parsed))
        if i % 10 == 0:
            print(f'transcription {i}/{len(pages)}', flush=True)


def thumbnail_url(page, host='upload.wikimedia.org', width=3840):
    """Derive the Commons URL from the saved, decoded file title."""
    if host not in IMAGE_HOSTS:
        raise ValueError('thumbnail host requires explicit authorization: ' + host)
    name = page['scan_file'].removeprefix('File:').replace(' ', '_')
    if not re.search(r'\.(pdf|djvu)$', name, re.I) or '/' in name:
        raise ValueError('expected a saved PDF/DjVu file title')
    number = int(page['page'])
    if number < 1 or width not in (2500, 1600, 3840, 1920, 1280):
        raise ValueError('invalid page number or unauthorized thumbnail width')
    if page.get('url') and int(page['url'].rsplit('/', 1)[1]) != number:
        raise ValueError('scan page differs from saved Page title')
    digest = hashlib.md5(name.encode('utf-8')).hexdigest()
    encoded = quote(name, safe='')
    return f'https://{host}/wikipedia/commons/thumb/{digest[0]}/{digest[:2]}/{encoded}/page{number}-{width}px-{encoded}.jpg'


def resolve_thumbnail(http, page, width):
    """No image API or HTML requests: reuse the frozen Commons provenance.

    The selection's Commons thumbnail is evidence of its hosting location,
    not a template for the URL. Local hosting requires explicit file-page
    evidence and is unavailable in this Commons-only saved selection.
    """
    from greekocr.harvest.readers import atomic
    saved = OUT / 'image_resolution' / f"{page['id']}-{width}.json"
    if '/commons/thumb/' in page.get('thumbnail', ''):
        result = dict(status='resolved', method='deterministic_commons_md5',
                      url=thumbnail_url(page, width=width), width=width,
                      network_request_sent=False, hosting_evidence='saved selection Commons thumbnail')
    else:
        result = dict(status='hosting_unavailable', width=width,
                      network_request_sent=False)
    atomic(saved, result)
    return result


def retry_delay(headers, attempt, *, now=None):
    """429 Retry-After (seconds or HTTP-date) takes precedence over backoff."""
    value = next((v for k, v in headers.items() if k.lower() == 'retry-after'), '0')
    try:
        retry_after = float(value)
    except (ValueError, TypeError):
        try:
            date = parsedate_to_datetime(value)
            retry_after = date.timestamp() - (time.time() if now is None else now)
        except (ValueError, TypeError, OverflowError):
            retry_after = 0
    return max(10, retry_after, min(300, 10 * 2 ** (attempt - 1)))


def fetch_scan(http, page, *, standard_width=True):
    """At most six image attempts per page, persisted across interruptions."""
    from greekocr.harvest.readers import atomic
    saved = OUT / 'image_attempts' / (page['id'] + '.json')
    state = json.loads(saved.read_text()) if saved.exists() else dict(page_id=page['id'], attempts=[])
    if state.get('status') == 'obtained':
        receipt = state['attempts'][-1]['receipt']
        data = (ROOT / receipt['body_path']).read_bytes()
        if hashlib.sha256(data).hexdigest() != receipt['sha256']:
            raise ValueError('saved image response changed')
        return data, state
    if state.get('status') in ('http_permanent_failure', 'unsupported_thumbnail_width'):
        if not standard_width or state['attempts'][-1]['width'] in (3840, 1920, 1280):
            return None, state
    while len(state['attempts']) < 6:
        if state.get('next_attempt_at'):
            http.sleep(max(0, state['next_attempt_at'] - http.clock()))
        count429 = sum(a['receipt']['status'] == 429 for a in state['attempts'])
        fallback404 = any(a['width'] == 2500 and a['receipt']['status'] == 404 for a in state['attempts'])
        if standard_width:
            # Only a permanent 400/404 moves to the next approved width.
            # Historical 2500/1600 receipts remain in the six-attempt total.
            failed_widths = {a['width'] for a in state['attempts']
                             if a['receipt']['status'] in (400, 404)}
            width = next((w for w in (3840, 1920, 1280) if w not in failed_widths), None)
            if width is None:
                state.update(status='http_permanent_failure', finished_at=http.clock())
                atomic(saved, state)
                return None, state
        else:
            width = 1600 if count429 >= 2 or fallback404 else 2500
        resolved = resolve_thumbnail(http, page, width)
        if resolved['status'] != 'resolved':
            state.update(status=resolved['status'], resolution=resolved)
            atomic(saved, state)
            return None, state
        data, receipt = http.get(resolved['url'], refresh=True, image=True)
        state['attempts'].append(dict(width=width, resolution=resolved, receipt=receipt))
        state.pop('next_attempt_at', None)
        if receipt['status'] == 200:
            state['status'] = 'obtained'
            atomic(saved, state)
            return data, state
        if standard_width and receipt['status'] in (400, 404) and width != 1280:
            state['status'] = 'fallback_pending'
            atomic(saved, state)
            continue
        if not standard_width and receipt['status'] == 400 and b'Use thumbnail sizes listed' in data:
            state.update(status='unsupported_thumbnail_width', finished_at=http.clock())
            atomic(saved, state)
            return None, state
        if receipt['status'] == 404 and width == 2500:
            state['status'] = 'fallback_404_pending'
            atomic(saved, state)
            continue
        if receipt['status'] != 429 and receipt['status'] < 500:
            state['status'] = 'http_permanent_failure'
            atomic(saved, state)
            return None, state
        delay = retry_delay(receipt['headers'], len(state['attempts']), now=http.clock())
        state.update(status='retry_pending', next_attempt_at=http.clock() + delay)
        atomic(saved, state)
        if len(state['attempts']) < 6:
            print(f"image retry {page['id']} {len(state['attempts'])}/6 HTTP {receipt['status']}; wait {delay:.0f}s", flush=True)
    state.update(status='retry_exhausted', finished_at=http.clock())
    state.pop('next_attempt_at', None)
    atomic(saved, state)
    return None, state


def delivery_image(data, *, fallback=False):
    import io
    from PIL import Image
    with Image.open(io.BytesIO(data)) as original:
        if original.width < (1280 if fallback else 2000):
            raise ValueError('Commons image below the permitted request width')
        image, dpi = original.convert('L'), original.info.get('dpi')
    served_size = image.size
    image.thumbnail((3500, 3500), Image.Resampling.LANCZOS)
    return image, dpi, served_size


def local_receipts(selected):
    """Bind the coordinator's local scans to the frozen selection, offline.

    A failed receipt is terminal for this run. Missing, duplicate or changed
    inputs are errors, never reasons to try Wikimedia again.
    """
    from scripts.harvest import vouli
    receipts_path = BULK / 'thumbs/receipts.jsonl'
    rows = [json.loads(line) for line in receipts_path.read_text().splitlines() if line.strip()]
    receipts = {r['page_id']: r for r in rows}
    if len(receipts) != len(rows) or set(receipts) != {p['id'] for p in selected}:
        raise ValueError('local receipt scope must equal the frozen page selection exactly')
    for p in selected:
        r = receipts[p['id']]
        if r.get('failed'):
            continue
        path = BULK / 'thumbs' / (p['id'] + '.jpg')
        if r['width'] not in (3840, 1920, 1280):
            raise ValueError('unexpected coordinator thumbnail width')
        if r['url'] != thumbnail_url(p, width=r['width']):
            raise ValueError('local receipt scan URL differs from the selected scan page')
        if path.stat().st_size != r['bytes'] or vouli.sha(path) != r['sha256']:
            raise ValueError('local JPEG size/hash differs from coordinator receipt: ' + p['id'])
    return receipts


def gate_local_page(task):
    """Convert one supplied JPEG and apply T21's frozen gate without filtering."""
    from greekocr.harvest.readers import atomic
    from scripts.harvest import vouli
    p, receipt, receipt_sha = task
    saved = OUT / 'gates' / (p['id'] + '.json')
    if saved.exists():
        page = json.loads(saved.read_text())
        if (page.get('local_thumbnail_receipt') != receipt or
                page.get('local_receipts_sha256') != receipt_sha or
                vouli.sha(ROOT / page['image']) != page['image_sha256']):
            raise ValueError('local gate resume input changed: ' + p['id'])
        return page
    path = BULK / 'thumbs' / (p['id'] + '.jpg')
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != receipt['sha256']:
        raise ValueError('JPEG changed after local preflight')
    image, original_dpi, served_size = delivery_image(data, fallback=receipt['width'] < 2000)
    image_path = BULK / 'images' / f"{p['key']}-{p['page']:06d}.png"
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(image_path, dpi=(200, 200), compress_level=3)
    g = vouli.gate_image(image_path, vouli.WORKER_STACK, vouli.WORKER_GATE, vouli.WORKER_LIMITS)
    page = dict(p, image=str(image_path.relative_to(ROOT)), image_sha256=vouli.sha(image_path),
        width=image.width, height=image.height, dpi=200,
        dpi_scope='nominal delivery metadata; no physical size inferred',
        source_dpi=original_dpi, served_size=list(served_size),
        scale_x=image.width / served_size[0], scale_y=image.height / served_size[1],
        grayscale=True, thumbnail_receipt=receipt, local_thumbnail_receipt=receipt,
        local_thumbnail_path=str(path.relative_to(ROOT)), local_receipts_sha256=receipt_sha,
        requested_width=receipt['width'], gate=g, harvest_accepted=g['accepted'])
    atomic(saved, page)
    return page


def import_local():
    """T27e: use only coordinator JPEGs; this entry point has no HTTP client."""
    from collections import Counter
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import multiprocessing
    from greekocr.harvest.readers import atomic
    from scripts.harvest import vouli
    vouli.check_frozen()
    selected = json.loads((OUT / 'selected_pages.json').read_text())
    receipts = local_receipts(selected)
    receipt_path = BULK / 'thumbs/receipts.jsonl'
    receipt_sha = vouli.sha(receipt_path)
    tasks = [(p, receipts[p['id']], receipt_sha) for p in selected if not receipts[p['id']].get('failed')]
    unavailable = [dict(page_id=p['id'], lang=p['lang'], receipt=receipts[p['id']])
                   for p in selected if receipts[p['id']].get('failed')]
    atomic(OUT / 'unavailable_pages.json', unavailable)
    limits = json.loads((OUT / 'selection.json').read_text())['quality_limits']
    manifest = []
    with ProcessPoolExecutor(max_workers=3, mp_context=multiprocessing.get_context('spawn'),
                             initializer=vouli.init_gate_worker, initargs=(limits,)) as pool:
        futures = [pool.submit(gate_local_page, task) for task in tasks]
        for future in as_completed(futures):
            manifest.append(future.result())
            if len(manifest) % 10 == 0 or len(manifest) == len(tasks):
                print(f"local images/gates {len(manifest)}/{len(tasks)}; flagged {sum(not p['gate']['accepted'] for p in manifest)}", flush=True)
    order = {p['id']: i for i, p in enumerate(selected)}
    manifest.sort(key=lambda p: order[p['id']])
    atomic(OUT / 'manifest.json', manifest)
    atomic(OUT / 'acquisition_summary.json', dict(schema='t27e-local-acquisition-1',
        selected_pages=len(selected), obtained=len(manifest), missing=len(unavailable),
        obtained_share=len(manifest) / len(selected), finished=True,
        image_method='coordinator_local_jpeg', image_api_calls=0, wikimedia_requests=0,
        text_refetches=0, local_receipts_path=str(receipt_path.relative_to(ROOT)),
        local_receipts_sha256=receipt_sha, local_jpeg_hashes_checked=len(tasks),
        unavailable_pages=[r['page_id'] for r in unavailable],
        requested_widths=dict(Counter(str(p['requested_width']) for p in manifest)),
        gate_flagged=sum(not p['gate']['accepted'] for p in manifest),
        gate_policy='flag only; every obtained page goes to Document AI',
        blocked_by_size_policy=False, shortfall_exception_applied=False))


def acquire(*, standard_width=True, finish_on_shortfall=True):
    import io
    from PIL import Image
    from greekocr.harvest.pipeline import FrozenStack
    from greekocr.harvest.readers import atomic
    from scripts.harvest import vouli, round1
    vouli.check_frozen()
    selection = json.loads((OUT / 'selection.json').read_text())
    stack = gate = None
    http = WikimediaHTTP(); manifest = []
    interrupted_by_size_policy = False
    shortfall_stop = False
    for i, p in enumerate(json.loads((OUT / 'selected_pages.json').read_text()), 1):
        saved = OUT / 'gates' / (p['id'] + '.json')
        if saved.exists():
            page = json.loads(saved.read_text())
            if vouli.sha(ROOT / page['image']) != page['image_sha256']:
                raise ValueError('native page image changed')
        else:
            data, attempts = fetch_scan(http, p, standard_width=standard_width)
            if data is None:
                print(f"image unavailable {i}/400 {p['id']}: {attempts['status']}", flush=True)
                if attempts['status'] == 'unsupported_thumbnail_width':
                    interrupted_by_size_policy = True
                    break
                if finish_on_shortfall and attempts['status'] == 'retry_exhausted' and len(manifest) < 200:
                    # The coordinator explicitly allows finishing below 50%
                    # after the complete backoff schedule. Keep the untried
                    # scope explicit; do not call it 400 exhausted schedules.
                    shortfall_stop = True
                    break
                continue
            receipt = attempts['attempts'][-1]['receipt']
            image, original_dpi, served_size = delivery_image(data,
                fallback=attempts['attempts'][-1]['width'] < 2000)
            image_path = BULK / 'images' / f"{p['key']}-{p['page']:06d}.png"
            image_path.parent.mkdir(parents=True, exist_ok=True)
            # No invented physical page size or upsampling. 200 dpi is the
            # nominal delivery grid; original physical dpi stays explicit.
            image.save(image_path, dpi=(200, 200), compress_level=3)
            if stack is None:
                stack = FrozenStack(round1.PILOT / 'pilot/_stack_52cee3b')
                gate = round1.load_gate()
            g = vouli.gate_image(image_path, stack, gate, selection['quality_limits'])
            page = dict(p, image=str(image_path.relative_to(ROOT)), image_sha256=vouli.sha(image_path),
                width=image.width, height=image.height, dpi=200, dpi_scope='nominal delivery metadata; no physical size inferred',
                source_dpi=original_dpi, served_size=served_size, grayscale=True, thumbnail_receipt=receipt,
                requested_width=attempts['attempts'][-1]['width'],
                gate=g, harvest_accepted=g['accepted'])
            atomic(saved, page)
        manifest.append(page)
        atomic(OUT / 'manifest.json', manifest)
        if i % 10 == 0:
            print(f'images/gates {i}/400', flush=True)
    atomic(OUT / 'manifest.json', manifest)
    states = [json.loads(f.read_text()) for f in (OUT / 'image_attempts').glob('*.json')]
    atomic(OUT / 'acquisition_summary.json', dict(selected_pages=400, obtained=len(manifest),
        missing=400-len(manifest), obtained_share=len(manifest)/400,
        attempted_pages=sum(bool(s['attempts']) for s in states),
        image_attempts=sum(len(s['attempts']) for s in states),
        finished=not interrupted_by_size_policy, image_method='deterministic_commons_md5', image_api_calls=0,
        requested_primary_width=3840 if standard_width else 2500,
        standard_width_authorized=standard_width,
        blocked_by_size_policy=interrupted_by_size_policy,
        shortfall_exception_applied=shortfall_stop,
        shortfall_scope='collection stopped after a page exhausted its retry schedule; remaining pages are not claimed exhausted' if shortfall_stop else None,
        retry_exhausted_pages=sum(s['status'] == 'retry_exhausted' for s in states),
        retry_pending_pages=sum(s['status'] == 'retry_pending' for s in states),
        supported_width_attempted_pages=sum(any(a['width'] in (3840, 1920, 1280) for a in s['attempts']) for s in states),
        supported_width_attempts=sum(a['width'] in (3840, 1920, 1280) for s in states for a in s['attempts']),
        status_counts=dict(__import__('collections').Counter(s['status'] for s in states))))


def prepare_plan():
    import copy
    from scripts.harvest import vouli, round1
    from scripts.harvest.round1_reads import frozen
    vouli.check_frozen()
    pages = json.loads((OUT / 'manifest.json').read_text())
    acquisition = json.loads((OUT / 'acquisition_summary.json').read_text())
    if not acquisition['finished'] or not pages:
        raise ValueError('acquisition must finish with at least one image before Google reads')
    for p in pages:
        transcription = OUT / 'transcriptions' / (p['id'] + '.json')
        if not transcription.exists() or vouli.sha(ROOT / p['image']) != p['image_sha256']:
            raise ValueError('image/transcription prerequisite missing or changed')
    calls = len(vouli.unique_call_pages(pages))
    if calls * 1500 > 800_000:
        raise ValueError('USD 0.80 cap exceeded')
    binding = copy.deepcopy(json.loads((round1.OUT / 'reads_d1/plan.json').read_text())['bindings']['docai'])
    # Keep T21's fixed reader; language is selected by source, not corrected
    # against the gold transcription. Both languages get no hints.
    binding['options']['ocrConfig']['hints']['languageHints'] = []
    inputs = {str(p.relative_to(ROOT)): vouli.sha(p) for p in [OUT / n for n in
        ('source_books.json', 'selected_pages.json', 'holdout_books.json', 'selection.json', 'manifest.json')]}
    inputs.update({str(p.relative_to(ROOT)): vouli.sha(p) for p in (BULK / 'wikitext').glob('*.txt')})
    if acquisition.get('image_method') == 'coordinator_local_jpeg':
        inputs[str(BULK.relative_to(ROOT) / 'thumbs/receipts.jsonl')] = vouli.sha(BULK / 'thumbs/receipts.jsonl')
    plan = dict(schema='t27-plan-1', pages=pages, page_count=len(pages), max_calls=calls,
        pages_rendered=len(pages), pages_accepted=sum(p['harvest_accepted'] for p in pages),
        cap_usd=.80, max_cost_usd=calls * .0015, binding=binding, inputs=inputs,
        gate_sha256=round1.GATE_SHA, admission_sha256=vouli.ADMISSION_SHA,
        automatic_retries=False, vision_calls=0, train_allowed=False,
        raw_storage='Google response with document.pages[*].image.content removed before persistence',
        owner_approval='T27e: read supplied local selected pages including gate failures, USD 0.80 maximum',
        acquisition=acquisition)
    frozen(OUT / 'plan.json', plan)
    return plan


def load_plan():
    from scripts.harvest import vouli
    vouli.check_frozen()
    plan = json.loads((OUT / 'plan.json').read_text())
    for path, digest in plan['inputs'].items():
        if vouli.sha(ROOT / path) != digest:
            raise ValueError('frozen plan input changed: ' + path)
    return plan


def read():
    from scripts.harvest import vouli
    from scripts.harvest import compact_parliament_raw as archive
    plan = load_plan()
    class WikisourceReaders(vouli.VouliReaders):
        def __init__(self, value):
            super().__init__(value, root=BULK / 'google')
            # Remove the embedded raster before DocAIReader writes any raw
            # response. Geometry, text and confidence fields remain intact.
            self.docai._transport = compact_docai_transport
    old = vouli.OUT, vouli.VouliReaders
    try:
        vouli.OUT, vouli.VouliReaders = OUT, WikisourceReaders
        vouli.run(plan)
    finally:
        vouli.OUT, vouli.VouliReaders = old
    archive.compact(BULK / 'google', image_paths={p['image_sha256']: ROOT / p['image'] for p in plan['pages']})


def strip_response_images(raw):
    for page in raw.get('document', {}).get('pages', []):
        page.get('image', {}).pop('content', None)
    return raw


def compact_docai_transport(*args, **kwargs):
    response = requests.post(*args, **kwargs)
    class Response:
        status_code, headers = response.status_code, response.headers
        @property
        def text(self):
            return response.text
        def json(self):
            return strip_response_images(response.json())
    return Response()


if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'discover':
        discover()
        raise SystemExit
    if sys.argv[1] == 'transcribe':
        transcribe()
        raise SystemExit
    if sys.argv[1] in {'acquire', 'import_local', 'prepare_plan', 'read'}:
        if sys.argv[1] == 'acquire':
            acquire(finish_on_shortfall='--exhaust-all-pages' not in sys.argv[2:])
        else:
            globals()[sys.argv[1]]()
        raise SystemExit
    http = WikimediaHTTP()
    for title in sys.argv[2:]:
        soup, receipt = http.page(sys.argv[1], title)
        print(json.dumps(dict(receipt=receipt, text=soup.select_one('#mw-content-text').get_text(' ', strip=True)[:12000],
                              links=links(soup, receipt['url'])[:160]), ensure_ascii=False), flush=True)

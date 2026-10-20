"""T25 resumable three-part collection. Only acquire/read modes use network."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import multiprocessing
from pathlib import Path
import shutil
import time
from urllib.parse import urlsplit, urljoin

from PIL import Image
import pypdfium2 as pdfium
import requests

from greekocr.harvest import mixed as policy
from greekocr.harvest.pipeline import FrozenStack
from greekocr.harvest.readers import atomic, read_jsonl
from scripts.harvest import round1, round2, vouli
from scripts.harvest.round1_reads import frozen

REPO = round1.ROOT
OUT = REPO/'docs/harvest/mixed'
BULK = REPO/'docs/harvest/harvest_big/mixed'
GOOGLE = BULK/'google'
CAP = 2.00
ADMISSION_SHA = vouli.ADMISSION_SHA
sha, relative = vouli.sha, vouli.relative
PARTS = ('A','B','C')
PRIOR_WAVES = ('round1','vouli','round2','parliament','openarchives')


def select():
    vouli.check_frozen()
    OUT.mkdir(parents=True,exist_ok=True)
    frozen(OUT/'git_before.json',round1.git_snapshot())
    catalogue = read_jsonl(round2.CATALOGUE)
    prior = {b['book'] for name in ('round1','round2')
        for b in json.loads((REPO/f'docs/harvest/{name}/selection.json').read_text())['books']}
    early, early_inputs = round2.early_exclusions()
    excluded = prior | early
    fm = round1.fetch_module()
    candidates, rejected = [], Counter()
    for row in catalogue:
        ok, reason = policy.anemi_eligible(row,excluded)
        if not ok:
            rejected[reason] += 1
            continue
        plans = fm.build_plan([row])
        if not plans or plans[0]['pages'] is None:
            rejected['no_valid_page_plan'] += 1
            continue
        cat = plans[0]
        try:
            picks = policy.spread_positions(cat['pages'],12,row['document_id'])
        except ValueError:
            rejected['too_few_pages'] += 1
            continue
        key = fm.record_key(row['document_id'])
        candidates.append(dict(book=row['document_id'],key=key,id6=key[:6],part='A',
            title=row['title'],year=row['year'],decade=row['year']//10*10,pages=cat['pages'],
            catalogue=cat,positions=picks,allocation=12,source_url=row['record_url'],
            attribution='Anemi Digital Library, University of Crete',
            licence='anemi-research-internal',source='anemi_mixed',origin='anemi'))
    books = policy.anemi_draw(candidates)
    if len({b['key'][:8] for b in books}) != len(books):
        raise ValueError('crop key collision')
    for i,b in enumerate(books,1):
        b['catalogue']['rank'] = i
    raw = json.loads((REPO/'docs/harvest/openarchives/wave5_candidates.json').read_text())
    repos, failures = [], Counter()
    for row in raw:
        try:
            repos.append(policy.repository_candidate(row))
        except ValueError as exc:
            failures[str(exc)] += 1
    repo_order = policy.repository_order(repos)
    inputs = {relative(REPO/f'docs/harvest/{n}/selection.json'):sha(REPO/f'docs/harvest/{n}/selection.json') for n in ('round1','round2')}
    inputs.update({str(round2.CATALOGUE):sha(round2.CATALOGUE),
        'docs/harvest/openarchives/wave5_candidates.json':sha(REPO/'docs/harvest/openarchives/wave5_candidates.json'),**early_inputs})
    frozen(OUT/'selection.json',dict(schema='t25-selection-1',seed=policy.SEED,books=books,
        excluded=sorted(excluded),exclusion_counts=dict(round1_round2=len(prior),early=len(early)),
        eligible_anemi=len(candidates),anemi_rejections=dict(rejected),
        repository_candidates=len(repo_order),repository_rejections=dict(failures),
        quality_limits=json.loads((round1.OUT/'selection.json').read_text())['quality_limits'],inputs=inputs))
    frozen(OUT/'repository_order.json',repo_order)
    frozen(OUT/'books_A.json',books)
    frozen(OUT/'holdout_A.json',policy.select_holdout(books))
    atomic(OUT/'run_state.json',dict(started_at=datetime.now(timezone.utc).isoformat(),parts={}))
    print(json.dumps(dict(anemi=len(books),eligible=len(candidates),repositories=len(repo_order))),flush=True)


def gate_init(limits):
    global STACK,GATE,LIMITS
    import onnxruntime as ort
    ort.disable_telemetry_events()
    STACK,GATE,LIMITS = FrozenStack(round1.PILOT/'pilot/_stack_52cee3b'),round1.load_gate(),limits


def anemi_paths(book, number):
    volume,local = round1.locate(book,number)
    pdf = BULK/'records'/book['key']/volume['volume_id']/f'page-{local:06d}.pdf'
    return volume,local,pdf,BULK/'images'/f"{book['key']}-{number:06d}.png"


def replay_slots(books,gates,failed):
    slots,used=round2.replay_slots(books,gates,failed)
    for slot in slots:
        for step in slot['chain']:
            failure=failed.get(f"{slot['key']}:{step['page']}",{})
            if step['state']=='fetch_failed' and failure.get('reason')=='source_volume_unavailable':
                step.update(state='source_unavailable',reasons=['source_volume_unavailable'])
    return slots,used


def page_record(book, number, image, gate, **extra):
    names = ('book','key','id6','title','year','decade','source_url','attribution','licence','source','origin','part')
    page = {k:book[k] for k in names}
    with Image.open(image) as im:
        width,height = im.size
    page.update(id=f"{book['key']}-p{number:06d}",page=number,image=relative(image),
        image_sha256=gate['image_sha256'],width=width,height=height,dpi=200,grayscale=True,
        read_batch='mixed',gate=gate,harvest_accepted=gate['accepted'],**extra)
    atomic(OUT/'gates'/(page['id']+'.json'),page)
    return page


def gate_anemi(task):
    book,number,receipt = task
    volume,local,pdf,image = anemi_paths(book,number)
    image.parent.mkdir(parents=True,exist_ok=True)
    g = round1.gate_pdf(pdf,image,STACK,GATE,LIMITS)
    return page_record(book,number,image,g,volume=volume['volume_id'],volume_page=local,
        pdf=relative(pdf),pdf_sha256=sha(pdf),fetch_receipt=receipt)


def part_checkpoint(part, books, gates, failed, complete=False):
    slots,_ = replay_slots(books,gates,failed)
    manifest = sorted(gates.values(),key=lambda p:(p['book'],p['page']))
    for name,value in [('manifest',manifest),('slots',slots),('fetch_failures',failed)]:
        atomic(OUT/f'{name}_{part}.json',value)
    summary = dict(part=part,sources=len(books),target=sum(len(b['positions']) for b in books),
        rendered=len(manifest),accepted=sum(s['accepted_page'] is not None for s in slots),
        replacements=sum(s['accepted_page'] is not None and s['accepted_page']!=s['original_page'] for s in slots),
        failures=len(failed),gate_flags=dict(Counter(f for p in manifest for f in p['gate']['flags'])),complete=complete)
    atomic(OUT/f'fetch_summary_{part}.json',summary)
    return slots,summary


def acquire_a():
    vouli.check_frozen()
    data = json.loads((OUT/'selection.json').read_text())
    for name,digest in data['inputs'].items():
        if sha(REPO/name)!=digest:
            raise ValueError('selection input changed')
    books = data['books']
    fm = round1.fetch_module()
    http_root = BULK/'anemi_http'
    http_root.mkdir(parents=True,exist_ok=True)
    prior = round2.BULK/'anemi_http/rate_state.json'
    if not (http_root/'rate_state.json').exists():
        shutil.copyfile(prior,http_root/'rate_state.json')
    class PoliteAnemi(fm.AnemiHTTP):
        def _raw(self,url,limit,range_header=None,depth=0):
            if urlsplit(url).scheme!='https' or urlsplit(url).netloc!='anemi.lib.uoc.gr':
                raise fm.ProbeError('T25 acquisition is Anemi HTTPS only')
            path = http_root/'backoff.json'
            state = json.loads(path.read_text()) if path.exists() else {}
            time.sleep(max(0,state.get('not_before',0)-time.time()))
            self.interval = max(self.interval,state.get('interval',2))
            result = super()._raw(url,limit,range_header,depth)
            if result[0]['status'] in (429,503):
                n = state.get('throttles',0)+1
                atomic(path,dict(interval=min(30,max(4,self.interval*2)),
                    not_before=time.time()+min(600,60*2**(n-1)),throttles=n))
            return result
    client = PoliteAnemi(interval=2,root=http_root)
    authenticated = False
    authenticated_at=0
    blocked_path=OUT/'anemi_unavailable_volumes.json'
    blocked=json.loads(blocked_path.read_text()) if blocked_path.exists() else {}
    def login(http):
        nonlocal authenticated,authenticated_at
        if not authenticated:
            fm.authenticate(http)
            authenticated = True
            authenticated_at=time.time()
    def fetch_book(b,numbers):
        nonlocal client,authenticated,authenticated_at
        remaining = []
        failed,stalls,refreshes = {},0,0
        for n in numbers:
            volume,_,_,_=anemi_paths(b,n)
            key=b['key']+':'+volume['volume_id']
            if key in blocked:
                failed[f"{b['key']}:{n}"]=dict(book=b['book'],page=n,reason='source_volume_unavailable',
                    scope='volume acquisition; no saved page',volume_failure=blocked[key])
            else:remaining.append(n)
        while remaining:
            if authenticated and time.time()-authenticated_at>480:
                client=PoliteAnemi(interval=2,root=http_root)
                authenticated=False
            result = fm.fetch_wave(round1.stage_records([b],{b['book']:remaining}),wave=1,
                max_pages=1440,max_bytes=1_500_000_000,dest=BULK,http_root=http_root,
                http_factory=lambda **kwargs:client,login=login,emit=lambda value:None,page_range='explicit')
            folder=OUT/'anemi_fetch_invocations';folder.mkdir(exist_ok=True)
            index=1+len(list(folder.glob('*.json')))
            atomic(folder/f'{index:04d}.json',dict(book=b['book'],requested=remaining,summary=result))
            receipts = fm.latest_receipts(BULK/'records'/b['key'])
            rest = []
            for n in remaining:
                v,local,_,_ = anemi_paths(b,n)
                receipt = receipts.get((v['volume_id'],local-1),{})
                if fm.valid_receipt(receipt,BULK/'records'/b['key'],b['catalogue'],v,local-1):
                    continue
                if receipt.get('state')=='failed':
                    failed[f"{b['key']}:{n}"] = dict(book=b['book'],page=n,receipt=receipt,
                        errors=result['errors'],stop_reason=result['stop_reason'])
                else:
                    rest.append(n)
            if rest==remaining:
                stalls += 1
                if stalls>=3:
                    if refreshes==0:
                        client=PoliteAnemi(interval=2,root=http_root)
                        authenticated=False;authenticated_at=0;refreshes=1;stalls=0
                        with (OUT/'anemi_session_refreshes.jsonl').open('a') as stream:
                            stream.write(json.dumps(dict(book=b['book'],time=time.time(),
                                reason='three acquisition stalls; retry once with a fresh authenticated client'))+'\n')
                        continue
                    # A broken catalogue viewer must not prevent later sources
                    # from running. Preserve the volume-level failure and never
                    # pretend its unrequested pages had individual HTTP reads.
                    volume_id=next((e.get('volume_id') for e in result['errors'] if e.get('volume_id')),None)
                    if volume_id is None:
                        raise RuntimeError('Anemi authentication/global transport stalled without a source-specific error')
                    evidence=dict(book=b['book'],key=b['key'],volume_id=volume_id,
                        reason='three bounded acquisition stalls; volume unavailable',summary=result,
                        transfer_ledger=relative(http_root/'transfer.jsonl'))
                    blocked[b['key']+':'+volume_id]=evidence;atomic(blocked_path,blocked)
                    for n in list(rest):
                        volume,_,_,_=anemi_paths(b,n)
                        if volume['volume_id']==volume_id:
                            failed[f"{b['key']}:{n}"]=dict(book=b['book'],page=n,reason='source_volume_unavailable',
                                scope='volume acquisition; no saved page',volume_failure=evidence)
                            rest.remove(n)
                    stalls=0
                time.sleep(15*stalls)
            else:
                stalls = 0
            remaining = rest
        return failed
    gates = {f"{p['key']}:{p['page']}":p for p in
        [json.loads(f.read_text()) for f in (OUT/'gates').glob('*.json')] if p['part']=='A'}
    failed_path = OUT/'fetch_failures_A.json'
    failed = json.loads(failed_path.read_text()) if failed_path.exists() else {}
    for p in gates.values():
        if sha(REPO/p['image'])!=p['image_sha256'] or sha(REPO/p['pdf'])!=p['pdf_sha256']:
            raise ValueError('resume image/PDF changed')
    with ProcessPoolExecutor(max_workers=3,mp_context=multiprocessing.get_context('spawn'),
            initializer=gate_init,initargs=(data['quality_limits'],)) as pool,ThreadPoolExecutor(max_workers=1) as network:
        for stage in range(3):
            slots,_ = part_checkpoint('A',books,gates,failed)
            _,used = replay_slots(books,gates,failed)
            wanted = defaultdict(list)
            for s in slots:
                if s['accepted_page'] is None:
                    consumed = {c['page'] for c in s['chain']}
                    n = next((n for n in s['candidate_pages'] if n not in consumed and n not in used[s['book']]),None)
                    if n is not None:
                        wanted[s['book']].append(n)
                        used[s['book']].add(n)
            pending = {}
            for b in books:
                numbers = wanted.get(b['book'],[])
                if not numbers:
                    continue
                future = network.submit(fetch_book,b,numbers)
                submitted = set()
                while not future.done() or len(submitted)<len(numbers):
                    receipts = fm.latest_receipts(BULK/'records'/b['key'])
                    for n in numbers:
                        if n in submitted:
                            continue
                        v,local,_,_ = anemi_paths(b,n)
                        receipt = receipts.get((v['volume_id'],local-1),{})
                        if fm.valid_receipt(receipt,BULK/'records'/b['key'],b['catalogue'],v,local-1):
                            pending[pool.submit(gate_anemi,(b,n,receipt))] = (b,n)
                            submitted.add(n)
                    for done in [f for f in pending if f.done()]:
                        p = done.result();gates[f"{p['key']}:{p['page']}"] = p
                        del pending[done]
                    if future.done():
                        failed.update(future.result())
                        if any(n not in submitted and f"{b['key']}:{n}" not in failed for n in numbers):
                            raise ValueError('unattempted page lacks failure receipt')
                        break
                    time.sleep(.25)
                failed.update(future.result())
                _,summary = part_checkpoint('A',books,gates,failed)
                print('A '+json.dumps(summary),flush=True)
            for future in pending:
                p = future.result();gates[f"{p['key']}:{p['page']}"] = p
            part_checkpoint('A',books,gates,failed)
    part_checkpoint('A',books,gates,failed,complete=True)


class DirectHTTP:
    """Streaming public downloads; serial per host, explicit redirects, no retries."""
    def __init__(self):
        self.root = BULK/'direct_http'
        self.root.mkdir(parents=True,exist_ok=True)
        self.last = {}
        self.session = requests.Session()
        self.session.headers.update({'User-Agent':'GreekOCR-research-harvest/1.0 (polite public source collection)',
            'Accept-Encoding':'identity'})

    def download(self,url,path,limit=200_000_000):
        path = Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        temp = path.with_suffix('.part')
        try:
            for depth in range(7):
                parsed = urlsplit(url)
                if parsed.scheme not in ('http','https') or parsed.username or parsed.password:
                    raise ValueError('invalid public URL')
                host = parsed.netloc.lower()
                time.sleep(max(0,1.05-(time.time()-self.last.get(host,0))))
                started = time.time();self.last[host] = started
                receipt = dict(url=url,host=host,started=started,status=None,bytes=0,limit=limit)
                try:
                    with self.session.get(url,stream=True,allow_redirects=False,timeout=(25,90)) as response:
                        receipt.update(status=response.status_code,content_type=response.headers.get('Content-Type'))
                        if response.is_redirect:
                            url = urljoin(url,response.headers['Location'])
                            receipt['location'] = url
                            continue
                        response.raise_for_status()
                        if int(response.headers.get('Content-Length') or 0)>limit:
                            raise ValueError('pdf_size_limit')
                        with temp.open('wb') as stream:
                            for block in response.iter_content(1024*512):
                                receipt['bytes'] += len(block)
                                if receipt['bytes']>limit:
                                    raise ValueError('pdf_size_limit')
                                stream.write(block)
                    with temp.open('rb') as stream:
                        if stream.read(5)!=b'%PDF-':
                            raise ValueError('not_pdf')
                    receipt['sha256'] = sha(temp)
                    receipt['finished'] = time.time()
                    temp.replace(path)
                    return receipt
                except Exception as exc:
                    receipt['error'] = type(exc).__name__
                    raise
                finally:
                    receipt['finished'] = time.time()
                    # Never record request credentials or session headers.
                    with (self.root/'requests.jsonl').open('a') as stream:
                        stream.write(json.dumps(receipt,ensure_ascii=False)+'\n')
            raise ValueError('redirect_limit')
        finally:
            if temp.exists():
                temp.unlink()


def render_direct(task):
    book,pdf,receipt,limits = task
    pdf = Path(pdf)
    gates,failed = {},{}
    try:
        with pdfium.PdfDocument(pdf) as doc:
            total = len(doc)
            book = dict(book,pages=total,pdf_sha256=receipt['sha256'],pdf_bytes=receipt['bytes'],
                download_receipt=receipt)
            book['positions'] = policy.repository_positions(total,book['book']) if book['part']=='B' else policy.spread_positions(total,100,book['book'])
            used = set()
            for pos in book['positions']:
                for number in pos['candidates']:
                    if number in used:
                        continue
                    used.add(number)
                    ident = f"{book['key']}-p{number:06d}"
                    existing = OUT/'gates'/(ident+'.json')
                    if existing.exists():
                        p = json.loads(existing.read_text())
                        if p['pdf_sha256']!=receipt['sha256'] or sha(REPO/p['image'])!=p['image_sha256']:
                            raise ValueError('resume image/PDF changed')
                    else:
                        image_path = BULK/'images'/f"{book['key']}-{number:06d}.png"
                        image_path.parent.mkdir(parents=True,exist_ok=True)
                        try:
                            with closing(doc[number-1]) as page:
                                bitmap = page.render(scale=200/72,grayscale=True)
                                image = bitmap.to_pil().copy().convert('L');bitmap.close()
                            image.save(image_path,compress_level=3)
                            g = vouli.gate_image(image_path,STACK,GATE,limits)
                            p = page_record(book,number,image_path,g,volume=None,volume_page=number,
                                pdf_sha256=receipt['sha256'],pdf_bytes=receipt['bytes'],download_receipt=receipt,
                                sampling_region=pos['region'])
                        except Exception as exc:
                            failed[f"{book['key']}:{number}"] = dict(book=book['book'],page=number,
                                reason='render_gate_error',error_class=type(exc).__name__)
                            continue
                    gates[f"{book['key']}:{number}"] = p
                    if p['harvest_accepted']:
                        break
        return dict(book=book,gates=gates,failed=failed)
    finally:
        # Required for repository downloads; also release the large IA PDF.
        pdf.unlink(missing_ok=True)


def acquire_b():
    vouli.check_frozen()
    limits = json.loads((OUT/'selection.json').read_text())['quality_limits']
    candidates = json.loads((OUT/'repository_order.json').read_text())
    path = OUT/'repository_attempts.json'
    attempts = json.loads(path.read_text()) if path.exists() else []
    results = [json.loads(p.read_text()) for p in sorted((OUT/'direct_results_B').glob('*.json'))]
    books = [r['book'] for r in results]
    completed = {b['book'] for b in books}
    attempted = {r['book'] for r in attempts}
    counts = Counter(b['collection_slug'] for b in books)
    host_counts = Counter(urlsplit(b['pdf_url']).netloc.lower() for b in books)
    pdf_hashes = {b['pdf_sha256'] for b in books}
    gates = {k:p for r in results for k,p in r['gates'].items()}
    failed = {k:p for r in results for k,p in r['failed'].items()}
    http = DirectHTTP()
    with ProcessPoolExecutor(max_workers=3,mp_context=multiprocessing.get_context('spawn'),
            initializer=gate_init,initargs=(limits,)) as pool:
        pending = {}
        for b in candidates:
            if len(books)>=40:
                break
            host=urlsplit(b['pdf_url']).netloc.lower()
            if (b['book'] in completed or b['book'] in attempted or counts[b['collection_slug']]>=5
                    or host_counts[host]>=5):
                continue
            pdf = BULK/'pdf'/(b['book']+'.pdf')
            attempt = dict(book=b['book'],key=b['key'],repository=b['collection_slug'],url=b['pdf_url'],started=time.time())
            try:
                receipt = http.download(b['pdf_url'],pdf)
                if receipt['sha256'] in pdf_hashes:
                    pdf.unlink();raise ValueError('duplicate_pdf_content')
                result = pool.submit(render_direct,(b,str(pdf),receipt,limits)).result()
                b = result['book'];pdf_hashes.add(b['pdf_sha256'])
                books.append(b);completed.add(b['book']);counts[b['collection_slug']] += 1
                host_counts[host] += 1
                gates.update(result['gates']);failed.update(result['failed'])
                atomic(OUT/'direct_results_B'/(b['key']+'.json'),result)
                attempt.update(state='downloaded_rendered',pdf_sha256=b['pdf_sha256'],pages=b['pages'])
            except Exception as exc:
                pdf.unlink(missing_ok=True)
                attempt.update(state='failed',error_class=type(exc).__name__,reason=str(exc)[:220])
            attempts.append(attempt);atomic(path,attempts)
            frozen_books = sorted(books,key=lambda b:b['key'])
            atomic(OUT/'books_B.json',frozen_books)
            _,summary = part_checkpoint('B',frozen_books,gates,failed)
            print('B '+json.dumps(dict(summary,tried=len(attempts),last_state=attempt['state'])),flush=True)
            if len(attempts)>=160 and len(books)<40:
                raise RuntimeError('160 bounded repository attempts exhausted')
    books = sorted(books,key=lambda b:b['key'])
    frozen(OUT/'holdout_B.json',policy.select_holdout(books,dev_counts={'B':1}))
    part_checkpoint('B',books,gates,failed,complete=True)


def acquire_c():
    vouli.check_frozen()
    limits = json.loads((OUT/'selection.json').read_text())['quality_limits']
    key = hashlib.sha256(b'archive_b28038630').hexdigest()[:8]
    result_path = OUT/'direct_result_C.json'
    if result_path.exists():
        result = json.loads(result_path.read_text())
    else:
        meta = json.loads((OUT/'archive_metadata.json').read_text())
        media = next(f for f in meta['files'] if f['name']=='b28038630.pdf')
        b = dict(book='b28038630',key=key,id6=key[:6],title='A Greek-English lexicon',year=1883,
            decade=1880,part='C',pdf_url='https://archive.org/download/b28038630/b28038630.pdf',
            source_url='https://archive.org/details/b28038630',attribution='Liddell and Scott; Internet Archive / Wellcome Library',
            licence='public-domain',source='archive_b28038630',origin='archive',
            recorded_rights=meta['metadata'].get('rights'),declared_pages=1806)
        pdf = BULK/'pdf/b28038630.pdf'
        receipt = DirectHTTP().download(b['pdf_url'],pdf,limit=400_000_000)
        if receipt['bytes']!=int(media['size']) or hashlib.md5(pdf.read_bytes()).hexdigest()!=media['md5']:
            raise ValueError('IA media identity mismatch')
        with ProcessPoolExecutor(max_workers=1,mp_context=multiprocessing.get_context('spawn'),
                initializer=gate_init,initargs=(limits,)) as pool:
            result = pool.submit(render_direct,(b,str(pdf),receipt,limits)).result()
        frozen(result_path,result)
    books = [result['book']]
    frozen(OUT/'books_C.json',books)
    frozen(OUT/'holdout_C.json',policy.select_holdout(books))
    part_checkpoint('C',books,result['gates'],result['failed'],complete=True)
    print('C complete',flush=True)


def previous_page_hashes():
    names = ['round1/reads_d1/plan.json','round1/reads_rest/plan.json']
    names += [n+'/plan.json' for n in PRIOR_WAVES if n!='round1']
    return {p['image_sha256'] for name in names if (path:=REPO/'docs/harvest'/name).exists()
        for p in json.loads(path.read_text()).get('pages',[])}


def prepare_plan():
    vouli.check_frozen()
    books,held,manifest,slots = [],[],[],[]
    for part in PARTS:
        if not json.loads((OUT/f'fetch_summary_{part}.json').read_text())['complete']:
            raise ValueError('incomplete acquisition')
        for stem,acc in [('books',books),('holdout',held),('manifest',manifest),('slots',slots)]:
            acc.extend(json.loads((OUT/f'{stem}_{part}.json').read_text()))
    books.sort(key=lambda b:(b['part'],b['key']))
    held.sort(key=lambda b:(b['part'],b['book_key']))
    assert held==policy.select_holdout(books)
    manifest.sort(key=lambda p:(p['part'],p['book'],p['page']))
    for stem,data in [('books',books),('holdout_books',held),('manifest',manifest),('slots',slots)]:
        frozen(OUT/(stem+'.json'),data)
    chosen = {(s['key'],s['accepted_page']) for s in slots if s['accepted_page'] is not None}
    pages = [p for p in manifest if (p['key'],p['page']) in chosen]
    assert {p['id'] for p in pages}=={p['id'] for p in manifest if p['harvest_accepted']}
    if previous_page_hashes() & {p['image_sha256'] for p in pages}:
        raise ValueError('previous-wave image: no re-read')
    calls = len(vouli.unique_call_pages(pages))
    if calls*.0015>CAP:
        raise ValueError('plan exceeds USD 2.00')
    inputs = {relative(OUT/n):sha(OUT/n) for n in ('selection.json','books.json','manifest.json','slots.json','holdout_books.json')}
    inputs[relative(OUT/'archive_metadata.json')]=sha(OUT/'archive_metadata.json')
    for n in PRIOR_WAVES:
        p = REPO/f'docs/harvest/{n}/admitted.jsonl'
        if p.exists():
            inputs[relative(p)] = sha(p)
    plan = dict(schema='t25-plan-1',binding=json.loads((round1.OUT/'reads_d1/plan.json').read_text())['bindings']['docai'],
        pages=pages,page_count=len(pages),pages_rendered=len(manifest),pages_accepted=len(pages),
        max_calls=calls,max_cost_usd=calls*.0015,cap_usd=CAP,inputs=inputs,
        quality_limits=json.loads((OUT/'selection.json').read_text())['quality_limits'],
        gate_sha256=round1.GATE_SHA,admission_sha256=ADMISSION_SHA,automatic_retries=False,vision_calls=0,
        owner_approval='T25 explicit three-part fetch, gate and read; post-hoc review per execution state')
    frozen(OUT/'plan.json',plan)
    print(json.dumps(dict(rendered=len(manifest),accepted=len(pages),max_usd=calls*.0015)),flush=True)
    return plan


def load_plan():
    vouli.check_frozen()
    plan = json.loads((OUT/'plan.json').read_text())
    selection=json.loads((OUT/'selection.json').read_text())
    for name,digest in dict(selection['inputs'],**plan['inputs']).items():
        if sha(REPO/name)!=digest:
            raise ValueError('frozen input changed: '+name)
    pages={p['id']:p for p in plan['pages']}
    for path in sorted((OUT/'read_snapshots').glob('*.json')):
        snapshot=json.loads(path.read_text())
        for name,digest in snapshot['inputs'].items():
            if sha(REPO/name)!=digest:raise ValueError('read snapshot input changed: '+name)
        if any(pages.get(p['id'])!=p for p in snapshot['pages']):
            raise ValueError('read snapshot page outside final frozen scope')
    return plan


def git_audit():
    """Observe Git metadata without writes; distinguish another actor's commits.

    Git-state equality cannot establish which process wrote an index. Preserve
    both snapshots and appended reflog evidence rather than rolling anything
    back or attributing another task's commits to this harvest.
    """
    before=json.loads((OUT/'git_before.json').read_text())
    after=round1.git_snapshot()
    changed=[dict(path=key,before=before.get(key),after=after.get(key))
        for key in sorted(set(before)|set(after)) if before.get(key)!=after.get(key)]
    log=REPO/'.git/logs/refs/heads/main'
    raw=log.read_bytes();old=before['logs/refs/heads/main'];prefix=raw[:old['bytes']]
    prefix_unchanged=hashlib.sha256(prefix).hexdigest()==old['sha256']
    commits=[]
    if prefix_unchanged:
        for line in raw[old['bytes']:].decode().splitlines():
            head,message=line.split('\t',1);tokens=head.split()
            commits.append(dict(old=tokens[0],new=tokens[1],timestamp=int(tokens[-2]),timezone=tokens[-1],message=message))
    result=dict(unchanged=not changed,before=relative(OUT/'git_before.json'),after=after,
        changed=changed,reflog_prefix_unchanged=prefix_unchanged,appended_main_commits=commits,
        t25_git_write_operations=0,
        attribution='T25 invokes no Git writes. Appended T24/T24b commits and index/object changes were observed during the run; writer identity is not inferred.')
    atomic(OUT/'git_audit.json',result)
    return result


class MixedReaders(vouli.VouliReaders):
    def __init__(self,plan,root=GOOGLE):
        super().__init__(plan,root=root)


def read(plan):
    old = vouli.OUT,vouli.GOOGLE,vouli.VouliReaders
    try:
        vouli.OUT,vouli.GOOGLE,vouli.VouliReaders = OUT,GOOGLE,MixedReaders
        vouli.run(plan)
    finally:
        vouli.OUT,vouli.GOOGLE,vouli.VouliReaders = old


def read_watch():
    """Read permanent slots only after their part's source hold-outs are fixed."""
    vouli.check_frozen()
    binding=json.loads((round1.OUT/'reads_d1/plan.json').read_text())['bindings']['docai']
    previous=previous_page_hashes()
    while True:
        reserved={r['key'] for r in read_jsonl(GOOGLE/'budget.jsonl')}
        pages=[];complete=True;inputs={relative(OUT/'selection.json'):sha(OUT/'selection.json')}
        for part in PARTS:
            summary=OUT/f'fetch_summary_{part}.json'
            done=summary.exists() and json.loads(summary.read_text()).get('complete',False)
            complete=complete and done
            holdout=OUT/f'holdout_{part}.json'
            manifest=OUT/f'manifest_{part}.json';slots=OUT/f'slots_{part}.json'
            if not holdout.exists() or not manifest.exists() or not slots.exists():continue
            # B's final source membership must be frozen before any B reads.
            if part=='B' and not done:continue
            inputs[relative(holdout)]=sha(holdout)
            chosen={(s['key'],s['accepted_page']) for s in json.loads(slots.read_text()) if s['accepted_page'] is not None}
            pages.extend(p for p in json.loads(manifest.read_text())
                if (p['key'],p['page']) in chosen and p['image_sha256'] not in reserved)
        if previous&{p['image_sha256'] for p in pages}:raise ValueError('snapshot image was previously read')
        if len(pages)>=35 or (complete and pages):
            folder=OUT/'read_snapshots';folder.mkdir(exist_ok=True)
            index=1+max((int(p.stem) for p in folder.glob('*.json')),default=0)
            plan=dict(schema='t25-read-snapshot-1',binding=binding,pages=pages,cap_usd=CAP,max_calls=980,
                inputs=inputs,vision_calls=0,automatic_retries=False,scope='permanent accepted slots; per-part hold-outs frozen')
            frozen(folder/f'{index:03d}.json',plan)
            print(f'read snapshot {index}: {len(pages)} permanent accepted pages',flush=True)
            read(plan)
        elif complete:
            print('all permanent accepted pages have reserved cached reads',flush=True)
            return
        else:time.sleep(20)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['select','acquire-a','acquire-b','acquire-c','plan','read','read-watch','compile-watch','build','validate','publish'])
    args = parser.parse_args()
    if args.mode=='select':select()
    elif args.mode.startswith('acquire-'):globals()['acquire_'+args.mode[-1]]()
    elif args.mode=='plan':prepare_plan()
    elif args.mode=='read':read(load_plan())
    elif args.mode=='read-watch':read_watch()
    elif args.mode=='compile-watch':
        from scripts.harvest.mixed_outputs import compile_watch
        compile_watch()
    else:
        from scripts.harvest import mixed_outputs
        getattr(mixed_outputs,args.mode)(load_plan())


if __name__=='__main__':
    main()

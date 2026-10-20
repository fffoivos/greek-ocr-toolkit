"""T23: public CC-BY Parliament selection, bounded PDF lifetime, frozen gate/DocAI.

select-fetch-gate and run use only the public Parliament API and Google DocAI,
respectively. build/validate/publish are offline. Never writes Git metadata.
"""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from contextlib import closing
import json
import multiprocessing
from pathlib import Path
import threading
import time

from PIL import Image
import pypdfium2 as pdfium

from greekocr.harvest.parliament import (BASE, YEARS, SEED, MAX_PDF, candidate_slots,
    eligible, holdout, page_spread, neighbours, resolve_pdf, rights_raw)
from greekocr.harvest.parliament_http import ParliamentHTTP
from greekocr.harvest.readers import atomic, read_jsonl
from scripts.harvest import round1, vouli
from scripts.harvest.round1_reads import frozen

REPO = vouli.REPO
OUT = REPO / 'docs/records/harvest/parliament'
BULK = REPO / 'docs/harvest/harvest_big/parliament'
GOOGLE = BULK / 'google'
CATALOGUE = BULK / 'parliament_catalogue.jsonl'
SOURCE = 'parliament_proceedings_1975_2000'
BATCH = 'parliament_modern'
CAP = 2.50
ADMISSION_SHA = vouli.ADMISSION_SHA
sha, relative = vouli.sha, vouli.relative


def gate_task(page):
    result = vouli.gate_image(REPO/page['image'], vouli.WORKER_STACK,
                             vouli.WORKER_GATE, vouli.WORKER_LIMITS)
    page.update(gate=result, harvest_accepted=result['accepted'])
    atomic(OUT/'gates'/(page['id']+'.json'), page)
    return page


def gate_volume(book, pool):
    positions = page_spread(book['page_count'], book['book'])
    reserved = {p['page'] for p in positions}
    slots = []
    for p in positions:
        candidates = neighbours(p['page'], book['page_count'], reserved)
        reserved.update(candidates)
        slots.append(dict(key=book['key'], original_page=p['page'], position=p,
                          candidate_pages=candidates, attempts=[], accepted_page=None))
    manifest = []
    path = REPO/book['pdf']
    with pdfium.PdfDocument(path) as doc:
        for attempt in range(3):
            tasks = []
            for slot in slots:
                if slot['accepted_page'] is not None or attempt>=len(slot['candidate_pages']):
                    continue
                number = slot['candidate_pages'][attempt]
                ident = f"{book['key']}-p{number:06d}"
                receipt_path = OUT/'gates'/(ident+'.json')
                image_path = BULK/'images'/f"{book['key']}-{number:06d}.png"
                if receipt_path.exists():
                    p = json.loads(receipt_path.read_text())
                    if p['pdf_sha256'] != book['pdf_sha256'] or sha(REPO/p['image']) != p['image_sha256']:
                        raise ValueError('resume gate/image/PDF mismatch')
                    tasks.append((slot,p,None))
                    continue
                image_path.parent.mkdir(parents=True,exist_ok=True)
                with closing(doc[number-1]) as pdfpage:
                    bitmap = pdfpage.render(scale=200/72,grayscale=True)
                    image = bitmap.to_pil().copy().convert('L')
                    bitmap.close()
                image.save(image_path,compress_level=1)
                p = dict(book,id=ident,page=number,volume=None,volume_page=number,
                    image=relative(image_path),image_sha256=sha(image_path),
                    width=image.width,height=image.height,dpi=200,grayscale=True,read_batch=BATCH,
                    era='1975_1981_polytonic_possible' if book['year']<=1981 else '1982_2000_monotonic',
                    original_page=slot['original_page'],neighbour_offset=number-slot['original_page'])
                tasks.append((slot,None,pool.submit(gate_task,p)))
            for slot,p,future in tasks:
                p = future.result() if future is not None else p
                manifest.append(p)
                slot['attempts'].append(p['page'])
                if p['harvest_accepted']:
                    slot['accepted_page']=p['page']
    return manifest,slots


def selection_table(books, skips, missing):
    lines=['# T23 — Parliament proceedings selection','',
        'Seed 20263. Four chronological strata per available year; seeded candidate order within each stratum. '
        'Only literal collection ΠΡΑΚΤΙΚΑ ΒΟΥΛΗΣ, catalogue year 1975–2000 and raw CC BY 4.0; NC/ND excluded. '
        'ORIGINAL PDF only; >250,000,000 bytes replaced before download. PDFs too short for 12 distinct 8–95% pages are replaced.', '',
        f'Target: 104 volumes / 26 years. Selected: {len(books)}. Missing catalogue years: '+', '.join(map(str,missing))+'. '
        'No quota is silently moved to another year. See missing_year_probe.json for the bounded live check.','',
        '| Year | Title | UUID | Rights raw | Bitstream bytes | Session stratum |',
        '| --- | --- | --- | --- | ---: | ---: |']
    for b in books:
        title=' '.join(b['title'].split()).replace('|','\\|')
        rights='; '.join(b['rights_raw']).replace('|','\\|')
        lines.append(f"| {b['year']} | [{title}]({b['source_url']}) | {b['book']} | {rights} | {b['bitstream']['size']} | {b['stratum']+1} |")
    lines+=['','## Replaced candidates','', '| Year | UUID | Reason | Bytes |','| --- | --- | --- | ---: |']
    lines += [f"| {s['year']} | {s['uuid']} | {s['reason']} | {s.get('size','')} |" for s in skips]
    (OUT/'SELECTION.md').write_text('\n'.join(lines)+'\n')


def select_fetch_gate():
    vouli.check_frozen()
    OUT.mkdir(parents=True,exist_ok=True)
    if not (OUT/'git_before.json').exists():
        atomic(OUT/'git_before.json',round1.git_snapshot())
    catalogue=read_jsonl(CATALOGUE)
    slots=candidate_slots(catalogue)
    missing=[y for y in YEARS if not any(s['candidates'] for s in slots if s['year']==y)]
    limits=json.loads((_data_input(round1.OUT/'selection.json')).read_text())['quality_limits']
    client=ParliamentHTTP(BULK/'http_t23')
    skips,books,manifest,page_slots=[],[],[],[]
    completed=OUT/'volumes'
    completed.mkdir(exist_ok=True)
    with ProcessPoolExecutor(max_workers=3,mp_context=multiprocessing.get_context('spawn'),
            initializer=vouli.init_gate_worker,initargs=(limits,)) as pool:
        for slot in slots:
            if not slot['candidates']:
                continue
            done_path=completed/f"{slot['year']}-{slot['stratum']}.json"
            if done_path.exists():
                done=json.loads(done_path.read_text())
                old_pdf=REPO/done['book']['pdf']
                if old_pdf.exists():
                    if sha(old_pdf)!=done['book']['pdf_sha256']:
                        raise ValueError('completed PDF changed before retention cleanup')
                    old_pdf.unlink()
                atomic(BULK/'pdf_receipts'/(done['book']['book']+'.retention.json'),
                    dict(sha256=done['book']['pdf_sha256'],bytes=done['book']['pdf_bytes'],
                         page_count=done['book']['page_count'],deleted=True,
                         reason='T23 bounded disk: delete after sampled-page render/gate'))
                books.append(done['book']);manifest.extend(done['pages']);page_slots.extend(done['slots'])
                skips.extend(done['skips'])
                continue
            replacements=[]
            for row in slot['candidates']:
                uuid=row['document_id']; pdf=BULK/'pdf'/(uuid+'.pdf')
                print(f"resolve {slot['year']} stratum {slot['stratum']+1} {uuid}",flush=True)
                try:
                    bitstream=resolve_pdf(client,uuid)
                    if bitstream['size'] is not None and bitstream['size']>MAX_PDF:
                        replacements.append(dict(year=row['year'],uuid=uuid,reason='size',size=bitstream['size']))
                        continue
                    receipt_path=BULK/'pdf_receipts'/(uuid+'.json')
                    if pdf.exists() and receipt_path.exists():
                        download=json.loads(receipt_path.read_text())
                        if sha(pdf)!=download['sha256']:raise ValueError('PDF hash mismatch on resume')
                    else:
                        download=client.download(bitstream['url'],pdf,bitstream['size'],bitstream['checksum'])
                        atomic(receipt_path,download)
                    with pdfium.PdfDocument(pdf) as doc: count=len(doc)
                    try: page_spread(count,uuid)
                    except ValueError:
                        replacements.append(dict(year=row['year'],uuid=uuid,reason='short_pdf',size=pdf.stat().st_size,page_count=count))
                        pdf.unlink()
                        continue
                    if not row['record_url'].startswith('https://hdl.handle.net/'):
                        raise ValueError('catalogue record_url is not an HTTPS handle')
                    book=dict(book=uuid,key=uuid[:8],title=row['title'],year=row['year'],decade=row['year']//10*10,
                        stratum=slot['stratum'],pdf=relative(pdf),pdf_sha256=download['sha256'],pdf_bytes=download['bytes'],
                        page_count=count,bitstream=bitstream,rights_raw=rights_raw(row),catalogue=row,
                        source_url=row['record_url'],attribution='Hellenic Parliament Library; '+row['title'],
                        licence='CC-BY-4.0',source=SOURCE,origin='parliament',download_receipt=relative(receipt_path))
                    pages,pslots=gate_volume(book,pool)
                    done=dict(book=book,pages=pages,slots=pslots,skips=replacements,pdf_deleted=True)
                    atomic(done_path,done)
                    pdf.unlink()
                    atomic(BULK/'pdf_receipts'/(uuid+'.retention.json'),dict(sha256=book['pdf_sha256'],bytes=book['pdf_bytes'],
                        page_count=count,deleted=True,reason='T23 bounded disk: delete after sampled-page render/gate'))
                    books.append(book);manifest.extend(pages);page_slots.extend(pslots);skips.extend(replacements)
                    print(f"volumes {len(books)}; pages {len(manifest)} / {sum(p['harvest_accepted'] for p in manifest)} accepted; PDF deleted",flush=True)
                    break
                except (RuntimeError,ValueError,pdfium.PdfiumError) as exc:
                    if pdf.exists():pdf.unlink()
                    replacements.append(dict(year=row['year'],uuid=uuid,reason=type(exc).__name__,error=str(exc)))
                    atomic(OUT/'candidate_failures.json',skips+replacements)
                    print('candidate failed',uuid,type(exc).__name__,str(exc),flush=True)
            else:
                raise RuntimeError('all candidates exhausted for '+str((slot['year'],slot['stratum'])))
    books.sort(key=lambda b:(b['year'],b['stratum']))
    manifest.sort(key=lambda p:(p['book'],p['page']))
    if len({b['key'] for b in books})!=len(books):raise ValueError('UUID8 collision')
    frozen(OUT/'books.json',books)
    frozen(OUT/'holdout_books.json',holdout(books))
    frozen(OUT/'manifest.json',manifest)
    frozen(OUT/'slots.json',page_slots)
    atomic(OUT/'selection_summary.json',dict(target_volumes=104,selected=len(books),missing_years=missing,
        selected_per_year=dict(Counter(b['year'] for b in books)),skips=skips,catalogue_sha256=sha(CATALOGUE),seed=SEED))
    selection_table(books,skips,missing)
    atomic(OUT/'api_politeness.json',client.receipt())
    pages=[p for p in manifest if p['harvest_accepted']]
    binding=json.loads((round1.OUT/'reads_d1/plan.json').read_text())['bindings']['docai']
    unique=vouli.unique_call_pages(pages)
    if len(unique)*.0015>CAP:raise ValueError('accepted scope exceeds Google cap')
    # Previous waves remain separate, immutable and included in the O5 overlay.
    previous_hashes={r['image_sha256'] for name in ('round1/records_all.jsonl','vouli/records.jsonl','round2/records.jsonl')
                     for r in read_jsonl(REPO/'docs/records/harvest'/name)}
    if previous_hashes & {p['image_sha256'] for p in pages}:
        raise ValueError('page SHA already read in a prior wave; resolve reuse before reads')
    plan=dict(schema='t23-parliament-plan-1',binding=binding,pages=pages,page_count=len(pages),
        pages_rendered=len(manifest),pages_accepted=len(pages),max_calls=len(unique),cap_usd=CAP,
        max_cost_usd=len(unique)*.0015,quality_limits=limits,gate_sha256=round1.GATE_SHA,
        admission_sha256=ADMISSION_SHA,seed=SEED,holdout_seed=20261015,automatic_retries=False,vision_calls=0,
        inputs={relative(p):sha(p) for p in [CATALOGUE,OUT/'books.json',OUT/'holdout_books.json',OUT/'manifest.json',OUT/'slots.json',
            round1.OUT/'selection.json',round1.OUT/'reads_d1/plan.json',
            *[REPO/'docs/records/harvest'/name for name in ('round1/admitted.jsonl','vouli/admitted.jsonl','round2/admitted.jsonl')]]})
    frozen(OUT/'plan.json',plan)
    print(json.dumps({k:plan[k] for k in ('pages_rendered','pages_accepted','max_cost_usd')}),flush=True)


def load_plan():
    vouli.check_frozen()
    plan=json.loads((OUT/'plan.json').read_text())
    for p,digest in plan['inputs'].items():
        if sha(REPO/p)!=digest:raise ValueError('frozen input changed: '+p)
    return plan


class ParliamentReaders(vouli.VouliReaders):
    def __init__(self,plan,root=GOOGLE):
        super().__init__(plan,root=root)


def run(plan, *, workers=3, reverse=False, min_start_gap=0):
    # Same T21 adapter, binding, three workers and at-most-once reservations.
    # A definitive, retained HTTP 400 size refusal does not block other pages.
    readers=ParliamentReaders(plan)
    if min_start_gap:
        rate_lock,last_start=threading.Lock(),[0.0]
        read=readers.docai.read
        def paced_read(*args,**kwargs):
            with rate_lock:
                time.sleep(max(0,min_start_gap-(time.monotonic()-last_start[0])))
                last_start[0]=time.monotonic()
            return read(*args,**kwargs)
        readers.docai.read=paced_read
    failures=[]
    pages=vouli.unique_call_pages(plan['pages'])
    if reverse:pages.reverse()
    def call(page):
        if sha(REPO/page['image'])!=page['image_sha256']:
            raise ValueError('page changed before request')
        result=readers.call('docai',REPO/page['image'])
        if result['status']!='ok':
            ledger=[r for r in read_jsonl(GOOGLE/'docai/ledger.jsonl') if r['crop_sha256']==page['image_sha256']]
            raw=json.loads(Path(ledger[-1]['raw_json_path']).read_text()) if ledger and ledger[-1].get('raw_json_path') else {}
            if raw.get('error',{}).get('message')!='Input Document too large':
                raise RuntimeError('non-size provider failure retained; no retry: '+page['id'])
        return page['id'],result['status']
    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures={pool.submit(call,p):p for p in pages}
            for i,future in enumerate(as_completed(futures),1):
                ident,status=future.result()
                if status!='ok':failures.append(ident)
                if i%10==0 or i==len(pages):
                    print(f"processed unique page {i}/{len(pages)}; size failures {len(failures)}; {ident} {status}",flush=True)
    finally:
        cost=readers.budget.receipt()
        cost.update(prices={'docai':.0015},pricing_sources=['https://cloud.google.com/products/document-ai/pricing'],
            pricing_basis='conservative list-price reservations, including failed requests; not invoice readback')
        atomic(OUT/('cost_receipt_reverse.json' if reverse else 'cost_receipt.json'),cost)
        atomic(OUT/('read_attempt_failures_reverse.json' if reverse else 'read_attempt_failures.json'),sorted(failures))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['select-fetch-gate','run','build','validate','publish'])
    parser.add_argument('--reverse',action='store_true')
    parser.add_argument('--workers',type=int,default=3)
    parser.add_argument('--min-start-gap',type=float,default=0)
    args=parser.parse_args();mode=args.mode
    if not 1<=args.workers<=6 or args.min_start_gap<0:parser.error('invalid reader pacing')
    if mode=='select-fetch-gate':select_fetch_gate()
    elif mode=='run':run(load_plan(),workers=args.workers,reverse=args.reverse,min_start_gap=args.min_start_gap)
    else:
        from scripts.harvest.parliament_outputs import build,validate,publish
        {'build':build,'validate':validate,'publish':publish}[mode](load_plan())


if __name__=='__main__':main()

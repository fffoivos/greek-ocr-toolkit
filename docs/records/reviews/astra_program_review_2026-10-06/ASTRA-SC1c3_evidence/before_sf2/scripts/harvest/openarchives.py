"""T24c: pipeline selection, one-PDF acquisition, frozen gate and bounded DocAI.

No Git writes. prepare/build/validate/publish are offline; acquire/read use only
public bitstream hosts / Google. Per-candidate and per-page receipts allow resume.
"""
from __future__ import annotations
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import math
import multiprocessing
from pathlib import Path
import shutil
import threading
import time
from urllib.parse import urlsplit, urljoin
import requests
import pypdfium2 as pdfium
from PIL import Image
from greekocr.harvest import openarchives as policy
from greekocr.harvest.readers import atomic, read_jsonl
from greekocr.harvest.round1 import positions, replacement_candidates
from scripts.harvest import round1, vouli
from scripts.harvest.round1_reads import frozen

REPO=Path(__file__).resolve().parents[2]
OUT=REPO/'docs/harvest/openarchives'
BULK=REPO/'docs/harvest/harvest_big/openarchives'
GOOGLE=BULK/'google'
CAP=3.00
ADMISSION_SHA=vouli.ADMISSION_SHA
SEED=policy.SEED
sha,relative=vouli.sha,vouli.relative
PRIOR_WAVES=('round1','vouli','round2','parliament','mixed','cyrillic','wikisource')
MAIN_GIT=('HEAD','index','refs/heads/main','packed-refs','logs/HEAD','logs/refs/heads/main','config')


def git_snapshot():
    return {name:dict(bytes=p.stat().st_size,mtime_ns=p.stat().st_mtime_ns,sha256=sha(p))
        if (p:=REPO/'.git'/name).exists() else None for name in MAIN_GIT}


class LowDisk(RuntimeError):pass


def disk_check():
    free=shutil.disk_usage(REPO).free
    if free<4*2**30:
        state=dict(status='aborted_low_disk',free_bytes=free,minimum_bytes=4*2**30,
            at=datetime.now(timezone.utc).isoformat(),resume='Free space, then rerun the interrupted mode; paid pages are never retried.')
        atomic(OUT/'disk_abort.json',state)
        raise LowDisk('free disk below 4 GiB')
    return free


def check():vouli.check_frozen();disk_check()


def wait_metadata():
    while not (BULK/'doc_metadata.jsonl').exists() or list(BULK.glob('doc_metadata*.partial')):
        print('Waiting for final metadata; poll in 120 s',flush=True)
        time.sleep(60);time.sleep(60)


def prepare():
    check();OUT.mkdir(parents=True,exist_ok=True)
    if not (OUT/'git_before_t24c.json').exists():atomic(OUT/'git_before_t24c.json',git_snapshot())
    wait_metadata()
    files=[BULK/n for n in ('external_pdfs.parquet','all_links.parquet','collections_links_summary.parquet','doc_metadata.jsonl')]
    inputs={relative(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in files}
    # The T24/T24b mixed-candidate artifact is immutable for this run.
    wave5=OUT/'wave5_candidates.json';inputs[relative(wave5)]=dict(bytes=wave5.stat().st_size,sha256=sha(wave5))
    pool,_,summary=policy.build_pool(files[0],files[-1]);draw,cap=policy.capped_draw(pool)
    if len(draw)<130:raise ValueError('not enough candidates at cap <=30')
    for n,v in [('candidates',pool),('pool_summary',summary),('selection',draw)]:atomic(OUT/(n+'.json'),v)
    result=dict(schema='t24c-selection-1',inputs=inputs,seed=SEED,holdout_seed=20261015,cap_used=cap,
        target_documents=130,target_overdraw=173,overdraw=len(draw),pool_size=len(pool),
        quality_limits=json.loads((round1.OUT/'selection.json').read_text())['quality_limits'],
        disk_free_bytes=disk_check(),admission_sha256=ADMISSION_SHA,gate_sha256=round1.GATE_SHA,
        started_utc=datetime.now(timezone.utc).isoformat())
    atomic(OUT/'selection_config.json',result)
    selection_table(draw,[])
    print(json.dumps({k:result[k] for k in ('pool_size','overdraw','cap_used','disk_free_bytes')}),flush=True)


class DirectHTTP:
    """Serial streaming downloads, paced across redirects and restart history."""
    def __init__(self):
        self.path=BULK/'http/requests.jsonl';self.path.parent.mkdir(parents=True,exist_ok=True)
        self.last={}
        for r in read_jsonl(self.path):self.last[r['host']]=max(self.last.get(r['host'],0),r['started'])
        self.session=requests.Session()
        self.session.headers.update({'User-Agent':'GreekOCR-research-harvest/1.0 (public bitstream collection)', 'Accept-Encoding':'identity'})

    def download(self,url,path):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix('.part')
        try:
            for _ in range(7):
                p=urlsplit(url)
                if p.scheme not in ('http','https') or p.username or p.password:raise ValueError('invalid URL')
                host=p.hostname.lower();time.sleep(max(0,1.05-(time.time()-self.last.get(host,0))))
                disk_check();start=time.time();self.last[host]=start
                receipt=dict(url=url,host=host,started=start,status=None,bytes=0)
                try:
                    with self.session.get(url,stream=True,allow_redirects=False,timeout=(5,30)) as response:
                        receipt.update(status=response.status_code,content_type=response.headers.get('Content-Type'))
                        if response.is_redirect:
                            url=urljoin(url,response.headers['Location']);receipt['location']=url;continue
                        response.raise_for_status()
                        if int(response.headers.get('Content-Length') or 0)>policy.MAX_PDF:raise ValueError('pdf_size_limit')
                        with temp.open('wb') as stream:
                            for block in response.iter_content(512*1024):
                                disk_check();receipt['bytes']+=len(block)
                                if receipt['bytes']>policy.MAX_PDF:raise ValueError('pdf_size_limit')
                                if time.time()-start>240:raise TimeoutError('download wall-time limit')
                                stream.write(block)
                    with temp.open('rb') as stream:
                        if stream.read(5)!=b'%PDF-':raise ValueError('not_pdf')
                    receipt.update(sha256=sha(temp),finished=time.time());temp.replace(path)
                    return receipt
                except Exception as e:
                    receipt.update(error_class=type(e).__name__,reason='size' if str(e)=='pdf_size_limit' else 'download_error')
                    raise
                finally:
                    receipt['finished']=time.time()
                    with self.path.open('a') as stream:stream.write(json.dumps(receipt,ensure_ascii=False)+'\n')
            raise ValueError('redirect_limit')
        finally:temp.unlink(missing_ok=True)


def gate_task(p):
    disk_check()
    result=vouli.gate_image(REPO/p['image'],vouli.WORKER_STACK,vouli.WORKER_GATE,vouli.WORKER_LIMITS)
    p.update(gate=result,harvest_accepted=result['accepted'])
    atomic(OUT/'gates'/(p['id']+'.json'),p)
    return p


def render_page(page,path):
    """Render directly at capped scale; native refers to the requested 200 dpi."""
    w,h=page.get_size();native=[math.ceil(w*200/72),math.ceil(h*200/72)]
    scale=min(1.,3500/max(native));render_scale=200/72*scale
    # Rounding in PDFium may add a pixel: use a tiny conservative adjustment.
    render_scale=min(render_scale,3499.999/max(w,h))
    with closing(page.render(scale=render_scale,grayscale=True)) as bitmap:image=bitmap.to_pil().copy().convert('L')
    image.save(path,compress_level=6)
    return image,dict(native_page_points=[w,h],native_200dpi_size=native,render_scale_factor=render_scale/(200/72),
        pdf_points_to_pixels=render_scale,effective_dpi=render_scale*72,coordinate_frame='rendered PNG',png_compress_level=6)


def gate_volume(book,pdf,pool):
    with pdfium.PdfDocument(pdf) as doc:
        total=len(doc);book=dict(book,page_count=total,pages=total)
        spread=positions(total,12,seed=SEED,book=book['book'])
        reserved={p['page'] for p in spread};slots=[];manifest=[]
        for pos in spread:
            candidates=replacement_candidates(pos['page'],total,reserved=reserved);reserved.update(candidates)
            slots.append(dict(key=book['key'],position=pos,original_page=pos['page'],candidate_pages=candidates,attempts=[],accepted_page=None))
        for attempt in range(3):
            pending=[]
            for slot in slots:
                if slot['accepted_page'] is not None or attempt>=len(slot['candidate_pages']):continue
                disk_check();n=slot['candidate_pages'][attempt];ident=f"{book['key']}-p{n:06d}"
                saved=OUT/'gates'/(ident+'.json');path=BULK/'images'/f"{book['key']}-{n:06d}.png"
                if saved.exists():
                    p=json.loads(saved.read_text())
                    if p['pdf_sha256']!=book['pdf_sha256'] or p['image_sha256']!=sha(REPO/p['image']):raise ValueError('resume source mismatch')
                    pending.append((slot,p,None));continue
                path.parent.mkdir(parents=True,exist_ok=True)
                with closing(doc[n-1]) as page:image,render=render_page(page,path)
                fields=('book','key','title','year','decade','collection_slug','source','source_url','licence','attribution','origin','pdf_sha256','pdf_bytes')
                p=dict({k:book[k] for k in fields},id=ident,page=n,volume=None,volume_page=n,
                    image=relative(path),image_sha256=sha(path),width=image.width,height=image.height,dpi=200,
                    grayscale=True,read_batch='openarchives',original_page=slot['original_page'],neighbour_offset=n-slot['original_page'],**render)
                pending.append((slot,None,pool.submit(gate_task,p)))
            for slot,p,future in pending:
                p=future.result() if future is not None else p;manifest.append(p);slot['attempts'].append(p['page'])
                if p['harvest_accepted']:slot['accepted_page']=p['page']
    return dict(book=book,pages=manifest,slots=slots)


def selection_table(draw,results):
    config=json.loads((OUT/'selection_config.json').read_text()) if (OUT/'selection_config.json').exists() else {}
    done={r['key']:r for r in results}
    lines=['# T24c — Open Archives selection','',f"Seed {SEED}; cap {config.get('cap_used',10)} per metadata repository; 173 overdraw, first 130 successful PDF downloads. Type × decade strata within repository round-robin. Null scores pass; measured Greek-badness median applies. Earlier URL status is informational only.",'',
        '| Order | Repository | Type | Year | Title | Earlier status | PDF | Outcome |','| ---: | --- | --- | ---: | --- | --- | --- | --- |']
    for i,b in enumerate(draw,1):
        r=done.get(b['key']);outcome=r['outcome'] if r else 'not attempted'
        title=' '.join(b['title'].split()).replace('|','\\|')
        lines.append(f"| {i} | {b['collection_slug']} | {b['type']} | {b['year']} | {title} | {b.get('earlier_status_code')} | [PDF]({b['pdf_url']}) | {outcome} |")
    (OUT/'SELECTION.md').write_text('\n'.join(lines)+'\n')


def acquire():
    check();config=json.loads((OUT/'selection_config.json').read_text());draw=json.loads((OUT/'selection.json').read_text())
    for path,v in config['inputs'].items():
        if sha(REPO/path)!=v['sha256']:raise ValueError('input changed: '+path)
    http=DirectHTTP();results=[];books=[];manifest=[];slots=[]
    # A single PDF is downloaded/rendered/deleted before visiting the next row.
    with ProcessPoolExecutor(max_workers=3,mp_context=multiprocessing.get_context('spawn'),initializer=vouli.init_gate_worker,initargs=(config['quality_limits'],)) as pool:
        for i,b in enumerate(draw,1):
            if len(books)>=130:break
            disk_check();saved=OUT/'acquisitions'/(b['key']+'.json');pdf=BULK/'pdf'/(b['key']+'.pdf')
            if saved.exists():result=json.loads(saved.read_text())
            else:
                print(f"candidate {i}/{len(draw)} {b['collection_slug']} {b['key']}",flush=True)
                attempt_path=OUT/'download_attempts'/(b['key']+'.json')
                if attempt_path.exists():attempts=json.loads(attempt_path.read_text())
                else:
                    # Before T24c gained an attempt journal, the HTTP log still
                    # proves starts for the only potentially interrupted row.
                    attempts=[dict(attempt=n+1,reason='historical_or_interrupted_start') for n,r in enumerate(
                        r for r in read_jsonl(http.path) if r['url']==b['pdf_url'])]
                result=None
                for attempt in range(len(attempts),3):
                    attempts.append(dict(attempt=attempt+1,reason='started'))
                    atomic(attempt_path,attempts)
                    try:
                        # Remove only a stale same-candidate temporary; never another PDF.
                        if list((BULK/'pdf').glob('*.pdf')) and not pdf.exists():raise RuntimeError('one-PDF invariant violated')
                        receipt_path=BULK/'pdf_receipts'/(b['key']+'.json')
                        if pdf.exists() and receipt_path.exists():receipt=json.loads(receipt_path.read_text());assert sha(pdf)==receipt['sha256']
                        else:receipt=http.download(b['pdf_url'],pdf);atomic(receipt_path,receipt)
                        book=dict(b,pdf_sha256=receipt['sha256'],pdf_bytes=receipt['bytes'],download_receipt=relative(receipt_path))
                        rendered=gate_volume(book,pdf,pool)
                        result=dict(key=b['key'],outcome='downloaded',attempts=attempts,**rendered)
                        break
                    except LowDisk:raise
                    except (requests.RequestException,TimeoutError,ValueError,pdfium.PdfiumError) as e:
                        attempts[-1]=dict(attempt=attempt+1,error_class=type(e).__name__,reason='size' if str(e)=='pdf_size_limit' else 'download_or_pdf_error')
                        atomic(attempt_path,attempts)
                        print(f"candidate failure {b['key']} attempt {attempt+1}: {type(e).__name__}",flush=True)
                        # The brief sets a maximum of two retries, not a duty
                        # to repeat definitive refusals or unreachable hosts.
                        if str(e) in ('pdf_size_limit','not_pdf') or isinstance(e,requests.ConnectTimeout):break
                        if isinstance(e,requests.HTTPError) and e.response is not None and 400<=e.response.status_code<500:break
                    finally:pdf.unlink(missing_ok=True)
                if result is None:result=dict(key=b['key'],outcome='skipped_size' if attempts[-1]['reason']=='size' else 'dead_link',attempts=attempts)
                atomic(saved,result)
                if result['outcome']=='downloaded':
                    book=result['book'];atomic(BULK/'pdf_receipts'/(b['key']+'.retention.json'),dict(sha256=book['pdf_sha256'],bytes=book['pdf_bytes'],page_count=book['page_count'],deleted=True))
            results.append(result)
            if result['outcome']=='downloaded':books.append(result['book']);manifest.extend(result['pages']);slots.extend(result['slots'])
            for n,v in [('books',books),('manifest',manifest),('slots',slots),('acquisition_results',results)]:atomic(OUT/(n+'.json'),v)
            selection_table(draw,results)
            print(f"documents {len(books)}/{len(results)}; rendered {len(manifest)}; accepted {sum(p['harvest_accepted'] for p in manifest)}; free {disk_check()/2**30:.2f} GiB",flush=True)
    if len(books)<20:raise ValueError('too few downloaded documents for holdout')
    atomic(OUT/'holdout_books.json',policy.holdout(books))
    prepare_plan()


def prepare_plan():
    check();config=json.loads((OUT/'selection_config.json').read_text());manifest=json.loads((OUT/'manifest.json').read_text())
    pages=[p for p in manifest if p['harvest_accepted']];unique=vouli.unique_call_pages(pages)
    if len(unique)*1500>3_000_000:raise ValueError('Google cap exceeded')
    prior=set()
    for wave in PRIOR_WAVES:
        p=REPO/f'docs/harvest/{wave}/records.jsonl'
        if wave=='round1':p=REPO/'docs/harvest/round1/records_all.jsonl'
        for r in read_jsonl(p):prior.add(r['image_sha256'])
    duplicate=prior&{p['image_sha256'] for p in pages}
    if duplicate:raise ValueError('page already read in previous wave; must reuse existing receipts')
    inputs={relative(OUT/n):sha(OUT/n) for n in ('books.json','manifest.json','slots.json','holdout_books.json','selection.json','selection_config.json','acquisition_results.json')}
    for wave in PRIOR_WAVES:
        p=REPO/f'docs/harvest/{wave}/admitted.jsonl'
        if p.exists():inputs[relative(p)]=sha(p)
    binding=json.loads((round1.OUT/'reads_d1/plan.json').read_text())['bindings']['docai']
    plan=dict(schema='t24c-plan-1',pages=pages,pages_rendered=len(manifest),pages_accepted=len(pages),page_count=len(pages),max_calls=len(unique),max_cost_usd=len(unique)*.0015,
        binding=binding,cap_usd=CAP,inputs=inputs,quality_limits=config['quality_limits'],gate_sha256=round1.GATE_SHA,admission_sha256=ADMISSION_SHA,
        automatic_retries=False,vision_calls=0,owner_approval='T24c explicit acquisition and Google reads, cap USD 3.00')
    frozen(OUT/'plan.json',plan)
    print(f"plan {len(pages)} pages; USD {len(unique)*.0015:.4f}",flush=True)


def load_plan():
    check();plan=json.loads((OUT/'plan.json').read_text())
    for p,h in plan['inputs'].items():
        if sha(REPO/p)!=h:raise ValueError('frozen input changed: '+p)
    return plan


def strip_response_images(raw):
    removed=0
    for p in raw.get('document',{}).get('pages',[]):
        if 'content' in p.get('image',{}):p['image'].pop('content');removed+=1
    raw['content_stripped']=dict(page_images_removed=removed,note='document.pages[*].image.content removed before persistence; page PNG is image of record')
    return raw


def compact_transport(*args,**kwargs):
    disk_check();response=requests.post(*args,**kwargs)
    class Response:
        status_code,headers=response.status_code,response.headers
        @property
        def text(self):return response.text
        def json(self):return strip_response_images(response.json())
    return Response()


class OpenArchivesReaders(vouli.VouliReaders):
    def __init__(self,plan,root=GOOGLE):
        super().__init__(plan,root=root);self.docai._transport=compact_transport


def read(plan):
    readers=OpenArchivesReaders(plan);pages=vouli.unique_call_pages(plan['pages']);statuses=[]
    def call(p):
        disk_check()
        if sha(REPO/p['image'])!=p['image_sha256']:raise ValueError('image changed before read')
        return p['id'],readers.call('docai',REPO/p['image'])['status']
    try:
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures={pool.submit(call,p):p for p in pages}
            for i,f in enumerate(as_completed(futures),1):
                ident,status=f.result();statuses.append(dict(id=ident,status=status))
                if i%10==0 or status!='ok':print(f"DocAI {i}/{len(pages)} {ident} {status}",flush=True)
                if status!='ok':
                    for pending in futures:pending.cancel()
                    raise RuntimeError('provider failure retained; no automatic retry')
    finally:
        atomic(OUT/'cost_receipt.json',readers.budget.receipt());atomic(OUT/'read_status.json',statuses)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['prepare','acquire','plan','read','build','validate','publish'])
    mode=parser.parse_args().mode
    try:
        if mode=='prepare':prepare()
        elif mode=='acquire':acquire()
        elif mode=='plan':prepare_plan()
        elif mode=='read':read(load_plan())
        else:
            from scripts.harvest import openarchives_outputs
            getattr(openarchives_outputs,mode)(load_plan())
    except LowDisk:
        from scripts.harvest import openarchives_outputs
        openarchives_outputs.abort_report()
        raise

if __name__=='__main__':main()

"""T26 resumable IA scans -> frozen gate -> at-most-once, automatic-language DocAI."""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from contextlib import closing
from datetime import datetime, timezone
import copy
import hashlib
import json
import multiprocessing
from pathlib import Path
import time
from urllib.parse import urlsplit
import pypdfium2 as pdfium
from PIL import Image
from greekocr.harvest import cyrillic as policy
from greekocr.harvest.readers import atomic, read_jsonl
from scripts.harvest import round1, round2, vouli, mixed
from scripts.harvest.round1_reads import frozen

REPO=round1.ROOT
OUT=REPO/'docs/records/harvest/cyrillic'
BULK=REPO/'docs/harvest/harvest_big/cyrillic'
GOOGLE=BULK/'google'
INPUT=Path.home()/'Projects/greek-page-ocr/docs/evidence/o4c'
CAP=1.20
ADMISSION_SHA=vouli.ADMISSION_SHA
sha,relative=vouli.sha,vouli.relative
PRIOR_WAVES=mixed.PRIOR_WAVES+('mixed',)


def binding():
    result=copy.deepcopy(json.loads((round1.OUT/'reads_d1/plan.json').read_text())['bindings']['docai'])
    result['options']['ocrConfig']['hints']['languageHints']=[]
    return result


def select():
    vouli.check_frozen();OUT.mkdir(parents=True,exist_ok=True)
    frozen(OUT/'git_before.json',round1.git_snapshot())
    rows=policy.candidates(read_jsonl(INPUT/'candidates.jsonl'))
    probes={r['document_id']:r for r in read_jsonl(INPUT/'media_probes.jsonl')}
    books=[]
    for r in rows:
        ident=r['document_id'];key=policy.key(ident)
        books.append(dict(book=ident,key=key,id6=key[:6],title=r['title'],year=r['year'],decade=r['year']//10*10,
            pages=r['pages'],media=policy.media(r),source_url=r['record_url'],source='archive_'+ident,
            attribution='; '.join(str(x) for x in [r.get('creator'), 'Internet Archive',r['title']] if x),
            licence=r['rights']['identifier'] if r['rights']['family']=='CC-BY' else 'public-domain',
            recorded_rights=r['rights'],catalogue_language=r['language'],origin='archive',
            print_review=r['print_review'],media_probe=probes.get(ident,r['media_probe'])))
    frozen(OUT/'source_books.json',books)
    frozen(OUT/'holdout_books.json',policy.holdout(books))
    limits=json.loads((_data_input(round1.OUT/'selection.json')).read_text())['quality_limits']
    frozen(OUT/'selection.json',dict(schema='t26-selection-1',seed=policy.SEED,holdout_seed=policy.HOLDOUT_SEED,
        books=books,quality_limits=limits,inputs={str(INPUT/n):sha(INPUT/n) for n in ('candidates.jsonl','media_probes.jsonl')},
        gate_sha256=round1.GATE_SHA,admission_sha256=ADMISSION_SHA,selected_candidates=rows))
    frozen(OUT/'run_state.json',dict(started_at=datetime.now(timezone.utc).isoformat()))
    print(f'selected {len(books)} items; holdout 2 test + 1 dev',flush=True)


class ArchiveHTTP(mixed.DirectHTTP):
    def __init__(self):
        import requests
        self.root=BULK/'archive_http';self.root.mkdir(parents=True,exist_ok=True)
        self.last={};self.session=requests.Session()
        self.session.headers.update({'User-Agent':'GreekOCR-research-harvest/1.0 (public source collection)', 'Accept-Encoding':'identity'})
    def download(self,url,path,limit=policy.MAX_BYTES):
        host=urlsplit(url).hostname or ''
        if not (host=='archive.org' or host.endswith('.archive.org')):
            raise ValueError('IA only')
        return super().download(url,path,limit=limit)


def gate_init(limits):mixed.gate_init(limits)


def render_book(task):
    book,pdf,receipt,limits=task
    gates,failed={},{}
    try:
        with pdfium.PdfDocument(pdf) as doc:
            book=dict(book,pages=len(doc),pdf_sha256=receipt['sha256'],pdf_bytes=receipt['bytes'],download_receipt=receipt)
            book['positions']=policy.sample(len(doc),book['book'])
            used=set()
            for pos in book['positions']:
                for n in pos['candidates']:
                    if n in used:continue
                    used.add(n)
                    ident=f"{book['key']}-p{n:06d}";saved=OUT/'gates'/(ident+'.json')
                    if saved.exists():
                        p=json.loads(saved.read_text())
                        if p['pdf_sha256']!=receipt['sha256'] or sha(REPO/p['image'])!=p['image_sha256']:
                            raise ValueError('resume source mismatch')
                    else:
                        image_path=BULK/'images'/f"{book['key']}-{n:06d}.png"
                        image_path.parent.mkdir(parents=True,exist_ok=True)
                        with closing(doc[n-1]) as page:
                            bitmap=page.render(scale=200/72,grayscale=True)
                            image=bitmap.to_pil().copy().convert('L');bitmap.close()
                        image.save(image_path,compress_level=3)
                        g=vouli.gate_image(image_path,mixed.STACK,mixed.GATE,limits)
                        p={k:book[k] for k in ('book','key','id6','title','year','decade','source_url','source','attribution','licence','origin')}
                        p.update(id=ident,page=n,image=relative(image_path),image_sha256=sha(image_path),
                            width=image.width,height=image.height,dpi=200,grayscale=True,read_batch='cyrillic',
                            gate=g,harvest_accepted=g['accepted'],pdf_sha256=receipt['sha256'],pdf_bytes=receipt['bytes'],
                            volume=None,volume_page=n)
                        atomic(saved,p)
                    gates[f"{book['key']}:{n}"]=p
                    if p['harvest_accepted']:break
        return dict(book=book,gates=gates,failed=failed)
    finally:
        Path(pdf).unlink(missing_ok=True)


def acquire():
    vouli.check_frozen();selection=json.loads((OUT/'selection.json').read_text())
    for name,digest in selection['inputs'].items():
        if sha(name)!=digest:raise ValueError('source input changed')
    http=ArchiveHTTP();results=[]
    limits=selection['quality_limits']
    with ProcessPoolExecutor(max_workers=1,mp_context=multiprocessing.get_context('spawn'),initializer=gate_init,initargs=(limits,)) as pool:
        for b in selection['books']:
            saved=OUT/'acquisitions'/(b['key']+'.json')
            if saved.exists():result=json.loads(saved.read_text())
            else:
                if b['media']['kind']!='pdf':raise ValueError('page-image fallback required; no small PDF')
                pdf=BULK/'pdf'/(b['key']+'.pdf')
                print(f"downloading {b['book']} ({b['media']['bytes']/1e6:.1f} MB)",flush=True)
                receipt=http.download(b['media']['url'],pdf)
                if receipt['bytes']!=b['media']['bytes']:raise ValueError('IA media byte count changed')
                probe=b['media_probe']
                if probe['probe_url']==b['media']['url']:
                    with pdf.open('rb') as f:prefix=f.read(probe['bytes'])
                    if hashlib.sha256(prefix).hexdigest()!=probe['prefix_sha256']:raise ValueError('IA prefix identity changed')
                result=pool.submit(render_book,(b,str(pdf),receipt,limits)).result()
                frozen(saved,result)
            results.append(result)
            gates={k:p for r in results for k,p in r['gates'].items()}
            books=[r['book'] for r in results];failed={k:p for r in results for k,p in r['failed'].items()}
            slots,_=round2.replay_slots(books,gates,failed)
            manifest=sorted(gates.values(),key=lambda p:(p['book'],p['page']))
            for name,data in [('books',books),('manifest',manifest),('slots',slots),('fetch_failures',failed)]:atomic(OUT/(name+'.json'),data)
            print(json.dumps(dict(items=len(books),rendered=len(manifest),accepted=sum(p['harvest_accepted'] for p in manifest))),flush=True)
    prepare_plan()


def prepare_plan():
    books=json.loads((OUT/'books.json').read_text());assert len(books)==13
    manifest=json.loads((OUT/'manifest.json').read_text());pages=[p for p in manifest if p['harvest_accepted']]
    prior=set()
    for name in PRIOR_WAVES:
        file=REPO/f'docs/harvest/{name}/records.jsonl'
        if name=='round1':file=REPO/'docs/records/harvest/round1/records_all.jsonl'
        prior.update(r['image_sha256'] for r in read_jsonl(file))
    if prior & {p['image_sha256'] for p in pages}:raise ValueError('previous-wave image read')
    calls=len(vouli.unique_call_pages(pages))
    if calls*1500>1_200_000:raise ValueError('cost cap exceeded before reads')
    inputs={relative(OUT/n):sha(OUT/n) for n in ('selection.json','source_books.json','holdout_books.json','books.json','manifest.json','slots.json','fetch_failures.json')}
    for name in PRIOR_WAVES:
        p=REPO/f'docs/harvest/{name}/admitted.jsonl'
        if p.exists():inputs[relative(p)]=sha(p)
    plan=dict(schema='t26-plan-1',pages=pages,binding=binding(),pages_rendered=len(manifest),pages_accepted=len(pages),page_count=len(pages),
        max_calls=calls,max_cost_usd=calls*.0015,cap_usd=CAP,inputs=inputs,quality_limits=json.loads((OUT/'selection.json').read_text())['quality_limits'],
        automatic_retries=False,vision_calls=0,admission_sha256=ADMISSION_SHA,gate_sha256=round1.GATE_SHA,
        owner_approval='T26 explicit IA acquisition and DocAI reads, USD 1.20; no language hints; automatic quality checks')
    frozen(OUT/'plan.json',plan);print(f"plan {len(pages)} pages, USD {calls*.0015:.4f}",flush=True)
    return plan


def load_plan():
    vouli.check_frozen();plan=json.loads((OUT/'plan.json').read_text())
    for path,digest in plan['inputs'].items():
        if sha(REPO/path)!=digest:raise ValueError('frozen input changed: '+path)
    if plan['binding']!=binding():raise ValueError('DocAI binding changed')
    return plan


class CyrillicReaders(vouli.VouliReaders):
    def __init__(self,plan,root=GOOGLE):super().__init__(plan,root=root)


def read(plan):
    old=vouli.OUT,vouli.VouliReaders
    try:
        vouli.OUT,vouli.VouliReaders=OUT,CyrillicReaders
        vouli.run(plan)
    finally:vouli.OUT,vouli.VouliReaders=old


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['select','acquire','plan','read','build','validate','publish'])
    mode=parser.parse_args().mode
    if mode=='select':select()
    elif mode=='acquire':acquire()
    elif mode=='plan':prepare_plan()
    elif mode=='read':read(load_plan())
    else:
        from scripts.harvest import cyrillic_outputs
        getattr(cyrillic_outputs,mode)(load_plan())

if __name__=='__main__':main()

"""T7 isolated, resumable harvest. All mutations stay beside this script."""
from __future__ import annotations
import collections
import hashlib
import html
import io
import json
import os
from pathlib import Path
import random
import re
import sys
sys.dont_write_bytecode = True
import subprocess
import time
import types
import unicodedata as ud
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
OUT = Path(__file__).resolve().parent
MAIN = ROOT.parent / 'greek-ocr-toolkit'
L1 = ROOT.parent / 'greek-ocr-toolkit-spellcheck-l1/artifacts/labelfix_l1/binding/L1_input_documents.txt'
from bs4 import BeautifulSoup
from PIL import Image
from greekocr.harvest import wikisource as policy
from scripts.harvest import wikisource as source

UA = 'greek-ocr-research/0.1 (foivos.karounos@gmail.com)'
source.UA = UA
source.HOSTS = {'el.wikisource.org', 'commons.wikimedia.org', 'upload.wikimedia.org'}
SEED = 'T7-wikisource-r0-20261017'
DEADLINE = 1792195354.0  # 2026-10-17 00:02:34 UTC, 90 minutes from preflight.

def sha(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def save(name, value):
    p = OUT / name; p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(p)

def jsonl(name, rows):
    p = OUT / name; p.parent.mkdir(parents=True, exist_ok=True)
    def encode(x):
        value=json.dumps(x,ensure_ascii=False,separators=(',',':'))
        # HTTP header Latin-1 may contain NEL; retain it reversibly without
        # making generic Unicode splitlines() consumers split a JSON record.
        for c in ['\u0085','\u2028','\u2029']:value=value.replace(c,'\\u'+format(ord(c),'04x'))
        return value+'\n'
    tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(''.join(encode(x) for x in rows));tmp.replace(p)

def load(name): return json.loads((OUT / name).read_text())
def rel(path): return str(Path(path).relative_to(ROOT))

def scrub_outputs():
    # Public custody needs revision/date/content headers, not tracking cookies
    # or client IPs. Complete original HTTP receipts remain in ignored limiter/.
    keep={'date','etag','last-modified','content-type','content-length','retry-after','x-database-lag'}
    def scrub(v):
        if isinstance(v,list):return [scrub(x) for x in v]
        if isinstance(v,dict):
            return {k:({a:b for a,b in x.items() if a.lower() in keep} if k=='headers' and isinstance(x,dict) else scrub(x)) for k,x in v.items()}
        return v
    for p in sorted(OUT.rglob('*')):
        if not p.is_file() or p.suffix not in {'.json','.jsonl'}:continue
        rp=p.relative_to(OUT)
        if rp.parts[0]=='exclusions' or p.name in {'books.jsonl','RUN_POLICY.json','T7B_INPUTS.json'}:continue
        if rp.parts[0] in {'limiter','page_records','scans','images','crops'} or rp.parts[:2]==('google','provider') or p.name=='COMMIT_MANIFEST.json':continue
        if p.suffix=='.json':save(str(rp),scrub(json.loads(p.read_text())))
        else:jsonl(str(rp),[scrub(json.loads(l)) for l in p.read_text().split('\n') if l.strip()])

def norm(text):
    return ' '.join(re.sub(r'[^\w]+', ' ', ''.join(c for c in ud.normalize('NFD', unquote(str(text)).replace('_', ' ').casefold()) if not ud.combining(c))).split())
def index_key(url):
    t = unquote(url).split('/wiki/')[-1].replace('_', ' ')
    return norm(re.sub(r'^(Index|Μεταγραφή):', '', t, flags=re.I))

def clean(raw):
    parsed=policy.strip_wikitext(raw)
    # Execute the unchanged stripper with whitespace-only normalization to keep
    # pre-NFC Unicode as well. Template and newline handling are identical.
    literal_strip=types.FunctionType(policy.strip_wikitext.__code__,dict(policy.__dict__,nfc=lambda s:' '.join(s.split())))
    literal=literal_strip(raw)
    assert len(parsed['lines'])==len(literal['lines'])
    for line,lit in zip(parsed['lines'],literal['lines']):
        assert ud.normalize('NFC',lit['text'])==line['text']
        line['literal']=lit['text']
        # The shared stripper conservatively retains poem indentation colons.
        # Native scan df94dc99/p14 shows these are not printed punctuation.
        # Exclude the affected source line; never edit its human label.
        if line['text'].startswith(':'):
            line.update(usable=False,exclusion_reason='unresolved_leading_wiki_indentation')
    return parsed

class HTTP(source.WikimediaHTTP):
    def __init__(self): super().__init__(root=OUT / 'limiter')
    def fetch(self, url):
        for attempt in range(4):
            if time.time()>=DEADLINE-60:raise RuntimeError('T7 wall-clock limit reached; no further network requests')
            data, receipt = self.get(url, refresh=attempt > 0)
            if receipt['status'] == 200: return data, receipt
            if receipt['status'] not in (429, 503): raise RuntimeError(f"HTTP {receipt['status']}: {url}")
            wait = next((v for k,v in receipt['headers'].items() if k.lower()=='retry-after'), '10')
            try: wait = float(wait)
            except ValueError:
                from email.utils import parsedate_to_datetime
                wait = max(0, parsedate_to_datetime(wait).timestamp()-time.time())
            if wait > 55: raise RuntimeError(f'Retry deferred {wait}s: {url}')
            time.sleep(max(wait, 2**attempt))
        raise RuntimeError('retry exhausted')

def discover():
    http = HTTP()
    urls = json.loads((ROOT/'docs/harvest/wikisource/discovery_candidates.json').read_text())['el']
    local = json.loads((ROOT/'docs/harvest/wikisource/source_books.json').read_text())
    excluded = {index_key(x['index_url']) for x in local}
    # These are discovery priorities only; final eligibility uses live quality.
    priorities = [131, 41, 143, 148, 145, 118, 121, 146, 147, 30, 34, 27, 36, 40, 119, 129, 134, 138, 144, 186, 219, 88, 71, 124]
    books = load('candidates.json') if (OUT/'candidates.json').exists() else []
    done = {index_key(x['index_url']) for x in books}
    for i in priorities:
        u = urls[i]
        if index_key(u) in excluded | done: continue
        try:
            data, receipt = http.fetch(u)
            soup = BeautifulSoup(data, 'html.parser')
            b = source.index_metadata(soup, u, 'el')
            allpages = []
            for a in soup.select('.prp-index-pagelist a[href]'):
                q = next((int(c[-1]) for c in a.get('class', []) if re.fullmatch('quality[0-4]', c)), None)
                if q is not None: allpages.append(q)
            fields = b['fields']
            b.update(candidate_number=i, index_title=unquote(u.split('/wiki/')[-1]).replace('_',' '),
                author=fields.get('Συγγραφέας', fields.get('Συγγραφεύς', '')),
                printer=fields.get('Εκδότης', fields.get('Εκδόσεις', '')),
                pagequality_distribution=dict(collections.Counter(allpages)),
                metadata_receipt=receipt)
            b['scan_file'] = unquote(b['thumbnail'].split('/commons/thumb/')[1].split('/')[2]) if b['thumbnail'] else None
            if b['scan_file']: b['key'] = hashlib.sha256(('el:'+b['scan_file']).encode()).hexdigest()[:8]
            books.append(b); save('candidates.json', books)
            print(i, b['year'],len(b['eligible_pages']),b['title'],fields,flush=True)
        except Exception as e: print(i,type(e).__name__,str(e)[:180],flush=True)

def exclusions():
    ids = set(L1.read_text().splitlines())
    groups = {x:dict(document_id=x, book_key=x.split(':',1)[1], sources=[], source_urls=[], years=[], titles=[], authors=[], metadata=[]) for x in ids}
    cp = MAIN/'docs/harvest/collection'
    hashes = {str(L1):sha(L1)}
    for name in ['import_real_all.jsonl', 'admitted_all.jsonl']:
        p=cp/name; hashes[str(p)]=sha(p)
        with p.open() as f:
            for line in f:
                x=json.loads(line)
                d=x.get('doc') or (x['wave']+':'+x['book_key'])
                d=re.sub(r'-p\d+$','',d)
                if d not in groups: continue
                g=groups[d]
                for target,field in [('sources','source'),('source_urls','source_url'),('years','year')]:
                    v=x.get(field)
                    if v is not None and v not in g[target]:g[target].append(v)
                if x.get('attribution') and x['attribution'] not in g.setdefault('attributions',[]):g['attributions'].append(x['attribution'])
    for wave in ['round1','round2','mixed','openarchives','vouli','parliament']:
        for name in ['selection.json','plan.json','manifest.json']:
            p=MAIN/'docs/harvest'/wave/name
            if not p.exists():continue
            hashes[str(p)]=sha(p)
            x=json.loads(p.read_text())
            items=x if isinstance(x,list) else x.get('books',x.get('pages',[]))
            if isinstance(items,dict): items=list(items.values())
            for b in items:
                if not isinstance(b,dict):continue
                key=b.get('key',b.get('book_key'))
                d=wave+':'+str(key)
                if d not in groups:continue
                g=groups[d]
                for target,field in [('titles','title'),('authors','author'),('years','year')]:
                    v=b.get(field)
                    if v is not None and v not in g[target]:g[target].append(v)
                # Retain bibliographic metadata, never line labels or credentials.
                meta={k:v for k,v in b.items() if k in ['book','title','author','year','scan_file','index_url','catalogue','external_row']}
                if meta and meta not in g['metadata']:g['metadata'].append(meta)
    jsonl('exclusions/l1_documents.jsonl', [groups[x] for x in sorted(groups)])
    save('exclusions/input_hashes.json',hashes)
    print('L1',len(groups),'source resolved',sum(bool(g['sources']) for g in groups.values()),'title resolved',sum(bool(g['titles']) for g in groups.values()))
    for g in groups.values():
        if not g['titles']:print('no title',g['document_id'],g['sources'],g['source_urls'])

def scan_metadata(http, b, download=True):
    u='https://commons.wikimedia.org/wiki/File:'+quote(b['scan_file'],safe='')
    data, receipt=http.fetch(u)
    soup=BeautifulSoup(data,'html.parser')
    a=soup.select_one('.fullMedia a.internal') or soup.select_one('.fullMedia a')
    if not a: raise ValueError('Commons original file link missing')
    url=a['href'].split('?')[0]
    if urlsplit(url).hostname!='upload.wikimedia.org':raise ValueError('not Commons upload')
    b.update(commons_url=u,scan_url=url,commons_receipt=receipt)
    rights=soup.select_one('a[href*="creativecommons.org/publicdomain/mark"]')
    b['scan_rights']='Commons public domain mark' if rights else 'See frozen Commons file description'
    if download:
        data, sr=http.fetch(url)
        path=OUT/'scans'/b['scan_file'];path.parent.mkdir(exist_ok=True)
        if not path.exists():path.write_bytes(data)
        b.update(scan_sha1=sha(path,'sha1'),scan_sha256=sha(path),scan_path=rel(path),scan_bytes=path.stat().st_size,scan_receipt=sr)
    return b

def freeze():
    http=HTTP()
    candidates=load('candidates.json')
    numbers=[124,71,27,146,40]
    selected=[]
    for n in numbers:
        b=next(x for x in candidates if x['candidate_number']==n)
        if not b['scan_file'] or not b['author'] or not b['year'] or not b['eligible_pages']:raise ValueError('ineligible book')
        b=scan_metadata(http,b)
        eligible=sorted(b['eligible_pages'],key=lambda x:x['page'])
        chosen=sorted(random.Random(SEED+':'+b['key']).sample(eligible,min(30,len(eligible))),key=lambda x:x['page'])
        b.update(drawn_pages=chosen,sampling_seed=SEED+':'+b['key'],sampling='random.sample without replacement from every quality-3/4 page',
            document_ids=['wikisource:'+b['key'],'mixed:'+b['key']],stratum='i-b',split='locked_test_R0',train_pool_eligible=False,training_release_allowed=False)
        selected.append(b);jsonl('books.jsonl',selected)
        print('frozen',b['key'],b['year'],b['title'],'sha1',b['scan_sha1'],flush=True)

def local_hashes():
    http=HTTP()
    books=json.loads((ROOT/'docs/harvest/wikisource/source_books.json').read_text())
    rows=load('exclusions/local20_books.json') if (OUT/'exclusions/local20_books.json').exists() else []
    done={b['key'] for b in rows}
    for old in books:
        if old['lang']!='el' or old['key'] in done:continue
        b={k:old.get(k) for k in ['key','title','year','scan_file','index_url','fields']}
        b['author']=b['fields'].get('Συγγραφέας','')
        b=scan_metadata(http,b)
        b['document_ids']=['wikisource:'+b['key'],'mixed:'+b['key']]
        rows.append(b);save('exclusions/local20_books.json',rows)
        print('local20 scan hash',len(rows),b['key'],b['scan_bytes'],flush=True)

def acquire():
    http=HTTP();pages=[]
    books=[json.loads(x) for x in (OUT/'books.jsonl').read_text().splitlines()]
    for b in books:
        for q in b['drawn_pages']:
            pid=f"{b['key']}-p{q['page']:06d}"
            record=OUT/'page_records'/(pid+'.json')
            if record.exists():pages.append(json.loads(record.read_text()));continue
            raw,rr=http.fetch(q['url']+'?action=raw')
            rawpath=OUT/'wikitext'/(pid+'.txt');rawpath.parent.mkdir(exist_ok=True);rawpath.write_bytes(raw)
            parsed=clean(raw.decode('utf-8'))
            if parsed['proofread_level'] not in (3,4):raise ValueError('proofread status changed')
            image=OUT/'images'/(pid+'.png');image.parent.mkdir(exist_ok=True)
            if not image.exists():
                assert len(list((OUT/'images').glob('*.png')))<150,'total physical page acquisition cap'
                if b['scan_file'].lower().endswith('.pdf'):
                    result=subprocess.run(['pdftoppm','-f',str(q['page']),'-l',str(q['page']),'-singlefile','-scale-to','3000','-gray','-png',str(ROOT/b['scan_path']),str(image.with_suffix(''))],capture_output=True)
                    if result.returncode:raise RuntimeError('PDF rendering failed')
                    render=dict(tool='pdftoppm',scale_to=3000,grayscale=True,scan_page=q['page'])
                else:
                    url=source.thumbnail_url(dict(b,**q),width=3840)
                    data,ir=http.fetch(url)
                    with Image.open(io.BytesIO(data)) as im:
                        im=im.convert('L');served=list(im.size);im.thumbnail((3000,3000),Image.Resampling.LANCZOS);im.save(image)
                    render=dict(tool='Commons DjVu JPEG thumbnail',url=url,receipt=ir,served_size=served,scale_to=3000,grayscale=True,scan_page=q['page'])
            else: render=dict(tool='previous verified rendering',scale_to=3000,scan_page=q['page'])
            with Image.open(image) as im:width,height=im.size
            p=dict(page_id=pid,book_key=b['key'],page=q['page'],source_url=q['url'],index_url=b['index_url'],scan_file=b['scan_file'],scan_sha1=b['scan_sha1'],
                quality=parsed['proofread_level'],quality_at_draw=q['quality'],image=rel(image),image_sha256=sha(image),width=width,height=height,
                render=render,wikitext=rel(rawpath),wikitext_sha256=sha(rawpath),wikitext_receipt=rr,
                cleaned=parsed,geometry=None,google_status='not_read',stratum='i-b',split='locked_test_R0',train_pool_eligible=False,training_release_allowed=False)
            save('page_records/'+pid+'.json',p);pages.append(p)
            jsonl('pages.jsonl',pages)
            print('acquired',len(pages),pid,'human lines',len(parsed['lines']),flush=True)
    jsonl('pages.jsonl',pages)

def keysets(book):
    return dict(document_id=set(book.get('document_ids',[])),
        index_title={index_key(book.get('index_url',''))}-{''},
        commons_filename={norm(book.get('scan_file',''))}-{''},
        scan_sha1={book.get('scan_sha1','')}-{''},
        title_author_year={norm(book['title'])+'|'+norm(book['author'])+'|'+str(book['year'])} if book.get('author') and book.get('year') else set(),
        title_year={norm(book['title'])+'|'+str(book['year'])} if book.get('year') else set(),
        title_only={norm(book['title'])},
        upstream_source_url=set(book.get('upstream_source_urls',[])))

def enrich_origins():
    groups=[]
    groups.append(('books.jsonl',[json.loads(x) for x in (OUT/'books.jsonl').read_text().splitlines()]))
    groups.append(('exclusions/local20_books.json',load('exclusions/local20_books.json')))
    rawmeta={x['book_key']:x for x in load('commons_bibliography.json')}
    for name,books in groups:
        for b in books:
            receipt=b['commons_receipt']
            body=Path(receipt['body_path']);body=body if body.is_absolute() else ROOT/body
            text=body.read_text()
            if b['key'] in rawmeta:
                receipt2=rawmeta[b['key']]['receipt'];bp=Path(receipt2['body_path']);bp=bp if bp.is_absolute() else ROOT/bp
                text+='\n'+bp.read_text()
            urls=re.findall(r'https?://anemi\.lib\.uoc\.gr(/metadata/[^\s"<>\[\]]+?\.tkl)',html.unescape(text))
            paths=sorted(set(unquote(p) for p in urls))
            b['upstream_source_urls']=['anemi.lib.uoc.gr'+p for p in paths]
            b['upstream_anemi_record_ids']=paths
            ids=set(b.get('document_ids',[]))
            for path in paths:
                key=hashlib.sha256(path.encode()).hexdigest()[:24]
                ids.update(wave+':'+key for wave in ['round1','round2','mixed'])
            b['document_ids']=sorted(ids)
        if name.endswith('.jsonl'):jsonl(name,books)
        else:save(name,books)

def disjointness():
    enrich_origins()
    books=[json.loads(x) for x in (OUT/'books.jsonl').read_text().splitlines()]
    local=load('exclusions/local20_books.json')
    assert len(local)==20 and len(books)==5
    l1=[json.loads(x) for x in (OUT/'exclusions/l1_documents.jsonl').read_text().splitlines()]
    targets={k:set() for k in keysets(books[0])}
    coverage={k:0 for k in targets}
    for g in l1:
        targets['document_id'].update([g['document_id'],'wikisource:'+g['book_key'],'mixed:'+g['book_key']]);coverage['document_id']+=1
        # Resolve bibliography from saved catalogues; no forbidden source hosts.
        vals={k:set() for k in targets}
        for u in g['source_urls']:
            z=urlsplit(u)
            if z.hostname=='anemi.lib.uoc.gr':vals['upstream_source_url'].add(z.hostname+unquote(z.path))
        authors=list(g['authors'])
        for title in g['titles']:
            if '/' in title:authors.append(title.split('/',1)[1].split(';')[0].strip())
            title=title.split('/',1)[0].strip(' [].')
            aliases={norm(title),norm(title.split(':',1)[0])}
            vals['title_only'].update(aliases)
            for y in g['years']:
                vals['title_year'].update(t+'|'+str(y) for t in aliases)
                vals['title_author_year'].update(t+'|'+norm(a)+'|'+str(y) for t in aliases for a in authors if a)
        for m in g['metadata']:
            for k,v in [('index_title',m.get('index_url')),('commons_filename',m.get('scan_file')),('scan_sha1',m.get('scan_sha1'))]:
                if v:vals[k].add(index_key(v) if k=='index_title' else norm(v) if k=='commons_filename' else v)
        for k,v in vals.items():
            if v:coverage[k]+=1;targets[k].update(v)
    selected={k:set().union(*(keysets(b)[k] for b in books)) for k in targets}
    localsets={k:set().union(*(keysets(b)[k] for b in local)) for k in targets}
    result=dict(schema='t7-disjointness-1',l1_documents=318,local_books=20,
        mapping='collection import_real_all.doc = wave:book_key, except repaired lexicon uses wave:page_id; admitted_all recovers book_key',
        l1_key_coverage=coverage,selected_coverage={k:sum(bool(keysets(b)[k]) for b in books) for k in targets},
        local_key_coverage={k:sum(bool(keysets(b)[k]) for b in local) for k in targets},
        intersections={k:dict(L1=sorted(selected[k]&targets[k]),local20=sorted(selected[k]&localsets[k])) for k in targets},
        limitation='No L1 source is Wikisource/Commons in the collection manifests: Index/file/SHA1 keys are not applicable there. Bibliographic title-only aliases are additionally checked across all 318 sources; unknown years/authors are not invented.')
    assert all(not v['L1'] and not v['local20'] for v in result['intersections'].values())
    assert coverage['title_only']==318
    save('exclusions/disjointness.json',result)
    print('zero intersections on',len(targets),'resolved key types',flush=True)

def reads():
    import fcntl
    import requests
    import google.auth
    from google.auth.transport.requests import Request
    from greekocr.harvest.readers import Budget
    from greekocr.readers.services.google_docai import DocAIReader, DEFAULT_VERSION
    from greekocr.harvest.page_reads import _response_geometry
    continuation=load('T7B_POLICY.json')
    deadline=continuation['deadline_epoch']
    # Reuse the frozen selection and exclusions without rewriting their receipts.
    for path,digest in load('T7B_INPUTS.json')['files'].items():
        if sha(ROOT/path)!=digest:raise ValueError('frozen T7 input changed')
    assert all(not v['L1'] and not v['local20'] for v in load('exclusions/disjointness.json')['intersections'].values())
    save('google/preflight.json',dict(discovery='google.auth.default',environment_override_present=bool(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')),credential_value_logged=False,credential_path_logged=False,reservation_made=False))
    class RateSession(requests.Session):
        def send(self, request, **kwargs):
            host=urlsplit(request.url).hostname
            if host not in {'oauth2.googleapis.com','eu-documentai.googleapis.com'}:raise ValueError('Google host outside allowlist')
            if time.time()>=deadline-60:raise RuntimeError('T7b wall-clock limit reached')
            (OUT/'limiter').mkdir(exist_ok=True)
            state=OUT/'limiter'/('google-'+host+'.json')
            with state.with_suffix('.lock').open('a') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX)
                last=json.loads(state.read_text()).get('last',0) if state.exists() else 0
                time.sleep(max(0,1.05-(time.time()-last)))
                save(rel(state).removeprefix(rel(OUT)+'/'),dict(last=time.time()))
                started=time.time();kwargs['allow_redirects']=False
                response=super().send(request,**kwargs)
                with (OUT/'google/network.jsonl').open('a') as f:f.write(json.dumps(dict(host=host,path=urlsplit(request.url).path,started_at=started,status=response.status_code))+'\n')
                return response
    session=RateSession()
    scopes=['https://www.googleapis.com/auth/cloud-platform']
    creds,_=google.auth.default(scopes=scopes,quota_project_id='ocr-ground-truth-20261008',request=Request(session=session))
    # Credential contents and refresh headers are never persisted or printed.
    class Reader(DocAIReader):
        def _ledger(self,row):
            if 'error' in row:row=dict(row,error='provider failure details suppressed to protect credentials')
            super()._ledger(row)
        def _headers(self):
            headers={'Content-Type':'application/json','x-goog-user-project':self.user_project}
            creds.before_request(Request(session=session),'POST',self.endpoint,headers)
            return headers
    reader=Reader('ocr-ground-truth-20261008','eu','9a98b7aca3c19561',version=DEFAULT_VERSION,
        receipts_dir=OUT/'google/provider',credentials=creds,transport=session.post)
    # Refresh before reserving any billable OCR read.
    reader._headers()
    budget=Budget(OUT/'google/ledger.jsonl',cap=.30,max_calls=116)
    pages=[json.loads(x) for x in (OUT/'pages.jsonl').read_text().splitlines()]
    reserved={r['key'] for r in __import__('greekocr.harvest.readers',fromlist=['read_jsonl']).read_jsonl(budget.path)}
    for i,p in enumerate(pages):
        if time.time()>=deadline-60:raise RuntimeError('T7b wall-clock limit reached; no further Google calls')
        if p['google_status']=='ok':continue
        parsed=clean((ROOT/p['wikitext']).read_text());p['cleaned']=parsed
        if not any(x['usable'] for x in parsed['lines']):raise ValueError('drawn page has no usable human text')
        if p['image_sha256'] in reserved:raise RuntimeError('previous reserved read requires reconciliation; no automatic retry')
        budget.reserve('docai',p['image_sha256']);reserved.add(p['image_sha256'])
        reading=reader.read(ROOT/p['image'],expected_sha256=p['image_sha256'])
        rawpath=Path(reading.raw_json_path);raw=json.loads(rawpath.read_text())
        geometry=_response_geometry('docai',raw,(p['width'],p['height']))
        geometry.pop('symbols',None)  # Raw symbols remain hash-bound in provider evidence.
        provider_page=raw['document']['pages'][0]
        p.update(google_status='ok',geometry=geometry,
            google=dict(receipt_id=reading.receipt_id,raw_path=rel(rawpath),raw_sha256=sha(rawpath),binding=reader.binding(),
                page_dimension=provider_page.get('dimension'),line_boxes=provider_page.get('lines',[]),token_boxes=provider_page.get('tokens',[]),
                transforms=provider_page.get('transforms',[]),token_box_frame='provider returned page; inverse_to_native is in geometry.coordinate_frame'))
        save('page_records/'+p['page_id']+'.json',p);pages[i]=p;jsonl('pages.jsonl',pages)
        print('Google',i+1,'/',len(pages),p['page_id'],'lines',len(geometry['lines']),'reserved USD',budget.receipt()['cost_usd'],flush=True)
    save('google/cost_receipt.json',budget.receipt())

def refresh():
    books=[json.loads(x) for x in (OUT/'books.jsonl').read_text().splitlines()]
    pages=[]
    for b in books:
        if b['key']=='df94dc99':
            b['printer']='ΤΥΠΟΙΣ Π. ΣΟΥΤΣΑ ΚΑΙ Δ. ΚΤΕΝΑ.'
            b['printer_evidence']=dict(method='native title-page inspection',scan_page=1,image=rel(OUT/'images/ancillary-df94dc99-p000001.png'),image_sha256=sha(OUT/'images/ancillary-df94dc99-p000001.png'))
        elif b['key']=='e90ad4c2':
            b['printer']='Τὰ Γράμματα, Ἀλεξάντρεια'
            b['printer_evidence']=dict(method='native title-page inspection; imprint says ΤΟ ΤΥΠΩΣΑΝ ΤΑ ΓΡΑΜΜΑΤΑ',scan_page=1,image=rel(OUT/'images/e90ad4c2-p000001.png'),image_sha256=sha(OUT/'images/e90ad4c2-p000001.png'))
        receipt=b['metadata_receipt'];body=Path(receipt['body_path']);body=body if body.is_absolute() else ROOT/body
        soup=BeautifulSoup(body.read_bytes(),'html.parser')
        links=soup.select('.prp-index-pagelist a[href]')
        b['pagequality_distribution']['uncreated']=sum(not any(re.fullmatch('quality[0-4]',c) for c in a.get('class',[])) for a in links)
        b['index_scan_pages']=len(links)
        b['metadata_method']='robots-permitted Index and Commons HTML/raw; standard query API disallowed, allowed mobileview action retired'
        for q in b['drawn_pages']:
            pid=f"{b['key']}-p{q['page']:06d}";p=load('page_records/'+pid+'.json')
            p['cleaned']=clean((ROOT/p['wikitext']).read_text());save('page_records/'+pid+'.json',p);pages.append(p)
    jsonl('books.jsonl',books);jsonl('pages.jsonl',pages)
    (OUT/'google/ledger.jsonl').touch(exist_ok=True)
    (OUT/'crops').mkdir(exist_ok=True)
    save('RUN_POLICY.json',dict(start_utc='2026-10-16T22:32:34Z',deadline_utc='2026-10-17T00:02:34Z',
        maximum_scan_pages=150,maximum_pages_per_book=40,google_cap_usd=.30,price_per_page_usd=.0015,
        seed=SEED,user_agent=UA,minimum_request_interval_s=1.05,
        allowed_hosts=sorted(source.HOSTS|{'eu-documentai.googleapis.com','oauth2.googleapis.com'}),
        processor=dict(project='ocr-ground-truth-20261008',location='eu',processor='9a98b7aca3c19561',version='pretrained-ocr-v2.1-2024-08-07'),
        ledger='docs/harvest/wikisource_r0/google/ledger.jsonl',limiter='docs/harvest/wikisource_r0/limiter/',
        purpose='locked test R0, stratum i-b; prohibited from every training release'))

def align():
    import math
    pages=[json.loads(x) for x in (OUT/'pages.jsonl').read_text().splitlines()]
    rejection_path=OUT/'qa/source_line_rejections.json'
    native_rejections={r['line_id']:r for r in load('qa/source_line_rejections.json')['rejections']} if rejection_path.exists() else {}
    records=[];audits=[]
    for p in pages:
        if p['google_status']!='ok':
            audits.append(dict(page_id=p['page_id'],status=p['google_status'],aligned=0));continue
        human=clean((ROOT/p['wikitext']).read_text())
        rows=[x for x in p['geometry']['lines'] if x['source']=='lines']
        assignments,blocks=policy.align_lines([x['text'] for x in rows],human['lines'])
        aligned=0;rejections=[]
        with Image.open(ROOT/p['image']) as image:
            for i,(r,a) in enumerate(zip(rows,assignments)):
                if a['alignment']!='aligned':continue
                j=a['human_line_indices'][0];h=human['lines'][j]
                assert h['usable'] and policy.UNKNOWN not in h['text']
                if not any('\u0370'<=ch<='\u03ff' or '\u1f00'<=ch<='\u1fff' for ch in h['text']):
                    rejections.append(dict(google_index=i,human_index=j,reason='no_Greek_character'));continue
                box=r['bbox']
                cropbox=[max(0,math.floor(box[0])-4),max(0,math.floor(box[1])-2),min(image.width,math.ceil(box[2])+4),min(image.height,math.ceil(box[3])+2)]
                if cropbox[2]<=cropbox[0] or cropbox[3]<=cropbox[1]:raise ValueError('invalid crop')
                lid='r0-ws-'+p['page_id']+f'-l{i+1:04d}'
                if lid in native_rejections:
                    witness=native_rejections[lid]
                    assert witness['record']['human_label_literal']==h['literal'] and witness['record']['human_label_nfc']==h['text']
                    rejections.append(dict(google_index=i,human_index=j,line_id=lid,reason=witness['reason'],finding=witness['finding']))
                    continue
                crop=OUT/'crops'/p['book_key']/(lid+'.png');crop.parent.mkdir(parents=True,exist_ok=True)
                image.crop(cropbox).save(crop)
                record=dict(line_id=lid,document_id='wikisource:'+p['book_key'],book_key=p['book_key'],page_id=p['page_id'],page=p['page'],source_url=p['source_url'],
                    index_url=p['index_url'],pagequality=p['quality'],scan_sha1=p['scan_sha1'],image_sha256=p['image_sha256'],
                    crop_path=rel(crop),crop_sha256=sha(crop),crop_bbox=cropbox,crop_size=[cropbox[2]-cropbox[0],cropbox[3]-cropbox[1]],google_line_bbox=box,
                    human_label_literal=h['literal'],human_label_nfc=h['text'],label=h['text'],
                    alignment=dict(a,google_line_index=i,human_source_line=h['cleaned_line'],google_text=r['text'],
                        minimum_similarity=.65,policy_path='greekocr/harvest/wikisource.py',policy_sha256=sha(ROOT/'greekocr/harvest/wikisource.py'),
                        wikitext_sha256=p['wikitext_sha256'],google_receipt_id=p['google']['receipt_id']),
                    human_transcription_licence='CC-BY-SA-4.0 (Wikisource contributors)',
                    split='locked_test_R0',stratum='i-b',train_pool_eligible=False,training_release_allowed=False)
                records.append(record);aligned+=1
        save('assignments/'+p['page_id']+'.json',dict(page_id=p['page_id'],blocks=blocks,assignments=assignments,rejections=rejections))
        audits.append(dict(page_id=p['page_id'],book_key=p['book_key'],page=p['page'],status='ok',google_lines=len(rows),human_lines=len(human['lines']),aligned=aligned,
            aligned_share=aligned/len(rows) if rows else None,
            native_source_rejections=sum(r.get('reason')=='native_source_label_discrepancy' for r in rejections),
            unknown_templates=human['unknown_templates'],excluded_template_lines=sum(not h['usable'] for h in human['lines'])))
        print('aligned',p['page_id'],aligned,'/',len(rows),flush=True)
    jsonl('lines.jsonl',records);save('alignment_summary.json',dict(pages=audits,lines=len(records),aligned_per_page=len(records)/len(pages) if pages else 0,
        rate_denominator='provider physical line boxes, including non-Greek headings and page numbers',
        policy_sha256=sha(ROOT/'greekocr/harvest/wikisource.py')))

if __name__=='__main__':
    if sys.argv[1]=='reads':
        try: reads()
        except Exception as error:
            save('google/failure.json',dict(error_class=type(error).__name__,details='suppressed to protect credential material; no automatic retry'))
            raise SystemExit('Google reads stopped ('+type(error).__name__+'); credential/error details suppressed') from None
    else: globals()[sys.argv[1]]()

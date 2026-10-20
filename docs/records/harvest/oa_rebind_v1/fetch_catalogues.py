"""Bounded public catalogue reads, with contact UA, robots and per-host pacing."""
from __future__ import annotations
import collections, concurrent.futures, datetime, hashlib, json, re, subprocess, threading, time
import urllib.parse, urllib.robotparser
from pathlib import Path
from bs4 import BeautifulSoup
from audit import OUT, write, sha, canonical_url
from greekocr._vendor.scripts.fetch.o4c_common import robots_allowed

UA='greek-ocr-research/0.1 (foivos.karounos@gmail.com)'
LOCK=threading.RLock();HOST_LOCKS=collections.defaultdict(threading.Lock);LAST={};ROBOTS={};STOPPED=set()
HTTP=OUT/'receipts/http.jsonl'
RAW_OPTIONS=[]
if HTTP.exists():
    for line in HTTP.read_text().splitlines():
        h=json.loads(line);LAST[h['host']]=max(LAST.get(h['host'],0),time.monotonic()-(time.time()-h['started_unix']))
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
class Blocked(Exception):pass
def raw(url,kind,delay=1.1):
    host=urllib.parse.urlsplit(url).netloc
    if host in STOPPED:raise Blocked('host stopped after HTTP 429/503')
    key=sha(url.encode());bodypath=OUT/'receipts/bodies'/f'{key}.body';headpath=bodypath.with_suffix('.headers')
    bodypath.parent.mkdir(parents=True,exist_ok=True)
    with HOST_LOCKS[host]:
        time.sleep(max(0,LAST.get(host,0)+max(1.1,delay)-time.monotonic()))
        start=time.time();LAST[host]=time.monotonic()
        proc=subprocess.run(['/usr/bin/curl','-q','-sS','--max-time','35','--max-filesize','8000000','--compressed',*RAW_OPTIONS,'-A',UA,'-D',str(headpath),'-o',str(bodypath),'-w','%{http_code}',url],capture_output=True)
    if not bodypath.exists():bodypath.write_bytes(b'')
    b=bodypath.read_bytes()
    headers={}
    for line in (headpath.read_text(errors='replace') if headpath.exists() else '').splitlines():
        if ':' in line:
            k,v=line.split(':',1);headers[k.lower()]=v.strip()
    status=int(proc.stdout or 0)
    rec=dict(url=url,host=host,kind=kind,status=status,started_unix=start,started_at=datetime.datetime.fromtimestamp(start,datetime.timezone.utc).isoformat(),ended_at=stamp(),seconds=time.time()-start,bytes=len(b),sha256=sha(b),body=str(bodypath.relative_to(OUT)),headers=str(headpath.relative_to(OUT)),user_agent=UA,curl_options=list(RAW_OPTIONS),curl_exit=proc.returncode,error=proc.stderr.decode(errors='replace')[:500],rate_interval_seconds=max(1.1,delay))
    with LOCK:
        with HTTP.open('a') as f:f.write(json.dumps(rec,ensure_ascii=False)+'\n')
    if status in [429,503]:STOPPED.add(host)
    return rec,b,headers
def robot(url):
    p=urllib.parse.urlsplit(url);origin=p.scheme+'://'+p.netloc
    # Whole host runs serially, so robot population cannot race.
    if origin not in ROBOTS:
        ru=origin+'/robots.txt'
        for _ in range(6):
            r,b,h=raw(ru,'robots')
            if r['status'] in [301,302,303,307,308] and h.get('location'):
                ru=urllib.parse.urljoin(ru,h['location']);continue
            break
        text=b.decode('utf8','replace') if r['status']==200 and r['curl_exit']==0 else ''
        allowed_missing=r['status'] in [404,410]
        if not text and not allowed_missing:text='User-agent: *\nDisallow: /'
        rp=urllib.robotparser.RobotFileParser();rp.parse(text.splitlines())
        delay=rp.crawl_delay(UA) or 0
        ROBOTS[origin]=dict(text=text,delay=delay,status=r['status'],receipt=r,missing_allowed=allowed_missing)
        write('receipts/robots/'+sha(origin.encode())+'.json',dict(origin=origin,**ROBOTS[origin]))
    policy=ROBOTS[origin]
    if not robots_allowed(policy['text'],url,UA):raise Blocked('robots disallow or unavailable: '+url)
    return max(1.1,policy['delay'])
def get(url,kind='catalogue'):
    for _ in range(8):
        delay=robot(url);r,b,h=raw(url,kind,delay)
        if r['status'] in [301,302,303,307,308] and h.get('location'):
            url=urllib.parse.urljoin(url,h['location']);continue
        if r['status']!=200 or r['curl_exit']:raise Blocked(f"HTTP {r['status']} curl {r['curl_exit']}: {url}")
        return r,b
    raise Blocked('redirect limit')

def parse(book,r,b):
    s=BeautifulSoup(b,'html.parser');meta=collections.defaultdict(list)
    for el in s.select('meta[content]'):
        n=(el.get('name') or el.get('property') or '').lower()
        if n:meta[n].append(el['content'])
    def vals(names):return [dict(field=k,value=v) for k in names for v in meta.get(k,[])]
    titles=vals(['citation_title','dc.title','dcterms.title','og:title'])
    dates=vals(['citation_date','citation_publication_date','dc.date.issued','dcterms.issued'])
    types=vals(['dc.type','dcterms.type','citation_dissertation_institution','og:type'])
    links=[urllib.parse.urljoin(r['url'],a['href']) for a in s.select('a[href],link[rel="item"][href]')]+meta.get('citation_pdf_url',[])
    # Exact canonical match preserves query, path-only match is separately labelled.
    exact=[u for u in links if canonical_url(u)==book['canonical_pdf_url']]
    finalmatches=[u for u in links if canonical_url(u)==canonical_url(book['download_final_url'])]
    path=urllib.parse.unquote(urllib.parse.urlsplit(book['pdf_url']).path)
    pathmatches=[u for u in links if urllib.parse.urlsplit(u).netloc==urllib.parse.urlsplit(book['pdf_url']).netloc and urllib.parse.unquote(urllib.parse.urlsplit(u).path)==path]
    title=titles[0]['value'] if titles else None
    date=dates[0]['value'] if dates else None
    ys=re.findall(r'(?<!\d)(?:1[5-9]\d{2}|20[0-2]\d)(?!\d)',date or '')
    return dict(book_key=book['book_key'],catalogue_url=book['link_table']['external_link'],final_url=r['url'],http_receipt=r,title=title,title_evidence=titles,date_raw=date,date_evidence=dates,year=int(ys[0]) if len(set(ys))==1 else None,type_evidence=types,rights_evidence=vals(['dc.rights','dcterms.rights','dc.rights.uri']),attachment_exact_matches=exact,attachment_final_matches=finalmatches,attachment_path_matches=pathmatches,title_element=s.title.get_text(' ',strip=True) if s.title else None,headings=[h.get_text(' ',strip=True) for h in s.select('h1')],verified=bool(title and (exact or pathmatches or finalmatches)))
def one(book):
    path=OUT/'receipts/catalogues'/f"{book['book_key']}.json"
    if path.exists():return json.loads(path.read_text())
    try:
        r,b=get(book['link_table']['external_link']);result=parse(book,r,b)
    except Exception as e:result=dict(book_key=book['book_key'],catalogue_url=book['link_table']['external_link'],verified=False,error=str(e))
    write('receipts/catalogues/'+book['book_key']+'.json',result)
    print(book['book_key'],book['link_table']['collection_slug'],bool(result.get('title')),result.get('year'),result.get('verified'),result.get('error',''),flush=True)
    return result
def host(books):return [one(b) for b in books]
if __name__=='__main__':
    books=json.loads((OUT/'receipts/initial-bindings.json').read_text());groups=collections.defaultdict(list)
    for b in books:
        if b['link_table']:groups[urllib.parse.urlsplit(b['link_table']['external_link']).netloc].append(b)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        result=[r for group in pool.map(host,groups.values()) for r in group]
    write('receipts/catalogue-summary.json',dict(at=stamp(),attempted=len(result),title=sum(bool(r.get('title')) for r in result),verified=sum(r.get('verified',False) for r in result)))

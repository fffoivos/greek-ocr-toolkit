"""Bounded S1 receipt collector; uses unchanged O4c robots/rate transport."""
from __future__ import annotations
import concurrent.futures, datetime, hashlib, html, json, pathlib, sys, threading, time, importlib.util
from html.parser import HTMLParser
from urllib.parse import urlsplit, quote

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
spec=importlib.util.spec_from_file_location('s1_o4c_common', ROOT/'greekocr/_vendor/scripts/fetch/o4c_common.py')
transport=importlib.util.module_from_spec(spec);spec.loader.exec_module(transport)
def http_client(source,root,**kwargs):return transport.HTTP(source,root=root,**kwargs)

BASE = pathlib.Path(__file__).resolve().parent
LOCKS = {}; LAST = {}; GUARD = threading.Lock()

class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self.skip=0; self.links=[]
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip+=1
        if tag in ('p','div','br','li','h1','h2','h3','tr'): self.parts.append('\n')
        if tag == 'a':
            d=dict(attrs)
            if d.get('href'): self.links.append(d['href'])
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def collect(job):
    source=job['source']; folder=BASE/'receipts'/source
    client=http_client('archive',folder,offline=False,interval=2,budget=50_000_000)
    raw=client.raw
    def paced(url,*args,**kwargs):
        origin=urlsplit(url).netloc
        with GUARD: lock=LOCKS.setdefault(origin,threading.RLock())
        with lock:
            time.sleep(max(0,2-(time.monotonic()-LAST.get(origin,0))))
            try:return raw(url,*args,**kwargs)
            finally:LAST[origin]=time.monotonic()
    client.raw=paced
    results=[]
    for entry in job['requests']:
        client.retry_errors=bool(entry.get('retry_transient',False))
        url=quote(entry['url'],safe=":/?&=%|+,;@!$'()*[]"); label=entry['label']; result=dict(entry,source=source,checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
        try:
            if source in ('anemi','google-books') and entry.get('probe'): raise ValueError('media forbidden for this source')
            if urlsplit(url).path.lower().endswith('.pdf') and '/wiki/' not in urlsplit(url).path and not entry.get('probe') and entry.get('role')!='terms': raise ValueError('PDF requires explicit bounded probe')
            if entry.get('probe'):
                prior=list(folder.glob('probe-*.json'))
                if len(prior)>=20 and not (folder/('probe-'+label+'.json')).exists(): raise ValueError('20-page source cap')
            m,b=client.get(url,limit=entry.get('limit',2_000_000),range_header=entry.get('range'))
            result.update(ok=True,response_url=m['url'],status=m['status'],bytes=m['bytes'],sha256=m['sha256'],http_receipt=str((client.cache/(hashlib.sha256((m['url']+'\n'+str(entry.get('range'))).encode()).hexdigest()+'.json')).relative_to(BASE)))
            if entry.get('probe'):
                # Only single-page raster media are accepted by this collector.
                from PIL import Image
                import io
                im=Image.open(io.BytesIO(b)); im.verify()
                if im.format not in ('JPEG','PNG','TIFF','WEBP'):raise ValueError('not a supported raster')
                ext={'JPEG':'.jpg','PNG':'.png','TIFF':'.tif','WEBP':'.webp'}[im.format]
                target=folder/('probe-'+label+ext);target.write_bytes(b)
                result.update(image_path=str(target.relative_to(BASE)),width=im.width,height=im.height,pages=1)
                write(folder/('probe-'+label+'.json'),result)
            else:
                text=b.decode('utf-8','replace')
                if 'html' in m['headers'].get('content-type','') or text.lstrip().startswith('<!DOCTYPE html'):
                    parser=Text();parser.feed(text)
                    (folder/(label+'.txt')).write_text(''.join(parser.parts))
                    write(folder/(label+'-links.json'),parser.links)
                else:(folder/(label+'.txt')).write_text(text)
        except Exception as e:
            result.update(ok=False,error=str(e))
        write(folder/(label+'-result.json'),result);results.append(result)
        print(source,label,'OK' if result['ok'] else result['error'],flush=True)
    return results

if __name__=='__main__':
    jobs=json.loads(pathlib.Path(sys.argv[1]).read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for result in pool.map(collect,jobs):pass

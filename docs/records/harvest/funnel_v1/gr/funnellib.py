"""F1-GR bounded verification, adapted from P1 pilotlib/acquire_pdf.

No OCR, cloud calls, corpus admission, credentials on disk, or automatic retries.
All network requests (including redirects and robots) share host start spacing.
"""
from __future__ import annotations
import contextlib, datetime, fcntl, hashlib, io, json, os, pathlib, re, time
from urllib.parse import urljoin, urlsplit
import requests
from PIL import Image
import pypdfium2 as pdfium
from pypdfium2 import raw
from greekocr._vendor.scripts.fetch.o4c_common import robots_allowed

BASE=pathlib.Path(__file__).resolve().parent
UA='greek-ocr-research/0.1 (foivos.karounos@gmail.com)'
MAIN=BASE.parents[3].parent/'greek-ocr-toolkit'
INVENTORY=BASE.parents[3].parent/'greek-ocr-toolkit-sol-inventory/docs/harvest/inventory_v2'
def sha(b): return hashlib.sha256(b).hexdigest()
def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(path,obj):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def append(path,obj):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a') as f:
        fcntl.flock(f,fcntl.LOCK_EX);f.write(json.dumps(obj,ensure_ascii=False,allow_nan=False)+'\n')
def rows(path):
    p=pathlib.Path(path)
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []
def safe(value):
    text=json.dumps(value,ensure_ascii=False)
    for k in ['ANEMI_USER','ANEMI_PASS','HF_TOKEN','HUGGING_FACE_HUB_TOKEN']:
        v=os.environ.get(k)
        if v and v in text: raise ValueError('secret excluded from receipt')
    return value
class Blocked(RuntimeError):pass

class HTTP:
    def __init__(self,source,interval=1.):
        self.source=source;self.interval=max(interval,2. if source=='anemi' else 1.)
        self.session=requests.Session();self.session.headers.update({'User-Agent':UA,'Accept-Encoding':'identity'})
        self.robots={};self.last_receipt=None
    def _raw(self,url,kind,limit,method='GET',data=None):
        host=urlsplit(url).netloc
        lock=BASE/'bulk/host-state.lock';lock.parent.mkdir(parents=True,exist_ok=True)
        with lock.open('a') as f:
            fcntl.flock(f,fcntl.LOCK_EX)
            statepath=BASE/'bulk/host-state.json';state=json.loads(statepath.read_text()) if statepath.exists() else {}
            st=state.get(host,{})
            if st.get('stopped'):raise Blocked('host stopped after second throttle: '+host)
            delay=max(self.interval,self.robots.get(urlsplit(url).scheme+'://'+host,{}).get('delay',0))
            wait=max(0,st.get('next',0)-time.time(),st.get('last',0)+delay-time.time())
            # Reserve a host-specific start without holding the global file lock
            # during a long delay belonging to this host.
            st['last']=time.time()+wait;state[host]=st;write(statepath,state)
        if wait:time.sleep(wait)
        # The reservation above can wake with scheduler jitter. Serialize actual
        # starts for this host and retain a 100-ms margin, without blocking others.
        guarddir=BASE/'bulk/start-guards';guarddir.mkdir(exist_ok=True)
        guard=guarddir/(sha(host.encode())+'.lock');lastfile=guard.with_suffix('.json')
        with guard.open('a') as f:
            fcntl.flock(f,fcntl.LOCK_EX)
            previous=json.loads(lastfile.read_text())['last'] if lastfile.exists() else 0
            time.sleep(max(0,previous+delay+.1-time.time()))
            started=time.time();write(lastfile,dict(last=started))
        body=b'';status=0;headers={};error=None;truncated=False;ttfb=None
        try:
            with self.session.request(method,url,data=data,stream=True,timeout=(12,25),allow_redirects=False) as resp:
                status=resp.status_code
                headers={k.lower():v for k,v in resp.headers.items() if k.lower() in ['content-type','content-length','content-range','retry-after','accept-ranges','location']}
                ttfb=time.time()-started
                length=int(headers.get('content-length','0') or 0)
                if length>limit:truncated=True;error='size_limit_before_body'
                else:
                    chunks=[];n=0
                    for chunk in resp.iter_content(65536):
                        if time.time()-started>100:raise TimeoutError('100 second total body budget')
                        n+=len(chunk)
                        if n>limit:truncated=True;error='size_limit';break
                        chunks.append(chunk)
                    body=b''.join(chunks)
                    if length and len(body)!=length and not truncated:truncated=True;error='truncated_body'
        except requests.exceptions.ConnectionError:
            # macOS native trust store, as in the existing O4c/Anemi transport.
            # This is a fresh request: reserve another politely spaced host start.
            import subprocess
            with lock.open('a') as f:
                fcntl.flock(f,fcntl.LOCK_EX);state=json.loads(statepath.read_text());st=state[host]
                time.sleep(max(0,st['last']+delay-time.time()));st['last']=time.time();write(statepath,state)
            args=['/usr/bin/curl','-q','--silent','--show-error','--include','--max-time','100','--max-filesize',str(limit),'-A',UA,'-X',method]
            if data is not None:args+=['-H','Content-Type: application/json','--data-binary','@-']
            proc=subprocess.run(args+[url],input=data.encode() if isinstance(data,str) else data,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            payload=proc.stdout
            while payload.startswith(b'HTTP/'):
                head,sep,payload=payload.partition(b'\r\n\r\n')
                if not sep:break
                lines=head.decode('iso8859-1').splitlines();status=int(lines[0].split()[1]);headers={}
                for line in lines[1:]:
                    if ':' in line:
                        k,v=line.split(':',1)
                        if k.lower() in ['content-type','content-length','content-range','retry-after','accept-ranges','location']:headers[k.lower()]=v.strip()
                if status>=200 and b'Connection established' not in head:break
            body=payload[:limit];truncated=len(payload)>limit or proc.returncode==63
            if proc.returncode:error='native_curl_'+str(proc.returncode)
            elif truncated:error='size_limit'
            else:error=None
            append(BASE/'receipts/transport-corrections.jsonl',dict(source=self.source,url=url,correction='Python connection or TLS failure; native verified macOS TLS used',at=stamp()))
        except requests.RequestException as e:error=type(e).__name__
        except TimeoutError:error='total_timeout'
        elapsed=time.time()-started
        rec=dict(source=self.source,url=url,host=host,kind=kind,method=method,status=status,bytes=len(body),seconds=elapsed,
                 ttfb_seconds=ttfb,sha256=sha(body),started_at=datetime.datetime.fromtimestamp(started,datetime.timezone.utc).isoformat(),
                 ended_at=stamp(),error=error,truncated=truncated,user_agent=UA,rate_interval_seconds=delay,
                 headers={k:v for k,v in headers.items() if k!='location'})
        rec['rate_limiter_version']='host-actual-start-v2'
        safe(rec);append(BASE/'receipts/http.jsonl',rec);self.last_receipt=rec
        if status in [429,503]:
            with lock.open('a') as f:
                fcntl.flock(f,fcntl.LOCK_EX);state=json.loads(statepath.read_text());st=state[host]
                st['throttles']=st.get('throttles',0)+1
                try:retry=float(headers.get('retry-after',0))
                except ValueError:
                    from email.utils import parsedate_to_datetime
                    try:retry=max(0,parsedate_to_datetime(headers['retry-after']).timestamp()-time.time())
                    except Exception:retry=0
                backoff=max(60 if st['throttles']==1 else 300,retry)
                st['next']=time.time()+backoff;st['stopped']=st['throttles']>=2;write(statepath,state)
            raise Blocked(f'HTTP {status}; host backoff {backoff}s; Retry-After={headers.get("retry-after")}')
        return rec,body,headers
    def check(self,url):
        origin=urlsplit(url).scheme+'://'+urlsplit(url).netloc
        if origin not in self.robots:
            robotsurl=origin+'/robots.txt'
            for _ in range(6):
                rec,body,rh=self._raw(robotsurl,'robots',1_000_000)
                if rec['status'] in [301,302,303,307,308] and rh.get('location'):
                    robotsurl=urljoin(robotsurl,rh['location']);continue
                break
            if rec['status']==200 and not rec['error']:
                text=body.decode('utf8','replace');delay=0
                # Only the matching User-agent group applies (e.g. AhrefsBot's
                # 600-second delay does not apply to greek-ocr-research).
                import urllib.robotparser
                parser=urllib.robotparser.RobotFileParser();parser.parse(text.splitlines())
                delay=parser.crawl_delay(UA) or 0
                self.robots[origin]=dict(text=text,delay=delay,status=200)
            elif rec['status'] in [400,404,410]:self.robots[origin]=dict(text='',delay=0,status=rec['status'])
            else:
                self.robots[origin]=dict(text='User-agent: *\nDisallow: /',delay=0,status=rec['status'])
            write(BASE/'receipts/robots'/(sha(origin.encode())[:16]+'.json'),dict(origin=origin,**self.robots[origin]))
        robot=self.robots[origin]
        if not robots_allowed(robot['text'],url,UA):
            append(BASE/'receipts/http.jsonl',dict(source=self.source,url=url,host=urlsplit(url).netloc,kind='robots_refusal',status=None,bytes=0,seconds=0,error='robots_disallow_or_unavailable',started_at=stamp(),sha256=sha(b'')))
            raise Blocked('robots disallow or unavailable: '+url)
    def get(self,url,kind='metadata',limit=8_000_000,method='GET',data=None,private=False):
        for _ in range(7):
            self.check(url);rec,body,headers=self._raw(url,kind,limit,method,data)
            if rec['status'] in [301,302,303,307,308] and headers.get('location'):
                target=urljoin(url,headers['location'])
                if private and urlsplit(target).netloc!=urlsplit(url).netloc:raise Blocked('private redirect outside origin')
                url=target;method='GET';data=None;continue
            if rec['status'] not in [200,206] or rec['error']:raise Blocked(f"HTTP {rec['status']} {rec['error']}: {url}")
            if kind=='metadata' and not private:
                p=BASE/'bulk/metadata'/(sha(url.encode())+'.body');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body)
                write(BASE/'receipts/metadata'/(sha(url.encode())+'.json'),rec)
            return rec,body
        raise Blocked('redirect limit')

def positions(total,count):
    # Reuse P1's front/body/back stratification, at a smaller disk cap.
    count=min(total,count)
    return sorted(set([0,total-1]+[round((total-1)*i/max(1,count-1)) for i in range(count)]))[:count]

def raster(im,source,item,n,url,fetch,**extra):
    im.load();native=list(im.size);im=im.convert('L');im.thumbnail((2000,2000),Image.Resampling.LANCZOS)
    dest=BASE/'bulk/pages'/source/(re.sub('[^a-zA-Z0-9_.-]','_',str(item))[:100]+f'--{n:05d}.jpg');dest.parent.mkdir(parents=True,exist_ok=True)
    im.save(dest,quality=83,optimize=True)
    used=sum(p.stat().st_size for p in (BASE/'bulk/pages').rglob('*.jpg'))
    if used>400_000_000:dest.unlink();raise Blocked('400 MB page image cap')
    rec=dict(source=source,item=str(item),page=n,url=url,fetch_sha256=fetch['sha256'],original_bytes=fetch['bytes'],
             image=str(dest.relative_to(BASE)),image_sha256=sha(dest.read_bytes()),width=im.width,height=im.height,native_size=native,
             fetched_at=fetch['ended_at'],fresh=True,**extra)
    append(BASE/'probe_pages.jsonl',rec);return rec

def physical(page):
    w,h=page.get_size();images=[];texts=[];text_orders=[];text_bounds=[];other=0;full_opaque_images=[]
    for order,obj in enumerate(page.get_objects(max_depth=10)):
        if obj.type==raw.FPDF_PAGEOBJ_IMAGE:
            b=obj.get_bounds();area=max(0,min(w,b[2])-max(0,b[0]))*max(0,min(h,b[3])-max(0,b[1]))/(w*h)
            opaque=None
            if area>=.85:
                bitmap=obj.get_bitmap()
                pil=bitmap.to_pil()
                opaque='A' not in pil.getbands() or pil.getchannel('A').getextrema()==(255,255)
                # FPDFImageObj_GetBitmap returns an image-owned (foreign) bitmap.
                # Do not explicitly close its non-owning wrapper.
                del pil,bitmap
                if opaque:full_opaque_images.append((order,b))
            images.append(dict(bounds=list(b),coverage=area,pixels=list(obj.get_px_size()),drawing_order=order,opaque=opaque))
        elif obj.type==raw.FPDF_PAGEOBJ_TEXT:
            texts.append(int(raw.FPDFTextObj_GetTextRenderMode(obj.raw)));text_orders.append(order);text_bounds.append(obj.get_bounds())
        else:other+=1
    tp=page.get_textpage();text=tp.get_text_range();tp.close()
    full=any(i['coverage']>=.85 for i in images)
    covered_orders=[order for order,b in full_opaque_images if all(t[0]>=b[0]-.5 and t[1]>=b[1]-.5 and t[2]<=b[2]+.5 and t[3]<=b[3]+.5 for t in text_bounds)]
    if full and not texts:label='scanned_image_no_text_operators'
    elif full and texts and all(m==3 for m in texts):label='scanned_image_hidden_OCR'
    elif full and texts and covered_orders and max(text_orders)<max(covered_orders):label='scanned_image_OCR_covered_by_opaque_image'
    elif full and texts:label='full_page_image_with_visible_text_uncertain'
    elif texts and not full:label='born_digital_text'
    else:label='uncertain'
    return dict(classification=label,page_points=[w,h],image_objects=images,text_object_count=len(texts),text_render_modes=sorted(set(texts)),text_drawing_order_range=[min(text_orders),max(text_orders)] if text_orders else None,other_objects=other,text_snippet=text[:1800],greek_text_letters=sum('\u0370'<=c<='\u03ff' or '\u1f00'<=c<='\u1fff' for c in text))

def document_scan(pages,url=''):
    wrappers=[p['page'] for p in pages if 'epublishing.ekt.gr' in url and p['page']==1 and p['classification']=='born_digital_text' and re.search(r'\bdoi\b|ePublishing',p.get('text_snippet',''),re.I)]
    body=[p for p in pages if p['page'] not in wrappers]
    return dict(all_sampled_pages_scanned=bool(pages) and all(p['classification'].startswith('scanned_') for p in pages),
                scanned_body_verified=bool(body) and all(p['classification'].startswith('scanned_') for p in body),
                generated_wrapper_pages=wrappers,has_born_digital_content=any(p['classification']=='born_digital_text' for p in body),
                mixed_or_uncertain=any(not p['classification'].startswith('scanned_') and p['classification']!='born_digital_text' for p in body))

def pdf(c,url,item,pages=10,limit=100_000_000,extra=None,mode='sequential'):
    start=time.time();attempt=dict(source=c.source,item=str(item),url=url,kind='pdf',mode=mode,started_at=stamp(),success=False)
    try:
        rec,body=c.get(url,'pdf',limit)
        attempt.update(bytes=rec['bytes'],download_seconds=rec['seconds'],http_sha256=rec['sha256'])
        if not body.startswith(b'%PDF'):raise Blocked('HTML_or_non_PDF_instead_of_PDF')
        with pdfium.PdfDocument(body) as doc:
            total=len(doc);attempt['page_count']=total;attempt['physical_pages']=[]
            for j,i in enumerate(positions(total,pages)):
                with contextlib.closing(doc[i]) as page:
                    phys=physical(page);attempt['physical_pages'].append(dict(page=i+1,**phys))
                    w,h=page.get_size();scale=2000/max(w,h)
                    with contextlib.closing(page.render(scale=scale,grayscale=True)) as bm:im=bm.to_pil().copy()
                    raster(im,c.source,item,i+1,url,rec,physical=phys,pdf_page_count=total,mode=mode,**(extra or {}))
                    if j==0:attempt['time_to_first_page_seconds']=time.time()-start
            attempt.update(success=True,decoded_pages=len(attempt['physical_pages']))
    except Exception as e:attempt['error']=str(e)[:450]
    attempt['total_seconds']=time.time()-start;attempt['ended_at']=stamp();append(BASE/'receipts/media.jsonl',attempt)
    print(c.source,item,attempt['success'],attempt.get('page_count'),attempt.get('error',''),flush=True)
    return attempt

def image(c,url,item,n,extra=None):
    start=time.time();attempt=dict(source=c.source,item=str(item),page=n,url=url,kind='image',mode='sequential',started_at=stamp(),success=False)
    try:
        rec,body=c.get(url,'image',25_000_000)
        with Image.open(io.BytesIO(body)) as im:raster(im,c.source,item,n,url,rec,**(extra or {}))
        attempt.update(success=True,bytes=rec['bytes'],download_seconds=rec['seconds'],decoded_pages=1)
    except Exception as e:attempt['error']=str(e)[:450]
    attempt['total_seconds']=time.time()-start;attempt['ended_at']=stamp();append(BASE/'receipts/media.jsonl',attempt)
    return attempt

def candidate(source,item,title,year,url,result,**extra):
    if not result.get('success'):return None
    rec=dict(id=str(item),source=source,title=title,year=year,decade=year//10*10 if year else None,
             language_script_evidence='Greek catalogue; physical script review pending',page_count=result.get('page_count'),
             page_access_route=url,page_access_verified=True,page_access_evidence=result.get('http_sha256'),restriction_flags=[],
             overlap_flag='unresolved',held_out_test=False,scan_rights='unresolved',text_rights='unresolved',
             access_terms_url=None,licence_string=None)
    rec.update(extra)
    append(BASE/f'candidates_{source}.jsonl',rec);return rec

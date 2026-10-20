#!/usr/bin/env python3
"""O4c bounded, robots-aware discovery primitives (no corpus downloader)."""
from __future__ import annotations
import ctypes
import gzip
import http.client
import argparse, datetime, hashlib, io, json, os, pathlib, re, time, unicodedata, subprocess, tempfile, ssl, fcntl
from contextlib import closing
from functools import lru_cache
import urllib.error, urllib.parse, urllib.request, urllib.robotparser
ROOT = pathlib.Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'docs/evidence/o4c'
UA = 'GreekPageOCR-O4c/1.0 (noncommercial OCR research; metadata and bounded text-layer probes)'
BUDGET = 2_000_000_000

def write_json(path, obj):
    path = pathlib.Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp'); tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n'); tmp.replace(path)

def append(path, obj):
    path = pathlib.Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as f: f.write(json.dumps(obj, ensure_ascii=False)+'\n')

def read_rows(path):
    return [json.loads(s) for s in pathlib.Path(path).read_text().splitlines() if s.strip()] if pathlib.Path(path).exists() else []

class ProbeError(RuntimeError): pass
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args): return None

def robots_allowed(text,url,user_agent=UA):
    groups=[];agents=[];rules=[];seen_rules=False
    for raw in text.lstrip('\ufeff').splitlines():
        line=raw.split('#',1)[0].strip()
        if ':' not in line:continue
        k,v=line.split(':',1);k=k.strip().lower();v=v.strip()
        if k=='user-agent':
            if seen_rules:groups.append((agents,rules));agents=[];rules=[];seen_rules=False
            agents.append(v.lower())
        elif k in ('allow','disallow') and agents:
            rules.append((k,v));seen_rules=True
    if agents:groups.append((agents,rules))
    ua=user_agent.lower();matches=[]
    for agents,rules in groups:
        score=max((len(a) if a!='*' else 0 for a in agents if a=='*' or a in ua),default=-1)
        if score>=0:matches.append((score,rules))
    if not matches:return True
    score=max(x[0] for x in matches);target=urllib.parse.urlsplit(url).path or '/'
    if urllib.parse.urlsplit(url).query:target+='?'+urllib.parse.urlsplit(url).query
    decisions=[]
    for level,rules in matches:
        if level!=score:continue
        for kind,value in rules:
            if not value:continue
            anchor=value.endswith('$');pattern=value[:-1] if anchor else value
            regex='^'+'.*'.join(re.escape(z) for z in pattern.split('*'))+('$' if anchor else '')
            if re.search(regex,target):decisions.append((len(pattern.replace('*','')),kind=='allow'))
    return max(decisions,default=(0,True))[1]

class HTTP:
    """Serial crawler. One process at a time; shared ledger includes error/robots bodies.

    Cache keys bind URL and Range; receipts bind body hash. Offline misses fail closed.
    Redirects pass through this client so each destination checks robots and rate limits.
    """
    def __init__(self, source, offline=False, interval=.6, budget=BUDGET, root=EVIDENCE, retry_errors=False):
        if interval < .5: raise ValueError('interval must be >= 0.5 seconds')
        if budget > BUDGET or budget < 1: raise ValueError('budget must be 1..2,000,000,000')
        self.source, self.offline, self.interval, self.budget = source, offline, interval, budget
        self.retry_errors=retry_errors
        self.root=pathlib.Path(root); self.cache=self.root/'http'; self.cache.mkdir(parents=True,exist_ok=True)
        self.ledger=self.root/'transfer.jsonl'; self.last={}; self.robots={}; self.requests=0
        self.transferred=sum(r['bytes'] for r in read_rows(self.ledger))
    def raw(self,url,limit,range_header=None,depth=0):
        # Cross-process locking prevents parallel invocations overspending or exceeding host rates.
        with (self.root/'http.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            self.transferred=sum(r['bytes'] for r in read_rows(self.ledger))
            rates=self.root/'rate_state.json'
            saved=json.loads(rates.read_text()) if rates.exists() else {}
            # Persist Unix time, not a monotonic clock that resets at reboot.
            # Old flat monotonic receipts are deliberately discarded on migration.
            self.last=saved.get('hosts',{}) if saved.get('clock')=='unix-seconds-v1' else {}
            try:return self._raw(url,limit,range_header,depth)
            finally:write_json(rates,{'clock':'unix-seconds-v1','hosts':self.last})
    def _raw(self,url,limit,range_header=None,depth=0):
        if depth>6: raise ProbeError('redirect limit')
        key=hashlib.sha256((url+'\n'+str(range_header)).encode()).hexdigest()
        meta=self.cache/(key+'.json'); blob=self.cache/(key+'.body')
        if meta.exists() and blob.exists():
            m=json.loads(meta.read_text()); b=blob.read_bytes()
            if hashlib.sha256(b).hexdigest()!=m['sha256']: raise ProbeError('cache hash mismatch')
            retryable=self.retry_errors and not self.offline and (m['status'] in (429,500,502,503,504) or m.get('truncated'))
            if m.get('truncated') and not retryable:raise ProbeError('recorded response exceeded probe limit')
            if not retryable:
                return m,b
        if self.offline: raise ProbeError('offline cache miss: '+url)
        host=urllib.parse.urlsplit(url).netloc
        interval=max(self.interval,self.robots.get(host,{}).get('delay',0))
        now=time.time();previous=self.last.get(host)
        elapsed=max(0,now-previous) if previous is not None else interval
        time.sleep(max(0,interval-elapsed))
        self.last[host]=time.time()
        remaining=self.budget-self.transferred
        if remaining<=0: raise ProbeError('task transfer budget exhausted')
        limit=min(limit,remaining)
        headers={'User-Agent':UA,'Accept-Encoding':'gzip' if '/discover/search/objects' in url and not range_header else 'identity'}
        if range_header: headers['Range']=range_header
        body=b''; truncated=False;read_error=None
        try:
            response=urllib.request.build_opener(NoRedirect).open(urllib.request.Request(url,headers=headers),timeout=35)
        except urllib.error.HTTPError as e: response=e
        except (urllib.error.URLError,TimeoutError,OSError) as e:
            if isinstance(getattr(e,'reason',None),ssl.SSLCertVerificationError):
                # macOS curl uses the native certificate trust store; never disable TLS checks.
                with tempfile.NamedTemporaryFile() as headerfile:
                    command=['/usr/bin/curl','--silent','--show-error','--max-time','35','--max-filesize',str(limit),'-A',UA,'-D',headerfile.name]
                    if range_header: command+=['-H','Range: '+range_header]
                    command+=[url]
                    proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    body=proc.stdout.read(limit)
                    if len(body)==limit:proc.terminate()
                    _,err=proc.communicate()
                    headerfile.seek(0);rawheaders=headerfile.read().decode('iso-8859-1')
                    blocks=[z for z in rawheaders.split('\r\n\r\n') if z.startswith('HTTP/')]
                    if not blocks:raise ProbeError(err.decode('utf-8','replace'))
                    lines=blocks[-1].splitlines();status=int(lines[0].split()[1]);h={}
                    for line in lines[1:]:
                        if ':' in line:k,v=line.split(':',1);h[k.lower()]=v.strip()
                    truncated=proc.returncode==63 or len(body)==limit
                    if proc.returncode and not truncated:read_error=err.decode('utf-8','replace');truncated=True
                    response=None
            else:raise ProbeError(str(e)) from e
        if response is not None:
          with response:
            status=response.code; h={k.lower():v for k,v in response.headers.items()}
            # Never read a large media response that ignores Range.
            length=int(h.get('content-length','0') or 0)
            if length>limit: truncated=True
            else:
                chunks=[]; n=0
                while n<limit:
                    try:chunk=response.read(min(65536,limit-n))
                    except (OSError,TimeoutError,http.client.IncompleteRead) as error:
                        partial=getattr(error,'partial',b'')[:limit-n]
                        if partial:chunks.append(partial);n+=len(partial)
                        read_error=str(error);truncated=True;break
                    if not chunk: break
                    chunks.append(chunk); n+=len(chunk)
                body=b''.join(chunks)
                if n==limit and (not length or length>limit): truncated=True
        self.transferred+=len(body); self.requests+=1
        m={'url':url,'range':range_header,'status':status,'headers':h,'sha256':hashlib.sha256(body).hexdigest(),
           'bytes':len(body),'truncated':truncated,'read_error':read_error,'fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':self.source,'user_agent':UA}
        blob.write_bytes(body); write_json(meta,m); append(self.ledger,m)
        if truncated: raise ProbeError((read_error or 'response exceeds probe limit')+': '+url)
        return m,body
    def check_robots(self,url):
        p=urllib.parse.urlsplit(url); host=p.netloc
        if host not in self.robots:
            robots_url=p.scheme+'://'+host+'/robots.txt'
            m,b=self.raw(robots_url,262144)
            for _ in range(6):
                if m['status'] not in (301,302,303,307,308):break
                robots_url=urllib.parse.urljoin(robots_url,m['headers']['location'])
                m,b=self.raw(robots_url,262144)
            rp=urllib.robotparser.RobotFileParser()
            status=m['status']
            if status==200: rp.parse(b.decode('utf-8','replace').splitlines())
            elif status in (404,410): rp.parse([])
            else: raise ProbeError(f'robots unverified HTTP {status}: {host}')
            delay=rp.crawl_delay(UA) or rp.crawl_delay('*') or 0
            rate=rp.request_rate(UA) or rp.request_rate('*')
            if rate: delay=max(delay,rate.seconds/rate.requests)
            self.robots[host]={'parser':rp,'delay':delay,'url':m['url'],'status':status,'text':b.decode('utf-8','replace') if status==200 else ''}
        if not robots_allowed(self.robots[host]['text'],url): raise ProbeError('robots disallows '+url)
    def get(self,url,limit=8_000_000,range_header=None,depth=0):
        if urllib.parse.urlsplit(url).scheme not in ('http','https'): raise ProbeError('unsupported URL')
        if depth>6: raise ProbeError('redirect limit')
        self.check_robots(url)
        m,b=self.raw(url,limit,range_header,depth)
        if m['status'] in (301,302,303,307,308):
            return self.get(urllib.parse.urljoin(url,m['headers']['location']),limit,range_header,depth+1)
        if m['status'] not in (200,206): raise ProbeError(f'HTTP {m["status"]}: {url}')
        if m['headers'].get('content-encoding','').lower()=='gzip':
            with gzip.GzipFile(fileobj=io.BytesIO(b)) as zipped:decoded=zipped.read(limit+1)
            if len(decoded)>limit:raise ProbeError('decoded metadata exceeds probe limit')
            b=decoded
        return m,b
    def json(self,url): return json.loads(self.get(url,limit=32_000_000 if '/discover/search/objects' in url else 8_000_000)[1])
    def event(self,**kwargs): append(self.root/(self.source+'_events.jsonl'),kwargs)

def api(base,**params): return base+'?'+urllib.parse.urlencode(params,doseq=True)

@lru_cache(maxsize=8192)
def letter_info(ch):
    nfd=unicodedata.normalize('NFD',ch)
    letters=[c for c in nfd if unicodedata.category(c).startswith('L')]
    greek=sum('GREEK' in unicodedata.name(c,'') for c in letters)
    cyr=sum('CYRILLIC' in unicodedata.name(c,'') for c in letters)
    marked=greek>0 and (('\u1f00'<=ch<='\u1fff' and unicodedata.category(ch).startswith('L')) or any(c in '\u0313\u0314\u0342\u0300\u0345' for c in nfd))
    return greek,cyr,len(letters),marked,unicodedata.category(ch).startswith('M')

def metrics(text,pages_sampled=1,total_pages=None):
    """Greek letter denominator; original Greek Extended letters or attached polytonic marks.

    NFC/NFD breathings are equivalent. Extended oxia counts in the requested raw-codepoint
    diagnostic; ordinary Greek tonos does not. Punctuation in U+1F00..1FFF never counts.
    Lines are nonempty physical OCR lines, not gold supervision.
    """
    greek=cyr=marked=letters=plines=clines=glines=0
    lines=[s for s in text.splitlines() if s.strip()]
    for line in lines:
        lg=lc=lm=0;pending=False;seen=False
        for ch in line:
            g,c,l,m,is_mark=letter_info(ch);greek+=g;cyr+=c;letters+=l;lg+=g;lc+=c
            if l:
                pending=g>0;seen=bool(m)
                if m:marked+=g;lm+=g
            elif is_mark and pending and ch in '\u0313\u0314\u0342\u0300\u0345' and not seen:
                marked+=1;lm+=1;seen=True
            elif not is_mark:pending=False
        plines+=lm>0;glines+=lg>0;clines+=lc>0
    scale=total_pages/pages_sampled if total_pages and pages_sampled else None
    return {'chars':len(text),'chars_per_page':len(text)/pages_sampled if pages_sampled else None,
      'greek_letters':greek,'polytonic_letters':marked,'cyrillic_letters':cyr,'letters':letters,
      'polytonic_ratio':marked/greek if greek else 0,'cyrillic_ratio':cyr/letters if letters else 0,
      'greek_ratio':greek/letters if letters else 0,'sample_lines':len(lines),'sample_polytonic_lines':plines,'sample_cyrillic_lines':clines,
      'estimated_polytonic_lines':round(plines*scale) if scale else None,'estimated_cyrillic_lines':round(clines*scale) if scale else None}

def license_info(raw):
    vals=raw if isinstance(raw,list) else [raw]
    s=' | '.join(str(v) for v in vals if v)
    low=s.lower(); good=False; label='unverified'
    if re.search(r'\b(?:nc|nd)\b',low) or 'noncommercial' in low or 'non-commercial' in low or 'commercial use is strictly prohibited' in low: label='excluded-NC-or-ND'
    elif 'creativecommons.org/licenses/by-sa/' in low or 'cc-by-sa' in low or 'cc by-sa' in low: good=True; label='CC-BY-SA'
    elif 'creativecommons.org/licenses/by/' in low or 'cc-by-' in low or 'cc by ' in low: good=True; label='CC-BY'
    elif 'publicdomain/zero/' in low or 'cc0' in low: good=True; label='CC0'
    elif 'publicdomain/mark/' in low or '/public-domain/pdm/' in low or 'public domain' in low or low in ('pd','pd-us'): good=True; label='public-domain'
    if good and 'all rights reserved' in low:good=False;label='unverified-conflicting-rights'
    identifier=label
    version=re.search(r'licenses/(?:by|by-sa)/(\d+\.\d+)',low) or re.search(r'cc[ -]by(?:[ -]sa)?[ -]+(\d+\.\d+)',low)
    if label in ('CC-BY','CC-BY-SA') and version:identifier=label+'-'+version[1]
    if label=='excluded-NC-or-ND':
        exact=re.search(r'licenses/([a-z-]+)/(\d+\.\d+)',low) or re.search(r'cc[ -]([a-z]+(?:-[a-z]+)*)[ -]+(\d+\.\d+)',low)
        if exact:identifier='CC-'+exact[1].upper()+'-'+exact[2]
    if label=='CC0':identifier='CC0-1.0'
    if label=='public-domain':identifier='Public Domain Mark 1.0' if 'publicdomain/mark/1.0' in low else 'Public domain (as declared; jurisdiction unverified)'
    return {'raw':vals,'compatible':good,'family':label,'identifier':identifier,'verification':'source-declared' if good else 'unverified' if label=='unverified' else 'excluded'}

def row(source,id,title,url,year=None,pages=None,size=None,rights=None,**extra):
    return dict(schema_version='o4c-1',source=source,document_id=str(id),title=title,record_url=url,year=year,pages=pages,size=size,
      download_url=None,rights=license_info(rights),text_layer={'status':'unverified'},polytonic_ratio=None,cyrillic_ratio=None,
      estimated_polytonic_lines=None,estimated_cyrillic_lines=None,status='unverified',**extra)

def apply_text(r,text,kind,pages_sampled=None):
    # Full text sidecar is allowed, but line counts are OCR physical/newline counts, not accepted labels.
    m=metrics(text,pages_sampled or 1,r.get('pages') if pages_sampled else None)
    if not pages_sampled:
        m['estimated_polytonic_lines']=m['sample_polytonic_lines'];m['estimated_cyrillic_lines']=m['sample_cyrillic_lines'];m['chars_per_page']=len(text)/r['pages'] if r.get('pages') else None
    r.update({k:m[k] for k in ('polytonic_ratio','cyrillic_ratio','estimated_polytonic_lines','estimated_cyrillic_lines')})
    r['text_layer']={'status':'verified' if m['chars'] else 'empty-sample','kind':kind,'sample_pages':pages_sampled,'measurement':m}
    r['polytonic_document']=m['greek_letters']>=50 and m['polytonic_ratio']>=.01
    r['cyrillic_document']=m['cyrillic_letters']>=50 and m['cyrillic_ratio']>=.2
    r['status']='candidate' if r['rights']['compatible'] and (r['polytonic_document'] or r['cyrillic_document']) and r.get('download_url') else 'unverified'

class RangeFile(io.RawIOBase):
    """Seekable HTTP range file for PDFium. No full-PDF fallback; per-doc byte bound."""
    def __init__(self,http,url,max_bytes=4_000_000,block=262144):
        self.http,self.url,self.pos,self.block,self.max_bytes=http,url,0,block,max_bytes
        self.parts={};self.used=0;self.error=None
        m,b=http.get(url,limit=block,range_header=f'bytes=0-{block-1}')
        if m['status']!=206: raise ProbeError('server did not support bounded PDF Range')
        cr=m['headers'].get('content-range','');match=re.fullmatch(r'bytes 0-(\d+)/(\d+)',cr)
        if not match or int(match[1])+1!=len(b): raise ProbeError('invalid Content-Range')
        self.length=int(match[2]);self.parts[0]=b;self.used=len(b)
    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos
    def seek(self,offset,whence=0):
        self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.length+offset
        if self.pos<0: raise ValueError('negative seek')
        return self.pos
    def read(self,n=-1):
        end=self.length if n<0 else min(self.length,self.pos+n); chunks=[]
        while self.pos<end:
            start=(self.pos//self.block)*self.block
            if start not in self.parts:
                count=min(self.block,self.length-start)
                if self.used+count>self.max_bytes: raise ProbeError('per-document PDF probe byte cap')
                m,b=self.http.get(self.url,limit=count,range_header=f'bytes={start}-{start+count-1}')
                if m['status']!=206 or m['headers'].get('content-range')!=f'bytes {start}-{start+count-1}/{self.length}' or len(b)!=count: raise ProbeError('invalid range response')
                self.parts[start]=b;self.used+=len(b)
            b=self.parts[start];off=self.pos-start;chunk=b[off:off+end-self.pos]
            if not chunk: raise ProbeError('short range block')
            chunks.append(chunk);self.pos+=len(chunk)
        return b''.join(chunks)
    def readinto(self,b):
        try:
            data=self.read(len(b));b[:len(data)]=data;return len(data)
        except Exception as e:
            self.error=str(e);return 0

def probe_pdf(http,r,local=None):
    import pypdfium2 as pdfium
    from pypdfium2.raw import FPDF_PAGEOBJ_IMAGE
    handle=None
    try:
        handle=pathlib.Path(local) if local else RangeFile(http,r['download_url'])
        reader=callback=None
        if isinstance(handle,RangeFile):
            reader=pdfium.raw.FPDF_FILEACCESS();reader.m_FileLen=handle.length
            callback_type=dict(pdfium.raw.FPDF_FILEACCESS._fields_)['m_GetBlock']
            def get_block(_,position,pointer,size):
                if handle.error:return 0
                try:
                    handle.seek(position);data=handle.read(size)
                    if len(data)!=size:raise ProbeError('short PDF range read')
                    ctypes.memmove(pointer,data,size);return 1
                except BaseException as error:
                    handle.error=str(error) or type(error).__name__;return 0
            callback=callback_type(get_block);reader.m_GetBlock=callback;reader.m_Param=None
            rawdoc=pdfium.raw.FPDF_LoadCustomDocument(reader,None)
            if not rawdoc:raise ProbeError(handle.error or 'PDFium could not load bounded ranges')
            document=pdfium.PdfDocument(rawdoc)
        else:document=pdfium.PdfDocument(handle)
        with document as doc:
            r['pages']=len(doc)
            index=min(2,len(doc)-1)
            with closing(doc[index]) as page:
                with closing(page.get_textpage()) as tp:text=tp.get_text_range()
                pw,ph=page.get_size();images=[]
                for obj in page.get_objects():
                    if obj.type==FPDF_PAGEOBJ_IMAGE:
                        x0,y0,x1,y1=obj.get_bounds();images.append(abs((x1-x0)*(y1-y0))/(pw*ph))
            if isinstance(handle,RangeFile) and handle.error:raise ProbeError(handle.error)
            apply_text(r,text,'PDFium embedded PDF text',1)
            r['text_layer'].update(page_indices=[index],probe_bytes=handle.used if isinstance(handle,RangeFile) else 0,
              text_sha256=hashlib.sha256(text.encode()).hexdigest(),text_excerpt=text[:500],
              scan_status='verified-large-raster-object' if max(images,default=0)>=.5 else 'unverified',
              largest_image_area_fraction=max(images,default=0))
    except Exception as e:
        r['text_layer']={'status':'unverified','error':str(e),'probe_bytes':handle.used if isinstance(handle,RangeFile) else 0}
        r['status']='unverified'
    return r

def parser(source):
    p=argparse.ArgumentParser(description=source+' O4c bounded discovery')
    p.add_argument('--out',type=pathlib.Path,default=EVIDENCE/(source+'.jsonl'))
    p.add_argument('--max-pages',type=int,default=5,help='metadata/API pages this invocation; use --all for completion')
    p.add_argument('--all',action='store_true');p.add_argument('--probe-docs',type=int,default=10)
    p.add_argument('--retry-errors',action='store_true',help='retry cached 429/5xx responses; bodies still counted')
    p.add_argument('--offline',action='store_true');p.add_argument('--interval',type=float,default=.6)
    return p

def load_state(args):
    path=args.out.with_suffix('.state.json')
    return path,json.loads(path.read_text()) if path.exists() else {}

def save_rows(path,rows):
    path=pathlib.Path(path);tmp=path.with_suffix('.tmp')
    tmp.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows));tmp.replace(path)

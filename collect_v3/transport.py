"""F2 robots/UA policy with a persistent capacity-one per-host token bucket."""
from __future__ import annotations
import email.utils,json,time,urllib.request,urllib.error,urllib.parse,urllib.robotparser
from pathlib import Path
from .common import lock,read_json,write_json,sha_bytes,atomic_bytes,scrub
from .vendor.robots import robots_allowed,UA

class NetworkDisabled(RuntimeError): pass
def iri_to_uri(url):
    """Percent-encode non-ASCII characters (e.g. Greek IIIF file names) so urllib can send the request.
    Already-encoded %XX sequences and URL delimiters are preserved; ASCII URLs pass through unchanged."""
    if url.isascii():return url
    p=urllib.parse.urlsplit(url)
    host=p.hostname.encode('idna').decode() if p.hostname else ''
    netloc=host+(f':{p.port}' if p.port else '')
    safe="/%:@!$&'()*+,;=-._~"
    return urllib.parse.urlunsplit((p.scheme,netloc,urllib.parse.quote(p.path,safe=safe),urllib.parse.quote(p.query,safe=safe+'?'),urllib.parse.quote(p.fragment,safe=safe)))

class AccessStopped(ValueError):
    """Robots disallow/unreachable or access control: stops that item/page (recorded), never the whole run."""
    pass
class HTTPStatusFailure(ValueError):
    """Non-200 final status (after server-error retries): stops that item/page, recorded."""
    pass
class NetworkFailure(ValueError):
    """Persistent transport failure after retries: callers treat it as an item/page failure, not a run abort."""
    pass
NETWORK_RETRIES=3
class DailyLimit(AccessStopped): pass

class HostBucket:
    def __init__(self,root,rate=1.,clock=time.time,sleep=time.sleep,mdz_daily_image_cap=500):
        if not 0<rate<=1:raise ValueError('host rate must be <=1 request/s')
        self.root=Path(root);self.interval=1/rate;self.clock=clock;self.sleep=sleep
        if not isinstance(mdz_daily_image_cap,int) or mdz_daily_image_cap<=0:raise ValueError('positive MDZ image cap required')
        self.mdz_daily_image_cap=mdz_daily_image_cap
    def acquire(self,host,delay=0,mdz_image=False):
        host=(urllib.parse.urlsplit('//'+host).hostname or host).lower()
        key=sha_bytes(host.encode());p=self.root/(key+'.json')
        while True:
            with lock(self.root/(key+'.lock')):
                d=read_json(p) if p.exists() else {}
                wait=max(d.get('next',0),d.get('last',0)+max(self.interval,delay))-self.clock()
                if wait<=0:
                    now=self.clock()
                    if mdz_image:
                        # Rolling 24h attempts, shared across all MDZ hosts.
                        with lock(self.root/'mdz-image-daily.lock'):
                            daily=self.root/'mdz-image-daily.json'
                            starts=[t for t in (read_json(daily).get('starts',[]) if daily.exists() else []) if t>now-86400]
                            if len(starts)>=self.mdz_daily_image_cap:raise DailyLimit('MDZ Image API rolling 24h cap reached; resume later')
                            write_json(daily,dict(starts=starts+[now],cap=self.mdz_daily_image_cap,limit_basis='conservative configurable fallback; documented limit unavailable offline'))
                    write_json(p,dict(last=now,next=now+max(self.interval,delay)))
                    return now
            # Do not sleep while holding the lock: another process must be able
            # to extend Retry-After before this waiting process starts a request.
            self.sleep(wait)
    def defer(self,host,seconds):
        host=(urllib.parse.urlsplit('//'+host).hostname or host).lower()
        key=sha_bytes(host.encode());p=self.root/(key+'.json')
        with lock(self.root/(key+'.lock')):
            d=read_json(p) if p.exists() else {};d['next']=max(d.get('next',0),self.clock()+seconds);write_json(p,d)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args):return None

def retry_seconds(value,now=None):
    try:return max(0.,float(value))
    except (ValueError,TypeError):
        try:return max(0.,email.utils.parsedate_to_datetime(value).timestamp()-(time.time() if now is None else now))
        except (ValueError,TypeError):return 60.

class HTTP:
    def __init__(self,cache,network=False,rate=1.,sender=None,bucket=None):
        self.cache=Path(cache);self.network=network;self.bucket=bucket or HostBucket(self.cache/'hosts',rate)
        self.sender=sender;self.robots={};self.delays={};self.events=[]
        self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
    def raw(self,url,limit=160_000_000):
        url=iri_to_uri(url)
        if not self.network and self.sender is None:raise NetworkDisabled('provider HTTP disabled')
        if self.sender is None:
            from .egress import check_url
            check_url(url)
        host=urllib.parse.urlsplit(url).netloc.lower()
        parsed=urllib.parse.urlsplit(url)
        mdz_image=(parsed.hostname or '').lower().endswith('.digitale-sammlungen.de') and '/iiif/image/' in parsed.path.lower()
        start=self.bucket.acquire(host,self.delays.get(host,0),mdz_image=mdz_image)
        if self.sender is not None:status,headers,data=self.sender(url)
        else:
            import http.client,socket
            for attempt in range(NETWORK_RETRIES+1):
                try:
                    with self.opener.open(urllib.request.Request(url,headers={'User-Agent':UA,'Accept-Encoding':'identity'}),timeout=90) as r:
                        status=r.status;headers=dict(r.headers);data=r.read(limit+1)
                    break
                except urllib.error.HTTPError as e:
                    status=e.code;headers=dict(e.headers);data=e.read(min(limit+1,262144));break
                except (TimeoutError,socket.timeout,urllib.error.URLError,ConnectionError,http.client.HTTPException) as e:
                    # Transient transport failure: back off on this host and retry through the shared limiter.
                    self.events.append(dict(host=host,start=start,status='network_error',error=type(e).__name__,attempt=attempt,url=scrub(url)))
                    if attempt==NETWORK_RETRIES:raise NetworkFailure(f'network failure after {NETWORK_RETRIES} retries: {type(e).__name__}') from None
                    self.bucket.defer(host,30*(2**attempt))
                    start=self.bucket.acquire(host,self.delays.get(host,0),mdz_image=mdz_image)
        headers={k.lower():v for k,v in headers.items()}
        if len(data)>limit:raise ValueError('HTTP byte cap exceeded')
        self.events.append(dict(host=host,start=start,status=status,bytes=len(data),url=scrub(url)))
        if status in (429,503):self.bucket.defer(host,retry_seconds(headers.get('retry-after')))
        return status,headers,data
    def refresh_robots(self,urls=()):
        """Each W1 invocation discards decisions, even with warm media caches."""
        self.robots.clear();self.delays.clear();self.robots_failed={}
        for url in sorted(set(urls)):
            try:self.check_robots(url)
            except (AccessStopped,NetworkFailure) as e:
                p=urllib.parse.urlsplit(url);self.robots_failed[p.scheme.lower()+'://'+p.netloc.lower()]=str(e)
    def check_robots(self,url):
        p=urllib.parse.urlsplit(url);origin=p.scheme.lower()+'://'+p.netloc.lower()
        if origin in getattr(self,'robots_failed',{}):raise AccessStopped('robots unreachable for origin; item stopped')
        if origin not in self.robots:
            target=origin+'/robots.txt'
            for _ in range(5):
                try:status,headers,data=self.raw(target,262144)
                except NetworkFailure:raise AccessStopped('robots unreachable; source stopped') from None
                if status not in (301,302,303,307,308):break
                nexturl=urllib.parse.urljoin(target,headers.get('location',''))
                if urllib.parse.urlsplit(nexturl).netloc!=p.netloc:raise AccessStopped('cross-origin robots redirect')
                target=nexturl
            # RFC 9309 2.3.1.3: 4xx = unavailable -> no rules (e.g. Azure blob storage answers 400);
            # 429, 5xx and network failure = unreachable -> stop the source.
            if not (status==200 or (400<=status<500 and status!=429)):raise AccessStopped('robots unavailable; source stopped')
            text=data.decode(errors='replace') if status==200 else ''
            rp=urllib.robotparser.RobotFileParser();rp.parse(text.splitlines());rr=rp.request_rate(UA) or rp.request_rate('*')
            self.delays[p.netloc.lower()]=max(rp.crawl_delay(UA) or rp.crawl_delay('*') or 0,rr.seconds/rr.requests if rr else 0)
            self.robots[origin]=text
        if not robots_allowed(self.robots[origin],url,UA):raise AccessStopped('robots disallowed path')
    def prune_media(self):
        removed=0
        for body in (self.cache/'http').glob('*.body'):
            with body.open('rb') as f:prefix=f.read(8)
            if prefix.startswith((b'%PDF',b'\xff\xd8\xff',b'\x89PNG')):
                removed+=body.stat().st_size;body.unlink();body.with_suffix('.json').unlink(missing_ok=True)
        return removed
    def evict(self,url):
        key=sha_bytes(url.encode());body=self.cache/'http'/(key+'.body');meta=body.with_suffix('.json')
        size=body.stat().st_size if body.exists() else 0
        body.unlink(missing_ok=True);meta.unlink(missing_ok=True);return size
    def get(self,url,limit=160_000_000):
        self.check_robots(url)
        key=sha_bytes(url.encode());body=self.cache/'http'/(key+'.body');meta=body.with_suffix('.json')
        if body.exists() and meta.exists():
            m=read_json(meta);data=body.read_bytes()
            if sha_bytes(data)!=m['sha256']:raise ValueError('HTTP cache hash mismatch')
            if m.get('final_url'):self.check_robots(m['final_url'])
            return data
        server_errors=0;throttled=0
        for _ in range(8+2*NETWORK_RETRIES):
            self.check_robots(url);status,headers,data=self.raw(url,limit)
            if status in (301,302,303,307,308):url=urllib.parse.urljoin(url,headers.get('location',''));continue
            if status in (401,403) or b'captcha' in data[:10000].lower():raise AccessStopped('access control or CAPTCHA; source stopped')
            if status in (429,503):
                # Honour Retry-After by waiting: raw() already persisted the host deferral, so the next
                # acquire sleeps until then. Long or repeated deferrals stop the item, never bypass.
                wait=retry_seconds(headers.get('retry-after'))
                if throttled<NETWORK_RETRIES and wait<=900:throttled+=1;continue
                raise AccessStopped('Retry-After persisted; restart later, no bypass')
            if status in (500,502,504) and server_errors<NETWORK_RETRIES:
                # Transient server error: back off on this host and retry through the shared limiter.
                self.bucket.defer(urllib.parse.urlsplit(url).netloc.lower(),30*(2**server_errors));server_errors+=1;continue
            if status!=200:raise HTTPStatusFailure(f'HTTP status {status}')
            atomic_bytes(body,data);write_json(meta,dict(sha256=sha_bytes(data),bytes=len(data),final_url=url));return data
        raise HTTPStatusFailure('redirect limit')

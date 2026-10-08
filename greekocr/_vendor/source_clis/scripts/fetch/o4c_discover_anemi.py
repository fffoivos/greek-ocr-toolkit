#!/usr/bin/env python3
"""S2: authenticated, robots-aware Anemi catalogue and bounded viewer PDF probes."""
import html, http.cookiejar, posixpath, xml.etree.ElementTree as ET
from html.parser import HTMLParser
from o4c_common import *
BASE='https://anemi.lib.uoc.gr'
SITE_RESTRICTION='Commercial use is strictly prohibited. Systematic storage or printing of the whole content of the digital items is strictly forbidden.'
ANEMI_BUDGET=1_500_000_000

class AnemiHTTP(HTTP):
    """Cookie jar stays in memory; no automatic raw-response body cache.

    Only allowlisted response headers and public URLs enter the shared ledger.
    POST bodies, cookies, login responses and account banners are never recorded.
    Explicitly selected public fixtures are recorded separately from this transport.
    The inherited lock, robots gate and rate state cover every request/redirect.
    """
    def __init__(self, offline=False, interval=2, root=EVIDENCE, **kwargs):
        if interval < 2:raise ValueError('Anemi interval must be >= 2 seconds')
        super().__init__('anemi',offline,interval,budget=ANEMI_BUDGET,root=root,**kwargs)
        self.jar=http.cookiejar.CookieJar()
        self.opener=urllib.request.build_opener(NoRedirect,urllib.request.HTTPCookieProcessor(self.jar),
            urllib.request.HTTPSHandler(context=ssl.create_default_context()))
        self._post_body=None
        self.secrets=tuple(os.environ.get(k,'') for k in ('ANEMI_USER','ANEMI_PASS'))

    def safe(self, value):
        def strings(item):
            # Inspect values directly: repr(dict) can hide newline/backslash secrets.
            if isinstance(item,dict):
                for key,val in item.items():yield from strings(key);yield from strings(val)
            elif isinstance(item,(list,tuple,set)):
                for val in item:yield from strings(val)
            else:yield str(item)
        patterns={s for secret in self.secrets+tuple(cookie.value for cookie in self.jar) if secret
            for s in (secret,urllib.parse.quote(secret,safe=''),urllib.parse.quote_plus(secret,safe=''),html.escape(secret))}
        if any(s in text for text in strings(value) for s in patterns):
            raise ProbeError('private account data excluded from evidence')
        return value

    def event(self,**kwargs):
        self.safe(kwargs);return super().event(**kwargs)

    def check_robots(self,url):
        path=posixpath.normpath(urllib.parse.unquote(urllib.parse.urlsplit(url).path))
        if path in ('/tools','/db') or path.startswith(('/tools/','/db/')):raise ProbeError('explicitly prohibited Anemi path')
        return super().check_robots(url)

    def _raw(self,url,limit,range_header=None,depth=0):
        self.safe(url)
        parts=urllib.parse.urlsplit(url)
        path=posixpath.normpath(urllib.parse.unquote(parts.path))
        if path in ('/tools','/db') or path.startswith(('/tools/','/db/')):
            raise ProbeError('explicitly prohibited Anemi path')
        if any(re.search(r'cookie|session|phpsess|token|password|username',k,re.I) for k in urllib.parse.parse_qs(parts.query)):
            raise ProbeError('private URL parameters excluded from evidence')
        if self.offline:raise ProbeError('authenticated transport disabled offline; use recorded public fixtures')
        host=urllib.parse.urlsplit(url).netloc
        interval=max(self.interval,self.robots.get(host,{}).get('delay',0))
        previous=self.last.get(host);elapsed=max(0,time.time()-previous) if previous is not None else interval
        time.sleep(max(0,interval-elapsed));self.last[host]=time.time()
        started_at=datetime.datetime.fromtimestamp(self.last[host],datetime.timezone.utc).isoformat()
        remaining=self.budget-self.transferred
        if remaining<=0:raise ProbeError('task transfer budget exhausted')
        limit=min(limit,remaining)
        headers={'User-Agent':UA,'Accept-Encoding':'identity'}
        if range_header:headers['Range']=range_header
        if self._post_body is not None:headers['Content-Type']='application/x-www-form-urlencoded'
        req=urllib.request.Request(url,data=self._post_body,headers=headers)
        try:response=self.native_open(req,limit) if sys_platform_is_macos() else self.opener.open(req,timeout=120)
        except urllib.error.HTTPError as error:response=error
        except (ProbeError,urllib.error.URLError,OSError):
            self.requests+=1
            append(self.ledger,{'url':url,'range':range_header,'method':req.get_method(),'status':0,
                'headers':{},'sha256':hashlib.sha256(b'').hexdigest(),'bytes':0,'truncated':False,
                'read_error':'connection or TLS verification failed before response body',
                'request_started_at':started_at,'rate_interval_seconds':interval,
                'fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'source':'anemi','user_agent':UA,'body_storage':'memory-only'})
            raise ProbeError('Anemi connection or TLS verification failed') from None
        body=b'';truncated=False
        with response:
            status=response.code
            # No Set-Cookie, Location (may contain session identifiers), or account headers on disk.
            safe_headers={k.lower():v for k,v in response.headers.items() if k.lower() in
                ('content-length','content-range','content-type','content-encoding','accept-ranges')}
            for key,value in list(safe_headers.items()):
                try:self.safe(value)
                except ProbeError:safe_headers.pop(key)
            redirect=response.headers.get('Location')
            length=int(safe_headers.get('content-length','0') or 0)
            if length>limit:truncated=True
            else:
                chunks=[];n=0
                try:
                    while n<limit:
                        chunk=response.read(min(65536,limit-n))
                        if not chunk:break
                        chunks.append(chunk);n+=len(chunk)
                except (OSError,http.client.IncompleteRead) as error:
                    partial=getattr(error,'partial',b'')[:limit-n]
                    chunks.append(partial);truncated=True
                body=b''.join(chunks)
                truncated=truncated or (len(body)==limit and (not length or length>limit)) or bool(length and len(body)<length)
        self.transferred+=len(body);self.requests+=1
        m={'url':url,'range':range_header,'method':'POST' if self._post_body is not None else 'GET',
           'status':status,'headers':safe_headers,'sha256':hashlib.sha256(body).hexdigest(),
           'request_started_at':started_at,'rate_interval_seconds':interval,
           'bytes':len(body),'truncated':truncated,'fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'source':'anemi','user_agent':UA,'body_storage':'memory-only'}
        append(self.ledger,m)
        # Redirect is used only in memory by HTTP.get/check_robots.
        if redirect:m['headers']={**safe_headers,'location':redirect}
        if truncated:raise ProbeError('Anemi response exceeds probe limit')
        return m,body

    def native_open(self,req,limit):
        """macOS native verified TLS, with curl config/headers/body in pipes only.

        No cookie file, header file, argv secret, debug output, or automatic redirect.
        Read response headers separately so Set-Cookie reaches only CookieJar.
        """
        import email.parser
        self.jar.add_cookie_header(req)
        def quoted(s):return '"'+s.replace('\\','\\\\').replace('"','\\"').replace('\r','').replace('\n','')+'"'
        config=['url = '+quoted(req.full_url)]
        config+=['header = '+quoted(k+': '+v) for k,v in req.header_items()]
        if req.data is not None:config.append('data = '+quoted(req.data.decode('ascii')))
        # -q must be first: a user's curlrc must not enable traces or cookie files.
        child_env={k:v for k,v in os.environ.items() if k not in ('ANEMI_USER','ANEMI_PASS','SSLKEYLOGFILE')}
        proc=subprocess.Popen(['/usr/bin/curl','-q','--silent','--max-time','120','--include',
            '--max-filesize',str(limit),'--config','-'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,env=child_env)
        proc.stdin.write(('\n'.join(config)+'\n').encode());proc.stdin.close()
        try:
            while True:
                first=proc.stdout.readline(8192)
                if not first.startswith(b'HTTP/'):raise ProbeError('Anemi native TLS/HTTP connection failed')
                status=int(first.split()[1]);lines=[];header_bytes=len(first)
                while True:
                    line=proc.stdout.readline(8192);header_bytes+=len(line)
                    if header_bytes>65536 or not line:raise ProbeError('invalid Anemi response headers')
                    if line in (b'\r\n',b'\n'):break
                    lines.append(line)
                headers=email.parser.BytesParser().parsebytes(b''.join(lines))
                if status>=200 and b'Connection established' not in first:break
            class Response:
                code=status
                def __init__(self):self.headers=headers
                def info(self):return self.headers
                def read(self,n):return proc.stdout.read(n)
                def __enter__(self):return self
                def __exit__(self,*args):
                    proc.terminate() if proc.poll() is None else None
                    proc.stdout.close();proc.wait()
            response=Response();self.jar.extract_cookies(response,req)
            return response
        except BaseException:
            if proc.poll() is None:proc.terminate()
            proc.stdout.close();proc.wait();raise

    def post(self,url,fields):
        if urllib.parse.urlsplit(url).netloc!=urllib.parse.urlsplit(BASE).netloc:
            raise ProbeError('login must remain on Anemi HTTPS origin')
        if not url.startswith(BASE+'/'):raise ProbeError('login must use HTTPS')
        self.check_robots(url)
        self._post_body=urllib.parse.urlencode(fields).encode()
        try:m,b=self.raw(url,2_000_000)
        finally:self._post_body=None
        if m['status'] in (301,302,303,307,308):
            if m['status'] in (307,308):raise ProbeError('login POST redirect refused')
            return self.get(urllib.parse.urljoin(url,m['headers']['location']),limit=2_000_000)
        if m['status']!=200:raise ProbeError('login HTTP failure')
        return m,b

def sys_platform_is_macos():
    import sys
    return sys.platform=='darwin'

class Page(HTMLParser):
    """Small stdlib HTML parser for forms and public links."""
    def __init__(self,data):
        super().__init__(convert_charrefs=True);self.forms=[];self.links=[];self.text=[];self.form=None;self.link=None
        self.feed(data.decode('utf-8','replace') if isinstance(data,bytes) else data)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='form':self.form={**a,'inputs':[]};self.forms.append(self.form)
        if tag=='input' and self.form is not None:self.form['inputs'].append(a)
        if tag=='a':self.link={**a,'text':''};self.links.append(self.link)
    def handle_endtag(self,tag):
        if tag=='form':self.form=None
        if tag=='a':self.link=None
    def handle_data(self,data):
        self.text.append(data)
        if self.link is not None:self.link['text']+=data

def login_form(data,url):
    form=next((f for f in Page(data).forms if any(i.get('type')=='password' for i in f['inputs'])),None)
    if form is None:raise ProbeError('no login form found')
    if form.get('method','get').lower()!='post':raise ProbeError('refuse credentials in a GET form')
    target=urllib.parse.urldefrag(urllib.parse.urljoin(url,form.get('action',url)))[0]
    fields={i['name']:i.get('value','') for i in form['inputs'] if i.get('name') and i.get('type')=='hidden'}
    password=next(i['name'] for i in form['inputs'] if i.get('type')=='password')
    username=next((i['name'] for i in form['inputs'] if i.get('type') in ('text','email') and i.get('name')),None)
    if username is None:raise ProbeError('no login ID field found')
    return target,fields,username,password

def authenticate(http):
    user=os.environ.get('ANEMI_USER');password=os.environ.get('ANEMI_PASS')
    if not user or not password:raise ProbeError('ANEMI_USER and ANEMI_PASS are required')
    url=BASE+'/login/?action=login'
    receipt,body=http.get(url,limit=2_000_000)
    target,fields,user_key,pass_key=login_form(body,receipt['url'])
    fields.update({user_key:user,pass_key:password})
    _,body=http.post(target,fields)
    # A cookie alone proves nothing; require the signed-in navigation state.
    links=Page(body).links
    success=any('logout' in x.get('href','').lower() or 'sign out' in x['text'].lower() for x in links)
    if not success:raise ProbeError('Anemi authentication not verified')
    http.event(stage='authentication',url=url,status='verified-signed-in-navigation',cookie_storage='memory-only')
    return True

def parse_oai(data):
    tree=ET.fromstring(data);out=[]
    for rec in tree.findall('.//{*}record'):
        header=rec.find('{*}header')
        if header is None or header.get('status')=='deleted':continue
        identifier=header.findtext('{*}identifier');dc=rec.find('.//{http://www.openarchives.org/OAI/2.0/oai_dc/}dc')
        if dc is None:continue
        vals=lambda k:[x.text or '' for x in dc.findall('{http://purl.org/dc/elements/1.1/}'+k)]
        ids=vals('identifier');url=next((u for u in ids if u.startswith('http')),BASE)
        dates=vals('date');year=next((int(x[:4]) for x in dates if re.match(r'\d{4}',x)),None)
        r=row('anemi',identifier,(vals('title') or [identifier])[0],url,year=year,rights=vals('rights')+[SITE_RESTRICTION],language=vals('language'),site_restriction=SITE_RESTRICTION)
        r['download_url']=next((u for u in ids if re.search(r'\.(pdf|djvu)(?:\?|$)',u,re.I)),None)
        out.append(r)
    token=tree.findtext('.//{*}resumptionToken');return out,token

def parse_search(data):
    text=data.decode('utf-8','replace');out=[];seen=set()
    for block in re.findall(r'<tr\b[^>]*class=["\']resultsnorm["\'][^>]*>(.*?)</tr>',text,re.S|re.I):
        match=re.search(r'srfile=([^"\'&]+)',html.unescape(block))
        title_match=re.search(r'>Title:</span>(.*?)(?:<br|</p)',block,re.S|re.I)
        if not match or not title_match:continue
        id=urllib.parse.unquote(match[1]);title=html.unescape(re.sub('<[^>]+>',' ',title_match[1])).strip()
        if id in seen:continue
        seen.add(id)
        # Overview's first href is a query-position link; srfile is a SAVE action.
        # Neither is a stable document URL. Never visit the SAVE action.
        url=BASE+id
        date=re.search(r'>Publication Date:</span>(.*?)(?:<br|</p)',block,re.I|re.S)
        years=re.findall(r'(?<!\d)(1[5-9]\d{2}|20\d{2})(?!\d)',date[1] if date else '')
        creator=re.search(r'>(?:Creator|Author):</span>(.*?)(?:<br|</p)',block,re.I|re.S)
        r=row('anemi',id,title,url,year=None,rights=None,
          site_restriction=SITE_RESTRICTION,metadata_url=BASE+id,media_status='unverified')
        r['year']=int(years[0]) if years else None
        r['author']=r['creator']=visible(creator[1]) if creator else None
        out.append(r)
    return out

def visible(fragment):
    return ''.join(Page(fragment).text).strip()

def search_url(start,end,language,material,offset=1,number=100):
    return api(BASE+'/search/',search_type='advanced',display_mode='overview',wf_step='init',
        number=number,offset=offset,cclfield4='datefrom',cclterm4=start,cclop3='and',
        cclfield5='dateto',cclterm5=end,cclop4='and',cclfield7='lang',cclterm7=language,cclop6='and',
        cclfield8='collection',cclterm8='/hierarchy/material/'+material,cclop7='and',
        store_query=1,dtab='m',**{'search_coll[metadata]':1})

def search_total(data):
    text=visible(data.decode('utf-8','replace'))
    # Actual site text: Results 1 - 42 from 42; detail uses Current Record.
    match=re.search(r'(?:Results|Records)\s*:?\s*[\d,]+\s*-\s*[\d,]+\s*(?:from|of)\s*([\d,]+)',text,re.I)
    if not match:match=re.search(r'(?:from|of)\s+([\d,]+)\s*(?:results|records)',text,re.I)
    return int(match[1].replace(',','')) if match else None

def search_positions(data):
    blocks=re.findall(r'<tr\b[^>]*class=["\']resultsnorm["\'][^>]*>(.*?)</tr>',data.decode('utf-8','replace'),re.S|re.I)
    if any(('Document is invalid after' not in visible(x)) and
           (not re.search(r'srfile=([^"\'&]+)',html.unescape(x)) or not re.search(r'>Title:</span>',x)) for x in blocks):
        raise ProbeError('unparsed catalogue position; cursor not advanced')
    return len(blocks)

def parse_detail(data,r,terms):
    """Single-record metadata only; reject the site's merged multi-record detail view."""
    text=data.decode('utf-8','replace') if isinstance(data,bytes) else data
    text=text[text.find('<div class="data">'):] if '<div class="data">' in text else text
    attachment_names=set(re.findall(r'[/]attached-(metadata-[^/\s\"\']+)/',text))
    if len(attachment_names)>1:raise ProbeError('merged multi-record detail response refused')
    fields={};previous=None
    for label,value in re.findall(r'<td\b[^>]*class=["\']detaillabel["\'][^>]*>(.*?)</td>\s*<td\b[^>]*class=["\']detailtext["\'][^>]*>(.*?)</td>',text,re.I|re.S):
        label=visible(label);value=visible(value)
        if label:previous=label
        if previous:fields.setdefault(previous,[]).append(value)
    if not fields.get('Title'):raise ProbeError('no single-record metadata found')
    permanent=fields.get('Permanent Link',[])
    if permanent and permanent!=[BASE+r['document_id']]:raise ProbeError('metadata identity mismatch')
    if len(fields.get('Title',[]))!=1:
        raise ProbeError('merged multi-record detail response refused')
    r['title']=fields['Title'][0]
    r['author']=r['creator']=fields.get('Creator') or fields.get('Author') or r.get('author')
    dates=fields.get('Date of publication',[])
    years=re.findall(r'(?<!\d)(1[5-9]\d{2}|20\d{2})(?!\d)',' '.join(dates))
    r['year']=int(years[0]) if years else r.get('year')
    r['publication_date_displayed']=dates
    r['language']=fields.get('Language',[])
    r['physical_description']=fields.get('Physical description',[])
    r['metadata_fields_displayed']=fields
    rights=[v for k,values in fields.items() if re.search(r'rights|licen[cs]e|copyright|access',k,re.I) for v in values]
    r['record_rights_displayed']=rights
    r['terms']=terms;r['site_restriction']=terms['quote']
    # Site restrictions remain binding evidence even if a record declares PD/CC.
    r['rights']=license_info(rights+[terms['quote']])
    r['licence_tier']='research-access-only; redistribution not granted; commercial use prohibited'
    files=[]
    for link in Page(text).links:
        onclick=link.get('onclick','');href=link.get('href','')
        match=re.search(r"showRecaptcha\(['\"]([^'\"]+\.pdf)['\"]",onclick,re.I)
        pdf=match[1] if match else href if re.search(r'\.pdf(?:\?|$)',href,re.I) else None
        if pdf:
            # Size/pages come from this file's Download Document line, never Preservation Info.
            offset=text.find(onclick) if onclick else text.find(href)
            info=re.search(r'Size:\s*([\d,]+)\s*bytes,\s*([\d,]+)\s*pages',visible(text[offset:offset+1600]),re.I)
            files.append({'url':urllib.parse.urljoin(BASE,pdf),'size':int(info[1].replace(',','')) if info else None,
                'pages':int(info[2].replace(',','')) if info else None,'format':'PDF',
                'download_gate':'CAPTCHA' if match else 'source-listed','access':'source-declared'})
    viewers=[urllib.parse.urljoin(BASE,x['href']) for x in Page(text).links if '/php/pdf_pager.php?' in x.get('href','')]
    r['scan_files']=files;r['viewer_urls']=viewers
    r['pdf_availability']='source-listed' if files else 'not-listed-in-record'
    r['media_status']='source-declared' if files else 'no-listed-PDF'
    if files:
        r['download_url']=files[0]['url'];r['size']=files[0]['size'];r['pages']=files[0]['pages']
    else:r['download_url']=None;r['size']=None;r['pages']=None
    # PDF availability and book type are separate from catalogue presence.
    r['in_scope']=bool(r.get('year') and 1800<=r['year']<=1950 and any('Greek' in x for x in r['language']))
    r['metadata_status']='verified-source-page'
    r['status']='excluded-site-terms'
    return r

def parse_media_inventory(data,rows,terms):
    """Join bulk detail MEDIA links by explicit record/path identity, never field order.

    The legacy bulk detail page merges bibliographic arrays. Its PDF viewer's `rec`
    parameter and each attached-metadata directory still identify individual books.
    Titles/authors/years come from separate overview rows. Unattributed rights or
    bibliographic arrays are never distributed across documents.
    """
    text=data.decode('utf-8','replace');page=Page(text);by_id={r['document_id']:r for r in rows}
    viewers={};files={};current_viewer=None
    by_filename={r['document_id'].rsplit('/',1)[-1]:r['document_id'] for r in rows}
    if len(by_filename)!=len(by_id):raise ProbeError('ambiguous record filename join')
    for link in page.links:
        href=link.get('href','')
        if '/php/pdf_pager.php?' in href:
            url=urllib.parse.urljoin(BASE,href);q=urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
            if q.get('rec') and q.get('do'):
                current_viewer=(q['rec'][0],q['do'][0],url)
                viewers[(q['rec'][0],q['do'][0])]=url
        match=re.search(r"showRecaptcha\(['\"]([^'\"]+\.pdf)['\"]",link.get('onclick',''),re.I)
        if not match:continue
        pdfpath=urllib.parse.urlsplit(match[1]).path
        parent,name=pdfpath.rsplit('/',1)
        directory,attachment=parent.rsplit('/',1)
        if not attachment.startswith('attached-metadata-'):continue
        attachment_id=directory+'/'+attachment.removeprefix('attached-')+'.tkl'
        # Bulk detail incorrectly reuses the FIRST record's directory and rec parameter.
        # Join ONLY the unique attached-metadata filename to an overview record filename.
        # Retain the broken displayed URL and label the canonical reconstruction.
        identifier=by_filename.get(attachment.removeprefix('attached-')+'.tkl')
        if identifier is None:raise ProbeError('bulk PDF attachment outside bound overview records')
        start=text.find(link['onclick'])
        info=re.search(r'Size:\s*([\d,]+)\s*bytes,\s*([\d,]+)\s*pages',visible(text[start:start+1600]),re.I)
        if not info:raise ProbeError('PDF attachment has no individually bound size/page line')
        canonical=identifier.rsplit('/',1)[0]+'/'+attachment+'/'+name
        displayed_viewer=current_viewer[2] if current_viewer and current_viewer[1]==name else None
        viewer_query=urllib.parse.parse_qs(urllib.parse.urlsplit(displayed_viewer).query) if displayed_viewer else {}
        viewer_query.update(rec=[identifier],do=[name],maxpage=[info[2].replace(',','')])
        viewer_url=api(BASE+'/php/pdf_pager.php',**viewer_query) if displayed_viewer else None
        files.setdefault(identifier,[]).append({'url':BASE+canonical,
            'size':int(info[1].replace(',','')),'pages':int(info[2].replace(',','')),
            'format':'PDF','download_gate':'CAPTCHA','access':'source-declared',
            'viewer_url':viewer_url,'attachment_record_id':attachment_id,
            'source_url_displayed':urllib.parse.urljoin(BASE,match[1]),'viewer_url_displayed':displayed_viewer,
            'url_basis':'canonical record directory plus unique source-listed attachment filename; original PDF access unverified'})
    # A bulk rights string cannot be attributed by row position; fail closed to individual pages.
    labels=re.findall(r'<td\b[^>]*class=["\']detaillabel["\'][^>]*>(.*?)</td>',text,re.I|re.S)
    if any(re.search(r'rights|licen[cs]e|copyright|access',visible(x),re.I) for x in labels):
        raise ProbeError('bulk inventory contains unattributed rights; inspect individual records')
    for r in rows:
        r['scan_files']=files.get(r['document_id'],[])
        r['viewer_urls']=[f['viewer_url'] for f in r['scan_files'] if f.get('viewer_url')]
        if r['scan_files']:
            f=r['scan_files'][0];r.update(download_url=f['url'],pages=f['pages'],size=f['size'])
        else:r.update(download_url=None,pages=None,size=None)
        r['pdf_availability']='source-listed' if r['scan_files'] else 'not-listed-in-bound-search-inventory'
        r['language']=r.get('catalogue_languages',[])
        r['in_scope']=bool(r.get('year') and 1800<=r['year']<=1950)
        r['language_basis']='source search language filter; printed language unverified'
        r['rights']=license_info([terms['quote']]);r['record_rights_displayed']=None
        r['record_rights_verification']='no attributable record-level declaration in inventory; individual page unverified'
        r['terms']=terms;r['site_restriction']=terms['quote']
        r['licence_tier']='research-access-only; redistribution not granted; commercial use prohibited'
        r['metadata_status']='verified-source-overview-and-bound-media-links'
        r['field_verification']={'title':'source overview row; printed edition unverified',
            'author':'source overview Creator field; missing is null','year':'source overview publication date',
            'language':'source search language filter; printed language unverified',
            'pages':'source-declared per-file offered PDF page count',
            'size':'source-declared offered PDF bytes; preservation master distinct',
            'download_url':'canonical reconstruction from source record/attachment identity; full-PDF access unverified',
            'rights':'exact site access notice; individual per-record rights unverified'}
        r['media_status']='source-declared' if r['scan_files'] else 'no-listed-PDF'
        r['status']='excluded-site-terms'
    return rows

def probe_viewer_page(http,r,sample_pages=3):
    """Use the site's public page PDF viewer, without bypassing download CAPTCHA.

    At most three original pages are sampled (starting at index 2, or final page).
    Original page count/size remain source-declared; PDFium verifies the extracted page.
    """
    import pypdfium2 as pdfium
    from pypdfium2.raw import FPDF_PAGEOBJ_IMAGE
    if sample_pages not in (1,2,3):raise ValueError('sample pages must be 1..3')
    before=http.transferred
    try:
        viewer=r.get('viewer_urls',[None])[0]
        if not viewer:raise ProbeError('no public page viewer')
        q=urllib.parse.parse_qs(urllib.parse.urlsplit(viewer).query)
        index=min(2,max(0,(r.get('pages') or 1)-1));q['pageno']=[str(index+1)]
        url=api(BASE+'/php/pdf_pager.php',**q)
        template=getattr(http,'viewer_template',None)
        if template is None:
            vm,b=http.get(url,limit=1_000_000)
            match=re.search(r'<iframe\b[^>]*src=["\']([^"\']+)',b.decode('utf-8','replace'),re.I)
            if not match:raise ProbeError('viewer has no published page PDF')
            pdfurl=urllib.parse.urljoin(vm['url'],html.unescape(match[1]))
            params=urllib.parse.parse_qs(urllib.parse.urlsplit(pdfurl).query)
            path=urllib.parse.urlsplit(r['download_url']).path
            filename=(params.get('filename') or [''])[0]
            if not filename.endswith(path):raise ProbeError('viewer/attachment filename mismatch')
            http.viewer_template=template={'endpoint':pdfurl.split('?')[0],
                'filename_prefix':filename[:-len(path)],'verified_viewer_url':vm['url'],'viewer_sha256':vm['sha256']}
        else:
            path=urllib.parse.urlsplit(r['download_url']).path
            pdfurl=api(template['endpoint'],filename=template['filename_prefix']+path,pageno=index+1,pagenum=1)
        params=urllib.parse.parse_qs(urllib.parse.urlsplit(pdfurl).query)
        if params.get('pagenum')!=['1'] or params.get('pageno')!=[str(index+1)]:
            raise ProbeError('viewer PDF must contain exactly one requested page')
        n=min(sample_pages,max(1,(r.get('pages') or 1)-index))
        params['pagenum']=[str(n)];pdfurl=api(pdfurl.split('?')[0],**params)
        m,b=http.get(pdfurl,limit=8_000_000)
        if not b.startswith(b'%PDF-'):raise ProbeError('viewer did not return PDF')
        texts=[];measurements=[];images=[]
        with pdfium.PdfDocument(b) as doc:
            if len(doc)!=n:raise ProbeError('viewer PDF does not match bounded page count')
            for i in range(n):
                with closing(doc[i]) as p:
                    with closing(p.get_textpage()) as tp:text=tp.get_text_range()
                    texts.append(text);measurements.append({'page_index':index+i,**metrics(text,1,r.get('pages'))})
                    width,height=p.get_size()
                    for obj in p.get_objects():
                        if obj.type==FPDF_PAGEOBJ_IMAGE:
                            x0,y0,x1,y1=obj.get_bounds();images.append(abs((x1-x0)*(y1-y0))/(width*height))
        text='\n'.join(texts) if any(texts) else ''
        apply_text(r,text,'PDFium embedded text in source bounded-page PDF viewer',n)
        r['text_layer'].update(page_indices=list(range(index,index+n)),probe_url=pdfurl,probe_sha256=m['sha256'],
            probe_bytes=m['bytes'],viewer_url=url,viewer_template=template,
            text_sha256=hashlib.sha256(text.encode()).hexdigest(),
            scan_status='verified-large-raster-object' if max(images,default=0)>=.5 else 'unverified',
            largest_image_area_fraction=max(images,default=0),original_pdf_embedded_text='unverified; viewer derivative measured')
        r['text_layer']['page_measurements']=measurements
        r['media_status']='verified-source-bounded-page-viewer; full-PDF CAPTCHA not crossed'
    except ProbeError as error:
        r['text_layer']={'status':'unverified','error':str(error)}
    except Exception:
        r['text_layer']={'status':'unverified','error':'one-page PDF decoding failed'}
    r['text_layer']['transfer_bytes']=http.transferred-before
    r['status']='excluded-site-terms'
    return r

def main():
    p=parser('anemi');p.set_defaults(interval=2,probe_docs=1_000_000)
    p.add_argument('--catalogue-only',action='store_true',help='enumerate overview records; resume details/probes later')
    p.add_argument('--details-only',action='store_true',help='resolve metadata without PDF page probes')
    p.add_argument('--sample-pages',type=int,choices=(1,2,3),default=3)
    args=p.parse_args()
    if args.offline:raise ProbeError('use bench/tests/test_o4c_anemi.py for credential-free recorded replay')
    h=AnemiHTTP(interval=args.interval,retry_errors=args.retry_errors)
    path,state=load_state(args);rows={r['document_id']:r for r in read_rows(args.out)}
    for r in rows.values():
        if r.get('catalogue_queries'):
            stable=BASE+r['document_id']
            if r['record_url']!=stable:
                r.setdefault('previous_public_search_record_url',r['record_url'])
                r['record_url']=stable;r['metadata_url']=stable
            r['in_scope']=bool(r.get('year') and 1800<=r['year']<=1950)
            if r.get('metadata_status')=='verified-source-page':
                r['in_scope']=r['in_scope'] and any('Greek' in x for x in r.get('language',[]))
            r.setdefault('author',r.get('creator'));r.setdefault('creator',r.get('author'))
    state.update(schema_version='anemi-crawl-2',transfer_limit_bytes=ANEMI_BUDGET,
        rate_interval_seconds=args.interval,cookie_storage='memory-only',scope_years=[1800,1950],
        scope_languages=['gre','grc'],scope_materials=['010','020'])
    authenticate(h);state['authentication']='verified-signed-in-navigation'
    m,b=h.get(BASE+'/',limit=2_000_000)
    quotes=[visible(x) for x in re.findall(r'<em>(.*?)</em>',b.decode('utf-8','replace'),re.S) if 'Systematic storage' in x]
    if len(quotes)!=1:raise ProbeError('displayed site terms could not be bound')
    terms={'url':BASE+'/','quote':quotes[0],'fetched_at':m['fetched_at'],'response_sha256':m['sha256']}
    h.safe(terms);write_json(EVIDENCE/'anemi_terms.json',terms)
    streams=state.setdefault('streams',{});count=0
    for start in range(1800,1951,10):
      for language in ('gre','grc'):
       for material in ('010','020'):
        key=f'{start}-{min(start+9,1950)}:{language}:{material}'
        stream=streams.setdefault(key,{'offset':1,'complete':False,'urls':[],'records_returned':0})
        while not stream['complete'] and (args.all or count<args.max_pages):
            u=search_url(start,min(start+9,1950),language,material,stream['offset'])
            try:
                m,b=h.get(u,limit=4_000_000);new=parse_search(b);positions=search_positions(b)
                text=visible(b.decode('utf-8','replace'))
                if 'CCL error' in text:raise ProbeError('catalogue CCL error')
                total=search_total(b)
                h.safe(new)
                h.event(stage='authenticated-catalogue',url=u,documents=len(new),reported_total=total,sha256=m['sha256'])
                if not stream['urls']:
                    stream['reported_total']=total
                elif total is not None and total!=stream['reported_total']:
                    stream['changed_total']=total
                # One portable overview fixture, with navigation/account banners stripped.
                if not (EVIDENCE/'fixtures/anemi_decade_search.html').exists():
                    blocks=re.findall(r'<tr\b[^>]*class=["\']resultsnorm["\'][^>]*>.*?</tr>',b.decode('utf-8','replace'),re.S|re.I)
                    fixture='\n'.join(blocks);h.safe(fixture)
                    (EVIDENCE/'fixtures/anemi_decade_search.html').write_text(fixture)
                    write_json(EVIDENCE/'fixtures/anemi_decade_search_provenance.json',dict(url=u,
                        response_sha256=m['sha256'],fixture_sha256=hashlib.sha256(fixture.encode()).hexdigest(),excerpt=True))
                for r in new:
                    r.setdefault('catalogue_queries',[]).append(u)
                    r['catalogue_languages']=[language];r['catalogue_materials']=[material]
                    r['in_scope']=bool(r.get('year') and 1800<=r['year']<=1950)
                    if r['document_id'] in rows:
                        old=rows[r['document_id']]
                        if not old.get('metadata_status'):
                            for field in ('title','year','author','creator','record_url','metadata_url','in_scope'):
                                old[field]=r.get(field)
                        for field in ('catalogue_queries','catalogue_languages','catalogue_materials'):
                            old[field]=sorted(set(old.get(field,[])+r[field]))
                    else:rows[r['document_id']]=r
                stream['urls'].append(u);stream['records_returned']+=positions
                stream['offset']+=positions
                stream['complete']=positions==0 or (total is not None and stream['offset']>total) or (total is None and positions<100)
                stream['invalid_positions']=stream.get('invalid_positions',0)+positions-len(new)
                if new and positions<100 and total is not None and stream['offset']<=total:
                    raise ProbeError('catalogue pagination cardinality mismatch')
                if len(stream['urls'])>1 and new and all(r['document_id'] in stream.get('last_ids',[]) for r in new):
                    stream['complete']=False;raise ProbeError('catalogue repeated page; no complete-census claim')
                stream['last_ids']=[r['document_id'] for r in new]
                count+=1;save_rows(args.out,rows.values());write_json(path,state)
                print('catalogue',key,'offset',stream['offset'],'records',len(rows),'bytes',h.transferred,flush=True)
            except ProbeError as error:
                stream['error']=str(error);h.event(stage='authenticated-catalogue',url=u,error=str(error))
                save_rows(args.out,rows.values());write_json(path,state);raise
    state['catalogue_complete']=len(streams)==64 and all(s['complete'] for s in streams.values())
    if not args.catalogue_only:
      inventories=state.setdefault('media_inventories',{})
      urls=sorted({u for r in rows.values() for u in r.get('catalogue_queries',[])})
      # Metadata first, so budget-limited text probes do not hide catalogue/PDF counts.
      for overview in urls:
        if inventories.get(overview,{}).get('complete'):continue
        group=[r for r in rows.values() if overview in r.get('catalogue_queries',[])]
        q=urllib.parse.parse_qs(urllib.parse.urlsplit(overview).query);q['display_mode']=['detail']
        url=api(BASE+'/search/',**q)
        failures=sum(r.get('url')==url and r['status']==0 for r in read_rows(h.ledger))
        m={'sha256':None,'fetched_at':None}
        try:
            if failures>=2:raise ProbeError('bulk transport failed twice; use individual source pages')
            m,b=h.get(url,limit=8_000_000);parse_media_inventory(b,group,terms)
        except ProbeError as error:
            # Unjoinable or attributable record-rights fields require individual evidence.
            h.event(stage='media-inventory-fallback',url=url,error=str(error),documents=len(group))
            for r in group:
                if r.get('metadata_status')=='verified-source-page':continue
                rm,rb=h.get(r['record_url'],limit=2_000_000);parse_detail(rb,r,terms)
                r['metadata_sha256']=rm['sha256'];r['metadata_fetched_at']=rm['fetched_at']
                h.safe(r);save_rows(args.out,rows.values());write_json(path,state)
        h.safe(group)
        for r in group:
            r['inventory_url']=url;r['inventory_sha256']=m['sha256'];r['inventory_fetched_at']=m['fetched_at']
        inventories[overview]={'url':url,'sha256':m['sha256'],'complete':True,'documents':len(group),
            'PDF_documents':sum(bool(r['download_url']) for r in group)}
        save_rows(args.out,rows.values());write_json(path,state)
        print('inventories',len(inventories),'of',len(urls),'PDF_docs',sum(bool(r['download_url']) for r in rows.values()),'bytes',h.transferred,flush=True)
      if not args.details_only:
       done=0
       for r in sorted(rows.values(),key=lambda r:(-(r.get('year') or 0),r['document_id'])):
        if not (r.get('in_scope') and r.get('viewer_urls')) or 'page_indices' in r['text_layer']:continue
        if done>=args.probe_docs:state['stop_reason']='invocation-probe-limit';break
        if h.budget-h.transferred<9_000_000:state['stop_reason']='transfer-budget-reserve';break
        probe_viewer_page(h,r,args.sample_pages);done+=1;h.safe(r)
        h.event(stage='viewer-text-probe',document_id=r['document_id'],
            status=r['text_layer']['status'],page_indices=r['text_layer'].get('page_indices'),
            probe_url=r['text_layer'].get('probe_url'),probe_sha256=r['text_layer'].get('probe_sha256'))
        if done%10==0:
            save_rows(args.out,rows.values());write_json(path,state)
            print('probes',done,'with_layer',sum(x['text_layer']['status']=='verified' for x in rows.values()),'bytes',h.transferred,flush=True)
    state['details_resolved']=sum(r.get('metadata_status','').startswith('verified-source-') for r in rows.values())
    state['documents']=sum(r.get('in_scope',False) for r in rows.values())
    state['polytonic_docs']=sum(r.get('in_scope',False) and r.get('polytonic_document',False) for r in rows.values())
    state['pdf_with_layer']=sum(r.get('in_scope',False) and r['text_layer']['status']=='verified' for r in rows.values())
    state['payload_bytes_cumulative']=h.transferred
    state['inventory_complete']=state['catalogue_complete'] and all(r.get('metadata_status','').startswith('verified-source-') for r in rows.values() if r.get('catalogue_queries'))
    state['probes_complete']=all('page_indices' in r['text_layer'] for r in rows.values() if r.get('in_scope') and r.get('viewer_urls'))
    state['complete']=state['inventory_complete'] and state['probes_complete']
    save_rows(args.out,rows.values());write_json(path,state)
    print(json.dumps({k:state[k] for k in ('documents','polytonic_docs','pdf_with_layer','payload_bytes_cumulative','complete')},ensure_ascii=False),flush=True)
if __name__=='__main__':main()

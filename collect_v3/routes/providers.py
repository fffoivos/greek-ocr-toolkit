"""F2 route adaptations: IA page JPEG, MDZ/NLG IIIF, OJS and official PDFs.

Derived from F2 IA census.manifest/fetch_page, INTL acquire.resolve/page,
GR sample.Source.metadata/get_pages and f2lib.fetch_pdf. No external worktree imports.
"""
from __future__ import annotations
import contextlib,io,json,re,xml.etree.ElementTree as ET,zipfile
from pathlib import Path
from urllib.parse import quote,urljoin,urlsplit,parse_qs
from html.parser import HTMLParser
from PIL import Image
from ..common import sha_bytes,read_json,write_json,atomic_bytes
from ..planner import rng

class Links(HTMLParser):
    def __init__(self,data):
        super().__init__();self.links=[];self.feed(data.decode(errors='replace') if isinstance(data,bytes) else data)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and a.get('href'):self.links.append(a['href'])

def iiif_images(d):
    if d.get('sequences'):
        return [c['images'][0]['resource'].get('@id') or c['images'][0]['resource']['id'] for c in d['sequences'][0]['canvases']]
    out=[]
    for c in d.get('items',[]):
        for ap in c.get('items',[]):
            for an in ap.get('items',[]):
                b=an.get('body',{});b=b[0] if isinstance(b,list) else b
                if b.get('id') or b.get('@id'):out.append(b.get('id') or b['@id'])
    if not out:raise ValueError('IIIF manifest has no image canvases')
    return out

def stable_download(url,item):
    if item.get('stable_redownload_url') is False:return False
    parts=urlsplit(url)
    sensitive={'token','sig','signature','expires','x-amz-signature','x-goog-signature','se'}
    return parts.scheme in ('http','https') and bool(parts.netloc) and not (sensitive & {k.lower() for k in parse_qs(parts.query)})

class Routes:
    def __init__(self,http,cache,exclusions=None):self.http=http;self.cache=Path(cache);self.exclusions=exclusions
    def pdf(self,url):
        data=self.http.get(url)
        if not data.startswith(b'%PDF'):raise ValueError('offered response is not PDF')
        if self.exclusions and sha_bytes(data) in self.exclusions.keys['media_hash']:raise ValueError('excluded PDF hash')
        import pypdfium2 as pdfium
        with pdfium.PdfDocument(data) as doc:n=len(doc)
        return data,n
    def resolve(self,item):
        key=sha_bytes((item['provider']+':'+item['id']).encode());dest=self.cache/'resolved'/(key+'.json')
        if dest.exists():
            cached=read_json(dest)
            if self.exclusions and self.exclusions.match(cached,cached['provider']):raise ValueError('excluded cached resolved item identity')
            return cached
        r=dict(item);route=r['route']
        if route=='ia':
            d=json.loads(self.http.get('https://archive.org/metadata/'+quote(r['id'],safe='')));n=int(d.get('metadata',{}).get('imagecount') or 0)
            leaves=[];fs=d.get('files',[]);sc=next((f for f in fs if 'Scandata' in f.get('format','') and not f.get('private')),None)
            if sc:
                data=self.http.get('https://archive.org/download/'+quote(r['id'],safe='')+'/'+quote(sc['name']))
                if data.startswith(b'PK'):
                    with zipfile.ZipFile(io.BytesIO(data)) as z:data=z.read(next(n for n in z.namelist() if n.endswith('.xml')))
                leaves=[int(p.attrib['leafNum']) for p in ET.fromstring(data).findall('.//pageData/page')]
            if not n:n=len(leaves)
            if not n:raise ValueError('no scandata/imagecount bounds')
            r['valid_leaves']=[p for p in leaves if 0<=p<n] if leaves else list(range(n));r['page_count']=n
            r['bounds_basis']='scandata_and_imagecount' if leaves else 'metadata_imagecount'
        elif route=='iiif':
            r['page_urls']=iiif_images(json.loads(self.http.get(r['manifest_url'])));r['page_count']=len(r['page_urls'])
        elif route=='ojs':
            # Catalogue first: enumerate every published galley in this issue,
            # flatten its pages and draw uniformly over the resulting page bounds.
            u=r['catalogue_url'];catalogue=self.http.get(u);links=Links(catalogue).links
            from bs4 import BeautifulSoup
            soup=BeautifulSoup(catalogue,'html.parser');spans=[]
            for obj in soup.select('.obj_article_summary'):
                printed=obj.select_one('.pages');galley=obj.select_one('a.obj_galley_link[href]')
                numbers=re.findall(r'\d+',printed.get_text(' ',strip=True)) if printed else []
                if galley and numbers:
                    first=int(numbers[0]);last=int(numbers[1]) if len(numbers)>1 else first
                    if 0<=last-first<500:spans.append(dict(first=first,last=last,galley=urljoin(u,galley['href'])))
            if spans:
                start=min(x['first'] for x in spans);end=max(x['last'] for x in spans)
                r.update(issue_page_spans=spans,issue_printed_start=start,page_count=end-start+1,bounds_basis='F2 own-catalogue printed page spans')
                write_json(dest,r);return r
            galleys=list(dict.fromkeys(urljoin(u,v) for v in links if re.search(r'/(?:article|issue)/view/\d+/\d+$',v)))
            issue=[v for v in galleys if '/issue/view/' in v]
            if issue:galleys=issue
            if not galleys:raise ValueError('no published OJS galleys')
            pages=[];seen=set()
            for galley in galleys:
                downloads=[urljoin(galley,v) for v in Links(self.http.get(galley)).links if re.search(r'/(?:article|issue)/download/',v)]
                if not downloads:raise ValueError('galley lacks offered download')
                url=downloads[0]
                if url in seen:continue
                seen.add(url);data,n=self.pdf(url);pages.extend(dict(url=url,pdf_page=i) for i in range(1,n+1))
            r['pdf_pages']=pages;r['page_count']=len(pages);r['bounds_basis']='all offered OJS galley PDF pages in issue'
        else:
            if route=='gazette':
                if not r.get('official_catalogue_id') or not r.get('metadata_sha256'):raise ValueError('Gazette catalogue binding required')
                # Frozen A0 catalogue entry supplies the confirmed official ID;
                # request its public catalogue page before its offered download.
                self.http.get(r['catalogue_url'])
                if not r.get('url','').startswith('https://ia37rg02wpsa01.blob.core.windows.net/fek/'):raise ValueError('unofficial Gazette download')
            url=r.get('pdf_url') or r.get('url');data,n=self.pdf(url);r['page_count']=n;r['url']=url;r['pdf_sha256']=sha_bytes(data)
        if self.exclusions and self.exclusions.match(r,r['provider']):raise ValueError('excluded resolved item identity')
        write_json(dest,r);return r
    def leaf(self,record,resolved):
        leaves=resolved.get('valid_leaves') if resolved.get('route')=='ia' else list(range(1,resolved['page_count']+1))
        n=record['item_pages']
        if len(leaves)<n:raise ValueError(f'page bounds shortfall: requested {n}, available {len(leaves)}; replan required')
        # Known bounds must still agree with current provider bounds.
        if record['page'] is not None:
            if record['page'] not in leaves:raise ValueError('draw outside resolved bounds')
            return record['page']
        import random
        return random.Random(record['page_seed']).sample(leaves,n)[record['page_slot']]
    def prune(self,page,item_complete=False):
        # A render binding must be durable before the downloaded body goes away.
        binding=self.cache/'render_bindings'/(page['id']+'.json')
        if not binding.exists() or sha_bytes(Path(page['image']).read_bytes())!=read_json(binding)['image_sha256']:
            raise ValueError('render hash binding required before source eviction')
        if page.get('source_pdf_retained'):return 0
        return self.http.evict(page['provider_url'])
    def prepare_pages(self,records):
        # Resolution may inspect multiple PDFs. Render and release one item
        # before resolving another, so stable source PDFs never accumulate.
        for record in records:
            if record['route'] in ('pdf','ojs','gazette'):self.fetch(record)
    def fetch(self,record):
        binding=self.cache/'render_bindings'/(record['id']+'.json')
        if binding.exists():
            saved=read_json(binding)
            if saved['item']!=record['item'] or saved.get('page_seed')!=record.get('page_seed'):raise ValueError('render draw changed')
            if sha_bytes(Path(saved['image']).read_bytes())!=saved['image_sha256']:raise ValueError('render hash mismatch')
            return dict(saved,tranche=record.get('tranche',saved.get('tranche')))
        r=self.resolve(record['item_record']);n=self.leaf(record,r);route=r['route'];pdf_hash=None;physical='raster_scan_candidate'
        if route=='ia':url=f'https://archive.org/download/{quote(r["id"],safe="")}/page/n{n}.jpg';data=self.http.get(url);im=Image.open(io.BytesIO(data));original=sha_bytes(data)
        elif route=='iiif':url=r['page_urls'][n-1];data=self.http.get(url);im=Image.open(io.BytesIO(data));original=sha_bytes(data)
        else:
            if route=='ojs' and r.get('issue_page_spans'):
                printed=r['issue_printed_start']+n-1
                span=next((s for s in r['issue_page_spans'] if s['first']<=printed<=s['last']),None)
                if span is None:raise ValueError('drawn issue page falls in unoffered galley gap')
                offered=[urljoin(span['galley'],v) for v in Links(self.http.get(span['galley'])).links if '/article/download/' in v]
                if not offered:raise ValueError('galley lacks offered download')
                p=dict(url=offered[0],pdf_page=printed-span['first']+1)
            else:p=r['pdf_pages'][n-1] if route=='ojs' else dict(url=r.get('pdf_url') or r['url'],pdf_page=n)
            data,total=self.pdf(p['url']);pdf_hash=sha_bytes(data);original=pdf_hash;url=p['url']
            import pypdfium2 as pdfium
            with pdfium.PdfDocument(data) as doc:
                with contextlib.closing(doc[p['pdf_page']-1]) as page:
                    # Match F2 physical gate: an embedded raster is required.
                    objects=list(page.get_objects());raster=any(o.type==3 for o in objects)
                    if not raster:physical='born_digital_or_unresolved'
                    w,h=page.get_size();scale=min(200/72,3500/max(w,h))
                    with contextlib.closing(page.render(scale=scale,grayscale=True)) as bm:im=bm.to_pil().copy()
        with im:
            image=im.convert('L');native=list(image.size);image.thumbnail((3500,3500),Image.Resampling.LANCZOS)
        encoded=io.BytesIO();image.save(encoded,format='JPEG',quality=94 if route=='ia' else 92,optimize=True)
        imagepath=self.cache/'pages'/(sha_bytes(encoded.getvalue())+'.jpg');atomic_bytes(imagepath,encoded.getvalue())
        result=dict(record,id=record['id'],page=n,year=r.get('year'),title=r.get('title'),width=image.width,height=image.height,native_size=native,image=str(imagepath),image_sha256=sha_bytes(encoded.getvalue()),original_sha256=original,pdf_sha256=pdf_hash,physical=physical,provider_url=url)
        result['source_pdf_retained']=bool(pdf_hash and not stable_download(url,r))
        if result['source_pdf_retained']:
            result['source_pdf_cache']=str(self.cache/'http'/(sha_bytes(url.encode())+'.body'))
        write_json(binding,result)
        self.prune(result,True)
        return result

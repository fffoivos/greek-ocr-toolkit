"""Only the ordinary logged-in pdf_pager -> pdf_split one-page route, <=50 pages."""
from funnellib import *
from urllib.parse import urljoin,urlencode
import html
import greekocr._vendor.scripts.fetch.o4c_discover_anemi as anemi
import greekocr._vendor.scripts.fetch.o4c_common as common
anemi.UA=common.UA=UA

class Adapter:
    source='anemi'
    def __init__(self,c):self.c=c
    def get(self,url,kind='metadata',limit=8_000_000):
        if 'pdf_dump.php' in url:raise Blocked('Forbidden full-PDF route')
        start=time.time();m,b=self.c.get(url,limit=limit)
        rec=dict(source='anemi',url=url,kind=kind,status=m['status'],bytes=len(b),seconds=time.time()-start,
                 sha256=sha(b),started_at=m.get('request_started_at',stamp()),ended_at=m.get('fetched_at',stamp()),
                 host=urlsplit(url).netloc,error=None,rate_interval_seconds=2,user_agent=UA)
        append(BASE/'receipts/http.jsonl',rec);return rec,b

def run():
    start=time.time();c=anemi.AnemiHTTP(root=BASE/'bulk/anemi-http',interval=2)
    try:
        anemi.authenticate(c)
        write(BASE/'receipts/anemi-auth.json',dict(success=True,auth='signed-in navigation verified',cookies='memory only',credentials='environment only'))
        _,home=c.get('https://anemi.lib.uoc.gr/',limit=2_000_000)
        text=anemi.Page(home);flat=' '.join(text.text)
        phrase='Systematic storage or printing of the whole content of the digital items is strictly forbidden.'
        write(BASE/'receipts/anemi-terms.json',dict(url='https://anemi.lib.uoc.gr/',excerpt=phrase if phrase in flat else 'exact phrase not found; see prior rights receipt',verified=phrase in flat,rights_decision='owner',checked_at=stamp()))
        selected=json.loads((BASE.parents[3]/'docs/harvest/round1/selection.json').read_text())['books']
        held={r['book_key'] for r in json.loads((BASE.parents[3]/'docs/harvest/round1/holdout_books.json').read_text())}
        books=[b for b in selected if b['key'] not in held][:5];a=Adapter(c);count=0
        for book in books:
            volume=book['catalogue']['volumes'][0]
            meta,body=a.get(volume['viewer_url']);p=anemi.Page(body)
            match=re.search(r'<iframe\b[^>]*src=["\']([^"\']+)',body.decode('utf8','replace'),re.I)
            if not match:raise Blocked('viewer has no published page PDF iframe')
            split=urljoin(volume['viewer_url'],html.unescape(match[1]));assert urlsplit(split).path=='/php/pdf_split.php'
            from urllib.parse import parse_qs
            params=parse_qs(urlsplit(split).query);assert params.get('pagenum')==['1']
            success=0
            for i in positions(volume['pages'],10):
                if count>=50:break
                params2={k:v[0] for k,v in params.items()};params2['pageno']=i+1;params2['pagenum']=1
                u='https://anemi.lib.uoc.gr/php/pdf_split.php?'+urlencode(params2);count+=1
                rr=pdf(a,u,book['key']+'-'+str(i+1),pages=1,limit=12_000_000,extra=dict(book_key=book['key'],source_page=i+1))
                success+=rr['success']
                if not rr['success'] and any(t in rr.get('error','').lower() for t in ['captcha','429','503']):return
            if success:
                candidate('anemi',book['key'],book['title'],book['year'],volume['viewer_url'],dict(success=True,page_count=volume['pages'],http_sha256=meta['sha256']),
                          overlap_flag='collected',held_out_test=False,target_classes=['poly1850' if book['year']<1900 else 'poly1900','dialogue'],
                          scan_rights='Anemi copyright notice; systematic whole-item storage forbidden',text_rights='per author and edition unresolved',
                          licence_string=None,access_terms_url='https://anemi.lib.uoc.gr/',fresh_pages=success,proposed_for_collection=False)
        write(BASE/'receipts/anemi-run.json',dict(pages_attempted=count,books=len(books),elapsed_seconds=time.time()-start,full_pdf_calls=0))
    except Exception as e:
        write(BASE/'receipts/anemi-blocker.json',dict(error=type(e).__name__,message=str(e)[:200] if not isinstance(e,requests.RequestException) else 'connection failure',at=stamp(),elapsed_seconds=time.time()-start))
        print('anemi',type(e).__name__,flush=True)
    finally:
        # Existing Anemi transport already excludes all cookies/login bodies/credentials.
        for name in ['transfer.jsonl','events.jsonl']:
            p=BASE/'bulk/anemi-http'/name
            if p.exists():
                for r in rows(p):safe(r)
                (BASE/'receipts'/('anemi-'+name)).write_bytes(p.read_bytes())

if __name__=='__main__':run()

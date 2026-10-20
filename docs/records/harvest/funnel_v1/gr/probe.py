from funnellib import *
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import sys,html

def meta(c,url):
    try:
        r,b=c.get(url);print(c.source,'META',url,r['bytes'],flush=True);return BeautifulSoup(b,'html.parser'),r,b
    except Exception as e:
        append(BASE/'receipts/discovery-errors.jsonl',dict(source=c.source,url=url,error=str(e),at=stamp()))
        print(c.source,'BLOCK',str(e),flush=True);return None,None,None

SEEDS={
 'kosmopolis':['https://kosmopolis.library.upatras.gr/','https://kosmopolis.library.upatras.gr/index.php/xrysallis/issue/archive','https://kosmopolis.library.upatras.gr/index.php/xrysallis/issue/view/4162'],
 'pleias':['https://pleias.library.upatras.gr/','https://pleias.library.upatras.gr/index.php/kritiki/issue/view/10989'],
 'pergamos':['https://pergamos.lib.uoa.gr/','https://pergamos.lib.uoa.gr/item/uoadl:2880180'],
 'nlg-digital':['https://digitalcollections.nlg.gr/nlg-repo/dl/el/browse/1494073','https://digitalcollections.nlg.gr/nlg-repo/dl/el/browse/1493481'],
 'nlg-newspapers':['http://efimeris.nlg.gr/ns/main.html','http://efimeris.nlg.gr/ns/dateselect.asp','http://efimeris.nlg.gr/ns/demoCheckboxLeftFrame.asp'],
 'elstat':['http://dlib.statistics.gr/portal/page/portal/ESYE','https://www.statistics.gr/el/statistical-digital-library'],
 'government-gazette':['https://search.et.gr/el/search-legislation/?selectYear=1833','https://search.et.gr/el/simple-search/'],
 'bank-of-greece':['https://www.bankofgreece.gr/ekdoseis-ereyna/ekdoseis/ekthesh-dioikhth'],
 'psifiothiki':['https://digital.lib.auth.gr/collection/Rare%20Books?ln=en','https://digital.lib.auth.gr/record/151062'],
 'lekythos':['https://lekythos.library.ucy.ac.cy/archive/search?tr1=14018&tr2=Ελληνικά+Γράμματα&tr3=tree'],
 'medusa-veria':['https://medusa.libver.gr/iguana/www.main.cls?surl=medusa-veria-books-monographs'],
 'anemi':['https://anemi.lib.uoc.gr/']}

def seeds(source):
    c=HTTP(source)
    for url in SEEDS[source]:meta(c,url)

def patras(source):
    c=HTTP(source);host=source+'.library.upatras.gr';base='https://'+host
    s,r,b=meta(c,base+'/')
    if s is None:return
    journals=list(dict.fromkeys(re.findall(r'index.php/([^/"\s]+)(?:/issue/current)?["\s]',str(s))))
    journals=[j for j in journals if j not in ['index']]
    journals=(['xrysallis']+[j for j in journals if j!='xrysallis']) if source=='kosmopolis' else (['kritiki']+[j for j in journals if j!='kritiki'])
    nitems=0;npages=0
    for journal in journals[:8]:
        s,r,b=meta(c,base+f'/index.php/{journal}/issue/archive')
        if s is None:continue
        issues=list(dict.fromkeys(urljoin(base,a['href']) for a in s.select('a[href]') if '/issue/view/' in a['href']))
        for issue in issues[:5]:
            s,r,b=meta(c,issue)
            if s is None:continue
            itext=s.get_text(' ',strip=True);years=re.findall(r'\b(18\d\d|19\d\d)\b',itext[:1200]);year=int(years[0]) if years else None
            links=list(dict.fromkeys(urljoin(base,a['href']) for a in s.select('a[href]') if re.search(r'/article/view/\d+/\d+$',a['href'])))
            append(BASE/'receipts/issues.jsonl',dict(source=source,issue=issue,journal=journal,year=year,galley_links=len(links),metadata_sha256=r['sha256']))
            for galley in links[:14]:
                article=galley.rsplit('/',1)[0];item=journal+'-'+galley.split('/')[-2]
                a,ar,ab=meta(c,article)
                if a is None:continue
                title=a.select_one('.page_title') or a.title
                title=title.get_text(' ',strip=True) if title else item
                licence=a.select_one('.item.license');licence=licence.get_text(' ',strip=True) if licence else None
                # Viewer supplies the supported download path including its file ID.
                v,vr,vb=meta(c,galley)
                urls=[urljoin(base,x['href']) for x in v.select('a[href]') if '/article/download/' in x['href']] if v else []
                url=urls[0] if urls else galley.replace('/article/view/','/article/download/')
                rr=pdf(c,url,item,pages=10,limit=60_000_000,extra=dict(issue=issue,journal=journal))
                if rr['success']:
                    candidate(source,item,title,year,url,rr,issue=issue,journal=journal,licence_string=licence,scan_rights=licence or 'unresolved',access_terms_url=article,target_classes=['poly1850' if year and year<1900 else 'poly1900','headings','dialogue'])
                    nitems+=1;npages+=rr['decoded_pages']
                if nitems>=20 and npages>=50:return
                if not rr['success'] and any(x in rr.get('error','') for x in ['429','503','host stopped']):return
            if nitems>=5 and npages>=50 and source=='pleias':return
        if nitems>=5 and npages>=50:return

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='seeds':
        with ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(seeds,SEEDS))
    elif mode=='patras':patras(sys.argv[2])

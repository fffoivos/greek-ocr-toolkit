"""Metadata-only population enumeration. Independent hosts run concurrently."""
from f2lib import *
from concurrent.futures import ThreadPoolExecutor,as_completed
import datetime,html

class CensusHTTP(HTTP):
 """Reuse current-run successful metadata by exact URL and stored body hash."""
 def get(self,url,kind='metadata',limit=8_000_000,method='GET',data=None,private=False):
  p=BASE/'bulk/metadata'/(digest(url.encode())+'.body');receipt=BASE/'receipts/metadata'/(digest(url.encode())+'.json')
  if kind=='metadata' and method=='GET' and p.exists() and receipt.exists():
   r=json.loads(receipt.read_text())
   if sha(p)==r['sha256']:
    append(BASE/'receipts/metadata-reuse.jsonl',dict(source=self.source,url=url,sha256=r['sha256'],original_started_at=r['started_at'],at=stamp()));return r,p.read_bytes()
  return super().get(url,kind,limit,method,data,private)
HTTP=CensusHTTP

def patras(source):
 c=HTTP(source);base=f'https://{source}.library.upatras.gr';s,_,_=soup(c,base+'/')
 journals=sorted({m[1] for a in s.select('a[href]') if (m:=re.fullmatch(r'https://[^/]+/index.php/([^/]+)',a['href'].strip())) and m[1]!='index'})
 found={};archives=[];complete=True
 for journal in journals:
  u=base+f'/index.php/{journal}/issue/archive';visited=set()
  while u and u not in visited:
   visited.add(u);s,r,b=soup(c,u);archives.append(dict(url=u,sha256=r['sha256']))
   for a in s.select('a[href*="/issue/view/"]'):
    link=urljoin(u,a['href']);container=a.find_parent('div',class_='obj_issue_summary') or a.parent
    text=container.get_text(' ',strip=True);ys=re.findall(r'(?<!\d)(18\d\d|19\d\d)(?!\d)',text);y=int(ys[-1]) if ys else None
    if source=='kosmopolis' and y and not 1850<=y<=1930:continue
    ident=journal+'-'+link.rstrip('/').rsplit('/',1)[-1]
    found[ident]=dict(id=ident,journal=journal,title=text,year=y,catalogue_url=link,url=None,kind='periodical_issue',date_filter_status='verified archive year' if y else 'unresolved date; excluded from dated supply')
   nxt=s.select_one('a.next[href],a.nextPage[href],a[rel=next][href]')
   if not nxt:
    nxt=next((a for a in s.select('a[href*="/issue/archive/"]') if a.get_text(' ',strip=True).lower() in ['επόμενο','next','>','»']),None)
   u=urljoin(u,nxt['href']) if nxt else None
   if len(visited)>250:complete=False;break
 jsonl(BASE/'receipts'/f'{source}-archives.jsonl',archives)
 if source=='kosmopolis':
  # OJS archive cards omit dates. Resolve dates from each issue's own metadata,
  # then its first article's citation_date only when issue headings omit them.
  for it in found.values():
   if it['year']:continue
   try:
    ss,m,b=soup(c,it['catalogue_url']);head=ss.select_one('.page_title') or ss.select_one('h1');yy=year(head.get_text(' ',strip=True) if head else '')
    if not yy:
     article=next((urljoin(it['catalogue_url'],a['href']) for a in ss.select('a[href]') if re.search(r'/article/view/\d+$',a['href'])),None)
     if article:
      aa,ar,ab=soup(c,article);dt=aa.select_one('meta[name=citation_date]');yy=year(dt.get('content')) if dt else None
    it['year']=yy
   except Exception as e:append(BASE/'receipts/kosmopolis-date-errors.jsonl',dict(item=it['id'],error=type(e).__name__))
  complete=complete and all(it['year'] for it in found.values())
 records=[r for r in found.values() if source!='kosmopolis' or (r['year'] and 1850<=r['year']<=1930)]
 return population(source,records,complete,'All journal links on current home page; every linked archive page; unique published issue IDs. Article galleys are not counted as items.',journals=len(journals),issues_before_date_filter=len(found),unit='issue/volume')

def pergamos():
 source='pergamos';c=HTTP(source);c.session.headers['Content-Type']='application/json';api='https://pergamos.lib.uoa.gr/public-api/search';found=[];totals={}
 for model in ['ArchivalBook','RareBook','PsachosBook']:
  start=0
  while True:
   q=dict(start=start,count=100,models=[model],fields=[],strict=False,query=dict(filters={},aggregations=[],sorting=['id:asc']))
   r,b=c.get(api,'api_query',15_000_000,method='POST',data=json.dumps(q));d=json.loads(b);totals[model]=d.get('total');items=d.get('items',[])
   write(BASE/'receipts'/f'pergamos-catalogue-{model}-{start}.json',dict(request=q,sha256=r['sha256'],total=d.get('total'),returned=len(items)))
   for it in items:
    yo=it.get('creationYear') or it.get('temporalCoverageDateRange');y=datetime.datetime.fromtimestamp(yo['from']/1000,datetime.timezone.utc).year if isinstance(yo,dict) and yo.get('from') else None
    if not y or not 1850<=y<=1982:continue
    langs=plain(it.get('language') or it.get('languages'));title=plain(it.get('title'))
    found.append(dict(id=it['id'],title=title,year=y,catalogue_url='https://pergamos.lib.uoa.gr/item/uoadl:'+it['id'],url=None,kind=model,language_metadata=langs,metadata_sha256=r['sha256']))
   start+=len(items)
   if not items or start>=d.get('total',0):break
   if start>20000:raise ValueError('unexpected printed population >20000')
 return population(source,found,True,'Complete public-api/search of ArchivalBook, RareBook and PsachosBook; catalogue date 1850-1982; Greek print verified in random leaf; theses excluded.',model_totals=totals,unit='printed book')

def nlg():
 source='nlg-digital';c=HTTP(source);base='https://digitalcollections.nlg.gr';found={};seen=set();start=0;complete=True;total_hint=None
 # No language facet: inspect each result's actual catalogue languages. The old
 # 100091 facet is Ancient Greek and must not define the modern-Greek frame.
 while True:
  u=base+'/nlg-repo/dl/el/search.html?'+urlencode({'p.proto':'/butterfly/backie/monograph','p.collabKinds':'NLG_ONLY','p.start':start,'p.count':100})
  s,r,b=soup(c,u);links={a['href'].rsplit('/',1)[-1]:a for a in s.select('a[href]') if re.search(r'/browse/\d+$',a['href']) and a.get_text(' ',strip=True)}
  ids=set(links)
  if not ids or ids<=seen:break
  for ident,a in links.items():
   # Keep manifest metadata as the authoritative per-item date/language source.
   if ident in seen:continue
   mu=base+'/nlg-repo/dl/el/iiifmetadata/'+ident
   try:mr,mb=c.get(mu);d=json.loads(mb)
   except Exception as e:append(BASE/'receipts/nlg-metadata-errors.jsonl',dict(id=ident,error=type(e).__name__));continue
   md={plain(x.get('label')):plain(x.get('value')) for x in d.get('metadata',[])}
   y=next((year(v) for k,v in md.items() if 'Χρονολογία έκδοσης' in k),None)
   lang=next((v for k,v in md.items() if 'Γλώσσα' in k),'')
   if y and 1850<=y<=1982 and 'Ελληνική' in lang.replace('Ελληνική, Αρχαία',''):
    found[ident]=dict(id=ident,title=a.get_text(' ',strip=True),year=y,catalogue_url=base+'/nlg-repo/dl/el/browse/'+ident,url=None,manifest_url=mu,manifest_sha256=mr['sha256'],language_metadata=lang,page_count=len(d.get('sequences',[{}])[0].get('canvases',[])),kind='printed monograph')
  seen|=ids;start+=len(ids)
  print('NLG enumeration',len(seen),'eligible',len(found),flush=True)
  # A documented lower bound is preferable to consuming the entire two-hour run.
  if len(seen)>=500:complete=False;break
 return population(source,list(found.values()),complete,'Unique own-catalogue monograph search results and per-item IIIF metadata; dates 1850-1982, Modern Greek language present; Ancient-Greek-only excluded. First 500 records if complete crawl exceeds bounded census.',catalogue_records_inspected=len(seen),unit='printed book')

def elstat():
 source='elstat';c=HTTP(source);root='http://dlib.statistics.gr/portal/page/portal/ESYE/';found={};series=[]
 s,_,_=soup(c,root+'categoryyears?p_cat=10007369&p_topic=10007369')
 cats={urljoin(root,a['href']):a.get_text(' ',strip=True) for a in s.select('a[href*="categoryyears?"]') if any(x in a.get_text().lower() for x in ['yearbook','bulletin'])}
 for u,label in cats.items():
  ss,r,b=soup(c,u);years={urljoin(u,a['href']):a.get_text(' ',strip=True) for a in ss.select('a[href*="yeararticles?"]')}
  for yu,yt in years.items():
   y=year(yt)
   if not y or not 1930<=y<=1990:continue
   ys,yr,yb=soup(c,yu);yearpages={yu:ys};queue=[urljoin(yu,a['href']) for a in ys.select('a[href*="yeararticles?"]') if 'p_page' in parse_qs(urlsplit(a['href']).query) and parse_qs(urlsplit(a['href']).query).get('p_catage')==parse_qs(urlsplit(yu).query).get('p_catage')]
   for pu in queue:
    if pu not in yearpages:
     ps,pr,pb=soup(c,pu);yearpages[pu]=ps
   links=[];details=[]
   for pageurl,ps in yearpages.items():
    links += [urljoin(pageurl,a['href']) for a in ps.select('a[href]') if re.search(r'/(?:Book|Mag)/.*\.pdf',a['href'],re.I)]
    details += [urljoin(pageurl,a['href']) for a in ps.select('a[href*="showdetails?"]')]
   details=list(dict.fromkeys(details))
   for du in details:
    ds,dr,db=soup(c,du)
    for a in ds.select('a[href]'):
     if re.search(r'/(?:Book|Mag)/.*\.pdf',a['href'],re.I):links.append(urljoin(du,a['href']))
   for link in dict.fromkeys(links):
    ident=link.rsplit('/',1)[-1].removesuffix('.pdf');found[ident]=dict(id=ident,title=label+' '+yt,year=y,catalogue_url=yu,url=link,kind='yearbook/bulletin',metadata_sha256=yr['sha256'])
  series.append(dict(url=u,label=label,year_links=len(years)))
 return population(source,list(found.values()),True,'All exposed year lists for catalogue series whose title contains Yearbook or Bulletin, every linked result-page pagination and detail page for 1930-1990, and all offered /Book/ and /Mag/ PDFs; unique volume/issue PDF IDs.',series=series,unit='volume/issue')

def lekythos():
 source='lekythos';c=HTTP(source);base='https://lekythos.library.ucy.ac.cy';found={};visited=set();queue=[base+'/archive/item/14018']
 # Literary series and their constituent catalogue nodes. Each offered issue PDF
 # is a separate printed item, irrespective of its enclosing aggregate record.
 while queue:
  u=queue.pop(0)
  if u in visited:continue
  visited.add(u);s,r,b=soup(c,u)
  for li in s.select('li.bitstreams-item'):
   a=li.select_one('a[href*="/archive/download/"]')
   if not a:continue
   link=urljoin(u,a['href']);ident=link.rsplit('/',1)[-1].removesuffix('.pdf');title=li.get_text(' ',strip=True)
   found[ident]=dict(id=ident,title=title,year=year(title),url=link,catalogue_url=u,kind='literary periodical issue',metadata_sha256=r['sha256'])
  if u.endswith('/14018'):
   queue += sorted({base+'/archive/item/'+m[1] for a in s.select('a[href]') if (m:=re.search(r'/archive/item/(\d+)',a['href'])) and m[1]!='14018'})
 # Extend the documented frame with all literary catalogue nodes already found
 # in F1, freshly rebinding each node (not merely reusing the F1 PDF list).
 for old in rows(F1/'candidates_lekythos.jsonl'):
  u=old.get('catalogue_url')
  if not u or u in visited:continue
  visited.add(u);s,r,b=soup(c,u)
  for li in s.select('li.bitstreams-item'):
   a=li.select_one('a[href*="/archive/download/"]')
   if a:
    link=urljoin(u,a['href']);ident=link.rsplit('/',1)[-1].removesuffix('.pdf');title=li.get_text(' ',strip=True);found[ident]=dict(id=ident,title=title,year=year(title),url=link,catalogue_url=u,kind='literary periodical issue',metadata_sha256=r['sha256'])
 return population(source,list(found.values()),False,'Complete exposed issue-PDF lists under Ελληνικά Γράμματα collection and F1 literary catalogue nodes, freshly fetched. Lower bound on all literary books/periodicals: catalogue-wide genre enumeration not established.',catalogue_nodes=len(visited),unit='printed issue PDF')

def anemi():
 source='anemi';import greekocr._vendor.scripts.fetch.o4c_discover_anemi as a
 a.UA=a.common.UA if hasattr(a,'common') else f1.UA
 install_anemi_limiter(a);c=a.AnemiHTTP(root=BASE/'bulk/anemi-http',interval=2.1);a.authenticate(c)
 m,b=c.get(a.BASE+'/',limit=2_000_000);txt=a.visible(b.decode('utf8','replace'));phrase='Systematic storage or printing of the whole content of the digital items is strictly forbidden.'
 if phrase not in ' '.join(txt.split()):
  existing=BASE/'receipts/anemi-terms.json'
  if not existing.exists():raise ValueError('Anemi systematic-storage notice not bound')
  terms=json.loads(existing.read_text())
  append(BASE/'receipts/anemi-terms-rechecks.jsonl',dict(at=stamp(),home_sha256=m['sha256'],exact_notice_found=False,using_current_run_verified_terms_sha256=sha(existing)))
 else:
  terms=dict(url=a.BASE+'/',quote=a.SITE_RESTRICTION,response_sha256=m['sha256'],fetched_at=m['fetched_at']);write(BASE/'receipts/anemi-terms.json',terms)
 found={};streams=[];complete=True
 for decade in range(1850,1900,10):
  off=1;total=None
  while True:
   u=a.search_url(decade,decade+9,'gre','010',off);m,b=c.get(u,limit=5_000_000);new=a.parse_search(b);positions=a.search_positions(b);total=a.search_total(b)
   streams.append(dict(url=u,sha256=m['sha256'],positions=positions,total=total))
   for it in new:
    if it.get('year') and 1850<=it['year']<=1899:found[it['document_id']]=dict(id=it['document_id'],title=it['title'],year=it['year'],catalogue_url=it['record_url'],url=None,kind='printed book',systematic_storage_notice=terms['quote'])
   off+=positions
   if not positions or total is None:
    complete=False
    if not positions:break
   if total is not None and off>total or total is None and positions<100:break
 jsonl(BASE/'receipts/anemi-catalogue-streams.jsonl',streams)
 return population(source,list(found.values()),complete,'Greek-language printed-book (material 010) overview positions in five decade date-filtered catalogue searches 1850-1899; exact overlap exclusions. Empty/total-less pages before reported totals make this an enumerated lower bound, never a full census.',streams=len(streams),unit='book')

def openarchives():
 import pyarrow.parquet as pq
 from greekocr.harvest.openarchives import urls,canonical_url
 source='openarchives';binding=json.loads((F1/'receipts/hf-link-table.json').read_text());table=F1/'bulk/hf/data/external_pdfs.parquet';assert sha(table)==binding['sha256']
 rr=pq.read_table(table,columns=['collection_slug','pdf_links_json','status_code','external_link','edm_url','type']).to_pylist();rates={r['host']:r['success_percent'] for r in json.loads((F1/'receipts/oa-host-rates.json').read_text())}
 hosts={'ntua':'dspace.lib.ntua.gr','hellanicus':'hellanicus.lib.aegean.gr','Dione':'dione.lib.unipi.gr','uoi':'olympias.lib.uoi.gr','deltion':'ejournals.epublishing.ekt.gr','rep_ihu':'repository.ihu.gr'};found=[];status=[]
 for col,host in hosts.items():
  if rates.get(host,0)<95:
   status.append(dict(collection=col,host=host,eligible=False,F1_success_percent=rates.get(host),reason='coordinator host-success >=95% gate'));continue
  pool={}
  for x in rr:
   us=urls(x.get('pdf_links_json'))
   if x['collection_slug']!=col or x['status_code']!=200 or not us or not x.get('external_link'):continue
   u=html.unescape(us[0]);pool[canonical_url(u)]=x
  c=HTTP(source);bound=[]
  # Each counted lower-bound member is individually bound to an own-catalogue
  # record plus the revision-pinned HF row; never the text projection.
  order=sorted(pool);rng('oa-catalogue-'+col).shuffle(order)
  for key in order[:60]:
   x=pool[key];cu=x['external_link']
   try:
    s,m,b=soup(c,cu);offered=[urljoin(cu,a['href']) for a in s.select('a[href]')];target=urlsplit(key).path
    bound_link=any(urlsplit(u).path==target for u in offered)
    if not bound_link:continue
    def val(*names):
     for name in names:
      el=s.select_one('meta[name="'+name+'"],meta[property="'+name+'"]')
      if el and el.get('content'):return el['content']
    title=val('citation_title','DC.title','dc.title','DCTERMS.title','og:title') or s.title.get_text(' ',strip=True)
    y=year(val('citation_date','citation_publication_date','DC.date.issued','DC.date','dc.date','DCTERMS.issued'))
    ident='hf-'+digest((col+'\n'+key).encode())[:16]
    it=dict(id=ident,title=title,year=y,url=key,catalogue_url=cu,collection_slug=col,host=host,kind=x.get('type'),link_table_revision=binding['revision'],catalogue_sha256=m['sha256'],offered_pdf_path_verified=True)
    if not excluded(dict(it,source=source)):bound.append(it)
   except Exception as e:append(BASE/'receipts/oa-catalogue-failures.jsonl',dict(collection=col,catalogue_url=cu,error=type(e).__name__))
  found+=bound;status.append(dict(collection=col,host=host,eligible=True,F1_success_percent=rates[host],hf_rows=len(pool),own_catalogue_bound_lower_bound=len(bound)))
 write(BASE/'receipts/oa-collections.json',status)
 return population(source,found,False,'Per eligible collection: up to 60 seeded HF link-table records individually verified against own repository offered PDF path. Counts are catalogue-bound lower bounds; HF totals alone are not scanned-print supply.',collections=status,unit='catalogue-bound PDF item')

def gazette():
 source='government-gazette';c=HTTP(source);c.session.headers['Content-Type']='application/json';found={};queries=[];complete=True
 api='https://searchetv99.azurewebsites.net/api/simplesearch'
 for y in range(1833,1991):
  q=dict(selectYear=[str(y)],selectIssue=[],documentNumber='',searchText='',datePublished='',dateReleased='')
  dest=BASE/'bulk'/f'gazette-catalogue-{y}.json'
  if dest.exists():d=json.loads(dest.read_text());h=sha(dest)
  else:
   m,b=c.get(api,'api_query',25_000_000,method='POST',data=json.dumps(q));d=json.loads(b);write(dest,d);h=m['sha256']
  if d.get('status')!='ok':raise ValueError('official Gazette catalogue query failed')
  items=json.loads(d['data']) if isinstance(d.get('data'),str) else d.get('data',[])
  if len(items)>=12000:complete=False
  for it in items:
   number=it.get('search_DocumentNumber');issue=it.get('search_IssueGroupID')
   if not number or not issue:continue
   ident=f'{y}{int(issue):02d}{int(number):05d}'
   found[ident]=dict(id=ident,title=it.get('search_PrimaryLabel'),year=y,issue_type=int(issue),number=int(number),page_count=int(it.get('search_Pages') or 0),url=f'https://ia37rg02wpsa01.blob.core.windows.net/fek/{int(issue):02d}/{y}/{ident}.pdf',catalogue_url='https://search.et.gr/el/simple-search/?'+urlencode(dict(selectYear=y,selectIssue=issue,documentNumber=number)),kind='official issue',official_catalogue_id=it.get('search_ID'),metadata_sha256=h)
  queries.append(dict(year=y,request=q,response_sha256=h,items=len(items),truncated_possible=len(items)>=12000))
  jsonl(BASE/'receipts/gazette-catalogue-queries.jsonl',queries)
  if y%10==0:print('GAZETTE catalogue',y,len(found),flush=True)
 return population(source,list(found.values()),complete,'Every year 1833-1990 through the current official UI public simplesearch API, no text filter; unique issue-type/year/number; per-year 12000 ceiling checked. Scanned status verified in random pages, not inferred from date.',by_decade=dict(__import__('collections').Counter(str(r['year']//10*10) for r in found.values())),unit='issue')

if __name__=='__main__':
 funcs={'kosmopolis':lambda:patras('kosmopolis'),'pleias':lambda:patras('pleias'),'pergamos':pergamos,'nlg-digital':nlg,'elstat':elstat,'lekythos':lekythos,'anemi':anemi,'openarchives':openarchives,'government-gazette':gazette}
 names=sys.argv[1:] or list(funcs)
 overlap_sets()
 def run(name):
  try:funcs[name]();return name,'ok'
  except Exception as e:
   write(BASE/'receipts'/('census-error-'+name+'.json'),dict(source=name,error=type(e).__name__,message=str(e)[:400],at=stamp()));return name,type(e).__name__,str(e)[:200]
 with ThreadPoolExecutor(max_workers=len(names)) as pool:
  for future in as_completed([pool.submit(run,n) for n in names]):print('DONE',future.result(),flush=True)

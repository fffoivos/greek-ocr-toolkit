"""A0 one-leaf verification before stratified source page sampling."""
from f2lib import *
from concurrent.futures import ThreadPoolExecutor,as_completed
import html,os

class Source:
 def __init__(self,name):
  self.name=name;self.c=HTTP(name);self.resolved={}
  if name=='anemi':
   import greekocr._vendor.scripts.fetch.o4c_discover_anemi as a
   install_anemi_limiter(a);self.a=a;self.ac=a.AnemiHTTP(root=BASE/'bulk/anemi-http-sample',interval=2.1);a.authenticate(self.ac)
 def metadata(self,r):
  name=self.name;c=self.c;r=dict(r)
  if name in ['kosmopolis','pleias']:
   s,m,b=soup(c,r['catalogue_url']);galleys=list(dict.fromkeys(urljoin(r['catalogue_url'],a['href']) for a in s.select('a[href]') if re.search(r'/article/view/\d+/\d+$',a['href'])))
   spans=[]
   for obj in s.select('.obj_article_summary'):
    pg=obj.select_one('.pages');g=obj.select_one('a[href] .obj_galley_link') or obj.select_one('a.obj_galley_link[href]')
    nums=re.findall(r'\d+',pg.get_text(' ',strip=True)) if pg else []
    if g and nums:
     first=int(nums[0]);last=int(nums[1]) if len(nums)>1 else first
     if 0<=last-first<500:spans.append(dict(first=first,last=last,galley=urljoin(r['catalogue_url'],g['href'])))
   if spans:
    start=min(x['first'] for x in spans);end=max(x['last'] for x in spans)
    r.update(issue_page_spans=spans,issue_printed_start=start,page_count=end-start+1,verification_scope='seeded body leaf of issue, mapped through own catalogue article printed-page ranges',galley_downloads={})
    self.resolved[r['id']]=r;write(BASE/'receipts/items'/(name+'--'+digest(r['id'].encode())[:20]+'.json'),r);return r
   issueg=[urljoin(r['catalogue_url'],a['href']) for a in s.select('a[href]') if '/issue/view/' in a['href'] and re.search(r'/\d+/\d+$',a['href'])]
   if issueg:galleys=issueg
   if not galleys:raise ValueError('issue has no published scan galley')
   # The uniform random unit remains the issue. Its verification leaf is from
   # a seeded uniformly selected published article galley, with scope explicit.
   rng(r['id']+':galley').shuffle(galleys)
   r['galleys']=galleys;r['verification_scope']='one randomly selected article galley within catalogue issue; not an entire-issue media census'
   v,vr,vb=soup(c,galleys[0]);links=[urljoin(galleys[0],a['href']) for a in v.select('a[href]') if '/article/download/' in a['href'] or '/issue/download/' in a['href']]
   if not links:raise ValueError('published galley has no offered download link')
   r['url']=links[0];r['galley_url']=galleys[0]
   # Article citation date is preferable to archive issue heading when offered.
   art=galleys[0].rsplit('/',1)[0];aa,ar,ab=soup(c,art);dt=aa.select_one('meta[name=citation_date]')
   if dt:r['year']=year(dt.get('content')) or r.get('year')
  elif name=='pergamos':
   c.session.headers['Content-Type']='application/json';q=dict(start=0,count=1000,models=['Page'],fields=[],strict=False,query=dict(filters={'and':[{'eq':{'parents':'uoadl:'+r['id']}},{'exists':'webFile'}]},aggregations=[],sorting=['pageNumber:asc']))
   m,b=c.get('https://pergamos.lib.uoa.gr/public-api/search','api_query',20_000_000,method='POST',data=json.dumps(q));d=json.loads(b)
   pp=[p for p in d.get('items',[]) if (p.get('webFile') or {}).get('published')]
   r['image_pages']=[dict(page=int(p.get('pageNumber') or i+1),url='https://pergamos.lib.uoa.gr/public-api/files/uoadl/'+p['webFile']['id']+'/payload-inline',file_id=p['webFile']['id']) for i,p in enumerate(pp)];r['page_count']=len(pp);r['declared_page_count']=d.get('total');r['pages_list_complete']=len(d.get('items',[]))>=d.get('total',0)
  elif name=='nlg-digital':
   m,b=c.get(r['manifest_url']);d=json.loads(b);can=d.get('sequences',[{}])[0].get('canvases',[])
   r['image_pages']=[dict(page=i+1,url=p['images'][0]['resource']['@id']) for i,p in enumerate(can)];r['page_count']=len(can)
  elif name=='anemi':
   a=self.a;m,b=self.ac.get(r['catalogue_url'],limit=6_000_000)
   terms=json.loads((BASE/'receipts/anemi-terms.json').read_text());it=a.parse_detail(b,dict(document_id=r['id']),terms)
   if not it.get('viewer_urls'):raise ValueError('no ordinary offered viewer')
   viewer=it['viewer_urls'][0];m,b=self.ac.get(viewer,limit=3_000_000);match=re.search(r'<iframe\b[^>]*src=["\']([^"\']+)',b.decode('utf8','replace'),re.I)
   if not match:raise ValueError('ordinary viewer has no one-page iframe')
   split=urljoin(viewer,html.unescape(match[1]));assert urlsplit(split).path=='/php/pdf_split.php'
   q=parse_qs(urlsplit(split).query);assert q.get('pagenum')==['1']
   r.update(split_query={k:v[0] for k,v in q.items()},viewer_url=viewer,page_count=it.get('pages'),systematic_storage_notice=terms['quote'],record_rights_displayed=it.get('record_rights_displayed'))
  self.resolved[r['id']]=r;write(BASE/'receipts/items'/(name+'--'+digest(r['id'].encode())[:20]+'.json'),r);return r
 def get_pages(self,r,n=1,band=False,verify=False,positions=None):
  if r.get('issue_page_spans'):
   pp=positions or page_positions(r['page_count'],n,band,r['id']+(':verify' if verify else ':sample'));out=[]
   for i,role in pp:
    printed=r['issue_printed_start']+i-1;span=next((x for x in r['issue_page_spans'] if x['first']<=printed<=x['last']),None)
    if not span:continue
    galley=span['galley'];downloads=r.setdefault('galley_downloads',{})
    if galley not in downloads:
     s,m,b=soup(self.c,galley);links=[urljoin(galley,a['href']) for a in s.select('a[href]') if '/article/download/' in a['href']]
     if not links:raise ValueError('galley has no offered download link')
     downloads[galley]=links[0]
    rr=dict(r,url=downloads[galley],_source_page=i,_total_pages=r['page_count'])
    if excluded(rr):raise ValueError('collected/test overlap at resolved offered galley')
    got=fetch_pdf(self.c,rr,positions=[(printed-span['first']+1,role)],verify=verify)
    for p in got:p.update(printed_page=printed,galley_url=galley,issue_page_count=r['page_count'],page_band_basis='own issue catalogue first/last printed page ranges');write(BASE/'receipts'/('verify-pages' if verify else 'pages')/(p['id']+'.json'),p)
    out+=got
   return out
  if self.name=='anemi':
   pp=positions or page_positions(r['page_count'],n,band,r['id']+(':verify' if verify else ':sample'));out=[]
   class Adapter:
    source='anemi'
    def __init__(self,ac):self.ac=ac
    def get(self,url,kind='pdf',limit=12_000_000):
     if 'pdf_dump.php' in url:raise ValueError('forbidden full PDF path')
     import fcntl
     ledger=BASE/'receipts/anemi-page-reservations.jsonl'
     with ledger.with_suffix('.lock').open('a') as lock:
      fcntl.flock(lock,fcntl.LOCK_EX)
      if not ledger.exists():
       prior=[x for path in (BASE/'bulk').glob('anemi-http*/transfer.jsonl') for x in rows(path) if '/pdf_split.php?' in x['url']]
       jsonl(ledger,[dict(url=x['url'],state='historical_attempt',time=x.get('request_started_at')) for x in prior])
      if len(rows(ledger))>=50:raise ValueError('Anemi inherited 50 viewer-page request cap')
      append(ledger,dict(url=url,state='reserved_before_network',time=stamp()))
     m,b=self.ac.get(url,limit=limit);return dict(sha256=m['sha256']),b
   for i,role in pp:
    q=dict(r['split_query'],pageno=i,pagenum=1);u='https://anemi.lib.uoc.gr/php/pdf_split.php?'+urlencode(q)
    rr=dict(r,url=u,_source_page=i,_total_pages=r['page_count']);got=fetch_pdf(Adapter(self.ac),rr,positions=[(1,role)],verify=verify)
    for p in got:p.update(page=i,page_count=r['page_count'],url=u,systematic_storage_notice=r['systematic_storage_notice']);write(BASE/'receipts'/('verify-pages' if verify else 'pages')/(p['id']+'.json'),p)
    out+=got
   return out
  if r.get('image_pages') is not None:
   pp=positions or page_positions(len(r['image_pages']),n,band,r['id']+(':verify' if verify else ':sample'));out=[]
   for i,role in pp:
    ip=r['image_pages'][i-1];m,b=self.c.get(ip['url'],'image',35_000_000)
    with Image.open(io.BytesIO(b)) as im:p=raster(im.copy(),dict(r,url=ip['url']),ip['page'],role,m,total=len(r['image_pages']),verify=verify)
    out.append(p)
   return out
  return fetch_pdf(self.c,r,positions=positions,verify=verify,n=n,band=band)

def verify_script(p):
 if p['machine']['dominant_script']=='Greek':return True,'tesseract OSD Greek'
 # OSD confuses short Greek/Latin headings. A separate local diagnostic counts
 # recognized script, never supplies Google labels or released text.
 try:
  data=(BASE/p['review_image']).read_bytes();out=subprocess.run(['tesseract','stdin','stdout','-l','ell+eng','--psm','3'],input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=25,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
  txt=out.stdout.decode('utf8','replace');g=sum('\u0370'<=c<='\u03ff' or '\u1f00'<=c<='\u1fff' for c in txt);l=sum(c.isalpha() for c in txt)
  p['machine']['local_script_diagnostic']=dict(greek_letters=g,all_letters=l,greek_share=g/max(1,l),text_retained=False)
  return g>=20 and g/max(1,l)>=.25,'local ell+eng script-count diagnostic'
 except subprocess.TimeoutExpired:return False,'local script diagnostic timed out'

def run(name):
 draw=rows(BASE/f'draw_{name}.jsonl')
 if not draw:raise ValueError('population draw missing/empty')
 source=Source(name);verified=[];results=[]
 for r in draw:
  dest=BASE/'receipts/verify-items'/(name+'--'+digest(r['id'].encode())[:20]+'.json')
  if dest.exists():
   result=json.loads(dest.read_text());results.append(result)
   if result['pass']:verified.append(result['resolved_item']);source.resolved[r['id']]=result['resolved_item']
   continue
  try:
   resolved=source.metadata(r);pp=source.get_pages(resolved,verify=True)
   if not pp:raise ValueError('no eligible body leaf in short galley')
   p=pp[0];script,basis=verify_script(p);passed=p['machine_pass'] and script
   write(BASE/'receipts/verify-pages'/(p['id']+'.json'),p)
   result=dict(source=name,item=r['id'],pass_=passed,**{'pass':passed},page_id=p['id'],script_pass=script,script_basis=basis,machine_pass=p['machine_pass'],reasons=p['excluded_reasons']+([] if script else ['target_script_not_verified']),resolved_item=resolved)
   if passed:verified.append(resolved)
  except Exception as e:result=dict(source=name,item=r['id'],**{'pass':False},error=type(e).__name__,reason=str(e)[:250])
  write(dest,result);results.append(result);print('VERIFY',name,len(results),'/',len(draw),result['pass'],flush=True)
 jsonl(BASE/f'verification_{name}.jsonl',results)
 census=json.loads((BASE/'receipts'/f'census-{name}.json').read_text());N=census['N'];k=len(verified);ci=wilson(k,len(draw));census.update(verified_n=len(draw),verified_k=k,verified_share=k/len(draw),wilson95=ci,estimated_accessible_target_items=N*k/len(draw),estimated_accessible_target_items_ci=[N*x for x in ci],pages_at_40_item_ceiling=N*40*k/len(draw),pages_at_40_item_ceiling_ci=[N*40*x for x in ci],estimate_scope='enumerated frame only; lower-bound frames cannot be extrapolated to entire source; scan-print and script are diagnostic proposals pending blind native review')
 write(BASE/'receipts'/f'census-{name}.json',census)
 if len(verified)<6:
  # Add only from the same population, preserving the random-20 estimator.
  extra=[r for r in rows(BASE/f'population_{name}.jsonl') if r['id'] not in {x['id'] for x in draw}];rng(name+':replacement').shuffle(extra)
  if name=='openarchives':
   # Once the random collection samples fail, the authorised supplemental
   # search may use F1's scanned-print witnesses. Rebind them afresh to BOTH
   # the pinned HF table and their own catalogue; do not change survey N/k.
   import pyarrow.parquet as pq
   from greekocr.harvest.openarchives import urls,canonical_url
   bind=json.loads((F1/'receipts/hf-link-table.json').read_text());path=F1/'bulk/hf/data/external_pdfs.parquet';assert sha(path)==bind['sha256']
   lookup={canonical_url(html.unescape(u)) for x in pq.read_table(path,columns=['pdf_links_json']).to_pylist() for u in urls(x.get('pdf_links_json'))}
   for old in rows(F1/'candidates_openarchives.jsonl'):
    if old.get('collection_slug') not in ['Dione','uoi','deltion'] or not old.get('new_candidate_eligible') or not old.get('physical_scanned_sample') or not old.get('catalogue_url'):continue
    u=canonical_url(old['page_access_route'])
    if u not in lookup:continue
    try:
     from urllib.parse import unquote
     ss,m,b=soup(source.c,old['catalogue_url']);offered=[urljoin(old['catalogue_url'],a['href']) for a in ss.select('a[href]')]+[a['content'] for a in ss.select('meta[name=citation_pdf_url][content]')]
     if not any(unquote(urlsplit(x).path)==unquote(urlsplit(u).path) for x in offered):continue
     rr=dict(id='hf-'+digest((old['collection_slug']+'\n'+u).encode())[:16],source=name,title=old['title'],year=old.get('year'),url=u,catalogue_url=old['catalogue_url'],collection_slug=old['collection_slug'],catalogue_sha256=m['sha256'],link_table_revision=bind['revision'],offered_pdf_path_verified=True,supplemental_basis='F1 scanned witness, freshly catalogue/HF rebound after insufficient random passes')
     if not excluded(rr):extra.append(rr)
    except Exception:continue
  for r in extra:
   if r['id'] in {x['id'] for x in verified}:continue
   try:
    rr=source.metadata(r);pp=source.get_pages(rr,verify=True)
    if pp and pp[0]['machine_pass'] and verify_script(pp[0])[0]:verified.append(rr)
   except Exception as e:
    if '50 viewer-page' in str(e):break
   if len(verified)>=6:break
  jsonl(BASE/'receipts'/f'supplemental-items-{name}.jsonl',[r for r in verified if r['id'] not in {x['id'] for x in draw}])
 target=20 if name=='anemi' else 30
 # Round-robin year strata among verified random items, retaining item identity.
 groups={}
 for r in verified:groups.setdefault(period(r.get('year')),[]).append(r)
 order=[]
 while any(groups.values()):
  for key in sorted(groups):
   if groups[key]:order.append(groups[key].pop(0))
 # At most eight pages/item. Six early/late pages over six items for all sources
 # carrying headings or leaders; Anemi's separate 20-page request has no band tag.
 selected=[];used={r['id']:set() for r in order};counts={r['id']:0 for r in order};bands=0
 if name=='anemi':
  # The A0 verified body leaf can itself be one of the 20 sampled leaves.
  # Reuse its raster: this preserves the 50-request source cap.
  for r in order:
   vv=next((x for x in results if x['item']==r['id'] and x['pass']),None)
   candidates=[BASE/'receipts/verify-pages'/(vv['page_id']+'.json')] if vv else list((BASE/'receipts/verify-pages').glob('anemi--*.json'))
   for path in candidates:
    if not path.exists():continue
    p=json.loads(path.read_text())
    if p['item']!=r['id']:continue
    p.update(verification_only=False,reused_A0_body_leaf=True);selected.append(p);used[r['id']].add(p['page']);counts[r['id']]+=1;write(BASE/'receipts/pages'/(p['id']+'.json'),p);break
 for r in order:
  if len(selected)>=target:break
  total=r.get('page_count') or 0
  if total<=0:continue
  want_band=name!='anemi' and bands<6
  positions=page_positions(total,2 if want_band else 1,want_band,r['id']+':sample-initial')
  positions=[p for p in positions if p[0] not in used[r['id']]]
  if not positions:continue
  try:pp=source.get_pages(r,positions=positions)
  except Exception as e:append(BASE/'receipts/sample-errors.jsonl',dict(source=name,item=r['id'],error=type(e).__name__,reason=str(e)[:250]));continue
  for p in pp:
   if len(selected)>=target:break
   selected.append(p);used[r['id']].add(p['page']);counts[r['id']]+=1;bands+=p['role']=='band'
 while len(selected)<target:
  progress=False
  for r in order:
   if counts[r['id']]>=8 or len(selected)>=target:continue
   avail=[p for p in page_positions(r.get('page_count') or 0,100,False,r['id']+':remaining') if p[0] not in used[r['id']]]
   if not avail:continue
   pos=rng(r['id']+str(counts[r['id']])).choice(avail)
   try:pp=source.get_pages(r,positions=[pos])
   except Exception:continue
   selected+=pp;counts[r['id']]+=len(pp);used[r['id']].update(p['page'] for p in pp);progress=bool(pp) or progress
  if not progress:break
 # PDF galley refetches do not add items to the uniform draw or overwrite N.
 jsonl(BASE/f'pages_{name}.jsonl',selected)
 write(BASE/'receipts'/f'sampling-{name}.json',dict(source=name,target=target,sampled=len(selected),items=len({p['item'] for p in selected}),max_pages_per_item=max(counts.values(),default=0),band_pages=sum(p['role']=='band' for p in selected),source_item_scope='catalogue issue; media galley for OJS; book/volume otherwise',at=stamp()))
 print('SAMPLED',name,len(selected),'items',len({p['item'] for p in selected}),'bands',bands,flush=True)

if __name__=='__main__':
 names=sys.argv[1:]
 def wrapper(n):
  try:run(n);return n,'ok'
  except Exception as e:
   import traceback;traceback.print_exc();write(BASE/'receipts'/f'sample-error-{n}.json',dict(source=n,error=type(e).__name__,message=str(e)[:500]));return n,type(e).__name__
 with ThreadPoolExecutor(max_workers=len(names)) as pool:
  for f in as_completed([pool.submit(wrapper,n) for n in names]):print('DONE',f.result(),flush=True)

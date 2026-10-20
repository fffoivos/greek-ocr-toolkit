"""F2-GR custody, catalogue transport, deterministic sampling and raster limits."""
from __future__ import annotations
import pathlib,sys,json,hashlib,random,math,re,io,contextlib,subprocess,threading,time
import numpy as np
from PIL import Image
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlsplit,urlencode,parse_qs
ROOT=pathlib.Path(__file__).resolve().parents[4]
BASE=pathlib.Path(__file__).resolve().parent
F1=ROOT/'docs/harvest/funnel_v1/gr'
P1_ORIGINAL=ROOT.parent/'greek-ocr-toolkit-sol-inventory/docs/harvest/pilots_v2'
P1=BASE/'reference/p1'
sys.path.insert(0,str(F1));sys.path.insert(0,str(ROOT))
import funnellib as f1
f1.BASE=BASE
HTTP=f1.HTTP;write=f1.write;append=f1.append;rows=f1.rows;stamp=f1.stamp;physical=f1.physical
SEED=2026101602
PDF_LOCK=threading.Lock()
def sha(p):
 p=pathlib.Path(p)
 if not p.exists() and p.with_suffix(p.suffix+'.gz').exists():
  import gzip
  return hashlib.sha256(gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes())).hexdigest()
 return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(path):
 p=pathlib.Path(path)
 if p.exists():return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
 compressed=p.with_suffix(p.suffix+'.gz')
 if compressed.exists():
  import gzip
  with gzip.open(compressed,'rt',encoding='utf8') as stream:return [json.loads(line) for line in stream if line.strip()]
 return []
def digest(b):return hashlib.sha256(b).hexdigest()
def jsonl(p,rr):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in rr))
def rng(name):return random.Random(str(SEED)+':'+name)
def soup(c,u,**kw):
 r,b=c.get(u,**kw);return BeautifulSoup(b,'html.parser'),r,b
def install_anemi_limiter(a):
 """One cross-process host guard for authenticated catalogue and viewer calls."""
 import fcntl
 original=a.AnemiHTTP._raw
 def raw(self,*args,**kwargs):
  lock=BASE/'bulk/anemi-host.lock';state=BASE/'bulk/anemi-host.json'
  with lock.open('a') as stream:
   fcntl.flock(stream,fcntl.LOCK_EX)
   previous=json.loads(state.read_text()).get('completed',0) if state.exists() else 0
   time.sleep(max(0,previous+2.1-time.time()))
   try:return original(self,*args,**kwargs)
   finally:write(state,dict(completed=time.time()))
 a.AnemiHTTP._raw=raw
def year(text):
 m=re.search(r'(?<!\d)(1[5-9]\d\d|20[0-2]\d)(?!\d)',str(text or ''));return int(m[1]) if m else None
def plain(v):
 if isinstance(v,list):return ' '.join(plain(x) for x in v)
 if isinstance(v,dict):return str(v.get('value',v.get('@value','')))
 return str(v or '')
def period(y):return 'poly1850' if y and 1850<=y<=1890 else 'poly1891_1899_aux' if y and 1891<=y<=1899 else 'poly1900' if y and 1900<=y<=1982 else 'modern' if y and y>=1983 else 'pre1850' if y and y<1850 else 'unknown'
def wilson(k,n):
 if not n:return [0.,1.]
 z=1.959963984540054;a=(k/n+z*z/(2*n))/(1+z*z/n);b=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/(1+z*z/n);return [a-b,a+b]
def overlap_sets():
 import curate
 old=curate.BASE;curate.BASE=BASE
 try:
  values=curate.overlap();ids,testids,urls,testurls,titles,testtitles=values
  from greekocr.harvest.openarchives import canonical_url
  for name in ['selection.json','holdout_books.json','books.json']:
   path=f1.MAIN/'docs/harvest/round1'/name
   if not path.exists():continue
   obj=json.loads(path.read_text());items=obj if isinstance(obj,list) else obj.get('books',[])
   for r in items:
    cat=r.get('catalogue') or {};held='holdout' in name or r.get('split') in ['test','reserved']
    for ident in [cat.get('record_id'),*(cat.get('viewer_rec_ids') or [])]:
     if ident:
      ids.add(ident)
      if held:testids.add(ident)
    for v in cat.get('volumes',[]):
     for key in ['source_pdf_url','viewer_url']:
      if v.get(key):
       urls.add(canonical_url(v[key]))
       if held:testurls.add(canonical_url(v[key]))
  return values
 finally:curate.BASE=old
OVERLAP=None
PRIOR={}
def excluded(r):
 global OVERLAP
 if OVERLAP is None:OVERLAP=overlap_sets()
 from greekocr.harvest.openarchives import canonical_url
 import curate
 ids,testids,urls,testurls,titles,testtitles=OVERLAP
 ident=str(r['id']);title=curate.norm(r.get('title'));u=canonical_url(r.get('catalogue_url') or r.get('url') or '');media=canonical_url(r.get('url') or '')
 hit=ident in ids or u in urls or media in urls or (len(title)>12 and title in titles)
 held=ident in testids or u in testurls or media in testurls or (len(title)>12 and title in testtitles)
 # Apply F1's already-established exact overlap exclusions as well.
 if r['source'] not in PRIOR:PRIOR[r['source']]={x['id']:x for x in rows(F1/f"candidates_{r['source']}.jsonl")}
 prior=PRIOR[r['source']].get(ident,{})
 held=held or prior.get('held_out_test',False);hit=hit or prior.get('overlap_flag')=='collected'
 r['overlap_screen']=dict(collected=bool(hit),held_out=bool(held),method='F1 exact ID/URL/normalized-title inputs; semantic cross-edition identity unresolved')
 return hit or held
def population(source,records,complete,method,**extra):
 unique={str(r['id']):dict(r,source=source) for r in records};kept=[];out=[]
 for r in sorted(unique.values(),key=lambda x:str(x['id'])):
  (out if excluded(r) else kept).append(r)
 jsonl(BASE/f'population_{source}.jsonl',kept);jsonl(BASE/'receipts'/f'overlap-excluded-{source}.jsonl',out)
 info=dict(source=source,N=len(kept),population_complete=complete,population_kind='complete enumerated catalogue frame' if complete else 'documented enumerated lower-bound frame',method=method,seed=SEED,random_algorithm='Python random.Random(str(seed)+":"+source).sample(sorted(frame,id), min(20,N)); no replacement',excluded_overlap=len(out),metadata_only=True,at=stamp(),**extra)
 write(BASE/'receipts'/f'census-{source}.json',info)
 selected=rng(source).sample(kept,min(20,len(kept)))
 jsonl(BASE/f'draw_{source}.jsonl',selected)
 print('CENSUS',source,len(kept),'complete',complete,'draw',len(selected),flush=True)
 return selected
def osd(im):
 b=io.BytesIO();small=im.copy();small.thumbnail((1600,1600));small.save(b,format='PNG')
 try:
  p=subprocess.run(['tesseract','stdin','stdout','--psm','0'],input=b.getvalue(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15,env={**__import__('os').environ,'OMP_THREAD_LIMIT':'1'})
  t=p.stdout.decode();s=re.search(r'Script: (.+)',t);conf=re.search(r'Script confidence: ([\d.]+)',t);angle=re.search(r'Orientation in degrees: (\d+)',t)
  return dict(script=s[1].strip() if s else 'unresolved',confidence=float(conf[1]) if conf else None,orientation=int(angle[1]) if angle else None,status=p.returncode)
 except subprocess.TimeoutExpired:return dict(script='unresolved',confidence=None,orientation=None,status='timeout')
def raster(im,r,n,role,fetch,phys=None,total=None,verify=False):
 im=im.convert('L');native=list(im.size);cap=1600 if verify else 3500;im.thumbnail((cap,cap),Image.Resampling.LANCZOS)
 ident=r['source']+'--'+re.sub('[^a-zA-Z0-9_.-]','_',str(r['id']))[:60]+'-'+digest(str(r['id']).encode())[:8]+f'--{n:06d}'
 folder='verify' if verify else 'pages';p=BASE/'bulk'/folder/(ident+'.jpg');p.parent.mkdir(parents=True,exist_ok=True);im.save(p,quality=92,optimize=True)
 view=BASE/'bulk/review'/(ident+'.jpg');view.parent.mkdir(parents=True,exist_ok=True);small=im.copy();small.thumbnail((1600,1600),Image.Resampling.LANCZOS);small.save(view,quality=86,optimize=True)
 a=np.asarray(im);ink=float(np.mean(a<180));o=osd(im)
 classification=(phys or {}).get('classification','raster_scan_candidate')
 reasons=[]
 if classification=='born_digital_text':reasons.append('born_digital')
 if classification not in ['raster_scan_candidate'] and not classification.startswith('scanned_'):reasons.append('scan_construction_unresolved')
 if ink<.0015:reasons.append('blank')
 # OSD commonly calls Greek caps Cyrillic/Latin. Those remain explicit suspicions,
 # with Greek catalogue evidence and later native review, not forced non-Greek truth.
 out=dict(id=ident,pilot=r['source'],source=r['source'],item=str(r['id']),title=r.get('title'),year=r.get('year'),period=period(r.get('year')),page=n,role=role,url=r.get('url'),catalogue_url=r.get('catalogue_url'),image=str(p.relative_to(BASE)),image_sha256=sha(p),review_image=str(view.relative_to(BASE)),review_sha256=sha(view),width=im.width,height=im.height,native_size=native,long_side_cap=3500,pdf_dpi_cap=200,fetch_sha256=fetch['sha256'],page_count=total,physical=phys or dict(classification=classification,evidence='Published image endpoint; scanned-print status requires native review'),machine=dict(ink_fraction=ink,dominant_script=o['script'],script_detector=o,blank_suspicion=ink<.0015,plate_suspicion=None,cover_suspicion=role!='body',handwriting_suspicion='unresolved; native review required',skew_degrees=None,median_text_line_px=None),machine_pass=not reasons,excluded_reasons=reasons,verification_only=verify,at=stamp())
 write(BASE/'receipts'/('verify-pages' if verify else 'pages')/(ident+'.json'),out)
 return out
def page_positions(total,n,band=False,name=''):
 rr=rng(name);body=[i for i in range(1,total+1) if .10<=(i-.5)/max(1,total)<=.90];edge=[i for i in range(1,total+1) if (i-1)/max(1,total-1)<=.08 or (i-1)/max(1,total-1)>=.95]
 chosen=[]
 if band and edge:chosen=[(rr.choice(edge),'band')]
 available=[i for i in body if i not in {x[0] for x in chosen}]
 chosen += [(i,'body') for i in rr.sample(available,min(n-len(chosen),len(available)))]
 return sorted(chosen)
def fetch_pdf(c,r,positions=None,verify=False,n=1,band=False):
 rec,b=c.get(r['url'],'pdf',160_000_000)
 if not b.startswith(b'%PDF'):raise ValueError('offered response is not PDF')
 import pypdfium2 as pdfium
 out=[]
 # PDFium is not thread-safe. Network hosts remain parallel.
 with PDF_LOCK:
  with pdfium.PdfDocument(b) as doc:
   total=len(doc);r['page_count']=total
   pp=positions or page_positions(total,n,band,str(r['id'])+(':verify' if verify else ':sample'))
   for i,role in pp:
    with contextlib.closing(doc[i-1]) as page:
     phys=physical(page);w,h=page.get_size();scale=min(200/72,3500/max(w,h))
     with contextlib.closing(page.render(scale=scale,grayscale=True)) as bm:im=bm.to_pil().copy()
    out.append((im,i,role,phys))
 # OCR script diagnostics run outside the PDFium lock.
 return [raster(im,r,r.get('_source_page',i),role,rec,phys,r.get('_total_pages',total),verify) for im,i,role,phys in out]

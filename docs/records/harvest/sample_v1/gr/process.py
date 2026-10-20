"""P1-identical provider/admission/geometry, with F2 paths and strict USD 1 cap."""
from f2lib import *
import fcntl,importlib.util,statistics,shutil
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor,as_completed
import greekocr
greekocr.__path__.append(str(BASE/'reference/greekocr'))
sys.path.insert(0,str(P1))
sys.path.insert(0,str(BASE))
# Load the exact P1 routines; only output/source roots are rebound.
import pilotlib,prepare_detector,process_reads,read_pilots
pilotlib.BASE=BASE;pilotlib.ROOT=ROOT
prepare_detector.BASE=BASE;prepare_detector.ROOT=ROOT
process_reads.BASE=BASE;process_reads.ROOT=ROOT
process_reads.THRESHOLDS=BASE/'reference/greekocr/labelfix/geometry/thresholds.json'
from greekocr.labelfix.geometry.io import cache_page

def machine(p):
 dest=BASE/'receipts/machine'/(p['id']+'.json')
 if dest.exists():return json.loads(dest.read_text())
 try:
  data,ink,labels,rec=cache_page(BASE/p['image'],BASE/'cache/g1b'/p['id'],p['image_sha256'],prepare_detector.detector_identity())
  rr=data['rows'];heights=[statistics.median(np.array(r['bottom'])-np.array(r['top'])) for r in rr if r['x1']-r['x0']>=50]
  slopes=[math.degrees(math.atan(float(np.polyfit(np.arange(len(r['baseline'])),r['baseline'],1)[0]))) for r in rr if len(r['baseline'])>=100]
  median=float(statistics.median(heights)) if heights else None;skew=float(statistics.median(slopes)) if slopes else None
  p['machine'].update(median_text_line_px=median,median_xheight_px=float(statistics.median(r['xheight'] for r in rr)) if rr else None,skew_degrees=skew,detector_rows=len(rr),plate_suspicion=len(rr)<3,detector_seconds=rec['detector_s'],detector_code_sha256=prepare_detector.detector_identity())
  if not rr:p['excluded_reasons'].append('no_detector_text_rows')
  if median is not None and median<10:p['excluded_reasons'].append('median_text_line_below_10px')
  if skew is not None and abs(skew)>12:p['excluded_reasons'].append('severe_skew')
  p['machine_pass']=not p['excluded_reasons']
 except Exception as e:
  p['machine'].update(detector_error=type(e).__name__);p['excluded_reasons'].append('page_detector_failed');p['machine_pass']=False
 write(dest,p);return p

class F2Budget(read_pilots.P1Budget):
 def __init__(self):
  self.path=BASE/'google/ledger.jsonl';self.cap=1.;self.max_calls=666;self.path.parent.mkdir(parents=True,exist_ok=True)
 def reserve(self,engine,key):
  if engine!='docai':raise ValueError('only Document AI authorised')
  with self.path.with_suffix('.lock').open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX);rr=rows(self.path)
   if any(r['key']==key for r in rr):raise ValueError('already reserved; no retry')
   if sum(r['micro_usd'] for r in rr)+1500>1_000_000:raise ValueError('F2-GR USD 1 hard cap')
   with self.path.open('a') as stream:
    stream.write(json.dumps(dict(engine=engine,key=key,micro_usd=1500,time=time.time(),state='reserved',track='F2-GR'))+'\n');stream.flush();os.fsync(stream.fileno())
   return len(rr)+1

class F2Reader(read_pilots.P1Readers):
 def __init__(self):
  import threading
  from greekocr.readers.services.google_docai import DocAIReader,DEFAULT_VERSION
  self.root=BASE/'google';self.root.mkdir(parents=True,exist_ok=True);self.budget=F2Budget()
  self.docai=DocAIReader('ocr-ground-truth-20261008','eu','9a98b7aca3c19561',version=DEFAULT_VERSION,language_hints=(),receipts_dir=self.root/'docai')
  self.rate_lock=threading.Lock();self.last_docai=0.

def stripped_transport(url,**kwargs):
 """Discard provider-embedded page bitmaps before the reader can save a response."""
 import requests
 response=requests.post(url,**kwargs)
 if response.ok:
  raw=response.json();removed=[]
  for i,p in enumerate(raw.get('document',{}).get('pages',[])):
   if 'image' in p:removed.append(dict(page=i+1,bytes_base64=len(p['image'].get('content',''))));p.pop('image',None)
  raw.get('document',{}).pop('content',None)
  response._content=json.dumps(raw,ensure_ascii=False).encode('utf8')
 return response

def read_one(reader,p):
 assert sha(BASE/p['image'])==p['image_sha256']
 r=reader.call('docai',BASE/p['image'])
 write(BASE/'receipts/reads'/(p['id']+'.json'),dict(page_id=p['id'],source=p['source'],image_sha256=p['image_sha256'],status=r['status'],result='google/parsed/docai/'+p['image_sha256']+'.json',error_class=r.get('error_class')))
 return p['id'],r['status']

def analyse_one(p):
 result=process_reads.one(p)
 lp=BASE/'bulk/lines'/(p['id']+'.jsonl')
 removed=0
 for r in rows(lp):
  crop=BASE/r['crop_path']
  if crop.parent in [BASE/'bulk/crops',BASE/'bulk/heading_crops'] and crop.exists():
   assert sha(crop)==r['crop_sha256'];crop.unlink();removed+=1
 if removed:write(BASE/'receipts/ephemeral-crops'/(p['id']+'.json'),dict(page_id=p['id'],derived_crops_removed=removed,scope='only output bulk/crops and bulk/heading_crops',reconstruction='exact original page raster + recorded crop_bbox, PNG compress_level=3; selected native label cards are reconstructed and hash-checked'))
 return result

if __name__=='__main__':
 import os
 names=sys.argv[2:];stage=sys.argv[1]
 pages=[p for name in names for p in rows(BASE/f'pages_{name}.jsonl')]
 if stage=='machine':
  with ProcessPoolExecutor(max_workers=3) as pool:
   for f in as_completed([pool.submit(machine,p) for p in pages]):
    r=f.result();print('MACHINE',r['id'],r['machine_pass'],r['excluded_reasons'],flush=True)
 elif stage=='read':
  pages=[json.loads((BASE/'receipts/machine'/(p['id']+'.json')).read_text()) for p in pages if (BASE/'receipts/machine'/(p['id']+'.json')).exists()]
  pages=[p for p in pages if p['machine_pass']]
  reader=F2Reader();reader.docai._transport=stripped_transport;write(BASE/'receipts/processor-binding.json',reader.docai.binding())
  with ThreadPoolExecutor(max_workers=3) as pool:
   for f in as_completed([pool.submit(read_one,reader,p) for p in pages]):print('READ',*f.result(),flush=True)
  write(BASE/'receipts/cost.json',reader.budget.receipt())
 elif stage=='analyse':
  with ProcessPoolExecutor(max_workers=2) as pool:
   for f in as_completed([pool.submit(analyse_one,p) for p in pages]):print('ANALYSE',*f.result(),flush=True)

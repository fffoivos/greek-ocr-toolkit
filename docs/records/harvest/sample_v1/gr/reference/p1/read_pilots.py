"""Explicit P1 reads only; durable integer reservations precede every request."""
from __future__ import annotations
import argparse,fcntl,hashlib,json,os,sys,threading,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pilotlib import *
sys.path.insert(0,str(ROOT))
from greekocr.harvest.readers import Readers,BudgetExceeded
from greekocr.readers.services.google_docai import DocAIReader,DEFAULT_VERSION

class P1Budget:
    def __init__(self,path,cap=5):
        self.path=pathlib.Path(path);self.cap=cap;self.max_calls=3333
        if not 0<cap<=5:raise ValueError('P1 hard cap is USD 5')
        self.path.parent.mkdir(parents=True,exist_ok=True)
    def reserve(self,engine,key):
        if engine!='docai':raise ValueError('only Document AI authorised')
        with self.path.with_suffix('.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            ledger=rows(self.path)
            if any(r['key']==key and r['engine']==engine for r in ledger):raise ValueError('already reserved; no automatic retry')
            spent=sum(int(r['micro_usd']) for r in ledger)
            if spent+1500>round(self.cap*1_000_000):raise BudgetExceeded('USD 5 cumulative P1 stop')
            with self.path.open('a') as stream:
                stream.write(json.dumps(dict(engine=engine,key=key,micro_usd=1500,time=time.time(),state='reserved',pilot='P1'))+'\n')
                stream.flush();os.fsync(stream.fileno())
            return len(ledger)+1
    def receipt(self):
        r=rows(self.path)
        return dict(calls_reserved=len(r),micro_usd_reserved=sum(x['micro_usd'] for x in r),cost_usd=sum(x['micro_usd'] for x in r)/1e6,cap_usd=self.cap,policy='all P1 attempts reserved at list price, including failures; no free-tier subtraction; not an invoice')

class P1Readers(Readers):
    def __init__(self):
        self.root=BASE/'google';self.root.mkdir(parents=True,exist_ok=True)
        self.budget=P1Budget(self.root/'budget.jsonl',5)
        self.docai=DocAIReader('ocr-ground-truth-20261008','eu','9a98b7aca3c19561',version=DEFAULT_VERSION,language_hints=(),receipts_dir=self.root/'docai')
        self.rate_lock=threading.Lock();self.last_docai=0.
    def call(self,engine,image):
        if engine!='docai':raise ValueError('P1 is Document AI only')
        return super().call(engine,image)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');parser.add_argument('--pilot');args=parser.parse_args()
    pages=[json.loads(p.read_text()) for p in sorted((BASE/'receipts/pages').glob('*.json'))]
    pages=[p for p in pages if not p.get('excluded') and p.get('google_read') is not False and p['pilot']!='ajax' and (args.pilot is None or p['pilot']==args.pilot)]
    if not args.run:
        print(json.dumps(dict(pages=len(pages),max_read_cost_usd=.0015*len(pages),status='preflight; no ADC or reader calls')));sys.exit()
    auth=json.loads((BASE/'receipts/authorization.json').read_text())
    if auth.get('ledger_status')!='resolved':raise RuntimeError('exact ledger scope remains pending user clarification; no paid read')
    if auth['ledger_path']!='google/budget.jsonl':raise ValueError('ledger path differs from reviewed P1 runner')
    reader=P1Readers();write(BASE/'receipts/processor-binding.json',reader.docai.binding())
    def one(p):
        assert sha(BASE/p['image'])==p['image_sha256']
        r=reader.call('docai',BASE/p['image'])
        write(BASE/'receipts/reads'/(p['id']+'.json'),dict(page_id=p['id'],pilot=p['pilot'],image_sha256=p['image_sha256'],status=r['status'],result='google/parsed/docai/'+p['image_sha256']+'.json',error_class=r.get('error_class')))
        return p['id'],r['status']
    with ThreadPoolExecutor(max_workers=3) as pool:
        for f in as_completed([pool.submit(one,p) for p in pages]):print(*f.result(),flush=True)
    write(BASE/'receipts/cost.json',reader.budget.receipt())

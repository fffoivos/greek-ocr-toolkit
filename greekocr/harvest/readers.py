"""Budget-reserved single-crop Google calls; no implicit retries."""
from __future__ import annotations
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import dataclasses, fcntl, json, hashlib, time, threading
from PIL import Image
from .core import list_return, normalise
from greekocr.readers.services.google_vision import VisionReader, _piece
from greekocr.readers.services.google_docai import DocAIReader, DEFAULT_VERSION

PRICE = .0015

def read_jsonl(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()] if Path(path).exists() else []

def atomic(path, value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp'); tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)); tmp.replace(path)

class BudgetExceeded(RuntimeError): pass

class Budget:
    """Reserve integer microdollars before network I/O, under a cross-process lock.

    Failed/ambiguous requests remain reserved. Cache re-use is free; reservations
    survive interruption. No monthly free allowance is deducted from list price.
    """
    def __init__(self, path, cap=3, max_calls=1000):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        if not 0<float(cap)<=3: raise ValueError('cap must be <=3 USD')
        self.cap=float(cap)
        self.max_calls=min(1000,int(max_calls))
        self.state=self.path.with_suffix('.state.json')
        if not self.state.exists(): atomic(self.state,{'calls':len(read_jsonl(self.path))})
    def reserve(self, engine, key):
        with self.path.with_suffix('.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            calls=json.loads(self.state.read_text())['calls']
            if calls>=self.max_calls or (calls+1)*1500>round(self.cap*1_000_000): raise BudgetExceeded('cost/call cap reached')
            atomic(self.state,{'calls':calls+1})
            row=dict(engine=engine,key=key,micro_usd=1500,time=time.time(),state='reserved')
            with self.path.open('a') as f: f.write(json.dumps(row)+'\n'); f.flush()
            return calls+1
    def receipt(self):
        rows=read_jsonl(self.path)
        calls=max(len(rows),json.loads(self.state.read_text())['calls'])
        return dict(calls_reserved=calls,calls_by_engine={k:sum(r['engine']==k for r in rows) for k in ('vision','docai')},
                    cost_usd=calls*PRICE,cap_usd=self.cap,max_calls=self.max_calls,policy='all attempts reserved at list price; no free-tier deduction',
                    prices={'vision':PRICE,'docai':PRICE},
                    pricing_sources=['https://cloud.google.com/vision/pricing','https://cloud.google.com/products/document-ai/pricing'])

def polygon_box(poly, size):
    vertices=poly.get('vertices')
    if not vertices: vertices=[dict(x=v.get('x',0)*size[0],y=v.get('y',0)*size[1]) for v in poly.get('normalizedVertices',[])]
    if not vertices: return None
    return [min(v.get('x',0) for v in vertices),min(v.get('y',0) for v in vertices),max(v.get('x',0) for v in vertices),max(v.get('y',0) for v in vertices)]

def union(boxes):
    return [min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)]

def response_pieces(engine, raw, size):
    result=[]
    if engine=='docai':
        doc=raw['document']; text=doc.get('text','')
        for p in doc.get('pages',[]):
            for line in p.get('lines',[]):
                layout=line.get('layout',{}); box=polygon_box(layout.get('boundingPoly',{}),size)
                t=''.join(text[int(s.get('startIndex',0)):int(s['endIndex'])] for s in layout.get('textAnchor',{}).get('textSegments',[]))
                if box: result.append(dict(text=t,bbox=box,confidence=layout.get('confidence')))
    else:
        annotation=raw.get('responses',[{}])[0].get('fullTextAnnotation',{})
        for p in annotation.get('pages',[]):
            for block in p.get('blocks',[]):
                for para in block.get('paragraphs',[]):
                    chars=[]; boxes=[]
                    for word in para.get('words',[]):
                        for symbol in word.get('symbols',[]):
                            chars.append(_piece(symbol)); b=polygon_box(symbol.get('boundingBox',{}),size)
                            if b: boxes.append(b)
                            br=symbol.get('property',{}).get('detectedBreak',{}).get('type')
                            if br in ('LINE_BREAK','EOL_SURE_SPACE','HYPHEN'):
                                if boxes: result.append(dict(text=''.join(chars).strip(),bbox=union(boxes),confidence=para.get('confidence')))
                                chars=[];boxes=[]
                    if boxes: result.append(dict(text=''.join(chars).strip(),bbox=union(boxes),confidence=para.get('confidence')))
    return result

def montage(records, path, *, separator=24):
    if not 1<=len(records)<=20: raise ValueError('montage requires 1..20 crops')
    images=[]
    for r in records:
        with Image.open(r['straight_crop']) as im: images.append(im.convert('L'))
    width=max(im.width for im in images); height=sum(im.height for im in images)+separator*(len(images)+1)
    out=Image.new('L',(width+48,height),255); mapping=[]; y=separator
    for r,im in zip(records,images):
        out.paste(im,(24,y)); mapping.append(dict(id=r['id'],bbox=[24,y,24+im.width,y+im.height],crop=r['straight_crop']))
        y+=im.height+separator
    out.save(path); atomic(Path(path).with_suffix('.map.json'),mapping)
    return mapping

def split_montage(pieces, mapping, *, column_context=None):
    groups={m['id']:[] for m in mapping}; errors={m['id']:[] for m in mapping}
    for p in pieces:
        b=p['bbox']; area=max(1,(b[2]-b[0])*(b[3]-b[1])); overlaps=[]
        for m in mapping:
            a=m['bbox']; inter=max(0,min(b[2],a[2])-max(b[0],a[0]))*max(0,min(b[3],a[3])-max(b[1],a[1]))
            if inter: overlaps.append((inter/area,m))
        if not overlaps: continue
        fraction,m=max(overlaps,key=lambda q:q[0]); a=m['bbox']
        if fraction<.6 or sum(f>.15 for f,_ in overlaps)>1:
            for _,hit in overlaps: errors[hit['id']].append('montage_cross_crop_box')
            continue
        groups[m['id']].append(dict(p,bbox=[b[0]-a[0],b[1]-a[1],b[2]-a[0],b[3]-a[1]]))
    results={}
    for ident,group in groups.items():
        result=list_return(group,**(column_context or {}).get(ident,{}))
        if errors[ident]: result.update(rejected=True,text='',flags=result['flags']+errors[ident])
        results[ident]=result
    return results

class Readers:
    def __init__(self, root, cap=3, project='ocr-ground-truth-20261008', processor='9a98b7aca3c19561'):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True); self.budget=Budget(self.root/'budget.jsonl',cap)
        self.vision=VisionReader(project,responses_dir=self.root/'vision/responses')
        self.rate_lock=threading.Lock(); self.last_docai=0.0
        self.docai=DocAIReader(project,'eu',processor,version=DEFAULT_VERSION,receipts_dir=self.root/'docai')
    def call(self, engine, image):
        data=Path(image).read_bytes(); key=hashlib.sha256(data).hexdigest()
        result_path=self.root/'parsed'/engine/(key+'.json')
        result_path.parent.mkdir(parents=True,exist_ok=True)
        with result_path.with_suffix('.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            return self._call_locked(engine,image,key,result_path)
    def _call_locked(self, engine, image, key, result_path):
        if result_path.exists(): return json.loads(result_path.read_text())
        if any(r['engine']==engine and r['key']==key for r in read_jsonl(self.budget.path)):
            result=dict(engine=engine,pieces=[],raw_text='',mean_confidence=None,min_confidence=None,
                        elapsed_s=0.,status='error',error_class='InterruptedReservedAttempt',image_sha256=key)
            atomic(result_path,result)
            return result
        self.budget.reserve(engine,key)
        if engine=='docai':
            with self.rate_lock:
                time.sleep(max(0,.55-(time.monotonic()-self.last_docai)))
                self.last_docai=time.monotonic()
        start=time.perf_counter()
        try:
            reading=self.vision.read_annotation(image) if engine=='vision' else self.docai.read(image)
            raw=json.loads(Path(reading.raw_json_path).read_text())
            with Image.open(image) as im: pieces=response_pieces(engine,raw,im.size)
            result=dict(engine=engine,pieces=pieces,raw_text=getattr(reading,'raw_text',reading.text),
                        mean_confidence=reading.mean_symbol_conf,min_confidence=reading.min_symbol_conf,
                        receipt_id=reading.receipt_id,raw_json_path=reading.raw_json_path,
                        latency_s=reading.latency_s,elapsed_s=time.perf_counter()-start,binding=getattr(self,engine).binding(),
                        image_sha256=key,status='ok')
        except Exception as e:
            # Do not write credential-bearing exception payloads.
            result=dict(engine=engine,pieces=[],raw_text='',mean_confidence=None,min_confidence=None,
                        elapsed_s=time.perf_counter()-start,status='error',error_class=type(e).__name__,image_sha256=key)
        atomic(result_path,result); return result
    def pair(self,image):
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures={e:pool.submit(self.call,e,image) for e in ('vision','docai')}
            return {e:f.result() for e,f in futures.items()}
    def single(self,r):
        pair=self.pair(r['straight_crop'])
        context=dict(column_bands=r['gates'].get('column_bands'),
                     x_offset=(r.get('straighten') or {}).get('page_x_offset',r['bbox'][0])) if 'gates' in r else {}
        return {e:dict(v,**list_return(v['pieces'],**context)) for e,v in pair.items()}
    def batch(self,records):
        identity=hashlib.sha256('|'.join(r['id'] for r in records).encode()).hexdigest()[:24]
        path=self.root/'montages'/(identity+'.png'); path.parent.mkdir(parents=True,exist_ok=True)
        mapping=montage(records,path); pair=self.pair(path); result={r['id']:{} for r in records}
        for e,v in pair.items():
            context={r['id']:dict(column_bands=r['gates'].get('column_bands'),
                x_offset=(r.get('straighten') or {}).get('page_x_offset',r['bbox'][0])) for r in records if 'gates' in r}
            for ident,parsed in split_montage(v['pieces'],mapping,column_context=context).items():
                confidences=[p['confidence'] for p in parsed['pieces'] if p.get('confidence') is not None]
                result[ident][e]=dict(v,**parsed,raw_text='\n'.join(p['text'] for p in parsed['pieces']),
                                     mean_confidence=sum(confidences)/len(confidences) if confidences else None,
                                     confidence_scope='montage line boxes; paragraph/line confidence',
                                     montage=str(path),montage_crop_count=len(records),box_map=str(path.with_suffix('.map.json')))
        return result
    def qualify(self,records):
        if len(records)!=50: raise ValueError('qualification requires exactly 50 crops')
        singles={r['id']:self.single(r) for r in records}; batched={}
        for i in range(0,50,20): batched.update(self.batch(records[i:i+20]))
        comparisons=[]
        for r in records:
            for e in ('vision','docai'):
                a,b=singles[r['id']][e],batched[r['id']][e]
                equal=normalise(a['text'])==normalise(b['text']) and a['rejected']==b['rejected'] and a['status']==b['status']=='ok'
                comparisons.append(dict(id=r['id'],engine=e,equal=equal,single=a['text'],montage=b['text'],single_flags=a['flags'],montage_flags=b['flags']))
        receipt=dict(crops=50,comparisons=comparisons,matched=sum(x['equal'] for x in comparisons),required=100,
                     qualified=all(x['equal'] for x in comparisons),rule='all 50 crops match both readers, NFD/whitespace and rejection state',separator_px=24,max_crops=20)
        atomic(self.root/'montage_qualification.json',receipt); return receipt,singles

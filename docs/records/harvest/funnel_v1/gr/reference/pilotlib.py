"""P1 bounded acquisition utilities; unchanged O4c robots/rate transport."""
from __future__ import annotations
import hashlib, importlib.util, io, json, pathlib, time
from urllib.parse import quote
from PIL import Image

BASE=pathlib.Path(__file__).resolve().parent
ROOT=BASE.parents[2]
MAIN=ROOT.parent/'greek-ocr-toolkit'
S1=ROOT/'docs/harvest/inventory_v2'
LONG_SIDE=3500
spec=importlib.util.spec_from_file_location('p1_o4c',ROOT/'greekocr/_vendor/scripts/fetch/o4c_common.py')
o4c=importlib.util.module_from_spec(spec);spec.loader.exec_module(o4c)

def sha(path):
    with pathlib.Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def write(path,obj):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n');tmp.replace(path)

def append(path,obj):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a') as f:f.write(json.dumps(obj,ensure_ascii=False,allow_nan=False)+'\n');f.flush()

def rows(path):
    p=pathlib.Path(path)
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []

def client(source):return o4c.HTTP(source,root=BASE/'bulk/http'/source,interval=1.,budget=2_000_000_000)

def fetch(c,url,path,limit=16_000_000):
    path=pathlib.Path(path);receipt=BASE/'receipts/fetch'/(hashlib.sha256(url.encode()).hexdigest()+'.json')
    if path.exists() and receipt.exists():
        r=json.loads(receipt.read_text());assert r['sha256']==sha(path);return path
    try:
        meta,data=c.get(quote(url,safe=":/?&=%|+,;@!$'()*[]"),limit=limit)
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        write(receipt,dict(url=url,path=str(path.relative_to(BASE)),sha256=sha(path),bytes=len(data),status='ok',http_status=meta['status'],fetched_at=meta['fetched_at']))
        return path
    except Exception as e:
        write(receipt,dict(url=url,status='error',error=str(e),time=time.time()))
        raise

def raster(source,item,n,url,c,role='body'):
    ident=f'{source}--{item}--{n:06d}'
    manifest=BASE/'receipts/pages'/(ident+'.json')
    if manifest.exists():return json.loads(manifest.read_text())
    original=fetch(c,url,BASE/'bulk/originals'/source/item/(f'{n:06d}.jpg'),32_000_000)
    with Image.open(original) as im:
        im.load();native=list(im.size);im=im.convert('L');im.thumbnail((LONG_SIDE,LONG_SIDE),Image.Resampling.LANCZOS)
        path=BASE/'bulk/pages'/(ident+'.png');path.parent.mkdir(parents=True,exist_ok=True);im.save(path,compress_level=3)
        result=dict(id=ident,pilot=source,item=item,page=n,role=role,url=url,image=str(path.relative_to(BASE)),image_sha256=sha(path),width=im.width,height=im.height,native_size=native,original=str(original.relative_to(BASE)),original_sha256=sha(original),long_side_cap=LONG_SIDE)
    write(manifest,result);return result

def positions(total,count):
    """Five early, five late, and evenly spaced mid-body leaves, without replacement."""
    if count<=0 or total<=0:return []
    front=list(range(1,min(total,6)+1));back=list(range(max(1,total-5),total+1))
    nf=min(5,(count+1)//2);nb=min(5,count-nf)
    selected=set(front[:nf]+(back[-nb:] if nb else []));remaining=count-len(selected)
    if remaining>0:
        for i in range(remaining):selected.add(max(1,min(total,round(total*(.12+.76*(i+.5)/remaining)))))
    for n in range(1,total+1):
        if len(selected)>=min(count,total):break
        selected.add(n)
    return sorted(selected)

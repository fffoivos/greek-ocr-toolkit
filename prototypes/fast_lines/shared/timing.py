"""S7: atomic, content/config/source-keyed receipts and intentional repeat records."""
import hashlib,json,os,time
from pathlib import Path
from contextlib import contextmanager
import numpy as np

def json_default(v):
    if isinstance(v,np.ndarray): return v.tolist()
    if isinstance(v,np.generic): return v.item()
    if isinstance(v,Path): return str(v)
    raise TypeError(type(v).__name__)

def dump(path,value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp'); tmp.write_text(json.dumps(value,default=json_default,allow_nan=False)); tmp.replace(path)

def append(path,value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a') as f: f.write(json.dumps(value,default=json_default,allow_nan=False)+'\n')

def key(*parts): return hashlib.sha256(json.dumps(parts,sort_keys=True,default=json_default).encode()).hexdigest()

class Registry:
    def __init__(self,directory):
        self.directory=Path(directory); self.directory.mkdir(parents=True,exist_ok=True)
        self.ledger=self.directory/'experiments.jsonl'
    @contextmanager
    def claim(self,experiment,input_hash,config,source_hash,repeat=None):
        identity=key(experiment,input_hash,config,source_hash,repeat)
        receipt=self.directory/(identity+'.json')
        if receipt.exists() and json.loads(receipt.read_text()).get('status')=='complete':
            append(self.ledger,dict(id=identity,experiment=experiment,event='cache_hit'))
            yield None; return
        record=dict(id=identity,experiment=experiment,input_hash=input_hash,config=config,source_hash=source_hash,repeat=repeat,status='running')
        dump(receipt,record); start=time.perf_counter()
        try:
            yield record
        except Exception as exc:
            record.update(status='failed',error=repr(exc)); dump(receipt,record); append(self.ledger,record); raise
        else:
            record.update(status='complete',wall_s=time.perf_counter()-start); dump(receipt,record); append(self.ledger,record)

def summary(values):
    return dict(n=len(values),p50=float(np.median(values)),p95=float(np.percentile(values,95)),max=float(max(values))) if values else dict(n=0)

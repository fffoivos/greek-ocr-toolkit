"""S4 page record and dependency reader; algorithms never receive selection/name."""
import json,time
from pathlib import Path
import numpy as np
from .geometry import height_proxy
from .image_evidence import ImageEvidence
from .timing import dump
from .manifest import OUT

class Context:
    def __init__(self,gray,pm,items,products=None,reference=None,detector=None):
        self.gray=gray; self.pm=pm; self.items=items; self.size=(gray.shape[1],gray.shape[0])
        self.height=height_proxy(items,self.size); self.ev=ImageEvidence(gray,self.height)
        self.products=products or {}; self.reference=reference or {}; self.detector=detector
    def get(self,name): return self.products.get(name,{})

def read_product(name,page):
    d=OUT/name
    e=d/f'{page}.evidence.json'; j=d/f'{page}.json'
    return dict(json.loads(e.read_text()),items=json.loads(j.read_text())['items']) if e.exists() and j.exists() else {}

def materialize_primitives(ctx,path):
    """Diagnostic cache: execution reuse is recorded, runtime still pays on fresh pages."""
    path=Path(path)
    if path.exists():
        z=np.load(path)
        for k in ('gray','paper','contrast','persistence','ink'): ctx.ev.__dict__[k]=z[k]
        ctx.ev.__dict__['gradients']=(z['gx'],z['gy'])
        return dict(cache=True,compute_s=json.loads(path.with_suffix('.json').read_text())['compute_s'])
    t=time.perf_counter(); e=ctx.ev; gx,gy=e.gradients
    arrays={k:getattr(e,k) for k in ('gray','paper','contrast','persistence','ink')}; arrays.update(gx=gx,gy=gy)
    elapsed=time.perf_counter()-t; path.parent.mkdir(parents=True,exist_ok=True); np.savez_compressed(path,**arrays)
    dump(path.with_suffix('.json'),dict(compute_s=elapsed,shape=e.shape,height_proxy=ctx.height,frame='S2 1200 long-side image evidence'))
    return dict(cache=False,compute_s=elapsed)

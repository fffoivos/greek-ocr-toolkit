"""S4: immutable-by-convention evidence, geometry, requests, ownership."""
from dataclasses import dataclass, field, asdict
import numpy as np
from .geometry_memo import entry

@dataclass
class RegionRequest:
    id: str
    bbox: list
    purpose: str
    derivation: list
    uncertainty: str = 'ownership unknown'
    dependencies: list = field(default_factory=list)

@dataclass
class LineEvidence:
    polygon: list
    baseline: object = None
    score: object = None
    centreline: object = None
    height_interval: object = None
    guides: dict = field(default_factory=dict)
    source_ids: list = field(default_factory=list)
    provenance: str = 'unknown'

@dataclass
class LayoutEvidence:
    barriers: list
    blocks: list
    cells: list
    uncertain: list = field(default_factory=list)

@dataclass
class FamilyProfile:
    id: int
    members: list
    height: float
    profile: list
    guides: dict

@dataclass
class Decision:
    source_ids: list
    reason: str
    state: str = 'unknown'
    bbox: object = None

def bbox(item):
    cache=entry(item['polygon'])
    if cache is not None and 'bbox' in cache:return list(cache['bbox'])
    p=np.asarray(item['polygon'],float);out=[*p.min(0),*p.max(0)]
    if cache is not None:cache['bbox']=out
    return list(out)

def rect(b):
    x0,y0,x1,y1=map(float,b)
    return [[x0,y0],[x1,y0],[x1,y1],[x0,y1]]

def overlap(a,b):
    w=max(0,min(a[2],b[2])-max(a[0],b[0])); h=max(0,min(a[3],b[3])-max(a[1],b[1]))
    return w*h

def merge_requests(requests):
    """Merge intersecting requests to a fixed point, carrying every reason/id."""
    out=[]
    for r in requests:
        r=dict(asdict(r) if isinstance(r,RegionRequest) else r)
        r['derivation']=list(r['derivation']); r['dependencies']=list(r.get('dependencies',[]))
        again=True
        while again:
            again=False
            for i,q in enumerate(out):
                if overlap(r['bbox'],q['bbox'])>0:
                    a,b=r['bbox'],q['bbox']; r['bbox']=[min(a[0],b[0]),min(a[1],b[1]),max(a[2],b[2]),max(a[3],b[3])]
                    r['derivation']+=q['derivation']; r['dependencies']+=q['dependencies']+[q['id']]
                    out.pop(i); again=True; break
        out.append(r)
    return out

def deduplicate(existing,candidates,threshold=.7):
    kept=list(existing); conflicts=[]
    for item in candidates:
        b=bbox(item); area=max(1.,(b[2]-b[0])*(b[3]-b[1]))
        matches=[i for i,q in enumerate(kept) if overlap(b,bbox(q))/min(area,max(1.,np.prod(np.subtract(bbox(q)[2:],bbox(q)[:2]))))>threshold]
        if matches: conflicts.append(dict(candidate=item,overlaps=matches))
        else: kept.append(item)
    return kept,conflicts

def result(items, **evidence):
    return dict(items=items, **evidence)

"""MIX1 deterministic CPU draw arithmetic. No network, scheduler or GPU imports."""
import gzip, hashlib, json, math, random
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
D=428872
SEED=20261015

def require(x, why):
    if not x: raise ValueError(why)

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def rows(p):
    with (gzip.open(p,'rt') if str(p).endswith('.gz') else open(p)) as f:
        for l in f:yield json.loads(l)

def dump(p,obj):Path(p).write_text(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False)+'\n')

def lr(weights,n):
    w={k:Fraction(v) for k,v in weights.items()};s=sum(w.values())
    require(n>=0 and s>0 and all(v>=0 for v in w.values()),'invalid allocation')
    exact={k:n*v/s for k,v in w.items()};out={k:int(v) for k,v in exact.items()}
    for k in sorted(w,key=lambda k:(-(exact[k]-out[k]),k))[:n-sum(out.values())]:out[k]+=1
    return out

def epoch_counts(percent,d=D):
    # Hamilton across epochs, followed by the complementary real count.
    exact=[Fraction(d*p,100) for p in percent];target=round(sum(exact));q=[int(v) for v in exact]
    for i in sorted(range(len(q)),key=lambda i:(-(exact[i]-q[i]),i))[:target-sum(q)]:q[i]+=1
    return q

def cycle(pool,n,seed):
    require(bool(pool) or n==0,'positive quota without support');r=random.Random(str(seed));out=[]
    while len(out)<n:
        a=list(pool);r.shuffle(a);out.extend(a[:n-len(out)])
    return out

def stream_epochs(pool,counts,seed):
    # One shared stream makes curriculum exposure EXACTLY equal to 50%, both components.
    stream=cycle(pool,sum(counts),seed);offset=0;out=[]
    for n in counts:out.append(stream[offset:offset+n]);offset+=n
    return out

def stratum(r):return r['script_class'],math.ceil(r['width']/128)*128

def replay(base,real,born,total,epoch):
    available=defaultdict(list);scanned=defaultdict(list)
    for i,r in enumerate(born):available[stratum(r)].append(i)
    for p,(c,i,_) in enumerate(base):
        if c==0:scanned[stratum(real[i])].append(p)
    supported={k:len(v) for k,v in scanned.items() if available[k]}
    require(sum(supported.values())>=total,'M1 stopped: insufficient supported scanned draws')
    q=lr(supported,total);out=list(base);ledger=[]
    for k,slots in sorted(scanned.items()):
        n=q.get(k,0);chosen=random.Random(f'M1:{SEED}:{epoch}:{k}').sample(slots,n)
        for p,j in zip(chosen,cycle(available[k],n,f'M1:born:{epoch}:{k}')):out[p]=(2,j,born[j]['line_id'])
        ledger.append(dict(script=k[0],bucket=k[1],removed_scanned_draws=n,replay_draws=n,unsupported=not bool(available[k]),stay_scanned=len(slots)-n))
    return out,ledger

def cap(weights,parliament,limit=Fraction(1,4)):
    s=sum(weights.values());p=sum(v for k,v in weights.items() if k in parliament)
    require(s>0,'empty weights');before={k:v/s for k,v in weights.items()}
    if p/s<=limit:return before
    require(s>p,'cap has no non-parliament support')
    return {k:(limit*v/p if k in parliament else (1-limit)*v/(s-p)) for k,v in weights.items()}

def temperature(counts,alpha,parliament):
    require(alpha in (1,.5),'temperature');raw={k:(Fraction(v) if alpha==1 else Fraction(str(math.sqrt(v)))) for k,v in counts.items()}
    post=cap(raw,parliament)
    return post,dict(alpha=alpha,raw={k:str(v) for k,v in raw.items()},normalizer=str(sum(raw.values())),before_cap={k:str(v/sum(raw.values())) for k,v in raw.items()},after_cap={k:str(v) for k,v in post.items()})

def script_quota(counts,cyrillic,parliament,capped):
    # cap natural draw measure first, then hold parliament fixed while allocating other classes.
    natural=cap(counts,parliament) if capped else {k:Fraction(v,sum(counts.values())) for k,v in counts.items()}
    cy=sum(v for k,v in natural.items() if k in cyrillic);target=Fraction(6,100)
    require(cy>0,'M3 stopped: no Cyrillic support')
    require(not cyrillic&parliament,'M3 stopped: intersecting quotas require coordinator ruling')
    held=sum(v for k,v in natural.items() if k in parliament);other=1-held-cy
    require(other>0 and held+target<1,'M3 stopped: infeasible quota')
    return {k:(v if k in parliament else v*target/cy if k in cyrillic else v*(1-held-target)/other) for k,v in natural.items()}

def audit(r,blocked):
    require(r.get('split')=='train','non-train exposure')
    require(r.get('edition_id'),'unknown edition lineage')
    require(r.get('crop_sha256'),'missing crop SHA')
    require(r['edition_id'] not in blocked['editions'],'edition exposure')
    require(tuple(r['key']) not in blocked['keys'],'key exposure')
    require(r['crop_sha256'] not in blocked['crops'],'crop exposure')

def exclude(train,held):
    require(not {r['line_id'] for r in train}&{r['line_id'] for r in held},'E1 heldout ID')
    require(not {r['source_doc_id'] for r in train}&{r['source_doc_id'] for r in held},'E1 heldout document')
    require(all(r['split']=='train' for r in train),'E1 split')

def encode(r):return (json.dumps(r,ensure_ascii=True,separators=(',',':'))+'\n').encode()

def save_epoch(path,indexed,pools):
    h=hashlib.sha256();stats=defaultdict(Counter);unique=defaultdict(set)
    with open(path,'wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0,compresslevel=1) as f:
        for c,i,ident in indexed:
            require(pools[c][i]['line_id']==ident,'physical pool identity mismatch')
            b=encode((c,i,ident));f.write(b);h.update(b)
            for key in (f'component:{c}',f'class:{c}:{pools[c][i]["script_class"]}'):
                stats[key]['draws']+=1;unique[key].add((c,i))
    for k in stats:stats[k].update(unique=len(unique[k]),repeats=stats[k]['draws']-len(unique[k]))
    return dict(path=Path(path).name,sha256=sha(path),ordered_identity_sha256=h.hexdigest(),counts=dict(stats))

# MIX1B coordinator rules. Full strings are indexed, never probabilistic hashes.
def normalize_text(text):
    import unicodedata
    require(isinstance(text,str),'missing text label')
    return ' '.join(unicodedata.normalize('NFC',text).split())

class TextExposure:
    def __init__(self,references):
        normalized=[normalize_text(x) for x in references]
        self.exact=set(normalized)
        self.windows={s[i:i+30] for s in normalized for i in range(len(s)-29)}
    def hit(self,text):
        s=normalize_text(text)
        if s in self.exact:return 'exact'
        if any(s[i:i+30] in self.windows for i in range(len(s)-29)):return 'substring30'
        return None

def dominant_script(decision):
    inv=decision.get('final_inventory')
    if not isinstance(inv,dict):return 'none'
    counts={k:inv.get(k+'_letters',0) for k in ('greek','latin','cyrillic')}
    peak=max(counts.values());best=[k for k,v in counts.items() if v==peak]
    return best[0] if peak>0 and len(best)==1 else 'none'

IMPORT_COUNTS=dict(zip(('parliament','round1','mixed','vouli','openarchives','round2','cyrillic'),(64521,46964,27583,24938,19625,18782,12023)))
def wave_join(ref,imports):
    by_id={};counts=Counter()
    for r in imports:
        require(r['id'] not in by_id,'duplicate import id')
        require(r['wave'] in IMPORT_COUNTS,'unknown import wave')
        by_id[r['id']]=r['wave'];counts[r['wave']]+=1
    admitted=Counter()
    for r in ref:
        parent=r['key'][0]
        wave=by_id[r['key'][1]] if parent=='collection-v2-train' else 'W1' if parent=='collect-v3-W1-20261018-0524' else 'W2' if parent=='collect-v3-W2-20261018-0524' else None
        require(wave is not None,'unknown ref parent');r['wave']=wave;admitted[wave]+=1
    return counts,admitted

def exposure_filter(pool,blocked,text_index):
    kept=[];ledger=defaultdict(Counter)
    for r in pool:
        require(r['split']=='train','non-train exposure')
        source=r['text_source'];entry=ledger[source];entry['candidates']+=1
        reason=text_index.hit(r['label'])
        key_hit=tuple(r['key']) in blocked['keys'];crop_hit=bool({r['crop_sha256'],r.get('original_crop_sha256')} & blocked['crops'])
        if reason:entry[reason]+=1
        if key_hit:entry['key']+=1
        if crop_hit:entry['crop']+=1
        if reason or key_hit or crop_hit:entry['dropped']+=1
        else:kept.append(r);entry['kept']+=1
    return kept,{k:dict(v) for k,v in sorted(ledger.items())}

"""Manifest emitter for qualified pools, using the trainer's E4 fixed-draw schema.

Caller must bind physical pool ordering and audit every row first. Qualification
is enforced by run.py; this module also refuses unknown edition lineage.
"""
from core import *
from index_contract import write_index, verify_index

def indexed_epoch(real_indices,syn_indices,pools):
    # train.mix.assemble uses concatenated component order, not a global shuffle.
    return [(c,i,pools[c][i]['line_id']) for c,indices in enumerate((real_indices,syn_indices)) for i in indices]

def emit(out,name,epochs,pools,fraction,ledgers=None,d=D):
    folder=Path(out)/name;folder.mkdir(parents=True,exist_ok=False)
    plan=dict(schema='e4-fixed-draws-v1',seed=SEED,fractions=[1-fraction,fraction]+([0] if len(pools)==3 else []),epoch_rows=d,pool_sizes=[len(g) for g in pools],epochs={})
    for e,indexed in enumerate(epochs,1):
        require(len(indexed)==d,'epoch draw budget')
        stats=defaultdict(Counter);unique=defaultdict(set)
        for c,i,ident in indexed:
            for key in (f'component:{c}',f'class:{c}:{pools[c][i]["script_class"]}'):
                stats[key]['draws']+=1;unique[key].add((c,i))
        for key in stats:stats[key].update(unique=len(unique[key]),repeats=stats[key]['draws']-len(unique[key]))
        plan['epochs'][str(e)]=dict(draws=len(indexed),counts=dict(stats))
        keys=folder/f'epoch-{e}-keys.jsonl.gz'
        with open(keys,'wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0,compresslevel=1) as f:
            for position,(c,i,ident) in enumerate(indexed):f.write(encode([e,position,pools[c][i]['key']]))
        plan['epochs'][str(e)]['census_keys']=dict(path=keys.name,sha256=sha(keys))
    index=folder/'indices.jsonl.gz'
    write_index(index,epochs,pools)
    verify_index(index,epochs,pools)
    plan.update(schema='mix1-wave1c-index-v1',index=dict(path=index.name,sha256=sha(index)),seed_provenance=SEED,epochs_count=8)
    dump(folder/'draws.json',plan)
    dump(folder/'RECEIPT.json',dict(plan_sha256=sha(folder/'draws.json'),inputs={str(c):hashlib.sha256(b''.join(encode([i,r['line_id'],r['crop_sha256'],r['edition_id']]) for i,r in enumerate(g))).hexdigest() for c,g in enumerate(pools)},ledgers=ledgers or {},epochs=plan['epochs']))
    return dict(path=str(folder/'draws.json'),sha256=sha(folder/'draws.json'))

def fraction_epochs(pools,percent,d=D):
    q=epoch_counts(percent,d);r=[d-x for x in q]
    si=stream_epochs(list(range(len(pools[1]))),q,f'MIX1:{SEED}:synthetic')
    ri=stream_epochs(list(range(len(pools[0]))),r,f'MIX1:{SEED}:real')
    return [indexed_epoch(a,b,pools) for a,b in zip(ri,si)]

def generate(out,pools,blocked,active=('M1','M2'),d=D):
    require(set(active)<= {'M1','M2'},'M3/M4 stopped: qualify dominant script and original wave mapping first')
    for pool in pools:
        for r in pool:audit(r,blocked)
    require(len({tuple(r['key']) for r in pools[0]})==len(pools[0]),'duplicate real key')
    plans={};base=fraction_epochs(pools,[50]*8,d)
    if 'M2' in active:
        for p in (40,50,60):plans[f'M2_syn{p}']=emit(out,f'M2_syn{p}',base if p==50 else fraction_epochs(pools,[p]*8,d),pools[:2],p/100,d=d)
        curriculum=fraction_epochs(pools,[70]*4+[30]*4,d)
        require(Counter((c,i) for ep in base for c,i,_ in ep)==Counter((c,i) for ep in curriculum for c,i,_ in ep),'curriculum per-image exposure mismatch')
        plans['M2_curriculum']=emit(out,'M2_curriculum',curriculum,pools[:2],.5,dict(percent=[70]*4+[30]*4,exact_per_image_exposure=True),d=d)
    if 'M1' in active:
        epochs=[];ledger={}
        for e,ep in enumerate(base,1):
            replaced,stats=replay(ep,pools[0],pools[2],round(d/10),e);epochs.append(replaced);ledger[str(e)]=stats
        # Nominal fractions describe exact fixed draws only; trainer accepts them
        # without recomputing quotas. Replay is its own physical component.
        spec=emit(out,'M1',epochs,pools,.5,ledger,d=d)
        plan=json.loads(Path(spec['path']).read_text());plan['fractions']=[.4,.5,.1]
        dump(spec['path'],plan);spec['sha256']=sha(spec['path'])
        receipt_path=Path(spec['path']).parent/'RECEIPT.json';receipt=json.loads(receipt_path.read_text());receipt['plan_sha256']=spec['sha256'];dump(receipt_path,receipt)
        plans['M1']=spec
    return plans

def weighted_epochs(pools,group_key,weights,d=D):
    groups=defaultdict(list)
    for i,r in enumerate(pools[0]):groups[group_key(r)].append(i)
    q=epoch_counts([50]*8,d);epochs=[]
    for e,sn in enumerate(q,1):
        quota=lr(weights,d-sn);ri=[]
        for k,n in sorted(quota.items()):ri.extend(cycle(groups[k],n,f'{SEED}:{e}:{k}'))
        si=cycle(list(range(len(pools[1]))),sn,f'{SEED}:{e}:syn')
        epochs.append(indexed_epoch(ri,si,pools))
    return epochs

def all_arms(out,pools,blocked,m3_ok,d=D,*,bound_sources=None):
    plans=generate(out,pools,blocked,active=('M2',),d=d)
    status={'M2':{'status':'ok'}}
    try:
        plans.update(generate(out,pools,blocked,active=('M1',),d=d));status['M1']={'status':'ok'}
    except ValueError as e:status['M1']={'status':'stopped','reason':str(e)}
    status['M3']={'status':'ok' if m3_ok else 'stopped','reason':'census missing-inventory threshold' if not m3_ok else None}
    status['M4']={'status':'ok'}
    dump(Path(out)/'ARM_STATUS.json',status)
    if m3_ok:
        key=lambda r:(r['dominant_script'],r['wave']=='parliament')
        counts=Counter(key(r) for r in pools[0]);cy={k for k in counts if k[0]=='cyrillic'};parl={k for k in counts if k[1]}
        for capped in (False,True):
            weights=script_quota(counts,cy,parl,capped)
            name='M3_'+('capped' if capped else 'uncapped')
            plans[name]=emit(out,name,weighted_epochs(pools,key,weights,d),pools[:2],.5,dict(cap_first=capped,weights={str(k):str(v) for k,v in weights.items()},evidence='census decision.final_inventory'),d=d)
    for alpha in (1,.5):
        weights,ledger=temperature(Counter(r['wave'] for r in pools[0]),alpha,{'parliament'})
        name='M4_alpha'+str(alpha)
        plans[name]=emit(out,name,weighted_epochs(pools,lambda r:r['wave'],weights,d),pools[:2],.5,ledger,d=d)
    # Explicit census-key pool identity and original physical index in bound shards.
    pool_path=Path(out)/'POOLS.jsonl'
    with open(pool_path,'wb') as f:
        for c,pool in enumerate(pools):
            for i,r in enumerate(pool):f.write(encode(dict(component=c,index=i,physical_index=r.get('physical_index',i),key=r['key'],line_id=r['line_id'],crop_sha256=r['crop_sha256'])))
    dump(Path(out)/'MANIFESTS_RECEIPT.json',dict(bound_sources=bound_sources or {},plans=plans,pools=dict(path=str(pool_path),sha256=sha(pool_path)),physical_index_form=['epoch','position','component','physical pool index','line_id']))
    return plans

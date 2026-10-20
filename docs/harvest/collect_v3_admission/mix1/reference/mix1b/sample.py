"""Read-only real-input qualification; stdout JSON, no remote writes."""
from core import *
import io
W=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
P=W/'greek-page-ocr'
if 'CORE_SOURCE' not in globals():CORE_SOURCE=Path(__file__).with_name('core.py').read_text()

def record(path):return dict(path=str(path),sha256=sha(path),bytes=Path(path).stat().st_size)

def metadata(r):
    require(r['split'] in ('train','val','reserved'),'bad shard split')
    require(r['width']>0 and r['line_id'] and r['script_class'],'bad shard metadata')
    return {k:r[k] for k in ('line_id','source_doc_id','source_dataset','script_class','split','width')}

def dominant_paths(d,prefix='decision'):
    out={}
    if isinstance(d,dict):
        for k,v in d.items():
            if 'script' in k.lower() and ('dominant' in k.lower() or isinstance(v,str)):out[prefix+'.'+k]=v
            if k not in ('character_counts','detected_rows'):out.update(dominant_paths(v,prefix+'.'+k))
    elif isinstance(d,list):
        for i,v in enumerate(d):out.update(dominant_paths(v,prefix+f'[{i}]'))
    return out

def qualify():
    import pyarrow.parquet as pq
    from PIL import Image
    result=dict(schema='mix1-real-sample-v1',pending=['ref_364871'],inputs={},parents={},arms={},code_sha256=hashlib.sha256(CORE_SOURCE.encode()).hexdigest())
    tags_path=W/'scaling_w3/tags/scale1-c05-002/train_tags.jsonl.gz'
    tags={};waves=Counter();parent_rows=Counter()
    for r in rows(tags_path):
        require(r['key']==[r['parent_id'],r['row_id']],'tag key');require(r['edition_id'] and len(r['crop_sha256'])==64,'tag binding')
        tags[tuple(r['key'])]=r;waves[(r['parent_id'],r['source'])]+=1;parent_rows[r['parent_id']]+=1
    result['inputs']['tags']=dict(**record(tags_path),rows=len(tags),covered=True)
    rec=W/'scaling_w3/tags/scale1-c05-002/TAGS_RECEIPT.json';result['inputs']['tags_receipt']=dict(**record(rec),covered=True,rows=1)
    require(sha(rec)=='e4a155ebf5a2b13e28b5b3a45f3244bc0d2612e1704b00df3b24362a03335d39','tag receipt SHA')
    require(json.loads(rec.read_text())['output']['sha256']==sha(tags_path),'tag output SHA')
    result['source_table']=[dict(parent=k[0],source=k[1],rows=v) for k,v in sorted(waves.items())]
    seal=W/'benchmark_0.2/seal04';blocked=dict(editions=set(),keys=set(),crops=set())
    for name in ('suite.json','SEAL_RECEIPT.json','benchmark_v02_dev.jsonl','benchmark_v02_test.jsonl'):
        p=seal/name;obj=json.loads(p.read_text()) if p.suffix=='.json' else list(rows(p))
        item=dict(**record(p),rows=len(obj),covered=True)
        if isinstance(obj,list):
            crops=[]
            for r in obj:
                require(r.get('doc') and r['crop_sha256'] and r['parent_id'],'seal row binding')
                blocked['editions'].add(r.get('edition_id',r['doc']));blocked['keys'].add((r['parent_id'],r['row_id']));blocked['crops'].add(r['crop_sha256'])
                if len(crops)<20:
                    pimage=seal/r['crop_path'];require(sha(pimage)==r['crop_sha256'],'seal crop SHA');crops.append(record(pimage))
            item['crops']=crops
        result['inputs']['seal/'+name]=item
    release=W/'release_v3/rel3_c05_full_01/release_v3_admission.jsonl'
    rel={}
    for r in rows(release):
        k=(r['parent_id'],r['row_id'])
        if sum(1 for x in rel if x[0]==k[0])<1000:rel[k]=r
        if len(rel)>=2000:break
    # Census ordered by parent; parse to >=1000 per parent, never alter source or compute launches.
    census=W/'census_05_20261020/attempts/full-split-001/current/admitted_train.jsonl'
    selected=defaultdict(list);paths=defaultdict(Counter);sample_pools=defaultdict(list);rehashes=defaultdict(list)
    for r in rows(census):
        parent=r['parent_id']
        if len(selected[parent])>=1000:continue
        k=(parent,r['id']);require(k in tags,'census/tag join');t=tags[k]
        require(r['decision']['binding']['crop_sha256']==t['crop_sha256']==r['crop_sha256'],'census crop binding')
        require(r['split']=='train' and r['decision']['admitted'],'census disposition')
        selected[parent].append(k[1]);paths[parent].update(dominant_paths(r['decision']).keys())
        crop=Path(r['crop_path'])
        if parent!='collection-v2-train':
            rr=rel.get(k)
            require(rr is not None and rr['crop_sha256']==r['crop_sha256'],'REL3 join missing')
            crop=W/rr['crop_relative_path']
        if len(rehashes[parent])<20:
            require(sha(crop)==r['crop_sha256'],'real crop SHA');rehashes[parent].append(record(crop))
        with Image.open(crop) as im:width=max(64,min(2560,math.floor(im.width*48/im.height+.5)))
        o=dict(line_id=k[1],key=list(k),edition_id=r['edition_id'],crop_sha256=r['crop_sha256'],split='train',width=width,script_class=r.get('script_class'),source=r['source'])
        require(o['script_class'],'M1 missing census script_class');audit(o,blocked);sample_pools[parent].append(o)
        if len(selected)==3 and min(map(len,selected.values()))>=1000:break
    for p,ids in selected.items():result['parents'][p]=dict(rows=len(ids),dominant_script_paths=dict(paths[p]),crops=rehashes[p])
    result['inputs']['census']=dict(path=str(census),sha256='fe955d00af930b90b1d963a0454a4f4cba26de8fd24332ecc6873fd99f42c4f3',hash_deferred_to_job=True,rows=sum(map(len,selected.values())),covered=len(selected)==3)
    result['inputs']['release']=dict(path=str(release),sha256='92770112efe63669eb079384da0b2e4754901fff0b14fdcc97208207533e37b9',hash_deferred_to_job=True,rows=len(rel),covered=len(rel)==2000)
    pools=[]
    for family,label in [('real','E1'),('synthetic','synthetic_v5')]:
        root=P/f'out/e1_run4/{family}';info=json.loads((root/'build_info.json').read_text())
        result['inputs'][label+'/build_info']=dict(**record(root/'build_info.json'),rows=1,covered=True)
        train=[];held=[];image_hashes=[];inventory={}
        files=sorted((root/'train').glob('shard-*.parquet'))
        for p in files:
            count=0;crop_records=[]
            for batch in pq.ParquetFile(p).iter_batches(batch_size=256):
                for r in batch.to_pylist():
                    if count>=max(22,math.ceil(1000/len(files))):break
                    o=metadata(r);require(o['split']=='train','non-train shard');train.append(o);count+=1
                    if len(crop_records)<20:
                        h=hashlib.sha256(r['image_png']).hexdigest();Image.open(io.BytesIO(r['image_png'])).verify()
                        crop_records.append(dict(line_id=r['line_id'],sha256=h));image_hashes.append(h)
                if count>=max(22,math.ceil(1000/len(files))):break
            result['inputs'][label+'/'+p.name]=dict(path=str(p),sha256=info['shard_sha256']['train/'+p.name],hash_deferred_to_job=True,rows=count,crops=crop_records,covered=count>=20)
            inventory[p.name]=count
        for split in ('val','reserved'):
            count=0
            for p in sorted((root/split).glob('shard-*.parquet')):
                chunk=pq.read_table(p,columns=['line_id','source_doc_id','split']).to_pylist();held.extend(chunk);count+=len(chunk)
                result['inputs'][label+'/'+split+'/'+p.name]=dict(path=str(p),sha256=info['shard_sha256'][split+'/'+p.name],hash_deferred_to_job=True,rows=len(chunk),covered=True)
            require(count==info['written'][split],label+' heldout count')
        if label=='E1':exclude(train,held)
        # Real arithmetic path, not just a schema inspection.
        counts=epoch_counts([50]*8,d=1000);cur=epoch_counts([70]*4+[30]*4,d=1000)
        a=stream_epochs(list(range(len(train))),counts,'synthetic' if label!='E1' else 'real')
        b=stream_epochs(list(range(len(train))),cur,'synthetic' if label!='E1' else 'real')
        require(Counter(x for e in a for x in e)==Counter(x for e in b for x in e),'real curriculum exposure')
        pools.append(train)
        result[label]=dict(rows=len(train),images_rehashed=len(image_hashes),shards=inventory,heldout_rows=len(held),sample_identity_sha256=hashlib.sha256(json.dumps(train,sort_keys=True).encode()).hexdigest(),lineage_fields=list(train[0]))
    real=[r for g in sample_pools.values() for r in g];syn=pools[1];born=pools[0]
    base=[(0,i,r['line_id']) for i,r in enumerate(real)]+[(1,i,r['line_id']) for i,r in enumerate(syn)]
    try:
        replaced,ledger=replay(base,real,born,round(len(base)*.1),1);result['M1_sample']=dict(draws=len(replaced),strata=ledger)
    except ValueError as e:result['M1_sample']=dict(stopped=str(e))
    result['arms']['M3']=dict(status='stopped',reason='No per-line dominant script field in census decision/content_gate for W1/W2/v_c; inventories are not an owner-approved replacement',paths={p:dict(v) for p,v in paths.items()})
    result['arms']['M4']=dict(status='stopped',reason='M4 follows M3; original collection-round mapping not established by source labels alone')
    # E1 and synthetic lack canonical edition IDs. Do not claim their source_doc_id is a seal edition.
    for arm in ('M1','M2'):result['arms'][arm]=dict(status='stopped',reason='A10/A12 parquet has source_doc_id but no canonical edition_id or bound crosswalk for seal04; full edition audit cannot be certified')
    ctrl=P/'out/e4/wave1b/v2-codec/mixes/recovered.json'
    result['inputs']['wave2_ctrl']=dict(**record(ctrl),rows=1,covered=True)
    result['ctrl']=json.loads(ctrl.read_text());require(sha(ctrl)=='334f49a63d517b58713b7dfb82fcf45db7521fcdae8676f4b7fc3f5bde05f6f3','a707a36 control binding');require(sum(c['fraction'] for c in result['ctrl']['components'] if c['kind']=='synthetic')==.5,'ctrl synthetic fraction')
    result['seal_blocked_counts']={k:len(v) for k,v in blocked.items()}
    result['covered']=sum(bool(v['covered']) for v in result['inputs'].values());result['required']=len(result['inputs'])+1
    return result

if __name__=='__main__':print(json.dumps(qualify(),sort_keys=True))

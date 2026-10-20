"""Bound real joins and exposure audit, shared by qualification and manifests.
No writes, scheduler calls, or network access in this module.
"""
from core import *
from PIL import Image
import io
W=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
SUBSET=W/'scaling_w3/subsets/scale1-c05-003/SUBSETS_RECEIPT.json'
SUBSET_SHA='467566a7877a6abb18af855d166ebd45597c984d5ad15f595a5f2f0d1a4414e2'
REF_SHA='0cf865f094ff3f951b5f2bae6a5a0190d0e4209ae71407e94451a2f35be966b3'
WAVE2=W/'e4_wave2_rel3_20261020/code/27a49e51fa735e8f'

def load_real(receipt=SUBSET,digest=SUBSET_SHA,*,widths=False):
    require(sha(receipt)==digest==SUBSET_SHA,'subset receipt binding')
    spec=json.loads(Path(receipt).read_text())['subsets']['ref_364871']['output']
    require(sha(spec['path'])==spec['sha256']==REF_SHA,'ref binding')
    ref=list(rows(spec['path']));require(len(ref)==364871,'ref count')
    by_key={tuple(r['key']):r for r in ref};require(len(by_key)==len(ref),'duplicate ref key')
    tag_path=W/'scaling_w3/tags/scale1-c05-002/train_tags.jsonl.gz'
    for t in rows(tag_path):
        k=tuple(t['key'])
        if k not in by_key:continue
        r=by_key[k];require(r['crop_sha256']==t['crop_sha256'],'ref tag crop');r['edition_id']=t['edition_id']
    census=W/'census_05_20261020/attempts/full-split-001/current/admitted_train.jsonl'
    missing=Counter();parents=Counter();scripts=Counter();joined=set()
    for c in rows(census):
        k=(c['parent_id'],c['id'])
        if k not in by_key:continue
        require(k not in joined,'duplicate census key');joined.add(k);r=by_key[k];d=c['decision']
        require(c['crop_sha256']==r['crop_sha256'] and d['admitted'],'census binding')
        require(d['final_text']==r['label'],'subset differs census final_text')
        r.update(line_id=r['row_id'],split='train',script_class=c['script_class'],dominant_script=dominant_script(d))
        box=c.get('crop_bbox')
        if box:w,h=box[2]-box[0],box[3]-box[1]
        elif widths:
            with Image.open(r['crop_path']) as im:w,h=im.size
        else:w,h=None,None
        r['width']=max(64,min(2560,math.floor(w*48/h+.5))) if w is not None else None
        r['final_text']=d['final_text'];r['inventory_missing']=not isinstance(d.get('final_inventory'),dict)
        parents[k[0]]+=1;missing[k[0]]+=r['inventory_missing'];scripts[r['dominant_script']]+=1
    require(len(joined)==len(ref),'census coverage')
    import_path=W/'collection_v2/import_real_v2_train.jsonl'
    imported,admitted=wave_join(ref,rows(import_path));require(dict(imported)==IMPORT_COUNTS,'import wave counts')
    # Width comes from census crop_bbox, with real-sample validation against PNG headers.
    return ref,dict(ref=dict(spec),subset=dict(path=str(receipt),sha256=digest),import_binding=dict(path=str(import_path),sha256=sha(import_path)),waves=[dict(wave=k,import_rows=imported.get(k),admitted_rows=admitted[k]) for k in ('W1','W2',*IMPORT_COUNTS)],parents=dict(parents),missing_inventory=dict(missing),scripts=dict(scripts),cyrillic_share=scripts['cyrillic']/len(ref),M3_ok=all(missing[p]*100<=parents[p] for p in parents),script_evidence='census decision.final_inventory, not import script_class')

def load_candidates():
    import pyarrow.parquet as pq
    seal=W/'benchmark_0.2/seal04';references=[];blocked=dict(keys=set(),crops=set(),editions=set())
    for split in ('test','dev'):
        for r in rows(seal/f'benchmark_v02_{split}.jsonl'):
            references.append(r['reference']);blocked['editions'].add(r.get('edition_id',r['doc']));blocked['keys'].add((r['parent_id'],r['row_id']));blocked['crops'].add(r['crop_sha256'])
    require(len(references)==2690,'seal reference count');index=TextExposure(references)
    pools=[];receipts={}
    for family,label in (('synthetic','synthetic_v5'),('real','E1')):
        root=W/f'greek-page-ocr/out/e1_run4/{family}';info=json.loads((root/'build_info.json').read_text())
        pool=[];physical=0;hashes=[]
        for p in sorted((root/'train').glob('shard-*.parquet')):
            require(sha(p)==info['shard_sha256']['train/'+p.name],'candidate shard SHA')
            for batch in pq.ParquetFile(p).iter_batches(batch_size=256):
                for r in batch.to_pylist():
                    h=hashlib.sha256(r['image_png']).hexdigest()
                    pool.append(dict(line_id=r['line_id'],key=[label,r['line_id']],physical_index=physical,edition_id='text-audit-replaces-edition',original_crop_sha256=info.get('crop_sha256',{}).get(r['line_id']),crop_sha256=h,split=r['split'],width=r['width'],script_class=r['script_class'],label=r['gt_nfd'],text_source=r['source_doc_id'] if label=='E1' else r['source_dataset'],source_doc_id=r['source_doc_id']))
                    physical+=1
        if label=='E1':
            held=[]
            for split in ('val','reserved'):
                for p in sorted((root/split).glob('shard-*.parquet')):held.extend(pq.read_table(p,columns=['line_id','source_doc_id']).to_pylist())
            exclude(pool,held)
        kept,ledger=exposure_filter(pool,blocked,index)
        receipts[label]=dict(rows=len(pool),kept=len(kept),dropped=len(pool)-len(kept),per_source=ledger,codec_version=info['codec_version'],build_info=dict(path=str(root/'build_info.json'),sha256=sha(root/'build_info.json')),shards=info['shard_sha256'])
        pools.append(kept)
    return pools,blocked,dict(method='exact+30char',normalization='NFC then Unicode whitespace collapse and strip',references=2690,windows=len(index.windows),exactness='Exact full-string set and all 30-codepoint windows; any shared substring of length >=30 contains a 30-window. No hashing collision or approximate matching.',families=receipts)

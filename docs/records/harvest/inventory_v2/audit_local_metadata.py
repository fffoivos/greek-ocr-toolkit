"""Read-only census of existing HF-derived metadata and link tables."""
import collections, hashlib, json, pathlib, sys
import pyarrow.parquet as pq
BASE=pathlib.Path(__file__).resolve().parent
folder=BASE/'receipts/openarchives'
source=pathlib.Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/openarchives')
remote=json.loads((folder/'hf-authenticated-tables.json').read_text())
files=[]
for name in ['external_pdfs.parquet','all_links.parquet','collections_links_summary.parquet']:
    p=source/name;h=hashlib.sha256(p.read_bytes()).hexdigest();f=pq.ParquetFile(p)
    r=next((x for x in remote if x['path']=='data/'+name),{})
    rh=r.get('lfs',{}).get('oid');files.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h,remote_path='data/'+name,remote_lfs_oid=rh,byte_identity_verified=h==rh,rows=f.metadata.num_rows,schema=str(f.schema_arrow)))
counts=collections.Counter();repos=collections.Counter();years=collections.Counter();sample=[];sha=hashlib.sha256()
p=source/'doc_metadata.jsonl'
with p.open('rb') as f:
    for raw in f:
        sha.update(raw);r=json.loads(raw);counts['documents']+=1
        pm=r.get('pipeline_metadata') or {};sm=r.get('source_metadata') or {}
        if pm.get('ocr_success') is True:
            counts['ocr_success_true']+=1;repos[str(sm.get('collection_slug'))]+=1
            if pm.get('download_success') is True:counts['download_and_ocr_success_true']+=1
            if len(sample)<20:
                sample.append(dict(pipeline_metadata=pm,source_metadata=sm))
        if pm.get('ocr_success') is False:counts['ocr_success_false']+=1
        if pm.get('ocr_success') is None:counts['ocr_success_missing_or_null']+=1
out=dict(link_tables=files,local_metadata=dict(path=str(p),bytes=p.stat().st_size,sha256=sha.hexdigest(),provenance_limit='Existing derived metadata projection; extraction revision is not proven by the live HF tree. No corpus shard downloaded.'),counts=dict(counts),ocr_success_by_repository=dict(repos),candidate_sample=sample,physical_scan_status='ocr_success is pipeline metadata, not visual verification of a scan',pdfs_fetched=0)
(folder/'local-metadata-census.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(dict(counts));print('HF table byte matches',[x['byte_identity_verified'] for x in files])

"""Read-only Clariden extraction; emits tar to stdout, never writes remote files."""
import io, json, gzip, tarfile, hashlib, sys
from pathlib import Path
import pyarrow.parquet as pq
W=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
S=W/'scaling_w3/mix1_runs/MIX1D-8d25940f-export-001'
C=W/'e4_wave2_rel3_20261020/code/27a49e51fa735e8f'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as tar:
 def add(name,data):
  t=tarfile.TarInfo(name);t.size=len(data);tar.addfile(t,io.BytesIO(data))
 for name in ['EXPORT_RECEIPT.json',*[str(p.relative_to(S)) for p in sorted(S.glob('*/mix.json'))],*[str(p.relative_to(S)) for p in sorted(S.glob('*/INDEX.json'))]]:
  add(name,(S/name).read_bytes())
 bindings={}; labels=io.BytesIO()
 with gzip.GzipFile(fileobj=labels,mode='wb',mtime=0) as out:
  for rel in ('shared/real','prep/E1','prep/A12'):
   root=S/rel;info=json.loads((root/'build_info.json').read_text());add(rel+'/build_info.json',(root/'build_info.json').read_bytes())
   bindings[rel]={'build_info_sha256':sha(root/'build_info.json'),'shards':info['shard_sha256'],'bytes':0,'rows':0}
   for name,digest in sorted(info['shard_sha256'].items()):
    p=root/name;bindings[rel]['bytes']+=p.stat().st_size
    table=pq.read_table(p,columns=['line_id','gt_nfd','script_class'])
    bindings[rel]['rows']+=len(table)
    for row in table.to_pylist():out.write((json.dumps(dict(row,pool=rel,shard=name),ensure_ascii=False)+'\n').encode())
    if rel=='shared/real' and name=='train/shard-00000.parquet':
     assert sha(p)==digest
     table=pq.read_table(p).slice(0,1000);buf=io.BytesIO();pq.write_table(table,buf,compression='zstd',use_compliant_nested_type=False);add('sample.parquet',buf.getvalue())
     bindings['sample']={'source':str(p),'source_sha256':digest,'offset':0,'rows':1000,'sample_sha256':hashlib.sha256(buf.getvalue()).hexdigest()}
 add('labels.jsonl.gz',labels.getvalue());add('SOURCE_BINDINGS.json',json.dumps(bindings,indent=2).encode())
 for name in ('train/mix.py','codec/v2.1.json'):
  add('wave2/'+name,(C/name).read_bytes())

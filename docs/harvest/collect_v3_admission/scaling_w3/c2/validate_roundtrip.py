"""Read-only Clariden roundtrip validation. Run with python -B, E4_ROOT set."""
import hashlib,json,os,sys
from pathlib import Path
import pyarrow.parquet as pq
W=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
loader=W/'e4_wave2_rel3_20261020/code/27a49e51fa735e8f'
root=Path(sys.argv[1]);assert root.parent==W/'scaling_w3/c2_scratch' and root.name.startswith('roundtrip_')
sys.path.insert(0,str(loader));os.environ['E4_ROOT']=str(loader)
from train.mix import validate,load_rows,sha256
mix=validate(root/'mix.json',repo=loader);rows=load_rows(mix,'train')[0];assert len(rows)>=1000
info=json.loads((root/'real/build_info.json').read_text());sample=info['encoding_derivation']['sample'];source=Path(sample['source']);assert sha256(source)==sample['source_sha256']
before=pq.read_table(source).slice(sample['offset'],sample['rows']);after=pq.read_table(root/'real/train/shard-00000.parquet')
assert before.equals(after.select(before.column_names),check_metadata=True)
codec={a['ch']:a['id'] for a in json.loads((loader/'codec/v2.1.json').read_text())['atoms']}
import unicodedata
for row in rows:
 text=''.join(c for c in unicodedata.normalize('NFD',row['gt_nfd']) if unicodedata.category(c)!='Mn').lower()
 assert all(c in codec for c in text if unicodedata.category(c).startswith('L'))
 expected=' '.join(filter(None,''.join(c for c in text if c==' ' or (unicodedata.category(c).startswith('L') and c in codec)).split(' ')))
 assert row['base_label']==expected and row['base_label_ids']==[codec[c] for c in expected]
print(json.dumps(dict(status='ok',unicode_version=unicodedata.unidata_version,rows=len(rows),full_validate_ok=True,load_rows_ok=True,source_columns_equal=True,line_id_order_equal=True,pool_index_equal=True,evidence_directory=str(root),source_sample=sample,codec_sha256=sha256(loader/'codec/v2.1.json'),loader_sha256=sha256(loader/'train/mix.py'),contents_sha256={str(p.relative_to(root)):sha256(p) for p in sorted(root.rglob('*')) if p.is_file()}),sort_keys=True))

"""Prepare bounded evidence locally; deployment is rsync, validation is read-only."""
from pathlib import Path
import time
import pyarrow.parquet as pq
import build_c2 as b
P=Path(__file__).resolve().parent

def prepare():
 identity=b.read(P/'IDENTITY.json')['sha8'];remote=b.W/f'scaling_w3/c2_scratch/roundtrip_{identity}'
 out=P/'roundtrip';out.mkdir(exist_ok=False);(out/'real/train').mkdir(parents=True)
 codec=b.codec_map(P/'evidence/wave2/codec/v2.1.json');before=pq.read_table(P/'evidence/sample.parquet');t=time.perf_counter();after=b.augment(before,codec)
 path=out/'real/train/shard-00000.parquet';pq.write_table(after,path,compression='zstd',use_compliant_nested_type=False);actual=pq.read_table(path);b.assert_original(before,actual);assert after.equals(actual,check_metadata=True);elapsed=time.perf_counter()-t
 info=b.read(P/'evidence/shared/real/build_info.json');source_inventory=info['shard_sha256'];info['shard_sha256']=b.inventory(out/'real');info['written']={'train':len(before)};info['n_written']=len(before)
 info['encoding_derivation']=dict(source=str(b.SOURCE/'shared/real'),source_shard_inventory_sha256=b.digest(source_inventory),codec_sha256=b.sha(P/'evidence/wave2/codec/v2.1.json'),projection_source_sha256=b.projection_sha(),sample=b.read(P/'evidence/SOURCE_BINDINGS.json')['sample'],source_columns_equal=True,readback_equal=True,line_id_order_equal=True,pool_index_equal=True)
 b.dump(out/'real/build_info.json',info)
 mix=dict(schema_version=1,codec_version='v2.1',components=[dict(kind='real',fraction=1.0,partition_id=info['partition_id'],source='C2-real-roundtrip-export-001',shard_dir=str(remote/'real'),shard_sha256=info['shard_sha256'])],seed=20261015,created_by='C2',notes='bounded real sample from immutable export-001; C2 extra columns')
 b.dump(out/'mix.json',mix)
 result=dict(rows=len(before),seconds=elapsed,rows_per_second=len(before)/elapsed,remote_root=str(remote),contents_sha256={str(p.relative_to(out)):b.sha(p) for p in sorted(out.rglob('*')) if p.is_file()},source_columns_equal=True,readback_equal=True,projection_source_sha256=b.projection_sha())
 b.dump(P/'LOCAL_ROUNDTRIP.json',result);print(result)
if __name__=='__main__':prepare()

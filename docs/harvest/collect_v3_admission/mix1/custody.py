"""A12 source custody. Full shard hashing/equality is a CPU export-job gate."""
from core import *
W=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
P=W/'greek-page-ocr/out'
A12_SOURCE=P/'e4/wave1b/v2-codec/old_v2/synthetic'
A12_ROOT=P/'e1_run4/synthetic'
E1_SOURCE=P/'e1_run4/real'
A12_SHA='94e899a34929ee82c564c935b21a6659515a30d3fbdddae42366dc0ed71219cc'
ROOT_SHA='495453433c2efff88a8a0d7d39de32e856d878d815b923dbf3eb9354411bfbff'
CODEC_SHA='eae613e8eb18fd144314f68ae3b6424fb48dd778a2134fef417b06ac2353c4b6'
CONTROL=W/'e4_wave2_rel3_20261020/preparation/inventory03/control_synthetic_7/build_info.json'
GT_COLUMNS=['line_id','gt_nfd','gt_nfc','label_ids']

def compare_columns(left,right,columns=None):
    """Bounded Arrow comparison preserving row order across shard boundaries."""
    import pyarrow.parquet as pq
    counts={};equality={}
    for split in ('train','val','reserved'):
        def batches(root):
            for path in sorted((Path(root)/split).glob('shard-*.parquet')):
                yield from pq.ParquetFile(path).iter_batches(batch_size=256,columns=columns)
        a=iter(batches(left));b=iter(batches(right));x=next(a,None);y=next(b,None);n=0;checks={}
        while x is not None and y is not None:
            require(x.schema.names==y.schema.names,'column names differ '+split)
            size=min(len(x),len(y))
            for name in x.schema.names:
                checks[name]=checks.get(name,True) and x.column(x.schema.get_field_index(name)).slice(0,size).equals(y.column(y.schema.get_field_index(name)).slice(0,size))
            n+=size
            x=x.slice(size) if size<len(x) else next(a,None)
            y=y.slice(size) if size<len(y) else next(b,None)
        require(x is None and y is None,'row count differs '+split)
        counts[split]=n;equality[split]=checks
    require(all(all(c.values()) for c in equality.values()),'column equality failed')
    return dict(rows=counts,columns=equality,order_equal=True)

def chain_equal(*,full=False,source=A12_SOURCE,root=A12_ROOT):
    import pyarrow.parquet as pq
    source=Path(source);root=Path(root)
    require(sha(source/'build_info.json')==A12_SHA,'A12 source receipt')
    require(sha(root/'build_info.json')==ROOT_SHA,'A12 provenance root receipt')
    info=json.loads((source/'build_info.json').read_text());old=json.loads((root/'build_info.json').read_text())
    require(info['encoding_derivation']['source_receipt_sha256']==ROOT_SHA,'A12 chain link')
    for key in ('recipe_sha256','recipe_effective_sha256','written'):require(info[key]==old[key],'chain '+key)
    require(info['written']==dict(train=190486,val=9208,reserved=3999),'chain split counts')
    result=dict(source=dict(path=str(source),sha256=A12_SHA),provenance_root=dict(path=str(root),sha256=ROOT_SHA),full=full)
    if full:
        for base,receipt in ((source,info),(root,old)):
            paths={str(p.relative_to(base)) for p in base.rglob('shard-*.parquet')}
            require(paths==set(receipt['shard_sha256']),'chain shard inventory paths')
            for name,digest in receipt['shard_sha256'].items():require(sha(base/name)==digest,'chain shard SHA '+name)
        result.update(compare_columns(source,root,GT_COLUMNS));result['shards_hashed']=len(info['shard_sha256'])+len(old['shard_sha256'])
    else:
        witnesses=[]
        for split in ('train','val','reserved'):
            files=sorted((source/split).glob('shard-*.parquet'))
            require([p.name for p in files]==[p.name for p in sorted((root/split).glob('shard-*.parquet'))],'sample shard layout')
            for path in files:
                a=next(pq.ParquetFile(path).iter_batches(batch_size=22,columns=GT_COLUMNS))
                b=next(pq.ParquetFile(root/split/path.name).iter_batches(batch_size=22,columns=GT_COLUMNS))
                require(a.equals(b),'chain gt sample '+str(path))
                witnesses.append(dict(shard=f'{split}/{path.name}',rows=len(a),gt_sha256=hashlib.sha256(encode(a.to_pylist())).hexdigest()))
        result.update(sample_rows=sum(x['rows'] for x in witnesses),sample_shards=len(witnesses),witnesses=witnesses,columns=GT_COLUMNS)
        require(result['sample_rows']>=1000 and result['sample_shards']>=20,'chain sample coverage')
    result['status']='ok';return result

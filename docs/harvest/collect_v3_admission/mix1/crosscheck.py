"""A12 contract now; derivative inventory and columns after export. Read-only."""
from core import *

def crosscheck(path=None,own=None,*,source=None,codec=None):
    if not path:return dict(status='pending',reason='control build_info path required')
    other=Path(path);other=other/'build_info.json' if other.is_dir() else other
    require(other.is_file(),'control receipt unavailable')
    right=json.loads(other.read_text());derivation=right['encoding_derivation']
    if own:
        own=Path(own);require(own.is_file(),'own derivative unavailable')
        left=json.loads(own.read_text());bound=left['encoding_derivation']
        result=dict(phase='post-export',own=dict(path=str(own),sha256=sha(own)))
    else:
        from custody import A12_SOURCE,A12_SHA,CODEC_SHA
        source=Path(source or A12_SOURCE/'build_info.json')
        codec=Path(codec or Path(__file__).parent/'wave2/codec/v2.1.json')
        bound=dict(source_receipt_sha256=sha(source),codec_sha256=sha(codec))
        require(bound['source_receipt_sha256']==A12_SHA and bound['codec_sha256']==CODEC_SHA,'bound A12 source/codec mismatch')
        result=dict(phase='pre-export',source=dict(path=str(source),sha256=sha(source)),post_export='pending: export job compares derivative shard inventories and columns')
    equality={k:bound[k]==derivation[k] for k in ('source_receipt_sha256','codec_sha256')}
    result.update(status='ok' if all(equality.values()) else 'failed',contract=equality,other=dict(path=str(other),sha256=sha(other)))
    if result['status']!='ok':return result
    if own:
        # Verify physical bytes before taking the equal-inventory fast path.
        for root,info in ((own.parent,left),(other.parent,right)):
            actual={str(p.relative_to(root)):sha(p) for p in root.rglob('shard-*.parquet')}
            require(actual==info['shard_sha256'],'crosscheck shard inventory SHA')
        result['shard_inventory_equal']=left['shard_sha256']==right['shard_sha256']
        result['shard_inventory_sha256']={k:hashlib.sha256(encode(v['shard_sha256'])).hexdigest() for k,v in [('own',left),('control',right)]}
        if not result['shard_inventory_equal']:
            from custody import compare_columns
            result['column_equality']=compare_columns(own.parent,other.parent)
        else:result['column_equality']='guaranteed by equal verified shard bytes'
    result['line']='CROSSCHECK_A12_CONTRACT_OK source '+bound['source_receipt_sha256']+' codec '+bound['codec_sha256']
    return result

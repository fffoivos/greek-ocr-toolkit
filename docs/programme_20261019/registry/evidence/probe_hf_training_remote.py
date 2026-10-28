"""Read-only stat/receipt probe of the actual v4 trainer pools; no jobs."""
from pathlib import Path
import hashlib
import json
import time

R=Path('/capstor/scratch/cscs/fffoivos/greek-ocr-e3/e4_wave2_rel4_e0735c1_20261021_prep03/code')
out=dict(root=str(R),files=[],pools=[],listings=[])


def info(p):
    b=p.read_bytes();r=dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
    if p.suffix=='.json':
        obj=json.loads(b)
        if len(b)<=100000:r['content']=obj
        else:
            r['content_summary']={k:obj[k] for k in ['kind','codec_version','partition_id','source','operation','shard_sha256','written','n_written'] if k in obj}
            r['content_keys']=list(obj)
    out['files'].append(r);return r


def pool(p):
    if any(x['path']==str(p) for x in out['pools']):return
    q=dict(path=str(p),exists=p.exists(),files=0,bytes=0,complete=True,shards=[])
    start=time.monotonic()
    if p.exists():
        for f in p.rglob('*'):
            if f.is_file() and not f.is_symlink():
                q['files']+=1;q['bytes']+=f.stat().st_size
                if f.suffix=='.parquet':q['shards'].append(dict(path=str(f),bytes=f.stat().st_size))
                if time.monotonic()-start>8:q['complete']=False;break
        for name in ['build_info.json','partition_info.json','select_report.json']:
            if (p/name).exists(): info(p/name)
    out['pools'].append(q)


for sub in ['out/e4/wave2/job02','out/e4/wave2/job01','out/e4/wave2_prep/inventory04']:
    p=R/sub
    out['listings'].append(dict(path=str(p),exists=p.exists(),entries=[f.name for f in p.iterdir()] if p.exists() else []))
    for name in ['ctrl_mix.json','add_mix.json','add_corr_mix.json','val_v2.json','eval_v2_test.json','PREPARED.json','PREPARE_RECEIPT.json']:
        f=p/name
        if not f.exists():continue
        obj=info(f).get('content',{})
        for c in obj.get('components',[]):
            d=c.get('build_dir',c.get('shard_dir'))
            if d:pool(Path(d))
    for f in p.glob('*.json'):
        if f.stat().st_size<20000 and ('eval' in f.name or 'val' in f.name):
            obj=info(f).get('content',{})
            for c in obj.get('components',[]):
                d=c.get('build_dir',c.get('shard_dir'))
                if d:pool(Path(d))
print(json.dumps(out))

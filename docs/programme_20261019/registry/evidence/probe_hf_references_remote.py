"""Small, read-only v4 reference and archive-size probe; no crop-tree walk."""
from pathlib import Path
import hashlib
import json

W=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')
P=Path('/capstor/scratch/cscs/fffoivos/greek-ocr-e3/e4_wave2_rel4_e0735c1_20261021_prep03/code/out/e4/wave2/job02')
out=dict(files=[],groups=[],listings=[],selected_reference_shards=[])
for p in [P/'benchmark_0_2',P/'validation_v21',W/'greek-page-ocr/out/e4/wave1b/v2-codec',P/'control_synthetic_7']:
    out['listings'].append(dict(path=str(p),exists=p.exists(),entries=[dict(name=f.name,dir=f.is_dir(),bytes=f.stat().st_size) for f in p.iterdir()] if p.exists() else []))
    if not p.exists():continue
    # Parquet images are already sharded: a few hundred files, no image tree.
    shards=[f for f in p.rglob('*.parquet') if not f.is_symlink()]
    out['groups'].append(dict(path=str(p),files=len(shards),bytes=sum(f.stat().st_size for f in shards),basis='all Parquet shards under root; may contain multiple reference views'))
    for f in p.rglob('mix.json'):
        b=f.read_bytes();out['files'].append(dict(path=str(f),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),content=json.loads(b)))
    if p.name=='control_synthetic_7':
        for split in ['train','val','reserved']:
            fs=list((p/split).glob('*.parquet'))
            out['groups'].append(dict(path=str(p/split),files=len(fs),bytes=sum(f.stat().st_size for f in fs)))
V=W/'greek-page-ocr/out/e4/wave1b/v2-codec'
mixes=[('validation',P/'validation_v21/mix.json','val')]
for view in ['common_intersection','full_coverage']:
    f=V/(view+'.json');b=f.read_bytes();obj=json.loads(b)
    out['files'].append(dict(path=str(f),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),content=obj))
    for name,rec in obj['instruments'].items():
        if name=='v2_test':mixes.append((view+':v2_test',Path(rec['path']),'reserved'))
for name,f,split in mixes:
    b=f.read_bytes();obj=json.loads(b)
    out['files'].append(dict(path=str(f),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),content=obj))
    shards=[]
    for c in obj['components']:
        root=Path(c.get('build_dir',c.get('shard_dir')))
        for s in (root/split).glob('*.parquet'):
            shards.append(dict(path=str(s),bytes=s.stat().st_size))
    out['selected_reference_shards'].append(dict(name=name,split=split,files=len(shards),bytes=sum(s['bytes'] for s in shards),shards=shards))
print(json.dumps(out))

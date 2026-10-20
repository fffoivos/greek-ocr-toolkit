"""Prepare bounded mock fixtures. No inference/training here; r2_job.sbatch runs A-D."""
import argparse
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scripts.labelfix.clariden.r1_common import INDEX_DTYPE, sha256, write_json, write_rows, rows
from greekocr.labelfix.release_gate import policy_binding


def prepare(out,teacher,recognizer):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    inventory=[];metadata=[];index=[];images=[];manifest=[]
    for i in range(4):
        # Explicit mock-only synthetic old-pool data; no new supervision is admitted.
        path=out/f'crop-{i}.png';im=Image.new('L',(160,40),255);draw=ImageDraw.Draw(im)
        for j in range(8):draw.rectangle((j*18+4,12,j*18+14,30),fill=0)
        draw.point((i,0),fill=200+i)
        im.save(path);crop=f'docs/harvest/mock/crops/{i}.png';ch=sha256(path)
        inventory.append(dict(crop=crop,sha256=ch))
        metadata.append(dict(line=i,id=f'mock-{i}',doc=f'mock:{i}',crop=crop,recogniser_text='α'*8,
            coverage=[dict(start=j,base='α',scored=True,fused=False) for j in range(8)]))
        for j in range(8):
            y=([0,0,0,0],[1,1,0,0],[2,3,0,1],[0,1,1,0])[j%4]
            index.append((0,len(index),i,j,0,int(i==3),y,[[20,80],[20,80]]));images.append(np.asarray(im.resize((128,64))))
            if i!=3: manifest.append(dict(slot_id=[ch,j],line_id=f'mock-{i}',doc=f'mock:{i}',source='mock',provenance='old',targets=y,loss_weight=1))
    for name in ('data','heldout'):
        dest=out/name;dest.mkdir();np.save(dest/'index.npy',np.array(index,dtype=INDEX_DTYPE))
        for view in ('wide','narrow'):np.save(dest/f'shard-00000-{view}.npy',np.asarray(images))
        write_rows(dest/'lines.jsonl.gz',metadata)
        write_json(dest/'extraction_receipt.json',dict(complete=True,mode='c1',disjointness={'mock':True},
            document_split=dict(train=['mock:0','mock:1','mock:2'],validation=['mock:3']),
            sha256={p.name:sha256(p) for p in dest.iterdir() if p.is_file()}))
    write_rows(out/'inventory.jsonl',inventory);write_rows(out/'old_only.jsonl',manifest)
    # Exercise R2a in the mock with a print-proven mock target override.
    r2a=dict(manifest[0],provenance='native_print',targets=[0,1,0,0],replaces=manifest[0]['slot_id'])
    write_rows(out/'r2a.jsonl',[r2a])
    population=[]
    for i,path in enumerate(sorted(Path('tests/data/labelfix_s6').glob('*.png'))[:2]):
        population.append(dict(line_id=path.stem,doc=f'mock-teacher:{i}',source='mock-native',image=str(path.resolve()),crop_sha256=sha256(path),role='train' if i==0 else 'validation_reserve'))
    write_rows(out/'population.jsonl',population)
    cfg=dict(mock=True,data=str(out/'data'),heldout=str(out/'heldout'),teacher=str(Path(teacher).resolve()),
        recognizer=str(Path(recognizer).resolve()),line_list=str(out/'population.jsonl'),manifest=str(out/'r2a.jsonl'),
        inventory=str(out/'inventory.jsonl'),source_commit='52f34de9+R2P-uncommitted',policy=policy_binding(),excluded_documents=[],excluded_lines=[])
    cfg['sha256']={str(p):sha256(p) for p in [Path(cfg[k]) for k in ('teacher','recognizer','line_list','manifest','inventory')]+[out/'data/extraction_receipt.json',out/'heldout/extraction_receipt.json']}
    write_json(out/'config.json',cfg)
    return cfg

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ('out','teacher','recognizer'):ap.add_argument('--'+key,type=Path,required=True)
    prepare(**vars(ap.parse_args()))

"""Stage missing crops locally with exact native byte hashes; enforce upload cap."""
import json
import shutil
from pathlib import Path
from PIL import Image
from scripts.labelfix.clariden.r1_common import rows,write_rows,write_json,sha256
from scripts.labelfix.clariden.r2_population import OUT,CARDS,REMOTE

def stage():
    population=list(rows(OUT/'population_unstaged.jsonl'));local={r['line_id']:r for r in rows(OUT/'local_crops.jsonl')};probe={r['line_id']:r for r in rows(OUT/'crop_probe.jsonl')}
    w1={r['id']:r for r in rows(CARDS/'eligible_lines.jsonl') if r['pool']=='W1'}
    dest=OUT/'upload';dest.mkdir(exist_ok=True);uploaded={};found=0
    for r in population:
        if probe[r['line_id']]['found']:
            r['image']=probe[r['line_id']]['found'];found+=1;continue
        h=r['crop_sha256'];p=Path(local[r['line_id']]['local']);target=dest/(h+'.png')
        if not target.exists():
            if p.exists():shutil.copyfile(p,target)
            else:
                rr=w1[r['line_id']]
                with Image.open(rr['crop_source_image']) as im:im.convert('L').crop(rr['crop_bbox']).save(target,compress_level=3)
        if sha256(target)!=h:raise ValueError('staged native crop mismatch')
        uploaded[h]=target.stat().st_size;r['image']=f'{REMOTE}/labelfix_r2_20261017/crops/{h}.png'
    total=sum(uploaded.values())
    if total>600_000_000:raise RuntimeError(f'STOP: upload {total/1e6} MB exceeds budget')
    (dest/'CROPS_SHA256.txt').write_text(''.join(h+'  '+h+'.png\n' for h in sorted(uploaded)))
    write_rows(OUT/'population.jsonl',population)
    report=dict(lines=len(population),found_in_place=found,uploaded_files=len(uploaded),uploaded_bytes=total,uploaded_MB=total/1e6)
    write_json(OUT/'crop_staging.json',report);print(json.dumps(report))
if __name__=='__main__':stage()

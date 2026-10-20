import collections,hashlib,io,json,os,pathlib,sys
from PIL import Image,features
assert os.environ.get('SLURM_JOB_ID')
root=pathlib.Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018')
rows=[json.loads(x) for x in (root/'attempts/qual_03/qualify/sample.jsonl').read_text().splitlines()]
print(json.dumps(dict(versions={n:features.version(n) for n in ['zlib','libjpeg_turbo']})),flush=True)
for row in [rows[16],rows[17],rows[32],rows[33]]:
    source=pathlib.Path(row['crop_source_image']);box=row['crop_bbox'];expected=row['crop_sha256'];results={}
    with Image.open(source) as page:
        source_mode=page.mode
        for mode in ['L','RGB']:
            crop=page.convert(mode).crop(box)
            for level in [0,1,3,6,9]:
                b=io.BytesIO();crop.save(b,format='PNG',compress_level=level)
                results[f'{mode}/{level}']=hashlib.sha256(b.getvalue()).hexdigest()
    candidates=[root.parent/'collection_w1_originals'/row['source']/(row['id']+ext) for ext in ['.png','']]
    originals=[]
    for candidate in candidates:
        if candidate.is_file():
            raw=candidate.read_bytes()
            with Image.open(io.BytesIO(raw)) as actual:
                originals.append(dict(path=str(candidate),sha256=hashlib.sha256(raw).hexdigest(),mode=actual.mode,size=actual.size))
    print(json.dumps(dict(id=row['id'],expected=expected,source_mode=source_mode,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),box=box,results=results,originals=originals)),flush=True)

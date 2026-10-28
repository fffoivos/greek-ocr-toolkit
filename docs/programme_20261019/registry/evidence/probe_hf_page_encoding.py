"""Three-page lossless WebP size probe only; outputs stay outside Git."""
from pathlib import Path
import hashlib
import json
import time
from PIL import Image
import PIL

C=Path('/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data')
root=Path('/private/tmp/runner4-hf-book-20261022')
paths=sorted([p for w in ['W1','W2'] for p in (C/f'run/{w}/pages').glob('bsb_poly1850--027215cc6d2a7e8a--s*.json') if 'image' in json.loads(p.read_text())])
out=dict(pillow=PIL.__version__,scope='3 pages from one book; not a representative compression benchmark',pages=[])
for p in [paths[0],paths[len(paths)//2],paths[-1]]:
    d=json.loads(p.read_text());src=Path(d['image']);dest=root/(d['id']+'.webp');start=time.perf_counter()
    with Image.open(src) as im:
        im.load();mode=im.mode;size=im.size;pixels=hashlib.sha256(im.tobytes()).hexdigest()
        im.save(dest,format='WEBP',lossless=True,method=4)
    with Image.open(dest) as im:
        assert im.size==size
        assert hashlib.sha256(im.convert(mode).tobytes()).hexdigest()==pixels
    out['pages'].append(dict(source=str(src),source_bytes=src.stat().st_size,page_id=d['id'],
        webp=str(dest),webp_bytes=dest.stat().st_size,webp_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
        mode=mode,dimensions=size,decoded_pixels_sha256=pixels,pixel_match=True,seconds=time.perf_counter()-start))
out['source_bytes']=sum(r['source_bytes'] for r in out['pages']);out['webp_bytes']=sum(r['webp_bytes'] for r in out['pages'])
out['ratio']=out['webp_bytes']/out['source_bytes']
Path('out/runner4/HF_PAGE_ENCODING_PROBE.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))

"""Read-only foreground/label consistency census; stdout only, no preparation."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[4]
RUN=Path.home()/'Projects/collect-v3-data/run'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    rows=[]
    roots=(RUN/'cache/g1b',Path(__file__).parent/'CP3_geometry',Path(__file__).parent/'CP4_geometry')
    for root in roots:
        for receipt in sorted(root.glob('*/receipt.json')):
            cache=receipt.parent
            before={n:sha(cache/n) for n in ('receipt.json','ink.png','labels.npz','detector.json.gz')}
            with Image.open(cache/'ink.png') as im: ink=np.asarray(im).astype(bool)
            with np.load(cache/'labels.npz',allow_pickle=False) as ar: labels=ar['labels']
            row=dict(cache=str(cache),sha256=before,shape_equal=ink.shape==labels.shape)
            if row['shape_equal']:
                y,x=np.nonzero(ink!=(labels>0))
                row.update(disagreeing_pixels=len(x),ink_without_label=int((ink & (labels==0)).sum()),
                           label_without_ink=int(((labels>0)&~ink).sum()),
                           mismatch_box=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None)
            assert before=={n:sha(cache/n) for n in before},'cache changed during read'
            rows.append(row)
    print(json.dumps(dict(pages=len(rows),inconsistent=sum(not r['shape_equal'] or r['disagreeing_pixels']>0 for r in rows),
                         by_root={str(p):dict(pages=sum(Path(r['cache']).parent==p for r in rows),
                         inconsistent=sum(Path(r['cache']).parent==p and (not r['shape_equal'] or r['disagreeing_pixels']>0) for r in rows)) for p in roots},
                         pages_detail=rows),indent=2))

if __name__=='__main__': main()

"""Allowed R5 cohort and reuse of already computed R4b evidence; no held-out IO."""
import json
from pathlib import Path
import cv2
import numpy as np
from ..round2 import manifest,ROOT,COMMON,OLD
from ..shared.manifest import digest
from ..shared.timing import dump
REVIEW=ROOT.parent/'greek-ocr-toolkit-astra-lines4/.astra/fast_lines/review_r4'
PREVIOUS=ROOT.parent/'greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r4b'
DEST=ROOT/'.astra/fast_lines/out/round5/geometry'

def rows():
    out=manifest()['pages'][:]
    for p in sorted((REVIEW/'pages').glob('*.png')):
        g=cv2.imread(str(p),0)
        out.append(dict(page=p.stem,path=str(p),image_size=[g.shape[1],g.shape[0]],sha256=digest(p),group='new_curved',direction='new',parked=False))
    assert len(out)==200 and len({r['page'] for r in out})==200
    return out

def load(row):
    p=row['page'];gray=cv2.imread(str(ROOT/row['path']),0)
    cache=DEST/'baseline';record=cache/(p+'.json')
    if record.exists():
        obj=json.loads(record.read_text());pm=np.load(cache/(p+'.npy'));return gray,obj,pm
    if row['group']=='new_curved':
        raise FileNotFoundError('Pinned R4b baseline required for new curved page: '+str(record)+
            '. The supplied baseline was generated before R5 changes. Do not silently regenerate it with current Stack.')
    else:
        obj=json.loads((PREVIOUS/(p+'.evidence.json')).read_text());obj['items']=json.loads((PREVIOUS/(p+'.json')).read_text())['items']
        mapfile=next(q for q in [OLD/(p+'.npy'),COMMON/'baseline'/(p+'.npy')] if q.exists());pm=np.load(mapfile)
    return gray,obj,pm

"""Seed whole non-parliament pages until at least 1,000 v2 crops are covered."""
from collections import defaultdict
import json
from pathlib import Path
import random
import phase0_inventory as inventory

BASE=Path(__file__).resolve().parent
RECEIPTS=BASE/'receipts'
ROOT=Path.home()/'Projects/greek-ocr-toolkit'
W=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/recut_1d_20261017')
E3=W.parent
pages=inventory.rows(RECEIPTS/'pages.jsonl')
pool=sorted((p for p in pages if p['needed_for_masking']),key=lambda p:(p['wave'],p['doc'],p['page']))
random.Random(inventory.SEED).shuffle(pool)
selected=[]
for p in pool:
    selected.append(p)
    if sum(p['line_count'] for p in selected)>=1000:
        break
selected_keys={(p['wave'],p['doc'],p['page']) for p in selected}
grouped=defaultdict(list)
for split,data,_ in inventory.population(ROOT):
    for r in data:
        k=inventory.key(r)
        if k in selected_keys:
            grouped[k].append(r)
admitted={}
wanted={r['id'] for v in grouped.values() for r in v}
for wave in sorted({p['wave'] for p in selected}):
    for r in inventory.rows(ROOT/'docs/harvest'/wave/'admitted.jsonl'):
        if r['id'] in wanted:
            assert r['id'] not in admitted
            admitted[r['id']]=r
assert set(admitted)==wanted
selection=[]
for p in selected:
    lines=[]
    for r in grouped[(p['wave'],p['doc'],p['page'])]:
        a=admitted[r['id']]
        assert r['crop']==a['crop_path']
        lines.append(dict(r,crop_bbox=a['crop_bbox'],crop_sha256=a['crop_sha256'],
            crop=str(E3.relative_to(E3.parents[1])/'collection_v2/crops'/r['wave']/Path(r['crop']).parent.name/Path(r['crop']).name)))
    selection.append(dict(wave=p['wave'],doc=p['doc'],page=p['page'],page_id=f'{p["doc"]}-p{p["page"]:06d}',
        raster=str(W/'rate_pages'/p['path']),scan=p,megapixels=p['w']*p['h']/1e6,lines=lines))
inventory.write(RECEIPTS/'rate_selection.json',selection)
(RECEIPTS/'rate_pages_files.txt').write_text(''.join(p['path']+'\n' for p in selected))
inventory.write(RECEIPTS/'rate_selection_receipt.json',dict(seed=inventory.SEED,pages=len(selected),crops=len(wanted),bytes=sum(p['bytes'] for p in selected)))
print('Prepared',len(wanted),'crops on',len(selected),'pages; no remote run started')

"""Build /opt/e2-assets/parity/100_train_crops.jsonl: 100 distinct crops with parity_kind tags from the E1 f50 TRAIN pool.
short = narrowest real/synthetic lines; very_long = widest; padded = real imports (letterboxed, 'import_real:resize_letterbox');
blank = white canvases (no text; synthesized, provenance recorded) — parity compares native vs converted tensors, not accuracy."""
import json, sys, io, hashlib
from pathlib import Path
sys.path.insert(0, '.')
from train.mix import load_rows, validate
from PIL import Image
out = Path('/opt/e2-assets/parity'); crops = out/'crops'; crops.mkdir(parents=True, exist_ok=True)
m = validate('out/e1_run4/mix_f50.json', role='eval')
rows = [r for pool in load_rows(m, 'train') for r in pool]
real = [r for r in rows if r.get('font') == 'real']; synth = [r for r in rows if r.get('font') != 'real' and r.get('source_doc_id')]
synth.sort(key=lambda r: int(r['width'])); real.sort(key=lambda r: int(r['width']))
pick = [('short', r) for r in synth[:30]] + [('very_long', r) for r in synth[-30:]] + [('padded', r) for r in real[-30:]]
records = []
for kind, r in pick:
    png = r['image_png']; h = hashlib.sha256(png).hexdigest()[:16]; p = crops/f'{kind}_{h}.png'; p.write_bytes(png)
    records.append(dict(crop_path=str(p), parity_kind=kind, line_id=r['line_id'], width=int(r['width']), source='e1_run4 mix_f50 train pool'))
for i in range(10):
    w = 64 + 48*i; im = Image.new('L', (w, 48), 255); p = crops/f'blank_{w}.png'; im.save(p)
    records.append(dict(crop_path=str(p), parity_kind='blank', line_id=f'blank-{w}', width=w, source='synthesized white canvas'))
assert len(records) == 100 and len({r['crop_path'] for r in records}) == 100
with open(out/'100_train_crops.jsonl', 'w') as f:
    for r in records: f.write(json.dumps(r, ensure_ascii=False)+'\n')
import collections; print('kinds', dict(collections.Counter(r['parity_kind'] for r in records)), 'widths', min(r['width'] for r in records), max(r['width'] for r in records))

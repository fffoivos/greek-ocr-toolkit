"""S0: the only image enumerator. Selection is metadata, never an algorithm input."""
from greekocr.ops.data_root import input_path as _data_input
from pathlib import Path
import hashlib, json, platform
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.astra/fast_lines/out'
MODEL = ROOT / '.astra/fast_lines/onnx/PP-OCRv6_small_det.onnx'
PARKED = 's2-6419488b7f8e69fd20da-p00001'

def digest(path):
    h = hashlib.sha256()
    with _data_input(Path(path)).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

def source_hash():
    h = hashlib.sha256()
    for p in sorted((ROOT/'prototypes/fast_lines').rglob('*.py')):
        h.update(str(p.relative_to(ROOT)).encode()); h.update(p.read_bytes())
    return h.hexdigest()

def build():
    selection_path = ROOT/'.astra/fast_lines/discrepancy/selection.json'
    selection = json.loads(selection_path.read_text())
    entries = [(p, 'development', {}) for p in sorted((ROOT/'.astra/pages').glob('*.png'))]
    assert len(entries) == 54
    for group in ('discrepancy', 'agreement'):
        for row in selection[group]:
            p = ROOT/'.astra/fast_lines/discrepancy/pages'/f"{row['page']}.png"
            entries.append((p, group, row))
    assert len(entries) == 174 and len({p.stem for p,_,_ in entries}) == 174
    rows = []
    for p,group,sel in entries:
        with Image.open(p) as im: size = list(im.size)
        ours = (ROOT/'.astra/fast_lines/ours_lines'/f'{p.stem}.lines.json' if group == 'development'
                else p.with_name(p.stem+'.ours.lines.json'))
        rows.append(dict(page=p.stem, path=str(p.relative_to(ROOT)), sha256=digest(p),
                         image_size=size, group=group, selection=sel, parked=p.stem==PARKED,
                         ours=str(ours.relative_to(ROOT)), ours_sha256=digest(ours)))
    return dict(pages=rows, selection_sha256=digest(selection_path), model_sha256=digest(MODEL),
                environment=dict(platform=platform.platform(), python=platform.python_version()),
                scope='54 dev + 80 disagreement + 40 supplied agreement; no held-out', schema=1)

def load(path):
    obj=json.loads(_data_input(Path(path)).read_text())
    for r in obj['pages']:
        p=Path(r['path'])
        if p.is_absolute() or '..' in p.parts: raise ValueError('unsafe manifest path')
        if p.parent not in (Path('.astra/pages'),Path('.astra/fast_lines/discrepancy/pages')):
            raise ValueError('outside allowlist')
    return obj

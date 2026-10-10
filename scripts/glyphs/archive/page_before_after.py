"""One page, before and after: the text-layer boxes, then every line's outermost boundary (greekocr.glyphs.page_lines).
Runs where the page PDFs are (GPU node). Usage: page_before_after.py PAGE_KEY OUT_DIR   (PAGE_KEY = s2-<doc>-pNNNNN)"""
import json, re, sys, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(1, str(Path.home() / 'work/greek-page-ocr'))
from bench.extract_lines import SCALE                                        # noqa: E402
import pypdfium2 as pdfium                                                   # noqa: E402
from greekocr.glyphs.page_lines import page_lines                            # noqa: E402

V = Path.home() / 'work/greek-page-ocr/out/e2d/vouli_v6'
key, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
raw = subprocess.run(['grep', '-F', f'"line_id": "{key}-l', str(V / 'adjudicated/all.jsonl')], capture_output=True, text=True).stdout
rows = [json.loads(l) for l in raw.splitlines() if l.strip()]
rows = [r for r in rows if r['line_id'].startswith(key + '-l') and r.get('bbox_pixel')]
h2p = {b['source_url']: b['input_path'] for b in json.load(open(V / 'sources.json'))['books']}
pdf = pdfium.PdfDocument(h2p[rows[0]['source_doc_id']])
r0 = rows[0]
best = None
for idx in {int(r0['page']), int(r0['page']) - 1}:                          # the index whose render matches the crop
    if 0 <= idx < len(pdf):
        img = pdf[idx].render(scale=SCALE, grayscale=True).to_pil().convert('L')
        x0, y0, x1, y1 = (int(round(v)) for v in r0['bbox_pixel'])
        d = float(np.abs(np.asarray(img, float)[y0:y1, x0:x1] - np.asarray(Image.open(r0['crop_path']).convert('L'), float)).mean())
        if best is None or d < best[0]:
            best = (d, img)
page = best[1]
boxes = [tuple(int(round(v)) for v in r['bbox_pixel']) for r in rows]
lines = page_lines(page, boxes)
COL = [(214, 39, 40), (31, 119, 180), (44, 160, 44), (148, 103, 189)]
before = page.convert('RGB'); d = ImageDraw.Draw(before)
for k, b in enumerate(boxes):
    d.rectangle(b, outline=COL[k % 2], width=3)
after = page.convert('RGB'); ov = Image.new('RGBA', after.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(ov)
order = sorted(range(len(lines)), key=lambda i: (lines[i].x0 // 600, float(np.median(lines[i].base))))
for n, i in enumerate(order):
    L = lines[i]
    xs = np.arange(L.x0, L.x1)
    poly = [(int(x), float(t)) for x, t in zip(xs[::4], L.top[::4])] + [(int(x), float(b)) for x, b in zip(xs[::-4], L.bottom[::-4])]
    c = COL[n % 4]
    d2.polygon(poly, fill=c + (40,), outline=c + (255,), width=3)
    d2.line([(int(x), float(b)) for x, b in zip(xs[::4], L.base[::4])], fill=c + (160,), width=2)
after = Image.alpha_composite(after.convert('RGBA'), ov).convert('RGB')
w = 1600
for name, im in (('before', before), ('after', after)):
    im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(out / f'{key}.{name}.jpg', quality=70)
json.dump(dict(page=key, boxes=len(boxes), lines=len(lines), splits=sum(L.kind == 'split' for L in lines),
               stops=[L.stops for L in lines]), open(out / f'{key}.json', 'w'))
print(key, len(boxes), 'boxes →', len(lines), 'lines')

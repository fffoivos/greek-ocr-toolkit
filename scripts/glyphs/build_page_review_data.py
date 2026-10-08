"""Review data for every text-layer segment of one page, with the crop-level tools, as on the first review batches
(owner 8 Oct 20:15). Saves the segment crops as a fixture, runs greekocr.glyphs.report.line_record on each, and groups
the cards by column (top to bottom). Usage: build_page_review_data.py PAGE.png BOXES.json FIXTURE_DIR OUT.json
[--jpeg] [--overview LINES.jpg]   (--jpeg: crops embedded as JPEG; --overview: the page image with its lines, on top)"""
import base64, io, json, sys, time
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from greekocr.glyphs.components import binarise                             # noqa: E402
from greekocr.glyphs.report import document_priors, line_record             # noqa: E402

page_path, boxes_path, fix, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
JPEG = '--jpeg' in sys.argv
OVERVIEW = Path(sys.argv[sys.argv.index('--overview') + 1]) if '--overview' in sys.argv else None
page = Image.open(page_path).convert('L'); W, H = page.size
rows = json.load(open(boxes_path))
(fix / 'crops').mkdir(parents=True, exist_ok=True)
paths = []
for r in rows:
    p = fix / 'crops' / f"{r['line_id']}.png"
    page.crop(tuple(r['box'])).save(p)
    paths.append(str(p))
json.dump(dict(note='Every text-layer segment of one Vouli page (crops cut from the extractor-identical render, bench.extract_lines.SCALE); '
               'the text layer is another OCR, not a reference.', page=page_path.stem, size=[W, H], lines=rows),
          open(fix / 'index.json', 'w'), ensure_ascii=False, indent=0)

# the column rule: the longest unbroken vertical run of ink near the page centre
ink = binarise(np.asarray(page, np.float64))
lo, hi = int(.35 * W), int(.65 * W)
band = ink[int(.05 * H):int(.95 * H), lo:hi]
runs = np.zeros(hi - lo, int)
for j in range(hi - lo):
    col = band[:, j].astype(np.int8)
    if col.any():
        e = np.diff(np.r_[0, col, 0]); runs[j] = int((np.nonzero(e == -1)[0] - np.nonzero(e == 1)[0]).max())
share = band.mean(axis=0)                                              # ink share of every column near the centre
rule = lo + int(np.argmax(share))                                      # the column rule: the most inked column
jr = int(np.argmax(share)); side = np.r_[share[max(0, jr - 25):max(0, jr - 15)], share[jr + 15:jr + 25]]
thin = side.size > 0 and float(side.max()) < .5 * float(share[jr])   # a rule is thin; bold text is not
short = sum(r['box'][2] - r['box'][0] < .35 * W for r in rows) > .4 * len(rows)   # mostly short boxes: a table
two_columns = float(share.max()) >= .2 and thin and not short          # rule pages: share 0.25–0.55

priors = document_priors(paths)
t0 = time.time()
lines = []
for r, p in zip(rows, paths):
    x0, y0, x1, y1 = r['box']
    left_start = x0 < rule - 200                                         # left-column boxes start at its margin
    if not two_columns:
        section = 'body'                                                 # one column (or a table): top to bottom
    elif x1 - x0 < .35 * W and ((330 < x0 < rule - 200) or x0 > rule + .7 * (W - rule)):
        section = 'heading'                                              # short, centred or far right: headings, page numbers
    elif left_start:
        section = 'left'
    else:
        section = 'right'
    rec = line_record(p, priors=priors)
    spans = ' · spans both columns' if two_columns and x0 < rule - 200 and x1 > rule + 200 else ''
    rec.update(section=section, label=f"box x {x0}–{x1}, y {y0}–{y1}{spans}", note=f"text layer (another OCR, not a reference): {r['text']}" if r.get('text') else '')
    if JPEG:
        b = io.BytesIO(); Image.open(p).convert('L').save(b, 'JPEG', quality=60, optimize=True)
        rec['png'] = base64.b64encode(b.getvalue()).decode(); rec['img_type'] = 'jpeg'
    lines.append(rec)
order = {'heading': 0, 'left': 1, 'right': 2, 'body': 1}
lines.sort(key=lambda r: (order[r['section']], json.load(open(fix / 'index.json'))['lines'][[x['line_id'] for x in rows].index(r['id'])]['box'][1]))
extra = {}
if OVERVIEW:
    ov = Image.open(OVERVIEW); w = min(1400, ov.width); ov = ov.resize((w, round(ov.height * w / ov.width)), Image.LANCZOS)
    b = io.BytesIO(); ov.convert('RGB').save(b, 'JPEG', quality=62, optimize=True)
    extra = dict(overview=base64.b64encode(b.getvalue()).decode(), overview_w=ov.width, overview_h=ov.height)
json.dump(dict(built=time.strftime('%Y-%m-%d %H:%M'), mode='page', reviews=True, pool=len(lines), page=page_path.stem, **extra,
               lede=f"Every text-layer segment of page {page_path.stem} ({len(lines)} boxes), run through the crop-level tools exactly as on the "
                    "first review batches: underline (baseline), four guide lines, neighbour lines in the crop, columns, cut letters and ink. "
                    "Write a review under any line; reviews are saved with the page.",
               lines=lines), open(out, 'w'), ensure_ascii=False, allow_nan=False)
print(len(lines), 'segments;', round(time.time() - t0, 1), 's;', {k: sum(r['section'] == k for r in lines) for k in order})

"""Per text-layer box of one page: (1) the curves detected on the box's crop (four guide lines of every line found
in it — greekocr.glyphs.baseline.text_lines, as on the earlier review pages), (2) the correction by the page-lines
algorithm (greekocr.glyphs.page_lines): the line's band and baseline on the page, with the box.
Runs where the page PDFs are. Usage: page_segments_report.py PAGE_KEY OUT_DIR"""
import base64, io, json, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(1, str(Path.home() / 'work/greek-page-ocr'))
from bench.extract_lines import SCALE                                        # noqa: E402
import pypdfium2 as pdfium                                                   # noqa: E402
from greekocr.glyphs.baseline import text_lines                             # noqa: E402
from greekocr.glyphs.columns import column_segments                         # noqa: E402
from greekocr.glyphs.page_lines import page_lines                            # noqa: E402

V = Path.home() / 'work/greek-page-ocr/out/e2d/vouli_v6'
key, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
raw = subprocess.run(['grep', '-F', f'"line_id": "{key}-l', str(V / 'adjudicated/all.jsonl')], capture_output=True, text=True).stdout
rows = sorted((json.loads(l) for l in raw.splitlines() if l.strip()), key=lambda r: r['line_id'])
rows = [r for r in rows if r['line_id'].startswith(key + '-l') and r.get('bbox_pixel')]
h2p = {b['source_url']: b['input_path'] for b in json.load(open(V / 'sources.json'))['books']}
pdf = pdfium.PdfDocument(h2p[rows[0]['source_doc_id']])
r0, best = rows[0], None
for idx in {int(rows[0]['page']), int(rows[0]['page']) - 1}:
    if 0 <= idx < len(pdf):
        img = pdf[idx].render(scale=SCALE, grayscale=True).to_pil().convert('L')
        x0, y0, x1, y1 = (int(round(v)) for v in r0['bbox_pixel'])
        d = float(np.abs(np.asarray(img, float)[y0:y1, x0:x1] - np.asarray(Image.open(r0['crop_path']).convert('L'), float)).mean())
        if best is None or d < best[0]:
            best = (d, img)
page = best[1]
gray = np.asarray(page, np.float64)
boxes = [tuple(int(round(v)) for v in r['bbox_pixel']) for r in rows]
lines = page_lines(page, boxes)
mh = float(np.median([b[3] - b[1] for b in boxes]))

TEAL, PURPLE, RED, GREEN = (13, 110, 114), (122, 76, 194), (200, 30, 30), (20, 150, 60)


def b64(im, q=60, w=1400):
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q)
    return base64.b64encode(b.getvalue()).decode(), im.width, im.height


def poly(d, xs, ys, fill, width=2, dash=False):
    pts = [(float(x), float(y)) for x, y in zip(xs, ys)]
    if dash:
        for k in range(0, len(pts) - 6, 12):
            d.line(pts[k:k + 6], fill=fill, width=width)
    else:
        d.line(pts, fill=fill, width=width)


cards = []
for i, (r, b) in enumerate(zip(rows, boxes)):
    bx0, by0, bx1, by1 = b
    # (1) curves detected on the crop
    crop = page.crop(b)
    s = 2 if crop.height < 60 else 1
    vis = crop.convert('RGB').resize((crop.width * s, crop.height * s))
    d = ImageDraw.Draw(vis)
    found = []
    for seg in column_segments(crop):
        g = seg.glyphs
        if g is None:
            continue
        for L in text_lines(g):
            xs = np.arange(L.x0, L.x1) if L.side != 'main' else np.arange(g.width)
            col = TEAL if L.side == 'main' else PURPLE
            X = (xs + seg.x0) * s
            poly(d, X, L.base[xs] * s, col, 3)
            poly(d, X, L.mean[xs] * s, col, 2, dash=True)
            poly(d, X, L.ascender[xs] * s, col, 1, dash=True)
            poly(d, X, L.descender[xs] * s, col, 1, dash=True)

    a = b64(vis)
    # (2) the correction on the page
    mine = [L for L in lines if L.box == i]
    X0 = max(0, min([bx0] + [L.x0 for L in mine]) - 20); X1 = min(page.width, max([bx1] + [L.x1 for L in mine]) + 20)
    Y0 = max(0, int(by0 - 1.2 * mh)); Y1 = min(page.height, int(by1 + 1.2 * mh))
    ctx = page.crop((X0, Y0, X1, Y1)).convert('RGB'); d2 = ImageDraw.Draw(ctx)
    d2.rectangle((bx0 - X0, by0 - Y0, bx1 - X0 - 1, by1 - Y0 - 1), outline=RED, width=2)
    for L in mine:
        xs = np.arange(L.x0, L.x1) - X0
        poly(d2, xs, L.top - Y0, GREEN, 3); poly(d2, xs, L.bottom - Y0, GREEN, 3); poly(d2, xs, L.base - Y0, TEAL, 2, dash=True)
    c = b64(ctx)
    info = '; '.join(f"{L.kind} line, column {L.column}: x {L.x0}–{L.x1} (box {bx0}–{bx1}), stops {L.stops[0]} / {L.stops[1]}, "
                     f"up {'yes' if L.links.get('up') is not None else 'no'}, down {'yes' if L.links.get('down') is not None else 'no'}"
                     for L in mine) or 'no line fitted'
    cards.append(f'<article><h3>{r["line_id"]}</h3><p class="t">{info}</p>'
                 f'<figure><img src="data:image/jpeg;base64,{a[0]}" width="{a[1]}" height="{a[2]}"><figcaption>(1) detected on the crop: '
                 f'baseline solid, mean line dashed, top / bottom thin dashed — teal = the box\'s line, purple = other lines in the crop</figcaption></figure>'
                 f'<figure><img src="data:image/jpeg;base64,{c[0]}" width="{c[1]}" height="{c[2]}"><figcaption>(2) correction on the page: '
                 f'red = text-layer box, green = the line\'s boundary (top / bottom), teal dashed = its baseline</figcaption></figure></article>')

html = f'''<title>Page Segments Report</title>
<style>
:root {{ --bg: #f4f5f6; --fg: #1b1f24; --muted: #5b6570; --rule: #d5dbe0; --surface: #fff; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #12171c; --fg: #e3e8ed; --muted: #98a3ad; --rule: #2b343d; --surface: #1a222a; color-scheme: dark; }} }}
:root[data-theme="dark"] {{ --bg: #12171c; --fg: #e3e8ed; --muted: #98a3ad; --rule: #2b343d; --surface: #1a222a; color-scheme: dark; }}
body {{ background: var(--bg); color: var(--fg); font: 14px/1.45 system-ui, -apple-system, sans-serif; }}
main {{ max-width: 1460px; margin: 0 auto; padding-inline: 16px; padding-block: 20px 48px; display: grid; gap: 16px; }}
h1 {{ font-size: 1.35rem; margin: 0; }} h3 {{ font: 500 .85rem ui-monospace, Menlo, monospace; margin: 0; overflow-wrap: anywhere; }}
p {{ margin: 0; max-width: 80ch; color: var(--muted); }} .t {{ font-size: .8rem; }}
article {{ background: var(--surface); border: 1px solid var(--rule); border-radius: 6px; padding: 12px; display: grid; gap: 8px; }}
figure {{ margin: 0; display: grid; gap: 4px; }} figcaption {{ font-size: .75rem; color: var(--muted); }}
img {{ display: block; max-width: 100%; height: auto; border: 1px solid var(--rule); }}
</style>
<main><h1>{key}: every text-layer box — detected curves, then the correction</h1>
<p>{len(boxes)} boxes on the page, in reading order of their line ids. Per box: (1) the four guide lines detected on the box's own crop; (2) the line's boundary after the page-lines algorithm, drawn on the page around the box.</p>
{"".join(cards)}</main>'''
(out / f'{key}.segments.html').write_text(html)
print(len(boxes), 'boxes;', round((out / f'{key}.segments.html').stat().st_size / 1e6, 1), 'MB')

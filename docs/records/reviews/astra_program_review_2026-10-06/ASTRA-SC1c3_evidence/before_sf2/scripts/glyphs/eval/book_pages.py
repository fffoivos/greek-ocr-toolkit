"""Several pages from the same book/PDF, for book-level statistics (fonts, ink, show-through) — the counterpart of
diverse_pages.py, which takes one page per book. Pages are drawn at random from the middle 80 % of each named book,
skipping pages with almost no ink and pages already in use (--exclude). Renders: Vouli at bench SCALE, page index
verified against the stored crops; Anemi at native resolution. Writes <out>/<key>.png and <out>/selection.json.
Usage: book_pages.py --backup DIR --pdf-cache DIR --out DIR --books ID [ID ...] [--per-book 8] [--exclude KEY ...]
[--seed 20261010]   (ID = the 12-char Anemi book id or the 20-char Vouli PDF id, as in page keys)"""
import argparse, hashlib, json, random, sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from greekocr._vendor.bench.extract_lines import SCALE                        # noqa: E402


def render(pdf, index, scale):
    with pdfium.PdfDocument(str(pdf)) as doc:
        page = doc[index]; bm = page.render(scale=scale, grayscale=True); im = bm.to_pil().copy(); bm.close(); page.close()
    return im


def native_scale(pdf):
    with pdfium.PdfDocument(str(pdf)) as doc:
        page = doc[0]; imgs = list(page.get_objects(filter=[pdfium_c.FPDF_PAGEOBJ_IMAGE]))
        native = max((o.get_px_size() for o in imgs), key=lambda s: s[0] * s[1]); pw, ph = page.get_size()
        for o in imgs:
            o.close()
        page.close()
    return max(native[0] / pw, native[1] / ph)


def inked(im):
    a = np.asarray(im.convert('L'), np.float64); h, w = a.shape
    a = a[int(.1 * h):int(.9 * h), int(.1 * w):int(.9 * w)]
    return float((a < np.percentile(a, 50) - 60).mean())


ap = argparse.ArgumentParser(); ap.add_argument('--backup', type=Path, required=True); ap.add_argument('--pdf-cache', type=Path, required=True)
ap.add_argument('--out', type=Path, required=True); ap.add_argument('--books', nargs='+', required=True)
ap.add_argument('--per-book', type=int, default=8); ap.add_argument('--exclude', nargs='*', default=[]); ap.add_argument('--seed', type=int, default=20261010)
a = ap.parse_args(); rng = random.Random(a.seed); a.out.mkdir(parents=True, exist_ok=True); excl = set(a.exclude)
sel = dict(seed=a.seed, rule=f'{a.per_book} pages per named book/PDF, random from the middle 80 %, ink share 0.02–0.5', pages=[])
abooks = defaultdict(list)
for p in sorted((a.backup / 'e2-assets/anemi/records').glob('*/*/page-*.pdf')):
    abooks[p.parts[-3][:12]].append(p)
vouli = a.backup / 'out/e2d/vouli_v6'
by_url = {r['source_url']: a.pdf_cache / Path(r['input_path']).name for r in json.loads((vouli / 'sources.json').read_text())['books']}
vpages = defaultdict(lambda: defaultdict(list))
for t in (vouli / 'vouli_v6_rows.jsonl').read_text().splitlines():
    r = json.loads(t); key = r['line_id'].rsplit('-l', 1)[0]
    if by_url.get(r['source_doc_id'], Path('/missing')).is_file():
        vpages[key.split('-')[1]][key].append(r)
for b in a.books:
    got = 0
    if b in abooks:
        ps = abooks[b]; lo, hi = int(.1 * len(ps)), max(int(.1 * len(ps)) + 1, int(.9 * len(ps)))
        for p in rng.sample(ps[lo:hi], hi - lo):
            key = f'an-{b}-p{p.stem.split("-")[1]}'
            if got >= a.per_book: break
            if key in excl: continue
            im = render(p, 0, native_scale(p))
            if .02 <= inked(im) <= .5:
                im.save(a.out / f'{key}.png'); got += 1
                sel['pages'].append(dict(book=b, page=key, pdf=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), size=im.size))
                print(b, key, im.size, flush=True)
    elif b in vpages:
        keys = sorted(vpages[b], key=lambda k: int(k.rsplit('-p', 1)[1])); lo, hi = int(.1 * len(keys)), max(int(.1 * len(keys)) + 1, int(.9 * len(keys)))
        for key in rng.sample(keys[lo:hi], hi - lo):
            if got >= a.per_book: break
            if key in excl: continue
            rows = vpages[b][key]; pdf = by_url[rows[0]['source_doc_id']]
            probes = [(r, Image.open(vouli / 'lines/crops' / Path(r['crop_path']).name).convert('L')) for r in rows[:3]
                      if (vouli / 'lines/crops' / Path(r['crop_path']).name).exists()]
            best = None
            for idx in (int(rows[0]['page']) - 1, int(rows[0]['page'])):
                try:
                    im = render(pdf, idx, SCALE)
                except (IndexError, pdfium.PdfiumError):
                    continue
                err = np.mean([255. if im.crop(r['bbox_pixel']).size != o.size else
                               float(np.abs(np.asarray(im.crop(r['bbox_pixel']), float) - np.asarray(o, float)).mean()) for r, o in probes]) if probes else 255.
                if best is None or err < best[0]:
                    best = (err, idx, im)
            if best is None or best[0] > 2 or not .02 <= inked(best[2]) <= .5:
                continue
            best[2].save(a.out / f'{key}.png'); got += 1
            sel['pages'].append(dict(book=b, page=key, pdf=str(pdf), index=best[1], crop_check_mae=round(float(best[0]), 3), size=best[2].size))
            print(b, key, best[2].size, flush=True)
    else:
        print('unknown book', b, flush=True)
    if got < a.per_book: print(b, 'only', got, 'pages', flush=True)
json.dump(sel, open(a.out / 'selection.json', 'w'), indent=1)

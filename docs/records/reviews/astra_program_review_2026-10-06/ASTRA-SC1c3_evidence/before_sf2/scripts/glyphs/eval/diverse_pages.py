"""A diverse page set for the page-line work: one page per Anemi book and one per Vouli PDF (different printers, type,
layouts, years), split into a development set (given to the implementer) and a held-out set (kept back for the
generalisation check). Pages are drawn at random from the middle 80 % of each book/PDF; a page with almost no ink
(blank, plate, cover) is replaced by the next draw. Renders: Vouli at bench.extract_lines.SCALE (grayscale; the page
index is verified against the stored crops), Anemi at the page image's native resolution. Writes <out>/<split>/<key>.png
(+ <key>.boxes.json for Vouli: the text layer's boxes, optional hints only) and <out>/selection.json.
Usage: diverse_pages.py --backup DIR --pdf-cache DIR --out DIR [--exclude KEY ...] [--dev-anemi 18 --held-anemi 12
--dev-vouli 18 --held-vouli 12 --seed 20261009]"""
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
    """Share of dark pixels inside the central 80 % of the page: blank pages, plates and covers are near 0 or 1."""
    a = np.asarray(im.convert('L'), np.float64); h, w = a.shape
    a = a[int(.1 * h):int(.9 * h), int(.1 * w):int(.9 * w)]
    return float((a < np.percentile(a, 50) - 60).mean())


ap = argparse.ArgumentParser(); ap.add_argument('--backup', type=Path, required=True); ap.add_argument('--pdf-cache', type=Path, required=True)
ap.add_argument('--out', type=Path, required=True); ap.add_argument('--exclude', nargs='*', default=[])
ap.add_argument('--dev-anemi', type=int, default=18); ap.add_argument('--held-anemi', type=int, default=12)
ap.add_argument('--dev-vouli', type=int, default=18); ap.add_argument('--held-vouli', type=int, default=12)
ap.add_argument('--seed', type=int, default=20261009)
a = ap.parse_args()
rng = random.Random(a.seed)
excl_books = {k.split('-')[1] for k in a.exclude}                   # a book/PDF already in use is not drawn again
sel = dict(seed=a.seed, rule='one page per Anemi book / Vouli PDF, random from the middle 80 %, ink share 0.02–0.5', pages=[])

books = defaultdict(list)
for p in sorted((a.backup / 'e2-assets/anemi/records').glob('*/*/page-*.pdf')):
    books[p.parts[-3][:12]].append(p)
ab = [b for b in sorted(books) if b not in excl_books]; rng.shuffle(ab)
vouli = a.backup / 'out/e2d/vouli_v6'
srcs = json.loads((vouli / 'sources.json').read_text())['books']
by_url = {r['source_url']: a.pdf_cache / Path(r['input_path']).name for r in srcs}
pages = defaultdict(lambda: defaultdict(list))
for t in (vouli / 'vouli_v6_rows.jsonl').read_text().splitlines():
    r = json.loads(t); key = r['line_id'].rsplit('-l', 1)[0]
    if by_url.get(r['source_doc_id'], Path('/missing')).is_file():
        pages[key.split('-')[1]][key].append(r)
vb = [d for d in sorted(pages) if d not in excl_books]; rng.shuffle(vb)

for split, n_a, n_v in (('dev', a.dev_anemi, a.dev_vouli), ('heldout', a.held_anemi, a.held_vouli)):
    (a.out / split).mkdir(parents=True, exist_ok=True)
    got = 0
    while got < n_a and ab:
        b = ab.pop(); ps = books[b]; lo, hi = int(.1 * len(ps)), max(int(.1 * len(ps)) + 1, int(.9 * len(ps)))
        for p in rng.sample(ps[lo:hi], min(6, hi - lo)):
            im = render(p, 0, native_scale(p))
            if .02 <= inked(im) <= .5:
                key = f'an-{b}-p{p.stem.split("-")[1]}'; im.save(a.out / split / f'{key}.png')
                sel['pages'].append(dict(split=split, page=key, pdf=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), size=im.size))
                got += 1; print(split, key, im.size, flush=True); break
    got = 0
    while got < n_v and vb:
        d = vb.pop(); keys = sorted(pages[d], key=lambda k: int(k.rsplit('-p', 1)[1]))
        lo, hi = int(.1 * len(keys)), max(int(.1 * len(keys)) + 1, int(.9 * len(keys)))
        for key in rng.sample(keys[lo:hi], min(6, hi - lo)):
            rows = pages[d][key]; pdf = by_url[rows[0]['source_doc_id']]
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
            best[2].save(a.out / split / f'{key}.png')
            json.dump([dict(line_id=r['line_id'], box=r['bbox_pixel'], text=r.get('text', '')) for r in rows],
                      open(a.out / split / f'{key}.boxes.json', 'w'), ensure_ascii=False)
            sel['pages'].append(dict(split=split, page=key, pdf=str(pdf), index=best[1], crop_check_mae=round(float(best[0]), 3), size=best[2].size))
            got += 1; print(split, key, best[2].size, flush=True); break
json.dump(sel, open(a.out / 'selection.json', 'w'), indent=1)

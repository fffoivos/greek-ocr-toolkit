"""Recut real parliament lines from their rendered pages (owner 8 Oct 18:05–18:25). Runs on the worker that holds the
page PDFs (GPU node), never on the MacBook.

Usage: recut_real.py TARGETS.json OUT_DIR [N_PROC]
  TARGETS.json: list of line ids (s2-<doc20>-pNNNNN-lNNNNN).
Per target page: render the PDF page in the frame of bbox_pixel (scale = pixel width / PDF width), check the frame
and the page index against the stored crop, fit every text-layer box on the page, recut the targets
(greekocr.glyphs.recut.fix_page). Writes OUT/img/<id>.orig.png (stored crop), .line<N>.png (output lines), .context.jpg (page region
with the original box in red and the recut region in green), and OUT/meta.jsonl.
"""
import json, re, sys, time
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from greekocr.glyphs.recut import fix_page                                # noqa: E402

VOULI = Path.home() / 'work/greek-page-ocr/out/e2d/vouli_v6'
KEEP = ('line_id', 'source_doc_id', 'page', 'bbox_pixel', 'bbox_pdf', 'crop_path', 'text')
ID = re.compile(r'"line_id":\s*"(s2-[0-9a-f]+-p\d+)-l\d+"')


def load_pages(targets: set[str]) -> dict[str, list[dict]]:
    pages = {t.rsplit('-l', 1)[0] for t in targets}
    out = defaultdict(list)
    with open(VOULI / 'adjudicated' / 'all.jsonl') as fh:
        for line in fh:
            m = ID.search(line[:4000]) or ID.search(line)
            if not m or m.group(1) not in pages:
                continue
            r = json.loads(line)
            out[m.group(1)].append({k: r.get(k) for k in KEEP})
    return out


def best_index(pdf, page: int, row: dict, scale: float):
    """Page index (page or page−1) whose render at bbox_pixel matches the stored crop best."""
    stored = np.asarray(Image.open(row['crop_path']).convert('L'), np.float64)
    x0, y0, x1, y1 = (int(round(v)) for v in row['bbox_pixel'])
    best = None
    for idx in {page, page - 1}:
        if not 0 <= idx < len(pdf):
            continue
        img = pdf[idx].render(scale=scale).to_pil().convert('L')
        cut = np.asarray(img, np.float64)[y0:y1, x0:x1]
        if cut.shape != stored.shape:
            h, w = min(cut.shape[0], stored.shape[0]), min(cut.shape[1], stored.shape[1])
            a, b = cut[:h, :w], stored[:h, :w]
        else:
            a, b = cut, stored
        d = float(np.abs(a - b).mean()) if a.size else 1e9
        if best is None or d < best[0]:
            best = (d, idx, img, cut.shape, stored.shape)
    return best


def do_page(args):
    key, rows, targets, out = args
    import pypdfium2 as pdfium
    books = json.load(open(VOULI / 'sources.json'))['books']
    h2p = {b['source_url']: b['input_path'] for b in books}
    t0 = time.time()
    res = []
    try:
        r0 = next(r for r in rows if r['line_id'] in targets)
        pdf = pdfium.PdfDocument(h2p[r0['source_doc_id']])
        bp, bd = r0['bbox_pixel'], r0['bbox_pdf']
        scale = (bp[2] - bp[0]) / max(1e-6, bd[2] - bd[0])
        d, idx, img, cut_shape, stored_shape = best_index(pdf, int(r0['page']), r0, scale)
        pdf.close()
        gray = np.asarray(img, np.float64)
        rows = [r for r in rows if r.get('bbox_pixel')]
        boxes = [tuple(int(round(v)) for v in r['bbox_pixel']) for r in rows]
        tix = {i for i, r in enumerate(rows) if r['line_id'] in targets}
        page_lines = fix_page(gray, boxes, only=tix)
        by_box = {}
        for pl in page_lines:
            by_box.setdefault(pl.box_index, []).append(pl)
        for i in sorted(tix):
            r = rows[i]; lid = r['line_id']
            meta = dict(line_id=lid, page_key=key, page_index=idx, frame_mad=round(d, 2), cut_shape=cut_shape,
                        stored_shape=stored_shape, box=boxes[i], n_page_boxes=len(boxes), text=r['text'])
            Image.open(r['crop_path']).convert('L').save(out / 'img' / f'{lid}.orig.png')
            pls = sorted(by_box.get(i, []), key=lambda p: (p.kind != 'main', p.segment))
            if not pls:
                meta['error'] = 'no line fitted'; res.append(meta); continue
            reg = np.zeros(gray.shape, bool)
            lines_meta = []
            for n, pl in enumerate(pls):
                L = pl.recut
                reg |= L.region
                (pl.box_image if not pl.fixed else L.image).save(out / 'img' / f'{lid}.line{n}.png')
                lines_meta.append(dict(kind=pl.kind, segment=pl.segment, fixed=pl.fixed, reason=pl.reason,
                                       cut=pl.cut, cut_sides=pl.cut_sides, stops=[L.stop_left, L.stop_right],
                                       added=[L.added_left, L.added_right, L.added_top, L.added_bottom],
                                       x=[L.x0, L.x1], y=[L.y0, L.y1], xh=round(L.xh, 2), notes=L.notes,
                                       straight_shape=[L.image.height, L.image.width]))
            ys, xs = np.nonzero(reg)
            bx0, by0, bx1, by1 = boxes[i]
            xh = pls[0].recut.xh
            X0 = max(0, min(bx0, xs.min()) - 30); X1 = min(gray.shape[1], max(bx1, xs.max() + 1) + 30)
            Y0 = max(0, int(min(by0, ys.min()) - 2.5 * xh)); Y1 = min(gray.shape[0], int(max(by1, ys.max() + 1) + 2.5 * xh))
            ctx = Image.fromarray(np.clip(gray[Y0:Y1, X0:X1], 0, 255).astype(np.uint8)).convert('RGB')
            arr = np.asarray(ctx).copy()
            for pl in pls:
                rg = pl.recut.region[Y0:Y1, X0:X1]
                edge = rg & ~ndi.binary_erosion(rg)
                arr[edge] = (20, 150, 60)
            ctx = Image.fromarray(arr)
            ImageDraw.Draw(ctx).rectangle([bx0 - X0, by0 - Y0, bx1 - X0 - 1, by1 - Y0 - 1], outline=(200, 30, 30), width=2)
            ctx.save(out / 'img' / f'{lid}.context.jpg', quality=60)
            meta.update(lines=lines_meta, context=[X0, Y0, X1, Y1])
            res.append(meta)
    except Exception as e:                                               # noqa: BLE001
        res.append(dict(page_key=key, error=repr(e)[:300]))
    for m in res:
        m['page_seconds'] = round(time.time() - t0, 1)
    return res


if __name__ == '__main__':
    targets = set(json.load(open(sys.argv[1])))
    out = Path(sys.argv[2]); (out / 'img').mkdir(parents=True, exist_ok=True)
    nproc = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    t0 = time.time()
    pages = load_pages(targets)
    print(f'{len(targets)} targets on {len(pages)} pages ({sum(map(len, pages.values()))} boxes) loaded in {time.time() - t0:.0f}s', flush=True)
    done = 0
    with open(out / 'meta.jsonl', 'w') as fh, Pool(nproc) as pool:
        for res in pool.imap_unordered(do_page, [(k, v, targets, out) for k, v in pages.items()]):
            for m in res:
                fh.write(json.dumps(m, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, 'item') else str(o)) + '\n')
            fh.flush()
            done += 1
            if done % 10 == 0:
                print(f'{done}/{len(pages)} pages {time.time() - t0:.0f}s', flush=True)
    print('RECUT_REAL_DONE', flush=True)

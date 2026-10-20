#!/usr/bin/env python3
"""Compile any page-read JSONL into the owner's approved native-size diptychs.

Offline only. Optional --plan includes pages with no line records. Font fitting
and raster placement reproduce the final owner-approved 14 October builder.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
import hashlib
import json
import multiprocessing
from pathlib import Path
import re
import statistics
import sys

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from greekocr.harvest.readers import atomic, read_jsonl

FONT = '/System/Library/Fonts/Supplemental/Times New Roman.ttf'
NUMBER_FONT = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
PAD = GAP = 40
GREEN, RED, LOW = (20, 150, 60), (200, 30, 30), (170, 0, 0)
README = "One image per page. Left: the page with Document AI's line boxes (green; RED box = it spans more than one printed row). Right: the same lines' text drawn where their box sits, one type size per page. Red text = Document AI's mean confidence on that line is below 0.89 (the weakest 5%). Numbers match on both sides.\n"


@lru_cache(maxsize=72)
def font(size):
    return ImageFont.truetype(FONT, max(9, min(80, int(size))))


@lru_cache(maxsize=1)
def number_font():
    return ImageFont.truetype(NUMBER_FONT, 20)


def slug(title, length=40):
    title = re.sub(r'[/:\\?*"<>|]', ' ', title)
    return re.sub(r'\s+', ' ', title).strip()[:length].strip()


def relative_path(page):
    prefix = 'RESCUED_' if page.get('origin') == 'rescue' else ''
    key = page.get('key', page.get('book_key'))
    title = slug(page['title'])
    if title in ('', '.', '..'):
        title = 'untitled'
    return Path(f"{page['decade']}s") / f"{prefix}{page['year']}_{title}_{key[:6]}" / f"p{page['page']:04d}.jpg"


def fit(draw, text, width, start):
    f = font(start)
    while f.size > 9 and draw.textlength(text, font=f) > width * 1.05:
        f = font(f.size - 1)
    return f.size


def render_page(image, rows):
    """Return the final canvas and explicit native/canvas text positions."""
    page = image.convert('RGB')
    width, height = page.size
    draw = ImageDraw.Draw(page)
    heights = [r['bbox'][3]-r['bbox'][1] for r in rows if r.get('counted')]
    median = statistics.median(heights or [r['bbox'][3]-r['bbox'][1] for r in rows] or [1])
    panel = Image.new('RGB', (width, height), 'white')
    pd = ImageDraw.Draw(panel)
    items = []
    for row in rows:
        x0, y0, x1, y1 = row['bbox']
        text = ' '.join(row['docai_text'].split())
        if text:
            items.append((row, text, fit(pd, text, x1-x0, median*.95)))
    sizes = sorted(s for r, _, s in items if r.get('counted')) or sorted(s for _, _, s in items)
    # The approved builder uses the discrete lower quartile, index n//4.
    page_size = sizes[len(sizes)//4] if sizes else median*.8
    for row in rows:
        x0, y0, x1, y1 = row['bbox']
        tall = y1-y0 > 1.7*median
        draw.rectangle([x0, y0, x1, y1], outline=RED if tall else GREEN, width=3 if tall else 2)
        draw.text((max(2, x0-40), y0-2), str(row['line_number']), fill=RED, font=number_font())
    positions = []
    for row, text, fitted in items:
        x0, y0, x1, y1 = row['bbox']
        h = y1-y0
        tall = h > 1.7*median
        confidence = row.get('confidence')
        low = confidence is not None and confidence < .89
        f = font(min(page_size, fitted))
        ty = y0+2 if tall else y0+(h-f.size)/2-f.size*.15
        pd.text((x0, ty), text, fill=LOW if low else (0, 0, 0), font=f)
        pd.text((max(2, x0-40), y0-2), str(row['line_number']), fill=RED, font=number_font())
        if tall:
            pd.rectangle([x0, y0, x1, y1], outline=RED, width=2)
        positions.append(dict(line_number=row['line_number'], text=text, font_size=f.size,
                              fitted_size=fitted, panel_xy=[x0, ty],
                              canvas_xy=[PAD+width+GAP+x0, PAD+ty],
                              tall=tall, low_confidence=low,
                              overflow_at_minimum=f.size == 9 and pd.textlength(text, font=f) > (x1-x0)*1.05))
    canvas = Image.new('RGB', (2*width+GAP+2*PAD, height+2*PAD), 'white')
    canvas.paste(page, (PAD, PAD))
    canvas.paste(panel, (PAD+width+GAP, PAD))
    ImageDraw.Draw(canvas).line([(PAD+width+GAP//2, PAD), (PAD+width+GAP//2, PAD+height)],
                               fill=(200, 200, 200), width=2)
    return canvas, dict(native_size=[width, height], canvas_size=list(canvas.size),
                        median_counted_height=median, page_font_size=font(page_size).size,
                        positions=positions)


def default_books():
    result = {}
    for name in ('selection.json', 'rescue/selection.json'):
        path = REPO / 'docs/harvest/round1' / name
        if path.exists():
            result.update({b['key']: b for b in json.loads(path.read_text())['books']})
    return result


def compile_page_task(task):
    page, rows, target, relative = task
    with Image.open(REPO / page['image']) as image:
        canvas, layout = render_page(image, rows)
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target, 'JPEG', quality=85)
    return dict(page_id=page.get('page_id', page.get('id')), path=str(relative),
                jpeg_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                raster_sha256=hashlib.sha256(canvas.tobytes()).hexdigest(), **layout)


def compile_records(records_file, output, *, pages=None, books=None, path_builder=None, workers=1):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    groups = defaultdict(list)
    for row in read_jsonl(records_file):
        groups[row['page_id']].append(row)
    books = default_books() if books is None else books
    if pages is None:
        pages = [dict(rows[0], **{k: books[rows[0]['book_key']][k] for k in ('title', 'key')})
                 if 'title' not in rows[0] else rows[0] for rows in groups.values()]
    if len({p['id'] if 'id' in p and 'page_id' not in p else p['page_id'] for p in pages}) != len(pages):
        raise ValueError('duplicate page in compile plan')
    receipts, paths, tasks = [], set(), []
    for index, page in enumerate(pages, 1):
        pid = page.get('page_id', page.get('id'))
        rows = sorted(groups.pop(pid, []), key=lambda r: r['docai_index'])
        path = REPO / page['image']
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != page['image_sha256'] or any(r['image_sha256'] != digest for r in rows):
            raise ValueError('compile source image changed: ' + pid)
        relative = (path_builder or relative_path)(page)
        if relative in paths:
            raise ValueError('compiled path collision')
        paths.add(relative)
        target = output / relative
        tasks.append((page, rows, str(target), str(relative)))
    if groups:
        raise ValueError('record pages missing from compile plan')
    def collect(iterator):
        for index, receipt in enumerate(iterator, 1):
            receipts.append(receipt)
            if index % 50 == 0:
                print(f'compiled {index}/{len(pages)}', flush=True)
    if workers == 1:
        collect(map(compile_page_task, tasks))
    else:
        with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('spawn')) as pool:
            collect(pool.map(compile_page_task, tasks, chunksize=1))
    (output / 'README.txt').write_text(README)
    receipt = dict(schema='t19-compiled-page-reads-1', records_file=str(records_file),
                   records_sha256=hashlib.sha256(Path(records_file).read_bytes()).hexdigest(),
                   builder_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   fonts={p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in (FONT, NUMBER_FONT)},
                   pad=PAD, gap=GAP, jpeg_quality=85, page_count=len(receipts), pages=receipts)
    atomic(output / 'compile_receipt.json', receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('records', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--plan', type=Path)
    args = parser.parse_args()
    pages = json.loads(args.plan.read_text())['pages'] if args.plan else None
    result = compile_records(args.records, args.output, pages=pages)
    print(json.dumps(dict(pages=result['page_count'], output=str(args.output))))


if __name__ == '__main__':
    main()

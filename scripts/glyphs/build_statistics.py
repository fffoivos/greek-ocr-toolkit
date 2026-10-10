"""Build Q2 statistics from frozen Q1 outputs, with resumable per-page measurement.

Example: python scripts/glyphs/build_statistics.py --pages .astra/pages --out .astra/out
Multiple --collection PAGES OUT pairs produce a combined corpus and book references.
This command never writes line/cell/structure files or invokes an OCR reader.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import sys
import time

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from greekocr.glyphs.statistics import (
    page_statistics, book_statistics, corpus_statistics, write_statistics,
    render_glyph_statistics, render_book_statistics,
)
from greekocr.pages.outputs import read_statistics as read_page
from greekocr.pages import statistics as statistics_module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collection', nargs=2, action='append', metavar=('PAGES', 'OUT'), required=True)
    parser.add_argument('--summary-out', type=Path, default=Path('.astra/out'))
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--keys', nargs='*')
    args = parser.parse_args()
    implementation = hashlib.sha256(Path(statistics_module.__file__).read_bytes()).hexdigest()
    locations = {}
    grouped = defaultdict(list)
    for inputs, outputs in args.collection:
        inputs, outputs = Path(inputs), Path(outputs)
        selection = inputs/'selection.json'
        books = {r['page']: r['book'] for r in json.loads(selection.read_text())['pages']} if selection.exists() else {}
        for path in sorted(inputs.glob('*.png')):
            key = path.stem
            if args.keys and key not in args.keys:
                continue
            if key in locations:
                raise ValueError(f'Duplicate page across collections: {key}')
            start = time.perf_counter()
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            geometry = outputs/f'{key}.lines.json'
            geo_digest = hashlib.sha256(geometry.read_bytes()).hexdigest()
            st = outputs/f'{key}.stats.json'
            if args.resume and st.exists():
                previous = json.loads(st.read_text())
                reuse = (previous.get('source_sha256') == digest and previous.get('implementation_sha256') == implementation and previous.get('lines_file_sha256') == geo_digest)
            else:
                reuse = False
            book = books.get(key, key.split('-', 1)[-1].rsplit('-p', 1)[0])
            if not reuse:
                lines = json.loads(geometry.read_text())
                structure = json.loads((outputs/f'{key}.structure.json').read_text())
                with Image.open(path) as im:
                    im.load()
                    result = page_statistics(im, lines, page_key=key, book_id=book, structure=structure)
                    result['stats'].update(source_sha256=digest, implementation_sha256=implementation,
                        lines_file_sha256=geo_digest, source_image=str(path),
                        seconds=round(time.perf_counter()-start, 3))
                    write_statistics(result, outputs)
                    render_glyph_statistics(im, result).save(outputs/f'{key}.glyphs.jpg', quality=92)
                print(key, 'letters', result['stats']['summary']['letter_bodies'], 'rows', len(result['glyphs']),
                      'seconds', round(time.perf_counter()-start, 2), flush=True)
            else:
                print(key, 'reused source/geometry/implementation-verified measurement', flush=True)
            locations[key] = (path, outputs)
            grouped[book].append(key)
    # One book at a time bounds memory. The full corpus needs only page summaries.
    page_summaries = []
    books_dir = args.summary_out/'books'
    books_dir.mkdir(parents=True, exist_ok=True)
    for book, keys in sorted(grouped.items()):
        pages = [read_page(locations[key][1], key) for key in keys]
        result = book_statistics(pages, book_id=book)
        for page in result['pages']:
            key = page['stats']['page_key']
            write_statistics(page, locations[key][1])
            page_summaries.append(page['stats'])
        (books_dir/f'{book}.stats.json').write_text(json.dumps(result['stats'], indent=2, allow_nan=False)+'\n')
        render_book_statistics(result['stats']).save(books_dir/f'{book}.summary.jpg', quality=93)
        print('book', book, 'pages', len(keys), flush=True)
    corpus = corpus_statistics(page_summaries)
    args.summary_out.mkdir(parents=True, exist_ok=True)
    (args.summary_out/'corpus.stats.json').write_text(json.dumps(corpus, indent=2, allow_nan=False)+'\n')
    with (args.summary_out/'corpus.summary.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(corpus['table'][0]) if corpus['table'] else ['page_key'])
        writer.writeheader()
        writer.writerows(corpus['table'])
    print('corpus', {k: v for k, v in corpus.items() if k != 'table'}, flush=True)


if __name__ == '__main__':
    main()

"""Serializers for geometry, glyph tables, summaries and selected review images."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from .options import OutputOptions
from .records import BookResult, PageResult
from .statistics import render_book_statistics, render_glyph_statistics, write_statistics
from .structure import render_structure

# Encoding settings, not geometric thresholds: retain Q2 review JPEG qualities.
LINE_JPEG_QUALITY = 92
STRIP_JPEG_QUALITY = 94
BOOK_JPEG_QUALITY = 93


def _json(path: Path, data: Any) -> str:
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n')
    return str(path)


def read_statistics(directory: str | Path, page_key: str) -> dict[str, Any]:
    """Read Q2 page statistics and restore the nested mark evidence from storage."""
    directory = Path(directory)
    stats = json.loads((directory / f'{page_key}.stats.json').read_text())
    path = directory / stats['glyph_table']
    if path.suffix == '.parquet':
        import pyarrow.parquet as pq
        glyphs = pq.read_table(path).to_pylist()
        for row in glyphs:
            row['attached_marks'] = json.loads(row['attached_marks'])
    else:
        glyphs = [json.loads(line) for line in path.read_text().splitlines()]
    return dict(stats=stats, glyphs=glyphs)


def write_page(result: PageResult, source: Any, outputs: OutputOptions) -> dict[str, str]:
    directory = Path(outputs.directory)
    needs_image = outputs.files & {'lines_image', 'unrolled_image', 'structure_image', 'glyphs_image'}
    if source is None and needs_image:
        raise ValueError('Writing review images from existing PageResults requires the original images')
    if outputs.files & {'statistics', 'glyphs_image'} and result.statistics is None:
        raise ValueError('Statistics were not measured')
    payloads = result.to_records()
    if 'rows' in outputs.files and payloads['rows'] is None:
        raise ValueError('Rows output requires an existing result joined at rows granularity')
    directory.mkdir(parents=True, exist_ok=True)
    files = {}
    for name in ('lines', 'segments', 'structure', 'cells', 'delivery', 'rows', 'checks'):
        if name in outputs.files:
            files[name] = _json(directory / f'{result.page_key}.{name}.json', payloads[name])
    if 'statistics' in outputs.files:
        files.update(write_statistics(result.statistics, directory))
    if 'orientation' in outputs.files:
        if result.orientation is None:
            raise ValueError('Orientation was not requested')
        oriented = result.orientation
        files['orientation'] = _json(directory / f'{result.page_key}.orientation.json', dict(
            dominant=oriented.dominant.to_record(), proposals=oriented.proposals, groups=oriented.groups,
            words=[word.to_record(result.image_size, result.page_size) for word in oriented.words]))
    if needs_image:
        if isinstance(source, Image.Image):
            image = source
        else:
            # Keep the supplied color channels; normalized arrays use the same
            # full gray-level range as the detector's accepted 0-1 inputs.
            array = np.asarray(source)
            if array.max() <= 1:
                array = array * 255
            image = Image.fromarray(np.clip(array, 0, 255).astype(np.uint8))
        images = {}
        if outputs.files & {'lines_image', 'unrolled_image'}:
            from .render import render_lines
            images.update(render_lines(image, result.segmentation))
        if 'structure_image' in outputs.files:
            images['structure_image'] = render_structure(image, result.lines, result.structure)
        if 'glyphs_image' in outputs.files:
            images['glyphs_image'] = render_glyph_statistics(image, result.statistics)
        for name, image in images.items():
            if name not in outputs.files:
                continue
            path = directory / f"{result.page_key}.{name.removesuffix('_image')}.jpg"
            image.save(path, quality=STRIP_JPEG_QUALITY if name == 'unrolled_image' else LINE_JPEG_QUALITY)
            files[name] = str(path)
    return files


def write_book(result: BookResult, outputs: OutputOptions) -> dict[str, str]:
    files = {}
    directory = Path(outputs.directory)
    if result.statistics is None:
        return files
    books = directory / 'books'
    if outputs.files & {'statistics', 'book_image'}:
        books.mkdir(parents=True, exist_ok=True)
    if 'statistics' in outputs.files:
        files['book_statistics'] = _json(books / f'{result.book_id}.stats.json', result.statistics)
        files['corpus_statistics'] = _json(directory / 'corpus.stats.json', result.corpus)
        path = directory / 'corpus.summary.csv'
        with path.open('w', newline='') as stream:
            table = result.corpus['table']
            writer = csv.DictWriter(stream, fieldnames=list(table[0]) if table else ['page_key'])
            writer.writeheader()
            writer.writerows(table)
        files['corpus_summary'] = str(path)
    if 'book_image' in outputs.files:
        path = books / f'{result.book_id}.summary.jpg'
        render_book_statistics(result.statistics).save(path, quality=BOOK_JPEG_QUALITY)
        files['book_image'] = str(path)
    return files

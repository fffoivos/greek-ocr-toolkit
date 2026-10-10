"""Compose the existing detector, delivery, joining and descriptive measurements."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray
from PIL import Image

from . import lines as detector
from .layout import LayoutProvider, TableRegions, compute_layout
from .options import OutputOptions, PageOptions
from .pixels import _gray
from .records import BookResult, PageResult
from .statistics import book_statistics, corpus_statistics, page_statistics
from .structure import joining_result
from .tables import prepare_delivery

__all__ = ['process_page', 'process_book']
PageImage = Image.Image | NDArray[Any] | str | Path


def _key(value: str) -> str:
    if not value or value in ('.', '..') or Path(value).name != value or '\\' in value:
        raise ValueError('page_key and book_id must be filename stems')
    return value


def _load(image: PageImage) -> Image.Image | NDArray[Any]:
    if isinstance(image, (str, Path)):
        with Image.open(image) as opened:
            return opened.copy()
    return image


def _drop_discounted(segmentation: detector.PageSegmentation, pieces: list) -> None:
    """Compact line indices and all links; retain original stable address IDs."""
    keep = {i: j for j, i in enumerate(i for i, line in enumerate(segmentation.lines)
                                     if line.discounted is None)}
    segmentation.lines = [line for line in segmentation.lines if line.discounted is None]
    for line in segmentation.lines:
        for key, values in line.neighbours.items():
            if key in ('above', 'below'):
                line.neighbours[key] = np.asarray([keep.get(int(v), -1) for v in values])
            else:
                line.neighbours[key] = keep.get(values)
    for piece in pieces:
        piece.line_index = keep[piece.line_index]
    for name in ('columns', 'blocks', 'rows'):
        records = segmentation.structure[name]
        for record in records:
            record['line_indices'] = [keep[i] for i in record['line_indices'] if i in keep]
        segmentation.structure[name] = [r for r in records if r['line_indices']]
    for name in ('violations', 'crossing_evidence'):
        records = segmentation.structure[name]
        segmentation.structure[name] = [dict(r, line_index=keep[r['line_index']])
                                       for r in records if r['line_index'] in keep]
    def remap_evidence(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == 'line_index':
                    value[key] = keep.get(item)
                else:
                    remap_evidence(item)
        elif isinstance(value, list):
            for item in value:
                remap_evidence(item)
    # Boundaries contain supporting-line references independent of their IDs.
    for name in ('boundaries', 'rejected_boundaries'):
        remap_evidence(segmentation.structure[name])
    for column in segmentation.structure['columns']:
        remap_evidence(column['left_boundary'])
        remap_evidence(column['right_boundary'])
    table_delivery = segmentation.diagnostics.get('table_delivery')
    segmentation.diagnostics = detector._diagnostics(segmentation.pixels, segmentation.lines)
    if table_delivery is not None:
        segmentation.diagnostics['table_delivery'] = table_delivery


def process_page(image: PageImage, *, options: PageOptions = PageOptions(),
                 page_key: str | None = None, book_id: str | None = None,
                 table_regions: TableRegions | None = None,
                 layout_provider: LayoutProvider | None = None,
                 page_size: Sequence[float] | None = None,
                 recognizer: Any = None) -> PageResult:
    """Analyse one raster; optional layout, orientation, joining, statistics and files."""
    page_key = _key(page_key or (Path(image).stem if isinstance(image, (str, Path)) else 'page'))
    if book_id is not None:
        _key(book_id)
    source = _load(image)
    # The same Q2 conversion validates arrays before layout or detection runs.
    gray = _gray(source)
    height, width = gray.shape
    size = tuple(page_size) if page_size is not None else (width, height)
    if len(size) != 2 or not np.isfinite(size).all() or min(size) <= 0:
        raise ValueError('page_size must contain two finite positive dimensions')
    regions = []
    if options.tables:
        if table_regions is not None and layout_provider is not None:
            raise ValueError('Supply table_regions or layout_provider, not both')
        if table_regions is None:
            raster = source if isinstance(source, Image.Image) else Image.fromarray(
                np.clip(gray, 0, 255).astype(np.uint8))
            regions = list((layout_provider or compute_layout)(raster))
        else:
            regions = list(table_regions)
    elif table_regions is not None or layout_provider is not None:
        raise ValueError('Layout input requires tables=True')
    for identity, box in regions:
        if len(box) != 4 or not np.isfinite(box).all() or box[2] <= box[0] or box[3] <= box[1]:
            raise ValueError(f'Invalid table region: {identity}')
    segmentation = detector.segment_page(source)
    if options.strict_geometry and any(
            not np.isfinite(line.top).all() or not np.isfinite(line.bottom).all()
            or np.any(line.bottom <= line.top)
            for line in segmentation.lines if line.discounted is None):
        raise ValueError('invalid_line_geometry')
    segmentation, pieces, regions = prepare_delivery(source, segmentation, regions, supplement=options.tables)
    if options.discounted == 'drop':
        _drop_discounted(segmentation, pieces)
    oriented = None
    if options.orientation:
        from ..glyphs.oriented_page import oriented_page
        raster = source if isinstance(source, Image.Image) else Image.fromarray(
            np.clip(segmentation.pixels.gray, 0, 255).astype(np.uint8))
        oriented = oriented_page(raster, regions, recognizer=recognizer,
                                 segmentation=segmentation, pieces=pieces, supplement=options.tables)
    lines = [line.to_record() for line in segmentation.lines]
    joining = (joining_result(lines, structure=segmentation.structure,
                              pieces=[p.to_record(i, (width, height), size) for i, p in enumerate(pieces)],
                              granularity=options.granularity) if options.join_lines else None)
    delivered = joining['rows'] if joining is not None else [l for l in lines if l['discounted'] is None]
    measured = (page_statistics(source, lines, page_key=page_key, book_id=book_id,
                                structure=segmentation.structure) if options.statistics else None)
    result = PageResult(page_key, book_id, (width, height), size, options, segmentation,
                        lines, pieces, delivered, measured, oriented, regions, joining=joining)
    if options.outputs.directory is not None:
        from .outputs import write_page
        result.files = write_page(result, source, options.outputs)
    return result


def process_book(pages: Iterable[PageImage | PageResult], *, book_id: str,
                 options: PageOptions = PageOptions(),
                 table_regions: Mapping[str, TableRegions] | None = None,
                 layout_provider: LayoutProvider | None = None,
                 page_size: Sequence[float] | None = None,
                 recognizer: Any = None) -> BookResult:
    """Process ordered pages, then apply Q2 leave-one-page-out book statistics."""
    _key(book_id)
    results = []
    sources = []
    keys = set()
    for index, page in enumerate(pages):
        if isinstance(page, PageResult):
            result = page
            if result.book_id != book_id:
                raise ValueError('Book identity mismatch')
            if options.statistics and result.statistics is None:
                raise ValueError('Book statistics require measured page results')
            source = None
        else:
            key = Path(page).stem if isinstance(page, (str, Path)) else f'page-{index:05d}'
            source = _load(page)
            result = process_page(source, options=replace(options, outputs=OutputOptions()),
                                  page_key=key, book_id=book_id,
                                  table_regions=table_regions.get(key) if table_regions is not None else None,
                                  layout_provider=layout_provider, page_size=page_size, recognizer=recognizer)
        if result.page_key in keys:
            raise ValueError('Duplicate pages would bias book statistics')
        keys.add(result.page_key)
        results.append(result)
        sources.append(source)
    stats = corpus = None
    if options.statistics:
        measured = book_statistics([p.statistics for p in results], book_id=book_id)
        # Do not overwrite a caller's page measurement when enriching a book.
        results = [replace(page, statistics=measurement) for page, measurement in zip(results, measured['pages'])]
        stats = measured['stats']
        corpus = corpus_statistics([p.statistics for p in results])
    book = BookResult(book_id, results, stats, corpus)
    if options.outputs.directory is not None:
        from .outputs import write_book, write_page
        for result, source in zip(results, sources):
            result.files = write_page(result, source, options.outputs)
        book.files = write_book(book, options.outputs)
    return book

"""Reproduce the pixel-only development review and its machine-readable checks.

Run from the repository root: python scripts/glyphs/render_page_line_segments.py
The input directory is never modified; outputs go under .astra/out by default.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from greekocr.pages import process_page, PageOptions
from greekocr.pages.layout import read_layout
from greekocr.pages.provenance import implementation_sha256
from greekocr.glyphs.page_text_lines import segment_page
from greekocr.glyphs.line_structure import render_structure

def render(page, result, prefix):
    """Compatibility wrapper for the shared Q2 review renderer."""
    from greekocr.pages.render import render_lines
    images = render_lines(page, result)
    images['lines_image'].save(str(prefix) + '.lines.jpg', quality=92)
    images['unrolled_image'].save(str(prefix) + '.unrolled.jpg', quality=94)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pages', type=Path, default=Path('.astra/pages'))
    parser.add_argument('--out', type=Path, default=Path('.astra/out'))
    parser.add_argument('--keys', nargs='*')
    parser.add_argument('--compare-hints', action='store_true', help='also rerun Vouli pages with text-layer box hints')
    parser.add_argument('--layout', type=Path, help='Cached image-only layout predictions for table delivery')
    args = parser.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    implementation = implementation_sha256()
    for path in sorted(args.pages.glob('*.png')):
        if args.keys and path.stem not in args.keys:
            continue
        start = time.perf_counter()
        with Image.open(path) as im:
            page = im.convert('L')
        regions = read_layout(args.layout / f'{path.stem}.json', page.size) if args.layout else None
        analysis = process_page(page, page_key=path.stem, options=PageOptions(tables=args.layout is not None),
                                table_regions=regions)
        result, pieces = analysis.segmentation, analysis.pieces
        comparison = None
        hint_path = path.with_suffix('.boxes.json')
        if args.compare_hints and path.stem.startswith('s2-') and hint_path.exists():
            hints = [row['box'] for row in json.loads(hint_path.read_text())]
            other = segment_page(page, hints=hints)
            same = len(other.lines) == len(result.lines)
            for a, b in zip(result.lines, other.lines):
                same &= (a.x0, a.x1, a.column, a.segment_indices) == (b.x0, b.x1, b.column, b.segment_indices)
                same &= all(np.array_equal(getattr(a, k), getattr(b, k))
                            for k in ('baseline', 'font_top', 'meanline', 'font_bottom', 'top', 'bottom'))
            comparison = dict(hint_boxes=len(hints), identical_pixel_geometry=bool(same),
                              source_sha256=hashlib.sha256(hint_path.read_bytes()).hexdigest())
            if not same:
                raise AssertionError(f'hints changed pixel geometry: {path.stem}')
        prefix = args.out / path.stem
        render(page, result, prefix)
        (args.out / f'{path.stem}.structure.json').write_text(json.dumps(result.structure,indent=2))
        render_structure(page,[l.to_record() for l in result.lines],result.structure).save(
            args.out / f'{path.stem}.structure.jpg',quality=92)
        (args.out / f'{path.stem}.segments.json').write_text(json.dumps([
            dict(line_id=f'{path.stem}-s{i:05d}', box=list(box)) for i, box in enumerate(result.segments)]))
        (args.out / f'{path.stem}.lines.json').write_text(json.dumps([l.to_record() for l in result.lines]))
        if pieces is not None:
            (args.out / f'{path.stem}.cells.json').write_text(json.dumps(dict(
                image_size=list(page.size), page_size=[v/3 for v in page.size],
                page_units='research raster page: PNG pixels / 3; plugin uses actual page size',
                cells=[p.to_record(i, page.size, [v/3 for v in page.size]) for i,p in enumerate(pieces)]), indent=2))
        record = dict(key=path.stem, source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                      implementation_sha256=implementation, hint_comparison=comparison,
                      image_size=list(page.size), xheight=result.xheight,
                      seconds=round(time.perf_counter() - start, 2), **result.diagnostics)
        (args.out / f'{path.stem}.checks.json').write_text(json.dumps(record, indent=2))
        print(path.stem, {k: record[k] for k in ('seconds', 'pixel_segments', 'final_lines', 'cut_ink_lines',
                                               'foreign_ink_lines', 'rule_gutter_crossings', 'broken_line_pairs')}, flush=True)
    # Include existing completed pages for resumable foreground runs.
    records = [json.loads(p.read_text()) for p in sorted(args.out.glob('*.checks.json'))]
    (args.out / 'checks.json').write_text(json.dumps(records, indent=2))


if __name__ == '__main__':
    main()

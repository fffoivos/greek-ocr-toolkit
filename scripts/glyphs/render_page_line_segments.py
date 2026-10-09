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
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from greekocr.glyphs.page_text_lines import _extract, segment_page

COLORS = [(204, 44, 58), (26, 118, 180), (25, 143, 92), (159, 65, 178)]


def render(page, result, prefix):
    overlay = Image.new('RGBA', page.size)
    d = ImageDraw.Draw(overlay)
    for i, line in enumerate(result.lines):
        if line.discounted is not None:
            continue
        x = np.arange(line.x0, line.x1)
        indices = np.unique(np.r_[np.arange(0, len(x), 3), len(x) - 1])
        color = COLORS[i % len(COLORS)]
        top = [(int(x[k]), float(line.top[k])) for k in indices]
        bottom = [(int(x[k]), float(line.bottom[k])) for k in indices]
        d.polygon(top + bottom[::-1], fill=color + (32,))
        for curve in ('top', 'bottom', 'font_top', 'meanline', 'baseline', 'font_bottom', 'accent_bottom', 'accent_top'):
            points = [(int(x[k]), float(getattr(line, curve)[k])) for k in indices]
            if len(points) < 2:
                continue
            guide_colors = dict(baseline=(220,30,30), meanline=(0,110,235), font_top=(0,150,90),
                                font_bottom=(150,40,190), accent_bottom=(230,120,0), accent_top=(20,170,180))
            stroke = guide_colors.get(curve,(30,30,30))+(220,)
            if curve.startswith('accent'):
                for start in range(0,len(points)-1,4):
                    d.line(points[start:start+2],fill=stroke,width=2)
            else:
                d.line(points,fill=stroke,width=2 if curve=='baseline' else 1)
        d.text((line.x0, float(line.baseline[0]) - line.xheight), str(i)+(' [discounted]' if line.discounted else ''), fill=(0, 0, 0, 255))
    Image.alpha_composite(page.convert('RGBA'), overlay).convert('RGB').save(str(prefix) + '.lines.jpg', quality=92)
    active = [(i, line) for i, line in enumerate(result.lines) if line.discounted is None]
    strips = [_extract(result.pixels.gray, line, 32) for _, line in active]
    # All strips use the same scale and baseline position. Nothing is squeezed
    # to fit the contact sheet; long strips retain their full width.
    width = max([s.width for s in strips] + [400]) + 70
    # JPEG has a 65500-pixel dimension limit. Wrap long tables into labelled
    # consecutive stacks, top-to-bottom then left-to-right, without rescaling.
    rows = min(300, max(1, len(strips)))
    columns = max(1, int(np.ceil(len(strips) / rows)))
    sheet = Image.new('RGB', (columns * width, rows * 140), 'white'); sd = ImageDraw.Draw(sheet)
    for position, ((i, line), strip) in enumerate(zip(active, strips)):
        x, y = (position // rows) * width, (position % rows) * 140
        sheet.paste(strip, (x + 60, y))
        sd.text((x + 4, y + 50), f'{i}\nc{line.column}'+(' D' if line.discounted else ''), fill=COLORS[i % len(COLORS)])
        sd.line([(x, y + 134), (x + width, y + 134)], fill=(210, 210, 210))
    sheet.save(str(prefix) + '.unrolled.jpg', quality=94)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pages', type=Path, default=Path('.astra/pages'))
    parser.add_argument('--out', type=Path, default=Path('.astra/out'))
    parser.add_argument('--keys', nargs='*')
    parser.add_argument('--compare-hints', action='store_true', help='also rerun Vouli pages with text-layer box hints')
    parser.add_argument('--layout', type=Path, help='Cached image-only layout predictions for table delivery')
    args = parser.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    rows = []
    sources = ['greekocr/glyphs/pixel_segments.py', 'greekocr/glyphs/page_text_lines.py',
               'greekocr/glyphs/table_lines.py', 'greekocr/glyphs/page_font.py',
               'greekocr/glyphs/components.py', 'greekocr/glyphs/baseline.py', __file__]
    implementation_sha256 = hashlib.sha256(b''.join(Path(p).read_bytes() for p in sources)).hexdigest()
    for path in sorted(args.pages.glob('*.png')):
        if args.keys and path.stem not in args.keys:
            continue
        start = time.perf_counter()
        with Image.open(path) as im:
            page = im.convert('L')
        result = segment_page(page)
        pieces = None
        if args.layout:
            from greekocr.glyphs.table_lines import prepare_delivery
            layout = json.loads((args.layout / f'{path.stem}.json').read_text())
            regions = [(str(c['id']), [v*3 for v in c['box']]) for c in layout['retained']]
            result, pieces, _ = prepare_delivery(page, result, regions)
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
        (args.out / f'{path.stem}.segments.json').write_text(json.dumps([
            dict(line_id=f'{path.stem}-s{i:05d}', box=list(box)) for i, box in enumerate(result.segments)]))
        (args.out / f'{path.stem}.lines.json').write_text(json.dumps([l.to_record() for l in result.lines]))
        if pieces is not None:
            (args.out / f'{path.stem}.cells.json').write_text(json.dumps(dict(
                image_size=list(page.size), page_size=[v/3 for v in page.size],
                page_units='research raster page: PNG pixels / 3; plugin uses actual page size',
                cells=[p.to_record(i, page.size, [v/3 for v in page.size]) for i,p in enumerate(pieces)]), indent=2))
        record = dict(key=path.stem, source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                      implementation_sha256=implementation_sha256, hint_comparison=comparison,
                      image_size=list(page.size), xheight=result.xheight,
                      seconds=round(time.perf_counter() - start, 2), **result.diagnostics)
        (args.out / f'{path.stem}.checks.json').write_text(json.dumps(record, indent=2))
        rows.append(record)
        print(path.stem, {k: record[k] for k in ('seconds', 'pixel_segments', 'final_lines', 'cut_ink_lines',
                                               'foreign_ink_lines', 'rule_gutter_crossings', 'broken_line_pairs')}, flush=True)
    # Include existing completed pages for resumable foreground runs.
    records = [json.loads(p.read_text()) for p in sorted(args.out.glob('*.checks.json'))]
    (args.out / 'checks.json').write_text(json.dumps(records, indent=2))


if __name__ == '__main__':
    main()

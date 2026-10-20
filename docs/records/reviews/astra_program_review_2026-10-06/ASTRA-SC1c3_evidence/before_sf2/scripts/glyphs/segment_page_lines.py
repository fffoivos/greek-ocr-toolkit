"""Pixel rough segments (columns, rules, then row valleys), without text-layer boxes.

Usage: segment_page_lines.py PAGE.png OUT.json
The same segmenter starts greekocr.glyphs.page_text_lines.segment_page.
"""
import argparse
import json
from pathlib import Path
import sys

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from greekocr.glyphs.pixel_segments import prepare_pixels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('page', type=Path)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    with Image.open(args.page) as page:
        result = prepare_pixels(page)
    args.out.write_text(json.dumps([
        dict(line_id=f'{args.page.stem}-s{i:05d}', box=[int(v) for v in b])
        for i, b in enumerate(result.boxes)]))
    print(args.page.stem, len(result.boxes), 'pixel segments; x-height', result.xheight)


if __name__ == '__main__':
    main()

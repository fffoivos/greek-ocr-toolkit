"""Independently audit serialized page-line geometry and delivered image files.

This checks all overlapping pairs, including non-neighbours, rather than
assuming that sharing seams implies valid regions. It does not invent visual
ground truth for the scanned pages. Run after render_page_line_segments.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


FIELDS = ('baseline', 'font_top', 'meanline', 'font_bottom', 'top', 'bottom', 'accent_top', 'accent_bottom')


def audit(pages, out):
    records, failures = [], []
    for page in sorted(pages.glob('*.png')):
        key = page.stem
        paths = {suffix: out / f'{key}.{suffix}' for suffix in ('segments.json', 'lines.json', 'checks.json', 'lines.jpg', 'unrolled.jpg')}
        absent = [str(p) for p in paths.values() if not p.is_file()]
        if absent:
            failures.append(dict(key=key, missing=absent)); continue
        record = json.loads(paths['checks.json'].read_text())
        lines = json.loads(paths['lines.json'].read_text())
        segments = json.loads(paths['segments.json'].read_text())
        with Image.open(page) as image:
            width, height = image.size
        assert record['source_sha256'] == hashlib.sha256(page.read_bytes()).hexdigest(), key
        assert record['pixel_segments'] == len(segments) and record['final_lines'] == len(lines), key
        assert len(record['checks']) == 10, (key, 'checks 1-10')
        invalid = []
        for i, line in enumerate(lines):
            a, b = line['x0'], line['x1']
            assert 0 <= a < b <= width, (key, i, 'extent')
            for name in FIELDS:
                line[name] = np.array(line[name])
                assert len(line[name]) == b - a and np.isfinite(line[name]).all(), (key, i, name)
            assert all(0 <= j < len(segments) for j in line['segment_indices']), (key, i, 'provenance')
            assert all(name in line for name in ('borrowed','ink_classes','contrast','discounted')), (key,i,'round3 schema')
            assert line['segment_indices'], (key, i, 'missing provenance')
            assert np.all(line['font_top'] <= line['meanline'] + .002), (key, i, 'font order')
            assert np.all(line['meanline'] < line['baseline']), (key, i, 'font order')
            assert np.all(line['font_bottom'] > line['baseline']), (key, i, 'font order')
            assert np.all(line['accent_top'] < line['accent_bottom']), (key, i, 'accent order')
            assert np.all(line['accent_bottom'] < line['meanline']), (key, i, 'accent order')
            if np.any(line['top'] >= line['bottom']):
                invalid.append(i)
        overlapping = []
        for i, a in enumerate(lines):
            for j, b in enumerate(lines[i + 1:], i + 1):
                if a.get('discounted') is not None or b.get('discounted') is not None:
                    continue
                lo, hi = max(a['x0'], b['x0']), min(a['x1'], b['x1'])
                if hi <= lo:
                    continue
                ai, bi = slice(lo - a['x0'], hi - a['x0']), slice(lo - b['x0'], hi - b['x0'])
                # An actual positive vertical interval common to BOTH regions.
                top = np.maximum(a['top'][ai], b['top'][bi])
                bottom = np.minimum(a['bottom'][ai], b['bottom'][bi])
                if np.any(bottom - top > .002):
                    overlapping.append([i, j])
        for suffix in ('lines.jpg', 'unrolled.jpg'):
            with Image.open(paths[suffix]) as image:
                image.verify()
            with Image.open(paths[suffix]) as image:
                image.load()  # Decode the actual saved JPEG, not only its header.
        with Image.open(paths['lines.jpg']) as image:
            assert image.size == (width, height), key
        with Image.open(paths['unrolled.jpg']) as image:
            assert image.height == max(1, min(300, len(lines))) * 140, key
            row_width = max([int(np.ceil((l['x1']-l['x0'])*32/l['xheight'])) for l in lines]+[400])+70
            assert image.width == max(1,int(np.ceil(len(lines)/300))) * row_width, (key, 'all strip stacks')
        result = dict(key=key, lines=len(lines), invalid_lines=invalid, overlap_pairs=overlapping,
                      files={suffix: dict(bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                             for suffix, path in paths.items()})
        records.append(result)
        if invalid or overlapping:
            failures.append(dict(key=key, invalid_lines=invalid, overlap_pairs=overlapping))
    versions = {json.loads(p.read_text()).get('implementation_sha256') for p in out.glob('*.checks.json')}
    assert len(versions) == 1 and None not in versions, 'mixed implementation versions'
    root = Path(__file__).resolve().parents[2]
    sources = ['greekocr/glyphs/pixel_segments.py', 'greekocr/glyphs/page_text_lines.py',
               'greekocr/glyphs/page_font.py', 'greekocr/glyphs/components.py', 'greekocr/glyphs/baseline.py',
               'scripts/glyphs/render_page_line_segments.py']
    assert versions == {hashlib.sha256(b''.join((root/p).read_bytes() for p in sources)).hexdigest()}, 'stale implementation'
    report = dict(pages=len(records), implementation_sha256=versions.pop(), failures=failures, records=records)
    (out / 'artifact_audit.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(dict(pages=len(records), failures=failures), indent=2))
    return 1 if failures else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pages', type=Path, default=Path('.astra/pages'))
    parser.add_argument('--out', type=Path, default=Path('.astra/out'))
    args = parser.parse_args()
    raise SystemExit(audit(args.pages, args.out))

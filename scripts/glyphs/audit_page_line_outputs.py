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


FIELDS = ('baseline', 'font_top', 'meanline', 'font_bottom', 'top', 'bottom')


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
        invalid = []
        for i, line in enumerate(lines):
            a, b = line['x0'], line['x1']
            assert 0 <= a < b <= width, (key, i, 'extent')
            for name in FIELDS:
                line[name] = np.array(line[name])
                assert len(line[name]) == b - a and np.isfinite(line[name]).all(), (key, i, name)
            assert all(0 <= j < len(segments) for j in line['segment_indices']), (key, i, 'provenance')
            assert line['segment_indices'], (key, i, 'missing provenance')
            assert np.all(line['font_top'] <= line['meanline'] + .002), (key, i, 'font order')
            assert np.all(line['meanline'] < line['baseline']), (key, i, 'font order')
            assert np.all(line['font_bottom'] > line['baseline']), (key, i, 'font order')
            if np.any(line['top'] >= line['bottom']):
                invalid.append(i)
        overlapping = []
        for i, a in enumerate(lines):
            for j, b in enumerate(lines[i + 1:], i + 1):
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
        result = dict(key=key, lines=len(lines), invalid_lines=invalid, overlap_pairs=overlapping,
                      files={suffix: dict(bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                             for suffix, path in paths.items()})
        records.append(result)
        if invalid or overlapping:
            failures.append(dict(key=key, invalid_lines=invalid, overlap_pairs=overlapping))
    versions = {json.loads(p.read_text()).get('implementation_sha256') for p in out.glob('*.checks.json')}
    assert len(versions) == 1 and None not in versions, 'mixed implementation versions'
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

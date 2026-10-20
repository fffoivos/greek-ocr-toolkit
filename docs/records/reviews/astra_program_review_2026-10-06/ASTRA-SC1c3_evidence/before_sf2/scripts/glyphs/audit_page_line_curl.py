"""Check page curves against the owner's frozen curl contact points.

Box coordinates only register the independently selected crop contact points
on the original page. They do not seed, fit, or select the page's line set.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
from PIL import Image


def audit(pages, out):
    key = 's2-49598b2e848ab1f0ee1e-p00001'
    fixture = Path(__file__).resolve().parents[2] / 'tests/glyphs/test_curl.py'
    spec = importlib.util.spec_from_file_location('frozen_curl_contacts', fixture)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    boxes = json.loads((pages / f'{key}.boxes.json').read_text())
    lines = json.loads((out / f'{key}.lines.json').read_text())
    page = np.asarray(Image.open(pages / f'{key}.png').convert('L'))
    result = []
    for number, contacts in module.CONTACTS.items():
        box = next(row['box'] for row in boxes if row['line_id'].endswith(f'-l{number:05d}'))
        a, t, b, bot = box
        crop = np.asarray(Image.open(module.PAGE / f'{key}-l{number:05d}.png').convert('L'))
        assert np.array_equal(page[t:bot, a:b], crop), f'coordinate registration differs for {number}'
        x = np.array([a + p[0] for p in contacts]); y = np.array([t + p[1] for p in contacts])
        candidates = []
        for i, line in enumerate(lines):
            if line.get('discounted') is not None:
                continue
            inside = (x >= line['x0']) & (x < line['x1'])
            if inside.sum() >= len(x) / 2:
                pred = np.interp(x, np.arange(line['x0'], line['x1']), line['baseline'])
                candidates.append((float(np.median(abs(pred[inside] - y[inside]))), i, pred, inside))
        if not candidates:
            result.append(dict(crop=number, matched_line=None)); continue
        _, i, pred, inside = min(candidates, key=lambda c: c[0])
        result.append(dict(crop=number, matched_line=i, contacts=len(x), covered_contacts=int(inside.sum()),
                           median_absolute_error_px=float(np.median(abs(pred[inside] - y[inside]))),
                           max_absolute_error_px=float(np.max(abs(pred[inside] - y[inside])))))
    report = dict(page=key, evidence='Frozen manually selected baseline contacts in tests/glyphs/test_curl.py',
                  lines_sha256=hashlib.sha256((out / f'{key}.lines.json').read_bytes()).hexdigest(),
                  contacts_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),
                  scope='Nearest corresponding detected line; coverage reported separately. Not a text/recall score.',
                  lines=result)
    (out / 'curl_contacts.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pages', type=Path, default=Path('.astra/pages'))
    parser.add_argument('--out', type=Path, default=Path('.astra/out'))
    args = parser.parse_args()
    audit(args.pages, args.out)

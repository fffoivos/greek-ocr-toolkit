"""Probe mirror-histogram ambiguity on retained dev-line crops; no ownership labels."""
import json
from pathlib import Path
import numpy as np
from PIL import Image

PARKED = 's2-6419488b7f8e69fd20da-p00001'


def histogram(pixels, signed):
    gy, gx = np.gradient(pixels.astype(np.float32))
    period = 2 * np.pi if signed else np.pi
    angles = np.arctan2(gy, gx) % period
    h = np.histogram(angles, bins=16, range=(0, period),
                     weights=np.hypot(gx, gy))[0].astype(float)
    return h / max(h.sum(), np.finfo(float).eps)


def main():
    paths = sorted(Path('.astra/pages').glob('*.png'))
    assert len(paths) == 54
    rows = []
    for path in paths:
        if path.stem == PARKED:
            rows.append({'page': path.stem, 'status': 'orientation parked'})
            continue
        lines = json.loads((Path('.astra/fast_lines/ours_lines') /
                            (path.stem + '.lines.json')).read_text())
        candidates = [(i, l) for i, l in enumerate(lines)
                      if not l.get('discounted') and l.get('xheight', 0) > 0
                      and l['x1'] - l['x0'] >= 5 * l['xheight']]
        selected = [candidates[i] for i in np.unique(np.linspace(
            0, len(candidates) - 1, min(8, len(candidates)), dtype=int))] if candidates else []
        with Image.open(path) as image:
            pixels = np.asarray(image.convert('L'))
        crops = []
        for i, line in selected:
            x0, x1 = max(0, int(np.floor(line['x0']))), min(pixels.shape[1], int(np.ceil(line['x1'])))
            y0, y1 = max(0, int(np.floor(min(line['top'])))), min(pixels.shape[0], int(np.ceil(max(line['bottom']))))
            crop = pixels[y0:y1, x0:x1]
            if min(crop.shape) < 2:  # numeric gradient needs adjacent samples
                continue
            crops.append((i, (x0, y0, x1, y1), crop))
        for signed in (False, True):
            hs = [histogram(c, signed) for _, _, c in crops]
            for j, (i, bbox, crop) in enumerate(crops):
                others = [float(np.abs(hs[j] - h).sum()) for k, h in enumerate(hs) if k != j]
                rows.append({'page': path.stem, 'ours_index': i, 'bbox': bbox,
                             'signed': signed, 'status': 'unlabelled crop',
                             'flip_l1': float(np.abs(hs[j] - histogram(crop[:, ::-1], signed)).sum()),
                             'median_other_line_l1': float(np.median(others)) if others else None})
    out = Path('.astra/fast_lines/out/q6_review')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'mirror_histograms.json').write_text(json.dumps(rows, indent=2) + '\n')
    for signed in (False, True):
        r = [x for x in rows if x.get('signed') == signed]
        paired = [x for x in r if x['median_other_line_l1'] is not None]
        print(json.dumps({'signed': signed, 'crops': len(r),
              'median_flip_l1': float(np.median([x['flip_l1'] for x in r])),
              'median_other_line_l1': float(np.median([x['median_other_line_l1'] for x in paired])),
              'flip_not_larger_than_other_lines': sum(x['flip_l1'] <= x['median_other_line_l1'] for x in paired)}))


if __name__ == '__main__':
    main()

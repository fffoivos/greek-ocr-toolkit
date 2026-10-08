"""A simple line segmenter for pages with no text layer (Anemi scans): text columns from the gaps in the ink, then one
segment per text line at the valleys of the row-ink profile. It stands in for the recogniser's segments as the input
of the page-lines procedure (docs/PAGE_LINES_ALGORITHM.md, step 1). Usage: segment_page_lines.py PAGE.png OUT.json"""
import json, sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from greekocr.glyphs.components import binarise                             # noqa: E402

page_path, out = Path(sys.argv[1]), Path(sys.argv[2])
gray = np.asarray(Image.open(page_path).convert('L'), np.float64)
H, W = gray.shape
ink = binarise(gray)
lab, n = ndi.label(ink)
sizes = np.bincount(lab.ravel()); objs = ndi.find_objects(lab)
for i, sl in enumerate(objs, start=1):              # drop frames, rules and scan borders: not text
    if sl is None:
        continue
    h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
    if h > .25 * H or w > .25 * W or sizes[i] < 6:
        ink[sl][lab[sl] == i] = False

# columns: split at blank stretches ≥ 2 % of the width (column gutters, the fold of a two-page spread); keep parts
# ≥ 10 % of the width
col = ndi.uniform_filter1d(ink.mean(axis=0), max(3, W // 200))
thr = .1 * np.percentile(col, 90)
low = col <= thr
cols, x = [], 0
edges = np.diff(np.r_[0, low.astype(np.int8), 0])
starts, ends = np.nonzero(edges == 1)[0], np.nonzero(edges == -1)[0]
seps = [(a_, b_) for a_, b_ in zip(starts, ends) if b_ - a_ >= .02 * W]
cuts = [0] + [int((a_ + b_) / 2) for a_, b_ in seps] + [W]
for a_, b_ in zip(cuts[:-1], cuts[1:]):
    inked = np.nonzero(~low[a_:b_])[0]
    if len(inked) and inked[-1] - inked[0] >= .1 * W:
        cols.append([int(a_ + inked[0]), int(a_ + inked[-1] + 1)])

boxes = []
for c0, c1 in cols:
    prof = ink[:, c0:c1].mean(axis=1)
    sm = ndi.uniform_filter1d(prof, 5)
    x = sm - sm.mean()
    ac = np.correlate(x, x, 'full')[len(x) - 1:]
    lo, hi = 15, min(len(ac) - 1, 250)
    pitch = lo + int(np.argmax(ac[lo:hi])) if hi > lo else 40
    peaks_w = max(3, pitch // 3)
    mx = ndi.maximum_filter1d(sm, 2 * peaks_w + 1)
    centres = [y for y in range(H) if sm[y] == mx[y] and sm[y] > .15 * sm.max()
               and (y == 0 or sm[y] > sm[y - 1])]
    merged = []
    for y in centres:                               # one centre per line: closer than half a pitch → the stronger
        if merged and y - merged[-1] < .5 * pitch:
            if sm[y] > sm[merged[-1]]:
                merged[-1] = y
        else:
            merged.append(y)
    for k, y in enumerate(merged):
        top = int(np.argmin(sm[merged[k - 1]:y]) + merged[k - 1]) if k else max(0, y - pitch // 2)
        bot = int(np.argmin(sm[y:merged[k + 1]]) + y) if k + 1 < len(merged) else min(H, y + pitch // 2)
        band = ink[top:bot, c0:c1]
        xs = np.nonzero(band.any(axis=0))[0]
        if len(xs) < 10 or band.sum() < 50:
            continue
        boxes.append([int(c0 + xs[0]), top, int(c0 + xs[-1] + 1), bot])
key = page_path.stem
rows = [dict(line_id=f'{key}-l{k:05d}', box=b, text='') for k, b in enumerate(sorted(boxes, key=lambda b: (b[0] > W / 2 and len(cols) > 1, b[1])))]
json.dump(rows, open(out, 'w'))
print(key, 'columns', [tuple(c) for c in cols], 'line pitch px ~', pitch, '→', len(rows), 'segments')

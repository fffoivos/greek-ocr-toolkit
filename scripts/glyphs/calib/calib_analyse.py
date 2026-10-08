"""Readability thresholds from the calibration strips: reader CER per strip vs (a) the injected degradation and (b) the
glyph tools' measurement of it. A limit is where the median CER leaves the clean band: clean median CER + max(0.05,
2 × clean IQR) — the line is still read about as well as an undamaged one below it. Usage: calib_analyse.py DIR"""
import json, sys, unicodedata as ud
from collections import defaultdict
from pathlib import Path
import numpy as np

D = Path(sys.argv[1])
man = {json.loads(l)['line_id']: json.loads(l) for l in open(D / 'manifest.jsonl')}
mes = {json.loads(l)['line_id']: json.loads(l) for l in open(D / 'measurements.jsonl')}
pred = {}
for l in open(D / (sys.argv[2] if len(sys.argv) > 2 else 'predictions_cllg.jsonl')):
    r = json.loads(l)
    pred[r.get('line_id') or Path(r.get('crop_path', '')).stem] = r


def norm(t: str) -> str:
    return ud.normalize('NFC', ' '.join((t or '').split()))


def cer(ref: str, hyp: str) -> float:
    a, b = norm(ref), norm(hyp)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1] / max(1, len(a))


rows = []
for lid, m in man.items():
    if lid not in pred:
        continue
    text = pred[lid].get('text') or pred[lid].get('prediction') or ''
    rows.append(dict(m, cer=cer(m['gt_text'], text), **{f'm_{k}': v for k, v in mes.get(lid, {}).items() if k != 'line_id'}))
print(len(rows), 'strips with a reading of', len(man))
clean = np.array([r['cer'] for r in rows if r['degradation'] == 'clean'])
band = float(np.median(clean)) + max(.05, 2 * float(np.subtract(*np.percentile(clean, [75, 25]))))
print('clean CER: median %.3f p75 %.3f → limit band: CER ≤ %.3f' % (np.median(clean), np.percentile(clean, 75), band))
by = defaultdict(list)
for r in rows:
    by[(r['degradation'], r['intensity'])].append(r)
print('\nby injected degradation (median CER, share of strips over the band):')
limits = {}
for kind in ('accent_cut', 'top_cut', 'tail_cut', 'bottom_cut', 'fade', 'thin', 'break', 'thick', 'skew'):
    pts = sorted((k[1], np.median([x['cer'] for x in v]), np.mean([x['cer'] > band for x in v])) for k, v in by.items() if k[0] == kind)
    print('  %-10s ' % kind + '  '.join('%.1f:%.3f/%.0f%%' % (i, c, 100 * f) for i, c, f in pts))
    over = [i for i, c, f in pts if c > band]
    limits[kind] = min(over) if over else None
print('\nfirst injected strength whose median CER leaves the band:', limits)
# against the tools' own measurements (pooled over conditions that drive them)
def curve(key, kinds, edges):
    xs = np.array([r.get(f'm_{key}') for r in rows if r['degradation'] in kinds and r.get(f'm_{key}') is not None], float)
    cs = np.array([r['cer'] for r in rows if r['degradation'] in kinds and r.get(f'm_{key}') is not None], float)
    out = []
    for a, b in zip(edges, edges[1:]):
        sel = (xs >= a) & (xs < b)
        if sel.sum() >= 5:
            out.append((a, b, int(sel.sum()), float(np.median(cs[sel])), float(np.mean(cs[sel] > band))))
    return out
print('\nby the tools\' measurement (bin: n, median CER, share over band):')
for key, kinds, edges in (('accent_cut', ('accent_cut', 'clean'), [0, .05, .1, .2, .3, .4, .5, .6, .7, .8, 1.01]),
                          ('tail_cut', ('tail_cut', 'clean'), [0, .05, .1, .2, .3, .4, .5, .6, .7, .8, 1.01]),
                          ('top_cut', ('top_cut', 'clean'), [0, .05, .1, .15, .2, .25, .3, .35, .4, .5, .6, 1.01]),
                          ('bottom_cut', ('bottom_cut', 'clean'), [0, .05, .1, .15, .2, .25, .3, .35, .4, .5, .6, 1.01]),
                          ('ink_contrast', ('fade', 'clean'), [0, 30, 45, 60, 75, 90, 105, 120, 255]),
                          ('broken', ('break', 'thin', 'clean'), [0, .05, .1, .15, .2, .3, .4, 1.01]),
                          ('merged', ('thick', 'clean'), [0, .1, .2, .3, .4, .5, .6, 1.01])):
    print('  %-12s' % key, '  '.join('[%.2f,%.2f) n%d %.3f/%.0f%%' % (a, b, n, c, 100 * f) for a, b, n, c, f in curve(key, kinds, edges)))
json.dump(dict(band=band, clean_median=float(np.median(clean)), limits=limits), open(D / ('calibration_' + (sys.argv[2] if len(sys.argv) > 2 else 'predictions_cllg.jsonl').replace('predictions_', '').replace('.jsonl', '') + '.json'), 'w'), indent=1)

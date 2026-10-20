"""Read-only independent checks of L1M2 ledgers; writes its own receipt only."""
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPORT = HERE.parents[1] / 'L1M_REPORT.md'
LABELS = ['background', 'own', 'neighbour-above', 'neighbour-below', 'unowned', 'ring-abstained']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name):
    return list(map(json.loads, gzip.open(HERE / name, 'rt')))


def pixel_class(values):
    counts = [int((values == i).sum()) for i in range(6)]
    k = max(range(6), key=lambda i: counts[i])
    cls = LABELS[k] if k and counts[k] / len(values) >= .8 else 'mixed'
    return cls, dict(zip(LABELS, counts))


def main():
    hashes = json.loads((HERE / 'input_hashes.json').read_text())
    for path, digest in hashes.items():
        assert sha(path) == digest, ('input changed', path)
    baseline = json.loads((HERE / 'baseline.json').read_text())
    body = REPORT.read_bytes()
    assert len(body) > baseline['report_bytes']
    assert hashlib.sha256(body[:baseline['report_bytes']]).hexdigest() == baseline['report_prefix_sha256']
    appendix = (HERE / 'appendix.md').read_bytes()
    assert body[baseline['report_bytes']:] == b'\n' + appendix
    assert body.count(b'## L1M2 \xe2\x80\x94') == 1
    assert body.rstrip().splitlines()[-1].startswith(b'L1M2 RESULT: border blobs 2699:')
    blobs, before, after, lines = [load(n) for n in ['border_blobs.jsonl.gz', 'border_flags.jsonl.gz', 'masked_border_flags.jsonl.gz', 'lines.jsonl.gz']]
    assert len(blobs) == 2699 and len(before) == 2947 and len(after) == 862 and len(lines) == 260
    assert len({(b['id'], b['key']) for b in blobs}) == len(blobs)
    assert len({(f['id'], f['start'], f['edge']) for f in before}) == len(before)
    assert len({(f['id'], f['start'], f['edge']) for f in after}) == len(after)
    alignment = {r['id']: r for r in csv.DictReader((HERE / 'alignment.csv').open())}
    bmap = {(b['id'], b['key']): b for b in blobs}
    amap = {(f['id'], f['start'], f['edge']): f for f in after}
    details = {}
    for sample in ['200', 'vouli']:
        details.update({r['id']: r for r in map(json.loads, gzip.open(HERE.parent / sample / 'details.jsonl.gz', 'rt'))})
    checked_pixels = 0
    for line in lines:
        key, sample = line['id'], line['sample']
        omap = np.array(Image.open(alignment[key]['ownership_path']))
        assert not (omap == 5).any()
        with np.load(HERE.parent / sample / 'pixels' / f'{key}.npz') as p:
            oi, mi = p['original_ink'], p['masked_ink']
            ol, ml = p['original_labels'], p['masked_labels']
        for b in [b for b in blobs if b['id'] == key]:
            xx, yy = np.asarray(b['native_pixels']).T
            assert oi[yy, xx].all() and (ol[yy, xx] == b['label']).all()
            attr, counts = pixel_class(omap[yy, xx])
            assert attr == b['attribution'] and counts == b['class_pixels']
            assert sum(counts.values()) == b['pixels']
            assert b['pixels'] == int((ol == b['label']).sum())
            checked_pixels += len(xx)
        bf = [f for f in before if f['id'] == key]
        af = [f for f in after if f['id'] == key]
        for f in bf:
            y = 0 if f['edge'] == 'top' else oi.shape[0] - 1
            lo, hi = f['window']
            xx = np.flatnonzero(oi[y, lo:hi]) + lo
            assert set(ol[y, xx]) == {bmap[(key, k)]['label'] for k in f['blob_keys']}
            classes = {bmap[(key, k)]['attribution'] for k in f['blob_keys']}
            assert f['attribution'] == (next(iter(classes)) if len(classes) == 1 else 'mixed')
            assert f['persists'] == ((key, f['start'], f['edge']) in amap)
            _, counts = pixel_class(omap[y, xx])
            assert f['border_split']['class_pixels'] == counts
        own_keys = set()
        for f in af:
            y = 0 if f['edge'] == 'top' else mi.shape[0] - 1
            lo, hi = f['window']
            xx = np.flatnonzero(mi[y, lo:hi]) + lo
            assert xx.tolist() == f['border_ink_x']
            assert xx[omap[y, xx] == 1].tolist() == f['own_border_x']
            assert f['own_ink_clipping'] == bool(f['sf4_relevant'] and f['own_border_x'])
            reason = 'detector_clipped_' + f['edge']
            slot = next(t for t in details[key]['modes']['masked']['ENSEMBLE_AB']['slots'] if t['start'] == f['start'])
            assert f['sf4_relevant'] == (reason in slot['hold_reasons'])
            if f['own_ink_clipping']:
                own_keys.add((f['start'], reason))
        holds = details[key]['overlays']['masked']['ENSEMBLE_AB']['hold_slots']
        other = [h for h in holds if (h['start'], h['detail']) not in own_keys]
        assert line['remaining_non_own_holds'] == other
        assert line['own_ink_clipping'] == bool(own_keys)
        assert line['sole_remaining_AB_hold'] == bool(own_keys and not other)
    for c in load('padding_components.jsonl.gz'):
        y0, y1 = c['own_bbox'][1], c['own_bbox'][3]
        for m in c['measurements']:
            extent = max(0, m['meanline'] - y0) if c['edge'] == 'top' else max(0, y1 - m['baseline'])
            assert abs(m['extent_px'] - extent) < 1e-9
            assert abs(m['extent_xh'] - extent / m['xh']) < 1e-9
    assert sum(f['persists'] for f in before) + sum(f['new'] for f in after) == len(after)
    assert sum(f['original_sf4_relevant'] for f in before) == 1383
    assert sum(f['sf4_relevant'] for f in after) == 378
    assert sum(f['own_ink_clipping'] for f in after) == 290
    assert sum(l['own_ink_clipping'] for l in lines) == 100
    assert sum(l['sole_remaining_AB_hold'] for l in lines) == 27
    assert sum(l['sole_pure_own_border_hold'] for l in lines) == 25
    selection = json.loads((HERE / 'visual_selection.json').read_text())
    assert len(selection) == len({f['id'] for f in selection}) == 12
    assert Counter(f['category'].split('-')[0] for f in selection) == {'neighbour': 4, 'own': 4, 'mixed': 4}
    review = json.loads((HERE / 'visual_review.json').read_text())
    for path, digest in review['images'].items():
        assert sha(HERE / path) == digest
    assert review['requested_panels_inspected'] == 12 and review['candidate_line_thumbnails_inspected'] == 100
    for target in re.findall(r'\]\(([^)]+)\)', appendix.decode()):
        destination = REPORT.parent / target
        if destination.resolve() != (HERE / 'validation.json').resolve():
            assert destination.exists(), target
    diff = subprocess.check_output(['git', '--no-optional-locks', 'diff', '--name-only'], text=True).splitlines()
    assert set(diff) == set(baseline['initial_tracked_diff']) | {'docs/labelfix/spellcheck/L1M_REPORT.md'}, diff
    receipt = dict(complete=True, input_files_rehashed=len(hashes), lines=260,
        original_blobs=2699, original_flags=2947, masked_flags=862,
        blob_pixel_incidences_independently_checked=checked_pixels,
        original_flag_joins_checked=2947, masked_pixel_queries_checked=862,
        sf4_relevant_flags=[1383, 378], own_contact_flags=290,
        map_based_own_contact_lines=100, nonambiguous_own_contact_lines=98,
        sole_remaining_AB_hold=27, pure_own_only_sole_hold=25,
        class5_pixels=0, report_prefix_preserved=True, report_sha256=sha(REPORT),
        requested_panels_inspected=12, own_candidate_thumbnails_inspected=100,
        network='OFF', reader_runs=0, gate_runs=0, read_ink_runs=0,
        code_change_scope='analysis scripts only in ownership evidence directory',
        tracked_diff_paths=diff)
    (HERE / 'validation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()

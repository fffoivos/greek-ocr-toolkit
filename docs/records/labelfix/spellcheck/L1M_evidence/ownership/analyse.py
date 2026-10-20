"""Local L1M2 accounting. Reuses frozen SF4 decisions; never runs a reader/gate.

PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 \
 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python \
 docs/labelfix/spellcheck/L1M_evidence/ownership/analyse.py

Only this directory is written. ink.analyse + case.estimate_font reconstruct the
crop-wide x-height used by the clipping window (before slot/capital overrides). Its native
ink and labels must equal the saved arrays exactly. No read_ink call is made.
"""
import os
import sys
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
sys.dont_write_bytecode = True

from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
import types
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
SOURCING = Path('/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/v2_masked')
FROZEN = Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck')
sys.path.insert(0, str(FROZEN))
from greekocr.labelfix import ink, case

CLASSES = {0: 'background', 1: 'own', 2: 'neighbour-above',
           3: 'neighbour-below', 4: 'unowned', 5: 'ring-abstained'}
WAVES = ('round1', 'round2', 'mixed', 'vouli')
ATTRS = tuple(CLASSES[i] for i in range(1, 6)) + ('mixed',)
INPUT_HASHES = {}
SOURCE_DRIFT = {}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bind(path, expected=None):
    digest = sha(path)
    if expected is not None:
        assert digest == expected, ('hash mismatch', str(path), digest, expected)
    INPUT_HASHES[str(path)] = digest
    return digest


def readjson(path):
    bind(path)
    return json.loads(Path(path).read_text())


def readrows(path):
    bind(path)
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt') as f:
        return [json.loads(line) for line in f]


def writejson(name, data):
    (HERE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def writerows(name, rows):
    # Fixed gzip timestamp makes the compressed evidence reproducible.
    payload = ''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in rows).encode()
    (HERE / name).write_bytes(gzip.compress(payload, mtime=0))


def writecsv(name, rows):
    with (HERE / name).open('w', newline='') as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                        for k, v in row.items()})


def split(values):
    counts = np.bincount(values, minlength=6)
    n = int(counts.sum())
    assert n
    dominant = int(np.argmax(counts))
    # Background is retained in the denominator. A background-majority native
    # detector blob is mixed/unattributed, never silently promoted to own ink.
    cls = CLASSES[dominant] if dominant and int(counts[dominant]) * 5 >= n * 4 else 'mixed'
    return dict(attribution=cls, pixels=n,
                class_pixels={CLASSES[i]: int(counts[i]) for i in range(6)},
                class_fractions={CLASSES[i]: float(counts[i] / n) for i in range(6)},
                dominant_label=dominant, dominant_fraction=float(counts[dominant] / n))


def flag_class(blobs):
    # Each slot-edge flag is counted once. Different blob classes in the same
    # window stay mixed; a large blob cannot overrule a separate small blob.
    classes = {b['attribution'] for b in blobs}
    return next(iter(classes)) if len(classes) == 1 else 'mixed'


def clipping_window(slot, xh, width):
    b0, b1 = slot['evidence']['body']
    return [max(0, math.floor(b0 - .1 * xh)), min(width, math.ceil(b1 + .2 * xh))]


def stats(values):
    if not values:
        return dict(n=0, median=None, p25=None, p75=None, p90=None, maximum=None)
    a = np.asarray(values)
    return dict(n=len(a), median=float(np.median(a)), p25=float(np.quantile(a, .25)),
                p75=float(np.quantile(a, .75)), p90=float(np.quantile(a, .9)),
                maximum=float(a.max()), zero=int((a == 0).sum()))


def main():
    started = time.monotonic()
    blobrows, flagrows, afterrows, lineout, components, alignment = [], [], [], [], [], []
    exceptions = []
    for sample, tree in [('200', 'l1e_sample_r4'), ('vouli', 'l1e_sample_vouli_r2')]:
        eroot, root = EVIDENCE / sample, SOURCING / tree
        receipt = readjson(eroot / 'receipt.json')
        assert receipt['source_binding']['policy']['schema'] == 'sf4-release-v1'
        for path, digest in receipt['source_binding']['sources'].items():
            current = bind(FROZEN / path)
            if current != digest:
                # These are not imported or executed. Verify the historical
                # binding read-only against the original committed source.
                committed = subprocess.check_output(['git', '--no-optional-locks', 'show',
                    receipt['source_binding']['commit'] + ':' + path], cwd=FROZEN)
                assert hashlib.sha256(committed).hexdigest() == digest
                SOURCE_DRIFT[path] = dict(recorded_sha256=digest, current_sha256=current,
                                          imported=False, executed=False)
                if path == 'greekocr/labelfix/text.py':
                    # markshape.load_model imports text constants indirectly.
                    # Load the exact historical utilities in memory; do not
                    # alter either worktree or import the current text code.
                    name = 'greekocr.labelfix.text'
                    module = types.ModuleType(name)
                    module.__file__ = '<L1M2-historical>/' + path
                    module.__package__ = 'greekocr.labelfix'
                    sys.modules[name] = module
                    exec(compile(committed, module.__file__, 'exec'), module.__dict__)
                    SOURCE_DRIFT[path]['historical_loaded_in_memory'] = True
        for path, digest in receipt['outputs'].items():
            bind(eroot / path, digest)
        case.configure_model(FROZEN / 'docs/labelfix/case_model_S5.json')
        sr_receipt = readjson(root / 'receipt.json')
        bind(root / 'lines.jsonl', sr_receipt['lines_sha256'])
        sr = {r['id']: r for r in readrows(root / 'lines.jsonl')}
        comparison = readjson(root / 'comparison.json')
        oldroot = Path(comparison['directory'])
        bind(oldroot / 'lines.jsonl', comparison['lines_sha256'])
        assert comparison['lines_sha256'] == receipt['staging_lines_sha256']
        oldsr = {r['id']: r for r in readrows(oldroot / 'lines.jsonl')}
        lines = readrows(eroot / 'lines.jsonl.gz')
        details = {r['id']: r for r in readrows(eroot / 'details.jsonl.gz')}
        before_flags = readrows(eroot / 'border_flags.jsonl.gz')
        before_blobs = readrows(eroot / 'border_blobs.jsonl.gz')
        assert set(sr) == set(oldsr) == set(details) == {r['id'] for r in lines}
        byblob, byflag = defaultdict(list), defaultdict(list)
        for b in before_blobs:
            byblob[b['id']].append(b)
        for f in before_flags:
            byflag[f['id']].append(f)
        for line in lines:
            key, wave = line['id'], line['wave']
            s, old, d = sr[key], oldsr[key], details[key]
            assert s['original_crop_sha256'] == old['original_crop_sha256'] == line['source']['original_crop_sha256']
            assert s['masked_sha256'] == old['masked_sha256'] == line['source']['masked_sha256']
            assert s['crop_box'] == old['crop_box'] == line['source']['crop_box']
            original, masked = Path(s['original_path']), root / s['masked_path']
            bind(original, s['original_crop_sha256'])
            bind(masked, s['masked_sha256'])
            bind(oldroot / old['masked_path'], s['masked_sha256'])
            assert comparison['records'][key]['masked_sha256'] == s['masked_sha256']
            ownpath = root / s['ownership_path']
            bind(ownpath, s['ownership_sha256'])
            with Image.open(ownpath) as im:
                assert im.mode == 'L', (key, im.mode)
                omap = np.array(im)
            with Image.open(original) as im:
                orig_img = im.convert('L')
            with Image.open(masked) as im:
                masked_img = im.convert('L')
            arr, marr = np.array(orig_img), np.array(masked_img)
            assert omap.shape == arr.shape == marr.shape
            assert set(np.unique(omap)) <= set(CLASSES)
            assert {str(i): int((omap == i).sum()) for i in CLASSES} == s['ownership_checks']['class_pixels']
            mask = np.isin(omap, [2, 3, 4])
            assert hashlib.sha256(mask.tobytes()).hexdigest() == s['mask_sha256']
            assert not ((arr != marr) & ~mask).any(), (key, 'changed outside mask')
            bind(eroot / 'pixels' / f'{key}.npz')
            with np.load(eroot / 'pixels' / f'{key}.npz') as p:
                original_ink, masked_ink = p['original_ink'], p['masked_ink']
                original_labels, masked_labels = p['original_labels'], p['masked_labels']
                assert omap.shape == original_ink.shape == masked_ink.shape
            # Reconstruct only ink/labels/xh; decisions and letter evidence are saved.
            cis = [ink.analyse(img) for img in (orig_img, masked_img)]
            for ci in cis:
                case.estimate_font(ci)
            for ci, bi, labels in zip(cis, [original_ink, masked_ink], [original_labels, masked_labels]):
                assert np.array_equal(ci.ink, bi), (key, 'native ink drift')
                assert np.array_equal(ci.labels, labels), (key, 'native labels drift')
            h, w = arr.shape
            alignment.append(dict(id=key, wave=wave, sample=sample, shape=[h, w],
                original_sha256=s['original_crop_sha256'], masked_sha256=s['masked_sha256'],
                ownership_sha256=s['ownership_sha256'], ownership_path=str(ownpath),
                export_status=s['ownership_export_status'], keep_basis=s['ownership_checks']['keep_basis'],
                original_crop_xh=cis[0].xh, masked_crop_xh=cis[1].xh,
                ring_pixels=int((omap == 5).sum()),
                r3_or_vouli_crop_byte_identical=True, native_arrays_exact=True))
            bmap = {}
            for b in byblob[key]:
                xx, yy = np.asarray(b['native_pixels']).T
                assert (original_labels[yy, xx] == b['label']).all()
                assert len(xx) == int((original_labels == b['label']).sum())
                y = 0 if b['edge'] == 'top' else h - 1
                z = dict(id=key, wave=wave, sample=sample, key=b['key'], edge=b['edge'],
                         label=b['label'], bbox=b['bbox'], **split(omap[yy, xx]),
                         edge_split=split(omap[y, b['edge_x']]),
                         native_pixels=b['native_pixels'],
                         original_edge_x=b['edge_x'],
                         surviving_edge_x=[x for x in b['edge_x'] if masked_ink[y, x]],
                         ownership_export_status=s['ownership_export_status'])
                bmap[b['key']] = z
                blobrows.append(z)
            oslots = {t['start']: t for t in d['detector']['original']['slots']}
            mslots = {t['start']: t for t in d['detector']['masked']['slots']}
            ogate = {t['start']: t for t in d['modes']['original']['ENSEMBLE_AB']['slots']}
            mgate = {t['start']: t for t in d['modes']['masked']['ENSEMBLE_AB']['slots']}
            original_keys = {(f['start'], f['edge']) for f in byflag[key]}
            for f in byflag[key]:
                lo, hi = clipping_window(oslots[f['start']], cis[0].xh, w)
                assert [lo, hi] == f['window'], (key, f['start'], cis[0].xh, [lo, hi], f['window'], oslots[f['start']]['evidence'])
                y = 0 if f['edge'] == 'top' else h - 1
                xx = np.flatnonzero(original_ink[y, lo:hi]) + lo
                assert xx.tolist() == f['border_ink_x']
                bs = [bmap[k] for k in f['blob_keys']]
                cls = flag_class(bs)
                reason = 'detector_clipped_' + f['edge']
                persisted = bool(mslots.get(f['start'], {}).get('evidence', {}).get('clipped_' + f['edge']))
                assert persisted == f['persists']
                survivor_x = xx[masked_ink[y, xx]]
                masked_window = (clipping_window(mslots[f['start']], cis[1].xh, w)
                                 if mslots.get(f['start'], {}).get('evidence') else None)
                z = dict(id=key, wave=wave, sample=sample, start=f['start'], base=f['base'],
                    edge=f['edge'], window=f['window'], blob_keys=f['blob_keys'],
                    attribution=cls, blob_classes=[b['attribution'] for b in bs],
                    border_split=split(omap[y, xx]), persists=persisted,
                    masked_window=masked_window,
                    window_changed=masked_window != f['window'],
                    original_border_pixels_surviving=survivor_x.tolist(),
                    surviving_original_border_split=split(omap[y, survivor_x]) if len(survivor_x) else None,
                    original_sf4_relevant=reason in ogate[f['start']]['hold_reasons'],
                    masked_sf4_hold=reason in mgate.get(f['start'], {}).get('hold_reasons', []),
                    ownership_export_status=s['ownership_export_status'])
                flagrows.append(z)
                expected = {'own', 'ring-abstained'} if persisted else {'neighbour-above', 'neighbour-below', 'unowned'}
                if cls not in expected:
                    exceptions.append(dict(**z, exception='persistent_non_own_or_ring' if persisted else 'cleared_non_neighbour_or_unowned'))
            after_for_line, own_components = [], {}
            for slot in mslots.values():
                ev = slot.get('evidence', {})
                for edge, y in [('top', 0), ('bottom', h - 1)]:
                    if not ev.get('clipped_' + edge):
                        continue
                    lo, hi = clipping_window(slot, cis[1].xh, w)
                    xx = np.flatnonzero(masked_ink[y, lo:hi]) + lo
                    assert len(xx)
                    labels = sorted(int(a) for a in set(masked_labels[y, xx]))
                    assert 0 not in labels
                    bs = []
                    for label in labels:
                        yy2, xx2 = np.nonzero(masked_labels == label)
                        bs.append(dict(label=label, bbox=[int(xx2.min()), int(yy2.min()), int(xx2.max()) + 1, int(yy2.max()) + 1],
                                       **split(omap[yy2, xx2])))
                    own_x = xx[omap[y, xx] == 1]
                    reason = 'detector_clipped_' + edge
                    relevant = reason in mgate[slot['start']]['hold_reasons']
                    z = dict(id=key, wave=wave, sample=sample, start=slot['start'], base=slot['base'], edge=edge,
                        window=[lo, hi], border_ink_x=xx.tolist(), blob_classes=[b['attribution'] for b in bs],
                        blobs=bs, attribution=flag_class(bs), border_split=split(omap[y, xx]),
                        sf4_relevant=relevant, own_border_x=own_x.tolist(),
                        own_ink_clipping=bool(relevant and len(own_x)),
                        new=(slot['start'], edge) not in original_keys,
                        ownership_export_status=s['ownership_export_status'])
                    afterrows.append(z)
                    after_for_line.append(z)
                    if relevant and len(own_x):
                        # Ownership-restricted native components: retain only class 1,
                        # preventing a fused foreign portion from inflating the extent.
                        for label in sorted(set(int(v) for v in masked_labels[y, own_x])):
                            yy2, xx2 = np.nonzero((masked_labels == label) & (omap == 1))
                            ckey = (edge, label)
                            extent = max(0., ev['meanline'] - int(yy2.min())) if edge == 'top' else max(0., int(yy2.max()) + 1 - ev['baseline'])
                            measure = dict(start=slot['start'], base=slot['base'], meanline=ev['meanline'],
                                baseline=ev['baseline'], xh=ev['xh'], band_source=ev.get('band_source'),
                                extent_px=extent, extent_xh=extent / ev['xh'])
                            if ckey not in own_components:
                                own_components[ckey] = dict(id=key, wave=wave, sample=sample, edge=edge, label=label,
                                    own_pixels=len(xx2), own_bbox=[int(xx2.min()), int(yy2.min()), int(xx2.max()) + 1, int(yy2.max()) + 1],
                                    measurements=[], ownership_export_status=s['ownership_export_status'])
                            own_components[ckey]['measurements'].append(measure)
            holds = d['overlays']['masked']['ENSEMBLE_AB']['hold_slots']
            own_keys = {(f['start'], 'detector_clipped_' + f['edge']) for f in after_for_line if f['own_ink_clipping']}
            other = [t for t in holds if (t['start'], t['detail']) not in own_keys]
            assert bool(holds) == (line['status']['masked']['ENSEMBLE_AB'] == 'hold')
            # A stricter policy-only rescue additionally requires every border ink
            # pixel of every remaining hold to be class 1 (no ring/background residue).
            all_pure_own = bool(own_keys) and not other and all(
                f['border_split']['class_pixels']['own'] == f['border_split']['pixels']
                for f in after_for_line if f['sf4_relevant'])
            for c in own_components.values():
                c['extent_px'] = max(t['extent_px'] for t in c['measurements'])
                c['extent_xh'] = max(t['extent_xh'] for t in c['measurements'])
                components.append(c)
            lineout.append(dict(id=key, wave=wave, sample=sample, ownership_export_status=s['ownership_export_status'],
                own_ink_clipping=bool(own_keys), own_ink_flags=len(own_keys),
                sf4_clipping_flags=sum(f['sf4_relevant'] for f in after_for_line),
                sole_remaining_AB_hold=bool(own_keys) and not other,
                sole_pure_own_border_hold=all_pure_own,
                remaining_non_own_holds=other,
                masked_AB_status=line['status']['masked']['ENSEMBLE_AB'],
                extent_px=max((c['extent_px'] for c in own_components.values()), default=None),
                extent_xh=max((c['extent_xh'] for c in own_components.values()), default=None)))
        print(f'{sample}: verified {len(lines)} crops and all native arrays', flush=True)
    assert len(alignment) == 260 and len(blobrows) == 2699 and len(flagrows) == 2947 and len(afterrows) == 862
    assert sum(f['new'] for f in afterrows) == 14
    # Verify all runtime imports match sources bound by the paired run.
    for mod in list(sys.modules.values()):
        path = getattr(mod, '__file__', None)
        if path and str(path).startswith(str(FROZEN) + '/') and str(path).endswith('.py'):
            assert str(Path(path)) in INPUT_HASHES, ('unbound imported source', path)
            relative = str(Path(path).relative_to(FROZEN))
            assert relative not in SOURCE_DRIFT, ('imported source drift', relative)
    transition_table, independent_table = [], []
    for wave in WAVES:
        for edge in ('top', 'bottom'):
            ff = [f for f in flagrows if f['wave'] == wave and f['edge'] == edge]
            aa = [f for f in afterrows if f['wave'] == wave and f['edge'] == edge]
            for cls in ATTRS:
                subset = [f for f in ff if f['attribution'] == cls]
                transition_table.append(dict(wave=wave, edge=edge, attribution=cls,
                    before=len(subset), same_slot_after=sum(f['persists'] for f in subset),
                    cleared=sum(not f['persists'] for f in subset),
                    sf4_before=sum(f['original_sf4_relevant'] for f in subset),
                    sf4_same_slot_after=sum(f['masked_sf4_hold'] for f in subset)))
                after = [f for f in aa if f['attribution'] == cls]
                independent_table.append(dict(wave=wave, edge=edge, attribution=cls,
                    before=len(subset), after=len(after), new_after=sum(f['new'] for f in after),
                    sf4_after=sum(f['sf4_relevant'] for f in after)))
    bywave = {}
    for wave in [*WAVES, '200', 'ALL']:
        ls = [l for l in lineout if wave == 'ALL' or l['wave'] == wave or l['sample'] == wave]
        cs = [c for c in components if wave == 'ALL' or c['wave'] == wave or c['sample'] == wave]
        bywave[wave] = dict(n=len(ls), own_ink_clipping_lines=sum(l['own_ink_clipping'] for l in ls),
            sole_remaining_AB_hold=sum(l['sole_remaining_AB_hold'] for l in ls),
            sole_pure_own_border_hold=sum(l['sole_pure_own_border_hold'] for l in ls),
            own_ink_flags=sum(l['own_ink_flags'] for l in ls),
            qualified_own_lines=sum(l['own_ink_clipping'] and l['ownership_export_status'] != 'identity_ambiguous' for l in ls),
            qualified_sole_hold=sum(l['sole_remaining_AB_hold'] and l['ownership_export_status'] != 'identity_ambiguous' for l in ls),
            padding_per_line_xh=stats([l['extent_xh'] for l in ls if l['own_ink_clipping']]),
            padding_per_line_px=stats([l['extent_px'] for l in ls if l['own_ink_clipping']]),
            padding_per_component_xh=stats([c['extent_xh'] for c in cs]),
            padding_per_component_px=stats([c['extent_px'] for c in cs]))
    summary = dict(schema='l1m2-ownership-v1', lines=260, border_blobs=len(blobrows),
        blob_attribution=dict(Counter(b['attribution'] for b in blobrows)),
        flag_attribution_before=dict(Counter(f['attribution'] for f in flagrows)),
        flag_attribution_after=dict(Counter(f['attribution'] for f in afterrows)),
        ring_flags_before=sum('ring-abstained' in f['blob_classes'] for f in flagrows),
        ring_flags_after=sum('ring-abstained' in f['blob_classes'] for f in afterrows),
        ring_pixels_all_maps=sum(a['ring_pixels'] for a in alignment),
        exception_types=dict(Counter(f['exception'] for f in exceptions)),
        exception_attribution={kind: dict(Counter(f['attribution'] for f in exceptions if f['exception'] == kind))
                               for kind in ('persistent_non_own_or_ring', 'cleared_non_neighbour_or_unowned')},
        by_wave=bywave, seconds=time.monotonic() - started,
        policy='sf4-release-v1', reader_runs=0, read_ink_runs=0, gate_runs=0,
        source_drift_current_code_not_executed=SOURCE_DRIFT,
        native_ink_geometry_reconstructions=520, network='OFF', workers=1, threads=1)
    writerows('border_blobs.jsonl.gz', blobrows)
    writerows('border_flags.jsonl.gz', flagrows)
    writerows('masked_border_flags.jsonl.gz', afterrows)
    writerows('exceptions.jsonl.gz', exceptions)
    writerows('padding_components.jsonl.gz', components)
    writerows('lines.jsonl.gz', lineout)
    writecsv('flag_transitions.csv', transition_table)
    writecsv('flag_counts_independent.csv', independent_table)
    writecsv('alignment.csv', alignment)
    writecsv('lines.csv', lineout)
    writejson('summary.json', summary)
    writejson('input_hashes.json', INPUT_HASHES)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

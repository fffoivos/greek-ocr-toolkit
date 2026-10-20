"""T4b offline feature extraction, calibration, and admission-only screening.

Run with PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/harvest/screen_v1/screen.py extract
All outputs are confined to this directory. No network or reader imports.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import gzip
import json
import math
from pathlib import Path
import random
import statistics
import sys
import time
import unicodedata as ud
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d, label as connected_labels, find_objects
from scipy.signal import find_peaks
from assembly_fix import assemble_line, page_tokens, spans, normalise

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
TRACKS = {t: (ROOT if t == 'gr' else ROOT.parent / ('greek-ocr-toolkit-sol-funnel-'+t)) / 'docs/harvest/sample_v1' / t for t in ('ia', 'intl', 'gr')}
BLIND = ROOT / 'docs/harvest/blind_checks_v1'
SEED = 20261016


def rows(path):
    path = Path(path)
    if not path.exists() and Path(str(path)+'.gz').exists():
        path = Path(str(path)+'.gz')
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt') as f:
        return [json.loads(s) for s in f if s.strip()]


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def write_rows(path, values):
    with path.open('w') as f:
        for v in values:
            f.write(json.dumps(v, ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n')


def sha(path):
    h = hashlib.sha256()
    path = Path(path)
    fallback = not path.exists() and Path(str(path)+'.gz').exists()
    opener = gzip.open if fallback else open
    if fallback:
        path = Path(str(path)+'.gz')
    with opener(path, 'rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def bind_cards():
    cards = []
    for f in sorted(BLIND.glob('*_labels_*.jsonl')):
        track, source = f.stem.split('_labels_', 1)
        base = TRACKS[track]
        if track == 'gr':
            keypath = base/'label_cards'/f'{source}_key.json'
            key = {r['card']: r for r in json.loads(keypath.read_text())}
        elif track == 'intl':
            keypath = base/'label_cards_keys'/f'{source}.json'
            key = json.loads(keypath.read_text())['cards']
        else:
            keypath = base/'label_cards_key.json'
            key = {k.split('/')[1]: v for k, v in json.loads(keypath.read_text()).items() if k.startswith(source+'/')}
        for v in rows(f):
            b = key[v['card_id']]
            cards.append(dict(v, track=track, source=source, id=b.get('line_id', b.get('id')),
                              verdict_path=str(f), key_path=str(keypath)))
    # Exactly 20 calibration and 20 test cards per source. No outcome stratification.
    for group in sorted({(c['track'], c['source']) for c in cards}):
        cc = sorted([c for c in cards if (c['track'], c['source']) == group], key=lambda c: c['card_id'])
        random.Random(str(SEED)+':'+':'.join(group)).shuffle(cc)
        for i, c in enumerate(cc):
            c['split'] = 'calibration' if i < len(cc)//2 else 'test'
    assert len(cards) == 640
    return cards


def pixel_features(crop, fallback_xheight):
    a = np.asarray(crop.convert('L'))
    # Fixed robust dark-ink threshold; no OCR and no additional page segmentation.
    lo, hi = np.percentile(a, [5, 90])
    threshold = min(200., (float(lo)+float(hi))/2)
    ink = a < threshold
    # Estimate body height solely from this existing crop, never G1b's row
    # detector or measurements outside the crop. Accent/noise components and
    # very wide/tall rules are excluded by fixed, unsupervised shape criteria.
    labels, _ = connected_labels(ink)
    heights = []
    for obj in find_objects(labels):
        if obj is None:
            continue
        h, w = obj[0].stop-obj[0].start, obj[1].stop-obj[1].start
        if max(3., a.shape[0]*.12) <= h <= a.shape[0]*.90 and .12 <= w/h <= 3. and w <= max(6., a.shape[1]*.25):
            heights.append(h)
    xheight = float(statistics.median(heights)) if len(heights)>=3 else max(1.,float(fallback_xheight))
    xheight_method = 'crop_component_median_body_height_proxy' if len(heights)>=3 else 'google_token_height_half_fallback'
    ym = ink.sum(axis=1).astype(float)
    xm = ink.sum(axis=0).astype(float)
    nonzero = np.flatnonzero(xm > 0)
    width = int(nonzero[-1]-nonzero[0]+1) if len(nonzero) else 0
    smoothed = gaussian_filter1d(ym, max(.6, xheight*.12))
    peaks, props = find_peaks(np.pad(smoothed, 1), distance=max(2, xheight*.7),
                             prominence=max(2., smoothed.max()*.18), height=max(2., smoothed.max()*.20))
    peaks = peaks-1
    # Internal low-ink run with >=10% ink on either side. Margins never count.
    gap = 0
    cum = np.cumsum(xm)
    if len(nonzero) and cum[-1] > 0:
        low = xm <= max(0., float(np.median(xm[xm > 0]))*.08)
        start = None
        for i in range(int(nonzero[0]), int(nonzero[-1])+2):
            if i < len(low) and low[i]:
                if start is None:
                    start = i
            elif start is not None:
                if cum[max(0, start-1)] >= cum[-1]*.10 and cum[-1]-cum[min(i, len(cum)-1)] >= cum[-1]*.10:
                    gap = max(gap, i-start)
                start = None
    return dict(xheight=xheight, xheight_method=xheight_method, body_component_count=len(heights),
                ink_width=width, ink_pixels=int(ink.sum()), projection_peaks=int(len(peaks)),
                projection_peak_y=peaks.tolist(), internal_gap_xh=gap/max(1., xheight),
                crop_height_xh=a.shape[0]/max(1., xheight))


def token_features(tokens, xheight):
    tt = [t for t in tokens if t['bbox'] and any(c.isalnum() for c in t['text'])]
    yy = sorted((t['bbox'][1]+t['bbox'][3])/2 for t in tt)
    centers = []
    for y in yy:
        if not centers or y-statistics.median(centers[-1]) > .75*xheight:
            centers.append([y])
        else:
            centers[-1].append(y)
    return dict(token_count=len(tt), token_row_clusters=len(centers),
                token_y_spread_xh=float(np.percentile(yy, 90)-np.percentile(yy, 10))/max(1., xheight) if yy else 0.)


def extract():
    start = time.time()
    cards = bind_cards()
    write_rows(OUT/'receipts/split.jsonl', cards)
    inputs = []
    features, changed, card_traces = [], [], []
    card_by_id = {c['id']: c for c in cards}
    for track, base in TRACKS.items():
        aggregate = rows(base/'lines.jsonl')
        by_page = defaultdict(list)
        for r in aggregate:
            by_page[r['page_id']].append(r)
        pages = rows(base/'pages.jsonl')
        for pth in [base/'lines.jsonl', base/'pages.jsonl']:
            inputs.append(dict(path=str(pth), sha256=sha(pth)))
        for pi, page in enumerate(pages):
            if page['id'] not in by_page:
                continue
            parsed_path = base/'google/parsed/docai'/f"{page['image_sha256']}.json"
            parsed = json.loads(parsed_path.read_text())
            raw_path = Path(parsed['raw_json_path'])
            if not raw_path.exists():
                hits = list((base/'google/docai').rglob(raw_path.name))
                assert len(hits) == 1, (track, page['id'], raw_path)
                raw_path = hits[0]
            inputs.append(dict(path=str(raw_path), sha256=sha(raw_path)))
            raw = json.loads(raw_path.read_text())
            doc = raw['document']
            tokens, inverse, returned = page_tokens(doc, (page['width'], page['height']))
            bulk_path = base/'bulk/lines'/f"{page['id']}.jsonl"
            bulk = {r['id']: r for r in rows(bulk_path)}
            inputs.append(dict(path=str(bulk_path), sha256=sha(bulk_path)))
            image_path = base/page['image']
            inputs.append(dict(path=str(image_path), sha256=sha(image_path)))
            # Eagerly load once: crop pixels are the original F2 crop rectangle.
            with Image.open(image_path) as im:
                image = im.convert('L')
            rr = []
            # Page scale is a median of saved Google line boxes, not a detector
            # output. Baseline F2 G1b flags are used only for eligibility counts.
            heights = [b['bbox'][3]-b['bbox'][1] for b in bulk.values() if sum(c.isalpha() for c in b['docai_raw_text'])>=3]
            medheight = statistics.median(heights or [b['bbox'][3]-b['bbox'][1] for b in bulk.values()])
            for old in by_page[page['id']]:
                b = bulk[old['id']]
                assembly = assemble_line(doc, b['docai_index'], tokens)
                assert assembly['old_label'] == normalise(b['docai_raw_text'])
                if 'text' in old:
                    assert normalise(old['text']) == assembly['old_label'], old['id']
                token_heights = [t['bbox'][3]-t['bbox'][1] for t in assembly['kept_tokens'] if t['bbox'] and any(c.isalpha() for c in t['text'])]
                fallback = statistics.median(token_heights)*.5 if token_heights else medheight*.5
                pix = pixel_features(image.crop(b['crop_bbox']), fallback)
                xheight = pix['xheight']
                tok = token_features(assembly['kept_tokens'], xheight)
                ownsp = spans(doc['pages'][0]['lines'][b['docai_index']])
                paras = [i for i, q in enumerate(doc['pages'][0].get('paragraphs', []))
                         if any(max(a, c) < min(z, d) for a, z in ownsp for c, d in spans(q))]
                fixed = assembly['fixed_label']
                density = sum(not c.isspace() and not ud.category(c).startswith('M') for c in ud.normalize('NFD', fixed))*xheight/max(1, pix['ink_width'])
                r = dict(track=track, source=old['source'], id=old['id'], page_id=page['id'],
                         item=old.get('item'), primary_class=old.get('primary_allocation', old.get('primary_target')),
                         year=old.get('year', page.get('year')), old_label=assembly['old_label'], fixed_label=fixed,
                         assembly_changed=assembly['changed'], dropped_token_ids=[d['dropped_token_id'] for d in assembly['drops']],
                         original_usable=bool(old['usable_candidate']), admitted=old['admitted'],
                         codec_v1_pass=old['codec_v1_pass'], geometry_positive=old['geometry_positive'],
                         crop_bbox=b['crop_bbox'], crop_sha256=b['crop_sha256'], crop_page_path=str(image_path),
                         page_median_row_height=medheight,
                         height_ratio=(b['crop_bbox'][3]-b['crop_bbox'][1])/medheight,
                         label_density=density, google_line_contributors=1, google_paragraph_contributors=len(paras),
                         google_paragraph_ids=paras, docai_line_index=b['docai_index'],
                         tags=list(old.get('line_tags', [])), **pix, **tok)
                rr.append(r)
                if assembly['changed'] or old['id'] in card_by_id:
                    trace = dict(track=track, source=old['source'], id=old['id'], page_id=page['id'],
                                 raw_path=str(raw_path), raw_sha256=inputs[-3]['sha256'], **assembly)
                    trace.pop('kept_tokens')
                    if assembly['changed']:
                        changed.append(trace)
                    if old['id'] in card_by_id:
                        card_traces.append(dict(trace, card_id=card_by_id[old['id']]['card_id']))
            median_density = statistics.median(r['label_density'] for r in rr if r['label_density'] > 0)
            for r in rr:
                r['density_ratio'] = r['label_density']/max(1e-9, median_density)
            features.extend(rr)
            if pi % 10 == 0:
                print(track, pi, len(features), round(time.time()-start, 1), flush=True)
    write_rows(OUT/'receipts/base_features.jsonl', features)
    write_rows(OUT/'receipts/assembly_changes.jsonl', changed)
    write_rows(OUT/'receipts/card_traces.jsonl', card_traces)
    for f in BLIND.glob('*labels*.jsonl'):
        inputs.append(dict(path=str(f), sha256=sha(f)))
    for c in cards:
        if not any(v['path'] == c['key_path'] for v in inputs):
            inputs.append(dict(path=c['key_path'], sha256=sha(c['key_path'])))
    write_json(OUT/'receipts/inputs.json', dict(seed=SEED, network=False, provider_calls=0, spend_usd=0,
               input_files=inputs, lines=len(features), cards=len(cards), changed_lines=len(changed), elapsed_seconds=time.time()-start))
    print('complete', len(features), len(changed), round(time.time()-start, 1))


def positive(c):
    # User-specified endpoint, kept even if assembly alone repairs the extra text.
    return c['letters'] == 'n' and bool(set(c['errors']) & {'merged_two_lines', 'extra_text', 'crop_overrun'})


def confusion(truth, pred):
    truth, pred = np.asarray(truth, bool), np.asarray(pred, bool)
    tp = int((truth & pred).sum())
    fp = int((~truth & pred).sum())
    fn = int((truth & ~pred).sum())
    tn = int((~truth & ~pred).sum())
    return dict(tp=tp, fp=fp, fn=fn, tn=tn,
                precision=tp/(tp+fp) if tp+fp else None,
                recall=tp/(tp+fn) if tp+fn else None,
                f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.)


def branch(r, b):
    return all(r[k] > v for k, v in b.items())


def reject(r, model):
    return any(branch(r, b) for b in model['branches'])


def calibrate():
    """Fit on calibration outcomes only; replay the frozen snapshot if present."""
    archive = OUT/'receipts/calibration_base_features.jsonl.gz'
    feature_path = archive if archive.exists() else OUT/'receipts/base_features.jsonl'
    split_archive = OUT/'receipts/calibration_split.jsonl'
    split_path = split_archive if split_archive.exists() else OUT/'receipts/split.jsonl'
    allfeatures = {r['id']: r for r in rows(feature_path)}
    calibration = [c for c in rows(split_path) if c['split'] == 'calibration']
    if feature_path.suffix == '.gz':
        h = hashlib.sha256()
        with gzip.open(feature_path, 'rb') as stream:
            for block in iter(lambda: stream.read(1024*1024), b''):
                h.update(block)
        feature_hash = h.hexdigest()
    else:
        feature_hash = sha(feature_path)
    features = [allfeatures[c['id']] for c in calibration]
    truth = np.array([positive(c) for c in calibration])
    # Fixed family, maximum three branches. No source identifiers enter the model.
    candidates = []
    for k, values in {
        'height_ratio': [1.3, 1.5, 1.7, 1.9, 2.2, 2.6],
        'token_y_spread_xh': [.65, .9, 1.2, 1.5, 2., 2.5],
        'internal_gap_xh': [2., 3., 4., 5., 7., 10.],
        'density_ratio': [1.3, 1.5, 1.8, 2.2, 2.8],
        'google_paragraph_contributors': [1, 2, 3],
    }.items():
        candidates.extend({k: v} for v in values)
    for peaks in [1, 2, 3]:
        for height in [2., 2.5, 3., 3.5]:
            candidates.append(dict(projection_peaks=peaks, crop_height_xh=height))
    predictions = np.array([[branch(r, b) for r in features] for b in candidates], bool)
    import itertools
    best = None
    tested = 0
    for count in (0, 1, 2, 3):
        for combo in itertools.combinations(range(len(candidates)), count):
            # At most one branch of each feature family.
            if len({tuple(candidates[i]) for i in combo}) < count:
                continue
            pred = predictions[list(combo)].any(axis=0) if combo else np.zeros(len(truth), bool)
            cm = confusion(truth, pred)
            key = (cm['f1'], cm['precision'] or 0., -int(pred.sum()), -count)
            tested += 1
            if best is None or key > best[0]:
                best = (key, combo, cm)
    _, combo, cm = best
    model = dict(schema='t4b-admission-screen-v1', seed=SEED,
                 branches=[candidates[i] for i in combo], calibration=cm,
                 objective='maximum F1; ties: precision, fewer calibration rejections, fewer branches',
                 candidate_branches=candidates, models_tested=tested,
                 calibration_cards=[dict(track=c['track'], source=c['source'], card_id=c['card_id']) for c in calibration],
                 endpoint='original blind letters=n and errors includes merged_two_lines or extra_text or crop_overrun',
                 test_outcomes_used=False, inputs=dict(features_sha256=feature_hash,
                 split_sha256=sha(split_path)))
    write_json(OUT/'receipts/model.json', model)
    print(json.dumps({k: model[k] for k in ['branches', 'calibration', 'models_tested']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['extract', 'calibrate'])
    args = parser.parse_args()
    if args.command == 'extract':
        extract()
    elif args.command == 'calibrate':
        calibrate()

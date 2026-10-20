"""Offline, train-only C1 agreement harvesting and S4 classifier fitting.

No recogniser is constructed. The crop cap is enforced before decoding images.
"""
from greekocr.ops.data_root import input_path as _data_input
import os
for k in ('VECLIB_MAXIMUM_THREADS', 'OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS'):
    os.environ[k] = '1'
import gzip
import hashlib
import json
import random
import time
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image
from greekocr.labelfix import ink as I, markshape as M
from greekocr.labelfix.candidates import pair_tokens
from greekocr.labelfix.ctc_align import Alignment
from greekocr.labelfix.text import clusters, nfd, VOWELS
from greekocr.labelfix.validate import DEV_BOOKS, load_three_way

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/records/labelfix/spellcheck'
CANON = ROOT.parent / 'greek-ocr-toolkit'


def read(path):
    with (gzip.open if str(path).endswith('.gz') else open)(_data_input(path), 'rt') as f:
        return [json.loads(x) for x in f]


def main():
    start = time.monotonic()
    selection = read(ROOT / '.cache/labelfix/clariden/C1_selection.jsonl')
    test = load_three_way(0)
    excluded = {l['doc'] for l in test} - set(DEV_BOOKS)
    assert all(r['doc'] not in excluded and r['split'] == 'train' for r in selection)
    assert not {r['id'] for r in selection} & {l['line_id'] for l in test}
    # Rare classes first, then seeded coverage. Labels only choose crops; only
    # exact agreeing words contribute fitting targets below.
    freq = Counter(M.mark_class(c.marks) for r in selection for c in clusters(nfd(r['label'])) if c.base in VOWELS)
    rng = random.Random(20261016)
    rng.shuffle(selection)
    selection.sort(key=lambda r: min((freq[M.mark_class(c.marks)] for c in clusters(nfd(r['label']))
                                     if c.base in VOWELS and '+' in (M.mark_class(c.marks) or '')), default=10**9))
    selected = {}
    coverage = Counter()
    for r in selection:
        cc = Counter(M.mark_class(c.marks) for c in clusters(nfd(r['label'])) if c.base in VOWELS)
        if any(v and coverage[k] < 650 for k, v in cc.items() if k not in (None, 'none')):
            selected[r['crop']] = r
            coverage.update(cc)
        if len(selected) >= 10000:
            break
    print('selected', len(selected), dict(coverage), flush=True)
    samples = []
    decoded = []
    agreements = Counter()
    with gzip.open(ROOT / '.cache/labelfix/clariden/C1_alignments.jsonl.gz', 'rt') as f:
        for raw in f:
            r = json.loads(raw)
            meta = selected.get(r['crop'])
            if meta is None:
                continue
            al = Alignment.from_record(r['alignment'])
            pairs = [(g, m) for g, m in pair_tokens(nfd(meta['label']), nfd(al.prediction))
                     if m is not None and g.core and g.core == m.core]
            with Image.open(CANON / r['crop']) as im:
                ci = I.analyse(im)
            decoded.append(r['crop'])
            for g, m in pairs:
                for cl in clusters(m.core):
                    if cl.base not in VOWELS:
                        continue
                    label = M.mark_class(cl.marks)
                    if label is None:
                        continue
                    agreements[label] += 1
                    span = al.span(m.core_start + cl.start)
                    ev = I.mark_evidence(ci, span.x0-ci.xh, span.x1+ci.xh,
                                         core_x0=span.x0, core_x1=span.x1, base_letter=cl.base)
                    if ev.body_source != 'letter' or ev.n_letters_in_span != 1:
                        continue
                    samples.append(dict(line_id=meta['id'], doc=meta['doc'], source='C1',
                                        label=label, x=M.features(ev)))
            if len(decoded) % 250 == 0:
                print('harvest', len(decoded), 'samples', len(samples), 'seconds', round(time.monotonic()-start), flush=True)
    assert len(decoded) == len(selected) <= 10000
    dev = read(ROOT / 'docs/records/labelfix/markshape_samples_S3.jsonl.gz')
    assert all(s['doc'] in DEV_BOOKS for s in dev)
    samples.extend(dict(s, source='DEV') for s in dev)
    # Preserve the S3 DEV line partition, and keep C1 calibration out of fitting.
    s3 = M.load_model(ROOT / 'docs/records/labelfix/markshape_model_S3.json')
    cal_ids = set(s3.meta['calibration_lines'])
    c1_ids = sorted({s['line_id'] for s in samples if s['source'] == 'C1'})
    rng.shuffle(c1_ids)
    # Rare classes remain in fit; calibration is DEV only, as requested.
    fit = [s for s in samples if s['line_id'] not in cal_ids]
    cal = [s for s in samples if s['line_id'] in cal_ids]
    counts = Counter(s['label'] for s in fit)
    # Bound ordinary classes without discarding rare compound examples.
    rng.shuffle(fit)
    bounded = []; used = Counter()
    for s in fit:
        if used[s['label']] < 1600 or s['source'] == 'DEV':
            bounded.append(s); used[s['label']] += 1
    classes = sorted(set(s3.classes) | set(counts))
    model = M.fit_mlp([s['x'] for s in bounded], [s['label'] for s in bounded], classes,
                      hidden=96, epochs=100, seed=20261016)
    calibration = M.calibrate(model, [s['x'] for s in cal], [s['label'] for s in cal])
    model.tau = calibration['threshold']['tau'] if calibration['threshold'] else 1.
    model.meta = dict(iteration='S4', seed=20261016, epochs=100, crop_cap=10000,
                      decoded_crops=len(decoded), heldout_used_for_selection=False,
                      fit_counts=dict(used), available_counts=dict(counts), agreement_counts=dict(agreements),
                      calibration=calibration, calibration_lines=sorted(cal_ids),
                      fit_docs=sorted({s['doc'] for s in bounded}))
    model.save(ROOT / 'docs/records/labelfix/markshape_model_S4.json')
    with gzip.open(OUT / 'S4_training_samples.jsonl.gz', 'wt') as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False)+'\n')
    receipt = dict(model.meta, decoded=decoded, elapsed_seconds=time.monotonic()-start,
                   model_sha256=hashlib.sha256((ROOT/'docs/records/labelfix/markshape_model_S4.json').read_bytes()).hexdigest(),
                   cpu_only=True, network=False, ctc_forward_passes=0)
    (OUT/'S4_training.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    print('TRAIN DONE', json.dumps(dict(used)), round(time.monotonic()-start), flush=True)


if __name__ == '__main__':
    main()

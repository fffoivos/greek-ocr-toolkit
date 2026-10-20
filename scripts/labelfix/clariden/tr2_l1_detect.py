"""CPU S6 detector and unchanged R1-A window extraction, receipt per shard."""
from __future__ import annotations
import argparse
from collections import Counter
import json
import multiprocessing as mp
import os
from pathlib import Path
import time

from scripts.labelfix.clariden.l1_common import canonical, rows, write_rows, sha256, write_json
from scripts.labelfix.clariden.r1_common import crop_key, crop_path

_STATE = None


def initialise(settings):
    global _STATE
    from greekocr.labelfix import case, markshape
    case.configure_model('docs/records/labelfix/case_model_S5.json')
    _STATE = settings, markshape.load_model('docs/records/labelfix/markshape_model_S4.json')


def chunk(task):
    import numpy as np
    from PIL import Image
    from greekocr.labelfix import ink, reading
    from greekocr.labelfix.ctc_align import Alignment
    from greekocr.labelfix.text import nfc
    from scripts.labelfix.clariden.r1_extract import extract_line
    from scripts.labelfix.owner_reading import serialize
    number, records = task
    settings, detector = _STATE
    out, crop_root, layout, log_lines = settings
    prefix = Path(out) / f'shard-{number:05d}'
    runtime, windows, samples, timings = [], [], [], []
    for r, ar in records:
        with Image.open(crop_path(r['crop'], crop_root, layout)) as source:
            image = source.convert('L')
        al = Alignment.from_record(ar)
        started = time.perf_counter()
        raw = reading.read_ink(ink.analyse(image), al.prediction, al, detector, filtered=False)
        detector_seconds = time.perf_counter() - started
        started = time.perf_counter()
        ss, wide, _, losses, coverage, size = extract_line(
            dict(id=r['id'], recogniser_text=al.prediction, _line=len(runtime)), ar, image, evaluation=True)
        window_seconds = time.perf_counter() - started
        for s in ss:
            samples.append(dict(line=len(runtime), start=s[3], letter=s[4], mask=s[7][0]))
        windows.extend(wide)
        runtime.append(dict(id=r['id'], recogniser_text=nfc(al.prediction), recogniser_nfd=al.prediction, detector=serialize(raw),
            coverage=coverage, font_size=size, extraction_counts=dict(losses)))
        timings.append(dict(id=r['id'], detector_seconds=detector_seconds, window_seconds=window_seconds, windows=len(ss)))
        if log_lines:
            print('LINE_TIMING ' + canonical(timings[-1]), flush=True)
    write_rows(str(prefix) + '-detector.jsonl.gz', runtime)
    write_json(str(prefix) + '-samples.json', samples)
    np.save(str(prefix) + '-wide.npy', np.asarray(windows, dtype=np.uint8).reshape(-1, 64, 128), allow_pickle=False)
    write_rows(str(prefix) + '-timings.jsonl', timings)
    paths = [Path(str(prefix) + suffix) for suffix in ('-detector.jsonl.gz', '-samples.json', '-wide.npy', '-timings.jsonl')]
    receipt = dict(shard=number, lines=len(runtime), windows=len(windows), complete=True,
        detector_seconds=sum(t['detector_seconds'] for t in timings),
        window_seconds=sum(t['window_seconds'] for t in timings),
        sha256={p.name: sha256(p) for p in paths})
    write_json(str(prefix) + '-receipt.json', receipt)
    return receipt


def run(selection, alignments, out, crop_root, layout, workers=64, chunk_size=128, log_lines=False):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    records = {r['crop']: r for r in rows(selection)}
    seen = set()
    def tasks():
        batch, number = [], 0
        for path in alignments:
            for ar in rows(path):
                key = crop_key(ar['crop'])
                if key not in records:
                    continue
                if key in seen:
                    raise ValueError('duplicate alignment ' + key)
                seen.add(key)
                batch.append((records[key], ar['alignment']))
                if len(batch) == chunk_size:
                    yield number, batch
                    number += 1
                    batch = []
        if batch:
            yield number, batch
    settings = (str(out), str(crop_root), layout, log_lines)
    receipts = []
    if workers == 1:
        initialise(settings)
        for task in tasks():
            receipts.append(chunk(task))
    else:
        with mp.get_context('spawn').Pool(workers, initializer=initialise, initargs=(settings,)) as pool:
            for receipt in pool.imap_unordered(chunk, tasks(), chunksize=1):
                receipts.append(receipt)
                print(f'DETECTOR_SHARD {len(receipts)} complete; lines={receipt["lines"]}', flush=True)
    assert seen == set(records), f'missing alignments: {len(set(records)-seen)}'
    receipt = dict(schema='l1-detector-windows-v1', complete=True, lines=len(records),
        selection_sha256=sha256(selection), alignment_sha256={str(p): sha256(p) for p in alignments},
        workers=workers, elapsed_seconds=time.monotonic()-started,
        detector_cpu_seconds=sum(r['detector_seconds'] for r in receipts),
        window_cpu_seconds=sum(r['window_seconds'] for r in receipts),
        windows=sum(r['windows'] for r in receipts), shards=sorted(receipts, key=lambda r:r['shard']))
    write_json(out / 'detector_receipt.json', receipt)
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('selection', 'out', 'crop-root'):
        ap.add_argument('--' + name, type=Path, required=True)
    ap.add_argument('--alignments', type=Path, nargs='+', required=True)
    ap.add_argument('--layout', choices=['toolkit', 'e3'], required=True)
    ap.add_argument('--workers', type=int, default=64)
    ap.add_argument('--mock', action='store_true')
    a = ap.parse_args()
    if a.mock:
        assert len(list(rows(a.selection))) <= 192 and a.workers == 1
    else:
        assert os.environ.get('SLURM_JOB_ID'), 'bulk work requires a Slurm allocation'
    print(canonical(run(a.selection, a.alignments, a.out, a.crop_root, a.layout, a.workers, log_lines=a.mock)), flush=True)


if __name__ == '__main__':
    main()

"""Clariden-only real-weight gate; load the final export through Docling's recognizer.

Uses byte-bound prepared005 dev PNGs, unchanged trainer collate, fp32 CPU, NFD
comparison. No test set loading, checkpoint selection, fetching or submission.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import unicodedata

import numpy as np
import pyarrow.parquet as pq
import torch

from greekocr.train.ckpt_io import sha256_file
from greekocr.train.data import ManifestDataset, make_loader
from greekocr.train.cer import greedy_decode_line
from greekocr.train.model import masked_forward
from greekocr.train.export import load_release
from greekocr.deploy.docling_plugin.recognizer.inference import Recognizer


def check(spec):
    p = Path(spec['path'])
    if p.stat().st_size != spec['bytes'] or sha256_file(str(p)) != spec['sha256']:
        raise ValueError('input byte/SHA binding mismatch: '+str(p))
    return p


def verify(release, runtime, runtime_sha256, panel, predictions, predictions_sha256, output):
    if panel not in ('seal04_dev', 'harvest_dev'):
        raise ValueError('release parity is dev only')
    runtime, predictions = map(Path, (runtime, predictions))
    if sha256_file(str(runtime)) != runtime_sha256 or sha256_file(str(predictions)) != predictions_sha256:
        raise ValueError('runtime/predictions SHA mismatch')
    rt = json.loads(runtime.read_text()); pool = rt['pools'][panel]
    rows = [row for entry in pool['files'] for row in pq.read_table(check(entry)).to_pylist()]
    if len(rows) != pool['rows']:
        raise ValueError('pool row count differs')
    ids = [r['line_id'] for r in rows]
    stored = [json.loads(line) for line in predictions.read_text().splitlines() if line.strip()]
    expected = {r['id']: r['hyp'] for r in stored}
    if len(expected) != len(stored) or len(set(ids)) != len(ids) or set(expected) != set(ids):
        raise ValueError('duplicate/missing/extra dev prediction IDs')
    trainer, codec, config = load_release(release)
    recognizer = Recognizer(str(release), device='cpu')
    dataset = ManifestDataset(rows, codec.version, codec.n_classes-1, 'reserved')
    loader, sampler = make_loader(dataset, 64, shuffle=False, num_workers=0)
    mismatch = []; served_mismatch = []; logit_mismatch = 0; count = 0
    with torch.no_grad():
        for indices, batch in zip(sampler, loader):
            lp = masked_forward(trainer, batch['images'], batch['input_lengths'])
            actual = masked_forward(recognizer.model, batch['images'], batch['input_lengths'])
            if not torch.equal(lp, actual):
                logit_mismatch += 1
            strips = [dataset[i]['image'].astype(np.float32)/255 for i in indices]
            served = recognizer.recognize(strips, bs=64)
            for j, index in enumerate(indices):
                identity = ids[index]
                n = int(batch['input_lengths'][j])
                hyp = greedy_decode_line(lp[j, :n].argmax(-1).tolist(), codec)
                nfd = lambda text: unicodedata.normalize('NFD', text)
                if nfd(served[j][0]) != nfd(hyp):
                    served_mismatch.append(identity)
                if nfd(served[j][0]) != nfd(expected[identity]):
                    mismatch.append(identity)
                count += 1
    receipt = dict(status='PASS' if not (mismatch or served_mismatch or logit_mismatch) else 'FAIL',
                   panel=panel, rows=count, precision='fp32 CPU; no autocast', comparison='NFD',
                   preprocessing='trainer ManifestDataset + collate_strips; exact bound PNG bytes; no page extraction',
                   stored_prediction_mismatches=len(mismatch), trainer_serve_mismatches=len(served_mismatch),
                   logit_mismatch_batches=logit_mismatch, first_mismatch_ids=mismatch[:20],
                   runtime_sha256=runtime_sha256, predictions_sha256=predictions_sha256,
                   export_manifest_sha256=sha256_file(str(Path(release)/'MANIFEST.json')))
    Path(output).write_text(json.dumps(receipt, indent=2)+'\n')
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('release', 'runtime', 'runtime-sha256', 'panel', 'predictions', 'predictions-sha256', 'output'):
        parser.add_argument('--'+name, required=True)
    args = vars(parser.parse_args(argv))
    result = verify(**args)
    print(json.dumps({k: result[k] for k in ('status', 'rows', 'stored_prediction_mismatches', 'trainer_serve_mismatches', 'logit_mismatch_batches')}))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())

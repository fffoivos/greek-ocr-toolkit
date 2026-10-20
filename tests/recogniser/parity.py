"""Explicit CU3 parity experiment; never collected by pytest. Exactly 200 distinct crops."""
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import random
import socket
import torch
from PIL import Image
from greekocr.labelfix import validate
from greekocr.labelfix.ctc_align import Recognizer
from greekocr._vendor.bench.e2_reader_parity import E1Reader
from greekocr.recogniser import load


def main():
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', CUDA_VISIBLE_DEVICES='')
    def blocked(*a, **kw):
        raise RuntimeError('CU3 network OFF')
    socket.socket.connect = blocked
    socket.socket.connect_ex = blocked
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    root = Path(__file__).resolve().parents[2]
    source = root.parent/'greek-ocr-toolkit-spellcheck'
    # This worktree has no ignored manifest/crops; bind the existing frozen local dataset.
    validate.TOOLKIT = source
    validate.TEST_JSONL = source/'docs/harvest/collection/v2/import_real_v2_test.jsonl'
    rows = random.Random(20261017).sample(sorted(validate.load_three_way(0), key=lambda r:r['line_id']), 200)
    paths = [r['crop'] for r in rows]
    assert len(set(paths)) == 200
    checkpoint = validate.CKPT[0]
    api = load(checkpoint, threads=4)
    old = Recognizer(checkpoint, threads=4)
    checks = []
    for start in range(0, 200, 16):
        batch = paths[start:start+16]
        images = []
        for p in batch:
            with Image.open(p) as im:
                im.load(); images.append(im.copy())
        reference = old.align_batch(images)
        actual = api.read(images, profile='labelfix', bs=16)
        for path, row, a, b in zip(batch, rows[start:start+16], reference, actual):
            identical = dataclasses.asdict(a) == dataclasses.asdict(b.alignment)
            assert identical, row['line_id']
            checks.append(dict(line_id=row['line_id'], crop=path,
                crop_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                labelfix=a.prediction, labelfix_old_identical=identical))
        print('labelfix',start+len(batch),flush=True)
    del old
    old_eval = E1Reader(checkpoint, api.codec_path, 'cpu')
    for i, (p, check) in enumerate(zip(paths, checks)):
        reference = old_eval.read(p)
        actual = api.read([p], profile='eval')[0].text
        assert reference == actual, check['line_id']
        check.update(eval=actual, eval_old_identical=reference == actual,
                     profiles_differ=check['labelfix'] != actual)
        if (i+1)%20 == 0: print('eval',i+1,flush=True)
    report = dict(schema='cu3-parity-v1', seed=20261017, rows=200, device='cpu', threads=4,
        interop_threads=1, batch_size_labelfix=16, batch_size_eval=1,
        source_root=str(source), manifest_sha256=hashlib.sha256(validate.TEST_JSONL.read_bytes()).hexdigest(),
        provenance=api.provenance, strict_binding_errors=api.binding_errors,
        labelfix_identical=sum(r['labelfix_old_identical'] for r in checks),
        eval_identical=sum(r['eval_old_identical'] for r in checks),
        labelfix_eval_differences=sum(r['profiles_differ'] for r in checks), checks=checks)
    (root/'artifacts/cleanup_step3/parity.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print({k:v for k,v in report.items() if k not in ('checks','provenance')},flush=True)


if __name__ == '__main__':
    main()

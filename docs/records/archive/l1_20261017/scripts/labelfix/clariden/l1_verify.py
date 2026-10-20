"""Held-out verification only: golden M2 readings and fail-closed node parity gate."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import time

from scripts.labelfix.clariden.l1_common import canonical, parity_projection, rows, sha256, write_json, write_rows
from scripts.labelfix.clariden.r1_common import crop_path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('binding', 'checkpoint', 'crop-root', 'out'):
        ap.add_argument('--' + name, type=Path, required=True)
    ap.add_argument('--layout', choices=['toolkit', 'e3'], required=True)
    ap.add_argument('--device', choices=['cpu', 'cuda:0'], required=True)
    ap.add_argument('--write-expected', action='store_true')
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    records = list(rows(a.binding / 'parity_selection.jsonl'))
    assert len(records) == 32 and len({r['id'] for r in records}) == 32
    expected = a.binding / 'parity_expected.jsonl'
    from scripts.labelfix.clariden.l1_infer import load_reader, run as infer
    from scripts.labelfix.clariden.l1_detect import run as detect
    if a.write_expected:
        assert a.device == 'cpu' and not expected.exists()
        import torch
        from PIL import Image
        from greekocr.labelfix import case, markshape
        from greekocr.labelfix.ctc_align import Alignment
        from scripts.labelfix.m2_run import infer_line
        torch.set_num_threads(4)
        case.configure_model('docs/labelfix/case_model_S5.json')
        detector = markshape.load_model('docs/labelfix/markshape_model_S4.json')
        reader = load_reader(a.checkpoint, 'cpu')
        golden = []
        crop_sha = {}
        for r in records:
            p = crop_path(r['crop'], a.crop_root, a.layout)
            crop_sha[r['id']] = sha256(p)
            with Image.open(p) as image:
                tick = time.monotonic()
                value = infer_line(r['id'], image.convert('L'), Alignment.from_record(r['alignment']), detector, reader)
                golden.append(parity_projection(value))
                print('M2_GOLDEN ' + canonical(dict(id=r['id'], seconds=time.monotonic()-tick)), flush=True)
        expected.write_text(''.join(canonical(r) + '\n' for r in sorted(golden, key=lambda r:r['id'])))
        write_json(a.binding / 'parity_crop_sha256.json', crop_sha)
        del reader
    crop_sha = json.loads((a.binding / 'parity_crop_sha256.json').read_text())
    assert all(sha256(crop_path(r['crop'], a.crop_root, a.layout)) == crop_sha[r['id']] for r in records)
    # No original Google labels or truth fields enter these shared inference calls.
    selection = a.out / 'verification_selection.jsonl'
    alignment = a.out / 'verification_alignments.jsonl'
    write_rows(selection, [dict(id=r['id'], crop=r['crop']) for r in records])
    write_rows(alignment, [dict(crop=r['crop'], alignment=r['alignment']) for r in records])
    detect(selection, [alignment], a.out / 'detector', a.crop_root, a.layout, workers=1, log_lines=True)
    infer(a.out / 'detector', a.checkpoint, a.out / 'combined', a.device, batch_size=64, log_lines=True)
    actual = {r['id']: canonical(parity_projection(r)) for p in sorted((a.out / 'combined').glob('*-combined.jsonl.gz')) for r in rows(p)}
    reference = {r['id']: canonical(r) for r in rows(expected)}
    differences = [i for i in sorted(reference.keys() | actual.keys()) if reference.get(i) != actual.get(i)]
    (a.out / 'actual_readings_hold.jsonl').write_text(''.join(actual[i] + '\n' for i in sorted(actual)))
    receipt = dict(schema='l1-parity-v1', verification_only=True, never_L1_training_input=True,
        expected=len(reference), actual=len(actual), exact=len(reference)-len(differences),
        byte_equal_readings_and_hold_decisions=not differences, differences=differences,
        expected_sha256=sha256(expected), actual_sha256=sha256(a.out / 'actual_readings_hold.jsonl'),
        comparison='canonical UTF-8 JSON per line: detector readings/parts/localisation, full combined PRESENCE/FULL readings and every HOLD decision/reason',
        golden_entrypoint='unchanged scripts.labelfix.m2_run.infer_line; frozen held-out recogniser text and cached spans',
        device=a.device, checkpoint_sha256=sha256(a.checkpoint))
    write_json(a.out / 'parity_receipt.json', receipt)
    print('PARITY ' + canonical(receipt), flush=True)
    if differences or len(actual) != 32:
        raise SystemExit('STOP: L1 held-out parity failed; no training crop processed and no L1 overlay/release permitted')


if __name__ == '__main__':
    main()

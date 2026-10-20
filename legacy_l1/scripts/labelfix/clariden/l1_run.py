"""Exact mock/Slurm orchestration. Never calls sbatch or requests an allocation."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from scripts.labelfix.clariden.l1_common import canonical, release, rows, sha256, write_json
from scripts.labelfix.clariden.r1_common import check_disjointness


def command(script, *args):
    cmd = [sys.executable, '-B', '-u', f'scripts/labelfix/clariden/{script}.py', *map(str, args)]
    print('ENTRYPOINT ' + canonical(cmd), flush=True)
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('binding', 'source', 'c1-alignments', 'ctc', 'r1', 'crop-root', 'out'):
        ap.add_argument('--' + name, type=Path, required=True)
    ap.add_argument('--layout', choices=['toolkit', 'e3'], required=True)
    ap.add_argument('--detector', choices=['s6', 's7'], required=True)
    ap.add_argument('--mock', action='store_true')
    ap.add_argument('--write-expected', action='store_true')
    a = ap.parse_args()
    if not a.mock:
        assert os.environ.get('SLURM_JOB_ID'), 'L1 full run requires a Slurm allocation'
        assert not a.write_expected, 'node must use shipped local expected outputs'
    a.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    binding = json.loads((a.binding / 'binding.json').read_text())
    if a.detector != binding['detector']:
        raise SystemExit('Detector parameter differs from frozen binding; S7 requires a separately prepared L1b bundle')
    assert sha256(a.source) == binding['source_sha256']
    assert sha256(a.r1) == binding['r1_sha256']
    assert sha256(a.c1_alignments) == binding['c1_alignment_sha256']
    assert sha256(a.ctc) == binding['ctc_sha256']
    assert sha256(a.ctc.with_suffix('.safetensors')) == binding['ctc_safetensors_sha256']
    assert sha256(a.binding / 'policy.json') == binding['policy_sha256']
    policy = json.loads((a.binding / 'policy.json').read_text())
    for p, digest in {**policy['source_sha256'], **policy['assets']}.items():
        assert sha256(p) == digest, 'frozen S6 source/asset changed: ' + p
    # This must finish before alignment, detector or R1 processing of any training crop.
    command('l1_verify', '--binding', a.binding, '--checkpoint', a.r1, '--crop-root', a.crop_root,
        '--layout', a.layout, '--device', 'cpu' if a.mock else 'cuda:0', '--out', a.out / 'verification',
        *(['--write-expected'] if a.write_expected else []))
    parity = json.loads((a.out / 'verification/parity_receipt.json').read_text())
    assert parity['byte_equal_readings_and_hold_decisions'] and parity['exact'] == 32
    write_json(a.out / 'parity_receipt.json', parity)
    selection = a.binding / ('mock_selection.jsonl' if a.mock else 'selection.jsonl')
    remaining = a.binding / ('mock_remaining_selection.jsonl' if a.mock else 'remaining_selection.jsonl')
    input_receipt = json.loads((a.binding / 'input_receipt.json').read_text())
    selected = list(rows(selection))
    assert len(selected) == (160 if a.mock else 124669)
    assert all(r['script_class'] == 'greek_poly' for r in selected)
    exclusions = json.loads((a.binding / 'exclusions.json').read_text())
    disjoint = check_disjointness(selected, exclusions)
    assert all(r['document_count'] == r['line_count'] == 0 for r in disjoint.values())
    write_json(a.out / 'input_receipt.json', dict(input_receipt, actual_run_lines=len(selected), mock=a.mock))
    command('c1_run', '--selection', remaining, '--checkpoint', a.ctc, '--crop-root', a.crop_root,
        '--crop-layout', a.layout, '--out', a.out / 'alignment', '--device', 'cpu' if a.mock else 'cuda',
        '--workers', 1 if a.mock else 4, '--threads', 4 if a.mock else 8, '--batch-size', 16,
        '--chunk-size', 32 if a.mock else 512, *(['--mock'] if a.mock else []))
    command('l1_detect', '--selection', selection, '--alignments', a.c1_alignments,
        a.out / 'alignment/C1_alignments.jsonl.gz', '--out', a.out / 'detector',
        '--crop-root', a.crop_root, '--layout', a.layout, '--workers', 1 if a.mock else 64,
        *(['--mock'] if a.mock else []))
    command('l1_infer', '--data', a.out / 'detector', '--checkpoint', a.r1, '--out', a.out / 'combined',
        '--device', 'cpu' if a.mock else 'cuda:0', *(['--mock'] if a.mock else []))
    counts = release(selection, sorted((a.out / 'combined').glob('*-combined.jsonl.gz')),
                     a.out / 'release', binding, a.source, input_receipt)
    assert sha256(a.source) == binding['source_sha256'], 'source labels changed'
    receipt = dict(schema='l1-run-v1', complete=True, mock=a.mock, lines=len(selected),
        parity=parity, counts=counts, elapsed_seconds=time.monotonic()-started,
        original_labels_unchanged=True, detector=a.detector, binding_sha256=sha256(a.binding / 'binding.json'),
        step_receipts={str(p.relative_to(a.out)): sha256(p) for p in a.out.rglob('*receipt.json')})
    write_json(a.out / 'run_receipt.json', receipt)
    print('L1_MOCK_DONE ' + canonical(receipt) if a.mock else 'L1_JOB_DONE ' + canonical(receipt), flush=True)


if __name__ == '__main__':
    main()

"""R1-A fp32 GPU inference then unchanged M2 composition, with durable shard receipts."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import time
import numpy as np
import torch

from greekocr.labelfix.release_gate import compose_runtime
from greekocr.labelfix.ctc_align import recognition_fields
from scripts.labelfix.clariden.l1_common import canonical, rows, write_rows, write_json, sha256
from scripts.labelfix.clariden.r1_common import HEADS, LETTERS, compose
from scripts.labelfix.clariden.r1_model import MarkReader


def load_reader(checkpoint, device):
    model = MarkReader(embedding=True).to(device, memory_format=torch.channels_last)
    ck = torch.load(checkpoint, map_location='cpu', weights_only=True)
    assert ck['arm'] == 'A'
    model.load_state_dict(ck['model'])
    model.eval()
    return model


def predictions(model, samples, windows, device, batch_size):
    """M2 tensor construction and fp32 softmax; only placement/batching differs."""
    result = []
    with torch.inference_mode():
        for i in range(0, len(samples), batch_size):
            ss = samples[i:i+batch_size]
            grey = torch.from_numpy(np.array(windows[i:i+batch_size])).to(device=device, dtype=torch.float32).div_(255)
            masks = torch.tensor([s['mask'] for s in ss], device=device, dtype=torch.float32)
            xx = torch.arange(128, device=device, dtype=torch.float32)[None, :] + .5
            mask = ((xx >= masks[:, 0, None]) & (xx < masks[:, 1, None])).float()[:, None, :].expand(-1, 64, -1)
            x = torch.stack((grey, mask), dim=1).contiguous(memory_format=torch.channels_last)
            letters = torch.tensor([s['letter'] for s in ss], device=device, dtype=torch.long)
            prob = [z.float().softmax(1) for z in model(x, letters)]
            values = torch.stack([z.argmax(1) for z in prob], 1).tolist()
            probabilities = [p.cpu() for p in prob]
            for j, (s, v) in enumerate(zip(ss, values)):
                cls = compose(v)
                result.append(dict(start=s['start'], base=LETTERS[s['letter']], factors=v, cls=cls,
                    parts=cls.split('+') if cls != 'none' else [],
                    mark_probabilities={choices[q]: float(probabilities[h][j, q])
                        for h, (choices, q) in enumerate(zip(HEADS.values(), v)) if q}))
    return result


def run(data, checkpoint, out, device, batch_size=512, log_lines=False):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(4 if device == 'cpu' else 8)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    model = load_reader(checkpoint, device)
    started = time.monotonic()
    receipts = []
    for rp in sorted(Path(data).glob('shard-*-receipt.json')):
        receipt = json.loads(rp.read_text())
        for name, expected in receipt['sha256'].items():
            assert sha256(Path(data) / name) == expected, 'detector/window shard changed'
        prefix = Path(data) / f'shard-{receipt["shard"]:05d}'
        records = list(rows(str(prefix) + '-detector.jsonl.gz'))
        samples = json.loads(Path(str(prefix) + '-samples.json').read_text())
        windows = np.load(str(prefix) + '-wide.npy', mmap_mode='r', allow_pickle=False)
        line_seconds = []
        tick = time.perf_counter()
        if log_lines:
            pred, offset = [], 0
            for i in range(len(records)):
                count = sum(s['line'] == i for s in samples)
                line_tick = time.perf_counter()
                pred.extend(predictions(model, samples[offset:offset+count], windows[offset:offset+count], device, batch_size))
                line_seconds.append(time.perf_counter()-line_tick)
                offset += count
            assert offset == len(samples)
        else:
            pred = predictions(model, samples, windows, device, batch_size)
        seconds = time.perf_counter() - tick
        byline = [{} for r in records]
        for sample, p in zip(samples, pred):
            byline[sample['line']][p['start']] = p
        combined = []
        for i, r in enumerate(records):
            rr = dict(r,status='ok',r1_predictions=list(byline[i].values()))
            rr.update(recognition_fields(r))
            rr['modes']={mode:compose_runtime(rr,mode) for mode in ('PRESENCE','FULL')}
            combined.append(rr)
            if log_lines:
                print('LINE_R1_TIMING ' + canonical(dict(id=r['id'], samples=len(byline[i]),
                    r1_seconds=line_seconds[i], timing_basis='measured per-line inference wall')), flush=True)
        dest = out / f'shard-{receipt["shard"]:05d}-combined.jsonl.gz'
        write_rows(dest, combined)
        shard_receipt = dict(shard=receipt['shard'], lines=len(records), samples=len(samples),
            inference_seconds=seconds, output=dest.name, output_sha256=sha256(dest), complete=True)
        write_json(out / f'shard-{receipt["shard"]:05d}-receipt.json', shard_receipt)
        receipts.append(shard_receipt)
        print('R1_SHARD ' + canonical(shard_receipt), flush=True)
    receipt = dict(schema='l1-r1-composition-v1', complete=True, device=device, precision='fp32, TF32 off, no autocast',
        checkpoint_sha256=sha256(checkpoint), samples=sum(r['samples'] for r in receipts),
        lines=sum(r['lines'] for r in receipts), inference_seconds=sum(r['inference_seconds'] for r in receipts),
        elapsed_seconds=time.monotonic()-started, shards=receipts)
    write_json(out / 'r1_receipt.json', receipt)
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('data', 'checkpoint', 'out'):
        ap.add_argument('--' + name, type=Path, required=True)
    ap.add_argument('--device', choices=['cpu', 'cuda:0'], required=True)
    ap.add_argument('--mock', action='store_true')
    a = ap.parse_args()
    if a.mock:
        assert a.device == 'cpu'
        assert json.loads((a.data / 'detector_receipt.json').read_text())['lines'] <= 192
    else:
        assert os.environ.get('SLURM_JOB_ID'), 'bulk inference requires a Slurm allocation'
    print(canonical(run(a.data, a.checkpoint, a.out, a.device, 64 if a.mock else 512, a.mock)), flush=True)


if __name__ == '__main__':
    main()

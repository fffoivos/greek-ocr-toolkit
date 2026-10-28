#!/usr/bin/env python3
"""REL0-S1 fixed-order, selected-weight OCR speed benchmark on Clariden only."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from analyze_models import (DEFAULT_DATA, load_sealed, prepare_output, read, require,
                           resolve_selected, run_list, sha, spec, timestamp, write)


def hardware(torch, device):
    info = dict(hostname=platform.node(), platform=platform.platform(), machine=platform.machine(),
                processor=platform.processor(), logical_cpus=os.cpu_count(),
                torch_version=torch.__version__, python=platform.python_version(),
                torch_config=torch.__config__.show(), interop_threads=torch.get_num_interop_threads(),
                affinity=sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None,
                slurm_job_id=os.environ.get('SLURM_JOB_ID'), slurm_cpus_per_task=os.environ.get('SLURM_CPUS_PER_TASK'),
                cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'))
    if Path('/proc/cpuinfo').exists():
        info['cpuinfo'] = Path('/proc/cpuinfo').read_text()
    if device == 'gpu':
        require(torch.cuda.device_count() == 1, 'benchmark requires exactly one visible GPU')
        props = torch.cuda.get_device_properties(0)
        info.update(gpu_name=props.name, gpu_memory_bytes=props.total_memory,
                    gpu_capability=list(torch.cuda.get_device_capability(0)), cuda_version=torch.version.cuda,
                    cudnn_version=torch.backends.cudnn.version())
        try:
            info['nvidia_smi'] = subprocess.check_output(
                ['nvidia-smi', '--query-gpu=name,uuid,driver_version,memory.total', '--format=csv,noheader'], text=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            info['nvidia_smi_error'] = str(exc)
    return info


def fixed_samples(data_dir, runtime, count=2000):
    """First 2000 rows of lexicographically sorted shards, stored row order.

    Narrow reads only: stop after the bounded sample; hash bound full shards for
    custody, but never decode or load the full image population into memory.
    """
    import pyarrow.parquet as pq
    files = sorted((Path(data_dir) / 'harvest_dev').glob('part-*.parquet'))
    require(files and {str(f.resolve()) for f in files} ==
            {str(Path(f['path']).resolve()) for f in runtime['pools']['harvest_dev']['files']}, 'sample/runtime shards differ')
    from analyze_models import check_bound
    for f in runtime['pools']['harvest_dev']['files']:
        check_bound(f)
    rows = []
    cols = ['line_id', 'image_png', 'width', 'label_ids', 'script_class', 'codec_version']
    for file in files:
        for batch in pq.ParquetFile(file).iter_batches(columns=cols, batch_size=128):
            rows.extend(batch.to_pylist()[:count-len(rows)])
            if len(rows) == count:
                break
        if len(rows) == count:
            break
    require(len(rows) == count and len({r['line_id'] for r in rows}) == count, 'incomplete/duplicate speed sample')
    ids = [r['line_id'] for r in rows]
    return rows, dict(lines=count, order='lexicographic shard path then stored row order; first 2000; no width sorting',
                      ids=ids, ids_sha256=hashlib.sha256(json.dumps(ids, separators=(',', ':')).encode()).hexdigest(),
                      shards=[spec(f) for f in files])


def benchmark_case(torch, model, model_code, data_code, cer, codec, rows, device, precision, threads, batch_size,
                   repeats=5, warmup_batches=10):
    import numpy as np
    from PIL import Image
    torch.set_num_threads(threads)
    dtype = torch.bfloat16 if precision == 'bf16' else None
    if precision == 'bf16' and model_code.amp_dtype_for(device) != dtype:
        return dict(device=device.type, precision=precision, threads=threads, batch_size=batch_size,
                    status='UNSUPPORTED', reason='sealed trainer/device does not support bf16')
    require(model_code.STRIDE == data_code.STRIDE if hasattr(model_code, 'STRIDE') else True, 'stride differs')

    def infer(chunk):
        samples = []
        for row in chunk:
            require(row['codec_version'] == codec.version, 'speed sample codec mismatch')
            with Image.open(io.BytesIO(row['image_png'])) as image:
                require(image.mode == 'L' and image.size == (row['width'], data_code.STRIP_HEIGHT), 'speed image contract mismatch')
                arr = np.asarray(image, dtype=np.uint8).copy()
            samples.append(dict(image=arr, width=row['width'], label=np.asarray(row['label_ids'], dtype=np.int64), script_class=row['script_class']))
        batch = data_code.collate_strips(samples)
        with model_code.autocast_ctx(device, dtype):
            output = model_code.masked_forward(model, batch['images'].to(device), batch['input_lengths'])
        ids = output.float().cpu().argmax(-1)
        decoded = [cer.greedy_decode_line(ids[i, :int(batch['input_lengths'][i])].tolist(), codec) for i in range(len(chunk))]
        return len(decoded)

    def sync():
        if device.type == 'cuda':
            torch.cuda.synchronize(device)

    chunks = [rows[start:start+batch_size] for start in range(0, len(rows), batch_size)]
    with torch.inference_mode():
        for i in range(warmup_batches):
            infer(chunks[i % len(chunks)])
        sync()
        if device.type == 'cuda':
            torch.cuda.reset_peak_memory_stats(device)
        durations = []
        for _ in range(repeats):
            sync()
            start = time.perf_counter()
            n = sum(infer(chunk) for chunk in chunks)
            sync()
            elapsed = time.perf_counter() - start
            require(n == len(rows), 'speed pass coverage mismatch')
            durations.append(elapsed)
    median = statistics.median(durations)
    return dict(status='PASS', device=device.type, precision=precision, threads=torch.get_num_threads(),
                interop_threads=torch.get_num_interop_threads(), batch_size=batch_size, lines=len(rows),
                tail_batch=len(chunks[-1]), repeat_seconds=durations, median_seconds=median,
                ms_per_line=median * 1000 / len(rows), lines_per_second=len(rows)/median,
                warmup_batches=warmup_batches, peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(device) if device.type == 'cuda' else None)


def worker(args, run, output):
    import torch
    torch.set_num_interop_threads(1)
    torch.set_num_threads(1)
    _, cer = load_sealed(run['package'])
    selection, _, runtime, receipts = resolve_selected(run)
    from train import model as model_code, data as data_code
    from train import ckpt_io
    codec = cer.load_codec(str(Path(run['package']) / 'vendor/codec/v2.1.json'))
    weights, meta = ckpt_io.load_model_weights(selection['safetensors']['path'])
    require(float(meta['width_mult']) == float(run['width_mult']) and meta['codec_version'] == codec.version
            and int(meta['n_classes']) == codec.n_classes and meta['head'] == 'nfd', 'benchmark model metadata mismatch')
    model, _ = model_code.build_model(n_classes=codec.n_classes, arch=meta['arch'], width_mult=float(meta['width_mult']))
    model.load_state_dict(weights, strict=True)
    count = sum(p.numel() for p in model.parameters())
    require(count == selection['parameter_count'], 'parameter count mismatch')
    device = torch.device('cuda:0' if args.device == 'gpu' else 'cpu')
    hw = hardware(torch, args.device)
    model.to(device).eval()
    # Disable TF32 so the fp32 case is an explicit fp32 baseline.
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    rows, sample = fixed_samples(args.data_dir, runtime)
    cases = []
    grid = ([(t, 'fp32', b) for t in (1, 8) for b in (1, 32)] if args.device == 'cpu' else
            [(1, precision, b) for precision in ('bf16', 'fp32') for b in (1, 32, 256)])
    for threads, precision, batch in grid:
        print(f"{run['label']} {args.device} {precision} threads={threads} batch={batch}", flush=True)
        try:
            case = benchmark_case(torch, model, model_code, data_code, cer, codec, rows, device, precision, threads, batch)
        except torch.cuda.OutOfMemoryError as exc:
            torch.cuda.empty_cache()
            case = dict(status='OOM', device=device.type, precision=precision, threads=threads, batch_size=batch, reason=str(exc))
        cases.append(case)
    receipt = dict(status='PASS' if all(c['status'] in ('PASS', 'UNSUPPORTED') for c in cases) else 'FAIL',
                   generated_at=timestamp(), run=run, selection=selection, parameter_count=count,
                   safetensors_bytes=Path(selection['safetensors']['path']).stat().st_size,
                   hardware=hw, sample=sample, repeats=5, warmup_batches=10,
                   input_height=data_code.STRIP_HEIGHT, normalization='sealed collate_strips: (uint8/255 - .5)/.5; own-background halo',
                   timing_scope='PNG decode + sealed collate/normalise + transfer + masked_forward + CPU greedy CTC decode; disk/load/warmup excluded',
                   tf32=False, cases=cases, inputs=receipts,
                   code={p.name: spec(p) for p in Path(__file__).parent.glob('*.py')})
    write(output / f"speed_{run['label']}_{args.device}.json", receipt)
    require(receipt['status'] == 'PASS', 'benchmark cases failed; receipt retained')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs', required=True, type=Path)
    p.add_argument('--data-dir', default=Path(DEFAULT_DATA), type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--device', required=True, choices=('cpu', 'gpu'))
    p.add_argument('--worker', help=argparse.SUPPRESS)
    args = p.parse_args()
    runs = run_list(args.runs)
    output = prepare_output(args.out, runs, args.data_dir)
    try:
        if args.worker:
            worker(args, next(r for r in runs if r['label'] == args.worker), output)
        else:
            for r in runs:
                subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--runs', str(args.runs.resolve()),
                                '--data-dir', str(args.data_dir), '--out', str(output), '--device', args.device, '--worker', r['label']], check=True)
    except Exception as exc:
        write(output / f"FAILURE_speed_{args.worker or 'driver'}_{args.device}.json",
              dict(status='FAIL', error=str(exc), generated_at=timestamp()))
        raise


if __name__ == '__main__':
    main()

"""Single-GPU throughput measurement; TRAIN pools only, no eval/checkpoint IO.

The numerical update matches S1 segment mode: deterministic bf16 model, fp32
CPU CTC, AdamW, norm/bias exemption, clip 5, OneCycle without momentum cycling.
Measurement weights are disposable. Incomplete points restart from initialization.
"""
import argparse
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import threading
import time

from common import atomic, bound, digest, read, sha, spec

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'vendor'))
THREAD_KEYS = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')


def binding(runtime, width, batch, workers, warmup, updates, fixture=False):
    return dict(schema='TRAIN_FULL-stage-A-point-v1', runtime=spec(runtime),
                payload_sha256=sha(ROOT / 'PAYLOAD.json'), width_mult=width,
                batch=batch, workers=workers, warmup=warmup, updates=updates, fixture=fixture)


def train_rows(runtime):
    """Never open a DEV/TEST pool. Verify every input train shard's bytes."""
    import pyarrow.parquet as pq
    from train.mix import assemble
    if sum(c['fraction'] for c in runtime['components'] if c['kind'] == 'synthetic') != .5:
        raise ValueError('half synthetic mixture required')
    groups = []
    for c in runtime['components']:
        pool = runtime['pools'][c['name']]
        rr = [r for f in pool['files'] for r in pq.read_table(bound(f)).to_pylist()]
        if len(rr) != pool['rows'] or any(r['split'] != 'train' for r in rr):
            raise ValueError('train pool row/split mismatch')
        groups.append(rr)
    count = 2 * runtime['train_rows'] if not runtime.get('mock') else 4096
    rr, _ = assemble(groups, [c['fraction'] for c in runtime['components']],
                     runtime['seed'], 1, count, exact_rows=True)
    real = [r for r in rr if runtime['components'][r['_component']]['kind'] == 'real']
    if len(real) * 2 != len(rr):
        raise ValueError('mixture exposure changed')
    if sum(r.get('source_dataset') == 'parliament_proceedings_1975_2000' for r in real) * 4 > len(real):
        raise ValueError('parliament cap changed')
    return rr


def gpu_uuid():
    output = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid,gpu_uuid',
                                      '--format=csv,noheader,nounits'], text=True)
    found = {parts[1].strip() for line in output.splitlines()
             if len(parts := line.split(',')) == 2 and parts[0].strip() == str(os.getpid())}
    if len(found) != 1:
        raise ValueError('cannot attest this process to exactly one physical GPU')
    return found.pop()


class Monitor:
    def __init__(self, uuid):
        self.uuid, self.samples, self.errors = uuid, [], []
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.poll, daemon=True)

    def poll(self):
        while not self.stop.is_set():
            try:
                value = subprocess.check_output(['nvidia-smi', '-i', self.uuid,
                    '--query-gpu=utilization.gpu,memory.used,power.draw',
                    '--format=csv,noheader,nounits'], text=True, timeout=5)
                util, mem, power = map(float, value.strip().split(','))
                self.samples.append(dict(time=time.time(), util_percent=util, memory_MiB=mem, power_W=power))
            except (ValueError, subprocess.SubprocessError) as e:
                self.errors.append(str(e))
            self.stop.wait(1)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.stop.set()
        self.thread.join(timeout=6)


def measure(runtime_path, width, batch, workers, warmup, updates, *, fixture=False):
    started = time.time()
    from train import train as t
    from train.data import ManifestDataset, make_loader, collate_strips
    from train.ctc_health import CtcHealth
    t._runtime()
    torch = t.torch
    runtime = read(runtime_path)
    if bool(runtime.get('mock')) != fixture:
        raise ValueError('fixture/production mismatch')
    if not fixture:
        from verify import verify, data_package_matches
        verify()
        if not data_package_matches(runtime.get('package_sha256'), runtime_path):
            raise ValueError('prepared data binding changed')
        bound(runtime['manifest']); bound(runtime['config'])
        if torch.__version__ != '2.11.0+cu128' or torch.version.cuda != '12.8':
            raise ValueError('S1 torch/CUDA profile changed')
        if torch.backends.cudnn.version() != 91900 or torch.cuda.get_device_name(0) != 'NVIDIA GH200 120GB':
            raise ValueError('S1 cuDNN/GPU changed')
        if torch.cuda.device_count() != 1 or not os.environ.get('CUDA_VISIBLE_DEVICES'):
            raise ValueError('srun must pin exactly one GPU per lane')
        if len(os.sched_getaffinity(0)) < 24 or any(os.environ.get(k) != '1' for k in THREAD_KEYS):
            raise ValueError('24 CPUs and four native thread limits required')
    device = torch.device('cpu' if fixture else 'cuda')
    rr = train_rows(runtime)
    codec = t.load_codec(str(ROOT / 'vendor/codec/v2.1.json'))
    ds = ManifestDataset(rr, codec.version, codec.n_classes - 1, 'train')
    loader, sampler = make_loader(ds, batch, seed=runtime['seed'], shuffle=True,
        num_workers=workers, pin_memory=not fixture, pack_bucket_tails=True)
    sampler.set_epoch(1)
    batches = list(sampler)
    if warmup + updates > len(batches):
        raise ValueError('measurement exceeds one epoch; do not cycle a small sample')
    t.set_seeds(0)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)
    model = t.build_arm('nfd', 'compact', codec, width_mult=width).to(device)
    model.train()
    opt = torch.optim.AdamW(t.no_decay_param_groups(model, .05), lr=1e-4, weight_decay=.05)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=1e-4, total_steps=warmup + updates + 1,
                                               pct_start=.075, cycle_momentum=False)
    ctc, health = torch.nn.CTCLoss(blank=0, zero_infinity=True), CtcHealth()
    amp = t.amp_dtype_for(device)

    def sync():
        if not fixture:
            torch.cuda.synchronize()

    def update(b):
        opt.zero_grad(set_to_none=True)
        with t.autocast_ctx(device, amp):
            out = t.masked_forward(model, b['images'].to(device), b['input_lengths'])
        # S1 --segment: deterministic CTC on CPU, including differentiable transfer.
        lp = out.float().transpose(0, 1).to('cpu')
        health.update_batch(b['targets'].tolist(), b['target_lengths'].tolist(), b['input_lengths'].tolist())
        if health.batches % 200 == 0:
            health.check_abort()
        loss = ctc(lp, b['targets'], b['input_lengths'], b['target_lengths'])
        if not torch.isfinite(loss):
            raise ValueError('nonfinite CTC in throughput probe')
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 5.)
        opt.step(); sched.step()
        return loss.item()

    # Probe the largest actual padded tensor in the complete packed epoch plan.
    # This catches rare wide/tail batches that a 330-update prefix might miss.
    widest = max(batches, key=lambda ids: len(ids) * (max(rr[i]['width'] for i in ids) + 128))
    capacity = dict(rows=len(widest), max_width=max(rr[i]['width'] for i in widest),
                    indices_sha256=digest(widest))
    update(collate_strips([ds[i] for i in widest])); sync()
    if not fixture:
        capacity['peak_allocated_bytes'] = torch.cuda.max_memory_allocated()
        capacity['peak_reserved_bytes'] = torch.cuda.max_memory_reserved()
        torch.cuda.reset_peak_memory_stats()
    iterator = iter(loader)
    for _ in range(warmup):
        update(next(iterator))
    sync()
    uuid = 'MOCK-GPU' if fixture else gpu_uuid()
    monitor = Monitor(uuid) if not fixture else None
    samples = []
    if monitor:
        monitor.__enter__()
    try:
        tick = time.perf_counter()
        for _ in range(updates):
            begin = time.perf_counter()
            b = next(iterator)
            wait = time.perf_counter() - begin
            loss = update(b)
            sync()
            samples.append(dict(seconds=time.perf_counter() - begin, loader_wait_seconds=wait,
                                rows=len(b['labels']), padded_width=b['images'].shape[-1], loss=loss))
        elapsed = time.perf_counter() - tick
    finally:
        if monitor:
            monitor.__exit__()
    lines = sum(s['rows'] for s in samples)
    chunks = [sum(s['rows'] for s in samples[i:i+100]) / sum(s['seconds'] for s in samples[i:i+100])
              for i in range(0, len(samples), 100)]
    util = monitor.samples if monitor else []
    if not fixture and not util:
        raise ValueError('GPU telemetry missing; measurement incomplete')
    return dict(status='OK', started_unix=started, ended_unix=time.time(), seconds=elapsed,
        drawn_lines=lines, lines_per_second=lines / elapsed,
        loader_stall_share=sum(s['loader_wait_seconds'] for s in samples) / elapsed,
        chunk_lines_per_second=chunks,
        chunk_cv=statistics.pstdev(chunks) / statistics.mean(chunks),
        peak_allocated_bytes=0 if fixture else torch.cuda.max_memory_allocated(),
        peak_reserved_bytes=0 if fixture else torch.cuda.max_memory_reserved(),
        gpu_util_mean=statistics.mean(s['util_percent'] for s in util) if util else None,
        gpu_uuid=uuid, cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),
        cpu_affinity=sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else [],
        native_threads={k: os.environ.get(k) for k in THREAD_KEYS}, pid=os.getpid(),
        slurm_job_id=os.environ.get('SLURM_JOB_ID'), restart_count=os.environ.get('SLURM_RESTART_COUNT', '0'),
        capacity_probe=capacity, samples=samples, telemetry=util,
        telemetry_errors=monitor.errors if monitor else [], ctc_health=health.as_dict(),
        data_draw_sha256=digest([(r['line_id'], r['_component'], r['_pool_index']) for r in rr]),
        measurement_schedule='1 capacity update + 30 warmup + 300 timed updates; short OneCycle; disposable weights',
        packing='S1 128px width buckets, pack_bucket_tails=True, own-background halo')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--width', type=float, choices=(1., 1.5, 2.), required=True)
    p.add_argument('--batch', type=int, choices=(64, 128, 256, 512, 1024), required=True)
    p.add_argument('--workers', type=int, choices=(6, 12), required=True)
    p.add_argument('--warmup', type=int, default=30)
    p.add_argument('--updates', type=int, default=300)
    a = p.parse_args()
    if a.warmup < 1 or a.updates < 1:
        p.error('positive warmup/updates required')
    identity = binding(a.runtime, a.width, a.batch, a.workers, a.warmup, a.updates)
    if Path(a.out).exists():
        raise ValueError('immutable result exists')
    try:
        result = measure(a.runtime, a.width, a.batch, a.workers, a.warmup, a.updates)
    except Exception as e:
        import torch
        if not isinstance(e, torch.cuda.OutOfMemoryError):
            raise
        result = dict(status='OOM', error=str(e), ended_unix=time.time())
    atomic(a.out, dict(binding=identity, **result))


if __name__ == '__main__':
    main()

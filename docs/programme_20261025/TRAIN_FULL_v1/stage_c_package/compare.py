"""Compare owner-run real CUDA control against forced scheduler requeue."""
import argparse
from pathlib import Path
import sys
from common import atomic, read, sha, spec

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'vendor'))

FIELDS = ('model', 'opt', 'sched', 'rng', 'epoch', 'batch_position', 'iterator_created',
          'global_step', 'best', 'bad_epochs', 'health', 'trace', 'draw_chain', 'draw_position')


def forced_requeue_proof(resumed, allocations):
    """The first allocation must have yielded the archived step-3 bytes.

    segment.pt is rewritten on continuation, so authenticate the immutable
    archive rather than trying to bind the old yield's now-stale rolling path.
    """
    resumed = Path(resumed)
    yield_path = resumed / 'SEGMENT_YIELD.json'
    yielded = read(yield_path)
    if (int(yielded['restart_count']) != 0 or not any(
            x['job_id'] == yielded['job_id'] and int(x['restart_count']) == 0
            and x['mode'] == 'smoke-requeue' for x in allocations)):
        raise ValueError('first-allocation forced requeue yield missing')
    archive = resumed / 'checkpoints/step-000000003.pt'
    if sha(archive) != yielded['checkpoint']['sha256']:
        raise ValueError('forced requeue did not yield the exact step-3 checkpoint')
    return dict(yield_record=spec(yield_path), archived_checkpoint=spec(archive), step=3)


def compare(control, resumed, out):
    import torch
    from train import train as trainer
    trainer._runtime()
    control, resumed = Path(control), Path(resumed)
    a = torch.load(control / 'segment.pt', map_location='cpu', weights_only=False)
    b = torch.load(resumed / 'segment.pt', map_location='cpu', weights_only=False)
    for ck in (a, b):
        if ck['state_sha256'] != trainer.checkpoint_state_sha256(ck):
            raise ValueError('state digest invalid')
    if trainer.checkpoint_state_sha256({k: a[k] for k in FIELDS}) != trainer.checkpoint_state_sha256({k: b[k] for k in FIELDS}):
        raise ValueError('continuation state is not BIT_IDENTICAL')
    baseline = read(control / 'COMPLETE.json')
    split = read(resumed / 'COMPLETE.json')
    if baseline['binding']['evaluation_steps'] != [3, 6] or split['binding']['evaluation_steps'] != [3, 6]:
        raise ValueError('two full smoke evaluations required')
    if baseline['binding']['mock'] or split['binding']['mock']:
        raise ValueError('mock cannot qualify real CUDA smoke')
    if baseline['binding']['runtime'] != split['binding']['runtime']:
        raise ValueError('control and resumed data differ')
    allocations = [read(p) for p in resumed.glob('ALLOCATION_*.json')]
    if not any(int(x['restart_count']) >= 1 for x in allocations):
        raise ValueError('actual scheduler restart evidence missing')
    forced = forced_requeue_proof(resumed, allocations)
    forced_state = torch.load(forced['archived_checkpoint']['path'], map_location='cpu', weights_only=False)
    if (forced_state['global_step'] != 3 or forced_state['state_sha256'] != trainer.checkpoint_state_sha256(forced_state)):
        raise ValueError('invalid forced requeue checkpoint')
    if a['binding']['device'] != 'cuda' or a['binding']['workers'] != 6 or a['binding']['width_mult'] != 1.0:
        raise ValueError('smoke did not use S1 width1/CUDA/six-worker profile')
    if a['binding'] != b['binding']:
        raise ValueError('smoke parameters differ')
    for step in (3, 6):
        left = read(control / 'eval' / ('step-%09d.json' % step))
        right = read(resumed / 'eval' / ('step-%09d.json' % step))
        if left['instruments'] != right['instruments']:
            raise ValueError('checkpoint metrics differ after requeue')
    from loss_journal import records
    plans = [v['binding']['loss_plan'] for v in (baseline, split)]
    if plans[0] != plans[1] or plans[0]['steps'] != [2, 4, 6]:
        raise ValueError('three loss evals straddling requeue required')
    for folder in (control, resumed):
        events, torn = records(folder / 'loss_eval.jsonl')
        if torn is not None or [v['step'] for v in events] != plans[0]['steps']:
            raise ValueError('missing/duplicate smoke loss point')
        for event in events:
            from common import bound
            bound(event['record'])
    for point in plans[0]['points']:
        name = 'step-%09d.json' % point['step']
        left, right = (read(folder / 'loss_eval' / name) for folder in (control, resumed))
        for key in ('step', 'drawn_lines', 'model_sha256', 'thresholds', 'instruments'):
            if left[key] != right[key]:
                raise ValueError('loss-only continuation differs: ' + key)
        if left['drawn_lines'] != point['drawn_lines']:
            raise ValueError('loss cadence draw count changed')
    atomic(out, dict(status='BIT_IDENTICAL', mock=False, fields=list(FIELDS),
        control=spec(control / 'COMPLETE.json'), resumed=spec(resumed / 'COMPLETE.json'),
        runtime_sha256=baseline['binding']['runtime']['sha256'],
        allocations=allocations, width_mult=1.0, loss_steps=plans[0]['steps'],
        full_steps=[3, 6], forced_requeue_step=3, forced_requeue=forced,
        package_sha256=sha(ROOT / 'PAYLOAD.json')))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--control', required=True)
    p.add_argument('--resumed', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    compare(a.control, a.resumed, a.out)

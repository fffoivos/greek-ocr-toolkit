"""Immutable, weights-only-loadable model archives at Stage C loss points.

The segment is durable first; archive -> point JSON -> append-only index follows.
One lane owns RUN.lock. Recovery validates existing bytes, never replaces them.
Optimizer/scheduler/RNG/cursor remain in segment.pt and the full CER archives.
"""
import os
from pathlib import Path
import time
from common import bound, sha, spec

SCHEMA = 'TRAIN_FULL-loss-checkpoint-v1'


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def validate(entry, trainer, *, step, drawn_lines, runtime_sha, model_sha=None, binding=None):
    path = bound(entry)
    ck = trainer.torch.load(path, map_location='cpu', weights_only=True)
    if (ck['schema'] != SCHEMA or ck['global_step'] != step or ck['drawn_lines'] != drawn_lines
            or ck['package_sha256'] != sha(Path(__file__).parent/'PAYLOAD.json')
            or ck['runtime_sha256'] != runtime_sha
            or ck['model_sha256'] != trainer.checkpoint_state_sha256(ck['model'])
            or (model_sha is not None and ck['model_sha256'] != model_sha)
            or (binding is not None and ck['config'] != binding)):
        raise ValueError('loss checkpoint state/config binding changed')
    import hashlib
    if hashlib.sha256(ck['codec_json'].encode()).hexdigest() != ck['codec_sha256']:
        raise ValueError('loss checkpoint codec binding changed')
    return ck


def retain(segment, step, runtime_sha, model_sha):
    """Return a SHA-bound archive and measured call cost; preserve RNG and mode."""
    started = time.monotonic()
    path = segment.path.parent / 'loss_checkpoints' / ('step-%09d.pt' % step)
    path.parent.mkdir(parents=True, exist_ok=True)
    created = not path.exists()
    if created:
        codec = Path(segment.args.codec).read_bytes()
        import hashlib
        # CPU copies cannot alias live training weights. Only primitives/tensors
        # are serialized, allowing torch.load(..., weights_only=True).
        ck = dict(schema=SCHEMA, global_step=step, drawn_lines=segment.draws,
            package_sha256=sha(Path(__file__).parent/'PAYLOAD.json'),
            runtime_sha256=runtime_sha, model_sha256=model_sha,
            model={k:v.detach().cpu().clone() for k,v in segment.model.state_dict().items()},
            config=segment.binding, codec_json=codec.decode(),
            codec_sha256=hashlib.sha256(codec).hexdigest(),
            arch=segment.args.arch, width_mult=segment.args.width_mult,
            head=segment.args.head, seed=segment.args.seed,
            resume_policy='model archive only; exact continuation uses segment.pt/full CER state')
        # Use the actual codec, independent of architecture/state-dict ordering.
        from train.cer import load_codec
        loaded_codec = load_codec(segment.args.codec)
        ck.update(n_classes=loaded_codec.n_classes, codec_version=loaded_codec.version)
        tmp = path.with_suffix('.pt.tmp')
        with tmp.open('wb') as stream:
            segment.t.torch.save(ck, stream)
            stream.flush()
            os.fsync(stream.fileno())
        tmp.replace(path)
        sync_dir(path.parent)
        sync_dir(path.parent.parent)
    entry = spec(path)
    validate(entry, segment.t, step=step, drawn_lines=segment.draws,
             runtime_sha=runtime_sha, model_sha=model_sha, binding=segment.binding)
    return entry, dict(seconds=time.monotonic()-started, created=created,
                       includes='CPU copy, serialize, fsync, rename, directory fsync, SHA and reload validation')

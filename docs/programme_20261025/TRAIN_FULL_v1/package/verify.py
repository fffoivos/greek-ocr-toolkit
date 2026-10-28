"""Offline payload verification, used again on the deployed compute node."""
from pathlib import Path
from common import read, sha

ROOT = Path(__file__).resolve().parent


def restore_beta1(text):
    """Undo only the declared Stage B optimizer argument, for S1 byte proof."""
    return (text.replace('    p.add_argument("--beta1", type=float, default=0.9, help="AdamW beta1; beta2 stays 0.999")\n', '')
            .replace('    if not 0 <= args.beta1 < 1:\n        p.error("--beta1 must lie in [0,1)")\n', '')
            .replace(', betas=(args.beta1, 0.999)', ''))


def verify():
    payload = read(ROOT / 'PAYLOAD.json')
    for name, value in payload['files'].items():
        path = ROOT / name
        if path.stat().st_size != value['bytes'] or sha(path) != value['sha256']:
            raise ValueError('payload SHA mismatch: ' + name)
    # Original numerical modules remain byte-exact. Trainer edits: checkpoint
    # hook plus explicit beta1 (default .9, identical to AdamW's S1 default).
    upstream = read(ROOT / 'vendor/UPSTREAM.json')
    for name, value in upstream['files'].items():
        if name != 'train/train.py' and sha(ROOT / 'vendor' / name) != value:
            raise ValueError('unexpected S1 source change: ' + name)
    text = (ROOT / 'vendor/train/train.py').read_text()
    restored = restore_beta1(text).replace('if stopping or global_step-segment.last_save>=100 or segment.full_due(global_step):',
                            'if stopping or global_step-segment.last_save>=100:')
    import hashlib
    if hashlib.sha256(restored.encode()).hexdigest() != upstream['files']['train/train.py']:
        raise ValueError('trainer change exceeds declared checkpoint hook + beta1 argument')
    return payload


# Width/cadence change: old DATA may bind; old scientific smoke never may.
PARENT_SHA = '294c3458c0d1fbbb45c61dcac2e11e8fab92f1ce10558cf9576ecccaabd30aac'
X2_SHA = '0446ee734d2c867cda056973ce5052f917865f1f53ecc6c2b8301c99d437280f'
RUNTIME_SHA = '21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4'


def data_compatibility():
    """Exact width-independent preparation/audit proof; no smoke inheritance."""
    payload = verify()
    if sha(ROOT / 'x1_parent_payload.json') != X2_SHA or sha(ROOT / 'launch_parent_payload.json') != PARENT_SHA:
        raise ValueError('unrecognized data parent payload')
    parent = read(ROOT / 'x1_parent_payload.json')
    # All inputs and all data-producing code, including every frozen vendor
    # module and codec, must be byte-identical. Runtime environment is unchanged.
    names = {'common.py', 'horizon.py', 'manifest.py', 'prepare.py', 'prepare_job.py',
             'audit_job.py', 'audit.sbatch', 'prepare.sbatch', 'bind_config.py',
             'data.template.json', 'registry_v2.jsonl.gz', 'runtime_env.sh', 'job.sbatch'}
    names |= {n for n in parent['files'] if n.startswith('vendor/')}
    for name in names:
        current = payload['files'].get(name)
        if name == 'vendor/train/train.py':
            import hashlib
            restored_trainer = restore_beta1((ROOT / name).read_text()).encode()
            current = dict(bytes=len(restored_trainer), sha256=hashlib.sha256(restored_trainer).hexdigest())
        if current != parent['files'][name]:
            raise ValueError('data compatibility refused: ' + name)
        # The old runtime was created by the pre-format-fix package. Prove the
        # data-producing inputs also equal that original preparation package.
        if name != 'job.sbatch' and parent['files'][name] != read(ROOT / 'launch_parent_payload.json')['files'][name]:
            raise ValueError('data parent lineage changed: ' + name)
    old = read(ROOT / 'recipe.json')
    import copy
    restored = copy.deepcopy(old)
    if (restored['parameters']['width_mult'] != 1.0 or restored['loss_evaluation_every_drawn_lines'] != 50000
            or restored['loss_evaluation_at_end'] is not True or restored['source']['cell'] != 'w1/ref_364871/seed0'):
        raise ValueError('unexpected x1 recipe')
    restored['parameters']['width_mult'] = 2.0
    del restored['loss_evaluation_every_drawn_lines']
    del restored['loss_evaluation_at_end']
    del restored['source']['cell']
    # Compare parsed recipe identity to the exact preserved parent recipe.
    parent_recipe = read(ROOT / 'x2_recipe.json')
    if sha(ROOT / 'x2_recipe.json') != parent['files']['recipe.json']['sha256'] or restored != parent_recipe:
        raise ValueError('data-relevant recipe changed')
    return dict(parent_sha256=X2_SHA, prepared_package_sha256=PARENT_SHA,
                unchanged_data_files=sorted(names),
                trainer_identity='vendor trainer restored by undoing only beta1 parser/validation/explicit betas; original data path unchanged',
                recipe_changes=['width_mult 2 -> 1', 'drawn-line loss cadence added', 'S1 reference cell named'],
                inherited='audit/runtime/pools only; no x2 smoke, review or training state')


def data_package_matches(value, runtime_path=None):
    if value == sha(ROOT / 'PAYLOAD.json'):
        return True
    if value != PARENT_SHA:
        return False
    data_compatibility()
    if runtime_path is None or sha(runtime_path) != RUNTIME_SHA:
        raise ValueError('only the exact prepared005 runtime may be inherited')
    return True


def package_matches(value):
    """Scientific smoke/review must come from THIS package, never the x2 run."""
    return value == sha(ROOT / 'PAYLOAD.json')


if __name__ == '__main__':
    verify()
    print('TRAIN_FULL_PAYLOAD_VERIFIED')

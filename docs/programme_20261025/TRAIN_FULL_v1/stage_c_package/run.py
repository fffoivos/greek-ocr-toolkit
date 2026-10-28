"""Run the frozen S1 training body with a SHA-bound population adapter.

The single vendor trainer edit schedules the new checkpoint hook. All model,
optimizer, scheduler, assembly, sampler, loss and continuation math is S1 code.
"""
import argparse
import copy
from pathlib import Path
import sys

from common import atomic, bound, digest, read, schedule, sha, spec
from horizon import resolve, verify_full_pass

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'vendor'))


def load_pools(runtime, names=None):
    import pyarrow.parquet as pq
    pools = {}
    for name, pool in runtime['pools'].items():
        if names is not None and name not in names:
            continue
        data = [r for file in pool['files'] for r in pq.read_table(bound(file)).to_pylist()]
        if len(data) != pool['rows']:
            raise ValueError('pool count mismatch: ' + name)
        pools[name] = data
    return pools


def install(runtime_path, *, evaluator=None, study=False, selection_pool=None):
    from train import train as trainer
    import s1_segment
    from full_hook import segment_class
    runtime_path = Path(runtime_path)
    runtime = read(runtime_path)
    runtime['_sha256'] = sha(runtime_path)
    panels = ('seal04_dev', 'harvest_dev') if study else None
    names = {c['name'] for c in runtime['components']} | set(panels) if study else None
    pools = load_pools(runtime, names)
    selection = 'seal04_dev' if study else (selection_pool or 'validation')
    if selection not in ('validation', 'seal04_dev'):
        raise ValueError('unsupported selection pool')
    if selection == 'seal04_dev':
        # S1's epoch diagnostic requires split=val. This is an in-memory role
        # view of the exact seal04 dev bytes/labels, never an evaluation filter.
        pools['validation'] = [dict(r, split='val') for r in pools['seal04_dev']]
    selection_binding = dict(name=selection, pool=runtime['pools'][selection],
        rows=len(pools['validation']),
        identity_sha256=digest([(r['line_id'], r['label_ids']) for r in pools['validation']]), role='val',
        rule='best.pt and bad_epochs use only this loader CER; tests report only')
    mix = dict(seed=runtime['seed'], codec_version=runtime['codec_version'], components=runtime['components'])
    if sum(c['fraction'] for c in mix['components'] if c['kind'] == 'synthetic') != .5:
        raise ValueError('S1 synthetic fraction changed')

    def validate(path, **kwargs):
        if Path(path).resolve() != runtime_path.resolve() or sha(path) != runtime['_sha256']:
            raise ValueError('training input is not the bound prepared runtime')
        return mix

    def load_rows(mix, split):
        if split == 'val':
            return [pools['validation']]
        if split != 'train':
            raise ValueError('transfer is not configured')
        return [pools[c['name']] for c in mix['components']]

    def provenance(args, mix, assembled):
        for epoch, roles in assembled.items():
            if 'train' in roles:
                rr = roles['train']
                real = [r for r in rr if mix['components'][r['_component']]['kind'] == 'real']
                if (len(real) * 2 != len(rr)
                        or sum(r.get('source_dataset') == 'parliament_proceedings_1975_2000' for r in real) * 4 > len(real)):
                    raise ValueError('S1 half-synthetic/parliament draw policy violated')
                if (not study and not runtime.get('mock') and not args.full_smoke
                        and runtime.get('horizon_recipe', 'full') != 's1-literal'):
                    counts = __import__('collections').Counter((r['_component'], r['_pool_index']) for r in real)
                    if len(counts) != runtime['train_rows'] or any(n != 1 for n in counts.values()):
                        raise ValueError('epoch is not exactly one pass over unique real TRAIN rows')
        return dict(schema_version=1, git_head=runtime.get('producing_commit', 'prepared-uncommitted'),
            mix=read(runtime_path), mix_sha256=runtime['_sha256'], resolved_mix=mix,
            # These fields are validated by the original Segment constructor.
            recipe_sha256s=[digest(dict(hook=sha(ROOT / 'full_hook.py'), run=sha(__file__),
                                        data=runtime['_sha256']))],
            validation=runtime['pools'][selection],
            epochs={str(epoch): {role: dict(rows=len(rr), distinct_lines=len({r['line_id'] for r in rr}),
                real_rows=sum(mix['components'][r['_component']]['kind'] == 'real' for r in rr) if role == 'train' else len(rr),
                draw_sha256=digest([
                (r['line_id'], r.get('_component'), r.get('_pool_index')) for r in rr]))
                for role, rr in roles.items()} for epoch, roles in assembled.items()})

    trainer.full_selection = selection_binding
    trainer.full_pools = pools
    trainer.validate = validate
    trainer.load_rows = load_rows
    trainer.shared_validation = lambda args, mix: pools['validation']
    trainer.training_provenance = provenance
    base = s1_segment.Segment
    s1_segment.Segment = segment_class(base, runtime, pools,
        **({'panels': panels} if study else {}), **({'evaluator': evaluator} if evaluator else {}))
    return trainer, runtime


def execute(runtime_path, output, *, smoke=False, mock=False):
    if not mock:
        from verify import verify, data_package_matches
        verify()
    trainer, runtime = install(runtime_path)
    if bool(runtime.get('mock')) != mock:
        raise ValueError('mock/production mismatch')
    if not mock:
        if not data_package_matches(runtime.get('package_sha256'), runtime_path):
            raise ValueError('prepared runtime belongs to another package')
        trainer._runtime()
        if str(trainer.torch.__version__) != '2.11.0+cu128' or trainer.torch.version.cuda != '12.8':
            raise ValueError('S1 torch/CUDA runtime changed; qualify before changing the recipe')
        if (trainer.torch.backends.cudnn.version() != 91900
                or trainer.torch.cuda.get_device_name(0) != 'NVIDIA GH200 120GB'):
            raise ValueError('S1 cuDNN/GH200 profile changed; qualify before changing the recipe')
    cfg = read(ROOT / 'recipe.json')
    options = copy.deepcopy(cfg['parameters'])
    horizon = None
    if not mock:
        horizon = resolve(cfg, runtime['train_rows'], runtime.get('horizon_recipe', 'full'))
        if runtime.get('horizon') != horizon:
            raise ValueError('prepared horizon differs from audited recipe/count')
        options.update(epochs=horizon['epochs'], epoch_rows=horizon['epoch_rows'])
        if horizon['choice'] != 's1-literal':
            verify_full_pass(runtime['components'],
                {name: pool['rows'] for name, pool in runtime['pools'].items()}, runtime['train_rows'])
    options.update(mix=str(Path(runtime_path).resolve()), val_mix=str(Path(runtime_path).resolve()),
                   codec=str(ROOT / 'vendor/codec/v2.1.json'), out_dir=str(Path(output).resolve()))
    if smoke:
        # Explicitly diagnostic: real model/profile, small draw horizon only.
        options.update(epochs=2, epoch_rows=192)
    if mock:
        options.update(epochs=2, epoch_rows=256, device='cpu', workers=0, pin_memory=False)
    argv = []
    for key, value in options.items():
        if value is True:
            argv.append('--' + key.replace('_', '-'))
        elif value is not None and value is not False:
            argv.extend(['--' + key.replace('_', '-'), str(value)])
    args = trainer.parse_args(argv)
    args.full_every = 3 if smoke else 2 if mock else cfg['evaluation_every_updates']
    args.full_smoke = smoke
    from loss_cadence import plan
    # This planning uses only private sampler RNGs. The original trainer will
    # initialize its own RNG identically after this read-only preflight.
    trainer._runtime()
    args.loss_plan = plan(trainer, runtime, trainer.full_pools, args.epochs, args.epoch_rows,
                          args.bs, 128 if (smoke or mock) else cfg['loss_evaluation_every_drawn_lines'])
    # Fixed eight-epoch horizon; tests never govern stopping. See recipe table.
    trainer.PATIENCE = args.epochs + 1
    total = args.epochs * ((args.epoch_rows + args.bs - 1) // args.bs)
    Path(output).mkdir(parents=True, exist_ok=True)
    (Path(output) / 'eval').mkdir(exist_ok=True)
    binding = dict(runtime=spec(runtime_path), recipe=spec(ROOT / 'recipe.json'),
        total_updates=total, evaluation_steps=schedule(total, args.full_every), smoke=smoke, mock=mock,
        production_horizon=horizon, loss_plan=args.loss_plan)
    path = Path(output) / 'RUN_BINDING.json'
    if path.exists() and read(path) != binding:
        raise ValueError('run/config binding changed')
    atomic(path, binding)
    atomic(Path(output) / 'LOSS_CADENCE.json', args.loss_plan)
    status = trainer.train(args)
    if status == 0:
        import torch
        state = torch.load(Path(output) / 'segment.pt', map_location='cpu', weights_only=False)
        if state['global_step'] != total:
            raise ValueError('training returned before full horizon')
        eval_files = [Path(output) / 'eval' / ('step-%09d.json' % s) for s in schedule(total, args.full_every)]
        for file in eval_files:
            read(file)
        loss_files = [Path(output) / 'loss_eval' / ('step-%09d.json' % s) for s in args.loss_plan['steps']]
        from loss_journal import records
        entries, torn = records(Path(output) / 'loss_eval.jsonl')
        if torn is not None or [r['step'] for r in entries] != args.loss_plan['steps']:
            raise ValueError('missing/duplicate loss journal points')
        for expected, file in zip(args.loss_plan['points'], loss_files):
            result = read(file)
            if result['step'] != expected['step'] or result['drawn_lines'] != expected['drawn_lines']:
                raise ValueError('loss evaluation differs from drawn-line schedule')
        atomic(Path(output) / 'COMPLETE.json', dict(binding=binding, checkpoint=spec(Path(output) / 'segment.pt'),
            evaluations=[spec(p) for p in eval_files], loss_evaluations=[spec(p) for p in loss_files],
            loss_journal=spec(Path(output) / 'loss_eval.jsonl'), state_sha256=state['state_sha256']))
    return status


def plan_only(runtime_path, output):
    """CPU-only exact production step list; read only narrow parquet columns."""
    import pyarrow.parquet as pq
    from train import train as trainer
    from loss_cadence import plan
    from verify import verify, data_package_matches
    verify()
    runtime = read(runtime_path)
    if runtime.get('mock') or not data_package_matches(runtime.get('package_sha256'), runtime_path):
        raise ValueError('real prepared data required')
    pools = {c['name']: [r for file in runtime['pools'][c['name']]['files']
                        for r in pq.read_table(bound(file), columns=['line_id', 'width']).to_pylist()]
             for c in runtime['components']}
    recipe = read(ROOT / 'recipe.json')
    h = resolve(recipe, runtime['train_rows'], runtime.get('horizon_recipe', 'full'))
    if h != runtime['horizon']:
        raise ValueError('prepared horizon changed')
    trainer._runtime()
    result = plan(trainer, runtime, pools, h['epochs'], h['epoch_rows'],
                  recipe['parameters']['bs'], recipe['loss_evaluation_every_drawn_lines'])
    atomic(output, dict(**result, runtime=spec(runtime_path), recipe=spec(ROOT / 'recipe.json')))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--runtime', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--smoke', action='store_true')
    p.add_argument('--plan-only', action='store_true')
    a = p.parse_args()
    if a.plan_only:
        plan_only(a.runtime, a.out)
    else:
        raise SystemExit(execute(a.runtime, a.out, smoke=a.smoke))

"""Emit the exact post-dedupe population and a smoke-informed forecast."""
import argparse
from pathlib import Path
from common import atomic, read, schedule, spec
from horizon import resolve


def readout(manifest, runtime, output, smoke_control=None):
    m = read(manifest)
    rt = read(runtime)
    if m['fixture'] or rt['mock']:
        raise ValueError('mock counts cannot describe the full dataset')
    historical = read(Path(__file__).with_name('s1_w1_timing.json'))
    step = historical['seconds_per_update_including_epoch_validation']
    checkpoint, validation, startup = 1.6060056961141527, 19.770273582078516, 175.89016032603104
    evaluation, loss_evaluation, smoke_step = None, None, None
    if smoke_control:
        from common import bound, sha
        smoke = read(Path(smoke_control) / 'COMPLETE.json')
        if (smoke['binding']['mock'] or not smoke['binding']['smoke']
                or smoke['binding']['runtime']['sha256'] != sha(runtime)):
            raise ValueError('real same-data x1 smoke required')
        if smoke['binding']['recipe']['sha256'] != sha(Path(__file__).with_name('recipe.json')):
            raise ValueError('smoke recipe differs')
        evaluation = max(read(bound(p))['elapsed_seconds'] for p in smoke['evaluations'])
        loss_evaluation = max(read(bound(p))['elapsed_seconds'] for p in smoke['loss_evaluations'])
        timings = [read(p) for p in Path(smoke_control).glob('BATCH_TIMING_*.json')]
        seconds = sum(r['seconds'] for r in timings)
        samples = sum(r['samples'] for r in timings)
        if not samples:
            raise ValueError('smoke did not measure training update cost')
        smoke_step = seconds / samples
    forecasts = []
    recipe = read(Path(__file__).with_name('recipe.json'))
    if rt['train_rows'] != m['train_unique']:
        raise ValueError('prepared count differs from audited union')
    for choice in ('full', 's1-literal', 'longer'):
        horizon = resolve(recipe, m['train_unique'], choice)
        epochs, updates = horizon['epochs'], horizon['total_updates']
        evals = horizon['checkpoint_steps']
        # Width-independent draw count determines the number of threshold
        # crossings; partial batches affect only their exact update locations.
        every = recipe['loss_evaluation_every_drawn_lines']
        loss_evals = (horizon['mixed_draws'] + every - 1) // every
        update_time = smoke_step if smoke_step is not None else step
        compute = updates * update_time + (updates // 100 + epochs + loss_evals) * checkpoint + epochs * validation + startup
        extra = loss_evals * loss_evaluation + len(evals) * evaluation if evaluation is not None else None
        fraction = loss_evals * loss_evaluation / (updates * update_time) if loss_evaluation is not None else None
        total_fraction = extra / (updates * update_time) if extra is not None else None
        forecasts.append(dict(**horizon, updates=updates, loss_evaluations=loss_evals,
            optimizer_hours=updates * update_time / 3600,
            historical_s1_w1_epoch_wall_projection_hours=updates * step / 3600,
            smoke_mean_update_seconds=smoke_step,
            estimated_gpu_hours=(compute + extra) / 3600 if extra is not None else None,
            evaluation_seconds_from_real_smoke=evaluation,
            loss_evaluation_seconds_from_real_smoke=loss_evaluation,
            projected_loss_eval_hours=loss_evals * loss_evaluation / 3600 if loss_evaluation is not None else None,
            projected_loss_eval_fraction_of_training=fraction,
            projected_total_eval_hours=extra / 3600 if extra is not None else None,
            projected_total_eval_fraction_of_training=total_fraction,
            exceeds_25_percent=total_fraction > .25 if total_fraction is not None else None,
            options_if_over_25_percent=[
                'Keep every 50000 lines and reserve the measured overhead (owner choice).',
                'Owner may explicitly choose a larger drawn-line interval; reseal and review.',
                'Qualify a faster complete-instrument evaluator with exact loss parity; no silent subsampling.'],
            training_recovery_startup_validation_hours=compute / 3600,
            minimum_12h_segments=__import__('math').ceil((compute + extra) / (12 * 3600)) if extra is not None else None,
            estimate_status='projection; tiny x1 smoke widths may differ from full run; checkpoint/startup constants are S1 width2 allowances; queue, production iterator/replay and preemptions extra'))
    result = dict(schema='TRAIN_FULL-owner-readout-v1', manifest=spec(manifest), runtime=spec(runtime),
        dataset_unique_crops=m['dataset_unique_crops'], train_unique=m['train_unique'],
        dataset_retained_rows=m['dataset_retained_rows'], by_split=m['dataset_by_split'],
        unique_by_split=m['dataset_unique_by_split'], unique_population_table=m['unique_population_table'],
        s1_comparison=m['s1_comparison'],
        external_seal04_instruments=m['external_seal04_instruments'],
        duplicate_train_rows=m['duplicate_train_rows'], population_table=m['after'],
        forecasts=forecasts, default_requested_gpu_hours_per_segment=12,
        selected_horizon=rt['horizon'],
        budget=dict(cap=350, historical_used=118.995, historical_remaining=231.005,
            status='historical 22 October snapshot; refresh scoped sacct before launch'))
    atomic(output, result)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--manifest', required=True)
    p.add_argument('--runtime', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--smoke-control')
    a = p.parse_args()
    readout(a.manifest, a.runtime, a.out, a.smoke_control)

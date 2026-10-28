"""Owner correction: x1, actual drawn lines, loss only, exact continuation."""
import json
import os
from pathlib import Path
import signal
import sys
import time

import pytest

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(PKG / 'vendor'))
from common import atomic, read, sha
from loss_journal import append_point, records
from test_package import mock_runtime, spawn


def test_smoke_authenticates_forced_yield_against_immutable_step3(tmp_path):
    from compare import forced_requeue_proof
    from common import spec
    archive = tmp_path / 'checkpoints/step-000000003.pt'
    archive.parent.mkdir()
    archive.write_bytes(b'step3')
    rolling = tmp_path / 'segment.pt'
    rolling.write_bytes(b'step3')
    atomic(tmp_path / 'SEGMENT_YIELD.json', dict(job_id='123', restart_count='0', checkpoint=spec(rolling)))
    allocations = [dict(job_id='123', restart_count='0', mode='smoke-requeue'),
                   dict(job_id='123', restart_count='1', mode='smoke-requeue')]
    rolling.write_bytes(b'final step6')
    assert forced_requeue_proof(tmp_path, allocations)['step'] == 3
    archive.write_bytes(b'wrong step')
    with pytest.raises(ValueError, match='step-3 checkpoint'):
        forced_requeue_proof(tmp_path, allocations)


def test_exact_s1_x1_parameters_and_width_independent_horizon():
    from horizon import resolve
    e = PKG.parent / 'evidence'
    original = read(e / 'w1_ref_364871_s0_E1_RUN_COMPLETE.json')
    params = original['binding']['parameters']
    recipe = read(PKG / 'recipe.json')
    for name, value in recipe['parameters'].items():
        assert value == (None if name == 'epoch_rows' else params[name]), name
    assert params['width_mult'] == 1.0
    assert original['artifact_hashes']['train_log.csv'] == sha(e / 'w1_ref_364871_s0.csv')
    cell = read(e / 'w1_CELL_COMPLETE.json')
    assert cell['completions']['w1_ref_364871_s0']['sha256'] == sha(e / 'w1_ref_364871_s0_E1_RUN_COMPLETE.json')
    h = resolve(recipe, 793227)
    assert h['total_updates'] == 198312 and h['mixed_draws'] == 12691632
    assert h['checkpoint_steps'] == [50000, 100000, 150000, 198312]
    assert (h['mixed_draws'] + 49999) // 50000 == 254
    assert h == resolve(read(PKG / 'x2_recipe.json'), 793227)


def test_draw_schedule_uses_shuffled_partial_batch_and_restores_rng():
    import random
    import numpy as np
    import torch
    from train import train as trainer
    from loss_cadence import plan
    trainer._runtime()
    runtime = dict(seed=20261015, components=[dict(name='real', fraction=.5), dict(name='syn', fraction=.5)])
    pools = {name: [dict(width=64 + (i % 3) * 128, line_id=f'{name}-{i}') for i in range(85)]
             for name in ('real', 'syn')}
    before = (random.getstate(), np.random.get_state(), torch.get_rng_state())
    p = plan(trainer, runtime, pools, 3, 170, 64, 50)
    after = (random.getstate(), np.random.get_state(), torch.get_rng_state())
    assert before[0] == after[0] and np.array_equal(before[1][1], after[1][1]) and torch.equal(before[2], after[2])
    assert p['total_drawn_lines'] == 510 and p['total_updates'] == 9
    assert p['steps'] == sorted(set(p['steps']))
    assert p['points'][-1]['step'] == 9
    assert [t for r in p['points'] for t in r['thresholds']] == list(range(50, 501, 50))
    assert any(r['drawn_lines'] != r['step'] * 64 for r in p['points'])
    assert p == plan(trainer, runtime, pools, 3, 170, 64, 50)


def test_loss_evaluator_never_decodes_and_matches_full_loss(tmp_path, monkeypatch):
    import torch
    import train.cer
    import bench.score
    from train.cer import load_codec
    from run import load_pools
    from full_hook import evaluate_panel
    runtime = mock_runtime(tmp_path)
    rr = load_pools(read(runtime))['seal04_test']
    codec = load_codec(str(PKG / 'vendor/codec/v2.1.json'))
    class Toy(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.p = torch.nn.Parameter(torch.zeros(1))
        def forward(self, x):
            return (torch.zeros(len(x), x.shape[-1] // 4, codec.n_classes) + self.p).log_softmax(-1)
    model = Toy()
    refs = {r['line_id']: 'ABC' for r in rr}
    full, _ = evaluate_panel(model, rr, refs, codec, torch.device('cpu'))
    def refuse(*a, **k):
        pytest.fail('loss-only evaluation attempted decoding/scoring')
    monkeypatch.setattr(train.cer, 'greedy_decode_line', refuse)
    monkeypatch.setattr(bench.score, 'aggregate', refuse)
    loss, predictions = evaluate_panel(model, rr, refs, codec, torch.device('cpu'), decode=False)
    assert predictions == [] and 'score' not in loss
    assert loss['rows'] == len(rr) and loss['ctc_loss'] == full['ctc_loss']


@pytest.mark.parametrize('torn', [b'{"ste', b'{"ste\n', b''])
def test_append_only_journal_recovers_missing_index_and_torn_tail(tmp_path, torn):
    journal = tmp_path / 'loss_eval.jsonl'
    point = tmp_path / 'point.json'
    atomic(point, dict(step=2, drawn_lines=128, instruments={'test': dict(ctc_loss=1., rows=5)}))
    journal.write_bytes(torn)
    append_point(journal, point)
    first = journal.read_bytes()
    assert first.startswith(torn)
    append_point(journal, point)
    assert journal.read_bytes() == first
    entries, pending = records(journal)
    assert pending is None and [r['step'] for r in entries] == [2]
    atomic(point, dict(step=2, drawn_lines=129, instruments={}))
    with pytest.raises(ValueError, match='changed'):
        append_point(journal, point)


@pytest.mark.parametrize('kill_step', [2, 4, 8])
def test_kill_after_loss_before_full_eval_has_no_missing_or_duplicate_points(tmp_path, kill_step):
    runtime = mock_runtime(tmp_path)
    output = tmp_path / 'split'
    c = spawn(runtime, output, {'TRAIN_FULL_TEST_PAUSE_LOSS_STEP': str(kill_step)})
    deadline = time.monotonic() + 40
    while not (output / 'TEST_PAUSED.json').exists() and c.poll() is None and time.monotonic() < deadline:
        time.sleep(.05)
    if not (output / 'TEST_PAUSED.json').exists():
        c.kill(); c.wait(timeout=5)
        pytest.fail((output / 'process.log').read_text())
    os.kill(c.pid, signal.SIGKILL)
    c.wait(timeout=5)
    initial = (output / 'loss_eval.jsonl').read_bytes()
    c = spawn(runtime, output)
    assert c.wait(timeout=40) == 0, (output / 'process.log').read_text()
    assert (output / 'loss_eval.jsonl').read_bytes().startswith(initial)
    events, torn = records(output / 'loss_eval.jsonl')
    assert torn is None and [r['step'] for r in events] == [2, 4, 6, 8]
    assert [r['drawn_lines'] for r in events] == [128, 256, 384, 512]
    complete = read(output / 'COMPLETE.json')
    assert len(complete['loss_evaluations']) == 4 and len(complete['evaluations']) == 4


def test_periodic_loss_evaluation_does_not_change_training_trajectory(tmp_path):
    import torch
    from train import train as trainer
    from compare import FIELDS
    trainer._runtime()
    runtime = mock_runtime(tmp_path)
    outputs = [tmp_path / 'periodic', tmp_path / 'final-only']
    for out, env in zip(outputs, ({}, {'TEST_LOSS_EVERY': '100000'})):
        c = spawn(runtime, out, env)
        assert c.wait(timeout=40) == 0, (out / 'process.log').read_text()
    states = [torch.load(o / 'segment.pt', map_location='cpu', weights_only=False) for o in outputs]
    assert trainer.checkpoint_state_sha256({k: states[0][k] for k in FIELDS}) == trainer.checkpoint_state_sha256({k: states[1][k] for k in FIELDS})
    assert len(read(outputs[0] / 'COMPLETE.json')['loss_evaluations']) == 4
    assert len(read(outputs[1] / 'COMPLETE.json')['loss_evaluations']) == 1


def test_unfinished_loss_eval_restarts_identically_without_publishing_partial_metrics(tmp_path):
    import torch
    from train import train as trainer
    from compare import FIELDS
    trainer._runtime()
    runtime = mock_runtime(tmp_path)
    output = tmp_path / 'interrupted'
    marker = tmp_path / 'loss-interrupted.txt'
    c = spawn(runtime, output, {'TEST_INTERRUPT_LOSS_MARKER': str(marker)})
    assert c.wait(timeout=40) != 0 and marker.exists()
    assert not (output / 'loss_eval/step-000000002.json').exists()
    assert not (output / 'loss_eval.jsonl').exists()
    c = spawn(runtime, output)
    assert c.wait(timeout=40) == 0, (output / 'process.log').read_text()
    control = tmp_path / 'control'
    c = spawn(runtime, control)
    assert c.wait(timeout=40) == 0, (control / 'process.log').read_text()
    states = [torch.load(o / 'segment.pt', map_location='cpu', weights_only=False) for o in (control, output)]
    assert trainer.checkpoint_state_sha256({k: states[0][k] for k in FIELDS}) == trainer.checkpoint_state_sha256({k: states[1][k] for k in FIELDS})
    assert records(output / 'loss_eval.jsonl')[0][0]['step'] == 2


@pytest.mark.parametrize('loss_seconds,exceeds', [(1., False), (18., True), (100., True)])
def test_forecast_reports_measured_complete_eval_cost_and_options(tmp_path, loss_seconds, exceeds):
    from readout import readout
    from common import spec
    # Explicit forecast fixtures, not exported scientific or CUDA evidence.
    m = dict(fixture=False, train_unique=793227, dataset_unique_crops=862423,
        dataset_retained_rows=862424, dataset_by_split={}, dataset_unique_by_split={},
        unique_population_table=[], s1_comparison=[], external_seal04_instruments={},
        duplicate_train_rows=2, after=[])
    manifest, runtime = tmp_path / 'manifest.json', tmp_path / 'runtime.json'
    atomic(manifest, m)
    atomic(runtime, dict(mock=False, train_rows=793227, horizon={}))
    smoke = tmp_path / 'smoke'
    smoke.mkdir()
    atomic(smoke / 'loss.json', dict(elapsed_seconds=loss_seconds))
    atomic(smoke / 'full.json', dict(elapsed_seconds=150.))
    atomic(smoke / 'BATCH_TIMING_1.json', dict(seconds=.4, samples=4))
    atomic(smoke / 'COMPLETE.json', dict(binding=dict(mock=False, smoke=True,
        runtime=spec(runtime), recipe=spec(PKG / 'recipe.json')),
        evaluations=[spec(smoke / 'full.json')], loss_evaluations=[spec(smoke / 'loss.json')]))
    report = readout(manifest, runtime, tmp_path / 'forecast.json', smoke)
    f = report['forecasts'][0]
    assert f['loss_evaluations'] == 254
    assert f['projected_loss_eval_hours'] == 254 * loss_seconds / 3600
    assert f['projected_total_eval_hours'] == (254 * loss_seconds + 4 * 150) / 3600
    assert f['exceeds_25_percent'] == exceeds
    assert len(f['options_if_over_25_percent']) == 3
    assert f['minimum_12h_segments'] >= 1

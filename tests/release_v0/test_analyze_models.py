"""Tiny, offline fixtures only. Run with --confcutdir=tests/release_v0.

The repository-wide conftest provisions an unrelated native predictor; isolating
this test directory avoids that build and keeps REL0-S1 tests strictly tiny.
"""
from collections import OrderedDict
import importlib
import io
import json
from pathlib import Path
import sys
import subprocess
from types import SimpleNamespace
import unicodedata

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/release_v0'))
import analyze_models as a
import bench_speed as b

PACKAGE = ROOT / 'docs/programme_20261025/TRAIN_FULL_v1/stage_c_package'


@pytest.fixture(scope='module')
def sealed():
    return a.load_sealed(PACKAGE)


def line(ident, edits, units):
    return dict(id=ident, correct=edits == 0, metrics={m: dict(edits=edits, reference_units=units) for m in a.MODES})


def test_literal_scorer_reproduction_and_failure(sealed):
    scorer, _ = sealed
    pairs = [(dict(text='α\u0314\u0301'), 'α\u0301\u0314'),
             (dict(text='α\u0301\u0323'), 'α\u0323\u0301'),
             (dict(text='abc'), 'ab')]
    result = scorer.aggregate(pairs)
    assert result['cer']['nfd_atom'] == dict(edits=5, reference_units=9, rate=5/9)
    assert result['cer']['diacritic_insensitive']['edits'] == 1
    assert result['exact_lines'] == 1  # whole-string NFC repairs cross-ccc ordering only
    a.assert_reproduced(result, json.loads(json.dumps(result)), 'tiny')
    wrong = json.loads(json.dumps(result))
    wrong['cer']['nfd_atom']['edits'] += 1
    with pytest.raises(ValueError, match='SCORER REPRODUCTION MISMATCH'):
        a.assert_reproduced(result, wrong, 'tiny')


def test_breakdown_sums_error_ops_and_definitions(sealed):
    scorer, _ = sealed
    refs = ['α\u0314\u0301', '123', 'ΑΒ', 'abc1', '---', 'a\u0300']
    rows = {str(i): dict(line_id=str(i), text=r, source_dataset='s'+str(i % 2), script_class='greek') for i,r in enumerate(refs)}
    preds = {str(i): h for i,h in enumerate(['α\u0301', '12', 'ΑΓ', 'ab1x', '---', 'a'])}
    detail = a.detailed(rows, preds, scorer)
    aggregate = scorer.aggregate([(dict(text=rows[i]['text']),h) for i,h in preds.items()])
    for dimension, groups in detail['breakdowns'].items():
        assert sum(g['lines'] for g in groups.values()) == len(rows), dimension
        assert sum(g['exact_lines'] for g in groups.values()) == aggregate['exact_lines']
        for mode in a.MODES:
            assert sum(g['metrics'][mode]['edits'] for g in groups.values()) == aggregate['cer'][mode]['edits']
            assert sum(g['metrics'][mode]['reference_units'] for g in groups.values()) == aggregate['cer'][mode]['reference_units']
    assert sum(detail['error_types'].values()) == aggregate['cer']['nfd_atom']['edits']
    assert sum(detail['error_atom_classes'].values()) == sum(detail['error_types'].values())
    assert sum(detail['error_line_classes'].values()) == len(rows)
    assert detail['breakdowns']['polytonic']['true']['lines'] == 1
    assert detail['breakdowns']['all_caps']['true']['lines'] == 1
    assert set(detail['breakdowns']['content']) == {'digits_only', 'letters', 'mixed', 'other'}
    assert all(c['examples'] for c in detail['top_confusions'])


def test_bootstrap_deterministic_ratio_of_sums():
    left = [line('b', 3, 10), line('a', 0, 2), line('c', 1, 4)]
    right = [line('c', 0, 4), line('b', 1, 10), line('a', 1, 2)]
    x = a.paired_bootstrap(left, right, resamples=10000)
    assert x == a.paired_bootstrap(left[::-1], right[::-1], resamples=10000)
    assert x['difference'] == 2/16
    assert x['seed'] == 20261028 and x['resamples'] == 10000
    assert x['ci95'][0] <= x['difference'] <= x['ci95'][1]
    identical = a.paired_bootstrap(left, left)
    assert identical['ci95'] == [0., 0.]
    with pytest.raises(ValueError, match='ID mismatch'):
        a.paired_bootstrap(left, right[:-1])


def test_nfd_error_class_despite_nfc_exact(sealed):
    scorer, _ = sealed
    rows = {'id': dict(line_id='harvest:wave1:id', text='α\u0301\u0323', source_dataset='tiny', script_class='greek')}
    detail = a.detailed(rows, {'id':'α\u0323\u0301'}, scorer)
    assert detail['lines'][0]['correct'] and not detail['lines'][0]['nfd_exact']
    assert detail['error_line_classes']['diacritic_only'] == 1
    assert detail['breakdowns']['id_prefix']['harvest:wave1']['lines'] == 1


def test_cross_models_dev_only_bootstrap_and_id_lists():
    results = {}
    for i, label in enumerate(('w1h14-full', 'w1.5-full', 'w2-full')):
        results[label] = dict(selected_panels={p: dict(lines=[line('shared',1,5), line('one',int(i == 0),5)]) for p in a.PANELS})
    cross = a.cross_models(results, 4, 20)
    assert len(cross['bootstrap']) == 3
    assert all(set(v) == {'harvest_dev', 'seal04_dev', 'pooled_dev'} for v in cross['bootstrap'].values())
    for p, overlap in cross['overlap'].items():
        assert overlap['wrong_in_all'] == overlap['wrong_in_one'] == 1
        assert overlap['all_three_wrong_ids'] == (['shared'] if p.endswith('_dev') else None)
    assert all(v['pooled_dev']['lines'] == 4 for v in cross['bootstrap'].values())


def test_selection_strict_ties_rounding_and_mismatch():
    log = [dict(epoch=e, step=e*10, val_cer=str(.4 if e < 3 else .2)) for e in range(1,9)]
    meta = dict(select_metric='val_cer', best_epoch=3, best_metric=.2)
    exact = [dict(result=dict(cer=float(r['val_cer']))) for r in log]
    selected = a.selected_from_records(meta, log, exact)
    assert selected['epoch'] == 3 and selected['step'] == 30
    with pytest.raises(ValueError, match='strict-improvement'):
        a.selected_from_records(dict(meta, best_epoch=8), log, exact)
    with pytest.raises(ValueError, match='8 ordered'):
        a.selected_from_records(meta, log[:-1])
    with pytest.raises(ValueError, match='NO EXACT SELECTED PREDICTIONS'):
        a.match_selected(selected, 'a'*64, [dict(step=30, weight_sha256='b'*64)])
    with pytest.raises(ValueError, match='NO EXACT SELECTED PREDICTIONS'):
        a.match_selected(selected, 'a'*64, [dict(step=80, weight_sha256='a'*64)])
    assert a.match_selected(selected, 'a'*64, [dict(step=30, weight_sha256='a'*64)])['step'] == 30


@pytest.fixture
def tiny_run(tmp_path, sealed):
    import numpy as np
    import pyarrow as pa
    import pyarrow.parquet as pq
    import torch
    from PIL import Image
    scorer, cer = sealed
    trainer = importlib.import_module('train.train')
    trainer.torch, trainer.np = torch, np
    from train import ckpt_io
    codec_path = PACKAGE / 'vendor/codec/v2.1.json'
    codec = cer.load_codec(str(codec_path))
    ids = {ch:i for i,ch in enumerate(codec.atom_by_id)}
    root, data = tmp_path/'run', tmp_path/'data'
    root.mkdir()
    (root/'eval').mkdir()
    (root/'checkpoints').mkdir()
    pools, refs = {}, {}
    png = io.BytesIO()
    Image.new('L', (64,48), color=255).save(png, format='PNG')
    for panel in a.PANELS:
        path = data/panel/'part-00000.parquet'
        path.parent.mkdir(parents=True)
        rows = [dict(line_id=f's:{i}', gt_nfd=t, label_ids=[ids[c] for c in t], codec_version=codec.version,
                     source_dataset='tiny', script_class='greek', image_png=png.getvalue(), width=64)
                for i,t in enumerate(('α\u0314\u0301','123'))]
        pq.write_table(pa.Table.from_pylist(rows), path)
        pools[panel] = dict(files=[a.spec(path)], rows=len(rows))
        refs[panel] = {r['line_id']:r['gt_nfd'] for r in rows}
    runtime = dict(pools=pools, references=refs)
    runtime_path = data/'runtime.json'
    a.write(runtime_path, runtime)
    selection = dict(name='seal04_dev', pool=pools['seal04_dev'])
    config = dict(payload_sha256=a.sha(PACKAGE/'PAYLOAD.json'), runtime=a.spec(runtime_path),
                  parameters=dict(width_mult=1.5), selection_pool='seal04_dev', cer_steps=[20,40,60,80])
    a.write(root/'CLAIM.json', config)
    a.write(root/'RUN_BINDING.json', dict(config=config, selection=selection, evaluation_steps=config['cer_steps']))
    (root/'train_log.csv').write_text('epoch,step,val_cer\n'+''.join(f'{e},{e*10},{1/e:.6f}\n' for e in range(1,9)))
    meta = dict(select_metric='val_cer', best_epoch=8, best_metric=1/8, width_mult=1.5, param_count=4)
    for step in config['cer_steps']:
        ck = dict(epoch=step//10, global_step=step, model=OrderedDict(w=torch.full((2,2), float(step))),
                  arch='compact', head='nfd', codec_version=codec.version, codec_sha256=a.sha(codec_path),
                  width_mult=1.5, n_classes=codec.n_classes, best=dict(epoch=step//10, metric=10/step))
        ck['model']._metadata = {'': {'version': 1}}
        ck['state_sha256'] = trainer.checkpoint_state_sha256(ck)
        archive = root/'checkpoints'/f'step-{step:09d}.pt'
        torch.save(ck, archive)
        instruments, pred_files = {}, {}
        for panel in a.PANELS:
            preds = [dict(id=i,hyp=t if i.endswith('1') else 'α\u0301') for i,t in refs[panel].items()]
            path = root/'eval'/f'step-{step:09d}-{panel}.predictions.jsonl'
            path.write_text(''.join(json.dumps(p)+'\n' for p in preds))
            pred_files[panel] = a.spec(path)
            instruments[panel] = dict(rows=2, scorer=a.SCORER, score=scorer.aggregate([(dict(text=refs[panel][p['id']]),p['hyp']) for p in preds]))
        a.write(root/'eval'/f'step-{step:09d}.json', dict(step=step, checkpoint=a.spec(archive), state_sha256=ck['state_sha256'],
                 runtime_sha256=a.sha(runtime_path), instruments=instruments, prediction_files=pred_files))
    torch.save(ck, root/'best.pt')
    st_meta = {k:ck[k] for k in ('arch','head','codec_version','codec_sha256','width_mult','n_classes','epoch')}
    assert ckpt_io.save_safetensors(ck['model'], st_meta, str(root/'best.safetensors'))
    meta['best_pt_sha256'] = a.sha(root/'best.pt')
    a.write(root/'checkpoint_meta.json', meta)
    return dict(label='w1.5-full', run_dir=str(root), package=str(PACKAGE), width_mult=1.5), data


def test_selected_checkpoint_actual_weight_sha_and_mismatch(tiny_run):
    import torch
    run, data = tiny_run
    selection, entries, runtime, receipts = a.resolve_selected(run)
    assert selection['step'] == 80 and len(entries) == 4
    assert len(selection['weight_sha256']) == 64
    assert selection['safetensors']['bytes'] > 0
    # Tamper safe weights while retaining their legitimate epoch/codec metadata.
    from train import ckpt_io
    weights, md = ckpt_io.load_model_weights(str(Path(run['run_dir'])/'best.safetensors'))
    weights['w'] = weights['w'] + 1
    ckpt_io.save_safetensors(weights, md, str(Path(run['run_dir'])/'best.safetensors'))
    with pytest.raises(ValueError, match='weight SHA mismatch'):
        a.resolve_selected(run)


def test_selected_archive_weight_mismatch_fails_without_substitution(tiny_run):
    import numpy as np
    import torch
    run, _ = tiny_run
    root = Path(run['run_dir'])
    trainer = importlib.import_module('train.train')
    trainer.torch, trainer.np = torch, np
    path = root/'checkpoints/step-000000080.pt'
    ck = torch.load(path, map_location='cpu', weights_only=False)
    ck['model']['w'] += 1
    ck['state_sha256'] = trainer.checkpoint_state_sha256(ck)
    torch.save(ck, path)
    ep = root/'eval/step-000000080.json'
    entry = a.read(ep)
    entry.update(checkpoint=a.spec(path), state_sha256=ck['state_sha256'])
    a.write(ep, entry)
    with pytest.raises(ValueError, match='NO EXACT SELECTED PREDICTIONS'):
        a.resolve_selected(run)


def test_selected_step_has_no_prediction_archive(tiny_run):
    run, _ = tiny_run
    root = Path(run['run_dir'])
    ep = root/'eval/step-000000080.json'
    entry = a.read(ep)
    entry['step'] = 70
    a.write(ep, entry)
    binding = a.read(root/'RUN_BINDING.json')
    config = a.read(root/'CLAIM.json')
    config['cer_steps'][-1] = 70
    binding.update(config=config, evaluation_steps=config['cer_steps'])
    a.write(root/'CLAIM.json', config)
    a.write(root/'RUN_BINDING.json', binding)
    with pytest.raises(ValueError, match='NO EXACT SELECTED PREDICTIONS'):
        a.resolve_selected(run)


def test_tiny_worker_outputs_and_prediction_checksum(tiny_run, sealed, tmp_path):
    run, data = tiny_run
    out = a.prepare_output(tmp_path/'out', [run], data)
    args = SimpleNamespace(data_dir=data, jobs=1)
    a.worker(args, run, out)
    result = a.read(out/'analysis_w1.5-full.json')
    assert len(result['trajectory']) == 4 and result['status'] == 'PASS'
    assert set(result['selected_panels']) == set(a.PANELS)
    cross = a.cross_models({'w1.5-full':result}, 1, 10)
    report = a.render_report(dict(runs={'w1.5-full':result}, cross_model=cross, generated_at='fixture'))
    assert 'Test — report only' in report and 'Trajectory' in report and 'Speed' in report
    bad = Path(run['run_dir'])/'eval/step-000000080-harvest_dev.predictions.jsonl'
    bad.write_text(bad.read_text()+'\n')
    with pytest.raises(ValueError, match='input SHA mismatch'):
        a.analyze_panel((80,'harvest_dev',a.read(bad.parent/'step-000000080.json'),True))
    with pytest.raises(ValueError, match='must not be inside'):
        a.prepare_output(data/'bad-output', [run], data)


def test_bounded_fixed_sample_and_tiny_speed(tiny_run, sealed):
    import torch
    run, data = tiny_run
    _, _, runtime, _ = a.resolve_selected(run)
    rows, receipt = b.fixed_samples(data, runtime, count=2)
    assert receipt['ids'] == ['s:0','s:1'] and receipt['lines'] == 2
    from train import model as model_code, data as data_code
    _, cer = sealed
    codec = cer.load_codec(str(PACKAGE/'vendor/codec/v2.1.json'))
    class TinyModel(torch.nn.Module):
        def forward(self, x):
            z = torch.zeros(len(x), (x.shape[-1]+3)//4, codec.n_classes)
            z[:,:,1] = 1
            return z.log_softmax(-1)
    result = b.benchmark_case(torch, TinyModel().eval(), model_code, data_code, cer, codec, rows,
                              torch.device('cpu'), 'fp32', 1, 1, repeats=2, warmup_batches=1)
    assert result['status'] == 'PASS' and len(result['repeat_seconds']) == 2
    assert result['lines'] == 2 and result['ms_per_line'] > 0


def test_cli_fresh_process_and_parallel_panels(tiny_run, tmp_path):
    run, data = tiny_run
    path = tmp_path/'runs.json'
    a.write(path, [run])
    out = tmp_path/'cli-output'
    result = subprocess.run([sys.executable, '-B', str(ROOT/'scripts/release_v0/analyze_models.py'),
                             '--runs', str(path), '--data-dir', str(data), '--out', str(out),
                             '--jobs', '2', '--resamples', '20'], text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    summary = a.read(out/'SUMMARY.json')
    assert summary['status'] == 'PASS' and summary['bootstrap_resamples'] == 20
    assert a.read(out/'RECEIPT.json')['status'] == 'PASS'
    assert (out/'REPORT.md').exists()


def test_speed_collection_binding_grid_and_render(tiny_run, tmp_path):
    run, data = tiny_run
    out = a.prepare_output(tmp_path/'out', [run], data)
    a.worker(SimpleNamespace(data_dir=data, jobs=1), run, out)
    result = a.read(out/'analysis_w1.5-full.json')
    for mode in ('cpu','gpu'):
        grid = ([(t,'fp32',bs) for t in (1,8) for bs in (1,32)] if mode == 'cpu' else
                [(1,pr,bs) for pr in ('bf16','fp32') for bs in (1,32,256)])
        bench = dict(status='PASS', run=run, selection=result['selection'], repeats=5,
                     sample=dict(lines=2000, ids_sha256='fixed'), input_height=48,
                     hardware=dict(hostname='fixture', processor='tiny CPU', machine='tiny', torch_version='fixture', interop_threads=1),
                     cases=[dict(device='cpu' if mode == 'cpu' else 'cuda', precision=pr, threads=t, batch_size=bs,
                                 status='PASS', lines=2000, repeat_seconds=[1.]*5, ms_per_line=.5, lines_per_second=2000.) for t,pr,bs in grid])
        a.write(out/f'speed_w1.5-full_{mode}.json', bench)
    summary = dict(runs={'w1.5-full':result}, cross_model=a.cross_models({'w1.5-full':result},1,20), generated_at='fixture')
    summary['speed'] = a.collect_speed(summary,out)
    assert 'tiny CPU' in a.render_report(summary)
    path = out/'speed_w1.5-full_gpu.json'
    bad = a.read(path)
    bad['cases'].pop()
    a.write(path,bad)
    with pytest.raises(ValueError, match='incomplete benchmark grid'):
        a.collect_speed(summary,out)


def test_run_list_retired_x1_rejected(tmp_path):
    path = tmp_path/'runs.json'
    a.write(path, [dict(label='w1-full', run_dir='/tmp/full-v1-013-stage-c-sel/w1-full',package='/tmp/pkg',width_mult=1)])
    with pytest.raises(ValueError, match='retired'):
        a.run_list(path)

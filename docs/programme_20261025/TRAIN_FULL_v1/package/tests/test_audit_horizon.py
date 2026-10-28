"""Resume-brief gates: real-population horizon, exact quotas, diagnostic CPU audit."""
from pathlib import Path
import sys

import pytest

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
from common import atomic, bound, read, rows, sha, spec, write_rows
from horizon import resolve, verify_full_pass
from manifest import Registry, build, combine, harvest_rows
from test_package import book, row
from test_rehearsal import tiny_inputs


def test_audited_count_drives_default_and_sealed_alternatives():
    recipe = read(PKG / 'recipe.json')
    full = resolve(recipe, 364871 + 417280)
    assert full['epoch_rows'] == 1564302
    assert full['steps_per_epoch'] == 24443
    assert full['total_updates'] == full['onecycle_total_steps'] == 195544
    assert full['checkpoint_steps'] == [50000, 100000, 150000, 195544]
    assert full['real_draws'] == 8 * 782151
    # Dedupe changes both schedule and terminal evaluation, never stale nominal counts.
    smaller = resolve(recipe, 700000)
    assert smaller['total_updates'] == 175000
    assert smaller['checkpoint_steps'] == [50000, 100000, 150000, 175000]
    literal = resolve(recipe, 782151, 's1-literal')
    assert literal['total_updates'] == 53616 and not literal['default']
    longer = resolve(recipe, 782151, 'longer')
    assert longer['total_updates'] == 293316
    assert longer['checkpoint_steps'] == [50000, 100000, 150000, 200000, 250000, 293316]


def test_unchanged_sampler_full_unique_real_coverage_each_epoch():
    sys.path.insert(0, str(PKG / 'vendor'))
    from train.mix import assemble
    groups = [[dict(line_id=f'non-{i}') for i in range(17)],
              [dict(line_id=f'parl-{i}') for i in range(4)], [dict(line_id='synthetic')]]
    comp = [dict(name='non', kind='real', fraction=.5 * 17 / 21),
            dict(name='parl', kind='real', fraction=.5 * 4 / 21),
            dict(name='syn', kind='synthetic', fraction=.5)]
    result = verify_full_pass(comp, dict(non=17, parl=4, syn=1), 21)
    assert result['component_draws'] == dict(non=17, parl=4, syn=21)
    for epoch in range(1, 9):
        selected, counts = assemble(groups, [c['fraction'] for c in comp], 20261015, epoch, 42, exact_rows=True)
        assert counts == [17, 4, 21]
        real = [r['line_id'] for r in selected if r['_component'] < 2]
        assert len(real) == len(set(real)) == 21
    with pytest.raises(ValueError, match='conflicts with unchanged S1 source quotas'):
        verify_full_pass([dict(name='non', kind='real', fraction=.375),
                          dict(name='parl', kind='real', fraction=.125),
                          dict(name='syn', kind='synthetic', fraction=.5)],
                         dict(non=5, parl=5, syn=1), 10)


def test_diagnostic_scan_reports_all_collisions_without_clearing_leakage():
    reg = Registry([book(), book('book-b', 'dev', 'ed-b')])
    a = row(item='same-provider')
    b = row('b', 'a' * 64, 'dev', 'book-b', 'ed-b', item='same-provider')
    c = dict(row(), text='conflicting label', release='harvest')
    issues = []
    _, report = combine([a, b, c], reg, issues=issues)
    assert report['leakage'].startswith('FAIL')
    assert report['train_eval_removed_rows'] == 2
    assert any(i['message'] == 'cross-split provider' for i in issues)
    assert any(i['message'] == 'conflicting duplicate line' for i in issues)
    assert len(issues) >= 2


def reseal(config):
    cfg = read(config)
    root = Path(cfg['harvest_root'])
    transfer = read(root / 'TRANSFER.json')
    for name in list(transfer['files']):
        transfer['files'][name] = dict(sha256=sha(root / name))
    atomic(root / 'TRANSFER.json', transfer)
    cfg['harvest_transfer'] = spec(root / 'TRANSFER.json')
    atomic(config, cfg)


def test_collision_cpu_job_leaves_diagnostics_and_no_train_manifest(tmp_path):
    from audit_job import execute
    config, _ = tiny_inputs(tmp_path)
    cfg = read(config)
    subset = list(rows(cfg['s1_subset']['path']))[0]
    release = Path(cfg['harvest_root'])
    data = list(rows(release / 'metadata.jsonl'))
    train = next(r for r in data if r['split'] == 'train')
    # Same pixels but another canonical book: forbidden duplicate, never silently kept.
    dest = release / train['file_name']
    dest.write_bytes(Path(subset['crop_path']).read_bytes())
    train['crop_sha256'] = sha(dest)
    (release / 'metadata.jsonl').write_text(''.join(__import__('json').dumps(r) + '\n' for r in data))
    for split in ('train', 'dev', 'test'):
        file = release / 'data' / split / 'metadata.jsonl'
        file.write_text(''.join(__import__('json').dumps(dict(r,
            file_name=str(Path(r['file_name']).relative_to(Path('data') / split)))) + '\n'
            for r in data if r['split'] == split))
    reseal(config)
    with pytest.raises(ValueError, match='union audit BLOCKED'):
        execute(config, tmp_path / 'audit', fixture=True)
    report = read(tmp_path / 'audit/manifest/AUDIT.json')
    assert report['status'] == 'BLOCKED' and report['collisions'] > 0
    assert report['horizons'] == []
    assert list((tmp_path / 'audit').glob('AUDIT_FAILED_*.json'))
    assert not (tmp_path / 'audit/manifest/train.jsonl').exists()
    assert not (tmp_path / 'audit/AUDIT_COMPLETE.json').exists()


def test_split_metadata_exact_view_checked_even_after_transfer_reseal(tmp_path):
    config, _ = tiny_inputs(tmp_path)
    cfg = read(config)
    split = Path(cfg['harvest_root']) / 'data/train/metadata.jsonl'
    data = list(rows(split))
    data[0]['text'] = 'changed only in split view'
    split.write_text(__import__('json').dumps(data[0]) + '\n')
    reseal(config)
    with pytest.raises(ValueError, match='split-level metadata differs'):
        build(config, tmp_path / 'manifest', fixture=True)


def test_single_harvest_switch_and_horizon_binding(tmp_path):
    from bind_config import bind
    roots = []
    for name in ('harvest_20261025_v1', 'release_with_gennadius_cached_v4'):
        root = tmp_path / name
        root.mkdir()
        atomic(root / 'RELEASE_RECEIPT.json', dict(variant=name))
        atomic(root / 'TRANSFER.json', dict(variant=name))
        roots.append(root)
    for i, root in enumerate(roots):
        result = bind(PKG / 'data.template.json', root, tmp_path / f'bound-{i}.json')
        assert result['harvest_root'] == str(root)
        assert result['horizon_recipe'] == 'full'
        assert bound(result['harvest_receipt']) == root / 'RELEASE_RECEIPT.json'
    result = bind(PKG / 'data.template.json', roots[1], tmp_path / 'literal.json', horizon='s1-literal')
    assert result['horizon_recipe'] == 's1-literal'

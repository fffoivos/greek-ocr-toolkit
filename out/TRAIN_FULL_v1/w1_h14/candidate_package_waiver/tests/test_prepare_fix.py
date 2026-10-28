"""3748213 regression: preserve admitted digit/punctuation rows and report-only audits."""
import hashlib
from pathlib import Path
import sys

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
from common import atomic, read, rows, sha, spec, write_rows
from prepare import factory_coverage, harvest_record, nonletter_label, prepare
from audit_job import execute
from test_rehearsal import tiny_inputs


@pytest.mark.parametrize('text', ['139', '1.234,50', '— · /', '123 456', ';'])
def test_frozen_s1_nonletter_fallback(text):
    r = dict(wave='W5-1', id='n', text=text, edition_id='e', crop_path='/c', source='s', split='dev')
    record = harvest_record(r)
    assert nonletter_label(text) and record.pop('script_class') == 'furniture'
    assert record == dict(id='harvest:W5-1:n', text=text, doc='e', crop_path='/c',
                         source_dataset='s', split='reserved', admitted=True)


@pytest.mark.parametrize('text', ['139α', '139A', '139Н', 'ἅ', 'Α / A', 'ѣ', '÷'])
def test_script_bearing_import_is_unchanged(text):
    r = dict(wave='W3', id='n', text=text, edition_id='e', crop_path='/c', source='s', split='train')
    assert not nonletter_label(text)
    assert 'script_class' not in harvest_record(r)


def test_report_only_length_flag_never_changes_admission(tmp_path):
    feed = tmp_path / 'import.jsonl'
    feed.write_text('{}\n')
    info = dict(records_sha256=sha(feed), drop_ledger=[], audit_ok=False)
    factory_coverage(info, feed)
    for changed in (dict(info, drop_ledger=[dict(reason='unmapped_script_class')]),
                    dict(info, records_sha256='0' * 64)):
        with pytest.raises(ValueError, match='dropped/changed'):
            factory_coverage(changed, feed)


def parent_audit(config, root):
    """Fixture receipt with the actual parent seal; audit code is byte-exact."""
    from reuse_audit import PARENT_SHA
    execute(config, root, fixture=True)
    parent = spec(PKG / 'audit_parent_payload.json')
    assert parent['sha256'] == PARENT_SHA
    a = read(root / 'manifest/AUDIT.json')
    a['package'] = parent
    atomic(root / 'manifest/AUDIT.json', a)
    m = read(root / 'manifest/MANIFEST.json')
    m.update(package_sha256=PARENT_SHA, audit=spec(root / 'manifest/AUDIT.json'))
    atomic(root / 'manifest/MANIFEST.json', m)
    c = read(root / 'AUDIT_COMPLETE.json')
    c.update(package=parent, audit=m['audit'], manifest=spec(root / 'manifest/MANIFEST.json'))
    atomic(root / 'AUDIT_COMPLETE.json', c)


def test_audit_reuse_and_digit_import_all_splits_e2e(tmp_path):
    from reuse_audit import reuse
    from train.cer import load_codec
    from test_package import spawn
    config, fake_factory = tiny_inputs(tmp_path)
    cfg = read(config)
    codec = load_codec(str(PKG / 'vendor/codec/v2.1.json'))
    ids = {a['ch']: a['id'] for a in codec.atoms}
    # A digit-only v4 row is already furniture: preserve its entire stored row.
    shared = read(cfg['s1_shared_mix']['path'])
    c = shared['components'][0]
    shard = Path(c['shard_dir']) / 'train/shard-00000.parquet'
    old = pq.read_table(shard).to_pylist()[0]
    old.update(label_ids=[ids[x] for x in '139'], script_class='furniture')
    pq.write_table(pa.Table.from_pylist([old]), shard)
    c['shard_sha256']['train/shard-00000.parquet'] = sha(shard)
    atomic(cfg['s1_shared_mix']['path'], shared)
    cfg['s1_shared_mix'] = spec(cfg['s1_shared_mix']['path'])
    info = read(cfg['s1_build_info']['path'])
    info['shard_sha256'] = c['shard_sha256']
    atomic(cfg['s1_build_info']['path'], info)
    cfg['s1_build_info'] = spec(cfg['s1_build_info']['path'])
    subset = list(rows(cfg['s1_subset']['path']))
    subset[0]['label'] = '139'
    # write_rows is exclusive; use a new bound fixture instead of replacing input.
    subset_path = tmp_path / 'numeric-subset.jsonl'
    write_rows(subset_path, subset)
    cfg['s1_subset'] = dict(spec(subset_path), rows=1)
    release = Path(cfg['harvest_root'])
    labels = dict(train='139', dev='1.234,50', test='— · /')
    for metadata in [release / 'metadata.jsonl', *release.glob('data/*/metadata.jsonl')]:
        data = list(rows(metadata))
        for r in data:
            r.update(text=labels[r['split']], primary_class='numerics_tables',
                     label_sha256=hashlib.sha256(labels[r['split']].encode()).hexdigest())
        metadata.write_text(''.join(__import__('json').dumps(r, ensure_ascii=False) + '\n' for r in data))
    transfer = read(release / 'TRANSFER.json')
    for name in transfer['files']:
        transfer['files'][name] = dict(sha256=sha(release / name))
    atomic(release / 'TRANSFER.json', transfer)
    cfg['harvest_transfer'] = spec(release / 'TRANSFER.json')
    atomic(config, cfg)
    prior = tmp_path / 'prior'
    parent_audit(config, prior)
    prior_hash = sha(prior / 'AUDIT_COMPLETE.json')
    prepared_root = tmp_path / 'fresh'
    reused = reuse(config, prior, prepared_root, fixture=True)
    assert sha(prior / 'AUDIT_COMPLETE.json') == prior_hash
    assert reused['files']['rows.jsonl']['path'].startswith(str(prior))
    assert not (prepared_root / 'manifest/rows.jsonl').exists()  # no large copy

    def numeric_factory(argv, **kwargs):
        feed = list(rows(argv[argv.index('--records') + 1]))
        assert len(feed) == 3 and all(r['script_class'] == 'furniture' for r in feed)
        fake_factory(argv, **kwargs)
        factory = Path(argv[argv.index('--out') + 1])
        by_id = {r['id']: r for r in feed}
        info = read(factory / 'build_info.json')
        for path in factory.rglob('shard-*.parquet'):
            data = pq.read_table(path).to_pylist()
            for r in data:
                r.update(label_ids=[ids[x] for x in by_id[r['line_id']]['text']], script_class='furniture')
            pq.write_table(pa.Table.from_pylist(data), path)
            info['shard_sha256'][str(path.relative_to(factory))] = sha(path)
        info['audit_ok'] = False  # actual report-only length diagnostic shape
        atomic(factory / 'build_info.json', info)
    rt = prepare(config, prepared_root / 'manifest', prepared_root / 'prepared',
                 factory_runner=numeric_factory, fixture=True)
    train = [r for f in rt['pools']['non_parliament']['files'] for r in pq.read_table(f['path']).to_pylist()]
    assert next(r for r in train if r['line_id'] == 'old') == old
    assert {codec.decode(r['label_ids']) for r in train} == {'139'}
    for split in ('dev', 'test'):
        panel = pq.read_table(rt['pools']['harvest_' + split]['files'][0]['path']).to_pylist()
        assert len(panel) == 1 and panel[0]['script_class'] == 'furniture'
        assert codec.decode(panel[0]['label_ids']) == labels[split]
    assert rt['import_diagnostics']['s1_nonletter_classes'] == {'furniture': 1}
    assert rt['import_diagnostics']['harvest_nonletter_by_split'] == dict(train=1, dev=1, test=1)
    assert rt['train_rows'] == 2 and rt['import_diagnostics']['audit_ok'] is False
    run = tmp_path / 'run'
    proc = spawn(prepared_root / 'prepared/runtime.json', run)
    assert proc.wait(timeout=40) == 0, (run / 'process.log').read_text()
    assert read(run / 'COMPLETE.json')['binding']['evaluation_steps'] == [2, 4, 6, 8]


@pytest.mark.parametrize('failure', ['config', 'rows', 'input', 'mode', 'package', 'audit_code'])
def test_reuse_refuses_changed_identity(tmp_path, monkeypatch, failure):
    import reuse_audit
    config, _ = tiny_inputs(tmp_path)
    prior = tmp_path / 'prior'
    parent_audit(config, prior)
    fixture = True
    if failure == 'config':
        cfg = read(config)
        cfg['horizon_recipe'] = 's1-literal'
        atomic(config, cfg)
    elif failure == 'rows':
        (prior / 'manifest/rows.jsonl').write_text('changed')
    elif failure == 'input':
        Path(read(config)['s1_records']['path']).write_text('changed')
    elif failure == 'mode':
        fixture = False
    elif failure == 'package':
        c = read(prior / 'AUDIT_COMPLETE.json')
        c['package']['sha256'] = '0' * 64
        atomic(prior / 'AUDIT_COMPLETE.json', c)
    else:
        import verify
        payload = read(PKG / 'PAYLOAD.json')
        payload['files']['manifest.py'] = dict(bytes=1, sha256='changed')
        monkeypatch.setattr(verify, 'verify', lambda: payload)
    with pytest.raises(ValueError):
        reuse_audit.reuse(config, prior, tmp_path / 'new', fixture=fixture)
    assert not (tmp_path / 'new').exists()

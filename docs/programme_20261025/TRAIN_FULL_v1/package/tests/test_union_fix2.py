"""3747871 regression: v4 typed identities and witnessed eval-wins crop policy."""
from pathlib import Path
import sys

import pytest

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
from common import rows, read
from manifest import Registry, combine, build
from test_package import book, row
from test_rehearsal import tiny_inputs


def test_reported_parliament_identity_uses_actual_authority():
    registry = Registry(list(rows(PKG / 'registry_v2.jsonl.gz')))
    r = row('55062aa4-p000043-l0130', bid=None, ed='parliament:55062aa4')
    r['source'] = 'parliament_proceedings_1975_2000'
    assert registry.resolve(r) == 'book-f99bc90d5d1377b723437a2f'
    # Prefix is independently a recorded identity, never a guessed hash.
    r['edition_id'] = 'unknown'
    assert registry.resolve(r) == 'book-f99bc90d5d1377b723437a2f'


@pytest.mark.parametrize('namespace', ['v2_book_id', 'pdf_sha256'])
def test_restored_namespaces_require_global_uniqueness(namespace):
    a, b = book(), book('book-b', edition='ed-b')
    for r in (a, b):
        r['aliases'].append(dict(namespace=namespace, value='same'))
    with pytest.raises(ValueError, match='ambiguous registry identity aliases'):
        Registry([a], [b])


def test_all_bundled_v2_and_hash_aliases_resolve_with_registry_split():
    authority = list(rows(PKG / 'registry_v2.jsonl.gz'))
    registry = Registry(authority)
    counts = {}
    for record in authority:
        if record['split'].removeprefix('seal04_') not in ('train', 'dev', 'test'):
            continue
        for alias in record['aliases']:
            if alias['namespace'] not in ('v2_book_id', 'pdf_sha256', 'seal04_edition_hash'):
                continue
            r = row('opaque-id', bid=None, ed=alias['value'], split=record['split'].removeprefix('seal04_'))
            assert registry.resolve(r) == record['book_id']
            counts[alias['namespace']] = counts.get(alias['namespace'], 0) + 1
    assert counts == dict(v2_book_id=746, pdf_sha256=341, seal04_edition_hash=1359)


def test_new_harvest_protection_separate_from_bound_s1_membership():
    b = book()
    b['harvest_protection'] = True
    registry = Registry([b])
    assert registry.resolve(row()) == b['book_id']
    with pytest.raises(ValueError, match='protected train book'):
        registry.resolve(dict(row(), release='harvest'))
    with pytest.raises(ValueError, match='registry split/conflict'):
        registry.resolve(dict(row(), split='dev'))


@pytest.mark.parametrize('reverse', [False, True])
def test_exact_reported_serbia_and_uoi_shapes_eval_wins(reverse):
    books = [book('v4'), book('harvest-train', edition='h-train'),
             book('harvest-dev', 'dev', 'h-dev'), book('seal-test', 'seal04_test', 's-test'),
             book('uoi', 'test', 'uoi')]
    registry = Registry(books)
    def r(ident, crop, split, bid, ed, release, text, source):
        return dict(row(ident, crop * 64, split, bid, ed), release=release, text=text, source=source)
    records = []
    for i, text in enumerate(['НБС', 'Дигитални објекат на адреси:', 'НБС', 'власништво је Народне библиотеке Србије.']):
        crop = str(i)
        if i == 0:
            a = r('v4-0', crop, 'train', 'v4', 'ed-a', 'v4', text, 'serbia')
            b = r('harvest-dev-0', crop, 'dev', 'harvest-dev', 'h-dev', 'harvest', text, 'serbia')
        elif i == 1:
            a = r('harvest-dev-1', crop, 'dev', 'harvest-dev', 'h-dev', 'harvest', text, 'serbia')
            b = r('seal-test-1', crop, 'test', 'seal-test', 's-test', 'seal04', text, 'serbia')
        else:
            a = r('harvest-train-' + str(i), crop, 'train', 'harvest-train', 'h-train', 'harvest', text, 'serbia')
            b = r('seal-test-' + str(i), crop, 'test', 'seal-test', 's-test', 'seal04', text, 'serbia')
        records.extend([a, b])
    records.extend(r('uoi-' + str(i), 'f', 'test', 'uoi', 'uoi', 'harvest', 'συγχώρησις μᾶς', 'oa_uoi') for i in range(2))
    if reverse:
        records.reverse()
    issues = []
    kept, report = combine(records, registry, issues=issues)
    assert issues == []
    assert len(kept) == 7 and report['train_unique'] == 0
    assert report['train_eval_removed_rows'] == 3
    assert report['eval_crop_repeat_rows'] == 2
    assert report['duplicate_train_rows'] == 0
    assert sum(r['split'] != 'train' for r in records) == len(kept)
    for removal in report['train_eval_removals']:
        assert removal['row']['crop_sha256'] == removal['eval_witness']['crop_sha256']
        assert removal['row']['split'] == 'train' and removal['eval_witness']['split'] in ('dev', 'test')


def test_eval_wins_does_not_hide_book_leakage_or_train_label_conflicts():
    reg = Registry([book(), book('b', 'dev', 'ed-b')])
    with pytest.raises(ValueError, match='registry split/conflict'):
        combine([row(), dict(row(), split='dev')], reg)
    with pytest.raises(ValueError, match='conflicting duplicate'):
        combine([row(), dict(row(), text='different', id='other')], reg)
    # Eval labels stay literal; crop-based exclusion doesn't depend on text equality.
    kept, report = combine([row(), dict(row('ev', 'a'*64, 'dev', 'b', 'ed-b'), text='other')], reg)
    assert len(kept) == 1 and report['train_eval_removals'][0]['labels_equal'] is False


def test_audit_proves_all_s1_assignments_before_dedupe_and_seals_witness_files(tmp_path):
    config, _ = tiny_inputs(tmp_path)
    report = build(config, tmp_path / 'manifest', fixture=True, audit=True)
    assert report['s1_resolution'] == dict(input_rows=1, resolved_split_matches_s1=1, unresolved_or_split_mismatch=0)
    assert read(tmp_path / 'manifest/AUDIT.json')['s1_resolution'] == report['s1_resolution']
    assert set(report['files']) >= {'train_eval_removals.jsonl', 'eval_crop_repeats.jsonl'}

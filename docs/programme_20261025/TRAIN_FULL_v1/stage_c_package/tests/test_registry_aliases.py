"""Regression for audit 3747846: real collection URLs are provenance, not identity."""
from collections import defaultdict
from pathlib import Path
import sys

import pytest

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
from common import atomic, read, rows, spec
from manifest import Registry, build
from test_package import book, row
from test_rehearsal import tiny_inputs


def actual_shared_catalogue_aliases():
    aliases = defaultdict(set)
    for record in rows(PKG / 'registry_v2.jsonl.gz'):
        for alias in record.get('aliases', []):
            aliases[(alias['namespace'], str(alias.get('value', alias.get('id'))))].add(record['book_id'])
    return {key: bids for key, bids in aliases.items() if len(bids) > 1}


SHARED = actual_shared_catalogue_aliases()


def test_bundled_authority_has_exact_eight_reported_metadata_shapes():
    assert len(SHARED) == 8
    assert {ns for ns, _ in SHARED} == {'catalogue_reference'}
    lekythos = {value.rsplit('/', 1)[-1]: len(bids) for (_, value), bids in SHARED.items()
               if 'lekythos.library.ucy.ac.cy' in value}
    assert lekythos == {'14019': 4, '14041': 17, '14212': 3, '14249': 6, '14147': 2, '14172': 4}
    gennadius = {value: len(bids) for (_, value), bids in SHARED.items() if '/akolouthies/List2.php?' in value}
    assert len(gennadius) == 2 and set(gennadius.values()) == {2}
    registry = Registry(list(rows(PKG / 'registry_v2.jsonl.gz')))
    recorded = {(r['namespace'], r['value']): set(r['book_ids'])
                for r in registry.alias_report()['shared_metadata_aliases']}
    assert recorded == SHARED
    assert not any(ns == 'catalogue_reference' for ns, _ in registry.aliases)


@pytest.mark.parametrize('key', sorted(SHARED), ids=lambda key: key[1])
def test_real_shared_metadata_never_resolves_or_merges_books(key):
    namespace, value = key
    books = []
    for bid in sorted(SHARED[key]):
        record = book(bid, edition='edition-' + bid)
        record['aliases'].append(dict(namespace=namespace, value=value))
        books.append(record)
    registry = Registry(books)
    assert registry.metadata_aliases[key] == SHARED[key]
    for record in books:
        assert registry.resolve(row(bid=record['book_id'], ed='edition-' + record['book_id'])) == record['book_id']
    with pytest.raises(ValueError, match='unknown/contradictory book aliases'):
        registry.resolve(dict(row(bid=None, ed=value), catalogue_reference=value))


@pytest.mark.parametrize('namespace', ['book_id', 'edition_id', 'seal04_edition_hash',
                                        'provider_item:lekythos', 'line_id_prefix', 'v2_book_id', 'pdf_sha256'])
def test_every_identity_namespace_still_refuses_ambiguity(namespace):
    a, b = book(), book('book-b', edition='ed-b')
    value = a['book_id'] if namespace == 'book_id' else 'shared-identity'
    for record in (a, b):
        record['aliases'].append(dict(namespace=namespace, value=value))
    with pytest.raises(ValueError, match='ambiguous registry identity aliases'):
        Registry([a, b])
    with pytest.raises(ValueError, match='ambiguous registry identity aliases'):
        Registry([a], [b])


def test_audit_and_manifest_record_shared_metadata_without_collision(tmp_path):
    config, _ = tiny_inputs(tmp_path)
    cfg = read(config)
    authority = list(rows(cfg['registry_v2']['path']))
    for record in authority[:2]:
        record['aliases'].append(dict(namespace='catalogue_reference', value='https://collection.example/search'))
    from common import write_rows
    path = tmp_path / 'authority-with-metadata.jsonl'
    write_rows(path, authority)
    cfg['registry_v2'] = spec(path)
    atomic(config, cfg)
    report = build(config, tmp_path / 'manifest', fixture=True, audit=True)
    audit = read(tmp_path / 'manifest/AUDIT.json')
    assert audit['status'] == 'PASS' and audit['collisions'] == 0
    assert audit['registry_aliases'] == report['registry_aliases']
    assert audit['registry_aliases']['shared_metadata_aliases'] == [dict(
        namespace='catalogue_reference', value='https://collection.example/search',
        book_ids=sorted(r['book_id'] for r in authority[:2]))]

"""Requested T6g filter, reproducibility, isolation and byte-custody checks."""
import ast
import importlib.util
import json
from pathlib import Path
import random
import unicodedata

import pytest

SPEC = importlib.util.spec_from_file_location('t6g_pack', Path(__file__).with_name('pack.py'))
pack = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pack)


@pytest.fixture(scope='module')
def live():
    pool, counts = pack.load_pool()
    cards = pack.rows(pack.READER / 'cards.jsonl')
    key = json.loads(pack.KEY.read_text())
    return pool, counts, cards, key


def test_pool_filter_all_requested_boundaries():
    records = [dict(id=str(i), source='kosmopolis', output_kind='masked', screen_merged=False)
               for i in range(8)]
    joined = {r['id']: dict(r, primary_class='poly1850') for r in records}
    records[1]['output_kind'] = 'unmatched_original'
    records[2]['screen_merged'] = True
    joined['3']['screen_merged'] = True
    joined['4']['primary_class'] = 'poly1900'
    records[7]['output_kind'] = 'guarded_original'
    pool, counts = pack.filter_pool(records[::-1], joined, {'5'}, {'6'})
    assert [r['id'] for r in pool] == ['0', '7']
    assert counts == dict(records=8, other_output_kind=1, screen_merged=2,
                         other_primary_class=1, rotated_crop=1, previous_t6b_card=1, pool=2)


def test_pool_rejects_missing_join():
    with pytest.raises(ValueError, match='missing W1 join'):
        pack.filter_pool([dict(id='a')], {}, set(), set())


def test_pool_rejects_duplicate_ids():
    with pytest.raises(ValueError, match='duplicate row id'):
        pack.unique_by_id([dict(id='a'), dict(id='a')])


def test_live_pool_independently_filtered(live):
    pool, counts, _, key = live
    records = pack.rows(pack.RECORDS)
    ids = {r['id'] for r in records}
    with pack.W1.open() as stream:
        joined = {r['id']: r for line in stream if (r := json.loads(line))['id'] in ids}
    old = json.loads(pack.OLD_KEY.read_text())
    previous = {r['line_id'] for r in old.values() if isinstance(r, dict)}
    rotated = set(pack.ROTATED.read_text().splitlines())
    expected = sorted(r['id'] for r in records
                      if joined[r['id']]['primary_class'] == 'poly1850'
                      and r['output_kind'] in ('masked', 'guarded_original')
                      and not r['screen_merged'] and not joined[r['id']]['screen_merged']
                      and r['id'] not in rotated and r['id'] not in previous)
    assert [r['id'] for r in pool] == expected == key['_pool_line_ids']
    assert len(expected) == counts['pool'] == key['_pool']
    assert counts['records'] == counts['joined']


def test_seed_reproducibility_and_no_length_sort(live):
    pool, _, cards, key = live
    expected = random.Random('t6g:kosmopolis:poly1850').sample(
        sorted(pool, key=lambda r: r['id']), min(100, len(pool)))
    observed = [key[c['card_id']]['line_id'] for c in cards]
    assert observed == [r['id'] for r in expected]
    assert pack.draw(pool[::-1]) == pack.draw(pool) == expected
    assert len(observed) == len(set(observed)) == 100
    lengths = [len(c['google_text']) for c in cards]
    assert lengths != sorted(lengths) and lengths != sorted(lengths, reverse=True)


@pytest.mark.parametrize('size', [0, 3, 99])
def test_short_pool_takes_all(size):
    pool = [dict(id=f'r{i:03d}') for i in range(size)]
    drawn = pack.draw(pool)
    assert len(drawn) == size
    assert {r['id'] for r in drawn} == {r['id'] for r in pool}


def test_live_crop_shas_copies_protocol_and_isolation(live):
    result = pack.verify()
    assert result['cards'] == 100 and result['isolation']['ok']
    _, _, cards, key = live
    records = {r['id']: r for r in pack.rows(pack.RECORDS)}
    for card in cards:
        record = records[key[card['card_id']]['line_id']]
        assert pack.sha(pack.READER / card['crop']) == record['masked_crop_sha256']
    assert (pack.READER / 'PROTOCOL.md').read_bytes() == pack.PROTOCOL.read_bytes()
    assert pack.KEY.parent == pack.READER.parent.parent


@pytest.mark.parametrize('leak', ['parent-key', 'reader-key', 'crop-key', 'private-card-field', 'symlink'])
def test_isolation_rejects_leaks(tmp_path, leak):
    reader = tmp_path / 'pack/reader'
    (reader / 'crops').mkdir(parents=True)
    card = dict(card_id='c001', crop='crops/c001.png', google_text='α', word_scripts=[['α', 'Greek']])
    (reader / 'crops/c001.png').write_bytes(b'copied-crop')
    (reader / 'PROTOCOL.md').write_text('frozen protocol')
    (reader / 'cards.jsonl').write_text(json.dumps(card) + '\n')
    key = tmp_path / 'key.json'
    assert pack.isolation_check(reader, key)['ok']
    if leak == 'parent-key':
        (reader.parent / 'answer_key.json').write_text('{}')
    elif leak == 'reader-key':
        (reader / 'anonymous.json').write_text('{"line_id":"secret"}')
    elif leak == 'crop-key':
        (reader / 'crops/.key').write_text('{}')
    elif leak == 'private-card-field':
        card['line_id'] = 'secret'
        (reader / 'cards.jsonl').write_text(json.dumps(card) + '\n')
    else:
        (reader / 'crops/c001.png').unlink()
        (reader / 'crops/c001.png').symlink_to(key)
    with pytest.raises(ValueError):
        pack.isolation_check(reader, key)


def test_record_crop_sha_and_guarded_original(tmp_path, monkeypatch):
    monkeypatch.setattr(pack, 'BASE', tmp_path)
    crop = tmp_path / 'kosmopolis/crops/guard.png'
    crop.parent.mkdir(parents=True)
    crop.write_bytes(b'byte-exact-existing-original')
    record = dict(id='guard', masked_crop='kosmopolis/crops/guard.png',
                  output_kind='guarded_original', masked_crop_sha256=pack.sha(crop),
                  original_crop_sha256=pack.sha(crop))
    assert pack.checked_crop(record) == crop
    record['original_crop_sha256'] = '0' * 64
    with pytest.raises(ValueError, match='differs from original'):
        pack.checked_crop(record)
    record['original_crop_sha256'] = record['masked_crop_sha256']
    crop.write_bytes(b'changed-after-record')
    with pytest.raises(ValueError, match='record crop sha mismatch'):
        pack.checked_crop(record)


def test_word_scripts_match_t6b_without_importing_masker(live):
    tree = ast.parse((pack.BASE / 'run.py').read_text())
    func = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'word_scripts')
    namespace = dict(unicodedata=unicodedata)
    exec(compile(ast.Module(body=[func], type_ignores=[]), 't6b-word-scripts-only', 'exec'), namespace)
    for card in live[2]:
        assert card['word_scripts'] == namespace['word_scripts'](card['google_text'])

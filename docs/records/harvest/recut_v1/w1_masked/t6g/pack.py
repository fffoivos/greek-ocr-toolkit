"""T6g local draw/pack only. No masking, admission, or network dependencies."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import time
import unicodedata

BASE = Path(__file__).resolve().parent.parent
READER = BASE / 'cards_kosmo_poly1850/reader'
KEY = BASE / 'cards_kosmo_poly1850_key.json'
RECORDS = BASE / 'kosmopolis/records.jsonl'
W1 = Path.home() / 'Projects/collect-v3-data/run/W1/crop_tight_page.jsonl'
ROTATED = Path.home() / 'Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions/w1_rotated_crop_ids.txt'
OLD_KEY = BASE / 'cards/kosmopolis_key.json'
PROTOCOL = BASE / 'cards/LABEL_CHECK_v2.md'
SEED = 't6g:kosmopolis:poly1850'
CARD_FIELDS = {'card_id', 'crop', 'google_text', 'word_scripts'}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def rows(path):
    with Path(path).open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def unique_by_id(values):
    result = {}
    for row in values:
        rid = row['id']
        if rid in result:
            raise ValueError('duplicate row id: ' + rid)
        if row.get('row_id', rid) != rid:
            raise ValueError('conflicting row id: ' + rid)
        result[rid] = row
    return result


def filter_pool(records, joined, rotated, previous):
    """Apply only the requested eligibility/exclusions; order by line id."""
    unique_by_id(records)
    counts = Counter(records=len(records))
    pool = []
    for record in records:
        rid = record['id']
        if rid not in joined:
            raise ValueError('missing W1 join: ' + rid)
        row = joined[rid]
        if record['source'] != 'kosmopolis' or row['source'] != 'kosmopolis':
            raise ValueError('unexpected source: ' + rid)
        if row['primary_class'] != 'poly1850':
            counts['other_primary_class'] += 1
        elif record['output_kind'] not in {'masked', 'guarded_original'}:
            counts['other_output_kind'] += 1
        elif record.get('screen_merged') or row.get('screen_merged'):
            counts['screen_merged'] += 1
        elif rid in rotated:
            counts['rotated_crop'] += 1
        elif rid in previous:
            counts['previous_t6b_card'] += 1
        else:
            pool.append(record)
    counts['pool'] = len(pool)
    for name in ('other_output_kind', 'screen_merged', 'rotated_crop', 'previous_t6b_card'):
        counts.setdefault(name, 0)
    return sorted(pool, key=lambda row: row['id']), dict(counts)


def load_pool():
    records = rows(RECORDS)
    ids = set(unique_by_id(records))
    joined = {}
    # Stream W1; do not retain unrelated rows or write to the run root.
    with W1.open() as stream:
        for line in stream:
            row = json.loads(line)
            if row['id'] in ids:
                if row['id'] in joined:
                    raise ValueError('duplicate W1 join: ' + row['id'])
                joined[row['id']] = row
    old = json.loads(OLD_KEY.read_text())
    previous = {v['line_id'] for v in old.values() if isinstance(v, dict) and 'line_id' in v}
    if len(previous) != 100:
        raise ValueError('expected 100 distinct previous T6b cards')
    rotated = {line.strip() for line in ROTATED.read_text().splitlines()
               if line.strip() and not line.lstrip().startswith('#')}
    pool, counts = filter_pool(records, joined, rotated, previous)
    counts['joined'] = len(joined)
    counts['previous_t6b_cards_total'] = len(previous)
    return pool, counts


def draw(pool):
    ordered = sorted(pool, key=lambda row: row['id'])
    return random.Random(SEED).sample(ordered, min(100, len(ordered)))


def word_scripts(text):
    # Same Unicode-name convention and whitespace tokenization as T6b.
    result = []
    for word in text.split():
        scripts = {next((s for s in ('Greek', 'Latin', 'Cyrillic')
                         if s.upper() in unicodedata.name(c, '')), 'Other')
                   for c in word if c.isalpha()}
        result.append([word, next(iter(scripts)) if len(scripts) == 1
                       else 'Mixed' if scripts else 'none'])
    return result


def input_bindings():
    return {name: dict(path=str(path), sha256=sha(path)) for name, path in (
        ('records', RECORDS), ('w1', W1), ('rotated_ids', ROTATED),
        ('previous_key', OLD_KEY), ('protocol', PROTOCOL))}


def checked_crop(record):
    """Read existing output bytes; guarded outputs must equal original bytes' hash."""
    path = BASE / record['masked_crop']
    if not path.resolve().is_relative_to((BASE / 'kosmopolis/crops').resolve()):
        raise ValueError('crop escapes existing output directory')
    if path.is_symlink() or sha(path) != record['masked_crop_sha256']:
        raise ValueError('record crop sha mismatch: ' + record['id'])
    if record['output_kind'] == 'guarded_original':
        if record['masked_crop_sha256'] != record['original_crop_sha256']:
            raise ValueError('guarded crop differs from original sha')
    return path


def isolation_check(reader=READER, key_path=KEY):
    """An exact public-tree allowlist rejects keys, metadata and symlink escapes."""
    parent = reader.parent
    if reader.is_symlink() or parent.is_symlink():
        raise ValueError('reader directory symlink')
    if key_path.parent.resolve() != parent.parent.resolve():
        raise ValueError('key must be two levels above reader')
    if {p.name for p in parent.iterdir()} != {'reader'}:
        raise ValueError('unexpected/key-like entry in reader parent')
    if {p.name for p in reader.iterdir()} != {'cards.jsonl', 'PROTOCOL.md', 'crops'}:
        raise ValueError('unexpected/key-like entry in reader')
    if any(p.is_symlink() for p in parent.rglob('*')):
        raise ValueError('symlink in public tree')
    cards = rows(reader / 'cards.jsonl')
    expected_crops = set()
    for i, card in enumerate(cards, 1):
        cid = f'c{i:03d}'
        if set(card) != CARD_FIELDS or card['card_id'] != cid or card['crop'] != f'crops/{cid}.png':
            raise ValueError('non-v2/private fields or nonanonymous crop path')
        expected_crops.add(cid + '.png')
    actual = {p.name for p in (reader / 'crops').iterdir()}
    if actual != expected_crops or not all(p.is_file() for p in (reader / 'crops').iterdir()):
        raise ValueError('unexpected/key-like entry in crops')
    return dict(ok=True, reader_contexts=1, cards=len(cards),
                parent_entries=['reader'], key_levels_above_reader=2)


def build():
    started = time.monotonic()
    nice = os.getpriority(os.PRIO_PROCESS, 0)
    if nice <= 0:
        raise ValueError('positive inherited nice priority required')
    if READER.parent.exists() or KEY.exists():
        raise ValueError('refusing to overwrite an existing card pack/key')
    before = input_bindings()
    pool, counts = load_pool()
    picked = draw(pool)
    # Verify every chosen source before creating the public pack.
    sources = [checked_crop(record) for record in picked]
    (READER / 'crops').mkdir(parents=True)
    shutil.copyfile(PROTOCOL, READER / 'PROTOCOL.md')
    key = dict(_seed=SEED, _pool=len(pool), _counts=counts,
               _draw='uniform without replacement over line-id ordered pool; no length sorting',
               _short_pool=len(pool) < 100, _admitted=False,
               _pool_line_ids=[r['id'] for r in pool], _inputs=before)
    cards = []
    for i, (record, source) in enumerate(zip(picked, sources), 1):
        cid = f'c{i:03d}'
        dest = READER / 'crops' / (cid + '.png')
        shutil.copyfile(source, dest)
        if sha(dest) != record['masked_crop_sha256'] or os.path.samefile(source, dest):
            raise ValueError('copy custody failed: ' + cid)
        cards.append(dict(card_id=cid, crop=f'crops/{cid}.png',
                          google_text=record['google_text'], word_scripts=word_scripts(record['google_text'])))
        key[cid] = {name: record[name] for name in (
            'page_id', 'original_crop_sha256', 'masked_crop_sha256', 'wrong_line_risk',
            'output_kind', 'mask_applied', 'changed', 'params_sha256')}
        key[cid].update(line_id=record['id'], primary_class='poly1850',
                        card_crop_sha256=sha(dest), screen_merged=False, rotated_crop=False)
    (READER / 'cards.jsonl').write_text(''.join(
        json.dumps(card, ensure_ascii=False, separators=(',', ':')) + '\n' for card in cards))
    write_json(KEY, key)
    if input_bindings() != before:
        raise ValueError('source inputs changed during packing')
    verified = verify()
    elapsed = time.monotonic() - started
    if elapsed > 30 * 60:
        raise ValueError('30 minute limit exceeded')
    receipt = dict(task='T6g', counts=counts, cards=len(cards), short_pool=len(pool) < 100,
                   output_kinds=dict(Counter(r['output_kind'] for r in picked)),
                   reader=str(READER), key=str(KEY), key_sha256=sha(KEY),
                   cards_sha256=sha(READER / 'cards.jsonl'), protocol_sha256=sha(PROTOCOL),
                   isolation=verified['isolation'], inherited_nice=nice,
                   priority_note='nice/taskpolicy changes denied by sandbox; inherited positive nice retained',
                   network='OFF; local standard-library file operations only',
                   masking_rerun=False, admitted=False, elapsed_seconds=round(elapsed, 3))
    write_json(Path(__file__).parent / 'receipt.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False))


def verify():
    pool, counts = load_pool()
    picked = draw(pool)
    cards = rows(READER / 'cards.jsonl')
    key = json.loads(KEY.read_text())
    if key['_inputs'] != input_bindings() or key['_counts'] != counts:
        raise ValueError('input or pool binding changed')
    if key['_seed'] != SEED or key['_pool'] != len(pool) or key['_admitted'] is not False:
        raise ValueError('draw metadata mismatch')
    if key['_pool_line_ids'] != [r['id'] for r in pool] or key['_short_pool'] != (len(pool) < 100):
        raise ValueError('pool identity mismatch')
    if len(cards) != len(picked):
        raise ValueError('wrong card count')
    if {k for k in key if not k.startswith('_')} != {f'c{i:03d}' for i in range(1, len(cards) + 1)}:
        raise ValueError('unexpected key entries')
    for i, (card, record) in enumerate(zip(cards, picked), 1):
        cid = f'c{i:03d}'
        expected = dict(card_id=cid, crop=f'crops/{cid}.png', google_text=record['google_text'],
                        word_scripts=word_scripts(record['google_text']))
        if card != expected or key[cid]['line_id'] != record['id']:
            raise ValueError('draw/card mismatch: ' + cid)
        source = checked_crop(record)
        dest = READER / card['crop']
        actual = sha(dest)
        if actual != record['masked_crop_sha256'] or actual != key[cid]['card_crop_sha256']:
            raise ValueError('card crop sha mismatch: ' + cid)
        if any(key[cid][name] != record[name] for name in (
            'page_id', 'original_crop_sha256', 'masked_crop_sha256', 'wrong_line_risk',
            'output_kind', 'mask_applied', 'changed', 'params_sha256')):
            raise ValueError('record/key mismatch: ' + cid)
        if (key[cid]['primary_class'], key[cid]['screen_merged'], key[cid]['rotated_crop']) != ('poly1850', False, False):
            raise ValueError('key eligibility mismatch: ' + cid)
        if dest.is_symlink() or os.path.samefile(source, dest) or dest.stat().st_nlink != 1:
            raise ValueError('crop must be an independent copy')
    if (READER / 'PROTOCOL.md').read_bytes() != PROTOCOL.read_bytes():
        raise ValueError('protocol differs from frozen v2')
    return dict(pool=len(pool), cards=len(cards), isolation=isolation_check())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify:
        print(json.dumps(verify()))
    else:
        build()

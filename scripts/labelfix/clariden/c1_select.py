"""Freeze the exact C1 train-only selection; reads metadata, never opens crops."""
import argparse
import ast
from collections import Counter
import json
from pathlib import Path
import random

from c1_common import compound_clusters, compound_counts, crop_key, read_jsonl, sha256, write_json


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--train', type=Path, required=True)
    ap.add_argument('--test', type=Path, required=True)
    ap.add_argument('--dev', type=Path, required=True)
    ap.add_argument('--validate-source', type=Path, default=Path('greekocr/labelfix/validate.py'))
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seed', type=int, default=20261016)
    ap.add_argument('--random-n', type=int, default=30000)
    a = ap.parse_args()
    # Read the declared book split without importing the evaluation instruments.
    tree = ast.parse(a.validate_source.read_text())
    dev_books = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == 'DEV_BOOKS' for t in n.targets))
    test = read_jsonl(a.test)
    dev = read_jsonl(a.dev)
    test_ids = {r['id'] for r in test}
    test_crops = {crop_key(r['crop']) for r in test}
    wiki_books = {r['doc'] for r in test + dev if r['doc'].startswith('wikisource:')}
    held_books = wiki_books - set(dev_books)
    selected, other = [], []
    counts, excluded, classes = Counter(), Counter(), Counter()
    seen_ids, seen_crops = set(), set()
    for ordinal, r in enumerate(read_jsonl(a.train)):
        counts['train_rows'] += 1
        if r['script_class'] != 'greek_poly':
            continue
        counts['greek_poly_rows'] += 1
        key = crop_key(r['crop'])
        reasons = []
        if r['split'] != 'train':
            reasons.append('not_train')
        if r['id'] in test_ids:
            reasons.append('v2_test_id')
        if key in test_crops:
            reasons.append('v2_test_crop')
        # Any non-dev Wikisource book is held out, even if absent from current instruments.
        if r['doc'].startswith('wikisource:') and r['doc'] not in dev_books:
            reasons.append('held_out_wikisource_book')
        if reasons:
            excluded.update(reasons)
            counts['excluded_rows'] += 1
            continue
        if r['id'] in seen_ids or key in seen_crops:
            raise ValueError(f'duplicate train identity: {r["id"]}, {key}')
        seen_ids.add(r['id'])
        seen_crops.add(key)
        compound = bool(compound_clusters(r['label']))
        record = dict(crop=key, id=r['id'], doc=r['doc'], label=r['label'], wave=r['wave'],
                      split='train', script_class='greek_poly', train_ordinal=ordinal,
                      selection_reason='compound' if compound else 'random_other')
        (selected if compound else other).append(record)
    counts['eligible_compound_rows'] = len(selected)
    counts['eligible_other_rows'] = len(other)
    counts['random_other_selected'] = a.random_n
    if len(other) < a.random_n:
        raise ValueError(f'only {len(other)} eligible noncompound rows')
    # Source order is fixed and hashed; CPython Random.sample with the requested seed.
    selected += random.Random(a.seed).sample(other, a.random_n)
    selected.sort(key=lambda r: r['train_ordinal'])
    counts['selected_rows'] = len(selected)
    for r in selected:
        assert r['id'] not in test_ids and r['crop'] not in test_crops
        assert not r['doc'].startswith('wikisource:') or r['doc'] in dev_books
        classes.update(compound_counts(r['label']))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open('x', encoding='utf-8') as f:
        for r in selected:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    summary = dict(seed=a.seed, algorithm='random.Random(seed).sample(source_order_other, 30000); output source order',
                   counts=counts, excluded_reasons=excluded, dev_wikisource_books=list(dev_books),
                   held_out_wikisource_books=sorted(held_books),
                   leakage_policy='v2 test IDs/crops excluded; every non-dev Wikisource book excluded; labels unchanged',
                   selected_by_wave=Counter(r['wave'] for r in selected),
                   selected_label_compound_clusters=classes,
                   inputs={str(p): sha256(p) for p in (a.train, a.test, a.dev, a.validate_source)},
                   selection_sha256=sha256(a.out))
    write_json(a.out.with_suffix('.summary.json'), summary)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()

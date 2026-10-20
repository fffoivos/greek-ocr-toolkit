"""Read back the collection v2 artifacts built by scripts/harvest/apply_clean.py (no rebuild, no network)."""
from collections import Counter, defaultdict
import json
from pathlib import Path

import pytest

from greekocr.harvest.collection import MANIFEST_FIELDS, SPLITS, normalize_label, read_jsonl

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "docs/records/harvest/collection"
V2 = V1 / "v2"

# A merged checkout may retain the validation receipt after the bulk corpus
# was archived. This suite is an optional readback of the complete build.
_REQUIRED = [V1/'admitted_all.jsonl', *[V2/name for name in (
    'validation_v2.json', 'admitted_all_v2.jsonl', 'dropped_v2.jsonl',
    'rejected_global_v2.jsonl', 'relabels_v2.jsonl', 'split_moves_v2.json',
)], *[V2/f'manifest_v2_{split}.json' for split in SPLITS],
    *[V2/f'import_real_v2_{split}.jsonl' for split in SPLITS]]
_MISSING = [str(path.relative_to(ROOT)) for path in _REQUIRED if not path.is_file()]
pytestmark = pytest.mark.skipif(bool(_MISSING), reason='collection v2 readback inputs unavailable: ' + ', '.join(_MISSING))


@pytest.fixture(scope="module")
def validation():
    return json.loads((V2 / "validation_v2.json").read_text())


@pytest.fixture(scope="module")
def pool_v1():
    return {r["id"]: r for r in read_jsonl(V1 / "admitted_all.jsonl")}


@pytest.fixture(scope="module")
def rows_v2():
    return read_jsonl(V2 / "admitted_all_v2.jsonl")


def test_counts_add_up(validation, pool_v1, rows_v2):
    dropped = read_jsonl(V2 / "dropped_v2.jsonl")
    rejected = read_jsonl(V2 / "rejected_global_v2.jsonl")
    assert validation["pool_v1"] == len(pool_v1)
    assert len(dropped) == validation["dropped"]
    assert len(rejected) == validation["rejected_global"]
    assert len(rows_v2) == validation["admitted_v2"] == len(pool_v1) - len(dropped) - len(rejected)
    assert all(d["rules"] for d in dropped)
    ids_v2 = {r["id"] for r in rows_v2}
    assert len(ids_v2) == len(rows_v2)
    assert ids_v2.isdisjoint({d["id"] for d in dropped})
    assert ids_v2 <= set(pool_v1)


def test_relabels_applied(validation, pool_v1, rows_v2):
    relabels = {r["id"]: r for r in read_jsonl(V2 / "relabels_v2.jsonl")}
    assert len(relabels) == validation["relabelled"]
    changed = 0
    for r in rows_v2:
        original = pool_v1[r["id"]]
        if r["id"] in relabels:
            assert r["label"] == relabels[r["id"]]["label"] != original["label"]
            assert r["label_v1"] == original["label"] and r["rules_applied"]
            changed += 1
        else:
            assert r["label"] == original["label"] and "label_v1" not in r and r["rules_applied"] == []
    assert changed <= len(relabels)


def test_books_are_split_disjoint_and_lexicon_in_train(validation, rows_v2):
    books = defaultdict(set)
    for r in rows_v2:
        books[r["source"], r["book_key"]].add(r["split"])
        if (r["wave"], r["source"]) == ("mixed", "archive_b28038630"):
            assert r["split"] == "train"
    assert all(len(v) == 1 for v in books.values())
    assert validation["books_in_several_splits"] == {}
    moves = json.loads((V2 / "split_moves_v2.json").read_text())
    assert moves["moved"] == validation["moved_to_train"] == len(moves["rows"])


def test_no_train_label_in_holdout(rows_v2):
    held = {normalize_label(r["label"]) for r in rows_v2 if r["split"] != "train"}
    assert not any(normalize_label(r["label"]) in held for r in rows_v2 if r["split"] == "train")


def test_manifests_match_rows(rows_v2, validation):
    by_split = Counter(r["split"] for r in rows_v2)
    for split in SPLITS:
        manifest = json.loads((V2 / f"manifest_v2_{split}.json").read_text())
        assert len(manifest) == by_split[split]
        assert all(tuple(m) == MANIFEST_FIELDS for m in manifest[:50])
        importer = read_jsonl(V2 / f"import_real_v2_{split}.jsonl")
        assert len(importer) == by_split[split]
        assert {i["split"] for i in importer} == {{"train": "train", "dev": "val", "test": "reserved"}[split]}
    after = validation["per_class_split_after"]
    assert sum(after[c][s] for c in after for s in SPLITS) == len(rows_v2)

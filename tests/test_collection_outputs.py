"""Read back the built T28 artifacts. No network, import-real job or crop generation."""
from collections import Counter, defaultdict
import json
from pathlib import Path

import pytest
from tests._paths import require_file

from greekocr.harvest.collection import (
    FIELDS, MANIFEST_FIELDS, SPLITS, WAVES, digest, global_holdout, normalize_label,
    read_jsonl, source_caps, tallies, validate_row,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/records/harvest/collection"


@pytest.fixture(scope="module")
def collection():
    return read_jsonl(require_file(OUT / "admitted_all.jsonl"))


def test_all_merged_rows_have_uniform_valid_schema(collection):
    for row in collection:
        assert set(row) == set(FIELDS)
        validate_row(row)
    assert len({r["id"] for r in collection}) == len(collection)
    assert len({r["crop_path"] for r in collection}) == len(collection)


def test_all_input_rows_are_accounted_for_and_only_train_rejected(collection):
    rejected = read_jsonl(OUT / "rejected_global.jsonl")
    original = [r for w in WAVES for r in read_jsonl(ROOT / "docs/records/harvest" / w / "admitted.jsonl")]
    assert {r["id"] for r in collection}.isdisjoint({r["id"] for r in rejected})
    assert {r["id"] for r in collection + rejected} == {r["id"] for r in original}
    assert len(collection) + len(rejected) == len(original)
    assert all(r["split"] == "train" and r["reason"] == "label_in_holdout" for r in rejected)
    assert all(r["matching_holdout_labels"] for r in rejected)


def test_no_global_label_leakage_or_prior_wikisource_exclusions(collection):
    held = {normalize_label(r["label"]) for r in collection if r["split"] in ("dev", "test")}
    train = {normalize_label(r["label"]) for r in collection if r["split"] == "train"}
    assert not train & held
    prior = read_jsonl(ROOT / "docs/records/harvest/wikisource/prior_train_exclusions.jsonl")
    assert not train & {r["normalized_label"] for r in prior}


@pytest.mark.parametrize("split", SPLITS)
def test_manifest_is_exact_projection_of_merged_rows(collection, split):
    actual = json.loads(require_file(OUT / f"manifest_{split}.json").read_text())
    expected = [r for r in collection if r["split"] == split]
    assert len(actual) == len(expected)
    for a, e in zip(actual, expected):
        assert set(a) == set(MANIFEST_FIELDS)
        assert a == {k: e["crop_path"] if k == "crop" else e[k] for k in MANIFEST_FIELDS}


def test_import_real_fields_splits_paths_and_document_boundaries(collection):
    imported = read_jsonl(OUT / "import_real_all.jsonl")
    assert len(imported) == len(collection)
    docs = defaultdict(set)
    for a, e in zip(imported, collection):
        assert a["id"] == e["id"] and a["crop"] == e["crop_path"] and a["label"] == e["label"]
        assert a["license"] == e["licence"] and a["source_dataset"] == e["source"]
        assert a["split"] == {"train": "train", "dev": "val", "test": "reserved"}[e["split"]]
        assert a["doc"] and a["admitted"] and a["label_tier"] == "silver"
        docs[a["doc"]].add(a["split"])
    assert all(len(splits) == 1 for splits in docs.values())
    for split in SPLITS:
        subset = read_jsonl(OUT / f"import_real_{split}.jsonl")
        assert {r["id"] for r in subset} == {r["id"] for r in collection if r["split"] == split}


def test_lexicon_70_page_repair_counts_and_no_page_crossing(collection):
    repairs = json.loads((OUT / "split_repairs.json").read_text())["repairs"]
    lex = next(r for r in repairs if r["source"] == "archive_b28038630")
    assert lex["pages"] == 70 and lex["page_splits"] == {"train": 49, "dev": 7, "test": 14}
    assert sum(sum(s.values()) for s in lex["before"].values()) == 9788
    assert sum(s["train"] for s in lex["before"].values()) == 0
    group = [r for r in collection if r["source"] == "archive_b28038630"]
    assert tallies(group) == lex["after_global"]
    assert all(r["split"] == lex["page_assignments"][r["page_id"]] for r in group)


def test_validation_caps_counts_and_sample_coverage(collection):
    validation = json.loads((OUT / "validation.json").read_text())
    assert source_caps(collection) == validation["source_caps"]
    assert tallies(collection) == validation["per_class_split"]
    assert validation["label_collisions"] == validation["duplicate_ids"] == validation["duplicate_paths"] == 0
    for wave, check in validation["crop_checks"].items():
        input_count = len(read_jsonl(ROOT / "docs/records/harvest" / wave / "admitted.jsonl"))
        assert check["existence_checked"] == input_count
        assert check["sha256_and_dimensions_checked"] == min(input_count, 2000)
        assert len(check["sampled_ids"]) == len(set(check["sampled_ids"])) == min(input_count, 2000)
        assert check["errors"] == 0


def test_provenance_sums_all_wave_budgets():
    inventory = json.loads((OUT / "inventory.json").read_text())
    for name in inventory['inputs']:
        if '/google/budget' in name and not (ROOT / name).is_file():
            pytest.skip(f'missing input: {name}')
    provenance = json.loads((OUT / "data_provenance.json").read_text())
    total = 0
    for wave in WAVES:
        entries = [r for p in (ROOT / "docs/harvest/harvest_big" / wave / "google").glob("budget*.jsonl") for r in read_jsonl(p)]
        micro = sum(r["micro_usd"] for r in entries)
        assert provenance[wave]["ledger_micro_usd"] == micro
        assert provenance[wave]["ledger_usd"] == micro / 1_000_000
        total += micro
    assert provenance["round1"]["ledger_by_engine_usd"]["vision"] == .5145
    assert total == 9945000
    assert provenance["wikisource"]["pages"]["read"] == 400
    assert provenance["openarchives"]["lines"]["wave_admitted"] == 25606


def test_frozen_wave_inputs_remain_unchanged():
    inventory = json.loads((OUT / "inventory.json").read_text())
    for name in inventory['inputs']:
        if not (ROOT / name).is_file():
            pytest.skip(f'missing input: {name}')
    inventory = json.loads((OUT / "inventory.json").read_text())
    assert inventory["input_files_unchanged"]
    for path, expected in inventory["inputs"].items():
        assert digest(ROOT / path) == expected


def test_sheet_index_lists_every_existing_admission_image():
    required = ROOT / 'docs/harvest/harvest_big/collection/SHEETS.md'
    if not required.is_file():
        pytest.skip(f'missing input: {required}')
    text = (ROOT / "docs/harvest/harvest_big/collection/SHEETS.md").read_text()
    for wave in WAVES:
        assert wave in text
        for path in (ROOT / "docs/harvest/harvest_big" / wave / "admission_sheet").glob("*"):
            if path.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
                assert str(path) in text
    assert "wikisource" in text

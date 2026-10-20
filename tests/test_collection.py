"""T28 synthetic contracts; tests/conftest.py blocks live network connections."""
from copy import deepcopy
from hashlib import sha256
import json

from PIL import Image
import pytest

from greekocr.harvest.collection import (
    FIELDS, MANIFEST_FIELDS, cap_source, check_crops, check_duplicates, global_holdout,
    importer_row, ledger_cost, mix_marginals, normalize_row, read_wave, repair_splits,
    source_caps, tallies, trainer_manifest, validate_row,
)
from scripts.harvest.collection import plan_targets, reserved_wikisource, test_result as read_test_result


def raw_row(**overrides):
    row = dict(id="book-p000001-l0001", book_key="book", page_id="book-p000001", year=1901,
               decade=1900, source="anemi_round1", licence="internal", script_class="greek_poly",
               split="train", label="Ἄλφα καὶ βῆτα", confidence=.95, bbox=[1, 2, 301, 42],
               crop_path="crops/line.png", crop_sha256="a" * 64, crop_width=300, crop_height=40,
               read_batch="d1")
    row.update(overrides)
    return row


def row(**overrides):
    return normalize_row(raw_row(**overrides), "round1")


def test_uniform_schema_and_round1_metadata_recovery():
    raw = raw_row(year=None, decade=None)
    before = deepcopy(raw)
    result = normalize_row(raw, "round1", {"book": "https://example.invalid/book"})
    assert set(result) == set(FIELDS)
    assert result["human_label"] is None and result["attribution"] is None
    assert result["source_url"] == "https://example.invalid/book"
    assert result["year"] is None and result["decade"] is None
    assert raw == before


def test_label_normalization_matches_t20():
    result = row(label="  α\u0301λφα\tκαὶ\u02d9 βῆτα\n")
    assert result["label"] == "άλφα καὶ· βῆτα"


def test_human_label_is_wikisource_only():
    raw = raw_row(human_label="human", split="test", human_transcription_licence="CC-BY-SA-4.0")
    assert normalize_row(raw, "round1")["human_label"] is None
    wiki = normalize_row(raw, "wikisource")
    assert wiki["human_label"] == "human"
    assert wiki["human_transcription_licence"] == "CC-BY-SA-4.0"
    raw["split"] = "train"
    with pytest.raises(ValueError, match="held out"):
        normalize_row(raw, "wikisource")


@pytest.mark.parametrize("patch", [dict(crop_path="/tmp/a.png"), dict(crop_path="../a.png"),
                                  dict(crop_path="crops/../a.png"), dict(crop_path="./a.png"),
                                  dict(crop_sha256="invalid"), dict(crop_width=0),
                                  dict(crop_height=True), dict(confidence=float("nan")),
                                  dict(confidence=1.1), dict(bbox=[4, 2, 3, 8]),
                                  dict(bbox=[1, 2, float("inf"), 8]), dict(decade=1910),
                                  dict(split="val"), dict(script_class="unknown"), dict(id="")])
def test_schema_rejects_invalid_rows(patch):
    with pytest.raises(ValueError):
        row(**patch)


def test_schema_rejects_extra_keys():
    result = row()
    result["unexpected"] = True
    with pytest.raises(ValueError, match="nonuniform"):
        validate_row(result)


@pytest.mark.parametrize("field", ["id", "crop_path"])
def test_global_duplicate_detection_before_filtering(field):
    first = row()
    second = row(id="another", crop_path="crops/another.png")
    second[field] = first[field]
    second["wave"] = "vouli"
    with pytest.raises(ValueError, match=f"duplicate {field}"):
        check_duplicates([first, second])


def test_identical_labels_with_unique_crops_are_not_duplicates():
    check_duplicates([row(), row(id="another", crop_path="crops/another.png")])


@pytest.mark.parametrize("split", ["dev", "test"])
def test_global_holdout_is_cross_wave_cross_class_and_train_only(split):
    training = row()
    held = row(id="held", split=split, crop_path="crops/held.png")
    held.update(wave="vouli", script_class="greek_mono")
    other = row(id="other", label="διαφορετικό κείμενο", crop_path="crops/other.png")
    original = deepcopy([training, held, other])
    kept, rejected = global_holdout([training, held, other])
    assert [r["id"] for r in kept] == ["held", "other"]
    assert rejected[0]["reason"] == "label_in_holdout"
    assert rejected[0]["matching_holdout_labels"] == ["vouli:held"]
    assert rejected[0]["crop_sha256"] == training["crop_sha256"]
    assert original == [training, held, other]


def test_holdout_handles_canonical_equivalence_and_saved_human_text():
    training = row(label="άλφα")
    kept, rejected = global_holdout([training], {"α\u0301λφα": ["human:page:0"]})
    assert not kept and len(rejected) == 1
    held = normalize_row(raw_row(id="held", split="dev", label="Google differs", human_label="άλφα"), "wikisource")
    kept, rejected = global_holdout([training, held])
    assert kept == [held] and len(rejected) == 1


def test_repeated_train_text_is_retained_without_a_holdout_match():
    rows = [row(), row(id="other", crop_path="crops/other.png")]
    assert global_holdout(rows) == (rows, [])


def test_caps_use_class_train_denominator_and_strict_threshold():
    rows = [row(source="a" if i < 4 else "b", id=str(i)) for i in range(10)]
    rows += [row(source="a", split="test", id="held")]
    rows += [row(source="c", script_class="latin", id="latin")]
    caps = {(r["script_class"], r["source"]): r for r in source_caps(rows)}
    assert caps["greek_poly", "a"]["share"] == .4
    assert not caps["greek_poly", "a"]["over_40_percent"]
    assert caps["greek_poly", "b"]["over_40_percent"]
    assert caps["latin", "c"]["share"] == 1
    assert source_caps([row(split="dev")]) == []


def test_caps_combine_the_same_repository_across_waves():
    rows = [row(source=s) for s in ["openarchives_ntua", "openarchives_mixed_ntua", "other", "other"]]
    caps = source_caps(rows)
    ntua = next(r for r in caps if r["source"] == "openarchives_ntua")
    assert ntua["train"] == 2 and ntua["share"] == .5
    assert cap_source("anemi_round1") != cap_source("anemi_round2")


def test_caps_combine_vouli_and_modern_parliament_repository():
    rows = [row(source=s) for s in ["vouli_parliament_1850s", "parliament_proceedings_1975_2000", "other"]]
    parliament = next(r for r in source_caps(rows) if r["source"] == "hellenic_parliament")
    assert parliament["train"] == 2 and parliament["over_40_percent"]


def lexicon_rows(source="archive_b28038630", wave="mixed", pages=10):
    return [normalize_row(raw_row(id=f"lex-p{p:06d}-l{i}", book_key="lex", page_id=f"lex-p{p:06d}",
                                  source=source, split="test", script_class="latin",
                                  label=f"lexicon printed text {p} {i}", crop_path=f"crops/{p}-{i}.png"), wave)
            for p in range(pages) for i in range(2)]


def test_lexicon_repair_is_seeded_page_disjoint_and_input_order_independent():
    source = lexicon_rows()
    original = deepcopy(source)
    repaired, repairs, _ = repair_splits(source, {})
    reverse, reverse_repairs, _ = repair_splits(list(reversed(source)), {})
    assert repairs[0]["page_splits"] == {"train": 7, "dev": 1, "test": 2}
    assert repairs[0]["page_assignments"] == reverse_repairs[0]["page_assignments"]
    assert {r["id"]: r["split"] for r in repaired} == {r["id"]: r["split"] for r in reverse}
    assert len({(r["page_id"], r["split"]) for r in repaired}) == 10
    assert source == original


def test_repair_happens_before_global_holdout():
    repaired, _, _ = repair_splits(lexicon_rows(), {})
    train = next(r for r in repaired if r["split"] == "train")
    held = row(id="external", split="dev", label=train["label"], crop_path="crops/ext.png")
    kept, rejected = global_holdout(repaired + [held])
    assert train["id"] in {r["id"] for r in rejected}
    assert held in kept


def test_automatic_repair_requires_one_proven_heldout_source():
    rows = lexicon_rows(source="single_repository", wave="openarchives")
    _, repairs, scan = repair_splits(rows, {"openarchives": [{"book_key": "lex"}]})
    assert len(repairs) == 1 and scan[0]["repair_eligible"]
    assert not repair_splits(rows, {})[1]
    rows[0]["source"] = "other_repository"
    assert not repair_splits(rows, {"openarchives": [{"book_key": "lex"}]})[1]


def test_intentional_wikisource_test_only_is_never_repaired():
    rows = lexicon_rows(source="wikisource_el", wave="wikisource")
    repaired, repairs, _ = repair_splits(rows, {"wikisource": [{"book_key": "lex"}]})
    assert not repairs and all(r["split"] == "test" for r in repaired)


def test_manifest_exact_fields_and_importer_adaptation():
    source = row(split="dev")
    manifest = trainer_manifest(source)
    assert set(manifest) == set(MANIFEST_FIELDS)
    assert manifest["crop"] == source["crop_path"]
    imported = importer_row(source, set())
    assert imported["split"] == "val" and imported["doc"] == "round1:book"
    assert imported["license"] == source["licence"]
    assert importer_row(source, {("round1", "anemi_round1")})["doc"] == "round1:book-p000001"
    source["split"] = "test"
    assert importer_row(source, set())["split"] == "reserved"


@pytest.mark.parametrize("kind", ["missing_folder", "missing_summary"])
def test_missing_delivery_does_not_fail(tmp_path, kind):
    if kind == "missing_summary":
        (tmp_path / "docs/records/harvest/round1").mkdir(parents=True)
    result = read_wave(tmp_path, "round1")
    assert result["status"] == "not delivered" and result["rows"] == []


def test_missing_summary_keeps_wave_report_reason(tmp_path):
    directory = tmp_path / "docs/records/harvest/round1"
    directory.mkdir(parents=True)
    (directory / "READS.md").write_text("Collection blocked: saved source shortfall.\n")
    result = read_wave(tmp_path, "round1")
    assert result["status"] == "not delivered"
    assert "source shortfall" in result["reports"]["READS.md"]


def test_budget_sums_integer_reservations_including_failed_attempts(tmp_path):
    directory = tmp_path / "docs/harvest/harvest_big/round1/google"
    directory.mkdir(parents=True)
    entries = [dict(engine="docai", key="a", micro_usd=1500, state="reserved"),
               dict(engine="vision", key="a", micro_usd=1500, state="reserved")]
    (directory / "budget.jsonl").write_text("\n".join(map(json.dumps, entries)))
    (directory / "budget_rest.jsonl").write_text(json.dumps(dict(entries[0], key="b")))
    cost = ledger_cost(tmp_path, "round1")
    assert cost["ledger_micro_usd"] == 4500 and cost["ledger_usd"] == .0045
    assert cost["ledger_by_engine_usd"] == {"docai": .003, "vision": .0015}
    (directory / "budget_rest.jsonl").write_text(json.dumps(entries[0]))
    with pytest.raises(ValueError, match="duplicate budget"):
        ledger_cost(tmp_path, "round1")


@pytest.mark.parametrize("failure", ["missing", "sha", "dimension", "none"])
def test_crop_verification_all_for_small_waves(tmp_path, failure):
    path = tmp_path / "crops/line.png"
    path.parent.mkdir()
    Image.new("L", (300, 40), 255).save(path)
    source = row(crop_sha256=sha256(path.read_bytes()).hexdigest())
    if failure == "missing":
        path.unlink()
    elif failure == "sha":
        source["crop_sha256"] = "b" * 64
    elif failure == "dimension":
        source["crop_height"] = 41
    if failure == "none":
        checked = check_crops(tmp_path, [source])
        assert checked["round1"]["sha256_and_dimensions_checked"] == 1
        assert checked["wikisource"]["existence_checked"] == 0
    else:
        with pytest.raises(ValueError):
            check_crops(tmp_path, [source])


def test_mix_marginals_define_length_digits_and_uppercase():
    rows = [row(label="ΑΒΓΔ １２", year=None, decade=None), row(label="α" * 40)]
    mix = mix_marginals(rows)
    assert mix["digit_bearing"] == 1 and mix["all_caps"] == 1
    assert mix["length_buckets"]["0-19"] == 1 and mix["length_buckets"]["40-79"] == 1
    assert mix["decade"] == {"1900": 1, "unknown": 1}
    assert mix_marginals([])["digit_bearing_share"] == 0


def test_failed_test_receipt_cannot_mark_closeout_done(tmp_path):
    path = tmp_path / "tests.xml"
    path.write_text('<testsuites><testsuite><testcase><failure/></testcase></testsuite></testsuites>')
    with pytest.raises(ValueError, match="all passed"):
        read_test_result(path)
    path.write_text('<testsuites><testsuite><testcase/></testsuite></testsuites>')
    assert read_test_result(path) == 1

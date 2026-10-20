"""T20 synthetic contracts; the global fixtures forbid network connections."""
import copy
import unicodedata as ud

import pytest

from greekocr.harvest.admission import (
    admit, apply_holdout_labels, crop_geometry, has_spacing_mark, inventory,
    normalize_label, page_quality, select_holdout_books, spatial_neighbours,
)


def record(text="Σήμερα γράφουμε ελληνικά", **kwargs):
    return dict(docai_text=text, confidence=.95, flags=[], page_id="p", **kwargs)


def test_inventory_counts_and_foreign_names():
    inv = inventory("αβ éZ Яю 漢한กאב １２3 ·;?! $+=\u0301")
    assert [inv[k] for k in ("greek_letters", "latin_letters", "cyrillic_letters", "other_letters")] == [2, 2, 2, 5]
    assert inv["digits"] == 3 and inv["greek_punctuation"] == 4
    assert inv["other_symbols"] == 4
    assert inv["other_script_letters"] == {"CJK": 1, "HANGUL": 1, "HEBREW": 2, "THAI": 1}
    assert inv["other_letter_names"]["CJK UNIFIED IDEOGRAPH-6F22"] == 1
    assert inv["letter_count"] == 11
    assert inv["nonspace_count"] == 22


@pytest.mark.parametrize("word", ["ΚΕΦΑΛΑΙΟN", "Δαβій", "Fιδον", "δυτικοβо", "ab漢", "aЯ"])
def test_mixed_word_examples(word):
    assert inventory(word)["mixed_words"] == [word]
    assert "mixed_word" in admit(record("ελληνική λέξη " + word))[2]


@pytest.mark.parametrize("text", ["αβ=ab", "αβ-ab", "αβ/ab", "(αβ),[ab];{Яю}", "αβ\tab\nЯю", "αβ—ab…Яю"])
def test_word_delimiters(text):
    assert inventory(text)["mixed_words"] == []


@pytest.mark.parametrize("text", ["IVΙΧLC", "ΙV", "XΧ", "ΙΧ", "IVXLC"])
def test_roman_numerals_exempt(text):
    assert inventory(text)["mixed_words"] == []


@pytest.mark.parametrize("text", ["ΙD", "ΧM", "Ιv", "ΙV2"])
def test_roman_exception_is_exact(text):
    assert inventory(text)["mixed_words"] == [text]


def test_short_rule_uses_unicode_category_not_cached_count():
    assert admit(record("α" * 9, letter_count=999))[2] == ["short_line"]
    assert admit(record("α" * 10))[0]
    assert admit(record("α" * 9 + "\u0301"))[2] == ["short_line"]


@pytest.mark.parametrize("confidence,expected", [(.889999, False), (.89, True), (.95, True)])
def test_confidence_threshold(confidence, expected):
    row = record()
    row["confidence"] = confidence
    assert admit(row)[0] is expected


def test_tall_flag():
    row = record()
    row["flags"] = ["tall_box"]
    assert admit(row)[2] == ["tall_box"]


@pytest.mark.parametrize("suffix,expected", [("!!!!!", True), ("!!!!!!", False), ("\t \n", True)])
def test_symbol_threshold_exact_and_whitespace(suffix, expected):
    assert admit(record("α" * 10 + suffix))[0] is expected


@pytest.mark.parametrize("letter", ["漢", "한", "ก", "ກ", "ཀ", "क", "ક", "ক", "א", "ا", "Ա", "Ა"])
def test_foreign_script_rule(letter):
    assert admit(record("ελληνική λέξη " + letter))[2] == ["foreign_script"]


def test_all_failures_are_reported_in_order_and_input_is_pure():
    row = record("aα漢!!!!!!!!!", bad_page=True)
    row.update(confidence=.1, flags=["tall_box"])
    before = copy.deepcopy(row)
    assert admit(row) == (False, None, ["short_line", "low_confidence", "tall_box", "symbol_heavy",
                                       "foreign_script", "mixed_word", "bad_page"], None)
    assert row == before


def test_page_quality_denominators_and_strict_boundaries():
    rows = [record() for _ in range(10)]
    for row in rows[:5]:
        row["confidence"] = .88
    for row in rows[:3]:
        row["flags"] = ["tall_box"]
    assert not page_quality(rows)["p"]["bad_page"]
    rows[5]["confidence"] = .88
    q = page_quality(rows)["p"]
    assert q["bad_page"] and q["triggers"] == ["low_confidence"]
    rows[5]["confidence"] = .95
    rows[3]["flags"] = ["tall_box"]
    assert page_quality(rows)["p"]["triggers"] == ["tall_boxes"]


def test_page_quality_short_lines_do_not_vote_low_but_tall_lines_do():
    rows = [record(), record("1"), record("1"), record("1")]
    for row in rows[1:]:
        row.update(confidence=.1, flags=["tall_box"])
    q = page_quality(rows)["p"]
    assert q["eligible_lines"] == 1 and q["low_confidence"] == 0
    assert q["bad_page"] and q["tall_box_share"] == .75
    assert page_quality([record("1")])["p"]["low_confidence_share"] == 0


def test_bad_page_propagates_to_individually_good_line():
    assert admit(record(bad_page=True))[2] == ["bad_page"]


@pytest.mark.parametrize("text,expected", [
    ("Σήμερα γράφουμε ελληνικά", "greek_mono"),
    ("ὁ λόγος εἶναι ἑλληνικός", "greek_poly"),
    ("λόγος Ελληνικός ab", "greek_latin_cs"),
    ("ὁ λόγος εἶναι ab", "greek_latin_cs"),
    ("This is a Latin sentence α", "latin"),
    ("Это русская строка", "cyrillic"),
    ("Ελληνικές λέξεις A", "greek_mono"),
    ("Ελληνικές λέξεις 12ab", "greek_mono"),
    ("Ελληνικές λέξεις café", "greek_latin_cs"),
    ("Ελληνικές λέξεις è", "greek_mono"),
])
def test_class_assignment(text, expected):
    assert admit(record(text))[1] == expected


@pytest.mark.parametrize("mark", ["\u0313", "\u0314", "\u0342", "\u0345", "\u0300"])
def test_polytonic_combining_marks_in_nfd(mark):
    assert admit(record("ελληνική γραφή α" + mark))[1] == "greek_poly"


def test_majority_tie_is_deterministic():
    assert admit(record("ααααα BBBBB"))[1] == "greek_latin_cs"


def test_label_normalization_dot_and_spacing_marks_preserved():
    text = "  α\u0301λφα\t \u1fbf\nβητα  \u02d9   "
    assert normalize_label(text) == "άλφα \u1fbf βητα ·"
    assert ud.is_normalized("NFC", normalize_label(text))
    assert has_spacing_mark(text)
    for mark in "\u1fbf\u1fbd\u0384":
        assert normalize_label(f"α {mark} β") == f"α {mark} β"
        assert has_spacing_mark(f"α {mark} β")
    assert not has_spacing_mark("α᾿ β")
    assert not has_spacing_mark("᾿ α")
    assert not has_spacing_mark("1 ᾿ β")


def books(decades=8, size=5):
    return [dict(book_key=f"{d}-{i}", title=f"Book {d}-{i}", year=1860 + 10*d,
                 decade=1860 + 10*d, admitted_lines=500 if i < 3 else 20)
            for d in range(decades) for i in range(size)]


def test_seeded_stratified_holdout_reproducible_preferred_and_pure():
    source = books()
    before = copy.deepcopy(source)
    held = select_holdout_books(source)
    assert held == select_holdout_books(list(reversed(source)))
    assert len(held) == 20 and sum(b["split"] == "dev" for b in held) == 5
    assert sum(b["split"] == "test" for b in held) == 15
    assert all(sum(b["decade"] == d for b in held) >= 2 for d in range(1860, 1940, 10))
    assert all(b["admitted_lines"] >= 300 for b in held)
    assert source == before


def test_holdout_capacity_one_stratum_is_taken_and_total_still_twenty():
    source = books(decades=7) + [dict(book_key="only", title="Only", year=1930, decade=1930, admitted_lines=1)]
    held = select_holdout_books(source)
    assert len(held) == 20 and sum(b["decade"] == 1930 for b in held) == 1
    assert next(b for b in held if b["book_key"] == "only")["admitted_lines"] == 1


def test_holdout_fallback_within_stratum():
    source = books()
    for b in source:
        if b["decade"] == 1860:
            b["admitted_lines"] = 3
    assert sum(b["decade"] == 1860 for b in select_holdout_books(source)) == 2


@pytest.mark.parametrize("source", [books(decades=11), books(decades=2, size=2), books() + [books()[0]]])
def test_holdout_invalid_capacity_or_duplicate_keys(source):
    with pytest.raises(ValueError):
        select_holdout_books(source)


def test_o5_canonical_equality_drops_train_only_and_preserves_raw_text():
    source = [dict(id="a", label="άλφα βητα", split="test"),
              dict(id="b", label="α\u0301λφα\tβητα", split="train", docai_text="raw"),
              dict(id="c", label="άλφα βητα", split="dev"),
              dict(id="d", label="Άλφα βητα", split="train")]
    before = copy.deepcopy(source)
    kept, rejected = apply_holdout_labels(source)
    assert [r["id"] for r in kept] == ["a", "c", "d"]
    assert rejected == [dict(id="b", reasons=["label_in_holdout"], docai_text="raw")]
    assert source == before


def test_o5_normalizes_dot_above():
    kept, rejected = apply_holdout_labels([
        dict(id="a", label="άλφα · βητα", split="dev"),
        dict(id="b", label="άλφα ˙ βητα", split="train")])
    assert len(kept) == len(rejected) == 1


def test_crop_midpoints_then_padding_and_native_rounding():
    bounds, trimmed = crop_geometry([10, 40, 90, 80], [10, 20, 90, 50], [10, 70, 90, 100], [100, 120])
    assert bounds == [6, 43, 94, 77] and trimmed
    assert crop_geometry([10.2, 40.2, 90.2, 80.2], None, None, [100, 120]) == ([6, 38, 95, 83], False)


def test_crop_exact_fifteen_percent_is_not_trimmed():
    assert crop_geometry([10, 20, 90, 40], [10, 0, 90, 23], None, [100, 100]) == ([6, 18, 94, 42], False)
    assert crop_geometry([10, 20, 90, 40], [10, 0, 90, 24], None, [100, 100]) == ([6, 20, 94, 42], True)


def test_crop_page_edge_padding_clamped():
    assert crop_geometry([0, 0, 100, 120], None, None, [100, 120]) == ([0, 0, 100, 120], False)


@pytest.mark.parametrize("bbox,previous,following", [([0, 0, 0, 10], None, None),
    ([0, 0, 10, 10], [0, 0, 10, 10], [0, 0, 10, 10]), ([200, 0, 220, 10], None, None)])
def test_crop_invalid_geometry_raises(bbox, previous, following):
    with pytest.raises(ValueError):
        crop_geometry(bbox, previous, following, [100, 100])


def test_spatial_neighbours_use_all_boxes_independent_of_provider_order():
    rows = [dict(id="middle", page_id="p", bbox=[0, 40, 100, 80]),
            dict(id="below_rejected", page_id="p", bbox=[0, 70, 100, 110]),
            dict(id="other_column", page_id="p", bbox=[110, 45, 210, 85]),
            dict(id="above_rejected", page_id="p", bbox=[0, 10, 100, 50]),
            dict(id="duplicate", page_id="p", bbox=[0, 40, 100, 80])]
    neighbours = spatial_neighbours(rows)
    assert neighbours == spatial_neighbours(list(reversed(rows)))
    assert neighbours["middle"] == (rows[3]["bbox"], rows[1]["bbox"])
    assert neighbours["other_column"] == (None, None)
    assert crop_geometry(rows[0]["bbox"], *neighbours["middle"], [220, 120])[0] == [0, 43, 104, 77]


def test_neighbours_reject_cross_page_input():
    with pytest.raises(ValueError):
        spatial_neighbours([dict(page_id="a"), dict(page_id="b")])


def test_margin_box_with_small_horizontal_overlap_is_not_same_column():
    rows = [dict(id="line", page_id="p", bbox=[1583, 1055, 2463, 1090]),
            dict(id="margin", page_id="p", bbox=[1369, 901, 1633, 1186]),
            dict(id="below", page_id="p", bbox=[1515, 1048, 2459, 1161])]
    neighbours = spatial_neighbours(rows)
    assert neighbours["line"] == (None, rows[2]["bbox"])
    assert crop_geometry(rows[0]["bbox"], *neighbours["line"], [2500, 1400]) == ([1579, 1053, 2467, 1075], True)


# ADM5 standard source-aware contract. Historical source-free tests above
# intentionally keep the Wave-0 tuple API stable.
from greekocr.harvest.admission import (
    TABLE_VERSION, SOURCE_POLICIES, evaluate, evaluate_rows, load_codec, run_files,
)


def standard(text="ὁ λόγος εἶναι ἑλληνικός", source="bsb_poly1850", **fields):
    return dict(label=text, source=source, primary_class="poly1850", **fields)


@pytest.mark.parametrize("word,rule", [
    ("한", "unexpected_script"), ("Δαβій", "mixed_script_word"), ("ΚΕΦΑΛΑΙΟN", "mixed_script_word"),
    ("Fιδον", "mixed_script_word"), ("ΙV", "mixed_script_word"),
])
def test_standard_planted_foreign_and_mixed(word, rule):
    result = evaluate(standard("ἑλληνικὸς λόγος " + word))
    assert not result["rules_passed"] and rule in result["failed_rules"]
    if word == "한":
        assert "foreign_char" in result["failed_rules"]


def test_standard_six_letters():
    result = evaluate(standard("αβγδεζ"))
    assert result["failed_rules"] == ["short_line", "geometry_unavailable"]


@pytest.mark.parametrize("row", [
    standard(), standard("Это чистая русская строка", source="serbia"),
    standard("Σύνολο πληθυσμού 1234 56", source="elstat"),
])
def test_standard_clean_sources_pass_and_missing_checks_are_na(row):
    result = evaluate(row)
    assert result["failed_rules"] == ["geometry_unavailable"], result
    assert not result["passed"] and result["status"] == "fail"
    assert result["confidence"] == "n/a"
    assert result["checks"]["low_confidence"] == result["checks"]["tall_box"] == "n/a"
    assert result["expected_language"]


def test_standard_number_only_still_obeys_length_and_symbols():
    assert evaluate(standard("1234567890", source="elstat"))["failed_rules"] == ["short_line", "nonletter_frac", "geometry_unavailable"]


def test_standard_tall_pre_drop_median_and_boundary():
    rows = [standard(page_id="p", bbox=[0, 0, 100, h]) for h in (10, 10, 10, 17, 18)]
    results = list(evaluate_rows(rows))
    assert all(r["failed_rules"] == ["geometry_unavailable"] for r in results[:4])
    assert results[-1]["failed_rules"] == ["tall_box", "geometry_unavailable"]
    assert results[-1]["page_median_line_height"] == 10


def test_standard_pages_and_sources_do_not_mix_medians():
    rows = [standard(page_id="a", crop_bbox=[0, 0, 100, 10]),
            standard(page_id="b", crop_bbox=[0, 0, 100, 50]),
            standard(source="nlg", page_id="a", crop_bbox=[0, 0, 100, 40])]
    assert [r["page_median_line_height"] for r in evaluate_rows(rows)] == [10, 50, 40]


def test_standard_dot_above_nfc_and_no_lookalike_correction():
    result = evaluate(standard("  ὁ λόγος εἶναι\tἑλληνικός ˙"))
    assert result["failed_rules"] == ["geometry_unavailable"]
    assert result["label"] == "ὁ λόγος εἶναι ἑλληνικός ·"
    assert result["normalisations"] == ["R8:dot_above_to_middle_dot", "NFC", "collapse_whitespace"]
    result = evaluate(standard("ἑλληνικὸς λόγος ΚΕΦΑΛΑΙΟN"))
    assert "ΚΕΦΑΛΑΙΟN" in result["label"] and not result["rules_passed"]


@pytest.mark.parametrize("symbol", list("§†°%=+/"))
def test_standard_codec_symbols_preserved(symbol):
    result = evaluate(standard("ἑλληνικὸς λόγος " + symbol))
    assert result["failed_rules"] == ["geometry_unavailable"] and result["label"].endswith(symbol)


def test_standard_symbols_are_checked_against_actual_codec():
    codec = load_codec()
    codec["atoms"] = codec["atoms"] - {"§"}
    assert "foreign_char" in evaluate(standard("ἑλληνικὸς λόγος §"), codec=codec)["failed_rules"]
    assert "foreign_char" in evaluate(standard("ἑλληνικὸς λόγος 🚀"))["failed_rules"]


def test_standard_majority_latin_needs_mixed_class_and_no_cyrillic_on_greek():
    row = standard("This is a Latin sentence α")
    assert evaluate(row)["failed_rules"] == ["unexpected_language", "geometry_unavailable"]
    row["primary_class"] = "mixed_greek_latin"
    assert evaluate(row)["failed_rules"] == ["geometry_unavailable"]
    assert evaluate(standard("ἑλληνικὸς λόγος ab"))["failed_rules"] == ["geometry_unavailable"]
    assert "unexpected_script" in evaluate(standard("ἑλληνικὸς λόγος Я"))["failed_rules"]


def test_standard_v2_class_is_declared_not_inferred():
    row = dict(source="anemi_mixed", wave="mixed", script_class="latin", label="This is a Latin sentence")
    assert evaluate(row)["failed_rules"] == ["geometry_unavailable"]
    row["script_class"] = "greek_poly"
    assert evaluate(row)["failed_rules"] == ["unexpected_language", "geometry_unavailable"]
    row["script_class"] = "invented"
    with pytest.raises(ValueError):
        evaluate(row)
    with pytest.raises(ValueError):
        evaluate(standard(source="unknown"))
    row.update(script_class="latin", wave="round1")
    with pytest.raises(ValueError):
        evaluate(row)


@pytest.mark.parametrize("confidence,failed", [(.889, True), (.89, False), (None, False)])
def test_standard_confidence(confidence, failed):
    result = evaluate(standard(confidence=confidence))
    assert ("low_confidence" in result["failed_rules"]) is failed


def test_standard_all_failures_and_input_pure():
    row = standard("αa한!!!!!!!!!", confidence=.1, bbox=[0, 0, 100, 18], page_median_line_height=10)
    before = copy.deepcopy(row)
    result = evaluate(row)
    assert result["failed_rules"] == ["short_line", "low_confidence", "tall_box", "nonletter_frac", "unexpected_script", "mixed_script_word", "foreign_char", "geometry_unavailable"]
    assert result["first_failure"] == "short_line" and row == before


def test_standard_source_aware_admit_routes_to_standard():
    row = standard("ἑλληνικὸς λόγος ΙV")
    assert admit(row)[2] == ["mixed_script_word", "geometry_unavailable"]


def test_standard_cli_receipt_and_census(tmp_path):
    import hashlib
    import json
    from greekocr.harvest.admission import main
    source = tmp_path / "input.jsonl"
    rows = [standard("ὁ λόγος εἶναι ἑλληνικός ˙"), standard("αβγδεζ"), standard("aα한!!!!!!!!!")]
    source.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    before = source.read_bytes()
    main(["admit", str(source), "--output-dir", str(tmp_path / "out")])
    receipt = json.loads((tmp_path / "out/input_admission_receipt.json").read_text())
    assert receipt["rows_total"] == 3 and receipt["rows_pass"] == 0
    assert receipt["drops_per_rule"]["short_line"] == 2
    assert receipt["drops_per_rule"]["mixed_script_word"] == 1
    assert receipt["input_sha256"] == hashlib.sha256(before).hexdigest()
    assert len((tmp_path / "out/input_admission.jsonl").read_text().splitlines()) == 3
    assert (tmp_path / "out/input_admitted.jsonl").read_text() == ""
    decision = json.loads((tmp_path / "out/input_admission.jsonl").read_text().splitlines()[0])
    assert not decision["pass"] and decision["rules_failed"] == ["geometry_unavailable"]
    assert receipt["neighbour_words_unavailable"] == 3
    main(["census", str(source), "--output-prefix", str(tmp_path / "census")])
    census = json.loads((tmp_path / "census_admission_receipt.json").read_text())
    assert census["drops_per_rule"] == receipt["drops_per_rule"]
    assert (tmp_path / "census.md").exists() and source.read_bytes() == before
    assert all(p["provenance"] for p in SOURCE_POLICIES.values())


def test_standard_unknown_source_does_not_create_outputs(tmp_path):
    import json
    source = tmp_path / "input.jsonl"
    source.write_text(json.dumps(standard(source="unknown")) + "\n")
    with pytest.raises(ValueError):
        run_files([source], output_dir=tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_standard_v2_cyrillic_wave_can_declare_latin_dictionary_class():
    row = dict(source="archive_b28038630", wave="mixed", script_class="latin", label="This is a Latin dictionary")
    assert evaluate(row)["failed_rules"] == ["geometry_unavailable"]
    row.update(source="archive_b24878935", wave="cyrillic")
    assert evaluate(row)["failed_rules"] == ["geometry_unavailable"]
    row["label"] = "Это чистая русская строка"
    assert evaluate(row)["failed_rules"] == ["unexpected_script", "geometry_unavailable"]


def test_standard_explicit_full_page_median_precedes_subset_median():
    row = standard(page_id="p", bbox=[0, 0, 100, 18], page_median_line_height=10)
    assert list(evaluate_rows([row]))[0]["failed_rules"] == ["tall_box", "geometry_unavailable"]

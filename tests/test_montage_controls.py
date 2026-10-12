"""T14b layout/comparison and budget controls, entirely offline."""
import json
from pathlib import Path

from PIL import Image, ImageChops
import pytest

from greekocr.harvest.montage import build_montages
from greekocr.harvest.montage_controls import letters_marks, compare_control, summarise_controls
from greekocr.harvest.readers import Readers, read_jsonl


@pytest.mark.parametrize("mode", ["L", "RGB"])
def test_no_rule_preserves_pixels_geometry_and_white_gap(tmp_path, mode):
    records = []
    for i, size in enumerate(((50, 32), (80, 85), (65, 40))):
        path = tmp_path / f"crop{i}.png"
        Image.new(mode, size, 30 if mode == "L" else (30, 60, 90)).save(path)
        records.append(dict(id=str(i), straight_crop=str(path)))
    rule = build_montages(records, 20, tmp_path / "rule", tmp_path / "rule_maps")[0]
    plain = build_montages(records, 20, tmp_path / "plain", tmp_path / "plain_maps", grey_rule=False)[0]
    assert rule["boxes"] == plain["boxes"]
    assert (rule["width"], rule["height"], rule["mode"]) == (plain["width"], plain["height"], plain["mode"])
    with Image.open(plain["image"]) as montage, Image.open(rule["image"]) as ruled:
        for record in records:
            band = plain["boxes"][record["id"]]
            with Image.open(record["straight_crop"]) as source:
                assert montage.crop((0, band["y0"], band["x1"], band["y1"])).tobytes() == source.tobytes()
            if band["x1"] < montage.width:
                padding = montage.crop((band["x1"], band["y0"], montage.width, band["y1"]))
                assert all(lo == hi == 255 for lo, hi in ([padding.getextrema()] if mode == "L" else padding.getextrema()))
        for a, b in zip(rule["separators"], plain["separators"]):
            assert (a["y0"], a["y1"]) == (b["y0"], b["y1"])
            assert b["rule_y0"] is b["rule_y1"] is None
            gap = montage.crop((0, b["y0"], montage.width, b["y1"]))
            assert all(lo == hi == 255 for lo, hi in ([gap.getextrema()] if mode == "L" else gap.getextrema()))
            ruled.paste(gap, (0, b["y0"]))
        assert ImageChops.difference(montage, ruled).getbbox() is None
    assert json.loads(Path(plain["map"]).read_text()) == plain


def test_no_rule_n20_tail_and_height_split(tmp_path):
    path = tmp_path / "crop.png"
    Image.new("L", (80, 30), 20).save(path)
    records = [dict(id=str(i), straight_crop=str(path)) for i in range(30)]
    maps = build_montages(records, 20, tmp_path / "images", tmp_path / "maps", grey_rule=False)
    assert [m["actual_n"] for m in maps] == [20, 10]
    smaller = build_montages(records[:10], 20, tmp_path / "small", tmp_path / "small_maps", max_height=450, grey_rule=False)
    assert [m["actual_n"] for m in smaller] == [5, 5]
    assert all(s["rule_y0"] is None for m in smaller for s in m["separators"])


@pytest.mark.parametrize("value", [0, 1, None, "false"])
def test_no_rule_requires_boolean(tmp_path, value):
    with pytest.raises(ValueError, match="grey_rule"):
        build_montages([], 20, tmp_path, tmp_path, grey_rule=value)


@pytest.mark.parametrize("apostrophe", ["'", "’", "‘", "ʼ", "᾿", "᾽", "῾", "`", "´"])
def test_letters_marks_unifies_spacing_apostrophes(apostrophe):
    assert letters_marks("* ν" + apostrophe + " ἄλφα, 123!") == letters_marks("ν ἄλφα")


@pytest.mark.parametrize("reference,prediction,exact,lm", [
    ("ά", "α\u0301", True, True),
    ("α", "ἀ", False, False),
    ("σ", "ς", False, False),
    ("α", "Α", False, False),
    ("* α β!", "αβ", False, True),
    ("α  β", "α β", False, True),
])
def test_control_identity(reference, prediction, exact, lm):
    result = compare_control(reference, prediction)
    assert result["identical"] is exact
    assert result["letters_marks_identical"] is lm
    assert sum(result["edit_operations"].values()) == result["nfd_edits"]


def test_difference_histogram_counts_both_sides_of_substitution():
    result = compare_control("α", "β")
    assert result["char_kind_histogram"] == {"letter": 2}
    assert result["edit_operations"] == {"substitute": 1}
    assert result["kind_transitions"] == {"letter->letter": 1}
    assert compare_control("α", "ἀ")["char_kind_histogram"] == {"mark": 1}
    assert compare_control("α", "* α")["char_kind_histogram"] == {"punctuation": 1, "whitespace": 1}


def test_histogram_all_character_kinds_and_empty_inputs():
    result = compare_control("", "α\u0301 1*$\x00")
    assert result["char_kind_histogram"] == dict(letter=1, mark=1, whitespace=1, number=1, punctuation=1, symbol=1, other=1)
    assert result["nfd_edits"] == 7 and result["edit_operations"] == {"insert": 7}
    assert compare_control("", "")["identical"]


def test_summary_percentages_and_histogram():
    rows = [compare_control("ά", "α\u0301"), compare_control("α", "α!"), compare_control("α", "β")]
    result = summarise_controls(rows)
    assert result["exact_count"] == 1 and result["exact_pct"] == pytest.approx(100 / 3)
    assert result["letters_marks_count"] == 2
    assert result["char_kind_histogram"] == {"letter": 2, "punctuation": 1}
    with pytest.raises(ValueError):
        summarise_controls([])


def test_reserved_interrupted_attempt_is_not_recalled(tmp_path, monkeypatch):
    image = tmp_path / "crop.png"
    Image.new("L", (10, 10), 255).save(image)
    from hashlib import sha256
    key = sha256(image.read_bytes()).hexdigest()
    readers = Readers(tmp_path / "fresh", cap=.5)
    readers.budget.max_calls = 64
    readers.budget.reserve("vision", key)
    monkeypatch.setattr(readers.vision, "read_annotation", lambda _: pytest.fail("network called"))
    assert readers.call("vision", image)["error_class"] == "InterruptedReservedAttempt"
    assert len(read_jsonl(readers.budget.path)) == 1


def test_control_budget_stops_at_64_calls(tmp_path):
    from greekocr.harvest.readers import Budget, BudgetExceeded
    budget = Budget(tmp_path / "budget.jsonl", cap=.5, max_calls=64)
    for i in range(64):
        budget.reserve("vision" if i % 2 == 0 else "docai", str(i))
    with pytest.raises(BudgetExceeded):
        budget.reserve("vision", "extra")
    assert budget.receipt()["cost_usd"] == .096


@pytest.mark.parametrize("changed,safe", [
    ({"objects/aa/bb": [10, 2], "worktrees/other/index": [10, 2], "refs/heads/other": [41, 2]}, True),
    ({"index": [10, 2]}, False),
    ({"refs/heads/main": [41, 2]}, False),
])
def test_git_audit_distinguishes_other_worktree_from_main(changed, safe):
    from scripts.harvest.montage_controls import audit_git
    before = {"HEAD": [20, 1], "index": [10, 1], "refs/heads/main": [41, 1]}
    after = dict(before, **changed)
    audit = audit_git(before, after)
    assert audit["global_git_metadata_unchanged"] is False
    assert audit["main_worktree_git_metadata_unchanged"] is safe

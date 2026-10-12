"""Offline physical layout, response-box assignment and T14 gate tests."""
import hashlib
import json

import numpy as np
from PIL import Image
import pytest

from greekocr.harvest.montage import (assign_lines, assign_symbols, build_montages,
                                     compare_nfd, response_lines, response_symbols, summarise)


def crops(tmp_path, sizes):
    result = []
    for i, size in enumerate(sizes):
        path = tmp_path / f"crop{i}.png"
        # Nonuniform pixels catch scaling and offset mistakes.
        data = np.random.default_rng(i).integers(0, 256, (size[1], size[0]), dtype=np.uint8)
        Image.fromarray(data).save(path)
        result.append(dict(id=f"crop{i}", straight_crop=str(path)))
    return result


def build(tmp_path, records, n=10, **limits):
    return build_montages(records, n, tmp_path / "images", tmp_path / "maps", **limits)


@pytest.mark.parametrize("n,counts", [(10, [10, 10, 3]), (20, [20, 3]), (40, [23])])
def test_native_layout_and_map(tmp_path, n, counts):
    records = crops(tmp_path, [(30 + i, 20 + i % 4) for i in range(23)])
    maps = build(tmp_path, records, n)
    assert [m["actual_n"] for m in maps] == counts
    for mapping in maps:
        assert json.loads(open(mapping["map"]).read()) == mapping
        assert hashlib.sha256(open(mapping["image"], "rb").read()).hexdigest() == mapping["image_sha256"]
        out = np.asarray(Image.open(mapping["image"]))
        assert mapping["width"] == max(b["width"] for b in mapping["boxes"].values())
        for band in mapping["boxes"].values():
            original = np.asarray(Image.open(band["crop"]))
            np.testing.assert_array_equal(out[band["y0"]:band["y1"], band["x0"]:band["x1"]], original)
            assert (out[band["y0"]:band["y1"], band["x1"]:] == 255).all()
        for gap in mapping["separators"]:
            pixels = out[gap["y0"]:gap["y1"]]
            assert gap["y1"] - gap["y0"] == 60
            assert (out[gap["rule_y0"]:gap["rule_y1"]] == 153).all()
            assert np.count_nonzero(pixels != 255) == 2 * mapping["width"]


def test_gap_uses_larger_adjacent_height(tmp_path):
    mapping = build(tmp_path, crops(tmp_path, [(100, 80), (90, 110)]))[0]
    assert mapping["height"] == 300
    gap = mapping["separators"][0]
    assert gap["y1"] - gap["y0"] == 110
    assert gap["rule_y0"] == 134


def test_height_split(tmp_path):
    maps = build(tmp_path, crops(tmp_path, [(100, 40)] * 10), max_height=250)
    assert sum(m["actual_n"] for m in maps) == 10
    assert all(m["height"] <= 250 and m["split_reasons"] for m in maps)


def test_png_split_uses_encoded_bytes(tmp_path):
    records = crops(tmp_path, [(100, 40)] * 4)
    one = build_montages(records[:1], 10, tmp_path / "one", tmp_path / "one_maps")[0]
    cap = one["png_bytes"] + 1000
    maps = build(tmp_path, records, max_png_bytes=cap)
    assert len(maps) == 4
    assert all(m["png_bytes"] <= cap and m["split_reasons"] == ["png_bytes", "png_bytes"] for m in maps)


@pytest.mark.parametrize("limits", [dict(max_height=10), dict(max_png_bytes=50), dict(max_width=20)])
def test_oversized_native_singleton_is_rejected(tmp_path, limits):
    with pytest.raises(ValueError):
        build(tmp_path, crops(tmp_path, [(30, 40)]), **limits)


@pytest.mark.parametrize("n", [0, 1, 11, True, 10.0])
def test_invalid_n(tmp_path, n):
    with pytest.raises(ValueError):
        build(tmp_path, crops(tmp_path, [(30, 40)]), n)


def test_duplicate_ids(tmp_path):
    rows = crops(tmp_path, [(30, 40)])
    with pytest.raises(ValueError, match="unique"):
        build(tmp_path, rows * 2)


@pytest.mark.parametrize("limits", [dict(max_width=2601), dict(max_height=10001), dict(max_png_bytes=8_000_001)])
def test_t14_size_ceilings_cannot_be_relaxed(tmp_path, limits):
    with pytest.raises(ValueError, match="ceilings"):
        build(tmp_path, crops(tmp_path, [(30, 40)]), **limits)


def mapping():
    return dict(boxes=dict(a=dict(x0=0, x1=100, y0=0, y1=40),
                           b=dict(x0=0, x1=100, y0=100, y1=140)))


def piece(text, box):
    return dict(text=text, bbox=box, confidence=.9)


def test_height_threshold_is_not_area():
    # Exactly 70% vertically, with most width in the padded region.
    assigned = assign_lines([piece("άλφα", [0, -3, 1000, 7])], mapping())
    assert assigned["crops"]["a"]["text"] == "άλφα"
    assert assigned["crops"]["a"]["status"] == "ok"
    assert assigned["crops"]["b"]["lost"]


def test_below_threshold_and_separator_boxes_are_unassigned():
    assigned = assign_lines([piece("άλφα", [0, -4, 90, 6]), piece("—", [0, 65, 100, 67])], mapping())
    assert assigned["unassigned_box_count"] == 2
    assert all(crop["lost"] and not crop["merged"] for crop in assigned["crops"].values())


def test_cross_band_merged_marks_both_and_does_not_guess():
    assigned = assign_lines([piece("άλφα βήτα", [0, 20, 90, 120])], mapping())
    assert assigned["merged_box_count"] == 1
    assert all(crop["merged"] and crop["lost"] and crop["text"] == "" for crop in assigned["crops"].values())


def test_side_by_side_split_joins_in_x_order():
    assigned = assign_lines([piece("βήτα", [50, 2, 95, 35]), piece("άλφα", [0, 3, 40, 36])], mapping())
    crop = assigned["crops"]["a"]
    assert crop["text"] == "άλφα βήτα"
    assert crop["split"] and not crop["lost"] and not crop["merged"]
    assert "horizontal_pieces_joined" in crop["flags"] and not crop["rejected"]


def test_stacked_split_is_retained_and_rejected():
    assigned = assign_lines([piece("βήτα", [0, 25, 90, 38]), piece("άλφα", [0, 0, 90, 15])], mapping())
    crop = assigned["crops"]["a"]
    assert crop["text"] == "άλφα\nβήτα"
    assert crop["split"] and crop["rejected"] and "stacked_bands" in crop["flags"]


def vertices(box, normalized=False, size=(100, 140)):
    x0, y0, x1, y1 = box
    points = [dict(x=x, y=y) for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
    if normalized:
        return dict(normalizedVertices=[dict(x=p["x"] / size[0], y=p["y"] / size[1]) for p in points])
    return dict(vertices=points)


def test_synthetic_docai_lines_symbols_and_assignment():
    def layout(start, end, box):
        return dict(textAnchor=dict(textSegments=[dict(startIndex=start, endIndex=end)]),
                    boundingPoly=vertices(box, True), confidence=.8)
    raw = dict(document=dict(text="Α\nΒ\n", pages=[dict(
        lines=[dict(layout=layout(0, 2, [0, 1, 90, 35])), dict(layout=layout(2, 4, [0, 101, 90, 135]))],
        symbols=[dict(layout=layout(0, 1, [0, 1, 20, 35])), dict(layout=layout(2, 3, [0, 101, 20, 135]))])]))
    lines = response_lines("docai", raw, (100, 140))
    assert len(lines) == 2
    assigned = assign_lines(lines, mapping())["crops"]
    assert assigned["a"]["text"] == "Α" and assigned["b"]["text"] == "Β"
    symbols = assign_symbols(response_symbols("docai", raw, (100, 140)), mapping())
    assert not symbols["unassigned"] and symbols["crops"]["a"][0]["confidence"] == .8


def test_docai_paragraph_fallback_preserves_cross_band_box():
    raw = dict(document=dict(text="Α Β", pages=[dict(paragraphs=[dict(layout=dict(
        textAnchor=dict(textSegments=[dict(endIndex=3)]), boundingPoly=vertices([0, 0, 90, 135])))])]))
    lines = response_lines("docai", raw, (100, 140))
    assert assign_lines(lines, mapping())["merged_box_count"] == 1


def test_synthetic_vision_breaks_and_symbol_boxes():
    def symbol(text, box):
        return dict(text=text, boundingBox=vertices(box), confidence=.9,
                    property=dict(detectedBreak=dict(type="LINE_BREAK")))
    raw = dict(responses=[dict(fullTextAnnotation=dict(pages=[dict(blocks=[dict(paragraphs=[dict(
        confidence=.85, words=[dict(symbols=[symbol("Α", [0, 1, 90, 35]), symbol("Β", [0, 101, 90, 135])])])])])]))])
    lines = response_lines("vision", raw, (100, 140))
    assigned = assign_lines(lines, mapping())["crops"]
    assert assigned["a"]["text"] == "Α" and assigned["b"]["text"] == "Β"
    assert len(response_symbols("vision", raw, (100, 140))) == 2


def test_no_geometry_fails_closed():
    lines = response_lines("vision", dict(responses=[dict(fullTextAnnotation=dict(text="Α Β"))]), (100, 140))
    assert all(crop["lost"] for crop in assign_lines(lines, mapping())["crops"].values())


def test_nfd_equality_preserves_whitespace_and_counts_combining_marks():
    assert compare_nfd("ά", "α\u0301")["identical"]
    assert not compare_nfd("Α Β", "Α  Β")["identical"]
    assert compare_nfd("ά", "α")["nfd_cer"] == .5


@pytest.mark.parametrize("identical,merged,lost,adopt", [(97, 0, 0, True), (96, 0, 0, False),
                                                       (100, 1, 0, False), (100, 0, 1, False)])
def test_summary_gate_and_weighted_confidence(identical, merged, lost, adopt):
    rows = [dict(identical=i < identical, nfd_cer=0 if i < identical else .1,
                 merged=i < merged, lost=i < lost, split=False, rejected=False,
                 single_symbols=[dict(confidence=.8)], montage_symbols=[dict(confidence=.9), dict(confidence=.7)])
            for i in range(100)]
    result = summarise(rows, 5)
    assert result["adopt"] is adopt
    assert result["cost_per_1000_lines_usd"] == .075
    assert result["single_symbol_count"] == 100 and result["montage_symbol_count"] == 200
    assert result["confidence_delta"] == pytest.approx(0)

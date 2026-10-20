"""Native flush pixels, grouping and adjacent-band assignment, offline."""
import hashlib
import json

import numpy as np
from PIL import Image
import pytest

from greekocr.harvest.montage import (assign_lines, background_shade,
                                     build_montages, group_flush_crops)


def save_crop(tmp_path, ident, pixels, mode="L"):
    path = tmp_path / f"{ident}.png"
    Image.fromarray(np.asarray(pixels, dtype=np.uint8), mode=mode).save(path)
    return dict(id=ident, straight_crop=str(path))


@pytest.mark.parametrize("pixels,expected", [
    ([[0, 10, 20, 30]], 25), ([[0, 10, 20, 30, 40]], 30),
    ([[0, 100, 200, 200, 200, 210]], 200), ([[255]], 255),
    ([[12]], 12), ([[0, 255, 255, 255]], 255),
])
def test_background_is_median_of_brightest_half(tmp_path, pixels, expected):
    row = save_crop(tmp_path, "crop", pixels)
    assert background_shade(row["straight_crop"]) == expected


@pytest.mark.parametrize("mode", ["L", "RGB", "mixed"])
def test_flush_native_pixels_own_padding_and_contiguous_map(tmp_path, mode):
    rows = []
    for index, (width, height, shade) in enumerate(((8, 3, 170), (5, 7, 221), (7, 4, 193))):
        pixels = np.full((height, width), shade, np.uint8)
        pixels[0, 0] = index  # verify native nonuniform pixels and placement
        crop_mode = "RGB" if mode == "RGB" or mode == "mixed" and index == 1 else "L"
        if crop_mode == "RGB":
            pixels = np.repeat(pixels[:, :, None], 3, axis=2)
        rows.append(save_crop(tmp_path, str(index), pixels, crop_mode))
    mapping = build_montages(rows, 10, tmp_path / "images", tmp_path / "maps", layout="flush")[0]
    assert mapping["layout"] == "flush" and mapping["separators"] == []
    assert (mapping["width"], mapping["height"]) == (8, 14)
    assert list(mapping["boxes"]) == [r["id"] for r in rows]
    assert json.loads(open(mapping["map"]).read()) == mapping
    assert hashlib.sha256(open(mapping["image"], "rb").read()).hexdigest() == mapping["image_sha256"]
    with Image.open(mapping["image"]) as montage:
        out = np.asarray(montage)
        y = 0
        for row in rows:
            band = mapping["boxes"][row["id"]]
            with Image.open(row["straight_crop"]) as crop:
                expected = np.asarray(crop.convert(montage.mode))
            assert band["x0"] == 0 and band["y0"] == y
            assert band["y1"] == y + band["height"]
            np.testing.assert_array_equal(out[y:band["y1"], :band["width"]], expected)
            assert (out[y:band["y1"], band["width"]:] == band["background_shade"]).all()
            assert band["padding_shade"] == band["background_shade"] != 255
            y = band["y1"]
        assert y == montage.height


def test_rgb_shade_uses_luminance_without_changing_native_color(tmp_path):
    pixels = np.full((2, 3, 3), (120, 160, 200), np.uint8)
    row = save_crop(tmp_path, "color", pixels, "RGB")
    assert background_shade(row["straight_crop"]) == Image.open(row["straight_crop"]).convert("L").getpixel((0, 0))
    wide = save_crop(tmp_path, "wide", np.full((2, 6), 180))
    mapping = build_montages([row, wide], 10, tmp_path / "out", tmp_path / "maps", layout="flush")[0]
    out = np.asarray(Image.open(mapping["image"]))
    np.testing.assert_array_equal(out[:2, :3], pixels)
    assert (out[:2, 3:] == background_shade(row["straight_crop"])).all()


def test_half_integral_shade_rounds_up_in_8bit_padding(tmp_path):
    rows = [save_crop(tmp_path, "narrow", [[0, 1, 10, 11]]),
            save_crop(tmp_path, "wide", [[70] * 7])]
    mapping = build_montages(rows, 10, tmp_path / "out", tmp_path / "maps", layout="flush")[0]
    assert mapping["boxes"]["narrow"]["background_shade"] == 10.5
    assert mapping["boxes"]["narrow"]["padding_shade"] == 11
    assert (np.asarray(Image.open(mapping["image"]))[0, 4:] == 11).all()


@pytest.mark.parametrize("n,counts", [(10, [10, 10, 3]), (20, [20, 3])])
def test_group_shade_then_height_stable_ties_and_tail(tmp_path, n, counts):
    specs = [(180, 5), (170, 6), (170, 3), (180, 5)] + [(175 + i % 3, 3 + i % 4) for i in range(19)]
    rows = [save_crop(tmp_path, str(i), np.full((height, 5), shade)) for i, (shade, height) in enumerate(specs)]
    original = [dict(row) for row in rows]
    groups = group_flush_crops(rows, n)
    flat = [row for group in groups for row in group]
    assert rows == original
    assert [len(group) for group in groups] == counts
    assert [int(row["id"]) for row in flat] == sorted(range(23), key=lambda i: specs[i])
    assert [row["sorted_index"] for row in flat] == list(range(23))
    for index, group in enumerate(groups):
        assert all(row["group"] == f"n{n:02d}-{index:03d}" for row in group)
        assert all(row["source_index"] == int(row["id"]) for row in group)
        assert all((row["background_shade"], row["height"]) == specs[int(row["id"])] for row in group)


def test_flush_height_limit_has_no_phantom_gap(tmp_path):
    row = save_crop(tmp_path, "a", np.full((40, 10), 180))
    rows = [dict(row, id=str(i)) for i in range(10)]
    maps = build_montages(rows, 10, tmp_path / "images", tmp_path / "maps", layout="flush", max_height=200)
    assert [m["actual_n"] for m in maps] == [5, 5]
    assert all(m["height"] == 200 and m["split_reasons"] == ["height"] for m in maps)


def test_flush_encoded_size_split(tmp_path):
    rows = [save_crop(tmp_path, str(i), np.random.default_rng(i).integers(0, 200, (40, 100), dtype=np.uint8)) for i in range(4)]
    one = build_montages(rows[:1], 10, tmp_path / "one", tmp_path / "one_maps", layout="flush")[0]
    maps = build_montages(rows, 10, tmp_path / "out", tmp_path / "maps", layout="flush", max_png_bytes=one["png_bytes"] + 1000)
    assert [m["actual_n"] for m in maps] == [1] * 4
    assert all(m["split_reasons"] == ["png_bytes", "png_bytes"] for m in maps)


def test_flush_never_uses_rule_even_with_default_true(tmp_path):
    rows = [save_crop(tmp_path, str(i), np.full((5, 10), 170 + i)) for i in range(2)]
    a = build_montages(rows, 10, tmp_path / "a", tmp_path / "a_maps", layout="flush")[0]
    b = build_montages(rows, 10, tmp_path / "b", tmp_path / "b_maps", layout="flush", grey_rule=False)[0]
    assert a["image_sha256"] == b["image_sha256"]


def test_adjacent_straddle_counts_merged_even_above_70_percent():
    mapping = dict(boxes=dict(a=dict(y0=0, y1=10), b=dict(y0=10, y1=20)))
    result = assign_lines([dict(text="α", bbox=[0, 2, 20, 11])], mapping)
    assert result["merged_box_count"] == 1
    assert all(c["merged"] and c["lost"] for c in result["crops"].values())
    assert result["lines"][0]["overlaps"]["a"] == pytest.approx(8 / 9)


@pytest.mark.parametrize("mode", ["RGBA", "P", "I"])
def test_unsupported_native_modes_fail_closed(tmp_path, mode):
    path = tmp_path / "bad.png"
    Image.new(mode, (10, 10)).save(path)
    with pytest.raises(ValueError, match="8-bit"):
        background_shade(path)
    with pytest.raises(ValueError, match="8-bit"):
        build_montages([dict(id="bad", straight_crop=str(path))], 10, tmp_path / "out", tmp_path / "maps", layout="flush")


@pytest.mark.parametrize("value", ["unknown", None, False])
def test_invalid_layout(tmp_path, value):
    with pytest.raises(ValueError, match="layout"):
        build_montages([], 10, tmp_path, tmp_path, layout=value)


@pytest.mark.parametrize("n", [True, 10.0, 0])
def test_invalid_group_size(n):
    with pytest.raises(ValueError, match="N must"):
        group_flush_crops([], n)


def test_group_empty_and_duplicate_ids(tmp_path):
    assert group_flush_crops([], 10) == []
    row = save_crop(tmp_path, "same", [[170]])
    with pytest.raises(ValueError, match="unique"):
        group_flush_crops([row, row], 10)

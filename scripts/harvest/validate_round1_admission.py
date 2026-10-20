#!/usr/bin/env python3
"""Offline full replay: gates, splits, O5, crop bytes, geometry and native pixels."""
from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import time
import unicodedata as ud

from PIL import Image

from greekocr.harvest.admission import (
    CLASSES, REASONS, admit, apply_holdout_labels, crop_geometry, has_spacing_mark,
    normalize_label, page_quality, select_holdout_books, spatial_neighbours,
)
from scripts.harvest.admit_round1 import OUT, REPO, read_jsonl, sha, write_json


def validate(repo: Path = REPO, output_dir: Path = OUT, *, check_pixels=True, emit=print) -> dict:
    started = time.monotonic()
    out = repo / output_dir
    receipt = json.loads((out / "admission_inventory.json").read_text())
    for kind in ("inputs", "sources", "outputs"):
        for path, expected in receipt[kind].items():
            assert sha(repo / path) == expected, ("hash mismatch", kind, path)
    input_paths = list(receipt["inputs"])
    records = read_jsonl(repo / input_paths[0])
    catalogue = {b["key"]: b for b in json.loads((repo / input_paths[2]).read_text())["books"]}
    admitted = read_jsonl(out / "admitted.jsonl")
    rejected = read_jsonl(out / "rejected.jsonl")
    summary = json.loads((out / "admission_summary.json").read_text())
    held = json.loads((out / "holdout_books.json").read_text())
    quality = page_quality(records)
    pages = defaultdict(list)
    before_o5, expected_rejected = [], []
    for r in records:
        pages[r["page_id"]].append(r)
        good, cls, reasons, label = admit(dict(r, bad_page=quality[r["page_id"]]["bad_page"]))
        if good:
            before_o5.append(dict(id=r["id"], book_key=r["book_key"], label=label,
                                  script_class=cls, docai_text=r["docai_text"]))
        else:
            expected_rejected.append(dict(id=r["id"], reasons=reasons, docai_text=r["docai_text"]))
    book_counts = Counter(r["book_key"] for r in before_o5)
    book_rows = {r["book_key"]: r for r in records}
    books = [dict(book_key=k, title=catalogue[k]["title"], year=r["year"], decade=r["decade"],
                  admitted_lines=book_counts[k]) for k, r in sorted(book_rows.items())]
    assert held == select_holdout_books(books, count=summary["holdout_policy"]["count"],
                                       dev_count=summary["holdout_policy"]["dev"])
    splits = {r["book_key"]: r["split"] for r in held}
    for row in before_o5:
        row["split"] = splits.get(row["book_key"], "train")
    expected_admitted, o5 = apply_holdout_labels(before_o5)
    expected_rejected.extend(o5)
    assert rejected == sorted(expected_rejected, key=lambda r: r["id"]), "rejection replay"
    assert [r["id"] for r in admitted] == [r["id"] for r in expected_admitted], "admission replay"
    admitted_map = {r["id"]: r for r in admitted}
    rejected_ids = {r["id"] for r in rejected}
    assert len(admitted_map) == len(admitted) and len(rejected_ids) == len(rejected)
    assert not set(admitted_map) & rejected_ids
    assert set(admitted_map) | rejected_ids == {r["id"] for r in records}
    for actual, expected in zip(admitted, expected_admitted):
        for field in ("label", "script_class", "split", "book_key"):
            assert actual[field] == expected[field], (actual["id"], field)
        assert ud.is_normalized("NFC", actual["label"])
        assert actual["label"] == normalize_label(actual["label"])
        assert actual["has_spacing_mark"] == has_spacing_mark(actual["label"])
        assert actual["source"] == "anemi_round1" and actual["licence"] == "anemi-research-internal"
    held_labels = {r["label"] for r in admitted if r["split"] in ("test", "dev")}
    assert not held_labels & {r["label"] for r in admitted if r["split"] == "train"}
    reasons = Counter(reason for r in rejected for reason in r["reasons"])
    assert summary["per_reason"] == {r: reasons[r] for r in REASONS}
    assert summary["per_class"] == {c: sum(r["script_class"] == c for r in admitted) for c in CLASSES}
    assert summary["per_split"] == {s: sum(r["split"] == s for r in admitted) for s in ("train", "dev", "test")}
    assert summary["per_class_split"] == {c: {s: sum(r["script_class"] == c and r["split"] == s for r in admitted)
                                            for s in ("train", "dev", "test")} for c in CLASSES}
    assert summary["input_lines"] == len(records) and summary["admitted_before_o5"] == len(before_o5)
    assert summary["admitted"] == len(admitted) and summary["rejected"] == len(rejected)
    assert summary["label_in_holdout"] == len(o5)
    assert {p["page_id"] for p in summary["bad_pages"]} == {p for p, q in quality.items() if q["bad_page"]}
    crops = trimmed = 0
    image_receipts = {p["page_id"]: p for p in receipt["page_images"]}
    for i, (page_id, rows) in enumerate(sorted(pages.items()), 1):
        kept = [r for r in rows if r["id"] in admitted_map]
        if not kept:
            continue
        neighbours = spatial_neighbours(rows)
        assert sha(repo / rows[0]["image"]) == image_receipts[page_id]["sha256"]
        with Image.open(repo / rows[0]["image"]) as page:
            if check_pixels:
                page.load()
            for r in kept:
                row = admitted_map[r["id"]]
                for field in ("page_id", "year", "decade", "confidence", "bbox", "read_batch"):
                    assert row[field] == r[field], (row["id"], field)
                bounds, was_trimmed = crop_geometry(r["bbox"], *neighbours[r["id"]], page.size)
                assert row["crop_bbox"] == bounds and row["trimmed"] == was_trimmed
                crop_path = repo / row["crop_path"]
                assert crop_path.name == f"p{r['page']:06d}-l{r['line_number']:04d}.png"
                assert crop_path.parent.name == row["book_key"]
                assert sha(crop_path) == row["crop_sha256"], row["id"]
                with Image.open(crop_path) as crop:
                    assert crop.mode == "L" and crop.format == "PNG"
                    assert crop.size == (row["crop_width"], row["crop_height"])
                    assert crop.size == (bounds[2]-bounds[0], bounds[3]-bounds[1])
                    if check_pixels:
                        assert crop.tobytes() == page.crop(tuple(bounds)).tobytes(), ("native pixels", row["id"])
                crops += 1
                trimmed += was_trimmed
        if i % 200 == 0:
            emit(f"validated page {i}/{len(pages)}; {crops} crops; {time.monotonic()-started:.1f}s", flush=True)
    assert summary["crops"] == crops == len(admitted)
    assert summary["trimmed"] == trimmed
    assert summary["has_spacing_mark"] == sum(r["has_spacing_mark"] for r in admitted)
    for cls, sheet in summary["contact_sheets"].items():
        assert sha(repo / sheet["path"]) == sheet["sha256"]
        assert len(sheet["ids"]) == len(set(sheet["ids"])) == sheet["count"]
        assert sheet["count"] == min(60, summary["per_class"][cls])
        assert all(admitted_map[i]["script_class"] == cls for i in sheet["ids"])
        with Image.open(repo / sheet["path"]) as image:
            image.load()
            assert image.size == (sheet["width"], sheet["height"])
    result = dict(schema="t20-validation-1", passed=True, input_lines=len(records),
                  admitted=len(admitted), rejected=len(rejected), crops_checked=crops,
                  native_pixels_checked=crops if check_pixels else 0,
                  admitted_page_images=len(image_receipts), holdout_books=len(held),
                  label_in_holdout=len(o5), contact_sheets=len(summary["contact_sheets"]),
                  train_holdout_equal_labels=0, seconds=time.monotonic()-started)
    write_json(out / "admission_validation.json", result)
    return result


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))

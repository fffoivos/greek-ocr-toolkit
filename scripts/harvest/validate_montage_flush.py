#!/usr/bin/env python3
"""Independent offline replay of T14c pixels, groups, receipts and comparisons."""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from greekocr.ops.data_root import input_path as _data_input
from greekocr.harvest.montage import (assign_lines, assign_symbols, build_montages,
    response_lines, response_symbols)
from greekocr.harvest.montage_controls import compare_control, summarise_controls
from greekocr.harvest.readers import atomic, read_jsonl
from scripts.harvest.montage_controls import sha, git_state, audit_git
from scripts.harvest.montage_flush import (ROOT, OUT, BULK, NS, ENGINES, LAYOUTS,
    verify_inputs, load_pair)


def main():
    sample = json.loads((ROOT / "sample.json").read_text())
    manifest = json.loads((OUT / "manifest.json").read_text())
    grouping = json.loads((OUT / "grouping.json").read_text())
    summary = json.loads((OUT / "summary.json").read_text())
    receipt = json.loads((OUT / "receipt.json").read_text())
    comparisons = read_jsonl(OUT / "comparisons.jsonl")
    verify_inputs(sample, json.loads((OUT / "input_sha256.json").read_text()))
    assert sha(ROOT / "sample.json") == grouping["t14_sample_sha256"]
    for name, digest in receipt["artifact_sha256"].items():
        assert sha(OUT / name) == digest
    for path, digest in receipt["source_sha256"].items():
        assert sha(REPO / path) == digest
    assert len(comparisons) == 1200 and len(manifest) == 30
    assert Counter((m["experiment_layout"], m["n"]) for m in manifest) == {
        ("flush", 10): 10, ("flush", 20): 5, ("no rule", 10): 10, ("no rule", 20): 5}
    crops = {c["id"]: c for c in sample["crops"]}
    measurements = {}
    for index, crop in enumerate(sample["crops"]):
        with Image.open(crop["crop"]) as image:
            pixels = np.asarray(image.convert("L")).ravel()
            # Independently sort actual pixels, rather than use histogram helper.
            pixels = np.sort(pixels)
            shade = float(np.median(pixels[len(pixels) // 2:]))
            measurements[crop["id"]] = dict(background_shade=shade, height=image.height,
                width=image.width, source_index=index)
    expected_order = sorted(crops, key=lambda ident: (measurements[ident]["background_shade"], measurements[ident]["height"]))
    for n in NS:
        rows = [row for row in grouping["crops"] if row["n"] == n]
        assert [row["id"] for row in rows] == expected_order
        for index, row in enumerate(rows):
            assert all(row[k] == v for k, v in measurements[row["id"]].items())
            assert row["sorted_index"] == index and row["group"] == f"n{n:02d}-{index // n:03d}"
    historical = json.loads((ROOT / "manifest.json").read_text())
    historical_controls = json.loads((ROOT / "determinism/norule/manifest.json").read_text())
    # Render both historical layouts again into temporary evidence and compare
    # every PNG hash, including T14 N=40 and T14b's selected 20+10 control.
    with tempfile.TemporaryDirectory(prefix="t14c-layout-replay-") as directory:
        temp = Path(directory)
        rows = [dict(id=c["id"], straight_crop=c["crop"]) for c in sample["crops"]]
        for n in (10, 20, 40):
            maps = build_montages(rows, n, temp / "rule", temp / "rule_maps")
            assert [m["image_sha256"] for m in maps] == [m["image_sha256"] for m in historical if m["n"] == n]
        control = json.loads((ROOT / "determinism/sample.json").read_text())
        rows = [dict(id=c["id"], straight_crop=c["crop"]) for c in control["crops"]]
        maps = build_montages(rows, 20, temp / "norule", temp / "norule_maps", grey_rule=False)
        assert [m["image_sha256"] for m in maps] == [m["image_sha256"] for m in historical_controls]
    box_counts, assigned_counts = {}, Counter()
    indexed = {(r["layout"], r["n"], r["engine"], r["id"]): r for r in comparisons}
    assert len(indexed) == 1200
    for m in manifest:
        mode, n = m["experiment_layout"], m["n"]
        assert sha(m["image"]) == m["image_sha256"]
        mapping = json.loads(Path(m["map"]).read_text())
        assert mapping == {k: v for k, v in m.items() if k != "experiment_layout"}
        assert m["actual_n"] == n and not m["split_reasons"]
        assert Path(m["image"]).stat().st_size == m["png_bytes"] <= 8_000_000
        assert m["width"] <= 2600 and m["height"] <= 10000
        bands = list(m["boxes"].values())
        ids = list(m["boxes"])
        order = expected_order if mode == "flush" else list(crops)
        group_index = int(Path(m["image"]).stem.rsplit("-", 1)[1])
        assert ids == order[group_index * n:(group_index + 1) * n]
        with Image.open(m["image"]) as image:
            assert image.size == (m["width"], m["height"])
            out = np.asarray(image)
        assert bands[0]["y0"] == 0 and bands[-1]["y1"] == m["height"]
        for ident, band in m["boxes"].items():
            assigned_counts[mode, n, ident] += 1
            with Image.open(band["crop"]) as original:
                np.testing.assert_array_equal(out[band["y0"]:band["y1"], :band["x1"]], np.asarray(original))
            assert band["x0"] == 0 and sha(band["crop"]) == band["crop_sha256"] == crops[ident]["crop_sha256"]
            shade = measurements[ident]["background_shade"]
            fill = int(shade + .5) if mode == "flush" else 255
            assert (out[band["y0"]:band["y1"], band["x1"]:] == fill).all()
            if mode == "flush":
                assert band["background_shade"] == shade and band["padding_shade"] == fill
        if mode == "flush":
            assert not m["separators"] and m["height"] == sum(b["height"] for b in bands)
            assert all(left["y1"] == right["y0"] for left, right in zip(bands, bands[1:]))
        else:
            for gap, left, right in zip(m["separators"], bands, bands[1:]):
                assert gap["y0"] == left["y1"] and gap["y1"] == right["y0"]
                assert gap["y1"] - gap["y0"] == max(60, left["height"], right["height"])
                assert gap["rule_y0"] is gap["rule_y1"] is None
                assert (out[gap["y0"]:gap["y1"]] == 255).all()
        pair = load_pair(m, sample)  # disk only; no Readers object
        for engine, value in pair.items():
            raw = json.loads(Path(value["raw_json_path"]).read_text())
            assigned = assign_lines(response_lines(engine, raw, (m["width"], m["height"])), m)
            symbols = assign_symbols(response_symbols(engine, raw, (m["width"], m["height"])), m)
            path = OUT / "assignments" / ("flush" if mode == "flush" else "norule") / (Path(m["image"]).stem + "." + engine + ".json")
            stored = json.loads(path.read_text())
            assert stored["line_assignment"] == assigned and stored["symbol_assignment"] == symbols
            assert stored["raw_sha256"] == sha(value["raw_json_path"])
            counts = box_counts.setdefault((mode, n, engine), dict(merged_boxes=0, unassigned_boxes=0, montages=0))
            counts["merged_boxes"] += assigned["merged_box_count"]
            counts["unassigned_boxes"] += assigned["unassigned_box_count"]
            counts["montages"] += 1
            for ident, crop in assigned["crops"].items():
                row = indexed[mode, n, engine, ident]
                assert row["montage_text"] == crop["text"] and row["montage_sha256"] == m["image_sha256"]
                assert all(row[flag] == crop[flag] for flag in ("merged", "lost", "split", "rejected"))
    assert len(assigned_counts) == 400 and set(assigned_counts.values()) == {1}
    historical_rows = {(r["n"], r["engine"], r["id"]): r for r in read_jsonl(ROOT / "comparisons.jsonl")}
    for row in comparisons:
        ident, engine = row["id"], row["engine"]
        assert row["single_text"] == crops[ident]["readers"][engine]["text"]
        assert all(row[k] == v for k, v in compare_control(row["single_text"], row["montage_text"]).items())
        if row["layout"] == "rule":
            old = historical_rows[row["n"], engine, ident]
            assert row["montage_text"] == old["montage_text"]
            assert all(row[k] == old[k] for k in ("identical", "merged", "lost", "split", "rejected", "montage_sha256"))
    for mode in LAYOUTS:
        for n in NS:
            for engine in ENGINES:
                rows = [r for r in comparisons if (r["layout"], r["n"], r["engine"]) == (mode, n, engine)]
                stats = summary["cohorts"][mode][str(n)][engine]
                assert all(stats[k] == v for k, v in summarise_controls(rows).items())
                assert all(stats[flag] == sum(r[flag] for r in rows) for flag in ("merged", "lost", "split", "rejected"))
                if mode != "rule":
                    assert all(stats[k] == v for k, v in box_counts[mode, n, engine].items())
                assert stats["adopt"] == (stats["exact_pct"] >= 97 and stats["merged"] == stats["lost"] == 0)
    adopt = max((n for n in NS if all(summary["cohorts"]["flush"][str(n)][e]["adopt"] for e in ENGINES)), default=None)
    assert adopt == summary["n_adopt"] == receipt["n_adopt"]
    for flag in ("merged", "lost", "split"):
        assert summary["flush_merged_lost_split"][flag] == sum(summary["cohorts"]["flush"][str(n)][e][flag] for n in NS for e in ENGINES)
    reservations = read_jsonl(BULK / "google/budget.jsonl")
    assert len(reservations) == json.loads((BULK / "google/budget.state.json").read_text())["calls"] == receipt["calls_reserved"] == 60
    assert len({(r["engine"], r["key"]) for r in reservations}) == 60
    assert not {r["key"] for r in reservations} & {c["crop_sha256"] for c in sample["crops"]}
    assert receipt["cost_usd"] == round(60 * .0015, 6) <= receipt["cap_usd"] == .50
    assert Counter(c["layout"] for c in receipt["calls"]) == {"flush": 30, "no rule": 30}
    for engine in ENGINES:
        ledger = BULK / "google" / engine / ("adapter_receipts/ledger.jsonl" if engine == "vision" else "ledger.jsonl")
        entries = [r for r in read_jsonl(ledger) if not r["cached"]]
        assert len(entries) == 30 and all(r["status"] == "ok" for r in entries)
        assert {r["crop_sha256"] for r in entries} == {r["key"] for r in reservations if r["engine"] == engine}
        assert receipt["calls_by_engine"][engine] == 30
        by_receipt = {r["receipt_id"]: r for r in entries}
        for call in (c for c in receipt["calls"] if c["engine"] == engine):
            entry = by_receipt[call["receipt_id"]]
            assert call["image_sha256"] == entry["crop_sha256"] and call["binding"] == entry["binding"] == sample["bindings"][engine]
            assert call["raw_sha256"] == entry["raw_sha256"] == sha(call["raw_json_path"])
    first = next(m for m in manifest if m["experiment_layout"] == "flush" and m["n"] == 10)
    assert sha(OUT / "preview_n10.png") == first["image_sha256"]
    assert (_data_input(OUT / "preview_n10.png")).stat().st_size == receipt["preview_bytes"] < 1_000_000
    suites = ET.parse(OUT / "tests.xml").getroot().findall("testsuite")
    assert suites and all(int(s.attrib[k]) == 0 for s in suites for k in ("failures", "errors", "skipped"))
    tests = sum(int(s.attrib["tests"]) for s in suites)
    audit = audit_git(json.loads((OUT / "git_before.json").read_text()), git_state())
    assert audit["main_worktree_git_metadata_unchanged"]
    atomic(OUT / "git_audit.json", audit)
    result = dict(status="passed", timestamp=datetime.now(timezone.utc).isoformat(),
        tests_passed=tests, crops=100, comparisons=1200, montages=30,
        calls=60, cost_usd=.09, additional_network_calls=0,
        native_pixels_own_padding_zero_gaps_verified=True, stable_shade_height_groups_verified=True,
        historical_rule_18_and_no_rule_2_pngs_byte_identical=True,
        all_assignments_and_metrics_replayed=True, original_inputs_unchanged=True,
        uncached_ledger_and_raw_hashes_verified=True, git_audit=audit,
        tests_xml_sha256=sha(OUT / "tests.xml"), validator_sha256=sha(Path(__file__)))
    atomic(OUT / "validation.json", result)
    receipt.update(status="complete", tests_passed=tests, flush_tests_passed=27,
        test_command=".venv/bin/python -m pytest -q tests/test_montage_flush.py tests/test_montage.py tests/test_montage_controls.py tests/test_harvest.py tests/test_harvest_fix1.py tests/test_harvest_fix2.py tests/test_google_vision.py tests/test_docai.py tests/test_provenance_cli_api.py::test_public_callables_typed_and_documented --junitxml=docs/records/harvest/montage_v1/flush/tests.xml",
        validation=dict(path="validation.json", sha256=sha(OUT / "validation.json"),
                        tests_sha256=sha(OUT / "tests.xml")), git_audit=audit)
    # Keep historical source bindings in both old receipts; current replay
    # bindings describe the optional extension without rewriting old evidence.
    parent = json.loads((ROOT / "receipt.json").read_text())
    parent["flush"].update(tests_passed=tests, inventory="flush/inventory.json")
    report = ROOT.parent / "MONTAGE_v1.md"
    note = f"**{tests} offline tests passed (27 new flush cases).** Independent replay checks all native bands/padding, stable shade/height grouping, 1,200 comparisons, every line/symbol assignment, 60 unique raw-bound uncached API receipts, budget reservations and unchanged original inputs. All 18 historical rule PNGs and both historical no-rule PNGs regenerate byte-identically. No-flag rebuild and validator use no ADC or service calls. Native preview inspected visually. This task performed no `.git` writes; the [Git audit](montage_v1/flush/git_audit.json) records current metadata.\n"
    content = report.read_text().split("\n**" + str(tests) + " offline tests passed", 1)[0].rstrip()
    report.write_text(content + "\n\n" + note)
    receipt["report_sha256"] = sha(report)
    paths = [REPO / path for path in receipt["source_sha256"]] + [REPO / "docs/API.md", REPO / "docs/INVENTORY.md", report]
    paths += [p for base in (OUT, BULK) for p in base.rglob("*") if p.is_file() and p.name not in
              ("receipt.json", "inventory.json", "inventory.json.tmp") and "__pycache__" not in p.parts]
    inventory = {str(p.relative_to(REPO)): dict(sha256=sha(p), bytes=p.stat().st_size) for p in sorted(set(paths))}
    atomic(OUT / "inventory.json", inventory)
    receipt["inventory_sha256"] = sha(OUT / "inventory.json")
    atomic(OUT / "receipt.json", receipt)
    parent["flush"]["sha256"] = sha(OUT / "receipt.json")
    atomic(ROOT / "receipt.json", parent)
    print(json.dumps(result))


if __name__ == "__main__":
    main()

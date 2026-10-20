#!/usr/bin/env python3
"""Replay all T14b evidence offline; no ADC, reader construction or network."""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from greekocr.harvest.core import list_return
from greekocr.harvest.montage import assign_lines, response_lines, response_symbols
from greekocr.harvest.montage_controls import compare_control, summarise_controls
from greekocr.harvest.readers import atomic, read_jsonl, response_pieces
from scripts.harvest.montage_controls import OUT, ROOT, ENGINES, sha, verify_inputs, git_state, audit_git


def main():
    receipt = json.loads((OUT / "receipt.json").read_text())
    sample = json.loads((OUT / "sample.json").read_text())
    summary = json.loads((OUT / "summary.json").read_text())
    singles = {r["id"]: r["readers"] for r in read_jsonl(OUT / "singles.jsonl")}
    old = {(r["id"], r["engine"]): r for r in read_jsonl(ROOT / "comparisons.jsonl") if r["n"] == 20}
    comparisons = read_jsonl(OUT / "comparisons.jsonl")
    manifest = json.loads((OUT / "norule/manifest.json").read_text())
    verify_inputs(sample)
    assert len(comparisons) == 300 and len(singles) == 30
    assert Counter(c["vision_t14_identical"] for c in sample["crops"]) == {True: 15, False: 15}
    for filename, key in (("sample.json", "sample_sha256"), ("norule/manifest.json", "manifest_sha256"),
                          ("comparisons.jsonl", "comparisons_sha256"), ("summary.json", "summary_sha256")):
        assert sha(OUT / filename) == receipt[key]
    for path, digest in receipt.get("replay_source_sha256", receipt["source_sha256"]).items():
        assert sha(REPO / path) == digest
    git_before = Path(receipt.get("replay_git_before_path", OUT / "git_before.json"))
    if "replay_git_before_sha256" in receipt:
        assert sha(git_before) == receipt["replay_git_before_sha256"]
    git_audit = audit_git(json.loads(git_before.read_text()), git_state())
    assert git_audit["main_worktree_git_metadata_unchanged"]
    atomic(Path(receipt.get("replay_git_audit_path", OUT / "git_audit.json")), git_audit)
    reservations = read_jsonl(OUT / "google/budget.jsonl")
    assert len(reservations) == receipt["calls_reserved"] == len(receipt["calls"]) == 64
    assert len({(r["engine"], r["key"]) for r in reservations}) == 64
    assert json.loads((OUT / "google/budget.state.json").read_text())["calls"] == 64
    assert receipt["cost_usd"] == round(64 * .0015, 6) <= receipt["cap_usd"] == .5
    assert Counter(c["kind"] for c in receipt["calls"]) == {"single": 60, "montage_no_rule": 4}
    rows = {r["id"]: r for r in read_jsonl(sample["records"]) if r["id"] in singles}
    for e in ENGINES:
        ledger_path = OUT / "google" / e / ("adapter_receipts/ledger.jsonl" if e == "vision" else "ledger.jsonl")
        ledger = [r for r in read_jsonl(ledger_path) if not r["cached"]]
        assert len(ledger) == 32 and all(r["status"] == "ok" for r in ledger)
        assert len({r["crop_sha256"] for r in ledger}) == 32
        assert {r["crop_sha256"] for r in ledger} == {r["key"] for r in reservations if r["engine"] == e}
        by_receipt = {r["receipt_id"]: r for r in ledger}
        for call in [c for c in receipt["calls"] if c["engine"] == e]:
            entry = by_receipt[call["receipt_id"]]
            assert sha(call["raw_json_path"]) == call["raw_sha256"] == entry["raw_sha256"]
            assert call["binding"] == entry["binding"] == sample["bindings"][e]
        for c in sample["crops"]:
            v = singles[c["id"]][e]
            assert v == json.loads((OUT / "singles" / (c["id"] + ".json")).read_text())[e]
            assert v["image_sha256"] == c["crop_sha256"]
            assert v["receipt_id"] != c["readers"][e]["receipt_id"]
            with Image.open(c["crop"]) as image:
                size = image.size
            raw = json.loads(Path(v["raw_json_path"]).read_text())
            pieces = response_pieces(e, raw, size)
            r = rows[c["id"]]
            context = dict(column_bands=r["gates"].get("column_bands"),
                           x_offset=(r.get("straighten") or {}).get("page_x_offset", r["bbox"][0]))
            for k, value in list_return(pieces, **context).items():
                assert v[k] == value
    norule, geometry = {c["id"]: {} for c in sample["crops"]}, {}
    assert [m["actual_n"] for m in manifest] == [20, 10]
    assert [ident for m in manifest for ident in m["boxes"]] == [c["id"] for c in sample["crops"]]
    for m in manifest:
        assert json.loads(Path(m["map"]).read_text()) == m
        assert sha(m["image"]) == m["image_sha256"]
        assert Path(m["image"]).stat().st_size == m["png_bytes"] <= 8_000_000
        assert m["width"] <= 2600 and m["height"] <= 10000
        with Image.open(m["image"]) as image:
            out = np.asarray(image)
            assert image.size == (m["width"], m["height"])
        bands = list(m["boxes"].values())
        for band in bands:
            with Image.open(band["crop"]) as crop:
                np.testing.assert_array_equal(out[band["y0"]:band["y1"], :band["x1"]], np.asarray(crop))
            assert (out[band["y0"]:band["y1"], band["x1"]:] == 255).all()
        for gap, left, right in zip(m["separators"], bands, bands[1:]):
            assert gap["y0"] == left["y1"] and gap["y1"] == right["y0"]
            assert gap["y1"] - gap["y0"] == max(60, left["height"], right["height"])
            assert gap["rule_y0"] is gap["rule_y1"] is None
            assert (out[gap["y0"]:gap["y1"]] == 255).all()
        for e in ENGINES:
            path = OUT / "norule/assignments" / (Path(m["image"]).stem + "." + e + ".json")
            stored = json.loads(path.read_text())
            assert sha(stored["raw_json_path"]) == stored["raw_sha256"]
            raw = json.loads(Path(stored["raw_json_path"]).read_text())
            assigned = assign_lines(response_lines(e, raw, (m["width"], m["height"])), m)
            assert all(stored[k] == v for k, v in assigned.items())
            for ident, crop in assigned["crops"].items():
                norule[ident][e] = crop
            if sample["artifact_id"] in m["boxes"]:
                geometry[e] = dict(no_rule_band=m["boxes"][sample["artifact_id"]],
                    no_rule_stars=[s for s in response_symbols(e, raw, (m["width"], m["height"])) if "*" in s["text"]])
    for r in comparisons:
        c = next(c for c in sample["crops"] if c["id"] == r["id"])
        e, ident = r["engine"], r["id"]
        reference = c["readers"][e]["text"] if r["reference"] == "cached" else singles[ident][e]["text"]
        prediction = {"single-vs-single": singles[ident][e]["text"],
                      "montage(rule)-vs-single": old[ident, e]["montage_text"],
                      "montage(no rule)-vs-single": norule[ident][e]["text"]}[r["mode"]]
        assert (reference, prediction) == (r["reference_text"], r["prediction_text"])
        assert all(r[k] == v for k, v in compare_control(reference, prediction).items())
    for mode, engines in summary["cohorts"].items():
        for e, refs in engines.items():
            for ref, stats in refs.items():
                group = [r for r in comparisons if (r["mode"], r["engine"], r["reference"]) == (mode, e, ref)]
                assert len(group) == 30
                assert all(stats[k] == v for k, v in summarise_controls(group).items())
                assert stats["by_stratum"] == {s: summarise_controls(r for r in group if r["stratum"] == s)
                                               for s in ("identical", "different")}
    assert summary["no_rule_assignment"] == {e: {f: sum(norule[c["id"]][e][f] for c in sample["crops"])
                                                 for f in ("merged", "lost", "split", "rejected")} for e in ENGINES}
    # Bind the old star to its actual symbol box, rather than assuming separator ink.
    for m in json.loads((ROOT / "manifest.json").read_text()):
        if m["n"] == 20 and sample["artifact_id"] in m["boxes"]:
            for e in ENGINES:
                a = json.loads((ROOT / "assignments" / (Path(m["image"]).stem + "." + e + ".assignment.json")).read_text())
                geometry[e].update(rule_band=m["boxes"][sample["artifact_id"]],
                    rule_stars=[s for s in a["symbol_assignment"]["crops"][sample["artifact_id"]] if "*" in s["text"]])
    atomic(OUT / "asterisk_geometry.json", geometry)
    suites = ET.parse(OUT / "tests.xml").getroot().findall("testsuite")
    assert all(int(s.attrib[k]) == 0 for s in suites for k in ("failures", "errors", "skipped"))
    tests = sum(int(s.attrib["tests"]) for s in suites)
    result = dict(status="passed", timestamp=datetime.now(timezone.utc).isoformat(), tests_passed=tests,
        comparisons=300, crops=30, montage_images=2, calls=64, additional_network_calls=0,
        fresh_api_ledger_verified=True, original_inputs_unchanged=True, git_audit=git_audit,
        native_pixels_and_white_gaps_verified=True, all_assignments_and_metrics_replayed=True,
        tests_xml_sha256=sha(OUT / "tests.xml"), validator_sha256=sha(Path(__file__)),
        asterisk_geometry_sha256=sha(OUT / "asterisk_geometry.json"))
    atomic(Path(receipt.get("replay_validation_path", OUT / "validation.json")), result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()

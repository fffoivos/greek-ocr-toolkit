#!/usr/bin/env python3
"""Offline verification of T14 custody, physical layout, assignments and metrics."""
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from scripts.harvest.montage_pilot import preflight, sha
from greekocr.harvest.montage import (assign_lines, assign_symbols, compare_nfd,
    response_lines, response_symbols, summarise)
from greekocr.harvest.readers import atomic, read_jsonl


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.cards, self.images, self.hrefs = [], [], [], []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "article":
            self.cards.append(attrs["id"])
        if tag == "img":
            self.images.append(attrs["src"])
        if tag == "a":
            self.hrefs.append(attrs["href"])


def main():
    evidence = REPO / "docs/harvest/montage_v1"
    receipt = json.loads((evidence / "receipt.json").read_text())
    frozen = json.loads((evidence / "sample.json").read_text())
    rows, singles, verified = preflight(Path(frozen["records"]), evidence)
    assert verified == frozen
    manifest = json.loads((evidence / "manifest.json").read_text())
    comparisons = read_jsonl(evidence / "comparisons.jsonl")
    summary = json.loads((evidence / "summary.json").read_text())
    assert len(rows) == 100 and len(comparisons) == 600
    assert Counter(r["tier"] for r in rows) == {"tier1": 40, "tier2": 40, "tier3": 20}
    for name, key in [("sample.json", "sample_sha256"), ("manifest.json", "manifest_sha256"),
                      ("comparisons.jsonl", "comparisons_sha256"), ("summary.json", "summary_sha256")]:
        assert sha(evidence / name) == receipt[key]
    for path, digest in receipt.get("replay_source_sha256", receipt["source_sha256"]).items():
        assert sha(REPO / path) == digest
    budget = read_jsonl(Path(receipt["bulk_root"]) / "google/budget.jsonl")
    assert len(budget) == receipt["calls_reserved"] == len(receipt["calls"])
    assert len({(r["engine"], r["key"]) for r in budget}) == len(budget)
    assert receipt["cost_usd"] == round(len(budget) * .0015, 6) <= 1
    assert receipt["new_single_crop_calls"] == 0 and receipt["cached_single_reads_reused"] == 200
    assert not {r["key"] for r in budget} & {r["crop_sha256"] for r in frozen["crops"]}
    assert receipt["unique_montage_images"] == len({m["image_sha256"] for m in manifest})
    assert len(receipt["evaluations"]) == len(manifest) * 2
    for engine in ("vision", "docai"):
        ledger_path = Path(receipt["bulk_root"]) / "google" / engine / ("adapter_receipts/ledger.jsonl" if engine == "vision" else "ledger.jsonl")
        ledger = [r for r in read_jsonl(ledger_path) if not r["cached"]]
        assert len(ledger) == receipt["calls_by_engine"][engine]
        assert all(r["status"] == "ok" for r in ledger)
        assert len({r["crop_sha256"] for r in ledger}) == len(ledger)
    assigned_counts = Counter()
    for m in manifest:
        assert sha(m["image"]) == m["image_sha256"]
        assert json.loads(Path(m["map"]).read_text()) == m
        assert Path(m["image"]).stat().st_size == m["png_bytes"] <= 8_000_000
        with Image.open(m["image"]) as im:
            out = np.asarray(im)
            assert im.size == (m["width"], m["height"])
        assert m["width"] <= 2600 and m["height"] <= 10000
        for ident, band in m["boxes"].items():
            original = np.asarray(Image.open(band["crop"]))
            np.testing.assert_array_equal(out[band["y0"]:band["y1"], band["x0"]:band["x1"]], original)
            assert (out[band["y0"]:band["y1"], band["x1"]:] == 255).all()
            assert sha(band["crop"]) == band["crop_sha256"]
            assigned_counts[(m["n"], ident)] += 1
        for gap in m["separators"]:
            assert (out[gap["rule_y0"]:gap["rule_y1"]] == 153).all()
            assert (out[gap["y0"]:gap["rule_y0"]] == 255).all()
            assert (out[gap["rule_y1"]:gap["y1"]] == 255).all()
        for engine in ("vision", "docai"):
            parsed = json.loads((Path(receipt["bulk_root"]) / "google/parsed" / engine / (m["image_sha256"] + ".json")).read_text())
            stored = json.loads((evidence / "assignments" / (Path(m["image"]).stem + "." + engine + ".assignment.json")).read_text())
            raw = json.loads(Path(parsed["raw_json_path"]).read_text())
            assert sha(parsed["raw_json_path"]) == stored["raw_sha256"]
            a = assign_lines(response_lines(engine, raw, (m["width"], m["height"])), m)
            symbols = assign_symbols(response_symbols(engine, raw, (m["width"], m["height"])), m)
            assert a == stored["line_assignment"] and symbols == stored["symbol_assignment"]
            for ident, crop in a["crops"].items():
                row = next(r for r in comparisons if (r["id"], r["n"], r["engine"]) == (ident, m["n"], engine))
                for key, value in compare_nfd(singles[ident][engine]["text"], crop["text"]).items():
                    assert row[key] == value
                for key, value in crop.items():
                    assert row["montage_text" if key == "text" else key] == value
                row["single_symbols"] = singles[ident][engine]["symbols"]
                row["montage_symbols"] = symbols["crops"][ident]
    assert len(assigned_counts) == 300 and set(assigned_counts.values()) == {1}
    for n in (10, 20, 40):
        for engine in ("vision", "docai"):
            s = summarise([r for r in comparisons if r["n"] == n and r["engine"] == engine], sum(m["n"] == n for m in manifest))
            assert all(summary["cohorts"][str(n)][engine][k] == v for k, v in s.items())
    recommended = max((n for n in (10, 20, 40) if all(summary["cohorts"][str(n)][e]["adopt"] for e in ("vision", "docai"))), default=None)
    assert summary["n_adopt"] == recommended
    gallery_path = evidence.parent / "montage_review.html"
    links = Links()
    links.feed(gallery_path.read_text())
    assert len(links.ids) == len(set(links.ids))
    assert Counter(links.cards) == Counter(r["id"] for r in rows)
    assert len(links.images) == 100
    for src in links.images:
        assert not src.startswith(("data:", "http:", "https:"))
        assert (gallery_path.parent / unquote(src)).is_file()
    for href in links.hrefs:
        if href.startswith(("http:", "https:")):
            continue
        assert (gallery_path.parent / unquote(href.partition("#")[0])).is_file()
    xml = ET.parse(evidence / "tests.xml")
    suites = xml.getroot().findall("testsuite")
    tests = sum(int(s.attrib["tests"]) for s in suites)
    assert all(int(s.attrib["failures"]) == int(s.attrib["errors"]) == int(s.attrib["skipped"]) == 0 for s in suites)
    validation = dict(status="passed", timestamp=datetime.now(timezone.utc).isoformat(),
        crops=100, comparisons=600, montages=len(manifest), unique_images=receipt["unique_montage_images"],
        calls=len(budget), cost_usd=receipt["cost_usd"], additional_network_calls=0,
        native_pixel_conservation=True, cache_inputs_unchanged=True, assignment_metric_recomputation=True,
        all_100_cards_images_links_valid=True, tests_passed=tests, tests_xml_sha256=sha(evidence / "tests.xml"),
        gallery_sha256=sha(gallery_path), validator_sha256=sha(Path(__file__)))
    atomic(evidence / "validation.json", validation)
    print(json.dumps(validation))


if __name__ == "__main__":
    main()

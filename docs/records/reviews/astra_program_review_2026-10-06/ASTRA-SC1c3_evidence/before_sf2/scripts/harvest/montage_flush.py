#!/usr/bin/env python3
"""T14c: frozen 100-line flush and expanded no-rule controls, USD 0.50 cap.

--prepare renders only; --run permits at-most-once missing montage reads.
Without flags, replay saved responses offline (no reader construction or ADC).
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from greekocr.harvest.montage import (assign_lines, assign_symbols, build_montages,
    group_flush_crops, response_lines, response_symbols)
from greekocr.harvest.montage_controls import compare_control, summarise_controls
from greekocr.harvest.readers import Readers, atomic, read_jsonl
from scripts.harvest.montage_controls import sha, frozen, git_state, audit_git, write_jsonl

ROOT = REPO / "docs/harvest/montage_v1"
OUT = ROOT / "flush"
BULK = REPO / "docs/harvest/harvest_big/montage_v1/t14c"
ENGINES = ("vision", "docai")
NS = (10, 20)
LAYOUTS = ("rule", "no rule", "flush")
SOURCE_PATHS = ("greekocr/harvest/montage.py", "greekocr/harvest/montage_controls.py",
    "scripts/harvest/montage_flush.py", "scripts/harvest/validate_montage_flush.py",
    "scripts/harvest/validate_montage_controls.py", "tests/test_montage_flush.py", "scripts/generate_api_docs.py")


def history_bindings():
    """Freeze historical evidence, including raw responses and single caches."""
    paths = [ROOT / name for name in ("sample.json", "manifest.json", "comparisons.jsonl", "summary.json")]
    paths += list((ROOT / "assignments").glob("*.json"))
    control = ROOT / "determinism"
    paths += [control / name for name in ("sample.json", "comparisons.jsonl", "summary.json",
              "singles.jsonl", "norule/manifest.json", "plan.json")]
    paths += list((control / "norule/assignments").glob("*.json"))
    for root in (ROOT, control):
        receipt = json.loads((root / "receipt.json").read_text())
        for call in receipt["calls"]:
            path = Path(call["raw_json_path"])
            if sha(path) != call["raw_sha256"]:
                raise ValueError("historical response changed")
            paths.append(path)
    return {str(path.resolve()): sha(path) for path in sorted(set(paths))}


def verify_inputs(sample, history):
    if sha(sample["records"]) != sample["records_sha256"]:
        raise ValueError("pilot records changed")
    for crop in sample["crops"]:
        if sha(crop["crop"]) != crop["crop_sha256"]:
            raise ValueError("native single crop changed")
        for engine in ENGINES:
            value = crop["readers"][engine]
            if sha(value["raw_json_path"]) != value["raw_sha256"]:
                raise ValueError("cached single response changed")
    for path, digest in history.items():
        if sha(path) != digest:
            raise ValueError("historical evidence changed: " + path)


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    if not (OUT / "git_before.json").exists():
        initial = Path("/tmp/t14c_git_before.json")
        atomic(OUT / "git_before.json", json.loads(initial.read_text()) if initial.exists() else git_state())
    sample = json.loads((ROOT / "sample.json").read_text())
    history = history_bindings()
    frozen(OUT / "input_sha256.json", history)
    verify_inputs(sample, history)
    rows = [dict(id=c["id"], straight_crop=c["crop"]) for c in sample["crops"]]
    if len(rows) != 100 or len({r["id"] for r in rows}) != 100:
        raise ValueError("T14 requires exactly 100 unique frozen crops")
    grouping, manifest = [], []
    for n in NS:
        groups = group_flush_crops(rows, n)
        ordered = [row for group in groups for row in group]
        grouping += [dict(row, n=n) for row in ordered]
        for mode, records, options in (("flush", ordered, dict(layout="flush")),
                                      ("no rule", rows, dict(grey_rule=False))):
            key = "flush" if mode == "flush" else "norule"
            maps = build_montages(records, n, BULK / key / "images", OUT / "maps" / key, **options)
            if [m["actual_n"] for m in maps] != [n] * (100 // n) or any(m["split_reasons"] for m in maps):
                raise ValueError("size split would change the fixed 60-call plan")
            manifest += [dict(m, experiment_layout=mode) for m in maps]
    single_shas = {crop["crop_sha256"] for crop in sample["crops"]}
    if any(m["image_sha256"] in single_shas or m["actual_n"] < 2 for m in manifest):
        raise ValueError("refusing a new single-crop call")
    frozen(OUT / "manifest.json", manifest)
    frozen(OUT / "grouping.json", dict(schema="greekocr-flush-grouping-1",
        t14_sample_sha256=sha(ROOT / "sample.json"), count=100,
        sort="stable (background_shade, height); input ties preserve frozen T14 order",
        shade="median of brightest ceil(50%) luminance pixels; halves round upward for padding",
        measured_255_policy="use measured 255 only for crops whose own median is 255; no white fallback",
        crops=grouping))
    calls = 2 * len({m["image_sha256"] for m in manifest})
    if calls != 60:
        raise ValueError("expected 30 flush + 30 expanded no-rule calls")
    frozen(OUT / "plan.json", dict(flush_calls=30, expanded_no_rule_calls=30,
        max_calls=60, max_cost_usd=.09, cap_usd=.50, single_crop_calls=0,
        no_rule_reason="T14b covered 30 selected lines at N=20 only; full 100-line N=10/20 controls are required",
        retry_policy="persistent reservation before invocation; no automatic retries",
        raw_response_root=str(BULK / "google")))
    preview = OUT / "preview_n10.png"
    first = next(m for m in manifest if m["experiment_layout"] == "flush" and m["n"] == 10)
    # A native copy: preview-only rescaling is unnecessary for this small PNG.
    if not preview.exists():
        shutil.copyfile(first["image"], preview)
    if sha(preview) != first["image_sha256"]:
        raise ValueError("preview differs from the first native flush montage")
    return sample, manifest, history


def load_pair(mapping, sample, readers=None):
    key = mapping["image_sha256"]
    if sha(mapping["image"]) != key:
        raise ValueError("montage changed before read")
    pair = readers.pair(mapping["image"]) if readers is not None else {
        e: json.loads((BULK / "google/parsed" / e / (key + ".json")).read_text()) for e in ENGINES}
    for engine, value in pair.items():
        if value["status"] != "ok" or value["image_sha256"] != key or value["binding"] != sample["bindings"][engine]:
            raise RuntimeError("failed/mismatched reserved attempt; no retry: " + engine + " " + value.get("error_class", ""))
        ledger = BULK / "google" / engine / ("adapter_receipts/ledger.jsonl" if engine == "vision" else "ledger.jsonl")
        entries = [r for r in read_jsonl(ledger) if r["receipt_id"] == value["receipt_id"] and not r["cached"]]
        if len(entries) != 1 or entries[0]["status"] != "ok" or entries[0]["crop_sha256"] != key:
            raise ValueError("missing unique uncached API ledger entry")
        if sha(value["raw_json_path"]) != entries[0]["raw_sha256"] or entries[0]["binding"] != sample["bindings"][engine]:
            raise ValueError("raw hash/binding mismatch")
    return pair


def cohort_summary(comparisons, box_counts):
    summary = dict(schema="greekocr-montage-flush-summary-1", cohorts={})
    for mode in LAYOUTS:
        summary["cohorts"][mode] = {}
        for n in NS:
            summary["cohorts"][mode][str(n)] = {}
            for engine in ENGINES:
                rows = [r for r in comparisons if (r["layout"], r["n"], r["engine"]) == (mode, n, engine)]
                if len(rows) != 100 or len({r["id"] for r in rows}) != 100:
                    raise ValueError("incomplete 100-line cohort")
                stats = summarise_controls(rows)
                stats.update({flag: sum(r[flag] for r in rows) for flag in ("merged", "lost", "split", "rejected")})
                stats.update(box_counts[mode, n, engine])
                stats["adopt"] = stats["exact_pct"] >= 97 and stats["merged"] == stats["lost"] == 0
                summary["cohorts"][mode][str(n)][engine] = stats
    summary["n_adopt"] = max((n for n in NS if all(summary["cohorts"]["flush"][str(n)][e]["adopt"] for e in ENGINES)), default=None)
    summary["flush_merged_lost_split"] = {flag: sum(summary["cohorts"]["flush"][str(n)][e][flag] for n in NS for e in ENGINES)
        for flag in ("merged", "lost", "split")}
    summary["flush_exact_delta_pp"] = {str(n): {e: {mode: summary["cohorts"]["flush"][str(n)][e]["exact_pct"] -
        summary["cohorts"][mode][str(n)][e]["exact_pct"] for mode in ("rule", "no rule")} for e in ENGINES} for n in NS}
    return summary


def report_addendum(summary, receipt):
    lines = ["## Flush layout", "", "13 October 2026. **Recommended flush N: " + str(summary["n_adopt"] or "none") + ".** Same frozen 100 T14 lines and cached single cleaned readings; exact NFD and the unchanged T14b letters+marks helper measure preservation, not accuracy.", "",
        "Flush uses native pixels, zero gaps, no rules and no outer padding. Left-aligned bands meet exactly; each band's right padding uses its own median of the brightest ceil(50%) pixels (RGB estimation uses L luminance only; pasted colors remain native). Half-integral medians round upward for 8-bit padding. **82/100 crops have a measured median of 255**: those retain their own white shade; there is no unconditional white fallback. The other shades range from 162 to 241. [Per-crop shades, heights, source/sorted indices and groups](montage_v1/flush/grouping.json).", "",
        "Sort stably by `(background shade, crop height)`, using frozen T14 order for ties, then take consecutive groups of 10 and 20. All batches are full; no size splits. Rule rows reuse the historical 100-line T14 reads. T14b's no-rule control covered only 30 selected lines at N=20, so **30 additional no-rule calls** expand that identical gap/no-rule renderer to the full 100 lines at N=10/20, in original T14 order. Historical T14b results remain above. The expanded rule/no-rule pair shares neighbors; flush changes neighbors as well as layout. This experiment therefore assesses the combined flush-and-grouping hypothesis and does not isolate the effect of gaps alone.", "",
        "| Layout | N | Reader | Exact NFD identity | Letters+marks identity | Merged crops | Lost crops | Split crops | Merged boxes | Unassigned boxes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for mode in LAYOUTS:
        for n in NS:
            for engine in ENGINES:
                s = summary["cohorts"][mode][str(n)][engine]
                lines.append(f"| {mode} | {n} | {engine} | {s['exact_pct']:.1f}% ({s['exact_count']}/100) | {s['letters_marks_pct']:.1f}% ({s['letters_marks_count']}/100) | {s['merged']} | {s['lost']} | {s['split']} | {s['merged_boxes']} | {s['unassigned_boxes']} |")
    lines += ["", "All 100 crops remain in every denominator, including merged/lost crops. Assignment is unchanged: a reported box overlapping two adjacent bands marks every touched crop merged even if one overlap is ≥70%; it is never guessed into one band. Otherwise ≥70% of box height assigns it. Zero assigned lines is lost, ≥2 is split; flags are independent, so merged and lost can overlap. Side-by-side splits retain T14 cleanup; stacked splits retain LF and rejection. Every raw-bound line/symbol and overlap is retained in the [assignment audits](montage_v1/flush/manifest.json) and [1,200 crop comparisons](montage_v1/flush/comparisons.jsonl).", "",
        "![First N=10 flush montage, native pixels](montage_v1/flush/preview_n10.png)", "",
        f"Preview is a byte-identical native copy of the first N=10 flush PNG ({receipt['preview_bytes']:,} bytes).", ""]
    for n in NS:
        a, b = (summary["cohorts"]["flush"][str(n)][e] for e in ENGINES)
        qualify = a["adopt"] and b["adopt"]
        lines.append(f"**N={n}: {'ADOPT' if qualify else 'do not adopt'}.** Flush reaches {a['exact_pct']:.1f}% exact identity for Vision and {b['exact_pct']:.1f}% for DocAI; merged/lost are {a['merged']}/{a['lost']} and {b['merged']}/{b['lost']}, respectively. Adoption requires ≥97% exact identity and zero merged/lost in both readers.")
        for engine in ENGINES:
            delta = summary["flush_exact_delta_pp"][str(n)][engine]
            direction = "closer to singles than both gap layouts" if all(v > 0 for v in delta.values()) else "not closer to singles than both gap layouts"
            lines.append(f"{engine}: {direction}; exact changes vs rule/no rule are {delta['rule']:+.1f}/{delta['no rule']:+.1f} percentage points.")
        lines.append("")
    lines += ["The verdict applies only to these 100 lines, recorded bindings, grouping and layout. Cached single text is not ground truth; Vision remains unpinned. No production default is changed.", "",
        f"**{receipt['calls_reserved']} successful uncached calls: 30 flush + 30 expanded no-rule, USD {receipt['cost_usd']:.4f} conservative list-price estimate; cap USD 0.50.** Rate USD 0.0015 per image/page checked 13 October 2026 against [Vision pricing](https://cloud.google.com/vision/pricing) and [Document AI pricing](https://cloud.google.com/products/document-ai/pricing). Free allowances/discounts are not deducted; this is not an invoice. Persistent reservations precede every invocation, successful parsed/raw responses are reused and failed/interrupted attempts are never automatically retried. Zero single-crop calls; all 200 original single responses are reused and hash-verified.", "",
        "Bulk PNGs and Google raw/parsed responses, budgets and adapter ledgers are under ignored `docs/harvest/harvest_big/montage_v1/t14c/`. Maps, groups, assignments, comparisons, preview, test results and audit are under `montage_v1/flush/`. Original T14/T14b evidence and external pilot records/crops/single raw responses remain hash-verified. [Flush receipt](montage_v1/flush/receipt.json), [updated parent receipt](montage_v1/receipt.json), [offline replay validation](montage_v1/flush/validation.json), [test results](montage_v1/flush/tests.xml), [inventory](../INVENTORY.md#t14c-flush-montage-13-october-2026).", ""]
    path = ROOT.parent / "MONTAGE_v1.md"
    original = path.read_text().split("\n## Flush layout\n", 1)[0].rstrip()
    path.write_text(original + "\n\n" + "\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.prepare and args.run:
        parser.error("--prepare and --run are mutually exclusive")
    sample, manifest, history = prepare()
    if args.prepare:
        print((OUT / "plan.json").read_text()); return
    readers = None
    if args.run:
        readers = Readers(BULK / "google", cap=.50, project=sample["bindings"]["vision"]["user_project"],
                          processor=sample["bindings"]["docai"]["processor"])
        readers.budget.max_calls = 60
        if any(getattr(readers, e).binding() != sample["bindings"][e] for e in ENGINES):
            raise ValueError("reader binding differs from frozen singles")
    singles = {c["id"]: c["readers"] for c in sample["crops"]}
    comparisons, calls, box_counts = [], [], {}
    original_summary = json.loads((ROOT / "summary.json").read_text())
    for row in read_jsonl(ROOT / "comparisons.jsonl"):
        if row["n"] not in NS:
            continue
        comparisons.append(dict(id=row["id"], engine=row["engine"], n=row["n"], layout="rule",
            montage_sha256=row["montage_sha256"], single_text=singles[row["id"]][row["engine"]]["text"],
            montage_text=row["montage_text"], **{flag: row[flag] for flag in ("merged", "lost", "split", "rejected")},
            **compare_control(singles[row["id"]][row["engine"]]["text"], row["montage_text"])))
    for n in NS:
        for engine in ENGINES:
            s = original_summary["cohorts"][str(n)][engine]
            box_counts["rule", n, engine] = {k: s[k] for k in ("merged_boxes", "unassigned_boxes", "montages")}
    for index, m in enumerate(manifest, 1):
        pair = load_pair(m, sample, readers)
        mode, n = m["experiment_layout"], m["n"]
        for engine, value in pair.items():
            raw = json.loads(Path(value["raw_json_path"]).read_text())
            size = m["width"], m["height"]
            assigned = assign_lines(response_lines(engine, raw, size), m)
            symbols = assign_symbols(response_symbols(engine, raw, size), m)
            directory = "flush" if mode == "flush" else "norule"
            atomic(OUT / "assignments" / directory / (Path(m["image"]).stem + "." + engine + ".json"),
                dict(montage_sha256=m["image_sha256"], engine=engine, raw_json_path=value["raw_json_path"],
                     raw_sha256=sha(value["raw_json_path"]), line_assignment=assigned, symbol_assignment=symbols))
            counter = box_counts.setdefault((mode, n, engine), dict(merged_boxes=0, unassigned_boxes=0, montages=0))
            counter["merged_boxes"] += assigned["merged_box_count"]
            counter["unassigned_boxes"] += assigned["unassigned_box_count"]
            counter["montages"] += 1
            calls.append(dict(layout=mode, n=n, actual_n=m["actual_n"], **value, raw_sha256=sha(value["raw_json_path"])))
            for ident, crop in assigned["crops"].items():
                single = singles[ident][engine]
                comparisons.append(dict(id=ident, engine=engine, n=n, layout=mode,
                    montage_sha256=m["image_sha256"], single_text=single["text"], montage_text=crop["text"],
                    **{flag: crop[flag] for flag in ("merged", "lost", "split", "rejected")},
                    **compare_control(single["text"], crop["text"])))
        print(f"{index}/30 {mode} N={n} {Path(m['image']).name}: both ok", flush=True)
    summary = cohort_summary(comparisons, box_counts)
    write_jsonl(OUT / "comparisons.jsonl", comparisons)
    atomic(OUT / "summary.json", summary)
    verify_inputs(sample, history)
    reservations = read_jsonl(BULK / "google/budget.jsonl")
    if len(reservations) != 60 or len({(r["engine"], r["key"]) for r in reservations}) != 60:
        raise ValueError("expected exactly 60 distinct reserved successful calls")
    audit = audit_git(json.loads((OUT / "git_before.json").read_text()), git_state())
    if not audit["main_worktree_git_metadata_unchanged"]:
        raise ValueError("main-worktree Git metadata changed")
    atomic(OUT / "git_audit.json", audit)
    budget = json.loads((BULK / "google/budget.state.json").read_text())
    if budget["calls"] != len(reservations):
        raise ValueError("budget state and reservation ledger differ")
    receipt = dict(schema="greekocr-montage-flush-receipt-1", status="analysed",
        timestamp=datetime.now(timezone.utc).isoformat(), calls_reserved=60,
        calls_by_engine=dict(Counter(r["engine"] for r in reservations)),
        cost_usd=.09, cap_usd=.50, max_calls=60, flush_calls=30, expanded_no_rule_calls=30,
        new_single_crop_calls=0, cached_single_reads_reused=200, calls=calls,
        price_checked_date="2026-10-13", prices={e: .0015 for e in ENGINES},
        pricing_sources=["https://cloud.google.com/vision/pricing", "https://cloud.google.com/products/document-ai/pricing"],
        policy="all attempts reserved at list price; no free-tier deduction or automatic retries",
        reader_bindings=sample["bindings"], bulk_root=str(BULK), n_adopt=summary["n_adopt"],
        preview_bytes=(OUT / "preview_n10.png").stat().st_size,
        artifact_sha256={name: sha(OUT / name) for name in ("manifest.json", "grouping.json", "input_sha256.json",
                         "comparisons.jsonl", "summary.json", "plan.json", "preview_n10.png")},
        source_sha256={path: sha(REPO / path) for path in SOURCE_PATHS},
        single_inputs_revalidated_unchanged=True, historical_evidence_revalidated_unchanged=True,
        git_writes_by_this_task=0, git_audit=audit)
    atomic(OUT / "receipt.json", receipt)
    report_addendum(summary, receipt)
    parent = json.loads((ROOT / "receipt.json").read_text())
    parent["flush"] = dict(path="flush/receipt.json", sha256=sha(OUT / "receipt.json"),
        calls_reserved=60, cost_usd=.09, cap_usd=.50, n_adopt=summary["n_adopt"], validation="flush/validation.json")
    parent["cumulative_calls_reserved"] = parent["calls_reserved"] + parent["controls"]["calls_reserved"] + 60
    parent["cumulative_cost_usd"] = round(parent["cost_usd"] + parent["controls"]["cost_usd"] + .09, 6)
    parent["replay_source_sha256"] = {path: sha(REPO / path) for path in parent["source_sha256"]}
    parent["replay_source_note"] = "T14c adds optional flush/grouping; historical source hashes retained; both gap layouts replayed unchanged."
    atomic(ROOT / "receipt.json", parent)
    print(json.dumps({k: summary[k] for k in ("n_adopt", "flush_merged_lost_split", "flush_exact_delta_pp")}), flush=True)


if __name__ == "__main__":
    main()

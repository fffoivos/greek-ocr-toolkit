#!/usr/bin/env python3
"""T14b: --prepare is offline; --run permits exactly one fresh pair per image.

The deliberately separate google/ namespace bypasses all T14/pilot caches.
Subsequent invocations reuse only these control receipts, never repeat calls.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from greekocr.ops.data_root import input_path as _data_input
from greekocr.harvest.core import list_return
from greekocr.harvest.montage import assign_lines, build_montages, response_lines
from greekocr.harvest.montage_controls import compare_control, summarise_controls
from greekocr.harvest.readers import Readers, atomic, read_jsonl

ROOT = REPO / "docs/records/harvest/montage_v1"
OUT = ROOT / "determinism"
ENGINES = ("vision", "docai")
SEED = 1402


def sha(path):
    return hashlib.sha256(_data_input(Path(path)).read_bytes()).hexdigest()


def frozen(path, value):
    if path.exists() and json.loads(path.read_text()) != value:
        raise ValueError("frozen control input changed: " + str(path))
    atomic(path, value)


def git_state():
    # No git commands and no writes under .git. Metadata detects file writes,
    # creation/deletion, even when a file is rewritten with identical bytes.
    return {str(p.relative_to(REPO / ".git")): [p.stat().st_size, p.stat().st_mtime_ns]
            for p in sorted((REPO / ".git").rglob("*")) if p.is_file()}


def audit_git(before, after):
    """Distinguish main-worktree metadata from shared other-worktree activity."""
    changed = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
    def shared(p):
        return p.startswith(("objects/", "worktrees/")) or (
            p.startswith(("refs/heads/", "logs/refs/heads/")) and p not in
            ("refs/heads/main", "logs/refs/heads/main"))
    unexpected = [p for p in changed if not shared(p)]
    return dict(global_git_metadata_unchanged=not changed,
                main_worktree_git_metadata_unchanged=not unexpected,
                changed_paths=changed, shared_changed_paths=[p for p in changed if shared(p)],
                unexpected_changed_paths=unexpected)


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    before = OUT / "git_before.json"
    if not before.exists():
        atomic(before, git_state())
    sample = json.loads((ROOT / "sample.json").read_text())
    if sha(sample["records"]) != sample["records_sha256"]:
        raise ValueError("pilot records changed")
    old = {(r["id"], r["engine"]): r for r in read_jsonl(ROOT / "comparisons.jsonl") if r["n"] == 20}
    rng = random.Random(SEED)
    identical = sorted(r["id"] for r in old.values() if r["engine"] == "vision" and r["identical"])
    different = sorted(r["id"] for r in old.values() if r["engine"] == "vision" and not r["identical"])
    artifact = sorted(r["id"] for r in old.values() if r["engine"] == "vision" and "*" in r["montage_text"])
    if len(artifact) != 1 or artifact[0] not in different:
        raise ValueError("expected one differing asterisk artifact")
    chosen = set(rng.sample(identical, 15) + artifact + rng.sample([i for i in different if i not in artifact], 14))
    crops = [dict(c, vision_t14_identical=old[c["id"], "vision"]["identical"]) for c in sample["crops"] if c["id"] in chosen]
    if len(crops) != 30 or Counter(c["vision_t14_identical"] for c in crops) != {True: 15, False: 15}:
        raise ValueError("invalid 15/15 cohort")
    controls = dict(schema="greekocr-montage-controls-sample-1", seed=SEED, count=30,
        selection="sort IDs; seeded 15 identical + artifact crop + seeded 14 differing; preserve T14 order",
        stratum_population=dict(identical=len(identical), different=len(different)),
        strata=dict(identical=15, different=15), artifact_id=artifact[0],
        t14_sample_sha256=sha(ROOT / "sample.json"), t14_comparisons_sha256=sha(ROOT / "comparisons.jsonl"),
        records=sample["records"], records_sha256=sample["records_sha256"], bindings=sample["bindings"], crops=crops)
    frozen(OUT / "sample.json", controls)
    verify_inputs(controls)
    records = {r["id"]: r for r in read_jsonl(sample["records"]) if r["id"] in chosen}
    rows = [dict(records[c["id"]], straight_crop=c["crop"]) for c in crops]
    if len({c["crop_sha256"] for c in crops}) != 30:
        raise ValueError("duplicate image would invalidate 60-call control")
    manifest = build_montages(rows, 20, OUT / "norule/images", OUT / "norule/maps", grey_rule=False)
    if [m["actual_n"] for m in manifest] != [20, 10]:
        raise ValueError("size splits would exceed the four montage calls")
    frozen(OUT / "norule/manifest.json", manifest)
    plan = dict(single_calls=60, montage_calls=4, max_calls=64, cost_usd=.096, cap_usd=.50,
                cache_bypass="isolated determinism/google namespace; unchanged image bytes; same reader bindings",
                retry_policy="no automatic retries; persistent budget reservation before invocation")
    frozen(OUT / "plan.json", plan)
    return controls, rows, old, manifest


def verify_inputs(sample):
    if sha(sample["records"]) != sample["records_sha256"]:
        raise ValueError("pilot records changed")
    for c in sample["crops"]:
        if sha(c["crop"]) != c["crop_sha256"]:
            raise ValueError("native crop changed")
        for e in ENGINES:
            v = c["readers"][e]
            if sha(v["raw_json_path"]) != v["raw_sha256"]:
                raise ValueError("cached single response changed")
    for name in ("sample", "comparisons"):
        suffix = "json" if name == "sample" else "jsonl"
        if sha(ROOT / (name + "." + suffix)) != sample["t14_" + name + "_sha256"]:
            raise ValueError("T14 evidence changed")


def load_pair(readers, image, live):
    key = sha(image)
    if live:
        pair = readers.pair(image)
    else:
        pair = {e: json.loads((readers.root / "parsed" / e / (key + ".json")).read_text()) for e in ENGINES}
    for e, v in pair.items():
        if v["status"] != "ok" or v["image_sha256"] != key or v["binding"] != getattr(readers, e).binding():
            raise RuntimeError("failed or mismatched reserved attempt; no automatic retry: " + e)
        ledger_path = readers.vision.ledger_path if e == "vision" else readers.docai.ledger_path
        entries = [r for r in read_jsonl(ledger_path) if r["receipt_id"] == v["receipt_id"] and not r["cached"]]
        if len(entries) != 1 or entries[0]["status"] != "ok" or sha(v["raw_json_path"]) != entries[0]["raw_sha256"]:
            raise ValueError("control is not backed by exactly one new hash-bound API call")
    return pair


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False, allow_nan=False) + "\n" for r in rows))


def analyse(sample, singles, old, norule, assignments):
    comparisons = []
    for c in sample["crops"]:
        ident = c["id"]
        for e in ENGINES:
            cached, fresh = c["readers"][e]["text"], singles[ident][e]["text"]
            pairs = [("single-vs-single", "cached", cached, fresh),
                     ("montage(rule)-vs-single", "cached", cached, old[ident, e]["montage_text"]),
                     ("montage(rule)-vs-single", "new", fresh, old[ident, e]["montage_text"]),
                     ("montage(no rule)-vs-single", "cached", cached, norule[ident][e]["text"]),
                     ("montage(no rule)-vs-single", "new", fresh, norule[ident][e]["text"])]
            for mode, reference, a, b in pairs:
                comparisons.append(dict(id=ident, engine=e, mode=mode, reference=reference,
                    stratum="identical" if c["vision_t14_identical"] else "different",
                    reference_text=a, prediction_text=b, **compare_control(a, b)))
    write_jsonl(OUT / "comparisons.jsonl", comparisons)
    summary = dict(schema="greekocr-montage-controls-summary-1", cohorts={})
    for mode in ("single-vs-single", "montage(rule)-vs-single", "montage(no rule)-vs-single"):
        summary["cohorts"][mode] = {}
        for e in ENGINES:
            summary["cohorts"][mode][e] = {}
            for ref in ("cached", "new"):
                group = [r for r in comparisons if (r["mode"], r["engine"], r["reference"]) == (mode, e, ref)]
                if group:
                    stats = summarise_controls(group)
                    stats["by_stratum"] = {s: summarise_controls(r for r in group if r["stratum"] == s)
                                           for s in ("identical", "different")}
                    summary["cohorts"][mode][e][ref] = stats
    summary["no_rule_assignment"] = {e: {flag: sum(norule[c["id"]][e][flag] for c in sample["crops"])
                                       for flag in ("merged", "lost", "split", "rejected")} for e in ENGINES}
    summary["asterisks"] = {e: dict(
        cached_single=sum(c["readers"][e]["text"].count("*") for c in sample["crops"]),
        new_single=sum(singles[c["id"]][e]["text"].count("*") for c in sample["crops"]),
        rule_assigned=sum(old[c["id"], e]["montage_text"].count("*") for c in sample["crops"]),
        no_rule_assigned=sum(norule[c["id"]][e]["text"].count("*") for c in sample["crops"]),
        no_rule_all_raw=sum(a["raw_text"].count("*") for a in assignments if a["engine"] == e)) for e in ENGINES}
    summary["artifact_id"] = sample["artifact_id"]
    summary["artifact_texts"] = {e: dict(cached=next(c for c in sample["crops"] if c["id"] == sample["artifact_id"])["readers"][e]["text"],
        new=singles[sample["artifact_id"]][e]["text"], rule=old[sample["artifact_id"], e]["montage_text"],
        no_rule=norule[sample["artifact_id"]][e]["text"]) for e in ENGINES}
    summary["equivalent_by_reader"] = {}
    for e in ENGINES:
        baseline = summary["cohorts"]["single-vs-single"][e]["cached"]
        summary["equivalent_by_reader"][e] = all(
            summary["cohorts"]["montage(no rule)-vs-single"][e][ref][metric + "_pct"] >= baseline[metric + "_pct"] - 3
            for ref in ("cached", "new") for metric in ("exact", "letters_marks")) and not any(
            summary["no_rule_assignment"][e][f] for f in ("merged", "lost"))
    summary["equivalent"] = all(summary["equivalent_by_reader"].values())
    summary["n_adopt"] = 20 if summary["equivalent"] else None
    summary["raw_single_control"] = {e: summarise_controls(compare_control(c["readers"][e]["raw_text"], singles[c["id"]][e]["raw_text"])
        for c in sample["crops"]) for e in ENGINES}
    atomic(OUT / "summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    if args.run and args.prepare:
        parser.error("--run and --prepare are mutually exclusive")
    sample, rows, old, manifest = prepare()
    if args.prepare:
        print((OUT / "plan.json").read_text()); return
    readers = Readers(OUT / "google", cap=.50, project=sample["bindings"]["vision"]["user_project"],
                      processor=sample["bindings"]["docai"]["processor"])
    readers.budget.max_calls = 64
    if any(getattr(readers, e).binding() != sample["bindings"][e] for e in ENGINES):
        raise ValueError("reader settings differ from T14")
    singles, audit_calls = {}, []
    for index, row in enumerate(rows, 1):
        pair = load_pair(readers, row["straight_crop"], args.run)
        context = dict(column_bands=row["gates"].get("column_bands"),
                       x_offset=(row.get("straighten") or {}).get("page_x_offset", row["bbox"][0]))
        singles[row["id"]] = {e: dict(v, **list_return(v["pieces"], **context)) for e, v in pair.items()}
        atomic(OUT / "singles" / (row["id"] + ".json"), singles[row["id"]])
        for e, v in pair.items():
            audit_calls.append(dict(kind="single", id=row["id"], **v, raw_sha256=sha(v["raw_json_path"])))
        print(f"single {index}/30: both ok", flush=True)
    write_jsonl(OUT / "singles.jsonl", [dict(id=i, readers=v) for i, v in singles.items()])
    norule, assignments = {r["id"]: {} for r in rows}, []
    for index, m in enumerate(manifest, 1):
        pair = load_pair(readers, m["image"], args.run)
        for e, v in pair.items():
            raw = json.loads(Path(v["raw_json_path"]).read_text())
            assigned = assign_lines(response_lines(e, raw, (m["width"], m["height"])), m)
            assignment = dict(engine=e, image_sha256=m["image_sha256"], raw_text=v["raw_text"],
                              raw_json_path=v["raw_json_path"], raw_sha256=sha(v["raw_json_path"]), **assigned)
            atomic(OUT / "norule/assignments" / (Path(m["image"]).stem + "." + e + ".json"), assignment)
            assignments.append(assignment)
            for ident, crop in assigned["crops"].items():
                norule[ident][e] = crop
            audit_calls.append(dict(kind="montage_no_rule", actual_n=m["actual_n"], **v,
                                    raw_sha256=sha(v["raw_json_path"])))
        print(f"no-rule montage {index}/2: both ok", flush=True)
    summary = analyse(sample, singles, old, norule, assignments)
    verify_inputs(sample)
    budget = readers.budget.receipt()
    if budget["calls_reserved"] != 64 or budget["calls_by_engine"] != {"vision": 32, "docai": 32}:
        raise ValueError("expected exactly 64 new calls")
    git_audit = audit_git(json.loads((OUT / "git_before.json").read_text()), git_state())
    atomic(OUT / "git_audit.json", git_audit)
    if not git_audit["main_worktree_git_metadata_unchanged"]:
        raise ValueError("main-worktree .git metadata changed during control")
    sources = ["greekocr/harvest/montage.py", "greekocr/harvest/montage_controls.py", "scripts/harvest/montage_controls.py"]
    receipt = dict(schema="greekocr-montage-controls-receipt-1", timestamp=datetime.now(timezone.utc).isoformat(),
        **budget, status="complete", single_calls=60, montage_calls=4, calls=audit_calls,
        sample_sha256=sha(OUT / "sample.json"), manifest_sha256=sha(OUT / "norule/manifest.json"),
        comparisons_sha256=sha(OUT / "comparisons.jsonl"), summary_sha256=sha(OUT / "summary.json"),
        source_sha256={s: sha(REPO / s) for s in sources}, reader_bindings=sample["bindings"],
        single_inputs_revalidated_unchanged=True, git_audit=git_audit,
        price_checked_date="2026-10-12", n_adopt=summary["n_adopt"],
        cache_bypass="fresh isolated response directory; adapter ledgers prove 64 uncached calls; one per image/engine",
        report="docs/records/harvest/MONTAGE_v1.md#controls")
    atomic(OUT / "receipt.json", receipt)
    parent = json.loads((ROOT / "receipt.json").read_text())
    parent["controls"] = dict(path="determinism/receipt.json", sha256=sha(OUT / "receipt.json"),
        calls_reserved=64, cost_usd=budget["cost_usd"], cap_usd=.50, n_adopt=summary["n_adopt"])
    parent["cumulative_calls_reserved"] = parent["calls_reserved"] + 64
    parent["cumulative_cost_usd"] = round(parent["cost_usd"] + budget["cost_usd"], 6)
    atomic(ROOT / "receipt.json", parent)
    print(json.dumps(dict(calls=64, cost_usd=budget["cost_usd"], equivalent=summary["equivalent"], n_adopt=summary["n_adopt"])))


if __name__ == "__main__":
    main()

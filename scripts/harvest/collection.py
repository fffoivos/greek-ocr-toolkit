"""Build T28 artifacts locally: python -m scripts.harvest.collection --help."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from greekocr.harvest.collection import (
    BRIEFS, CLASSES, FIELDS, MANIFEST_FIELDS, SEED, SPLITS, WAVES, cap_source,
    check_crops, check_duplicates, digest, global_holdout, importer_row, ledger_cost,
    mix_marginals, normalize_label, normalize_row, read_jsonl, read_wave,
    repair_splits, source_caps, tallies, trainer_manifest, write_json, write_jsonl,
)


def markdown_table(headers, rows):
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    return "\n".join(["| " + " | ".join(map(cell, headers)) + " |",
                      "| " + " | ".join("---" for _ in headers) + " |"] +
                     ["| " + " | ".join(map(cell, row)) + " |" for row in rows]) + "\n"


def class_table(counts):
    return markdown_table(["Class", "Train", "Dev", "Test", "Total"],
                          [[c, *[counts[c][s] for s in SPLITS], sum(counts[c].values())] for c in CLASSES])


def plan_targets(root):
    lines = (root / "docs/records/harvest/COLLECTION_PLAN_v1.md").read_text().splitlines()
    targets = {}
    for line in lines:
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        for title, cls in (("Polytonic", "greek_poly"), ("Modern Greek", "greek_mono"),
                           ("Greek with Latin", "greek_latin_cs"), ("Latin only", "latin"),
                           ("Cyrillic", "cyrillic")):
            if cells[0].startswith(title):
                targets[cls] = dict(title=cells[0], train=int(cells[1].replace(",", "")),
                                    holdout=int(cells[2].replace(",", "")))
    if len(targets) != 5:
        raise ValueError("cannot parse the five plan section-1 targets")
    return targets


def test_result(path):
    if path is None:
        return None
    tree = ET.parse(path)
    cases = tree.findall(".//testcase")
    if not cases or any(c.find(tag) is not None for c in cases for tag in ("failure", "error", "skipped")):
        raise ValueError("T28 tests have not all passed")
    return len(cases)


def page_counts(root, wave, summary):
    directory = root / "docs/records/harvest" / wave
    if not summary:
        return dict(rendered=0, accepted=0, read=0)
    if wave == "round1":
        return dict(rendered=summary["pages"], accepted=summary["pages"], read=summary["pages"])
    path = directory / "manifest.json"
    manifest = json.loads(path.read_text()) if path.exists() else []
    read = summary.get("pages_read", summary.get("pages", 0))
    plan_path = directory / "plan.json"
    plan = json.loads(plan_path.read_text()) if plan_path.exists() else []
    accepted = len(plan) if isinstance(plan, list) else len(plan.get("pages", []))
    return dict(rendered=len(manifest), accepted=accepted, read=read)


def reserved_wikisource(root, delivered):
    reserved = defaultdict(list)
    if not delivered:
        return {}
    for path in sorted((root / "docs/records/harvest/wikisource/transcriptions").glob("*.json")):
        obj = json.loads(path.read_text())
        for line in obj["lines"]:
            if line.get("usable") and line["text"].strip():
                reserved[normalize_label(line["text"])].append(f'human:{obj["page"]["id"]}:{line["index"]}')
    # Retain previously recorded exclusions even when their human line format differs.
    path = root / "docs/records/harvest/wikisource/prior_train_exclusions.jsonl"
    if path.exists():
        for row in read_jsonl(path):
            reserved[normalize_label(row["label"])].extend(row["matching_holdout_labels"])
    return dict(reserved)


def sheet_index(root):
    result = {}
    text = ["# Collection contact sheets and compiled images\n",
            "Absolute paths below can be pasted into Finder → Go → Go to Folder. "
            "These are existing wave images; the collection merge did not regenerate them. "
            "They retain the original split annotations, including the lexicon's former test assignment. "
            "Use collection/split_repairs.json and admitted_all.jsonl for final splits.\n"]
    for wave in WAVES:
        base = root / "docs/harvest/harvest_big" / wave
        sheets = sorted(p for p in (base / "admission_sheet").rglob("*")
                        if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))
        compiled_roots = sorted(p for p in base.iterdir() if p.is_dir() and "compiled" in p.name) if base.exists() else []
        image_folders = set()
        for directory in compiled_roots:
            for path in directory.rglob("*"):
                if path.is_file() and path.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                    image_folders.add(path.parent)
        result[wave] = dict(admission_sheets=[p.relative_to(root).as_posix() for p in sheets],
                            compiled_roots=[p.relative_to(root).as_posix() for p in compiled_roots],
                            compiled_image_folders=[p.relative_to(root).as_posix() for p in sorted(image_folders)])
        text.append(f"## {wave}\n")
        text.append(f"{len(sheets)} admission-sheet images; {len(image_folders)} folders with compiled images.\n")
        for kind, paths in (("Admission sheet", sheets), ("Compiled root", compiled_roots),
                            ("Compiled image folder", sorted(image_folders))):
            for path in paths:
                text.append(f"- {kind}: [{path.name}](<{path}>) — `{path}`")
        if not sheets:
            text.append("\nAdmission-sheet images not delivered.")
        if not image_folders:
            text.append("\nCompiled page images not delivered (a receipt-only folder is not an image delivery).")
        text.append("")
    return "\n".join(text), result


def git_snapshot(root):
    result = {}
    for path in sorted((root / ".git").rglob("*")):
        if path.is_file():
            stat = path.stat()
            result[path.relative_to(root).as_posix()] = dict(
                bytes=stat.st_size, mtime_ns=stat.st_mtime_ns,
                sha256=None if "objects" in path.relative_to(root / ".git").parts else digest(path))
    return result


def build_report(root, waves, rows, raw, repairs, rejected, validation, provenance, targets, tests, status):
    counts = tallies(rows)
    total = len(rows)
    money = sum(p["ledger_micro_usd"] for p in provenance.values()) / 1_000_000
    delivered = sum(w["status"] == "delivered" for w in waves.values())
    text = ["# Collection plan v1 — T28 close-out\n",
            f"Offline close-out, 15 October 2026. **{total:,} admitted lines** after page-split repair and "
            f"{len(rejected):,} global train exclusions. **{delivered}/8 input artifact deliveries**, "
            f"{sum(bool(w['rows']) for w in waves.values())}/8 with admitted crops. "
            f"Historical Google ledger reservations total **USD {money:.4f}**. "
            "No network or Google calls, training, or Git writes were made by T28.\n",
            "Wikisource delivered an empty admission inventory and a source-shortfall report, "
            "not scan/crop coverage or independent OCR accuracy measurements. Open Archives T24c "
            "supersedes the earlier blocked T24/T24b preflights. Source-cap violations below remain in "
            "the manifests as requested; closing this collection does not establish that the targets or mix were met.\n",
            "## Targets and gaps\n",
            "Targets come directly from [plan §1](../COLLECTION_PLAN_v1.md#1-targets-and-gaps). "
            "The plan gives a combined dev+test target, so a separate dev or test quota cannot be inferred. "
            "Gaps are max(target − have, 0); surpluses are not reassigned across classes.\n"]
    target_rows = []
    for cls, target in targets.items():
        n = counts[cls]
        target_rows.append([target["title"], target["train"], target["holdout"], *[n[s] for s in SPLITS],
                            max(0, target["train"] - n["train"]),
                            max(0, target["holdout"] - n["dev"] - n["test"])])
    deficits = (sum(r[-2] for r in target_rows), sum(r[-1] for r in target_rows))
    target_train = sum(t["train"] for t in targets.values())
    target_held = sum(t["holdout"] for t in targets.values())
    have_train = sum(n["train"] for n in counts.values())
    have_held = sum(n["dev"] + n["test"] for n in counts.values())
    target_rows.append(["Total (net count)", target_train, target_held,
                        *[sum(n[s] for n in counts.values()) for s in SPLITS],
                        max(0, target_train-have_train), max(0, target_held-have_held)])
    text.append(markdown_table(["Class", "Train target", "Dev+test target", "Have train", "Have dev", "Have test",
                                "Train gap", "Dev+test gap"], target_rows))
    text.append(f"Unmet class-specific quotas sum to {deficits[0]:,} train and {deficits[1]:,} dev+test lines; "
                "the net total gap is smaller because it includes surplus polytonic/other held-out rows.\n")
    scoped = tallies([r for r in rows if r["script_class"] == "greek_poly" and r["year"] is not None
                      and 1850 <= r["year"] <= 1935])["greek_poly"]
    text.append("The table counts script classes across all recorded years. The plan's polytonic target specifically "
                "names 1850–1935; later parliamentary polytonic is useful but outside that date range. "
                f"Within 1850–1935 the polytonic counts are **{scoped['train']:,} train / {scoped['dev']:,} dev / "
                f"{scoped['test']:,} test**, leaving a scoped train gap of {max(0, targets['greek_poly']['train']-scoped['train']):,} "
                f"and combined hold-out gap of {max(0, targets['greek_poly']['holdout']-scoped['dev']-scoped['test']):,}. "
                "Modern-class counts follow the supplied tags; metadata OCR routing is not physical proof of a scanned page. "
                "Furniture has no admitted rows or §1 line quota.\n")
    text.append("## Pages, cost and delivery\n")
    delivery_rows = []
    for index, wave in enumerate(WAVES):
        p = provenance[wave]
        delivery_rows.append([f"{index}: {wave}", waves[wave]["status"],
                              f"{p['pages']['rendered']} / {p['pages']['accepted']} / {p['pages']['read']}",
                              p["lines"]["input"], p["lines"]["wave_admitted"], p["lines"]["collection_admitted"],
                              f"{p['ledger_usd']:.4f}"])
    text.append(markdown_table(["Wave", "Artifact delivery", "Rendered / accepted / read pages", "Provider lines",
                                "Wave admitted", "Collection admitted", "Ledger USD"], delivery_rows))
    text.append(f"Total read pages: {sum(p['pages']['read'] for p in provenance.values()):,}; "
                f"total ledger USD: **{money:.4f}** ({money:.2f} rounded). "
                "Round 1's 1,532 pages are reused, with zero new T20/T28 reads. Its historical ledgers cost "
                f"USD {provenance['round1']['ledger_usd']:.4f}: 1,532 DocAI calls plus 343 Vision pilot calls. "
                "These sunk charges are included once, even though the plan lists wave 0 incremental spend as zero. "
                "The total is the sum of integer micro-USD budget reservations, including failed attempts, without "
                "free-tier deductions; it is not an invoice. Adapter receipt ledgers corroborate processor IDs and "
                "are not charged again. Full ledger paths, hashes and per-engine totals are in [data_provenance.json](data_provenance.json).\n")
    text.append("## Missing deliveries and bounded shortfalls\n")
    for wave in WAVES:
        entry = waves[wave]
        last = next((line.strip() for report in entry["reports"].values()
                     for line in reversed(report.splitlines()) if line.strip()), "No wave report delivered.")
        last = re.sub(r"\]\((?!https?://|/|#)([^)]+)\)", rf"](../{wave}/\1)", last)
        if entry["status"] == "not delivered":
            text.append(f"- **{wave}: not delivered** — {entry['why']}. Last report line: {last}")
        else:
            text.append(f"- **{wave}** — wave report's last nonblank line: {last}")
    text.append(("\nAll eight wave summaries are present; no entire input folder is absent. " if delivered == 8 else
                 f"\n{8-delivered} wave input deliveries are absent as listed above. ") + "Output delivery is partial: "
                "wave 2 finished 37 accepted pages below 650; parliament lacks 32/104 volumes "
                "(1990–1993 and 1997–2000 absent from eligible catalogue searches), and read 690/705 accepted pages "
                "with 15 failed reads; Open Archives delivered 89/130 documents and 917/1,500 accepted pages "
                "after its bounded 173-candidate draw (84 dead/invalid PDFs); mixed delivered 782/980 authorized "
                "accepted pages, 198 short (the original plan proposed about 1,000). "
                "Wikisource delivered **0/400 scans**, 0 reads and 0 crops; 400 transcriptions / 3,357 source lines exist. "
                "Its recorded causes include imageinfo robots exclusions, unsupported thumbnail widths and HTTP 429; "
                "the bounded close-out stopped after one page exhausted its retry allowance. Two pages reached supported-width "
                "attempts; the remaining pages were not individually exhausted. "
                "These details come from the saved [Wikisource](../wikisource/READS.md), "
                "[Open Archives](../openarchives/READS.md), [mixed](../mixed/READS.md), "
                "[round 2](../round2/READS.md), and [parliament](../parliament/READS.md) reports, beyond their status tails.\n")
    text.append("## Split repair and global hold-out\n")
    text.append("Repairs affect collection outputs only. Eligible admitted pages are sorted by page ID, shuffled with "
                "Python Random(20261015), then assigned floor(0.70N) train, floor(0.10N) dev, remainder test. "
                "Every class and line on the same page follows that page. This explicitly replaces book-disjoint "
                "hold-out for the repaired source with page-disjoint hold-out; it is not evidence of generalization to a new book. "
                "All other source/book assignments are retained. [split_repairs.json](split_repairs.json) records every "
                "page assignment and changed ID, plus the zero-train-class scan.\n")
    for repair in repairs:
        text.append(f"### {repair['wave']} / {repair['source']}\n")
        text.append(f"{repair['pages']} pages; final page allocation {repair['page_splits']}. "
                    f"Reason: {repair['reason']}.\n")
        table = []
        for cls in CLASSES:
            if any(sum(repair[k][cls].values()) for k in ("before", "after_page_repair", "after_global")):
                table.append([cls, *[repair[k][cls][s] for k in ("before", "after_page_repair", "after_global") for s in SPLITS]])
        text.append(markdown_table(["Class", "Before train", "Before dev", "Before test", "Repair train", "Repair dev",
                                    "Repair test", "Final train", "Final dev", "Final test"], table))
    text.append(f"{max(0, len(repairs)-1)} additional wave/source repairs were needed for train=0 and test>0 "
                "in a populated class due to a single held-out source. "
                "Intentional Wikisource evaluation-only rows are never eligible for repair.\n")
    text.append(f"After repair, NFC/whitespace/DocAI-dot normalization is applied consistently with T20. "
                f"All dev/test labels across all waves reserve their text; Wikisource human labels do too. "
                f"The {validation['reserved_wikisource_labels']:,} distinct usable saved Wikisource transcription/audit labels "
                "also remain reserved despite missing crops, preserving the wave-7 contamination exclusions. "
                f"**{len(rejected):,} train rows** moved to [rejected_global.jsonl](rejected_global.jsonl) with reason "
                "`label_in_holdout`, full normalized rows and matching hold-out references. Dev/test rows remain. "
                "Zero train/held-out label collisions remain. This union is rebuilt from the wave admitted files, "
                "not the older cumulative train_pool overlays.\n")
    text.append(markdown_table(["Wave", "Global train exclusions"],
                               [[w, sum(r["wave"] == w for r in rejected)] for w in WAVES]))
    text.append("## Class × split tallies per wave\n")
    for wave in WAVES:
        text.append(f"### {wave}\n")
        text.append(class_table(tallies([r for r in rows if r["wave"] == wave])))
    text.append("## Wave rejection reasons\n")
    text.append("Original wave reasons are recomputed from rejected.jsonl and checked against each summary. "
                "Reason counts overlap; they need not sum to rejected rows. Global exclusions are additional.\n")
    reason_names = sorted({k for entry in waves.values() for k in entry.get("rejection_reasons", {})})
    text.append(markdown_table(["Reason", *WAVES], [[reason, *[waves[w].get("rejection_reasons", {}).get(reason, 0)
                                                              for w in WAVES]] for reason in reason_names]))
    text.append("## Source shares and 40% cap\n")
    text.append("Denominator: final train rows in the same class. Hellenic Parliament, each Anemi round, each repository, "
                "and each Internet Archive item are sources. Wave-4 `openarchives_X` and wave-5 "
                "`openarchives_mixed_X` are combined as the same repository. Vouli and modern parliamentary proceedings "
                "are combined as `hellenic_parliament`, since both use the Hellenic Parliament Library repository. "
                "Original source tags stay in rows/manifests. "
                "A share strictly above 40% is a violation; exactly 40% passes. No cap thinning was performed.\n")
    text.append(markdown_table(["Class", "Source", "Train", "Class train", "Share", ">40%"],
                               [[c["script_class"], c["source"], c["train"], c["class_train"], f"{100*c['share']:.2f}%",
                                 "VIOLATION" if c["over_40_percent"] else ""] for c in validation["source_caps"]]))
    text.append("The two Parliament wave tags separately contribute:\n")
    tag_counts = Counter((r["script_class"], r["source"]) for r in rows
                         if r["split"] == "train" and cap_source(r["source"]) == "hellenic_parliament")
    text.append(markdown_table(["Class", "Original source tag", "Train", "Class train", "Share"],
                               [[c, s, n, counts[c]["train"], f"{100*n/counts[c]['train']:.2f}%"]
                                for (c, s), n in sorted(tag_counts.items())]))
    text.append("## Realised mix marginals\n")
    text.append("The comparison baseline specified in T28 is modern 40 / polytonic 25 / Greek–Latin 15 / Latin 10 / "
                "Cyrillic 5 / furniture 5 percent. These are mix weights, distinct from §1 ceiling quotas. "
                "Both the total admitted pool and train-only mix are shown. No resampling was applied.\n")
    mix, train_mix = validation["mix_all"], validation["mix_train"]
    proposed = {"greek_mono": 40, "greek_poly": 25, "greek_latin_cs": 15, "latin": 10, "cyrillic": 5, "furniture": 5}
    text.append(markdown_table(["Class", "Proposed %", "Pool lines", "Pool %", "Difference pp", "Train %"],
                               [[c, proposed[c], mix["script_class"][c],
                                 f"{100*mix['script_class'][c]/total:.2f}" if total else "0.00",
                                 f"{100*mix['script_class'][c]/total-proposed[c]:+.2f}" if total else f"{-proposed[c]:+.2f}",
                                 f"{100*train_mix['script_class'][c]/train_mix['total']:.2f}" if train_mix["total"] else "0.00"]
                                for c in CLASSES]))
    text.append("Decades use recorded metadata year (unknown retained). Length is normalized label length in NFC "
                "Unicode code points, including spaces and punctuation; buckets below are T28 reporting buckets. "
                "Digit-bearing means ≥1 Unicode Nd character; all-caps means Python str.isupper() (at least one cased "
                "character, every cased character uppercase). The plan specifies no numeric decade, length, digit or "
                "all-caps marginal, so their target and gap are undefined rather than invented.\n")
    for key in ("decade", "length_buckets"):
        text.append(markdown_table([key, "Pool lines", "Pool %", "Train lines", "Target"],
                                   [[k, v, f"{100*v/total:.2f}" if total else "0.00", train_mix[key].get(k, 0), "unspecified"]
                                    for k, v in mix[key].items()]))
    text.append(markdown_table(["Marginal", "Pool lines", "Pool share", "Train share", "Target"],
                               [[key, mix[key], f"{100*mix[key+'_share']:.2f}%", f"{100*train_mix[key+'_share']:.2f}%", "unspecified"]
                                for key in ("digit_bearing", "all_caps")]))
    text.append("## Google versus human CER (wave 7)\n")
    cer = waves["wikisource"]["summary"].get("cer", {})
    text.append(markdown_table(["Language", "Google lines", "Aligned", "Human characters", "Edits", "CER"],
                               [[lang, v["lines"], v["aligned"], v["human_characters"], v["edit_distance"],
                                 "undefined (no scans/reads)" if v["cer"] is None else v["cer"]] for lang, v in cer.items()]))
    text.append("No measured CER is available, including breathings, iota subscript, perispomeni, grave or dialytika "
                "cohorts. Zero aligned lines is not zero error. For any future delivered rows, the wave's reported CER "
                "is conditional on 1:1 alignment, not an unbiased estimate over all scanned text.\n")
    text.append("## Schemas and trainer handoff\n")
    text.append("[admitted_all.jsonl](admitted_all.jsonl) contains one flat JSON object per row, with identical keys: "
                + ", ".join(f"`{key}`" for key in FIELDS) + ". `book_key` is the original document key; "
                "`page_id` retains page identity for the repair audit. `crop_path` is relative to this repository root; "
                "`crop_width`/`crop_height` are native pixels, using round-1 names. `bbox` is the supplied provider box "
                "in that wave's rendered-page frame, not the post-trim crop box. `human_label` and its transcription "
                "licence are null outside Wikisource; unknown year/decade/URL/attribution stay null. "
                "Round-1 source URLs are recovered from saved selection metadata, never fetched.\n")
    text.append("[manifest_train.json](manifest_train.json), [manifest_dev.json](manifest_dev.json), and "
                "[manifest_test.json](manifest_test.json) are JSON arrays with exactly these seven fields: "
                + ", ".join(f"`{key}`" for key in MANIFEST_FIELDS) + ". `crop` aliases `crop_path`; other names "
                "match admitted rows. Labels remain Google labels; human labels are retained separately in the union.\n")
    text.append("The checked local greek-page-ocr `factory/src/import_real.rs` reads JSONL and additionally requires "
                "`id` and `doc`, accepts `train`/`val`/`reserved`, and consumes `source_dataset`/`license` aliases. "
                "The seven-field JSON arrays alone are therefore insufficient for that CLI. Companion "
                "`import_real_train.jsonl`, `import_real_dev.jsonl`, `import_real_test.jsonl`, and the combined "
                "[import_real_all.jsonl](import_real_all.jsonl) supply those fields, preserving source, licence, "
                "URL and attribution. Mapping: train→train, dev→val, test→reserved. Labels are `silver` Google labels. "
                "For repaired sources only, importer `doc` is the namespaced page ID so the importer's document-split "
                "check enforces the intentional page boundary; otherwise it is namespaced book_key. Use `--crops` "
                "equal to this repo root. No import or training was launched. Example from greek-page-ocr:\n\n"
                "```sh\nlinefactory import-real \\\n"
                f"  --records {root}/docs/records/harvest/collection/import_real_all.jsonl \\\n"
                f"  --crops {root} \\\n"
                "  --out /path/to/new/collection-v1-import --partition collection-v1-t28\n```\n")
    text.append("[data_provenance.json](data_provenance.json) records each wave's brief, read batches, observed "
                "DocAI processor IDs, ledger USD, pages, input/admitted/remaining lines, and admission module SHA. "
                "A processor ID is null when there was no provider receipt. Anemi remains research/internal-only; "
                "per-repository licences remain recorded and unverified as in the wave inputs.\n")
    text.append("## Validation and owner review\n")
    text.append(f"Every one of the {len(raw):,} input admitted rows passed uniform-schema, unique ID/path and file-existence "
                "checks before exclusions. SHA-256, PNG integrity and recorded dimensions were checked for a deterministic "
                "2,000-row sample per nonempty wave (all rows for a wave smaller than 2,000); "
                f"{sum(v['sha256_and_dimensions_checked'] for v in validation['crop_checks'].values()):,} crops checked, "
                "zero failures. Sampling happens before global rejection, so all final splits and excluded rows are eligible. "
                "This is sampled integrity verification, not every-file hashing or visual transcription validation.\n")
    text.append(f"Offline tests: **{tests if tests is not None else 'pending'} passed**. "
                "[validation.json](validation.json) records counts, crop sample IDs, source caps and mix marginals. "
                "[tests.xml](tests.xml) contains test outcomes; [inventory.json](inventory.json) binds inputs, code and outputs. "
                "The recorded admission-module SHA matches the current T20 module. "
                "[git_audit.json](git_audit.json) compares Git file metadata/content fingerprints before and after; "
                "Git object payloads use size/mtime metadata rather than rehashing the whole object store.\n")
    text.append("Owner after-the-fact review starts at [SHEETS.md](../harvest_big/collection/SHEETS.md), with absolute "
                "Finder-ready sheet paths and compiled-image folders. Original wave sheets are unchanged and may show "
                "old splits. Prior physical crop/label counterexamples remain admitted under the original text policy; "
                "this merge provides integrity and leakage checks, not owner accuracy acceptance. Cyrillic transcription "
                "quality remains unvalidated by the owner and lacks the planned independent Wikisource CER.\n")
    text.append(status)
    return "\n".join(text) + "\n"


def run(root, tests_xml=None, git_before=None):
    root = root.resolve()
    out = root / "docs/records/harvest/collection"
    out.mkdir(parents=True, exist_ok=True)
    tests = test_result(tests_xml)
    # Bind every wave artifact consumed here, including untouched inputs and all human transcriptions.
    inputs = [root / "docs/records/harvest/COLLECTION_PLAN_v1.md"]
    names = ("admitted.jsonl", "rejected.jsonl", "admission_summary.json", "holdout_books.json", "READS.md",
             "ADMISSION.md", "selection.json", "manifest.json", "plan.json", "cost_receipt.json",
             "prior_train_exclusions.jsonl", "label_in_holdout.json", "admission_inventory.json")
    for wave in WAVES:
        directory = root / "docs/records/harvest" / wave
        inputs.extend(directory / n for n in names if (directory / n).is_file())
        inputs.extend((directory / "transcriptions").glob("*.json"))
        inputs.extend((root / "docs/harvest/harvest_big" / wave / "google").glob("budget*.jsonl"))
        path = root / "docs/harvest/harvest_big" / wave / "google/docai/ledger.jsonl"
        if path.exists():
            inputs.append(path)
    inputs = sorted(set(inputs))
    before = {p.relative_to(root).as_posix(): digest(p) for p in inputs}
    print("Reading wave inputs", flush=True)
    waves = {w: read_wave(root, w) for w in WAVES}
    urls = {}
    path = root / "docs/records/harvest/round1/selection.json"
    if path.exists():
        for book in json.loads(path.read_text())["books"]:
            urls[book["key"]] = "https://anemi.lib.uoc.gr" + book["book"]
    raw = [normalize_row(r, w, urls if w == "round1" else {}) for w in WAVES for r in waves[w]["rows"]]
    check_duplicates(raw)
    print(f"Checking existence of {len(raw):,} crops and sampling SHA/dimensions", flush=True)
    crop_checks = check_crops(root, raw)
    repaired, repairs, scan = repair_splits(raw, {w: waves[w]["holdouts"] for w in WAVES})
    reserved = reserved_wikisource(root, waves["wikisource"]["status"] == "delivered")
    rows, rejected = global_holdout(repaired, reserved)
    check_duplicates(rows)
    for repair in repairs:
        repair["after_global"] = tallies([r for r in rows if (r["wave"], r["source"]) == (repair["wave"], repair["source"])])
    write_json(out / "split_repairs.json", dict(seed=SEED, repairs=repairs, zero_train_class_scan=scan))
    held = {normalize_label(r["label"]) for r in rows if r["split"] != "train"} | set(reserved)
    collisions = sum(normalize_label(r["label"]) in held for r in rows if r["split"] == "train")
    assert collisions == 0 and len(rows) + len(rejected) == len(raw)
    write_jsonl(out / "admitted_all.jsonl", rows)
    write_jsonl(out / "rejected_global.jsonl", rejected)
    repaired_sources = {(r["wave"], r["source"]) for r in repairs}
    for split in SPLITS:
        group = [r for r in rows if r["split"] == split]
        # Compact arrays keep the seven-field manifests practical at this size.
        with (out / f"manifest_{split}.json").open("w") as stream:
            stream.write("[\n")
            for i, row in enumerate(group):
                stream.write((",\n" if i else "") + json.dumps(trainer_manifest(row), ensure_ascii=False))
            stream.write("\n]\n")
        write_jsonl(out / f"import_real_{split}.jsonl", (importer_row(r, repaired_sources) for r in group))
    write_jsonl(out / "import_real_all.jsonl", (importer_row(r, repaired_sources) for r in rows))
    print("Writing provenance and owner report", flush=True)
    module_sha = digest(root / "greekocr/harvest/admission.py")
    provenance = {}
    for i, wave in enumerate(WAVES):
        entry, summary = waves[wave], waves[wave]["summary"]
        recorded_sha = summary.get("admission_module_sha256")
        if wave == "round1" and (root / "docs/records/harvest/round1/admission_inventory.json").exists():
            recorded_sha = json.loads((root / "docs/records/harvest/round1/admission_inventory.json").read_text())["sources"].get("greekocr/harvest/admission.py")
        if recorded_sha and recorded_sha != module_sha:
            raise ValueError(f"{wave}: admission module changed")
        ledger = root / "docs/harvest/harvest_big" / wave / "google/docai/ledger.jsonl"
        processors = sorted({r["binding"]["processor"] for r in read_jsonl(ledger)}) if ledger.exists() else []
        provenance[wave] = dict(wave_number=i, status=entry["status"], delivery_detail=entry["why"],
                                brief="docs/records/briefs/" + BRIEFS[i],
                                read_batch=sorted({r["read_batch"] for r in entry["rows"] if r.get("read_batch")}),
                                docai_processor_id=processors[0] if len(processors) == 1 else processors or None,
                                pages=page_counts(root, wave, summary),
                                lines=dict(input=summary.get("input_lines", 0), wave_admitted=len(entry["rows"]),
                                           collection_admitted=sum(r["wave"] == wave for r in rows),
                                           global_rejected=sum(r["wave"] == wave for r in rejected)),
                                admission_module_sha256=module_sha, recorded_admission_module_sha256=recorded_sha,
                                source_cap_groups=sorted({cap_source(r["source"]) for r in entry["rows"]}),
                                **ledger_cost(root, wave))
    write_json(out / "data_provenance.json", provenance)
    text, sheets = sheet_index(root)
    sheets_path = root / "docs/harvest/harvest_big/collection/SHEETS.md"
    sheets_path.parent.mkdir(parents=True, exist_ok=True)
    sheets_path.write_text(text)
    validation = dict(schema="t28-validation-1", seed=SEED, input_admitted=len(raw), admitted=len(rows),
                      rejected_global=len(rejected), duplicate_ids=0, duplicate_paths=0, label_collisions=collisions,
                      reserved_wikisource_labels=len(reserved), crop_checks=crop_checks,
                      per_class_split=tallies(rows), per_wave_class_split={w: tallies([r for r in rows if r["wave"] == w]) for w in WAVES},
                      per_wave_input_class_split={w: tallies([r for r in raw if r["wave"] == w]) for w in WAVES},
                      source_caps=source_caps(rows), mix_all=mix_marginals(rows),
                      mix_train=mix_marginals([r for r in rows if r["split"] == "train"]),
                      sheets=sheets, input_files_unchanged=True, tests_passed=tests,
                      network_calls=0, google_calls=0, git_writes=0)
    write_json(out / "validation.json", validation)
    counts = Counter(r["split"] for r in rows)
    classes = Counter(r["script_class"] for r in rows)
    money = sum(p["ledger_micro_usd"] for p in provenance.values()) / 1_000_000
    delivered = sum(w["status"] == "delivered" for w in waves.values())
    status = (f"T28: {'done' if tests is not None else 'validation pending'} | waves: {delivered}/8 | "
              f"train: {counts['train']} | dev: {counts['dev']} | test: {counts['test']} | "
              f"poly: {classes['greek_poly']} | mono: {classes['greek_mono']} | cs: {classes['greek_latin_cs']} | "
              f"latin: {classes['latin']} | cyr: {classes['cyrillic']} | usd_total: {money:.2f} | tests: {tests or 0} passed")
    (out / "COLLECTION_REPORT.md").write_text(build_report(root, waves, rows, raw, repairs, rejected,
                                                          validation, provenance, plan_targets(root), tests, status))
    state_path = out / "EXECUTION_STATE.md"
    original = state_path.read_text().split("\n## Close-out", 1)[0].rstrip()
    state_path.write_text(original + "\n\n## Close-out\n\n" +
                          "T28 closes the delivered local collection after the final T24c and T27d reports. "
                          "Open Archives delivered 25,606 crops; the blocked Wave 4 entry above is historical. "
                          "Wikisource delivered its source-shortfall report and an empty admitted inventory: no scan images, "
                          "no crops and no measured CER. There are eight input deliveries, seven with crops.\n\n" +
                          f"Merged {len(raw):,} wave rows; repaired lexicon pages 70/10/20 with seed {SEED}; "
                          f"removed {len(rejected):,} train rows by global label hold-out. "
                          "Source-cap violations are reported and retained. Original wave files/crops remain unchanged. "
                          f"Offline tests: {tests if tests is not None else 'pending'} passed; no network, Google calls or Git writes.\n\n" +
                          "[Owner report](COLLECTION_REPORT.md) · [validation](validation.json) · [provenance](data_provenance.json) · "
                          "[inventory](INVENTORY.md) · [Finder image index](../harvest_big/collection/SHEETS.md)\n\n" + status + "\n")
    after = {p.relative_to(root).as_posix(): digest(p) for p in inputs}
    if before != after:
        raise ValueError("wave inputs changed during collection build")
    current_git = git_snapshot(root)
    baseline_git = json.loads(git_before.read_text()) if git_before else current_git
    changed = sorted(k for k in baseline_git.keys() | current_git.keys() if baseline_git.get(k) != current_git.get(k))
    if changed:
        raise ValueError(f"Git metadata changed: {changed}")
    write_json(out / "git_audit.json", dict(unchanged=True, baseline_supplied=git_before is not None,
                                           files_checked=len(current_git), changed=changed,
                                           before=baseline_git, after=current_git))
    # Hash outputs, code and tests, excluding the inventory pair to avoid self-reference.
    output_paths = sorted(p for p in out.iterdir() if p.is_file() and p.name not in ("inventory.json", "INVENTORY.md"))
    output_paths.append(sheets_path)
    code_paths = [root / p for p in ("greekocr/harvest/collection.py", "scripts/harvest/collection.py",
                                    "tests/test_collection.py", "tests/test_collection_outputs.py", "docs/INVENTORY.md")]
    output_meta = {p.relative_to(root).as_posix(): dict(bytes=p.stat().st_size, sha256=digest(p))
                   for p in output_paths + code_paths if p.exists()}
    inventory_text = "# T28 inventory\n\n" + markdown_table(["Artifact / code", "Bytes", "SHA-256"],
                                                            [[f"[{p}](<{root / p}>)", v["bytes"], v["sha256"]]
                                                             for p, v in sorted(output_meta.items())])
    inventory_text += (f"\n{len(before)} frozen input artifacts are hashed in [inventory.json](inventory.json). "
                       "All were rehashed after the build and are unchanged. Crop files are referenced by admitted_all.jsonl; "
                       "existence is checked exhaustively and SHA/dimensions by the recorded deterministic sample. "
                       "The two inventory files exclude themselves from output hashes to avoid recursive hashes.\n")
    (out / "INVENTORY.md").write_text(inventory_text)
    write_json(out / "inventory.json", dict(schema="t28-inventory-1", inputs=before, outputs_and_code=output_meta,
                                             input_files_unchanged=True, excluded_self=["inventory.json", "INVENTORY.md"],
                                             command=".venv/bin/python -m scripts.harvest.collection --tests-xml docs/records/harvest/collection/tests.xml --git-before /private/tmp/t28_git_before.json",
                                             network_calls=0, google_calls=0, git_writes=0))
    print(status, flush=True)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--tests-xml", type=Path)
    parser.add_argument("--git-before", type=Path)
    args = parser.parse_args()
    run(args.root, args.tests_xml, args.git_before)


if __name__ == "__main__":
    main()

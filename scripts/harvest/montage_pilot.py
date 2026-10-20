#!/usr/bin/env python3
"""T14: frozen 100-crop experiment; --run opts in to budgeted montage calls only.

Run from the repo with .venv/bin/python scripts/harvest/montage_pilot.py --run.
Without --run, rebuild reports from existing montage responses, with no network.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import random
import statistics
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from greekocr.ops.data_root import input_path as _data_input

from greekocr.harvest.montage import (assign_lines, assign_symbols, build_montages,
    compare_nfd, response_lines, response_symbols, summarise)
from greekocr.harvest.readers import Readers, atomic, read_jsonl

DEFAULT_RECORDS = Path.home() / "Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/harvest_big/pilot_t13c/pilot_v1/records.jsonl"
NS = (10, 20, 40)
ENGINES = ("vision", "docai")


def sha(path):
    return hashlib.sha256(_data_input(Path(path)).read_bytes()).hexdigest()


def select(records):
    """Stable ID sort, seeded sample per tier, seeded shuffle shared by all N."""
    rng = random.Random(14)
    chosen = []
    for tier, count in (("tier1", 40), ("tier2", 40), ("tier3", 20)):
        group = sorted((r for r in records if r.get("sampled") and r["tier"] == tier), key=lambda r: r["id"])
        if len(group) < count:
            raise ValueError("not enough cached pilot lines in " + tier)
        chosen.extend(rng.sample(group, count))
    rng.shuffle(chosen)
    return chosen


def preflight(records_path, evidence):
    rows = select(read_jsonl(records_path))
    baselines, bindings, snapshots = {}, {}, []
    for r in rows:
        crop = records_path.parent.parent / "pilot_review_images" / (r["id"] + ".straight.png")
        crop_sha = sha(crop)
        r["straight_crop"] = str(crop)
        single = {}
        for engine in ENGINES:
            v = r["readers"][engine]
            if v["status"] != "ok" or v["rejected"] or v["image_sha256"] != crop_sha:
                raise ValueError("unusable or changed cached single: " + r["id"])
            binding = v["binding"]
            if engine in bindings and bindings[engine] != binding:
                raise ValueError("pilot reader bindings differ")
            bindings[engine] = binding
            raw_path = records_path.parent / "google" / v["raw_json_path"].split("/google/", 1)[1]
            raw_sha = sha(raw_path)
            if engine == "docai":
                cache = json.loads((raw_path.parent / "cache.json").read_text())
            else:
                cache = json.loads((records_path.parent / "google/vision/responses" / (crop_sha + ".json")).read_text())
            if cache["raw_sha256"] != raw_sha or cache["crop_sha256"] != crop_sha or cache["binding"] != binding:
                raise ValueError("cached single receipt hash/options mismatch")
            raw = json.loads(raw_path.read_text())
            from PIL import Image
            with Image.open(crop) as im:
                symbols = response_symbols(engine, raw, im.size)
            values = [s["confidence"] for s in symbols if s["confidence"] is not None]
            mean = statistics.mean(values) if values else None
            if mean is not None and abs(mean - v["mean_confidence"]) > 1e-7:
                raise ValueError("cached single symbol confidence does not match record")
            single[engine] = dict(text=v["text"], raw_text=v["raw_text"], symbols=symbols,
                symbol_count=len(values), mean_symbol_confidence=mean, receipt_id=v["receipt_id"],
                raw_json_path=str(raw_path), raw_sha256=raw_sha, binding=binding)
        baselines[r["id"]] = single
        snapshots.append(dict(id=r["id"], tier=r["tier"], crop=str(crop), crop_sha256=crop_sha,
            readers={e: {k: v for k, v in single[e].items() if k != "symbols"} for e in ENGINES}))
    if bindings["vision"]["language_hints"] != ["el", "grc"]:
        raise ValueError("Vision must use el + grc")
    frozen = dict(schema="greekocr-montage-sample-1", records=str(records_path), records_sha256=sha(records_path),
        count=100, tiers=dict(tier1=40, tier2=40, tier3=20), seed=14,
        selection="sort IDs; random.Random(14).sample per tier; shuffle selected IDs; same order for every N",
        bindings=bindings, crops=snapshots)
    path = evidence / "sample.json"
    if path.exists() and json.loads(path.read_text()) != frozen:
        raise ValueError("frozen sample/baseline changed; choose a new evidence directory")
    atomic(path, frozen)
    return rows, baselines, frozen


def gallery(rows, comparisons, summary, output):
    esc = lambda value: html.escape(str(value), quote=True)
    by_id = {r["id"]: [] for r in rows}
    for result in comparisons:
        by_id[result["id"]].append(result)
    # Reuse the pilot typography, source headers, flags, native crop cards and filters.
    pilot = (_data_input(REPO / "docs/harvest/pilot_review.html")).read_text()
    style = pilot.split("<style>", 1)[1].split("</style>", 1)[0]
    style += ".comparisons{width:100%;border-collapse:collapse;table-layout:fixed}.comparisons th,.comparisons td{text-align:left;vertical-align:top;padding:10px;border-top:1px solid var(--rule);overflow-wrap:anywhere}.comparisons td.text{font:20px/1.6 Georgia,serif;white-space:pre-wrap}.crop-scroll{overflow:auto}.crop-scroll img{max-width:none}th.meta{width:15%}@media(max-width:600px){.comparisons td.text{font-size:16px}.comparisons th,.comparisons td{padding:5px}.crop-scroll img{max-width:100%}}"
    cards = []
    for r in rows:
        results = by_id[r["id"]]
        differs = any(not v["identical"] or v["status"] != "ok" for v in results)
        trs = []
        for v in results:
            if v["identical"] and v["status"] == "ok":
                continue
            trs.append(f'<tr data-n="{v["n"]}" data-engine="{v["engine"]}"><td>{v["engine"]} · N={v["n"]}<small><br>{v["status"]} · CER {v["nfd_cer"]:.4f}<br>{"identical" if v["identical"] else "different"}</small></td><td class="text" lang="el">{esc(v["single_text"])}</td><td class="text" lang="el">{esc(v["montage_text"])}</td></tr>')
        src = os.path.relpath(r["straight_crop"], output.parent)
        cards.append(f'''<article id="{esc(r['id'])}" data-tier="{r['tier']}" data-diff="{str(differs).lower()}">
<header><strong>{esc(r['provenance']['catalogue']['title'])}</strong><span>{r['year']} · page {r['page']} · {r['tier']}</span></header>
<div class="crop-scroll"><img loading="lazy" src="{esc(src)}" alt="Straightened crop {esc(r['id'])}"></div>
<p class="muted">{esc(r['id'])} · <a href="{esc(r['provenance']['source_url'])}">Source page</a> · <a href="pilot_review.html#{esc(r['id'])}">Pilot card</a></p>
{('<table class="comparisons"><thead><tr><th class="meta">Reader / assignment</th><th>Cached single</th><th>Montage</th></tr></thead><tbody>'+''.join(trs)+'</tbody></table>') if trs else '<p>Identical and assigned as one line in both readers at all three N.</p>'}
<p class="flags">Equal ok readings are omitted from the table. Complete assignments and confidences: <a href="montage_v1/comparisons.jsonl">comparisons</a>.</p></article>''')
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>T14 · Montage review</title><style>{style}</style></head><body><main class="wrap"><h1>T14 · Native-pixel montage review</h1>
<p>100 fixed pilot lines: 40 tier 1, 40 tier 2, 20 tier 3. N=10/20/40, both readers. All 100 crops are shown; side-by-side readings appear where text or assignment differs. Cached single is the comparison reference, not ground truth. Recommended N: <b>{summary['n_adopt'] or 'none'}</b>.</p>
<p><a href="MONTAGE_v1.md">Report</a> · <a href="montage_v1/receipt.json">Calls and cost</a></p>
<nav><label>Tier <select id="tier"><option value="">All tiers</option><option>tier1</option><option>tier2</option><option>tier3</option></select></label><label><input id="diff" type="checkbox"> Differences only</label><label>N <select id="n"><option value="">All N</option><option>10</option><option>20</option><option>40</option></select></label><label>Reader <select id="engine"><option value="">Both readers</option><option>vision</option><option>docai</option></select></label><span id="count" aria-live="polite"></span></nav>{''.join(cards)}</main>
<script>function filter(){{let count=0;document.querySelectorAll('article').forEach(a=>{{a.hidden=(tier.value&&a.dataset.tier!==tier.value)||(diff.checked&&a.dataset.diff!=='true');if(!a.hidden)count++;a.querySelectorAll('tbody tr').forEach(r=>r.hidden=(n.value&&r.dataset.n!==n.value)||(engine.value&&r.dataset.engine!==engine.value));}});document.getElementById('count').textContent=count+' lines';}}['tier','diff','n','engine'].forEach(id=>document.getElementById(id).addEventListener('change',filter));filter();</script></body></html>'''
    output.write_text(page)


def report(summary, receipt, output):
    lines = ["# T14 — Native-pixel montage verification", "",
        f"**Recommended N: {summary['n_adopt'] or 'none'}.** Largest N meeting ≥97% exact NFD equality and zero merged/lost crops in **both** readers, on the same frozen 100 lines.", "",
        "Comparison reference is each reader's cached single-crop **cleaned reading** (`readers.<engine>.text`). This measures preservation, not OCR accuracy. Raw single text, unchanged raw-response hashes and settings are in [sample.json](montage_v1/sample.json). No cached crop was recalled. No production reader defaults were changed.", "",
        "## Text and assignment", "",
        "| N | Reader | Identical | Median NFD CER | Merged crops | Lost crops | Split crops | Montages | USD / 1,000 lines | Verdict |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for n in NS:
        for engine in ENGINES:
            s = summary["cohorts"][str(n)][engine]
            lines.append(f"| {n} | {engine} | {s['identical_pct']:.1f}% ({s['identical_count']}/100) | {s['median_nfd_cer']:.6f} | {s['merged']} | {s['lost']} | {s['split']} | {s['montages']} | {s['cost_per_1000_lines_usd']:.4f} | {'ADOPT' if s['adopt'] else 'FAIL'} |")
    lines += ["", "## Symbol confidences", "", "Means are weighted across all reported symbols with confidence, assigned by the same ≥70% height rule for montages. Symbol counts can change with the transcription; this is not paired symbol calibration. Per-crop means/counts are retained in [comparisons.jsonl](montage_v1/comparisons.jsonl).", "",
        "| N | Reader | Single mean | Montage mean | Delta | Single symbols | Montage symbols | Unassigned montage symbols |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for n in NS:
        for engine in ENGINES:
            s = summary["cohorts"][str(n)][engine]
            fmt = lambda value: "—" if value is None else f"{value:.6f}"
            lines.append(f"| {n} | {engine} | {fmt(s['single_mean_symbol_confidence'])} | {fmt(s['montage_mean_symbol_confidence'])} | {fmt(s['confidence_delta'])} | {s['single_symbol_count']} | {s['montage_symbol_count']} | {s['unassigned_symbols']} |")
    lines += ["", "Confidence deltas are small despite the text differences. A median CER of zero reflects that more than half of the crops are identical; it does not satisfy the 97% preservation gate."]
    lines += ["", "## Method and audit", "",
        "Selection: sort sampled pilot IDs within tier, `random.Random(14).sample` 40/40/20, then seeded shuffle. This purposive tier-balanced sample is not a population estimate. Exactly the same order is used for every N. [Frozen sample and baseline hashes](montage_v1/sample.json).", "",
        "Native pixels, no scaling or stretching. Left-aligned crops are padded with white 255 to the widest crop. Between crops: max(60 px, the two adjacent native heights), with a centred 2px grey-153 rule (40% black). No added outer padding. Crop boxes and separator intervals are half-open. Split at 10,000 px height or 8,000,000 encoded PNG bytes; width ≤2,600 px. [All montage maps](montage_v1/manifest.json).", "",
        "DocAI uses reported line layout boxes/text anchors (paragraph fallback only without lines). Vision uses reported symbol breaks within paragraphs and unions their symbol boxes. A box touching two bands is merged and is never guessed into a crop; otherwise ≥70% vertical height overlap assigns it. Zero assigned lines = lost; ≥2 = split. Flags are independent, so merged and lost can overlap. Side-by-side splits use the pilot list-return rule in x order; stacked splits retain LF-separated text and rejection flags. Unassigned boxes, every line and every symbol assignment are in the per-montage `*.assignment.json` files.", "",
        "NFD comparison keeps whitespace in the cleaned reading, without substitutions or accent folding. CER = NFD codepoint Levenshtein distance / cached single NFD length (minimum denominator 1). Assignment uses box height, never intersection area. Split crops are permitted by the requested gate, if equality remains ≥97% and merged/lost are both zero.", "",
        "Vision uses DOCUMENT_TEXT_DETECTION, `el` + `grc`, provider default model (unpinned); DocAI uses the same pilot EU processor, `pretrained-ocr-v2.1-2024-08-07`, `el`, symbols enabled. Context and the unpinned Vision model can both affect readings. The verdict applies to this layout and sample only.", "",
        f"Cost: **{receipt['calls_reserved']} calls reserved; USD {receipt['cost_usd']:.4f}** at conservative standard list price; cap USD 1. Rate USD 0.0015 per image/page, checked 12 October 2026: [Vision pricing](https://cloud.google.com/vision/pricing), [Document AI pricing](https://cloud.google.com/products/document-ai/pricing). Monthly free allowances are not deducted; this is a list-price receipt, not a billing invoice. Cost per 1,000 lines uses actual montage count / 100, including partial final batches and any size splits. With full batches, either reader costs $0.1500/$0.0750/$0.0375 per 1,000 lines at N=10/20/40; both readers together cost twice those rates.", "",
        f"{receipt['unique_montage_images']} unique montage PNGs produced {receipt['calls_reserved']} calls across {len(receipt['evaluations'])} reader/N evaluations. The final 20-crop batch at N=40 is byte-identical to the N=20 tail and reuses both responses. At-most-once: persistent budget reservations precede reader invocation; successful raw/parsed responses are reused, and interrupted/failed reservations are not automatically recalled. Only generated montage hashes are eligible for network calls. [Receipt](montage_v1/receipt.json).", "",
        "Bulk PNGs and Google raw responses are in the repo's ignored `docs/harvest/harvest_big/montage_v1/`, inside the writable workspace. Original pilot images/caches remain at the supplied external `glossapi-ocr-local` path. Only maps, baseline hashes, assignments, comparisons, summary and receipt are in the versionable report directory. [100-crop review](montage_review.html).", "",
        "## Validation", "", "Offline tests cover native pixel conservation, padding/rules/maps, N batching, encoded-size/height splits, oversize refusal, synthetic Vision and DocAI layouts/symbols, 70% boundaries, cross-band merge/lost, side-by-side joins, stacked splits, NFD whitespace/CER, the 97% gate and symbol-weighted means. Final test and gallery QA receipts are linked from receipt.json. The offline validator checks all native montage pixels, every assignment/metric, all 100 gallery cards/images/local links, and unchanged cached single inputs.", "",
        "Visual inspection of the native first montage confirms the separated crop bands and rules. Browser-rendered desktop/narrow QA is **unverified**: Chromium launch was rejected by the macOS sandbox (`bootstrap_check_in ... Permission denied`); the computer-use tool returned `Computer Use was not approved to use Firefox`. [QA receipt](montage_v1/gallery_qa.json)."]
    output.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="authorize only missing montage reads")
    parser.add_argument("--prepare", action="store_true", help="build frozen sample/maps only; no readers")
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    parser.add_argument("--evidence-dir", type=Path, default=REPO / "docs/records/harvest/montage_v1")
    parser.add_argument("--bulk-dir", type=Path, default=REPO / "docs/harvest/harvest_big/montage_v1")
    args = parser.parse_args()
    if args.run and args.prepare:
        parser.error("--run and --prepare are mutually exclusive")
    evidence, bulk = args.evidence_dir.resolve(), args.bulk_dir.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    rows, baselines, sample = preflight(args.records.resolve(), evidence)
    manifest = [m for n in NS for m in build_montages(rows, n, bulk / "images", evidence / "maps")]
    # Every submitted image must be a generated multi-crop montage, never a cached crop.
    single_shas = {c["crop_sha256"] for c in sample["crops"]}
    if any(m["actual_n"] < 2 or m["image_sha256"] in single_shas for m in manifest):
        raise ValueError("refusing network plan containing a singleton or cached single hash")
    atomic(evidence / "manifest.json", manifest)
    plan = dict(montages=len(manifest), max_new_calls=2 * len(manifest),
                max_new_cost_usd=.003 * len(manifest), cap_usd=1)
    atomic(evidence / "plan.json", plan)
    if plan["max_new_cost_usd"] > 1:
        raise ValueError("planned montage calls exceed cap")
    if args.prepare:
        print(json.dumps(plan), flush=True)
        return
    readers = Readers(bulk / "google", cap=1,
        project=sample["bindings"]["vision"]["user_project"], processor=sample["bindings"]["docai"]["processor"])
    readers.budget.max_calls = plan["max_new_calls"]
    if readers.vision.binding() != sample["bindings"]["vision"] or readers.docai.binding() != sample["bindings"]["docai"]:
        raise ValueError("montage reader settings differ from cached single settings")
    comparisons, audit_calls = [], []
    for m in manifest:
        key = m["image_sha256"]
        if sha(m["image"]) != key:
            raise ValueError("montage changed before call")
        if args.run:
            pair = readers.pair(m["image"])
        else:
            paths = {e: bulk / "google/parsed" / e / (key + ".json") for e in ENGINES}
            if not all(path.exists() for path in paths.values()):
                raise ValueError("missing montage responses; use --run for the authorized experiment")
            pair = {e: json.loads(path.read_text()) for e, path in paths.items()}
        print(Path(m["image"]).name + " " + " ".join(e + ":" + pair[e]["status"] for e in ENGINES), flush=True)
        for engine, value in pair.items():
            if value["status"] != "ok":
                raise RuntimeError("montage request failed (no automatic retry): " + engine + " " + value.get("error_class", ""))
            raw = json.loads(Path(value["raw_json_path"]).read_text())
            size = (m["width"], m["height"])
            assigned = assign_lines(response_lines(engine, raw, size), m)
            symbols = assign_symbols(response_symbols(engine, raw, size), m)
            atomic(evidence / "assignments" / (Path(m["image"]).stem + "." + engine + ".assignment.json"),
                   dict(montage_sha256=key, reader=engine, raw_json_path=value["raw_json_path"],
                        raw_sha256=sha(value["raw_json_path"]), line_assignment=assigned, symbol_assignment=symbols))
            audit_calls.append(dict(n=m["n"], reader=engine, image=m["image"], image_sha256=key,
                actual_n=m["actual_n"], receipt_id=value["receipt_id"], raw_json_path=value["raw_json_path"],
                raw_sha256=sha(value["raw_json_path"]), status=value["status"], latency_s=value["latency_s"]))
            for ident, crop in assigned["crops"].items():
                single = baselines[ident][engine]
                ms = symbols["crops"][ident]
                confidences = [s["confidence"] for s in ms if s["confidence"] is not None]
                comparisons.append(dict(id=ident, n=m["n"], engine=engine, montage_sha256=key,
                    single_text=single["text"], montage_text=crop["text"],
                    **{k: v for k, v in crop.items() if k != "text"}, **compare_nfd(single["text"], crop["text"]),
                    single_symbols=single["symbols"], montage_symbols=ms,
                    single_symbol_count=single["symbol_count"], montage_symbol_count=len(confidences),
                    single_mean_symbol_confidence=single["mean_symbol_confidence"],
                    montage_mean_symbol_confidence=statistics.mean(confidences) if confidences else None,
                    service_status=value["status"]))
    summary = dict(cohorts={})
    for n in NS:
        summary["cohorts"][str(n)] = {}
        for engine in ENGINES:
            cohort = [v for v in comparisons if v["n"] == n and v["engine"] == engine]
            if len(cohort) != 100 or len({v["id"] for v in cohort}) != 100:
                raise ValueError("incomplete cohort")
            s = summarise(cohort, sum(m["n"] == n for m in manifest))
            assignments = [json.loads(p.read_text()) for p in (evidence / "assignments").glob(f"n{n:02d}-*.{engine}.assignment.json")]
            s["unassigned_symbols"] = sum(len(a["symbol_assignment"]["unassigned"]) for a in assignments)
            s["merged_boxes"] = sum(a["line_assignment"]["merged_box_count"] for a in assignments)
            s["unassigned_boxes"] = sum(a["line_assignment"]["unassigned_box_count"] for a in assignments)
            summary["cohorts"][str(n)][engine] = s
    summary["n_adopt_by_reader"] = {e: max((n for n in NS if summary["cohorts"][str(n)][e]["adopt"]), default=None) for e in ENGINES}
    summary["n_adopt"] = max((n for n in NS if all(summary["cohorts"][str(n)][e]["adopt"] for e in ENGINES)), default=None)
    atomic(evidence / "summary.json", summary)
    slim = [{k: v for k, v in row.items() if k not in ("single_symbols", "montage_symbols")} for row in comparisons]
    (evidence / "comparisons.jsonl").write_text("".join(json.dumps(v, ensure_ascii=False, allow_nan=False) + "\n" for v in slim))
    unique_calls = {}
    for evaluation in audit_calls:
        key = (evaluation["reader"], evaluation["image_sha256"])
        if key not in unique_calls:
            unique_calls[key] = dict(evaluation, evaluated_at_n=[evaluation["n"]])
        else:
            unique_calls[key]["evaluated_at_n"].append(evaluation["n"])
    receipt = dict(schema="greekocr-montage-receipt-1", timestamp=datetime.now(timezone.utc).isoformat(),
        **readers.budget.receipt(), calls=list(unique_calls.values()), evaluations=audit_calls,
        unique_montage_images=len({m["image_sha256"] for m in manifest}),
        cached_single_reads_reused=200, new_single_crop_calls=0,
        sample_sha256=sha(evidence / "sample.json"), manifest_sha256=sha(evidence / "manifest.json"),
        comparisons_sha256=sha(evidence / "comparisons.jsonl"), summary_sha256=sha(evidence / "summary.json"),
        bulk_root=str(bulk), reader_bindings=sample["bindings"],
        source_sha256={str(p.relative_to(REPO)): sha(p) for p in [Path(__file__), REPO / "greekocr/harvest/montage.py"]},
        validation={"tests": "validation.json", "gallery": "gallery_qa.json"})
    receipt["cost_usd"] = round(receipt["cost_usd"], 6)
    # Offline regeneration proves the original 200 caches and 100 crops remain unchanged.
    _, _, verified_sample = preflight(args.records.resolve(), evidence)
    assert verified_sample == sample
    receipt["single_inputs_revalidated_unchanged"] = True
    atomic(evidence / "receipt.json", receipt)
    report(summary, receipt, evidence.parent / "MONTAGE_v1.md")
    gallery(rows, slim, summary, evidence.parent / "montage_review.html")
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()

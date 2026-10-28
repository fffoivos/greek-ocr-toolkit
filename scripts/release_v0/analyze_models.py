#!/usr/bin/env python3
"""REL0-S1: read-only Stage C analysis; each sealed package runs in its own process.

No checkpoint choice uses test metrics. Run-list schema and exact commands: COMMANDS.md.
Only the supplied output directory is written (including failures and input receipts).
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
import importlib
import itertools
import json
import math
import multiprocessing
import os
from pathlib import Path
import re
import subprocess
import sys
import unicodedata as ud
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True
PANELS = ("harvest_dev", "seal04_dev", "harvest_test", "seal04_test")
MODES = ("nfd_atom", "nfc_char", "diacritic_insensitive")
SCORER = "unchanged S1 SEAL02 o1-metrics/v1 aggregate; literal per-codepoint NFD"
DEFAULT_DATA = "/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-005-genn/data/prepared"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def spec(path):
    path = Path(path).resolve()
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))


def write(path, obj):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def timestamp():
    return datetime.now(ZoneInfo("Europe/Athens")).isoformat()


def run_list(path):
    runs = read(path)
    require(isinstance(runs, list) and runs, "run list must be a nonempty JSON array")
    labels = []
    for r in runs:
        label = r["label"]
        require(re.fullmatch(r"[A-Za-z0-9_.-]+", label) is not None, "unsafe run label")
        require(float(r["width_mult"]) in (1., 1.5, 2.), "unsupported width")
        require(Path(r["run_dir"]).is_absolute() and Path(r["package"]).is_absolute(), "absolute input paths required")
        if float(r["width_mult"]) == 1.:
            require(label == "w1h14-full" and "full-v1-014-w1-h14" in Path(r["run_dir"]).parts,
                    "retired 013 w1-full excluded; x1 must be attempt 014, label w1h14-full")
        labels.append(label)
    require(len(set(labels)) == len(labels), "duplicate run labels")
    require(len({float(r['width_mult']) for r in runs}) == len(runs), "duplicate model widths")
    return runs


def prepare_output(output, runs, data):
    output = Path(output).resolve()
    # Runtime pool roots may lie outside --data-dir; check those too before any writes.
    protected = [Path(data).resolve()]
    for r in runs:
        protected.extend((Path(r["run_dir"]).resolve(), Path(r["package"]).resolve()))
        binding = read(Path(r["run_dir"]) / "RUN_BINDING.json")
        runtime = read(binding["config"]["runtime"]["path"])
        protected.extend(Path(f["path"]).resolve().parent
                         for p in runtime["pools"].values() for f in p["files"])
    require(not any(output == p or p in output.parents for p in protected),
            "output directory must not be inside any run, sealed package or data directory")
    output.mkdir(parents=True, exist_ok=True)
    return output


def load_sealed(package):
    """Call once per worker process, before importing any trainer modules."""
    package = Path(package).resolve()
    payload = read(package / "PAYLOAD.json")
    for rel, identity in payload["files"].items():
        p = (package / rel).resolve()
        require(package in p.parents, "package manifest path escapes root")
        require(p.stat().st_size == identity["bytes"] and sha(p) == identity["sha256"],
                "sealed package differs: " + str(p))
    # Bind the namespace package before adding vendor/train: otherwise train.py
    # shadows the namespace and makes `train.cer` unimportable.
    sys.path.insert(0, str(package / "vendor"))
    importlib.import_module("train")
    scorer = importlib.import_module("bench.score")
    cer = importlib.import_module("train.cer")
    require(Path(scorer.__file__).resolve().is_relative_to(package), "foreign scorer imported")
    require(Path(cer.__file__).resolve().is_relative_to(package), "foreign CER imported")
    return scorer, cer


def check_bound(entry):
    p = Path(entry["path"])
    require(sha(p) == entry["sha256"], "input SHA mismatch: " + str(p))
    if "bytes" in entry:
        require(p.stat().st_size == entry["bytes"], "input size mismatch: " + str(p))
    return p


def selected_from_records(meta, log, exact_evaluations=None):
    """Resolve epoch from dev-only custody, respecting full-precision metadata.

    CSV CER is rounded to six decimals. Rounded ties alone cannot disprove a strict
    improvement. Exact SELECTION_EVAL records, when present, remove that ambiguity.
    """
    require(meta["select_metric"] == "val_cer", "selection metric must be val_cer")
    require(len(log) == 8 and [int(r["epoch"]) for r in log] == list(range(1, 9)),
            "need exactly 8 ordered epoch-end seal04_dev evaluations")
    steps = [int(r["step"]) for r in log]
    require(all(a < b for a, b in zip(steps, steps[1:])), "epoch steps must increase")
    scores = [float(r["val_cer"]) for r in log]
    require(all(math.isfinite(x) and x >= 0 for x in scores), "invalid dev CER")
    epoch, metric = int(meta["best_epoch"]), float(meta["best_metric"])
    require(1 <= epoch <= 8 and math.isfinite(metric), "invalid best metadata")
    require(abs(scores[epoch-1] - metric) <= 0.500001e-6, "best metric differs from train_log")
    require(all(x >= metric - 0.500001e-6 for x in scores), "best metadata is not dev minimum")
    if exact_evaluations is not None:
        require(len(exact_evaluations) == 8, "need exactly eight exact selection evaluations")
        exact = [float(e["result"]["cer"]) for e in exact_evaluations]
        require(all(math.isfinite(x) and x >= 0 for x in exact), "invalid exact dev CER")
        require(all(abs(a-b) <= 0.500001e-6 for a, b in zip(scores, exact)), "exact/CSV selection mismatch")
        require(min(range(8), key=exact.__getitem__) + 1 == epoch and exact[epoch-1] == metric,
                "best epoch violates strict-improvement dev selection")
    return dict(epoch=epoch, step=steps[epoch-1], val_cer=metric,
                rule="strict-improvement best of 8 epoch-end seal04_dev evaluations",
                verification="exact selection records" if exact_evaluations is not None else
                "checkpoint_meta authority; CSV rounded to 6 decimals (ties may be ambiguous)")


def match_selected(selection, best_weight_sha, archives):
    matches = [a for a in archives if a["step"] == selection["step"] and a["weight_sha256"] == best_weight_sha]
    require(len(matches) == 1,
            "NO EXACT SELECTED PREDICTIONS: selected step/weight SHA absent or mismatched; stop, no substitution")
    return matches[0]


def weight_sha256(trainer, weights):
    # Format-independent weights: discard state_dict container metadata/storage
    # layout, retain every named tensor, dtype, shape and byte through sealed hash.
    canonical = {k: v.detach().cpu().contiguous().clone() for k, v in weights.items()}
    return trainer.checkpoint_state_sha256(canonical)


def resolve_selected(run):
    """Trusted owner-custody .pt reads only; no conversions or writes to inputs.

    Full checkpoints contain NumPy RNG state and require pickle. Verify custody SHA
    before loading; inference itself later uses only the sealed safe weights loader.
    Weight SHA uses the producing trainer's canonical model-state hash, NOT the
    full resume-state hash (which also includes optimizer/RNG/cursor).
    """
    import torch
    import numpy as np
    root, package = Path(run["run_dir"]), Path(run["package"])
    binding, claim, meta = (read(root / name) for name in ("RUN_BINDING.json", "CLAIM.json", "checkpoint_meta.json"))
    require(binding["config"] == claim, "RUN_BINDING/CLAIM mismatch")
    require(claim["payload_sha256"] == sha(package / "PAYLOAD.json"), "foreign sealed package")
    require(binding["selection"]["name"] == claim["selection_pool"] == "seal04_dev", "foreign selection pool")
    require(not claim.get("mock") and not claim.get("fixture") and not claim.get("smoke"), "not a production run")
    require(float(meta["width_mult"]) == float(claim["parameters"]["width_mult"]) == float(run["width_mult"]), "width mismatch")
    runtime_path = check_bound(claim["runtime"])
    runtime = read(runtime_path)
    require(binding["selection"]["pool"] == runtime["pools"]["seal04_dev"], "selection pool differs from runtime")
    with (root / "train_log.csv").open(newline="") as stream:
        log = list(csv.DictReader(stream))
    exact_files = sorted(root.glob("SELECTION_EVAL_*.json"), key=lambda p: int(p.stem.rsplit("_", 1)[1]))
    exact_records = [read(p) for p in exact_files]
    require(all(e["selection"] == binding["selection"] for e in exact_records), "selection records use foreign pool")
    # These diagnostics have timestamps, not epoch/step tags. Interrupted
    # attempts can leave extra records; do not guess which belongs to an epoch.
    exact = exact_records if len(exact_records) == 8 else None
    selected = selected_from_records(meta, log, exact)
    selected['exact_selection_record_count'] = len(exact_records)
    require(sha(root / "best.pt") == meta["best_pt_sha256"], "best.pt custody SHA mismatch")
    trainer = importlib.import_module("train.train")
    trainer.torch, trainer.np = torch, np
    ck = torch.load(root / "best.pt", map_location="cpu", weights_only=False)
    require(ck["epoch"] == selected["epoch"] and ck["global_step"] == selected["step"], "best.pt epoch/step mismatch")
    require(ck["best"] == dict(epoch=selected["epoch"], metric=selected["val_cer"]), "best.pt selection mismatch")
    require(ck["state_sha256"] == trainer.checkpoint_state_sha256(ck), "best.pt canonical state mismatch")
    weight_sha = weight_sha256(trainer, ck["model"])
    from train import ckpt_io
    weights, weights_meta = ckpt_io.load_model_weights(str(root / "best.safetensors"))
    require(weight_sha256(trainer, weights) == weight_sha, "best.safetensors/best.pt weight SHA mismatch")
    codec_path = package / "vendor/codec/v2.1.json"
    require(ck["codec_sha256"] == weights_meta["codec_sha256"] == sha(codec_path), "codec SHA mismatch")
    for key in ("arch", "head", "codec_version", "n_classes", "width_mult", "epoch"):
        require(str(weights_meta[key]) == str(ck[key]), "safetensors metadata mismatch: " + key)
    require(ck['head'] == 'nfd', "only the producing NFD head is supported")
    param_count = sum(v.numel() for v in weights.values())
    del ck, weights
    eval_paths = sorted((root / "eval").glob("step-*.json"))
    entries = [read(p) for p in eval_paths]
    require(len(entries) == 4 and sorted(e["step"] for e in entries) == sorted(binding["evaluation_steps"]) == sorted(claim["cer_steps"]),
            "need exactly four bound CER steps")
    candidates = []
    for e in entries:
        require(e["runtime_sha256"] == claim["runtime"]["sha256"], "eval runtime mismatch")
        require(set(e["instruments"]) == set(PANELS) == set(e["prediction_files"]), "incomplete instruments")
        if e["step"] != selected["step"]:
            continue
        archive = check_bound(e["checkpoint"])
        a = torch.load(archive, map_location="cpu", weights_only=False)
        require(a["global_step"] == e["step"] and a["state_sha256"] == e["state_sha256"] == trainer.checkpoint_state_sha256(a),
                "selected archive canonical state mismatch")
        candidates.append(dict(step=e["step"], weight_sha256=weight_sha256(trainer, a["model"]),
                               checkpoint=spec(archive), state_sha256=e['state_sha256']))
        del a
    selected_archive = match_selected(selected, weight_sha, candidates)
    selected.update(weight_sha256=weight_sha, safetensors=spec(root / "best.safetensors"),
                    archive=selected_archive,
                    best_pt=spec(root / "best.pt"), metadata=weights_meta,
                    weight_sha_method='sealed checkpoint_state_sha256 v2 on plain dict of cloned contiguous CPU tensors',
                    parameter_count=meta["param_count"], state_tensor_elements_including_buffers=param_count)
    receipts = {name: spec(root / name) for name in ("RUN_BINDING.json", "CLAIM.json", "checkpoint_meta.json", "train_log.csv")}
    receipts.update(runtime=spec(runtime_path), package_payload=spec(package / "PAYLOAD.json"), codec=spec(codec_path),
                    exact_selection_records=[spec(p) for p in exact_files],
                    evaluation_records=[dict(record=spec(p), prediction_files=e['prediction_files'],
                                             checkpoint_declared=e['checkpoint']) for p,e in zip(eval_paths, entries)])
    return selected, entries, runtime, receipts


def load_references(data, runtime, codec):
    import pyarrow.parquet as pq
    columns = ["line_id", "gt_nfd", "label_ids", "codec_version", "source_dataset", "script_class"]
    panels, receipts = {}, {}
    for panel in PANELS:
        files = sorted((Path(data) / panel).glob("part-*.parquet"))
        require(files, "no reference shards: " + panel)
        require({str(p.resolve()) for p in files} == {str(Path(f['path']).resolve()) for f in runtime['pools'][panel]['files']},
                "reference shards differ from bound runtime: " + panel)
        for f in runtime['pools'][panel]['files']:
            check_bound(f)
        rows = [r for p in files for batch in pq.ParquetFile(p).iter_batches(columns=columns, batch_size=2048)
                for r in batch.to_pylist()]
        byid = {r["line_id"]: r for r in rows}
        require(len(byid) == len(rows) == runtime["pools"][panel]["rows"] and rows, "duplicate/empty/incomplete reference IDs")
        require(set(byid) == set(runtime["references"][panel]), "runtime/reference ID mismatch")
        for ident, row in byid.items():
            require(row["codec_version"] == codec.version, "reference codec mismatch")
            require(codec.decode(row["label_ids"]) == row["gt_nfd"], "label/gt_nfd mismatch: " + ident)
            # full_hook scores the original literal runtime text, not re-encoded labels.
            text = runtime["references"][panel][ident]
            require(''.join(ud.normalize('NFD', c) for c in text) == row['gt_nfd'], "runtime/gt_nfd mismatch: " + ident)
            row["text"] = text
        panels[panel] = byid
        receipts[panel] = [spec(p) for p in files]
    return panels, receipts


def groups(row, ref):
    letters = [c for c in ref if c.isalpha()]
    digits = any(c.isdecimal() for c in ref)
    compact = ''.join(c for c in ref if not c.isspace())
    kind = ("digits_only" if compact and all(c.isdecimal() for c in compact) else
            "mixed" if letters and digits else "letters" if letters else "other")
    n = len(ref)
    bucket = "0-25" if n <= 25 else "26-50" if n <= 50 else "51-100" if n <= 100 else "101-200" if n <= 200 else "201+"
    # Marks belong to the preceding Greek base; Latin grave is not polytonic Greek.
    greek = poly = False
    for c in ref:
        if not ud.category(c).startswith("M"):
            greek = "GREEK" in ud.name(c, "")
        elif greek and c in "\u0313\u0314\u0342\u0345\u0300":
            poly = True
    parts = row['line_id'].split(':')
    prefix = ':'.join(parts[:2]) if parts[0] == 'harvest' and len(parts) > 2 else parts[0] if len(parts) > 1 else '<none>'
    return dict(source_dataset=row["source_dataset"], id_prefix=prefix,
                script_class=row["script_class"], length_bucket=bucket, content=kind,
                polytonic=str(poly).lower(), all_caps=str(bool(letters) and all(c.isupper() for c in letters)).lower())


def totals(lines):
    result = dict(lines=len(lines), exact_lines=sum(r["correct"] for r in lines), metrics={})
    result["exact_line_rate"] = result["exact_lines"] / len(lines) if lines else None
    for mode in MODES:
        edits = sum(r["metrics"][mode]["edits"] for r in lines)
        units = sum(r["metrics"][mode]["reference_units"] for r in lines)
        result["metrics"][mode] = dict(edits=edits, reference_units=units, cer=edits/units if units else None)
    return result


def detailed(rows, predictions, scorer):
    lines, buckets = [], defaultdict(lambda: defaultdict(list))
    operations, confusion, examples = Counter(), Counter(), defaultdict(list)
    error_lines = Counter(nfd_correct=0, diacritic_only=0, base_or_other=0)
    error_ops = Counter(diacritic=0, base_or_other=0)
    for ident in sorted(rows):
        row, hyp = rows[ident], predictions[ident]
        ref = row["text"]
        metrics = {}
        for mode in MODES:
            r, h = scorer.normalize(ref, mode), scorer.normalize(hyp, mode)
            metrics[mode] = dict(edits=scorer.levenshtein(r, h), reference_units=len(r))
        correct = scorer.normalize(ref, "nfc_char") == scorer.normalize(hyp, "nfc_char")
        line = dict(id=ident, correct=correct, nfd_exact=metrics["nfd_atom"]["edits"] == 0, metrics=metrics)
        lines.append(line)
        r, h = scorer.normalize(ref, "nfd_atom"), scorer.normalize(hyp, "nfd_atom")
        for dimension, value in groups(row, r).items():
            buckets[dimension][value].append(line)
        error_lines["nfd_correct" if metrics['nfd_atom']['edits'] == 0 else "diacritic_only" if metrics["diacritic_insensitive"]["edits"] == 0 else "base_or_other"] += 1
        # Avoid full quadratic alignment allocation for correct lines.
        if r == h:
            continue
        aligned_edits = 0
        for a, b in scorer.alignment(r, h):
            if a == b:
                continue
            aligned_edits += 1
            op = "insertion" if a is None else "deletion" if b is None else "substitution"
            operations[op] += 1
            key = (a, b)
            confusion[key] += 1
            if ident not in examples[key] and len(examples[key]) < 3:
                examples[key].append(ident)
            marks = all(ud.category(c).startswith("M") for c in (a, b) if c is not None)
            error_ops["diacritic" if marks else "base_or_other"] += 1
        require(aligned_edits == metrics['nfd_atom']['edits'], "alignment/edit distance disagreement")
    top = sorted(confusion, key=lambda k: (-confusion[k], k[0] or '', k[1] or ''))[:50]
    return dict(totals=totals(lines), lines=lines,
                breakdowns={d: {str(k): totals(v) for k, v in sorted(bs.items(), key=lambda x: str(x[0]))} for d, bs in buckets.items()},
                error_types={op: operations[op] for op in ("substitution", "insertion", "deletion")},
                error_line_classes=dict(error_lines), error_atom_classes=dict(error_ops),
                top_confusions=[dict(reference=a, hypothesis=b, reference_cp=f"U+{ord(a):04X}" if a else None,
                                     hypothesis_cp=f"U+{ord(b):04X}" if b else None, count=confusion[a,b], examples=examples[a,b]) for a,b in top])


def assert_reproduced(actual, stored, context):
    # Compare the ENTIRE sealed aggregate, including WER/script confusion; no tolerance.
    require(actual == stored, "SCORER REPRODUCTION MISMATCH: " + context)


_REFS = _SCORE = None


def analyze_panel(task):
    step, name, entry, selected = task
    p = check_bound(entry["prediction_files"][name])
    records = [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
    predictions = {r["id"]: r["hyp"] for r in records}
    rows = _REFS[name]
    require(len(predictions) == len(records) and set(predictions) == set(rows), "duplicate/missing/extra prediction IDs: " + str(p))
    require(all(isinstance(h, str) for h in predictions.values()) and not any(r.get('error') for r in records), "failed/nonstring prediction")
    stored = entry["instruments"][name]
    require(stored["scorer"] == SCORER and stored["rows"] == len(rows), "foreign scorer or row count")
    aggregate = _SCORE.aggregate([(dict(text=rows[r["id"]]["text"]), r["hyp"]) for r in records])
    assert_reproduced(aggregate, stored["score"], f"step={step} instrument={name}")
    return step, name, dict(aggregate=aggregate, predictions=spec(p),
                            **(detailed(rows, predictions, _SCORE) if selected else {}))


def paired_bootstrap(left, right, seed=20261028, resamples=10000):
    """Paired line resampling, corpus ratio of sums, left CER minus right CER.

    NumPy PCG64 and linear percentile interpolation are explicit. Chunk size 64
    bounds temporary memory, including pooled dev. No test-set caller exists.
    """
    import numpy as np
    require(resamples > 0 and len(left) > 0, "empty bootstrap or invalid resample count")
    a, b = {r["id"]: r for r in left}, {r["id"]: r for r in right}
    require(len(a) == len(left) and len(b) == len(right) and set(a) == set(b), "bootstrap ID mismatch")
    ids = sorted(a)
    units, delta = [], []
    for ident in ids:
        x, y = a[ident]["metrics"]["nfd_atom"], b[ident]["metrics"]["nfd_atom"]
        require(x["reference_units"] == y["reference_units"], "bootstrap reference mismatch")
        units.append(x["reference_units"])
        delta.append(x["edits"] - y["edits"])
    units, delta = np.array(units, dtype=np.int64), np.array(delta, dtype=np.int64)
    require(int(units.sum()) > 0 and bool((units > 0).all()), "bootstrap needs nonempty reference lines")
    rng = np.random.Generator(np.random.PCG64(seed))
    estimates = np.empty(resamples, dtype=np.float64)
    for start in range(0, resamples, 64):
        idx = rng.integers(0, len(ids), size=(min(64, resamples-start), len(ids)))
        estimates[start:start+len(idx)] = delta[idx].sum(axis=1) / units[idx].sum(axis=1)
    return dict(difference=float(delta.sum()/units.sum()), ci95=np.quantile(estimates, [.025, .975], method="linear").tolist(),
                seed=seed, resamples=resamples, lines=len(ids), numpy_version=np.__version__,
                rng="PCG64", method="paired lines; corpus NFD-atom edits/reference units; percentile linear; left minus right")


def cross_models(results, seed, resamples):
    labels = list(results)
    overlap, bootstrap = {}, {}
    for panel in PANELS:
        maps = {label: {r["id"]: r for r in results[label]["selected_panels"][panel]["lines"]} for label in labels}
        ids = sorted(maps[labels[0]])
        require(all(set(v) == set(ids) for v in maps.values()), "cross-model coverage mismatch")
        counts, all_wrong = Counter(), []
        for ident in ids:
            wrong = tuple(label for label in labels if not maps[label][ident]["correct"])
            counts[wrong] += 1
            if len(wrong) == len(labels):
                all_wrong.append(ident)
        overlap[panel] = dict(models=labels, lines=len(ids), wrong_in_all=counts[tuple(labels)],
                              wrong_in_one=sum(n for k,n in counts.items() if len(k) == 1),
                              wrong_in_some=sum(n for k,n in counts.items() if 0 < len(k) < len(labels)),
                              wrong_in_some_exclusive=sum(n for k,n in counts.items() if 1 < len(k) < len(labels)),
                              correct_in_all=counts[()], patterns=[dict(wrong_in=list(k), lines=v) for k,v in sorted(counts.items())],
                              all_three_wrong_ids=all_wrong if len(labels) == 3 and panel.endswith("_dev") else None,
                              role="dev decision evidence" if panel.endswith("_dev") else "report only")
    for left, right in itertools.combinations(labels, 2):
        bootstrap[left + " minus " + right] = {}
        for panel_names, key in ((("harvest_dev",), "harvest_dev"), (("seal04_dev",), "seal04_dev"),
                                 (("harvest_dev", "seal04_dev"), "pooled_dev")):
            samples = []
            for label in (left, right):
                # Namespace IDs by instrument in the pooled resampling unit.
                samples.append([dict(r, id=p + ":" + r["id"]) for p in panel_names
                                for r in results[label]["selected_panels"][p]["lines"]])
            bootstrap[left + " minus " + right][key] = paired_bootstrap(*samples, seed, resamples)
    return dict(overlap=overlap, bootstrap=bootstrap)


def table(headers, rows):
    def cell(v):
        return str(v).replace("|", "\\|").replace("\n", " ").replace("\r", " ")
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"]*len(headers)) + " |"] +
                     ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows])


def render_report(summary):
    results, cross = summary["runs"], summary["cross_model"]
    out = ["# Greek OCR release analysis", "Generated " + summary["generated_at"],
           "Checkpoint choice: trainer best.pt, strict improvement over eight epoch-end seal04_dev evaluations. "
           "All aggregates reproduced exactly with the sealed scorer. CER is a fraction; bootstrap differences are left minus right.",
           "Correct/incorrect and exact-line rate use sealed NFC equality. NFD-exact is also retained per line. "
           "Length buckets count NFD atoms. Digits-only ignores whitespace, letters excludes decimal digits, mixed has both, other covers remaining furniture. "
           "All-caps requires at least one letter and every letter uppercase. Polytonic requires a Greek base with breathing, perispomeni, subscript or grave. "
           "Diacritic-only error lines are NFD-incorrect but accent-blind-correct; nfd_correct counts NFD-exact lines. Base_or_other includes punctuation, spaces and digits. "
           "ID prefix is the first colon namespace (harvest includes its wave); IDs without a colon have no prefix. "
           "Confusions use sealed NFD alignment (substitution/deletion/insertion tie order), at most three example IDs each.",
           "## Selected weights", table(["Run", "Epoch", "Step", "Weight SHA256", "Parameters", "Safetensors bytes"],
             [[label, r['selection']['epoch'], r['selection']['step'], r['selection']['weight_sha256'],
               r['selection']['parameter_count'], r['selection']['safetensors']['bytes']] for label,r in results.items()])]
    for role, panels in (("Dev — decision evidence", PANELS[:2]), ("Test — report only", PANELS[2:])):
        out.append("## " + role)
        out.append("### Trajectory")
        out.append(table(["Run", "Step", "Selected", "Instrument", "Lines", "NFD CER", "NFC CER", "Accent-blind CER", "Exact-line rate"],
          [[label, step, int(step) == r['selection']['step'], panel, vals[panel]['lines'],
            *[vals[panel]['cer'][m]['rate'] for m in MODES], vals[panel]['exact_line_rate']]
           for label,r in results.items() for step,vals in r['trajectory'].items() for panel in panels]))
        for label,r in results.items():
            for panel in panels:
                d = r['selected_panels'][panel]
                out.extend([f"### {label} / {panel} — selected checkpoint breakdowns", table(
                    ["Dimension", "Group", "Lines", "NFD units", "NFD edits", "NFD CER", "NFC CER", "Accent-blind CER", "Exact-line rate"],
                    [[dim,k,v['lines'],v['metrics']['nfd_atom']['reference_units'],v['metrics']['nfd_atom']['edits'],
                      *[v['metrics'][m]['cer'] for m in MODES],v['exact_line_rate']]
                     for dim,bs in d['breakdowns'].items() for k,v in bs.items()]),
                    "Error types: " + json.dumps(d['error_types']) + "; error line classes: " + json.dumps(d['error_line_classes']) +
                    "; error atom classes: " + json.dumps(d['error_atom_classes']),
                    "#### Top 50 NFD atom confusions (null means insertion/deletion gap)",
                    table(["Reference", "Hypothesis", "Count", "Example IDs"],
                          [[json.dumps(c['reference'],ensure_ascii=True),json.dumps(c['hypothesis'],ensure_ascii=True),c['count'],', '.join(c['examples'])]
                           for c in d['top_confusions']])])
        out.extend(["### Cross-model overlap", "Wrong in some includes one; the exclusive column counts 2..N-1. With two models, all means both; three-way ID lists are pending x1.",
                    table(["Instrument", "Correct all", "Wrong all", "Wrong some", "Wrong one", "Wrong 2..N-1"],
                          [[p,*[cross['overlap'][p][k] for k in ('correct_in_all','wrong_in_all','wrong_in_some','wrong_in_one','wrong_in_some_exclusive')]] for p in panels])])
        if role.startswith("Dev"):
            for p in panels:
                ids = cross['overlap'][p]['all_three_wrong_ids']
                out.extend([f"#### {p}: wrong in all three (dev IDs)", ', '.join(ids) if ids is not None else "Pending all three models."])
            out.extend(["### Paired bootstrap — dev only", table(["Pair", "Instrument", "CER difference", "95% CI", "Resamples", "Seed"],
                [[pair,p,b['difference'],b['ci95'],b['resamples'],b['seed']] for pair,ps in cross['bootstrap'].items() for p,b in ps.items()])])
    out.append("## Speed — harvest_dev only")
    speed = summary.get('speed', {})
    out.append(table(["Run", "Device", "Precision", "Threads", "Batch", "ms/line", "lines/s", "Status"],
        [[label,c['device'],c['precision'],c['threads'],c['batch_size'],c.get('ms_per_line'),c.get('lines_per_second'),c['status']]
         for label,modes in speed.items() for bench in modes.values() for c in bench['cases']]))
    if not speed:
        out.append("Pending benchmark jobs. Merge CPU/GPU receipts with --collect-speed after they finish.")
    else:
        out.append(table(["Run", "Allocation", "Host", "CPU", "GPU", "Torch", "Interop threads", "Height"],
            [[label, mode, bench['hardware']['hostname'], bench['hardware']['processor'] or bench['hardware']['machine'],
              bench['hardware'].get('gpu_name', ''), bench['hardware']['torch_version'],
              bench['hardware']['interop_threads'], bench['input_height']]
             for label,modes in speed.items() for mode,bench in modes.items()]))
    out.append("Speed includes PNG decode/collation, normalisation, device transfer, masked forward, CPU greedy decoding; excludes disk reads, weight load and warm-up. "
               "Five timed passes over the same 2,000 fixed-order harvest_dev lines; medians and raw repeats in speed JSON. "
               "Hardware, Torch, thread settings, parameter counts and input identities are recorded per benchmark receipt.")
    return "\n\n".join(out) + "\n"


def worker(args, run, output):
    global _REFS, _SCORE
    _SCORE, cer = load_sealed(run['package'])
    import torch
    torch.set_num_threads(1)
    selected, entries, runtime, receipts = resolve_selected(run)
    codec = cer.load_codec(str(Path(run['package']) / 'vendor/codec/v2.1.json'))
    _REFS, receipts['references'] = load_references(args.data_dir, runtime, codec)
    tasks = [(e['step'], p, e, e['step'] == selected['step']) for e in entries for p in PANELS]
    if args.jobs == 1:
        values = list(map(analyze_panel, tasks))
    else:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=args.jobs, mp_context=multiprocessing.get_context('fork')) as pool:
            values = list(pool.map(analyze_panel, tasks))
    trajectory, panels = defaultdict(dict), {}
    for step, panel, result in values:
        trajectory[str(step)][panel] = result['aggregate']
        if step == selected['step']:
            panels[panel] = result
    result = dict(status='PASS', run=run, selection=selected, inputs=receipts, trajectory=dict(trajectory),
                  selected_panels=panels, generated_at=timestamp(), code={p.name: spec(p) for p in Path(__file__).parent.glob('*.py')})
    write(output / ('analysis_' + run['label'] + '.json'), result)


def collect_speed(summary, output):
    speed = {}
    sample_sha = None
    for label,r in summary['runs'].items():
        speed[label] = {}
        for mode in ('cpu', 'gpu'):
            path = output / f'speed_{label}_{mode}.json'
            require(path.exists(), 'missing speed receipt: ' + str(path))
            bench = read(path)
            require(bench['run'] == r['run'] and bench['selection']['weight_sha256'] == r['selection']['weight_sha256']
                    and bench['selection']['step'] == r['selection']['step'], 'speed/analysis binding mismatch')
            require(bench['sample']['lines'] == 2000 and bench['repeats'] == 5, 'incomplete benchmark recipe')
            expected = ({('cpu', 'fp32', t, b) for t in (1, 8) for b in (1, 32)} if mode == 'cpu' else
                        {('cuda', precision, 1, b) for precision in ('bf16', 'fp32') for b in (1, 32, 256)})
            actual = [(c['device'], c['precision'], c['threads'], c['batch_size']) for c in bench['cases']]
            require(len(actual) == len(expected) and set(actual) == expected, 'incomplete benchmark grid')
            if sample_sha is None:
                sample_sha = bench['sample']['ids_sha256']
            require(bench['sample']['ids_sha256'] == sample_sha, 'speed samples differ across models or devices')
            require(bench['status'] == 'PASS', 'benchmark receipt failed')
            require(all(c['status'] in ('PASS', 'UNSUPPORTED') for c in bench['cases']), 'benchmark has failed cases')
            require(all(c['status'] != 'PASS' or (len(c['repeat_seconds']) == 5 and c['lines'] == 2000) for c in bench['cases']),
                    'incomplete benchmark repeat coverage')
            speed[label][mode] = bench
    return speed


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs', required=True, type=Path)
    p.add_argument('--data-dir', type=Path, default=Path(DEFAULT_DATA))
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--jobs', type=int, default=16)
    p.add_argument('--seed', type=int, default=20261028)
    p.add_argument('--resamples', type=int, default=10000)
    p.add_argument('--collect-speed', action='store_true', help='merge completed speed receipts; do not recompute analysis')
    p.add_argument('--worker', help=argparse.SUPPRESS)
    args = p.parse_args()
    require(args.jobs > 0 and args.resamples > 0, 'jobs/resamples must be positive')
    runs = run_list(args.runs)
    output = prepare_output(args.out, runs, args.data_dir)
    try:
        if args.worker:
            worker(args, next(r for r in runs if r['label'] == args.worker), output)
            return
        if args.collect_speed:
            summary = read(output / 'SUMMARY.json')
            require([r for r in runs] == [r['run'] for r in summary['runs'].values()], 'summary/run list mismatch')
            summary['speed'] = collect_speed(summary, output)
            for label, result in summary['runs'].items():
                result['speed'] = summary['speed'][label]
                write(output / ('analysis_' + label + '.json'), result)
        else:
            for r in runs:
                subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--runs', str(args.runs.resolve()),
                                '--data-dir', str(args.data_dir), '--out', str(output), '--jobs', str(args.jobs), '--worker', r['label']], check=True)
            results = {r['label']: read(output / ('analysis_' + r['label'] + '.json')) for r in runs}
            summary = dict(status='PASS', generated_at=timestamp(), run_list=spec(args.runs), runs=results,
                           cross_model=cross_models(results, args.seed, args.resamples), speed={},
                           test_policy='report only; never checkpoint, threshold or model selection',
                           bootstrap_seed=args.seed, bootstrap_resamples=args.resamples)
        summary['generated_at'] = timestamp()
        write(output / 'SUMMARY.json', summary)
        (output / 'REPORT.md').write_text(render_report(summary), encoding='utf-8')
        write(output / 'RECEIPT.json', dict(generated_at=timestamp(), status='PASS',
              outputs=[spec(output / name) for name in ['SUMMARY.json', 'REPORT.md'] + ['analysis_' + r['label'] + '.json' for r in runs]]))
    except Exception as exc:
        write(output / ('FAILURE_' + (args.worker or 'analysis') + '.json'), dict(status='FAIL', error=str(exc), generated_at=timestamp()))
        raise


if __name__ == '__main__':
    main()

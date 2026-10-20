"""T6c2 paired CPU CER gate, using T6a2's unchanged evaluator and strip adapter."""
from __future__ import annotations

import run
import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time

HERE, ROOT, OCR = run.HERE, run.ROOT, run.OCR
EVALUATOR_PINS = {
    "train/eval_cer.py": "3ee768a4501974085f32b8efd901415557ecfaa547b3471607f1193793785f21",
    "bench/o4b_models.py": "cdaf5b04a425ebca368d085575e787291ba457985e313d8db87ddf7659eba2ec",
    "train/data.py": "7f145aa9af70727bb54303bda0f9bb92a8b4b613508f1bf4566acc2c27b73ebc",
    "out/e4/wave1a/job01/runs/ctrl_s0/best.pt": "e20cd6cdfc908339b3c7c8f83e88888120240aabc01370a86b7b48606fa81c30",
    "out/e4/wave1a/job01/runs/ctrl_s0/best.safetensors": "29228867db27792f94f6040fed1c828da4335405ab9993e16fc02fbac098ef49",
}


def stratified_subset(records, size, seed):
    """Proportional wave quotas by largest remainder, exact total, seeded IDs."""
    if size < 1 or not records:
        raise ValueError("nonempty population and positive sample required")
    groups = defaultdict(list)
    for row in sorted(records, key=lambda r: r["id"]):
        groups[row["wave"]].append(row)
    n = min(size, len(records))
    quotas = {w: n*len(g)//len(records) for w, g in groups.items()}
    ranking = sorted(groups, key=lambda w: (-(n*len(groups[w]) % len(records)), w))
    for w in ranking[:n-sum(quotas.values())]:
        quotas[w] += 1
    if any(not q for q in quotas.values()):
        raise ValueError("sample too small to represent every wave")
    rng = random.Random(seed)
    selected = [r for w in sorted(groups) for r in rng.sample(groups[w], quotas[w])]
    return sorted(selected, key=lambda r: r["id"]), quotas


def bootstrap(records, unit, replicates, seed):
    """Paired percentile CIs for corpus CER, resampling whole lines or pages."""
    import numpy as np
    groups = defaultdict(lambda: [0, 0, 0])
    for r in records:
        key = r["id"] if unit == "line" else (r["wave"], r["page"])
        value = groups[key]
        value[0] += r["original_edits"]
        value[1] += r["masked_edits"]
        value[2] += r["ref_len"]
    values = np.asarray(list(groups.values()), dtype=np.float64)
    rng = np.random.default_rng(seed)
    samples = []
    for offset in range(0, replicates, 64):
        weights = rng.multinomial(len(values), np.full(len(values), 1/len(values)), size=min(64, replicates-offset))
        totals = weights @ values
        original, masked = totals[:, 0]/totals[:, 2], totals[:, 1]/totals[:, 2]
        samples.append(np.column_stack((original, masked, masked-original)))
    interval = np.quantile(np.concatenate(samples), [.025, .975], axis=0)
    return dict(units=len(values), replicates=replicates, confidence=.95, method="paired percentile bootstrap of corpus CER",
                **{name: interval[:, i].tolist() for i, name in enumerate(("original_cer", "masked_cer", "delta_masked_minus_original"))})


def metrics(records, replicates, seed):
    refs = sum(r["ref_len"] for r in records)
    original = sum(r["original_edits"] for r in records)
    masked = sum(r["masked_edits"] for r in records)
    return dict(lines=len(records), pages=len({(r["wave"], r["page"]) for r in records}), ref_len=refs,
                original_edits=original, masked_edits=masked, original_cer=original/refs, masked_cer=masked/refs,
                delta_masked_minus_original=(masked-original)/refs,
                line_bootstrap_95_ci=bootstrap(records, "line", replicates, seed),
                page_cluster_bootstrap_95_ci=bootstrap(records, "page", replicates, seed+1))


def matching_counts(records):
    return {w: {s: sum(r["wave"] == w and r["match_status"] == s for r in records)
                for s in ("matched", "ambiguous", "unmatched")} for w in run.WAVES}


def verify_mask_output(output):
    receipt = json.loads((output / "mask_receipt.json").read_text())
    if receipt["schema"] != "t6c2-mask-1" or receipt["status"] != "completed":
        raise RuntimeError("complete masking receipt required; failed pages cannot disappear from harm gate")
    if receipt["binding"]["runner_sha256"] != run.sha(HERE / "run.py"):
        raise RuntimeError("runner changed after masking")
    for name, digest in receipt["artifacts"].items():
        if run.sha(output / name) != digest:
            raise RuntimeError("mask artifact changed: " + name)
    for path, digest in receipt["binding"]["inputs"].items():
        if run.sha(path) != digest:
            raise RuntimeError("mask input changed: " + path)
    records = list(run.rows(output / "lines.jsonl"))
    imports = {r["line_id"]: r for r in run.rows(output / "real_v2_test_masked.jsonl")}
    ids = {r["id"] for r in records}
    if len(ids) != len(records) or ids != set(imports) or len(records) != receipt["selected_lines"]:
        raise RuntimeError("mask records/import/selection inventory differs")
    for r in records:
        if r["wave"] not in run.WAVES or imports[r["id"]]["crop"] != str(output / r["masked_path"]):
            raise RuntimeError("wave/path import mismatch")
        if not r["mask_applied"] and r["masked_path"] != r["original_path"]:
            raise RuntimeError("unmatched line must point to original crop")
    return receipt, records, imports


def infer(output, harm_out, size, seed, replicates):
    import numpy as np
    from PIL import Image
    import torch
    sys.path.insert(0, str(OCR))
    sys.path.insert(0, str(OCR / "train"))
    from eval_cer import evaluate, load_checkpoint
    from data import collate_strips
    from cer import load_codec
    from bench.o4b_models import strip
    from bench.o5_prepare import codec_tables, normalize
    from model import amp_dtype_for
    from ckpt_io import load_safetensors
    from torch.utils.data import DataLoader
    start = time.monotonic()
    frozen = run.frozen()
    for name, expected in EVALUATOR_PINS.items():
        if run.sha(OCR / name) != expected:
            raise RuntimeError("T6a2 evaluator/checkpoint changed: " + name)
    receipt, records, imports = verify_mask_output(output)
    selected, quotas = stratified_subset(records, size, seed)
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    torch.manual_seed(seed)
    device = torch.device("cpu")
    checkpoint = OCR / "out/e4/wave1a/job01/runs/ctrl_s0/best.pt"
    weights = checkpoint.with_suffix(".safetensors")
    codec = load_codec(str(OCR / "codec/v1.json"))
    model, meta = load_checkpoint(str(weights), codec, device)
    safe_sd, _ = load_safetensors(str(weights))
    with torch.serialization.safe_globals([np._core.multiarray._reconstruct, np.ndarray, np.dtype, type(np.dtype(np.uint32))]):
        full = torch.load(checkpoint, map_location="cpu", weights_only=True)
    if safe_sd.keys() != full["model"].keys() or not all(torch.equal(safe_sd[k], full["model"][k]) for k in safe_sd):
        raise RuntimeError("safetensors differ from verified ctrl_s0 best.pt")
    del full, safe_sd
    atoms, folds = codec_tables()
    labels = {}
    factory_labels = run.import_labels(output, imports)
    for r in selected:
        text = normalize(imports[r["id"]]["text"], folds)
        if not text or set(text) - atoms.keys():
            raise RuntimeError("excluded/empty label entered harm test")
        labels[r["id"]] = np.asarray(factory_labels[r["id"]], dtype=np.int64)
        for key, digest in (("original_path", "stored_crop_sha256"), ("masked_path", "masked_sha256")):
            if run.sha(output / r[key]) != r[digest]:
                raise RuntimeError("crop changed: " + r["id"])
    def width(r):
        x0, y0, x1, y1 = r["crop_box"]
        return min(2560, max(64, round((x1-x0)*48/(y1-y0))))
    ordered = sorted(selected, key=width)
    run.write_rows(harm_out / "sample.jsonl", selected)
    binding = dict(device="cpu", threads=4, interop_threads=1, batch_size=16, seed=seed,
                   evaluator_inputs=EVALUATOR_PINS, frozen=frozen, harm_sha256=run.sha(__file__), checkpoint_metadata=meta,
                   safetensors_tensor_equality_to_verified_pt=True, sample_sha256=run.sha(harm_out / "sample.jsonl"),
                   mask_receipt_sha256=run.sha(output / "mask_receipt.json"), sample_lines=len(selected), quotas=quotas,
                   network="OFF", metric="strict NFD codepoint corpus CER", label_normalization="unchanged E3 codec v1 normalize/folds",
                   adapter="unchanged train/eval_cer.py:evaluate + bench/o4b_models.py:strip + train/data.py:collate_strips; raw uint8 48-pixel strips",
                   evaluate_run_not_used="CUDA training runtime wrapper; same CPU adapter as T6a2")
    run.write_json(harm_out / "binding.json", binding)
    predictions = {}
    for arm in ("original", "masked"):
        class Crops:
            def __len__(self):
                return len(ordered)
            def __getitem__(self, index):
                r = ordered[index]
                key = "original_path" if arm == "original" else "masked_path"
                digest = "stored_crop_sha256" if arm == "original" else "masked_sha256"
                path = output / r[key]
                if run.sha(path) != r[digest]:
                    raise RuntimeError("crop changed during read: " + r["id"])
                with Image.open(path) as image:
                    array = np.clip(np.rint(strip(image)*255), 0, 255).astype(np.uint8)
                if array.shape[1] != width(r):
                    raise RuntimeError("crop dimensions changed")
                return dict(image=array, width=array.shape[1], label=labels[r["id"]], script_class=r["script_class"])
        path = harm_out / (arm + ".jsonl")
        counter, arm_rows, arm_start = iter(ordered), [], time.monotonic()
        with path.open("x") as stream:
            def collect(ref, hyp, edits):
                r = next(counter)
                value = dict(id=r["id"], ref=ref, prediction=hyp, edits=edits, ref_len=len(ref))
                arm_rows.append(value)
                stream.write(run.dump_row(value))
                if len(arm_rows) % 100 == 0:
                    stream.flush()
                    print("HARM", arm, len(arm_rows), "/", len(selected), round(time.monotonic()-arm_start, 1), flush=True)
            loader = DataLoader(Crops(), batch_size=16, shuffle=False, collate_fn=collate_strips, num_workers=0)
            result = evaluate(model, loader, codec, device, amp_dtype=amp_dtype_for(device), per_script=True, line_callback=collect)
        if result["n_lines"] != len(selected) or len(arm_rows) != len(selected):
            raise RuntimeError("evaluator omitted lines")
        predictions[arm] = {r["id"]: r for r in arm_rows}
        run.write_json(harm_out / (arm + ".receipt.json"), dict(result=result, seconds=time.monotonic()-arm_start,
                       predictions_sha256=run.sha(path), binding_sha256=run.sha(harm_out / "binding.json")))
    paired, mismatches = [], []
    for r in selected:
        original, masked = (predictions[a][r["id"]] for a in ("original", "masked"))
        if original["ref"] != masked["ref"]:
            raise RuntimeError("paired references differ")
        if not r["changed"] and original != masked:
            mismatches.append(r["id"])
        paired.append(dict(id=r["id"], wave=r["wave"], page=r["page"], script_class=r["script_class"],
                           match_status=r["match_status"], candidate_count=r["candidate_count"], changed=r["changed"],
                           original_edits=original["edits"], masked_edits=masked["edits"], ref_len=original["ref_len"],
                           original_prediction=original["prediction"], masked_prediction=masked["prediction"]))
    run.write_rows(harm_out / "paired.jsonl", paired)
    overall = metrics(paired, replicates, seed)
    by_wave = {w: metrics([r for r in paired if r["wave"] == w], replicates, seed) for w in sorted(quotas)}
    by_script = {s: metrics([r for r in paired if r["script_class"] == s], replicates, seed)
                 for s in sorted({r["script_class"] for r in paired})}
    passed = overall["masked_edits"] <= overall["original_edits"] and not mismatches
    result = dict(schema="t6c2-harm-1", status="completed", gate="pass" if passed else "fail",
                  gate_rule="Overall paired CER must not get worse; per-wave results reported either way; unchanged predictions must be identical",
                  test_mode=receipt["test_mode"], production_gate=passed and not receipt["test_mode"] and len(selected) == 10000,
                  policy=run.POLICY, overall=overall, per_wave=by_wave, per_script_class=by_script,
                  unchanged=dict(lines=sum(not r["changed"] for r in selected), identical_predictions=not mismatches, mismatch_ids=mismatches),
                  per_wave_matching_population=matching_counts(records), per_wave_matching_sample=matching_counts(selected),
                  bootstrap_seed=seed, bootstrap_replicates=replicates, wall_seconds=time.monotonic()-start,
                  binding_sha256=run.sha(harm_out / "binding.json"), paired_sha256=run.sha(harm_out / "paired.jsonl"))
    run.write_json(harm_out / "harm_receipt.json", result)
    report = ["# T6c2 paired harm test", "", f"Gate: **{result['gate']}**; production gate: **{result['production_gate']}**. Test mode: {result['test_mode']}.",
              "", run.POLICY, "", "CER and intervals are fractions; delta = masked minus original. Paired percentile 95% CIs use 2,000 resamples by default. Page units include wave and page identity.",
              "", "| Slice | Lines / pages | Original CER | Masked CER | Delta | Line delta 95% CI | Page delta 95% CI |", "|---|---:|---:|---:|---:|---|---|"]
    for name, m in [("overall", overall), *[("wave: "+w, m) for w, m in by_wave.items()], *[("script: "+s, m) for s, m in by_script.items()]]:
        report.append(f"| {name} | {m['lines']} / {m['pages']} | {m['original_cer']:.6f} | {m['masked_cer']:.6f} | {m['delta_masked_minus_original']:+.6f} | {m['line_bootstrap_95_ci']['delta_masked_minus_original']} | {m['page_cluster_bootstrap_95_ci']['delta_masked_minus_original']} |")
    report += ["", "Full original/masked/delta CIs and matching counts: `harm_receipt.json`.",
               f"Unchanged crop predictions: {result['unchanged']['lines']} checked; identical: {not mismatches}.", "", "| Wave | Ambiguous population / sample | Unmatched population / sample |", "|---|---:|---:|"]
    for w in run.WAVES:
        a, b = result["per_wave_matching_population"][w], result["per_wave_matching_sample"][w]
        report.append(f"| {w} | {a['ambiguous']} / {b['ambiguous']} | {a['unmatched']} / {b['unmatched']} |")
    with (harm_out / "REPORT.md").open("x") as stream:
        stream.write("\n".join(report) + "\n")
    print(json.dumps(dict(gate=result["gate"], production_gate=result["production_gate"], overall=overall,
                          unchanged=result["unchanged"], wall_seconds=result["wall_seconds"])), flush=True)
    return 0 if passed else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=run.OUTPUT, help="existing masking output")
    parser.add_argument("--sample-size", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=run.SEED)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--max-seconds", type=int, default=run.MAX_SECONDS)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    run.low_priority()
    if not 1 <= args.max_seconds <= run.MAX_SECONDS or args.bootstrap < 100 or args.sample_size < 1:
        parser.error("require budget 1..5400, bootstrap >=100 and positive sample size")
    output = run.validate_output(args.out, test=True)
    harm_out = output / "harm"
    if not args.worker:
        verify_mask_output(output)
        harm_out.mkdir(exist_ok=False)
        (harm_out / "tmp").mkdir()
    run.io_guard(harm_out)
    if args.worker:
        return infer(output, harm_out, args.sample_size, args.seed, args.bootstrap)
    watchdog = run.Watchdog(harm_out, args.max_seconds)
    watchdog.start()
    started = time.monotonic()
    try:
        with (harm_out / "worker.log").open("xb") as log:
            with watchdog.lock:
                process = subprocess.Popen([sys.executable, "-B", str(HERE / "harm.py"), "--out", str(output),
                                            "--sample-size", str(args.sample_size), "--seed", str(args.seed),
                                            "--bootstrap", str(args.bootstrap), "--worker"],
                                           cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                watchdog.processes[process.pid] = process
            code = process.wait()
    finally:
        if any(p.poll() is None for p in watchdog.processes.values()):
            watchdog.terminate()
        watchdog.stop()
    run.write_json(harm_out / "process_receipt.json", dict(exit_code=code, stop_reason=watchdog.reason,
                   wall_seconds=time.monotonic()-started, minimum_free_bytes=watchdog.minimum_free_bytes,
                   disk_floor_bytes=run.DISK_FLOOR, watchdog_samples=watchdog.samples, nice=run.low_priority(), network="OFF"))
    print("Harm exit", code, "receipt:", harm_out / "harm_receipt.json", flush=True)
    return code if code >= 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

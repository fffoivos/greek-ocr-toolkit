"""Offline T6c1 pilot. One fresh, low-priority worker per page; never resumes.

Run from the worktree with:
  nice -n 15 .venv/bin/python -B docs/harvest/recut_v1/v2_pilot/run.py

Data, logs, manifests and receipts go exclusively to the fixed external pilot
directory. Only the explicitly requested PILOT.md copy goes into this worktree.
"""
from __future__ import annotations

import os
import sys

sys.dont_write_bytecode = True
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[_name] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

import argparse
import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import random
import re
import resource
import shutil
import signal
import statistics
import subprocess
import threading
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
HOME = Path.home()
INPUT = HOME / "Projects/greek-ocr-toolkit/docs/harvest"
OUTPUT = HOME / "Projects/collect-v3-data/v2_masked/pilot"
SCAN = Path("/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/"
            "8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/pages_scan.jsonl")
PARAMS = HERE.parent / "masking/params.json"
PROBE = HERE.parent / "masking/probe.py"
EXPECTED_PARAMS = "801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8"
EXPECTED_LIBRARY = "f203504a8703561569486450d7e725fe7b399cd4c8fbf581b79cd249e3c5aeb5"
DISK_FLOOR = 10_000_000_000
MAX_SECONDS = 55 * 60
WAVES = ("parliament", "vouli")


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def rows(path):
    with Path(path).open() as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def dump_row(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n"


def low_priority():
    # macOS sandbox can deny nice(1) but still execute its command. Fail closed
    # before reading the collection or importing the detector in that case.
    priority = os.getpriority(os.PRIO_PROCESS, 0)
    if priority < 15:
        raise RuntimeError(f"nice priority {priority}; require at least 15; no processing started")
    return priority


def install_io_guard():
    if OUTPUT.resolve() != OUTPUT or not OUTPUT.is_dir():
        raise RuntimeError("pilot directory must already exist without symlink ancestors")

    def writable(path):
        if isinstance(path, int):
            return
        target = Path(os.fsdecode(path)).absolute().resolve()
        if target == HERE / "PILOT.md":
            return  # The sole explicitly authorized worktree report copy.
        if not target.is_relative_to(OUTPUT):
            raise PermissionError(f"T6c1 write outside pilot: {target}")

    def audit(event, args):
        if event in ("socket.connect", "socket.getaddrinfo", "socket.bind"):
            raise PermissionError("T6c1 network OFF")
        if event == "open":
            path, mode, flags = args
            if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
                writable(path)
        elif event in ("os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.truncate"):
            writable(args[0])
        elif event in ("os.rename", "os.link", "os.symlink"):
            writable(args[0])
            writable(args[1])
    sys.addaudithook(audit)


def frozen():
    value = json.loads(PARAMS.read_text())
    actual = hashlib.sha256(json.dumps(value["params"], sort_keys=True,
                                      separators=(",", ":")).encode()).hexdigest()
    if actual != EXPECTED_PARAMS or value["params_sha256"] != actual:
        raise RuntimeError("frozen parameters changed")
    for name, expected in value["source_hashes"].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError(f"frozen source changed: {name}")
    if sha(ROOT / "greekocr/glyphs/foreign_ink.py") != EXPECTED_LIBRARY:
        raise RuntimeError("frozen masking library changed")
    # Bind the actual original matching functions, without importing probe's
    # F2-only module, which would read unrelated F2 artifacts at import time.
    original = subprocess.check_output(
        ["git", "show", "eacb5c39:docs/harvest/recut_v1/masking/probe.py"], cwd=ROOT)
    if hashlib.sha256(original).hexdigest() != sha(PROBE):
        raise RuntimeError("T6a2 matching source changed")
    return dict(params_sha256=actual, params_file_sha256=sha(PARAMS),
                source_hashes=value["source_hashes"], matcher_sha256=sha(PROBE),
                runner_sha256=sha(__file__))


class Watchdog:
    """Monitor HOME every second; kill only this pilot's current process group."""

    def __init__(self):
        self.deadline = time.monotonic() + MAX_SECONDS
        self.done = threading.Event()
        self.lock = threading.Lock()
        self.process = None
        self.reason = None
        self.minimum_free_bytes = shutil.disk_usage(HOME).free
        self.samples = 0
        self.thread = threading.Thread(target=self.watch, daemon=True)

    def check(self):
        free = shutil.disk_usage(HOME).free
        self.minimum_free_bytes = min(self.minimum_free_bytes, free)
        self.samples += 1
        if free < DISK_FLOOR:
            self.reason = f"disk_below_10_GB: {free} bytes"
        elif time.monotonic() >= self.deadline:
            self.reason = "55_minute_run_budget"
        return self.reason

    def watch(self):
        while not self.done.is_set():
            if self.check():
                with self.lock:
                    process = self.process
                    if process is not None and process.poll() is None:
                        try:
                            os.killpg(process.pid, signal.SIGTERM)
                        except ProcessLookupError:
                            return
                        try:
                            process.wait(timeout=2)
                        except subprocess.TimeoutExpired:
                            try:
                                os.killpg(process.pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                            process.wait()
                return
            self.done.wait(1)

    def start(self):
        if self.check():
            raise RuntimeError(self.reason)
        self.thread.start()

    def stop(self):
        self.done.set()
        if self.thread.is_alive():
            self.thread.join(timeout=3)


def sample():
    manifest = INPUT / "collection/v2/import_real_v2_test.jsonl"
    groups = defaultdict(list)
    for row in rows(manifest):
        if row["wave"] not in WAVES:
            continue
        if row["split"] not in ("test", "reserved"):
            raise RuntimeError("non-test row in test manifest")
        crop = Path(row["crop"])
        number = re.fullmatch(r"p(\d+)-l\d+\.png", crop.name)
        if number is None:
            raise RuntimeError(f"unrecognised crop path: {crop}")
        groups[(row["wave"], crop.parent.name, int(number[1]))].append(row)
    scan = {(r["wave"], r["doc"], r["page"]): r for r in rows(SCAN)}
    rng = random.Random("t6c1")
    selected = {}
    for wave in WAVES:
        candidates = sorted(key for key in groups if key[0] == wave)
        selected[wave] = rng.sample(candidates, 10)
    # Interleave waves; one active page means a failure cannot overshoot into
    # another page. A stopped sample is never silently replenished.
    keys = [selected[wave][i] for i in range(10) for wave in WAVES]
    wanted = {r["id"] for key in keys for r in groups[key]}
    admitted = {}
    bindings = {str(manifest): sha(manifest), str(SCAN): sha(SCAN)}
    for wave in WAVES:
        path = INPUT / wave / "admitted.jsonl"
        bindings[str(path)] = sha(path)
        for row in rows(path):
            if row["id"] in wanted:
                if row["id"] in admitted:
                    raise RuntimeError("duplicate admitted line id")
                admitted[row["id"]] = row
    pages = []
    for wave, doc, number in keys:
        observation = scan[(wave, doc, number)]
        page = dict(wave=wave, doc=doc, page=number, page_id=f"{doc}-p{number:06d}",
                    raster=str(INPUT / observation["path"]), scan=observation, lines=[])
        for row in groups[(wave, doc, number)]:
            saved = admitted[row["id"]]
            if saved["split"] != "test" or saved["crop_path"] != row["crop"]:
                raise RuntimeError(f"test/crop binding mismatch: {row['id']}")
            page["lines"].append(dict(id=row["id"], crop=row["crop"],
                                      crop_bbox=saved["crop_bbox"],
                                      crop_sha256=saved["crop_sha256"]))
        pages.append(page)
    if len(wanted) != sum(len(p["lines"]) for p in pages):
        raise RuntimeError("duplicate test line ids")
    return pages, bindings


def matcher():
    import numpy as np
    from greekocr.glyphs.recut import LineFit
    tree = ast.parse(PROBE.read_text(), filename=str(PROBE))
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name in ("match", "runtime_fit")]
    if len(functions) != 2:
        raise RuntimeError("missing original matching functions")
    namespace = dict(np=np, LineFit=LineFit)
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(PROBE), "exec"), namespace)
    return namespace["match"], namespace["runtime_fit"]


def candidate_diagnostics(box, fits):
    import numpy as np
    x0, y0, x1, y1 = box
    xs = np.arange(x0, x1, dtype=float)
    candidates = []
    for i, fit in enumerate(fits):
        overlap = max(0, min(x1, fit.x1) - max(x0, fit.x0)) / (x1 - x0)
        if overlap < .5:
            continue
        distance = abs(float(np.median(fit.base_at(xs))) - (y0 + y1) / 2) / max(1, fit.xh)
        if distance <= 1.5:
            candidates.append(dict(index=i, distance_xh=distance, overlap=overlap))
    return sorted(candidates, key=lambda r: (r["distance_xh"], r["index"]))


def line_failures(index, candidates, original_sha, stored_sha, expected_sha, pixel_equal):
    failures = []
    if index is None:
        failures.append("unmatched")
    elif len(candidates) > 1:
        failures.append("ambiguous")
    if original_sha != expected_sha:
        failures.append("recut_sha_mismatch")
    if stored_sha != expected_sha or not pixel_equal:
        failures.append("stored_crop_mismatch")
    return failures


def page_stop_reason(result):
    name = result["wave"] + "--" + result["page_id"]
    reasons = []
    if result["match_failures"]:
        reasons.append(f"line_curve_matching_failure: {name} ({result['match_failures']} lines)")
    if result["wave"] == "parliament" and max(result["page_seconds"], result["worker_wall_seconds"]) > 60:
        reasons.append(f"parliament_page_over_60_seconds: {name}")
    return "; ".join(reasons) or None


def worker(index):
    import numpy as np
    from PIL import Image
    from greekocr.glyphs.foreign_ink import PARAMETERS, prepare_mask_page, mask_foreign_ink
    from greekocr.pages import process_page

    binding = frozen()
    if PARAMETERS != json.loads(PARAMS.read_text())["params"]:
        raise RuntimeError("live parameters differ from freeze")
    selected = json.loads((OUTPUT / "sample.json").read_text())[index]
    name = selected["wave"] + "--" + selected["page_id"]
    started = time.perf_counter()
    native_path = Path(selected["raster"])
    if not native_path.resolve().is_relative_to(INPUT.resolve()):
        raise RuntimeError("raster outside read-only harvest inputs")
    if sha(native_path) != selected["scan"]["sha"]:
        raise RuntimeError("page raster differs from feasibility scan")
    with Image.open(native_path) as opened:
        native = opened.copy()
    if (native.width, native.height, native.mode) != (
            selected["scan"]["w"], selected["scan"]["h"], selected["scan"]["mode"]):
        raise RuntimeError("raster header differs from feasibility scan")
    detect_started = time.perf_counter()
    analysis = process_page(native)
    detector_seconds = time.perf_counter() - detect_started
    mask_started = time.perf_counter()
    lines = [line for line in analysis.segmentation.lines if line.discounted is None]
    match, runtime_fit = matcher()
    fits = [runtime_fit(line) for line in lines]
    prepared = prepare_mask_page(native)
    curves = [dict(x0=line.x0, x1=line.x1, xheight=line.xheight,
                   baseline=line.baseline.tolist(), meanline=line.meanline.tolist()) for line in lines]
    curve_path = OUTPUT / "curves" / (name + ".json.gz")
    curve_path.write_bytes(gzip.compress(json.dumps(curves, allow_nan=False).encode(), mtime=0))
    records = []
    records_path = OUTPUT / "lines" / (name + ".jsonl")
    with records_path.open("x") as stream:
        for row in selected["lines"]:
            box = row["crop_bbox"]
            original = native.crop(tuple(box))
            buffer = io.BytesIO()
            original.save(buffer, format="PNG", compress_level=3)
            original_sha = hashlib.sha256(buffer.getvalue()).hexdigest()
            stored_path = ROOT.parent / "greek-ocr-toolkit" / row["crop"]
            if not stored_path.resolve().is_relative_to(INPUT.resolve()):
                raise RuntimeError("crop outside read-only harvest inputs")
            stored_sha = sha(stored_path)
            with Image.open(stored_path) as stored:
                pixel_equal = stored.mode == original.mode and stored.size == original.size and np.array_equal(
                    np.asarray(stored), np.asarray(original))
            index = match(box, fits)  # Execute T6a2's exact function unchanged.
            x0, y0, x1, y1 = box
            candidates = candidate_diagnostics(box, fits)
            if index != (candidates[0]["index"] if candidates else None):
                raise RuntimeError("candidate diagnostics differ from original matcher")
            failures = line_failures(index, candidates, original_sha, stored_sha, row["crop_sha256"], pixel_equal)
            if failures:
                # Finish this page with explicit identity proposals for failures;
                # no invented curve and no arbitrary ambiguous choice is applied.
                image = original
                mask = np.zeros((y1-y0, x1-x0), dtype=bool)
                record = dict(crop_box=box, masked_pixel_count=0, proposed_masked_pixel_count=0,
                              masked_component_count=0, ring_median=None, ring_spread=None,
                              fills=[], empty_ring_abstentions=0, changed=False,
                              native_changed_pixels=0, mask_sha256=hashlib.sha256(mask.tobytes()).hexdigest())
            else:
                result = mask_foreign_ink(prepared, lines[index], lines, box)
                image, record = result.image, result.record
            dest = OUTPUT / "crops" / selected["wave"] / selected["doc"] / Path(row["crop"]).name
            dest.parent.mkdir(parents=True, exist_ok=True)
            image.save(dest, format="PNG", compress_level=3)
            record.update(id=row["id"], wave=selected["wave"], page_id=selected["page_id"],
                          original_crop_sha256=original_sha, stored_crop_sha256=stored_sha,
                          admitted_crop_sha256=row["crop_sha256"], recut_pixels_equal=pixel_equal,
                          masked_sha256=sha(dest), masked_path=str(dest.relative_to(OUTPUT)),
                          runtime_index=index, candidates=candidates, match_status="ok" if not failures else "+".join(failures),
                          failures=failures, mask_applied=not failures,
                          curves_path=str(curve_path.relative_to(OUTPUT)))
            if not record["changed"] and record["masked_sha256"] != original_sha:
                raise RuntimeError("identity PNG encoding mismatch")
            stream.write(dump_row(record))
            stream.flush()
            records.append(record)
    masking_seconds = time.perf_counter() - mask_started
    result = dict(wave=selected["wave"], page_id=selected["page_id"], status="completed",
                  megapixels=native.width*native.height/1e6, detector_seconds=detector_seconds,
                  masking_seconds=masking_seconds, page_seconds=time.perf_counter()-started,
                  lines=len(records), changed=sum(r["changed"] for r in records),
                  match_failures=sum(bool(r["failures"]) for r in records),
                  failure_kinds=dict(Counter(f for r in records for f in r["failures"])),
                  detector_curves=len(lines), worker_pid=os.getpid(), nice=low_priority(),
                  peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024),
                  binding=binding, curves_sha256=sha(curve_path),
                  records_path=str(records_path.relative_to(OUTPUT)), records_sha256=sha(records_path))
    write_json(OUTPUT / "pages" / (name + ".json"), result)


def report(pages, results, binding, watchdog, reason, started):
    complete = [p for p in results if p.get("status") == "completed"]
    summaries = {}
    for wave in WAVES:
        subset = [p for p in complete if p["wave"] == wave]
        times = [p["page_seconds"] for p in subset]
        count = sum(p["lines"] for p in subset)
        changed = sum(p["changed"] for p in subset)
        summaries[wave] = dict(pages=len(subset), lines=count, changed=changed,
                               changed_percent=100*changed/count if count else None,
                               seconds_median=statistics.median(times) if times else None,
                               seconds_max=max(times) if times else None,
                               peak_rss_bytes=max((p["peak_rss_bytes"] for p in subset), default=None),
                               match_failures=sum(p["match_failures"] for p in subset))
    failures = sum(p["match_failures"] for p in complete)
    count = sum(p["lines"] for p in complete)
    changed = sum(p["changed"] for p in complete)
    verdict = "go" if len(complete) == 20 and not reason and not failures else "stop"
    receipt = dict(schema="t6c1-pilot-1", started_utc=started, finished_utc=utc(),
                   seed="t6c1", selected_pages=len(pages), completed_pages=len(complete),
                   results=results, summaries=summaries, match_failures=failures,
                   lines=count, changed=changed, changed_percent=100*changed/count if count else None,
                   verdict=verdict, stop_reason=reason, binding=binding, workers_max=1,
                   threads_per_worker=1, network="OFF", disk_floor_bytes=DISK_FLOOR,
                   minimum_free_bytes=watchdog.minimum_free_bytes, watchdog_samples=watchdog.samples,
                   watchdog_interval_seconds=1, run_budget_seconds=MAX_SECONDS,
                   timing="page_seconds includes raster custody/decode, detector, matching, masking and crop/curve I/O; worker_wall_seconds also includes interpreter/import startup",
                   ambiguity="more than one curve meets the unchanged T6a2 eligibility gates; preserve its ranked winner for diagnosis and emit an identity proposal")
    write_json(OUTPUT / "pilot_receipt.json", receipt)
    completed_by_key = {(p["wave"], p["page_id"]): p for p in results}
    lines = ["# T6c1 large-page masking pilot", "", f"Verdict: **{verdict}**. Completed {len(complete)}/20 selected pages.",
             f"Stop reason: {reason or 'none'}.", "", "Seed: `t6c1`; sorted test-page population, Python Random.sample: parliament then vouli; alternating execution order.",
             "One fresh worker per page, nice >=15, one numerical thread. All data are external; original crops are read-only.",
             "Timing includes native raster custody/decode, detector, matching, masking and output I/O; worker wall time additionally includes startup. The parliament stop gate checks both times.",
             "Matching executes T6a2's exact functions. Multiple eligible curves are conservatively ambiguous; failure rows receive explicit identity proposals. Failure counts are distinct affected lines.",
             "", "| Wave | Page | Status | MP | Detector s | Masking s | Page s | Worker wall s | Peak RSS MiB | Lines | Changed | Failures |",
             "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for p in pages:
        r = completed_by_key.get((p["wave"], p["page_id"]))
        if r is None or r.get("status") != "completed":
            lines.append(f"| {p['wave']} | {p['page_id']} | {r.get('status') if r else 'not run'} | — | — | — | — | — | — | — | — | — |")
        else:
            lines.append(f"| {r['wave']} | {r['page_id']} | completed | {r['megapixels']:.3f} | {r['detector_seconds']:.3f} | {r['masking_seconds']:.3f} | {r['page_seconds']:.3f} | {r['worker_wall_seconds']:.3f} | {r['peak_rss_bytes']/2**20:.1f} | {r['lines']} | {r['changed']} | {r['match_failures']} |")
    lines += ["", "| Wave | Pages | Median/max s | Lines | Changed | Matching failures |", "|---|---:|---|---:|---:|---:|"]
    def fmt(value):
        return f"{value:.3f}" if value is not None else "n/a"
    for wave, s in summaries.items():
        lines.append(f"| {wave} | {s['pages']} | {fmt(s['seconds_median'])}/{fmt(s['seconds_max'])} | {s['lines']} | {fmt(s['changed_percent'])}% | {s['match_failures']} |")
    a, b = summaries["parliament"], summaries["vouli"]
    completion = "done" if len(complete) == 20 or (reason and "line_curve_matching_failure" in reason) or (reason and "parliament_page_over_60_seconds" in reason) else "blocked"
    final = (f"T6c1: {completion} | pages: {len(complete)} | parliament s/page median/max: {fmt(a['seconds_median'])}/{fmt(a['seconds_max'])}"
             f" | vouli s/page median/max: {fmt(b['seconds_median'])}/{fmt(b['seconds_max'])} | match failures: {failures}"
             f" | changed: {fmt(receipt['changed_percent'])}% | verdict: {verdict}")
    lines += ["", f"Frozen params: `{EXPECTED_PARAMS}`; library: `{EXPECTED_LIBRARY}`.",
              f"Minimum free disk: {watchdog.minimum_free_bytes/1e9:.3f} GB ({watchdog.samples} checks).",
              "The verdict concerns this pilot only. T6c2 remains pending; all-v2 processing requires the owner's explicit go.",
              "", final]
    (OUTPUT / "PILOT.md").write_text("\n".join(lines) + "\n")
    (HERE / "PILOT.md").write_bytes((OUTPUT / "PILOT.md").read_bytes())
    print(final, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()
    low_priority()
    install_io_guard()
    sys.path.insert(0, str(ROOT))
    if args.worker is not None:
        worker(args.worker)
        return
    started = utc()
    watchdog = Watchdog()
    pages, results, binding, reason = [], [], {}, None
    # Exclusive marker prevents concurrent starts and accidental reruns. Never
    # take a W1 lock. Preserve partial output rather than silently resuming it.
    with (OUTPUT / "pilot_started.json").open("x") as stream:
        stream.write(dump_row(dict(pid=os.getpid(), utc=started, nice=low_priority())))
    try:
        watchdog.start()
        binding = frozen()
        pages, inputs = sample()
        if watchdog.reason:
            raise RuntimeError(watchdog.reason)
        binding["inputs"] = inputs
        binding["python"] = sys.version
        binding["base_head"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
        write_json(OUTPUT / "sample.json", pages)
        for directory in ("pages", "curves", "crops", "lines", "logs"):
            (OUTPUT / directory).mkdir()
        write_json(OUTPUT / "input_bindings.json", binding)
        for i, page in enumerate(pages):
            if watchdog.check():
                reason = watchdog.reason
                break
            name = page["wave"] + "--" + page["page_id"]
            start = time.perf_counter()
            with (OUTPUT / "logs" / (name + ".log")).open("x") as log:
                with watchdog.lock:
                    if watchdog.reason:
                        reason = watchdog.reason
                        break
                    process = subprocess.Popen([sys.executable, "-B", str(Path(__file__).resolve()), "--worker", str(i)],
                                               cwd=OUTPUT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                    watchdog.process = process
                code = process.wait()
                with watchdog.lock:
                    watchdog.process = None
            path = OUTPUT / "pages" / (name + ".json")
            if code != 0 or not path.exists():
                results.append(dict(wave=page["wave"], page_id=page["page_id"], status="interrupted" if watchdog.reason else "worker_error", returncode=code))
                reason = watchdog.reason or f"worker_error: {name}, exit {code}"
                break
            result = json.loads(path.read_text())
            result["worker_wall_seconds"] = time.perf_counter() - start
            write_json(path, result)
            results.append(result)
            print(dump_row(result | {"binding": "input_bindings.json"}), end="", flush=True)
            reason = page_stop_reason(result) or watchdog.reason
            if reason:
                break
    except Exception as exc:
        reason = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    finally:
        watchdog.stop()
    report(pages, results, binding, watchdog, reason or watchdog.reason, started)


if __name__ == "__main__":
    main()

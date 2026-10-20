"""Offline T6c2 masking. Fresh processes/pages and fresh output directories only."""
from __future__ import annotations

import os
import sys

sys.dont_write_bytecode = True
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[_name] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import random
import re
import resource
import shutil
import signal
import subprocess
import threading
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
HOME = Path.home()
HARVEST = HOME / "Projects/greek-ocr-toolkit/docs/harvest"
OCR = HOME / "Projects/greek-page-ocr"
OUTPUT = HOME / "Projects/collect-v3-data/v2_masked/v2_test"
TEST_OUTPUT = HERE / "test-out"
PAGE_INDEX = HERE / "page_index.jsonl"
FACTORY = OCR / "factory/target/release/linefactory"
spec = importlib.util.spec_from_file_location("t6c1_pilot", HERE.parent / "v2_pilot/run.py")
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)
sha, rows, dump_row, utc, low_priority = pilot.sha, pilot.rows, pilot.dump_row, pilot.utc, pilot.low_priority
WAVES = ("round1", "round2", "mixed", "vouli", "openarchives", "cyrillic", "wikisource")
DISK_FLOOR = 10_000_000_000
MAX_SECONDS = 90 * 60
SEED = 20261017
POLICY = "Pilot zero-ambiguity rule retired in favour of paired harm test; ambiguous lines use T6a2 nearest curve; unmatched lines remain unmasked. Parliament excluded pending separate matching fix."
EXPECTED_WAVES = {"round1": (8083, 188), "round2": (3651, 75), "mixed": (2151, 67),
                  "vouli": (1739, 49), "openarchives": (4642, 154), "cyrillic": (346, 21),
                  "wikisource": (9490, 342), "parliament": (11936, 99)}
PINS = {
    HARVEST / "collection/v2/import_real_v2_test.jsonl": "e7a4f4025adde53b8a5e7894f87bde3b12d7730e893d2f1b78dc4e78b83c00f8",
    OCR / "out/e3d/prepare/instrument_exclusions.jsonl": "3f1683e479f6a8a551d45c556cfc44c9f585a636f0af6bd38c086fca62a8b636",
    OCR / "out/e3_dryrun2/records/v2_test.jsonl": "3770e30dc0b4ca342323120336253f3d311d7138352f767b38198a4733091e82",
    OCR / "codec/v1.json": "d1b7e2d40565e89e699f748692265e06e2d7028409b78d02d6df6f89b2e82a86",
    OCR / "factory/src/codec.rs": "420d48331a669483e941e67f4376e0b329b04d7bd30794b6c9db204300d8f4ec",
    OCR / "bench/o5_prepare.py": "14bd3147dfe5cd2ed71bce69b5a2859ce65296c07457c31082864711ab5211e5",
    OCR / "bench/codec_coverage.py": "45ab84733caa432eb08eb639fe4c9260286d4e1b1594ecb8b9dbffb6febc237f",
    PAGE_INDEX: "d18af4c743d521b79a3c43e050be6c752967006bfe975fdb919b5af99cc48c56",
    FACTORY: "81847dcd6b94967b3225fa4aaae617fe6c09e2a54512f880f97081c1cd2b2b19",
}


def write_json(path, value):
    with Path(path).open("x") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def write_rows(path, records):
    with Path(path).open("x") as stream:
        for row in records:
            stream.write(dump_row(row))


def frozen():
    binding = pilot.frozen()
    binding.update(pilot_runner_sha256=sha(pilot.__file__), runner_sha256=sha(__file__))
    for path, expected in PINS.items():
        if sha(path) != expected:
            raise RuntimeError(f"frozen input changed: {path}")
    binding["inputs"] = {str(p): digest for p, digest in PINS.items()}
    return binding


def io_guard(output):
    """Permit writes only in this fresh output, deny network, including DNS."""
    if output.resolve() != output or not output.is_dir():
        raise RuntimeError("output must exist without symlink ancestors")
    def writable(path):
        if isinstance(path, int) or os.fsdecode(path) == os.devnull:
            return  # Torch/dill opens this device to identify Python file types.
        if not Path(os.fsdecode(path)).absolute().resolve().is_relative_to(output):
            raise PermissionError(f"T6c2 write outside output: {path}")
    def audit(event, args):
        if event in ("socket.connect", "socket.getaddrinfo", "socket.bind", "socket.sendto"):
            raise PermissionError("T6c2 network OFF")
        if event == "open":
            if args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
                writable(args[0])
        elif event in ("os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.truncate"):
            writable(args[0])
        elif event in ("os.rename", "os.link", "os.symlink"):
            writable(args[0]); writable(args[1])
    sys.addaudithook(audit)
    os.environ["TMPDIR"] = str(output / "tmp")
    os.environ["XDG_CACHE_HOME"] = str(output / "tmp")


def validate_output(output, test=False):
    output = Path(output).expanduser().absolute()
    if output.resolve() != output:
        raise ValueError("symlink output/ancestor forbidden")
    if output.is_relative_to(ROOT):
        if not test or not output.is_relative_to(TEST_OUTPUT):
            raise ValueError("checkout outputs allowed only below ignored test-out in test mode")
    if output.is_relative_to(HARVEST) or output.is_relative_to(OCR):
        raise ValueError("output overlaps immutable inputs/evaluation")
    return output


def page_key(row):
    crop = Path(row["crop"])
    match = re.fullmatch(r"p(\d+)-l\d+\.png", crop.name)
    if match is None:
        raise ValueError(f"unrecognised crop: {crop}")
    return row["wave"], crop.parent.name, int(match[1])


def population():
    """Bind E3's actual rejection identities, and independently reproduce codec coverage."""
    frozen()
    sys.path.insert(0, str(OCR))
    from bench.o5_prepare import codec_tables, normalize
    atoms, folds = codec_tables()
    manifest, excluded_file, template_file = list(PINS)[:3]
    original = list(rows(manifest))
    excluded = [r["line_id"] for r in rows(excluded_file) if r["instrument"] == "v2_test"]
    bad = set(excluded)
    if len(excluded) != 1991 or len(bad) != 1991:
        raise RuntimeError("E3 rejection inventory is not exactly 1,991 unique lines")
    ids = {r["id"] for r in original}
    if len(ids) != len(original) or not bad <= ids:
        raise RuntimeError("duplicate source ids or unknown exclusions")
    actual_bad = {r["id"] for r in original if set(normalize(r["label"], folds)) - atoms.keys()}
    if actual_bad != bad:
        raise RuntimeError("E3 exclusion list differs from unchanged v1 codec coverage")
    retained = [r for r in original if r["id"] not in bad]
    counts = {wave: dict(lines=sum(r["wave"] == wave for r in retained),
                        pages=len({page_key(r) for r in retained if r["wave"] == wave}))
              for wave in EXPECTED_WAVES}
    if len(retained) != 42038 or len({page_key(r) for r in retained}) != 995:
        raise RuntimeError("pre-parliament population must be 42,038 lines / 995 pages")
    if counts != {w: dict(zip(("lines", "pages"), n)) for w, n in EXPECTED_WAVES.items()}:
        raise RuntimeError("per-wave population drift")
    templates = {r["line_id"]: r for r in rows(template_file)}
    if set(templates) != ids:
        raise RuntimeError("E3 projected import ids differ from collection feed")
    for r in original:
        t = templates[r["id"]]
        if (t["text"], t["script_class"], t["source_doc_id"], t["split"], t["crop"]) != (
                r["label"], r["script_class"], r["doc"], "reserved",
                str(Path(r["wave"]) / Path(r["crop"]).parent.name / Path(r["crop"]).name)):
            raise RuntimeError("E3 import projection differs: " + r["id"])
    retained = [r for r in retained if r["wave"] != "parliament"]
    summary = dict(raw_lines=len(original), codec_excluded=1991, before_parliament=dict(lines=42038, pages=995),
                   per_wave=counts, excluded_parliament=counts["parliament"], lines=len(retained),
                   pages=len({page_key(r) for r in retained}))
    return retained, templates, summary


def select_pages(records, test_pages=0):
    groups = defaultdict(list)
    for row in records:
        groups[page_key(row)].append(row)
    rng = random.Random(SEED)
    keys = []
    for wave in WAVES:
        candidates = sorted(k for k in groups if k[0] == wave)
        keys.extend(rng.sample(candidates, test_pages) if test_pages else candidates)
    scan = {(r["wave"], r["doc"], r["page"]): r for r in rows(PAGE_INDEX)}
    if set(scan) != set(groups):
        raise RuntimeError("frozen page catalogue differs from eligible population")
    wanted = {r["id"] for key in keys for r in groups[key]}
    admitted, bindings = {}, {str(PAGE_INDEX): sha(PAGE_INDEX)}
    for wave in WAVES:
        path = HARVEST / wave / "admitted.jsonl"
        bindings[str(path)] = sha(path)
        for row in rows(path):
            if row["id"] in wanted:
                if row["id"] in admitted:
                    raise RuntimeError("duplicate admitted line")
                admitted[row["id"]] = row
    pages = []
    for wave, doc, number in keys:
        observation = scan[(wave, doc, number)]
        page = dict(wave=wave, doc=doc, page=number, page_id=f"{doc}-p{number:06d}",
                    raster=str(HARVEST / observation["path"]), scan=observation,
                    megapixels=observation["w"]*observation["h"]/1e6, lines=[])
        for row in groups[(wave, doc, number)]:
            saved = admitted[row["id"]]
            if saved["split"] != "test" or saved["crop_path"] != row["crop"]:
                raise RuntimeError("admitted test/crop mismatch: " + row["id"])
            page["lines"].append(dict(id=row["id"], crop=row["crop"], crop_bbox=saved["crop_bbox"],
                                      crop_sha256=saved["crop_sha256"], script_class=row["script_class"]))
        pages.append(page)
    return pages, bindings


def can_launch(active_megapixels, next_megapixels):
    cap = 3 if any(mp > 20 for mp in [*active_megapixels, next_megapixels]) else 6
    return len(active_megapixels) < cap


def match_status(index, candidates):
    return "unmatched" if index is None else "ambiguous" if len(candidates) > 1 else "matched"


class Watchdog:
    def __init__(self, output, seconds):
        self.output, self.deadline = output, time.monotonic() + seconds
        self.done, self.lock = threading.Event(), threading.Lock()
        self.processes, self.reason, self.samples = {}, None, 0
        self.minimum_free_bytes = shutil.disk_usage(output).free
        self.thread = threading.Thread(target=self.watch, daemon=True)

    def check(self):
        free = shutil.disk_usage(self.output).free
        self.minimum_free_bytes = min(self.minimum_free_bytes, free)
        self.samples += 1
        if free < DISK_FLOOR:
            self.reason = f"disk_below_10_GB: {free}"
        elif time.monotonic() >= self.deadline:
            self.reason = "90_minute_or_requested_run_budget"
        return self.reason

    def watch(self):
        while not self.done.wait(1):
            if self.check():
                self.terminate()
                return

    def terminate(self):
        with self.lock:
            processes = list(self.processes.values())
        for process in processes:
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
        deadline = time.monotonic() + 2
        for process in processes:
            try:
                process.wait(timeout=max(0, deadline-time.monotonic()))
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()

    def start(self):
        if self.check():
            raise RuntimeError(self.reason)
        self.thread.start()

    def stop(self):
        self.done.set()
        self.thread.join(timeout=3)


def worker(output, index):
    import numpy as np
    from PIL import Image
    from greekocr.glyphs.foreign_ink import PARAMETERS, prepare_mask_page, mask_foreign_ink
    from greekocr.pages import process_page
    binding = frozen()
    if PARAMETERS != json.loads(pilot.PARAMS.read_text())["params"]:
        raise RuntimeError("live parameters differ from freeze")
    page = json.loads((output / "selection.json").read_text())[index]
    started = time.monotonic()
    raster = Path(page["raster"])
    if not raster.resolve().is_relative_to(HARVEST.resolve()) or sha(raster) != page["scan"]["sha"]:
        raise RuntimeError("native raster custody mismatch")
    with Image.open(raster) as opened:
        native = opened.copy()
    if (native.width, native.height, native.mode) != (page["scan"]["w"], page["scan"]["h"], page["scan"]["mode"]):
        raise RuntimeError("native raster header mismatch")
    detect = time.monotonic()
    analysis = process_page(native)
    detector_seconds = time.monotonic() - detect
    lines = [line for line in analysis.segmentation.lines if line.discounted is None]
    match, runtime_fit = pilot.matcher()
    fits = [runtime_fit(line) for line in lines]
    prepared = prepare_mask_page(native)
    records = []
    for row in page["lines"]:
        stored_path = HARVEST.parents[1] / row["crop"]
        if not stored_path.resolve().is_relative_to(HARVEST.resolve()):
            raise RuntimeError("stored crop outside immutable harvest")
        stored_sha = sha(stored_path)
        original = native.crop(tuple(row["crop_bbox"]))
        buffer = io.BytesIO()
        original.save(buffer, format="PNG", compress_level=3)
        original_sha = hashlib.sha256(buffer.getvalue()).hexdigest()
        with Image.open(stored_path) as stored:
            equal = stored.mode == original.mode and stored.size == original.size and np.array_equal(np.asarray(stored), np.asarray(original))
        if stored_sha != row["crop_sha256"] or not equal:
            raise RuntimeError("re-cut/stored/admitted custody mismatch: " + row["id"])
        index = match(row["crop_bbox"], fits)
        candidates = pilot.candidate_diagnostics(row["crop_bbox"], fits)
        if index != (candidates[0]["index"] if candidates else None):
            raise RuntimeError("diagnostics disagree with exact T6a2 matcher")
        status = match_status(index, candidates)
        if index is None:
            record = dict(masked_pixel_count=0, proposed_masked_pixel_count=0, masked_component_count=0,
                          ring_median=None, ring_spread=None, fills=[], empty_ring_abstentions=0,
                          changed=False, native_changed_pixels=0)
            masked_path, masked_sha = str(stored_path), stored_sha
        else:
            result = mask_foreign_ink(prepared, lines[index], lines, row["crop_bbox"])
            dest = output / "crops" / page["wave"] / page["doc"] / Path(row["crop"]).name
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("xb") as stream:
                if result.record["changed"]:
                    result.image.save(stream, format="PNG", compress_level=3)
                else:
                    # Native equality is the custody contract. Original PNGs
                    # use several encodings; retain their exact bytes on identity.
                    stream.write(stored_path.read_bytes())
            record, masked_path, masked_sha = result.record, str(dest.relative_to(output)), sha(dest)
        if not record["changed"] and masked_sha != stored_sha:
            raise RuntimeError("unchanged crop encoding differs")
        if sha(stored_path) != stored_sha:
            raise RuntimeError("original crop changed during worker")
        record.update(id=row["id"], wave=page["wave"], page=page["page_id"], page_id=page["page_id"],
                      script_class=row["script_class"], original_path=str(stored_path),
                      original_crop_sha256=original_sha, stored_crop_sha256=stored_sha,
                      admitted_crop_sha256=row["crop_sha256"], recut_pixels_equal=equal,
                      recut_encoded_sha_equal=original_sha == stored_sha,
                      masked_path=masked_path, masked_sha256=masked_sha, match_status=status,
                      candidate_count=len(candidates), candidates=candidates, runtime_index=index,
                      mask_applied=index is not None, crop_box=row["crop_bbox"])
        records.append(record)
    if sha(raster) != page["scan"]["sha"]:
        raise RuntimeError("native raster changed during worker")
    name = page["wave"] + "--" + page["page_id"]
    record_path = output / "page-lines" / (name + ".jsonl")
    write_rows(record_path, records)
    write_json(output / "pages" / (name + ".json"), dict(status="completed", wave=page["wave"],
               page_id=page["page_id"], megapixels=page["megapixels"], lines=len(records),
               detector_seconds=detector_seconds, page_seconds=time.monotonic()-started,
               worker_pid=os.getpid(), nice=low_priority(), binding=binding,
               peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024),
               records_path=str(record_path.relative_to(output)), records_sha256=sha(record_path)))


def import_labels(output, imports):
    """Read actual E3/E4-format shards and verify every reference against codec v1."""
    import pyarrow.parquet as pq
    sys.path.insert(0, str(OCR))
    from bench.o5_prepare import codec_tables, normalize
    atoms, folds = codec_tables()
    labels = {}
    for path in sorted((output / "real_v2_test_masked/reserved").glob("shard-*.parquet")):
        table = pq.read_table(path, columns=["line_id", "label_ids", "gt_nfd", "codec_version", "split", "script_class"])
        for row in table.to_pylist():
            key = row["line_id"]
            if key in labels or key not in imports:
                raise RuntimeError("factory import duplicate/unknown id")
            expected = imports[key]
            text = normalize(expected["text"], folds)
            if (row["gt_nfd"], row["codec_version"], row["split"], row["script_class"], row["label_ids"]) != (
                    text, "v1", "reserved", expected["script_class"], [atoms[c] for c in text]):
                raise RuntimeError("factory shard reference/codec mismatch: " + key)
            labels[key] = row["label_ids"]
    if set(labels) != set(imports):
        raise RuntimeError("factory shard identities differ from masked import")
    return labels


def build_import(output, imports, seconds):
    """Materialize a NEW real_v2_test_masked factory import; no existing eval writes."""
    watchdog = Watchdog(output, max(.001, seconds))
    watchdog.start()
    started = time.monotonic()
    def command(arguments, name):
        if watchdog.check():
            raise RuntimeError(watchdog.reason)
        with (output / "logs" / name).open("xb") as log:
            with watchdog.lock:
                process = subprocess.Popen([str(FACTORY), *map(str, arguments)], cwd=ROOT,
                                           stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
                                           env=dict(os.environ, RAYON_NUM_THREADS="1"))
                watchdog.processes[process.pid] = process
            code = process.wait()
            with watchdog.lock:
                watchdog.processes.pop(process.pid, None)
        if code or watchdog.reason:
            raise RuntimeError(f"factory {name}: exit {code}; {watchdog.reason}; see logs/{name}")
    try:
        emitted = output / "tmp/factory-codec.json"
        command(["codec-emit", "--out", emitted], "factory-codec.log")
        actual, expected = (json.loads(p.read_text()) for p in (emitted, OCR / "codec/v1.json"))
        if (actual["version"], actual["blank_id"], actual["atoms"]) != (expected["version"], expected["blank_id"], expected["atoms"]):
            raise RuntimeError("pinned factory binary codec differs from E3 v1")
        crop_root = Path(os.path.commonpath([output, HARVEST]))
        destination = output / "real_v2_test_masked"
        command(["import-real", "--records", output / "real_v2_test_masked.jsonl", "--crops", crop_root,
                 "--out", destination, "--partition", "collection-v2-test-masked"], "factory-import.log")
        info = json.loads((destination / "build_info.json").read_text())
        expected_shas = {r["id"]: r["masked_sha256"] for r in rows(output / "lines.jsonl")}
        if (info["kind"] != "real" or info["partition_id"] != "collection-v2-test-masked"
                or info["n_records"] != len(imports) or info["n_written"] != len(imports) or info["drop_ledger"]
                or info["records_sha256"] != sha(output / "real_v2_test_masked.jsonl")
                or info["crop_sha256"] != expected_shas):
            raise RuntimeError("factory import counts/drops/crop or manifest hashes differ")
        import_labels(output, {r["line_id"]: r for r in imports})
        # Same reserved/test alias used by the E3 instrument, entirely in NEW output.
        (destination / "test").symlink_to(destination / "reserved", target_is_directory=True)
        return dict(status="completed", lines=info["n_written"], drops=0, codec="v1", crop_root=str(crop_root),
                    seconds=time.monotonic()-started, factory_sha256=sha(FACTORY),
                    emitted_codec_sha256=sha(emitted), build_info_sha256=sha(destination / "build_info.json"),
                    minimum_free_bytes=watchdog.minimum_free_bytes, watchdog_samples=watchdog.samples)
    finally:
        if any(p.poll() is None for p in watchdog.processes.values()):
            watchdog.terminate()
        watchdog.stop()


def run(output, test_pages, seconds):
    started, start = utc(), time.monotonic()
    binding = frozen()
    records, templates, summary = population()
    pages, inputs = select_pages(records, test_pages)
    binding["inputs"].update(inputs)
    write_json(output / "selection.json", pages)
    binding["selection_sha256"] = sha(output / "selection.json")
    watchdog = Watchdog(output, seconds)
    results, active, schedule = [], {}, []
    pending = list(enumerate(pages))
    watchdog.start()
    try:
        while pending or active:
            while pending and not watchdog.check() and can_launch([v[1]["megapixels"] for v in active.values()], pending[0][1]["megapixels"]):
                idx, page = pending.pop(0)
                name = page["wave"] + "--" + page["page_id"]
                log = (output / "logs" / (name + ".log")).open("xb")
                with watchdog.lock:
                    process = subprocess.Popen([sys.executable, "-B", str(HERE / "run.py"), "--out", str(output),
                                                "--worker", str(idx)], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                               start_new_session=True)
                    watchdog.processes[process.pid] = process
                active[process.pid] = (process, page, time.monotonic(), log)
                schedule.append(dict(event="start", pid=process.pid, wave=page["wave"], page=page["page_id"],
                                     active_megapixels=[v[1]["megapixels"] for v in active.values()]))
            for pid, (process, page, launched, log) in list(active.items()):
                code = process.poll()
                if code is None:
                    continue
                log.close()
                name = page["wave"] + "--" + page["page_id"]
                path = output / "pages" / (name + ".json")
                try:
                    result = json.loads(path.read_text())
                    if code or sha(output / result["records_path"]) != result["records_sha256"]:
                        raise RuntimeError("worker exit or records hash mismatch")
                except Exception as exc:
                    result = dict(status="page_failed", wave=page["wave"], page_id=page["page_id"],
                                  lines=len(page["lines"]), exit_code=code, error=str(exc), log=f"logs/{name}.log")
                    write_json(output / "pages" / (name + ".failure.json"), result)
                result["worker_wall_seconds"] = time.monotonic() - launched
                results.append(result)
                print(result["status"], page["wave"], page["page_id"], round(result["worker_wall_seconds"], 2), flush=True)
                with watchdog.lock:
                    watchdog.processes.pop(pid, None)
                del active[pid]
            if watchdog.reason and not active:
                break
            time.sleep(.1)
    finally:
        if active:
            watchdog.terminate()
        watchdog.stop()
    for _, page in pending:
        results.append(dict(status="not_run", wave=page["wave"], page_id=page["page_id"], reason=watchdog.reason))
    completed = [p for p in results if p["status"] == "completed"]
    final = sorted((r for p in completed for r in rows(output / p["records_path"])), key=lambda r: r["id"])
    write_rows(output / "lines.jsonl", final)
    # A shared ancestor as factory --crops admits both new masked crops and
    # immutable unmatched originals. Each individual crop was already bound.
    imports = [dict(templates[r["id"]], crop=str(output / r["masked_path"])) for r in final]
    write_rows(output / "real_v2_test_masked.jsonl", imports)
    import_result = dict(status="not_run", reason="incomplete masking")
    if len(completed) == len(pages) and not watchdog.reason:
        try:
            import_result = build_import(output, imports, seconds-(time.monotonic()-start))
        except Exception as exc:
            import_result = dict(status="failed", error=str(exc), traceback=traceback.format_exc())
            write_json(output / "import_failure.json", import_result)
    matches = {wave: dict(Counter(r["match_status"] for r in final if r["wave"] == wave)) for wave in WAVES}
    artifacts = {p: sha(output / p) for p in ("lines.jsonl", "real_v2_test_masked.jsonl", "selection.json")}
    if import_result["status"] == "completed":
        artifacts.update({str(p.relative_to(output)): sha(p) for p in (output / "real_v2_test_masked").rglob("*")
                          if p.is_file() and not p.is_symlink()})
    receipt = dict(schema="t6c2-mask-1", status="completed" if len(completed) == len(pages) and import_result["status"] == "completed" else "incomplete",
                   started_utc=started, finished_utc=utc(), wall_seconds=time.monotonic()-start, binding=binding,
                   population=summary, selected_pages=len(pages), selected_lines=sum(len(p["lines"]) for p in pages),
                   completed_pages=len(completed), completed_lines=len(final), per_wave_matching=matches,
                   results=results, schedule=schedule, policy=POLICY, test_mode=bool(test_pages), seed=SEED,
                   network="OFF; socket operations forbidden", nice=low_priority(), workers_small_max=6, workers_with_large_max=3,
                   threads_per_worker=1, disk_floor_bytes=DISK_FLOOR, minimum_free_bytes=watchdog.minimum_free_bytes,
                   watchdog_samples=watchdog.samples, run_budget_seconds=seconds, stop_reason=watchdog.reason,
                   import_format="unchanged E3 projected JSONL keys and real factory Parquet shards; reserved, codec v1",
                   factory_import=import_result, artifacts=artifacts)
    write_json(output / "mask_receipt.json", receipt)
    print(json.dumps(dict(status=receipt["status"], population=summary, selected_pages=len(pages),
                          completed_pages=len(completed), completed_lines=len(final), wall_seconds=receipt["wall_seconds"])), flush=True)
    return 0 if receipt["status"] == "completed" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUTPUT)
    parser.add_argument("--test-pages-per-wave", type=int, default=0)
    parser.add_argument("--max-seconds", type=int, default=MAX_SECONDS)
    parser.add_argument("--worker", type=int)
    args = parser.parse_args()
    low_priority()
    if not 0 < args.max_seconds <= MAX_SECONDS or args.test_pages_per_wave < 0:
        parser.error("budget must be 1..5400 seconds; sample size nonnegative")
    output = validate_output(args.out, args.test_pages_per_wave > 0 or args.worker is not None)
    if args.worker is None:
        output.mkdir(parents=True, exist_ok=False)
        for name in ("crops", "pages", "page-lines", "logs", "tmp"):
            (output / name).mkdir()
    io_guard(output)
    sys.path.insert(0, str(ROOT))
    if args.worker is not None:
        worker(output, args.worker)
        return 0
    return run(output, args.test_pages_per_wave, args.max_seconds)


if __name__ == "__main__":
    raise SystemExit(main())

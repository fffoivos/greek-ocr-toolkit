"""Q5 opt-in replay and decision checks on real development-page arrays.

Default --prototype-device off executes only Q4. Explicit cpu/mps/cuda enables
experiments, with no device fallback. Run serially, separately from tests or
other timings. Each receipt includes individual calls and packed batch timings,
transfer/packing/readback included; these are not kernel-only GPU timings.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[name] = "1"
os.environ.update(PYTHONDONTWRITEBYTECODE="1", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")

import cv2
import numpy as np
from PIL import Image

from greekocr.pages import PageOptions, process_page
from greekocr.pages import font, lines, pixels
from greekocr.pages.layout import read_layout


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def snapshot(result):
    """Full public values plus unrounded internal geometry and ownership."""
    return dict(records=result.to_records(), statistics=result.statistics,
                joining=result.joining, pieces=[p.line.to_record() for p in result.pieces],
                internal=[dict(curves={k: getattr(l, k).tolist() for k in
                    ("baseline", "meanline", "font_top", "font_bottom", "accent_top", "accent_bottom", "top", "bottom")},
                    components=l.component_ids, neighbours={k: v.tolist() if isinstance(v, np.ndarray) else v
                        for k, v in l.neighbours.items()}) for l in result.segmentation.lines],
                pixels={k: hashlib.sha256(getattr(result.segmentation.pixels, k).tobytes()).hexdigest()
                        for k in ("ink", "labels", "components", "barriers")})


def differences(a, b, *, atol=1e-3):
    """Discrete values exact; floats finite with absolute pixel/stat tolerance.

    Metadata is normalized using the same explicit Q3b allowlist as Q4 before
    this comparison. Report counts and first examples, never stop at one error.
    """
    report = dict(discrete=0, numerical=0, maximum_float_error=0., examples=[])

    def fail(kind, path, left, right):
        report[kind] += 1
        if sum(e["kind"] == kind for e in report["examples"]) < 20:
            report["examples"].append(dict(kind=kind, path=path, left=str(left)[:160], right=str(right)[:160]))

    def walk(left, right, path):
        if isinstance(left, dict) and isinstance(right, dict):
            if left.keys() != right.keys():
                fail("discrete", path, list(left), list(right))
            for key in left.keys() & right.keys():
                walk(left[key], right[key], path+"."+key)
        elif isinstance(left, (tuple, list)) and isinstance(right, (tuple, list)):
            if len(left) != len(right):
                fail("discrete", path, len(left), len(right))
            for i, (x, y) in enumerate(zip(left, right)):
                walk(x, y, f"{path}[{i}]")
        elif isinstance(left, (float, np.floating)) and isinstance(right, (float, np.floating)):
            error = abs(float(left)-float(right))
            report["maximum_float_error"] = max(report["maximum_float_error"], error)
            if not np.isfinite([left, right]).all() or error > atol+1e-9:
                fail("numerical", path, left, right)
        elif left != right:
            fail("discrete", path, left, right)
    walk(a, b, "$")
    return report


def timed(fn, repeats, sync=lambda: None):
    values, last = [], None
    for _ in range(repeats):
        sync()
        start = time.perf_counter()
        last = fn()
        sync()
        values.append(time.perf_counter()-start)
    return last, dict(samples_seconds=values, median_seconds=float(np.median(values)))


def compare_arrays(expected, actual, tolerance):
    errors, changed, elements = [], 0, 0
    shapes_equal = len(expected) == len(actual)
    for left, right in zip(expected, actual):
        if left.shape != right.shape:
            shapes_equal = False
            continue
        diff = np.abs(left.astype(float)-right.astype(float))
        errors.append(float(diff.max(initial=0)))
        changed += int(np.count_nonzero(diff))
        elements += diff.size
    maximum = max(errors, default=0.)
    return dict(equal_within_tolerance=bool(shapes_equal and np.isfinite(maximum) and maximum <= tolerance),
                tolerance=tolerance, max_abs_error=maximum, changed_elements=changed,
                elements=elements, arrays=len(expected), shapes_equal=shapes_equal)


def run_page(path, args, backend):
    from benchmark_q4 import allowlist, normalized
    with Image.open(path) as image:
        source = image.copy()
    gray = np.asarray(source.convert("L"), dtype=float)
    layout = ROOT/".astra/layout"/(path.stem+".json")
    regions = read_layout(layout, source.size) if layout.exists() else []
    calls = {"morphology": [], "wls": []}
    expected = {"morphology": [], "wls": []}
    refs = dict(morphology=pixels._rect_morphology, wls=font._smooth_samples)

    def morphology(mask, shape, *, closing=False):
        value = refs["morphology"](mask, shape, closing=closing)
        calls["morphology"].append((mask.copy(), shape, closing))
        expected["morphology"].append(value)
        return value

    def smooth(xs, ys, grid, xh):
        value = refs["wls"](xs, ys, grid, xh)
        calls["wls"].append((xs.copy(), ys.copy(), grid.copy(), xh))
        expected["wls"].append(value)
        return value

    kwargs = dict(page_key=path.stem, page_size=tuple(v/3 for v in source.size), table_regions=regions,
                  options=PageOptions(tables=True, statistics=True, join_lines=True))
    with ExitStack() as stack:
        if backend is not None:
            stack.enter_context(patch.object(pixels, "_rect_morphology", morphology))
            stack.enter_context(patch.object(font, "_smooth_samples", smooth))
        start = time.perf_counter()
        result = process_page(source, **kwargs)
        seconds = time.perf_counter()-start
    receipt = dict(page_key=path.stem, source_sha256=sha(path), layout_sha256=sha(layout) if layout.exists() else None,
                   shape=list(gray.shape), reference_api_seconds=seconds, lines=len(result.lines),
                   pieces=len(result.pieces), glyphs=len(result.glyphs))
    if backend is None:
        return receipt
    # Timings replay the actual Q4 calls; collection time is never a baseline.
    receipt["stages"] = {}
    for name, tolerance in (("morphology", 0.), ("wls", 1e-3)):
        fn = getattr(backend, "morphology_batch" if name == "morphology" else "smooth_batch")
        data = calls[name]
        baseline = (lambda: [refs[name](m, s, closing=c) for m, s, c in data]) if name == "morphology" else (lambda: [refs[name](*c) for c in data])
        if data:
            fn(data[:1])  # explicit warm-up, not timed
        _, reference_time = timed(baseline, args.repeats)
        individual, individual_time = timed(lambda: [fn([c])[0] for c in data], args.repeats, backend.synchronize)
        batched, batch_time = timed(lambda: fn(data), args.repeats, backend.synchronize)
        receipt["stages"][name] = dict(calls=len(data), reference=reference_time, individual=individual_time,
            batch=batch_time, individual_check=compare_arrays(expected[name], individual, tolerance),
            batch_check=compare_arrays(expected[name], batched, tolerance),
            input_array_bytes=sum(v.nbytes for c in data for v in c if isinstance(v, np.ndarray)))
    active = [p.line for p in result.pieces if p.line.discounted is None]
    original, original_time = timed(lambda: [np.asarray(lines._extract(gray, l, 32)) for l in active], args.repeats)
    if active:
        backend.straighten_batch(gray, active[:1])
    individual, individual_time = timed(lambda: [backend.straighten_batch(gray, [l])[0] for l in active], args.repeats, backend.synchronize)
    batched, batch_time = timed(lambda: backend.straighten_batch(gray, active), args.repeats, backend.synchronize)
    receipt["stages"]["straighten"] = dict(calls=len(active), reference=original_time,
        individual=individual_time, batch=batch_time, individual_check=compare_arrays(original, individual, 1.),
        batch_check=compare_arrays(original, batched, 1.), page_float32_bytes=gray.size*4,
        output_uint8_bytes=sum(a.nbytes for a in original))
    # Exercise downstream decisions, not just a shadow calculation: both
    # experimental morphology and WLS values actually drive a second full API.
    with patch.object(pixels, "_rect_morphology", lambda mask, shape, closing=False: backend.morphology_batch([(mask, shape, closing)])[0]), \
         patch.object(font, "_smooth_samples", lambda *c: backend.smooth_batch([c])[0]):
        start = time.perf_counter()
        candidate = process_page(source, **kwargs)
        receipt["experimental_api_seconds"] = time.perf_counter()-start
    left, right = snapshot(result), snapshot(candidate)
    allowed = allowlist()
    for value in (left, right):
        value["records"] = {k: normalized(v, k, allowed) for k, v in value["records"].items()}
        value["statistics"]["stats"] = normalized(value["statistics"]["stats"], "stats", allowed)
    # This derived hash must change for any permitted floating geometry change.
    # Record both values; compare the actual geometry above, not its hash as a
    # detector decision. The strict default/Q4 gate does NOT omit this field.
    receipt["geometry_hashes"] = [v["statistics"]["stats"].pop("geometry_sha256") for v in (left, right)]
    receipt["pipeline_check"] = differences(left, right)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prototype-device", choices=("off", "cpu", "mps", "cuda"), default="off")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--keys", nargs="*")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()
    if args.repeats < 1 or args.batch_size < 1:
        parser.error("repeats and batch-size must be positive")
    args.out.mkdir(parents=True, exist_ok=True)
    cv2.setNumThreads(1)
    summary = dict(device=args.prototype_device, platform=platform.platform(), python=sys.version,
        repeats=args.repeats, batch_size=args.batch_size, threads=1,
        timing_scope="host packing, device copies, synchronized compute and CPU readback; warmup excluded",
        script_sha256=sha(__file__), source_manifest={str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT/"greekocr").rglob("*.py"))},
        pages=[], failures=[])
    backend = None
    if args.prototype_device != "off":
        import torch
        from greekocr.pages.torch_prototypes import TorchArrays
        torch.set_num_threads(1)
        summary.update(torch=torch.__version__, mps_built=torch.backends.mps.is_built(), mps_available=torch.backends.mps.is_available(),
                       mps_fallback=os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK", "unset"))
        if os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK") == "1":
            raise ValueError("Disable MPS fallback so GPU receipts cannot hide CPU operations")
        try:
            backend = TorchArrays(args.prototype_device, args.batch_size)
        except (RuntimeError, AssertionError) as exc:
            summary["failures"].append(dict(stage="device_allocation", error=f"{type(exc).__name__}: {exc}"))
            (args.out/"summary.json").write_text(json.dumps(summary, indent=2))
            print(summary["failures"], flush=True)
            return 2
    start = time.perf_counter()
    for path in sorted((ROOT/".astra/pages").glob("*.png")):
        if args.keys and path.stem not in args.keys:
            continue
        receipt = run_page(path, args, backend)
        (args.out/(path.stem+".json")).write_text(json.dumps(receipt, indent=2))
        summary["pages"].append(receipt)
        if backend:
            for name, stage in receipt["stages"].items():
                for kind in ("individual_check", "batch_check"):
                    if not stage[kind]["equal_within_tolerance"]:
                        summary["failures"].append(dict(page=path.stem, stage=name, check=kind))
            if receipt["pipeline_check"]["discrete"] or receipt["pipeline_check"]["numerical"]:
                summary["failures"].append(dict(page=path.stem, stage="pipeline", **receipt["pipeline_check"]))
        summary["wall_seconds"] = time.perf_counter()-start
        (args.out/"summary.json").write_text(json.dumps(summary, indent=2))
        print(path.stem, "complete", len(summary["pages"]), "pages;", len(summary["failures"]), "failures", flush=True)
    if not summary["pages"]:
        raise ValueError("No pages selected")
    return int(bool(summary["failures"]))


if __name__ == "__main__":
    raise SystemExit(main())

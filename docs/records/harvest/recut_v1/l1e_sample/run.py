"""Offline L1E sample runner with opt-in T6e ownership exports."""
from __future__ import annotations

import os
import sys

sys.dont_write_bytecode = True
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS", "OMP_THREAD_LIMIT"):
    os.environ[_name] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

import argparse
import ast
import importlib.util
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
OUTPUT = HOME / "Projects/collect-v3-data/v2_masked/l1e_sample"
SCAN = Path("/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/"
            "8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/pages_scan.jsonl")
PARAMS = HERE.parent / "masking/params.json"
PROBE = HERE.parent / "masking/probe.py"
EXPECTED_PARAMS = "801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8"
EXPECTED_LIBRARY = "f203504a8703561569486450d7e725fe7b399cd4c8fbf581b79cd249e3c5aeb5"
DISK_FLOOR = 10_000_000_000
MAX_SECONDS = 55 * 60
WAVES = ("round1", "round2", "mixed", "vouli")
AUDIT = HERE.parent / "masking/audit_dev.py"
OWNERSHIP = ROOT.parent / "greek-ocr-toolkit-sol-funnel-gr/docs/harvest/sample_v1/gr/reference/greekocr/labelfix/geometry/ownership.py"
EXPECTED_OWNERSHIP = "1dd618bc2d884cf2490498456653f49b0276944f3bde83d38e26e633031eb641"


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
        raise RuntimeError("output directory must already exist without symlink ancestors")

    def writable(path):
        if isinstance(path, int):
            return
        target = Path(os.fsdecode(path)).absolute().resolve()
        if not target.is_relative_to(OUTPUT):
            raise PermissionError(f"T6d write outside output: {target}")

    def audit(event, args):
        if event in ("socket.connect", "socket.getaddrinfo", "socket.bind", "socket.sendto"):
            raise PermissionError("T6d network OFF")
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
    if sha(OWNERSHIP) != EXPECTED_OWNERSHIP:
        raise RuntimeError("dev component ownership source changed")
    return dict(audit_dev_sha256=sha(AUDIT), ownership_sha256=sha(OWNERSHIP),
                params_sha256=actual, params_file_sha256=sha(PARAMS),
                source_hashes=value["source_hashes"], matcher_sha256=sha(PROBE),
                runner_sha256=sha(__file__))


class Watchdog:
    """Monitor HOME and output each second; kill only our worker process group."""

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
        free = min(shutil.disk_usage(HOME).free, shutil.disk_usage(OUTPUT).free)
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


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_ids(filename):
    ids = Path(filename).read_text().splitlines()
    if not ids or any(not ident or ident != ident.strip() for ident in ids):
        raise ValueError('IDs must be nonempty, one unpadded ID per row')
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate requested ID')
    return ids


def validate_ids(ids, manifests):
    """Reject every invalid row before taking a processing subset."""
    wanted, found = set(ids), {}
    for split, filename in manifests.items():
        for row in rows(filename):
            if row.get('id') not in wanted:
                continue
            ident = row['id']
            if ident in found:
                raise ValueError(f'duplicate v2 ID: {ident}')
            wave = row.get('wave')
            if wave not in WAVES:
                raise ValueError(f'unsupported wave {wave}: {ident}')
            crop = Path(row.get('crop', ''))
            number = re.fullmatch(r'p(\d+)-l\d+\.png', crop.name)
            expected = Path('docs/harvest/harvest_big') / wave / 'crops'
            doc = row.get('doc', '').removeprefix(wave + ':')
            if (number is None or crop.parent.parent != expected or
                    not doc or ident != f'{doc}-{crop.stem}' or
                    row.get('doc') != f'{wave}:{doc}' or
                    row.get('split') != split or row.get('admitted') is not True):
                raise ValueError(f'not a valid v2 line: {ident}')
            found[ident] = dict(row, page=int(number[1]), doc_id=doc)
    missing = wanted - found.keys()
    if missing:
        raise ValueError('not a v2 line: ' + ', '.join(sorted(missing)))
    return [found[ident] for ident in ids]


def group_pages(lines):
    groups = defaultdict(list)
    for row in lines:
        groups[(row['wave'], row['doc_id'], row['page'])].append(row)
    return groups


def bind_sample(ids_file, limit):
    manifests = {split: INPUT / f'collection/v2/import_real_v2_{split}.jsonl'
                 for split in ('train', 'dev', 'test')}
    ids = read_ids(ids_file)
    validated = validate_ids(ids, manifests)
    wanted = set(ids)
    admitted, bindings = {}, {str(Path(ids_file).resolve()): sha(ids_file), str(SCAN): sha(SCAN)}
    bindings.update({str(filename): sha(filename) for filename in manifests.values()})
    for wave in WAVES:
        filename = INPUT / wave / 'admitted.jsonl'
        bindings[str(filename)] = sha(filename)
        for row in rows(filename):
            if row.get('id') in wanted:
                if row['id'] in admitted:
                    raise ValueError('duplicate admitted ID: ' + row['id'])
                admitted[row['id']] = (wave, row)
    observations = defaultdict(list)
    for row in rows(SCAN):
        observations[(row['wave'], row['doc'], row['page'])].append(row)
    all_pages = []
    for (wave, doc, number), group in group_pages(validated).items():
        crop_doc = Path(group[0]['crop']).parent.name
        candidates = observations[(wave, crop_doc, number)]
        if len(candidates) != 1:
            raise ValueError(f'expected one feasibility scan raster: {wave}/{doc}/{number}')
        scan = candidates[0]
        raster = (INPUT / scan['path']).resolve()
        allowed = [INPUT / 'harvest_big' / wave / 'images']
        if wave == 'round1':
            allowed.append(INPUT / 'harvest_big/round1/rescue/images')
        if not any(raster.is_relative_to(folder.resolve()) for folder in allowed) or not raster.is_file():
            raise ValueError(f'missing or out-of-scope raster: {raster}')
        page = dict(wave=wave, doc=crop_doc, page=number, page_id=f'{doc}-p{number:06d}',
                    raster=str(raster), scan=scan, lines=[])
        for row in group:
            admitted_wave, saved = admitted.get(row['id'], (None, {}))
            box = saved.get('crop_bbox')
            if (admitted_wave != wave or saved.get('crop_path') != row['crop'] or
                    saved.get('page_id') != page['page_id'] or saved.get('split') != row['split'] or
                    not isinstance(box, list) or len(box) != 4 or
                    any(type(value) is not int for value in box) or
                    not (0 <= box[0] < box[2] <= scan['w'] and 0 <= box[1] < box[3] <= scan['h']) or
                    not re.fullmatch(r'[0-9a-f]{64}', saved.get('crop_sha256', ''))):
                raise ValueError('admitted metadata mismatch: ' + row['id'])
            stored = (INPUT.parents[1] / row['crop']).resolve()
            if not stored.is_relative_to(INPUT.resolve()) or not stored.is_file():
                raise ValueError('missing or out-of-scope crop: ' + str(stored))
            page['lines'].append(dict(id=row['id'], crop=row['crop'], split=row['split'],
                                      script_class=row['script_class'], crop_bbox=box,
                                      crop_sha256=saved['crop_sha256']))
        all_pages.append(page)
    selected_ids = set(ids[:limit] if limit else ids)
    pages = [dict(page, lines=[r for r in page['lines'] if r['id'] in selected_ids]) for page in all_pages]
    pages = [page for page in pages if page['lines']]
    validation = dict(ids=len(ids), pages=len(all_pages),
                      per_wave=dict(Counter(r['wave'] for r in validated)),
                      per_split=dict(Counter(r['split'] for r in validated)),
                      per_script=dict(Counter(r['script_class'] for r in validated)),
                      selected_ids=[ident for ident in ids if ident in selected_ids])
    return pages, bindings, validation


def match_failure(index, candidates):
    if index is None:
        return 'unmatched'
    return 'ambiguous' if len(candidates) > 1 else None


def identity(original, box):
    import numpy as np
    mask = np.zeros((box[3]-box[1], box[2]-box[0]), dtype=bool)
    return original, dict(crop_box=box, masked_pixel_count=0, proposed_masked_pixel_count=0,
        masked_component_count=0, ring_median=None, ring_spread=None, fills=[],
        empty_ring_abstentions=0, changed=False, native_changed_pixels=0,
        mask_sha256=hashlib.sha256(mask.tobytes()).hexdigest())


def prepare_audit_rows(analysis, lines, own):
    """Use full assigned components, including ink outside the detector ribbon."""
    import numpy as np
    from greekocr.pages.lines import CURVES
    pixels = analysis.segmentation.pixels
    prepared = {}
    for index, line in enumerate(lines):
        record = line.to_record()
        record.update({key: getattr(line, key) for key in CURVES})
        components = pixels.components[np.isin(pixels.components[:, 5], line.component_ids)]
        if len(components):
            y0, y1 = int(components[:, 1].min()), int(components[:, 3].max())
        else:
            y0, y1 = 0, pixels.ink.shape[0]
        record.update(row_id=index, component_ids=list(line.component_ids),
                      owned_box=[line.x0, y0, line.x1, y1])
        try:
            prepared[index] = own.prepare_row(record, pixels.ink, pixels.labels)
        except ValueError:
            # invalid_detector_geometry: this detector row cannot be audited; the page's audit becomes unknown.
            INVALID_AUDIT_ROWS.append(index)
    return prepared


INVALID_AUDIT_ROWS = []


def single_thread_opencv():
    import cv2
    # GCD on macOS only supports <=0; 1 silently leaves all cores enabled.
    # Zero disables OpenCV parallel regions on GCD and other backends.
    cv2.setNumThreads(0)
    if cv2.getNumThreads() != 1:
        raise RuntimeError('could not disable OpenCV numerical parallelism')
    return cv2


def ownership_sets(prepared, line, neighbours, box):
    """Reconstruct the frozen Voronoi proposal and per-component ring abstentions."""
    import numpy as np
    from greekocr.glyphs.foreign_ink import _centre_fit, _foreign_mask, _ring
    x0, y0, x1, y1 = box
    ink = prepared.ink[y0:y1, x0:x1]
    proposed = _foreign_mask(prepared.ink, _centre_fit(line),
                             [_centre_fit(n) for n in neighbours if n is not line], tuple(box))
    components = prepared.labels[y0:y1, x0:x1]
    abstained = np.zeros_like(proposed)
    for ident in np.unique(components[proposed]):
        if _ring(prepared, int(ident))['fill'] is None:
            abstained |= proposed & (components == ident)
    return ink, proposed, abstained


def check_ownership_map(labels, ink, proposed, abstained, mask, mask_sha256):
    """Fail closed on any partition, native-grid, or applied-mask discrepancy."""
    import numpy as np
    if (labels.dtype != np.uint8 or labels.ndim != 2 or
            any(part.shape != labels.shape for part in (ink, proposed, abstained, mask)) or
            np.any(labels > 5)):
        raise RuntimeError('ownership PNG dtype, shape or class mismatch')
    union = (labels >= 2) & (labels <= 4)
    digest = hashlib.sha256(union.tobytes()).hexdigest()
    if not np.array_equal(union, mask) or digest != mask_sha256:
        raise RuntimeError('ownership class union != applied mask (mask_sha256 mismatch)')
    if (not np.array_equal(labels == 5, abstained) or np.any(mask & abstained) or
            not np.array_equal(proposed, mask | abstained)):
        raise RuntimeError('ownership class 5 != ring-abstained set')
    if (not np.array_equal(labels == 0, ~ink) or
            not np.array_equal(labels == 1, ink & ~proposed)):
        raise RuntimeError('ownership background/keep partition mismatch')
    return dict(mask_union_sha256=digest,
                abstained_sha256=hashlib.sha256(abstained.tobytes()).hexdigest(),
                class_pixels={str(i): int((labels == i).sum()) for i in range(6)})


def save_ownership_map(destination, labels, box):
    """Write an unscaled, single-channel uint8 PNG and verify its native readback."""
    import numpy as np
    from PIL import Image
    expected = (box[2] - box[0], box[3] - box[1])
    if labels.dtype != np.uint8 or labels.shape != expected[::-1]:
        raise RuntimeError('ownership PNG is not aligned to crop rectangle')
    destination.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(labels).save(destination, format='PNG', compress_level=3)
    with Image.open(destination) as opened:
        if (opened.mode != 'L' or opened.size != expected or
                not np.array_equal(np.asarray(opened), labels)):
            raise RuntimeError('ownership PNG native-grid readback mismatch')


def build_ownership_map(prepared, detector_labels, owned_rows, lines, index, box, result, identity_reason=None):
    """Crosswalk masking components to detector components on the native pixel grid.

    Component IDs in the two observations are distinct namespaces. Never infer
    an entire masking component's owner from a majority of overlapping pixels.
    """
    import numpy as np
    from greekocr.glyphs.foreign_ink import _centre_fit
    if identity_reason:
        x0, y0, x1, y1 = box
        ink = prepared.ink[y0:y1, x0:x1]
        proposed = np.zeros_like(ink)
        abstained = np.zeros_like(ink)
    else:
        ink, proposed, abstained = ownership_sets(prepared, lines[index], lines, box)
    labels = np.zeros(ink.shape, dtype=np.uint8)
    labels[ink & ~proposed] = 1
    labels[abstained] = 5
    x0, y0, x1, y1 = box
    masking_ids = prepared.labels[y0:y1, x0:x1]
    detector_ids = detector_labels[y0:y1, x0:x1]
    assigned = {}
    for row_id, line in enumerate(lines):
        # prepare_audit_rows rejects invalid ribbons, but their detector
        # component assignments remain explicit. Retain that provenance rather
        # than silently calling those assigned components unassigned.
        row = owned_rows.get(row_id)
        ids = row['component_ids'] if row is not None else line.component_ids
        for ident in ids:
            ident = int(ident)
            if ident in assigned and assigned[ident] != row_id:
                raise RuntimeError(f'detector component {ident} has multiple owner rows')
            assigned[ident] = row_id
    own_fit = _centre_fit(lines[index]) if not identity_reason else None
    components = []
    own_masked_pixels = 0
    # Group by both observed component IDs; this preserves split/merged and
    # unobserved detector pixels without conflating the label namespaces.
    yy, xx = np.nonzero(ink)
    pairs = np.stack((masking_ids[yy, xx], detector_ids[yy, xx]), axis=1)
    unique, inverse = np.unique(pairs, axis=0, return_inverse=True)
    for group, (masking_id, detector_id) in enumerate(unique):
        hit = inverse == group
        ry, rx = yy[hit], xx[hit]
        owner_id = assigned.get(int(detector_id))
        if owner_id is None:
            side = 'unassigned'
        elif identity_reason:
            side = 'unresolved'
        elif owner_id == index:
            side = 'own'
        else:
            xs = (rx + x0).astype(float)
            offset = float(np.median(_centre_fit(lines[owner_id]).base_at(xs) - own_fit.base_at(xs)))
            if offset == 0:
                raise RuntimeError(f'detector owner row {owner_id} has no vertical side relative to row {index}')
            side = 'above' if offset < 0 else 'below'
        masked = result.mask[ry, rx]
        if masked.any():
            if side == 'own':
                # The requested classes omit detector-own ink lost by Voronoi.
                # Preserve the exact mask union and the true detector owner;
                # expose this exception explicitly instead of calling it unassigned.
                below = ry[masked] + y0 >= own_fit.base_at((rx[masked] + x0).astype(float))
                labels[ry[masked], rx[masked]] = np.where(below, 3, 2)
                own_masked_pixels += int(masked.sum())
            else:
                labels[ry[masked], rx[masked]] = {'above': 2, 'below': 3, 'unassigned': 4}[side]
        for value in np.unique(labels[ry, rx]):
            conflict = side == 'own' and value in (2, 3)
            components.append(dict(component_id=int(masking_id), detector_component_id=int(detector_id) or None,
                class_value=int(value), pixel_count=int((labels[ry, rx] == value).sum()),
                owner_row_id=owner_id, side=('above' if value == 2 else 'below') if conflict else side,
                ownership_conflict='masked_detector_own' if conflict else None,
                side_basis='pixel_position' if conflict else ('unresolved_identity' if identity_reason else 'detector_owner'),
                owner_geometry_valid=owner_id in owned_rows if owner_id is not None else None))
    checks = check_ownership_map(labels, ink, proposed, abstained, result.mask, result.record['mask_sha256'])
    if sum(r['pixel_count'] for r in components) != int(ink.sum()):
        raise RuntimeError('ownership components do not partition crop ink')
    checks.update(detector_own_masked_pixels=own_masked_pixels,
                  keep_basis='identity_unmasked' if identity_reason else '_voronoi_keep')
    return labels, components, checks


def bind_comparison(directory, pages):
    """Bind only selected reference crops; never write to the reference output."""
    directory = Path(directory).expanduser().resolve()
    if not directory.is_dir():
        raise ValueError(f'comparison directory does not exist: {directory}')
    if directory.is_relative_to(OUTPUT) or OUTPUT.is_relative_to(directory):
        raise ValueError('comparison directory overlaps output')
    selected = {r['id']: (page, r) for page in pages for r in page['lines']}
    filename = directory / 'lines.jsonl'
    references = {}
    for record in rows(filename):
        ident = record['id']
        if ident not in selected:
            continue
        if ident in references:
            raise ValueError(f'duplicate comparison ID: {ident}')
        page, row = selected[ident]
        relative = str(Path('crops') / page['wave'] / page['doc'] / Path(row['crop']).name)
        if record['masked_path'] != relative or record['old_box'] != row['crop_bbox']:
            raise ValueError(f'comparison crop path/rectangle mismatch: {ident}')
        path = (directory / relative).resolve()
        if not path.is_relative_to(directory) or sha(path) != record['masked_sha256']:
            raise ValueError(f'comparison crop hash mismatch: {ident}: {path}')
        references[ident] = dict(path=str(path), masked_sha256=record['masked_sha256'],
                                 mask_sha256=record['mask_sha256'])
    if selected.keys() != references.keys():
        raise ValueError('missing comparison IDs: ' + ', '.join(sorted(selected.keys() - references.keys())))
    return dict(directory=str(directory), lines_sha256=sha(filename), records=references)


def compare_crop(destination, record, reference):
    actual, expected = sha(destination), sha(reference['path'])
    if (actual != reference['masked_sha256'] or expected != reference['masked_sha256'] or
            record['mask_sha256'] != reference['mask_sha256']):
        raise RuntimeError(f"comparison mismatch for {record['id']}: {destination} vs {reference['path']}; "
                           f"crop SHA256 {actual} vs {expected}; "
                           f"mask SHA256 {record['mask_sha256']} vs {reference['mask_sha256']}")
    return dict(path=reference['path'], masked_sha256=actual, crops_identical=True, mask_identical=True)


def worker(index, export_ownership=False, compare=False):
    binding = frozen()
    import numpy as np
    from PIL import Image
    from greekocr.glyphs.foreign_ink import PARAMETERS, MaskedCrop, prepare_mask_page, mask_foreign_ink
    from greekocr.pages import process_page
    cv2 = single_thread_opencv()
    if PARAMETERS != json.loads(PARAMS.read_text())['params']:
        raise RuntimeError('live parameters differ from freeze')
    audit = load_module('t6d_audit_dev', AUDIT)
    own = load_module('t6d_component_ownership', OWNERSHIP)
    selected = json.loads((OUTPUT / 'sample.json').read_text())[index]
    comparison = json.loads((OUTPUT / 'comparison.json').read_text()) if compare else None
    name = selected['wave'] + '--' + selected['page_id']
    native_path = Path(selected['raster'])
    started = time.perf_counter()
    if sha(native_path) != selected['scan']['sha']:
        raise RuntimeError('raster differs from feasibility scan')
    with Image.open(native_path) as opened:
        native = opened.copy()
    if (native.width, native.height, native.mode) != (
            selected['scan']['w'], selected['scan']['h'], selected['scan']['mode']):
        raise RuntimeError('raster header differs from feasibility scan')
    detector_started = time.perf_counter()
    analysis = process_page(native)
    detector_seconds = time.perf_counter() - detector_started
    lines = [line for line in analysis.segmentation.lines if line.discounted is None]
    match, runtime_fit = matcher()
    fits = [runtime_fit(line) for line in lines]
    prepared = prepare_mask_page(native)
    owned_rows = prepare_audit_rows(analysis, lines, own)
    records = []
    for row in selected['lines']:
        box = row['crop_bbox']
        original = native.crop(tuple(box))
        buffer = io.BytesIO()
        original.save(buffer, format='PNG', compress_level=3)
        original_sha = hashlib.sha256(buffer.getvalue()).hexdigest()
        stored_path = INPUT.parents[1] / row['crop']
        stored_sha = sha(stored_path)
        with Image.open(stored_path) as stored:
            pixel_equal = (stored.mode == original.mode and stored.size == original.size and
                           np.array_equal(np.asarray(stored), np.asarray(original)))
        index = match(box, fits)  # The exact frozen T6a2 matcher, executed unchanged.
        candidates = candidate_diagnostics(box, fits)
        if index != (candidates[0]['index'] if candidates else None):
            raise RuntimeError('candidate diagnostics differ from frozen matcher')
        failure = match_failure(index, candidates)
        custody_failures = []
        if original_sha != row['crop_sha256']:
            custody_failures.append('recut_sha_mismatch')
        if stored_sha != row['crop_sha256'] or not pixel_equal:
            custody_failures.append('stored_crop_mismatch')
        if failure or custody_failures:
            # Matching failures are diagnostic identities, never page stop gates.
            image, record = identity(original, box)
            if custody_failures:
                # Preserve the stored original on custody failures too.
                with Image.open(stored_path) as stored:
                    image = stored.copy()
        else:
            result = mask_foreign_ink(prepared, lines[index], lines, box)
            image, record = result.image, result.record
        a, b = np.asarray(original), np.asarray(image)
        owner = own.ownership(box, list(owned_rows.values())) if not INVALID_AUDIT_ROWS else None
        if custody_failures or INVALID_AUDIT_ROWS:
            counts = {key: None for key in ('own_component_pixels_lost', 'own_pixels',
                'own_components_before', 'own_components_touched', 'foreign_pixels_before',
                'foreign_pixels_removed', 'foreign_components_before', 'foreign_components_touched',
                'foreign_components_removed_from_crop')}
        else:
            changed_mask = np.any(a != b, axis=2) if a.ndim == 3 else a != b
            counts, _ = audit.component_audit(owned_rows, analysis.segmentation.pixels.labels,
                                            box, changed_mask, owner['row_id'], own.box_hits)
        dest = OUTPUT / 'crops' / selected['wave'] / selected['doc'] / Path(row['crop']).name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if failure or custody_failures:
            # Byte-exact stored originals for every identity crop.
            shutil.copyfile(stored_path, dest)
        else:
            image.save(dest, format='PNG', compress_level=3)
        if sha(stored_path) != stored_sha:
            raise RuntimeError('original crop changed during processing')
        record.update(counts, id=row['id'], wave=selected['wave'], page=selected['page'],
            page_id=selected['page_id'], old_box=box, split=row['split'], script_class=row['script_class'],
            original_crop_sha256=original_sha, stored_crop_sha256=stored_sha,
            admitted_crop_sha256=row['crop_sha256'], masked_sha256=sha(dest),
            recut_pixels_equal=pixel_equal, original_path=str(stored_path),
            masked_path=str(dest.relative_to(OUTPUT)), runtime_index=index, candidates=candidates,
            match_status=failure or 'ok', failure_kind=failure, custody_failures=custody_failures,
            mask_applied=not failure and not custody_failures, ownership=owner,
            own_pixels_lost=counts['own_component_pixels_lost'], originals_unchanged=True,
            audit_status='custody_failure' if custody_failures else ('invalid_detector_geometry_on_page' if owner is None else owner['ownership_status']))
        if comparison is not None:
            record['comparison'] = compare_crop(dest, record, comparison['records'][row['id']])
        if export_ownership:
            if custody_failures:
                raise RuntimeError(f"cannot export native ownership for custody-failed crop {row['id']}")
            if failure:
                result = MaskedCrop(image, np.zeros((box[3]-box[1], box[2]-box[0]), dtype=bool), record)
            label_map, components, checks = build_ownership_map(
                prepared, analysis.segmentation.pixels.labels, owned_rows, lines, index, box, result, failure)
            ownership_path = OUTPUT / 'ownership' / selected['wave'] / selected['doc'] / dest.name
            save_ownership_map(ownership_path, label_map, box)
            record.update(components=components, ownership_path=str(ownership_path.relative_to(OUTPUT)),
                          ownership_sha256=sha(ownership_path), ownership_export_status=(
                              'identity_' + failure if failure else 'voronoi_with_detector_conflicts'
                              if checks['detector_own_masked_pixels'] else 'voronoi'),
                          ownership_checks=checks)
        if not record['changed'] and not custody_failures and record['masked_sha256'] != stored_sha:
            raise RuntimeError('identity PNG differs from stored original')
        records.append(record)
    if sha(native_path) != selected['scan']['sha']:
        raise RuntimeError('source raster changed during processing')
    frozen()
    write_json(OUTPUT / 'pages' / (name + '.json'), dict(
        wave=selected['wave'], page_id=selected['page_id'], records=records,
        page_seconds=time.perf_counter()-started, detector_seconds=detector_seconds,
        worker_pid=os.getpid(), nice=low_priority(), opencv_threads=cv2.getNumThreads(),
        numerical_threads={key: os.environ[key] for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
            'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS', 'BLIS_NUM_THREADS')},
        peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == 'darwin' else 1024),
        originals_unchanged=True, binding=binding))


def summary(records):
    losses = [r['own_pixels_lost'] for r in records if r['own_pixels_lost'] is not None]
    ratios = [r['own_pixels_lost']/r['own_pixels'] for r in records if r['own_pixels']]
    count = len(records)
    return dict(lines=count, masked=sum(r['mask_applied'] for r in records),
        changed=sum(r['changed'] for r in records), failed=sum(
            bool(r['failure_kind'] or r['custody_failures']) for r in records),
        share_masked=sum(r['mask_applied'] for r in records)/count if count else None,
        share_changed=sum(r['changed'] for r in records)/count if count else None,
        share_failed=sum(bool(r['failure_kind'] or r['custody_failures']) for r in records)/count if count else None,
        failure_kinds=dict(Counter(f for r in records for f in
            ([r['failure_kind']] if r['failure_kind'] else []) + r['custody_failures'])),
        masked_pixels=sum(r['masked_pixel_count'] for r in records),
        foreign_pixels_removed=sum(r['foreign_pixels_removed'] or 0 for r in records),
        foreign_measurement_unknown=sum(r['foreign_pixels_removed'] is None for r in records),
        own_loss=dict(measured=len(losses), unknown=count-len(losses),
            zero=sum(n == 0 for n in losses), nonzero=sum(n > 0 for n in losses),
            pixels_total=sum(losses), pixels_min=min(losses, default=None),
            pixels_max=max(losses, default=None), pixels_median=statistics.median(losses) if losses else None,
            pixels_histogram=dict(Counter(map(str, losses))),
            fraction_max=max(ratios, default=None),
            fraction_median=statistics.median(ratios) if ratios else None))


def prepare_output(out):
    global OUTPUT
    requested = Path(out).expanduser().absolute()
    resolved = requested.resolve()
    if requested != resolved:
        raise ValueError('output path must have no symlink ancestors')
    if INPUT.resolve().is_relative_to(resolved) or resolved.is_relative_to(INPUT.resolve()) or ROOT.is_relative_to(resolved):
        raise ValueError('output overlaps read-only inputs or checkout root')
    OUTPUT = resolved
    if OUTPUT.exists() and (not OUTPUT.is_dir() or any(OUTPUT.iterdir())):
        raise ValueError('output must be new or empty; no resume or overwrite')
    OUTPUT.mkdir(parents=True, exist_ok=True)


def main():
    global OUTPUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=OUTPUT)
    parser.add_argument('--limit', type=int, help='validate every ID, then process only the first N')
    parser.add_argument('--validate-only', action='store_true', help='validate all IDs/metadata, without output or detection')
    parser.add_argument('--export-ownership', action='store_true', help='export crop-aligned uint8 ownership PNGs and component records')
    parser.add_argument('--compare', type=Path, help='require byte-identical crops and mask hashes from an earlier output directory')
    parser.add_argument('--worker', type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.limit is not None and args.limit <= 0:
        parser.error('--limit must be positive')
    low_priority()
    sys.path.insert(0, str(ROOT))
    if args.validate_only:
        # Network guard without enabling any writable output directory.
        def no_network(event, unused):
            if event.startswith('socket.'):
                raise PermissionError('T6d network OFF')
        sys.addaudithook(no_network)
        frozen()
        pages, _, validation = bind_sample(args.ids, args.limit)
        if args.compare is not None:
            comparison = bind_comparison(args.compare, pages)
            validation['comparison'] = dict(directory=comparison['directory'],
                                             crops_bound=len(comparison['records']))
        print(json.dumps(validation, indent=2))
        return
    if args.worker is not None:
        OUTPUT = args.out.expanduser().resolve()
        install_io_guard()
        worker(args.worker, args.export_ownership, args.compare is not None)
        return
    if args.compare is not None:
        reference, destination = args.compare.expanduser().resolve(), args.out.expanduser().resolve()
        if reference.is_relative_to(destination) or destination.is_relative_to(reference):
            parser.error('--compare directory must not overlap --out')
    prepare_output(args.out)
    install_io_guard()
    started = utc()
    watchdog = Watchdog()
    results, records, pages, binding, validation, reason = [], [], [], {}, {}, None
    comparison = None
    # Output-only exclusive marker, never a W1 lock.
    with (OUTPUT / 'started.json').open('x') as stream:
        stream.write(dump_row(dict(pid=os.getpid(), utc=started, nice=low_priority())))
    try:
        watchdog.start()
        binding = frozen()
        pages, inputs, validation = bind_sample(args.ids, args.limit)
        if args.compare is not None:
            comparison = bind_comparison(args.compare, pages)
            write_json(OUTPUT / 'comparison.json', comparison)
        binding.update(inputs=inputs, python=sys.version)
        write_json(OUTPUT / 'sample.json', pages)
        for directory in ('pages', 'logs', 'crops'):
            (OUTPUT / directory).mkdir()
        with (OUTPUT / 'lines.jsonl').open('x') as stream:
            for i, page in enumerate(pages):
                if watchdog.check():
                    raise RuntimeError(watchdog.reason)
                name = page['wave'] + '--' + page['page_id']
                with (OUTPUT / 'logs' / (name + '.log')).open('x') as log:
                    with watchdog.lock:
                        if watchdog.reason:
                            raise RuntimeError(watchdog.reason)
                        command = [sys.executable, '-B', str(Path(__file__).resolve()),
                            '--ids', str(args.ids.resolve()), '--out', str(OUTPUT), '--worker', str(i)]
                        if args.export_ownership:
                            command.append('--export-ownership')
                        if comparison is not None:
                            command.extend(['--compare', comparison['directory']])
                        process = subprocess.Popen(command,
                            cwd=OUTPUT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                        watchdog.process = process
                    code = process.wait()
                    with watchdog.lock:
                        watchdog.process = None
                result_file = OUTPUT / 'pages' / (name + '.json')
                if code != 0 or not result_file.exists():
                    raise RuntimeError(watchdog.reason or f'worker_error: {name}, exit {code}; see logs/{name}.log')
                result = json.loads(result_file.read_text())
                results.append({key: value for key, value in result.items() if key != 'records'})
                for record in result['records']:
                    stream.write(dump_row(record))
                    records.append(record)
                stream.flush()
                print(f"PAGE {i+1}/{len(pages)} {name}: {len(result['records'])} lines; "
                      f"{result['page_seconds']:.2f}s", flush=True)
        for filename, expected in inputs.items():
            if sha(filename) != expected:
                raise RuntimeError('read-only metadata changed: ' + filename)
        if comparison is not None:
            if sha(Path(comparison['directory']) / 'lines.jsonl') != comparison['lines_sha256']:
                raise RuntimeError('read-only comparison lines.jsonl changed')
            for record in records:
                compare_crop(OUTPUT / record['masked_path'], record, comparison['records'][record['id']])
        frozen()
    except Exception as exc:
        reason = f'{type(exc).__name__}: {exc}'
        traceback.print_exc()
    finally:
        watchdog.stop()
    reason = reason or watchdog.reason
    receipt = dict(schema='t6e-l1e-sample-1', status='failed' if reason else 'completed',
        export_ownership=args.export_ownership,
        comparison=dict(directory=comparison['directory'], lines_sha256=comparison['lines_sha256'],
                        crops_verified=sum('comparison' in r for r in records)) if comparison is not None else None,
        started_utc=started, finished_utc=utc(), stop_reason=reason, validation=validation,
        selected_pages=len(pages), completed_pages=len(results), pages=results,
        totals=summary(records), per_wave={wave: summary([r for r in records if r['wave'] == wave]) for wave in WAVES},
        binding=binding, network='OFF', nice=low_priority(), workers_max=1, threads_per_worker=1,
        disk_floor_bytes=DISK_FLOOR, minimum_free_bytes=watchdog.minimum_free_bytes,
        watchdog_samples=watchdog.samples, watchdog_interval_seconds=1, run_budget_seconds=MAX_SECONDS,
        originals_unchanged=all(r['originals_unchanged'] for r in records) if records and not reason else None,
        own_loss_audit='masking/audit_dev.py:component_audit; original OWN.prepare_row/ownership/box_hits',
        ownership_limit='detector component attribution, not semantic ground truth; unknown owners remain null',
        matching='exact frozen T6a2 matcher; multiple eligible curves are ambiguous identities; no added x-overlap gate',
        lines_sha256=sha(OUTPUT / 'lines.jsonl') if (OUTPUT / 'lines.jsonl').exists() else None)
    write_json(OUTPUT / 'receipt.json', receipt)
    print(json.dumps(dict(status=receipt['status'], totals=receipt['totals'], stop_reason=reason)), flush=True)
    return 1 if reason else 0


if __name__ == '__main__':
    raise SystemExit(main())

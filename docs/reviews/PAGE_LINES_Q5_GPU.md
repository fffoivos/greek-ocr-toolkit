# Q5: arrays, GPU design and small prototypes

**A GPU makes architectural sense for the neural stages and potentially for
large batches of line resampling. It is not yet a measured detector speedup on
this Mac.** Local weighted guide fitting benefits from batching even on the
CPU; moving optimized OpenCV morphology into torch can be much slower.

Measured on CPU across all 54 pages: batched inner guide fitting is **14.93×
faster**, morphology **115.8× slower**, and straightening **1.17× slower** than
their Q4 CPU references. The float32 fit changes downstream statistics on three
pages, so it is not safe to adopt as an equivalent replacement.

**MPS speedup: not measured.** This session's
PyTorch reports MPS built but unavailable and rejects the initial tensor
allocation. The requested MPS corpus run therefore remains unfinished. CUDA
was not run. The [design](../research/GPU_DESIGN.md) specifies the complete
Docling chain, CPU/GPU division, recogniser interface, memory/transfer costs,
throughput bounds and the later CUDA benchmark.

## Implementation and scope

`greekocr/pages/torch_prototypes.py` contains three experimental array paths:

- Rectangular opening/closing, using separable extrema pooling with Q4's
  border values and even-kernel origins.
- The expensive inner local weighted guide fit, batching knots and independent
  calls, preserving three robust iterations and both regularizers. Class
  decisions, outer fit iterations, interpolation and smoothing stay CPU.
- Packed bilinear straightening, uploading a page once per page batch and
  retaining Q4's float64 coordinate and outside-envelope decisions on CPU.

No existing production API, default-option or CLI code was changed. Normal
page processing does not import the prototype module; constructing its backend
explicitly imports torch.
The separate `benchmark_q5.py` command defaults to `--prototype-device off`.
An explicit `cpu`, `mps` or `cuda` selects the experiment; no automatic device
substitution is allowed. The benchmark checks the individual kernels and then
reruns the full API with experimental morphology and guide values actually
driving downstream decisions. It does not claim that independent replay calls
are already batched inside the production detector.

Selection follows Q4's retained profile: local smoothing 0.595 s, rule-mask
construction 0.422 s and extraction 0.322 s on the profiled page. Rectangular
morphology is only a subset of rule construction; the replay measures that
subset separately. Binarisation, CCL and statistics are mapped in the design;
they are not presented as implemented GPU stages.

## Device evidence

The Mac reports Apple M5, 10 CPU cores, 10 GPU cores, 32 GB unified memory,
macOS 26.5.1, Python 3.11.3 and torch 2.14.1. The failing probe returns:

```
mps_built: true
mps_available: false
RuntimeError: The MPS backend is supported on macOS 14.0+.
Current OS version can be queried using `sw_vers`
```

That message does not match the reported OS version. It establishes that this
execution session cannot allocate MPS tensors, not that the physical Mac lacks
a GPU or that MPS would be slow. No fallback flag was enabled. No MPS stage,
transfer, per-page or per-batch timing is available. The same explicit MPS
command is ready to rerun in a session with device access.

## Measurement method

All 54 development PNGs and their available Docling layout files are used;
book and held-out pages are excluded. Layout inference itself is not rerun.
Frame is PNG/3; tables, default joining and statistics are enabled. The CPU
benchmark runs serially, with one BLAS/OpenMP/OpenCV/torch compute thread and
no overlapping tests or other benchmarks. There are three timed repetitions
per kernel workload, after one separate warm-up call. That first-call warm-up
does not guarantee every shape is warm; all raw samples are retained.

Each reference API run captures its real morphology and local-fit inputs.
Reference, individual torch calls and batched torch calls replay those same
inputs. Batches are capped at 16 entries; WLS also caps padded contact×knot
products and straightening tiles at one million output pixels. Morphology
groups only identical mask/kernel shapes. Straightening uses all active
delivered pieces. Timings include host packing, transfers, synchronized device
work, CPU interpolation where retained, and readback. They exclude initial
module/device startup and capture instrumentation. The individual
straightening path uploads the page per line; the page batch shares one upload.

“Page batch” below means all calls for that page, internally chunked under those
limits, not one 16-item GPU launch. Per-page receipts retain all three timing
samples, item counts, dimensions, array bytes, tolerances and errors. Reported
corpus totals sum per-page medians. These observations have no confidence
interval and no thermal control; the reference and experimental API wall times
are diagnostic only, not controlled speedup claims.

## Numerical and decision gates

These are reproduction checks against Q4, not a human-adjudicated OCR or
segmentation quality score. No PDF text layer supplies a reference.

Morphology must be bit-exact. WLS corrections must have maximum absolute error
at most 0.001 pixels against Q4 float64. Straightened crop dimensions are exact,
with at most one gray level of uint8 pixel difference. Float32 resampling is
not bit-exact crop extraction and does not establish equal recogniser text.

The complete experimental API comparison checks raw guide/boundary curves and
all public values within 0.001 absolute units (plus 1e-9 solely for binary
representation at that decimal limit). Integers, strings, Boolean decisions,
ownership, masks/labels, counts, IDs, classes, discounts and links are exact.
The derived `geometry_sha256` is recorded separately because any permitted
floating change changes that hash. It is **not** omitted from the strict
default-versus-Q4 gate. Q4's existing metadata allowlist is otherwise used.

An early sparse/extrapolated-contact test caught cancellation in a raw 2x2
normal-equation solve (0.00337 px error); centering the solve while retaining
the original ridges fixed it. The first pilot also counted the expected
geometry hash change as a decision change and rejected decimal 0.001 due to
binary representation; these harness distinctions are explicit above. Raw
pilot evidence is retained separately from the final corpus run.

## Measured results: all 54 development pages

**CPU guide WLS batching is 14.93× faster for that inner operation. This is not
a 14.93× detector or GPU speedup.** Rectangular morphology is 115.8× slower
than OpenCV; straightening is 1.17× slower than the reference, although sharing
the page upload makes it 3.35× faster than the individual torch calls.

Times below sum each page's three-repetition median. All packing, retained CPU
work and output conversion/readback are included. No MPS timings are available.

| Operation | Actual calls/crops | Q4 CPU total s | Torch CPU individual total s | Torch CPU page-batch total s | Q4 / batch |
|---|---:|---:|---:|---:|---:|
| Rectangular morphology | 3,353 | 1.567 | 179.600 | 181.488 | 0.0086× |
| Local guide WLS | 11,290 | 11.353 | 1.520 | 0.760 | 14.93× |
| Straightening | 8,546 | 11.712 | 45.831 | 13.689 | 0.856× |

| Operation | Reference median s/page | Batched median s/page | Reference p95 s/page | Batched p95 s/page | Worst batched s/page |
|---|---:|---:|---:|---:|---:|
| Rectangular morphology | 0.01783 | 1.72022 | 0.06377 | 8.69442 | 23.18007 |
| Local guide WLS | 0.15839 | 0.01025 | 0.53724 | 0.03533 | 0.04036 |
| Straightening | 0.16090 | 0.18722 | 0.51589 | 0.59462 | 0.62439 |

The entire capture/replay/second-API/comparison run took 2,731.721 seconds; that
is validation workload time, not 54-page production throughput. Kernel timings
exclude the expensive comparisons. The morphology replay's small 1.567-second
reference total also establishes that this subset of rule construction is not
a promising CPU bottleneck, despite its enclosing stage's profile time.

The reference page raster cast to float32 required a median 25,935,976 bytes
and a maximum 73,636,304 bytes. Returned uint8 crops used a median 8,476,864
bytes/page and a maximum 30,108,288 bytes/page. These are payload sizes, not
measured peak memory or MPS transfer times. Source arrays, indices, fractions,
temporaries, capture buffers and neural models require additional memory.
In particular, the gather implementation supplies 25 geometry bytes per output
pixel (two int64 indices, two float32 fractions and a mask): 211,921,600 nominal
bytes at the median output volume, before the page upload. CUDA qualification
must compare this with CPU crops plus a one-byte/pixel upload; keeping the page
resident alone does not remove this cost.

### Kernel checks

Both individual and batched CPU-torch paths passed on **54/54 pages**:

| Operation | Compared elements across actual calls | Maximum error | Changed elements |
|---|---:|---:|---:|
| Morphology masks | 2,620,885,407 | 0 | 0 |
| WLS correction samples | 11,148,706 | 0.000067433 pixels | 11,148,706 |
| Straightened uint8 crop pixels | 632,638,720 | 1 gray level | 10,328,301 (1.63%) |

Counts include repeated/overlapping work, not unique source pixels. Crop shapes
match exactly. Straightening is checked with fixed Q4 geometry; this does not
qualify crops made from the changed guide fits or establish recognition
invariance. It is a candidate after unchanged CPU detector decisions.

### Every failing experimental page

**The complete experimental API fails the no-discrete-change requirement on
3/54 pages.** The remaining 51 pages pass the declared continuous tolerance
and exact discrete comparison. All observed failures are in statistics;
detector masks, component ownership, line identities and other discrete fields
have no observed changes. The failures are not excluded from timing or totals.
Glyph indices below are zero-based JSON array positions.

| Page | Discrete field differences | Numerical values beyond tolerance | What changed |
|---|---:|---:|---|
| `an-9ea1564fcf4f-p000013` | 2 | 0 | `rule_like` false→true for glyph rows 3881 and 5209. |
| `s2-200e977f2dab5291c42c-p00035` | 1 | 0 | `rule_like` false→true for glyph row 152. |
| `s2-5ca02b142a2a3eaf078a-p00002` | 28 | 13 | Glyph 1508 changes `thickened` true→false and coverage `over_inked`→`intact`; glyph 1629 changes `thickened` false→true. Coverage/legacy counts and derived summaries also change. Largest numeric difference: 1.391191 in readability. |

These are **31 discrete field differences and 13 numerical differences**,
including repeated aggregate consequences, not 31 independently changed glyphs.
Every differing field and both values are retained in
[the full failure audit](q5-gpu-evidence/full-failures.json). An independent
targeted rerun removes only the diagnostic display cap, retains the same
comparison predicates and requires exactly the original failure counts and
maximum errors. This evidence rules out adopting the float32 fit as an
equivalent replacement, even though its kernel error is very small.

## Default-behaviour gate

**PASS: 54/54 pages, 864 API calls per revision, 7,776 fingerprint comparisons,
zero differences.** The fresh Q5 default run exercises all 16 combinations of
tables off/on, statistics off/on and joining off/default/rows/pieces. It checks
parsed records and written JSON, ordered Parquet rows/schema, delivered crop
dimensions/pixels, ownership and detector ink/labels/components/barriers.

The reference is Q4 commit `76ad6fb4f513fb3eb99531cc553899976b4c8801`'s retained
receipt. All 181 pre-existing production Python files were verified byte for
byte against that receipt's source manifest and the commit before reuse. The
current outputs were generated afresh with the unchanged Q4 harness, including
its documented within-page deterministic memoization. No old output supplies a
current detector result. Only Q4's existing, enumerated metadata allowlist is
used; there is no new exclusion, no numeric tolerance, no rounding and no
array sorting. In particular, `geometry_sha256` is checked in this strict gate.

The exact gate took 810.261 seconds with four spawned page workers. That is an
equality-run duration with cached repeated option modes, not a throughput
benchmark. The [comparison](q5-gpu-evidence/default-equality.json),
[current fingerprints](q5-gpu-evidence/default-current.json.gz) and
[reference binding](q5-gpu-evidence/reference-binding.json) preserve the evidence.

## Reproduction

Run from the worktree, one command at a time:

```sh
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
$PY scripts/pages/benchmark_q5.py --prototype-device cpu --repeats 3 --out .astra/q5-cpu-recheck
$PY scripts/pages/benchmark_q5.py --prototype-device mps --repeats 3 --out .astra/q5-mps-recheck
$PY scripts/pages/check_q5_default.py --workers 4 --out .astra/q5-default-recheck
$PY -m pytest -p no:cacheprovider -q
```

Use `--keys KEY ...` for a focused replay and `--batch-size` for a batch sweep.
The later CUDA plan uses the same harness with `--prototype-device cuda`, then
adds device-resident and full neural-chain timings. It does not rent hardware,
submit work, or assume a recogniser architecture on the user's behalf.

## Tests and evidence

**2,353 passed, 16 skipped, zero failures** (2,369 collected), in 98.49 seconds.
The 17 new CPU differential cases cover odd/even morphology origins and borders,
ragged/sparse/outlier/translated WLS contacts, crop tiling and outside-envelope
pixels, empty batches and invalid configuration. Existing orientation tests
remain included and pass. The 16 skips are the existing optional browser cases
whose Chromium executable is absent or cannot launch in this sandbox; no GUI
rendering success is claimed. These CPU tests do not stand in for an MPS run.

Evidence: [environment](q5-gpu-evidence/environment.json),
[all CPU page receipts and raw repetitions](q5-gpu-evidence/cpu.json.gz),
[aggregate measurements](q5-gpu-evidence/measurements.json),
[CPU run log](q5-gpu-evidence/cpu.log.gz),
[MPS allocation failure](q5-gpu-evidence/mps.json.gz),
[full failed-field audit](q5-gpu-evidence/full-failures.json),
[audit reproducer](q5-gpu-evidence/collect-failures.py),
[test log](q5-gpu-evidence/tests.txt),
[test counts](q5-gpu-evidence/tests.json),
[receipt audit](q5-gpu-evidence/receipt-audit.json),
[initial sparse-fit test failure](q5-gpu-evidence/initial-unit-failure.txt.gz),
[first pilot](q5-gpu-evidence/pilot.json.gz), and
[second pilot](q5-gpu-evidence/pilot-v2.json.gz).

Both mandatory gates pass. **Q5 is partial:** the requested MPS execution is
blocked, and the experimental full-API no-decision-change check fails. The
design and CPU measurements are complete; no experimental backend is promoted
into normal page processing.

## Commit handoff

Git staging failed because the sandbox denied creation of the worktree's
`index.lock` (`Operation not permitted`). No commit or push was made. As required
by `.astra/QUEUE_COMMON.md`, `.astra/Q5.patch` and `.astra/commit-Q5.sh` provide
the fallback. The patch is checked and applied in a temporary directory, with
every resulting file compared by SHA-256. The script verifies the Q4 base,
branch, file hashes, patch and commit message before staging only these files;
`--check-only` validates the handoff without committing. Both required commit
trailers are retained.

## Remaining limits

The CPU measurements predict where batching may help, not a CUDA multiplier.
Local fits are already cheap after CPU batching, so a GPU launch and readback
can consume the saving. Straightening has a stronger integration case if page
rasters and the next recogniser stay on-device. The pooling morphology port
needs a more efficient algorithm before its CPU slowdown can inform a fair GPU
comparison. CUDA kernels, launch costs, precision and discrete-memory transfers
differ from this Mac; measure them with the same gates rather than extrapolating
from CPU arithmetic or GPU specifications.

MPS execution and timings are blocked by device allocation in this session.
CUDA, real recogniser output, neural-model contention and complete Docling
throughput remain unmeasured. The full-chain numerical capacity estimate is
therefore anchored only to Q4's observed CPU throughput (11.597 pages/minute with four workers
on its 95 pages), with the missing GPU service time made explicit. A fast
isolated fit does not remove CPU discovery, tables, statistics or transfer
costs. Production adoption requires passing the discrete gate on the target
GPU and improving the complete chain.

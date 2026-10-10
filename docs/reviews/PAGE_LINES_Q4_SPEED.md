# Q4: exact-behaviour performance work

**PARTIAL: 2.23× median speedup.** Exact equality passed on all 95 pages and all 16 Q3b option combinations. The test suite passed (2,336 passed; 16 existing optional browser skips). The 3× median target was not reached.

## Changes

The Q3 API remains the entry point. The changes remove repeated work and move the same operations into array/library calls:

- Prove stable crop masks before peeling: when every retained pixel must remain strong under the original Sauvola and global-floor tests, reuse that mask as whole components are removed. The proof uses the original quantiles and conservative local-mean lower bounds; failure of any condition keeps the original binarization path.
- Reuse the original page ink mask for boundary checks and supplemental table discovery; reuse table rule masks.
- Skip hole, stroke and distance-map descriptors when discovery or statistics only needs geometry. Final statistics still measures each final entity mask. Cache exact component descriptors across overlapping crop windows and peeling passes, keyed by mask, intensities and border contacts.
- Batch the existing RANSAC candidates, end-tracking votes, assignment scores and table ownership comparisons while retaining candidate order and tie rules. Cache invariant support/weights and component lookups for guide fits.
- Use equivalent OpenCV rectangular morphology with the same even-kernel origins and zero borders; use 4-connected background components for the same hole areas. Defer the full-image distance transform until its unchanged faint-component predicate needs it.
- Discard provably impossible diagnostic pairs before the original exact checks. Copy dense scalar curve/neighbor lists directly while retaining independent records.
- Evaluate only the two relevant curve samples, scan glyph masks inside their known bounds, reuse identical statistics summaries, and calculate only the requested quantiles. Write compact JSON with unchanged parsed values.

No detector thresholds were changed, and no tuning or page identities were added to production code. The literal module-constant audit found no changes. Orientation remains opt-in; its existing tests are included in the passing suite.

The peel order remains intact. Mask reuse requires a constant paper percentile, an unchanged global-floor guarantee, and every ink pixel below a conservative lower bound on the original local threshold after any whitening. Integer box sums of floored pixels and outward floating-point error bounds are used only to prove eligibility, never as detector values. Arbitrary whitening differential tests and the complete equality gate check the shortcut. Other crops keep the original local window and repeated binarization; there is no unconditional replacement by the page mask or approximate all-segment peeling.

## Measurement method

Machine: macOS 26.5.1, arm64, 10 logical CPUs; Python 3.11.3 from the repository venv. Dependencies: NumPy 2.4.6, SciPy 1.17.1, OpenCV 5.0.0, Pillow 12.3.0 and PyArrow 25.0.1. BLAS/OpenMP and OpenCV are configured for one compute thread per page worker; the receipt’s thread count records this configuration, not a count of runtime helper threads. Each run processes all 95 pages once; multiprocess runs use spawned page workers. Runs execute sequentially without overlapping tests, profiles, or other benchmark/equality runs. These are one-pass observations, not confidence intervals or thermally controlled laboratory measurements.

Inputs: 54 development PNGs plus 41 book PNGs from six books, with the available development layout regions. The frame is the legacy PNG width/3 and height/3. Tables, joining at default granularity, and statistics are on. The API timer includes lines, segments, structure, cells, checks, delivery, statistics JSON and glyph Parquet writing. Image decoding and layout reading are outside each API timer; batch throughput includes them, spawned-worker startup and temporary-output cleanup. The batch wall timer excludes parent-interpreter setup, source-manifest construction and reference-archive extraction. No prior result is loaded by timing runs. The receipt audit confirms matching input/layout/book identities and output counts across all five timing runs, with stage sums reconciling exactly.

The requested re-profile was completed on unchanged Q3b before editing: `an-d83e7a198ade-p000099`, 24.932 s with cProfile overhead, including 309 crop calls and 313 binarizations. This differs from the older 8.3 s profile supplied with the prompt; all speed ratios below use the fresh 95-page Q3b baseline. Before/after cumulative profiles for the same page are retained with the evidence. Profiler times are not mixed with benchmark times.

On that same page, the final profiled API time is 10.054 s; discovery falls from 7.768 s to 1.565 s. Binarization calls fall from 313 to 84 and their cumulative time from 4.585 s to 0.518 s. Geometry-only crop work replaces the same 309 full-descriptor calls. These are profiler observations for one page, not the reported corpus latency ratio.

## Single-process latency, all 95 pages

| Run | Median s/page | p95 s/page | Worst s/page | Sum API seconds |
| --- | ---: | ---: | ---: | ---: |
| Fresh Q3b | 11.453 | 44.871 | 315.384 | 2175.777 |
| Q4 | 5.137 | 25.139 | 155.656 | 1010.667 |

Median ratio: **2.230×**; p95 ratio: **1.785×**; worst ratio: **2.026×**. Percentiles use NumPy's default linear interpolation. No pages are excluded.

## Exclusive stage times, single process

| Stage | Before median s | After median s | Before p95 s | After p95 s | Before worst s | After worst s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| segmenter | 1.510 | 1.044 | 4.652 | 3.191 | 16.125 | 10.117 |
| line finding | 4.431 | 1.658 | 15.733 | 8.482 | 49.127 | 42.660 |
| ink assignment | 0.467 | 0.088 | 2.064 | 0.390 | 18.084 | 2.683 |
| guide fit | 0.368 | 0.316 | 1.264 | 1.041 | 5.371 | 2.085 |
| table delivery | 0.874 | 0.537 | 9.759 | 5.840 | 160.647 | 55.851 |
| joining | 0.111 | 0.009 | 0.387 | 0.140 | 1.210 | 0.947 |
| statistics | 2.391 | 1.285 | 11.914 | 6.484 | 20.853 | 17.205 |
| checks | 1.106 | 0.328 | 4.139 | 1.648 | 39.173 | 22.216 |
| writing | 0.442 | 0.181 | 1.365 | 0.581 | 4.522 | 1.619 |
| other | 0.014 | 0.014 | 0.051 | 0.058 | 0.270 | 0.272 |

Stage ownership is identical in both runs. Segmenter wraps pixel preparation; ink assignment wraps `_assign`; guide fit wraps pooling, bottom-contact refinement and normal-detector font fits; checks wraps detector diagnostics and structure attachment. Line finding is the remaining normal detector time, including discovery/coalescing. Table delivery is the remaining delivery time, including table-specific single-piece fits and bounded prefix redetection. Joining, statistics and writing wrap their API stages. Nested intervals are subtracted once, so stage sums equal API time; medians of stages do not sum to the median of a page.

## Page-worker throughput

| Revision | Workers | Batch wall seconds | Pages/minute |
| --- | ---: | ---: | ---: |
| Fresh Q3b | 1 | 2181.185 | 2.613 |
| Q4 | 1 | 1016.004 | 5.610 |
| Q4 | 2 | 606.280 | 9.402 |
| Q4 | 4 | 491.517 | 11.597 |
| Q4 | 8 | 488.716 | 11.663 |

Best observed throughput: 8 workers, 11.663 pages/minute.

The 4- and 8-worker runs are within 0.6%; the extra workers did little for batch throughput. Parallel throughput is independent page processing. It does not claim a single-page speedup. The dense table page remains included in every worker count.

## Exact equality gate

Reference: fresh `git archive` of Q3b `32e4920710a014646bf8aeeb832dd7df00234825`, extracted into a temporary directory and imported by its own fresh Python interpreter. The runner asserts the package path belongs to the requested source tree. No historical review output is used as the detector reference.

**95/95 pages, 1,520 API calls per revision, 13,680 output fingerprint comparisons, zero differences.** Options are the Cartesian product of tables off/on, statistics off/on, and joining off/default/rows/pieces. Book identities, source hashes, layout hashes and frame are recorded.

The gate compares parsed JSON values with full floating-point representations, without rounding, coercion or array sorting. It also checks ordered Parquet rows and serialized schema, delivered piece records and crop dimensions/pixels, component ownership, and the detector ink/labels/components/barriers. Only the exact metadata allowlist from `docs/PAGES_OUTPUT_FORMAT.md` is removed. No floating-point tolerance was used: maximum observed coordinate difference is **0 px**, and maximum statistics difference is **0**. Line counts, assignments, discounts, IDs and classes match exactly.

As in Q3b’s equality runner, deterministic detection/delivery/statistics results are memoized only within one page by the complete pickled inputs and returned as independent copies. Both revisions execute their own cache misses; no detector result crosses revisions or comes from a historical file. All option modes also exercise the writer. Crop extraction caches the validation of the same immutable raster and hashes each distinct extraction input using each revision’s own public extraction function. A fresh 16-mode check verified the harness optimization against the earlier fingerprints. Timing runs have none of these stage caches. Equality resumes used only completed receipts with unchanged implementation and input hashes; their elapsed times are not performance measurements.

## Tests and remaining limits

**2,336 passed, 16 skipped, zero failures** (2,352 collected). The 19 added differential cases cover morphology borders/even origins, hole connectivity, mode-count endpoints, deterministic RANSAC ties, bit-exact curve interpolation, component-cache translation, geometry-only descriptor independence, conservative diagnostic pairs, quantiles, run edges and stable-mask reuse under arbitrary whitening. Existing orientation tests pass.

The 16 skips are existing optional browser-rendering cases. Retrying the installed Chromium through `PLAYWRIGHT_BROWSERS_PATH` also failed to launch in the sandbox; no browser-rendering success is claimed. The first intermediate full run caught a missing type annotation on the private mask-reuse keyword; that was fixed before this final suite and final equality candidate.

The largest remaining costs across all 95 pages are:

| Stage | Total seconds | Share of API time |
| --- | ---: | ---: |
| line finding | 275.272 | 27.2% |
| statistics | 228.859 | 22.6% |
| table delivery | 183.752 | 18.2% |
| segmenter | 152.489 | 15.1% |
| checks | 76.263 | 7.5% |

Worst Q4 page: `s2-0ce9d1025b3f23c7119e-p00002` (155.656 s, 11,311 line candidates, 10,202 delivered pieces).

The median target remains unmet. The changes are retained because equality and tests pass and the measured gains are substantial; this report does not label Q4 fully complete. Further work should target the measured remaining stages without substituting thresholds or changing decisions.

## Reproduction and evidence

Run from the worktree with the repository venv and offline environment:

```sh
export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
$PY scripts/pages/benchmark_q4.py timing --reference 32e4920 --out .astra/recheck-before
for n in 1 2 4 8; do
  $PY scripts/pages/benchmark_q4.py timing --workers "$n" --out ".astra/recheck-after-w$n"
done
$PY scripts/pages/benchmark_q4.py equality --reference 32e4920 --workers 2 --out .astra/recheck-reference
$PY scripts/pages/benchmark_q4.py equality --workers 2 --out .astra/recheck-current
$PY scripts/pages/benchmark_q4.py compare --left .astra/recheck-reference --right .astra/recheck-current --out .astra/recheck-equality
$PY -m pytest -p no:cacheprovider -q
```

Use `--keys KEY ...` for a focused reproduction and `--details` on both equality runs for full gzipped diagnostic payloads. Do not overlap timing runs with each other, tests or equality jobs. `--resume` is restricted to equality and checks source/input hashes.

Evidence: [environment](q4-speed-evidence/environment.json), [comparison summary](q4-speed-evidence/equality.json), [fresh reference identity](q4-speed-evidence/reference.json), [reference fingerprints](q4-speed-evidence/reference-equality.json.gz), [current fingerprints](q4-speed-evidence/current-equality.json.gz), [baseline timings](q4-speed-evidence/before.json.gz), [1-worker](q4-speed-evidence/after-w1.json.gz), [2-worker](q4-speed-evidence/after-w2.json.gz), [4-worker](q4-speed-evidence/after-w4.json.gz), [8-worker](q4-speed-evidence/after-w8.json.gz), [tests](q4-speed-evidence/tests.txt), [before profile](q4-speed-evidence/profile-before.txt), [after profile](q4-speed-evidence/profile-after.txt), [constant audit](q4-speed-evidence/constant-audit.json), [receipt audit](q4-speed-evidence/receipt-audit.json). Compressed receipts include every page, stage, input identity and implementation source hash.

## Commit handoff

Git staging is blocked by the sandbox when creating the worktree's `index.lock` (`Operation not permitted`). Following `.astra/QUEUE_COMMON.md`, `.astra/Q4.patch` contains the complete change and `.astra/commit-Q4.sh` checks the base revision and file hashes, then stages and commits the existing working-tree files with the required trailers. The patch was checked and applied to fresh Q3b files in a temporary directory; every resulting file matches the working tree. `.astra/Q4.patch.validation.json` records the patch hash and complete file manifest. No commit or push is claimed from this sandbox.

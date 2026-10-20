# A03: local_ribbons

Isolated Q7 prototype. All 174 allowed pages; orientation parked as in the manifest.

 (rank 3)

**Show:** local curved paths, multi-ridge checks and endpoint completion beyond accepted boxes. **Prediction:** `s2-3229` and `s2-8686` need endpoint/path changes; `an-ffcc` exposes script/diacritic attachment; `s2-77d1` should remain unchanged and avoid dense tracing.

1. Sample sparse normal profiles inside and beyond ends in body-height units. This tests whether the current in-box curve test's blind spot is visible cheaply.
2. Trace only nominated strips using multiple ridge hypotheses and continuity, respecting A02 barriers. Compare against dense R03 measurements. This tests real geometry rather than mean-density movement.
3. Fit a small ribbon and attach supported guides/accents through A07's outputs. Publish measured versus uncertain endpoints and record any neighbour jumps.

**Shared:** S0–S7, A02 barriers, optional A07 profiles; **reference/output:** R03 support tiles and polylines; baseline stays null if only a centreline is identified. **Owns:** E03 local path variants. No full-region graph or independent guide estimator here.


## Reproduce

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.run prototype --approach local_ribbons --phase 2
```

Run shared manifest, baseline and references first; dependencies use saved outputs in the topological order in `../README.md`. Configurations are global in code and experiments.json.

Legend: green retained line candidates, cyan explicit support, amber uncertain requests. Baselines stay null unless supported. Discounted results never reach the renderer. Unreviewed candidates are not claimed corrections.

## Running prediction → result → next-step log

### Step 1 — explicit evidence before the heuristic

Prediction: Sparse endpoint witnesses nominate curved ends, and clean controls avoid dense tracing. Inspect s2-3229200bf47ca465a42d-p00004; s2-86865c33eef5932c013b-p00005; s2-77d1bd63d5babbe0df73-p00001, both supplied sets and agreement controls.

Result: shared S5 supplies all-line original-pixel crops, dense raw support, contrast/persistence and original-size stroke panels. Initial unconstrained ridges jumped rows even on s2-77d1; those are retained as references-v1. Continuity-constrained v2 is a hypothesis, not a truth label.

Next: run the globally fixed witness/variant study; retain per-line differences and abstain on semantic ownership.

### Step 2 — registered fixed-input prototype study

Prediction (before execution): Sparse endpoint witnesses nominate curved ends, and clean controls avoid dense tracing. On s2-3229200bf47ca465a42d-p00004; s2-86865c33eef5932c013b-p00005; s2-77d1bd63d5babbe0df73-p00001. All other supplied pages and 40 agreement controls test generality. Lengths use body-height proxies/page fractions; no page-name decisions.

Duplicate check: E00 maps, ER dense supports, S2 primitives and saved dependency products are reused. The registry keys image, dependencies, algorithm/source and fixed configuration; successful repeated calls are cache hits.

Measured result: `{"agreement": {"max": 0.095363125030417, "n": 40, "p50": 0.032091812521684915, "p95": 0.08392988186387808}, "changed_count_pages": 0, "development": {"max": 0.3639353329781443, "n": 53, "p50": 0.06411999999545515, "p95": 0.23397308301646258}, "discrepancy": {"max": 0.25383966602385044, "n": 80, "p50": 0.05182656249962747, "p95": 0.2000695847498718}, "total_records": 174}`. These are marginal times with diagnostic inputs reused, not complete page latency.

Next: inspect changed regions and raw supports; compare against the fresh composed path. No automatic acceptance from counts or old-model overlap.

### Visual result before composition

The clean control `s2-77d1bd63d5babbe0df73-p00001` refutes the prediction:
several straight bands are needlessly retraced; the President signature bends toward
its neighbour and some endpoints shrink to map support. The current `old_inside`
check does not actually guarantee endpoint preservation. On `s2-3229…p00004`,
multi-ridge abstention leaves most straddles unresolved. These are failures, not
successful corrections inferred from a small numeric discrepancy.

Next: keep this as a negative prototype and time its actual cost; do not promote
it into a clean-page product. Round 2 needs explicit per-end ownership and a
non-crossing, support-preserving acceptance check. No page-specific exception is added.
### Step 3 — freeze and next decision

Result: raw measurements in the linked `summary.json` and per-page evidence, including all failures/unknowns. No detector rerun or parameter reselection.

Next: use the reviewed findings and failure list in FAST_LINES_ROUND1_RESULTS.md. A candidate is not promoted based on agreement with the old detector.

## Final inspected findings and measured limits

Result: The clean-control prediction failed: `s2-77d1bd63d5babbe0df73-p00001` has unnecessary retracing, a signature pulled toward its neighbour, and clipped ends. `s2-3229200bf47ca465a42d-p00004` largely remains unresolved after multi-ridge abstention. Preserving item count is not preserving geometry.

Measured marginal study cost: agreement: p50 0.032092 s, p95 0.083930 s, max 0.095363 s; discrepancy: p50 0.051827 s, p95 0.200070 s, max 0.253840 s. Shared dependencies were reused; these are not fresh-page added times. See the results report for fresh composition timing.

Next: Do not promote this repair. Replace the endpoint acceptance check, preserve supported extents, and enforce neighbour ownership/noncrossing before another runtime claim.

[Output gallery](../../../.astra/fast_lines/out/local_ribbons/index.html) · [All failures and unknowns](../../../.astra/fast_lines/out/local_ribbons/page_failures.json) · [Round-1 report](../../../docs/research/FAST_LINES_ROUND1_RESULTS.md).

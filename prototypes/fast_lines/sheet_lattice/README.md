# A04: sheet_lattice

Isolated Q7 prototype. All 174 allowed pages; orientation parked as in the manifest.

 (rank 4)

**Show:** shared per-leaf displacement, local pitch/phase and cheap box audits. **Prediction:** coherent left bend on `s2-3229` reduces repeated per-line fitting; `s2-8686` tests whether fragments suffice for a shared field; `an-d83e7` defeats a single pitch across sizes; `an-c8b9` defeats a single sheet across the spread.

1. Compute robust box-tilt initialisers, strip correlations, anchor supports and multiple pitch candidates using S3. Render phase ambiguity and alternative grid membership for A05, retaining different physical leaves/blocks. This tests F01/F02 directly without assuming a regular page.
2. Fit separate affine-plus-smooth leaf fields; compare sparse fit against the independently dense R04 support. This tests whether sheet physics predicts held-back anchors **within dev pages**, not held-out pages.
3. Transport paths, report residuals and dispatch local failures to A03. Compare one shared field to A03 on the same geometry requests, reusing its results. This measures marginal cost and structural failure, not two duplicated benchmarks.

**Shared:** S0–S7, A02 leaf blocks; **reference/output:** R04 mesh/residual stages, transformed JSON and pitch/phase strips. **Owns:** E04 field/lattice fit. Full external dewarper adapters remain deferred A15.


## Reproduce

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.run prototype --approach sheet_lattice --phase 2
```

Run shared manifest, baseline and references first; dependencies use saved outputs in the topological order in `../README.md`. Configurations are global in code and experiments.json.

Legend: green retained line candidates, cyan explicit support, amber uncertain requests. Baselines stay null unless supported. Discounted results never reach the renderer. Unreviewed candidates are not claimed corrections.

## Running prediction → result → next-step log

### Step 1 — explicit evidence before the heuristic

Prediction: Several lines can share a displacement but mixed leaves and sizes defeat one field. Inspect s2-3229200bf47ca465a42d-p00004; an-c8b96a901917-p000068; an-d83e7a198ade-p000099, both supplied sets and agreement controls.

Result: shared S5 supplies all-line original-pixel crops, dense raw support, contrast/persistence and original-size stroke panels. Initial unconstrained ridges jumped rows even on s2-77d1; those are retained as references-v1. Continuity-constrained v2 is a hypothesis, not a truth label.

Next: run the globally fixed witness/variant study; retain per-line differences and abstain on semantic ownership.

### Step 2 — registered fixed-input prototype study

Prediction (before execution): Several lines can share a displacement but mixed leaves and sizes defeat one field. On s2-3229200bf47ca465a42d-p00004; an-c8b96a901917-p000068; an-d83e7a198ade-p000099. All other supplied pages and 40 agreement controls test generality. Lengths use body-height proxies/page fractions; no page-name decisions.

Duplicate check: E00 maps, ER dense supports, S2 primitives and saved dependency products are reused. The registry keys image, dependencies, algorithm/source and fixed configuration; successful repeated calls are cache hits.

Measured result: `{"agreement": {"max": 0.030504083028063178, "n": 40, "p50": 0.013573937496403232, "p95": 0.021371446159901098}, "changed_count_pages": 0, "development": {"max": 0.06001320801442489, "n": 53, "p50": 0.017098499985877424, "p95": 0.04407040837686508}, "discrepancy": {"max": 0.06213099998421967, "n": 80, "p50": 0.0129669375019148, "p95": 0.03822300210013054}, "total_records": 174}`. These are marginal times with diagnostic inputs reused, not complete page latency.

Next: inspect changed regions and raw supports; compare against the fresh composed path. No automatic acceptance from counts or old-model overlap.

### Step 3 — freeze and next decision

Result: raw measurements in the linked `summary.json` and per-page evidence, including all failures/unknowns. No detector rerun or parameter reselection.

Next: use the reviewed findings and failure list in FAST_LINES_ROUND1_RESULTS.md. A candidate is not promoted based on agreement with the old detector.

## Final inspected findings and measured limits

Result: It makes shared geometry and residuals inspectable, but blocks are not verified physical leaves. Sparse fragments and mixed sizes remain underconstrained. `s2-3229200bf47ca465a42d-p00004`, `s2-86865c33eef5932c013b-p00005`, and `an-d83e7a198ade-p000099` are the key unresolved cases; no independent curl-accuracy success is established.

Measured marginal study cost: agreement: p50 0.013574 s, p95 0.021371 s, max 0.030504 s; discrepancy: p50 0.012967 s, p95 0.038223 s, max 0.062131 s. Shared dependencies were reused; these are not fresh-page added times. See the results report for fresh composition timing.

Next: Use explicit leaf/column assignment, fit/train anchor separation and residual coverage. Keep local alternatives instead of imposing one sheet on a spread.

[Output gallery](../../../.astra/fast_lines/out/sheet_lattice/index.html) · [All failures and unknowns](../../../.astra/fast_lines/out/sheet_lattice/page_failures.json) · [Round-1 report](../../../docs/research/FAST_LINES_ROUND1_RESULTS.md).

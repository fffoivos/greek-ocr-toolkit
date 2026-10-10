# A10: ink_condition

Isolated Q7 prototype. All 174 allowed pages; orientation parked as in the manifest.

 (rank 10)

**Show:** ink-condition evidence distinct from faintness and font weight. **Prediction:** `s2-8686` yields useful damaged/dense stroke examples; `an-3352`/`an-ef48` expose noise and fragmentation; bold/display material in `an-1f8e` is a counterexample to declaring all thick strokes over-inked. Actual unreadability is unresolved until original-size review.

1. Select representative suspect component groups using existing evidence, then render width, skeleton endpoints, counters and threshold variants from S2. This tests whether the proposed grammar is visible at all.
2. Compare local family-conditioned samples to dense R10 patches and a smooth condition field with explicit local exceptions. This tests F08 without assuming page-wide uniform damage.
3. Emit independent contrast/width/fragmentation axes and broken/filled/unknown hypotheses; obtain visual verdicts. Do not synthesise repaired glyphs or turn a heuristic into a definitive readability label.

**Shared:** S0–S7, A05/A07; **reference/output:** R10 original-size patch sheets and condition overlays on retained lines. **Owns:** E10 stroke/condition study. A12 imports the same width/persistence products.


## Reproduce

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.run prototype --approach ink_condition --phase 2
```

Run shared manifest, baseline and references first; dependencies use saved outputs in the topological order in `../README.md`. Configurations are global in code and experiments.json.

Legend: green retained line candidates, cyan explicit support, amber uncertain requests. Baselines stay null unless supported. Discounted results never reach the renderer. Unreviewed candidates are not claimed corrections.

## Running prediction → result → next-step log

### Step 1 — explicit evidence before the heuristic

Prediction: Stroke axes differ from darkness; bold and detached accents defeat automatic damage labels. Inspect s2-86865c33eef5932c013b-p00005; an-3352d912f2e9-p000104; an-1f8e7d022643-p000003, both supplied sets and agreement controls.

Result: shared S5 supplies all-line original-pixel crops, dense raw support, contrast/persistence and original-size stroke panels. Initial unconstrained ridges jumped rows even on s2-77d1; those are retained as references-v1. Continuity-constrained v2 is a hypothesis, not a truth label.

Next: run the globally fixed witness/variant study; retain per-line differences and abstain on semantic ownership.

### Step 2 — registered fixed-input prototype study

Prediction (before execution): Stroke axes differ from darkness; bold and detached accents defeat automatic damage labels. On s2-86865c33eef5932c013b-p00005; an-3352d912f2e9-p000104; an-1f8e7d022643-p000003. All other supplied pages and 40 agreement controls test generality. Lengths use body-height proxies/page fractions; no page-name decisions.

Duplicate check: E00 maps, ER dense supports, S2 primitives and saved dependency products are reused. The registry keys image, dependencies, algorithm/source and fixed configuration; successful repeated calls are cache hits.

Measured result: `{"agreement": {"max": 0.033224958984646946, "n": 40, "p50": 0.016895582986762747, "p95": 0.027529774655704383}, "changed_count_pages": 0, "development": {"max": 0.07706383394543082, "n": 53, "p50": 0.021565958042629063, "p95": 0.043338608602061866}, "discrepancy": {"max": 0.05284454202046618, "n": 80, "p50": 0.01906995798344724, "p95": 0.03867548989655913}, "total_records": 174}`. These are marginal times with diagnostic inputs reused, not complete page latency.

Next: inspect changed regions and raw supports; compare against the fresh composed path. No automatic acceptance from counts or old-model overlap.

### Step 3 — freeze and next decision

Result: raw measurements in the linked `summary.json` and per-page evidence, including all failures/unknowns. No detector rerun or parameter reselection.

Next: use the reviewed findings and failure list in FAST_LINES_ROUND1_RESULTS.md. A candidate is not promoted based on agreement with the old detector.

## Final inspected findings and measured limits

Result: Condition and faintness are separate numbers. `s2-86865c33eef5932c013b-p00005` has 63 measured samples but no automatic damage attribution; readability is unknown. `an-1f8e7d022643-p000003` bold/display text and `an-3352d912f2e9-p000104` noise remain counterexamples. No verified unreadability classification.

Measured marginal study cost: agreement: p50 0.016896 s, p95 0.027530 s, max 0.033225 s; discrepancy: p50 0.019070 s, p95 0.038675 s, max 0.052845 s. Shared dependencies were reused; these are not fresh-page added times. See the results report for fresh composition timing.

Next: Review original-size glyph groups against the dense threshold panels; improve family matching before interpreting width or fragmentation as damage.

[Output gallery](../../../.astra/fast_lines/out/ink_condition/index.html) · [All failures and unknowns](../../../.astra/fast_lines/out/ink_condition/page_failures.json) · [Round-1 report](../../../docs/research/FAST_LINES_ROUND1_RESULTS.md).

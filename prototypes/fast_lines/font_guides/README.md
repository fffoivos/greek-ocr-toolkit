# A07: font_guides

Isolated Q7 prototype. All 174 allowed pages; orientation parked as in the manifest.

 (rank 7)

**Show:** compatible local type families, letter-height intervals, supported guides and honest borrowing. **Prediction:** `an-ffcc` needs separate script/profile treatment; `an-d83e7` separates large verse and tiny apparatus; `an-e745` needs local family changes; `an-1f8e` display spacing must not dictate body spacing.

1. Build exemplar groups using body profiles, scale and spacing from a few credible lines; show the grouped crops. This tests compatibility without font recognition.
2. Stack aligned profiles and estimate only supported body/baseline/extent/accent modes, comparing to R07 and ours' displayed hypotheses. This tests an adaptive guide count against a fixed six-guide assumption.
3. Borrow within a compatible block, recording residual checks, reset and unknown cases. This measures whether sharing saves work without propagating a wrong font/guide estimate.

**Shared:** S0–S7; **reference/output:** R07 exemplar atlas, guide overlay stages and evidence JSON; line JSON only for supported geometry. **Owns:** E07 all body/guide/spacing estimation. No independent x-height algorithm in other prototypes; book identity work is deferred A13.


## Reproduce

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.run prototype --approach font_guides --phase 2
```

Run shared manifest, baseline and references first; dependencies use saved outputs in the topological order in `../README.md`. Configurations are global in code and experiments.json.

Legend: green retained line candidates, cyan explicit support, amber uncertain requests. Baselines stay null unless supported. Discounted results never reach the renderer. Unreviewed candidates are not claimed corrections.

## Running prediction → result → next-step log

### Step 1 — explicit evidence before the heuristic

Prediction: Local profile families separate scales; baseline and accent semantics often remain unknown. Inspect an-ffccc97c07de-p000152; an-d83e7a198ade-p000099; an-e74539ae215c-p000338, both supplied sets and agreement controls.

Result: shared S5 supplies all-line original-pixel crops, dense raw support, contrast/persistence and original-size stroke panels. Initial unconstrained ridges jumped rows even on s2-77d1; those are retained as references-v1. Continuity-constrained v2 is a hypothesis, not a truth label.

Next: run the globally fixed witness/variant study; retain per-line differences and abstain on semantic ownership.

### Step 2 — registered fixed-input prototype study

Prediction (before execution): Local profile families separate scales; baseline and accent semantics often remain unknown. On an-ffccc97c07de-p000152; an-d83e7a198ade-p000099; an-e74539ae215c-p000338. All other supplied pages and 40 agreement controls test generality. Lengths use body-height proxies/page fractions; no page-name decisions.

Duplicate check: E00 maps, ER dense supports, S2 primitives and saved dependency products are reused. The registry keys image, dependencies, algorithm/source and fixed configuration; successful repeated calls are cache hits.

Measured result: `{"agreement": {"max": 0.01988512498792261, "n": 40, "p50": 0.010427167027955875, "p95": 0.01756939821352716}, "changed_count_pages": 0, "development": {"max": 0.24121845798799768, "n": 53, "p50": 0.017913333023898304, "p95": 0.06553284201072523}, "discrepancy": {"max": 0.08213191694812849, "n": 80, "p50": 0.01445758351474069, "p95": 0.05112621694570406}, "total_records": 174}`. These are marginal times with diagnostic inputs reused, not complete page latency.

Next: inspect changed regions and raw supports; compare against the fresh composed path. No automatic acceptance from counts or old-model overlap.

### Step 3 — freeze and next decision

Result: raw measurements in the linked `summary.json` and per-page evidence, including all failures/unknowns. No detector rerun or parameter reselection.

Next: use the reviewed findings and failure list in FAST_LINES_ROUND1_RESULTS.md. A candidate is not promoted based on agreement with the old detector.

## Final inspected findings and measured limits

Result: Adaptive mode counts are available, but baseline/accent semantics remain unknown. `an-ffccc97c07de-p000152` has 25 families for 34 bands and visually mixed Arabic-row extents; `an-d83e7a198ade-p000099` has 65 families for 120 bands. This is overfragmented for a useful shared type prior.

Measured marginal study cost: agreement: p50 0.010427 s, p95 0.017569 s, max 0.019885 s; discrepancy: p50 0.014458 s, p95 0.051126 s, max 0.082132 s. Shared dependencies were reused; these are not fresh-page added times. See the results report for fresh composition timing.

Next: Build compatible block exemplar stacks and attach components to guide modes. Test actual amortisation and reject borrowing across mixed scripts/scales.

[Output gallery](../../../.astra/fast_lines/out/font_guides/index.html) · [All failures and unknowns](../../../.astra/fast_lines/out/font_guides/page_failures.json) · [Round-1 report](../../../docs/research/FAST_LINES_ROUND1_RESULTS.md).

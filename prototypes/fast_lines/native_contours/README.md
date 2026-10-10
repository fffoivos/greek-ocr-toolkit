# A01: native_contours

Isolated Q7 prototype. All 174 allowed pages; orientation parked as in the manifest.

 (rank 1)

**Show:** whether existing map geometry and documented controls already correct bands. **Prediction:** polygons improve some left bend on `s2-3229`; reducing expansion can reduce overlap, but neither restores missing right-end response on `s2-8686` nor necessarily splits `an-a73d`. Lower thresholds risk ghosts on `s2-0ce9` and ornament on `an-1f8e`.

1. Record the source-pinned DB defaults/config and replay baseline quad/poly on one saved float map per page. This identifies representation losses without a second network pass.
2. Run one global compact study: baseline quad, baseline poly, and lower/higher map threshold, box-score threshold and expansion around the recorded baseline poly (eight configurations total). Values are fixed globally before results; constrain probabilities to valid ranges. Inspect dilation and score-mode support; add at most one justified paired ablation, recorded in the registry, if rejection genealogy implicates it. No Cartesian sweep.
3. Inspect end/accent/merge and rejection changes; freeze a documented candidate config or conclude native controls are insufficient. Emit variant results and genealogy, preserving regression cases.

**Shared:** S0/S1/S3–S7; **reference/output:** R01 plus original-size crops, quad/poly detector JSON and stage images. **Owns:** E01, all fixed-map DB control sweeps. Input-size experiments belong solely to A09.


## Reproduce

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.run prototype --approach native_contours --phase 2
```

Run shared manifest, baseline and references first; dependencies use saved outputs in the topological order in `../README.md`. Configurations are global in code and experiments.json.

Legend: green retained line candidates, cyan explicit support, amber uncertain requests. Baselines stay null unless supported. Discounted results never reach the renderer. Unreviewed candidates are not claimed corrections.

## Running prediction → result → next-step log

### Step 1 — explicit evidence before the heuristic

Prediction: Existing contours preserve some bent geometry; thresholds trade pale fronts against ghosts. Inspect s2-3229200bf47ca465a42d-p00004; s2-0ce9d1025b3f23c7119e-p00001, both supplied sets and agreement controls.

Result: shared S5 supplies all-line original-pixel crops, dense raw support, contrast/persistence and original-size stroke panels. Initial unconstrained ridges jumped rows even on s2-77d1; those are retained as references-v1. Continuity-constrained v2 is a hypothesis, not a truth label.

Next: run the globally fixed witness/variant study; retain per-line differences and abstain on semantic ownership.

### Step 2 — registered fixed-input prototype study

Prediction (before execution): Existing contours preserve some bent geometry; thresholds trade pale fronts against ghosts. On s2-3229200bf47ca465a42d-p00004; s2-0ce9d1025b3f23c7119e-p00001. All other supplied pages and 40 agreement controls test generality. Lengths use body-height proxies/page fractions; no page-name decisions.

Duplicate check: E00 maps, ER dense supports, S2 primitives and saved dependency products are reused. The registry keys image, dependencies, algorithm/source and fixed configuration; successful repeated calls are cache hits.

Measured result: `{"agreement": {"max": 0.015081332996487617, "n": 40, "p50": 0.003890041494742036, "p95": 0.013349326470051888}, "changed_count_pages": 82, "development": {"max": 0.056337792018894106, "n": 53, "p50": 0.0067757919896394014, "p95": 0.02245889137266202}, "discrepancy": {"max": 0.027141249971464276, "n": 80, "p50": 0.0064858749974519014, "p95": 0.02156306043034419}, "total_records": 174}`. These are marginal times with diagnostic inputs reused, not complete page latency.

Next: inspect changed regions and raw supports; compare against the fresh composed path. No automatic acceptance from counts or old-model overlap.

### Control-study disposition

The pinned DB source supports optional 2×2 network-map dilation and fast versus
contour score modes. No observed rejection genealogy justified adding the optional
paired ablation, so the globally frozen eight configurations are the whole study.
Native polygons retain some shape on `s2-3229…p00004`, but cross-gutter merges on
`an-a73d…p000301` and lower-left fragments remain. No threshold configuration is
selected by matching the old detector. Use the same-map poly-960 result when
isolating the effect of A09's poly-1440 sampling comparator.
### Step 3 — freeze and next decision

Result: raw measurements in the linked `summary.json` and per-page evidence, including all failures/unknowns. No detector rerun or parameter reselection.

Next: use the reviewed findings and failure list in FAST_LINES_ROUND1_RESULTS.md. A candidate is not promoted based on agreement with the old detector.

## Final inspected findings and measured limits

Result: Polygons preserve local contour shape but do not repair topology. `s2-3229200bf47ca465a42d-p00004` retains bent contours and lower-left fragments; `an-a73d22211479-p000301` still crosses the rule. Lower-threshold outputs are diagnostic variants, not a selected accuracy winner.

Measured marginal study cost: agreement: p50 0.003890 s, p95 0.013349 s, max 0.015081 s; discrepancy: p50 0.006486 s, p95 0.021563 s, max 0.027141 s. Shared dependencies were reused; these are not fresh-page added times. See the results report for fresh composition timing.

Next: Keep contour genealogy and compare polygon versus local geometry only on adjudicated ends. No global control setting is accepted as superior.

[Output gallery](../../../.astra/fast_lines/out/native_contours/index.html) · [All failures and unknowns](../../../.astra/fast_lines/out/native_contours/page_failures.json) · [Round-1 report](../../../docs/research/FAST_LINES_ROUND1_RESULTS.md).

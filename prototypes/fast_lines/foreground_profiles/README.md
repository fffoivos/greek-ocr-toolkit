# A05: foreground_profiles

Isolated Q7 prototype. All 174 allowed pages; orientation parked as in the manifest.

 (rank 5)

**Show:** foreground/ghost/unknown evidence separate from darkness. **Prediction:** `s2-09f5` should lose many scout nominations without deleting the right body; `s2-0ce9` challenges sharp ghost rejection; `an-1be6` must retain weak front print; `an-ef48` exposes a poor paper estimate.

1. Render contrast, edge spread and threshold-persistence profiles from shared S2 on nominated regions and matched credible front samples. This makes the physical hypothesis inspectable.
2. Compare contrast-only, normalised edge and combined witnesses using the same samples. Reuse A04's competing pitch/phase/skew grids as coordinator C04's additional explicit witness; display memberships on `s2-0ce9` and `s2-93f807`. This tests whether sharpness or a second grid adds separation. A dominant grid is not automatically front, and in-register verso defeats the cue.
3. Assign cautious ownership/unknown outputs and test sparse versus dense agreement. Retain overlap ambiguity; report preserved/lost pale fronts explicitly.

**Shared:** S0–S7, A07 compatibility when available; **reference/output:** R05 tiles, ownership masks and decision records, optional retained-line JSON. **Owns:** E05 foreground witness study. No source-layer restoration or separate threshold sweep elsewhere.


## Reproduce

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.run prototype --approach foreground_profiles --phase 2
```

Run shared manifest, baseline and references first; dependencies use saved outputs in the topological order in `../README.md`. Configurations are global in code and experiments.json.

Legend: green retained line candidates, cyan explicit support, amber uncertain requests. Baselines stay null unless supported. Discounted results never reach the renderer. Unreviewed candidates are not claimed corrections.

## Running prediction → result → next-step log

### Step 1 — explicit evidence before the heuristic

Prediction: Contrast and edge cues expose uncertainty; sharp ghosts prevent safe automatic rejection. Inspect s2-09f5dfca4af4d74173c6-p00005; s2-0ce9d1025b3f23c7119e-p00001; an-1be60011c435-p000215, both supplied sets and agreement controls.

Result: shared S5 supplies all-line original-pixel crops, dense raw support, contrast/persistence and original-size stroke panels. Initial unconstrained ridges jumped rows even on s2-77d1; those are retained as references-v1. Continuity-constrained v2 is a hypothesis, not a truth label.

Next: run the globally fixed witness/variant study; retain per-line differences and abstain on semantic ownership.

### Step 2 — registered fixed-input prototype study

Prediction (before execution): Contrast and edge cues expose uncertainty; sharp ghosts prevent safe automatic rejection. On s2-09f5dfca4af4d74173c6-p00005; s2-0ce9d1025b3f23c7119e-p00001; an-1be60011c435-p000215. All other supplied pages and 40 agreement controls test generality. Lengths use body-height proxies/page fractions; no page-name decisions.

Duplicate check: E00 maps, ER dense supports, S2 primitives and saved dependency products are reused. The registry keys image, dependencies, algorithm/source and fixed configuration; successful repeated calls are cache hits.

Measured result: `{"agreement": {"max": 0.0029363330104388297, "n": 40, "p50": 0.0020620625000447035, "p95": 0.002567893723607994}, "changed_count_pages": 0, "development": {"max": 0.01607716700527817, "n": 53, "p50": 0.002702082972973585, "p95": 0.006591799971647557}, "discrepancy": {"max": 0.007336415990721434, "n": 80, "p50": 0.0024036245013121516, "p95": 0.005355541652534157}, "total_records": 174}`. These are marginal times with diagnostic inputs reused, not complete page latency.

Next: inspect changed regions and raw supports; compare against the fresh composed path. No automatic acceptance from counts or old-model overlap.

### Step 3 — freeze and next decision

Result: raw measurements in the linked `summary.json` and per-page evidence, including all failures/unknowns. No detector rerun or parameter reselection.

Next: use the reviewed findings and failure list in FAST_LINES_ROUND1_RESULTS.md. A candidate is not promoted based on agreement with the old detector.

## Final inspected findings and measured limits

Result: All ownership remains unknown and existing pale fronts are retained. On `s2-09f5dfca4af4d74173c6-p00005` and `an-1be60011c435-p000215`, contrast-only flags are zero and edge-only flags are three each: this does not separate ghosts from pale fronts. `s2-0ce9d1025b3f23c7119e-p00001` remains a sharp-ghost counterexample. No verified false-positive removal.

Measured marginal study cost: agreement: p50 0.002062 s, p95 0.002568 s, max 0.002936 s; discrepancy: p50 0.002404 s, p95 0.005356 s, max 0.007336 s. Shared dependencies were reused; these are not fresh-page added times. See the results report for fresh composition timing.

Next: Materialise actual cross-stroke edge-spread measurements and matched front/ghost exemplars. Do not turn relative darkness or the dominant grid into ownership.

[Output gallery](../../../.astra/fast_lines/out/foreground_profiles/index.html) · [All failures and unknowns](../../../.astra/fast_lines/out/foreground_profiles/page_failures.json) · [Round-1 report](../../../docs/research/FAST_LINES_ROUND1_RESULTS.md).

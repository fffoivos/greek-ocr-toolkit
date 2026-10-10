# A11: map_graph

Isolated Q7 prototype. All 174 allowed pages; orientation parked as in the manifest.

 (rank 11)

**Show:** a regional map-only topology fallback, distinct from local ribbon correction. **Prediction:** map-present fragments on `s2-3229`/`s2-4959` may join without raw-ink noise; absent tiny-map response on `an-d83e7` cannot be restored; `an-a73d` requires imported barriers to prevent the same crossing.

1. Reuse A06's region requests, map ridges and barriers; build a minimal noncrossing seam/line graph. This tests regional grouping without reimplementing our full model.
2. Compare to A03 on exactly the same relevant regions and R03/R06 references. This identifies complementary wins versus redundancy.
3. Publish only supported paths plus unresolved map-blind requests routed to A12/A09. Negative or redundant results are retained in the final comparison.

**Shared:** S0–S7, A02/A06/A07; **reference/output:** R03/R06 graph/path stages and line JSON. **Owns:** E11 regional map topology. No new map run, threshold sweep or independent benchmark set.


## Reproduce

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.run prototype --approach map_graph --phase 2
```

Run shared manifest, baseline and references first; dependencies use saved outputs in the topological order in `../README.md`. Configurations are global in code and experiments.json.

Legend: green retained line candidates, cyan explicit support, amber uncertain requests. Baselines stay null unless supported. Discounted results never reach the renderer. Unreviewed candidates are not claimed corrections.

## Running prediction → result → next-step log

### Step 1 — explicit evidence before the heuristic

Prediction: Regional map paths join some fragments but cannot recover map-absent fronts. Inspect s2-49598b2e848ab1f0ee1e-p00001; an-d83e7a198ade-p000099, both supplied sets and agreement controls.

Result: shared S5 supplies all-line original-pixel crops, dense raw support, contrast/persistence and original-size stroke panels. Initial unconstrained ridges jumped rows even on s2-77d1; those are retained as references-v1. Continuity-constrained v2 is a hypothesis, not a truth label.

Next: run the globally fixed witness/variant study; retain per-line differences and abstain on semantic ownership.

### Step 2 — registered fixed-input prototype study

Prediction (before execution): Regional map paths join some fragments but cannot recover map-absent fronts. On s2-49598b2e848ab1f0ee1e-p00001; an-d83e7a198ade-p000099. All other supplied pages and 40 agreement controls test generality. Lengths use body-height proxies/page fractions; no page-name decisions.

Duplicate check: E00 maps, ER dense supports, S2 primitives and saved dependency products are reused. The registry keys image, dependencies, algorithm/source and fixed configuration; successful repeated calls are cache hits.

Measured result: `{"agreement": {"max": 0.45272891700733453, "n": 40, "p50": 0.2200562709767837, "p95": 0.41875231102749233}, "changed_count_pages": 44, "development": {"max": 1.258282708004117, "n": 53, "p50": 0.31965616601519287, "p95": 0.7642679586075246}, "discrepancy": {"max": 0.9561052090139128, "n": 80, "p50": 0.24313577098655514, "p95": 0.7709841544623486}, "total_records": 174}`. These are marginal times with diagnostic inputs reused, not complete page latency.

Next: inspect changed regions and raw supports; compare against the fresh composed path. No automatic acceptance from counts or old-model overlap.

### Step 3 — freeze and next decision

Result: raw measurements in the linked `summary.json` and per-page evidence, including all failures/unknowns. No detector rerun or parameter reselection.

Next: use the reviewed findings and failure list in FAST_LINES_ROUND1_RESULTS.md. A candidate is not promoted based on agreement with the old detector.

## Final inspected findings and measured limits

Result: Its map-only candidates cannot restore absent evidence. It does not solve ownership or validate topology merely by having strong map support. `s2-49598b2e848ab1f0ee1e-p00001` and `s2-86865c33eef5932c013b-p00007` provide review candidates; tiny apparatus on `an-d83e7a198ade-p000099` and ghosts remain unresolved. The inspected `s2-86865c33eef5932c013b-p00007` result is a regression: twelve additional candidates include thin overlapping bands over already boxed text, and the severe right-end curl remains. Its 68 paths are not 68 useful lines. The clean development control adds zero candidates from 37 paths.

Measured marginal study cost: agreement: p50 0.220056 s, p95 0.418752 s, max 0.452729 s; discrepancy: p50 0.243136 s, p95 0.770984 s, max 0.956105 s. Shared dependencies were reused; these are not fresh-page added times. See the results report for fresh composition timing.

Next: Compare request by request with A03 using the saved line evidence and original pixels; keep only complementary, adjudicated geometry. No second network or independent request set.

[Output gallery](../../../.astra/fast_lines/out/map_graph/index.html) · [All failures and unknowns](../../../.astra/fast_lines/out/map_graph/page_failures.json) · [Round-1 report](../../../docs/research/FAST_LINES_ROUND1_RESULTS.md).

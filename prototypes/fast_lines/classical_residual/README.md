# A12: classical_residual

Isolated Q7 prototype. All 174 allowed pages; orientation parked as in the manifest.

 (rank 12)

**Show:** a bounded map-independent fallback from stable intensity regions and stroke-supported grouping. **Prediction:** some faint/map-weak fronts in `an-1be6`/`s2-4959` may be nominated independently; `s2-09f5`/`s2-0ce9` will demonstrate that stable, coherent strokes also describe ghosts; `an-ffcc` challenges component-to-glyph assumptions.

1. In the same frozen A06 regions, construct intensity-stable components and reuse stroke-width features; show them without premature acceptance. This tests whether independent evidence exists where the map is weak.
2. Add a simple normalised neighbour graph constrained by A02/A07 and compare persistence-only versus persistence-plus-width. This tests the classical literature addition with one shared implementation of each primitive.
3. Run one coarse full-page diagnostic with that same algorithm on each upright page to expose completely absent blocks. Compare the triggered version against this offline view and cost it separately. Keep wrong ghost nominations and unresolved ownership visible.

**Shared:** S0–S7, A02/A05/A06/A07/A10; **reference/output:** R05/R06/R10 component/stroke/graph stages and reviewed line JSON. **Owns:** E12 classical grouping. This is the bounded twelfth experiment, not permission for a new global production detector.


## Reproduce

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.run prototype --approach classical_residual --phase 2
```

Run shared manifest, baseline and references first; dependencies use saved outputs in the topological order in `../README.md`. Configurations are global in code and experiments.json.

Legend: green retained line candidates, cyan explicit support, amber uncertain requests. Baselines stay null unless supported. Discounted results never reach the renderer. Unreviewed candidates are not claimed corrections.

## Running prediction → result → next-step log

### Step 1 — explicit evidence before the heuristic

Prediction: Stable regions supply independent candidates but also form coherent ghost lines. Inspect an-1be60011c435-p000215; s2-09f5dfca4af4d74173c6-p00005; s2-0ce9d1025b3f23c7119e-p00001, both supplied sets and agreement controls.

Result: shared S5 supplies all-line original-pixel crops, dense raw support, contrast/persistence and original-size stroke panels. Initial unconstrained ridges jumped rows even on s2-77d1; those are retained as references-v1. Continuity-constrained v2 is a hypothesis, not a truth label.

Next: run the globally fixed witness/variant study; retain per-line differences and abstain on semantic ownership.

### Step 2 — registered fixed-input prototype study

Prediction (before execution): Stable regions supply independent candidates but also form coherent ghost lines. On an-1be60011c435-p000215; s2-09f5dfca4af4d74173c6-p00005; s2-0ce9d1025b3f23c7119e-p00001. All other supplied pages and 40 agreement controls test generality. Lengths use body-height proxies/page fractions; no page-name decisions.

Duplicate check: E00 maps, ER dense supports, S2 primitives and saved dependency products are reused. The registry keys image, dependencies, algorithm/source and fixed configuration; successful repeated calls are cache hits.

Measured result: `{"agreement": {"max": 0.31485687504755333, "n": 40, "p50": 0.08797999998205341, "p95": 0.2925252464279765}, "changed_count_pages": 109, "development": {"max": 1.359529624984134, "n": 53, "p50": 0.14157749997684732, "p95": 0.6773142089834434}, "discrepancy": {"max": 1.0524664580007084, "n": 80, "p50": 0.08536106249084696, "p95": 0.6541795523837204}, "total_records": 174}`. These are marginal times with diagnostic inputs reused, not complete page latency.

Next: inspect changed regions and raw supports; compare against the fresh composed path. No automatic acceptance from counts or old-model overlap.

### Step 3 — freeze and next decision

Result: raw measurements in the linked `summary.json` and per-page evidence, including all failures/unknowns. No detector rerun or parameter reselection.

Next: use the reviewed findings and failure list in FAST_LINES_ROUND1_RESULTS.md. A candidate is not promoted based on agreement with the old detector.


## Export audit follow-up — prediction before correction

The optional persistence, persistence-width and full-page comparator exports for
`s2-86865c33eef5932c013b-p00007` contain an out-of-page polygon; the main result
is already bounded. This is an export inconsistency, not evidence of recovery.
Prediction: routing all detector exports through the existing shared clipping
contract fixes these three JSON files without changing any in-page candidate,
main result, timing, request or experimental decision. Preserve the original
exports, then recheck all 2595 saved comparator/variant files. No inference.


Result: all 2595 exports now pass. Exactly three changed, each by only
2.2737367544323206e-13 pixels at the edge (floating-point rounding). Main
results and all timings are unchanged; originals remain in the audit archive.
Next: retain the shared export contract and its regression test. This correction
has no bearing on the unresolved line-recovery quality.

## Final inspected findings and measured limits

Result: It provides map-independent candidates, not foreground decisions. Stable coherent ghost print on `s2-09f5dfca4af4d74173c6-p00005` and `s2-0ce9d1025b3f23c7119e-p00001` defeats the premise that stability alone means front. Pale `an-1be60011c435-p000215` and mixed-script `an-ffccc97c07de-p000152` require component-level review. On `s2-86865c33eef5932c013b-p00007`, fourteen extra candidates include narrow fragments and isolated marks; the main curl remains. The clean development control `s2-77d1bd63d5babbe0df73-p00001` gains one unvalidated candidate. Neither is demonstrated missing-line recovery.

Measured marginal study cost: agreement: p50 0.087980 s, p95 0.292525 s, max 0.314857 s; discrepancy: p50 0.085361 s, p95 0.654180 s, max 1.052466 s. Shared dependencies were reused; these are not fresh-page added times. See the results report for fresh composition timing.

Next: Reuse stroke primitives and common requests; do not turn the coarse full-page diagnostic into an always-on detector. Review accents, touching components and every accepted new candidate.

[Output gallery](../../../.astra/fast_lines/out/classical_residual/index.html) · [All failures and unknowns](../../../.astra/fast_lines/out/classical_residual/page_failures.json) · [Round-1 report](../../../docs/research/FAST_LINES_ROUND1_RESULTS.md).

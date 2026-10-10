# A02: layout_barriers

Isolated Q7 prototype. All 174 allowed pages; orientation parked as in the manifest.

 (rank 2)

**Show:** a fast explicit representation of leaves, columns, rules and cell constraints. **Prediction:** `an-a73d` cross-gutter boxes split despite zero residual-ink flags. `an-c8b9` needs four text columns on two leaves; `s2-200e` and `an-7a2b` expose rule/cell grouping, while `an-a3c2` and centred headings resist blind splitting.

1. Render coarse whitespace persistence, long runs and candidate separators once. This separates an actual gutter from a single word gap or a dash.
2. Build block-local barrier/cell graphs and mark crossed Paddle bands; nominate full-resolution checks only there. This tests whether the cheap graph can stand in for explicit ink/rule inspection.
3. Split only supported crossings, keep spanning text and uncertain cells, and publish assignments and failures. Inside a supported table region preserve small-detector cell boxes by default: no prose-slot filling, cross-cell merging or shared curl fit. A real cell-text error needs its own explicit evidence. This establishes barriers reusable by all later line graphs; it does not require a Docling call.

**Shared:** S0–S7; **reference/output:** R02 mask/graph stages, split-line JSON, uncertainty ledger. **Owns:** E02 barrier/rule experiments; no duplicate table detector in another folder.


## Reproduce

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.run prototype --approach layout_barriers --phase 2
```

Run shared manifest, baseline and references first; dependencies use saved outputs in the topological order in `../README.md`. Configurations are global in code and experiments.json.

Legend: green retained line candidates, cyan explicit support, amber uncertain requests. Baselines stay null unless supported. Discounted results never reach the renderer. Unreviewed candidates are not claimed corrections.

## Running prediction → result → next-step log

### Step 1 — explicit evidence before the heuristic

Prediction: Persistent separators split merged prose columns while table cell boxes remain intact. Inspect an-a73d22211479-p000301; an-a73d22211479-p000141; s2-661ddf05c8865e7b2c45-p00005, both supplied sets and agreement controls.

Result: shared S5 supplies all-line original-pixel crops, dense raw support, contrast/persistence and original-size stroke panels. Initial unconstrained ridges jumped rows even on s2-77d1; those are retained as references-v1. Continuity-constrained v2 is a hypothesis, not a truth label.

Next: run the globally fixed witness/variant study; retain per-line differences and abstain on semantic ownership.

### Step 2 — registered fixed-input prototype study

Prediction (before execution): Persistent separators split merged prose columns while table cell boxes remain intact. On an-a73d22211479-p000301; an-a73d22211479-p000141; s2-661ddf05c8865e7b2c45-p00005. All other supplied pages and 40 agreement controls test generality. Lengths use body-height proxies/page fractions; no page-name decisions.

Duplicate check: E00 maps, ER dense supports, S2 primitives and saved dependency products are reused. The registry keys image, dependencies, algorithm/source and fixed configuration; successful repeated calls are cache hits.

Measured result: `{"agreement": {"max": 0.016564791032578796, "n": 40, "p50": 0.01178287499351427, "p95": 0.015580550362938084}, "changed_count_pages": 40, "development": {"max": 0.01768749998882413, "n": 53, "p50": 0.012254292028956115, "p95": 0.016548175422940403}, "discrepancy": {"max": 0.01874329097336158, "n": 80, "p50": 0.013471479498548433, "p95": 0.016603722612489942}, "total_records": 174}`. These are marginal times with diagnostic inputs reused, not complete page latency.

Next: inspect changed regions and raw supports; compare against the fresh composed path. No automatic acceptance from counts or old-model overlap.

### Follow-up prediction — separators that skew, after inspecting the first outputs

Measured: the axis-aligned run prototype made no split on either `an-a73d` page,
and mislabelled the ruled newspaper `s2-661ddf…p00005` as a table. It did preserve
`an-7a2b` and left the clean `s2-77d1` unchanged. This refutes the main success
prediction, despite a low measured marginal time (~12–13 ms median).

Prediction before the next step: a long sloped rule can be made explicit as a
supported segment, whereas a vertical morphology kernel loses it. Use a shared
native Hough operator with lengths in body heights, then verify ink continuously
along each segment. A table needs intersections at distinct row/column positions;
fragmented pieces of one header rule are not several table rows. This is a physical
mechanism change applied globally, not a page-specific threshold adjustment.

Next: retain v1 artifacts, render supported sloped segments and recompute the
crossing split on all 174 pages. Reuse cached baseline, primitive and reference
measurements. Re-run only descendants whose dependency receipt changes.
### Step 2 — registered fixed-input prototype study

Prediction (before execution): Persistent separators split merged prose columns while table cell boxes remain intact. On an-a73d22211479-p000301; an-a73d22211479-p000141; s2-661ddf05c8865e7b2c45-p00005. All other supplied pages and 40 agreement controls test generality. Lengths use body-height proxies/page fractions; no page-name decisions.

Duplicate check: E00 maps, ER dense supports, S2 primitives and saved dependency products are reused. The registry keys image, dependencies, algorithm/source and fixed configuration; successful repeated calls are cache hits.

Measured result: `{"agreement": {"n": 0}, "changed_count_pages": 3, "development": {"max": 1.2596994999912567, "n": 2, "p50": 0.714277333492646, "p95": 1.2051572833413957}, "discrepancy": {"max": 0.16957550001097843, "n": 2, "p50": 0.1569612085004337, "p95": 0.16831407085992395}, "total_records": 4}`. These are marginal times with diagnostic inputs reused, not complete page latency.

Next: inspect changed regions and raw supports; compare against the fresh composed path. No automatic acceptance from counts or old-model overlap.

### Step 2 — registered fixed-input prototype study

Prediction (before execution): Persistent separators split merged prose columns while table cell boxes remain intact. On an-a73d22211479-p000301; an-a73d22211479-p000141; s2-661ddf05c8865e7b2c45-p00005. All other supplied pages and 40 agreement controls test generality. Lengths use body-height proxies/page fractions; no page-name decisions.

Duplicate check: E00 maps, ER dense supports, S2 primitives and saved dependency products are reused. The registry keys image, dependencies, algorithm/source and fixed configuration; successful repeated calls are cache hits.

### Sloped-rule check result

The four-page preflight supports the mechanism: 40 split crossings on development
`an-a73d22211479-p000301`, 36 on discrepancy `an-a73d22211479-p000141`, and 52 on
discrepancy `s2-661ddf05c8865e7b2c45-p00005`. The newspaper is no longer called a
table. The inspected overlays separate the two visible prose columns. The dense
`an-7a2b17a3fb0f-p000200` table remains unchanged.

Cost refutes the hoped-for cheap check: respectively 0.168855, 0.169576, 0.144347,
and 1.259699 seconds marginally. Hough on dense ink is expensive. These observations
authorise the already-planned all-page follow-up, not production adoption. Every
new split remains subject to detailed character/heading review.

Next: measure all cohorts and the fresh runtime path; round 2 must materialise a
cheap separator witness before dense segment search. Earlier fallback experiments
retain A02 v1 and their frozen requests. Their evidence is not retroactively changed.
Measured result: `{"agreement": {"max": 0.9624573329929262, "n": 40, "p50": 0.22965327047859319, "p95": 0.8684700881276511}, "changed_count_pages": 96, "development": {"max": 1.2596994999912567, "n": 53, "p50": 0.16885516699403524, "p95": 0.46331102458061646}, "discrepancy": {"max": 0.8309972499846481, "n": 80, "p50": 0.1840134999656584, "p95": 0.5885538853617617}, "total_records": 174}`. These are marginal times with diagnostic inputs reused, not complete page latency.

Next: inspect changed regions and raw supports; compare against the fresh composed path. No automatic acceptance from counts or old-model overlap.

### Step 3 — freeze and next decision

Result: raw measurements in the linked `summary.json` and per-page evidence, including all failures/unknowns. No detector rerun or parameter reselection.

Next: use the reviewed findings and failure list in FAST_LINES_ROUND1_RESULTS.md. A candidate is not promoted based on agreement with the old detector.

## Final inspected findings and measured limits

Result: V1 failed both `an-a73d22211479-p000301` and `an-a73d22211479-p000141`, and falsely protected newspaper `s2-661ddf05c8865e7b2c45-p00005` as a table. This prompted a globally applied, explicitly supported sloped-rule revision and distinct grid intersections. Its final named-page findings are recorded below. `an-7a2b17a3fb0f-p000200` is a table-preservation check, not an accuracy label.

Measured marginal study cost: agreement: p50 0.229653 s, p95 0.868470 s, max 0.962457 s; discrepancy: p50 0.184013 s, p95 0.588554 s, max 0.830997 s. Shared dependencies were reused; these are not fresh-page added times. See the results report for fresh composition timing.

Next: Prioritise explicit separators, then validate spanning headings, local cell/leaf identity and every new split. Do not call the provisional block list a physical leaf model.

[Output gallery](../../../.astra/fast_lines/out/layout_barriers/index.html) · [All failures and unknowns](../../../.astra/fast_lines/out/layout_barriers/page_failures.json) · [Round-1 report](../../../docs/research/FAST_LINES_ROUND1_RESULTS.md).

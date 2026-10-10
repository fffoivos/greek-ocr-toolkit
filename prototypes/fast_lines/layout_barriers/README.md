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

## Q8 — materialise rule-backed separators

Choice, before experiments: materialise A02, with a genuinely conditional runtime.
It has the clearest Q7 visible success and an explicit physical witness: a printed
rule between columns. Keep Q7's code and saved evidence as the dense reference.
Retire the unconditional A02/A03 composition from this new path: Hough over every
page is wasteful, and A03's endpoint/ownership regression remains unresolved.
Do not repeat native-contour sweeps or recovery studies. Unused book/duplex dreams
still lack verified identity/pairing; mirrored histograms lack spatial ownership.
Neither warrants replacing a concrete separator experiment.

### R2.1 prediction — scope and explicit rendering first

Freeze exactly the 54 development and 141 direction-labelled supplied images,
including the 21 added pages. Reuse the 174 Q7 baselines and dense A02 products;
materialise only missing baseline/reference products. Render raw pixels beside
Q7's supported rules, each crossing, and every line decision before implementing
the fast gate. Expect the two `an-a73d` pages and `s2-661ddf…p00005` to expose real
column splits; expect whitespace-only Q7 splits to be less safe on centred text,
lists and verse. Check all directions, not just detector count disagreements.

Next: inspect the dense rule/crossing images; implement a sparse run/segment
witness with letter-height lengths, then refine only witnessed crossings. Preserve
the original slanted polygon by clipping it; never turn a tilted box into its
axis-aligned bounding rectangle. A full table/cell/physical-leaf solver is not
presupposed. Claims of no changes will be checked by exact polygon identity.

### Planned verification and receipts

Each phase uses the shared registry and fresh source/input hashes, and refuses
duplicate successful experiments. Final timing will include preprocessing,
inference, DB postprocessing, every gate dependency and conditional correction;
three intentional warm repetitions in a seeded order, decode and review I/O
separate, startup separate. Review every page and every changed line, with
direction-specific wins/failures in a tracked ledger. Output lives only under
`.astra/fast_lines/out/round2/rule_separators/`. Green is added geometry, red
removed ink, and changed polygons are drawn over their old box. Discounted
old-model lines are never loaded into these overlays. Ours is not a reference.

### R2.1 result → R2.2 prediction

The supplied set is exactly 195 pages (194 upright): directions 41 ours_more,
46 paddle_more, 8 both, 46 neither on the 141 new pages; 40 are agreement controls.
The rule on `an-a73d…p000301` and `s2-661ddf…p00005` visibly runs between separate
columns. The dense table reference `an-7a2b…p000200` has many intersecting rules;
clean `s2-77d1…p00001` has no vertical separator. Q7 reference files were reused;
only the 21 newly supplied pages needed inference and dense layout evidence.

Prediction before R2.2: a short horizontal tolerance followed by a 12-body-height
vertical opening will nominate near-vertical rules without dense Hough voting.
Only a rule crossed well inside at least three boxes calls original-pixel
verification. Fit the rule from its raw support and require an empty corridor
beside it; repeated text stems should fail that support test. Restrict this path
to rule-backed splits; whitespace-only layouts and severe curvature abstain.
Preserve tables with multiple intersecting rows. Expect both `an-a73d` cases and
the newspaper to split, and all 40 agreement controls to retain exact geometry.
This is an expectation, not a claimed result. Export every per-line decision,
compare with the dense reference, and inspect every changed polygon.

### R2.2 result → R2.3 prediction

R2.2 (`study-0af417179e22`) nominates 20 pages and changes ten. Zero agreement
controls are nominated or changed. It misses the development `an-a73d…p000301`
rule entirely, only splits 12 boxes on `…p000141`, and rejects the newspaper's
three nominated segments as discontinuous. It also splits two boxes inside
`s2-200e…p00035`, a table-preservation failure. Raw median added time is 25.044 ms
(single diagnostic run, not the final benchmark).

The sampled body height is only six pixels (the a73d page becomes 300×426), so
thin rules disappear during downsampling; the darkest-pixel verifier can follow
nearby letters. Prediction: twelve samples per body plus bridging breaks shorter
than half a body will retain thin rules. Average vertical support over two body
heights before fitting to prevent individual letters stealing the fit. Preserve
regions bounded by at least two horizontal rules and two vertical runs, including
sparse tables with only a header and bottom rule. Use integer area reduction before
the final resize: it preserves integrated ink while avoiding the slow arbitrary
large-ratio resize. No parameter is keyed to a page. Expect the named misses to
improve and the table changes to disappear; rerun only this changed algorithm.

### R2.3 result → R2.4 prediction

R2.3 (`study-4d93d1a18156`) recovers 40 cuts on development `an-a73d…p000301`
and 39 on `…p000141`. The visible separator is correct, but original vertical
straddles remain in some boxes: splitting columns is not a complete line repair.
The clean controls still incur no corrections. The newspaper's rule verifier
still abstains. The proposed enclosing-grid test fails on sparse currency tables:
`s2-200e…p00035` now has eight unwanted cuts through drachma/lepta groups, and
`s2-831…p00020` nine. The correct action here is to preserve Paddle's cell unit.

Prediction: restrict this materialised path to wide text on both sides of the
rule (six body heights per side instead of two). This is an explicit scope
restriction to prose-width column crossings; short entries/marginalia remain
unresolved. It should reject these currency divisions before any correction work
while retaining the long prose and name-list column splits. Retire the ineffective
enclosing-grid branch; retain the existing three-intersection preservation check.
Do not weaken raw rule verification to rescue the newspaper. Verify every changed
line, including any sparse-table header that still gets through; then freeze.

### R2.4 result → R2.5 prediction

The width restriction removes all changes on both named currency tables; 18 pages
still change, with the same main prose-column gains. A new physical invariant test
fails (42/43 pass): a solid heading crossing the rule fills the narrow comparison
strip and is mistakenly treated as its own paper. This is a photometry bug, not
permission to ignore the test. Prediction: estimate paper from a neighbourhood
extended by one body height above/below the line, keeping the same corridor and
threshold, so the spanning ink veto can see that solid ink. This should preserve
the synthetic heading and may reject additional questionable real crossings.
Next: run the changed tests, materialise this new source once, inspect final lines,
then measure three intentional fresh-page repetitions.

### R2.5 result → R2.6 prediction

All 43 isolated prototype tests now pass. The changed paper estimate vetoes one
additional crossing each on `s2-a0e…p00002` and `s2-c0b…p00005`; 18 pages still
change. All 195 explicit reference overviews have been inspected, including the
21 extra pages. Many dense Hough hypotheses visibly follow aligned letters,
stamps and borders: these are comparison evidence, not a truth annotation.

R2.6 freezes algorithm `f186b9c26f02` for final review and measurement. Render
each changed seam twice (raw pixels and changed geometry), retain its original
line ID, and compare every baseline line with the dense rule hypotheses. Expect
clear column-boundary improvements, but inherited vertical straddles on the
wide merged boxes. Review all 195 output overviews and all 332 changed source
boxes (the renderer will count exactly), then adjudicate without the ours model.

Benchmark prediction: zero corrections on the 40 agreement controls, less than
34 ms median added time there, and every activated correction below one second.
Three intentional, registry-keyed repetitions use freshly decoded pixels, fresh
small-model inference and fresh DB postprocessing; no cached maps or boxes enter
the timed path. Measure decode, session startup and warmup separately. Publish
the first measured output and all raw times, comparing it with the frozen study.

### R2.6 result — final source frozen

The exact count is 308 changed source boxes, not the rough 332 in the prediction:
18 changed pages, 24 nominated pages, 177 exactly unchanged pages. Inspected all
195 final page overviews and all 25 raw/overlay seam boards (every changed seam).
Every inspected cut follows a printed separator between independent text, with
no new glyph cut observed. This is a boundary improvement count, **not** 308 fully
correct lines: inherited multirow boxes and top/bottom overlaps remain.

Fresh benchmark: 585 measured executions (195 pages × three declared repeats),
exactly matching cached baselines and the frozen study in every pass. Agreement:
10.937604 ms median added, 13.500564 ms p95, 23.169292 ms maximum; zero correction
calls and zero changes. Activated corrections: 7.311666 ms median, 14.671167 ms
maximum. Maximum total addition including scout is 41.655791 ms. This meets the
subsecond budget comfortably; approximately 9% agreement overhead is an honest
improvement over Q7, not a claim of zero/negligible cost for every application.

There are clear failures outside and inside this scope. `s2-661ddf…p00005`,
`s2-49598…p00005` and `s2-d12a…p00008` retain column joins after verification
abstains. `an-1ba3…p000009` retains a plainly missing body line. `an-ef481…p000151`
retains mirrored bleed-through boxes. The same unresolved omission/ownership
problems appear in the both-direction group. No missing-text recovery or whole
false-box rejection is claimed. All failures seen, all changed pages and the
limits of overview inspection are recorded in the round-two report and review
ledger. The earlier currency-table and synthetic heading regressions were fixed.

Next work: validate this narrow optional module on owner-held unseen pages; then
build an independent, inexpensive residual-ink witness for missing text and a
spatial foreground-ownership verifier for false boxes. Repair vertical straddles
locally after a verified column split. Do not simply relax the faint-rule gate or
restore unconditional A03. No additional algorithm experiment is planned here.

Entry point: `layout_barriers.fast.run(gray, paddle_items)`. The Q7 `run.py` remains
the explicit reference; the old unconditional composition is not used by Q8.
The harness is `python -m prototypes.fast_lines.round2` with phases `references`,
`study`, `review`, `benchmark`, `publish`. Completed experiments are registry
protected. `python -m prototypes.fast_lines.validate_round2` validates artifacts
without detector execution. All use the charter's Python and bytecode setting.

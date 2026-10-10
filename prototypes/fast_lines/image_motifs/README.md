# A08: image_motifs

Isolated Q7 prototype. All 174 allowed pages; orientation parked as in the manifest.

 (rank 8)

**Show:** image/frame/motif ownership that protects text. **Prediction:** `an-d600` engraving stops driving speculative line recovery while vignette lettering stays inspectable; `an-1f8e` repeated border separates from display title; stamp overlaps in `an-7781` resist rectangular suppression; leaders in `s2-200e` remain structural evidence.

1. Render coarse directional support and candidate repeated crops in residual-rich regions. This tests text-band versus area texture without a deep image model.
2. Compute regional motif similarity/autocorrelation, boundary and optional ring/tall-initial evidence only when triggered. This tests F11's addition against repeated characters/digits and semantic marks.
3. Publish region ownership and suppress unsupported new proposals; separately adjudicate any existing line rejection. This measures false-positive reduction and protected embedded text.

**Shared:** S0–S7, A02/A05/A07; **reference/output:** R08 repeated crop pairs, ownership stages, retained-line JSON. **Owns:** E08 picture/motif study. No colour experiment: Q6 measured 54/54 grayscale pages.


## Reproduce

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.run prototype --approach image_motifs --phase 2
```

Run shared manifest, baseline and references first; dependencies use saved outputs in the topological order in `../README.md`. Configurations are global in code and experiments.json.

Legend: green retained line candidates, cyan explicit support, amber uncertain requests. Baselines stay null unless supported. Discounted results never reach the renderer. Unreviewed candidates are not claimed corrections.

## Running prediction → result → next-step log

### Step 1 — explicit evidence before the heuristic

Prediction: Area texture suppresses some speculative engraving recovery without erasing detected lettering. Inspect an-d6002cf45e4d-p000058; an-1f8e7d022643-p000003; an-778126cc8c2b-p000010, both supplied sets and agreement controls.

Result: shared S5 supplies all-line original-pixel crops, dense raw support, contrast/persistence and original-size stroke panels. Initial unconstrained ridges jumped rows even on s2-77d1; those are retained as references-v1. Continuity-constrained v2 is a hypothesis, not a truth label.

Next: run the globally fixed witness/variant study; retain per-line differences and abstain on semantic ownership.

### Step 2 — registered fixed-input prototype study

Prediction (before execution): Area texture suppresses some speculative engraving recovery without erasing detected lettering. On an-d6002cf45e4d-p000058; an-1f8e7d022643-p000003; an-778126cc8c2b-p000010. All other supplied pages and 40 agreement controls test generality. Lengths use body-height proxies/page fractions; no page-name decisions.

Duplicate check: E00 maps, ER dense supports, S2 primitives and saved dependency products are reused. The registry keys image, dependencies, algorithm/source and fixed configuration; successful repeated calls are cache hits.

Measured result: `{"agreement": {"max": 0.012411915988195688, "n": 40, "p50": 0.008364479028386995, "p95": 0.01227931037719827}, "changed_count_pages": 0, "development": {"max": 0.019824333023279905, "n": 53, "p50": 0.008991333015728742, "p95": 0.013100333418697119}, "discrepancy": {"max": 0.015394582995213568, "n": 80, "p50": 0.010082208493258804, "p95": 0.012935960761387833}, "total_records": 174}`. These are marginal times with diagnostic inputs reused, not complete page latency.

Next: inspect changed regions and raw supports; compare against the fresh composed path. No automatic acceptance from counts or old-model overlap.

### Step 3 — freeze and next decision

Result: raw measurements in the linked `summary.json` and per-page evidence, including all failures/unknowns. No detector rerun or parameter reselection.

Next: use the reviewed findings and failure list in FAST_LINES_ROUND1_RESULTS.md. A candidate is not promoted based on agreement with the old detector.

## Final inspected findings and measured limits

Result: On `an-d6002cf45e4d-p000058`, the engraving and decorative initial become texture regions while all existing lettering remains. The region extends beyond the picture and is not an exact boundary. On `an-1f8e7d022643-p000003`, ornament boxes remain; repeated glyph versus ornament ownership is unresolved. `an-778126cc8c2b-p000010` remains an overlap challenge.

Measured marginal study cost: agreement: p50 0.008364 s, p95 0.012279 s, max 0.012412 s; discrepancy: p50 0.010082 s, p95 0.012936 s, max 0.015395 s. Shared dependencies were reused; these are not fresh-page added times. See the results report for fresh composition timing.

Next: Keep the new-proposal-only veto as a candidate, refine support boundaries and review every suppressed crop. Existing line rejection needs separate evidence.

[Output gallery](../../../.astra/fast_lines/out/image_motifs/index.html) · [All failures and unknowns](../../../.astra/fast_lines/out/image_motifs/page_failures.json) · [Round-1 report](../../../docs/research/FAST_LINES_ROUND1_RESULTS.md).

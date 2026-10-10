# A09: selective_rerun

Isolated Q7 prototype. All 174 allowed pages; orientation parked as in the manifest.

 (rank 9)

**Show:** whether the cost of another inference restores genuinely missing information. **Prediction:** tiny cells/apparatus on `an-7a2b`/`an-d83e7` may improve with sampling; `s2-8686` may benefit from scale/unbend; `s2-0ce9` may gain undesirable ghosts. Clean controls should issue zero crop requests.

1. Use shared height/map-resolution uncertainty to merge crop requests. Run **one full-page larger-input comparator** per upright page at a single globally chosen scale factor, cached here alone. This distinguishes resolution limitations from crop-context effects; it is offline diagnostic cost, not the clean runtime path.
2. On frozen relevant requests compare scale-only, unbend-only and combined reruns with identical remap code. This separates information gain from coordinate flattening; charge actual tensor sizes and every call.
3. Deduplicate at seams with S4 and expose conflicting ownership. Compare benefits, crop area, number of calls and latency against the same baseline; publish cases where doing nothing wins.

**Shared:** S0–S8, A02/A04/A06/A07; **reference/output:** R09, map-before/after stages and remapped detector JSON. **Owns:** E09 every input-size/crop/unbend neural experiment. Do not add local threshold tuning; use A01's recorded configurations.


## Reproduce

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.run prototype --approach selective_rerun --phase 2
```

Run shared manifest, baseline and references first; dependencies use saved outputs in the topological order in `../README.md`. Configurations are global in code and experiments.json.

Legend: green retained line candidates, cyan explicit support, amber uncertain requests. Baselines stay null unless supported. Discounted results never reach the renderer. Unreviewed candidates are not claimed corrections.

## Running prediction → result → next-step log

### Step 1 — explicit evidence before the heuristic

Prediction: More samples recover tiny structure and also ghosts; crop inference may cost a full pass. Inspect an-7a2b17a3fb0f-p000200; an-d83e7a198ade-p000099; s2-0ce9d1025b3f23c7119e-p00001, both supplied sets and agreement controls.

Result: shared S5 supplies all-line original-pixel crops, dense raw support, contrast/persistence and original-size stroke panels. Initial unconstrained ridges jumped rows even on s2-77d1; those are retained as references-v1. Continuity-constrained v2 is a hypothesis, not a truth label.

Next: run the globally fixed witness/variant study; retain per-line differences and abstain on semantic ownership.

### Step 2 — registered fixed-input prototype study

Prediction (before execution): More samples recover tiny structure and also ghosts; crop inference may cost a full pass. On an-7a2b17a3fb0f-p000200; an-d83e7a198ade-p000099; s2-0ce9d1025b3f23c7119e-p00001. All other supplied pages and 40 agreement controls test generality. Lengths use body-height proxies/page fractions; no page-name decisions.

Duplicate check: E00 maps, ER dense supports, S2 primitives and saved dependency products are reused. The registry keys image, dependencies, algorithm/source and fixed configuration; successful repeated calls are cache hits.

Measured result: `{"agreement": {"max": 0.8929135840153322, "n": 40, "p50": 0.3553581249725539, "p95": 0.6335695000452687}, "changed_count_pages": 49, "development": {"max": 1.122427417023573, "n": 53, "p50": 0.42469683301169425, "p95": 0.8516482417704536}, "discrepancy": {"max": 1.1599440420395695, "n": 80, "p50": 0.4436688129499089, "p95": 0.8521190185041632}, "total_records": 174}`. These are marginal times with diagnostic inputs reused, not complete page latency.

Next: inspect changed regions and raw supports; compare against the fresh composed path. No automatic acceptance from counts or old-model overlap.

### Step 3 — freeze and next decision

Result: raw measurements in the linked `summary.json` and per-page evidence, including all failures/unknowns. No detector rerun or parameter reselection.

Next: use the reviewed findings and failure list in FAST_LINES_ROUND1_RESULTS.md. A candidate is not promoted based on agreement with the old detector.

## Final inspected findings and measured limits

Result: Actual tensor dimensions and all crop calls are saved. The three-request budget explicitly leaves requests unresolved. Increased item count cannot establish missing-line recovery; inspect `an-d83e7a198ade-p000099`, `an-7a2b17a3fb0f-p000200`, `s2-86865c33eef5932c013b-p00007`, and ghost-rich `s2-0ce9d1025b3f23c7119e-p00001`. Where no shared field is supported, unbend is the identity and is labelled by its zero shift. On clean development control `s2-77d1bd63d5babbe0df73-p00001`, nine calls add no candidates and leave eight requests unscheduled. On `s2-86865c33eef5932c013b-p00007`, ten extra candidates include isolated ditto/letter marks, while broad bands still straddle at the curved right edge. On `s2-d12a9a4feb23254f4080-p00009`, nine calls add no candidates and leave 23 requests unscheduled.

Measured marginal study cost: agreement: p50 0.355358 s, p95 0.633570 s, max 0.892914 s; discrepancy: p50 0.443669 s, p95 0.852119 s, max 1.159944 s. Shared dependencies were reused; these are not fresh-page added times. See the results report for fresh composition timing.

Next: First fix request quality, then adjudicate actual tiny-front gains and new ghost detections. Do not infer cost from crop area; use the recorded tensor/call cost.

[Output gallery](../../../.astra/fast_lines/out/selective_rerun/index.html) · [All failures and unknowns](../../../.astra/fast_lines/out/selective_rerun/page_failures.json) · [Round-1 report](../../../docs/research/FAST_LINES_ROUND1_RESULTS.md).

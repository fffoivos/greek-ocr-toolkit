# A06: residual_ledger

Isolated Q7 prototype. All 174 allowed pages; orientation parked as in the manifest.

 (rank 6)

**Show:** useful missing-text nominations without flooding the page with ghost/picture candidates. **Prediction:** `an-fd4fa` lower continuation, `s2-4959` first-word areas and `an-5c09` marginal/running-head cases nominate plausible misses; `s2-09f5` and `an-d600` must shrink the flood. `an-a73d` must still be handled by A02, not claimed as a residual success.

1. Render actual unexplained support separately from envelope subtraction using the shared baseline and physical/layout evidence. This reveals whether oversized boxes conceal omissions.
2. Add a page-wide coarse image scout and both rhythm-gap and off-rhythm requests. This tests whole-block and margin blindness. No rhythm slot becomes a line without ink.
3. Save one frozen `RegionRequest` set with nomination reasons; ask A03/A11/A12/A09 for geometry where relevant. Compare raw candidate counts, visually supported cases, false alarms and unexplained remainder to the supplied stage scout, without treating its 102 disagreements as labels.

**Shared:** S0–S8, A02/A05/A07/A08 products; **reference/output:** R06 ownership/residual stages and request JSON, retained recovered lines after review. **Owns:** E06 request nomination and fixed request corpus used by the other fallbacks.


## Reproduce

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.run prototype --approach residual_ledger --phase 2
```

Run shared manifest, baseline and references first; dependencies use saved outputs in the topological order in `../README.md`. Configurations are global in code and experiments.json.

Legend: green retained line candidates, cyan explicit support, amber uncertain requests. Baselines stay null unless supported. Discounted results never reach the renderer. Unreviewed candidates are not claimed corrections.

## Running prediction → result → next-step log

### Step 1 — explicit evidence before the heuristic

Prediction: Support subtraction reveals omissions hidden by envelopes but still nominates ghosts. Inspect an-fd4fa0018ae1-p000037; s2-49598b2e848ab1f0ee1e-p00001; an-d6002cf45e4d-p000058, both supplied sets and agreement controls.

Result: shared S5 supplies all-line original-pixel crops, dense raw support, contrast/persistence and original-size stroke panels. Initial unconstrained ridges jumped rows even on s2-77d1; those are retained as references-v1. Continuity-constrained v2 is a hypothesis, not a truth label.

Next: run the globally fixed witness/variant study; retain per-line differences and abstain on semantic ownership.

### Step 2 — registered fixed-input prototype study

Prediction (before execution): Support subtraction reveals omissions hidden by envelopes but still nominates ghosts. On an-fd4fa0018ae1-p000037; s2-49598b2e848ab1f0ee1e-p00001; an-d6002cf45e4d-p000058. All other supplied pages and 40 agreement controls test generality. Lengths use body-height proxies/page fractions; no page-name decisions.

Duplicate check: E00 maps, ER dense supports, S2 primitives and saved dependency products are reused. The registry keys image, dependencies, algorithm/source and fixed configuration; successful repeated calls are cache hits.

Measured result: `{"agreement": {"max": 0.025459708995185792, "n": 40, "p50": 0.006171541986986995, "p95": 0.01578743091085925}, "changed_count_pages": 0, "development": {"max": 0.03070791595382616, "n": 53, "p50": 0.00822750001680106, "p95": 0.013206008390989154}, "discrepancy": {"max": 0.03933787503046915, "n": 80, "p50": 0.007229458482470363, "p95": 0.014553435432026163}, "total_records": 174}`. These are marginal times with diagnostic inputs reused, not complete page latency.

Next: inspect changed regions and raw supports; compare against the fresh composed path. No automatic acceptance from counts or old-model overlap.

### Step 3 — freeze and next decision

Result: raw measurements in the linked `summary.json` and per-page evidence, including all failures/unknowns. No detector rerun or parameter reselection.

Next: use the reviewed findings and failure list in FAST_LINES_ROUND1_RESULTS.md. A candidate is not promoted based on agreement with the old detector.

## Final inspected findings and measured limits

Result: `s2-77d1bd63d5babbe0df73-p00001` produces 70 raw nominations merged to 11 requests despite being a clean control. `s2-09f5dfca4af4d74173c6-p00005` produces zero accepted-size regions while 263116 support-residual pixels remain: the component size filter hides a large region; this is not successful ghost classification. `an-d6002cf45e4d-p000058` has 21 nominations, 10 texture vetoes and seven merged requests.

Measured marginal study cost: agreement: p50 0.006172 s, p95 0.015787 s, max 0.025460 s; discrepancy: p50 0.007229 s, p95 0.014553 s, max 0.039338 s. Shared dependencies were reused; these are not fresh-page added times. See the results report for fresh composition timing.

Next: Tile and inspect the rejected large residuals; compare actual support ownership before suppression. Reduce clean-page false alarms without losing whole blocks. Preserve the frozen request corpus for fair fallbacks.

[Output gallery](../../../.astra/fast_lines/out/residual_ledger/index.html) · [All failures and unknowns](../../../.astra/fast_lines/out/residual_ledger/page_failures.json) · [Round-1 report](../../../docs/research/FAST_LINES_ROUND1_RESULTS.md).

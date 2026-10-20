# T6a: frozen vertical tightening on F2

T6a completes steps 0, 1 and 3 only. Step 2 is deferred to T6b; W1 was not accessed. No rows are admitted by this run. Original source trees and crops remain unchanged.

## Development results

The exact 2f34ed52 v2 keys, cards and saved verdict bytes were verified using `git show` before development; the complete features file also matches that revision byte-for-byte ([input identity](INPUTS.json)). The eligible F2 pool uses `fixed_usable` and no `text_exclusions`; it deliberately includes screen-rejected crops to expose merged-line effects. No new Google calls, page segmentation, label changes, horizontal edits or outward expansion occurred.

| Source | v2 n/y | Median crop height xh before → after | Changed | Readable neighbour removed among overrun n | Own component pixels lost on y |
|---|---:|---:|---:|---:|---:|
| gazette_modern | 18/22 | 2.978 → 2.784 | 15/40 (37.5%) | 2/18 | 0/64,198 |
| lekythos_poly1900 | 11/29 | 2.995 → 2.969 | 11/40 (27.5%) | 0/10 | 0/58,067 |
| kosmopolis_poly1900 | 26/14 | 3.595 → 3.595 | 4/40 (10.0%) | 0/26 | 0/35,829 |
| ia_greek_latin | 3/37 | 2.688 → 2.684 | 2/40 (5.0%) | 0/3 | 0/352,464 |

Unblinded inspection covered all 160 pairs in [32 contact sheets](dev/review/) and three native 3× change witnesses. Gazette c015 and c038 lose the readable neighbouring fragments; 55/57 overrun cards retain their original overrun. Lekythos c037 is the remaining crop-ok n: its right-edge clipping after Ἐ persists because X is immutable. No newly cut own body/accent/descender was seen on the 102 original crop-ok y cards, including the 29 changed y cards. These observations do not replace a fresh blind check.

The separate detector-defined body-band metric finds neighbour body pixels in 52/58 n crops and complete body removal in **0/52**; body pixels remain 36,080 → 36,080. Readable partial glyphs outside the body band explain why the two visual improvements are not counted by that narrower measure. Visual readable-neighbour removal is 2/57 overrun cards (3.51%), or 2/58 all n cards (3.45%). Assigned foreign-component pixels on n cards fall 52,515 → 52,084. The cached component assignment is a measurement witness, not independent glyph truth.

The own-component guard refuses 69/160 proposals; the raw proposals would lose 5,190 assigned own pixels. Accepted loss is 0/510,558 pixels on y cards and zero on all 5,770 F2 lines, by construction. This is why zero accepted loss is not claimed as proof of guide correctness. [Full grid](dev/grid.json), [dev row records](dev/records.jsonl), [unblinded observations](dev/visual_review.jsonl).

The result is a conservative negative efficacy finding under the requested token-edge constraint. Within the tested margin grid, many token boundaries conflict with the own-line band or would discard owned pixels. The cutter abstains in those cases.

## Frozen parameters

All nine top/bottom combinations from {0.1, 0.2, 0.3} xh were evaluated on the 160 v2 development cards only. Selection maximises n-card complete neighbour body removal, then minimises residual neighbour body pixels, then prefers the larger total/top margin. All combinations tie on neighbour body removal; the conservative 0.3/0.3 tie-break wins. No harm-test predictions were used to choose or revise parameters.

```json
{
  "top_margin_xh": 0.3,
  "bottom_margin_xh": 0.3,
  "neighbour_center_clearance_xh": 0.5,
  "max_own_pixels_lost": 0,
  "version": "vertical-tighten-1"
}
```

Parameter SHA256: `09c79d81da1777dae34a55d903b885812f948124f35fb7c34cbd407cf5ddf0c1`. Frozen at `2026-10-16T22:28:25.135939+00:00`, before inference began at `2026-10-16T22:29:53.505347+00:00`. [Freeze receipt](params.json).

For each uniquely owned F2 row, use the receipt-verified saved six-guide font band: top=min(font_top, accent_top), bottom=font_bottom, evaluated on the crop X overlap, with 0.3 xh margins. Clip against the closest overlapping-X foreign Google token edges above/below the own body centre; same-row centres within 0.5 xh do not clip. Font guides round outward, token edges inward. Intersect with the original rectangle. Conflicting geometry or any lost supplied own-component pixel returns the original. Horizontal bounds and native sampling remain literal.

The general `tighten_page` callable accepts arbitrary native Google line/token geometry, plus optional existing bands/ownership. Without supplied bands it calls existing `fit_box(splits=False)` on a stable `guide_box`. Source IDs and F2 paths are unnecessary. Supply immutable guides/guide boxes on repeated calls for idempotence. Without supplied component coordinates, the pixel guard is unavailable: generic output still requires the same owner qualification gate. F2 always supplies its cached assigned-component evidence.

The old four-guide fit and the current six-guide page font runtime were inspected; F2 uses its saved detector identity, recorded per page in [provenance](f2/provenance.jsonl), not a claim to have rerun 046bd52. `fix_page`, `separate_lines`, and the expansion path are not invoked. `_voronoi_keep` was considered, but final loss measurement uses the stronger pre-existing assigned-component cache instead.

## Qualification card sets — T6b only

Not generated or qualified here. W1 status, `collector.exit`, locks and PID files were not accessed. Each source receipt records null card/key paths and the unchanged original `LABEL_CHECK_v2.md` hash for the later run. No 100-card sets are represented as ready. IA remains included in the T6b handoff; the saved 2f34ed52 IA verdict is 37/40 crop-ok y, whereas the brief separately cites 35/40. T6a does not resolve that discrepancy by editing verdicts.

## Paired CPU harm test

E4 wave1a `ctrl_s0`: full checkpoint SHA256 `e20cd6cdfc908339b3c7c8f83e88888120240aabc01370a86b7b48606fa81c30`; safetensors SHA256 `29228867db27792f94f6040fed1c828da4335405ab9993e16fc02fbac098ef49`. The full-checkpoint hash matches the existing local Clariden comparison receipt; safe CPU loading verified every safetensors model tensor equal to that checkpoint. Clariden was not contacted. Codec SHA256 `d1b7e2d40565e89e699f748692265e06e2d7028409b78d02d6df6f89b2e82a86`.

All 5,770 distinct eligible F2 crops on 87 pages were included: Gazette 525, Lekythos 4,023, Kosmopolis 562, IA 660. This is below the 10k input-crop cap; evaluating both versions gives 11,540 paired-arm observations. The raw Google labels are the post-fix `label_after_conventions`, encoded to the model codec in NFD once. CER is strict NFD codepoint edit distance, weighted by reference character count. These are silver-reference harm results, not human transcription accuracy.

The unchanged `train/eval_cer.py:evaluate` core is used with `load_checkpoint`, the existing `bench/o4b_models.py:strip` 48-pixel crop adapter, and `data.collate_strips` own-background halo; CPU float32, four threads, batch size 16, sorted by width. The factory `evaluate_run` custody wrapper itself requires the CUDA training runtime and cannot certify this CPU readout. The explicit adapter boundary and hashes are recorded in [harm binding](harm/binding.json). Both arms use the same preprocessing and scorer. No unchanged prediction may differ: this is checked exactly.

Difference is recut − original CER, in percentage points below. CIs use 5,000 paired line resamples per cell; [machine-readable results](harm/summary.json) also contain 5,000 whole-page cluster bootstrap intervals, preserving within-page dependence. A zero point difference is allowed by the stated non-worsening rule; an interval crossing zero does not prove non-inferiority.

| Source | Subset | N | Orig CER % | Recut CER % | Δ pp [paired 95% CI] |
|---|---|---:|---:|---:|---:|
| gazette_modern | all | 525 | 3.9642 | 3.9028 | -0.0615 [-0.1555, +0.0139] |
| gazette_modern | changed | 136 | 2.2431 | 1.9567 | -0.2864 [-0.7025, +0.0670] |
| gazette_modern | unchanged | 389 | 4.4346 | 4.4346 | +0.0000 [+0.0000, +0.0000] |
| gazette_modern | dev_crop_n | 18 | 2.5328 | 2.2707 | -0.2620 [-0.6752, +0.0000] |
| gazette_modern | dev_crop_y | 22 | 2.1845 | 2.0227 | -0.1618 [-0.5668, +0.1770] |
| gazette_modern | geometry_clean | 470 | 2.3113 | 2.2409 | -0.0704 [-0.1723, +0.0194] |
| gazette_modern | screen_merged_flag | 55 | 15.3349 | 15.3349 | +0.0000 [+0.0000, +0.0000] |
| lekythos_poly1900 | all | 4,023 | 1.1629 | 1.1618 | -0.0012 [-0.0231, +0.0167] |
| lekythos_poly1900 | changed | 913 | 0.7809 | 0.7754 | -0.0054 [-0.1027, +0.0788] |
| lekythos_poly1900 | unchanged | 3,110 | 1.2659 | 1.2659 | +0.0000 [+0.0000, +0.0000] |
| lekythos_poly1900 | dev_crop_n | 11 | 5.9448 | 5.9448 | +0.0000 [+0.0000, +0.0000] |
| lekythos_poly1900 | dev_crop_y | 29 | 0.7109 | 0.8689 | +0.1580 [+0.0000, +0.4955] |
| lekythos_poly1900 | geometry_clean | 3,762 | 0.9488 | 0.9482 | -0.0006 [-0.0231, +0.0181] |
| lekythos_poly1900 | screen_merged_flag | 261 | 3.9258 | 3.9178 | -0.0080 [-0.0244, +0.0000] |
| kosmopolis_poly1900 | all | 562 | 5.8271 | 5.8366 | +0.0095 [-0.0095, +0.0287] |
| kosmopolis_poly1900 | changed | 65 | 0.3752 | 0.4618 | +0.0866 [-0.0880, +0.2488] |
| kosmopolis_poly1900 | unchanged | 497 | 6.5011 | 6.5011 | +0.0000 [+0.0000, +0.0000] |
| kosmopolis_poly1900 | dev_crop_n | 26 | 8.4701 | 8.4701 | +0.0000 [+0.0000, +0.0000] |
| kosmopolis_poly1900 | dev_crop_y | 14 | 0.9736 | 0.8345 | -0.1391 [-0.4967, +0.0000] |
| kosmopolis_poly1900 | geometry_clean | 396 | 1.4411 | 1.4550 | +0.0139 [-0.0139, +0.0418] |
| kosmopolis_poly1900 | screen_merged_flag | 166 | 15.2821 | 15.2821 | +0.0000 [+0.0000, +0.0000] |
| ia_greek_latin | all | 660 | 3.8777 | 3.8271 | -0.0506 [-0.2112, +0.0435] |
| ia_greek_latin | changed | 43 | 3.2609 | 2.6973 | -0.5636 [-2.3139, +0.4806] |
| ia_greek_latin | unchanged | 617 | 3.9386 | 3.9386 | +0.0000 [+0.0000, +0.0000] |
| ia_greek_latin | dev_crop_n | 3 | 4.6296 | 4.6296 | +0.0000 [+0.0000, +0.0000] |
| ia_greek_latin | dev_crop_y | 37 | 3.4914 | 3.5573 | +0.0659 [+0.0000, +0.2059] |
| ia_greek_latin | geometry_clean | 660 | 3.8777 | 3.8271 | -0.0506 [-0.2118, +0.0430] |
| ia_greek_latin | screen_merged_flag | 0 | — | — | not estimable |
| overall | all | 5,770 | 2.3249 | 2.3130 | -0.0118 [-0.0358, +0.0080] |
| overall | changed | 1,157 | 1.0655 | 1.0023 | -0.0633 [-0.1914, +0.0407] |
| overall | unchanged | 4,613 | 2.6150 | 2.6150 | +0.0000 [+0.0000, +0.0000] |
| overall | dev_crop_n | 58 | 5.8824 | 5.7900 | -0.0924 [-0.2416, +0.0000] |
| overall | dev_crop_y | 102 | 2.0257 | 2.0257 | +0.0000 [-0.1458, +0.1479] |
| overall | geometry_clean | 5,288 | 1.4856 | 1.4729 | -0.0127 [-0.0390, +0.0093] |
| overall | screen_merged_flag | 482 | 9.8807 | 9.8769 | -0.0038 [-0.0116, +0.0000] |

Overall non-worsening point-estimate rule: **PASS**. 77 lines improve, 95 worsen, 5598 have equal edits. The 4,613 unchanged crops have exactly identical predictions. Per-source outcomes remain visible regardless of the overall result. No post-readout parameter changes were made.

The overall paired 95% interval is -0.0358 to +0.0080 pp; the whole-page interval is -0.0372 to +0.0091 pp. Both cross zero. Kosmopolis worsens from 5.8271% to 5.8366%, with changed-line CER 0.3752% to 0.4618%. Its source-specific harm is not hidden by the overall gain. Lekythos and IA development y subsets also worsen despite zero measured component loss: preserving assigned ink does not guarantee identical recognition after height normalisation.

The geometry-clean subset means exactly F2 `geometry_positive is False` (G1b-negative) and no `screen_reject` flag (the v2 key names this `screen_merged`). All eligible lines already have G1b-negative status; the screen flag supplies the additional split. It is an audit-defined subset, not a physical-correctness guarantee. Development-card n/y cells are repeated-development diagnostics, not held-out evidence.

## Artifacts, validation and handoff

The native validation checks 5,770 literal pixel subarrays, source hashes, raw-response/cache hashes, X invariance, no expansion, and unchanged PNG identity. [Validation receipt](validation.json). Cutter tests: 10 passed (26 total including 16 existing structure regressions), covering inclusion, neighbour clipping/rounding, conflicts, idempotence, owned accent/descender refusal, exact native pixels, arbitrary-page use without cache, accent guides, missing/invalid fits and canonical hashes. [Tests log](tests.log).

Recut PNGs remain in `f2/<source>/recut/` beside references to immutable original page/crop geometry; every row records old/new/proposed boxes, parameter hash and PNG hash. They are experimental outputs and not collection admission. Bulk PNGs and review sheets are git-ignored, present locally, and bound by the tracked records. Per-source receipts:

- [gazette_modern](gazette_modern/receipt.json)
- [lekythos_poly1900](lekythos_poly1900/receipt.json)
- [kosmopolis_poly1900](kosmopolis_poly1900/receipt.json)
- [ia_greek_latin](ia_greek_latin/receipt.json)

Reuse count convention: 14 directly called existing repository functions; 47 added named functions/methods in total, of which 8 are in the cutter library; the rest are experimental binding/evaluation/reporting/commit helpers and tests. The last line uses the total addition count. [Inventory](REUSE.md), [counts](function_counts.json), [runtime](runtime.json).

The guarded commit attempt was blocked: Git could not create the worktree `index.lock` under the read-only main checkout (`Operation not permitted`). **No worker commit was created.** No retry or alternate index was used. The source-bound helper remains ready; `--prepare` and `--check-only` validate exact HEAD, branch, file hashes, an empty staging area and exclusion of git-ignored payloads. The local `handoff.patch.gz` packages the reviewed source files and manifest; its application/hash validation is recorded in `HANDOFF.json`. The original failure is recorded in `COMMIT_STATUS.json`.

T6a: done | reused: 14 functions added: 47 | dev neighbour-ink removed: 3.45% own-ink loss: 0.00% | harm CER orig/recut overall: 2.3249%/2.3130% changed-lines: 1.0655%/1.0023% | params: 09c79d81da17 | model: e20cd6cdfc90

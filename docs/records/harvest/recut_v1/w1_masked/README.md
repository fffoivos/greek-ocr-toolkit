# T6b W1 foreign-ink masking qualification

This is qualification evidence only. No rows are admitted. IA Greek+Latin remains hold-tagged with masking off and is not processed.

The coordinator amends the old literal rule, `own-ink loss = 0`, to **own-ink loss stated per source and judged blind**. The reason is the large paired CER gains and improvement on the crop_ok-y subset with no source worse. T6a2 dev damage is stated as Gazette 0 px, Kosmopolis 11 px, and Lekythos 20 px. These historical dev numbers are distinct from the W1 component measurements in each source receipt.

W1 passed its precondition: `collector.exit` exists with value `0`, and `W1/state.json` has status `completed_selected_sources`. The run root is read-only. No collector locks are opened. Python audit hooks reject writes outside this output directory and socket operations; Hugging Face and Transformers are offline.

## Population and outputs

| Source | W1 candidates | Merged removed first | Rotated total | Already merged | Additional rotated removed | Before caps/heading | Caps/heading excluded | Outputs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Gazette modern | 16,691 | 1,392 | 767 | 669 | 98 | 15,201 | 1,829 | 13,372 |
| Kosmopolis | 3,864 | 676 | 0 | 0 | 0 | 3,188 | 70 | 3,118 |
| Lekythos | 9,113 | 1,124 | 0 | 0 | 0 | 7,989 | 226 | 7,763 |

| Source | Rows through masking | Guarded originals (pages) | Unmatched originals | Crops changed | Cards (guarded) |
|---|---:|---:|---:|---:|---:|
| Gazette modern | 12,306 | 658 (86) | 408 | 8,676 / 13,372 (64.88%) | 100 (7) |
| Kosmopolis | 3,040 | 77 (26) | 1 | 2,481 / 3,118 (79.57%) | 100 (1) |
| Lekythos | 7,500 | 233 (34) | 30 | 7,210 / 7,763 (92.88%) | 100 (2) |

Overall, 18,367 / 24,253 output crops changed (75.73%). The 22,846 rows through masking include matched rows whose frozen mask changes no pixels. The other outputs are 968 guarded originals and 439 frozen unmatched identities. The draw population is all 24,253 outputs.

The W1 assigned-own component pixels changed after the guard are 11,933 Gazette, 4,551 Kosmopolis, and 15,503 Lekythos. These ownership diagnostics are recorded for blind clipping judgment; they are distinct from the historical T6a2 dev figures of 0 / 11 / 20 px. Seven Gazette rows have zero detector-assigned own pixels in their crop; this does not disable the original-dark-ink guard. All own-ink audits were run before applying the output decision.

`excluded.jsonl` records the sequential exclusion and overlapping flags for each excluded row. A rotated crop is strictly taller than wide and has at least four Unicode letters in its unchanged post-convention label. No rotation repair, text rewrite, additional merged-line screen, or middle-band matching rule is applied. Source-level `usable_final=false` is preserved.

Per source, `records.jsonl` binds every output to its original and output PNG SHA, original box, label, parameters, fill statistics, would-be mask and actual mask counts, skip decision, and component audit. Native PNGs are under `<source>/crops/`. `component_audit.jsonl` contains both would-be and applied measurements for every output, including unchanged and guarded rows. `provenance.jsonl` binds source rasters, saved Google responses, page metadata, full-precision mask curves, audit component planes, and source code hashes. Per-page working files are ignored in favor of these consolidated records.

Some disposable W1 PNGs were pruned under W1's storage policy. Original PNG bytes are reconstructed from the retained native crop-source raster and original box with W1's PNG compression level 3. The SHA must match the original row's `crop_sha256` exactly before masking. Retained original PNGs, where present, must match byte-for-byte. No original files are modified or recreated in W1.

## Frozen method and skip guard

Parameters: `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`.

Library: `f203504a8703561569486450d7e725fe7b399cd4c8fbf581b79cd249e3c5aeb5` (`greekocr/glyphs/foreign_ink.py`). All nine source hashes from T6a2's parameter freeze are checked. Ownership and ring fill are unchanged. Background fill is the component's local page-ring median; ring spread is p90-p10. An empty ring abstains.

As in T6a2, masking uses the runtime's non-discounted detected line curves, the unchanged nearest-curve matcher from `masking/probe.py`, and the original crop rectangle. The saved Google response is hash-verified and every row's Google line index and box are checked against it. Google-derived curves do not replace the qualified runtime curves.

The own-ink audit reproduces the independent G1b joined detector-component ownership used for W1. Its owner is the saved `measured_row_id` associated with the original Google line box, independently of the mask match. The unchanged shared T6a2/T6d `component_audit` function is copied to `component_audit.py` and its AST is checked against the shared implementation. `OWN.prepare_row` and `box_hits` are executed unchanged. W1's existing handling of invalid detector audit rows is reproduced; every selected row must still have a valid measured owner, or the run fails its prerequisite. Zero assigned own-component pixels are recorded as such, with a null assigned-own fraction and `own_ink_empty=true`; this does not disable the original-pixel guard. Unassigned foreground is not silently counted as foreign ink in the component audit.

For each row:

1. Compute the exact native pixels that the frozen mask would change.
2. Audit these changes against the original crop's detector-assigned own components, separately from the guard.
3. Set `own_ink_masked_fraction = would_be_changed_original_dark_pixels / original_dark_pixels`. Dark pixels are the unchanged frozen `binarise` foreground of the native original page, clipped to the original crop. This original-pixel denominator does not depend on detector component assignment. A genuinely empty dark mask has zero changes and fraction zero, with an explicit flag.
4. If the fraction is **strictly greater than 0.30**, write the byte-exact original PNG and set `wrong_line_risk=true`.
5. Record the actual output audit too. Guarded rows have zero applied loss and remain in the card population. Unmatched curves retain the frozen identity behavior.

The component measurements are ownership-based diagnostics; semantic clipping is judged blind as `crop_clipped`. Guarded contact sheets show up to 20 rows per source, with original pixels above and exact would-be changes in red below. The output of every guarded row remains its original.

## Blind hand-off and gate

Each source has 100 cards under `cards/<source>/cards.jsonl` plus `crops/`. The separate key is `cards/<source>_key.json`. Public cards contain exactly `card_id`, relative `crop`, unchanged post-convention `google_text`, and `word_scripts`.

Draws use Python `random.Random('t6b:<source>').sample(pool, 100)` over all eligible outputs ordered by line ID. There is no length sorting or filtering after the guard. Guarded originals and frozen unmatched identities remain eligible, and their output kind is recorded only in the private key. The instruction file in `cards/LABEL_CHECK_v2.md` is copied unchanged from the specified v2 checker instructions. Checkers must open only their cards file and crop images.

The coordinator applies the gate after blind checking: **crop_ok at least 90/100 and letters at least 90/100 on the same 100 cards**, using point estimates. Own-ink clipping is `crop_clipped`. For Gazette, this also serves as the W2 Gazette probe; C1 original crops had letters 86 and crop_ok 70. A pass admits the resulting rows for the wave-1d arm only. No gate is applied by this task.

C1 Gazette's `screen_merged` caught 4/7 merged crops (57.14%). T6b blind verdicts are pending. Record residual `merged_two_lines` counts as they return. Because every flagged row was excluded before this draw, unconditional screen recall cannot be estimated from these 100 cards alone; it additionally needs labelled excluded rows. No new screen is introduced to conceal residual merges.

## Validation and commit

`verify.py` independently reconstructs and hashes every original crop, checks every output and component audit, enforces byte-exact guarded originals, and reproduces all three seeded draws and unchanged labels. `validation.json` records the result. `artifact_hashes.jsonl` lists all local image and curve hashes; images and bulk curves are git-ignored and are never force-added.

Validation passed for all 24,253 outputs and 300 cards. The 15 focused tests passed. The artifact manifest binds 25,922 local artifacts: 24,253 output crops, 300 card crops, 968 native guarded overlays, 12 contact sheets, and 389 full-precision curve files. The first contact sheet per source was also visually inspected for original/overlay/label layout. This is mechanical qualification evidence; blind letters, crop_ok, and crop_clipped judgments remain pending.

Materialization completed before a reporting-only NumPy quantile serialization error. `report_fix.json` binds the executed materializer source in `attempts/materializer_source.py` and the corrected reporter. Verification checks that their entire ASTs are identical after excluding the reporting `finish` function, and checks that every page has the same original materializer binding. The only source correction is the report's quantile array conversion from `.items()` to `.tolist()`. Six retired preliminary guard overlays were moved to ignored temporary storage; final records and contact sheets use only the settled original-dark-ink guard.

`guarded_commit.py` is adapted from `masking/guarded_commit.py`, with T6b's exact starting HEAD and output-only scope. It requires the completed 24,253-row / 300-card validation, binds all nonignored commit files by SHA, and checks branch, HEAD, an empty index, scope, and ignore rules. An index permission failure is terminal: no retry or alternate index. In that case it leaves a reviewable `source.patch` and `COMMIT_STATUS.json` without claiming a commit.

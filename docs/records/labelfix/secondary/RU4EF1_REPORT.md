# RU4E-F1 phase 1

Status: lead material and replacement packs are ready. Adjudication remains `PENDING_READS`; no new reader runs or version overlay were performed. Network, browser/computer use and `.git` writes were not used.

The original `ru4e2_finalize.sh` was started, then superseded by the phase-1 extension using the same canonical collection and combine functions in four offline workers. Original hash-bound protocol files and build bindings remain intact.

## Results

- 32 original reader contexts: 23 VALID, 5 VOID, 4 FAILED canonical scans.
- Decisions over 1,753 candidate positions: 274 edit_hard, 698 keep_soft, 781 held for lead review.
- Hold reasons: missing_independent_reads 761; reader_disagreement 19; uncertain_read 1.
- For 28 scan-clean contexts, derived-view coverage totals: direct 504, derived 2,038, unviewed 88, assigned 2,630. Unviewed items are dropped before gating; ctx07/r1 has no usable correct controls. The four scan-invalid contexts have no admitted coverage or votes.

## Original contexts needing replacement

| Original | Status | Cause |
|---|---|---|
| ctx01/r2 | VOID | wrong signs 2; abstentions 1; correct 19 |
| ctx04/r2 | FAILED | unresolvable load expression (12) |
| ctx07/r1 | VOID | no_usable_correct_controls |
| ctx08/r1 | VOID | wrong signs 2; abstentions 0; correct 18 |
| ctx08/r2 | FAILED | image provenance: unmatched image provenance (2) |
| ctx11/r1 | FAILED | image provenance: unmatched image provenance (19) |
| ctx11/r2 | VOID | wrong signs 2; abstentions 0; correct 17 |
| ctx12/r1 | VOID | wrong signs 2; abstentions 0; correct 17 |
| ctx14/r2 | FAILED | unresolvable load expression (36) |

## Replacement packs

Nine independent replacement contexts (seven r3 and two r4): 845 item reads, estimated 1.690 points at 0.2 points per 100 reads. These are prepared, not run. Both readers failed in ctx08 and ctx11; their two logical reader roles route independently to r3 and r4.

| Replaces | Reader | Items | Pack |
|---|---|---:|---|
| ctx01/r2 | r3 | 93 | `/private/tmp/ru4e2/sol_packs/ru4e_r3/ctx01-r2` |
| ctx04/r2 | r3 | 94 | `/private/tmp/ru4e2/sol_packs/ru4e_r3/ctx04-r2` |
| ctx07/r1 | r3 | 94 | `/private/tmp/ru4e2/sol_packs/ru4e_r3/ctx07-r1` |
| ctx08/r1 | r3 | 94 | `/private/tmp/ru4e2/sol_packs/ru4e_r3/ctx08-r1` |
| ctx08/r2 | r4 | 94 | `/private/tmp/ru4e2/sol_packs/ru4e_r4/ctx08-r2` |
| ctx11/r1 | r3 | 94 | `/private/tmp/ru4e2/sol_packs/ru4e_r3/ctx11-r1` |
| ctx11/r2 | r4 | 94 | `/private/tmp/ru4e2/sol_packs/ru4e_r4/ctx11-r2` |
| ctx12/r1 | r3 | 94 | `/private/tmp/ru4e2/sol_packs/ru4e_r3/ctx12-r1` |
| ctx14/r2 | r3 | 94 | `/private/tmp/ru4e2/sol_packs/ru4e_r3/ctx14-r2` |

Driver: `scripts/secondary/run_ru4e2_r3_all.sh` (includes r4). `--dry-run` reports 9 pending, model gpt-6.1-sol, medium, network false, zero probes and reads. Actual later invocation uses the canonical weekly limit probes, stops at 70%, and refuses repeat attempts. No live probe was made in this phase.

Finaliser for later replacement routing: `scripts/secondary/ru4e2_finalize_f1.sh`. It handles VOID and scan-invalid originals, validates new evidence, and recombines logical roles. No `--apply-lead` option is exposed by the phase-1 extension.

## Lead material

Path: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/ru1_review/ru4e2`

- `index.html`, `audit_001.html` through `audit_003.html`: seeded audit of 20 edit_hard and 10 keep_soft.
- `review_001.html` through `review_079.html`: 781 held positions.
- `template.jsonl`: 811 unanswered cells; all pixel_checked false.
- Seed: `RU4EF1:20261018:audit:20+10`; deterministic sampling from sorted candidate positions.
- Same-book references in 12 books: 23 reference signs from two VALID reader agreements, and one explicitly marked RAW-Google-labelled internal hard sign in book 5a6a4fec. References are unadjudicated. No target is used as a reference.
- Native full-line PNGs and 4x nearest-neighbour views; RAW Google code-point offsets are marked without guessed glyph boxes.
- The original finaliser also retains its all-proposed-edit check material in `artifacts/ru1/ru4e2/lead/` (274 edit checks, 19 disagreements, and its own 30-cell audit). These proposed edits still require lead pixel checks before any later overlay.

## Validation

- Five phase-1 tests passed, including later admission of r3/r4, cache invalidation, pack isolation and a no-read driver dry run.
- Existing RU4E/RU4E-2 tests: 29 passed.
- Checked every sheet image/link, all source and output bindings, all 811 HTML/template cells, exact audit balance, independent references, replacement pack bindings and pairwise fresh IDs.
- No visual reading was performed and no glyph judgement is claimed.
- `ru1_v3_test_edits` was not written.

Receipts: `artifacts/ru1/ru4e2/RU4EF1_RECEIPT.json`, `RU4EF1_VALIDATION.json`, `r3_driver_dry_run.json`, `r3_to_run.jsonl`.

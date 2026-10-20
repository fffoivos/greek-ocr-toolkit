# W1c: three fixes from the CP-5r re-review, plus a storage diet (gpt-6.1-sol, xhigh, network OFF, no spend, ≤ 60 min)

Work in this worktree, branch `sol/collect-v3`, base 9f286b30 (your W1b).
- The plan is rev 2.1: `~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/SOURCING_T5_COLLECTION_PLAN_20261016.md`. It is read-only.
- The second review is `.../reviews/ASTRA-CP5src_review_1.md`, findings 5 and 6.
- Nothing is collected.

## Fixes

### 1. Look-alike rule, Unicode equivalence
Bug: `core()` strips combining marks before `is_lookalike()` checks for diacritics, so a decomposed `ό` next to Latin words gets mapped.

Fix:
- NFC-normalise the label first;
- check every token for combining marks or precomposed diacritics before any punctuation stripping;
- map only tokens that are diacritic-free.

Update the hash binding. Tests:
- the three mapping witnesses (V. Η.→V. H.; N. Τ.→N. T.; Iph. Τ.→Iph. T.) still map;
- `Latin ό Latin`, in both NFC and NFD, is left unchanged (and so excluded or kept exactly as the rule defines);
- υ-containing tokens exclude the line;
- the 660-line IA Greek+Latin recount still gives 618 / 3 / 39.

### 2. Gazette modern: physical condition and probe strata
- A Gazette row counts toward **modern** only if the pipeline's primary class for that row is `modern_scanned`. The year alone does not decide it.
- Rows from Gazette pages whose lines classify as polytonic are kept as Gazette-polytonic and are **not admitted**, because that stratum failed its v2 check.
- 1986–1990 are the measured strata.
- 1982–1985 become a **W1 probe stratum**: 40 pages, inside the W1 Gazette tranche. They enter W2 only if C1 qualifies them (letters ≥90%, a monotonic share reported) — otherwise W2 draws 1986–1990 only.
- Use same-period denominators in all Gazette projections. Measured on the 1986–1990 pages: modern 525/12, numerics 67/12, headings 57/12, dialogue 36/12.
- The frame for 1982–1990 is 37,764 issues.

### 3. Small-number corrections

| Item | Correction |
|---|---|
| NLG remaining inventory | 23 items, ≤920 capped pages |
| Lekythos | ≥13 issues at ≤24 pages each |
| Serbia yield | 614 eligible rows / 30 pages |
| Row-share caps | Applied **after dedupe**; reported per class |

### 4. Storage diet
Keep exactly one copy of each crop-source raster plus the raw Google response, with per-page hash binding, and nothing that can be regenerated:
- **regenerable from the retained raster and the response:** crops, detector caches, separated exports, review copies;
- **downloaded source PDFs:** delete once the render is hash-recorded, unless the source has no stable re-download URL.

Re-project disk use for 6,850 pages, split into retained and regenerable, and give the peak working-set size. The target is ≤20 GB retained.

## Tests and hand-off
- Re-run the full test suite and the dry-run parity.
- Commit if git allows. Otherwise write a guarded helper that **excludes git-ignored paths**: last time the helper failed on ignored replay files.

The last line must be exactly:
`W1c: done | lookalike NFC fix: <ok> | gazette physical condition + 1982-85 probe: <ok> | retained GB: <x> peak GB: <y> | tests: <n> passed`

# ASTRA-CLEANUP cycle 2 — certification report

Scope: base `ac1c38cf6` → HEAD `3b4090bf9`, assessed against the owner’s brief. Evidence includes Git objects, source inspection, exhaustive file accounting, all external receipt hashes, independent score recounts, and a fresh full pytest run. **All 45,412 tracked files remained unchanged.**

[Full report and evidence index](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CLEANUP2/ASTRA_CLEANUP2_REVIEW.md)

**Not certified for merge: the required test gate has 11 failures and 40 errors; one HIGH remains.**

## Findings

### [HIGH] H1 — Fresh-checkout tests require an unavailable, hard-coded predictor binary

Locations: `tests/test_seg_curve.py:84`, `tests/test_seg_small.py:26,41`, `tests/test_seg_gate.py:25`, `tests/test_seg_deskew.py:20`; setup instructions `README.md:53–58`.

The full suite ran from the repository root with `PYTHONDONTWRITECODE` avoided in favor of the required `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`, and the external data root configured. Raw result:

```text
11 failed, 7255 passed, 101 skipped, 9 warnings, 40 errors,
63 subtests passed in 336.54s (0:05:36)
```

Exit **1**. All **51** failing/error cases encounter the same missing executable:

```text
scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict
```

The Rust source and lockfile exist. The ignored build product does not, and the documented install→pytest sequence supplies no build step. The cycle-1 green receipt therefore does not establish reproducibility in this fresh checkout.

**Failure scenario:** a clean checkout cannot run the documented suite, and a read-only certifier cannot build at the hard-coded destination. These failures demonstrate a prerequisite/path defect; they do not establish a segmentation-policy regression.

**Fix:** supply a reproducible locked build into scratch and a shared configurable predictor path, including historical replay adapters. Then rerun the complete data-enabled suite without converting these cases into skips.

[Raw log](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CLEANUP2/pytest_head.log) · [JUnit](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CLEANUP2/pytest_head.xml)

### [MEDIUM] M1 — “SEG10 only” remains an inaccurate description of behavioral changes

Locations: review brief `:16`; `greekocr/harvest/line_pipeline.py:447–466`; `docs/records/harvest/collect_v3_admission/stage_crops.py:122–125,238`.

`CHANGES_BEYOND_RELOCATION.md` now accurately discloses the expanded scope. Independent witnesses confirm:

- With identical synthetic KEEP measurements and missing polytonic evidence, empty scope produces **HOLD**; `routes_out_of_scope=['polytonic']` produces **ADMIT**, retaining raw text.
- CROPS3’s exact selection code changes mixed legacy **[W1,W2] → [W2]**; its default disk floor changes **0 → 10 GB**.

All **12 PIPE032 scope tests pass**. These are disclosed intentional features, so the former hidden-scope problem is reduced to a review-description discrepancy.

**Failure scenario:** merging under “relocation plus SEG10” implies unchanged correction obligations and staging selection.

**Fix:** reconcile the review/merge scope with these changes, or split them into separately reviewed work. Do not claim unconditional behavioral parity.

### [LOW] L1 — Remaining documentation drift and broken links

- `docs/A_ocr_development/segmenters/NEXT_GEN_R8.md:7` claims an empty prototype diff against `046bd52`. The diff contains **three paths**: an externalized NPZ fixture and two resolver adaptations. Stack/detector algorithms remain unchanged; whole-tree byte equality is false.
- `docs/B_training_data/d_review/README.md:47` labels S4 the current replay; the current adoption replay is `seg_steps/s5_adopt/`.
- `README.md:48` retains an obsolete warning about current version drift. `TEST_RECORDS.md:7` says 41 preserved historical function bodies; the ruling contains **42**, all unchanged when skipped.
- Two of **355** checked local link targets are missing: `READERS_TRANSKRIBUS.md:128` and `READERS_VISION.md:38` reference old review-HTML locations.

**Failure scenario:** readers follow obsolete evidence, infer unsupported byte continuity, or reach dead links.

**Fix:** correct the current labels, comparison scope and count; provide valid retained locations or receipt-backed retrieval instructions.

## Cleared and verified-good

**Taxonomy and process:** the A/B mapping is substantive. A.i identifies the pixel-first implementation; A.iii/R7 and A.ii/R8 are defensible generations of the same small-detector Stack. The relevant ancestry checks pass. B.a–d have real implementations and substantial documentation. AGENTS covers all requested process areas, and the owner-sheet code implements the last-two-version display and guards writes behind user edits.

**Exhaustive base-file accounting:**

| Disposition | Files |
|---|---:|
| Original path, identical | 8,889 |
| Original path, modified | 411 |
| Mapped path, identical | 34,696 |
| Mapped path, modified | 649 |
| Externally receipted, matching original Git blob | 16,888 |
| **Unaccounted** | **0** |
| **Total** | **61,533** |

All cycle-1 **3,409** omissions are now tracked: **3,407 exact base bytes**, two changed HTML files. All final **36** restored fixtures match base exactly. The Git-only alias check passes **170/170**.

[Complete accounting](/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CLEANUP2/base_file_accounting.tsv)

**Data and history:**

- Hashed **all 16,898 receipt entries / 10,537,020,663 bytes**: **zero missing entries, hash/size mismatches, duplicate paths, or manifest mismatches**.
- All **199 distinct producing commit identities** resolve. The CP5 gzip independently reproduces the receipted **119,720,892-byte** payload.
- `SEGEVAL1.bundle`: **147,025,055 bytes**, SHA256 `25c38794aacb89d083b461175471735575551f0acc4d1f612214b3e43fee1e1a`.
- Size guard passes: **zero tracked blobs over 5,000,000 bytes**; maximum **4,992,029**.
- All **56 inventoried branch tips remain preserved**: 47 refs unchanged, nine advanced without losing their original tip. Seven `records/*` tags remain.

**Cycle-1 reader/isolation fixes:** real probes return round1 **61,882** and round2 **24,430** admitted rows; SF7 loads **100 rows / three hash bindings**; the R2 sibling witness returns **1 admission / 1 record**. Reader regressions **9 passed**, R2 cards **47 passed**, OS5 **3 passed**, capture **3 passed**. The prior repository-write/socket failures did not recur.

**Historical tests and collection counts:** the skip ruling preserved **42 function bodies**; subsequent differences inspected only adapt paths/readers. Historical JUnit independently confirms **7,329 → 6,823**: 521 evidence parameters disappeared, offset by 15 added tests. Current collection is **6,886 without data → 7,407 with data**, restoring exactly those **521 parameters**. The explanation in `TEST_PATHS_AFTER_LAYOUT.md` is true.

**Specific factual checks:**

| Claim | Firsthand result |
|---|---|
| Pipeline | **0.3.2** |
| Segmentation | **0.13**, label **0.9-s5**, inclusive **0.30–2.00** |
| Gate / final eligibility | **0.3 / 0.3** |
| Polytonic / Cyrillic / numerics / dashes | **0.7 / 0.3 / 0.3 / 0.1** |
| Inventory / repair / composer / census | **0.1 / 0.2 / 0.3 / 0.7** |
| Manifest verification | **11 tools**, 35 component occurrences / 23 unique paths pass |
| Q4 page modules | `lines.py`, `pixels.py`, `font.py` byte-identical |
| Prototype test files | **41**, outside default test discovery |
| LQB truth | **61,463 rows** |
| SF7 audit | **70 CORRECT / 30 PENDING** |
| SPLIT2 | **320,479** rows: **253,402 / 7,007 / 60,070** train/dev/test |
| SEG10 replay | **1,705 records**, 111 verdict flips, three reason-only changes |
| SEG10 150-panel FP/FN | **16/15 → 4/19**; after gate **11/15 → 2/18** |
| SEG10 agreement | **109→117/135**, **189→209/235**, **160→173/185** |
| Changed owner-judged IDs | **59**, or **38** after gate; exact proposed-set match |

The false-negative increases remain explicit. These are saved-row recounts on reused review populations, not fresh native replay or independent generalization. Band adoption remains a coordinator decision.

## Ordered asks

1. Fix H1 and obtain **0 failed / 0 errors** in a fresh read-only, data-enabled checkout; re-review before merging.
2. Reconcile the merge/review scope with PIPE032 and CROPS3.
3. Correct or log the documentation issues, preserving all restored fixtures and custody records.

VERDICT: NOT CERTIFIED FOR MERGE — fix the fresh-checkout test gate and re-review | BLOCKERS: 0 | HIGH: 1
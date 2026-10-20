# Collection plan v1 — execution state (autonomous run started 15 Oct 2026; owner: "complete the page scans, filter bad ones after the fact")

Owner constraints: no owner look during the run (post-hoc filtering instead); owner can judge Greek and English only, so Cyrillic quality rests on
automatic checks + Wikisource human transcriptions; spend per the plan (Google ≈ USD 10); one Codex job on this tree at a time.

| Wave | Brief | Status | Started | Finished | Pages | Lines admitted | USD |
|---|---|---|---|---|---|---|---|
| 0 admission + crops | T20 | complete | 2026-10-15 | 2026-10-15 | 0 new (1,532 reused) | 61,882 | 0 |
| 1 Vouli | T21 | complete | 2026-10-15 00:53 | 2026-10-15 01:58 | 1126 / 779 / 779 | 37367 | 1.1580 |
| 2 polytonic round 2 | T22 | complete | 2026-10-15 02:01 | 2026-10-15 03:10 | 781 / 613 / 613 | 24430 | 0.9195 |
| 3 parliament 1975–2000 | T23 | complete (72/104; source shortfall) | 2026-10-15 03:12 | 2026-10-15 06:12 | 1153 / 705 / 690 | 85042 | 1.0575 |
| 4 Open Archives | T24 | blocked (all scanned mojibake scores null) | 2026-10-15 06:23 | | 0 / 0 / 0 | 0 | 0 |
| 5 mixed + Latin | T25 | complete (bounded page shortfall) | 2026-10-15 06:28 | 2026-10-15 07:24 | 1396 / 782 / 782 | 33114 | 1.1730 |
| 6 Cyrillic | T26 | complete | 2026-10-15 07:26 | 2026-10-15 07:48 | 663 / 566 / 566 | 13683 | 0.8490 |
| 7 Wikisource test labels | T27 → T27e | done (T27–T27d blocked by sandbox 429 / robots / widths; coordinator fetched the 400 thumbnails from the Mac) | 2026-10-15 07:49 | 10:21 | 400 read | 12,356 test/dev crops; 2,030 aligned to human lines; Google CER vs human el 4.93 % / ru 1.98 % | 0.60 |
| close-out | T28 (run 1 09:32; final 10:30) | done — final: train 228,445 / dev 15,646 / test 49,348 (poly 178,109 / mono 75,853 / cs 8,050 / latin 15,201 / cyr 16,226); USD 9.95 total; 66 tests | 2026-10-15 09:16 | 09:32 | 5,879 read pages | 281,102 admitted: train 228,464 / dev 14,528 / test 38,110 (poly 169,323 / mono 75,629 / cs 7,938 / latin 15,104 / cyr 13,108) | 9.35 total |
| scaling arm (GPU) | — | deferred to the end | | | | | |

Decisions log:
- 15 Oct: owner look replaced by (a) the page gate, (b) post-read page quality flags (bad_page), (c) contact sheets per class for an after-the-fact look.

## Wave 0

T20 completed locally on 15 October 2026: 75,061 DocAI lines from 1,532 existing pages / 130 books; 61,882 admitted and 13,179 rejected; 61,882 native grey PNG crops, 28,960 trimmed. No network, new Google calls, or `.git` writes.

| Class | Train | Dev | Test | Total |
|---|---:|---:|---:|---:|
| greek_poly | 46,596 | 3,205 | 8,172 | 57,973 |
| greek_mono | 1,374 | 124 | 223 | 1,721 |
| greek_latin_cs | 903 | 22 | 101 | 1,026 |
| latin | 1,078 | 14 | 70 | 1,162 |
| cyrillic | 0 | 0 | 0 | 0 |
| **Total** | **49,951** | **3,365** | **8,566** | **61,882** |

20 seeded held-out books: 15 test / 5 dev. All seven nonsingleton decades contribute at least two books; the 1930s has only one round-1 book, which is held out in test (917 admitted lines). This is the documented capacity exception. O5 dropped 221 train lines whose normalized labels equal dev/test labels; zero equal labels remain across train and hold-out.

| Rejection reason | Lines (overlapping counts) |
|---|---:|
| short_line | 8,632 |
| low_confidence | 4,786 |
| tall_box | 1,112 |
| symbol_heavy | 5,560 |
| foreign_script | 93 |
| mixed_word | 117 |
| bad_page | 152 |
| label_in_holdout | 221 |

Four bad pages exclude 152 lines. Six admitted labels retain standalone spacing marks for a later label decision. Crop width min/median/max: 52 / 738 / 1,706 px; height: 11 / 40 / 261 px.

**353 offline tests passed**; every crop hash, dimension, geometry and source pixel was checked. Four populated-class sheets have 60 unique examples each; Cyrillic has an explicit empty-class sheet. Sheet layout checks passed; observed source-box/label alignment issues are recorded for the owner’s after-the-fact review.

Artifacts: [report](../round1/ADMISSION.md), [admitted](../round1/admitted.jsonl), [rejected](../round1/rejected.jsonl), [held-out books](../round1/holdout_books.json), [summary](../round1/admission_summary.json), [full validation](../round1/admission_validation.json), [visual QA](../round1/admission_visual_qa.json), [tests](../round1/admission_tests.xml), [inventory](../round1/admission_inventory.json).

## Wave 1

T21 completed 2026-10-15 01:58 Athens: 107 books; 1126 pages rendered at 200 dpi grey; 779 gate accepted / 779 read once with Document AI; 48169 lines, 37367 admitted, 10802 rejected and 37367 native crops. USD 1.1580 reserved (cap 2.50); zero Vision calls. 230 offline tests passed.

Recorded book years span 1824–1916 plus 11 undated, despite the brief's 1850s description; all 107 inputs retain supplied metadata. Seed 20261015: 16 held-out books, 12 test / 4 dev. O5 checks both waves' hold-out labels. Split line totals: train 32535, dev 2212, test 2620; polytonic 34545.

Polytonic source share: admitted 39.24%; effective combined train pool 39.24% (30094 Vouli / 76688 total), cap ≤40%. Use [train_pool.jsonl](../vouli/train_pool.jsonl): it applies 2 reverse O5 round-1 exclusions and 0 Vouli source-cap exclusions while retaining all admitted crops.

779 compiled read pages and five class sheets; all crop pixels and compiled rasters validated. Failures: 0 lost / 0 empty / 0 no-line reads; 1 bad pages excluded at admission; 2 uncuttable crop geometries rejected. [Report](../vouli/READS.md), [summary](../vouli/admission_summary.json), [validation](../vouli/validation.json), [inventory](../vouli/inventory.json).

T21: done | pages: 1126/779/779 | lines: 48169 | admitted: 37367 | poly: 34545 | train: 32535 | dev: 2212 | test: 2620 | usd: 1.16 | tests: 230 passed

## Wave 2

T22 completed 2026-10-15 03:10 Athens: 50 new Anemi books, 781 fetched / 613 accepted / 613 read pages. 49 books yielded accepted/read pages. 29943 DocAI lines, 24430 admitted native crops, 22311 polytonic. Train 19693 / dev 703 / test 4034; 8 held-out books (6 test / 2 dev). USD 0.9195, cap 1.50; zero Vision calls. 214 offline tests passed.

Target 650 accepted pages; shortfall 37, after the bounded original/+1/+2 neighbour rule. 3 bad pages rejected after reading and marked in compiled images. O5 checks all three waves and the combined training overlay; the T20 admission module is unchanged. Vouli polytonic train share 31.83% (≤40%).

Sample [visual QA](../round2/visual_qa.json) retains two concrete crop/row counterexamples under unchanged T20 rules. All three bad-page headings were visibly checked; automatic parity is not a transcription or glyph-ownership guarantee.

[Selection](../round2/SELECTION.md), [report](../round2/READS.md), [summary](../round2/admission_summary.json), [validation](../round2/validation.json), [training pool](../round2/train_pool.jsonl), [inventory](../round2/inventory.json).

T22: done | books: 50 | pages: 781/613/613 | lines: 29943 | admitted: 24430 | poly: 22311 | train: 19693 | dev: 703 | test: 4034 | usd: 0.92 | tests: 214 passed

## Wave 3

T23 completed available-source scope 2026-10-15 06:12 Athens: 72 volumes (four/year in 18 available years), 1153 rendered / 705 accepted / 690 DocAI-read pages; 95438 lines; 85042 admitted native crops. USD 1.0575; 270 offline tests passed.

The 104-volume target remains short by 32: no eligible catalogue rows for 1990, 1991, 1992, 1993, 1997, 1998, 1999, 2000. Complete live dated-title searches also returned zero eligible records. No replacement across years or licence relaxation.

Monotonic class 46089 / polytonic class 37988; train 67527, dev 4856, test 12659. Sixteen year-stratified held-out volumes (12 test / 4 dev), frozen before reads. O5 checks all four waves. Era and script class stay separate. T20 admission unchanged; zero Vision calls.

254 public API/download requests; minimum gap 2.010081 s. PDFs deleted after sampled render/gate; hashes, sizes and page counts retained. All crop pixels and compiled rasters validated. [Selection](../parliament/SELECTION.md), [report](../parliament/READS.md), [summary](../parliament/admission_summary.json), [validation](../parliament/validation.json), [inventory](../parliament/inventory.json).

T23: done | volumes: 72 | pages: 1153/705/690 | lines: 95438 | admitted: 85042 | mono: 46089 | poly: 37988 | train: 67527 | dev: 4856 | test: 12659 | usd: 1.06 | tests: 270 passed

## Wave 4

T24 preflight 2026-10-15 06:23 Athens: **blocked, not complete**. All 41,675 scanned metadata records have null mojibake_badness_score; none meets the required == 0 filter. No criteria were relaxed. No downloads, page renders, Google reads, admissions or hold-out assignments; USD 0.00 of the USD 3.00 cap.

Full metadata join: 64,340/175,973 (36.56%); scanned join: 10,658/41,675 (25.57%). 7,341 scanned mixed-script candidates retained for T25. 139 offline tests passed. T20 admission unchanged; no Git writes.

[Report](../openarchives/READS.md), [selection](../openarchives/SELECTION.md), [pool audit](../openarchives/pool_summary.json), [Wave 5 candidates](../openarchives/wave5_candidates.json), [validation](../openarchives/validation.json), [inventory](../openarchives/inventory.json).

- 15 Oct 06:30: disk fell to 1.2 GB free. Deleted: scratch copies of the HF tables, the duplicate Vouli PDFs, pip/uv/npm/VS Code caches; stripped the embedded
  page image (5 MB base64) from 2,619 raw Document AI responses (−6.4 GB). Free now ≈ 23 GB. T24b adds disk discipline (render cap 3,500 px, strip images, one PDF at a time).
- T24's mojibake==0 filter was my error: scanned docs have null scores. T24b treats null as pass.

## Wave 5

T25 completed 2026-10-15 07:24 Athens: 40 Anemi / 40 repository / 1 Internet Archive sources; 1396 rendered / 782 accepted / 782 read pages. 46515 DocAI lines, 33114 admitted native crops; 3979 Greek-with-Latin and 10326 Latin lines. USD 1.1730, cap 2.00; 248 offline tests passed. Zero Vision calls; T20 unchanged; no Git writes by T25 (external T24/T24b commits recorded in Git audit).

A/B hold-outs: six sources each; A 4 test / 2 dev, B 5 test / 1 dev; the single IA source is test-only. Total 10 test / 3 dev after integer rounding. O5 includes all prior hold-outs; 11 earlier train lines excluded in the combined overlay. Target shortfall 198 pages after bounded replacements. All native crops and compiled rasters replay-validated; physical/transcription limitations remain in visual QA.

[Selection](../mixed/SELECTION.md), [report](../mixed/READS.md), [validation](../mixed/validation.json), [combined training pool](../mixed/train_pool.jsonl), [inventory](../mixed/inventory.json).

T25: done | sources: 40/40/1 | pages: 1396/782/782 | lines: 46515 | admitted: 33114 | cs: 3979 | latin: 10326 | poly: 16276 | mono: 2533 | usd: 1.17 | tests: 248 passed

## Wave 6

T26 completed 2026-10-15 07:48 Athens: 13 IA items; 663 rendered / 566 accepted / 566 read pages; 37398 DocAI lines, 13683 native crops; 13108 Cyrillic and 575 Latin. Train 12786 / dev 232 / test 665; two test items and one dev, seed 20261015. USD 0.8490 (cap 1.20); 192 offline tests. 177 read pages dropped by <70% Cyrillic; language detection has no hints. T20 unchanged; automatic checks only, no owner Cyrillic transcription validation; zero Vision calls and Git writes. Approximately 550 accepted pages requested; bounded shortfall 0.

[Report](../cyrillic/READS.md), [validation](../cyrillic/validation.json), [inventory](../cyrillic/inventory.json).

T26: done | items: 13 | pages: 663/566/566 | lines: 37398 | admitted: 13683 | cyr: 13108 | latin: 575 | train: 12786 | dev: 232 | test: 665 | usd: 0.85 | tests: 192 passed

## Close-out

T28 closes the current local wave deliveries. Earlier wave status entries above are historical; the current summaries and owner report supersede them. 8/8 wave artifact deliveries, 8/8 with admitted crops. Wikisource delivered 12,356 evaluation crops from 400 read pages; human labels are available only for one-to-one aligned lines.

Merged 293,480 wave rows; repaired lexicon pages 70/10/20 with seed 20261015; removed 41 train rows by global label hold-out. Source-cap violations are reported and retained. Original wave files/crops remain unchanged. Offline tests: 66 passed; no network, Google calls or Git writes.

[Owner report](COLLECTION_REPORT.md) · [validation](validation.json) · [provenance](data_provenance.json) · [inventory](INVENTORY.md) · [Finder image index](../../../harvest/harvest_big/collection/SHEETS.md)

T28: done | waves: 8/8 | train: 228445 | dev: 15646 | test: 49348 | poly: 178109 | mono: 75853 | cs: 8050 | latin: 15201 | cyr: 16226 | usd_total: 9.95 | tests: 66 passed

## Clean-up v2 (anomaly decisions applied)

2026-10-15 14:00 Athens. Owner: "OK apply this" after the Opus adjudication pass (120 dossiers, 16 rules, [DECISIONS.md](../analysis/DECISIONS.md)). Applied with `scripts/harvest/apply_clean.py` using the **strict** crop/label variant (R3 needs the low characters-per-pixel signal or two of its three signals; R13 bad-page share recomputed on it) and the Liddell-Scott lexicon (mixed/archive_b28038630) moved wholly to train so every book sits in one split.

Pool v1 293,439 → dropped 21,449 (DROP_BOOK 2,783; R2 column merges 5,274; R3 2,948; R7 bare capital vowel 7,397; R5 2,435; R13 1,976; R15 2,860; R12 765; R4 592; R10 394; R6 175; R14 155; R9 127; R1 92 — overlapping) → relabelled 10,313 (R6 9,853 breathing-on-capital, R8 112, R15 364; label_v1 kept on the row) → 2,868 lexicon lines moved dev/test → train → 3 train rows rejected by the label hold-out after relabel → **271,987 admitted v2** (train 214,436 / dev 13,522 / test 44,029; poly 161,399 / mono 73,074 / cs 7,621 / latin 14,425 / cyr 15,468). Books in several splits: 0. Crop sample 2,804 rows, 0 missing. Pool v1, wave files and crops untouched. Reserved Wikisource human labels in the hold-out: 3,114 distinct (T28 had reported 16,693 with the same function; the hold-out also contains every dev/test label, so the difference does not change the check). Tests: tests/test_apply_clean.py 5 passed; two stale T28 assertions (run-1 budget total 9.345, "receipt-only") updated to the final-run values.

Not applied (owner's eye, see DECISIONS.md contradictions): R4 drops ~60 genuine printed doubles; Vouli column detection errs both ways; R12 on KEEP theses 130–132.

[Clean report](v2/CLEAN_REPORT.md) · [validation](v2/validation_v2.json) · [dropped](v2/dropped_v2.jsonl) · [relabels](v2/relabels_v2.jsonl) · [split moves](v2/split_moves_v2.json). Bulk v2 files (admitted_all_v2.jsonl, manifest_v2_*.json, import_real_v2_*.jsonl) are git-ignored and rebuilt by `.venv/bin/python -m scripts.harvest.apply_clean`.

CLEAN_V2: done | variant: strict | pool_v1: 293439 | dropped: 21449 | relabelled: 10313 | moved: 2868 | rejected: 3 | admitted_v2: 271987 | train: 214436 | dev: 13522 | test: 44029 | poly: 161399 | mono: 73074 | cs: 7621 | latin: 14425 | cyr: 15468

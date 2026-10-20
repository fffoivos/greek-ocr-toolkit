# G1 — Harvested-label line geometry

Offline study of the stable pixel page-line detector. Source harvest data and prediction files were read-only. No recognition inference, network call, publication or replacement of an admitted crop was performed.

All **1195 planned pages** have disposition ledgers: **995 test** and **200 sampled training** pages, containing **53,952 old admitted lines**. The detector succeeded on 1194 pages; 1 page remains unresolved after a detector failure. The repairs are proposals pending the coordinator’s blind adjudication.

There are only **20 safe recuts** and **43,276 unresolved old lines**. No real multi-fragment merge passed every physical guard in this study. The broad geometry-positive rate does not qualify an automatic filtering or dataset-replacement policy.

**Commits are blocked.** Git could not create the shared worktree metadata `index.lock` under the main checkout’s `.git/worktrees/`. No commit or push was made. The source-bound patches in `patches/` are the small-step handoff. The main checkout and other worktrees were not modified.

## Sources and population

The admitted test manifest has **997 pages / 44,029 lines**. Both E3 seed files have **42,038 lines on the same 995 pages**. The two pages absent from E3 are `mixed/16555249-p000094`, `wikisource/416065e0-p000106`. The study includes every admitted line on the 995 selected pages, even when that line has no E3 prediction. Flag agreement uses only the 41,903 matched prediction lines; training lines and codec-excluded lines remain in the disposition ledger. Neither a length flag nor a prediction text can discard an admitted line.

Training selection: seed **20261016**, equal-wave quotas (28 or 29 pages), uniform sampling without replacement within each wave. The overall training tool-positive ratio uses page inclusion weights `N_wave / n_wave`; it is an estimated ratio of totals. Its value is **77.46%**. This is a detector-audit positive rate, not a human-confirmed corruption rate. The 40 historical judgments are a selected test burst sample and cannot validate the training population estimate.

Source reconciliation matched **53,952 fragment boxes/texts on 1195 pages** against frozen native-frame Google assignments. Five provider layouts were replayed from raw responses. Raw byte-hash mismatches among those witnesses: **1**; all five native geometry/text replays agree. Parliament’s established normalized-vertex adapter is retained where its integer coordinates disagree. The raw byte discrepancy is documented in `CUSTODY.json`; no source receipt was repaired.

Sources: [selection receipt](artifacts-owned/plan.receipt.json), [plan](artifacts-owned/plan.jsonl), [source reconciliation](artifacts-owned/layout_custody.jsonl), [metrics](METRICS.json), [complete ledger](artifacts-owned/ledger.jsonl). Input hashes were rechecked when this report was generated.

## Method and evidence

1. Run `pages.process_page` with guarded row joining, tables/statistics/orientation off. Cache addressed row curves, row structure, foreground and component labels, bound to source pixels and detector source. Caches live under the output tree because `docs/harvest/` is immutable.

2. A Google box owns a row when its mean vertical overlap across shared X columns is at least 50% of box height. Multiple qualifying rows or no qualifying row produce `cross_row`. Row ink is the detector’s assigned components, including owned pixels outside its returned ribbon; ribbon residual ink is not a row label witness.

3. `fragment` means additional owned row ink or admitted siblings. `overrun` means a different detector row has assigned ink inside the Google box. Siblings assemble in X order using their admitted v2 Google fragment labels, preserving existing diacritic cleaning. Original provider text is retained separately for custody; raw text must not undo established label repairs. Any uncovered row ink, including at row ends, is `gap`; overlapping fragment ink custody blocks a merge. No text-length heuristic supplies missing text.

4. Compare the original crop’s stored, possibly trimmed bounds with the fitted body and upper-accent curves. Report guide cut depth and require actual owned ink for `body_cut` or `accents_cut`. `accent_bottom` is the lower edge of the upper accent band. A missing owner makes clipping unevaluable; `clip_status=ok` on those rows is a nominal category, not a successful clipping check.

5. Safe complete rows can be recut with native X sampling, baseline-relative unrolling, 0.2-xheight margins and the detector boundary mask. Recuts refuse cross-row ownership, overruns, gaps, overlapping label custody, ambiguous boxes touching the row, unclassified cut ink, or a detector boundary that cuts its own assigned ink. The row ledger preserves the transform and PNG hash. A separate preservation check binarizes each candidate’s old native crops before page-level foreground suppression and refuses any ink outside the proposed band. A representative is `recropped`; additional old fragments are `merged_into` its new row ID.

The first ribbon-only probe was withdrawn after visual inspection showed why residual ink needs explicit ownership. Only `artifacts-owned/` contributes to these results. The smaller/older probe directories are excluded. Native recut QA additionally found an omitted word tail: `cyrillic/94847f75-p000170-l0062` would lose 178 right-tail foreground pixels. The final preservation guard withdraws that proposal; previously generated unsafe proposals are quarantined under `withdrawn_recuts/`, not counted as recuts. Rows with a full box but semantically incorrect Google text can remain undetected: geometry does not transcribe missing words.

## Per-wave results

Counts include all old admitted lines on selected pages. `recut` counts unique new rows; `unresolved` counts old lines. 2,542 clipping checks are unevaluable; 135 lines have no detector measurement because their page failed. Failed-page nominal cross/ok categories are retained for exhaustive accounting and excluded from agreement.

| Split / wave | Pages | Lines | Whole | Fragment | Overrun | Cross | Clip OK | Accents | Body | Recut rows | Unresolved |
|---|---|---|---|---|---|---|---|---|---|---|---|
| test/cyrillic | 21 | 658 | 360 | 270 | 28 | 0 | 656 | 0 | 2 | 0 | 307 |
| test/mixed | 67 | 2199 | 622 | 529 | 880 | 168 | 1722 | 6 | 471 | 2 | 1663 |
| test/openarchives | 154 | 4680 | 2205 | 2349 | 21 | 105 | 4647 | 1 | 32 | 1 | 2497 |
| test/parliament | 99 | 11942 | 1551 | 1000 | 8033 | 1358 | 7647 | 230 | 4065 | 0 | 10947 |
| test/round1 | 188 | 8115 | 2188 | 1426 | 4323 | 178 | 6766 | 16 | 1333 | 1 | 6414 |
| test/round2 | 75 | 3689 | 1012 | 633 | 1941 | 103 | 2718 | 13 | 958 | 0 | 2807 |
| test/vouli | 49 | 1742 | 90 | 102 | 1479 | 71 | 1007 | 13 | 722 | 0 | 1705 |
| test/wikisource | 342 | 10999 | 2679 | 3517 | 4603 | 200 | 9718 | 38 | 1243 | 11 | 8923 |
| train/cyrillic | 29 | 1167 | 391 | 275 | 479 | 22 | 1127 | 8 | 32 | 0 | 859 |
| train/mixed | 29 | 1455 | 161 | 168 | 1087 | 39 | 1302 | 8 | 145 | 0 | 1338 |
| train/openarchives | 29 | 756 | 315 | 390 | 4 | 47 | 753 | 0 | 3 | 0 | 443 |
| train/parliament | 29 | 3462 | 925 | 443 | 1957 | 137 | 2449 | 57 | 956 | 5 | 2722 |
| train/round1 | 28 | 1057 | 239 | 211 | 579 | 28 | 812 | 2 | 243 | 0 | 850 |
| train/round2 | 28 | 983 | 249 | 194 | 504 | 36 | 751 | 4 | 228 | 0 | 768 |
| train/vouli | 28 | 1048 | 69 | 89 | 840 | 50 | 849 | 9 | 190 | 0 | 1033 |

Disposition totals: **kept: 10,656**, **merged_into: 0**, **recropped: 20**, **relabelled_same_pixels: 0**, **unresolved: 43,276**.

| Unresolved reason | Old lines |
|---|---|
| ambiguous_box_touches_row | 20567 |
| cross_row:multiple_owners | 575 |
| cross_row:no_detector_row | 220 |
| cross_row:under_half_height | 1612 |
| cut_ink_outside_guide_classes | 120 |
| detector_band_cuts_owned_ink | 8903 |
| gap | 9594 |
| overlapping_fragment_ink | 10 |
| overrun | 1460 |
| page_failure:TypeError | 135 |
| recut_would_discard_old_crop_ink | 80 |

| Split / wave | Gap | Overrun | Cross | Ambiguous touching box | Detector cuts own ink | Native preservation refusal | Other |
|---|---|---|---|---|---|---|---|
| test/cyrillic | 256 | 12 | 0 | 28 | 9 | 0 | 2 |
| test/mixed | 464 | 57 | 168 | 910 | 62 | 1 | 1 |
| test/openarchives | 2309 | 13 | 105 | 8 | 30 | 24 | 8 |
| test/parliament | 457 | 305 | 1223 | 5141 | 3668 | 9 | 144 |
| test/round1 | 1120 | 314 | 178 | 4399 | 391 | 4 | 8 |
| test/round2 | 503 | 94 | 103 | 1770 | 331 | 4 | 2 |
| test/vouli | 38 | 60 | 71 | 607 | 926 | 2 | 1 |
| test/wikisource | 3113 | 276 | 200 | 3550 | 1666 | 28 | 90 |
| train/cyrillic | 204 | 68 | 22 | 453 | 111 | 1 | 0 |
| train/mixed | 116 | 59 | 39 | 891 | 232 | 0 | 1 |
| train/openarchives | 384 | 0 | 47 | 1 | 9 | 2 | 0 |
| train/parliament | 313 | 86 | 137 | 1362 | 814 | 4 | 6 |
| train/round1 | 154 | 43 | 28 | 528 | 97 | 0 | 0 |
| train/round2 | 143 | 30 | 36 | 468 | 89 | 1 | 1 |
| train/vouli | 20 | 43 | 50 | 451 | 468 | 0 | 1 |

## Independent agreement

Positive tool decision: `span_status != whole_row OR clip_status != ok`. Precision/recall below treat length flags as the reference only for **agreement**, not as verified corruption truth. The primary final-line flag comparison uses **both seeds**.

| Flag reference | TP | FP | FN | TN | Precision | Recall |
|---|---|---|---|---|---|---|
| s0 | 1156 | 31032 | 31 | 9684 | 3.59% | 97.39% |
| s1 | 1160 | 31028 | 35 | 9680 | 3.60% | 97.07% |
| both | 884 | 31304 | 22 | 9693 | 2.75% | 97.57% |
| union | 1432 | 30756 | 44 | 9671 | 4.45% | 97.02% |

| Test wave | Both flags: TP | FP | FN | TN | P | R |
|---|---|---|---|---|---|---|
| cyrillic | 1 | 168 | 0 | 177 | 0.59% | 100.00% |
| mixed | 140 | 1411 | 7 | 593 | 9.03% | 95.24% |
| openarchives | 20 | 2443 | 5 | 2174 | 0.81% | 80.00% |
| parliament | 197 | 10165 | 1 | 1438 | 1.90% | 99.49% |
| round1 | 195 | 5731 | 2 | 2155 | 3.29% | 98.98% |
| round2 | 158 | 2510 | 2 | 981 | 5.92% | 98.75% |
| vouli | 128 | 1529 | 0 | 82 | 7.72% | 100.00% |
| wikisource | 45 | 7347 | 5 | 2093 | 0.61% | 90.00% |

Historical ASTRA comparison: **32/40 binary agreements** (M/C positive; R/L negative), 40/40 covered. This is primary-burst-cause agreement, not exhaustive defect-presence accuracy. Some historical R/L rows explicitly also have span defects. [Original ASTRA table](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/reviews/ASTRA-E3plan_review_1_full.md); [all 40 tool decisions](artifacts-owned/vs_40.jsonl).

| Historical class | Rows | Geometry detected |
|---|---|---|
| M | 23 | 23 |
| C | 7 | 7 |
| R | 8 | 6 |
| L | 2 | 2 |

| Human reference | TP | FP | FN | TN | Precision | Recall |
|---|---|---|---|---|---|---|
| M/C vs R/L | 30 | 8 | 0 | 2 | 78.95% | 100.00% |

| ASTRA wave | Binary agreements | Precision | Recall |
|---|---|---|---|
| cyrillic | 1/1 | n/a | n/a |
| mixed | 5/6 | 80.00% | 100.00% |
| openarchives | 5/5 | 100.00% | 100.00% |
| parliament | 6/6 | 100.00% | 100.00% |
| round1 | 4/6 | 66.67% | 100.00% |
| round2 | 4/6 | 66.67% | 100.00% |
| vouli | 5/5 | 100.00% | 100.00% |
| wikisource | 2/5 | 40.00% | 100.00% |

## Failure witnesses and unresolved work

These witnesses are diagnostic examples, not newly adjudicated ground truth. The original 40 judgments remain unchanged.

| Line | ASTRA | Tool | Disposition / reason | Pixels |
|---|---|---|---|---|
| bf9e75e3d578179c81701e86-p000079-l0033 | M | cross_row/ok | cross_row:under_half_height | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/mixed/crops/bf9e75e3/p000079-l0033.png) |
| b7de2754269251a231d83a36-p000025-l0034 | M | overrun/body_cut | ambiguous_box_touches_row | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/mixed/crops/b7de2754/p000025-l0034.png) |
| bf9e75e3d578179c81701e86-p000079-l0003 | R | cross_row/ok | cross_row:under_half_height | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/mixed/crops/bf9e75e3/p000079-l0003.png) |
| b7de2754269251a231d83a36-p000066-l0053 | M | overrun/body_cut | ambiguous_box_touches_row | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/mixed/crops/b7de2754/p000066-l0053.png) |
| b7de2754269251a231d83a36-p000066-l0056 | M | overrun/body_cut | ambiguous_box_touches_row | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/mixed/crops/b7de2754/p000066-l0056.png) |
| 0b63328a-p000057-l0031 | C | fragment/body_cut | recut_would_discard_old_crop_ink | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/openarchives/crops/0b63328a/p000057-l0031.png) |
| c82ac45f-p000067-l0029 | M | fragment/ok | gap | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/openarchives/crops/c82ac45f/p000067-l0029.png) |
| c82ac45f-p000083-l0013 | C | whole_row/body_cut | cut_ink_outside_guide_classes | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/openarchives/crops/c82ac45f/p000083-l0013.png) |
| 0b63328a-p000017-l0021 | M | fragment/ok | gap | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/openarchives/crops/0b63328a/p000017-l0021.png) |
| c82ac45f-p000058-l0006 | C | whole_row/body_cut | cut_ink_outside_guide_classes | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/openarchives/crops/c82ac45f/p000058-l0006.png) |
| 20900789-p000006-l0082 | M | cross_row/ok | cross_row:under_half_height | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/parliament/crops/20900789/p000006-l0082.png) |
| 548cab64-p000026-l0116 | C | overrun/body_cut | detector_band_cuts_owned_ink | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/parliament/crops/548cab64/p000026-l0116.png) |
| 87d33c70-p000013-l0066 | M | overrun/body_cut | detector_band_cuts_owned_ink | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/parliament/crops/87d33c70/p000013-l0066.png) |
| 87d33c70-p000013-l0039 | M | overrun/body_cut | ambiguous_box_touches_row | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/parliament/crops/87d33c70/p000013-l0039.png) |
| 548cab64-p000008-l0103 | M | overrun/body_cut | detector_band_cuts_owned_ink | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/parliament/crops/548cab64/p000008-l0103.png) |
| 87d33c70-p000031-l0117 | C | overrun/body_cut | detector_band_cuts_owned_ink | [old crop](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/parliament/crops/87d33c70/p000031-l0117.png) |

Detector failure `parliament/100763df-p000027`: `TypeError('expected non-empty vector for x')`. Its old IDs remain unresolved. No fallback row geometry or invented labels were used.

The stable detector sometimes groups running furniture (for example a page number and running title) into one row. A title-only admitted label then has uncovered row ink and is unresolved. Exact box edges can also leave small owned overhangs; those are recorded literally, rather than being silently called a missing word. Detector ownership, body/accent guide borrowing and row tessellation still require native-pixel adjudication.

A strict preservation counterexample is `openarchives/0b63328a-p000057-l0028`: its complete heading-fragment assembly is refused because two left-edge foreground pixels fall outside the detector extent. Accepting such cases safely requires resolving native overhang ownership; this pass does not silently tolerate the loss or enlarge a box across a detector boundary.

## Blind adjudication package

**600 lines / 30 sheets**, 20 per sheet, and **50 full test-page overlays**. All 50 page overlays have detector rows; a box-only failed-page witness is retained separately under `review/failed_pages/`. The line sample has 300 wave/book-stratified both-seed flags and 300 uniformly random neither-seed controls, deterministically shuffled. Keep `review/private/blind_key.jsonl` hidden until judgments are frozen. The sheets withhold model predictions and detector decisions; primary recognition-error attribution therefore remains unavailable until the coordinator supplies prediction evidence. The schema retains M/C/R/L/OK and explicit uncertainty fields.

[First contact sheet](artifacts-owned/review/blind-001.jpg), [line manifest](artifacts-owned/review/manifest.jsonl), [whole-page manifest](artifacts-owned/review/page_manifest.jsonl), [schema](classification_schema.json), [empty adjudication file](adjudication.jsonl), [600 blank keyed forms](artifacts-owned/review/adjudication_template.jsonl). No new human judgments have been claimed.

All **20 surviving recuts** also have a separate [old/new contact sheet](artifacts-owned/review/recuts-001.jpg) and [manifest](artifacts-owned/review/recut_manifest.jsonl), for proposal QA rather than population estimation. Passing these guards does not certify transcription accuracy or complete physical row ownership.

## Timing and Linux projection

Mean cold detector wall time: **10.502 s per successful page**; sum **3.483 occupied worker-hours**. This Mac CPU pass used two workers initially and four after a cache-resuming restart; a separate two-worker Wikisource shard overlapped the long Parliament pages, and isolated cross-wave read-back witnesses were also precomputed. Cached receipts retain their original detector time. These are observed Mac wall times under concurrency, not CPU instruction counts or a Linux benchmark.

The final cache-only ownership/span/clipping/recut audit averaged **0.326 s/page**. The cold-detector figure and Linux table exclude cache-writing and contact-sheet work. [Runtime environment](artifacts-owned/runtime_environment.json); [final artifact checks](artifacts-owned/validation.receipt.json).

The table extrapolates each wave’s measured mean to all its admitted train/dev/test pages. Assumptions: 1× Linux/Mac per-worker throughput; eight independent Linux CPU workers; perfect scheduling. Halving/doubling per-worker throughput doubles/halves those durations. Failed pages, I/O, memory contention and review time are not predicted. A Linux five-page timing probe is still required to replace this assumption.

| Wave | Measured pages | s/page | Full admitted pages | 1-worker hours at 1× | 8-worker minutes at 1× |
|---|---|---|---|---|---|
| cyrillic | 50 | 3.205 | 325 | 0.289 | 2.2 |
| mixed | 96 | 4.372 | 701 | 0.851 | 6.4 |
| openarchives | 183 | 2.953 | 913 | 0.749 | 5.6 |
| parliament | 127 | 49.677 | 686 | 9.466 | 71.0 |
| round1 | 216 | 5.324 | 1516 | 2.242 | 16.8 |
| round2 | 103 | 5.604 | 605 | 0.942 | 7.1 |
| vouli | 77 | 9.992 | 739 | 2.051 | 15.4 |
| wikisource | 342 | 7.641 | 398 | 0.845 | 6.3 |

## Validation and handoff

New G1 suite: **45 passed**, including synthetic ownership/span/clipping witnesses and native pixel/hash read-back on five real pages. Broader regression: **3275 passed**, 19 skipped. The full unfiltered suite initially had **5 failures and 5 errors**: missing git-ignored harvest inputs/indices and pre-existing vendor-inventory/API-example checks. The green regression invocation excludes those two data-output modules and the two existing failing documentation/inventory tests; no unrelated test was changed. Exact commands and logs are in `artifacts-owned/tests.receipt.json`.

The handoff consists of the implementation/CLI, Linux launcher, report generator, complete per-old-line and per-row ledgers, source-bound detector caches, proposed PNG recuts, contact sheets, schema, and receipts. [FILES.tsv](FILES.tsv) lists generated/source artifacts with sizes and SHA-256 hashes; original crop/render paths and hashes are bound by the plan, ledger and selection receipt.

Owner questions: confirm whether running furniture should share a row label; qualify detector false positives on the blind controls; decide how R should be adjudicated after predictions are unblinded; investigate the round1 raw-byte discrepancy and the detector’s failed rule fit; and approve any later admission/export policy only after blind review. This pass publishes no repaired dataset.

G1: done | test_pages: 995 train_pages: 200 | span: whole 13056 fragment 11596 overrun 26758 cross 2542 | clip: ok 42924 accents 405 body 10623 | recut: 20 unresolved: 43276 | vs_flags: P 0.0275 R 0.9757 | vs_40: 32/40 | s_per_page: 10.502 | tests: 45 passed

## G1b calibration

G1b supersedes the G1 touch-based decisions above. **All 995 test pages and the same 200 training pages were rescored offline**, retaining all **53,952 old lines**. The locked audit flags **4,372 (8.10%)**, with **1,612 span** and **3,355 clipping** positives (families overlap). The fresh random estimate is **16/300 = 5.33%**; seven safe recuts were regenerated. Source crops, labels, detector caches and G1 evidence were not replaced.

**Qualification:** these are measured audit candidates, not human-certified defects. Development precision is **69.77%**, with **13 reference-negative positives**. The reduction makes a review pilot smaller, but the requested statement that every positive is a physical defect is **not established**. The low body threshold and large span threshold below expose a remaining detector/label-reference trade-off; they must not be hidden by the aggregate recall.

Development protocol: seed **2026101602**, uniform sampling without replacement from the 53,952 selected-page lines after excluding the historical 40. The first 160 sampled lines form development; a disjoint next 300 were reserved before scoring. **Eight sheets, 20 lines each**, show the native crop and full-width source context with only the target crop rectangle. IDs, labels, flags, predictions, detector curves, scores and replacement proposals were withheld during pixel review. All 160 judgments contain a class and a pixel-specific reason in [dev_adjudication.jsonl](dev_adjudication.jsonl); the [key](dev_adjudication_key.jsonl) was joined after the freeze. Judgments were frozen at `2026-10-16T13:36:54.368329+00:00` (SHA-256 `440a1d5eaf558858adcd88350c3494ca6c9dd8a70ad01ee040c50ea913c8ec87`). The final threshold lock is dated `2026-10-16T13:45:49.234498+00:00`. Feature extraction and all threshold computations followed the judgment freeze. An initial development-only search without density corroboration is retained in `artifacts-calibrated/initial_development_search.json`; no held-out score was used to revise the final rule or thresholds.

The new pixel judgments are **AI adjudication**, not independent human truth: **157 OK, 2 M, 1 C**. M means a substantial missing printed-row segment; C means destructive body/accent loss. Isolated punctuation or detached neighbor traces were treated as immaterial. Pixel-only sheets cannot identify an invisible label omission or a model recognition error. The historical 40 keep their original primary M/C/R/L classes, including R/L cases that can have secondary geometry defects.

Raw feature definitions (retained for every old line in the [calibrated ledger](artifacts-calibrated/ledger.jsonl), with explicit nulls for unmeasurable owners):

- `ink_outside_box_left/right`: number of owning-row occupied columns outside the Google box, divided by row x-height. Only columns with mass at least 30% of the median nonzero owning-row column mass count. Whitespace and distance to a remote speck do not count as ink. `row_ink_extent_xh` is the first-to-last qualified column extent, including internal whitespace.
- `body_cut_fraction`: area fraction of [meanline, baseline] outside the actual stored crop vertically, integrated over qualified ink columns shared with the crop. `accent_cut_fraction` is the analogous [accent_top, accent_bottom] band fraction. A cut decision also requires actual owned ink to be lost from that band; raw guide loss alone is insufficient. `body_ink_cut_fraction` and `accent_ink_cut_fraction` separately retain lost ink fractions. The fractions are dimensionless, not x-height lengths.
- `box_height_in_row`: mean ribbon overlap on shared X columns divided by Google box height. A unique under-half-height candidate gets diagnostic measurements without being promoted to safe recut ownership. Multiple qualifying owners remain unresolved; no candidate or invalid geometry is a detector failure.
- `label_vs_ink_ratio`: NFD code points (including spaces/combining marks) per qualified owning-row extent in x-heights, divided by the page median of that ratio. It is supporting evidence, never a standalone physical-defect decision.
- `neighbour_body_ink_xh`: maximum qualifying body-ink columns from another assigned row inside the Google box, divided by that neighbor’s x-height. It requires actual body ink, not a ribbon or an accent-only touch. Density corroboration suppresses some detector splits of one physical row.

**Locked decision:** `span_defect` is fragment ink outside either box side exceeding the ink threshold, or neighbor body ink exceeding that threshold with low label/ink density, or a corroborated cross-row height deficit. `clip_defect` is a body or accent band fraction exceeding its threshold with nonzero actual band ink cut. Comparisons are strict; equality is negative. The OR of the two families is the audit positive.

|Parameter|Locked value|
|---|---|
|ink_out|16 xh|
|body_cut|0.005|
|accent_cut|0.15|
|label_ratio_support_max|0.9 (overrun/cross only)|
|box_height_min|0 (cross channel disabled at this operating point)|
|column mass minimum|0.30 of nonzero median|

Threshold search: **41888 settings**, only the 200 development references; minimize positive count subject to combined M+C recall ≥90%. Ties prefer higher recall, then larger ink/body/accent thresholds, smaller density-support maximum and smaller cross threshold. The complete grid, lock and five development operating points are in [locked_thresholds.json](locked_thresholds.json). Each curve row is independently optimized at its recall target; the 90% target row is the sole deployed policy.

|Recall target|Ink xh|Body|Accent|Density max|Cross min|M+C detected|Recall|Positive rate|
|---|---|---|---|---|---|---|---|---|
|100.00%|0.05|0.4|0.15|0.9|0|33/33|100.00%|84/200 (42.00%)|
|95.00%|0.05|0.6|0.15|0.9|0|32/33|96.97%|83/200 (41.50%)|
|90.00%|16|0.005|0.15|0.9|0|30/33|90.91%|43/200 (21.50%)|
|85.00%|16|0.005|0.3|0.9|0|29/33|87.88%|39/200 (19.50%)|
|80.00%|20|0.005|1|0.9|0|27/33|81.82%|35/200 (17.50%)|

|Development class|Lines|Detected|
|---|---|---|
|M|25|22|
|C|8|8|
|R|8|3|
|L|2|1|
|OK|157|9|

Selected point: **30/33 M+C = 90.91% recall; 43/200 = 21.50% positives**. The historical subset detects **28/30** M+C; the random development subset detects **2/3**. Random development produces **11/160** positives, including **9** judged OK. Thus the combined ≥90% recall does not establish ≥90% recall on the random population.

The three missed development positives are:

|Line|Reference|Evidence limitation|
|---|---|---|
|openarchives/0b63328a-p000017-l0021|M|Historical missing-label span, but fitted row largely fits box; no material measured extent.|
|openarchives/c82ac45f-p000067-l0029|M|Historical missing-label span, but fitted row largely fits box; no material measured extent.|
|openarchives/f35043b8-p000011-l0015|M|Pixel review: omitted contents page number; detector owns it separately.|

Per-wave calibrated counts below are old-line counts; span and clip overlap, and recuts are unique new rows. A negative with a refused recut still gets `measured_ok`; a positive with a refused recut gets `measured_defect`. Gap, ambiguous touch, detector boundary ink, overrun and preservation refusals remain in `recut_block_reason`, without being counted as unresolved audit decisions.

|Split / wave|Pages|Lines|Positive|Rate|Span|Clip|Unresolved|Recut rows|
|---|---|---|---|---|---|---|---|---|
|test/cyrillic|21|658|19|2.89%|19|0|0|0|
|test/mixed|67|2199|262|11.91%|152|197|78|0|
|test/openarchives|154|4680|55|1.18%|26|32|101|1|
|test/parliament|99|11942|2081|17.43%|718|1536|316|0|
|test/round1|188|8115|277|3.41%|69|253|133|1|
|test/round2|75|3689|306|8.29%|159|250|18|0|
|test/vouli|49|1742|267|15.33%|55|237|9|0|
|test/wikisource|342|10999|348|3.16%|75|282|89|3|
|train/cyrillic|29|1167|26|2.23%|12|16|20|0|
|train/mixed|29|1455|34|2.34%|23|11|39|0|
|train/openarchives|29|756|6|0.79%|6|2|47|0|
|train/parliament|29|3462|469|13.55%|253|346|10|2|
|train/round1|28|1057|96|9.08%|18|84|18|0|
|train/round2|28|983|79|8.04%|25|63|9|0|
|train/vouli|28|1048|47|4.48%|2|46|43|0|

Unresolved is limited to **575 multiple owners**, **220 no valid detector row**, and **135 lines on the failed detector page**: **930 total**. No failed measurement is asserted negative in the ledger.

Locked external evaluation: **906 both-seed flags** were retained; **629 detected**, **271 measured misses**, **6 abstentions**. Precision needs the control population, so P/R agreement uses all **41,903 measurable-page matched prediction lines**, with abstentions conservatively counted as not detected: **P 17.67%, R 69.43%**. Confusion: TP 629, FP 2930, FN 277, TN 38067. Excluding ownership abstentions gives measured-only R **69.89%** on 900 flags. There are 582 abstentions across the 41,903 lines. These are model-length **agreement**, not verified physical precision. The full 906 include historical development cases and therefore are not an independent hold-out set.

**Fresh random300:** positive **16/300 (5.33%)**, span **8/300 (2.67%)**, clip **11/300 (3.67%)**; **3** have both families. Four lines abstain. The Wilson 95% interval for the measured-positive rate over all 300 is **3.31%–8.49%**. Assigning every abstention positive would give 6.67%. This estimates audit review load among lines on the selected 1,195 pages, conditional on that page plan; it is not a human-confirmed defect prevalence estimate or an unweighted estimate for the entire training census. The 300 are disjoint from all development lines.

**Recuts:** unchanged G1 guards leave 20 physically safe original proposals. Of these, **7** are calibrated positives and were regenerated from native source pages: **5 test + 2 training**, one old line per new row; **0 merges**. There are **0 newly safe rows**: calibration of an audit decision cannot waive complete fragment coverage, zero gap, unique ownership, non-overrun, non-overlapping custody, native ink preservation or the original conservative boundary/touch refusals. The other 13 original proposals do not meet the calibrated defect threshold. All seven have zero native preservation loss and PNG hashes identical to the original safe G1 proposals. [Recut manifest](artifacts-calibrated/recuts.jsonl), [old/new sheet](artifacts-calibrated/review/calibrated-recuts.png). No admitted data were replaced.

**Timing:** detector execution is unchanged: **10.502 s/page** observed on this Mac, reused from the same 1,194 successful-page receipts; no detector rerun. Magnitude extraction from cached masks took **113.36 s total (0.095 s/planned page)**, excluding review sheets and threshold fitting. Linux projection below repeats the per-wave cold-detector cost using measured Mac means, Linux/Mac per-worker throughput assumed 1×, eight independent workers and perfect scheduling. It remains an assumption, not a Linux benchmark; I/O, cache writing, calibration and review are excluded.

|Wave|Measured pages|s/page|Full admitted pages|1-worker hours at 1×|8-worker minutes at 1×|
|---|---|---|---|---|---|
|cyrillic|50|3.205|325|0.289|2.2|
|mixed|96|4.372|701|0.851|6.4|
|openarchives|183|2.953|913|0.749|5.6|
|parliament|127|49.677|686|9.466|71.0|
|round1|216|5.324|1516|2.242|16.8|
|round2|103|5.604|605|0.942|7.1|
|vouli|77|9.992|739|2.051|15.4|
|wikisource|342|7.641|398|0.845|6.3|

Validation: **70 targeted tests passed** (45 G1 plus 25 G1b), including scaled native units, the 30% speck boundary, curved bands, borrowed accents without ink, density corroboration, strict threshold boundaries, four native-page pipeline replays and seven recut hash readbacks. The existing green regression invocation passed **3300 tests**, with the same G1 exclusions for unavailable harvest outputs and two pre-existing inventory/API checks. This is not a claim that unfiltered pytest is green; commands and logs are in [tests receipt](artifacts-calibrated/tests.receipt.json).

The CLI now defaults to the packaged locked G1b policy (`--audit-policy calibrated`); `--audit-policy g1` reproduces historical touch decisions. `--thresholds` accepts an explicit lock. The low-level pipeline keeps its legacy call compatible and accepts `audit_thresholds` for calibrated processing. The offline calibration script exposes `sample`, `features`, `fit`, `evaluate` stages with explicit source/output options; scoring never fits thresholds. [CALIBRATION_METRICS.json](CALIBRATION_METRICS.json) is the tracked result summary, and [FILES.tsv](FILES.tsv) binds source, locks, judgments, ledgers, sheets, tests and recuts.

G1b: done | thresholds: ink_out 16 xh, body_cut 0.005, accent_cut 0.15 | dev: recall_MC 90.91% positive_rate 21.50% | flags906: P 0.1767 R 0.6943 | random300: positive 5.33% span 2.67% clip 3.67% | recut: 7 | s_per_page: 10.502 | tests: 3300 passed

## G1c repairs and pilot package

**All 995 test + 200 training pages were processed offline**, retaining all **53,952 old line IDs** and the frozen G1b scores. Of **4,372 measured-positive lines**, **2,220 (50.78%)** have a guarded proposal addressing every flagged family. **447** further lines have a vertical repair while their span family remains pending or unresolved. There are **2,660 expand_vertical**, **0 trim_to_label**, **0 extend_label**, and **7 recut_merge** applied actions; **450 needs_reread** and **1,702 unresolved** are terminal positive-line dispositions. The six counts overlap: a vertical action can accompany a pending span. The terminal reconciliation is **2,220 fully repaired + 450 reread + 1,702 unresolved = 4,372**. The **930 measurement abstentions** remain separate from these calibrated positives.

**These are repair proposals, not adjudicator-certified corrected labels or physical precision.** Here “fully repaired” means that each calibrated family has a supported action under the recorded guards. It does not mean every detector-owned mark belongs to the intended row. No source crop, admitted label, detector cache, model prediction or training manifest was replaced. The public pilot and owner decisions are empty; the coordinator performs adjudication.

**Implementation and guards.** [repairs.py](../../../../greekocr/labelfix/geometry/repairs.py) implements the explicit action guards; [repair runner](../../../../scripts/labelfix/repair_geometry.py) consumes the frozen calibrated ledger and verified cached geometry. [actions.jsonl](artifacts-repairs/actions.jsonl) records every attempted action, including rejected attempts, before/after geometry, occupied-column changes in x-height units, the 0.5-xh limit, guard evidence and status. [ledger.jsonl](artifacts-repairs/ledger.jsonl) keeps the original records and scores plus applied actions, version, resolved/remaining families and output paths.

- **expand_vertical** keeps the old line ID and label with `recrop_version=G1c-1`. Native X columns are unchanged; recorded displacement from both the actual old crop and the Google box must be ≤0.5 xh (actual crop displacement is exactly zero). Font/accent guides receive 0.2-xh margins. The old rectangle is preserved literally, and added pixels are bounded per column by the detector tessellation, with local extensions for assigned ink protrusions. There is no rescaling or baseline interpolation in this action. A plain rectangular envelope was rejected during development because borrowed guides expose adjacent rows. Known/unknown newly exposed foreign ink outside the permitted support is measured and must remain within 0.5 xh. Diagnostic partial-height owners cannot authorize this action. Rejected foreign-ink guards number **336** among uniquely owned clip candidates.
- **trim_to_label** cuts only at an admitted same-row sibling's Google boundary. Every removed native foreground pixel must be inside that sibling's labelled span and retained source crop; no target Google-span ink may be removed. Empty labels, overlapping target/sibling custody, another row and missing crop coverage refuse the cut. A combined vertical/trim action retains the already masked working pixels. **No real positive passes these custody conditions**; the implementation passes a synthetic end-to-end swallowed-sibling case. In this population most overrun evidence concerns another row, and geometry cannot locate characters inside overlapping Google boxes.
- **extend_label** assembles cleaned admitted Google fragment texts in X order only with complete coverage, no duplicated ink custody, one row, preserved native ink, no G1 overrun/ambiguous touches, and a band that preserves assigned ink. Siblings map to one representative crop/label rather than duplicating the assembled training row. **No additional real assembly passes**. A missing owning-row span produces **needs_reread**, never inferred text. [needs_reread.jsonl](artifacts-repairs/needs_reread.jsonl) contains **450 line requests**; [reread_row_inventory.jsonl](artifacts-repairs/reread_row_inventory.jsonl) deduplicates these to **342 detector rows** for later costing. Their native context crops have null labels and are not admitted repair crops. No Google request was made.
- **recut_merge** retains the **seven** G1b proposals, rechecking complete coverage and native preservation and reproducing their exact PNG hashes. As in G1b, all seven are single-fragment row recuts; **zero actual fragment merges** were added. The name retains the existing complete-row route, with `single_fragment=true` recorded explicitly.

The harm guard does not accept an action name as permission to change ink: each explicit exception requires its physical evidence. An unexplained occupied-column change beyond 0.5 xh refuses. Exact-boundary, row-swap, newly exposed foreign ink, missing/overlapping sibling custody, native loss and combined-mask tests are included. Applied physical actions must have every recorded check true. Unresolved/pending disposition events intentionally have failed guard evidence and do not count as physical actions.

**Measured inventory and per-wave dispositions.** There are **2,667 active repair PNGs + 450 unadmitted reread-context PNGs = 3,117 active PNGs**, bound in [crop_inventory.jsonl](artifacts-repairs/crop_inventory.jsonl). Two early rectangular proposals that fail the final guards were moved into `withdrawn_crops/`, with hashes/reasons in [withdrawn_crops.jsonl](artifacts-repairs/withdrawn_crops.jsonl); they are outside the active inventory. Resolved calibrated families: clip **2667 / 3,355**, span **0 / 1,612**; remaining families: clip **688**, span **1612**. Span and clip overlap. Full machine-readable counts are in [REPAIR_METRICS.json](REPAIR_METRICS.json).

|Split / wave|Pages|Positive|Expand vertical|Trim to label|Extend label|Recut merge|Needs reread|Unresolved|Fully repaired|Repair PNGs|Reread PNGs|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|test/cyrillic|21|19|0|0|0|0|15|4|0|0|15|
|test/mixed|67|262|154|0|0|0|46|140|76|154|46|
|test/openarchives|154|55|27|0|0|1|18|10|27|28|18|
|test/parliament|99|2081|1224|0|0|0|125|850|1106|1224|125|
|test/round1|188|277|224|0|0|1|19|62|196|225|19|
|test/round2|75|306|205|0|0|0|35|147|124|205|35|
|test/vouli|49|267|123|0|0|0|20|136|111|123|20|
|test/wikisource|342|348|199|0|0|3|16|136|196|202|16|
|train/cyrillic|29|26|15|0|0|0|11|1|14|15|11|
|train/mixed|29|34|11|0|0|0|12|11|11|11|12|
|train/openarchives|29|6|2|0|0|0|5|1|0|2|5|
|train/parliament|29|469|302|0|0|2|113|159|197|304|113|
|train/round1|28|96|73|0|0|0|9|18|69|73|9|
|train/round2|28|79|58|0|0|0|4|24|51|58|4|
|train/vouli|28|47|43|0|0|0|2|3|42|43|2|
|**Total**|1195|4372|2660|0|0|7|450|1702|2220|2667|450|

**Pixel witnesses and limitations.** [Six native old/new witness panels](artifacts-repairs/qa/repair_witnesses.jsonl) cover parliament, vouli, mixed, round1, round2 and wikisource; they were visually inspected separately from the blind judgments. Parliament `100763df-p000003-l0007` and mixed `0aac601a9e11de9769392ff8-p000005-l0019` visibly restore cut letter strokes. The [wikisource title witness](artifacts-repairs/qa/repair-06.png), `02a3a2a6-p000009-l0010`, also exposes detached quote/mark traces above the title: the detector can assign such marks to the target, so the recorded geometry guards cannot certify their semantic ownership. Existing neighbor traces are deliberately preserved with the old pixels. This is a concrete counterexample to treating an applied expansion as proof of a clean crop; the blind “repair correct?” judgment must assess this. Partial ownership (940 positive lines) and foreign-ink/coverage refusals remain visible, rather than being waived to increase repair coverage.

**Blind adjudication pilot.** Hand the adjudicator only [pilot-blind.zip](artifacts-repairs/pilot-blind.zip) (624,138,900 bytes; 1,987 entries), or the equivalent [pilot directory](artifacts-repairs/pilot/index.html). It contains **300 calibrated positives + 300 random measured-OK lines**, **30 sheets of 20**, individually readable lossless A/B/strip assets, old/comparison labels, and **50 full-resolution native test pages with detector/Google overlays and admitted-label lists**. The native pages are pixel-equal after RGB conversion to their source renders; pages with no detector rows are excluded before seeded page selection. All 50 final pages have detector overlays.

Selection uses line seed **2026101603**, page seed **2026101604**, no replacement. Positives are equal-wave, round-robin-book sampled across the selected test and training pages; controls are a uniform random sample of measured-OK lines. All 600 lines are disjoint from **G1b dev160, random300 and historical40** (500 exclusions), not just the development subset. The positive sample reaches ≥10 books in each wave where possible; cyrillic has only seven positive books available after exclusions. [PILOT_METRICS.json](PILOT_METRICS.json) binds counts and sheet hashes.

|Wave|Positive lines|Positive books / available|Random measured-OK lines|Whole test pages|
|---|---:|---:|---:|---:|
|cyrillic|38|7 / 7|15|7|
|mixed|38|16 / 16|28|7|
|openarchives|38|14 / 14|31|6|
|parliament|38|31 / 31|65|6|
|round1|37|20 / 21|51|6|
|round2|37|15 / 15|29|6|
|vouli|37|15 / 15|16|6|
|wikisource|37|17 / 18|65|6|

Every public line has the same neutral A/B presentation. A is existing; B is the available comparison, repeating A where no repair is available. Neither panel says whether the audit was positive, which action ran, or why an action was refused. Public filenames use anonymous `B0001` etc.; no source IDs, waves, books, scores, action names or expected answers are in the card data. Detector context is present for review, so this is blinding to the measured group and repair metadata, not blinding to visible geometry. Native asset links avoid interpreting a downsampled sheet as native-pixel proof.

[Classification schema](artifacts-repairs/pilot/classification_schema.json) has `primary_cause` = M/C/R/L/OK and `repair_correct` = y/n/u, with secondary causes, confidence and notes. R requires later model-prediction evidence; a visible transcription error is L. [adjudication.jsonl](artifacts-repairs/pilot/adjudication.jsonl) is **zero bytes**; [the 600-record template](artifacts-repairs/pilot/adjudication_template.jsonl) contains only blank judgments and must be filled before schema validation. No adjudicator was run.

The sheet-position → source-line mapping is in **[sealed/sheet_index.jsonl](artifacts-repairs/sealed/sheet_index.jsonl)**, separate from the public archive. The directory is coordinator-only by filesystem mode (0700); this is a handling separation, not encryption. `sealed/page_index.jsonl` maps whole pages, and `sealed/owner_index.jsonl` holds owner control references. Do not hand over `sealed/` or unseal it before freezing judgments. [Package receipt](artifacts-repairs/package.receipt.json) confirms no sealed key is in the ZIP; [sealed receipt](artifacts-repairs/sealed.receipt.json) binds the separate key files.

**Owner deck.** [owner_deck/index.html](artifacts-repairs/owner_deck/index.html) follows the fable branch's local HTML review pattern: old/comparison crops and labels, source strip, native zoom, y/n/u and arrow keys, progress, local browser persistence and JSON download. Its **60 cards = 40 guarded candidates + 20 mixed-in reference controls** are disjoint from the 600-line pilot. The owner question assesses crop geometry; the printed labels identify the target, without making these controls a label-transcription benchmark. Ten controls repeat historical M/C defects unchanged (expected n); ten repeat G1b pixel-reviewed OK lines (expected y). The latter references are **AI pixel adjudication**, not independent human truth. Reference type and expected answers are only in the sealed index. The deck embeds no answers and has not been adjudicated.

**Validation and execution.** All 1,195 native-page hashes, all 4,372 positive source-crop hashes, and 437 used cache receipts/planes were verified. [Readback receipt](artifacts-repairs/validation.receipt.json) verifies all 53,952 retained records/scores, every active PNG/hash, all 2,660 expanded old rasters as literal native subarrays of their replacement, line sampling/disjointness, all 50 native page copies, all 600 anonymous cards and the 60/20 owner split. Six repair panels and the first contact-sheet segment received pixel inspection; this is not adjudication of the pilot population.

**106 targeted tests passed** (70 G1/G1b + 36 G1c). The existing documented regression invocation passed **3,336 tests, 19 skipped, 2 deselected**. The same G1b exclusions remain: `tests/test_apply_clean.py`, `tests/test_collection_outputs.py`, and the two pre-existing vendor inventory/API tests. This is a green scoped invocation, **not unfiltered pytest green**. Commands, source hashes and logs are in [tests.receipt.json](artifacts-repairs/tests.receipt.json). The offline Node DOM-double check verifies y/n/u, arrows, last-card behavior, local persistence and download handling without filling actual decisions. Browser rendering is **not verified**: local Playwright browsers were unavailable/unlaunchable, the tool approval check rejected Firefox UI access, and no in-app browser was available. [Owner logic check](artifacts-repairs/qa/owner_logic.json) labels that limit explicitly.

The final warm-cache repair pass took **240.24 s** (**0.201 s/planned page**), including cache/source verification and PNG production, excluding pilot generation, tests and visual review. There was no detector rerun and no network or recognition inference. This is local proposal-generation timing, not a Linux performance claim.

Reproduce from the worktree with locally staged dependencies:

```sh
PYTHONPATH=. /path/to/python scripts/labelfix/repair_geometry.py --source-root /read-only/harvest-repository
PYTHONPATH=. /path/to/python scripts/labelfix/build_geometry_pilot.py --source-root /read-only/harvest-repository
PYTHONPATH=. /path/to/python scripts/labelfix/validate_repairs.py
node scripts/labelfix/check_owner_deck.mjs
```

The two builders expose explicit source/G1/calibrated/output paths; they fit no thresholds and make no service requests. `FILES.tsv` binds implementation, reports, active/withdrawn proposals, public package and separate sealed evidence. Bulk evidence remains local and git-ignored as in G1/G1b.

G1c: done | expand_vertical 2660 trim_to_label 0 extend_label 0 recut_merge 7 needs_reread 450 unresolved 1702 | positives_repaired: 50.78% | pilot: 300+300 lines, 50 pages, sheets 30 | deck: docs/records/labelfix/geometry/artifacts-repairs/owner_deck/index.html | tests: 3336 passed

## Coordinator: blind pilot adjudication (16 Oct 2026, 17:40 Athens)
Adjudicator: Opus agent, pixels only, no access to `sealed/`; files in `adjudication_20261016/`. Joined against `sealed/sheet_index.jsonl` by the coordinator.

| Population | n | M | C | R | L | OK | M+C |
|---|---:|---:|---:|---:|---:|---:|---:|
| audit-positive | 300 | 36 | 90 | 5 | 22 | 147 | 42.0% |
| measured-OK (random) | 300 | 4 | 1 | 0 | 32 | 263 | 1.7% |

- **Audit:** 42% of positives are verified geometry defects (precision), 49% are fine lines; the residual defect rate among measured-OK lines is 1.7%, so recall of the calibrated audit is high. Non-geometric label defects (L) are 7–11% in both populations and are not the audit's target.
- **Repairs:** `expand_vertical` judged on 165 applied lines: y 126 (≈47 of them neutral: A already fine, B only adds margin), n 37, u 2 → **22% of applied re-crops made the line worse**, by swallowing the neighbouring row on stacked headings, mastheads, tables with leaders, tight line spacing and warped rows (cases B0492, B0467, B0172, B0393, B0510, B0513, B0165). `recut_merge` 2/2 correct. Random controls received no repair (harm 0/300, UB95 0.99%) — this passes trivially and does not test the repair.
- **Acceptance (data plan §2.1):** the audit passes as a screen; **the `expand_vertical` repair does not pass** (harmful-change rate among applied repairs 22%, far above the 2% bound). It returns to Sol (G1d) with a second-row guard.
- **Page coverage (50 pages):** 2,624 printed rows, 2,123 boxed (80.9%), 501 missed, 27 merged, 6 split, 138 headings/table cells unboxed. Page numbers almost never boxed; headings, datelines, signatures, one-word paragraph ends often missed; on skewed polytonic scans the boxes run into the next row (source of the M cases). Two-column 19th-century debate pages lose up to 73% of rows. This is a harvest-level finding: Google's line boxes miss about one printed row in five.

# SF7 RC1 — RB7 readback, LQB choice and sparse candidate

**Chosen variant: A.** The preregistered tier A/B out-of-sample marks precision is A 100.000000%, B 100.000000%. This is an exact tie, so A wins.

**Candidate before audit.** Nothing is bound, registered, submitted or sent. No reader packs were built. No Git writes or authentication refresh occurred. Network was used only for read-only Clariden queries/transfers.

## Verified readback

Job 3687228 and its steps are COMPLETED, exit 0:0. The job log was read before release processing. All 4,881 output hashes match the final receipt; all 3,896 shard-output checks match their stage receipts. The 985 downloaded output files (including 974 shard receipts) match the final receipt. The remote verifier hashes the shard payloads read-only; local release files include the complete per-line rule traces. The final receipt SHA is `09f7c34d982f707fd9d7f51113f313010d4a0c80878c4bbb3da31b44f598103f`.

The initial tar completed all requested outputs but exited 2 for the guessed, nonexistent `config/sf7_production.json`; the actual `config/sf7_job.json` was retrieved separately and matches the run config SHA. This was a missing optional path, not an authentication error. Transfer stderr is retained.

Input maps match sf6 L1R3 3680729 exactly. The selection contains 124,669 unique IDs; every A/B/sf6 overlay covers it once. Original-label hashes match the selection, and the baseline receipt is `c7cfcc852281c9ba6ebbe4c6d121455e8b094f48da84472989b0ac795fd991a3`.

## Release summary

| Variant | Corrected | Unchanged | HOLD | Explicit edited lines | Formatting-only corrected |
|---|---:|---:|---:|---:|---:|
| sf6 | 236 | 10807 | 113626 | 155 | 81 |
| A | 686 | 10807 | 113176 | 605 | 81 |
| B | 675 | 10807 | 113187 | 594 | 81 |

| Variant | Addition | Substitution | Deletion | Alias consume | Alias keep |
|---|---:|---:|---:|---:|---:|
| sf6 | 163 | 0 | 0 | 0 | 0 |
| A | 166 | 496 | 0 | 3 | 0 |
| B | 153 | 495 | 0 | 3 | 0 |

Substitution counts pair removed/added atoms once. Head counts assign the replacement head; quote keep is a decision count. Counts describe accepted edits, not truth correctness.

| Variant | Head | Edits |
|---|---|---:|
| sf6 | accent | 31 |
| sf6 | breathing | 47 |
| sf6 | dialytika | 1 |
| sf6 | subscript | 84 |
| A | accent | 432 |
| A | breathing | 163 |
| A | dialytika | 2 |
| A | quote_alias | 3 |
| A | subscript | 65 |
| B | accent | 426 |
| B | breathing | 155 |
| B | dialytika | 2 |
| B | quote_alias | 3 |
| B | subscript | 65 |

| Variant | Wave | Corrected | Unchanged | HOLD | Edited lines | Add | Substitute | Delete | Alias consume/keep |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| sf6 | mixed | 44 | 1595 | 11588 | 28 | 33 | 0 | 0 | 0/0 |
| sf6 | openarchives | 2 | 37 | 196 | 2 | 2 | 0 | 0 | 0/0 |
| sf6 | parliament | 6 | 269 | 26949 | 3 | 3 | 0 | 0 | 0/0 |
| sf6 | round1 | 112 | 5416 | 38341 | 67 | 69 | 0 | 0 | 0/0 |
| sf6 | round2 | 59 | 2848 | 14119 | 49 | 50 | 0 | 0 | 0/0 |
| sf6 | vouli | 13 | 642 | 22433 | 6 | 6 | 0 | 0 | 0/0 |
| A | mixed | 116 | 1595 | 11516 | 100 | 30 | 82 | 0 | 0/0 |
| A | openarchives | 4 | 37 | 194 | 4 | 2 | 2 | 0 | 0/0 |
| A | parliament | 24 | 269 | 26931 | 21 | 3 | 20 | 0 | 0/0 |
| A | round1 | 329 | 5416 | 38124 | 284 | 76 | 235 | 0 | 2/0 |
| A | round2 | 175 | 2848 | 14003 | 165 | 45 | 130 | 0 | 0/0 |
| A | vouli | 38 | 642 | 22408 | 31 | 10 | 27 | 0 | 1/0 |
| B | mixed | 114 | 1595 | 11518 | 98 | 27 | 82 | 0 | 0/0 |
| B | openarchives | 3 | 37 | 195 | 3 | 1 | 2 | 0 | 0/0 |
| B | parliament | 23 | 269 | 26932 | 20 | 2 | 20 | 0 | 0/0 |
| B | round1 | 323 | 5416 | 38130 | 278 | 70 | 235 | 0 | 2/0 |
| B | round2 | 175 | 2848 | 14003 | 165 | 45 | 130 | 0 | 0/0 |
| B | vouli | 37 | 642 | 22409 | 30 | 8 | 26 | 0 | 1/0 |

## LQB method and coverage

Truth: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-secondary/docs/labelfix/lqb/truth_v1_1.jsonl`, SHA `b54e238ccfd89df91cabf5255ad8c9b8b26701304fb0bf552f12e4baf435fa5b`; frozen v1.1 is the latest truth file. Raw Google uses `google_truth_v1_1.jsonl`, SHA `f74254c51417084e83aae311a92dedb0e1b80787ba08d003952cce512ffed67f`. The secondary checkout was read only, including imports with bytecode writes disabled. Method: `LQB_PLAN.md`, `SCORE_v2.md`, `greekocr/labelfix/lqb.py` and its exact R2 union scorer. sf6 labels come from the full ENSEMBLE_AB release, verified against L1R3 receipts, extending SX1b coverage to the new truth IDs.

Precision is atomic micro TP/(TP+FP), recall TP/(TP+FN), over exact nonzero head identities. A wrong positive is both FP and FN. Known unmarked heads do not inflate precision. Head error counts and accuracy are retained separately, matching LQB error() on every scored item. HOLD proposals are never scored or treated as correct; uncovered truth is reported. All model comparisons use the same in-sample exclusion mask; pair deltas use only common measured truth items.

The guard excludes `SF7`/`quote_alias` plus inherited frozen gate/reader tags (`sf6_release`, `sf6_gate`, `S6`, `R1-A`). It additionally excludes substitution60: the binding preregistration explicitly used that owner review, although its used_by metadata is empty. The metadata-only SF7 sensitivity is recorded separately in JSON. Audit100 remains in-sample, never a choice credit.

The selected population overlaps 24215 marks truth items on 547 lines. After the common guard, the choice truth frame has 21920 items on 393 lines, but A/B released coverage is only 604/564 heads on 20/19 lines. Only two corrected DEV lines contribute; the rest are unchanged labels. There are no tier B or C marks rows. All-tiers therefore equals tier A/B. **This overlap is too small to establish a meaningful A/B precision difference or population improvement. The fixed rule still applies.**

| Version | Tier | Heads | Lines | TP | FP | FN | Precision | Recall | Errors |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| google | tier_A | 21892 | 391 | 1195 | 50 | 56 | 95.983936% | 95.523581% | 73 |
| sf6 | tier_A | 612 | 20 | 38 | 1 | 0 | 97.435897% | 100.000000% | 1 |
| A | tier_A | 604 | 20 | 38 | 0 | 0 | 100.000000% | 100.000000% | 0 |
| B | tier_A | 564 | 19 | 34 | 0 | 0 | 100.000000% | 100.000000% | 0 |
| google | tier_B | 0 | 0 | 0 | 0 | 0 | not measured | not measured | 0 |
| sf6 | tier_B | 0 | 0 | 0 | 0 | 0 | not measured | not measured | 0 |
| A | tier_B | 0 | 0 | 0 | 0 | 0 | not measured | not measured | 0 |
| B | tier_B | 0 | 0 | 0 | 0 | 0 | not measured | not measured | 0 |
| google | tier_C | 0 | 0 | 0 | 0 | 0 | not measured | not measured | 0 |
| sf6 | tier_C | 0 | 0 | 0 | 0 | 0 | not measured | not measured | 0 |
| A | tier_C | 0 | 0 | 0 | 0 | 0 | not measured | not measured | 0 |
| B | tier_C | 0 | 0 | 0 | 0 | 0 | not measured | not measured | 0 |
| google | tier_AB | 21892 | 391 | 1195 | 50 | 56 | 95.983936% | 95.523581% | 73 |
| sf6 | tier_AB | 612 | 20 | 38 | 1 | 0 | 97.435897% | 100.000000% | 1 |
| A | tier_AB | 604 | 20 | 38 | 0 | 0 | 100.000000% | 100.000000% | 0 |
| B | tier_AB | 564 | 19 | 34 | 0 | 0 | 100.000000% | 100.000000% | 0 |
| google | all_tiers | 21892 | 391 | 1195 | 50 | 56 | 95.983936% | 95.523581% | 73 |
| sf6 | all_tiers | 612 | 20 | 38 | 1 | 0 | 97.435897% | 100.000000% | 1 |
| A | all_tiers | 604 | 20 | 38 | 0 | 0 | 100.000000% | 100.000000% | 0 |
| B | all_tiers | 564 | 19 | 34 | 0 | 0 | 100.000000% | 100.000000% | 0 |

Individual Google scores cover a larger truth frame; compare paired rows for a matched-denominator result. Bootstrap: 4,000 percentile replicates, seed 20261017, whole documents resampled with the same pairs. The secondary weighted DEV ledger uses saved card weights unchanged and resamples documents independently within wave, following SCORE_v2. Both unweighted sample results and weighted covered-subset results are in JSON; neither estimates full-DEV release performance.

| Pair | Common heads/lines | Precision delta | 95% cluster CI | Recall delta | 95% cluster CI |
|---|---:|---:|---|---:|---|
| google→sf6 | 612/20 | -2.564103% | [-9.090909%, 0.000000%] | 2.631579% | [0.000000%, 8.337766%] |
| google→A | 604/20 | 2.702703% | [0.000000%, 10.000000%] | 5.263158% | [0.000000%, 13.890504%] |
| google→B | 564/19 | 2.941176% | [0.000000%, 11.538462%] | 2.941176% | [0.000000%, 11.538462%] |
| sf6→A | 576/19 | 0.000000% | [0.000000%, 0.000000%] | 0.000000% | [0.000000%, 0.000000%] |
| sf6→B | 536/18 | 0.000000% | [0.000000%, 0.000000%] | 0.000000% | [0.000000%, 0.000000%] |
| A→B | 564/19 | 0.000000% | [0.000000%, 0.000000%] | 0.000000% | [0.000000%, 0.000000%] |

Deltas above are percentage-point differences (second minus first). Zero A/B delta with a degenerate interval describes identical labels on this tiny overlap; it does not prove general equivalence. All per-head counts, individual intervals, paired head-error intervals, guard sensitivity and weighted numerators/denominators are in `artifacts/sf7_rc1/lqb_scores.json`.

The strict four-way common panel is only 536 heads / 18 lines, all unchanged: all four versions score 100% precision and recall there. It contains no jointly covered corrected lines, so it cannot measure correction gains. Version-native precision values have different denominators and must not be interpreted as a paired improvement.

## Exact-import candidate and audit frame

Raw parent: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl`, SHA `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3`. This is the exact `label` field designated `google_raw_v2_import`, traced through the Cyrillic report `greek-ocr-toolkit-secondary/docs/labelfix/secondary/RU3TD_REPORT.md` and the sourcing coordinator’s `greek-page-ocr-wave1c/out/e4/wave1c_reg2/HANDOFF.md`/derivation receipts.

`release_edits_only_A.jsonl`: **605 rows / 665 edits**, SHA `1e3ac3344d0054d8e7639325afdf13826181e6eec10983b7e162b9648c5faf5a`. Status: **candidate_pre_audit**. Parent: `google_raw_v2_import`. Every edit records slot, kind, head, rule, signals, variant, policy digest and source job. Exact UTF-8 byte patches and their inverse reconstruct output and parent; every unedited byte remains identical. Mark-bearing letter clusters agree with the chosen release. Every output ID is selected and every output text differs from raw. The 81 formatting-only corrected rows are omitted.

The blind frame contains 100 exact line IDs, uniformly drawn without replacement with seed 20261017 from 515 eligible corrected candidate lines. Every line in either truth v1 or v1.1 and every historical audit100 ID (including the unreadable row) is excluded. The frame carries anonymous audit IDs and crop references, with no labels, candidate identities, mark decisions or truth. Reader packs remain unbuilt. Frame SHA: `66e54b65fe4adbba0ccc786f52a90cafdc119d658c6b5857ff30f793c3dea13e`.

Receipts: `artifacts/sf7_rc1/output_3687228/READBACK_RECEIPT.json`, `artifacts/sf7_rc1/RELEASE_RECEIPT.json`; full breakdown: `artifacts/sf7_rc1/release_summary.json`. Reproduce offline after readback with `build_rb7.py`, `../greek-ocr-toolkit/.venv/bin/python -B artifacts/sf7_rc1/score_rb7.py`, `convert_rb7.py`, and `report_rb7.py` from that artifact directory.

**ASTRA-CENSUS05R — checkpoint 2 / P4 results certification, 20 October 2026**

The census generation passes the integrity and protection checks below. **The downstream gate is NOT CERTIFIED: two HIGH findings prevent the planned benchmark draw and therefore release-v3 completion under the P6/P8 dependency.** Neither finding calls for changing the verified census dispositions. No BLOCKER was found.

Reviewed repository HEAD `5860bf45fd77bd6e07035ab3c712c43662e9aaac`, the supplied results brief, the prior package certification, and the live Clariden generation. All remote actions were foreground, read-only `ls` or Python reads/counts/hashes through SSH; SQLite used `mode=ro&immutable=1`. No scheduler jobs were submitted; no remote writes, source fixes, commits, or publication occurred. New artifacts are confined to this scratch directory.


**H1 — HIGH: the frozen split and edition cap cannot supply the required benchmark**

Split2 has **148 TEST editions (99 forced) and 52 DEV editions**. All 99 forced editions carry v2/locked-evaluation leakage witnesses and the draw correctly excludes them, leaving at most **49 TEST editions**. The global four-lines-per-edition cap therefore permits at most **196 test / 208 dev** candidates, before admission, class availability, series caps or overdraw. Even retaining all forced editions would permit only 592 test rows. This is far below the night plan’s 2,400/600.

The implemented 16 class quotas actually sum to **2,460/615**, and their 20% overdraw to **2,952/738**, whereas P6 budgets 3,600 total checks. These inconsistencies were logged by BENCH02D; the completed census cannot resolve them.

The fresh pool has **4,929 unforced TEST admissions and 3,364 DEV admissions**, across all 49/52 eligible editions. Neither side supplies a historical-Russian or polytonic-dictionary/journal primary class; the available modern-Cyrillic language is Serbian only. Thus relaxing the edition cap alone would still not fill the stated class/language quotas. The **31,337** admitted rows in the 99 forced TEST editions remain excluded.

Required resolution: record an authorized feasible benchmark design and input/split revision, or an explicitly reduced target, before drawing/sealing it. Preserve v2/locked-edition exclusions; do not silently relax caps or fill one class with another. This review does not authorize a redesign. Sources: [docs/records/harvest/collect_v3_admission/split2/SPLIT2.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-results/docs/records/harvest/collect_v3_admission/split2/SPLIT2.md:37), [docs/records/harvest/collect_v3_admission/bench02/bench02_draw.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-results/docs/records/harvest/collect_v3_admission/bench02/bench02_draw.py:21), [docs/records/harvest/collect_v3_admission/bench02/bench02_draw.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-results/docs/records/harvest/collect_v3_admission/bench02/bench02_draw.py:294).


**H2 — HIGH: the benchmark extractor does not map the completed census’s cell evidence**

The current `slim()`/`tag()` consumer requires `cell_flag` and `A`. They are absent in this export, so numeric-cell and short-line quota tags cannot be populated. A live admitted TEST witness is `bsb_poly1850--0ab5fcea9a6fd52e--s000-l0002`, final text `693`, crop bbox `[1530,166,1610,200]`: original dimensions 80×34, aspect **2.3529411764705883**, but both required fields are absent. [Exact live witness](benchmark_cell_witness.json).

The executed consumer reports **0 numeric-cell positives and 0 short-line positives** across all 39,630 admitted W1/W2 TEST/DEV rows. The numeric-cell tag is unavailable on 6,484 numeric-grammar rows (5,455 forced TEST, 627 unforced TEST, 402 DEV); short is unavailable on every row.

Fix the consumer mapping from the bound original crop dimensions to the programme’s explicit aspect/cell contract, then recount all class supply. **Do not alias `diagnostics.is_cell` or `box_aspect_ratio` blindly:** the former is an older numeric-and-small-image diagnostic (≤200×40 px, ≤10 visible characters); the latter measures the ink box, not the crop. They are not the gate’s rotation-free aspect≤6 definition. The export retains enough original dimensions to resolve this without a new census. Degraded/letter-spaced/punctuation-heavy availability and missing language subgroups also need explicit reporting, not inferred positive tags.

Sources: [docs/records/harvest/collect_v3_admission/bench02/bench02_draw.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-results/docs/records/harvest/collect_v3_admission/bench02/bench02_draw.py:74), [docs/records/harvest/collect_v3_admission/bench02/bench02_draw.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-results/docs/records/harvest/collect_v3_admission/bench02/bench02_draw.py:138), [greekocr/harvest/numeric_cells.py](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-results/greekocr/harvest/numeric_cells.py:71). The class tables below execute the current consumer’s actual `slim` twice and `tag` function bodies against each admitted W1/W2 evaluation row; no draw or write function was invoked.


**Publication identity and independent integrity**

| Artifact | Identity |
|---|---|
| Attempt | /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/attempts/full-split-001 |
| Generation | g1-6283e1bcdf124516b599f8028ad910be |
| CURRENT status | completed |
| CURRENT SHA256 | 5ee1c70e980ce62b5b0d10d62eeb61486ac1abf1ead354ed6d95707501b32f39 |
| Summary SHA256 | 096b18a885f1d6bdced71a9f42e0eeee3cc2b8f61d0ce0eacb26abacbe1402be |
| Run binding SHA256 | 392a987c596c6a163e9f77ce6e6d0bb849becc32b7236d816ce420afc23f2fb6 |
| Saved readout SHA256 | 24e88ff201acd134052ce33f3a96cd80b6dc93573438170cf6d12a7358fe53e0 |
| Baseline summary SHA256 | b187a2e7a0e218b433aa28dbc96d31f0c8f7e7e373b35027ba366b0467894fe3 |
| Split2 compressed SHA256 | 7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82 |

The live ledger binding rehashes exactly to CURRENT and the summary; its configuration equals `inputs/config.json`. Inventory, rows, dedup and export phases are committed. Every original parent hash and row count was checked, every decision identity was matched against the original parents, all eight JSONL exports were hashed while being counted, and the admission/train/evaluation decision bindings, routes, reasons, final labels and edits were cross-checked. CURRENT remained byte-identical across the scan. The separate live SQL aggregation matches all **1,423** summary strata.

| Check | Result |
|---|---|
| Input / decision / admission rows | 592,466 |
| Training export | 364,871 |
| Evaluation rows | 124,628 |
| Missing decisions | 0 |
| Missing admission records | 0 |
| Missing eligible training rows | 0 |
| Missing evaluation rows | 0 |
| Stream audit violations | 0 |
| Saved readout invariants | 15/15 PASS |
| Current unchanged | yes |

[Independent stream audit](independent_audit.json), [read-only SQL / finite-panel / numeric-ledger audit](targeted_audit.json), [captured published readout and samples](remote_metadata.json), [ancillary hashes](ancillary_hashes.json), [ledger and manifest hashes](ledger_manifest_hashes.json).


**Saved readout invariants and fresh reconciliation**

| Invariant | Status | Problems |
|---|---|---|
| admitted_train_equals_eligible | PASS | 0 |
| admitted_train_violations | PASS | 0 |
| bound_inventory_counts | PASS | 0 |
| dispositions_sum | PASS | 0 |
| duplicates | PASS | 0 |
| expect_rows | PASS | 0 |
| gate_route_violations | PASS | 0 |
| gate_segmentation_violations | PASS | 0 |
| heldout_leaks | PASS | 0 |
| missing_rows | PASS | 0 |
| no_reason | PASS | 0 |
| pipeline_version_mismatch | PASS | 0 |
| summary_by_stratum | PASS | 0 |
| summary_dispositions | PASS | 0 |
| unexpected_rows | PASS | 0 |

The independent counters, identity joins, all 13 readout file hashes, SQL strata, split receipt, ledger binding and publication checks are reconciled separately in [reconciliation.json](reconciliation.json).


**Generation output hashes**

| Output | Rows | Bytes | SHA256 |
|---|---|---|---|
| admission_records.jsonl | 592,466 | 10,412,166,460 | 0acfb1c9b6b5a7094313d362925bdded6803e7cd5d12a72d05ccbb1d2a8caeae |
| admitted_train.jsonl | 364,871 | 7,870,677,512 | fe955d00af930b90b1d963a0454a4f4cba26de8fd24332ecc6873fd99f42c4f3 |
| decisions.jsonl | 592,466 | 10,156,784,052 | 903fd9ed755112a77b13531493dedf66c6e5a2b77eff7ba0fcb32f135cdbc509 |
| evaluation_diagnostics.jsonl | 124,628 | 2,487,364,889 | bbb8d1700353ae1da0b661880fb9a4197396134445eca25555b24d60fc6f8c05 |
| pending_content_repair.jsonl | 28,572 | 194,484,402 | 469fe221bcbb8542e875b26f49e4baf4f374c580727b467ee90bda9c6df9ca78 |
| pending_cyrillic.jsonl | 8,478 | 26,075,598 | 5ae577ddab29a8b3dce61b77952f5545aea4ca9cf3ccfb22e5b08e40e492b2d3 |
| pending_numerics.jsonl | 36,503 | 239,412,167 | 75597ca992d095cf5ccde3f63e420716adc08efcc11d5d2a28a32680994d942b |
| pending_polytonic.jsonl | 0 | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |



**Held-out protection — recounted from admitted_train**

| Protection / check | Count |
|---|---|
| configured_crop_hashes | 9,119 |
| configured_editions | 61 |
| configured_only_crops | 6,904 |
| observed_eval_crops | 124,425 |
| observed_eval_editions | 320 |
| split2_heldout_editions | 200 |
| configured_crop_leak | 0 |
| observed_eval_crop_leak | 0 |
| configured_edition_leak | 0 |
| split2_edition_leak | 0 |
| observed_eval_edition_leak | 0 |
| duplicate_train_crop | 0 |

All admitted train rows were checked against the **9,119 configured crop hashes**, the split2 TEST/DEV editions, the **61 configured editions**, and observed evaluation crops/editions. Config-only hashes were included; no protection was inferred merely from a passing producer receipt. The configured and observed crop sets overlap, so their totals are not additive.


**Dispositions and census_03 baseline delta**

| Parent | Rows | 05 ADMIT | 05 HOLD | 05 DROP | 03 ADMIT | 03 HOLD | 03 DROP | Δ ADMIT | Δ HOLD | Δ DROP |
|---|---|---|---|---|---|---|---|---|---|---|
| v2 train | 214,436 | 196,234 | 8,922 | 9,280 | 65,900 | 145,131 | 3,405 | 130,334 | -136,209 | 5,875 |
| v2 dev | 13,522 | 13,000 | 229 | 293 | 3,984 | 9,374 | 164 | 9,016 | -9,145 | 129 |
| v2 test | 44,029 | 40,490 | 1,904 | 1,635 | 10,314 | 33,311 | 404 | 30,176 | -31,407 | 1,231 |
| W1 | 101,098 | 68,779 | 19,324 | 12,995 | 0 | 96,953 | 4,145 | 68,779 | -77,629 | 8,850 |
| W2 | 219,381 | 139,488 | 47,661 | 32,232 | 0 | 208,637 | 10,744 | 139,488 | -160,976 | 21,488 |

All-parent totals: **457,991 ADMIT / 78,040 HOLD / 56,435 DROP**. This includes evaluation admissions; it is not the training-release size. UNPROCESSED and INFRA_ERROR are zero. The baseline is the live frozen census_03 summary with SHA256 `b187a2e7a0e218b433aa28dbc96d31f0c8f7e7e373b35027ba366b0467894fe3`. Its per-parent deltas were recalculated independently.

| Disposition | First deciding reason | Rows |
|---|---|---|
| DROP | codec_unencodable | 4,578 |
| DROP | duplicate_training_observation | 279 |
| DROP | heldout_crop_identity | 1,780 |
| DROP | low_confidence | 13,709 |
| DROP | mixed_script_word | 1,720 |
| DROP | nonletter_fraction | 4,714 |
| DROP | numeric_shape | 2,451 |
| DROP | segmentation | 13,306 |
| DROP | short_line | 3,202 |
| DROP | single_character_cell | 10,696 |
| HOLD | content_repair_unresolved | 27,976 |
| HOLD | correction_unresolved | 44,940 |
| HOLD | same_crop_conflicting_labels | 396 |
| HOLD | segmentation | 2,462 |
| HOLD | unexpected_script | 2,266 |

The following are overlapping reason occurrences; they must not be summed as unique rejected rows.

| Disposition | Carried reason | Occurrences |
|---|---|---|
| DROP | codec_unencodable | 4,617 |
| DROP | duplicate_training_observation | 279 |
| DROP | heldout_crop_identity | 1,780 |
| DROP | low_confidence | 14,397 |
| DROP | mixed_script_word | 1,720 |
| DROP | nonletter_fraction | 4,714 |
| DROP | numeric_shape | 2,451 |
| DROP | segmentation | 13,306 |
| DROP | short_line | 3,202 |
| DROP | single_character_cell | 10,696 |
| DROP | unexpected_script | 385 |
| HOLD | content_repair_unresolved | 27,976 |
| HOLD | correction_unresolved | 44,981 |
| HOLD | same_crop_conflicting_labels | 396 |
| HOLD | segmentation | 2,462 |
| HOLD | unexpected_script | 2,266 |



**Reason deltas and interpretation**

| Overlapping reason | census_03 | census_05 | Delta |
|---|---|---|---|
| codec_unencodable | 593 | 4,617 | 4,024 |
| content_repair_unresolved | 26,475 | 27,976 | 1,501 |
| correction_unresolved | 172,823 | 44,981 | -127,842 |
| duplicate_training_observation | 252 | 279 | 27 |
| heldout_crop_identity | 980 | 1,780 | 800 |
| low_confidence | 0 | 14,397 | 14,397 |
| mixed_script_word | 0 | 1,720 | 1,720 |
| nonletter_fraction | 0 | 4,714 | 4,714 |
| numeric_shape | 0 | 2,451 | 2,451 |
| same_crop_conflicting_labels | 2 | 396 | 394 |
| segmentation | 168,967 | 15,768 | -153,199 |
| short_line | 1 | 3,202 | 3,201 |
| single_character_cell | 0 | 10,696 | 10,696 |
| split_or_edition_identity_unresolved | 142,959 | 0 | -142,959 |
| unexpected_script | 0 | 2,651 | 2,651 |

The increase from 80,198 to 457,991 all-split admissions combines changed segmentation, the early content gate/final rules, finalized W1/W2 splits and explicit polytonic exclusion. It is not an isolated segmentation accuracy gain. Split-only HOLDs fall 142,959→0; correction-unresolved occurrences fall 172,823→44,981; segmentation rejection/uncertainty occurrences fall 168,967→15,768. Numeric ledgers are unchanged in status, yet numerics unresolved routes grow 27,942→36,503 because different rows reach correction routing. These denominators must remain distinct.


**Frozen tool expectations versus the completed population**

Gate 0.3 excludes **17,888/592,466 (3.019%)** before native work: **15,622 DROP / 2,266 HOLD**. The carried reasons are mixed-script word 1,720; unexpected script 2,651 (385 overlap mixed-script drops); short line 3,202; single-character cell 10,696; early numeric shape 4. No gate-excluded row has native segmentation or a subsequently run route.

Frozen panel exclusion shares were 13/150 (8.667%), 69/888 (7.770%), 37/250 cells (14.8%), and 133/417 typology (31.894%). These selected panels are not representative prevalence estimates, so their larger shares do not imply a census defect. The actual 150-panel join has **12** early exclusions, not 13: `252fd568-p000234-l0033` now resolves to the frozen Bulgarian book declaration allowing Cyrillic, whereas the gate re-report used Latin/Greek source fallback. It still HOLDs for unresolved Cyrillic evidence. This is a documented expectation-resolution difference, not an altered gate rule. [Exact witness](gate_witness.jsonl).

| Panel | Input matched | Excluded before native | Native verdict+reason exact | Native differences |
|---|---|---|---|---|
| 150 | 150 | 12 | 138 | 0 |
| 888 | 888 | 69 | 819 | 0 |

The receipt-pinned SEG10 replay was reconstructed from the two gzip chunks and its SHA256 checked (`6e9ab21d…`). Every matching input crop and raw-text hash agrees. The finite-set s5 scores remain 150 FP/FN/UNC **4/19/0**, after the original gate exclusions **2/18/0**; 888 rated agreement **117/135**, after original gate exclusions **82/91**. The current 138-row live panel is not the original 137-row gate-filtered panel. The live calibration exclusion count remains 69, but its mask differs on four rows: two ELSTAT rows reach final numeric-shape rejection instead of early short-line rejection, while one Serbian and one Russian row now HOLD early for unexpected Latin under their bound declarations. Neither historical gate-filtered accuracy score is asserted for these changed masks. [All five 150/888 mask differences](gate_mask_differences.jsonl). A further cells-panel Bulgarian row changes from unexpected-script HOLD to Cyrillic-evidence HOLD; its witness is retained in the stream audit. These are source-policy-only versus bound-metadata differences; no native verdict/reason difference was found. Fitted finite-panel results do not establish population accuracy.

| Native verdict | Rows |
|---|---|
| DROP | 13,306 |
| KEEP | 558,810 |
| UNCERTAIN | 2,462 |

Native ran on 574,578 rows. The 13,306 native drops comprise second complete line 8,521; too many whole neighbour words 2,680; too little output 200; too much output 1,249; excessive padding 656. Uncertain: no main row 2,446; unavailable box 16. No unexplained disposition mass contradicts the frozen evaluations.


**Correction scope, ledgers and pending work**

Polytonic is deliberately out of scope: **258,629** routed records say `not_applied_out_of_scope`, distributed **247,883 ADMIT / 6,464 DROP / 4,282 HOLD**. The latter HOLDs arise from other required checks; there is no unresolved polytonic route and no pending polytonic row. These are retained raw polytonic labels, not corrected or verified-no-change SF7 labels.

The five numerics 0.3 ledgers contain **556,245** records. The independent old/new row comparison finds **zero status, edit, binding or raw-text-hash changes**. Their 47 applied records are all W1 TEST in this census. Standing Cyrillic ledgers contain **19,898** records and match their configured hashes; they were not regenerated.

| Tool | Parent | Status | Version | Records |
|---|---|---|---|---|
| cyrillic | W1 | verified_no_change | 0.3 | 4,164 |
| cyrillic | W2 | verified_no_change | 0.3 | 6,854 |
| cyrillic | v2 dev | applied | 0.3 | 64 |
| cyrillic | v2 dev | required_evidence_unresolved | 0.3 | 14 |
| cyrillic | v2 dev | verified_no_change | 0.3 | 323 |
| cyrillic | v2 test | applied | 0.3 | 290 |
| cyrillic | v2 test | required_evidence_unresolved | 0.3 | 180 |
| cyrillic | v2 test | verified_no_change | 0.3 | 1,780 |
| cyrillic | v2 train | applied | 0.3 | 424 |
| cyrillic | v2 train | required_evidence_unresolved | 0.3 | 256 |
| cyrillic | v2 train | verified_no_change | 0.3 | 5,549 |
| numerics | W1 | applied | 0.3 | 47 |
| numerics | W1 | required_evidence_unresolved | 0.3 | 582 |
| numerics | W1 | verified_no_change | 0.3 | 93,369 |
| numerics | W2 | verified_no_change | 0.3 | 190,632 |
| numerics | v2 dev | verified_no_change | 0.3 | 13,413 |
| numerics | v2 test | verified_no_change | 0.3 | 43,766 |
| numerics | v2 train | required_evidence_unresolved | 0.3 | 1,919 |
| numerics | v2 train | verified_no_change | 0.3 | 212,517 |

| Pending tool | Rows |
|---|---|
| polytonic | 0 |
| cyrillic | 8,478 |
| numerics | 36,503 |
| content_repair | 28,572 |

Pending queues were checked by identity against unresolved decision routes; no missing or unexpected queue members were found. Large remaining queues are outstanding evidence obligations, not silent admissions or changed numeric-ledger statuses. [Route/status counts](audit_tables/routes.tsv), [parent route/status/disposition counts](audit_tables/routes_parent.tsv), [unresolved witnesses](unresolved_witnesses.jsonl).


**Training-release implications**

| Parent | All input rows | Assigned train | Admitted train | % assigned train | % all parent rows | census_03 train admit |
|---|---|---|---|---|---|---|
| v2 train | 214,436 | 214,436 | 196,234 | 91.5117% | 91.5117% | 65,900 |
| W1 | 101,098 | 71,796 | 50,736 | 70.6669% | 50.1850% | 0 |
| W2 | 219,381 | 181,606 | 117,901 | 64.9213% | 53.7426% | 0 |

The train export contains **364,871** rows: v2 train **196,234**, W1 **50,736**, W2 **117,901**. W1/W2 contribute **168,637** train rows, versus **0** in census_03 when their split was unassigned; their 208,267 all-split admissions must not be substituted for that training contribution. Final release v3 and crop upload receipts still belong to P8. The release consumer must use the exported final_text and its decision binding; inherited label/text and older admission flags remain in the canonical payload and are not substitutes for the new final label. **193,693 train rows explicitly retain unapplied polytonic corrections.**

| Edits | Final text versus raw | Train rows |
|---|---|---|
| edits | changed | 167 |
| no_edits | raw_equal | 364,704 |

| Parent | Edits | Final text versus raw | Rows |
|---|---|---|---|
| W1 | no_edits | raw_equal | 50,736 |
| W2 | no_edits | raw_equal | 117,901 |
| v2 train | edits | changed | 167 |
| v2 train | no_edits | raw_equal | 196,067 |

**M1 — MEDIUM, experiment interpretation:** newly admitted W1/W2 training rows have **zero applied corrections**. The 167 edited training rows are standing RU1 corrections in v2 train; N1 contributes zero training edits. The add/add_corr design must record where its actual label contrast comes from, and must not claim corrections to the added W1/W2 tranche. SF7 remains unapplied.


**Admitted train by source**

| source | Rows |
|---|---|
| anemi_mixed | 14,244 |
| anemi_round1 | 46,172 |
| anemi_round2 | 18,421 |
| archive_AA9613308335D0B014B | 1,459 |
| archive_b24878935 | 20 |
| archive_b28038630 | 9,432 |
| archive_bub_gb_Cmg6AQAAIAAJ | 660 |
| archive_bub_gb_mG0mAQAAIAAJ | 1,113 |
| archive_izvestiianabul25192530bul | 32 |
| archive_izvestiianabulga610193138bulg | 55 |
| archive_izvestiianatsars12192829tsar | 57 |
| archive_izvestiianatsars1516194243tsar | 18 |
| archive_sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930 | 1,509 |
| bsb_poly1850 | 18,327 |
| elstat | 4,403 |
| gazette_modern | 84,078 |
| ia_greek_latin | 7,361 |
| ia_poly1850 | 26,969 |
| kosmopolis | 4,220 |
| lekythos | 10,657 |
| nlg | 9,396 |
| openarchives_Dione | 1,910 |
| openarchives_KEIED | 1,941 |
| openarchives_Pandemos | 2,370 |
| openarchives_anaktisis | 1,961 |
| openarchives_apothesis | 1,580 |
| openarchives_hellanicus | 1,905 |
| openarchives_kallipos | 2,070 |
| openarchives_ktisis | 1,868 |
| openarchives_mixed_Dione | 411 |
| openarchives_mixed_KEIED | 404 |
| openarchives_mixed_Pandemos | 58 |
| openarchives_mixed_anaktisis | 407 |
| openarchives_mixed_apothesis | 584 |
| openarchives_mixed_hellanicus | 273 |
| openarchives_mixed_kallipos | 23 |
| openarchives_mixed_ktisis | 527 |
| openarchives_mixed_nemertes | 41 |
| openarchives_mixed_ntua | 30 |
| openarchives_nemertes | 1,482 |
| openarchives_ntua | 1,342 |
| parliament_proceedings_1975_2000 | 57,251 |
| serbia | 3,226 |
| vouli_parliament_1850s | 24,604 |



**Admitted train by export primary_class**

| export primary_class | Rows |
|---|---|
| None | 196,234 |
| cyrillic | 2,974 |
| dialogue_fiction | 8,121 |
| greek_mono | 1,472 |
| greek_poly | 1,775 |
| headings_caps | 14,925 |
| latin | 20,270 |
| leaders_indices | 21 |
| mixed_greek_latin | 8,401 |
| modern_scanned | 55,013 |
| nonletter | 11 |
| numerics_tables | 14,803 |
| poly1850 | 25,047 |
| poly1900 | 15,804 |



**Admitted train by canonical declared role**

| Declared role | Rows |
|---|---|
| cyrillic | 2,974 |
| dialogue_fiction | 8,114 |
| greek_mono | 1,472 |
| greek_poly | 1,775 |
| headings_caps | 14,889 |
| latin | 19,611 |
| leaders_indices | 21 |
| mixed_greek_latin | 8,387 |
| modern_scanned | 54,562 |
| nonletter | 11 |
| numerics_tables | 16,143 |
| poly1850 | 25,047 |
| poly1900 | 15,631 |
| prose | 196,234 |

The primary_class field and canonical content_role are kept distinct. A missing primary_class is not a missing role: the original v2 rows carry the canonical prose role.


**Benchmark edition supply and export class tags**

| Split | Forced status | Admitted rows | Editions with admissions | Upper bound at cap 4 |
|---|---|---|---|---|
| dev | unforced | 3,364 | 52 | 208 |
| test | forced | 31,337 | 99 | 396 |
| test | unforced | 4,929 | 49 | 196 |

Forced TEST admissions are counted here as requested; they remain excluded from the new benchmark by its v2/locked-set rule. TEST+DEV W1/W2 admissions are 39,630; all v2 diagnostics are retained separately.

| Current extractor primary class | TEST forced | TEST unforced | DEV |
|---|---|---|---|
| caps_headings | 800 | 311 | 439 |
| curved_skewed | 1,783 | 141 | 146 |
| font_extremes | 6,238 | 236 | 391 |
| greek_latin | 1,899 | 23 | 22 |
| historical_russian | 491 | 0 | 0 |
| latin | 3,860 | 6 | 6 |
| leaders_dashes | 37 | 4 | 1 |
| long | 4,311 | 85 | 166 |
| modern_cyrillic | 46 | 180 | 139 |
| monotonic | 2,193 | 608 | 648 |
| poly_dictionary_journal | 5,724 | 0 | 0 |
| polytonic | 1,349 | 2,203 | 454 |
| unclassified | 2,278 | 336 | 179 |
| vertical_turned | 328 | 796 | 773 |

These are **pre-draw** primary-class supplies, not realized candidates. [All tag states, including unavailable](audit_tables/benchmark_tags.tsv), [split/forced/source/collector-class supply](audit_tables/benchmark_source_class.tsv). The consumer’s primary class differs from the collector class because its fixed precedence assigns physical/specialized classes before script fallbacks.

| Tag | TEST forced true / unavailable | TEST unforced true / unavailable | DEV true / unavailable |
|---|---|---|---|
| monotonic | 4474 / 0 | 1723 / 0 | 2079 / 0 |
| polytonic | 10122 / 0 | 2343 / 0 | 681 / 0 |
| poly_dictionary_journal | 8359 / 0 | 0 / 0 | 0 / 0 |
| latin | 6533 / 0 | 13 / 0 | 11 / 0 |
| greek_latin | 2948 / 0 | 30 / 0 | 37 / 0 |
| historical_russian | 1427 / 0 | 0 / 0 | 0 / 0 |
| modern_cyrillic | 124 / 0 | 191 / 0 | 153 / 0 |
| numeric_cells | 0 / 5455 | 0 / 627 | 0 / 402 |
| short | 0 / 31337 | 0 / 4929 | 0 / 3364 |
| long | 4553 / 0 | 144 / 0 | 224 / 0 |
| vertical_turned | 328 / 0 | 796 / 0 | 773 / 0 |
| caps_headings | 1035 / 0 | 544 / 0 | 677 / 0 |
| leaders_dashes | 69 / 0 | 4 / 0 | 7 / 0 |
| font_extremes | 6308 / 0 | 308 / 0 | 548 / 0 |
| degraded | 0 / 31337 | 0 / 4929 | 0 / 3364 |
| curved_skewed | 3100 / 0 | 234 / 0 | 259 / 0 |

The 99 forced editions are not an independent unexposed benchmark pool. Existing held-out protection remains intact; changing the benchmark design must preserve that separation.


**All-population dispositions by source**

| Source | ADMIT | HOLD | DROP |
|---|---|---|---|
| anemi_mixed | 16,733 | 145 | 382 |
| anemi_round1 | 57,329 | 362 | 522 |
| anemi_round2 | 22,698 | 218 | 212 |
| archive_AA9613308335D0B014B | 1,459 | 253 | 0 |
| archive_b24878935 | 20 | 1,173 | 0 |
| archive_b28038630 | 9,432 | 229 | 4 |
| archive_b29337124 | 95 | 0 | 124 |
| archive_bub_gb_Cmg6AQAAIAAJ | 660 | 34 | 837 |
| archive_bub_gb_mG0mAQAAIAAJ | 1,113 | 445 | 0 |
| archive_izvestiianabul25192530bul | 32 | 1,406 | 0 |
| archive_izvestiianabulga610193138bulg | 55 | 1,170 | 0 |
| archive_izvestiianatsars1112193839tsar | 8 | 201 | 0 |
| archive_izvestiianatsars12192829tsar | 57 | 726 | 0 |
| archive_izvestiianatsars1516194243tsar | 18 | 990 | 0 |
| archive_izvestiianatsars910193637tsar | 22 | 427 | 0 |
| archive_sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930 | 1,509 | 63 | 3 |
| bsb_poly1850 | 25,314 | 5,346 | 2,430 |
| elstat | 8,659 | 6,778 | 4,442 |
| gazette_modern | 93,720 | 30,949 | 23,878 |
| ia_greek_latin | 8,871 | 902 | 1,982 |
| ia_poly1850 | 38,035 | 20,736 | 5,705 |
| ia_russian | 1,590 | 1,107 | 266 |
| kosmopolis | 4,876 | 74 | 406 |
| lekythos | 12,366 | 138 | 903 |
| nlg | 10,994 | 178 | 937 |
| openarchives_Dione | 2,665 | 80 | 83 |
| openarchives_IKEE_AUT | 250 | 10 | 0 |
| openarchives_KEIED | 2,146 | 28 | 83 |
| openarchives_Pandemos | 2,690 | 40 | 36 |
| openarchives_anaktisis | 2,583 | 26 | 120 |
| openarchives_apothesis | 2,119 | 39 | 49 |
| openarchives_hellanicus | 2,684 | 60 | 117 |
| openarchives_kallipos | 2,818 | 30 | 88 |
| openarchives_ktisis | 2,444 | 26 | 150 |
| openarchives_mixed_Dione | 577 | 54 | 41 |
| openarchives_mixed_KEIED | 465 | 89 | 24 |
| openarchives_mixed_Pandemos | 58 | 1 | 1 |
| openarchives_mixed_anaktisis | 407 | 23 | 58 |
| openarchives_mixed_apothesis | 584 | 70 | 24 |
| openarchives_mixed_hellanicus | 273 | 53 | 9 |
| openarchives_mixed_kallipos | 200 | 14 | 5 |
| openarchives_mixed_ktisis | 585 | 51 | 27 |
| openarchives_mixed_nemertes | 113 | 6 | 5 |
| openarchives_mixed_ntua | 96 | 1 | 0 |
| openarchives_nemertes | 2,021 | 27 | 108 |
| openarchives_ntua | 1,669 | 32 | 51 |
| parliament_proceedings_1975_2000 | 72,120 | 1,367 | 7,694 |
| serbia | 3,842 | 777 | 4,278 |
| vouli_parliament_1850s | 27,872 | 112 | 275 |
| wikisource_el | 8,866 | 34 | 75 |
| wikisource_ru | 2,179 | 940 | 1 |



**All-population dispositions by collector class**

| Collector class | ADMIT | HOLD | DROP |
|---|---|---|---|
| cyrillic | 4,867 | 1,374 | 4,196 |
| dialogue_fiction | 9,342 | 628 | 1,009 |
| greek_mono | 2,026 | 509 | 821 |
| greek_poly | 2,109 | 47 | 298 |
| headings_caps | 17,212 | 1,078 | 5,854 |
| latin | 26,642 | 25,299 | 5,416 |
| leaders_indices | 23 | 4 | 18 |
| mixed_greek_latin | 11,219 | 1,988 | 2,974 |
| modern_scanned | 60,315 | 8,322 | 8,160 |
| nonletter | 14 | 3 | 5,132 |
| numerics_tables | 21,525 | 26,952 | 7,993 |
| poly1850 | 34,055 | 542 | 1,757 |
| poly1900 | 18,918 | 239 | 1,599 |
| prose | 249,724 | 11,055 | 11,208 |



**Baseline delta by source**

| Source | 03 ADMIT | 03 HOLD | 03 DROP | 05 ADMIT | 05 HOLD | 05 DROP | Δ ADMIT | Δ HOLD | Δ DROP |
|---|---|---|---|---|---|---|---|---|---|
| anemi_mixed | 3,273 | 13,726 | 261 | 16,733 | 145 | 382 | 13,460 | -13,581 | 121 |
| anemi_round1 | 7,941 | 49,558 | 714 | 57,329 | 362 | 522 | 49,388 | -49,196 | -192 |
| anemi_round2 | 4,244 | 18,599 | 285 | 22,698 | 218 | 212 | 18,454 | -18,381 | -73 |
| archive_AA9613308335D0B014B | 1,384 | 321 | 7 | 1,459 | 253 | 0 | 75 | -68 | -7 |
| archive_b24878935 | 20 | 1,173 | 0 | 20 | 1,173 | 0 | 0 | 0 | 0 |
| archive_b28038630 | 3,251 | 6,413 | 1 | 9,432 | 229 | 4 | 6,181 | -6,184 | 3 |
| archive_b29337124 | 72 | 65 | 82 | 95 | 0 | 124 | 23 | -65 | 42 |
| archive_bub_gb_Cmg6AQAAIAAJ | 454 | 563 | 514 | 660 | 34 | 837 | 206 | -529 | 323 |
| archive_bub_gb_mG0mAQAAIAAJ | 1,107 | 450 | 1 | 1,113 | 445 | 0 | 6 | -5 | -1 |
| archive_izvestiianabul25192530bul | 31 | 1,406 | 1 | 32 | 1,406 | 0 | 1 | 0 | -1 |
| archive_izvestiianabulga610193138bulg | 49 | 1,169 | 7 | 55 | 1,170 | 0 | 6 | 1 | -7 |
| archive_izvestiianatsars1112193839tsar | 8 | 201 | 0 | 8 | 201 | 0 | 0 | 0 | 0 |
| archive_izvestiianatsars12192829tsar | 57 | 726 | 0 | 57 | 726 | 0 | 0 | 0 | 0 |
| archive_izvestiianatsars1516194243tsar | 17 | 991 | 0 | 18 | 990 | 0 | 1 | -1 | 0 |
| archive_izvestiianatsars910193637tsar | 21 | 428 | 0 | 22 | 427 | 0 | 1 | -1 | 0 |
| archive_sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930 | 1,333 | 169 | 73 | 1,509 | 63 | 3 | 176 | -106 | -70 |
| bsb_poly1850 | 0 | 32,623 | 467 | 25,314 | 5,346 | 2,430 | 25,314 | -27,277 | 1,963 |
| elstat | 0 | 19,018 | 861 | 8,659 | 6,778 | 4,442 | 8,659 | -12,240 | 3,581 |
| gazette_modern | 0 | 138,387 | 10,160 | 93,720 | 30,949 | 23,878 | 93,720 | -107,438 | 13,718 |
| ia_greek_latin | 0 | 11,354 | 401 | 8,871 | 902 | 1,982 | 8,871 | -10,452 | 1,581 |
| ia_poly1850 | 0 | 62,790 | 1,686 | 38,035 | 20,736 | 5,705 | 38,035 | -42,054 | 4,019 |
| ia_russian | 0 | 2,809 | 154 | 1,590 | 1,107 | 266 | 1,590 | -1,702 | 112 |
| kosmopolis | 0 | 5,175 | 181 | 4,876 | 74 | 406 | 4,876 | -5,101 | 225 |
| lekythos | 0 | 13,065 | 342 | 12,366 | 138 | 903 | 12,366 | -12,927 | 561 |
| nlg | 0 | 11,676 | 433 | 10,994 | 178 | 937 | 10,994 | -11,498 | 504 |
| openarchives_Dione | 2,625 | 88 | 115 | 2,665 | 80 | 83 | 40 | -8 | -32 |
| openarchives_IKEE_AUT | 250 | 10 | 0 | 250 | 10 | 0 | 0 | 0 | 0 |
| openarchives_KEIED | 2,143 | 31 | 83 | 2,146 | 28 | 83 | 3 | -3 | 0 |
| openarchives_Pandemos | 2,525 | 205 | 36 | 2,690 | 40 | 36 | 165 | -165 | 0 |
| openarchives_anaktisis | 2,582 | 25 | 122 | 2,583 | 26 | 120 | 1 | 1 | -2 |
| openarchives_apothesis | 2,112 | 38 | 57 | 2,119 | 39 | 49 | 7 | 1 | -8 |
| openarchives_hellanicus | 2,676 | 61 | 124 | 2,684 | 60 | 117 | 8 | -1 | -7 |
| openarchives_kallipos | 2,779 | 69 | 88 | 2,818 | 30 | 88 | 39 | -39 | 0 |
| openarchives_ktisis | 2,440 | 26 | 154 | 2,444 | 26 | 150 | 4 | 0 | -4 |
| openarchives_mixed_Dione | 571 | 57 | 44 | 577 | 54 | 41 | 6 | -3 | -3 |
| openarchives_mixed_KEIED | 460 | 92 | 26 | 465 | 89 | 24 | 5 | -3 | -2 |
| openarchives_mixed_Pandemos | 46 | 13 | 1 | 58 | 1 | 1 | 12 | -12 | 0 |
| openarchives_mixed_anaktisis | 405 | 24 | 59 | 407 | 23 | 58 | 2 | -1 | -1 |
| openarchives_mixed_apothesis | 580 | 70 | 28 | 584 | 70 | 24 | 4 | 0 | -4 |
| openarchives_mixed_hellanicus | 265 | 48 | 22 | 273 | 53 | 9 | 8 | 5 | -13 |
| openarchives_mixed_kallipos | 200 | 14 | 5 | 200 | 14 | 5 | 0 | 0 | 0 |
| openarchives_mixed_ktisis | 583 | 53 | 27 | 585 | 51 | 27 | 2 | -2 | 0 |
| openarchives_mixed_nemertes | 113 | 6 | 5 | 113 | 6 | 5 | 0 | 0 | 0 |
| openarchives_mixed_ntua | 68 | 29 | 0 | 96 | 1 | 0 | 28 | -28 | 0 |
| openarchives_nemertes | 2,018 | 27 | 111 | 2,021 | 27 | 108 | 3 | 0 | -3 |
| openarchives_ntua | 1,667 | 32 | 53 | 1,669 | 32 | 51 | 2 | 0 | -2 |
| parliament_proceedings_1975_2000 | 25,334 | 55,193 | 654 | 72,120 | 1,367 | 7,694 | 46,786 | -53,826 | 7,040 |
| serbia | 0 | 8,693 | 204 | 3,842 | 777 | 4,278 | 3,842 | -7,916 | 4,074 |
| vouli_parliament_1850s | 2,239 | 25,858 | 162 | 27,872 | 112 | 275 | 25,633 | -25,746 | 113 |
| wikisource_el | 310 | 8,620 | 45 | 8,866 | 34 | 75 | 8,556 | -8,586 | 30 |
| wikisource_ru | 1,945 | 1,169 | 6 | 2,179 | 940 | 1 | 234 | -229 | -5 |



**Baseline delta by declared role**

| Declared role | 03 ADMIT | 03 HOLD | 03 DROP | 05 ADMIT | 05 HOLD | 05 DROP | Δ ADMIT | Δ HOLD | Δ DROP |
|---|---|---|---|---|---|---|---|---|---|
| cyrillic | 0 | 10,319 | 118 | 4,867 | 1,374 | 4,196 | 4,867 | -8,945 | 4,078 |
| dialogue_fiction | 0 | 10,594 | 305 | 9,334 | 627 | 938 | 9,334 | -9,967 | 633 |
| greek_mono | 0 | 3,081 | 275 | 2,026 | 509 | 821 | 2,026 | -2,572 | 546 |
| greek_poly | 0 | 2,432 | 22 | 2,109 | 47 | 298 | 2,109 | -2,385 | 276 |
| headings_caps | 0 | 20,573 | 3,312 | 17,159 | 1,075 | 5,651 | 17,159 | -19,498 | 2,339 |
| latin | 0 | 53,194 | 1,281 | 25,603 | 24,512 | 4,360 | 25,603 | -28,682 | 3,079 |
| leaders_indices | 0 | 44 | 0 | 23 | 4 | 17 | 23 | -40 | 17 |
| mixed_greek_latin | 0 | 15,229 | 267 | 11,192 | 1,945 | 2,359 | 11,192 | -13,284 | 2,092 |
| modern_scanned | 0 | 72,694 | 2,931 | 59,613 | 8,306 | 7,706 | 59,613 | -64,388 | 4,775 |
| nonletter | 0 | 2,559 | 2,431 | 14 | 3 | 4,973 | 14 | -2,556 | 2,542 |
| numerics_tables | 0 | 59,221 | 3,394 | 23,578 | 27,832 | 11,205 | 23,578 | -31,389 | 7,811 |
| poly1850 | 0 | 36,114 | 240 | 34,055 | 542 | 1,757 | 34,055 | -35,572 | 1,517 |
| poly1900 | 0 | 19,536 | 313 | 18,694 | 209 | 946 | 18,694 | -19,327 | 633 |
| prose | 80,198 | 187,816 | 3,973 | 249,724 | 11,055 | 11,208 | 169,526 | -176,761 | 7,235 |



**Validation, limits and complete raw tables**

Fresh pytest from the read-only repository root: **19 passed, 9 skipped, 0 failed in 32.55 s**, with `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`, and `/tmp` basetemp. The nine skips are absent historical fixtures, not passing cases. [Log](pytest.log). The prior package review’s separately supplied fixtures and 28-pass result are historical, not re-claimed as this execution.

**M2 — MEDIUM, qualification limit:** integrity, identical finite replay verdicts and zero leakage do not certify the physical correctness of every admitted crop or label. P6’s last-filter checks remain necessary; no reader or physical requalification ran here. No additional acceptance threshold was introduced.

**L1 — LOW, retained schema caution:** `complete=true` means completed census accounting. HOLD/DROP and outstanding queues remain legitimate. Consume CURRENT, the pinned generation, all invariants and explicit decision/admission fields; inherited raw-row flags in diagnostics/pending files are not final admission authority.

Full parent×source×class×split×disposition counts are in [the independent cross-table](audit_tables/parent_source_class_disposition.tsv); training parent×source×class counts are [here](audit_tables/train_parent_source_class.tsv). All 33 producer tables are separately preserved under [readout_tables](readout_tables/). The independent streams, exact sent scripts, configuration/readout capture, finite references, targeted witnesses, and hash manifest are retained beside this report. The main audit used the original benchmark function bodies; only its unused future-annotations directive was removed for Clariden’s system Python 3.6 compatibility.


VERDICT: NOT CERTIFIED for release v3 and benchmark draw until H1-H2 are resolved; census integrity checks pass | BLOCKERS: 0 | HIGH: 2

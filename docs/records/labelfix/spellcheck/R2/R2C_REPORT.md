# R2C blind grader decks — 17 October 2026

**Prepared: T2 800 + 80 proposed controls; T4 800 + 80 proposed controls. No acquisition shortfalls.**
Lead pixel verification of the 160 proposed controls and the geometry QA strips remains required before readers start. No reader was run; no printed truth or usable supervised targets are claimed yet.

## Reservation and exclusions

169 eligible documents: validation 17, witness 30, calibration 23, supervision 99. Roles were persisted before geometry/mining; the input-hash recheck passed.

source x decade; v2 source = wave:source; sha256("R2:2026-10-17:"+doc) ascending within cells; global rounded 10% validation; 20% of remaining witness (minimum 20); 15% of post-validation calibration; largest remainder per role over remaining cells, fractional ties source/era lexical; rest supervision

Collection-v2 source cells use wave:source and decade; missing years use unknown. Global largest-remainder quotas avoid reserving every singleton cell. C1 selection was absent here; the S8 copy was used after all nine available copies matched SHA-256 bd0f740258bcf64688323d3a79eb8f1ee78518bc7a8c2a491adc7766dd8adbc3.

Current saved load_three_way(0) ID join has 1264 lines; conservatively excluded all, versus brief 666.

Raw inputs: W1 25,920 rows; v2 train 214,436 rows. Eligible after all rules: W1 7,436 lines; v2 35,295 lines. Sequential exclusions are mutually exclusive and reconcile exactly; overlapping counts below show every independent rule, including zeros.

| Rule | W1 excluded | v2 excluded |
|---|---:|---:|
| C1_316 | 0 | 163,069 |
| S8_DEV | 0 | 111,947 |
| audit100 | 0 | 30,224 |
| heldout666 | 0 | 0 |
| line_admission_failed | 0 | 0 |
| not_Greek_class | 0 | 31,018 |
| not_requested_Greek_stratum | 18,484 | 0 |
| release_eval_only_dev | 0 | 0 |
| release_locked_eval | 0 | 0 |
| release_locked_eval_ia_wikisource | 0 | 0 |
| release_locked_eval_ib_wikisource | 0 | 0 |
| release_rotated_crop | 23 | 0 |
| release_separator_ambiguous | 75 | 0 |
| stratum_not_c1_pass | 14,598 | 0 |
| v2_dev_test | 0 | 0 |

Sequential counts: `{"W1:not_requested_Greek_stratum": 18484, "W1_eligible": 7436, "W1_input": 25920, "v2:C1_316": 34496, "v2:S8_DEV": 108403, "v2:audit100": 5224, "v2:not_Greek_class": 31018, "v2_eligible": 35295, "v2_input": 214436}`.

Exclusions expand line IDs to their whole v2 documents (including namespaced/bare document aliases), and apply all release class files. The W1 owner exclusion manifest and saved eligible decisions were additionally checked for all W1 documents; that manifest carries provider/edition aliases. A renamed release class file is accepted only by its declared exact SHA-256. See doc_roles.json and receipts/w1_exclusion_custody.json.

Conservative scope: audit100 was excluded at whole-document level as well as by line, beyond the brief's minimum line exclusion. This stronger separation was fixed in the initial reservation; the sequential audit100 exclusion removes 5,224 otherwise surviving v2 lines. No slice needed backfill from those exposed documents.

The live owner release index gained a 1,681-line rotated-crop quality class during the final check. Its overlap with the eligible pool and with either deck is zero. Quality classes are applied at line level; evaluation cohorts also exclude documents. receipts/live_exclusion_refresh.json records the updated input custody and proves eligible line IDs and every frozen document role stayed unchanged.

## Geometry and QA

29,834/31,766 attempted supervision/witness lines have at least one safe word (93.92%); 241,030 saved-geometry word candidates. The 10,965 validation/calibration lines were reserved and not located. This is safe-word line coverage, not full-word or full-corpus OCR accuracy.

Provider token text anchors are joined to saved lines by case-preserving base letters and exact word count. Unsupported frames and mismatches are rejected. Discovery native_size can predate downscaling: the actual retained submitted raster determines the W1 frame. Parliament uses its saved normalized-vertices native-frame flag. No equal-width word estimates, recogniser spans, inference, teacher output, or spelling rules are used.

Missing disposable W1 PNGs were recreated inside this worktree by cropping retained page rasters; each reconstructed PNG matches the original crop SHA-256 byte for byte. Compressed Parliament responses use the saved t23-raw-dedup-1 representation bound to the original response hash and their own compressed-file hashes. Input files were read without locks or modifications.

QA: 22 source strips, 20 deterministically random word boxes each (440 total), in qa/. Red boxes appear only in these private QA strips. Every selected card passed ink, clear side-boundary, unclipped top/bottom, crop hash, frame and scale checks.

| Source | Eligible lines | Reserved | Attempted | Safe-word lines | No safe word / rejected | Words |
|---|---:|---:|---:|---:|---:|---:|
| bsb_poly1850 | 3,951 | 1,374 | 2,577 | 2,132 | 445 | 12,796 |
| ia_poly1850 | 2,076 | 487 | 1,589 | 1,270 | 319 | 8,122 |
| nlg | 1,409 | 324 | 1,085 | 489 | 596 | 2,194 |
| parliament_proceedings_1975_2000 | 17,689 | 5,207 | 12,482 | 12,146 | 336 | 88,985 |
| openarchives_Dione | 1,683 | 318 | 1,365 | 1,331 | 34 | 12,850 |
| openarchives_ntua | 1,131 | 0 | 1,131 | 1,126 | 5 | 9,704 |
| openarchives_ktisis | 1,810 | 202 | 1,608 | 1,599 | 9 | 15,491 |
| openarchives_kallipos | 1,352 | 199 | 1,153 | 1,140 | 13 | 11,252 |
| openarchives_apothesis | 1,445 | 734 | 711 | 705 | 6 | 6,585 |
| openarchives_Pandemos | 2,026 | 576 | 1,450 | 1,430 | 20 | 13,948 |
| openarchives_nemertes | 1,420 | 116 | 1,304 | 1,272 | 32 | 11,660 |
| openarchives_KEIED | 1,940 | 615 | 1,325 | 1,306 | 19 | 11,629 |
| openarchives_anaktisis | 1,897 | 663 | 1,234 | 1,218 | 16 | 11,951 |
| openarchives_hellanicus | 1,842 | 150 | 1,692 | 1,648 | 44 | 15,955 |
| openarchives_mixed_kallipos | 18 | 0 | 18 | 18 | 0 | 119 |
| openarchives_mixed_KEIED | 106 | 0 | 106 | 100 | 6 | 844 |
| openarchives_mixed_anaktisis | 308 | 0 | 308 | 301 | 7 | 2,247 |
| openarchives_mixed_Dione | 326 | 0 | 326 | 313 | 13 | 2,155 |
| openarchives_mixed_apothesis | 108 | 0 | 108 | 98 | 10 | 815 |
| openarchives_mixed_hellanicus | 52 | 0 | 52 | 52 | 0 | 486 |
| openarchives_mixed_ktisis | 98 | 0 | 98 | 96 | 2 | 885 |
| openarchives_mixed_nemertes | 44 | 0 | 44 | 44 | 0 | 357 |

Detailed rejection reasons per source are in geometry_coverage.json. A line can supply safe words while other words on it are refused.

Robustness acquisition uses neighbour_body_ink_xh >= 1.0, accent_ink_cut_fraction >= 0.05, or a token within half a crop height of either horizontal crop edge. These are selection thresholds only. Initial-diphthong breathings are classified as psili/dasia rather than crasis; final-accent mining includes the last vowel before terminal consonants.

## Drawn cards, candidates and caps

| Deck / slice | Absent candidates | Marked candidates | Drawn absent | Drawn marked | Total | Shortfall |
|---|---:|---:|---:|---:|---:|---:|
| T2 / capitals | 3,510 | 843 | 130 | 130 | 260 | 0 |
| T2 / omicron_monotonic | 43,689 | 3,800 | 80 | 80 | 160 | 0 |
| T2 / subscript | 47,354 | 398 | 90 | 90 | 180 | 0 |
| T2 / specks | 29,295 | 5,452 | 60 | 60 | 120 | 0 |
| T2 / exact_names | 137,644 | 45,203 | 0 | 80 | 80 | 0 |

T2: 97 data documents; maximum 5 cards/page including controls. Maximum per-document slice counts: `{"capitals": 8, "omicron_monotonic": 7, "subscript": 12, "specks": 2, "exact_names": 7}`. Cap rejections: `{"already_selected_word": 76, "page_cap": 112}`. C1 error-line priority cards drawn: 49. Exact-name subtypes: `{"final_accent": 6, "circumflex": 8, "crasis": 28, "dialytika": 36, "psili_dasia": 2}`.

| T4 / capitals | 1,664 | 321 | 50 | 50 | 100 | 0 |
| T4 / omicron_monotonic | 15,527 | 2,154 | 50 | 50 | 100 | 0 |
| T4 / subscript | 17,955 | 321 | 50 | 50 | 100 | 0 |
| T4 / exact_names | 51,589 | 18,883 | 50 | 50 | 100 | 0 |
| T4 / random | 63,138 | 2,178 | — | — | 200 | 0 |
| T4 / specks | 11,363 | 2,501 | 100 | 100 | 200 | 0 |

T4: 29 data documents; maximum 5 cards/page including controls. Maximum per-document slice counts: `{"capitals": 5, "omicron_monotonic": 6, "subscript": 8, "exact_names": 10, "random": 20, "specks": 11}`. Cap rejections: `{"already_selected_word": 20, "page_cap": 324, "document_slice_cap": 121}`. C1 error-line priority cards drawn: 0. Exact-name subtypes: `{"absent_counterpart": 50, "crasis": 10, "dialytika": 12, "final_accent": 10, "psili_dasia": 8, "circumflex": 10}`.

C1 priority uses marks=n verdicts joined through the owner key and exact crop raster equality; these are candidate error lines, not accepted printed labels or guaranteed error words. Existing C1 correction text is never shown. Candidate counts are overlapping anchor opportunities; drawn words are unique within each deck. Slice polarity is an acquisition key, not print truth.

T4 has 400 contrasts (100 per specified slice), 200 vowel-bearing words sampled by a uniform hash permutation subject to uniqueness/diversity caps, and 200 robustness words. Fifty robustness cards additionally show padding-only, ±1.5 degree skew, and expanded span-jitter views of the same source word. All 150 extra views retain the same witness group and add no denominator slots. Native line context remains unchanged. Sampling is constrained, so no unconstrained population inclusion probability is claimed.

## Blinding, controls and handoff

Each card has an unboxed word zoom at an exact integer uniform scale of 1–3, plus the complete line at native pixels. HTML scrolls wide lines rather than scaling them. Public image names hash their PNG contents; public paths/manifests have opaque card IDs and no source, book, page, line, selection text, confidence, or private joins. Leak scans cover text, paths, image metadata and content-hash names and passed for both decks. Intrinsic printed text may identify a work; required native context is retained.

Options use base letters and punctuation only, adding alternatives for one anchor head. No provider marks are copied. Consequently other printed marks may be missing from every option: readers must then select literal transcription of the complete printed word. This deliberate limitation is explicit in each README. Literal transcription remains available for base-letter errors and misprints.

The complete expected control forms, complete proposed letter tuples and review images are together in each private/controls_proposed.json directory. Open private/controls_review.html for the native-pixel lead review gallery. They are PROPOSED from selection keys, not pixel-verified truth. All lead_verified flags remain false; the resolver refuses to consume real readers until every control is verified. The deck-level controls_proposed.json is an index to that private key. All 80 controls per deck are excluded from truth/inventory denominators.

Pass only decks/T2/blind/ or decks/T4/blind/ to readers. Reader 1 uses cards.jsonl / index.html; reader 2 independently uses cards_reverse.jsonl / reverse.html. Preserve all source/private directories outside reader access. Tranche 3 was not built; its documents remain reserved.

## Resolution and usable inventory

r2_cards_resolve.py accepts two reader JSONL files and optional reader 3. It enforces assigned IDs/order, rejects inconsistent literal/head tuples, gates each batch at at most one control error, and omits every failed batch. Disagreements produce tiebreak/blind/cards.jsonl with re-randomised option identities and a separate private option map; controls are included for the third-reader gate. Third answers must use that new map. At least two matching votes are required. Ownership failures, undecided heads, absent votes and unresolved forms remain unknown.

Truth records complete printed forms and explicitly voted four-head targets. Omitted non-anchor targets remain unknown even if their transcription looks unmarked. Inventory counts distinct (crop SHA-256, crop-relative letter index), using the word offset so separate words on the same crop do not collapse. It reports complete targets, unknown targets and target-head absent/marked counts by deck and slice. Repeated views never multiply slots. No truth file is emitted for these ungraded real decks.

Example after control verification:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python scripts/labelfix/r2_cards_resolve.py --deck docs/records/labelfix/spellcheck/R2/decks/T2 --reader1 r1.jsonl --reader2 r2.jsonl --out docs/records/labelfix/spellcheck/R2/resolved/T2
```

| Deck | Data cards prepared | Controls proposed | Actual readings | Tiebreak readings | Actual Opus tokens | Usable printed slots |
|---|---:|---:|---:|---:|---:|---|
| T2 | 800 | 80 | 0 | 0 | 0 | pending independent readers |
| T4 | 800 | 80 | 0 | 0 | 0 | pending independent readers |

Initial forecast: 3,520 card readings including controls, plus disagreements. The 150 additional paired views add visual work but no independent source cards. The resolver sums reported input/output tokens and labels missing usage unknown; synthetic test usage is never reported as real Opus usage.

## Validation and provenance

150 tests passed (tests/test_r2_cards.py, tests/test_docai.py, tests/test_harvest_admission.py); none modified or weakened. Synthetic integration exercises agreement, strict reverse order, >1-control batch rejection, one allowed control error, unverified-key refusal, re-keyed tiebreak resolution, UNKNOWN preservation, explicit ownership masking, inconsistent tuple refusal, crop-relative distinct slot counts and exact saved crop reconstruction.

Artifact validation passed: 1,760 cards, every selected pixel/geometry/hash/scale check, role disjointness, zero cross-deck crop overlap, diversity caps, 50 repeated T4 witnesses, all QA strips and both leak scans. Receipts and copied S8 reference code are in receipts/. Those reference files are never imported; runtime code uses only standard library, Pillow and NumPy.

Observed checkout: opus/r2-cards at 339e221ba3baddc8e43f88647fb19ab17d635b9a (R2 brief), directly after plan 52f34de9. No Git writes, network, recogniser/reader/detector inference, Clariden, or writes/locks in any input worktree were performed. All generated files are inside this worktree.

Acquisition shortfalls: none. Readiness limitation: lead pixel verification of proposed controls and QA, followed by independent readers; usable truth counts remain pending.

## R2C2 resolver fixes

17 October 2026. This is a **protocol/private-key correction**, not a correction of reader carelessness. For an anchor whose four heads are all `none`, ownership is not applicable: the resolver normalises ownership to `None` in answers and agreement signatures, and ignores ownership on both sides of a control comparison when either answer or expectation has an unmarked anchor. Marked anchors still require the existing ownership decision. Explicitly voted heads still need two valid votes; omitted/undecided heads stay unknown. Resolved unmarked anchors remain usable with ownership n/a.

Private key changes: **61 of 79 T2 controls; 69 of 80 T4 controls**. Each changed entry has `expected_ownership_ok: null` and `key_fix_20261017: "ownership not applicable on unmarked anchor"`. Every `lead_verified` value and every other pre-existing field is preserved. Deck-level index keys and all blind assets are unchanged.

Validation now isolates a malformed answer as an invalid vote, recording its card ID and reason in the gate and receipt. It is absent from agreement and majority voting. An affected data card enters the tiebreak when the two eligible reader batches cannot agree, including a valid vote opposite an invalid vote. Other data cards continue resolving normally. An invalid control counts as a control failure; more than one control failure still excludes the whole batch. Receipts and usage tables count invalid answers, retaining well-formed reported token usage for those readings. File/assignment integrity (complete IDs in assigned order) remains a prerequisite, so unfinished files are not admitted to the gate.

Added `--dry-run --manifest <assigned cards.jsonl>` for single-batch validation with `--reader1 <answers.jsonl>`. It writes only validation receipts, control results and usage under the supplied worktree output directory, forbidding deck and reader folders. It emits no truth, inventory or tiebreak deck. The real-reader check used this validation path against byte snapshots under `artifacts/r2c2_dryrun/inputs/`; reader source files were read only. Original source paths, UTC snapshot times and SHA-256 hashes are recorded in `artifacts/r2c2_dryrun/summary.json`.

**Live input discrepancy:** the brief describes 13 finished batches. At the final snapshot (2026-10-17T08:36:42.706155+00:00), the supplied paths contained **8 complete 110-card batches and 8 partial files**; these files were visibly growing during this task. The denominator below uses complete assigned batches available at validation time. Partial files are listed separately and are neither failed control gates nor claimed passes. No reader output was repaired or completed by this task.

Before/after results use the saved pre-change resolver and pre-change control key. “Before control failures” and “Before invalid” are per-card diagnostic counts; the actual old resolver aborts at its first invalid answer, so an aborted batch has no completed old gate. Invalid control answers count as diagnostic control failures. Complete batches: **2/8 passed before; 8/8 pass after**, with **5 invalid data answers** excluded from voting after the fix. Every complete batch has zero control failures after the fix.

| Batch | Answers / assigned | Controls | Before control failures (diagnostic) | Before invalid (diagnostic) | Before result | After control failures | After invalid | After gate |
|---|---:|---:|---:|---:|---|---:|---:|---|
| r1_b00 | 110/110 | 14 | 0 | 0 | pass | 0 | 0 | pass |
| r1_b01 | 110/110 | 5 | 0 | 2 | aborted | 0 | 2 | pass |
| r1_b02 | 51/110 | 7 | — | — | incomplete | — | — | not evaluated |
| r1_b03 | 100/110 | 14 | — | — | incomplete | — | — | not evaluated |
| r1_b04 | 110/110 | 11 | 9 | 0 | fail | 0 | 0 | pass |
| r1_b05 | 105/110 | 10 | — | — | incomplete | — | — | not evaluated |
| r1_b06 | 110/110 | 13 | 0 | 0 | pass | 0 | 0 | pass |
| r1_b07 | 110/110 | 5 | 0 | 1 | aborted | 0 | 1 | pass |
| r2_b00 | 95/110 | 5 | — | — | incomplete | — | — | not evaluated |
| r2_b01 | 110/110 | 13 | 0 | 1 | aborted | 0 | 1 | pass |
| r2_b02 | 110/110 | 10 | 9 | 0 | fail | 0 | 0 | pass |
| r2_b03 | 104/110 | 11 | — | — | incomplete | — | — | not evaluated |
| r2_b04 | 110/110 | 14 | 8 | 1 | aborted | 0 | 1 | pass |
| r2_b05 | 104/110 | 7 | — | — | incomplete | — | — | not evaluated |
| r2_b06 | 92/110 | 5 | — | — | incomplete | — | — | not evaluated |
| r2_b07 | 100/110 | 14 | — | — | incomplete | — | — | not evaluated |

Evidence: `artifacts/r2c2_dryrun/batches/*/validation_receipt.json` contains per-card invalid reasons and control IDs; `summary.json`, `batch_results.md`, `key_changes.json`, the pre-change resolver/key snapshots, and `validate_finished.py` reproduce the comparison. The real dry-run hashes checked **3,549 blind files unchanged** across validation. No real truth/tiebreak was published. Synthetic integration outputs are confined to the artifact test directory.

Validation: **167 tests passed** across `tests/test_r2_cards.py`, `tests/test_docai.py` and `tests/test_harvest_admission.py` (including 17 additional protocol/invalid-vote cases). The existing ownership-failure test now uses a marked anchor so it continues testing applicable ownership. New cases cover unmarked true/false/null signatures, old/new control expectations, marked ownership enforcement, contradictory/out-of-range data votes, invalid controls and strict gating, usage/receipt accounting, two-of-three tiebreak recovery, two invalid data votes, read-only dry-run output, and incomplete assignments. Network access was blocked by the test fixtures. CLI dry-run smoke validation passed; `git diff --check` passed. The requested Python and `PYTHONPATH=$PWD` were used with bytecode and pytest cache writes disabled.

Observed worktree: `opus/r2-cards` at `ba6cd164f`, rather than the brief's `6130a4b8`. No Git writes, network calls, blind-deck edits or reader-folder writes were performed. Changes are limited to the resolver, its tests, the two specified private control keys, this appended report section, and `artifacts/r2c2_dryrun/`.

R2C2 READY: ownership n/a rule; per-card invalid votes; controls changed T2 61 / T4 69; dry-run batches passing gate 8/8; tests 167 passed

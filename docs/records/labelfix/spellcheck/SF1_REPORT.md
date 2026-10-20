# SF1 — ASTRA-SC1 fix round

Implemented on `opus/spellcheck`, actual checkout HEAD `0ac89abf525b5d335a8cf7524adb660f6a8ae1f4` (the brief-only commit after the prompt's `6929c738`). No `.git` writes, external network, CTC forward passes, training jobs, model-asset changes, or toolkit S1–S4 substitutions. CPU and cached alignments only. The review and both probe scripts were read before implementation.

Validation: **223 passed** across the runnable labelfix suite (42 SF1 cases plus 181 existing cases). The unchanged HTTP-server integration test is blocked at `socket.bind` by the sandbox (`PermissionError: Operation not permitted`): the full command reports 223 passed / 1 setup error; the explicitly offline command reports 223 passed / 1 deselected. No assertion test fails. Existing K1 deletion assertions now select `output="normalised"` explicitly; their expected outputs and evidence assertions remain, and the public-reader test additionally asserts print preservation.

The initial regression run had **17 failed / 1 passed**. Its one passing case checks already-valid model-asset separation and exclusion receipts. All behavioural counterexamples from `review_probes.py` are now repository tests; expanded coverage also checks receipt tampering, source masks, missing lines, namespaces, configuration, and label HOLD propagation. Logs are in [SF1_evidence](SF1_evidence/).

## B01 — Print-preserving default

`apply_constraints`, `read_ink`, `read_line_details`, and `read_line` preserve detected parts by default. Orthographic conflicts carry rule/evidence receipts in `constraint_flags`; affected character slots receive `hold=True` and `label_status="HOLD"`. Owner pages retain the flagged printed letter with the dotted “reader and detector disagree / impossible by rule” style. R1 raw scoring propagates HOLD into frozen label slots, and `agreement_mode.py` honours those holds. Only explicit `output="normalised"` selects deletion. `filtered=False` remains an explicit historical raw bypass. C1-after-consonant and C3 remain held back.

| split | old default deletions | old UNKNOWN deletions included in total | new default deletions | those deletions now flags |
|---|---:|---:|---:|---:|
| held-out | 100 | 10 | 0 | 100 |
| DEV | 40 | 3 | 0 | 40 |
| combined | 140 | 13 | 0 | 140 |

The expected “100 + 13 unknown” is not an additive held-out count: the saved receipts contain 100 held-out deletions **including 10 unknown**, plus 40 DEV deletions **including 3 unknown**. UNKNOWN removals are not established corrections. There are 303 held character slots in saved-evidence replay, including held-back/tied proposals.

| character atomic metric | old normalized K1 TP/FP/FN | print-preserving TP/FP/FN |
|---|---|---|
| heldout | 4431/246/423 | 4431/336/423 |
| dev | 2546/119/310 | 2546/156/310 |

Explicit normalization reproduces the old K1 character totals. The increase in measured false positives in print output reflects retaining suspicious pixel readings for review, not silent orthographic correction. Tests: `test_supported_printed_misprint_is_flagged_and_hold`, `test_flagged_page_letter_dotted_and_keeps_mark`, `test_raw_r1_reading_flags_reach_label_slot`, and retained K1 rule/holdback tests. Evidence: [SF1_truth_K1_metrics.json](SF1_truth_K1_metrics.json), [SF1_constraint_flags.jsonl.gz](SF1_constraint_flags.jsonl.gz).

## M03 — Unsupported printed truths remain UNKNOWN

`char_truth` checks `mark_class` before calling `mark_set`. Unsupported double accents, macron, breve and other combining marks become `None`, with `unsupported_printed_marks`, printed witness, and adjudication/agreement provenance. S6 serializes that reason. The legacy slot truth builder also records the reason; the Unicode classifier rejects unrecognized combining marks. Its unrelated legacy caller in `rules.py` now passes combining characters rather than Greek base letters.

Fresh text-only replay of all 1,264 saved S6 lines found **0 existing character truths requiring reclassification**. The synthetic defect is real, but its demonstrated corpus prevalence is zero; no positive count is invented. The four regression witnesses change known-empty → UNKNOWN.

| S6 character metric | known before → after | unknown before → after | TP/FP/FN before → after |
|---|---|---|---|
| heldout | 19249 → 19249 | 1176 → 1176 | 4431/336/423 → 4431/336/423 |
| dev | 11149 → 11149 | 772 → 772 | 2546/156/310 → 2546/156/310 |

K1 qualification counts and explicit-normalization totals are unchanged by truth repair; the print-policy change is reported under B01. Tests: `test_unsupported_print_truth_unknown` (four cases). Replay: `python -m scripts.labelfix.sf1_rescore`; [SF1_truth_changes.jsonl](SF1_truth_changes.jsonl) is empty. These are saved-evidence truth/policy comparisons, not a fresh full-corpus detector qualification.

## M04 — Exact source-pixel custody

Each blob carries immutable local membership, full native component IDs and lossless serialized pixel runs. Clipping intersects its original mask with scalar or per-column legal boundaries. It never rediscovers membership from a rectangle. Whole-line deduplication uses intersecting source pixels, preserves the full union under one owner, and asserts conservation. Native labels stay immutable.

The review witness changes **32 source pixels → 48 foreign pixels (old)** to **32 source pixels → 19 original pixels (fixed)**. Clipped pixels are a subset, area cannot grow, and no foreign component enters the evidence. Tests: `test_clipping_preserves_source_pixels_and_never_grows`, `test_pixel_union_conserved_when_deduplicating_native_proposals`, `test_blob_mask_serialization_is_lossless`, `test_per_column_zone_only_intersects_original_pixels`.

## M05 — Complete virtual-union masks

Virtual regions retain their complete parent-ID tuple and exact mask. Case features, capital upper/lower widths, occupancy/shape grids, attached-mark slicing and vowel-mark slicing consume shared `component_mask` membership. The source dimensions and shape evidence therefore describe the same union.

The two-parent witness changes occupancy **1/3 → 2/3**; mark slicing now preserves both parents. All six saved native S6 fixture texts remain unchanged (0/6 changed), without retraining or altering detector band/split policy. Tests: `test_union_case_occupancy_uses_all_parents`, `test_virtual_union_mark_shape_consumers_keep_every_parent`, retained split-eta/capital/side-mark tests. Evidence: [SF1_native_checks.json](SF1_native_checks.json). No new population-level case-accuracy claim is made.

## M07 — Reproducible owner pages

Both builders require `--reading-config` with the detector commit and source hashes, shape/case asset paths and hashes, explicit R1 checkpoint (null for detector-only), and constraint-policy hash. The default shape asset is `markshape_model_S4.json`; missing configuration, wrong checkout/source/model hashes, missing alignment, or unbound combined-reader inputs fail closed. R1 prediction files and checkpoint receipts are checked for combined pages. The unused Google-using `ours_line` / `reconstructed` helpers were removed.

Text and overlays derive from one serialized `LineReading`; the sidecar retains raw detection, raw parts, final parts, constraint flags, displayed character-slot IDs, parent labels and geometry. Reader support is distinct from detector ink, including in combined-page constraint ranking. Configuration is in the HTML comment and sidecar; the sidecar also hashes the exact HTML. The local six-line smoke build succeeded. Both builder parity tests prove that changing only Google/human/printed fields cannot change Ours, its image, or serialized reading; the chosen unchanged native reading matches saved S6.

Tests: `test_owner_page_same_serialized_reading_and_reference_parity` (both builders), `test_flagged_page_letter_dotted_and_keeps_mark`, `test_combined_reader_flags_do_not_rank_with_detector_support`. Evidence: [SF1_reading_config.json](SF1_reading_config.json), [six-line HTML](SF1_owner_smoke.html), [hash-bound sidecar](SF1_owner_smoke_boxes.json). No owner page was published or sent.

## M08 — Regression and owner-note instruments

Box matching is canonical-order, one-to-one maximum cardinality then maximum total IoU. Entirely missing lines are reported. Ownership requires full containment in a two-dimensional legal mark zone; legacy horizontal ranges, ambiguous zones and distant boxes remain unassigned. Old/new slot namespaces stay separate. The review order-dependence witness changes **1 lost + 1 added → 0 lost + 0 added + 2 moved**, identically under reversal.

`owner_implicit_changes.py` requires the reviewed HTML hash and its hash-bound old sidecar; it uses the old serialized slot geometry. Only slot-shaped clauses (`at 7`, `slot 7`, `7-8`) name targets. Counts/dates do not, neighbours are not widened, and missing lines/slots are unresolved. S6/R1 checks reject missing targets and compare approved names/multiplicity, including UNKNOWN truths. R1 positive count checks reject extra units. Current 49/57 note sets and old 59/33/56 sets remain separately labelled. The old 33-review instrument is read from its explicit saved review checks rather than misreading the now-56-row example file.

| current note set | saved S6 complete-note success | strict replay |
|---|---|---|
| owner_notes_review_v16_20261016.jsonl | 36/49 | 35/49 |
| owner_notes_examples_v10_20261016.jsonl | 33/57 | 33/57 |

| R1-A set | old reported fixed | strict raw fixed |
|---|---|---|
| old_59 | 38/59 | 35/59 |
| review_33 | 21/33 | 11/33 |
| examples_56 | 29/56 | 23/56 |
| review_v16_49 | not previously reported | 10/49 |
| examples_v10_57 | not previously reported | 24/57 |

The current 57-example set contains **1 line without an R1 prediction**, now unresolved. Physical/presence, naming, segmentation-clause and complete-note dimensions are separate in [SF1_owner_summary.json](SF1_owner_summary.json) and the regenerated R1 result. These clause counts are instrument results, not independent certification of printed geometry.

Tests: `test_box_matching_order_independent_and_global`, `test_box_missing_lines_and_separate_slot_namespaces`, `test_box_owner_requires_full_two_dimensional_legal_zone`, `test_new_slot_numbers_never_alias_reviewed_old_notes`, `test_slot_clause_parser_excludes_counts_dates_and_neighbours`, `test_implicit_missing_targets_and_no_neighbour_widening`, `test_missing_note_target_unresolved` (five kinds), `test_approved_unknown_name_loss_fails`, `test_r1_missing_target_and_unknown_approved_name_loss`.

## M09 — Named baselines and complete scoring receipts

`r1_score.py` requires repeated named `--baseline NAME=path` inputs. The checked manifest verifies each full file hash, explicit expected metric totals and canonical line/slot/box/recogniser identities. Prediction receipts are bound to the supplied extraction receipt, actual index and actual checkpoint; extraction files are verified. Saved R1 predictions have no exported confidence: their support remains UNKNOWN, and neither scoring nor combined-page constraint ranking borrows S4 detector blobs. Future prediction serialization exports its own head probabilities with uncalibrated provenance; no inference/training was rerun.

The rebuilt [R1 result](clariden/R1_result_3678928/RESULT.md) contains symmetric raw and explicitly normalized tables. S5 changes from the mislabeled **3731/245/322 → 3714/249/339**; S6 is now separately shown as **3731/245/322**. The historical default-normalized R1 columns equal the new explicitly normalized columns; their raw counterparts are separately shown.

| reader | raw TP/FP/FN | normalized TP/FP/FN |
|---|---|---|
| S4 | 3726/261/327 | 3735/216/318 |
| S5 | 3714/249/339 | 3723/211/330 |
| S6 | 3731/245/322 | 3744/196/309 |
| A | 3818/33/235 | 3821/30/232 |
| B | 3805/37/248 | 3807/30/246 |
| C | 3800/45/253 | 3804/39/249 |
| D | 3803/36/250 | 3804/31/249 |
| E | 3812/43/241 | 3814/38/239 |

All eight columns use the same 666 held-out lines and frozen slot denominator; raw/normalized policies are distinct. The held-out unmapped count is 715, separately from the historical 755 pooled held-out-plus-DEV count. The score receipt binds baseline manifest/files/identities/totals, extraction/index/metadata, predictions/receipts/checkpoints, reader support, note versions, scorer dependencies and constraint policies. Original metrics/results/receipt and old raw report are retained as `*_superseded`.

Tests: `test_saved_r1_baselines_have_correct_labels`, `test_baseline_name_hash_and_expected_totals_bound`, `test_prediction_receipt_binds_extraction_index_and_checkpoint`, `test_r1_support_cannot_borrow_s4_detector_pixels`, `test_rescoring_receipt_and_current_note_sets_bound`, plus retained frozen-slot scoring tests. Bindings: [SF1_baselines.json](SF1_baselines.json), [score_receipt.json](clariden/R1_result_3678928/score_receipt.json). Original held-out extraction was verified read-only under the adjacent `greek-ocr-toolkit-spellcheck-r1` checkout; no missing metadata was guessed.

## N01 — Historical behavior is pinned

S4/S5/S6 calls explicitly select `filtered=False`; S4/S5 serialize the rendered parts, and virtual/fallback components no longer require a nonexistent native lookup. Historical entry points reject the incompatible SF1 pixel/schema runtime before loading crops or overwriting saved artifacts. New saved-evidence comparisons use the separately versioned SF1 replay scripts. Historical S4/S5/S6/K1 artifacts are preserved.

Tests: `test_historical_validators_explicit_raw_and_rendered_parts`, `test_historical_runtime_guard_prevents_overwrite` (three entry points). Existing raw-reader and native-fixture assertions remain green.

## N03 — Fail-closed case and honest heuristic confidence

A missing case model raises `FileNotFoundError`; it cannot emit heuristic capital probability 1.0. Configured case assets are hash-bound. A heuristic acute/circumflex/breathing carries its own `heuristic_unqualified` method and `probability=None`; the rejected classifier probability is recorded separately and is not ranked as support for the chosen name. The synthetic rejected probability **0.99 → chosen-name confidence None** makes that separation explicit.

Tests: `test_missing_case_model_fails_closed`, `test_heuristic_mark_confidence_has_own_provenance`, `test_r1_support_cannot_borrow_s4_detector_pixels`. No diagnostic score is promoted to a calibrated correction gate.

## Scope retained for the next round

M01/M02 supervision/independent truth and fused coverage, M06 toolkit geometry substitutions, and M10 scale/validity qualification are not closed by SF1. The two R1 padding/blank probes are executable regression tests: the trained full-height view is explicitly marked padding-sensitive (32 versus 16 dark rows), while blank admitted samples carry UNKNOWN/no-pixel evidence. Their input geometry/admission is preserved; no connected-component gate or retraining was introduced. N02's sampling-plus-loss-weight and selected-source-prevalence limits are stated in the rebuilt R1 report.

## Reproduction and verification

Use the requested interpreter with `PYTHONPATH=$PWD` and `PYTHONDONTWRITEBYTECODE=1`:

```sh
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m pytest tests/labelfix -q -p no:cacheprovider --basetemp=/tmp/sf1-tests -k "not test_server_appends_each_decision_and_serves_static"
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m scripts.labelfix.sf1_rescore
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m scripts.labelfix.sf1_owner_rescore
```

R1 command (choose a new output directory):

```sh
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m scripts.labelfix.clariden.r1_score \
  --runs artifacts/labelfix_r1/output_3678928 \
  --heldout /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-r1/artifacts/labelfix_r1/heldout_font \
  --baseline S4=docs/records/labelfix/spellcheck/S4_lines.jsonl.gz \
  --baseline S5=docs/records/labelfix/spellcheck/S5_lines.jsonl.gz \
  --baseline S6=docs/records/labelfix/spellcheck/S6_lines.jsonl.gz \
  --out /tmp/sf1-score-replay
```

SF1 RESULT: B01 fixed (140 deletions now flags); M03 0 truths now unknown; M04/M05/M07/M08/M09/N01/N03 fixed; tests 223 passed; numbers changed: held-out deletions 100→0, DEV 40→0, 13 unknown deletions now flagged; K1 print FP held-out 246→336 and DEV 119→156; S5 reference 3731/245/322→3714/249/339; S6 owner review 36/49→35/49; R1-A old owner checks 38/59→35/59, 21/33→11/33, 29/56→23/56.

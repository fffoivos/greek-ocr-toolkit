# R0 recogniser audit — R0a handoff

**Letter truth first:** no full line in the 666-line continuity instrument or the 200-line new-source locked stratum has newly adjudicated complete print-letter truth in this phase (0 full lines / 0 full slots certified). Wikisource supplies human reference text for all 666 continuity lines; M2 supplies existing blind verdicts for the new-source lines, not complete transcriptions. Owner notes supply partial observations, not a replacement full-line transcription. No letter error rate is calculated against Google or any unadjudicated reference.

Planted controls have preparer-verified base letters and case for 83 isolated words (565 letter positions); they are quality checks, not an accuracy sample. 350 of the 666 lines have at least one non-control adjudication card. Completing a word card does not certify the rest of its line. R0b can record a full-line letter transcription; R0c must report exactly which full lines/slots have truth, retaining the risk of shared errors in three-way agreement.

**Status: R0a independent work ready; required Wikisource stratum (i) is pending a scope decision/additional books. Do not call the complete two-stratum audit READY.** R0b and R0c have not run. The expected truth, error rates, case winner/extrapolation, print-conditioned apostrophe rates and causal DATA/MODEL decisions remain null.

## Fresh-book feasibility and frozen sets

The specified local harvest has 20 Greek books. The 14 continuity books and three detector DEV books exclude 17. The remaining three are original harvest `dev` books (distinct from the detector DEV books). No fourth or fifth fresh Greek book exists in this pool; ten additional fresh books are Russian and are ineligible. The referenced E3 human prediction file covers only the existing 17 Greek instrument books, so it cannot supply fresh-book recognitions.

| Fresh Greek book | Harvest split | Human-aligned lines, before admission | Admitted polytonic candidate lines |
|---|---|---:|---:|
| 81d8091c: Η εθνική ημών μουσική | dev | 6 | 1 |
| 309ff6cf: Σύνταγμα της Κρητικής Πολιτείας | dev | 70 | 10 |
| f7c74d15: Ἀστέρια | dev | 159 | 122 |

Thus at most 235 human-aligned lines exist before admission/script checks, and 133 candidates remain after admission, one-to-one human alignment, existing crop and explicit polytonic-mark checks. Crops are whole admitted line crops; pixel completeness remains subject to adjudication. No selection depends on recogniser accuracy. The requested ≈300–500 lines / ≥5 books cannot be met offline. No candidate stratum was silently frozen or forwarded through CTC. `R0_locked_set.jsonl` is intentionally empty; its receipt says `PENDING_SCOPE_DECISION`. The question about accepting an undersized set remains unanswered.

Stratum (ii): **200 locked lines / 11 sources**, seeded 20261017, from 409 eligible measured polytonic M2 cards; 200/409 is 48.9%, capped at the requested 200. **273 remaining measured cards form DEV** (including 40 modern-source cards and other cards without explicit polytonic evidence). The 40 unmeasured Cyrillic cards do not enter either list. All 473 measured cards are accounted for exactly once. The locked and DEV lists contain line ids; `R0_newsource_exclusion_ids.txt` contains the 200 frozen training exclusions. DEV and locked are a line split and share documents; document-disjointness between these two pools is not claimed.

Selection requires a non-modern/non-Cyrillic source and a breathing, grave, circumflex or subscript in Google or recogniser text, and no Cyrillic codepoint. This script filter may enrich marked text and is not an unbiased source-population estimate. Mixed Greek/Latin cards are retained; monotonic-only cards are excluded from the lock.

**Never tune:** the locked strata judge L1 and wave 1c from now on, never policy/checkpoint/threshold selection, never training. The 666 remain the continuity instrument. All M2 cards had already been used as S7 qualification targets; this freeze cannot undo that prior exposure.

### Zero-intersection receipt

The L1 manifest was copied read-only from the specified worktree and checked byte-for-byte against commit `6b91ebaa`. For the 200 new-source locked rows, intersections against 666, detector DEV and L1 input are all **zero** for line ids, document ids and normalized document stems; exact crop hashes also have zero overlap with 666/DEV and the development remainder. Source cards, key line ids, Google labels and crop bytes were checked against the original blind-card files. Cross-stratum (i)/(ii) exclusion is **PENDING**, because stratum (i) does not yet exist; no vacuous zero is advertised as a completed receipt. Identifier checks cannot exclude undocumented copies of the same edition across archives.

[Frozen split receipt](R0_newsource_split_receipt.json) · [Fresh pool inventory](R0_evidence/fresh_pool_inventory.json) · [L1 manifest copy](R0_evidence/L1_input_documents.txt) · [Input hashes](R0_evidence/input_binding.json)

## Native CTC span placement, all alphabetic slots

**998 / 25437 clean slots = 3.9234% outside their assigned blob** across 866 lines. Every emitted alphabetic slot is retained in the census: 27534 total. Fused slots: 1396; split slots: 601; no letter blob: 100. These are slot counts, not distinct blob counts.

Method: run the unchanged native detector `ink.analyse`, `case.estimate_font`, `segmentation.recogniser_slots`, and `case.prepare` with the actual cached CTC prediction. A clean slot owns exactly one native connected component and no other character owns that component, with neither fusion, split-union nor unknown localisation. The reference is its native component bbox, not a CTC-derived partition. Outside means `(x0+x1)/2` is outside `[blob.x0, blob.x1)`. The assignment still uses the runtime overlap rule: it is not independent pixel truth for glyph identity. Do not interpret this geometry diagnostic as a letter error rate or a causal training-label verdict.

Actual cached predictions are used for span measurement; **10 continuity lines differ from the stored instrument prediction**, including eight with different base letters. Their native spans are not transferred. The deck includes native-cache variant cards in addition to the stored-prediction cards; R0c must keep the two prediction streams distinct. [Exact drift receipt](R0_evidence/cached_prediction_drift_10.jsonl). Card locators alone may transfer spans to stored text, and their coordinate provenance is recorded. Nonalphabetic CTC atoms (combining marks, spaces, punctuation) are separately counted in the line census; the clean letter-blob denominator does not apply to them.

| Script | All slots | Clean | Outside | Outside % |
|---|---:|---:|---:|---:|
| greek_poly | 25838 | 23888 | 931 | 3.8974 |
| modern | 1265 | 1183 | 59 | 4.9873 |
| Latin | 431 | 366 | 8 | 2.1858 |
| other | 0 | 0 | 0 | — |

Greek script uses the recorded line class (`greek_mono` → modern, otherwise Greek polytonic/mixed); Latin is identified per emitted character. A polytonic-source card can contain a modern-class line, so book/source names alone are not script truth. Size is the runtime pixel x-height (including capital-run bands), with fixed <20, 20–34 and ≥35 px buckets.

| Pixel x-height | All slots | Clean | Outside | Outside % |
|---|---:|---:|---:|---:|
| <20px | 5467 | 4738 | 231 | 4.8755 |
| 20-34px | 20431 | 19170 | 687 | 3.5837 |
| >=35px | 1636 | 1529 | 80 | 5.2322 |

Script × size, per-book and per-stratum denominators are in [span_summary.json](R0_evidence/span_summary.json); every slot is in [span_slots.jsonl.gz](R0_evidence/span_slots.jsonl.gz), and nonletter atoms are in [span_line_census.jsonl](R0_evidence/span_line_census.jsonl).

## The original 715 R1 unmapped samples

Reproduced exactly: 11,329 scored samples, 10,614 mapped, 715 unmapped. Every unmapped frozen S4 recogniser slot has `localisation_unknown=True` and lacks `component_slot`. Of these, **698 share a primary blob with other recognised characters**, so the historical mapper rejects unique ownership; **17 have no overlapping primary letter blob**. The saved primary-owner lists give the reason for each individual sample. [Historical S4 mapping source](R0_evidence/historical_S4_reading.py.txt), read from commit `afe67823`, explicitly refuses `k is None or len(owners[k]) != 1`. These are original frozen-instrument mapping omissions, not 715 missing recogniser letters. The independent R1 extraction uses different component/window rules and can still admit a window. Its additional support partition is:

| R1 support / frozen mapping | Count | Example line ids |
|---|---:|---|
| R1_single_owner_component_frozen_mapper_unlocated | 261 | 177b717d-p000013-l0002, 177b717d-p000013-l0004, 177b717d-p000017-l0004 |
| R1_no_component_owners_frozen_mapper_unlocated | 6 | 22fda82b-p000052-l0033, 22fda82b-p000118-l0008, 22fda82b-p000118-l0014 |
| R1_shared_component_frozen_mapper_unlocated | 448 | 0b7bf21d-p000013-l0026, 177b717d-p000013-l0006, 177b717d-p000013-l0009 |

Frozen evaluation bbox overlaps per unmapped CTC interval: {'0': 17, '1': 257, '2': 433, '3': 8}. Overlap does not confer unique ownership. [All 715 individual reasons, owner starts and exact saved evidence](R0_evidence/R1_unmapped_715.jsonl) are preserved; neither fusion nor a nearest-blob fallback invents truth. The 698 shared-blob versus 17 no-primary distinction closes the historical mapping mechanism; judging whether each shared component really contains multiple printed letters still requires pixels.

## Blind handoff and truth placeholders

**948 adjudication cards + 83 planted controls = 1031 cards (8.05% controls)**. Every disagreement group is included, rather than sampled; character-aligned word groups retain joins, splits and reference insertions. Forms are NFD-mark-stripped, case kept, and contain at most three distinct candidates. Candidate order and complete item order are seeded/randomized; source names, original line ids, reference verdicts and control flags are absent from the blind file. Zooms are at most 3× native. Each item includes the full line.

| Card kind (can share a card) | Count |
|---|---:|
| S4_apostrophe_candidate | 208 |
| letter_word_disagreement | 287 |
| apostrophe_quote_disagreement | 227 |
| case_disagreement | 160 |
| existing_blind_reference_disagreement | 23 |
| S4_opening_quote_candidate | 40 |
| native_cached_prediction_variant | 10 |
| owner_Latin_a_witness | 1 |
| M2_apostrophe_candidate | 2 |

The exact 753 S5 case-disagreement slots are retained as the population. The seeded sample contains **160 slots from all 13 books with disagreements**. Population and sample counts per book are in [case_sampling_receipt.json](R0_evidence/case_sampling_receipt.json). R0c uses the stratified estimator `sum_h N_h × recogniser_right_h/n_h`; the winner percentage and extrapolated count are null now.

R0b delivery: give each independent Opus reader only [R0_cards/](R0_cards/index.html), its images/README, and a fresh blank [R0_expected_truth.json](R0_expected_truth.json). Keep [items_key.json](R0_adjudication_private/items_key.json) and all other evidence private. The key is outside the blind directory and never embedded/fetched by its viewer. The preparer visually checked planted-control words; controls are excluded from accuracy. Readers must be able to reject all candidate forms, identify ambiguous print and record full-line transcription explicitly. The track lead validates controls privately and resolves reader disagreements. No adjudicator was run during R0a.

The owner evidence ledger retains 37 relevant note records (including repeated historical note sets), with original note source/line id. Notes such as misread rho, εις segmentation, eta classification and Latin-a output are partial or method-specific observations, not automatically recogniser identity failures. [Owner notes ledger](R0_evidence/owner_letter_punctuation_evidence.jsonl).

Apostrophe/quote cards include textual disagreements, S4 apostrophe/opening-quote candidates and new-source detector candidates. Existing M2 blind pairs add candidate forms where an exact reference phrase can be located. Existing verdicts remain reference-only. Apostrophe versus breathing and Greek/Latin homoglyphs need explicit pixel/context judgment. The [punctuation inventory](R0_evidence/punctuation_emissions.jsonl) records raw emissions and source coverage; print-positive denominators and emitted/present rates remain null.

## Training-label evidence and R0c DATA/MODEL boundary

The exact local `import_real_v2_train.jsonl` contains 214,436 rows; its hash and symbol-by-script frequencies are recorded. These are training-manifest labels, not a claim that every row was consumed unchanged by E3. Frequency alone does not establish correctness, elision semantics or causal model limitations.

| Label symbol | Codepoint | Occurrences | Lines |
|---|---|---:|---:|
| " | U+0022 | 1111 | 909 |
| ' | U+0027 | 5571 | 5259 |
| « | U+00AB | 4700 | 4476 |
| » | U+00BB | 4967 | 4699 |
| ʼ | U+02BC | 0 | 0 |
| ᾽ | U+1FBD | 4027 | 3877 |
| ‘ | U+2018 | 21 | 21 |
| ’ | U+2019 | 2 | 2 |
| “ | U+201C | 130 | 129 |
| ” | U+201D | 51 | 51 |

The straight apostrophe and spacing koronis are present, while the right curly apostrophe is extremely rare. This rules out the broad unsupported assertion “training labels contain no apostrophes”; it does not prove whether Google dropped particular printed elisions. The codec also admits U+2019. R0c must join adjudicated print, Google labels, recogniser output and label/preprocessing evidence before selecting DATA (bad/missing labels or coverage) versus MODEL (correct labels but failed reading/position). Mixed or unresolved causes must remain explicit rather than forced into a wider-model recommendation.

`R0_failures.jsonl` is a **candidate/geometry observation ledger** in R0a: one row per observed diagnostic or unresolved card kind, with line id, slot, evidence, `DATA_MODEL=null` and status. It does not label disagreement as confirmed failure. Confirmed letter substitution/insertion/deletion/case/script counts, ≥3 examples per supported final failure type, DATA/MODEL verdict and training-arm recommendation belong to R0c; [failure_type_placeholders.json](R0_evidence/failure_type_placeholders.json) and [R0_result_placeholders.json](R0_result_placeholders.json) make the missing fields explicit.

## Review page and verification

[R0_review_positions.html](R0_review_positions.html) is a 60-line pre-adjudication position preview with full line, line id, Google, native recogniser text, a thin box/character label for every CTC atom and one autosaving/exportable note. The final failure-type selection remains R0c work; the track lead publishes it. No Firefox presentation was opened and nothing was published.

Execution: local Mac CPU, network off, **0 new CTC crops**, 200 reused crop/checkpoint-bound M2 cached alignments, no CTC forward on the 666. Runtime/model assets are unchanged. Launch checkout `51aa2f320e94b1af27067d648ece8f561e6d655a` is two R0 brief commits after requested `fabcd6d4`; no detector/recogniser code was edited and no Git mutation command was used. Reproduction scripts are `scripts/labelfix/r0_prepare.py` and `scripts/labelfix/r0_finish.py`. All card PNGs decode, blind/key schemas and control counts validate, both viewers pass JavaScript syntax checks, and runtime/checkpoint/shared-cache hashes are unchanged. Nineteen representative card images were inspected, covering all card kinds and controls. Browser visual/interaction QA could not run: the in-app browser is unavailable and the browser inventory is empty. Final artifact/reference/hash checks are in [validation.json](R0_evidence/validation.json).

R0a is stopped here. The unresolved fresh-book scope prevents the exact requested READY receipt. R0b must provide independent pixel judgments; R0c must score and classify.

R0a PARTIAL READY: locked set (i) PENDING (0 lines / 0 books; 133 candidates / 3 books available), (ii) 200 new-source lines / 11 sources (dev pool 273); zero overlap (ii) with 666, DEV, L1 input; cross-stratum receipt PENDING; cards 948 (+controls 83); span placement outside-blob 3.9234%; R0 RESULT (after R0c): letter truth PENDING (0 full lines certified in R0a); letter error PENDING (case-folded PENDING); spans outside blob 3.9234% (by script/size in receipt); case disagreements recogniser right PENDING; apostrophes emitted PENDING; DATA types PENDING; MODEL types PENDING.

## R0a2 — frozen stratum (i-a), 17 October 2026

Coordinator option (c) supersedes the earlier scope-pending status: **133 lines / 3 books frozen as (i-a)**; (i-b) awaits a new harvest. Counts: 81d8091c 1, 309ff6cf 10, f7c74d15 122. **Ἀστέρια (f7c74d15) supplies 122/133 lines: stratum (i-a) is dominated by one book**. Rerunning unchanged R0a eligibility matched all prior candidate rows; seed 20261017, all eligible lines retained. [Manifest](R0_locked_set.jsonl), [freeze/exclusion receipt](R0_locked_set_receipt.json), [release-exclusion IDs](R0_locked_ia_ids.txt). Line/document/normalized-stem intersections with 666, DEV, L1 input and (ii) are zero; crop hashes also exclude 666/DEV/(ii). L1 uses its locally bound document-only manifest. **Never tune or train on locked strata:** they judge L1 and wave 1c; the 666 remain continuity.

**133 E3 full_s0 CPU forwards**, same `Recognizer.align_paths` as the 666 cache; no other lines forwarded. [Alignment receipt](../../../.cache/labelfix/r0/align_locked_ia.receipt.json). The workspace cache parent was localized before writing; shared cache hashes are unchanged. Head `9d01c9b7` adds only the R0a2 brief to `b7fd49ba`. Network off; no Git/other-worktree writes.

Separate [blind IA deck](R0_cards_ia/index.html): **24 cards + 3 planted controls** (11.11%; unchanged minimum-8% rounding rule), using R0a's generator and seeded ordering. Disagreement cards cover 23/133 lines; fresh lines have no historical S4/S5/M2 cohorts. New controls were pixel-verified. The IA key was written once under `R0_adjudication_private/ia/`, validated in memory, never reopened. No existing private material, original deck or R0b truth file was read or modified. IA IDs/answer storage are separate. [Blank truth](R0_expected_truth_ia.json) and [133 full-line placeholders](R0_line_truth_placeholders_ia.jsonl) await R0b; shared errors remain unadjudicated.

Native span census, all 133 lines: **143 / 2695 clean alphabetic slots = 5.3061% outside blob**, from 2777 alphabetic slots (31 split, 45 fused, 6 without a letter blob). Same native component/ownership method as R0a; geometry only, no letter-error claim. [Script/size/book summary](R0_evidence/ia/span_summary.json), [all slots](R0_evidence/ia/span_slots.jsonl.gz), [line/atom census](R0_evidence/ia/span_line_census.jsonl), [validation](R0_evidence/ia/validation.json).

R0a2 READY: stratum (i-a) 133 lines / 3 books (Ἀστέρια 122); zero overlap with 666, DEV, L1 input, (ii); cards 24 (+controls 3); spans outside blob 5.3061%


## Selection exposure of stratum (i-a) (17 Oct, sourcing lead)

131 of the 133 (i-a) lines are in collection v2 val; E3/E4 checkpoints were selected on v2 val. (i-a) is therefore labelled **selection-exposed (v2 val)** on every table and is reported beside, never pooled with, the clean strata. Model-comparison judgments (L1 arms, wave 1c) use stratum (ii) and the coming (i-b). Checked intersections with v2 val: (i-a) 131, (ii) 0, new-source dev 0, 666+DEV instrument 0. Every future locked-stratum receipt reports its intersection with v2 val.

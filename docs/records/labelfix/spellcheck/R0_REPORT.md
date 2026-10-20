# R0 recogniser audit — final R0c scoring, 17 October 2026

**Letter truth first: 2,376 adjudicated word-letter slots on 361 distinct lines across the three separately reported strata; 0 complete lines / 0 full-line slots certified.** The inventory total adds coverage only, never error rates. There are also 160 case-only cards, physical punctuation probes, ten native-cache variant word cards and one separate DEV witness. These are different evidence scopes.

R0b supplies literal print forms, with combining diacritics ignored. The main deck has 932 AGREED, 14 MAJORITY_OF_3, 2 UNRESOLVED and 83 CONTROL; (i-a) has 24 AGREED and 3 CONTROL. Each reader passes 83/83 main controls and 3/3 IA controls. Controls are excluded from accuracy. No reader supplied `full_line_letters`. Shared errors outside the adjudicated words therefore remain possible; **whole-line/population letter error is UNKNOWN for every stratum**. The rates below describe the selected word cards, whose selection deliberately enriches disagreements.

| Stratum | Cohort lines | Non-control cards (resolved) | Lines touched by any card | Word cards / known letter slots / lines | Case-only cards | Full lines certified |
| --- | --- | --- | --- | --- | --- | --- |
| 666 continuity instrument | 666 | 805 (803) | 350 | 385 / 1632 / 282 | 160 | 0 |
| (ii) mark-enriched, not a population estimate | 200 | 142 (142) | 61 | 117 / 619 / 56 | 0 | 0 |
| (i-a) selection-exposed (v2 val) | 133 | 24 (24) | 23 | 24 / 125 / 23 | 0 | 0 |
| owner DEV supplement; excluded | 1 | 1 (1) | 1 | 1 / 4 / 1 | 0 | 0 |

Word identity is scored only on complete word-card scopes (`model_words`), including punctuation-disagreement words whose accepted printed form contains letters. Case probes certify case only; punctuation anchors certify their requested sign only. Neither silently adds letter-identity truth. Word windows are disjoint within each prediction stream. Exact line IDs, NFD windows and accepted text are in [line_truth_inventory.jsonl](R0_evidence/scoring/line_truth_inventory.jsonl); per-word counts are in [letter_units.jsonl](R0_evidence/scoring/letter_units.jsonl). Lines with no such scopes have no certified letter denominator.

**UNKNOWN stays UNKNOWN.** `item00171` (`177b717d-p000045-l0004`) and `item00564` (`51fe7386-p000024-l0022`) are wholly excluded at their unresolved scopes. An overlapping punctuation card cannot resolve item00564: its boundary is masked. `item00174` (`384c3f89-p000050-l0034`) is MAJORITY_OF_3 but reads `επιστα?υεσκον`: its one `?` glyph is excluded, while its 11 known letters are retained. Its card pixels show the clipped lower part that readers identified. No alternative letter or punctuation shape was guessed.

## Letter errors on adjudicated word-card slots

NFD combining marks, spaces, digits and punctuation are excluded. Case is kept for the first rate; the second uses Unicode casefold (including final-sigma folding). Unit-cost Levenshtein edits are divided by the number of known printed letters. Insertions add errors, not denominator slots. Case and Greek/Latin script substitutions are disjoint subtypes of substitution; the “substitution” column below contains the remaining substitutions. Google is used to diagnose label evidence, never as accuracy truth.

| Stratum | Known slots / lines | Errors | Letter error | Case-folded | Substitution | Insertion | Deletion | Case | Script mix-up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 666 continuity instrument | 1632 / 282 | 106 | 6.50% | 6.43% | 59 | 21 | 22 | 1 | 3 |
| (ii) mark-enriched, not a population estimate | 619 / 56 | 152 | 24.56% | 24.23% | 42 | 13 | 62 | 2 | 33 |
| (i-a) selection-exposed (v2 val) | 125 / 23 | 2 | 1.60% | 1.60% | 1 | 0 | 1 | 0 | 0 |

These are **not CERs on all 666 / 200 / 133 lines**. In particular, 6.50% on the 666 card scopes cannot be compared directly with the old 1.37% v2_test CER against Google labels.

**Prediction streams:** the primary 666 result uses the stored instrument prediction, not substituted native-cache output. Ten native variant cards cover 79 printed letters on eight lines, with 17 edits (12 substitutions, 5 deletions), 21.52% with either case convention **on those variant cards only**. They are not added to the 106 stored-stream errors or its denominator. Ten lines have cached text drift, eight at base-letter level; see [drift receipt](R0_evidence/cached_prediction_drift_10.jsonl). The DEV `02a3a2a6-p000318-l0017` witness has one Greek α → Latin a error in four letters (`ξανα` → `ξaνα`); it is excluded from every stratum.

### By book and source, same selected-word denominator

| Stratum | Book/source | Known slots | Errors | Case kept | Case folded | Sub/ins/del/case/script |
| --- | --- | --- | --- | --- | --- | --- |
| 666 continuity instrument | wikisource:0b7bf21d | 23 | 3 | 13.04% | 13.04% | 2/1/0/0/0 |
| 666 continuity instrument | wikisource:177b717d | 92 | 3 | 3.26% | 3.26% | 2/0/0/0/1 |
| 666 continuity instrument | wikisource:22fda82b | 59 | 2 | 3.39% | 3.39% | 1/1/0/0/0 |
| 666 continuity instrument | wikisource:263438a3 | 36 | 3 | 8.33% | 8.33% | 1/0/1/0/1 |
| 666 continuity instrument | wikisource:384c3f89 | 1016 | 21 | 2.07% | 2.07% | 3/15/2/0/1 |
| 666 continuity instrument | wikisource:4ad622a4 | 103 | 27 | 26.21% | 26.21% | 23/0/4/0/0 |
| 666 continuity instrument | wikisource:4f60b077 | 61 | 1 | 1.64% | 1.64% | 1/0/0/0/0 |
| 666 continuity instrument | wikisource:51fe7386 | 15 | 4 | 26.67% | 26.67% | 1/2/1/0/0 |
| 666 continuity instrument | wikisource:602cc72e | 9 | 2 | 22.22% | 22.22% | 1/0/1/0/0 |
| 666 continuity instrument | wikisource:69e993c1 | 136 | 35 | 25.74% | 25.74% | 21/2/12/0/0 |
| 666 continuity instrument | wikisource:6b47791c | 14 | 1 | 7.14% | 0.00% | 0/0/0/1/0 |
| 666 continuity instrument | wikisource:8fb8cb49 | 0 | 0 | UNKNOWN | UNKNOWN | 0/0/0/0/0 |
| 666 continuity instrument | wikisource:9c1dca9b | 68 | 4 | 5.88% | 5.88% | 3/0/1/0/0 |
| 666 continuity instrument | wikisource:c3e12e31 | 0 | 0 | UNKNOWN | UNKNOWN | 0/0/0/0/0 |
| (ii) mark-enriched, not a population estimate | anemi_poly1850 | 60 | 8 | 13.33% | 10.00% | 1/0/5/2/0 |
| (ii) mark-enriched, not a population estimate | bsb_mixed | 188 | 73 | 38.83% | 38.83% | 22/3/21/0/27 |
| (ii) mark-enriched, not a population estimate | bsb_poly1850 | 30 | 4 | 13.33% | 13.33% | 2/0/2/0/0 |
| (ii) mark-enriched, not a population estimate | gazette_poly1900 | 94 | 19 | 20.21% | 20.21% | 2/4/13/0/0 |
| (ii) mark-enriched, not a population estimate | ia_greek_latin | 58 | 15 | 25.86% | 25.86% | 3/2/4/0/6 |
| (ii) mark-enriched, not a population estimate | ia_poly1850 | 28 | 4 | 14.29% | 14.29% | 1/2/1/0/0 |
| (ii) mark-enriched, not a population estimate | kosmopolis_poly | 10 | 2 | 20.00% | 20.00% | 0/0/2/0/0 |
| (ii) mark-enriched, not a population estimate | lekythos_poly1900 | 5 | 0 | 0.00% | 0.00% | 0/0/0/0/0 |
| (ii) mark-enriched, not a population estimate | nlg_poly | 16 | 1 | 6.25% | 6.25% | 1/0/0/0/0 |
| (ii) mark-enriched, not a population estimate | oa_poly1900 | 80 | 18 | 22.50% | 22.50% | 6/1/11/0/0 |
| (ii) mark-enriched, not a population estimate | pleias_poly1850 | 50 | 8 | 16.00% | 16.00% | 4/1/3/0/0 |
| (i-a) selection-exposed (v2 val) | wikisource:309ff6cf | 16 | 2 | 12.50% | 12.50% | 1/0/1/0/0 |
| (i-a) selection-exposed (v2 val) | wikisource:81d8091c | 0 | 0 | UNKNOWN | UNKNOWN | 0/0/0/0/0 |
| (i-a) selection-exposed (v2 val) | wikisource:f7c74d15 | 109 | 0 | 0.00% | 0.00% | 0/0/0/0/0 |

Zero-denominator books are shown as UNKNOWN, not 0% error. The machine metrics additionally retain every (ii) document beneath its source group; see `letters.by_book_source` in [R0_metrics.json](R0_metrics.json).

## Case: recogniser versus the S5 pixel-case decision

**Recogniser right 160/160; S5 pixel-case right 0/160; UNKNOWN 0.** The book-stratified estimator `sum_h N_h × recogniser_right_h/n_h` gives **753.0 / 753 = 100.00% recogniser right** as a point estimate. This does not certify all 753 individually. All-success strata yield a zero plug-in standard error; that is not a useful confidence interval and none is asserted.

| Stratum | Book | Population N | Adjudicated n | Recogniser right | S5 pixel right | Extrapolated recogniser right |
| --- | --- | --- | --- | --- | --- | --- |
| 666 continuity instrument | wikisource:0b7bf21d | 36 | 8 | 8 | 0 | 36.0 |
| 666 continuity instrument | wikisource:177b717d | 40 | 9 | 9 | 0 | 40.0 |
| 666 continuity instrument | wikisource:22fda82b | 10 | 3 | 3 | 0 | 10.0 |
| 666 continuity instrument | wikisource:263438a3 | 41 | 9 | 9 | 0 | 41.0 |
| 666 continuity instrument | wikisource:384c3f89 | 53 | 11 | 11 | 0 | 53.0 |
| 666 continuity instrument | wikisource:4ad622a4 | 202 | 41 | 41 | 0 | 202.0 |
| 666 continuity instrument | wikisource:4f60b077 | 1 | 1 | 1 | 0 | 1.0 |
| 666 continuity instrument | wikisource:51fe7386 | 25 | 6 | 6 | 0 | 25.0 |
| 666 continuity instrument | wikisource:602cc72e | 14 | 4 | 4 | 0 | 14.0 |
| 666 continuity instrument | wikisource:69e993c1 | 43 | 9 | 9 | 0 | 43.0 |
| 666 continuity instrument | wikisource:6b47791c | 204 | 41 | 41 | 0 | 204.0 |
| 666 continuity instrument | wikisource:8fb8cb49 | 12 | 3 | 3 | 0 | 12.0 |
| 666 continuity instrument | wikisource:9c1dca9b | 72 | 15 | 15 | 0 | 72.0 |

These are failures of the **S5 pixel-case decision**, not recogniser case errors. The word cards independently find three recogniser case errors: one Φ → φ on `6b47791c-p000005-l0005` (666 continuity instrument), and two Ι → ι on `anemi--_metadata_6_2_f_metadata-352-0000000.tkl-23eeee17--000052-l0033` ((ii), mark-enriched, not a population estimate). The case cohort has a locator caveat: item00818 offers Ο/ο at frozen S5 slot 7, while its saved NFD start 6 points to Τ. It is scored as uppercase-versus-lowercase only; no body identity or span is transferred from it.

## Apostrophes, elision and quotation

The denominator is **deduplicated print-positive sites in adjudicated candidate scopes**, not punctuation prevalence in a source population. Straight apostrophe, curly apostrophe, modifier apostrophe, spacing koronis and grave-like elision ticks count as functional apostrophe emissions; exact printed shape is reported separately. Opening and closing quote shapes are also recorded separately. One logical site is counted once even when a word card and an S4/M2 probe both cover it. Thirty-five rejected S4 opening-quote probes are physical components (often breathings), not 35 absent signs at text offset zero; their pixels/boxes are retained separately.

| Stratum | Printed kind | Printed sites | Recogniser emitted/printed | Google emitted/printed | Human emitted/printed |
| --- | --- | --- | --- | --- | --- |
| 666 continuity instrument | apostrophe_elision | 213 | 212/213 (99.53%) | 212/213 (99.53%) | 212/213 (99.53%) |
| 666 continuity instrument | quote | 10 | 4/10 (40.00%) | 5/10 (50.00%) | 10/10 (100.00%) |
| (ii) mark-enriched, not a population estimate | apostrophe_elision | 2 | 2/2 (100.00%) | 2/2 (100.00%) | 0/0 (UNKNOWN) |
| (ii) mark-enriched, not a population estimate | quote | 0 | 0/0 (UNKNOWN) | 0/0 (UNKNOWN) | 0/0 (UNKNOWN) |
| (i-a) selection-exposed (v2 val) | apostrophe_elision | 9 | 9/9 (100.00%) | 3/9 (33.33%) | 9/9 (100.00%) |
| (i-a) selection-exposed (v2 val) | quote | 0 | 0/0 (UNKNOWN) | 0/0 (UNKNOWN) | 0/0 (UNKNOWN) |

| Stratum | Printed kind | Recogniser exact shape/available | Google exact shape/available | Human exact shape/available |
| --- | --- | --- | --- | --- |
| 666 continuity instrument | apostrophe_elision | 1/213 | 1/213 | 207/213 |
| 666 continuity instrument | quote | 2/10 | 3/10 | 3/10 |
| (ii) mark-enriched, not a population estimate | apostrophe_elision | 0/2 | 0/2 | 0/0 |
| (ii) mark-enriched, not a population estimate | quote | 0/0 | 0/0 | 0/0 |
| (i-a) selection-exposed (v2 val) | apostrophe_elision | 1/9 | 0/9 | 9/9 |
| (i-a) selection-exposed (v2 val) | quote | 0/0 | 0/0 | 0/0 |

No human full-line reference exists for (ii); 0/0 means unavailable. For the 666 apostrophes, recogniser and Google each emit 212/213, and human 212/213; most recogniser/Google emissions are straight ASCII apostrophes. Their exact-shape count is only 1/213, versus human 207/213. The one recogniser omission is `384c3f89-p000050-l0037`, where Google and human contain the printed elision. The 666 quote omissions are six sites, five also absent from Google and one with a correct Google quote. Presence and shape are different questions: **the data do not support “the recogniser never emits apostrophes.”**

The one unresolved typography site is excluded even though an overlapping S4 card proposes an apostrophe. There are no remaining contradictory resolved site joins. [Punctuation site evidence](R0_evidence/scoring/punctuation_sites.jsonl) contains every source emission, card ID and letter boundary; [rejected physical quote probes](R0_evidence/scoring/rejected_opening_quote_probes.jsonl) retain their component boxes.

## Span placement and historical mapping — R0a evidence retained

The historical R0a headline **998/25,437 = 3.9234% outside blob** is a diagnostic total over 666+(ii), retained only for continuity with the requested 3.92% line. Separate strata are below; it is not a pooled accuracy estimate. A clean slot owns one native connected component, no other character owns it, and its CTC centre is tested against the half-open native bbox. Blob assignment itself uses the runtime overlap rule, so this is not independent print truth for glyph identity.

| Stratum | All alphabetic slots | Clean | Outside | Outside % | Fused | Split | No letter blob |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 666 continuity instrument | 20422 | 19329 | 726 | 3.76% | 749 | 300 | 44 |
| (ii) mark-enriched, not a population estimate | 7112 | 6108 | 272 | 4.45% | 647 | 301 | 56 |
| (i-a) selection-exposed (v2 val) | 2777 | 2695 | 143 | 5.31% | 45 | 31 | 6 |

| Stratum | Dimension | Bucket | All slots | Clean | Outside | Outside % |
| --- | --- | --- | --- | --- | --- | --- |
| 666 continuity instrument | script_class | Latin | 42 | 38 | 1 | 2.63% |
| 666 continuity instrument | script_class | greek_poly | 19115 | 18108 | 666 | 3.68% |
| 666 continuity instrument | script_class | modern | 1265 | 1183 | 59 | 4.99% |
| 666 continuity instrument | size_bucket | 20-34px | 18482 | 17548 | 625 | 3.56% |
| 666 continuity instrument | size_bucket | <20px | 304 | 252 | 21 | 8.33% |
| 666 continuity instrument | size_bucket | >=35px | 1636 | 1529 | 80 | 5.23% |
| (ii) mark-enriched, not a population estimate | script_class | Latin | 389 | 328 | 7 | 2.13% |
| (ii) mark-enriched, not a population estimate | script_class | greek_poly | 6723 | 5780 | 265 | 4.58% |
| (ii) mark-enriched, not a population estimate | size_bucket | 20-34px | 1949 | 1622 | 62 | 3.82% |
| (ii) mark-enriched, not a population estimate | size_bucket | <20px | 5163 | 4486 | 210 | 4.68% |
| (i-a) selection-exposed (v2 val) | script_class | greek_poly | 2777 | 2695 | 143 | 5.31% |
| (i-a) selection-exposed (v2 val) | size_bucket | 20-34px | 2611 | 2546 | 128 | 5.03% |
| (i-a) selection-exposed (v2 val) | size_bucket | <20px | 40 | 34 | 8 | 23.53% |
| (i-a) selection-exposed (v2 val) | size_bucket | >=35px | 126 | 115 | 7 | 6.09% |

Geometry uses native cached predictions only. Greek/modern classification follows the saved line script; Latin is per character. Size uses the saved runtime x-height: <20, 20–34, ≥35 px. Fused, split and absent-blob cases are **diagnostic states, not automatically bad letters or bad physical print**. The full native slot ledgers and script × size/book tables remain [R0a span evidence](R0_evidence/span_summary.json) and [(i-a) span evidence](R0_evidence/ia/span_summary.json).

For the **666 continuity instrument**, the original R1 mapper still omits 715/11,329 scored frozen samples: 698 share a primary blob and 17 have no overlapping primary letter blob. Every one is `localisation_unknown=True` and lacks `component_slot`; the historical mapper refuses non-unique ownership. The separate R1 extractor supports 261 with one component owner, 448 with shared owners and six with no owners under its own windows. These are evaluation/mapping omissions, not 715 missing letters. Every original reason is preserved in [R1_unmapped_715.jsonl](R0_evidence/R1_unmapped_715.jsonl) and the final failure ledger.

## DATA / MODEL verdicts and training-track evidence

Each final ledger row has `DATA_MODEL`, a line ID, a slot with an explicit coordinate convention, prediction stream and evidence. Text errors use adjudicated print. **DATA** means the paired Google target is also wrong/missing at that error; **MODEL** means the paired Google target is correct, or the failure is runtime position/case mapping. These are evidence-backed routes for the training track, **not causal identification of which training example E3 consumed**. An observed held-out Google error is not proof that the same error was present in a consumed training row. Geometry cannot be attributed to text-label frequencies alone.

The exact `import_real_v2_train.jsonl` was read once as a stream: 214,436 rows, SHA-256 `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3`. Frequency evidence for every target letter and punctuation symbol is in [training_frequencies.json](R0_evidence/scoring/training_frequencies.json); per-error rows carry the relevant target frequency.

| Evidence scope / stratum | Symbol | Training occurrences | greek_poly occurrences | Implication |
| --- | --- | --- | --- | --- |
| all training label scripts (not an audit accuracy stratum) | ASCII ' / U+0027 | 5571 | 2908 | functional apostrophes present |
| all training label scripts (not an audit accuracy stratum) | ᾽ / U+1FBD | 4027 | 3736 | spacing-koronis convention well represented |
| all training label scripts (not an audit accuracy stratum) | ’ / U+2019 | 2 | 0 | curly printed form has essentially no polytonic target coverage |
| all training label scripts (not an audit accuracy stratum) | ‘ / U+2018 | 21 | 8 | opening-single-quote target is rare |
| all training label scripts (not an audit accuracy stratum) | “ / U+201C | 130 | 45 | curly double quote exists but is uncommon |
| all training label scripts (not an audit accuracy stratum) | Α / α | 29,471 / 882,246 | 13,664 / 571,413 | case and Greek alpha targets exist |
| all training label scripts (not an audit accuracy stratum) | Latin a | 39675 | 2 | mixed-script routing remains a reading problem where Google is correct |
| all training label scripts (not an audit accuracy stratum) | ſ | 1 | 0 | historical Latin long-s coverage is scarce; do not infer broad competence |

DATA training arm: correct demonstrably bad letter targets and missing/misencoded quotes; choose and consistently normalize the desired apostrophe representation before changing capacity. The existing apostrophe detector may propose corrections, but its rejected breathing probes show why pixel validation is needed. MODEL arm: evaluate letter identity, mixed-script reading and deletion recovery with correct targets, and address pixel-case/component/CTC localisation separately. More width might help reading; this audit supplies no measured width gain and does not establish model capacity as the cause. Leave locked strata out of all selection/tuning.

### Every observed type, with separate stratum counts and example IDs

Counts below are error/diagnostic slots, not unique lines. No stratum is pooled into an accuracy estimate. “Stored” includes the stored 666 instrument and the unchanged locked recognitions. Native variant errors and the DEV witness are in separate rows. Sparse subtypes have fewer than three observed lines; all actual IDs are shown. **The requested ≥3 distinct examples is not attainable for those sparse cells/types without inventing observations.** Their evidence is retained rather than suppressing or exaggerating them.

| Prediction stream / stratum scope | Type | Verdict | 666 continuity instrument | (ii) mark-enriched, not a population estimate | (i-a) selection-exposed (v2 val) | DEV excluded | Example line IDs with stratum |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S5_pixel_case | S5_pixel_case_wrong | MODEL | 160 | 0 | 0 | 0 | 666 continuity instrument: `0b7bf21d-p000001-l0005`; 666 continuity instrument: `0b7bf21d-p000001-l0012`; 666 continuity instrument: `0b7bf21d-p000002-l0005` |
| historical_S4_mapping | R1_frozen_mapping_omission | MODEL | 715 | 0 | 0 | 0 | 666 continuity instrument: `0b7bf21d-p000013-l0026`; 666 continuity instrument: `177b717d-p000013-l0002`; 666 continuity instrument: `177b717d-p000013-l0004` |
| native_cached | fused_multi_character_blob | MODEL | 749 | 647 | 45 | 0 | 666 continuity instrument: `0b7bf21d-p000013-l0026`; 666 continuity instrument: `177b717d-p000013-l0006`; 666 continuity instrument: `177b717d-p000013-l0009` |
| native_cached | no_letter_blob | MODEL | 44 | 56 | 6 | 0 | 666 continuity instrument: `0b7bf21d-p000003-l0001`; 666 continuity instrument: `22fda82b-p000013-l0006`; 666 continuity instrument: `22fda82b-p000013-l0007` |
| native_cached | span_outside_blob | MODEL | 726 | 272 | 143 | 0 | 666 continuity instrument: `0b7bf21d-p000002-l0004`; 666 continuity instrument: `0b7bf21d-p000013-l0026`; 666 continuity instrument: `177b717d-p000013-l0002` |
| native_cached | split_character_multi_blob | MODEL | 300 | 301 | 31 | 0 | 666 continuity instrument: `0b7bf21d-p000001-l0005`; 666 continuity instrument: `0b7bf21d-p000013-l0026`; 666 continuity instrument: `177b717d-p000013-l0005` |
| native_cached_variant | deletion | MODEL | 5 | 0 | 0 | 0 | 666 continuity instrument: `4ad622a4-p000001-l0002`; 666 continuity instrument: `69e993c1-p000008-l0007`; 666 continuity instrument: `69e993c1-p000008-l0010` |
| native_cached_variant | substitution | MODEL | 12 | 0 | 0 | 0 | 666 continuity instrument: `263438a3-p000005-l0001`; 666 continuity instrument: `4ad622a4-p000001-l0002`; 666 continuity instrument: `51fe7386-p000026-l0029` |
| stored_instrument | apostrophe_omission | MODEL | 1 | 0 | 0 | 0 | 666 continuity instrument: `384c3f89-p000050-l0037` (only 1 observed lines) |
| stored_instrument | apostrophe_shape | DATA | 211 | 2 | 8 | 0 | 666 continuity instrument: `177b717d-p000013-l0007`; 666 continuity instrument: `177b717d-p000013-l0008`; 666 continuity instrument: `177b717d-p000017-l0006` |
| stored_instrument | case | MODEL | 1 | 2 | 0 | 0 | 666 continuity instrument: `6b47791c-p000005-l0005`; (ii) mark-enriched, not a population estimate: `anemi--_metadata_6_2_f_metadata-352-0000000.tkl-23eeee17--000052-l0033` (only 2 observed lines) |
| stored_instrument | deletion | DATA | 1 | 4 | 0 | 0 | 666 continuity instrument: `69e993c1-p000108-l0009`; (ii) mark-enriched, not a population estimate: `bsb--8ae29ae07364--00446-l0095`; (ii) mark-enriched, not a population estimate: `bsb--b0643b33ea85--00565-l0092` |
| stored_instrument | deletion | MODEL | 21 | 58 | 1 | 0 | 666 continuity instrument: `263438a3-p000005-l0001`; 666 continuity instrument: `384c3f89-p000091-l0014`; 666 continuity instrument: `4ad622a4-p000001-l0002` |
| stored_instrument | insertion | DATA | 2 | 0 | 0 | 0 | 666 continuity instrument: `384c3f89-p000030-l0016` (only 1 observed lines) |
| stored_instrument | insertion | MODEL | 19 | 13 | 0 | 0 | 666 continuity instrument: `0b7bf21d-p000002-l0004`; 666 continuity instrument: `22fda82b-p000052-l0032`; 666 continuity instrument: `384c3f89-p000030-l0016` |
| stored_instrument | quote_omission | DATA | 5 | 0 | 0 | 0 | 666 continuity instrument: `0b7bf21d-p000002-l0004`; 666 continuity instrument: `384c3f89-p000030-l0023`; 666 continuity instrument: `384c3f89-p000030-l0029` |
| stored_instrument | quote_omission | MODEL | 1 | 0 | 0 | 0 | 666 continuity instrument: `384c3f89-p000030-l0010` (only 1 observed lines) |
| stored_instrument | quote_shape | DATA | 2 | 0 | 0 | 0 | 666 continuity instrument: `384c3f89-p000030-l0025`; 666 continuity instrument: `384c3f89-p000142-l0003` (only 2 observed lines) |
| stored_instrument | script_mixup | DATA | 0 | 2 | 0 | 0 | (ii) mark-enriched, not a population estimate: `bsb--b0643b33ea85--00565-l0092` (only 1 observed lines) |
| stored_instrument | script_mixup | MODEL | 3 | 31 | 0 | 1 | 666 continuity instrument: `177b717d-p000030-l0004`; 666 continuity instrument: `263438a3-p000001-l0005`; 666 continuity instrument: `384c3f89-p000030-l0009` |
| stored_instrument | spurious_apostrophe_or_quote | MODEL | 1 | 2 | 5 | 0 | 666 continuity instrument: `384c3f89-p000030-l0032`; (ii) mark-enriched, not a population estimate: `government-gazette--19800201000-da54f14b--000009-l0080`; (ii) mark-enriched, not a population estimate: `operaeusebius02euseuoft--n93-l0032` |
| stored_instrument | substitution | DATA | 1 | 0 | 0 | 0 | 666 continuity instrument: `69e993c1-p000008-l0004` (only 1 observed lines) |
| stored_instrument | substitution | MODEL | 58 | 42 | 1 | 0 | 666 continuity instrument: `0b7bf21d-p000002-l0004`; 666 continuity instrument: `0b7bf21d-p000002-l0005`; 666 continuity instrument: `177b717d-p000041-l0007` |

The stored-stream letter totals route **4 DATA / 102 MODEL** errors for the 666 continuity instrument, **6 DATA / 146 MODEL** for (ii), and **0 DATA / 2 MODEL** for (i-a). For example, the weak historical-Latin targets `auch`, `ſ`, and `b` are not grounds to claim all mixed-script errors need a wider model. Conversely, correct paired Google targets and abundant target-letter frequencies support the MODEL route for the bulk of measured letter failures.

## Locked-set scope and exposure

(ii) remains 200 lines / 11 sources from the seeded 20261017 M2 split; 273 measured cards remain DEV. Its explicit polytonic-mark selection makes it **mark-enriched, not a population estimate**. M2 was previously used for S7 qualification; freezing cannot undo that exposure. (i-a) remains 133 lines / three books, with 122 from Ἀστέρια. Its 131/133 collection-v2-val overlap means **selection-exposed (v2 val)**. It is reported beside, never pooled with, the other strata. The coming clean (i-b) is not measured here.

Frozen receipts retain zero line/document/normalized-stem overlap with 666, detector DEV and L1 input, and zero (i-a)/(ii) overlap; crop-hash checks are also retained. (ii), new-source DEV and the 666+DEV instrument have zero v2-val overlap. Locked strata are never used for training, threshold/policy/checkpoint selection or tuning. See [IA freeze receipt](R0_locked_set_receipt.json), [new-source split receipt](R0_newsource_split_receipt.json), [IA exclusion IDs](R0_locked_ia_ids.txt) and [(ii) exclusion IDs](R0_newsource_exclusion_ids.txt).

## Review page, validation and reproduction

[R0_review_failures.html](R0_review_failures.html) contains exactly 60 distinct lines, all observed failure categories and all strata, plus the DEV witness. Each row has its line ID/stratum, full crop, thin native CTC letter-span boxes and letter labels, Google line, native recogniser line, stored line when different, card truth scopes and one note placeholder with local autosave/export. It is written locally; **the track lead publishes it**. Geometry badges identify diagnostics rather than certifying text errors.

Machine checks verify source/truth/cache hashes unchanged, disjoint word windows, independent edit-count agreement, the 160-card case join, UNKNOWN exclusions, all 60 embedded PNGs and SVG span counts, single note fields, no external page resources and JavaScript syntax. Browser visual/interaction QA is **unverified**: the cached headless Firefox build aborts in this sandbox, and computer-use access to Firefox was not approved. No browser download or publication was attempted. Native card images were inspected for the clipped UNKNOWN and distinct opening-quote versus breathing probes; this is not browser layout proof.

Launch head `661bae240c2e8c5458df45fb8bf7e2086faf91fa` on `opus/spellcheck-r0`. Local Mac CPU, network off, zero new CTC forwards, no model/detector changes and no `.git` mutation commands. [Validation receipt](R0_evidence/scoring/validation.json), [machine metrics](R0_metrics.json), [per-failure ledger](R0_failures.jsonl), [original R0a/R0a2 report snapshot](R0_evidence/scoring/R0a_REPORT_snapshot.md).

Reproduce with the specified venv Python and `PYTHONPATH=$PWD`, `PYTHONDONTWRITEBYTECODE=1`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `GIT_OPTIONAL_LOCKS=0`: run `scripts/labelfix/r0_score.py`, `scripts/labelfix/r0_score_validate.py`, then `scripts/labelfix/r0_score_report.py`. These scripts neither forward crops nor change runtime/model data.

R0 RESULT: letter truth 2376 slots/361 lines (word-card scopes; 0 full lines certified); letter error 6.50% (case-folded 6.43%) on 666 continuity instrument, (ii) 24.56% (24.23%; mark-enriched, not a population estimate), (i-a) 1.60% (1.60%; selection-exposed (v2 val)), all on adjudicated word cards only; spans outside blob 3.92% (historical 666+(ii) diagnostic); case disagreements recogniser right 100.00% (160/160; stratified extrapolation 753/753); apostrophes emitted 99.53% of printed on 666 (212/213; (ii) 2/2, (i-a) 9/9); DATA types letter-label errors, apostrophe/quote representation and missing quote labels; MODEL types letter substitution/insertion/deletion/case/script, punctuation reading, S5 pixel case, CTC span/component localisation and frozen R1 mapping.


## R0a3 — clean locked Wikisource stratum (i-b)

Frozen **400 complete polytonic lines / 5 books**, seed 20261017. Eligible pool: 1127 / 1,246 harvest lines; the R0a one-to-one human alignment, whole-crop and NFD polytonic admission rules are unchanged. Proportional largest-remainder quotas, stable line-ID order and seeded sampling were reproduced; no model output influenced admission.

| Book hash | Eligible | Drawn |
|---|---:|---:|
| 45855dfb | 100 | 36 |
| a3114593 | 107 | 38 |
| bf4f6c1b | 133 | 47 |
| df94dc99 | 445 | 158 |
| e90ad4c2 | 342 | 121 |

Maximum share **39.5%**. [Frozen lines](R0_locked_ib.jsonl), [IDs](R0_locked_ib_ids.txt), [receipt](R0_locked_set_receipt.json), [input bindings](R0_evidence/ib/input_binding.json). Existing (i-a) receipt fields and its selection-exposed v2-val warning are preserved.

| Intersection against | Comparison rows | Matching rows / books |
|---|---:|---:|
| continuity_666 | 666 | 0 |
| DEV | 598 | 0 |
| L1_input_documents | 318 | 0 |
| stratum_ii | 200 | 0 |
| stratum_ii_development | 273 | 0 |
| stratum_ia | 133 | 0 |
| local20_books | 20 | 0 |
| collection_v2_val | 13522 | 0 |
| collection_v2_train | 214436 | 0 |
| collection_v2_test | 44029 | 0 |

Checks use exact and prefix-normalized line IDs, document IDs, and the bare book hashes in **both `id` and `doc`**; all three v2 files were independently streamed. Crop hashes are also disjoint from 666, DEV, (ii), (ii)-development and (i-a). L1 input and local20 are document/book inventories; no crop-equivalence claim is made for them or v2. These checks cannot identify undocumented copies/editions. [Full intersection receipts](R0_evidence/ib/locked_receipt.json).

**Never tune:** (i-b) judges L1 and wave 1c; never use it for training or policy/checkpoint/threshold selection. Keep selection-exposed (i-a) separate. The 666 remain the continuity instrument. All 1,246 harvest rows remain subject to the sourcing lead’s release exclusion; this task does not alter that manifest.

Google labels come from the harvest `pages.jsonl` Google geometry line text, indexed by the recorded Google line index and checked against `alignment.google_text` and the Google bbox. Human labels come from `lines.jsonl`; literal and NFC fields are retained, with NFD used for processing. Human reference wording is not established print truth.

**400 E3 full_s0 CPU forwards**, only on the frozen crops, unchanged `Recognizer.align_paths`/`masked_forward`; four threads, batches of 16. [Alignment receipt](../../../../.cache/labelfix/r0/align_locked_ib.receipt.json). Native span census: **420 / 9055 clean one-blob/one-character alphabetic slots = 4.6383% outside blob**; 10352 alphabetic slots censused in total. The clean-slot rate is a geometry diagnostic using runtime CTC-overlap ownership, not independent glyph identity or a letter error rate. Nonclean slots, marks, spaces and punctuation remain explicitly counted. [Summary by script, size and book](R0_evidence/ib/span_summary.json), [all slots](R0_evidence/ib/span_slots.jsonl.gz), [line census](R0_evidence/ib/span_line_census.jsonl).

R1-A production checkpoint `719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636` ran on CPU with the **unchanged R1 full-height extraction**: 5807 / 5807 vowel/rho windows (100.00% coverage), no training or extra CTC. Unscored windows stay UNKNOWN. S6 uses the unchanged raw `read_ink` detector, S4 markshape asset, no filtering/constraints or geometry substitutions, and no Google/human input. [Extraction](R0_evidence/ib/r1_extraction/extraction_receipt.json), [R1 inference](R0_evidence/ib/r1_inference_receipt.json), [S6 receipt](R0_evidence/ib/s6_receipt.json).

The [mixed blind deck](R0_cards_ib/index.html) contains **157 LETTER + 151 MARK adjudication cards**, plus **14 letter + 14 mark planted controls** (8.33% overall). Mark coverage includes all 86 differing word groups and 63 groups with unnamed/unlocalised detector marks or unscored R1 windows; groups can overlap. 1 word group requires two panels to cover all four distinct source forms without exceeding three candidates per card. The recogniser locates MARK windows only; its marks never vote or supply mark candidates. Combining-mark forms use all four sources with elision signs removed from every candidate; separate elision cards use Google/human/S6 only because R1-A has no apostrophe head. Candidate order and item order are seeded and shuffled, source/control labels and kinds stay in the private IB key, zooms are at most 3x, and every card includes the full native line. Controls were read against pixels before planting a single letter or mark change. [Plan/coverage receipt](R0_evidence/ib/combined_plan_receipt.json), [card receipt](R0_evidence/ib/cards_receipt.json), [validation](R0_evidence/ib/validation.json).

**Print truth remains PENDING:** two independent readers and pixel tiebreak are required. Difference cards alone do not establish full-line truth or eliminate shared errors; no mark/letter accuracy is claimed here. Blank [reader slots](R0_expected_truth_ib.json) and [line truth placeholders](R0_line_truth_placeholders_ib.jsonl) are supplied. Runtime, checkpoints, shared alignment caches, harvest inputs and existing IA receipt fields were verified unchanged. Network stayed off; no Git mutation was used. Representative final zooms/full lines and every planted control were visually inspected; all full-line images are native-pixel identical. Viewer JavaScript syntax and DOM interactions were checked locally. Browser render QA was unavailable (empty browser inventory; in-app browser unavailable), so no browser-render claim is made.

R0a3 READY: stratum (i-b) 400 lines / 5 books (45855dfb 36, a3114593 38, bf4f6c1b 47, df94dc99 158, e90ad4c2 121); zero overlap with 666, DEV, L1 input, (ii), (i-a), local books, v2 val; cards 308 (+controls 28); spans outside blob 4.6383%

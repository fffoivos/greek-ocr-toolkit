# N1TR-F2: final n1_v1_train

Finalized offline with `scripts/numerics/n1tr_finalize.sh --apply-lead`, followed by `scripts/numerics/n1tr_f2.py` to expose resolved dash tags and separate resolved baseline dots from HOLDs. The sealed finalizer, build inputs, review binding, keys and original decisions are unchanged. No new reading, image inspection, browser/computer use, network operation or `.git` write was performed in F2. The earlier preparation-only statements below are historical.

**Finding:** among the **474 localised candidate slots** in the v2 train rows, agreed reads found **83 hyphens/dashes, 215 baseline dots and 0 confirmed raised dots** after lead adjudication. The two provisional raised agreements were rejected by the supplied lead pixel rulings: cell 1 `69846639273a60b797e93cb9-p000219-l0023` has the printed hyphen in range `100-300`; cell 2 `39fbbdfd2c8030f211a318b7-p000138-l0012` has the printed hyphen in page range `433-444`. Both template entries record `pixel_checked: true`, `printed: "hyphen"`, and Google text unchanged. The 83 agreed dash reads exclude these two lead-resolved hyphens, giving **85 final dash tags** (55 hyphens, 6 en dashes, 24 em dashes).

The raised-thousands-dot fault is concentrated in **ELSTAT-type tables, which are not in the v2 train rows**. This supplied lead finding is consistent with the absence of any confirmed raised dot here; the conservatively localised subset does not establish absence in the unlocalised population.

The final artifact retains **214,436 rows**, with **0 edits** and every label unchanged. The 2,923 candidate slots partition into 85 dash tags, 215 resolved unchanged baseline dots, and **2,623 HOLDs**: 2,449 unlocalised positions, 158 positions from VOID/invalid contexts, and 16 unresolved disagreements/unreadable pairs. `ctx01/r1` and `ctx01/r2` are VOID (two viewed control errors each); `ctx04/r2` is INVALID (unclean canonical v4.4 scan). These positions stay held even where a grammar range reason takes precedence in the original decision. All per-slot reads, confidence, context status, rollout hashes, offsets and original decision/reason are retained. No invalid or VOID vote resolves a slot.

Release artifacts:

- [n1_v1_train.jsonl](../../../../artifacts/n1/n1_v1_train.jsonl), SHA-256 `0b32e8d9b04383cc8fe5542b0b40ccfa47978c5cd09b36c1a535083f0b41bf92`.
- [Manifest](../../../../artifacts/n1/n1_v1_train_manifest.json) and [SHA sidecar](../../../../artifacts/n1/n1_v1_train.sha256).
- [Final receipt](../../../../artifacts/n1/n1tr/FINALIZED_RECEIPT.json) and [full-stream validation](../../../../artifacts/n1/n1tr/F2_VALIDATION.json).
- [LQB registry](../lqb/versions.json): `n1_v1_train` registered under `collection_v2_train` with matching hash.
- [LQB re-score](../../../../artifacts/n1/n1tr/lqb_rescore.json): frozen `truth_v1_1`, parent and final version summaries identical, paired error counts identical. The paired N1 separator sample has **0 items** and no measurable delta; this score is not evidence of a separator improvement.

Validation checked the full parent/output streams in order: identical row count, IDs, every original field and label; zero edits; exact slot coverage with no duplicates; original read provenance and parent offsets preserved; and output/parent/lead/build/decisions/re-score hash bindings matching the manifest and registry.

# Historical N1TR preparation record

Prepared offline; **no reads, account probes, browser/computer use, network calls, production finalisation, LQB registration or re-score were executed**. The driver and finaliser are implemented and tested on fixtures. The ink rule remains failed at 0/5 and is never consulted for edits.

The parent contains **214,436 rows** (SHA-256 `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3`). Tokenisation finds **2,936 raw slots**; 13 excluded slots leave **2,923 eligible candidates**: 1,022 hyphens and 1,901 periods. All release-exclusion classes and N1 reserved document/line locks are bound by hash. Exclusions are applied before localisation. Approved controls are a separate, already adjudicated population; candidate exclusion IDs are never admitted as bed items.

**Coverage limitation:** only **474/2,923 slots (16.22%)** could be localised conservatively. All **2,449 remaining slots are explicit HOLDs**, listed with offsets, source/document identity and failure reason in `artifacts/n1/n1tr/unlocalised.jsonl`. They are not silently dropped, guessed, or placed in reading packs. The finaliser preserves every candidate as an edit or hold.

## Localisation and packs

V2 train rows do not supply per-slot symbol geometry in this population. The preparer accepts saved per-slot geometry when supplied; otherwise it uses the existing `line_glyphs` native mask and `n1_render.render` helper. Crop hashes are checked against `admitted_all_v2.jsonl`. Localisation requires a unique whitespace-word partition, an all-numeric word, exactly one horizontal ink run per visible character, and adequate digit flank heights. Touching/fragmented digits, mixed words and ambiguous partitions remain unlocalised. No new OCR/model reading is used. This deliberately conservative method does not claim full physical coverage.

| Unlocalised reason | Slots |
|---|---:|
| character_run_count_differs | 832 |
| digit_fragment_or_band_mismatch | 42 |
| mixed_or_non_numeric_word | 1256 |
| word_partition_ambiguous | 319 |

Six contexts contain 79 candidate slots + 9 approved controls each (88 items, 10.23% controls), each with at least one raised-dot control. R2 is the exact reverse, with disjoint opaque IDs and a fresh derangement of all ten sep2 options. Keys live only in `artifacts/n1/n1tr/keys/`. All 12 packs have sealed manifests and passing closure checks. Pack root: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/n1tr`. The in-repo root guard is active.

The current packs plan **1,056 reads / 2.112 points**, using 0.2 points per 100 reads. This cost covers the localised subset. If every eligible slot later became localisable with the same packing policy, 37 contexts ×2 and 6,512 reads would cost **13.024 points**. This hypothetical full-population estimate is not a queued run.

## Driver and finaliser

Explicit later operator invocation:

```sh
scripts/secondary/reading/run_n1tr_all.sh --dry-run
# Launch only when separately instructed:
scripts/secondary/reading/run_n1tr_all.sh
```

The driver validates all bound inputs, keys and sealed packs, locks itself, probes before every context, and stops at weekly usage ≥70% with `STOPPED_AT_70.json`. A permanent attempt claim precedes launch; failed or interrupted contexts never rerun. It also probes after each context and records usage. The existing launch helper pins gpt-6.1-sol, medium effort, network off, web disabled and multi-agent/apps disabled. Dry-run performs no probes or reads. The 12-context dry-run transcript is `artifacts/n1/n1tr/driver_dry_run.jsonl`.

```sh
scripts/numerics/n1tr_finalize.sh
# Fill scratchpad/n1_review/n1tr/lead_template.jsonl after pixel review.
scripts/numerics/n1tr_finalize.sh --apply-lead
```

The first invocation re-scans actual rollouts with canonical v4.4, verifies model/effort and independent rollout hashes, decodes sep2 answers, and gates viewed controls. More than one viewed control error, an unseen/incorrect raised control, or fewer than two viewed controls makes the context VOID. Line or zoom views qualify; derived images qualify only through the existing command-ancestry tracer at the time of a matched view. Unviewed items contribute no usable vote. Missing, malformed or invalid contexts become per-slot holds with provenance. An unattempted context requires the explicit 70% stop marker for partial finalisation.

Only two valid r1/r2 raised-dot votes can reach lead review. Every such slot, including range proposals, gets a cell and a template row. Sheets show the target zoom, line, parent text/offset, and available same-document raised references. Approved references are labelled as approved; peer two-read references are labelled unadjudicated. Where no same-document reference exists, the sheet and index explicitly record UNAVAILABLE rather than substitute another document or invent truth. Actual reference availability cannot be known until the reads exist. No production lead sheet has been fabricated during preparation.

`--apply-lead` requires exactly the agreed raised slots, `pixel_checked: true`, a completed `printed` value, and unchanged review/image hashes. It changes only one existing `-` or `.` to U+00B7. Tokenizer range proposals are conservatively vetoed even after raised agreement; lead range rulings also hold. Every disagreement, unreadable/other call, nonraised agreement, VOID, invalid/missing read and unlocalised slot holds. Confidence remains in provenance; the requested two-valid-read rule does not add a high-confidence threshold.

The production apply step writes `artifacts/n1/n1_v1_train.jsonl` with the original row, `parent_label`, `new_label`, `label`, `edits`, `holds` and `slot_provenance`; then a manifest and SHA. The full parent population is retained, including in partial mode. It computes a paired LQB re-score against frozen truth and registers `n1_v1_train` under `collection_v2_train` only after scoring succeeds. Manifest and registry identify partial outputs explicitly. None of these production output actions were run here.

## Validation

**33 N1TR fixture tests passed; 90 tests plus 24 subtests passed including RU2T/RU3T regressions.** XML receipts: `artifacts/n1/N1TR_FINALIZER_TESTS.xml` and `artifacts/n1/N1TR_TESTS.xml`. Coverage includes actual canonical scan fixtures, direct/derived image ancestry, model mismatch, rollout reuse, malformed answers, control errors/VOID, reverse/fresh packs, tamper rejection, numeric localisation, range protection, lead enforcement, one-character application, stop-at-70, crash/retry prevention, partial output/registration and a complete staged lead/apply fixture. No visual correctness claim is inferred from these synthetic tests.

## Counts by source

| Source | Candidates | Localised | Unlocalised |
|---|---:|---:|---:|
| anemi_mixed | 22 | 6 | 16 |
| anemi_round1 | 133 | 27 | 106 |
| anemi_round2 | 111 | 33 | 78 |
| archive_b28038630 | 191 | 0 | 191 |
| archive_bub_gb_Cmg6AQAAIAAJ | 21 | 4 | 17 |
| archive_bub_gb_mG0mAQAAIAAJ | 16 | 7 | 9 |
| archive_izvestiianabul25192530bul | 18 | 2 | 16 |
| archive_izvestiianabulga610193138bulg | 8 | 2 | 6 |
| archive_izvestiianatsars12192829tsar | 10 | 7 | 3 |
| archive_izvestiianatsars1516194243tsar | 7 | 0 | 7 |
| archive_sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930 | 14 | 3 | 11 |
| openarchives_Dione | 38 | 17 | 21 |
| openarchives_KEIED | 29 | 8 | 21 |
| openarchives_Pandemos | 37 | 14 | 23 |
| openarchives_anaktisis | 19 | 16 | 3 |
| openarchives_apothesis | 24 | 15 | 9 |
| openarchives_hellanicus | 51 | 23 | 28 |
| openarchives_kallipos | 30 | 13 | 17 |
| openarchives_ktisis | 19 | 10 | 9 |
| openarchives_mixed_Dione | 17 | 3 | 14 |
| openarchives_mixed_KEIED | 87 | 3 | 84 |
| openarchives_mixed_Pandemos | 3 | 2 | 1 |
| openarchives_mixed_anaktisis | 7 | 0 | 7 |
| openarchives_mixed_apothesis | 68 | 12 | 56 |
| openarchives_mixed_hellanicus | 23 | 10 | 13 |
| openarchives_mixed_ktisis | 7 | 0 | 7 |
| openarchives_nemertes | 18 | 5 | 13 |
| openarchives_ntua | 26 | 11 | 15 |
| parliament_proceedings_1975_2000 | 1831 | 215 | 1616 |
| vouli_parliament_1850s | 38 | 6 | 32 |

## Counts by source/era

Era uses supplied v2 year metadata in 50-year bins; these are metadata groupings, not newly verified publication dates.

| Source / era | Candidates |
|---|---:|
| anemi_mixed:1850-1899 | 16 |
| anemi_mixed:1900-1949 | 6 |
| anemi_round1:1850-1899 | 25 |
| anemi_round1:1900-1949 | 108 |
| anemi_round2:1850-1899 | 12 |
| anemi_round2:1900-1949 | 99 |
| archive_b28038630:1850-1899 | 191 |
| archive_bub_gb_Cmg6AQAAIAAJ:1900-1949 | 21 |
| archive_bub_gb_mG0mAQAAIAAJ:1850-1899 | 16 |
| archive_izvestiianabul25192530bul:1900-1949 | 18 |
| archive_izvestiianabulga610193138bulg:1900-1949 | 8 |
| archive_izvestiianatsars12192829tsar:1900-1949 | 10 |
| archive_izvestiianatsars1516194243tsar:1900-1949 | 7 |
| archive_sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930:1900-1949 | 14 |
| openarchives_Dione:1900-1949 | 22 |
| openarchives_Dione:1950-1999 | 8 |
| openarchives_Dione:2000-2049 | 8 |
| openarchives_KEIED:1900-1949 | 27 |
| openarchives_KEIED:1950-1999 | 2 |
| openarchives_Pandemos:1900-1949 | 6 |
| openarchives_Pandemos:1950-1999 | 22 |
| openarchives_Pandemos:2000-2049 | 9 |
| openarchives_anaktisis:2000-2049 | 19 |
| openarchives_apothesis:2000-2049 | 24 |
| openarchives_hellanicus:1850-1899 | 2 |
| openarchives_hellanicus:1900-1949 | 9 |
| openarchives_hellanicus:2000-2049 | 40 |
| openarchives_kallipos:2000-2049 | 30 |
| openarchives_ktisis:2000-2049 | 19 |
| openarchives_mixed_Dione:2000-2049 | 17 |
| openarchives_mixed_KEIED:1900-1949 | 1 |
| openarchives_mixed_KEIED:1950-1999 | 24 |
| openarchives_mixed_KEIED:2000-2049 | 62 |
| openarchives_mixed_Pandemos:2000-2049 | 3 |
| openarchives_mixed_anaktisis:2000-2049 | 7 |
| openarchives_mixed_apothesis:2000-2049 | 68 |
| openarchives_mixed_hellanicus:1950-1999 | 7 |
| openarchives_mixed_hellanicus:2000-2049 | 16 |
| openarchives_mixed_ktisis:2000-2049 | 7 |
| openarchives_nemertes:2000-2049 | 18 |
| openarchives_ntua:1850-1899 | 2 |
| openarchives_ntua:1900-1949 | 12 |
| openarchives_ntua:1950-1999 | 1 |
| openarchives_ntua:2000-2049 | 11 |
| parliament_proceedings_1975_2000:1950-1999 | 1831 |
| vouli_parliament_1850s:1800-1849 | 4 |
| vouli_parliament_1850s:1850-1899 | 31 |
| vouli_parliament_1850s:unknown | 3 |

N1TR READY: candidates 2923 (by source anemi_mixed 22, anemi_round1 133, anemi_round2 111, archive_b28038630 191, archive_bub_gb_Cmg6AQAAIAAJ 21, archive_bub_gb_mG0mAQAAIAAJ 16, archive_izvestiianabul25192530bul 18, archive_izvestiianabulga610193138bulg 8, archive_izvestiianatsars12192829tsar 10, archive_izvestiianatsars1516194243tsar 7, archive_sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930 14, openarchives_Dione 38, openarchives_KEIED 29, openarchives_Pandemos 37, openarchives_anaktisis 19, openarchives_apothesis 24, openarchives_hellanicus 51, openarchives_kallipos 30, openarchives_ktisis 19, openarchives_mixed_Dione 17, openarchives_mixed_KEIED 87, openarchives_mixed_Pandemos 3, openarchives_mixed_anaktisis 7, openarchives_mixed_apothesis 68, openarchives_mixed_hellanicus 23, openarchives_mixed_ktisis 7, openarchives_nemertes 18, openarchives_ntua 26, parliament_proceedings_1975_2000 1831, vouli_parliament_1850s 38), unlocalised 2449; contexts 6 ×2; est 2.112 pts; closure ok; driver dry-run ok; finalizer tests 33 passed


N1TRF2 READY: n1_v1_train rows 214436; edits 0; tags 85; holds 2623; sha256 0b32e8d9b04383cc8fe5542b0b40ccfa47978c5cd09b36c1a535083f0b41bf92; LQB registered ok

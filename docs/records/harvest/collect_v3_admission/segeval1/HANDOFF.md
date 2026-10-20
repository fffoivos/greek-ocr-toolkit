# SEGEVAL-1 blind evaluation handoff

Prepared 19 October 2026. **150 unseen study lines; no reads launched; no accuracy conclusion yet.** Two independent contexts each contain 75 study cards plus five approved controls (80 cards per context). No stratification was used. The owner decides whether observed false positives are small enough; no numerical proceed threshold is invented.

## Population and exact policy

The completed published `census_02/census/decisions.jsonl` generation is `g1-1c775230225d4bbea5871d4fae2475da`. Read-only SSH streamed the export and original parent metadata; no remote files, databases, jobs or filters were changed. All 592,466 rows have a segmentation stage. Parent scope includes original-v2 train/dev/test and W1/W2, including held-out cohorts for this diagnostic only. No train release is produced.

Export SHA256: `568d4759257787086ee8c0780cd0d4cf633c5ebf7b355d519d6053ff8c42764a` (8,168,706,501 bytes). Full source receipt and frozen parent hashes are in `draw_receipt.json`; the lossless reduced decision inventory is `keys/pipeline_population.jsonl.gz`. Every selected decision retains parent, crop hash, raw-text hash, run binding, toolchain digest, verdict and verbatim reason.

Exact recorded identity: segmentation **0.5**, `policy_sha256=8334dd4028822edbd740a1a96a0ead6367c7af953e545bad8bd60a911c65a819`; run binding `9350d138c83c494a429bcb1a811266be6d1879a4b1a711ce740b02031eed5a07`; toolchain digest `25e84c656ab1d1f32144c1916bb1f384acaeb787eef8cc781ca4555b1c1870b7`. The worktree frozen `segmentation-policy.js` has that same hash. Its selected defaults are OCR output ratio 0.5–1.5, prediction mode 2, at most 2 whole neighbour words, no second complete line, and combined vertical padding at most 1.5 target-line heights. Orientation and unavailable/unresolved geometry can return UNCERTAIN. These are the exported decisions, not a recomputation of historical merged/neighbour/orientation screens.

**Population interpretation:** REJECT means explicit segmentation `DROP`, ACCEPT means segmentation `KEEP`, regardless of subsequent tool dispositions. Segmentation `UNCERTAIN` becomes pipeline `HOLD`, so it is reported separately and is not silently called DROP or ACCEPT. This is a material scope boundary: the 150-line draw does not estimate false positives among unresolved/HOLD rows. The export has no blanket geometry-unavailable DROP substitution. `unresolved_population.json` gives exact reasons (including 77 rows with no usable text box before exclusions).

Before exclusions: DROP 17,036; KEEP 423,499; UNCERTAIN 151,931. Exclusions match 7844 evaluated rows from 8399 unique exclusion IDs. After exclusions: **REJECT 16,736; ACCEPT 416,241; separate UNCERTAIN/HOLD 151,645**.

Exclusions include the calibration ledger KEEP/DROP/witness IDs, all C1 keys, W2C1 card keys/inventories, both CP7 fresh-100 draws and controls, and owner segmentation/failure-mode sheets and actual cardmap/labelmap mappings. `keys/exclusion_sources.json` records every source path, SHA256 and ID count; `keys/excluded_ids.txt` records the union. The owner-sheet labelmap text/gtext dictionaries are population text inventories, so only its cardmap is an exclusion source. No complete population or unseen sampling pool is mistaken for reviewed cards.

### Pools after exclusion, source × class

Class is the saved `primary_class` for W1/W2; original-v2 lacks that field and uses its saved `script_class` (shown directly below).

| Source | Class | REJECT (DROP) | ACCEPT (KEEP) | UNCERTAIN/HOLD |
|---|---|---:|---:|---:|
| anemi_mixed | greek_latin_cs | 10 | 534 | 188 |
| anemi_mixed | greek_mono | 12 | 439 | 69 |
| anemi_mixed | greek_poly | 228 | 7798 | 6973 |
| anemi_mixed | latin | 4 | 800 | 205 |
| anemi_round1 | greek_latin_cs | 33 | 466 | 476 |
| anemi_round1 | greek_mono | 75 | 1312 | 141 |
| anemi_round1 | greek_poly | 591 | 27930 | 26134 |
| anemi_round1 | latin | 10 | 786 | 259 |
| anemi_round2 | greek_latin_cs | 6 | 234 | 169 |
| anemi_round2 | greek_mono | 10 | 623 | 29 |
| anemi_round2 | greek_poly | 263 | 11195 | 9634 |
| anemi_round2 | latin | 1 | 634 | 330 |
| archive_AA9613308335D0B014B | cyrillic | 7 | 1620 | 85 |
| archive_b24878935 | cyrillic | 0 | 981 | 68 |
| archive_b24878935 | latin | 0 | 133 | 11 |
| archive_b28038630 | greek_latin_cs | 0 | 854 | 1740 |
| archive_b28038630 | greek_mono | 0 | 56 | 3 |
| archive_b28038630 | greek_poly | 0 | 64 | 33 |
| archive_b28038630 | latin | 1 | 2390 | 4524 |
| archive_b29337124 | cyrillic | 0 | 154 | 65 |
| archive_bub_gb_Cmg6AQAAIAAJ | cyrillic | 3 | 960 | 542 |
| archive_bub_gb_Cmg6AQAAIAAJ | latin | 0 | 23 | 3 |
| archive_bub_gb_mG0mAQAAIAAJ | cyrillic | 1 | 1543 | 6 |
| archive_bub_gb_mG0mAQAAIAAJ | latin | 0 | 8 | 0 |
| archive_izvestiianabul25192530bul | cyrillic | 1 | 1155 | 183 |
| archive_izvestiianabul25192530bul | latin | 0 | 89 | 10 |
| archive_izvestiianabulga610193138bulg | cyrillic | 4 | 933 | 192 |
| archive_izvestiianabulga610193138bulg | latin | 3 | 81 | 12 |
| archive_izvestiianatsars1112193839tsar | cyrillic | 0 | 177 | 0 |
| archive_izvestiianatsars1112193839tsar | latin | 0 | 32 | 0 |
| archive_izvestiianatsars12192829tsar | cyrillic | 0 | 707 | 6 |
| archive_izvestiianatsars12192829tsar | latin | 0 | 70 | 0 |
| archive_izvestiianatsars1516194243tsar | cyrillic | 0 | 830 | 129 |
| archive_izvestiianatsars1516194243tsar | latin | 0 | 45 | 4 |
| archive_izvestiianatsars910193637tsar | cyrillic | 0 | 409 | 14 |
| archive_izvestiianatsars910193637tsar | latin | 0 | 25 | 1 |
| archive_sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930 | cyrillic | 73 | 1390 | 112 |
| bsb_poly1850 | cyrillic | 1 | 8 | 1 |
| bsb_poly1850 | dialogue_fiction | 0 | 353 | 1 |
| bsb_poly1850 | greek_mono | 15 | 500 | 13 |
| bsb_poly1850 | headings_caps | 22 | 66 | 3 |
| bsb_poly1850 | latin | 185 | 11422 | 197 |
| bsb_poly1850 | mixed_greek_latin | 32 | 3607 | 96 |
| bsb_poly1850 | nonletter | 98 | 63 | 8 |
| bsb_poly1850 | numerics_tables | 63 | 1653 | 144 |
| bsb_poly1850 | poly1850 | 45 | 13700 | 42 |
| elstat | dialogue_fiction | 3 | 69 | 5 |
| elstat | headings_caps | 140 | 64 | 51 |
| elstat | latin | 115 | 2409 | 218 |
| elstat | leaders_indices | 0 | 1 | 0 |
| elstat | mixed_greek_latin | 20 | 544 | 22 |
| elstat | modern_scanned | 17 | 1025 | 53 |
| elstat | nonletter | 5 | 51 | 103 |
| elstat | numerics_tables | 535 | 12057 | 918 |
| elstat | poly1900 | 7 | 807 | 38 |
| gazette_modern | cyrillic | 22 | 29 | 52 |
| gazette_modern | dialogue_fiction | 275 | 6422 | 199 |
| gazette_modern | headings_caps | 3091 | 14786 | 4371 |
| gazette_modern | latin | 380 | 1048 | 682 |
| gazette_modern | leaders_indices | 0 | 17 | 0 |
| gazette_modern | mixed_greek_latin | 162 | 1220 | 137 |
| gazette_modern | modern_scanned | 2916 | 65978 | 6250 |
| gazette_modern | nonletter | 1176 | 877 | 1098 |
| gazette_modern | numerics_tables | 1968 | 20061 | 12021 |
| gazette_modern | poly1900 | 84 | 1584 | 90 |
| ia_greek_latin | cyrillic | 0 | 3 | 0 |
| ia_greek_latin | dialogue_fiction | 0 | 63 | 2 |
| ia_greek_latin | greek_mono | 0 | 246 | 12 |
| ia_greek_latin | greek_poly | 14 | 1220 | 14 |
| ia_greek_latin | headings_caps | 0 | 7 | 0 |
| ia_greek_latin | latin | 122 | 6022 | 128 |
| ia_greek_latin | leaders_indices | 0 | 3 | 0 |
| ia_greek_latin | mixed_greek_latin | 9 | 2027 | 82 |
| ia_greek_latin | nonletter | 178 | 59 | 16 |
| ia_greek_latin | numerics_tables | 44 | 625 | 52 |
| ia_poly1850 | cyrillic | 3 | 63 | 6 |
| ia_poly1850 | dialogue_fiction | 1 | 570 | 9 |
| ia_poly1850 | greek_mono | 148 | 811 | 105 |
| ia_poly1850 | headings_caps | 27 | 292 | 3 |
| ia_poly1850 | latin | 490 | 32253 | 243 |
| ia_poly1850 | leaders_indices | 0 | 1 | 0 |
| ia_poly1850 | mixed_greek_latin | 43 | 7173 | 155 |
| ia_poly1850 | nonletter | 592 | 193 | 49 |
| ia_poly1850 | numerics_tables | 290 | 3019 | 459 |
| ia_poly1850 | poly1850 | 56 | 16464 | 66 |
| ia_russian | cyrillic | 15 | 2352 | 17 |
| ia_russian | greek_mono | 1 | 4 | 1 |
| ia_russian | latin | 11 | 42 | 4 |
| ia_russian | nonletter | 105 | 4 | 3 |
| ia_russian | numerics_tables | 15 | 84 | 13 |
| kosmopolis | dialogue_fiction | 9 | 321 | 15 |
| kosmopolis | greek_mono | 17 | 106 | 3 |
| kosmopolis | headings_caps | 1 | 19 | 0 |
| kosmopolis | latin | 3 | 9 | 2 |
| kosmopolis | mixed_greek_latin | 2 | 32 | 1 |
| kosmopolis | nonletter | 19 | 22 | 10 |
| kosmopolis | numerics_tables | 5 | 28 | 3 |
| kosmopolis | poly1850 | 1 | 468 | 1 |
| kosmopolis | poly1900 | 91 | 3216 | 134 |
| lekythos | cyrillic | 0 | 3 | 1 |
| lekythos | dialogue_fiction | 6 | 677 | 77 |
| lekythos | greek_mono | 34 | 354 | 35 |
| lekythos | headings_caps | 81 | 255 | 11 |
| lekythos | latin | 21 | 48 | 8 |
| lekythos | mixed_greek_latin | 3 | 30 | 8 |
| lekythos | nonletter | 13 | 23 | 2 |
| lekythos | numerics_tables | 19 | 81 | 18 |
| lekythos | poly1900 | 108 | 9714 | 1048 |
| nlg | dialogue_fiction | 5 | 871 | 2 |
| nlg | greek_mono | 13 | 443 | 8 |
| nlg | greek_poly | 5 | 820 | 1 |
| nlg | headings_caps | 30 | 186 | 11 |
| nlg | latin | 12 | 39 | 17 |
| nlg | mixed_greek_latin | 1 | 61 | 0 |
| nlg | nonletter | 179 | 74 | 22 |
| nlg | numerics_tables | 23 | 446 | 41 |
| nlg | poly1850 | 133 | 4455 | 17 |
| nlg | poly1900 | 21 | 3178 | 20 |
| openarchives_Dione | greek_latin_cs | 11 | 385 | 1 |
| openarchives_Dione | greek_mono | 21 | 2267 | 19 |
| openarchives_Dione | latin | 3 | 121 | 0 |
| openarchives_IKEE_AUT | greek_latin_cs | 0 | 18 | 0 |
| openarchives_IKEE_AUT | greek_mono | 0 | 209 | 0 |
| openarchives_IKEE_AUT | latin | 0 | 33 | 0 |
| openarchives_KEIED | greek_latin_cs | 0 | 94 | 0 |
| openarchives_KEIED | greek_mono | 0 | 2110 | 7 |
| openarchives_KEIED | latin | 0 | 44 | 2 |
| openarchives_Pandemos | greek_latin_cs | 0 | 191 | 0 |
| openarchives_Pandemos | greek_mono | 1 | 2275 | 5 |
| openarchives_Pandemos | greek_poly | 0 | 89 | 96 |
| openarchives_Pandemos | latin | 0 | 109 | 0 |
| openarchives_anaktisis | greek_latin_cs | 0 | 170 | 0 |
| openarchives_anaktisis | greek_mono | 6 | 2491 | 9 |
| openarchives_anaktisis | latin | 0 | 53 | 0 |
| openarchives_apothesis | greek_latin_cs | 0 | 194 | 0 |
| openarchives_apothesis | greek_mono | 9 | 1918 | 0 |
| openarchives_apothesis | latin | 2 | 84 | 0 |
| openarchives_hellanicus | greek_latin_cs | 0 | 220 | 0 |
| openarchives_hellanicus | greek_mono | 8 | 2490 | 2 |
| openarchives_hellanicus | latin | 0 | 141 | 0 |
| openarchives_kallipos | greek_latin_cs | 0 | 234 | 2 |
| openarchives_kallipos | greek_mono | 2 | 2527 | 9 |
| openarchives_kallipos | greek_poly | 0 | 49 | 1 |
| openarchives_kallipos | latin | 0 | 112 | 0 |
| openarchives_ktisis | greek_latin_cs | 0 | 248 | 0 |
| openarchives_ktisis | greek_mono | 4 | 2290 | 0 |
| openarchives_ktisis | latin | 2 | 76 | 0 |
| openarchives_mixed_Dione | greek_latin_cs | 0 | 129 | 1 |
| openarchives_mixed_Dione | greek_mono | 2 | 465 | 2 |
| openarchives_mixed_Dione | latin | 3 | 69 | 1 |
| openarchives_mixed_KEIED | greek_latin_cs | 0 | 40 | 0 |
| openarchives_mixed_KEIED | greek_mono | 8 | 140 | 0 |
| openarchives_mixed_KEIED | latin | 1 | 385 | 4 |
| openarchives_mixed_Pandemos | greek_latin_cs | 0 | 8 | 0 |
| openarchives_mixed_Pandemos | greek_mono | 0 | 30 | 0 |
| openarchives_mixed_Pandemos | greek_poly | 0 | 10 | 3 |
| openarchives_mixed_Pandemos | latin | 0 | 6 | 3 |
| openarchives_mixed_anaktisis | greek_latin_cs | 0 | 38 | 0 |
| openarchives_mixed_anaktisis | greek_mono | 1 | 306 | 1 |
| openarchives_mixed_anaktisis | latin | 0 | 140 | 2 |
| openarchives_mixed_apothesis | greek_latin_cs | 0 | 35 | 0 |
| openarchives_mixed_apothesis | greek_mono | 9 | 190 | 0 |
| openarchives_mixed_apothesis | greek_poly | 0 | 1 | 0 |
| openarchives_mixed_apothesis | latin | 0 | 443 | 0 |
| openarchives_mixed_hellanicus | greek_latin_cs | 0 | 11 | 0 |
| openarchives_mixed_hellanicus | greek_mono | 0 | 52 | 0 |
| openarchives_mixed_hellanicus | latin | 13 | 259 | 0 |
| openarchives_mixed_kallipos | greek_latin_cs | 0 | 33 | 0 |
| openarchives_mixed_kallipos | greek_mono | 0 | 45 | 0 |
| openarchives_mixed_kallipos | latin | 0 | 141 | 0 |
| openarchives_mixed_ktisis | greek_latin_cs | 0 | 42 | 1 |
| openarchives_mixed_ktisis | greek_mono | 0 | 207 | 0 |
| openarchives_mixed_ktisis | greek_poly | 0 | 2 | 0 |
| openarchives_mixed_ktisis | latin | 1 | 410 | 0 |
| openarchives_mixed_nemertes | greek_latin_cs | 0 | 19 | 0 |
| openarchives_mixed_nemertes | greek_mono | 0 | 103 | 0 |
| openarchives_mixed_nemertes | latin | 0 | 2 | 0 |
| openarchives_mixed_ntua | greek_latin_cs | 0 | 26 | 0 |
| openarchives_mixed_ntua | greek_mono | 0 | 23 | 0 |
| openarchives_mixed_ntua | greek_poly | 0 | 28 | 2 |
| openarchives_mixed_ntua | latin | 0 | 18 | 0 |
| openarchives_nemertes | greek_latin_cs | 0 | 198 | 0 |
| openarchives_nemertes | greek_mono | 4 | 1864 | 0 |
| openarchives_nemertes | latin | 0 | 89 | 1 |
| openarchives_ntua | greek_latin_cs | 0 | 231 | 0 |
| openarchives_ntua | greek_mono | 1 | 1434 | 0 |
| openarchives_ntua | latin | 6 | 76 | 4 |
| parliament_proceedings_1975_2000 | greek_latin_cs | 0 | 91 | 105 |
| parliament_proceedings_1975_2000 | greek_mono | 155 | 25249 | 19280 |
| parliament_proceedings_1975_2000 | greek_poly | 320 | 9369 | 25872 |
| parliament_proceedings_1975_2000 | latin | 5 | 481 | 254 |
| serbia | cyrillic | 75 | 7359 | 38 |
| serbia | dialogue_fiction | 0 | 1 | 0 |
| serbia | greek_mono | 3 | 11 | 2 |
| serbia | headings_caps | 0 | 8 | 0 |
| serbia | latin | 28 | 248 | 31 |
| serbia | mixed_greek_latin | 0 | 3 | 0 |
| serbia | nonletter | 32 | 25 | 10 |
| serbia | numerics_tables | 55 | 497 | 50 |
| vouli_parliament_1850s | greek_latin_cs | 0 | 4 | 19 |
| vouli_parliament_1850s | greek_mono | 42 | 1498 | 277 |
| vouli_parliament_1850s | greek_poly | 119 | 6497 | 19562 |
| vouli_parliament_1850s | latin | 1 | 114 | 126 |
| wikisource_el | greek_latin_cs | 0 | 58 | 54 |
| wikisource_el | greek_mono | 40 | 183 | 15 |
| wikisource_el | greek_poly | 4 | 5198 | 3329 |
| wikisource_el | latin | 1 | 71 | 17 |
| wikisource_ru | cyrillic | 6 | 2804 | 308 |
| wikisource_ru | latin | 0 | 2 | 0 |

## Draw and seal

Integer seed **20261019**; CPython `random.Random(seed)`; sort each complete pool by row ID, create a uniform random permutation with `sample(pool, len(pool))` for DROP then KEEP, take the first 50/100. Remaining candidates are a locked replacement order. No source/reason quotas or image-based selection. Full orders and their hashes are preserved in `keys/candidate_order_{DROP,KEEP}.jsonl`; `tools/verify.py` independently replays both permutations.

Active seal, before any image production: `keys/sealed_decisions.jsonl`, SHA256 **`c708cf4dedb86af914c6654bf0c8bbaea92e835663b84bdc372ad54b63b6b312`**. The initial metadata-only exclusion error and its preliminary seal are retained in `keys/superseded_metadata_only/`; corrected before any crop generation or pixel inspection. `verification.json` confirms active seal mtime precedes every crop mtime.

### Composition of the 50 REJECT rows

| Source | Verbatim segmentation reason | Drawn |
|---|---|---:|
| anemi_mixed | Too much OCR output for the text box after height normalisation. | 1 |
| anemi_round1 | Too much OCR output for the text box after height normalisation. | 2 |
| anemi_round2 | Too much OCR output for the text box after height normalisation. | 1 |
| elstat | Too much OCR output for the text box after height normalisation. | 1 |
| elstat | Top and bottom padding together exceed 1.5 target-line heights. | 3 |
| gazette_modern | A second complete printed line is visible. | 1 |
| gazette_modern | Too little OCR output for the text box after height normalisation. | 15 |
| gazette_modern | Too much OCR output for the text box after height normalisation. | 15 |
| gazette_modern | Top and bottom padding together exceed 1.5 target-line heights. | 2 |
| ia_poly1850 | Too much OCR output for the text box after height normalisation. | 3 |
| ia_poly1850 | Top and bottom padding together exceed 1.5 target-line heights. | 1 |
| lekythos | Too little OCR output for the text box after height normalisation. | 1 |
| nlg | Too little OCR output for the text box after height normalisation. | 1 |
| openarchives_Dione | Too much OCR output for the text box after height normalisation. | 1 |
| parliament_proceedings_1975_2000 | Too little OCR output for the text box after height normalisation. | 2 |

## Crops and packs

All **150/150** crops are in `crops/<row_id>.png`; `crops_manifest.jsonl` binds each SHA256 and size to the pipeline crop identity. Zero failures, zero replacements (`crop_failures.json`). 112 W1/W2 crops were regenerated using collector `.venv` and unchanged `collect_v3.storage.ensure_crop`; 38 original-v2 PNGs were fetched byte-exact from retained source crops by read-only SSH, then verified by `ensure_crop` against the export hash. No OCR, detector, orientation process or segmentation inference ran on the Mac. Metadata draw/pack/scoring preparation only accompanies crop materialisation.

Public pack paths:

- `/private/tmp/segeval1-packs-20261019/segeval1_a/r1`
- `/private/tmp/segeval1-packs-20261019/segeval1_b/r1`

Each reader folder has only `cards.jsonl` and `crops/`; manifests are beside `r1`, outside the reader folder. Fresh opaque IDs, seeded mixed order, four public fields (`card_id`, `crop`, `google_text`, `word_scripts`), content-hash filenames, regular copies, no links, no source IDs/reasons/decision/control marker. Global mixing precedes a 75/75 split; order seeds and split procedure are in `tools/build_packs.py`.

All 150 repository crops remain byte-exact. One public copy (`5a6a4fec-p000052-l0021`) drops only the ancillary PNG iCCP metadata chunk, retaining mode, dimensions, compressed raster chunks and exact pixel bytes; its public filename/hash changes. The other public PNGs are byte copies. `keys/crop_custody.json` records original/public hashes and the metadata removal. No crop is resized, rotated or masked.

The ten reused CAPS1/CP7 controls are c057, c009, c013, c026, c046, c041, c029, c072, c035, c066. Their existing lead-approved status is recorded in `seg/CP7b_RECEIPT.md` (10/10 against lead-approved CAPS1 control_truth); original truth is `docs/records/harvest/recut_v1/w1_masked/caps1/keys/control_truth.json`. No new lead pixel review is claimed. Five controls per context, indistinguishable from study cards. Control scoring uses letters/crop_ok; more than one control error invalidates that context. No owner-rubric control truth is invented.

Portable pack-only archive: `blind_packs.tar.gz`. Restore, if needed, with `mkdir -p /private/tmp/segeval1-packs-20261019` then `tar -xzf blind_packs.tar.gz -C /private/tmp/segeval1-packs-20261019` from this directory, only into an absent/empty target. Never put keys or reports under PACK_ROOT.

## Protocol and prepared launcher

Canonical scanner v4.4 copied byte-for-byte, SHA256 `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`. `prompts/bsb.md` matches the canonical sol-reading file verbatim. `owner_rubric.md` adds whole neighbour word / two complete lines / rotated or vertical / horizontal final-letter end-clip plus free text. This last item follows the present owner request and is scored as its own rubric item. It does not reuse CP7’s different broad horizontal-block question. `path_addendum.md` preserves CP7’s literal relative-path guidance.

Prepared launcher (DO NOT run as part of preparation):

```sh
bash docs/records/harvest/collect_v3_admission/segeval1/launch.sh
```

This adapts the sourcing lead’s `seg/cp7/r2/launchers/run_bed.sh` workflow: verify closure → limit probe → gpt-6.1-sol / medium reading context → canonical leak scan → answer/rollout hash custody → limit probe → second context → score. The copied `run_read.sh` and `limit_probe.sh` retain the CP7 model and isolation flags: workspace-write at the reader directory, no network/web, no multi-agent/apps/plugins, project docs disabled. Preparation used network only for read-only Clariden SSH; future readers keep CP7 network OFF. Launcher refuses existing answers/logs, changed scanner/pack/decision hashes, missing weekly limit evidence or ≥78% weekly usage. No limit probes have been run in this task.

## Scoring and owner sheet

`segeval1_score.py` consumes both complete ordered answer files, clean v4.4 scans and answer/scan/rollout hash custody, plus the sealed decisions. It writes `scored/summary.json`, `owner_rows.jsonl` and `owner_sheet.csv` (line ID, crop, Google text, decision/reason, full reader answer). `keys/owner_sheet_pending.csv` is the pre-read table, explicitly PENDING.

- False positive: REJECT and all four owner answers “no”; report count/rate out of 50 and per reason (with drawn denominators).
- False negative: ACCEPT and any rubric answer “yes”; count out of 100 and per rubric item (overlapping counts).
- No “yes” but any “uncertain”: unresolved, never silently fine.
- bsb transcription/diacritic errors and its stricter crop_ok are retained, but do not replace the owner rubric.
- Control failure invalidates the result; no automated proceed threshold is applied.

Validation: 150 original hashes checked; both independent pack closures pass; deterministic draw replay, exclusion disjointness and seal-before-crop checks pass; verbatim base prompt and canonical scanner hashes pass; seven synthetic scorer tests pass (`scoring_tests.log`). No test fixture is a reader result. No images were judged by this preparation session.

Packaging: `SEGEVAL1.bundle` is a self-contained artifact Git bundle created in a temporary repository, preserving the shared checkout/index and unrelated existing changes. `package_receipt.json` records its commit and SHA256. The bundle’s commit contains this entire handoff directory except the bundle and its self-referential packaging receipt.

SEGEVAL1: done | pools after exclusion: reject 16736 / accept 416241 | drawn 50/100 sealed c708cf4d | crops 150/150 | packs: /private/tmp/segeval1-packs-20261019/segeval1_a/r1,/private/tmp/segeval1-packs-20261019/segeval1_b/r1 | launch: bash docs/records/harvest/collect_v3_admission/segeval1/launch.sh | commit: docs/records/harvest/collect_v3_admission/segeval1/SEGEVAL1.bundle

# LQB inputs, by reference (read-only; never copied into truth without provenance)

## From the sourcing lead (17 Oct; sol/collect-v3 e1673384 unless stated)

### 1. Locked strata

Registry: `docs/records/harvest/collect_v3/release_exclusions/release_exclusions.json` (sha 09c351f5…). The table gives the truth source of
each class.

| Class | File / n / sha prefix | Truth source |
|---|---|---|
| locked_eval | r0_locked_eval_ids.txt, 200, ac79c799… | R0 stratum (ii), spell-check lead (greek-ocr-toolkit-spellcheck-r0, opus/spellcheck-r0 b7fd49ba) — truth file from the spell-check lead |
| locked_eval_ia_wikisource | 133, 7c739c5c… | R0 (i-a), spell-check lead |
| eval_only_dev | 273, 9a3175cf… | dev pool, spell-check lead |
| locked_eval_ib_wikisource | r0_locked_eval_ib_wikisource_ids.txt, 1,246, 1d41c3b2… | sourcing T7/T7b (sol/wikisource-r0 db011b01, docs/records/harvest/wikisource_r0/) |
| n1_locked_eval | 258, 3d6f0d29… | this track |

Notes per class:
- **locked_eval.**
  - Line ids come from the blind-check keys: `sol/funnel-gr docs/records/harvest/blind_checks_v1/{t4c,c0}/<src>_key.json`.
  - Crops are the saved blind-card PNGs. Their bytes can differ from the feature-crop encoding.
  - Page boxes: `sol/collect-v3 docs/records/harvest/screen_v1/features.jsonl`.
- **locked_eval_ib_wikisource.**
  - The label is the Wikisource transcription aligned to the scan, R0 (i-b) "clean locked Wikisource".
  - Crops and boxes are in `lines.jsonl`, rasters in `pages.jsonl`.
  - The spell-check subset is `r0_ib_spellcheck_subset_ids.txt` (400).
- **Masked versions of (ii) 200 + (i-b) 400** (test-only): `sol/recut-v1 925544b6 docs/records/harvest/recut_v1/v2_full/locked/records.jsonl`
  (sha d4a9fee5…), with `resolution.jsonl` beside it.
- **Screens, not truth:** separator_ambiguous (75), rotated_crop (1,681), mirrored_showthrough (1).

### 2. Admission files (`release_admissions/`)

- `w1_masked_1d.jsonl` (d9343b74…) and `w1_masked_1d_summary.json` (7824940e…).
- Arms: wave-1d 16,562 (gazette modern_scanned measured, kosmopolis poly1900, lekythos poly1900); release-v3-candidate kosmopolis
  poly1850 462; release-v3-candidate headings_caps 1,626.
- Label = W1 post-convention `label`, unchanged; only the crop is masked. No RU1 or other repaired label is in any admission file.
- There is no W2 admission yet.

### 3. C1 verdicts (final)

- `docs/records/harvest/collect_v3/c1/verdicts/*.jsonl` (28 files) and `c1_results.json` (70ebebc6…).
- `c1/yer_adjudication/table.json`.
- Card → line ids: `~/Projects/collect-v3-data/run/W1/c1/<stratum>_key.json` (ids only).
- Caveats:
  - **Blinding:** KEY-IN-REACH, not opened (C1_REPORT).
  - **mixed_greek_latin** is c1_pending.
  - **Masked-card results:** `sol/recut-v1 docs/records/harvest/recut_v1/w1_masked/{checks,caps1,caps3,kosmo2,ruc1}/`.

## From the spell-check lead (17 Oct)

The by-reference file is `~/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/LQB_MARKS_INPUTS.md` (opus/spellcheck
33cacf520). It gives the paths, sha256, method and readers for each set.

**Truth sets** (print = what is printed; four mark heads):
- the 189 print truth;
- the 39 owner cards + notes;
- the 60 substitution sample;
- audit100 (L1A2, owner, 83/100);
- S8 DEV (600 lines);
- T4 791 and T2 790 resolved (two blind Opus readers + 2-of-3 tiebreak, controls gated).

**sf6 release.** 124,669 selected lines (selection.jsonl ee6c51bd…), R1-A reader, policy digest 6f62925a. The remote path and receipt
are in the file.

**CQ1.** No new truth: its 60 capitals are a subset of T2.

**In-sample map.**

| Version | In-sample sets |
|---|---|
| S6/sf6 detector | print truth 189 |
| sf6 gate rules | print truth + L1-era evidence. audit100 and the substitution sample are OUT-of-sample for sf6, but in-sample for anything new designed from them (SF7, the quote-alias rule). |
| R1-A evaluation | the 39 cards (they set overlay v1.1) |
| R2a | T2 (training) and T4 (capital-recall primary chosen after seeing T4) |
| S8b | S8 DEV. The frozen sf6 detector did not use DEV. |

**Exclusion caution.** T2 is supervision (the R2a overlay), so its ids are **NOT** listed in release_exclusions. The truth records
carry `exclude_from_training`: false for T2 and true for T4, DEV, the print truth, the 39 and audit100.

## This track

- RU1: `artifacts/ru1/` (keys/control_inventory.json; RU1_LEAD_REVIEW.md; ru1_v1.jsonl, sha 1fb0a9f5…).
- N1: `artifacts/n1/controls/approved.jsonl` (f0ef2f86…), `dash_types.jsonl` (fb600648…), `lead_t.jsonl`, N1T_LEAD_RAISED.md.

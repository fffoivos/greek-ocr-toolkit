# Benchmark 0.2: seal04 record (20 Oct 2026). Supersedes seal03.

**SEALED.** Clariden job 3705113, submitted by the coordinator. Output: `$W/benchmark_0.2/seal04/`. Package `benchmark_0.2/pkg/fdaf8ca2`: SEAL02 + B + D (cross-panel pixel-duplicate drop, within-panel uniqueness), deployed in SEAL02E.

seal03 (`../seal03_record/`) is superseded because of ASTRA-CP3 HIGH 1: one pixel-identical crop sat in both test and dev.

Files in this directory, each sha-checked against Clariden:
- `SEAL_RECEIPT.json`, sha256 `34d024a725b02a9b090d061ed3e7c502ad799ad24371504f2fa5cb99502b3850`;
- `seal04.inputs.json`, sha256 `98b97de595a4f58e6a8b3963c8e70ebe4307bdd682bca813eb9ca15f7ff0f7f3` (= `bindings_sha256`).

## Identity
- Receipt fields:
  - status `SEALED`, version `0.2`, mock false, comparison_status `diagnostic_only`;
  - rows 2,690 = images 2,690;
  - test 2,253 (panel sha `3f6f3ef4…`, byte-identical to seal03's test panel); dev 437 (panel sha `73f647b5…`).
- `suite_sha256` `9447f09c6073028c1085996e1663232a18ac70ef8b81eda4be5c232a4025b924`. The lead re-hashed a fetched copy and it matches.
- `package_manifest_sha256` `37232421d4f058f507fabc44998a9a22a5fd260e75aa9859f1b918f718d194ff`.
- Inputs are identical to seal03:
  - LF1 v2: final_list `0fa4a1fe…`, finalize.receipt `00016527…`, verdicts `a203509c…`;
  - candidates_v3 `0432c56f…`, readout `929e231c…`;
  - CROPS4 W1 `8062f8e7…`, W2 `975fd413…`;
  - census `5ee1c70e…` / `096b18a8…`.
- `cross_panel_pixel_duplicates_dropped`: 1 entry. Image `4b22b2ff…` ("НБС"): dev `serbia--27b182bf4116728f--s009-l0006` dropped (dev:font_extremes:small), test `serbia--d6030713c8d88c96--s005-l0006` kept. There are no within-panel repeats.
- LF1: flagged 350 = REPLACED 248 + UNFILLED 102 (test 298 = 211 + 87; dev 52 = 37 + 15).

## What the references certify (ASTRA-CP3 M1)
The references are the pipeline's corrected labels, filtered by LF1. An LF1 `OK` certifies the crop rules and that the **letters** match the image. It does **not** certify diacritics: accents, breathings, iota subscript and dialytika. Benchmark 0.2 is a pipeline-reference, letter- and crop-filtered instrument whose **diacritics are unqualified**.

Diacritic-sensitive scores (strict NFD CER, mark metrics) measure agreement with the pipeline's marks. Report them that way. The diacritic-insensitive measures are the ones LF1 qualifies.

## Coverage and deficit sources (ASTRA-CP3 M2)
All numbers below are computed from the sealed panel files, the receipt and candidates_v3, and are asserted per scope: **total deficit = quota − sealed = draw-supply deficit + LF1 UNFILLED + duplicate drop**.
- **Draw-supply deficit** = quota − in-quota candidates drawn: no supply, or Serbian-only modern Cyrillic.
- **LF1 UNFILLED** = a flagged in-quota line with no OK same-scope, same-source reserve.
- **Duplicate drop** = removed by the cross-panel pixel check.

These replace the candidate-stage figures (15/16 test, 11/16 dev classes "filled") and the programme's 2,400/600 and "15 classes" prose. Modern Cyrillic is Serbian-only: 40 test, 8 dev.

### Coverage per class × split (16 classes; modern_cyrillic and font_extremes summed over subgroups)

| Split | Class | Quota | Sealed | Nonempty | Quota-complete | Draw-supply deficit | LF1 UNFILLED | Duplicate drop |
|---|---|---:|---:|:-:|:-:|---:|---:|---:|
| test | caps_headings | 120 | 119 | yes | no | 0 | 1 | 0 |
| test | curved_skewed | 100 | 99 | yes | no | 0 | 1 | 0 |
| test | degraded | 100 | 80 | yes | no | 0 | 20 | 0 |
| test | font_extremes | 100 | 97 | yes | no | 0 | 3 | 0 |
| test | greek_latin | 160 | 152 | yes | no | 0 | 8 | 0 |
| test | historical_russian | 120 | 120 | yes | yes | 0 | 0 | 0 |
| test | latin | 160 | 157 | yes | no | 0 | 3 | 0 |
| test | leaders_dashes | 100 | 94 | yes | no | 0 | 6 | 0 |
| test | long | 160 | 146 | yes | no | 0 | 14 | 0 |
| test | modern_cyrillic | 160 | 40 | yes | no | 120 | 0 | 0 |
| test | monotonic | 240 | 240 | yes | yes | 0 | 0 | 0 |
| test | numeric_cells | 200 | 199 | yes | no | 0 | 1 | 0 |
| test | poly_dictionary_journal | 160 | 155 | yes | no | 0 | 5 | 0 |
| test | polytonic | 360 | 340 | yes | no | 0 | 20 | 0 |
| test | short | 120 | 119 | yes | no | 0 | 1 | 0 |
| test | vertical_turned | 100 | 96 | yes | no | 0 | 4 | 0 |
| dev | caps_headings | 30 | 30 | yes | yes | 0 | 0 | 0 |
| dev | curved_skewed | 25 | 24 | yes | no | 0 | 1 | 0 |
| dev | degraded | 25 | 20 | yes | no | 0 | 5 | 0 |
| dev | font_extremes | 25 | 23 | yes | no | 0 | 1 | 1 |
| dev | greek_latin | 40 | 12 | yes | no | 25 | 3 | 0 |
| dev | historical_russian | 30 | 0 | no | no | 30 | 0 | 0 |
| dev | latin | 40 | 3 | yes | no | 37 | 0 | 0 |
| dev | leaders_dashes | 25 | 25 | yes | yes | 0 | 0 | 0 |
| dev | long | 40 | 38 | yes | no | 0 | 2 | 0 |
| dev | modern_cyrillic | 40 | 8 | yes | no | 30 | 2 | 0 |
| dev | monotonic | 60 | 60 | yes | yes | 0 | 0 | 0 |
| dev | numeric_cells | 50 | 50 | yes | yes | 0 | 0 | 0 |
| dev | poly_dictionary_journal | 40 | 0 | no | no | 40 | 0 | 0 |
| dev | polytonic | 90 | 90 | yes | yes | 0 | 0 | 0 |
| dev | short | 30 | 30 | yes | yes | 0 | 0 | 0 |
| dev | vertical_turned | 25 | 24 | yes | no | 0 | 1 | 0 |

| Split | Classes nonempty | Classes quota-complete | Quota | Sealed | Draw-supply deficit | LF1 UNFILLED | Duplicate drop |
|---|---:|---:|---:|---:|---:|---:|---:|
| test | 16/16 | 2/16 | 2460 | 2253 | 120 | 87 | 0 |
| dev | 14/16 | 6/16 | 615 | 437 | 162 | 15 | 1 |


### Deficit split per scope (quota − sealed = draw-supply deficit + LF1 UNFILLED + duplicate drop)

| Scope | Quota | In-quota drawn | Sealed | Draw-supply deficit | LF1 UNFILLED | Duplicate drop | Total deficit |
|---|---:|---:|---:|---:|---:|---:|---:|
| test:caps_headings | 120 | 120 | 119 | 0 | 1 | 0 | 1 |
| test:curved_skewed | 100 | 100 | 99 | 0 | 1 | 0 | 1 |
| test:degraded | 100 | 100 | 80 | 0 | 20 | 0 | 20 |
| test:font_extremes:large | 50 | 50 | 49 | 0 | 1 | 0 | 1 |
| test:font_extremes:small | 50 | 50 | 48 | 0 | 2 | 0 | 2 |
| test:greek_latin | 160 | 160 | 152 | 0 | 8 | 0 | 8 |
| test:historical_russian | 120 | 120 | 120 | 0 | 0 | 0 | 0 |
| test:latin | 160 | 160 | 157 | 0 | 3 | 0 | 3 |
| test:leaders_dashes | 100 | 100 | 94 | 0 | 6 | 0 | 6 |
| test:long | 160 | 160 | 146 | 0 | 14 | 0 | 14 |
| test:modern_cyrillic:bg | 40 | 0 | 0 | 40 | 0 | 0 | 40 |
| test:modern_cyrillic:ru | 40 | 0 | 0 | 40 | 0 | 0 | 40 |
| test:modern_cyrillic:sr | 40 | 40 | 40 | 0 | 0 | 0 | 0 |
| test:modern_cyrillic:uk | 40 | 0 | 0 | 40 | 0 | 0 | 40 |
| test:monotonic | 240 | 240 | 240 | 0 | 0 | 0 | 0 |
| test:numeric_cells | 200 | 200 | 199 | 0 | 1 | 0 | 1 |
| test:poly_dictionary_journal | 160 | 160 | 155 | 0 | 5 | 0 | 5 |
| test:polytonic | 360 | 360 | 340 | 0 | 20 | 0 | 20 |
| test:short | 120 | 120 | 119 | 0 | 1 | 0 | 1 |
| test:vertical_turned | 100 | 100 | 96 | 0 | 4 | 0 | 4 |
| dev:caps_headings | 30 | 30 | 30 | 0 | 0 | 0 | 0 |
| dev:curved_skewed | 25 | 25 | 24 | 0 | 1 | 0 | 1 |
| dev:degraded | 25 | 25 | 20 | 0 | 5 | 0 | 5 |
| dev:font_extremes:large | 12 | 12 | 12 | 0 | 0 | 0 | 0 |
| dev:font_extremes:small | 13 | 13 | 11 | 0 | 1 | 1 | 2 |
| dev:greek_latin | 40 | 15 | 12 | 25 | 3 | 0 | 28 |
| dev:historical_russian | 30 | 0 | 0 | 30 | 0 | 0 | 30 |
| dev:latin | 40 | 3 | 3 | 37 | 0 | 0 | 37 |
| dev:leaders_dashes | 25 | 25 | 25 | 0 | 0 | 0 | 0 |
| dev:long | 40 | 40 | 38 | 0 | 2 | 0 | 2 |
| dev:modern_cyrillic:bg | 10 | 0 | 0 | 10 | 0 | 0 | 10 |
| dev:modern_cyrillic:ru | 10 | 0 | 0 | 10 | 0 | 0 | 10 |
| dev:modern_cyrillic:sr | 10 | 10 | 8 | 0 | 2 | 0 | 2 |
| dev:modern_cyrillic:uk | 10 | 0 | 0 | 10 | 0 | 0 | 10 |
| dev:monotonic | 60 | 60 | 60 | 0 | 0 | 0 | 0 |
| dev:numeric_cells | 50 | 50 | 50 | 0 | 0 | 0 | 0 |
| dev:poly_dictionary_journal | 40 | 0 | 0 | 40 | 0 | 0 | 40 |
| dev:polytonic | 90 | 90 | 90 | 0 | 0 | 0 | 0 |
| dev:short | 30 | 30 | 30 | 0 | 0 | 0 | 0 |
| dev:vertical_turned | 25 | 25 | 24 | 0 | 1 | 0 | 1 |


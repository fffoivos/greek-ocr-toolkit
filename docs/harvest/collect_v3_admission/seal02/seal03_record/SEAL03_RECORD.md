# Benchmark 0.2: seal03 record (20 Oct 2026)

**SEALED.** Clariden job 3705072, submitted by the coordinator. Output: `$W/benchmark_0.2/seal03/` (`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`). Seal package `benchmark_0.2/pkg/253921bf` (SEAL02 + SEAL02B).

This directory holds read-only copies of the two binding files, each sha-checked against Clariden:
- `SEAL_RECEIPT.json`, sha256 `32db74bc4915be286fb6e69303283f3b4f6402291db1af73583bee2f40489ca7`;
- `seal03.inputs.json`, sha256 `9da9acac4eab1b9742098eebf99413802dd17ad4ad62c9321cdf4ca2eea04e30` (= the receipt's `bindings_sha256`).

## Identity
- Receipt fields:
  - status `SEALED`, version `0.2`, mock false, comparison_status `diagnostic_only`;
  - rows 2,691 and images 2,690 (see the duplicate-image finding below).
- `suite_sha256` `33e7fe9f0392518bcea030772a6ff18934d94513bcce6e28c7a9c81c53f09539`. The lead re-hashed a fetched `suite.json` and it matches.
- `package_manifest_sha256` `29c5460242d6f8d2864840cdd629ae1d2e9916a13c9fdfa3b9cb7eb34fb861f1`.
- Bound inputs (sha256):
  - candidates_v3 `0432c56f…34c2`, readout `929e231c…0973`, counts `5e1c0a74…`, draw_plan `8007e93f…`, tags receipt `4b07d43a…`;
  - census CURRENT `5ee1c70e…`, summary `096b18a8…`;
  - LF1 v2 (re-finalised with scope_rank pairing): final_list `0fa4a1fe747e06dfeb9bdb4e6c1a8f3027140b4b160330c4ce07621a9315a08b`, finalize.receipt `0001652776fd2e45261081bdeffd67b05749edec5a5abadd4162d3d893be6537`, verdicts `a203509cbd8105f4c7aeeba04f2ecc32fcb43662a26af8a87902c12b142d12e9` (unchanged from v1);
  - CROPS4 W1 receipt `8062f8e7…e6c4`, W2 `975fd413…1ffc`.

## Panels (counted from the panel files)
- `benchmark_v02_test.jsonl`: 2253 rows, sha256 `3f6f3ef46a9f9b59e045eed6e6314a727d4a9244140a20cd584eacd7c315ea37`
- `benchmark_v02_dev.jsonl`: 438 rows, sha256 `156195af95931820b0d9f471042053f2fe90ac06812e6502bb2d717c331b809b`

| Scope | Quota | Sealed (panel) | of which replacements | UNFILLED (LF1) | Deficit vs quota | Sources | Editions |
|---|---:|---:|---:|---:|---:|---:|---:|
| test:caps_headings | 120 | 119 | 2 | 1 | 1 | 6 | 88 |
| test:curved_skewed | 100 | 99 | 4 | 1 | 1 | 10 | 51 |
| test:degraded | 100 | 80 | 12 | 20 | 20 | 10 | 40 |
| test:font_extremes:large | 50 | 49 | 1 | 1 | 1 | 10 | 35 |
| test:font_extremes:small | 50 | 48 | 1 | 2 | 2 | 10 | 25 |
| test:greek_latin | 160 | 152 | 27 | 8 | 8 | 7 | 35 |
| test:historical_russian | 120 | 120 | 8 | 0 | 0 | 1 | 6 |
| test:latin | 160 | 157 | 9 | 3 | 3 | 6 | 27 |
| test:leaders_dashes | 100 | 94 | 11 | 6 | 6 | 10 | 42 |
| test:long | 160 | 146 | 19 | 14 | 14 | 9 | 45 |
| test:modern_cyrillic:bg | 40 | 0 | 0 | 0 | 40 | 0 | 0 |
| test:modern_cyrillic:ru | 40 | 0 | 0 | 0 | 40 | 0 | 0 |
| test:modern_cyrillic:sr | 40 | 40 | 3 | 0 | 0 | 1 | 3 |
| test:modern_cyrillic:uk | 40 | 0 | 0 | 0 | 40 | 0 | 0 |
| test:monotonic | 240 | 240 | 27 | 0 | 0 | 1 | 75 |
| test:numeric_cells | 200 | 199 | 5 | 1 | 1 | 10 | 61 |
| test:poly_dictionary_journal | 160 | 155 | 21 | 5 | 5 | 2 | 12 |
| test:polytonic | 360 | 340 | 39 | 20 | 20 | 6 | 22 |
| test:short | 120 | 119 | 11 | 1 | 1 | 10 | 47 |
| test:vertical_turned | 100 | 96 | 11 | 4 | 4 | 7 | 34 |
| dev:caps_headings | 30 | 30 | 1 | 0 | 0 | 3 | 13 |
| dev:curved_skewed | 25 | 24 | 1 | 1 | 1 | 4 | 12 |
| dev:degraded | 25 | 20 | 3 | 5 | 5 | 4 | 10 |
| dev:font_extremes:large | 12 | 12 | 1 | 0 | 0 | 3 | 7 |
| dev:font_extremes:small | 13 | 12 | 0 | 1 | 1 | 4 | 7 |
| dev:greek_latin | 40 | 12 | 0 | 3 | 28 | 3 | 6 |
| dev:historical_russian | 30 | 0 | 0 | 0 | 30 | 0 | 0 |
| dev:latin | 40 | 3 | 0 | 0 | 37 | 2 | 2 |
| dev:leaders_dashes | 25 | 25 | 3 | 0 | 0 | 4 | 10 |
| dev:long | 40 | 38 | 3 | 2 | 2 | 4 | 9 |
| dev:modern_cyrillic:bg | 10 | 0 | 0 | 0 | 10 | 0 | 0 |
| dev:modern_cyrillic:ru | 10 | 0 | 0 | 0 | 10 | 0 | 0 |
| dev:modern_cyrillic:sr | 10 | 8 | 2 | 2 | 2 | 1 | 2 |
| dev:modern_cyrillic:uk | 10 | 0 | 0 | 0 | 10 | 0 | 0 |
| dev:monotonic | 60 | 60 | 5 | 0 | 0 | 1 | 25 |
| dev:numeric_cells | 50 | 50 | 8 | 0 | 0 | 4 | 23 |
| dev:poly_dictionary_journal | 40 | 0 | 0 | 0 | 40 | 0 | 0 |
| dev:polytonic | 90 | 90 | 5 | 0 | 0 | 2 | 2 |
| dev:short | 30 | 30 | 2 | 0 | 0 | 3 | 17 |
| dev:vertical_turned | 25 | 24 | 3 | 1 | 1 | 1 | 19 |

| Split | Quota | Sealed | Replacements | UNFILLED | Deficit |
|---|---:|---:|---:|---:|---:|
| test | 2460 | 2253 | 211 | 87 | 207 |
| dev | 615 | 438 | 37 | 15 | 177 |

UNFILLED rows by scope:
- `dev:curved_skewed` (1): `lekythos--7f67b784930deef5--s004-l0023`
- `dev:degraded` (5): `serbia--9caa9fc02f50cad6--s003-l0009`, `serbia--9caa9fc02f50cad6--s002-l0007`, `kosmopolis--91040f2da70b9ae0--s004-l0038`, `kosmopolis--91040f2da70b9ae0--s001-l0038`, `serbia--9caa9fc02f50cad6--s002-l0005`
- `dev:font_extremes:small` (1): `lekythos--7f67b784930deef5--s003-l0018`
- `dev:greek_latin` (3): `kosmopolis--91040f2da70b9ae0--s000-l0024`, `kosmopolis--91040f2da70b9ae0--s000-l0033`, `gazette_modern--d6092126b747cac8--s000-l0030`
- `dev:long` (2): `gazette_modern--a6c088328b5ced3c--s000-l0129`, `gazette_modern--2bb702efc2330588--s000-l0011`
- `dev:modern_cyrillic:sr` (2): `serbia--9caa9fc02f50cad6--s004-l0021`, `serbia--27b182bf4116728f--s005-l0024`
- `dev:vertical_turned` (1): `gazette_modern--eb386b5f1e04d525--s000-l0016`
- `test:caps_headings` (1): `lekythos--a0c4e6327052acfc--s001-l0008`
- `test:curved_skewed` (1): `nlg--6146c0455e0103d2--s008-l0024`
- `test:degraded` (20): `lekythos--a0c4e6327052acfc--s001-l0024`, `kosmopolis--0cd4687d9d1882ae--s000-l0008`, `gazette_modern--12109f1915738d9d--s000-l0203`, `kosmopolis--3ccb484c8655e2ec--s003-l0032`, `nlg--6146c0455e0103d2--s007-l0016`, `kosmopolis--0cd4687d9d1882ae--s001-l0013`, `serbia--557369d8d117b91a--s009-l0001`, `gazette_modern--e6046fd6f1e8fc1a--s000-l0039`, `ia_poly1850--36dcee7ce4c29f8b--s036-l0060`, `bsb_poly1850--0ab5fcea9a6fd52e--s007-l0043`, `kosmopolis--3ccb484c8655e2ec--s003-l0030`, `nlg--6146c0455e0103d2--s025-l0017`, `ia_poly1850--3bfe0ab3a504d025--s006-l0017`, `ia_poly1850--8b16b26eee5a53a8--s037-l0046`, `ia_greek_latin--a8c58d8eb21f93c8--s001-l0034`, `gazette_modern--09a3cd5f83d7fd59--s000-l0025`, `kosmopolis--0cd4687d9d1882ae--s001-l0033`, `ia_russian--03b43bc5289ad8ce--s000-l0026`, `nlg--6ae0ac01064a587e--s039-l0004`, `ia_poly1850--29e9490734cc1653--s003-l0002`
- `test:font_extremes:large` (1): `lekythos--40ed3fea207e3d94--s002-l0011`
- `test:font_extremes:small` (2): `bsb_poly1850--0ab5fcea9a6fd52e--s021-l0046`, `kosmopolis--3ccb484c8655e2ec--s004-l0031`
- `test:greek_latin` (8): `lekythos--a0c4e6327052acfc--s000-l0024`, `kosmopolis--3ccb484c8655e2ec--s004-l0034`, `gazette_modern--bbfc3f6881dda38a--s000-l0046`, `gazette_modern--c42f96d5421dab93--s000-l0036`, `gazette_modern--eedc3ed403ef92fe--s000-l0021`, `gazette_modern--306f3db36191aba6--s000-l0022`, `bsb_poly1850--0ab5fcea9a6fd52e--s004-l0041`, `ia_poly1850--3bfe0ab3a504d025--s023-l0038`
- `test:latin` (3): `kosmopolis--3ccb484c8655e2ec--s004-l0012`, `gazette_modern--d4e7c0bb57264e92--s000-l0010`, `ia_greek_latin--e2d30795088743d8--s000-l0034`
- `test:leaders_dashes` (6): `kosmopolis--3ccb484c8655e2ec--s004-l0007`, `kosmopolis--0cd4687d9d1882ae--s004-l0041`, `ia_russian--d83b48ac6a21756e--s003-l0003`, `ia_greek_latin--34f544df6c245b5d--s003-l0040`, `nlg--6146c0455e0103d2--s011-l0002`, `bsb_poly1850--2032df1e3e983f1d--s001-l0036`
- `test:long` (14): `ia_poly1850--a89bd2c9bdb1ca6d--s017-l0029`, `ia_poly1850--36dcee7ce4c29f8b--s032-l0030`, `ia_poly1850--3bfe0ab3a504d025--s024-l0013`, `ia_poly1850--8b16b26eee5a53a8--s008-l0027`, `bsb_poly1850--515c78c513c1c8c5--s011-l0090`, `bsb_poly1850--2032df1e3e983f1d--s002-l0036`, `ia_poly1850--8b16b26eee5a53a8--s027-l0046`, `ia_poly1850--a89bd2c9bdb1ca6d--s015-l0034`, `ia_poly1850--36dcee7ce4c29f8b--s001-l0082`, `kosmopolis--0cd4687d9d1882ae--s004-l0040`, `ia_greek_latin--e2d30795088743d8--s001-l0027`, `kosmopolis--0cd4687d9d1882ae--s004-l0020`, `ia_poly1850--3bfe0ab3a504d025--s024-l0003`, `bsb_poly1850--515c78c513c1c8c5--s023-l0029`
- `test:numeric_cells` (1): `nlg--6ae0ac01064a587e--s032-l0001`
- `test:poly_dictionary_journal` (5): `ia_poly1850--b3d418e8a99d8bec--s036-l0109`, `ia_poly1850--174d84a441d69a70--s010-l0011`, `ia_poly1850--b3d418e8a99d8bec--s030-l0016`, `ia_poly1850--36dcee7ce4c29f8b--s025-l0047`, `ia_poly1850--36dcee7ce4c29f8b--s000-l0109`
- `test:polytonic` (20): `bsb_poly1850--515c78c513c1c8c5--s021-l0099`, `bsb_poly1850--0ab5fcea9a6fd52e--s004-l0059`, `bsb_poly1850--515c78c513c1c8c5--s013-l0107`, `bsb_poly1850--0ab5fcea9a6fd52e--s013-l0063`, `bsb_poly1850--515c78c513c1c8c5--s021-l0071`, `bsb_poly1850--0ab5fcea9a6fd52e--s013-l0068`, `bsb_poly1850--515c78c513c1c8c5--s016-l0054`, `bsb_poly1850--0ab5fcea9a6fd52e--s026-l0055`, `bsb_poly1850--0ab5fcea9a6fd52e--s007-l0051`, `bsb_poly1850--0ab5fcea9a6fd52e--s035-l0044`, `ia_poly1850--36dcee7ce4c29f8b--s000-l0018`, `bsb_poly1850--0ab5fcea9a6fd52e--s014-l0037`, `bsb_poly1850--0ab5fcea9a6fd52e--s018-l0058`, `ia_poly1850--a89bd2c9bdb1ca6d--s025-l0022`, `bsb_poly1850--0ab5fcea9a6fd52e--s007-l0062`, `bsb_poly1850--0ab5fcea9a6fd52e--s005-l0072`, `bsb_poly1850--0ab5fcea9a6fd52e--s023-l0059`, `ia_poly1850--36dcee7ce4c29f8b--s016-l0040`, `bsb_poly1850--0ab5fcea9a6fd52e--s005-l0055`, `ia_poly1850--36dcee7ce4c29f8b--s013-l0087`
- `test:short` (1): `ia_russian--03b43bc5289ad8ce--s007-l0014`
- `test:vertical_turned` (4): `ia_poly1850--36dcee7ce4c29f8b--s005-l0061`, `ia_poly1850--36dcee7ce4c29f8b--s038-l0079`, `ia_poly1850--36dcee7ce4c29f8b--s024-l0089`, `ia_poly1850--36dcee7ce4c29f8b--s025-l0083`


Notes on the table:
- **Deficit** = quota − sealed. It combines the draw's supply deficits (no supply, or Serbian-only modern Cyrillic) with the UNFILLED slots left by LF1. Nothing is padded.
- **Editions** counts distinct `doc` (edition) ids.
- **Replacements** are reserve lines promoted under the coordinator's rule: same quota_scope and source, ascending overdraw_order, non-OK reserves skipped, pairing ascending scope_rank.

## LF1 diagnostics
- flagged 350 = REPLACED 248 + UNFILLED 102:
  - test: 298 = 211 + 87, giving 2,253 final;
  - dev: 52 = 37 + 15, giving 438 final;
  - in-quota 2,340 + 453 − 102 = 2,691.
- The vertical control context `vert_w1a_w2_00003` over-flagged 3 horizontal controls as "turned" under the vertical statement. These are over-flags only; no bad line was admitted. This records LF1's strictness, not a seal fault.
- LF1 v1's final list paired replacements in emission order. The seal enforces ascending scope_rank pairing, and job 3705061 failed on it. LF1 re-finalised with the same 2,691 rows and the same 248/102 (v2 above). The seal check was not changed.

## Finding: one pixel-identical image is in both test and dev
- `image_sha256` `4b22b2ff40ca5b79195fd9e735a7d15c25f56bb3dac2d8eb904a16d02ff0dafb` (reference "НБС", the National Bank of Serbia masthead) appears twice:
  - test `serbia--d6030713c8d88c96--s005-l0006` (test:font_extremes:small, edition `122c52e6…`);
  - dev `serbia--27b182bf4116728f--s009-l0006` (dev:font_extremes:small, edition `b864d188…`).
- These are two different editions, so the edition split holds. But the bytes are identical, which is why the receipt reports 2,690 images for 2,691 rows.
- The seal checks image hashes per row, not test↔dev pixel overlap. This record leaves the decision to the coordinator (e.g. drop the dev row as a dev deficit of 1); the sealed suite is unchanged.

### Coordinator ruling (20 Oct)
- The dev row `serbia--27b182bf4116728f--s009-l0006` is **dropped**; test keeps `serbia--d6030713c8d88c96--s005-l0006`.
- This is done as **seal04**, not an erratum. The seal gains:
  - a test↔dev pixel-overlap check: identical `image_sha256` across panels drops the dev row, which is recorded under an explicit receipt key and counted as a dev deficit;
  - a check that no `image_sha256` repeats within a panel.
- The package is SEAL02D. It is deployed only after ASTRA-CP3 on seal03 returns, so that any CP3 HIGH on the seal goes into the same package. seal03 stays as it is.

## What the references certify (ASTRA-CP3 M1)
The references are the pipeline's corrected labels, filtered by LF1. An LF1 `OK` certifies that the crop obeys the segmentation rules and that the **letters** match the image. It does **not** certify diacritics: accents, breathings, iota subscript and dialytika. Benchmark 0.2 is therefore a pipeline-reference, letter- and crop-filtered instrument whose **diacritics are unqualified**.

Scores on diacritic-sensitive measures (strict NFD CER, mark metrics) measure agreement with the pipeline's marks, not with verified print. Report them that way. The diacritic-insensitive measures are the ones LF1 qualifies.

## ASTRA-CP3 outcome (20 Oct)
- Release v3 passes.
- HIGH 1 is the dev/test identical-crop collision above, fixed in seal04 (package fdaf8ca2).
- There are no other seal findings.

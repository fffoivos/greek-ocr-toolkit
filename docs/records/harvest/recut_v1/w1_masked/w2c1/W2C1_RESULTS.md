# W2C1 results — complete letters/crop check

Included 16/16 contexts; VOID originals are excluded permanently. Replacements are used only after a clean canonical scan and complete mapping.

C1 bars: letters ≥90% and crop_ok ≥90%, point estimates on 100 bed cards per stratum. Source: [C1_REPORT.md](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/C1_REPORT.md). Controls are excluded from bed denominators; >1 control error flags a context and prevents a passing stratum. Missing contexts are pending, never zero-score cards. `u` stays in the denominator and is not an exact match.

Letters exact-match means `letters=y` under LABEL_CHECK_v2 (base letters/digits/words and script; diacritics ignored). These are reader label-quality calls, not independent reader-accuracy measurements.

| Stratum | Bed cards | Letters exact match | crop_ok | Controls passed | Observed ≥90% bars | Stratum pass/fail |
|---|---:|---:|---:|---:|---|---|
| bsb_poly1850_poly1850 | 100/100 | 92/100 (92.0%) | 94/100 (94.0%) | 9/10 | PASS | PASS |
| ia_poly1850_poly1850 | 100/100 | 99/100 (99.0%) | 89/100 (89.0%) | 10/10 | FAIL | FAIL |
| nlg_poly1850 | 100/100 | 93/100 (93.0%) | 88/100 (88.0%) | 10/10 | FAIL | FAIL |
| nlg_poly1900 | 100/100 | 97/100 (97.0%) | 89/100 (89.0%) | 10/10 | FAIL | FAIL |
| nlg_greek_poly | 100/100 | 100/100 (100.0%) | 89/100 (89.0%) | 10/10 | FAIL | FAIL |
| serbia_cyrillic | 100/100 | 96/100 (96.0%) | 98/100 (98.0%) | 10/10 | PASS | PASS |
| elstat_numerics_tables | 100/100 | 99/100 (99.0%) | 99/100 (99.0%) | 10/10 | PASS | PASS |
| gazette_modern_modern_scanned | 100/100 | 98/100 (98.0%) | 84/100 (84.0%) | 10/10 | FAIL | FAIL |

Marks: pending Opus for grave-heavy strata; all Sol whole-line mark calls are excluded from decisions under HANDOVER §§1, 3. No marks pass or admission is claimed. Partial observed gates do not establish a 100-card stratum result.

## Context custody

- `w2c1_bsb_poly1850_poly1850/c1`: included; controls 5/5; weekly probe before/after 6%/7% (recorded, not live)
- `w2c1_bsb_poly1850_poly1850/c2`: included; controls 4/5; weekly probe before/after 7%/7% (recorded, not live)
- `w2c1_ia_poly1850_poly1850/c1`: included; controls 5/5; weekly probe before/after 7%/7% (recorded, not live)
- `w2c1_ia_poly1850_poly1850/c2`: included; controls 5/5; weekly probe before/after 7%/7% (recorded, not live)
- `w2c1_nlg_poly1850/c1`: included; controls 5/5; weekly probe before/after 7%/7% (recorded, not live)
- `w2c1_nlg_poly1850/c2`: included; controls 5/5; weekly probe before/after 7%/7% (recorded, not live)
- `w2c1_nlg_poly1900_r2/c1`: included; controls 5/5; weekly probe before/after 7%/7% (recorded, not live)
- `w2c1_nlg_poly1900_r2/c2`: included; controls 5/5; weekly probe before/after 7%/7% (recorded, not live)
- `w2c1_nlg_greek_poly_r2/c1`: included; controls 5/5; weekly probe before/after 7%/7% (recorded, not live)
- `w2c1_nlg_greek_poly/c2`: included; controls 5/5; weekly probe before/after 7%/7% (recorded, not live)
- `w2c1_serbia_cyrillic/c1`: included; controls 5/5; weekly probe before/after 7%/7% (recorded, not live)
- `w2c1_serbia_cyrillic/c2`: included; controls 5/5; weekly probe before/after 7%/7% (recorded, not live)
- `w2c1_elstat_numerics_tables/c1`: included; controls 5/5; weekly probe before/after 7%/7% (recorded, not live)
- `w2c1_elstat_numerics_tables/c2`: included; controls 5/5; weekly probe before/after 7%/7% (recorded, not live)
- `w2c1_gazette_modern_modern_scanned/c1`: included; controls 5/5; weekly probe before/after 7%/7% (recorded, not live)
- `w2c1_gazette_modern_modern_scanned_r2/c2`: included; controls 5/5; weekly probe before/after 7%/7% (recorded, not live)

Canonical scanner SHA-256: `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`. JSON records all scoring input hashes. Reports are deterministic and use no network, probe, reader, or live features file.

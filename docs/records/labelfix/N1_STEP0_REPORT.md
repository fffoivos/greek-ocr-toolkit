# N1 step 0: numeric separators census and convention recommendation

17 October 2026. Step 0 only; lead convention ruling pending.

Implemented a text-only tokenizer and froze an unrendered frame. No image was opened, decoded, rendered or read; no recognizer or model was run, no network tool was used, and no `.git` command or write was made. Dashes remain tags/proposals only. No labels, codecs or external inputs were modified.

## Scope and counting

W1 is counted on its `text` field (Google text), over all lines regardless of admission/quality gate. Source and year come from W1 metadata. Gazette is split into 1982–85 and 1986–90; ELSTAT spans its supplied historical years. Every other W1 source reaches 100 numeric tokens and is included. Source data and card metadata were read only as text; source pixels remain unread.

Tokens are maximal ASCII-digit runs joined by the specified separator candidates, including U+00B7 and U+0387 separately, and ordinary spaces. All adjacent digit pairs yield an inner slot, including zero-length gaps; each token adds two boundary slots. Thus a token with D digits has D+1 slots. Offsets are half-open Python character offsets into the original line, not pixel coordinates. Boundary glyphs capture adjacent nonspace separators. `NONE_TEXT` means an empty text span, not a fabricated printed `none` verdict.

Grammar labels propose thousands groups (initial 1–3 digits then groups of three), decimal suffixes (comma/period before 1–2 final digits), ascending year/page-style ranges (two groups of 1–4 digits), and text-indicated table boundaries (multiple spaces or an adjacent pipe/tab). Remaining slots are `other`. Range has priority over thousands when both apply; alternative candidates remain in the tokenizer and frame. A space-separated table can be mistaken for grouping; text cannot locate an unprinted gap or prove a table edge. No grammar label authorizes correction.

The hyphen class counts U+002D occurrences in **inner** slots of tokens with at least four **total** digits. It includes true ranges; it is a candidate population, not an error count. Token counts containing such hyphens are also recorded in the census.

## W1 census

| Source / era | Lines | Numeric tokens | Slots | Inner / boundary | Hyphens in 4+ digit tokens |
|---|---:|---:|---:|---:|---:|
| bsb_poly1850 | 12774 | 4635 | 15394 | 6124 / 9270 | 55 |
| elstat | 5044 | 4004 | 24867 | 16859 / 8008 | 161 |
| gazette_1982_1985 | 4786 | 2635 | 10135 | 4865 / 5270 | 58 |
| gazette_1986_1990 | 24728 | 17344 | 88936 | 54248 / 34688 | 353 |
| ia_greek_latin | 11755 | 6182 | 22457 | 10093 / 12364 | 195 |
| ia_poly1850 | 16022 | 5950 | 21872 | 9972 / 11900 | 210 |
| ia_russian | 2963 | 1044 | 3374 | 1286 / 2088 | 18 |
| kosmopolis | 5356 | 299 | 1076 | 478 / 598 | 3 |
| lekythos | 13407 | 528 | 2222 | 1166 / 1056 | 8 |
| nlg | 2220 | 234 | 781 | 313 / 468 | 5 |
| serbia | 2043 | 512 | 4072 | 3048 / 1024 | 12 |
| **Total** | **101098** | **43367** | **195186** | **108452 / 86734** | **1078** |

All tables count primary grammar labels once per slot. Code-point sequences preserve compound gaps; U+0020 is space. Empty slots and boundaries are included, so table totals equal slot totals.

### bsb_poly1850

| Google/label glyph code points | Thousands | Decimal | Range | Table boundary | Other |
|---|---:|---:|---:|---:|---:|
| NONE_TEXT | 0 | 0 | 0 | 134 | 12425 |
| U+0020 | 0 | 0 | 0 | 0 | 68 |
| U+0020+U+002D+U+0020 | 0 | 0 | 1 | 0 | 0 |
| U+0020+U+2013+U+0020 | 0 | 0 | 0 | 0 | 1 |
| U+002C | 5 | 8 | 0 | 0 | 554 |
| U+002C+U+0020 | 0 | 0 | 0 | 0 | 695 |
| U+002D | 0 | 0 | 25 | 0 | 25 |
| U+002D+U+002D | 0 | 0 | 0 | 0 | 1 |
| U+002D+U+002E | 0 | 0 | 0 | 0 | 14 |
| U+002E | 1 | 51 | 0 | 0 | 1073 |
| U+002E+U+0020 | 0 | 0 | 0 | 0 | 217 |
| U+002E+U+0020+U+002D | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+0020+U+002D+U+0020 | 0 | 0 | 0 | 0 | 11 |
| U+002E+U+002D | 0 | 0 | 0 | 0 | 68 |
| U+002E+U+002D+U+0020 | 0 | 0 | 0 | 0 | 12 |
| U+002E+U+002D+U+002E | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+2014 | 0 | 0 | 0 | 0 | 1 |
| U+00B7 | 0 | 0 | 0 | 0 | 2 |

### elstat

| Google/label glyph code points | Thousands | Decimal | Range | Table boundary | Other |
|---|---:|---:|---:|---:|---:|
| NONE_TEXT | 0 | 0 | 0 | 0 | 20031 |
| U+0020 | 107 | 0 | 0 | 0 | 743 |
| U+0020+U+002D+U+0020 | 0 | 0 | 1 | 0 | 0 |
| U+0020+U+2013+U+0020 | 0 | 0 | 1 | 0 | 0 |
| U+002C | 80 | 574 | 0 | 0 | 145 |
| U+002C+U+0020 | 0 | 0 | 0 | 0 | 1 |
| U+002D | 49 | 0 | 68 | 0 | 49 |
| U+002D+U+0020 | 0 | 0 | 2 | 0 | 3 |
| U+002E | 1291 | 70 | 0 | 0 | 1641 |
| U+002E+U+0020 | 0 | 0 | 0 | 0 | 3 |
| U+002E+U+002E | 0 | 0 | 0 | 0 | 2 |
| U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 2 |
| U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+002E+U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+0020 | 0 | 0 | 0 | 0 | 1 |

### gazette_1982_1985

| Google/label glyph code points | Thousands | Decimal | Range | Table boundary | Other |
|---|---:|---:|---:|---:|---:|
| NONE_TEXT | 0 | 0 | 0 | 0 | 8975 |
| U+0020 | 0 | 0 | 0 | 0 | 55 |
| U+0020+U+002D+U+0020 | 0 | 0 | 2 | 0 | 1 |
| U+0020+U+2013+U+0020 | 0 | 0 | 0 | 0 | 2 |
| U+002C | 1 | 52 | 0 | 0 | 66 |
| U+002C+U+0020 | 0 | 0 | 0 | 0 | 23 |
| U+002D | 0 | 0 | 16 | 0 | 50 |
| U+002D+U+002D | 0 | 0 | 0 | 0 | 1 |
| U+002D+U+002D+U+002D | 0 | 0 | 0 | 0 | 1 |
| U+002D+U+002D+U+002D+U+002D | 0 | 0 | 0 | 0 | 1 |
| U+002E | 25 | 148 | 0 | 0 | 684 |
| U+002E+U+0020 | 0 | 0 | 0 | 0 | 3 |
| U+002E+U+002C | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+002E | 0 | 0 | 0 | 0 | 8 |
| U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 12 |
| U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 4 |
| U+002E+U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 2 |
| U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 1 |

### gazette_1986_1990

| Google/label glyph code points | Thousands | Decimal | Range | Table boundary | Other |
|---|---:|---:|---:|---:|---:|
| NONE_TEXT | 0 | 0 | 0 | 9 | 74444 |
| U+0020 | 237 | 0 | 0 | 0 | 496 |
| U+0020+U+002D+U+0020 | 0 | 0 | 4 | 0 | 28 |
| U+0020+U+002E+U+002E+U+002E+U+0020 | 0 | 0 | 0 | 0 | 2 |
| U+0020+U+2013+U+0020 | 0 | 0 | 4 | 0 | 4 |
| U+002C | 702 | 118 | 0 | 0 | 817 |
| U+002C+U+0020 | 0 | 0 | 0 | 0 | 117 |
| U+002C+U+002E | 0 | 0 | 0 | 0 | 1 |
| U+002C+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 1 |
| U+002D | 3 | 0 | 66 | 0 | 405 |
| U+002D+U+0020 | 0 | 0 | 6 | 0 | 5 |
| U+002D+U+002D | 0 | 0 | 0 | 0 | 4 |
| U+002D+U+002D+U+002D+U+002D | 0 | 0 | 0 | 0 | 1 |
| U+002E | 5544 | 783 | 0 | 0 | 5030 |
| U+002E+U+0020 | 0 | 0 | 0 | 0 | 14 |
| U+002E+U+0020+U+002D+U+0020 | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+0020+U+2013+U+0020 | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+002C | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+002D | 0 | 0 | 0 | 0 | 41 |
| U+002E+U+002D+U+0020 | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+002D+U+002E | 0 | 0 | 0 | 0 | 2 |
| U+002E+U+002E | 0 | 0 | 0 | 0 | 17 |
| U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 8 |
| U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 4 |
| U+002E+U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+002E+U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 4 |
| U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 2 |
| U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 2 |
| U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+2013 | 0 | 0 | 0 | 0 | 2 |
| U+00B7 | 0 | 0 | 0 | 0 | 1 |
| U+00B7+U+002C | 0 | 0 | 0 | 0 | 1 |
| U+00B7+U+002D | 0 | 0 | 0 | 0 | 1 |

### ia_greek_latin

| Google/label glyph code points | Thousands | Decimal | Range | Table boundary | Other |
|---|---:|---:|---:|---:|---:|
| NONE_TEXT | 0 | 0 | 0 | 56 | 17826 |
| U+0020 | 16 | 0 | 0 | 0 | 99 |
| U+002C | 2 | 20 | 0 | 0 | 412 |
| U+002C+U+0020 | 0 | 0 | 0 | 0 | 900 |
| U+002C+U+002D | 0 | 0 | 0 | 0 | 1 |
| U+002C+U+002E | 0 | 0 | 0 | 0 | 1 |
| U+002D | 3 | 0 | 73 | 0 | 179 |
| U+002E | 6 | 188 | 0 | 0 | 1726 |
| U+002E+U+0020 | 0 | 0 | 0 | 0 | 915 |
| U+002E+U+002C | 0 | 0 | 0 | 0 | 11 |
| U+002E+U+002C+U+002C | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+002C+U+002D | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+002D | 0 | 0 | 0 | 0 | 4 |
| U+002E+U+002D+U+002D+U+002D | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+002E | 0 | 0 | 0 | 0 | 3 |
| U+00B7 | 0 | 0 | 0 | 0 | 1 |
| U+2013 | 0 | 0 | 0 | 0 | 12 |

### ia_poly1850

| Google/label glyph code points | Thousands | Decimal | Range | Table boundary | Other |
|---|---:|---:|---:|---:|---:|
| NONE_TEXT | 0 | 0 | 0 | 35 | 17533 |
| U+0020 | 13 | 0 | 0 | 0 | 49 |
| U+0020+U+002D | 0 | 0 | 0 | 0 | 2 |
| U+0020+U+002D+U+0020 | 0 | 0 | 1 | 0 | 0 |
| U+0020+U+2013+U+0020 | 0 | 0 | 0 | 0 | 1 |
| U+002C | 0 | 36 | 0 | 0 | 372 |
| U+002C+U+0020 | 0 | 0 | 0 | 0 | 876 |
| U+002C+U+002C | 0 | 0 | 0 | 0 | 1 |
| U+002D | 6 | 0 | 130 | 0 | 125 |
| U+002E | 12 | 43 | 0 | 0 | 2211 |
| U+002E+U+0020 | 0 | 0 | 0 | 0 | 413 |
| U+002E+U+002C | 0 | 0 | 0 | 0 | 4 |
| U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 1 |
| U+00B7 | 0 | 0 | 0 | 0 | 2 |
| U+2013 | 0 | 0 | 1 | 0 | 2 |
| U+2014 | 0 | 0 | 0 | 0 | 3 |

### ia_russian

| Google/label glyph code points | Thousands | Decimal | Range | Table boundary | Other |
|---|---:|---:|---:|---:|---:|
| NONE_TEXT | 0 | 0 | 0 | 0 | 3058 |
| U+0020 | 0 | 0 | 0 | 0 | 9 |
| U+0020+U+2014+U+0020 | 0 | 0 | 2 | 0 | 0 |
| U+002C | 27 | 0 | 0 | 0 | 50 |
| U+002C+U+0020 | 0 | 0 | 0 | 0 | 12 |
| U+002D | 0 | 0 | 19 | 0 | 61 |
| U+002D+U+002D | 0 | 0 | 0 | 0 | 2 |
| U+002D+U+2014 | 0 | 0 | 0 | 0 | 1 |
| U+002E | 0 | 0 | 0 | 0 | 124 |
| U+002E+U+0020 | 0 | 0 | 0 | 0 | 3 |
| U+002E+U+002D | 0 | 0 | 0 | 0 | 1 |
| U+2014 | 0 | 0 | 4 | 0 | 1 |

### kosmopolis

| Google/label glyph code points | Thousands | Decimal | Range | Table boundary | Other |
|---|---:|---:|---:|---:|---:|
| NONE_TEXT | 0 | 0 | 0 | 0 | 1017 |
| U+002C | 0 | 1 | 0 | 0 | 13 |
| U+002C+U+0020 | 0 | 0 | 0 | 0 | 6 |
| U+002D | 0 | 0 | 4 | 0 | 4 |
| U+002E | 0 | 0 | 0 | 0 | 27 |
| U+002E+U+002E | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+2013 | 0 | 0 | 0 | 0 | 1 |
| U+00B7 | 0 | 0 | 0 | 0 | 1 |
| U+2013 | 0 | 0 | 1 | 0 | 0 |

### lekythos

| Google/label glyph code points | Thousands | Decimal | Range | Table boundary | Other |
|---|---:|---:|---:|---:|---:|
| NONE_TEXT | 0 | 0 | 0 | 0 | 2043 |
| U+0020 | 4 | 0 | 0 | 0 | 19 |
| U+0020+U+002D | 0 | 0 | 0 | 0 | 1 |
| U+002C | 8 | 2 | 0 | 0 | 10 |
| U+002C+U+0020 | 0 | 0 | 0 | 0 | 5 |
| U+002C+U+002D | 0 | 0 | 0 | 0 | 1 |
| U+002D | 0 | 0 | 3 | 0 | 15 |
| U+002E | 44 | 7 | 0 | 0 | 50 |
| U+002E+U+0020 | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+002D | 0 | 0 | 0 | 0 | 7 |
| U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 2 |

### nlg

| Google/label glyph code points | Thousands | Decimal | Range | Table boundary | Other |
|---|---:|---:|---:|---:|---:|
| NONE_TEXT | 0 | 0 | 0 | 0 | 703 |
| U+0020+U+2013+U+0020 | 0 | 0 | 1 | 0 | 0 |
| U+002C | 0 | 0 | 0 | 0 | 18 |
| U+002C+U+0020 | 0 | 0 | 0 | 0 | 3 |
| U+002D | 0 | 0 | 3 | 0 | 3 |
| U+002E | 0 | 2 | 0 | 0 | 45 |
| U+002E+U+0020 | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 2 |

### serbia

| Google/label glyph code points | Thousands | Decimal | Range | Table boundary | Other |
|---|---:|---:|---:|---:|---:|
| NONE_TEXT | 0 | 0 | 0 | 11 | 2858 |
| U+0020 | 0 | 0 | 0 | 0 | 348 |
| U+002C | 0 | 148 | 0 | 0 | 256 |
| U+002C+U+0020 | 0 | 0 | 0 | 0 | 3 |
| U+002C+U+002D+U+0020 | 0 | 0 | 0 | 0 | 3 |
| U+002C+U+002D+U+002D+U+0020 | 0 | 0 | 0 | 0 | 1 |
| U+002D | 0 | 0 | 3 | 0 | 7 |
| U+002D+U+0020 | 0 | 0 | 0 | 0 | 1 |
| U+002E | 17 | 63 | 0 | 0 | 331 |
| U+002E+U+0020 | 0 | 0 | 0 | 0 | 18 |
| U+002E+U+002D+U+0020 | 0 | 0 | 0 | 0 | 2 |
| U+002E+U+002E | 0 | 0 | 0 | 0 | 1 |
| U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 1 |

## Collection-v2 / E3 label census

Input paths were found through toolkit `docs/records/reviews/ASTRA-R2design_brief.md` and `docs/records/labelfix/candidates_train_sample.md`: `~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_{train,dev,test}.jsonl`. Each split is read once; `all` is not added again. Train is the training-label population; dev and test are separate convention checks.

E3's `~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/E3_RESULTS.md` reports 207,851 real training rows after codec, mixed with synthetic data. This census also reconstructs codec eligibility using NFD, the enumerated folds parsed from `factory/src/codec.rs`, whitespace collapse, and the v1 atom inventory, matching `bench/o5_prepare.py` / `bench/codec_coverage.py`. The reconstructed eligible train set has 207,867 rows, 16 more than the 207,851 reported in E3_RESULTS; this mismatch remains unresolved. It has 38,649 numeric tokens, 142,842 slots, 1 raised dot in an inner gap (with a following space), and 1,039 inner hyphens in 4+-digit tokens. This is an input-label/encoding census, not a checkpoint-specific draw ledger or a synthetic-training census. Original source labels and normalized codec-eligible tables are both retained per source/era in `census.json`. Collection-v2 era metadata are used as supplied; E3_RESULTS flags old Open Archives date metadata as unreliable, so those years are not asserted as verified publication dates.

| Split | Source rows | Numeric tokens | Slots | Inner hyphens, 4+ digits | U+00B7 all / between digits | U+0387 all / between digits | Codec-eligible rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| train | 214436 | 40602 | 149741 | 1074 | 7432 / 0 | 0 / 0 | 207867 |
| dev | 13522 | 1780 | 6182 | 68 | 342 / 0 | 0 / 0 | 13158 |
| test | 44029 | 5424 | 19726 | 114 | 1382 / 0 | 0 / 0 | 42038 |

### Training labels: all source rows

| Google/label glyph code points | Thousands | Decimal | Range | Table boundary | Other |
|---|---:|---:|---:|---:|---:|
| NONE_TEXT | 0 | 0 | 0 | 11 | 125576 |
| U+0020 | 23 | 0 | 0 | 0 | 132 |
| U+0020+U+002C | 0 | 0 | 0 | 0 | 1 |
| U+0020+U+002D | 0 | 0 | 3 | 0 | 0 |
| U+0020+U+002D+U+0020 | 0 | 0 | 36 | 0 | 5 |
| U+0020+U+2013+U+0020 | 0 | 0 | 18 | 0 | 6 |
| U+0020+U+2014+U+0020 | 0 | 0 | 2 | 0 | 0 |
| U+002C | 394 | 380 | 0 | 0 | 4390 |
| U+002C+U+0020 | 0 | 0 | 0 | 0 | 1542 |
| U+002C+U+002D | 0 | 0 | 0 | 0 | 2 |
| U+002C+U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 1 |
| U+002D | 14 | 0 | 611 | 0 | 928 |
| U+002D+U+0020 | 0 | 0 | 3 | 0 | 4 |
| U+002D+U+002D | 0 | 0 | 0 | 0 | 9 |
| U+002D+U+002D+U+002D | 0 | 0 | 0 | 0 | 2 |
| U+002E | 933 | 1325 | 0 | 0 | 9261 |
| U+002E+U+0020 | 0 | 0 | 0 | 0 | 3765 |
| U+002E+U+0020+U+2014+U+0020 | 0 | 0 | 0 | 0 | 2 |
| U+002E+U+002C | 0 | 0 | 0 | 0 | 25 |
| U+002E+U+002C+U+0020 | 0 | 0 | 0 | 0 | 59 |
| U+002E+U+002D | 0 | 0 | 0 | 0 | 56 |
| U+002E+U+002E | 0 | 0 | 0 | 0 | 15 |
| U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 9 |
| U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 2 |
| U+002E+U+2014 | 0 | 0 | 0 | 0 | 1 |
| U+00B7 | 0 | 0 | 0 | 0 | 108 |
| U+00B7+U+0020 | 0 | 0 | 0 | 0 | 1 |
| U+00B7+U+002D | 0 | 0 | 0 | 0 | 1 |
| U+2013 | 0 | 0 | 40 | 0 | 37 |
| U+2013+U+2013 | 0 | 0 | 0 | 0 | 1 |
| U+2014 | 0 | 0 | 6 | 0 | 1 |

### Training labels: normalized codec-eligible rows

| Google/label glyph code points | Thousands | Decimal | Range | Table boundary | Other |
|---|---:|---:|---:|---:|---:|
| NONE_TEXT | 0 | 0 | 0 | 0 | 119456 |
| U+0020 | 23 | 0 | 0 | 0 | 126 |
| U+0020+U+002C | 0 | 0 | 0 | 0 | 1 |
| U+0020+U+002D | 0 | 0 | 3 | 0 | 0 |
| U+0020+U+002D+U+0020 | 0 | 0 | 35 | 0 | 4 |
| U+0020+U+2013+U+0020 | 0 | 0 | 18 | 0 | 6 |
| U+0020+U+2014+U+0020 | 0 | 0 | 1 | 0 | 0 |
| U+002C | 392 | 373 | 0 | 0 | 4254 |
| U+002C+U+0020 | 0 | 0 | 0 | 0 | 1532 |
| U+002C+U+002D | 0 | 0 | 0 | 0 | 2 |
| U+002D | 14 | 0 | 559 | 0 | 893 |
| U+002D+U+0020 | 0 | 0 | 3 | 0 | 4 |
| U+002D+U+002D | 0 | 0 | 0 | 0 | 7 |
| U+002D+U+002D+U+002D | 0 | 0 | 0 | 0 | 2 |
| U+002E | 910 | 1312 | 0 | 0 | 8814 |
| U+002E+U+0020 | 0 | 0 | 0 | 0 | 3744 |
| U+002E+U+0020+U+2014+U+0020 | 0 | 0 | 0 | 0 | 2 |
| U+002E+U+002C | 0 | 0 | 0 | 0 | 22 |
| U+002E+U+002C+U+0020 | 0 | 0 | 0 | 0 | 58 |
| U+002E+U+002D | 0 | 0 | 0 | 0 | 54 |
| U+002E+U+002E | 0 | 0 | 0 | 0 | 15 |
| U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 9 |
| U+002E+U+002E+U+002E+U+002E | 0 | 0 | 0 | 0 | 2 |
| U+002E+U+2014 | 0 | 0 | 0 | 0 | 1 |
| U+00B7 | 0 | 0 | 0 | 0 | 107 |
| U+00B7+U+0020 | 0 | 0 | 0 | 0 | 1 |
| U+00B7+U+002D | 0 | 0 | 0 | 0 | 1 |
| U+2013 | 0 | 0 | 40 | 0 | 37 |
| U+2013+U+2013 | 0 | 0 | 0 | 0 | 1 |
| U+2014 | 0 | 0 | 4 | 0 | 0 |

### Training labels by source / era

| Source / era | Rows | Tokens | Slots | Hyphens in 4+ digits |
|---|---:|---:|---:|---:|
| anemi_round1 | 46964 | 5463 | 18090 | 104 |
| vouli_parliament_1850s | 24938 | 3339 | 12091 | 27 |
| anemi_round2 | 18782 | 2146 | 7611 | 53 |
| parliament_proceedings_1975_2000 | 64521 | 9630 | 35672 | 479 |
| openarchives_Dione | 2059 | 389 | 1510 | 16 |
| openarchives_ntua | 1420 | 262 | 853 | 1 |
| openarchives_ktisis | 2037 | 330 | 1148 | 11 |
| openarchives_kallipos | 2184 | 697 | 2473 | 12 |
| openarchives_apothesis | 1657 | 421 | 1313 | 0 |
| openarchives_Pandemos | 2443 | 684 | 2425 | 19 |
| openarchives_nemertes | 1608 | 353 | 1299 | 14 |
| openarchives_KEIED | 2050 | 489 | 1671 | 22 |
| openarchives_anaktisis | 2088 | 314 | 1226 | 9 |
| openarchives_hellanicus | 2079 | 568 | 2381 | 32 |
| anemi_mixed | 14663 | 1290 | 4329 | 26 |
| openarchives_mixed_kallipos | 33 | 9 | 24 | 0 |
| openarchives_mixed_KEIED | 512 | 432 | 2115 | 84 |
| openarchives_mixed_ntua | 30 | 0 | 0 | 0 |
| openarchives_mixed_anaktisis | 488 | 193 | 637 | 6 |
| openarchives_mixed_Pandemos | 60 | 22 | 78 | 3 |
| openarchives_mixed_Dione | 502 | 164 | 559 | 2 |
| openarchives_mixed_apothesis | 678 | 492 | 2119 | 57 |
| openarchives_mixed_hellanicus | 335 | 229 | 813 | 13 |
| openarchives_mixed_ktisis | 571 | 126 | 453 | 3 |
| openarchives_mixed_nemertes | 46 | 18 | 59 | 0 |
| archive_b28038630 | 9665 | 8736 | 35606 | 8 |
| archive_AA9613308335D0B014B | 1712 | 799 | 2959 | 0 |
| archive_b24878935 | 1193 | 4 | 9 | 0 |
| archive_bub_gb_Cmg6AQAAIAAJ | 1531 | 304 | 1220 | 7 |
| archive_bub_gb_mG0mAQAAIAAJ | 1558 | 328 | 1176 | 10 |
| archive_izvestiianabul25192530bul | 1438 | 449 | 1537 | 21 |
| archive_izvestiianabulga610193138bulg | 1225 | 303 | 1045 | 6 |
| archive_izvestiianatsars12192829tsar | 783 | 381 | 1199 | 10 |
| archive_izvestiianatsars1516194243tsar | 1008 | 623 | 2093 | 6 |
| archive_sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930 | 1575 | 615 | 1948 | 13 |

The full glyph × grammar tables for every training source/era and all three splits are in `collection_v2` in the census JSON.

## Convention recommendation

**Recommend U+00B7 MIDDLE DOT. The lead rules; no convention was changed.** Both inspected codec versions have a U+00B7 atom, no U+0387 atom, and explicitly specify NFD with U+0387 → U+00B7. Python's local Unicode normalization independently produces that decomposition. v1 is the requested toolkit vendor file; no v2 exists beside it, so v2 was checked at `~/Projects/greek-page-ocr/codec/v2.json`. Exact atom records, policies and input hashes are in `census.json`.

Training labels use U+00B7 as prose punctuation (examples with line IDs and character offsets are in `collection_v2.train.unicode`). Neither dot code point occurs directly between digits in train, dev or test. There is one space-adjacent numeric-context exception in both the raw and normalized eligible train set: `6cc7ddf6ed4e-p000005-l0080`, `185· 95 εἶπον ὄχι, 85 εἶπον ναί, 5 ἠρνήθησαν ψῆφον·`. Its inner gap is `· `, classified `other`, not thousands. It may be prose punctuation between numbers; pixels were not checked. Thus no direct digit–dot–digit or grammar-thousands raised-dot supervision was found, but a broader numeric-token census does contain this one dot. Its numeric hyphens include valid ranges and cannot be called wrong without ink. Raised dots should map to U+00B7 under the current codec contract; preserve raw input code points in audit metadata.

## C1 evidence and exclusions

- `elstat__numerics_tables` / `c013` / `elstat--c5f7ea1f26d39839--s000-l0367`: 555,6 → 555.6

- `elstat__numerics_tables` / `c038` / `elstat--ee37bc488988f1bd--s000-l0445`: 4·547·331 (mid-height dots) → 4-547-331

- `elstat__numerics_tables` / `c093` / `elstat--ee37bc488988f1bd--s000-l0457`: · → - (twice: 4·479·781 → 4-479-781)

- `ia_poly1850__latin` / `c008` / `ia_poly1850--c39403323b6d5d89--s005-l0007`: 255—6 (em dash) → 255-6; next line's upper halves readable at bottom ('abies defendatur')

- `ia_poly1850__mixed_greek_latin` / `c014` / `ia_poly1850--6a9e5e4676cec552--s002-l0035`: Ἀκροασις → Ακροασις; 110—133 → 110-133

- `nlg__poly1850` / `c032` / `nlg--3d71f4f87abea186--s002-l0032`: Ὀδ. → Οδ.; 485—488 → 485-488

Read 1400 existing verdict records. Excluded all 6797 line IDs found in W1 C1 key files, including supplemental cards, from both sample partitions. Existing C1 separator entries are evidence anchors only; no new glyph verdicts were produced.

## Frozen sampling frame

Seed **20261017**. `frame_step1.jsonl` contains **900 rows**: select `partition == "step1"` for the **600-slot** development frame, and `partition == "locked_eval"` for **300 locked slots**. All truth fields are null and rendered flags false. Frame rows carry crop paths/hashes for future use, token/slot character offsets and Google glyphs; pixel localization/alignment remains step 1 work.

Before development sampling, shuffled document lists reserve a quarter of each target source/era's documents, at least two, expanding only if 100 slots are unavailable. Evaluation draws 100 slots each from ELSTAT, Gazette 1982–85 and Gazette 1986–90, preferentially 90 observed separator/table candidates then 10 remaining slots. All pages/lines of reserved documents are forbidden to N1 fitting, not just the chosen slots.

Development first draws 240 suspected inner-hyphen slots, balances remaining observed separator/table candidates up to 540, then fills to 600 with remaining slots. Allocation uses round-robin source/era × primary grammar × exact glyph cells, shuffling within cells; rare cells are retained and common cells are downweighted. This is an enriched diagnostic sample, not a population-rate sample. The final hyphen count can exceed 240 through other strata. Controls are not fabricated: the lead must pixel-verify and plant the 10% controls in step 1; sampling these slots is not verification.

step1 source allocations: bsb_poly1850 85, elstat 73, gazette_1982_1985 55, gazette_1986_1990 107, ia_greek_latin 70, ia_poly1850 76, ia_russian 37, kosmopolis 16, lekythos 35, nlg 10, serbia 36.

locked_eval source allocations: elstat 100, gazette_1982_1985 100, gazette_1986_1990 100.

The explicit development list has 167 documents; the reserved lock has 62. Both lists, all locked slot IDs, and all excluded C1 line IDs are in `locked_eval_docs.json`; both lists also appear in `census.json`. Document identity is `source:item`, covering every page. The lock is document-disjoint for N1 development; earlier C1 exposure is not erased or claimed absent.

## Validation and reproduction

Run `python3 scripts/numerics/n1_step0.py`, then `python3 scripts/numerics/n1_report.py`. The census binds each data/codec/card input by SHA-256. `python3 -m pytest --noconftest -q tests/test_numeric_tokens.py` passes **17 tests**, covering all requested fixtures plus U+0387, en/em dashes, decimal/grouping combinations, original offsets, empty gaps, signs, boundaries, multiple spaces and ambiguous ranges. The initial ordinary pytest invocation hit the existing autouse Torch fixture's x86_64/arm64 library mismatch before any test body; `--noconftest` runs this pure text suite without importing Torch. No model was loaded.

Artifact verification checks exact slot totals, table sums, 600/300 partition sizes, unique slot IDs, C1 exclusion, document disjointness, per-source locked quotas, null truth and unchanged crop hashes across partitions. Frame and document-lock byte hashes are replayed to check determinism. No tokenizer output is a printed-glyph judgment. Step 1 rendering/reading, control creation, fitting and convention adoption remain unperformed.

Final training-label comparison below uses numeric raised-dot inner occurrences versus the 4+-digit inner-hyphen class on the source train labels, not all prose dots/hyphens.

N1S0 READY: tokens 43367 slots 195186; hyphen-in-4+digit 1078 (ELSTAT 161, Gazette 411); training labels raised-dot 1 vs hyphen 1074; convention recommend U+00B7; frame 600 / locked 300; tests 17 passed

# Short non-numeric crops: what they are

Read-only. Built by `scripts/draw_samples.py`, `scripts/sheets.py`, `scripts/typology.py` and `scripts/typology_md.py`. Every crop was looked at by eye. The crops were viewed on contact sheets that keep each crop's aspect ratio and draw a red frame at the crop's edge, 10 crops per sheet and 18 sheets in all. The originals are listed in `samples.jsonl` (`viewed: true`).

## How the sample was drawn

- Pool: short (chars ≤ 9), non-numeric (the definitions are in `size_vs_output.md`), non-vertical (height ≤ width) crops from the 150, the 888 and W1, deduplicated by line_id with the order 150 > 888 > W1. The pool has **6,700** crops: W1 6,586, 888 102, 150 12. The 888 and 150 rows are also W1 or W2 census rows.
- **Uniform sample:** `random.Random(20261019).sample(pool sorted by (population, line_id), 120)`. It drew 118 W1 crops, 1 from the 888 and 1 from the 150. The counts in the main table come from this sample.
- **Owner supplement (59 crops, beyond the ~120 asked for):** every other short non-numeric crop from the 150 (11) and every other owner-rated one from the 888 (48). I added these to tie each type to the owner's verdicts. They are counted separately and do not enter the uniform percentages.
- W1 crops are not on this Mac (`collect-v3-data/run/W1/crops/` is empty). I rebuilt the 266 W1 crops I needed in memory from the local page cache (`collect-v3-data/run/cache/pages/<crop_source_sha256>.jpg`, using `crop_bbox` from the W1 features snapshot of 2026-10-18 05:24). I used the census contract: `convert('L')`, crop, PNG at `compress_level=3`. **All 266 match the census `crop_sha256` byte for byte.** They are in `cells_opus/crops/`. The 888 crops come from `ocr-review-sites-20261018/population-images/` and the 150 crops from `segeval1/crops/`.

## Types observed (assigned by eye; no rules)

| type | what it looks like |
|---|---|
| word_or_phrase | One or more complete printed words in lower or mixed case. Includes line tails and hyphenated word parts ("ζουμε:", "zations", "ανέρ-"), which are complete printed short lines. |
| heading_caps_display | Capitals or display type: headings, names, signatures in capitals, table headers ("ΧΡΗΣΗ 1989", "ΑΡΘΡΟ 1ον"). Often letter-spaced ("Α Θ Η Ν Α", "P A E O N I A", "S o m m a i r e"), large, inverse or outlined. |
| abbreviation_reference_label | Abbreviations and references with or without a number: "ver. 51.", "Luc. 11.", "xviii. 12,", "Αριθ. 2939", "Δρχ.", "Члан 35.", "5. Cholera", "(Α+Γ)". |
| roman_numeral_lowercase | Lower-case Roman numerals that the numeric rule (upper-case only) does not cover: "xviii", "Xili" (= xiii). |
| punctuation_only | Printed marks and no letters: leader dots, ditto marks », rules or dashes, quote marks, "%", "========". Two were misread as other scripts ("وو" for closing quotes, "《 《" for ditto marks). |
| noise_non_text | Blobs, specks, scattered dots or near-blank faint crops, often read as another script (Arabic, Hebrew) or as a stray letter. |
| handwriting | Signatures, scribbles and handwritten notes. |
| foreign_script_printed | Printed CJK. All 3 come from one ia_poly1850 item (`26e14cb9c90b750f`). |
| map_figure_ornament_logo | Map labels (rotated or over map graphics), ornament patterns and an advertisement logo. |
| scan_watermark | Google digitisation marks ("Digitized", "Google"). |
| show_through_mirrored | Mirrored text from the other side of the page. |
| cut_fragment | The crop clips letters at its edge, so the text is a piece of a word or line. |
| multi_line_crop | Two or more printed lines in the crop; the Google text is one of them. |
| text_covers_part_of_crop | The crop holds a whole printed line (or more), but the Google text is only 1–2 words, usually the tail of the next line or the last word of the line. |

## Counts

| type | uniform sample n (of 120) | % | owner supplement n (of 59) | 0.5 KEEP / DROP / UNCERTAIN (all 179) | owner good / bad (rated rows) | median w×h px | median ratio | median ratio/char |
|---|---:|---:|---:|---|---|---|---:|---:|
| word_or_phrase | 43 | 35.8% | 2 | 43 / 2 / 0 | 1 / 1 | 117×35 | 3.52 | 0.50 |
| heading_caps_display | 24 | 20.0% | 19 | 27 / 11 / 5 | 20 / 0 | 151×27 | 5.00 | 0.71 |
| abbreviation_reference_label | 14 | 11.7% | 1 | 14 / 1 / 0 | 1 / 0 | 154×35 | 4.17 | 0.54 |
| punctuation_only | 13 | 10.8% | 3 | 5 / 10 / 1 | 3 / 0 | 56×16 | 4.09 | 1.22 |
| roman_numeral_lowercase | 2 | 1.7% | 0 | 2 / 0 / 0 | 0 / 0 | 116×47 | 2.47 | 0.56 |
| noise_non_text | 8 | 6.7% | 2 | 2 / 7 / 1 | 1 / 1 | 34×16 | 1.41 | 0.95 |
| handwriting | 3 | 2.5% | 2 | 1 / 3 / 1 | 1 / 1 | 80×61 | 1.93 | 0.38 |
| foreign_script_printed | 3 | 2.5% | 0 | 0 / 2 / 1 | 0 / 0 | 241×75 | 3.21 | 1.47 |
| map_figure_ornament_logo | 2 | 1.7% | 2 | 0 / 4 / 0 | 0 / 2 | 268×238 | 1.19 | 0.20 |
| scan_watermark | 0 | 0.0% | 2 | 2 / 0 / 0 | 2 / 0 | 442×146 | 3.29 | 0.45 |
| show_through_mirrored | 1 | 0.8% | 0 | 0 / 1 / 0 | 0 / 0 | 182×25 | 7.28 | 0.91 |
| cut_fragment | 4 | 3.3% | 0 | 2 / 0 / 2 | 0 / 0 | 56×30 | 2.22 | 0.61 |
| multi_line_crop | 1 | 0.8% | 0 | 1 / 0 / 0 | 0 / 0 | 243×85 | 2.86 | 0.32 |
| text_covers_part_of_crop | 2 | 1.7% | 26 | 0 / 28 / 0 | 1 / 25 | 714×52 | 13.23 | 2.65 |
| **total** | 120 | 100% | 59 | 99 / 69 / 11 | 30 / 30 | | | |

"Owner good / bad" counts the rated rows only: in the 150, the owner standard state fine or faulty; in the 888, the owner rating KEEP or DROP. Ratio = width/height; ratio/char = ratio ÷ chars.

### Legitimate lines vs segmentation faults (from what the crops show)

- **They look like legitimate printed lines:** word_or_phrase 43, heading_caps_display 24, abbreviation_reference_label 14 and roman_numeral_lowercase 2. That is **83 of 120 (69.2%)** of the uniform sample. In the owner-rated rows these types are owner-good 22 times and owner-bad once: "Kede", a blackletter "Rede" with a wrong Google label. Of the 105 crops of these types across all 179, 0.5 dropped 14 and left 5 UNCERTAIN, and 10 of the 14 drops were owner-good headings.
- **Printed marks, segmentation fine:** punctuation_only, **13 of 120 (10.8%)**. The crops are clean, but the text is only leaders, dittos or rules. All 3 owner-rated ones are owner-good (2 leader rows and "-"), and 0.5 dropped 10 of the 16 seen. Whether they are training lines is the owner's call; the crops themselves are not segmentation faults.
- **They look like segmentation faults or non-text:** noise_non_text 8, cut_fragment 4, handwriting 3, foreign_script_printed 3, map_figure_ornament_logo 2, text_covers_part_of_crop 2, show_through_mirrored 1 and multi_line_crop 1. That is **24 of 120 (20.0%)**. Scan watermarks (0 in the uniform sample, 2 in the supplement) are printed by the scanner, not the book, and the owner rated both KEEP.
- In the owner supplement, **text_covers_part_of_crop dominates: 26 of 59, owner-bad 25 of 26.** These are full-width line crops (median 714×52 px; ratio/char 2.65, against 0.50 for word_or_phrase) whose Google text is a word or two. They sit at the 96th to 100th percentile of the census ratio for their chars group (see `size_vs_output.md`, A3b), and the 0.5 "too little OCR for box" verdict dropped all 28. The one owner-good case (`ia_poly1850--63f57af8d450f3e8--s009-l0033`, "τους υπερ", 1538×78) is a clean full line with a truncated Google label.

### Examples (3 per type; uniform sample first, then supplement)


**word_or_phrase**

| line_id | population | crop_path | Google text | w×h | chars | 0.5 | owner | note |
|---|---|---|---|---|---:|---|---|---|
| lekythos--1a3def6495932802--s001-l0268 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/lekythos--1a3def6495932802--s001-l0268.png` | `Δύο εἶπα.` | 103×22 | 8 | KEEP |  |  |
| elstat--df38bce62200e7db--s000-l0029 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/elstat--df38bce62200e7db--s000-l0029.png` | `Καλλιερ` | 74×21 | 7 | KEEP |  |  |
| ia_greek_latin--a8c58d8eb21f93c8--s007-l0030 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/ia_greek_latin--a8c58d8eb21f93c8--s007-l0030.png` | `πλέξαιμι` | 214×55 | 8 | KEEP |  |  |

**heading_caps_display**

| line_id | population | crop_path | Google text | w×h | chars | 0.5 | owner | note |
|---|---|---|---|---|---:|---|---|---|
| kosmopolis--ecc23d7812913d0a--s006-l0009 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/kosmopolis--ecc23d7812913d0a--s006-l0009.png` | `ΣΤΟ ΒΑΛΑΙ` | 123×23 | 8 | KEEP |  | last letter at right edge |
| gazette_modern--affc069208f11f21--s000-l0038 | 888 | `/Users/foivoskarounos-zamparloukos/Projects/ocr-review-sites-20261018/population-images/af48b15be1159f1f55bafd93a527ec067fc01d94acdc4c3f9584782f9ab29008.png` | `ΥΛΙΚΑ` | 37×13 | 5 | KEEP |  | ink of line above at top |
| gazette_modern--a87013273db4352c--s000-l0066 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/gazette_modern--a87013273db4352c--s000-l0066.png` | `ΠΑΡΑΡΤΗΜΑ` | 179×27 | 9 | KEEP |  |  |

**abbreviation_reference_label**

| line_id | population | crop_path | Google text | w×h | chars | 0.5 | owner | note |
|---|---|---|---|---|---:|---|---|---|
| ia_poly1850--36dcee7ce4c29f8b--s003-l0004 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/ia_poly1850--36dcee7ce4c29f8b--s003-l0004.png` | `ver. 51.` | 154×41 | 7 | KEEP |  |  |
| ia_greek_latin--7156a8b65e724719--s004-l0082 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/ia_greek_latin--7156a8b65e724719--s004-l0082.png` | `xviii. 12,` | 93×27 | 9 | KEEP |  |  |
| bsb_poly1850--b05b8313ad5d52e2--s007-l0015 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/bsb_poly1850--b05b8313ad5d52e2--s007-l0015.png` | `data 1660.` | 204×36 | 9 | KEEP |  |  |

**punctuation_only**

| line_id | population | crop_path | Google text | w×h | chars | 0.5 | owner | note |
|---|---|---|---|---|---:|---|---|---|
| gazette_modern--79750acfeada2565--s000-l0058 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/gazette_modern--79750acfeada2565--s000-l0058.png` | `========` | 94×12 | 8 | DROP |  |  |
| gazette_modern--98dfb00fa203c6d5--s000-l0048 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/gazette_modern--98dfb00fa203c6d5--s000-l0048.png` | `《 《` | 58×21 | 2 | DROP |  | ditto marks |
| ia_poly1850--c3f3a531e277da9a--s001-l0038 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/ia_poly1850--c3f3a531e277da9a--s001-l0038.png` | `......` | 88×13 | 6 | DROP |  |  |

**roman_numeral_lowercase**

| line_id | population | crop_path | Google text | w×h | chars | 0.5 | owner | note |
|---|---|---|---|---|---:|---|---|---|
| ia_greek_latin--e3dff0a8a9829e59--s003-l0001 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/ia_greek_latin--e3dff0a8a9829e59--s003-l0001.png` | `xviii` | 140×58 | 5 | KEEP |  |  |
| ia_poly1850--4ab77886725d9e1e--s002-l0002 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/ia_poly1850--4ab77886725d9e1e--s002-l0002.png` | `Xili` | 91×36 | 4 | KEEP |  |  |

**noise_non_text**

| line_id | population | crop_path | Google text | w×h | chars | 0.5 | owner | note |
|---|---|---|---|---|---:|---|---|---|
| gazette_modern--b21451311e269f58--s000-l0001 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/gazette_modern--b21451311e269f58--s000-l0001.png` | `سے` | 24×14 | 2 | UNCERTAIN |  | blob read as Arabic |
| gazette_modern--49b793056935d163--s000-l0043 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/gazette_modern--49b793056935d163--s000-l0043.png` | `דוד דר` | 52×10 | 5 | DROP |  | blobs read as Hebrew |
| gazette_modern--fd0c55b5cf1557ca--s000-l0042 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/gazette_modern--fd0c55b5cf1557ca--s000-l0042.png` | `لارن` | 37×29 | 4 | DROP |  | squiggle read as Arabic |

**handwriting**

| line_id | population | crop_path | Google text | w×h | chars | 0.5 | owner | note |
|---|---|---|---|---|---:|---|---|---|
| gazette_modern--d2281f8022512d7b--s000-l0232 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/gazette_modern--d2281f8022512d7b--s000-l0232.png` | `m` | 28×20 | 1 | UNCERTAIN |  |  |
| gazette_modern--d2281f8022512d7b--s000-l0329 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/gazette_modern--d2281f8022512d7b--s000-l0329.png` | `Ξετώμαδα` | 150×61 | 8 | DROP |  | signature |
| gazette_modern--79750acfeada2565--s000-l0220 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/gazette_modern--79750acfeada2565--s000-l0220.png` | `AM` | 54×28 | 2 | KEEP |  | scribble |

**foreign_script_printed**

| line_id | population | crop_path | Google text | w×h | chars | 0.5 | owner | note |
|---|---|---|---|---|---:|---|---|---|
| ia_poly1850--26e14cb9c90b750f--s003-l0047 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/ia_poly1850--26e14cb9c90b750f--s003-l0047.png` | `頂 硬` | 241×75 | 2 | DROP |  |  |
| ia_poly1850--26e14cb9c90b750f--s003-l0102 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/ia_poly1850--26e14cb9c90b750f--s003-l0102.png` | `滑` | 106×72 | 1 | UNCERTAIN |  |  |
| ia_poly1850--26e14cb9c90b750f--s005-l0016 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/ia_poly1850--26e14cb9c90b750f--s005-l0016.png` | `推而凹兒—五法凹` | 660×81 | 8 | DROP |  |  |

**map_figure_ornament_logo**

| line_id | population | crop_path | Google text | w×h | chars | 0.5 | owner | note |
|---|---|---|---|---|---:|---|---|---|
| gazette_modern--f4a16fe9302ade1e--s000-l0081 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/gazette_modern--f4a16fe9302ade1e--s000-l0081.png` | `ΛΕΣΒΟΥ` | 57×48 | 6 | DROP |  | rotated map label |
| bsb_poly1850--2032df1e3e983f1d--s005-l0136 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/bsb_poly1850--2032df1e3e983f1d--s005-l0136.png` | `SPARTA` | 96×40 | 6 | DROP |  | map label over map graphics |
| ia_greek_latin--a232aaf9a41fe898--s001-l0012 | 888 | `/Users/foivoskarounos-zamparloukos/Projects/ocr-review-sites-20261018/population-images/1f02febc2307feb8d421297d440deb9973e93f6c871889bce5f380847f463876.png` | `*****` | 439×427 | 5 | DROP | DROP | ornament pattern |

**scan_watermark**

| line_id | population | crop_path | Google text | w×h | chars | 0.5 | owner | note |
|---|---|---|---|---|---:|---|---|---|
| ia_greek_latin--a232aaf9a41fe898--s001-l0010 | 888 | `/Users/foivoskarounos-zamparloukos/Projects/ocr-review-sites-20261018/population-images/084f0f3bfb7246e6fec31b5c72ab6fbe545463685567c28a639c269f26025bb8.png` | `Digitized` | 150×41 | 9 | KEEP | KEEP |  |
| ia_poly1850--3773a91327e98bc0--s004-l0001 | 888 | `/Users/foivoskarounos-zamparloukos/Projects/ocr-review-sites-20261018/population-images/6cd89ad1b4e299fedd9d36d114dac2271d4ca937066b170a1e5893a2a347bcc2.png` | `Google` | 735×251 | 6 | KEEP | KEEP |  |

**show_through_mirrored**

| line_id | population | crop_path | Google text | w×h | chars | 0.5 | owner | note |
|---|---|---|---|---|---:|---|---|---|
| lekythos--dcfa99599048d352--s000-l0001 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/lekythos--dcfa99599048d352--s000-l0001.png` | `HVED !!-8` | 182×25 | 8 | DROP |  | mirrored verso text |

**cut_fragment**

| line_id | population | crop_path | Google text | w×h | chars | 0.5 | owner | note |
|---|---|---|---|---|---:|---|---|---|
| bsb_poly1850--d7db5a3b1eb289a3--s006-l0029 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/bsb_poly1850--d7db5a3b1eb289a3--s006-l0029.png` | `νὴ τοὺς δ.` | 156×43 | 8 | KEEP |  | first letter clipped at left edge |
| gazette_modern--69e6dd699507ba6a--s000-l0050 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/gazette_modern--69e6dd699507ba6a--s000-l0050.png` | `ΑΡΟ` | 44×19 | 3 | UNCERTAIN |  | clipped illegible glyphs |
| bsb_poly1850--2032df1e3e983f1d--s005-l0179 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/bsb_poly1850--2032df1e3e983f1d--s005-l0179.png` | `Chall` | 55×26 | 5 | KEEP |  | clipped at both edges |

**multi_line_crop**

| line_id | population | crop_path | Google text | w×h | chars | 0.5 | owner | note |
|---|---|---|---|---|---:|---|---|---|
| ia_poly1850--36dcee7ce4c29f8b--s003-l0032 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/ia_poly1850--36dcee7ce4c29f8b--s003-l0032.png` | `1 Joan. 16.` | 243×85 | 9 | KEEP |  | three lines in crop; text = middle line |

**text_covers_part_of_crop**

| line_id | population | crop_path | Google text | w×h | chars | 0.5 | owner | note |
|---|---|---|---|---|---:|---|---|---|
| lekythos--456def1ccfc2283e--s002-l0164 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/lekythos--456def1ccfc2283e--s002-l0164.png` | `, τὸ πρό-` | 533×57 | 7 | DROP |  | crop holds a whole printed line; text is the tail of the next line |
| kosmopolis--acb323b6cb8d169d--s004-l0035 | W1 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/crops/kosmopolis--acb323b6cb8d169d--s004-l0035.png` | `Σιγά-` | 710×54 | 5 | DROP |  | crop holds a whole line; text = last word of the line below |
| gazette_modern--b7877bdaa2fcf7f5--s000-l0029 | 150 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/crops/gazette_modern--b7877bdaa2fcf7f5--s000-l0029.png` | `ΕΤΑΙ-` | 724×46 | 5 | DROP | faulty |  |

### Owner-good short non-numeric rows that 0.5 or 0.8 dropped, by type (150 + 888 rated rows in the 179)

| type | n |
|---|---:|
| heading_caps_display | 10 |
| punctuation_only | 3 |
| handwriting | 1 |
| noise_non_text | 1 |
| abbreviation_reference_label | 1 |
| word_or_phrase | 1 |
| text_covers_part_of_crop | 1 |

Of the owner-good short non-numeric drops, 10 of 18 are headings in capitals or display type, mostly letter-spaced or large: ΑΘΗΝΑ, ΠΑΓΙΟ, PAEONIA, MEER, Sommaire, SCHOOL, Ο ΠΥΡΓΟΣ, Ν. Φ., INCAII. (ПИСАЦ.) and ВИЉЕМ БУE. Their ratio sits at the 74th to 99th percentile of the census for their chars group (A3b). Three are leader or dash rows. The remaining five are one each: the handwriting is the signature "Скрирания", the noise is a lone '"', the abbreviation is "*Vid. Luc.", the word_or_phrase is "ἐᾶν, 95", and the text_covers_part_of_crop is "τους υπερ".

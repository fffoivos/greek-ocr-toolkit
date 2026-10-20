# Small segments: what counts as small, where they come from, what they are

Small-segment analysis session (Opus lead; all computation by Sol briefs SS1–SS6, each with tests and a receipt), 19 Oct 2026.
Read-only analysis of the frozen census (592,466 rows, `cells/population_cells.jsonl.gz`). No tool, rule or verdict was changed.

## Numbers first

| question | answer |
|---|---|
| Q1 recommended definition | **small = Google chars ≤ 8 AND A ≤ 6**, A = crop long side / short side. Computable from the crop size and the Google output alone. It is rotation-invariant, so it is the same before and after the step-2 turn. |
| rows inside | 59,002 (10.0% of the census): numeric 38,221, nonnumeric 19,481, mixed 1,300 |
| 0.5 box failures (too little + too much + no supported row) | 18.0% inside vs 2.0% outside |
| owner-judged lines (362 unique) | inside 152 good / 19 bad; outside 126 good / 67 bad |
| owner-good lines that 0.5 did not KEEP | 51 of 99 are inside (0.8: 14 of 53) |
| Q2 sources | gazette_modern 51.1%, elstat 23.7%, ia_poly1850 11.9%, bsb_poly1850 5.2%, the rest ≤ 2.3% each. All W1/W2; no v2 row has fewer than 10 chars. |
| Q2 books | 1,370 of 1,917 books have ≥1 small row. 50/80/95% of small rows sit in 107/420/908 books, vs 249/815/1,480 for all lines. |
| Q2 pages | 37% on numeric-majority pages, 40% on small-majority pages, 15% on pages where small rows are < 10% of lines |
| Q3 non-numeric typology (est., 150-row source-weighted sample) | legitimate text 65% (words 39%, abbreviations/labels 13%, capitals/display 11%, markers 6%); punctuation-only 15%; non-text 8% (handwriting, stamps/ornaments, specks); CJK 1%; segmentation faults 10% |
| Q3 label quality | Google text right or minor-only on 90% of the legitimate lines and 88% of the punctuation lines; 15% on non-text; 32% on faults |

Sources: `q1/Q1_TABLES.md` + `q1/q1.json` (SS1), `q2/Q2_TABLES.md` + `q2/q2.json` (SS2), `q3/` (SS3–SS5).

## Q1 — what dimensions constitute "small"

### Measurements
- `chars` = the census's saved visible-character count of the Google text.
- `L`, `S` = the crop's long and short side in px (after the step-2 turn, L is the reading length). `A = L/S`.
- x-height = the detector's saved estimate (`xheight_px`). It is used only as a diagnostic: on these crops it is exactly the quantity the detector cannot measure.

### Where the font-line path breaks
Census distributions (SS1 T1):

| cohort | chars p50 | S p50 / p99 px | A p10 / p50 / p90 |
|---|---:|---|---|
| numeric | 6 | 21 / 57 | 1.4 / 3.3 / 5.8 |
| nonnumeric | 44 | 43 / 112 | 7.1 / 18.1 / 25.3 |
| chars ≤ 10 | 6 | 22 / 82 | 1.4 / 3.3 / 5.5 |
| chars > 10 | 45 | 44 / 112 | 8.9 / 18.4 / 25.5 |

The 0.5 box-failure rate on non-rotated rows, by chars (SS1 T2):

| chars | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 12 | 14 | 16 | 20 | 31–40 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nonnumeric+mixed | 48% | 49% | 34% | 23% | 22% | 16% | 13% | 12% | 10% | 11% | 5% | 3.5% | 2.7% | 2.2% | 0.5% |
| numeric | 38% | 17% | 18% | 13% | 7% | 10% | 11% | 10% | 10% | 7% | 7% | 4% | 1.5% | 3% | 0.7% |

Much of that failure is a mismatch between chars and crop width, which is the length model's job. To separate the two, look along the diagonal where the crop's A fits its char count (SS1 T3: box-failure % / n):

| chars | A where the crop fits | box failure |
|---|---|---|
| 1 | 1–1.5 | 41% / 3,718 and 31% / 2,202 |
| 2 | 1.5–2 | 14% / 4,808 |
| 3 | 2–2.5 | 8% / 4,535 |
| 4 | 2.5–3 | 7% / 1,842 |
| 5 | 3–4 | 5% / 3,125 |
| 6–7 | 3–5 | 7–8% / 13,272 |
| 8–9 | 4–6 | 5% / 10,110 |
| 10–12 | 5–8 | 3% / 12,095 |
| 13–15 | 5–10 | 2% / 15,268 |

So, on well-sized crops:
- The detector **fails badly on 1–2 glyphs**.
- It **fails at 2–4× the text-line level from 3 to 9 chars**.
- It **reaches the text-line level (~2%) from about 13 chars**.
- "No supported row" (UNCERTAIN) is the single-glyph failure:
  - nonnumeric: 11% at 1 char, 30% at 2, 3–8% at 3–8;
  - numeric: 15% at 1–3, and 6–9% up to 11 chars (digits have no x-height).
- Rotated rows (h > w, 24,648) are never KEEP in 0.5 (reading direction unresolved). The step-2 turn handles them.

### Candidate definitions (SS1 T4, SS2 G0; owner = 362 unique owner-judged lines)

| candidate | rows inside | box fail in / out | owner in good/bad | owner out good/bad | owner-good 0.5 false rejects inside (of 99) |
|---|---:|---|---|---|---:|
| **chars ≤ 8 & A ≤ 6 (recommended)** | **59,002** | **18.0% / 2.0%** | **152 / 19** | **126 / 67** | **51** |
| chars ≤ 8 alone | 60,605 | 19.4% / 1.8% | 164 / 45 | 114 / 41 | 62 |
| chars ≤ 5 & A ≤ 4 | 35,744 | 21.0% / 2.5% | 112 / 12 | 166 / 74 | 41 |
| chars ≤ 8 & A ≤ 5 | 56,714 | 17.4% / 2.2% | 150 / 19 | 128 / 67 | 49 |
| chars ≤ 10 & A ≤ 6 | 75,522 | 15.6% / 1.9% | 173 / 22 | 105 / 64 | 53 |
| chars ≤ 12 & A ≤ 8 | 90,476 | 14.4% / 1.7% | 182 / 26 | 96 / 60 | 57 |
| A ≤ 4 alone | 54,584 | 18.1% / 2.2% | 142 / 27 | 136 / 59 | 47 |
| L ≤ 100 px | 60,426 | 18.0% / 2.0% | 143 / 11 | 135 / 75 | 40 |
| L ≤ 5 x-heights | 40,173 | 24.6% / 2.1% | 114 / 11 | 164 / 75 | 37 |
| SEG-CELLS cut (S ≤ 40, L ≤ 200, chars ≤ 10) | 70,708 | 16.0% / 1.9% | 163 / 11 | 115 / 75 | 49 |

### Recommendation and why
**Small = chars ≤ 8 and A ≤ 6.**
- **Chars ≤ 8:** the detector's failure on well-sized crops stays at 2–4× the text-line level up to 9 chars, then falls to ~3% at 10–12. Raising the cut to 10 adds 16,520 rows for +2 owner false rejects; raising it to 12 adds 31,474 rows for +6.
- **A ≤ 6:** the cap removes only 1,603 of the 60,605 rows with ≤ 8 chars. Those rows are wide crops whose Google text covers only part of the printed line ('στὴν' 652×55, 'μὲ τὰ' 535×47, 'κόστους' 1385×35). They are true faults, the normal length check already drops them, and the cap removes 26 of the 45 owner-bad lines that chars alone would put inside.
- **Why not the others:**
  - Absolute pixel cuts give the cleanest owner split (L ≤ 100: 143/11), but they depend on scan resolution.
  - x-height cuts rely on the measurement that fails on these crops.
  - A alone pulls in tall many-character crops and leaves wide few-character ones outside: of the ≤10-char rows it leaves outside, 15% fail at A ≤ 4 and 82% at A ≤ 8.

### Notes for the filter steps
1. **Step 2 vs single glyphs.**
   - 2,540 crops with 1–2 chars are taller than wide (1,710 with 1 char, 830 with 2), but only 248 have h > 2w (e.g. "1" at 22×24 or 14×15).
   - A plain h > w turn rotates them. The owner marked 7 such single-digit "1" cells good, and 0.5 dropped them all.
   - Because the definition is rotation-invariant, step 2 can test it before turning.
   - With 3–8 chars, most taller-than-wide crops are genuinely upright (h > 2w for 90–99%).
2. **Letter-spaced and wide-set text is a step-5 population, not step 4.** 14 owner-good lines with ≤ 10 chars that 0.5 did not keep stay outside the definition at A 6.7–19.7. Their glyphs are all there; the length model fails on the spacing:
   - letter-spaced capitals: PAEONIA 338×37, Sommaire, ВИЉЕМ БУE, Ο ΠΥΡΓΟΣ;
   - leader dots: '.....' A 13–17;
   - wide-set digits: '3.237.787' 190×20.
3. **Big few-character blobs inside.** Four owner-bad lines are huge crops with few chars ('*****' 439×427, 'Longine' 1302×1093, 'MELA OF 10' 700×562, 'ποσό' 470×2217). Text lines have S p99 = 112 px. With the box taken from all ink, these give "too much" output, which agrees with the owner's DROP.
4. **Owner-bad lines inside are not a problem of the definition.** The small path still has to drop them by its own box and length test:
   - tiny specks read as '"' and '-';
   - vertical cells;
   - a 'Δήμ' cut fragment;
   - '6 10 6', a 3-line cell.

## Q2 — where small segments come from (definition above; SS2)

| source | rows | small | % of all small | density | numeric / mixed / nonnumeric |
|---|---:|---:|---:|---:|---|
| gazette_modern | 148,547 | 30,144 | 51.1% | 20.3% | 19,049 / 507 / 10,588 |
| elstat | 19,879 | 13,982 | 23.7% | 70.3% | 12,174 / 61 / 1,747 |
| ia_poly1850 | 64,476 | 6,994 | 11.9% | 10.8% | 3,172 / 422 / 3,400 |
| bsb_poly1850 | 33,090 | 3,059 | 5.2% | 9.2% | 1,602 / 195 / 1,262 |
| ia_greek_latin | 11,755 | 1,363 | 2.3% | 11.6% | 629 / 46 / 688 |
| nlg | 12,109 | 1,119 | 1.9% | 9.2% | 571 / 10 / 538 |
| serbia | 8,897 | 1,049 | 1.8% | 11.8% | 519 / 51 / 479 |
| lekythos | 13,407 | 566 | 1.0% | 4.2% | 152 / 4 / 410 |
| ia_russian | 2,963 | 427 | 0.7% | 14.4% | 215 / 3 / 209 |
| kosmopolis | 5,356 | 299 | 0.5% | 5.6% | 138 / 1 / 160 |
| all v2 sources | 271,987 | 0 | 0 | 0 | — |

- **Wave:** W2 43,264 (73.3%; 19.7% of W2 lines), W1 15,738 (26.7%; 15.6%).
- **Class:**
  - numerics_tables: 37,291 (63.2%; 66% of the class);
  - latin 6,067; modern_scanned 5,503;
  - nonletter 4,448 (86% of the class);
  - headings_caps 2,659; greek_mono 1,518;
  - Cyrillic, polytonic and dialogue: < 600 each.
- **Concentration:**

  | small rows held by | 50% | 80% | 95% |
  |---|---:|---:|---:|
  | all small rows | 107 books | 420 | 908 |
  | all lines (baseline) | 249 | 815 | 1,480 |
  | nonnumeric small only | 137 | 497 | 928 |

  The top book holds 3.1% of small rows, the top 20 hold 24.7% and the top 100 hold 48.8%. 15 of the top 20 by count are elstat statistical yearbooks, at 67–86% small density where the table shows it. The top nonnumeric book is ia_poly1850--36dcee7ce4c29f8b (5.1% of nonnumeric small; the 'ver. 51.' / 'Luc. 11.' scripture references).
- **Density over books with ≥ 50 lines:** 530 have none; 612 have ≤ 10%; 544 have 10–50%; 107 have > 50%. All 40 densest are elstat or gazette_modern issues.
- **Pages:**
  - 37.3% of small rows are on pages where ≥ 50% of lines are numeric (189 pages), and 39.8% on pages where ≥ 50% of lines are small (245 pages);
  - 15.1% are on pages where small rows are < 10% of lines;
  - 652 are the only small row on their page; 593 of these are numeric, page-number-like.
- **Plain answer:** small segments are **mostly two sources** (gazette_modern + elstat = 75%) and **mostly table material** (63% numerics_tables). Within those sources they are **spread over many books**, about 2× more concentrated than lines in general but not a handful. The nonnumeric ones are more spread still: ia_poly1850, bsb_poly1850 and the gazette's headings.

## Q3 — what the non-numeric small ones are

### How it was done
- **Sample:** SS3 drew 437 crops of non-numeric and mixed small rows. 256 were rebuilt byte-exact from the page cache and 181 copied; all 437 sha256-verified.

  | stratum | crops |
  |---|---:|
  | the Opus 179 (120 uniform + 59 owner supplement) | 179 |
  | 150 new inside the definition, proportional by source with a floor of 4 | 150 |
  | 30 mixed digit+letter | 30 |
  | 25 rotated | 25 |
  | 45 just outside the border (9–12 chars, or A 6–12) | 45 |
  | 8 owner-judged | 8 |

  The table sums to 437 because it includes the 20 controls. The bed is 417 crops; 159 of the Opus 179 stayed in the bed.
- **Typing:** a blind Sol one-reader pass per the sol-reading HANDOVER (gpt-6.1-sol medium, scanner v4.5.5, ≤ 100 items per context). There were 5 contexts of 83–84 bed crops plus 8 controls each, drawn from 20 controls I pixel-verified.
  - Four runs were VOID and are kept as evidence: pwd-built view paths, a replay layout the scanner cannot seed, a helper file left in the folder, and a `-rotate` zoom.
  - Each void run led to one added environment sentence in the prompt; the protocol body was not changed.
  - Every counted run has a clean scan. Total 5.55 M tokens; the Codex weekly meter went from 30% to 31%.
- **Controls:** errors per context under the amended expectations were t01 1, t02 2, t03 1, t04 0, t05 4.
  - I made three amendments, each a case where my expected value contradicted the prompt's own definition of `minor`. They are recorded in `q3/LEAD_CONTROLS.json` with their reasons.
  - t02 and t05 stay flagged. Almost all of their errors are on the three speck controls, which Sol never types `noise`; t05 also misread '51' as '61'.
- **My eye pass:** I checked 209 crops by eye. The checks covered every non-text, fault, punctuation, marker, number and unreadable call, every Sol-vs-Opus disagreement, and a random 10% of the rest. I corrected 19:
  - 7 were specks or blobs Sol had called punctuation, marker or cut_fragment;
  - 5 were complete short words Sol had called clipped;
  - 4 were map labels or stamps;
  - 3 were other.

  The random 10% (24 crops) needed no correction (`q3/LEAD_EYE.json`).
- **Sol vs Opus** on the 159 Opus-typed bed crops: 72% exact agreement. Most disagreements are Opus `part_of_line` vs Sol `multi_line` (22); both are segmentation faults.

### What they are: estimate for the non-numeric small population
The estimate comes from the 150-row proportional sample inside the definition, source-weighted (`q3/Q3_TABLES.md` T8). The pool is 19,377 rows; Wilson 95% intervals are on the unweighted shares.

| class | type | share | ≈ rows |
|---|---|---:|---:|
| **legitimate text** | | **65%** (57–72) | ≈ 12,600 |
| | words or phrases ('ἔπαιξαν:', 'it, but is', 'tions', 'λος.') | 39% | |
| | abbreviations, references, labels ('ver. 51.', 'Αριθ. 2939', 'Μάρτ.', 'A.B.E.E.', '(Α+Γ)') | 13% | |
| | capitals and display text ('ΓΕΩΡΓΙΑΣ', 'ПОСЛАНИЦА', 'TAMEIO', map labels) | 11% | |
| | single-letter markers ('Β΄', 'A', 'η)') | 6% | |
| **printed non-letters** | punctuation only: ditto marks », leader dots, dashes, '==', quotes | **15%** (11–23) | ≈ 3,000 |
| **non-text** | handwriting 3%, figure / ornament / stamp 3%, specks 2% | **8%** (4–13) | ≈ 1,500 |
| **foreign script** | printed CJK, one ia_poly1850 item | **1%** | ≈ 270 |
| **segmentation faults** | cut fragments 5%, multi-line or part-of-line crops 1% | **10%** (6–16) | ≈ 2,000 |

Label quality (Google text right or minor-only, my eye corrections applied):
- legitimate text: 90%;
- punctuation: 88%;
- non-text: 15%;
- faults: 32%.

By source (T9):
- ia_poly1850 has the most faults: 24% segmentation faults and 8% CJK.
- gazette_modern: 68% legitimate, 17% punctuation, 8% non-text (handwriting and stamps), 8% faults.
- elstat: 85% legitimate.

Other strata:
- **Border, just outside the definition (45):** 62% legitimate, 16% punctuation, 9% non-text, 13% faults. The composition hardly changes at the border.
- **Rotated (25):** 40% legitimate, 24% punctuation (ruled dashes), 28% faults.
- **Opus 179 (W1, chars ≤ 9; 72 of them outside the definition):** 25% faults. The wide part-of-line crops the A ≤ 6 cap removes are concentrated here.

### Mixed digits + letters (30)
- 20 are legitimate:
  - 10 abbreviations or references with numbers (scripture and section references in bsb_poly1850 and ia_poly1850);
  - 5 digits with letters or units;
  - 5 numbers that Google misread with a letter ('220p', '12.8.so', '-=4,00').
- 4 are non-text: 3 handwriting, 1 show-through.
- 6 are segmentation faults.

### What the Google text looks like (T10)
- **Legitimate text:** 45% letters only, 16% digits+letters.
- **Punctuation:** 76% punctuation only. When Google gets it wrong, it reads ditto marks » as 《 and quote marks as Arabic (وو).
- **Non-text:** 63% letters only and 10% foreign script. Google invents letters for specks and scribbles ('A', 'E', 'Mimpis', 'Hack'), or Arabic, Hebrew and CJK characters.
- **Faults:** usually 1–2 words of a longer printed line.

No local word list was found in the toolkit (lexicon code exists, but no data), so a dictionary-word share was not computed.

### Which types are legitimate training lines
| verdict | types | condition |
|---|---|---|
| **Legitimate** | word, caps_display, abbrev_label, marker, roman_lower, digits_letters, number | crop ok and label right or minor; 90% of them meet this |
| **Owner's call** | punctuation only | real printed ink, and the label is right 88% of the time, but the line holds no letters |
| **Not training lines** | handwriting, figure / ornament / stamp, watermark, show-through, specks | Google text is invented for them |
| **Not training lines** | foreign script | out of scope |
| **Not training lines (faults)** | cut fragments, multi-line, part-of-line | |

The owner's existing marks agree with this split (T12):

| class | owner good | owner bad | mixed |
|---|---:|---:|---:|
| legitimate | 14 | 1 | 1 conflict |
| segmentation faults | 5 | 27 | |
| non-text | 3 | 8 | |

### Owner review sheet
`sheet/small_segments_sheet.html` (SS6; package `greekocr.adjudicate.owner_sheet`, branch coord/review-sheets):
- **Cards:** 417, grouped by type. Within a group, rows inside the definition come first, then border rows. Controls are excluded.
- **Marks:** KEEP = usable training line, DROP = not.
- **Inner frame:** the latest saved tool verdict (0.8 where present, otherwise 0.5).
- **Database:** ids are `smallseg:<line_id>`, and the page never writes on load.
- **Check:** HTML parse and image checks passed. The headless visual check could not run locally; the coordinator checked the rendered page before publishing.
- **Published** 19 Oct by the coordinator: https://claude.ai/artifact/LZ69m33YqGxf3fJHdobMpD (db + user).

### Files
- `samples.jsonl`: all 437 crops, with sizes, source, book, verdicts, the Sol, lead and final types, and the class.
- `crops/`: the crop images.
- `q3/`: sample, keys, answers (VOID runs kept), agreement, eye sheets, LEAD_CONTROLS / LEAD_EYE, Q3 tables, receipts SS3–SS6.
- `briefs/`: SS1–SS6 and SS4b/c.
- `prompts/type.md`: the reader prompt.

## Addendum 19 Oct evening — content-gate failures and the owner's admission rule

**Why:** the coordinator found that the content gate recorded foreign-script and mixed-script lines without excluding them. The owner then set an admission rule (gate 0.3 part 2, segcensus caa32d5a0):
- a cell (A ≤ 6) needs more than one letter-or-digit (L* + Nd);
- a non-cell numeric line needs the same;
- any other line needs 10 letters, or 4 for headings_caps.

Every small row is a cell, so only `single_character_cell` can fire on the small set. Runs: SS8 (`gate_recheck/`) and SS9 (`r1_survivors/`).

**What is removed from the 59,002:**
- gate failures: 706;
- single-character cells: 10,702 more, of which 6,139 are numeric (single digits) and 4,563 text.
  - By alnum: 3,332 have none, 7,370 have one.
  - In the 417 bed: 57 removed, the same as the lead's count. They are 39 punctuation, 9 markers, 4 noise, 2 figures, 2 cut fragments and 1 handwriting.
- Survivors: **47,594** (numeric 32,082, mixed 1,212, nonnumeric 14,300).

**Owner marks:** the rule removes none of the owner's marked crops. Of the 185 marks:
- 143 are on survivors (136 KEEP / 7 DROP);
- the other 42 are border rows outside the small definition.

| | original | gate removed | gate + admission rule |
|---|---:|---:|---:|
| Q1 rows inside | 59,002 | 58,296 | 47,594 |
| box_fail inside / outside | 18.0% / 2.0% | 17.7% / 2.0% | **10.7% / 1.8%** |
| owner good / bad inside | 152 / 19 | 152 / 19 | 118 / 14 |
| owner good / bad outside | 126 / 67 | 124 / 65 | 112 / 37 |
| owner-good 0.5 false rejects inside | 51 | 51 | 33 |
| Q2 gazette / elstat / ia_poly1850 share | 51 / 24 / 12% | 51 / 24 / 11% | 49 / 27 / 11% |
| numerics_tables share | 63% | 64% | 69% |
| books for 50 / 80 / 95% | 107 / 420 / 908 | 108 / 420 / 911 | 90 / 382 / 855 |
| Q3 legit text (weighted) | 65% | 68% | **84%** (words 54%, abbrev 18%, caps 16%) |
| Q3 punctuation-only | 15% | 16% | 0% (all removed) |
| Q3 non-text / CJK | 8% / 1% | 6% / 0% | 5% / 0% |
| Q3 segmentation faults | 10% | 10% | 10% |

The Q3 survivor sample is 105 of the 150 rows. Its weights are the survivor counts per source, a slightly different frame from the original residual pool.

**What moves and what does not:**
- The recommended definition stands.
- The box-failure gap between small and other rows narrows (10.7% vs 1.8%), but small rows still fail about 6× as often.
- On survivors, the remaining non-length problem groups are segmentation faults (about 10%, ≈ 1,400 of the 14,300 nonnumeric) and non-text (about 5%).

**Keys:**
- `small_population_key.v2.jsonl.gz` adds `gate_failed` and `gate_reason`;
- `small_population_key.v3.jsonl.gz` adds `letters`, `alnum`, `reason`, `admit` and `survivor`;
- v1 is unchanged.

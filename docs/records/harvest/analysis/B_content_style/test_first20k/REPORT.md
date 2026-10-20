# Aspect B — content and style

Input: `docs/records/harvest/collection/admitted_all.jsonl` (first 20000 lines only — TEST RUN). Lines processed: **20,000**; books (source, book_key): **49**.

Page height for the running-title detector: {'png_header': 574} (`png_header` = height read from the page PNG header via the image path in the wave's records.jsonl; `max_y1_records` = fallback, not needed if absent).

Script: `docs/records/harvest/analysis/B_content_style/analysis_B.py` (re-runnable; `--limit N --out <subdir>` for tests).

## 0. Key findings (numbers from this run)

1. **Breathing/accent on a capital is encoded two ways.** 1,309 lines write a spacing mark (mostly U+1FBF ᾿) followed by a bare capital (`᾿Αθῆναι`) instead of the precomposed capital (`Ἀθῆναι`); per wave, spacing-form / all breathing-capitals: round1 1,375/4,765 (29%). 49 books use BOTH encodings, so this is a label-normalisation inconsistency (Google output), not a property of the print: the same glyph gets two different targets.
2. **Final-sigma errors are rare but systematic in 19th-c. type.** 66 lines (0.33%); occurrences: word-final σ 22, word-internal ς 47, of which 21 have the στ-spelling attested elsewhere in the pool — the στ ligature (ϛ-like glyph) read as ς (`μέγιςος`, `Πανεπιςημίου`, `καταςροφὴν`). A further 65 compound-boundary ς (`προςάγω`, `ὥςτε`, `ὁποιοςδήποτε`, aphaeresis `᾿ς`) follow the print's orthography and are not counted.
3. **Library stamp admitted as text.** 69 lines are digitisation/ownership marks, not book text: mostly the University of Crete seal on Anemi scans (`ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ`, partial `ΠΑΝΕΠΙΣΤΗΜΙ…`; curved lettering over a logo in a ~190×240 px box at ~92 % of the page height), a few rubber library stamps (`ΒΙΒΛΙΟΘΗΚΗ`) and `Digitized by Google` footers on Wikisource scans.
4. **No book exceeds the 30 % spec limits** for digit-heavy or running-title lines (max digit-heavy share 10.0% in anemi_round1 1697d5cc21fa26717b97e073; max running-title share 4.2% in anemi_round1 ffe26907d1e3e9c1f75337e2). Running titles and session headers are 0.70% of lines (140). The largest single book is anemi_round1 18ed614c7b7c25896c49680b 982 lines (4.9% of the pool); anemi_round1 a588c9878d5b1197798bb2c5 844 lines (4.2% of the pool); anemi_round1 1697d5cc21fa26717b97e073 806 lines (4.0% of the pool).

## 1. Feature distributions per wave × script class

Shares are per line over visible characters (whitespace and combining marks excluded). Columns: median / p90 / p99 (mean for shares in brackets).

| wave | class | n | digit_share | punct_share | symbol_share | upper_share | n_tokens | mean_word_len | longest_token | n_chars |
|---|---|---:|---|---|---|---|---|---|---|---|
| round1 | greek_latin_cs | 339 | 0.000 / 0.078 / 0.160 (0.015) | 0.064 / 0.143 / 0.231 (0.075) | 0.000 / 0.000 / 0.033 (0.002) | 0.04 / 0.09 / 0.18 (0.045) | 9 / 13 / 18 | 5.00 / 6.61 / 8.87 | 10 / 13 / 18 | 58 / 72 / 103 |
| round1 | greek_mono | 673 | 0.000 / 0.068 / 0.160 (0.014) | 0.077 / 0.167 / 0.239 (0.076) | 0.000 / 0.000 / 0.037 (0.001) | 0.15 / 1.00 / 1.00 (0.480) | 2 / 5 / 12 | 7.00 / 10.00 / 12.00 | 10 / 13 / 16 | 19 / 44 / 69 |
| round1 | greek_poly | 18,495 | 0.000 / 0.023 / 0.133 (0.008) | 0.037 / 0.098 / 0.203 (0.046) | 0.000 / 0.000 / 0.000 (0.000) | 0.02 / 0.07 / 0.17 (0.028) | 9 / 11 / 16 | 5.11 / 6.50 / 8.40 | 10 / 13 / 16 | 54 / 64 / 101 |
| round1 | latin | 493 | 0.000 / 0.083 / 0.172 (0.017) | 0.062 / 0.142 / 0.226 (0.072) | 0.000 / 0.000 / 0.000 (0.000) | 0.05 / 0.12 / 1.00 (0.067) | 7 / 10 / 13 | 4.89 / 7.00 / 11.00 | 9 / 13 / 17 | 40 / 61 / 73 |

Pattern rates per wave × class (share of lines):

| wave | class | n | is_all_caps | cap_initial | hyphen_end | numeric_table | biblio | rep_run | dictionary_like | top_bottom | sigma_err lines | compound-ς lines (not errors) | spacing-apos lines | of which mark before a capital |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| round1 | greek_latin_cs | 339 | 0.0000 | 0.3156 | 0.2566 | 0.0059 | 0.0088 | 0.0000 | 0.0000 | 0.0059 | 0.0000 | 0.0029 | 0.0413 | 0.0413 |
| round1 | greek_mono | 673 | 0.4324 | 0.7667 | 0.0193 | 0.0059 | 0.0000 | 0.0000 | 0.0119 | 0.2764 | 0.0015 | 0.0000 | 0.0550 | 0.0550 |
| round1 | greek_poly | 18,495 | 0.0000 | 0.2133 | 0.2316 | 0.0028 | 0.0018 | 0.0002 | 0.0017 | 0.0192 | 0.0035 | 0.0034 | 0.0694 | 0.0679 |
| round1 | latin | 493 | 0.0122 | 0.5781 | 0.1237 | 0.0041 | 0.0101 | 0.0000 | 0.0020 | 0.0527 | 0.0000 | 0.0020 | 0.0061 | 0.0061 |

Bibliographic pattern kinds (line counts): {'year_in_parens': 8, 'σ.+number': 33, 'vol.': 1, 'Bd.': 1}. Line-end hyphen kinds: {'-': 4442, 'U+2010': 3}.

## 2. Line-flag thresholds (per script class, whole pool as reference)

| class | n lines | digit_heavy > (p90 of digit-bearing lines) | punct_heavy > (p99 of punctuated) | symbol_heavy > (p99 of symbol-bearing) | long_token > p99 | word length outside [p1, p99] (lines >= 3 words) | short (running title) <= p50 chars |
|---|---:|---:|---:|---:|---:|---|---:|
| greek_latin_cs | 339 | 0.123 | 0.233 | 0.048 | 18 | [3.33, 8.55] | 58 |
| greek_mono | 673 | 0.155 | 0.255 | 0.122 | 16 | [3.50, 9.93] | 19 |
| greek_poly | 18,495 | 0.128 | 0.206 | 0.104 | 16 | [3.40, 8.00] | 54 |
| latin | 493 | 0.156 | 0.226 | 0.020 | 17 | [2.76, 8.67] | 40 |

## 3. Flag rates per wave × class (share of lines carrying the flag)

| wave | class | n | digit_heavy | punct_heavy | symbol_heavy | all_caps | long_token | word_length_outlier | repeated_run | numeric_table | bibliographic | running_title_or_page_number | final_sigma_error | spacing_apostrophe | line_end_not_sign | dictionary_like | digitisation_stamp |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| round1 | greek_latin_cs | 339 | 0.0206 | 0.0118 | 0.0029 | 0.0000 | 0.0118 | 0.0236 | 0.0000 | 0.0059 | 0.0088 | 0.0000 | 0.0000 | 0.0413 | 0.0000 | 0.0000 | 0.0000 |
| round1 | greek_mono | 673 | 0.0134 | 0.0074 | 0.0015 | 0.4324 | 0.0074 | 0.0074 | 0.0000 | 0.0059 | 0.0000 | 0.2080 | 0.0015 | 0.0550 | 0.0000 | 0.0119 | 0.1025 |
| round1 | greek_poly | 18,495 | 0.0122 | 0.0086 | 0.0001 | 0.0000 | 0.0074 | 0.0198 | 0.0002 | 0.0028 | 0.0018 | 0.0000 | 0.0035 | 0.0694 | 0.0000 | 0.0017 | 0.0000 |
| round1 | latin | 493 | 0.0162 | 0.0101 | 0.0020 | 0.0122 | 0.0101 | 0.0183 | 0.0000 | 0.0041 | 0.0101 | 0.0000 | 0.0000 | 0.0061 | 0.0000 | 0.0020 | 0.0000 |
| **all** | | 20,000 | 0.0125 | 0.0086 | 0.0002 | 0.0149 | 0.0076 | 0.0194 | 0.0002 | 0.0029 | 0.0021 | 0.0070 | 0.0033 | 0.0669 | 0.0000 | 0.0021 | 0.0034 |

Final-sigma error parts (occurrences): word-final σ 22; word-internal ς 47, of which ς where the same word with στ is attested in the pool 21; compound-boundary / aphaeresis ς (print orthography, NOT counted) 65. Spacing mark word-initially before a capital (e.g. ᾿Α for Ἀ): 1,309 lines.

Total flagged lines per type: digit_heavy 250, punct_heavy 173, symbol_heavy 4, all_caps 297, long_token 151, word_length_outlier 389, repeated_run 4, numeric_table 59, bibliographic 42, running_title_or_page_number 140, final_sigma_error 66, spacing_apostrophe 1,338, line_end_not_sign 0, dictionary_like 41, digitisation_stamp 69.

## 4. Book reference populations and hard flags

Book script class = majority class of its lines. Reference books: n_lines >= 30; final-sigma reference additionally needs >= 100 Greek words.

| class | books | ref books (N for z) | final-sigma ref N | final-sigma rate p95 | all-caps share p95 | capital-initial p95 |
|---|---:|---:|---:|---:|---:|---:|
| greek_poly | 49 | 49 | 49 | 0.0015 | 0.048 | 0.596 |

Hard-flag books per flag: all_caps_above_class_p95 **3**, final_sigma_above_class_p95 **3**; books with ≥1 hard flag: **6**; verse-like books (informational): 3.

### Hard-flag books, ranked (number of hard flags, then features beyond 2σ vs same-class books)

| # | source | book_key | waves | class | n | hard flags (reasons) | features beyond 2σ |
|---:|---|---|---|---|---:|---|---:|
| 1 | anemi_round1 | 928e34aaaa78469aacd6c7ef | round1 | greek_poly | 214 | **all_caps_above_class_p95**: all-caps line share 0.051 > greek_poly book p95 0.048 (N=49 books) | 6 |
| 2 | anemi_round1 | ffe26907d1e3e9c1f75337e2 | round1 | greek_poly | 501 | **all_caps_above_class_p95**: all-caps line share 0.052 > greek_poly book p95 0.048 (N=49 books) | 3 |
| 3 | anemi_round1 | 0bff55647d1c2acd1caa8bf3 | round1 | greek_poly | 406 | **all_caps_above_class_p95**: all-caps line share 0.071 > greek_poly book p95 0.048 (N=49 books) | 2 |
| 4 | anemi_round1 | d55d101cb2fa4c91b9e11083 | round1 | greek_poly | 413 | **final_sigma_above_class_p95**: final-sigma error rate 0.0019 (5/2653 Greek words) > greek_poly book p95 0.0015 (N=49 books) | 1 |
| 5 | anemi_round1 | 53e3db8de066783d632e29c5 | round1 | greek_poly | 184 | **final_sigma_above_class_p95**: final-sigma error rate 0.0021 (3/1438 Greek words) > greek_poly book p95 0.0015 (N=49 books) | 1 |
| 6 | anemi_round1 | c20219eff76f2fbc39f4c6fd | round1 | greek_poly | 782 | **final_sigma_above_class_p95**: final-sigma error rate 0.0015 (9/6125 Greek words) > greek_poly book p95 0.0015 (N=49 books) | 0 |

### Verse-like books (informational)

| source | book_key | class | n | reason |
|---|---|---|---:|---|
| anemi_round1 | 0bff55647d1c2acd1caa8bf3 | greek_poly | 406 | capital-initial line share 0.608 > greek_poly book p95 0.596 and median length 40 < greek_poly book median 54 |
| anemi_round1 | 686431e9a7fe04175e6e9be9 | greek_poly | 693 | capital-initial line share 0.646 > greek_poly book p95 0.596 and median length 29 < greek_poly book median 54 |
| anemi_round1 | 928e34aaaa78469aacd6c7ef | greek_poly | 214 | capital-initial line share 1.000 > greek_poly book p95 0.596 and median length 21 < greek_poly book median 54 |

### Books with most features beyond 2σ (z of medians + z of flag shares, same-class books)

| source | book_key | class | n | n beyond 2σ | largest |z| (feature: z) |
|---|---|---|---:|---:|---|
| anemi_round1 | 1697d5cc21fa26717b97e073 | greek_poly | 806 | 8 | median digit_share: +6.9; share numeric_table: +6.8; share bibliographic: +5.6; share digit_heavy: +4.9 |
| anemi_round1 | 928e34aaaa78469aacd6c7ef | greek_poly | 214 | 6 | median longest_token: -3.1; median n_chars: -2.9; median n_tokens: -2.8; share word_length_outlier: +2.6 |
| anemi_round1 | 6c82556081bbe4aada41e496 | greek_poly | 718 | 4 | median n_chars: +4.2; median n_tokens: +4.2; median longest_token: +2.7; share long_token: +2.5 |
| anemi_round1 | eed91c3c88be77cac51e7629 | greek_poly | 480 | 4 | share spacing_apostrophe: +3.2; median upper_share: +2.8; share digit_heavy: +2.6; share dictionary_like: +2.2 |
| anemi_round1 | ffe26907d1e3e9c1f75337e2 | greek_poly | 501 | 3 | share running_title_or_page_number: +3.2; share digitisation_stamp: +3.0; share all_caps: +2.2; median y_rel: +1.6 |
| anemi_round1 | 8a77bd3f3cff4d5e3bec99f0 | greek_poly | 479 | 3 | share digitisation_stamp: +3.1; share bibliographic: +2.7; share running_title_or_page_number: +2.4; share all_caps: +1.1 |
| anemi_round1 | 727f1e3f8d0a3a622943e9b1 | greek_poly | 262 | 3 | share dictionary_like: +5.7; share punct_heavy: +5.0; median punct_share: +4.1; share spacing_apostrophe: -1.1 |
| anemi_round1 | db1ed5f902d696fb53656a7d | greek_poly | 482 | 2 | share digitisation_stamp: +2.7; share running_title_or_page_number: +2.4; share all_caps: +1.2; share long_token: +0.8 |
| anemi_round1 | f07e2d5bdef7328dfb1671bf | greek_poly | 522 | 2 | share digitisation_stamp: +2.9; share running_title_or_page_number: +2.2; median y_rel: +1.4; median longest_token: +1.2 |
| anemi_round1 | 0bff55647d1c2acd1caa8bf3 | greek_poly | 406 | 2 | share all_caps: +3.3; share running_title_or_page_number: +2.1; median longest_token: -1.7; median n_chars: -1.2 |
| anemi_round1 | 686431e9a7fe04175e6e9be9 | greek_poly | 693 | 2 | median n_chars: -2.2; median n_tokens: -2.1; median longest_token: -1.7; median upper_share: +1.4 |
| anemi_round1 | 6389d36a8d20c1541b1d4bcb | greek_poly | 366 | 2 | share symbol_heavy: +5.4; share word_length_outlier: +3.7; median n_chars: -1.6; median y_rel: +1.6 |
| anemi_round1 | 66112e132fd96ac8e30e5328 | greek_poly | 529 | 1 | median y_rel: -2.7; share spacing_apostrophe: -1.4; median upper_share: -1.2; median mean_word_len: -1.2 |
| anemi_round1 | 460b94bc8e2c58a95074382b | greek_poly | 529 | 1 | share final_sigma_error: +2.2; share long_token: +1.2; median y_rel: -0.9; share all_caps: -0.8 |
| anemi_round1 | 4fb1fdd9b2f3f5caa8e0be18 | greek_poly | 165 | 1 | share long_token: +3.4; median mean_word_len: +1.3; median longest_token: +1.2; share spacing_apostrophe: -1.2 |
| anemi_round1 | 9e60fbb6b1fc1da9f26b775e | greek_poly | 280 | 1 | share repeated_run: +3.3; share digit_heavy: +1.6; median mean_word_len: +1.3; median longest_token: +1.2 |
| anemi_round1 | 53e3db8de066783d632e29c5 | greek_poly | 184 | 1 | share final_sigma_error: +3.4; median y_rel: +1.3; share word_length_outlier: +1.0; share spacing_apostrophe: +1.0 |
| anemi_round1 | ebf7798c60cbeffbddbfb70a | greek_poly | 64 | 1 | share digitisation_stamp: +2.9; median mean_word_len: +1.8; share word_length_outlier: -1.3; median longest_token: +1.2 |
| anemi_round1 | c194db932e54383910fe40a7 | greek_poly | 182 | 1 | share repeated_run: +5.1; share spacing_apostrophe: -1.1; median mean_word_len: -0.9; share final_sigma_error: -0.8 |
| anemi_round1 | e1006e79dabe16c9460ae218 | greek_poly | 249 | 1 | median mean_word_len: +2.1; share word_length_outlier: +0.9; median n_tokens: -0.9; share final_sigma_error: -0.8 |
| anemi_round1 | 453f156dc6352286456a08cb | greek_poly | 246 | 1 | share symbol_heavy: +3.9; share digit_heavy: +1.9; share word_length_outlier: +1.3; median longest_token: +1.2 |
| anemi_round1 | 18f05e4e68aadfc094bbe31d | greek_poly | 182 | 1 | share spacing_apostrophe: +2.5; share final_sigma_error: -0.8; share digit_heavy: +0.6; share running_title_or_page_number: -0.6 |
| anemi_round1 | d55d101cb2fa4c91b9e11083 | greek_poly | 413 | 1 | share final_sigma_error: +2.4; median mean_word_len: -1.9; median longest_token: -1.7; median y_rel: -1.3 |
| anemi_round1 | b7a2ad096ab8ab67b203d3cd | greek_poly | 385 | 1 | median y_rel: -2.3; share long_token: +1.3; share word_length_outlier: +0.7; share running_title_or_page_number: -0.6 |
| anemi_round1 | 99c8dbb018ec2c87af3fdce9 | greek_poly | 403 | 1 | share long_token: +2.3; median longest_token: +1.2; share final_sigma_error: +1.2; share all_caps: -0.9 |

## 5. Examples (20 random lines per flag type, reservoir sample, fixed seed)

### digit_heavy (250 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `κατὰ μέσον ὅρον 7,000 πλοῖα, ὧν 200 μὲν εἶναι πο-` | docs/records/harvest/harvest_big/round1/crops/b7a2ad096ab8ab67b203d3cd/p000088-l0025.png | digit share 0.175 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 2 | `5, 4, μτγν. ἐλούετο Πολυβ. π. Αθην. 10, 438, μελ. λούσομαι` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000127-l0020.png | digit share 0.146 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 3 | `Θουκ. 4, 28. Μέσ. ἀπαλλάττομαι Πλατ. Παρμ. 156, παρατ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000031-l0031.png | digit share 0.130 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 4 | `λυμανοῦμαι Κωμ. ἀποσπ. 4, 496, μ. ἄορ. ἐλυμηνάμην Εὐρ. Ελ. 1099, Ηρ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000127-l0083.png | digit share 0.140 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 5 | `. 38, π. μελ. ἀποφηθήσομαι Αυσ. 22, 14 ἀγορεύω.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000031-l0017.png | digit share 0.154 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 6 | `Βολιναῖος ποτμ. Αχ. 158` | docs/records/harvest/harvest_big/round1/crops/eed91c3c88be77cac51e7629/p000198-l0015.png | digit share 0.150 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 7 | `ἐτελεύτησα Θουκ. 2, 41, παρκ, τετελεύτηκα Αυσ. 2, 74.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000189-l0004.png | digit share 0.133 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 8 | `τῶν ἐξαγομένων εἰς 400,000.` | docs/records/harvest/harvest_big/round1/crops/b7a2ad096ab8ab67b203d3cd/p000088-l0031.png | digit share 0.250 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 9 | `Γαρέαὶ πόλ. ᾿Αρκδ. 178` | docs/records/harvest/harvest_big/round1/crops/eed91c3c88be77cac51e7629/p000198-l0044.png | digit share 0.158 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 10 | `Οἰνόφυτα πόλ. Βτ. 110` | docs/records/harvest/harvest_big/round1/crops/eed91c3c88be77cac51e7629/p000209-l0043.png | digit share 0.167 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 11 | `Ἐν ᾿Αθήναις, τὴν 21 Νοεμβρίου (3) Δεκεμβρίου) 1868.` | docs/records/harvest/harvest_big/round1/crops/6c82556081bbe4aada41e496/p000016-l0007.png | digit share 0.159 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 12 | `Νίσα πόλ. Μγρδ. 140` | docs/records/harvest/harvest_big/round1/crops/eed91c3c88be77cac51e7629/p000209-l0006.png | digit share 0.188 > greek_mono p90 of digit-bearing lines 0.155 (n=89) |
| 13 | `ὁ Β΄. (1765-90) μέγας δοὺξ τῆς Τοσκάνης, ὅστις τῷ` | docs/records/harvest/harvest_big/round1/crops/9e60fbb6b1fc1da9f26b775e/p002060-l0025.png | digit share 0.146 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 14 | `7] Ἡ ἐν Λαοδικεία, τῷ 357.` | docs/records/harvest/harvest_big/round1/crops/cf2272f4329d987f840e81ab/p000039-l0038.png | digit share 0.190 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 15 | `Θαύματα τοῦ 1872.` | docs/records/harvest/harvest_big/round1/crops/460b94bc8e2c58a95074382b/p000044-l0007.png | digit share 0.267 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 16 | `Νίσαία ἐπίνειον Μγρδ. 142` | docs/records/harvest/harvest_big/round1/crops/eed91c3c88be77cac51e7629/p000209-l0007.png | digit share 0.136 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 17 | `76, ἴων. κατέατο (Ξἐκάθηντο) Ηρ. 9, 90, μελ. καθήσεσθε Εὐρ. ἀποσπ. 952` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000103-l0090.png | digit share 0.136 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 18 | `πάσης κινήσεως αἰτία. Ἡ ἐν Νόμοις (896Ε 897 Β) κακὴ ψυχὴ σελ. 44)` | docs/records/harvest/harvest_big/round1/crops/54a124e5cac779ec617e3ace/p000010-l0006.png | digit share 0.151 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 19 | `γύπτῳ (τῷ 1865 καὶ τῷ 1883) ἀθρόοι οἱ αὐτόθι Λέριοι κατέφυγον εἰς` | docs/records/harvest/harvest_big/round1/crops/453f156dc6352286456a08cb/p000155-l0034.png | digit share 0.148 > greek_poly p90 of digit-bearing lines 0.128 (n=2173) |
| 20 | `184. 186 καὶ ἐναντίον τοῦ Cohen ἔνθ. ἀνωτ. σελ. 437, τοῦ πρώτου διι-` | docs/records/harvest/harvest_big/round1/crops/54a124e5cac779ec617e3ace/p000100-l0034.png | digit share 0.161 > greek_latin_cs p90 of digit-bearing lines 0.123 (n=69) |

### punct_heavy (173 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `clu-o-ἀκούω), ἀ-κρο-άομαι. Παρ. ἀκοή, θυοσ-κόος, Λαο-κόων, Δημο-κόων.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000019-l0083.png | punctuation share 0.238 > greek_latin_cs p99 of punctuated lines 0.233 |
| 2 | `(ΕΠΙΤ. ΒΙΟΓΡ ΙΣΤΟΡΙΑ, - ΤΕΥΧ, Β').` | docs/records/harvest/harvest_big/round1/crops/e1006e79dabe16c9460ae218/p000131-l0053.png | punctuation share 0.276 > greek_mono p99 of punctuated lines 0.255 |
| 3 | `Στρουθός. Τὸ κ. σπουργίτι. (Ιλ. Β. 311).` | docs/records/harvest/harvest_big/round1/crops/ef3cad078cfd452259f5b836/p000115-l0028.png | punctuation share 0.235 > greek_poly p99 of punctuated lines 0.206 |
| 4 | `Επ. ἔρχαται (Ξἔρχνται) Ιλ. σ, 481, ὑπερσ. ὑπερσ. γ. πλ. ἐπ. ἐπ. ἔρχατο, ρ, 354, ὑποτ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000078-l0111.png | punctuation share 0.229 > greek_poly p99 of punctuated lines 0.206 |
| 5 | `Μήπως; ὤ! εἰπέ.` | docs/records/harvest/harvest_big/round1/crops/723c450ea9bb07fc4cdf47f9/p000039-l0007.png | punctuation share 0.231 > greek_poly p99 of punctuated lines 0.206 |
| 6 | `»(Υπογ). Ι. ΔΕΛΙΓΙΑΝΝΗΣ».` | docs/records/harvest/harvest_big/round1/crops/6c82556081bbe4aada41e496/p000013-l0005.png | punctuation share 0.304 > greek_mono p99 of punctuated lines 0.255 |
| 7 | `Ηρ. 1, 170, παρκ. γ. πλ. δειδέχαται Οδ. η, 72, ὑπερσ. ἐπ. γ. ἐν. δείδεκτο Ιλ. τ, 224, γ. πλ. δειδέχατο` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000055-l0093.png | punctuation share 0.220 > greek_poly p99 of punctuated lines 0.206 |
| 8 | `Ὀχέω (φέρω, σηκώνω τι, ὑποφέρω) Ξεν. Κυρ. 1, 3, 8, μελ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000152-l0041.png | punctuation share 0.222 > greek_poly p99 of punctuated lines 0.206 |
| 9 | `καὶ μετὰ ε προτακτ. ἐ-ρεύγ-ομαι, ἐ-ρυγ-γάνω, ἤ-ρυγ-ον, ἐ-φυγή,` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000078-l0071.png | punctuation share 0.218 > greek_poly p99 of punctuated lines 0.206 |
| 10 | `μην. Παρ. ἄρσις, ἄρμα.` | docs/records/harvest/harvest_big/round1/crops/727f1e3f8d0a3a622943e9b1/p000012-l0003.png | punctuation share 0.211 > greek_poly p99 of punctuated lines 0.206 |
| 11 | `Πολύς, ὁ, γεν. πολλοῦ, δοτ. πολλῷ, αἰτ. πολύν, κλ. πολύ,` | docs/records/harvest/harvest_big/round1/crops/727f1e3f8d0a3a622943e9b1/p000123-l0002.png | punctuation share 0.213 > greek_poly p99 of punctuated lines 0.206 |
| 12 | `Σκήπ-τ-ω (ἀκουμβῶ), μᾶλλον σύνθ. μελ. σκήψω, ἀορ. ἔ-` | docs/records/harvest/harvest_big/round1/crops/727f1e3f8d0a3a622943e9b1/p000093-l0019.png | punctuation share 0.222 > greek_poly p99 of punctuated lines 0.206 |
| 13 | `5) τρέχω (παροιμία). 6) γεν. Θάλεω (ἰωνικῶς). 7) ῥᾴ-` | docs/records/harvest/harvest_big/round1/crops/c20219eff76f2fbc39f4c6fd/p000047-l0026.png | punctuation share 0.250 > greek_poly p99 of punctuated lines 0.206 |
| 14 | `θαυμαστὸς Ησυχ. θά-ομαι, θᾶ-έ-ομαι (των.. θη-έ-ομαι ἀττ. θε-ά-` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000091-l0101.png | punctuation share 0.236 > greek_poly p99 of punctuated lines 0.206 |
| 15 | `Πῦρ, τό, γεν. πυρός, δοτ. πυρί, πληθ. πυρά, γεν. πυρῶν,` | docs/records/harvest/harvest_big/round1/crops/727f1e3f8d0a3a622943e9b1/p000123-l0024.png | punctuation share 0.217 > greek_poly p99 of punctuated lines 0.206 |
| 16 | `Πλύν- ω (πλένω) ᾿Αριστοτ. προβλ. 23, 40, ἀπαρ. -ειν Ξεν.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000164-l0070.png | punctuation share 0.213 > greek_poly p99 of punctuated lines 0.206 |
| 17 | `ὄφελ-ος, ὀφείλω ὁ ὀφέλλω (=ὀφελ-ίω), ὄφλ-ω, ὀφλ-ισκάνω, ὠφελ-έω,` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000152-l0021.png | punctuation share 0.211 > greek_poly p99 of punctuated lines 0.206 |
| 18 | `ἐκρυβόμην (μτγν.).` | docs/records/harvest/harvest_big/round1/crops/727f1e3f8d0a3a622943e9b1/p000059-l0041.png | punctuation share 0.235 > greek_poly p99 of punctuated lines 0.206 |
| 19 | `ἀορ. 6. ἐκαθ-άρην, ὑποκ. ἀποκαθ-αρῇ ᾿Αρρ. κυν. 27, 1, π. μελ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000103-l0033.png | punctuation share 0.235 > greek_poly p99 of punctuated lines 0.206 |
| 20 | `Ὁ βήξ (ὁ βήχας).` | docs/records/harvest/harvest_big/round1/crops/686431e9a7fe04175e6e9be9/p000216-l0003.png | punctuation share 0.231 > greek_poly p99 of punctuated lines 0.206 |

### symbol_heavy (4 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `44. 226. Beudant, cours élémentaire d'histoire naturelle <` | docs/records/harvest/harvest_big/round1/crops/453f156dc6352286456a08cb/p000209-l0020.png | symbol share 0.020 > latin p99 of symbol-bearing lines 0.020 (n=2) |
| 2 | `ρός, rump-o=ἀνιάω λατ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000127-l0098.png | symbol share 0.050 > greek_latin_cs p99 of symbol-bearing lines 0.048 (n=21) |
| 3 | `«Φρισ \| σώ δε σε \| δέρκομε \| νά»` | docs/records/harvest/harvest_big/round1/crops/6389d36a8d20c1541b1d4bcb/p000026-l0005.png | symbol share 0.125 > greek_mono p99 of symbol-bearing lines 0.122 (n=10) |
| 4 | `Ἢ Θεὸς \| ἤλθ᾽ ἐπὶ \| γῆν ἐξ \| οὐρανοῦ \| εἰκόνα \| δείξων` | docs/records/harvest/harvest_big/round1/crops/6389d36a8d20c1541b1d4bcb/p000068-l0028.png | symbol share 0.122 > greek_poly p99 of symbol-bearing lines 0.104 (n=83) |

### all_caps (297 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/ffe26907d1e3e9c1f75337e2/p000100-l0022.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 2 | `ΒΙΒΛΙΟΝ ΔΕΚΑΤΟΝ` | docs/records/harvest/harvest_big/round1/crops/a588c9878d5b1197798bb2c5/p000324-l0002.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 3 | `ΑΝΑΓΝΩΣΘΕΙΣΑ` | docs/records/harvest/harvest_big/round1/crops/f0acb2fc3dab2a9bb69f8726/p000005-l0004.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 4 | `ΛΟΥΚΑΣ ΝΟΤΑΡΑΣ.` | docs/records/harvest/harvest_big/round1/crops/0bff55647d1c2acd1caa8bf3/p000199-l0002.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 5 | `ΛΟΓΟΙ ΕΚΚΛΗΣΙΑΣΤΙΚΟΙ` | docs/records/harvest/harvest_big/round1/crops/bf38261008b005a7898b7005/p000034-l0002.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 6 | `ΠΕΡΙΓΡΑΦΗ ΟΛΗΣ ΤΗΣ ΝΗΣΟΥ.` | docs/records/harvest/harvest_big/round1/crops/460b94bc8e2c58a95074382b/p000023-l0036.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 7 | `ΛΟΥΚΑΣ ΝΟΤΑΡΑΣ,` | docs/records/harvest/harvest_big/round1/crops/0bff55647d1c2acd1caa8bf3/p000247-l0001.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 8 | `ΛΟΓΟΙ ΕΚΚΛΗΣΙΑΣΤΙΚΟΙ` | docs/records/harvest/harvest_big/round1/crops/bf38261008b005a7898b7005/p000074-l0057.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 9 | `ΔΗΜΟΣ ΑΛΙΚΙΑΝΟΥ.` | docs/records/harvest/harvest_big/round1/crops/6296ac8dc850e29e2fa2f0b1/p000018-l0002.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 10 | `ΚΕΦΑΛΑΙΟΝ ΠΡΩΤΟΝ` | docs/records/harvest/harvest_big/round1/crops/eed91c3c88be77cac51e7629/p000019-l0003.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 11 | `ΟΛΓΑΣ Θ. ΙΩΑΝΝΙΔΟΥ` | docs/records/harvest/harvest_big/round1/crops/928e34aaaa78469aacd6c7ef/p000035-l0001.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 12 | `ΣΚΗΝΗ ΔΕΚΑΤΗ.` | docs/records/harvest/harvest_big/round1/crops/0bff55647d1c2acd1caa8bf3/p000087-l0016.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 13 | `ΠΑΝΕΠΙΣΤΗΜΙΟ` | docs/records/harvest/harvest_big/round1/crops/f07e2d5bdef7328dfb1671bf/p000130-l0035.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 14 | `ΗΛΙΑ ΤΑΝΤΑΛΙΔΟΥ` | docs/records/harvest/harvest_big/round1/crops/1118b0c89e773062b4cf69f5/p000101-l0001.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 15 | `ΣΚΗΝΗ ΕΝΝΑΤΗ.` | docs/records/harvest/harvest_big/round1/crops/0bff55647d1c2acd1caa8bf3/p000087-l0007.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 16 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗ` | docs/records/harvest/harvest_big/round1/crops/ffe26907d1e3e9c1f75337e2/p000136-l0001.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 17 | `ΠΕΡΙ ΤΗΣ ΦΥΣΙΚΗΣ ΘΕΟΓΝΩΣΙΑΣ.` | docs/records/harvest/harvest_big/round1/crops/cf2272f4329d987f840e81ab/p000061-l0021.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 18 | `ΠΑΡΩΧΗΜΕΝΟΣ ΑΟΡΙΣΤΟΣ.` | docs/records/harvest/harvest_big/round1/crops/686431e9a7fe04175e6e9be9/p000112-l0005.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 19 | `Ι. ΔΕΛΙΓΙΑΝΝΗΣ.` | docs/records/harvest/harvest_big/round1/crops/6c82556081bbe4aada41e496/p000026-l0037.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |
| 20 | `Ι. ΔΕΛΙΓΙΑΝΝΗΣ.` | docs/records/harvest/harvest_big/round1/crops/6c82556081bbe4aada41e496/p000023-l0037.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.432 |

### long_token (151 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `παθ. παρκ. ἐσκεύασμαι, π. μελ. κατα-σκευασθήσομαι. Μέσ` | docs/records/harvest/harvest_big/round1/crops/727f1e3f8d0a3a622943e9b1/p000093-l0014.png | longest token 19 chars > greek_poly p99 16 |
| 2 | `ἐν Κωνσταντινουπόλει σύνοδον ἐκ 383 περίπου ἐπισκόπων τῷ 879,` | docs/records/harvest/harvest_big/round1/crops/ecadd6f5c84ab0f85c671729/p000111-l0006.png | longest token 17 chars > greek_poly p99 16 |
| 3 | `28. Νέα τις Θεοδωροῦλα ἀπὸ γαλατᾶν Κωνσταντινουπόλεως·` | docs/records/harvest/harvest_big/round1/crops/460b94bc8e2c58a95074382b/p000020-l0037.png | longest token 19 chars > greek_poly p99 16 |
| 4 | `μικαῖς οὐσίαις ἐπεξεργαζομένοις, τὰ δὲ εἰς τὴν μυελώδη οὐ-` | docs/records/harvest/harvest_big/round1/crops/f0acb2fc3dab2a9bb69f8726/p000030-l0019.png | longest token 17 chars > greek_poly p99 16 |
| 5 | `τῶν πλεγματοειδῶν ἀγγειοσαρκωμάτων, εἶνε δὲ ἀξιοσημείωτον` | docs/records/harvest/harvest_big/round1/crops/f0acb2fc3dab2a9bb69f8726/p000040-l0019.png | longest token 17 chars > greek_poly p99 16 |
| 6 | `Ἡ ἑορτὴ τῆς τετρακοσιετηρίδος τοῦ Λουθήρου` | docs/records/harvest/harvest_big/round1/crops/ecadd6f5c84ab0f85c671729/p000151-l0002.png | longest token 17 chars > greek_poly p99 16 |
| 7 | `Ἡ Ῥωσσικὴ ἐκκλησία ἀπὸ Κωνσταντινουπόλεως λαβοῦσα τὸ` | docs/records/harvest/harvest_big/round1/crops/18ed614c7b7c25896c49680b/p000115-l0055.png | longest token 18 chars > greek_poly p99 16 |
| 8 | `τιωθῶσι κατὰ ποιὸν, ἐπολλαπλασιάσθησαν τὰ σχολεία κατὰ` | docs/records/harvest/harvest_big/round1/crops/4fb1fdd9b2f3f5caa8e0be18/p000024-l0029.png | longest token 18 chars > greek_poly p99 16 |
| 9 | `πολιτικῆς; καὶ πρὸ πάντων ὅταν ἀντιπολιτεύωνται, γνωρί` | docs/records/harvest/harvest_big/round1/crops/4fb1fdd9b2f3f5caa8e0be18/p000017-l0004.png | longest token 17 chars > greek_poly p99 16 |
| 10 | `τῶνμεγαλοπρεπῶνκοσμημάτων. Πρωΐανλοιπόν τινα εἶδον εἰσερχό` | docs/records/harvest/harvest_big/round1/crops/46241fd09ba5dae869149357/p000137-l0010.png | longest token 26 chars > greek_poly p99 16 |
| 11 | `Ὁ ἐν Κωνσταντινουπόλει Πρεσβευτὴς τῆς Αὐτοῦ Μεγαλειότητος` | docs/records/harvest/harvest_big/round1/crops/6c82556081bbe4aada41e496/p000026-l0013.png | longest token 17 chars > greek_poly p99 16 |
| 12 | `βόμενοι, καταστρεφόμενοι, διασκορπιζόμενοι· ἂς δράμω λοιπόν` | docs/records/harvest/harvest_big/round1/crops/292f4a0b4f0dc8e6dddb103d/p000386-l0014.png | longest token 17 chars > greek_poly p99 16 |
| 13 | `Ὁ Πρῶτος Διερμηνεὺς τῆς ἐν Κωνσταντινουμόλει Β. Πρεσβείας` | docs/records/harvest/harvest_big/round1/crops/6c82556081bbe4aada41e496/p000019-l0005.png | longest token 17 chars > greek_poly p99 16 |
| 14 | `ἐδάφους καὶ ἐδόθη εἰς τὴν φυγὴν, ὑπερευχαριστηθεὶς διότι ἐξε` | docs/records/harvest/harvest_big/round1/crops/ffe26907d1e3e9c1f75337e2/p000247-l0028.png | longest token 17 chars > greek_poly p99 16 |
| 15 | `ρίας ἠδύναντο νὰ ἔχωσιν᾽ ἦλθον λοιπὸν εἰς διαπραγματεύσεις,` | docs/records/harvest/harvest_big/round1/crops/46241fd09ba5dae869149357/p000120-l0012.png | longest token 17 chars > greek_poly p99 16 |
| 16 | `σάρκωμα στρογγυλοκύτταρον τοῦ μεσεντερίου ὑπὸ τοῦ κ. Σ.` | docs/records/harvest/harvest_big/round1/crops/f0acb2fc3dab2a9bb69f8726/p000040-l0015.png | longest token 17 chars > greek_poly p99 16 |
| 17 | `πραγματοποιήθησαν. Οὐχὶ μόνον τοῖς ἀπηγορεύθη νὰ συγκοινωνήσωσι μετὰ τῶν οἰκογενειῶν των, ἀλλ᾿ ἕνε-` | docs/records/harvest/harvest_big/round1/crops/6c82556081bbe4aada41e496/p000016-l0018.png | longest token 18 chars > greek_poly p99 16 |
| 18 | `νοτιανατολικώτερον, ὁ δὲ ἐκ νότου βορειανατολικώτερον ...` | docs/records/harvest/harvest_big/round1/crops/96bb7196d840fe7513c2ed43/p000015-l0018.png | longest token 19 chars > greek_poly p99 16 |
| 19 | `νατολικώτερον, ὁ δὲ δεύτερος βορειοδυτικώτερον.» Τώρα λέν` | docs/records/harvest/harvest_big/round1/crops/96bb7196d840fe7513c2ed43/p000015-l0022.png | longest token 19 chars > greek_poly p99 16 |
| 20 | `νοντες εἰς τὴν ἰδέαν, ὅτι εἶναι ἀναντικατάστατοι, ὅπως οἱ` | docs/records/harvest/harvest_big/round1/crops/4fb1fdd9b2f3f5caa8e0be18/p000024-l0004.png | longest token 17 chars > greek_poly p99 16 |

### word_length_outlier (389 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `ἄλλοτε ὑπ᾽ ἄλλων καὶ τὸ 220 [π. Χ.] ὑπὸ Αἰτωλῶν στρα` | docs/records/harvest/harvest_big/round1/crops/eed91c3c88be77cac51e7629/p000045-l0006.png | mean word length 3.40 over 10 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 2 | `τῇ εὐρωπαϊκῇ Τουρκίᾳ διεσπαρμένων Βουλγάρων ἐκκλησιαστι` | docs/records/harvest/harvest_big/round1/crops/18ed614c7b7c25896c49680b/p000144-l0020.png | mean word length 8.33 over 6 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 3 | `καὶ στή τω με τὰ φόβου καὶ τρόμου. 5` | docs/records/harvest/harvest_big/round1/crops/6389d36a8d20c1541b1d4bcb/p000153-l0014.png | mean word length 3.25 over 8 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 4 | `πολλάκις ἐκ συμφώνου ἐπληροφορήθημεν.` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000051-l0031.png | mean word length 8.25 over 4 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 5 | `Οἱ δὲ πρὸς θρόνους ἔσω μο λόν τες Εὐρ.0.1418)` | docs/records/harvest/harvest_big/round1/crops/6389d36a8d20c1541b1d4bcb/p000052-l0054.png | mean word length 3.22 over 9 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 6 | `ἐπολλαπλασιάσθησαν αἱ κατώτεραι ἐκκλησιαστικαὶ σχολαίς` | docs/records/harvest/harvest_big/round1/crops/18ed614c7b7c25896c49680b/p000184-l0011.png | mean word length 10.00 over 5 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 7 | `λανθρωπικὰ καταστήματα, πτωχοκομεῖα, γηροκομεῖα καὶ` | docs/records/harvest/harvest_big/round1/crops/ecadd6f5c84ab0f85c671729/p000028-l0032.png | mean word length 9.00 over 5 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 8 | `ἐκκλησιαστικοὶ συγγραφεῖς. ᾿Αθανάσιος Πάριος (1813), σχο` | docs/records/harvest/harvest_big/round1/crops/18ed614c7b7c25896c49680b/p000170-l0033.png | mean word length 8.40 over 5 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 9 | `τὸν ιβ΄. αἰῶνα.` | docs/records/harvest/harvest_big/round1/crops/6296ac8dc850e29e2fa2f0b1/p000082-l0006.png | mean word length 3.33 over 3 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 10 | `θα' δὲ ὁ ᾿Αστυάγης λέγει πρὸς τὸν Κῦρον· ὦ παῖ,` | docs/records/harvest/harvest_big/round1/crops/c20219eff76f2fbc39f4c6fd/p000053-l0017.png | mean word length 3.40 over 10 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 11 | `περιφρονητικῶν ἐκείνων μειδιαμάτων, ἅτινα ἦσαν ἀποκλειστικῶς` | docs/records/harvest/harvest_big/round1/crops/46241fd09ba5dae869149357/p000110-l0007.png | mean word length 9.00 over 6 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 12 | `σημεῖα ἐπιτρέποντα συστηματικὴν ὀχύρωσιν πρὸς ἀναχαίτη-` | docs/records/harvest/harvest_big/round1/crops/cd71a3283d310fc887e742d5/p000027-l0025.png | mean word length 8.17 over 6 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 13 | `Ἐδέσσης (Βοδενῶν), Κορυτσᾶς, Βελεγράδων, Τιβεριουπόλεως (Στρω-` | docs/records/harvest/harvest_big/round1/crops/9e60fbb6b1fc1da9f26b775e/p000984-l0014.png | mean word length 8.33 over 6 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 14 | `ἡ Ἐράτυρα. – [δ' τὰ Σέρβια.]` | docs/records/harvest/harvest_big/round1/crops/eed91c3c88be77cac51e7629/p000033-l0008.png | mean word length 3.40 over 5 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 15 | `Ἓν Παρθεναγωγεῖον, καλούμενον Αρσάκειον` | docs/records/harvest/harvest_big/round1/crops/b7a2ad096ab8ab67b203d3cd/p000072-l0008.png | mean word length 8.75 over 4 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 16 | `χετε εἰς τὸν νοῦν σας.` | docs/records/harvest/harvest_big/round1/crops/686431e9a7fe04175e6e9be9/p000277-l0046.png | mean word length 3.40 over 5 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 17 | `ἀναφανέντων ἀναβαπτιστῶν, ἐνομασθέντες μετὰ ταῦτα Μεννω` | docs/records/harvest/harvest_big/round1/crops/18ed614c7b7c25896c49680b/p000198-l0043.png | mean word length 8.17 over 6 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 18 | `ἐμοί τε καὶ τῇ σὺν ἐμοὶ στρατιᾷ. Ἐγὼ δὲ, ἔφη ὁ` | docs/records/harvest/harvest_big/round1/crops/c20219eff76f2fbc39f4c6fd/p000060-l0023.png | mean word length 3.09 over 11 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 19 | `τὸν χριστιανισμὸν, καὶ αὐτοκράτορας συμβουλεύσας. Μιμητής` | docs/records/harvest/harvest_big/round1/crops/18ed614c7b7c25896c49680b/p000089-l0029.png | mean word length 8.33 over 6 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |
| 20 | `γης, π.λάνης, γυμνής. β) τὰ εἰς ας, αδος· ὡς φυγάς, φορ-` | docs/records/harvest/harvest_big/round1/crops/c20219eff76f2fbc39f4c6fd/p000021-l0013.png | mean word length 3.36 over 11 words outside greek_poly [p1 3.40, p99 8.00] of >=3-word lines |

### repeated_run (4 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `(10000 – μ.) εἶναι καὶ χαμηλότερον τῆς ἐπιφανείας τῆς` | docs/records/harvest/harvest_big/round1/crops/96bb7196d840fe7513c2ed43/p000017-l0013.png | 1 run(s) of >=4 identical chars, max 4, chars '0'; greek_poly line rate 0.0002 |
| 2 | `χὴς καὶ ἐπιζήμιος τῷ ἑλληνικῷ ἔθνει........διὰ τοῦ νέου τούτου ὀργανισμοῦ ἡ` | docs/records/harvest/harvest_big/round1/crops/9e60fbb6b1fc1da9f26b775e/p001792-l0013.png | 1 run(s) of >=4 identical chars, max 8, chars '.'; greek_poly line rate 0.0002 |
| 3 | `ὑποφέρω! . . Ἔπειτα .... τὸ ἀγαπᾶσθαι, ὡς ἠγαπώ-` | docs/records/harvest/harvest_big/round1/crops/c194db932e54383910fe40a7/p000272-l0025.png | 1 run(s) of >=4 identical chars, max 4, chars '.'; greek_poly line rate 0.0002 |
| 4 | `τ' ἐστι καὶ πεπήρωται τοὺς ὀφθαλμούς· ὁ δὲ ἁλιαίετος»....` | docs/records/harvest/harvest_big/round1/crops/ef3cad078cfd452259f5b836/p000115-l0035.png | 1 run(s) of >=4 identical chars, max 4, chars '.'; greek_poly line rate 0.0002 |

### numeric_table (59 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `4. 40,4. 41,1.2) εὕρομεν ἀφορμὴν νὰ θαυμάσωμεν τὴν ἐπιείκειαν` | docs/records/harvest/harvest_big/round1/crops/9e60fbb6b1fc1da9f26b775e/p000175-l0008.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 2 | `Κρέμ-αμαι (κρεμῶμαι) Ξεν. ἀν. 3, 2, 19, ὑποτ. κρέμη-` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000117-l0015.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 3 | `Ὀχέω (φέρω, σηκώνω τι, ὑποφέρω) Ξεν. Κυρ. 1, 3, 8, μελ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000152-l0041.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 4 | `σθαι Ξεν. ἀπομν. 2, 7, 1, μτχ. ἀκούμενος Πλατ. Φιλ. 30, ἀλλὰ` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000019-l0027.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 5 | `ἀποθ. ἀκροβολίζεσθαι Ξεν. Κυρ. 8, 8, 22, ἀορ. ἠκροβολισάμην` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000019-l0105.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 6 | `Ξεν. ἀν. 6, 5, 30, π. παρκ. ἀπηγόρευμαι Αριστοτ. πολιτ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000031-l0013.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 7 | `154, ἀορ. ἔκρουσα Ξεν. ἀν. 4, 5, 18, παρκ. κέκρουκα Διογ. παν` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000117-l0097.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 8 | `Φιλ. 24, -ξατο Ξεν. Κυρ. 7, 1, 3, παρκ. ἔφθεγμαι Πλατ. ἐπιστ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000201-l0072.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 9 | `σαι Ξεν. ἀν. 1, 2, 8, π. ὑπερσ. κατα-κεκρέμαστο Δ. Σικ. 18,` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000117-l0029.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 10 | `μαι Ξεν. Κυρ. 3, 1, 15. Παρ. βουλευτέον Θουκ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000046-l0028.png | 3 consecutive numeric tokens; greek_mono line rate 0.0059 |
| 11 | `Ξεν. Κυρ. 1, 3, 11, λούεται Λουκ. φιλοψ. 19, ἀπαρ. λούεσθαι` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000127-l0017.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 12 | `νοντο, ἰουδ. πολ. 5, 2, 4. Παρ. φθαστέον.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000201-l0047.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 13 | `Χρυσανθ. Συνταγμ. 72. 86. 87. Καὶ ἡ μὲν τοῦ Τυρνάβου αὐτονομία εἶ-` | docs/records/harvest/harvest_big/round1/crops/18ed614c7b7c25896c49680b/p000144-l0033.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 14 | `Κυρ. 8, 4, 21, ὑπερσ. ἐδεδειπνήκειν ᾿Αντιφ. 1, 18. Τοῦ δὲ δει-` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000055-l0120.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 15 | `ρατ. ἐκρεμάμην, ἀν. 4, 1, 2, μελ. κρεμήσομαι Λουκ. δραπ. 31.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000117-l0017.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 16 | `δείητε ᾿Ανδοκ. 2, 19, εἰδείηταν Ξεν. Ἑλλ. 4, 2, 6, εἰδεῖεν Κυρ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000067-l0065.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 17 | `ἐθαύμασα Ἰσοκ. 4, 1, παρκ. τεθαύμακα Ξεν. ἀπομν. 1, 4, 2, π.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000091-l0078.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 18 | `4, 1, 6, προστ. ἐπ-ίσπου Πλατ. Θεαιτ. 169, συν-επίσπεσθε,` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000078-l0010.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |
| 19 | `Κυρ. 8, 7, 4, μτχ. λουσάμενος, συμπ. 1, 7. Παρ. λουστέον Γεωπ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000127-l0022.png | 3 consecutive numeric tokens; greek_mono line rate 0.0059 |
| 20 | `θανατώσοιτο Ξεν. Κυρ. 7, 5, 31· ἴδε θνήσκω.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000091-l0007.png | 3 consecutive numeric tokens; greek_poly line rate 0.0028 |

### bibliographic (42 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `δευτέρῳ ἔτει (1798) ἐκινήθη ῥωσσοθωμανικός στόλος διὰ` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000040-l0005.png | patterns ['year_in_parens']; greek_poly line rate 0.0018 |
| 2 | `μτχ.-ύντος Λουκ. Δημ. ἐγκ. 7, σκεδάζων Θεοδ. Στουδ. σ. 139,` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000177-l0051.png | patterns ['σ.+number']; greek_poly line rate 0.0018 |
| 3 | `(1) Ο Π. Αραβαντινὸς ἐν σ. 148 τοῦ πρώτου τόμου τῆς χρονογραφίας` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000122-l0034.png | patterns ['σ.+number']; greek_poly line rate 0.0018 |
| 4 | `(1) Juris Graeco-Romani σ. 100.` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000137-l0030.png | patterns ['σ.+number']; latin line rate 0.0101 |
| 5 | `(3) G. Unger, Philologus σ. 522. Πρβλ. τῆς παρούσης πραγματείας σ. 18.` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000137-l0032.png | patterns ['σ.+number']; greek_latin_cs line rate 0.0088 |
| 6 | `9, 49, π. παρκ. ἔξασμαι, μτχ. ἀν-εξασμένων Ὀρειβ. σ. 195.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000141-l0068.png | patterns ['σ.+number']; greek_poly line rate 0.0018 |
| 7 | `(1540), ἀπέξη ἰσχυρότατον ταχέως διὰ τοῦ αὐστηροῦ` | docs/records/harvest/harvest_big/round1/crops/18ed614c7b7c25896c49680b/p000211-l0015.png | patterns ['year_in_parens']; greek_poly line rate 0.0018 |
| 8 | `θύς; ὁ Ησίοδος ἀριθμεῖ τοὺς Τιτᾶνας οὕτω (Θεογ. σ. 133.)` | docs/records/harvest/harvest_big/round1/crops/96bb7196d840fe7513c2ed43/p000024-l0026.png | patterns ['σ.+number']; greek_poly line rate 0.0018 |
| 9 | `τῷ ἐν Πετρουπόλει (1830) ἐκδοθέντι περὶ γνησίας προφορᾶς τῆς` | docs/records/harvest/harvest_big/round1/crops/6389d36a8d20c1541b1d4bcb/p000163-l0017.png | patterns ['year_in_parens']; greek_poly line rate 0.0018 |
| 10 | `Lamark (1744) καὶ τοῦ Cuvier (1769), ἀποτελεῖ τὴν τετάρ-` | docs/records/harvest/harvest_big/round1/crops/f0acb2fc3dab2a9bb69f8726/p000020-l0025.png | patterns ['year_in_parens']; greek_latin_cs line rate 0.0088 |
| 11 | `(α) Καὶ «ἐκρεμάννυεν ᾿Αττικοί, ἐκρήμνα Ἕλληνες» Μοῖρ. σ. 106, 67` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000117-l0051.png | patterns ['σ.+number']; greek_poly line rate 0.0018 |
| 12 | `συμπίνω), μτχ. κρατηρίζων Φωτ. σ. 176, 13, ὑπερσ. κὴκρατηρίχημες ᾿Αθην.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000117-l0012.png | patterns ['σ.+number']; greek_poly line rate 0.0018 |
| 13 | `λοπούλου ἐφέτου σ. 241.` | docs/records/harvest/harvest_big/round1/crops/bf38261008b005a7898b7005/p000131-l0032.png | patterns ['σ.+number']; greek_poly line rate 0.0018 |
| 14 | `παθ. μτγν. μόν. ἀκεῖται Ἀρεται. αἰτ. ἀσθ. 1, σ. 70, μελ. α. ἀκέ-` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000019-l0028.png | patterns ['σ.+number']; greek_poly line rate 0.0018 |
| 15 | `ρουν Δημ. σ. 30, 15, ἐθάρσουν Θουκ. 3, 25, μελ. θαρρήσω Πλατ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000091-l0053.png | patterns ['σ.+number']; greek_poly line rate 0.0018 |
| 16 | `ἔργ. σ. 301, 4, παρατ. ἐκροταλίζετο Οἰνομ. παρ᾿ Εὐσεβ. Εὐαγγ. προπ. σ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000117-l0094.png | patterns ['σ.+number']; greek_poly line rate 0.0018 |
| 17 | `ἐν τῷ οἰκείῳ τόπῳ τὰ δέοντα (σ. 61). Κατα τὴν ἐποχὴν ταύ` | docs/records/harvest/harvest_big/round1/crops/18ed614c7b7c25896c49680b/p000048-l0042.png | patterns ['σ.+number']; greek_poly line rate 0.0018 |
| 18 | `ρηγοπούλου Ιστορ. Ελλ. ἔθνους. Τ. 3 σ. 367).` | docs/records/harvest/harvest_big/round1/crops/99c8dbb018ec2c87af3fdce9/p000012-l0037.png | patterns ['σ.+number']; greek_poly line rate 0.0018 |
| 19 | `Κατὰ πρῶτον, ὅπως καὶ ἀνωτέρω παρετηρήσαμεν (σ. 89),` | docs/records/harvest/harvest_big/round1/crops/18ed614c7b7c25896c49680b/p000048-l0057.png | patterns ['σ.+number']; greek_poly line rate 0.0018 |
| 20 | `μαι, -θαπται Ηρ. σ. 103, Ἐπιγρ. Πλατ Φαιδρ, 264, γ. πλ. ἰων. τετάφαται` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000091-l0031.png | patterns ['σ.+number']; greek_poly line rate 0.0018 |

### running_title_or_page_number (140 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `ΛΟΥΚΑΣ ΝΟΤΑΡΑΣ,` | docs/records/harvest/harvest_big/round1/crops/0bff55647d1c2acd1caa8bf3/p000247-l0001.png | box y0=18 y1=43 of page h=1294 (in top/bottom 8%), 15 chars <= greek_mono p50 19, no lowercase letters |
| 2 | `ΣΟΥΛΤΑΝ ΣΕΛΙΜ Ο Γ΄.` | docs/records/harvest/harvest_big/round1/crops/e1006e79dabe16c9460ae218/p000131-l0001.png | box y0=20 y1=54 of page h=1284 (in top/bottom 8%), 19 chars <= greek_mono p50 19, no lowercase letters |
| 3 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/ffe26907d1e3e9c1f75337e2/p000302-l0001.png | box y0=1265 y1=1508 of page h=1509 (in top/bottom 8%), 19 chars <= greek_mono p50 19, no lowercase letters |
| 4 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000015-l0032.png | box y0=1430 y1=1674 of page h=1675 (in top/bottom 8%), 19 chars <= greek_mono p50 19, no lowercase letters |
| 5 | `Η ΟΛΛΕΝΔΟΡΦΟΥ` | docs/records/harvest/harvest_big/round1/crops/686431e9a7fe04175e6e9be9/p000112-l0002.png | box y0=88 y1=117 of page h=1664 (in top/bottom 8%), 13 chars <= greek_mono p50 19, no lowercase letters |
| 6 | `ΠΑΝΕΠΙΣΤΗΜΙΟ` | docs/records/harvest/harvest_big/round1/crops/f07e2d5bdef7328dfb1671bf/p000137-l0035.png | box y0=1511 y1=1679 of page h=1732 (in top/bottom 8%), 12 chars <= greek_mono p50 19, no lowercase letters |
| 7 | `ΠΑΝΕΠΙΣΤΗΜΙ` | docs/records/harvest/harvest_big/round1/crops/96bb7196d840fe7513c2ed43/p000038-l0063.png | box y0=1452 y1=1609 of page h=1676 (in top/bottom 8%), 11 chars <= greek_mono p50 19, no lowercase letters |
| 8 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000081-l0034.png | box y0=1258 y1=1503 of page h=1504 (in top/bottom 8%), 19 chars <= greek_mono p50 19, no lowercase letters |
| 9 | `ΟΙ ΚΑΛΛΕΡΓΑΙ.` | docs/records/harvest/harvest_big/round1/crops/0bff55647d1c2acd1caa8bf3/p000120-l0003.png | box y0=36 y1=61 of page h=1294 (in top/bottom 8%), 13 chars <= greek_mono p50 19, no lowercase letters |
| 10 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/f07e2d5bdef7328dfb1671bf/p000121-l0035.png | box y0=1488 y1=1731 of page h=1732 (in top/bottom 8%), 19 chars <= greek_mono p50 19, no lowercase letters |
| 11 | `ΣΟΥΛΤΑΝ ΣΕΛΙΜ Ο Β΄.` | docs/records/harvest/harvest_big/round1/crops/e1006e79dabe16c9460ae218/p000013-l0001.png | box y0=71 y1=102 of page h=1312 (in top/bottom 8%), 19 chars <= greek_mono p50 19, no lowercase letters |
| 12 | `ΛΟΥΚΑΣ ΝΟΤΑΡΑΣ,` | docs/records/harvest/harvest_big/round1/crops/0bff55647d1c2acd1caa8bf3/p000215-l0001.png | box y0=32 y1=55 of page h=1294 (in top/bottom 8%), 15 chars <= greek_mono p50 19, no lowercase letters |
| 13 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000048-l0030.png | box y0=1427 y1=1671 of page h=1672 (in top/bottom 8%), 19 chars <= greek_mono p50 19, no lowercase letters |
| 14 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/f07e2d5bdef7328dfb1671bf/p000106-l0035.png | box y0=1483 y1=1728 of page h=1729 (in top/bottom 8%), 19 chars <= greek_mono p50 19, no lowercase letters |
| 15 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000089-l0035.png | box y0=1259 y1=1503 of page h=1504 (in top/bottom 8%), 19 chars <= greek_mono p50 19, no lowercase letters |
| 16 | `ΠΑΝΕΠΙΣΤΗΜΙΟ` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000012-l0033.png | box y0=1283 y1=1447 of page h=1506 (in top/bottom 8%), 12 chars <= greek_mono p50 19, no lowercase letters |
| 17 | `ΟΙ ΒΥΡΓΡΑΒΟΙ,` | docs/records/harvest/harvest_big/round1/crops/66112e132fd96ac8e30e5328/p000113-l0002.png | box y0=69 y1=90 of page h=1654 (in top/bottom 8%), 13 chars <= greek_mono p50 19, no lowercase letters |
| 18 | `ΑΙ ΠΕΡΙΠΕΤΙΑΙ` | docs/records/harvest/harvest_big/round1/crops/46241fd09ba5dae869149357/p000094-l0002.png | box y0=63 y1=94 of page h=1423 (in top/bottom 8%), 13 chars <= greek_mono p50 19, no lowercase letters |
| 19 | `ΒΙΒΛΙΟΝ ΔΕΚΑΤΟΝ` | docs/records/harvest/harvest_big/round1/crops/a588c9878d5b1197798bb2c5/p000324-l0002.png | box y0=127 y1=153 of page h=1654 (in top/bottom 8%), 15 chars <= greek_mono p50 19, no lowercase letters |
| 20 | `ΟΙ ΚΑΛΛΕΡΓΑΙ.` | docs/records/harvest/harvest_big/round1/crops/0bff55647d1c2acd1caa8bf3/p000104-l0002.png | box y0=64 y1=85 of page h=1294 (in top/bottom 8%), 13 chars <= greek_mono p50 19, no lowercase letters |

### final_sigma_error (66 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `(α) ἐν τῇ βιβλιοθήκη τοῦ Πανεπιςημίου τῶν Ἀθηνῶν εὐρέθη` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000023-l0028.png | 0 word-final σ + 1 word-internal ς (of which 1 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ῦ Πανεπιςημ']); greek_poly line rate 0.0035 |
| 2 | `τὸ ὁποῖον μὲ ἐχάρισες, κυμαινόμενον εἰς τὸν ἀνεμοςρό-` | docs/records/harvest/harvest_big/round1/crops/66112e132fd96ac8e30e5328/p000065-l0023.png | 0 word-final σ + 1 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ὸν ἀνεμοςρό']); greek_poly line rate 0.0035 |
| 3 | `«Φρισ \| σώ δε σε \| δέρκομε \| νά»` | docs/records/harvest/harvest_big/round1/crops/6389d36a8d20c1541b1d4bcb/p000026-l0005.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['«Φρισ /']); greek_mono line rate 0.0015 |
| 4 | `ἴσος μὲ ὑμᾶς κατὰ τὸ ἀνάςημαι` | docs/records/harvest/harvest_big/round1/crops/686431e9a7fe04175e6e9be9/p000338-l0029.png | 0 word-final σ + 1 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ὰ τὸ ἀνάςημ']); greek_poly line rate 0.0035 |
| 5 | `2. ᾿Αλλ᾿ ὁ μέγιςος τῶν πατέρων καὶ διδασκάλων τῆς` | docs/records/harvest/harvest_big/round1/crops/53e3db8de066783d632e29c5/p000157-l0029.png | 0 word-final σ + 1 word-internal ς (of which 1 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['᾿ ὁ μέγιςος']); greek_poly line rate 0.0035 |
| 6 | `ΔΕΩΝ ΚΑΛΛΕΡΓΗΣ ἀρχηγὸς τῶν Κρητῶν ἀποςατῶν.` | docs/records/harvest/harvest_big/round1/crops/723c450ea9bb07fc4cdf47f9/p000024-l0002.png | 0 word-final σ + 1 word-internal ς (of which 1 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ητῶν ἀποςατ']); greek_poly line rate 0.0035 |
| 7 | `πευε μόνον τὴν τῶν ὁπαδῶν τοῦ Μωάμεθ καταςροφὴν, καὶ ἐλὰττό-` | docs/records/harvest/harvest_big/round1/crops/f07e2d5bdef7328dfb1671bf/p000106-l0009.png | 0 word-final σ + 1 word-internal ς (of which 1 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['μεθ καταςρο']); greek_poly line rate 0.0035 |
| 8 | `τωςεἶχε τότε δὴ περισσότερον δίκαιον ἤθελεν ἔχει ἡ ἐν Μα-` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000137-l0027.png | 0 word-final σ + 1 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['τωςεἶ']); greek_poly line rate 0.0035 |
| 9 | `γίους, ὁποῦ εὐαρέςησαν αὐτῷ διὰ τῆς καλῆς` | docs/records/harvest/harvest_big/round1/crops/d55d101cb2fa4c91b9e11083/p000023-l0024.png | 0 word-final σ + 1 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['οῦ εὐαρέςησ']); greek_poly line rate 0.0035 |
| 10 | `«Κάμ μὲν ἀδέψητον βοέην στόρεσσ᾽ αὐτὰρ ὑπερθεν` | docs/records/harvest/harvest_big/round1/crops/ef3cad078cfd452259f5b836/p000108-l0008.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ν στόρεσσ᾽ ']); greek_poly line rate 0.0035 |
| 11 | `᾿Ανὴρ ἄνδρασ καὶ πόλις πόλιν σώζει. – Ἡ κακή` | docs/records/harvest/harvest_big/round1/crops/c20219eff76f2fbc39f4c6fd/p000021-l0050.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ὴρ ἄνδρασ κ']); greek_poly line rate 0.0035 |
| 12 | `τοὺς δικαςὰς ἀπολῦσαι ἑαυτὸντοῦ θανάτου, ἀλλὰ πι-` | docs/records/harvest/harvest_big/round1/crops/c20219eff76f2fbc39f4c6fd/p000030-l0040.png | 0 word-final σ + 1 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['οὺς δικαςὰς']); greek_poly line rate 0.0035 |
| 13 | `» Σὰ σπόρος, ποῦ δὲ σέπεται θαμμένος μὲς ἐσ τὸ χιόνι·` | docs/records/harvest/harvest_big/round1/crops/ef44b5f8b81d770825ea1475/p000036-l0018.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ος μὲς ἐσ τ']); greek_poly line rate 0.0035 |
| 14 | `Διαβιβάζω ὑμῖν ἐσωκλείστως ἀντίγραφον τῆς διαμαρτυρήσεως ἣν διεβίβασ τυρήσεως διεβίβασα χθὲς πρὸς τοὺς ἀντιπροσώπους` | docs/records/harvest/harvest_big/round1/crops/6c82556081bbe4aada41e496/p000051-l0040.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx [' διεβίβασ τ']); greek_poly line rate 0.0035 |
| 15 | `τῇ φιλοσοφίᾳ αὐτῆς μεταςρέψασα, ἡ ἐλαφρὰ φιλο- λογία τοῦ Βαλζάκ,` | docs/records/harvest/harvest_big/round1/crops/0bff55647d1c2acd1caa8bf3/p000041-l0009.png | 0 word-final σ + 1 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['τῆς μεταςρέ']); greek_poly line rate 0.0035 |
| 16 | `πατέρων εἰς τὴν ῾Αγίαν Γραφὴν, εἰς τὴν ἑρμηνείαν ἐκκλησιαςι-` | docs/records/harvest/harvest_big/round1/crops/18ed614c7b7c25896c49680b/p000170-l0028.png | 0 word-final σ + 1 word-internal ς (of which 1 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ἐκκλησιαςι-']); greek_poly line rate 0.0035 |
| 17 | `διότι ἐν αὐτῇ ἐσαρκώθη ὁ Λόγος τοῦ Θεοῦ. Ὁ Νεςό-` | docs/records/harvest/harvest_big/round1/crops/53e3db8de066783d632e29c5/p000112-l0019.png | 0 word-final σ + 1 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['οῦ. Ὁ Νεςό-']); greek_poly line rate 0.0035 |
| 18 | `σων μερῶν· ἔπειτα ἔρχεταί τις πάλιν εἰς τὴν Εὐαγγελίςριαν.` | docs/records/harvest/harvest_big/round1/crops/460b94bc8e2c58a95074382b/p000026-l0020.png | 0 word-final σ + 1 word-internal ς (of which 1 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['Εὐαγγελίςρι']); greek_poly line rate 0.0035 |
| 19 | `Θαρρέω, ω, θαρσέω, θαρσ θαρρύνω καὶ θαρσύνω (ἔχω ἢ λαμα` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000091-l0046.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['σέω, θαρσ θ']); greek_poly line rate 0.0035 |
| 20 | `νοοῦσα καὶ ἦλθεν εἰς τὸν ναὸν τῆς Εὐαγγελισρίαςμετὰ δακρύων` | docs/records/harvest/harvest_big/round1/crops/460b94bc8e2c58a95074382b/p000023-l0008.png | 0 word-final σ + 1 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['γελισρίαςμε']); greek_poly line rate 0.0035 |

### spacing_apostrophe (1,338 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `μελ. κρεμάσω Π. Δ. Γενεσ. 40, 19, ἀορ. α. ἐκρέμασα ᾿Αριστοτ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000117-l0027.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 2 | `ὁρῶντες ἐθαύμαζον, ὅ,τι ἐποίουν, πρὶν Νίκαρχος ᾿Αρ-` | docs/records/harvest/harvest_big/round1/crops/c20219eff76f2fbc39f4c6fd/p000060-l0046.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 3 | `Ἐν ᾿Αθήναις, τὴν 28 Νοεμβρίου (10 Δεκεμβρίου) 1868.` | docs/records/harvest/harvest_big/round1/crops/6c82556081bbe4aada41e496/p000039-l0006.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 4 | `μετὰ δὲ αἰνέοντες ᾿Αθηναίους καὶ τὸ ἔργον αὐτῶν ἀπαλλάσ-` | docs/records/harvest/harvest_big/round1/crops/96bb7196d840fe7513c2ed43/p000030-l0027.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 5 | `Πασᾶ, καιρὸν μὴ χάνῃς ᾿ςτὸν κάμπον νὰ φανῆς·` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000021-l0003.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before lowercase': 1}; greek_poly line rate 0.0694 |
| 6 | `τῆς ᾿Αττικῆς, Μεγαρίδος καὶ τῆς ἐν τῷ Κορινθιακῷ κόλπῳ` | docs/records/harvest/harvest_big/round1/crops/eed91c3c88be77cac51e7629/p000094-l0015.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 7 | `Πρὸς τοὺς ἐν ᾿Αθήναις ἀντιπροσώπους τῆς Γαλλίας, τῆς Μεγάλης Βρετανίας καὶ τῆς ῾Ρωσσίας.` | docs/records/harvest/harvest_big/round1/crops/6c82556081bbe4aada41e496/p000050-l0005.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 8 | `Φλέσιας Παπαζούνης καὶ ὅλοι τοῦ κάτω ᾿Αχαγιὲ, ἀμέσως ἔσπευ-` | docs/records/harvest/harvest_big/round1/crops/8b206cd5e2c3714cf6bdff88/p000016-l0005.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 9 | `ἦν πολυάνδριον τῶν τοὺς Λακεδαιμονίους τρεψάντων ᾿Αρ-` | docs/records/harvest/harvest_big/round1/crops/eed91c3c88be77cac51e7629/p000158-l0026.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 10 | `ἐν ᾿Αμφίσση διεβιβάσθη εἰς Πελοπόννησον, ἀλλ᾽ ἐπὶ` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000023-l0011.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 11 | `πιεῖον καλούμενοι. Ἐπὶ τῆς ᾿Αχαϊκῆς συμμαχίας ἡ πόλις` | docs/records/harvest/harvest_big/round1/crops/eed91c3c88be77cac51e7629/p000172-l0014.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 12 | `σμα τοῦ Κλεινίου πατρὸς τοῦ ᾿Αράτου· 11 ἱερὸν τῆς ᾿Αθηνᾶς,` | docs/records/harvest/harvest_big/round1/crops/eed91c3c88be77cac51e7629/p000147-l0015.png | 0 standing alone + 2 word-initial before a letter {'U+1FBF psili before capital': 2}; greek_poly line rate 0.0694 |
| 13 | `*᾿Ανω (καταλαμβάνω, ἀκούω, αἰσθάνομαι), μτγν. καὶ ποιητ.` | docs/records/harvest/harvest_big/round1/crops/727f1e3f8d0a3a622943e9b1/p000012-l0021.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 14 | `χνος σῴζεται, ἀλλὰ παρέμεινε τὸ ὄνομα ᾿Αγριότικα.` | docs/records/harvest/harvest_big/round1/crops/6296ac8dc850e29e2fa2f0b1/p000082-l0029.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 15 | `λῆς ἦν Διονύσιος ὁ ᾿Αλεξανδρείας, διάδοχος αὐτοῦ ἐν τῇ σχολῇ ἀπὸ` | docs/records/harvest/harvest_big/round1/crops/9e60fbb6b1fc1da9f26b775e/p000175-l0005.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 16 | `Εὐρώπης, τῆς ᾿Ασίας καὶ τῆς ᾿Αφρικῆς, ἐκυριεύθη ὑπὸ` | docs/records/harvest/harvest_big/round1/crops/d8dfd78fb29485b6707ae96c/p000004-l0029.png | 0 standing alone + 2 word-initial before a letter {'U+1FBF psili before capital': 2}; greek_poly line rate 0.0694 |
| 17 | `ὕμν. Ἑρμ. 367, εὐκτ. ἐν-δείξαιτο Εὐρ. ᾿Αλκ. 154, ἀπαρ. ἀποδέξασθαι` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000055-l0092.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 18 | `χωρὶς τῶν ἔργων, κατὰ τὸν ᾿Απόστολον, νεκρά ἐστι·` | docs/records/harvest/harvest_big/round1/crops/cf2272f4329d987f840e81ab/p000007-l0061.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 19 | `μέρας. -Καλοὶ πλοῖεἰσιν εἰς Ἰταλίαν. - Οἱ ᾿Αθηναῖοι` | docs/records/harvest/harvest_big/round1/crops/c20219eff76f2fbc39f4c6fd/p000008-l0063.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |
| 20 | `ποίημαι Δημ.. 25, 80. Μέσ. παιδοποιοῦμαι ᾿Ανδοκ. 4, 23, μελ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000152-l0086.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0694 |

### line_end_not_sign (0 lines)

_none_

### dictionary_like (41 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `μάλωτος - ᾿Αποκτᾷ τὴν φιλίαν τοῦ Κοὺρὸ Πασᾶ` | docs/records/harvest/harvest_big/round1/crops/f07e2d5bdef7328dfb1671bf/p000030-l0012.png | headword + dash/colon at line start; greek_poly line rate 0.0017 |
| 2 | `Καπελάν – Γάμος τῆς Σαϊνίτζας – Στρατήγημα αὐτοῦ` | docs/records/harvest/harvest_big/round1/crops/f07e2d5bdef7328dfb1671bf/p000030-l0014.png | headword + dash/colon at line start; greek_poly line rate 0.0017 |
| 3 | `δια - σκεδάζεις (ἐκ ῥ. σκεδάζω) μτγν. Θεοδ. Στουδ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000177-l0044.png | headword + dash/colon at line start; greek_poly line rate 0.0017 |
| 4 | `ρεσιν, - τὸ ὄρος τοῦ Σινᾶ, οἱ Ἑβραῖοι καὶ ὁ Μωϋσῆς !–` | docs/records/harvest/harvest_big/round1/crops/0bff55647d1c2acd1caa8bf3/p000120-l0019.png | headword + dash/colon at line start; greek_poly line rate 0.0017 |
| 5 | `Πλήθω – Πλήσσω.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000164-l0002.png | headword + dash/colon at line start; greek_mono line rate 0.0119 |
| 6 | `Κρί - νω ὡς καὶ παρ᾿ ἡμῖν Θουκ. 5, 60, παρατ. ἔκρινον,` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000117-l0068.png | headword + dash/colon at line start; greek_poly line rate 0.0017 |
| 7 | `Λύσις: ᾿Αστασία - Αναστασία.` | docs/records/harvest/harvest_big/round1/crops/928e34aaaa78469aacd6c7ef/p000053-l0030.png | headword + dash/colon at line start; greek_mono line rate 0.0119 |
| 8 | `πολίτης: Χαρακμωβηνὸς καὶ ὁ ἐκ Χάρακος. Σημῖται δὲν` | docs/records/harvest/harvest_big/round1/crops/99c8dbb018ec2c87af3fdce9/p000022-l0025.png | headword + dash/colon at line start; greek_poly line rate 0.0017 |
| 9 | `Φορέω - ὦ (φέρω), παρτ. ἐφόρουν, μελ. φορήσω, ἀυρ. ἐφό-` | docs/records/harvest/harvest_big/round1/crops/727f1e3f8d0a3a622943e9b1/p000108-l0033.png | headword + dash/colon at line start; greek_poly line rate 0.0017 |
| 10 | `ἔλεγον : Θὰ δοκιμάσῃς ἐπὶ ὀκτὼ ἡμέρας τὴν` | docs/records/harvest/harvest_big/round1/crops/c194db932e54383910fe40a7/p000272-l0029.png | headword + dash/colon at line start; greek_poly line rate 0.0017 |
| 11 | `παροιμία: «᾿Ανάγυρον κινεῖν ». Ἡ πόλις, ὡς φαίνεται, ἦν ὠ-` | docs/records/harvest/harvest_big/round1/crops/eed91c3c88be77cac51e7629/p000133-l0014.png | headword + dash/colon at line start; greek_poly line rate 0.0017 |
| 12 | `μία: «᾿Αναγυράσιος δαίμων»· 3 τὸ «Νυμφαῖον » ὅ ἐστι σπή-` | docs/records/harvest/harvest_big/round1/crops/eed91c3c88be77cac51e7629/p000133-l0018.png | headword + dash/colon at line start; greek_poly line rate 0.0017 |
| 13 | `Φθέγγομαι – Φθίνω.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000201-l0055.png | headword + dash/colon at line start; greek_mono line rate 0.0119 |
| 14 | `E: Wagner, Cohnheim, Rindfleisch, Eberth, J. Arnold, Langhans,` | docs/records/harvest/harvest_big/round1/crops/f0acb2fc3dab2a9bb69f8726/p000026-l0025.png | headword + dash/colon at line start; latin line rate 0.0020 |
| 15 | `Συστήματος: Αὐτὴ ἡ Ἐκκλησία βασίζεται ἰδίᾳ ἐπὶ τῆς` | docs/records/harvest/harvest_big/round1/crops/bc780ca03714543a92331cd2/p000029-l0005.png | headword + dash/colon at line start; greek_poly line rate 0.0017 |
| 16 | `ἀρεταί : πίστις, ἐλπὶς καὶ ἀγάπη. Οἱ δὲ κα- τηχούμενοι ἐν` | docs/records/harvest/harvest_big/round1/crops/cf2272f4329d987f840e81ab/p000007-l0030.png | headword + dash/colon at line start; greek_poly line rate 0.0017 |
| 17 | `Τελευτάω - Τέλλω.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000189-l0002.png | headword + dash/colon at line start; greek_mono line rate 0.0119 |
| 18 | `πατέρες - Ἐξῆρχε δὲ τῆς αἱρέσεως τῶν εἰκονομάχων` | docs/records/harvest/harvest_big/round1/crops/cf2272f4329d987f840e81ab/p000039-l0034.png | headword + dash/colon at line start; greek_poly line rate 0.0017 |
| 19 | `Ὀρχέομαι - οῦμαι (χορεύω) μεσ. παρτ. ὠρχούμην, μελ. ὀρ-` | docs/records/harvest/harvest_big/round1/crops/727f1e3f8d0a3a622943e9b1/p000077-l0028.png | headword + dash/colon at line start; greek_poly line rate 0.0017 |
| 20 | `Φιλέω - ὦ (ἀγαπῶ, εὐνοῶ, φιλικῶς ὑποδέχομαι), παρτ. ἐφί-` | docs/records/harvest/harvest_big/round1/crops/727f1e3f8d0a3a622943e9b1/p000108-l0006.png | headword + dash/colon at line start; greek_poly line rate 0.0017 |

### digitisation_stamp (69 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `ΠΑΝΕΠΙΣΤΗΜΙ` | docs/records/harvest/harvest_big/round1/crops/96bb7196d840fe7513c2ed43/p000038-l0063.png | label is a library/digitiser stamp; box 62x157px at y_rel 0.913 |
| 2 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000105-l0034.png | label is a library/digitiser stamp; box 191x243px at y_rel 0.919 |
| 3 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000081-l0034.png | label is a library/digitiser stamp; box 192x245px at y_rel 0.918 |
| 4 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/ffe26907d1e3e9c1f75337e2/p000285-l0001.png | label is a library/digitiser stamp; box 198x242px at y_rel 0.919 |
| 5 | `ΠΑΝΕΠΙΣΤΗΜΙΟ` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000020-l0036.png | label is a library/digitiser stamp; box 57x169px at y_rel 0.908 |
| 6 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000023-l0032.png | label is a library/digitiser stamp; box 194x243px at y_rel 0.927 |
| 7 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000026-l0001.png | label is a library/digitiser stamp; box 195x243px at y_rel 0.927 |
| 8 | `ΠΑΝΕΠΙΣΤΗΜΙΟ` | docs/records/harvest/harvest_big/round1/crops/f07e2d5bdef7328dfb1671bf/p000070-l0035.png | label is a library/digitiser stamp; box 57x168px at y_rel 0.92 |
| 9 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/ffe26907d1e3e9c1f75337e2/p000247-l0001.png | label is a library/digitiser stamp; box 190x241px at y_rel 0.92 |
| 10 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗ` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000037-l0033.png | label is a library/digitiser stamp; box 187x243px at y_rel 0.927 |
| 11 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000040-l0031.png | label is a library/digitiser stamp; box 195x242px at y_rel 0.927 |
| 12 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗ` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000031-l0001.png | label is a library/digitiser stamp; box 185x242px at y_rel 0.919 |
| 13 | `ΠΑΝΕΠΙΣΤΗΜΙΟ` | docs/records/harvest/harvest_big/round1/crops/f07e2d5bdef7328dfb1671bf/p000062-l0033.png | label is a library/digitiser stamp; box 58x171px at y_rel 0.92 |
| 14 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000056-l0001.png | label is a library/digitiser stamp; box 195x243px at y_rel 0.927 |
| 15 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/ffe26907d1e3e9c1f75337e2/p000026-l0001.png | label is a library/digitiser stamp; box 194x243px at y_rel 0.919 |
| 16 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/ffe26907d1e3e9c1f75337e2/p000045-l0001.png | label is a library/digitiser stamp; box 193x243px at y_rel 0.919 |
| 17 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/ffe26907d1e3e9c1f75337e2/p000064-l0034.png | label is a library/digitiser stamp; box 194x242px at y_rel 0.919 |
| 18 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000129-l0001.png | label is a library/digitiser stamp; box 192x241px at y_rel 0.919 |
| 19 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗ` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000047-l0001.png | label is a library/digitiser stamp; box 179x243px at y_rel 0.918 |
| 20 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗ` | docs/records/harvest/harvest_big/round1/crops/f07e2d5bdef7328dfb1671bf/p000013-l0035.png | label is a library/digitiser stamp; box 183x245px at y_rel 0.929 |


## 6. What I judged and why (detector definitions and limits)

**Reference groups.** Line flags compare a line with all pool lines of its own `script_class` (whole pool, all waves). Book hard
flags and z-scores compare a book with books of the same majority script class that have >= 30 lines; class-quantile hard flags,
verse-like and z-scores are only evaluated when that population has >= 5 books (greek_latin_cs has 2 majority books, so it is
not evaluated). z = (book median − mean of same-class book medians) / sd; I also give z of each flag share, because the medians
of sparse features (digit share, symbol share) are 0 for nearly every book and their z is degenerate. `N_books` is stored in
every book row (`z_reference`).

**Thresholds (all quantiles of the reference group, no hand-set cut-offs except the spec's 30 % and 8 %).**
- *digit_heavy*: digit share above the class p90 **of lines that contain any digit** (plain p95 over all lines is 0 for every
  class, since most lines have no digits). Same idea for punctuation (p99 of punctuated lines) and symbols (p99 of symbol-bearing
  lines). Shares are over visible characters (whitespace and combining marks excluded). Greek spacing accents (U+0384, U+1FBF …)
  are Unicode "symbols" but are counted as their own feature, not in symbol share.
- *word_length_outlier*: mean word length outside the class [p1, p99] computed over lines with >= 3 words; 1–2-word lines have
  degenerate means and are not flagged (constant 3 is my choice).
- *long_token*: longest whitespace token above the class p99. In Greek this is mostly genuine long words
  (`Κωνσταντινουπόλεως`); merged words show up here too but the flag is not specific to them.
- *running_title_or_page_number*: spec rule — box in the top or bottom 8 % of the **page image height** (read from the PNG header;
  all 5,967 pages had an image, no fallback needed), no lowercase letters (all-caps or digits), and "short" = at most the class
  median length (p25 cut off real headers like `ΣΥΝΕΔΡΙΑΣΗ Π' – 21 ΦΕΒΡΟΥΑΡΙΟΥ 1996`). Limit: page images include scan margins, so
  a header printed at 9–10 % of the scan is missed; mixed-case running titles (`Κεφ. Γ'. Ἐσωτ. ὀργαν.`) are missed by design.
  Page numbers themselves are mostly not admitted (records mark them `counted: false`), so this flag is mostly running titles.
- *final_sigma_error*: σ at a word end (next char not a letter/combining mark, not a hyphen), excluding the single-letter
  abbreviation `σ.` and σ before a period (possible abbreviation such as `Ἰησ.`; counted separately as `sigma_end_period`), plus ς
  followed by a letter. Not counted as errors: ς at a compound boundary in 19th-c. orthography (prefix ends in προ/ει/δυ or is
  ὡ/ὁ/ὁπω/ἐ/καθω/οὑτω/οἱα/ὁποια…, or the rest starts δηποτ/περ/τις/τιν…) and aphaeresis `᾿ς`. The στ-ligature sub-count checks
  whether the same word with στ instead of ς occurs in the pool (exact word match; line-end fragments like `ἐκκλησιαςι-` are only
  caught when the fragment itself is attested). Book hard flag: rate per Greek word above the class p95 of books with >= 100 Greek
  words AND >= 2 occurrences (a single error is listed under "below support", not hard-flagged).
- *spacing_apostrophe*: U+1FBF, U+1FBD, U+0384, U+2019 standing alone as a token, or word-initially directly before a letter.
  Elision/keraia after a letter (`ἀλλ᾿`, `Α΄`) is normal usage and not flagged. Almost all hits are `᾿` + capital = breathing on a
  capital written as a separate character (see finding 1); a few are `’ς`/`᾿ς` aphaeresis, which is legitimate.
- *dictionary_like*: one headword (no sentence-final period), optional comma, then a dash or a colon and more text. It also fires on
  speaker labels in parliament minutes (`ΠΡΟΕΔΡΟΣ:`), dialogue dashes after a broken word (`νον - ἐνῷ`) and `word: text` in prose;
  it is a style descriptor, not an error flag. URLs are excluded.
- *numeric_table*: >= 3 consecutive numeric tokens. In practice it catches classical citation strings (`Xen. An. 6. 1, 21`) far
  more than tables; real tables are rare in the admitted pool (admission already removed most).
- *bibliographic*: year in parentheses, `pp.`, `Bd.`, `vol.`, `σ.` + number (spec list only; `σελ.`, `τόμ.` not included).
- *repeated_run*: >= 4 identical non-space characters; almost all are ellipses/leaders `....` (table-of-contents leaders in
  theses, vote lists in vouli). Leader dots are hard to count visually, so these labels are higher risk.
- *digitisation_stamp* (added, not in the spec): whole label = `ΠΑΝΕΠΙΣΤΗΜΙ…` (+ `ΚΡ…`), `Digitized by Google` or `ΒΙΒΛΙΟΘΗΚΗ`.
  The University of Crete seal is curved text over a logo; it is not book text.
- *line_end_not_sign*: label ending in `¬` (text-layer hyphenation artefact). Zero in this pool — the Google reads carry no text
  layer artefacts of that kind.
- *verse-like book* (informational): share of capital-initial lines above the class p95 of books AND median line length below the
  class median of book medians. It also catches lists of names (vouli vote lists, thesis front matter), not only verse.
- *all_caps*: a line whose cased letters are all uppercase (>= 2). It is not an error per line; the book hard flag is the book's
  share above the class p95. Note that all-caps headings carry no breathings or accents in the print, so in polytonic books many all-caps
  lines are classed `greek_mono` (43 % of round1 greek_mono lines are all-caps); per-class rates must be read with that in mind.

**Things I did not judge.** Whether a flagged label is wrong: only the crop can tell. Digit-heavy, all-caps, dictionary-like,
numeric-table and bibliographic flags describe content type, not label quality. The label-quality signals in this aspect are
final_sigma_error (especially the στ sub-count), spacing_apostrophe (encoding inconsistency), digitisation_stamp and repeated_run.

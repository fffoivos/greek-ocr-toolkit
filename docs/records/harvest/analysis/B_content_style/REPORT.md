# Aspect B — content and style

Input: `docs/records/harvest/collection/admitted_all.jsonl`. Lines processed: **293,439**; books (source, book_key): **557**.

Page height for the running-title detector: {'png_header': 5967} (`png_header` = height read from the page PNG header via the image path in the wave's records.jsonl; `max_y1_records` = fallback, not needed if absent).

Script: `docs/records/harvest/analysis/B_content_style/analysis_B.py` (re-runnable; `--limit N --out <subdir>` for tests).

## 0. Key findings (numbers from this run)

1. **Breathing/accent on a capital is encoded two ways.** 9,789 lines write a spacing mark (mostly U+1FBF ᾿) followed by a bare capital (`᾿Αθῆναι`) instead of the precomposed capital (`Ἀθῆναι`); per wave, spacing-form / all breathing-capitals: mixed 1,201/4,356 (28%); openarchives 2/57 (4%); parliament 1,494/10,325 (14%); round1 4,154/15,183 (27%); round2 1,770/5,771 (31%); vouli 1,181/5,298 (22%); wikisource 491/1,976 (25%). 359 books use BOTH encodings, so this is a label-normalisation inconsistency (Google output), not a property of the print: the same glyph gets two different targets.
2. **Final-sigma errors are rare but systematic in 19th-c. type.** 452 lines (0.15%); occurrences: word-final σ 245, word-internal ς 215, of which 100 have the στ-spelling attested elsewhere in the pool — the στ ligature (ϛ-like glyph) read as ς (`μέγιςος`, `Πανεπιςημίου`, `καταςροφὴν`). A further 290 compound-boundary ς (`προςάγω`, `ὥςτε`, `ὁποιοςδήποτε`, aphaeresis `᾿ς`) follow the print's orthography and are not counted.
3. **Library stamp admitted as text.** 83 lines are digitisation/ownership marks, not book text: mostly the University of Crete seal on Anemi scans (`ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ`, partial `ΠΑΝΕΠΙΣΤΗΜΙ…`; curved lettering over a logo in a ~190×240 px box at ~92 % of the page height), a few rubber library stamps (`ΒΙΒΛΙΟΘΗΚΗ`) and `Digitized by Google` footers on Wikisource scans.
4. **No book exceeds the 30 % spec limits** for digit-heavy or running-title lines (max digit-heavy share 15.0% in openarchives_mixed_hellanicus 9cd3290f; max running-title share 8.0% in openarchives_mixed_anaktisis 732cfbe1). Running titles and session headers are 0.31% of lines (908). The largest single book is archive_b28038630 4c207e1e 9,788 lines (3.3% of the pool); archive_AA9613308335D0B014B 9a32fb66 2,314 lines (0.8% of the pool); parliament_proceedings_1975_2000 f74236d5 1,633 lines (0.6% of the pool) — the first is the Liddell–Scott Greek–English lexicon (visible in its lines); its citation lines dominate the latin/greek_latin_cs numeric-table and digit-heavy flags.

## 1. Feature distributions per wave × script class

Shares are per line over visible characters (whitespace and combining marks excluded). Columns: median / p90 / p99 (mean for shares in brackets).

| wave | class | n | digit_share | punct_share | symbol_share | upper_share | n_tokens | mean_word_len | longest_token | n_chars |
|---|---|---:|---|---|---|---|---|---|---|---|
| cyrillic | cyrillic | 13,108 | 0.000 / 0.083 / 0.175 (0.018) | 0.047 / 0.136 / 0.217 (0.062) | 0.000 / 0.000 / 0.000 (0.000) | 0.02 / 0.10 / 0.31 (0.040) | 8 / 11 / 15 | 5.50 / 7.62 / 10.75 | 10 / 14 / 19 | 54 / 72 / 83 |
| cyrillic | latin | 575 | 0.000 / 0.116 / 0.195 (0.028) | 0.104 / 0.192 / 0.250 (0.106) | 0.000 / 0.000 / 0.019 (0.000) | 0.08 / 0.16 / 1.00 (0.091) | 4 / 10 / 12 | 6.00 / 9.50 / 13.00 | 11 / 14 / 18 | 28 / 63 / 77 |
| mixed | greek_latin_cs | 3,979 | 0.034 / 0.121 / 0.170 (0.046) | 0.125 / 0.192 / 0.250 (0.121) | 0.000 / 0.018 / 0.059 (0.004) | 0.05 / 0.13 / 0.55 (0.072) | 10 / 14 / 18 | 4.78 / 6.50 / 9.50 | 10 / 14 / 19 | 65 / 73 / 91 |
| mixed | greek_mono | 2,531 | 0.000 / 0.065 / 0.172 (0.015) | 0.032 / 0.111 / 0.214 (0.046) | 0.000 / 0.000 / 0.053 (0.002) | 0.02 / 1.00 / 1.00 (0.159) | 6 / 13 / 16 | 6.25 / 10.00 / 13.00 | 11 / 14 / 19 | 45 / 81 / 91 |
| mixed | greek_poly | 16,276 | 0.000 / 0.000 / 0.120 (0.005) | 0.036 / 0.083 / 0.182 (0.041) | 0.000 / 0.000 / 0.000 (0.000) | 0.02 / 0.06 / 0.18 (0.023) | 9 / 11 / 13 | 5.20 / 6.67 / 9.00 | 10 / 13 / 16 | 55 / 63 / 72 |
| mixed | latin | 10,326 | 0.036 / 0.109 / 0.169 (0.044) | 0.128 / 0.197 / 0.250 (0.125) | 0.000 / 0.000 / 0.074 (0.002) | 0.06 / 0.16 / 0.54 (0.082) | 11 / 14 / 19 | 4.60 / 7.00 / 25.50 | 10 / 15 / 37 | 66 / 76 / 116 |
| openarchives | greek_latin_cs | 2,254 | 0.000 / 0.087 / 0.174 (0.025) | 0.036 / 0.095 / 0.159 (0.045) | 0.000 / 0.000 / 0.029 (0.001) | 0.05 / 0.14 / 0.74 (0.074) | 11 / 14 / 16 | 5.77 / 7.37 / 10.00 | 12 / 15 / 20 | 75 / 87 / 97 |
| openarchives | greek_mono | 22,126 | 0.000 / 0.038 / 0.147 (0.010) | 0.016 / 0.061 / 0.133 (0.026) | 0.000 / 0.000 / 0.000 (0.000) | 0.01 / 0.07 / 1.00 (0.036) | 10 / 13 / 16 | 6.08 / 8.00 / 12.00 | 12 / 15 / 19 | 74 / 85 / 96 |
| openarchives | greek_poly | 236 | 0.000 / 0.093 / 0.195 (0.026) | 0.027 / 0.076 / 0.174 (0.037) | 0.000 / 0.000 / 0.012 (0.000) | 0.03 / 0.07 / 0.20 (0.029) | 7 / 13 / 17 | 6.00 / 8.00 / 10.00 | 11 / 13 / 18 | 46 / 90 / 112 |
| openarchives | latin | 988 | 0.000 / 0.105 / 0.191 (0.034) | 0.071 / 0.164 / 0.243 (0.078) | 0.000 / 0.000 / 0.067 (0.002) | 0.11 / 0.22 / 1.00 (0.130) | 7 / 14 / 17 | 6.26 / 12.00 / 63.00 | 11 / 22 / 82 | 65 / 89 / 103 |
| parliament | greek_latin_cs | 209 | 0.000 / 0.082 / 0.200 (0.018) | 0.044 / 0.097 / 0.172 (0.048) | 0.000 / 0.000 / 0.015 (0.000) | 0.18 / 0.40 / 0.71 (0.217) | 8 / 10 / 12 | 5.12 / 7.00 / 9.00 | 10 / 13 / 17 | 50 / 57 / 77 |
| parliament | greek_mono | 46,088 | 0.000 / 0.022 / 0.200 (0.010) | 0.036 / 0.083 / 0.143 (0.039) | 0.000 / 0.000 / 0.000 (0.000) | 0.02 / 0.17 / 1.00 (0.080) | 8 / 11 / 13 | 5.33 / 7.12 / 10.00 | 11 / 13 / 16 | 54 / 60 / 68 |
| parliament | greek_poly | 37,988 | 0.000 / 0.021 / 0.184 (0.009) | 0.027 / 0.071 / 0.132 (0.036) | 0.000 / 0.000 / 0.000 (0.000) | 0.02 / 0.09 / 0.61 (0.047) | 8 / 10 / 12 | 5.25 / 6.86 / 8.75 | 11 / 14 / 17 | 54 / 58 / 61 |
| parliament | latin | 756 | 0.000 / 0.000 / 0.125 (0.006) | 0.024 / 0.091 / 0.191 (0.039) | 0.000 / 0.000 / 0.000 (0.000) | 0.02 / 0.21 / 1.00 (0.121) | 7 / 11 / 16 | 5.50 / 8.00 / 13.25 | 11 / 14 / 26 | 50 / 64 / 103 |
| round1 | greek_latin_cs | 1,026 | 0.000 / 0.070 / 0.155 (0.016) | 0.057 / 0.137 / 0.257 (0.068) | 0.000 / 0.000 / 0.029 (0.001) | 0.04 / 0.10 / 0.27 (0.048) | 10 / 13 / 17 | 5.19 / 6.86 / 9.00 | 11 / 14 / 20 | 61 / 75 / 101 |
| round1 | greek_mono | 1,707 | 0.000 / 0.032 / 0.176 (0.011) | 0.062 / 0.148 / 0.231 (0.064) | 0.000 / 0.000 / 0.000 (0.000) | 0.14 / 1.00 / 1.00 (0.457) | 2 / 6 / 10 | 7.00 / 11.00 / 13.97 | 10 / 13 / 17 | 19 / 41 / 67 |
| round1 | greek_poly | 57,970 | 0.000 / 0.000 / 0.125 (0.006) | 0.034 / 0.083 / 0.180 (0.041) | 0.000 / 0.000 / 0.000 (0.000) | 0.02 / 0.07 / 0.18 (0.028) | 9 / 11 / 15 | 5.12 / 6.60 / 8.67 | 10 / 13 / 16 | 53 / 66 / 86 |
| round1 | latin | 1,162 | 0.000 / 0.077 / 0.168 (0.017) | 0.065 / 0.166 / 0.226 (0.080) | 0.000 / 0.000 / 0.021 (0.001) | 0.06 / 0.14 / 0.59 (0.075) | 8 / 11 / 14 | 5.11 / 7.00 / 10.69 | 10 / 13 / 17 | 51 / 67 / 80 |
| round2 | greek_latin_cs | 416 | 0.000 / 0.072 / 0.146 (0.019) | 0.055 / 0.112 / 0.189 (0.060) | 0.000 / 0.000 / 0.033 (0.001) | 0.04 / 0.11 / 0.27 (0.058) | 9 / 12 / 14 | 5.00 / 6.43 / 8.90 | 10 / 13 / 18 | 57 / 72 / 83 |
| round2 | greek_mono | 719 | 0.000 / 0.000 / 0.124 (0.006) | 0.062 / 0.133 / 0.237 (0.059) | 0.000 / 0.000 / 0.000 (0.000) | 0.21 / 1.00 / 1.00 (0.512) | 2 / 4 / 7 | 6.50 / 11.00 / 15.00 | 10 / 13 / 17 | 18 / 30 / 48 |
| round2 | greek_poly | 22,311 | 0.000 / 0.000 / 0.143 (0.007) | 0.031 / 0.075 / 0.146 (0.038) | 0.000 / 0.000 / 0.000 (0.000) | 0.02 / 0.07 / 0.14 (0.025) | 8 / 11 / 15 | 5.11 / 6.57 / 8.60 | 10 / 13 / 16 | 52 / 65 / 97 |
| round2 | latin | 970 | 0.000 / 0.023 / 0.150 (0.009) | 0.043 / 0.093 / 0.149 (0.050) | 0.000 / 0.000 / 0.045 (0.002) | 0.03 / 0.11 / 0.24 (0.050) | 9 / 12 / 14 | 5.22 / 7.00 / 11.12 | 10 / 13 / 16 | 56 / 70 / 76 |
| vouli | greek_latin_cs | 54 | 0.000 / 0.000 / 0.052 (0.003) | 0.038 / 0.074 / 0.162 (0.045) | 0.000 / 0.010 / 0.012 (0.002) | 0.02 / 0.10 / 0.48 (0.049) | 13 / 19 / 21 | 5.47 / 6.70 / 7.68 | 12 / 15 / 16 | 86 / 116 / 136 |
| vouli | greek_mono | 2,439 | 0.000 / 0.000 / 0.143 (0.004) | 0.083 / 0.175 / 0.250 (0.091) | 0.000 / 0.000 / 0.000 (0.000) | 0.16 / 1.00 / 1.00 (0.258) | 2 / 4 / 7 | 6.50 / 10.00 / 12.00 | 11 / 14 / 16 | 17 / 25 / 51 |
| vouli | greek_poly | 34,542 | 0.000 / 0.022 / 0.174 (0.009) | 0.027 / 0.064 / 0.133 (0.034) | 0.000 / 0.000 / 0.000 (0.000) | 0.01 / 0.07 / 0.31 (0.029) | 9 / 16 / 21 | 5.38 / 6.75 / 9.00 | 11 / 14 / 16 | 56 / 109 / 121 |
| vouli | latin | 327 | 0.000 / 0.093 / 0.227 (0.019) | 0.042 / 0.083 / 0.143 (0.043) | 0.000 / 0.000 / 0.024 (0.001) | 0.03 / 0.14 / 0.94 (0.084) | 8 / 10 / 15 | 5.00 / 6.58 / 8.57 | 10 / 13 / 15 | 49 / 54 / 95 |
| wikisource | cyrillic | 3,118 | 0.000 / 0.000 / 0.128 (0.004) | 0.048 / 0.102 / 0.179 (0.055) | 0.000 / 0.000 / 0.000 (0.000) | 0.02 / 0.07 / 0.16 (0.029) | 7 / 10 / 12 | 5.44 / 7.33 / 10.00 | 10 / 14 / 17 | 48 / 61 / 66 |
| wikisource | greek_latin_cs | 112 | 0.000 / 0.114 / 0.206 (0.034) | 0.059 / 0.123 / 0.166 (0.064) | 0.000 / 0.000 / 0.000 (0.000) | 0.05 / 0.11 / 0.20 (0.053) | 10 / 13 / 15 | 5.00 / 6.28 / 8.22 | 10 / 13 / 15 | 58 / 74 / 76 |
| wikisource | greek_mono | 243 | 0.000 / 0.000 / 0.172 (0.005) | 0.000 / 0.124 / 0.227 (0.044) | 0.000 / 0.000 / 0.000 (0.000) | 1.00 / 1.00 / 1.00 (0.569) | 2 / 5 / 7 | 7.00 / 10.00 / 12.29 | 10 / 13 / 16 | 19 / 38 / 55 |
| wikisource | greek_poly | 8,786 | 0.000 / 0.000 / 0.091 (0.003) | 0.029 / 0.072 / 0.146 (0.037) | 0.000 / 0.000 / 0.000 (0.000) | 0.02 / 0.06 / 0.12 (0.022) | 7 / 10 / 13 | 5.14 / 6.67 / 8.50 | 10 / 13 / 16 | 44 / 56 / 74 |
| wikisource | latin | 97 | 0.000 / 0.145 / 0.208 (0.044) | 0.075 / 0.139 / 0.178 (0.069) | 0.000 / 0.000 / 0.000 (0.000) | 0.09 / 1.00 / 1.00 (0.229) | 8 / 12 / 16 | 5.36 / 7.08 / 9.07 | 9 / 14 / 20 | 48 / 73 / 77 |

Pattern rates per wave × class (share of lines):

| wave | class | n | is_all_caps | cap_initial | hyphen_end | numeric_table | biblio | rep_run | dictionary_like | top_bottom | sigma_err lines | compound-ς lines (not errors) | spacing-apos lines | of which mark before a capital |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cyrillic | cyrillic | 13,108 | 0.0050 | 0.2760 | 0.2516 | 0.0005 | 0.0014 | 0.0005 | 0.0073 | 0.0198 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| cyrillic | latin | 575 | 0.0122 | 0.5026 | 0.1461 | 0.0000 | 0.0052 | 0.0017 | 0.0209 | 0.0365 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| mixed | greek_latin_cs | 3,979 | 0.0023 | 0.2478 | 0.0824 | 0.0493 | 0.0028 | 0.0005 | 0.0096 | 0.0535 | 0.0020 | 0.0000 | 0.0153 | 0.0153 |
| mixed | greek_mono | 2,531 | 0.1181 | 0.4698 | 0.0387 | 0.0012 | 0.0024 | 0.0008 | 0.0245 | 0.0770 | 0.0000 | 0.0000 | 0.0099 | 0.0095 |
| mixed | greek_poly | 16,276 | 0.0000 | 0.1866 | 0.2410 | 0.0004 | 0.0009 | 0.0012 | 0.0049 | 0.0263 | 0.0015 | 0.0008 | 0.0641 | 0.0627 |
| mixed | latin | 10,326 | 0.0081 | 0.2675 | 0.0575 | 0.0515 | 0.0302 | 0.0012 | 0.0099 | 0.0473 | 0.0005 | 0.0001 | 0.0035 | 0.0032 |
| openarchives | greek_latin_cs | 2,254 | 0.0093 | 0.3980 | 0.0142 | 0.0018 | 0.0288 | 0.0004 | 0.0071 | 0.0106 | 0.0004 | 0.0000 | 0.0000 | 0.0000 |
| openarchives | greek_mono | 22,126 | 0.0140 | 0.2942 | 0.0074 | 0.0007 | 0.0042 | 0.0005 | 0.0048 | 0.0230 | 0.0001 | 0.0000 | 0.0004 | 0.0000 |
| openarchives | greek_poly | 236 | 0.0000 | 0.4025 | 0.1398 | 0.0042 | 0.0042 | 0.0000 | 0.0042 | 0.0678 | 0.0000 | 0.0000 | 0.0127 | 0.0085 |
| openarchives | latin | 988 | 0.0162 | 0.7034 | 0.0385 | 0.0040 | 0.1457 | 0.0000 | 0.0425 | 0.0040 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| parliament | greek_latin_cs | 209 | 0.0096 | 0.4689 | 0.2297 | 0.0000 | 0.0000 | 0.0000 | 0.0096 | 0.0335 | 0.0000 | 0.0000 | 0.0144 | 0.0144 |
| parliament | greek_mono | 46,088 | 0.0209 | 0.2834 | 0.1833 | 0.0001 | 0.0004 | 0.0003 | 0.0046 | 0.0512 | 0.0005 | 0.0000 | 0.0024 | 0.0023 |
| parliament | greek_poly | 37,988 | 0.0000 | 0.2272 | 0.2656 | 0.0002 | 0.0000 | 0.0006 | 0.0039 | 0.0127 | 0.0004 | 0.0000 | 0.0352 | 0.0351 |
| parliament | latin | 756 | 0.0661 | 0.4220 | 0.1429 | 0.0000 | 0.0000 | 0.0000 | 0.0040 | 0.0198 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| round1 | greek_latin_cs | 1,026 | 0.0000 | 0.2739 | 0.2593 | 0.0049 | 0.0234 | 0.0010 | 0.0019 | 0.0117 | 0.0019 | 0.0010 | 0.0673 | 0.0673 |
| round1 | greek_mono | 1,707 | 0.4066 | 0.7434 | 0.0393 | 0.0023 | 0.0000 | 0.0012 | 0.0146 | 0.1605 | 0.0006 | 0.0000 | 0.0568 | 0.0557 |
| round1 | greek_poly | 57,970 | 0.0000 | 0.2462 | 0.2128 | 0.0011 | 0.0012 | 0.0015 | 0.0031 | 0.0152 | 0.0028 | 0.0030 | 0.0685 | 0.0650 |
| round1 | latin | 1,162 | 0.0095 | 0.4750 | 0.1575 | 0.0034 | 0.0284 | 0.0034 | 0.0034 | 0.0284 | 0.0000 | 0.0009 | 0.0120 | 0.0120 |
| round2 | greek_latin_cs | 416 | 0.0048 | 0.3341 | 0.2356 | 0.0000 | 0.0120 | 0.0000 | 0.0072 | 0.0192 | 0.0000 | 0.0048 | 0.0553 | 0.0529 |
| round2 | greek_mono | 719 | 0.4631 | 0.7677 | 0.0209 | 0.0000 | 0.0000 | 0.0000 | 0.0042 | 0.1460 | 0.0000 | 0.0000 | 0.0348 | 0.0320 |
| round2 | greek_poly | 22,311 | 0.0000 | 0.2379 | 0.2133 | 0.0001 | 0.0009 | 0.0019 | 0.0014 | 0.0173 | 0.0041 | 0.0022 | 0.0764 | 0.0719 |
| round2 | latin | 970 | 0.0072 | 0.2691 | 0.1649 | 0.0000 | 0.0052 | 0.0021 | 0.0010 | 0.0113 | 0.0000 | 0.0000 | 0.0021 | 0.0021 |
| vouli | greek_latin_cs | 54 | 0.0000 | 0.1852 | 0.1667 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1481 | 0.0000 | 0.0185 | 0.0370 | 0.0370 |
| vouli | greek_mono | 2,439 | 0.1169 | 0.9086 | 0.0152 | 0.0000 | 0.0000 | 0.0152 | 0.0000 | 0.0652 | 0.0008 | 0.0000 | 0.0476 | 0.0476 |
| vouli | greek_poly | 34,542 | 0.0000 | 0.2108 | 0.2108 | 0.0008 | 0.0001 | 0.0012 | 0.0003 | 0.0572 | 0.0028 | 0.0006 | 0.0297 | 0.0296 |
| vouli | latin | 327 | 0.0061 | 0.3456 | 0.2324 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0398 | 0.0000 | 0.0000 | 0.0031 | 0.0031 |
| wikisource | cyrillic | 3,118 | 0.0045 | 0.2938 | 0.2733 | 0.0000 | 0.0000 | 0.0003 | 0.0115 | 0.0324 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| wikisource | greek_latin_cs | 112 | 0.0000 | 0.2857 | 0.2054 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0268 | 0.0000 | 0.0000 | 0.0625 | 0.0625 |
| wikisource | greek_mono | 243 | 0.5432 | 0.7613 | 0.0329 | 0.0000 | 0.0000 | 0.0041 | 0.0000 | 0.0988 | 0.0000 | 0.0000 | 0.0288 | 0.0288 |
| wikisource | greek_poly | 8,786 | 0.0000 | 0.2131 | 0.2444 | 0.0000 | 0.0000 | 0.0007 | 0.0013 | 0.0209 | 0.0027 | 0.0017 | 0.0529 | 0.0511 |
| wikisource | latin | 97 | 0.1649 | 0.5155 | 0.1237 | 0.0000 | 0.0000 | 0.0000 | 0.0206 | 0.2680 | 0.0000 | 0.0000 | 0.0103 | 0.0103 |

Bibliographic pattern kinds (line counts): {'year_in_parens': 622, 'σ.+number': 177, 'vol.': 34, 'Bd.': 2, 'pp.': 29}. Line-end hyphen kinds: {'-': 55609, 'U+2010': 4}.

## 2. Line-flag thresholds (per script class, whole pool as reference)

| class | n lines | digit_heavy > (p90 of digit-bearing lines) | punct_heavy > (p99 of punctuated) | symbol_heavy > (p99 of symbol-bearing) | long_token > p99 | word length outside [p1, p99] (lines >= 3 words) | short (running title) <= p50 chars |
|---|---:|---:|---:|---:|---:|---|---:|
| cyrillic | 16,226 | 0.143 | 0.217 | 0.054 | 18 | [3.25, 9.38] | 53 |
| greek_latin_cs | 8,050 | 0.136 | 0.240 | 0.083 | 20 | [3.08, 9.14] | 66 |
| greek_mono | 75,853 | 0.174 | 0.176 | 0.127 | 18 | [3.58, 9.33] | 55 |
| greek_poly | 178,109 | 0.158 | 0.167 | 0.075 | 16 | [3.50, 8.33] | 54 |
| latin | 15,201 | 0.130 | 0.246 | 0.177 | 39 | [3.00, 10.00] | 61 |

## 3. Flag rates per wave × class (share of lines carrying the flag)

| wave | class | n | digit_heavy | punct_heavy | symbol_heavy | all_caps | long_token | word_length_outlier | repeated_run | numeric_table | bibliographic | running_title_or_page_number | final_sigma_error | spacing_apostrophe | line_end_not_sign | dictionary_like | digitisation_stamp |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cyrillic | cyrillic | 13,108 | 0.0205 | 0.0108 | 0.0001 | 0.0050 | 0.0111 | 0.0185 | 0.0005 | 0.0005 | 0.0014 | 0.0024 | 0.0000 | 0.0000 | 0.0000 | 0.0073 | 0.0000 |
| cyrillic | latin | 575 | 0.0765 | 0.0122 | 0.0000 | 0.0122 | 0.0000 | 0.0087 | 0.0017 | 0.0000 | 0.0052 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0209 | 0.0000 |
| mixed | greek_latin_cs | 3,979 | 0.0613 | 0.0163 | 0.0010 | 0.0023 | 0.0090 | 0.0246 | 0.0005 | 0.0493 | 0.0028 | 0.0008 | 0.0020 | 0.0153 | 0.0000 | 0.0096 | 0.0000 |
| mixed | greek_mono | 2,531 | 0.0099 | 0.0249 | 0.0004 | 0.1181 | 0.0134 | 0.0399 | 0.0008 | 0.0012 | 0.0024 | 0.0415 | 0.0000 | 0.0099 | 0.0000 | 0.0245 | 0.0000 |
| mixed | greek_poly | 16,276 | 0.0049 | 0.0135 | 0.0000 | 0.0000 | 0.0058 | 0.0209 | 0.0012 | 0.0004 | 0.0009 | 0.0000 | 0.0015 | 0.0641 | 0.0000 | 0.0049 | 0.0000 |
| mixed | latin | 10,326 | 0.0488 | 0.0114 | 0.0007 | 0.0081 | 0.0081 | 0.0197 | 0.0012 | 0.0515 | 0.0302 | 0.0000 | 0.0005 | 0.0035 | 0.0000 | 0.0099 | 0.0000 |
| openarchives | greek_latin_cs | 2,254 | 0.0297 | 0.0000 | 0.0004 | 0.0093 | 0.0093 | 0.0191 | 0.0004 | 0.0018 | 0.0288 | 0.0000 | 0.0004 | 0.0000 | 0.0000 | 0.0071 | 0.0000 |
| openarchives | greek_mono | 22,126 | 0.0041 | 0.0023 | 0.0000 | 0.0140 | 0.0127 | 0.0179 | 0.0005 | 0.0007 | 0.0042 | 0.0034 | 0.0001 | 0.0004 | 0.0000 | 0.0048 | 0.0000 |
| openarchives | greek_poly | 236 | 0.0339 | 0.0169 | 0.0000 | 0.0000 | 0.0297 | 0.0381 | 0.0000 | 0.0042 | 0.0042 | 0.0000 | 0.0000 | 0.0127 | 0.0000 | 0.0042 | 0.0000 |
| openarchives | latin | 988 | 0.0719 | 0.0101 | 0.0000 | 0.0162 | 0.0648 | 0.0263 | 0.0000 | 0.0040 | 0.1457 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0425 | 0.0000 |
| parliament | greek_latin_cs | 209 | 0.0287 | 0.0000 | 0.0000 | 0.0096 | 0.0000 | 0.0048 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0144 | 0.0000 | 0.0096 | 0.0000 |
| parliament | greek_mono | 46,088 | 0.0168 | 0.0030 | 0.0000 | 0.0209 | 0.0022 | 0.0170 | 0.0003 | 0.0001 | 0.0004 | 0.0063 | 0.0005 | 0.0024 | 0.0000 | 0.0046 | 0.0000 |
| parliament | greek_poly | 37,988 | 0.0166 | 0.0023 | 0.0000 | 0.0000 | 0.0107 | 0.0182 | 0.0006 | 0.0002 | 0.0000 | 0.0000 | 0.0004 | 0.0352 | 0.0000 | 0.0039 | 0.0000 |
| parliament | latin | 756 | 0.0066 | 0.0040 | 0.0000 | 0.0661 | 0.0013 | 0.0146 | 0.0000 | 0.0000 | 0.0000 | 0.0093 | 0.0000 | 0.0000 | 0.0000 | 0.0040 | 0.0000 |
| round1 | greek_latin_cs | 1,026 | 0.0156 | 0.0127 | 0.0000 | 0.0000 | 0.0088 | 0.0117 | 0.0010 | 0.0049 | 0.0234 | 0.0000 | 0.0019 | 0.0673 | 0.0000 | 0.0019 | 0.0000 |
| round1 | greek_mono | 1,707 | 0.0105 | 0.0475 | 0.0000 | 0.4066 | 0.0053 | 0.0269 | 0.0012 | 0.0023 | 0.0000 | 0.1388 | 0.0006 | 0.0568 | 0.0000 | 0.0146 | 0.0428 |
| round1 | greek_poly | 57,970 | 0.0043 | 0.0135 | 0.0001 | 0.0000 | 0.0084 | 0.0236 | 0.0015 | 0.0011 | 0.0012 | 0.0000 | 0.0028 | 0.0685 | 0.0000 | 0.0031 | 0.0000 |
| round1 | latin | 1,162 | 0.0379 | 0.0052 | 0.0000 | 0.0095 | 0.0000 | 0.0086 | 0.0034 | 0.0034 | 0.0284 | 0.0000 | 0.0000 | 0.0120 | 0.0000 | 0.0034 | 0.0000 |
| round2 | greek_latin_cs | 416 | 0.0144 | 0.0000 | 0.0000 | 0.0048 | 0.0048 | 0.0048 | 0.0000 | 0.0000 | 0.0120 | 0.0000 | 0.0000 | 0.0553 | 0.0000 | 0.0072 | 0.0000 |
| round2 | greek_mono | 719 | 0.0056 | 0.0250 | 0.0000 | 0.4631 | 0.0028 | 0.0264 | 0.0000 | 0.0000 | 0.0000 | 0.1238 | 0.0000 | 0.0348 | 0.0000 | 0.0042 | 0.0000 |
| round2 | greek_poly | 22,311 | 0.0081 | 0.0051 | 0.0000 | 0.0000 | 0.0089 | 0.0228 | 0.0019 | 0.0001 | 0.0009 | 0.0000 | 0.0041 | 0.0764 | 0.0000 | 0.0014 | 0.0000 |
| round2 | latin | 970 | 0.0175 | 0.0000 | 0.0000 | 0.0072 | 0.0010 | 0.0052 | 0.0021 | 0.0000 | 0.0052 | 0.0021 | 0.0000 | 0.0021 | 0.0000 | 0.0010 | 0.0000 |
| vouli | greek_latin_cs | 54 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0370 | 0.0000 | 0.0000 | 0.0000 |
| vouli | greek_mono | 2,439 | 0.0025 | 0.0877 | 0.0008 | 0.1169 | 0.0025 | 0.0226 | 0.0152 | 0.0000 | 0.0000 | 0.0123 | 0.0008 | 0.0476 | 0.0000 | 0.0000 | 0.0000 |
| vouli | greek_poly | 34,542 | 0.0137 | 0.0034 | 0.0000 | 0.0000 | 0.0079 | 0.0142 | 0.0012 | 0.0008 | 0.0001 | 0.0000 | 0.0028 | 0.0297 | 0.0000 | 0.0003 | 0.0000 |
| vouli | latin | 327 | 0.0703 | 0.0000 | 0.0000 | 0.0061 | 0.0000 | 0.0031 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0031 | 0.0000 | 0.0000 | 0.0000 |
| wikisource | cyrillic | 3,118 | 0.0071 | 0.0029 | 0.0003 | 0.0045 | 0.0038 | 0.0176 | 0.0003 | 0.0000 | 0.0000 | 0.0013 | 0.0000 | 0.0000 | 0.0000 | 0.0115 | 0.0000 |
| wikisource | greek_latin_cs | 112 | 0.0536 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0179 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0625 | 0.0000 | 0.0000 | 0.0000 |
| wikisource | greek_mono | 243 | 0.0123 | 0.0206 | 0.0000 | 0.5432 | 0.0000 | 0.0247 | 0.0041 | 0.0000 | 0.0000 | 0.0782 | 0.0000 | 0.0288 | 0.0000 | 0.0000 | 0.0165 |
| wikisource | greek_poly | 8,786 | 0.0024 | 0.0055 | 0.0000 | 0.0000 | 0.0055 | 0.0213 | 0.0007 | 0.0000 | 0.0000 | 0.0000 | 0.0027 | 0.0529 | 0.0000 | 0.0013 | 0.0000 |
| wikisource | latin | 97 | 0.1443 | 0.0000 | 0.0000 | 0.1649 | 0.0000 | 0.0309 | 0.0000 | 0.0000 | 0.0000 | 0.1546 | 0.0000 | 0.0103 | 0.0000 | 0.0206 | 0.0619 |
| **all** | | 293,439 | 0.0133 | 0.0079 | 0.0001 | 0.0113 | 0.0079 | 0.0195 | 0.0011 | 0.0030 | 0.0029 | 0.0031 | 0.0015 | 0.0346 | 0.0000 | 0.0042 | 0.0003 |

Final-sigma error parts (occurrences): word-final σ 245; word-internal ς 215, of which ς where the same word with στ is attested in the pool 100; compound-boundary / aphaeresis ς (print orthography, NOT counted) 290. Spacing mark word-initially before a capital (e.g. ᾿Α for Ἀ): 9,789 lines.

Total flagged lines per type: digit_heavy 3,916, punct_heavy 2,313, symbol_heavy 24, all_caps 3,324, long_token 2,321, word_length_outlier 5,718, repeated_run 315, numeric_table 884, bibliographic 850, running_title_or_page_number 908, final_sigma_error 452, spacing_apostrophe 10,157, line_end_not_sign 0, dictionary_like 1,228, digitisation_stamp 83.

## 4. Book reference populations and hard flags

Book script class = majority class of its lines. Reference books: n_lines >= 30; final-sigma reference additionally needs >= 100 Greek words.

| class | books | ref books (N for z) | final-sigma ref N | final-sigma rate p95 | all-caps share p95 | capital-initial p95 |
|---|---:|---:|---:|---:|---:|---:|
| cyrillic | 22 | 22 | 0 | – | 0.017 | 0.517 |
| greek_latin_cs | 2 | 2 | 2 | 0.0000 | 0.005 | 0.439 |
| greek_mono | 141 | 139 | 137 | 0.0002 | 0.071 | 0.539 |
| greek_poly | 371 | 370 | 370 | 0.0014 | 0.045 | 0.585 |
| latin | 21 | 20 | 19 | 0.0001 | 0.116 | 0.672 |

Hard-flag books per flag: all_caps_above_class_p95 **29**, final_sigma_above_class_p95 **24**; books with ≥1 hard flag: **51**; verse-like books (informational): 27.

### Hard-flag books, ranked (number of hard flags, then features beyond 2σ vs same-class books)

| # | source | book_key | waves | class | n | hard flags (reasons) | features beyond 2σ |
|---:|---|---|---|---|---:|---|---:|
| 1 | anemi_round2 | bd99a3200cffaf6bf4d7c23a | round2 | greek_poly | 390 | **final_sigma_above_class_p95**: final-sigma error rate 0.0049 (9/1850 Greek words) > greek_poly book p95 0.0014 (N=370 books)<br>**all_caps_above_class_p95**: all-caps line share 0.087 > greek_poly book p95 0.045 (N=370 books) | 6 |
| 2 | anemi_round2 | b19c8b10f87827637b935a52 | round2 | greek_poly | 287 | **final_sigma_above_class_p95**: final-sigma error rate 0.0025 (5/1962 Greek words) > greek_poly book p95 0.0014 (N=370 books)<br>**all_caps_above_class_p95**: all-caps line share 0.045 > greek_poly book p95 0.045 (N=370 books) | 3 |
| 3 | openarchives_mixed_Pandemos | 9440aa94 | mixed | greek_mono | 35 | **all_caps_above_class_p95**: all-caps line share 0.657 > greek_mono book p95 0.071 (N=139 books) | 12 |
| 4 | anemi_round1 | 928e34aaaa78469aacd6c7ef | round1 | greek_poly | 214 | **all_caps_above_class_p95**: all-caps line share 0.051 > greek_poly book p95 0.045 (N=370 books) | 7 |
| 5 | anemi_round2 | a0b5d853d583a846d7f6ee31 | round2 | greek_poly | 168 | **final_sigma_above_class_p95**: final-sigma error rate 0.0020 (2/1009 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 6 |
| 6 | wikisource_el | 02a3a2a6 | wikisource | greek_poly | 245 | **final_sigma_above_class_p95**: final-sigma error rate 0.0031 (3/965 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 5 |
| 7 | wikisource_el | f7c74d15 | wikisource | greek_poly | 173 | **all_caps_above_class_p95**: all-caps line share 0.064 > greek_poly book p95 0.045 (N=370 books) | 5 |
| 8 | archive_b28038630 | 4c207e1e | mixed | latin | 9788 | **final_sigma_above_class_p95**: final-sigma error rate 0.0005 (14/27021 Greek words) > latin book p95 0.0001 (N=19 books) | 4 |
| 9 | wikisource_el | 8b6b0de9 | wikisource | greek_poly | 306 | **final_sigma_above_class_p95**: final-sigma error rate 0.0033 (4/1202 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 4 |
| 10 | anemi_round1 | cc0e056392dd2ef4916b3e7d | round1 | greek_poly | 247 | **all_caps_above_class_p95**: all-caps line share 0.065 > greek_poly book p95 0.045 (N=370 books) | 4 |
| 11 | anemi_round2 | 5a69150abb15eb1006f5a3ba | round2 | greek_poly | 458 | **final_sigma_above_class_p95**: final-sigma error rate 0.0029 (12/4075 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 3 |
| 12 | openarchives_mixed_anaktisis | 732cfbe1 | mixed | greek_mono | 224 | **all_caps_above_class_p95**: all-caps line share 0.085 > greek_mono book p95 0.071 (N=139 books) | 3 |
| 13 | wikisource_el | 2793d64c | wikisource | greek_poly | 203 | **final_sigma_above_class_p95**: final-sigma error rate 0.0023 (2/885 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 3 |
| 14 | anemi_round1 | fdcac2103d02191960287381 | round1 | greek_poly | 195 | **final_sigma_above_class_p95**: final-sigma error rate 0.0022 (2/905 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 3 |
| 15 | openarchives_mixed_ktisis | 16555249 | mixed | latin | 140 | **all_caps_above_class_p95**: all-caps line share 0.200 > latin book p95 0.116 (N=20 books) | 3 |
| 16 | anemi_round1 | e988c46677e75b38c15117fc | round1 | greek_poly | 47 | **all_caps_above_class_p95**: all-caps line share 0.128 > greek_poly book p95 0.045 (N=370 books) | 3 |
| 17 | anemi_round1 | ffe26907d1e3e9c1f75337e2 | round1 | greek_poly | 501 | **all_caps_above_class_p95**: all-caps line share 0.052 > greek_poly book p95 0.045 (N=370 books) | 2 |
| 18 | anemi_round1 | 0bff55647d1c2acd1caa8bf3 | round1 | greek_poly | 406 | **all_caps_above_class_p95**: all-caps line share 0.071 > greek_poly book p95 0.045 (N=370 books) | 2 |
| 19 | openarchives_KEIED | b014c5aa | openarchives | greek_mono | 81 | **all_caps_above_class_p95**: all-caps line share 0.210 > greek_mono book p95 0.071 (N=139 books) | 2 |
| 20 | vouli_parliament_1850s | c01ce1ebca0d | vouli | greek_poly | 61 | **all_caps_above_class_p95**: all-caps line share 0.082 > greek_poly book p95 0.045 (N=370 books) | 2 |
| 21 | archive_bub_gb_mG0mAQAAIAAJ | 0b4bf868 | cyrillic | cyrillic | 1562 | **all_caps_above_class_p95**: all-caps line share 0.017 > cyrillic book p95 0.017 (N=22 books) | 1 |
| 22 | parliament_proceedings_1975_2000 | 7bd6c40b | parliament | greek_mono | 1390 | **final_sigma_above_class_p95**: final-sigma error rate 0.0003 (3/9437 Greek words) > greek_mono book p95 0.0002 (N=137 books) | 1 |
| 23 | parliament_proceedings_1975_2000 | c72a5c9e | parliament | greek_mono | 1365 | **final_sigma_above_class_p95**: final-sigma error rate 0.0003 (3/10944 Greek words) > greek_mono book p95 0.0002 (N=137 books) | 1 |
| 24 | parliament_proceedings_1975_2000 | 5674da8d | parliament | greek_mono | 1192 | **final_sigma_above_class_p95**: final-sigma error rate 0.0002 (2/8885 Greek words) > greek_mono book p95 0.0002 (N=137 books) | 1 |
| 25 | parliament_proceedings_1975_2000 | 7b996aa5 | parliament | greek_mono | 1177 | **final_sigma_above_class_p95**: final-sigma error rate 0.0002 (2/8904 Greek words) > greek_mono book p95 0.0002 (N=137 books) | 1 |
| 26 | anemi_round1 | cbe5e7b92d36edf08153017b | round1 | greek_poly | 917 | **final_sigma_above_class_p95**: final-sigma error rate 0.0021 (10/4694 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 1 |
| 27 | anemi_round2 | cbdbe3782ed6eaa30604e844 | round2 | greek_poly | 854 | **final_sigma_above_class_p95**: final-sigma error rate 0.0024 (16/6639 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 1 |
| 28 | anemi_mixed | 5165f9e7fe1f3d7053f5adcf | mixed | greek_poly | 697 | **all_caps_above_class_p95**: all-caps line share 0.076 > greek_poly book p95 0.045 (N=370 books) | 1 |
| 29 | anemi_round1 | 6df192e72b10d13c5fc1374a | round1 | greek_poly | 605 | **final_sigma_above_class_p95**: final-sigma error rate 0.0015 (5/3426 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 1 |
| 30 | anemi_round1 | bf2ce6d100950eec319cef00 | round1 | greek_poly | 602 | **final_sigma_above_class_p95**: final-sigma error rate 0.0050 (20/3991 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 1 |
| 31 | anemi_round1 | 42c339ce492d83665f00774d | round1 | greek_poly | 589 | **final_sigma_above_class_p95**: final-sigma error rate 0.0025 (10/4000 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 1 |
| 32 | anemi_round2 | 066ab274bf75a3a1539e034b | round2 | greek_poly | 494 | **all_caps_above_class_p95**: all-caps line share 0.053 > greek_poly book p95 0.045 (N=370 books) | 1 |
| 33 | anemi_round1 | d55d101cb2fa4c91b9e11083 | round1 | greek_poly | 413 | **final_sigma_above_class_p95**: final-sigma error rate 0.0019 (5/2653 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 1 |
| 34 | wikisource_el | 69e993c1 | wikisource | greek_poly | 380 | **all_caps_above_class_p95**: all-caps line share 0.068 > greek_poly book p95 0.045 (N=370 books) | 1 |
| 35 | anemi_round1 | 8f477fb59c9bc6957aadc800 | round1 | greek_poly | 310 | **final_sigma_above_class_p95**: final-sigma error rate 0.0017 (4/2391 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 1 |
| 36 | anemi_round1 | 3a65f68ff36d911f4ca179e8 | round1 | greek_poly | 305 | **final_sigma_above_class_p95**: final-sigma error rate 0.0042 (9/2137 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 1 |
| 37 | openarchives_anaktisis | b6215fda | openarchives | greek_mono | 286 | **all_caps_above_class_p95**: all-caps line share 0.101 > greek_mono book p95 0.071 (N=139 books) | 1 |
| 38 | vouli_parliament_1850s | 3445120e6970 | vouli | greek_poly | 266 | **final_sigma_above_class_p95**: final-sigma error rate 0.0018 (4/2171 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 1 |
| 39 | anemi_mixed | b5076e8734ba287d549d79b5 | mixed | greek_poly | 265 | **all_caps_above_class_p95**: all-caps line share 0.049 > greek_poly book p95 0.045 (N=370 books) | 1 |
| 40 | anemi_round2 | 9dd010d6eb008870ea7c536c | round2 | greek_poly | 224 | **all_caps_above_class_p95**: all-caps line share 0.067 > greek_poly book p95 0.045 (N=370 books) | 1 |
| 41 | wikisource_ru | 18079f21 | wikisource | cyrillic | 221 | **all_caps_above_class_p95**: all-caps line share 0.027 > cyrillic book p95 0.017 (N=22 books) | 1 |
| 42 | anemi_round1 | 53e3db8de066783d632e29c5 | round1 | greek_poly | 184 | **final_sigma_above_class_p95**: final-sigma error rate 0.0021 (3/1438 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 1 |
| 43 | anemi_mixed | 6f9ad9bf99fd956607f4f9b3 | mixed | greek_poly | 162 | **all_caps_above_class_p95**: all-caps line share 0.167 > greek_poly book p95 0.045 (N=370 books) | 1 |
| 44 | anemi_round1 | a12ae0de4bd110201e75b12a | round1 | greek_poly | 149 | **all_caps_above_class_p95**: all-caps line share 0.054 > greek_poly book p95 0.045 (N=370 books) | 1 |
| 45 | anemi_round1 | 32d0263ab8da177020a40ccf | round1 | greek_poly | 96 | **all_caps_above_class_p95**: all-caps line share 0.115 > greek_poly book p95 0.045 (N=370 books) | 1 |
| 46 | vouli_parliament_1850s | 18167bc1e4a8 | vouli | greek_poly | 92 | **all_caps_above_class_p95**: all-caps line share 0.054 > greek_poly book p95 0.045 (N=370 books) | 1 |
| 47 | openarchives_mixed_nemertes | fdb7f5b4 | mixed | greek_mono | 46 | **all_caps_above_class_p95**: all-caps line share 0.087 > greek_mono book p95 0.071 (N=139 books) | 1 |
| 48 | anemi_round1 | c20219eff76f2fbc39f4c6fd | round1 | greek_poly | 782 | **final_sigma_above_class_p95**: final-sigma error rate 0.0015 (9/6125 Greek words) > greek_poly book p95 0.0014 (N=370 books) | 0 |
| 49 | anemi_round1 | 1c3c81f346537e276486e9fd | round1 | greek_poly | 575 | **all_caps_above_class_p95**: all-caps line share 0.049 > greek_poly book p95 0.045 (N=370 books) | 0 |
| 50 | openarchives_Dione | 9e7a9507 | openarchives | greek_mono | 268 | **all_caps_above_class_p95**: all-caps line share 0.138 > greek_mono book p95 0.071 (N=139 books) | 0 |
| 51 | openarchives_ntua | 73a3371b | openarchives | greek_mono | 242 | **all_caps_above_class_p95**: all-caps line share 0.107 > greek_mono book p95 0.071 (N=139 books) | 0 |

Books above the class p95 final-sigma rate but with fewer than 2 error occurrences (NOT hard-flagged, a single occurrence is not a book-level pattern):

- openarchives_nemertes a6e49c3a (greek_mono, 145 lines): rate 0.0010 > p95 0.0002 but only 1 error(s)
- openarchives_apothesis d02210f9 (greek_mono, 265 lines): rate 0.0004 > p95 0.0002 but only 1 error(s)
- openarchives_hellanicus fdbd7fa5 (greek_mono, 322 lines): rate 0.0003 > p95 0.0002 but only 1 error(s)

Classes with fewer than 5 reference books (class-p95 hard flags, verse-like and z-scores NOT evaluated): greek_latin_cs (N=2).

### Verse-like books (informational)

| source | book_key | class | n | reason |
|---|---|---|---:|---|
| anemi_round1 | 0bff55647d1c2acd1caa8bf3 | greek_poly | 406 | capital-initial line share 0.608 > greek_poly book p95 0.585 and median length 40 < greek_poly book median 54 |
| anemi_round1 | 686431e9a7fe04175e6e9be9 | greek_poly | 693 | capital-initial line share 0.646 > greek_poly book p95 0.585 and median length 29 < greek_poly book median 54 |
| anemi_round1 | 928e34aaaa78469aacd6c7ef | greek_poly | 214 | capital-initial line share 1.000 > greek_poly book p95 0.585 and median length 21 < greek_poly book median 54 |
| anemi_round1 | b4bb45a610fbcbc974b0eb32 | greek_poly | 356 | capital-initial line share 0.992 > greek_poly book p95 0.585 and median length 44 < greek_poly book median 54 |
| anemi_round1 | 3a65f68ff36d911f4ca179e8 | greek_poly | 305 | capital-initial line share 0.905 > greek_poly book p95 0.585 and median length 46 < greek_poly book median 54 |
| anemi_round1 | cc0e056392dd2ef4916b3e7d | greek_poly | 247 | capital-initial line share 0.632 > greek_poly book p95 0.585 and median length 33 < greek_poly book median 54 |
| anemi_round1 | 8e3c482e1f6c81bb67f24395 | greek_poly | 206 | capital-initial line share 0.592 > greek_poly book p95 0.585 and median length 39 < greek_poly book median 54 |
| anemi_round1 | 42c339ce492d83665f00774d | greek_poly | 589 | capital-initial line share 0.642 > greek_poly book p95 0.585 and median length 46 < greek_poly book median 54 |
| anemi_round1 | e28081a0d8ed58a169d0b77d | greek_poly | 891 | capital-initial line share 0.973 > greek_poly book p95 0.585 and median length 39 < greek_poly book median 54 |
| anemi_round1 | d9d705c23499ff012aa70783 | greek_poly | 578 | capital-initial line share 0.998 > greek_poly book p95 0.585 and median length 45 < greek_poly book median 54 |
| vouli_parliament_1850s | 05a4cbfdcb62 | greek_poly | 33 | capital-initial line share 0.848 > greek_poly book p95 0.585 and median length 42 < greek_poly book median 54 |
| vouli_parliament_1850s | 0d5814a3d03f | greek_poly | 35 | capital-initial line share 0.771 > greek_poly book p95 0.585 and median length 52 < greek_poly book median 54 |
| vouli_parliament_1850s | 1f485870372f | greek_poly | 450 | capital-initial line share 0.658 > greek_poly book p95 0.585 and median length 21 < greek_poly book median 54 |
| vouli_parliament_1850s | 452f5a742630 | greek_mono | 195 | capital-initial line share 0.672 > greek_mono book p95 0.539 and median length 22 < greek_mono book median 70 |
| vouli_parliament_1850s | 5c950fbb119c | greek_poly | 176 | capital-initial line share 0.614 > greek_poly book p95 0.585 and median length 24 < greek_poly book median 54 |
| vouli_parliament_1850s | bec70ac3ff65 | greek_poly | 204 | capital-initial line share 0.603 > greek_poly book p95 0.585 and median length 26 < greek_poly book median 54 |
| anemi_round2 | cbdbe3782ed6eaa30604e844 | greek_poly | 854 | capital-initial line share 0.863 > greek_poly book p95 0.585 and median length 47 < greek_poly book median 54 |
| anemi_round2 | 395473997d50a60416fa3684 | greek_poly | 93 | capital-initial line share 0.613 > greek_poly book p95 0.585 and median length 23 < greek_poly book median 54 |
| openarchives_nemertes | a6e49c3a | greek_mono | 145 | capital-initial line share 0.607 > greek_mono book p95 0.539 and median length 68 < greek_mono book median 70 |
| openarchives_mixed_KEIED | 18655fc2 | greek_mono | 51 | capital-initial line share 0.725 > greek_mono book p95 0.539 and median length 22 < greek_mono book median 70 |
| openarchives_mixed_anaktisis | 570b68fc | greek_mono | 71 | capital-initial line share 0.676 > greek_mono book p95 0.539 and median length 68 < greek_mono book median 70 |
| openarchives_mixed_Pandemos | 9440aa94 | greek_mono | 35 | capital-initial line share 1.000 > greek_mono book p95 0.539 and median length 18 < greek_mono book median 70 |
| openarchives_mixed_Dione | aa816f48 | greek_mono | 155 | capital-initial line share 0.787 > greek_mono book p95 0.539 and median length 25 < greek_mono book median 70 |
| openarchives_mixed_apothesis | e3cc19aa | greek_mono | 36 | capital-initial line share 0.722 > greek_mono book p95 0.539 and median length 23 < greek_mono book median 70 |
| wikisource_el | f7c74d15 | greek_poly | 173 | capital-initial line share 0.925 > greek_poly book p95 0.585 and median length 24 < greek_poly book median 54 |
| wikisource_ru | 155dbad1 | cyrillic | 276 | capital-initial line share 0.518 > cyrillic book p95 0.517 and median length 45 < cyrillic book median 52 |
| wikisource_ru | 18079f21 | cyrillic | 221 | capital-initial line share 1.000 > cyrillic book p95 0.517 and median length 37 < cyrillic book median 52 |

### Books with most features beyond 2σ (z of medians + z of flag shares, same-class books)

| source | book_key | class | n | n beyond 2σ | largest |z| (feature: z) |
|---|---|---|---:|---:|---|
| openarchives_mixed_Pandemos | 9440aa94 | greek_mono | 35 | 12 | median upper_share: +11.5; share all_caps: +10.4; share repeated_run: +10.4; share spacing_apostrophe: +10.3 |
| anemi_round1 | 1697d5cc21fa26717b97e073 | greek_poly | 806 | 7 | median digit_share: +17.7; share numeric_table: +14.8; share punct_heavy: +14.0; median punct_share: +9.3 |
| anemi_round1 | 928e34aaaa78469aacd6c7ef | greek_poly | 214 | 7 | median longest_token: -3.0; median n_chars: -2.9; share running_title_or_page_number: +2.6; median n_tokens: -2.6 |
| anemi_round2 | 395473997d50a60416fa3684 | greek_poly | 93 | 7 | share word_length_outlier: +6.2; median longest_token: -4.2; median mean_word_len: -3.6; median n_chars: -2.7 |
| anemi_round2 | bd99a3200cffaf6bf4d7c23a | greek_poly | 390 | 6 | share final_sigma_error: +4.8; share word_length_outlier: +3.9; share all_caps: +3.8; median longest_token: -3.0 |
| anemi_round2 | a0b5d853d583a846d7f6ee31 | greek_poly | 168 | 6 | median longest_token: -3.0; median y_rel: +2.6; median mean_word_len: -2.5; share word_length_outlier: +2.4 |
| anemi_mixed | b4266bf58120943ab8864b23 | greek_poly | 816 | 6 | share dictionary_like: +5.6; median punct_share: +5.0; share punct_heavy: +3.6; share word_length_outlier: +2.9 |
| openarchives_mixed_anaktisis | 570b68fc | greek_mono | 71 | 6 | median digit_share: +6.7; share punct_heavy: +3.8; share word_length_outlier: +3.3; median mean_word_len: -2.4 |
| vouli_parliament_1850s | 746bca682ecc | greek_poly | 31 | 5 | share digit_heavy: +4.8; median y_rel: -3.5; share long_token: +3.4; median punct_share: -2.3 |
| vouli_parliament_1850s | 87d27561a995 | greek_poly | 78 | 5 | median y_rel: +3.5; median n_chars: +2.6; share repeated_run: +2.5; median n_tokens: +2.2 |
| anemi_round2 | c3468c02b6d929362f6e3fe7 | greek_poly | 483 | 5 | median digit_share: +7.5; share spacing_apostrophe: +7.3; share digit_heavy: +5.8; median upper_share: +3.5 |
| openarchives_mixed_KEIED | 18655fc2 | greek_mono | 51 | 5 | median mean_word_len: +5.1; median n_tokens: -4.0; median n_chars: -3.3; share word_length_outlier: +3.0 |
| openarchives_mixed_anaktisis | 48c1767a | greek_mono | 141 | 5 | share punct_heavy: +8.1; median digit_share: +7.1; median punct_share: +4.1; share numeric_table: +3.2 |
| openarchives_mixed_kallipos | 8db498b8 | greek_mono | 221 | 5 | share symbol_heavy: +11.2; share word_length_outlier: +5.5; median punct_share: +3.5; median mean_word_len: -2.7 |
| openarchives_mixed_ktisis | b807848d | greek_mono | 17 | 5 | median digit_share: +18.9; share word_length_outlier: +8.1; share all_caps: +3.5; median punct_share: +3.1 |
| openarchives_mixed_KEIED | b9fd4990 | greek_mono | 66 | 5 | median y_rel: +3.1; median n_tokens: -2.4; median n_chars: -2.3; median punct_share: -2.1 |
| archive_b24878935 | 94847f75 | cyrillic | 1249 | 5 | share punct_heavy: +4.2; median punct_share: +3.6; median n_tokens: -2.6; share dictionary_like: +2.5 |
| wikisource_el | 02a3a2a6 | greek_poly | 245 | 5 | share word_length_outlier: +3.1; median longest_token: -3.0; median n_chars: -2.7; median n_tokens: -2.6 |
| wikisource_el | f7c74d15 | greek_poly | 173 | 5 | median longest_token: -3.0; median n_chars: -2.6; share all_caps: +2.6; median n_tokens: -2.6 |
| anemi_round1 | 6c82556081bbe4aada41e496 | greek_poly | 718 | 4 | median n_chars: +4.1; median n_tokens: +4.0; share long_token: +2.2; median longest_token: +2.0 |
| anemi_round1 | cc0e056392dd2ef4916b3e7d | greek_poly | 247 | 4 | median longest_token: -3.0; share all_caps: +2.7; share word_length_outlier: +2.5; share running_title_or_page_number: +2.2 |
| anemi_round1 | 2f9e996ffbdaaa3b4a9dfdcf | greek_poly | 255 | 4 | share dictionary_like: +5.1; share word_length_outlier: +4.9; median longest_token: -3.0; median mean_word_len: -2.5 |
| anemi_round1 | 650670ab271096716888b108 | greek_poly | 545 | 4 | median punct_share: +3.0; share word_length_outlier: +2.7; median upper_share: +2.5; median mean_word_len: -2.5 |
| vouli_parliament_1850s | 1f485870372f | greek_poly | 450 | 4 | median upper_share: +6.4; median n_chars: -2.9; median n_tokens: -2.6; share punct_heavy: +2.1 |
| vouli_parliament_1850s | 5c950fbb119c | greek_poly | 176 | 4 | median upper_share: +5.0; median n_tokens: -3.2; median n_chars: -2.7; median mean_word_len: +2.4 |

## 5. Examples (20 random lines per flag type, reservoir sample, fixed seed)

### digit_heavy (3,916 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `secondary health care: retrospective cohort study. BMJ. 2001;332(32):1-4.` | docs/records/harvest/harvest_big/mixed/crops/dedae223/p000272-l0033.png | digit share 0.167 > latin p90 of digit-bearing lines 0.130 (n=7100) |
| 2 | `1897 ᾿Απριλίου 23 εἰς Φάρσαλα.` | docs/records/harvest/harvest_big/round2/crops/c3468c/p000082-l0005.png | digit share 0.231 > greek_poly p90 of digit-bearing lines 0.158 (n=16302) |
| 3 | `Αθήνα, 14 Νοεμβρίου 1986` | docs/records/harvest/harvest_big/parliament/crops/7bd6c40b/p000011-l0036.png | digit share 0.286 > greek_mono p90 of digit-bearing lines 0.174 (n=9492) |
| 4 | `εὐέρκεια, ἡ, security, Plat. Legg. 778 C, 779 B: v. 1. εὐερκία.` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p000621-l0120.png | digit share 0.135 > latin p90 of digit-bearing lines 0.130 (n=7100) |
| 5 | `ΣΥΝΕΔΡΙΑΣΙΣ Ι' – 13 ΙΟΥΛΙΟΥ 1976` | docs/records/harvest/harvest_big/parliament/crops/7aea9867/p000051-l0002.png | digit share 0.222 > greek_mono p90 of digit-bearing lines 0.174 (n=9492) |
| 6 | `TRANSPARENCY 100` | docs/records/harvest/harvest_big/mixed/crops/16555249/p000090-l0022.png | digit share 0.200 > latin p90 of digit-bearing lines 0.130 (n=7100) |
| 7 | `485.57 ; τὰ οἰκηακά the private property, of the Emperor, C. I. 8685;` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p001051-l0020.png | digit share 0.158 > latin p90 of digit-bearing lines 0.130 (n=7100) |
| 8 | `30.4.1977 εἰς τὸν κατεχόμενον σήμερον χῶρον` | docs/records/harvest/harvest_big/parliament/crops/7765f98b/p000003-l0112.png | digit share 0.184 > greek_poly p90 of digit-bearing lines 0.158 (n=16302) |
| 9 | `Plat. Apol. 36 C, cf. Rep. 615 Β; ὅ τι ἂν ἡμᾶς εὐεργετήσῃς Ib. 345` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p000621-l0049.png | digit share 0.154 > greek_latin_cs p90 of digit-bearing lines 0.136 (n=3481) |
| 10 | `ἀρῆς Od. 4. 767; αἱ δ᾽ ὀλόλυξαν, at a sacrifice, 3.450; ἴθυσέν ῥ᾽` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p001065-l0127.png | digit share 0.151 > greek_latin_cs p90 of digit-bearing lines 0.136 (n=3481) |
| 11 | `380.000 δραχμές το μήνα και παίρνουν σύνταξη 150.000` | docs/records/harvest/harvest_big/parliament/crops/30fff481/p000053-l0059.png | digit share 0.267 > greek_mono p90 of digit-bearing lines 0.174 (n=9492) |
| 12 | `97. Malacosoma neustrium L. (956).` | docs/records/harvest/harvest_big/cyrillic/crops/252fd568/p000486-l0037.png | digit share 0.167 > latin p90 of digit-bearing lines 0.130 (n=7100) |
| 13 | `ΣΥΝΕΔΡΙΑΣΙΣ Λ΄ – 31 ΑΥΓΟΥΣΤΟΥ 1979` | docs/records/harvest/harvest_big/parliament/crops/1d27927c/p000015-l0001.png | digit share 0.207 > greek_mono p90 of digit-bearing lines 0.174 (n=9492) |
| 14 | `αριθμ. 1251/11.6.96 έγγραφο από τον Υπουργό Εθνικής` | docs/records/harvest/harvest_big/parliament/crops/29bccf95/p000012-l0086.png | digit share 0.200 > greek_mono p90 of digit-bearing lines 0.174 (n=9492) |
| 15 | `νεκροφορέω, to bear as a dead body to the burial, Philo 2. 540, cf. 1. 100.` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p001018-l0008.png | digit share 0.133 > latin p90 of digit-bearing lines 0.130 (n=7100) |
| 16 | `in a Phocian, 1725; in a Thessal., 1775). To be priest or priestess,` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p000717-l0081.png | digit share 0.143 > latin p90 of digit-bearing lines 0.130 (n=7100) |
| 17 | `23. Στην με αριθμό 6680/5-4-96 ερώτηση δόθηκε με το υπ'` | docs/records/harvest/harvest_big/parliament/crops/de9da003/p000010-l0020.png | digit share 0.217 > greek_mono p90 of digit-bearing lines 0.174 (n=9492) |
| 18 | `Wochenschrift 1890 N° 17 σελ. 542), ὑπὲρ ἧς τοσούτου ἐνθουσια-` | docs/records/harvest/harvest_big/round1/crops/1092c25534f45a95669f3d2b/p000059-l0015.png | digit share 0.170 > greek_latin_cs p90 of digit-bearing lines 0.136 (n=3481) |
| 19 | `καὶ κατὰ τὴν τετραετία 1975–1978 διετέθη τὸ ποσὸ τῶν` | docs/records/harvest/harvest_big/parliament/crops/a65a813d/p000011-l0058.png | digit share 0.182 > greek_poly p90 of digit-bearing lines 0.158 (n=16302) |
| 20 | `καὶ μνημείου Καραϊσκάκη μ. τ. 270,000.` | docs/records/harvest/harvest_big/round1/crops/b8b71bfd410ddd2e68429ffe/p000029-l0026.png | digit share 0.182 > greek_poly p90 of digit-bearing lines 0.158 (n=16302) |

### punct_heavy (2,313 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `Ν.Π.Δ.Δ. καὶ Ν.Π.Ι.Δ.) ἀποφάσισε καὶ γιὰ τὰ τρία Ἔρευ-` | docs/records/harvest/harvest_big/parliament/crops/f47c50c8/p000007-l0105.png | punctuation share 0.217 > greek_poly p99 of punctuated lines 0.167 |
| 2 | `παρατ. ἐλύπεε, 9, 61. Παθ. λυποῦμαι Εὐρ. Μηδ. 286, ὑποτ. -ώμεθα Σοφ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000127-l0094.png | punctuation share 0.193 > greek_poly p99 of punctuated lines 0.167 |
| 3 | `(Rbl. III. 313, Дормиторъ на 1750 м. в.), Армения, Уралъ, Алтай, Сев.-Изт.` | docs/records/harvest/harvest_big/cyrillic/crops/e2a71638/p000240-l0021.png | punctuation share 0.222 > cyrillic p99 of punctuated lines 0.217 |
| 4 | `α. μτγν. ἐπλήχθην Πλουτ. ήθ. 901, π. ἀορ. 6. ἐπλήγην ᾿Αντιφ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000164-l0034.png | punctuation share 0.180 > greek_poly p99 of punctuated lines 0.167 |
| 5 | `ρίζεται μόνον». (Βασιλ. Σειρ. Πατ. σελ. 51).` | docs/records/harvest/harvest_big/round2/crops/b19c8b/p000036-l0025.png | punctuation share 0.237 > greek_mono p99 of punctuated lines 0.176 |
| 6 | `πολὺν χρόνον Hom., Hes., etc.; οὐ π. χρ. Soph. Ph. 348, etc.; so,` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p001270-l0177.png | punctuation share 0.264 > latin p99 of punctuated lines 0.246 |
| 7 | `Ηρ. 1, 170, παρκ. γ. πλ. δειδέχαται Οδ. η, 72, ὑπερσ. ἐπ. γ. ἐν. δείδεκτο Ιλ. τ, 224, γ. πλ. δειδέχατο` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000055-l0093.png | punctuation share 0.220 > greek_poly p99 of punctuated lines 0.167 |
| 8 | `ὡς ἕρμα (Σχῆμα 13).` | docs/records/harvest/harvest_big/round2/crops/e85d2d/p000012-l0077.png | punctuation share 0.188 > greek_poly p99 of punctuated lines 0.167 |
| 9 | `SIGNAL s_clk: std_logic :='0';` | docs/records/harvest/harvest_big/mixed/crops/5bcf3381/p000030-l0005.png | punctuation share 0.259 > latin p99 of punctuated lines 0.246 |
| 10 | `rfumer (-мър) п. търго-` | docs/records/harvest/harvest_big/cyrillic/crops/94847f75/p000649-l0028.png | punctuation share 0.250 > cyrillic p99 of punctuated lines 0.217 |
| 11 | `θάπω ἢ τάφω (ὡς ἀνωτ.) ἐπ. καὶ ἴων. παρκ. α. τέθᾶφα Κωμ. ἀποσπ. 4;` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000091-l0041.png | punctuation share 0.189 > greek_poly p99 of punctuated lines 0.167 |
| 12 | `beach (би'ич) п. брѣгъ, край.` | docs/records/harvest/harvest_big/cyrillic/crops/94847f75/p000086-l0006.png | punctuation share 0.240 > cyrillic p99 of punctuated lines 0.217 |
| 13 | `τὸς Λάκωνες Ησυχ. δημιο-εργός, ὄργανον, ᾿Αργ-αδεῖς, ἐν-εργ-έω, εὐ-εργ-` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000078-l0100.png | punctuation share 0.175 > greek_poly p99 of punctuated lines 0.167 |
| 14 | `Φ. ΙΙ. Βάρβογλης,` | docs/records/harvest/harvest_big/vouli/crops/4522d4e8fd58/p000005-l0027.png | punctuation share 0.200 > greek_mono p99 of punctuated lines 0.176 |
| 15 | `Sonis, S.T., Eilers,J.P., Epstein, J.B., Le Vaque, F.G., Liggett, W.H., Mulagha, M.Τ.,` | docs/records/harvest/harvest_big/mixed/crops/df20db94/p000194-l0020.png | punctuation share 0.320 > latin p99 of punctuated lines 0.246 |
| 16 | `μελ. δια-φθερέει 5, 51, ἐπ. δια-φθέρσει Ιλ. ν,` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000201-l0107.png | punctuation share 0.205 > greek_poly p99 of punctuated lines 0.167 |
| 17 | `ἀποδεικνύμενος Πινδ. Ν. 6, 49, μελ. ἐν-δείξομαι Ιλ. τ, 83, Εὐρ. Βακ. 47, ἄορ. δείξατο Ὁμ.` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000055-l0091.png | punctuation share 0.189 > greek_poly p99 of punctuated lines 0.167 |
| 18 | `sun-light, Eccl.:-ἡλιό-βολος, ov, sun-burnt, Theophr. C. P. 4. 12, 3.` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p000669-l0043.png | punctuation share 0.267 > latin p99 of punctuated lines 0.246 |
| 19 | `(Ὑδρο-) χλωρική μορφίνη.` | docs/records/harvest/harvest_big/mixed/crops/70e0a344/p000198-l0026.png | punctuation share 0.182 > greek_poly p99 of punctuated lines 0.167 |
| 20 | `(ὁδὸς Εὐριπίδου ἀριθ. 51).` | docs/records/harvest/harvest_big/mixed/crops/137e9af6/p000003-l0011.png | punctuation share 0.174 > greek_poly p99 of punctuated lines 0.167 |

### symbol_heavy (24 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `ὅπερ δακτυλικῶς προφέρεται Ἔν πολυ \| ὕμνη \|\| τῷ Διος \| ἄλσει.` | docs/records/harvest/harvest_big/round1/crops/6389d36a8d20c1541b1d4bcb/p000041-l0009.png | symbol share 0.080 > greek_poly p99 of symbol-bearing lines 0.075 (n=549) |
| 2 | `Ἢ Θεὸς \| ἤλθ᾽ ἐπὶ \| γῆν ἐξ \| οὐρανοῦ \| εἰκόνα \| δείξων` | docs/records/harvest/harvest_big/round1/crops/6389d36a8d20c1541b1d4bcb/p000068-l0028.png | symbol share 0.122 > greek_poly p99 of symbol-bearing lines 0.075 (n=549) |
| 3 | `Ὡς ἥδομαι \| καὶ τέρπομαι \|\| καὶ βούλομαι \| χορεῦσαι` | docs/records/harvest/harvest_big/round1/crops/6389d36a8d20c1541b1d4bcb/p000088-l0020.png | symbol share 0.095 > greek_poly p99 of symbol-bearing lines 0.075 (n=549) |
| 4 | `Καλότυχα \| ψηλά βουνά \|\| καὶ κάμποι βλο \| γημένοι` | docs/records/harvest/harvest_big/round1/crops/6389d36a8d20c1541b1d4bcb/p000088-l0024.png | symbol share 0.100 > greek_poly p99 of symbol-bearing lines 0.075 (n=549) |
| 5 | `- - \| λάλα,λάλα \| λαλὰ,λαλὰ` | docs/records/harvest/harvest_big/round1/crops/6389d36a8d20c1541b1d4bcb/p000140-l0021.png | symbol share 0.091 > greek_poly p99 of symbol-bearing lines 0.075 (n=549) |
| 6 | `φθονῶ τινα. μὴ = μήπως. δοκῶ = φαίνομαι. – κοσμῶ=` | docs/records/harvest/harvest_big/round1/crops/1495fc2311427a558abbfd88/p000049-l0009.png | symbol share 0.075 > greek_poly p99 of symbol-bearing lines 0.075 (n=549) |
| 7 | `\|12\| Καλλιφωνίας` | docs/records/harvest/harvest_big/vouli/crops/92d580f394fe/p000025-l0034.png | symbol share 0.133 > greek_mono p99 of symbol-bearing lines 0.127 (n=375) |
| 8 | `\|23\| Νεβροπόλεως` | docs/records/harvest/harvest_big/vouli/crops/92d580f394fe/p000036-l0089.png | symbol share 0.133 > greek_mono p99 of symbol-bearing lines 0.127 (n=375) |
| 9 | `$newEntry=$ytf-` | docs/records/harvest/harvest_big/mixed/crops/ac96c674/p000192-l0009.png | symbol share 0.200 > latin p99 of symbol-bearing lines 0.177 (n=664) |
| 10 | `FS = <ρομπότ, επενεργητές>` | docs/records/harvest/harvest_big/openarchives/crops/4c106110/p000063-l0012.png | symbol share 0.130 > greek_latin_cs p99 of symbol-bearing lines 0.083 (n=635) |
| 11 | `<Units>inches</Units>` | docs/records/harvest/harvest_big/mixed/crops/16555249/p000085-l0033.png | symbol share 0.190 > latin p99 of symbol-bearing lines 0.177 (n=664) |
| 12 | `<Units>meters</Units>` | docs/records/harvest/harvest_big/mixed/crops/16555249/p000085-l0040.png | symbol share 0.190 > latin p99 of symbol-bearing lines 0.177 (n=664) |
| 13 | `№ 2.- Русскій Архивъ № 2. — Историческій Вѣстникъ № 2.` | docs/records/harvest/harvest_big/cyrillic/crops/0b4bf868/p000588-l0013.png | symbol share 0.068 > cyrillic p99 of symbol-bearing lines 0.054 (n=106) |
| 14 | `<Units>percent</Units>` | docs/records/harvest/harvest_big/mixed/crops/16555249/p000085-l0048.png | symbol share 0.182 > latin p99 of symbol-bearing lines 0.177 (n=664) |
| 15 | `Waterways <br> </br>` | docs/records/harvest/harvest_big/mixed/crops/16555249/p000094-l0024.png | symbol share 0.222 > latin p99 of symbol-bearing lines 0.177 (n=664) |
| 16 | `<p>Reference:<br>` | docs/records/harvest/harvest_big/mixed/crops/16555249/p000094-l0034.png | symbol share 0.235 > latin p99 of symbol-bearing lines 0.177 (n=664) |
| 17 | `λίζει ότι silp ZG = ∞ και άρα spli ZG = ∞ (Θεώρημα 4.5). Επιπλέον, αφού findim ZG = ∞, από` | docs/records/harvest/harvest_big/mixed/crops/16c9d9fc/p000125-l0014.png | symbol share 0.086 > greek_latin_cs p99 of symbol-bearing lines 0.083 (n=635) |
| 18 | `όπου Π(a)(x + L) = ax + L. Έχουμε` | docs/records/harvest/harvest_big/mixed/crops/8db498b8/p000037-l0035.png | symbol share 0.120 > greek_latin_cs p99 of symbol-bearing lines 0.083 (n=635) |
| 19 | `κάθε περιοχή ν του χ και κάθε Ι ∈ Z+ υπάρχει μια ακολουθία n = (nk) ⊆ Z+` | docs/records/harvest/harvest_big/mixed/crops/8db498b8/p000081-l0008.png | symbol share 0.091 > greek_latin_cs p99 of symbol-bearing lines 0.083 (n=635) |
| 20 | `συμπαγές ανοικτό σύνολο V₁ με diam(V₁) < 1 ώστε V₁ ⊆ φ−−1 (V)∩V. Επειδή` | docs/records/harvest/harvest_big/mixed/crops/8db498b8/p000084-l0031.png | symbol share 0.086 > greek_latin_cs p99 of symbol-bearing lines 0.083 (n=635) |

### all_caps (3,324 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `ΑΠΛΑ ΦΑΡΜΑΚΑ ΚΑΙ ΠΑΡΕΣΚΕΥΑΣΜΕΝΑ. - ΧΗΜΙΚΑΙ` | docs/records/harvest/harvest_big/mixed/crops/5165f9e7/p000021-l0007.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 2 | `ΕΜ. ΣΚΟΥΛΑΚΗΣ"` | docs/records/harvest/harvest_big/parliament/crops/f74236d5/p000006-l0083.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 3 | `ΣΥΝΕΔΡΙΑΣΙΣ ΡΙΒ΄ 26 ΑΠΡΙΛΙΟΥ 1977` | docs/records/harvest/harvest_big/parliament/crops/51e4207d/p000015-l0002.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 4 | `ΚΩΝΣΤΑΝΤΙΝΟΣ ΛΑΛΙΩΤΗΣ` | docs/records/harvest/harvest_big/parliament/crops/f36aba38/p000005-l0060.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 5 | `ΑΓ. ΚΟΥΤΣΟΓΙΩΡΓΑΣ»` | docs/records/harvest/harvest_big/parliament/crops/859c90dc/p000006-l0089.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 6 | `ΠΕΡΙΓΡΑΦΗ ΟΛΗΣ ΤΗΣ ΝΗΣΟΥ.` | docs/records/harvest/harvest_big/round1/crops/460b94bc8e2c58a95074382b/p000023-l0036.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 7 | `ΑΛΕΞΑΝΔΡΟΣ` | docs/records/harvest/harvest_big/round2/crops/066ab2/p000055-l0016.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 8 | `ΔΙΑΧΕΙΡΙΣΗ` | docs/records/harvest/harvest_big/openarchives/crops/cffac36f/p000019-l0025.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 9 | `ΦΩΝΗ ΕΚ ΠΙΝΔΟΥ` | docs/records/harvest/harvest_big/round2/crops/68ab53/p000174-l0002.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 10 | `Π. ΠΑΝΟΥΡΓΙΑΣ»` | docs/records/harvest/harvest_big/parliament/crops/7f661ed4/p000011-l0136.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 11 | `ΣΥΝΕΔΡΙΑΣΙΣ` | docs/records/harvest/harvest_big/vouli/crops/452f5a742630/p000004-l0043.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 12 | `Ν. ΑΚΡΙΤΙΔΗΣ"` | docs/records/harvest/harvest_big/parliament/crops/30fff481/p000010-l0111.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 13 | `ΑΠΟ ΤΗΝ ΙΣΤΟΡΙΑΝ` | docs/records/harvest/harvest_big/round2/crops/8b1c7b/p000098-l0013.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 14 | `ΗΛΙΑ ΤΑΝΤΑΛΙΔΟΥ` | docs/records/harvest/harvest_big/round1/crops/1118b0c89e773062b4cf69f5/p000101-l0001.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 15 | `ΣΥΝΕΔΡΙΑΣΗ ΡΜΘ' – 19 ΙΟΥΝΙΟΥ 1996` | docs/records/harvest/harvest_big/parliament/crops/29bccf95/p000029-l0001.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 16 | `ΚΥΡΙΑ ΣΥΝΤΑΓΜΑ.` | docs/records/harvest/harvest_big/round2/crops/9dd010/p000034-l0023.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 17 | `ΙΣΤΟΡΙΚΗ ΕΙΣΑΓΩΓΗΙ` | docs/records/harvest/harvest_big/mixed/crops/5755602e/p000086-l0002.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 18 | `THE GREATER` | docs/records/harvest/harvest_big/parliament/crops/48a58eb5/p000037-l0019.png | all cased letters uppercase (upper share 1.00); latin all-caps line rate 0.013 |
| 19 | `ΔΙΑΧΕΙΡΙΣΤΙΚΟΙ ΕΛΕΓΧΟΙ` | docs/records/harvest/harvest_big/openarchives/crops/1d5ad22a/p000038-l0018.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |
| 20 | `Β΄) ΣΙΤΟΚΑΛΛΙΕΡΓΕΙΑ - ΑΛΑΤΟΠΑΡΑΓΩΓΗ` | docs/records/harvest/harvest_big/round2/crops/b3c6af/p000047-l0005.png | all cased letters uppercase (upper share 1.00); greek_mono all-caps line rate 0.040 |

### long_token (2,321 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `εἰς τὰς βασάνους, οἱ διῶκται προπαρασκευάζοντες αὐτάς.` | docs/records/harvest/harvest_big/round1/crops/bf38261008b005a7898b7005/p000013-l0042.png | longest token 18 chars > greek_poly p99 16 |
| 2 | `τῇ φυγοπονίᾳ των δικαιολογουμένους ὅτι δὲν εὐ-` | docs/records/harvest/harvest_big/wikisource/crops/9c1dca9b/p000015-l0033.png | longest token 17 chars > greek_poly p99 16 |
| 3 | `ΠΑΠΑΜΙΧΑΛΟΠΟΥΛΟΣ. Τὸ ἀντίτιμον τῆς ἐκποιήσεως` | docs/records/harvest/harvest_big/vouli/crops/fefd8ab7740f/p000004-l0083.png | longest token 17 chars > greek_poly p99 16 |
| 4 | `σε συγκεκριμένους παράγοντες-κλειδιά.` | docs/records/harvest/harvest_big/openarchives/crops/5b6f51a1/p000051-l0022.png | longest token 19 chars > greek_mono p99 18 |
| 5 | `ΠΑΠΑΜΙΧΑΛΟΠΟΥΛΟΣ. Πρὸ δύο ἡμερῶν ἀνέλαβον τὴν` | docs/records/harvest/harvest_big/vouli/crops/240e6345063d/p000011-l0068.png | longest token 17 chars > greek_poly p99 16 |
| 6 | `μικτῶν ἐπαγγελματοβιοτεχνικῶν Ἐπιμελητηρίων, δὲν ὑπάρ-` | docs/records/harvest/harvest_big/parliament/crops/dd625312/p000023-l0014.png | longest token 22 chars > greek_poly p99 16 |
| 7 | `συμβουλές σε άλλους επαγγελματίες του σχολείου, συμπεριλαμβανομένου του` | docs/records/harvest/harvest_big/openarchives/crops/982e0266/p000013-l0005.png | longest token 19 chars > greek_mono p99 18 |
| 8 | `Συμπερασματικά, η εφαρμογή της Μουσειοπαιδαγωγικής Επιστήμης θέτει ως κύριο` | docs/records/harvest/harvest_big/openarchives/crops/fdbd7fa5/p000018-l0024.png | longest token 19 chars > greek_mono p99 18 |
| 9 | `<ShowCustomLogos>false</ShowCustomLogos>` | docs/records/harvest/harvest_big/mixed/crops/16555249/p000085-l0021.png | longest token 40 chars > latin p99 39 |
| 10 | `εὐπρεπείας ἀποδιοπομπήσασθαι τοὺς φιλοσόφους ἅπαντας` | docs/records/harvest/harvest_big/mixed/crops/1c13bd49/p000135-l0004.png | longest token 17 chars > greek_poly p99 16 |
| 11 | `ἀπ-ακοντίζω (μλ.-ιῶ)ἐκσφενδονίζω,` | docs/records/harvest/harvest_big/mixed/crops/b4266bf5/p000225-l0030.png | longest token 21 chars > greek_poly p99 16 |
| 12 | `ActiveWorkbook.Worksheets(1).Sort.SortFields.` | docs/records/harvest/harvest_big/mixed/crops/a85515c7/p000313-l0037.png | longest token 45 chars > latin p99 39 |
| 13 | `νους τῶν σήμερον δημοσιογραφούντων τὸν ἰσό` | docs/records/harvest/harvest_big/wikisource/crops/51fe7386/p000004-l0022.png | longest token 17 chars > greek_poly p99 16 |
| 14 | `χικοῦ οἴκου καὶ ναοῦ Κωνσταντινούπολις 1884 σ. 13-Τοῦ αὐτοῦ` | docs/records/harvest/harvest_big/round2/crops/39fbbd/p000053-l0036.png | longest token 17 chars > greek_poly p99 16 |
| 15 | `συμμετοχή των επιχειρήσεων, των εκπαιδευτών/συμβούλων και των μεντόρων/έμπειρων` | docs/records/harvest/harvest_big/openarchives/crops/a0822ede/p000023-l0021.png | longest token 21 chars > greek_mono p99 18 |
| 16 | `συμβούλων/εκπαιδευτών και συμμετεχόντων/ωφελουμένων, εκ των υστέρων αξιολόγηση` | docs/records/harvest/harvest_big/openarchives/crops/a0822ede/p000023-l0018.png | longest token 26 chars > greek_mono p99 18 |
| 17 | `τρίου, υποβάλετε ένσταση αντισυνταγματικότητας και θέλετε` | docs/records/harvest/harvest_big/parliament/crops/7a1452d8/p000026-l0135.png | longest token 21 chars > greek_mono p99 18 |
| 18 | `генералъ-фельдцехмейстеру, ландграфу Гес- усмотрѣнію архієрея, для чего и выданъ` | docs/records/harvest/harvest_big/cyrillic/crops/9a32fb66/p000095-l0047.png | longest token 26 chars > cyrillic p99 18 |
| 19 | `ἤδη ἀποκατασταθέντων, ὡς διωχθέντων γιὰ πολιτικούς λό-` | docs/records/harvest/harvest_big/parliament/crops/95d812ab/p000023-l0065.png | longest token 17 chars > greek_poly p99 16 |
| 20 | `Κωνσταντινουπόλεως ἦσαν ἰσχυρὰ ὡς τὰ τῆς Βαβυλῶνος, τὸ τη-` | docs/records/harvest/harvest_big/mixed/crops/a51f2efd/p000016-l0067.png | longest token 18 chars > greek_poly p99 16 |

### word_length_outlier (5,718 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `τόμ. Ι΄. τεῦχος Α΄, Β΄, Γ΄. Ἐν ᾿Αθήναις 1888, σελὶς 83 καὶ τεῦχος` | docs/records/harvest/harvest_big/round2/crops/39fbbd/p000015-l0019.png | mean word length 3.27 over 11 words outside greek_poly [p1 3.50, p99 8.33] of >=3-word lines |
| 2 | `κατά την έξοδό του από τη χώρα.` | docs/records/harvest/harvest_big/parliament/crops/859c90dc/p000009-l0099.png | mean word length 3.43 over 7 words outside greek_mono [p1 3.58, p99 9.33] of >=3-word lines |
| 3 | `Από την επιλογή του Ν,` | docs/records/harvest/harvest_big/mixed/crops/570b68fc/p000028-l0065.png | mean word length 3.40 over 5 words outside greek_mono [p1 3.58, p99 9.33] of >=3-word lines |
| 4 | `Ἤθελα νὰ ἴδω τὴν στάσιν του, τὸ ὕφος του, νὰ μάθω ἐπὶ` | docs/records/harvest/harvest_big/wikisource/crops/22fda82b/p000112-l0006.png | mean word length 3.33 over 12 words outside greek_poly [p1 3.50, p99 8.33] of >=3-word lines |
| 5 | `Θέλω νὰ πῶ γιὰ κείνους πὄχουν θέση. Ἂς ᾔ-` | docs/records/harvest/harvest_big/round1/crops/8f477fb59c9bc6957aadc800/p000108-l0031.png | mean word length 3.44 over 9 words outside greek_poly [p1 3.50, p99 8.33] of >=3-word lines |
| 6 | `II. the Act, is found in Lxx` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p000164-l0114.png | mean word length 2.86 over 7 words outside latin [p1 3.00, p99 10.00] of >=3-word lines |
| 7 | `✓ Διατραπεζική μεταφορά εξωτερικού` | docs/records/harvest/harvest_big/openarchives/crops/6797597d/p000013-l0013.png | mean word length 10.00 over 3 words outside greek_mono [p1 3.58, p99 9.33] of >=3-word lines |
| 8 | `Αθ. Λ. Νίκενας` | docs/records/harvest/harvest_big/round2/crops/592f08/p000083-l0057.png | mean word length 3.33 over 3 words outside greek_mono [p1 3.58, p99 9.33] of >=3-word lines |
| 9 | `καὶ τὴν πώληση σ' ὅλη τὴν ἔκταση τῆς Χώρας μας τὴν φε-` | docs/records/harvest/harvest_big/parliament/crops/13dcc39a/p000012-l0048.png | mean word length 3.42 over 12 words outside greek_poly [p1 3.50, p99 8.33] of >=3-word lines |
| 10 | `μα με τις οφειλές των ΠΑΕ και προς το ΙΚΑ και προς το` | docs/records/harvest/harvest_big/parliament/crops/7c411292/p000034-l0120.png | mean word length 3.15 over 13 words outside greek_mono [p1 3.58, p99 9.33] of >=3-word lines |
| 11 | `λα να σημειώσω ότι η συζήτηση από την πλευρά του κ. Υ-` | docs/records/harvest/harvest_big/parliament/crops/30d76051/p000020-l0030.png | mean word length 3.42 over 12 words outside greek_mono [p1 3.58, p99 9.33] of >=3-word lines |
| 12 | `κοκρατίας κακοενδύεται, κακοϋποδύεται, κακοδιαιτᾶται, ἀποκαλεῖται μὲν` | docs/records/harvest/harvest_big/round1/crops/7d1e098609bb25ba5bb9c0ed/p000009-l0038.png | mean word length 10.17 over 6 words outside greek_poly [p1 3.50, p99 8.33] of >=3-word lines |
| 13 | `μόνος του εἰς τὸ ὄρος.` | docs/records/harvest/harvest_big/round1/crops/83df10d25e7c4c1cefe2aed5/p000053-l0054.png | mean word length 3.40 over 5 words outside greek_poly [p1 3.50, p99 8.33] of >=3-word lines |
| 14 | `ἀπὸ τὸν Θεὸν νὰ` | docs/records/harvest/harvest_big/round1/crops/f3cfa262eedab9cd43a9e412/p000049-l0054.png | mean word length 3.00 over 4 words outside greek_poly [p1 3.50, p99 8.33] of >=3-word lines |
| 15 | `Πρὸ τοῦ 480 π. Χ. περίπου.` | docs/records/harvest/harvest_big/mixed/crops/c8654864/p000449-l0034.png | mean word length 3.00 over 5 words outside greek_poly [p1 3.50, p99 8.33] of >=3-word lines |
| 16 | `Ἐκκλησίας Κύπρου διεξάγεται` | docs/records/harvest/harvest_big/round1/crops/1d9da09e2d3f82285de0cf2d/p000033-l0029.png | mean word length 8.33 over 3 words outside greek_poly [p1 3.50, p99 8.33] of >=3-word lines |
| 17 | `7. Στρατηγική Ακαδημαϊκής Ανάπτυξης` | docs/records/harvest/harvest_big/openarchives/crops/94fbbe22/p000140-l0001.png | mean word length 10.00 over 3 words outside greek_mono [p1 3.58, p99 9.33] of >=3-word lines |
| 18 | `Εἶν᾿ ὡραία; Τι ξέρω ἐγώ! καὶ οἱ πιὸ γέροι` | docs/records/harvest/harvest_big/round2/crops/8b1c7b/p000175-l0018.png | mean word length 3.33 over 9 words outside greek_poly [p1 3.50, p99 8.33] of >=3-word lines |
| 19 | `φαντασίας ἀπηλλαγμένον ! ἀπήντησα.` | docs/records/harvest/harvest_big/round2/crops/3598eb/p000050-l0034.png | mean word length 9.67 over 3 words outside greek_poly [p1 3.50, p99 8.33] of >=3-word lines |
| 20 | `γης, π.λάνης, γυμνής. β) τὰ εἰς ας, αδος· ὡς φυγάς, φορ-` | docs/records/harvest/harvest_big/round1/crops/c20219eff76f2fbc39f4c6fd/p000021-l0013.png | mean word length 3.36 over 11 words outside greek_poly [p1 3.50, p99 8.33] of >=3-word lines |

### repeated_run (315 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `ποὺ ἔλεγε «σὲ θέλω ἐπιτυχόντα καὶ ὄχι ἐνιστάμενο»....` | docs/records/harvest/harvest_big/parliament/crops/847e1ec1/p000036-l0105.png | 1 run(s) of >=4 identical chars, max 4, chars '.'; greek_poly line rate 0.0012 |
| 2 | `Νὰ φτάσει τὸ ἀντιλάλημα. Στὰ πεθαμένα----` | docs/records/harvest/harvest_big/round1/crops/d9d705c23499ff012aa70783/p000036-l0047.png | 1 run(s) of >=4 identical chars, max 4, chars '-'; greek_poly line rate 0.0012 |
| 3 | `Dieu qui m'a inspiré de....` | docs/records/harvest/harvest_big/mixed/crops/57256519/p001130-l0035.png | 1 run(s) of >=4 identical chars, max 4, chars '.'; latin line rate 0.0012 |
| 4 | `ніе), 10000 зол. на епископскую церковь въ Крылосѣ близь Га-` | docs/records/harvest/harvest_big/cyrillic/crops/0b4bf868/p001007-l0024.png | 1 run(s) of >=4 identical chars, max 4, chars '0'; cyrillic line rate 0.0004 |
| 5 | `ὕψη υι, υ2.... τείνουσι νὰ καταστῶσι πάντα ἴσα τῇ πλευρᾷ` | docs/records/harvest/harvest_big/round1/crops/666498b9ed183dc88c1e8716/p000138-l0045.png | 1 run(s) of >=4 identical chars, max 4, chars '.'; greek_poly line rate 0.0012 |
| 6 | `Νικόλ. Καναβός ....` | docs/records/harvest/harvest_big/vouli/crops/91252504a906/p000008-l0118.png | 1 run(s) of >=4 identical chars, max 4, chars '.'; greek_mono line rate 0.0008 |
| 7 | `ζουσῶν σκηνῶν καὶ ἀναμνήσεων....` | docs/records/harvest/harvest_big/round1/crops/8298db8c50ae1b18df756118/p000015-l0039.png | 1 run(s) of >=4 identical chars, max 4, chars '.'; greek_poly line rate 0.0012 |
| 8 | `πῆτέ μου ὅμως πρωτύτερα τί ξεύρετε διὰ τὴν μυῖγα...... Γίνεται.` | docs/records/harvest/harvest_big/mixed/crops/b8b6779d/p000026-l0037.png | 1 run(s) of >=4 identical chars, max 6, chars '.'; greek_poly line rate 0.0012 |
| 9 | `Στὸ ἄρθρο 2 παρ. ὁ λέτε: «γαῖαι αἱ ὁποῖαι ἀνήκουν....»` | docs/records/harvest/harvest_big/parliament/crops/20900789/p000040-l0055.png | 1 run(s) of >=4 identical chars, max 4, chars '.'; greek_poly line rate 0.0012 |
| 10 | `Ν. Καφετζόγλους ....` | docs/records/harvest/harvest_big/vouli/crops/3e08dd4de36e/p000016-l0053.png | 1 run(s) of >=4 identical chars, max 4, chars '.'; greek_mono line rate 0.0008 |
| 11 | `Γεώργιος Θεοτόκης ....` | docs/records/harvest/harvest_big/vouli/crops/3e08dd4de36e/p000014-l0010.png | 1 run(s) of >=4 identical chars, max 4, chars '.'; greek_mono line rate 0.0008 |
| 12 | `πολοχαγό. Τοῦ λέγω δὲ Κλ..... Τί νὰ λέγῃ τὸ Μαρικάκι` | docs/records/harvest/harvest_big/round1/crops/2d29e5e76d90adc4cc1b093a/p000010-l0035.png | 1 run(s) of >=4 identical chars, max 5, chars '.'; greek_poly line rate 0.0012 |
| 13 | `αὐτή, αὐτή, αὐτή.... τἱ ἀποτελοῦν ; ἀποτελοῦν τὴν περιφέρειαν` | docs/records/harvest/harvest_big/mixed/crops/b8b6779d/p000028-l0040.png | 1 run(s) of >=4 identical chars, max 4, chars '.'; greek_poly line rate 0.0012 |
| 14 | `Τομέας Β΄: Διαχείρισης – επιχειρησιακού σχεδιασμού – συντονισμού – εκπαίδευσης............16` | docs/records/harvest/harvest_big/openarchives/crops/5794f70e/p000005-l0035.png | 1 run(s) of >=4 identical chars, max 12, chars '.'; greek_mono line rate 0.0008 |
| 15 | `.... όχι όταν συνοδεύουν τον Πρωθυπουργό, αλλά λογικά` | docs/records/harvest/harvest_big/parliament/crops/7a1452d8/p000032-l0070.png | 1 run(s) of >=4 identical chars, max 4, chars '.'; greek_mono line rate 0.0008 |
| 16 | `Ἐμβατήριον.....` | docs/records/harvest/harvest_big/wikisource/crops/f7c74d15/p000031-l0015.png | 1 run(s) of >=4 identical chars, max 5, chars '.'; greek_poly line rate 0.0012 |
| 17 | `-Δώσατε τα καὶ εἰς τοὺς ἄλλους· τί παρετηρήσατε; (....)-καλά.` | docs/records/harvest/harvest_big/mixed/crops/b8b6779d/p000020-l0066.png | 1 run(s) of >=4 identical chars, max 4, chars '.'; greek_poly line rate 0.0012 |
| 18 | `τὰ ὁποῖα δικαιοῦται νὰ ἔχῃ. Εἶναι πενέστατος καὶ ἄξιος τῆς τέρων αἰτίων βεβαίως θέλει παραδεχθῆ..... :` | docs/records/harvest/harvest_big/vouli/crops/182619a5630d/p000002-l0040.png | 1 run(s) of >=4 identical chars, max 5, chars '.'; greek_poly line rate 0.0012 |
| 19 | `Теодорить Василіе началникъ.....` | docs/records/harvest/harvest_big/cyrillic/crops/7235f8d0/p000104-l0029.png | 1 run(s) of >=4 identical chars, max 5, chars '.'; cyrillic line rate 0.0004 |
| 20 | `αὐτῶν, δίδων διαταγὰς περὶ μυστικῆς παρασκευῆς 100000 μερίδων` | docs/records/harvest/harvest_big/round1/crops/00c322b3ee04b419d1979f22/p000166-l0050.png | 1 run(s) of >=4 identical chars, max 5, chars '0'; greek_poly line rate 0.0012 |

### numeric_table (884 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `ὑπ-οιδέω, intr. to swell up a little, Hipp. Coac. 137., 262, 11, Ael.` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p001651-l0107.png | 3 consecutive numeric tokens; latin line rate 0.0355 |
| 2 | `λεσιν τῶν κατὰ τὰς 38 1, 2 καὶ 5 τοῦ αὐτοῦ ἄρθρ. ἀπο- φάτεων` | docs/records/harvest/harvest_big/vouli/crops/b63ac145f7c7/p000001-l0100.png | 3 consecutive numeric tokens; greek_poly line rate 0.0006 |
| 3 | `Hermipp. Φορμ. 1. 16; used for fattening cattle, Arist. H. A. 8. 7, 1;` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p000256-l0194.png | 3 consecutive numeric tokens; latin line rate 0.0355 |
| 4 | `σθαι Ξεν. ἀπομν. 2, 7, 1, μτχ. ἀκούμενος Πλατ. Φιλ. 30, ἀλλὰ` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000019-l0027.png | 3 consecutive numeric tokens; greek_poly line rate 0.0006 |
| 5 | `Xen. Cyr. 7. 1, 32; τὸ στεγάζον, of the body which covers the soul,` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p001445-l0008.png | 3 consecutive numeric tokens; latin line rate 0.0355 |
| 6 | `προειργασμένη δόξα glory won before, Xen. An. 6. 1, 21.` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p001304-l0004.png | 3 consecutive numeric tokens; latin line rate 0.0355 |
| 7 | `Ενισχύει τη στρατηγική για τη δια βίου μάθηση με συνεκτικό τρόπο (υποέργα 1, 2, 3 και 4)` | docs/records/harvest/harvest_big/openarchives/crops/a0822ede/p000087-l0019.png | 3 consecutive numeric tokens; greek_mono line rate 0.0004 |
| 8 | `προερύσσω (sc. νῆας) 9. 358. 2. to move the ship forward, by` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p001304-l0029.png | 3 consecutive numeric tokens; latin line rate 0.0355 |
| 9 | `γοῦν σοί [ἀποκρίνεσθαι] Xen. Hell. 4. 1, 37; cf. Plat. Prot. 312 B, al.` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p001287-l0173.png | 3 consecutive numeric tokens; latin line rate 0.0355 |
| 10 | `12, al. ΙΙ. ὁ δ. (sc. ναύς), a temple with double peristyle, Vitruv. 3. 1, 21.` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p000399-l0046.png | 3 consecutive numeric tokens; latin line rate 0.0355 |
| 11 | `τἂν μαθέτω Anth. P. 12. 206. 4. first, for the first time, ἐνταῦθα` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p001351-l0068.png | 3 consecutive numeric tokens; latin line rate 0.0355 |
| 12 | `γυναιξὶ τοῦ τεκνοῦσθαι καὶ τοῖς ἄρρεσι τοῦ τεκνοῦν Arist. Η. Α. 7. 5, 2;` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p001557-l0102.png | 3 consecutive numeric tokens; greek_latin_cs line rate 0.0255 |
| 13 | `σαρκόρριζος, ον, with a fleshy root, Theophr. H. P. 7. 12, 1, Odor. 63.` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p001397-l0052.png | 3 consecutive numeric tokens; latin line rate 0.0355 |
| 14 | `μαλακία is attributed to the Scythian kings by Arist. Eth. N. 7. 7, 6.` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p000494-l0145.png | 3 consecutive numeric tokens; latin line rate 0.0355 |
| 15 | `Κάσσ. 39, 6, 2). Τὸ illius εἶναι γένους οὐδετέρου (sceleris illius), ὄχι ἀρσενι·` | docs/records/harvest/harvest_big/round1/crops/2b1d2b5340150ddc135a2b1a/p000099-l0025.png | 3 consecutive numeric tokens; greek_latin_cs line rate 0.0255 |
| 16 | `ἐπούρωσις, εως, ή, a dub. word in Arist. Rhet. 3. 13, 5, prob. a speed-` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p000590-l0126.png | 3 consecutive numeric tokens; latin line rate 0.0355 |
| 17 | `Απ. 2. 8, 7; τῷ κοινῷ σ. adapted to a commonwealth, of bees, Plut.` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p001491-l0005.png | 3 consecutive numeric tokens; latin line rate 0.0355 |
| 18 | `ἄσπρις, ἡ, a kind of oak, Theophr. H. P. 3. 8, 7.` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p000256-l0017.png | 3 consecutive numeric tokens; latin line rate 0.0355 |
| 19 | `-Mostly poët., but used by Hipp. (v. supr.) and Arist. Meteor. 2. 8, 26.,` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p000289-l0122.png | 3 consecutive numeric tokens; latin line rate 0.0355 |
| 20 | `each go of himself, 11. 17. 254; σπεύδοντα καὶ αὐτὸν ὀτρύνεις 8. 293;` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p000276-l0043.png | 3 consecutive numeric tokens; greek_latin_cs line rate 0.0255 |

### bibliographic (850 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `Ο Εθνικός Νόμος περί Ασφάλισης Υγείας (2008) προσδιορίζει τις πιο` | docs/records/harvest/harvest_big/openarchives/crops/51db636c/p000066-l0017.png | patterns ['year_in_parens']; greek_mono line rate 0.0015 |
| 2 | `рији Карађорђев устанак (1804) подмлађен најпре млађим` | docs/records/harvest/harvest_big/cyrillic/crops/7235f8d0/p000168-l0012.png | patterns ['year_in_parens']; cyrillic line rate 0.0012 |
| 3 | `Ehrsson, Y. T., Langius-Eklöf, A., & Laurell, G. (2012). Nutritional surveillance and` | docs/records/harvest/harvest_big/mixed/crops/df20db94/p000179-l0031.png | patterns ['year_in_parens']; latin line rate 0.0327 |
| 4 | `(1) Juris Graeco-Romani σ. 100.` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000137-l0030.png | patterns ['σ.+number']; latin line rate 0.0327 |
| 5 | `ANA). (2005). Scope and Standards of School Nursing Practice. Silver` | docs/records/harvest/harvest_big/openarchives/crops/982e0266/p000062-l0009.png | patterns ['year_in_parens']; latin line rate 0.0327 |
| 6 | `3 Federal Maritime Commission (2000). The Ocean Shipping Reform Act: An interim status report.` | docs/records/harvest/harvest_big/openarchives/crops/72da5586/p000059-l0039.png | patterns ['year_in_parens']; latin line rate 0.0327 |
| 7 | `11. Vulkaneifel European Geopark-Germany (2004)` | docs/records/harvest/harvest_big/mixed/crops/732cfbe1/p000131-l0016.png | patterns ['year_in_parens']; latin line rate 0.0327 |
| 8 | `Council of Europe (2000). Presidency Conclusions. Διαθέσιμο στο: https://www.euro` | docs/records/harvest/harvest_big/openarchives/crops/0b7fade4/p000128-l0023.png | patterns ['year_in_parens']; latin line rate 0.0327 |
| 9 | `брача није учествовао, а по пропасти (1813) остао је у` | docs/records/harvest/harvest_big/cyrillic/crops/7235f8d0/p000175-l0014.png | patterns ['year_in_parens']; cyrillic line rate 0.0012 |
| 10 | `Lamark (1744) καὶ τοῦ Cuvier (1769), ἀποτελεῖ τὴν τετάρ-` | docs/records/harvest/harvest_big/round1/crops/f0acb2fc3dab2a9bb69f8726/p000020-l0025.png | patterns ['year_in_parens']; greek_latin_cs line rate 0.0130 |
| 11 | `(2005), Techniques in Robotics for Evaluation and Rehabilitation of Upper` | docs/records/harvest/harvest_big/openarchives/crops/520de75a/p000127-l0009.png | patterns ['year_in_parens']; latin line rate 0.0327 |
| 12 | `ἔποψιν (ἴδε τὸ ἐπιχείρημα τῆς ἀντιθέτου γνώμης, ἀνωτέρω σ. 28, σημ. 1 ). Ὅπως,` | docs/records/harvest/harvest_big/round1/crops/8b231047fdbd96ec30e1eded/p000033-l0022.png | patterns ['σ.+number']; greek_poly line rate 0.0006 |
| 13 | `association, www.apa.org/pi/parent.html, University of Virginia 90 Ryan –Flood, R (2009),` | docs/records/harvest/harvest_big/openarchives/crops/a330e1fc/p000095-l0017.png | patterns ['year_in_parens']; latin line rate 0.0327 |
| 14 | `UNESCO (2005). UN Decade of Education for Sustainable Development 2005-2014,` | docs/records/harvest/harvest_big/openarchives/crops/5b6f51a1/p000145-l0022.png | patterns ['year_in_parens']; latin line rate 0.0327 |
| 15 | `Mollen, D., Ridley, C. R., & Hill, C. L. (2003). Models of multicultural competence:` | docs/records/harvest/harvest_big/openarchives/crops/c0cb6888/p000099-l0023.png | patterns ['year_in_parens']; latin line rate 0.0327 |
| 16 | `Επίσης ο Νιάκας (2002) αναφέρει ότι, στις μαιευτικές υπηρεσίες` | docs/records/harvest/harvest_big/openarchives/crops/51db636c/p000021-l0023.png | patterns ['year_in_parens']; greek_mono line rate 0.0015 |
| 17 | `Gelsleichter J, Walker CJ (2010) Pollutant exposure and effects in sharks and their relatives. In: Sharks and Their Relatives:` | docs/records/harvest/harvest_big/mixed/crops/f583aad3/p000492-l0058.png | patterns ['year_in_parens']; latin line rate 0.0327 |
| 18 | `Geld> 2 ἔκδ. σ. 179) ὑπελογίζετο ἡ κατὰ Ἰούνιον 1914 ἐν Γερμανίᾳ εὑρισκομένη` | docs/records/harvest/harvest_big/round1/crops/7cb612112b4f28a4f704a9cb/p000032-l0031.png | patterns ['σ.+number']; greek_poly line rate 0.0006 |
| 19 | `Хаџи-Продановим (1814), па после најмлађим кнеза Ми-` | docs/records/harvest/harvest_big/cyrillic/crops/7235f8d0/p000168-l0013.png | patterns ['year_in_parens']; cyrillic line rate 0.0012 |
| 20 | `14. Astroblème Châtaigneraie Limousine-France (2004)` | docs/records/harvest/harvest_big/mixed/crops/732cfbe1/p000131-l0019.png | patterns ['year_in_parens']; latin line rate 0.0327 |

### running_title_or_page_number (908 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `ΠΡΑΚΤΙΚΑ ΒΟΥΛΗΣ (ΟΛΟΜΕΛΕΙΑ)` | docs/records/harvest/harvest_big/parliament/crops/be486d8c/p000030-l0002.png | box y0=75 y1=136 of page h=4615 (in top/bottom 8%), 27 chars <= greek_mono p50 55, no lowercase letters |
| 2 | `ΣΥΝΕΔΡΙΑΣΗ Π' – 21 ΦΕΒΡΟΥΑΡΙΟΥ 1996` | docs/records/harvest/harvest_big/parliament/crops/18369cae/p000039-l0001.png | box y0=153 y1=200 of page h=4682 (in top/bottom 8%), 35 chars <= greek_mono p50 55, no lowercase letters |
| 3 | `ΣΥΝΕΔΡΙΑΣΙΣ Γ΄` | docs/records/harvest/harvest_big/parliament/crops/7aea9867/p000009-l0001.png | box y0=436 y1=501 of page h=7361 (in top/bottom 8%), 14 chars <= greek_mono p50 55, no lowercase letters |
| 4 | `ΓΕΩΡΓΙΟΣ ΖΑΛΟΚΩΣΤΑΣ` | docs/records/harvest/harvest_big/round1/crops/6df192e72b10d13c5fc1374a/p000027-l0033.png | box y0=91 y1=118 of page h=1433 (in top/bottom 8%), 19 chars <= greek_mono p50 55, no lowercase letters |
| 5 | `ΣΥΝΕΔΡΙΑΣΙΣ ΙΔ΄ - 31 ΟΚΤΩΒΡΙΟΥ 1979` | docs/records/harvest/harvest_big/parliament/crops/a65a813d/p000003-l0001.png | box y0=492 y1=560 of page h=7614 (in top/bottom 8%), 35 chars <= greek_mono p50 55, no lowercase letters |
| 6 | `ΑΝΑΣΧΕΔΙΑΣΜΟΣ ΕΠΙΧΕΙΡΗΣΙΑΚΩΝ ΔΙΑΔΙΚΑΣΙΩΝ` | docs/records/harvest/harvest_big/openarchives/crops/e2f49c6f/p000076-l0001.png | box y0=106 y1=128 of page h=2339 (in top/bottom 8%), 40 chars <= greek_mono p50 55, no lowercase letters |
| 7 | `КІЕВСКАЯ СТАРИНА.` | docs/records/harvest/harvest_big/cyrillic/crops/0b4bf868/p000937-l0002.png | box y0=85 y1=98 of page h=1378 (in top/bottom 8%), 17 chars <= cyrillic p50 53, no lowercase letters |
| 8 | `ΕΦΗΜΕΡΙΣ ΤΩΝ ΣΥΖΗΤΗΣΕΩΝ` | docs/records/harvest/harvest_big/vouli/crops/8392b35378bd/p000001-l0002.png | box y0=148 y1=213 of page h=4863 (in top/bottom 8%), 23 chars <= greek_mono p50 55, no lowercase letters |
| 9 | `ΠΡΑΚΤΙΚΑ ΒΟΥΛΗΣ (ΤΜΗΜΑ ΔΙΑΚΟΠΗΣ ΕΡΓΑΣΙΩΝ ΒΟΥΛΗΣ)` | docs/records/harvest/harvest_big/parliament/crops/7a1452d8/p000016-l0002.png | box y0=90 y1=153 of page h=4602 (in top/bottom 8%), 48 chars <= greek_mono p50 55, no lowercase letters |
| 10 | `Π. Σ. ΣΥΝΟΔΙΝΟΥ` | docs/records/harvest/harvest_big/round2/crops/b518f9/p000227-l0002.png | box y0=80 y1=103 of page h=1654 (in top/bottom 8%), 15 chars <= greek_mono p50 55, no lowercase letters |
| 11 | `ΠΡΑΚΤΙΚΑ ΒΟΥΛΗΣ (ΟΛΟΜΕΛΕΙΑ` | docs/records/harvest/harvest_big/parliament/crops/20900789/p000006-l0083.png | box y0=434 y1=534 of page h=7552 (in top/bottom 8%), 26 chars <= greek_mono p50 55, no lowercase letters |
| 12 | `ΓΕΩΡΓΙΟΣ Φ. ΦΩΤΙΑΔΗΣ` | docs/records/harvest/harvest_big/openarchives/crops/0b63328a/p000155-l0003.png | box y0=100 y1=120 of page h=2339 (in top/bottom 8%), 20 chars <= greek_mono p50 55, no lowercase letters |
| 13 | `Α. Δ. ΝΙΚΟΛΑΡΑ` | docs/records/harvest/harvest_big/round1/crops/cc0e056392dd2ef4916b3e7d/p000095-l0001.png | box y0=67 y1=83 of page h=1417 (in top/bottom 8%), 14 chars <= greek_mono p50 55, no lowercase letters |
| 14 | `AESOPI FABVLAE` | docs/records/harvest/harvest_big/wikisource/crops/602cc72e/p000167-l0001.png | box y0=111 y1=161 of page h=3500 (in top/bottom 8%), 14 chars <= latin p50 61, no lowercase letters |
| 15 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000089-l0035.png | box y0=1259 y1=1503 of page h=1504 (in top/bottom 8%), 19 chars <= greek_mono p50 55, no lowercase letters |
| 16 | `ΠΑΝΕΠΙΣΤΗΜΙΟ` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000012-l0033.png | box y0=1283 y1=1447 of page h=1506 (in top/bottom 8%), 12 chars <= greek_mono p50 55, no lowercase letters |
| 17 | `ΗΡΩΕΣ Η ΗΜΙΘΕΟΙ.` | docs/records/harvest/harvest_big/mixed/crops/34d2967a/p000151-l0001.png | box y0=63 y1=91 of page h=1306 (in top/bottom 8%), 16 chars <= greek_mono p50 55, no lowercase letters |
| 18 | `ΣΥΝΕΔΡΙΑΣΗ ΜΕ΄ - 8 ΔΕΚΕΜΒΡΙΟΥ 1983` | docs/records/harvest/harvest_big/parliament/crops/3be8f3b1/p000021-l0001.png | box y0=596 y1=686 of page h=7552 (in top/bottom 8%), 34 chars <= greek_mono p50 55, no lowercase letters |
| 19 | `ΝΙΚΟΣ ΦΑΡΜΑΚΗΣ"` | docs/records/harvest/harvest_big/parliament/crops/de9da003/p000005-l0067.png | box y0=4387 y1=4438 of page h=4678 (in top/bottom 8%), 15 chars <= greek_mono p50 55, no lowercase letters |
| 20 | `ΣΥΝΕΔΡΙΑΣΙΣ Λ' - 31 ΑΥΓΟΥΣΤΟΥ 1979` | docs/records/harvest/harvest_big/parliament/crops/1d27927c/p000027-l0001.png | box y0=524 y1=592 of page h=7638 (in top/bottom 8%), 34 chars <= greek_mono p50 55, no lowercase letters |

### final_sigma_error (452 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `ποὺ οἱ ναῦτεςτου ἀντιμάχονται γιὰ νὰμὴν πέσουν σκλάβοι.` | docs/records/harvest/harvest_big/round2/crops/a0b5d8/p000030-l0008.png | 0 word-final σ + 1 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['οἱ ναῦτεςτο']); greek_poly line rate 0.0023 |
| 2 | `Δήμου Θεσ/νίκης, σας πληροφορούμε τα εξής:` | docs/records/harvest/harvest_big/parliament/crops/f1cf6e4b/p000006-l0138.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['Δήμου Θεσ/ν']); greek_mono line rate 0.0003 |
| 3 | `Τὰ διανεμητέα εἰς τοὺς δήμουςποσὰ προσδιορίζονται ὡς ἑξῆς:` | docs/records/harvest/harvest_big/vouli/crops/92d580f394fe/p000002-l0020.png | 0 word-final σ + 1 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ὺς δήμουςπο']); greek_poly line rate 0.0023 |
| 4 | `τὰς σχέσεις αὐτοῦ πρὸς τὸ φυσ φυσικόν Δίκαιον καὶ` | docs/records/harvest/harvest_big/round1/crops/8e3c482e1f6c81bb67f24395/p000020-l0066.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ὸς τὸ φυσ φ']); greek_poly line rate 0.0023 |
| 5 | `εὐεργετικοὺς σκοποὺς διὰ τὴν ἀποκατάςασιν τῶν ἑλληνικῶν` | docs/records/harvest/harvest_big/vouli/crops/68ff7ed0985f/p000004-l0014.png | 0 word-final σ + 1 word-internal ς (of which 1 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx [' ἀποκατάςασ']); greek_poly line rate 0.0023 |
| 6 | `ΔΕΩΝ ΚΑΛΛΕΡΓΗΣ ἀρχηγὸς τῶν Κρητῶν ἀποςατῶν.` | docs/records/harvest/harvest_big/round1/crops/723c450ea9bb07fc4cdf47f9/p000024-l0002.png | 0 word-final σ + 1 word-internal ς (of which 1 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ητῶν ἀποςατ']); greek_poly line rate 0.0023 |
| 7 | `- Θυμᾶσ' ὅταν σὲ φύτευα γελοιοῦντας τραλουδοῦντας,` | docs/records/harvest/harvest_big/round1/crops/42c339ce492d83665f00774d/p000032-l0036.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ["- Θυμᾶσ' "]); greek_poly line rate 0.0023 |
| 8 | `εἰς πρόσωπον, ἀπεῤῥόφησε σύμπασαν τὴν κοσμικὴν ἐκκλησιαςικὴν` | docs/records/harvest/harvest_big/vouli/crops/3445120e6970/p000005-l0009.png | 0 word-final σ + 1 word-internal ς (of which 1 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ἐκκλησιαςικ']); greek_poly line rate 0.0023 |
| 9 | `ταῦτά γ᾿ ἀπολάχωσ᾽ οἴκων πατρός that they may obtain.., Eur. H. F.` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p000208-l0166.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx [' ἀπολάχωσ᾽ ']); greek_latin_cs line rate 0.0014 |
| 10 | `διδοῦσ᾽, ἐπεί με γᾶς·` | docs/records/harvest/harvest_big/round1/crops/bf2ce6d100950eec319cef00/p000023-l0044.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['διδοῦσ᾽,']); greek_poly line rate 0.0023 |
| 11 | `᾿Ανὴρ ἄνδρασ καὶ πόλις πόλιν σώζει. – Ἡ κακή` | docs/records/harvest/harvest_big/round1/crops/c20219eff76f2fbc39f4c6fd/p000021-l0050.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ὴρ ἄνδρασ κ']); greek_poly line rate 0.0023 |
| 12 | `Σκοτείνιασ᾽ οὐρανὸς καὶ γῆ, ἀνατολὴ καὶ δύση.` | docs/records/harvest/harvest_big/round2/crops/cbdbe3/p000052-l0009.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['κοτείνιασ᾽ ']); greek_poly line rate 0.0023 |
| 13 | `» Σὰ σπόρος, ποῦ δὲ σέπεται θαμμένος μὲς ἐσ τὸ χιόνι·` | docs/records/harvest/harvest_big/round1/crops/ef44b5f8b81d770825ea1475/p000036-l0018.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ος μὲς ἐσ τ']); greek_poly line rate 0.0023 |
| 14 | `διώκουσ' οἱ δεσμόται !` | docs/records/harvest/harvest_big/wikisource/crops/8b6b0de9/p000018-l0015.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ["διώκουσ' "]); greek_poly line rate 0.0023 |
| 15 | `· Διὰ τὸ γραφ. τῆς ἐν Κωνςαντινουπόλει πρεσβείας δρ. 10,000` | docs/records/harvest/harvest_big/vouli/crops/d9b7dfa900e3/p000015-l0002.png | 0 word-final σ + 1 word-internal ς (of which 1 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ς ἐν Κωνςαν']); greek_poly line rate 0.0023 |
| 16 | `ν᾿ ἀπαλειφθῶσιν ἐκ τῶν φύλλων λεπτομερείας, ὡς οὖσαι προσ·` | docs/records/harvest/harvest_big/vouli/crops/23e59c57bd30/p000009-l0033.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ὖσαι προσ·']); greek_poly line rate 0.0023 |
| 17 | `ἅπλωσ᾽ ἐδῶ τ' ἀγαπημένο χέρι` | docs/records/harvest/harvest_big/round1/crops/6df192e72b10d13c5fc1374a/p000126-l0045.png | 1 word-final σ + 0 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ἅπλωσ᾽ ']); greek_poly line rate 0.0023 |
| 18 | `Εὐςρ. Μ. Παρίσσης.` | docs/records/harvest/harvest_big/vouli/crops/d9b7dfa900e3/p000016-l0013.png | 0 word-final σ + 1 word-internal ς (of which 1 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['Εὐςρ.']); greek_poly line rate 0.0023 |
| 19 | `ναςρίζας τῶν νωτιαίων νεύρων, τὰς προσθίας καὶ ὀπισθίας.` | docs/records/harvest/harvest_big/round2/crops/6dd672/p000023-l0020.png | 0 word-final σ + 1 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['ναςρί']); greek_poly line rate 0.0023 |
| 20 | `νοοῦσα καὶ ἦλθεν εἰς τὸν ναὸν τῆς Εὐαγγελισρίαςμετὰ δακρύων` | docs/records/harvest/harvest_big/round1/crops/460b94bc8e2c58a95074382b/p000023-l0008.png | 0 word-final σ + 1 word-internal ς (of which 0 where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) (ctx ['γελισρίαςμε']); greek_poly line rate 0.0023 |

### spacing_apostrophe (10,157 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `Ἐν ᾿Αθήναις τῇ 15 Δεκεμβρίου 1979` | docs/records/harvest/harvest_big/parliament/crops/1a035976/p000008-l0044.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 2 | `νομίμως καὶ ὡς ἁρμόζει εἰς ἀκαδημαϊκοὺς πολίτας. ᾿Επιβάλλεται ἵνα ἐπιμεί-` | docs/records/harvest/harvest_big/round2/crops/0efd67/p000093-l0022.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 3 | `τέχει μεγάλην θέσιν ἐν τῷ βίῳ τῶν ᾿Αλβανῶν, λέγει ὁ René Pinon La` | docs/records/harvest/harvest_big/mixed/crops/b7de2754/p000007-l0059.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_latin_cs line rate 0.0205 |
| 4 | `τῆς ᾿Αγγλίας καὶ Πρόεδρον τῆς ἐν Λονδίνῳ Συνδιασκέψεως τῶν Πρεσβευτῶν τῶν Μεγάλων` | docs/records/harvest/harvest_big/round1/crops/2c8742589d947f8d749c7ba2/p000043-l0093.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 5 | `Ποῦ πολεμᾷ Δεμὶρ ᾿Αγᾶς σὰν ἄξιο παλληκάρι.»` | docs/records/harvest/harvest_big/round1/crops/3a65f68ff36d911f4ca179e8/p000129-l0012.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 6 | `τῆς ᾿Αττικῆς, Μεγαρίδος καὶ τῆς ἐν τῷ Κορινθιακῷ κόλπῳ` | docs/records/harvest/harvest_big/round1/crops/eed91c3c88be77cac51e7629/p000094-l0015.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 7 | `ξαν, ἐλᾶτε, ἐμβῆτε μέσα. ᾿Αλλά νὰ μοῦ` | docs/records/harvest/harvest_big/round1/crops/2f9e996ffbdaaa3b4a9dfdcf/p000082-l0017.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 8 | `μέτρῳ» (᾿Απόκρ. τη΄ Βαρσανουφίου καὶ Ἰωάννου ἐρωταποκρίσεις. Ενετίησιν 1816).` | docs/records/harvest/harvest_big/round2/crops/adc48c/p000047-l0035.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 9 | `᾿Αλλ᾿ ἀπέδειξα τάχα τὴ θεωρία μου πρὸς εὐχαρίστησή σου;` | docs/records/harvest/harvest_big/round2/crops/32aae9/p000026-l0005.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 10 | `σταντινουπόλεως μέχρι τοῦ Ἔβρου ποταμοῦ. ᾿Αρ-` | docs/records/harvest/harvest_big/round2/crops/290a13/p000238-l0003.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 11 | `ἐν ἀγνοίᾳ εὑρίσκεται ὁ στρατιώτης, αἱ ἄδειαι, ὁ θάνατος, ἡ τὸν ᾿Απρίλιον 385, τὸν Μάϊον 528, τὸν Ἰούνιον 516, ήτοι ἐν` | docs/records/harvest/harvest_big/vouli/crops/5090074e9fac/p000008-l0023.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 12 | `ΠΡΟΕΔΡΟΣ (Ιωάννης Ν. ᾿Αλευρᾶς). Ὁ κ. Ὑπουργός` | docs/records/harvest/harvest_big/parliament/crops/13dcc39a/p000003-l0117.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 13 | `*᾿Ανω (καταλαμβάνω, ἀκούω, αἰσθάνομαι), μτγν. καὶ ποιητ.` | docs/records/harvest/harvest_big/round1/crops/727f1e3f8d0a3a622943e9b1/p000012-l0021.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 14 | `μῳδίᾳ τοῦ ἀθανάτου ᾿Αριστοφάνους. Ἡ φωνή` | docs/records/harvest/harvest_big/wikisource/crops/263438a3/p000013-l0044.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 15 | `δυνάμεως καὶ δι᾽ ὑπερτάτης ἀνδρείας. ᾿Αντὶ νὰ ἀντι-` | docs/records/harvest/harvest_big/round1/crops/1118b0c89e773062b4cf69f5/p000216-l0027.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 16 | `Εὐρώπης, τῆς ᾿Ασίας καὶ τῆς ᾿Αφρικῆς, ἐκυριεύθη ὑπὸ` | docs/records/harvest/harvest_big/round1/crops/d8dfd78fb29485b6707ae96c/p000004-l0029.png | 0 standing alone + 2 word-initial before a letter {'U+1FBF psili before capital': 2}; greek_poly line rate 0.0536 |
| 17 | `ὕμν. Ἑρμ. 367, εὐκτ. ἐν-δείξαιτο Εὐρ. ᾿Αλκ. 154, ἀπαρ. ἀποδέξασθαι` | docs/records/harvest/harvest_big/round1/crops/1697d5cc21fa26717b97e073/p000055-l0092.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 18 | `΄ Διαδικασία συνοπτική` | docs/records/harvest/harvest_big/mixed/crops/d0eda948/p000542-l0002.png | 1 standing alone + 0 word-initial before a letter {'U+0384 tonos': 1}; greek_mono line rate 0.0051 |
| 19 | `ιδ'. Δόξαι φιλοσόφων περὶ ἀρχῶν. ᾿Απὸ τῶν` | docs/records/harvest/harvest_big/round2/crops/a300f5/p000103-l0054.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |
| 20 | `Νότια ᾿Αφρικὴ μὲ τὸ δίκιο τους θὰ ζητήσουν τὰ ἴδια προ-` | docs/records/harvest/harvest_big/mixed/crops/0aac601a/p000022-l0048.png | 0 standing alone + 1 word-initial before a letter {'U+1FBF psili before capital': 1}; greek_poly line rate 0.0536 |

### line_end_not_sign (0 lines)

_none_

### dictionary_like (1,228 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `μα: Γίνεται δεκτή η πρόταση του Προεδρείου;` | docs/records/harvest/harvest_big/parliament/crops/be486d8c/p000046-l0077.png | headword + dash/colon at line start; greek_mono line rate 0.0054 |
| 2 | `наль: канализирамъ; -ег,` | docs/records/harvest/harvest_big/cyrillic/crops/94847f75/p000295-l0084.png | headword + dash/colon at line start; cyrillic line rate 0.0081 |
| 3 | `оказалось - сборныхъ въ Петропавловскомъ` | docs/records/harvest/harvest_big/cyrillic/crops/9a32fb66/p000118-l0040.png | headword + dash/colon at line start; cyrillic line rate 0.0081 |
| 4 | `οδηγίας: Είναι απογραφή έναρξης. απογραφή λήξης, κίνη-` | docs/records/harvest/harvest_big/parliament/crops/3be8f3b1/p000015-l0135.png | headword + dash/colon at line start; greek_mono line rate 0.0054 |
| 5 | `ἐκχωρεῖν – νὰ παραχωρῶσι τὴν θέσιν των. - μάλιστα=παρὰ` | docs/records/harvest/harvest_big/round1/crops/1495fc2311427a558abbfd88/p000063-l0073.png | headword + dash/colon at line start; greek_poly line rate 0.0026 |
| 6 | `Πηγή: Πληροφοριακό σύστημα myschool (Ιαν.2017), επεξεργασία: Παρατηρητήριο Μαθητικής` | docs/records/harvest/harvest_big/openarchives/crops/0a40e453/p000027-l0018.png | headword + dash/colon at line start; greek_latin_cs line rate 0.0076 |
| 7 | `ες: εκπομπή εδάφους,` | docs/records/harvest/harvest_big/openarchives/crops/bc17a162/p000071-l0025.png | headword + dash/colon at line start; greek_mono line rate 0.0054 |
| 8 | `DataOption:=xlSortNormal)` | docs/records/harvest/harvest_big/mixed/crops/a85515c7/p000313-l0024.png | headword + dash/colon at line start; latin line rate 0.0109 |
| 9 | `χώρους– γιατὶ αὐτὴ ἡ θέση τοῦ Ὑπουργείου Ἐμπορίου νὰ·` | docs/records/harvest/harvest_big/parliament/crops/f47c50c8/p000018-l0049.png | headword + dash/colon at line start; greek_poly line rate 0.0026 |
| 10 | `• Νηπιαγωγείο: Παρατηρώ τον εαυτό μου, Φροντίζω το σώμα μου, Πώς ήρθα` | docs/records/harvest/harvest_big/openarchives/crops/c7d62b6a/p000038-l0012.png | headword + dash/colon at line start; greek_mono line rate 0.0054 |
| 11 | `θησαυρὸν : χρυσὸς, ἄργυρος, σμάραγδος, μαργαρίτης, ἔβε-` | docs/records/harvest/harvest_big/mixed/crops/fa6c4ad0/p000129-l0012.png | headword + dash/colon at line start; greek_poly line rate 0.0026 |
| 12 | `νον - ἐνῷ ἐκαθήμεθα ἐπὶ τοῦ φραγμοῦ τοῦ βλέποντος τὸν Κετσουρένειον` | docs/records/harvest/harvest_big/round1/crops/cbe5e7b92d36edf08153017b/p000220-l0012.png | headword + dash/colon at line start; greek_poly line rate 0.0026 |
| 13 | `νται: Η Επιτροπή Απόδημου Ελληνισμού, καλή είναι και είναι` | docs/records/harvest/harvest_big/parliament/crops/29bccf95/p000047-l0097.png | headword + dash/colon at line start; greek_mono line rate 0.0054 |
| 14 | `Conclusions: The methodological quality of reviewed RCT's studies was low and many failed to provide sufficient information in order to assess` | docs/records/harvest/harvest_big/mixed/crops/70165e43/p000334-l0029.png | headword + dash/colon at line start; latin line rate 0.0109 |
| 15 | `του: Δεν μιλάω για το τι θα γίνει σε 6 μήνες ή ένα χρόνο.` | docs/records/harvest/harvest_big/parliament/crops/7b996aa5/p000032-l0045.png | headword + dash/colon at line start; greek_mono line rate 0.0054 |
| 16 | `мовича: первая 11 ноября 1743 г. и, нода, о представленіи Кабинету Ея Импе-` | docs/records/harvest/harvest_big/cyrillic/crops/9a32fb66/p000140-l0043.png | headword + dash/colon at line start; cyrillic line rate 0.0081 |
| 17 | `rivations:-Ζεὺς Μόριος was the guardian of these sacred olives, Soph.` | docs/records/harvest/harvest_big/mixed/crops/4c207e1e/p001000-l0161.png | headword + dash/colon at line start; latin line rate 0.0109 |
| 18 | `νισμένη – δικός σας ο όρος, δική μου η χρήση – απάντη-` | docs/records/harvest/harvest_big/parliament/crops/c72a5c9e/p000012-l0076.png | headword + dash/colon at line start; greek_mono line rate 0.0054 |
| 19 | `πλοίου: Πῶς θὰ ἔχουμε καινούργιο νεότευκτο πλοῖο; Πῶς` | docs/records/harvest/harvest_big/parliament/crops/48a58eb5/p000061-l0101.png | headword + dash/colon at line start; greek_poly line rate 0.0026 |
| 20 | `ничнитѣ: посредствомъ избиване ларвитѣ на скакалцитѣ още` | docs/records/harvest/harvest_big/cyrillic/crops/252fd568/p000185-l0005.png | headword + dash/colon at line start; cyrillic line rate 0.0081 |

### digitisation_stamp (83 lines)

| # | label | crop_path | reason |
|---:|---|---|---|
| 1 | `ΠΑΝΕΠΙΣΤΗΜΙ` | docs/records/harvest/harvest_big/round1/crops/96bb7196d840fe7513c2ed43/p000038-l0063.png | label is a library/digitiser stamp; box 62x157px at y_rel 0.913 |
| 2 | `ΒΙΒΛΙΟΘΗΚΗ` | docs/records/harvest/harvest_big/round1/crops/b8b71bfd410ddd2e68429ffe/p000018-l0035.png | label is a library/digitiser stamp; box 226x48px at y_rel 0.075 |
| 3 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000081-l0034.png | label is a library/digitiser stamp; box 192x245px at y_rel 0.918 |
| 4 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/ffe26907d1e3e9c1f75337e2/p000285-l0001.png | label is a library/digitiser stamp; box 198x242px at y_rel 0.919 |
| 5 | `ΠΑΝΕΠΙΣΤΗΜΙΟ` | docs/records/harvest/harvest_big/round1/crops/55beb2ad05d46b48576a486d/p000017-l0109.png | label is a library/digitiser stamp; box 309x42px at y_rel 0.852 |
| 6 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000023-l0032.png | label is a library/digitiser stamp; box 194x243px at y_rel 0.927 |
| 7 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000026-l0001.png | label is a library/digitiser stamp; box 195x243px at y_rel 0.927 |
| 8 | `ΠΑΝΕΠΙΣΤΗΜΙΟ` | docs/records/harvest/harvest_big/round1/crops/f07e2d5bdef7328dfb1671bf/p000070-l0035.png | label is a library/digitiser stamp; box 57x168px at y_rel 0.92 |
| 9 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/ffe26907d1e3e9c1f75337e2/p000247-l0001.png | label is a library/digitiser stamp; box 190x241px at y_rel 0.92 |
| 10 | `ΒΙΒΛΙΟΘΗΚΗ` | docs/records/harvest/harvest_big/round1/crops/6976af7d6e1671818ccf9781/p000018-l0069.png | label is a library/digitiser stamp; box 206x28px at y_rel 0.909 |
| 11 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000040-l0031.png | label is a library/digitiser stamp; box 195x242px at y_rel 0.927 |
| 12 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗ` | docs/records/harvest/harvest_big/round1/crops/8a77bd3f3cff4d5e3bec99f0/p000031-l0001.png | label is a library/digitiser stamp; box 185x242px at y_rel 0.919 |
| 13 | `ΠΑΝΕΠΙΣΤΗΜΙΟ` | docs/records/harvest/harvest_big/round1/crops/f07e2d5bdef7328dfb1671bf/p000062-l0033.png | label is a library/digitiser stamp; box 58x171px at y_rel 0.92 |
| 14 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/db1ed5f902d696fb53656a7d/p000056-l0001.png | label is a library/digitiser stamp; box 195x243px at y_rel 0.927 |
| 15 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/ffe26907d1e3e9c1f75337e2/p000026-l0001.png | label is a library/digitiser stamp; box 194x243px at y_rel 0.919 |
| 16 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/ffe26907d1e3e9c1f75337e2/p000045-l0001.png | label is a library/digitiser stamp; box 193x243px at y_rel 0.919 |
| 17 | `ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ` | docs/records/harvest/harvest_big/round1/crops/6976af7d6e1671818ccf9781/p000018-l0068.png | label is a library/digitiser stamp; box 336x38px at y_rel 0.885 |
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

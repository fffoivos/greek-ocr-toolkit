# BENCH02H — edition-cap / forced-pool diagnostic sweep

Offline metadata only; network OFF, no spend. Production defaults remain edition cap 4 / series cap 12, forced editions excluded. No admission or benchmark qualification.

Dry uses exactly the sole split-identity reason. **UPPER BOUND (not admitted)** uses all W1/W2 split rows regardless of census verdict, retaining the classifier, exclusions, seeded draw order and 20% overdraw. Exact registered locked/eval rows are excluded in every pool. Forced editions are identified by exact registered N1/LQB row membership and must already be forced test editions. No train/dev edition is reassigned.

Credit = min(drawn, class quota); class filled means aggregate deficit zero, as in BENCH02G. Language/font subgroup deficits remain separate and cannot be substituted. Edition/source counts, edition maxima and top-five shares describe all drawn candidates, including overdraw. Caps are global across classes and both splits. Unlimited disables both edition and series caps. No series is invented when metadata is absent.

Smallest change that fills ≥ 14/16 test classes in the upper bound: 100/lqb. Search order: increasing cap, then none/n1/lqb/both; this is a numerical ordering, not a recommendation.

Best is ranked by test classes filled, test credit, dev classes filled, then dev credit; ties retain sweep order. Classes are reported test/dev separately.

BENCH02G default candidates reproduced byte-identically: `5cd95d9dc07edec2abe63c9ec3a8cc238b8104d79b7cfe4532c4d89de26b48a3`. Sweep checks: 48 combinations, zero locked-row intersections, zero edition/series cap violations.

Input caveat retained from BENCH02G: tags have a locally measured checksum, but the extract receipt has no coordinator-pinned output checksum. This upper bound cannot establish census_05 admission supply. Book diversity uses distinct edition IDs (gazette issues count as editions); the ≥10 editions / ≥3 sources diagnostic does not establish independent canonical works.

## Pool additions

Rows added before class selection/caps, excluding every exact registered locked/eval ID. Classified additions are the drawable primary-class subset. Membership counts: {'n1': 46, 'lqb': 53}.

| Rule | Pool | N1 rows added | LQB rows added | N1 classified | LQB classified |
|---|---|---:|---:|---:|---:|
| dry | none | 0 | 0 | 0 | 0 |
| dry | n1 | 5221 | 0 | 5172 | 0 |
| dry | lqb | 0 | 14293 | 0 | 14205 |
| dry | both | 5221 | 14293 | 5172 | 14205 |
| upper_bound | none | 0 | 0 | 0 | 0 |
| upper_bound | n1 | 8920 | 0 | 8702 | 0 |
| upper_bound | lqb | 0 | 42632 | 0 | 42253 |
| upper_bound | both | 8920 | 42632 | 8702 | 42253 |

## Dry — sole split reason

| Cap | Pool | Test credit /2460 | Dev credit /615 | Filled T/D /16 | Deficit T/D | Max edition T/D | Test top5 share | Diversity classes T/D | Subgroup-qualified T/D |
|---|---|---:|---:|---|---|---|---:|---|---|
| 4 | none | 171 | 146 | 0/4 | 2289/469 | 4/4 | 11.70% (20/171) | 2/2 | 0/4 |
| 4 | n1 | 323 | 146 | 2/4 | 2137/469 | 4/4 | 5.76% (20/347) | 3/2 | 2/4 |
| 4 | lqb | 336 | 146 | 2/4 | 2124/469 | 4/4 | 5.32% (20/376) | 4/2 | 2/4 |
| 4 | both | 491 | 146 | 3/4 | 1969/469 | 4/4 | 3.63% (20/551) | 4/2 | 3/4 |
| 12 | none | 400 | 308 | 2/8 | 2060/307 | 12/12 | 14.85% (60/404) | 3/3 | 1/8 |
| 12 | n1 | 795 | 308 | 5/8 | 1665/307 | 12/12 | 6.67% (60/899) | 4/3 | 5/8 |
| 12 | lqb | 818 | 308 | 6/8 | 1642/307 | 12/12 | 6.36% (60/943) | 7/3 | 6/8 |
| 12 | both | 1258 | 308 | 7/8 | 1202/307 | 12/12 | 4.24% (60/1416) | 7/3 | 7/8 |
| 25 | none | 667 | 325 | 4/8 | 1793/290 | 25/25 | 17.29% (125/723) | 4/4 | 3/8 |
| 25 | n1 | 1239 | 325 | 8/8 | 1221/290 | 25/25 | 8.54% (125/1463) | 5/4 | 8/8 |
| 25 | lqb | 1337 | 325 | 9/8 | 1123/290 | 25/25 | 7.89% (125/1585) | 7/4 | 9/8 |
| 25 | both | 1366 | 325 | 9/8 | 1094/290 | 25/25 | 7.74% (125/1614) | 8/4 | 9/8 |
| 50 | none | 1035 | 344 | 6/9 | 1425/271 | 50/50 | 21.48% (250/1164) | 5/5 | 5/9 |
| 50 | n1 | 1290 | 344 | 9/9 | 1170/271 | 50/50 | 16.25% (250/1538) | 7/5 | 9/9 |
| 50 | lqb | 1602 | 344 | 11/9 | 858/271 | 50/50 | 13.19% (250/1895) | 8/5 | 11/9 |
| 50 | both | 1615 | 344 | 11/9 | 845/271 | 50/50 | 13.12% (250/1906) | 8/5 | 11/9 |
| 100 | none | 1136 | 344 | 7/9 | 1324/271 | 100/56 | 33.05% (433/1310) | 5/5 | 6/9 |
| 100 | n1 | 1410 | 344 | 9/9 | 1050/271 | 100/56 | 27.32% (453/1658) | 7/5 | 9/9 |
| 100 | lqb | 1605 | 344 | 11/9 | 855/271 | 100/56 | 18.12% (346/1909) | 8/5 | 11/9 |
| 100 | both | 1617 | 344 | 11/9 | 843/271 | 100/56 | 17.33% (333/1921) | 8/5 | 11/9 |
| unlimited | none | 1136 | 344 | 7/9 | 1324/271 | 109/56 | 33.66% (441/1310) | 5/5 | 6/9 |
| unlimited | n1 | 1419 | 344 | 9/9 | 1041/271 | 133/56 | 29.69% (495/1667) | 7/5 | 9/9 |
| unlimited | lqb | 1605 | 344 | 11/9 | 855/271 | 111/56 | 18.65% (356/1909) | 8/5 | 11/9 |
| unlimited | both | 1617 | 344 | 11/9 | 843/271 | 110/56 | 17.60% (338/1921) | 8/5 | 11/9 |

## UPPER BOUND (not admitted)

| Cap | Pool | Test credit /2460 | Dev credit /615 | Filled T/D /16 | Deficit T/D | Max edition T/D | Test top5 share | Diversity classes T/D | Subgroup-qualified T/D |
|---|---|---:|---:|---|---|---|---:|---|---|
| 4 | none | 189 | 163 | 1/4 | 2271/452 | 4/4 | 10.20% (20/196) | 2/1 | 1/4 |
| 4 | n1 | 335 | 163 | 2/4 | 2125/452 | 4/4 | 5.33% (20/375) | 2/1 | 2/4 |
| 4 | lqb | 352 | 163 | 2/4 | 2108/452 | 4/4 | 5.10% (20/392) | 3/1 | 2/4 |
| 4 | both | 483 | 163 | 4/4 | 1977/452 | 4/4 | 3.55% (20/563) | 3/1 | 4/4 |
| 12 | none | 446 | 333 | 3/9 | 2014/282 | 12/12 | 11.86% (60/506) | 4/2 | 3/9 |
| 12 | n1 | 823 | 333 | 6/9 | 1637/282 | 12/12 | 6.20% (60/967) | 4/2 | 6/9 |
| 12 | lqb | 846 | 333 | 7/9 | 1614/282 | 12/12 | 5.95% (60/1009) | 6/2 | 7/9 |
| 12 | both | 1286 | 333 | 8/9 | 1174/282 | 12/12 | 4.07% (60/1474) | 6/2 | 8/9 |
| 25 | none | 770 | 350 | 6/9 | 1690/265 | 25/25 | 14.16% (125/883) | 6/4 | 6/9 |
| 25 | n1 | 1367 | 350 | 10/9 | 1093/265 | 25/25 | 7.65% (125/1635) | 6/4 | 10/9 |
| 25 | lqb | 1413 | 350 | 10/9 | 1047/265 | 25/25 | 7.44% (125/1681) | 10/4 | 10/9 |
| 25 | both | 1433 | 350 | 10/9 | 1027/265 | 25/25 | 7.35% (125/1701) | 10/4 | 10/9 |
| 50 | none | 1246 | 365 | 9/10 | 1214/250 | 50/50 | 16.93% (250/1477) | 9/8 | 9/10 |
| 50 | n1 | 1383 | 365 | 10/10 | 1077/250 | 50/50 | 15.14% (250/1651) | 9/8 | 10/10 |
| 50 | lqb | 2009 | 365 | 13/10 | 451/250 | 50/50 | 10.57% (250/2365) | 11/8 | 13/10 |
| 50 | both | 2051 | 365 | 13/10 | 409/250 | 50/50 | 10.39% (250/2407) | 12/8 | 13/10 |
| 100 | none | 1488 | 445 | 9/10 | 972/170 | 100/100 | 29.00% (500/1724) | 9/8 | 9/10 |
| 100 | n1 | 1617 | 445 | 10/10 | 843/170 | 100/100 | 26.53% (500/1885) | 10/8 | 10/10 |
| 100 | lqb | 2348 | 445 | 15/10 | 112/170 | 100/100 | 17.06% (479/2808) | 12/8 | 15/10 |
| 100 | both | 2348 | 445 | 15/10 | 112/170 | 100/100 | 16.92% (475/2808) | 12/8 | 15/10 |
| unlimited | none | 1676 | 468 | 10/11 | 784/147 | 338/124 | 42.39% (841/1984) | 9/8 | 10/11 |
| unlimited | n1 | 1940 | 468 | 12/11 | 520/147 | 299/124 | 40.57% (938/2312) | 11/8 | 12/11 |
| unlimited | lqb | 2348 | 468 | 15/11 | 112/147 | 126/124 | 18.59% (522/2808) | 12/8 | 15/11 |
| unlimited | both | 2348 | 468 | 15/11 | 112/147 | 123/124 | 18.30% (514/2808) | 12/8 | 15/11 |

## Per-class deficits and diversity

Each cell pair is test/dev; E/S are distinct editions/sources drawn. Diversity ✓ requires ≥10 editions AND ≥3 sources. Subgroup deficits are explicit JSON maps in the final column. Full precision and supply/overdraw counts are in sweep.json.

### dry — 4/none

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 0/2 | 240/58 | 0/2 | 0/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| greek_latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 11/24 | 189/26 | 7/19 | 3/1 | —/— | {} / {} |
| short | 0/3 | 120/27 | 0/3 | 0/1 | —/— | {} / {} |
| long | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| vertical_turned | 13/9 | 87/16 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 15/30 | 105/0 | 13/35 | 1/1 | —/— | {} / {} |
| leaders_dashes | 0/3 | 100/22 | 0/3 | 0/1 | —/— | {} / {} |
| font_extremes | 77/25 | 23/0 | 34/23 | 5/3 | ✓/✓ | {"large": 27, "small": 0} / {"large": 0, "small": 0} |
| degraded | 35/25 | 65/0 | 17/30 | 2/2 | —/— | {} / {} |
| curved_skewed | 20/25 | 80/0 | 14/25 | 3/3 | ✓/✓ | {} / {} |

### dry — 4/n1

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 0/2 | 240/58 | 0/2 | 0/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| greek_latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 18/24 | 182/26 | 13/19 | 3/1 | ✓/— | {} / {} |
| short | 0/3 | 120/27 | 0/3 | 0/1 | —/— | {} / {} |
| long | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| vertical_turned | 13/9 | 87/16 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 24/30 | 96/0 | 20/35 | 1/1 | —/— | {} / {} |
| leaders_dashes | 0/3 | 100/22 | 0/3 | 0/1 | —/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 64/23 | 6/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 51/30 | 2/2 | —/— | {} / {} |
| curved_skewed | 68/25 | 32/0 | 34/25 | 4/3 | ✓/✓ | {} / {} |

### dry — 4/lqb

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 0/2 | 240/58 | 0/2 | 0/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| greek_latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 22/24 | 178/26 | 14/19 | 3/1 | ✓/— | {} / {} |
| short | 0/3 | 120/27 | 0/3 | 0/1 | —/— | {} / {} |
| long | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| vertical_turned | 13/9 | 87/16 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 29/30 | 91/0 | 21/35 | 1/1 | —/— | {} / {} |
| leaders_dashes | 0/3 | 100/22 | 0/3 | 0/1 | —/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 58/23 | 10/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 55/30 | 6/2 | ✓/— | {} / {} |
| curved_skewed | 72/25 | 28/0 | 42/25 | 7/3 | ✓/✓ | {} / {} |

### dry — 4/both

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 1/2 | 239/58 | 1/2 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| greek_latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 97/24 | 103/26 | 61/19 | 3/1 | ✓/— | {} / {} |
| short | 0/3 | 120/27 | 0/3 | 0/1 | —/— | {} / {} |
| long | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| vertical_turned | 13/9 | 87/16 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 80/30 | 40/0 | 53/35 | 1/1 | —/— | {} / {} |
| leaders_dashes | 0/3 | 100/22 | 0/3 | 0/1 | —/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 59/23 | 10/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 88/30 | 7/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 89/25 | 8/3 | ✓/✓ | {} / {} |

### dry — 12/none

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 1/60 | 239/0 | 1/21 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 2/3 | 158/37 | 1/2 | 1/2 | —/— | {} / {} |
| greek_latin | 0/9 | 160/31 | 0/4 | 0/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 46/50 | 154/0 | 18/21 | 4/3 | ✓/✓ | {} / {} |
| short | 2/30 | 118/0 | 2/18 | 2/2 | —/— | {} / {} |
| long | 1/16 | 159/24 | 1/6 | 1/1 | —/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 79/30 | 41/0 | 31/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 1/25 | 99/0 | 1/18 | 1/2 | —/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 34/18 | 5/3 | ✓/✓ | {"large": 10, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 24/29 | 2/2 | —/— | {} / {} |
| curved_skewed | 51/25 | 49/0 | 25/16 | 4/4 | ✓/✓ | {} / {} |

### dry — 12/n1

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 44/60 | 196/0 | 16/21 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 2/3 | 158/37 | 1/2 | 1/2 | —/— | {} / {} |
| greek_latin | 4/9 | 156/31 | 4/4 | 1/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 160/50 | 40/0 | 56/21 | 5/3 | ✓/✓ | {} / {} |
| short | 30/30 | 90/0 | 22/18 | 3/2 | ✓/— | {} / {} |
| long | 18/16 | 142/24 | 10/6 | 2/1 | —/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 77/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 45/18 | 2/2 | —/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 55/18 | 6/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 54/29 | 2/2 | —/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 69/16 | 5/4 | ✓/✓ | {} / {} |

### dry — 12/lqb

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 28/60 | 212/0 | 11/21 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 4/3 | 156/37 | 3/2 | 3/2 | —/— | {} / {} |
| greek_latin | 4/9 | 156/31 | 4/4 | 1/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 56/21 | 8/3 | ✓/✓ | {} / {} |
| short | 22/30 | 98/0 | 16/18 | 4/2 | ✓/— | {} / {} |
| long | 23/16 | 137/24 | 12/6 | 3/1 | ✓/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 54/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 32/18 | 5/2 | ✓/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 53/18 | 10/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 48/29 | 8/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 55/16 | 9/4 | ✓/✓ | {} / {} |

### dry — 12/both

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 234/60 | 6/0 | 47/21 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 6/3 | 154/37 | 4/2 | 3/2 | —/— | {} / {} |
| greek_latin | 15/9 | 145/31 | 12/4 | 1/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 96/21 | 9/3 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 55/18 | 4/2 | ✓/— | {} / {} |
| long | 146/16 | 14/24 | 39/6 | 3/1 | ✓/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 104/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 75/18 | 5/2 | ✓/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 56/18 | 10/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 50/29 | 8/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 54/16 | 9/4 | ✓/✓ | {} / {} |

### dry — 25/none

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 45/60 | 195/0 | 10/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 3/3 | 157/37 | 1/2 | 1/2 | —/— | {} / {} |
| greek_latin | 3/9 | 157/31 | 3/4 | 1/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 86/50 | 114/0 | 22/22 | 4/4 | ✓/✓ | {} / {} |
| short | 15/30 | 105/0 | 8/19 | 3/2 | —/— | {} / {} |
| long | 7/33 | 153/7 | 4/6 | 2/1 | —/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 37/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 71/25 | 29/0 | 13/19 | 2/3 | —/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 34/18 | 5/3 | ✓/✓ | {"large": 8, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 26/17 | 3/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 33/16 | 5/4 | ✓/✓ | {} / {} |

### dry — 25/n1

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 46/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 5/3 | 155/37 | 2/2 | 2/2 | —/— | {} / {} |
| greek_latin | 13/9 | 147/31 | 9/4 | 1/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 57/22 | 5/4 | ✓/✓ | {} / {} |
| short | 84/30 | 36/0 | 40/19 | 3/2 | ✓/— | {} / {} |
| long | 160/33 | 0/7 | 25/6 | 2/1 | —/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 85/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 53/19 | 2/3 | —/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 52/18 | 6/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 58/17 | 4/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 73/16 | 6/4 | ✓/✓ | {} / {} |

### dry — 25/lqb

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 37/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 38/3 | 122/37 | 9/2 | 5/2 | —/— | {} / {} |
| greek_latin | 18/9 | 142/31 | 12/4 | 1/1 | —/— | {} / {} |
| historical_russian | 24/0 | 96/30 | 3/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 66/22 | 9/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 44/19 | 8/2 | ✓/— | {} / {} |
| long | 160/33 | 0/7 | 27/6 | 6/1 | ✓/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 61/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 42/19 | 6/3 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 53/18 | 10/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 47/17 | 8/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 50/16 | 10/4 | ✓/✓ | {} / {} |

### dry — 25/both

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 76/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 50/3 | 110/37 | 13/2 | 6/2 | ✓/— | {} / {} |
| greek_latin | 32/9 | 128/31 | 19/4 | 1/1 | —/— | {} / {} |
| historical_russian | 26/0 | 94/30 | 3/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 1/0 | 159/40 | 1/0 | 1/0 | —/— | {"bg": 40, "ru": 40, "sr": 39, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 80/22 | 9/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 65/19 | 9/2 | ✓/— | {} / {} |
| long | 160/33 | 0/7 | 53/6 | 7/1 | ✓/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 104/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 42/19 | 7/3 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 56/18 | 10/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 49/17 | 8/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 53/16 | 10/4 | ✓/✓ | {} / {} |

### dry — 50/none

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 19/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 5/3 | 155/37 | 2/2 | 2/2 | —/— | {} / {} |
| greek_latin | 8/9 | 152/31 | 5/4 | 1/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/12 | 160/28 | 0/1 | 0/1 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 187/50 | 13/0 | 25/22 | 5/4 | ✓/✓ | {} / {} |
| short | 42/30 | 78/0 | 15/21 | 4/3 | ✓/✓ | {} / {} |
| long | 16/40 | 144/0 | 6/8 | 2/2 | —/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 40/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 17/17 | 2/3 | —/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 34/18 | 5/3 | ✓/✓ | {"large": 8, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 26/17 | 3/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 33/15 | 5/4 | ✓/✓ | {} / {} |

### dry — 50/n1

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 60/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 12/3 | 148/37 | 3/2 | 3/2 | —/— | {} / {} |
| greek_latin | 21/9 | 139/31 | 12/4 | 1/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/12 | 160/28 | 0/1 | 0/1 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 60/22 | 6/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 45/21 | 5/3 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 26/8 | 3/2 | ✓/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 85/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 57/17 | 3/3 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 52/18 | 6/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 58/17 | 4/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 46/15 | 6/4 | ✓/✓ | {} / {} |

### dry — 50/lqb

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 38/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 160/3 | 0/37 | 24/2 | 6/2 | ✓/— | {} / {} |
| greek_latin | 20/9 | 140/31 | 13/4 | 1/1 | —/— | {} / {} |
| historical_russian | 120/0 | 0/30 | 6/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 45/12 | 115/28 | 2/1 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 67/22 | 10/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 52/21 | 9/3 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 37/8 | 8/2 | ✓/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 61/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 44/17 | 7/3 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 53/18 | 10/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 47/17 | 8/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 49/15 | 10/4 | ✓/✓ | {} / {} |

### dry — 50/both

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 76/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 160/3 | 0/37 | 26/2 | 6/2 | ✓/— | {} / {} |
| greek_latin | 32/9 | 128/31 | 19/4 | 1/1 | —/— | {} / {} |
| historical_russian | 120/0 | 0/30 | 6/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 46/12 | 114/28 | 2/1 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 70/22 | 10/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 55/21 | 9/3 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 58/8 | 8/2 | ✓/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 104/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 44/17 | 7/3 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 56/18 | 10/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 49/17 | 8/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 52/15 | 10/4 | ✓/✓ | {} / {} |

### dry — 100/none

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 22/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 5/3 | 155/37 | 2/2 | 2/2 | —/— | {} / {} |
| greek_latin | 9/9 | 151/31 | 6/4 | 1/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 2/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 25/22 | 5/4 | ✓/✓ | {} / {} |
| short | 80/30 | 40/0 | 18/21 | 4/3 | ✓/✓ | {} / {} |
| long | 17/40 | 143/0 | 7/8 | 3/2 | —/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 42/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 19/17 | 2/3 | —/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 34/18 | 5/3 | ✓/✓ | {"large": 8, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 26/17 | 3/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 33/15 | 5/4 | ✓/✓ | {} / {} |

### dry — 100/n1

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 60/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 84/3 | 76/37 | 4/2 | 3/2 | —/— | {} / {} |
| greek_latin | 21/9 | 139/31 | 12/4 | 1/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 2/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 60/22 | 6/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 48/21 | 5/3 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 28/8 | 4/2 | ✓/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 85/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 57/17 | 3/3 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 52/18 | 6/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 58/17 | 4/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 46/15 | 6/4 | ✓/✓ | {} / {} |

### dry — 100/lqb

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 38/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 160/3 | 0/37 | 25/2 | 6/2 | ✓/— | {} / {} |
| greek_latin | 20/9 | 140/31 | 13/4 | 1/1 | —/— | {} / {} |
| historical_russian | 120/0 | 0/30 | 6/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 3/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 67/22 | 10/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 51/21 | 9/3 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 38/8 | 8/2 | ✓/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 61/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 44/17 | 7/3 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 53/18 | 10/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 47/17 | 8/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 49/15 | 10/4 | ✓/✓ | {} / {} |

### dry — 100/both

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 76/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 160/3 | 0/37 | 27/2 | 6/2 | ✓/— | {} / {} |
| greek_latin | 32/9 | 128/31 | 19/4 | 1/1 | —/— | {} / {} |
| historical_russian | 120/0 | 0/30 | 6/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 3/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 70/22 | 10/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 54/21 | 9/3 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 54/8 | 8/2 | ✓/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 104/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 44/17 | 7/3 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 56/18 | 10/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 49/17 | 8/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 52/15 | 10/4 | ✓/✓ | {} / {} |

### dry — unlimited/none

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 22/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 5/3 | 155/37 | 2/2 | 2/2 | —/— | {} / {} |
| greek_latin | 9/9 | 151/31 | 6/4 | 1/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 2/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 25/22 | 5/4 | ✓/✓ | {} / {} |
| short | 80/30 | 40/0 | 18/21 | 4/3 | ✓/✓ | {} / {} |
| long | 17/40 | 143/0 | 7/8 | 3/2 | —/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 42/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 19/17 | 2/3 | —/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 34/18 | 5/3 | ✓/✓ | {"large": 8, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 26/17 | 3/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 33/15 | 5/4 | ✓/✓ | {} / {} |

### dry — unlimited/n1

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 60/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 93/3 | 67/37 | 4/2 | 3/2 | —/— | {} / {} |
| greek_latin | 21/9 | 139/31 | 12/4 | 1/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 2/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 60/22 | 6/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 48/21 | 5/3 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 28/8 | 4/2 | ✓/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 85/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 57/17 | 3/3 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 52/18 | 6/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 58/17 | 4/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 46/15 | 6/4 | ✓/✓ | {} / {} |

### dry — unlimited/lqb

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 38/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 160/3 | 0/37 | 25/2 | 6/2 | ✓/— | {} / {} |
| greek_latin | 20/9 | 140/31 | 13/4 | 1/1 | —/— | {} / {} |
| historical_russian | 120/0 | 0/30 | 6/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 3/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 67/22 | 10/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 51/21 | 9/3 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 38/8 | 8/2 | ✓/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 61/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 44/17 | 7/3 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 53/18 | 10/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 47/17 | 8/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 49/15 | 10/4 | ✓/✓ | {} / {} |

### dry — unlimited/both

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 76/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 160/3 | 0/37 | 27/2 | 6/2 | ✓/— | {} / {} |
| greek_latin | 32/9 | 128/31 | 19/4 | 1/1 | —/— | {} / {} |
| historical_russian | 120/0 | 0/30 | 6/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 3/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 70/22 | 10/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 54/21 | 9/3 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 54/8 | 8/2 | ✓/— | {} / {} |
| vertical_turned | 17/10 | 83/15 | 5/5 | 1/1 | —/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 104/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 44/17 | 7/3 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 56/18 | 10/3 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 49/17 | 8/2 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 52/15 | 10/4 | ✓/✓ | {} / {} |

### upper_bound — 4/none

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 0/0 | 240/60 | 0/0 | 0/0 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| greek_latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 0/40 | 200/10 | 0/25 | 0/1 | —/— | {} / {} |
| short | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| long | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| vertical_turned | 100/25 | 0/0 | 34/27 | 5/2 | ✓/— | {} / {} |
| caps_headings | 0/23 | 120/7 | 0/20 | 0/1 | —/— | {} / {} |
| leaders_dashes | 0/0 | 100/25 | 0/0 | 0/0 | —/— | {} / {} |
| font_extremes | 76/25 | 24/0 | 28/22 | 4/4 | ✓/✓ | {"large": 15, "small": 9} / {"large": 0, "small": 0} |
| degraded | 11/25 | 89/0 | 5/30 | 2/1 | —/— | {} / {} |
| curved_skewed | 2/25 | 98/0 | 1/30 | 1/1 | —/— | {} / {} |

### upper_bound — 4/n1

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 0/0 | 240/60 | 0/0 | 0/0 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| greek_latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 2/40 | 198/10 | 2/25 | 1/1 | —/— | {} / {} |
| short | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| long | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| vertical_turned | 100/25 | 0/0 | 54/27 | 6/2 | ✓/— | {} / {} |
| caps_headings | 15/23 | 105/7 | 13/20 | 1/1 | —/— | {} / {} |
| leaders_dashes | 0/0 | 100/25 | 0/0 | 0/0 | —/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 74/22 | 5/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 80/25 | 20/0 | 41/30 | 2/1 | —/— | {} / {} |
| curved_skewed | 38/25 | 62/0 | 18/30 | 1/1 | —/— | {} / {} |

### upper_bound — 4/lqb

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 0/0 | 240/60 | 0/0 | 0/0 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| greek_latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 2/40 | 198/10 | 1/25 | 1/1 | —/— | {} / {} |
| short | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| long | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| vertical_turned | 100/25 | 0/0 | 63/27 | 10/2 | ✓/— | {} / {} |
| caps_headings | 15/23 | 105/7 | 12/20 | 1/1 | —/— | {} / {} |
| leaders_dashes | 0/0 | 100/25 | 0/0 | 0/0 | —/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 69/22 | 10/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 99/25 | 1/0 | 44/30 | 4/1 | ✓/— | {} / {} |
| curved_skewed | 36/25 | 64/0 | 19/30 | 1/1 | —/— | {} / {} |

### upper_bound — 4/both

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 0/0 | 240/60 | 0/0 | 0/0 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| greek_latin | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 50/40 | 150/10 | 37/25 | 1/1 | —/— | {} / {} |
| short | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| long | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| vertical_turned | 100/25 | 0/0 | 66/27 | 10/2 | ✓/— | {} / {} |
| caps_headings | 33/23 | 87/7 | 25/20 | 1/1 | —/— | {} / {} |
| leaders_dashes | 0/0 | 100/25 | 0/0 | 0/0 | —/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 67/22 | 10/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 76/30 | 4/1 | ✓/— | {} / {} |
| curved_skewed | 100/25 | 0/0 | 83/30 | 1/1 | —/— | {} / {} |

### upper_bound — 12/none

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 0/60 | 240/0 | 0/22 | 0/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 0/7 | 160/33 | 0/2 | 0/1 | —/— | {} / {} |
| greek_latin | 0/9 | 160/31 | 0/4 | 0/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 35/50 | 165/0 | 14/29 | 1/1 | —/— | {} / {} |
| short | 0/30 | 120/0 | 0/22 | 0/1 | —/— | {} / {} |
| long | 0/22 | 160/18 | 0/9 | 0/1 | —/— | {} / {} |
| vertical_turned | 100/25 | 0/0 | 34/25 | 5/2 | ✓/— | {} / {} |
| caps_headings | 39/30 | 81/0 | 24/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 0/25 | 100/0 | 0/20 | 0/1 | —/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 38/12 | 5/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 32/19 | 4/4 | ✓/✓ | {} / {} |
| curved_skewed | 72/25 | 28/0 | 32/27 | 3/2 | ✓/— | {} / {} |

### upper_bound — 12/n1

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 2/60 | 238/0 | 1/22 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 0/7 | 160/33 | 0/2 | 0/1 | —/— | {} / {} |
| greek_latin | 0/9 | 160/31 | 0/4 | 0/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 64/29 | 1/1 | —/— | {} / {} |
| short | 0/30 | 120/0 | 0/22 | 0/1 | —/— | {} / {} |
| long | 2/22 | 158/18 | 1/9 | 1/1 | —/— | {} / {} |
| vertical_turned | 100/25 | 0/0 | 54/25 | 6/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 70/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 99/25 | 1/0 | 30/20 | 1/1 | —/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 71/12 | 6/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 63/19 | 4/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 74/27 | 4/2 | ✓/— | {} / {} |

### upper_bound — 12/lqb

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 2/60 | 238/0 | 1/22 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 5/7 | 155/33 | 1/2 | 1/1 | —/— | {} / {} |
| greek_latin | 0/9 | 160/31 | 0/4 | 0/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 58/29 | 5/1 | ✓/— | {} / {} |
| short | 18/30 | 102/0 | 8/22 | 1/1 | —/— | {} / {} |
| long | 1/22 | 159/18 | 1/9 | 1/1 | —/— | {} / {} |
| vertical_turned | 100/25 | 0/0 | 44/25 | 10/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 61/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 29/20 | 4/1 | ✓/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 52/12 | 10/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 52/19 | 9/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 56/27 | 7/2 | ✓/— | {} / {} |

### upper_bound — 12/both

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 161/60 | 79/0 | 44/22 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 9/7 | 151/33 | 5/2 | 2/1 | —/— | {} / {} |
| greek_latin | 17/9 | 143/31 | 13/4 | 1/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 100/29 | 6/1 | ✓/— | {} / {} |
| short | 120/30 | 0/0 | 70/22 | 1/1 | —/— | {} / {} |
| long | 159/22 | 1/18 | 47/9 | 1/1 | —/— | {} / {} |
| vertical_turned | 100/25 | 0/0 | 46/25 | 10/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 104/36 | 1/1 | —/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 77/20 | 4/1 | ✓/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 55/12 | 10/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 54/19 | 9/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 54/27 | 8/2 | ✓/— | {} / {} |

### upper_bound — 25/none

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 2/60 | 238/0 | 1/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 0/8 | 160/32 | 0/3 | 0/1 | —/— | {} / {} |
| greek_latin | 0/9 | 160/31 | 0/4 | 0/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 30/32 | 4/3 | ✓/✓ | {} / {} |
| short | 7/30 | 113/0 | 2/22 | 1/1 | —/— | {} / {} |
| long | 0/38 | 160/2 | 0/9 | 0/1 | —/— | {} / {} |
| vertical_turned | 100/25 | 0/0 | 34/25 | 5/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 34/27 | 3/2 | ✓/— | {} / {} |
| leaders_dashes | 41/25 | 59/0 | 6/17 | 2/2 | —/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 38/12 | 5/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 33/13 | 4/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 35/13 | 4/4 | ✓/✓ | {} / {} |

### upper_bound — 25/n1

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 56/26 | 1/1 | —/— | {} / {} |
| polytonic | 0/0 | 360/90 | 0/0 | 0/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 8/8 | 152/32 | 6/3 | 1/1 | —/— | {} / {} |
| greek_latin | 19/9 | 141/31 | 12/4 | 1/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 69/32 | 4/3 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 55/22 | 1/1 | —/— | {} / {} |
| long | 160/38 | 0/2 | 34/9 | 1/1 | —/— | {} / {} |
| vertical_turned | 100/25 | 0/0 | 54/25 | 6/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 89/27 | 3/2 | ✓/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 57/17 | 2/2 | —/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 63/12 | 6/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 64/13 | 4/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 76/13 | 5/4 | ✓/✓ | {} / {} |

### upper_bound — 25/lqb

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 38/26 | 1/1 | —/— | {} / {} |
| polytonic | 5/0 | 355/90 | 1/0 | 1/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 19/8 | 141/32 | 11/3 | 3/1 | ✓/— | {} / {} |
| greek_latin | 26/9 | 134/31 | 14/4 | 2/1 | —/— | {} / {} |
| historical_russian | 23/0 | 97/30 | 3/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 74/32 | 9/3 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 54/22 | 4/1 | ✓/— | {} / {} |
| long | 160/38 | 0/2 | 31/9 | 4/1 | ✓/— | {} / {} |
| vertical_turned | 100/25 | 0/0 | 44/25 | 10/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 66/27 | 4/2 | ✓/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 47/17 | 8/2 | ✓/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 51/12 | 10/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 52/13 | 10/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 52/13 | 10/4 | ✓/✓ | {} / {} |

### upper_bound — 25/both

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 77/26 | 1/1 | —/— | {} / {} |
| polytonic | 4/0 | 356/90 | 1/0 | 1/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 23/8 | 137/32 | 14/3 | 3/1 | ✓/— | {} / {} |
| greek_latin | 41/9 | 119/31 | 21/4 | 2/1 | —/— | {} / {} |
| historical_russian | 25/0 | 95/30 | 3/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} / {"bg": 10, "ru": 10, "sr": 10, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 76/32 | 9/3 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 63/22 | 6/1 | ✓/— | {} / {} |
| long | 160/38 | 0/2 | 59/9 | 4/1 | ✓/— | {} / {} |
| vertical_turned | 100/25 | 0/0 | 46/25 | 10/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 112/27 | 5/2 | ✓/— | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 48/17 | 9/2 | ✓/— | {} / {} |
| font_extremes | 100/25 | 0/0 | 54/12 | 10/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 54/13 | 10/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 55/13 | 10/4 | ✓/✓ | {} / {} |

### upper_bound — 50/none

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 22/26 | 1/1 | —/— | {} / {} |
| polytonic | 2/0 | 358/90 | 1/0 | 1/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 5/9 | 155/31 | 4/4 | 1/2 | —/— | {} / {} |
| greek_latin | 12/9 | 148/31 | 7/4 | 2/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 6/12 | 154/28 | 1/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 34, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 31/33 | 4/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 26/15 | 4/4 | ✓/✓ | {} / {} |
| long | 41/40 | 119/0 | 12/12 | 3/3 | ✓/✓ | {} / {} |
| vertical_turned | 100/25 | 0/0 | 34/25 | 5/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 46/15 | 3/3 | ✓/✓ | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 24/11 | 4/4 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 38/12 | 5/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 34/13 | 5/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 36/12 | 4/4 | ✓/✓ | {} / {} |

### upper_bound — 50/n1

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 61/26 | 1/1 | —/— | {} / {} |
| polytonic | 2/0 | 358/90 | 1/0 | 1/0 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 9/9 | 151/31 | 7/4 | 1/2 | —/— | {} / {} |
| greek_latin | 26/9 | 134/31 | 14/4 | 2/1 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 6/12 | 154/28 | 1/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 34, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 71/33 | 5/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 60/15 | 4/4 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 37/12 | 3/3 | ✓/✓ | {} / {} |
| vertical_turned | 100/25 | 0/0 | 54/25 | 6/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 89/15 | 3/3 | ✓/✓ | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 36/11 | 4/4 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 36/12 | 6/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 53/13 | 6/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 65/12 | 5/4 | ✓/✓ | {} / {} |

### upper_bound — 50/lqb

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 38/26 | 1/1 | —/— | {} / {} |
| polytonic | 78/0 | 282/90 | 8/0 | 5/0 | —/— | {} / {} |
| poly_dictionary_journal | 111/0 | 49/40 | 8/0 | 2/0 | —/— | {} / {} |
| latin | 160/9 | 0/31 | 33/4 | 7/2 | ✓/— | {} / {} |
| greek_latin | 160/9 | 0/31 | 35/4 | 8/1 | ✓/— | {} / {} |
| historical_russian | 120/0 | 0/30 | 6/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 40/12 | 120/28 | 2/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 65/33 | 10/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 54/15 | 10/4 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 47/12 | 9/3 | ✓/✓ | {} / {} |
| vertical_turned | 100/25 | 0/0 | 44/25 | 10/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 69/15 | 6/3 | ✓/✓ | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 47/11 | 10/4 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 51/12 | 10/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 52/13 | 10/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 52/12 | 10/4 | ✓/✓ | {} / {} |

### upper_bound — 50/both

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 77/26 | 1/1 | —/— | {} / {} |
| polytonic | 85/0 | 275/90 | 11/0 | 5/0 | ✓/— | {} / {} |
| poly_dictionary_journal | 146/0 | 14/40 | 8/0 | 2/0 | —/— | {} / {} |
| latin | 160/9 | 0/31 | 41/4 | 7/2 | ✓/— | {} / {} |
| greek_latin | 160/9 | 0/31 | 43/4 | 8/1 | ✓/— | {} / {} |
| historical_russian | 120/0 | 0/30 | 6/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 40/12 | 120/28 | 2/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 68/33 | 10/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 57/15 | 10/4 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 57/12 | 9/3 | ✓/✓ | {} / {} |
| vertical_turned | 100/25 | 0/0 | 46/25 | 10/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 103/15 | 6/3 | ✓/✓ | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 50/11 | 10/4 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 54/12 | 10/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 54/13 | 10/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 55/12 | 10/4 | ✓/✓ | {} / {} |

### upper_bound — 100/none

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 22/26 | 1/1 | —/— | {} / {} |
| polytonic | 173/67 | 187/23 | 4/2 | 2/2 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 8/14 | 152/26 | 5/6 | 2/4 | —/— | {} / {} |
| greek_latin | 18/17 | 142/23 | 9/6 | 3/3 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 2/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 31/33 | 4/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 27/14 | 4/4 | ✓/✓ | {} / {} |
| long | 61/40 | 99/0 | 13/13 | 4/4 | ✓/✓ | {} / {} |
| vertical_turned | 100/25 | 0/0 | 34/25 | 5/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 46/15 | 3/3 | ✓/✓ | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 24/11 | 4/4 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 38/12 | 5/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 34/13 | 5/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 37/12 | 5/4 | ✓/✓ | {} / {} |

### upper_bound — 100/n1

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 61/26 | 1/1 | —/— | {} / {} |
| polytonic | 185/67 | 175/23 | 4/2 | 2/2 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 12/14 | 148/26 | 8/6 | 2/4 | —/— | {} / {} |
| greek_latin | 32/17 | 128/23 | 16/6 | 3/3 | ✓/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 2/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 74/33 | 6/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 63/14 | 5/4 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 38/13 | 4/4 | ✓/✓ | {} / {} |
| vertical_turned | 100/25 | 0/0 | 54/25 | 6/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 92/15 | 4/3 | ✓/✓ | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 33/11 | 5/4 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 36/12 | 6/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 38/13 | 6/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 40/12 | 6/4 | ✓/✓ | {} / {} |

### upper_bound — 100/lqb

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 38/26 | 1/1 | —/— | {} / {} |
| polytonic | 360/67 | 0/23 | 22/2 | 6/2 | ✓/— | {} / {} |
| poly_dictionary_journal | 160/0 | 0/40 | 12/0 | 2/0 | —/— | {} / {} |
| latin | 160/14 | 0/26 | 36/6 | 7/4 | ✓/— | {} / {} |
| greek_latin | 160/17 | 0/23 | 36/6 | 8/3 | ✓/— | {} / {} |
| historical_russian | 120/0 | 0/30 | 6/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 3/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 64/33 | 10/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 54/14 | 10/4 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 50/13 | 10/4 | ✓/✓ | {} / {} |
| vertical_turned | 100/25 | 0/0 | 44/25 | 10/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 70/15 | 6/3 | ✓/✓ | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 48/11 | 10/4 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 51/12 | 10/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 52/13 | 10/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 52/12 | 10/4 | ✓/✓ | {} / {} |

### upper_bound — 100/both

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 77/26 | 1/1 | —/— | {} / {} |
| polytonic | 360/67 | 0/23 | 22/2 | 6/2 | ✓/— | {} / {} |
| poly_dictionary_journal | 160/0 | 0/40 | 12/0 | 2/0 | —/— | {} / {} |
| latin | 160/14 | 0/26 | 43/6 | 8/4 | ✓/— | {} / {} |
| greek_latin | 160/17 | 0/23 | 43/6 | 8/3 | ✓/— | {} / {} |
| historical_russian | 120/0 | 0/30 | 6/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 3/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 67/33 | 10/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 57/14 | 10/4 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 55/13 | 10/4 | ✓/✓ | {} / {} |
| vertical_turned | 100/25 | 0/0 | 46/25 | 10/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 98/15 | 6/3 | ✓/✓ | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 51/11 | 10/4 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 54/12 | 10/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 54/13 | 10/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 55/12 | 10/4 | ✓/✓ | {} / {} |

### upper_bound — unlimited/none

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 22/26 | 1/1 | —/— | {} / {} |
| polytonic | 360/90 | 0/0 | 5/2 | 3/2 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 8/14 | 152/26 | 5/6 | 2/4 | —/— | {} / {} |
| greek_latin | 18/17 | 142/23 | 9/6 | 3/3 | —/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 2/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 32/33 | 5/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 28/14 | 5/4 | ✓/✓ | {} / {} |
| long | 62/40 | 98/0 | 14/13 | 5/4 | ✓/✓ | {} / {} |
| vertical_turned | 100/25 | 0/0 | 34/25 | 5/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 47/15 | 4/3 | ✓/✓ | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 25/11 | 5/4 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 38/12 | 5/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 34/13 | 5/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 37/12 | 5/4 | ✓/✓ | {} / {} |

### upper_bound — unlimited/n1

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 61/26 | 1/1 | —/— | {} / {} |
| polytonic | 360/90 | 0/0 | 5/2 | 3/2 | —/— | {} / {} |
| poly_dictionary_journal | 0/0 | 160/40 | 0/0 | 0/0 | —/— | {} / {} |
| latin | 160/14 | 0/26 | 11/6 | 3/4 | ✓/— | {} / {} |
| greek_latin | 32/17 | 128/23 | 16/6 | 3/3 | ✓/— | {} / {} |
| historical_russian | 0/0 | 120/30 | 0/0 | 0/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 2/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 74/33 | 6/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 65/14 | 6/4 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 42/13 | 6/4 | ✓/✓ | {} / {} |
| vertical_turned | 100/25 | 0/0 | 54/25 | 6/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 93/15 | 5/3 | ✓/✓ | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 30/11 | 6/4 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 36/12 | 6/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 38/13 | 6/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 40/12 | 6/4 | ✓/✓ | {} / {} |

### upper_bound — unlimited/lqb

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 38/26 | 1/1 | —/— | {} / {} |
| polytonic | 360/90 | 0/0 | 22/2 | 6/2 | ✓/— | {} / {} |
| poly_dictionary_journal | 160/0 | 0/40 | 12/0 | 2/0 | —/— | {} / {} |
| latin | 160/14 | 0/26 | 37/6 | 8/4 | ✓/— | {} / {} |
| greek_latin | 160/17 | 0/23 | 36/6 | 8/3 | ✓/— | {} / {} |
| historical_russian | 120/0 | 0/30 | 6/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 3/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 64/33 | 10/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 54/14 | 10/4 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 50/13 | 10/4 | ✓/✓ | {} / {} |
| vertical_turned | 100/25 | 0/0 | 44/25 | 10/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 70/15 | 6/3 | ✓/✓ | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 48/11 | 10/4 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 51/12 | 10/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 52/13 | 10/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 52/12 | 10/4 | ✓/✓ | {} / {} |

### upper_bound — unlimited/both

| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |
|---|---|---|---|---|---|---|
| monotonic | 240/60 | 0/0 | 77/26 | 1/1 | —/— | {} / {} |
| polytonic | 360/90 | 0/0 | 22/2 | 6/2 | ✓/— | {} / {} |
| poly_dictionary_journal | 160/0 | 0/40 | 12/0 | 2/0 | —/— | {} / {} |
| latin | 160/14 | 0/26 | 43/6 | 8/4 | ✓/— | {} / {} |
| greek_latin | 160/17 | 0/23 | 43/6 | 8/3 | ✓/— | {} / {} |
| historical_russian | 120/0 | 0/30 | 6/0 | 1/0 | —/— | {} / {} |
| modern_cyrillic | 48/12 | 112/28 | 3/2 | 1/1 | —/— | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} / {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| numeric_cells | 200/50 | 0/0 | 67/33 | 10/4 | ✓/✓ | {} / {} |
| short | 120/30 | 0/0 | 57/14 | 10/4 | ✓/✓ | {} / {} |
| long | 160/40 | 0/0 | 55/13 | 10/4 | ✓/✓ | {} / {} |
| vertical_turned | 100/25 | 0/0 | 46/25 | 10/2 | ✓/— | {} / {} |
| caps_headings | 120/30 | 0/0 | 98/15 | 6/3 | ✓/✓ | {} / {} |
| leaders_dashes | 100/25 | 0/0 | 51/11 | 10/4 | ✓/✓ | {} / {} |
| font_extremes | 100/25 | 0/0 | 54/12 | 10/4 | ✓/✓ | {"large": 0, "small": 0} / {"large": 0, "small": 0} |
| degraded | 100/25 | 0/0 | 54/13 | 10/4 | ✓/✓ | {} / {} |
| curved_skewed | 100/25 | 0/0 | 55/12 | 10/4 | ✓/✓ | {} / {} |

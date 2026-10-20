# BENCH02K — census_05 draw v2

| Split | Class | Pre-filter | Eligible supply | Quota | Target | Drawn | Credited | Deficit | Editions | Sources | Top-edition share | ≥10 books / ≥3 sources |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| test | caps_headings | 1056 | 1056 | 120 | 144 | 144 | 120 | 0 | 112 | 6 | 8.33% | 1 |
| dev | caps_headings | 414 | 414 | 30 | 36 | 36 | 30 | 0 | 16 | 3 | 36.11% | 1 |
| test | curved_skewed | 1806 | 1799 | 100 | 120 | 120 | 100 | 0 | 54 | 10 | 5.83% | 1 |
| dev | curved_skewed | 138 | 138 | 25 | 30 | 30 | 25 | 0 | 17 | 4 | 23.33% | 1 |
| test | degraded (relative: bottom 5% confidence within source) | 1273 | 1264 | 100 | 120 | 120 | 100 | 0 | 49 | 10 | 5.83% | 1 |
| dev | degraded (relative: bottom 5% confidence within source) | 99 | 99 | 25 | 30 | 30 | 25 | 0 | 12 | 4 | 26.67% | 1 |
| test | font_extremes | 6474 | 6438 | 100 | 120 | 120 | 100 | 0 | 54 | 10 | 6.67% | 1 |
| dev | font_extremes | 391 | 391 | 25 | 31 | 31 | 25 | 0 | 12 | 4 | 29.03% | 1 |
| test | greek_latin | 1343 | 1340 | 160 | 192 | 192 | 160 | 0 | 37 | 7 | 6.77% | 1 |
| dev | greek_latin | 15 | 15 | 40 | 48 | 15 | 15 | 25 | 6 | 3 | 33.33% | 0 |
| test | historical_russian | 314 | 314 | 120 | 144 | 144 | 120 | 0 | 6 | 1 | 20.83% | 0 |
| dev | historical_russian | 0 | 0 | 30 | 36 | 0 | 0 | 30 | 0 | 0 | 0.00% | 0 |
| test | latin | 2820 | 2820 | 160 | 192 | 192 | 160 | 0 | 28 | 6 | 6.77% | 1 |
| dev | latin | 3 | 3 | 40 | 48 | 3 | 3 | 37 | 2 | 2 | 66.67% | 0 |
| test | leaders_dashes | 4855 | 4795 | 100 | 120 | 120 | 100 | 0 | 47 | 10 | 5.83% | 1 |
| dev | leaders_dashes | 264 | 264 | 25 | 30 | 30 | 25 | 0 | 11 | 4 | 26.67% | 1 |
| test | long | 3160 | 3121 | 160 | 192 | 192 | 160 | 0 | 50 | 9 | 14.06% | 1 |
| dev | long | 110 | 110 | 40 | 48 | 48 | 40 | 0 | 10 | 4 | 33.33% | 1 |
| test | modern_cyrillic | 163 | 163 | 160 | 192 | 48 | 48 | 112 | 3 | 1 | 33.33% | 0 |
| dev | modern_cyrillic | 91 | 91 | 40 | 48 | 12 | 12 | 28 | 2 | 1 | 50.00% | 0 |
| test | monotonic | 2138 | 2126 | 240 | 288 | 288 | 240 | 0 | 76 | 1 | 1.39% | 0 |
| dev | monotonic | 514 | 514 | 60 | 72 | 72 | 60 | 0 | 25 | 1 | 5.56% | 0 |
| test | numeric_cells | 2344 | 2323 | 200 | 240 | 240 | 200 | 0 | 67 | 10 | 10.42% | 1 |
| dev | numeric_cells | 166 | 166 | 50 | 60 | 60 | 50 | 0 | 25 | 4 | 8.33% | 1 |
| test | poly_dictionary_journal | 4353 | 4226 | 160 | 192 | 192 | 160 | 0 | 12 | 2 | 10.42% | 0 |
| dev | poly_dictionary_journal | 0 | 0 | 40 | 48 | 0 | 0 | 40 | 0 | 0 | 0.00% | 0 |
| test | polytonic | 2543 | 2543 | 360 | 432 | 432 | 360 | 0 | 22 | 6 | 11.57% | 1 |
| dev | polytonic | 336 | 336 | 90 | 108 | 100 | 90 | 0 | 2 | 2 | 50.00% | 0 |
| test | short | 419 | 411 | 120 | 144 | 144 | 120 | 0 | 54 | 10 | 9.72% | 1 |
| dev | short | 49 | 49 | 30 | 36 | 36 | 30 | 0 | 18 | 3 | 13.89% | 1 |
| test | vertical_turned | 1124 | 1120 | 100 | 120 | 120 | 100 | 0 | 38 | 7 | 16.67% | 1 |
| dev | vertical_turned | 773 | 773 | 25 | 30 | 30 | 25 | 0 | 22 | 1 | 6.67% | 0 |

| Split | Credited / quota | Drawn / target | Classes filled | Deficit |
|---|---:|---:|---:|---:|
| test | 2348/2460 | 2808/2952 | 15/16 | 112 |
| dev | 455/615 | 533/739 | 11/16 | 160 |

| Split | Class | BENCH02J credited | V2 credited | Δ credited | BENCH02J drawn | V2 drawn | Δ drawn | BENCH02J supply | V2 supply | Δ supply |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| test | vertical_turned | 100 | 100 | 0 | 120 | 120 | 0 | 1120 | 1120 | 0 |
| test | font_extremes | 100 | 100 | 0 | 120 | 120 | 0 | 6438 | 6438 | 0 |
| test | degraded (relative: bottom 5% confidence within source) | 0 | 100 | 100 | 0 | 120 | 120 | 0 | 1264 | 1264 |
| test | curved_skewed | 100 | 100 | 0 | 120 | 120 | 0 | 1917 | 1799 | -118 |
| test | numeric_cells | 200 | 200 | 0 | 240 | 240 | 0 | 2386 | 2323 | -63 |
| test | caps_headings | 120 | 120 | 0 | 144 | 144 | 0 | 1111 | 1056 | -55 |
| test | leaders_dashes | 100 | 100 | 0 | 120 | 120 | 0 | 5021 | 4795 | -226 |
| test | short | 120 | 120 | 0 | 144 | 144 | 0 | 454 | 411 | -43 |
| test | long | 160 | 160 | 0 | 192 | 192 | 0 | 3162 | 3121 | -41 |
| test | greek_latin | 160 | 160 | 0 | 192 | 192 | 0 | 1444 | 1340 | -104 |
| test | historical_russian | 120 | 120 | 0 | 144 | 144 | 0 | 344 | 314 | -30 |
| test | modern_cyrillic | 48 | 48 | 0 | 48 | 48 | 0 | 167 | 163 | -4 |
| test | latin | 160 | 160 | 0 | 192 | 192 | 0 | 2843 | 2820 | -23 |
| test | poly_dictionary_journal | 160 | 160 | 0 | 192 | 192 | 0 | 4533 | 4226 | -307 |
| test | polytonic | 360 | 360 | 0 | 432 | 432 | 0 | 2675 | 2543 | -132 |
| test | monotonic | 240 | 240 | 0 | 288 | 288 | 0 | 2224 | 2126 | -98 |
| dev | vertical_turned | 25 | 25 | 0 | 30 | 30 | 0 | 773 | 773 | 0 |
| dev | font_extremes | 25 | 25 | 0 | 31 | 31 | 0 | 391 | 391 | 0 |
| dev | degraded (relative: bottom 5% confidence within source) | 0 | 25 | 25 | 0 | 30 | 30 | 0 | 99 | 99 |
| dev | curved_skewed | 25 | 25 | 0 | 30 | 30 | 0 | 146 | 138 | -8 |
| dev | numeric_cells | 50 | 50 | 0 | 60 | 60 | 0 | 168 | 166 | -2 |
| dev | caps_headings | 30 | 30 | 0 | 36 | 36 | 0 | 439 | 414 | -25 |
| dev | leaders_dashes | 25 | 25 | 0 | 30 | 30 | 0 | 276 | 264 | -12 |
| dev | short | 30 | 30 | 0 | 36 | 36 | 0 | 55 | 49 | -6 |
| dev | long | 40 | 40 | 0 | 48 | 48 | 0 | 110 | 110 | 0 |
| dev | greek_latin | 16 | 15 | -1 | 16 | 15 | -1 | 16 | 15 | -1 |
| dev | historical_russian | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| dev | modern_cyrillic | 12 | 12 | 0 | 12 | 12 | 0 | 94 | 91 | -3 |
| dev | latin | 4 | 3 | -1 | 4 | 3 | -1 | 4 | 3 | -1 |
| dev | poly_dictionary_journal | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| dev | polytonic | 90 | 90 | 0 | 100 | 100 | 0 | 356 | 336 | -20 |
| dev | monotonic | 60 | 60 | 0 | 72 | 72 | 0 | 535 | 514 | -21 |

| Split | Source | Admitted population | Ranked | Flagged | Missing confidence | Degraded primary eligible | Degraded drawn | Degraded credited |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | gazette_modern | 2487 | 2487 | 125 | 0 | 59 | 8 | 6 |
| dev | kosmopolis | 194 | 194 | 10 | 0 | 9 | 8 | 7 |
| dev | lekythos | 520 | 520 | 26 | 0 | 24 | 7 | 6 |
| dev | serbia | 163 | 163 | 9 | 0 | 7 | 7 | 6 |
| test | bsb_poly1850 | 6987 | 6987 | 350 | 0 | 343 | 12 | 10 |
| test | elstat | 4256 | 4256 | 213 | 0 | 89 | 13 | 10 |
| test | gazette_modern | 7155 | 7155 | 358 | 0 | 223 | 12 | 10 |
| test | ia_greek_latin | 1510 | 1510 | 76 | 0 | 63 | 12 | 10 |
| test | ia_poly1850 | 11066 | 11066 | 554 | 0 | 322 | 12 | 10 |
| test | ia_russian | 1590 | 1590 | 80 | 0 | 55 | 12 | 10 |
| test | kosmopolis | 462 | 462 | 24 | 0 | 23 | 12 | 10 |
| test | lekythos | 1189 | 1189 | 60 | 0 | 60 | 12 | 10 |
| test | nlg | 1598 | 1598 | 80 | 0 | 75 | 12 | 10 |
| test | serbia | 453 | 453 | 23 | 0 | 11 | 11 | 10 |

| Split | Previous primary → degraded (relative: bottom 5% confidence within source) | Before exclusions | Eligible |
|---|---|---:|---:|
| dev | caps_headings | 25 | 25 |
| dev | curved_skewed | 8 | 8 |
| dev | greek_latin | 1 | 1 |
| dev | latin | 1 | 1 |
| dev | leaders_dashes | 12 | 12 |
| dev | modern_cyrillic | 3 | 3 |
| dev | monotonic | 21 | 21 |
| dev | numeric_cells | 2 | 2 |
| dev | polytonic | 20 | 20 |
| dev | short | 6 | 6 |
| test | caps_headings | 55 | 55 |
| test | curved_skewed | 118 | 118 |
| test | greek_latin | 104 | 104 |
| test | historical_russian | 30 | 30 |
| test | latin | 23 | 23 |
| test | leaders_dashes | 232 | 226 |
| test | long | 41 | 41 |
| test | modern_cyrillic | 4 | 4 |
| test | monotonic | 98 | 98 |
| test | numeric_cells | 63 | 63 |
| test | poly_dictionary_journal | 309 | 307 |
| test | polytonic | 132 | 132 |
| test | short | 44 | 43 |
| test | unclassified | 20 | 20 |

| Artifact | Bytes | Lines | SHA-256 |
|---|---:|---:|---|
| `docs/harvest/collect_v3_admission/bench02/census05/candidates.jsonl` | 3811251 | 3341 | `70a29c202691584a3382e77505ef56db7b9a0d1347fa5ac2eccc95ac8e9acfe5` |
| `docs/harvest/collect_v3_admission/bench02/census05/draw_plan.json` | 10330 | 244 | `8007e93ff170fdf897d4604d5c6bffe5725317cec226ab16f33ecc31c3b0ddb7` |

| Split | BENCH02J row IDs | V2 row IDs | Kept | Added | Dropped |
|---|---:|---:|---:|---:|---:|
| test | 2688 | 2808 | 1308 | 1500 | 1380 |
| dev | 505 | 533 | 351 | 182 | 154 |
| all | 3193 | 3341 | 1659 | 1682 | 1534 |

| Check | Count |
|---|---:|
| Missing confidence | 0 |
| Candidate locked intersections | 0 |
| Byte-identical rerun artifacts | 4 |
| Extract/readout function or helper changes | 0 |
| Launcher changes | 0 |
| Jobs submitted | 0 |

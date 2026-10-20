# BENCH02I cap choice

Coordinator ruling: both forced pools; per class × edition cap and per class × series cap (3×). All-rows upper bound (not admitted), unchanged classification, quotas, precedence, exclusions and subgroup limits. Credit = min(drawn, quota), including candidates up to the unchanged 20% overdraw target.

With supply means eligible primary-class supply > 0. Test and dev are evaluated independently; every supplied class must reach 90%. No-supply classes remain deficits and do not block. Diversity counts all drawn candidates; books are edition IDs (gazette issues included), not verified canonical works.

| Cap | Test credit /2460 | Dev credit /615 | Supplied classes below 90% (test; dev) | Pass |
|---:|---:|---:|---|---|
| 12 | 2108 | 402 | historical_russian, modern_cyrillic, poly_dictionary_journal, polytonic; greek_latin, modern_cyrillic, latin, polytonic | False |
| 25 | 2348 | 428 | modern_cyrillic; greek_latin, modern_cyrillic, latin, polytonic | False |
| 50 | 2348 | 468 | modern_cyrillic; greek_latin, modern_cyrillic, latin | False |

Chosen production default: **50**. No tested value meets the condition; fallback 50. Below 90%: test:modern_cyrillic, dev:greek_latin, dev:modern_cyrillic, dev:latin

Series cap compliance is unverifiable without series identity; no identity is invented. Zero-supply deficits, bg/uk subquotas, Serbian-only modern Cyrillic and polytonic awaiting sf7 remain visible. No quota transfer.

## Evaluation per class and split

| Cap | Split:class | Supply | Credit/quota | Editions | Sources | Top-edition share | ≥10 books / ≥3 sources |
|---:|---|---:|---|---:|---:|---:|---|
| 12 | test:vertical_turned (vertical_turned) | 3095 | 100/100 | 46 | 10 | 9.17% | True |
| 12 | test:font_extremes (font_extremes) | 12347 | 100/100 | 54 | 10 | 5.00% | True |
| 12 | test:degraded (degraded) | 2611 | 100/100 | 54 | 10 | 5.00% | True |
| 12 | test:curved_skewed (curved_skewed) | 2871 | 100/100 | 55 | 10 | 5.83% | True |
| 12 | test:numeric_cells (numeric_cells) | 4635 | 200/200 | 74 | 10 | 5.00% | True |
| 12 | test:caps_headings (caps_headings) | 1205 | 120/120 | 98 | 6 | 8.33% | True |
| 12 | test:leaders_dashes (leaders_dashes) | 6899 | 100/100 | 51 | 10 | 5.00% | True |
| 12 | test:short (short) | 1438 | 120/120 | 57 | 10 | 5.56% | True |
| 12 | test:long (long) | 4929 | 160/160 | 57 | 10 | 6.25% | True |
| 12 | test:greek_latin (greek_latin) | 1572 | 160/160 | 43 | 8 | 6.25% | True |
| 12 | test:historical_russian (historical_russian) | 459 | 72/120 | 6 | 1 | 16.67% | False |
| 12 | test:modern_cyrillic (Serbian-only) | 332 | 36/160 | 3 | 1 | 33.33% | False |
| 12 | test:latin (latin) | 6186 | 160/160 | 43 | 8 | 5.21% | True |
| 12 | test:poly_dictionary_journal (poly_dictionary_journal) | 4619 | 137/160 | 12 | 2 | 8.76% | False |
| 12 | test:polytonic (polytonic) | 2724 | 203/360 | 22 | 6 | 5.91% | True |
| 12 | test:monotonic (monotonic) | 2575 | 240/240 | 77 | 1 | 1.39% | False |
| 12 | dev:vertical_turned (vertical_turned) | 2269 | 25/25 | 25 | 2 | 20.00% | False |
| 12 | dev:font_extremes (font_extremes) | 809 | 25/25 | 12 | 4 | 29.03% | True |
| 12 | dev:degraded (degraded) | 373 | 25/25 | 13 | 4 | 30.00% | True |
| 12 | dev:curved_skewed (curved_skewed) | 251 | 25/25 | 12 | 4 | 26.67% | True |
| 12 | dev:numeric_cells (numeric_cells) | 808 | 50/50 | 33 | 4 | 5.00% | True |
| 12 | dev:caps_headings (caps_headings) | 489 | 30/30 | 16 | 3 | 33.33% | True |
| 12 | dev:leaders_dashes (leaders_dashes) | 368 | 25/25 | 11 | 4 | 26.67% | True |
| 12 | dev:short (short) | 235 | 30/30 | 14 | 4 | 27.78% | True |
| 12 | dev:long (long) | 150 | 40/40 | 13 | 4 | 25.00% | True |
| 12 | dev:greek_latin (greek_latin) | 17 | 17/40 | 6 | 3 | 29.41% | False |
| 12 | dev:historical_russian (historical_russian) | 0 | 0/30 | 0 | 0 | 0.00% | False |
| 12 | dev:modern_cyrillic (Serbian-only) | 198 | 12/40 | 2 | 1 | 50.00% | False |
| 12 | dev:latin (latin) | 14 | 14/40 | 6 | 4 | 42.86% | False |
| 12 | dev:poly_dictionary_journal (poly_dictionary_journal) | 0 | 0/40 | 0 | 0 | 0.00% | False |
| 12 | dev:polytonic (polytonic) | 373 | 24/90 | 2 | 2 | 50.00% | False |
| 12 | dev:monotonic (monotonic) | 582 | 60/60 | 26 | 1 | 4.17% | False |
| 25 | test:vertical_turned (vertical_turned) | 3095 | 100/100 | 46 | 10 | 9.17% | True |
| 25 | test:font_extremes (font_extremes) | 12347 | 100/100 | 54 | 10 | 5.00% | True |
| 25 | test:degraded (degraded) | 2611 | 100/100 | 54 | 10 | 5.00% | True |
| 25 | test:curved_skewed (curved_skewed) | 2871 | 100/100 | 55 | 10 | 5.83% | True |
| 25 | test:numeric_cells (numeric_cells) | 4635 | 200/200 | 67 | 10 | 10.42% | True |
| 25 | test:caps_headings (caps_headings) | 1205 | 120/120 | 98 | 6 | 8.33% | True |
| 25 | test:leaders_dashes (leaders_dashes) | 6899 | 100/100 | 51 | 10 | 5.00% | True |
| 25 | test:short (short) | 1438 | 120/120 | 57 | 10 | 5.56% | True |
| 25 | test:long (long) | 4929 | 160/160 | 55 | 10 | 10.94% | True |
| 25 | test:greek_latin (greek_latin) | 1572 | 160/160 | 43 | 8 | 6.25% | True |
| 25 | test:historical_russian (historical_russian) | 459 | 120/120 | 6 | 1 | 16.67% | False |
| 25 | test:modern_cyrillic (Serbian-only) | 332 | 48/160 | 3 | 1 | 33.33% | False |
| 25 | test:latin (latin) | 6186 | 160/160 | 43 | 8 | 5.21% | True |
| 25 | test:poly_dictionary_journal (poly_dictionary_journal) | 4619 | 160/160 | 12 | 2 | 10.42% | False |
| 25 | test:polytonic (polytonic) | 2724 | 360/360 | 22 | 6 | 6.44% | True |
| 25 | test:monotonic (monotonic) | 2575 | 240/240 | 77 | 1 | 1.39% | False |
| 25 | dev:vertical_turned (vertical_turned) | 2269 | 25/25 | 25 | 2 | 20.00% | False |
| 25 | dev:font_extremes (font_extremes) | 809 | 25/25 | 12 | 4 | 29.03% | True |
| 25 | dev:degraded (degraded) | 373 | 25/25 | 13 | 4 | 30.00% | True |
| 25 | dev:curved_skewed (curved_skewed) | 251 | 25/25 | 12 | 4 | 26.67% | True |
| 25 | dev:numeric_cells (numeric_cells) | 808 | 50/50 | 33 | 4 | 5.00% | True |
| 25 | dev:caps_headings (caps_headings) | 489 | 30/30 | 15 | 3 | 36.11% | True |
| 25 | dev:leaders_dashes (leaders_dashes) | 368 | 25/25 | 11 | 4 | 26.67% | True |
| 25 | dev:short (short) | 235 | 30/30 | 14 | 4 | 27.78% | True |
| 25 | dev:long (long) | 150 | 40/40 | 13 | 4 | 25.00% | True |
| 25 | dev:greek_latin (greek_latin) | 17 | 17/40 | 6 | 3 | 29.41% | False |
| 25 | dev:historical_russian (historical_russian) | 0 | 0/30 | 0 | 0 | 0.00% | False |
| 25 | dev:modern_cyrillic (Serbian-only) | 198 | 12/40 | 2 | 1 | 50.00% | False |
| 25 | dev:latin (latin) | 14 | 14/40 | 6 | 4 | 42.86% | False |
| 25 | dev:poly_dictionary_journal (poly_dictionary_journal) | 0 | 0/40 | 0 | 0 | 0.00% | False |
| 25 | dev:polytonic (polytonic) | 373 | 50/90 | 2 | 2 | 50.00% | False |
| 25 | dev:monotonic (monotonic) | 582 | 60/60 | 26 | 1 | 4.17% | False |
| 50 | test:vertical_turned (vertical_turned) | 3095 | 100/100 | 46 | 10 | 9.17% | True |
| 50 | test:font_extremes (font_extremes) | 12347 | 100/100 | 54 | 10 | 5.00% | True |
| 50 | test:degraded (degraded) | 2611 | 100/100 | 54 | 10 | 5.00% | True |
| 50 | test:curved_skewed (curved_skewed) | 2871 | 100/100 | 55 | 10 | 5.83% | True |
| 50 | test:numeric_cells (numeric_cells) | 4635 | 200/200 | 67 | 10 | 10.42% | True |
| 50 | test:caps_headings (caps_headings) | 1205 | 120/120 | 98 | 6 | 8.33% | True |
| 50 | test:leaders_dashes (leaders_dashes) | 6899 | 100/100 | 51 | 10 | 5.00% | True |
| 50 | test:short (short) | 1438 | 120/120 | 57 | 10 | 5.56% | True |
| 50 | test:long (long) | 4929 | 160/160 | 55 | 10 | 10.94% | True |
| 50 | test:greek_latin (greek_latin) | 1572 | 160/160 | 43 | 8 | 6.25% | True |
| 50 | test:historical_russian (historical_russian) | 459 | 120/120 | 6 | 1 | 16.67% | False |
| 50 | test:modern_cyrillic (Serbian-only) | 332 | 48/160 | 3 | 1 | 33.33% | False |
| 50 | test:latin (latin) | 6186 | 160/160 | 43 | 8 | 5.21% | True |
| 50 | test:poly_dictionary_journal (poly_dictionary_journal) | 4619 | 160/160 | 12 | 2 | 10.42% | False |
| 50 | test:polytonic (polytonic) | 2724 | 360/360 | 22 | 6 | 11.57% | True |
| 50 | test:monotonic (monotonic) | 2575 | 240/240 | 77 | 1 | 1.39% | False |
| 50 | dev:vertical_turned (vertical_turned) | 2269 | 25/25 | 25 | 2 | 20.00% | False |
| 50 | dev:font_extremes (font_extremes) | 809 | 25/25 | 12 | 4 | 29.03% | True |
| 50 | dev:degraded (degraded) | 373 | 25/25 | 13 | 4 | 30.00% | True |
| 50 | dev:curved_skewed (curved_skewed) | 251 | 25/25 | 12 | 4 | 26.67% | True |
| 50 | dev:numeric_cells (numeric_cells) | 808 | 50/50 | 33 | 4 | 5.00% | True |
| 50 | dev:caps_headings (caps_headings) | 489 | 30/30 | 15 | 3 | 36.11% | True |
| 50 | dev:leaders_dashes (leaders_dashes) | 368 | 25/25 | 11 | 4 | 26.67% | True |
| 50 | dev:short (short) | 235 | 30/30 | 14 | 4 | 27.78% | True |
| 50 | dev:long (long) | 150 | 40/40 | 13 | 4 | 25.00% | True |
| 50 | dev:greek_latin (greek_latin) | 17 | 17/40 | 6 | 3 | 29.41% | False |
| 50 | dev:historical_russian (historical_russian) | 0 | 0/30 | 0 | 0 | 0.00% | False |
| 50 | dev:modern_cyrillic (Serbian-only) | 198 | 12/40 | 2 | 1 | 50.00% | False |
| 50 | dev:latin (latin) | 14 | 14/40 | 6 | 4 | 42.86% | False |
| 50 | dev:poly_dictionary_journal (poly_dictionary_journal) | 0 | 0/40 | 0 | 0 | 0.00% | False |
| 50 | dev:polytonic (polytonic) | 373 | 90/90 | 2 | 2 | 50.00% | False |
| 50 | dev:monotonic (monotonic) | 582 | 60/60 | 26 | 1 | 4.17% | False |

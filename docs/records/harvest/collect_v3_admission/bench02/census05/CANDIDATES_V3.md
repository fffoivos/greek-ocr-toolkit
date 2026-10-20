# BENCH02L candidates v3

- Output SHA-256: `0432c56f75ed1efded00b76e7aeabcc0a2bf9441bfad00e825e4e105006134c2`
- Output bytes: 4102669
- Output lines: 3341
- Input SHA-256: `70a29c202691584a3382e77505ef56db7b9a0d1347fa5ac2eccc95ac8e9acfe5`
- counts.json SHA-256: `5e1c0a7432af92c34f5d9d2c0c705cf1eb98461b96defbf3ff7b11e029e8458f`
- draw_plan.json SHA-256: `8007e93ff170fdf897d4604d5c6bffe5725317cec226ab16f33ecc31c3b0ddb7`

Quotas come from counts.json classes and are cross-checked against draw_plan.json quotas, dev_quotas and subquotas. Subgroup quotas are cross-checked between both files. Subgroup tags are cyrillic_language for modern_cyrillic and font_size for font_extremes.

quota_scope is split:class, extended with :subgroup for every recorded subgroup quota. For ordinary scopes, scope_rank is the original rank. For subgroup scopes, sort the class rows by original numeric rank, restrict to that subgroup, and number from 1. JSONL emission order is never used as draw rank. in_quota is scope_rank <= scope quota; overdraw_order is null in quota and scope_rank - scope quota otherwise. Reserve use follows increasing overdraw_order within scope; a replacement must also share split, class and source with the replaced row. No replacements are performed.

Original JSON member bytes are retained; only four members are appended. Row keys are (parent_id, row_id). All scopes, including empty scopes, appear below.

| Scope | Quota | In quota | Reserve |
| --- | ---: | ---: | ---: |
| dev:caps_headings | 30 | 30 | 6 |
| dev:curved_skewed | 25 | 25 | 5 |
| dev:degraded | 25 | 25 | 5 |
| dev:font_extremes:large | 12 | 12 | 3 |
| dev:font_extremes:small | 13 | 13 | 3 |
| dev:greek_latin | 40 | 15 | 0 |
| dev:historical_russian | 30 | 0 | 0 |
| dev:latin | 40 | 3 | 0 |
| dev:leaders_dashes | 25 | 25 | 5 |
| dev:long | 40 | 40 | 8 |
| dev:modern_cyrillic:bg | 10 | 0 | 0 |
| dev:modern_cyrillic:ru | 10 | 0 | 0 |
| dev:modern_cyrillic:sr | 10 | 10 | 2 |
| dev:modern_cyrillic:uk | 10 | 0 | 0 |
| dev:monotonic | 60 | 60 | 12 |
| dev:numeric_cells | 50 | 50 | 10 |
| dev:poly_dictionary_journal | 40 | 0 | 0 |
| dev:polytonic | 90 | 90 | 10 |
| dev:short | 30 | 30 | 6 |
| dev:vertical_turned | 25 | 25 | 5 |
| test:caps_headings | 120 | 120 | 24 |
| test:curved_skewed | 100 | 100 | 20 |
| test:degraded | 100 | 100 | 20 |
| test:font_extremes:large | 50 | 50 | 10 |
| test:font_extremes:small | 50 | 50 | 10 |
| test:greek_latin | 160 | 160 | 32 |
| test:historical_russian | 120 | 120 | 24 |
| test:latin | 160 | 160 | 32 |
| test:leaders_dashes | 100 | 100 | 20 |
| test:long | 160 | 160 | 32 |
| test:modern_cyrillic:bg | 40 | 0 | 0 |
| test:modern_cyrillic:ru | 40 | 0 | 0 |
| test:modern_cyrillic:sr | 40 | 40 | 8 |
| test:modern_cyrillic:uk | 40 | 0 | 0 |
| test:monotonic | 240 | 240 | 48 |
| test:numeric_cells | 200 | 200 | 40 |
| test:poly_dictionary_journal | 160 | 160 | 32 |
| test:polytonic | 360 | 360 | 72 |
| test:short | 120 | 120 | 24 |
| test:vertical_turned | 100 | 100 | 20 |

| Split/class | Credited | In quota | Drawn - credited | Reserve | Subgroup gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| dev:caps_headings | 30 | 30 | 6 | 6 | 0 |
| dev:curved_skewed | 25 | 25 | 5 | 5 | 0 |
| dev:degraded | 25 | 25 | 5 | 5 | 0 |
| dev:font_extremes | 25 | 25 | 6 | 6 | 0 |
| dev:greek_latin | 15 | 15 | 0 | 0 | 0 |
| dev:historical_russian | 0 | 0 | 0 | 0 | 0 |
| dev:latin | 3 | 3 | 0 | 0 | 0 |
| dev:leaders_dashes | 25 | 25 | 5 | 5 | 0 |
| dev:long | 40 | 40 | 8 | 8 | 0 |
| dev:modern_cyrillic | 12 | 10 | 0 | 2 | 2 |
| dev:monotonic | 60 | 60 | 12 | 12 | 0 |
| dev:numeric_cells | 50 | 50 | 10 | 10 | 0 |
| dev:poly_dictionary_journal | 0 | 0 | 0 | 0 | 0 |
| dev:polytonic | 90 | 90 | 10 | 10 | 0 |
| dev:short | 30 | 30 | 6 | 6 | 0 |
| dev:vertical_turned | 25 | 25 | 5 | 5 | 0 |
| test:caps_headings | 120 | 120 | 24 | 24 | 0 |
| test:curved_skewed | 100 | 100 | 20 | 20 | 0 |
| test:degraded | 100 | 100 | 20 | 20 | 0 |
| test:font_extremes | 100 | 100 | 20 | 20 | 0 |
| test:greek_latin | 160 | 160 | 32 | 32 | 0 |
| test:historical_russian | 120 | 120 | 24 | 24 | 0 |
| test:latin | 160 | 160 | 32 | 32 | 0 |
| test:leaders_dashes | 100 | 100 | 20 | 20 | 0 |
| test:long | 160 | 160 | 32 | 32 | 0 |
| test:modern_cyrillic | 48 | 40 | 0 | 8 | 8 |
| test:monotonic | 240 | 240 | 48 | 48 | 0 |
| test:numeric_cells | 200 | 200 | 40 | 40 | 0 |
| test:poly_dictionary_journal | 160 | 160 | 32 | 32 | 0 |
| test:polytonic | 360 | 360 | 72 | 72 | 0 |
| test:short | 120 | 120 | 24 | 24 | 0 |
| test:vertical_turned | 100 | 100 | 20 | 20 | 0 |

| Split | Credited | In quota | Reserve | Subgroup gap |
| --- | ---: | ---: | ---: | ---: |
| test | 2348 | 2340 | 468 | 8 |
| dev | 455 | 453 | 80 | 2 |

Scopes: 40; subgroup scopes: 12.

counts.json uses credited = min(drawn, class quota). For subgroup scopes the rule instead credits sum(min(subgroup drawn, subgroup quota)). The subgroup gap is the difference. Assertions require in_quota = credited - gap and reserve = drawn - credited + gap. Thus an unqualified in_quota = credited assertion is false wherever gap is nonzero; the input accounting is preserved.

Verified: unique input/output row keys; unique JSON member names; identical row order, row set and existing values; contiguous original class ranks; scope ranks and reserve order; all class and subgroup counts; second independent derivation byte-identical; written output read back byte-identical; input files unchanged.

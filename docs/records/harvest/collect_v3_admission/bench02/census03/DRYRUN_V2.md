# BENCH02I — census_03 dry draw v2

Offline metadata only, network OFF, no spend. Production defaults: 50 per class × edition; both forced pools. Sole split-identity reason only; no admission or benchmark qualification. BENCH02G dryrun/ preserved. Reproduce: `python3 -B bench02/run_ruled_draw.py` from collect_v3_admission/.

Tags: {'bytes': 32741890, 'sha256': '9f8f0c721766a95a10cece695726f8e9581214169f0fcde3abe46d3add46d26b', 'verified_against': 'argument'}. The old receipt is unchanged; coordinator-pinned checksum supplied by argument and checked. New extract receipts carry tags_sha256 and tags_bytes; census_05 wrapper requires receipt sha. Input hashes and exact deterministic selection/emission order are in dryrun_v2/draw_plan.json.

| Split | Class | Pre-filter | Eligible supply | Quota | Target | Drawn | Credited | Deficit | Editions | Sources | Top-edition share | ≥10 books / ≥3 sources |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| test | caps_headings | 1027 | 1026 | 120 | 144 | 144 | 120 | 0 | 104 | 1 | 1.39% | False |
| dev | caps_headings | 391 | 391 | 30 | 36 | 36 | 30 | 0 | 36 | 1 | 2.78% | False |
| test | curved_skewed | 1866 | 1863 | 100 | 120 | 120 | 100 | 0 | 52 | 10 | 11.67% | True |
| dev | curved_skewed | 182 | 182 | 25 | 30 | 30 | 25 | 0 | 15 | 4 | 23.33% | True |
| test | degraded | 927 | 922 | 100 | 120 | 120 | 100 | 0 | 49 | 8 | 6.67% | True |
| dev | degraded | 176 | 176 | 25 | 30 | 30 | 25 | 0 | 17 | 2 | 43.33% | False |
| test | font_extremes | 5039 | 5032 | 100 | 120 | 120 | 100 | 0 | 56 | 10 | 7.50% | True |
| dev | font_extremes | 400 | 400 | 25 | 31 | 31 | 25 | 0 | 18 | 3 | 38.71% | True |
| test | greek_latin | 32 | 32 | 160 | 192 | 32 | 32 | 128 | 19 | 1 | 15.62% | False |
| dev | greek_latin | 9 | 9 | 40 | 48 | 9 | 9 | 31 | 4 | 1 | 33.33% | False |
| test | historical_russian | 345 | 345 | 120 | 144 | 144 | 120 | 0 | 6 | 1 | 19.44% | False |
| dev | historical_russian | 0 | 0 | 30 | 36 | 0 | 0 | 30 | 0 | 0 | 0.00% | False |
| test | latin | 2969 | 2969 | 160 | 192 | 192 | 160 | 0 | 27 | 6 | 6.77% | True |
| dev | latin | 3 | 3 | 40 | 48 | 3 | 3 | 37 | 2 | 2 | 66.67% | False |
| test | leaders_dashes | 2458 | 2430 | 100 | 120 | 120 | 100 | 0 | 44 | 7 | 6.67% | True |
| dev | leaders_dashes | 198 | 198 | 25 | 30 | 30 | 25 | 0 | 17 | 3 | 26.67% | True |
| test | long | 1723 | 1720 | 160 | 192 | 192 | 160 | 0 | 54 | 8 | 15.10% | True |
| dev | long | 49 | 49 | 40 | 48 | 48 | 40 | 0 | 8 | 2 | 31.25% | False |
| test | modern_cyrillic (Serbian-only) | 304 | 304 | 160 | 192 | 48 | 48 | 112 | 3 | 1 | 33.33% | False |
| dev | modern_cyrillic (Serbian-only) | 192 | 192 | 40 | 48 | 12 | 12 | 28 | 2 | 1 | 50.00% | False |
| test | monotonic | 2244 | 2229 | 240 | 288 | 288 | 240 | 0 | 76 | 1 | 1.39% | False |
| dev | monotonic | 548 | 548 | 60 | 72 | 72 | 60 | 0 | 26 | 1 | 4.17% | False |
| test | numeric_cells | 2261 | 2241 | 200 | 240 | 240 | 200 | 0 | 70 | 10 | 12.50% | True |
| dev | numeric_cells | 154 | 154 | 50 | 60 | 60 | 50 | 0 | 22 | 4 | 11.67% | True |
| test | poly_dictionary_journal | 0 | 0 | 160 | 192 | 0 | 0 | 160 | 0 | 0 | 0.00% | False |
| dev | poly_dictionary_journal | 0 | 0 | 40 | 48 | 0 | 0 | 40 | 0 | 0 | 0.00% | False |
| test | polytonic | 0 | 0 | 360 | 432 | 0 | 0 | 360 | 0 | 0 | 0.00% | False |
| dev | polytonic | 0 | 0 | 90 | 108 | 0 | 0 | 90 | 0 | 0 | 0.00% | False |
| test | short | 441 | 430 | 120 | 144 | 144 | 120 | 0 | 54 | 9 | 7.64% | True |
| dev | short | 63 | 63 | 30 | 36 | 36 | 30 | 0 | 21 | 3 | 25.00% | True |
| test | vertical_turned | 17 | 17 | 100 | 120 | 17 | 17 | 83 | 5 | 1 | 47.06% | False |
| dev | vertical_turned | 10 | 10 | 25 | 30 | 10 | 10 | 15 | 5 | 1 | 50.00% | False |

Dry v2 test: credit 1617/2460; drawn 1921; filled 11/16; deficit 843; subgroup-qualified filled 11/16.

Dry v2 dev: credit 344/615; drawn 407; filled 9/16; deficit 271; subgroup-qualified filled 9/16.

All-rows upper bound (not admitted) test: credit 2348/2460; drawn 2808; filled 15/16; deficit 112; subgroup-qualified filled 15/16.

All-rows upper bound (not admitted) dev: credit 468/615; drawn 546; filled 11/16; deficit 147; subgroup-qualified filled 11/16.

Forced-pool additions before caps/class selection (dry): {'pool_include_forced': 'both', 'added_rows': {'lqb': 14293, 'n1': 5221}, 'included_forced_editions': 99, 'locked_rows_never_drawable': True}; upper bound: {'pool_include_forced': 'both', 'added_rows': {'lqb': 42632, 'n1': 8920}, 'included_forced_editions': 99, 'locked_rows_never_drawable': True}.

Books diagnostic uses distinct edition IDs, including gazette issues; canonical-work independence is unverified. Series identity remains absent, so 3× per-class series cap is unverifiable. Polytonic and dictionary/journal deficits remain (sf7 pending); bg/uk have no supply, and modern Cyrillic is Serbian-only. Reopening forced editions restores historical Russian test supply (345 sole-reason rows, 120/120 credit); the earlier zero-supply test deficit no longer applies. Historical Russian dev still has no supply. No quota transfers.

## Subgroup deficits

| Split:class | Supply by subgroup | Drawn | Quotas | Deficits |
|---|---|---|---|---|
| test:modern_cyrillic | {"sr": 304} | {"sr": 48} | {"bg": 40, "ru": 40, "sr": 40, "uk": 40} | {"bg": 40, "ru": 40, "sr": 0, "uk": 40} |
| test:font_extremes | {"large": 2759, "small": 2273} | {"large": 60, "small": 60} | {"large": 50, "small": 50} | {"large": 0, "small": 0} |
| dev:modern_cyrillic | {"sr": 192} | {"sr": 12} | {"bg": 10, "ru": 10, "sr": 10, "uk": 10} | {"bg": 10, "ru": 10, "sr": 0, "uk": 10} |
| dev:font_extremes | {"large": 33, "small": 367} | {"large": 15, "small": 16} | {"large": 12, "small": 13} | {"large": 0, "small": 0} |

Full tag availability, cap-hit IDs, source/edition accounting and deficits are in dryrun_v2/counts.json. Fresh-cache replay produced identical candidates and counts; no locked rows drawn; candidates unique; original dryrun candidate checksum unchanged. Thresholds and classifier are unchanged. census_05 still requires admitted supply and its own receipt; the upper bound is not admission evidence.

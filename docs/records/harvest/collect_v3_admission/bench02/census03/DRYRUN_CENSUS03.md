# BENCH02G — census_03 mechanics dry draw

Offline metadata-only draw; no text/crop readout, image access, model call, submission, spend, benchmark qualification or seal. The exact Mac command in `../run_dryrun_census03.md` completed with Python 3.11.3, exit 0, and output in `dryrun/`. No code changed; the failure-triggered 34-test rerun was therefore not required. Existing unrelated workspace changes were left untouched.

## Receipt and coverage

| Check | Observed | Result |
|---|---|---|
| Decision join | 320,479 / 320,479 = 100% | Receipt verified arithmetically |
| Diagnostic join | 320,479 / 320,479 = 100%; unmatched 0 | Receipt verified arithmetically |
| W1/W2 output rows | 320479 | Matches receipt decisions, diagnostics and joined |
| collect-v3-W1-20261018-0524 | 101098 | W1/W2 decision-derived tags |
| collect-v3-W2-20261018-0524 | 219381 | W1/W2 decision-derived tags |
| Sole split-identity reason | 142959 | 142,959 expected; shortfall 0 |
| SPLIT rows | 320479 | 320,479 expected; shortfall 0; exact key-set equality |
| Duplicate tag keys | 0 | None |
| Admitted | 0 | No rows admitted |
| Dispositions | {'DROP': 14889, 'HOLD': 305590} | Full census W1/W2 |

The 142,959 count is the **sole-reason pool**, not the total census size. Other rows retain their reasons and never enter this dry pool. The current draw tool SHA-256 matches the extract receipt code hash. Both join rates are receipt claims with matching local row/key coverage; the remote decisions/diagnostics were not copied and were not independently rejoined here.

**Receipt shortfall:** `tags.jsonl.receipt.json` contains only source input hashes and a code hash; it contains no output tags SHA-256. Consequently transfer integrity **cannot be checked against the receipt**. Local `tags.jsonl.gz`: **32,741,890 bytes**, SHA-256 `9f8f0c721766a95a10cece695726f8e9581214169f0fcde3abe46d3add46d26b`. This is a newly measured local hash, not a remote receipt match. Obtain a coordinator-pinned output checksum before relying on the transfer for a real run; do not retroactively invent one in the extract receipt.

## Supply, quotas and deficits

Pre-filter means sole-reason rows before edition exclusions and split eligibility. Test/dev pre-filter columns below partition that pool by SPLIT; the eligible supply column is after v2/locked exclusions, before global caps. Primary classes use the unchanged precedence. Drawn includes 20% overdraw; credited = min(drawn, quota), so overdraw cannot fill another class. Font subgroup deficits are also reported separately below.

| Split | Class | Pre-filter | Eligible supply | Quota | Target | Drawn | Credited | Deficit |
|---|---|---|---|---|---|---|---|---|
| test | caps_headings | 1027 | 275 | 120 | 144 | 15 | 15 | 105 |
| dev | caps_headings | 391 | 391 | 30 | 36 | 36 | 30 | 0 |
| test | curved_skewed | 1866 | 135 | 100 | 120 | 20 | 20 | 80 |
| dev | curved_skewed | 182 | 182 | 25 | 30 | 30 | 25 | 0 |
| test | degraded | 927 | 173 | 100 | 120 | 35 | 35 | 65 |
| dev | degraded | 176 | 176 | 25 | 30 | 30 | 25 | 0 |
| test | font_extremes | 5039 | 283 | 100 | 120 | 77 | 77 | 23 |
| dev | font_extremes | 400 | 400 | 25 | 31 | 31 | 25 | 0 |
| test | greek_latin | 32 | 9 | 160 | 192 | 0 | 0 | 160 |
| dev | greek_latin | 9 | 9 | 40 | 48 | 0 | 0 | 40 |
| test | historical_russian | 345 | 0 | 120 | 144 | 0 | 0 | 120 |
| dev | historical_russian | 0 | 0 | 30 | 36 | 0 | 0 | 30 |
| test | latin | 2969 | 5 | 160 | 192 | 0 | 0 | 160 |
| dev | latin | 3 | 3 | 40 | 48 | 0 | 0 | 40 |
| test | leaders_dashes | 2458 | 200 | 100 | 120 | 0 | 0 | 100 |
| dev | leaders_dashes | 198 | 198 | 25 | 30 | 3 | 3 | 22 |
| test | long | 1723 | 17 | 160 | 192 | 0 | 0 | 160 |
| dev | long | 49 | 49 | 40 | 48 | 0 | 0 | 40 |
| test | modern_cyrillic | 304 | 222 | 160 | 192 | 0 | 0 | 160 |
| dev | modern_cyrillic | 192 | 192 | 40 | 48 | 0 | 0 | 40 |
| test | monotonic | 2244 | 496 | 240 | 288 | 0 | 0 | 240 |
| dev | monotonic | 548 | 548 | 60 | 72 | 2 | 2 | 58 |
| test | numeric_cells | 2261 | 271 | 200 | 240 | 11 | 11 | 189 |
| dev | numeric_cells | 154 | 154 | 50 | 60 | 24 | 24 | 26 |
| test | poly_dictionary_journal | 0 | 0 | 160 | 192 | 0 | 0 | 160 |
| dev | poly_dictionary_journal | 0 | 0 | 40 | 48 | 0 | 0 | 40 |
| test | polytonic | 0 | 0 | 360 | 432 | 0 | 0 | 360 |
| dev | polytonic | 0 | 0 | 90 | 108 | 0 | 0 | 90 |
| test | short | 441 | 80 | 120 | 144 | 0 | 0 | 120 |
| dev | short | 63 | 63 | 30 | 36 | 3 | 3 | 27 |
| test | vertical_turned | 17 | 17 | 100 | 120 | 13 | 13 | 87 |
| dev | vertical_turned | 10 | 10 | 25 | 30 | 9 | 9 | 16 |

**test:** pre-filter pool 21,825 (including unclassified); eligible pool 2,218; classifiable supply 2,183; quota 2,460; drawn 171; credited 171; deficit 2,289; classes filled 0/16.

**dev:** pre-filter pool 2,403 (including unclassified); eligible pool 2,403; classifiable supply 2,375; quota 615; drawn 168; credited 146; deficit 469; classes filled 4/16.

Pool accounting: {'all': 142959, 'post_dev': 2403, 'post_excluded': 19607, 'post_test': 2218, 'post_train': 118731, 'pre_dev': 2403, 'pre_test': 21825, 'pre_train': 118731}. Eligible test/dev unclassified total: 63; no quota is assigned to those rows. All-split primary supply: {'caps_headings': 11582, 'curved_skewed': 8727, 'degraded': 5096, 'font_extremes': 19265, 'greek_latin': 559, 'historical_russian': 345, 'latin': 12021, 'leaders_dashes': 19381, 'long': 14477, 'modern_cyrillic': 5031, 'monotonic': 34055, 'numeric_cells': 8550, 'short': 2704, 'unclassified': 1081, 'vertical_turned': 85}.

## Full-census tag and field availability

Denominator is all 320,479 extracted census_03 W1/W2 rows, replacing the historical 4,000-row sample. Available means the classifier emits an observed value (including False); it does not mean the tag fires. `short` is unavailable on cell rows by definition even when letter count exists. Cyrillic language availability includes not-applicable non-Cyrillic rows.

| Tag | Available | Unavailable |
|---|---|---|
| caps_headings | 320479 | 0 |
| cell_flag | 320479 | 0 |
| curved_skewed | 320479 | 0 |
| cyrillic_language | 319629 | 850 |
| degraded | 320479 | 0 |
| font_extremes | 320479 | 0 |
| font_size | 320479 | 0 |
| greek_latin | 320479 | 0 |
| historical_russian | 320479 | 0 |
| latin | 320479 | 0 |
| leaders_dashes | 320479 | 0 |
| letter_spaced | 0 | 320479 |
| long | 320479 | 0 |
| modern_cyrillic | 319629 | 850 |
| monotonic | 320479 | 0 |
| numeric_cells | 320479 | 0 |
| poly_dictionary_journal | 320479 | 0 |
| polytonic | 320479 | 0 |
| punctuation_heavy | 320479 | 0 |
| short | 233058 | 87421 |
| vertical_turned | 320479 | 0 |

Effective evidence combines the pinned snapshots and decision-bound slim evidence with the existing adapter precedence; present means non-null, including false/zero and explicit empty lists/strings. These are exported sufficient statistics, not an assertion that an optional field was present in every original decision. Slim-only counts distinguish census-carried evidence from snapshot completion.

| Evidence field | Effective present | Unavailable | Slim evidence present |
|---|---|---|---|
| source | 320479 | 0 | 320479 |
| primary_class | 320479 | 0 | 320479 |
| confidence | 320479 | 0 | 320479 |
| confidence_scope | 320479 | 0 | 320479 |
| leader_runs | 320479 | 0 | 320479 |
| emdash_label_count | 320479 | 0 | 320479 |
| cell_flag | 320479 | 0 | 320479 |
| A | 320479 | 0 | 320479 |
| turn_cw | 320479 | 0 | 320479 |
| source_width | 320479 | 0 | 320479 |
| source_height | 320479 | 0 | 320479 |
| xheight_px | 320479 | 0 | 320479 |
| ink_density | 0 | 320479 | 0 |
| degraded | 0 | 320479 | 0 |
| language | 0 | 320479 | 0 |
| languages | 0 | 320479 | 0 |
| baseline_angle_deg | 320479 | 0 | 320479 |
| curve_deviation_px | 320479 | 0 | 320479 |
| letter_spaced | 0 | 320479 | 0 |
| dash_tag | 49634 | 270845 | 49634 |

| Text facet / edition field | Present | Unavailable |
|---|---|---|
| text_facets.greek_letters | 320479 | 0 |
| text_facets.latin_letters | 320479 | 0 |
| text_facets.cyrillic_letters | 320479 | 0 |
| text_facets.letter_count | 320479 | 0 |
| text_facets.characters | 320479 | 0 |
| text_facets.numeric | 320479 | 0 |
| text_facets.has_upper | 320479 | 0 |
| text_facets.has_lower | 320479 | 0 |
| text_facets.punctuation_share | 320479 | 0 |
| text_facets.orthography | 320479 | 0 |
| text_facets.cyrillic_orthography | 320479 | 0 |
| text_facets.scripts | 320479 | 0 |
| text_facets.languages | 320479 | 0 |
| series | 0 | 320479 |

## Sources, editions and caps

Class × source counts below retain pre-filter and eligible supply as well as selected counts. TRAIN supply is shown for completeness; it cannot supply test/dev. Exact edition-level counts are in `dryrun/counts.json` (`pre_filter_class_source_edition`, `class_source_edition`).

| Split | Class | Source | Pre-filter | Eligible | Drawn |
|---|---|---|---|---|---|
| dev | caps_headings | gazette_modern | 391 | 391 | 36 |
| dev | curved_skewed | gazette_modern | 163 | 163 | 23 |
| dev | curved_skewed | kosmopolis | 5 | 5 | 4 |
| dev | curved_skewed | lekythos | 5 | 5 | 3 |
| dev | curved_skewed | serbia | 9 | 9 | 0 |
| dev | degraded | gazette_modern | 161 | 161 | 29 |
| dev | degraded | serbia | 15 | 15 | 1 |
| dev | font_extremes | gazette_modern | 384 | 384 | 23 |
| dev | font_extremes | lekythos | 1 | 1 | 1 |
| dev | font_extremes | serbia | 15 | 15 | 7 |
| dev | greek_latin | gazette_modern | 9 | 9 | 0 |
| dev | latin | kosmopolis | 2 | 2 | 0 |
| dev | latin | lekythos | 1 | 1 | 0 |
| dev | leaders_dashes | gazette_modern | 104 | 104 | 3 |
| dev | leaders_dashes | kosmopolis | 1 | 1 | 0 |
| dev | leaders_dashes | serbia | 93 | 93 | 0 |
| dev | long | gazette_modern | 33 | 33 | 0 |
| dev | long | serbia | 16 | 16 | 0 |
| dev | modern_cyrillic | serbia | 192 | 192 | 0 |
| dev | monotonic | gazette_modern | 548 | 548 | 2 |
| dev | numeric_cells | gazette_modern | 151 | 151 | 24 |
| dev | numeric_cells | kosmopolis | 1 | 1 | 0 |
| dev | numeric_cells | lekythos | 1 | 1 | 0 |
| dev | numeric_cells | serbia | 1 | 1 | 0 |
| dev | short | gazette_modern | 51 | 51 | 3 |
| dev | short | lekythos | 1 | 1 | 0 |
| dev | short | serbia | 11 | 11 | 0 |
| dev | unclassified | gazette_modern | 22 | 22 | 0 |
| dev | unclassified | lekythos | 1 | 1 | 0 |
| dev | unclassified | serbia | 5 | 5 | 0 |
| dev | vertical_turned | gazette_modern | 10 | 10 | 9 |
| test | caps_headings | gazette_modern | 1027 | 275 | 15 |
| test | curved_skewed | bsb_poly1850 | 109 | 0 | 0 |
| test | curved_skewed | elstat | 906 | 0 | 0 |
| test | curved_skewed | gazette_modern | 413 | 89 | 14 |
| test | curved_skewed | ia_greek_latin | 16 | 0 | 0 |
| test | curved_skewed | ia_poly1850 | 254 | 0 | 0 |
| test | curved_skewed | ia_russian | 83 | 0 | 0 |
| test | curved_skewed | kosmopolis | 5 | 5 | 5 |
| test | curved_skewed | lekythos | 1 | 1 | 1 |
| test | curved_skewed | nlg | 29 | 28 | 0 |
| test | curved_skewed | serbia | 50 | 12 | 0 |
| test | degraded | bsb_poly1850 | 54 | 0 | 0 |
| test | degraded | elstat | 68 | 0 | 0 |
| test | degraded | gazette_modern | 516 | 158 | 32 |
| test | degraded | ia_greek_latin | 37 | 0 | 0 |
| test | degraded | ia_poly1850 | 182 | 0 | 0 |
| test | degraded | ia_russian | 37 | 0 | 0 |
| test | degraded | nlg | 17 | 7 | 0 |
| test | degraded | serbia | 16 | 8 | 3 |
| test | font_extremes | bsb_poly1850 | 50 | 0 | 0 |
| test | font_extremes | elstat | 1383 | 0 | 0 |
| test | font_extremes | gazette_modern | 775 | 253 | 65 |
| test | font_extremes | ia_greek_latin | 219 | 0 | 0 |
| test | font_extremes | ia_poly1850 | 1874 | 0 | 0 |
| test | font_extremes | ia_russian | 649 | 0 | 0 |
| test | font_extremes | kosmopolis | 1 | 1 | 1 |
| test | font_extremes | lekythos | 2 | 2 | 2 |
| test | font_extremes | nlg | 34 | 14 | 4 |
| test | font_extremes | serbia | 52 | 13 | 5 |
| test | greek_latin | gazette_modern | 32 | 9 | 0 |
| test | historical_russian | ia_russian | 345 | 0 | 0 |
| test | latin | bsb_poly1850 | 1444 | 0 | 0 |
| test | latin | elstat | 214 | 0 | 0 |
| test | latin | gazette_modern | 4 | 2 | 0 |
| test | latin | ia_greek_latin | 224 | 0 | 0 |
| test | latin | ia_poly1850 | 1080 | 0 | 0 |
| test | latin | kosmopolis | 3 | 3 | 0 |
| test | leaders_dashes | bsb_poly1850 | 629 | 0 | 0 |
| test | leaders_dashes | elstat | 15 | 0 | 0 |
| test | leaders_dashes | gazette_modern | 802 | 119 | 0 |
| test | leaders_dashes | ia_greek_latin | 62 | 0 | 0 |
| test | leaders_dashes | ia_poly1850 | 493 | 0 | 0 |
| test | leaders_dashes | ia_russian | 299 | 0 | 0 |
| test | leaders_dashes | serbia | 158 | 81 | 0 |
| test | long | bsb_poly1850 | 91 | 0 | 0 |
| test | long | elstat | 11 | 0 | 0 |
| test | long | gazette_modern | 446 | 15 | 0 |
| test | long | ia_greek_latin | 86 | 0 | 0 |
| test | long | ia_poly1850 | 733 | 0 | 0 |
| test | long | ia_russian | 179 | 0 | 0 |
| test | long | kosmopolis | 1 | 1 | 0 |
| test | long | serbia | 176 | 1 | 0 |
| test | modern_cyrillic | serbia | 304 | 222 | 0 |
| test | monotonic | gazette_modern | 2244 | 496 | 0 |
| test | numeric_cells | bsb_poly1850 | 121 | 0 | 0 |
| test | numeric_cells | elstat | 1398 | 0 | 0 |
| test | numeric_cells | gazette_modern | 435 | 237 | 4 |
| test | numeric_cells | ia_greek_latin | 9 | 0 | 0 |
| test | numeric_cells | ia_poly1850 | 180 | 0 | 0 |
| test | numeric_cells | ia_russian | 43 | 0 | 0 |
| test | numeric_cells | kosmopolis | 7 | 7 | 2 |
| test | numeric_cells | lekythos | 6 | 6 | 5 |
| test | numeric_cells | nlg | 17 | 17 | 0 |
| test | numeric_cells | serbia | 45 | 4 | 0 |
| test | short | bsb_poly1850 | 33 | 0 | 0 |
| test | short | elstat | 112 | 0 | 0 |
| test | short | gazette_modern | 162 | 69 | 0 |
| test | short | ia_greek_latin | 16 | 0 | 0 |
| test | short | ia_poly1850 | 80 | 0 | 0 |
| test | short | ia_russian | 17 | 0 | 0 |
| test | short | kosmopolis | 1 | 1 | 0 |
| test | short | lekythos | 1 | 1 | 0 |
| test | short | serbia | 19 | 9 | 0 |
| test | unclassified | bsb_poly1850 | 5 | 0 | 0 |
| test | unclassified | elstat | 57 | 0 | 0 |
| test | unclassified | gazette_modern | 76 | 31 | 0 |
| test | unclassified | ia_greek_latin | 3 | 0 | 0 |
| test | unclassified | ia_poly1850 | 22 | 0 | 0 |
| test | unclassified | ia_russian | 5 | 0 | 0 |
| test | unclassified | lekythos | 1 | 1 | 0 |
| test | unclassified | nlg | 3 | 3 | 0 |
| test | vertical_turned | gazette_modern | 17 | 17 | 13 |
| train | caps_headings | gazette_modern | 10164 | 10164 | 0 |
| train | curved_skewed | bsb_poly1850 | 400 | 400 | 0 |
| train | curved_skewed | elstat | 925 | 925 | 0 |
| train | curved_skewed | gazette_modern | 4385 | 4385 | 0 |
| train | curved_skewed | ia_greek_latin | 194 | 194 | 0 |
| train | curved_skewed | ia_poly1850 | 384 | 384 | 0 |
| train | curved_skewed | kosmopolis | 37 | 37 | 0 |
| train | curved_skewed | lekythos | 47 | 47 | 0 |
| train | curved_skewed | nlg | 138 | 138 | 0 |
| train | curved_skewed | serbia | 169 | 169 | 0 |
| train | degraded | bsb_poly1850 | 162 | 162 | 0 |
| train | degraded | elstat | 82 | 82 | 0 |
| train | degraded | gazette_modern | 3106 | 3106 | 0 |
| train | degraded | ia_greek_latin | 110 | 110 | 0 |
| train | degraded | ia_poly1850 | 205 | 205 | 0 |
| train | degraded | kosmopolis | 2 | 2 | 0 |
| train | degraded | lekythos | 22 | 22 | 0 |
| train | degraded | nlg | 44 | 44 | 0 |
| train | degraded | serbia | 260 | 260 | 0 |
| train | font_extremes | bsb_poly1850 | 125 | 125 | 0 |
| train | font_extremes | elstat | 751 | 751 | 0 |
| train | font_extremes | gazette_modern | 6731 | 6731 | 0 |
| train | font_extremes | ia_greek_latin | 1746 | 1746 | 0 |
| train | font_extremes | ia_poly1850 | 4199 | 4199 | 0 |
| train | font_extremes | kosmopolis | 17 | 17 | 0 |
| train | font_extremes | lekythos | 34 | 34 | 0 |
| train | font_extremes | nlg | 32 | 32 | 0 |
| train | font_extremes | serbia | 191 | 191 | 0 |
| train | greek_latin | gazette_modern | 518 | 518 | 0 |
| train | latin | bsb_poly1850 | 2932 | 2932 | 0 |
| train | latin | elstat | 504 | 504 | 0 |
| train | latin | gazette_modern | 269 | 269 | 0 |
| train | latin | ia_greek_latin | 2048 | 2048 | 0 |
| train | latin | ia_poly1850 | 3270 | 3270 | 0 |
| train | latin | kosmopolis | 11 | 11 | 0 |
| train | latin | lekythos | 9 | 9 | 0 |
| train | latin | nlg | 6 | 6 | 0 |
| train | leaders_dashes | bsb_poly1850 | 1273 | 1273 | 0 |
| train | leaders_dashes | elstat | 70 | 70 | 0 |
| train | leaders_dashes | gazette_modern | 12682 | 12682 | 0 |
| train | leaders_dashes | ia_greek_latin | 421 | 421 | 0 |
| train | leaders_dashes | ia_poly1850 | 1202 | 1202 | 0 |
| train | leaders_dashes | kosmopolis | 1 | 1 | 0 |
| train | leaders_dashes | nlg | 9 | 9 | 0 |
| train | leaders_dashes | serbia | 1067 | 1067 | 0 |
| train | long | bsb_poly1850 | 632 | 632 | 0 |
| train | long | elstat | 21 | 21 | 0 |
| train | long | gazette_modern | 9039 | 9039 | 0 |
| train | long | ia_greek_latin | 789 | 789 | 0 |
| train | long | ia_poly1850 | 2068 | 2068 | 0 |
| train | long | kosmopolis | 6 | 6 | 0 |
| train | long | nlg | 1 | 1 | 0 |
| train | long | serbia | 149 | 149 | 0 |
| train | modern_cyrillic | serbia | 4535 | 4535 | 0 |
| train | monotonic | gazette_modern | 31263 | 31263 | 0 |
| train | numeric_cells | bsb_poly1850 | 590 | 590 | 0 |
| train | numeric_cells | elstat | 1580 | 1580 | 0 |
| train | numeric_cells | gazette_modern | 3273 | 3273 | 0 |
| train | numeric_cells | ia_greek_latin | 110 | 110 | 0 |
| train | numeric_cells | ia_poly1850 | 212 | 212 | 0 |
| train | numeric_cells | kosmopolis | 66 | 66 | 0 |
| train | numeric_cells | lekythos | 30 | 30 | 0 |
| train | numeric_cells | nlg | 166 | 166 | 0 |
| train | numeric_cells | serbia | 108 | 108 | 0 |
| train | short | bsb_poly1850 | 217 | 217 | 0 |
| train | short | elstat | 162 | 162 | 0 |
| train | short | gazette_modern | 1424 | 1424 | 0 |
| train | short | ia_greek_latin | 134 | 134 | 0 |
| train | short | ia_poly1850 | 96 | 96 | 0 |
| train | short | kosmopolis | 1 | 1 | 0 |
| train | short | lekythos | 7 | 7 | 0 |
| train | short | nlg | 10 | 10 | 0 |
| train | short | serbia | 149 | 149 | 0 |
| train | unclassified | bsb_poly1850 | 33 | 33 | 0 |
| train | unclassified | elstat | 74 | 74 | 0 |
| train | unclassified | gazette_modern | 704 | 704 | 0 |
| train | unclassified | ia_greek_latin | 6 | 6 | 0 |
| train | unclassified | ia_poly1850 | 26 | 26 | 0 |
| train | unclassified | kosmopolis | 5 | 5 | 0 |
| train | unclassified | lekythos | 8 | 8 | 0 |
| train | unclassified | nlg | 7 | 7 | 0 |
| train | unclassified | serbia | 18 | 18 | 0 |
| train | vertical_turned | gazette_modern | 58 | 58 | 0 |

Diversity target: ≥10 editions/books and ≥3 sources where supply allows. Counts refer to edition identities, including gazette issues; no extra canonical-work audit was performed. “Available” is post-exclusion class supply before earlier classes consume the global cap. Even nominally sufficient diversity can be lost to earlier classes; caps are shared globally across classes and overdraw, test then dev.

| Split | Class | Available editions | Available sources | Drawn editions | Drawn sources | Assessment |
|---|---|---|---|---|---|---|
| test | caps_headings | 42 | 1 | 13 | 1 | supply limited |
| test | curved_skewed | 33 | 5 | 14 | 3 | met |
| test | degraded | 26 | 3 | 17 | 2 | cap/order constrained |
| test | font_extremes | 34 | 5 | 34 | 5 | met |
| test | greek_latin | 6 | 1 | 0 | 0 | supply limited |
| test | historical_russian | 0 | 0 | 0 | 0 | supply limited |
| test | latin | 2 | 2 | 0 | 0 | supply limited |
| test | leaders_dashes | 19 | 2 | 0 | 0 | supply limited |
| test | long | 7 | 3 | 0 | 0 | supply limited |
| test | modern_cyrillic | 2 | 1 | 0 | 0 | supply limited |
| test | monotonic | 22 | 1 | 0 | 0 | supply limited |
| test | numeric_cells | 25 | 5 | 7 | 3 | cap/order constrained |
| test | poly_dictionary_journal | 0 | 0 | 0 | 0 | supply limited |
| test | polytonic | 0 | 0 | 0 | 0 | supply limited |
| test | short | 18 | 4 | 0 | 0 | cap/order constrained |
| test | vertical_turned | 5 | 1 | 5 | 1 | supply limited |
| dev | caps_headings | 47 | 1 | 35 | 1 | supply limited |
| dev | curved_skewed | 40 | 4 | 25 | 3 | met |
| dev | degraded | 31 | 2 | 30 | 2 | supply limited |
| dev | font_extremes | 29 | 3 | 23 | 3 | met |
| dev | greek_latin | 4 | 1 | 0 | 0 | supply limited |
| dev | historical_russian | 0 | 0 | 0 | 0 | supply limited |
| dev | latin | 2 | 2 | 0 | 0 | supply limited |
| dev | leaders_dashes | 20 | 3 | 3 | 1 | cap/order constrained |
| dev | long | 8 | 2 | 0 | 0 | supply limited |
| dev | modern_cyrillic | 2 | 1 | 0 | 0 | supply limited |
| dev | monotonic | 26 | 1 | 2 | 1 | supply limited |
| dev | numeric_cells | 22 | 4 | 19 | 1 | cap/order constrained |
| dev | poly_dictionary_journal | 0 | 0 | 0 | 0 | supply limited |
| dev | polytonic | 0 | 0 | 0 | 0 | supply limited |
| dev | short | 21 | 3 | 3 | 1 | cap/order constrained |
| dev | vertical_turned | 5 | 1 | 5 | 1 | supply limited |

**71 edition-cap hits at 4/edition**; maximum selected per edition 4. No evidenced series and no series-cap hits; the 12/series rule cannot be certified for unknown series. Unknown-series eligible rows: 824. Zero selection from blocked editions. Earlier physical classes consume most edition capacity, explaining later zero draws despite positive supply.

Cap-hit edition IDs (exact list):

```
03b27335c85fcb18e216ca1194bd43235b51f38b35ad47f630894c2307b57d29
06b4b25e7b51bc1b5cd0a3d14a67a60072f1f33b35610c629c91287d859dd285
0afc99184712063617f5afeed126827f73042916b598b34f5a324007792a8b39
0e29b3aa977c54063d7c9f4019cbcf864090f515be9e6bc9fc6c0b04cd5de36b
0e2b4531d9dc55cdf4abcec8762d40a25c0dc733685a86813a4bb92ed3c50d45
1126ec81ce710a09e54a0c7f901cc19544f121d230bd71d82ba034bdcf59da40
122c52e696f5f8931b1b06c37362373dc2bdb2739f9a17b80a30b1917c100e99
127e84606fb866d5632e1b3fdba9893834c724e3624ad8dfa6e52767bf10be88
14fe2e5c867fca351ad823c2c9f10b77e55b745ad307b9e9cc7fbe687e4b8e18
16fe9bf0b7a79b3b2e6f6802ca5cefd0fad3bdd3256a769e7e841dde61892d54
20f34f4d3a8812c7f0a9c78e311622a1bb158b9acd97e3253a3a967eef21ed4c
2243615b69482200ad6bc58eef9ba4a893abaa61057ef897ed87adb2d71783e6
226ce6f6209078bfecc19723b1ec5052afb8688b4ad968dbd5e19b6f3562f9eb
2567909b79ce07ac4835d427efb84556a8f670cb88a52953412605eaf8268eb2
2bb08c6f8a18ab56777e60830effa94296d6cab4fe1e3fc98d95a5deec31b960
375986327b90672912cc2440ee37fb6f22108372809cfc78de1d4b52d82d91fb
3834b97376db3c988d03f5977ebf1a5e8696d65bb3f700c5830b65bb12bac97b
3c56acbc8645d31c029cad2b126ce9324f032e2b9bfe62734f71f3e430a6f3fc
44f1ac8307a18563290639581c5f7cafffb64b93c63b1e0c3c7c5b19827f9dd0
45c40588d6e8f066e53e4a365e79397446ef04adc2db4b595eecd1f0596c0aa4
46f03884e639fc5397dd81d473d8aa3970fef49e9437893321d905a724f30e70
4c7b11dc80af47c29076407825fc80d67f915ee56a252774d59be4fc4bae3061
4dd7d90a923969f169190c62fd8b6eb138f9835901c2bf9b799d3240e6df12dc
51828dcc6dd72d571937e51c6f225d5482cdef70592432e752d0275a5c9b2bc3
537f66dbf396e3a10ce2c5abe50ec1b0558c1d71895a53a2965c9d7859b28e28
54c8b4fe94b933406e2f7bf5bd57f93f39d8e2029eba551970d84332a27f5396
5d3825eaa4ef117af37bdde77b8e0586a3ba847a8b9156c6a1f84e78883a15b3
622a268a2d2f2ff2bceec53645d2f8763f21b6829a7fbfba4382b80d1fdcc1ef
670b9b27cb2684de8c5ca72407f6713f0147586ab456e1c0082914691b66aa5c
6a8fcf970921a1ba02694f2e16fbe756fb9a4299b1b2f2192f6b62fbd6480c31
6c71a172b878ba42db7e6d2584b764c022d13dc04ee42c1bb478d8b542df94a0
6e16606623611fcd9cbf933c7444e506ffa02be08605d86281265c67b96bb30e
6f76cf215bb9ba2dc3c78432d6a30ff866b424c6866f9f0b86b34c073dea06d0
7062c762bf8e4b4eb04437b1ccde9e56098ba37ed10284d5728150c47eeedb8e
7590163209399d3dcfb80aedbf8bbdcbde740db05bfb194722cdb6f9662b6e5d
80bd4802d0fd6e98ff00743a8f5f4899a3d4d7aae8a584a094c8390f9d6935d0
84e1225e79ecfd06e41af5cbe9dc9a125d019b699e7e502e5f7fcee75efe7e8a
8e6fc11fae7f09c83825213b8051db7fed299b2ca37498a8c7a34cd35b074e34
8ee3a5d3931367efbed4236efed55ffdf1660f03284e389355141c58b49d7c47
97a4decf1cfc19409ba8fd03faa04b6869c179096ed9943a30f315634e058068
9b728da2293153c02dfb3ae6f41794f9f8d18c339bd93e625860597123906902
9cd3ff0e43e7fab7142a9ac36b64bfb55d452640eb2366a5e52cbc0719a7ec55
a707367f6aecc2cca441bc898142231f06da09a2f87bfa5b6dba94fe5b475b5d
a89289d17d133462b7556b0b60f079955b0a3556eff3c7a9cc1d7727c0ef2770
ab99ee266557d66af077a3c04a54c89bdf3eb439780f65bee16c78f5a7bb8e73
adc7fb2bcf3716107bacaaecebfca3e84bb97a07bfb791afab2867e7a5c7769a
b135560d4c8a226723ca8df0d3afab2be27d402413f4086a87e2260702036494
b77a55dbbbbd5ac7ead7e0398cb8c22e38dcb8ae83671e246185f2f2fc83ae1b
b811f9750334b9c8cd949647db3ec80cdd8d136283a5df67dd60e4cefa821716
b864d188c49355b3268530b7e8008b01539b52ee2b18cb5fe2780db40396d0ed
bae72c1716a4a4045ac64ec4defcb534b382d62fef5e7c739fe7de696d81ad81
c3ca9df71a477c6858452d456fb5959c687a8a4fbb013f85378ed5e34a896c81
c43c3a6d3e59298cbc54b18bd4e5421a55eb8a91dc2261f537ed79bb4736bc91
c733af18179f1f9dd0e0ef7e9999be056592377ccbaccbd572ad5bef9a18a3d4
cbcaf8e7e00197d0ce9f8974841d3ca76b7e3048cff9bf4a6d3a6e3d5b65f1af
cede4459e5b91943e6ce1c8472ff54745e5c9612926fea2a8cfbd33c32986de3
de59beeef40cab7dbb01d92acb1536765f5e9677b3670e91e17da245ec95e6a5
e02729f2e120e89a366bcdc6a322273dfb92f0848021fbf835c0bca3de1ed276
e03e0a718ee7b769da2dd3b980189dedf13ea23f690af09eb838cc0681845372
e188d43e638068033ada7a7456aa416e97d31a88dc3f23f6c5f471f2b6106e2d
e1cc93f699b4749f649235939f1562def7667afce0961a653b457c33153b19ec
e9a1481a8ac822fdcf8b8488856cfa3ca3cfa32b23a6315ddbfc8b9231f1f681
eac5106e61f660176818b1a49e3e201ac7312b9684451a4135acb4cc239dfd7a
ece01e1561d16263b2c00c8a8fdcb6370b22e600e0a0857d19282208ff2b0b17
ed1efaa4e6c14c0945136dd4230a64d12a96423e0a4bb7facaac891eee170ab6
f231f55617b9a933529999808c8e10745588f33dfb19ed066db613ea40c6a387
f5409c9de8b82c69f05c6f25247ca148319325a96a491c1077137a851885ce02
f5e060bea73601774ec994ca819083cb6a1e7b87d707b17ea4b9db00106abd83
fa272b26c26abff7ab76cb8028f298e584ab29cc2ea42a56cc88883df7bb4bad
fb9e2f514f15461698a092aff3b8f74f5c1fd8055b323cc6c2036c0544c340b2
fcb034a9647a6734bf1fc1324883fd0564f0b4e5deab24ec6d394637ee76f5b3
```

**Excluded editions: 99**, including 99 forced-test editions; 19,607 sole-reason rows removed. Exclusion is the union of existing v2 leakage witnesses, direct v2 document/row membership and registered locked/eval row membership. The tool checks locked-file hashes; unrelated release exclusions do not become draw filters. Exact IDs:

```
015c0ba74ce41bcb3906b7e909001f75b0a5724d7a5b10458c497debe9721842
05dc9147e50b0c7db2388df16c630d78bb06feadf8817603d230102ff8956972
0880c76931b1c5193c4b01c05cc9a79ce215693176061eca3906513bcecbda1a
0955f1ae5b85cf4d6db977abaf74c0ea16d79a95105133fe63021eac3149593b
0a7c168e74130e72ece9460ff4100974eab7c0a261483f6355ea4461f5b5a32f
0f5b2b8a00bde53d9f1b8c31a33837c0e14515332ea2bf2f6252dea39ba78b48
12903d5ae5ca6064f0e766239dec6aaa7910348d50db283ab78991cc1a6cf0bb
12ad489a9f8456e15527823a675ada36b87e636200f94e37006d0ee6ddb9fe8f
16dba3fe048be0230b4756c30816769aba3f2bc5777c0e4dbeec4441af65d487
1757c91e057aaa3de6638a90596f0dd30ae14b5be4c2ac349e08ddc38b94ace8
18aba2916d132f0adcc76d1dc756dfe447257e2d71edb3d2ce94233d454517bf
1972d955186299f8d30eb5bb0f777db64a8de01fe22f93e24b1f23691e0c66ae
1e1dca58e6841dbb5c6d475dbdd2594585b920a7acdb57bd6647eeada7774988
260c34514b5725d4229c88c4608bfdd765f8ad58ef8b61087dd3b65aebf0b954
289269c92c9ca090950360c85a6ce297ad53cc5e323f0cf73054b3026b5c82e7
2b445c37e207a8cf310054b15a3ce32f332a85a0f3f77ed9654f1223b450ecef
2b921667887eb8861f7b2f5fea2f185ce63fa162af989e21e2f6e155e23edf1b
2c4e1cab18ad1ba9390d9b06ea888f6c0d9a8a8691d01f183c06a54b0c70cd43
2f85612c5332296e6524c81427169173ca35925bb58c47f88d4ae7638f19db57
303339a4f321281eb3cef0171b45c5e45a84c5f07d11c22b6688974728286558
31458569111f019f027ce19e63660576dab7784b132ad0a5b7a10942e688c7e6
31fa4739de599c86533ec26235a479a444a96a19dc01ae79e7749623dc77d97e
325048e0774a4491bf09386816c5100f868a6cdbb5c4fd55ccd03b90011977a0
370a20a1091c641b17f4c63e5b5d683711450f5d49429ccd79b711dda5f22853
3d3c7cde1879a0a77dfec93a60fd7f3d4a135371eac6f58a532664226d1a2fd5
3fd44fc02574e39451851b21d053dae48498d1a0ffcc827b0d6b4d8fba880675
41e15241539b51d9d065b65a0d8b820718fb88b79330f79d2fdfcc811f215c69
468e2b06a76d74bc5316e52e5217f050277e379eaa749fc2d345c575ee0b137d
477bc6a0e95aa93bd9ae580b5bc774e67b03aec55701a77e60dbf9230d281421
49656020581aead5d52cb1a614f16e36ec2f80956964fef38f530c81d45bd0d2
49c4a0151714a8a8c28c02c1036453e2ed2ef9a96f869aaaa8d0ae6aad20b6c4
4afb6d84159a7b877d4aa9cc2c1d4f89ba8c58991e9bd096e304533f092b7d41
501a76594b7ef62a76f57aad3f7e28a44c620c467c90cc3c24f368740196f32a
5168de5ebd93816ce747d4a67e4a10c9e30d87673b5712d76547469295fb42d1
51edc2caa1db92329467082e12392c6e618c1e1958479dcb39906ff81020c100
58e15ad074d80b9cada05956079b1849eb51265b4f5ce8b55d09c61d428bbd0c
5c89485ca163b98decf08e0e0328ea57b406ee2847ce17c9e43c3b0445aab252
5cfd57c87d312a7784947762b77b39ffd280eefcff8b9a48b7293137fc1e3a18
5f39777d933a653d3181d62eaba7152583f752ccebf8291ac38e407cb09726a8
5fa5b5010ae8a173cea438f1301ce67c63654caff567952ddf2a107d90bf3c44
663d271c1e62df828e74abdb671535f259f6a8a63651c457b8a2952e022d4f63
6a21fa88b40646133111580b7306ed23a82fe0b09cb35280fb2d732a8e0316d3
6b43da53d9af47b1ccc64358e81d57b05d7fba50a5ced2f69e2fcc77af600e2d
6f5e05fdb36c4f4ba15138d21058b74a86d6184a6ca302c2854d66f05d52e3e0
70893655d8639e7382689aaa3077899cb2e3395ac5ac5974bb43c36e12cbaada
72390a48aa70ffe7eed8fb5f67494712f070f249f7345489e33c56bb62b2d2f3
72d722f66cb91371c585e1cc44af2502a685db83948dceb5cd820e7d27a33194
732bb792c49492e8aa6fb36bfa0866cb7538575861ee41b94bd64280919e336e
74181cc4c7b320c7147977255a50c997a38560425d85c56492f4c966c3717ca0
74b27f3e4e1c10daeaab745e43b49fc4f18fbe5249e3b4ada94aa54b2de50288
7561b5b43f903ae84277bf1787b0573f88320a2cc9290d82992bbe0dcdcdf2f1
757cf60947a7932be8b6104862b215dd521aaf37402d72c286366b9b076b661c
77b253f461c3a43523a16b40dfffdd33497858d15b7ce060703a329e0af6e525
7b1f07a2736587139d2b787d154d8fd3df86b064639d214c71e6705d2b9dc2a3
7c3cf0fe680871c847c16a2d15ca1e6ee30c8c97f427ccf90c38e3cb0b9bf397
825cf24acf2ccb5fd89e6b84971b4b569bac9447457c95f2104e06f501223ba3
87d2cdaad8986deabcb8cab898bf78c2f4da8032146c1d9e9a2f466d19af72bd
8c621dfc2604609306c466c2f4ae21487b4c6e14d03c5294f422d83cbba82993
8cf451da3860158fcf6a4f2e38b2ed97eef87c53713d42b4624e1051f14efee5
8da94bf6ca4782708eef717da33e05ef948e150ae89b5b62895f0c2aa23840e9
8f41630b13df81b6e5b4464a51b6559e10dbf4f25f59fc0580914018a87945c7
93035a16fcec25a8b582a857c3ae087b9c14f2d1ead57bc24906adf6d017fcdb
93766ee844b67c5cd1bbda62b5e1005b3ca14da1d426fdf644f456980541ec5e
93dbf44a3ccc680642ef9694344c900cc84baef8bb76f4d4c59db464fae295ce
98914b5fa23a7fede57ff9907fec45607fbef0b036442e9e056c67b9b202370d
99d5b77b02b4707fe7812a629d4e0cfb72d641ef91f75a2e6774cb77f066e170
a116e24c8848c498ab12f9272c4904831436a903707c2565679617a4bb2b09a3
a2442c4e1557bd1c5ac80c94f85f6373703687be2ac6c79f4396fb1c87391fe7
a6b759877381b21ba7a1a7cf6d48075726853b8339ca3c5d5e77dd25ff19b18a
abed134094996130b0f0bb3d29f8c85870001d4c124ade025af18c5c5a9e1523
ad62d31c2f25dc6e5b37d00c600c8cab903aaf02a5a8b538e3e217e42679088b
b0c7613d634baa8442d6c2b5dffc135ab2612cce9babd823e8239753244e8792
b3a6aab194e0f3f11898cfd5f10b5944c9d3b5977724739654ebf1b996d90a47
b3ebf3d33fa72d1782fb15de99cb55cdd37ae6f98f45069db25ae538f6fdc281
b8e4bcedd85a33667de7477265437cd2a3d630c4749a73deb767b8ceaa69afdc
ba421f6597ca542afccd1be09977279c4d33a7f00287c6d9e607c0183560622a
bb9f7406bcbb94372db8f42fcf940962d6dfa1e5eadb2aa7105ac45ce7347932
bf38945a8164e660c44e92bf570b8cf9c22f486583b51f691ee2d650e2eec333
c1e5dc754740408f5503dde2b153ea2dddecadd42460fab27b2a4d848c555b4c
c4197c24c09fd893ee9253427881c42c2626cd7dfb0bbadb3d1bdeb99ea069f7
c5459c78e76b61004d7f898a7204bc8d6ea5d76999f5aefd7b17fe69896cff8a
c8f75b85d5869867a64b246b6a88f614cbb13e4c4de74fe59d967ad44dfc745a
cbbf7a7de2b00f92ff010a8863d1e962a3957b18d9e74495602571aecd602e2c
cd3d6362c67f97266b34e4fe000777524825f5de7d56e06f3907cde6c1aa4e95
ce1eae0102aaadda9d73b1db1e17f313913f66886fcbaf62ff205ae6427c1345
cf2c663848e3caa95fbb614497f24b33c9c9f666bb0cdbb3b1cc879616edf1fb
d2286794a8f7944f9f5074606ffdba93694ae469976cef1b5f581e516714bbe7
e1860e88970b2ff2aab3c4680db7467f4517b6172fa7fba918160b23ab8a4346
e1aa0c6d26ba8c0cc8c7d7eb6fd88c52b1004be434d27bd4729ac5aaadace358
e94db10b37e92f28d8d3f89b9cbfe5c1bcb0d3f8469a84432fbbe6d7ffb83b80
eeb2c20de8ca004b435e0d44e187d3e68f6a284953537d69b487f67432a148e9
f05bb84c49800c0908c2f61e1684a158656358e7e55b66f2e1a163f8d87b4534
f51c8432ef225559d5577a197912a3a8c9da6347f94b4672cada9f4282183e0b
f5b432d6947c6aedda32b25c2fe7317144cbe11e9e0b5eacbf3efdf939b8934d
f5d681e74fd9e8c747bf1b82c6a017c90bc6698b12ba0d510350396b2a2db338
f74d76a5fedb76e5ec7ef0c2c44681c69853581abc445257815058018b8095e6
f8d31f703b9cab2a76c74714a32d535b41e1756e56a893a7bc9c3219d2e8a8a4
fb187b7e611eb4e7721168e4588487fcad93a507d218df4df73d7d8683eeaca1
fed4b338619d08b233bd61870a9a2869f254f0c1ca32f33dc279a7468d61b776
```

## Modern Cyrillic and font subgroups

Subgroups below are primary-class pools, not secondary tag totals; pre is before exclusions, eligible after exclusions, drawn after shared caps. Missing groups never transfer quotas.

| Split | Class | Subgroup | Pre-filter | Eligible | Quota | Target | Drawn | Deficit |
|---|---|---|---|---|---|---|---|---|
| test | modern_cyrillic | ru | 0 | 0 | 40 | 48 | 0 | 40 |
| test | modern_cyrillic | sr | 304 | 222 | 40 | 48 | 0 | 40 |
| test | modern_cyrillic | bg | 0 | 0 | 40 | 48 | 0 | 40 |
| test | modern_cyrillic | uk | 0 | 0 | 40 | 48 | 0 | 40 |
| test | font_extremes | small | 2280 | 241 | 50 | 60 | 54 | 0 |
| test | font_extremes | large | 2759 | 42 | 50 | 60 | 23 | 27 |
| dev | modern_cyrillic | ru | 0 | 0 | 10 | 12 | 0 | 10 |
| dev | modern_cyrillic | sr | 192 | 192 | 10 | 12 | 0 | 10 |
| dev | modern_cyrillic | bg | 0 | 0 | 10 | 12 | 0 | 10 |
| dev | modern_cyrillic | uk | 0 | 0 | 10 | 12 | 0 | 10 |
| dev | font_extremes | small | 367 | 367 | 13 | 16 | 16 | 0 |
| dev | font_extremes | large | 33 | 33 | 12 | 15 | 15 | 0 |

The test font class has aggregate deficit 23 but subgroup deficits total 27: 54 small candidates exceed the small quota by 4, while large supplies only 23/50. Aggregate class deficit and subgroup deficit are distinct. Modern Cyrillic selection is zero after preceding classes use the shared edition allowance; the table shows whether each language exists before that step.

## Degraded and census_05 readiness

Confidence-only branch counts: {'dev_degraded_primary': 176, 'full_confidence_below_0.89': 26996, 'sole_reason_confidence_below_0.89': 8152, 'test_degraded_primary': 173}. All low-confidence evidence is `confidence < 0.89`; density percentiles are empty. Primary degraded drawn: test 35, dev 30. The low-confidence secondary count can exceed primary degraded supply because earlier vertical/font classes win precedence. Physical ink density is absent; no density proxy was invented.

**Expected-new versus absent:** gate 0.3 `cell_flag` / `A` was a census_05 producer expectation, but both are already present in all 320,479 census_03 slim rows. This dry run has no missing cell/A blocker. The adapter derives them from diagnostic `crop_bbox` using `A=max(w,h)/min(w,h)` and `cell_flag=(A<=6)`; it does not infer them from numeric text. Actual census_05 completeness still requires its own receipt and full-population checks.

**Readiness blockers / unresolved gates:** (1) receipt output hash absent: require remote-pinned tags checksum; (2) census_05 admitted-only supply and class/subgroup deficits must be measured anew—this dry run fills 0/16 test and 4/16 dev, so it cannot qualify the real benchmark; (3) series identity absent: global 12/book-series compliance cannot be verified; (4) Cyrillic language missing on 850 full-census rows and bg/uk supply must satisfy fixed subquotas in census_05. These are evidence/qualification blockers, not draw execution failures. Letter-spaced evidence is absent; the caps branch remains usable. Ink density is absent in the documented census_05 producer too, so confidence-only degraded is expected, not a new field promised by census_05. No new letter-spaced, series, or density producer is promised. No admission was waived for a real run.

## Artifacts and guarded commit scope

`dryrun/candidates.jsonl`: 361,224 bytes; SHA-256 `5cd95d9dc07edec2abe63c9ec3a8cc238b8104d79b7cfe4532c4d89de26b48a3`; below 5,000,000 bytes and eligible for the guarded list. The large tags archive stays untracked: 32,741,890 bytes, hash above. `verification.json` records the independent local census accounting; `GUARDED_COMMIT_LIST.md` enumerates exact small paths plus the supplied brief. No staging, commit or push performed.

BENCH02G: done | census_03 tags 320479 rows (join 100%/100%) | dry pool test 21825 dev 2403 | classes filled test 0/16 dev 4/16 | deficits test:caps_headings=105,curved_skewed=80,degraded=65,font_extremes=23,greek_latin=160,historical_russian=120,latin=160,leaders_dashes=100,long=160,modern_cyrillic=160,monotonic=240,numeric_cells=189,poly_dictionary_journal=160,polytonic=360,short=120,vertical_turned=87; dev:greek_latin=40,historical_russian=30,latin=40,leaders_dashes=22,long=40,modern_cyrillic=40,monotonic=58,numeric_cells=26,poly_dictionary_journal=40,polytonic=90,short=27,vertical_turned=16 | blockers for census_05 receipt-output-hash,admitted-class/subgroup-supply,series-identity,Cyrillic-language

## Out of git
- `tags.jsonl.gz`: 32741890 bytes, sha256 `9f8f0c721766a95a10cece695726f8e9581214169f0fcde3abe46d3add46d26b`. It stays on disk in the sol-recut worktree, and on Clariden under `filter_pipeline_20261018/bench02/census03/`.

# Label Quality Scoreboard v1.1

Google vs ours on selected supervision words for marks and capitals; selected witness words for marks (contrasts and capped diversity sampling): 25 errors → 25 errors (ours: RU1 labels; 95% interval for B−A on the sample: 0.00 to 0.00 errors per opportunity; 11484 scoped items).
Google vs ours on approved numeric separator controls; lead-ruled raised numeric separator cells: 33 errors → 33 errors (ours: RU1 labels; 95% interval for B−A on the sample: 0.00 to 0.00 errors per opportunity; 103 scoped items).
Google vs ours on the Russian yer decision audit (30 edits and 10 keeps): 30 errors → 0 errors (ours: RU1 labels; 95% interval for B−A on the sample: -0.87 to -0.53 errors per opportunity; 40 scoped items).
Google vs ours on lead-reviewed Russian yer/yat fault and control cells: 2 errors → 2 errors (ours: W1 labels (RU1 comparison is in-sample); 95% interval for B−A on the sample: 0.00 to 0.00 errors per opportunity; 2 scoped items).
Google vs ours on selected supervision words for marks and capitals: 0 errors → 0 errors (ours: RU1 labels; 95% interval for B−A on the sample: 0.00 to 0.00 errors per opportunity; 24 scoped items).
Not measured: letters, superscript, dash, lunate, lookalike, crop.
sf6 release (accents): not scored yet; its labels on the truth lines are being fetched
Network OFF: fetching is pending outside this task; no labels were fetched here.

Frozen truth: 39,508 scoped items; tiers {'A': 39001, 'B': 169, 'C': 338}; 0 conflicts. Truth SHA256 `9f31e392e51b2c1b39e6d7ae5d23f949f4580f1b0bbefdd4d2d6e158013dfbe4`.

[Scoreboard](scoreboard.html): 130 cards, 7.75 MB. [Scores](score_v1.json), [manifest](truth_v1.manifest.json), [receipt](LQB1_RECEIPT.json).

## Sample contract

`uniform` means a seeded uniform draw from a stated population. `enriched` means selected faults, contrasts or controls. `decision_audit` means selected from a version’s decisions. `locked_stratum` identifies a frozen evaluation stratum. Only uniform and eligible locked-stratum rows print a POPULATION error rate. Mixed aggregates never print one. The selected i-a word scopes explicitly disable population rates despite their locked-stratum label. All other measurements describe errors on the sample; these are not errors per 100 lines.

Document bootstrap intervals resample documents intact, 4,000 replicates, seed 20261017; intervals on selected samples are descriptive and do not undo selection. Degenerate intervals do not prove population equality. Decision-precision intervals are Wilson diagnostics conditional on sampled decisions, not population-error estimates. Audit100 samples sf6 releases, so a Google row on it describes Google correctness conditional on sf6 selection, not Google release precision.

## A+B scores by sample type

Only covered out-of-sample, non-regression items enter measurements. `n` is known opportunities (marks heads, N1 gaps, or letters), not full lines. In-sample/regression/uncovered counts remain separate in the JSON. Owner39 never enters a headline. Sample types are split before display; no selected audit is pooled into a population rate.

| class | version | sample_type | measurement | in-sample items | regression items | uncovered |
|---|---|---|---|---:|---:|---:|
| marks | google_raw | decision_audit | not measured | 0 | 0 | 2232 |
| marks | google_raw | enriched | 25 / 11484 on this sample | 0 | 0 | 25136 |
| marks | w1_label | decision_audit | not measured | 0 | 0 | 2232 |
| marks | w1_label | enriched | 25 / 11484 on this sample | 0 | 0 | 25136 |
| marks | ru1_v1 | decision_audit | not measured | 0 | 0 | 2232 |
| marks | ru1_v1 | enriched | 25 / 11484 on this sample | 0 | 0 | 25136 |
| marks | w1_masked_1d | decision_audit | not measured | 0 | 0 | 2232 |
| marks | w1_masked_1d | enriched | not measured | 0 | 0 | 36620 |
| marks | sf6_release | decision_audit | not measured | 0 | 0 | 2232 |
| marks | sf6_release | enriched | not measured | 0 | 0 | 36620 |
| letters | google_raw | locked_stratum | not measured | 0 | 0 | 24 |
| letters | w1_label | locked_stratum | not measured | 0 | 0 | 24 |
| letters | ru1_v1 | locked_stratum | not measured | 0 | 0 | 24 |
| letters | w1_masked_1d | locked_stratum | not measured | 0 | 0 | 24 |
| letters | sf6_release | locked_stratum | not measured | 0 | 0 | 24 |
| n1_separator | google_raw | enriched | 33 / 103 on this sample | 0 | 0 | 0 |
| n1_separator | w1_label | enriched | 33 / 103 on this sample | 0 | 0 | 0 |
| n1_separator | ru1_v1 | enriched | 33 / 103 on this sample | 0 | 0 | 0 |
| n1_separator | w1_masked_1d | enriched | 0 / 11 on this sample | 0 | 0 | 92 |
| n1_separator | sf6_release | enriched | not measured | 0 | 0 | 103 |
| ru1_yer | google_raw | decision_audit | decision precision: 10/40 correct (95% CI 0.142–0.402) | 0 | 0 | 0 |
| ru1_yer | google_raw | enriched | 23 / 24 on this sample | 0 | 0 | 0 |
| ru1_yer | google_raw | uniform | POPULATION: 53.061 errors per 100 opportunities | 0 | 0 | 16 |
| ru1_yer | w1_label | decision_audit | decision precision: 10/40 correct (95% CI 0.142–0.402) | 0 | 0 | 0 |
| ru1_yer | w1_label | enriched | 23 / 24 on this sample | 0 | 0 | 0 |
| ru1_yer | w1_label | uniform | POPULATION: 53.061 errors per 100 opportunities | 0 | 0 | 16 |
| ru1_yer | ru1_v1 | decision_audit | decision precision: 40/40 correct (95% CI 0.912–1.000) | 0 | 0 | 0 |
| ru1_yer | ru1_v1 | enriched | not measured | 24 | 0 | 0 |
| ru1_yer | ru1_v1 | uniform | not measured | 49 | 0 | 16 |
| ru1_yer | w1_masked_1d | decision_audit | not measured | 0 | 0 | 40 |
| ru1_yer | w1_masked_1d | enriched | not measured | 0 | 0 | 24 |
| ru1_yer | w1_masked_1d | uniform | not measured | 0 | 0 | 65 |
| ru1_yer | sf6_release | decision_audit | not measured | 0 | 0 | 40 |
| ru1_yer | sf6_release | enriched | not measured | 0 | 0 | 24 |
| ru1_yer | sf6_release | uniform | not measured | 0 | 0 | 65 |
| ru2_yat | google_raw | enriched | 2 / 2 on this sample | 0 | 0 | 0 |
| ru2_yat | w1_label | enriched | 2 / 2 on this sample | 0 | 0 | 0 |
| ru2_yat | ru1_v1 | enriched | not measured | 2 | 0 | 0 |
| ru2_yat | w1_masked_1d | enriched | not measured | 0 | 0 | 2 |
| ru2_yat | sf6_release | enriched | not measured | 0 | 0 | 2 |
| superscript | google_raw | not measured | not measured | 0 | 0 | 0 |
| superscript | w1_label | not measured | not measured | 0 | 0 | 0 |
| superscript | ru1_v1 | not measured | not measured | 0 | 0 | 0 |
| superscript | w1_masked_1d | not measured | not measured | 0 | 0 | 0 |
| superscript | sf6_release | not measured | not measured | 0 | 0 | 0 |
| dash | google_raw | not measured | not measured | 0 | 0 | 0 |
| dash | w1_label | not measured | not measured | 0 | 0 | 0 |
| dash | ru1_v1 | not measured | not measured | 0 | 0 | 0 |
| dash | w1_masked_1d | not measured | not measured | 0 | 0 | 0 |
| dash | sf6_release | not measured | not measured | 0 | 0 | 0 |
| lunate | google_raw | not measured | not measured | 0 | 0 | 0 |
| lunate | w1_label | not measured | not measured | 0 | 0 | 0 |
| lunate | ru1_v1 | not measured | not measured | 0 | 0 | 0 |
| lunate | w1_masked_1d | not measured | not measured | 0 | 0 | 0 |
| lunate | sf6_release | not measured | not measured | 0 | 0 | 0 |
| lookalike | google_raw | not measured | not measured | 0 | 0 | 0 |
| lookalike | w1_label | not measured | not measured | 0 | 0 | 0 |
| lookalike | ru1_v1 | not measured | not measured | 0 | 0 | 0 |
| lookalike | w1_masked_1d | not measured | not measured | 0 | 0 | 0 |
| lookalike | sf6_release | not measured | not measured | 0 | 0 | 0 |
| capitals | google_raw | enriched | 0 / 24 on this sample | 0 | 0 | 36 |
| capitals | w1_label | enriched | 0 / 24 on this sample | 0 | 0 | 36 |
| capitals | ru1_v1 | enriched | 0 / 24 on this sample | 0 | 0 | 36 |
| capitals | w1_masked_1d | enriched | not measured | 0 | 0 | 60 |
| capitals | sf6_release | enriched | not measured | 0 | 0 | 60 |
| crop | google_raw | not measured | not measured | 0 | 0 | 0 |
| crop | w1_label | not measured | not measured | 0 | 0 | 0 |
| crop | ru1_v1 | not measured | not measured | 0 | 0 | 0 |
| crop | w1_masked_1d | not measured | not measured | 0 | 0 | 0 |
| crop | sf6_release | not measured | not measured | 0 | 0 | 0 |
| marks/breathing | google_raw | decision_audit | not measured | 0 | 0 | 558 |
| marks/breathing | google_raw | enriched | 8 / 2859 on this sample | 0 | 0 | 6284 |
| marks/breathing | w1_label | decision_audit | not measured | 0 | 0 | 558 |
| marks/breathing | w1_label | enriched | 8 / 2859 on this sample | 0 | 0 | 6284 |
| marks/breathing | ru1_v1 | decision_audit | not measured | 0 | 0 | 558 |
| marks/breathing | ru1_v1 | enriched | 8 / 2859 on this sample | 0 | 0 | 6284 |
| marks/breathing | w1_masked_1d | decision_audit | not measured | 0 | 0 | 558 |
| marks/breathing | w1_masked_1d | enriched | not measured | 0 | 0 | 9143 |
| marks/breathing | sf6_release | decision_audit | not measured | 0 | 0 | 558 |
| marks/breathing | sf6_release | enriched | not measured | 0 | 0 | 9143 |
| marks/accent | google_raw | decision_audit | not measured | 0 | 0 | 558 |
| marks/accent | google_raw | enriched | 10 / 2874 on this sample | 0 | 0 | 6284 |
| marks/accent | w1_label | decision_audit | not measured | 0 | 0 | 558 |
| marks/accent | w1_label | enriched | 10 / 2874 on this sample | 0 | 0 | 6284 |
| marks/accent | ru1_v1 | decision_audit | not measured | 0 | 0 | 558 |
| marks/accent | ru1_v1 | enriched | 10 / 2874 on this sample | 0 | 0 | 6284 |
| marks/accent | w1_masked_1d | decision_audit | not measured | 0 | 0 | 558 |
| marks/accent | w1_masked_1d | enriched | not measured | 0 | 0 | 9158 |
| marks/accent | sf6_release | decision_audit | not measured | 0 | 0 | 558 |
| marks/accent | sf6_release | enriched | not measured | 0 | 0 | 9158 |
| marks/dialytika | google_raw | decision_audit | not measured | 0 | 0 | 558 |
| marks/dialytika | google_raw | enriched | 1 / 2876 on this sample | 0 | 0 | 6284 |
| marks/dialytika | w1_label | decision_audit | not measured | 0 | 0 | 558 |
| marks/dialytika | w1_label | enriched | 1 / 2876 on this sample | 0 | 0 | 6284 |
| marks/dialytika | ru1_v1 | decision_audit | not measured | 0 | 0 | 558 |
| marks/dialytika | ru1_v1 | enriched | 1 / 2876 on this sample | 0 | 0 | 6284 |
| marks/dialytika | w1_masked_1d | decision_audit | not measured | 0 | 0 | 558 |
| marks/dialytika | w1_masked_1d | enriched | not measured | 0 | 0 | 9160 |
| marks/dialytika | sf6_release | decision_audit | not measured | 0 | 0 | 558 |
| marks/dialytika | sf6_release | enriched | not measured | 0 | 0 | 9160 |
| marks/subscript | google_raw | decision_audit | not measured | 0 | 0 | 558 |
| marks/subscript | google_raw | enriched | 6 / 2875 on this sample | 0 | 0 | 6284 |
| marks/subscript | w1_label | decision_audit | not measured | 0 | 0 | 558 |
| marks/subscript | w1_label | enriched | 6 / 2875 on this sample | 0 | 0 | 6284 |
| marks/subscript | ru1_v1 | decision_audit | not measured | 0 | 0 | 558 |
| marks/subscript | ru1_v1 | enriched | 6 / 2875 on this sample | 0 | 0 | 6284 |
| marks/subscript | w1_masked_1d | decision_audit | not measured | 0 | 0 | 558 |
| marks/subscript | w1_masked_1d | enriched | not measured | 0 | 0 | 9159 |
| marks/subscript | sf6_release | decision_audit | not measured | 0 | 0 | 558 |
| marks/subscript | sf6_release | enriched | not measured | 0 | 0 | 9159 |

## Paired comparisons

B−A is reported in errors per opportunity on the common sample. Only eligible population pairs additionally carry per-100 rates in JSON. Both versions’ in-sample items and regression items are excluded.

| class | A → B | sample_type | common items | A errors → B errors | B−A on the sample | document 95% interval |
|---|---|---|---:|---|---|---|
| marks | google_raw→w1_label | enriched | 11484 | 25 → 25 | 0.000000 | [0.000000, 0.000000] |
| letters | google_raw→w1_label | not measured | 0 | — | not measured | — |
| n1_separator | google_raw→w1_label | enriched | 103 | 33 → 33 | 0.000000 | [0.000000, 0.000000] |
| ru1_yer | google_raw→w1_label | mixed | 113 | 79 → 79 | 0.000000 | [0.000000, 0.000000] |
| ru2_yat | google_raw→w1_label | enriched | 2 | 2 → 2 | 0.000000 | [0.000000, 0.000000] |
| superscript | google_raw→w1_label | not measured | 0 | — | not measured | — |
| dash | google_raw→w1_label | not measured | 0 | — | not measured | — |
| lunate | google_raw→w1_label | not measured | 0 | — | not measured | — |
| lookalike | google_raw→w1_label | not measured | 0 | — | not measured | — |
| capitals | google_raw→w1_label | enriched | 24 | 0 → 0 | 0.000000 | [0.000000, 0.000000] |
| crop | google_raw→w1_label | not measured | 0 | — | not measured | — |
| marks/breathing | google_raw→w1_label | enriched | 2859 | 8 → 8 | 0.000000 | [0.000000, 0.000000] |
| marks/accent | google_raw→w1_label | enriched | 2874 | 10 → 10 | 0.000000 | [0.000000, 0.000000] |
| marks/dialytika | google_raw→w1_label | enriched | 2876 | 1 → 1 | 0.000000 | [0.000000, 0.000000] |
| marks/subscript | google_raw→w1_label | enriched | 2875 | 6 → 6 | 0.000000 | [0.000000, 0.000000] |
| marks | w1_label→ru1_v1 | enriched | 11484 | 25 → 25 | 0.000000 | [0.000000, 0.000000] |
| letters | w1_label→ru1_v1 | not measured | 0 | — | not measured | — |
| n1_separator | w1_label→ru1_v1 | enriched | 103 | 33 → 33 | 0.000000 | [0.000000, 0.000000] |
| ru1_yer | w1_label→ru1_v1 | decision_audit | 40 | 30 → 0 | -0.750000 | [-0.866667, -0.531250] |
| ru2_yat | w1_label→ru1_v1 | not measured | 0 | — | not measured | — |
| superscript | w1_label→ru1_v1 | not measured | 0 | — | not measured | — |
| dash | w1_label→ru1_v1 | not measured | 0 | — | not measured | — |
| lunate | w1_label→ru1_v1 | not measured | 0 | — | not measured | — |
| lookalike | w1_label→ru1_v1 | not measured | 0 | — | not measured | — |
| capitals | w1_label→ru1_v1 | enriched | 24 | 0 → 0 | 0.000000 | [0.000000, 0.000000] |
| crop | w1_label→ru1_v1 | not measured | 0 | — | not measured | — |
| marks/breathing | w1_label→ru1_v1 | enriched | 2859 | 8 → 8 | 0.000000 | [0.000000, 0.000000] |
| marks/accent | w1_label→ru1_v1 | enriched | 2874 | 10 → 10 | 0.000000 | [0.000000, 0.000000] |
| marks/dialytika | w1_label→ru1_v1 | enriched | 2876 | 1 → 1 | 0.000000 | [0.000000, 0.000000] |
| marks/subscript | w1_label→ru1_v1 | enriched | 2875 | 6 → 6 | 0.000000 | [0.000000, 0.000000] |
| marks | ru1_v1→w1_masked_1d | not measured | 0 | — | not measured | — |
| letters | ru1_v1→w1_masked_1d | not measured | 0 | — | not measured | — |
| n1_separator | ru1_v1→w1_masked_1d | enriched | 11 | 0 → 0 | 0.000000 | [0.000000, 0.000000] |
| ru1_yer | ru1_v1→w1_masked_1d | not measured | 0 | — | not measured | — |
| ru2_yat | ru1_v1→w1_masked_1d | not measured | 0 | — | not measured | — |
| superscript | ru1_v1→w1_masked_1d | not measured | 0 | — | not measured | — |
| dash | ru1_v1→w1_masked_1d | not measured | 0 | — | not measured | — |
| lunate | ru1_v1→w1_masked_1d | not measured | 0 | — | not measured | — |
| lookalike | ru1_v1→w1_masked_1d | not measured | 0 | — | not measured | — |
| capitals | ru1_v1→w1_masked_1d | not measured | 0 | — | not measured | — |
| crop | ru1_v1→w1_masked_1d | not measured | 0 | — | not measured | — |
| marks/breathing | ru1_v1→w1_masked_1d | not measured | 0 | — | not measured | — |
| marks/accent | ru1_v1→w1_masked_1d | not measured | 0 | — | not measured | — |
| marks/dialytika | ru1_v1→w1_masked_1d | not measured | 0 | — | not measured | — |
| marks/subscript | ru1_v1→w1_masked_1d | not measured | 0 | — | not measured | — |
| marks | w1_masked_1d→sf6_release | not measured | 0 | — | not measured | — |
| letters | w1_masked_1d→sf6_release | not measured | 0 | — | not measured | — |
| n1_separator | w1_masked_1d→sf6_release | not measured | 0 | — | not measured | — |
| ru1_yer | w1_masked_1d→sf6_release | not measured | 0 | — | not measured | — |
| ru2_yat | w1_masked_1d→sf6_release | not measured | 0 | — | not measured | — |
| superscript | w1_masked_1d→sf6_release | not measured | 0 | — | not measured | — |
| dash | w1_masked_1d→sf6_release | not measured | 0 | — | not measured | — |
| lunate | w1_masked_1d→sf6_release | not measured | 0 | — | not measured | — |
| lookalike | w1_masked_1d→sf6_release | not measured | 0 | — | not measured | — |
| capitals | w1_masked_1d→sf6_release | not measured | 0 | — | not measured | — |
| crop | w1_masked_1d→sf6_release | not measured | 0 | — | not measured | — |
| marks/breathing | w1_masked_1d→sf6_release | not measured | 0 | — | not measured | — |
| marks/accent | w1_masked_1d→sf6_release | not measured | 0 | — | not measured | — |
| marks/dialytika | w1_masked_1d→sf6_release | not measured | 0 | — | not measured | — |
| marks/subscript | w1_masked_1d→sf6_release | not measured | 0 | — | not measured | — |
| marks | google_raw→ru1_v1 | enriched | 11484 | 25 → 25 | 0.000000 | [0.000000, 0.000000] |
| letters | google_raw→ru1_v1 | not measured | 0 | — | not measured | — |
| n1_separator | google_raw→ru1_v1 | enriched | 103 | 33 → 33 | 0.000000 | [0.000000, 0.000000] |
| ru1_yer | google_raw→ru1_v1 | decision_audit | 40 | 30 → 0 | -0.750000 | [-0.866667, -0.531250] |
| ru2_yat | google_raw→ru1_v1 | not measured | 0 | — | not measured | — |
| superscript | google_raw→ru1_v1 | not measured | 0 | — | not measured | — |
| dash | google_raw→ru1_v1 | not measured | 0 | — | not measured | — |
| lunate | google_raw→ru1_v1 | not measured | 0 | — | not measured | — |
| lookalike | google_raw→ru1_v1 | not measured | 0 | — | not measured | — |
| capitals | google_raw→ru1_v1 | enriched | 24 | 0 → 0 | 0.000000 | [0.000000, 0.000000] |
| crop | google_raw→ru1_v1 | not measured | 0 | — | not measured | — |
| marks/breathing | google_raw→ru1_v1 | enriched | 2859 | 8 → 8 | 0.000000 | [0.000000, 0.000000] |
| marks/accent | google_raw→ru1_v1 | enriched | 2874 | 10 → 10 | 0.000000 | [0.000000, 0.000000] |
| marks/dialytika | google_raw→ru1_v1 | enriched | 2876 | 1 → 1 | 0.000000 | [0.000000, 0.000000] |
| marks/subscript | google_raw→ru1_v1 | enriched | 2875 | 6 → 6 | 0.000000 | [0.000000, 0.000000] |
| marks | w1_label→w1_masked_1d | not measured | 0 | — | not measured | — |
| letters | w1_label→w1_masked_1d | not measured | 0 | — | not measured | — |
| n1_separator | w1_label→w1_masked_1d | enriched | 11 | 0 → 0 | 0.000000 | [0.000000, 0.000000] |
| ru1_yer | w1_label→w1_masked_1d | not measured | 0 | — | not measured | — |
| ru2_yat | w1_label→w1_masked_1d | not measured | 0 | — | not measured | — |
| superscript | w1_label→w1_masked_1d | not measured | 0 | — | not measured | — |
| dash | w1_label→w1_masked_1d | not measured | 0 | — | not measured | — |
| lunate | w1_label→w1_masked_1d | not measured | 0 | — | not measured | — |
| lookalike | w1_label→w1_masked_1d | not measured | 0 | — | not measured | — |
| capitals | w1_label→w1_masked_1d | not measured | 0 | — | not measured | — |
| crop | w1_label→w1_masked_1d | not measured | 0 | — | not measured | — |
| marks/breathing | w1_label→w1_masked_1d | not measured | 0 | — | not measured | — |
| marks/accent | w1_label→w1_masked_1d | not measured | 0 | — | not measured | — |
| marks/dialytika | w1_label→w1_masked_1d | not measured | 0 | — | not measured | — |
| marks/subscript | w1_label→w1_masked_1d | not measured | 0 | — | not measured | — |
| marks | ru1_v1→sf6_release | not measured | 0 | — | not measured | — |
| letters | ru1_v1→sf6_release | not measured | 0 | — | not measured | — |
| n1_separator | ru1_v1→sf6_release | not measured | 0 | — | not measured | — |
| ru1_yer | ru1_v1→sf6_release | not measured | 0 | — | not measured | — |
| ru2_yat | ru1_v1→sf6_release | not measured | 0 | — | not measured | — |
| superscript | ru1_v1→sf6_release | not measured | 0 | — | not measured | — |
| dash | ru1_v1→sf6_release | not measured | 0 | — | not measured | — |
| lunate | ru1_v1→sf6_release | not measured | 0 | — | not measured | — |
| lookalike | ru1_v1→sf6_release | not measured | 0 | — | not measured | — |
| capitals | ru1_v1→sf6_release | not measured | 0 | — | not measured | — |
| crop | ru1_v1→sf6_release | not measured | 0 | — | not measured | — |
| marks/breathing | ru1_v1→sf6_release | not measured | 0 | — | not measured | — |
| marks/accent | ru1_v1→sf6_release | not measured | 0 | — | not measured | — |
| marks/dialytika | ru1_v1→sf6_release | not measured | 0 | — | not measured | — |
| marks/subscript | ru1_v1→sf6_release | not measured | 0 | — | not measured | — |

## Truth inventory

| set | tier | sample_type | sample description |
|---|---|---|---|
| print189 | A | enriched | the 189 selected printed-word marks cards |
| owner39 | A | enriched | the 39 owner-reviewed reader-error regression cards |
| T4 | A | enriched | selected witness words for marks (contrasts and capped diversity sampling) |
| T2 | A | enriched | selected supervision words for marks and capitals |
| audit100 | A | decision_audit | selected sf6 release decisions, adjudicated for word marks |
| yer_adjudication | A | uniform | the seeded C1 uniform Russian yer draw within its stratum |
| RU1_review | B | enriched | lead-reviewed Russian yer/yat fault and control cells |
| RU1_audit | B | decision_audit | the Russian yer decision audit (30 edits and 10 keeps) |
| RU1_two_sol | C | enriched | Russian yer construction decisions with two Sol votes |
| N1_controls | B | enriched | approved numeric separator controls |
| N1_lead | B | enriched | lead-ruled raised numeric separator cells |
| R0_ia_letters | A | locked_stratum | 24 pixel-adjudicated letter word scopes from locked Wikisource i-a (selected disagreements, 23 of 133 lines; selection-exposed v2 val) |

## Letters evidence decision

**Added one tier-A letters truth set: `R0_ia_letters`, `sample_type=locked_stratum`.** It contains only 24 AGREED word-card scopes, 125 known printed letters on 23 distinct lines within the 133-line i-a cohort. There are zero certified complete lines. [R0 report, lines 3–16](../spellcheck/R0_REPORT.md#letter-errors-on-adjudicated-word-card-slots) states the coverage and disagreement enrichment. [R0c input contract](../../briefs/R0c_scoring.md) identifies completed R0b truth, 24 AGREED plus 3 excluded controls, private keys and raw answers. [R0 reader plan](../../briefs/R0_recogniser_audit.md) specifies two blind Opus readers against pixels. [Completed i-a verdicts](../spellcheck/R0_expected_truth_ia.json), [scope keys](../spellcheck/R0_adjudication_private/ia/items_key.json), and [per-word inventory](../spellcheck/R0_evidence/scoring/letter_units.jsonl) bind the retained literal forms. These existing adjudications are reused; no new reading occurred.

**Edition-normalisation caveat:** aligned Wikisource text is a reference transcription, not automatic pixel truth. NFC/whitespace and formatting/variant cleanup are documented in [source READS, lines 11–15](../../harvest/wikisource/READS.md). The [i-a source records](../spellcheck/R0_locked_set.jsonl) explicitly label the human text “Wikisource reference; not yet pixel-adjudicated”. Literal R0 pixel rulings override that reference only within certified scopes. The remaining i-a line spans remain reference transcription, not pixel truth. i-a has 131/133 v2-val overlap and one book supplies 122/133 lines ([R0 report, lines 199–201](../spellcheck/R0_REPORT.md)); it is selection-exposed and cannot establish general letter accuracy.

**i-b: reference transcription, not pixel truth.** The source registry has 1,246 harvest lines; the R0 locked subset has 400 lines. [R0 report, lines 216–255](../spellcheck/R0_REPORT.md) says print truth remains PENDING and two independent readers plus pixel tiebreak are required. [i-b expected truth](../spellcheck/R0_expected_truth_ib.json) remains unadjudicated. No i-b reference label enters truth. The [T7b source receipt](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-wsr0/docs/harvest/wikisource_r0/RECEIPT.md), lines 39–45 and 189–210, records finite preparer QA: 20 candidates inspected, 3 source/print discrepancies excluded and 17 retained examples with no discrepancy identified. It explicitly does not certify every glyph. This supplies extraction/source QA, not a tier-A/B adjudicated letter-scope inventory; those examples are not silently promoted.

**Version coverage:** all 24 i-a scopes are absent from the registered W1 versions, so letters are not measured in this scoreboard. Truth availability does not authorize substituting the R0 recogniser stream for an LQB version. Reference scopes are anchored to base-letter spans in the frozen i-a Google text; the builder verifies the census and exact span, and the scorer maps those boundaries across version changes.

## Retained safeguards and unresolved sources

Deduplication is `(line_id, slot, class)`; contradictory truth excludes the key. Equal truth unions provenance and contamination. Different sampling types merging on one key conservatively become enriched. Unknown/unreadable items remain absent. The owner ἤγε → ἦγε overlay is applied symmetrically before deduplication. RU1 review and original yer controls are in-sample for ru1_v1; RU1 audit is not. N1 truth excludes held/show-through cells and carries `n1_*` contamination. T2 is supervision, not an exclusion holdout. Exclusion ids are a handoff only; none were registered.

Google, W1, RU1 and masked-admission membership remain defined by [versions.json](versions.json). Masks are a sibling admission branch, not a new RU1 text repair. sf6 remains remote_unfetched; no network action was attempted. Marks use peer union alignment and known head opportunities; inserted letters have unknown marks. N1 uses digit-anchored gap classes. Letters ignore combining diacritics and count base-letter edits only in certified spans. All source hashes are bound in the manifest.

- **S8_DEV**: peer says two-reader adjudicated, but does not identify reader models/blinding; tier unclear.

- **substitution60**: sample contains proposed substitutions; aggregate owner precision and notes do not bind complete printed heads for all 60; no blank-note acceptance convention authorized for this sheet.

- **C1/bsb_poly1850__poly1850__a**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/bsb_poly1850__poly1850__b**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/elstat__numerics_tables__a**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/elstat__numerics_tables__b**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/gazette_modern__modern_scanned__measured_1986_1990__a**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/gazette_modern__modern_scanned__measured_1986_1990__b**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/gazette_modern__modern_scanned__probe_1982_1985__a**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/gazette_modern__modern_scanned__probe_1982_1985__b**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/ia_poly1850__latin__a**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/ia_poly1850__latin__b**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/ia_poly1850__mixed_greek_latin__a**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/ia_poly1850__mixed_greek_latin__b**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/ia_poly1850__poly1850__a**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/ia_poly1850__poly1850__b**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/ia_russian__cyrillic__a**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/ia_russian__cyrillic__b**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/kosmopolis__poly1900__a**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/kosmopolis__poly1900__b**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/lekythos__poly1900__a**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/lekythos__poly1900__b**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/nlg__greek_poly__a**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/nlg__greek_poly__b**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/nlg__poly1850__a**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/nlg__poly1850__b**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/nlg__poly1900__a**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/nlg__poly1900__b**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/serbia__cyrillic__a**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **C1/serbia__cyrillic__b**: one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier.

- **locked_strata**: i-a has 24 tier-A pixel-adjudicated word scopes (125 known letters/23 lines), added separately; remaining i-a and all 1,246 i-b lines are reference transcription, not pixel truth; i-b reader slots remain pending.

## Reproduction and receipt

```sh
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$PWD/docs/labelfix/lqb/validation/tmp"
PY=../greek-ocr-toolkit-sol-collect/.venv/bin/python
$PY -B scripts/lqb/build_truth.py > docs/records/labelfix/lqb/truth_build_v1.log
$PY -B -m greekocr.labelfix.lqb trend --output docs/records/labelfix/lqb/score_v1.json
PYTHONPATH=../greek-ocr-toolkit-cleanup $PY -B scripts/lqb/build_scoreboard.py
$PY -B -m pytest tests/test_lqb.py -q --basetemp=docs/records/labelfix/lqb/validation/pytest_tmp > docs/records/labelfix/lqb/tests_v1.txt
$PY -B scripts/lqb/validate_scoreboard.py
$PY -B scripts/lqb/finalize.py
```

LQB1b tests: **41 passed** ([log](tests_v1.txt)). Revalidated 79 input hashes and truth/score equality. Structural validation decoded all 130 embedded images, verified 130 cards and disabled remote notes. Visible browser layout was not reverified in LQB1b; structural checks do not establish visible correctness.

LQB1b: network OFF; zero new readers, recogniser/inference runs, .git writes, peer/collector writes or external publication. All temporary writes use this worktree, including TMPDIR and pytest basetemp. The predecessor LQB1 receipt documented system-temp deviations; they were not repeated in LQB1b.

## LQB2

Lead ruling: retain all 11 preregistered wave-1d truth items and mark them `in_training: "wave-1d"` through [truth_v1_flags.jsonl](truth_v1_flags.jsonl). The frozen truth and original exclusion list are unchanged. The sidecar has one record per line ID and applies to every truth scope on that line; these 11 lines currently have exactly 11 N1 separator items.

**Alternate exclusion handoff:** [truth_v1_exclusion_ids_alt.txt](truth_v1_exclusion_ids_alt.txt), **1,476 unique IDs**, SHA256 `a6c498a423072e30901c53d5af4c7c37efe5c741fe48f26f45acaa86061aeaad`. Original order and newline format are preserved. Calculation: current 1,499 IDs − 11 wave-1d IDs − 12 unverified source IDs = 1,476. Both literal admission arms `wave-1d` and `wave-1d only` were checked: alternate overlap is **0**. This task writes only the local alternate handoff; it does not change the collector registration.

Truth SHA256 remains `9f31e392e51b2c1b39e6d7ae5d23f949f4580f1b0bbefdd4d2d6e158013dfbe4`; original exclusion SHA256 remains `0b42dd319879e7aded3cb9976db4a9ccd1aae13e23cbe69682375ca25686ea9a`. Sidecar SHA256: `945cb12e114fce3200d401935d5300ff11b1e1329862a2ef1c5ae7b38b4a0f59`. [LQB2 receipt](LQB2_RECEIPT.json) binds the source hashes, removed IDs, and individual unmatched-ID decisions.

**Source-version discrepancy:** REG3 expected the older 1,476-ID list and truth hash `d2cdc75c…`; it actually observed the current 1,499-ID list and truth hash `9f31e392…`. We bind its `observed` hashes and `classification.specified_commit_0b3834f6a`, retaining the later 23 i-a lines. During read-only verification the collector already contained a later 1,465-ID `lqb_truth_v1` handoff sourced from `daed1af19`. That handoff still lists these 12 as unmatched. Its exclusion membership is not independent evidence of a valid source line ID. No collector file was edited.

### The 12 unmatched IDs

All 12 originate in the `yer_adjudication` truth set, from [RU1 control_inventory.json](../../../../artifacts/ru1/keys/control_inventory.json). The inventory explicitly records `source_set: "v2"`, `w1_id: null`, and `w1_mapping: "absent: v2 source population, not W1"`. Their ID space is the older IA Russian source-line format `<book>--n<page>-l<line>`, rather than the W1 `<source>--<hash>--s<sample>-l<line>` format. The truth builder falls back to `source_id` when `w1_id` is absent; this is how they entered the original exclusion handoff.

Exact membership checks found none in the registered v2 `import_real_v2_{train,dev,test}.jsonl` populations, W1 features, or independent pre-LQB exclusion classes. W2 features are absent. The inventory proves their source provenance but does not establish registered release-line membership; no ID was guessed or translated. Under the LQB2 validity rule, **kept 0 / dropped 12** from the alternate exclusions. Their adjudicated truth items remain intact.

| unmatched ID | RU1 adjudication | source set / population | alternate action |
|---|---|---|---|
| `1931-2_202512--n10-l0027` | `a049` | yer_adjudication / v2 IA Russian | dropped |
| `1931-2_202512--n10-l0046` | `a039` | yer_adjudication / v2 IA Russian | dropped |
| `1931-2_202512--n10-l0068` | `a055` | yer_adjudication / v2 IA Russian | dropped |
| `1931-2_202512--n3-l0046` | `a019` | yer_adjudication / v2 IA Russian | dropped |
| `1931-2_202512--n3-l0049` | `a021` | yer_adjudication / v2 IA Russian | dropped |
| `1931-2_202512--n8-l0070` | `a022` | yer_adjudication / v2 IA Russian | dropped |
| `aleksandrilnbessarabijaibessarabskijvo81--n36-l0012` | `a008` | yer_adjudication / v2 IA Russian | dropped |
| `golosminuvshegog31915520--n256-l0032` | `a027` | yer_adjudication / v2 IA Russian | dropped |
| `istorija114gopehotnogonovotorzhskogopol95--n142-l0113` | `a042` | yer_adjudication / v2 IA Russian | dropped |
| `lektsiistorifil00zaligoog--n381-l0006` | `a051` | yer_adjudication / v2 IA Russian | dropped |
| `liubav_ancient--n103-l0041` | `a025` | yer_adjudication / v2 IA Russian | dropped |
| `liubav_ancient--n269-l0031` | `a018` | yer_adjudication / v2 IA Russian | dropped |

### Scorer contract and validation

The scorer auto-loads `<truth stem>_flags.jsonl` beside the truth file; `--flags PATH` overrides that location. Missing flags for the default frozen truth fail closed. Invalid, duplicate, unknown-line, or conflicting flags are rejected. The sidecar is applied in memory and its SHA256 is recorded in score schema `lqb-score-v1.2`.

Trained model versions must declare `"trained_on": ["wave-1d"]` in their versions-registry entry. Descendants inherit training arms through `parent`. For those versions, all covered flagged items go to `in_sample`, including per-sample-type breakdowns, and leave headline and paired comparisons. Existing `used_by` / `n1_*` guards remain effective. Label/admission versions declare no training arms and keep their scores; a masked admission list is not itself a trained model. No version-name heuristic substitutes for explicit training metadata.

```sh
PY=../greek-ocr-toolkit-sol-collect/.venv/bin/python
PYTHONDONTWRITEBYTECODE=1 $PY -B -m pytest tests/test_lqb.py -q -p no:cacheprovider --basetemp=docs/records/labelfix/lqb/validation/lqb2/pytest_tmp
# score/trend discovers the sidecar automatically:
PYTHONDONTWRITEBYTECODE=1 $PY -B -m greekocr.labelfix.lqb trend --output /tmp/lqb2_score.json
```

**54 tests passed** ([log](tests_lqb2.txt)): alternate-list identity and hashes, frozen truth retention, the real 11-item in-sample split, label-version invariance, end-to-end sidecar loading, inherited training arms, paired exclusion, malformed/missing/conflicting flags, and invalid/cyclic lineage. Full frozen label-version score and paired-comparison equality is checked separately in [label_score_parity.json](validation/lqb2/label_score_parity.json). Historical v1 score/HTML artifacts remain the label-version baseline.

Network OFF; no new reading or inference, `.git` writes, or peer writes. The original truth/list and collector files remain unchanged.

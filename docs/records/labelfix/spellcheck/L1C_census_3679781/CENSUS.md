# L1C HOLD census

Analysis only; exact reasons read from completed SF4 releases.

Slot counts deduplicate (line, start, letter, exact detail). Blank-letter edit guards are
line guards, not glyph slots. ALONE means the union of all exact reasons on the line
is that singleton. Family counts deduplicate lines; families can overlap (K1 observation
wrappers also tag their underlying family). Unknown reasons remain visible.

JSON includes global top-10 exact sets and wave × source groups. Full exact-set
counters are retained in shard partials for exact aggregation and restart.
Clipping includes crop_UNSEEN; R1 uncertainty includes missing/unscored/unsupported
reader evidence. Exact strings are preserved, without merging synonyms.

## PRESENCE

| Wave | Source | Lines | HOLD | Held glyph slots |
|---|---|---:|---:|---:|
| ALL | ALL | 124669 | 118455 | 1065830 |
| mixed | ALL | 13227 | 12407 | 93653 |
| openarchives | ALL | 235 | 205 | 1149 |
| parliament | ALL | 27224 | 27084 | 353941 |
| round1 | ALL | 43869 | 40673 | 307526 |
| round2 | ALL | 17026 | 15423 | 105679 |
| vouli | ALL | 23088 | 22663 | 203882 |
| ALL | anemi_mixed | 13084 | 12284 | 92772 |
| ALL | anemi_round1 | 43869 | 40673 | 307526 |
| ALL | anemi_round2 | 17026 | 15423 | 105679 |
| ALL | archive_b28038630 | 97 | 78 | 410 |
| ALL | openarchives_Pandemos | 185 | 169 | 1059 |
| ALL | openarchives_kallipos | 50 | 36 | 90 |
| ALL | openarchives_mixed_Pandemos | 13 | 12 | 75 |
| ALL | openarchives_mixed_apothesis | 1 | 1 | 1 |
| ALL | openarchives_mixed_ktisis | 2 | 2 | 2 |
| ALL | openarchives_mixed_ntua | 30 | 30 | 393 |
| ALL | parliament_proceedings_1975_2000 | 27224 | 27084 | 353941 |
| ALL | vouli_parliament_1850s | 23088 | 22663 | 203882 |
| mixed | anemi_mixed | 13084 | 12284 | 92772 |
| mixed | archive_b28038630 | 97 | 78 | 410 |
| mixed | openarchives_mixed_Pandemos | 13 | 12 | 75 |
| mixed | openarchives_mixed_apothesis | 1 | 1 | 1 |
| mixed | openarchives_mixed_ktisis | 2 | 2 | 2 |
| mixed | openarchives_mixed_ntua | 30 | 30 | 393 |
| openarchives | openarchives_Pandemos | 185 | 169 | 1059 |
| openarchives | openarchives_kallipos | 50 | 36 | 90 |
| parliament | parliament_proceedings_1975_2000 | 27224 | 27084 | 353941 |
| round1 | anemi_round1 | 43869 | 40673 | 307526 |
| round2 | anemi_round2 | 17026 | 15423 | 105679 |
| vouli | vouli_parliament_1850s | 23088 | 22663 | 203882 |

### ALL / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 543 | 0 | 525 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 770 | 0 | 741 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 6 | 0 | 6 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 6 | 0 | 6 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 18 | 0 | 18 | 0 |
| K1:C3:two_accents:evidence_tie | 58 | 0 | 29 | 0 |
| K1:C3:two_accents:rule_held_back | 8094 | 0 | 3535 | 20 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 956 | 0 | 917 | 3 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 48 | 0 | 46 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1782 | 0 | 1627 | 6 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 3 | 0 | 3 | 0 |
| detector_clipped_bottom | 176335 | 0 | 68784 | 1327 |
| detector_clipped_top | 420955 | 0 | 89886 | 4934 |
| detector_localisation_unknown | 151696 | 0 | 46253 | 0 |
| detector_segmentation_uncertain | 254880 | 0 | 60333 | 293 |
| detector_unnamed_mark | 40015 | 0 | 26798 | 112 |
| edit_guard:base_or_character_mismatch | 4440 | 13689 | 13689 | 68 |
| edit_guard:punctuation_mismatch | 16841 | 15070 | 15070 | 422 |
| edit_guard:unsupported_character:0 | 7792 | 66 | 189 | 0 |
| edit_guard:unsupported_character:1 | 4010 | 28 | 93 | 0 |
| edit_guard:unsupported_character:10 | 1272 | 16 | 34 | 0 |
| edit_guard:unsupported_character:11 | 665 | 9 | 17 | 0 |
| edit_guard:unsupported_character:12 | 601 | 8 | 15 | 0 |
| edit_guard:unsupported_character:13 | 917 | 14 | 28 | 0 |
| edit_guard:unsupported_character:14 | 1018 | 15 | 28 | 0 |
| edit_guard:unsupported_character:15 | 864 | 16 | 24 | 0 |
| edit_guard:unsupported_character:16 | 685 | 7 | 20 | 0 |
| edit_guard:unsupported_character:17 | 785 | 10 | 20 | 0 |
| edit_guard:unsupported_character:18 | 933 | 10 | 23 | 0 |
| edit_guard:unsupported_character:19 | 930 | 10 | 25 | 0 |
| edit_guard:unsupported_character:2 | 1700 | 13 | 46 | 0 |
| edit_guard:unsupported_character:20 | 1105 | 13 | 28 | 0 |
| edit_guard:unsupported_character:21 | 854 | 10 | 24 | 0 |
| edit_guard:unsupported_character:22 | 844 | 14 | 22 | 0 |
| edit_guard:unsupported_character:23 | 1021 | 11 | 28 | 0 |
| edit_guard:unsupported_character:24 | 830 | 10 | 21 | 0 |
| edit_guard:unsupported_character:25 | 689 | 6 | 19 | 0 |
| edit_guard:unsupported_character:26 | 1089 | 10 | 28 | 0 |
| edit_guard:unsupported_character:27 | 1334 | 18 | 34 | 0 |
| edit_guard:unsupported_character:28 | 1287 | 14 | 34 | 0 |
| edit_guard:unsupported_character:29 | 1711 | 18 | 43 | 0 |
| edit_guard:unsupported_character:3 | 2344 | 14 | 61 | 0 |
| edit_guard:unsupported_character:30 | 1154 | 13 | 31 | 0 |
| edit_guard:unsupported_character:31 | 1482 | 14 | 37 | 0 |
| edit_guard:unsupported_character:32 | 1122 | 10 | 29 | 0 |
| edit_guard:unsupported_character:33 | 1159 | 9 | 28 | 0 |
| edit_guard:unsupported_character:34 | 1438 | 10 | 34 | 0 |
| edit_guard:unsupported_character:35 | 1137 | 10 | 28 | 0 |
| edit_guard:unsupported_character:36 | 1520 | 10 | 37 | 0 |
| edit_guard:unsupported_character:37 | 1698 | 16 | 40 | 0 |
| edit_guard:unsupported_character:38 | 1008 | 9 | 23 | 0 |
| edit_guard:unsupported_character:39 | 1490 | 16 | 33 | 0 |
| edit_guard:unsupported_character:4 | 1264 | 13 | 32 | 0 |
| edit_guard:unsupported_character:40 | 1397 | 10 | 31 | 0 |
| edit_guard:unsupported_character:41 | 1588 | 16 | 35 | 0 |
| edit_guard:unsupported_character:42 | 1431 | 14 | 31 | 0 |
| edit_guard:unsupported_character:43 | 1353 | 15 | 28 | 0 |
| edit_guard:unsupported_character:44 | 825 | 9 | 17 | 0 |
| edit_guard:unsupported_character:45 | 811 | 5 | 16 | 0 |
| edit_guard:unsupported_character:46 | 759 | 4 | 15 | 0 |
| edit_guard:unsupported_character:47 | 562 | 6 | 11 | 0 |
| edit_guard:unsupported_character:48 | 503 | 6 | 10 | 0 |
| edit_guard:unsupported_character:49 | 568 | 4 | 11 | 0 |
| edit_guard:unsupported_character:5 | 953 | 9 | 20 | 0 |
| edit_guard:unsupported_character:50 | 450 | 4 | 8 | 0 |
| edit_guard:unsupported_character:51 | 547 | 3 | 10 | 0 |
| edit_guard:unsupported_character:52 | 281 | 2 | 5 | 0 |
| edit_guard:unsupported_character:53 | 402 | 1 | 7 | 0 |
| edit_guard:unsupported_character:54 | 370 | 2 | 6 | 0 |
| edit_guard:unsupported_character:55 | 471 | 2 | 7 | 0 |
| edit_guard:unsupported_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_character:57 | 202 | 1 | 3 | 0 |
| edit_guard:unsupported_character:58 | 186 | 1 | 3 | 0 |
| edit_guard:unsupported_character:59 | 125 | 2 | 2 | 0 |
| edit_guard:unsupported_character:6 | 1058 | 10 | 28 | 0 |
| edit_guard:unsupported_character:60 | 254 | 2 | 4 | 0 |
| edit_guard:unsupported_character:61 | 187 | 0 | 3 | 0 |
| edit_guard:unsupported_character:62 | 133 | 1 | 2 | 0 |
| edit_guard:unsupported_character:65 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_character:7 | 1516 | 18 | 35 | 0 |
| edit_guard:unsupported_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_character:74 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:76 | 163 | 0 | 2 | 0 |
| edit_guard:unsupported_character:8 | 1285 | 11 | 31 | 0 |
| edit_guard:unsupported_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_character:9 | 1108 | 14 | 28 | 0 |
| edit_guard:unsupported_raw_character:0 | 7590 | 6 | 187 | 0 |
| edit_guard:unsupported_raw_character:1 | 3453 | 0 | 84 | 0 |
| edit_guard:unsupported_raw_character:10 | 1272 | 0 | 34 | 0 |
| edit_guard:unsupported_raw_character:11 | 687 | 0 | 18 | 0 |
| edit_guard:unsupported_raw_character:12 | 601 | 1 | 16 | 0 |
| edit_guard:unsupported_raw_character:13 | 917 | 0 | 28 | 0 |
| edit_guard:unsupported_raw_character:14 | 1084 | 0 | 30 | 0 |
| edit_guard:unsupported_raw_character:15 | 798 | 0 | 22 | 0 |
| edit_guard:unsupported_raw_character:16 | 719 | 0 | 22 | 0 |
| edit_guard:unsupported_raw_character:17 | 785 | 0 | 20 | 0 |
| edit_guard:unsupported_raw_character:18 | 955 | 0 | 24 | 0 |
| edit_guard:unsupported_raw_character:19 | 916 | 0 | 25 | 0 |
| edit_guard:unsupported_raw_character:2 | 1634 | 0 | 44 | 0 |
| edit_guard:unsupported_raw_character:20 | 1105 | 0 | 28 | 0 |
| edit_guard:unsupported_raw_character:21 | 820 | 0 | 23 | 0 |
| edit_guard:unsupported_raw_character:22 | 844 | 0 | 22 | 0 |
| edit_guard:unsupported_raw_character:23 | 1069 | 0 | 30 | 0 |
| edit_guard:unsupported_raw_character:24 | 782 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:25 | 678 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:26 | 1116 | 0 | 29 | 0 |
| edit_guard:unsupported_raw_character:27 | 1303 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:28 | 1411 | 0 | 36 | 0 |
| edit_guard:unsupported_raw_character:29 | 1742 | 1 | 45 | 0 |
| edit_guard:unsupported_raw_character:3 | 2330 | 0 | 61 | 0 |
| edit_guard:unsupported_raw_character:30 | 1155 | 1 | 32 | 0 |
| edit_guard:unsupported_raw_character:31 | 1482 | 0 | 37 | 0 |
| edit_guard:unsupported_raw_character:32 | 1198 | 0 | 31 | 0 |
| edit_guard:unsupported_raw_character:33 | 1122 | 1 | 28 | 0 |
| edit_guard:unsupported_raw_character:34 | 1399 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:35 | 1137 | 0 | 28 | 0 |
| edit_guard:unsupported_raw_character:36 | 1520 | 0 | 37 | 0 |
| edit_guard:unsupported_raw_character:37 | 1739 | 0 | 41 | 0 |
| edit_guard:unsupported_raw_character:38 | 990 | 1 | 24 | 0 |
| edit_guard:unsupported_raw_character:39 | 1530 | 0 | 34 | 0 |
| edit_guard:unsupported_raw_character:4 | 1280 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:40 | 1388 | 0 | 31 | 0 |
| edit_guard:unsupported_raw_character:41 | 1545 | 0 | 34 | 0 |
| edit_guard:unsupported_raw_character:42 | 1480 | 1 | 33 | 0 |
| edit_guard:unsupported_raw_character:43 | 1353 | 1 | 29 | 0 |
| edit_guard:unsupported_raw_character:44 | 825 | 1 | 18 | 0 |
| edit_guard:unsupported_raw_character:45 | 811 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:46 | 759 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:47 | 562 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:48 | 503 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:49 | 568 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:5 | 951 | 0 | 20 | 0 |
| edit_guard:unsupported_raw_character:50 | 399 | 1 | 8 | 0 |
| edit_guard:unsupported_raw_character:51 | 488 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:52 | 281 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:53 | 402 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:54 | 370 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:55 | 471 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:57 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:58 | 186 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:59 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:6 | 1058 | 0 | 28 | 0 |
| edit_guard:unsupported_raw_character:60 | 254 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:61 | 187 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:62 | 133 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:65 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 1507 | 0 | 34 | 0 |
| edit_guard:unsupported_raw_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:74 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:76 | 80 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 1187 | 0 | 28 | 0 |
| edit_guard:unsupported_raw_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:9 | 1214 | 0 | 30 | 0 |
| mark_kind_disagreement | 298710 | 0 | 91946 | 5967 |
| r1_evidence_UNKNOWN | 1567 | 0 | 1567 | 0 |
| r1_missing | 4770 | 0 | 2991 | 0 |
| r1_uncertainty:out_of_image_span | 1567 | 0 | 1567 | 0 |
| r1_unscored:line_confidence_below_0.5 | 149 | 0 | 9 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 1735 | 0 | 941 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 2886 | 0 | 2129 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 71761 |
| clipping | 99259 |
| K1 | 5313 |
| edit-guard | 22877 |
| A/B disagreement | 0 |
| kind disagreement | 91946 |
| R1 uncertainty | 4502 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 10694 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 8520 |
| ["detector_clipped_bottom","detector_clipped_top"] | 7212 |
| ["mark_kind_disagreement"] | 5967 |
| ["detector_clipped_top","mark_kind_disagreement"] | 5741 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 5297 |
| ["detector_clipped_top"] | 4934 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 4742 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 4222 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 3648 |

### mixed / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 48 | 0 | 47 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 103 | 0 | 100 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 2 | 0 | 2 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:evidence_tie | 4 | 0 | 2 | 0 |
| K1:C3:two_accents:rule_held_back | 874 | 0 | 382 | 3 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 124 | 0 | 122 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 219 | 0 | 206 | 3 |
| detector_clipped_bottom | 15216 | 0 | 6417 | 157 |
| detector_clipped_top | 39943 | 0 | 8844 | 696 |
| detector_localisation_unknown | 8743 | 0 | 3355 | 0 |
| detector_segmentation_uncertain | 17178 | 0 | 5101 | 29 |
| detector_unnamed_mark | 2410 | 0 | 1955 | 11 |
| edit_guard:base_or_character_mismatch | 389 | 1293 | 1293 | 6 |
| edit_guard:punctuation_mismatch | 1288 | 1509 | 1509 | 55 |
| edit_guard:unsupported_character:0 | 570 | 6 | 14 | 0 |
| edit_guard:unsupported_character:1 | 335 | 3 | 8 | 0 |
| edit_guard:unsupported_character:10 | 312 | 5 | 8 | 0 |
| edit_guard:unsupported_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 49 | 1 | 1 | 0 |
| edit_guard:unsupported_character:13 | 211 | 3 | 5 | 0 |
| edit_guard:unsupported_character:14 | 107 | 3 | 3 | 0 |
| edit_guard:unsupported_character:15 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:16 | 192 | 3 | 5 | 0 |
| edit_guard:unsupported_character:17 | 27 | 1 | 1 | 0 |
| edit_guard:unsupported_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:19 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_character:20 | 113 | 2 | 3 | 0 |
| edit_guard:unsupported_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_character:22 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_character:25 | 97 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 104 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 209 | 3 | 5 | 0 |
| edit_guard:unsupported_character:28 | 323 | 2 | 8 | 0 |
| edit_guard:unsupported_character:29 | 68 | 1 | 1 | 0 |
| edit_guard:unsupported_character:3 | 270 | 3 | 7 | 0 |
| edit_guard:unsupported_character:30 | 158 | 3 | 4 | 0 |
| edit_guard:unsupported_character:31 | 260 | 2 | 6 | 0 |
| edit_guard:unsupported_character:32 | 155 | 1 | 4 | 0 |
| edit_guard:unsupported_character:33 | 114 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_character:36 | 165 | 1 | 4 | 0 |
| edit_guard:unsupported_character:37 | 307 | 3 | 7 | 0 |
| edit_guard:unsupported_character:38 | 130 | 1 | 3 | 0 |
| edit_guard:unsupported_character:39 | 134 | 2 | 3 | 0 |
| edit_guard:unsupported_character:4 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_character:41 | 101 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 233 | 3 | 5 | 0 |
| edit_guard:unsupported_character:43 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:44 | 253 | 3 | 5 | 0 |
| edit_guard:unsupported_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_character:46 | 144 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 159 | 1 | 3 | 0 |
| edit_guard:unsupported_character:48 | 102 | 2 | 2 | 0 |
| edit_guard:unsupported_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_character:50 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:6 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 145 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 227 | 4 | 5 | 0 |
| edit_guard:unsupported_raw_character:0 | 563 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:1 | 335 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 312 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:13 | 211 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:14 | 156 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:16 | 192 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:17 | 27 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:19 | 97 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:20 | 113 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:25 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:26 | 131 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 209 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:28 | 323 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:29 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 270 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:30 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:31 | 260 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:32 | 155 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 114 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 165 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 307 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:38 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:4 | 130 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:41 | 101 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 233 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:44 | 253 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:46 | 144 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 159 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:48 | 102 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:50 | 57 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:8 | 227 | 0 | 5 | 0 |
| mark_kind_disagreement | 26522 | 0 | 9608 | 977 |
| r1_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_missing | 440 | 0 | 249 | 0 |
| r1_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 151 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 269 | 0 | 201 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6062 |
| clipping | 9669 |
| K1 | 616 |
| edit-guard | 2239 |
| A/B disagreement | 0 |
| kind disagreement | 9608 |
| R1 uncertainty | 299 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 1457 |
| ["mark_kind_disagreement"] | 977 |
| ["detector_clipped_bottom","detector_clipped_top"] | 950 |
| ["detector_clipped_top","mark_kind_disagreement"] | 825 |
| ["detector_clipped_top"] | 696 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 546 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 520 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 472 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 387 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 324 |

### openarchives / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 12 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_bottom | 366 | 0 | 118 | 19 |
| detector_clipped_top | 629 | 0 | 120 | 20 |
| detector_segmentation_uncertain | 110 | 0 | 38 | 0 |
| detector_unnamed_mark | 24 | 0 | 19 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 19 | 19 | 3 |
| mark_kind_disagreement | 241 | 0 | 116 | 23 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 50 |
| clipping | 159 |
| K1 | 5 |
| edit-guard | 19 |
| A/B disagreement | 0 |
| kind disagreement | 116 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 43 |
| ["mark_kind_disagreement"] | 23 |
| ["detector_clipped_top"] | 20 |
| ["detector_clipped_bottom"] | 19 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 18 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","mark_kind_disagreement"] | 9 |
| ["detector_segmentation_uncertain","mark_kind_disagreement"] | 9 |
| ["detector_clipped_bottom","mark_kind_disagreement"] | 8 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 7 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 7 |

### parliament / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 69 | 0 | 67 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 90 | 0 | 88 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C3:two_accents:evidence_tie | 14 | 0 | 7 | 0 |
| K1:C3:two_accents:rule_held_back | 1343 | 0 | 613 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 159 | 0 | 155 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 7 | 0 | 7 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 292 | 0 | 253 | 0 |
| detector_clipped_bottom | 44633 | 0 | 16119 | 79 |
| detector_clipped_top | 98404 | 0 | 20688 | 237 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 52 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 10 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 2 |
| edit_guard:punctuation_mismatch | 1472 | 2781 | 2781 | 8 |
| edit_guard:unsupported_character:0 | 1663 | 17 | 43 | 0 |
| edit_guard:unsupported_character:1 | 594 | 4 | 17 | 0 |
| edit_guard:unsupported_character:10 | 206 | 3 | 6 | 0 |
| edit_guard:unsupported_character:11 | 221 | 5 | 5 | 0 |
| edit_guard:unsupported_character:12 | 139 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 254 | 4 | 7 | 0 |
| edit_guard:unsupported_character:14 | 201 | 1 | 5 | 0 |
| edit_guard:unsupported_character:15 | 64 | 2 | 2 | 0 |
| edit_guard:unsupported_character:17 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:18 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:19 | 46 | 1 | 1 | 0 |
| edit_guard:unsupported_character:2 | 565 | 4 | 17 | 0 |
| edit_guard:unsupported_character:20 | 277 | 4 | 7 | 0 |
| edit_guard:unsupported_character:21 | 135 | 4 | 4 | 0 |
| edit_guard:unsupported_character:22 | 200 | 3 | 5 | 0 |
| edit_guard:unsupported_character:23 | 94 | 2 | 2 | 0 |
| edit_guard:unsupported_character:24 | 258 | 3 | 7 | 0 |
| edit_guard:unsupported_character:25 | 163 | 1 | 5 | 0 |
| edit_guard:unsupported_character:26 | 121 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 291 | 6 | 7 | 0 |
| edit_guard:unsupported_character:28 | 75 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 160 | 2 | 4 | 0 |
| edit_guard:unsupported_character:3 | 559 | 5 | 15 | 0 |
| edit_guard:unsupported_character:30 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:31 | 157 | 4 | 4 | 0 |
| edit_guard:unsupported_character:32 | 88 | 2 | 2 | 0 |
| edit_guard:unsupported_character:33 | 112 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 254 | 3 | 6 | 0 |
| edit_guard:unsupported_character:35 | 80 | 2 | 2 | 0 |
| edit_guard:unsupported_character:36 | 183 | 2 | 4 | 0 |
| edit_guard:unsupported_character:37 | 132 | 2 | 3 | 0 |
| edit_guard:unsupported_character:38 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:39 | 227 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 349 | 3 | 9 | 0 |
| edit_guard:unsupported_character:40 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:41 | 436 | 7 | 10 | 0 |
| edit_guard:unsupported_character:42 | 176 | 2 | 4 | 0 |
| edit_guard:unsupported_character:43 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:44 | 180 | 2 | 4 | 0 |
| edit_guard:unsupported_character:45 | 188 | 3 | 4 | 0 |
| edit_guard:unsupported_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_character:49 | 50 | 1 | 1 | 0 |
| edit_guard:unsupported_character:5 | 142 | 2 | 3 | 0 |
| edit_guard:unsupported_character:6 | 168 | 2 | 4 | 0 |
| edit_guard:unsupported_character:7 | 417 | 3 | 11 | 0 |
| edit_guard:unsupported_character:8 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:9 | 265 | 3 | 6 | 0 |
| edit_guard:unsupported_raw_character:0 | 1567 | 2 | 41 | 0 |
| edit_guard:unsupported_raw_character:1 | 521 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:10 | 206 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:11 | 221 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:12 | 139 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 254 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:14 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:15 | 64 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:17 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:18 | 179 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:19 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:2 | 546 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:20 | 277 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:21 | 135 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:22 | 200 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:23 | 142 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:24 | 210 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:25 | 163 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:26 | 121 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 291 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:28 | 75 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 191 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:3 | 559 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:30 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 157 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:32 | 88 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 112 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:34 | 254 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:35 | 80 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 183 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 132 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 227 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 349 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:40 | 222 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:41 | 393 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:42 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:43 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_raw_character:44 | 180 | 1 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 188 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:49 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 142 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:6 | 168 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 393 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:8 | 94 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:9 | 265 | 0 | 6 | 0 |
| mark_kind_disagreement | 111173 | 0 | 21977 | 159 |
| r1_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_missing | 1452 | 0 | 955 | 0 |
| r1_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4765 |
| A/B disagreement | 0 |
| kind disagreement | 21977 |
| R1 uncertainty | 1829 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 4161 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 2749 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 2237 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1432 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1308 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 1263 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 984 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 822 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 650 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 495 |

### round1 / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 0 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 11 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 3 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 2 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 596 |
| detector_clipped_top | 140308 | 0 | 29544 | 2188 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 127 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 41 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 33 |
| edit_guard:punctuation_mismatch | 9153 | 6398 | 6398 | 207 |
| edit_guard:unsupported_character:0 | 3286 | 23 | 79 | 0 |
| edit_guard:unsupported_character:1 | 2211 | 16 | 47 | 0 |
| edit_guard:unsupported_character:10 | 439 | 5 | 12 | 0 |
| edit_guard:unsupported_character:11 | 317 | 3 | 9 | 0 |
| edit_guard:unsupported_character:12 | 144 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 283 | 6 | 9 | 0 |
| edit_guard:unsupported_character:14 | 407 | 9 | 13 | 0 |
| edit_guard:unsupported_character:15 | 470 | 7 | 14 | 0 |
| edit_guard:unsupported_character:16 | 268 | 3 | 7 | 0 |
| edit_guard:unsupported_character:17 | 383 | 4 | 9 | 0 |
| edit_guard:unsupported_character:18 | 295 | 3 | 8 | 0 |
| edit_guard:unsupported_character:19 | 337 | 3 | 10 | 0 |
| edit_guard:unsupported_character:2 | 409 | 4 | 11 | 0 |
| edit_guard:unsupported_character:20 | 535 | 6 | 13 | 0 |
| edit_guard:unsupported_character:21 | 407 | 4 | 12 | 0 |
| edit_guard:unsupported_character:22 | 427 | 8 | 11 | 0 |
| edit_guard:unsupported_character:23 | 668 | 7 | 19 | 0 |
| edit_guard:unsupported_character:24 | 469 | 7 | 11 | 0 |
| edit_guard:unsupported_character:25 | 228 | 3 | 7 | 0 |
| edit_guard:unsupported_character:26 | 599 | 6 | 15 | 0 |
| edit_guard:unsupported_character:27 | 636 | 6 | 17 | 0 |
| edit_guard:unsupported_character:28 | 581 | 6 | 17 | 0 |
| edit_guard:unsupported_character:29 | 1243 | 12 | 33 | 0 |
| edit_guard:unsupported_character:3 | 622 | 2 | 15 | 0 |
| edit_guard:unsupported_character:30 | 652 | 5 | 18 | 0 |
| edit_guard:unsupported_character:31 | 551 | 3 | 15 | 0 |
| edit_guard:unsupported_character:32 | 684 | 4 | 18 | 0 |
| edit_guard:unsupported_character:33 | 538 | 5 | 13 | 0 |
| edit_guard:unsupported_character:34 | 781 | 4 | 18 | 0 |
| edit_guard:unsupported_character:35 | 701 | 6 | 17 | 0 |
| edit_guard:unsupported_character:36 | 745 | 2 | 19 | 0 |
| edit_guard:unsupported_character:37 | 765 | 5 | 19 | 0 |
| edit_guard:unsupported_character:38 | 408 | 1 | 10 | 0 |
| edit_guard:unsupported_character:39 | 791 | 6 | 18 | 0 |
| edit_guard:unsupported_character:4 | 497 | 4 | 11 | 0 |
| edit_guard:unsupported_character:40 | 448 | 3 | 10 | 0 |
| edit_guard:unsupported_character:41 | 811 | 5 | 18 | 0 |
| edit_guard:unsupported_character:42 | 454 | 4 | 10 | 0 |
| edit_guard:unsupported_character:43 | 569 | 6 | 12 | 0 |
| edit_guard:unsupported_character:44 | 300 | 3 | 6 | 0 |
| edit_guard:unsupported_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_character:46 | 262 | 1 | 5 | 0 |
| edit_guard:unsupported_character:47 | 207 | 4 | 4 | 0 |
| edit_guard:unsupported_character:48 | 251 | 2 | 5 | 0 |
| edit_guard:unsupported_character:49 | 315 | 1 | 6 | 0 |
| edit_guard:unsupported_character:5 | 299 | 2 | 7 | 0 |
| edit_guard:unsupported_character:50 | 284 | 3 | 5 | 0 |
| edit_guard:unsupported_character:51 | 495 | 3 | 9 | 0 |
| edit_guard:unsupported_character:52 | 175 | 1 | 3 | 0 |
| edit_guard:unsupported_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_character:54 | 202 | 2 | 3 | 0 |
| edit_guard:unsupported_character:55 | 247 | 2 | 4 | 0 |
| edit_guard:unsupported_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_character:57 | 202 | 1 | 3 | 0 |
| edit_guard:unsupported_character:58 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:59 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 421 | 2 | 12 | 0 |
| edit_guard:unsupported_character:60 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_character:62 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:65 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 431 | 3 | 9 | 0 |
| edit_guard:unsupported_character:74 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:8 | 618 | 4 | 15 | 0 |
| edit_guard:unsupported_character:9 | 433 | 4 | 11 | 0 |
| edit_guard:unsupported_raw_character:0 | 3282 | 1 | 78 | 0 |
| edit_guard:unsupported_raw_character:1 | 1715 | 0 | 40 | 0 |
| edit_guard:unsupported_raw_character:10 | 439 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:11 | 339 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:12 | 144 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:13 | 283 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:14 | 424 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:15 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:16 | 302 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:17 | 383 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:18 | 317 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:19 | 379 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:2 | 409 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:20 | 535 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:21 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:22 | 427 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:23 | 668 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:24 | 469 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:25 | 228 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:26 | 599 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:27 | 636 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:28 | 581 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:29 | 1243 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:3 | 644 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:30 | 652 | 1 | 19 | 0 |
| edit_guard:unsupported_raw_character:31 | 551 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:32 | 718 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:33 | 543 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:34 | 742 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:35 | 701 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:36 | 745 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:37 | 806 | 0 | 20 | 0 |
| edit_guard:unsupported_raw_character:38 | 402 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:39 | 831 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:4 | 497 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:40 | 448 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:41 | 811 | 0 | 18 | 0 |
| edit_guard:unsupported_raw_character:42 | 454 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:43 | 569 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:44 | 300 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:46 | 262 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:47 | 207 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:48 | 251 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:49 | 315 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:5 | 270 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 233 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 436 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:52 | 175 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:54 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:55 | 247 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:57 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:58 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:59 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 421 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:60 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:62 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:65 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 471 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:74 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 545 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:9 | 433 | 0 | 11 | 0 |
| mark_kind_disagreement | 73450 | 0 | 30611 | 2924 |
| r1_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_missing | 1687 | 0 | 1129 | 0 |
| r1_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9251 |
| A/B disagreement | 0 |
| kind disagreement | 30611 |
| R1 uncertainty | 1276 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 4389 |
| ["detector_clipped_bottom","detector_clipped_top"] | 3171 |
| ["mark_kind_disagreement"] | 2924 |
| ["detector_clipped_top","mark_kind_disagreement"] | 2456 |
| ["detector_clipped_top"] | 2188 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1925 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 1367 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1223 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1141 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 1052 |

### round2 / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 84 | 0 | 81 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 107 | 0 | 103 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 6 | 0 | 3 | 0 |
| K1:C3:two_accents:rule_held_back | 1020 | 0 | 467 | 4 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 101 | 0 | 98 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 1 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 216 |
| detector_clipped_top | 48664 | 0 | 10763 | 911 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 49 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 22 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 18 |
| edit_guard:punctuation_mismatch | 1491 | 2095 | 2095 | 113 |
| edit_guard:unsupported_character:0 | 1107 | 12 | 28 | 0 |
| edit_guard:unsupported_character:1 | 360 | 2 | 9 | 0 |
| edit_guard:unsupported_character:10 | 169 | 1 | 4 | 0 |
| edit_guard:unsupported_character:11 | 54 | 1 | 1 | 0 |
| edit_guard:unsupported_character:12 | 178 | 3 | 5 | 0 |
| edit_guard:unsupported_character:13 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_character:14 | 169 | 2 | 4 | 0 |
| edit_guard:unsupported_character:15 | 122 | 3 | 3 | 0 |
| edit_guard:unsupported_character:16 | 225 | 1 | 8 | 0 |
| edit_guard:unsupported_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_character:18 | 252 | 3 | 7 | 0 |
| edit_guard:unsupported_character:19 | 108 | 1 | 3 | 0 |
| edit_guard:unsupported_character:2 | 238 | 4 | 6 | 0 |
| edit_guard:unsupported_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_character:21 | 129 | 1 | 4 | 0 |
| edit_guard:unsupported_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_character:23 | 43 | 1 | 1 | 0 |
| edit_guard:unsupported_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_character:27 | 150 | 3 | 4 | 0 |
| edit_guard:unsupported_character:28 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 71 | 0 | 2 | 0 |
| edit_guard:unsupported_character:3 | 236 | 3 | 6 | 0 |
| edit_guard:unsupported_character:30 | 225 | 3 | 6 | 0 |
| edit_guard:unsupported_character:31 | 201 | 3 | 5 | 0 |
| edit_guard:unsupported_character:32 | 79 | 1 | 2 | 0 |
| edit_guard:unsupported_character:33 | 250 | 2 | 6 | 0 |
| edit_guard:unsupported_character:34 | 116 | 1 | 3 | 0 |
| edit_guard:unsupported_character:35 | 152 | 1 | 4 | 0 |
| edit_guard:unsupported_character:36 | 212 | 2 | 5 | 0 |
| edit_guard:unsupported_character:37 | 356 | 5 | 8 | 0 |
| edit_guard:unsupported_character:38 | 192 | 4 | 4 | 0 |
| edit_guard:unsupported_character:39 | 98 | 2 | 2 | 0 |
| edit_guard:unsupported_character:4 | 63 | 1 | 2 | 0 |
| edit_guard:unsupported_character:40 | 87 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 241 | 2 | 5 | 0 |
| edit_guard:unsupported_character:43 | 92 | 1 | 2 | 0 |
| edit_guard:unsupported_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_character:45 | 51 | 1 | 1 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_character:5 | 121 | 3 | 3 | 0 |
| edit_guard:unsupported_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_character:53 | 113 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_character:59 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 165 | 4 | 5 | 0 |
| edit_guard:unsupported_character:60 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 173 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 145 | 1 | 4 | 0 |
| edit_guard:unsupported_character:9 | 114 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:0 | 1012 | 0 | 26 | 0 |
| edit_guard:unsupported_raw_character:1 | 341 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 54 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 178 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:13 | 96 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:14 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 122 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:16 | 225 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 252 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:19 | 108 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:2 | 238 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:21 | 98 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:23 | 43 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:28 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 41 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 236 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:30 | 193 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:31 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:32 | 79 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 250 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:34 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:35 | 152 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:36 | 212 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 356 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:38 | 192 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:4 | 79 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 241 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 92 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 148 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 113 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:59 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 165 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:60 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 148 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:8 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:9 | 114 | 0 | 4 | 0 |
| mark_kind_disagreement | 27905 | 0 | 11778 | 1590 |
| r1_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_missing | 434 | 0 | 268 | 0 |
| r1_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3059 |
| A/B disagreement | 0 |
| kind disagreement | 11778 |
| R1 uncertainty | 354 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 1794 |
| ["mark_kind_disagreement"] | 1590 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1212 |
| ["detector_clipped_top","mark_kind_disagreement"] | 1078 |
| ["detector_clipped_top"] | 911 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 559 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 483 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 457 |
| ["detector_segmentation_uncertain","mark_kind_disagreement"] | 343 |
| ["detector_unnamed_mark","mark_kind_disagreement"] | 323 |

### vouli / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 86 | 0 | 83 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 130 | 0 | 120 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 3 | 0 | 3 | 0 |
| K1:C3:two_accents:evidence_tie | 18 | 0 | 9 | 0 |
| K1:C3:two_accents:rule_held_back | 1597 | 0 | 641 | 2 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 200 | 0 | 181 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 12 | 0 | 10 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 281 | 0 | 258 | 0 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 2 | 0 | 2 | 0 |
| detector_clipped_bottom | 40732 | 0 | 15658 | 260 |
| detector_clipped_top | 93007 | 0 | 19927 | 882 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 36 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 28 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 9 |
| edit_guard:punctuation_mismatch | 3437 | 2268 | 2268 | 36 |
| edit_guard:unsupported_character:0 | 1166 | 8 | 25 | 0 |
| edit_guard:unsupported_character:1 | 510 | 3 | 12 | 0 |
| edit_guard:unsupported_character:10 | 146 | 2 | 4 | 0 |
| edit_guard:unsupported_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_character:15 | 112 | 2 | 3 | 0 |
| edit_guard:unsupported_character:17 | 256 | 4 | 7 | 0 |
| edit_guard:unsupported_character:18 | 156 | 1 | 3 | 0 |
| edit_guard:unsupported_character:19 | 309 | 3 | 8 | 0 |
| edit_guard:unsupported_character:2 | 313 | 1 | 8 | 0 |
| edit_guard:unsupported_character:20 | 40 | 1 | 1 | 0 |
| edit_guard:unsupported_character:21 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:22 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:23 | 72 | 1 | 2 | 0 |
| edit_guard:unsupported_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_character:25 | 91 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 171 | 2 | 4 | 0 |
| edit_guard:unsupported_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_character:28 | 222 | 4 | 5 | 0 |
| edit_guard:unsupported_character:29 | 169 | 3 | 3 | 0 |
| edit_guard:unsupported_character:3 | 657 | 1 | 18 | 0 |
| edit_guard:unsupported_character:30 | 78 | 1 | 2 | 0 |
| edit_guard:unsupported_character:31 | 313 | 2 | 7 | 0 |
| edit_guard:unsupported_character:32 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:33 | 145 | 0 | 3 | 0 |
| edit_guard:unsupported_character:34 | 213 | 2 | 5 | 0 |
| edit_guard:unsupported_character:35 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:36 | 215 | 3 | 5 | 0 |
| edit_guard:unsupported_character:37 | 138 | 1 | 3 | 0 |
| edit_guard:unsupported_character:38 | 94 | 1 | 2 | 0 |
| edit_guard:unsupported_character:39 | 240 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 225 | 3 | 7 | 0 |
| edit_guard:unsupported_character:40 | 426 | 2 | 9 | 0 |
| edit_guard:unsupported_character:41 | 240 | 2 | 5 | 0 |
| edit_guard:unsupported_character:42 | 327 | 3 | 7 | 0 |
| edit_guard:unsupported_character:43 | 412 | 4 | 8 | 0 |
| edit_guard:unsupported_character:44 | 47 | 1 | 1 | 0 |
| edit_guard:unsupported_character:45 | 189 | 1 | 3 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:48 | 100 | 2 | 2 | 0 |
| edit_guard:unsupported_character:49 | 203 | 2 | 4 | 0 |
| edit_guard:unsupported_character:5 | 345 | 2 | 6 | 0 |
| edit_guard:unsupported_character:50 | 109 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_character:6 | 251 | 1 | 6 | 0 |
| edit_guard:unsupported_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_character:7 | 350 | 4 | 7 | 0 |
| edit_guard:unsupported_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_character:76 | 163 | 0 | 2 | 0 |
| edit_guard:unsupported_character:8 | 176 | 1 | 4 | 0 |
| edit_guard:unsupported_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_character:9 | 296 | 6 | 7 | 0 |
| edit_guard:unsupported_raw_character:0 | 1166 | 3 | 28 | 0 |
| edit_guard:unsupported_raw_character:1 | 541 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:10 | 146 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:15 | 112 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:17 | 256 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:18 | 156 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:19 | 286 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:2 | 266 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:20 | 40 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:21 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:23 | 72 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:25 | 131 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 346 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:29 | 169 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:3 | 621 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:30 | 78 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 313 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:32 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 103 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:34 | 213 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:35 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:36 | 215 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 138 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:39 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 225 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:40 | 374 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:41 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:42 | 376 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:43 | 412 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:44 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 189 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:48 | 100 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:49 | 203 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:5 | 345 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 109 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:6 | 251 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 350 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:76 | 80 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:9 | 402 | 0 | 9 | 0 |
| mark_kind_disagreement | 59419 | 0 | 17856 | 294 |
| r1_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_missing | 757 | 0 | 390 | 0 |
| r1_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3544 |
| A/B disagreement | 0 |
| kind disagreement | 17856 |
| R1 uncertainty | 744 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 2615 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 2561 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1449 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1405 |
| ["detector_clipped_top","mark_kind_disagreement"] | 1057 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 969 |
| ["detector_clipped_top"] | 882 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 847 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 765 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 681 |

### ALL / anemi_mixed

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 48 | 0 | 47 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 102 | 0 | 99 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 2 | 0 | 2 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:evidence_tie | 4 | 0 | 2 | 0 |
| K1:C3:two_accents:rule_held_back | 868 | 0 | 379 | 3 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 123 | 0 | 121 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 214 | 0 | 201 | 3 |
| detector_clipped_bottom | 15059 | 0 | 6360 | 156 |
| detector_clipped_top | 39633 | 0 | 8777 | 690 |
| detector_localisation_unknown | 8716 | 0 | 3345 | 0 |
| detector_segmentation_uncertain | 17133 | 0 | 5085 | 29 |
| detector_unnamed_mark | 2392 | 0 | 1939 | 10 |
| edit_guard:base_or_character_mismatch | 389 | 1258 | 1258 | 6 |
| edit_guard:punctuation_mismatch | 1184 | 1470 | 1470 | 50 |
| edit_guard:unsupported_character:0 | 570 | 6 | 14 | 0 |
| edit_guard:unsupported_character:1 | 335 | 3 | 8 | 0 |
| edit_guard:unsupported_character:10 | 312 | 5 | 8 | 0 |
| edit_guard:unsupported_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 49 | 1 | 1 | 0 |
| edit_guard:unsupported_character:13 | 211 | 3 | 5 | 0 |
| edit_guard:unsupported_character:14 | 107 | 3 | 3 | 0 |
| edit_guard:unsupported_character:15 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:16 | 192 | 3 | 5 | 0 |
| edit_guard:unsupported_character:17 | 27 | 1 | 1 | 0 |
| edit_guard:unsupported_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:19 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_character:20 | 113 | 2 | 3 | 0 |
| edit_guard:unsupported_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_character:22 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_character:25 | 97 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 104 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 209 | 3 | 5 | 0 |
| edit_guard:unsupported_character:28 | 288 | 2 | 7 | 0 |
| edit_guard:unsupported_character:29 | 68 | 1 | 1 | 0 |
| edit_guard:unsupported_character:3 | 270 | 3 | 7 | 0 |
| edit_guard:unsupported_character:30 | 158 | 3 | 4 | 0 |
| edit_guard:unsupported_character:31 | 260 | 2 | 6 | 0 |
| edit_guard:unsupported_character:32 | 155 | 1 | 4 | 0 |
| edit_guard:unsupported_character:33 | 114 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_character:36 | 165 | 1 | 4 | 0 |
| edit_guard:unsupported_character:37 | 307 | 3 | 7 | 0 |
| edit_guard:unsupported_character:38 | 130 | 1 | 3 | 0 |
| edit_guard:unsupported_character:39 | 134 | 2 | 3 | 0 |
| edit_guard:unsupported_character:4 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_character:41 | 101 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 233 | 3 | 5 | 0 |
| edit_guard:unsupported_character:43 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:44 | 253 | 3 | 5 | 0 |
| edit_guard:unsupported_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_character:46 | 144 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 102 | 1 | 2 | 0 |
| edit_guard:unsupported_character:48 | 102 | 2 | 2 | 0 |
| edit_guard:unsupported_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_character:50 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_character:6 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 145 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 227 | 4 | 5 | 0 |
| edit_guard:unsupported_raw_character:0 | 563 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:1 | 335 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 312 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:13 | 211 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:14 | 156 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:16 | 192 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:17 | 27 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:19 | 97 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:20 | 113 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:25 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:26 | 131 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 209 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:28 | 288 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:29 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 270 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:30 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:31 | 260 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:32 | 155 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 114 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 165 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 307 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:38 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:4 | 130 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:41 | 101 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 233 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:44 | 253 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:46 | 144 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 102 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:48 | 102 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:50 | 57 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:8 | 227 | 0 | 5 | 0 |
| mark_kind_disagreement | 26287 | 0 | 9517 | 964 |
| r1_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_missing | 418 | 0 | 244 | 0 |
| r1_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 132 | 0 | 51 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 266 | 0 | 200 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6032 |
| clipping | 9594 |
| K1 | 609 |
| edit-guard | 2191 |
| A/B disagreement | 0 |
| kind disagreement | 9517 |
| R1 uncertainty | 294 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 1438 |
| ["mark_kind_disagreement"] | 964 |
| ["detector_clipped_bottom","detector_clipped_top"] | 940 |
| ["detector_clipped_top","mark_kind_disagreement"] | 819 |
| ["detector_clipped_top"] | 690 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 546 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 519 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 470 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 387 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 322 |

### ALL / anemi_round1

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 0 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 11 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 3 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 2 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 596 |
| detector_clipped_top | 140308 | 0 | 29544 | 2188 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 127 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 41 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 33 |
| edit_guard:punctuation_mismatch | 9153 | 6398 | 6398 | 207 |
| edit_guard:unsupported_character:0 | 3286 | 23 | 79 | 0 |
| edit_guard:unsupported_character:1 | 2211 | 16 | 47 | 0 |
| edit_guard:unsupported_character:10 | 439 | 5 | 12 | 0 |
| edit_guard:unsupported_character:11 | 317 | 3 | 9 | 0 |
| edit_guard:unsupported_character:12 | 144 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 283 | 6 | 9 | 0 |
| edit_guard:unsupported_character:14 | 407 | 9 | 13 | 0 |
| edit_guard:unsupported_character:15 | 470 | 7 | 14 | 0 |
| edit_guard:unsupported_character:16 | 268 | 3 | 7 | 0 |
| edit_guard:unsupported_character:17 | 383 | 4 | 9 | 0 |
| edit_guard:unsupported_character:18 | 295 | 3 | 8 | 0 |
| edit_guard:unsupported_character:19 | 337 | 3 | 10 | 0 |
| edit_guard:unsupported_character:2 | 409 | 4 | 11 | 0 |
| edit_guard:unsupported_character:20 | 535 | 6 | 13 | 0 |
| edit_guard:unsupported_character:21 | 407 | 4 | 12 | 0 |
| edit_guard:unsupported_character:22 | 427 | 8 | 11 | 0 |
| edit_guard:unsupported_character:23 | 668 | 7 | 19 | 0 |
| edit_guard:unsupported_character:24 | 469 | 7 | 11 | 0 |
| edit_guard:unsupported_character:25 | 228 | 3 | 7 | 0 |
| edit_guard:unsupported_character:26 | 599 | 6 | 15 | 0 |
| edit_guard:unsupported_character:27 | 636 | 6 | 17 | 0 |
| edit_guard:unsupported_character:28 | 581 | 6 | 17 | 0 |
| edit_guard:unsupported_character:29 | 1243 | 12 | 33 | 0 |
| edit_guard:unsupported_character:3 | 622 | 2 | 15 | 0 |
| edit_guard:unsupported_character:30 | 652 | 5 | 18 | 0 |
| edit_guard:unsupported_character:31 | 551 | 3 | 15 | 0 |
| edit_guard:unsupported_character:32 | 684 | 4 | 18 | 0 |
| edit_guard:unsupported_character:33 | 538 | 5 | 13 | 0 |
| edit_guard:unsupported_character:34 | 781 | 4 | 18 | 0 |
| edit_guard:unsupported_character:35 | 701 | 6 | 17 | 0 |
| edit_guard:unsupported_character:36 | 745 | 2 | 19 | 0 |
| edit_guard:unsupported_character:37 | 765 | 5 | 19 | 0 |
| edit_guard:unsupported_character:38 | 408 | 1 | 10 | 0 |
| edit_guard:unsupported_character:39 | 791 | 6 | 18 | 0 |
| edit_guard:unsupported_character:4 | 497 | 4 | 11 | 0 |
| edit_guard:unsupported_character:40 | 448 | 3 | 10 | 0 |
| edit_guard:unsupported_character:41 | 811 | 5 | 18 | 0 |
| edit_guard:unsupported_character:42 | 454 | 4 | 10 | 0 |
| edit_guard:unsupported_character:43 | 569 | 6 | 12 | 0 |
| edit_guard:unsupported_character:44 | 300 | 3 | 6 | 0 |
| edit_guard:unsupported_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_character:46 | 262 | 1 | 5 | 0 |
| edit_guard:unsupported_character:47 | 207 | 4 | 4 | 0 |
| edit_guard:unsupported_character:48 | 251 | 2 | 5 | 0 |
| edit_guard:unsupported_character:49 | 315 | 1 | 6 | 0 |
| edit_guard:unsupported_character:5 | 299 | 2 | 7 | 0 |
| edit_guard:unsupported_character:50 | 284 | 3 | 5 | 0 |
| edit_guard:unsupported_character:51 | 495 | 3 | 9 | 0 |
| edit_guard:unsupported_character:52 | 175 | 1 | 3 | 0 |
| edit_guard:unsupported_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_character:54 | 202 | 2 | 3 | 0 |
| edit_guard:unsupported_character:55 | 247 | 2 | 4 | 0 |
| edit_guard:unsupported_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_character:57 | 202 | 1 | 3 | 0 |
| edit_guard:unsupported_character:58 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:59 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 421 | 2 | 12 | 0 |
| edit_guard:unsupported_character:60 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_character:62 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:65 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 431 | 3 | 9 | 0 |
| edit_guard:unsupported_character:74 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:8 | 618 | 4 | 15 | 0 |
| edit_guard:unsupported_character:9 | 433 | 4 | 11 | 0 |
| edit_guard:unsupported_raw_character:0 | 3282 | 1 | 78 | 0 |
| edit_guard:unsupported_raw_character:1 | 1715 | 0 | 40 | 0 |
| edit_guard:unsupported_raw_character:10 | 439 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:11 | 339 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:12 | 144 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:13 | 283 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:14 | 424 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:15 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:16 | 302 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:17 | 383 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:18 | 317 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:19 | 379 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:2 | 409 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:20 | 535 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:21 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:22 | 427 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:23 | 668 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:24 | 469 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:25 | 228 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:26 | 599 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:27 | 636 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:28 | 581 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:29 | 1243 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:3 | 644 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:30 | 652 | 1 | 19 | 0 |
| edit_guard:unsupported_raw_character:31 | 551 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:32 | 718 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:33 | 543 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:34 | 742 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:35 | 701 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:36 | 745 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:37 | 806 | 0 | 20 | 0 |
| edit_guard:unsupported_raw_character:38 | 402 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:39 | 831 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:4 | 497 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:40 | 448 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:41 | 811 | 0 | 18 | 0 |
| edit_guard:unsupported_raw_character:42 | 454 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:43 | 569 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:44 | 300 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:46 | 262 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:47 | 207 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:48 | 251 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:49 | 315 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:5 | 270 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 233 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 436 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:52 | 175 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:54 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:55 | 247 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:57 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:58 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:59 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 421 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:60 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:62 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:65 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 471 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:74 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 545 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:9 | 433 | 0 | 11 | 0 |
| mark_kind_disagreement | 73450 | 0 | 30611 | 2924 |
| r1_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_missing | 1687 | 0 | 1129 | 0 |
| r1_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9251 |
| A/B disagreement | 0 |
| kind disagreement | 30611 |
| R1 uncertainty | 1276 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 4389 |
| ["detector_clipped_bottom","detector_clipped_top"] | 3171 |
| ["mark_kind_disagreement"] | 2924 |
| ["detector_clipped_top","mark_kind_disagreement"] | 2456 |
| ["detector_clipped_top"] | 2188 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1925 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 1367 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1223 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1141 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 1052 |

### ALL / anemi_round2

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 84 | 0 | 81 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 107 | 0 | 103 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 6 | 0 | 3 | 0 |
| K1:C3:two_accents:rule_held_back | 1020 | 0 | 467 | 4 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 101 | 0 | 98 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 1 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 216 |
| detector_clipped_top | 48664 | 0 | 10763 | 911 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 49 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 22 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 18 |
| edit_guard:punctuation_mismatch | 1491 | 2095 | 2095 | 113 |
| edit_guard:unsupported_character:0 | 1107 | 12 | 28 | 0 |
| edit_guard:unsupported_character:1 | 360 | 2 | 9 | 0 |
| edit_guard:unsupported_character:10 | 169 | 1 | 4 | 0 |
| edit_guard:unsupported_character:11 | 54 | 1 | 1 | 0 |
| edit_guard:unsupported_character:12 | 178 | 3 | 5 | 0 |
| edit_guard:unsupported_character:13 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_character:14 | 169 | 2 | 4 | 0 |
| edit_guard:unsupported_character:15 | 122 | 3 | 3 | 0 |
| edit_guard:unsupported_character:16 | 225 | 1 | 8 | 0 |
| edit_guard:unsupported_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_character:18 | 252 | 3 | 7 | 0 |
| edit_guard:unsupported_character:19 | 108 | 1 | 3 | 0 |
| edit_guard:unsupported_character:2 | 238 | 4 | 6 | 0 |
| edit_guard:unsupported_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_character:21 | 129 | 1 | 4 | 0 |
| edit_guard:unsupported_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_character:23 | 43 | 1 | 1 | 0 |
| edit_guard:unsupported_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_character:27 | 150 | 3 | 4 | 0 |
| edit_guard:unsupported_character:28 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 71 | 0 | 2 | 0 |
| edit_guard:unsupported_character:3 | 236 | 3 | 6 | 0 |
| edit_guard:unsupported_character:30 | 225 | 3 | 6 | 0 |
| edit_guard:unsupported_character:31 | 201 | 3 | 5 | 0 |
| edit_guard:unsupported_character:32 | 79 | 1 | 2 | 0 |
| edit_guard:unsupported_character:33 | 250 | 2 | 6 | 0 |
| edit_guard:unsupported_character:34 | 116 | 1 | 3 | 0 |
| edit_guard:unsupported_character:35 | 152 | 1 | 4 | 0 |
| edit_guard:unsupported_character:36 | 212 | 2 | 5 | 0 |
| edit_guard:unsupported_character:37 | 356 | 5 | 8 | 0 |
| edit_guard:unsupported_character:38 | 192 | 4 | 4 | 0 |
| edit_guard:unsupported_character:39 | 98 | 2 | 2 | 0 |
| edit_guard:unsupported_character:4 | 63 | 1 | 2 | 0 |
| edit_guard:unsupported_character:40 | 87 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 241 | 2 | 5 | 0 |
| edit_guard:unsupported_character:43 | 92 | 1 | 2 | 0 |
| edit_guard:unsupported_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_character:45 | 51 | 1 | 1 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_character:5 | 121 | 3 | 3 | 0 |
| edit_guard:unsupported_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_character:53 | 113 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_character:59 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 165 | 4 | 5 | 0 |
| edit_guard:unsupported_character:60 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 173 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 145 | 1 | 4 | 0 |
| edit_guard:unsupported_character:9 | 114 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:0 | 1012 | 0 | 26 | 0 |
| edit_guard:unsupported_raw_character:1 | 341 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 54 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 178 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:13 | 96 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:14 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 122 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:16 | 225 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 252 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:19 | 108 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:2 | 238 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:21 | 98 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:23 | 43 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:28 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 41 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 236 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:30 | 193 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:31 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:32 | 79 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 250 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:34 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:35 | 152 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:36 | 212 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 356 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:38 | 192 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:4 | 79 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 241 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 92 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 148 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 113 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:59 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 165 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:60 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 148 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:8 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:9 | 114 | 0 | 4 | 0 |
| mark_kind_disagreement | 27905 | 0 | 11778 | 1590 |
| r1_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_missing | 434 | 0 | 268 | 0 |
| r1_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3059 |
| A/B disagreement | 0 |
| kind disagreement | 11778 |
| R1 uncertainty | 354 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 1794 |
| ["mark_kind_disagreement"] | 1590 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1212 |
| ["detector_clipped_top","mark_kind_disagreement"] | 1078 |
| ["detector_clipped_top"] | 911 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 559 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 483 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 457 |
| ["detector_segmentation_uncertain","mark_kind_disagreement"] | 343 |
| ["detector_unnamed_mark","mark_kind_disagreement"] | 323 |

### ALL / archive_b28038630

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 2 | 0 | 1 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 130 | 0 | 45 | 1 |
| detector_clipped_top | 254 | 0 | 58 | 6 |
| detector_localisation_unknown | 7 | 0 | 6 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 13 | 13 | 0 |
| edit_guard:punctuation_mismatch | 0 | 22 | 22 | 5 |
| mark_kind_disagreement | 75 | 0 | 49 | 4 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 13 |
| clipping | 61 |
| K1 | 3 |
| edit-guard | 24 |
| A/B disagreement | 0 |
| kind disagreement | 49 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 17 |
| ["detector_clipped_bottom","detector_clipped_top"] | 8 |
| ["detector_clipped_top"] | 6 |
| ["detector_clipped_top","mark_kind_disagreement"] | 5 |
| ["edit_guard:punctuation_mismatch"] | 5 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 4 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 4 |
| ["mark_kind_disagreement"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch"] | 2 |

### ALL / openarchives_Pandemos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_clipped_bottom | 366 | 0 | 118 | 19 |
| detector_clipped_top | 604 | 0 | 118 | 20 |
| detector_segmentation_uncertain | 100 | 0 | 35 | 0 |
| detector_unnamed_mark | 23 | 0 | 18 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 9 | 9 | 0 |
| mark_kind_disagreement | 184 | 0 | 83 | 4 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 46 |
| clipping | 157 |
| K1 | 0 |
| edit-guard | 9 |
| A/B disagreement | 0 |
| kind disagreement | 83 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 43 |
| ["detector_clipped_top"] | 20 |
| ["detector_clipped_bottom"] | 19 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 18 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","mark_kind_disagreement"] | 9 |
| ["detector_clipped_bottom","mark_kind_disagreement"] | 8 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 7 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 7 |
| ["detector_segmentation_uncertain","mark_kind_disagreement"] | 6 |
| ["detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 5 |

### ALL / openarchives_kallipos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 12 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_top | 25 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 10 | 0 | 3 | 0 |
| detector_unnamed_mark | 1 | 0 | 1 | 0 |
| edit_guard:punctuation_mismatch | 0 | 10 | 10 | 3 |
| mark_kind_disagreement | 57 | 0 | 33 | 19 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 2 |
| K1 | 5 |
| edit-guard | 10 |
| A/B disagreement | 0 |
| kind disagreement | 33 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_kind_disagreement"] | 19 |
| ["edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 4 |
| ["detector_segmentation_uncertain","mark_kind_disagreement"] | 3 |
| ["edit_guard:punctuation_mismatch"] | 3 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","mark_kind_disagreement"] | 2 |
| ["detector_clipped_top","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 2 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_unnamed_mark","mark_kind_disagreement"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 1 |
| ["K1:C3:two_accents:rule_held_back","mark_kind_disagreement"] | 1 |

### ALL / openarchives_mixed_Pandemos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_clipped_bottom | 16 | 0 | 7 | 0 |
| detector_clipped_top | 27 | 0 | 4 | 0 |
| detector_localisation_unknown | 5 | 0 | 1 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 2 | 0 |
| detector_unnamed_mark | 3 | 0 | 3 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 1 | 1 | 0 |
| edit_guard:punctuation_mismatch | 0 | 1 | 1 | 0 |
| mark_kind_disagreement | 25 | 0 | 10 | 2 |
| r1_missing | 1 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 7 |
| K1 | 0 |
| edit-guard | 2 |
| A/B disagreement | 0 |
| kind disagreement | 10 |
| R1 uncertainty | 1 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top"] | 2 |
| ["detector_clipped_bottom","mark_kind_disagreement"] | 2 |
| ["mark_kind_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 1 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","mark_kind_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |
| ["detector_unnamed_mark","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 1 |
| ["detector_unnamed_mark","mark_kind_disagreement"] | 1 |

### ALL / openarchives_mixed_apothesis

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| mark_kind_disagreement | 1 | 0 | 1 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 0 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 1 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_kind_disagreement"] | 1 |

### ALL / openarchives_mixed_ktisis

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_unnamed_mark | 1 | 0 | 1 | 1 |
| mark_kind_disagreement | 1 | 0 | 1 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 1 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 1 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_unnamed_mark"] | 1 |
| ["mark_kind_disagreement"] | 1 |

### ALL / openarchives_mixed_ntua

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_not_initial:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:rule_held_back | 4 | 0 | 2 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_bottom | 11 | 0 | 5 | 0 |
| detector_clipped_top | 29 | 0 | 5 | 0 |
| detector_localisation_unknown | 15 | 0 | 3 | 0 |
| detector_segmentation_uncertain | 27 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 21 | 21 | 0 |
| edit_guard:punctuation_mismatch | 104 | 16 | 16 | 0 |
| edit_guard:unsupported_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| mark_kind_disagreement | 133 | 0 | 30 | 5 |
| r1_missing | 21 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 18 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 3 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 12 |
| clipping | 7 |
| K1 | 4 |
| edit-guard | 22 |
| A/B disagreement | 0 |
| kind disagreement | 30 |
| R1 uncertainty | 4 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 7 |
| ["mark_kind_disagreement"] | 5 |
| ["edit_guard:base_or_character_mismatch","mark_kind_disagreement"] | 2 |
| ["K1:C1:breathing_not_initial:impossible_by_rule","K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","edit_guard:unsupported_character:28","edit_guard:unsupported_raw_character:28","mark_kind_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","r1_unscored:width_outside_0.2_2.0_median_ctc"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","mark_kind_disagreement"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","mark_kind_disagreement"] | 1 |
| ["detector_clipped_bottom","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |

### ALL / parliament_proceedings_1975_2000

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 69 | 0 | 67 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 90 | 0 | 88 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C3:two_accents:evidence_tie | 14 | 0 | 7 | 0 |
| K1:C3:two_accents:rule_held_back | 1343 | 0 | 613 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 159 | 0 | 155 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 7 | 0 | 7 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 292 | 0 | 253 | 0 |
| detector_clipped_bottom | 44633 | 0 | 16119 | 79 |
| detector_clipped_top | 98404 | 0 | 20688 | 237 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 52 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 10 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 2 |
| edit_guard:punctuation_mismatch | 1472 | 2781 | 2781 | 8 |
| edit_guard:unsupported_character:0 | 1663 | 17 | 43 | 0 |
| edit_guard:unsupported_character:1 | 594 | 4 | 17 | 0 |
| edit_guard:unsupported_character:10 | 206 | 3 | 6 | 0 |
| edit_guard:unsupported_character:11 | 221 | 5 | 5 | 0 |
| edit_guard:unsupported_character:12 | 139 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 254 | 4 | 7 | 0 |
| edit_guard:unsupported_character:14 | 201 | 1 | 5 | 0 |
| edit_guard:unsupported_character:15 | 64 | 2 | 2 | 0 |
| edit_guard:unsupported_character:17 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:18 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:19 | 46 | 1 | 1 | 0 |
| edit_guard:unsupported_character:2 | 565 | 4 | 17 | 0 |
| edit_guard:unsupported_character:20 | 277 | 4 | 7 | 0 |
| edit_guard:unsupported_character:21 | 135 | 4 | 4 | 0 |
| edit_guard:unsupported_character:22 | 200 | 3 | 5 | 0 |
| edit_guard:unsupported_character:23 | 94 | 2 | 2 | 0 |
| edit_guard:unsupported_character:24 | 258 | 3 | 7 | 0 |
| edit_guard:unsupported_character:25 | 163 | 1 | 5 | 0 |
| edit_guard:unsupported_character:26 | 121 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 291 | 6 | 7 | 0 |
| edit_guard:unsupported_character:28 | 75 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 160 | 2 | 4 | 0 |
| edit_guard:unsupported_character:3 | 559 | 5 | 15 | 0 |
| edit_guard:unsupported_character:30 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:31 | 157 | 4 | 4 | 0 |
| edit_guard:unsupported_character:32 | 88 | 2 | 2 | 0 |
| edit_guard:unsupported_character:33 | 112 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 254 | 3 | 6 | 0 |
| edit_guard:unsupported_character:35 | 80 | 2 | 2 | 0 |
| edit_guard:unsupported_character:36 | 183 | 2 | 4 | 0 |
| edit_guard:unsupported_character:37 | 132 | 2 | 3 | 0 |
| edit_guard:unsupported_character:38 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:39 | 227 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 349 | 3 | 9 | 0 |
| edit_guard:unsupported_character:40 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:41 | 436 | 7 | 10 | 0 |
| edit_guard:unsupported_character:42 | 176 | 2 | 4 | 0 |
| edit_guard:unsupported_character:43 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:44 | 180 | 2 | 4 | 0 |
| edit_guard:unsupported_character:45 | 188 | 3 | 4 | 0 |
| edit_guard:unsupported_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_character:49 | 50 | 1 | 1 | 0 |
| edit_guard:unsupported_character:5 | 142 | 2 | 3 | 0 |
| edit_guard:unsupported_character:6 | 168 | 2 | 4 | 0 |
| edit_guard:unsupported_character:7 | 417 | 3 | 11 | 0 |
| edit_guard:unsupported_character:8 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:9 | 265 | 3 | 6 | 0 |
| edit_guard:unsupported_raw_character:0 | 1567 | 2 | 41 | 0 |
| edit_guard:unsupported_raw_character:1 | 521 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:10 | 206 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:11 | 221 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:12 | 139 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 254 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:14 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:15 | 64 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:17 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:18 | 179 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:19 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:2 | 546 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:20 | 277 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:21 | 135 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:22 | 200 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:23 | 142 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:24 | 210 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:25 | 163 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:26 | 121 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 291 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:28 | 75 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 191 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:3 | 559 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:30 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 157 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:32 | 88 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 112 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:34 | 254 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:35 | 80 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 183 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 132 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 227 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 349 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:40 | 222 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:41 | 393 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:42 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:43 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_raw_character:44 | 180 | 1 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 188 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:49 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 142 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:6 | 168 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 393 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:8 | 94 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:9 | 265 | 0 | 6 | 0 |
| mark_kind_disagreement | 111173 | 0 | 21977 | 159 |
| r1_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_missing | 1452 | 0 | 955 | 0 |
| r1_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4765 |
| A/B disagreement | 0 |
| kind disagreement | 21977 |
| R1 uncertainty | 1829 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 4161 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 2749 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 2237 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1432 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1308 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 1263 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 984 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 822 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 650 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 495 |

### ALL / vouli_parliament_1850s

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 86 | 0 | 83 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 130 | 0 | 120 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 3 | 0 | 3 | 0 |
| K1:C3:two_accents:evidence_tie | 18 | 0 | 9 | 0 |
| K1:C3:two_accents:rule_held_back | 1597 | 0 | 641 | 2 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 200 | 0 | 181 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 12 | 0 | 10 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 281 | 0 | 258 | 0 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 2 | 0 | 2 | 0 |
| detector_clipped_bottom | 40732 | 0 | 15658 | 260 |
| detector_clipped_top | 93007 | 0 | 19927 | 882 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 36 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 28 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 9 |
| edit_guard:punctuation_mismatch | 3437 | 2268 | 2268 | 36 |
| edit_guard:unsupported_character:0 | 1166 | 8 | 25 | 0 |
| edit_guard:unsupported_character:1 | 510 | 3 | 12 | 0 |
| edit_guard:unsupported_character:10 | 146 | 2 | 4 | 0 |
| edit_guard:unsupported_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_character:15 | 112 | 2 | 3 | 0 |
| edit_guard:unsupported_character:17 | 256 | 4 | 7 | 0 |
| edit_guard:unsupported_character:18 | 156 | 1 | 3 | 0 |
| edit_guard:unsupported_character:19 | 309 | 3 | 8 | 0 |
| edit_guard:unsupported_character:2 | 313 | 1 | 8 | 0 |
| edit_guard:unsupported_character:20 | 40 | 1 | 1 | 0 |
| edit_guard:unsupported_character:21 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:22 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:23 | 72 | 1 | 2 | 0 |
| edit_guard:unsupported_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_character:25 | 91 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 171 | 2 | 4 | 0 |
| edit_guard:unsupported_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_character:28 | 222 | 4 | 5 | 0 |
| edit_guard:unsupported_character:29 | 169 | 3 | 3 | 0 |
| edit_guard:unsupported_character:3 | 657 | 1 | 18 | 0 |
| edit_guard:unsupported_character:30 | 78 | 1 | 2 | 0 |
| edit_guard:unsupported_character:31 | 313 | 2 | 7 | 0 |
| edit_guard:unsupported_character:32 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:33 | 145 | 0 | 3 | 0 |
| edit_guard:unsupported_character:34 | 213 | 2 | 5 | 0 |
| edit_guard:unsupported_character:35 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:36 | 215 | 3 | 5 | 0 |
| edit_guard:unsupported_character:37 | 138 | 1 | 3 | 0 |
| edit_guard:unsupported_character:38 | 94 | 1 | 2 | 0 |
| edit_guard:unsupported_character:39 | 240 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 225 | 3 | 7 | 0 |
| edit_guard:unsupported_character:40 | 426 | 2 | 9 | 0 |
| edit_guard:unsupported_character:41 | 240 | 2 | 5 | 0 |
| edit_guard:unsupported_character:42 | 327 | 3 | 7 | 0 |
| edit_guard:unsupported_character:43 | 412 | 4 | 8 | 0 |
| edit_guard:unsupported_character:44 | 47 | 1 | 1 | 0 |
| edit_guard:unsupported_character:45 | 189 | 1 | 3 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:48 | 100 | 2 | 2 | 0 |
| edit_guard:unsupported_character:49 | 203 | 2 | 4 | 0 |
| edit_guard:unsupported_character:5 | 345 | 2 | 6 | 0 |
| edit_guard:unsupported_character:50 | 109 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_character:6 | 251 | 1 | 6 | 0 |
| edit_guard:unsupported_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_character:7 | 350 | 4 | 7 | 0 |
| edit_guard:unsupported_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_character:76 | 163 | 0 | 2 | 0 |
| edit_guard:unsupported_character:8 | 176 | 1 | 4 | 0 |
| edit_guard:unsupported_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_character:9 | 296 | 6 | 7 | 0 |
| edit_guard:unsupported_raw_character:0 | 1166 | 3 | 28 | 0 |
| edit_guard:unsupported_raw_character:1 | 541 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:10 | 146 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:15 | 112 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:17 | 256 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:18 | 156 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:19 | 286 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:2 | 266 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:20 | 40 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:21 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:23 | 72 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:25 | 131 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 346 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:29 | 169 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:3 | 621 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:30 | 78 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 313 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:32 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 103 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:34 | 213 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:35 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:36 | 215 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 138 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:39 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 225 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:40 | 374 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:41 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:42 | 376 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:43 | 412 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:44 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 189 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:48 | 100 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:49 | 203 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:5 | 345 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 109 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:6 | 251 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 350 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:76 | 80 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:9 | 402 | 0 | 9 | 0 |
| mark_kind_disagreement | 59419 | 0 | 17856 | 294 |
| r1_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_missing | 757 | 0 | 390 | 0 |
| r1_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3544 |
| A/B disagreement | 0 |
| kind disagreement | 17856 |
| R1 uncertainty | 744 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 2615 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 2561 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1449 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1405 |
| ["detector_clipped_top","mark_kind_disagreement"] | 1057 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 969 |
| ["detector_clipped_top"] | 882 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 847 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 765 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 681 |

### mixed / anemi_mixed

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 48 | 0 | 47 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 102 | 0 | 99 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 2 | 0 | 2 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:evidence_tie | 4 | 0 | 2 | 0 |
| K1:C3:two_accents:rule_held_back | 868 | 0 | 379 | 3 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 123 | 0 | 121 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 214 | 0 | 201 | 3 |
| detector_clipped_bottom | 15059 | 0 | 6360 | 156 |
| detector_clipped_top | 39633 | 0 | 8777 | 690 |
| detector_localisation_unknown | 8716 | 0 | 3345 | 0 |
| detector_segmentation_uncertain | 17133 | 0 | 5085 | 29 |
| detector_unnamed_mark | 2392 | 0 | 1939 | 10 |
| edit_guard:base_or_character_mismatch | 389 | 1258 | 1258 | 6 |
| edit_guard:punctuation_mismatch | 1184 | 1470 | 1470 | 50 |
| edit_guard:unsupported_character:0 | 570 | 6 | 14 | 0 |
| edit_guard:unsupported_character:1 | 335 | 3 | 8 | 0 |
| edit_guard:unsupported_character:10 | 312 | 5 | 8 | 0 |
| edit_guard:unsupported_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 49 | 1 | 1 | 0 |
| edit_guard:unsupported_character:13 | 211 | 3 | 5 | 0 |
| edit_guard:unsupported_character:14 | 107 | 3 | 3 | 0 |
| edit_guard:unsupported_character:15 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:16 | 192 | 3 | 5 | 0 |
| edit_guard:unsupported_character:17 | 27 | 1 | 1 | 0 |
| edit_guard:unsupported_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:19 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_character:20 | 113 | 2 | 3 | 0 |
| edit_guard:unsupported_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_character:22 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_character:25 | 97 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 104 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 209 | 3 | 5 | 0 |
| edit_guard:unsupported_character:28 | 288 | 2 | 7 | 0 |
| edit_guard:unsupported_character:29 | 68 | 1 | 1 | 0 |
| edit_guard:unsupported_character:3 | 270 | 3 | 7 | 0 |
| edit_guard:unsupported_character:30 | 158 | 3 | 4 | 0 |
| edit_guard:unsupported_character:31 | 260 | 2 | 6 | 0 |
| edit_guard:unsupported_character:32 | 155 | 1 | 4 | 0 |
| edit_guard:unsupported_character:33 | 114 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_character:36 | 165 | 1 | 4 | 0 |
| edit_guard:unsupported_character:37 | 307 | 3 | 7 | 0 |
| edit_guard:unsupported_character:38 | 130 | 1 | 3 | 0 |
| edit_guard:unsupported_character:39 | 134 | 2 | 3 | 0 |
| edit_guard:unsupported_character:4 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_character:41 | 101 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 233 | 3 | 5 | 0 |
| edit_guard:unsupported_character:43 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:44 | 253 | 3 | 5 | 0 |
| edit_guard:unsupported_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_character:46 | 144 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 102 | 1 | 2 | 0 |
| edit_guard:unsupported_character:48 | 102 | 2 | 2 | 0 |
| edit_guard:unsupported_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_character:50 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_character:6 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 145 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 227 | 4 | 5 | 0 |
| edit_guard:unsupported_raw_character:0 | 563 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:1 | 335 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 312 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:13 | 211 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:14 | 156 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:16 | 192 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:17 | 27 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:19 | 97 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:20 | 113 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:25 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:26 | 131 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 209 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:28 | 288 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:29 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 270 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:30 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:31 | 260 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:32 | 155 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 114 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 165 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 307 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:38 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:4 | 130 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:41 | 101 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 233 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:44 | 253 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:46 | 144 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 102 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:48 | 102 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:50 | 57 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:8 | 227 | 0 | 5 | 0 |
| mark_kind_disagreement | 26287 | 0 | 9517 | 964 |
| r1_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_missing | 418 | 0 | 244 | 0 |
| r1_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 132 | 0 | 51 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 266 | 0 | 200 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6032 |
| clipping | 9594 |
| K1 | 609 |
| edit-guard | 2191 |
| A/B disagreement | 0 |
| kind disagreement | 9517 |
| R1 uncertainty | 294 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 1438 |
| ["mark_kind_disagreement"] | 964 |
| ["detector_clipped_bottom","detector_clipped_top"] | 940 |
| ["detector_clipped_top","mark_kind_disagreement"] | 819 |
| ["detector_clipped_top"] | 690 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 546 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 519 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 470 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 387 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 322 |

### mixed / archive_b28038630

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 2 | 0 | 1 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 130 | 0 | 45 | 1 |
| detector_clipped_top | 254 | 0 | 58 | 6 |
| detector_localisation_unknown | 7 | 0 | 6 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 13 | 13 | 0 |
| edit_guard:punctuation_mismatch | 0 | 22 | 22 | 5 |
| mark_kind_disagreement | 75 | 0 | 49 | 4 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 13 |
| clipping | 61 |
| K1 | 3 |
| edit-guard | 24 |
| A/B disagreement | 0 |
| kind disagreement | 49 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 17 |
| ["detector_clipped_bottom","detector_clipped_top"] | 8 |
| ["detector_clipped_top"] | 6 |
| ["detector_clipped_top","mark_kind_disagreement"] | 5 |
| ["edit_guard:punctuation_mismatch"] | 5 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 4 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 4 |
| ["mark_kind_disagreement"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch"] | 2 |

### mixed / openarchives_mixed_Pandemos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_clipped_bottom | 16 | 0 | 7 | 0 |
| detector_clipped_top | 27 | 0 | 4 | 0 |
| detector_localisation_unknown | 5 | 0 | 1 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 2 | 0 |
| detector_unnamed_mark | 3 | 0 | 3 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 1 | 1 | 0 |
| edit_guard:punctuation_mismatch | 0 | 1 | 1 | 0 |
| mark_kind_disagreement | 25 | 0 | 10 | 2 |
| r1_missing | 1 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 7 |
| K1 | 0 |
| edit-guard | 2 |
| A/B disagreement | 0 |
| kind disagreement | 10 |
| R1 uncertainty | 1 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top"] | 2 |
| ["detector_clipped_bottom","mark_kind_disagreement"] | 2 |
| ["mark_kind_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 1 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","mark_kind_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |
| ["detector_unnamed_mark","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 1 |
| ["detector_unnamed_mark","mark_kind_disagreement"] | 1 |

### mixed / openarchives_mixed_apothesis

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| mark_kind_disagreement | 1 | 0 | 1 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 0 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 1 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_kind_disagreement"] | 1 |

### mixed / openarchives_mixed_ktisis

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_unnamed_mark | 1 | 0 | 1 | 1 |
| mark_kind_disagreement | 1 | 0 | 1 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 1 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 1 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_unnamed_mark"] | 1 |
| ["mark_kind_disagreement"] | 1 |

### mixed / openarchives_mixed_ntua

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_not_initial:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:rule_held_back | 4 | 0 | 2 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_bottom | 11 | 0 | 5 | 0 |
| detector_clipped_top | 29 | 0 | 5 | 0 |
| detector_localisation_unknown | 15 | 0 | 3 | 0 |
| detector_segmentation_uncertain | 27 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 21 | 21 | 0 |
| edit_guard:punctuation_mismatch | 104 | 16 | 16 | 0 |
| edit_guard:unsupported_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| mark_kind_disagreement | 133 | 0 | 30 | 5 |
| r1_missing | 21 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 18 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 3 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 12 |
| clipping | 7 |
| K1 | 4 |
| edit-guard | 22 |
| A/B disagreement | 0 |
| kind disagreement | 30 |
| R1 uncertainty | 4 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 7 |
| ["mark_kind_disagreement"] | 5 |
| ["edit_guard:base_or_character_mismatch","mark_kind_disagreement"] | 2 |
| ["K1:C1:breathing_not_initial:impossible_by_rule","K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","edit_guard:unsupported_character:28","edit_guard:unsupported_raw_character:28","mark_kind_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","r1_unscored:width_outside_0.2_2.0_median_ctc"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","mark_kind_disagreement"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","mark_kind_disagreement"] | 1 |
| ["detector_clipped_bottom","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |

### openarchives / openarchives_Pandemos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_clipped_bottom | 366 | 0 | 118 | 19 |
| detector_clipped_top | 604 | 0 | 118 | 20 |
| detector_segmentation_uncertain | 100 | 0 | 35 | 0 |
| detector_unnamed_mark | 23 | 0 | 18 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 9 | 9 | 0 |
| mark_kind_disagreement | 184 | 0 | 83 | 4 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 46 |
| clipping | 157 |
| K1 | 0 |
| edit-guard | 9 |
| A/B disagreement | 0 |
| kind disagreement | 83 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 43 |
| ["detector_clipped_top"] | 20 |
| ["detector_clipped_bottom"] | 19 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 18 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","mark_kind_disagreement"] | 9 |
| ["detector_clipped_bottom","mark_kind_disagreement"] | 8 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 7 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 7 |
| ["detector_segmentation_uncertain","mark_kind_disagreement"] | 6 |
| ["detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 5 |

### openarchives / openarchives_kallipos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 12 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_top | 25 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 10 | 0 | 3 | 0 |
| detector_unnamed_mark | 1 | 0 | 1 | 0 |
| edit_guard:punctuation_mismatch | 0 | 10 | 10 | 3 |
| mark_kind_disagreement | 57 | 0 | 33 | 19 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 2 |
| K1 | 5 |
| edit-guard | 10 |
| A/B disagreement | 0 |
| kind disagreement | 33 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_kind_disagreement"] | 19 |
| ["edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 4 |
| ["detector_segmentation_uncertain","mark_kind_disagreement"] | 3 |
| ["edit_guard:punctuation_mismatch"] | 3 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","mark_kind_disagreement"] | 2 |
| ["detector_clipped_top","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 2 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_unnamed_mark","mark_kind_disagreement"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 1 |
| ["K1:C3:two_accents:rule_held_back","mark_kind_disagreement"] | 1 |

### parliament / parliament_proceedings_1975_2000

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 69 | 0 | 67 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 90 | 0 | 88 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C3:two_accents:evidence_tie | 14 | 0 | 7 | 0 |
| K1:C3:two_accents:rule_held_back | 1343 | 0 | 613 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 159 | 0 | 155 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 7 | 0 | 7 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 292 | 0 | 253 | 0 |
| detector_clipped_bottom | 44633 | 0 | 16119 | 79 |
| detector_clipped_top | 98404 | 0 | 20688 | 237 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 52 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 10 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 2 |
| edit_guard:punctuation_mismatch | 1472 | 2781 | 2781 | 8 |
| edit_guard:unsupported_character:0 | 1663 | 17 | 43 | 0 |
| edit_guard:unsupported_character:1 | 594 | 4 | 17 | 0 |
| edit_guard:unsupported_character:10 | 206 | 3 | 6 | 0 |
| edit_guard:unsupported_character:11 | 221 | 5 | 5 | 0 |
| edit_guard:unsupported_character:12 | 139 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 254 | 4 | 7 | 0 |
| edit_guard:unsupported_character:14 | 201 | 1 | 5 | 0 |
| edit_guard:unsupported_character:15 | 64 | 2 | 2 | 0 |
| edit_guard:unsupported_character:17 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:18 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:19 | 46 | 1 | 1 | 0 |
| edit_guard:unsupported_character:2 | 565 | 4 | 17 | 0 |
| edit_guard:unsupported_character:20 | 277 | 4 | 7 | 0 |
| edit_guard:unsupported_character:21 | 135 | 4 | 4 | 0 |
| edit_guard:unsupported_character:22 | 200 | 3 | 5 | 0 |
| edit_guard:unsupported_character:23 | 94 | 2 | 2 | 0 |
| edit_guard:unsupported_character:24 | 258 | 3 | 7 | 0 |
| edit_guard:unsupported_character:25 | 163 | 1 | 5 | 0 |
| edit_guard:unsupported_character:26 | 121 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 291 | 6 | 7 | 0 |
| edit_guard:unsupported_character:28 | 75 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 160 | 2 | 4 | 0 |
| edit_guard:unsupported_character:3 | 559 | 5 | 15 | 0 |
| edit_guard:unsupported_character:30 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:31 | 157 | 4 | 4 | 0 |
| edit_guard:unsupported_character:32 | 88 | 2 | 2 | 0 |
| edit_guard:unsupported_character:33 | 112 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 254 | 3 | 6 | 0 |
| edit_guard:unsupported_character:35 | 80 | 2 | 2 | 0 |
| edit_guard:unsupported_character:36 | 183 | 2 | 4 | 0 |
| edit_guard:unsupported_character:37 | 132 | 2 | 3 | 0 |
| edit_guard:unsupported_character:38 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:39 | 227 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 349 | 3 | 9 | 0 |
| edit_guard:unsupported_character:40 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:41 | 436 | 7 | 10 | 0 |
| edit_guard:unsupported_character:42 | 176 | 2 | 4 | 0 |
| edit_guard:unsupported_character:43 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:44 | 180 | 2 | 4 | 0 |
| edit_guard:unsupported_character:45 | 188 | 3 | 4 | 0 |
| edit_guard:unsupported_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_character:49 | 50 | 1 | 1 | 0 |
| edit_guard:unsupported_character:5 | 142 | 2 | 3 | 0 |
| edit_guard:unsupported_character:6 | 168 | 2 | 4 | 0 |
| edit_guard:unsupported_character:7 | 417 | 3 | 11 | 0 |
| edit_guard:unsupported_character:8 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:9 | 265 | 3 | 6 | 0 |
| edit_guard:unsupported_raw_character:0 | 1567 | 2 | 41 | 0 |
| edit_guard:unsupported_raw_character:1 | 521 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:10 | 206 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:11 | 221 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:12 | 139 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 254 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:14 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:15 | 64 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:17 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:18 | 179 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:19 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:2 | 546 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:20 | 277 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:21 | 135 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:22 | 200 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:23 | 142 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:24 | 210 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:25 | 163 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:26 | 121 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 291 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:28 | 75 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 191 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:3 | 559 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:30 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 157 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:32 | 88 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 112 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:34 | 254 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:35 | 80 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 183 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 132 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 227 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 349 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:40 | 222 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:41 | 393 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:42 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:43 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_raw_character:44 | 180 | 1 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 188 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:49 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 142 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:6 | 168 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 393 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:8 | 94 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:9 | 265 | 0 | 6 | 0 |
| mark_kind_disagreement | 111173 | 0 | 21977 | 159 |
| r1_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_missing | 1452 | 0 | 955 | 0 |
| r1_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4765 |
| A/B disagreement | 0 |
| kind disagreement | 21977 |
| R1 uncertainty | 1829 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 4161 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 2749 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 2237 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1432 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1308 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 1263 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 984 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 822 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 650 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 495 |

### round1 / anemi_round1

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 0 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 11 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 3 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 2 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 596 |
| detector_clipped_top | 140308 | 0 | 29544 | 2188 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 127 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 41 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 33 |
| edit_guard:punctuation_mismatch | 9153 | 6398 | 6398 | 207 |
| edit_guard:unsupported_character:0 | 3286 | 23 | 79 | 0 |
| edit_guard:unsupported_character:1 | 2211 | 16 | 47 | 0 |
| edit_guard:unsupported_character:10 | 439 | 5 | 12 | 0 |
| edit_guard:unsupported_character:11 | 317 | 3 | 9 | 0 |
| edit_guard:unsupported_character:12 | 144 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 283 | 6 | 9 | 0 |
| edit_guard:unsupported_character:14 | 407 | 9 | 13 | 0 |
| edit_guard:unsupported_character:15 | 470 | 7 | 14 | 0 |
| edit_guard:unsupported_character:16 | 268 | 3 | 7 | 0 |
| edit_guard:unsupported_character:17 | 383 | 4 | 9 | 0 |
| edit_guard:unsupported_character:18 | 295 | 3 | 8 | 0 |
| edit_guard:unsupported_character:19 | 337 | 3 | 10 | 0 |
| edit_guard:unsupported_character:2 | 409 | 4 | 11 | 0 |
| edit_guard:unsupported_character:20 | 535 | 6 | 13 | 0 |
| edit_guard:unsupported_character:21 | 407 | 4 | 12 | 0 |
| edit_guard:unsupported_character:22 | 427 | 8 | 11 | 0 |
| edit_guard:unsupported_character:23 | 668 | 7 | 19 | 0 |
| edit_guard:unsupported_character:24 | 469 | 7 | 11 | 0 |
| edit_guard:unsupported_character:25 | 228 | 3 | 7 | 0 |
| edit_guard:unsupported_character:26 | 599 | 6 | 15 | 0 |
| edit_guard:unsupported_character:27 | 636 | 6 | 17 | 0 |
| edit_guard:unsupported_character:28 | 581 | 6 | 17 | 0 |
| edit_guard:unsupported_character:29 | 1243 | 12 | 33 | 0 |
| edit_guard:unsupported_character:3 | 622 | 2 | 15 | 0 |
| edit_guard:unsupported_character:30 | 652 | 5 | 18 | 0 |
| edit_guard:unsupported_character:31 | 551 | 3 | 15 | 0 |
| edit_guard:unsupported_character:32 | 684 | 4 | 18 | 0 |
| edit_guard:unsupported_character:33 | 538 | 5 | 13 | 0 |
| edit_guard:unsupported_character:34 | 781 | 4 | 18 | 0 |
| edit_guard:unsupported_character:35 | 701 | 6 | 17 | 0 |
| edit_guard:unsupported_character:36 | 745 | 2 | 19 | 0 |
| edit_guard:unsupported_character:37 | 765 | 5 | 19 | 0 |
| edit_guard:unsupported_character:38 | 408 | 1 | 10 | 0 |
| edit_guard:unsupported_character:39 | 791 | 6 | 18 | 0 |
| edit_guard:unsupported_character:4 | 497 | 4 | 11 | 0 |
| edit_guard:unsupported_character:40 | 448 | 3 | 10 | 0 |
| edit_guard:unsupported_character:41 | 811 | 5 | 18 | 0 |
| edit_guard:unsupported_character:42 | 454 | 4 | 10 | 0 |
| edit_guard:unsupported_character:43 | 569 | 6 | 12 | 0 |
| edit_guard:unsupported_character:44 | 300 | 3 | 6 | 0 |
| edit_guard:unsupported_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_character:46 | 262 | 1 | 5 | 0 |
| edit_guard:unsupported_character:47 | 207 | 4 | 4 | 0 |
| edit_guard:unsupported_character:48 | 251 | 2 | 5 | 0 |
| edit_guard:unsupported_character:49 | 315 | 1 | 6 | 0 |
| edit_guard:unsupported_character:5 | 299 | 2 | 7 | 0 |
| edit_guard:unsupported_character:50 | 284 | 3 | 5 | 0 |
| edit_guard:unsupported_character:51 | 495 | 3 | 9 | 0 |
| edit_guard:unsupported_character:52 | 175 | 1 | 3 | 0 |
| edit_guard:unsupported_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_character:54 | 202 | 2 | 3 | 0 |
| edit_guard:unsupported_character:55 | 247 | 2 | 4 | 0 |
| edit_guard:unsupported_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_character:57 | 202 | 1 | 3 | 0 |
| edit_guard:unsupported_character:58 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:59 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 421 | 2 | 12 | 0 |
| edit_guard:unsupported_character:60 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_character:62 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:65 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 431 | 3 | 9 | 0 |
| edit_guard:unsupported_character:74 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:8 | 618 | 4 | 15 | 0 |
| edit_guard:unsupported_character:9 | 433 | 4 | 11 | 0 |
| edit_guard:unsupported_raw_character:0 | 3282 | 1 | 78 | 0 |
| edit_guard:unsupported_raw_character:1 | 1715 | 0 | 40 | 0 |
| edit_guard:unsupported_raw_character:10 | 439 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:11 | 339 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:12 | 144 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:13 | 283 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:14 | 424 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:15 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:16 | 302 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:17 | 383 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:18 | 317 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:19 | 379 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:2 | 409 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:20 | 535 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:21 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:22 | 427 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:23 | 668 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:24 | 469 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:25 | 228 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:26 | 599 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:27 | 636 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:28 | 581 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:29 | 1243 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:3 | 644 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:30 | 652 | 1 | 19 | 0 |
| edit_guard:unsupported_raw_character:31 | 551 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:32 | 718 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:33 | 543 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:34 | 742 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:35 | 701 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:36 | 745 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:37 | 806 | 0 | 20 | 0 |
| edit_guard:unsupported_raw_character:38 | 402 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:39 | 831 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:4 | 497 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:40 | 448 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:41 | 811 | 0 | 18 | 0 |
| edit_guard:unsupported_raw_character:42 | 454 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:43 | 569 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:44 | 300 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:46 | 262 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:47 | 207 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:48 | 251 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:49 | 315 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:5 | 270 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 233 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 436 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:52 | 175 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:54 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:55 | 247 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:57 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:58 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:59 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 421 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:60 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:62 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:65 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 471 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:74 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 545 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:9 | 433 | 0 | 11 | 0 |
| mark_kind_disagreement | 73450 | 0 | 30611 | 2924 |
| r1_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_missing | 1687 | 0 | 1129 | 0 |
| r1_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9251 |
| A/B disagreement | 0 |
| kind disagreement | 30611 |
| R1 uncertainty | 1276 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 4389 |
| ["detector_clipped_bottom","detector_clipped_top"] | 3171 |
| ["mark_kind_disagreement"] | 2924 |
| ["detector_clipped_top","mark_kind_disagreement"] | 2456 |
| ["detector_clipped_top"] | 2188 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1925 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 1367 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1223 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1141 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 1052 |

### round2 / anemi_round2

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 84 | 0 | 81 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 107 | 0 | 103 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 6 | 0 | 3 | 0 |
| K1:C3:two_accents:rule_held_back | 1020 | 0 | 467 | 4 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 101 | 0 | 98 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 1 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 216 |
| detector_clipped_top | 48664 | 0 | 10763 | 911 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 49 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 22 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 18 |
| edit_guard:punctuation_mismatch | 1491 | 2095 | 2095 | 113 |
| edit_guard:unsupported_character:0 | 1107 | 12 | 28 | 0 |
| edit_guard:unsupported_character:1 | 360 | 2 | 9 | 0 |
| edit_guard:unsupported_character:10 | 169 | 1 | 4 | 0 |
| edit_guard:unsupported_character:11 | 54 | 1 | 1 | 0 |
| edit_guard:unsupported_character:12 | 178 | 3 | 5 | 0 |
| edit_guard:unsupported_character:13 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_character:14 | 169 | 2 | 4 | 0 |
| edit_guard:unsupported_character:15 | 122 | 3 | 3 | 0 |
| edit_guard:unsupported_character:16 | 225 | 1 | 8 | 0 |
| edit_guard:unsupported_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_character:18 | 252 | 3 | 7 | 0 |
| edit_guard:unsupported_character:19 | 108 | 1 | 3 | 0 |
| edit_guard:unsupported_character:2 | 238 | 4 | 6 | 0 |
| edit_guard:unsupported_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_character:21 | 129 | 1 | 4 | 0 |
| edit_guard:unsupported_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_character:23 | 43 | 1 | 1 | 0 |
| edit_guard:unsupported_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_character:27 | 150 | 3 | 4 | 0 |
| edit_guard:unsupported_character:28 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 71 | 0 | 2 | 0 |
| edit_guard:unsupported_character:3 | 236 | 3 | 6 | 0 |
| edit_guard:unsupported_character:30 | 225 | 3 | 6 | 0 |
| edit_guard:unsupported_character:31 | 201 | 3 | 5 | 0 |
| edit_guard:unsupported_character:32 | 79 | 1 | 2 | 0 |
| edit_guard:unsupported_character:33 | 250 | 2 | 6 | 0 |
| edit_guard:unsupported_character:34 | 116 | 1 | 3 | 0 |
| edit_guard:unsupported_character:35 | 152 | 1 | 4 | 0 |
| edit_guard:unsupported_character:36 | 212 | 2 | 5 | 0 |
| edit_guard:unsupported_character:37 | 356 | 5 | 8 | 0 |
| edit_guard:unsupported_character:38 | 192 | 4 | 4 | 0 |
| edit_guard:unsupported_character:39 | 98 | 2 | 2 | 0 |
| edit_guard:unsupported_character:4 | 63 | 1 | 2 | 0 |
| edit_guard:unsupported_character:40 | 87 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 241 | 2 | 5 | 0 |
| edit_guard:unsupported_character:43 | 92 | 1 | 2 | 0 |
| edit_guard:unsupported_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_character:45 | 51 | 1 | 1 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_character:5 | 121 | 3 | 3 | 0 |
| edit_guard:unsupported_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_character:53 | 113 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_character:59 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 165 | 4 | 5 | 0 |
| edit_guard:unsupported_character:60 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 173 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 145 | 1 | 4 | 0 |
| edit_guard:unsupported_character:9 | 114 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:0 | 1012 | 0 | 26 | 0 |
| edit_guard:unsupported_raw_character:1 | 341 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 54 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 178 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:13 | 96 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:14 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 122 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:16 | 225 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 252 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:19 | 108 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:2 | 238 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:21 | 98 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:23 | 43 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:28 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 41 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 236 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:30 | 193 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:31 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:32 | 79 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 250 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:34 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:35 | 152 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:36 | 212 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 356 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:38 | 192 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:4 | 79 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 241 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 92 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 148 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 113 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:59 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 165 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:60 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 148 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:8 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:9 | 114 | 0 | 4 | 0 |
| mark_kind_disagreement | 27905 | 0 | 11778 | 1590 |
| r1_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_missing | 434 | 0 | 268 | 0 |
| r1_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3059 |
| A/B disagreement | 0 |
| kind disagreement | 11778 |
| R1 uncertainty | 354 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 1794 |
| ["mark_kind_disagreement"] | 1590 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1212 |
| ["detector_clipped_top","mark_kind_disagreement"] | 1078 |
| ["detector_clipped_top"] | 911 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 559 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 483 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 457 |
| ["detector_segmentation_uncertain","mark_kind_disagreement"] | 343 |
| ["detector_unnamed_mark","mark_kind_disagreement"] | 323 |

### vouli / vouli_parliament_1850s

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 86 | 0 | 83 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 130 | 0 | 120 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 3 | 0 | 3 | 0 |
| K1:C3:two_accents:evidence_tie | 18 | 0 | 9 | 0 |
| K1:C3:two_accents:rule_held_back | 1597 | 0 | 641 | 2 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 200 | 0 | 181 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 12 | 0 | 10 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 281 | 0 | 258 | 0 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 2 | 0 | 2 | 0 |
| detector_clipped_bottom | 40732 | 0 | 15658 | 260 |
| detector_clipped_top | 93007 | 0 | 19927 | 882 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 36 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 28 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 9 |
| edit_guard:punctuation_mismatch | 3437 | 2268 | 2268 | 36 |
| edit_guard:unsupported_character:0 | 1166 | 8 | 25 | 0 |
| edit_guard:unsupported_character:1 | 510 | 3 | 12 | 0 |
| edit_guard:unsupported_character:10 | 146 | 2 | 4 | 0 |
| edit_guard:unsupported_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_character:15 | 112 | 2 | 3 | 0 |
| edit_guard:unsupported_character:17 | 256 | 4 | 7 | 0 |
| edit_guard:unsupported_character:18 | 156 | 1 | 3 | 0 |
| edit_guard:unsupported_character:19 | 309 | 3 | 8 | 0 |
| edit_guard:unsupported_character:2 | 313 | 1 | 8 | 0 |
| edit_guard:unsupported_character:20 | 40 | 1 | 1 | 0 |
| edit_guard:unsupported_character:21 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:22 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:23 | 72 | 1 | 2 | 0 |
| edit_guard:unsupported_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_character:25 | 91 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 171 | 2 | 4 | 0 |
| edit_guard:unsupported_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_character:28 | 222 | 4 | 5 | 0 |
| edit_guard:unsupported_character:29 | 169 | 3 | 3 | 0 |
| edit_guard:unsupported_character:3 | 657 | 1 | 18 | 0 |
| edit_guard:unsupported_character:30 | 78 | 1 | 2 | 0 |
| edit_guard:unsupported_character:31 | 313 | 2 | 7 | 0 |
| edit_guard:unsupported_character:32 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:33 | 145 | 0 | 3 | 0 |
| edit_guard:unsupported_character:34 | 213 | 2 | 5 | 0 |
| edit_guard:unsupported_character:35 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:36 | 215 | 3 | 5 | 0 |
| edit_guard:unsupported_character:37 | 138 | 1 | 3 | 0 |
| edit_guard:unsupported_character:38 | 94 | 1 | 2 | 0 |
| edit_guard:unsupported_character:39 | 240 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 225 | 3 | 7 | 0 |
| edit_guard:unsupported_character:40 | 426 | 2 | 9 | 0 |
| edit_guard:unsupported_character:41 | 240 | 2 | 5 | 0 |
| edit_guard:unsupported_character:42 | 327 | 3 | 7 | 0 |
| edit_guard:unsupported_character:43 | 412 | 4 | 8 | 0 |
| edit_guard:unsupported_character:44 | 47 | 1 | 1 | 0 |
| edit_guard:unsupported_character:45 | 189 | 1 | 3 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:48 | 100 | 2 | 2 | 0 |
| edit_guard:unsupported_character:49 | 203 | 2 | 4 | 0 |
| edit_guard:unsupported_character:5 | 345 | 2 | 6 | 0 |
| edit_guard:unsupported_character:50 | 109 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_character:6 | 251 | 1 | 6 | 0 |
| edit_guard:unsupported_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_character:7 | 350 | 4 | 7 | 0 |
| edit_guard:unsupported_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_character:76 | 163 | 0 | 2 | 0 |
| edit_guard:unsupported_character:8 | 176 | 1 | 4 | 0 |
| edit_guard:unsupported_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_character:9 | 296 | 6 | 7 | 0 |
| edit_guard:unsupported_raw_character:0 | 1166 | 3 | 28 | 0 |
| edit_guard:unsupported_raw_character:1 | 541 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:10 | 146 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:15 | 112 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:17 | 256 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:18 | 156 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:19 | 286 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:2 | 266 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:20 | 40 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:21 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:23 | 72 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:25 | 131 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 346 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:29 | 169 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:3 | 621 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:30 | 78 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 313 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:32 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 103 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:34 | 213 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:35 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:36 | 215 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 138 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:39 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 225 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:40 | 374 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:41 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:42 | 376 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:43 | 412 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:44 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 189 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:48 | 100 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:49 | 203 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:5 | 345 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 109 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:6 | 251 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 350 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:76 | 80 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:9 | 402 | 0 | 9 | 0 |
| mark_kind_disagreement | 59419 | 0 | 17856 | 294 |
| r1_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_missing | 757 | 0 | 390 | 0 |
| r1_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3544 |
| A/B disagreement | 0 |
| kind disagreement | 17856 |
| R1 uncertainty | 744 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 2615 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 2561 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1449 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1405 |
| ["detector_clipped_top","mark_kind_disagreement"] | 1057 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 969 |
| ["detector_clipped_top"] | 882 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 847 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 765 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 681 |
## FULL

| Wave | Source | Lines | HOLD | Held glyph slots |
|---|---|---:|---:|---:|
| ALL | ALL | 124669 | 118820 | 1077475 |
| mixed | ALL | 13227 | 12464 | 94919 |
| openarchives | ALL | 235 | 207 | 1157 |
| parliament | ALL | 27224 | 27088 | 357776 |
| round1 | ALL | 43869 | 40865 | 311370 |
| round2 | ALL | 17026 | 15514 | 107122 |
| vouli | ALL | 23088 | 22682 | 205131 |
| ALL | anemi_mixed | 13084 | 12341 | 94019 |
| ALL | anemi_round1 | 43869 | 40865 | 311370 |
| ALL | anemi_round2 | 17026 | 15514 | 107122 |
| ALL | archive_b28038630 | 97 | 78 | 423 |
| ALL | openarchives_Pandemos | 185 | 170 | 1065 |
| ALL | openarchives_kallipos | 50 | 37 | 92 |
| ALL | openarchives_mixed_Pandemos | 13 | 12 | 75 |
| ALL | openarchives_mixed_apothesis | 1 | 1 | 1 |
| ALL | openarchives_mixed_ktisis | 2 | 2 | 2 |
| ALL | openarchives_mixed_ntua | 30 | 30 | 399 |
| ALL | parliament_proceedings_1975_2000 | 27224 | 27088 | 357776 |
| ALL | vouli_parliament_1850s | 23088 | 22682 | 205131 |
| mixed | anemi_mixed | 13084 | 12341 | 94019 |
| mixed | archive_b28038630 | 97 | 78 | 423 |
| mixed | openarchives_mixed_Pandemos | 13 | 12 | 75 |
| mixed | openarchives_mixed_apothesis | 1 | 1 | 1 |
| mixed | openarchives_mixed_ktisis | 2 | 2 | 2 |
| mixed | openarchives_mixed_ntua | 30 | 30 | 399 |
| openarchives | openarchives_Pandemos | 185 | 170 | 1065 |
| openarchives | openarchives_kallipos | 50 | 37 | 92 |
| parliament | parliament_proceedings_1975_2000 | 27224 | 27088 | 357776 |
| round1 | anemi_round1 | 43869 | 40865 | 311370 |
| round2 | anemi_round2 | 17026 | 15514 | 107122 |
| vouli | vouli_parliament_1850s | 23088 | 22682 | 205131 |

### ALL / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 543 | 0 | 525 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 770 | 0 | 741 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 6 | 0 | 6 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 6 | 0 | 6 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 18 | 0 | 18 | 0 |
| K1:C3:two_accents:evidence_tie | 58 | 0 | 29 | 0 |
| K1:C3:two_accents:rule_held_back | 8094 | 0 | 3535 | 17 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 956 | 0 | 917 | 2 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 48 | 0 | 46 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1782 | 0 | 1627 | 6 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 3 | 0 | 3 | 0 |
| detector_clipped_bottom | 176335 | 0 | 68784 | 1234 |
| detector_clipped_top | 420955 | 0 | 89886 | 4594 |
| detector_localisation_unknown | 151696 | 0 | 46253 | 0 |
| detector_segmentation_uncertain | 254880 | 0 | 60333 | 265 |
| detector_unnamed_mark | 40015 | 0 | 26798 | 94 |
| edit_guard:base_or_character_mismatch | 4440 | 13689 | 13689 | 61 |
| edit_guard:punctuation_mismatch | 16841 | 15070 | 15070 | 391 |
| edit_guard:unsupported_character:0 | 7792 | 66 | 189 | 0 |
| edit_guard:unsupported_character:1 | 4010 | 28 | 93 | 0 |
| edit_guard:unsupported_character:10 | 1272 | 16 | 34 | 0 |
| edit_guard:unsupported_character:11 | 665 | 9 | 17 | 0 |
| edit_guard:unsupported_character:12 | 601 | 8 | 15 | 0 |
| edit_guard:unsupported_character:13 | 917 | 14 | 28 | 0 |
| edit_guard:unsupported_character:14 | 1018 | 15 | 28 | 0 |
| edit_guard:unsupported_character:15 | 864 | 16 | 24 | 0 |
| edit_guard:unsupported_character:16 | 685 | 7 | 20 | 0 |
| edit_guard:unsupported_character:17 | 785 | 10 | 20 | 0 |
| edit_guard:unsupported_character:18 | 933 | 10 | 23 | 0 |
| edit_guard:unsupported_character:19 | 930 | 10 | 25 | 0 |
| edit_guard:unsupported_character:2 | 1700 | 13 | 46 | 0 |
| edit_guard:unsupported_character:20 | 1105 | 13 | 28 | 0 |
| edit_guard:unsupported_character:21 | 854 | 10 | 24 | 0 |
| edit_guard:unsupported_character:22 | 844 | 14 | 22 | 0 |
| edit_guard:unsupported_character:23 | 1021 | 11 | 28 | 0 |
| edit_guard:unsupported_character:24 | 830 | 10 | 21 | 0 |
| edit_guard:unsupported_character:25 | 689 | 6 | 19 | 0 |
| edit_guard:unsupported_character:26 | 1089 | 10 | 28 | 0 |
| edit_guard:unsupported_character:27 | 1334 | 18 | 34 | 0 |
| edit_guard:unsupported_character:28 | 1287 | 14 | 34 | 0 |
| edit_guard:unsupported_character:29 | 1711 | 18 | 43 | 0 |
| edit_guard:unsupported_character:3 | 2344 | 14 | 61 | 0 |
| edit_guard:unsupported_character:30 | 1154 | 13 | 31 | 0 |
| edit_guard:unsupported_character:31 | 1482 | 14 | 37 | 0 |
| edit_guard:unsupported_character:32 | 1122 | 10 | 29 | 0 |
| edit_guard:unsupported_character:33 | 1159 | 9 | 28 | 0 |
| edit_guard:unsupported_character:34 | 1438 | 10 | 34 | 0 |
| edit_guard:unsupported_character:35 | 1137 | 10 | 28 | 0 |
| edit_guard:unsupported_character:36 | 1520 | 10 | 37 | 0 |
| edit_guard:unsupported_character:37 | 1698 | 16 | 40 | 0 |
| edit_guard:unsupported_character:38 | 1008 | 9 | 23 | 0 |
| edit_guard:unsupported_character:39 | 1490 | 16 | 33 | 0 |
| edit_guard:unsupported_character:4 | 1264 | 13 | 32 | 0 |
| edit_guard:unsupported_character:40 | 1397 | 10 | 31 | 0 |
| edit_guard:unsupported_character:41 | 1588 | 16 | 35 | 0 |
| edit_guard:unsupported_character:42 | 1431 | 14 | 31 | 0 |
| edit_guard:unsupported_character:43 | 1353 | 15 | 28 | 0 |
| edit_guard:unsupported_character:44 | 825 | 9 | 17 | 0 |
| edit_guard:unsupported_character:45 | 811 | 5 | 16 | 0 |
| edit_guard:unsupported_character:46 | 759 | 4 | 15 | 0 |
| edit_guard:unsupported_character:47 | 562 | 6 | 11 | 0 |
| edit_guard:unsupported_character:48 | 503 | 6 | 10 | 0 |
| edit_guard:unsupported_character:49 | 568 | 4 | 11 | 0 |
| edit_guard:unsupported_character:5 | 953 | 9 | 20 | 0 |
| edit_guard:unsupported_character:50 | 450 | 4 | 8 | 0 |
| edit_guard:unsupported_character:51 | 547 | 3 | 10 | 0 |
| edit_guard:unsupported_character:52 | 281 | 2 | 5 | 0 |
| edit_guard:unsupported_character:53 | 402 | 1 | 7 | 0 |
| edit_guard:unsupported_character:54 | 370 | 2 | 6 | 0 |
| edit_guard:unsupported_character:55 | 471 | 2 | 7 | 0 |
| edit_guard:unsupported_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_character:57 | 202 | 1 | 3 | 0 |
| edit_guard:unsupported_character:58 | 186 | 1 | 3 | 0 |
| edit_guard:unsupported_character:59 | 125 | 2 | 2 | 0 |
| edit_guard:unsupported_character:6 | 1058 | 10 | 28 | 0 |
| edit_guard:unsupported_character:60 | 254 | 2 | 4 | 0 |
| edit_guard:unsupported_character:61 | 187 | 0 | 3 | 0 |
| edit_guard:unsupported_character:62 | 133 | 1 | 2 | 0 |
| edit_guard:unsupported_character:65 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_character:7 | 1516 | 18 | 35 | 0 |
| edit_guard:unsupported_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_character:74 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:76 | 163 | 0 | 2 | 0 |
| edit_guard:unsupported_character:8 | 1285 | 11 | 31 | 0 |
| edit_guard:unsupported_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_character:9 | 1108 | 14 | 28 | 0 |
| edit_guard:unsupported_raw_character:0 | 7590 | 6 | 187 | 0 |
| edit_guard:unsupported_raw_character:1 | 3453 | 0 | 84 | 0 |
| edit_guard:unsupported_raw_character:10 | 1272 | 0 | 34 | 0 |
| edit_guard:unsupported_raw_character:11 | 687 | 0 | 18 | 0 |
| edit_guard:unsupported_raw_character:12 | 601 | 1 | 16 | 0 |
| edit_guard:unsupported_raw_character:13 | 917 | 0 | 28 | 0 |
| edit_guard:unsupported_raw_character:14 | 1084 | 0 | 30 | 0 |
| edit_guard:unsupported_raw_character:15 | 798 | 0 | 22 | 0 |
| edit_guard:unsupported_raw_character:16 | 719 | 0 | 22 | 0 |
| edit_guard:unsupported_raw_character:17 | 785 | 0 | 20 | 0 |
| edit_guard:unsupported_raw_character:18 | 955 | 0 | 24 | 0 |
| edit_guard:unsupported_raw_character:19 | 916 | 0 | 25 | 0 |
| edit_guard:unsupported_raw_character:2 | 1634 | 0 | 44 | 0 |
| edit_guard:unsupported_raw_character:20 | 1105 | 0 | 28 | 0 |
| edit_guard:unsupported_raw_character:21 | 820 | 0 | 23 | 0 |
| edit_guard:unsupported_raw_character:22 | 844 | 0 | 22 | 0 |
| edit_guard:unsupported_raw_character:23 | 1069 | 0 | 30 | 0 |
| edit_guard:unsupported_raw_character:24 | 782 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:25 | 678 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:26 | 1116 | 0 | 29 | 0 |
| edit_guard:unsupported_raw_character:27 | 1303 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:28 | 1411 | 0 | 36 | 0 |
| edit_guard:unsupported_raw_character:29 | 1742 | 1 | 45 | 0 |
| edit_guard:unsupported_raw_character:3 | 2330 | 0 | 61 | 0 |
| edit_guard:unsupported_raw_character:30 | 1155 | 1 | 32 | 0 |
| edit_guard:unsupported_raw_character:31 | 1482 | 0 | 37 | 0 |
| edit_guard:unsupported_raw_character:32 | 1198 | 0 | 31 | 0 |
| edit_guard:unsupported_raw_character:33 | 1122 | 1 | 28 | 0 |
| edit_guard:unsupported_raw_character:34 | 1399 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:35 | 1137 | 0 | 28 | 0 |
| edit_guard:unsupported_raw_character:36 | 1520 | 0 | 37 | 0 |
| edit_guard:unsupported_raw_character:37 | 1739 | 0 | 41 | 0 |
| edit_guard:unsupported_raw_character:38 | 990 | 1 | 24 | 0 |
| edit_guard:unsupported_raw_character:39 | 1530 | 0 | 34 | 0 |
| edit_guard:unsupported_raw_character:4 | 1280 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:40 | 1388 | 0 | 31 | 0 |
| edit_guard:unsupported_raw_character:41 | 1545 | 0 | 34 | 0 |
| edit_guard:unsupported_raw_character:42 | 1480 | 1 | 33 | 0 |
| edit_guard:unsupported_raw_character:43 | 1353 | 1 | 29 | 0 |
| edit_guard:unsupported_raw_character:44 | 825 | 1 | 18 | 0 |
| edit_guard:unsupported_raw_character:45 | 811 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:46 | 759 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:47 | 562 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:48 | 503 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:49 | 568 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:5 | 951 | 0 | 20 | 0 |
| edit_guard:unsupported_raw_character:50 | 399 | 1 | 8 | 0 |
| edit_guard:unsupported_raw_character:51 | 488 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:52 | 281 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:53 | 402 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:54 | 370 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:55 | 471 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:57 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:58 | 186 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:59 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:6 | 1058 | 0 | 28 | 0 |
| edit_guard:unsupported_raw_character:60 | 254 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:61 | 187 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:62 | 133 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:65 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 1507 | 0 | 34 | 0 |
| edit_guard:unsupported_raw_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:74 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:76 | 80 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 1187 | 0 | 28 | 0 |
| edit_guard:unsupported_raw_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:9 | 1214 | 0 | 30 | 0 |
| mark_set_disagreement | 315973 | 0 | 94675 | 6332 |
| r1_evidence_UNKNOWN | 1567 | 0 | 1567 | 0 |
| r1_missing | 4770 | 0 | 2991 | 0 |
| r1_uncertainty:out_of_image_span | 1567 | 0 | 1567 | 0 |
| r1_unscored:line_confidence_below_0.5 | 149 | 0 | 9 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 1735 | 0 | 941 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 2886 | 0 | 2129 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 71761 |
| clipping | 99259 |
| K1 | 5313 |
| edit-guard | 22877 |
| A/B disagreement | 0 |
| kind disagreement | 94675 |
| R1 uncertainty | 4502 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 11276 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 8746 |
| ["detector_clipped_bottom","detector_clipped_top"] | 6630 |
| ["mark_set_disagreement"] | 6332 |
| ["detector_clipped_top","mark_set_disagreement"] | 6081 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 5435 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 4779 |
| ["detector_clipped_top"] | 4594 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 4260 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 3741 |

### mixed / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 48 | 0 | 47 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 103 | 0 | 100 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 2 | 0 | 2 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:evidence_tie | 4 | 0 | 2 | 0 |
| K1:C3:two_accents:rule_held_back | 874 | 0 | 382 | 2 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 124 | 0 | 122 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 219 | 0 | 206 | 3 |
| detector_clipped_bottom | 15216 | 0 | 6417 | 149 |
| detector_clipped_top | 39943 | 0 | 8844 | 624 |
| detector_localisation_unknown | 8743 | 0 | 3355 | 0 |
| detector_segmentation_uncertain | 17178 | 0 | 5101 | 24 |
| detector_unnamed_mark | 2410 | 0 | 1955 | 7 |
| edit_guard:base_or_character_mismatch | 389 | 1293 | 1293 | 4 |
| edit_guard:punctuation_mismatch | 1288 | 1509 | 1509 | 49 |
| edit_guard:unsupported_character:0 | 570 | 6 | 14 | 0 |
| edit_guard:unsupported_character:1 | 335 | 3 | 8 | 0 |
| edit_guard:unsupported_character:10 | 312 | 5 | 8 | 0 |
| edit_guard:unsupported_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 49 | 1 | 1 | 0 |
| edit_guard:unsupported_character:13 | 211 | 3 | 5 | 0 |
| edit_guard:unsupported_character:14 | 107 | 3 | 3 | 0 |
| edit_guard:unsupported_character:15 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:16 | 192 | 3 | 5 | 0 |
| edit_guard:unsupported_character:17 | 27 | 1 | 1 | 0 |
| edit_guard:unsupported_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:19 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_character:20 | 113 | 2 | 3 | 0 |
| edit_guard:unsupported_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_character:22 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_character:25 | 97 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 104 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 209 | 3 | 5 | 0 |
| edit_guard:unsupported_character:28 | 323 | 2 | 8 | 0 |
| edit_guard:unsupported_character:29 | 68 | 1 | 1 | 0 |
| edit_guard:unsupported_character:3 | 270 | 3 | 7 | 0 |
| edit_guard:unsupported_character:30 | 158 | 3 | 4 | 0 |
| edit_guard:unsupported_character:31 | 260 | 2 | 6 | 0 |
| edit_guard:unsupported_character:32 | 155 | 1 | 4 | 0 |
| edit_guard:unsupported_character:33 | 114 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_character:36 | 165 | 1 | 4 | 0 |
| edit_guard:unsupported_character:37 | 307 | 3 | 7 | 0 |
| edit_guard:unsupported_character:38 | 130 | 1 | 3 | 0 |
| edit_guard:unsupported_character:39 | 134 | 2 | 3 | 0 |
| edit_guard:unsupported_character:4 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_character:41 | 101 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 233 | 3 | 5 | 0 |
| edit_guard:unsupported_character:43 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:44 | 253 | 3 | 5 | 0 |
| edit_guard:unsupported_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_character:46 | 144 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 159 | 1 | 3 | 0 |
| edit_guard:unsupported_character:48 | 102 | 2 | 2 | 0 |
| edit_guard:unsupported_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_character:50 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:6 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 145 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 227 | 4 | 5 | 0 |
| edit_guard:unsupported_raw_character:0 | 563 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:1 | 335 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 312 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:13 | 211 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:14 | 156 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:16 | 192 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:17 | 27 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:19 | 97 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:20 | 113 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:25 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:26 | 131 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 209 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:28 | 323 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:29 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 270 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:30 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:31 | 260 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:32 | 155 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 114 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 165 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 307 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:38 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:4 | 130 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:41 | 101 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 233 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:44 | 253 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:46 | 144 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 159 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:48 | 102 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:50 | 57 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:8 | 227 | 0 | 5 | 0 |
| mark_set_disagreement | 28258 | 0 | 9933 | 1034 |
| r1_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_missing | 440 | 0 | 249 | 0 |
| r1_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 151 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 269 | 0 | 201 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6062 |
| clipping | 9669 |
| K1 | 616 |
| edit-guard | 2239 |
| A/B disagreement | 0 |
| kind disagreement | 9933 |
| R1 uncertainty | 299 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 1523 |
| ["mark_set_disagreement"] | 1034 |
| ["detector_clipped_top","mark_set_disagreement"] | 897 |
| ["detector_clipped_bottom","detector_clipped_top"] | 884 |
| ["detector_clipped_top"] | 624 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 559 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 523 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 478 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 398 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 326 |

### openarchives / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 12 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_bottom | 366 | 0 | 118 | 19 |
| detector_clipped_top | 629 | 0 | 120 | 20 |
| detector_segmentation_uncertain | 110 | 0 | 38 | 0 |
| detector_unnamed_mark | 24 | 0 | 19 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 19 | 19 | 3 |
| mark_set_disagreement | 256 | 0 | 122 | 25 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 50 |
| clipping | 159 |
| K1 | 5 |
| edit-guard | 19 |
| A/B disagreement | 0 |
| kind disagreement | 122 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 39 |
| ["mark_set_disagreement"] | 25 |
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 22 |
| ["detector_clipped_top"] | 20 |
| ["detector_clipped_bottom"] | 19 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","mark_set_disagreement"] | 9 |
| ["detector_segmentation_uncertain","mark_set_disagreement"] | 9 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 8 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 7 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 7 |

### parliament / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 69 | 0 | 67 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 90 | 0 | 88 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C3:two_accents:evidence_tie | 14 | 0 | 7 | 0 |
| K1:C3:two_accents:rule_held_back | 1343 | 0 | 613 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 159 | 0 | 155 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 7 | 0 | 7 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 292 | 0 | 253 | 0 |
| detector_clipped_bottom | 44633 | 0 | 16119 | 74 |
| detector_clipped_top | 98404 | 0 | 20688 | 221 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 48 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 8 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 2 |
| edit_guard:punctuation_mismatch | 1472 | 2781 | 2781 | 7 |
| edit_guard:unsupported_character:0 | 1663 | 17 | 43 | 0 |
| edit_guard:unsupported_character:1 | 594 | 4 | 17 | 0 |
| edit_guard:unsupported_character:10 | 206 | 3 | 6 | 0 |
| edit_guard:unsupported_character:11 | 221 | 5 | 5 | 0 |
| edit_guard:unsupported_character:12 | 139 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 254 | 4 | 7 | 0 |
| edit_guard:unsupported_character:14 | 201 | 1 | 5 | 0 |
| edit_guard:unsupported_character:15 | 64 | 2 | 2 | 0 |
| edit_guard:unsupported_character:17 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:18 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:19 | 46 | 1 | 1 | 0 |
| edit_guard:unsupported_character:2 | 565 | 4 | 17 | 0 |
| edit_guard:unsupported_character:20 | 277 | 4 | 7 | 0 |
| edit_guard:unsupported_character:21 | 135 | 4 | 4 | 0 |
| edit_guard:unsupported_character:22 | 200 | 3 | 5 | 0 |
| edit_guard:unsupported_character:23 | 94 | 2 | 2 | 0 |
| edit_guard:unsupported_character:24 | 258 | 3 | 7 | 0 |
| edit_guard:unsupported_character:25 | 163 | 1 | 5 | 0 |
| edit_guard:unsupported_character:26 | 121 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 291 | 6 | 7 | 0 |
| edit_guard:unsupported_character:28 | 75 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 160 | 2 | 4 | 0 |
| edit_guard:unsupported_character:3 | 559 | 5 | 15 | 0 |
| edit_guard:unsupported_character:30 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:31 | 157 | 4 | 4 | 0 |
| edit_guard:unsupported_character:32 | 88 | 2 | 2 | 0 |
| edit_guard:unsupported_character:33 | 112 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 254 | 3 | 6 | 0 |
| edit_guard:unsupported_character:35 | 80 | 2 | 2 | 0 |
| edit_guard:unsupported_character:36 | 183 | 2 | 4 | 0 |
| edit_guard:unsupported_character:37 | 132 | 2 | 3 | 0 |
| edit_guard:unsupported_character:38 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:39 | 227 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 349 | 3 | 9 | 0 |
| edit_guard:unsupported_character:40 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:41 | 436 | 7 | 10 | 0 |
| edit_guard:unsupported_character:42 | 176 | 2 | 4 | 0 |
| edit_guard:unsupported_character:43 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:44 | 180 | 2 | 4 | 0 |
| edit_guard:unsupported_character:45 | 188 | 3 | 4 | 0 |
| edit_guard:unsupported_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_character:49 | 50 | 1 | 1 | 0 |
| edit_guard:unsupported_character:5 | 142 | 2 | 3 | 0 |
| edit_guard:unsupported_character:6 | 168 | 2 | 4 | 0 |
| edit_guard:unsupported_character:7 | 417 | 3 | 11 | 0 |
| edit_guard:unsupported_character:8 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:9 | 265 | 3 | 6 | 0 |
| edit_guard:unsupported_raw_character:0 | 1567 | 2 | 41 | 0 |
| edit_guard:unsupported_raw_character:1 | 521 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:10 | 206 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:11 | 221 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:12 | 139 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 254 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:14 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:15 | 64 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:17 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:18 | 179 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:19 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:2 | 546 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:20 | 277 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:21 | 135 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:22 | 200 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:23 | 142 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:24 | 210 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:25 | 163 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:26 | 121 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 291 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:28 | 75 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 191 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:3 | 559 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:30 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 157 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:32 | 88 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 112 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:34 | 254 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:35 | 80 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 183 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 132 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 227 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 349 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:40 | 222 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:41 | 393 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:42 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:43 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_raw_character:44 | 180 | 1 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 188 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:49 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 142 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:6 | 168 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 393 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:8 | 94 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:9 | 265 | 0 | 6 | 0 |
| mark_set_disagreement | 116911 | 0 | 22520 | 163 |
| r1_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_missing | 1452 | 0 | 955 | 0 |
| r1_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4765 |
| A/B disagreement | 0 |
| kind disagreement | 22520 |
| R1 uncertainty | 1829 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 4277 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 2820 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 2266 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1467 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 1281 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1192 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1016 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 751 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 656 |
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 515 |

### round1 / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 0 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 10 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 2 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 2 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 553 |
| detector_clipped_top | 140308 | 0 | 29544 | 2030 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 116 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 36 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 31 |
| edit_guard:punctuation_mismatch | 9153 | 6398 | 6398 | 193 |
| edit_guard:unsupported_character:0 | 3286 | 23 | 79 | 0 |
| edit_guard:unsupported_character:1 | 2211 | 16 | 47 | 0 |
| edit_guard:unsupported_character:10 | 439 | 5 | 12 | 0 |
| edit_guard:unsupported_character:11 | 317 | 3 | 9 | 0 |
| edit_guard:unsupported_character:12 | 144 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 283 | 6 | 9 | 0 |
| edit_guard:unsupported_character:14 | 407 | 9 | 13 | 0 |
| edit_guard:unsupported_character:15 | 470 | 7 | 14 | 0 |
| edit_guard:unsupported_character:16 | 268 | 3 | 7 | 0 |
| edit_guard:unsupported_character:17 | 383 | 4 | 9 | 0 |
| edit_guard:unsupported_character:18 | 295 | 3 | 8 | 0 |
| edit_guard:unsupported_character:19 | 337 | 3 | 10 | 0 |
| edit_guard:unsupported_character:2 | 409 | 4 | 11 | 0 |
| edit_guard:unsupported_character:20 | 535 | 6 | 13 | 0 |
| edit_guard:unsupported_character:21 | 407 | 4 | 12 | 0 |
| edit_guard:unsupported_character:22 | 427 | 8 | 11 | 0 |
| edit_guard:unsupported_character:23 | 668 | 7 | 19 | 0 |
| edit_guard:unsupported_character:24 | 469 | 7 | 11 | 0 |
| edit_guard:unsupported_character:25 | 228 | 3 | 7 | 0 |
| edit_guard:unsupported_character:26 | 599 | 6 | 15 | 0 |
| edit_guard:unsupported_character:27 | 636 | 6 | 17 | 0 |
| edit_guard:unsupported_character:28 | 581 | 6 | 17 | 0 |
| edit_guard:unsupported_character:29 | 1243 | 12 | 33 | 0 |
| edit_guard:unsupported_character:3 | 622 | 2 | 15 | 0 |
| edit_guard:unsupported_character:30 | 652 | 5 | 18 | 0 |
| edit_guard:unsupported_character:31 | 551 | 3 | 15 | 0 |
| edit_guard:unsupported_character:32 | 684 | 4 | 18 | 0 |
| edit_guard:unsupported_character:33 | 538 | 5 | 13 | 0 |
| edit_guard:unsupported_character:34 | 781 | 4 | 18 | 0 |
| edit_guard:unsupported_character:35 | 701 | 6 | 17 | 0 |
| edit_guard:unsupported_character:36 | 745 | 2 | 19 | 0 |
| edit_guard:unsupported_character:37 | 765 | 5 | 19 | 0 |
| edit_guard:unsupported_character:38 | 408 | 1 | 10 | 0 |
| edit_guard:unsupported_character:39 | 791 | 6 | 18 | 0 |
| edit_guard:unsupported_character:4 | 497 | 4 | 11 | 0 |
| edit_guard:unsupported_character:40 | 448 | 3 | 10 | 0 |
| edit_guard:unsupported_character:41 | 811 | 5 | 18 | 0 |
| edit_guard:unsupported_character:42 | 454 | 4 | 10 | 0 |
| edit_guard:unsupported_character:43 | 569 | 6 | 12 | 0 |
| edit_guard:unsupported_character:44 | 300 | 3 | 6 | 0 |
| edit_guard:unsupported_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_character:46 | 262 | 1 | 5 | 0 |
| edit_guard:unsupported_character:47 | 207 | 4 | 4 | 0 |
| edit_guard:unsupported_character:48 | 251 | 2 | 5 | 0 |
| edit_guard:unsupported_character:49 | 315 | 1 | 6 | 0 |
| edit_guard:unsupported_character:5 | 299 | 2 | 7 | 0 |
| edit_guard:unsupported_character:50 | 284 | 3 | 5 | 0 |
| edit_guard:unsupported_character:51 | 495 | 3 | 9 | 0 |
| edit_guard:unsupported_character:52 | 175 | 1 | 3 | 0 |
| edit_guard:unsupported_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_character:54 | 202 | 2 | 3 | 0 |
| edit_guard:unsupported_character:55 | 247 | 2 | 4 | 0 |
| edit_guard:unsupported_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_character:57 | 202 | 1 | 3 | 0 |
| edit_guard:unsupported_character:58 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:59 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 421 | 2 | 12 | 0 |
| edit_guard:unsupported_character:60 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_character:62 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:65 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 431 | 3 | 9 | 0 |
| edit_guard:unsupported_character:74 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:8 | 618 | 4 | 15 | 0 |
| edit_guard:unsupported_character:9 | 433 | 4 | 11 | 0 |
| edit_guard:unsupported_raw_character:0 | 3282 | 1 | 78 | 0 |
| edit_guard:unsupported_raw_character:1 | 1715 | 0 | 40 | 0 |
| edit_guard:unsupported_raw_character:10 | 439 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:11 | 339 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:12 | 144 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:13 | 283 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:14 | 424 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:15 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:16 | 302 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:17 | 383 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:18 | 317 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:19 | 379 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:2 | 409 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:20 | 535 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:21 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:22 | 427 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:23 | 668 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:24 | 469 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:25 | 228 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:26 | 599 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:27 | 636 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:28 | 581 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:29 | 1243 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:3 | 644 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:30 | 652 | 1 | 19 | 0 |
| edit_guard:unsupported_raw_character:31 | 551 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:32 | 718 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:33 | 543 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:34 | 742 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:35 | 701 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:36 | 745 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:37 | 806 | 0 | 20 | 0 |
| edit_guard:unsupported_raw_character:38 | 402 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:39 | 831 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:4 | 497 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:40 | 448 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:41 | 811 | 0 | 18 | 0 |
| edit_guard:unsupported_raw_character:42 | 454 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:43 | 569 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:44 | 300 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:46 | 262 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:47 | 207 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:48 | 251 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:49 | 315 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:5 | 270 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 233 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 436 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:52 | 175 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:54 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:55 | 247 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:57 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:58 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:59 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 421 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:60 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:62 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:65 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 471 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:74 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 545 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:9 | 433 | 0 | 11 | 0 |
| mark_set_disagreement | 78967 | 0 | 31761 | 3116 |
| r1_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_missing | 1687 | 0 | 1129 | 0 |
| r1_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9251 |
| A/B disagreement | 0 |
| kind disagreement | 31761 |
| R1 uncertainty | 1276 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 4677 |
| ["mark_set_disagreement"] | 3116 |
| ["detector_clipped_bottom","detector_clipped_top"] | 2883 |
| ["detector_clipped_top","mark_set_disagreement"] | 2614 |
| ["detector_clipped_top"] | 2030 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1976 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 1388 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1257 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1176 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 1072 |

### round2 / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 84 | 0 | 81 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 107 | 0 | 103 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 6 | 0 | 3 | 0 |
| K1:C3:two_accents:rule_held_back | 1020 | 0 | 467 | 3 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 101 | 0 | 98 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 1 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 194 |
| detector_clipped_top | 48664 | 0 | 10763 | 853 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 44 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 19 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 16 |
| edit_guard:punctuation_mismatch | 1491 | 2095 | 2095 | 103 |
| edit_guard:unsupported_character:0 | 1107 | 12 | 28 | 0 |
| edit_guard:unsupported_character:1 | 360 | 2 | 9 | 0 |
| edit_guard:unsupported_character:10 | 169 | 1 | 4 | 0 |
| edit_guard:unsupported_character:11 | 54 | 1 | 1 | 0 |
| edit_guard:unsupported_character:12 | 178 | 3 | 5 | 0 |
| edit_guard:unsupported_character:13 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_character:14 | 169 | 2 | 4 | 0 |
| edit_guard:unsupported_character:15 | 122 | 3 | 3 | 0 |
| edit_guard:unsupported_character:16 | 225 | 1 | 8 | 0 |
| edit_guard:unsupported_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_character:18 | 252 | 3 | 7 | 0 |
| edit_guard:unsupported_character:19 | 108 | 1 | 3 | 0 |
| edit_guard:unsupported_character:2 | 238 | 4 | 6 | 0 |
| edit_guard:unsupported_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_character:21 | 129 | 1 | 4 | 0 |
| edit_guard:unsupported_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_character:23 | 43 | 1 | 1 | 0 |
| edit_guard:unsupported_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_character:27 | 150 | 3 | 4 | 0 |
| edit_guard:unsupported_character:28 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 71 | 0 | 2 | 0 |
| edit_guard:unsupported_character:3 | 236 | 3 | 6 | 0 |
| edit_guard:unsupported_character:30 | 225 | 3 | 6 | 0 |
| edit_guard:unsupported_character:31 | 201 | 3 | 5 | 0 |
| edit_guard:unsupported_character:32 | 79 | 1 | 2 | 0 |
| edit_guard:unsupported_character:33 | 250 | 2 | 6 | 0 |
| edit_guard:unsupported_character:34 | 116 | 1 | 3 | 0 |
| edit_guard:unsupported_character:35 | 152 | 1 | 4 | 0 |
| edit_guard:unsupported_character:36 | 212 | 2 | 5 | 0 |
| edit_guard:unsupported_character:37 | 356 | 5 | 8 | 0 |
| edit_guard:unsupported_character:38 | 192 | 4 | 4 | 0 |
| edit_guard:unsupported_character:39 | 98 | 2 | 2 | 0 |
| edit_guard:unsupported_character:4 | 63 | 1 | 2 | 0 |
| edit_guard:unsupported_character:40 | 87 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 241 | 2 | 5 | 0 |
| edit_guard:unsupported_character:43 | 92 | 1 | 2 | 0 |
| edit_guard:unsupported_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_character:45 | 51 | 1 | 1 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_character:5 | 121 | 3 | 3 | 0 |
| edit_guard:unsupported_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_character:53 | 113 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_character:59 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 165 | 4 | 5 | 0 |
| edit_guard:unsupported_character:60 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 173 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 145 | 1 | 4 | 0 |
| edit_guard:unsupported_character:9 | 114 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:0 | 1012 | 0 | 26 | 0 |
| edit_guard:unsupported_raw_character:1 | 341 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 54 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 178 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:13 | 96 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:14 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 122 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:16 | 225 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 252 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:19 | 108 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:2 | 238 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:21 | 98 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:23 | 43 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:28 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 41 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 236 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:30 | 193 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:31 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:32 | 79 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 250 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:34 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:35 | 152 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:36 | 212 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 356 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:38 | 192 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:4 | 79 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 241 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 92 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 148 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 113 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:59 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 165 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:60 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 148 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:8 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:9 | 114 | 0 | 4 | 0 |
| mark_set_disagreement | 29904 | 0 | 12180 | 1681 |
| r1_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_missing | 434 | 0 | 268 | 0 |
| r1_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3059 |
| A/B disagreement | 0 |
| kind disagreement | 12180 |
| R1 uncertainty | 354 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 1899 |
| ["mark_set_disagreement"] | 1681 |
| ["detector_clipped_top","mark_set_disagreement"] | 1136 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1107 |
| ["detector_clipped_top"] | 853 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 565 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 501 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 458 |
| ["detector_segmentation_uncertain","mark_set_disagreement"] | 348 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 333 |

### vouli / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 86 | 0 | 83 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 130 | 0 | 120 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 3 | 0 | 3 | 0 |
| K1:C3:two_accents:evidence_tie | 18 | 0 | 9 | 0 |
| K1:C3:two_accents:rule_held_back | 1597 | 0 | 641 | 2 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 200 | 0 | 181 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 12 | 0 | 10 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 281 | 0 | 258 | 0 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 2 | 0 | 2 | 0 |
| detector_clipped_bottom | 40732 | 0 | 15658 | 245 |
| detector_clipped_top | 93007 | 0 | 19927 | 846 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 33 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 24 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 8 |
| edit_guard:punctuation_mismatch | 3437 | 2268 | 2268 | 36 |
| edit_guard:unsupported_character:0 | 1166 | 8 | 25 | 0 |
| edit_guard:unsupported_character:1 | 510 | 3 | 12 | 0 |
| edit_guard:unsupported_character:10 | 146 | 2 | 4 | 0 |
| edit_guard:unsupported_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_character:15 | 112 | 2 | 3 | 0 |
| edit_guard:unsupported_character:17 | 256 | 4 | 7 | 0 |
| edit_guard:unsupported_character:18 | 156 | 1 | 3 | 0 |
| edit_guard:unsupported_character:19 | 309 | 3 | 8 | 0 |
| edit_guard:unsupported_character:2 | 313 | 1 | 8 | 0 |
| edit_guard:unsupported_character:20 | 40 | 1 | 1 | 0 |
| edit_guard:unsupported_character:21 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:22 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:23 | 72 | 1 | 2 | 0 |
| edit_guard:unsupported_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_character:25 | 91 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 171 | 2 | 4 | 0 |
| edit_guard:unsupported_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_character:28 | 222 | 4 | 5 | 0 |
| edit_guard:unsupported_character:29 | 169 | 3 | 3 | 0 |
| edit_guard:unsupported_character:3 | 657 | 1 | 18 | 0 |
| edit_guard:unsupported_character:30 | 78 | 1 | 2 | 0 |
| edit_guard:unsupported_character:31 | 313 | 2 | 7 | 0 |
| edit_guard:unsupported_character:32 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:33 | 145 | 0 | 3 | 0 |
| edit_guard:unsupported_character:34 | 213 | 2 | 5 | 0 |
| edit_guard:unsupported_character:35 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:36 | 215 | 3 | 5 | 0 |
| edit_guard:unsupported_character:37 | 138 | 1 | 3 | 0 |
| edit_guard:unsupported_character:38 | 94 | 1 | 2 | 0 |
| edit_guard:unsupported_character:39 | 240 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 225 | 3 | 7 | 0 |
| edit_guard:unsupported_character:40 | 426 | 2 | 9 | 0 |
| edit_guard:unsupported_character:41 | 240 | 2 | 5 | 0 |
| edit_guard:unsupported_character:42 | 327 | 3 | 7 | 0 |
| edit_guard:unsupported_character:43 | 412 | 4 | 8 | 0 |
| edit_guard:unsupported_character:44 | 47 | 1 | 1 | 0 |
| edit_guard:unsupported_character:45 | 189 | 1 | 3 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:48 | 100 | 2 | 2 | 0 |
| edit_guard:unsupported_character:49 | 203 | 2 | 4 | 0 |
| edit_guard:unsupported_character:5 | 345 | 2 | 6 | 0 |
| edit_guard:unsupported_character:50 | 109 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_character:6 | 251 | 1 | 6 | 0 |
| edit_guard:unsupported_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_character:7 | 350 | 4 | 7 | 0 |
| edit_guard:unsupported_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_character:76 | 163 | 0 | 2 | 0 |
| edit_guard:unsupported_character:8 | 176 | 1 | 4 | 0 |
| edit_guard:unsupported_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_character:9 | 296 | 6 | 7 | 0 |
| edit_guard:unsupported_raw_character:0 | 1166 | 3 | 28 | 0 |
| edit_guard:unsupported_raw_character:1 | 541 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:10 | 146 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:15 | 112 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:17 | 256 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:18 | 156 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:19 | 286 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:2 | 266 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:20 | 40 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:21 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:23 | 72 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:25 | 131 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 346 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:29 | 169 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:3 | 621 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:30 | 78 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 313 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:32 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 103 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:34 | 213 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:35 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:36 | 215 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 138 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:39 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 225 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:40 | 374 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:41 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:42 | 376 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:43 | 412 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:44 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 189 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:48 | 100 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:49 | 203 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:5 | 345 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 109 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:6 | 251 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 350 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:76 | 80 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:9 | 402 | 0 | 9 | 0 |
| mark_set_disagreement | 61677 | 0 | 18159 | 313 |
| r1_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_missing | 757 | 0 | 390 | 0 |
| r1_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3544 |
| A/B disagreement | 0 |
| kind disagreement | 18159 |
| R1 uncertainty | 744 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 2640 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 2628 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1433 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1370 |
| ["detector_clipped_top","mark_set_disagreement"] | 1093 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 972 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 856 |
| ["detector_clipped_top"] | 846 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 781 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 683 |

### ALL / anemi_mixed

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 48 | 0 | 47 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 102 | 0 | 99 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 2 | 0 | 2 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:evidence_tie | 4 | 0 | 2 | 0 |
| K1:C3:two_accents:rule_held_back | 868 | 0 | 379 | 2 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 123 | 0 | 121 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 214 | 0 | 201 | 3 |
| detector_clipped_bottom | 15059 | 0 | 6360 | 148 |
| detector_clipped_top | 39633 | 0 | 8777 | 620 |
| detector_localisation_unknown | 8716 | 0 | 3345 | 0 |
| detector_segmentation_uncertain | 17133 | 0 | 5085 | 24 |
| detector_unnamed_mark | 2392 | 0 | 1939 | 6 |
| edit_guard:base_or_character_mismatch | 389 | 1258 | 1258 | 4 |
| edit_guard:punctuation_mismatch | 1184 | 1470 | 1470 | 45 |
| edit_guard:unsupported_character:0 | 570 | 6 | 14 | 0 |
| edit_guard:unsupported_character:1 | 335 | 3 | 8 | 0 |
| edit_guard:unsupported_character:10 | 312 | 5 | 8 | 0 |
| edit_guard:unsupported_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 49 | 1 | 1 | 0 |
| edit_guard:unsupported_character:13 | 211 | 3 | 5 | 0 |
| edit_guard:unsupported_character:14 | 107 | 3 | 3 | 0 |
| edit_guard:unsupported_character:15 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:16 | 192 | 3 | 5 | 0 |
| edit_guard:unsupported_character:17 | 27 | 1 | 1 | 0 |
| edit_guard:unsupported_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:19 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_character:20 | 113 | 2 | 3 | 0 |
| edit_guard:unsupported_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_character:22 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_character:25 | 97 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 104 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 209 | 3 | 5 | 0 |
| edit_guard:unsupported_character:28 | 288 | 2 | 7 | 0 |
| edit_guard:unsupported_character:29 | 68 | 1 | 1 | 0 |
| edit_guard:unsupported_character:3 | 270 | 3 | 7 | 0 |
| edit_guard:unsupported_character:30 | 158 | 3 | 4 | 0 |
| edit_guard:unsupported_character:31 | 260 | 2 | 6 | 0 |
| edit_guard:unsupported_character:32 | 155 | 1 | 4 | 0 |
| edit_guard:unsupported_character:33 | 114 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_character:36 | 165 | 1 | 4 | 0 |
| edit_guard:unsupported_character:37 | 307 | 3 | 7 | 0 |
| edit_guard:unsupported_character:38 | 130 | 1 | 3 | 0 |
| edit_guard:unsupported_character:39 | 134 | 2 | 3 | 0 |
| edit_guard:unsupported_character:4 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_character:41 | 101 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 233 | 3 | 5 | 0 |
| edit_guard:unsupported_character:43 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:44 | 253 | 3 | 5 | 0 |
| edit_guard:unsupported_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_character:46 | 144 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 102 | 1 | 2 | 0 |
| edit_guard:unsupported_character:48 | 102 | 2 | 2 | 0 |
| edit_guard:unsupported_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_character:50 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_character:6 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 145 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 227 | 4 | 5 | 0 |
| edit_guard:unsupported_raw_character:0 | 563 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:1 | 335 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 312 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:13 | 211 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:14 | 156 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:16 | 192 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:17 | 27 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:19 | 97 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:20 | 113 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:25 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:26 | 131 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 209 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:28 | 288 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:29 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 270 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:30 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:31 | 260 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:32 | 155 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 114 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 165 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 307 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:38 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:4 | 130 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:41 | 101 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 233 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:44 | 253 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:46 | 144 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 102 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:48 | 102 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:50 | 57 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:8 | 227 | 0 | 5 | 0 |
| mark_set_disagreement | 27999 | 0 | 9837 | 1021 |
| r1_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_missing | 418 | 0 | 244 | 0 |
| r1_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 132 | 0 | 51 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 266 | 0 | 200 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6032 |
| clipping | 9594 |
| K1 | 609 |
| edit-guard | 2191 |
| A/B disagreement | 0 |
| kind disagreement | 9837 |
| R1 uncertainty | 294 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 1504 |
| ["mark_set_disagreement"] | 1021 |
| ["detector_clipped_top","mark_set_disagreement"] | 889 |
| ["detector_clipped_bottom","detector_clipped_top"] | 874 |
| ["detector_clipped_top"] | 620 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 559 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 522 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 476 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 398 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 324 |

### ALL / anemi_round1

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 0 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 10 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 2 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 2 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 553 |
| detector_clipped_top | 140308 | 0 | 29544 | 2030 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 116 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 36 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 31 |
| edit_guard:punctuation_mismatch | 9153 | 6398 | 6398 | 193 |
| edit_guard:unsupported_character:0 | 3286 | 23 | 79 | 0 |
| edit_guard:unsupported_character:1 | 2211 | 16 | 47 | 0 |
| edit_guard:unsupported_character:10 | 439 | 5 | 12 | 0 |
| edit_guard:unsupported_character:11 | 317 | 3 | 9 | 0 |
| edit_guard:unsupported_character:12 | 144 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 283 | 6 | 9 | 0 |
| edit_guard:unsupported_character:14 | 407 | 9 | 13 | 0 |
| edit_guard:unsupported_character:15 | 470 | 7 | 14 | 0 |
| edit_guard:unsupported_character:16 | 268 | 3 | 7 | 0 |
| edit_guard:unsupported_character:17 | 383 | 4 | 9 | 0 |
| edit_guard:unsupported_character:18 | 295 | 3 | 8 | 0 |
| edit_guard:unsupported_character:19 | 337 | 3 | 10 | 0 |
| edit_guard:unsupported_character:2 | 409 | 4 | 11 | 0 |
| edit_guard:unsupported_character:20 | 535 | 6 | 13 | 0 |
| edit_guard:unsupported_character:21 | 407 | 4 | 12 | 0 |
| edit_guard:unsupported_character:22 | 427 | 8 | 11 | 0 |
| edit_guard:unsupported_character:23 | 668 | 7 | 19 | 0 |
| edit_guard:unsupported_character:24 | 469 | 7 | 11 | 0 |
| edit_guard:unsupported_character:25 | 228 | 3 | 7 | 0 |
| edit_guard:unsupported_character:26 | 599 | 6 | 15 | 0 |
| edit_guard:unsupported_character:27 | 636 | 6 | 17 | 0 |
| edit_guard:unsupported_character:28 | 581 | 6 | 17 | 0 |
| edit_guard:unsupported_character:29 | 1243 | 12 | 33 | 0 |
| edit_guard:unsupported_character:3 | 622 | 2 | 15 | 0 |
| edit_guard:unsupported_character:30 | 652 | 5 | 18 | 0 |
| edit_guard:unsupported_character:31 | 551 | 3 | 15 | 0 |
| edit_guard:unsupported_character:32 | 684 | 4 | 18 | 0 |
| edit_guard:unsupported_character:33 | 538 | 5 | 13 | 0 |
| edit_guard:unsupported_character:34 | 781 | 4 | 18 | 0 |
| edit_guard:unsupported_character:35 | 701 | 6 | 17 | 0 |
| edit_guard:unsupported_character:36 | 745 | 2 | 19 | 0 |
| edit_guard:unsupported_character:37 | 765 | 5 | 19 | 0 |
| edit_guard:unsupported_character:38 | 408 | 1 | 10 | 0 |
| edit_guard:unsupported_character:39 | 791 | 6 | 18 | 0 |
| edit_guard:unsupported_character:4 | 497 | 4 | 11 | 0 |
| edit_guard:unsupported_character:40 | 448 | 3 | 10 | 0 |
| edit_guard:unsupported_character:41 | 811 | 5 | 18 | 0 |
| edit_guard:unsupported_character:42 | 454 | 4 | 10 | 0 |
| edit_guard:unsupported_character:43 | 569 | 6 | 12 | 0 |
| edit_guard:unsupported_character:44 | 300 | 3 | 6 | 0 |
| edit_guard:unsupported_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_character:46 | 262 | 1 | 5 | 0 |
| edit_guard:unsupported_character:47 | 207 | 4 | 4 | 0 |
| edit_guard:unsupported_character:48 | 251 | 2 | 5 | 0 |
| edit_guard:unsupported_character:49 | 315 | 1 | 6 | 0 |
| edit_guard:unsupported_character:5 | 299 | 2 | 7 | 0 |
| edit_guard:unsupported_character:50 | 284 | 3 | 5 | 0 |
| edit_guard:unsupported_character:51 | 495 | 3 | 9 | 0 |
| edit_guard:unsupported_character:52 | 175 | 1 | 3 | 0 |
| edit_guard:unsupported_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_character:54 | 202 | 2 | 3 | 0 |
| edit_guard:unsupported_character:55 | 247 | 2 | 4 | 0 |
| edit_guard:unsupported_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_character:57 | 202 | 1 | 3 | 0 |
| edit_guard:unsupported_character:58 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:59 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 421 | 2 | 12 | 0 |
| edit_guard:unsupported_character:60 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_character:62 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:65 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 431 | 3 | 9 | 0 |
| edit_guard:unsupported_character:74 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:8 | 618 | 4 | 15 | 0 |
| edit_guard:unsupported_character:9 | 433 | 4 | 11 | 0 |
| edit_guard:unsupported_raw_character:0 | 3282 | 1 | 78 | 0 |
| edit_guard:unsupported_raw_character:1 | 1715 | 0 | 40 | 0 |
| edit_guard:unsupported_raw_character:10 | 439 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:11 | 339 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:12 | 144 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:13 | 283 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:14 | 424 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:15 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:16 | 302 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:17 | 383 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:18 | 317 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:19 | 379 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:2 | 409 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:20 | 535 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:21 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:22 | 427 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:23 | 668 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:24 | 469 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:25 | 228 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:26 | 599 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:27 | 636 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:28 | 581 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:29 | 1243 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:3 | 644 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:30 | 652 | 1 | 19 | 0 |
| edit_guard:unsupported_raw_character:31 | 551 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:32 | 718 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:33 | 543 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:34 | 742 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:35 | 701 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:36 | 745 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:37 | 806 | 0 | 20 | 0 |
| edit_guard:unsupported_raw_character:38 | 402 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:39 | 831 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:4 | 497 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:40 | 448 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:41 | 811 | 0 | 18 | 0 |
| edit_guard:unsupported_raw_character:42 | 454 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:43 | 569 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:44 | 300 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:46 | 262 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:47 | 207 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:48 | 251 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:49 | 315 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:5 | 270 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 233 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 436 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:52 | 175 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:54 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:55 | 247 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:57 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:58 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:59 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 421 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:60 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:62 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:65 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 471 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:74 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 545 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:9 | 433 | 0 | 11 | 0 |
| mark_set_disagreement | 78967 | 0 | 31761 | 3116 |
| r1_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_missing | 1687 | 0 | 1129 | 0 |
| r1_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9251 |
| A/B disagreement | 0 |
| kind disagreement | 31761 |
| R1 uncertainty | 1276 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 4677 |
| ["mark_set_disagreement"] | 3116 |
| ["detector_clipped_bottom","detector_clipped_top"] | 2883 |
| ["detector_clipped_top","mark_set_disagreement"] | 2614 |
| ["detector_clipped_top"] | 2030 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1976 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 1388 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1257 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1176 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 1072 |

### ALL / anemi_round2

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 84 | 0 | 81 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 107 | 0 | 103 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 6 | 0 | 3 | 0 |
| K1:C3:two_accents:rule_held_back | 1020 | 0 | 467 | 3 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 101 | 0 | 98 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 1 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 194 |
| detector_clipped_top | 48664 | 0 | 10763 | 853 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 44 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 19 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 16 |
| edit_guard:punctuation_mismatch | 1491 | 2095 | 2095 | 103 |
| edit_guard:unsupported_character:0 | 1107 | 12 | 28 | 0 |
| edit_guard:unsupported_character:1 | 360 | 2 | 9 | 0 |
| edit_guard:unsupported_character:10 | 169 | 1 | 4 | 0 |
| edit_guard:unsupported_character:11 | 54 | 1 | 1 | 0 |
| edit_guard:unsupported_character:12 | 178 | 3 | 5 | 0 |
| edit_guard:unsupported_character:13 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_character:14 | 169 | 2 | 4 | 0 |
| edit_guard:unsupported_character:15 | 122 | 3 | 3 | 0 |
| edit_guard:unsupported_character:16 | 225 | 1 | 8 | 0 |
| edit_guard:unsupported_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_character:18 | 252 | 3 | 7 | 0 |
| edit_guard:unsupported_character:19 | 108 | 1 | 3 | 0 |
| edit_guard:unsupported_character:2 | 238 | 4 | 6 | 0 |
| edit_guard:unsupported_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_character:21 | 129 | 1 | 4 | 0 |
| edit_guard:unsupported_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_character:23 | 43 | 1 | 1 | 0 |
| edit_guard:unsupported_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_character:27 | 150 | 3 | 4 | 0 |
| edit_guard:unsupported_character:28 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 71 | 0 | 2 | 0 |
| edit_guard:unsupported_character:3 | 236 | 3 | 6 | 0 |
| edit_guard:unsupported_character:30 | 225 | 3 | 6 | 0 |
| edit_guard:unsupported_character:31 | 201 | 3 | 5 | 0 |
| edit_guard:unsupported_character:32 | 79 | 1 | 2 | 0 |
| edit_guard:unsupported_character:33 | 250 | 2 | 6 | 0 |
| edit_guard:unsupported_character:34 | 116 | 1 | 3 | 0 |
| edit_guard:unsupported_character:35 | 152 | 1 | 4 | 0 |
| edit_guard:unsupported_character:36 | 212 | 2 | 5 | 0 |
| edit_guard:unsupported_character:37 | 356 | 5 | 8 | 0 |
| edit_guard:unsupported_character:38 | 192 | 4 | 4 | 0 |
| edit_guard:unsupported_character:39 | 98 | 2 | 2 | 0 |
| edit_guard:unsupported_character:4 | 63 | 1 | 2 | 0 |
| edit_guard:unsupported_character:40 | 87 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 241 | 2 | 5 | 0 |
| edit_guard:unsupported_character:43 | 92 | 1 | 2 | 0 |
| edit_guard:unsupported_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_character:45 | 51 | 1 | 1 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_character:5 | 121 | 3 | 3 | 0 |
| edit_guard:unsupported_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_character:53 | 113 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_character:59 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 165 | 4 | 5 | 0 |
| edit_guard:unsupported_character:60 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 173 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 145 | 1 | 4 | 0 |
| edit_guard:unsupported_character:9 | 114 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:0 | 1012 | 0 | 26 | 0 |
| edit_guard:unsupported_raw_character:1 | 341 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 54 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 178 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:13 | 96 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:14 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 122 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:16 | 225 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 252 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:19 | 108 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:2 | 238 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:21 | 98 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:23 | 43 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:28 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 41 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 236 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:30 | 193 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:31 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:32 | 79 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 250 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:34 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:35 | 152 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:36 | 212 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 356 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:38 | 192 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:4 | 79 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 241 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 92 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 148 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 113 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:59 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 165 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:60 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 148 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:8 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:9 | 114 | 0 | 4 | 0 |
| mark_set_disagreement | 29904 | 0 | 12180 | 1681 |
| r1_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_missing | 434 | 0 | 268 | 0 |
| r1_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3059 |
| A/B disagreement | 0 |
| kind disagreement | 12180 |
| R1 uncertainty | 354 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 1899 |
| ["mark_set_disagreement"] | 1681 |
| ["detector_clipped_top","mark_set_disagreement"] | 1136 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1107 |
| ["detector_clipped_top"] | 853 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 565 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 501 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 458 |
| ["detector_segmentation_uncertain","mark_set_disagreement"] | 348 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 333 |

### ALL / archive_b28038630

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 2 | 0 | 1 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 130 | 0 | 45 | 1 |
| detector_clipped_top | 254 | 0 | 58 | 4 |
| detector_localisation_unknown | 7 | 0 | 6 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 13 | 13 | 0 |
| edit_guard:punctuation_mismatch | 0 | 22 | 22 | 4 |
| mark_set_disagreement | 92 | 0 | 54 | 4 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 13 |
| clipping | 61 |
| K1 | 3 |
| edit-guard | 24 |
| A/B disagreement | 0 |
| kind disagreement | 54 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 17 |
| ["detector_clipped_bottom","detector_clipped_top"] | 8 |
| ["detector_clipped_top","mark_set_disagreement"] | 7 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 6 |
| ["detector_clipped_top"] | 4 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 4 |
| ["edit_guard:punctuation_mismatch"] | 4 |
| ["mark_set_disagreement"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 2 |

### ALL / openarchives_Pandemos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_clipped_bottom | 366 | 0 | 118 | 19 |
| detector_clipped_top | 604 | 0 | 118 | 20 |
| detector_segmentation_uncertain | 100 | 0 | 35 | 0 |
| detector_unnamed_mark | 23 | 0 | 18 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 9 | 9 | 0 |
| mark_set_disagreement | 197 | 0 | 88 | 5 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 46 |
| clipping | 157 |
| K1 | 0 |
| edit-guard | 9 |
| A/B disagreement | 0 |
| kind disagreement | 88 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 39 |
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 22 |
| ["detector_clipped_top"] | 20 |
| ["detector_clipped_bottom"] | 19 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","mark_set_disagreement"] | 9 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 8 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 7 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 7 |
| ["detector_segmentation_uncertain","mark_set_disagreement"] | 6 |
| ["detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 5 |

### ALL / openarchives_kallipos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 12 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_top | 25 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 10 | 0 | 3 | 0 |
| detector_unnamed_mark | 1 | 0 | 1 | 0 |
| edit_guard:punctuation_mismatch | 0 | 10 | 10 | 3 |
| mark_set_disagreement | 59 | 0 | 34 | 20 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 2 |
| K1 | 5 |
| edit-guard | 10 |
| A/B disagreement | 0 |
| kind disagreement | 34 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_set_disagreement"] | 20 |
| ["edit_guard:punctuation_mismatch","mark_set_disagreement"] | 4 |
| ["detector_segmentation_uncertain","mark_set_disagreement"] | 3 |
| ["edit_guard:punctuation_mismatch"] | 3 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","mark_set_disagreement"] | 2 |
| ["detector_clipped_top","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 2 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_unnamed_mark","mark_set_disagreement"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 1 |
| ["K1:C3:two_accents:rule_held_back","mark_set_disagreement"] | 1 |

### ALL / openarchives_mixed_Pandemos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_clipped_bottom | 16 | 0 | 7 | 0 |
| detector_clipped_top | 27 | 0 | 4 | 0 |
| detector_localisation_unknown | 5 | 0 | 1 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 2 | 0 |
| detector_unnamed_mark | 3 | 0 | 3 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 1 | 1 | 0 |
| edit_guard:punctuation_mismatch | 0 | 1 | 1 | 0 |
| mark_set_disagreement | 25 | 0 | 10 | 2 |
| r1_missing | 1 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 7 |
| K1 | 0 |
| edit-guard | 2 |
| A/B disagreement | 0 |
| kind disagreement | 10 |
| R1 uncertainty | 1 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top"] | 2 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 2 |
| ["mark_set_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 1 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","mark_set_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |
| ["detector_unnamed_mark","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 1 |
| ["detector_unnamed_mark","mark_set_disagreement"] | 1 |

### ALL / openarchives_mixed_apothesis

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| mark_set_disagreement | 1 | 0 | 1 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 0 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 1 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_set_disagreement"] | 1 |

### ALL / openarchives_mixed_ktisis

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_unnamed_mark | 1 | 0 | 1 | 1 |
| mark_set_disagreement | 1 | 0 | 1 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 1 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 1 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_unnamed_mark"] | 1 |
| ["mark_set_disagreement"] | 1 |

### ALL / openarchives_mixed_ntua

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_not_initial:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:rule_held_back | 4 | 0 | 2 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_bottom | 11 | 0 | 5 | 0 |
| detector_clipped_top | 29 | 0 | 5 | 0 |
| detector_localisation_unknown | 15 | 0 | 3 | 0 |
| detector_segmentation_uncertain | 27 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 21 | 21 | 0 |
| edit_guard:punctuation_mismatch | 104 | 16 | 16 | 0 |
| edit_guard:unsupported_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| mark_set_disagreement | 140 | 0 | 30 | 5 |
| r1_missing | 21 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 18 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 3 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 12 |
| clipping | 7 |
| K1 | 4 |
| edit-guard | 22 |
| A/B disagreement | 0 |
| kind disagreement | 30 |
| R1 uncertainty | 4 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 7 |
| ["mark_set_disagreement"] | 5 |
| ["edit_guard:base_or_character_mismatch","mark_set_disagreement"] | 2 |
| ["K1:C1:breathing_not_initial:impossible_by_rule","K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","edit_guard:unsupported_character:28","edit_guard:unsupported_raw_character:28","mark_set_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","r1_unscored:width_outside_0.2_2.0_median_ctc"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","mark_set_disagreement"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","mark_set_disagreement"] | 1 |
| ["detector_clipped_bottom","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |

### ALL / parliament_proceedings_1975_2000

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 69 | 0 | 67 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 90 | 0 | 88 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C3:two_accents:evidence_tie | 14 | 0 | 7 | 0 |
| K1:C3:two_accents:rule_held_back | 1343 | 0 | 613 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 159 | 0 | 155 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 7 | 0 | 7 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 292 | 0 | 253 | 0 |
| detector_clipped_bottom | 44633 | 0 | 16119 | 74 |
| detector_clipped_top | 98404 | 0 | 20688 | 221 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 48 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 8 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 2 |
| edit_guard:punctuation_mismatch | 1472 | 2781 | 2781 | 7 |
| edit_guard:unsupported_character:0 | 1663 | 17 | 43 | 0 |
| edit_guard:unsupported_character:1 | 594 | 4 | 17 | 0 |
| edit_guard:unsupported_character:10 | 206 | 3 | 6 | 0 |
| edit_guard:unsupported_character:11 | 221 | 5 | 5 | 0 |
| edit_guard:unsupported_character:12 | 139 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 254 | 4 | 7 | 0 |
| edit_guard:unsupported_character:14 | 201 | 1 | 5 | 0 |
| edit_guard:unsupported_character:15 | 64 | 2 | 2 | 0 |
| edit_guard:unsupported_character:17 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:18 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:19 | 46 | 1 | 1 | 0 |
| edit_guard:unsupported_character:2 | 565 | 4 | 17 | 0 |
| edit_guard:unsupported_character:20 | 277 | 4 | 7 | 0 |
| edit_guard:unsupported_character:21 | 135 | 4 | 4 | 0 |
| edit_guard:unsupported_character:22 | 200 | 3 | 5 | 0 |
| edit_guard:unsupported_character:23 | 94 | 2 | 2 | 0 |
| edit_guard:unsupported_character:24 | 258 | 3 | 7 | 0 |
| edit_guard:unsupported_character:25 | 163 | 1 | 5 | 0 |
| edit_guard:unsupported_character:26 | 121 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 291 | 6 | 7 | 0 |
| edit_guard:unsupported_character:28 | 75 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 160 | 2 | 4 | 0 |
| edit_guard:unsupported_character:3 | 559 | 5 | 15 | 0 |
| edit_guard:unsupported_character:30 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:31 | 157 | 4 | 4 | 0 |
| edit_guard:unsupported_character:32 | 88 | 2 | 2 | 0 |
| edit_guard:unsupported_character:33 | 112 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 254 | 3 | 6 | 0 |
| edit_guard:unsupported_character:35 | 80 | 2 | 2 | 0 |
| edit_guard:unsupported_character:36 | 183 | 2 | 4 | 0 |
| edit_guard:unsupported_character:37 | 132 | 2 | 3 | 0 |
| edit_guard:unsupported_character:38 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:39 | 227 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 349 | 3 | 9 | 0 |
| edit_guard:unsupported_character:40 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:41 | 436 | 7 | 10 | 0 |
| edit_guard:unsupported_character:42 | 176 | 2 | 4 | 0 |
| edit_guard:unsupported_character:43 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:44 | 180 | 2 | 4 | 0 |
| edit_guard:unsupported_character:45 | 188 | 3 | 4 | 0 |
| edit_guard:unsupported_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_character:49 | 50 | 1 | 1 | 0 |
| edit_guard:unsupported_character:5 | 142 | 2 | 3 | 0 |
| edit_guard:unsupported_character:6 | 168 | 2 | 4 | 0 |
| edit_guard:unsupported_character:7 | 417 | 3 | 11 | 0 |
| edit_guard:unsupported_character:8 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:9 | 265 | 3 | 6 | 0 |
| edit_guard:unsupported_raw_character:0 | 1567 | 2 | 41 | 0 |
| edit_guard:unsupported_raw_character:1 | 521 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:10 | 206 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:11 | 221 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:12 | 139 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 254 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:14 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:15 | 64 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:17 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:18 | 179 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:19 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:2 | 546 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:20 | 277 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:21 | 135 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:22 | 200 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:23 | 142 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:24 | 210 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:25 | 163 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:26 | 121 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 291 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:28 | 75 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 191 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:3 | 559 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:30 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 157 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:32 | 88 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 112 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:34 | 254 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:35 | 80 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 183 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 132 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 227 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 349 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:40 | 222 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:41 | 393 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:42 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:43 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_raw_character:44 | 180 | 1 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 188 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:49 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 142 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:6 | 168 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 393 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:8 | 94 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:9 | 265 | 0 | 6 | 0 |
| mark_set_disagreement | 116911 | 0 | 22520 | 163 |
| r1_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_missing | 1452 | 0 | 955 | 0 |
| r1_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4765 |
| A/B disagreement | 0 |
| kind disagreement | 22520 |
| R1 uncertainty | 1829 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 4277 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 2820 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 2266 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1467 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 1281 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1192 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1016 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 751 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 656 |
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 515 |

### ALL / vouli_parliament_1850s

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 86 | 0 | 83 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 130 | 0 | 120 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 3 | 0 | 3 | 0 |
| K1:C3:two_accents:evidence_tie | 18 | 0 | 9 | 0 |
| K1:C3:two_accents:rule_held_back | 1597 | 0 | 641 | 2 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 200 | 0 | 181 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 12 | 0 | 10 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 281 | 0 | 258 | 0 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 2 | 0 | 2 | 0 |
| detector_clipped_bottom | 40732 | 0 | 15658 | 245 |
| detector_clipped_top | 93007 | 0 | 19927 | 846 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 33 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 24 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 8 |
| edit_guard:punctuation_mismatch | 3437 | 2268 | 2268 | 36 |
| edit_guard:unsupported_character:0 | 1166 | 8 | 25 | 0 |
| edit_guard:unsupported_character:1 | 510 | 3 | 12 | 0 |
| edit_guard:unsupported_character:10 | 146 | 2 | 4 | 0 |
| edit_guard:unsupported_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_character:15 | 112 | 2 | 3 | 0 |
| edit_guard:unsupported_character:17 | 256 | 4 | 7 | 0 |
| edit_guard:unsupported_character:18 | 156 | 1 | 3 | 0 |
| edit_guard:unsupported_character:19 | 309 | 3 | 8 | 0 |
| edit_guard:unsupported_character:2 | 313 | 1 | 8 | 0 |
| edit_guard:unsupported_character:20 | 40 | 1 | 1 | 0 |
| edit_guard:unsupported_character:21 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:22 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:23 | 72 | 1 | 2 | 0 |
| edit_guard:unsupported_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_character:25 | 91 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 171 | 2 | 4 | 0 |
| edit_guard:unsupported_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_character:28 | 222 | 4 | 5 | 0 |
| edit_guard:unsupported_character:29 | 169 | 3 | 3 | 0 |
| edit_guard:unsupported_character:3 | 657 | 1 | 18 | 0 |
| edit_guard:unsupported_character:30 | 78 | 1 | 2 | 0 |
| edit_guard:unsupported_character:31 | 313 | 2 | 7 | 0 |
| edit_guard:unsupported_character:32 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:33 | 145 | 0 | 3 | 0 |
| edit_guard:unsupported_character:34 | 213 | 2 | 5 | 0 |
| edit_guard:unsupported_character:35 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:36 | 215 | 3 | 5 | 0 |
| edit_guard:unsupported_character:37 | 138 | 1 | 3 | 0 |
| edit_guard:unsupported_character:38 | 94 | 1 | 2 | 0 |
| edit_guard:unsupported_character:39 | 240 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 225 | 3 | 7 | 0 |
| edit_guard:unsupported_character:40 | 426 | 2 | 9 | 0 |
| edit_guard:unsupported_character:41 | 240 | 2 | 5 | 0 |
| edit_guard:unsupported_character:42 | 327 | 3 | 7 | 0 |
| edit_guard:unsupported_character:43 | 412 | 4 | 8 | 0 |
| edit_guard:unsupported_character:44 | 47 | 1 | 1 | 0 |
| edit_guard:unsupported_character:45 | 189 | 1 | 3 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:48 | 100 | 2 | 2 | 0 |
| edit_guard:unsupported_character:49 | 203 | 2 | 4 | 0 |
| edit_guard:unsupported_character:5 | 345 | 2 | 6 | 0 |
| edit_guard:unsupported_character:50 | 109 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_character:6 | 251 | 1 | 6 | 0 |
| edit_guard:unsupported_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_character:7 | 350 | 4 | 7 | 0 |
| edit_guard:unsupported_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_character:76 | 163 | 0 | 2 | 0 |
| edit_guard:unsupported_character:8 | 176 | 1 | 4 | 0 |
| edit_guard:unsupported_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_character:9 | 296 | 6 | 7 | 0 |
| edit_guard:unsupported_raw_character:0 | 1166 | 3 | 28 | 0 |
| edit_guard:unsupported_raw_character:1 | 541 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:10 | 146 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:15 | 112 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:17 | 256 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:18 | 156 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:19 | 286 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:2 | 266 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:20 | 40 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:21 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:23 | 72 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:25 | 131 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 346 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:29 | 169 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:3 | 621 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:30 | 78 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 313 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:32 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 103 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:34 | 213 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:35 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:36 | 215 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 138 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:39 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 225 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:40 | 374 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:41 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:42 | 376 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:43 | 412 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:44 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 189 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:48 | 100 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:49 | 203 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:5 | 345 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 109 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:6 | 251 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 350 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:76 | 80 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:9 | 402 | 0 | 9 | 0 |
| mark_set_disagreement | 61677 | 0 | 18159 | 313 |
| r1_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_missing | 757 | 0 | 390 | 0 |
| r1_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3544 |
| A/B disagreement | 0 |
| kind disagreement | 18159 |
| R1 uncertainty | 744 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 2640 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 2628 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1433 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1370 |
| ["detector_clipped_top","mark_set_disagreement"] | 1093 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 972 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 856 |
| ["detector_clipped_top"] | 846 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 781 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 683 |

### mixed / anemi_mixed

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 48 | 0 | 47 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 102 | 0 | 99 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 2 | 0 | 2 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:evidence_tie | 4 | 0 | 2 | 0 |
| K1:C3:two_accents:rule_held_back | 868 | 0 | 379 | 2 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 123 | 0 | 121 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 214 | 0 | 201 | 3 |
| detector_clipped_bottom | 15059 | 0 | 6360 | 148 |
| detector_clipped_top | 39633 | 0 | 8777 | 620 |
| detector_localisation_unknown | 8716 | 0 | 3345 | 0 |
| detector_segmentation_uncertain | 17133 | 0 | 5085 | 24 |
| detector_unnamed_mark | 2392 | 0 | 1939 | 6 |
| edit_guard:base_or_character_mismatch | 389 | 1258 | 1258 | 4 |
| edit_guard:punctuation_mismatch | 1184 | 1470 | 1470 | 45 |
| edit_guard:unsupported_character:0 | 570 | 6 | 14 | 0 |
| edit_guard:unsupported_character:1 | 335 | 3 | 8 | 0 |
| edit_guard:unsupported_character:10 | 312 | 5 | 8 | 0 |
| edit_guard:unsupported_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 49 | 1 | 1 | 0 |
| edit_guard:unsupported_character:13 | 211 | 3 | 5 | 0 |
| edit_guard:unsupported_character:14 | 107 | 3 | 3 | 0 |
| edit_guard:unsupported_character:15 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:16 | 192 | 3 | 5 | 0 |
| edit_guard:unsupported_character:17 | 27 | 1 | 1 | 0 |
| edit_guard:unsupported_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:19 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_character:20 | 113 | 2 | 3 | 0 |
| edit_guard:unsupported_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_character:22 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_character:25 | 97 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 104 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 209 | 3 | 5 | 0 |
| edit_guard:unsupported_character:28 | 288 | 2 | 7 | 0 |
| edit_guard:unsupported_character:29 | 68 | 1 | 1 | 0 |
| edit_guard:unsupported_character:3 | 270 | 3 | 7 | 0 |
| edit_guard:unsupported_character:30 | 158 | 3 | 4 | 0 |
| edit_guard:unsupported_character:31 | 260 | 2 | 6 | 0 |
| edit_guard:unsupported_character:32 | 155 | 1 | 4 | 0 |
| edit_guard:unsupported_character:33 | 114 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_character:36 | 165 | 1 | 4 | 0 |
| edit_guard:unsupported_character:37 | 307 | 3 | 7 | 0 |
| edit_guard:unsupported_character:38 | 130 | 1 | 3 | 0 |
| edit_guard:unsupported_character:39 | 134 | 2 | 3 | 0 |
| edit_guard:unsupported_character:4 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_character:41 | 101 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 233 | 3 | 5 | 0 |
| edit_guard:unsupported_character:43 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:44 | 253 | 3 | 5 | 0 |
| edit_guard:unsupported_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_character:46 | 144 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 102 | 1 | 2 | 0 |
| edit_guard:unsupported_character:48 | 102 | 2 | 2 | 0 |
| edit_guard:unsupported_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_character:50 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_character:6 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 145 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 227 | 4 | 5 | 0 |
| edit_guard:unsupported_raw_character:0 | 563 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:1 | 335 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 312 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:13 | 211 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:14 | 156 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:16 | 192 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:17 | 27 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:19 | 97 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:20 | 113 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:25 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:26 | 131 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 209 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:28 | 288 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:29 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 270 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:30 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:31 | 260 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:32 | 155 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 114 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 165 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 307 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:38 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:4 | 130 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:41 | 101 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 233 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:44 | 253 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:46 | 144 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 102 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:48 | 102 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:50 | 57 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:8 | 227 | 0 | 5 | 0 |
| mark_set_disagreement | 27999 | 0 | 9837 | 1021 |
| r1_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_missing | 418 | 0 | 244 | 0 |
| r1_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 132 | 0 | 51 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 266 | 0 | 200 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6032 |
| clipping | 9594 |
| K1 | 609 |
| edit-guard | 2191 |
| A/B disagreement | 0 |
| kind disagreement | 9837 |
| R1 uncertainty | 294 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 1504 |
| ["mark_set_disagreement"] | 1021 |
| ["detector_clipped_top","mark_set_disagreement"] | 889 |
| ["detector_clipped_bottom","detector_clipped_top"] | 874 |
| ["detector_clipped_top"] | 620 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 559 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 522 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 476 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 398 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 324 |

### mixed / archive_b28038630

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 2 | 0 | 1 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 130 | 0 | 45 | 1 |
| detector_clipped_top | 254 | 0 | 58 | 4 |
| detector_localisation_unknown | 7 | 0 | 6 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 13 | 13 | 0 |
| edit_guard:punctuation_mismatch | 0 | 22 | 22 | 4 |
| mark_set_disagreement | 92 | 0 | 54 | 4 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 13 |
| clipping | 61 |
| K1 | 3 |
| edit-guard | 24 |
| A/B disagreement | 0 |
| kind disagreement | 54 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 17 |
| ["detector_clipped_bottom","detector_clipped_top"] | 8 |
| ["detector_clipped_top","mark_set_disagreement"] | 7 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 6 |
| ["detector_clipped_top"] | 4 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 4 |
| ["edit_guard:punctuation_mismatch"] | 4 |
| ["mark_set_disagreement"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 2 |

### mixed / openarchives_mixed_Pandemos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_clipped_bottom | 16 | 0 | 7 | 0 |
| detector_clipped_top | 27 | 0 | 4 | 0 |
| detector_localisation_unknown | 5 | 0 | 1 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 2 | 0 |
| detector_unnamed_mark | 3 | 0 | 3 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 1 | 1 | 0 |
| edit_guard:punctuation_mismatch | 0 | 1 | 1 | 0 |
| mark_set_disagreement | 25 | 0 | 10 | 2 |
| r1_missing | 1 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 7 |
| K1 | 0 |
| edit-guard | 2 |
| A/B disagreement | 0 |
| kind disagreement | 10 |
| R1 uncertainty | 1 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top"] | 2 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 2 |
| ["mark_set_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 1 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","mark_set_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |
| ["detector_unnamed_mark","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 1 |
| ["detector_unnamed_mark","mark_set_disagreement"] | 1 |

### mixed / openarchives_mixed_apothesis

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| mark_set_disagreement | 1 | 0 | 1 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 0 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 1 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_set_disagreement"] | 1 |

### mixed / openarchives_mixed_ktisis

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_unnamed_mark | 1 | 0 | 1 | 1 |
| mark_set_disagreement | 1 | 0 | 1 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 1 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 1 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_unnamed_mark"] | 1 |
| ["mark_set_disagreement"] | 1 |

### mixed / openarchives_mixed_ntua

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_not_initial:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:rule_held_back | 4 | 0 | 2 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_bottom | 11 | 0 | 5 | 0 |
| detector_clipped_top | 29 | 0 | 5 | 0 |
| detector_localisation_unknown | 15 | 0 | 3 | 0 |
| detector_segmentation_uncertain | 27 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 21 | 21 | 0 |
| edit_guard:punctuation_mismatch | 104 | 16 | 16 | 0 |
| edit_guard:unsupported_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| mark_set_disagreement | 140 | 0 | 30 | 5 |
| r1_missing | 21 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 18 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 3 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 12 |
| clipping | 7 |
| K1 | 4 |
| edit-guard | 22 |
| A/B disagreement | 0 |
| kind disagreement | 30 |
| R1 uncertainty | 4 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 7 |
| ["mark_set_disagreement"] | 5 |
| ["edit_guard:base_or_character_mismatch","mark_set_disagreement"] | 2 |
| ["K1:C1:breathing_not_initial:impossible_by_rule","K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","edit_guard:unsupported_character:28","edit_guard:unsupported_raw_character:28","mark_set_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","r1_unscored:width_outside_0.2_2.0_median_ctc"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","mark_set_disagreement"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","mark_set_disagreement"] | 1 |
| ["detector_clipped_bottom","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |

### openarchives / openarchives_Pandemos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_clipped_bottom | 366 | 0 | 118 | 19 |
| detector_clipped_top | 604 | 0 | 118 | 20 |
| detector_segmentation_uncertain | 100 | 0 | 35 | 0 |
| detector_unnamed_mark | 23 | 0 | 18 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 9 | 9 | 0 |
| mark_set_disagreement | 197 | 0 | 88 | 5 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 46 |
| clipping | 157 |
| K1 | 0 |
| edit-guard | 9 |
| A/B disagreement | 0 |
| kind disagreement | 88 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 39 |
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 22 |
| ["detector_clipped_top"] | 20 |
| ["detector_clipped_bottom"] | 19 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","mark_set_disagreement"] | 9 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 8 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 7 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 7 |
| ["detector_segmentation_uncertain","mark_set_disagreement"] | 6 |
| ["detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 5 |

### openarchives / openarchives_kallipos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 12 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_top | 25 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 10 | 0 | 3 | 0 |
| detector_unnamed_mark | 1 | 0 | 1 | 0 |
| edit_guard:punctuation_mismatch | 0 | 10 | 10 | 3 |
| mark_set_disagreement | 59 | 0 | 34 | 20 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 2 |
| K1 | 5 |
| edit-guard | 10 |
| A/B disagreement | 0 |
| kind disagreement | 34 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_set_disagreement"] | 20 |
| ["edit_guard:punctuation_mismatch","mark_set_disagreement"] | 4 |
| ["detector_segmentation_uncertain","mark_set_disagreement"] | 3 |
| ["edit_guard:punctuation_mismatch"] | 3 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","mark_set_disagreement"] | 2 |
| ["detector_clipped_top","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 2 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_unnamed_mark","mark_set_disagreement"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 1 |
| ["K1:C3:two_accents:rule_held_back","mark_set_disagreement"] | 1 |

### parliament / parliament_proceedings_1975_2000

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 69 | 0 | 67 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 90 | 0 | 88 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C3:two_accents:evidence_tie | 14 | 0 | 7 | 0 |
| K1:C3:two_accents:rule_held_back | 1343 | 0 | 613 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 159 | 0 | 155 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 7 | 0 | 7 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 292 | 0 | 253 | 0 |
| detector_clipped_bottom | 44633 | 0 | 16119 | 74 |
| detector_clipped_top | 98404 | 0 | 20688 | 221 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 48 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 8 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 2 |
| edit_guard:punctuation_mismatch | 1472 | 2781 | 2781 | 7 |
| edit_guard:unsupported_character:0 | 1663 | 17 | 43 | 0 |
| edit_guard:unsupported_character:1 | 594 | 4 | 17 | 0 |
| edit_guard:unsupported_character:10 | 206 | 3 | 6 | 0 |
| edit_guard:unsupported_character:11 | 221 | 5 | 5 | 0 |
| edit_guard:unsupported_character:12 | 139 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 254 | 4 | 7 | 0 |
| edit_guard:unsupported_character:14 | 201 | 1 | 5 | 0 |
| edit_guard:unsupported_character:15 | 64 | 2 | 2 | 0 |
| edit_guard:unsupported_character:17 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:18 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:19 | 46 | 1 | 1 | 0 |
| edit_guard:unsupported_character:2 | 565 | 4 | 17 | 0 |
| edit_guard:unsupported_character:20 | 277 | 4 | 7 | 0 |
| edit_guard:unsupported_character:21 | 135 | 4 | 4 | 0 |
| edit_guard:unsupported_character:22 | 200 | 3 | 5 | 0 |
| edit_guard:unsupported_character:23 | 94 | 2 | 2 | 0 |
| edit_guard:unsupported_character:24 | 258 | 3 | 7 | 0 |
| edit_guard:unsupported_character:25 | 163 | 1 | 5 | 0 |
| edit_guard:unsupported_character:26 | 121 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 291 | 6 | 7 | 0 |
| edit_guard:unsupported_character:28 | 75 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 160 | 2 | 4 | 0 |
| edit_guard:unsupported_character:3 | 559 | 5 | 15 | 0 |
| edit_guard:unsupported_character:30 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:31 | 157 | 4 | 4 | 0 |
| edit_guard:unsupported_character:32 | 88 | 2 | 2 | 0 |
| edit_guard:unsupported_character:33 | 112 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 254 | 3 | 6 | 0 |
| edit_guard:unsupported_character:35 | 80 | 2 | 2 | 0 |
| edit_guard:unsupported_character:36 | 183 | 2 | 4 | 0 |
| edit_guard:unsupported_character:37 | 132 | 2 | 3 | 0 |
| edit_guard:unsupported_character:38 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:39 | 227 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 349 | 3 | 9 | 0 |
| edit_guard:unsupported_character:40 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:41 | 436 | 7 | 10 | 0 |
| edit_guard:unsupported_character:42 | 176 | 2 | 4 | 0 |
| edit_guard:unsupported_character:43 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:44 | 180 | 2 | 4 | 0 |
| edit_guard:unsupported_character:45 | 188 | 3 | 4 | 0 |
| edit_guard:unsupported_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_character:49 | 50 | 1 | 1 | 0 |
| edit_guard:unsupported_character:5 | 142 | 2 | 3 | 0 |
| edit_guard:unsupported_character:6 | 168 | 2 | 4 | 0 |
| edit_guard:unsupported_character:7 | 417 | 3 | 11 | 0 |
| edit_guard:unsupported_character:8 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:9 | 265 | 3 | 6 | 0 |
| edit_guard:unsupported_raw_character:0 | 1567 | 2 | 41 | 0 |
| edit_guard:unsupported_raw_character:1 | 521 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:10 | 206 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:11 | 221 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:12 | 139 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 254 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:14 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:15 | 64 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:17 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:18 | 179 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:19 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:2 | 546 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:20 | 277 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:21 | 135 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:22 | 200 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:23 | 142 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:24 | 210 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:25 | 163 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:26 | 121 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 291 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:28 | 75 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 191 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:3 | 559 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:30 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 157 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:32 | 88 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 112 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:34 | 254 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:35 | 80 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 183 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 132 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 227 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 349 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:40 | 222 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:41 | 393 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:42 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:43 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_raw_character:44 | 180 | 1 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 188 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:49 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 142 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:6 | 168 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 393 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:8 | 94 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:9 | 265 | 0 | 6 | 0 |
| mark_set_disagreement | 116911 | 0 | 22520 | 163 |
| r1_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_missing | 1452 | 0 | 955 | 0 |
| r1_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4765 |
| A/B disagreement | 0 |
| kind disagreement | 22520 |
| R1 uncertainty | 1829 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 4277 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 2820 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 2266 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1467 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 1281 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1192 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1016 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 751 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 656 |
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 515 |

### round1 / anemi_round1

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 0 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 10 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 2 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 2 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 553 |
| detector_clipped_top | 140308 | 0 | 29544 | 2030 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 116 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 36 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 31 |
| edit_guard:punctuation_mismatch | 9153 | 6398 | 6398 | 193 |
| edit_guard:unsupported_character:0 | 3286 | 23 | 79 | 0 |
| edit_guard:unsupported_character:1 | 2211 | 16 | 47 | 0 |
| edit_guard:unsupported_character:10 | 439 | 5 | 12 | 0 |
| edit_guard:unsupported_character:11 | 317 | 3 | 9 | 0 |
| edit_guard:unsupported_character:12 | 144 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 283 | 6 | 9 | 0 |
| edit_guard:unsupported_character:14 | 407 | 9 | 13 | 0 |
| edit_guard:unsupported_character:15 | 470 | 7 | 14 | 0 |
| edit_guard:unsupported_character:16 | 268 | 3 | 7 | 0 |
| edit_guard:unsupported_character:17 | 383 | 4 | 9 | 0 |
| edit_guard:unsupported_character:18 | 295 | 3 | 8 | 0 |
| edit_guard:unsupported_character:19 | 337 | 3 | 10 | 0 |
| edit_guard:unsupported_character:2 | 409 | 4 | 11 | 0 |
| edit_guard:unsupported_character:20 | 535 | 6 | 13 | 0 |
| edit_guard:unsupported_character:21 | 407 | 4 | 12 | 0 |
| edit_guard:unsupported_character:22 | 427 | 8 | 11 | 0 |
| edit_guard:unsupported_character:23 | 668 | 7 | 19 | 0 |
| edit_guard:unsupported_character:24 | 469 | 7 | 11 | 0 |
| edit_guard:unsupported_character:25 | 228 | 3 | 7 | 0 |
| edit_guard:unsupported_character:26 | 599 | 6 | 15 | 0 |
| edit_guard:unsupported_character:27 | 636 | 6 | 17 | 0 |
| edit_guard:unsupported_character:28 | 581 | 6 | 17 | 0 |
| edit_guard:unsupported_character:29 | 1243 | 12 | 33 | 0 |
| edit_guard:unsupported_character:3 | 622 | 2 | 15 | 0 |
| edit_guard:unsupported_character:30 | 652 | 5 | 18 | 0 |
| edit_guard:unsupported_character:31 | 551 | 3 | 15 | 0 |
| edit_guard:unsupported_character:32 | 684 | 4 | 18 | 0 |
| edit_guard:unsupported_character:33 | 538 | 5 | 13 | 0 |
| edit_guard:unsupported_character:34 | 781 | 4 | 18 | 0 |
| edit_guard:unsupported_character:35 | 701 | 6 | 17 | 0 |
| edit_guard:unsupported_character:36 | 745 | 2 | 19 | 0 |
| edit_guard:unsupported_character:37 | 765 | 5 | 19 | 0 |
| edit_guard:unsupported_character:38 | 408 | 1 | 10 | 0 |
| edit_guard:unsupported_character:39 | 791 | 6 | 18 | 0 |
| edit_guard:unsupported_character:4 | 497 | 4 | 11 | 0 |
| edit_guard:unsupported_character:40 | 448 | 3 | 10 | 0 |
| edit_guard:unsupported_character:41 | 811 | 5 | 18 | 0 |
| edit_guard:unsupported_character:42 | 454 | 4 | 10 | 0 |
| edit_guard:unsupported_character:43 | 569 | 6 | 12 | 0 |
| edit_guard:unsupported_character:44 | 300 | 3 | 6 | 0 |
| edit_guard:unsupported_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_character:46 | 262 | 1 | 5 | 0 |
| edit_guard:unsupported_character:47 | 207 | 4 | 4 | 0 |
| edit_guard:unsupported_character:48 | 251 | 2 | 5 | 0 |
| edit_guard:unsupported_character:49 | 315 | 1 | 6 | 0 |
| edit_guard:unsupported_character:5 | 299 | 2 | 7 | 0 |
| edit_guard:unsupported_character:50 | 284 | 3 | 5 | 0 |
| edit_guard:unsupported_character:51 | 495 | 3 | 9 | 0 |
| edit_guard:unsupported_character:52 | 175 | 1 | 3 | 0 |
| edit_guard:unsupported_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_character:54 | 202 | 2 | 3 | 0 |
| edit_guard:unsupported_character:55 | 247 | 2 | 4 | 0 |
| edit_guard:unsupported_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_character:57 | 202 | 1 | 3 | 0 |
| edit_guard:unsupported_character:58 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:59 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 421 | 2 | 12 | 0 |
| edit_guard:unsupported_character:60 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_character:62 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:65 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 431 | 3 | 9 | 0 |
| edit_guard:unsupported_character:74 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:8 | 618 | 4 | 15 | 0 |
| edit_guard:unsupported_character:9 | 433 | 4 | 11 | 0 |
| edit_guard:unsupported_raw_character:0 | 3282 | 1 | 78 | 0 |
| edit_guard:unsupported_raw_character:1 | 1715 | 0 | 40 | 0 |
| edit_guard:unsupported_raw_character:10 | 439 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:11 | 339 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:12 | 144 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:13 | 283 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:14 | 424 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:15 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:16 | 302 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:17 | 383 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:18 | 317 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:19 | 379 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:2 | 409 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:20 | 535 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:21 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:22 | 427 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:23 | 668 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:24 | 469 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:25 | 228 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:26 | 599 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:27 | 636 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:28 | 581 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:29 | 1243 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:3 | 644 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:30 | 652 | 1 | 19 | 0 |
| edit_guard:unsupported_raw_character:31 | 551 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:32 | 718 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:33 | 543 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:34 | 742 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:35 | 701 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:36 | 745 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:37 | 806 | 0 | 20 | 0 |
| edit_guard:unsupported_raw_character:38 | 402 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:39 | 831 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:4 | 497 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:40 | 448 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:41 | 811 | 0 | 18 | 0 |
| edit_guard:unsupported_raw_character:42 | 454 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:43 | 569 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:44 | 300 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:46 | 262 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:47 | 207 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:48 | 251 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:49 | 315 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:5 | 270 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 233 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 436 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:52 | 175 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:54 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:55 | 247 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:57 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:58 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:59 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 421 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:60 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:62 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:65 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 471 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:74 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 545 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:9 | 433 | 0 | 11 | 0 |
| mark_set_disagreement | 78967 | 0 | 31761 | 3116 |
| r1_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_missing | 1687 | 0 | 1129 | 0 |
| r1_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9251 |
| A/B disagreement | 0 |
| kind disagreement | 31761 |
| R1 uncertainty | 1276 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 4677 |
| ["mark_set_disagreement"] | 3116 |
| ["detector_clipped_bottom","detector_clipped_top"] | 2883 |
| ["detector_clipped_top","mark_set_disagreement"] | 2614 |
| ["detector_clipped_top"] | 2030 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1976 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 1388 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1257 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1176 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 1072 |

### round2 / anemi_round2

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 84 | 0 | 81 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 107 | 0 | 103 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 6 | 0 | 3 | 0 |
| K1:C3:two_accents:rule_held_back | 1020 | 0 | 467 | 3 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 101 | 0 | 98 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 1 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 194 |
| detector_clipped_top | 48664 | 0 | 10763 | 853 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 44 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 19 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 16 |
| edit_guard:punctuation_mismatch | 1491 | 2095 | 2095 | 103 |
| edit_guard:unsupported_character:0 | 1107 | 12 | 28 | 0 |
| edit_guard:unsupported_character:1 | 360 | 2 | 9 | 0 |
| edit_guard:unsupported_character:10 | 169 | 1 | 4 | 0 |
| edit_guard:unsupported_character:11 | 54 | 1 | 1 | 0 |
| edit_guard:unsupported_character:12 | 178 | 3 | 5 | 0 |
| edit_guard:unsupported_character:13 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_character:14 | 169 | 2 | 4 | 0 |
| edit_guard:unsupported_character:15 | 122 | 3 | 3 | 0 |
| edit_guard:unsupported_character:16 | 225 | 1 | 8 | 0 |
| edit_guard:unsupported_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_character:18 | 252 | 3 | 7 | 0 |
| edit_guard:unsupported_character:19 | 108 | 1 | 3 | 0 |
| edit_guard:unsupported_character:2 | 238 | 4 | 6 | 0 |
| edit_guard:unsupported_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_character:21 | 129 | 1 | 4 | 0 |
| edit_guard:unsupported_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_character:23 | 43 | 1 | 1 | 0 |
| edit_guard:unsupported_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_character:27 | 150 | 3 | 4 | 0 |
| edit_guard:unsupported_character:28 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 71 | 0 | 2 | 0 |
| edit_guard:unsupported_character:3 | 236 | 3 | 6 | 0 |
| edit_guard:unsupported_character:30 | 225 | 3 | 6 | 0 |
| edit_guard:unsupported_character:31 | 201 | 3 | 5 | 0 |
| edit_guard:unsupported_character:32 | 79 | 1 | 2 | 0 |
| edit_guard:unsupported_character:33 | 250 | 2 | 6 | 0 |
| edit_guard:unsupported_character:34 | 116 | 1 | 3 | 0 |
| edit_guard:unsupported_character:35 | 152 | 1 | 4 | 0 |
| edit_guard:unsupported_character:36 | 212 | 2 | 5 | 0 |
| edit_guard:unsupported_character:37 | 356 | 5 | 8 | 0 |
| edit_guard:unsupported_character:38 | 192 | 4 | 4 | 0 |
| edit_guard:unsupported_character:39 | 98 | 2 | 2 | 0 |
| edit_guard:unsupported_character:4 | 63 | 1 | 2 | 0 |
| edit_guard:unsupported_character:40 | 87 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 241 | 2 | 5 | 0 |
| edit_guard:unsupported_character:43 | 92 | 1 | 2 | 0 |
| edit_guard:unsupported_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_character:45 | 51 | 1 | 1 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_character:5 | 121 | 3 | 3 | 0 |
| edit_guard:unsupported_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_character:53 | 113 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_character:59 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 165 | 4 | 5 | 0 |
| edit_guard:unsupported_character:60 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 173 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 145 | 1 | 4 | 0 |
| edit_guard:unsupported_character:9 | 114 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:0 | 1012 | 0 | 26 | 0 |
| edit_guard:unsupported_raw_character:1 | 341 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 54 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 178 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:13 | 96 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:14 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 122 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:16 | 225 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 252 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:19 | 108 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:2 | 238 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:21 | 98 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:23 | 43 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:28 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 41 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 236 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:30 | 193 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:31 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:32 | 79 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 250 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:34 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:35 | 152 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:36 | 212 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 356 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:38 | 192 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:4 | 79 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 241 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 92 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 148 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 113 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:59 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 165 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:60 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 148 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:8 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:9 | 114 | 0 | 4 | 0 |
| mark_set_disagreement | 29904 | 0 | 12180 | 1681 |
| r1_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_missing | 434 | 0 | 268 | 0 |
| r1_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3059 |
| A/B disagreement | 0 |
| kind disagreement | 12180 |
| R1 uncertainty | 354 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 1899 |
| ["mark_set_disagreement"] | 1681 |
| ["detector_clipped_top","mark_set_disagreement"] | 1136 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1107 |
| ["detector_clipped_top"] | 853 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 565 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 501 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 458 |
| ["detector_segmentation_uncertain","mark_set_disagreement"] | 348 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 333 |

### vouli / vouli_parliament_1850s

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 86 | 0 | 83 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 130 | 0 | 120 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 3 | 0 | 3 | 0 |
| K1:C3:two_accents:evidence_tie | 18 | 0 | 9 | 0 |
| K1:C3:two_accents:rule_held_back | 1597 | 0 | 641 | 2 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 200 | 0 | 181 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 12 | 0 | 10 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 281 | 0 | 258 | 0 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 2 | 0 | 2 | 0 |
| detector_clipped_bottom | 40732 | 0 | 15658 | 245 |
| detector_clipped_top | 93007 | 0 | 19927 | 846 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 33 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 24 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 8 |
| edit_guard:punctuation_mismatch | 3437 | 2268 | 2268 | 36 |
| edit_guard:unsupported_character:0 | 1166 | 8 | 25 | 0 |
| edit_guard:unsupported_character:1 | 510 | 3 | 12 | 0 |
| edit_guard:unsupported_character:10 | 146 | 2 | 4 | 0 |
| edit_guard:unsupported_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_character:15 | 112 | 2 | 3 | 0 |
| edit_guard:unsupported_character:17 | 256 | 4 | 7 | 0 |
| edit_guard:unsupported_character:18 | 156 | 1 | 3 | 0 |
| edit_guard:unsupported_character:19 | 309 | 3 | 8 | 0 |
| edit_guard:unsupported_character:2 | 313 | 1 | 8 | 0 |
| edit_guard:unsupported_character:20 | 40 | 1 | 1 | 0 |
| edit_guard:unsupported_character:21 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:22 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:23 | 72 | 1 | 2 | 0 |
| edit_guard:unsupported_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_character:25 | 91 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 171 | 2 | 4 | 0 |
| edit_guard:unsupported_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_character:28 | 222 | 4 | 5 | 0 |
| edit_guard:unsupported_character:29 | 169 | 3 | 3 | 0 |
| edit_guard:unsupported_character:3 | 657 | 1 | 18 | 0 |
| edit_guard:unsupported_character:30 | 78 | 1 | 2 | 0 |
| edit_guard:unsupported_character:31 | 313 | 2 | 7 | 0 |
| edit_guard:unsupported_character:32 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:33 | 145 | 0 | 3 | 0 |
| edit_guard:unsupported_character:34 | 213 | 2 | 5 | 0 |
| edit_guard:unsupported_character:35 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:36 | 215 | 3 | 5 | 0 |
| edit_guard:unsupported_character:37 | 138 | 1 | 3 | 0 |
| edit_guard:unsupported_character:38 | 94 | 1 | 2 | 0 |
| edit_guard:unsupported_character:39 | 240 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 225 | 3 | 7 | 0 |
| edit_guard:unsupported_character:40 | 426 | 2 | 9 | 0 |
| edit_guard:unsupported_character:41 | 240 | 2 | 5 | 0 |
| edit_guard:unsupported_character:42 | 327 | 3 | 7 | 0 |
| edit_guard:unsupported_character:43 | 412 | 4 | 8 | 0 |
| edit_guard:unsupported_character:44 | 47 | 1 | 1 | 0 |
| edit_guard:unsupported_character:45 | 189 | 1 | 3 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:48 | 100 | 2 | 2 | 0 |
| edit_guard:unsupported_character:49 | 203 | 2 | 4 | 0 |
| edit_guard:unsupported_character:5 | 345 | 2 | 6 | 0 |
| edit_guard:unsupported_character:50 | 109 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_character:6 | 251 | 1 | 6 | 0 |
| edit_guard:unsupported_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_character:7 | 350 | 4 | 7 | 0 |
| edit_guard:unsupported_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_character:76 | 163 | 0 | 2 | 0 |
| edit_guard:unsupported_character:8 | 176 | 1 | 4 | 0 |
| edit_guard:unsupported_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_character:9 | 296 | 6 | 7 | 0 |
| edit_guard:unsupported_raw_character:0 | 1166 | 3 | 28 | 0 |
| edit_guard:unsupported_raw_character:1 | 541 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:10 | 146 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:15 | 112 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:17 | 256 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:18 | 156 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:19 | 286 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:2 | 266 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:20 | 40 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:21 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:23 | 72 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:25 | 131 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 346 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:29 | 169 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:3 | 621 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:30 | 78 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 313 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:32 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 103 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:34 | 213 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:35 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:36 | 215 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 138 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:39 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 225 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:40 | 374 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:41 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:42 | 376 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:43 | 412 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:44 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 189 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:48 | 100 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:49 | 203 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:5 | 345 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 109 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:6 | 251 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 350 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:76 | 80 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:9 | 402 | 0 | 9 | 0 |
| mark_set_disagreement | 61677 | 0 | 18159 | 313 |
| r1_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_missing | 757 | 0 | 390 | 0 |
| r1_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3544 |
| A/B disagreement | 0 |
| kind disagreement | 18159 |
| R1 uncertainty | 744 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 2640 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 2628 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1433 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1370 |
| ["detector_clipped_top","mark_set_disagreement"] | 1093 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 972 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 856 |
| ["detector_clipped_top"] | 846 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 781 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 683 |
## ENSEMBLE_AB

| Wave | Source | Lines | HOLD | Held glyph slots |
|---|---|---:|---:|---:|
| ALL | ALL | 124669 | 112789 | 893776 |
| mixed | ALL | 13227 | 11465 | 77563 |
| openarchives | ALL | 235 | 194 | 1053 |
| parliament | ALL | 27224 | 26927 | 286767 |
| round1 | ALL | 43869 | 37901 | 266074 |
| round2 | ALL | 17026 | 13913 | 89432 |
| vouli | ALL | 23088 | 22389 | 172887 |
| ALL | anemi_mixed | 13084 | 11355 | 76829 |
| ALL | anemi_round1 | 43869 | 37901 | 266074 |
| ALL | anemi_round2 | 17026 | 13913 | 89432 |
| ALL | archive_b28038630 | 97 | 74 | 374 |
| ALL | openarchives_Pandemos | 185 | 165 | 991 |
| ALL | openarchives_kallipos | 50 | 29 | 62 |
| ALL | openarchives_mixed_Pandemos | 13 | 10 | 55 |
| ALL | openarchives_mixed_apothesis | 1 | 0 | 0 |
| ALL | openarchives_mixed_ktisis | 2 | 1 | 1 |
| ALL | openarchives_mixed_ntua | 30 | 25 | 304 |
| ALL | parliament_proceedings_1975_2000 | 27224 | 26927 | 286767 |
| ALL | vouli_parliament_1850s | 23088 | 22389 | 172887 |
| mixed | anemi_mixed | 13084 | 11355 | 76829 |
| mixed | archive_b28038630 | 97 | 74 | 374 |
| mixed | openarchives_mixed_Pandemos | 13 | 10 | 55 |
| mixed | openarchives_mixed_apothesis | 1 | 0 | 0 |
| mixed | openarchives_mixed_ktisis | 2 | 1 | 1 |
| mixed | openarchives_mixed_ntua | 30 | 25 | 304 |
| openarchives | openarchives_Pandemos | 185 | 165 | 991 |
| openarchives | openarchives_kallipos | 50 | 29 | 62 |
| parliament | parliament_proceedings_1975_2000 | 27224 | 26927 | 286767 |
| round1 | anemi_round1 | 43869 | 37901 | 266074 |
| round2 | anemi_round2 | 17026 | 13913 | 89432 |
| vouli | vouli_parliament_1850s | 23088 | 22389 | 172887 |

### ALL / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 543 | 0 | 525 | 3 |
| K1:C1:breathing_not_initial:impossible_by_rule | 770 | 0 | 741 | 7 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 6 | 0 | 6 | 2 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 6 | 0 | 6 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 18 | 0 | 18 | 0 |
| K1:C3:two_accents:evidence_tie | 58 | 0 | 29 | 1 |
| K1:C3:two_accents:rule_held_back | 8094 | 0 | 3535 | 47 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 956 | 0 | 917 | 4 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 48 | 0 | 46 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1782 | 0 | 1627 | 10 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 3 | 0 | 3 | 0 |
| detector_clipped_bottom | 176335 | 0 | 68784 | 2823 |
| detector_clipped_top | 420955 | 0 | 89886 | 10297 |
| detector_localisation_unknown | 151696 | 0 | 46253 | 0 |
| detector_segmentation_uncertain | 254880 | 0 | 60333 | 1735 |
| detector_unnamed_mark | 40015 | 0 | 26798 | 1241 |
| edit_guard:base_or_character_mismatch | 4440 | 13689 | 13689 | 220 |
| edit_guard:punctuation_mismatch | 16841 | 15070 | 15070 | 876 |
| edit_guard:unsupported_character:0 | 7792 | 66 | 189 | 0 |
| edit_guard:unsupported_character:1 | 4010 | 28 | 93 | 0 |
| edit_guard:unsupported_character:10 | 1272 | 16 | 34 | 0 |
| edit_guard:unsupported_character:11 | 665 | 9 | 17 | 0 |
| edit_guard:unsupported_character:12 | 601 | 8 | 15 | 0 |
| edit_guard:unsupported_character:13 | 917 | 14 | 28 | 0 |
| edit_guard:unsupported_character:14 | 1018 | 15 | 28 | 0 |
| edit_guard:unsupported_character:15 | 864 | 16 | 24 | 0 |
| edit_guard:unsupported_character:16 | 685 | 7 | 20 | 0 |
| edit_guard:unsupported_character:17 | 785 | 10 | 20 | 0 |
| edit_guard:unsupported_character:18 | 933 | 10 | 23 | 0 |
| edit_guard:unsupported_character:19 | 930 | 10 | 25 | 0 |
| edit_guard:unsupported_character:2 | 1700 | 13 | 46 | 0 |
| edit_guard:unsupported_character:20 | 1105 | 13 | 28 | 0 |
| edit_guard:unsupported_character:21 | 854 | 10 | 24 | 0 |
| edit_guard:unsupported_character:22 | 844 | 14 | 22 | 0 |
| edit_guard:unsupported_character:23 | 1021 | 11 | 28 | 0 |
| edit_guard:unsupported_character:24 | 830 | 10 | 21 | 0 |
| edit_guard:unsupported_character:25 | 689 | 6 | 19 | 0 |
| edit_guard:unsupported_character:26 | 1089 | 10 | 28 | 0 |
| edit_guard:unsupported_character:27 | 1334 | 18 | 34 | 0 |
| edit_guard:unsupported_character:28 | 1287 | 14 | 34 | 0 |
| edit_guard:unsupported_character:29 | 1711 | 18 | 43 | 0 |
| edit_guard:unsupported_character:3 | 2344 | 14 | 61 | 0 |
| edit_guard:unsupported_character:30 | 1154 | 13 | 31 | 0 |
| edit_guard:unsupported_character:31 | 1482 | 14 | 37 | 0 |
| edit_guard:unsupported_character:32 | 1122 | 10 | 29 | 0 |
| edit_guard:unsupported_character:33 | 1159 | 9 | 28 | 0 |
| edit_guard:unsupported_character:34 | 1438 | 10 | 34 | 0 |
| edit_guard:unsupported_character:35 | 1137 | 10 | 28 | 0 |
| edit_guard:unsupported_character:36 | 1520 | 10 | 37 | 0 |
| edit_guard:unsupported_character:37 | 1698 | 16 | 40 | 0 |
| edit_guard:unsupported_character:38 | 1008 | 9 | 23 | 0 |
| edit_guard:unsupported_character:39 | 1490 | 16 | 33 | 0 |
| edit_guard:unsupported_character:4 | 1264 | 13 | 32 | 0 |
| edit_guard:unsupported_character:40 | 1397 | 10 | 31 | 0 |
| edit_guard:unsupported_character:41 | 1588 | 16 | 35 | 0 |
| edit_guard:unsupported_character:42 | 1431 | 14 | 31 | 0 |
| edit_guard:unsupported_character:43 | 1353 | 15 | 28 | 0 |
| edit_guard:unsupported_character:44 | 825 | 9 | 17 | 0 |
| edit_guard:unsupported_character:45 | 811 | 5 | 16 | 0 |
| edit_guard:unsupported_character:46 | 759 | 4 | 15 | 0 |
| edit_guard:unsupported_character:47 | 562 | 6 | 11 | 0 |
| edit_guard:unsupported_character:48 | 503 | 6 | 10 | 0 |
| edit_guard:unsupported_character:49 | 568 | 4 | 11 | 0 |
| edit_guard:unsupported_character:5 | 953 | 9 | 20 | 0 |
| edit_guard:unsupported_character:50 | 450 | 4 | 8 | 0 |
| edit_guard:unsupported_character:51 | 547 | 3 | 10 | 0 |
| edit_guard:unsupported_character:52 | 281 | 2 | 5 | 0 |
| edit_guard:unsupported_character:53 | 402 | 1 | 7 | 0 |
| edit_guard:unsupported_character:54 | 370 | 2 | 6 | 0 |
| edit_guard:unsupported_character:55 | 471 | 2 | 7 | 0 |
| edit_guard:unsupported_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_character:57 | 202 | 1 | 3 | 0 |
| edit_guard:unsupported_character:58 | 186 | 1 | 3 | 0 |
| edit_guard:unsupported_character:59 | 125 | 2 | 2 | 0 |
| edit_guard:unsupported_character:6 | 1058 | 10 | 28 | 0 |
| edit_guard:unsupported_character:60 | 254 | 2 | 4 | 0 |
| edit_guard:unsupported_character:61 | 187 | 0 | 3 | 0 |
| edit_guard:unsupported_character:62 | 133 | 1 | 2 | 0 |
| edit_guard:unsupported_character:65 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_character:7 | 1516 | 18 | 35 | 0 |
| edit_guard:unsupported_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_character:74 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:76 | 163 | 0 | 2 | 0 |
| edit_guard:unsupported_character:8 | 1285 | 11 | 31 | 0 |
| edit_guard:unsupported_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_character:9 | 1108 | 14 | 28 | 0 |
| edit_guard:unsupported_raw_character:0 | 7590 | 6 | 187 | 0 |
| edit_guard:unsupported_raw_character:1 | 3453 | 0 | 84 | 0 |
| edit_guard:unsupported_raw_character:10 | 1272 | 0 | 34 | 0 |
| edit_guard:unsupported_raw_character:11 | 687 | 0 | 18 | 0 |
| edit_guard:unsupported_raw_character:12 | 601 | 1 | 16 | 0 |
| edit_guard:unsupported_raw_character:13 | 917 | 0 | 28 | 0 |
| edit_guard:unsupported_raw_character:14 | 1084 | 0 | 30 | 0 |
| edit_guard:unsupported_raw_character:15 | 798 | 0 | 22 | 0 |
| edit_guard:unsupported_raw_character:16 | 719 | 0 | 22 | 0 |
| edit_guard:unsupported_raw_character:17 | 785 | 0 | 20 | 0 |
| edit_guard:unsupported_raw_character:18 | 955 | 0 | 24 | 0 |
| edit_guard:unsupported_raw_character:19 | 916 | 0 | 25 | 0 |
| edit_guard:unsupported_raw_character:2 | 1634 | 0 | 44 | 0 |
| edit_guard:unsupported_raw_character:20 | 1105 | 0 | 28 | 0 |
| edit_guard:unsupported_raw_character:21 | 820 | 0 | 23 | 0 |
| edit_guard:unsupported_raw_character:22 | 844 | 0 | 22 | 0 |
| edit_guard:unsupported_raw_character:23 | 1069 | 0 | 30 | 0 |
| edit_guard:unsupported_raw_character:24 | 782 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:25 | 678 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:26 | 1116 | 0 | 29 | 0 |
| edit_guard:unsupported_raw_character:27 | 1303 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:28 | 1411 | 0 | 36 | 0 |
| edit_guard:unsupported_raw_character:29 | 1742 | 1 | 45 | 0 |
| edit_guard:unsupported_raw_character:3 | 2330 | 0 | 61 | 0 |
| edit_guard:unsupported_raw_character:30 | 1155 | 1 | 32 | 0 |
| edit_guard:unsupported_raw_character:31 | 1482 | 0 | 37 | 0 |
| edit_guard:unsupported_raw_character:32 | 1198 | 0 | 31 | 0 |
| edit_guard:unsupported_raw_character:33 | 1122 | 1 | 28 | 0 |
| edit_guard:unsupported_raw_character:34 | 1399 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:35 | 1137 | 0 | 28 | 0 |
| edit_guard:unsupported_raw_character:36 | 1520 | 0 | 37 | 0 |
| edit_guard:unsupported_raw_character:37 | 1739 | 0 | 41 | 0 |
| edit_guard:unsupported_raw_character:38 | 990 | 1 | 24 | 0 |
| edit_guard:unsupported_raw_character:39 | 1530 | 0 | 34 | 0 |
| edit_guard:unsupported_raw_character:4 | 1280 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:40 | 1388 | 0 | 31 | 0 |
| edit_guard:unsupported_raw_character:41 | 1545 | 0 | 34 | 0 |
| edit_guard:unsupported_raw_character:42 | 1480 | 1 | 33 | 0 |
| edit_guard:unsupported_raw_character:43 | 1353 | 1 | 29 | 0 |
| edit_guard:unsupported_raw_character:44 | 825 | 1 | 18 | 0 |
| edit_guard:unsupported_raw_character:45 | 811 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:46 | 759 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:47 | 562 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:48 | 503 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:49 | 568 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:5 | 951 | 0 | 20 | 0 |
| edit_guard:unsupported_raw_character:50 | 399 | 1 | 8 | 0 |
| edit_guard:unsupported_raw_character:51 | 488 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:52 | 281 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:53 | 402 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:54 | 370 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:55 | 471 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:57 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:58 | 186 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:59 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:6 | 1058 | 0 | 28 | 0 |
| edit_guard:unsupported_raw_character:60 | 254 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:61 | 187 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:62 | 133 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:65 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 1507 | 0 | 34 | 0 |
| edit_guard:unsupported_raw_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:74 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:76 | 80 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 1187 | 0 | 28 | 0 |
| edit_guard:unsupported_raw_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:9 | 1214 | 0 | 30 | 0 |
| ensemble_ab_mark_set_disagreement | 13126 | 0 | 10199 | 301 |
| r1_B_evidence_UNKNOWN | 1567 | 0 | 1567 | 0 |
| r1_B_missing | 4770 | 0 | 2991 | 0 |
| r1_B_uncertainty:out_of_image_span | 1567 | 0 | 1567 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 149 | 0 | 9 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 1735 | 0 | 941 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 2886 | 0 | 2129 | 0 |
| r1_evidence_UNKNOWN | 1567 | 0 | 1567 | 0 |
| r1_missing | 4770 | 0 | 2991 | 0 |
| r1_uncertainty:out_of_image_span | 1567 | 0 | 1567 | 0 |
| r1_unscored:line_confidence_below_0.5 | 149 | 0 | 9 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 1735 | 0 | 941 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 2886 | 0 | 2129 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 71761 |
| clipping | 99259 |
| K1 | 5313 |
| edit-guard | 22877 |
| A/B disagreement | 10199 |
| kind disagreement | 0 |
| R1 uncertainty | 4502 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 17160 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 10379 |
| ["detector_clipped_top"] | 10297 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 6692 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 4760 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 4557 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 4037 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 4027 |
| ["detector_clipped_bottom"] | 2823 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 2219 |

### mixed / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 48 | 0 | 47 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 103 | 0 | 100 | 1 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 2 | 0 | 2 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:evidence_tie | 4 | 0 | 2 | 0 |
| K1:C3:two_accents:rule_held_back | 874 | 0 | 382 | 6 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 124 | 0 | 122 | 2 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 219 | 0 | 206 | 5 |
| detector_clipped_bottom | 15216 | 0 | 6417 | 342 |
| detector_clipped_top | 39943 | 0 | 8844 | 1454 |
| detector_localisation_unknown | 8743 | 0 | 3355 | 0 |
| detector_segmentation_uncertain | 17178 | 0 | 5101 | 297 |
| detector_unnamed_mark | 2410 | 0 | 1955 | 143 |
| edit_guard:base_or_character_mismatch | 389 | 1293 | 1293 | 22 |
| edit_guard:punctuation_mismatch | 1288 | 1509 | 1509 | 125 |
| edit_guard:unsupported_character:0 | 570 | 6 | 14 | 0 |
| edit_guard:unsupported_character:1 | 335 | 3 | 8 | 0 |
| edit_guard:unsupported_character:10 | 312 | 5 | 8 | 0 |
| edit_guard:unsupported_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 49 | 1 | 1 | 0 |
| edit_guard:unsupported_character:13 | 211 | 3 | 5 | 0 |
| edit_guard:unsupported_character:14 | 107 | 3 | 3 | 0 |
| edit_guard:unsupported_character:15 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:16 | 192 | 3 | 5 | 0 |
| edit_guard:unsupported_character:17 | 27 | 1 | 1 | 0 |
| edit_guard:unsupported_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:19 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_character:20 | 113 | 2 | 3 | 0 |
| edit_guard:unsupported_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_character:22 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_character:25 | 97 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 104 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 209 | 3 | 5 | 0 |
| edit_guard:unsupported_character:28 | 323 | 2 | 8 | 0 |
| edit_guard:unsupported_character:29 | 68 | 1 | 1 | 0 |
| edit_guard:unsupported_character:3 | 270 | 3 | 7 | 0 |
| edit_guard:unsupported_character:30 | 158 | 3 | 4 | 0 |
| edit_guard:unsupported_character:31 | 260 | 2 | 6 | 0 |
| edit_guard:unsupported_character:32 | 155 | 1 | 4 | 0 |
| edit_guard:unsupported_character:33 | 114 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_character:36 | 165 | 1 | 4 | 0 |
| edit_guard:unsupported_character:37 | 307 | 3 | 7 | 0 |
| edit_guard:unsupported_character:38 | 130 | 1 | 3 | 0 |
| edit_guard:unsupported_character:39 | 134 | 2 | 3 | 0 |
| edit_guard:unsupported_character:4 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_character:41 | 101 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 233 | 3 | 5 | 0 |
| edit_guard:unsupported_character:43 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:44 | 253 | 3 | 5 | 0 |
| edit_guard:unsupported_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_character:46 | 144 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 159 | 1 | 3 | 0 |
| edit_guard:unsupported_character:48 | 102 | 2 | 2 | 0 |
| edit_guard:unsupported_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_character:50 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:6 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 145 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 227 | 4 | 5 | 0 |
| edit_guard:unsupported_raw_character:0 | 563 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:1 | 335 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 312 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:13 | 211 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:14 | 156 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:16 | 192 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:17 | 27 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:19 | 97 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:20 | 113 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:25 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:26 | 131 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 209 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:28 | 323 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:29 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 270 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:30 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:31 | 260 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:32 | 155 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 114 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 165 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 307 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:38 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:4 | 130 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:41 | 101 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 233 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:44 | 253 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:46 | 144 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 159 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:48 | 102 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:50 | 57 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:8 | 227 | 0 | 5 | 0 |
| ensemble_ab_mark_set_disagreement | 1631 | 0 | 1252 | 35 |
| r1_B_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_B_missing | 440 | 0 | 249 | 0 |
| r1_B_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 151 | 0 | 56 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 269 | 0 | 201 | 0 |
| r1_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_missing | 440 | 0 | 249 | 0 |
| r1_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 151 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 269 | 0 | 201 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6062 |
| clipping | 9669 |
| K1 | 616 |
| edit-guard | 2239 |
| A/B disagreement | 1252 |
| kind disagreement | 0 |
| R1 uncertainty | 299 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2285 |
| ["detector_clipped_top"] | 1454 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 625 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 536 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 521 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 445 |
| ["detector_clipped_bottom"] | 342 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 329 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 297 |
| ["detector_segmentation_uncertain"] | 297 |

### openarchives / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 12 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_bottom | 366 | 0 | 118 | 27 |
| detector_clipped_top | 629 | 0 | 120 | 25 |
| detector_segmentation_uncertain | 110 | 0 | 38 | 9 |
| detector_unnamed_mark | 24 | 0 | 19 | 1 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 19 | 19 | 7 |
| ensemble_ab_mark_set_disagreement | 19 | 0 | 16 | 12 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 50 |
| clipping | 159 |
| K1 | 5 |
| edit-guard | 19 |
| A/B disagreement | 16 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 61 |
| ["detector_clipped_bottom"] | 27 |
| ["detector_clipped_top"] | 25 |
| ["ensemble_ab_mark_set_disagreement"] | 12 |
| ["detector_clipped_bottom","detector_segmentation_uncertain"] | 9 |
| ["detector_segmentation_uncertain"] | 9 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 7 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 7 |
| ["edit_guard:punctuation_mismatch"] | 7 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 5 |

### parliament / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 69 | 0 | 67 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 90 | 0 | 88 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C3:two_accents:evidence_tie | 14 | 0 | 7 | 0 |
| K1:C3:two_accents:rule_held_back | 1343 | 0 | 613 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 159 | 0 | 155 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 7 | 0 | 7 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 292 | 0 | 253 | 0 |
| detector_clipped_bottom | 44633 | 0 | 16119 | 183 |
| detector_clipped_top | 98404 | 0 | 20688 | 547 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 84 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 72 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 8 |
| edit_guard:punctuation_mismatch | 1472 | 2781 | 2781 | 16 |
| edit_guard:unsupported_character:0 | 1663 | 17 | 43 | 0 |
| edit_guard:unsupported_character:1 | 594 | 4 | 17 | 0 |
| edit_guard:unsupported_character:10 | 206 | 3 | 6 | 0 |
| edit_guard:unsupported_character:11 | 221 | 5 | 5 | 0 |
| edit_guard:unsupported_character:12 | 139 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 254 | 4 | 7 | 0 |
| edit_guard:unsupported_character:14 | 201 | 1 | 5 | 0 |
| edit_guard:unsupported_character:15 | 64 | 2 | 2 | 0 |
| edit_guard:unsupported_character:17 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:18 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:19 | 46 | 1 | 1 | 0 |
| edit_guard:unsupported_character:2 | 565 | 4 | 17 | 0 |
| edit_guard:unsupported_character:20 | 277 | 4 | 7 | 0 |
| edit_guard:unsupported_character:21 | 135 | 4 | 4 | 0 |
| edit_guard:unsupported_character:22 | 200 | 3 | 5 | 0 |
| edit_guard:unsupported_character:23 | 94 | 2 | 2 | 0 |
| edit_guard:unsupported_character:24 | 258 | 3 | 7 | 0 |
| edit_guard:unsupported_character:25 | 163 | 1 | 5 | 0 |
| edit_guard:unsupported_character:26 | 121 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 291 | 6 | 7 | 0 |
| edit_guard:unsupported_character:28 | 75 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 160 | 2 | 4 | 0 |
| edit_guard:unsupported_character:3 | 559 | 5 | 15 | 0 |
| edit_guard:unsupported_character:30 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:31 | 157 | 4 | 4 | 0 |
| edit_guard:unsupported_character:32 | 88 | 2 | 2 | 0 |
| edit_guard:unsupported_character:33 | 112 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 254 | 3 | 6 | 0 |
| edit_guard:unsupported_character:35 | 80 | 2 | 2 | 0 |
| edit_guard:unsupported_character:36 | 183 | 2 | 4 | 0 |
| edit_guard:unsupported_character:37 | 132 | 2 | 3 | 0 |
| edit_guard:unsupported_character:38 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:39 | 227 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 349 | 3 | 9 | 0 |
| edit_guard:unsupported_character:40 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:41 | 436 | 7 | 10 | 0 |
| edit_guard:unsupported_character:42 | 176 | 2 | 4 | 0 |
| edit_guard:unsupported_character:43 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:44 | 180 | 2 | 4 | 0 |
| edit_guard:unsupported_character:45 | 188 | 3 | 4 | 0 |
| edit_guard:unsupported_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_character:49 | 50 | 1 | 1 | 0 |
| edit_guard:unsupported_character:5 | 142 | 2 | 3 | 0 |
| edit_guard:unsupported_character:6 | 168 | 2 | 4 | 0 |
| edit_guard:unsupported_character:7 | 417 | 3 | 11 | 0 |
| edit_guard:unsupported_character:8 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:9 | 265 | 3 | 6 | 0 |
| edit_guard:unsupported_raw_character:0 | 1567 | 2 | 41 | 0 |
| edit_guard:unsupported_raw_character:1 | 521 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:10 | 206 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:11 | 221 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:12 | 139 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 254 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:14 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:15 | 64 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:17 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:18 | 179 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:19 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:2 | 546 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:20 | 277 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:21 | 135 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:22 | 200 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:23 | 142 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:24 | 210 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:25 | 163 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:26 | 121 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 291 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:28 | 75 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 191 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:3 | 559 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:30 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 157 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:32 | 88 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 112 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:34 | 254 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:35 | 80 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 183 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 132 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 227 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 349 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:40 | 222 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:41 | 393 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:42 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:43 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_raw_character:44 | 180 | 1 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 188 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:49 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 142 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:6 | 168 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 393 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:8 | 94 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:9 | 265 | 0 | 6 | 0 |
| ensemble_ab_mark_set_disagreement | 2014 | 0 | 1653 | 2 |
| r1_B_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_B_missing | 1452 | 0 | 955 | 0 |
| r1_B_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |
| r1_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_missing | 1452 | 0 | 955 | 0 |
| r1_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4765 |
| A/B disagreement | 1653 |
| kind disagreement | 0 |
| R1 uncertainty | 1829 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 5274 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 3467 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 2207 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 1803 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 1262 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain"] | 1214 |
| ["detector_clipped_bottom","detector_clipped_top"] | 838 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 651 |
| ["detector_clipped_top"] | 547 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 502 |

### round1 / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 1 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 3 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 2 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 1 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 29 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 1 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 3 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 1209 |
| detector_clipped_top | 140308 | 0 | 29544 | 4475 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 862 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 553 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 118 |
| edit_guard:punctuation_mismatch | 9153 | 6398 | 6398 | 450 |
| edit_guard:unsupported_character:0 | 3286 | 23 | 79 | 0 |
| edit_guard:unsupported_character:1 | 2211 | 16 | 47 | 0 |
| edit_guard:unsupported_character:10 | 439 | 5 | 12 | 0 |
| edit_guard:unsupported_character:11 | 317 | 3 | 9 | 0 |
| edit_guard:unsupported_character:12 | 144 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 283 | 6 | 9 | 0 |
| edit_guard:unsupported_character:14 | 407 | 9 | 13 | 0 |
| edit_guard:unsupported_character:15 | 470 | 7 | 14 | 0 |
| edit_guard:unsupported_character:16 | 268 | 3 | 7 | 0 |
| edit_guard:unsupported_character:17 | 383 | 4 | 9 | 0 |
| edit_guard:unsupported_character:18 | 295 | 3 | 8 | 0 |
| edit_guard:unsupported_character:19 | 337 | 3 | 10 | 0 |
| edit_guard:unsupported_character:2 | 409 | 4 | 11 | 0 |
| edit_guard:unsupported_character:20 | 535 | 6 | 13 | 0 |
| edit_guard:unsupported_character:21 | 407 | 4 | 12 | 0 |
| edit_guard:unsupported_character:22 | 427 | 8 | 11 | 0 |
| edit_guard:unsupported_character:23 | 668 | 7 | 19 | 0 |
| edit_guard:unsupported_character:24 | 469 | 7 | 11 | 0 |
| edit_guard:unsupported_character:25 | 228 | 3 | 7 | 0 |
| edit_guard:unsupported_character:26 | 599 | 6 | 15 | 0 |
| edit_guard:unsupported_character:27 | 636 | 6 | 17 | 0 |
| edit_guard:unsupported_character:28 | 581 | 6 | 17 | 0 |
| edit_guard:unsupported_character:29 | 1243 | 12 | 33 | 0 |
| edit_guard:unsupported_character:3 | 622 | 2 | 15 | 0 |
| edit_guard:unsupported_character:30 | 652 | 5 | 18 | 0 |
| edit_guard:unsupported_character:31 | 551 | 3 | 15 | 0 |
| edit_guard:unsupported_character:32 | 684 | 4 | 18 | 0 |
| edit_guard:unsupported_character:33 | 538 | 5 | 13 | 0 |
| edit_guard:unsupported_character:34 | 781 | 4 | 18 | 0 |
| edit_guard:unsupported_character:35 | 701 | 6 | 17 | 0 |
| edit_guard:unsupported_character:36 | 745 | 2 | 19 | 0 |
| edit_guard:unsupported_character:37 | 765 | 5 | 19 | 0 |
| edit_guard:unsupported_character:38 | 408 | 1 | 10 | 0 |
| edit_guard:unsupported_character:39 | 791 | 6 | 18 | 0 |
| edit_guard:unsupported_character:4 | 497 | 4 | 11 | 0 |
| edit_guard:unsupported_character:40 | 448 | 3 | 10 | 0 |
| edit_guard:unsupported_character:41 | 811 | 5 | 18 | 0 |
| edit_guard:unsupported_character:42 | 454 | 4 | 10 | 0 |
| edit_guard:unsupported_character:43 | 569 | 6 | 12 | 0 |
| edit_guard:unsupported_character:44 | 300 | 3 | 6 | 0 |
| edit_guard:unsupported_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_character:46 | 262 | 1 | 5 | 0 |
| edit_guard:unsupported_character:47 | 207 | 4 | 4 | 0 |
| edit_guard:unsupported_character:48 | 251 | 2 | 5 | 0 |
| edit_guard:unsupported_character:49 | 315 | 1 | 6 | 0 |
| edit_guard:unsupported_character:5 | 299 | 2 | 7 | 0 |
| edit_guard:unsupported_character:50 | 284 | 3 | 5 | 0 |
| edit_guard:unsupported_character:51 | 495 | 3 | 9 | 0 |
| edit_guard:unsupported_character:52 | 175 | 1 | 3 | 0 |
| edit_guard:unsupported_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_character:54 | 202 | 2 | 3 | 0 |
| edit_guard:unsupported_character:55 | 247 | 2 | 4 | 0 |
| edit_guard:unsupported_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_character:57 | 202 | 1 | 3 | 0 |
| edit_guard:unsupported_character:58 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:59 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 421 | 2 | 12 | 0 |
| edit_guard:unsupported_character:60 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_character:62 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:65 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 431 | 3 | 9 | 0 |
| edit_guard:unsupported_character:74 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:8 | 618 | 4 | 15 | 0 |
| edit_guard:unsupported_character:9 | 433 | 4 | 11 | 0 |
| edit_guard:unsupported_raw_character:0 | 3282 | 1 | 78 | 0 |
| edit_guard:unsupported_raw_character:1 | 1715 | 0 | 40 | 0 |
| edit_guard:unsupported_raw_character:10 | 439 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:11 | 339 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:12 | 144 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:13 | 283 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:14 | 424 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:15 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:16 | 302 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:17 | 383 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:18 | 317 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:19 | 379 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:2 | 409 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:20 | 535 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:21 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:22 | 427 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:23 | 668 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:24 | 469 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:25 | 228 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:26 | 599 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:27 | 636 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:28 | 581 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:29 | 1243 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:3 | 644 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:30 | 652 | 1 | 19 | 0 |
| edit_guard:unsupported_raw_character:31 | 551 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:32 | 718 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:33 | 543 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:34 | 742 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:35 | 701 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:36 | 745 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:37 | 806 | 0 | 20 | 0 |
| edit_guard:unsupported_raw_character:38 | 402 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:39 | 831 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:4 | 497 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:40 | 448 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:41 | 811 | 0 | 18 | 0 |
| edit_guard:unsupported_raw_character:42 | 454 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:43 | 569 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:44 | 300 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:46 | 262 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:47 | 207 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:48 | 251 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:49 | 315 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:5 | 270 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 233 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 436 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:52 | 175 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:54 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:55 | 247 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:57 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:58 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:59 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 421 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:60 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:62 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:65 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 471 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:74 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 545 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:9 | 433 | 0 | 11 | 0 |
| ensemble_ab_mark_set_disagreement | 5515 | 0 | 4277 | 152 |
| r1_B_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_B_missing | 1687 | 0 | 1129 | 0 |
| r1_B_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |
| r1_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_missing | 1687 | 0 | 1129 | 0 |
| r1_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9251 |
| A/B disagreement | 4277 |
| kind disagreement | 0 |
| R1 uncertainty | 1276 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 7199 |
| ["detector_clipped_top"] | 4475 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 2210 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 1544 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 1461 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1425 |
| ["detector_clipped_bottom"] | 1209 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 1019 |
| ["detector_segmentation_uncertain"] | 862 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 828 |

### round2 / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 84 | 0 | 81 | 2 |
| K1:C1:breathing_not_initial:impossible_by_rule | 107 | 0 | 103 | 3 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 6 | 0 | 3 | 0 |
| K1:C3:two_accents:rule_held_back | 1020 | 0 | 467 | 8 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 101 | 0 | 98 | 1 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 2 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 511 |
| detector_clipped_top | 48664 | 0 | 10763 | 1916 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 381 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 324 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 59 |
| edit_guard:punctuation_mismatch | 1491 | 2095 | 2095 | 207 |
| edit_guard:unsupported_character:0 | 1107 | 12 | 28 | 0 |
| edit_guard:unsupported_character:1 | 360 | 2 | 9 | 0 |
| edit_guard:unsupported_character:10 | 169 | 1 | 4 | 0 |
| edit_guard:unsupported_character:11 | 54 | 1 | 1 | 0 |
| edit_guard:unsupported_character:12 | 178 | 3 | 5 | 0 |
| edit_guard:unsupported_character:13 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_character:14 | 169 | 2 | 4 | 0 |
| edit_guard:unsupported_character:15 | 122 | 3 | 3 | 0 |
| edit_guard:unsupported_character:16 | 225 | 1 | 8 | 0 |
| edit_guard:unsupported_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_character:18 | 252 | 3 | 7 | 0 |
| edit_guard:unsupported_character:19 | 108 | 1 | 3 | 0 |
| edit_guard:unsupported_character:2 | 238 | 4 | 6 | 0 |
| edit_guard:unsupported_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_character:21 | 129 | 1 | 4 | 0 |
| edit_guard:unsupported_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_character:23 | 43 | 1 | 1 | 0 |
| edit_guard:unsupported_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_character:27 | 150 | 3 | 4 | 0 |
| edit_guard:unsupported_character:28 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 71 | 0 | 2 | 0 |
| edit_guard:unsupported_character:3 | 236 | 3 | 6 | 0 |
| edit_guard:unsupported_character:30 | 225 | 3 | 6 | 0 |
| edit_guard:unsupported_character:31 | 201 | 3 | 5 | 0 |
| edit_guard:unsupported_character:32 | 79 | 1 | 2 | 0 |
| edit_guard:unsupported_character:33 | 250 | 2 | 6 | 0 |
| edit_guard:unsupported_character:34 | 116 | 1 | 3 | 0 |
| edit_guard:unsupported_character:35 | 152 | 1 | 4 | 0 |
| edit_guard:unsupported_character:36 | 212 | 2 | 5 | 0 |
| edit_guard:unsupported_character:37 | 356 | 5 | 8 | 0 |
| edit_guard:unsupported_character:38 | 192 | 4 | 4 | 0 |
| edit_guard:unsupported_character:39 | 98 | 2 | 2 | 0 |
| edit_guard:unsupported_character:4 | 63 | 1 | 2 | 0 |
| edit_guard:unsupported_character:40 | 87 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 241 | 2 | 5 | 0 |
| edit_guard:unsupported_character:43 | 92 | 1 | 2 | 0 |
| edit_guard:unsupported_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_character:45 | 51 | 1 | 1 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_character:5 | 121 | 3 | 3 | 0 |
| edit_guard:unsupported_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_character:53 | 113 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_character:59 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 165 | 4 | 5 | 0 |
| edit_guard:unsupported_character:60 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 173 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 145 | 1 | 4 | 0 |
| edit_guard:unsupported_character:9 | 114 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:0 | 1012 | 0 | 26 | 0 |
| edit_guard:unsupported_raw_character:1 | 341 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 54 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 178 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:13 | 96 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:14 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 122 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:16 | 225 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 252 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:19 | 108 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:2 | 238 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:21 | 98 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:23 | 43 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:28 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 41 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 236 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:30 | 193 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:31 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:32 | 79 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 250 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:34 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:35 | 152 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:36 | 212 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 356 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:38 | 192 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:4 | 79 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 241 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 92 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 148 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 113 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:59 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 165 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:60 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 148 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:8 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:9 | 114 | 0 | 4 | 0 |
| ensemble_ab_mark_set_disagreement | 1770 | 0 | 1426 | 80 |
| r1_B_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_B_missing | 434 | 0 | 268 | 0 |
| r1_B_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |
| r1_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_missing | 434 | 0 | 268 | 0 |
| r1_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3059 |
| A/B disagreement | 1426 |
| kind disagreement | 0 |
| R1 uncertainty | 354 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2870 |
| ["detector_clipped_top"] | 1916 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 590 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 544 |
| ["detector_clipped_bottom"] | 511 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 448 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 405 |
| ["detector_segmentation_uncertain"] | 381 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 356 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 326 |

### vouli / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 86 | 0 | 83 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 130 | 0 | 120 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 3 | 0 | 3 | 0 |
| K1:C3:two_accents:evidence_tie | 18 | 0 | 9 | 0 |
| K1:C3:two_accents:rule_held_back | 1597 | 0 | 641 | 4 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 200 | 0 | 181 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 12 | 0 | 10 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 281 | 0 | 258 | 0 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 2 | 0 | 2 | 0 |
| detector_clipped_bottom | 40732 | 0 | 15658 | 551 |
| detector_clipped_top | 93007 | 0 | 19927 | 1880 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 102 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 148 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 13 |
| edit_guard:punctuation_mismatch | 3437 | 2268 | 2268 | 71 |
| edit_guard:unsupported_character:0 | 1166 | 8 | 25 | 0 |
| edit_guard:unsupported_character:1 | 510 | 3 | 12 | 0 |
| edit_guard:unsupported_character:10 | 146 | 2 | 4 | 0 |
| edit_guard:unsupported_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_character:15 | 112 | 2 | 3 | 0 |
| edit_guard:unsupported_character:17 | 256 | 4 | 7 | 0 |
| edit_guard:unsupported_character:18 | 156 | 1 | 3 | 0 |
| edit_guard:unsupported_character:19 | 309 | 3 | 8 | 0 |
| edit_guard:unsupported_character:2 | 313 | 1 | 8 | 0 |
| edit_guard:unsupported_character:20 | 40 | 1 | 1 | 0 |
| edit_guard:unsupported_character:21 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:22 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:23 | 72 | 1 | 2 | 0 |
| edit_guard:unsupported_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_character:25 | 91 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 171 | 2 | 4 | 0 |
| edit_guard:unsupported_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_character:28 | 222 | 4 | 5 | 0 |
| edit_guard:unsupported_character:29 | 169 | 3 | 3 | 0 |
| edit_guard:unsupported_character:3 | 657 | 1 | 18 | 0 |
| edit_guard:unsupported_character:30 | 78 | 1 | 2 | 0 |
| edit_guard:unsupported_character:31 | 313 | 2 | 7 | 0 |
| edit_guard:unsupported_character:32 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:33 | 145 | 0 | 3 | 0 |
| edit_guard:unsupported_character:34 | 213 | 2 | 5 | 0 |
| edit_guard:unsupported_character:35 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:36 | 215 | 3 | 5 | 0 |
| edit_guard:unsupported_character:37 | 138 | 1 | 3 | 0 |
| edit_guard:unsupported_character:38 | 94 | 1 | 2 | 0 |
| edit_guard:unsupported_character:39 | 240 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 225 | 3 | 7 | 0 |
| edit_guard:unsupported_character:40 | 426 | 2 | 9 | 0 |
| edit_guard:unsupported_character:41 | 240 | 2 | 5 | 0 |
| edit_guard:unsupported_character:42 | 327 | 3 | 7 | 0 |
| edit_guard:unsupported_character:43 | 412 | 4 | 8 | 0 |
| edit_guard:unsupported_character:44 | 47 | 1 | 1 | 0 |
| edit_guard:unsupported_character:45 | 189 | 1 | 3 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:48 | 100 | 2 | 2 | 0 |
| edit_guard:unsupported_character:49 | 203 | 2 | 4 | 0 |
| edit_guard:unsupported_character:5 | 345 | 2 | 6 | 0 |
| edit_guard:unsupported_character:50 | 109 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_character:6 | 251 | 1 | 6 | 0 |
| edit_guard:unsupported_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_character:7 | 350 | 4 | 7 | 0 |
| edit_guard:unsupported_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_character:76 | 163 | 0 | 2 | 0 |
| edit_guard:unsupported_character:8 | 176 | 1 | 4 | 0 |
| edit_guard:unsupported_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_character:9 | 296 | 6 | 7 | 0 |
| edit_guard:unsupported_raw_character:0 | 1166 | 3 | 28 | 0 |
| edit_guard:unsupported_raw_character:1 | 541 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:10 | 146 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:15 | 112 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:17 | 256 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:18 | 156 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:19 | 286 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:2 | 266 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:20 | 40 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:21 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:23 | 72 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:25 | 131 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 346 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:29 | 169 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:3 | 621 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:30 | 78 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 313 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:32 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 103 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:34 | 213 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:35 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:36 | 215 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 138 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:39 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 225 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:40 | 374 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:41 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:42 | 376 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:43 | 412 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:44 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 189 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:48 | 100 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:49 | 203 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:5 | 345 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 109 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:6 | 251 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 350 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:76 | 80 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:9 | 402 | 0 | 9 | 0 |
| ensemble_ab_mark_set_disagreement | 2177 | 0 | 1575 | 20 |
| r1_B_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_B_missing | 757 | 0 | 390 | 0 |
| r1_B_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |
| r1_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_missing | 757 | 0 | 390 | 0 |
| r1_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3544 |
| A/B disagreement | 1575 |
| kind disagreement | 0 |
| R1 uncertainty | 744 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 3907 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 2646 |
| ["detector_clipped_top"] | 1880 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1726 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1029 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 976 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 930 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark"] | 662 |
| ["detector_clipped_top","detector_unnamed_mark"] | 650 |
| ["detector_clipped_bottom"] | 551 |

### ALL / anemi_mixed

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 48 | 0 | 47 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 102 | 0 | 99 | 1 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 2 | 0 | 2 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:evidence_tie | 4 | 0 | 2 | 0 |
| K1:C3:two_accents:rule_held_back | 868 | 0 | 379 | 6 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 123 | 0 | 121 | 1 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 214 | 0 | 201 | 5 |
| detector_clipped_bottom | 15059 | 0 | 6360 | 338 |
| detector_clipped_top | 39633 | 0 | 8777 | 1443 |
| detector_localisation_unknown | 8716 | 0 | 3345 | 0 |
| detector_segmentation_uncertain | 17133 | 0 | 5085 | 297 |
| detector_unnamed_mark | 2392 | 0 | 1939 | 140 |
| edit_guard:base_or_character_mismatch | 389 | 1258 | 1258 | 20 |
| edit_guard:punctuation_mismatch | 1184 | 1470 | 1470 | 119 |
| edit_guard:unsupported_character:0 | 570 | 6 | 14 | 0 |
| edit_guard:unsupported_character:1 | 335 | 3 | 8 | 0 |
| edit_guard:unsupported_character:10 | 312 | 5 | 8 | 0 |
| edit_guard:unsupported_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 49 | 1 | 1 | 0 |
| edit_guard:unsupported_character:13 | 211 | 3 | 5 | 0 |
| edit_guard:unsupported_character:14 | 107 | 3 | 3 | 0 |
| edit_guard:unsupported_character:15 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:16 | 192 | 3 | 5 | 0 |
| edit_guard:unsupported_character:17 | 27 | 1 | 1 | 0 |
| edit_guard:unsupported_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:19 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_character:20 | 113 | 2 | 3 | 0 |
| edit_guard:unsupported_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_character:22 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_character:25 | 97 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 104 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 209 | 3 | 5 | 0 |
| edit_guard:unsupported_character:28 | 288 | 2 | 7 | 0 |
| edit_guard:unsupported_character:29 | 68 | 1 | 1 | 0 |
| edit_guard:unsupported_character:3 | 270 | 3 | 7 | 0 |
| edit_guard:unsupported_character:30 | 158 | 3 | 4 | 0 |
| edit_guard:unsupported_character:31 | 260 | 2 | 6 | 0 |
| edit_guard:unsupported_character:32 | 155 | 1 | 4 | 0 |
| edit_guard:unsupported_character:33 | 114 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_character:36 | 165 | 1 | 4 | 0 |
| edit_guard:unsupported_character:37 | 307 | 3 | 7 | 0 |
| edit_guard:unsupported_character:38 | 130 | 1 | 3 | 0 |
| edit_guard:unsupported_character:39 | 134 | 2 | 3 | 0 |
| edit_guard:unsupported_character:4 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_character:41 | 101 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 233 | 3 | 5 | 0 |
| edit_guard:unsupported_character:43 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:44 | 253 | 3 | 5 | 0 |
| edit_guard:unsupported_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_character:46 | 144 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 102 | 1 | 2 | 0 |
| edit_guard:unsupported_character:48 | 102 | 2 | 2 | 0 |
| edit_guard:unsupported_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_character:50 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_character:6 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 145 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 227 | 4 | 5 | 0 |
| edit_guard:unsupported_raw_character:0 | 563 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:1 | 335 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 312 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:13 | 211 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:14 | 156 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:16 | 192 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:17 | 27 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:19 | 97 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:20 | 113 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:25 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:26 | 131 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 209 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:28 | 288 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:29 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 270 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:30 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:31 | 260 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:32 | 155 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 114 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 165 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 307 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:38 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:4 | 130 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:41 | 101 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 233 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:44 | 253 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:46 | 144 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 102 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:48 | 102 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:50 | 57 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:8 | 227 | 0 | 5 | 0 |
| ensemble_ab_mark_set_disagreement | 1607 | 0 | 1231 | 35 |
| r1_B_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_B_missing | 418 | 0 | 244 | 0 |
| r1_B_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 132 | 0 | 51 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 266 | 0 | 200 | 0 |
| r1_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_missing | 418 | 0 | 244 | 0 |
| r1_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 132 | 0 | 51 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 266 | 0 | 200 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6032 |
| clipping | 9594 |
| K1 | 609 |
| edit-guard | 2191 |
| A/B disagreement | 1231 |
| kind disagreement | 0 |
| R1 uncertainty | 294 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2260 |
| ["detector_clipped_top"] | 1443 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 625 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 535 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 515 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 445 |
| ["detector_clipped_bottom"] | 338 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 328 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 297 |
| ["detector_segmentation_uncertain"] | 297 |

### ALL / anemi_round1

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 1 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 3 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 2 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 1 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 29 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 1 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 3 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 1209 |
| detector_clipped_top | 140308 | 0 | 29544 | 4475 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 862 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 553 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 118 |
| edit_guard:punctuation_mismatch | 9153 | 6398 | 6398 | 450 |
| edit_guard:unsupported_character:0 | 3286 | 23 | 79 | 0 |
| edit_guard:unsupported_character:1 | 2211 | 16 | 47 | 0 |
| edit_guard:unsupported_character:10 | 439 | 5 | 12 | 0 |
| edit_guard:unsupported_character:11 | 317 | 3 | 9 | 0 |
| edit_guard:unsupported_character:12 | 144 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 283 | 6 | 9 | 0 |
| edit_guard:unsupported_character:14 | 407 | 9 | 13 | 0 |
| edit_guard:unsupported_character:15 | 470 | 7 | 14 | 0 |
| edit_guard:unsupported_character:16 | 268 | 3 | 7 | 0 |
| edit_guard:unsupported_character:17 | 383 | 4 | 9 | 0 |
| edit_guard:unsupported_character:18 | 295 | 3 | 8 | 0 |
| edit_guard:unsupported_character:19 | 337 | 3 | 10 | 0 |
| edit_guard:unsupported_character:2 | 409 | 4 | 11 | 0 |
| edit_guard:unsupported_character:20 | 535 | 6 | 13 | 0 |
| edit_guard:unsupported_character:21 | 407 | 4 | 12 | 0 |
| edit_guard:unsupported_character:22 | 427 | 8 | 11 | 0 |
| edit_guard:unsupported_character:23 | 668 | 7 | 19 | 0 |
| edit_guard:unsupported_character:24 | 469 | 7 | 11 | 0 |
| edit_guard:unsupported_character:25 | 228 | 3 | 7 | 0 |
| edit_guard:unsupported_character:26 | 599 | 6 | 15 | 0 |
| edit_guard:unsupported_character:27 | 636 | 6 | 17 | 0 |
| edit_guard:unsupported_character:28 | 581 | 6 | 17 | 0 |
| edit_guard:unsupported_character:29 | 1243 | 12 | 33 | 0 |
| edit_guard:unsupported_character:3 | 622 | 2 | 15 | 0 |
| edit_guard:unsupported_character:30 | 652 | 5 | 18 | 0 |
| edit_guard:unsupported_character:31 | 551 | 3 | 15 | 0 |
| edit_guard:unsupported_character:32 | 684 | 4 | 18 | 0 |
| edit_guard:unsupported_character:33 | 538 | 5 | 13 | 0 |
| edit_guard:unsupported_character:34 | 781 | 4 | 18 | 0 |
| edit_guard:unsupported_character:35 | 701 | 6 | 17 | 0 |
| edit_guard:unsupported_character:36 | 745 | 2 | 19 | 0 |
| edit_guard:unsupported_character:37 | 765 | 5 | 19 | 0 |
| edit_guard:unsupported_character:38 | 408 | 1 | 10 | 0 |
| edit_guard:unsupported_character:39 | 791 | 6 | 18 | 0 |
| edit_guard:unsupported_character:4 | 497 | 4 | 11 | 0 |
| edit_guard:unsupported_character:40 | 448 | 3 | 10 | 0 |
| edit_guard:unsupported_character:41 | 811 | 5 | 18 | 0 |
| edit_guard:unsupported_character:42 | 454 | 4 | 10 | 0 |
| edit_guard:unsupported_character:43 | 569 | 6 | 12 | 0 |
| edit_guard:unsupported_character:44 | 300 | 3 | 6 | 0 |
| edit_guard:unsupported_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_character:46 | 262 | 1 | 5 | 0 |
| edit_guard:unsupported_character:47 | 207 | 4 | 4 | 0 |
| edit_guard:unsupported_character:48 | 251 | 2 | 5 | 0 |
| edit_guard:unsupported_character:49 | 315 | 1 | 6 | 0 |
| edit_guard:unsupported_character:5 | 299 | 2 | 7 | 0 |
| edit_guard:unsupported_character:50 | 284 | 3 | 5 | 0 |
| edit_guard:unsupported_character:51 | 495 | 3 | 9 | 0 |
| edit_guard:unsupported_character:52 | 175 | 1 | 3 | 0 |
| edit_guard:unsupported_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_character:54 | 202 | 2 | 3 | 0 |
| edit_guard:unsupported_character:55 | 247 | 2 | 4 | 0 |
| edit_guard:unsupported_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_character:57 | 202 | 1 | 3 | 0 |
| edit_guard:unsupported_character:58 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:59 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 421 | 2 | 12 | 0 |
| edit_guard:unsupported_character:60 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_character:62 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:65 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 431 | 3 | 9 | 0 |
| edit_guard:unsupported_character:74 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:8 | 618 | 4 | 15 | 0 |
| edit_guard:unsupported_character:9 | 433 | 4 | 11 | 0 |
| edit_guard:unsupported_raw_character:0 | 3282 | 1 | 78 | 0 |
| edit_guard:unsupported_raw_character:1 | 1715 | 0 | 40 | 0 |
| edit_guard:unsupported_raw_character:10 | 439 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:11 | 339 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:12 | 144 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:13 | 283 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:14 | 424 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:15 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:16 | 302 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:17 | 383 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:18 | 317 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:19 | 379 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:2 | 409 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:20 | 535 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:21 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:22 | 427 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:23 | 668 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:24 | 469 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:25 | 228 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:26 | 599 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:27 | 636 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:28 | 581 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:29 | 1243 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:3 | 644 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:30 | 652 | 1 | 19 | 0 |
| edit_guard:unsupported_raw_character:31 | 551 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:32 | 718 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:33 | 543 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:34 | 742 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:35 | 701 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:36 | 745 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:37 | 806 | 0 | 20 | 0 |
| edit_guard:unsupported_raw_character:38 | 402 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:39 | 831 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:4 | 497 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:40 | 448 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:41 | 811 | 0 | 18 | 0 |
| edit_guard:unsupported_raw_character:42 | 454 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:43 | 569 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:44 | 300 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:46 | 262 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:47 | 207 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:48 | 251 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:49 | 315 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:5 | 270 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 233 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 436 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:52 | 175 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:54 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:55 | 247 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:57 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:58 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:59 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 421 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:60 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:62 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:65 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 471 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:74 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 545 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:9 | 433 | 0 | 11 | 0 |
| ensemble_ab_mark_set_disagreement | 5515 | 0 | 4277 | 152 |
| r1_B_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_B_missing | 1687 | 0 | 1129 | 0 |
| r1_B_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |
| r1_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_missing | 1687 | 0 | 1129 | 0 |
| r1_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9251 |
| A/B disagreement | 4277 |
| kind disagreement | 0 |
| R1 uncertainty | 1276 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 7199 |
| ["detector_clipped_top"] | 4475 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 2210 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 1544 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 1461 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1425 |
| ["detector_clipped_bottom"] | 1209 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 1019 |
| ["detector_segmentation_uncertain"] | 862 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 828 |

### ALL / anemi_round2

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 84 | 0 | 81 | 2 |
| K1:C1:breathing_not_initial:impossible_by_rule | 107 | 0 | 103 | 3 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 6 | 0 | 3 | 0 |
| K1:C3:two_accents:rule_held_back | 1020 | 0 | 467 | 8 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 101 | 0 | 98 | 1 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 2 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 511 |
| detector_clipped_top | 48664 | 0 | 10763 | 1916 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 381 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 324 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 59 |
| edit_guard:punctuation_mismatch | 1491 | 2095 | 2095 | 207 |
| edit_guard:unsupported_character:0 | 1107 | 12 | 28 | 0 |
| edit_guard:unsupported_character:1 | 360 | 2 | 9 | 0 |
| edit_guard:unsupported_character:10 | 169 | 1 | 4 | 0 |
| edit_guard:unsupported_character:11 | 54 | 1 | 1 | 0 |
| edit_guard:unsupported_character:12 | 178 | 3 | 5 | 0 |
| edit_guard:unsupported_character:13 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_character:14 | 169 | 2 | 4 | 0 |
| edit_guard:unsupported_character:15 | 122 | 3 | 3 | 0 |
| edit_guard:unsupported_character:16 | 225 | 1 | 8 | 0 |
| edit_guard:unsupported_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_character:18 | 252 | 3 | 7 | 0 |
| edit_guard:unsupported_character:19 | 108 | 1 | 3 | 0 |
| edit_guard:unsupported_character:2 | 238 | 4 | 6 | 0 |
| edit_guard:unsupported_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_character:21 | 129 | 1 | 4 | 0 |
| edit_guard:unsupported_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_character:23 | 43 | 1 | 1 | 0 |
| edit_guard:unsupported_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_character:27 | 150 | 3 | 4 | 0 |
| edit_guard:unsupported_character:28 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 71 | 0 | 2 | 0 |
| edit_guard:unsupported_character:3 | 236 | 3 | 6 | 0 |
| edit_guard:unsupported_character:30 | 225 | 3 | 6 | 0 |
| edit_guard:unsupported_character:31 | 201 | 3 | 5 | 0 |
| edit_guard:unsupported_character:32 | 79 | 1 | 2 | 0 |
| edit_guard:unsupported_character:33 | 250 | 2 | 6 | 0 |
| edit_guard:unsupported_character:34 | 116 | 1 | 3 | 0 |
| edit_guard:unsupported_character:35 | 152 | 1 | 4 | 0 |
| edit_guard:unsupported_character:36 | 212 | 2 | 5 | 0 |
| edit_guard:unsupported_character:37 | 356 | 5 | 8 | 0 |
| edit_guard:unsupported_character:38 | 192 | 4 | 4 | 0 |
| edit_guard:unsupported_character:39 | 98 | 2 | 2 | 0 |
| edit_guard:unsupported_character:4 | 63 | 1 | 2 | 0 |
| edit_guard:unsupported_character:40 | 87 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 241 | 2 | 5 | 0 |
| edit_guard:unsupported_character:43 | 92 | 1 | 2 | 0 |
| edit_guard:unsupported_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_character:45 | 51 | 1 | 1 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_character:5 | 121 | 3 | 3 | 0 |
| edit_guard:unsupported_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_character:53 | 113 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_character:59 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 165 | 4 | 5 | 0 |
| edit_guard:unsupported_character:60 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 173 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 145 | 1 | 4 | 0 |
| edit_guard:unsupported_character:9 | 114 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:0 | 1012 | 0 | 26 | 0 |
| edit_guard:unsupported_raw_character:1 | 341 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 54 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 178 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:13 | 96 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:14 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 122 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:16 | 225 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 252 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:19 | 108 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:2 | 238 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:21 | 98 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:23 | 43 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:28 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 41 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 236 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:30 | 193 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:31 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:32 | 79 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 250 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:34 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:35 | 152 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:36 | 212 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 356 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:38 | 192 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:4 | 79 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 241 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 92 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 148 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 113 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:59 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 165 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:60 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 148 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:8 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:9 | 114 | 0 | 4 | 0 |
| ensemble_ab_mark_set_disagreement | 1770 | 0 | 1426 | 80 |
| r1_B_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_B_missing | 434 | 0 | 268 | 0 |
| r1_B_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |
| r1_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_missing | 434 | 0 | 268 | 0 |
| r1_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3059 |
| A/B disagreement | 1426 |
| kind disagreement | 0 |
| R1 uncertainty | 354 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2870 |
| ["detector_clipped_top"] | 1916 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 590 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 544 |
| ["detector_clipped_bottom"] | 511 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 448 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 405 |
| ["detector_segmentation_uncertain"] | 381 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 356 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 326 |

### ALL / archive_b28038630

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 2 | 0 | 1 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 1 | 0 | 1 | 1 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 130 | 0 | 45 | 2 |
| detector_clipped_top | 254 | 0 | 58 | 11 |
| detector_localisation_unknown | 7 | 0 | 6 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 1 |
| edit_guard:base_or_character_mismatch | 0 | 13 | 13 | 0 |
| edit_guard:punctuation_mismatch | 0 | 22 | 22 | 5 |
| ensemble_ab_mark_set_disagreement | 12 | 0 | 12 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 13 |
| clipping | 61 |
| K1 | 3 |
| edit-guard | 24 |
| A/B disagreement | 12 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 21 |
| ["detector_clipped_top"] | 11 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 6 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch"] | 5 |
| ["edit_guard:punctuation_mismatch"] | 5 |
| ["detector_clipped_bottom","detector_clipped_top","ensemble_ab_mark_set_disagreement"] | 4 |
| ["detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch"] | 3 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:punctuation_mismatch"] | 2 |
| ["detector_clipped_bottom"] | 2 |
| ["K1:C3:two_accents:rule_held_back","detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement"] | 1 |

### ALL / openarchives_Pandemos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_clipped_bottom | 366 | 0 | 118 | 27 |
| detector_clipped_top | 604 | 0 | 118 | 25 |
| detector_segmentation_uncertain | 100 | 0 | 35 | 6 |
| detector_unnamed_mark | 23 | 0 | 18 | 1 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 9 | 9 | 0 |
| ensemble_ab_mark_set_disagreement | 2 | 0 | 2 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 46 |
| clipping | 157 |
| K1 | 0 |
| edit-guard | 9 |
| A/B disagreement | 2 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 61 |
| ["detector_clipped_bottom"] | 27 |
| ["detector_clipped_top"] | 25 |
| ["detector_clipped_bottom","detector_segmentation_uncertain"] | 9 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 7 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 7 |
| ["detector_segmentation_uncertain"] | 6 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 5 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch"] | 2 |

### ALL / openarchives_kallipos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 12 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_top | 25 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 10 | 0 | 3 | 3 |
| detector_unnamed_mark | 1 | 0 | 1 | 0 |
| edit_guard:punctuation_mismatch | 0 | 10 | 10 | 7 |
| ensemble_ab_mark_set_disagreement | 17 | 0 | 14 | 12 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 2 |
| K1 | 5 |
| edit-guard | 10 |
| A/B disagreement | 14 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["ensemble_ab_mark_set_disagreement"] | 12 |
| ["edit_guard:punctuation_mismatch"] | 7 |
| ["detector_segmentation_uncertain"] | 3 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule"] | 2 |
| ["detector_clipped_top","edit_guard:punctuation_mismatch"] | 2 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_unnamed_mark"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement"] | 1 |
| ["K1:C3:two_accents:rule_held_back","ensemble_ab_mark_set_disagreement"] | 1 |

### ALL / openarchives_mixed_Pandemos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_clipped_bottom | 16 | 0 | 7 | 2 |
| detector_clipped_top | 27 | 0 | 4 | 0 |
| detector_localisation_unknown | 5 | 0 | 1 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 2 | 0 |
| detector_unnamed_mark | 3 | 0 | 3 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 1 | 1 | 0 |
| edit_guard:punctuation_mismatch | 0 | 1 | 1 | 0 |
| ensemble_ab_mark_set_disagreement | 1 | 0 | 1 | 0 |
| r1_B_missing | 1 | 0 | 1 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 1 | 0 | 1 | 0 |
| r1_missing | 1 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 7 |
| K1 | 0 |
| edit-guard | 2 |
| A/B disagreement | 1 |
| kind disagreement | 0 |
| R1 uncertainty | 1 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 4 |
| ["detector_clipped_bottom"] | 2 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","detector_unnamed_mark"] | 1 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |
| ["detector_unnamed_mark","edit_guard:punctuation_mismatch"] | 1 |
| ["detector_unnamed_mark","ensemble_ab_mark_set_disagreement"] | 1 |

### ALL / openarchives_mixed_apothesis

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|

| Family | Lines held |
|---|---:|
| localisation/segmentation | 0 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|

### ALL / openarchives_mixed_ktisis

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_unnamed_mark | 1 | 0 | 1 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 1 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_unnamed_mark"] | 1 |

### ALL / openarchives_mixed_ntua

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_not_initial:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:rule_held_back | 4 | 0 | 2 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_bottom | 11 | 0 | 5 | 0 |
| detector_clipped_top | 29 | 0 | 5 | 0 |
| detector_localisation_unknown | 15 | 0 | 3 | 0 |
| detector_segmentation_uncertain | 27 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 1 |
| edit_guard:base_or_character_mismatch | 0 | 21 | 21 | 2 |
| edit_guard:punctuation_mismatch | 104 | 16 | 16 | 1 |
| edit_guard:unsupported_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| ensemble_ab_mark_set_disagreement | 11 | 0 | 8 | 0 |
| r1_B_missing | 21 | 0 | 4 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 18 | 0 | 4 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 3 | 0 | 1 | 0 |
| r1_missing | 21 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 18 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 3 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 12 |
| clipping | 7 |
| K1 | 4 |
| edit-guard | 22 |
| A/B disagreement | 8 |
| kind disagreement | 0 |
| R1 uncertainty | 4 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch"] | 5 |
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement"] | 2 |
| ["edit_guard:base_or_character_mismatch"] | 2 |
| ["K1:C1:breathing_not_initial:impossible_by_rule","K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","edit_guard:unsupported_character:28","edit_guard:unsupported_raw_character:28","ensemble_ab_mark_set_disagreement","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_B_unscored:width_outside_0.2_2.0_median_ctc","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","r1_unscored:width_outside_0.2_2.0_median_ctc"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","ensemble_ab_mark_set_disagreement"] | 1 |
| ["detector_clipped_bottom","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |

### ALL / parliament_proceedings_1975_2000

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 69 | 0 | 67 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 90 | 0 | 88 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C3:two_accents:evidence_tie | 14 | 0 | 7 | 0 |
| K1:C3:two_accents:rule_held_back | 1343 | 0 | 613 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 159 | 0 | 155 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 7 | 0 | 7 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 292 | 0 | 253 | 0 |
| detector_clipped_bottom | 44633 | 0 | 16119 | 183 |
| detector_clipped_top | 98404 | 0 | 20688 | 547 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 84 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 72 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 8 |
| edit_guard:punctuation_mismatch | 1472 | 2781 | 2781 | 16 |
| edit_guard:unsupported_character:0 | 1663 | 17 | 43 | 0 |
| edit_guard:unsupported_character:1 | 594 | 4 | 17 | 0 |
| edit_guard:unsupported_character:10 | 206 | 3 | 6 | 0 |
| edit_guard:unsupported_character:11 | 221 | 5 | 5 | 0 |
| edit_guard:unsupported_character:12 | 139 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 254 | 4 | 7 | 0 |
| edit_guard:unsupported_character:14 | 201 | 1 | 5 | 0 |
| edit_guard:unsupported_character:15 | 64 | 2 | 2 | 0 |
| edit_guard:unsupported_character:17 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:18 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:19 | 46 | 1 | 1 | 0 |
| edit_guard:unsupported_character:2 | 565 | 4 | 17 | 0 |
| edit_guard:unsupported_character:20 | 277 | 4 | 7 | 0 |
| edit_guard:unsupported_character:21 | 135 | 4 | 4 | 0 |
| edit_guard:unsupported_character:22 | 200 | 3 | 5 | 0 |
| edit_guard:unsupported_character:23 | 94 | 2 | 2 | 0 |
| edit_guard:unsupported_character:24 | 258 | 3 | 7 | 0 |
| edit_guard:unsupported_character:25 | 163 | 1 | 5 | 0 |
| edit_guard:unsupported_character:26 | 121 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 291 | 6 | 7 | 0 |
| edit_guard:unsupported_character:28 | 75 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 160 | 2 | 4 | 0 |
| edit_guard:unsupported_character:3 | 559 | 5 | 15 | 0 |
| edit_guard:unsupported_character:30 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:31 | 157 | 4 | 4 | 0 |
| edit_guard:unsupported_character:32 | 88 | 2 | 2 | 0 |
| edit_guard:unsupported_character:33 | 112 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 254 | 3 | 6 | 0 |
| edit_guard:unsupported_character:35 | 80 | 2 | 2 | 0 |
| edit_guard:unsupported_character:36 | 183 | 2 | 4 | 0 |
| edit_guard:unsupported_character:37 | 132 | 2 | 3 | 0 |
| edit_guard:unsupported_character:38 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:39 | 227 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 349 | 3 | 9 | 0 |
| edit_guard:unsupported_character:40 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:41 | 436 | 7 | 10 | 0 |
| edit_guard:unsupported_character:42 | 176 | 2 | 4 | 0 |
| edit_guard:unsupported_character:43 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:44 | 180 | 2 | 4 | 0 |
| edit_guard:unsupported_character:45 | 188 | 3 | 4 | 0 |
| edit_guard:unsupported_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_character:49 | 50 | 1 | 1 | 0 |
| edit_guard:unsupported_character:5 | 142 | 2 | 3 | 0 |
| edit_guard:unsupported_character:6 | 168 | 2 | 4 | 0 |
| edit_guard:unsupported_character:7 | 417 | 3 | 11 | 0 |
| edit_guard:unsupported_character:8 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:9 | 265 | 3 | 6 | 0 |
| edit_guard:unsupported_raw_character:0 | 1567 | 2 | 41 | 0 |
| edit_guard:unsupported_raw_character:1 | 521 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:10 | 206 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:11 | 221 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:12 | 139 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 254 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:14 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:15 | 64 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:17 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:18 | 179 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:19 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:2 | 546 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:20 | 277 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:21 | 135 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:22 | 200 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:23 | 142 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:24 | 210 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:25 | 163 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:26 | 121 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 291 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:28 | 75 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 191 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:3 | 559 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:30 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 157 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:32 | 88 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 112 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:34 | 254 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:35 | 80 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 183 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 132 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 227 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 349 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:40 | 222 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:41 | 393 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:42 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:43 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_raw_character:44 | 180 | 1 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 188 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:49 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 142 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:6 | 168 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 393 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:8 | 94 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:9 | 265 | 0 | 6 | 0 |
| ensemble_ab_mark_set_disagreement | 2014 | 0 | 1653 | 2 |
| r1_B_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_B_missing | 1452 | 0 | 955 | 0 |
| r1_B_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |
| r1_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_missing | 1452 | 0 | 955 | 0 |
| r1_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4765 |
| A/B disagreement | 1653 |
| kind disagreement | 0 |
| R1 uncertainty | 1829 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 5274 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 3467 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 2207 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 1803 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 1262 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain"] | 1214 |
| ["detector_clipped_bottom","detector_clipped_top"] | 838 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 651 |
| ["detector_clipped_top"] | 547 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 502 |

### ALL / vouli_parliament_1850s

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 86 | 0 | 83 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 130 | 0 | 120 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 3 | 0 | 3 | 0 |
| K1:C3:two_accents:evidence_tie | 18 | 0 | 9 | 0 |
| K1:C3:two_accents:rule_held_back | 1597 | 0 | 641 | 4 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 200 | 0 | 181 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 12 | 0 | 10 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 281 | 0 | 258 | 0 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 2 | 0 | 2 | 0 |
| detector_clipped_bottom | 40732 | 0 | 15658 | 551 |
| detector_clipped_top | 93007 | 0 | 19927 | 1880 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 102 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 148 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 13 |
| edit_guard:punctuation_mismatch | 3437 | 2268 | 2268 | 71 |
| edit_guard:unsupported_character:0 | 1166 | 8 | 25 | 0 |
| edit_guard:unsupported_character:1 | 510 | 3 | 12 | 0 |
| edit_guard:unsupported_character:10 | 146 | 2 | 4 | 0 |
| edit_guard:unsupported_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_character:15 | 112 | 2 | 3 | 0 |
| edit_guard:unsupported_character:17 | 256 | 4 | 7 | 0 |
| edit_guard:unsupported_character:18 | 156 | 1 | 3 | 0 |
| edit_guard:unsupported_character:19 | 309 | 3 | 8 | 0 |
| edit_guard:unsupported_character:2 | 313 | 1 | 8 | 0 |
| edit_guard:unsupported_character:20 | 40 | 1 | 1 | 0 |
| edit_guard:unsupported_character:21 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:22 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:23 | 72 | 1 | 2 | 0 |
| edit_guard:unsupported_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_character:25 | 91 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 171 | 2 | 4 | 0 |
| edit_guard:unsupported_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_character:28 | 222 | 4 | 5 | 0 |
| edit_guard:unsupported_character:29 | 169 | 3 | 3 | 0 |
| edit_guard:unsupported_character:3 | 657 | 1 | 18 | 0 |
| edit_guard:unsupported_character:30 | 78 | 1 | 2 | 0 |
| edit_guard:unsupported_character:31 | 313 | 2 | 7 | 0 |
| edit_guard:unsupported_character:32 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:33 | 145 | 0 | 3 | 0 |
| edit_guard:unsupported_character:34 | 213 | 2 | 5 | 0 |
| edit_guard:unsupported_character:35 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:36 | 215 | 3 | 5 | 0 |
| edit_guard:unsupported_character:37 | 138 | 1 | 3 | 0 |
| edit_guard:unsupported_character:38 | 94 | 1 | 2 | 0 |
| edit_guard:unsupported_character:39 | 240 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 225 | 3 | 7 | 0 |
| edit_guard:unsupported_character:40 | 426 | 2 | 9 | 0 |
| edit_guard:unsupported_character:41 | 240 | 2 | 5 | 0 |
| edit_guard:unsupported_character:42 | 327 | 3 | 7 | 0 |
| edit_guard:unsupported_character:43 | 412 | 4 | 8 | 0 |
| edit_guard:unsupported_character:44 | 47 | 1 | 1 | 0 |
| edit_guard:unsupported_character:45 | 189 | 1 | 3 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:48 | 100 | 2 | 2 | 0 |
| edit_guard:unsupported_character:49 | 203 | 2 | 4 | 0 |
| edit_guard:unsupported_character:5 | 345 | 2 | 6 | 0 |
| edit_guard:unsupported_character:50 | 109 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_character:6 | 251 | 1 | 6 | 0 |
| edit_guard:unsupported_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_character:7 | 350 | 4 | 7 | 0 |
| edit_guard:unsupported_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_character:76 | 163 | 0 | 2 | 0 |
| edit_guard:unsupported_character:8 | 176 | 1 | 4 | 0 |
| edit_guard:unsupported_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_character:9 | 296 | 6 | 7 | 0 |
| edit_guard:unsupported_raw_character:0 | 1166 | 3 | 28 | 0 |
| edit_guard:unsupported_raw_character:1 | 541 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:10 | 146 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:15 | 112 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:17 | 256 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:18 | 156 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:19 | 286 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:2 | 266 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:20 | 40 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:21 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:23 | 72 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:25 | 131 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 346 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:29 | 169 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:3 | 621 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:30 | 78 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 313 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:32 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 103 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:34 | 213 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:35 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:36 | 215 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 138 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:39 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 225 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:40 | 374 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:41 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:42 | 376 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:43 | 412 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:44 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 189 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:48 | 100 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:49 | 203 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:5 | 345 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 109 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:6 | 251 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 350 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:76 | 80 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:9 | 402 | 0 | 9 | 0 |
| ensemble_ab_mark_set_disagreement | 2177 | 0 | 1575 | 20 |
| r1_B_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_B_missing | 757 | 0 | 390 | 0 |
| r1_B_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |
| r1_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_missing | 757 | 0 | 390 | 0 |
| r1_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3544 |
| A/B disagreement | 1575 |
| kind disagreement | 0 |
| R1 uncertainty | 744 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 3907 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 2646 |
| ["detector_clipped_top"] | 1880 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1726 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1029 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 976 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 930 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark"] | 662 |
| ["detector_clipped_top","detector_unnamed_mark"] | 650 |
| ["detector_clipped_bottom"] | 551 |

### mixed / anemi_mixed

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 48 | 0 | 47 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 102 | 0 | 99 | 1 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 2 | 0 | 2 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:evidence_tie | 4 | 0 | 2 | 0 |
| K1:C3:two_accents:rule_held_back | 868 | 0 | 379 | 6 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 123 | 0 | 121 | 1 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 214 | 0 | 201 | 5 |
| detector_clipped_bottom | 15059 | 0 | 6360 | 338 |
| detector_clipped_top | 39633 | 0 | 8777 | 1443 |
| detector_localisation_unknown | 8716 | 0 | 3345 | 0 |
| detector_segmentation_uncertain | 17133 | 0 | 5085 | 297 |
| detector_unnamed_mark | 2392 | 0 | 1939 | 140 |
| edit_guard:base_or_character_mismatch | 389 | 1258 | 1258 | 20 |
| edit_guard:punctuation_mismatch | 1184 | 1470 | 1470 | 119 |
| edit_guard:unsupported_character:0 | 570 | 6 | 14 | 0 |
| edit_guard:unsupported_character:1 | 335 | 3 | 8 | 0 |
| edit_guard:unsupported_character:10 | 312 | 5 | 8 | 0 |
| edit_guard:unsupported_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 49 | 1 | 1 | 0 |
| edit_guard:unsupported_character:13 | 211 | 3 | 5 | 0 |
| edit_guard:unsupported_character:14 | 107 | 3 | 3 | 0 |
| edit_guard:unsupported_character:15 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:16 | 192 | 3 | 5 | 0 |
| edit_guard:unsupported_character:17 | 27 | 1 | 1 | 0 |
| edit_guard:unsupported_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:19 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_character:20 | 113 | 2 | 3 | 0 |
| edit_guard:unsupported_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_character:22 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_character:25 | 97 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 104 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 209 | 3 | 5 | 0 |
| edit_guard:unsupported_character:28 | 288 | 2 | 7 | 0 |
| edit_guard:unsupported_character:29 | 68 | 1 | 1 | 0 |
| edit_guard:unsupported_character:3 | 270 | 3 | 7 | 0 |
| edit_guard:unsupported_character:30 | 158 | 3 | 4 | 0 |
| edit_guard:unsupported_character:31 | 260 | 2 | 6 | 0 |
| edit_guard:unsupported_character:32 | 155 | 1 | 4 | 0 |
| edit_guard:unsupported_character:33 | 114 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_character:36 | 165 | 1 | 4 | 0 |
| edit_guard:unsupported_character:37 | 307 | 3 | 7 | 0 |
| edit_guard:unsupported_character:38 | 130 | 1 | 3 | 0 |
| edit_guard:unsupported_character:39 | 134 | 2 | 3 | 0 |
| edit_guard:unsupported_character:4 | 130 | 2 | 3 | 0 |
| edit_guard:unsupported_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_character:41 | 101 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 233 | 3 | 5 | 0 |
| edit_guard:unsupported_character:43 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:44 | 253 | 3 | 5 | 0 |
| edit_guard:unsupported_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_character:46 | 144 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 102 | 1 | 2 | 0 |
| edit_guard:unsupported_character:48 | 102 | 2 | 2 | 0 |
| edit_guard:unsupported_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_character:50 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_character:6 | 53 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 145 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 227 | 4 | 5 | 0 |
| edit_guard:unsupported_raw_character:0 | 563 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:1 | 335 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 312 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:11 | 39 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:13 | 211 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:14 | 156 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:16 | 192 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:17 | 27 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:19 | 97 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:2 | 175 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:20 | 113 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:21 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:23 | 144 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:25 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:26 | 131 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 209 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:28 | 288 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:29 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 270 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:30 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:31 | 260 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:32 | 155 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 114 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:34 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:35 | 85 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 165 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 307 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:38 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:4 | 130 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 257 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:41 | 101 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 233 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:44 | 253 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 99 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:46 | 144 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 102 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:48 | 102 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:5 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:50 | 57 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 58 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:8 | 227 | 0 | 5 | 0 |
| ensemble_ab_mark_set_disagreement | 1607 | 0 | 1231 | 35 |
| r1_B_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_B_missing | 418 | 0 | 244 | 0 |
| r1_B_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 132 | 0 | 51 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 266 | 0 | 200 | 0 |
| r1_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_missing | 418 | 0 | 244 | 0 |
| r1_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 132 | 0 | 51 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 266 | 0 | 200 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6032 |
| clipping | 9594 |
| K1 | 609 |
| edit-guard | 2191 |
| A/B disagreement | 1231 |
| kind disagreement | 0 |
| R1 uncertainty | 294 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2260 |
| ["detector_clipped_top"] | 1443 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 625 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 535 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 515 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 445 |
| ["detector_clipped_bottom"] | 338 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 328 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 297 |
| ["detector_segmentation_uncertain"] | 297 |

### mixed / archive_b28038630

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 2 | 0 | 1 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 1 | 0 | 1 | 1 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 130 | 0 | 45 | 2 |
| detector_clipped_top | 254 | 0 | 58 | 11 |
| detector_localisation_unknown | 7 | 0 | 6 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 1 |
| edit_guard:base_or_character_mismatch | 0 | 13 | 13 | 0 |
| edit_guard:punctuation_mismatch | 0 | 22 | 22 | 5 |
| ensemble_ab_mark_set_disagreement | 12 | 0 | 12 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 13 |
| clipping | 61 |
| K1 | 3 |
| edit-guard | 24 |
| A/B disagreement | 12 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 21 |
| ["detector_clipped_top"] | 11 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 6 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch"] | 5 |
| ["edit_guard:punctuation_mismatch"] | 5 |
| ["detector_clipped_bottom","detector_clipped_top","ensemble_ab_mark_set_disagreement"] | 4 |
| ["detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch"] | 3 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:punctuation_mismatch"] | 2 |
| ["detector_clipped_bottom"] | 2 |
| ["K1:C3:two_accents:rule_held_back","detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement"] | 1 |

### mixed / openarchives_mixed_Pandemos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_clipped_bottom | 16 | 0 | 7 | 2 |
| detector_clipped_top | 27 | 0 | 4 | 0 |
| detector_localisation_unknown | 5 | 0 | 1 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 2 | 0 |
| detector_unnamed_mark | 3 | 0 | 3 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 1 | 1 | 0 |
| edit_guard:punctuation_mismatch | 0 | 1 | 1 | 0 |
| ensemble_ab_mark_set_disagreement | 1 | 0 | 1 | 0 |
| r1_B_missing | 1 | 0 | 1 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 1 | 0 | 1 | 0 |
| r1_missing | 1 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 7 |
| K1 | 0 |
| edit-guard | 2 |
| A/B disagreement | 1 |
| kind disagreement | 0 |
| R1 uncertainty | 1 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 4 |
| ["detector_clipped_bottom"] | 2 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","detector_unnamed_mark"] | 1 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |
| ["detector_unnamed_mark","edit_guard:punctuation_mismatch"] | 1 |
| ["detector_unnamed_mark","ensemble_ab_mark_set_disagreement"] | 1 |

### mixed / openarchives_mixed_apothesis

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|

| Family | Lines held |
|---|---:|
| localisation/segmentation | 0 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|

### mixed / openarchives_mixed_ktisis

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_unnamed_mark | 1 | 0 | 1 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 1 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_unnamed_mark"] | 1 |

### mixed / openarchives_mixed_ntua

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_not_initial:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:rule_held_back | 4 | 0 | 2 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_bottom | 11 | 0 | 5 | 0 |
| detector_clipped_top | 29 | 0 | 5 | 0 |
| detector_localisation_unknown | 15 | 0 | 3 | 0 |
| detector_segmentation_uncertain | 27 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 1 |
| edit_guard:base_or_character_mismatch | 0 | 21 | 21 | 2 |
| edit_guard:punctuation_mismatch | 104 | 16 | 16 | 1 |
| edit_guard:unsupported_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| ensemble_ab_mark_set_disagreement | 11 | 0 | 8 | 0 |
| r1_B_missing | 21 | 0 | 4 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 18 | 0 | 4 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 3 | 0 | 1 | 0 |
| r1_missing | 21 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 18 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 3 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 12 |
| clipping | 7 |
| K1 | 4 |
| edit-guard | 22 |
| A/B disagreement | 8 |
| kind disagreement | 0 |
| R1 uncertainty | 4 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch"] | 5 |
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement"] | 2 |
| ["edit_guard:base_or_character_mismatch"] | 2 |
| ["K1:C1:breathing_not_initial:impossible_by_rule","K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","edit_guard:unsupported_character:28","edit_guard:unsupported_raw_character:28","ensemble_ab_mark_set_disagreement","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_B_unscored:width_outside_0.2_2.0_median_ctc","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","r1_unscored:width_outside_0.2_2.0_median_ctc"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","ensemble_ab_mark_set_disagreement"] | 1 |
| ["detector_clipped_bottom","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height"] | 1 |

### openarchives / openarchives_Pandemos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| detector_clipped_bottom | 366 | 0 | 118 | 27 |
| detector_clipped_top | 604 | 0 | 118 | 25 |
| detector_segmentation_uncertain | 100 | 0 | 35 | 6 |
| detector_unnamed_mark | 23 | 0 | 18 | 1 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 9 | 9 | 0 |
| ensemble_ab_mark_set_disagreement | 2 | 0 | 2 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 46 |
| clipping | 157 |
| K1 | 0 |
| edit-guard | 9 |
| A/B disagreement | 2 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 61 |
| ["detector_clipped_bottom"] | 27 |
| ["detector_clipped_top"] | 25 |
| ["detector_clipped_bottom","detector_segmentation_uncertain"] | 9 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 7 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 7 |
| ["detector_segmentation_uncertain"] | 6 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 5 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch"] | 2 |

### openarchives / openarchives_kallipos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 12 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_top | 25 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 10 | 0 | 3 | 3 |
| detector_unnamed_mark | 1 | 0 | 1 | 0 |
| edit_guard:punctuation_mismatch | 0 | 10 | 10 | 7 |
| ensemble_ab_mark_set_disagreement | 17 | 0 | 14 | 12 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 2 |
| K1 | 5 |
| edit-guard | 10 |
| A/B disagreement | 14 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["ensemble_ab_mark_set_disagreement"] | 12 |
| ["edit_guard:punctuation_mismatch"] | 7 |
| ["detector_segmentation_uncertain"] | 3 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule"] | 2 |
| ["detector_clipped_top","edit_guard:punctuation_mismatch"] | 2 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_unnamed_mark"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement"] | 1 |
| ["K1:C3:two_accents:rule_held_back","ensemble_ab_mark_set_disagreement"] | 1 |

### parliament / parliament_proceedings_1975_2000

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 69 | 0 | 67 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 90 | 0 | 88 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C3:two_accents:evidence_tie | 14 | 0 | 7 | 0 |
| K1:C3:two_accents:rule_held_back | 1343 | 0 | 613 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 159 | 0 | 155 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 7 | 0 | 7 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 292 | 0 | 253 | 0 |
| detector_clipped_bottom | 44633 | 0 | 16119 | 183 |
| detector_clipped_top | 98404 | 0 | 20688 | 547 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 84 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 72 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 8 |
| edit_guard:punctuation_mismatch | 1472 | 2781 | 2781 | 16 |
| edit_guard:unsupported_character:0 | 1663 | 17 | 43 | 0 |
| edit_guard:unsupported_character:1 | 594 | 4 | 17 | 0 |
| edit_guard:unsupported_character:10 | 206 | 3 | 6 | 0 |
| edit_guard:unsupported_character:11 | 221 | 5 | 5 | 0 |
| edit_guard:unsupported_character:12 | 139 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 254 | 4 | 7 | 0 |
| edit_guard:unsupported_character:14 | 201 | 1 | 5 | 0 |
| edit_guard:unsupported_character:15 | 64 | 2 | 2 | 0 |
| edit_guard:unsupported_character:17 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:18 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:19 | 46 | 1 | 1 | 0 |
| edit_guard:unsupported_character:2 | 565 | 4 | 17 | 0 |
| edit_guard:unsupported_character:20 | 277 | 4 | 7 | 0 |
| edit_guard:unsupported_character:21 | 135 | 4 | 4 | 0 |
| edit_guard:unsupported_character:22 | 200 | 3 | 5 | 0 |
| edit_guard:unsupported_character:23 | 94 | 2 | 2 | 0 |
| edit_guard:unsupported_character:24 | 258 | 3 | 7 | 0 |
| edit_guard:unsupported_character:25 | 163 | 1 | 5 | 0 |
| edit_guard:unsupported_character:26 | 121 | 1 | 3 | 0 |
| edit_guard:unsupported_character:27 | 291 | 6 | 7 | 0 |
| edit_guard:unsupported_character:28 | 75 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 160 | 2 | 4 | 0 |
| edit_guard:unsupported_character:3 | 559 | 5 | 15 | 0 |
| edit_guard:unsupported_character:30 | 41 | 1 | 1 | 0 |
| edit_guard:unsupported_character:31 | 157 | 4 | 4 | 0 |
| edit_guard:unsupported_character:32 | 88 | 2 | 2 | 0 |
| edit_guard:unsupported_character:33 | 112 | 1 | 3 | 0 |
| edit_guard:unsupported_character:34 | 254 | 3 | 6 | 0 |
| edit_guard:unsupported_character:35 | 80 | 2 | 2 | 0 |
| edit_guard:unsupported_character:36 | 183 | 2 | 4 | 0 |
| edit_guard:unsupported_character:37 | 132 | 2 | 3 | 0 |
| edit_guard:unsupported_character:38 | 184 | 2 | 4 | 0 |
| edit_guard:unsupported_character:39 | 227 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 349 | 3 | 9 | 0 |
| edit_guard:unsupported_character:40 | 179 | 3 | 4 | 0 |
| edit_guard:unsupported_character:41 | 436 | 7 | 10 | 0 |
| edit_guard:unsupported_character:42 | 176 | 2 | 4 | 0 |
| edit_guard:unsupported_character:43 | 96 | 2 | 2 | 0 |
| edit_guard:unsupported_character:44 | 180 | 2 | 4 | 0 |
| edit_guard:unsupported_character:45 | 188 | 3 | 4 | 0 |
| edit_guard:unsupported_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_character:49 | 50 | 1 | 1 | 0 |
| edit_guard:unsupported_character:5 | 142 | 2 | 3 | 0 |
| edit_guard:unsupported_character:6 | 168 | 2 | 4 | 0 |
| edit_guard:unsupported_character:7 | 417 | 3 | 11 | 0 |
| edit_guard:unsupported_character:8 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:9 | 265 | 3 | 6 | 0 |
| edit_guard:unsupported_raw_character:0 | 1567 | 2 | 41 | 0 |
| edit_guard:unsupported_raw_character:1 | 521 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:10 | 206 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:11 | 221 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:12 | 139 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 254 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:14 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:15 | 64 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:17 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:18 | 179 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:19 | 46 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:2 | 546 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:20 | 277 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:21 | 135 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:22 | 200 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:23 | 142 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:24 | 210 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:25 | 163 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:26 | 121 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 291 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:28 | 75 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 191 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:3 | 559 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:30 | 74 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 157 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:32 | 88 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 112 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:34 | 254 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:35 | 80 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:36 | 183 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:37 | 132 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 184 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 227 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 349 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:40 | 222 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:41 | 393 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:42 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:43 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_raw_character:44 | 180 | 1 | 5 | 0 |
| edit_guard:unsupported_raw_character:45 | 188 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:46 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:48 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:49 | 50 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 142 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:6 | 168 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 393 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:8 | 94 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:9 | 265 | 0 | 6 | 0 |
| ensemble_ab_mark_set_disagreement | 2014 | 0 | 1653 | 2 |
| r1_B_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_B_missing | 1452 | 0 | 955 | 0 |
| r1_B_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |
| r1_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_missing | 1452 | 0 | 955 | 0 |
| r1_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4765 |
| A/B disagreement | 1653 |
| kind disagreement | 0 |
| R1 uncertainty | 1829 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 5274 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 3467 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 2207 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 1803 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 1262 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain"] | 1214 |
| ["detector_clipped_bottom","detector_clipped_top"] | 838 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 651 |
| ["detector_clipped_top"] | 547 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 502 |

### round1 / anemi_round1

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 1 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 3 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 2 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 1 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 29 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 1 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 3 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 1209 |
| detector_clipped_top | 140308 | 0 | 29544 | 4475 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 862 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 553 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 118 |
| edit_guard:punctuation_mismatch | 9153 | 6398 | 6398 | 450 |
| edit_guard:unsupported_character:0 | 3286 | 23 | 79 | 0 |
| edit_guard:unsupported_character:1 | 2211 | 16 | 47 | 0 |
| edit_guard:unsupported_character:10 | 439 | 5 | 12 | 0 |
| edit_guard:unsupported_character:11 | 317 | 3 | 9 | 0 |
| edit_guard:unsupported_character:12 | 144 | 2 | 3 | 0 |
| edit_guard:unsupported_character:13 | 283 | 6 | 9 | 0 |
| edit_guard:unsupported_character:14 | 407 | 9 | 13 | 0 |
| edit_guard:unsupported_character:15 | 470 | 7 | 14 | 0 |
| edit_guard:unsupported_character:16 | 268 | 3 | 7 | 0 |
| edit_guard:unsupported_character:17 | 383 | 4 | 9 | 0 |
| edit_guard:unsupported_character:18 | 295 | 3 | 8 | 0 |
| edit_guard:unsupported_character:19 | 337 | 3 | 10 | 0 |
| edit_guard:unsupported_character:2 | 409 | 4 | 11 | 0 |
| edit_guard:unsupported_character:20 | 535 | 6 | 13 | 0 |
| edit_guard:unsupported_character:21 | 407 | 4 | 12 | 0 |
| edit_guard:unsupported_character:22 | 427 | 8 | 11 | 0 |
| edit_guard:unsupported_character:23 | 668 | 7 | 19 | 0 |
| edit_guard:unsupported_character:24 | 469 | 7 | 11 | 0 |
| edit_guard:unsupported_character:25 | 228 | 3 | 7 | 0 |
| edit_guard:unsupported_character:26 | 599 | 6 | 15 | 0 |
| edit_guard:unsupported_character:27 | 636 | 6 | 17 | 0 |
| edit_guard:unsupported_character:28 | 581 | 6 | 17 | 0 |
| edit_guard:unsupported_character:29 | 1243 | 12 | 33 | 0 |
| edit_guard:unsupported_character:3 | 622 | 2 | 15 | 0 |
| edit_guard:unsupported_character:30 | 652 | 5 | 18 | 0 |
| edit_guard:unsupported_character:31 | 551 | 3 | 15 | 0 |
| edit_guard:unsupported_character:32 | 684 | 4 | 18 | 0 |
| edit_guard:unsupported_character:33 | 538 | 5 | 13 | 0 |
| edit_guard:unsupported_character:34 | 781 | 4 | 18 | 0 |
| edit_guard:unsupported_character:35 | 701 | 6 | 17 | 0 |
| edit_guard:unsupported_character:36 | 745 | 2 | 19 | 0 |
| edit_guard:unsupported_character:37 | 765 | 5 | 19 | 0 |
| edit_guard:unsupported_character:38 | 408 | 1 | 10 | 0 |
| edit_guard:unsupported_character:39 | 791 | 6 | 18 | 0 |
| edit_guard:unsupported_character:4 | 497 | 4 | 11 | 0 |
| edit_guard:unsupported_character:40 | 448 | 3 | 10 | 0 |
| edit_guard:unsupported_character:41 | 811 | 5 | 18 | 0 |
| edit_guard:unsupported_character:42 | 454 | 4 | 10 | 0 |
| edit_guard:unsupported_character:43 | 569 | 6 | 12 | 0 |
| edit_guard:unsupported_character:44 | 300 | 3 | 6 | 0 |
| edit_guard:unsupported_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_character:46 | 262 | 1 | 5 | 0 |
| edit_guard:unsupported_character:47 | 207 | 4 | 4 | 0 |
| edit_guard:unsupported_character:48 | 251 | 2 | 5 | 0 |
| edit_guard:unsupported_character:49 | 315 | 1 | 6 | 0 |
| edit_guard:unsupported_character:5 | 299 | 2 | 7 | 0 |
| edit_guard:unsupported_character:50 | 284 | 3 | 5 | 0 |
| edit_guard:unsupported_character:51 | 495 | 3 | 9 | 0 |
| edit_guard:unsupported_character:52 | 175 | 1 | 3 | 0 |
| edit_guard:unsupported_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_character:54 | 202 | 2 | 3 | 0 |
| edit_guard:unsupported_character:55 | 247 | 2 | 4 | 0 |
| edit_guard:unsupported_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_character:57 | 202 | 1 | 3 | 0 |
| edit_guard:unsupported_character:58 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:59 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 421 | 2 | 12 | 0 |
| edit_guard:unsupported_character:60 | 63 | 1 | 1 | 0 |
| edit_guard:unsupported_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_character:62 | 64 | 1 | 1 | 0 |
| edit_guard:unsupported_character:65 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 431 | 3 | 9 | 0 |
| edit_guard:unsupported_character:74 | 83 | 1 | 1 | 0 |
| edit_guard:unsupported_character:8 | 618 | 4 | 15 | 0 |
| edit_guard:unsupported_character:9 | 433 | 4 | 11 | 0 |
| edit_guard:unsupported_raw_character:0 | 3282 | 1 | 78 | 0 |
| edit_guard:unsupported_raw_character:1 | 1715 | 0 | 40 | 0 |
| edit_guard:unsupported_raw_character:10 | 439 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:11 | 339 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:12 | 144 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:13 | 283 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:14 | 424 | 0 | 14 | 0 |
| edit_guard:unsupported_raw_character:15 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:16 | 302 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:17 | 383 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:18 | 317 | 0 | 9 | 0 |
| edit_guard:unsupported_raw_character:19 | 379 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:2 | 409 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:20 | 535 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:21 | 404 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:22 | 427 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:23 | 668 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:24 | 469 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:25 | 228 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:26 | 599 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:27 | 636 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:28 | 581 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:29 | 1243 | 0 | 33 | 0 |
| edit_guard:unsupported_raw_character:3 | 644 | 0 | 16 | 0 |
| edit_guard:unsupported_raw_character:30 | 652 | 1 | 19 | 0 |
| edit_guard:unsupported_raw_character:31 | 551 | 0 | 15 | 0 |
| edit_guard:unsupported_raw_character:32 | 718 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:33 | 543 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:34 | 742 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:35 | 701 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:36 | 745 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:37 | 806 | 0 | 20 | 0 |
| edit_guard:unsupported_raw_character:38 | 402 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:39 | 831 | 0 | 19 | 0 |
| edit_guard:unsupported_raw_character:4 | 497 | 0 | 11 | 0 |
| edit_guard:unsupported_raw_character:40 | 448 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:41 | 811 | 0 | 18 | 0 |
| edit_guard:unsupported_raw_character:42 | 454 | 1 | 11 | 0 |
| edit_guard:unsupported_raw_character:43 | 569 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:44 | 300 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:45 | 284 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:46 | 262 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:47 | 207 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:48 | 251 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:49 | 315 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:5 | 270 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 233 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 436 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:52 | 175 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:53 | 231 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:54 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:55 | 247 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:56 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:57 | 202 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:58 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:59 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 421 | 0 | 12 | 0 |
| edit_guard:unsupported_raw_character:60 | 63 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:61 | 125 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:62 | 64 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:65 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 471 | 0 | 10 | 0 |
| edit_guard:unsupported_raw_character:74 | 83 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 545 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:9 | 433 | 0 | 11 | 0 |
| ensemble_ab_mark_set_disagreement | 5515 | 0 | 4277 | 152 |
| r1_B_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_B_missing | 1687 | 0 | 1129 | 0 |
| r1_B_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |
| r1_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_missing | 1687 | 0 | 1129 | 0 |
| r1_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9251 |
| A/B disagreement | 4277 |
| kind disagreement | 0 |
| R1 uncertainty | 1276 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 7199 |
| ["detector_clipped_top"] | 4475 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 2210 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 1544 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 1461 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1425 |
| ["detector_clipped_bottom"] | 1209 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 1019 |
| ["detector_segmentation_uncertain"] | 862 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 828 |

### round2 / anemi_round2

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 84 | 0 | 81 | 2 |
| K1:C1:breathing_not_initial:impossible_by_rule | 107 | 0 | 103 | 3 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 6 | 0 | 3 | 0 |
| K1:C3:two_accents:rule_held_back | 1020 | 0 | 467 | 8 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 101 | 0 | 98 | 1 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 2 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 511 |
| detector_clipped_top | 48664 | 0 | 10763 | 1916 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 381 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 324 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 59 |
| edit_guard:punctuation_mismatch | 1491 | 2095 | 2095 | 207 |
| edit_guard:unsupported_character:0 | 1107 | 12 | 28 | 0 |
| edit_guard:unsupported_character:1 | 360 | 2 | 9 | 0 |
| edit_guard:unsupported_character:10 | 169 | 1 | 4 | 0 |
| edit_guard:unsupported_character:11 | 54 | 1 | 1 | 0 |
| edit_guard:unsupported_character:12 | 178 | 3 | 5 | 0 |
| edit_guard:unsupported_character:13 | 96 | 1 | 3 | 0 |
| edit_guard:unsupported_character:14 | 169 | 2 | 4 | 0 |
| edit_guard:unsupported_character:15 | 122 | 3 | 3 | 0 |
| edit_guard:unsupported_character:16 | 225 | 1 | 8 | 0 |
| edit_guard:unsupported_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_character:18 | 252 | 3 | 7 | 0 |
| edit_guard:unsupported_character:19 | 108 | 1 | 3 | 0 |
| edit_guard:unsupported_character:2 | 238 | 4 | 6 | 0 |
| edit_guard:unsupported_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_character:21 | 129 | 1 | 4 | 0 |
| edit_guard:unsupported_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_character:23 | 43 | 1 | 1 | 0 |
| edit_guard:unsupported_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_character:27 | 150 | 3 | 4 | 0 |
| edit_guard:unsupported_character:28 | 86 | 1 | 2 | 0 |
| edit_guard:unsupported_character:29 | 71 | 0 | 2 | 0 |
| edit_guard:unsupported_character:3 | 236 | 3 | 6 | 0 |
| edit_guard:unsupported_character:30 | 225 | 3 | 6 | 0 |
| edit_guard:unsupported_character:31 | 201 | 3 | 5 | 0 |
| edit_guard:unsupported_character:32 | 79 | 1 | 2 | 0 |
| edit_guard:unsupported_character:33 | 250 | 2 | 6 | 0 |
| edit_guard:unsupported_character:34 | 116 | 1 | 3 | 0 |
| edit_guard:unsupported_character:35 | 152 | 1 | 4 | 0 |
| edit_guard:unsupported_character:36 | 212 | 2 | 5 | 0 |
| edit_guard:unsupported_character:37 | 356 | 5 | 8 | 0 |
| edit_guard:unsupported_character:38 | 192 | 4 | 4 | 0 |
| edit_guard:unsupported_character:39 | 98 | 2 | 2 | 0 |
| edit_guard:unsupported_character:4 | 63 | 1 | 2 | 0 |
| edit_guard:unsupported_character:40 | 87 | 2 | 2 | 0 |
| edit_guard:unsupported_character:42 | 241 | 2 | 5 | 0 |
| edit_guard:unsupported_character:43 | 92 | 1 | 2 | 0 |
| edit_guard:unsupported_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_character:45 | 51 | 1 | 1 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_character:5 | 121 | 3 | 3 | 0 |
| edit_guard:unsupported_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_character:53 | 113 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_character:59 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:6 | 165 | 4 | 5 | 0 |
| edit_guard:unsupported_character:60 | 61 | 1 | 1 | 0 |
| edit_guard:unsupported_character:7 | 173 | 4 | 4 | 0 |
| edit_guard:unsupported_character:8 | 145 | 1 | 4 | 0 |
| edit_guard:unsupported_character:9 | 114 | 1 | 4 | 0 |
| edit_guard:unsupported_raw_character:0 | 1012 | 0 | 26 | 0 |
| edit_guard:unsupported_raw_character:1 | 341 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:10 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 54 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 178 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:13 | 96 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:14 | 169 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:15 | 122 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:16 | 225 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:17 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:18 | 252 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:19 | 108 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:2 | 238 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:20 | 140 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:21 | 98 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:22 | 60 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:23 | 43 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:25 | 110 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 94 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:27 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:28 | 86 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:29 | 41 | 1 | 2 | 0 |
| edit_guard:unsupported_raw_character:3 | 236 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:30 | 193 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:31 | 201 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:32 | 79 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:33 | 250 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:34 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:35 | 152 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:36 | 212 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 356 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:38 | 192 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:39 | 98 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:4 | 79 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:40 | 87 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:42 | 241 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:43 | 92 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:44 | 45 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 49 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:5 | 148 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:51 | 52 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:52 | 53 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:53 | 113 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:58 | 123 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:59 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:6 | 165 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:60 | 61 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:7 | 148 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:8 | 145 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:9 | 114 | 0 | 4 | 0 |
| ensemble_ab_mark_set_disagreement | 1770 | 0 | 1426 | 80 |
| r1_B_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_B_missing | 434 | 0 | 268 | 0 |
| r1_B_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |
| r1_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_missing | 434 | 0 | 268 | 0 |
| r1_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3059 |
| A/B disagreement | 1426 |
| kind disagreement | 0 |
| R1 uncertainty | 354 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2870 |
| ["detector_clipped_top"] | 1916 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 590 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 544 |
| ["detector_clipped_bottom"] | 511 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 448 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 405 |
| ["detector_segmentation_uncertain"] | 381 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 356 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 326 |

### vouli / vouli_parliament_1850s

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 86 | 0 | 83 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 130 | 0 | 120 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 3 | 0 | 3 | 0 |
| K1:C3:two_accents:evidence_tie | 18 | 0 | 9 | 0 |
| K1:C3:two_accents:rule_held_back | 1597 | 0 | 641 | 4 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 200 | 0 | 181 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 12 | 0 | 10 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 281 | 0 | 258 | 0 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 2 | 0 | 2 | 0 |
| detector_clipped_bottom | 40732 | 0 | 15658 | 551 |
| detector_clipped_top | 93007 | 0 | 19927 | 1880 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 102 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 148 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 13 |
| edit_guard:punctuation_mismatch | 3437 | 2268 | 2268 | 71 |
| edit_guard:unsupported_character:0 | 1166 | 8 | 25 | 0 |
| edit_guard:unsupported_character:1 | 510 | 3 | 12 | 0 |
| edit_guard:unsupported_character:10 | 146 | 2 | 4 | 0 |
| edit_guard:unsupported_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_character:15 | 112 | 2 | 3 | 0 |
| edit_guard:unsupported_character:17 | 256 | 4 | 7 | 0 |
| edit_guard:unsupported_character:18 | 156 | 1 | 3 | 0 |
| edit_guard:unsupported_character:19 | 309 | 3 | 8 | 0 |
| edit_guard:unsupported_character:2 | 313 | 1 | 8 | 0 |
| edit_guard:unsupported_character:20 | 40 | 1 | 1 | 0 |
| edit_guard:unsupported_character:21 | 96 | 1 | 2 | 0 |
| edit_guard:unsupported_character:22 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:23 | 72 | 1 | 2 | 0 |
| edit_guard:unsupported_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_character:25 | 91 | 1 | 2 | 0 |
| edit_guard:unsupported_character:26 | 171 | 2 | 4 | 0 |
| edit_guard:unsupported_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_character:28 | 222 | 4 | 5 | 0 |
| edit_guard:unsupported_character:29 | 169 | 3 | 3 | 0 |
| edit_guard:unsupported_character:3 | 657 | 1 | 18 | 0 |
| edit_guard:unsupported_character:30 | 78 | 1 | 2 | 0 |
| edit_guard:unsupported_character:31 | 313 | 2 | 7 | 0 |
| edit_guard:unsupported_character:32 | 116 | 2 | 3 | 0 |
| edit_guard:unsupported_character:33 | 145 | 0 | 3 | 0 |
| edit_guard:unsupported_character:34 | 213 | 2 | 5 | 0 |
| edit_guard:unsupported_character:35 | 119 | 1 | 3 | 0 |
| edit_guard:unsupported_character:36 | 215 | 3 | 5 | 0 |
| edit_guard:unsupported_character:37 | 138 | 1 | 3 | 0 |
| edit_guard:unsupported_character:38 | 94 | 1 | 2 | 0 |
| edit_guard:unsupported_character:39 | 240 | 3 | 5 | 0 |
| edit_guard:unsupported_character:4 | 225 | 3 | 7 | 0 |
| edit_guard:unsupported_character:40 | 426 | 2 | 9 | 0 |
| edit_guard:unsupported_character:41 | 240 | 2 | 5 | 0 |
| edit_guard:unsupported_character:42 | 327 | 3 | 7 | 0 |
| edit_guard:unsupported_character:43 | 412 | 4 | 8 | 0 |
| edit_guard:unsupported_character:44 | 47 | 1 | 1 | 0 |
| edit_guard:unsupported_character:45 | 189 | 1 | 3 | 0 |
| edit_guard:unsupported_character:46 | 153 | 1 | 3 | 0 |
| edit_guard:unsupported_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_character:48 | 100 | 2 | 2 | 0 |
| edit_guard:unsupported_character:49 | 203 | 2 | 4 | 0 |
| edit_guard:unsupported_character:5 | 345 | 2 | 6 | 0 |
| edit_guard:unsupported_character:50 | 109 | 1 | 2 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_character:6 | 251 | 1 | 6 | 0 |
| edit_guard:unsupported_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_character:7 | 350 | 4 | 7 | 0 |
| edit_guard:unsupported_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_character:76 | 163 | 0 | 2 | 0 |
| edit_guard:unsupported_character:8 | 176 | 1 | 4 | 0 |
| edit_guard:unsupported_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_character:9 | 296 | 6 | 7 | 0 |
| edit_guard:unsupported_raw_character:0 | 1166 | 3 | 28 | 0 |
| edit_guard:unsupported_raw_character:1 | 541 | 0 | 13 | 0 |
| edit_guard:unsupported_raw_character:10 | 146 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:11 | 34 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:12 | 91 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:13 | 73 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:14 | 134 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:15 | 112 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:17 | 256 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:18 | 156 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:19 | 286 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:2 | 266 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:20 | 40 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:21 | 96 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:22 | 116 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:23 | 72 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:24 | 103 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:25 | 131 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:26 | 171 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:27 | 48 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 346 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:29 | 169 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:3 | 621 | 0 | 17 | 0 |
| edit_guard:unsupported_raw_character:30 | 78 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:31 | 313 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:32 | 158 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:33 | 103 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:34 | 213 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:35 | 119 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:36 | 215 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:37 | 138 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:38 | 41 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:39 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:4 | 225 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:40 | 374 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:41 | 240 | 0 | 5 | 0 |
| edit_guard:unsupported_raw_character:42 | 376 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:43 | 412 | 0 | 8 | 0 |
| edit_guard:unsupported_raw_character:44 | 47 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:45 | 189 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:46 | 153 | 0 | 3 | 0 |
| edit_guard:unsupported_raw_character:47 | 51 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:48 | 100 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:49 | 203 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:5 | 345 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:50 | 109 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:55 | 168 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:6 | 251 | 0 | 6 | 0 |
| edit_guard:unsupported_raw_character:60 | 130 | 0 | 2 | 0 |
| edit_guard:unsupported_raw_character:61 | 62 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:62 | 69 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:67 | 292 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:7 | 350 | 0 | 7 | 0 |
| edit_guard:unsupported_raw_character:70 | 75 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:76 | 80 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:8 | 176 | 0 | 4 | 0 |
| edit_guard:unsupported_raw_character:84 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:85 | 88 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:86 | 87 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:87 | 89 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:9 | 402 | 0 | 9 | 0 |
| ensemble_ab_mark_set_disagreement | 2177 | 0 | 1575 | 20 |
| r1_B_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_B_missing | 757 | 0 | 390 | 0 |
| r1_B_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_B_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_B_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_B_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |
| r1_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_missing | 757 | 0 | 390 | 0 |
| r1_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3544 |
| A/B disagreement | 1575 |
| kind disagreement | 0 |
| R1 uncertainty | 744 |
| other/unclassified | 0 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 3907 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 2646 |
| ["detector_clipped_top"] | 1880 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1726 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1029 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 976 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 930 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark"] | 662 |
| ["detector_clipped_top","detector_unnamed_mark"] | 650 |
| ["detector_clipped_bottom"] | 551 |

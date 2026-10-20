# L1C HOLD census

Analysis only; exact reasons read from completed SF4/SF5 releases.

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
| ALL | ALL | 124669 | 118856 | 1350908 |
| mixed | ALL | 13227 | 12466 | 119060 |
| openarchives | ALL | 235 | 207 | 1224 |
| parliament | ALL | 27224 | 27090 | 411010 |
| round1 | ALL | 43869 | 40895 | 428855 |
| round2 | ALL | 17026 | 15516 | 135490 |
| vouli | ALL | 23088 | 22682 | 255269 |
| ALL | anemi_mixed | 13084 | 12341 | 117292 |
| ALL | anemi_round1 | 43869 | 40895 | 428855 |
| ALL | anemi_round2 | 17026 | 15516 | 135490 |
| ALL | archive_b28038630 | 97 | 80 | 706 |
| ALL | openarchives_Pandemos | 185 | 171 | 1124 |
| ALL | openarchives_kallipos | 50 | 36 | 100 |
| ALL | openarchives_mixed_Pandemos | 13 | 12 | 118 |
| ALL | openarchives_mixed_apothesis | 1 | 1 | 1 |
| ALL | openarchives_mixed_ktisis | 2 | 2 | 3 |
| ALL | openarchives_mixed_ntua | 30 | 30 | 940 |
| ALL | parliament_proceedings_1975_2000 | 27224 | 27090 | 411010 |
| ALL | vouli_parliament_1850s | 23088 | 22682 | 255269 |
| mixed | anemi_mixed | 13084 | 12341 | 117292 |
| mixed | archive_b28038630 | 97 | 80 | 706 |
| mixed | openarchives_mixed_Pandemos | 13 | 12 | 118 |
| mixed | openarchives_mixed_apothesis | 1 | 1 | 1 |
| mixed | openarchives_mixed_ktisis | 2 | 2 | 3 |
| mixed | openarchives_mixed_ntua | 30 | 30 | 940 |
| openarchives | openarchives_Pandemos | 185 | 171 | 1124 |
| openarchives | openarchives_kallipos | 50 | 36 | 100 |
| parliament | parliament_proceedings_1975_2000 | 27224 | 27090 | 411010 |
| round1 | anemi_round1 | 43869 | 40895 | 428855 |
| round2 | anemi_round2 | 17026 | 15516 | 135490 |
| vouli | vouli_parliament_1850s | 23088 | 22682 | 255269 |

### ALL / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 543 | 0 | 525 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 770 | 0 | 741 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 6 | 0 | 6 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 6 | 0 | 6 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 18 | 0 | 18 | 0 |
| K1:C3:two_accents:evidence_tie | 58 | 0 | 29 | 0 |
| K1:C3:two_accents:rule_held_back | 8094 | 0 | 3535 | 18 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 956 | 0 | 917 | 2 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 48 | 0 | 46 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1782 | 0 | 1627 | 1 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 3 | 0 | 3 | 0 |
| detector_clipped_bottom | 176335 | 0 | 68784 | 1203 |
| detector_clipped_top | 420955 | 0 | 89886 | 4608 |
| detector_localisation_unknown | 151696 | 0 | 46253 | 0 |
| detector_segmentation_uncertain | 254880 | 0 | 60333 | 276 |
| detector_unnamed_mark | 40015 | 0 | 26798 | 102 |
| edit_guard:base_or_character_mismatch | 4440 | 13689 | 13689 | 0 |
| edit_guard:punctuation_mismatch | 16841 | 14960 | 14960 | 78 |
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
| mark_kind_disagreement | 298710 | 0 | 91946 | 5414 |
| r1_evidence_UNKNOWN | 1567 | 0 | 1567 | 0 |
| r1_missing | 4770 | 0 | 2991 | 0 |
| r1_uncertainty:out_of_image_span | 1567 | 0 | 1567 | 0 |
| r1_unscored:line_confidence_below_0.5 | 149 | 0 | 9 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 1735 | 0 | 941 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 2886 | 0 | 2129 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1685 | 0 | 1580 | 18 |
| sf6:deletion_needs_two_positive_absences:keraia | 1786 | 0 | 1652 | 1 |
| sf6:deletion_needs_two_positive_absences:mark | 59885 | 0 | 20459 | 270 |
| sf6:deletion_needs_two_positive_absences:other | 226929 | 0 | 18993 | 1 |
| sf6:deletion_needs_two_positive_absences:quote | 2000 | 0 | 1953 | 69 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 71761 |
| clipping | 99259 |
| K1 | 5313 |
| edit-guard | 22768 |
| A/B disagreement | 0 |
| kind disagreement | 91946 |
| R1 uncertainty | 4502 |
| other/unclassified | 33060 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 9491 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 7174 |
| ["detector_clipped_bottom","detector_clipped_top"] | 6696 |
| ["mark_kind_disagreement"] | 5414 |
| ["detector_clipped_top","mark_kind_disagreement"] | 5155 |
| ["detector_clipped_top"] | 4608 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 4594 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 4095 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 3471 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 3207 |

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
| K1:C4:grave_not_final:impossible_by_rule | 219 | 0 | 206 | 0 |
| detector_clipped_bottom | 15216 | 0 | 6417 | 143 |
| detector_clipped_top | 39943 | 0 | 8844 | 645 |
| detector_localisation_unknown | 8743 | 0 | 3355 | 0 |
| detector_segmentation_uncertain | 17178 | 0 | 5101 | 26 |
| detector_unnamed_mark | 2410 | 0 | 1955 | 9 |
| edit_guard:base_or_character_mismatch | 389 | 1293 | 1293 | 0 |
| edit_guard:punctuation_mismatch | 1288 | 1495 | 1495 | 9 |
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
| mark_kind_disagreement | 26522 | 0 | 9608 | 902 |
| r1_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_missing | 440 | 0 | 249 | 0 |
| r1_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 151 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 269 | 0 | 201 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 166 | 0 | 162 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 125 | 0 | 117 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 5388 | 0 | 1937 | 43 |
| sf6:deletion_needs_two_positive_absences:other | 19982 | 0 | 1854 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 332 | 0 | 330 | 15 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6062 |
| clipping | 9669 |
| K1 | 616 |
| edit-guard | 2224 |
| A/B disagreement | 0 |
| kind disagreement | 9608 |
| R1 uncertainty | 299 |
| other/unclassified | 3212 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 1299 |
| ["mark_kind_disagreement"] | 902 |
| ["detector_clipped_bottom","detector_clipped_top"] | 888 |
| ["detector_clipped_top","mark_kind_disagreement"] | 740 |
| ["detector_clipped_top"] | 645 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 464 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 464 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 404 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 332 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 278 |

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
| edit_guard:punctuation_mismatch | 0 | 19 | 19 | 1 |
| mark_kind_disagreement | 241 | 0 | 116 | 23 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 13 | 0 | 10 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 9 | 0 | 7 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 52 | 0 | 9 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 50 |
| clipping | 159 |
| K1 | 5 |
| edit-guard | 19 |
| A/B disagreement | 0 |
| kind disagreement | 116 |
| R1 uncertainty | 0 |
| other/unclassified | 23 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 41 |
| ["mark_kind_disagreement"] | 23 |
| ["detector_clipped_top"] | 20 |
| ["detector_clipped_bottom"] | 19 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 17 |
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
| detector_clipped_bottom | 44633 | 0 | 16119 | 72 |
| detector_clipped_top | 98404 | 0 | 20688 | 222 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 49 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 10 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 0 |
| edit_guard:punctuation_mismatch | 1472 | 2778 | 2778 | 0 |
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
| mark_kind_disagreement | 111173 | 0 | 21977 | 142 |
| r1_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_missing | 1452 | 0 | 955 | 0 |
| r1_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 146 | 0 | 144 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 110 | 0 | 104 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 13124 | 0 | 5381 | 6 |
| sf6:deletion_needs_two_positive_absences:other | 45081 | 0 | 4338 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 236 | 0 | 230 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4762 |
| A/B disagreement | 0 |
| kind disagreement | 21977 |
| R1 uncertainty | 1829 |
| other/unclassified | 8007 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 3481 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 2366 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 1821 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1228 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1118 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 1057 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 839 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 739 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 665 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 546 |

### round1 / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 0 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 9 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 2 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 1 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 527 |
| detector_clipped_top | 140308 | 0 | 29544 | 2040 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 119 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 35 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 0 |
| edit_guard:punctuation_mismatch | 9153 | 6330 | 6330 | 52 |
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
| mark_kind_disagreement | 73450 | 0 | 30611 | 2639 |
| r1_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_missing | 1687 | 0 | 1129 | 0 |
| r1_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 801 | 0 | 737 | 11 |
| sf6:deletion_needs_two_positive_absences:keraia | 555 | 0 | 511 | 1 |
| sf6:deletion_needs_two_positive_absences:mark | 24346 | 0 | 7310 | 137 |
| sf6:deletion_needs_two_positive_absences:other | 97421 | 0 | 7498 | 1 |
| sf6:deletion_needs_two_positive_absences:quote | 934 | 0 | 915 | 44 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9185 |
| A/B disagreement | 0 |
| kind disagreement | 30611 |
| R1 uncertainty | 1276 |
| other/unclassified | 12135 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 3885 |
| ["detector_clipped_bottom","detector_clipped_top"] | 2922 |
| ["mark_kind_disagreement"] | 2639 |
| ["detector_clipped_top","mark_kind_disagreement"] | 2207 |
| ["detector_clipped_top"] | 2040 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1616 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 1220 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1052 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 985 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 872 |

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
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 0 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 200 |
| detector_clipped_top | 48664 | 0 | 10763 | 851 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 46 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 22 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 0 |
| edit_guard:punctuation_mismatch | 1491 | 2083 | 2083 | 15 |
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
| mark_kind_disagreement | 27905 | 0 | 11778 | 1445 |
| r1_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_missing | 434 | 0 | 268 | 0 |
| r1_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 279 | 0 | 258 | 7 |
| sf6:deletion_needs_two_positive_absences:keraia | 425 | 0 | 402 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 6370 | 0 | 2418 | 69 |
| sf6:deletion_needs_two_positive_absences:other | 23112 | 0 | 2395 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 250 | 0 | 233 | 4 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3047 |
| A/B disagreement | 0 |
| kind disagreement | 11778 |
| R1 uncertainty | 354 |
| other/unclassified | 4205 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 1607 |
| ["mark_kind_disagreement"] | 1445 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1137 |
| ["detector_clipped_top","mark_kind_disagreement"] | 959 |
| ["detector_clipped_top"] | 851 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 495 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 405 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 371 |
| ["detector_segmentation_uncertain","mark_kind_disagreement"] | 324 |
| ["detector_unnamed_mark","mark_kind_disagreement"] | 297 |

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
| detector_clipped_bottom | 40732 | 0 | 15658 | 242 |
| detector_clipped_top | 93007 | 0 | 19927 | 830 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 36 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 26 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 0 |
| edit_guard:punctuation_mismatch | 3437 | 2255 | 2255 | 1 |
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
| mark_kind_disagreement | 59419 | 0 | 17856 | 263 |
| r1_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_missing | 757 | 0 | 390 | 0 |
| r1_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 292 | 0 | 278 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 558 | 0 | 508 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 10648 | 0 | 3406 | 13 |
| sf6:deletion_needs_two_positive_absences:other | 41281 | 0 | 2899 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 248 | 0 | 245 | 6 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3531 |
| A/B disagreement | 0 |
| kind disagreement | 17856 |
| R1 uncertainty | 744 |
| other/unclassified | 5478 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 2328 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 2285 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1365 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1208 |
| ["detector_clipped_top","mark_kind_disagreement"] | 967 |
| ["detector_clipped_top"] | 830 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 812 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 768 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 684 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 598 |

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
| K1:C4:grave_not_final:impossible_by_rule | 214 | 0 | 201 | 0 |
| detector_clipped_bottom | 15059 | 0 | 6360 | 142 |
| detector_clipped_top | 39633 | 0 | 8777 | 641 |
| detector_localisation_unknown | 8716 | 0 | 3345 | 0 |
| detector_segmentation_uncertain | 17133 | 0 | 5085 | 26 |
| detector_unnamed_mark | 2392 | 0 | 1939 | 9 |
| edit_guard:base_or_character_mismatch | 389 | 1258 | 1258 | 0 |
| edit_guard:punctuation_mismatch | 1184 | 1453 | 1453 | 8 |
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
| mark_kind_disagreement | 26287 | 0 | 9517 | 891 |
| r1_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_missing | 418 | 0 | 244 | 0 |
| r1_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 132 | 0 | 51 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 266 | 0 | 200 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 154 | 0 | 150 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 125 | 0 | 117 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 5230 | 0 | 1897 | 41 |
| sf6:deletion_needs_two_positive_absences:other | 19239 | 0 | 1812 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 331 | 0 | 329 | 15 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6032 |
| clipping | 9594 |
| K1 | 609 |
| edit-guard | 2175 |
| A/B disagreement | 0 |
| kind disagreement | 9517 |
| R1 uncertainty | 294 |
| other/unclassified | 3154 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 1285 |
| ["mark_kind_disagreement"] | 891 |
| ["detector_clipped_bottom","detector_clipped_top"] | 879 |
| ["detector_clipped_top","mark_kind_disagreement"] | 734 |
| ["detector_clipped_top"] | 641 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 464 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 463 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 402 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 332 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 276 |

### ALL / anemi_round1

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 0 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 9 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 2 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 1 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 527 |
| detector_clipped_top | 140308 | 0 | 29544 | 2040 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 119 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 35 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 0 |
| edit_guard:punctuation_mismatch | 9153 | 6330 | 6330 | 52 |
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
| mark_kind_disagreement | 73450 | 0 | 30611 | 2639 |
| r1_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_missing | 1687 | 0 | 1129 | 0 |
| r1_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 801 | 0 | 737 | 11 |
| sf6:deletion_needs_two_positive_absences:keraia | 555 | 0 | 511 | 1 |
| sf6:deletion_needs_two_positive_absences:mark | 24346 | 0 | 7310 | 137 |
| sf6:deletion_needs_two_positive_absences:other | 97421 | 0 | 7498 | 1 |
| sf6:deletion_needs_two_positive_absences:quote | 934 | 0 | 915 | 44 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9185 |
| A/B disagreement | 0 |
| kind disagreement | 30611 |
| R1 uncertainty | 1276 |
| other/unclassified | 12135 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 3885 |
| ["detector_clipped_bottom","detector_clipped_top"] | 2922 |
| ["mark_kind_disagreement"] | 2639 |
| ["detector_clipped_top","mark_kind_disagreement"] | 2207 |
| ["detector_clipped_top"] | 2040 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1616 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 1220 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1052 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 985 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 872 |

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
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 0 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 200 |
| detector_clipped_top | 48664 | 0 | 10763 | 851 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 46 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 22 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 0 |
| edit_guard:punctuation_mismatch | 1491 | 2083 | 2083 | 15 |
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
| mark_kind_disagreement | 27905 | 0 | 11778 | 1445 |
| r1_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_missing | 434 | 0 | 268 | 0 |
| r1_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 279 | 0 | 258 | 7 |
| sf6:deletion_needs_two_positive_absences:keraia | 425 | 0 | 402 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 6370 | 0 | 2418 | 69 |
| sf6:deletion_needs_two_positive_absences:other | 23112 | 0 | 2395 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 250 | 0 | 233 | 4 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3047 |
| A/B disagreement | 0 |
| kind disagreement | 11778 |
| R1 uncertainty | 354 |
| other/unclassified | 4205 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 1607 |
| ["mark_kind_disagreement"] | 1445 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1137 |
| ["detector_clipped_top","mark_kind_disagreement"] | 959 |
| ["detector_clipped_top"] | 851 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 495 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 405 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 371 |
| ["detector_segmentation_uncertain","mark_kind_disagreement"] | 324 |
| ["detector_unnamed_mark","mark_kind_disagreement"] | 297 |

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
| edit_guard:punctuation_mismatch | 0 | 22 | 22 | 1 |
| mark_kind_disagreement | 75 | 0 | 49 | 4 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 5 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 17 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 252 | 0 | 20 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 13 |
| clipping | 61 |
| K1 | 3 |
| edit-guard | 24 |
| A/B disagreement | 0 |
| kind disagreement | 49 |
| R1 uncertainty | 0 |
| other/unclassified | 32 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 13 |
| ["detector_clipped_bottom","detector_clipped_top"] | 7 |
| ["detector_clipped_top","mark_kind_disagreement"] | 5 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["detector_clipped_top"] | 4 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 4 |
| ["edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["mark_kind_disagreement"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |

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
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 7 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 9 | 0 | 7 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 48 | 0 | 5 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 46 |
| clipping | 157 |
| K1 | 0 |
| edit-guard | 9 |
| A/B disagreement | 0 |
| kind disagreement | 83 |
| R1 uncertainty | 0 |
| other/unclassified | 14 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 41 |
| ["detector_clipped_top"] | 20 |
| ["detector_clipped_bottom"] | 19 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 17 |
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
| edit_guard:punctuation_mismatch | 0 | 10 | 10 | 1 |
| mark_kind_disagreement | 57 | 0 | 33 | 19 |
| sf6:deletion_needs_two_positive_absences:keraia | 6 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 4 | 0 | 4 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 2 |
| K1 | 5 |
| edit-guard | 10 |
| A/B disagreement | 0 |
| kind disagreement | 33 |
| R1 uncertainty | 0 |
| other/unclassified | 9 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_kind_disagreement"] | 19 |
| ["detector_segmentation_uncertain","mark_kind_disagreement"] | 3 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","mark_kind_disagreement"] | 2 |
| ["detector_clipped_top","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:keraia"] | 2 |
| ["edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:keraia"] | 2 |
| ["edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:other"] | 2 |
| ["edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:other"] | 2 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_unnamed_mark","mark_kind_disagreement"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:keraia"] | 1 |
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
| sf6:deletion_needs_two_positive_absences:mark | 4 | 0 | 2 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 39 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 7 |
| K1 | 0 |
| edit-guard | 2 |
| A/B disagreement | 0 |
| kind disagreement | 10 |
| R1 uncertainty | 1 |
| other/unclassified | 2 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2 |
| ["detector_clipped_bottom","mark_kind_disagreement"] | 2 |
| ["mark_kind_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 1 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","mark_kind_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
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
| detector_unnamed_mark | 1 | 0 | 1 | 0 |
| mark_kind_disagreement | 1 | 0 | 1 | 1 |
| sf6:deletion_needs_two_positive_absences:mark | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 1 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 1 |
| R1 uncertainty | 0 |
| other/unclassified | 1 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_unnamed_mark","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
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
| edit_guard:punctuation_mismatch | 104 | 19 | 19 | 0 |
| edit_guard:unsupported_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| mark_kind_disagreement | 133 | 0 | 30 | 3 |
| r1_missing | 21 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 18 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 3 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 7 | 0 | 7 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 106 | 0 | 20 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 452 | 0 | 21 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 12 |
| clipping | 7 |
| K1 | 4 |
| edit-guard | 23 |
| A/B disagreement | 0 |
| kind disagreement | 30 |
| R1 uncertainty | 4 |
| other/unclassified | 23 |

| Top exact reason set | Lines |
|---|---:|
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["mark_kind_disagreement"] | 3 |
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:apostrophe","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 2 |
| ["mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["K1:C1:breathing_not_initial:impossible_by_rule","K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","edit_guard:unsupported_character:28","edit_guard:unsupported_raw_character:28","mark_kind_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","r1_unscored:width_outside_0.2_2.0_median_ctc","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:apostrophe","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |

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
| detector_clipped_bottom | 44633 | 0 | 16119 | 72 |
| detector_clipped_top | 98404 | 0 | 20688 | 222 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 49 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 10 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 0 |
| edit_guard:punctuation_mismatch | 1472 | 2778 | 2778 | 0 |
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
| mark_kind_disagreement | 111173 | 0 | 21977 | 142 |
| r1_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_missing | 1452 | 0 | 955 | 0 |
| r1_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 146 | 0 | 144 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 110 | 0 | 104 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 13124 | 0 | 5381 | 6 |
| sf6:deletion_needs_two_positive_absences:other | 45081 | 0 | 4338 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 236 | 0 | 230 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4762 |
| A/B disagreement | 0 |
| kind disagreement | 21977 |
| R1 uncertainty | 1829 |
| other/unclassified | 8007 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 3481 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 2366 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 1821 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1228 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1118 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 1057 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 839 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 739 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 665 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 546 |

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
| detector_clipped_bottom | 40732 | 0 | 15658 | 242 |
| detector_clipped_top | 93007 | 0 | 19927 | 830 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 36 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 26 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 0 |
| edit_guard:punctuation_mismatch | 3437 | 2255 | 2255 | 1 |
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
| mark_kind_disagreement | 59419 | 0 | 17856 | 263 |
| r1_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_missing | 757 | 0 | 390 | 0 |
| r1_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 292 | 0 | 278 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 558 | 0 | 508 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 10648 | 0 | 3406 | 13 |
| sf6:deletion_needs_two_positive_absences:other | 41281 | 0 | 2899 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 248 | 0 | 245 | 6 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3531 |
| A/B disagreement | 0 |
| kind disagreement | 17856 |
| R1 uncertainty | 744 |
| other/unclassified | 5478 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 2328 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 2285 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1365 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1208 |
| ["detector_clipped_top","mark_kind_disagreement"] | 967 |
| ["detector_clipped_top"] | 830 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 812 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 768 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 684 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 598 |

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
| K1:C4:grave_not_final:impossible_by_rule | 214 | 0 | 201 | 0 |
| detector_clipped_bottom | 15059 | 0 | 6360 | 142 |
| detector_clipped_top | 39633 | 0 | 8777 | 641 |
| detector_localisation_unknown | 8716 | 0 | 3345 | 0 |
| detector_segmentation_uncertain | 17133 | 0 | 5085 | 26 |
| detector_unnamed_mark | 2392 | 0 | 1939 | 9 |
| edit_guard:base_or_character_mismatch | 389 | 1258 | 1258 | 0 |
| edit_guard:punctuation_mismatch | 1184 | 1453 | 1453 | 8 |
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
| mark_kind_disagreement | 26287 | 0 | 9517 | 891 |
| r1_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_missing | 418 | 0 | 244 | 0 |
| r1_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 132 | 0 | 51 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 266 | 0 | 200 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 154 | 0 | 150 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 125 | 0 | 117 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 5230 | 0 | 1897 | 41 |
| sf6:deletion_needs_two_positive_absences:other | 19239 | 0 | 1812 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 331 | 0 | 329 | 15 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6032 |
| clipping | 9594 |
| K1 | 609 |
| edit-guard | 2175 |
| A/B disagreement | 0 |
| kind disagreement | 9517 |
| R1 uncertainty | 294 |
| other/unclassified | 3154 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 1285 |
| ["mark_kind_disagreement"] | 891 |
| ["detector_clipped_bottom","detector_clipped_top"] | 879 |
| ["detector_clipped_top","mark_kind_disagreement"] | 734 |
| ["detector_clipped_top"] | 641 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 464 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 463 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 402 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 332 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 276 |

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
| edit_guard:punctuation_mismatch | 0 | 22 | 22 | 1 |
| mark_kind_disagreement | 75 | 0 | 49 | 4 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 5 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 17 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 252 | 0 | 20 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 13 |
| clipping | 61 |
| K1 | 3 |
| edit-guard | 24 |
| A/B disagreement | 0 |
| kind disagreement | 49 |
| R1 uncertainty | 0 |
| other/unclassified | 32 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 13 |
| ["detector_clipped_bottom","detector_clipped_top"] | 7 |
| ["detector_clipped_top","mark_kind_disagreement"] | 5 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["detector_clipped_top"] | 4 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 4 |
| ["edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["mark_kind_disagreement"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |

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
| sf6:deletion_needs_two_positive_absences:mark | 4 | 0 | 2 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 39 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 7 |
| K1 | 0 |
| edit-guard | 2 |
| A/B disagreement | 0 |
| kind disagreement | 10 |
| R1 uncertainty | 1 |
| other/unclassified | 2 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2 |
| ["detector_clipped_bottom","mark_kind_disagreement"] | 2 |
| ["mark_kind_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 1 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","mark_kind_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
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
| detector_unnamed_mark | 1 | 0 | 1 | 0 |
| mark_kind_disagreement | 1 | 0 | 1 | 1 |
| sf6:deletion_needs_two_positive_absences:mark | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 1 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 1 |
| R1 uncertainty | 0 |
| other/unclassified | 1 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_unnamed_mark","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
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
| edit_guard:punctuation_mismatch | 104 | 19 | 19 | 0 |
| edit_guard:unsupported_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| mark_kind_disagreement | 133 | 0 | 30 | 3 |
| r1_missing | 21 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 18 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 3 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 7 | 0 | 7 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 106 | 0 | 20 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 452 | 0 | 21 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 12 |
| clipping | 7 |
| K1 | 4 |
| edit-guard | 23 |
| A/B disagreement | 0 |
| kind disagreement | 30 |
| R1 uncertainty | 4 |
| other/unclassified | 23 |

| Top exact reason set | Lines |
|---|---:|
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["mark_kind_disagreement"] | 3 |
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:apostrophe","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 2 |
| ["mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["K1:C1:breathing_not_initial:impossible_by_rule","K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","edit_guard:unsupported_character:28","edit_guard:unsupported_raw_character:28","mark_kind_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","r1_unscored:width_outside_0.2_2.0_median_ctc","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","mark_kind_disagreement"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:apostrophe","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |

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
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 7 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 9 | 0 | 7 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 48 | 0 | 5 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 46 |
| clipping | 157 |
| K1 | 0 |
| edit-guard | 9 |
| A/B disagreement | 0 |
| kind disagreement | 83 |
| R1 uncertainty | 0 |
| other/unclassified | 14 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 41 |
| ["detector_clipped_top"] | 20 |
| ["detector_clipped_bottom"] | 19 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 17 |
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
| edit_guard:punctuation_mismatch | 0 | 10 | 10 | 1 |
| mark_kind_disagreement | 57 | 0 | 33 | 19 |
| sf6:deletion_needs_two_positive_absences:keraia | 6 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 4 | 0 | 4 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 2 |
| K1 | 5 |
| edit-guard | 10 |
| A/B disagreement | 0 |
| kind disagreement | 33 |
| R1 uncertainty | 0 |
| other/unclassified | 9 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_kind_disagreement"] | 19 |
| ["detector_segmentation_uncertain","mark_kind_disagreement"] | 3 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","mark_kind_disagreement"] | 2 |
| ["detector_clipped_top","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:keraia"] | 2 |
| ["edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:keraia"] | 2 |
| ["edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:other"] | 2 |
| ["edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:other"] | 2 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_unnamed_mark","mark_kind_disagreement"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:keraia"] | 1 |
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
| detector_clipped_bottom | 44633 | 0 | 16119 | 72 |
| detector_clipped_top | 98404 | 0 | 20688 | 222 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 49 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 10 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 0 |
| edit_guard:punctuation_mismatch | 1472 | 2778 | 2778 | 0 |
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
| mark_kind_disagreement | 111173 | 0 | 21977 | 142 |
| r1_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_missing | 1452 | 0 | 955 | 0 |
| r1_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 146 | 0 | 144 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 110 | 0 | 104 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 13124 | 0 | 5381 | 6 |
| sf6:deletion_needs_two_positive_absences:other | 45081 | 0 | 4338 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 236 | 0 | 230 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4762 |
| A/B disagreement | 0 |
| kind disagreement | 21977 |
| R1 uncertainty | 1829 |
| other/unclassified | 8007 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 3481 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 2366 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 1821 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1228 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1118 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 1057 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 839 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 739 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 665 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 546 |

### round1 / anemi_round1

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 0 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 9 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 2 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 1 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 527 |
| detector_clipped_top | 140308 | 0 | 29544 | 2040 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 119 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 35 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 0 |
| edit_guard:punctuation_mismatch | 9153 | 6330 | 6330 | 52 |
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
| mark_kind_disagreement | 73450 | 0 | 30611 | 2639 |
| r1_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_missing | 1687 | 0 | 1129 | 0 |
| r1_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 801 | 0 | 737 | 11 |
| sf6:deletion_needs_two_positive_absences:keraia | 555 | 0 | 511 | 1 |
| sf6:deletion_needs_two_positive_absences:mark | 24346 | 0 | 7310 | 137 |
| sf6:deletion_needs_two_positive_absences:other | 97421 | 0 | 7498 | 1 |
| sf6:deletion_needs_two_positive_absences:quote | 934 | 0 | 915 | 44 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9185 |
| A/B disagreement | 0 |
| kind disagreement | 30611 |
| R1 uncertainty | 1276 |
| other/unclassified | 12135 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 3885 |
| ["detector_clipped_bottom","detector_clipped_top"] | 2922 |
| ["mark_kind_disagreement"] | 2639 |
| ["detector_clipped_top","mark_kind_disagreement"] | 2207 |
| ["detector_clipped_top"] | 2040 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1616 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 1220 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1052 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 985 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 872 |

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
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 0 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 200 |
| detector_clipped_top | 48664 | 0 | 10763 | 851 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 46 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 22 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 0 |
| edit_guard:punctuation_mismatch | 1491 | 2083 | 2083 | 15 |
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
| mark_kind_disagreement | 27905 | 0 | 11778 | 1445 |
| r1_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_missing | 434 | 0 | 268 | 0 |
| r1_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 279 | 0 | 258 | 7 |
| sf6:deletion_needs_two_positive_absences:keraia | 425 | 0 | 402 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 6370 | 0 | 2418 | 69 |
| sf6:deletion_needs_two_positive_absences:other | 23112 | 0 | 2395 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 250 | 0 | 233 | 4 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3047 |
| A/B disagreement | 0 |
| kind disagreement | 11778 |
| R1 uncertainty | 354 |
| other/unclassified | 4205 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 1607 |
| ["mark_kind_disagreement"] | 1445 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1137 |
| ["detector_clipped_top","mark_kind_disagreement"] | 959 |
| ["detector_clipped_top"] | 851 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 495 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 405 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 371 |
| ["detector_segmentation_uncertain","mark_kind_disagreement"] | 324 |
| ["detector_unnamed_mark","mark_kind_disagreement"] | 297 |

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
| detector_clipped_bottom | 40732 | 0 | 15658 | 242 |
| detector_clipped_top | 93007 | 0 | 19927 | 830 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 36 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 26 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 0 |
| edit_guard:punctuation_mismatch | 3437 | 2255 | 2255 | 1 |
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
| mark_kind_disagreement | 59419 | 0 | 17856 | 263 |
| r1_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_missing | 757 | 0 | 390 | 0 |
| r1_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 292 | 0 | 278 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 558 | 0 | 508 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 10648 | 0 | 3406 | 13 |
| sf6:deletion_needs_two_positive_absences:other | 41281 | 0 | 2899 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 248 | 0 | 245 | 6 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3531 |
| A/B disagreement | 0 |
| kind disagreement | 17856 |
| R1 uncertainty | 744 |
| other/unclassified | 5478 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_kind_disagreement"] | 2328 |
| ["detector_clipped_bottom","detector_clipped_top","mark_kind_disagreement"] | 2285 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1365 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 1208 |
| ["detector_clipped_top","mark_kind_disagreement"] | 967 |
| ["detector_clipped_top"] | 830 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 812 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_kind_disagreement"] | 768 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_kind_disagreement"] | 684 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark","mark_kind_disagreement"] | 598 |
## FULL

| Wave | Source | Lines | HOLD | Held glyph slots |
|---|---|---:|---:|---:|
| ALL | ALL | 124669 | 119169 | 1362494 |
| mixed | ALL | 13227 | 12514 | 120320 |
| openarchives | ALL | 235 | 209 | 1232 |
| parliament | ALL | 27224 | 27094 | 414822 |
| round1 | ALL | 43869 | 41057 | 432686 |
| round2 | ALL | 17026 | 15596 | 136922 |
| vouli | ALL | 23088 | 22699 | 256512 |
| ALL | anemi_mixed | 13084 | 12389 | 118534 |
| ALL | anemi_round1 | 43869 | 41057 | 432686 |
| ALL | anemi_round2 | 17026 | 15596 | 136922 |
| ALL | archive_b28038630 | 97 | 80 | 719 |
| ALL | openarchives_Pandemos | 185 | 172 | 1130 |
| ALL | openarchives_kallipos | 50 | 37 | 102 |
| ALL | openarchives_mixed_Pandemos | 13 | 12 | 118 |
| ALL | openarchives_mixed_apothesis | 1 | 1 | 1 |
| ALL | openarchives_mixed_ktisis | 2 | 2 | 3 |
| ALL | openarchives_mixed_ntua | 30 | 30 | 945 |
| ALL | parliament_proceedings_1975_2000 | 27224 | 27094 | 414822 |
| ALL | vouli_parliament_1850s | 23088 | 22699 | 256512 |
| mixed | anemi_mixed | 13084 | 12389 | 118534 |
| mixed | archive_b28038630 | 97 | 80 | 719 |
| mixed | openarchives_mixed_Pandemos | 13 | 12 | 118 |
| mixed | openarchives_mixed_apothesis | 1 | 1 | 1 |
| mixed | openarchives_mixed_ktisis | 2 | 2 | 3 |
| mixed | openarchives_mixed_ntua | 30 | 30 | 945 |
| openarchives | openarchives_Pandemos | 185 | 172 | 1130 |
| openarchives | openarchives_kallipos | 50 | 37 | 102 |
| parliament | parliament_proceedings_1975_2000 | 27224 | 27094 | 414822 |
| round1 | anemi_round1 | 43869 | 41057 | 432686 |
| round2 | anemi_round2 | 17026 | 15596 | 136922 |
| vouli | vouli_parliament_1850s | 23088 | 22699 | 256512 |

### ALL / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 543 | 0 | 525 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 770 | 0 | 741 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 6 | 0 | 6 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 6 | 0 | 6 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 18 | 0 | 18 | 0 |
| K1:C3:two_accents:evidence_tie | 58 | 0 | 29 | 0 |
| K1:C3:two_accents:rule_held_back | 8094 | 0 | 3535 | 15 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 956 | 0 | 917 | 2 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 48 | 0 | 46 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1782 | 0 | 1627 | 1 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 3 | 0 | 3 | 0 |
| detector_clipped_bottom | 176335 | 0 | 68784 | 1127 |
| detector_clipped_top | 420955 | 0 | 89886 | 4319 |
| detector_localisation_unknown | 151696 | 0 | 46253 | 0 |
| detector_segmentation_uncertain | 254880 | 0 | 60333 | 251 |
| detector_unnamed_mark | 40015 | 0 | 26798 | 86 |
| edit_guard:base_or_character_mismatch | 4440 | 13689 | 13689 | 0 |
| edit_guard:punctuation_mismatch | 16841 | 14960 | 14960 | 70 |
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
| mark_set_disagreement | 315973 | 0 | 94675 | 5727 |
| r1_evidence_UNKNOWN | 1567 | 0 | 1567 | 0 |
| r1_missing | 4770 | 0 | 2991 | 0 |
| r1_uncertainty:out_of_image_span | 1567 | 0 | 1567 | 0 |
| r1_unscored:line_confidence_below_0.5 | 149 | 0 | 9 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 1735 | 0 | 941 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 2886 | 0 | 2129 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1685 | 0 | 1580 | 17 |
| sf6:deletion_needs_two_positive_absences:keraia | 1786 | 0 | 1652 | 1 |
| sf6:deletion_needs_two_positive_absences:mark | 59885 | 0 | 20459 | 229 |
| sf6:deletion_needs_two_positive_absences:other | 226929 | 0 | 18993 | 1 |
| sf6:deletion_needs_two_positive_absences:quote | 2000 | 0 | 1953 | 59 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 71761 |
| clipping | 99259 |
| K1 | 5313 |
| edit-guard | 22768 |
| A/B disagreement | 0 |
| kind disagreement | 94675 |
| R1 uncertainty | 4502 |
| other/unclassified | 33060 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 9996 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 7361 |
| ["detector_clipped_bottom","detector_clipped_top"] | 6191 |
| ["mark_set_disagreement"] | 5727 |
| ["detector_clipped_top","mark_set_disagreement"] | 5444 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 4717 |
| ["detector_clipped_top"] | 4319 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 4126 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 3501 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 3264 |

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
| K1:C4:grave_not_final:impossible_by_rule | 219 | 0 | 206 | 0 |
| detector_clipped_bottom | 15216 | 0 | 6417 | 138 |
| detector_clipped_top | 39943 | 0 | 8844 | 585 |
| detector_localisation_unknown | 8743 | 0 | 3355 | 0 |
| detector_segmentation_uncertain | 17178 | 0 | 5101 | 22 |
| detector_unnamed_mark | 2410 | 0 | 1955 | 5 |
| edit_guard:base_or_character_mismatch | 389 | 1293 | 1293 | 0 |
| edit_guard:punctuation_mismatch | 1288 | 1495 | 1495 | 7 |
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
| mark_set_disagreement | 28258 | 0 | 9933 | 950 |
| r1_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_missing | 440 | 0 | 249 | 0 |
| r1_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 151 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 269 | 0 | 201 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 166 | 0 | 162 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 125 | 0 | 117 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 5388 | 0 | 1937 | 34 |
| sf6:deletion_needs_two_positive_absences:other | 19982 | 0 | 1854 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 332 | 0 | 330 | 15 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6062 |
| clipping | 9669 |
| K1 | 616 |
| edit-guard | 2224 |
| A/B disagreement | 0 |
| kind disagreement | 9933 |
| R1 uncertainty | 299 |
| other/unclassified | 3212 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 1360 |
| ["mark_set_disagreement"] | 950 |
| ["detector_clipped_bottom","detector_clipped_top"] | 827 |
| ["detector_clipped_top","mark_set_disagreement"] | 800 |
| ["detector_clipped_top"] | 585 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 475 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 466 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 410 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 342 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 279 |

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
| edit_guard:punctuation_mismatch | 0 | 19 | 19 | 1 |
| mark_set_disagreement | 256 | 0 | 122 | 25 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 13 | 0 | 10 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 9 | 0 | 7 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 52 | 0 | 9 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 50 |
| clipping | 159 |
| K1 | 5 |
| edit-guard | 19 |
| A/B disagreement | 0 |
| kind disagreement | 122 |
| R1 uncertainty | 0 |
| other/unclassified | 23 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 37 |
| ["mark_set_disagreement"] | 25 |
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 21 |
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
| detector_clipped_bottom | 44633 | 0 | 16119 | 68 |
| detector_clipped_top | 98404 | 0 | 20688 | 209 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 45 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 8 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 0 |
| edit_guard:punctuation_mismatch | 1472 | 2778 | 2778 | 0 |
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
| mark_set_disagreement | 116911 | 0 | 22520 | 146 |
| r1_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_missing | 1452 | 0 | 955 | 0 |
| r1_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 146 | 0 | 144 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 110 | 0 | 104 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 13124 | 0 | 5381 | 6 |
| sf6:deletion_needs_two_positive_absences:other | 45081 | 0 | 4338 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 236 | 0 | 230 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4762 |
| A/B disagreement | 0 |
| kind disagreement | 22520 |
| R1 uncertainty | 1829 |
| other/unclassified | 8007 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 3575 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 2430 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 1845 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1258 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 1075 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1024 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 864 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 686 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 675 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 551 |

### round1 / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 0 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 8 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 2 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 1 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 493 |
| detector_clipped_top | 140308 | 0 | 29544 | 1902 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 109 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 32 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 0 |
| edit_guard:punctuation_mismatch | 9153 | 6330 | 6330 | 50 |
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
| mark_set_disagreement | 78967 | 0 | 31761 | 2801 |
| r1_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_missing | 1687 | 0 | 1129 | 0 |
| r1_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 801 | 0 | 737 | 10 |
| sf6:deletion_needs_two_positive_absences:keraia | 555 | 0 | 511 | 1 |
| sf6:deletion_needs_two_positive_absences:mark | 24346 | 0 | 7310 | 116 |
| sf6:deletion_needs_two_positive_absences:other | 97421 | 0 | 7498 | 1 |
| sf6:deletion_needs_two_positive_absences:quote | 934 | 0 | 915 | 36 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9185 |
| A/B disagreement | 0 |
| kind disagreement | 31761 |
| R1 uncertainty | 1276 |
| other/unclassified | 12135 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 4131 |
| ["mark_set_disagreement"] | 2801 |
| ["detector_clipped_bottom","detector_clipped_top"] | 2676 |
| ["detector_clipped_top","mark_set_disagreement"] | 2345 |
| ["detector_clipped_top"] | 1902 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1656 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 1239 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1079 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1017 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 888 |

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
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 0 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 180 |
| detector_clipped_top | 48664 | 0 | 10763 | 802 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 42 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 19 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 0 |
| edit_guard:punctuation_mismatch | 1491 | 2083 | 2083 | 11 |
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
| mark_set_disagreement | 29904 | 0 | 12180 | 1525 |
| r1_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_missing | 434 | 0 | 268 | 0 |
| r1_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 279 | 0 | 258 | 7 |
| sf6:deletion_needs_two_positive_absences:keraia | 425 | 0 | 402 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 6370 | 0 | 2418 | 59 |
| sf6:deletion_needs_two_positive_absences:other | 23112 | 0 | 2395 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 250 | 0 | 233 | 3 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3047 |
| A/B disagreement | 0 |
| kind disagreement | 12180 |
| R1 uncertainty | 354 |
| other/unclassified | 4205 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 1700 |
| ["mark_set_disagreement"] | 1525 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1044 |
| ["detector_clipped_top","mark_set_disagreement"] | 1008 |
| ["detector_clipped_top"] | 802 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 498 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 422 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 372 |
| ["detector_segmentation_uncertain","mark_set_disagreement"] | 328 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 300 |

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
| detector_clipped_bottom | 40732 | 0 | 15658 | 229 |
| detector_clipped_top | 93007 | 0 | 19927 | 801 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 33 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 22 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 0 |
| edit_guard:punctuation_mismatch | 3437 | 2255 | 2255 | 1 |
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
| mark_set_disagreement | 61677 | 0 | 18159 | 280 |
| r1_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_missing | 757 | 0 | 390 | 0 |
| r1_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 292 | 0 | 278 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 558 | 0 | 508 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 10648 | 0 | 3406 | 12 |
| sf6:deletion_needs_two_positive_absences:other | 41281 | 0 | 2899 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 248 | 0 | 245 | 5 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3531 |
| A/B disagreement | 0 |
| kind disagreement | 18159 |
| R1 uncertainty | 744 |
| other/unclassified | 5478 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 2355 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 2340 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1295 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1233 |
| ["detector_clipped_top","mark_set_disagreement"] | 996 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 814 |
| ["detector_clipped_top"] | 801 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 777 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 697 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 599 |

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
| K1:C4:grave_not_final:impossible_by_rule | 214 | 0 | 201 | 0 |
| detector_clipped_bottom | 15059 | 0 | 6360 | 137 |
| detector_clipped_top | 39633 | 0 | 8777 | 582 |
| detector_localisation_unknown | 8716 | 0 | 3345 | 0 |
| detector_segmentation_uncertain | 17133 | 0 | 5085 | 22 |
| detector_unnamed_mark | 2392 | 0 | 1939 | 5 |
| edit_guard:base_or_character_mismatch | 389 | 1258 | 1258 | 0 |
| edit_guard:punctuation_mismatch | 1184 | 1453 | 1453 | 7 |
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
| mark_set_disagreement | 27999 | 0 | 9837 | 939 |
| r1_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_missing | 418 | 0 | 244 | 0 |
| r1_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 132 | 0 | 51 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 266 | 0 | 200 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 154 | 0 | 150 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 125 | 0 | 117 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 5230 | 0 | 1897 | 32 |
| sf6:deletion_needs_two_positive_absences:other | 19239 | 0 | 1812 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 331 | 0 | 329 | 15 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6032 |
| clipping | 9594 |
| K1 | 609 |
| edit-guard | 2175 |
| A/B disagreement | 0 |
| kind disagreement | 9837 |
| R1 uncertainty | 294 |
| other/unclassified | 3154 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 1346 |
| ["mark_set_disagreement"] | 939 |
| ["detector_clipped_bottom","detector_clipped_top"] | 818 |
| ["detector_clipped_top","mark_set_disagreement"] | 793 |
| ["detector_clipped_top"] | 582 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 475 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 465 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 408 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 342 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 277 |

### ALL / anemi_round1

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 0 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 8 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 2 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 1 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 493 |
| detector_clipped_top | 140308 | 0 | 29544 | 1902 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 109 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 32 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 0 |
| edit_guard:punctuation_mismatch | 9153 | 6330 | 6330 | 50 |
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
| mark_set_disagreement | 78967 | 0 | 31761 | 2801 |
| r1_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_missing | 1687 | 0 | 1129 | 0 |
| r1_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 801 | 0 | 737 | 10 |
| sf6:deletion_needs_two_positive_absences:keraia | 555 | 0 | 511 | 1 |
| sf6:deletion_needs_two_positive_absences:mark | 24346 | 0 | 7310 | 116 |
| sf6:deletion_needs_two_positive_absences:other | 97421 | 0 | 7498 | 1 |
| sf6:deletion_needs_two_positive_absences:quote | 934 | 0 | 915 | 36 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9185 |
| A/B disagreement | 0 |
| kind disagreement | 31761 |
| R1 uncertainty | 1276 |
| other/unclassified | 12135 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 4131 |
| ["mark_set_disagreement"] | 2801 |
| ["detector_clipped_bottom","detector_clipped_top"] | 2676 |
| ["detector_clipped_top","mark_set_disagreement"] | 2345 |
| ["detector_clipped_top"] | 1902 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1656 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 1239 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1079 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1017 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 888 |

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
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 0 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 180 |
| detector_clipped_top | 48664 | 0 | 10763 | 802 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 42 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 19 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 0 |
| edit_guard:punctuation_mismatch | 1491 | 2083 | 2083 | 11 |
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
| mark_set_disagreement | 29904 | 0 | 12180 | 1525 |
| r1_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_missing | 434 | 0 | 268 | 0 |
| r1_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 279 | 0 | 258 | 7 |
| sf6:deletion_needs_two_positive_absences:keraia | 425 | 0 | 402 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 6370 | 0 | 2418 | 59 |
| sf6:deletion_needs_two_positive_absences:other | 23112 | 0 | 2395 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 250 | 0 | 233 | 3 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3047 |
| A/B disagreement | 0 |
| kind disagreement | 12180 |
| R1 uncertainty | 354 |
| other/unclassified | 4205 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 1700 |
| ["mark_set_disagreement"] | 1525 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1044 |
| ["detector_clipped_top","mark_set_disagreement"] | 1008 |
| ["detector_clipped_top"] | 802 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 498 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 422 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 372 |
| ["detector_segmentation_uncertain","mark_set_disagreement"] | 328 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 300 |

### ALL / archive_b28038630

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 2 | 0 | 1 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 130 | 0 | 45 | 1 |
| detector_clipped_top | 254 | 0 | 58 | 3 |
| detector_localisation_unknown | 7 | 0 | 6 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 13 | 13 | 0 |
| edit_guard:punctuation_mismatch | 0 | 22 | 22 | 0 |
| mark_set_disagreement | 92 | 0 | 54 | 4 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 5 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 17 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 252 | 0 | 20 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 13 |
| clipping | 61 |
| K1 | 3 |
| edit-guard | 24 |
| A/B disagreement | 0 |
| kind disagreement | 54 |
| R1 uncertainty | 0 |
| other/unclassified | 32 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 13 |
| ["detector_clipped_bottom","detector_clipped_top"] | 7 |
| ["detector_clipped_top","mark_set_disagreement"] | 6 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 5 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 4 |
| ["edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["mark_set_disagreement"] | 4 |
| ["detector_clipped_top"] | 3 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |

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
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 7 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 9 | 0 | 7 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 48 | 0 | 5 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 46 |
| clipping | 157 |
| K1 | 0 |
| edit-guard | 9 |
| A/B disagreement | 0 |
| kind disagreement | 88 |
| R1 uncertainty | 0 |
| other/unclassified | 14 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 37 |
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 21 |
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
| edit_guard:punctuation_mismatch | 0 | 10 | 10 | 1 |
| mark_set_disagreement | 59 | 0 | 34 | 20 |
| sf6:deletion_needs_two_positive_absences:keraia | 6 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 4 | 0 | 4 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 2 |
| K1 | 5 |
| edit-guard | 10 |
| A/B disagreement | 0 |
| kind disagreement | 34 |
| R1 uncertainty | 0 |
| other/unclassified | 9 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_set_disagreement"] | 20 |
| ["detector_segmentation_uncertain","mark_set_disagreement"] | 3 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","mark_set_disagreement"] | 2 |
| ["detector_clipped_top","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:keraia"] | 2 |
| ["edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:keraia"] | 2 |
| ["edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:other"] | 2 |
| ["edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:other"] | 2 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_unnamed_mark","mark_set_disagreement"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:keraia"] | 1 |
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
| sf6:deletion_needs_two_positive_absences:mark | 4 | 0 | 2 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 39 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 7 |
| K1 | 0 |
| edit-guard | 2 |
| A/B disagreement | 0 |
| kind disagreement | 10 |
| R1 uncertainty | 1 |
| other/unclassified | 2 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 2 |
| ["mark_set_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 1 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","mark_set_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
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
| detector_unnamed_mark | 1 | 0 | 1 | 0 |
| mark_set_disagreement | 1 | 0 | 1 | 1 |
| sf6:deletion_needs_two_positive_absences:mark | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 1 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 1 |
| R1 uncertainty | 0 |
| other/unclassified | 1 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_unnamed_mark","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
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
| edit_guard:punctuation_mismatch | 104 | 19 | 19 | 0 |
| edit_guard:unsupported_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| mark_set_disagreement | 140 | 0 | 30 | 3 |
| r1_missing | 21 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 18 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 3 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 7 | 0 | 7 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 106 | 0 | 20 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 452 | 0 | 21 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 12 |
| clipping | 7 |
| K1 | 4 |
| edit-guard | 23 |
| A/B disagreement | 0 |
| kind disagreement | 30 |
| R1 uncertainty | 4 |
| other/unclassified | 23 |

| Top exact reason set | Lines |
|---|---:|
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["mark_set_disagreement"] | 3 |
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:apostrophe","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 2 |
| ["mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["K1:C1:breathing_not_initial:impossible_by_rule","K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","edit_guard:unsupported_character:28","edit_guard:unsupported_raw_character:28","mark_set_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","r1_unscored:width_outside_0.2_2.0_median_ctc","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:apostrophe","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |

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
| detector_clipped_bottom | 44633 | 0 | 16119 | 68 |
| detector_clipped_top | 98404 | 0 | 20688 | 209 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 45 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 8 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 0 |
| edit_guard:punctuation_mismatch | 1472 | 2778 | 2778 | 0 |
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
| mark_set_disagreement | 116911 | 0 | 22520 | 146 |
| r1_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_missing | 1452 | 0 | 955 | 0 |
| r1_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 146 | 0 | 144 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 110 | 0 | 104 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 13124 | 0 | 5381 | 6 |
| sf6:deletion_needs_two_positive_absences:other | 45081 | 0 | 4338 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 236 | 0 | 230 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4762 |
| A/B disagreement | 0 |
| kind disagreement | 22520 |
| R1 uncertainty | 1829 |
| other/unclassified | 8007 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 3575 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 2430 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 1845 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1258 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 1075 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1024 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 864 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 686 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 675 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 551 |

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
| detector_clipped_bottom | 40732 | 0 | 15658 | 229 |
| detector_clipped_top | 93007 | 0 | 19927 | 801 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 33 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 22 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 0 |
| edit_guard:punctuation_mismatch | 3437 | 2255 | 2255 | 1 |
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
| mark_set_disagreement | 61677 | 0 | 18159 | 280 |
| r1_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_missing | 757 | 0 | 390 | 0 |
| r1_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 292 | 0 | 278 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 558 | 0 | 508 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 10648 | 0 | 3406 | 12 |
| sf6:deletion_needs_two_positive_absences:other | 41281 | 0 | 2899 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 248 | 0 | 245 | 5 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3531 |
| A/B disagreement | 0 |
| kind disagreement | 18159 |
| R1 uncertainty | 744 |
| other/unclassified | 5478 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 2355 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 2340 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1295 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1233 |
| ["detector_clipped_top","mark_set_disagreement"] | 996 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 814 |
| ["detector_clipped_top"] | 801 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 777 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 697 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 599 |

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
| K1:C4:grave_not_final:impossible_by_rule | 214 | 0 | 201 | 0 |
| detector_clipped_bottom | 15059 | 0 | 6360 | 137 |
| detector_clipped_top | 39633 | 0 | 8777 | 582 |
| detector_localisation_unknown | 8716 | 0 | 3345 | 0 |
| detector_segmentation_uncertain | 17133 | 0 | 5085 | 22 |
| detector_unnamed_mark | 2392 | 0 | 1939 | 5 |
| edit_guard:base_or_character_mismatch | 389 | 1258 | 1258 | 0 |
| edit_guard:punctuation_mismatch | 1184 | 1453 | 1453 | 7 |
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
| mark_set_disagreement | 27999 | 0 | 9837 | 939 |
| r1_evidence_UNKNOWN | 52 | 0 | 52 | 0 |
| r1_missing | 418 | 0 | 244 | 0 |
| r1_uncertainty:out_of_image_span | 52 | 0 | 52 | 0 |
| r1_unscored:line_confidence_below_0.5 | 20 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 132 | 0 | 51 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 266 | 0 | 200 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 154 | 0 | 150 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 125 | 0 | 117 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 5230 | 0 | 1897 | 32 |
| sf6:deletion_needs_two_positive_absences:other | 19239 | 0 | 1812 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 331 | 0 | 329 | 15 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6032 |
| clipping | 9594 |
| K1 | 609 |
| edit-guard | 2175 |
| A/B disagreement | 0 |
| kind disagreement | 9837 |
| R1 uncertainty | 294 |
| other/unclassified | 3154 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 1346 |
| ["mark_set_disagreement"] | 939 |
| ["detector_clipped_bottom","detector_clipped_top"] | 818 |
| ["detector_clipped_top","mark_set_disagreement"] | 793 |
| ["detector_clipped_top"] | 582 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 475 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 465 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 408 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 342 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 277 |

### mixed / archive_b28038630

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 2 | 0 | 1 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 130 | 0 | 45 | 1 |
| detector_clipped_top | 254 | 0 | 58 | 3 |
| detector_localisation_unknown | 7 | 0 | 6 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 13 | 13 | 0 |
| edit_guard:punctuation_mismatch | 0 | 22 | 22 | 0 |
| mark_set_disagreement | 92 | 0 | 54 | 4 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 5 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 17 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 252 | 0 | 20 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 13 |
| clipping | 61 |
| K1 | 3 |
| edit-guard | 24 |
| A/B disagreement | 0 |
| kind disagreement | 54 |
| R1 uncertainty | 0 |
| other/unclassified | 32 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 13 |
| ["detector_clipped_bottom","detector_clipped_top"] | 7 |
| ["detector_clipped_top","mark_set_disagreement"] | 6 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 5 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 4 |
| ["edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["mark_set_disagreement"] | 4 |
| ["detector_clipped_top"] | 3 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |

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
| sf6:deletion_needs_two_positive_absences:mark | 4 | 0 | 2 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 39 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 7 |
| K1 | 0 |
| edit-guard | 2 |
| A/B disagreement | 0 |
| kind disagreement | 10 |
| R1 uncertainty | 1 |
| other/unclassified | 2 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 2 |
| ["mark_set_disagreement"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 1 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","mark_set_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
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
| detector_unnamed_mark | 1 | 0 | 1 | 0 |
| mark_set_disagreement | 1 | 0 | 1 | 1 |
| sf6:deletion_needs_two_positive_absences:mark | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 1 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 1 |
| R1 uncertainty | 0 |
| other/unclassified | 1 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_unnamed_mark","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
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
| edit_guard:punctuation_mismatch | 104 | 19 | 19 | 0 |
| edit_guard:unsupported_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_character:54 | 56 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:28 | 35 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:47 | 57 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:54 | 56 | 0 | 1 | 0 |
| mark_set_disagreement | 140 | 0 | 30 | 3 |
| r1_missing | 21 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 18 | 0 | 4 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 3 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 7 | 0 | 7 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 106 | 0 | 20 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 452 | 0 | 21 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 12 |
| clipping | 7 |
| K1 | 4 |
| edit-guard | 23 |
| A/B disagreement | 0 |
| kind disagreement | 30 |
| R1 uncertainty | 4 |
| other/unclassified | 23 |

| Top exact reason set | Lines |
|---|---:|
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["mark_set_disagreement"] | 3 |
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:apostrophe","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 2 |
| ["mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["K1:C1:breathing_not_initial:impossible_by_rule","K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","edit_guard:unsupported_character:28","edit_guard:unsupported_raw_character:28","mark_set_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","r1_unscored:width_outside_0.2_2.0_median_ctc","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","mark_set_disagreement"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:apostrophe","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |

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
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 7 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 9 | 0 | 7 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 48 | 0 | 5 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 46 |
| clipping | 157 |
| K1 | 0 |
| edit-guard | 9 |
| A/B disagreement | 0 |
| kind disagreement | 88 |
| R1 uncertainty | 0 |
| other/unclassified | 14 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 37 |
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 21 |
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
| edit_guard:punctuation_mismatch | 0 | 10 | 10 | 1 |
| mark_set_disagreement | 59 | 0 | 34 | 20 |
| sf6:deletion_needs_two_positive_absences:keraia | 6 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 4 | 0 | 4 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 2 |
| K1 | 5 |
| edit-guard | 10 |
| A/B disagreement | 0 |
| kind disagreement | 34 |
| R1 uncertainty | 0 |
| other/unclassified | 9 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_set_disagreement"] | 20 |
| ["detector_segmentation_uncertain","mark_set_disagreement"] | 3 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","mark_set_disagreement"] | 2 |
| ["detector_clipped_top","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:keraia"] | 2 |
| ["edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:keraia"] | 2 |
| ["edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:other"] | 2 |
| ["edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:other"] | 2 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_unnamed_mark","mark_set_disagreement"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:keraia"] | 1 |
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
| detector_clipped_bottom | 44633 | 0 | 16119 | 68 |
| detector_clipped_top | 98404 | 0 | 20688 | 209 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 45 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 8 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 0 |
| edit_guard:punctuation_mismatch | 1472 | 2778 | 2778 | 0 |
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
| mark_set_disagreement | 116911 | 0 | 22520 | 146 |
| r1_evidence_UNKNOWN | 905 | 0 | 905 | 0 |
| r1_missing | 1452 | 0 | 955 | 0 |
| r1_uncertainty:out_of_image_span | 905 | 0 | 905 | 0 |
| r1_unscored:line_confidence_below_0.5 | 36 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 881 | 0 | 528 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 535 | 0 | 441 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 146 | 0 | 144 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 110 | 0 | 104 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 13124 | 0 | 5381 | 6 |
| sf6:deletion_needs_two_positive_absences:other | 45081 | 0 | 4338 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 236 | 0 | 230 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4762 |
| A/B disagreement | 0 |
| kind disagreement | 22520 |
| R1 uncertainty | 1829 |
| other/unclassified | 8007 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 3575 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 2430 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 1845 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1258 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 1075 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1024 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 864 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 686 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 675 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 551 |

### round1 / anemi_round1

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 0 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 0 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 8 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 2 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 1 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 493 |
| detector_clipped_top | 140308 | 0 | 29544 | 1902 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 109 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 32 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 0 |
| edit_guard:punctuation_mismatch | 9153 | 6330 | 6330 | 50 |
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
| mark_set_disagreement | 78967 | 0 | 31761 | 2801 |
| r1_evidence_UNKNOWN | 162 | 0 | 162 | 0 |
| r1_missing | 1687 | 0 | 1129 | 0 |
| r1_uncertainty:out_of_image_span | 162 | 0 | 162 | 0 |
| r1_unscored:line_confidence_below_0.5 | 28 | 0 | 2 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 374 | 0 | 189 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 1285 | 0 | 973 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 801 | 0 | 737 | 10 |
| sf6:deletion_needs_two_positive_absences:keraia | 555 | 0 | 511 | 1 |
| sf6:deletion_needs_two_positive_absences:mark | 24346 | 0 | 7310 | 116 |
| sf6:deletion_needs_two_positive_absences:other | 97421 | 0 | 7498 | 1 |
| sf6:deletion_needs_two_positive_absences:quote | 934 | 0 | 915 | 36 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9185 |
| A/B disagreement | 0 |
| kind disagreement | 31761 |
| R1 uncertainty | 1276 |
| other/unclassified | 12135 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 4131 |
| ["mark_set_disagreement"] | 2801 |
| ["detector_clipped_bottom","detector_clipped_top"] | 2676 |
| ["detector_clipped_top","mark_set_disagreement"] | 2345 |
| ["detector_clipped_top"] | 1902 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1656 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 1239 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1079 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1017 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 888 |

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
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 0 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 180 |
| detector_clipped_top | 48664 | 0 | 10763 | 802 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 42 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 19 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 0 |
| edit_guard:punctuation_mismatch | 1491 | 2083 | 2083 | 11 |
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
| mark_set_disagreement | 29904 | 0 | 12180 | 1525 |
| r1_evidence_UNKNOWN | 89 | 0 | 89 | 0 |
| r1_missing | 434 | 0 | 268 | 0 |
| r1_uncertainty:out_of_image_span | 89 | 0 | 89 | 0 |
| r1_unscored:line_confidence_below_0.5 | 11 | 0 | 1 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 126 | 0 | 56 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 297 | 0 | 220 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 279 | 0 | 258 | 7 |
| sf6:deletion_needs_two_positive_absences:keraia | 425 | 0 | 402 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 6370 | 0 | 2418 | 59 |
| sf6:deletion_needs_two_positive_absences:other | 23112 | 0 | 2395 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 250 | 0 | 233 | 3 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3047 |
| A/B disagreement | 0 |
| kind disagreement | 12180 |
| R1 uncertainty | 354 |
| other/unclassified | 4205 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 1700 |
| ["mark_set_disagreement"] | 1525 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1044 |
| ["detector_clipped_top","mark_set_disagreement"] | 1008 |
| ["detector_clipped_top"] | 802 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 498 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 422 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 372 |
| ["detector_segmentation_uncertain","mark_set_disagreement"] | 328 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 300 |

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
| detector_clipped_bottom | 40732 | 0 | 15658 | 229 |
| detector_clipped_top | 93007 | 0 | 19927 | 801 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 33 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 22 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 0 |
| edit_guard:punctuation_mismatch | 3437 | 2255 | 2255 | 1 |
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
| mark_set_disagreement | 61677 | 0 | 18159 | 280 |
| r1_evidence_UNKNOWN | 359 | 0 | 359 | 0 |
| r1_missing | 757 | 0 | 390 | 0 |
| r1_uncertainty:out_of_image_span | 359 | 0 | 359 | 0 |
| r1_unscored:line_confidence_below_0.5 | 54 | 0 | 3 | 0 |
| r1_unscored:width_outside_0.1_2.0_pixel_height | 203 | 0 | 112 | 0 |
| r1_unscored:width_outside_0.2_2.0_median_ctc | 500 | 0 | 294 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 292 | 0 | 278 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 558 | 0 | 508 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 10648 | 0 | 3406 | 12 |
| sf6:deletion_needs_two_positive_absences:other | 41281 | 0 | 2899 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 248 | 0 | 245 | 5 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3531 |
| A/B disagreement | 0 |
| kind disagreement | 18159 |
| R1 uncertainty | 744 |
| other/unclassified | 5478 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","mark_set_disagreement"] | 2355 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","mark_set_disagreement"] | 2340 |
| ["detector_clipped_bottom","detector_clipped_top"] | 1295 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 1233 |
| ["detector_clipped_top","mark_set_disagreement"] | 996 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 814 |
| ["detector_clipped_top"] | 801 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","mark_set_disagreement"] | 777 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","mark_set_disagreement"] | 697 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark","mark_set_disagreement"] | 599 |
## ENSEMBLE_AB

| Wave | Source | Lines | HOLD | Held glyph slots |
|---|---|---:|---:|---:|
| ALL | ALL | 124669 | 113626 | 1179631 |
| mixed | ALL | 13227 | 11588 | 103030 |
| openarchives | ALL | 235 | 196 | 1128 |
| parliament | ALL | 27224 | 26949 | 344172 |
| round1 | ALL | 43869 | 38341 | 387572 |
| round2 | ALL | 17026 | 14119 | 119295 |
| vouli | ALL | 23088 | 22433 | 224434 |
| ALL | anemi_mixed | 13084 | 11474 | 101404 |
| ALL | anemi_round1 | 43869 | 38341 | 387572 |
| ALL | anemi_round2 | 17026 | 14119 | 119295 |
| ALL | archive_b28038630 | 97 | 76 | 671 |
| ALL | openarchives_Pandemos | 185 | 167 | 1056 |
| ALL | openarchives_kallipos | 50 | 29 | 72 |
| ALL | openarchives_mixed_Pandemos | 13 | 10 | 98 |
| ALL | openarchives_mixed_apothesis | 1 | 0 | 0 |
| ALL | openarchives_mixed_ktisis | 2 | 1 | 2 |
| ALL | openarchives_mixed_ntua | 30 | 27 | 855 |
| ALL | parliament_proceedings_1975_2000 | 27224 | 26949 | 344172 |
| ALL | vouli_parliament_1850s | 23088 | 22433 | 224434 |
| mixed | anemi_mixed | 13084 | 11474 | 101404 |
| mixed | archive_b28038630 | 97 | 76 | 671 |
| mixed | openarchives_mixed_Pandemos | 13 | 10 | 98 |
| mixed | openarchives_mixed_apothesis | 1 | 0 | 0 |
| mixed | openarchives_mixed_ktisis | 2 | 1 | 2 |
| mixed | openarchives_mixed_ntua | 30 | 27 | 855 |
| openarchives | openarchives_Pandemos | 185 | 167 | 1056 |
| openarchives | openarchives_kallipos | 50 | 29 | 72 |
| parliament | parliament_proceedings_1975_2000 | 27224 | 26949 | 344172 |
| round1 | anemi_round1 | 43869 | 38341 | 387572 |
| round2 | anemi_round2 | 17026 | 14119 | 119295 |
| vouli | vouli_parliament_1850s | 23088 | 22433 | 224434 |

### ALL / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 543 | 0 | 525 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 770 | 0 | 741 | 4 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 6 | 0 | 6 | 1 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 6 | 0 | 6 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 18 | 0 | 18 | 0 |
| K1:C3:two_accents:evidence_tie | 58 | 0 | 29 | 1 |
| K1:C3:two_accents:rule_held_back | 8094 | 0 | 3535 | 43 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 956 | 0 | 917 | 2 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 48 | 0 | 46 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1782 | 0 | 1627 | 2 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 3 | 0 | 3 | 0 |
| detector_clipped_bottom | 176335 | 0 | 68784 | 2573 |
| detector_clipped_top | 420955 | 0 | 89886 | 9533 |
| detector_localisation_unknown | 151696 | 0 | 46253 | 0 |
| detector_segmentation_uncertain | 254880 | 0 | 60333 | 1628 |
| detector_unnamed_mark | 40015 | 0 | 26798 | 1123 |
| edit_guard:base_or_character_mismatch | 4440 | 13689 | 13689 | 1 |
| edit_guard:punctuation_mismatch | 16841 | 14960 | 14960 | 144 |
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
| ensemble_ab_mark_set_disagreement | 13126 | 0 | 10199 | 185 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 1685 | 0 | 1580 | 37 |
| sf6:deletion_needs_two_positive_absences:keraia | 1786 | 0 | 1652 | 11 |
| sf6:deletion_needs_two_positive_absences:mark | 59882 | 0 | 20456 | 592 |
| sf6:deletion_needs_two_positive_absences:other | 226929 | 0 | 18993 | 1 |
| sf6:deletion_needs_two_positive_absences:quote | 2000 | 0 | 1953 | 128 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 71761 |
| clipping | 99259 |
| K1 | 5313 |
| edit-guard | 22768 |
| A/B disagreement | 10199 |
| kind disagreement | 0 |
| R1 uncertainty | 4502 |
| other/unclassified | 33058 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 15718 |
| ["detector_clipped_top"] | 9533 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 9014 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 5953 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 4215 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 4053 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 3641 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 3424 |
| ["detector_clipped_bottom"] | 2573 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 2036 |

### mixed / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 48 | 0 | 47 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 103 | 0 | 100 | 1 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 2 | 0 | 2 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C3:two_accents:evidence_tie | 4 | 0 | 2 | 0 |
| K1:C3:two_accents:rule_held_back | 874 | 0 | 382 | 6 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 124 | 0 | 122 | 1 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 219 | 0 | 206 | 1 |
| detector_clipped_bottom | 15216 | 0 | 6417 | 316 |
| detector_clipped_top | 39943 | 0 | 8844 | 1337 |
| detector_localisation_unknown | 8743 | 0 | 3355 | 0 |
| detector_segmentation_uncertain | 17178 | 0 | 5101 | 275 |
| detector_unnamed_mark | 2410 | 0 | 1955 | 125 |
| edit_guard:base_or_character_mismatch | 389 | 1293 | 1293 | 0 |
| edit_guard:punctuation_mismatch | 1288 | 1495 | 1495 | 21 |
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
| ensemble_ab_mark_set_disagreement | 1631 | 0 | 1252 | 24 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 166 | 0 | 162 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 125 | 0 | 117 | 1 |
| sf6:deletion_needs_two_positive_absences:mark | 5388 | 0 | 1937 | 97 |
| sf6:deletion_needs_two_positive_absences:other | 19982 | 0 | 1854 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 332 | 0 | 330 | 23 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6062 |
| clipping | 9669 |
| K1 | 616 |
| edit-guard | 2224 |
| A/B disagreement | 1252 |
| kind disagreement | 0 |
| R1 uncertainty | 299 |
| other/unclassified | 3212 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2097 |
| ["detector_clipped_top"] | 1337 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 547 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 488 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 463 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 400 |
| ["detector_clipped_bottom"] | 316 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 286 |
| ["detector_segmentation_uncertain"] | 275 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 274 |

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
| edit_guard:punctuation_mismatch | 0 | 19 | 19 | 1 |
| ensemble_ab_mark_set_disagreement | 19 | 0 | 16 | 12 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 13 | 0 | 10 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 9 | 0 | 7 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 52 | 0 | 9 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 50 |
| clipping | 159 |
| K1 | 5 |
| edit-guard | 19 |
| A/B disagreement | 16 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 23 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 58 |
| ["detector_clipped_bottom"] | 27 |
| ["detector_clipped_top"] | 25 |
| ["ensemble_ab_mark_set_disagreement"] | 12 |
| ["detector_clipped_bottom","detector_segmentation_uncertain"] | 9 |
| ["detector_segmentation_uncertain"] | 9 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 7 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 7 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 5 |
| ["edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:other"] | 4 |

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
| detector_clipped_bottom | 44633 | 0 | 16119 | 162 |
| detector_clipped_top | 98404 | 0 | 20688 | 496 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 80 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 69 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 0 |
| edit_guard:punctuation_mismatch | 1472 | 2778 | 2778 | 0 |
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
| ensemble_ab_mark_set_disagreement | 2014 | 0 | 1653 | 1 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 146 | 0 | 144 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 110 | 0 | 104 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 13124 | 0 | 5381 | 21 |
| sf6:deletion_needs_two_positive_absences:other | 45081 | 0 | 4338 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 236 | 0 | 230 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4762 |
| A/B disagreement | 1653 |
| kind disagreement | 0 |
| R1 uncertainty | 1829 |
| other/unclassified | 8007 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 4491 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 3048 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 1845 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 1581 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 1084 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain"] | 1045 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","sf6:deletion_needs_two_positive_absences:mark"] | 764 |
| ["detector_clipped_bottom","detector_clipped_top"] | 725 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 560 |
| ["detector_clipped_top"] | 496 |

### round1 / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 1 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 1 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 1 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 25 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 1 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 1 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 1089 |
| detector_clipped_top | 140308 | 0 | 29544 | 4141 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 802 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 488 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 0 |
| edit_guard:punctuation_mismatch | 9153 | 6330 | 6330 | 91 |
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
| ensemble_ab_mark_set_disagreement | 5515 | 0 | 4277 | 86 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 801 | 0 | 737 | 23 |
| sf6:deletion_needs_two_positive_absences:keraia | 555 | 0 | 511 | 5 |
| sf6:deletion_needs_two_positive_absences:mark | 24344 | 0 | 7308 | 293 |
| sf6:deletion_needs_two_positive_absences:other | 97421 | 0 | 7498 | 1 |
| sf6:deletion_needs_two_positive_absences:quote | 934 | 0 | 915 | 81 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9185 |
| A/B disagreement | 4277 |
| kind disagreement | 0 |
| R1 uncertainty | 1276 |
| other/unclassified | 12134 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 6593 |
| ["detector_clipped_top"] | 4141 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1957 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 1376 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 1327 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1271 |
| ["detector_clipped_bottom"] | 1089 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 886 |
| ["detector_segmentation_uncertain"] | 802 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 755 |

### round2 / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 84 | 0 | 81 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 107 | 0 | 103 | 2 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 6 | 0 | 3 | 0 |
| K1:C3:two_accents:rule_held_back | 1020 | 0 | 467 | 8 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 101 | 0 | 98 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 0 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 469 |
| detector_clipped_top | 48664 | 0 | 10763 | 1773 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 362 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 302 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 1 |
| edit_guard:punctuation_mismatch | 1491 | 2083 | 2083 | 26 |
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
| ensemble_ab_mark_set_disagreement | 1770 | 0 | 1426 | 48 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 279 | 0 | 258 | 14 |
| sf6:deletion_needs_two_positive_absences:keraia | 425 | 0 | 402 | 5 |
| sf6:deletion_needs_two_positive_absences:mark | 6369 | 0 | 2417 | 148 |
| sf6:deletion_needs_two_positive_absences:other | 23112 | 0 | 2395 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 250 | 0 | 233 | 11 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3047 |
| A/B disagreement | 1426 |
| kind disagreement | 0 |
| R1 uncertainty | 354 |
| other/unclassified | 4204 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2656 |
| ["detector_clipped_top"] | 1773 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 530 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 482 |
| ["detector_clipped_bottom"] | 469 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 382 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 378 |
| ["detector_segmentation_uncertain"] | 362 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 337 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 303 |

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
| detector_clipped_bottom | 40732 | 0 | 15658 | 510 |
| detector_clipped_top | 93007 | 0 | 19927 | 1761 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 100 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 138 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 0 |
| edit_guard:punctuation_mismatch | 3437 | 2255 | 2255 | 5 |
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
| ensemble_ab_mark_set_disagreement | 2177 | 0 | 1575 | 14 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 292 | 0 | 278 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 558 | 0 | 508 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 10648 | 0 | 3406 | 31 |
| sf6:deletion_needs_two_positive_absences:other | 41281 | 0 | 2899 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 248 | 0 | 245 | 12 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3531 |
| A/B disagreement | 1575 |
| kind disagreement | 0 |
| R1 uncertainty | 744 |
| other/unclassified | 5478 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 3589 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 2389 |
| ["detector_clipped_top"] | 1761 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1537 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 931 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 889 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 804 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark"] | 590 |
| ["detector_clipped_top","detector_unnamed_mark"] | 580 |
| ["detector_clipped_bottom"] | 510 |

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
| K1:C4:grave_not_final:impossible_by_rule | 214 | 0 | 201 | 1 |
| detector_clipped_bottom | 15059 | 0 | 6360 | 312 |
| detector_clipped_top | 39633 | 0 | 8777 | 1328 |
| detector_localisation_unknown | 8716 | 0 | 3345 | 0 |
| detector_segmentation_uncertain | 17133 | 0 | 5085 | 275 |
| detector_unnamed_mark | 2392 | 0 | 1939 | 123 |
| edit_guard:base_or_character_mismatch | 389 | 1258 | 1258 | 0 |
| edit_guard:punctuation_mismatch | 1184 | 1453 | 1453 | 19 |
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
| ensemble_ab_mark_set_disagreement | 1607 | 0 | 1231 | 24 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 154 | 0 | 150 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 125 | 0 | 117 | 1 |
| sf6:deletion_needs_two_positive_absences:mark | 5230 | 0 | 1897 | 93 |
| sf6:deletion_needs_two_positive_absences:other | 19239 | 0 | 1812 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 331 | 0 | 329 | 23 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6032 |
| clipping | 9594 |
| K1 | 609 |
| edit-guard | 2175 |
| A/B disagreement | 1231 |
| kind disagreement | 0 |
| R1 uncertainty | 294 |
| other/unclassified | 3154 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2078 |
| ["detector_clipped_top"] | 1328 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 547 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 487 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 457 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 400 |
| ["detector_clipped_bottom"] | 312 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 285 |
| ["detector_segmentation_uncertain"] | 275 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 274 |

### ALL / anemi_round1

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 1 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 1 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 1 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 25 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 1 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 1 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 1089 |
| detector_clipped_top | 140308 | 0 | 29544 | 4141 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 802 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 488 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 0 |
| edit_guard:punctuation_mismatch | 9153 | 6330 | 6330 | 91 |
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
| ensemble_ab_mark_set_disagreement | 5515 | 0 | 4277 | 86 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 801 | 0 | 737 | 23 |
| sf6:deletion_needs_two_positive_absences:keraia | 555 | 0 | 511 | 5 |
| sf6:deletion_needs_two_positive_absences:mark | 24344 | 0 | 7308 | 293 |
| sf6:deletion_needs_two_positive_absences:other | 97421 | 0 | 7498 | 1 |
| sf6:deletion_needs_two_positive_absences:quote | 934 | 0 | 915 | 81 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9185 |
| A/B disagreement | 4277 |
| kind disagreement | 0 |
| R1 uncertainty | 1276 |
| other/unclassified | 12134 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 6593 |
| ["detector_clipped_top"] | 4141 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1957 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 1376 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 1327 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1271 |
| ["detector_clipped_bottom"] | 1089 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 886 |
| ["detector_segmentation_uncertain"] | 802 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 755 |

### ALL / anemi_round2

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 84 | 0 | 81 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 107 | 0 | 103 | 2 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 6 | 0 | 3 | 0 |
| K1:C3:two_accents:rule_held_back | 1020 | 0 | 467 | 8 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 101 | 0 | 98 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 0 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 469 |
| detector_clipped_top | 48664 | 0 | 10763 | 1773 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 362 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 302 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 1 |
| edit_guard:punctuation_mismatch | 1491 | 2083 | 2083 | 26 |
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
| ensemble_ab_mark_set_disagreement | 1770 | 0 | 1426 | 48 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 279 | 0 | 258 | 14 |
| sf6:deletion_needs_two_positive_absences:keraia | 425 | 0 | 402 | 5 |
| sf6:deletion_needs_two_positive_absences:mark | 6369 | 0 | 2417 | 148 |
| sf6:deletion_needs_two_positive_absences:other | 23112 | 0 | 2395 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 250 | 0 | 233 | 11 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3047 |
| A/B disagreement | 1426 |
| kind disagreement | 0 |
| R1 uncertainty | 354 |
| other/unclassified | 4204 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2656 |
| ["detector_clipped_top"] | 1773 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 530 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 482 |
| ["detector_clipped_bottom"] | 469 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 382 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 378 |
| ["detector_segmentation_uncertain"] | 362 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 337 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 303 |

### ALL / archive_b28038630

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 2 | 0 | 1 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 130 | 0 | 45 | 2 |
| detector_clipped_top | 254 | 0 | 58 | 9 |
| detector_localisation_unknown | 7 | 0 | 6 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 1 |
| edit_guard:base_or_character_mismatch | 0 | 13 | 13 | 0 |
| edit_guard:punctuation_mismatch | 0 | 22 | 22 | 1 |
| ensemble_ab_mark_set_disagreement | 12 | 0 | 12 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 5 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 17 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 252 | 0 | 20 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 13 |
| clipping | 61 |
| K1 | 3 |
| edit-guard | 24 |
| A/B disagreement | 12 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 32 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 16 |
| ["detector_clipped_top"] | 9 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 6 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","ensemble_ab_mark_set_disagreement"] | 4 |
| ["edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 3 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:punctuation_mismatch"] | 2 |
| ["detector_clipped_bottom"] | 2 |
| ["detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:other"] | 2 |

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
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 7 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 9 | 0 | 7 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 48 | 0 | 5 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 46 |
| clipping | 157 |
| K1 | 0 |
| edit-guard | 9 |
| A/B disagreement | 2 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 14 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 58 |
| ["detector_clipped_bottom"] | 27 |
| ["detector_clipped_top"] | 25 |
| ["detector_clipped_bottom","detector_segmentation_uncertain"] | 9 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 7 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 7 |
| ["detector_segmentation_uncertain"] | 6 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 5 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 3 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark"] | 2 |

### ALL / openarchives_kallipos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 12 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_top | 25 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 10 | 0 | 3 | 3 |
| detector_unnamed_mark | 1 | 0 | 1 | 0 |
| edit_guard:punctuation_mismatch | 0 | 10 | 10 | 1 |
| ensemble_ab_mark_set_disagreement | 17 | 0 | 14 | 12 |
| sf6:deletion_needs_two_positive_absences:keraia | 6 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 4 | 0 | 4 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 2 |
| K1 | 5 |
| edit-guard | 10 |
| A/B disagreement | 14 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 9 |

| Top exact reason set | Lines |
|---|---:|
| ["ensemble_ab_mark_set_disagreement"] | 12 |
| ["edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["detector_segmentation_uncertain"] | 3 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule"] | 2 |
| ["detector_clipped_top","edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:keraia"] | 2 |
| ["edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:keraia"] | 2 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_unnamed_mark"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:keraia"] | 1 |
| ["K1:C3:two_accents:rule_held_back","ensemble_ab_mark_set_disagreement"] | 1 |
| ["edit_guard:punctuation_mismatch"] | 1 |

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
| sf6:deletion_needs_two_positive_absences:mark | 4 | 0 | 2 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 39 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 7 |
| K1 | 0 |
| edit-guard | 2 |
| A/B disagreement | 1 |
| kind disagreement | 0 |
| R1 uncertainty | 1 |
| other/unclassified | 2 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 3 |
| ["detector_clipped_bottom"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","detector_unnamed_mark"] | 1 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
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
| detector_unnamed_mark | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 1 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 1 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_unnamed_mark","sf6:deletion_needs_two_positive_absences:mark"] | 1 |

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
| edit_guard:base_or_character_mismatch | 0 | 21 | 21 | 0 |
| edit_guard:punctuation_mismatch | 104 | 19 | 19 | 1 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 7 | 0 | 7 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 106 | 0 | 20 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 452 | 0 | 21 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 12 |
| clipping | 7 |
| K1 | 4 |
| edit-guard | 23 |
| A/B disagreement | 8 |
| kind disagreement | 0 |
| R1 uncertainty | 4 |
| other/unclassified | 23 |

| Top exact reason set | Lines |
|---|---:|
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 3 |
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:apostrophe","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 2 |
| ["sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["K1:C1:breathing_not_initial:impossible_by_rule","K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","edit_guard:unsupported_character:28","edit_guard:unsupported_raw_character:28","ensemble_ab_mark_set_disagreement","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_B_unscored:width_outside_0.2_2.0_median_ctc","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","r1_unscored:width_outside_0.2_2.0_median_ctc","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:apostrophe","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["detector_clipped_bottom","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","sf6:deletion_needs_two_positive_absences:apostrophe","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |

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
| detector_clipped_bottom | 44633 | 0 | 16119 | 162 |
| detector_clipped_top | 98404 | 0 | 20688 | 496 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 80 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 69 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 0 |
| edit_guard:punctuation_mismatch | 1472 | 2778 | 2778 | 0 |
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
| ensemble_ab_mark_set_disagreement | 2014 | 0 | 1653 | 1 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 146 | 0 | 144 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 110 | 0 | 104 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 13124 | 0 | 5381 | 21 |
| sf6:deletion_needs_two_positive_absences:other | 45081 | 0 | 4338 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 236 | 0 | 230 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4762 |
| A/B disagreement | 1653 |
| kind disagreement | 0 |
| R1 uncertainty | 1829 |
| other/unclassified | 8007 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 4491 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 3048 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 1845 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 1581 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 1084 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain"] | 1045 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","sf6:deletion_needs_two_positive_absences:mark"] | 764 |
| ["detector_clipped_bottom","detector_clipped_top"] | 725 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 560 |
| ["detector_clipped_top"] | 496 |

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
| detector_clipped_bottom | 40732 | 0 | 15658 | 510 |
| detector_clipped_top | 93007 | 0 | 19927 | 1761 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 100 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 138 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 0 |
| edit_guard:punctuation_mismatch | 3437 | 2255 | 2255 | 5 |
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
| ensemble_ab_mark_set_disagreement | 2177 | 0 | 1575 | 14 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 292 | 0 | 278 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 558 | 0 | 508 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 10648 | 0 | 3406 | 31 |
| sf6:deletion_needs_two_positive_absences:other | 41281 | 0 | 2899 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 248 | 0 | 245 | 12 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3531 |
| A/B disagreement | 1575 |
| kind disagreement | 0 |
| R1 uncertainty | 744 |
| other/unclassified | 5478 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 3589 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 2389 |
| ["detector_clipped_top"] | 1761 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1537 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 931 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 889 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 804 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark"] | 590 |
| ["detector_clipped_top","detector_unnamed_mark"] | 580 |
| ["detector_clipped_bottom"] | 510 |

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
| K1:C4:grave_not_final:impossible_by_rule | 214 | 0 | 201 | 1 |
| detector_clipped_bottom | 15059 | 0 | 6360 | 312 |
| detector_clipped_top | 39633 | 0 | 8777 | 1328 |
| detector_localisation_unknown | 8716 | 0 | 3345 | 0 |
| detector_segmentation_uncertain | 17133 | 0 | 5085 | 275 |
| detector_unnamed_mark | 2392 | 0 | 1939 | 123 |
| edit_guard:base_or_character_mismatch | 389 | 1258 | 1258 | 0 |
| edit_guard:punctuation_mismatch | 1184 | 1453 | 1453 | 19 |
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
| ensemble_ab_mark_set_disagreement | 1607 | 0 | 1231 | 24 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 154 | 0 | 150 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 125 | 0 | 117 | 1 |
| sf6:deletion_needs_two_positive_absences:mark | 5230 | 0 | 1897 | 93 |
| sf6:deletion_needs_two_positive_absences:other | 19239 | 0 | 1812 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 331 | 0 | 329 | 23 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6032 |
| clipping | 9594 |
| K1 | 609 |
| edit-guard | 2175 |
| A/B disagreement | 1231 |
| kind disagreement | 0 |
| R1 uncertainty | 294 |
| other/unclassified | 3154 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2078 |
| ["detector_clipped_top"] | 1328 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 547 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 487 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 457 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 400 |
| ["detector_clipped_bottom"] | 312 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 285 |
| ["detector_segmentation_uncertain"] | 275 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 274 |

### mixed / archive_b28038630

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 2 | 0 | 1 | 0 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 130 | 0 | 45 | 2 |
| detector_clipped_top | 254 | 0 | 58 | 9 |
| detector_localisation_unknown | 7 | 0 | 6 | 0 |
| detector_segmentation_uncertain | 9 | 0 | 7 | 0 |
| detector_unnamed_mark | 7 | 0 | 6 | 1 |
| edit_guard:base_or_character_mismatch | 0 | 13 | 13 | 0 |
| edit_guard:punctuation_mismatch | 0 | 22 | 22 | 1 |
| ensemble_ab_mark_set_disagreement | 12 | 0 | 12 | 0 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 5 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 17 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 252 | 0 | 20 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 13 |
| clipping | 61 |
| K1 | 3 |
| edit-guard | 24 |
| A/B disagreement | 12 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 32 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 16 |
| ["detector_clipped_top"] | 9 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 6 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","ensemble_ab_mark_set_disagreement"] | 4 |
| ["edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 3 |
| ["detector_clipped_bottom","detector_clipped_top","edit_guard:punctuation_mismatch"] | 2 |
| ["detector_clipped_bottom"] | 2 |
| ["detector_clipped_top","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:other"] | 2 |

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
| sf6:deletion_needs_two_positive_absences:mark | 4 | 0 | 2 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 39 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 7 |
| K1 | 0 |
| edit-guard | 2 |
| A/B disagreement | 1 |
| kind disagreement | 0 |
| R1 uncertainty | 1 |
| other/unclassified | 2 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 3 |
| ["detector_clipped_bottom"] | 2 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","detector_unnamed_mark"] | 1 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
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
| detector_unnamed_mark | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 1 | 0 | 1 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 1 |
| clipping | 0 |
| K1 | 0 |
| edit-guard | 0 |
| A/B disagreement | 0 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 1 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_unnamed_mark","sf6:deletion_needs_two_positive_absences:mark"] | 1 |

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
| edit_guard:base_or_character_mismatch | 0 | 21 | 21 | 0 |
| edit_guard:punctuation_mismatch | 104 | 19 | 19 | 1 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 7 | 0 | 7 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 106 | 0 | 20 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 452 | 0 | 21 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 12 |
| clipping | 7 |
| K1 | 4 |
| edit-guard | 23 |
| A/B disagreement | 8 |
| kind disagreement | 0 |
| R1 uncertainty | 4 |
| other/unclassified | 23 |

| Top exact reason set | Lines |
|---|---:|
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 3 |
| ["edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:apostrophe","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 2 |
| ["sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["K1:C1:breathing_not_initial:impossible_by_rule","K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","edit_guard:unsupported_character:28","edit_guard:unsupported_raw_character:28","ensemble_ab_mark_set_disagreement","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_B_unscored:width_outside_0.2_2.0_median_ctc","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","r1_unscored:width_outside_0.2_2.0_median_ctc","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:apostrophe","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","detector_localisation_unknown","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["detector_clipped_bottom","detector_segmentation_uncertain","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |
| ["detector_clipped_bottom","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","r1_B_missing","r1_B_unscored:width_outside_0.1_2.0_pixel_height","r1_missing","r1_unscored:width_outside_0.1_2.0_pixel_height","sf6:deletion_needs_two_positive_absences:apostrophe","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other"] | 1 |

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
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 7 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 9 | 0 | 7 | 2 |
| sf6:deletion_needs_two_positive_absences:other | 48 | 0 | 5 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 46 |
| clipping | 157 |
| K1 | 0 |
| edit-guard | 9 |
| A/B disagreement | 2 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 14 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 58 |
| ["detector_clipped_bottom"] | 27 |
| ["detector_clipped_top"] | 25 |
| ["detector_clipped_bottom","detector_segmentation_uncertain"] | 9 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 7 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 7 |
| ["detector_segmentation_uncertain"] | 6 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 5 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 3 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark"] | 2 |

### openarchives / openarchives_kallipos

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:rule_held_back | 12 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 4 | 0 | 4 | 0 |
| detector_clipped_top | 25 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 10 | 0 | 3 | 3 |
| detector_unnamed_mark | 1 | 0 | 1 | 0 |
| edit_guard:punctuation_mismatch | 0 | 10 | 10 | 1 |
| ensemble_ab_mark_set_disagreement | 17 | 0 | 14 | 12 |
| sf6:deletion_needs_two_positive_absences:keraia | 6 | 0 | 5 | 0 |
| sf6:deletion_needs_two_positive_absences:other | 4 | 0 | 4 | 0 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 4 |
| clipping | 2 |
| K1 | 5 |
| edit-guard | 10 |
| A/B disagreement | 14 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 9 |

| Top exact reason set | Lines |
|---|---:|
| ["ensemble_ab_mark_set_disagreement"] | 12 |
| ["edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:other"] | 4 |
| ["detector_segmentation_uncertain"] | 3 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule"] | 2 |
| ["detector_clipped_top","edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:keraia"] | 2 |
| ["edit_guard:punctuation_mismatch","sf6:deletion_needs_two_positive_absences:keraia"] | 2 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","detector_unnamed_mark"] | 1 |
| ["K1:C3:two_accents:rule_held_back","K1:C4:grave_not_final:impossible_by_rule","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:keraia"] | 1 |
| ["K1:C3:two_accents:rule_held_back","ensemble_ab_mark_set_disagreement"] | 1 |
| ["edit_guard:punctuation_mismatch"] | 1 |

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
| detector_clipped_bottom | 44633 | 0 | 16119 | 162 |
| detector_clipped_top | 98404 | 0 | 20688 | 496 |
| detector_localisation_unknown | 96860 | 0 | 22524 | 0 |
| detector_segmentation_uncertain | 143334 | 0 | 24024 | 80 |
| detector_unnamed_mark | 11624 | 0 | 7742 | 69 |
| edit_guard:base_or_character_mismatch | 723 | 2940 | 2940 | 0 |
| edit_guard:punctuation_mismatch | 1472 | 2778 | 2778 | 0 |
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
| ensemble_ab_mark_set_disagreement | 2014 | 0 | 1653 | 1 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 146 | 0 | 144 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 110 | 0 | 104 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 13124 | 0 | 5381 | 21 |
| sf6:deletion_needs_two_positive_absences:other | 45081 | 0 | 4338 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 236 | 0 | 230 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 24849 |
| clipping | 23558 |
| K1 | 910 |
| edit-guard | 4762 |
| A/B disagreement | 1653 |
| kind disagreement | 0 |
| R1 uncertainty | 1829 |
| other/unclassified | 8007 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 4491 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 3048 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 1845 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 1581 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 1084 |
| ["detector_clipped_bottom","detector_localisation_unknown","detector_segmentation_uncertain"] | 1045 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","sf6:deletion_needs_two_positive_absences:mark"] | 764 |
| ["detector_clipped_bottom","detector_clipped_top"] | 725 |
| ["detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 560 |
| ["detector_clipped_top"] | 496 |

### round1 / anemi_round1

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 256 | 0 | 247 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 340 | 0 | 330 | 1 |
| K1:C1:smooth_breathing_on_rho:impossible_by_rule | 5 | 0 | 5 | 1 |
| K1:C2:breathing_with_dialytika:impossible_by_rule | 4 | 0 | 4 | 0 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 16 | 0 | 8 | 1 |
| K1:C3:two_accents:rule_held_back | 3248 | 0 | 1427 | 25 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 372 | 0 | 361 | 1 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 20 | 0 | 20 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 724 | 0 | 662 | 1 |
| K1:C5:dialytika_not_on_iota_upsilon:impossible_by_rule | 1 | 0 | 1 | 0 |
| detector_clipped_bottom | 55996 | 0 | 22428 | 1089 |
| detector_clipped_top | 140308 | 0 | 29544 | 4141 |
| detector_localisation_unknown | 24619 | 0 | 10779 | 0 |
| detector_segmentation_uncertain | 48881 | 0 | 16074 | 802 |
| detector_unnamed_mark | 7676 | 0 | 6372 | 488 |
| edit_guard:base_or_character_mismatch | 1965 | 5589 | 5589 | 0 |
| edit_guard:punctuation_mismatch | 9153 | 6330 | 6330 | 91 |
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
| ensemble_ab_mark_set_disagreement | 5515 | 0 | 4277 | 86 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 801 | 0 | 737 | 23 |
| sf6:deletion_needs_two_positive_absences:keraia | 555 | 0 | 511 | 5 |
| sf6:deletion_needs_two_positive_absences:mark | 24344 | 0 | 7308 | 293 |
| sf6:deletion_needs_two_positive_absences:other | 97421 | 0 | 7498 | 1 |
| sf6:deletion_needs_two_positive_absences:quote | 934 | 0 | 915 | 81 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 19574 |
| clipping | 32549 |
| K1 | 2169 |
| edit-guard | 9185 |
| A/B disagreement | 4277 |
| kind disagreement | 0 |
| R1 uncertainty | 1276 |
| other/unclassified | 12134 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 6593 |
| ["detector_clipped_top"] | 4141 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1957 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 1376 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 1327 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1271 |
| ["detector_clipped_bottom"] | 1089 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 886 |
| ["detector_segmentation_uncertain"] | 802 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 755 |

### round2 / anemi_round2

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C1:breathing_after_consonant_start:rule_held_back | 84 | 0 | 81 | 0 |
| K1:C1:breathing_not_initial:impossible_by_rule | 107 | 0 | 103 | 2 |
| K1:C2:mark_on_consonant:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C3:two_accents:evidence_tie | 6 | 0 | 3 | 0 |
| K1:C3:two_accents:rule_held_back | 1020 | 0 | 467 | 8 |
| K1:C4:circumflex_before_penult:impossible_by_rule | 101 | 0 | 98 | 0 |
| K1:C4:circumflex_on_short_vowel:impossible_by_rule | 5 | 0 | 5 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 262 | 0 | 244 | 0 |
| detector_clipped_bottom | 19392 | 0 | 8044 | 469 |
| detector_clipped_top | 48664 | 0 | 10763 | 1773 |
| detector_localisation_unknown | 7207 | 0 | 2914 | 0 |
| detector_segmentation_uncertain | 15794 | 0 | 5153 | 362 |
| detector_unnamed_mark | 3197 | 0 | 2587 | 302 |
| edit_guard:base_or_character_mismatch | 447 | 1669 | 1669 | 1 |
| edit_guard:punctuation_mismatch | 1491 | 2083 | 2083 | 26 |
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
| ensemble_ab_mark_set_disagreement | 1770 | 0 | 1426 | 48 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 279 | 0 | 258 | 14 |
| sf6:deletion_needs_two_positive_absences:keraia | 425 | 0 | 402 | 5 |
| sf6:deletion_needs_two_positive_absences:mark | 6369 | 0 | 2417 | 148 |
| sf6:deletion_needs_two_positive_absences:other | 23112 | 0 | 2395 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 250 | 0 | 233 | 11 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 6662 |
| clipping | 11854 |
| K1 | 751 |
| edit-guard | 3047 |
| A/B disagreement | 1426 |
| kind disagreement | 0 |
| R1 uncertainty | 354 |
| other/unclassified | 4204 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 2656 |
| ["detector_clipped_top"] | 1773 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 530 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 482 |
| ["detector_clipped_bottom"] | 469 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 382 |
| ["detector_localisation_unknown","detector_segmentation_uncertain"] | 378 |
| ["detector_segmentation_uncertain"] | 362 |
| ["detector_clipped_top","detector_segmentation_uncertain"] | 337 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 303 |

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
| detector_clipped_bottom | 40732 | 0 | 15658 | 510 |
| detector_clipped_top | 93007 | 0 | 19927 | 1761 |
| detector_localisation_unknown | 14267 | 0 | 6681 | 0 |
| detector_segmentation_uncertain | 29583 | 0 | 9943 | 100 |
| detector_unnamed_mark | 15084 | 0 | 8123 | 138 |
| edit_guard:base_or_character_mismatch | 916 | 2195 | 2195 | 0 |
| edit_guard:punctuation_mismatch | 3437 | 2255 | 2255 | 5 |
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
| ensemble_ab_mark_set_disagreement | 2177 | 0 | 1575 | 14 |
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
| sf6:deletion_needs_two_positive_absences:apostrophe | 292 | 0 | 278 | 0 |
| sf6:deletion_needs_two_positive_absences:keraia | 558 | 0 | 508 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 10648 | 0 | 3406 | 31 |
| sf6:deletion_needs_two_positive_absences:other | 41281 | 0 | 2899 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 248 | 0 | 245 | 12 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 14564 |
| clipping | 21470 |
| K1 | 862 |
| edit-guard | 3531 |
| A/B disagreement | 1575 |
| kind disagreement | 0 |
| R1 uncertainty | 744 |
| other/unclassified | 5478 |

| Top exact reason set | Lines |
|---|---:|
| ["detector_clipped_bottom","detector_clipped_top"] | 3589 |
| ["detector_clipped_bottom","detector_clipped_top","detector_unnamed_mark"] | 2389 |
| ["detector_clipped_top"] | 1761 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 1537 |
| ["detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain"] | 931 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain"] | 889 |
| ["detector_clipped_bottom","detector_clipped_top","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 804 |
| ["detector_clipped_bottom","detector_clipped_top","detector_segmentation_uncertain","detector_unnamed_mark"] | 590 |
| ["detector_clipped_top","detector_unnamed_mark"] | 580 |
| ["detector_clipped_bottom"] | 510 |

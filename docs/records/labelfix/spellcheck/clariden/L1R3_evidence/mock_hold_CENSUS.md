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
| ALL | ALL | 64 | 61 | 277 |
| heldout-verification | ALL | 64 | 61 | 277 |
| mixed | ALL | 0 | 0 | 0 |
| openarchives | ALL | 0 | 0 | 0 |
| parliament | ALL | 0 | 0 | 0 |
| round1 | ALL | 0 | 0 | 0 |
| round2 | ALL | 0 | 0 | 0 |
| vouli | ALL | 0 | 0 | 0 |
| ALL | print-instrument | 64 | 61 | 277 |
| heldout-verification | print-instrument | 64 | 61 | 277 |

### ALL / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:evidence_tie | 2 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:flag | 13 | 0 | 8 | 0 |
| K1:observation:localisation_unknown | 4 | 0 | 2 | 0 |
| K1:observation:unnamed | 9 | 0 | 7 | 0 |
| detector_clipped_bottom | 23 | 0 | 15 | 1 |
| detector_clipped_top | 21 | 0 | 9 | 2 |
| detector_localisation_unknown | 4 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 12 | 0 | 5 | 0 |
| detector_unnamed_mark | 9 | 0 | 7 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 2 | 2 | 0 |
| edit_guard:unsupported_character:1 | 33 | 1 | 1 | 0 |
| edit_guard:unsupported_character:4 | 31 | 1 | 1 | 0 |
| edit_guard:unsupported_raw_character:1 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:4 | 31 | 0 | 1 | 0 |
| mark_kind_disagreement | 68 | 0 | 41 | 8 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 36 | 11 |
| sf6:deletion_needs_two_positive_absences:other | 47 | 0 | 3 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 3 | 0 | 3 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 11 |
| clipping | 20 |
| K1 | 10 |
| edit-guard | 5 |
| A/B disagreement | 0 |
| kind disagreement | 41 |
| R1 uncertainty | 0 |
| other/unclassified | 39 |

| Top exact reason set | Lines |
|---|---:|
| ["sf6:deletion_needs_two_positive_absences:mark"] | 11 |
| ["mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 8 |
| ["mark_kind_disagreement"] | 8 |
| ["detector_clipped_bottom","mark_kind_disagreement"] | 6 |
| ["K1:flag","K1:observation:unnamed","detector_unnamed_mark","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_bottom","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_top"] | 2 |
| ["K1:C3:two_accents:evidence_tie","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other","sf6:deletion_needs_two_positive_absences:quote"] | 1 |

### heldout-verification / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:evidence_tie | 2 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:flag | 13 | 0 | 8 | 0 |
| K1:observation:localisation_unknown | 4 | 0 | 2 | 0 |
| K1:observation:unnamed | 9 | 0 | 7 | 0 |
| detector_clipped_bottom | 23 | 0 | 15 | 1 |
| detector_clipped_top | 21 | 0 | 9 | 2 |
| detector_localisation_unknown | 4 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 12 | 0 | 5 | 0 |
| detector_unnamed_mark | 9 | 0 | 7 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 2 | 2 | 0 |
| edit_guard:unsupported_character:1 | 33 | 1 | 1 | 0 |
| edit_guard:unsupported_character:4 | 31 | 1 | 1 | 0 |
| edit_guard:unsupported_raw_character:1 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:4 | 31 | 0 | 1 | 0 |
| mark_kind_disagreement | 68 | 0 | 41 | 8 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 36 | 11 |
| sf6:deletion_needs_two_positive_absences:other | 47 | 0 | 3 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 3 | 0 | 3 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 11 |
| clipping | 20 |
| K1 | 10 |
| edit-guard | 5 |
| A/B disagreement | 0 |
| kind disagreement | 41 |
| R1 uncertainty | 0 |
| other/unclassified | 39 |

| Top exact reason set | Lines |
|---|---:|
| ["sf6:deletion_needs_two_positive_absences:mark"] | 11 |
| ["mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 8 |
| ["mark_kind_disagreement"] | 8 |
| ["detector_clipped_bottom","mark_kind_disagreement"] | 6 |
| ["K1:flag","K1:observation:unnamed","detector_unnamed_mark","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_bottom","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_top"] | 2 |
| ["K1:C3:two_accents:evidence_tie","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other","sf6:deletion_needs_two_positive_absences:quote"] | 1 |

### ALL / print-instrument

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:evidence_tie | 2 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:flag | 13 | 0 | 8 | 0 |
| K1:observation:localisation_unknown | 4 | 0 | 2 | 0 |
| K1:observation:unnamed | 9 | 0 | 7 | 0 |
| detector_clipped_bottom | 23 | 0 | 15 | 1 |
| detector_clipped_top | 21 | 0 | 9 | 2 |
| detector_localisation_unknown | 4 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 12 | 0 | 5 | 0 |
| detector_unnamed_mark | 9 | 0 | 7 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 2 | 2 | 0 |
| edit_guard:unsupported_character:1 | 33 | 1 | 1 | 0 |
| edit_guard:unsupported_character:4 | 31 | 1 | 1 | 0 |
| edit_guard:unsupported_raw_character:1 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:4 | 31 | 0 | 1 | 0 |
| mark_kind_disagreement | 68 | 0 | 41 | 8 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 36 | 11 |
| sf6:deletion_needs_two_positive_absences:other | 47 | 0 | 3 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 3 | 0 | 3 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 11 |
| clipping | 20 |
| K1 | 10 |
| edit-guard | 5 |
| A/B disagreement | 0 |
| kind disagreement | 41 |
| R1 uncertainty | 0 |
| other/unclassified | 39 |

| Top exact reason set | Lines |
|---|---:|
| ["sf6:deletion_needs_two_positive_absences:mark"] | 11 |
| ["mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 8 |
| ["mark_kind_disagreement"] | 8 |
| ["detector_clipped_bottom","mark_kind_disagreement"] | 6 |
| ["K1:flag","K1:observation:unnamed","detector_unnamed_mark","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_bottom","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_top"] | 2 |
| ["K1:C3:two_accents:evidence_tie","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other","sf6:deletion_needs_two_positive_absences:quote"] | 1 |

### heldout-verification / print-instrument

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:evidence_tie | 2 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:flag | 13 | 0 | 8 | 0 |
| K1:observation:localisation_unknown | 4 | 0 | 2 | 0 |
| K1:observation:unnamed | 9 | 0 | 7 | 0 |
| detector_clipped_bottom | 23 | 0 | 15 | 1 |
| detector_clipped_top | 21 | 0 | 9 | 2 |
| detector_localisation_unknown | 4 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 12 | 0 | 5 | 0 |
| detector_unnamed_mark | 9 | 0 | 7 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 2 | 2 | 0 |
| edit_guard:unsupported_character:1 | 33 | 1 | 1 | 0 |
| edit_guard:unsupported_character:4 | 31 | 1 | 1 | 0 |
| edit_guard:unsupported_raw_character:1 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:4 | 31 | 0 | 1 | 0 |
| mark_kind_disagreement | 68 | 0 | 41 | 8 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 36 | 11 |
| sf6:deletion_needs_two_positive_absences:other | 47 | 0 | 3 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 3 | 0 | 3 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 11 |
| clipping | 20 |
| K1 | 10 |
| edit-guard | 5 |
| A/B disagreement | 0 |
| kind disagreement | 41 |
| R1 uncertainty | 0 |
| other/unclassified | 39 |

| Top exact reason set | Lines |
|---|---:|
| ["sf6:deletion_needs_two_positive_absences:mark"] | 11 |
| ["mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 8 |
| ["mark_kind_disagreement"] | 8 |
| ["detector_clipped_bottom","mark_kind_disagreement"] | 6 |
| ["K1:flag","K1:observation:unnamed","detector_unnamed_mark","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_bottom","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_top"] | 2 |
| ["K1:C3:two_accents:evidence_tie","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_kind_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other","sf6:deletion_needs_two_positive_absences:quote"] | 1 |
## FULL

| Wave | Source | Lines | HOLD | Held glyph slots |
|---|---|---:|---:|---:|
| ALL | ALL | 64 | 62 | 283 |
| heldout-verification | ALL | 64 | 62 | 283 |
| mixed | ALL | 0 | 0 | 0 |
| openarchives | ALL | 0 | 0 | 0 |
| parliament | ALL | 0 | 0 | 0 |
| round1 | ALL | 0 | 0 | 0 |
| round2 | ALL | 0 | 0 | 0 |
| vouli | ALL | 0 | 0 | 0 |
| ALL | print-instrument | 64 | 62 | 283 |
| heldout-verification | print-instrument | 64 | 62 | 283 |

### ALL / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:evidence_tie | 2 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:flag | 13 | 0 | 8 | 0 |
| K1:observation:localisation_unknown | 4 | 0 | 2 | 0 |
| K1:observation:unnamed | 9 | 0 | 7 | 0 |
| detector_clipped_bottom | 23 | 0 | 15 | 1 |
| detector_clipped_top | 21 | 0 | 9 | 1 |
| detector_localisation_unknown | 4 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 12 | 0 | 5 | 0 |
| detector_unnamed_mark | 9 | 0 | 7 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 2 | 2 | 0 |
| edit_guard:unsupported_character:1 | 33 | 1 | 1 | 0 |
| edit_guard:unsupported_character:4 | 31 | 1 | 1 | 0 |
| edit_guard:unsupported_raw_character:1 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:4 | 31 | 0 | 1 | 0 |
| mark_set_disagreement | 76 | 0 | 47 | 9 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 36 | 8 |
| sf6:deletion_needs_two_positive_absences:other | 47 | 0 | 3 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 3 | 0 | 3 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 11 |
| clipping | 20 |
| K1 | 10 |
| edit-guard | 5 |
| A/B disagreement | 0 |
| kind disagreement | 47 |
| R1 uncertainty | 0 |
| other/unclassified | 39 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 11 |
| ["mark_set_disagreement"] | 9 |
| ["sf6:deletion_needs_two_positive_absences:mark"] | 8 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 6 |
| ["K1:flag","K1:observation:unnamed","detector_unnamed_mark","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_bottom","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_top","mark_set_disagreement"] | 2 |
| ["K1:C3:two_accents:evidence_tie","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other","sf6:deletion_needs_two_positive_absences:quote"] | 1 |

### heldout-verification / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:evidence_tie | 2 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:flag | 13 | 0 | 8 | 0 |
| K1:observation:localisation_unknown | 4 | 0 | 2 | 0 |
| K1:observation:unnamed | 9 | 0 | 7 | 0 |
| detector_clipped_bottom | 23 | 0 | 15 | 1 |
| detector_clipped_top | 21 | 0 | 9 | 1 |
| detector_localisation_unknown | 4 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 12 | 0 | 5 | 0 |
| detector_unnamed_mark | 9 | 0 | 7 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 2 | 2 | 0 |
| edit_guard:unsupported_character:1 | 33 | 1 | 1 | 0 |
| edit_guard:unsupported_character:4 | 31 | 1 | 1 | 0 |
| edit_guard:unsupported_raw_character:1 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:4 | 31 | 0 | 1 | 0 |
| mark_set_disagreement | 76 | 0 | 47 | 9 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 36 | 8 |
| sf6:deletion_needs_two_positive_absences:other | 47 | 0 | 3 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 3 | 0 | 3 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 11 |
| clipping | 20 |
| K1 | 10 |
| edit-guard | 5 |
| A/B disagreement | 0 |
| kind disagreement | 47 |
| R1 uncertainty | 0 |
| other/unclassified | 39 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 11 |
| ["mark_set_disagreement"] | 9 |
| ["sf6:deletion_needs_two_positive_absences:mark"] | 8 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 6 |
| ["K1:flag","K1:observation:unnamed","detector_unnamed_mark","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_bottom","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_top","mark_set_disagreement"] | 2 |
| ["K1:C3:two_accents:evidence_tie","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other","sf6:deletion_needs_two_positive_absences:quote"] | 1 |

### ALL / print-instrument

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:evidence_tie | 2 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:flag | 13 | 0 | 8 | 0 |
| K1:observation:localisation_unknown | 4 | 0 | 2 | 0 |
| K1:observation:unnamed | 9 | 0 | 7 | 0 |
| detector_clipped_bottom | 23 | 0 | 15 | 1 |
| detector_clipped_top | 21 | 0 | 9 | 1 |
| detector_localisation_unknown | 4 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 12 | 0 | 5 | 0 |
| detector_unnamed_mark | 9 | 0 | 7 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 2 | 2 | 0 |
| edit_guard:unsupported_character:1 | 33 | 1 | 1 | 0 |
| edit_guard:unsupported_character:4 | 31 | 1 | 1 | 0 |
| edit_guard:unsupported_raw_character:1 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:4 | 31 | 0 | 1 | 0 |
| mark_set_disagreement | 76 | 0 | 47 | 9 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 36 | 8 |
| sf6:deletion_needs_two_positive_absences:other | 47 | 0 | 3 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 3 | 0 | 3 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 11 |
| clipping | 20 |
| K1 | 10 |
| edit-guard | 5 |
| A/B disagreement | 0 |
| kind disagreement | 47 |
| R1 uncertainty | 0 |
| other/unclassified | 39 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 11 |
| ["mark_set_disagreement"] | 9 |
| ["sf6:deletion_needs_two_positive_absences:mark"] | 8 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 6 |
| ["K1:flag","K1:observation:unnamed","detector_unnamed_mark","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_bottom","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_top","mark_set_disagreement"] | 2 |
| ["K1:C3:two_accents:evidence_tie","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other","sf6:deletion_needs_two_positive_absences:quote"] | 1 |

### heldout-verification / print-instrument

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:evidence_tie | 2 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:flag | 13 | 0 | 8 | 0 |
| K1:observation:localisation_unknown | 4 | 0 | 2 | 0 |
| K1:observation:unnamed | 9 | 0 | 7 | 0 |
| detector_clipped_bottom | 23 | 0 | 15 | 1 |
| detector_clipped_top | 21 | 0 | 9 | 1 |
| detector_localisation_unknown | 4 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 12 | 0 | 5 | 0 |
| detector_unnamed_mark | 9 | 0 | 7 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 2 | 2 | 0 |
| edit_guard:unsupported_character:1 | 33 | 1 | 1 | 0 |
| edit_guard:unsupported_character:4 | 31 | 1 | 1 | 0 |
| edit_guard:unsupported_raw_character:1 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:4 | 31 | 0 | 1 | 0 |
| mark_set_disagreement | 76 | 0 | 47 | 9 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 36 | 8 |
| sf6:deletion_needs_two_positive_absences:other | 47 | 0 | 3 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 3 | 0 | 3 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 11 |
| clipping | 20 |
| K1 | 10 |
| edit-guard | 5 |
| A/B disagreement | 0 |
| kind disagreement | 47 |
| R1 uncertainty | 0 |
| other/unclassified | 39 |

| Top exact reason set | Lines |
|---|---:|
| ["mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 11 |
| ["mark_set_disagreement"] | 9 |
| ["sf6:deletion_needs_two_positive_absences:mark"] | 8 |
| ["detector_clipped_bottom","mark_set_disagreement"] | 6 |
| ["K1:flag","K1:observation:unnamed","detector_unnamed_mark","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_bottom","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 2 |
| ["detector_clipped_top","mark_set_disagreement"] | 2 |
| ["K1:C3:two_accents:evidence_tie","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other","sf6:deletion_needs_two_positive_absences:quote"] | 1 |
## ENSEMBLE_AB

| Wave | Source | Lines | HOLD | Held glyph slots |
|---|---|---:|---:|---:|
| ALL | ALL | 64 | 58 | 239 |
| heldout-verification | ALL | 64 | 58 | 239 |
| mixed | ALL | 0 | 0 | 0 |
| openarchives | ALL | 0 | 0 | 0 |
| parliament | ALL | 0 | 0 | 0 |
| round1 | ALL | 0 | 0 | 0 |
| round2 | ALL | 0 | 0 | 0 |
| vouli | ALL | 0 | 0 | 0 |
| ALL | print-instrument | 64 | 58 | 239 |
| heldout-verification | print-instrument | 64 | 58 | 239 |

### ALL / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:evidence_tie | 2 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:flag | 13 | 0 | 8 | 0 |
| K1:observation:localisation_unknown | 4 | 0 | 2 | 0 |
| K1:observation:unnamed | 9 | 0 | 7 | 0 |
| detector_clipped_bottom | 23 | 0 | 15 | 7 |
| detector_clipped_top | 21 | 0 | 9 | 3 |
| detector_localisation_unknown | 4 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 12 | 0 | 5 | 1 |
| detector_unnamed_mark | 9 | 0 | 7 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 2 | 2 | 0 |
| edit_guard:unsupported_character:1 | 33 | 1 | 1 | 0 |
| edit_guard:unsupported_character:4 | 31 | 1 | 1 | 0 |
| edit_guard:unsupported_raw_character:1 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:4 | 31 | 0 | 1 | 0 |
| ensemble_ab_mark_set_disagreement | 17 | 0 | 16 | 5 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 36 | 14 |
| sf6:deletion_needs_two_positive_absences:other | 47 | 0 | 3 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 3 | 0 | 3 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 11 |
| clipping | 20 |
| K1 | 10 |
| edit-guard | 5 |
| A/B disagreement | 16 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 39 |

| Top exact reason set | Lines |
|---|---:|
| ["sf6:deletion_needs_two_positive_absences:mark"] | 14 |
| ["detector_clipped_bottom"] | 7 |
| ["ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 5 |
| ["ensemble_ab_mark_set_disagreement"] | 5 |
| ["K1:flag","K1:observation:unnamed","detector_unnamed_mark","sf6:deletion_needs_two_positive_absences:mark"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 3 |
| ["detector_clipped_top"] | 3 |
| ["K1:C3:two_accents:evidence_tie","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other","sf6:deletion_needs_two_positive_absences:quote"] | 1 |
| ["K1:flag","K1:observation:localisation_unknown","K1:observation:unnamed","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 1 |

### heldout-verification / ALL

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:evidence_tie | 2 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:flag | 13 | 0 | 8 | 0 |
| K1:observation:localisation_unknown | 4 | 0 | 2 | 0 |
| K1:observation:unnamed | 9 | 0 | 7 | 0 |
| detector_clipped_bottom | 23 | 0 | 15 | 7 |
| detector_clipped_top | 21 | 0 | 9 | 3 |
| detector_localisation_unknown | 4 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 12 | 0 | 5 | 1 |
| detector_unnamed_mark | 9 | 0 | 7 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 2 | 2 | 0 |
| edit_guard:unsupported_character:1 | 33 | 1 | 1 | 0 |
| edit_guard:unsupported_character:4 | 31 | 1 | 1 | 0 |
| edit_guard:unsupported_raw_character:1 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:4 | 31 | 0 | 1 | 0 |
| ensemble_ab_mark_set_disagreement | 17 | 0 | 16 | 5 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 36 | 14 |
| sf6:deletion_needs_two_positive_absences:other | 47 | 0 | 3 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 3 | 0 | 3 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 11 |
| clipping | 20 |
| K1 | 10 |
| edit-guard | 5 |
| A/B disagreement | 16 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 39 |

| Top exact reason set | Lines |
|---|---:|
| ["sf6:deletion_needs_two_positive_absences:mark"] | 14 |
| ["detector_clipped_bottom"] | 7 |
| ["ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 5 |
| ["ensemble_ab_mark_set_disagreement"] | 5 |
| ["K1:flag","K1:observation:unnamed","detector_unnamed_mark","sf6:deletion_needs_two_positive_absences:mark"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 3 |
| ["detector_clipped_top"] | 3 |
| ["K1:C3:two_accents:evidence_tie","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other","sf6:deletion_needs_two_positive_absences:quote"] | 1 |
| ["K1:flag","K1:observation:localisation_unknown","K1:observation:unnamed","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 1 |

### ALL / print-instrument

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:evidence_tie | 2 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:flag | 13 | 0 | 8 | 0 |
| K1:observation:localisation_unknown | 4 | 0 | 2 | 0 |
| K1:observation:unnamed | 9 | 0 | 7 | 0 |
| detector_clipped_bottom | 23 | 0 | 15 | 7 |
| detector_clipped_top | 21 | 0 | 9 | 3 |
| detector_localisation_unknown | 4 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 12 | 0 | 5 | 1 |
| detector_unnamed_mark | 9 | 0 | 7 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 2 | 2 | 0 |
| edit_guard:unsupported_character:1 | 33 | 1 | 1 | 0 |
| edit_guard:unsupported_character:4 | 31 | 1 | 1 | 0 |
| edit_guard:unsupported_raw_character:1 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:4 | 31 | 0 | 1 | 0 |
| ensemble_ab_mark_set_disagreement | 17 | 0 | 16 | 5 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 36 | 14 |
| sf6:deletion_needs_two_positive_absences:other | 47 | 0 | 3 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 3 | 0 | 3 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 11 |
| clipping | 20 |
| K1 | 10 |
| edit-guard | 5 |
| A/B disagreement | 16 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 39 |

| Top exact reason set | Lines |
|---|---:|
| ["sf6:deletion_needs_two_positive_absences:mark"] | 14 |
| ["detector_clipped_bottom"] | 7 |
| ["ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 5 |
| ["ensemble_ab_mark_set_disagreement"] | 5 |
| ["K1:flag","K1:observation:unnamed","detector_unnamed_mark","sf6:deletion_needs_two_positive_absences:mark"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 3 |
| ["detector_clipped_top"] | 3 |
| ["K1:C3:two_accents:evidence_tie","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other","sf6:deletion_needs_two_positive_absences:quote"] | 1 |
| ["K1:flag","K1:observation:localisation_unknown","K1:observation:unnamed","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 1 |

### heldout-verification / print-instrument

| Exact reason | Slots | Line guards | Lines | Lines ALONE |
|---|---:|---:|---:|---:|
| K1:C3:two_accents:evidence_tie | 2 | 0 | 1 | 0 |
| K1:C4:grave_not_final:impossible_by_rule | 1 | 0 | 1 | 0 |
| K1:flag | 13 | 0 | 8 | 0 |
| K1:observation:localisation_unknown | 4 | 0 | 2 | 0 |
| K1:observation:unnamed | 9 | 0 | 7 | 0 |
| detector_clipped_bottom | 23 | 0 | 15 | 7 |
| detector_clipped_top | 21 | 0 | 9 | 3 |
| detector_localisation_unknown | 4 | 0 | 2 | 0 |
| detector_segmentation_uncertain | 12 | 0 | 5 | 1 |
| detector_unnamed_mark | 9 | 0 | 7 | 0 |
| edit_guard:base_or_character_mismatch | 0 | 3 | 3 | 0 |
| edit_guard:punctuation_mismatch | 0 | 2 | 2 | 0 |
| edit_guard:unsupported_character:1 | 33 | 1 | 1 | 0 |
| edit_guard:unsupported_character:4 | 31 | 1 | 1 | 0 |
| edit_guard:unsupported_raw_character:1 | 33 | 0 | 1 | 0 |
| edit_guard:unsupported_raw_character:4 | 31 | 0 | 1 | 0 |
| ensemble_ab_mark_set_disagreement | 17 | 0 | 16 | 5 |
| sf6:deletion_needs_two_positive_absences:apostrophe | 1 | 0 | 1 | 0 |
| sf6:deletion_needs_two_positive_absences:mark | 47 | 0 | 36 | 14 |
| sf6:deletion_needs_two_positive_absences:other | 47 | 0 | 3 | 0 |
| sf6:deletion_needs_two_positive_absences:quote | 3 | 0 | 3 | 1 |

| Family | Lines held |
|---|---:|
| localisation/segmentation | 11 |
| clipping | 20 |
| K1 | 10 |
| edit-guard | 5 |
| A/B disagreement | 16 |
| kind disagreement | 0 |
| R1 uncertainty | 0 |
| other/unclassified | 39 |

| Top exact reason set | Lines |
|---|---:|
| ["sf6:deletion_needs_two_positive_absences:mark"] | 14 |
| ["detector_clipped_bottom"] | 7 |
| ["ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 5 |
| ["ensemble_ab_mark_set_disagreement"] | 5 |
| ["K1:flag","K1:observation:unnamed","detector_unnamed_mark","sf6:deletion_needs_two_positive_absences:mark"] | 4 |
| ["detector_clipped_bottom","detector_clipped_top","sf6:deletion_needs_two_positive_absences:mark"] | 3 |
| ["detector_clipped_top"] | 3 |
| ["K1:C3:two_accents:evidence_tie","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark"] | 1 |
| ["K1:C4:grave_not_final:impossible_by_rule","edit_guard:base_or_character_mismatch","edit_guard:punctuation_mismatch","ensemble_ab_mark_set_disagreement","sf6:deletion_needs_two_positive_absences:mark","sf6:deletion_needs_two_positive_absences:other","sf6:deletion_needs_two_positive_absences:quote"] | 1 |
| ["K1:flag","K1:observation:localisation_unknown","K1:observation:unnamed","detector_localisation_unknown","detector_segmentation_uncertain","detector_unnamed_mark"] | 1 |

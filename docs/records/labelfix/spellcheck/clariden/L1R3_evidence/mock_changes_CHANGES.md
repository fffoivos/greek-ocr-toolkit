# L1R3 deletion / change census

Analysis only. The reported correction count is real mark-correction lines:
corrected-status lines with at least one combining-mark insertion or deletion.
NFD difflib, autojunk=False. Mark replacements count two codepoint edits;
an elision alias substitution counts once. Classes and source support describe
labels, not printed truth. Class marginals overlap real-mark totals.

Word-final and lowercase consonant-initial elision aliases are folded for
comparison (including ᾿στὸν → 'στὸν). Spacing breathings before capitals/vowels
are not folded. Explicit U+0374/U+0384/U+02B9 and apostrophes after uppercase
Greek numeral tokens, decimal tokens or Unicode numeral letters are keraia.
Lowercase ASCII-apostrophe numeral/elision ambiguity needs print adjudication.
Single-source means original-label codepoint/alias atom absent from recogniser
at the same letter boundary and occurrence. All deleted classes are counted.

SF6 deletion HOLD classes count each line once per class; checks count atoms.
MOVE applied counts only actual corrected releases. Proposal lines may still HOLD
on another veto. The full audit population is real_mark_correction_lines.jsonl
(line_id, wave, mode); alias-only and punctuation-only changes are excluded.

## PRESENCE

| Wave | Lines | Corrected status | Real mark-correction lines | Real mark lines with single-source deletion | Share of real mark-correction lines |
|---|---:|---:|---:|---:|---:|
| ALL | 64 | 2 | 2 | 0 | 0.000000% |
| heldout-verification | 64 | 2 | 2 | 0 | 0.000000% |
| mixed | 0 | 0 | 0 | 0 | 0.000000% |
| openarchives | 0 | 0 | 0 | 0 | 0.000000% |
| parliament | 0 | 0 | 0 | 0 | 0.000000% |
| round1 | 0 | 0 | 0 | 0 | 0.000000% |
| round2 | 0 | 0 | 0 | 0 | 0.000000% |
| vouli | 0 | 0 | 0 | 0 | 0.000000% |

### SF6 ALL

Deletion HOLD lines: 39; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 36 | 47 | 0b7bf21d-p000002-l0004, 0b7bf21d-p000013-l0026, 177b717d-p000013-l0009, 177b717d-p000030-l0011, 177b717d-p000045-l0013, 177b717d-p000097-l0007, 177b717d-p000104-l0012, 384c3f89-p000050-l0027, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000053-l0028, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0033, 384c3f89-p000068-l0036, 384c3f89-p000091-l0017, 384c3f89-p000091-l0039, 384c3f89-p000096-l0004, 384c3f89-p000096-l0005, 384c3f89-p000096-l0010 |
| apostrophe | 1 | 1 | 384c3f89-p000050-l0027 |
| quote | 3 | 3 | 0b7bf21d-p000002-l0004, 177b717d-p000067-l0009, 177b717d-p000097-l0010 |
| keraia | 0 | 0 |  |
| other | 3 | 47 | 0b7bf21d-p000002-l0004, 177b717d-p000030-l0004, 384c3f89-p000050-l0027 |

### ALL

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 2 | 2 | 384c3f89-p000050-l0040, 384c3f89-p000205-l0013 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 2 | 2 | 384c3f89-p000050-l0040, 384c3f89-p000205-l0013 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 heldout-verification

Deletion HOLD lines: 39; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 36 | 47 | 0b7bf21d-p000002-l0004, 0b7bf21d-p000013-l0026, 177b717d-p000013-l0009, 177b717d-p000030-l0011, 177b717d-p000045-l0013, 177b717d-p000097-l0007, 177b717d-p000104-l0012, 384c3f89-p000050-l0027, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000053-l0028, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0033, 384c3f89-p000068-l0036, 384c3f89-p000091-l0017, 384c3f89-p000091-l0039, 384c3f89-p000096-l0004, 384c3f89-p000096-l0005, 384c3f89-p000096-l0010 |
| apostrophe | 1 | 1 | 384c3f89-p000050-l0027 |
| quote | 3 | 3 | 0b7bf21d-p000002-l0004, 177b717d-p000067-l0009, 177b717d-p000097-l0010 |
| keraia | 0 | 0 |  |
| other | 3 | 47 | 0b7bf21d-p000002-l0004, 177b717d-p000030-l0004, 384c3f89-p000050-l0027 |

### heldout-verification

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 2 | 2 | 384c3f89-p000050-l0040, 384c3f89-p000205-l0013 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 2 | 2 | 384c3f89-p000050-l0040, 384c3f89-p000205-l0013 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 mixed

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### mixed

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 openarchives

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### openarchives

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 parliament

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### parliament

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 round1

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### round1

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 round2

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### round2

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 vouli

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### vouli

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |
## FULL

| Wave | Lines | Corrected status | Real mark-correction lines | Real mark lines with single-source deletion | Share of real mark-correction lines |
|---|---:|---:|---:|---:|---:|
| ALL | 64 | 2 | 2 | 0 | 0.000000% |
| heldout-verification | 64 | 2 | 2 | 0 | 0.000000% |
| mixed | 0 | 0 | 0 | 0 | 0.000000% |
| openarchives | 0 | 0 | 0 | 0 | 0.000000% |
| parliament | 0 | 0 | 0 | 0 | 0.000000% |
| round1 | 0 | 0 | 0 | 0 | 0.000000% |
| round2 | 0 | 0 | 0 | 0 | 0.000000% |
| vouli | 0 | 0 | 0 | 0 | 0.000000% |

### SF6 ALL

Deletion HOLD lines: 39; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 36 | 47 | 0b7bf21d-p000002-l0004, 0b7bf21d-p000013-l0026, 177b717d-p000013-l0009, 177b717d-p000030-l0011, 177b717d-p000045-l0013, 177b717d-p000097-l0007, 177b717d-p000104-l0012, 384c3f89-p000050-l0027, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000053-l0028, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0033, 384c3f89-p000068-l0036, 384c3f89-p000091-l0017, 384c3f89-p000091-l0039, 384c3f89-p000096-l0004, 384c3f89-p000096-l0005, 384c3f89-p000096-l0010 |
| apostrophe | 1 | 1 | 384c3f89-p000050-l0027 |
| quote | 3 | 3 | 0b7bf21d-p000002-l0004, 177b717d-p000067-l0009, 177b717d-p000097-l0010 |
| keraia | 0 | 0 |  |
| other | 3 | 47 | 0b7bf21d-p000002-l0004, 177b717d-p000030-l0004, 384c3f89-p000050-l0027 |

### ALL

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 2 | 2 | 384c3f89-p000050-l0040, 384c3f89-p000205-l0013 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 2 | 2 | 384c3f89-p000050-l0040, 384c3f89-p000205-l0013 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 heldout-verification

Deletion HOLD lines: 39; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 36 | 47 | 0b7bf21d-p000002-l0004, 0b7bf21d-p000013-l0026, 177b717d-p000013-l0009, 177b717d-p000030-l0011, 177b717d-p000045-l0013, 177b717d-p000097-l0007, 177b717d-p000104-l0012, 384c3f89-p000050-l0027, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000053-l0028, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0033, 384c3f89-p000068-l0036, 384c3f89-p000091-l0017, 384c3f89-p000091-l0039, 384c3f89-p000096-l0004, 384c3f89-p000096-l0005, 384c3f89-p000096-l0010 |
| apostrophe | 1 | 1 | 384c3f89-p000050-l0027 |
| quote | 3 | 3 | 0b7bf21d-p000002-l0004, 177b717d-p000067-l0009, 177b717d-p000097-l0010 |
| keraia | 0 | 0 |  |
| other | 3 | 47 | 0b7bf21d-p000002-l0004, 177b717d-p000030-l0004, 384c3f89-p000050-l0027 |

### heldout-verification

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 2 | 2 | 384c3f89-p000050-l0040, 384c3f89-p000205-l0013 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 2 | 2 | 384c3f89-p000050-l0040, 384c3f89-p000205-l0013 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 mixed

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### mixed

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 openarchives

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### openarchives

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 parliament

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### parliament

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 round1

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### round1

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 round2

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### round2

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 vouli

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### vouli

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |
## ENSEMBLE_AB

| Wave | Lines | Corrected status | Real mark-correction lines | Real mark lines with single-source deletion | Share of real mark-correction lines |
|---|---:|---:|---:|---:|---:|
| ALL | 64 | 2 | 2 | 0 | 0.000000% |
| heldout-verification | 64 | 2 | 2 | 0 | 0.000000% |
| mixed | 0 | 0 | 0 | 0 | 0.000000% |
| openarchives | 0 | 0 | 0 | 0 | 0.000000% |
| parliament | 0 | 0 | 0 | 0 | 0.000000% |
| round1 | 0 | 0 | 0 | 0 | 0.000000% |
| round2 | 0 | 0 | 0 | 0 | 0.000000% |
| vouli | 0 | 0 | 0 | 0 | 0.000000% |

### SF6 ALL

Deletion HOLD lines: 39; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 36 | 47 | 0b7bf21d-p000002-l0004, 0b7bf21d-p000013-l0026, 177b717d-p000013-l0009, 177b717d-p000030-l0011, 177b717d-p000045-l0013, 177b717d-p000097-l0007, 177b717d-p000104-l0012, 384c3f89-p000050-l0027, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000053-l0028, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0033, 384c3f89-p000068-l0036, 384c3f89-p000091-l0017, 384c3f89-p000091-l0039, 384c3f89-p000096-l0004, 384c3f89-p000096-l0005, 384c3f89-p000096-l0010 |
| apostrophe | 1 | 1 | 384c3f89-p000050-l0027 |
| quote | 3 | 3 | 0b7bf21d-p000002-l0004, 177b717d-p000067-l0009, 177b717d-p000097-l0010 |
| keraia | 0 | 0 |  |
| other | 3 | 47 | 0b7bf21d-p000002-l0004, 177b717d-p000030-l0004, 384c3f89-p000050-l0027 |

### ALL

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 2 | 2 | 384c3f89-p000050-l0040, 384c3f89-p000205-l0013 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 2 | 2 | 384c3f89-p000050-l0040, 384c3f89-p000205-l0013 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 heldout-verification

Deletion HOLD lines: 39; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 36 | 47 | 0b7bf21d-p000002-l0004, 0b7bf21d-p000013-l0026, 177b717d-p000013-l0009, 177b717d-p000030-l0011, 177b717d-p000045-l0013, 177b717d-p000097-l0007, 177b717d-p000104-l0012, 384c3f89-p000050-l0027, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000053-l0028, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0033, 384c3f89-p000068-l0036, 384c3f89-p000091-l0017, 384c3f89-p000091-l0039, 384c3f89-p000096-l0004, 384c3f89-p000096-l0005, 384c3f89-p000096-l0010 |
| apostrophe | 1 | 1 | 384c3f89-p000050-l0027 |
| quote | 3 | 3 | 0b7bf21d-p000002-l0004, 177b717d-p000067-l0009, 177b717d-p000097-l0010 |
| keraia | 0 | 0 |  |
| other | 3 | 47 | 0b7bf21d-p000002-l0004, 177b717d-p000030-l0004, 384c3f89-p000050-l0027 |

### heldout-verification

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 2 | 2 | 384c3f89-p000050-l0040, 384c3f89-p000205-l0013 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 2 | 2 | 384c3f89-p000050-l0040, 384c3f89-p000205-l0013 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 mixed

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### mixed

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 openarchives

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### openarchives

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 parliament

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### parliament

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 round1

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### round1

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 round2

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### round2

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 vouli

Deletion HOLD lines: 0; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 0 | 0 |  |
| apostrophe | 0 | 0 |  |
| quote | 0 | 0 |  |
| keraia | 0 | 0 |  |
| other | 0 | 0 |  |

### vouli

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

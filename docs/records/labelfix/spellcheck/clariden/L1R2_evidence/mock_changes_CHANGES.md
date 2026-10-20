# L1R2 deletion / change census

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

## PRESENCE

| Wave | Lines | Corrected status | Real mark-correction lines | Real mark lines with single-source deletion | Share of real mark-correction lines |
|---|---:|---:|---:|---:|---:|
| ALL | 64 | 14 | 14 | 8 | 57.142857% |
| heldout-verification | 64 | 14 | 14 | 8 | 57.142857% |
| mixed | 0 | 0 | 0 | 0 | 0.000000% |
| openarchives | 0 | 0 | 0 | 0 | 0.000000% |
| parliament | 0 | 0 | 0 | 0 | 0.000000% |
| round1 | 0 | 0 | 0 | 0 | 0.000000% |
| round2 | 0 | 0 | 0 | 0 | 0.000000% |
| vouli | 0 | 0 | 0 | 0 | 0.000000% |

### ALL

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 14 | 30 | 177b717d-p000030-l0011, 177b717d-p000045-l0013, 177b717d-p000097-l0010, 384c3f89-p000050-l0040, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0036, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011, 384c3f89-p000205-l0013 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 11 | 12 | 177b717d-p000030-l0011, 177b717d-p000045-l0013, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0036, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011 |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 1 | 1 | 177b717d-p000097-l0010 |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 8 | 9 | 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0023, 384c3f89-p000068-l0036, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011 |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 3 | 3 | 177b717d-p000030-l0011, 177b717d-p000045-l0013, 384c3f89-p000059-l0013 |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 1 | 1 | 177b717d-p000097-l0010 |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 14 | 18 | 177b717d-p000030-l0011, 177b717d-p000045-l0013, 177b717d-p000097-l0010, 384c3f89-p000050-l0040, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0036, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011, 384c3f89-p000205-l0013 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### heldout-verification

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 14 | 30 | 177b717d-p000030-l0011, 177b717d-p000045-l0013, 177b717d-p000097-l0010, 384c3f89-p000050-l0040, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0036, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011, 384c3f89-p000205-l0013 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 11 | 12 | 177b717d-p000030-l0011, 177b717d-p000045-l0013, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0036, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011 |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 1 | 1 | 177b717d-p000097-l0010 |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 8 | 9 | 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0023, 384c3f89-p000068-l0036, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011 |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 3 | 3 | 177b717d-p000030-l0011, 177b717d-p000045-l0013, 384c3f89-p000059-l0013 |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 1 | 1 | 177b717d-p000097-l0010 |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 14 | 18 | 177b717d-p000030-l0011, 177b717d-p000045-l0013, 177b717d-p000097-l0010, 384c3f89-p000050-l0040, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0036, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011, 384c3f89-p000205-l0013 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

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
| ALL | 64 | 11 | 11 | 7 | 63.636364% |
| heldout-verification | 64 | 11 | 11 | 7 | 63.636364% |
| mixed | 0 | 0 | 0 | 0 | 0.000000% |
| openarchives | 0 | 0 | 0 | 0 | 0.000000% |
| parliament | 0 | 0 | 0 | 0 | 0.000000% |
| round1 | 0 | 0 | 0 | 0 | 0.000000% |
| round2 | 0 | 0 | 0 | 0 | 0.000000% |
| vouli | 0 | 0 | 0 | 0 | 0.000000% |

### ALL

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 11 | 22 | 177b717d-p000097-l0010, 384c3f89-p000050-l0040, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011, 384c3f89-p000205-l0013 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 8 | 9 | 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011 |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 1 | 1 | 177b717d-p000097-l0010 |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 7 | 8 | 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0023, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011 |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 1 | 1 | 384c3f89-p000059-l0013 |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 1 | 1 | 177b717d-p000097-l0010 |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 11 | 13 | 177b717d-p000097-l0010, 384c3f89-p000050-l0040, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011, 384c3f89-p000205-l0013 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### heldout-verification

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 11 | 22 | 177b717d-p000097-l0010, 384c3f89-p000050-l0040, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011, 384c3f89-p000205-l0013 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 8 | 9 | 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011 |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 1 | 1 | 177b717d-p000097-l0010 |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 7 | 8 | 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0023, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011 |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 1 | 1 | 384c3f89-p000059-l0013 |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 1 | 1 | 177b717d-p000097-l0010 |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 11 | 13 | 177b717d-p000097-l0010, 384c3f89-p000050-l0040, 384c3f89-p000050-l0041, 384c3f89-p000053-l0004, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000205-l0011, 384c3f89-p000205-l0013 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

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
| ALL | 64 | 17 | 17 | 12 | 70.588235% |
| heldout-verification | 64 | 17 | 17 | 12 | 70.588235% |
| mixed | 0 | 0 | 0 | 0 | 0.000000% |
| openarchives | 0 | 0 | 0 | 0 | 0.000000% |
| parliament | 0 | 0 | 0 | 0 | 0.000000% |
| round1 | 0 | 0 | 0 | 0 | 0.000000% |
| round2 | 0 | 0 | 0 | 0 | 0.000000% |
| vouli | 0 | 0 | 0 | 0 | 0.000000% |

### ALL

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 17 | 36 | 177b717d-p000097-l0010, 384c3f89-p000050-l0040, 384c3f89-p000050-l0041, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0033, 384c3f89-p000068-l0036, 384c3f89-p000091-l0017, 384c3f89-p000096-l0004, 384c3f89-p000096-l0005, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000183-l0029, 384c3f89-p000205-l0011, 384c3f89-p000205-l0013, 602cc72e-p000167-l0027 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 14 | 17 | 384c3f89-p000050-l0041, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0033, 384c3f89-p000068-l0036, 384c3f89-p000091-l0017, 384c3f89-p000096-l0004, 384c3f89-p000096-l0005, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000183-l0029, 384c3f89-p000205-l0011, 602cc72e-p000167-l0027 |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 1 | 1 | 177b717d-p000097-l0010 |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 12 | 15 | 384c3f89-p000050-l0041, 384c3f89-p000059-l0023, 384c3f89-p000068-l0036, 384c3f89-p000091-l0017, 384c3f89-p000096-l0004, 384c3f89-p000096-l0005, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000183-l0029, 384c3f89-p000205-l0011, 602cc72e-p000167-l0027 |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 2 | 2 | 384c3f89-p000059-l0013, 384c3f89-p000068-l0033 |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 1 | 1 | 177b717d-p000097-l0010 |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 16 | 19 | 177b717d-p000097-l0010, 384c3f89-p000050-l0040, 384c3f89-p000050-l0041, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0033, 384c3f89-p000068-l0036, 384c3f89-p000091-l0017, 384c3f89-p000096-l0004, 384c3f89-p000096-l0005, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000183-l0029, 384c3f89-p000205-l0011, 384c3f89-p000205-l0013 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### heldout-verification

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 17 | 36 | 177b717d-p000097-l0010, 384c3f89-p000050-l0040, 384c3f89-p000050-l0041, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0033, 384c3f89-p000068-l0036, 384c3f89-p000091-l0017, 384c3f89-p000096-l0004, 384c3f89-p000096-l0005, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000183-l0029, 384c3f89-p000205-l0011, 384c3f89-p000205-l0013, 602cc72e-p000167-l0027 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 14 | 17 | 384c3f89-p000050-l0041, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0033, 384c3f89-p000068-l0036, 384c3f89-p000091-l0017, 384c3f89-p000096-l0004, 384c3f89-p000096-l0005, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000183-l0029, 384c3f89-p000205-l0011, 602cc72e-p000167-l0027 |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 1 | 1 | 177b717d-p000097-l0010 |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 12 | 15 | 384c3f89-p000050-l0041, 384c3f89-p000059-l0023, 384c3f89-p000068-l0036, 384c3f89-p000091-l0017, 384c3f89-p000096-l0004, 384c3f89-p000096-l0005, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000183-l0029, 384c3f89-p000205-l0011, 602cc72e-p000167-l0027 |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 2 | 2 | 384c3f89-p000059-l0013, 384c3f89-p000068-l0033 |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 1 | 1 | 177b717d-p000097-l0010 |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 16 | 19 | 177b717d-p000097-l0010, 384c3f89-p000050-l0040, 384c3f89-p000050-l0041, 384c3f89-p000059-l0013, 384c3f89-p000059-l0023, 384c3f89-p000068-l0033, 384c3f89-p000068-l0036, 384c3f89-p000091-l0017, 384c3f89-p000096-l0004, 384c3f89-p000096-l0005, 384c3f89-p000096-l0010, 384c3f89-p000096-l0031, 384c3f89-p000182-l0016, 384c3f89-p000183-l0029, 384c3f89-p000205-l0011, 384c3f89-p000205-l0013 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

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

# L1A2 — Print audit of 100 corrected lines from the sf6 AB release (L1R3 3680729)

Design: 100 of the 155 ENSEMBLE_AB sf6 real mark-correction lines (all vouli 6, parliament 3, openarchives 2; seeded round1 41, round2 30,
mixed 18; weights N/n). 101 word cards (Google form vs released form, + recogniser form where different) + 9 pixel-verified controls; two
blind Opus readers (reader 2 in reverse order), controls 9/9 each; agreement 92/101; 9 blind tiebreaks (1 high, 5 medium, 3 low confidence).
Truth = the ink, misprints included; elision aliases one atom. Answers: `S8_DEV/audit100_private/`; key `S8_DEV/private/audit100/`.

## Result
| | |
|---|---|
| Lines whose released words all match the print | **83/100 = 83.0%** (Wilson 95% 74.5–89.1) |
| Weighted to the 155-line population | **82.5%** (bootstrap 95% 75.0–89.8) |
| Per wave (right/audited) | parliament 3/3, vouli 6/6, mixed 17/18, round1 33/41, round2 23/30, openarchives 1/2 |
| Wrong cards | 16 Google-right (Google's original matched the print), 1 unreadable |

## Error class
13 of the 17 failing lines are **iota subscripts INSERTED by the release where the print has none** (τρώγη→τρώγῃ, νύμφη→νύμφῃ, τῆς→τῇς,
Μεγάλη→Μεγάλῃ, παληκαριά→παλῃκαριά, 1η→1ῃ, δεσπότη→δεσπότῃ, ὑποχωρήση→ὑποχωρήσῃ, τρέχη→τρέχῃ, εὐπορῆς→εὐπορῇς, περάση→περάσῃ, Ῥώμη→Ῥώμῃ,
δείξη→δείξῃ [unreadable]); the other 4 are breathings/accents inserted on unmarked forms (οι→οἱ, ο→ὁ, .Α.→.Ἀ., ΦΡΑΓΚΙΣΚΗ→ΦΡΆΓΚΙΣΚΗ).
SF6 governs deletions only; insertions pass on reader agreement (A∧B) alone. The detector's below-mark recall is very low (held-out below
47.9%, DEV subscript 0–33%), so it cannot confirm subscripts. Excluding inserted subscripts, the audited corrections match the print in
83/87 lines (95%): the reader's mark naming is sound; the defect is a missing symmetry in the gate (deletions need two signals since SF6,
insertions still need only reader agreement).

## Implication (for the owner; the gate is frozen tonight)
A rule symmetric to SF6 — an inserted mark needs two positive presence signals (reader AND detector, or reader AND scored recogniser text),
and subscript insertions need an observed below-mark — would remove the dominant error class; with today's detector it would hold almost
every subscript insertion. Not implemented: the coordinator's hard stop forbids further gate changes tonight.

## Ruling (coordinator, 17 Oct)
The sf6 release is NOT bound: 82.5% precision with inserted iota subscripts as the dominant error class fails the owner's rule
(transcribe what is printed). SF7 (insertion symmetry) is written as a brief + witnesses for the owner's morning decision; no run tonight.

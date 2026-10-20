# L1A — Print audit of the 48 masking-released L1M lines, and the elision-deletion defect in the sf4 releases

Readers: two independent blind Opus readers (each split in two halves; reader 2 in reverse order), 124 items = 114 cards + 10 planted
controls; both readers 10/10 on controls; agreement 108/114; 4 disagreements settled by a blind third reader (2 low, 2 medium confidence);
2 disagreements are representation-only (both readers: one smooth breathing, em dash) and are scored as such. Truth = the ink, misprints
included; elision apostrophe aliases (' ’ ʼ ᾽ ᾿ word-final) compared as one atom (codec v2.1); spacing ᾿ before a capital = a breathing.
Answers: `S8_DEV/audit_private/` (readers, tiebreak, audit_final.json); key `S8_DEV/private/audit/items_key.json`.

## Result
| Claim | Lines | All carded words right | Wrong |
|---|---|---|---|
| corrected (changed word) | 14 | 8 (57%) | 6 — in all 6 Google's original form matched the print |
| kept unchanged (disputed words + 20% of undisputed) | 34 | 29 (85%, lower bound on errors) | 5 lines / 6 words — Google's marks not as printed |

Wrong corrections: 2 printed elision apostrophes DELETED (κ᾿ → κ, μ᾿ → μ); 2 doubled breathing (Google "-᾿Αλλά" = one breathing, released
"-’Ἀλλά" = apostrophe + breathing; the recogniser's text carries both); 1 rough for smooth (ἐν → ἑν); 1 printed iota subscript removed
(διορίσῃ → διορίση). Wrong unchanged: 3 iota subscripts in the label that are not printed (λόγῳ, ἐντόνῳ, δώσῃ), 2 printed misprint-level marks
(ἥμῶν, άμέσως; low confidence), 1 printed stray grave (λομένὼν).

## The release defect (v2-corrected-ensemble-ab-sf4, L1R 3679725), from a label diff of all 2,107 corrected lines
| Class | Lines |
|---|---|
| deletes a printed elision apostrophe (753 deletions: μ᾿ ἐγοήτευσαν, ν᾿ ἀποδοθῇ, δι᾿ ἧς, κι᾿ ἄλλο, Μετ᾿ ὀλίγας …) | 714 (34%) — 647 apostrophe-only + 67 with mark changes |
| codepoint alias only (᾿/᾽ → ’; the codec v2.1 fold, not a correction) | 431 (20%) |
| combining mark changes (± alias) | 962 (46%) |
Mechanism (L1M witnesses): under ENSEMBLE_AB the detector supplies apostrophes; where it finds none, the composer drops Google's elision
mark even though the recogniser's own text has it (`κ' ἡ`, `μ' αὐτά`). The 666 held-out instrument did not catch it (it scores marks, not
elision). Real mark-correction lines ≈ 1,029 (0.8% of polytonic lines), not 2,107.

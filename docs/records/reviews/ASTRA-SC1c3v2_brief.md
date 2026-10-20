# ASTRA-SC1 cycle 3 — verification pass 2 (same reviewer session): SF5 only

Since your CLOSED verdict (ASTRA-SC1c3v), a print audit found a defect none of the cycles covered: the sf4 releases DELETE printed elision
apostrophes (AB: 714 of 2,107 corrected lines, 753 deletions; PRESENCE 354/1,003; FULL 323/903), because under ENSEMBLE_AB the detector
supplies apostrophes and the composer dropped Google's elision mark when the detector found none, although the recogniser's text had it.
Also: Google's spacing ᾿ before a capital (one breathing) was kept while the combining breathing was added (two marks), and alias-only
codepoint swaps (᾿/᾽/' → ’) were counted as corrections (431 AB lines). Evidence: `~/Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/
spellcheck/L1A_AUDIT_REPORT.md` (read-only). The sf4 releases are unbound. The 666 instrument never scored elision.

The fix round SF5 is committed on `opus/spellcheck` (5bdbcd41; `docs/records/labelfix/spellcheck/SF5_REPORT.md`, policy `sf5-release-v1`). The
coordinator's ruling, exactly: (1) never delete an elision mark that Google and the recogniser both have; (2) a spacing ᾿/᾽ before a capital
becomes the combining breathing in one edit, never kept alongside it; (3) alias-only lines are not corrections. Nothing else in the gate changes.

## Verify SF5 only (no new scope)
1. Do the three rules hold as written, and only these? Read the diff c6064650..5bdbcd41 (`release_gate.py` `release_text`, `_breathing_pair`
   and the edit-guard change; `text.py` `word_final_elision`, `spacing_breathing`, `punctuation_sites`, `elision_alias_key`; `l1_common.py`).
   Probe: can a printed elision present in both Google and the recogniser still be deleted (letter-sequence mismatch paths, multiple
   apostrophes, apostrophe + quote, line-final elision, hyphenation, combining-mark-after-letter cases)? Can `_breathing_pair` remove a real
   apostrophe, or a breathing without attachment? Does alias accounting ever hide a real mark edit?
2. Did SF5 change any slot decision, reason or mark output relative to sf4 (held-out 666, the 56 witnesses, the M2 dev pool)? The report
   claims identical mark rows (AB corrected 45, wrong 2, new 6) — confirm.
3. Is the new elision row's truth source and coverage stated correctly, and is held-out elision deleted 26→1 right?
4. Note, do not rule: the residual single-source deletions SF5 keeps by ruling (e.g. numeral keraia `Ι'.` → `Ι.` on
   `a300f5e1c3f6a38d97201791-p000442-l0085`; word-initial `᾿στὸν` → `'στὸν`). Count them if you can and list them as "out of scope notes".
Your earlier C3/C2 findings stay as you closed them; re-run their repository tests only to confirm SF5 did not regress them.

Last line: `ASTRA-SC1c3v2 VERDICT: <CLOSED|NOT CLOSED>; SF5 rules hold <yes|no>; slot decisions unchanged <yes|no>; recompose under sf5-release-v1 allowed: <yes|no>`.

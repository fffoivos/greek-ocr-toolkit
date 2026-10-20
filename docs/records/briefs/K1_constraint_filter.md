# K1 — Orthographic constraint filter on our independent reading (gpt-6.1-sol, xhigh)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck` (branch `opus/spellcheck`, head 6c5f9783 or later). No `.git` writes. Network OFF.
Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python` with `PYTHONPATH=$PWD`. Mac CPU, cached alignments,
≤ 20 min. Change NO detector geometry and NO classifier; this task only filters the reading.

## Why
Owner (16 Oct, day one): "three accents over a letter (impossible)". S6's reading still puts impossible marks on the owner's pages:
circumflex on ρ (Ἐμπρ͂ὂς, τρ͂ἰσκότειδο), breathing on a non-initial ι (πὄχεἵ, βἳος, αἲψα), breathing on a medial ο (ὂ). The deterministic
rules already exist in `greekocr/labelfix/constraints.py` (C1–C7 with the census exceptions: medial ῤῥ, crasis/elision coronis, all-caps
words unchecked, hyphenated parts, line-final enclitic). Coordinator: every detector and R1 reading passes through it before reporting;
impossible marks never reach the owner's page; "removed by constraint" is its own count.

## The tension you must measure, not assume away
The owner's rule is "transcribe what is printed": misprints stay. A constraint filter that deletes a mark that IS printed violates it.
So: measure on the 666 held-out lines (print truth, S2–S6 instrument) how many marks each rule would remove that print truth says ARE
printed. Rules whose removals are ≥ 99% false marks (or with zero true removals) are applied; any rule removing a printed mark is reported
with the line ids and NOT applied until the track lead decides.

## Implement `greekocr/labelfix/reading.py: apply_constraints(reading) -> (reading, removed)`
Per-letter rules, deterministic, no lexicon, no Google:
- mark impossible on the letter itself: accent or circumflex on a consonant (ρ may carry only a breathing; initial ῥ), dialytika on a
  letter other than ι/υ, subscript under a letter other than α/η/ω, two breathings or two accents on one letter, breathing + dialytika
  on one letter;
- breathing outside its legal place (C1: word-initial vowel or second vowel of an initial diphthong; exceptions as encoded);
- word-level conflicts (C3 two accents without a following enclitic; C4 grave not on the final syllable; perispomeni on ε/ο or before the
  penult): remove the mark with the WEAKER detector evidence (state the evidence used: blob area, classifier probability, distance to
  the letter) and record the alternative; if the evidence ties, leave both and flag.
Return every removal with rule id, letter, slot, evidence. Keep `read_line` behaviour selectable (filtered by default for pages).

## Measure
On the 666 held-out lines and DEV, S6 detector: removals per rule; of those, how many print truth says were false marks (good) vs printed
marks (bad); mark precision/recall before → after the filter; the owner's notes (current files) and the implicit-approval changes S4→S6
(`docs/records/labelfix/spellcheck/owner_implicit_changes_S4_to_S6.json`, `scripts/labelfix/owner_implicit_changes.py`) before → after.

## Deliverables
Code + tests (all labelfix tests green, existing tests untouched; tests on Ἐμπρός ρ, πὄχει, βίος, αἶψα/αἲψα, κἀγώ crasis kept, Τυῤῥηνῶν
kept), `docs/records/labelfix/spellcheck/K1_REPORT.md`, last line:
`K1 RESULT: removed <n> marks (<a> false per print truth, <b> printed); applied rules …; held back …; mark P …→… R …→…; owner implicit false marks …→…`.

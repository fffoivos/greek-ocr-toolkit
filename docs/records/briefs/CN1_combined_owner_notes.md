# CN1 — Combined system vs S6 on the owner's notes (gpt-6.1-sol, xhigh)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck` (branch `opus/spellcheck`, head bacb4efd or later). No `.git` writes. Network OFF.
Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`. Mac CPU, cached alignments,
saved R1 predictions only (no inference, no training). ≤ 20 min. Measurement only.

## Question
SF1's strict owner-note instrument scores R1-A ALONE at 10/49 (current review notes) and 24/57 (current example notes) against S6's
35/49 and 33/57 (`docs/records/labelfix/spellcheck/SF1_REPORT.md`, `SF1_owner_summary.json`). R1 has no apostrophe/quote/segmentation/letter
heads, so the deciding comparison is the COMBINED system (recogniser letters + S6 presence, segmentation, apostrophes and quotes + R1-A
names where S6 and R1 agree on the mark kinds present, R1-A names shown with a HOLD flag where they do not + K1 print-preserving flags)
against S6, on the same strict instrument.

## Do
1. Produce the combined reading per owner line with `scripts/labelfix/owner_pages_build_combined.py`'s hash-bound reading path (SF1),
   R1 predictions `~/Projects/greek-ocr-toolkit-spellcheck-r1/artifacts/labelfix_r1/output_3678928/A/{heldout,owner}_predictions.jsonl`.
   Do not publish anything.
2. Score combined and S6 with the SF1 owner instruments (`s6_notes.py` / `r1_owner.py` strict mode) on all five note sets: current
   review v16 (49), current examples v10 (57), old 59 slots, old review 33, old examples 56. Report complete-note success AND the
   per-clause split: physical presence, naming, segmentation, punctuation/apostrophe/quote, letter identity; HOLD slots reported as their
   own outcome (not counted as fixed, not counted as wrong).
3. For every note where combined fails but S6 passes (and vice versa), one line: note, clause, S6 reading, combined reading, cause.
4. Also run `scripts/labelfix/box_regression.py` S6 → combined on the owner pages (boxes should be identical; report any difference).

## Deliverables
`docs/records/labelfix/spellcheck/CN1_REPORT.md`, `CN1_checks.jsonl`, last line:
`CN1 RESULT: complete notes combined vs S6 — review_v16 a/49 vs b/49; examples_v10 c/57 vs d/57; old59 …; old33 …; old56 …; clause split …; HOLD slots …; combined-worse notes <n>`.

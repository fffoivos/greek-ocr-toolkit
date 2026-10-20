# S3 — Detector iteration 2: recall back without losing S2's precision; owner notes pinned to his slot numbering (gpt-6.1-sol, xhigh)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck`, branch `opus/spellcheck`, head 4a3ace67). No `.git` writes; leave changes in the
working tree. Never touch other worktrees. Network OFF. Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`
with `PYTHONPATH=$PWD` (the venv's editable install points at another checkout). CPU only, NO CTC forward passes. Whole run ≤ 20 min.

## Binding rules (unchanged)
Transcribe what is PRINTED (print truth = `docs/records/labelfix/spellcheck/print_truth_s0.json` + agreement words; Wikisource is a reference only).
Evaluate the whole visible line per slot. The recogniser only LOCATES. Thresholds on DEV_BOOKS only; the 14 held-out books never tune anything.
Read `docs/records/labelfix/spellcheck/S2_REPORT.md` first: S2 is the baseline you must not regress on precision.

## What S2 left open (from its report and the owner's 33 notes in `docs/records/labelfix/spellcheck/owner_notes_db_20261016.jsonl`)
1. **Subscript recall 89.4% → 41.5%.** The S2 below-baseline rule is too strict. Recover recall while keeping speck/descender/next-line
   rejection: a subscript is a short stroke/wedge under the vowel body's left half, connected or not, possibly touching the body; specks are
   round, tiny relative to xh, or off-centre; ink cut by the crop's bottom edge is UNKNOWN (abstain), not absent. Required rule (relative to the
   vowel): a below-baseline blob is a subscript candidate when its centre is under the vowel body (±0.3 xh), its height is 0.25–0.9 xh, its
   darkness is within the line's ink band, and it is not part of a descender or a punctuation run; specks fail on size or darkness. Report
   subscript recall and speck rejection on the held-out set SIDE BY SIDE, and subscript P/R per book.
2. **Missed accents** (most owner notes: "missed 2 at 1", "missed accent at 17", "2 accents of 7 missed", "missed at 6, 8, 11, 20, 37, 39"):
   find why each is missed (window too narrow, mark merged with the letter, mark judged ascender by the neck rule, faint, neighbour
   assignment) and fix the cause. Owner-line recall fell 79.2% → 68.5% in S2: get it above the S1 level without losing precision.
3. **Owner slot numbering.** The owner annotated the sheet built by `scripts/labelfix/sheet_build.py` at commit 4e95489d with the detector at
   commit 153ff82e (slots = `role == 'letter'` components of `ink.analyse` at THAT commit, sorted by x0, 1-based). S2 recomputed slots with the
   new detector, so some expectations land on the wrong letter (e.g. "accent of 8 missed" on 02a3a2a6-p000046-l0014 mapped to β). Recover the
   v8 slot x-ranges from the old code (`git show 153ff82e:greekocr/labelfix/ink.py`, `git show 153ff82e:greekocr/glyphs/components.py`;
   import them from a temporary copy outside the package), store them in `owner_slot_expectations.jsonl` (`v8_x0`, `v8_x1`), map old→new slots
   by x-overlap, and judge every expectation on the mapped slot. On every sheet card show BOTH numbers when they differ (e.g. "slot 8 (v8) = 9
   (now)"), so the owner's 59 expectations are read on the slots he meant. Re-report S2 and S3 against the corrected mapping.
4. **Split letters / full-vowel windows** (owner case 384c3f89-p000096-l0004, printed ᾗσι): the η prints as two components, the vowel window
   covers only the left stroke, the perispomeni arch falls outside and is never counted. A vowel whose CTC span overlaps two adjacent letter
   components that together are ≤ 1.6 xh wide is one body; marks are credited over the union.
5. **Compound marks**: keep the 12 compound classes; report which have samples. Do NOT invent samples. (Harvesting more agreement samples
   needs recogniser alignments → separate task, not here.)

## Measure (same instruments as S2, before = S2, after = S3)
Held-out per-slot P/R/F1 by mark kind (accent, breathing, compound, subscript, apostrophe, dialytika); owner 33 lines per expectation
fixed/not fixed at the v8 x-ranges; ascender false-mark rate; the S1 engine re-scored against print (ACCEPT, HOLD, L2). Any metric that gets
worse than S2 must be named in the last line.

## Sheet
Rebuild `docs/records/labelfix/spellcheck/sheets/owner_iter_S3.html` with `scripts/labelfix/sheet_build.py` (format and notes script unchanged):
section 1 = the owner's 33 noted lines, each card with a row "your notes: k/n fixed" and per-slot status; section 2 = the fixed held-out sample
(`heldout_sample60.txt`) + every held-out line whose detection changed vs S2 (cap 140; list the rest). No line twice on the page (duplicate notes
boxes clash). Header: iteration id, the before→after numbers, and every regression in plain words.

## Tests
Subscript stroke vs speck vs cut-off ink; split-η union window; v8 slot mapping on a fixture; all existing tests green.

## Deliverables
Code, tests, `docs/records/labelfix/spellcheck/S3_REPORT.md`, the sheet, last line:
`S3 RESULT: held-out P …→… R …→…; subscript R …→…; owner expectations fixed …/… (v8 mapping; S2 was …/…); ascender false …; S1 ACCEPT vs print p=…; regressions: …`.

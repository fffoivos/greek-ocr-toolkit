# S5 — Detector iteration 4: capitals (gpt-6.1-sol, xhigh)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck`, branch `opus/spellcheck`, head = S4 commit afe67823 or later). No `.git`
writes; leave changes in the working tree. Network OFF. Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`
with `PYTHONPATH=$PWD`. CPU only, NO CTC forward passes (cached alignments). Whole run ≤ 20 min. Same rules as S4
(`docs/records/briefs/S4_detector_capitals_stacks.md`): our reading = letters from OUR recogniser + every mark from OUR detector; nothing from Google;
truth = print truth / the owner's notes; S4 is the baseline.

## The owner's diagnosis (16 Oct 2026, verbatim)
"main issue is not properly detecting chars as capitals which seems to cause 2 types of confusion: (1) about where the accents are (on the
side) and (2) what the height of letters are in that word"

## What the code does today
- The glyph pass (`greekocr/glyphs/components.py`) has roles `letter` / `large` and ONE x-height per line with a fitted baseline; there is no
  capital class. A capital and a tall lowercase letter (β δ ζ θ λ ξ φ ψ, also ϑ) look alike to it.
- S4 (`greekocr/labelfix/ink.py` `mark_evidence`, `capital_left_marks`, `_reserved_for_capital`) calls a letter a capital only when the
  recogniser character `isupper()` or the body is ≥ 1.25 xh and rises above the band. When the recogniser reads a capital as lowercase, or the
  letter→component owner is wrong, the side search never runs; when a tall lowercase letter passes the height rule, its top or neighbour ink can
  be read as a mark.
- Owner notes that look like this failure (resolve each against the slots the published pages draw: letter components sorted by x, numbered
  from 1): "missed at 1", "missed 2 accents at 1", "missed quote and 2 accents at 1", "missed at 2 (confusion due to capital theta at 1)",
  "22 delta is detected", "delta 13 detected", "random mark under lambda", "faint eta at 18 is detected as accent". Check the rest too.

## The task
1. **Capital detection from pixels.** Give every letter component a case class: lowercase body / lowercase ascender / lowercase descender /
   capital (and all-caps runs). Use pixel geometry relative to the line's baseline and x-height (top at cap height, bottom on the baseline,
   width, stroke, no descender, shape) plus the recogniser character as ONE signal; record disagreements between pixels and recogniser as a
   flag rather than silently trusting either. You may fit a small classifier on agreement labels (Google letter = recogniser letter, case
   included) from the C1 crops already decoded in S4 (`S4_training.json` inventory; ≤ 10,000 crops; never the 14 held-out books).
2. **Use it for mark position (confusion 1).** A detected capital gets the upper-left side search (S4 logic) and its marks are read at the
   capital's own height (cap-height band), not the x-height band. A tall lowercase letter never gets the side search, and its own ascender ink
   is never a mark.
3. **Use it for letter height (confusion 2).** Capitals (and ascenders/descenders) must not set the height reference of the word they sit in;
   the word's x-height band and the mark zone above it come from its lowercase bodies. A line or word set in capitals (headings, small caps)
   gets its own band. Report how the band changes on the owner's lines.
4. **Breathing/accent naming beside capitals.** On the published pages the side marks are now found but often misnamed (print Ἦ read Ἤ, Ὅ read
   Ὄ, ἂ read ἆ). Measure naming accuracy at capitals separately and improve it if the case-aware geometry allows; do not regress elsewhere.

## Measure (before = S4, after = S5)
- Capital detection itself: precision/recall of the capital class on held-out letters (truth = print-truth letters where available, else
  Google = recogniser agreement), and how often pixels and recogniser disagree.
- Recall/precision of marks at capitals; naming accuracy at capitals; ascender false-mark rate (δ θ λ β tops read as marks); held-out per-slot
  P/R/F1 by mark kind; compound recall; DEV dialytika and compound precision (S4 regressions).
- **All owner notes, as machine checks, before → after:** the 59 earlier expectations, and ALL 56 notes in
  `docs/records/labelfix/spellcheck/owner_notes_examples_20261016.jsonl` (S4 scored only the first 33; extend `owner_examples_expectations.jsonl`).
  An empty note = the line was judged correct: no new errors there. Also the 33 notes on the review page
  (`docs/records/labelfix/spellcheck/owner_notes_db_20261016.jsonl`; note text only — its `printed` field is unedited prefill, never truth).
- List the owner lines whose reading (`reading.read_line`) changed, old → new.

## Coordinator conditions (binding; do them in this order)
0. **Baseline first.** Before changing any code, score S4 (afe67823 code + `markshape_model_S4.json`) on ALL 56 example notes (the 23 S4
   left unscored included) and the 33 review-page notes, so every after-number has an S4 before-number.
1. **Capital ground truth.** Recogniser uppercase is NOT the truth. Truth for the capital class = the case of the Google letter on slots
   where Google and our recogniser agree on the letter (ignoring marks); state how many held-out slots that leaves and how many capitals.
   Report capital P/R against it, plus the pixel-vs-recogniser disagreement rate.
2. **S4 regressions are checks, not footnotes.** Each must be recovered or explained with evidence: DEV compound precision 93.0→87.1,
   psili+circumflex precision 76.9→71.4, circumflex recall 96.7→89.1, dialytika (state the stratum size; if < 20 slots, add dialytika
   slots from the C1 agreement set so the number means something). Test this hypothesis FIRST, before touching the detector: the S4
   retrain set (C1 agreement crops) under-represents dialytika and compounds relative to DEV — print per-class counts (DEV vs C1 vs total)
   and, if confirmed, rebalance the retrain.
3. **One-line cause each** for the two lost expectations (602cc72e-p000155-l0009:11, 8b6b0de9-p000008-l0001:12) and the new error on an
   empty-note line (384c3f89-p000182-l0031 slot 8).
4. The report keeps S4's held-out table (666 lines, 14 books) row for row, plus new rows: capital detection P, capital detection R,
   marks-at-capitals naming accuracy.

## Deliverables
Code, tests (all labelfix tests green; add tests on 177b717d-p000013-l0009 "Ἦταν", 51fe7386-p000024-l0015 "Ὁ Ὅλυμπος … Ὅσσα",
02a3a2a6-p000318-l0017 "Θὰ", and one δ/λ ascender case), `docs/records/labelfix/spellcheck/S5_REPORT.md`, last line:
`S5 RESULT: capital detection P …/R …; marks at capitals R …→… naming …→…; held-out P …→… R …→…; ascender false …→…; owner notes …/56 + …/59 (S4 …/56, 46/59); regressions: …`.
Do not build or publish the owner pages (the track lead does).

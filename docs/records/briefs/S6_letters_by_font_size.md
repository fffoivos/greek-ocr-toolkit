# S6 — Detector iteration 5: letters by font size, accents merged with letters (gpt-6.1-sol, xhigh)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck`, branch `opus/spellcheck`, head = the S5 commit eed80de9). No `.git` writes.
Network OFF. Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python` with `PYTHONPATH=$PWD`. CPU only, NO CTC
forward passes (cached alignments). Same rules as S4/S5: our reading = letters from OUR recogniser + every mark from OUR detector; nothing from
Google; truth = print truth + the owner's notes; BOTH S4 (afe67823) and S5 (eed80de9) are baselines;
report every regression against each.

## The owner's rules (16 Oct 2026, verbatim)
1. "if you are detecting letters with no gap heuristic you need to reconsider because this causes problems / you need to consider font size"
2. "there are 2 cases where the accents are inked with the chars and you need to be careful to not cut into the char because it will be
   classified badly" — his two cases are on the review page:
   - 602cc72e-p000155-l0009: "care is required to not detect within the height of letters since the ink of accents and chars are merged
     and they might look like more than one where there is only once."
   - 602cc72e-p000113-l0030: "make sure the accent boxes are above mid-top font height"

## Where S5 left things (docs/records/labelfix/spellcheck/S5_REPORT.md)
- Capital class works only with the recogniser prior: P/R 95.6/98.7, but pixel-only 83.2/45.3. Rule 1 asks for font-size geometry from the
  pixels; make the pixel side carry the decision where it can and report pixel-only P/R again.
- Marks barely moved (held-out P 93.5→93.7, R 91.9→91.6) and DEV regressed: compound P 87.1→81.0, compound R 88.4→83.3, breathing R
  90.8→86.9, dialytika 0 (3 DEV slots). Owner notes 26/56 (S4 27/56), 45/59 (S4 46/59). S6 must recover these or explain each with
  evidence; if an S5 change causes them (e.g. word bands moving the mark zone), revert that part.
- S5's own reading of 602cc72e-p000155-l0009 lost a mark (ἶερεύς → ιερεύς): an owner merged-accent case, see rule 2.

## What his notes on the S4 pages show
Current note files (pulled 22:15 from the published pages built with the S4 detector; slots = letter components sorted by x, numbered from
1 on those pages): `docs/records/labelfix/spellcheck/owner_notes_review_v16_20261016.jsonl` (49 review-page notes) and
`owner_notes_examples_v10_20261016.jsonl` (57). These SUPERSEDE the older note files for the after-score (several earlier notes are now
empty = judged correct on S4); score both old and new.
- **Fused letters** (touching letters = one connected component, so a component holds 2–3 recogniser characters; S4 marks such a slot
  `localisation_unknown` and gives it NO marks): "fused letters at 33 and missed", "3 letters fused at 15 and missed accent there",
  "2 letters fused at 5 and misesd accent there", "τυ merged and accent missed at second letter of 20", "15 is 2 letters and accent missed
  there", "fused letters at 4 and 6, missed their accents", "fused letters at 3/22/26 …", "3 fused letters at 12/7 and missed accent".
- **Split letters**: "split eat at 1-2 and missed 2 accents" (one η drawn as two components).
- **Accents merged with letters**: the two cases above; accent ink touching the letter must be separated ABOVE the letter body, never by
  cutting into the letter.

## Coordinator directions (binding, 16 Oct 22:15)
- **Division of labour.** This track owns DETECTION and SEGMENTATION only: where a mark is, which letter it belongs to, fused/split
  letters, attached accents, capitals from pixels. NAMING belongs to the separate R1 mark reader. **No mark-classifier retrain** (keep
  `markshape_model_S4.json` and the S5 case model as they are). Report naming numbers, but do not optimise for them.
- **S6 is judged on** presence/location recall and precision (a mark of any kind found at the right letter, and no mark where none is
  printed), on fused vs clean slots, and on recovering the S5 DEV presence regressions (breathing/compound recall) or reverting the S5 part
  that causes them.
- **Capitals: two rows in every table**, combined (pixels + recogniser prior) and pixel-only, P and R each. State which decision drives the
  side-mark search and the word's letter height. If the combined decision is used, give the 753 slots where pixels and recogniser disagree
  their own precision line (the owner's cases live there).

## The task
1. **Letters by font size, not by gaps.** Estimate the line's font size from pixels (x-height of lowercase bodies, robust to capitals and
   ascenders; use S5's case classes). Assign each recogniser character a letter region from its CTC span AND the font size: a component
   wider than ~1.3 expected letter widths and covered by ≥ 2 recogniser characters is split at the span boundaries (refined to the lowest
   ink-column point within ±0.25 letter width); a component narrower than expected and covered by one character joins its neighbour piece
   (S4 union rule). Every recogniser vowel/ρ ends with exactly one letter region, so no slot is left without marks because of fusion.
2. **Mark zone by font size.** Accent/breathing boxes lie above the letter's mid-to-top font height: for a lowercase body, above the
   x-height line (meanline) minus a small tolerance; for a capital or ascender, beside/above per S5. Ink below that line belongs to the
   letter. When an accent's ink is joined to the letter, separate it at the meanline (or the capital's top) and keep the letter body intact;
   never take a slice from inside the letter's height as a mark, and never count one merged accent as two marks.
3. **Subscript zone** symmetric: below the baseline only.

## Measure (before = S5, after = S6)
- Fused slots on the 666 held-out lines: count; mark recall/precision on fused vs clean slots.
- Merged-accent slots (mark ink connected to the letter): count; recall/precision; how often a mark box reaches below the meanline (should be 0).
- The S4/S5 held-out table row for row; owner checks for ALL notes as machine checks before → after, including the new review-page notes
  (empty note = judged correct: no new errors there; no note document = unreviewed).
- List the owner lines whose reading changed, old → new.

## Deliverables
Code, tests (all labelfix tests green; add tests on 602cc72e-p000155-l0009, 602cc72e-p000113-l0030, 384c3f89-p000091-l0039 "τυ", one
3-letter fusion e.g. 8b6b0de9-p000007-l0030, and 384c3f89-p000142-l0002 split η), `docs/records/labelfix/spellcheck/S6_REPORT.md`, last line:
`S6 RESULT: presence P …→… R …→… (S4 …, S5 …); capitals combined P/R …, pixel-only P/R …, disagreement-slot P …; fused slots <n>, fused R …→… P …→…; merged-accent R …→…; marks below meanline …→0; held-out P …→… R …→…; owner notes …; regressions: …`.
Do not build or publish the owner pages.

# S7 — Detector presence via the toolkit's own geometry (gpt-6.1-sol, xhigh)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck` (branch `opus/spellcheck`, head at launch, after M2). No `.git` writes. Network OFF.
Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`. Mac CPU, cached alignments,
no CTC passes, no retraining (no mark-classifier or case-model retrain), ≤ 30 min. Same rules as S4–S6 and SF1: our reading = letters
from our recogniser + every mark from our detector; nothing from Google; print-preserving default; S6 (SF1 state) is the baseline.

## Why
ASTRA-SC1 (`docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1_review_1.md`, Question 1 table and M06) found that the detector
re-implements geometry the toolkit already has, owner-validated: `greekocr/glyphs/letters.py` (owner rule 8 Oct: letters = ink pieces in the
per-column middle region, connected AFTER restricting to the band; merged blobs split at thin bridges, otherwise "unresolved"; parent
label sets kept) and the guide machinery (`greekocr/glyphs/components.py` band fitting, `greekocr/glyphs/baseline.py` four guides per x,
`greekocr/pages/font.py` all-capital height / tall-body evidence). CN1 (`docs/records/labelfix/spellcheck/CN1_REPORT.md`) shows the combined
system's whole owner-note gap is 80 slots where the detector's PRESENCE (which mark kinds are present) disagrees with R1, and the
detector is the weaker side there (R1 right in 90% of known disagreements); pixel-only capital recall is 46.9%.

## Substitutions (each one qualified separately against S6 on the same tables BEFORE it replaces anything)
- **S1 — letters:** physical letter regions from `glyphs.letters` (middle-region pieces, parent-label sets, split-or-unresolved), then map
  the cached recogniser letters onto them. Where the recogniser count and the physical pieces disagree, keep an explicit ambiguity state
  (never let the CTC count become physical truth; never drop a fused letter from evaluation).
- **S2 — guides:** one shared guide object per line: per-x meanline, baseline, ascender and descender lines with provenance
  (measured / borrowed / fallback), curvature kept; mark zones and the capital side zone clipped per column. Keep S6's proven
  lowercase-body height repair as a qualified correction (the review measured toolkit x-height 48 vs S6 31 on 602cc72e-p000155-l0009 and
  40 vs 31 on 602cc72e-p000113-l0030, with S6 nearer the visible body): decide per line from evidence, report which one won.
- **S3 — cut masks:** propagate crop validity / directional cut masks so "mark cut off by the crop" is UNSEEN, not absent.
For capitals: use S2's ascender/cap guides and `pages.font` all-capital evidence as features for the PIXEL side of the case decision
(no retraining: geometric evidence only); report pixel-only and combined capital P/R separately as before.

## Measure (before = S6/SF1, after = each substitution alone, then the accepted set together)
- The 80 detector/R1 mark-KIND disagreements on the owner lines (CN1 `hold_slot` records): how many disappear, and who was right
  (print truth / owner notes) where they remain.
- Pixel-only capital P/R (truth = the S5 agreement stratum, 1,189 capitals) and the 753 disagreement-slot precision.
- Held-out presence P/R (S6 table), fused-slot recall, merged-accent cohort recall, ascender false marks, marks below the per-column
  meanline (now against S2's guides, not self-generated bounds).
- Owner checks with the strict SF1 instruments on all note sets; implicit-approval box regression S6 → S7 with
  `scripts/labelfix/box_regression.py` (reviewed lines: lost/added/moved, by status).
- Then re-run CN1 (combined system) with the S7 detector: complete notes, clause split, HOLD slots.
- **New sources (M2, `docs/records/labelfix/spellcheck/M2_REPORT.md`):** re-run `scripts/labelfix/m2_run.py`/`m2_score.py` with the S7 detector on
  the same 473 cached cards: PRESENCE HOLD lines 77.6% → …, Google mark errors corrected 25/77 → …, capital-breathing pairs 1/19 → …,
  new changes on marks-correct cards 30 → …. Add a scope rule first: the polytonic checker does not run on monotonic lines
  (gazette_modern: 2 of 3 wrong spot checks were monotonic accents read as breathings); decide monotonic from the line's script class /
  pixels, never from Google, and report how many lines it excludes.

## Deliverables
Code + tests (all labelfix tests green, none weakened), `docs/records/labelfix/spellcheck/S7_REPORT.md` with one qualification table per
substitution (accepted / rejected with the numbers), last line:
`S7 RESULT: accepted <S1/S2/S3>; kind-disagreements 80→…; pixel-only capitals P/R …→…; presence P/R …→…; fused R …→…; owner notes review_v16 …→…, examples_v10 …→…; implicit box changes lost … added …; CN1 combined review_v16 26→…, examples_v10 25→…; M2 HOLD lines 77.6%→…, corrected 25/77→…; regressions: …`.

# S8b — One bounded detector iteration on the training-wave fonts (gpt-6.1-sol, xhigh, network OFF)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-s8`, branch `opus/spellcheck-s8`). No `.git` writes; other worktrees
read-only. Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`. Mac CPU; saved evidence
only (no CTC/R1 inference). **Existing tools only** — the toolkit's own font/line tools (`greekocr/glyphs/*` baseline/meanline/x-height
guides, `greekocr/labelfix/{ink,segmentation,case,reading,markshape}.py`, recut/ownership); no new model, no learned detector. **Do not
change the release gate** (`release_gate.py`, `text.py` composer semantics) or the reader. One iteration: one coherent set of detector
changes, measured once; no tuning loop on the judging half.

## Why (coordinator, 17 Oct; S8a6 `docs/records/labelfix/spellcheck/S8a6_DEV_TRUTH.md`)
R1-A reads marks at ~99% presence on every training wave; the detector is the bottleneck: presence P/R parliament 82.6/68.2 (breathing
58/52), vouli 87.0/95.2, round1/round2/mixed ~97/90. Under SF6 the detector is a required second absence signal, so its recall limits the
release. S8a7 (masked crops, `docs/records/labelfix/spellcheck/S8a7_MASKED_DETECTOR.md`) gives the masked baseline: **start from masked crops wherever
the mask exists** (round1/round2/mixed/vouli); parliament unmasked.

## Targets, in this order
1. **Missing above-mark presence** (detector says no mark where the print has one) — every wave, worst on parliament.
2. **False above presence** on vouli and parliament (specks/foreign ink/letter parts read as marks).
3. **Breathing naming/shape** (extra/missing breathing vs accent; breathing family P/R).
Read the S8a6 failure examples (ids per wave) and the S8a baseline evidence; fix causes in the detector's geometry/segmentation/thresholds
using font-size-relative quantities (x-height, meanline, cap height — owner rule: consider font size; no gap heuristics; never cut into a
letter; accent boxes above mid-top font height).

## Overfitting guard
Split the adjudicated DEV **by document**, seeded `S8b-split-20261017`, stratified by wave, into TUNE (≈ 50%) and JUDGE (≈ 50%). Look only at
TUNE while developing; report JUDGE once at the end, plus TUNE and ALL. The S8a6 weights apply within each half.

## Regression checks (standard, owner rule)
- The 666 held-out instrument (Wikisource): detector presence/marks and the frozen-gate tables before/after — no regression beyond noise.
- **Box regression vs S6** on the owner pages (`scripts/labelfix/box_regression.py`): count boxes added/removed/moved per line; any removal on
  an owner-approved slot is listed.
- Implicit-approval regression on owner pages (missed/false vs the owner-approved state).

## Report
`docs/records/labelfix/spellcheck/S8b_REPORT.md`: the S8a6 table (detector presence P/R per wave and per family, with intervals) before (S6 on masked
where available) / after, on JUDGE, TUNE and ALL; loc_unknown / seg_uncertain / clipping rates per wave; held-out and regression tables; what
changed and why (code diff summary). Include a **Plan B section** (coordinator): if parliament recall stays below ~90%, the detector's
presence role passes to a second, independently built pixel reader (different architecture or input, not a reseed of R1), with the two-signal
rule reader-vs-reader and the detector kept for apostrophes, segmentation and clipping — state what it would need (data, labels, training
budget, how independence is shown, how it would be validated on this DEV). Last line:
`S8b RESULT: JUDGE detector presence P/R parliament <..>/<..> (was 82.6/68.2), vouli <..>, round1 <..>, round2 <..>, mixed <..>; breathing P/R parliament <..>; held-out regression <none|…>; box regression <..>; Plan B needed <yes|no>`.

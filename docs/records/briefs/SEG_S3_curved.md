# SEG step 3: curved lines are measured along the base curve (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`. The lead commits. HEAD contains step 2
(0.9-s2, `docs/records/harvest/seg_steps/s2/`). Use the new output directory `docs/records/harvest/seg_steps/s3/`. Same untouchables as step 2:
`seg_census/package/`, `seg09/`, and the untracked census02 evidence (read only).

**Read first:**
- `~/Projects/greek-ocr-toolkit-secondary/docs/CONTEXT_20261019_segmentation_and_secondary.md`. A tool is EXACTLY the owner's
  rules; never add a guard, test, threshold or heuristic; extras are diagnostics only.
- `docs/records/harvest/seg_steps/s2/REPORT.md` and `s1/REPORT.md`. Reuse their replay and scoring workflow unchanged.
- `sol-recut segeval1/gate/DESIGN.md` and `gate2/HANDOFF.md` (read only), for the row frame, `skew_line`, `text_lines` and the 0.6
  `tight_box` pixel-cell method.

## The single change (owner, 19 Oct), with the lead's ruling on how to measure it

This is version **0.9-s3**, built on 0.9-s2. Owner:
- the long side = the arc length of the detected main-row base curve over its support;
- the short side = the perpendicular ascender–descender distance;
- on straight lines it must equal the 0.8 box to the digit.

**Lead ruling (exact construction).** Measure the main row's ink in the frame of its base curve. Use the base curve the existing
detector already provides for the main row: the same `text_lines` / `skew_line` geometry. Do NOT fit a new curve, smooth it or add
parameters. For every main-row TEXT_ROLES ink pixel (the same pixels the 0.8 de-skewed box uses):
- **s** = arc-length position, along the base curve, of the pixel's foot point;
- **n** = signed perpendicular distance from the curve.

Then:
- long side = the s-extent of that ink;
- short side = the n-extent, by the same 0.6 `tight_box` pixel-cell method on (s, n) instead of the de-skewed (x', y').

On a straight base curve, (s, n) is exactly the de-skew rotation, so the box equals the 0.8/0.9-s2 box. Rule 2 normalises the long
side by this short side through the unchanged predictor; rule 3's padding uses this short side as the row-frame height. Nothing
else changes.

If the detector's base curve is not available as a per-x curve for some rows, report how it IS represented and use exactly that.
If a pixel's foot point is ambiguous (more than one nearest point on the curve), take the first in curve order and count the cases
as a diagnostic.

## Do

1. **Implement, with tests:**
   - a synthetic straight line at 0°, 1.2° and −3° reproduces the de-skewed box exactly;
   - a synthetic circular arc of known radius gives the analytic arc length within 1 px;
   - h ≤ w and turned (step 2) crops both pass through.
2. **Straight-line identity.** This is a correctness check, not a rule. On the 150 + 888 + 250, for every row whose detector base
   curve is a straight line (single angle), the 0.9-s3 long side, short side, ratio and padding must equal 0.9-s2 to the digit.
   - Report n/n.
   - If ANY straight row differs, that is a bug: fix it before the replay; never accept a tolerance.
3. **Witness `ia_poly1850--df8f2267db2b7275--s025-l0037`** (owner KEEP). 0.8 shows a 41 px baseline sag and a single-angle box
   92 px tall vs a 57 px line. Report 0.9-s2 vs 0.9-s3: long side, short side, ratio, padding and verdict. Give an overlay PNG
   with the base curve, the old box and the unrolled box (s, n) under `s3/overlays/`.
4. **Curvature diagnostic:** the distribution of the base-curve deviation from its chord over all replay rows, and the rows whose
   measurement changed, with the size of the change.
5. **Replay** 0.9-s3 on the **150**, the **888** and the **250**, scored exactly as in steps 1–2:
   - the 150: FP/FN/UNC;
   - the 888: rated agreement /135;
   - owner marks: /235, latest mark wins.

   Show the columns 0.8 | 0.9-s1 | 0.9-s2 | 0.9-s3 side by side, plus flip tables for s2 → s3: every changed verdict with the
   owner label or mark and the curve deviation.
6. **Readback:** every straight row replays byte-identical to step 2. Include a scope guard listing the changed source files.
7. **Report** in `docs/records/harvest/seg_steps/s3/REPORT.md`, plus `flips.jsonl`, `curvature.jsonl`, `summary.json` and a receipt.
   Update `tool_versions.json` as before.

**Last line:** `SEG S3 READY: straight identity <n>/<n>; witness l0037 ratio <s2> → <s3> (<verdict s2 → s3>); curved rows changed <n>; 150 FP/FN/UNC <s2> → <s3>; 888 rated agree <n> → <n>/135; owner marks agree <n> → <n>/235; flips <n>; tests <n> passed`

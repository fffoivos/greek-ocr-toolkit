# SEG step 3b: the curved-line box stays inside the ink (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`. HEAD contains 0.9-s4, content gate 0.3 and the
gate re-report (`docs/records/harvest/seg_steps/gate_rereport/`). The new output directory is `docs/records/harvest/seg_steps/s3b/`. Same
untouchables as before: `seg_census/package/`, `seg09/` and the census02 evidence (read only).

**Read first:**
- `~/Projects/greek-ocr-toolkit-secondary/docs/CONTEXT_20261019_segmentation_and_secondary.md`. A tool is EXACTLY the owner's
  rules; never add a guard, threshold or heuristic; extras are diagnostics only.
- `docs/records/briefs/SEG_S3_curved.md` (the lead's (s, n) ruling) and `s3/REPORT.md`, `s4/REPORT.md`, `gate_rereport/REPORT.md`.
- The (s, n) implementation from step 3 in `crop-tools.py` and `components.py` (`Band.curve_is_straight`).

## The defect (owner, 19 Oct)

Witness: `ia_greek_latin--d94cfff6c5bd6428--s004-l0037`, owner "should not have been dropped; the box is wrong".
- 21 chars, bold wide Latin.
- The step-3 flip went KEEP → DROP, "Too much OCR output".
- 0.8: ratio 1.23, KEEP.

Coordinator's render of the s3 overlay:
- the crop is 523×53 px, with ink support x ∈ [22, 502];
- the detector's degree-2 base and ascender curves bend sharply at the left end;
- the unrolled box extends below the crop under "Σ.".

Saved 0.9-s4 `row_frame`:
- `height` 79.40 on a 53 px crop;
- `length` 504.05;
- `sn_box` [21.75, −65.94, 525.80, 13.46];
- `angle_deg` −3.09.

The 0.9-s2 de-skewed frame gave 62 px, also taller than the crop; the upright box is 49 px.

A short side larger than the crop is a measurement error, not a property of the line.

## The owner's rule (unchanged)

- **Long side** = the arc length of the detected main-row base curve over the main row's ink support.
- **Short side** = the perpendicular ascender-to-descender distance sampled along that support, never beyond the ink.
- On straight lines this must equal the 0.8 / 0.9-s2 box to the digit.

## Do

1. **Diagnose the witness first, with numbers and an overlay PNG**, for each candidate cause:
   - (a) the curve evaluated or extrapolated outside the ink support: foot points or s beyond [22, 502], the s-extent running to
     525.8 on a 523 px crop;
   - (b) normals tilted by the sharp end bend, so ordinary ink projects to a large |n|. Measure the n-extent contributed by
     pixels whose foot point lies in the bend;
   - (c) the extreme corners or outliers of the ink taken instead of the ascender-to-descender distance along the support;
   - (d) the lower "Σ." treated as curvature by the detector's fit. Is the bend inside the support present in the detector's
     saved curve itself?

   Also explain the 62 px of the 0.9-s2 de-skewed frame on the same crop.
2. **Fix within the rule, using only the detector's existing curves.** Fit no new curve, add no smoothing and no new parameter,
   and change no verdict rule.
   - The base curve is used only over the main row's ink support: no extrapolation, and every foot point and arc length lies
     within that support.
   - The short side measures the ascender-to-descender extent along that support, by the same 0.6 `tight_box` pixel-cell method
     on (s, n), with every pixel's foot point inside the support.
   - If the diagnosis shows that no construction within these limits removes the error, because the cause is the detector's
     own curve inside the support, implement nothing for that cause. Report it with the numbers and stop that part, so the lead
     can rule.
3. **Diagnostic flag only.** Add `short_side_exceeds_crop_height` (true/false, plus both values) to every replay record, in the
   processed crop frame. Add no rule on it.
4. **Tests:**
   - the step-3 synthetic straight lines (0°, 1.2°, −3°) and the circular arc still pass;
   - a new synthetic case: a straight ink line whose detector curve bends beyond the ink at one end. The short side must equal
     the straight-line value, and the long side the support length, within 1 px;
   - non-curved rows are byte-identical to 0.9-s4.
5. **Straight identity:** every straight row (`curve_is_straight`) replays byte-identical to 0.9-s4. Report n/n; any difference
   is a bug.
6. **Replay** this version, **0.9-s3b**, built on 0.9-s4, on:
   - the 94 curved rows;
   - the 150, 888 and 250;
   - the small rows, which are unchanged unless they use the curved frame. Say which.

   **Scoring:**
   - Score as in `gate_rereport` (gate-failed rows removed), plus the unfiltered numbers for continuity.
   - Columns: 0.8 | 0.9-s4 | 0.9-s3b. Report the 150 FP/FN/UNC, the 888 /135 and the owner marks /N.
   - Flip table s4 → s3b: id, owner mark or label, before → after for long side, short side, ratio and verdict, and the flag.
   - Report how many rows had `short_side_exceeds_crop_height` true under s4, and how many under s3b.
7. **Witness result:** its 0.9-s3b long side, short side, ratio and verdict next to 0.8 (1.23 KEEP) and 0.9-s4. Give an overlay
   with the curve over the support and the new (s, n) box under `s3b/overlays/`.
8. **Versions and report:**
   - update `build_filter_versions.py` and `tool_versions.json` with the segmentation iteration "curve measurement bounded to the
     main-row ink support";
   - include a scope guard listing the changed files;
   - write `s3b/REPORT.md`, `flips.jsonl`, `replay.jsonl`, `summary.json` and a receipt.

**Last line:** `SEG S3b READY: cause <a|b|c|d|combo>; witness l0037 short <s4> → <s3b>, ratio <s4> → <s3b> (<verdict>); straight identity <n>/<n>; exceeds-crop flag s4 <n> → s3b <n>; curved changed <n>; 150 FP/FN/UNC <s4> → <s3b>; 888 <n> → <n>/135; marks <n> → <n>/<N>; tests <n> passed`

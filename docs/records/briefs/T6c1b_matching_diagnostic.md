# T6c1b: line-curve matching diagnostic on a two-column parliament page (gpt-6.1-sol, xhigh, network OFF, nice, ≤ 60 min)

This continues T6c1 in this worktree (`sol/recut-v1`).

**Where you can write.** Only inside this worktree, under `docs/records/harvest/recut_v1/v2_pilot/diag/`. You **can read** the pilot outputs in `~/Projects/collect-v3-data/v2_masked/pilot/` (records, curves, sample.json), but you **cannot write there**.

**Run everything at nice ≥ 15, one worker.** A live collection shares the CPU.

## Background
I executed the T6c1 pilot. It stopped on page 1: parliament `37e22f57-p000005`, 40.1 MP.
- Time: 22.7 s.
- **Matching: 48 failures among 87 lines** (36 ambiguous, 12 unmatched), from 89 detector curves.
- RSS: 4.8 GB.

The hypothesis is that parliament proceedings are two-column. The existing T6a2 matcher makes a curve eligible on vertical position, so in a two-column page the same row height exists in both columns.

## Do
1. **Contact sheet.** Make one for all 48 failures on this page. For each failure show:
   - the crop_bbox;
   - every eligible curve, drawn with its horizontal extent;
   - the failure kind.

   Also take **one vouli page** from the pilot sample (`sample.json`, the first vouli page) and run the same matcher on it for comparison. **If the vouli page has failures too, sheet them as well.**
2. **Eligibility restriction.** Add one restriction to the existing matcher:
   - a curve is eligible only if its horizontal extent **overlaps the line's crop_bbox horizontally** (state the overlap threshold, e.g. ≥50% of the crop width);
   - keep the existing vertical criterion and scoring unchanged;
   - add **no new scoring rule**;
   - make it opt-in, so T6a2 defaults stay unchanged.

   Report **matched / ambiguous / unmatched, before → after**, for both pages.
3. **The 12 unmatched lines** (and any left after step 2). Classify each against the 40 MP raster and the detector output:
   - **detector merge:** two printed lines in one curve, or a curve spanning both columns;
   - **detector miss:** no curve over the line's ink;
   - **crop_bbox problem:** the v2 crop is off its line;
   - other.

   Show the evidence in the sheet.
4. **Check that T6a2 is unchanged.** With the restriction on, the T6a2 F2 dev pages must give **identical matches to before**. Report counts and any differences.

## Hand-off
Write `docs/records/harvest/recut_v1/v2_pilot/diag/DIAG.md` with the before/after table, the unmatched classification, the contact sheets and the T6a2-unchanged check. Commit with the guarded helper (it excludes ignored paths).

The last line must be exactly:
`T6c1b: done | parliament before/after ambiguous: <a>/<b> unmatched: <c>/<d> | vouli before/after: <e>/<f> | unmatched causes: <merge n, miss n, crop n, other n> | T6a2 unchanged: <yes|no> | overlap threshold: <x>`

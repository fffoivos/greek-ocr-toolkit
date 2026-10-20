# Notes for later segmentation steps

- **For step 2** (19 Oct 15:27, from the Small segment analysis session). About 1,566 numeric 1–2-char crops are only
  slightly taller than wide (e.g. "1" at 22×24). The owner's rule (height > width → turn 90° right) will turn them.
  - Apply the rule exactly as given.
  - Report these crops in the step-2 replay as a diagnostic: count, verdict before/after, and examples on the sheet, so the owner can
    see the effect.
  - Do NOT add a threshold.

## Small-segment Q1 (19 Oct 15:35, from the Small segment analysis session)

Report: `sol-recut segeval1/small_segments/q1/Q1_TABLES.md`.

**Recommended small** = Google chars ≤ 8 AND A ≤ 6, where A = crop long side / short side. It is rotation-invariant.
- Census inside: 59,002 rows (10.0%), all W1/W2.
- Owner-judged lines inside: 152 good / 19 bad; outside: 126 good / 67 bad.
- Box failure under 0.5: 18.0% inside vs 2.0% outside.
- Alternatives rejected: chars ≤ 8 alone (164/45); chars ≤ 5 & A ≤ 4; A alone; L ≤ 100 px (cleanest 143/11, but
  resolution-dependent); L/x-height; the SEG-CELLS px cut.

**For step 2:** 2,540 crops with 1–2 chars are taller than wide, but only 248 have h > 2w. The owner marked good 7 single "1" cells of
this kind; 0.5 dropped them all.

**For step 5:** 14 owner-good false rejects with ≤10 chars stay outside "small" (letter-spaced caps, leader dots, wide-set digits).
They belong to the band population.

**Also:** 4 huge few-char blobs inside (e.g. '*****' 439×427). The all-ink box makes them "too much", matching the owner's DROP.

## Owner's first marks on the small-segment typology sheet (19 Oct, from the Small segment analysis session)

- **The marks:** 185 cards marked, 177 KEEP / 8 DROP, all from the word + caps_display groups (185 of the 196 there). On the
  legitimate text the split is 164 KEEP / 8 DROP.
- **Sol's fault calls:** all 13 crops Sol called clipped/extra are owner KEEP, so the 10% segmentation-fault estimate is likely
  overstated for this part.
- **The 8 DROPs:**
  - 4 are noted "wrong Google output";
  - 4 have text=wrong.

  These are label faults, not box faults.
- **0.5 against the owner:** the 0.5 tool drops, or leaves uncertain, 48 crops the owner keeps. This is step-4/step-5 evidence.
- The definition is still on hold, pending the owner's decision.


## Filter frozen (19 Oct); known limitation: curved short side larger than the crop

**The freeze.** The owner accepted 0.9-s4 plus content gate 0.3 (commits 875dc98bd, caa32d5a0, b5c5d06ba) as good enough. There
will be no further segmentation steps.

**Known limitation:** `ia_greek_latin--d94cfff6c5bd6428--s004-l0037`.
- **The fault:** the s3 unrolled box is 79 px tall on a 53 px crop, because the end bend of the base curve is used outside the
  ink support or with tilted normals. The witness flipped from KEEP to DROP.
- **The fix idea:** bound the arc length and the perpendicular extent to the ink support, and flag
  `short_side_exceeds_crop_height`. See `s3/REPORT.md` and `docs/records/briefs/SEG_S3b_curve_support.md`, which was not run.

**Re-report without gate-failed rows:** `gate_rereport/REPORT.md` (a674a35d2).

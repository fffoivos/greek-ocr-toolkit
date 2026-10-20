# N1-TS3: fold in r3, geometry-audit sheet, owner sheet under the size cap (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Continue N1-TS phase 2 (`N1T_REPORT.md`). Same worktree and constraints. The lead is running r3 on `n1t3` (6 contexts) now. Run this
brief after those answers exist; if an r3 context has no answers yet, stop and report.

**Do.**
1. **Fold r3 into the combiner** as a third independent read: its own gate, scan and provenance checks.
   - Two agreeing reads out of the three valid ones → truth candidate.
   - Otherwise lead_review.
   - Lead rulings (`lead_t.jsonl`) override, and the mirrored lekythos row stays `suspect:mirrored` with no decision
     (`N1T_LEAD_RAISED.md`).
   - Report counts before and after r3, by reason.
2. **Geometry-audit sheet.** For the 13 geometry-only audit slots where a reader saw something other than "nothing", build a
   contact sheet `n1_review/t_lead/geo_audit.png` (marked zoom, line, both reads, the geometry record), plus 4 audit slots where the
   readers agreed "nothing" as anchors. Write `geo_audit_template.jsonl`.
3. **Every newly raised slot.** Any slot that gets a raised-dot truth candidate from r3 and is not already lead-ruled goes on a sheet
   `n1_review/t_lead/raised_r3.png`, laid out like the raised sheets. Write a template.
4. **Owner sheet v2 rebuild,** same file path, **≤ 14 MB**. Cut the size, in this order:
   - (a) line crops as grey PNG at their native size, never upscaled;
   - (b) zooms as JPEG quality 85, but only for slots that have a mark;
   - (c) if still above 14 MB, keep only the 16 "raised" cards plus the dash and other-disagreement groups, and move "Needs a look"
     to a count with a seeded 40-card sample.

   Report the size and what was cut. Box styles and intro stay as phase 2 specified; "unsure" now means unresolved after r3.
5. Write the receipt `artifacts/n1/N1TS3_RECEIPT.json` and a section "N1-TS3" in `N1T_REPORT.md`. Run the tests.

**Last line:** `N1TS3 READY: lead_review before <n> → after r3 <n> (<reasons>); new raised candidates <n>; geo-audit cells 17; sheet <MB> MB, cards <n> (groups <...>); boxes changed <n>, unchanged <n>, unsure <n>; tests <n> passed`

**Step 0 (added 17 Oct, before step 1).**
1. **Replace this track's scanner copy** `scripts/secondary/reading/scan_rollout.py` with the canonical v4.4 file, BY HASH:
   - source `~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/tools/scan_rollout.py`;
   - expected sha256 `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`;
   - stop on a mismatch.

   Keep the old copy as `scan_rollout_secondary_pre_v44.py`.
2. **Re-scan with v4.4** every N1 rollout whose scan failed: n1t2 ctx01/r1, n1t3 ctx05/r3 and n1t3 ctx06/r3, plus any other failed
   scan under `artifacts/n1/answers/`.
   - A context whose v4.4 scan is clean has its answers ACCEPTED; record the reason and the old vs new findings.
   - Any context that still fails stays VOID.
   - Also re-scan every previously clean N1 rollout, to confirm v4.4 does not newly void it. Report each one.
3. Then continue with steps 1–5 as written.

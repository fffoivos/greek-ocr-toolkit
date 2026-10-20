# N1-Cc: zoom gap marker, approved controls, raised-dot candidates (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Continue N1-Cb (`docs/records/labelfix/secondary/N1C_REPORT.md` § N1-Cb). Same worktree, constraints, interpreters and allowed writes as
N1-C/N1-Cb. Read the lead's control review first: `docs/records/labelfix/secondary/N1_CONTROL_REVIEW.md`.

**Do.**
1. **Zoom marker** (renderer change, with tests). The zoom image gets the same two small mid-grey triangles as the line image:
   - placed in ADDED white margins above and below the zoom;
   - pointing at the x-centre of the target gap;
   - never overlapping an original pixel.

   Update the marker-preservation test to cover the zoom. Re-render the zoom for all 558 step1 slots, for every approved control and
   for the new candidates below. Keep the previous zoom files and write new ones under new hashes. The side measurement records do not
   change; re-verify them.
2. **Approved controls file** `artifacts/n1/controls/approved.jsonl`, from the review:
   - Map the cell numbers to slot ids through the scratchpad `n1_ctrl_sheets/sheets_index.json`.
   - Truth meanings use the `sep.md` vocabulary: `raised dot`, `baseline dot`, `comma`, `hyphen or dash`, `space`, `nothing`,
     `other`, `unreadable`.
   - The approved sets: baseline dot = cells 1–12, 14, 15, 18–24; comma = 25–47; hyphen or dash = 49, 50, 51, 53, 54, 56–70, 73,
     75, 76, 77, 78, 80, 81; nothing = 84, 87, 89, 90, 91, 92, 94; raised dot = the four C1 reference slots (C1 reference sheet cells
     1–4).
   - Check: 82 rows, no rejected cell included, and no id in step1 documents or reserved documents. The C1 lines are allowed only as
     controls.
3. **Raised-dot candidates.**
   - Draw from `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions/w1_elstat_separator_ambiguous_ids.txt`
     rows, and from any W1 elstat/gazette row whose Google text has `·` or `-` in a grammar-thousands slot of a 4+-digit token.
   - Exclusions: the row is not in step1 documents, not in reserved documents, not a C1 line, and its geometry is ok.
   - Draw up to 36 slots, at most 3 per document, seed `20261017:N1Cc:raised`. Render them with the new zoom marker.
   - Put them on contact sheets `n1cc_raised_NN.png` in the scratchpad `n1_ctrl_sheets/`: ≤12 per sheet, with the Google glyph and a
     cell numbering that continues from 101. Write `sheets_index_cc.json`.
   - Report how many candidates exist in total.
4. **One re-render sample sheet** `n1cc_zoom_check.png`: 12 cells drawn from the approved controls (cells 83–94-type multi-digit
   cases first). It lets the lead confirm the zoom marker.
5. Do NOT build any pack.
6. Write the receipt `artifacts/n1/N1Cc_RECEIPT.json`, append an "N1-Cc" section to `N1C_REPORT.md`, and run the tests.

**Last line:** `N1Cc READY: zoom re-rendered <n> (step1 <n>, controls <n>); approved controls 82 written (checks <ok>); raised-dot pool <n>, candidates <n> on <n> sheets; tests <n> passed`

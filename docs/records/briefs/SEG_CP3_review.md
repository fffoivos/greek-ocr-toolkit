# SEG-CP3 review: Sol code review (gpt-6.1-sol, medium, READ-ONLY; write only docs/records/reviews/SEG_CP3_review_2.md)

Review the uncommitted SEG-CP3 work, INCLUDING the SEG-CP3b fix round (`docs/records/briefs/SEG_CP3b_fix.md`) and whether the earlier review `docs/records/reviews/SEG_CP3_review.md` findings are closed (write to `docs/records/reviews/SEG_CP3_review_2.md` instead) in this worktree (brief `docs/records/briefs/SEG_CP3_build.md`, receipt `docs/records/harvest/collect_v3_admission/seg/CP3_RECEIPT.md`, commit list `seg/CP3_COMMIT_LIST.json`) against **CP3 of the ASTRA-SEG1 plan**: `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md` §"Numbered PLAN", item 3.

- Apply **its "Sol code-review criteria" verbatim**, one by one, each with a verdict and file:line.
- **Reproduce every acceptance number yourself** by rerunning the tests and the checkpoint's measurement scripts; do not trust the receipt.
- Confirm that no admission file, crops manifest or PNG changed (hashes vs HEAD), and that nothing wrote to the live run root.
- Check that the work reuses the existing segmenter tools rather than new heuristics, as the review's F2/F3 demand.

Write the findings by severity (blocking / high / medium / low), each with file:line. The last line must be exactly:
`SEG-CP3 review: <PASS|FAIL> | blocking: <n> | high: <n> | acceptance: <k>/<n> met reproduced | publish actions: <n>`

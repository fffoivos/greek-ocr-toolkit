# SEG-CP6 review: Sol code review (gpt-6.1-sol, medium, READ-ONLY; write only docs/records/reviews/SEG_CP6_review.md)

Review the uncommitted SEG-CP6 work in this worktree (brief `docs/records/briefs/SEG_CP6_build.md`, receipt `docs/records/harvest/collect_v3_admission/seg/CP6_RECEIPT.md`, commit list `seg/CP6_COMMIT_LIST.json`) against **CP6 of the ASTRA-SEG1 plan**: `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md` §"Numbered PLAN", item 6.

- Apply **its "Sol code-review criteria" verbatim**, one by one, each with a verdict and file:line.
- **Reproduce every acceptance number yourself** by rerunning the tests and the checkpoint's measurement scripts; do not trust the receipt.
- Confirm that no admission file, crops manifest or PNG changed (hashes vs HEAD), and that nothing wrote to the live run root.
- Also review the CP5c additions (regional inheritance for unknown axes, unknown -> admit as orientation_unknown, CP7 hooks), committed in dc47b8bb without their own review.
- Check the CENSUS3 parity claim yourself (decision-for-decision vs sha ef694589...).
- Check that the work reuses the existing segmenter tools rather than new heuristics, as the review's F2/F3 demand.

Write the findings by severity (blocking / high / medium / low), each with file:line. The last line must be exactly:
`SEG-CP6 review: <PASS|FAIL> | blocking: <n> | high: <n> | acceptance: <k>/<n> met reproduced | publish actions: <n>`

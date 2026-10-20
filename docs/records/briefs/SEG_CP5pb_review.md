# SEG-CP5′ review: Sol code review (gpt-6.1-sol, medium, READ-ONLY; write only docs/records/reviews/SEG_CP5p_review_2.md)

Review the uncommitted SEG-CP5′b work (brief `docs/records/briefs/SEG_CP5pb_component_edge_clip.md`, receipt `seg/CP5p_RECEIPT.md` section b; earlier review docs/records/reviews/SEG_CP5p_review.md).

**Criteria:**
- Does it implement the component-based target-band rule exactly (cut by L/R edge, >=50% band overlap, letter-scale via existing roles, native extent beyond edge > t) on the CP4 H2 path, with no new detector and no ownership retuning?
- Is it a target-row, left/right-edge rule only?
- Do touching components stay kept, and do shared-parent split letters resolve rather than false-drop?
- Is the tolerance stated in px and x-height, and taken from the middle of the passing interval rather than tuned to an edge case?
- Is `geometry_unavailable` behaviour unchanged, and is unavailable never counted as clip or keep?

**Reproduce yourself:**
- clips 4/4;
- the non-clip false drops on the CP7 draw;
- KEEP 22/22;
- the CP1 ledger numbers;
- the CP3/CP4/CP5 numbers;
- the tests.

Confirm that no admission file, crops manifest or PNG changed, and that SEG code wrote nothing to the live root.

Write the findings by severity with file:line. The last line must be exactly:
`SEG-CP5pb review: <PASS|FAIL> | blocking: <n> | high: <n> | reproduced: clips <a>/4, non-clip FP <b>/96, KEEP <c>/22 | publish actions: <n>`

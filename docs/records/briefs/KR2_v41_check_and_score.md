# KR2: scanner v4.1 replay check for kosmo2 c2b, then score the HANDOVER re-run (gpt-6.1-sol, medium, network OFF, mechanical)

## Coordinator ruling (option a)
The scanner misread a JS template literal: `${pwd}/zoom/NN.png` resolves inside the reader's own folder. **Accept c2b** after a replay check that:
- resolves every template path using the reader's recorded `pwd` (the exec_command output in the same rollout); and
- shows that each viewed image matches c2b's `zoom/` files **pixel for pixel**.

Record this as **scanner rule v4.1: "resolve pwd/template paths before the absolute-path test"**, with this run as the witness. The prompt stays verbatim.

## Do
1. **v4.1 check on c2b**, using the rollout in `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/kr1b_run.log` (`"rollout"`):
   - For record 27 and every other tool input, resolve `${…pwd…}` template paths to the recorded pwd. Confirm that pwd equals the c2b reader folder.
   - Confirm that every returned image matches a c2b `zoom/` file pixel-exactly, or a v4-accepted replay reproduction.
   - Re-run all the other v4 checks unchanged.
   - Write `scan/kosmo2/c2b.scan_v41.json`, recording the v4 violation, its resolution and the image matches.
   - **If anything else fails, c2b stays VOID:** report and stop.
   - Implement v4.1 as a **local wrapper** in `kosmo2/tools/` around the unchanged Sol-reading `scan_rollout.py`, with tests: the witness passes, and a true outside-path case still fails.
2. **Record v4.1** in `~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/HANDOVER.md` §5: append a "v4.1 (coordinator ruling, 17 Oct)" bullet with the rule, the witness (kosmo2 c2b, record 27) and the wrapper path. That session is closed; the coordinator authorised this edit. Change nothing else there, and leave a guarded commit list for that worktree as well.
3. **Score** c1 + c2b, 100 bed cards:
   - letters, crop_ok (final), marks (pending_opus), controls;
   - the review queue;
   - **paired against the pre-handover run** (SRK2, 87db4392: 96/99) on the same 100 cards: agreement per field and the flips.
4. Record SRK as "pre-handover, no controls" beside it.

Output: `docs/records/harvest/recut_v1/w1_masked/kosmo2/RESULTS.md` + `results.json`. Leave guarded commit lists. The last line must be exactly:
`KR2: <done|c2b VOID> | v4.1 witness: <ok> | letters y: <n> | crop_ok y: <n> | marks y: <n> (pending opus) | controls: <k>/10 | paired agreement letters/crop: <a>/<b> | review queue: <n>`

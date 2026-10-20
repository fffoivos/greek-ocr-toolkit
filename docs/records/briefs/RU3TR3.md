# RU3T-R3: r3 packs for the 12 VOID contexts + driver (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

RU3T-F1: 12/38 reader-contexts are VOID (ctx03/r1, ctx05/r1, ctx06/r1, ctx08/r1, ctx09/r2, ctx12/r2, ctx13/r1, ctx14/r1, ctx15/r1,
ctx18/r1, ctx18/r2, ctx19/r2). 1,100 positions lack an independent second read. The positions are in the scratchpad
`ru1_review/ru3t/fresh_r3_positions.jsonl`.

**Do.**
1. Report WHY each context is VOID: scan finding, control errors or coverage. One line each, to spot a systematic cause.
2. Build r3 packs for those positions: for each affected context, the same items, a fresh seeded order, fresh ids, the same controls.
   - ctx18 lost both readers, so it needs r3 AND r4. Build both, with independent orders.
   - Root: the scratchpad `sol_packs/ru3t/` (r3, r4 subfolders). Closure on every pack.
3. Driver `run_ru3t_r3_all.sh` (probe before each context, stop at 70%, never rerun), plus a finaliser update: r3/r4 replace the
   VOID readers; combine as before.
4. Write the receipt and a section "RU3T-R3" in `RU3T0_REPORT.md`, with the context list and a Codex estimate. Do not read.

**Last line:** `RU3TR3 READY: void causes <summary>; r3/r4 contexts <n>; items <n>; est <pts> pts; closure <ok>; dry-run <ok>`

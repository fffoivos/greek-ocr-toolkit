# SR-B4: resolve S2, final scoring and cost tables

Work non-interactively in `~/Projects/greek-ocr-toolkit-sol-reading`, and finish in this turn. Network off. Do not run git or codex. Write only under `docs/records/harvest/sol_reading/`. Use `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B` for any Pillow tool.

All 9 reading runs exist: r1, r2 and r3 for bsb, yer and owner39. Their answers, mapped files, controls, scans and ledger entries are under `answers/` and `usage_ledger.json`.

1. **Scans and mapping.**
   - Re-scan the three r3 rollouts with scanner v3 (rollouts from the ledger; reader dir `PACK_ROOT/<bed>/r3`). Report ok/violations.
   - Check that `answers/<bed>/r3.mapped.jsonl` and `r3.controls.json` exist and are complete. Re-run `map_answers.py <bed> r3` if not.
2. **Resolve and score.** Run `tools/resolve.py` for each bed, then `tools/score_all.py`. Regenerate `results/{results.json,TABLES.md,ERRORS.md}`.
3. **`results/SUMMARY.json` plus a short `results/SUMMARY.md`.** Tables only, no prose conclusions; every denominator stated.
   - **(a) Accuracy per bed × reader** (Sol r1, r2, S2; Opus E0a, E0b, E1; owner39 Opus partial pooled, plus Sol on the same 33 card-reads).
     - bsb: letters, marks, crop_ok, joint.
     - yer: slot, item.
     - owner39: per head and joint.
   - **(b) Variance yardsticks:** Sol r1 vs r2 and Opus E0a vs E0b. Give per-unit agreement, plus the absolute accuracy difference.
   - **(c) S1→S2 per bed,** with each of r1 and r2 taken as S1:
     - units changed;
     - changed to correct, changed to wrong, changed between wrong answers;
     - net accuracy change;
     - unresolved count.
   - **(d) Controls** per run.
   - **(e) Cost per run and per bed × arm** (S1 = one reader; S2 = r1 + r2 + r3):
     - wall seconds;
     - input, cached input, output and reasoning tokens;
     - uncached input = input − cached;
     - tokens per item;
     - tool calls;
     - weekly percent before and after;
     - credits.

     Also the cost ratio S2/S1, using r1 as S1 and r2 as S1.
   - **(f) Opus cost** from `opus_reference/usage_log.tsv`: total tokens, tool uses and duration_ms per item for E0a, E0b and E1 (bsb, yer), and the owner39 partial runs (marked partial). Keep the two meters apart.
   - **(g) Whole experiment:**
     - total Sol reading tokens;
     - weekly percent at the first and last probe of the reading runs (from `usage_ledger.json`);
     - the build/brief runs' tokens, from the rollouts named in the launcher logs `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/logs/SR-B*.codexlog` (session id → rollout), listed separately.
4. **Tests.** Run all tests and write `TEST_RESULTS_B4.txt`.

Last line: `SR-B4 READY: tests=<pass>/<total> scans r3=<ok/ok/ok> S2 joint bsb/yer/owner39=<x/n>/<x/n>/<x/n>`, or `SR-B4 BLOCKED: <reason>`.

# SR-B3: scorer fixes, matched comparisons, tie-break builds

Work non-interactively in `~/Projects/greek-ocr-toolkit-sol-reading`, and finish in this turn. Network off. Do not run git or codex. Write only under `docs/records/harvest/sol_reading/` and PACK_ROOT (`/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/sol_reading_packs`).

0. **Scanner v3 false positives** (bsb r1 rollout `~/.codex/sessions/2026/10/17/rollout-2026-10-17T13-00-24-01a1494e-34d0-7a00-b1c5-d734e6d8dde5.jsonl`, reader dir `PACK_ROOT/bsb/r1`; the lead reviewed it by hand and it is clean: all 122 returned images match its own zoom files).
   - **(a) Own folder.** The reader's own absolute folder path (`…/sol_reading_packs/bsb/r1` and anything under it) is inside the reader dir. It is not a violation. The `sol_reading_packs` name rule must fire only for paths that leave the reader's own folder (the pack root itself, a sibling bed or a sibling reader).
   - **(b) Template splitting.** A template such as ``${'<reader_dir>'}/zoom/${String(i).padStart(3,'0')}.png`` must not yield the bogus absolute path `/zoom/$`. Resolve string-literal interpolations (`${'…'}`) before path extraction. Treat any text that starts right after a `${…}` expression as relative to that expression, not as an absolute path.

   Add a regression test for each, plus one proving that a sibling reader path (`…/bsb/r2/…`) and the pack root still flag. Then re-scan EVERY run in `usage_ledger.json`, using each run's `rollout` with reader dir `PACK_ROOT/<bed>/<reader>`. Overwrite `answers/<bed>/<reader>.scan.json`, keeping any previous file as `.scan.v1.json` or `.scan.v2.json`, and report ok/violations per run. Note: run Pillow tools with `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B`. The default `python3` is arm64 and cannot load that Pillow; this crashed the yer r1 and bsb r1 scans in the driver.

1. **Bug in the owner39 agreement matrix.** In `results/TABLES.md`, every owner39 agreement cell is `0/0`, including `Sol r1 | Sol r1`. Find the cause, fix it, and add a regression test: self-agreement equals n, and two synthetic owner39 readers agree on a known count. Check the bsb and yer matrices for the same failure mode.

2. **Matched-card comparisons.** The Opus owner39 readers are partial: E0a r1 5, E0a r2 13, E0b r1 8, E0b r2 7 cards. For each Opus partial reader, report Sol r1, Sol r2 and S2 accuracy on exactly that reader's cards. Also pool all four into one "Opus partial pooled" row: each Opus card-read is one unit, and Sol is scored on the same card for each unit. Give paired better/worse/same counts against truth.

   For bsb and yer, add paired better/worse/same counts against truth for every Sol reader against Opus E0a, E0b and E1 on the same items.

3. **Wrong-answer listing.** For each Sol reader, list the owner39, yer and bsb units where it disagrees with truth. Give the item id, the original source id (from the efficiency keys, private), Sol's answer (form/heads, slot call, or the letters/marks/crop_ok/detail fields), the truth, and what each Opus reader said on that unit. Write `results/ERRORS.md` with one table per bed.

4. **Tie-breaks.** For each bed where both r1 and r2 answers exist, run `tools/build_tiebreak.py <bed>` and the pack scan on the r3 folder. Report disagreement counts and the r3 item counts.

5. Re-run `score_all.py` and regenerate `results/{results.json,TABLES.md}`. Run all tests and write `TEST_RESULTS_B3.txt`.

Last line: `SR-B3 READY: tests=<pass>/<total> r3 items bsb/yer/owner39=<n>/<n>/<n>`, or `SR-B3 BLOCKED: <reason>`.

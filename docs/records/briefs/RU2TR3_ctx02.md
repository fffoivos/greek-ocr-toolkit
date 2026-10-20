# RU2T-R3: void ctx02/r2, fresh r3 for ctx02 (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

`artifacts/ru1/ru2t/RU2TF_STOP.json`: ctx02/r2 failed the canonical v4.4 scan (unmatched image provenance at records 150 and 210).
**Lead ruling:** ctx02/r2 is VOID (its answers are kept, never used). ctx02 gets a fresh r3 reader, which is its independent second
read.

**Do.**
1. Scan every other RU2T reader-context with v4.4 (ctx03/r2 included, if the stop prevented it) and report.
2. Build `ctx02/r3` under the scratchpad `sol_packs/ru2t/`: same items, fresh seeded order `20261017:RU2T:ctx02:r3`, fresh ids,
   same controls, manifest, keys, closure. Add `r3` support to `run_ru2t.sh` and run a dry-run.
3. The finaliser uses r3 as ctx02's second read and never uses ctx02/r2. Add a test. Do NOT run the finaliser now.

**Last line:** `RU2TR3 READY: other scans <list ok/fail>; ctx02/r3 pack closure <ok>; dry-run <ok>; finalizer r3 routing test <passed>`

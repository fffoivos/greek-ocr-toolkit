# RU2T-R3b: void ctx03/r2, fresh r3 for ctx03 (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

`artifacts/ru1/ru2t/RU2TF_STOP.json`: ctx03/r2 failed the canonical v4.4 scan (unmatched image provenance at its recorded findings (RU2TR3_REPORT.md)).
**Lead ruling:** ctx03/r2 is VOID (its answers are kept, never used). ctx03 gets a fresh r3 reader, which is its independent second
read.

**Do.**
1. (Done in RU2T-R3; skip.)
2. Build `ctx03/r3` under the scratchpad `sol_packs/ru2t/`: same items, fresh seeded order `20261017:RU2T:ctx03:r3`, fresh ids,
   same controls, manifest, keys, closure. Add `r3` support to `run_ru2t.sh` and run a dry-run.
3. The finaliser uses r3 as ctx03's second read and never uses ctx03/r2. Add a test. Do NOT run the finaliser now.

**Last line:** `RU2TR3b READY: other scans <list ok/fail>; ctx03/r3 pack closure <ok>; dry-run <ok>; finalizer r3 routing test <passed>`

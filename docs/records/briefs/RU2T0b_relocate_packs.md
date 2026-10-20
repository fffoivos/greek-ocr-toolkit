# RU2T-0b: move RU2T packs outside the repo (gpt-6.1-sol, medium, network OFF; no .git writes; no reading)

RU2T-0 wrote its reader packs to `~/Projects/greek-ocr-toolkit-secondary/sol_packs/ru2t/`, INSIDE the repository, where the keys
(`artifacts/ru1/ru2t/`) are reachable. That violates HANDOVER §4: packs live outside every repository, away from keys.

**Do.**
1. Move the pack root to
   `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru2t/`,
   copy first and verify the bytes. Then remove the in-repo copy: this deletion is approved by the lead, because it holds only pack
   copies.
2. Update the RU2T launcher, finaliser and manifests (and anything else that records the root) to the new root.
3. Re-run closure on all 6 reader folders at the new location, plus the dry-run of `run_ru2t.sh` for every context and reader.
4. Add a guard to the pack builder that refuses any pack root inside a git worktree, with a test for it.
5. Append a note to `RU2T0_REPORT.md` and write the receipt `artifacts/ru1/RU2T0b_RECEIPT.json`.

**Last line:** `RU2T0b READY: packs moved <6/6>, closure <ok>, dry-runs <ok>, in-repo copy removed <yes>, guard test <passed>`

# RU1-R3: fresh reader for ctx04 + finalisation hook (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Same worktree, constraints and interpreters as RU1-S (`docs/records/labelfix/secondary/RU10_REPORT.md` § RU1-S).

**Lead ruling (17 Oct).**
- **ctx04/r2 is VOID.** Its 15 unmatched image-provenance findings stay unresolved, and the scanner's downscale policy is NOT
  widened. Keep its answers in `RU1S_uncleared/`; they never enter decisions.
- Context 4 gets a fresh **r3** reader instead. Its reads replace ctx04/r2 as the independent second read for ctx04 positions.
- The two scanner corrections made in RU1-S (the `pwd` template base, and Python `//` not being treated as a path) are accepted for
  this track's copy. Record them as a diff against the sol-reading scanner v4 in the report; the lead will tell the coordinator.

**Do.**
1. **r3 pack.** Build `PACK_ROOT/ctx04/r3/` with the same items as ctx04/r1 in a fresh seeded order (`20261017:RU1:ctx04:r3`), fresh
   opaque ids and the same controls. Write `MANIFEST.r3.json` and the keys `artifacts/ru1/keys/ctx04.r3.json`, then run closure.
2. **Launcher and mapper** accept `r3`, with the paths `ctx04.r3.*`. Run a dry-run check.
3. **Combiner.** For ctx04 positions, the second read comes from r3 and never from r2. Add tests for this.
4. **One finalisation command**, `scripts/secondary/ru1_finalize.sh`. After the lead runs the r3 reading, it does all of this in
   order:
   - the scan check;
   - the mapping;
   - the combiner;
   - the owner sheet HTML build (`ru1_owner_sheet.py`, as specified in RU1-S);
   - the summary.

   It refuses if any accepted reader-context's scan has not cleared. Test it on fixtures.
5. **Receipt** `artifacts/ru1/RU1R3_RECEIPT.json` and a section "RU1-R3" in `RU10_REPORT.md`.

**Last line:** `RU1R3 READY: ctx04/r3 pack closure <ok>; combiner r3 routing tests <n> passed; finalize dry-run <ok>`

# SCAN1: one canonical rollout leak scanner + HANDOVER §5 (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Worktree `~/Projects/greek-ocr-toolkit-sol-reading` (branch opus/sol-reading). It is now owned by the secondary-corrections lead
(coordinator ruling, 17 Oct). **One scanner implementation lives here.** The other leads copy it by hash and never fork it.

**Find the variants (read only):**
- this worktree: `docs/records/harvest/sol_reading/tools/scan_rollout.py` (v4) and `test_scan_rollout_v4.py`;
- the secondary-corrections copy: `~/Projects/greek-ocr-toolkit-secondary/scripts/secondary/reading/scan_rollout.py`, with two
  fixes: the literal `pwd` template base, and Python `//` not treated as a path. Its RU1-S report section in
  `docs/records/labelfix/secondary/RU10_REPORT.md` names the witness rollouts;
- the spell-check CQ1 v4.3 wrapper: `~/Projects/greek-ocr-toolkit-spellcheck-r2cards/artifacts/cq1/tools/` (opus/r2-cards
  caf0a39b9), with the scans `artifacts/cq1/answers/r1.scan_v43.json` and `r1b.scan.json`;
- v4.1 (template paths, the sourcing lead's witness) and v4.2 (read-only OS font paths): search the sourcing worktrees
  (`~/Projects/greek-ocr-toolkit-sol-recut`, `~/Projects/greek-ocr-toolkit-sol-collect`) and their scratchpad launcher copies for
  scanner versions, notes and witness rollouts. Report what you find and where. If a version's source or witness cannot be found,
  say so; do not reconstruct it from memory.

**Do.**
1. **Canonical scanner.** `docs/records/harvest/sol_reading/tools/scan_rollout.py`, with version string `v4.4-canonical`, implementing v4
   plus v4.1, v4.2 and v4.3 and the two secondary fixes, all as specified by their sources:
   - **v4.3:** resolve `load(NAME) + "literal"` / `'literal'` only from the reader's own literal `store(NAME, "…")` in the same
     rollout, before the absolute-path test; anything unresolved stays a violation.
   - Keep v4 under its old name, as `scan_rollout_v4.py`, untouched, for replay.
2. **Tests** in `test_scan_rollout_canonical.py`:
   - all existing v4 tests;
   - one positive and one negative test per rule. Negative cases include `store("base","/Users/x")` + `load("base")+"/keys/k.json"`
     fails, and a load without a store fails;
   - **witness replays.** Re-scan each witness rollout and assert the recorded outcome:
     - CQ1 `rollout-2026-10-17T18-40-41-01a14a85-bfd9-75e3-b20f-a79f924d6dbf.jsonl` (~/.codex/sessions/2026/10/17/): VOID, with
       record 24 unresolved;
     - CQ1 r1b: clean;
     - secondary RU1 ctx01/r2: clean after the fixes;
     - secondary RU1 ctx04/r2: still VOID with 15 provenance findings;
     - the v4.1/v4.2 witnesses if found.

   A witness whose rollout file is missing is skipped with an explicit message, never silently.
3. **HANDOVER.md §5:** add a "Scanner versions" table: version | rule | witness rollout + expected result | test name. Then add one
   line: "Canonical file sha256 = <hex>; copy by hash, do not fork". Update §9 so that the owner is the secondary-corrections lead.
4. **Distribution manifest** `docs/records/harvest/sol_reading/tools/SCANNER_CANONICAL.json`: sha256 of the canonical scanner and its test
   file, plus the list of known copies (paths) and whether each matches. Do NOT modify the copies.
5. Run all the tests and report.

**Last line:** `SCAN1 READY: canonical v4.4 sha256 <hex>; rules v4.1 <found|missing>, v4.2 <found|missing>, v4.3 ok, pwd ok, // ok; tests <n> passed; witnesses replayed <n> (skipped <n>); copies matching <n>/<n>`

# Spell-check (polytonic marks) track: hand-off, 18 Oct 2026 (Claude usage stop)

Scope: polytonic marks only. Numerics and other secondary faults belong to the "Correct secondary Google OCR errors" lead.
S = `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad`. Sol launcher:
`SOL_REPO=<worktree> bash $S/run_wt_medium.sh <NAME> <log> <brief.md> <on|off>` (the brief must live in `<worktree>/docs/briefs/`).
**Sol cannot run nested Sol readers** (no network in its sandbox). The lead runs reader scripts directly.

## 1. sf7-rc1 release (gate cycle; owner GO)

- **Preregistration:** `docs/records/labelfix/spellcheck/SF7_PREREGISTRATION.md` (sha 64a84ed0…).
- **Package:** opus/spellcheck 69a00ca13. Job 3687228 COMPLETED.
- **Readback and LQB:** RB7, commit 2135f3c36. LQB marks P on tier A/B: A 100% = B 100% (only about 20 lines overlap), so **A chosen**.
- **Release (train only):** `artifacts/sf7_rc1/release_edits_only_A.jsonl`, sha 1e3ac334…, 605 rows / 665 edits. Status
  **candidate_pre_audit, NOT bound.**
- **The blind 100-line audit:** frame `artifacts/sf7_rc1/audit100_frame.jsonl`.
  - **Sol part (AU1):** the pack build may have finished; check `$S/au1_run.txt` and `docs/records/labelfix/spellcheck/SF7_AUDIT_PARTIAL.md`.
    Next: the lead runs `bash artifacts/sf7_rc1/audit/RUN.sh`, then `REREAD.sh`, then `SCORE.sh`. The canonical scanner sha must be the
    adopted one; see §3.
  - **Opus part:** lowercase breathing, subscript and dialytika heads, as two-reader four-head cards. **After the Claude reset only.**
    The per-head counts are in `artifacts/sf7_rc1/audit/routing.json`.
  - **Bar:** ≥ 83/100 line precision. Nothing binds before the full audit.
- **Test/dev counterpart (TR1, coordinator-requested):** check `$S/tr1_run.txt` and `docs/records/labelfix/spellcheck/SF7_TEST_COUNTERPART.md`.
  It either deploys a package (then the lead runs its `VERIFY_CMD.sh` and the coordinator submits) or estimates the inference cost for
  the coordinator.
- **Disk:** about 7.5 GB free; the Gazette watchdog trips at 10 GB. Pull only small files from Clariden.

## 2. R2a / R2a-2 (owner GO for option (a))

- **R2a:** FAILED its preregistration (R2A_DIGEST.md, opus/r2-prep 8896ab792) and was not adopted. Capital recall rose from 47% to 87.5%.
- **R2a-2:** preregistration `R2A2_PREREGISTRATION.md` (opus/r2-prep c25e39098, sha dbac559f…, amendment 1: W-CAP from the validation
  documents). **TODO:** add amendment 1a (the coordinator's consequence note: the validation documents are now exposed to capitals
  witness selection, so they can't serve as a fresh final capitals readout; the locked (ii)/(i-b) strata are the only untouched final
  cohorts; the LQB in-sample guard lists the W-CAP items against R2a-2). Record the new sha in the CQ4 receipts.
- **CQ1:** Sol qualified on capitals, 57/60 = 95.0%, 0 invented breathings. Compounds 7/9, so the re-read rule is required.
- **CQ4 inputs** (opus/r2-cards, `artifacts/cq4/`): 18 contexts read. 3 VALID, 15 VOID; every VOID is a scanner v4.4 false positive
  (CQ4E_VOIDS.md).
  - **Current aggregate:** top-up 211 resolved, W-CAP 0/300. The void attempt is archived in `artifacts/cq4/void_attempt_cq4d/`.
  - **Next:** once v4.5 is adopted, rescan the 15 rollouts with v4.5, keeping the v4.4 VOIDs on record. Then re-run BUILD_REREAD,
    the re-read phase (`bash artifacts/cq4/RUN_ALL.sh --phase reread`), and AGGREGATE. The workflow needs a "rescan existing rollout"
    mode; brief Sol for it. Then the lead's pixel queue, then the R2a-2 package (B1 + real-input dry run + verify), then the
    coordinator submits.

## 3. Canonical scanner v4.5 (coordinator ruling (i))

- **Built (SC45):** `~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/tools/scan_rollout.py`, sha
  f2c2a346de7a0b52b9890edb632af9125a5779d5b2411f287023102030bc9f6b. 88 tests; v4.1–v4.4 regressions 53/53. NOT yet committed and NOT adopted.
- **Review (SC45R):** running; result in `$S/sc45r_run.txt` and `docs/records/harvest/sol_reading/SCANNER_V45_REVIEW.md`.
  - **On PASS:** commit it on opus/sol-reading, add the v4.5 row to HANDOVER.md §5 with the sha, send the sha to the coordinator (who
    informs the sourcing lead), then do the CQ4 rescan (§2).
  - **On HOLD:** a Sol fix round, then review again.

## 4. Other state

- **Merge** done (opus/spellcheck 960a70163). **Sync:** cleanup-1 6fe84030c, r2-prep d891bcaa3. r2-cards is not yet synced
  (`docs/records/reviews/harness/sync_20261017.sh`).
- **SR1 tools** done (cleanup-1 870014a4f). **DEL3** caches done (the suite note is in its receipt). **Worktree removals deferred**
  (WT1: custody 1.6 GB + 364 repoints) until there is disk.
- **Owner sheets:** the coordinator publishes them. Builder: cleanup-1 `scripts/review/build_owner_sheets_v2.py`; OS5 added the R2a
  group.
- **Marks status block** for CORRECTION_STATUS: `docs/records/labelfix/spellcheck/CORRECTION_STATUS_MARKS.md` (update it with sf7 when audited).
- **Owner rules in force:** Opus reading only after the reset, with two readers + tiebreak; Sol for execution; the lead writes no
  code; no pushes; report in Athens time.

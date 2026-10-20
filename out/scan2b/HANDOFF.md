# SCAN2B — scanner v4.5.1

Fixed SCAN2R H1–H3 in `docs/harvest/sol_reading/tools/scan_rollout.py`, offline. Canonical SHA-256: `d326e808d9e1964c4b58afc39b69d3377b4a8e8a13e650a125d63b262f393b42`. HANDOVER records the same identity.

- **H1** (original scanner lines 444–459): parse a closed sequence of independent shell units before replaying any extracted heredoc. Unsupported surrounding control flow rejects the whole command; false branches and uncalled functions confer no reconstruction authority. Literal helper arguments, including quoted multiline data, remain independent units.
- **H2** (original scanner lines 439–464): invalidate helper authority before every accepted inline replay, including the whole-command fast path. Inspect writes in the restricted AST: a known literal output invalidates its helper path; computed/unknown write targets and uncertain commands invalidate all cached helpers. Known image outputs such as `zoom/detail.png` preserve unrelated helper identity. There is no early successful exit before invalidation.
- **H3** (original scanner lines 562–576): preserve the pre-expansion text and inspect literals removed by loop replacement, alongside the expanded concrete paths. The existing answer-data and font exceptions remain scoped to their original proofs.

## Qualification

`tests/test_scan_rollout.py:181` adds three synthetic fixture tests: false-branch/uncalled-function heredocs, accepted-command helper overwrite, and unused forbidden loop-header paths (`/tmp/outside`, `../truth.json`). These are five concrete negative rollouts across the three requested probe families; all return VOID. `probes_v45_baseline.log` independently confirms unchanged v4.5 incorrectly returns VALID for all five (its five expected assertion failures are the baseline demonstration).

Final command, network OFF:

```
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B tests/test_scan_rollout.py
```

**96 passed in 123.979 seconds, zero skips**: all 93 prior tests plus three probe tests. The existing version assertion now expects `4.5.1`; the other prior assertions remain unchanged. All six external historical witnesses ran. See `tests_final.log`.

## Rescan versus v4.5

`out/scan2/rescan_v451.json`: **15/15 VALID, zero remaining flags, zero verdict changes versus v4.5**. All per-rollout image-match counts also remain unchanged. Individual receipts are `out/scan2/<tag>.v451.scan.json`. The final rescan process exited 0; `rescan_final.log` contains all 15 outcomes.

The script verifies rollout and parent-manifest hashes against preserved v4.5 identities, pins the scanner digest, and verifies every file in `out/scan2/cq4_receipts_sha256.json`. Protected CQ4 receipts/ledger and v4.5 outputs remain unchanged. No network, reader launches, answer scoring or external writes were used.

## Commit delivery and sandbox limitation

Bundled implementation commit: `29168a7d3704984974eb1fdad3d1546457114ee3`, parent `7900952351298701ff75ab4f2f97498413efd3e5`, branch name `opus/sol-reading` inside `scan2b-v451.bundle`. The bundle was verified and contains the scanner, tests, HANDOVER, final logs, rescan scripts, summary and all 15 receipts. `COMMIT.json` lists its exact 26 changed paths. This handoff and `COMMIT.json` accompany the bundle.

**The checkout branch was not advanced.** The requested staging operation failed with:

```
fatal: Unable to create '/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.git/worktrees/greek-ocr-toolkit-sol-reading/index.lock': Operation not permitted
```

The session grants read-only access to Git metadata and disallows escalation. The commit was therefore built in a temporary isolated Git repository and exported as a verified bundle; it is ready for installation in a write-enabled session. The checkout remains on `opus/sol-reading` at its original HEAD. Pre-existing untracked SC45 briefs were excluded.

SCAN2B: done | v4.5.1 sha d326e808 | tests 96 passed (+3 probes VOID) | rescan 15/15 | commit 29168a7d3704984974eb1fdad3d1546457114ee3

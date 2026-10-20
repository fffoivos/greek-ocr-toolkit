# SCAN2F — unconditional invalidation, v4.5.5

Canonical scanner: `docs/harvest/sol_reading/tools/scan_rollout.py`.
SHA-256: `e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1`. HANDOVER records the same identity.

The shared walker now exposes closed shell execution units in chronological order. Its per-command loop computes the write set and invalidates cached scripts before definition admission, argv checks, restricted parsing, skips or replay. Unknown shell scopes remain opaque and invalidate all authority. A later rewrite in a shell call does not move ahead of an earlier invocation.

Write analysis is independent of restricted replay admission. Literal heredoc destinations, Python saves and file writes invalidate their targets; unresolved targets/effects invalidate all cached scripts. Literal single-assignment Path/file bindings prove destinations without a recorder-specific exception. Rejected imports/argv, computed targets, Path.open, rebound APIs, callbacks, expanded arguments and ambiguous absolute/parent-relative paths cannot bypass the barrier. Target comparison also conservatively handles case-insensitive filesystems.

Only a new literal definition unit inserts a script into the authority cache. Replay materializes these definitions into its fresh temporary filesystem and compares exact on-disk bytes with the cached source before using a helper. A mismatching source makes its effects unknown and revokes authority; matching restored bytes alone never reinsert it. The currently executing source may finish its own self-overwrite, but is never reinstated afterward. P1 retains its exact current-recorder byte check, closed answer grammar and unchanged AST pin. Reader directories never seed helper replay.

## Qualification

`tests/fixtures/v45/rejected_recorder_overwrites.json` contains both SCAN2R5 variants. Each records DEFINE, the overwriter definition, its rejected invocation, the answer invocation, then DEFINE restoring the exact recorder bytes afterward, followed by an exact source-image return. Both remain **VOID** with `/n` findings and an exact byte image match. Tests also distinguish byte restoration from a new literal definition and check the current-helper byte gate, unknown effects, callbacks, expanded arguments and path aliases.

Offline command:

```sh
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B tests/test_scan_rollout.py
```

**107 tests passed in 132.106 seconds, zero skips**: all 105 existing tests plus the two new probes. All six historical witnesses ran. See `tests_final.log`, `targeted.log`, `barrier_probes.json` and the tested-source hashes in `SOURCE.json`. Pre-existing test changes and both required helper/recorder fixture files were retained; unrelated untracked SC45 briefs were excluded.

## Rescan

`out/scan2/rescan_v455.json`: **15/15 VALID, zero remaining findings**. Fifteen `.v455.scan.json` receipts accompany it. `rescan.py` runs offline with at most three worker processes; `verify.py` checks the final identities and evidence.

`verification.json` confirms all 22 protected CQ4 hashes are unchanged, all rollout/manifest identities match, and verdicts, violations, image counts, loop expansions and image evidence equal v4.5.4. All 64 reconstructed replay effect sequences are identical. Their command receipts differ in grouping/skipped-definition bookkeeping, which the verifier records separately and normalizes to compare actual replayed mkdir/Python effects, return codes and stderr. No P1–P3 rule was relaxed. Earlier rescans, protected receipts, ledgers and source packs were preserved. No network, reader launch or answer scoring was used.

## Commit delivery and branch limitation

Original checkout branch: `opus/sol-reading`; parent HEAD: `17c725ead711258b28d35ea2b07fc008ae645da7`. `git add` could not create its external Git metadata's `index.lock` (`Operation not permitted`); this environment disallows permission escalation. **The original checkout branch was not advanced.**

A temporary local Git repository created commit `ec200b877f1124f43ccb38ccadd3e7daa681cb74` on its `opus/sol-reading` ref, directly parented by that HEAD. `scan2f-v455.bundle` was verified offline and contains this commit with that parent as its prerequisite. Every one of its 32 changed blobs was compared byte-for-byte with the delivered workspace. `COMMIT.json` records the bundle hash and paths. This handoff and the COMMIT receipt accompany the bundle outside its commit tree, avoiding a self-referential commit SHA. Importing/advancing the original branch remains an environment-blocked delivery step.

SCAN2F: done | v4.5.5 sha e44f8c8a | tests 107 passed (+2 probes VOID) | rescan 15/15 | commit ec200b877f1124f43ccb38ccadd3e7daa681cb74

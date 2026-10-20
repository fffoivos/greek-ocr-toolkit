# SCAN2E — recorder authority v4.5.4

Canonical scanner: `docs/harvest/sol_reading/tools/scan_rollout.py`.
SHA-256: `c3abc4c7a2bcb16afc8ba2345d384d0935476f353cc27ded4cd595864bf4d844`. HANDOVER records the same identity.

`recorded_helpers()` no longer extracts heredocs or maintains its own textual invalidation policy. It drains `replay_history()` with one shared path-keyed script dictionary. That walker admits definitions only through `independent_units()` and applies `invalidate_helpers()` to inline and expanded helper writes. Computed, variable and literal-loop write targets clear the cache. Its replay admission policy is unchanged.

P1's `answer_data()` now requires the reader directory. Every caller passes it. Before the existing AST pin grants an exemption, the current recorder must be a readable nonsymlink file with exactly the bytes represented by its cached heredoc (including the shell's final newline). Missing or different bytes leave the original command for ordinary path inspection. The closed answer grammar and AST pin are unchanged.

## Qualification

`tests/fixtures/v45/recorder_overwrites.json` contains all five SCAN2R4 recorder histories: computed target, false branch, variable target, second helper and literal loop. All five return VOID, retaining `/n` findings while the source image matches exactly. The probes deliberately leave matching source on disk to verify that the shared history barrier independently revokes authority. Additional tests cover missing/changed current bytes, an uncalled function and a heredoc embedded in a Python string. Positive recorder fixtures now provide the actual on-disk source required by P1.

Offline command:

```sh
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B tests/test_scan_rollout.py
```

**105 tests passed in 100.938 seconds, zero skips.** All six historical witnesses ran. Final output: `out/scan2e/tests_final.log`. Pre-existing Scan2B/Scan2C test edits and their helper-overwrite fixture were preserved and included so the committed suite is complete. The two pre-existing untracked SC45 briefs are excluded.

## Rescan

`out/scan2/rescan_v454.json`: **15/15 VALID, zero remaining findings**. All 15 receipts are `<tag>.v454.scan.json` alongside it. `out/scan2e/verification.json` verifies identical verdicts, violations, complete image evidence, image-match counts and loop expansions against v4.5.2. All rollout/manifest identities, the scanner identity and all 22 protected CQ4 hashes match. No protected receipts, ledgers, source packs or existing rescans were overwritten. No network, reader launch or answer scoring was used.

Reproduce with `out/scan2e/rescan.py`, then `out/scan2e/verify.py`, using the same Python interpreter. Tested-source hashes are in `out/scan2e/SOURCE.json`.

## Commit delivery and remaining environment limitation

The requested checkout is on `opus/sol-reading`, but its branch could not be advanced: `git add` failed creating the external worktree metadata's `index.lock` with `Operation not permitted`. This session disallows permission escalation. No checkout Git metadata was changed.

A temporary local Git repository produced commit `a4056ec5f8e471d3773e7c6416ddfa839cb27579`, directly parented by checkout HEAD `da5f3550df4de7f92f5abf1fd63c6d9ed39fb2ab`, on its `opus/sol-reading` branch. The verified bundle is `out/scan2e/scan2e-v454.bundle`; its sole prerequisite is that parent. Every changed committed blob was compared byte-for-byte with the delivered workspace. `out/scan2e/COMMIT.json` lists all 28 paths and the bundle hash. This handoff and COMMIT receipt accompany the commit outside its tree to avoid a self-referential commit SHA.

The implementation, qualification and rescan are complete; updating the original branch remains blocked by the filesystem restriction. An authorized environment can import the bundle's `opus/sol-reading` ref and fast-forward from the recorded parent.

SCAN2E: done | v4.5.4 sha c3abc4c7 | tests 105 passed (+5 probes VOID) | rescan 15/15 | commit a4056ec5f8e471d3773e7c6416ddfa839cb27579

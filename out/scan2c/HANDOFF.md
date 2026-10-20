# SCAN2C — scanner v4.5.2

Closed SCAN2R2 H1 in `docs/harvest/sol_reading/tools/scan_rollout.py`, offline. Canonical SHA-256: `7b3647162c527426225f26b3c8eba494fb89b52302002594eb0b8246e5642f4e`. HANDOVER records the same identity.

The expanded helper-invocation branch now calls `invalidate_helpers(replay, helpers)` after substituting literal argv and validating the restricted Python, before yielding the replay. Its writes invalidate affected cached helper sources, including the invoking helper itself; computed/unknown targets retain the existing conservative invalidation of all helpers. A subsequent invocation cannot execute the invalidated cached Python. Whole-command and isolated inline replay retain their existing invalidation barriers. The original reader pack's final helper files are never used as historical authority.

`tests/fixtures/v45/helper_overwrites.json` records both review histories exactly, with separate recorded calls. `Scan2CProbes` checks both return VOID with unmatched image provenance and verifies the stale final invocation is skipped. Probe A leaves the requested image missing; probe B leaves the actual 1×1 blue overwrite. The unmodified v4.5.1 scanner from checkout HEAD incorrectly returns VALID for both; see `probes_v451_baseline.log` (two expected assertion failures, harness exits successfully). Fixed-probe output is `probes_final.log`.

## Qualification

```sh
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B tests/test_scan_rollout.py
```

**98 tests passed in 116.512 seconds, zero skips**: all 96 prior tests plus the two new probes. All six historical witnesses ran. The pre-existing uncommitted `Scan2BProbes` tests were preserved and included; the only other existing test edit is the version assertion to `4.5.2`. Full output: `tests_final.log`.

## Rescan

`out/scan2/rescan_v452.json`: **15/15 VALID, zero remaining findings, zero verdict changes versus v4.5.1**. All image-match counts remain unchanged. Individual receipts are `out/scan2/<tag>.v452.scan.json`; all 15 outcomes appear in `rescan_final.log`.

The rescan verifies the scanner, rollout, parent-manifest, baseline summary and protected CQ4 receipt identities before and after replay. All protected receipt hashes match. v4.5/v4.5.1 outputs, original packs, CQ4 receipts and ledgers remain unchanged. No network, reader launches, answer scoring or external writes were used.

## Commit delivery

The requested checkout staging failed:

```text
fatal: Unable to create '/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.git/worktrees/greek-ocr-toolkit-sol-reading/index.lock': Operation not permitted
```

Git metadata is read-only and this session disallows escalation. The checkout branch cannot be advanced here. Verified bundle `scan2c-v452.bundle` contains commit `a82920d81f9d9f8b19c145e723f580317b504cee`, parent `1297ab96dffe09b6cd9463bdb420b69dbfa6a7fe`, on its `opus/sol-reading` branch (28 changed paths listed in `COMMIT.json`); the handoff and commit receipt accompany the commit to avoid embedding its own SHA in its tree. The pre-existing untracked SC45 briefs are excluded.

SCAN2C: done | v4.5.2 sha 7b364716 | tests 98 passed (+2 probes VOID) | rescan 15/15 | commit a82920d81f9d9f8b19c145e723f580317b504cee

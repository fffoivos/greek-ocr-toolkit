# SCAN2 — canonical scanner v4.5

Implemented in `docs/harvest/sol_reading/tools/scan_rollout.py`; canonical SHA-256 `c5204fe88490c35af07d1257680a9d32d4e43ab7be329b352af83c88a9cee17c`. `docs/harvest/sol_reading/HANDOVER.md` records this hash and the coordinator's three rulings. The pre-existing SC45 candidate was reviewed and completed for SCAN2; its historical notes and files remain in the worktree.

- **P1:** closed breathing/accent and yes/no answer atoms (optional uncertainty `?`) plus decimal numeric ids are data only as complete argv to the recorded AST-pinned confined recorder. Real `/n`, `/tmp/outside`, `../truth.json`, invalid/mixed atoms, changed helpers and shell additions still fail path checks.
- **P2:** proven returns at any common non-upscaling scale, within one pixel on both axes, with RGB MAD strictly below 2/255 under a named standard filter and fully opaque alpha. New zoom scales require manifest-seeded reconstruction. Native same-size exact mode/pixel checks remain unchanged, as required by the CQ4E ruling. Crop, distortion, upscale, partial alpha, MAD >= 2/255 and unseeded zoom fixtures fail.
- **P3:** finite literal view arrays/ranges expand in output order. Recorded confined helpers replay their literal integer argv at the historical point, including overwritten `zoom/batch.png`. Independent `mkdir zoom` / `mkdir -p zoom` survives an unused rejected import; safe image heredocs are isolated from answer code. Unsafe/dynamic/path-escape/extra-image negatives fail.

## Qualification

`tests/test_scan_rollout.py` and `tests/fixtures/v45/` contain 40 v4.5 tests, including positive and negative fixture matrices for each pattern. The entrypoint also runs all 53 existing canonical/archived regression cases: **93 passed, 40 new, zero skips**. This includes all six external witnesses, the CQ1 record-24 VOID, and 19 synthetic overwritten snapshots. Two RU1 witness packs require temporary restoration of missing crops from a local hash-verified cache; source packs/rollouts remain unchanged. Existing native-size mode and one-pixel-change rejection fixtures still pass.

Command (network off):

```
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B tests/test_scan_rollout.py
```

Full final test output: `out/scan2/tests_final.log`.

## CQ4 rescan

`out/scan2/rescan_v45.json` contains the per-rollout v4.4 verdict and original flags, v4.5 verdict, remaining flags, rollout/manifest digests and image-match counts. All **15/15 are VALID; zero flags remain**, against **15 original VOID verdicts / 72 original flags**. Individual final-code receipts are `<tag>.v45.scan.json` alongside it.

The v4.4 comparison in the final adjudication uses the preserved CQ4E receipts and the hash-verified canonical v4.4 scanner identity (`dd2fc59d…`). A separate preliminary pass reran v4.4 and checked its violations against those receipts. It is retained under `preliminary/` for audit, not as the final-code adjudication. The final pass pins the actual v4.5 scanner digest at import and verifies it again at completion. Each rollout and parent manifest digest is checked against CQ4E before scanning. `cq4_receipts_sha256.json` records preserved receipt/ledger hashes, rechecked after all rescans.

No CQ4 receipts, ledgers, answers, scores or aggregates were overwritten. This delivers a scanner adjudication; it does not accept or rescore answers. No network or new reader runs were used.

## Delivery

Git metadata is read-only in this session, so delivery uses the authorized bundle option: `out/scan2/scan2-v45-c5204fe8.tar.gz`. It contains the scanner and required modules, tests/fixtures, updated HANDOVER, patch, final logs and receipts. `SOURCE.json` records source hashes. Base commit: `8b6b34dbd86a18a93631448ec24be69a29ffa4c0` on `opus/sol-reading`. No commit was attempted.

SCAN2: done | v4.5 sha c5204fe8 | tests: 93 passed (40 new) | rescan: 15/15 VALID, 0 still VOID (none) | commit: bundle

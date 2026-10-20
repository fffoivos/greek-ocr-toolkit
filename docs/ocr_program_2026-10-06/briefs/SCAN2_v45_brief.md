# SCAN2 — canonical scanner v4.5 (gpt-6.1-sol, medium, network OFF; commit on opus/sol-reading or bundle under out/scan2/)

Ruling (coordinator, 18 Oct): the three false-positive patterns found by CQ4E become canonical v4.5. Source of the patterns and fixtures: ~/Projects/greek-ocr-toolkit-spellcheck-r2cards/docs/labelfix/spellcheck/R2/CQ4E_VOIDS.md (read-only; 297 commands reviewed, 72 flags, 0 genuine leaks) and the 15 VOID rollouts it cites (~/.codex/sessions/…, read-only).

Implement in tools/scan_rollout.py (keep v4.1–v4.4 behaviour and all existing fixtures/tests passing):
- P1 (answer atoms as data): only tokens of the closed answer grammar (define it from the HANDOVER answer formats: e.g. `r?/n`, `s/a`, `y/n` atoms, numeric ids) passed as argv to the pack's own zoom/record helper are data; any other `/x` or `../` path keeps the path rules (`/n` as a real path, `/tmp/outside`, `../truth.json` must still fail — negative fixtures).
- P2 (image returns): accept a returned image at any common non-upscaling scale with ≤1 px rounding, MAD < 2/255 against the manifest-seeded source, fully opaque alpha (RGB→RGBA opaque allowed); still reject crops, distortions, upscales (negative fixtures with MAD ≥ 2/255, a crop, an upscale).
- P3 (templates/history): expand finite literal loops/ranges over `zoom/b${n}.png`-style templates; replay a recorded confined helper (`zoom/batch.png` overwritten per batch) with its literal argv; isolate a literal `mkdir zoom` next to an unused import (no drop of the mkdir).
Each pattern: positive + negative fixtures under tests/fixtures/v45/, tests in tests/test_scan_rollout.py; bump the version string to v4.5; rescan the 15 CQ4 rollouts and write out/scan2/rescan_v45.json (per rollout: v4.4 verdict, v4.5 verdict, flags remaining); keep the v4.4 VOIDs on record (do not overwrite the CQ4 receipts). Update HANDOVER.md: canonical v4.5 sha256 of tools/scan_rollout.py and the three rulings.

Hand-off: out/scan2/HANDOFF.md; last line exactly:
`SCAN2: done | v4.5 sha <sha8> | tests: <n> passed (<n> new) | rescan: <valid>/15 VALID, <n> still VOID (reasons) | commit: <sha|bundle>`

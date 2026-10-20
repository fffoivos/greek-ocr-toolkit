# SC45: canonical scanner 4.5

18 October 2026. Canonical file: `tools/scan_rollout.py`.

- Before SHA-256: `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`.
- After SHA-256: `f2c2a346de7a0b52b9890edb632af9125a5779d5b2411f287023102030bc9f6b`.
- Reported `scanner_version`: `"4.5"`.

## Changes and guards

**P1:** CQ1/CQ4 prompt semantics define four breathing categories (`n/s/r/u`), five accent categories (`n/a/g/c/u`), and high/low confidence. The closed shorthand grammar is `[nsru]\??/[nagcu]\??`: `?` marks low confidence. Only complete argv data to the historically recorded, AST-pinned confined `zoom/record.py` is masked for path checks. The pin covers its IO and category mappings; its filename alone grants nothing. Other arguments, shell syntax, forbidden names and real paths retain checks. Each command is checked once, in historical order.

**P2:** A common non-upscaling scale must fit both axes within one pixel. RGB MAD must be strictly below 2 on the 0–255 scale under a reported Pillow filter (LANCZOS, BICUBIC, BILINEAR, NEAREST, BOX or HAMMING). Alpha must be fully opaque for resized returns; source alpha must also be opaque. Existing native-size mode/pixel checks remain strict. Existing v4 byte/pixel and 2048 provenance baselines remain; newly admitted zoom scales require reconstruction seeded only from verified manifest `items.jsonl` and `img/`, never preserved `zoom/`. Reconstructed historical views use the same comparison function.

**P3:** Expand finite literal arrays or constant integer `++` ranges, at most 1,000 views per loop; resolve literal substitutions and fixed zero padding without executing JavaScript. Bind images to concrete requested paths in output order. Recorded helper source and literal integer argv are replayed at their historical invocation through the unchanged AST/API allowlist and IO audit hook. Independent literal `mkdir -p zoom` and separately validated image-only heredocs survive rejected answer code. Dynamic bounds, unsafe helpers, path escapes and extra/unproven images fail. Legacy manifest-data row views use recorded `ImageView` events, without granting dynamic expansion or zoom replay authority.

## Fixtures and verification

`tools/test_scan_rollout_v45.py` contains 35 positive/negative tests: P1 **3/5**, P2 **4/7**, P3 **7/9**. Subcases include all four CQ4E shorthand commands, real `/n`, `/a`, `/c`, `/tmp/outside`, `../truth.json`, `keys/`, bad atoms/helpers, resizing and strict MAD boundaries, crops, distortions, transparency, upscales, output order, dynamic bounds, isolated mkdir/heredocs, and 19 synthetic historical overwrites using the recorded batch helper. Helper text fixtures are in `tools/fixtures_v45/`.

Qualification: **88 distinct tests passed, 53/53 regressions, zero skips** (plus the rerun of the strengthened same-aspect crop fixture). The existing regression modules contain 53 tests, including six witness replays. Only the version assertion and P2-superseded smaller-downscale assertion change. CQ1 r1 must retain its exact record-24 VOID; r1b stays clean. Two RU1 packs have 87/88 missing original crops: the harness reconstructs temporary snapshots from the local content-addressed cache, verifies every recovered byte against the original manifest, and relocates only the reader root. Original packs and rollouts remain untouched; snapshot receipts are in `tools/v45_tests.log`.

No CQ4 rollout was rescanned. CQ4 evidence and ledger were read only. No network access, `.git` writes, registration/ledger changes, or `HANDOVER.md` edits were made.

# SR-G4: verify overwritten-zoom provenance, flag pass 1, build the re-read pack

Work non-interactively in `~/Projects/greek-ocr-toolkit-sol-reading`, and finish in this turn. Network off. Do not run git or codex. Write only under `docs/records/harvest/sol_reading/` (`grave_full/`, `answers/grave_full/`, `tools/`), `PACK_ROOT/grave_full/` (PACK_ROOT = `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/sol_reading_packs`) and a temp dir under `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/g4_tmp/`. Pillow: `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B`.

## 1. Provenance of overwritten zoom files (scanner v4)
In context p1c1, the scan (`answers/grave_full/p1c1.scan.json`, rollout in `usage_ledger.json`) flags record 42 as an unmatched image. The lead found the cause:
- The reader built `zoom/batch1.png` (982×1110) with a literal shell/Python `magick` command from `items.jsonl` images, viewed it, then later rebuilt `zoom/batch*.png` taller (982×1410) under the same names.
- The viewed version no longer exists on disk.

Extend `tools/scan_rollout.py` (v4) with a reproduction check, run only for unmatched images:
1. Copy the reader folder's ORIGINAL pack files (`items.jsonl`, `img/`), verified against the MANIFEST, into a fresh temp dir.
2. Replay, in rollout order, every `exec_command` whose command is fully literal and touches only relative paths, up to the unmatched view. Do not replay commands that write outside the temp dir, use the network, or are not literal. Skip `answers.jsonl` writes.
3. Compare the unmatched image with the reproduced file named in the view call (bytes, or downscale as in v3).

A reproduced match clears the violation and is recorded as `match: "reproduced"`. Anything else stays a violation.

Add a test with a synthetic overwrite. Then re-scan all `grave_full` pass-1 contexts and report ok/violations per context, keeping the old scans as `.scan.v3.json`.

## 2. Pass-1 flags
Run `grave_full/tools/flag_full.py` on `answers/grave_full/p1c1..p1c4.jsonl`. A context whose scan is not ok after step 1 is excluded and reported as VOID. Write `grave_full/PASS1.{json,md}`:
- items; flags by type;
- control passes per context;
- label-grave share and Sol-grave share;
- consistency on the 17 SR-G1 overlap items.

## 3. Re-read pack
Run `flag_full.py --build-reread` to build `PACK_ROOT/grave_full/p2/` (or `p2a`/`p2b` if more than 90). Run the closure scan.

Last line: `SR-G4 READY: scans <ok list> items=<n> flagged=<n> (by type …) p2 items=<n> controls=<n> G1 overlap agree=<x>/<n>`, or `SR-G4 BLOCKED: <reason>`.

# SS4b — Q3 packs: rebuild in the scanner's replayable layout (items.jsonl + img/)

You are Sol, executing for the small-segment analysis lead. Follow-up to SS4 (read `SS/q3/SS4_RECEIPT.json`, the SS4 tools and
`SS/briefs/SS4_q3_packs.md` first; every SS4 constraint still holds). Do NOT start reading runs.

Worktree `~/Projects/greek-ocr-toolkit-sol-recut`; `SS = docs/records/harvest/collect_v3_admission/segeval1/small_segments`.

## Why
Two t01 runs were VOID (`SS/q3/answers/t01.run1_VOID.scan.json`, `t01.run2_VOID.scan.json`). Run 2 failed because the reader
overwrote zoom montages, and the canonical scanner v4.5.5 (`reproduce()` in
`~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/tools/scan_rollout.py`) seeds its replay only from manifest
entries named `items.jsonl` or under `img/`. Our packs used `cards.jsonl` + `crops/`, so the replay had no input files
(`original_files: 0`). Run 2 also used an absolute font path. The reader prompt `SS/prompts/type.md` has been updated by the
lead (items.jsonl, img/, never overwrite zoom files, no absolute paths): use it verbatim.

## Do
1. Build a fresh pack tree `PACK_ROOT/type2/<ctx>/r1/` (PACK_ROOT as in SS4) with only `items.jsonl` and `img/` per reader folder.
   `items.jsonl` rows have exactly `card_id`, `crop` (`img/<sha256-of-bytes>.png`), `google_text`. Keep the SS4 context
   assignment (same bed rows and controls per context) but issue **fresh card ids** and a fresh seeded order (seed 20261019 + 1).
   `MANIFEST.r1.json` beside each reader folder, listing `items.jsonl` and every `img/` file with sha256. Leave the old
   `PACK_ROOT/type/` tree untouched.
2. New private key `SS/q3/keys/type2.json`; keep `type.json` as is.
3. Update the SS4 tools by adding a `--layout` / bed option, or new files, so that `run_type.sh`, `run_type.py`, `map_type.py` and
   the closure check work on `type2`. Write results to `SS/q3/answers/<ctx>.*` as before (the VOID files there stay).
   Keep the old behaviour reachable, or state that it is retired.
4. **Prove replay works before the lead runs anything.** Write a synthetic rollout fixture (no codex call) in which a reader in a
   copy of one `type2` pack makes a montage under `zoom/` with a literal `magick montage img/<a>.png img/<b>.png ... zoom/g01.png`
   command, views it, then overwrites it with a second literal command and views it again. Run the canonical scanner in place on
   it, and show that both views are accepted as `reproduced`. Also show that a view built from `pwd` and a `-font /System/...` path
   are still VOID. If the canonical scanner cannot accept the overwrite case even with this layout, say so plainly and stop: do not
   modify or fork the scanner.
5. Tests: the SS4 tests adapted to type2 (public fields, no private tokens under `PACK_ROOT/type2`, content-hash names, controls
   use, ≤ 100 per context, map_type validation), plus the replay fixture test above.

## Receipt and report
`SS/q3/SS4b_RECEIPT.json`: inputs, outputs and sha256, pack hashes, closure scan, replay-fixture result, tests. Final message: the
exact commands for the lead.
Last line exactly: `SS4b READY: type2 <N> contexts, replay fixture <PASS|FAIL>, launcher <path>` (or `SS4b FAILED: <reason>`).

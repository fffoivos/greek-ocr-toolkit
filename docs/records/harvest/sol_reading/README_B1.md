# SR-B1 build and validation

Status: SR-B1b controls corrected after the lead's pixel review (2026-10-17 12:41). Yer remains at the reviewed five controls / 64 items; its mixed s003 control is explicitly re-keyed from ink. Owner39 has four accent-head options on all 43 cards. No readers were launched. The lead handles commits; no git or codex commands are used for SR-B1b.

All scripts are offline. Use the prescribed interpreter:

```
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B
```

Append a script path and its arguments:

- `tools/build_packs.py --reuse-images`: rebuild SR-B1b using saved control zooms without changing any pack PNG; omit the flag for the original render-verifying full build. Rebuild the deterministic folders, private keys, reference copies and receipt. It never deletes stale files; scans detect unrecognized leftovers. Never rebuild after readers begin. It is intended for the fixed source snapshot, not concurrent use.
- `tools/scan_packs.py [reader_dir ...]`: scan all six folders by default. Exit 1 for failures. Write manifests beside successful reader folders.
- `tools/scan_rollout.py rollout.jsonl reader_dir`: audit tool inputs plus original-file integrity. Exit 2 for any violation. `--skip-manifest` permits an absent manifest only, for the historical probe; it does not skip an existing manifest.
- `tools/map_answers.py bed reader answers.jsonl` (reader r1, r2 or r3): require a complete ordered answer set, validate fields and head/transcription agreement, undo option-letter permutations, omit controls, and write mapped answers and control checks under `answers/`. More than one control error sets `flagged=true`. Mapping does not silently exclude flagged readers.
- `tools/ledger.py add --run '<launcher JSON>' --before '<probe line>' --after '<probe line>' --bed BED --reader READER --items N`: append measured usage and refuse duplicate rollout or bed/reader. Cached input is a subset of input; reasoning is a subset of output. The total is the reported total, not a sum double-counting subsets. A launcher final rate-limit snapshot supplies the after credit balance only; an unavailable before balance is explicitly null. Optional `rate_limits_before`, or an ordered list of rate-limit snapshots, can supply the before balance. No missing measurement becomes zero.
- `-m unittest discover -s docs/records/harvest/sol_reading/tools -p 'test_*.py' -v`: run from the worktree root.

The test fixtures and mapped outputs under `validation/synthetic/` are synthetic only. They are not Sol readings and must never enter experiment scoring. The usage ledger is empty because no experiment reader was launched. Probe usage is tested in a separately labelled synthetic ledger fixture; the one recorded limit-probe line is reused as test input, not represented as a measured after snapshot.

The PNG review sheets and Markdown are written only to `keys/control_review/`. The builder rejects unexpected top-level pack entries; PACK_ROOT contains only the three beds, each with r1, r2 and their two manifests. It never copies review sheets into PACK_ROOT. The lead's existing moved private archive is outside this build's write scope. The yer review records the source override and provenance; the owner39 review records regenerated options and choices.

All owner controls use private per-record `lead_verified=true` with a pixel-review note. The public summary and old receipt still say unverified; their contradictory/stale values are retained as source evidence. Each selected R2 word crop is re-rendered from its saved padded word_box using the E0 integer 1–3x LANCZOS formula, and exact RGB equality with the original zoom is required. Public schema and E0 README/schema bytes are preserved.

The rollout scan is a conservative static audit, not a proof of OS-level isolation. It checks recorded tool inputs, literal commands and paths, checks literal strings and returned image provenance (scanner v2, SR-B2), and checks final pack contents. Arbitrarily obfuscated shell programs cannot be proved safe by this scanner. Pack scanning rejects private field names and source/line IDs; expected Greek words cannot be banned wholesale because legitimate public text and options necessarily contain them. No source keys, truth records, expected-label annotations or manifests enter the reader folders.


SR-B1b validation: `TEST_RESULTS_B1b.txt`, `PACK_SCAN_B1b.json` and `BUILD_RECEIPT_B1b.json`. The receipt binds all six manifests, keys, review files, implementation and test results. `validation/BEFORE_B1b.json` preserves the original public-file hashes and owner key for raster/form/head regression checks. Every one of the 39 source bed cards must reproduce the fixed accent-head generator before a build proceeds. Control generation uses the same `eff:owner39:options:<source_id>` seed convention, followed by the common `sol-reading:owner39:r1` A–D permutation. Choices require exact NFC equality with the expected form.

SR-B2 stage commands, scanner-v2 evidence and result scope: see `REPORT_B2.md`.

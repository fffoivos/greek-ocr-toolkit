# AU1D — capital context repacked; coordinator read pending

Fresh context: **`capital_initial_001_au1d`**, staged in `reread_contexts.json` in place of `capital_initial_001_au1c`. Three targets, ten verified controls, fresh opaque item IDs. Seed `20261017`, order seed `20261017:capital_initial_001_au1c`; item order, independently permuted option mappings, native bindings and all image bytes match AU1C exactly. Targets: `RB7-065:17:breathing`, `RB7-053:0:breathing`, `RB7-055:6:breathing`.

Reader folder: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/sf7_audit/capital/capital_initial_001_au1d`. Key: `keys/capital_initial_001_au1d.json` (SHA-256 `5cef69eb1101b4a4d3f5b8a0cc734ebc23a795d7476531148e890361e6f6ef12`). Manifest SHA-256: `24ee466eb63d2b5629bc2518a556a0f8649de0e80036f9a4a978246ccf6e9043`. No answers or attempt directory exist for this fresh context.

## Verbatim source and operational addition

W2C1 source: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/w2c1/prompts/path_addendum.md` (SHA-256 `7abf28008969a180550f4e2e28af56590d33f70d197ddd52e67373b1467b5d64`). Copied byte-for-byte to `prompts/path_addendum.md`. Quoted verbatim:

```text

# Tool-use addendum
Use only relative paths inside your current reader folder. In every view_image call, write the complete relative path as a literal string, for example "zoom/card01-v1.png". Batch several explicit calls together. Do not build file paths in loops, template strings, concatenations, pwd expressions, or store/load expressions.

Create enlargements only inside ./zoom/. Give every new image a fresh filename. Never overwrite or delete an image after viewing it; preserve all zoom versions until the run is complete. Keep image-generation commands separate from commands that read or write answers.jsonl.

These instructions govern tool use only. Apply the label-check protocol above unchanged.
```

Additionally appended exactly:

```text
do not iterate over image paths in code; call the view tool once per image, with the literal path
```

`prompts/capital.md` remains byte-identical to the original CQ1 protocol. The effective prompt is that complete base followed by the complete W2C1 addendum and the additional sentence, saved as `prompts/capital_au1d.md` (SHA-256 `efa844e4b1f6f48432a9f7072bae38e9a4bb44d12f3a55ab925ccfde2df57d9c`). The driver checks the composed prompt before any probe/read, records the effective prompt hash, and carries the same prompt binding to any triggered capital re-read. Several explicit view calls may share an orchestration call; iteration over image paths is forbidden even for a literal array. The addendum's overwrite prohibition concerns viewed images; the protocol's incremental answers-file rewrite remains unchanged.

## Preserved evidence and scanner follow-up

All prior attempts, public packs, private keys, manifests, base prompts, frame, routing and scanner binding were hash-snapshotted and verified unchanged in `au1d/context_build_receipt.json`. Previous staging is archived in `au1d/previous_reread_contexts.json`. The driver retains the archived AU1C capital context for historical receipt accounting; VOID answers supply no observations. Earlier VOID/blocked attempts remain intact.

The capital AU1C attempt remains VOID under canonical v4.5.5: unsupported view loops at records 17/34 (`const p of paths`) and 51 (JS literal array). `SCANNER_FOLLOWUP.md` records that P3 does not expand JS `for (const p of [literal array])` loops at record 51 as a candidate v4.5.6 rule. No scanner modification, rescan or verdict override was performed.

## Validation and coordinator handoff

Passed `check_au1d.py`: preserved hashes, unchanged canonical v4.5.5 binding, identical seeded order/options/pixels, fresh IDs, pack integrity, verbatim prompt composition, VOID exclusion, offline initial retry → triggered capital re-read with inherited addendum → score, and VOID/budget stop behavior. `AU1D_validation.json` records the results. `check_scoring.py` passed its synthetic scoring checks. `REREAD.sh --build-only` succeeded; `SCORE.sh` succeeded with **70/70** resolved Sol-only lines, seven unresolved, and 23 Opus-pending lines. Both shell scripts are executable and pass shell syntax checks. Scoped `git diff --check -- artifacts/sf7_rc1/audit` passed; the repository-wide check reports a pre-existing blank EOF line in unrelated `artifacts/cq4/logs/topup_reread_000.codexlog`, which was left untouched.

AU1D launched **zero reads, zero probes, zero nested Codex invocations, zero network calls** and viewed no audit images. Future execution remains `gpt-6.1-sol`, medium, network OFF. The fresh pack has not been read or scanner-qualified. The coordinator runs the capital retry first, then the existing staged accent re-read and any triggered capital re-read; existing failed attempts cannot be overwritten.

```bash
bash artifacts/sf7_rc1/audit/REREAD.sh
bash artifacts/sf7_rc1/audit/SCORE.sh
```

AU1D: done | context capital_initial_001_au1d built with addendum | next: bash artifacts/sf7_rc1/audit/REREAD.sh

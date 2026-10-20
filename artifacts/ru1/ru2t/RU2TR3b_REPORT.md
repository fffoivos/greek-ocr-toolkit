# RU2T-R3b preparation

ctx03/r2 is VOID by lead ruling. Its answers, pack, run record, and historical scans are retained. The finaliser accepts ctx03/r1 + ctx03/r3 with no r2 fallback; ctx02 retains its existing r1/r3 routing. The launcher rejects the void r2 readers.

## Fresh ctx03/r3 pack

Pack: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru2t/ctx03/r3`.

Seed: `20261017:RU2T:ctx03:r3`. The 74 original r1 items, including 7 controls, were shuffled using this seed and assigned globally fresh opaque IDs. Crop bytes, public content, private metadata, and control truth are unchanged. Manifest: `ctx03/MANIFEST.r3.json`; keys: `keys/ctx03.r3.json`. All eight pack closures pass.

The shared r3 builder now accepts ctx02 or ctx03, uses a context-specific seed, preserves existing routing, refuses assignment overwrite, verifies existing data/pack bindings, and records explicit tool rebinding with previous hashes in `RU2TR3b_RECEIPT.json`. `run_ru2t.sh` documents ctx03/r3; its launcher uses the shared accepted-reader routing.

## Existing scans (step 1 skipped)

The RU2T-R3 scan results were reused; their scan-file hashes were verified against `RU2TR3_other_scans.json`. No new real-reader scans were performed.

| Reader context | Recorded result |
|---|---|
| ctx01/r1 | ok |
| ctx01/r2 | ok |
| ctx02/r1 | ok |
| ctx03/r1 | ok |
| ctx03/r2 | fail (VOID) |

## Validation

26 RU2T fixture tests passed, including ctx03/r3 routing and ctx02/r3 regression coverage. The routing tests poison the void r2 run record, verify only r1/r3 reach the scanner and decision evidence, and verify missing r3 cannot fall back to r2. Finalisation calls in tests use temporary synthetic fixtures only. 11 canonical rollout scanner tests passed. The canonical v4.4 scanner remains unchanged.

`scripts/secondary/reading/run_ru2t.sh ru2t ctx03 r3 --dry-run` passed with gpt-6.1-sol, medium, network false. Shell syntax passed. `verification_RU2TR3b.json` records exact seeded content/private-metadata equality, globally fresh IDs, eight successful closures, preserved ctx02 routing, current bound-input hashes, and absence of r3 answers/run records.

No OCR reading, reader launch, production finalisation, network, browser/computer use, or .git writes occurred. The historical STOP and RU2T-R3 artifacts were retained.

RU2TR3b READY: other scans ctx01/r1 ok, ctx01/r2 ok, ctx02/r1 ok, ctx03/r1 ok, ctx03/r2 fail (VOID); ctx03/r3 pack closure ok; dry-run ok; finalizer r3 routing test passed

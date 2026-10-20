# RU2T-R3 preparation

ctx02/r2 is VOID by lead ruling. Its answers, run record, pack, and historical stop record are retained. The finalizer accepts ctx02/r1 + ctx02/r3 and has no r2 fallback. Launching ctx02/r2 is refused. No reader or production finalizer was run.

## Canonical v4.4 scans

| Reader context | Result |
|---|---|
| ctx01/r1 | ok |
| ctx01/r2 | ok |
| ctx02/r1 | ok |
| ctx03/r1 | ok |
| ctx03/r2 | FAIL |

ctx03/r2 fails with 47 violations: 17 absolute path outside reader_dir, 30 unresolvable load expression. Full records are in `answers/ctx03.r2.scan.json`. The scanner remains canonical and unchanged. No acceptance or void ruling for ctx03/r2 is inferred; it remains a blocker for later finalization.

## ctx02/r3

Pack: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru2t/ctx02/r3`. Seed: `20261017:RU2T:ctx02:r3`. 74 items including 7 controls. The r1 items were shuffled using this seed, assigned globally fresh opaque IDs, and byte-copied with unchanged private item metadata and control truth. Manifest: `ctx02/MANIFEST.r3.json`; private keys: `keys/ctx02.r3.json`. All seven pack closures pass.

`build.json` retains original data/pack bindings, adds r3 bindings, and explicitly rebinds changed tooling. The receipt retains previous tooling hashes. The pack scanner now accepts an explicit r3 order seed while keeping its legacy RU1 default. The canonical rollout scanner was not changed.

## Validation

25 RU2T fixture tests and 11 canonical rollout scanner tests passed. The routing fixture poisons the void r2 run record, verifies only r1/r3 are scanned and included in decision evidence, checks the seeded content and unchanged metadata, and verifies missing r3 cannot fall back to r2. Finalizer execution was confined to temporary synthetic fixtures.

`scripts/secondary/reading/run_ru2t.sh ru2t ctx02 r3 --dry-run` passed with gpt-6.1-sol, medium, network false. Shell syntax passed. No network, browser, computer use, OCR reading, production finalization, or .git writes occurred.

RU2TR3 READY: other scans ctx01/r1 ok, ctx01/r2 ok, ctx02/r1 ok, ctx03/r1 ok, ctx03/r2 fail; ctx02/r3 pack closure ok; dry-run ok; finalizer r3 routing test passed

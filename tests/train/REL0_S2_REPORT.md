# REL0-S2 — local implementation and validation receipt

28 October 2026. No network, SSH, Git commands/metadata changes, remote processing, Hub operations, commits or publication were performed. No files under `docs/programme_20261025/TRAIN_FULL_v1/`, `scripts/release_v0/` or `tests/release_v0/` were edited.

Implemented:

- Maintained Stage C trainer in `greekocr/train/`; import-only mapping and original SHA256 values in `CONSOLIDATION.md`, complete historical comparison in `LEGACY_COMPARISON.diff`; `_vendor/train` aliases the same module objects. Compact model, heads, preprocessing, greedy decoder and codec implementations are preserved.
- Exact fp32 checkpoint export with config/codec SHA bindings and tensor readback; actual Docling release-directory loading for all three widths, strict key/shape/dtype checks, NFD head / NFC output. Legacy serving remains compatible.
- `scripts/release_v0_export/COMMANDS.md` and `verify_dev.py` prepare the actual final-artifact gate on Clariden. No real-weight parity is asserted locally.
- `VERSIONS.md` records ten supported OCR rounds, every named candidate disposition including E4 wave1b/O-series, and per-tool generation histories. Historical uncertainties remain explicit; some non-OCR component counts remain unresolved rather than invented.
- `MODELS.json` contains only ×1 attempt014 h14, ×1.5/×2 attempt013. Package payloads, producing commit/source state, upstream trainer/patch, original code file identities, PLAN/config/adopted-config identities are populated; final release/Hub/weight/dataset/selected-score fields are null with TODOs.
- README introduces release targets in pipeline order, emphasizes modern/polytonic Greek and other scripts, and preserves the useful taxonomy/reference material below.
- Public inventory/credential-location scan, complete excluded bulk-receipt manifest and fixture tests. Full local review TSV is over 5 MB; the receipt selects ≤4 MB review parts for Git. Inventory metadata omits itself to avoid circular hashes. It is a working-tree review aid, not proof of public history hygiene or remote receipt custody.

## Checks

Executed with `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, pytest cache disabled, and named basetemps under `/private/tmp/rel0-s2-pytest-*`. The system Python had an unrelated installed `tests` package shadowing this checkout; the existing project environment resolved that without repository changes.

Final touched-suite invocation:

```
python -m pytest tests/train tests/deploy tests/recogniser \
  tests/test_docling_contract.py tests/test_docling_orientation.py tests/test_docling_tables.py \
  tests/test_custody.py tests/test_real_annotate_score.py tests/test_warmstart_readers.py \
  tests/test_data_root.py tests/labelfix/test_constraints.py \
  tests/test_provenance_cli_api.py tests/test_ops_deploy_sources.py \
  -q -p no:cacheprovider --basetemp=/private/tmp/rel0-s2-pytest-final-all \
  --junitxml=tests/train/REL0_S2_TESTS.xml
```

**1,360 passed; 16 failed; 6 skipped** in 18.07 seconds. All 16 failures are old byte-hash assertions in `tests/test_provenance_cli_api.py` for the deliberately replaced legacy trainer and maintained plugin files. Its remaining provenance checks pass. Four existing historical skips plus two absent optional research fixtures account for the six skips. One existing Docling deprecation warning remains. This is not a green overall suite.

The **40 new tests pass** independently (`REL0_S2_NEW_TESTS.xml`). The separate runtime/import/Docling/custody suite passed **267 / 2 skipped** before the final added archive-member fixture; the final combined run above includes that fixture too. New tests cover seeded sealed-vs-maintained fp32 logits/decodes at ×1/×1.5/×2, complete codec round-trip, export/readback/actual lazy Docling engine load, same trainer/serving predictions, NFC output, tamper/strict-state rejection, a byte-bound tiny dev-pool gate, nonignored + tracked-ignored candidates/index v2/3/4, >5 MB exclusion, credential diagnostics, raw renamed/archived Google responses, caches/symlinks, complete ignored bulk receipt custody, and split inventory receipts.

**Sealed package integrity:** Stage C payload remains SHA256 `7e8a497f21527b90bfd758fa8afceeabcc4b329aa31dc08535a2ce0472dde1e6`; all **93** manifest files matched their original byte counts and SHAs. No numerical/preprocessing/codec edits were made to the trainer. Tiny random-init fixtures are not evidence of real-weight parity or pipeline accuracy.

## Outstanding scope boundaries

`GAPS.md` records the out-of-scope historical origins/test contract conflict, unresolved version histories, optional historical adapter closure, wheel package-data declaration, stored AMP versus required fp32 parity, and publication review/custody. The coordinator must handle the origins ledger/test update and final version/tag disposition in its own scope. Package data declarations are also outside this run's allowed files. The Clariden step-6 real-weight gate and final three-width release barrier remain pending by design.

The completed pytest basetemps created by this run were removed after the passing new/runtime checks; XML evidence is retained here. Public inventory row/count/hash details are in `scripts/release_v0_publish/PUBLIC_INVENTORY.receipt.json`; rerun after concurrent writers settle.

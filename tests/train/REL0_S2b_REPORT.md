# REL0-S2b — follow-up implementation and validation receipt

28 October 2026. Scope: provenance contract (Checkpoint A3), package data (A5),
and explicit exclusion of unavailable historical adapters (A4). No Git commands,
Git metadata changes, network requests, sealed-package edits or remote operations.
The working-tree follow-up has no assigned producing commit; original recorded
source commits remain intact.

- `greekocr/_vendor/origins.json`: preserves all 1,108 original records/fields,
  with a canonical SHA256 pin in the test. Seventeen superseded records are
  historical and bidirectionally referenced by 40 new live records. Live records
  verify current bytes, CONSOLIDATION.md SHA256, and sealed source SHA256 where
  applicable. Unrelated provenance, logic-hash, static-inventory and API/CLI
  assertions remain; the obsolete historical mix skip is removed.
- `greekocr/train/mix.py`: metadata validation, row loading, direct assembly and
  replay-plan loading reject codec_recovery, label_versions, matched_replay and
  s1_selection with MixError naming the absent adapter and sealed-package path.
  No adapter was fabricated. Exact sealed-to-maintained mix hunks and release
  scope are documented in CONSOLIDATION.md. Numerical model, preprocessing,
  decoder, codec, inference and export code were not changed by this follow-up.
- `pyproject.toml`: greekocr.train package-data explicitly ships codec JSON,
  mix.schema.json, CONSOLIDATION.md and LEGACY_COMPARISON.diff. The comparison is
  documentation, not a runtime dependency.
- `tests/train/test_historical_modes.py`: 19 cases cover metadata/full validation,
  row loading, direct recovery/replay assembly, replay-plan loading and CLI errors,
  including rejection before recipe/custody access.
- `tests/train/test_wheel_package.py`: one integration case builds from a fresh
  temporary source copy using the available setuptools backend (no downloads),
  verifies all four resources byte-for-byte in the wheel, installs with
  pip --no-index --no-deps into a fresh venv, and uses python -I outside the
  checkout to verify installed-module identity and every codec atom's round-trip.
  Two additional ledger-contract tests and 40 live-file parametrizations are
  included in the provenance suite.

## Validation

Interpreter: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`.
PYTHONDONTWRITEBYTECODE=1; pytest cache disabled.

```sh
python -m pytest tests/train tests/deploy tests/recogniser \
  tests/test_docling_contract.py tests/test_docling_orientation.py tests/test_docling_tables.py \
  tests/test_custody.py tests/test_real_annotate_score.py tests/test_warmstart_readers.py \
  tests/test_data_root.py tests/labelfix/test_constraints.py \
  tests/test_provenance_cli_api.py tests/test_ops_deploy_sources.py \
  -q -p no:cacheprovider --basetemp=/private/tmp/rel0-s2b-pytest-final-all \
  --junitxml=tests/train/REL0_S2b_TESTS.xml
```

**1,439 passed, 0 failed, 5 skipped, 1 existing Docling deprecation warning**
in 19.73 seconds. Skips: three unchanged historical bench bindings and two
absent optional research fixtures. Includes seeded sealed-versus-maintained fp32
logit/decoder equivalence at widths ×1/×1.5/×2, release export/readback and actual
Docling loading, plus ordinary custody/training compatibility checks. Tiny
fixtures do not establish real-weight release parity; that existing gate remains
outside this follow-up.

Focused provenance/mode run: **1,170 passed / 3 skipped**
(`REL0_S2b_FOCUSED_TESTS.xml`). Independent wheel run: **1 passed**
(`REL0_S2b_WHEEL_TESTS.xml`). The full suite reran that wheel check; the final wheel
identity and per-resource bytes/SHAs are in `REL0_S2b_WHEEL.receipt.json`.
Final wheel: `greek_ocr_toolkit-0.1.0-py3-none-any.whl`, 1,511,589 bytes, SHA256 `a5e5b3a9c7f36a73ad64b0fc803e01ae7a9d249e888a3f29b539275acab01060`.
Installed codec: v2.1, 266 classes, all 265 nonblank atoms round-trip.

All three named passing pytest basetemps were deleted and verified absent,
including both temporary wheel builds, copied sources and isolated venvs. Only
XML and JSON evidence remains in tests/train. Temporary ledger-generation inputs
were also removed.

## Documentation and final inventory

GAPS.md marks A3/A5 resolved and A4 scoped out. Its new A8 records the missing
maintained-namespace entries in the legacy static docs/INVENTORY.md; that document
was not edited. REL0_S2_REPORT.md remains the historical earlier-run receipt.

After the completed source/docs/test evidence and cleanup, rerun:
`python scripts/release_v0_publish/inventory.py`.
The generated PUBLIC_INVENTORY.receipt.json binds the complete local TSV, selected
≤4 MB review parts and credential-location diagnostics. This scan remains a
working-tree review aid; public-history review and remote receipt custody remain
coordinator-owned (A7). Its generated metadata omits itself to avoid circular hashes.

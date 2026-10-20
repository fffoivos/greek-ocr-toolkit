# CLEAN3B verification results

New resolver and read-only mover tests:

```sh
PYTHONDONTWRITEBYTECODE=1 arch -x86_64 /usr/local/bin/python3 -m pytest -q -p no:cacheprovider tests/test_data_root.py docs/cleanup_20261019/data_out/test_mover_v2.py
```

Result: **24 passed in 1.49s**. Includes repo precedence, external-root fallback, receipt errors, invalid paths, dangling links, import-cycle prevention, source/hash/type conflicts, destination skip behavior and symlink-ancestor rejection. Mover transfer/execute/rollback paths were not run; no test moves data files.

Additional pre-move checks (same interpreter, four existing files): `tests/test_ops_deploy_sources.py tests/test_custody.py tests/test_lqb.py tests/test_collection_outputs.py` — **96 passed, 17 failed in 23.81s**. Fourteen failures reached SciPy extension imports with an arm64/x86_64 mismatch; three concerned missing historical budget ledgers or `docs/records/harvest/harvest_big/collection/SHEETS.md`. The separate verify-suite collection also stopped at the SciPy architecture mismatch. No environment repair or existing-test edit was made by CLEAN3B. This does not establish a green broad suite or post-move behavior.

The native arm64 Python initially encountered x86_64 Pillow/Torch installations through existing package/global-test-fixture imports. The x86_64 interpreter runs the new tests. Resolver import was made standard-library-only to avoid the new receipt/vendor cycle, and the subprocess test checks that dependency boundary explicitly.

Read-only `git apply --check CLEAN4T_READER_HANDOFF_v2.diff` passed against the observed concurrent tests. Read-only reverse check of LIVE_READER_PATCHES_v2.diff also passed against the applied source edits. These commands do not apply patches or change the index.

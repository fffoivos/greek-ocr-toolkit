# SYNC2 additive frozen-tree test

Branch: `opus/cleanup-1`; inspected HEAD: `edf9c8786a10d0f1ce6aa1991bb3e45e84cd0747`.
Reference: `ce2f889d9084f850d07878479bcc02f49f0b6d58` (pinned SF6c).

All 282 existing reference files are present and byte-identical, including `greekocr/__init__.py` and all of `greekocr/labelfix/`.
All 16 policy paths are unchanged. Policy digest: `6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406` (`6f62925a`).

Only the test code was changed; no package changes, network calls, or repository `.git` writes were made.

Rule (a): require every reference file with its original SHA-256.
Rule (b): allow extras only beneath `greekocr/recogniser/` (CU3) or `greekocr/adjudicate/` (CU4), and only when that directory does not exist in the reference.
Extras beneath existing reference directories, or any other new directory, fail.

## Every extra file (16)

| File | Admitting rule |
|---|---|
| `greekocr/adjudicate/README.md` | (b): allowlisted reference-absent `greekocr/adjudicate/` |
| `greekocr/adjudicate/__init__.py` | (b): allowlisted reference-absent `greekocr/adjudicate/` |
| `greekocr/adjudicate/deck.js` | (b): allowlisted reference-absent `greekocr/adjudicate/` |
| `greekocr/adjudicate/deck.py` | (b): allowlisted reference-absent `greekocr/adjudicate/` |
| `greekocr/adjudicate/owner_sheet.css` | (b): allowlisted reference-absent `greekocr/adjudicate/` |
| `greekocr/adjudicate/owner_sheet.js` | (b): allowlisted reference-absent `greekocr/adjudicate/` |
| `greekocr/adjudicate/owner_sheet.py` | (b): allowlisted reference-absent `greekocr/adjudicate/` |
| `greekocr/adjudicate/protocol.py` | (b): allowlisted reference-absent `greekocr/adjudicate/` |
| `greekocr/adjudicate/score.py` | (b): allowlisted reference-absent `greekocr/adjudicate/` |
| `greekocr/recogniser/README.md` | (b): allowlisted reference-absent `greekocr/recogniser/` |
| `greekocr/recogniser/__init__.py` | (b): allowlisted reference-absent `greekocr/recogniser/` |
| `greekocr/recogniser/alignment.py` | (b): allowlisted reference-absent `greekocr/recogniser/` |
| `greekocr/recogniser/api.py` | (b): allowlisted reference-absent `greekocr/recogniser/` |
| `greekocr/recogniser/cache.py` | (b): allowlisted reference-absent `greekocr/recogniser/` |
| `greekocr/recogniser/evidence.py` | (b): allowlisted reference-absent `greekocr/recogniser/` |
| `greekocr/recogniser/guard.py` | (b): allowlisted reference-absent `greekocr/recogniser/` |

## Validation

Focused run: **15 passed**. Synthetic cases cover modified reference files (including root `__init__.py`), missing reference files, additions within `labelfix` (including a nested package), root additions, unlisted packages, lookalike prefixes, both permitted new subpackages, and rejection when an allowlisted directory already exists in the reference.

Interpreter: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python` (the merge-harness interpreter).
The initial system-Python attempt stopped during collection because its NumPy extension is x86_64 while Python runs as arm64; no tests ran in that attempt.

Full-suite command (offline fixture blocks network; no inherited selection flags):

```sh
GIT_OPTIONAL_LOCKS=0 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTEST_ADDOPTS= PYTHONOPTIMIZE= /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m pytest --junitxml=artifacts/sync2/suite.xml > artifacts/sync2/suite.log 2>&1
```

Full suite: **4,869 passed, 19 skipped, 5 failed, 6 errors** in 242.41 seconds. The five failures exactly match the known set (`test_collection_outputs`: 3; `test_provenance_cli_api`: 2). Five errors exactly match the known `test_apply_clean` set.

One additional sandbox error prevents the requested "pre-existing only" result: `tests/labelfix/test_capture.py::test_server_appends_each_decision_and_serves_static` fails during fixture setup because `socket.bind` raises `PermissionError: [Errno 1] Operation not permitted`. The test file is unchanged from SF6c; `greekocr/labelfix/deck_serve.py` is among the 282 byte-identical reference files. An isolated rerun reproduces the same denial (**2 passed, 1 error**). No test was skipped or changed to bypass the restriction. Running this loopback HTTP test requires an environment that permits local socket binding.

Receipts: `artifacts/sync2/suite.log`, `artifacts/sync2/suite.xml`, and `artifacts/sync2/capture_retry.log`. The XML and failure summaries were checked against the exact known node IDs plus this one sandbox error. `git diff --check` passes.

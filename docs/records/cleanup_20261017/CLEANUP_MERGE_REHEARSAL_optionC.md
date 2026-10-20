# MR-C rehearsal report

Ruling C is implemented in this scratch worktree only. Option A's 13 archive
moves were reversed in the working tree: ten drivers, two configurations and
one test are restored as detailed below. No commit, staging, ref change, network
access, deployment,
Slurm invocation or other-worktree mutation was performed.

Starting branch tip: `e8477c073529179b4f4b8942402caf3f087ac842`
(`rehearsal/merge-20261017`). Read-only comparison reference:
`opus/spellcheck` = `ce2f889d9084f850d07878479bcc02f49f0b6d58`
at verification. The pre-existing untracked `docs/records/briefs/MR_C_recompose_ext.md`
was read and left unchanged.

## Adapter and provenance

New non-hashed module: `scripts/labelfix/clariden/l1r_recompose_ext.py`.
The source is `docs/records/archive/l1f_hashed_paths_20261017.patch`
(SHA-256 `c0e98c03842538d61168bfb5fe5b98d3a2f61b1c0d59092e8920761ba8359e25`),
applied to copies of the two SF6c files under `/private/tmp/mrc_patch_source/`.
The patch was never applied to a live hashed path. The s8 patch is not needed:
the l1f patch supplies the complete cumulative implementation.

- From patched `l1_common.py`: `overlay`, `_overlays`, `release`. These preserve
  the shared gate consumer and add `composed_text`, decision `parts`, and the
  keyword-only `verified_source_sha256` optimization. Existing canonicalization,
  statuses, label hashing, hold classification and row/file helpers are imported
  from the frozen modules. No monkeypatching or mutation of frozen globals.
- From patched `l1r_recompose.py`: `load`, `digest`, `atomic_json`,
  `separate_output`, `verify_inputs`, `decision_record`, `validate_release`,
  `_initialise`, `code_sources`, `_shard`, `merge_shards`, `recompose`, `main`.
  These include receipt-DAG validation, sharded atomic reuse/merge, source/code
  binding, L1F joins, `--config`, `--verify-only`, and `--audit-decisions`.
- All 16 transplanted function bodies match the reconstructed patch by AST
  comparison; only imports/module placement differ. Gate composition remains
  `release_gate.compose_runtime`. No reverse import from a hashed file exists.

## Restored consumers

Restored from `docs/records/archive/l1r_line_20261017/` to their original paths:

- `scripts/labelfix/clariden/`: `l1f_job.sbatch`, `l1f_mock_check.py`,
  `l1f_preflight.sh`, `l1f_run.py`, `l1r3_preflight.sh`, `l1r4_job.sbatch`,
  `l1r4_mock_check.py`, `l1r4_preflight.sh`, `l1r_job.sbatch`, `l1r_mock_check.py`.
- `config/l1f_job.json`, `config/l1f_mock.json` (byte-identical restoration).
- `tests/labelfix/test_l1f.py` (byte-identical restoration).

Recomposition imports/CLI paths in the restored consumers now reference the
extension. `l1f_mock_check.py` and `l1r4_mock_check.py` use its overlay adapter.
`l1r_mock_check.py` no longer overrides the expected frozen `l1_common` hash with
the l1f hash: it checks the genuine SF6c source bytes. `test_l1r.py`,
`test_l1r2.py`, `test_l1r3.py` import the extension; their assertions are unchanged.
The archive README now records the restoration. Historical deployment receipts
and absolute paths in configurations remain provenance, not a new deployment.

## Frozen boundaries

`git diff opus/spellcheck -- <all 16 policy_binding sources>`: **empty**.
`git diff opus/spellcheck -- greekocr/`: **empty**.
Actual digest: **`6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406`**.

`tests/labelfix/test_policy_frozen_after_merge.py` checks the digest and exact
16-path diff, scans imports in all 16 source ASTs for the extension, and compares
the sorted `(path, SHA-256)` list for all tracked/nonignored `greekocr/` files
against a read-only Git archive of the pinned spellcheck reference. All pass.

## Validation

All commands use the requested toolkit venv Python, `PYTHONPATH=$PWD`, and
`PYTHONDONTWRITEBYTECODE=1`; pytest uses `python -m pytest`.

| Scope | Before | After |
|---|---|---|
| `test_l1r{,2,3,4}.py` | 69 passed, 15 failed | 84 passed, 0 failed |
| Above + restored `test_l1f.py` + three freeze tests | L1F archived; freeze tests absent | 98 passed, 0 failed |
| Full `tests/` | 4,779 passed, 20 failed, 6 errors, 19 skipped | 4,808 passed, 5 failed, 6 errors, 19 skipped |

Before/after targeted logs are in `docs/records/cleanup_20261017/MR_C_evidence/`. Four formerly broken
imports (`l1f_run`, `l1f_mock_check`, `l1r_mock_check`, `l1r4_mock_check`) pass.
The new CLI's `--help` exposes the config/verification/audit flags. All six
restored shell/sbatch files pass `bash -n`; none was executed.

Baseline full suite: **4,779 passed, 20 failed, 6 errors, 19 skipped** (128.80 s).
The 20 failures are the 15 L1R failures plus the five pre-existing failures.
The six errors include one additional sandbox limitation beyond the brief:
`tests/labelfix/test_capture.py::test_server_appends_each_decision_and_serves_static`
cannot bind its local HTTP server (`PermissionError: [Errno 1] Operation not permitted`).
It occurs in the baseline, so it is not introduced by MR-C.

The pre-existing failures/errors are recorded separately from L1R:

- `tests/test_collection_outputs.py`: 3 failures (absent collection budgets,
  frozen-wave budget JSONL, and collection `SHEETS.md`).
- `tests/test_provenance_cli_api.py`: 2 failures (vendor inventory excludes
  `parliament_resolution.json`; README example line-count assertion).
- `tests/test_apply_clean.py`: 5 setup errors (missing
  `docs/records/harvest/collection/v2/admitted_all_v2.jsonl`).
- `tests/labelfix/test_capture.py`: 1 setup error (sandbox socket bind denial).
- `test_deadline_terminates_inflight_pool`: passes in both full-suite runs.

After full suite: **4,808 passed, 5 failed, 6 errors, 19 skipped** (152.33 s).
The after failure/error node set is exactly the baseline set minus the 15 L1R
failures: **zero new failures or errors**. The 29 additional passes comprise
15 repaired L1R cases, 11 restored L1F cases and 3 new freeze checks. No xfails
were added; fallback A was unnecessary. Both full runs exit 1 solely for the
remaining baseline failures/errors. See `suite_before.log`, `suite_after.log`
and `verification.json` in `docs/records/cleanup_20261017/MR_C_evidence/`.

## Diff against starting branch tip

Unstaged `git diff --stat HEAD` (Git excludes restored/new untracked paths until
the lead stages them):

```text
 docs/records/archive/l1r_line_20261017/README.md           |  16 +-
 docs/records/archive/l1r_line_20261017/config/l1f_job.json |  51 ---
 .../archive/l1r_line_20261017/config/l1f_mock.json |  41 --
 .../scripts/labelfix/clariden/l1f_job.sbatch       |  33 --
 .../scripts/labelfix/clariden/l1f_mock_check.py    |  96 -----
 .../scripts/labelfix/clariden/l1f_preflight.sh     |  30 --
 .../scripts/labelfix/clariden/l1f_run.py           | 438 ---------------------
 .../scripts/labelfix/clariden/l1r3_preflight.sh    |  36 --
 .../scripts/labelfix/clariden/l1r4_job.sbatch      |  30 --
 .../scripts/labelfix/clariden/l1r4_mock_check.py   |  84 ----
 .../scripts/labelfix/clariden/l1r4_preflight.sh    |  57 ---
 .../scripts/labelfix/clariden/l1r_job.sbatch       |  28 --
 .../scripts/labelfix/clariden/l1r_mock_check.py    |  95 -----
 .../l1r_line_20261017/tests/labelfix/test_l1f.py   | 113 ------
 tests/labelfix/test_l1r.py                         |   2 +-
 tests/labelfix/test_l1r2.py                        |   2 +-
 tests/labelfix/test_l1r3.py                        |   2 +-
 17 files changed, 9 insertions(+), 1145 deletions(-)
```

Including untracked task files, a read-only `git diff --no-index --stat
--find-renames` between temporary HEAD/current snapshots gives the following
implementation stat (before this report and evidence logs; excludes the
pre-existing brief). No temporary Git index was created:

```text
 .../config/l1f_job.json                            |   0
 .../config/l1f_mock.json                           |   0
 .../docs/archive/l1r_line_20261017/README.md       |  16 +-
 .../scripts/labelfix/clariden/l1f_job.sbatch       |   0
 .../scripts/labelfix/clariden/l1f_mock_check.py    |   2 +-
 .../scripts/labelfix/clariden/l1f_preflight.sh     |   0
 .../scripts/labelfix/clariden/l1f_run.py           |   2 +-
 .../scripts/labelfix/clariden/l1r3_preflight.sh    |   4 +-
 .../scripts/labelfix/clariden/l1r4_job.sbatch      |   4 +-
 .../scripts/labelfix/clariden/l1r4_mock_check.py   |   4 +-
 .../scripts/labelfix/clariden/l1r4_preflight.sh    |   4 +-
 .../scripts/labelfix/clariden/l1r_job.sbatch       |   2 +-
 .../scripts/labelfix/clariden/l1r_mock_check.py    |   7 +-
 .../labelfix/clariden/l1r_recompose_ext.py}        | 672 +++++++++++++++++++++
 .../tests/labelfix/test_l1f.py                     |   0
 .../{before => after}/tests/labelfix/test_l1r.py   |   2 +-
 .../{before => after}/tests/labelfix/test_l1r2.py  |   2 +-
 .../{before => after}/tests/labelfix/test_l1r3.py  |   2 +-
 .../labelfix/test_policy_frozen_after_merge.py}    |  49 ++
 19 files changed, 743 insertions(+), 29 deletions(-)
```

MR-C READY: hashed diff empty yes; digest 6f62925a yes; L1R failures 15 -> 0; new failures 0; suite 4808/5

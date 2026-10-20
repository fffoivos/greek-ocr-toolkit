# ASTRA-CLEANUP3 — scoped certification, cycle 3

Reviewed repository: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra3`, detached HEAD **`ee77f07f3e8c6cb671c09f0bdd85c0165389d3c9`**. Scope: cycle-2 H1 and M1, their CLEAN7 fixes, and regressions introduced since `3b4090bf9`. Earlier cleared conclusions stand. This review independently inspected the source and Git objects, built a fresh archive, ran the full suite, and recomputed the numbers below. It did not modify the repository or launch detached jobs.

**CERTIFIED FOR MERGE within the scoped review: H1 and M1 are cleared; no BLOCKER or HIGH remains. An ancillary LOW test-harness limitation is logged below.**

During verification, `cleanup/20261019` advanced to `22b6b25d1c9dcc71d12805248d0dbdc24444d350`. Its only difference from the tested HEAD is two changed lines in `docs/programme_20261019/NIGHT_STATE.json`, recording this review's launch. No tested code, tests, package, or policy changed. The full-suite result belongs specifically to `ee77f07f3`. See [concurrent branch delta](concurrent_branch_delta.patch).

## Findings, most severe first

No new BLOCKER, HIGH, or MEDIUM finding.

### [LOW] L2 — Ancillary readout test writes its receipt beside the source

Location: `docs/records/harvest/census05/readout/test_census_readout.py:181`.

An additional, explicitly selected readout run from the read-only archive returned:

```text
1 failed, 11 passed, 8 deselected in 0.70s
```

`test_spooled_job` successfully executes the job, verifies its exit code, invocation, working directory, and **200-row** readout, then raises `PermissionError` when writing `HERE/'spool_receipt.json'`. The write already exists at `3b4090bf9:177`; this is an inherited limitation in a touched file, not a new production regression. These documentation tests are outside the default `testpaths = ["tests"]` suite.

**Failure scenario:** a certifier explicitly running this ancillary test against read-only source receives a failure after the functional checks succeed.

**Fix:** write this diagnostic receipt under `tmp_path` or an explicitly configured scratch output directory. Log/defer this LOW; it does not reopen the required full-suite gate.

For independent functional verification, the same three files—test module, readout implementation, and job script—were copied byte-for-byte into writable scratch, with the unchanged package available through a read-only source link. No assertions were edited. The same selection returned:

```text
12 passed, 8 deselected in 0.43s
```

Evidence: [original failure](readout_patch.log), [unchanged copy hashes](readout_portable_copy.json), [scratch result](readout_portable.log), [JUnit](readout_portable.xml).

Cycle-2 L1 documentation drift remains previously logged and outside the two reopened findings. No automatic fix loop was started.

## Cleared and verified-good

### H1 — Fresh-checkout test gate: CLEARED

The source was exported with **`git archive HEAD | tar -x -C <scratch>/fresh`**, without overlays. All archive files and directories were made read-only. At launch, the archive had no `.git`, no predictor `target/`, and the configured scratch build directory did not exist. `GREEK_OCR_PREDICTOR` was unset.

The full suite ran from the archive root with:

```text
PYTHONDONTWRITEBYTECODE=1
GREEK_OCR_DATA_ROOT=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-data
GREEK_OCR_BUILD_DIR=<scratch>/build
python -m pytest -q -p no:cacheprovider --junitxml=<scratch>/pytest_fresh.xml
```

The interpreter was `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`. As documented for archive verification, `GIT_DIR` referenced existing source metadata read-only, `GIT_WORK_TREE` selected the archive, and `GIT_OPTIONAL_LOCKS=0`. `CU3_CACHE_ROOT` selected three hash-verified scratch copies of the existing optional recognizer fixtures; they were not regenerated. The complete invocation/environment is in [suite_run.json](suite_run.json), and fixture custody is in [golden_cache_receipt.json](golden_cache_receipt.json).

**Raw full-suite summary, exit 0:**

```text
7312 passed, 101 skipped, 9 warnings, 63 subtests passed in 348.21s (0:05:48)
```

**Gate: 0 failed / 0 errors.** JUnit independently records **7,476 cases**, including the 63 subtests, **101 skips**, **0 failures**, and **0 errors**. The one-pass increase and one-skip decrease against CLEAN7's receipt is exactly the loopback capture test, which executed here. No predictor-dependent case was skipped. See [raw log](pytest_fresh.log), [JUnit](pytest_fresh.xml), and [skip comparison](skip_delta.json).

Firsthand resolver checks:

- `greekocr/harvest/predictor_path.py:35–64` resolves an explicit executable first, an existing scratch binary second, and an existing in-repo binary third. When none exists, it builds **debug and release** into scratch using **`cargo build --offline --locked --target-dir …`**. Invalid explicit paths and build failures raise errors.
- The real fresh-suite build produced [BUILD_RECEIPT.json](build/BUILD_RECEIPT.json). Its lockfile SHA256 is `c44e7f2a151bb76a3b24d03c182766e117f84c039eb97b0afb9e682fdcb843f4`; compiler is **rustc 1.96.1 (31fca3adb 2026-06-26), Homebrew**. Both recorded executable hashes were independently checked.
- A separate subprocess with no Cargo on PATH and no available binary exited **1** with `RuntimeError: Frozen predictor is missing and cargo is unavailable`; it neither skipped nor created a build directory. Debug/release outputs were byte-identical for **20 requests across five model groups**. See [resolver probe](resolver_probe.json).
- All **six resolver tests** passed. The affected native test files passed **11 curve + 6 deskew + 34 gate + 12 small = 63 tests**, with zero skips. Both S4-versus-S3 native identity cases, all three straight-curve identity cases, and all four S2-versus-S1 orientation identity cases executed and passed.
- All **28 frozen SEG baseline files** are byte-identical to cycle 2. Their saved bytes and identity assertions were not weakened. See [bindings audit](bindings_audit.json).
- [Grep results](predictor_grep.txt) show **zero hard-coded checkout predictor destinations in active native tests, S1–S5 replay/report adapters, or the parity CLI**. Literal strings remain intentionally in the AST compatibility matcher and six frozen-baseline lines; the loader redirects the latter in memory. Synthetic resolver tests construct temporary legacy targets. Clariden's five `runtime/rust-target/release` references remain explicitly bound deployment-runtime paths, outside this fresh-checkout test path. A blanket claim that no `target/` text exists anywhere would be false.

### M1 — Behavioral scope wording: CLEARED

The review brief's mandate item 5 at `docs/ocr_program_2026-10-06/briefs/ASTRA_CLEANUP_review_brief.md:16` now names **SEG10, PIPE032, CROPS3/CROPS4, BENCH02D–I, SPLIT2, CENSUS05-R, and census README packaging**, plus compatibility/test infrastructure and custody/process work. It preserves the merged-versus-adjacent distinction and explicitly qualifies split-input and staging effects.

The requested base-to-HEAD core comparison contains **290 paths, 1,488 insertions, and 833 deletions**. A recorded AST screen identifies **257 Python files** differing only after removal of docstrings and normalization of the declared documentation-path/data-reader adaptations; the remaining **33 paths** were inspected directly. This screen is a review aid, not a claim of unconditional byte or behavior parity. Evidence: [stat](core_stat.txt), [full core diff](core_diff.patch), [classification](scope_classification.json), [remaining diff](scope_residual.patch).

The substantive pipeline decision changes are exactly the disclosed exceptions:

- **SEG10:** common **0.30–2.00** band, digit/separator/digit automatic-negative recognition, and union of configured held-out crop hashes.
- **PIPE032:** configured out-of-scope routes bypass their correction-result obligation, preserve explicit `not_applied_out_of_scope` evidence and unedited text for that route; content repair cannot be excluded. All **12 route-scope tests** passed.

CROPS3 changes staging selection/disk deferral; SPLIT2 changes bound input assignments and can therefore change eligibility. Benchmark sampling and census readout do not rewrite pipeline decisions. CLEAN7 resolves/builds the same frozen predictor and adjusts test paths. The new census package applies the already disclosed `routes_out_of_scope=['polytonic']`; it does not introduce another decision rule. The scope list is complete for the requested decision-rule audit.

### Commits since cycle 2 — no merge-blocking regression found

The review interval contains **20 commits**, **318 added files**, and **33 modified files**. Outside tests and documentation, the only new/changed files since `3b4090bf9` are the predictor resolver and parity-CLI resolver adaptation. The current pipeline decision modules, native implementation, Rust predictor source, and tool-version manifest are unchanged since cycle 2.

Independent census checks:

| Check | Result |
|---|---:|
| Deployment manifest entries verified after mapping the outer archival path | **167/167** |
| Packaged source entries matching their recorded `3b4090bf9` Git blobs and SHA256 | **154/154** |
| Deployment/source hash failures | **0 / 0** |
| Recomputed package ID | **17b0eb1ca7fe81a7** |
| Saved-evidence policy replay: exact verdict and reason | **150/150 + 888/888** |
| Native images processed by this additional policy replay | **0** |
| Selected readout functional checks in unchanged writable copies | **12 passed** |

The readout patch replaces the fixed `0.3` expectation with explicit `--expect-pipeline-version`; job scripts derive it from the bound package. The direct API still rejects missing, empty, or inconsistent versions. It only reads published decisions and writes a separate report. The additional tests cover expected-version acceptance/rejection, mixed versions, publication pinning, held-out protection, and the spooled invocation. No census or scheduler job was submitted here. These checks do not certify a current remote deployment or a production census outcome.

Evidence: [package bindings](bindings_audit.json), [policy replay](census_policy_parity.json), [cycle-3 source diff](cycle3_diff.patch), [commit log](commit_log.txt).

### Read-only preservation and retained size gate

Both original source and fresh archive retained exactly **45,730 files / 2,977,112,445 bytes**, with **zero content changes**. The archive matched the source before execution and has no in-repo predictor target afterward. Canonical archive-manifest SHA256: `9934b98caada1863745675f4f2e7a043f7bee3b3b95d8d81afb4788ee0237c2e`.

The tracked-file size guard passes: **0 files over 5,000,000 bytes**; maximum **4,992,029 bytes**. The pre-existing untracked certifier `.codexlog` remains outside the tracked-content comparison. See [verification summary](verification_summary.json), before/after manifests, and [size audit](size_audit.json).

`git diff --check 3b4090bf9..HEAD` exits **2**, with **821 whitespace diagnostics** in archived logs/patches and three documentation/package files. This is recorded accurately in [diff_check.log](diff_check.log); it does not indicate a runtime failure or merge conflict and is not presented as a green check.

## Ordered asks

1. Coordinator: make the third-cycle merge decision using this scoped certification at `ee77f07f3`; the inspected subsequent `22b6b25d1` change is bookkeeping only.
2. Keep cycle-2 L1 and the ancillary L2 receipt-output limitation logged. Neither requires another automatic fix/re-review loop before merge under the stated disposition.

VERDICT: CERTIFIED FOR MERGE within the scoped review; LOW items logged | BLOCKERS: 0 | HIGH: 0

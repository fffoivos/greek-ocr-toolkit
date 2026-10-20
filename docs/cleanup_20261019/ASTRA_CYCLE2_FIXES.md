# CLEAN7 — Astra cycle-2 fixes

Scope: `cleanup/pipe032`, starting HEAD `8a5cafcc68c8bee985be7a5898e4daa748e4efde` plus the uncommitted edits recorded below. No staging, commits, worktree creation or other mutating Git commands. Review: [ASTRA-CLEANUP2_review_1.md](astra_cycle2/ASTRA-CLEANUP2_review_1.md).

| Finding | Change | Files |
|---|---|---|
| H1: a fresh/read-only tree has no hard-coded predictor executable | Shared `predictor_binary(profile='debug'|'release')`: explicit `GREEK_OCR_PREDICTOR` → scratch `GREEK_OCR_BUILD_DIR` (default per-user Cargo.lock-hash cache) → existing in-repo target. If missing, build **both profiles**, offline and locked, into scratch. Record Cargo.lock SHA256, rustc version and both binary SHA256 values in `BUILD_RECEIPT.json`. Invalid explicit paths, absent Cargo and offline build failures raise errors; none becomes a skip. | `greekocr/harvest/predictor_path.py`; `tests/test_predictor_path.py` |
| H1: tests and historical replay adapters bypass configuration | One session fixture resolves and exports the executable. Current native tests consume that fixture; S1–S5 replay and S1–S4 report adapters and the parity CLI use the helper. Frozen baseline test bodies keep their bytes; the existing historical AST loader redirects their predictor path through the helper in memory. S3/S4 byte-identity assertions and saved baselines remain unchanged. Deployment packages retain their explicitly bound packaged runtime paths. | `tests/conftest.py`, `tests/_paths.py`, `tests/test_seg_{curve,small,gate,deskew}.py`; `scripts/harvest/verify_filter_parity.py`; `docs/records/harvest/seg_steps/{s1,s2,s3,s4}/replay.py`, their `validate_report.py`, and `s5_adopt/replay.py` |
| H1: documented install/test sequence omits the prerequisite | Document Cargo/rustc, offline locked builds, debug/release profiles, scratch receipts and both predictor environment variables; note the external data root for complete saved-data coverage. | `README.md` §4; `AGENTS.md` §5 |
| Archive verification also exposes sibling-checkout assumptions | SR1 patch application uses the already tracked `scripts/labelfix/r2_score.py`, asserting the existing receipt's source SHA256. Gate grammar, legacy correction artifacts, the CP7 prompt and CP7 exclusions use their identical retained local copies. S1's review-site path falls back to the archived package, whose context evidence was compared byte-for-byte with the sibling site's input. All original assertions remain active. | `tests/adjudicate/test_sr1.py`, `tests/test_content_gate.py`, `tests/test_line_pipeline.py`, `tests/test_seg_cp7.py`, `tests/test_seg_cp7c.py`; `docs/records/harvest/seg_steps/s1/replay.py` |
| A Git archive has no `.git` marker; read-only fixture copies inherit read-only directories | The size guard uses its repository root directly, retaining the same index/blob checks with read-only `GIT_DIR`. RU3/RU4 worktree and symlink rejection tests now use synthetic temporary marker directories. Google-reader tests make only their copied temporary catalogue directory writable, so they can add synthetic comments when source fixtures are read-only. | `tests/test_size_guard.py`, `tests/test_ru3t.py`, `tests/test_ru4e.py`, `tests/test_google_failed_lines.py`, `tests/test_google_vision.py` |
| M1: mandate item 5 incorrectly says “SEG10 only” | Match [CHANGES_BEYOND_RELOCATION.md](CHANGES_BEYOND_RELOCATION.md): SEG10, PIPE032, CROPS3/CROPS4, BENCH02D–I, SPLIT2, CENSUS05-R readout and census README packaging. Preserve merged/adjacent distinctions and the split-input qualification. Only SEG10 and configured PIPE032 change pipeline decision rules as documented. | `docs/ocr_program_2026-10-06/briefs/ASTRA_CLEANUP_review_brief.md` item 5 |

## Reproduction and evidence

Fresh source: `/tmp/clean7_final_j5hemqnq/fresh`. Exported with `git archive HEAD` piped to `tar -x -C <scratch>`, then overlaid with the uncommitted tracked edits plus the new helper and its tests. This overlay is necessary because this run cannot commit. The export contains no `.git`, ignored targets or source caches. All exported files/directories had write permissions removed before testing. The archive's complete content digest is checked before and after pytest.

Cargo target directory: `/tmp/clean7_final_j5hemqnq/build`, absent before the full archive run. `GREEK_OCR_PREDICTOR` is unset at launch; the session fixture must therefore build through the helper. The in-place run uses that same scratch build. Both runs use:

```sh
PYTHONDONTWRITEBYTECODE=1
GREEK_OCR_DATA_ROOT=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-data
GREEK_OCR_BUILD_DIR=/tmp/clean7_final_j5hemqnq/build
CU3_CACHE_ROOT=/tmp/clean7_cmhp3loc/golden_cache
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m pytest -q -p no:cacheprovider
```

These are environment assignments passed together to the subprocess. `CU3_CACHE_ROOT` is the existing recogniser-test option: the scratch fixture contains the spellcheck `align_s0.jsonl` plus both R0 locked caches, copied without regeneration and hashed in the evidence receipt. Thus the archive also exercises the optional R0 golden records. For the archive only, `GIT_DIR` points read-only to the existing source worktree metadata and `GIT_WORK_TREE` points to the export; `GIT_OPTIONAL_LOCKS=0` throughout. This supports the existing Git-reading tests without creating or copying Git metadata.

The first full archive attempt exposed 14 failures from the checkout/permission assumptions above and the absent golden-cache configuration. Its log is retained as diagnostic evidence; it is not the final gate. No test was converted into a skip. All 28 files under the saved SEG baseline directories remain byte-identical, and the original S3/S4 identity assertions are unchanged. Six new resolver tests cover precedence, both-profile locked/offline builds and receipts, default cache identity, unavailable Cargo, build failure and invalid profile.

The fresh suite built both profiles successfully. [Build receipt](clean7_evidence/BUILD_RECEIPT.json): Cargo.lock `c44e7f2a151bb76a3b24d03c182766e117f84c039eb97b0afb9e682fdcb843f4`, rustc `1.96.1 (31fca3adb 2026-06-26) (Homebrew)`. [Profile parity](clean7_evidence/PROFILE_PARITY.json): debug, release and the pre-existing predictor returned byte-identical output on 20 requests across all five model groups.

The read-only archive remained exactly **45,414 files / 2,955,074,427 bytes** before and after the full suite; content digest `410257006cc15c7dfd04fee402576012bb55440294a8223a2cf667774704a273`. No in-repo `target/` was created. [Overlay paths and hashes](clean7_evidence/OVERLAY.json), [golden-cache input custody](clean7_evidence/GOLDEN_CACHE_RECEIPT.json), and [first diagnostic run](clean7_evidence/diagnostic_fresh_pytest.log) retain the exact bindings and initial failures.

Both suites have the same 102 skips under existing historical, missing-artifact, browser and sandbox conditions; no skip rule was added or broadened. In particular, this sandbox cannot bind the loopback test server (one skip), whereas the cycle-2 review recorded 101 skips. All predictor-dependent cases and both native S3/S4 identity cases execute successfully in both runs. [Baseline hashes](clean7_evidence/BASELINE_SHA256.json) bind the 28 unchanged saved baseline files.

## Raw full-suite results

Fresh read-only archive, exit **0**, **0 failed / 0 errors**:

```text
7311 passed, 102 skipped, 9 warnings, 63 subtests passed in 330.99s (0:05:30)
```

In-place, exit **0**, **0 failed / 0 errors**:

```text
7311 passed, 102 skipped, 9 warnings, 63 subtests passed in 330.50s (0:05:30)
```

Raw logs: [fresh](clean7_evidence/fresh_pytest.log), [in-place](clean7_evidence/inplace_pytest.log). The in-place wrapper checked every overlaid source hash before and after the suite; all matched the archive's tested source. Archive content receipts: [before](clean7_evidence/fresh_tree_before.json), [after](clean7_evidence/fresh_tree_after.json). [Evidence manifest](clean7_evidence/MANIFEST.json) records artifact paths, bytes, SHA256 values, the starting commit and the uncommitted overlay binding. `git diff --check` passes. No Git-mutating command was run. Independent Astra re-review remains separate from these implementation checks.

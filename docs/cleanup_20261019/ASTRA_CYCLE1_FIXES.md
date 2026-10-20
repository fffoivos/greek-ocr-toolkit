# Astra cycle-1 fixes (CLEAN6)

Worktree: `cleanup/pipe032`, starting HEAD `f1c5be45e`. No Git metadata writes. The coordinator must add/commit the prepared changes, including the restored base fixtures, before committed-HEAD re-review.

## HIGH 1 — committed custody and aliases

- Finding → 3,409 base files were absent from the reviewed Git tree.
- Cause → the text-ignore repair restored 3,373 of the listed files, but 36 binary/small replay fixtures still had old-path exceptions or nested output-directory ignores.
- Change → restored those 36 files from exact base `ac1c38cf6` blobs at mapped paths, verified all SHA256 values against Astra's list, and added narrow ignore exceptions. They are **pending coordinator add/commit**, not falsely described as already tracked. No files are deliberately discarded. Unexplained residual: **0**; current Git-tree residual: **36, all justified by the no-Git-writes boundary and prepared for tracking**.
- Files → `.gitignore`, two nested `.gitignore` files, 36 paths in [ASTRA_CYCLE1_CUSTODY_RESIDUAL.tsv](ASTRA_CYCLE1_CUSTODY_RESIDUAL.tsv), [counts](ASTRA_CYCLE1_CUSTODY.json), `scripts/layout_paths.py`.
- Test → `PYTHONDONTWRITEBYTECODE=1 python scripts/layout_paths.py --check`: **Git-only alias check: 170 rows resolved; 0 missing**. It exports the resolver, alias metadata and one real Git-tracked descendant per alias into a temporary checkout using `git archive HEAD`; imports and resolution run there with no working-tree fallback. Both sides of every alias resolve. Two historical copies of the human-review guide legitimately resolve to separate retained files. This is an alias/import check, not full-suite execution in a complete exported tree.

## HIGH 2 — readers after relocation

- Finding → SF7 hashes a missing local overlay after reading external bytes; collection rejects external round1/round2 inputs; R2 silently loses sibling metadata.
- Cause → reads and checks/hash paths disagree; R2's explicit unrelocated sibling was assigned the local checkout's new layout.
- Change → SF7 resolves JSON reads and hashes through the data-root adapter; collection resolves each report, summary and required input before checking/reading it; R2's binding returns the resolved file used by its reader, and deliberate sibling wave paths retain `docs/harvest`. Saved responses/native pages also use their bound inputs consistently. `input_path` delegates missing repository paths to `resolve` and preserves explicit sibling/temporary paths.
- Files → `scripts/labelfix/sf7_measure.py`, `greekocr/harvest/collection.py`, `scripts/labelfix/r2_cards_prepare.py`, `tests/test_cleanup_readers.py`.
- Test → tiny synthetic external SF7 audit/hash fixture; mixed local-summary/external-input round1 and round2 fixtures; explicit sibling metadata fixtures for both waves; R2 external JSONL read/hash identity. Reader + resolver gate: **59 passed in 0.86s**.

## HIGH 3 — test outputs and offline isolation

- Finding → 19 R2 setup errors, OS5 repository raster writes, and leaked socket replacement.
- Cause → overridden `tmp_path` created scratch in the checkout; the sheet builder retained production OUT; importing R2 globally monkeypatched sockets.
- Change → use pytest's external `tmp_path`; scope the R2 resolver's explicit `GREEK_OCR_R2C_TEST_OUTPUT_ROOT` override to tests (default production confinement and protected input-folder checks remain); inject OS5 OUT with `monkeypatch`; enforce the R2 CLI's offline guard with a restoring context manager, leaving imports free of socket mutations.
- Files → `tests/test_r2_cards.py`, `tests/adjudicate/test_os5_owner_sheets.py`, `scripts/labelfix/r2_cards_prepare.py`, `scripts/labelfix/r2_cards_resolve.py`.
- Test → **58 passed, 1 skipped in 2.40s** with the external data root enabled; skip is the pre-existing sandbox loopback-bind restriction, not a historical reclassification. New tests cover restoring sockets after an exception and rejection of external output when the test override is unset. Search of test temporary-directory constructors found no other repository-bound temp directory. Full-suite receipt follows below.

### Data-enabled expansion and real witnesses

Astra's real inputs now reproduce: round1 **61,882 delivered rows**, round2 **24,430**, named sibling row **1 admission /1 record**, SF7 audit **100 rows /3 SHA bindings**. Data-enabled collection succeeds: **7,404 tests collected in 7.76s**, no collection error (before three further tiny regressions were added).

The first expanded suite was **35 failed, 7,267 passed, 102 skipped, 9 warnings, 63 subtests passed in 310.47s (0:05:10)**, zero setup errors. All failures were unresolved external-input paths. Both raw `git status --porcelain` and `git diff --binary` were byte-identical before/after that run. These failures were repaired, not made historical skips:

- `scripts/labelfix/clariden/c1_common.py` and `scripts/numerics/n1t_packs.py`: hash/JSONL readers now use the data adapter (tiny external read/hash regression added).
- `tests/test_adm5b_schema.py`, `test_collection_outputs.py`, `test_content_gate.py`, `test_lqb*.py`, `test_n1*.py`, `test_round1_rescue.py`, `test_seg_{deskew,gate,cp7b_score}.py`, `labelfix/test_r2a_package.py`: retain assertion values and consume resolved inputs; native fixture rows bind the resolved crop path. Write calls remain at temporary destinations.
- `tests/_paths.py`: frozen documentation readers adapt read calls in memory, including CP7's external JSON/raster inputs; joined documentation paths are relocated at runtime so explicit sibling paths keep their own layout. Frozen source bytes remain unchanged. Tiny regressions cover external reads, unchanged output destinations and sibling layout.
- Expanded affected-module gate: **412 passed, 15 skipped in 72.36s**. Resolver/R2/new tiny fixtures: **109 passed in 1.15s**. Skips remain existing historical bindings or explicitly absent private scratch files; no new skip decorator or skip condition was added.

## HIGH 4 — operational scope beyond SEG10

- Finding → cleanup also integrated operational features.
- Cause → lead merges were described too narrowly as relocation plus SEG10.
- Change → [CHANGES_BEYOND_RELOCATION.md](CHANGES_BEYOND_RELOCATION.md) lists producing branches/commits, inclusion, purpose, recorded tests and decision effects for CROPS3/4, BENCH02D–I, split2, readout, package documentation, PIPE032 and other post-base infrastructure. No operational work reverted.
- Files → that scope record.
- Test → `git log ac1c38cf6..HEAD`, source diffs and per-commit `git merge-base --is-ancestor`. CROPS4 and BENCH02E–I are **not merged into this worktree**; their later `sol/recut-v1` commits remain listed explicitly as adjacent work. PIPE032 parity holds with empty scope; a nonempty explicit scope can change correction HOLD/admission. Split inputs can likewise change eligibility without changing the evaluator. The document avoids claiming unconditional decision parity.

## MEDIUM 5 — current documentation and history

- Finding → current guides/graphs disagreed with code; historical byte-equality and data-policy claims were too broad.
- Cause → CLEAN5 documents predated SEG10/PIPE032, while compatibility documentation was more recent.
- Change → synchronize pipeline **0.3.2**, segmentation **0.13 / label 0.9-s5**, band **0.30–2.00**, numerics **0.3**, census **0.7**, composer **0.3**, content gate/final **0.3**. Explicitly label S4 band and pre-integration limitations as history; document scope statuses, historical/demo exceptions, and corrected baseline byte/AST distinctions. Coordinator band provenance and rising SEG10 false negatives remain explicit.
- Files → README/AGENTS, A/B current guides and both canonical/compatibility graphs; [version audit](ASTRA_CYCLE1_VERSION_AUDIT.md) and [complete token inventory](ASTRA_CYCLE1_VERSION_STRINGS.tsv).
- Test → compare current identities against code/manifest; `verify_versions` passes **all 11 tools**, source hashes and aggregate digests. Q4 `baseline.py` current bytes differ but executable AST (without module docstring) is equal. Historical/model/threshold values remain in their own namespaces.

## MEDIUM 6 — receipt completeness and provenance

- Finding → index totals/manifest omitted later shards, and CP5 said `merge`.
- Cause → aggregate metadata did not follow later custody moves.
- Change → all four shard counts/TSV hashes updated; **16,898 entries /10,537,020,663 bytes**; append **10** receipt_02/03/04 rows using each receipt's UTC filesystem mtime (not an inferred historical move time). Replace CP5 producing marker with **dc47b8bb757a902aa180314527d2d0907b3da61c**.
- Files → `data_out/RECEIPTS/INDEX.md`, `receipt_03.tsv`, `data_out/MOVE_MANIFEST.tsv`.
- Test → every receipt path/bytes/hash matches the complete manifest; all ten later external payload hashes/sizes and mtimes verified. `git log ac1c38cf6 -- docs/harvest/collect_v3_admission/seg/CP5_verification.json.gz` supplies the producing SHA. Decompressing the base gzip yields exactly **119,720,892 bytes**, SHA256 `cc5131461ce6fa43a5f5be67fe74a5638b5d7226145dee2883ab1632c6a26731`. The receipt identifies this transformation; it does not invent an uncompressed old Git blob.

## LOW 7 — historical skip provenance

- Finding → N1W1-R3 claimed a green execution without a receipt.
- Cause → a producing-phase anchor was described as executed green.
- Change → exact wording: `historical binding; last executed green not on record; producing-phase anchor 686ec7de7`.
- Files → `tests/test_n1w1_r3.py`.
- Test → decorator text inspected; original test assertions remain unchanged. Full collection/run retains the historical skip.

## Final full-suite gate

Run with `PYTHONDONTWRITEBYTECODE=1`, `GREEK_OCR_DATA_ROOT=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-data` and the specified interpreter/pytest command. Before/after status and tracked-diff snapshots and the raw log are captured outside the checkout; no chmod or Git writes. Final results are appended after completion.


**Final result: 0 failed / 0 errors; exit 0.** Raw summary:

```text
7305 passed, 102 skipped, 9 warnings, 63 subtests passed in 324.53s (0:05:24)
```

[Raw full-suite log](ASTRA_CYCLE1_FULL_SUITE.log) · [verification receipt](ASTRA_CYCLE1_SUITE_VERIFICATION.json).

Before/after the suite: `git status --porcelain` **91 → 91 lines**, all status bytes equal; `-uall` bytes also equal; `git diff --binary` bytes equal; **39,405** source/evidence fingerprints, **0 changed**. Existing 102 skips were retained, with no new historical skip or skip condition. No tracked or prepared file was created/modified by the suite.

After saving the two final log/receipt files: `git status --porcelain | wc -l` = **93** (**78 CLEAN6 entries +15 untouched pre-existing untracked entries**). The pre-existing entries are Astra's supplied evidence directory, this task's brief and 13 PIPE032 evidence files. They were not removed or claimed as CLEAN6 output. Only report/receipt finalization and restoring the unrelated `mock-out/` ignore spelling followed the suite; executable code and tests remain exactly those tested. No Git metadata writes.

Coordinator handoff: add the prepared edits and the **36 exact-base restored fixtures** listed in the residual TSV, then commit/re-review. Their current Git-tree absence is explicit; all are now present, hash-verified and unignored. There is no unexplained custody residual.

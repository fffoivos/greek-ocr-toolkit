# Spell-check branches: merge rehearsal v2 (coordinator rulings applied), 17 Oct 2026

> **UPDATE 17 Oct ~11:50, coordinator ruling C adopted (supersedes "Option A" and the 15 failures above).**
> Real-merge sequence for the owner:
> 1. r0
> 2. s8 (case.py/ink.py kept frozen; S8b stays a patch)
> 3. l1f (hashed edits archived as a patch)
> 4. l1 (docs only; old package archived)
> 5. fixtures commit (10.8 MB)
> 6. **Option C**: l1f's recomposition adapter moved into the NON-hashed `scripts/labelfix/clariden/l1r_recompose_ext.py`; L1R drivers
>    restored; new test `test_policy_frozen_after_merge.py`.
>
> The Option-A commit (698cdfa7) is DROPPED from the real sequence. Rehearsal branch `rehearsal/merge-20261017` at a241ed75e.
>
> Lead-verified results (outside the Sol sandbox):
> - hashed-set diff vs opus/spellcheck: empty;
> - greekocr/ diff: empty;
> - policy_binding() = 6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406;
> - full suite: 4,809 passed / 19 skipped / 5 failed / 5 errors, all pre-existing environmental (test_collection_outputs 3,
>   test_provenance_cli_api 2, test_apply_clean 5 errors);
> - L1R failures 15 → 0; 0 new failures.
>
> The coordinator read the hashed-set diff and the new module: read-only imports of release_gate, text, l1_common and r1_common; no
> setattr/reload/sys.modules patching; no hashed source imports it. The coordinator did **not** recompute the digest or the suite: their
> Mac's default python3 lacks an arm64 numpy. **The digest and suite numbers are the lead's verified record.**
>
> The r1 worktree stays: it is blocked by the hashed m2_run.py checkpoint-path assert. Its 61 load-bearing files are already copied
> into main `artifacts/labelfix_r1/` with verified sha256.
>
> Details: `CLEANUP_MERGE_REHEARSAL_optionC.md`. The real merge remains the owner's gate.

## OWNER DECISION SHEET

| item | result |
|---|---|
| **Branches merged, in order** | r0 (7cef606f) → s8 (2e1efb3b; also brings l1r, l1r2, l1r3) → l1f (ed5037ae) → l1 (e3a69415, **docs only**) → sync with opus/spellcheck 052ec437. **Not merged:** align and r1 (already in spellcheck); l1r, l1r2, l1r3 (subsumed); r2-cards and r2-prep (excluded, in flight) |
| **Kept frozen (SF6c)** | `greekocr/labelfix/case.py` and `ink.py` (s8's S8b candidate is out; it stays archived as `docs/records/labelfix/spellcheck/S8_DEV/s8b/detector.patch`). The policy-hashed `scripts/labelfix/clariden/l1_common.py`, `l1r_recompose.py`, `l1_detect.py` and `l1_infer.py` stay at opus/spellcheck's versions |
| **Archived (not live)** | `docs/records/archive/s8_l1r3_hashed_paths_20261017.patch` (s8/l1r3 versions of l1_common + l1r_recompose, 626 lines) · `docs/records/archive/l1f_hashed_paths_20261017.patch` (l1f versions, 648 lines) · `docs/records/archive/l1_20261017/` (L1-v0 package: 6 scripts + sbatch, test_l1.py, 3 root L1_*.txt receipts, l1-side l1_common/l1_detect/l1_infer, README) · **OPTION A, needs a ruling:** `docs/records/archive/l1r_line_20261017/` (10 l1r/l1f/l1r4 drivers + 2 configs + test_l1f.py, README) |
| **Policy digest** | **unchanged**: `policy_binding()` = `6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406` (sf6-release-v1), the same before and after |
| **greekocr/ byte-identical to opus/spellcheck** | **yes**: same tree id `8902048294a7f27b397b107d28ac6fe889eb8ca4`, and the 282-file sha256 lists are identical |
| **Tests** (`pytest -q tests/labelfix`) | opus/spellcheck: 1431 passed. Final rehearsal: **1541 passed, 15 failed**. All 15 are in `test_l1r.py`, `test_l1r2.py` and `test_l1r3.py`, and they fail **only because ruling 3 keeps the SF6c `l1r_recompose`**. With the l1f patch applied they pass, apart from the 10 that need the archived `l1r_job.sbatch` |
| **Fixtures** | 10.8 MB together (sf6: 6 files, 146 KB; l1e: 24 files, 10.6 MB). That is under 50 MB, so **committed** in the rehearsal. Without them: 1369 passed, 187 failed (+172) |
| **Added vs opus/spellcheck** | 6,280 files (6,218 docs, 27 artifacts, 28 scripts, 6 tests, 2 config); 1,647,238 insertions; **374.5 MB uncompressed, about 276 MB packed** |
| **Push implication** | opus/spellcheck has no upstream; a push would upload these ~276 MB plus everything unpushed (30k objects not on any remote). Largest single file 20.3 MB (under GitHub's 100 MB limit). S8_DEV alone is 5,330 files |
| **Worktrees that could be retired later (owner's call)** | align and r1 (fully merged); l1r, l1r2, l1r3 (subsumed, once s8 is merged for real). s8, l1f and l1 only after the real merge. **r1 cannot be removed yet**, see the open risks and Appendix A |
| **r1 copy list** | **61 files / 219.0 MB** must be copied into main `artifacts/labelfix_r1/` first (Appendix A, with sha256): heldout_font 46, score_3678928_K1c_vsS6 14, and `output_3678928/RESULT.md` (main has a 385 B stub). 60 more output_3678928 files are already identical in main. Optional (provenance or uncited): heldout 48, mock_font 64, vsS5 13, vsS6 13 |

**Open risks and decisions needed:**

1. **Ruling 3 strands the L1R…L1R4 packages.**
   - These packages produced the sf4/sf5/sf6 Clariden releases, and L1R4b is pending in the l1f worktree. With the SF6c `l1r_recompose.py` and `l1_common.py` live, 4 scripts no longer import (`l1f_run`, `l1f_mock_check`, `l1r4_mock_check`, `l1r_mock_check`), and 6 drivers call a `--config` CLI that the SF6c version does not have.
   - OPTION A (rehearsed as commit 698cdfa7) archives them, but 15 tests still fail. `test_l1r.py` cannot be archived because `test_l1r2.py` and `test_l1r3.py` import its fixtures; those two modules also hold 48 passing tests of live census code.
   - Choices:
     - (A) archive and accept or mark the 15 tests;
     - (B) port the drivers and tests to the SF6c API (new work);
     - (C) move l1f's recompose adapter to a **non-hashed** path and point its drivers there. This keeps 6f62925a, but it is a code change and breaks the deploy receipts' path bindings;
     - (D) accept a packaging-bound digest (734158eb) under a documented policy note. Ruling 3 rejected this.
2. **Hidden r1-worktree dependency inside the frozen gate.**
   - `scripts/labelfix/m2_run.py`, which is policy-hashed, sets `R1_COPY = ../greek-ocr-toolkit-spellcheck-r1/artifacts/labelfix_r1/output_3678928/A/best.pt` and asserts it equals the main copy (lines 43, 157–158, 237).
   - `scripts/labelfix/r0_prepare.py:371` and s8's `s8b_regressions.py:39` also read the r1 worktree path.
   - Removing that worktree would break M2 measurement. Changing m2_run.py would change the digest. Before any removal, keep that path alive (copy the files there as a plain directory or symlink after `git worktree remove`), or recertify.
3. **case.py and ink.py are outside the digest.** Any later edit to them, or to constraints, markshape, candidates, rules, lexicon or toolkit_geometry, changes gate behaviour without moving 6f62925a, and no unit test notices; the S8b candidate demonstrated this. Consider extending `policy_binding()` to the full import closure at the next policy version.
4. **The merges record l1r…l1f as merged while their hashed-file changes are reverted inside the merge commits.** A future `git merge opus/spellcheck-l1f` (after L1R4b) will not re-offer those changes. Any later l1f change to `l1r_recompose.py` will conflict, and must again be resolved to SF6c.
5. **l1f is still in flight** (L1R4b brief committed, code not yet). Re-run the rehearsal after it lands. Its planned edit is in the non-hashed `l1r4_join.py`.
6. Flaky test `test_s8_fetch_job.py::test_deadline_terminates_inflight_pool` (one 30 s timeout in v1; passed in every v2 run).
7. `scripts/labelfix/s8_validate_truth.py` runs its validation at import time (it printed PASS during the import check). Harmless, but it surprises anyone who imports it.

- Scratch worktree: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal`
- Branch `rehearsal/merge-20261017` at **e8477c07** (left in place, clean).
- No real branch was touched, nothing was stashed, and no other worktree was modified. The r1 worktree was only read: `status`, `stat` and `shasum`.

---

## 1. Topology (against opus/spellcheck; unchanged since v1 apart from the spellcheck tip)

| branch | tip | merge-base | behind / ahead | contains | contained by | verdict |
|---|---|---|---|---|---|---|
| spellcheck-align | 2f764c96 | = tip | 0 ahead | — | spellcheck (fe75fa4c) and every sibling | already merged; do not merge |
| spellcheck-r1 | f6d74a52 | = tip | 0 ahead | align | spellcheck (7c04767c) and all l1*/s8/r0 | already merged |
| spellcheck-r0 | 7cef606f | d4c9b659 | 1 ahead | align, r1 | — | merge (docs: R0 i-b adjudicated truth) |
| spellcheck-l1 | e3a69415 | efdf5756 | 20 ahead | align, r1 | — | docs only (ruling 1) |
| spellcheck-l1r | c18f3d86 | 47f7b6b0 | 4 ahead | — | l1r2, l1r3, s8, l1f | subsumed |
| spellcheck-l1r2 | d57fcb4a | 05f2dafb | 8 ahead | l1r | l1r3, s8, l1f | subsumed |
| spellcheck-l1r3 | 4da66be4 | d893a04d | 14 ahead | l1r, l1r2 | s8 (at its tip); l1f up to 78ed28bd | subsumed by s8 |
| spellcheck-s8 | 2e1efb3b | d893a04d | 37 ahead | l1r, l1r2, l1r3 | — | merge; case/ink and the hashed paths stay frozen |
| spellcheck-l1f | ed5037ae | 90bcc286 | 20 ahead | l1r, l1r2, l1r3@78ed28bd | — | merge; hashed paths stay frozen; in flight |
| r2-cards / r2-prep | 6130a4b8 / f1610f2a (moved during the run) | 52f34de9 | — | — | — | excluded |

## 2. Per-merge results (v2)

| # | merge | commit | textual | resolution |
|---|---|---|---|---|
| 1 | r0 | d89d40e4 | clean | taken as-is (6 docs files) |
| 2 | s8 | 8bb0aebc | clean | `case.py` and `ink.py` restored to opus/spellcheck (S8b candidate, NOT adopted; archive = `S8_DEV/s8b/detector.patch`). Hashed `l1_common.py` and `l1r_recompose.py` restored to SF6c; s8's versions written to `docs/records/archive/s8_l1r3_hashed_paths_20261017.patch` |
| 3 | l1f | 4127c265 | **1 conflict**: `l1r_recompose.py` (ours = SF6c after step 2; theirs = l1f L1R4 adapter, +589 lines vs SF6c) | resolved to SF6c (ruling 3); `l1_common.py` restored to SF6c too; l1f's versions written to `docs/records/archive/l1f_hashed_paths_20261017.patch`. The patch applies cleanly to the live tree (`git apply` checked) |
| 4 | l1 | d834aa8d | **3 add/add conflicts** on the hashed `l1_common.py`, `l1_detect.py` and `l1_infer.py` (ours = SF6c shared-gate versions; theirs = pre-SF2 L1-v0) | kept ours. **Docs only (ruling 1):** the 3 root `L1_*.txt` receipts, `l1_inventory`, `l1_prepare`, `l1_run`, `l1_runtime`, `l1_verify`, `l1_job.sbatch` and `tests/labelfix/test_l1.py` were moved with `git mv` to `docs/records/archive/l1_20261017/<original path>`. The l1-side copies of the 3 hashed files were added there too, for provenance (the L1-v0 receipts bind those bytes). I also archived `l1_inventory`, `l1_run`, `l1_runtime` and the sbatch, although they import: `l1_run` drives the broken `l1_verify` and the mismatched SF6c `l1_detect`/`l1_infer`, and the receipts bind the whole package |
| 5 | fixtures | 6f6c3541 | — | 27 files committed (30 on disk; 3 `__pycache__/*.pyc` inside `frozen_sf5_05f2dafb` are gitignored and not needed) |
| 6 | OPTION A | 698cdfa7 | — | **needs a ruling.** l1r/l1f/l1r4 drivers that no longer import or that call the missing `--config` CLI, plus `config/l1f_*.json` and `test_l1f.py`, moved to `docs/records/archive/l1r_line_20261017/`. `config/l1r4_*.json` stay live because `l1r4_census_job.sbatch` and `test_l1r4.py` use them |
| 7 | sync | e8477c07 | clean | merged opus/spellcheck 052ec437 (print_truth README; docs) |

## 3. Gate closure and digest

- `policy_binding()` hashes 16 paths: release_gate, reading, text, segmentation and ctc_align, plus the scripts l1_common, l1r_recompose, owner_reading, owner_pages_build_combined, m2_run, r1_extract, l1_infer, l1e_measure, l1e_run, l1_detect and r1_common.
- Before (opus/spellcheck 291f581a/052ec437) and after (rehearsal e8477c07), both via the real function in each tree (toolkit venv, `PYTHONPATH=<tree>`): **`6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406`**.
- For comparison, with the l1f patch applied temporarily: `734158eb…`. That is the L1R4 packaging digest, so the patch is exactly what would move the digest.
- `greekocr/`: tree id `8902048294a7f27b397b107d28ac6fe889eb8ca4` in both. The sha256 list (282 files) of the opus/spellcheck blobs is identical to the rehearsal worktree files: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/greekocr_sha256_opus_spellcheck.txt` vs `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/greekocr_sha256_rehearsal_worktree.txt`.
- No live closure file differs from opus/spellcheck: `git diff opus/spellcheck HEAD` over the 16 hashed paths and `greekocr/` is empty.

## 4. Tests

| state | result |
|---|---|
| opus/spellcheck (v1 measurement, ba6d80aa; tips since are docs only) | 1431 passed |
| after all merges, before OPTION A (fixtures present) | 1541 passed, 15 failed, 1 collection error (`test_l1f.py`: `ImportError atomic_json`) |
| same, fixtures **absent** | 1369 passed, 187 failed (+171 test_sf6, +1 test_l1r4), 1 error |
| after OPTION A (= final e8477c07) | **1541 passed, 15 failed** |
| final + l1f hashed patch applied temporarily | 1546 passed, 10 failed (all need the archived `l1r_job.sbatch`) |

The 15 failures, all caused by SF6c `l1r_recompose` lacking `load`, `merge_shards` and the shard/receipt flow:
- test_l1r.py: all 7 tests (two-shard reuse; 4 input-corruption cases; missing peer fields; historical inputs);
- test_l1r2.py: 3 (multishard manifest census; sf6 census integrity; consensus zero gate);
- test_l1r3.py: 5 (two-shard real-mark list; job-2 inventory; 3 missing-optional-evidence cases).

Logs are in the scratchpad: `pytest_v2_final.log`, `pytest_v2_fixtures_present.log`, `pytest_v2_fixtures_absent.log`, `pytest_v2_optionA.log` and `pytest_v2_optionA_plus_l1fpatch.log`.

## 5. Fixtures (ruling 4)

| dir | du | files on disk | committed | bytes |
|---|---|---|---|---|
| artifacts/labelfix_sf6/frozen_sf5_05f2dafb | 156 KB | 6 | 3 (+3 ignored `.pyc`) | 146,457 |
| artifacts/labelfix_l1e/fixture_v4 | 10 MB (10,460 KB) | 24 | 24 | 10,644,686 |

Together they are about 10.8 MB, under 50 MB, so they are committed, and FIXTURES.md and the skip logic were not needed. The scratch copies were verified identical (`diff -r`) to the main worktree's untracked originals. Note that `frozen_sf5_05f2dafb` contains Python source copies (`greekocr/labelfix/release_gate.py`, `text.py`, `scripts/labelfix/clariden/l1_common.py`) under `artifacts/`; they are frozen sf5 references for `sf6_measure.py` and are not imported by the live gate.

sha256 per file:

```
a7596ee92c12d09dea37ce9849b1e887a9c0ed98b5f81145a941cf0af286d73b  artifacts/labelfix_l1e/fixture_v4/mock/binding/binding.json
117c24e86743fcda3c1fdda0f7cdb01c5916d607476e73b888cc6ee7901c7a11  artifacts/labelfix_l1e/fixture_v4/mock/expected_decisions.jsonl
7ad2ade9d342361e76fbfb439a912b4943850cfa76b8dfa670eb744142177cb8  artifacts/labelfix_l1e/fixture_v4/mock/fixture_receipt.json
d64efa0134c5b3365a5f41108233eda98c60658785ab7e5fc4d51146a417882a  artifacts/labelfix_l1e/fixture_v4/mock/historical/combined/shard-00000-combined.jsonl.gz
6183369472ce0924a93a4e7cbc07ddb5cec529e7b469be2f532dd2dd30125d47  artifacts/labelfix_l1e/fixture_v4/mock/historical/combined/shard-00000-receipt.json
725bb3f4cfd2ffb5f2ba80373dd23a4b6fa2f1baebc87253e12fa6ee23bfc6e2  artifacts/labelfix_l1e/fixture_v4/mock/historical/detector/detector_receipt.json
f6b4c6ecbf496d12eeff1e690edafd31b2a8f48e33b0413fb59e6779519dffde  artifacts/labelfix_l1e/fixture_v4/mock/historical/detector/shard-00000-detector.jsonl.gz
ed17e957671d712b6d3c066633d5c75a5e0a0460b06897e354e773e8f34b7e66  artifacts/labelfix_l1e/fixture_v4/mock/historical/detector/shard-00000-receipt.json
c37adf62a04e3ca25c6cfa1f8633f053d7f9dd3b55f661f721cb030021165e71  artifacts/labelfix_l1e/fixture_v4/mock/historical/detector/shard-00000-samples.json
566b78fc98315d81a13519edf339773aec0568b58adedb09aabe4c3fa4cfed7f  artifacts/labelfix_l1e/fixture_v4/mock/historical/detector/shard-00000-wide.npy
9c4b71c40a65b4a0e6ddf11e8326c7ec0bc27f0d1f52f574f89bbc4849f41653  artifacts/labelfix_l1e/fixture_v4/mock/historical/input_receipt.json
94896004f780d6becc3f72a49cedf5aefb78ccd678131ae7683722b47584319b  artifacts/labelfix_l1e/fixture_v4/mock/historical/release/ctrl_subset_full.jsonl.gz
fda5ca79ae067cce4bc9ff3bcb66f36cd7e3f6899bdb40dd5b5bea26001ceb1c  artifacts/labelfix_l1e/fixture_v4/mock/historical/release/ctrl_subset_presence.jsonl.gz
80debc503618ca2e5be2fc0b8905128b60e098e53000686d8f0462673d0146c1  artifacts/labelfix_l1e/fixture_v4/mock/historical/release/kept_full_line_ids.txt
0d5749e90959f344cca7d3bfd4a69aaf768dc4d9fe630de13d2b934ce84d467e  artifacts/labelfix_l1e/fixture_v4/mock/historical/release/kept_presence_line_ids.txt
6c295f2095a0d8ef13a85fcc7e106deb39255d267b873d19979fa2fea02ce0df  artifacts/labelfix_l1e/fixture_v4/mock/historical/release/overlay_full.jsonl.gz
b05c20fe3721292815e063fe691abb0e364573198aeb455094de79bce904c710  artifacts/labelfix_l1e/fixture_v4/mock/historical/release/overlay_presence.jsonl.gz
9fc5327f4be31af8ea4bdb2bd883d557c8a5021ce691841655d0f07c64bea8fd  artifacts/labelfix_l1e/fixture_v4/mock/historical/release/release_ctrl_subset_full.json
6ad6fe1214b4bc192eb709f814b00bbcad615283a14750799c6f5bd04a8cd76e  artifacts/labelfix_l1e/fixture_v4/mock/historical/release/release_ctrl_subset_presence.json
372d3a0a800d1c4f65c472c7f4e9d11fa23dcb894e7b904e090234688f389304  artifacts/labelfix_l1e/fixture_v4/mock/historical/release/release_full.json
8a367457aec911c218cf86ef3a522183e08494d5f7cfe69a98a8dd95af5eabbc  artifacts/labelfix_l1e/fixture_v4/mock/historical/release/release_presence.json
2cbfdd4ba67ae87d8afe68cd21633f463d486135ca15e82ec269b4ab976303ee  artifacts/labelfix_l1e/fixture_v4/mock/historical/run_receipt.json
f6e34a5ff240482c2e49dc04777030c7b2cd2c6e974cd8fd1b8f101a182916f1  artifacts/labelfix_l1e/fixture_v4/mock/selection.jsonl
f6e34a5ff240482c2e49dc04777030c7b2cd2c6e974cd8fd1b8f101a182916f1  artifacts/labelfix_l1e/fixture_v4/mock/source.jsonl
2b2c010786887613b95391949b45f5b4f0c1eacff3190a85cee0531adfac6a62  artifacts/labelfix_sf6/frozen_sf5_05f2dafb/greekocr/labelfix/__pycache__/release_gate.cpython-311.pyc
ea057d83bc20622612e79feac69798c45bf4b1ba6c30a3e50d1ef947f6397205  artifacts/labelfix_sf6/frozen_sf5_05f2dafb/greekocr/labelfix/__pycache__/text.cpython-311.pyc
b1137154ca1dce903967cd86974a83abae6e690dd818d21dc5ecf8eaf058a9c9  artifacts/labelfix_sf6/frozen_sf5_05f2dafb/greekocr/labelfix/release_gate.py
b2fbe9cf6d8c97d1f8e06e149bfe4e11cc58b9b4f2bb323bddc8afce2ca52c92  artifacts/labelfix_sf6/frozen_sf5_05f2dafb/greekocr/labelfix/text.py
1ccaeaeacec981c4f1b2ee7b701872d4a8e42f30ebe482043f5d8fc899609474  artifacts/labelfix_sf6/frozen_sf5_05f2dafb/scripts/labelfix/clariden/__pycache__/l1_common.cpython-311.pyc
d1e3b27f7494e2e0e4028a22fe358d5b9d20c64a655a7f889d41da20c215670c  artifacts/labelfix_sf6/frozen_sf5_05f2dafb/scripts/labelfix/clariden/l1_common.py
```

## 6. r1 worktree untracked inventory (ruling 5; read-only)

The worktree is `~/Projects/greek-ocr-toolkit-spellcheck-r1`. `git status --porcelain` lists 52 entries; with `-uall` that is **259 files, 522.7 MB**. Each file was compared with the main worktree (`~/Projects/greek-ocr-toolkit-spellcheck`) by sha256. Nothing was copied or removed.

| directory | files | MB | load-bearing? | cited by | action |
|---|---|---|---|---|---|
| output_3678928 | 61 | 50.7 | **yes** | hashed `m2_run.py` (R1 + R1_COPY at the r1-worktree path, asserted equal), sf2…sf6 measure scripts, `sf4_r1_compatibility.py`, CN1 brief, R2P teacher export (r2-prep `docs/records/briefs/R2P_reader_prep.md:49`), s8 `s8b_regressions.py` | 60 already **identical** in main (untracked); **copy** `RESULT.md` (r1 has 7,672 B `4b5cc721…`; main has a 385 B stub) |
| score_3678928_K1c_vsS6 | 14 | 32.0 | **yes** | `docs/records/labelfix/spellcheck/R2_evidence/page_builders/build_r1a_errors.py:14` (`A_mapped_lines.jsonl.gz`), `docs/records/reviews/ASTRA-R2design_brief.md` | **copy** (absent in main) |
| heldout_font | 46 | 187.0 | **yes** | `scripts/labelfix/clariden/r1_run.py:26` default; `scripts/labelfix/r0_prepare.py:371` (absolute r1-worktree path); SF3 measurement receipts; `R1_DEPLOY_SHA256.txt`; s8 `s8b_regressions.py` | **copy** (main tracks only `heldout_font/extraction_receipt.json`) |
| heldout | 48 | 45.7 | provenance | R1_REPORT and Astra review logs only (first extraction, `REJECTED_COLUMN_FILTER.txt`) | optional |
| mock_font | 64 | 144.5 | provenance | R1_REPORT, R1_mock.log, review logs (mock checkpoints) | optional |
| score_3678928_vsS5 | 13 | 31.4 | not cited | — | optional |
| score_3678928_vsS6 | 13 | 31.4 | not cited (superseded by K1c_vsS6) | — | optional |

The R2 plan (`R2_PLAN_20261017.md:12`) binds to arm A of job 3678928 through `R1_result_3678928/run_receipt.json`, which is tracked in docs. The arm-A checkpoint itself is `output_3678928/A/best.pt` (sha in Appendix B), which is already identical in main.

**Before any r1 worktree removal is proposed:**
1. copy the 61 files in Appendix A into the same relative paths under main `artifacts/labelfix_r1/`, and verify the sha256 values;
2. decide on the 151 optional files;
3. keep `../greek-ocr-toolkit-spellcheck-r1/artifacts/labelfix_r1/{output_3678928/A/best.pt, heldout_font/…}` reachable for `m2_run.py`, `r0_prepare.py` and `s8b_regressions.py`. Alternatively, repoint them, which for `m2_run.py` changes the digest.

## 7. Recommendation

1. Apply the real merge exactly as in this rehearsal: r0 → s8 → l1f → l1 (docs) → fixtures, with every hashed file and case/ink at SF6c, and the three patches/archives committed.
2. **The coordinator must rule on the stranded L1R line** (risk 1) before the real merge. My preference is **(C)**: give l1f's recomposition adapter its own non-hashed module, so the 6f62925a binding and the production packages both stay usable, followed by one review. If no code change is wanted now, (A) as rehearsed is safe for the gate, but it leaves 15 red tests that must be marked xfail with a reason.
3. Do not remove the r1 worktree until §6 is done. Retiring align and r1 is otherwise harmless git-wise, since both are fully merged.
4. At the next policy version, extend `policy_binding()` to the whole gate import closure (risk 3).

---

## Appendix A: r1 files that MUST be copied into main `artifacts/labelfix_r1/` (61 files, 219.0 MB)

| path | bytes | sha256 |
|---|---|---|
| `artifacts/labelfix_r1/heldout_font/index.npy` | 430,758 | `ff63ff6b89b4e3025d3ee605534da301dc2734b61d5b7d3f69e8c3f92c4b950b` |
| `artifacts/labelfix_r1/heldout_font/lines.jsonl.gz` | 274,498 | `d290010f13f3633be81459dacc7d85af124f63b5228bad406d78d675f521a61f` |
| `artifacts/labelfix_r1/heldout_font/shard-00000-index.npy` | 20,662 | `66258e7554cc15340682f7386c4dde58bb345f36a9c7e513d1fc5a4d323c684f` |
| `artifacts/labelfix_r1/heldout_font/shard-00000-lines.jsonl.gz` | 14,448 | `1895db0cb5aeca633fcfd8613a51e3f53a36bc31d6854706f21f4dc6e0bf7688` |
| `artifacts/labelfix_r1/heldout_font/shard-00000-narrow.npy` | 4,399,232 | `9d6ca767f5641afa939204cde014e4dcca5c46996049f44b4c2376d76232d920` |
| `artifacts/labelfix_r1/heldout_font/shard-00000-wide.npy` | 4,399,232 | `06a8000c3422a43305f188207ac88bc99e5d8625ff7f5f0cc44302ea56a00a08` |
| `artifacts/labelfix_r1/heldout_font/shard-00001-index.npy` | 28,566 | `047288b5b88abb448d774fc880db74d5bf4944dc479bbb33760a977e2d9befea` |
| `artifacts/labelfix_r1/heldout_font/shard-00001-lines.jsonl.gz` | 19,528 | `7c8ec730a7acb2b9feb9c09a3f80612e87985d065b3fd253bbcbbad54dca6e43` |
| `artifacts/labelfix_r1/heldout_font/shard-00001-narrow.npy` | 6,103,168 | `33584bccebe2e25334de8eaa72d717736615095405ebc75f42e0e42c0dcbb5ee` |
| `artifacts/labelfix_r1/heldout_font/shard-00001-wide.npy` | 6,103,168 | `8ca0f9543324346677b83d734059f81e06b8433a68a7e313a3787b195fc93a2e` |
| `artifacts/labelfix_r1/heldout_font/shard-00002-index.npy` | 36,470 | `e70204b0f96f69be12a676574750c6a0a05824b51962593290eb61667fc8b1be` |
| `artifacts/labelfix_r1/heldout_font/shard-00002-lines.jsonl.gz` | 24,516 | `3d823f671f4f5894ff379b84d225a4180f6e09646d28ad7e96f2d402fc351e23` |
| `artifacts/labelfix_r1/heldout_font/shard-00002-narrow.npy` | 7,807,104 | `fcb9ccdd4a4e1d502cb14506bc48dccf95ad2450e820afcc2d4f882c283f0b29` |
| `artifacts/labelfix_r1/heldout_font/shard-00002-wide.npy` | 7,807,104 | `306089b5387ab2e1aa1ad4ea7ff4668c10268a80d398ee4d4e19835f65acc10f` |
| `artifacts/labelfix_r1/heldout_font/shard-00003-index.npy` | 43,652 | `19366882787d01ed32c1f6f134a2921f03ec76479ac0f6ed090d3fc2a999e366` |
| `artifacts/labelfix_r1/heldout_font/shard-00003-lines.jsonl.gz` | 28,391 | `4f43185ad1e902d3f99ead661d8e55dcafb64daa6e9b67bf4c8e925db570435c` |
| `artifacts/labelfix_r1/heldout_font/shard-00003-narrow.npy` | 9,355,392 | `641316a04b8f195db3aa80c4067d60f95e957ccc39b9ca456244e75f30e5a3ed` |
| `artifacts/labelfix_r1/heldout_font/shard-00003-wide.npy` | 9,355,392 | `299569aee7016b0be5be194d3f715afd699146e15616f69f335695027905e114` |
| `artifacts/labelfix_r1/heldout_font/shard-00004-index.npy` | 45,932 | `5ebb833e7873220e7a01908b13c3565ba19395d766583613b8061385978eda67` |
| `artifacts/labelfix_r1/heldout_font/shard-00004-lines.jsonl.gz` | 29,736 | `4da22b2a9a325811eea69cf22dd7b01d5560bde00695d868be81033ca68060eb` |
| `artifacts/labelfix_r1/heldout_font/shard-00004-narrow.npy` | 9,846,912 | `df4ec193e523bf4ec20589f283bf5aac7be1f9e8363726945ad69b92ca01f521` |
| `artifacts/labelfix_r1/heldout_font/shard-00004-wide.npy` | 9,846,912 | `48c8f9a7e26513e0c8ad2f63c11e3eb38e97a8e5b83dd0f47e267cc658004323` |
| `artifacts/labelfix_r1/heldout_font/shard-00005-index.npy` | 46,844 | `c7c05d2e24cefdf1a71488d44af9c41ffb3026ecc0b803a33ead71ebb4b33566` |
| `artifacts/labelfix_r1/heldout_font/shard-00005-lines.jsonl.gz` | 30,013 | `4e9355b6fbe0f48a98544bf5b1e19e5d9cd015b59350f917d2efc82f15d00b4b` |
| `artifacts/labelfix_r1/heldout_font/shard-00005-narrow.npy` | 10,043,520 | `7b57a696ed812d158cd4daa87a957277e2e200db7757e424fc6d6c02fd10c538` |
| `artifacts/labelfix_r1/heldout_font/shard-00005-wide.npy` | 10,043,520 | `13063320c9543b70c9a78a49ec35775a6ce41b283a5afbc947fa64f1a4f74284` |
| `artifacts/labelfix_r1/heldout_font/shard-00006-index.npy` | 46,388 | `d238ef409c5d97f4a4d3f753b6b5c2128bf0020d0d7032268a4ae388a89278ca` |
| `artifacts/labelfix_r1/heldout_font/shard-00006-lines.jsonl.gz` | 29,835 | `c770d6f76d0fc2693505b831f83b5569699c28a913045333ce0f46e02faab73a` |
| `artifacts/labelfix_r1/heldout_font/shard-00006-narrow.npy` | 9,945,216 | `4561b398c5f18df2993c184f03c73596119312322c90d8771ed8a9c8dc420a1e` |
| `artifacts/labelfix_r1/heldout_font/shard-00006-wide.npy` | 9,945,216 | `430a49d3e565877a4c3c716fa317617c8aa960df06f6e5103d92f002735e9b70` |
| `artifacts/labelfix_r1/heldout_font/shard-00007-index.npy` | 48,858 | `656c89bd3a01a36c52391a46b4bdd8413513d0c73dcbf38fabdb3dafff825273` |
| `artifacts/labelfix_r1/heldout_font/shard-00007-lines.jsonl.gz` | 31,421 | `634583223fe3bad09e85b3fc8d832c27da7f8ca366cb847911743dc3540e5207` |
| `artifacts/labelfix_r1/heldout_font/shard-00007-narrow.npy` | 10,477,696 | `68bdc6e8e0764fa8b4db3a0522a1a896874605683808f710743a5eb90afa6443` |
| `artifacts/labelfix_r1/heldout_font/shard-00007-wide.npy` | 10,477,696 | `42defeff331022c0115bb28852b5f482e88ac962e40a3d865a92d962694728c5` |
| `artifacts/labelfix_r1/heldout_font/shard-00008-index.npy` | 48,326 | `db0256b797fee58a84d5506a4b2232dcc8e71782dadd811f056bb4b5c309eb47` |
| `artifacts/labelfix_r1/heldout_font/shard-00008-lines.jsonl.gz` | 30,829 | `bcb08df27af41b0edb2d4ad95d143d3ad3f80083d10feb910e0464fce9a565fc` |
| `artifacts/labelfix_r1/heldout_font/shard-00008-narrow.npy` | 10,363,008 | `67c14197df2ebb49e22e7085dbcdbd762d2906ee92e3a41d5d6d87e90d672993` |
| `artifacts/labelfix_r1/heldout_font/shard-00008-wide.npy` | 10,363,008 | `6754462daf44c23295e5e6fddb040dc1fc64a2dc047302d59ffc6e0cab19fb18` |
| `artifacts/labelfix_r1/heldout_font/shard-00009-index.npy` | 48,706 | `d42f66c2aabcdd665987981790768b45dc3e4112ea36e685e0e60ae40501f9f6` |
| `artifacts/labelfix_r1/heldout_font/shard-00009-lines.jsonl.gz` | 31,932 | `7aab6dc921c0855348f8594507a861a23e8cd4bea7b5498d7eb05bbb41254362` |
| `artifacts/labelfix_r1/heldout_font/shard-00009-narrow.npy` | 10,444,928 | `16ae5d38b876e4641a6891415529879a3048b51735db320d94a6552e1b4ff003` |
| `artifacts/labelfix_r1/heldout_font/shard-00009-wide.npy` | 10,444,928 | `587bb5a4fcd5af24b3c561f275a813122624dd34be7f3081b8d6e0c9c5fd6d8b` |
| `artifacts/labelfix_r1/heldout_font/shard-00010-index.npy` | 18,914 | `d929510ea27bb326a3e2c195ffea1cda1fe068308eb5f388ae37fb80c62e21b9` |
| `artifacts/labelfix_r1/heldout_font/shard-00010-lines.jsonl.gz` | 13,271 | `e7e2cf2eee9ce63cf2b97b5bbbc69bb67d1c6d07da8895c62d52b7c5724c819c` |
| `artifacts/labelfix_r1/heldout_font/shard-00010-narrow.npy` | 4,022,400 | `5a1473d31bf10132fe328dae6892b82ef09e0462ea9c620f6173046dfb7b33a2` |
| `artifacts/labelfix_r1/heldout_font/shard-00010-wide.npy` | 4,022,400 | `8b4dd36ae757afa6222d8b6a0ccd91d30946ab1d8ef11b10de7616cacee88856` |
| `artifacts/labelfix_r1/output_3678928/RESULT.md` | 7,672 | `4b5cc7215a651c93cd7105f946ab50a5e88868384c24ab91855c1d397764b4ad` |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/A_mapped_lines.jsonl.gz` | 6,207,710 | `1647c1ee69d60af24b006826ea1542b87b45465c58e7243ede5ee00c5f32360a` |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/A_owner_checks.jsonl` | 124,071 | `177c3af21db5107c9e0f81a38acb322f54ffcf87b445055cfd626fac0ba94bad` |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/B_mapped_lines.jsonl.gz` | 6,208,190 | `352e949d64dbd26690545dfc776ddb177927e0f9c9e6c09d6a446ac034453f69` |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/B_owner_checks.jsonl` | 124,075 | `c18b1e6ebe24953c4738c0858b692619400ed99c7bdc1e7436f984493b280c93` |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/C_mapped_lines.jsonl.gz` | 6,209,259 | `f14a1b93379d1c278bacd5b81c8a4930d0949dba35a9e2fde694a7679be85775` |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/C_owner_checks.jsonl` | 124,066 | `d054a63bacc61cc9980ed9d59cd44322aa93f251ba0097f93cfbdb240ea08cea` |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/D_mapped_lines.jsonl.gz` | 6,207,168 | `e45f9c79f8d034ec600c01a10b8044bef670feba0327d912986af9828bed352d` |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/D_owner_checks.jsonl` | 124,083 | `eb004e95d85a14a02647c51d75f1f160a00729c1b1466b32e98cb741f1a4d1ff` |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/E_mapped_lines.jsonl.gz` | 6,208,281 | `5cad5627bf7e9dfb04198a7c503712e3755b901b79a55d6ee6a17ddeedad2c5e` |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/E_owner_checks.jsonl` | 124,074 | `3149c6d255330437a4b921695acc8c26cd9bb4ba00a003112346cc982c2904d2` |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/RESULT.md` | 7,672 | `4b5cc7215a651c93cd7105f946ab50a5e88868384c24ab91855c1d397764b4ad` |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/error_types.json` | 1,378 | `fc6c92c0a660931ed814b49b8713c64a36674fe4c875df897da5db52e4aeee06` |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/metrics.json` | 280,604 | `8d64647ba551049ade70db7acb085a801bf63c8baa8afd2d52f112d667502e36` |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/score_receipt.json` | 675 | `bfaf3b6d86ad359d5c7078c71821b4b7439497c7d38fc8a7798517c7df7d1169` |

## Appendix B: full r1 untracked inventory (259 files)

| path | bytes | sha256 | class | action |
|---|---|---|---|---|
| `artifacts/labelfix_r1/heldout/REJECTED_COLUMN_FILTER.txt` | 129 | `c773b4c804611112afa7a29f7e23d6aaa55012972e830829f28e0fddb42cf62b` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/extraction_receipt.json` | 6,842 | `e67d0408192f8dcd45472deb540fc54c0496c162259c6d0ef124d0dfbdc56fa8` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/index.npy` | 105,326 | `b82f432384fc6d523115c1382c45d63e87275752536e3fd60d1dd4a8236e9275` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/lines.jsonl.gz` | 71,138 | `8fae420145e56ea51e2e01e3f87a06cdcdb7722f62f9e4cb3f104c9a59a9b50d` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00000-index.npy` | 4,702 | `94573818d30a32fbba4730397008f2a8d652930b23cdaa45346f9e91ddd407e0` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00000-lines.jsonl.gz` | 4,268 | `b9df4a2b9e864e6caf4f17a80b9f9071981fa69ab1d00752e514dcc05593581d` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00000-narrow.npy` | 958,592 | `fc91ecf03d303d14ba2707937dda81acfd277ed715cdca253766f44ff0a942fd` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00000-wide.npy` | 958,592 | `4524f13dcd460c409a334d5bc4f397a10710bc7b7e21c9962f273e1f447541de` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00001-index.npy` | 5,994 | `d2ad1bbfd3d28e29fd245c0e80a16936bde7e5e762d6125d2e15a866ea0fdefc` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00001-lines.jsonl.gz` | 5,613 | `34adf3a56dae16cd2e16b05ca7ff61d416d9665243d86607f79148b3a2156e85` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00001-narrow.npy` | 1,237,120 | `77845770ddb505b270e6fa256b7c091e07a81bfeadd1ef4de3d15eb6e09e4584` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00001-wide.npy` | 1,237,120 | `4f4815c1a59fafaa5d4c3f2e017ff7822db2951ca39b94914b1297b986290283` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00002-index.npy` | 8,730 | `1f2f13264bf141d90f77c8ca92a68a318f47c7b553e157b2487094153ec2d413` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00002-lines.jsonl.gz` | 6,850 | `2d9dba02fdcdabe7623682d39a02a84d1a589ec57c92ca64be4e0205138a6655` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00002-narrow.npy` | 1,826,944 | `b5c2b45d5238652227d176ad5175eb34c1f91a91917bbe13e15758ebf0752147` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00002-wide.npy` | 1,826,944 | `c9a871555876f8aa06435374e7c5d7b244f564ff4f11b8f5f587e776ebc3e846` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00003-index.npy` | 10,288 | `8f817424cb0bc46496a48e3a6c008b25d82da68235f4c100107c507f79c10567` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00003-lines.jsonl.gz` | 7,875 | `d44e01f0f68dadeb8567d28eed8cc0d613970442055b06cd21193ab0e1a447fb` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00003-narrow.npy` | 2,162,816 | `726cca047e7a6bb53f3fb1c53f00fa956d1cb0412a2e644f651aee8f471a1a42` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00003-wide.npy` | 2,162,816 | `51df2b74918f19283d0218225ea7a9a796dc019076def13df45a7ac2222744b6` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00004-index.npy` | 12,758 | `0aa6098bdf220feb9580f23d42bc3ab7b933e97df023e8b9a9a1d4992730c74d` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00004-lines.jsonl.gz` | 8,097 | `b76167d71fe6153e1cb714f6d709f0ebf8500dafa70ddf357300f284d4628c88` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00004-narrow.npy` | 2,695,296 | `b2960a54454d7ea7d92a7427b0c4da9de97fa97d62b9c95380df006496722ac6` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00004-wide.npy` | 2,695,296 | `6873d35ef76348c04331151d9c233620124e353a1a54ee55311749ba7b47ba33` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00005-index.npy` | 12,416 | `47cfd09faa3010aa4e096f8374b49b5d2e3e6174acf46c492f55d541d4b81248` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00005-lines.jsonl.gz` | 8,323 | `de15df571b7b59c0b354bd1f3962431b5cd61bc8a963b8930b974d4dd73ea74e` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00005-narrow.npy` | 2,621,568 | `6de1b72001b7f276f707d94bcdde18ace48825ed1d7909a8ecefd8c40d7adc16` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00005-wide.npy` | 2,621,568 | `c845028834cd9036ae8860fead2957785e6ad481c92de0937dcb814cb2071505` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00006-index.npy` | 12,112 | `62d8e71d5295a89d389dbc5453f93c219c8180cc727975f6b2f2735ce041d0a6` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00006-lines.jsonl.gz` | 8,131 | `b2fcb37c706b928f05d7fd447df7a79eadad4dca74fd4a803ce5332e4e8b58a6` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00006-narrow.npy` | 2,556,032 | `dee57dae4c3d3eb25d26426477f4cfdd69defd608ba2e5b088086cdb5b0a7882` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00006-wide.npy` | 2,556,032 | `780fa4fcf3af12b9d5d909d3c4d3de66f50cf685dace7a58c687640e959e93fd` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00007-index.npy` | 13,518 | `3caa33efad823c36d70960e93f8ddf9c0cdb7a38084b4fbcf7ce0238c2071eeb` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00007-lines.jsonl.gz` | 8,514 | `ff2e0663e7c713607d222c801656a67a1bc018bfa19f6a85212a7ba3bbfa1971` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00007-narrow.npy` | 2,859,136 | `ed74c55656bb1fc8f20554d814a466676553acb2a5af9adccec2f41715032281` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00007-wide.npy` | 2,859,136 | `a17ed3ec5b65d3c566b652873111c36d4aaef0293456ef804010e6315e3973d7` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00008-index.npy` | 12,416 | `e62ebe34972773a3849e22ff5366b7debbe139087832f38b8799b882f82d1f8c` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00008-lines.jsonl.gz` | 8,510 | `698f4065ca3ef3e68621c885cc2b106153ce637196d61db7ffc6523357ad8b63` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00008-narrow.npy` | 2,621,568 | `46f4a392e56fe8250a9ef5e30cf561e40aa7502c82732ac0c72b0dc3fec7f6c7` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00008-wide.npy` | 2,621,568 | `df8f210a3e62de4192226b776f8e32cd117c878dbf8f2e509db403fafd9bc9df` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00009-index.npy` | 12,644 | `8e83251c05a882d74e8c0c66f8209c0fa6df63c0ab26a3e68739009e21aa2e91` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00009-lines.jsonl.gz` | 8,521 | `8607c95e57ed8cff445812cd9d0f6bf62caf2dc1115318fb66c059a2be4eb389` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00009-narrow.npy` | 2,670,720 | `f5825c4e71f1237c3d5a3998426239561396dd8b5716b346b39cddc4e0dbfc81` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00009-wide.npy` | 2,670,720 | `eb25d5c3c086effcc4b0445d9d8f21911c8bfe9c4a6808cf24001e49db70a375` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00010-index.npy` | 2,308 | `a7316ec15b2fdfe45695e20d6cac3dae2719388ebafab6108d069335e06051fc` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00010-lines.jsonl.gz` | 3,458 | `e58d6792bb0c4ba4f75b18a1fb807895024f43968d81a2a555bed4437bc98c00` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00010-narrow.npy` | 442,496 | `deccda079e59c1256eaf3a3d0f7efd261210213d9eb40331d27200bd71703899` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout/shard-00010-wide.npy` | 442,496 | `1c9cf33be302770ffc2fd843ba9bbe1adfb753508fdc8aa3ac3f2508ae85454e` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/heldout_font/index.npy` | 430,758 | `ff63ff6b89b4e3025d3ee605534da301dc2734b61d5b7d3f69e8c3f92c4b950b` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/lines.jsonl.gz` | 274,498 | `d290010f13f3633be81459dacc7d85af124f63b5228bad406d78d675f521a61f` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00000-index.npy` | 20,662 | `66258e7554cc15340682f7386c4dde58bb345f36a9c7e513d1fc5a4d323c684f` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00000-lines.jsonl.gz` | 14,448 | `1895db0cb5aeca633fcfd8613a51e3f53a36bc31d6854706f21f4dc6e0bf7688` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00000-narrow.npy` | 4,399,232 | `9d6ca767f5641afa939204cde014e4dcca5c46996049f44b4c2376d76232d920` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00000-wide.npy` | 4,399,232 | `06a8000c3422a43305f188207ac88bc99e5d8625ff7f5f0cc44302ea56a00a08` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00001-index.npy` | 28,566 | `047288b5b88abb448d774fc880db74d5bf4944dc479bbb33760a977e2d9befea` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00001-lines.jsonl.gz` | 19,528 | `7c8ec730a7acb2b9feb9c09a3f80612e87985d065b3fd253bbcbbad54dca6e43` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00001-narrow.npy` | 6,103,168 | `33584bccebe2e25334de8eaa72d717736615095405ebc75f42e0e42c0dcbb5ee` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00001-wide.npy` | 6,103,168 | `8ca0f9543324346677b83d734059f81e06b8433a68a7e313a3787b195fc93a2e` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00002-index.npy` | 36,470 | `e70204b0f96f69be12a676574750c6a0a05824b51962593290eb61667fc8b1be` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00002-lines.jsonl.gz` | 24,516 | `3d823f671f4f5894ff379b84d225a4180f6e09646d28ad7e96f2d402fc351e23` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00002-narrow.npy` | 7,807,104 | `fcb9ccdd4a4e1d502cb14506bc48dccf95ad2450e820afcc2d4f882c283f0b29` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00002-wide.npy` | 7,807,104 | `306089b5387ab2e1aa1ad4ea7ff4668c10268a80d398ee4d4e19835f65acc10f` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00003-index.npy` | 43,652 | `19366882787d01ed32c1f6f134a2921f03ec76479ac0f6ed090d3fc2a999e366` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00003-lines.jsonl.gz` | 28,391 | `4f43185ad1e902d3f99ead661d8e55dcafb64daa6e9b67bf4c8e925db570435c` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00003-narrow.npy` | 9,355,392 | `641316a04b8f195db3aa80c4067d60f95e957ccc39b9ca456244e75f30e5a3ed` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00003-wide.npy` | 9,355,392 | `299569aee7016b0be5be194d3f715afd699146e15616f69f335695027905e114` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00004-index.npy` | 45,932 | `5ebb833e7873220e7a01908b13c3565ba19395d766583613b8061385978eda67` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00004-lines.jsonl.gz` | 29,736 | `4da22b2a9a325811eea69cf22dd7b01d5560bde00695d868be81033ca68060eb` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00004-narrow.npy` | 9,846,912 | `df4ec193e523bf4ec20589f283bf5aac7be1f9e8363726945ad69b92ca01f521` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00004-wide.npy` | 9,846,912 | `48c8f9a7e26513e0c8ad2f63c11e3eb38e97a8e5b83dd0f47e267cc658004323` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00005-index.npy` | 46,844 | `c7c05d2e24cefdf1a71488d44af9c41ffb3026ecc0b803a33ead71ebb4b33566` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00005-lines.jsonl.gz` | 30,013 | `4e9355b6fbe0f48a98544bf5b1e19e5d9cd015b59350f917d2efc82f15d00b4b` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00005-narrow.npy` | 10,043,520 | `7b57a696ed812d158cd4daa87a957277e2e200db7757e424fc6d6c02fd10c538` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00005-wide.npy` | 10,043,520 | `13063320c9543b70c9a78a49ec35775a6ce41b283a5afbc947fa64f1a4f74284` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00006-index.npy` | 46,388 | `d238ef409c5d97f4a4d3f753b6b5c2128bf0020d0d7032268a4ae388a89278ca` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00006-lines.jsonl.gz` | 29,835 | `c770d6f76d0fc2693505b831f83b5569699c28a913045333ce0f46e02faab73a` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00006-narrow.npy` | 9,945,216 | `4561b398c5f18df2993c184f03c73596119312322c90d8771ed8a9c8dc420a1e` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00006-wide.npy` | 9,945,216 | `430a49d3e565877a4c3c716fa317617c8aa960df06f6e5103d92f002735e9b70` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00007-index.npy` | 48,858 | `656c89bd3a01a36c52391a46b4bdd8413513d0c73dcbf38fabdb3dafff825273` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00007-lines.jsonl.gz` | 31,421 | `634583223fe3bad09e85b3fc8d832c27da7f8ca366cb847911743dc3540e5207` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00007-narrow.npy` | 10,477,696 | `68bdc6e8e0764fa8b4db3a0522a1a896874605683808f710743a5eb90afa6443` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00007-wide.npy` | 10,477,696 | `42defeff331022c0115bb28852b5f482e88ac962e40a3d865a92d962694728c5` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00008-index.npy` | 48,326 | `db0256b797fee58a84d5506a4b2232dcc8e71782dadd811f056bb4b5c309eb47` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00008-lines.jsonl.gz` | 30,829 | `bcb08df27af41b0edb2d4ad95d143d3ad3f80083d10feb910e0464fce9a565fc` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00008-narrow.npy` | 10,363,008 | `67c14197df2ebb49e22e7085dbcdbd762d2906ee92e3a41d5d6d87e90d672993` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00008-wide.npy` | 10,363,008 | `6754462daf44c23295e5e6fddb040dc1fc64a2dc047302d59ffc6e0cab19fb18` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00009-index.npy` | 48,706 | `d42f66c2aabcdd665987981790768b45dc3e4112ea36e685e0e60ae40501f9f6` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00009-lines.jsonl.gz` | 31,932 | `7aab6dc921c0855348f8594507a861a23e8cd4bea7b5498d7eb05bbb41254362` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00009-narrow.npy` | 10,444,928 | `16ae5d38b876e4641a6891415529879a3048b51735db320d94a6552e1b4ff003` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00009-wide.npy` | 10,444,928 | `587bb5a4fcd5af24b3c561f275a813122624dd34be7f3081b8d6e0c9c5fd6d8b` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00010-index.npy` | 18,914 | `d929510ea27bb326a3e2c195ffea1cda1fe068308eb5f388ae37fb80c62e21b9` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00010-lines.jsonl.gz` | 13,271 | `e7e2cf2eee9ce63cf2b97b5bbbc69bb67d1c6d07da8895c62d52b7c5724c819c` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00010-narrow.npy` | 4,022,400 | `5a1473d31bf10132fe328dae6892b82ef09e0462ea9c620f6173046dfb7b33a2` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/heldout_font/shard-00010-wide.npy` | 4,022,400 | `8b4dd36ae757afa6222d8b6a0ccd91d30946ab1d8ef11b10de7616cacee88856` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/mock_font/A/DONE` | 234 | `fd362c3bc64e368bc9d0a95a7980736f3205d14a2ed510604bdc43231a618288` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/A/best.pt` | 7,124,857 | `e686c38efc9acdea4e3efefb5b3c0cba49df840fe7fa4464814d7d2ba122de10` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/A/data_provenance.json` | 14,193 | `b6a61a318f3c3452bb6de57411f6cdb36f5567d6dfeea117124a308e934bb1ad` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/A/heldout_predictions.jsonl` | 1,678,675 | `43b3fe8d31ef7c0a3a48254e25bd4721bcfeabb4871824ba01535725fb28610f` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/A/heldout_predictions.receipt.json` | 470 | `a79effd9f32235354167864dcc4e22971c5ecef7d609324ab15c1925d4b7ff9b` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/A/run_binding.json` | 7,423 | `90bb3a1d222216e2a927008e6c15a59f5eab6bfbe51888df17247361edb13f2b` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/A/train_log.csv` | 232 | `b97a4c5b053229a873319b5f0258a4da1422469afda70c9a529f78989c7c836f` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/A/training_receipt.json` | 847 | `98f205dc0c1355057981b4e08a30795dc62d8df47ac14046a4e8a130985a6e0c` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/B/DONE` | 234 | `9a546a483f00807e94367bb51944d3be6243c2bb81544082160761026635afe1` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/B/best.pt` | 7,054,971 | `fe7cb769569c0ddc2cee2427e767bc8f10baa38489c85ec12deebf6ae47fafec` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/B/data_provenance.json` | 14,194 | `eb2a91adfb011f9fef0fef87b7d8d0e99979b00c2f2d08f0514d3116a94a45f3` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/B/heldout_predictions.jsonl` | 1,694,785 | `9d42b800a4b0f1aa6b668d0b53c4c23accf7f0fb38700642603c270d08e907a0` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/B/heldout_predictions.receipt.json` | 470 | `305ce205875a62fae19abb29d9324426c6dfff82cd0c8411ce712faef309d8e4` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/B/run_binding.json` | 7,544 | `2a6229561fe4b67335354bf1e94f033a746d983dded80e32c27d177051e458e5` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/B/train_log.csv` | 230 | `18d3262c90d3e577e3ee8468720ecf8a2dfd0311e4462dd2ffdc8d433782628d` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/B/training_receipt.json` | 847 | `2298fdb40c8a5326f21e9141913f5055ba4c330728e7673437a7ff7d2a2cb4fa` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/C/DONE` | 234 | `40db7879d51f1972c7806adf60d4041a07d2c0c27894b4d41a601cc3cf2d8435` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/C/best.pt` | 7,124,857 | `dbcc3e4b195235751f1fab124455a0966fdc207c407b2c4cb775cfae353224eb` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/C/data_provenance.json` | 14,194 | `3ae7f9c07933d2ed53fa91a2fe1cbedc23832ccc1c9b60f0faa7679d7d7dca1e` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/C/heldout_predictions.jsonl` | 1,681,757 | `39a76fc3aafabf4463506937dbd06cc30cb5ebe0fe5927f67fdacc970ae921e4` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/C/heldout_predictions.receipt.json` | 470 | `bf280a523237eb6ab69fe9aed7eccb8aae379781fe4d419487242f759e9f88e5` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/C/run_binding.json` | 7,544 | `409c069923e7ae41486525e37f01646cd1af021e549d96700e6953e9d836901f` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/C/train_log.csv` | 231 | `56c79d7a87f5104b5c7ba62448a199a54e5909edbbcfeadd2a99f63930538a98` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/C/training_receipt.json` | 847 | `dc396a5d133b1df04995a529ec3e850c87610d5f4e39c78711e2606771d56171` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/D/DONE` | 234 | `d60dcaf0d51a1ad55ef8c64c26b3c16632f688cdbeab0b92718664abae3f3c0e` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/D/best.pt` | 7,124,857 | `285058f695dca0ee05b7c8a98e7f18879d4580a7d211c9f27fc6951fe2e7bf68` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/D/data_provenance.json` | 14,197 | `6ccd8ea1a12e48376059a410e82f1a60025a6d62a533346b70b5728fe097dd17` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/D/heldout_predictions.jsonl` | 1,670,414 | `acee1f14850ab6890a07f9256e4c223c4f35b2e98264321db9d8440ad23d6f4f` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/D/heldout_predictions.receipt.json` | 470 | `d9515589fe00754ad8ce820e4df0e627d2ae2c456af1ab57bca9b501328b78c9` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/D/run_binding.json` | 7,547 | `1730af5241ef6be88eb2ea20d9f72d5b97b914333db774e2f427406ce2ceb81a` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/D/train_log.csv` | 231 | `b9fd76bea9223bf8d7345bd9348ce65d4a57e09d4b7a2e63ac07a679470b0d83` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/D/training_receipt.json` | 851 | `c208b0264e065e220778b6cde7be930dea459b41fddb50e758b60bc4184e84ee` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/E/DONE` | 234 | `33a575e0386ba4b4e614c451fab4d11b0649aa6aba80e53d255165de5516a7fd` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/E/best.pt` | 7,124,921 | `9b116995a9314b43d260175995d6f0b4afca48e328b6850d827c811038a7ab19` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/E/data_provenance.json` | 14,199 | `badae6aeb82a4ba75a20bc2a9c1b3abd42814f154fbe30226af5c2004e668a8a` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/E/heldout_predictions.jsonl` | 1,693,202 | `78e7e89ef96279c0a482c831a23c08005fd8a6d47deb1d66f3c2550253d481be` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/E/heldout_predictions.receipt.json` | 470 | `55bac20c578a37d069efe4e6020abd71bb31909442dc4c6b9c34cd690681bad5` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/E/run_binding.json` | 7,549 | `5ea943bb461d5f993fcf7218c57d0823d50f0fc4a00d39dc497e4cf9de00c4a5` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/E/train_log.csv` | 230 | `7140fd38299650c93340a71b046279d31d6de8485e99ae4a25edaf6345be29a7` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/E/training_receipt.json` | 851 | `ad6e80f3d3042526a023939d292b36317ae17b298eb9da3748aad2f8e73a8814` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/RESULT.md` | 7,044 | `d76b147c7fdb8a83c3d4573e099ef497f575ee80f303363b002cbce3023f4707` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/data/document_split.json` | 10,663 | `3a1ecae1141e6b6bb6ff3c4c87b2d629ad8bdce0e96ad48b8f0a094adb407d53` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/data/extraction_receipt.json` | 16,213 | `736115c1605b4e8b67d0915b070532cd3176a53a87b4639ebdd57e03e97fcc22` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/data/index.npy` | 158,678 | `b64b4756a3a3420456a31bbe3760cbf376e35f830ca33bf1f0beb6260f844f2a` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/data/lines.jsonl.gz` | 111,848 | `ea2f676384186277a4f2e885d58c0a9120acc9fe9028deff5d489eb5bb38fcf7` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/data/shard-00000-index.npy` | 158,678 | `b64b4756a3a3420456a31bbe3760cbf376e35f830ca33bf1f0beb6260f844f2a` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/data/shard-00000-lines.jsonl.gz` | 110,594 | `10668b76ee36e51142d5c41f4a2aafc1ee9958f060da9caf11fb4ff7bc997709` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/data/shard-00000-narrow.npy` | 34,152,576 | `e7773772e566fe193c7647ab5539b724d1b7c3e8beba44b9a04ebe7b1858f976` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/data/shard-00000-wide.npy` | 34,152,576 | `3dfeb58a56fcb3f6dc961c8b69e4670fabc8c7c194f52cf35738f576202b7772` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/run_binding.json` | 2,483 | `be02abd842644576eb87f2b2afc47db1d8a9bbe199416315e2559231406c02d7` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/run_receipt.json` | 4,929 | `bf911ae4d94c7389a4b6a20ca23727e72cc834c2329856aa7cf49411a612ec40` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/score/A_mapped_lines.jsonl.gz` | 6,126,446 | `70cc5f1457780bd0c3d6f4356cf98e267c2001cf06c457158b0ca33df2491cbe` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/score/A_owner_checks.jsonl` | 125,762 | `19012b8258785ef7ecb8627036bd08b0f6a68d5f08286990e6fa7225cb4735f0` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/score/B_mapped_lines.jsonl.gz` | 6,154,882 | `20bd7c6af80ef4063dfb8f31fde9cf21ee17742204dcf126506c9165f1108488` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/score/B_owner_checks.jsonl` | 125,884 | `ad73f361a1040dcf7c935bdc31349d582ca723106e348f1a264b1091b0e92419` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/score/C_mapped_lines.jsonl.gz` | 6,129,534 | `3fcf127b5aa20979b9f419936f950e47ad1ef8bc1cfa9458e75592708e8330a6` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/score/C_owner_checks.jsonl` | 125,904 | `084b7121505b4e1c3fbb98f71903cd95f06b72888fa1d7fac0a108593f2a6df3` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/score/D_mapped_lines.jsonl.gz` | 6,116,572 | `42f9f1038339a016d12e73f30125029e4c22da86d0748af7a08db8d6ae3dffb3` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/score/D_owner_checks.jsonl` | 125,723 | `ba001fa373391a00ad3a504399d2fa4f7940b7ae02660b5cff48ea78fa1186e0` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/score/E_mapped_lines.jsonl.gz` | 6,147,451 | `5844fda9f5ce4f790178cb1c79564eb9a4a1c752f56d2e7eb308208d880fcaba` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/score/E_owner_checks.jsonl` | 126,091 | `b52b28754e258ffbf25e3429c8c08417d3d735748155aee2fb7a53088ad78885` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/score/RESULT.md` | 7,044 | `d76b147c7fdb8a83c3d4573e099ef497f575ee80f303363b002cbce3023f4707` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/score/metrics.json` | 243,706 | `b1f51d6fb7a6ca93d3b00142288c0f8b5959521bed888fa91cf52a313a06b227` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/mock_font/score/score_receipt.json` | 674 | `b43dc4207b7b63f02162373edc6eb272516847a40fe6048a81d3f294efb08c6f` | provenance | copy optional (owner) |
| `artifacts/labelfix_r1/output_3678928/A/DONE` | 238 | `68876d26287a00c0a9759455bd41d064491d30d231f430a8c0ca0b1789ceb36a` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/A/best.pt` | 7,126,713 | `719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/A/data_provenance.json` | 84,147 | `915c4504b58337c916ea83f3eeff835d0db9862db85240fb107fd0c29c699895` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/A/heldout_predictions.jsonl` | 1,670,691 | `ab004f66dfa8ee6079082f99a6d7c9765ad34b804a21b9b2bec253fddc750083` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/A/heldout_predictions.receipt.json` | 470 | `b5012703c7c7b2d5b515a5a584ee7500b27c940d560b1f1e6d26596b24ade8db` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/A/owner_predictions.jsonl` | 50,595 | `6cda67b4e5534f9babcfb0830e146bae6b01977635e6b1dc80a374d24d53f9f2` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/A/owner_predictions.receipt.json` | 468 | `541943ab1bd4f307eeb55765995bfea217ef87eeb586c308d46a1e64516f8550` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/A/run_binding.json` | 77,506 | `6fef7a329aa04483dbe9c659cfa9dd8ab9cf8788854b0ecef9137d8f4be9ed7d` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/A/train_log.csv` | 2,114 | `48fd7ae7d09f0dbbcbc71c3753ea8c93fdac88f5a6f094285378677a1c7f0b20` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/A/training_receipt.json` | 849 | `9597dcf59fc0b21a58b3c3244789938feac72a82a68756e8c9b82a0e35c94222` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/B/DONE` | 238 | `d108642271ce042e8ec00787c577cae252c9ef65f02aeb82a43c57ebc8a74e9d` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/B/best.pt` | 7,056,763 | `f25f16e633966ec16037099e27ee75624b9a3600d96682dca654aeded9396d69` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/B/data_provenance.json` | 84,148 | `b081ab68f8798ba5cfc8a95aa191eac4488fc9aad9305ad470755542e75f2c23` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/B/heldout_predictions.jsonl` | 1,670,612 | `be9d5f5d41bc15aef258b2a152d39f60cbb83debe3d45ec8d6f2561ed8f2e4d8` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/B/heldout_predictions.receipt.json` | 470 | `3e32e80f4b69ae62321419d0056679ae997de7a411af8c0009949089f8dcd4b5` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/B/owner_predictions.jsonl` | 50,580 | `46f678700afd235355a66fdd4f9d95501614d3df87741c903051dc521ba51b1d` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/B/owner_predictions.receipt.json` | 468 | `f216eb5078440e2551c85e44d747159eb66b65771b5727c95c72367c72c75e05` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/B/run_binding.json` | 77,507 | `55168a8759c14f7741e0126b57f512a292f7363aae17ff1deae3ce2b1e047360` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/B/train_log.csv` | 2,115 | `51cc6c859c46ae5e518b3f00d400269bab5aafad9e3afde4a86a54f84e853ef3` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/B/training_receipt.json` | 849 | `f8da28cb0d9f367231118dc4f24abd53e0f81f8bf6710c7e6a7b4dae1ea92ea8` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/C/DONE` | 238 | `be46a4ad364d99bb3d4feb896b5fd30ff546890e425840a0bff43a3b87408287` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/C/best.pt` | 7,126,713 | `a19f7ca2533c5fb3b2c44a9d78f5a57f5e3b83398cf1a206bc697bcf376efe17` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/C/data_provenance.json` | 84,148 | `1095e15c2bb679518ada4bb9a23d74ccf504522c2a79a00d1d13a903d8b775c7` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/C/heldout_predictions.jsonl` | 1,670,715 | `a5bd08ebd15f13dac6a16424f3e2989d3dc7ff2099104a1a96132901d38e4076` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/C/heldout_predictions.receipt.json` | 470 | `f3405f2a55793a1542328737af966b5f9cf95533e6b9cec88627c37dcac422f1` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/C/owner_predictions.jsonl` | 50,591 | `e3c55e61b0b3226140ef68602535273e21c5d40531ce0a341768d502120734a2` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/C/owner_predictions.receipt.json` | 468 | `0fb45113d1afc9f121a4272ed91f70e02c0b107cdd8966e3f6c34beaca9f3e8b` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/C/run_binding.json` | 77,507 | `532fdd0ddfe551f304f172d1b276e7a776465aef8926947ad2a8ca5a94df5d43` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/C/train_log.csv` | 2,105 | `bc4622d986bb098c4b8e359e84b0593bb2439f6207dd7fb063f3753a743245ae` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/C/training_receipt.json` | 848 | `b42ad7b6dcfcd0ec36d2775f3b06b13306f91346b39d1c07754519a99c57c2d1` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/D/DONE` | 238 | `122598e4cadb15ae1bf22e615be56467e364523b208a49b80b07f39f832d7a03` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/D/best.pt` | 7,126,713 | `9cca17a309c8b76a2d8bc2c2e3784cf1a59231314ed2d92fd3bd3e19ed5d23fe` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/D/data_provenance.json` | 84,151 | `c9f48d01b23a924632176c838b1bdf139964b56315291cd1da8d5ea257ce799d` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/D/heldout_predictions.jsonl` | 1,670,539 | `99282ab4dec2805dfc5e15a1ac3fea91f4d4e8c3932b8f102fd3a678adcba779` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/D/heldout_predictions.receipt.json` | 470 | `8beecd20c3e2a45b7d5f4d4c054d37fabeebb1d0fbb8d935f37b00e7bf9511ca` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/D/owner_predictions.jsonl` | 50,559 | `994b4a9cb548b1911025a609418305a22fe226320813193dbd57acb5504b7ad9` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/D/owner_predictions.receipt.json` | 468 | `44cff801dea61a22e853e41cf09fc27b3e40cd8b7b9feca1bcc6d407569c11ce` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/D/run_binding.json` | 77,510 | `afd67668047b91eea1696b6ad65f6d1c98a68139b15a56911e5d0ff3378464a9` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/D/train_log.csv` | 2,134 | `90a85b159bf132dfae678ea08e8da9056e52939860da8300bce3a57ea076a6cb` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/D/training_receipt.json` | 853 | `598804ff8a4ea9d001bfe06d3db4ba7abcb635e483f78e9db8ba778f29b9f60b` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/E/DONE` | 238 | `9624b394c896d62d87bcdf62334548cc9c87ea57ab5858d4f6a2a3a4a9da48da` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/E/best.pt` | 7,126,713 | `330b43a04dc47425d3da977f06f28aaa54bee681700d81feef0bcb8ea1ed42c5` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/E/data_provenance.json` | 84,153 | `3a9331394bba707a7fd911b200894369e17b58df881b8a3b827e99a91251819b` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/E/heldout_predictions.jsonl` | 1,670,671 | `0a691d369aa7e61fb52f5724b6c7b08dc1f49c1cbc84bcbb322a9f03406841c5` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/E/heldout_predictions.receipt.json` | 470 | `8fbf2ea2a26310cfc33aa7a4dad21f7e5c0c9a5582f00867cc9afba2dc639471` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/E/owner_predictions.jsonl` | 50,579 | `edb1fb8a80ab310cbbf83393c64a090f275818c4ba6241ddc3ed268b29cbaba0` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/E/owner_predictions.receipt.json` | 468 | `a17a0c564ac8b7503439f3ce2f0461769180b51e59c61a09743582bb5b483f2a` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/E/run_binding.json` | 77,512 | `cac266d5b9bb0551d0790e88c164eb70b65242176ec7628e31ece5ac17bc3256` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/E/train_log.csv` | 2,122 | `8988c4ac32030c66cf89b2b475307495653bcbd0458a860561c962926a5f2f02` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/E/training_receipt.json` | 855 | `9bc8df7bb313fe7e82932030ff44981a9125b71ae7b7e50ea84bd7a66f3f0990` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/R1_3678928.log` | 34,197 | `0e65d0c98ee4c7838fb72aa27c8d9b8513431ee52c06fd5374bfd83f404aec32` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/RESULT.md` | 7,672 | `4b5cc7215a651c93cd7105f946ab50a5e88868384c24ab91855c1d397764b4ad` | LOAD-BEARING | COPY (main has a different 385 B stub) |
| `artifacts/labelfix_r1/output_3678928/owner_extra/extraction_receipt.json` | 2,482 | `d4bc403e0ed54e8e6c77b14b0db25f092191719842b85e319d4dcbae98ee88ec` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/owner_extra/index.npy` | 13,290 | `5972d7b883d88f9ffd4077565d9aa477ac6e6fadd41e85521ce3585d948afcac` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/owner_extra/lines.jsonl.gz` | 9,379 | `8234e880cca54c72de483d8feae98636aaec86c1089d031c5b4839cf036ff7f8` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/owner_extra/shard-00000-index.npy` | 13,290 | `5972d7b883d88f9ffd4077565d9aa477ac6e6fadd41e85521ce3585d948afcac` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/owner_extra/shard-00000-lines.jsonl.gz` | 9,381 | `64402edf847fe9d76dafa552cb456bbe20e9706d128daeaebc83b2456d91122c` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/owner_extra/shard-00000-narrow.npy` | 2,809,984 | `cf89495756045bfc0ccd7d1081e98ad14c4e3b177b4d6c6038114ee265cd1275` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/owner_extra/shard-00000-wide.npy` | 2,809,984 | `868af8be69e94223f945c29c19b4ce09ff181ca222804a47dc69e80d39185eab` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/run_binding.json` | 2,585 | `2af093a1e6478c1979e4e74dc4d0846158945b2e438ed4c4d42bdefe09f400f1` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/output_3678928/run_receipt.json` | 4,941 | `59de9d782b8505a17d4a456e477ea397daca4051f409f164c1e26d170a1d00e1` | LOAD-BEARING | already in main (identical, untracked): no copy needed |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/A_mapped_lines.jsonl.gz` | 6,207,710 | `1647c1ee69d60af24b006826ea1542b87b45465c58e7243ede5ee00c5f32360a` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/A_owner_checks.jsonl` | 124,071 | `177c3af21db5107c9e0f81a38acb322f54ffcf87b445055cfd626fac0ba94bad` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/B_mapped_lines.jsonl.gz` | 6,208,190 | `352e949d64dbd26690545dfc776ddb177927e0f9c9e6c09d6a446ac034453f69` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/B_owner_checks.jsonl` | 124,075 | `c18b1e6ebe24953c4738c0858b692619400ed99c7bdc1e7436f984493b280c93` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/C_mapped_lines.jsonl.gz` | 6,209,259 | `f14a1b93379d1c278bacd5b81c8a4930d0949dba35a9e2fde694a7679be85775` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/C_owner_checks.jsonl` | 124,066 | `d054a63bacc61cc9980ed9d59cd44322aa93f251ba0097f93cfbdb240ea08cea` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/D_mapped_lines.jsonl.gz` | 6,207,168 | `e45f9c79f8d034ec600c01a10b8044bef670feba0327d912986af9828bed352d` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/D_owner_checks.jsonl` | 124,083 | `eb004e95d85a14a02647c51d75f1f160a00729c1b1466b32e98cb741f1a4d1ff` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/E_mapped_lines.jsonl.gz` | 6,208,281 | `5cad5627bf7e9dfb04198a7c503712e3755b901b79a55d6ee6a17ddeedad2c5e` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/E_owner_checks.jsonl` | 124,074 | `3149c6d255330437a4b921695acc8c26cd9bb4ba00a003112346cc982c2904d2` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/RESULT.md` | 7,672 | `4b5cc7215a651c93cd7105f946ab50a5e88868384c24ab91855c1d397764b4ad` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/error_types.json` | 1,378 | `fc6c92c0a660931ed814b49b8713c64a36674fe4c875df897da5db52e4aeee06` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/metrics.json` | 280,604 | `8d64647ba551049ade70db7acb085a801bf63c8baa8afd2d52f112d667502e36` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/score_3678928_K1c_vsS6/score_receipt.json` | 675 | `bfaf3b6d86ad359d5c7078c71821b4b7439497c7d38fc8a7798517c7df7d1169` | LOAD-BEARING | COPY |
| `artifacts/labelfix_r1/score_3678928_vsS5/A_mapped_lines.jsonl.gz` | 6,097,414 | `27031aed1b9e3c132cf2c9c531dcd0756775e8e4766f4f380431a3ab2f2b1699` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS5/A_owner_checks.jsonl` | 124,072 | `33676d31c1344f3315c5aab78503103851dab1536c33e699bfe15793c8dfc9b0` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS5/B_mapped_lines.jsonl.gz` | 6,097,006 | `b4f898dde06ed7feb16b894085cab37a471be84a2733bc965c4667155f01b6e5` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS5/B_owner_checks.jsonl` | 124,075 | `c18b1e6ebe24953c4738c0858b692619400ed99c7bdc1e7436f984493b280c93` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS5/C_mapped_lines.jsonl.gz` | 6,097,378 | `e384c3338a92334a92cd05b3a22f0823f74d67a98641af51fe1c5837dd3ab2ee` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS5/C_owner_checks.jsonl` | 124,066 | `d054a63bacc61cc9980ed9d59cd44322aa93f251ba0097f93cfbdb240ea08cea` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS5/D_mapped_lines.jsonl.gz` | 6,096,775 | `1382ad08bd50b30887ba1a813bcf4d955eef3209c1026ae256897884a6cc54df` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS5/D_owner_checks.jsonl` | 124,083 | `eb004e95d85a14a02647c51d75f1f160a00729c1b1466b32e98cb741f1a4d1ff` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS5/E_mapped_lines.jsonl.gz` | 6,097,392 | `d977b077b6d5ddcefa8aa7854c99e4c5ad07f46ce929110427688b056fc110e2` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS5/E_owner_checks.jsonl` | 124,074 | `3149c6d255330437a4b921695acc8c26cd9bb4ba00a003112346cc982c2904d2` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS5/RESULT.md` | 7,653 | `722592f37e656362b18fa029e33c0072b4c4b3d7be0681fc8e696f8d65cb2be7` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS5/metrics.json` | 280,315 | `98fe6263be10a1af43adbd5a50beb90e23504bbdd2d3539dbbe7898545a86b2f` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS5/score_receipt.json` | 675 | `99f344465ca18744a707eca28a8eb16069d33af43b5d4d2d64d81443e587378f` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS6/A_mapped_lines.jsonl.gz` | 6,097,414 | `0881cacae40955a0e7063da5940614f47ce2eaad41bd6e73cad75b9f123683d7` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS6/A_owner_checks.jsonl` | 124,072 | `33676d31c1344f3315c5aab78503103851dab1536c33e699bfe15793c8dfc9b0` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS6/B_mapped_lines.jsonl.gz` | 6,097,006 | `b8511c73e7a33b419a64012cbe27ceffb64fe30b3d0402cc396bbdf708a1a83b` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS6/B_owner_checks.jsonl` | 124,075 | `c18b1e6ebe24953c4738c0858b692619400ed99c7bdc1e7436f984493b280c93` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS6/C_mapped_lines.jsonl.gz` | 6,097,378 | `49f9167f94c7877b4a223e26045ac0a06a47b4a41fb4cab0b969a2f3046a23d3` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS6/C_owner_checks.jsonl` | 124,066 | `d054a63bacc61cc9980ed9d59cd44322aa93f251ba0097f93cfbdb240ea08cea` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS6/D_mapped_lines.jsonl.gz` | 6,096,775 | `9140efcc5f45da7072ff2de347599996e0807ba7f5cd7827232d7f8e1cae7201` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS6/D_owner_checks.jsonl` | 124,083 | `eb004e95d85a14a02647c51d75f1f160a00729c1b1466b32e98cb741f1a4d1ff` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS6/E_mapped_lines.jsonl.gz` | 6,097,392 | `9335c84c6b37c5c06f2bd0d1bac560d79c5cf87232f4a4e94aaca404ea828282` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS6/E_owner_checks.jsonl` | 124,074 | `3149c6d255330437a4b921695acc8c26cd9bb4ba00a003112346cc982c2904d2` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS6/RESULT.md` | 7,665 | `906f93e32744f2ed95de3813e2a1c7d07acdce383591759b7b22821e2a624aab` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS6/metrics.json` | 280,223 | `4719569a368a4e3b5da824dc4225f2f3897985ddbc68ec9eb5c609ebadd10e54` | not cited | copy optional (owner) |
| `artifacts/labelfix_r1/score_3678928_vsS6/score_receipt.json` | 675 | `efc496ef362aed611bfb5dee1da0992c679ce7096b68dff234444fb948fc1566` | not cited | copy optional (owner) |

## Appendix C: verbatim diff of s8's case.py / ink.py (NOT merged; kept frozen)

```diff
diff --git a/greekocr/labelfix/case.py b/greekocr/labelfix/case.py
index 7c867f42..fa273b21 100644
--- a/greekocr/labelfix/case.py
+++ b/greekocr/labelfix/case.py
@@ -101,24 +101,32 @@ def estimate_font(ink):
     raw={c.index:classify(ink,c) for c in ink.components if c.role in ('letter','large')}
     ink.frozen_case={c.index:dict(raw[c.index],bbox=[c.x0,c.y0,c.x1,c.y1]) for c in ink.components if c.index in raw}
     bodies=[c for c in ink.components if raw.get(c.index,{}).get('raw_pixel_class')=='lowercase_body'
-            and .65*ink.xh<=c.h<=1.15*ink.xh and .35*ink.xh<=c.w<=1.4*ink.xh]
+            and .6*ink.xh<=c.h<=1.15*ink.xh and .35*ink.xh<=c.w<=1.4*ink.xh
+            and (c.area if hasattr(c,'area') else int(component_mask(ink,c).sum()))>=.20*ink.xh*ink.xh]
     ink.font_width=float(np.median([c.w for c in bodies])) if bodies else .85*ink.xh
     if len(bodies)<4:
         ink.font_fit=dict(source='frozen_line_fallback',n=len(bodies),xh=ink.xh)
         return
     xs=np.array([c.cx for c in bodies]);ys=np.array([c.y1 for c in bodies],float)
+    # Body contacts qualify the toolkit curve's vertical gauge. A new straight
+    # line through a curved row can cross the body and turn its top into ink
+    # evidence. Retain the toolkit's per-column baseline throughout.
+    curve=np.asarray(ink.glyphs.band.bottom)
+    offsets=ys-curve[np.clip(np.rint(xs).astype(int),0,ink.width-1)]
     keep=np.ones(len(xs),bool)
     for _ in range(3):
-        fit=np.polyfit(xs[keep],ys[keep],1) if np.ptp(xs[keep]) else np.array([0.,np.median(ys[keep])])
-        residual=ys-np.polyval(fit,xs)
+        shift=float(np.median(offsets[keep]))
+        residual=offsets-shift
         med=np.median(residual[keep]);mad=np.median(abs(residual[keep]-med))
         new=abs(residual-med)<=max(2.,3*mad)
         if new.sum()<4:break
         keep=new
     height=float(np.median([c.h for c,k in zip(bodies,keep) if k]))
-    ink.bottom=np.polyval(fit,np.arange(ink.width))
+    shift=float(np.median(offsets[keep]))
+    ink.bottom=curve+shift
     ink.xh=height;ink.top=ink.bottom-height
-    ink.font_fit=dict(source='pixel_lowercase_bodies',n=int(keep.sum()),xh=height,baseline_fit=fit.tolist())
+    ink.font_fit=dict(source='pixel_lowercase_bodies',n=int(keep.sum()),xh=height,
+                      baseline_shift=shift,baseline_geometry='toolkit_curve')
 
 
 def prepare(ink,slots):
diff --git a/greekocr/labelfix/ink.py b/greekocr/labelfix/ink.py
index e4330518..1c35355b 100644
--- a/greekocr/labelfix/ink.py
+++ b/greekocr/labelfix/ink.py
@@ -35,7 +35,7 @@ import numpy as np
 from PIL import Image
 from scipy import ndimage as ndi
 
-from ..glyphs.components import line_glyphs
+from ..glyphs.components import line_glyphs, _xheight
 
 EIGHT = np.ones((3, 3), bool)
 GRID = 8
@@ -165,18 +165,21 @@ class CropInk:
 
 def analyse(image: Image.Image, *, valid_mask=None, cut_masks=None) -> CropInk:
     g = line_glyphs(image)
+    # Broken strokes can outvote complete bodies in the component-count mode.
+    # Reuse the toolkit height estimator on substantial native components,
+    # then rerun its band/role fit at that scale. No pixels or labels are added.
+    free = [c for c in g.components if not {'top', 'bottom'} & set(c.touches)
+            and c.role != 'rule' and c.darkness <= g.paper-.45*(g.paper-g.ink_level)]
+    if free:
+        area = float(np.percentile([c.area for c in free], 90))
+        substantial = [c for c in free if c.area >= .5*area
+                       and .25*c.h <= c.w <= 2*c.h and c.h >= .6*g.band.xh]
+        height = _xheight(np.array([c.h for c in substantial], float))
+        if len(substantial) >= 8 and height > 1.5*g.band.xh:
+            g = line_glyphs(image, xh_prior=height)
     xh=float(g.band.xh)
     top=np.asarray(g.band.top)
     bottom=np.asarray(g.band.bottom)
-    # Heavy joined accents can dominate the glyph pass's height estimate.
-    # Complete short bodies provide an independent, pixel-only lower mode.
-    bodies=[c.h for c in g.components if c.role=='letter' and .45*xh <= c.h <= 1.15*xh
-            and abs(c.y1-float(bottom[min(int(c.cx),g.width-1)])) <= .25*xh]
-    if len(bodies)>=5:
-        body_h=float(np.quantile(bodies,.30))
-        if body_h < .8*xh:
-            xh=body_h
-            top=bottom-xh
     result = CropInk(g.gray, g.ink, g.labels, xh, top, bottom,
                      list(g.components), float(g.paper), g.width, g.height, float(g.ink_level))
     result.glyphs = g
@@ -394,7 +397,9 @@ def mark_evidence(ink: CropInk, x0: float, x1: float, *, core_x0: float | None =
             if c.h <= MAX_MARK_HEIGHT_XH * xh and c.w <= MAX_MARK_WIDTH_XH * xh:
                 sub = component_mask(ink,c)
                 b = _blob(sub, c.y0, c.x0, 'detached', ink)
-                if not faint_letter(c, ink) and not punctuation_dot(c, ink, excluded_stems=region_ids if mark_bearer else ()) and not _reserved_for_capital(ink, c, b1):
+                if (not b.faint and b.area >= max(MIN_BLOB_AREA, .008*xh*xh)
+                        and not faint_letter(c, ink) and not punctuation_dot(c, ink, excluded_stems=region_ids if mark_bearer else ())
+                        and not _reserved_for_capital(ink, c, b1)):
                     ev.above.append(b)
         elif c.role in ('mark', 'punct', 'fragment') and c.y0 >= base - 0.2 * xh and inside:
             sub = component_mask(ink,c)
@@ -486,11 +491,11 @@ def capital_left_marks(ink, body):
     naming the breathing/accent remains the mark classifier's responsibility.
     """
     xh = ink.xh
-    left = max((c.x1 for c in ink.components if c.role == 'letter'
+    left = max((c.x1 for c in ink.components if c.role == 'letter' and c.y1 >= body.y0+.6*body.h
                 and c.x1 <= body.x0 and c.index != body.index), default=0)
     out = []
     for c in ink.components:
-        if c.role not in ('mark','punct','fragment') or not (left <= c.x0 and c.x1 <= body.x0):
+        if c.role not in ('mark','punct','fragment','letter') or not (left <= c.x0 and c.x1 <= body.x0):
             continue
         if not (body.y0-.35*xh <= c.y0 and c.y1 <= body.y0+.6*body.h
                 and .1*xh <= c.h <= .9*xh and c.w <= 1.2*xh):
```

## Appendix D: verbatim archived l1f hashed-path patch (`docs/records/archive/l1f_hashed_paths_20261017.patch`; NOT live)

The s8/l1r3 patch (`docs/records/archive/s8_l1r3_hashed_paths_20261017.patch`, 626 lines) is the intermediate 78ed28bd state of the same two files. It is in the rehearsal tree.

```diff
diff --git a/scripts/labelfix/clariden/l1_common.py b/scripts/labelfix/clariden/l1_common.py
index 9fb2371a..25518e7f 100644
--- a/scripts/labelfix/clariden/l1_common.py
+++ b/scripts/labelfix/clariden/l1_common.py
@@ -45,7 +45,8 @@ def overlay(record, runtime, variant, binding):
     # Never trust previously composed decisions under an older policy.
     mode = compose_runtime(runtime,variant.upper())
     result.update(release_policy=POLICY,evidence_sha256=mode['evidence_sha256'],opening_quotes=mode['opening_quotes'],
-        gate_decisions=[{k:s.get(k) for k in ('start','base','label_status','hold_reasons',
+        composed_text=mode['text'],
+        gate_decisions=[{k:s.get(k) for k in ('start','base','parts','label_status','hold_reasons',
             'r1_coverage','segmentation_uncertain','localisation_unknown','unnamed',
             'detector_parts','r1_parts','peer_arm','peer_prediction','peer_coverage','evidence','constraint_flags','apostrophe')}
             for s in mode['slots']])
@@ -99,11 +100,14 @@ def _overlays(task):
     return runtime['id'],{v:overlay(record,runtime,v,binding) for v in variants}
 
 
-def release(selection, runtime_paths, out, binding, source, input_receipt, variants=('presence','full'), workers=1):
+def release(selection, runtime_paths, out, binding, source, input_receipt, variants=('presence','full'), workers=1,
+            *, verified_source_sha256=None):
     """Stream both variants, with one explicit kept-line list shared by each control."""
     out = Path(out)
     out.mkdir(parents=True, exist_ok=False)
-    original_sha = sha256(source)
+    # Shard orchestration verifies the complete source before and after all
+    # shards. Avoid rereading that same full manifest twice per shard.
+    original_sha = verified_source_sha256 or sha256(source)
     selected=list(rows(selection))
     records = {r['id']: r for r in selected}
     if len(records)!=len(selected):raise ValueError('duplicate selection IDs')
@@ -158,7 +162,8 @@ def release(selection, runtime_paths, out, binding, source, input_receipt, varia
             f.close()
     if seen != set(records):
         raise ValueError(f'incomplete runtime: {len(seen)}/{len(records)}')
-    assert original_sha == sha256(source), 'original labels changed'
+    if verified_source_sha256 is None:
+        assert original_sha == sha256(source), 'original labels changed'
     for variant in handles:
         op = out / f'overlay_{variant}.jsonl.gz'
         cp = out / f'ctrl_subset_{variant}.jsonl.gz'
diff --git a/scripts/labelfix/clariden/l1r_recompose.py b/scripts/labelfix/clariden/l1r_recompose.py
index c28bdf9f..21e836a0 100644
--- a/scripts/labelfix/clariden/l1r_recompose.py
+++ b/scripts/labelfix/clariden/l1r_recompose.py
@@ -1,116 +1,499 @@
-"""Re-release L1-v0 saved evidence under SF2. No detector or model execution.
+"""Receipt-bound SF6c recomposition; no detector, inference or submission.
 
-Missing gate inputs cause HOLD. Old files are never written. A complete input
-run, exact selection and all shard hashes must verify before release.
+--verify-only streams SHA-256 reads in place. Independent shard workers write
+atomic receipts and support exact-input reuse after a timeout.
 """
+from __future__ import annotations
 import argparse
 from collections import Counter
+from concurrent.futures import ThreadPoolExecutor
+import hashlib
 import json
+import multiprocessing as mp
 from pathlib import Path
-from greekocr.labelfix.release_gate import policy_binding
-from scripts.labelfix.clariden.l1_common import release, rows, sha256, write_json
-
-
-def recompose(input_run, selection, binding_dir, source, out, ensemble_run=None, workers=1):
-    base,out=Path(input_run),Path(out)
-    if out.resolve()==base.resolve() or base.resolve() in out.resolve().parents:
-        raise ValueError('L1r output must be separate from historical run')
-    run=json.loads((base/'run_receipt.json').read_text())
-    if not run.get('complete'):raise ValueError('incomplete historical run')
-    paths=sorted((base/'combined').glob('shard-*-combined.jsonl.gz'))
-    if not paths:raise ValueError('no saved combined shards')
-    inputs={str(selection):sha256(selection),str(source):sha256(source)}
-    inputs[str(base/'run_receipt.json')]=sha256(base/'run_receipt.json')
-    binding_path=Path(binding_dir)/'binding.json'
-    if sha256(binding_path)!=run['binding_sha256']:raise ValueError('historical binding changed')
-    inputs[str(binding_path)]=sha256(binding_path)
-    for name,digest in run['step_receipts'].items():
-        if sha256(base/name)!=digest:raise ValueError('historical step receipt changed: '+name)
-        inputs[str(base/name)]=digest
-    ids=[];missing=Counter();apostrophes=0
-    for path in paths:
-        receipt=json.loads(path.with_name(path.name.replace('-combined.jsonl.gz','-receipt.json')).read_text())
-        if not receipt.get('complete') or receipt['output_sha256']!=sha256(path):raise ValueError('invalid shard '+str(path))
-        inputs[str(path)]=sha256(path)
-        for r in rows(path):
-            ids.append(r['id'])
-            for key in ('detector','r1_predictions','coverage','recogniser_text'):
-                if key not in r:raise ValueError('missing line input '+key)
-            for c in r['coverage']:
-                for key in ('scored','evidence_state','uncertainty'):
-                    if key not in c:missing['r1_'+key]+=1
-            for s in r['detector']['slots']:
-                if 'segmentation_uncertain' not in s:missing['detector_segmentation_state']+=1
-                for k in ('clipped_top','clipped_bottom'):
-                    if k not in s.get('evidence',{}):missing[k]+=1
-                if s.get('apostrophe') and not s.get('evidence',{}).get('apostrophes'):apostrophes+=1
-    selected=list(rows(selection))
-    if len(ids)!=len(set(ids)) or set(ids)!={r['id'] for r in selected}:raise ValueError('runtime/selection mismatch')
-    for v in ('presence','full'):
-        manifest=json.loads((base/'release'/f'release_{v}.json').read_text())
-        inputs[str(base/'release'/f'release_{v}.json')]=sha256(base/'release'/f'release_{v}.json')
-        if manifest['source_sha256']!=sha256(source) or manifest['selection_sha256']!=sha256(selection):raise ValueError('source/selection changed')
-        for name,key in [('overlay','overlay_sha256'),('kept_line_ids','kept_line_ids_sha256')]:
-            if sha256(base/'release'/manifest[name])!=manifest[key]:raise ValueError('historical release hash mismatch')
-            inputs[str(base/'release'/manifest[name])]=manifest[key]
-        control=json.loads((base/'release'/f'release_ctrl_subset_{v}.json').read_text())
-        if sha256(base/'release'/control['labels_file'])!=control['labels_sha256']:raise ValueError('historical control changed')
-        inputs[str(base/'release'/control['labels_file'])]=control['labels_sha256']
-    if missing:raise ValueError('saved evidence incomplete; regenerate missing fields: '+str(dict(missing)))
-    runtime_paths=paths;ensemble=None
+import shutil
+import time
+import uuid
+from greekocr.labelfix.release_gate import MODES, POLICY, ENSEMBLE_CAVEAT, compose_runtime, policy_binding
+from scripts.labelfix.clariden.l1_common import STATUSES, canonical, label_sha, release, rows, sha256, write_json
+from scripts.labelfix.clariden.r1_common import write_rows
+
+VARIANTS = ('presence', 'full', 'ensemble_ab')
+_RECORDS = {}
+
+
+def load(path):
+    return json.loads(Path(path).read_text())
+
+
+def digest(value):
+    return hashlib.sha256(canonical(value).encode()).hexdigest()
+
+
+def atomic_json(path, value):
+    path = Path(path)
+    tmp = path.with_name(path.name + '.partial')
+    write_json(tmp, value)
+    tmp.replace(path)
+
+
+def separate_output(out, *inputs):
+    out = Path(out).resolve()
+    for original in inputs:
+        original = Path(original).resolve()
+        if out == original or original in out.parents or out in original.parents:
+            raise ValueError('output must be separate from historical inputs: ' + str(original))
+
+
+def verify_inputs(input_run, selection, binding_dir, source, ensemble_run=None, *, expected=None, workers=4):
+    """Verify the receipt DAG before creating releases; never loads pixels.
+
+    L1E's downstream recomposition/run receipt is deliberately not required.
+    Completion follows the complete inference receipt and every shard receipt.
+    """
+    started = time.monotonic()
+    base, selection, source = Path(input_run), Path(selection), Path(source)
+    inputs = {}
+
+    def checked(path, wanted=None):
+        path = Path(path)
+        got = sha256(path)
+        if wanted is not None and got != wanted:
+            raise ValueError('hash mismatch: ' + str(path))
+        if str(path) in inputs and inputs[str(path)] != got:
+            raise ValueError('input changed: ' + str(path))
+        inputs[str(path)] = got
+        return got
+
+    for name, wanted in (expected or {}).items():
+        checked(name, wanted)
+    checked(base / 'run_receipt.json')
+    run = load(base / 'run_receipt.json')
+    if not run.get('complete'):
+        raise ValueError('incomplete historical run')
+    bp = Path(binding_dir) / 'binding.json'
+    checked(bp, run['binding_sha256'])
+    binding = load(bp)
+    for name, wanted in run['step_receipts'].items():
+        checked(base / name, wanted)
+    checked(selection)
+    inp = load(base / 'input_receipt.json')
+    # The saved L1E mock predates the source field in input_receipt. Its
+    # source is byte-identical to its pinned, verification-only selection.
+    if 'source_sha256' not in inp:
+        if not (run.get('mock') and run.get('verification_only') and sha256(source) == inputs[str(selection)]):
+            raise ValueError('missing historical source binding')
+        inp['source_sha256'] = inputs[str(selection)]
+    checked(source, inp['source_sha256'])
+    if binding.get('source_sha256', inputs[str(source)]) != inputs[str(source)]:
+        raise ValueError('binding source mismatch')
+    top = load(base / 'detector/detector_receipt.json')
+    if not top.get('complete') or top['selection_sha256'] != inputs[str(selection)]:
+        raise ValueError('detector selection mismatch/incomplete')
+    selected = list(rows(selection))
+    ids = [r['id'] for r in selected]
+    if len(ids) != len(set(ids)) or len(ids) != run['lines'] or top['lines'] != len(ids):
+        raise ValueError('selection line count/uniqueness mismatch')
+    entries = sorted(top['shards'], key=lambda e: e['shard'])
+    numbers = [e['shard'] for e in entries]
+    if numbers != list(range(len(entries))):
+        raise ValueError('missing/duplicate detector shard')
+    expected_files, tasks = {}, []
+    for e in entries:
+        n = e['shard']
+        dp = base / 'detector' / f'shard-{n:05d}-receipt.json'
+        if str(dp) not in inputs or load(dp) != e or not e.get('complete'):
+            raise ValueError('unbound/incomplete detector shard: ' + str(n))
+        for name, wanted in e['sha256'].items():
+            expected_files[str(base / 'detector' / name)] = wanted
+        rp = base / 'combined' / f'shard-{n:05d}-receipt.json'
+        if str(rp) not in inputs:
+            raise ValueError('unbound A shard: ' + str(n))
+        ar = load(rp)
+        if not ar.get('complete') or ar['lines'] != e['lines'] or ar['samples'] != e['windows']:
+            raise ValueError('incomplete A inference shard: ' + str(n))
+        p = base / 'combined' / ar.get('output', f'shard-{n:05d}-combined.jsonl.gz')
+        expected_files[str(p)] = ar['output_sha256']
+        tasks.append(dict(shard=n, lines=e['lines'], samples=e['windows'], historical=str(p), runtime=str(p)))
+    if {p.name for p in (base / 'combined').glob('shard-*-combined.jsonl.gz')} != {Path(t['historical']).name for t in tasks}:
+        raise ValueError('unexpected/missing A shard files')
+    if sum(t['lines'] for t in tasks) != len(selected):
+        raise ValueError('shard population differs from selection')
+    peer = None
     if ensemble_run is not None:
-        ensemble_run=Path(ensemble_run)
-        ep=ensemble_run/'r1e_receipt.json';ensemble=json.loads(ep.read_text())
-        if not ensemble.get('complete') or ensemble['historical_run_receipt_sha256']!=sha256(base/'run_receipt.json'):
-            raise ValueError('ensemble not bound to completed historical run')
-        if ensemble['selection_sha256']!=sha256(selection):raise ValueError('ensemble selection changed')
-        inputs[str(ep)]=sha256(ep);runtime_paths=[]
-        for entry in ensemble['shards']:
-            rp=ensemble_run/entry['receipt'];sr=json.loads(rp.read_text())
-            if sha256(rp)!=entry['receipt_sha256'] or not sr['complete']:raise ValueError('ensemble shard receipt changed')
-            p=ensemble_run/sr['output']
-            if sha256(p)!=sr['output_sha256']:raise ValueError('ensemble shard changed')
-            inputs[str(rp)]=sha256(rp);inputs[str(p)]=sha256(p);runtime_paths.append(p)
-        if len(runtime_paths)!=len(paths):raise ValueError('ensemble shards missing')
-    out.mkdir(parents=True,exist_ok=False)
-    binding=json.loads(binding_path.read_text())
-    policy=policy_binding();binding['historical_policy_sha256']=binding['policy_sha256'];binding['policy_sha256']=policy['sha256']
-    binding['code_commit']='uncommitted-SF2-source-bound'
-    binding.update(policy_binding=policy,code_sha256=policy['sources'])
-    if ensemble is not None:
-        binding.update(checkpoint_sha256=ensemble['checkpoint_sha256'],code_commit='e48e06e8+L1E-source-bound',
-                       code_sha256=ensemble['code_sha256'])
-    inp=json.loads((base/'input_receipt.json').read_text())
-    variants=('presence','full','ensemble_ab') if ensemble is not None else ('presence','full')
-    counts=release(selection,runtime_paths,out/'release',binding,source,inp,variants,workers)
-    changes={}
-    for v in ('presence','full'):
-        old={r['line_id']:r for r in rows(base/'release'/f'overlay_{v}.jsonl.gz')}
-        delta=[]
-        for r in rows(out/'release'/f'overlay_{v}.jsonl.gz'):
-            a=old[r['line_id']]
-            if (a['status'],a.get('label'))!=(r['status'],r.get('label')):
-                delta.append(dict(line_id=r['line_id'],before=a['status'],after=r['status'],
-                    reasons=sorted({s['detail'] for s in r['hold_slots']})))
-        write_json(out/f'decision_changes_{v}.json',delta)
-        changes[v]=dict(changed=len(delta),reasons=dict(Counter(z for d in delta for z in d['reasons'])))
-    if any(sha256(Path(p))!=h for p,h in inputs.items()):raise ValueError('input changed during recomposition')
-    receipt=dict(schema='l1r-recomposition-v1',complete=True,policy=policy,inputs=inputs,
-        historical_run=str(base),counts=counts,changes=changes,evidence_sufficient=True,
-        historical_apostrophe_boxes_missing=apostrophes,network=False,detector_runs=0,r1_runs=0,
-        ensemble_receipt_sha256=inputs.get(str(Path(ensemble_run)/'r1e_receipt.json')) if ensemble_run else None,
-        outputs={str(p.relative_to(out)):sha256(p) for p in sorted(out.rglob('*')) if p.is_file()})
-    write_json(out/'receipt.json',receipt)
+        ep = Path(ensemble_run) / 'r1e_receipt.json'
+        checked(ep)
+        peer = load(ep)
+        if not peer.get('complete') or peer['historical_run_receipt_sha256'] != inputs[str(base / 'run_receipt.json')]:
+            raise ValueError('incomplete/unbound B/E inference')
+        if peer['selection_sha256'] != inputs[str(selection)] or peer['lines'] != len(selected):
+            raise ValueError('B/E selection mismatch')
+        if set(peer['checkpoint_sha256']) != {'A', 'B', 'E'} or peer['checkpoint_sha256']['A'] != binding['r1_sha256']:
+            raise ValueError('B/E checkpoint mismatch')
+        bynumber = {}
+        for e in peer['shards']:
+            rp = Path(ensemble_run) / e['receipt']
+            checked(rp, e['receipt_sha256'])
+            sr = load(rp)
+            n = sr['shard']
+            if n in bynumber or n not in numbers or not sr.get('complete'):
+                raise ValueError('missing/duplicate/incomplete B/E shard')
+            t = tasks[n]
+            if (sr['lines'], sr['samples']) != (t['lines'], t['samples']) or (e['lines'], e['samples']) != (t['lines'], t['samples']):
+                raise ValueError('incomplete B/E inference population')
+            si = sr['inputs']
+            dr = base / 'detector' / f'shard-{n:05d}-receipt.json'
+            if (si['historical_combined_sha256'] != expected_files[t['historical']]
+                    or si['window_receipt_sha256'] != inputs[str(dr)]
+                    or si['checkpoint_sha256'] != peer['checkpoint_sha256']
+                    or si['code_sha256'] != peer['code_sha256']):
+                raise ValueError('B/E shard input binding mismatch')
+            p = Path(ensemble_run) / sr['output']
+            expected_files[str(p)] = sr['output_sha256']
+            bynumber[n] = str(p)
+        if set(bynumber) != set(numbers) or peer['samples'] != sum(t['samples'] for t in tasks):
+            raise ValueError('B/E inference incomplete for one or more shards')
+        for t in tasks:
+            t['runtime'] = bynumber[t['shard']]
+        if {p.name for p in Path(ensemble_run).glob('shard-*-combined.jsonl.gz')} != {Path(p).name for p in bynumber.values()}:
+            raise ValueError('unexpected/missing B/E shard files')
+
+    def hash_file(item):
+        name, wanted = item
+        if sha256(name) != wanted:
+            raise ValueError('hash mismatch: ' + name)
+        return name, wanted
+
+    with ThreadPoolExecutor(max_workers=workers) as pool:
+        inputs.update(pool.map(hash_file, expected_files.items()))
+    result = dict(schema='l1r-input-verification-v1', complete=True, lines=len(selected),
+                  shards=len(tasks), samples=sum(t['samples'] for t in tasks),
+                  inputs=inputs, inputs_sha256=digest(inputs), historical_run=str(base),
+                  ensemble_run=str(ensemble_run) if ensemble_run else None,
+                  checkpoint_sha256=peer['checkpoint_sha256'] if peer else {'A': binding['r1_sha256']},
+                  historical_inference_code_sha256=peer['code_sha256'] if peer else {},
+                  elapsed_seconds=time.monotonic() - started)
+    return result, tasks, selected, binding, inp
+
+
+def decision_record(runtime):
+    return {m: compose_runtime(runtime, m) for m in MODES}
+
+
+def validate_release(out, selected, variants):
+    """Read actual overlay/control payloads, not aliases of an in-memory set."""
+    out = Path(out)
+    records = {r['id']: r for r in selected}
+    for v in variants:
+        m = load(out / f'release_{v}.json')
+        c = load(out / f'release_ctrl_subset_{v}.json')
+        name = v.replace('_', '-')
+        if m['release'] != f'v2-corrected-{name}-sf6' or c['release'] != f'v2-ctrl-subset-{name}-sf6':
+            raise ValueError('invalid SF5 release name')
+        for manifest in (m, c):
+            if manifest['release_policy'] != POLICY or manifest['ensemble_caveat'] != ENSEMBLE_CAVEAT:
+                raise ValueError('invalid policy/caveat')
+            if sha256(out / manifest['input_verification_file']) != manifest['input_verification_sha256']:
+                raise ValueError('input verification receipt changed')
+            for key, hk in [('overlay', 'overlay_sha256'), ('kept_line_ids', 'kept_line_ids_sha256')]:
+                if sha256(out / manifest[key]) != manifest[hk]:
+                    raise ValueError('release payload hash mismatch')
+        if sha256(out / c['labels_file']) != c['labels_sha256']:
+            raise ValueError('control hash mismatch')
+        seen, accepted, counts = set(), set(), Counter()
+        for r in rows(out / m['overlay']):
+            i = r['line_id']
+            if r['status'] not in STATUSES:
+                raise ValueError('invalid release status')
+            if i in seen or i not in records or r['original_label_sha256'] != label_sha(records[i]['label']):
+                raise ValueError('overlay original label/ID mismatch')
+            seen.add(i)
+            counts[r['status']] += 1
+            if r['status'] in ('corrected', 'unchanged'):
+                if r['hold_slots']:
+                    raise ValueError('HOLD line admitted')
+                accepted.add(i)
+            elif 'label' in r:
+                raise ValueError('excluded line has release label')
+        kept = (out / m['kept_line_ids']).read_text().splitlines()
+        controls = list(rows(out / c['labels_file']))
+        if (seen != set(records) or len(kept) != len(set(kept)) or set(kept) != accepted
+                or len(controls) != len(accepted) or {r['line_id'] for r in controls} != accepted
+                or m['kept_lines'] != len(accepted) or dict(counts) != {k: n for k, n in m['counts_by_status'].items() if n}):
+            raise ValueError('release/control population mismatch')
+        for r in controls:
+            if r['label'] != records[r['line_id']]['label'] or r['original_label_sha256'] != label_sha(r['label']):
+                raise ValueError('control label modified')
+        for dimension in ('coverage_per_wave', 'coverage_per_source'):
+            if sum(b['total'] for b in m[dimension].values()) != len(records):
+                raise ValueError('coverage population mismatch')
+    return dict(complete=True, lines=len(records), variants=list(variants),
+                original_label_sha_every_line=True, hold_excluded=True, exact_control_pairing=True)
+
+
+def _initialise(selection):
+    global _RECORDS
+    _RECORDS = {r['id']: r for r in rows(selection)}
+
+
+def code_sources():
+    root = Path(__file__).resolve().parents[3]
+    paths = sorted((root / 'greekocr').rglob('*.py')) + sorted((root / 'scripts/labelfix').rglob('*.py'))
+    paths.append(root / 'scripts/labelfix/clariden/l1r_job.sbatch')
+    paths.extend(root / 'scripts/labelfix/clariden' / name for name in
+                 ('l1r4_job.sbatch', 'l1r4_census_job.sbatch', 'l1r4_preflight.sh')
+                 if (root / 'scripts/labelfix/clariden' / name).exists())
+    return {str(p.relative_to(root)): sha256(p) for p in paths}
+
+
+def _shard(task):
+    t, out, binding, source, inp, audit = task
+    started = time.monotonic()
+    runtime = list(rows(t['runtime']))
+    if any(r['id'] not in _RECORDS for r in runtime):
+        raise ValueError('unexpected runtime ID')
+    selected = [_RECORDS[r['id']] for r in runtime]
+    dest = Path(out) / 'shards' / f'shard-{t["shard"]:05d}'
+    reuse_binding = dict(runtime_sha256=sha256(t['runtime']), selection_sha256=digest(selected), binding=binding, audit=audit)
+    rp = dest / 'receipt.json'
+    if rp.exists():
+        r = load(rp)
+        if not r.get('complete') or r['inputs'] != reuse_binding:
+            raise ValueError('stale recomposition shard receipt')
+        for name, wanted in r['outputs'].items():
+            if sha256(dest / name) != wanted:
+                raise ValueError('recomposition shard output changed')
+        return r
+    historical = list(rows(t['historical']))
+    byid = {r['id']: r for r in selected}
+    if len(runtime) != t['lines'] or len(historical) != t['lines'] or len(byid) != t['lines']:
+        raise ValueError('runtime shard count mismatch')
+    if [r['id'] for r in runtime] != [r['id'] for r in historical] or {r['id'] for r in runtime} != set(byid):
+        raise ValueError('runtime/selection shard identity mismatch')
+    for r, old in zip(runtime, historical):
+        for k in ('detector', 'recogniser_text', 'coverage', 'r1_predictions'):
+            if r[k] != old[k]:
+                raise ValueError('L1E historical evidence changed: ' + k)
+        for k in ('recogniser_nfd', 'recognition_confidence', 'recognition_evidence', 'image_width'):
+            if (k in r, r.get(k)) != (k in old, old.get(k)):
+                raise ValueError('L1E historical evidence changed: ' + k)
+        if 'ensemble_ab' in binding['variants']:
+            want = [(p['start'], p['base']) for p in r['r1_predictions']]
+            if len(want) != len(set(want)):
+                raise ValueError('duplicate A prediction')
+            for arm in ('B', 'E'):
+                ps = r.get('peer_predictions', {}).get(arm)
+                cov = r.get('peer_coverage', {}).get(arm)
+                if ps is None or cov is None or [(p['start'], p['base']) for p in ps] != want or cov != r['coverage']:
+                    raise ValueError('B/E inference incomplete: ' + r['id'] + ':' + arm)
+    partial = dest.with_name(dest.name + '.partial-' + uuid.uuid4().hex)
+    partial.mkdir(parents=True)
+    sp = partial / 'selection.jsonl'
+    write_rows(sp, selected)
+    runtime_path = t['runtime']
+    if 'l1f_join' in binding:
+        from scripts.labelfix.clariden.l1r4_join import join_runtime
+        runtime = join_runtime(runtime, Path(out) / 'l1f_join.sqlite')
+        runtime_path = partial / 'joined-runtime.jsonl.gz'
+        write_rows(runtime_path, runtime)
+    counts = release(sp, [runtime_path], partial / 'release', binding, source, inp, binding['variants'], workers=1,
+                     verified_source_sha256=inp['source_sha256'])
+    # Packaging census only: consume the frozen composer's actual overlays.
+    elisions = {}
+    for variant in binding['variants']:
+        fields = ('google', 'recogniser', 'both', 'google_only', 'recogniser_only',
+                  'both_kept', 'both_deleted', 'google_only_kept', 'google_only_deleted',
+                  'recogniser_only_kept', 'recogniser_only_deleted', 'added',
+                  'spacing_breathings', 'spacing_breathings_attached', 'aligned_lines', 'unaligned_lines')
+        all_rows, released = Counter(dict.fromkeys(fields, 0)), Counter(dict.fromkeys(fields, 0))
+        for row in rows(partial / 'release' / f'overlay_{variant}.jsonl.gz'):
+            c = row.get('elision_census')
+            if c is None:
+                continue
+            summary = {k: v for k, v in c.items() if k != 'aligned'}
+            summary.update(aligned_lines=int(c['aligned']), unaligned_lines=int(not c['aligned']))
+            all_rows.update(summary)
+            if row['status'] in ('corrected', 'unchanged'):
+                released.update(summary)
+        elisions[variant] = dict(elision_census=dict(all_rows), elision_census_released=dict(released))
+    for p in (partial / 'release').glob('release_*.json'):
+        m = load(p)
+        m['release'] = m['release'].removesuffix('-r') + '-sf6'
+        if 'paired_release' in m:
+            m['paired_release'] = m['paired_release'].removesuffix('-r') + '-sf6'
+        m.update(**elisions[m['variant']])
+        m.update(input_verification_file='../../../input_verification.json',
+                 input_verification_sha256=binding['input_verification_sha256'],
+                 input_hashes_sha256=binding['input_hashes_sha256'],
+                 historical_inference_code_sha256=binding['historical_inference_code_sha256'])
+        write_json(p, m)
+    validation = validate_release(partial / 'release', selected, binding['variants'])
+    if audit:
+        write_rows(partial / 'decisions.jsonl.gz', [dict(id=r['id'], decisions=decision_record(r)) for r in runtime])
+    r = dict(schema='l1r-recomposition-shard-v1', complete=True, shard=t['shard'], lines=len(runtime),
+             inputs=reuse_binding, counts=counts, validation=validation, elapsed_seconds=time.monotonic()-started,
+             outputs={str(p.relative_to(partial)): sha256(p) for p in sorted(partial.rglob('*')) if p.is_file()})
+    atomic_json(partial / 'receipt.json', r)
+    partial.rename(dest)
+    return r
+
+
+def merge_shards(out, shards, selection, selected, variants):
+    out = Path(out)
+    if (out / 'release').exists():
+        for v in variants:
+            merged = load(out / 'release' / f'release_{v}.json')
+            shard = load(out / 'shards' / f'shard-{shards[0]["shard"]:05d}' / 'release' / f'release_{v}.json')
+            for key in ('policy_sha', 'input_hashes_sha256', 'code_sha256', 'input_verification_sha256'):
+                if merged[key] != shard[key]:
+                    raise ValueError('stale aggregated release')
+        return validate_release(out / 'release', selected, variants)
+    dest = out / ('release.partial-' + uuid.uuid4().hex)
+    dest.mkdir()
+    for v in variants:
+        manifests = [load(out / 'shards' / f'shard-{r["shard"]:05d}' / 'release' / f'release_{v}.json') for r in shards]
+        m = dict(manifests[0])
+        for prefix in ('overlay_', 'ctrl_subset_'):
+            name = prefix + v + '.jsonl.gz'
+            with (dest / name).open('wb') as target:
+                for r in shards:
+                    with (out / 'shards' / f'shard-{r["shard"]:05d}' / 'release' / name).open('rb') as f:
+                        shutil.copyfileobj(f, target, 1024 * 1024)
+        kept = sorted(i for r in shards for i in (out / 'shards' / f'shard-{r["shard"]:05d}' / 'release' / m['kept_line_ids']).read_text().splitlines())
+        (dest / m['kept_line_ids']).write_text(''.join(i + '\n' for i in kept))
+        counts = Counter({s: 0 for s in STATUSES})
+        for sub in manifests:
+            counts.update(sub['counts_by_status'])
+        m.update(input_verification_file='../input_verification.json',
+                 selection_sha256=sha256(selection), counts_by_status=dict(counts), kept_lines=len(kept),
+                 overlay_sha256=sha256(dest / m['overlay']), kept_line_ids_sha256=sha256(dest / m['kept_line_ids']))
+        m['alias_only'] = sum(sub['alias_only'] for sub in manifests)
+        for key in ('elision_census', 'elision_census_released'):
+            total = Counter()
+            for sub in manifests:
+                total.update(sub[key])
+            m[key] = dict(total)
+        for dimension in ('coverage_per_wave', 'coverage_per_source'):
+            combined = {}
+            for sub in manifests:
+                for name, b in sub[dimension].items():
+                    combined.setdefault(name, Counter({s: 0 for s in STATUSES})).update({s: b[s] for s in (*STATUSES, 'alias_only')})
+            for b in combined.values():
+                b['total'] = sum(b[s] for s in STATUSES)
+                b['kept'] = b['corrected'] + b['unchanged']
+                b['kept_fraction'] = b['kept'] / b['total']
+            m[dimension] = combined
+        write_json(dest / f'release_{v}.json', m)
+        cp = dest / f'ctrl_subset_{v}.jsonl.gz'
+        write_json(dest / f'release_ctrl_subset_{v}.json', dict(m,
+                   release=m['release'].replace('v2-corrected-', 'v2-ctrl-subset-'), labels='ORIGINAL',
+                   labels_file=cp.name, labels_sha256=sha256(cp), paired_release=m['release'],
+                   corrected_and_control_line_sets_equal=True))
+    validation = validate_release(dest, selected, variants)
+    dest.rename(out / 'release')
+    return validation
+
+
+def recompose(input_run, selection, binding_dir, source, out, ensemble_run=None, workers=1,
+              *, expected=None, audit_decisions=False, code_commit='fbf491f5+L1R3-source-bound', l1f=None):
+    started = time.monotonic()
+    separate_output(out, input_run, *([ensemble_run] if ensemble_run else []), binding_dir, source, selection)
+    verification, tasks, selected, binding, inp = verify_inputs(input_run, selection, binding_dir, source, ensemble_run,
+                                                               expected=expected, workers=min(workers, 16))
+    out = Path(out)
+    out.mkdir(parents=True, exist_ok=True)
+    join = None
+    if l1f:
+        from scripts.labelfix.clariden.l1r4_join import prepare_join
+        separate_output(out, l1f['root'])
+        join = prepare_join(l1f, selected, out, verification['inputs'])
+        verification['inputs'].update(join['inputs'])
+        verification['inputs_sha256'] = digest(verification['inputs'])
+    vr = out / 'input_verification.json'
+    if vr.exists() and load(vr)['inputs'] != verification['inputs']:
+        raise ValueError('restart inputs changed')
+    if not vr.exists():
+        atomic_json(vr, verification)
+    policy = policy_binding()
+    variants = VARIANTS if ensemble_run else VARIANTS[:2]
+    binding.update(historical_policy_sha256=binding['policy_sha256'], policy_sha256=policy['sha256'],
+                   policy_binding=policy, code_sha256=code_sources(), code_commit=code_commit,
+                   checkpoint_sha256=verification['checkpoint_sha256'], variants=list(variants),
+                   input_verification_sha256=sha256(vr), input_hashes_sha256=verification['inputs_sha256'],
+                   historical_inference_code_sha256=verification['historical_inference_code_sha256'],
+                   audit_decisions=audit_decisions)
+    if join:
+        binding['l1f_join'] = dict(receipt_sha256=sha256(out / 'l1f_join_receipt.json'),
+                                 index_sha256=sha256(out / 'l1f_join.sqlite'), spec=l1f)
+    if (out / 'receipt.json').exists():
+        prior = load(out / 'receipt.json')
+        if not prior.get('complete') or prior['policy'] != policy or prior['binding'] != binding:
+            raise ValueError('completed output binding changed')
+        for name, wanted in prior['outputs'].items():
+            if sha256(out / name) != wanted:
+                raise ValueError('completed output changed')
+        return prior
+    work = [(t, str(out), binding, str(source), inp, audit_decisions) for t in tasks]
+    if workers > 1:
+        with mp.get_context('spawn').Pool(workers, initializer=_initialise, initargs=(selection,)) as pool:
+            shards = []
+            for r in pool.imap(_shard, work, chunksize=1):
+                shards.append(r)
+                print(f'L1R_SHARD {r["shard"]} lines={r["lines"]} seconds={r["elapsed_seconds"]:.3f}', flush=True)
+    else:
+        _initialise(selection)
+        shards = list(map(_shard, work))
+    validation = merge_shards(out, shards, selection, selected, variants)
+    with ThreadPoolExecutor(max_workers=min(workers, 16)) as pool:
+        for name, got in pool.map(lambda p: (p, sha256(p)), verification['inputs']):
+            if got != verification['inputs'][name]:
+                raise ValueError('input changed during recomposition: ' + name)
+    if code_sources() != binding['code_sha256']:
+        raise ValueError('recomposition code changed during run')
+    receipt = dict(schema='l1r-recomposition-v2', complete=True, policy=policy, binding=binding,
+                   inputs_sha256=verification['inputs_sha256'], input_verification_sha256=sha256(vr),
+                   counts={v: load(out / 'release' / f'release_{v}.json')['counts_by_status'] for v in variants},
+                   validation=validation, shards=[dict(shard=r['shard'], receipt=f'shards/shard-{r["shard"]:05d}/receipt.json',
+                       receipt_sha256=sha256(out / 'shards' / f'shard-{r["shard"]:05d}' / 'receipt.json')) for r in shards],
+                   outputs={str(p.relative_to(out)): sha256(p) for p in sorted((out / 'release').glob('*'))},
+                   elapsed_seconds=time.monotonic()-started, network=False, detector_runs=0, r1_runs=0,
+                   original_labels_unchanged=True)
+    if join:
+        receipt['outputs'].update({p: sha256(out / p) for p in ('l1f_join.sqlite', 'l1f_join_receipt.json')})
+    atomic_json(out / 'receipt.json', receipt)
     return receipt
 
 
 def main():
-    ap=argparse.ArgumentParser(description=__doc__)
-    for flag in ('input-run','selection','binding-dir','source','out'):ap.add_argument('--'+flag,type=Path,required=True)
-    ap.add_argument('--ensemble-run',type=Path);ap.add_argument('--workers',type=int,default=1)
-    a=ap.parse_args()
-    r=recompose(a.input_run,a.selection,a.binding_dir,a.source,a.out,a.ensemble_run,a.workers)
-    print(json.dumps({k:v for k,v in r.items() if k not in ('inputs','outputs')},ensure_ascii=False,indent=2))
+    ap = argparse.ArgumentParser(description=__doc__)
+    for flag in ('input-run', 'selection', 'binding-dir', 'source', 'out'):
+        ap.add_argument('--'+flag, type=Path)
+    ap.add_argument('--config', type=Path)
+    ap.add_argument('--ensemble-run', type=Path)
+    ap.add_argument('--workers', type=int, default=1)
+    ap.add_argument('--verify-only', action='store_true')
+    ap.add_argument('--audit-decisions', action='store_true')
+    a = ap.parse_args()
+    cfg = load(a.config) if a.config else {}
+    args = {k: cfg.get(k, getattr(a, k)) for k in ('input_run', 'selection', 'binding_dir', 'source', 'ensemble_run')}
+    if not all(args[k] for k in ('input_run', 'selection', 'binding_dir', 'source')) or a.out is None or a.workers < 1:
+        ap.error('input paths, --out and positive --workers required')
+    expected = cfg.get('expected_sha256')
+    if a.verify_only:
+        separate_output(a.out, args['input_run'], args['binding_dir'], args['source'], args['selection'],
+                        *([args['ensemble_run']] if args['ensemble_run'] else []))
+        result = verify_inputs(**args, expected=expected, workers=a.workers)[0]
+        a.out.parent.mkdir(parents=True, exist_ok=True)
+        atomic_json(a.out, result)
+    else:
+        if not cfg.get('verification_only') and not __import__('os').environ.get('SLURM_JOB_ID'):
+            ap.error('production recomposition requires a Slurm allocation')
+        if cfg.get('verification_only') and load(Path(args['input_run']) / 'run_receipt.json')['lines'] != 64:
+            ap.error('local mock must be the complete 64-line verification runtime')
+        result = recompose(**args, out=a.out, workers=a.workers, expected=expected, audit_decisions=a.audit_decisions,
+                           l1f=cfg.get('l1f'))
+    print(json.dumps({k: v for k, v in result.items() if k not in ('inputs', 'outputs', 'shards', 'binding', 'historical_inference_code_sha256')}, ensure_ascii=False, indent=2))
 
 
-if __name__=='__main__':main()
+if __name__ == '__main__':
+    main()
```


## Lead note (17 Oct, re-run)
L1R4b was CANCELLED by the owner decision of 08:50 (the recogniser only locates); "re-run after L1R4b lands" is void. Re-run before the real merge anyway, since the branches move. Ruling needed on Options A–D for the stranded L1R line; the lead recommends C.

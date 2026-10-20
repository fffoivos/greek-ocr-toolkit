# CENSUS06-A — qualification and lead-commit handoff

This is the pre-binding package for the final 20 October lead ruling. It is not deployed. SF7 binding is PENDING; the submission guard refuses it. The lead commits; CENSUS06-B deploys committed bytes and runs the unchanged verifier and scheduler test-only checks. No jobs, reader calls, spend, Git staging or commits occurred in A. The only remote actions were read-only SSH inspection.

`package_id.json` is the authoritative package identifier and remote root. `DEPLOY_PATHS.txt` is the exact repository-relative payload, and `DEPLOY_SHA256SUMS` binds every byte. `payload_diff.json` gives every inherited before/after SHA and additive path. No inherited payload file is dropped.

## Difference from census_05

Base: segcensus branch `opus/seg-census`, deployed package `997b7d2ab5a8775b`, CODE_SHA `3b4090bf9b15d2d2cac53ee55161e936157ec0e5`. Its files were hash-checked before copying; that worktree and the main checkout were never written. The source generator is captured from `git show main:scripts/harvest/build_filter_versions.py`, SHA256 `f75ac035ee07fe274dadb80f4f7e6bd14cb367ca518145e9ea04bdf8582f6440`, rechecked against main in this run. The `greek-ocr-toolkit-pipe032/` component prefix is retained.

Changes are precisely the authorized amendments: polytonic in scope; five pending per-parent SF7 full-result bindings; pipeline 0.3.3; released polytonic metadata; eight regenerated fingerprints with unchanged named versions; five converter-regenerated numerics ledgers; readout status/invariant extensions and flip reporting; names and binding/submission guards. `config_diff.json` proves all other config keys equal census05, including parents, metadata, native settings, held-out policy and frozen_05. The split remains `7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82`; B copies the same bytes to the new inputs root. The five standing cyrillic bindings and shas are identical. `CHANGES.md` lists every changed inherited file.

The only changed inherited package source files are `greekocr/harvest/line_pipeline.py`, `docs/harvest/line_pipeline/tool_versions.json`, and the one version expectation in `tests/test_content_gate.py`. All other inherited package source bytes are unchanged. `pipeline_033.patch` applies against CODE_SHA; `readout_033.patch` separately records all reporting/test wrapper changes against census05.

## Status contract and tool versions

Lead choice: **kept_unverified is polytonic-only**. It requires `evidence.kept_unverified: true` and a nonempty string `evidence.reason`; it cannot contain edits. The route retains this evidence. It avoids `correction_unresolved` but does not join SUCCESS or contribute edits. Other tools' successful edits and the existing NFC/whitespace composer stay unchanged. Missing results, failed, proposal_only and required_evidence_unresolved still HOLD. Existing applied, verified_no_change and tag_only behavior is unchanged.

The pipeline module SHA is `a78e6a8388006b3b67f2145f8aaaaa689842b3dc8651f235a5e79e08be855400` (base `9c6f8ead…`). Eight tool digests change because they fingerprint that module: numerics, dashes, content_gate, content_repair, composer, final_eligibility, census, inventory. `fingerprints.json` lists every old/new digest; **no tool version changes**. Pipeline alone becomes 0.3.3. Gate remains 0.3, segmentation 0.13 / label 0.9-s5, census 0.7.

The already released polytonic entry in the retained draft and the cyrillic entry are unchanged by fingerprint regeneration. Relative to census05, polytonic's scope changes from candidate_pre_audit to released; version 0.7, components and digest stay identical. The exact registered SF7 component remains SHA256 `2f7a777a91adae1af5238a9f2092c59326fc6cc7d83d6ad3bf115866455ec208`. Every SF7 per-row result must carry tool version **0.7** and digest **`de1a9a8bc6b0598f5b28ac213faa13ce00ced95aa2754291fc183373f60c60c5`**. The owner ruling 20 Oct 10:47 is in owner_decisions, and replaces the old coordinator polytonic_release_scope note. This schema has no history field; the untouched census05 manifest is the historical record.

Exact loader citation: packaged `greekocr/harvest/line_pipeline_census.py:299–300` tests the **correction release binding's `status`**, and downgrades SUCCESS results to proposal_only when it is not released. It does not inspect tool_versions scope for this decision. Both released metadata and `status: released` on each SF7 binding are supplied. The existing canonical unresolved wire status is `required_evidence_unresolved`; the brief's shorthand `unresolved` is reported in that bucket, but a literal unrecognized wire status is rejected. The producer must emit the canonical status; no silent conversion was added.

## Numerics provenance and input custody

`regenerate_n1.py` follows census05's producer converter method. It extracts canonical_result, legacy_convert and n1_candidates byte-for-byte from the same FP3 producer; the extraction and original producer scripts are retained. It hash-checks both original producer files and the tokenizer/scanner, uses the same original remote producer path identities, and generates results from producer inputs and canonical parent rows. It never generates from the old correction records and never restamps them.

All five numerics ledgers: identical membership and order, **zero status moves, zero edit/hold changes, zero content changes beyond tool_digest**. Named version stays 0.3. `corrections/report.json` contains per-ledger matrices, old/new bytes and hashes and the full 0.3.3 ArtifactCorrector.load PASS for all five regenerated plus all five unchanged cyrillic ledgers. There are 556,245 regenerated numerics records. The active numerics digest is `4042522a35a47aca9341da2560fc12e8fe0a2909ca64996b2c5845ca462c4a3d`.

`INPUTS.json` records the new numerics destination under `$W/census_06_20261020/inputs/`, all bytes/hashes, and exact ignored archive paths. Archives are retained under this worktree's `docs/harvest/census06/corrections/archives/`, outside Git and the code payload; no write to the data-root or census05 directory was made. Preserve/transfer these archives when moving checkouts. `restore_inputs.py` restores exact raw bytes without overwrite. `input_custody.json` freshly rehashes all five parent inputs, metadata, split and regenerated ledgers/archives. Disposable regeneration SQLite work databases were removed after qualification and load measurement; the reports and ledger/archive bytes remain.

## Qualification

- Existing packaged fixtures: baseline 360 passed / 9 inherited evidence skips; 0.3.3 360 passed / the same 9 skips, **zero test-outcome changes** (`regression_comparison.json`). The only fixture-source adjustment is the explicit pipeline version expectation.
- Amendment, binding/coverage, flip and readout tests: final result in `tests.log` and `tests.xml`. Together with packaged regression, **411 passed**, 19 skips (9 packaged evidence skips, 9 absent historical readout fixtures, and 1 real-SF7 PENDING head test). The unchanged 600,000-row streaming test passes. One rerun exhausted local disk while creating its fixture; only this run's disposable work/test databases were removed, then the complete suite was rerun successfully.
- Policy parity: **150/150 and 888/888**, exact verdicts and reasons, saved native measurements through the unchanged segmentation policy; zero new native images/readers. See `parity_result.json`.
- The same 200 real mock input rows and saved native observations are retained byte-for-byte from census05. Only polytonic scope, names and synthetic polytonic result cases change. The harness executes the real preparation/wrappers, canonical loader, pipeline and readout with fake Slurm/native I/O. No actual srun/sbatch executes. Smoke i, smoke ii and full ii pass **48/48 invariants** (16 each); unsplit full still refuses. Mocks include applied edits with tool provenance, kept_unverified, explicit unresolved and missing results; pending polytonic is nonzero. `test_mock_polytonic_witnesses` asserts these cases in each mode. `mock_result_diff.json` confirms identical row membership and zero outcome changes on rows not exercising polytonic; changed exercise rows are enumerated. Synthetic edits are **mock-only**, with no accuracy or production admission claim.
- Readout adds polytonic status counts by parent/class and parent/class separately, plus admitted routed rows by status. Non-routed not_applicable/prior-excluded rows remain in the existing global route totals. Kept-unverified admissions must reconstruct final_text from raw plus only other tools' serialized edits, followed by the unchanged NFC/whitespace policy. Hidden changes or any polytonic edit fail the new invariant.

## Runtime and resources

Read-only `sacct` for census05 full job 3703989: COMPLETED, **02:31:52** batch (9,112 s), **02:31:43** census Python (9,103 s), four-hour limit. `runtime_remote.log` is the receipt. A full local loader measurement validated 214,436 numerics records / 198,927,711 bytes in 5.376 s (~39,891 rows/s); this is **not Clariden throughput qualification**.

**Historical A sizing, superseded for full-limit selection by C1 below.** Planning allowance is deliberately 250 SF7 records/s for the 258,629 census05 routed rows: 1,034.516 s added load. `ceil((9112 + 258629/250) × 1.25) = 12684 s = 03:31:24`, leaving 00:28:36 within the unchanged **04:00:00** census limit. SF7 file bytes and actual load time remain PENDING; binding records elapsed time, and the coordinator reviews real binding/smoke timing before full. This arithmetic is a budget, not a performance claim. All batch files use account a0140, normal partition, one node/task. Regression/parity retain 00:05:00, census 04:00:00, readout 00:30:00. Binding and flips use four CPUs and 00:30:00; smoke overrides debug/00:30:00 as in census05-C. B must perform scheduler test-only checks, not A.

## SF7 binding procedure

All five configured parents can be touched: collection-v2-train, collection-v2-dev, collection-v2-test, collect-v3-W1-20261018-0524, collect-v3-W2-20261018-0524. The census05 global routed total is 258,629. `polytonic_parent_candidates.json` states candidly that exact per-parent route counts have not been inferred from the summary. Binding streams the full census05 published decisions to establish exact identities/counts; it requires every routed row exactly once and no extra rows. This large scan and the full loader belong in a small CPU job, not an unbounded login-node task. **A submits nothing.**

The coordinator supplies one **full line-tool-result-v1 file per parent**, not edits-only files, with path and SHA256. `bind_sf7.py PATH SHA [PATH SHA ...] --work NEW_DIRECTORY` runs on Clariden, checks every file's SHA/size, validates against the original registered census05 observation, and loads every record through the real ArtifactCorrector.load. Coverage missing/extra/duplicate, unknown parent, wrong digest/status or invalid evidence aborts before publishing. Status counts are per parent. `test_sf7_head_sample` loads the first N records per real file through that loader/validator once bound; until then it skips explicitly PENDING.

After validation, the binder creates a new `inputs/sf7-<content-id>/` directory, refusing overwrite. B's numerics inputs already occupy inputs/, so the new SF7 subdirectory is the never-existing destination. It stages the payload, fills config and INPUTS, removes pending placeholders, rebuilds the manifest/id and rsyncs to a new empty code directory, reading every manifest SHA back. It does not alter the committed pre-binding payload, census05, or Git. `--check-only` performs validation without input/code publication. `VERIFY.sh` adds the separate sf7-binding check (PENDING now); it does not replace or weaken the external verifier. `submit_chain.sh` and preparation both refuse pending bindings.

After binding, bring the staged bound config, INPUTS, binding report, package_id and two deploy manifests back into this authorized directory for the lead's review/commit. Run the unchanged verifier against that real commit and the new code directory before smoke; do not use the earlier pre-binding receipts for different bytes. The external verifier checks **all tracked dirt across the whole worktree**, not just payload paths (`verify_deploy.py:102–109`). The pre-existing unrelated geometry_observations.py, row_inclusion.py, pyproject.toml, limit_probe.log and other current changes were left alone. The lead must resolve whole-tree cleanliness before B verification; no temporary repository or exemption exists. `verify_b.py --out /absolute/external/directory` runs all four unchanged verifier calls and then the binding check; all receipts remain outside the repository until all kinds finish.

## Coordinator block — prepared, not executed

Prerequisites: A committed by lead; B deploy/readback and four unchanged verifier successes, scheduler checks, coordinator-provided SF7 path/SHA JSON. `SF7_BINDINGS_FILE` is a JSON object keyed by the five exact parent IDs; each value has `path` and `sha256`. It must contain actual coordinator-supplied values. No fake ledger binding is supplied here.

```bash
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
# Set PRE_ID from this handoff's package_id.json (on the Mac, before B).
export PRE_ID=de597753a70a5d6d
export CENSUS06_BUNDLE="$W/census_06_20261020/code/$PRE_ID/docs/harvest/census06"
export SF7_BINDINGS_FILE="$W/census_06_20261020/sf7-bindings.json"
export SF7_BIND_WORK="$W/census_06_20261020/binding/sf7-001" # must not exist
# Coordinator submits only after all real paths/shas have arrived and been reviewed.
mkdir -p "$W/census_06_20261020/logs"
BIND_JOB=$(sbatch --parsable --chdir="$W/census_06_20261020" --output="$W/census_06_20261020/logs/binding-%j.log" --export=ALL "$CENSUS06_BUNDLE/bind_sf7.sbatch")
printf 'binding=%s\n' "$BIND_JOB"
```

Wait for binding COMPLETED and review its report/counts. The report must show exact coverage and every full-file load PASS. Import the staged binding artifacts, obtain the lead commit, and run the unchanged verifier on those exact bytes. Then, separately on Clariden:

```bash
BOUND_ID=$(python3 -B -c 'import json,os,pathlib; print(json.loads((pathlib.Path(os.environ["SF7_BIND_WORK"])/"stage/docs/harvest/census06/package_id.json").read_text())["package_id"])')
export CENSUS06_BUNDLE="$W/census_06_20261020/code/$BOUND_ID/docs/harvest/census06"
"$W/venv_l1/bin/python" -B "$CENSUS06_BUNDLE/binding_state.py" --submit
# Real-head test, small slice through the full production loader; no reader.
"$W/venv_l1/bin/python" -B -m pytest -q -p no:cacheprovider \
  --basetemp="$SF7_BIND_WORK/head-test" "$CENSUS06_BUNDLE/test_pipeline_033.py::test_sf7_head_sample"
unset CENSUS06_RUN CENSUS06_READOUT_OUT CENSUS06_CONFIG CENSUS06_BASELINE
export CENSUS06_SPLIT_FILE="$W/census_06_20261020/inputs/row_split.jsonl.gz"
export CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82
export E4_SMOKE=1 CENSUS06_ATTEMPT=smoke-split-002 CENSUS06_EXPECT_ROWS=200
bash "$CENSUS06_BUNDLE/submit_chain.sh" --partition=debug --time=00:30:00
# Chain is regression -> afterok parity -> afterok census -> afterok readout.
```

**STOP for coordinator smoke review**: version 0.3.3, complete 200 rows, no INFRA_ERROR, every invariant PASS, no held-out leaks; inspect pending polytonic, kept-unverified reasons, actual edits and timing. Full is a separate coordinator action after review:

```bash
# After completed smoke: read the measured TIMING line and review its caveats.
export CENSUS06_SMOKE_READOUT="$W/census_06_20261020/attempts/smoke-split-002.readout/readout.json"
"$W/venv_l1/bin/python" -B -c 'import json,os; print(json.load(open(os.environ["CENSUS06_SMOKE_READOUT"]))["census_timing_line"])'
# suggested_limit = ceil(projection × 1.5), capped at normal MaxTime 12:00:00.
# If the uncapped projection exceeds MaxTime, STOP: the cap cannot make it fit.
export SBATCH_TIMELIMIT=$("$W/venv_l1/bin/python" -B -c 'import json,os; print(json.load(open(os.environ["CENSUS06_SMOKE_READOUT"]))["census_timing"]["suggested_limit"])')
# This environment override reaches the full census only. Alternative:
# submit_chain.sh --full-time HH:MM:SS (argument wins over the environment).
export E4_SMOKE=0 CENSUS06_ATTEMPT=full-split-002 CENSUS06_EXPECT_ROWS=592466
export CENSUS06_BASELINE="$W/census_05_20261020/attempts/full-split-001/summary.json"
bash "$CENSUS06_BUNDLE/submit_chain.sh"
unset SBATCH_TIMELIMIT
# Review printed IDs. Then coordinator submits flip reporting dependent on full readout:
# replace FULL_READOUT_JOB_ID with the actual printed readout ID, never an invented ID.
sbatch --dependency=afterok:FULL_READOUT_JOB_ID --output="$W/census_06_20261020/logs/flips-%j.log" --export=ALL "$CENSUS06_BUNDLE/flip_report.sbatch"
```

Readout derives `--expect-pipeline-version 0.3.3` from packaged code and writes a sibling `attempts/<attempt>.readout/`, never inside the run. Full outputs and invariants stay census05-compatible plus the new reporting invariant. The flip job writes sibling `attempts/full-split-002.flips/flip_report.json`, streams immutable completed generations with hash checks, and compares exact parent/row membership. Per parent it counts ADMIT-vs-not and admitted_train membership flips, both directions, with polytonic hold / polytonic edit / other breakdown. Attribution describes serialized routes and is not a causal claim. Tests cover flip dimensions/reasons, missing membership, duplicates, changed hashes and output-inside-run refusal.

A ends with `COMMIT_LIST.md` and `commit_paths.txt`. No deployment or verifier/scheduler success is claimed by A.


## B: committed deploy, readback and scheduler test-only (2026-10-20)

Deployed committed package `de597753a70a5d6d` from the untouched clean detached worktree `~/Projects/greek-ocr-toolkit-census06-verify`, HEAD `cf1db4dd48690544f4a88c208a082a0af4e5a4f7`, to `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/`. The destination was empty/absent; each input destination was absent. The guarded transfer refused existing inputs and used no overwrite. `restore_inputs.py` restored or verified exact archive-derived numerics bytes without overwriting. No write occurred under census05. A's “not deployed” statements above describe A's historical endpoint.

Remote readback: **180/180 payload files, 6/6 inputs, 5/5 standing cyrillic ledgers**. Tables: `b_evidence/payload_readback.sha256`, `inputs_readback.sha256`, `cyrillic_readback.sha256`; command records: `deployment_commands.json`; summary: `deployment_summary.json`. Standing cyrillic ledgers were rehashed in place, read-only, under `filter_pipeline_20261018/prepared/87407ec7430a375f/`.

Input destinations (prefix `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/`):

| Destination basename | Bytes | SHA256 |
| --- | ---: | --- |
| `numerics_collection-v2-train.jsonl` | 198927711 | `8e9ba91c207bdeb76548e3e2c076bb90d08448bbe9634c95754e1eff8cac6146` |
| `numerics_collection-v2-dev.jsonl` | 10556613 | `e803df22662200d502d00b7f5037b3e35f0f9cd6c49cf2d7f18340a61e781eaf` |
| `numerics_collection-v2-test.jsonl` | 34491534 | `8ba2eda0d95a7e6d6c07ce8923bebfe86e910a727cf8788ed0032cd739f6c5f3` |
| `numerics_collect-v3-W1-20261018-0524.jsonl` | 76975345 | `dde9ebc618b7a0b161e18ea63262d7f1891809ccd0a72cb92d0bcbd448406300` |
| `numerics_collect-v3-W2-20261018-0524.jsonl` | 155889454 | `923fe3fc930be84674f72e86121fcb404a8d1efb8f38f292abeb3535669c2254` |
| `row_split.jsonl.gz` | 1032585 | `7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82` |

The unchanged external verifier printed **VERIFY_OK ×4**, using the clean lead commit and the census05-D argument pattern adapted to census06. Receipts/logs were written directly into this repo's new `b_evidence/`, outside the verifier's source worktree. The source worktree stayed clean. **No `--allow-untracked` exemptions were used.** The unchanged verifier itself calls only `sbatch --test-only`; account `a0140`, normal partition and packaged times came from the hash-verified sbatch directives. `verifier_identity.json` seals the external verifier bytes.

| Kind | Receipt | SHA256 |
| --- | --- | --- |
| regression | `b_evidence/verify-regression.json` | `b3c1687eb937b453f8cf3634b20a670eb2d3c3a7d92685435f14ff74ddbe226b` |
| parity | `b_evidence/verify-parity.json` | `59bca85e2dc666ddefb9d213ac28bfa54a23e31b0ccb014dda734885ca0bd02d` |
| census | `b_evidence/verify-census.json` | `6c9400462309dfa6f8776f88d8bfa05ceda59886da3faa6b3c3ea24b9ea71acc` |
| readout | `b_evidence/verify-readout.json` | `89c41a1091ed628e967d054b9fbdab897faacb29731573053c86ca74f903c303` |

Additional scheduler tests passed **smoke 4/4 and full 4/4**. Every explicit test command used `--account=a0140`; smoke used debug/00:30:00, full used normal with regression/parity 00:05:00, census 04:00:00, readout 00:30:00. Debug live limits: MaxTime 01:30:00, MaxNodes 4; 00:30:00 fits. These independent test-only checks validate each chain member; no fictitious dependency IDs were supplied. The packaged chain's three afterok links were inspected. Scheduler “Job … to start” responses are test-only predictions, not submitted jobs.

Exact test-only command lines executed through `ssh clariden` (all responses retained in `b_evidence/test-only-*.log` and `verification_commands.json`):

```bash
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d && sbatch --test-only --account=a0140 --partition=debug --time=00:30:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06,E4_SMOKE=1,CENSUS06_ATTEMPT=test-only-smoke,CENSUS06_EXPECT_ROWS=200,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06/jobs/regression.sbatch
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d && sbatch --test-only --account=a0140 --partition=debug --time=00:30:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06,E4_SMOKE=1,CENSUS06_ATTEMPT=test-only-smoke,CENSUS06_EXPECT_ROWS=200,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06/jobs/parity.sbatch
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d && sbatch --test-only --account=a0140 --partition=debug --time=00:30:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06,E4_SMOKE=1,CENSUS06_ATTEMPT=test-only-smoke,CENSUS06_EXPECT_ROWS=200,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06/jobs/census.sbatch
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d && sbatch --test-only --account=a0140 --partition=debug --time=00:30:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06,E4_SMOKE=1,CENSUS06_ATTEMPT=test-only-smoke,CENSUS06_EXPECT_ROWS=200,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06/jobs/readout.sbatch
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d && sbatch --test-only --account=a0140 --partition=normal --time=00:05:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06,E4_SMOKE=0,CENSUS06_ATTEMPT=test-only-full,CENSUS06_EXPECT_ROWS=592466,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06/jobs/regression.sbatch
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d && sbatch --test-only --account=a0140 --partition=normal --time=00:05:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06,E4_SMOKE=0,CENSUS06_ATTEMPT=test-only-full,CENSUS06_EXPECT_ROWS=592466,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06/jobs/parity.sbatch
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d && sbatch --test-only --account=a0140 --partition=normal --time=04:00:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06,E4_SMOKE=0,CENSUS06_ATTEMPT=test-only-full,CENSUS06_EXPECT_ROWS=592466,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06/jobs/census.sbatch
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d && sbatch --test-only --account=a0140 --partition=normal --time=00:30:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06,E4_SMOKE=0,CENSUS06_ATTEMPT=test-only-full,CENSUS06_EXPECT_ROWS=592466,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/de597753a70a5d6d/docs/harvest/census06/jobs/readout.sbatch
```

SF7 stays **PENDING for all five parents**. `bind-pending.log` records `bind_sf7.py --check-only --work …` with no files: argparse refuses the missing required PATH/SHA bindings before creating anything. There is no separate `--pending` CLI option. `submit-pending.log` records the deployed `submit_chain.sh` refusal with `sf7-binding PENDING`; its guard runs before mkdir or any sbatch. `binding-state.log` confirms all five pending parents. No attempt, binding work directory, reader call, allocation or paid workload was started.

Coordinator block, **review only; no commands below were executed in B**. This supersedes the pre-binding coordinator example above. Supply the actual five full files and shas; do the large binding/coverage scan in the coordinator's CPU allocation. The existing `bind_sf7.sbatch` expands the supplied JSON into the exact per-parent `bind_sf7.py <file> <sha>` invocation shown below, then the binder rebuilds and redeploys a new code id.

```bash
#!/usr/bin/env bash
# REVIEW ONLY. NOT EXECUTED IN B. Coordinator authorization is required for jobs.
set -euo pipefail
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export PRE_ID=de597753a70a5d6d
export CENSUS06_BUNDLE="$W/census_06_20261020/code/$PRE_ID/docs/harvest/census06"
export SF7_BINDINGS_FILE="$W/census_06_20261020/sf7-bindings.json"
export SF7_BIND_WORK="$W/census_06_20261020/binding/sf7-001" # must not exist
# Populate SF7_BINDINGS_FILE with actual per-parent full-result paths and SHA256s.
# bind_sf7.sbatch expands that JSON, in its four-CPU allocation, to exactly:
# "$W/venv_l1/bin/python" -B "$CENSUS06_BUNDLE/bind_sf7.py" \
#   <collection-v2-train full-file> <sha256> \
#   <collection-v2-dev full-file> <sha256> \
#   <collection-v2-test full-file> <sha256> \
#   <collect-v3-W1-20261018-0524 full-file> <sha256> \
#   <collect-v3-W2-20261018-0524 full-file> <sha256> --work "$SF7_BIND_WORK"
mkdir -p "$W/census_06_20261020/attempts" "$W/census_06_20261020/logs"
BIND_JOB=$(sbatch --parsable --account=a0140 --partition=normal --time=00:30:00 \
  --chdir="$W/census_06_20261020" --output="$W/census_06_20261020/logs/binding-%j.log" \
  --export=ALL "$CENSUS06_BUNDLE/bind_sf7.sbatch")
printf 'binding=%s\n' "$BIND_JOB"
# STOP: wait for COMPLETED, review coverage, all five loader PASSes and elapsed time.
# The binder fills config/INPUTS, removes pending entries, rebuilds the package/id,
# deploys to NEW code/<BOUND_ID>/ and reads back every payload SHA. PRE_ID is immutable.
# Import stage config, INPUTS, binding report, package_id and manifests for lead commit.
# STOP: lead review/commit; clean verifier tree for that commit; re-readback code and
# inputs (including SF7), rehash cyrillic, unchanged verifier x4, test-only smoke/full
# x4 against BOUND_ID, then binding_state --submit and real SF7 head test.
# Do not continue on the strength of pre-binding B receipts.
BOUND_ID=$(python3 -B -c 'import json,os,pathlib; print(json.loads((pathlib.Path(os.environ["SF7_BIND_WORK"])/"stage/docs/harvest/census06/package_id.json").read_text())["package_id"])')
[[ "$BOUND_ID" != "$PRE_ID" ]]
export CENSUS06_BUNDLE="$W/census_06_20261020/code/$BOUND_ID/docs/harvest/census06"
"$W/venv_l1/bin/python" -B "$CENSUS06_BUNDLE/binding_state.py" --submit
# Run real-head loader test in the coordinator's CPU allocation, not on login:
# "$W/venv_l1/bin/python" -B -m pytest -q -p no:cacheprovider \
#   --basetemp="$SF7_BIND_WORK/head-test" "$CENSUS06_BUNDLE/test_pipeline_033.py::test_sf7_head_sample"
unset CENSUS06_RUN CENSUS06_READOUT_OUT CENSUS06_CONFIG CENSUS06_BASELINE
export CENSUS06_SPLIT_FILE="$W/census_06_20261020/inputs/row_split.jsonl.gz"
export CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82
export E4_SMOKE=1 CENSUS06_ATTEMPT=smoke-split-002 CENSUS06_EXPECT_ROWS=200
bash "$CENSUS06_BUNDLE/submit_chain.sh" --account=a0140 --partition=debug --time=00:30:00
# regression -> afterok parity -> afterok census -> afterok readout.
# STOP for coordinator review: pipeline 0.3.3, 200 rows, no INFRA_ERROR, all
# invariants PASS, no held-out leaks; inspect polytonic counts, reasons, edits,
# head/full-loader coverage and measured timing before authorizing full.
# After completed smoke: read the measured TIMING line and review its caveats.
export CENSUS06_SMOKE_READOUT="$W/census_06_20261020/attempts/smoke-split-002.readout/readout.json"
"$W/venv_l1/bin/python" -B -c 'import json,os; print(json.load(open(os.environ["CENSUS06_SMOKE_READOUT"]))["census_timing_line"])'
# suggested_limit = ceil(projection × 1.5), capped at normal MaxTime 12:00:00.
# If the uncapped projection exceeds MaxTime, STOP: the cap cannot make it fit.
export SBATCH_TIMELIMIT=$("$W/venv_l1/bin/python" -B -c 'import json,os; print(json.load(open(os.environ["CENSUS06_SMOKE_READOUT"]))["census_timing"]["suggested_limit"])')
# This environment override reaches the full census only. Alternative:
# submit_chain.sh --full-time HH:MM:SS (argument wins over the environment).
export E4_SMOKE=0 CENSUS06_ATTEMPT=full-split-002 CENSUS06_EXPECT_ROWS=592466
export CENSUS06_BASELINE="$W/census_05_20261020/attempts/full-split-001/summary.json"
bash "$CENSUS06_BUNDLE/submit_chain.sh" --account=a0140 --partition=normal
unset SBATCH_TIMELIMIT
# Full census uses the measured override; regression/parity retain 00:05:00;
# readout 00:30:00. Same afterok chain. Record actual returned IDs.
# Readout is a sibling: attempts/full-split-002.readout/, outside the census run.
# jobs/readout.sbatch derives PIPELINE_VERSION from the bound package (=0.3.3),
# then runs the following inside its allocated afterok readout job (do not duplicate):
# srun -A a0140 --partition=normal --cpu-bind=none --nodes=1 --ntasks=1 \
#   "$W/venv_l1/bin/python" -B "$CENSUS06_BUNDLE/readout/census_readout.py" \
#   --expect-pipeline-version 0.3.3 \
#   --run "$W/census_06_20261020/attempts/full-split-002" \
#   --out "$W/census_06_20261020/attempts/full-split-002.readout" \
#   --baseline "$CENSUS06_BASELINE" --expect-rows 592466
# Set from the actual chain output only:
: "${FULL_READOUT_JOB_ID:?set actual full readout job ID}"
sbatch --account=a0140 --partition=normal --time=00:30:00 \
  --dependency="afterok:$FULL_READOUT_JOB_ID" \
  --output="$W/census_06_20261020/logs/flips-%j.log" --export=ALL \
  "$CENSUS06_BUNDLE/flip_report.sbatch"
# flip_report compares completed census05/census06 and writes the sibling
# attempts/full-split-002.flips/flip_report.json; it never writes census05.
```

**After SF7 changes the package id, re-run** the bound-package lead review/commit and clean-source check, payload readback against its new manifests, input readback including the five SF7 files and existing six inputs, standing cyrillic checks, all four unchanged verifier calls against that real commit/new code root, and all eight smoke/full scheduler test-only checks. Check binding_state --submit and run the real SF7 head test. Then run the actual smoke chain, review outcomes/timing, separately authorize the full afterok chain, sibling readout at `--expect-pipeline-version 0.3.3`, and dependent flip_report. B's pre-binding verifier and scheduler receipts cannot qualify the new package. The unchanged six inputs need rehashing, not overwriting or copying again.

Cleanup (only the coordinator-authorized pytest basetemps; `b_evidence/cleanup_receipt.json`):

| Deleted directory | Allocated KiB | Regular-file bytes |
| --- | ---: | ---: |
| `033-regression-tmp/` | 4688 | 3655705 |
| `baseline-regression-tmp/` | 4688 | 3657556 |
| `test-tmp/` | 864012 | 884211461 |

Total deleted: **873,388 KiB** allocated (891,524,722 regular-file bytes). No new pytest basetemp was created in B. Logs/XML, baseline, mock_batch, corrections, archives and all other data were preserved. No Git staging/commit or jobs submitted.

Lead commit handoff: `COMMIT_LIST_B.md`, exact paths `B_COMMIT_PATHS.txt`, byte seal `B_COMMIT_SHA256SUMS`; run `b_evidence/guard_b.py` before staging under separate lead authority.


## CENSUS06-C1 — measured full time limit (source only, 20 October 2026)

C1 changes only this bundle. No deployment, allocation, scheduler test-only call,
job submission, staging or commit was performed. `de597753a70a5d6d` remains the
pre-binding deployed package; the locally rebuilt id is a source delta for C2,
not a deployed or qualified code id. SF7 remains PENDING. C2 must rebuild from
these sources after binding and repeat its deployment/readback/verifier checks.

Read-only `ssh clariden 'scontrol show partition normal'` reports **MaxTime
12:00:00**; the complete output is `partition_normal_c1.txt`. The brief supplies REL3's
`SBATCH_TIMELIMIT=01:30:00` precedent. I inspected the checked-out REL3.md and
wrappers; that particular coordinator override is not retained there. Slurm environment time overrides script directives. C1 consumes that
variable and removes it from every child sbatch environment, then adds an explicit
`--time` only to the full census. `--full-time HH:MM:SS` / `--full-time=HH:MM:SS`
win over the environment. With neither, the packaged full census remains
04:00:00. Smoke defaults to debug/00:30:00 and ignores both full-only mechanisms.
Explicit ordinary `--time` arguments retain their existing chain-wide scope;
full-only options take precedence on the full census. Regression/parity remain
00:05:00 and readout 00:30:00 unless explicitly overridden. Bind/flip scripts are
unchanged. Every chain member prints its effective `--time` to stderr before its
submission; stdout remains the four job IDs. Unset the caller's environment
variable after the chain, as shown above, before direct bind/flip submissions.

Before any sbatch, full mode checks `CENSUS06_SMOKE_READOUT`. When unset, it finds
the newest `attempts/smoke*.readout/readout.json` by mtime. Set the explicit path
for custom names and to select the reviewed smoke; no readout preserves the old
submission default. A discovered or explicitly selected readout missing measured
timing fails closed. Projection >04:00:00 without an explicit full limit refuses
before regression. Malformed limits and full limits above 12:00:00 also refuse.
An explicit limit is coordinator review authority, not proof that it is adequate.

Previously smoke subset every correction artifact. C1 preserves **full SF7 paths
and SHA256s** in smoke. The census reads, validates and indexes every SF7 record,
including records beyond its 40-per-parent decision slice. For these records a
separate temporary observation table is built from every whole hash-pinned source
parent; normal validation remains mandatory, including split rebinding. That
additional smoke source-table work is included in the measured SF7 load seconds,
a conservative extra load cost. No unmatched SF7 record bypasses validation.
Other correction inputs retain their existing smoke subsetting. Original files
are unchanged. Smoke still reports/decides 200 rows across five parents, and native
segmentation runs only for that slice. Whole-file binding and coverage remain
C2 prerequisites; this is not a replacement for `bind_sf7` coverage checks.

The published immutable generation's `summary.json.census_timing` contains SF7
source bytes, indexed records, load wall seconds (hashing, validation, split
transformation and indexing), decision rows/seconds/rows_per_second after all
loads, and SF7 correction-call count/seconds. Decision wall time includes native
waits, pipeline evaluation and ledger writes, and excludes dedup/export/cleanup.
The readout stores the projection in `readout.json.census_timing`, stores and
prints exactly one `CENSUS TIMING:` line, and appends it to `READOUT.md` for both
smoke and full. Historical summaries without timing remain readable. Zero rows,
zero load or no measured SF7 calls cannot supply a projection. Use fresh attempts;
resume/cache timings do not qualify the initial whole-file load or full throughput.

**Formula:** the smoke first-40 slice has an unrepresentative row/route mix and
native work, so its observed decision rows/s is reported but never extrapolated.
Use census_05 job **3703989**, **9,112 s for 592,466 rows**, as the complete measured
non-SF7 allowance (already includes fixed overhead; a separate fixed-overhead
measurement is unavailable). With L = measured whole-file SF7 load seconds,
Q = measured SF7 correction-call seconds, K = measured SF7 calls, and the
census_05 **258,629 routed rows**:

```text
projection_seconds = ceil(9112 + L + 258629 × Q / K)
suggested_limit_seconds = min(ceil(projection_seconds × 1.5), 43200)
```

Q measures SQLite lookup, deserialization and the existing result adapter in the
corrector; pipeline work outside the call is in the census_05 allowance. Using the
baseline routed count avoids projecting the first-40 route fraction. Call cost
may still vary with SF7 status/payload size and page-cache state; the ×1.5 margin
is a scheduling allowance, not a runtime guarantee. The TIMING line explicitly
states the fallback formula and its nonrepresentative smoke caveat instead of
claiming `592466 / smoke rows/s` is a full runtime. The old 250 records/s allowance
is retained in `runtime_sizing.json` only as historical arithmetic, superseded by
its C1 formula. No real bound smoke has run, so C1 supplies no measured production
projection or chosen production limit.

Coordinator sequence: completed bound smoke → read/review TIMING and invariants
→ set `SBATCH_TIMELIMIT` (or `--full-time`) to its suggested ×1.5 capped limit
→ separately authorized full. Both coordinator examples above now implement it.
C2 must use its new bound bundle rather than execute this local source package.

Validation: `tests.log` / `tests.xml` cover the packaged eight regression suites,
0.3.3 amendment/binding/flip tests, readout suite (including the 600,000-row
streaming check), and C1 fake-sbatch, refusal, full-file validation and timing tests.
Final result: **438 passed, 19 skipped**; C1 basetemp deleted.
The local-only manifest id is `5de4fcd496663eae` (182 payload files).
The exact review delta is **21 files**, including the patch, allowlist and seal.
Count and cleanup are also recorded in `COMMIT_LIST_C1.md`. Only C1's own
`c1-test-tmp` basetemp is removed after a successful complete run; historical
baselines, mock data and all other artifacts remain untouched. `timing_c1.patch`
and `C1_COMMIT_PATHS.txt` list the concrete review delta. The guarded allowlist
and SHA256 seal are checked without invoking git add or git commit.


## CENSUS06-C2a — pre-binding rebuild (20 October 2026)

Local pre-binding package **`fb0194d597f20655`**, 182 payload files, combines C1
unchanged with the kept_unverified reason split. **Not deployed.** The deployed
pre-binding id remains `de597753a70a5d6d`; the lead must commit this delta before
C2a-deploy installs and verifies the new code directory. The binder rebuilds from
the bundle in which it runs, so deploy this pre-binding bundle before the
coordinator submits `bind_sf7.sbatch`. C2a-deploy fills/verifies `CENSUS06_BUNDLE`
with the new code dir; the path below is an intended destination, not a deployment
receipt. Earlier C1 references to rebuilding only after binding are superseded
by this required pre-binding rebuild/deploy, followed by the existing bound rebuild.

Readout is additive: `tables.kept_unverified_reasons` counts exact
`evidence.reason` × parent × split × disposition × class (ledger role),
`tables.kept_unverified_reason_totals` lists every exact reason and its total,
and `tables.polytonic_route_status_counts_by_parent` counts exact wire statuses
for every parent, including excluded/not-applicable rows. Existing bucketed status
tables, outputs and invariants remain. `jobs/readout.sbatch` runs this same
`readout/census_readout.py` from the payload; there is no additional Python copy.
Unknown reason strings retain their own keys and do not fail.

Flip attribution preserves both directions for ADMIT and admitted_train per parent.
Unresolved statuses (including `failed`) retain `polytonic hold`; edits retain
`polytonic edit`. Otherwise a kept_unverified result uses `kept_unverified: ` plus
its exact evidence reason (after-side first, before-side fallback). Other flips
remain `other`. The binder adds `kept_unverified_reason_counts` beside each
parent's existing `status_counts`, without changing validation or coverage.
Coverage still selects census_05 `not_applied_out_of_scope` only; all 122,320
`not_run_due_to_prior_exclusion` rows remain omitted. Pipeline 0.3.3 and all tool
digests are unchanged. In particular `failed` still produces correction_unresolved.

Coordinator ruling (20 October, approximately 13:50): `sf7 hold` and
`sf7 out_of_scope` both have status kept_unverified. Expected routed-row ranges
are approximately 45–80% and 5–27% respectively; out_of_scope does not imply HOLD.
Other expected statuses: applied 1–2%, verified_no_change 8–35%, failed (no crop)
0–10%. These are coordinator expectations, not measured outcomes or validation
limits. Arbitrary nonempty evidence reasons remain accepted by the pipeline.

C1's full-only SBATCH_TIMELIMIT / --full-time override, refusal for projection
above 04:00:00 without an explicit limit, full-file SF7 smoke loading and smoke
CENSUS TIMING line are carried byte-for-byte. No production timing is inferred.
`payload_diff.json` compares against B's committed manifest for deployed
`de597753a70a5d6d`: 172 unchanged files, eight changed, two added, none dropped.
The eight changes include the unchanged C1 delta plus this reason accounting.

Validation: **461 passed, 19 skipped**, recorded in `tests.log` / `tests.xml`.
All eight packaged regression suites, census06, 0.3.3, readout (including the
600,000-row streaming test), and C1 suites pass. New tests cover both known
reasons and an unknown reason with exact whitespace/Unicode preservation,
readout split/disposition/class dimensions, both flip directions and parents,
failed/unresolved/edit attribution, binder reason totals and prior-exclusion
omission. A fresh mock batch runs smoke i, smoke ii and full ii with both reasons
and every invariant PASS; full i still refuses. Historical mock data is preserved.
The harness now refuses to overwrite an existing root and accepts a fresh test
root. Only this run's `c2a-test-tmp` was deleted after the passing full run;
only tests.log/tests.xml remain as test artifacts. Skips remain the 18 absent
historical fixtures and the real-SF7 head test awaiting supplied full files.
Both actual PENDING guards are exercised locally and refuse before creating an
attempt or invoking sbatch. No network access, deploy, scheduler calls, jobs,
git add or git commit occurred.

Review `C2A_COMMIT_PATHS.txt` and `C2A_COMMIT_SHA256SUMS`; the latter seals every
listed file except itself. Run `guard_c2a.py` before lead-controlled staging.
Pre-existing untracked artifacts and unrelated dirty files are excluded.

Coordinator block (review only): procedure unchanged from the latest B/C1 block;
only PRE_ID, and therefore the initial CENSUS06_BUNDLE code directory, changes.
C2a-deploy must install and verify it before use. No command below was executed
in C2a; the inherited B comment is retained verbatim.

```bash
#!/usr/bin/env bash
# REVIEW ONLY. NOT EXECUTED IN B. Coordinator authorization is required for jobs.
set -euo pipefail
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export PRE_ID=fb0194d597f20655
export CENSUS06_BUNDLE="$W/census_06_20261020/code/$PRE_ID/docs/harvest/census06"
export SF7_BINDINGS_FILE="$W/census_06_20261020/sf7-bindings.json"
export SF7_BIND_WORK="$W/census_06_20261020/binding/sf7-001" # must not exist
# Populate SF7_BINDINGS_FILE with actual per-parent full-result paths and SHA256s.
# bind_sf7.sbatch expands that JSON, in its four-CPU allocation, to exactly:
# "$W/venv_l1/bin/python" -B "$CENSUS06_BUNDLE/bind_sf7.py" \
#   <collection-v2-train full-file> <sha256> \
#   <collection-v2-dev full-file> <sha256> \
#   <collection-v2-test full-file> <sha256> \
#   <collect-v3-W1-20261018-0524 full-file> <sha256> \
#   <collect-v3-W2-20261018-0524 full-file> <sha256> --work "$SF7_BIND_WORK"
mkdir -p "$W/census_06_20261020/attempts" "$W/census_06_20261020/logs"
BIND_JOB=$(sbatch --parsable --account=a0140 --partition=normal --time=00:30:00 \
  --chdir="$W/census_06_20261020" --output="$W/census_06_20261020/logs/binding-%j.log" \
  --export=ALL "$CENSUS06_BUNDLE/bind_sf7.sbatch")
printf 'binding=%s\n' "$BIND_JOB"
# STOP: wait for COMPLETED, review coverage, all five loader PASSes and elapsed time.
# The binder fills config/INPUTS, removes pending entries, rebuilds the package/id,
# deploys to NEW code/<BOUND_ID>/ and reads back every payload SHA. PRE_ID is immutable.
# Import stage config, INPUTS, binding report, package_id and manifests for lead commit.
# STOP: lead review/commit; clean verifier tree for that commit; re-readback code and
# inputs (including SF7), rehash cyrillic, unchanged verifier x4, test-only smoke/full
# x4 against BOUND_ID, then binding_state --submit and real SF7 head test.
# Do not continue on the strength of pre-binding B receipts.
BOUND_ID=$(python3 -B -c 'import json,os,pathlib; print(json.loads((pathlib.Path(os.environ["SF7_BIND_WORK"])/"stage/docs/harvest/census06/package_id.json").read_text())["package_id"])')
[[ "$BOUND_ID" != "$PRE_ID" ]]
export CENSUS06_BUNDLE="$W/census_06_20261020/code/$BOUND_ID/docs/harvest/census06"
"$W/venv_l1/bin/python" -B "$CENSUS06_BUNDLE/binding_state.py" --submit
# Run real-head loader test in the coordinator's CPU allocation, not on login:
# "$W/venv_l1/bin/python" -B -m pytest -q -p no:cacheprovider \
#   --basetemp="$SF7_BIND_WORK/head-test" "$CENSUS06_BUNDLE/test_pipeline_033.py::test_sf7_head_sample"
unset CENSUS06_RUN CENSUS06_READOUT_OUT CENSUS06_CONFIG CENSUS06_BASELINE
export CENSUS06_SPLIT_FILE="$W/census_06_20261020/inputs/row_split.jsonl.gz"
export CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82
export E4_SMOKE=1 CENSUS06_ATTEMPT=smoke-split-002 CENSUS06_EXPECT_ROWS=200
bash "$CENSUS06_BUNDLE/submit_chain.sh" --account=a0140 --partition=debug --time=00:30:00
# regression -> afterok parity -> afterok census -> afterok readout.
# STOP for coordinator review: pipeline 0.3.3, 200 rows, no INFRA_ERROR, all
# invariants PASS, no held-out leaks; inspect polytonic counts, reasons, edits,
# head/full-loader coverage and measured timing before authorizing full.
# After completed smoke: read the measured TIMING line and review its caveats.
export CENSUS06_SMOKE_READOUT="$W/census_06_20261020/attempts/smoke-split-002.readout/readout.json"
"$W/venv_l1/bin/python" -B -c 'import json,os; print(json.load(open(os.environ["CENSUS06_SMOKE_READOUT"]))["census_timing_line"])'
# suggested_limit = ceil(projection × 1.5), capped at normal MaxTime 12:00:00.
# If the uncapped projection exceeds MaxTime, STOP: the cap cannot make it fit.
export SBATCH_TIMELIMIT=$("$W/venv_l1/bin/python" -B -c 'import json,os; print(json.load(open(os.environ["CENSUS06_SMOKE_READOUT"]))["census_timing"]["suggested_limit"])')
# This environment override reaches the full census only. Alternative:
# submit_chain.sh --full-time HH:MM:SS (argument wins over the environment).
export E4_SMOKE=0 CENSUS06_ATTEMPT=full-split-002 CENSUS06_EXPECT_ROWS=592466
export CENSUS06_BASELINE="$W/census_05_20261020/attempts/full-split-001/summary.json"
bash "$CENSUS06_BUNDLE/submit_chain.sh" --account=a0140 --partition=normal
unset SBATCH_TIMELIMIT
# Full census uses the measured override; regression/parity retain 00:05:00;
# readout 00:30:00. Same afterok chain. Record actual returned IDs.
# Readout is a sibling: attempts/full-split-002.readout/, outside the census run.
# jobs/readout.sbatch derives PIPELINE_VERSION from the bound package (=0.3.3),
# then runs the following inside its allocated afterok readout job (do not duplicate):
# srun -A a0140 --partition=normal --cpu-bind=none --nodes=1 --ntasks=1 \
#   "$W/venv_l1/bin/python" -B "$CENSUS06_BUNDLE/readout/census_readout.py" \
#   --expect-pipeline-version 0.3.3 \
#   --run "$W/census_06_20261020/attempts/full-split-002" \
#   --out "$W/census_06_20261020/attempts/full-split-002.readout" \
#   --baseline "$CENSUS06_BASELINE" --expect-rows 592466
# Set from the actual chain output only:
: "${FULL_READOUT_JOB_ID:?set actual full readout job ID}"
sbatch --account=a0140 --partition=normal --time=00:30:00 \
  --dependency="afterok:$FULL_READOUT_JOB_ID" \
  --output="$W/census_06_20261020/logs/flips-%j.log" --export=ALL \
  "$CENSUS06_BUNDLE/flip_report.sbatch"
# flip_report compares completed census05/census06 and writes the sibling
# attempts/full-split-002.flips/flip_report.json; it never writes census05.
```


## CENSUS06-C2a-D — committed deploy and verification (20 October 2026)

Deployed **fb0194d597f20655** from the lead's clean detached worktree
`~/Projects/greek-ocr-toolkit-census06-verify-c2a`, HEAD
`0cc5710bf1029189ab5957f429ed9c1f95622088`, to
`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/`.
The destination guard established an empty directory before rsync. All **182/182**
payload bytes matched the committed manifest on local inspection and remote readback.
Existing inputs were rehashed in place: **6/6** (five numerics ledgers and split),
plus **5/5** standing cyrillic ledgers. No inputs were recopied. Per-file SHA values
are in `c2ad_evidence/payload-readback.log`, `inputs-rehash.log` and `readback.json`.
No writes occurred under census_05 or the old code directory.

**The de597753a70a5d6d pre-binding bundle is superseded. Never bind from it.**
The current pre-binding bundle is fb0194d597f20655. Earlier deployment-status
statements and coordinator examples referring to the old bundle are historical.

The unchanged external verifier returned VERIFY_OK for every kind, checking commit,
manifest bytes, remote bytes and scheduler test-only. No exemptions were used.
Receipts were written outside the clean verifier source tree, in this repo's
`c2ad_evidence/`; that source remained clean (`source-final.json`). External verifier
identity is sealed in `verifier_identity.json`.

| Kind | Result | Receipt SHA256 (`c2ad_evidence/verify-<kind>.json`) |
| --- | --- | --- |
| regression | VERIFY_OK | `8a459ffd75a51bbd65bbc2a65bccfa4f752113394291dcc4c3c756f77837fb6a` |
| parity | VERIFY_OK | `fe8f07f454bdc57825bdb58f5bfe1f8b4358f82baee2762126f193c5edadf697` |
| census | VERIFY_OK | `cd052a68208fa8fbc2e6ec1b7b753fd052ca929b6cbdae11d9694046f2f010d0` |
| readout | VERIFY_OK | `3da5c52bc68b0b0cb133b2301b317129f9fb57e8eac1b5dd39c3fe5811cd8375` |

Scheduler test-only passed smoke **4/4**, full **4/4**, override **1/1**, bind **1/1**.
Every call used account a0140, explicit partition and time; the bind used four CPUs.
Normal MaxTime is 12:00:00; debug MaxTime is 01:30:00, MaxNodes 4 (`partition-limits.log`).
The full census override printed `census effective --time=06:00:00` and was expressed
as CLI `--time` after removing SBATCH_TIMELIMIT from the scheduler environment.
The unchanged C1 local fake-scheduler tests passed **5/5**; `override-isolation.log`
records the actual chain's printed times 00:05:00, 00:05:00, 06:00:00, 00:30:00,
with the environment override absent from all four scheduler calls. This fixture
isolates timing with a fake binding guard; it does not qualify real SF7 binding.
The live pending package was never allowed through its submission guard.

Exact live scheduler test-only command lines (stdout/stderr and exit codes retained
in `scheduler_commands.json` and individual `test-only-*.log`):

```bash
printf '%s\n' 'regression effective --time=00:30:00'; env -u SBATCH_TIMELIMIT sbatch --test-only --account=a0140 --partition=debug --time=00:30:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82,E4_SMOKE=1,CENSUS06_ATTEMPT=c2ad-test-only-smoke,CENSUS06_EXPECT_ROWS=200 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06/jobs/regression.sbatch
printf '%s\n' 'parity effective --time=00:30:00'; env -u SBATCH_TIMELIMIT sbatch --test-only --account=a0140 --partition=debug --time=00:30:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82,E4_SMOKE=1,CENSUS06_ATTEMPT=c2ad-test-only-smoke,CENSUS06_EXPECT_ROWS=200 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06/jobs/parity.sbatch
printf '%s\n' 'census effective --time=00:30:00'; env -u SBATCH_TIMELIMIT sbatch --test-only --account=a0140 --partition=debug --time=00:30:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82,E4_SMOKE=1,CENSUS06_ATTEMPT=c2ad-test-only-smoke,CENSUS06_EXPECT_ROWS=200 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06/jobs/census.sbatch
printf '%s\n' 'readout effective --time=00:30:00'; env -u SBATCH_TIMELIMIT sbatch --test-only --account=a0140 --partition=debug --time=00:30:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82,E4_SMOKE=1,CENSUS06_ATTEMPT=c2ad-test-only-smoke,CENSUS06_EXPECT_ROWS=200 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06/jobs/readout.sbatch
printf '%s\n' 'regression effective --time=00:05:00'; env -u SBATCH_TIMELIMIT sbatch --test-only --account=a0140 --partition=normal --time=00:05:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82,E4_SMOKE=0,CENSUS06_ATTEMPT=c2ad-test-only-full,CENSUS06_EXPECT_ROWS=592466 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06/jobs/regression.sbatch
printf '%s\n' 'parity effective --time=00:05:00'; env -u SBATCH_TIMELIMIT sbatch --test-only --account=a0140 --partition=normal --time=00:05:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82,E4_SMOKE=0,CENSUS06_ATTEMPT=c2ad-test-only-full,CENSUS06_EXPECT_ROWS=592466 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06/jobs/parity.sbatch
printf '%s\n' 'census effective --time=04:00:00'; env -u SBATCH_TIMELIMIT sbatch --test-only --account=a0140 --partition=normal --time=04:00:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82,E4_SMOKE=0,CENSUS06_ATTEMPT=c2ad-test-only-full,CENSUS06_EXPECT_ROWS=592466 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06/jobs/census.sbatch
printf '%s\n' 'readout effective --time=00:30:00'; env -u SBATCH_TIMELIMIT sbatch --test-only --account=a0140 --partition=normal --time=00:30:00 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82,E4_SMOKE=0,CENSUS06_ATTEMPT=c2ad-test-only-full,CENSUS06_EXPECT_ROWS=592466 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06/jobs/readout.sbatch
SBATCH_TIMELIMIT=06:00:00; export SBATCH_TIMELIMIT; printf "census effective --time=%s\n" "$SBATCH_TIMELIMIT"; env -u SBATCH_TIMELIMIT sbatch --test-only --account=a0140 --partition=normal --time="$SBATCH_TIMELIMIT" --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82,E4_SMOKE=0,CENSUS06_ATTEMPT=c2ad-test-only-override,CENSUS06_EXPECT_ROWS=592466 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06/jobs/census.sbatch
env -u SBATCH_TIMELIMIT sbatch --test-only --account=a0140 --partition=normal --time=00:30:00 --cpus-per-task=4 --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020 --export=ALL,W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3,CENSUS06_BUNDLE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06,CENSUS06_SPLIT_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/inputs/row_split.jsonl.gz,CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82,SF7_BINDINGS_FILE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/scratchpad/c2ad-test-only-bindings.json,SF7_BIND_WORK=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/binding/sf7-001 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06/bind_sf7.sbatch
```

Scheduler “Job … to start” lines are test-only predictions, not submissions.
The placeholder at `$W/census_06_20261020/scratchpad/c2ad-test-only-bindings.json`
is explicitly fake and was used only as an exported pathname for the bind scheduler
check. Test-only did not execute the binder. It must never be used for real binding.
`binding-state.log` reports PENDING for all five parents; `submit-pending.log` records
exit 1 before any sbatch or attempt creation; `bind-pending.log` records exit 2 for
missing PATH/SHA arguments. `no-binding-work.log` confirms sf7-001 and the no-files
probe work directory do not exist. No jobs, reader calls, binding or spend occurred.

Coordinator hand-off: **review only; nothing below was executed in C2a-D**.
The actual `$W/census_06_20261020/sf7-bindings.json` must have exactly these five
parent keys, each `{path, sha256}`. Replace every placeholder with the actual full
result file and its SHA256; this is a schema example, not a supplied binding:

```json
{
  "collection-v2-train": {
    "path": "<actual absolute full-result path>",
    "sha256": "<actual SHA256>"
  },
  "collection-v2-dev": {
    "path": "<actual absolute full-result path>",
    "sha256": "<actual SHA256>"
  },
  "collection-v2-test": {
    "path": "<actual absolute full-result path>",
    "sha256": "<actual SHA256>"
  },
  "collect-v3-W1-20261018-0524": {
    "path": "<actual absolute full-result path>",
    "sha256": "<actual SHA256>"
  },
  "collect-v3-W2-20261018-0524": {
    "path": "<actual absolute full-result path>",
    "sha256": "<actual SHA256>"
  }
}
```

After binding: import staged artifacts → lead review/commit → clean bound source
worktree → payload/input readback including SF7 and cyrillic → unchanged verifier
×4 at the bound commit/id → test-only smoke/full ×8 at that id →
`binding_state.py --submit` → real SF7 head test in a CPU allocation. Then smoke →
review the measured TIMING line → full with SBATCH_TIMELIMIT = ceil(projection × 1.5),
capped at the partition maximum (currently 12:00:00; stop if it cannot fit) → sibling
readout with `--expect-pipeline-version 0.3.3` → dependent flip_report. Pre-binding
receipts cannot qualify bound bytes. The exact coordinator block follows:

```bash
#!/usr/bin/env bash
# REVIEW ONLY. NOT EXECUTED IN C2a-D. Coordinator authorization is required for jobs.
set -euo pipefail
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export PRE_ID=fb0194d597f20655
export CENSUS06_BUNDLE="$W/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06"
export SF7_BINDINGS_FILE="$W/census_06_20261020/sf7-bindings.json"
export SF7_BIND_WORK="$W/census_06_20261020/binding/sf7-001" # must not exist
test ! -e "$SF7_BIND_WORK" # refuse reuse
unset SBATCH_TIMELIMIT
# Populate SF7_BINDINGS_FILE with actual per-parent full-result paths and SHA256s.
# bind_sf7.sbatch expands that JSON, in its four-CPU allocation, to exactly:
# "$W/venv_l1/bin/python" -B "$CENSUS06_BUNDLE/bind_sf7.py" \
#   <collection-v2-train full-file> <sha256> \
#   <collection-v2-dev full-file> <sha256> \
#   <collection-v2-test full-file> <sha256> \
#   <collect-v3-W1-20261018-0524 full-file> <sha256> \
#   <collect-v3-W2-20261018-0524 full-file> <sha256> --work "$SF7_BIND_WORK"
mkdir -p "$W/census_06_20261020/attempts" "$W/census_06_20261020/logs"
BIND_JOB=$(sbatch --parsable --account=a0140 --partition=normal --time=00:30:00 --cpus-per-task=4 \
  --chdir="$W/census_06_20261020" --output="$W/census_06_20261020/logs/binding-%j.log" \
  --export=ALL "$CENSUS06_BUNDLE/bind_sf7.sbatch")
printf 'binding=%s\n' "$BIND_JOB"
# STOP: wait for COMPLETED, review coverage, all five loader PASSes and elapsed time.
# The binder fills config/INPUTS, removes pending entries, rebuilds the package/id,
# deploys to NEW code/<BOUND_ID>/ and reads back every payload SHA. PRE_ID is immutable.
# Import stage config, INPUTS, binding report, package_id and manifests for lead commit.
# STOP: lead review/commit; clean verifier tree for that commit; re-readback code and
# inputs (including SF7), rehash cyrillic, unchanged verifier x4, test-only smoke/full
# x4 against BOUND_ID, then binding_state --submit and real SF7 head test.
# Do not continue on the strength of pre-binding B receipts.
BOUND_ID=$(python3 -B -c 'import json,os,pathlib; print(json.loads((pathlib.Path(os.environ["SF7_BIND_WORK"])/"stage/docs/harvest/census06/package_id.json").read_text())["package_id"])')
[[ "$BOUND_ID" != "$PRE_ID" ]]
export CENSUS06_BUNDLE="$W/census_06_20261020/code/$BOUND_ID/docs/harvest/census06"
"$W/venv_l1/bin/python" -B "$CENSUS06_BUNDLE/binding_state.py" --submit
# Run real-head loader test in the coordinator's CPU allocation, not on login:
# "$W/venv_l1/bin/python" -B -m pytest -q -p no:cacheprovider \
#   --basetemp="$SF7_BIND_WORK/head-test" "$CENSUS06_BUNDLE/test_pipeline_033.py::test_sf7_head_sample"
unset CENSUS06_RUN CENSUS06_READOUT_OUT CENSUS06_CONFIG CENSUS06_BASELINE
export CENSUS06_SPLIT_FILE="$W/census_06_20261020/inputs/row_split.jsonl.gz"
export CENSUS06_SPLIT_SHA256=7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82
export E4_SMOKE=1 CENSUS06_ATTEMPT=smoke-split-002 CENSUS06_EXPECT_ROWS=200
bash "$CENSUS06_BUNDLE/submit_chain.sh" --account=a0140 --partition=debug --time=00:30:00
# regression -> afterok parity -> afterok census -> afterok readout.
# STOP for coordinator review: pipeline 0.3.3, 200 rows, no INFRA_ERROR, all
# invariants PASS, no held-out leaks; inspect polytonic counts, reasons, edits,
# head/full-loader coverage and measured timing before authorizing full.
# After completed smoke: read the measured TIMING line and review its caveats.
export CENSUS06_SMOKE_READOUT="$W/census_06_20261020/attempts/smoke-split-002.readout/readout.json"
"$W/venv_l1/bin/python" -B -c 'import json,os; print(json.load(open(os.environ["CENSUS06_SMOKE_READOUT"]))["census_timing_line"])'
# suggested_limit = ceil(projection × 1.5), capped at normal MaxTime 12:00:00.
# If the uncapped projection exceeds MaxTime, STOP: the cap cannot make it fit.
export SBATCH_TIMELIMIT=$("$W/venv_l1/bin/python" -B -c 'import json,os; print(json.load(open(os.environ["CENSUS06_SMOKE_READOUT"]))["census_timing"]["suggested_limit"])')
# This environment override reaches the full census only. Alternative:
# submit_chain.sh --full-time HH:MM:SS (argument wins over the environment).
export E4_SMOKE=0 CENSUS06_ATTEMPT=full-split-002 CENSUS06_EXPECT_ROWS=592466
export CENSUS06_BASELINE="$W/census_05_20261020/attempts/full-split-001/summary.json"
bash "$CENSUS06_BUNDLE/submit_chain.sh" --account=a0140 --partition=normal
unset SBATCH_TIMELIMIT
# Full census uses the measured override; regression/parity retain 00:05:00;
# readout 00:30:00. Same afterok chain. Record actual returned IDs.
# Readout is a sibling: attempts/full-split-002.readout/, outside the census run.
# jobs/readout.sbatch derives PIPELINE_VERSION from the bound package (=0.3.3),
# then runs the following inside its allocated afterok readout job (do not duplicate):
# srun -A a0140 --partition=normal --cpu-bind=none --nodes=1 --ntasks=1 \
#   "$W/venv_l1/bin/python" -B "$CENSUS06_BUNDLE/readout/census_readout.py" \
#   --expect-pipeline-version 0.3.3 \
#   --run "$W/census_06_20261020/attempts/full-split-002" \
#   --out "$W/census_06_20261020/attempts/full-split-002.readout" \
#   --baseline "$CENSUS06_BASELINE" --expect-rows 592466
# Set from the actual chain output only:
: "${FULL_READOUT_JOB_ID:?set actual full readout job ID}"
sbatch --account=a0140 --partition=normal --time=00:30:00 \
  --dependency="afterok:$FULL_READOUT_JOB_ID" \
  --output="$W/census_06_20261020/logs/flips-%j.log" --export=ALL \
  "$CENSUS06_BUNDLE/flip_report.sbatch"
# flip_report compares completed census05/census06 and writes the sibling
# attempts/full-split-002.flips/flip_report.json; it never writes census05.
```

Cleanup: deleted only `docs/harvest/census06/c2ad-pytest-tmp` (42243 logical file bytes),
this run's own pytest basetemp. Logs/XML and the remote test-only placeholder are
retained. Nothing else was deleted; see `c2ad_evidence/cleanup.json`.

Guarded lead commit list: `C2AD_COMMIT_PATHS.txt` and `C2AD_COMMIT_SHA256SUMS`.
Run `python3 -B docs/harvest/census06/guard_c2ad.py` before staging exact listed
paths. SHA256SUMS seals every listed file except itself. No git add or git commit
was run; unrelated existing changes and untracked files are excluded.

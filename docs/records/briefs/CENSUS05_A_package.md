# CENSUS05-A: build the census_05 package from cleanup/20261019 at CODE_SHA (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs; no deploy; no Slurm)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`. The lead commits. It shares its object store
with `~/Projects/greek-ocr-toolkit-main-next`, so `CODE_SHA` is readable here with `git show` / `git archive`.

**CODE_SHA = `3b4090bf9b15d2d2cac53ee55161e936157ec0e5`** (cleanup/20261019 after SEG10 + PIPE032 + Astra cycle-1 fixes; suite
7,305 passed / 0 failed / 102 skipped, per the coordinator). Later commits tonight are docs/state only.
- **Check:** `docs/records/harvest/seg_steps/s5_adopt/REPORT.md` ends `SEG10 READY`, and
  `docs/records/harvest/pipe032/REPORT.md` ends `PIPE032 READY`. Otherwise stop.
- **Attempts 1 and 2 stopped correctly**, evidence in `5ca995d34` and `0387e9177`:
  - attempt 1: a stale census digest;
  - attempt 2: segmentation `0.9-s5` vs the version invariant, and four N1 ledgers at numerics 0.2.

  PIPE032 fixed the first of attempt 2's blockers (segmentation is now `0.13`, label `0.9-s5`). Section 2 handles the second.
- **Point `audit_code_sha.py` at this CODE_SHA first.** The regenerated manifest names its in-repo components with the project
  prefix `greek-ocr-toolkit-pipe032/` (the worktree it was built in). Before that it was `greek-ocr-toolkit-main-next/`.
  - Map that prefix to the CODE_SHA tree, exactly as the old prefix was mapped, and report it.
  - In `census05_config.json`, `component_roots` must map `greek-ocr-toolkit-pipe032` to the package root.
  - Do not edit the manifest.
- **Expected versions:**
  - pipeline 0.3.2;
  - segmentation 0.13 (label 0.9-s5);
  - content_gate 0.3, final_eligibility 0.3, composer 0.3, census 0.7, numerics 0.3;
  - polytonic 0.7, cyrillic 0.3.
- **SEG10's `replay.jsonl` is not in git** at CODE_SHA, and not in the main-next working tree.
  - Find it, read only, via `replay_receipt.json` (search the data root and the worktrees). If you find it, hash-check it.
  - Otherwise rebuild the parity expectation: run SEG10's committed `replay.py` locally, under the packaged code (64 s in SEG10).
    It must reproduce SEG10's committed `flips.jsonl` (111) and `summary.json` exactly.
  - That replay, committed under `docs/harvest/census05/parity/`, is the parity expectation. Report which route you took.
- **Attempt 3 (evidence `ae2703a69`): continue from it, do not redo it.**
  - Done and verified:
    - the component audit, 35/35;
    - the partial source capture, 226 CODE_SHA-identical files;
    - native parity, 150/150 + 888/888 verdict and reason = SEG10, against the data-root `replay.jsonl` (`6e9ab21d…`);
    - split2, validated 320,479 rows;
    - expectations, 592,466 resolved by page override;
    - focused tests, 305 passed.
  - Re-verify these by hash and reuse them.
  - It stopped on the readout's hard-coded `PIPELINE_VERSION = '0.3'`.
  - **The lead authorizes this one readout change,** the readout's only version logic:
    - replace the constant with a CLI argument, `--expect-pipeline-version`;
    - the invariant becomes: every decision carries one and the same pipeline version, equal to the argument when given;
    - `readout.sbatch` passes the version read from the packaged `greekocr/harvest/line_pipeline.py` (`PIPELINE_VERSION`), not a
      literal;
    - update the readout tests for this, and make no other readout change.
  - The readout copy at CODE_SHA (`docs/harvest/census05/readout/`, docs only) will then differ. Package the changed readout as
    an additive file with its sha256, and write the exact patch to `docs/harvest/census05/readout_version.patch` for the
    coordinator to merge as a docs-only commit.
  - The readout refuses `--out` inside the run directory. Keep that. The job writes to the sibling `<attempt>.readout/`, and the
    expected outputs say so.
  - **Still to do:**
    - section 2: regenerate the FIVE N1 ledgers, including W1, which attempt 3 found also incompatible; run the full load
      validation; record-diff each regenerated ledger and list every status that moves;
    - sections 3–6: config, jobs, 200-row mocks, deploy manifest, `PROJECTS_SHA256`, commit list, FOLLOW_UP.
- **Keep the stops** as short "attempt 1/2" sections in the new hand-off.

**Bind by file hashes, not by commit.** Commits after CODE_SHA tonight touch `docs/` only, and the local merge to main carries
identical code files. Write `PROJECTS_SHA256`: the sha256 of every packaged file taken from CODE_SHA, with its repository path.
The re-pointing check (section 6) is then a hash comparison against that file, on any later commit.

- Output: `docs/harvest/census05/` (package, jobs, config, mocks, report). The readout script is already in
  `docs/harvest/census05/readout/` (CENSUS05-R): use it, do not edit it.
- Never write in `~/Projects/greek-ocr-toolkit-main-next` or any other worktree. Read only everywhere outside
  `docs/harvest/census05/`.

**Read first:**
- `docs/harvest/seg_census/HANDOFF_SEGCENSUS1.md`, `FOLLOW_UP.md`, `JOB_KINDS.md`, `COMMIT_LIST.md`, `census04_config.json`,
  `prepare_config.py`, `finalize_package.py`, `split_input.schema.json`, `jobs/`, `mock_batch.py`, `mock_stage.py`,
  `mock_split_stage.py`, and `package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census04.py`. Census_04
  is the template: same job shapes, verifier, mocks and hand-off format. Census_04 was deployed and verified but never run.
- At CODE_SHA: `docs/records/harvest/seg_steps/s5_adopt/` (SEG10), `docs/harvest/line_pipeline/README.md`, `tool_versions.json`,
  `greekocr/harvest/line_pipeline*.py`, `numeric_cells.py`, `filtering_assets/`, `scripts/harvest/build_filter_versions.py`.
- `~/Projects/greek-ocr-toolkit-main-next/docs/programme_20261019/NIGHT_PLAN.md`, step P3 (read only).
- The label versions, read only: `~/Projects/greek-ocr-toolkit-secondary/docs/labelfix/lqb/versions.json`,
  `docs/labelfix/secondary/HANDOFF_20261018.md`, `artifacts/ru1/ru1_v3_edits{.jsonl,_manifest.json,.sha256}`,
  `artifacts/ru1/ru1_v3_test_edits*`, `artifacts/n1/n1_v1_w1{.jsonl,_manifest.json,.sha256}`.

**Layout at CODE_SHA.** The clean-up moved docs under `docs/A_ocr_development/`, `docs/B_training_data/`, `docs/shared/` and
`docs/records/`. `docs/harvest/seg_census/package/` stays in place. Any path above may have moved: locate it with
`git ls-tree -r --name-only CODE_SHA`, and report the path you used. Code paths (`greekocr/`, `scripts/`, `tests/`) are expected
unchanged.

A tool is EXACTLY the owner's rules: add no guard, threshold or heuristic. This run packages; it changes no verdict logic.

## What census_05 is

| Item | Value |
|---|---|
| Pipeline | 0.3.2 (CODE_SHA), `routes_out_of_scope: ["polytonic"]` |
| Segmentation | 0.13, label 0.9-s5 (band 0.30–2.00, coordinator decision under the owner's end-to-end mandate, 19 Oct 21:34) |
| Content gate | 0.3 |
| Final eligibility | 0.3 |
| Parents | the five census_03 parents, same paths, rows and sha256 as `census04_config.json` (592,466 rows) |
| Metadata | census_03's `metadata.json`, same path and sha |
| Final policy | census_03's held-out crops (9,119) and held-out editions (61), unchanged |
| Corrections | see below |
| Split | the sourcing lead's finalized `row_split.jsonl` (step P1), pinned at submit time by path + sha256 |
| Output root | `$W/census_05_20261020/`, with `code/<package_id>/`, `attempts/<attempt>/`, `logs/` |

`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`.

## 1. The code

Build `docs/harvest/census05/package/` from CODE_SHA, the way census_04 built its package from its snapshot:
- Every file that exists at CODE_SHA is a byte copy of CODE_SHA's blob. List them with their sha256, and prove the identity with
  `git ls-tree`/`git cat-file` hashes.
- Include exactly what the three jobs import or execute, plus what the regression job's tests need. Derive the list from the
  imports and from census_04's 338-file manifest. Say which census_04 files are dropped and why, and which are new.
- **Additive files**, not at CODE_SHA (for example the census_04 split/diagnostics adapter, the job scripts, `prepare_config.py`):
  - list each one, with its sha256 and its census_04 origin;
  - first check whether CODE_SHA already contains the capability (split-input plumbing, diagnostics). If it does, use CODE_SHA's
    code and drop the additive file;
  - an additive file may be changed only to fit CODE_SHA's interfaces. Show every such diff;
  - none may read or change a verdict, a reason or a disposition.
- **Native runtime.** The Rust predictor, Node and codec are remote inputs bound by census_03's runtime manifest; built artifacts
  are not tracked. Prove that CODE_SHA's `scripts/harvest/filter_runtime/` sources (committed lineage 3679c8412) hash-equal the sources the bound binary was built from. If they differ,
  stop.
- **Versions.** From CODE_SHA's `tool_versions.json`, give the stage composition table: version and digest per tool, as in the
  census_04 hand-off. All tools must show the expected versions above.
  - Segmentation policy sha256 = SEG10's new sha.
  - Any digest that does not match a recomputation from the packaged bytes is a finding: stop.

## 2. The corrections (revised after attempt 2)

**What attempt 2 established.** Census_03's 14 canonical ledgers already contain exactly `ru1_v3_edits` (`4f1a51f5…`),
`ru1_v3_test_edits` (`c4b3a248…`) and `n1_v1_w1` (`94fb67c1…`). No ledger derives from a superseded version. So there are no
new correction ledgers to build, with two changes.

1. **Numerics restamp, by regeneration.** The four standing N1 ledgers (collection-v2-train/dev/test and collect-v3-W2:
   `404b3041…`, `fc3fb99a…`, `a09c903b…`, `f5e24bb3…`) carry numerics `0.2`/`7903c9ec…`. CODE_SHA's validator requires the
   active numerics version and digest.
   - Regenerate these four with census_03's own converter (`../greek-page-ocr-wave2/out/fp3/prepare_remote.py` /
     `finalize_remote.py`, read only: copy what you run into `docs/harvest/census05/`, and show every diff). Use the same producer
     inputs (hash-checked), and CODE_SHA's numerics functions and identity.
   - **Record-diff** each regenerated ledger against census_03's, by status, edits and holds. Every record whose content changes
     beyond `tool_version`/`tool_digest` is listed with its cause (expected: the numeric-adjacency fix).
   - No relabelling of old records without regeneration.
   - Check whether the W1 numerics ledger (`edb43176…`) and the cyrillic ledgers pass CODE_SHA's validator as they are. Regenerate
     any that fail, by the same rule.
2. **Polytonic out of scope** (coordinator decision under the owner's end-to-end mandate, 20 Oct; pipeline 0.3.2,
   `routes_out_of_scope`).
   - Set `routes_out_of_scope: ["polytonic"]` in the census_05 config.
   - Unbind the four polytonic ledgers (three released plus the SF7 candidate), and list them as "not bound in census_05".
   - **The SF7/TR2 note** for FOLLOW_UP: when SF7's audit passes, a later census puts polytonic back in scope and rebinds its
     ledgers at the then-current status. Nothing is prepared to apply tonight.
3. **Everything else stands unchanged:** the same file and sha. Verify each standing ledger loads under CODE_SHA's
   `ArtifactCorrector.load`, since attempt 2 showed it validates every record.
4. **Report, per tool × parent:** records, edits, holds and no-change, census_03 → census_05; whether each file is standing,
   regenerated or unbound; and its bytes and sha256. The regenerated files are new remote inputs under
   `$W/census_05_20261020/inputs/`.

## 3. Config and split

- Write `docs/harvest/census05/census05_config.json` from `census04_config.json`, changing only: code/codec/versions paths
  (to the new package root), the corrections from section 2, the output root, and `frozen_05`. `frozen_05` stays as a diagnostic
  join to census_03's decisions, unchanged.
- Give a field-by-field diff against `census04_config.json`.
- **The split** is not in the package. It is bound at submit time by `CENSUS05_SPLIT_FILE` + `CENSUS05_SPLIT_SHA256`, with the
  census_04 schema (`split_input.schema.json`: finalized `split` field; unique parent+row; one split per edition).
  - Without them, the job must refuse to run in full mode. Smoke may run without them. No silent mode-i fallback in full.
  - **The P1 file** (sourcing, sol/recut-v1 `aa860af55`, read only from `~/Projects/greek-ocr-toolkit-sol-recut`):
    `docs/harvest/collect_v3_admission/split2/row_split.jsonl.gz`, sha256 of the compressed bytes
    `7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82`, with `edition_map.jsonl`, `receipt.json` and `SPLIT2.md`
    alongside. Sourcing's figures: 320,479 rows (train 253,402 / dev 7,007 / test 60,070); 1,359 editions, 99 forced test. The
    436 BSB pages read after the snapshot stay unassigned.
    - Check the sha, and that the bytes equal `git show aa860af55:<path>`.
    - Validate it against the schema and the W1/W2 parents: rows per split per parent, unmatched rows both ways, editions, one
      split per edition, the 99 forced-test editions all test.
    - Then run it through the packaged loader, not census_04's, and report the counts.
    - Name its remote path under `$W/census_05_20261020/inputs/` in the deploy commands.
- **Metadata expectations.** Gate 0.3 resolves expectations as page override > book declaration > source policy. On every row
  whose metadata is available locally, count the rows that resolve at each level and the rows that do not resolve. Otherwise
  make the smoke job write that count, and say so.

## 4. Jobs

Copy the census_04 shapes into `docs/harvest/census05/jobs/`: `common.sh`, `regression.sbatch`, `parity.sbatch`, `census.sbatch`,
plus `readout.sbatch` from `census05/readout/`. The env names become `CENSUS05_*`.

- **In-script production settings:**

  | Job | Partition | Nodes | Tasks | CPUs | Time |
  |---|---|---|---|---|---|
  | regression | normal | 1 | 1 | 256 | 00:05:00 |
  | parity | normal | 1 | 1 | 256 | 00:05:00 |
  | census | normal | 1 | 1 | 256 | 04:00:00 |
  | readout | normal | 1 | 1 | 16 | 00:30:00 |

  Smoke overrides partition and time on the command line only, never in the scripts.
- **Parity:** replay the saved 150 + 888 evidence under the packaged 0.9-s5. Verdict AND reason must equal SEG10's
  `docs/records/harvest/seg_steps/s5_adopt/replay.jsonl` exactly, row for row, or the job fails.
- **Regression:** the packaged tests, including `tests/test_content_gate.py`, `test_line_pipeline.py`, `test_integration_fixes.py`
  and the four `test_seg_*.py`.
- **Census:** as census_04, writing under `$W/census_05_20261020/attempts/$CENSUS05_ATTEMPT/`.
- **Readout:** chained after census, writing `readout/` inside the attempt.
- **Runtime.** Census_03 took 01:49:19 for 592,466 rows under 0.5. Estimate the 0.9-s5 census time from the per-row timings in
  the s4 and SEG10 replays, against the same rows' 0.8 timings. Say whether 04:00:00 holds with margin. Do not change it; report
  it.

## 5. Mocks (local, no Slurm)

Rerun the census_04 mocks against the new package. Double only `srun` and native image/reader I/O.
- **Native replay:** 150/150 + 888/888 verdict and reason equal SEG10's replay.
- **The 200-real-row whole-pipeline mock** through the real spooled scripts, smoke and full, with and without a fake finalized
  split. Report the ADMIT / DROP / HOLD table as census_04 did.
- **The readout** on each mock attempt: its last line, and its invariants all PASS.
- **Full mode without a split** refuses.

## 6. Deploy manifest and commands

- `DEPLOY_PATHS.txt`, `DEPLOY_SHA256SUMS`, and `package_id.json` (package id = sha256 prefix of DEPLOY_SHA256SUMS, 16 hex), plus
  `verifier_allow_untracked.txt` if any gitignored payload remains (prefer none).
- `COMMIT_LIST.md` with an exact pathspec file for the lead's commit.
- `FOLLOW_UP.md` with literal, unexecuted commands:
  1. **Deploy:** copy to `$W/census_05_20261020/code/<package_id>/`, refusing a non-empty destination, then a per-file sha256
     readback. Also copy the new correction ledgers and the split file to `$W/census_05_20261020/inputs/`, with a readback.
  2. **Verify:** the unchanged `~/Projects/greek-page-ocr-wave2/scripts/ops/verify_deploy.py`, once per job kind, with
     `--repo`/`--commit` = this worktree's commit. VERIFY_OK is required for all five.
  3. **Smoke:** coordinator commands, `E4_SMOKE=1`, `--partition=debug`, with `--time` within the debug partition's limit
     (`scontrol show partition debug`, read in CENSUS05-B; put the placeholder here), chained regression → parity → census →
     readout with `afterok`.
  4. **Full:** `E4_SMOKE=0`, in-script settings, the same chain, with `CENSUS05_SPLIT_FILE`/`SHA256` set.
  5. **Expected outputs** per attempt: `CURRENT.json` complete, `decisions.jsonl`, `admitted_train.jsonl`, `admission_records`,
     `pending_*`, `summary.json`, `readout/READOUT.md` + `readout.json`, with what each must contain for P4.
  6. **Re-pointing at main:** after the local merge, the command that proves main's tree equals CODE_SHA's for every packaged
     path (`git diff --quiet CODE_SHA main -- <paths>`, and a recompute of `PROJECTS_SHA256` on main's tree). A difference means a rebuild.
  7. **The per-reason count report format:** the readout's `READOUT.md` sections and last line, as the P4 input.

## Report

Write `docs/harvest/census05/HANDOFF_CENSUS05.md` in the census_04 hand-off format, `receipt.json`, and a scope guard listing
the changed files (all inside `docs/harvest/census05/`).

**Last line:** `CENSUS05-A READY: CODE_SHA <sha8>; package <id> files <n> (CODE_SHA-identical <n>, additive <n>); versions pipeline 0.3.1 seg 0.9-s5 gate 0.3 final 0.3; corrections <n> ledgers (new <list>, standing <n>, superseded-source <n>); parity 150 <n>/150 888 <n>/888 = SEG10 <yes|no>; mock 200 ADMIT/DROP/HOLD <a/d/h>; readout invariants <ok>; split <validated n rows|absent>; runtime estimate <hh:mm> vs 04:00; tests <n> passed <n> failed`

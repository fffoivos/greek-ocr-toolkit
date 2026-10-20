# SEGCENSUS-1c hand-off — ready for lead commits, not deployed

Updated 2026-10-19T14:19:53+03:00. SEGCENSUS-1 and 1b preparation are complete under the 1c rulings. No shared repository index/refs were written; no sol-recut source was changed; no remote file/job was changed. No deployment, verifier, Slurm test-only check, submission or correction reader ran. No all-ink diagnostic was added.

## Source capture and package provenance

- capture = sol-recut working tree on 19 Oct (includes 0.8); no Clariden code snapshot equals it
- census_03 ran snapshot 87407ec7430a375f (all 325 manifest files match)
- the census_04 package derives from 87407ec7 with only the 0.8 segmentation files + tool-versions changed

The last sentence describes changes **among baseline files**: exactly the three owner 0.8 files and tool_versions.json. The baseline is not the live capture. Two additive Python files implement the separately requested diagnostics/split plumbing: `numeric_cells.py` and `line_pipeline_census04.py`. All other baseline bytes, including the FP3 pipeline/core/source adapters and inherited caches, remain unchanged. [Composition](package_composition.json) records every stage hash and every changed/added file. All 150 capture paths also match their archived hashes now. [Capture](SOURCE_CAPTURE.md), [inventory](capture_inventory.json).

Ruling 1 is applied: geometry_observations.py, row_inclusion.py and pyproject.toml are sol-recut byte-for-byte. All three 0.8 implementation files match `git show 410f4566:<path>` in both this worktree and package. [Byte identity](byte_identity_1c.json). The capture commit title is **owner filter pipeline 0.2 source as of 18 Oct**.

## Full-suite baseline comparison

**No regression test IDs.** Current: **4,051 passed, 36 failed, 5 setup errors, 19 skipped**. Pristine sol/seg-cells `22f0caf7a`: **4,023 passed, 37 failed, 32 setup errors, 19 skipped**. Every current failure/error ID also fails on pristine. The additional baseline failures are absent untracked runtime/evidence dependencies, not improvements claimed for the owner tool. [Exact ID comparison](suite_comparison.json), [current log](full_current.log), [baseline log](full_baseline.log), [current XML](full_current.xml), [baseline XML](full_baseline.xml).

The only deselected file is **tests/test_seg_cp7c.py**. The identical missing `seg/CP5_verification.json` collection failure was proved on pristine; no historical evidence was copied. [Fresh collection proof](pristine_collection_1c3.log). CP7d and the standalone CP7c fixture test were NOT excluded; their runtime missing-file failures remain in the comparison.

Both full runs used the same Python 3.11 interpreter, flags and deselection, without stopping early:

```bash
PYTHONPATH=/private/tmp/segcensus1c3-bootstrap:/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect \
  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/.venv/bin/python -B \
  -m pytest -q -p no:cacheprovider --basetemp=/private/tmp/segcensus1c3-<current-or-baseline>-tests \
  tests --ignore=tests/test_seg_cp7c.py --junitxml=<current-or-baseline-receipt.xml>
```

The pristine tree lacks untracked `line_pipeline` modules imported by its tracked segmentation tests. The identical `sitecustomize.py` for both runs put the active checkout first on sys.path, then appended the read-only archived `source_capture/greekocr/harvest` directory to `greekocr.harvest.__path__` for absent modules. Tracked baseline modules won; no checkout files were copied or edited. Without that supplement pristine stops during segmentation-test collection. Other missing native assets were retained as baseline failures. The collector path supplies the pre-existing external collector dependency. The supplement did not change the current run's counts.

A direct shared worktree add was already sandbox-denied in 1c2. This run created an isolated temporary shared-object clone, then `git worktree add --detach` of origin/sol/seg-cells within it. Pristine `git status --short` was clean before removal. The temporary worktree and clone were removed after comparison. No shared Git metadata was modified. For a rerun, recreate the same small bootstrap; its contents are:

```python
import sys, os
sys.path.insert(0, os.getcwd())
import greekocr.harvest
greekocr.harvest.__path__.append('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/seg_census/source_capture/greekocr/harvest')
```

The final package suite, including all packaged pipeline regressions, split/diagnostic tests and the segmentation/cell tests against package imports, passes **292 tests + 13 subtests**. [Log](final_package_tests.log). This is separate focused verification; it is not added to the full-suite pass count. The two spooled regression job mocks each passed 144 tests + 13 subtests.

## Stage composition

| Stage | Version | SHA256 tool digest |
|---|---|---|
| census | 0.5 | `670ad2e3ea7cfcb214d8c5f12bae30163fc57fb433f8137bcd5deaa6be7d4957` |
| composer | 0.2 | `c56ad770599f7d3d0c399d10e0088855d39c1d07d6627ff261ff7889d0f55b0c` |
| content_gate | 0.2 | `c56ad770599f7d3d0c399d10e0088855d39c1d07d6627ff261ff7889d0f55b0c` |
| content_repair | 0.2 | `c56ad770599f7d3d0c399d10e0088855d39c1d07d6627ff261ff7889d0f55b0c` |
| cyrillic | 0.3 | `f63e1ba8696adb47dfc07b283c615fe83deb3f1d2fd28acbf0300de495235123` |
| dashes | 0.1 | `07a2c3f17d94f2467d70ea3c6af0b056c3f338707b0a45fefcab5eddccf4220c` |
| final_eligibility | 0.2 | `c56ad770599f7d3d0c399d10e0088855d39c1d07d6627ff261ff7889d0f55b0c` |
| inventory | 0.1 | `07a2c3f17d94f2467d70ea3c6af0b056c3f338707b0a45fefcab5eddccf4220c` |
| numerics | 0.2 | `7903c9ec8d1c52cefd8f4458879be1ea656b0b52874726c3169b7c7adc17a893` |
| polytonic | 0.7 | `de1a9a8bc6b0598f5b28ac213faa13ce00ced95aa2754291fc183373f60c60c5` |
| segmentation | 0.8 | `512e362a691c6f2f425acc41e587b4b751dedbaadd10077d42309ed3f1f7bebd` |

Segmentation policy SHA256: `e5b635ff9a04cc66f454a68e01ce9773229672e655b3ee08296ee5c0d149ee15`; segmentation digest: `512e362a691c6f2f425acc41e587b4b751dedbaadd10077d42309ed3f1f7bebd`. Only segmentation and census fingerprints differ from census_03. The census digest truthfully refreshes its native component and names both additive adapters; census remains the documented 0.5 orchestration generation. All correction/composer/content/final-eligibility tool entries retain census_03 hashes and versions. No scientific rule changed outside segmentation 0.8.

## Four census_02 integration defects retained as fixed

1. Metadata identity/expectations and held-out crop wiring: census_03 binds all 592,466 rows and preserves original v2 cohorts; the exact metadata, protected crops and policy remain inputs. The external held-out crop regression passes.
2. SF7 complete scoped outcomes: 235,257 canonical records include all outcomes, preserving 605 candidate-pre-audit corrections and their holds. No proposal is promoted.
3. N1/RU1 canonical ledgers: 556,245 N1 and 19,898 RU1 records retain parent/raw text bindings, scoped negatives and holds. Original correction artifacts are unchanged.
4. Numeric adjacency: the existing digit/separator/digit scan replaces the unrelated punctuation condition; the census_03 source fix and regression test are retained.

Evidence: [FP3 hand-off](remote_evidence/HANDOFF.md), [integration diff](remote_evidence/integration_fixes.diff), [source validation](remote_evidence/source_diff_validation.json). Census_03's 65,900 admissions are historical v2 results, not a census_04 prediction. The SPLIT1 sourcing proposal covers all **320,479 W1/W2 input rows**; 142,959 is the census_03 unassigned-hold subset, not the whole input population.

## Diagnostics and input preservation

Every decision gets a `diagnostics` object after the complete Pipeline.evaluate result, through an additive Ledger adapter. It contains 0.8 row-frame box long side, height, aspect ratio and unchanged character/prediction length ratio; saved characters; the pure classify_cell `is_cell`, `is_small_image`, `is_numeric_output` and reasons; frozen 0.5 verdict/reason. Unmeasured boxes remain null with the original segmentation reason/evidence available. These descriptive fields are never read by any verdict.

The frozen input is census_03's immutable generation `g1-a21c3b465ca94eee80cb5bd34b336d69/decisions.jsonl`, SHA256 `b2355093affcb54e6fdcd7733212909c348c5a1971ed2de545000deece1cb98d`, 8,900,374,978 bytes. It was hash-checked read-only on Clariden, not downloaded or regenerated. [Readback](remote_evidence/frozen05_hash.json). Each frozen diagnostic joins parent/row plus original crop/raw-text identities. A frozen stage that did not run records that fact instead of inventing a verdict.

Removing or replacing **all** added diagnostics yields identical complete row decisions in both 200-row split modes, plus explicit KEEP/DROP/UNCERTAIN unit cases. No all-ink box or new owner policy guard exists.

[census04_config.json](census04_config.json) preserves census_03 parents, counts, hashes, path maps, literal text priorities, metadata, corrections, final policy, predictor and runtime inputs. `prepare_config.py` rebases code/codec/version paths only in full mode and records input preservation. Smoke derives at most 40 literal rows per parent and subsets the same correction records, retaining original source bindings in receipts. It does not overwrite any input. The output root is **$W/filter_pipeline_20261018/census_04_seg08/**, with separate mode/smoke/full attempt directories.

## 1b: split input

**Split file consumed before: no. Plumbing: added.** The existing source adapter already accepts row_splits/book metadata overrides, but census_03 does not read a pinned split file. The additive entry point now consumes `split_input: {"path": "/absolute/file.jsonl[.gz]", "sha256": "<file-bytes-sha256>"}` before canonical row registration. Absent/null means mode i; original unassigned rows retain today's holds.

The sourcing docs are `../greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/split1/SPLIT_PROPOSAL.md` and `row_split_proposal.jsonl.gz`. Their proposal schema is parent_id, row_id, edition_id, proposed_split, forced. The runtime schema deliberately consumes a **finalized** `split` field (train/dev/test), retaining parent_id, row_id and edition_id; forced/extra provenance may remain. A proposal's `proposed_split` alone is not a final allocation. [Machine-readable schema](split_input.schema.json). JSONL and gzip JSONL are accepted, hashing compressed bytes for gzip. Unique parent+row keys and one split per edition are input integrity requirements.

Only collect-v3-feature parents are overridden. Absent rows keep their original split. The join sets edition identity and split from the same final assignment; no admission rule is added. Existing metadata remains untouched. Canonical correction records were bound to the old split: the adapter validates them against that original binding, retains their original record/artifact hashes, then derives an explicit split-only binding with the split input hash. Tool versions/digests, statuses, edits, holds and source artifacts remain unchanged; v2 cohorts retain the original adapter checks. Both modes use the same code and all ordinary correction/eligibility/leakage checks.

No real split file is pinned now, and no owner proposal was allocated. Mode ii remains conditional on the sourcing lead's finalized owner-approved file. Train allocation still requires all pipeline checks; dev/test stays in evaluation diagnostics.

## Job kinds and mocks

[JOB_KINDS.md](JOB_KINDS.md) gives measured evidence and margins. All are normal, one node, one task, 256 CPUs/task: **regression 00:05:00; parity 00:05:00; census 04:00:00**. Filtering, imported corrections and merge/admission/export remain one census kind, as measured in census_03; there are no independently measured or newly invented filter/correction shard jobs.

Fresh packaged native replay, unchanged source bindings: **150/150 + 888/888 verdict AND reason byte-exact** versus gate2. Fresh split-bound native replay: **150/150 + 888/888 byte-exact again**, consuming a fake pinned split with train/dev/test assignments. [Stage results](mock_stage_results.json), [split-stage results](mock_split_stage_results.json). Only verdict/reason equality is asserted; timing/evidence serialization is not claimed byte-identical. No reader ran.

Whole pipeline: a **200-real-row slice** (150 segeval + 50 calibration) runs through the real spooled batch scripts and CLI. Saved freshly verified native measurements and explicit synthetic no-change reader outcomes are the mock boundaries; source text/crop bindings are checked. Actual row adapters, canonical correction imports, composition, eligibility, dedup and atomic exports execute. This is a plumbing mock, not evidence of correction accuracy or a production retention forecast.

| Mode | Rows | ADMIT | DROP | HOLD | V3 train/dev/test/unassigned | Complete | All diagnostics invariant |
|---|---:|---:|---:|---:|---|---|---|
| i: no split | 200 | 73 | 40 | 87 | 0 / 0 / 0 / 112 | yes | yes |
| ii: fake finalized split | 200 | 133 | 53 | 14 | 91 / 9 / 11 / 1 | yes | yes |

Both E4_SMOKE=1 mock slices have 144 rows (six fixture parents; production has five). E4_SMOKE=0 runs all 200 mock rows. All three job kinds run from an unrelated submit cwd with scripts copied into a Slurm spool, an explicit deployed-bundle env variable, and **12 recorded srun calls**, all under the intended new output root. [Batch results](mock_batch_results.json), [harness](mock_batch.py). Every v3 admission remains absent in mode i; the intentionally omitted mode-ii row remains unassigned.

## Commit and deploy hand-off

[COMMIT_LIST.md](COMMIT_LIST.md) enumerates exact pathspec files for the capture and package commits and the four ignored payload files requiring verifier exemptions. Package ID: **bb1ea164338b3068**, **338 deploy manifest entries**; [expected SHA table](DEPLOY_SHA256SUMS). Runtime binaries are existing remote inputs, not copied portable assets; the local Mac predictor symlink is ignored and excluded from the deployment.

Use **../greek-page-ocr-wave2/scripts/ops/verify_deploy.py** unchanged. Its committed-file requirement is why this run stops before deployment. [FOLLOW_UP.md](FOLLOW_UP.md) gives exact verifier commands per kind and coordinator smoke/full submission commands for both modes. The lead commits first; a follow-up authorizes the copy, per-file readback and real test-only verification. **Deploy: NOT RUN. VERIFY_OK: NOT RUN. Remote sha table: pending. Test-only: NOT RUN. Submission: NOT RUN.**

[receipt.json](receipt.json) is the machine-readable final receipt. Earlier stopped attempts remain in their named logs; this hand-off supersedes their STOPPED status.

## b2: deploy + verify

Updated 2026-10-19T11:24:20.848830+00:00. **STOPPED: SSH banner exchange timeout; deployment not confirmed.**

HEAD `410b0100ce51f32dd0928c9e09b28914a9fad876` passes the required ancestry gate: the sole extra commit above `56e5695c5` changes only `docs/records/briefs/SEGCENSUS1d.md`. No tracked changes existed before the attempt. All 338 local payload files match `DEPLOY_SHA256SUMS`; manifest SHA256 is `bb1ea164338b30681cf45e36f1db41dc7dee8ebfbd7bd2f2df4f4fd8adce834f`. The repository-relative archive includes all four allowed gitignored cache files. No Git index or ref writes were made.

Remote root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/code/bb1ea164338b3068/`. The first, read-only SSH check returned `DESTINATION_ABSENT` (exit 0). The second SSH connection, intended to recheck the destination and extract with `--keep-old-files`, failed before a remote execution was confirmed (exit 255):

```text
Connection timed out during banner exchange
Connection to UNKNOWN port 65535 timed out
```

Per the brief's SSH-failure stop rule, no further remote connections or credential repair were attempted. No extraction success was received, no remote writes are confirmed, and no deployed file count is claimed.

| Kind | VERIFY_OK | Smoke mode-i test-only | Full mode-i test-only |
|---|---|---|---|
| regression | NOT RUN | NOT RUN | NOT RUN |
| parity | NOT RUN | NOT RUN | NOT RUN |
| census | NOT RUN | NOT RUN | NOT RUN |

Per-file remote SHA table: **NOT RUN, 0/338 verified**. No job was submitted. The coordinator smoke/full mode-i commands remain in [FOLLOW_UP.md](FOLLOW_UP.md); they cannot be finalized against deployed paths until deployment and remote verification succeed. They were not executed.

Machine-readable failure receipt: [receipt_b2.json](receipt_b2.json), also embedded under `b2` in [receipt.json](receipt.json). Owner-gated SSH access must be restored before a new attempt; recheck the remote destination and stop if it is non-empty. **SEGCENSUS1d is not READY.**


## b2: deploy + verify

Updated 2026-10-19T11:27:26.963121+00:00. **READY: deployed and verified; no submission.** This completed attempt supersedes the earlier stopped attempt above, preserved in [previous_stopped_receipt.json](b2_evidence/previous_stopped_receipt.json).

HEAD `410b0100ce51f32dd0928c9e09b28914a9fad876` passes: the sole extra commit above `56e5695c5` touches only `docs/records/briefs/SEGCENSUS1d.md`. No .git writes were made. Existing handoff/receipt edits were preserved across the unchanged verifier's clean-worktree checks.

Remote root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/code/bb1ea164338b3068/`. Read-only preflight returned `DESTINATION_ABSENT`. The deploy connection rechecked the destination before extraction with `--keep-old-files`; it returned `DEPLOY_EXTRACT_OK` and **338 files**. Remote writes were confined to this root.

The exact FOLLOW_UP.md verifier block ran unchanged:

```text
regression: VERIFY_OK
parity: VERIFY_OK
census: VERIFY_OK
```

Full verifier receipts: [regression](b2_evidence/verify-regression.json), [parity](b2_evidence/verify-parity.json), [census](b2_evidence/verify-census.json). Each records 338/338 remote SHA checks, a successful test-only check, and a currently valid certificate with more than two hours remaining.

Independent [per-file remote readback table](b2_evidence/remote_readback.tsv): **338/338 exact SHA256 matches**, including all four allowed ignored cache files; zero missing or mismatched files. Manifest SHA256: `bb1ea164338b30681cf45e36f1db41dc7dee8ebfbd7bd2f2df4f4fd8adce834f`.

Six additional mode-i dry checks cleared split/config environment bindings and passed E4_SMOKE=1 or 0 explicitly. [Exact argv and scheduler responses](b2_evidence/test_only.json):

| Mode | Kind | Exit | Scheduler response |
|---|---|---|---|
| smoke-mode-i | regression | 0 | `sbatch: Job 3697849 to start at 15:22:50 a using 288 processors on nodes nid006273 in partition normal` |
| smoke-mode-i | parity | 0 | `sbatch: Job 3697850 to start at 15:22:51 a using 288 processors on nodes nid006273 in partition normal` |
| smoke-mode-i | census | 0 | `sbatch: Job 3697851 to start at 15:22:51 a using 288 processors on nodes nid006273 in partition normal` |
| full-mode-i | regression | 0 | `sbatch: Job 3697852 to start at 15:22:52 a using 288 processors on nodes nid006273 in partition normal` |
| full-mode-i | parity | 0 | `sbatch: Job 3697853 to start at 15:22:52 a using 288 processors on nodes nid006273 in partition normal` |
| full-mode-i | census | 0 | `sbatch: Job 3697854 to start at 15:22:53 a using 288 processors on nodes nid006273 in partition normal` |

All scheduler calls used `sbatch --test-only`. The displayed job numbers/start times are scheduler dry-check responses; no real job was submitted. Two supplemental-helper attempts encountered Python 3.6 API incompatibilities before any scheduler call; the completed helper and final results are archived in b2_evidence.

Final coordinator commands below are copied from FOLLOW_UP.md, checked against the three deployed job paths and their remote SHA256 readbacks, and **not executed**. Creating the future output/log directory and submitting remain coordinator actions. Smoke first; full is a separate action after successful smoke review.

```bash
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export CENSUS04_BUNDLE="$W/filter_pipeline_20261018/code/bb1ea164338b3068/docs/harvest/seg_census"
RUN_ROOT="$W/filter_pipeline_20261018/census_04_seg08"
mkdir -p "$RUN_ROOT/logs"
submit_census04() {
  local regression parity
  regression=$(sbatch --parsable --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/regression-%j.log" "$CENSUS04_BUNDLE/jobs/regression.sbatch")
  parity=$(sbatch --parsable --dependency="afterok:$regression" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/parity-%j.log" "$CENSUS04_BUNDLE/jobs/parity.sbatch")
  sbatch --dependency="afterok:$parity" --chdir="$RUN_ROOT" --export=ALL \
    --output="$RUN_ROOT/logs/census-%j.log" "$CENSUS04_BUNDLE/jobs/census.sbatch"
}

# Mode (i): no split input pinned. Smoke first; inspect its publication before full.
unset CENSUS04_SPLIT_FILE CENSUS04_SPLIT_SHA256 CENSUS04_CONFIG
export E4_SMOKE=1 CENSUS04_ATTEMPT=smoke-mode-i-001
submit_census04
# Separate coordinator action only after successful smoke review:
export E4_SMOKE=0 CENSUS04_ATTEMPT=full-mode-i-001
submit_census04
```

Machine-readable completion receipt: [receipt_b2.json](receipt_b2.json), also embedded under `b2` in [receipt.json](receipt.json). No job was submitted.

# P1POOL: unlabelled, train-only census_06 pool

Package preparation only. No jobs were submitted and no git staging/commit was performed. The production input is exclusively `census_06_20261020/attempts/full-split-002`, after its full run and sibling readout complete. The census_05 rows below are development evidence, never production output.

The production manifest is `p1pool.jsonl`; `selection.jsonl` is its label-free reconstruction selection. The final `P1POOL_RECEIPT.json` is generated in the new selection attempt and reaches `status=ok` only after every crop passes SHA verification. The receipt in this package describes preparation and pending inputs; it is not a completed pool receipt.

## Selection rules

ADMIT or correction-only HOLD, and only `collection-v2-train` or W1/W2 with `split=train`. Every selected row must have content_gate version 0.3, a nonexcluded content gate stage, segmentation version 0.13 and a KEEP segmentation result. DROP is excluded. A kept_unverified polytonic route does not change these conditions and never supplies labels.

The exact allowed final reason set is `{correction_unresolved, required_evidence_unresolved}`. A HOLD needs at least one reason, and every reason must belong to that set. Route statuses are not substituted for final reasons. In particular, `content_repair_unresolved` is out under the coordinator's explicit ruling, despite its name.

| Final HOLD reason | census_05 count, all parents/splits | In/out |
|---|---:|---|
| correction_unresolved | 44,940 | in, subject to every other check |
| required_evidence_unresolved | 0 | in when emitted as a final reason |
| content_repair_unresolved | 27,976 | out |
| segmentation | 2,462 | out |
| unexpected_script | 2,266 | out |
| same_crop_conflicting_labels | 396 | out |

Source: `vendor/inputs/readout.json`, `tables.all_disposition_reasons`; the observed HOLD reasons sum to 78,040. Unknown/new final reasons remain out. The census_06 readout is pending; its vocabulary must be reviewed before submission for any changed interpretation.

Exclusions reuse REL4's SPLIT2 edition-to-member join and the exact seal04 test/dev + candidates_v3/readout key and crop-sha union. `rel4_exposure.py` contains the original exclusion-setup body verbatim, with its source and copied-body hashes in `REL4_EXPOSURE_COPY.json`. The original modules are byte copies pinned by `VENDOR_SHA256.json`; their three core hashes were checked against deployed REL4 `60fa450c`. Extra P1 checks exclude benchmark editions/documents and the completed census configuration's heldout editions/books and crop hashes. W1/W2 edition identities must join SPLIT2 exactly; dev/test editions are out even if a row says train. Every final row is re-audited against all these sets.

Deduplication is sequential: (a) keep one row per exact crop SHA, deterministically taking the lowest `(parent_id,row_id)`; (b) among the survivors, for each SPLIT2 edition represented by multiple member documents, elect the document with most pool rows, then the lexicographically lowest document ID. Keep only that member's rows. The receipt reports `pixel_rows_removed`, `multi_member_editions`, `edition_member_rows_removed` and the elected members. This implements the explicit coordinator rule; TRAINING_DIRECTIONS line 50 and DATA_PLAN_v2 §§1.6/on-disk require edition deduplication but do not specify a different member-election rule. The SHA is the census/CROPS4 exact encoded crop SHA; this is the existing REL4 identity contract.

## Historical flags

The actual list was located in `~/Projects/greek-ocr-toolkit/docs/harvest/{round1,vouli,round2,parliament,openarchives,mixed,cyrillic,wikisource}/rejected.jsonl`, selecting reason `label_in_holdout`. It contains exactly 1,557 flagged records among 84,799 initial rejects. `FLAGS_EVIDENCE.json` records each source file hash and count; `flags.jsonl` retains only wave and row ID.

This is the historical population described in TRAINING_DIRECTIONS_20261016.md:50 and DATA_PLAN_v2_20261016.md:37, not a demonstrated census_06 overlap. The builder performs an exact row-ID join across every census parent and excludes every eligible match; it records both total joins and the eligible exclusion count. No exclusion count or zero-overlap claim is invented while census_06 is pending. There are zero matches in the 250 available W1 head admission records; this says nothing about other parents or the full census. Final flags status is pending exact join, rather than a claim that all 1,557 apply to census_06.

## Crop custody and no labels

REL4's unchanged `input_check` and `crop_index` enforce census_06 CURRENT/summary/readout/run-binding, released sf7, CROPS4 c05/c06 full/smoke custody and crop-union consistency. The builder also opens the completed census ledger read-only and immutable, checks its readout SHA before and after reading, and joins its normalized observation metadata in the exact admission-record order. This supplies HOLD page/bbox and book/edition metadata absent from admission_records. A nonempty WAL blocks production.

Existing W1/W2 crops come from the authenticated CROPS4 union; collection-v2-train crops must reside in `$W/collection_v2/crops/`. Existing files are referenced by absolute path plus SHA and never copied. Missing ADMIT crops fail rather than silently reducing yield. Missing W1/W2 HOLD crops use only the new `$W/p1pool_crops/<attempt>/parent/source/id.png` tree.

`materialise_hold.py` is an explicit-selection wrapper around the unchanged, byte-pinned CROPS4 `page_job`, `load_code` and worker initializer. No changes were made to CROPS4. It imports `line_pipeline_native.reconstructed_crop` from the bound census code and requires module SHA `e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7`. The crops batch sources the unchanged CROPS4C `binding_checks.sh`; the wrapper also checks that code, census manifest, interpreter and PNG preload match REL4's CROPS4C binding. CROPS4 uses temporary PNGs plus atomic no-clobber hard links: conflicting existing files are never overwritten. A crop attempt must be new; failures are inspected and rerun under a new attempt rather than resumed over an incomplete tree.

Both manifests have an explicit field allowlist. The final one carries parent/row identity, source, book, edition, train split, crop path/SHA, disposition, reason class/reasons and primary class. Selection adds only page path/SHA, bbox and color mode. No text, label, raw_text, final_text, decision payload or raw_text_sha256 field can appear. `raw_text_sha256` is not used for deduplication and is omitted. Fixtures and vendored source artifacts contain original labelled inputs for tests; those are not pool manifests.

## census_05 projection and sizing

Projection from readout counts, before P1 exclusions/deduplication, not a measured census_06 yield:

| Parent | ADMIT train | correction_unresolved HOLD train | Projected ceiling |
|---|---:|---:|---:|
| W1 | 50,736 | 3,677 | 54,413 |
| W2 | 117,901 | 22,956 | 140,857 |
| collection-v2-train | 196,234 | 7,914 | 204,148 |
| Total | 364,871 | 34,547 | 399,418 |

The observed HOLD final reasons partition the census_05 HOLD rows, so these correction counts are not a sum of overlapping route queues. Actual exclusions and the two dedup losses require the complete run. Projected new W1/W2 HOLD crops are at most 26,633 before exclusions/dedup. At the c05 W1 CROPS4 mean of 1,221,239,678 / 68,779 = 17,756 bytes/crop, this is approximately 0.47 GB of new PNGs; differing HOLD widths/pages may change that estimate. V2 files are referenced, not copied.

Select: one normal node, one CPU, 12 GB, two hours. Crops: one normal node, eight CPUs, 16 GB, two hours. Both use account a0140, no GPU request. Selection hashes full large inputs and existing crops and repeats custody checks; its full runtime is unmeasured. These are conservative requested limits, not timing qualification. No timing/job probe was submitted.

## Verification and remaining coverage

`tests.log` and `tests.xml` preserve the passing suite. The tests exercise each exclusion, mixed HOLD reasons, DROP, both gate checks and versions, 0.3.3 kept_unverified, pixel/member dedup and election ties, label-field rejection, exact REL4 exposure-body reuse, synthetic end-to-end HOLD selection, missing ADMIT failure, unsafe attempt rejection, and CROPS4's no-clobber behavior.

Real head evidence: 250 admission_records and matching decisions, all W1 because the exports are single files ordered by parent. The requested coverage of all five parents is not yet met under strict head-only sampling. The launcher explicitly blocks submission while this required five-parent test is pending. Permission for bounded indexed read-only samples of the other four parents was requested; without that permission, no such SQLite sample was taken. The synthetic split tests cover all five named parent cohorts, but are not presented as real five-parent evidence.

`CROP_CHECK.json` records 20/20 byte-equal reconstructions from the real census_05 pending_cyrillic head queue, imported from the checked census code on the login node. `crop_check.log` records all binding checks. Only 20 temporary crops were written under a private new scratch directory and that directory was removed. This validates the HOLD reconstruction function and page custody; it does not claim those queued rows all pass P1's final reason filter. The check needs no job.

`VERIFY.sh package` checks package hashes and all vendored hashes. `VERIFY.sh inputs` checks available pinned inputs lightly (large files by size) and reports census_06 PENDING. Local verification can check only embedded inputs; remote readback checks remote pins too. With an explicit `--rel4-config`, inputs verification requires all completed REL4/census bindings, and the coordinator launcher refuses pending inputs.

## Exact coordinator block (after census_06 full + readout)

Run in the deployed P1POOL package directory. First obtain the completed, bound REL4b configuration through REL4's existing bind workflow, including completed CROPS4C full/smoke receipts and released sf7. These are intentional production prerequisites. Supply that exact configuration path as REL4_CONFIG. The block derives every reconstruction binding from it; no production path is guessed.

```bash
set -euo pipefail
W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export PYTHON="$W/venv_l1/bin/python"
export P1POOL_PACKAGE="$PWD"
: "${REL4_CONFIG:?absolute INPUTS.json path from completed REL4b binding}"
export REL4_CONFIG
export ATTEMPT=p1pool_c06_full_01
# Only completed full-split-002 plus its sibling readout is accepted by REL4.
bash "$P1POOL_PACKAGE/VERIFY.sh" package
bash "$P1POOL_PACKAGE/VERIFY.sh" inputs --rel4-config "$REL4_CONFIG"
export CENSUS_CODE=$("$PYTHON" -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["crops4c"]["context"]["census_code"])' "$REL4_CONFIG")
export CENSUS_MANIFEST=$("$PYTHON" -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["crops4c"]["census_manifest"]["path"])' "$REL4_CONFIG")
export PROJECTS_SUMS_ROOT=$(dirname "$CENSUS_MANIFEST")
export PROJECTS_SHA256=$("$PYTHON" -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["crops4c"]["census_manifest"]["sha256"])' "$REL4_CONFIG")
# Coordinator executes this only after reviewing five-parent test coverage.
bash "$P1POOL_PACKAGE/submit_p1pool.sh"
# Launcher prints select ID and crops ID; crops uses --dependency=afterok:<select ID>.
# After both finish, inspect this final receipt and require status=ok:
# $W/scaling_w3/p1pool_attempts/$ATTEMPT/P1POOL_RECEIPT.json
```

No submit command above was executed during package preparation. See COMMIT_LIST.md and guard_commit.py for the scoped commit candidates; no git add or commit is authorized by this package.

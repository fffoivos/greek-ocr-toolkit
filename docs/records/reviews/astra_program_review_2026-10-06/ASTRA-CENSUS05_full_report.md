# ASTRA-CENSUS05 — independent certification review, 20 October 2026

**Not certified for submission: one HIGH finding requires a fix and re-review.** The deployed code and input identities pass. The blocking certification issue is the readout's false-negative held-out-crop check, not an observed production leak.

Scope: repository `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-census`, inspected HEAD `e2836fa6288290bd61cdd42c61b37b1b35031257`; deployed package `17b0eb1ca7fe81a7`, rooted at `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/17b0eb1ca7fe81a7`. Local records reside under `docs/records/harvest/census05`; the deployment retains `docs/harvest/census05`. This reviews the specified pipeline 0.3.2 package before submission, not completed census results or release-v3 readiness.

The repository and Clariden were read only. No implementation edits, job submissions or background jobs were performed. Remote commands were reads and `sbatch --test-only`. Audit programs, scratch copies, synthetic witnesses and outputs are beside this report. The repository status before and after showed only the pre-existing review harness log. Pytest used `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`, and temporary output directories; the final package and readout verification commands ran from the repository root.

## Findings, most severe first

### H1 — HIGH: the readout omits configured held-out crops and can certify a leak

Location: [census_readout.py:140](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-census/docs/records/harvest/census05/readout/census_readout.py:140), with the incomplete set consumed at lines 258 and 271. The deployed file is SHA256 `749d9d1bf6eff04cabf5ddd4f2f7c36e8769d8ab06c4e9128e8e474fad1c56ba`.

The reader inserts configured held-out **editions**, then collects crop hashes from observed dev/test rows. It never inserts `config.final_policy.heldout_crop_sha256`. That violates the readout brief's explicit requirement to count admissions whose crop is in the held-out crop list.

Firsthand recount of this package's actual parents and finalized split:

| Protection measure | Count |
|---|---:|
| Configured protected crop hashes | 9,119 |
| Distinct observed non-train crop hashes | 124,425 |
| Configured protected hashes also in the observed set | 2,215 |
| Configured protected hashes absent from the readout's crop set | **6,904** |
| Train observations with configured protected crops absent from that set | **1,828** |
| Of those, also absent from the readout's protected-edition set | **1,828** |

Those 1,828 are **input observations**, not claimed admissions: 1,545 collection-v2-train and 283 W1. Exact IDs and bindings are in [protection_recount.json](protection_recount.json). The pipeline's own deduplicator correctly unions configured and observed protected crops, and its protection tests pass. This finding concerns the independent output check.

I constructed a one-row synthetic generation containing one train admission whose crop is explicitly protected in its run binding, with consistent publication and output hashes. The exact deployed reader, invoked with expected version 0.3.2 and expected row count 1, returned **exit 0**, `complete yes`, **heldout leaks 0**, and **14/14 PASS**. See [readout_witnesses.json](readout_witnesses.json), [witness program](readout_witnesses.py), and [the reader's output](configured_crop_leak.readout/readout.json).

Failure scenario: a regression or incorrectly produced export admits one of these protected observations, and the checkpoint report falsely certifies zero leakage. That compromises the release-v3/benchmark separation check even though today's upstream deduplicator contains the right rule.

Required fix: populate the readout's protected-crop set with the union already specified by the pipeline; test config-only protection with no matching dev/test observation, including a crop whose edition is not independently protected. Require one reported leak and nonzero CLI exit for the witness. Rebuild the additive readout package, regenerate its manifest/package ID, deploy, rehash and re-review before submission. No segmentation rule change is needed.

### M1 — MEDIUM: the 02:18 estimate is arithmetic, not qualification against the actual baseline

Locations: `timing_replay.py:23–30`, `runtime_estimate.json`, and the packaged S4 replay's `worker('08')`.

Re-summing all **1,038** raw timing rows gives **49.5921863243 s** for the labelled 0.8 comparator and **62.6184204374 s** for SEG10: ratio **1.2626670667**. Multiplying the census_03 principal step's **6,559 s** gives **8,281.8332905 s = 02:18:01.833**, leaving **6,118.1667095 s = 01:41:58.167** within four hours; limit/estimate = **1.73874546**. [Recalculation](runtime_estimate_recomputed.json).

However, census_03's verified manifest names segmentation **0.5**, whereas the paired Mac comparator is **0.8**. The measured ratio also covers segmentation on review cohorts, not the full workload with split rebinding, frozen-decision loading, correction validation, registration, deduplication and exports. Live accounting confirms census_03 **COMPLETED**, total **01:49:40**, principal step **01:49:19**, limit **04:00:00**. [Live accounting](baseline_accounting_live.json).

Log this as a sizing heuristic with substantial nominal margin, not a measured upper bound. The real smoke must establish native runtime compatibility, input preparation time and usable outputs before the full run. A 200-row smoke cannot by itself qualify population timing tails.

### M2 — MEDIUM: the claimed tests need a documented scratch layout to reproduce

The isolated deployed package reproduces **360 passed, 9 skipped in 2.96 s**. The 20 readout tests reproduce **20 passed in 13.22 s** when copied byte-for-byte into their original directory layout with the historical fixtures available. Thus **380 distinct passes are reproducible**, with those qualifications. [Package log](package-tests.log), [readout-view log](readout-view-tests.log), [view setup](run_readout_view.py).

Direct execution of the current checkout's readout tests together with `tests/test_routes_out_of_scope.py` instead gives **9 failed, 23 passed in 13.38 s**: five old mock paths and one old census_03 evidence path do not resolve from the relocated `ROOT`; three successful behavioral tests subsequently try to write receipts into the read-only repository and fail. All **12 PIPE032 scope tests pass**. The direct failures are preserved in [readout-tests.log](readout-tests.log) and [JUnit](readout-tests.xml).

Fix the test-root/fixture resolution and direct receipt outputs to pytest's temporary directory. This is a reproducibility defect, not nine demonstrated readout algorithm failures. The separate H1 witness remains valid even though all 20 original assertions pass. The deployed regression sbatch invokes the eight packaged modules; it does not include the separate PIPE032 scope module or the readout suite.

### M3 — MEDIUM: the input archive custody claim is stronger than the inspected tree

The handoff calls the **35 gzip correction chunks “committed”**, but neither the inspected HEAD nor `0736754c12dc6240fed2557df2a8ab68bb5f8841` lists them at the advertised archive location. They are absent from this review checkout, and no matching archive entry was found in its cleanup custody receipts/move manifest.

They do exist in the producer workspace `greek-ocr-toolkit-segcensus/docs/harvest/census05/corrections/archives`. I independently hashed and decompressed all 35 there: **476,840,657 uncompressed bytes**, reconstructing all five expected N1 file hashes exactly. The full local ledgers and deployed inputs also pass independently. [Archive audit](correction_archive_audit.json).

Correct the claim and establish an explicit durable location/receipt for these inputs. This does not invalidate the presently verified deployed bytes; it does limit reconstruction from this checkout alone.

### L1 — LOW: “complete” does not establish train-export completeness

The readout implements the requested `admitted_train ⊆ ADMIT ∩ train` check, but not equality or uniqueness. A consistent synthetic generation with **3 ADMIT/train decisions and an empty admitted_train export** returns **exit 0, complete yes, 14/14 PASS**. [Witness](missing_train_export.readout/readout.json).

This is a limitation of the stated subset invariant, not a violation of that narrower specification. Before using “complete” as release readiness, independently reconcile the full train export with eligible decisions, or extend the readout accordingly. No actual missing train export is asserted here.

## Package and runtime identity

Recomputed from filesystem bytes and Git blobs, rather than accepting the handoff totals:

| Check | Firsthand result |
|---|---|
| Deployed manifest entries | **167** |
| CODE_SHA-identical source files | **154/154**, compared with `git show 3b4090bf9b15d2d2cac53ee55161e936157ec0e5:<source>` |
| Additive files | **13**, exact disjoint remainder |
| Remote regular-file inventory | **167**, no extra regular files |
| Local versus remote manifest hashes | **167/167 equal** |
| Component bindings / distinct paths | **35/35 / 23**, all match |
| Recomputed tool digests | **11/11 match** |
| PROJECTS_SHA256 source-path set | **154/154 exact** |
| Initial remote package/input/baseline hash checks | **184/184 equal** |
| Additional runtime, metadata and baseline-summary bindings | **12/12 equal**; runtime manifest also rehashed |

Manifest SHA256: `17b0eb1ca7fe81a789c70c596d80d8ed69e4ea1597a227656f7f873f3f95ddf6`. PROJECTS_SHA256 file hash: `4864a067da0a597ea410d5bcb8346ec6736fb6f689beddff7f8d92da53c333e6`. [Local identity evidence](identity_local.json), [remote result](identity_remote.json), [remote hashes](remote_sha256sum.txt), [remote tree](remote_tree.txt).

Active versions are pipeline **0.3.2**, segmentation **0.13 / label 0.9-s5**, gate **0.3**, final eligibility **0.3**, numerics **0.3**, Cyrillic **0.3**, composer **0.3**, census **0.7**. The segmentation policy hash is `5888fe704e6170b51081d6fa4200a725d2b29f0c70301f238faf7b32088b5b99`. All stage digests are in the local evidence table.

The deployed native predictor is `2cc882d68be85cbef8ac43bf27a963bd6b249ff89ece80a23ff4821a1d3feacf`; runtime manifest is `84ed3add6190afe57198a9654bd16a0fc9464126d6c09a14cc5cd3e5f0ca68a4`. Python binary, Node, four compiled modules and three loaded codec files match the manifest. These are byte checks, not a fresh execution of the Clariden runtime. [Runtime evidence](runtime_hashes_live.json).

All four historical verifier receipts say `VERIFY_OK`, with no reasons and `job_submitted:false`; their manifests bind this package. Fresh remote comparisons and scheduler checks supplement those historical receipts.

## Input and configuration verification

I hashed and recounted all five local parents and matched their hashes remotely:

| Parent | Rows | Final train | Final dev | Final test |
|---|---:|---:|---:|---:|
| collection-v2-train | 214,436 | 214,436 | 0 | 0 |
| collection-v2-dev | 13,522 | 0 | 13,522 | 0 |
| collection-v2-test | 44,029 | 0 | 0 | 44,029 |
| W1 | 101,098 | 71,796 | 1,720 | 27,582 |
| W2 | 219,381 | 181,606 | 5,287 | 32,488 |
| Total | **592,466** | **467,838** | **20,529** | **104,099** |

These are input split counts, not admissions. Split2 is SHA256 `7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82`: **320,479 unique assignments**, **1,359 editions**, **253,402 train / 7,007 dev / 60,070 test**, **99 forced-test editions / 52,468 forced-test rows**, all test. Recount found **zero duplicate assignments, conflicting edition splits, missing W1/W2 assignments or orphan split rows**. The actual packaged loader also returns **320,479** assignments. [Input recount](input_recount.json), [configuration probes](config_checks.json).

`routes_out_of_scope` is exactly `["polytonic"]`. The four census_03 polytonic correction bindings, including the candidate ledger, are absent. Five N1 ledgers and five standing Cyrillic ledgers are bound. Retaining SF7 source/manifest components does not bind or run its excluded correction route.

Full N1 record-by-record comparison, preserving file order:

| Parent | Records | Applied → applied | Unresolved → unresolved | No-change → no-change | Other changes beyond version/digest |
|---|---:|---:|---:|---:|---:|
| v2 train | 214,436 | 0 | 1,919 | 212,517 | 0 |
| v2 dev | 13,413 | 0 | 0 | 13,413 | 0 |
| v2 test | 43,766 | 0 | 0 | 43,766 | 0 |
| W1 | 93,998 | 47 | 582 | 93,369 | 0 |
| W2 | 190,632 | 0 | 0 | 190,632 | 0 |
| Total | **556,245** | **47** | **2,501** | **553,697** | **0** |

There are **zero status moves**, zero added/removed/reordered records, and zero other record-field changes after excluding only `tool_version` and `tool_digest`. Every new record binds numerics 0.3 and its active digest. [Ledger diff](ledger_diff.json). The five unchanged Cyrillic files contain **19,898 records**: **778 applied**, **450 unresolved**, **18,670 no-change**; file hashes match the standing bindings. [Cyrillic recount](cyrillic_recount.json).

Comparison with the actual census_03 config (`b945ffa6…`, also rehashed remotely) confirms unchanged parents, metadata, final policy, predictor, runtime manifest, 64 workers, prefetch factor 64 and 120-second row timeout. Changes are code/codec/component-root locations, correction bindings, the frozen-output diagnostic input and release scope; split2 is added by preparation. Codec bytes are unchanged. [Config comparison](config_compared_census03.json).

Fresh preparation checks preserve full-mode parents/corrections/metadata/final policy exactly. A locally relocated smoke input produces **40 rows per parent, 200 total**. Missing full-mode split or an unpaired path/SHA exits **2** before creating output. The split's hash is validated by the packaged loader before execution. These preparation checks do not run a census.

## Tests, parity and readout

SEG10's external replay is **42,991,967 bytes**, SHA256 `6e9ab21d28340ec7acf9d2b1b39bc7cf899a6bfc87b754e59d986265da417f32`, matching `receipt_04.tsv:2`. Concatenated decompression of the two packaged chunks recreates those bytes exactly: **1,705 replay rows**.

The independent policy replay compares both verdict and reason and passes **150/150 segeval1 + 888/888 calibration**. The retained native result file was separately compared row-for-row, including row objects and cohort/order: **1,038/1,038 exact**. A fresh native sample selects every twentieth row within each cohort plus every S4→S5 verdict flip: **24 segeval1 + 75 calibration = 99/99 exact**, in **7.489 s**, with crop hashes checked. It uses the pinned local debug predictor `d2fe37a5…`, not the Clariden release executable. [Raw recomputation](parity_recomputed.json), [program](parity_audit.py).

The deployed `parity.sbatch` re-evaluates saved evidence through the current policy; it processes **zero native images**. Its success must not be described as a fresh Clariden image replay. No new independent accuracy qualification is claimed; the s5 band was fitted on existing owner marks.

Fresh readouts of the actual saved mock generations reproduce:

| Mock | Rows | ADMIT | HOLD | DROP | admitted_train | Invariants |
|---|---:|---:|---:|---:|---:|---|
| smoke mode i | 200 | 43 | 128 | 29 | 43 | 14/14 PASS |
| smoke mode ii | 200 | 119 | 39 | 42 | 103 | 14/14 PASS |
| full mode ii | 200 | 119 | 39 | 42 | 103 | 14/14 PASS |

Each has **77 polytonic `not_applied_out_of_scope` route statuses**. These are synthetic-correction/native-result mocks, not production admissions. [Recomputed readouts](mock_readouts_recomputed.json).

The 14 reported invariants cover disposition totals, admitted-train membership, held-out leaks, gate/segmentation and gate/route consistency, decision duplicates/missing/unexpected rows, missing reasons, pipeline version, stratum totals, bound inventory totals, summary dispositions and expected rows. Publication/output hashes and run binding are checked before counting. H1 and L1 describe their demonstrated limits.

## Intended behavior relative to census_03

The source comparison uses census_03's prepared source, with its pipeline/config/manifest bytes checked against Clariden. The parent canonicalizer, correction adapter and parallel scheduler are byte-identical. The policy-bearing pipeline changes match the specified gate/final-eligibility and scope features; segmentation changes belong to the adopted s5 lineage. Relocation/data-resolution and reporting changes also exist and should not be called byte-identical behavior. No additional disposition rule was found in the reviewed active pipeline changes. [Source comparison](baseline_source_comparison.json), [pipeline diff](greekocr_harvest_line_pipeline.py.diff), [census diff](greekocr_harvest_line_pipeline_census.py.diff).

| Intended change | Rows affected and consequence |
|---|---|
| Segmentation 0.5 → 0.13/s5 | Rows reaching segmentation can change through the adopted other-row gate, orientation, curve/small-component measurement and 0.30–2.00 band. This is more than changing the S4 band alone. Sample parity checks the final package against SEG10, not equality with census_03. |
| Gate/final eligibility 0.3 | Mixed-script words drop and unexpected scripts hold before native work; raw short-line/cell/numeric rules now apply early. Cells with more than one letter/digit bypass the old prose/nonletter/numeric-shape restrictions at final eligibility. Consequently both deciding reasons and final dispositions can change. |
| Polytonic excluded | Routed rows retain raw polytonic text and carry `not_applied_out_of_scope`; missing/proposal/failed polytonic evidence no longer creates that route's HOLD. Other routes and final checks still apply, so these rows are not automatically admitted. Earlier exclusions keep `not_run_due_to_prior_exclusion`. |
| N1 0.3 binding | The five regenerated ledgers cause **no status/edit/content movement**. Census_03's prepared code already contains the same digit/separator/digit automatic-negative rule; the version number does not imply an additional corpus-wide behavior change. |
| split2 | All **320,479** W1/W2 rows receive finalized split/edition bindings, replacing unassigned inputs. This can remove split-identity holds and changes protected editions/crops and train deduplication. V2 cohorts remain frozen. |
| Held-out crop union | Already present in census_03's prepared census source and retained here; it is not a new census_05-only rule. |

Exact population transition counts and the final set of admitted rows cannot be certified before the full census exists. The readout's optional baseline table compares aggregate counts; it is not a row-by-row causal attribution. Do not treat the mock deltas or the 99-row parity sample as those missing production results.

## Scheduler, restart and downstream risks

Fresh `sbatch --test-only` results are **8/8 exit 0**, covering smoke and full for all four job kinds. [Exact commands and responses](test_only_live.json).

| Job | Full partition | Nodes/tasks | CPUs | Full limit | Smoke override |
|---|---|---|---:|---|---|
| regression | normal | 1/1 | 256 | 00:05:00 | debug / 00:10:00 |
| parity | normal | 1/1 | 256 | 00:05:00 | debug / 00:10:00 |
| census | normal | 1/1 | 256 | **04:00:00** | debug / 00:10:00 |
| readout | normal | 1/1 | 16 | 00:30:00 | debug / 00:10:00 |

The documented full block explicitly sets `E4_SMOKE=0`, `CENSUS05_ATTEMPT=full-split-001`, expected rows **592466**, and the pinned split. It passes no debug/time override. Smoke uses `E4_SMOKE=1`, `smoke-split-001`, expected rows **200**. Readout outputs are sibling `.readout` directories. The common script's default remains smoke; submitting the census script without the documented full environment is not a full run.

At inspection, the remote `attempts/` and `logs/` directories did not exist and `squeue` showed no user jobs. The proposed smoke/full attempt names therefore had no current output collision. These scheduler responses are predictions, not submitted jobs or successful smoke execution.

The census ledger rejects changed config/code/runtime/input bindings, preserves committed observations/decisions, validates measurement cache entries and atomically publishes immutable generations. Passing package tests exercise interrupted resume, failed dedup/export, publication invalidation, timeouts, stale bindings and corrupt cache. A same-binding restart resumes unfinished observations. Existing HOLD/INFRA_ERROR decisions are not automatically retried: the underlying API has explicit retry flags, while the deployed census04 CLI exposes neither. Diagnose failure and choose a deliberate recovery/new attempt; do not assume resubmission repairs saved errors. There is no attempt-wide job lock, so avoid concurrent writers to one attempt.

No full census output is available. After H1 is fixed and re-reviewed, the required real smoke must still be inspected before full execution; completed output and release/benchmark suitability require the later results checkpoint. Zero pending polytonic rows is expected under the declared exclusion and does not certify polytonic correction quality. Benchmark quotas, candidate supply and training readiness remain unproven by this package review.

VERDICT: NOT CERTIFIED for submission; fix H1, redeploy and re-review | BLOCKERS: 0 | HIGH: 1

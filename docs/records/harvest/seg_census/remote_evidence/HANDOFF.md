# FP3 — census_03 prepared, 19 October 2026

**Prepared and validated; no Slurm submission and no executed census_03.** The conditional prediction is **65,900 eligible train candidates after final checks and global crop dedup**, from 67,134 before crop checks. It assumes the unchanged native policy/runtime repeats census_02 segmentation outcomes. These IDs are a prediction, not a training release. W1/W2 remain entirely `unassigned`.

All remote mutations were confined to `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03` and the new prepared build. The requested new code copy is nested at **`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/prepared/87407ec7430a375f/code/87407ec7430a375f/projects`**, keeping the remote write boundary. The owner's `attempts/census_02`, `prepared/d74ad2830c479f7b`, and `code/d74ad2830c479f7b` were read only. [owner_unchanged.json](final/owner_unchanged.json) verifies original sizes/mtimes and hashes for files below 100 MB; source/config hashes are pinned. Original SQLite reads used `mode=ro&immutable=1`, with an empty WAL. The existing local `train/mix.py` edit was untouched.

**Concrete files and fingerprints.** Remote config: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/prepared/87407ec7430a375f/census_w64_pf64.json`; remote metadata: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/prepared/87407ec7430a375f/metadata.json`; execution output: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03`. The complete local prepared copy is [prepared/87407ec7430a375f/](prepared/87407ec7430a375f/), including code, versions, metadata and all correction ledgers. Local row metadata is [row_metadata.jsonl.gz](row_metadata.jsonl.gz); full scoped SF7 outcome evidence is [sf7_scoped_outcomes.jsonl.gz](sf7_scoped_outcomes.jsonl.gz).

| Binding | Verified SHA-256 |
|---|---|
| Config | `b945ffa6bc16cd5c137223f4b48748bf9c31f5ce900fa393473a2bbe427c5b5a` |
| Expected run binding | `0bbf7c145d6782d8d661fe8c4c76eaf68c0ffdb3fd5f79dfaf636a0560951012` |
| Metadata | `dd2da6548a2dd6ed5624299be552e32204efb85220f4463590fb4c8e3ddd3bf5` |
| Versions | `6fbf2ab19da3851353d97eae07d22859d3c6d78c1c20f72046202682438beefe` |
| Codec, unchanged | `94485f72eac0aaf2324dc60b1c02110b271d362a79c440e2ce6bf6f4604997b9` |
| Predictor, unchanged | `2cc882d68be85cbef8ac43bf27a963bd6b249ff89ece80a23ff4821a1d3feacf` |
| Native runtime, unchanged | `84ed3add6190afe57198a9654bd16a0fc9464126d6c09a14cc5cd3e5f0ca68a4` |

The five parents preserve census_02 paths, hashes, counts, raw-text priority and path maps exactly. [config_receipt.json](config_receipt.json) contains their full bindings. Canonical registration was checked for every row:

| Parent | Rows | Split |
|---|---:|---|
| v2 train | 214,436 | train |
| v2 dev | 13,522 | dev |
| v2 test | 44,029 | test |
| W1 | 101,098 | unassigned |
| W2 | 219,381 | unassigned |

**Defect 1 — metadata inputs.** All **271,987 v2 + 101,098 W1 + 219,381 W2** rows bind to 1,917 books and 10,022 pages. V2 edition IDs are the literal canonical `doc` IDs, with the existing parent split and literal legacy `source_split` retained. W1/W2 join `(source,item)` to both collection manifests and resolved catalogues; exact provider/item identities share an edition across waves. Exact matching v2 source URLs supply aliases where available. No split allocation was invented. The original 271,987-entry crop map is copied unchanged; [metadata_join_report.json](metadata_join_report.json) records zero split changes and zero ambiguous mechanical joins.

Every row receipt identifies its parent SHA, original line number and record SHA, plus its metadata book/page keys and metadata SHA. Book declarations retain per-field provenance for identity, split, source, item, year, languages, scripts and orthography; page declarations retain their declared class values. This is a document/provider identity join, not a new claim that all title-level or mirrored-work aliases have been independently reviewed.

V2 expectations use the frozen CENSUS3 source/class/document table, including its explicit mixed-class branch and the two Serbian document IDs. Cyrillic catalogue languages are retained rather than inferred from recognized letters. W expectations use the owner's source declarations: BSB/IA/NLG poly1850 and Kosmopolis/Lekythos poly1900 are Greek/polytonic with their recorded years; IA Greek–Latin permits both scripts; Serbian is modern Serbian Cyrillic; IA Russian is historical Russian; ELSTAT declares the numeric role; Gazette is monotonic from 1982, polytonic before that boundary. See [prepare_remote.py:106](prepare_remote.py#L106) through expectation construction and [finalize_remote.py:53](finalize_remote.py#L53) for the preserved mixed-class branch. Frozen source definitions: `F/greek-ocr-toolkit-sol-recut/greekocr/harvest/admission.py:335–453` and `serbian.py:9–10`, where `F=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/code/d74ad2830c479f7b/projects`.

Held-out inputs cover the unchanged v2 dev/test cohorts, 1,527 historical `wikisource_human` rows, 3,600 `e1_real_test` rows and 2,665 unique LQB truth-line IDs. Of the LQB IDs, 2,652 occur in these parents. [protected_cohorts.json](protected_cohorts.json) binds their source hashes, 61 declared external edition IDs, 9,119 external/reference/raw crop hashes, and exact population joins. Existing non-train edition and dev/test crop protection still runs. The external reference files and original labels were not rewritten.

The frozen code had no external-crop input hook. To make the requested protection effective, the new census copy unions the bound external crop list into its **existing** held-out crop set, retaining the same `heldout_crop_identity` DROP rule. This is two lines of input wiring at new `line_pipeline_census.py:165–166`, separately visible in [integration_fixes.diff](integration_fixes.diff) and covered by [test_external_crop_input.py](test_external_crop_input.py). Final eligibility thresholds and exclusion rules are unchanged.

**Defects 2–3 — complete scoped correction ledgers.** All **811,400 canonical result records** are bound to exact parent/id/split/crop/raw text, method version and tool digest. Duplicate tool/parent/ID records are rejected. Producer hashes, original statuses and holds survive conversion. The method versions retain their named iterations; the new exact source/component hashes identify this patch.

| Tool | Canonical records wired | Existing producer coverage and negatives |
|---|---:|---|
| SF7/polytonic | 235,257 | All 124,669 SF7 A outcomes; full v2-train coverage after scoped negatives; applicable v2 dev/test negatives |
| N1/numerics | 556,245 | All 214,436 N1 train rows, all 629 W1 ELSTAT records, plus exact candidate-negative records |
| RU1/Cyrillic | 19,898 | All 680 train + 548 dev/test sparse outcomes, plus implemented regime/candidate negatives |

The SF7 stream was decoded from the actual Clariden job `labelfix_sf7_20261017/output_3687228/release/overlay_A.jsonl.gz`, SHA `80421ec0c9579d4dcf0d483e3d906873959210c0f44bda3b2af1325c5f7abf65`. It contains **10,807 unchanged + 686 composer-corrected + 113,176 HOLD** outcomes. Exactly **605** corrected records have qualified raw-parent edits; all remain in a separate `candidate_pre_audit` release and become proposal-only HOLD at runtime. The other **81** are the release receipt's normalization-only exclusions and receive explicit zero-raw-edit outcomes. No SF7 audit acceptance was fabricated. On the saved segmentation-KEEP slice, all **580** previous proposal-only routes remain proposal-only.

N1 train conversion checks `parent_label` against exact raw text and uses `new_label`; its **212,517 no-change rows + 1,919 held rows** preserve all **2,623 held slots**, with zero train separator edits. W1 preserves **47 applied rows + 582 held rows**, including partial edited rows kept held. See [prepare_remote.py:224](prepare_remote.py#L224) and [coverage.json](coverage.json). This fixes the omission/`parent_label` mismatch without changing the frozen legacy adapter (`F/.../line_pipeline_adapters.py:33–48`).

No sparse omission becomes a no-change verdict. SF7 negatives are limited to the declared v2 `script_class != greek_poly` scope (`scripts/labelfix/clariden/l1_common.py:39–44`). N1 negatives require no token with at least four ASCII digits and an internal single `-`/`.` slot (`scripts/numerics/n1tr.py:41–53`; `greekocr/numerics/tokens.py:1–89`). RU1 negatives reuse the existing declared-modern or historical-Russian/no-final-`ь` rules (`F/.../line_pipeline.py:248–254`). Definitions and their hashes are embedded in result evidence. No W1/W2 SF7 no-change coverage was invented from absent marks or absent releases.

**RU1 scope remains truthful.** Catalogue evidence identifies Bulgarian and Serbian books inside artifacts described elsewhere as Russian. Among no-hold edited records, train has **170 Russian-eligible / 254 ineligible** rows; dev has **64 eligible**; test has **254 eligible / 36 ineligible**. Ineligible edits remain held by the unchanged Russian-only guard. On the saved segmentation-KEEP slice, **167 train + 62 dev + 235 test = 464** existing edits become applicable, with **15,919** prior Cyrillic holds receiving scoped no-change outcomes. This is not permission to rename Bulgarian/Serbian as Russian or widen RU1. [prediction.json](final/prediction.json) records the exact language intersections; catalogue source copy is under `sources/greek-ocr-toolkit/docs/harvest/cyrillic/books.json`.

**Defect 4 — numeric adjacency.** Only the candidate-negative condition changes in `line_pipeline.py:246`: `not any(c in text for c in ".-·")` becomes `not re.search(r"\d\s*[.\-·]\s*\d", text)`. Unrelated sentence punctuation no longer blocks the negative. Spaced numeric candidates such as `1 . 234` remain unresolved, preserving the original regression. The population scan finds **65,480** newly negative digit-containing rows: train 18,087; dev 838; test 2,470; W1 12,958; W2 31,127. These overlap imported N1 negatives and are not an independent ADMIT yield. [numeric_patch.json](numeric_patch.json), [integration_fixes.diff](integration_fixes.diff), and [test_numeric_adjacency.py](test_numeric_adjacency.py) bind the change.

**Verification and expected effect.** Final suite: **134 tests and 13 subtests passed**. Saved parity: **888/888 segmentation decisions/reasons**, 184 context reconciliations, identical segmentation policy bytes, zero new native images. Codec, predictor, parent hashes and runtime remain identical to census_02. [tests_final.log](tests_final.log), [policy-parity.json](policy-parity.json), [validation.json](validation.json), and [owner_unchanged.json](final/owner_unchanged.json) are the receipts. [source_diff_validation.json](source_diff_validation.json) confirms that the only production source changes are the numeric condition and external crop-input wiring; 320 other frozen files are byte-identical.

The actual no-execute CLI preflight is [dry_cli_preflight.json](dry_cli_preflight.json). Its CLI is reporting-only; independent all-row/hash/schema validation supplies the config and expected run fingerprints above. No `--execute` census command was run. The prediction reuses saved segmentation and identical-text inventories, verifies all bindings and applies the current graph/final gates; four disjoint read-only row ranges are merged before **global**, ordered crop dedup. [validate_predict_remote.py](validate_predict_remote.py) and [aggregate_prediction.py](aggregate_prediction.py) reproduce it. The original all-row inventories/decisions remain untouched.

| Prior disjoint HOLD group | Prior rows | Expected movement with saved segmentation |
|---|---:|---|
| V2 identity only | 51,780 | All reach pre-dedup diagnostic ADMIT: 41,725 train, 3,079 dev, 6,976 test |
| W1/W2 identity only | 84,116 | Edition binds; all remain HOLD on unassigned split only: W1 18,629, W2 65,487 |
| Correction unresolved | 242,255 | 70,216 leave this terminal blocker; 172,039 remain. Of the exits: 29,652 pre-dedup ADMIT, 34,511 split-only HOLD, 5,459 content HOLD, 594 final DROP |
| Content repair unresolved | 45,348 | 24,332 clear the content blocker and reach split-only HOLD; 21,016 retain it |
| Segmentation uncertain | 151,931 | Unchanged HOLD; all 17,036 original segmentation DROPs also remain DROP |

Correction-route changes overlap and must not be summed as unique rows: prior numeric unresolved **85,701 → 27,942**, with **57,759** qualified no-change results; Cyrillic **24,787 → 8,404**, with **464 applied + 15,919 no-change**; polytonic obtains **14,667** qualified no-change results, **3,366** no-longer-applicable routes, and **163** routes excluded elsewhere, leaving **135,897 unresolved + 580 proposal-only**.

For **A**, 41,725 identity-only + 25,409 former correction-held train rows reach pre-dedup ADMIT = **67,134**. Global crop protection removes **980**, duplicate observations remove **252**, and two conflicting-label rows stay HOLD: **65,900 predicted train candidates**. Their origin is 40,661 former identity-only + 25,239 former correction-held rows. [predicted_post_dedup_train.jsonl](final/predicted_post_dedup_train.jsonl) contains their exact IDs/crop/final-text hashes, without presenting them as an executed release.

For **B**, all **320,479 W1/W2 rows remain unassigned**, so expected train ADMIT is **0**. Metadata/ledger coverage exposes **142,959 split-only candidates** (the original 84,116 plus 34,511 from correction HOLD and 24,332 from content HOLD). An owner edition-level split decision is still required.

| Predicted train disposition after crop checks | Rows |
|---|---:|
| ADMIT candidate | 65,900 |
| HOLD | 145,131 |
| DROP | 3,405 |
| Total old train | 214,436 |

Dev/test keep all original rows and original input references; their conditional diagnostic ADMIT counts (3,984 dev / 10,314 test) are not training supply. Full pre-dedup parent dispositions, old-to-new terminal transitions, route coverage and exact candidate IDs are in [prediction.json](final/prediction.json). A real census_03 must be checked against these counts and the saved-segmentation condition before any release claim.

**Staged job, not submitted.** [census03.sbatch](census03.sbatch) clones the frozen census payload order, runtime and 256-CPU step shape, with all writes redirected inside census_03. The old common helper wrote outside the permitted tree; the clone uses its same `srun` invocation directly. The already bound predictor is reused without a Cargo build. The historical batch script had expired from controller retrieval; the frozen job template and job accounting are retained in [code_original/greek-ocr-toolkit-sol-recut/scripts/harvest/clariden/filter_worker.sbatch](code_original/greek-ocr-toolkit-sol-recut/scripts/harvest/clariden/filter_worker.sbatch) and [census02_job.txt](census02_job.txt).

| Job | Partition | Measured elapsed | Requested time | Name |
|---|---|---|---|---|
| census_02, 3693110 | normal | 01:46:11 | 06:00:00 | ocr_filter_census |
| prepared census_03 | normal | unmeasured | 04:00:00 | ocr_filter_census03 |

Exact submit command, printed only:

```sh
ssh clariden 'sbatch /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/census03.sbatch'
```

Exact dry preflight command:

```sh
PYTHONPATH=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/prepared/87407ec7430a375f/code/87407ec7430a375f/projects/greek-ocr-toolkit-sol-recut \
/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/../venv_l1/bin/python -B -m greekocr.harvest.line_pipeline_census \
  /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/prepared/87407ec7430a375f/census_w64_pf64.json --out /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03
```

FP3: done | metadata rows bound: v2 271987 / W1 101098 / W2 219381 | ledgers wired: SF7 235257 N1 556245 RU1 19898 | numeric fix: 134 passed | config fingerprint b945ffa6 | submit: ssh clariden 'sbatch /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/census03.sbatch' | predicted ADMIT candidates: 65900

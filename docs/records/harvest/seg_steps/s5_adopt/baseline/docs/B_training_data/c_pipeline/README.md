# B — line-data pipeline 0.3

This is the organising document for creation of OCR training data: **B.a** acquires pages and Google observations; **B.b** supplies segmentation, filtering and qualified correction evidence; **B.c** binds those inputs and makes auditable row decisions; **B.d** supplies owner review sheets and returned decisions. See [Google page reads](../a_google_ocr/README.md), [sources and split custody](../a_google_ocr/SOURCES.md), [the corrected graph](pipeline.mmd) and [Clariden runbook](RUNBOOK_CLARIDEN.md).

Documentation for `cleanup/20261019`, inspected 19 October 2026. All source paths are repository-relative. This describes the **top-level implemented code**, with historical deployed bundles identified separately. Nothing was executed, trained, deployed or released by this documentation task.

## Authority and version drift

`greekocr/harvest/line_pipeline.py` declares `PIPELINE_VERSION = "0.3"`. `docs/harvest/line_pipeline/tool_versions.json` supplies named tool generations and exact component hashes/digests. Versions count documented methods, not commits or measured accuracy.

| Component | Current manifest version | Scope |
|---|---|---|
| Inventory | 0.1 | Raw text scripts, words, characters, marks, punctuation and counts |
| Content gate | **0.3** | Mixed-script DROP, unexpected-script HOLD, raw-text length/cell rules before native work |
| Segmentation | **0.9-s4** | Crop-only neighbour gate, clockwise tall-crop normalization, curved main-row measurement; all-component small-segment branch |
| Polytonic | **0.7 / SF7** | Seven named generations; saved `candidate_pre_audit` release is proposal-only |
| Cyrillic | **0.3 / RU1** | Historical Russian word-final `ь→ъ` only |
| Numerics | **0.2 / N1** | Assisted separator corrections; rejected automatic candidate remains disabled |
| Dashes | **0.1** | Tags only, no general repair release |
| Content repair | 0.2 | Independent evidence bound to exact row/content/profile |
| Composer | 0.2 | Compatible raw-parent spans, coverage and conflict checks |
| Final eligibility | **0.3** | Cell exemption matches early gate; content/confidence/codec/CTC/split checks remain |
| Census orchestration | **0.5** | Durable inventory, bounded parallel native execution, protected frozen-parent aliases |
| Codec | **v2** | `greekocr/_vendor/codec/v2.json`, NFD atoms; SHA256 `94485f72eac0aaf2324dc60b1c02110b271d362a79c440e2ce6bf6f4604997b9` |

The superseded pipeline README called segmentation 0.5 and census 0.3; its graph labelled pipeline 0.2 and segmentation 0.5. Those descriptions are retained only as dated records. This README and adjacent `pipeline.mmd` are corrected replacements; the superseded originals are preserved in `docs/records/harvest/line_pipeline_legacy/`. The JS policy file's “0.8” comment describes its unchanged three-rule functions; current native geometry and S4 orchestration in `crop-tools.py`, `line_pipeline_native.py` and `service.mjs` make the complete tool **0.9-s4**.

There are two additional integration discrepancies. The archived census03 `integration_fixes.diff` adds (1) digit/separator/digit numeric-adjacency negatives and (2) union of `final_policy.heldout_crop_sha256` into deduplication. **Both are absent from the inspected top-level code.** `automatic_result()` still uses `not any(c in text for c in ".-·")`; `Ledger.deduplicate()` protects only registered dev/test crop hashes. The archived census04 package preserves the repaired census03 code, but is a separate 0.8 deployment. Neither its results nor its external-crop protection can be attributed to the current top-level build. This document records the discrepancy and changes no code.

## Entry points and responsibility

`greekocr.harvest.line_pipeline_census` is the top-level census CLI. `line_pipeline.py` evaluates one canonical row; `line_pipeline_sources.py` adapts existing parents; `line_pipeline_adapters.py` imports earlier SF7/RU1/N1 results; `line_pipeline_native.py` obtains native evidence; `line_pipeline_parallel.py` bounds worker concurrency; `line_pipeline_runtime.py` binds the actual runtime. The Rust service in `scripts/harvest/filter_runtime/` performs frozen predictor inference; it is not a new detector or fit.

Historical `admission.evaluate`, `qualified_admission`, CP/ADMW2 and collector usable/admitted flags remain evidence for their original generations. They are not silently called as the current row-routing pipeline. The sourcing handoff parks `build_release_admission.py` and ADMW2 exports. Human review uses the existing owner-sheet contract in `docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md`; this pipeline exports evidence obligations rather than inventing reader or owner approvals.

## Frozen inputs and joins

The five recorded census parents total **592,466** rows:

| Parent | Format / initial split | Rows | SHA256 |
|---|---|---:|---|
| `collection-v2-train` | collection-v2 / train | 214,436 | `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3` |
| `collection-v2-dev` | collection-v2 / dev | 13,522 | `d462edac43e806ab87fac65860a3531cc9181d1c90a637d9e42eb45ca1940d17` |
| `collection-v2-test` | collection-v2 / test | 44,029 | `e7a4f4025adde53b8a5e7894f87bde3b12d7730e893d2f1b78dc4e78b83c00f8` |
| `collect-v3-W1-20261018-0524` | collect-v3-features / unassigned | 101,098 | `c85b407a724f4a17dfbe659cc9e2dfd171660de5e29baf1fd86b291f7cbd9c4c` |
| `collect-v3-W2-20261018-0524` | collect-v3-features / unassigned | 219,381 | `4954a94cc3c051aeb36e367101bc3448233448422bb05834d3276e090de987b4` |

The exact parent dictionaries, paths, path maps and raw-text priorities are in `docs/records/harvest/seg_census/remote_evidence/census03_config.json`. They point to **original v2**, not the O2 metadata-only v2-meta1 release. A replacement parent is a new input binding, even when label/crop tuples are unchanged.

Canonical required fields: `parent_id`, `id`, `source`, `book_id`, `edition_id`, `page_id`, `split`, `raw_text`, `crop_sha256`; raw text may be empty, other identity strings may not. Splits are train/dev/test/unassigned. Crop SHA must be 64 lowercase hex digits. Source adapters retain original fields, record `raw_text_field`, map explicit paths and join metadata crop bindings by `[parent_id,row_id]`. V2 defaults to `label`; v3 to `old_label`, then `text`, then `label`. “Raw” here means **immutable text in the selected parent**, not a claim to undo previous v2 cleaning.

For v2, `doc` is the book key; collect-v3 derives the document from `page_id` before `--s`. Missing canonical edition is marked unresolved; absent crop hashes use a zero placeholder **with unavailable status**, not a fabricated binding. Only parent-confirmed `val→dev` and `reserved→test` aliases are accepted; conflicting row/book/metadata split declarations raise an input error. Literal aliases survive in `source_split`.

Expectations resolve **page override > book declaration > existing source policy**. A declared expectation requires languages, scripts, orthography and provenance; `orthographies` can vary by script and content roles can vary by page. Page keys are compact JSON `[source,book_id,page_id]`. Reviewed profiles require `reviewed`, provenance and sample size; raw observations never train their own acceptance baseline. Metadata includes editions/splits, crops/source rasters, page overrides and optional reviewed line/page bounds.

Correction declarations bind tool, parent ID, parent-manifest SHA, artifact path/SHA and status. `released` and `candidate_pre_audit` are accepted declaration states; the latter cannot qualify an admission. Canonical `line-tool-result-v1` ledgers retain producer identities, original record hashes and original holds separately from adapter/toolchain identities. Sparse omission is not successful no-change evidence.

## Implemented stage order

### 1. Validate runtime, register and inventory every parent row

The execute path validates runtime and selected Node/predictor paths, component hashes, parent SHA and exact row counts; rehashes parents after registration; rejects duplicate parent IDs/row IDs and changed observations. SQLite stores every canonical payload and raw inventory **before filtering**. Inventories include letter/script/character counts, mixed words, numeric/mark/punctuation counts, raw codepoint count, NFC character count and raw-text SHA. Page summaries are calculated from all registered rows.

`--execute` absent returns a reporting-only `preflight` object and does **not** prove that inputs validate. `--validate-inputs-only` on the execute path performs real registration and correction indexing without native filtering; its receipt explicitly has no admission decisions. The code rejects ordinary native processing on Darwin unless an explicit test/local interface is supplied. This document ran neither path.

### 2. Content gate 0.3, before crop identity and native segmentation

Inventory and reviewed profile checks identify suspicion. A word containing letters from multiple scripts drops the entire row (`mixed_script_word`), regardless of homoglyph resemblance. If an unexpected script also occurs, retain both reasons. Without a mixed word, a script outside the expected set holds (`unexpected_script`) with script counts and offending characters. Whole words in an expected secondary script pass this part; there is no additional lookalike-only-word exclusion in current gate 0.3. Unexpected characters inside allowed scripts, minority-language anomalies and profile flags proceed as repairable suspicion after length checking.

Then apply the shared **raw-text** rule (`short_line_exclusion`):

- Rotation-free crop aspect `A=max(width,height)/min(width,height)` uses `crop_bbox`, falling back to the bound image header. Missing dimensions: `cell_status_unresolved` HOLD.
- **Cell: A≤6**, independently of role/script. More than one Unicode letter or decimal digit is sufficient for this length branch; otherwise `single_character_cell` DROP.
- For non-cells, declared `numerics_tables` or the exact numeric-text grammar is exempt from ordinary minimum letters but still needs >1 letter/digit; otherwise `numeric_shape` DROP. Grammar includes decimal/separator strings and valid uppercase Roman tokens with optional final `.`/`)`.
- Other prose needs 10 Unicode letters; `headings_caps` needs 4 (`short_line` DROP). These are policy defaults; the bound final-policy dictionary records overrides.

Early exclusions fill downstream route statuses as `not_run_due_to_prior_exclusion`; census preparation also skips native measurement/cache entries. Incomplete declared expectations hold as `expectations_unresolved`. After the gate, an unbound crop holds as `crop_identity_unresolved`.

### 3. Native segmentation 0.9-s4

Existing crop bytes must match `crop_sha256`; reconstruction is permitted only from a bound source image/SHA and frozen box with exactly matching encoded crop SHA. Verified-crop context is optional diagnostic evidence, not an additional source-availability veto.

`crop-tools.py::orient_crop` physically turns **every h>w crop 90° clockwise** before detection/measurement. Its legacy `QuarterTurn` argument is 270 under PIL's counterclockwise convention. h≤w remains horizontal; the frame/matrix is retained. Existing glyph components/font bands and the refocus path provide the crop inventory.

The accepted three rules execute in order:

1. **Other rows:** another complete row or >2 whole neighbour words drops. Cut-off groups do not count. A whole word requires letter-body evidence and **each** body ≥95% visible; a complete row uses the existing votes/body/visibility/coverage criteria. Reasons include `gate: second complete line`, `gate: too many whole neighbour words`; no main row ordinarily yields `gate: no main row found` UNCERTAIN.
2. **Output versus box:** main-row ink is measured along its existing base curve for non-small crops (S3); the unchanged predictor gives expected length. Keep `(characters+1)/(expected+1)` in inclusive **[0.5,1.5]**. Failure reasons are prefixed `length: Too little OCR output...` or `length: Too much OCR output...`; unavailable boxes/predictions are UNCERTAIN.
3. **Padding:** crop height ≤ upright box height + **1.5 × row-frame height**; equivalently combined padding/row-frame height ≤1.5. Too much padding drops; unavailable target height/padding is UNCERTAIN. There is no additional legacy tall-box veto.

**S4 branch:** `characters≤8` and crop aspect≤6 uses the axis-aligned box of **all extracted components** in the processed crop frame, including components outside a main-row assignment. Here `character_count()` counts NFC nonspace characters excluding combining marks and control-category characters; it is not a letter-only count. `service.mjs::decide()` lets the specific no-main-row abstention defer to length/padding, while retaining positive complete-line/whole-word drops. Empty components still leave the box unavailable. This definition is distinct from the gate's cell branch: cells have no ≤8-character condition. Non-small crops retain S3 behavior.

Native verdicts bind tool version, raw-text SHA and row identity; `DROP` maps to pipeline DROP, `UNCERTAIN` to HOLD, both under reason `segmentation` with native detail. Missing crop evidence is unavailable/UNCERTAIN; protocol, binding or invalid evidence errors become `INFRA_ERROR`, not scientific rejection.

### 4. Schedule every relevant corrective route

After segmentation KEEP, route polytonic Greek whenever declared orthography is neither monotonic nor modern, **including missing-mark candidates**; Cyrillic whenever present; numerics for digits; dashes for `-–—−`; content repair for residual content or reviewed-profile issues. Orthography comes from metadata, not the recognized script name.

Successful result statuses are `applied`, `verified_no_change`, and dash-only `tag_only`. Unresolved/proposal/failed records hold as `correction_unresolved`; original producer holds clear edits and remain unresolved. RU1 edits require declared Russian plus `historical_russian` and are limited to word-final `ь→ъ`. N1 edits allow only `-`/`.`→`·`. Modern declared Russian/Serbian or historical Russian without eligible final soft sign can produce explicit scope/candidate negatives. The current numeric automatic-negative is the stricter **no `.`, `-`, or `·` anywhere** condition described above; do not substitute the archived adjacency patch in this description. Dash results only tag positions; no general repair is enabled.

### 5. Validate and compose qualified raw-parent spans

Require exact parent/id/split/crop binding, raw-text SHA, tool version/digest and successful evidence. Python Unicode codepoint offsets refer to the immutable selected parent; adapters convert UTF-8 byte spans only at verified boundaries. Check every old span against that parent. Identical edits coalesce; ambiguous/overlapping edits HOLD as `conflicting_edits`, never last-writer-wins.

### 6. Re-inventory, stabilize and recheck coverage

Recompute routes after compatible edits, with at most `len(TOOLS)+1` orchestration iterations. Exhaustion holds as `routing_did_not_stabilize`. A route that already returned no change does not cover a candidate another edit introduces: raw-coordinate candidate identities and composed-text coverage bind the obligation (`candidate_scope_requires_recheck`). Reviewed final profile anomalies require an independently bound text/profile resolution; unresolved content repair holds as `content_repair_unresolved`. Apply **NFC and whitespace folding only** to the final label, recording before/after; no punctuation or diacritic folding is introduced here. Immutable parent text remains unchanged.

### 7. Split/edition integrity and final eligibility 0.3

Unassigned split or unresolved canonical edition holds as `split_or_edition_identity_unresolved`. Reuse the same raw-text length check from stage 2. For **cells**, >1 letter/digit is the only length/shape requirement: no prose `short_line`, nonletter-fraction or four-digit/60% numeric-shape gate. For **non-cell declared numeric roles**, require ≥4 decimal digits and ≥60% digits/separators (defaults); other non-cells allow at most one-third nonletters among nonspace characters (`nonletter_fraction`). An exact numeric-text exemption at the early gate does not itself change the final declared content role.

All rows retain final content checks, available mean confidence ≥0.89 (`low_confidence`), NFD codec membership (`codec_unencodable`), and held-out edition protection (`heldout_edition` for train). No independent inherited `tall_box` check runs. If supplied, CTC output steps must accommodate NFD atoms plus adjacent identical-atom repeats (`ctc_infeasible`); with `require_ctc_steps`, missing steps HOLD as `ctc_steps_unavailable`. This is an input/output contract, not a training-architecture selection. Measured final failures DROP; checks marked unresolved HOLD; otherwise row disposition is ADMIT.

### 8. Global train deduplication and evaluation retention

In deterministic parent/id order, group ADMIT train rows by exact crop SHA. A crop shared with registered dev/test drops as `heldout_crop_identity`; differing final labels for one train crop hold **all** members as `same_crop_conflicting_labels`; repeated same-label observations after the first drop as `duplicate_training_observation`, recording the retained identity. `pre_dedup_disposition` retains provenance. Top-level external held-out-crop hook is absent as noted above. Configured held-out editions and non-train registered editions still feed edition checks.

### 9. Publish a complete generation and pending obligations

`Ledger.export()` writes sorted, immutable generation files; fsyncs them; switches one `current` symlink; then publishes `CURRENT.json`. Root output aliases go through that generation. Downstream consumers must read the publication receipt and summary, not infer success from the presence of a filename.

| Output | Exact meaning |
|---|---|
| `ledger.sqlite` | WAL-backed canonical observations, raw inventory, measurement cache, correction releases/results, durable phases and decisions |
| `progress.json`, `runtime.json` | Progress/disposition counters; native attempts/reuse, unavailable/error counts, worker/prefetch settings and timing; not population accuracy |
| `decisions.jsonl` | One decision for every registered row, including explicit UNPROCESSED. **It is not a complete copy of every source row**; raw payloads live in the ledger and other exports. |
| `admission_records.jsonl` | Compatibility records: row/parent/split, pass, final label, crop SHA, source/class, pipeline version and full decision |
| `admitted_train.jsonl` | Only post-dedup ADMIT train rows, with canonical payload, final text and decision |
| `evaluation_diagnostics.jsonl` | Every **non-train** row, including unassigned, with original canonical row plus diagnostics/decision; retains the original dev/test cohorts |
| `pending_polytonic.jsonl`, `pending_cyrillic.jsonl`, `pending_numerics.jsonl`, `pending_content_repair.jsonl` | Scheduled unresolved/proposal/failed routes with raw `label`/`text`, crop/script fields, expectations, required binding and recheck obligation. There is no pending-dashes file. |
| `generations/gN-<uuid>/summary.json`, output files | Immutable generation, output hashes, phase completion and accounting |
| `CURRENT.json` | Publication status, generation/export ID, run-binding SHA and summary path/SHA; authoritative publication receipt |

Any changed decision invalidates publication before mutation and advances the generation. Census `complete` requires inventory, rows, dedup and committed export phases plus zero UNPROCESSED/INFRA_ERROR rows. A completed census may contain HOLD/DROP and proposal-only evidence; completion is not training readiness or accuracy qualification.

## Restart and worker execution

Resume checks the binding of config, parent inputs, metadata, codec, tool map, Python/assets, predictor and actual runtime. It reuses verified measurements and finished decisions. `--retry-errors` revisits infrastructure errors; `--retry-holds` revisits HOLD evidence under the same binding. New metadata/correction/split/code/runtime identities require a new ledger. Timeouts terminate the native process group; failed protocols restart the child. SQLite, composition, ordering and decisions remain on the coordinator thread.

Native workers support 1–256, prefetch 1–64, with **workers×prefetch≤4,096**. Default is 1 worker/factor2; historically qualified full settings were 64/factor64 with 256 task CPUs. The supported maximum is not a recommendation or speed result. Actual loaded libraries, binaries, compiled modules and thread settings are captured by `line_pipeline_runtime.py`.

Strict PNG reconstruction on Clariden uses private **zlib-ng 2.3.3 compatibility mode**: system zlib produced different frozen PNG bytes. `scripts/harvest/clariden/filter_worker.sbatch` verifies `runtime/png-codec.json` and preloads the hashed library; preserve strict crop witnesses and runtime identity. A codec-equivalent image is not byte-identical input.

## Census evidence so far — historical, version-specific

| Run | Recorded state and result | Evidence |
|---|---|---|
| census_01, job 3693052 | FAILED during registration on legacy val/reserved aliases; zero native decisions. Preserved failed attempt. | `docs/harvest/line_pipeline/clariden/{CENSUS_01_STATUS.md,census_01-failure-log.txt}` |
| census_02, job 3693110 | Completed historical segmentation **0.5** population: **17,036 DROP / 423,499 KEEP / 151,931 UNCERTAIN**, total 592,466. Pipeline final: **0 ADMIT / 17,036 DROP / 575,430 HOLD**. Whole job elapsed 01:46:11; six-hour request. | `segeval1/{HANDOFF.md,draw_receipt.json,cells/HANDOFF.md}` under `docs/records/harvest/collect_v3_admission/`; later census03 handoff accounting. |
| census_03, job 3695426 | **Completed**, normal, whole job 01:49:40; census step 01:49:19. Later handoff records **65,900 historical v2 train admissions**; W1/W2 still unassigned, 142,959 split-only candidates. This used segmentation 0.5 and repaired metadata/correction ledgers. | `docs/records/harvest/seg_census/remote_evidence/accounting_and_config.txt`; `docs/records/harvest/seg_census/HANDOFF_SEGCENSUS1.md` |
| census_04_seg08, package `bb1ea164338b3068` | **Deployed/verified/test-only; no submission** in final b2 receipt. 338/338 remote hashes match, three VERIFY_OK results, six smoke/full mode-i scheduler dry checks. Frozen package uses segmentation **0.8**, gate/final **0.2**, not current 0.9-s4/0.3. No real split pinned. | `docs/records/harvest/seg_census/{receipt.json,receipt_b2.json,HANDOFF_SEGCENSUS1.md,b2_evidence/remote_readback.tsv}` |

Census02 immutable export: `g1-1c775230225d4bbea5871d4fae2475da`, 8,168,706,501 bytes, SHA `568d4759257787086ee8c0780cd0d4cf633c5ebf7b355d519d6053ff8c42764a`, under `$W/filter_pipeline_20261018/attempts/census_02/census/generations/`. Its segmentation counts are **before** review exclusions. SEGEVAL's 16,736 DROP / 416,241 KEEP / 151,645 UNCERTAIN are the smaller sampling pools after exclusions, not whole-census totals.

Census03 frozen export: `g1-a21c3b465ca94eee80cb5bd34b336d69`, 8,900,374,978 bytes, SHA `b2355093affcb54e6fdcd7733212909c348c5a1971ed2de545000deece1cb98d`. Its early `remote_evidence/HANDOFF.md` says “prepared, not executed” and predicts 65,900; that timestamped prediction is superseded by later completed accounting and the package handoff. The root census02 status snapshot likewise says RUNNING because it was captured near launch; it does not override the completed export.

Census03 imports 235,257 SF7, 556,245 N1 and 19,898 RU1 canonical records, retaining scope negatives and holds. SF7's 605 raw-edit corrections remain candidate-pre-audit. W1/W2 SF7 absence never becomes no-change evidence. Metadata/protection/ledger fixes explain the historical result; **no whole-population result for the top-level 0.9-s4 + gate 0.3 build is established by these receipts**.

Clariden has three measured job kinds: **regression**, **parity**, and **census** (filter + correction import + composition/admission/dedup/export). Imported corrections are not separate reader jobs. `filter_worker.sbatch` is the earlier thin adapter with inventory/prepare/qualify/census/census-preflight modes; archived census04 separates the three bounded jobs. Follow the [runbook](RUNBOOK_CLARIDEN.md) for their different defaults and verify→smoke→full boundaries.

## Tests and interpretation

`tests/test_line_pipeline.py` covers routing order, binding, composition/UTF-8 spans, scoped negatives/holds, codec/CTC, cohort aliases, restart/generation publication and crop dedup. `tests/test_seg_small.py`, `test_seg_curve.py` and `test_seg_deskew.py` cover the named geometry changes; the S4 receipt records 1,288 fresh replay rows with 966 non-small results byte-identical to S3. Historical census04 package verification records 292 tests + 13 subtests and 150+888 verdict/reason parity for **its 0.8 build**. These are saved evidence, not tests rerun here or population accuracy claims. The frozen 888-row parity cannot qualify a changed policy simply by being repeated as a historical number.

## Sources read

- `docs/cleanup_20261019/{OWNER_BRIEF.md,PLAN.md}`; `AGENTS.md`; relevant entries in `docs/cleanup_20261019/inventory/INVENTORY_BRANCHES.md`.
- `greekocr/harvest/{line_pipeline,line_pipeline_sources,line_pipeline_census,line_pipeline_native}.py`.
- `greekocr/harvest/{line_pipeline_adapters,line_pipeline_parallel,line_pipeline_runtime}.py`.
- `greekocr/harvest/filtering_assets/{crop-tools.py,segmentation-policy.js,service.mjs}`.
- `docs/harvest/line_pipeline/{README.md,pipeline.mmd,tool_versions.json}`; `greekocr/_vendor/codec/v2.json` (codec identity).
- `scripts/harvest/clariden/filter_worker.sbatch`; `docs/records/harvest/seg_census/jobs/{common.sh,regression.sbatch,parity.sbatch,census.sbatch}`.
- `docs/records/harvest/seg_census/{JOB_KINDS.md,HANDOFF_SEGCENSUS1.md,FOLLOW_UP.md,receipt.json,OUT_OF_GIT_RECEIPT.md}`.
- `docs/records/harvest/seg_census/remote_evidence/{HANDOFF.md,census03_config.json,accounting_and_config.txt,runtime.json,integration_fixes.diff}`.
- `docs/harvest/line_pipeline/clariden/{CENSUS_02_STATUS.md,census_02-status.json}`.
- `docs/records/harvest/collect_v3_admission/segeval1/{HANDOFF.md,draw_receipt.json,cells/HANDOFF.md}`.
- `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census04.py`.
- `docs/records/harvest/collect_v3_admission/{HANDOFF_20261018_sourcing.md,split1/SPLIT_PROPOSAL.md}`.
- `docs/records/harvest/seg_steps/s4/{REPORT.md,receipt.json,summary.json}`; `docs/records/harvest/seg_steps/gate_rereport/summary.json`.
- `tests/test_line_pipeline.py` (test contracts); `docs/records/harvest/oa_rebind_v1/o2/RELEASE_NOTE.md`.

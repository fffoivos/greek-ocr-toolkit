# Line filtering pipeline 0.3

This is the implementation of the agreed row-routing graph. It reuses the existing text inventory, source policies, native crop/font guides, source-context word tools, SF7, RU1 and N1 result formats. It does not redesign segmentation, choose training experiments, launch readers or start a census.

The owner accepted the current segmentation policy as-is on 18 October 2026. Its code is frozen byte-for-byte; the 888 saved decisions and reasons are identical through the new service. Previous counterexamples remain evidence, but improving that policy is outside this implementation task.

## Versions

| Tool | Version | Counted iterations |
|---|---|---|
| Polytonic | 0.7 | Seven named S1–SF7 method generations |
| Historical Cyrillic | 0.3 | RU1 v1, v2 and v3 |
| Numeric separators | 0.2 | Rejected automatic ink candidate, then assisted reader/pixel method |
| Dashes | 0.1 | Existing tag-only method; no general repair enabled |
| Segmentation | 0.5 | Five recorded policy checkpoints ending at padding 1.5 |
| Inventory | 0.1 | First integrated graph implementation |
| Content gate | 0.3 | Owner gate: mixed-script word drops, unexpected script holds, before segmentation |
| Content-repair interface, composer, final eligibility | 0.2 each | Initial implementation, then Astra integration fixes |
| Census execution | 0.3 | Initial implementation, Astra fixes, bounded parallel native workers |

`tool_versions.json` records the named iterations, component hashes, scope and aggregate tool digest. These count documented method generations, not every individual edit or commit. Unknown historical patch rounds are not invented. Existing release names such as `sf7-rc1` and `ru1_v3_edits` remain intact alongside the new tool versions. Run `python scripts/harvest/build_filter_versions.py` only when intentionally issuing a new exact build; it fingerprints the working files and existing artifacts.

## Executed sequence

1. Register and inventory every input row before any filter. Retain its immutable raw text, crop hash, source/book/page, edition and split in SQLite.
2. Resolve declared page overrides, book expectations or existing source policies. Check unexpected scripts/characters, mixed-script words and frozen reviewed profiles. Content gate 0.3 drops any mixed-script word immediately (also retaining any unexpected-script reason), otherwise holds unexpected scripts with inventory counts and offending characters. These exclusions precede crop-identity checking and segmentation, skip every tool, and skip native census measurement/cache entry. Unexpected characters within expected scripts, frozen profile anomalies and unexpected-language handling remain repairable as before; they proceed to segmentation and evidence-backed repair without early length rules.
3. Apply segmentation 0.5 before correction. Its accepted thresholds, orientation handling, component envelopes, refocus and neighbouring-word reconciliation are unchanged. The former home-server dependency is removed; the existing ownership/magnitude helpers are included unchanged in the package.
4. Schedule every relevant corrective, including polytonic expectations even when marks are absent, Cyrillic spans with orthography eligibility, numeric spans and dash tags. An absent sparse-overlay record is not a no-change verdict.
5. Validate every result against parent, split, crop, raw-text hash, tool version and implementation digest. Combine compatible raw-parent spans, coalesce identical edits and hold conflicting overlaps. UTF-8 byte patches are converted only at verified character boundaries.
6. Re-inventory the merged label and schedule newly relevant routes until stable. Recheck candidate coverage for tools that already ran: a prior no-change result cannot cover a candidate introduced by another correction. Candidate identity uses immutable raw-coordinate anchors; unresolved composed candidates generate explicit recheck obligations. Recheck reviewed profiles on the final label and require any independent anomaly resolution to bind its text and profile scope. Resolve original character/script suspicion from the qualified edits and final checks. Unresolved required evidence excludes the row.
7. Apply content-role-specific length/shape, confidence and codec checks to the final label. Numeric role remains independent of `script_class=nonletter`. No inherited tall-box rule runs. CTC length is checked when the downstream contract supplies output steps; `require_ctc_steps` makes missing steps an explicit hold. This data-interface option does not select a training architecture.
8. Enforce held-out edition/crop protection and exact-crop duplicate/conflicting-label rules, then export all dispositions, retained train rows, unchanged evaluation cohorts, pending corrective queues and attrition accounting.

The current new entry point is `greekocr.harvest.line_pipeline_census`. Historical `admission.evaluate`, `qualified_admission` and their replay files remain available for historical consumers; they are not silently called by this pipeline. New filtered releases must use the new entry point and its exports.

## Input configuration

The CLI defaults to a no-processing preflight:

```sh
python -m greekocr.harvest.line_pipeline_census config.json --out /worker/filter-run
```

On the authorized worker:

```sh
cargo build --release --offline --manifest-path scripts/harvest/filter_runtime/Cargo.toml
python -m greekocr.harvest.line_pipeline_census config.json --out /worker/filter-run --execute
```

Example configuration structure (replace the explicit input bindings with frozen worker manifests):

```json
{
  "versions": "/worker/toolkit/docs/harvest/line_pipeline/tool_versions.json",
  "metadata": "/worker/frozen-book-page-metadata.json",
  "codec": "/worker/toolkit/greekocr/_vendor/codec/v2.json",
  "predictor": "/worker/toolkit/scripts/harvest/filter_runtime/target/release/greekocr-frozen-font-predict",
  "runtime_manifest": "/worker/frozen-native-runtime.json",
  "native_workers": 8,
  "row_timeout_seconds": 120,
  "component_roots": {
    "greek-ocr-toolkit-sol-recut": "/worker/toolkit",
    "greek-ocr-toolkit-spellcheck": "/worker/spellcheck",
    "greek-ocr-toolkit-secondary": "/worker/secondary"
  },
  "parents": [
    {
      "id": "frozen-W1-20261018-0524",
      "format": "collect-v3-features",
      "path": "/worker/W1_features_20261018_0524.jsonl",
      "sha256": "c85b407a724f4a17dfbe659cc9e2dfd171660de5e29baf1fd86b291f7cbd9c4c",
      "rows": 101098,
      "path_map": {"/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data": "/worker/collect-v3-data"}
    }
  ],
  "final_policy": {"require_ctc_steps": false},
  "corrections": []
}
```

Include all selected old and new parents, with their own exact hashes/counts. `collection-v2` is the adapter for the existing import rows; `collect-v3-features` preserves the saved population's raw-text priority (`old_label`, then `text`, then `label`). A canonical adapter is also supported. No size, character-count or historical-admission flag prefilters the input.

Book/page metadata separates expected languages/scripts from observed inventory. Book entries require `languages`, `scripts`, `orthography` and `provenance`; `orthographies` can declare different regimes for Greek and Cyrillic in the same book. Book entries can also supply canonical `edition_id`, split and content role. Page overrides use the JSON key `[source, book_id, page_id]`. Row split/crop manifests use `[parent_id, row_id]` keys. Unknown splits or canonical editions remain explicit holds, rather than being guessed as train; old crops without recorded hashes remain unbound until their crop manifest is supplied.

Reviewed `profiles` support line-level bounds and aggregate page bounds such as numeric-line fraction, line count, digits and letters. They require review provenance and sample size. Current observations supply descriptions and anomaly candidates; they never promote themselves into a trusted reference profile.

## Existing corrective outputs

Each correction artifact configuration names `tool`, `parent_id`, `parent_manifest_sha256`, `path`, `sha256` and `status`. Accepted statuses are `released` and `candidate_pre_audit`; candidates are proposal-only and cannot qualify a row. A `format` of `line-tool-result-v1` consumes full coverage results; otherwise the existing SF7/RU1/N1 formats are adapted. Producer policy/job/variant identities and the original record hash remain separate from the adapter version and toolchain digest; optional manifest-declared producer fields must match. Canonical imports use the bound ID, require registered parent membership, and enforce the same RU1/N1 edit scopes. Tag-only success is reserved for dashes. Original holds survive the adapter, including partial rows that also have some agreed edits.

No missing sparse record is upgraded to a successful no-change. Full results can state `applied`, `verified_no_change`, `tag_only`, `proposal_only`, `required_evidence_unresolved` or `failed`, with bound evidence. Dashes are tag-only. Exact candidate-negative numeric scans and declared out-of-scope modern RU1 regimes can produce explicit no-change evidence without a reader; separator ambiguity and unknown historical regimes cannot.

`pending_polytonic.jsonl`, `pending_cyrillic.jsonl`, `pending_numerics.jsonl` and `pending_content_repair.jsonl` contain the unresolved scheduled rows. They include compatible `id`, raw `label`/`text`, crop and script fields plus the required observation binding and expectations. Use the existing reader/pack/finalization workflows on these queues; import their complete result ledger through a newly fingerprinted run configuration. This implementation does not pretend that exported pending queues are completed inference.

The saved SF7 release is still candidate-pre-audit and W2 corrective coverage has not been run. This owner decision accepts segmentation only; it does not falsely record the unrelated SF7 audit as passed. Those are remote execution/evidence tasks after access is restored, not hidden automatic approvals.

## Restart and outputs

`ledger.sqlite` uses WAL and durable transactions. The binding covers inputs, metadata, codec, tool versions, predictor binary and Python/assets source. Resume refuses drift. Already completed rows and verified native measurements are reused; timeouts terminate the native process group. `--retry-errors` retries infrastructure failures; `--retry-holds` can retry missing crop evidence after the expected bytes become available. Changed correction/metadata manifests require a separate run ledger, preserving the old decisions.

`progress.json` records live registration/filtering progress. `summary.json` reconciles admitted, dropped, held and incomplete rows; separates unavailable geometry from measured decisions; includes source/class/script/split breakdowns and overlapping failure counts. Completion means census accounting is complete, not that all rows are admissible or that population accuracy was measured.

Exports are atomic, fingerprinted files:

- `decisions.jsonl`: every original row and its disposition, including unprocessed rows.
- `admission_records.jsonl`: row-level compatibility records, final labels and full decisions.
- `admitted_train.jsonl`: only eligible, deduplicated train rows.
- `evaluation_diagnostics.jsonl`: every original dev/test row with diagnostics; no silent cohort deletion.
- Pending tool queues: required evidence that remains unresolved.

## Verification and remaining execution

Local verification uses tiny metadata fixtures and saved evidence only. It covers ordering, multi-tool composition, Unicode/UTF-8 boundaries, no-change/hold distinction, source adapters, crash/resume, timeouts, stale bindings, numeric roles, leakage and duplicates. The new Rust service is inference-only with the original frozen coefficients; no fit or threshold was changed. It reproduces all 888 saved predictions with maximum absolute difference `1.4210854715202004e-13`, and the frozen JS policy reproduces all 888 saved verdicts and reasons exactly.

No full dataset was transformed and no new native crop was processed during implementation checks. Before operational use, bind the complete worker inputs/crops/metadata, perform a bounded worker smoke of the native adapter, complete applicable reader/audit coverage, and run the diagnostic census. Do not present the current selected 888-row outcomes as a population retention or accuracy estimate.


## Durable publication and progress

`CURRENT.json` is the authoritative publication receipt. A changed decision invalidates it before the database mutation, increments the generation, and disconnects the previous `current` alias. Inventory, row evaluation, deduplication and export completion are distinct durable phases. `complete` requires all phases for the active generation, a matching committed publication, and no unprocessed or infrastructure-error rows. A completed diagnostic census can contain excluded HOLD rows; it does not imply training release readiness.

Each export writes an immutable `generations/gN-<id>/` directory, hashes every output, then switches one `current` symlink and commits the publication receipt. Root output aliases all resolve through that same generation. Interrupted exports cannot be reported as complete; resume retains previous generations for inspection. Every decision carries a run fingerprint plus the complete toolchain version map/digest, including applicable negative results and early exclusions.

Progress updates use maintained disposition counters; they do not repeatedly decode all previous decisions. Full reasons/routes/stratum aggregation is reserved for final reporting. Page inventories are computed from all registered raw lines and cached without learning an acceptance baseline. Native requests and responses share one hard deadline, including partial responses; protocol failure terminates the process group and the next request starts a fresh worker.


## CSCS native-worker concurrency

`native_workers` defaults to 1 and accepts 1–256. Only native measurements run concurrently, each through an independent persistent, deadline-limited process. All SQLite access, correction composition, output ordering and release decisions stay in the coordinator. `native_prefetch_factor` accepts 1–64 and defaults to 2; worker count times factor must not exceed 4,096 pending observations. Both the pool and qualification planner reject oversized combinations before starting workers. This permits a wider queue with fewer native processes without increasing the global observation bound. Missing-boundary/expectation rows are excluded before native work; verified measurements are reused on resume. Worker failures remain infrastructure errors, and unavailable crops remain explicit holds. `runtime.json` records attempts, reuse and timing separately from the scientific decisions. Select deployment settings only from a fresh worker-side equality, throughput and memory comparison; the maximum supported worker count is not a recommended setting.

Use the same bound parents, metadata, versions and binary for worker-count comparisons. Output decision equality excludes the run-binding fingerprint, which intentionally changes when the worker-count configuration changes. No local or remote speedup is claimed before a same-input native comparison. Full native and timing qualification runs only on a Slurm worker; the Mac runs metadata fixtures only.

Native execution requires a runtime manifest. It records the actual loaded PNG/JPEG libraries, explicit preload and library hashes, compiled Python modules, package versions, Python/Node/predictor binaries and child-thread settings. Both the coordinator (including cached resumes) and actual native child validate the selected executable paths and loaded runtime before use. The manifest fingerprint enters run identity and measurement keys. A change requires a new ledger; never edit an existing manifest to conceal drift.

On Clariden the original collector's grayscale PNG encoding requires the private zlib-ng 2.3.3 compatibility library. The system zlib produced different frozen crop bytes; accepting those differences would violate the input identity contract. `filter_worker.sbatch` verifies the private library SHA before preloading it. Four crop witnesses, followed by all selected native qualification rows, must retain their strict frozen SHA checks. `png-codec.json` describes the installed library, while each run's runtime manifest binds what Python actually loads.

The thin Clariden adapter reuses the existing Greek OCR `common.sh` allocation/receipt helper. Its modes are `inventory`, `prepare`, `qualify` and `census`. `prepare` verifies every referenced source page, binds every original-v2 crop path/hash without rewriting original parent manifests, and emits a fingerprinted full diagnostic configuration with existing correction releases. Missing assets stop preparation. The original train/dev/test split manifests remain declared; new split and edition identities are not guessed. `qualify --stratified` selects deterministic SHA-priority samples across complete parents and compares fresh serial/parallel runs. `census --config <prepared/config.json>` executes the bound full diagnostic pipeline. This census still excludes unresolved corrective/audit/metadata evidence; it is not an unconditional training release.

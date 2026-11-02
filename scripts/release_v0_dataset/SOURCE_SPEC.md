# Explicit source selections for the REL0-S4b CPU builder

The spec is ordinary JSON, frozen with `--freeze SPEC --lock-out LOCK`. Paths in
`patterns`/`assets`/feature inputs can be relative to the spec. Pattern order
is pool order; files within each pattern sort lexically. Overlapping patterns
and missing matches fail. Generic page/synthetic assets still use the locked
asset selector. Original line crops use the REL0-S4t custody rule below.

Freeze also pins each `original_crops_source` parquet payload input with its
bytes and SHA256, separately from native metadata. Harvest payloads are joined
by the exact original tuple and recorded crop hash; parquet order and filenames
supply no identity, and native labels/provenance remain intact.

Each declared `crop_roots` entry gets an `index` with `files` and `sha256`.
The digest hashes UTF-8 canonical JSON `[sha256, absolute_path]` lines, each
terminated by a newline, sorted by SHA256 then path. This indexes regular files
with the same `FileChecks.build` implementation as S4r. Builder ingestion and
independent acceptance rebuild it from source bytes, including on resume;
a changed/missing root or digest/count fails. Each index-selected payload is
read and re-hashed before embedding. No builder index database is trusted by
acceptance.

An original line's recorded `crop_path`, `crop_relative_path`, `file_name` or
`image_path` is read directly. Relative paths require an absolute `image_root`
and `image_root_evidence` in that input's spec entry; no cwd or guessed root is
used. The v4 root is `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`, with the
hash-bound `V4_HANDOFF.md` release-acceptance paragraph recorded in the spec.
Original bytes are embedded only when they match the row's recorded crop hash.
An embedded original from a real source also requires its recorded hash.
`original_crop_custody` in `record_json` retains the recorded/resolved locator,
recorded/measured hash, dimensions, reason and any exact S1/v4 mapping.
`original_custody` is published per row as `recorded_path`, `index` or
`embedded_original` (null for an unavailable original). Index-only custody
requires recorded-hash membership in a declared root and measured byte equality;
it does not require a historical recorded path.
Missing originals stay null with `missing_file`, `hash_mismatch` or
`no_recorded_path`; `COVERAGE.json.original_crops.populations` counts rows,
recorded paths, existing files, matches, mappings and reasons. Unknown original
dimensions stay null. Original and trainer bytes may be identical only after
the original source has independently passed recorded-hash verification.

`assets.original_crops` is partial overall with a complete measured denominator.
S4r custody is resolved for harvest 497,556/497,556; S1 364,871/364,871;
v4 167,946/167,946; old 364,173/364,173; seal04 2,690/2,690; and validation
13,088/13,088. Census is partial: 483,078/592,466 covered, with 109,388
`no_recorded_path` (no matching crop under any declared root). These overlapping
source populations must not be summed as distinct release rows. The spec has
no pending resolver decisions. Builder and acceptor retain exact original
custody requirements and reasoned nulls. `COVERAGE.json.original_crops.published_images`
counts the actual public images for each frozen source population, including
overlap, and must equal its frozen `custody_established` measurement in full.
Smoke independently checks its selected source observations against public image
hashes and records partner observations outside the selected row sample as
`unselected`; missing selected census/S1/v4/harvest rows always fail. Census-only
and v4 admission rows receive an explicit release label so verified originals
reach the public `real` view without changing decisions or split evidence.
Fresh production execution/readback remains coordinator work; see GAPS.md.

Prepared payloads remain exact factory bytes in `trainer_image` and
`training_image_sha256`. Every row with nonempty `trained_in` requires both.
A smoke selects the first prepared shard and a bounded prefix: `split=train`
alone is a dataset assignment and does not mean a selected trainer membership.
A sampled train row can therefore have neither trainer field and empty
`trained_in`. The full build reads every prepared shard and enforces the
trained-row requirement. It never fills `image` from a prepared payload.

Top-level required fields:

```json
{
  "dataset_version": "v0.1",
  "hf_pins": {
    "staging-v4": "8ee9cb2e4c880f450c69b9c45cd683765d4da755",
    "harvest-20261025": "103c6dcd1e5dac6d72a1048462cd5b1864600cca"
  },
  "models": ["<v0 model id x1>", "<v0 model id x1.5>", "<v0 model id x2>"],
  "features": {"codec": "/pinned/codec-v2.json", "scripts": "/pinned/Scripts-14.0.0.txt", "unicode_version": "14.0.0"},
  "assets": ["/pinned/original-crops/**/*.png", "/pinned/source-crops.tar"],
  "inputs": [],
  "keyset_unions": {
    "old": ["old0", "old1"],
    "prepared_all_harvest": ["prepared_train_harvest", "prepared_dev_harvest", "prepared_test_harvest"]
  },
  "reconciliations": [
    {"name": "s1_old", "left": "s1", "right": "old", "left_only": 698, "right_only": 0},
    {"name": "s1_retained", "left": "s1", "right": "prepared_train_v4", "left_only": 1, "right_only": 0},
    {"name": "harvest_archive", "left": "harvest", "right": "hf_harvest", "left_only": 0, "right_only": 0},
    {"name": "harvest_retained", "left": "harvest", "right": "prepared_all_harvest", "left_only": 2, "right_only": 0}
  ],
  "expected_counts": [{"name": "v4 additions", "table": "label_versions", "where": {"label_variant": "v4_admission"}, "count": 167946}],
  "component_versions": {},
  "release_code_commit": null,
  "run_bindings": {},
  "probe_receipts": [],
  "smoke_rows_per_source": 512
}
```

Angle-bracket values and `/pinned` examples are **not executable production
bindings**. Substitute the actual reviewed model ids/version/component versions,
source paths and source/run receipts. `run_bindings` maps each model id to its
recorded SHA; unavailable final records stay null, never an expected CLAIM
presented as an executed one. `probe_receipts` and `release_code_commit` retain
their explicit identity/status. Optional `estimates.bytes_per_table` and
`estimates.aggregate_mb_per_cpu_second` replace the stated planning assumptions
with measured values. Spec selections, including all original assets, get full
bytes/SHA256 records in the resulting lock.

Every input has unique `name`, `adapter`, `patterns`. Optional `fields` maps
destination names to dotted source paths (including JSON-in-string paths);
`constants` supplies only inspected declarations; `templates` creates explicitly
declared identity strings from fields. `json_prefix` and `json_map` are the same
explicit streaming selectors as the probes. `columns` is optional Parquet
projection; payload-bearing sources must include their image column. Public
schemas never inherit source schema metadata. Every non-binary, non-private,
non-removed source field survives in `record_json`, even if it is not a typed
top-level column. Raw Google responses stay private; project their agreed parsed
fields from `raw_segmenter_json` using `fields` before that raw field is removed.

Inputs sort by priority then name: evidence 0, census 10, original rows 20,
S1/harvest 30, A12 40, relation tables/patches 50, prepared005 60. Override
`priority` for an inspected dependency. In particular load harvest decisions
before their release metadata, aliases/tuple bridges before prepared sources,
and supporting page tables before `row_patch` records which use those tables.

| Adapter | Required identity and behavior |
| --- | --- |
| `census` | Native g2 `binding.parent_id,binding.id,binding.split,binding.crop_sha256,disposition,reasons,final_text,routes,edits`; all 592,466 original tuples. Also writes sanitized complete decisions. Generation defaults to the pinned g2 id, may be stated explicitly. |
| `row` | Original `parent_id,row_id`; explicitly map the raw/corrected text and geometry/custody fields. `label_variant`/`producer_version` qualify every label. Use `trainer_alias:true` only where that original id is proven to be the trainer id. |
| `s1` | Native `ref_364871.jsonl`: original tuple, `label,crop_path,crop_sha256`; release v4; `keyset:s1`. It creates the verified original-id → row-key bridge. |
| `harvest` | Native `wave,id` release identity, plus book/page/crop/source fields. Original parent is retained when supplied; otherwise parent is explicitly the **release wave namespace**, with an `identity_origin` reason. Trainer id is exactly `harvest:<wave>:<id>`. Use `keyset:harvest` only for root metadata; load all decisions separately with `fields` for `text:final_text,decision:disposition,decision_reasons:reasons`, `record_decision:true` and a distinct label variant. |
| `keyset` | `keyset` plus `key_field`, no image reads needed. Old pools select `line_id` as `old0`/`old1`; HF harvest metadata uses an explicit `templates.line_id=harvest:{wave}:{id}` then `key_field:line_id,keyset:hf_harvest`. Do not strip wave namespaces. |
| `table` | `table` in PLAN's supporting relations. Explicitly project IDs/FKs from real source keys. Standard keys are in build_dataset.DEFAULT_KEYS; optional `keys` must preserve that table's logical identity. `page_images` copies `image_bytes`/`image_png`/HF image structs. |
| `row_patch` | Exact original tuple or an already-proven `trainer_line_id`/`line_id` resolves the row. Supply inspected parent/book/page/box/edition/source metadata. Conflicting identity/split/crop fields fail. No crop-hash or text join is inferred. |
| `synthetic` | Exact A12 shard, `factory_build_id,source_build,build_evidence`; all train/val/reserved. Native image_png/codec/font/origin/ordered operation columns are preserved. |
| `prepared` | Actual prepared005 shard; `pool,role` (`train/dev/test/reference`), optional `variant` (default prepared005), `keyset` prefix for real pools. Consumed byte/label/codec variant and pool order are retained per model. For synthetic add `synthetic:true,factory_build_id` and prove exact A12 equality. |
| `evidence` | Small (<32 MB) JSON object, sanitized into synthetic/BUILD with original SHA/path. Include A12 build_info, all retained recipe/codec/font/source/job manifests and the probe OP_IMPLEMENTATIONS. Large maps require a selected table/keyset source instead. |
| `decision` | Additional complete sanitized decision stream with file/ordinal identity; keeps duplicate historical observations as separate evidence records. |

Real sources can add `keyset`, optionally `keyset_key` (e.g. `row_key` for an
original-tuple set) and `keyset_where` for a literal equality selection. For the
inherited seven-key comparison, select the census's original `disposition=ADMIT`
and `binding.split=train` into a separate set; reconcile it with the old union
without confusing it with S1's 698 additions. Select the 167,946 v4 admissions
and 904 sf7 overlay records as independent label versions, retaining parent tuple,
producer versions, original text/hash and correction provenance. Use
`select_label:false` when a historical overlay is retained without replacing the
chosen convenience-view label. Those are source selections, not re-filtering.

Prepared real inputs use `keyset:prepared_train` for both train pools,
`prepared_dev` for harvest_dev and `prepared_test` for harvest_test; the adapter
adds `_v4` or `_harvest` based on the **intact** trainer id. Preserve each role
as its own source selection, including seal04 dev/test and validation. Split
metadata is not inferred from the factory `reserved` directory. Source and
trainer labels and images remain separate.

For the actual A12 inputs:

```json
[
  {"name":"a12_build","adapter":"evidence","patterns":["/capstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/mix1_runs/MIX1D-8d25940f-export-001/prep/A12/build_info.json"]},
  {"name":"a12","adapter":"synthetic","patterns":["/capstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/mix1_runs/MIX1D-8d25940f-export-001/prep/A12/*/*.parquet"],"factory_build_id":"A12@e81aa95bdc32113b398f16ebe9741782fc875a50eb3de6b75522b8183f258271","source_build":"/capstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/mix1_runs/MIX1D-8d25940f-export-001/prep/A12","build_evidence":"a12_build","recipe_name":"A12"}
]
```

The first evidence SHA must be
`e81aa95bdc32113b398f16ebe9741782fc875a50eb3de6b75522b8183f258271`.
Freezing binds observed file hashes; inspect them against the supplied probe
receipt rather than assuming a matching directory name proves the build.
Keep old_synth selections/build ids separate; production acceptance expects the
203,693 A12 rows, not a concatenation by recipe name.

Typed relational joins are optional but useful when foreign keys live in
different pinned tables. Example (only when these exact typed columns exist):

```json
{"joins":[{"name":"box-page","target":"boxes","source":"pages",
 "on":{"source_object_id":"source_object_id","raw_page_index":"raw_page_index"},
 "fields":{"page_id":"page_id"}}]}
```

Joins index their exact columns on disk, require one source match and reject
conflicting replacements. An explicit `nullable_reason` retains an unresolved
finding; it cannot make an unresolved **trained** row pass acceptance. Preserve
source coordinate frames, supplied transforms and raster mapping status; matching
dimensions/SHA never authorizes a native-frame transform. Map all page acquisition
and per-run outcomes, including failed/excluded/no-raster and zero/error/not_run.
Map page aliases, response representations, segmenter runs, contributor/crop/
release memberships into their containing relation records as in CROSSWALK.

Publication locators are portable config-index/key/field records under
`manifests/CONFIGS.json`; absolute source shard/ordinal paths are explicitly
historical, not advertised as publicly fetchable raw Google payloads. Include
source item/catalogue/manifest URLs, edition/volume, page convention and sanitized
source records when retained. Nulls have reasons; don't fill bibliography from
an id pattern.

Full input validation requires all supporting relation selections (including
reference and row-instrument sources), full archive pins, three model ids, explicit
count checks and keyed reconciliations. The acceptance script additionally fixes
the release population/pool counts from PLAN and the 28 October probes; a spec
cannot weaken them by changing `expected_counts`. Missing source/geometry/reference
bindings must be resolved from pinned evidence by the coordinator or remain a
release-blocking finding. This task neither fabricates those bindings nor runs
the missing remote probes.

## REL0-S4k synthetic observation identity (28 October 2026)

The synthetic primary key is `(factory_build_id, split, source_shard,
source_ordinal)`. `source_shard` is the complete locked input file path (never
just a basename); `source_ordinal` is the zero-based row position in that file.
`synthetic_key` is the canonical JSON serialization of this tuple. The lock
binds each file's bytes/SHA256. This native position distinguishes every input
observation, even byte-identical rows, without assuming anything about
`line_id`, `reuse_index`, image hashes or rendering metadata. Rewriting or
repacking inputs requires a new lock/key binding. Overlapping selections of the
same native position fail explicitly. No synthetic rows are deduplicated.
The existing expected counts remain 190,486 train, 9,208 val and 3,999 reserved.

`line_id` and `reuse_index` remain source attributes. `key_collision_group` is
SHA256 of canonical JSON `[factory_build_id,line_id,reuse_index]` for a repeated
legacy key, and null for a singleton; `key_collision_size` counts all members
across splits. `COVERAGE.json.synthetic_identity` reports per-split and global
collision rows/groups, plus groups with identical versus differing public native
observations. A differing group may also contain identical subsets. These are
measurements of rows actually ingested; smoke counts are explicitly bounded.
The coordinator's population measurements are recorded in GAPS.md, not inserted
as measured output of a local fixture build.

Synthetic `training_membership` rows have distinct `membership_id` values from
SHA256 of canonical JSON `['prepared-position-v1',model_id,role,pool,variant,
factory_build_id,source_shard,source_ordinal]`. All memberships now use
`membership_id` as their primary key; real membership IDs retain their previous
hash of `[model_id,role,pool,trainer_line_id,variant]`.

Prepared-to-A12 matching compares the exact image SHA256 and every public native
attribute named by `common.SYNTHETIC_MATCH_FIELDS`, including split, native width,
labels/codec, line/reuse IDs and render/origin metadata. The comparison attributes
are retained in `synthetic_native_attributes_json`; licence fields stay removed
under the existing release policy. `synthetic_match_group` hashes canonical JSON
`[factory_build_id,image_sha256,native_attributes]` in both populations. The
independent acceptor replays these attributes and both positional identities.

A single candidate yields `synthetic_key`, `synthetic_candidate_count=1` and
`synthetic_mapping_status=unique_exact`. Multiple indistinguishable candidates
yield a null `synthetic_key`, their exact candidate count and
`synthetic_mapping_status=ambiguous_identical_observations`: join every candidate
on `synthetic_match_group`. No arbitrary occurrence allocation or historical
one-to-one pairing is asserted. Each prepared position remains a separate
membership. Per-model/role/pool/variant `unique_exact_rows`, `ambiguous_rows` and
`ambiguous_groups` are reported in COVERAGE. Individual `trained_in` is assigned
to an ambiguous group only when its entire native multiplicity was consumed.
Full builds require the prepared train multiset to equal all A12 train
observations; missing/extra occurrences fail with counts. No exact candidate
fails with its prepared source locator. Smoke may sample only a subset and does
not certify population uniqueness or the full train multiset.

The real prepared005/A12 ambiguity count is **unmeasured in this local change**:
no source scan, SSH or network was performed. A complete build will report it;
the reported four byte-identical val collision groups do not establish train
membership ambiguity. Never substitute the legacy-key collision count for the
number of indistinguishable prepared-to-A12 matches.

### Materialized real splits (REL0-S4m)

S1 has no native `split`. After the explicit joins/book bridge and prepared
membership ingestion, derivation writes `split`, `split_reason` and
`split_resolution_json` on every row, before either the `rows` table or `real`
view is exported. The original row assignment is retained as `source_split`
(including an explicit null). A resolved pinned book assignment supplies a
missing native split; a conflicting resolved native assignment fails. A pinned
book with an unresolved assignment yields `unknown`, retaining its registry
split and unassigned reason. Without a registry assignment, an explicit native
assignment is retained; otherwise exactly one prepared train/dev/test role can
resolve it. Reference membership does not assign a split. Missing or conflicting
role evidence yields `unknown` with a reason. Prepared factory `reserved` is
never interpreted as a dev/test assignment.

Export no longer substitutes a partition name for an absent row field. The
acceptor rejects missing/null splits, reasonless unknowns, registry conflicts
and disagreement between the real view and row table. CLI failures include the
complete chained traceback as absolute `file:line` frames, as well as source,
adapter and key; unexpected consumer lookups retain the yielded row's context.
S4l smoke packages with missing row splits require a fresh build with this code
and new out/work directories; rerunning acceptance or resuming the old code
binding does not repair them.

### REL0-S4s measured original crop decision

The complete S4r report in `out/RELEASE_v0/probes/original-crops-s4r-001/`
(code `rel0-s4r-20261029`) scanned 2,274,777 records over eight sources.
The spec binds the report SHA256 and retains its exact per-population coverage,
complete content index (506,974 files, 501,236 distinct hashes), per-root counts,
and validation join evidence. The six fully covered populations are resolved;
census alone is partial with the counts stated above. There are no remaining
pending resolver entries in the machine spec.

The publication contract is `image` = verified original bytes for every covered
row; the 109,388 uncovered census observations require a null image with
`no_recorded_path`. Width, height and aspect come from that verified image and
remain null when it is absent. `COVERAGE.json.original_crops.measured_probe`
and the card's Images paragraph report the complete source measurement;
`original_crops.populations` reports actual build observations separately.
An honest measurement does not certify an unexecuted production build. See
GAPS.md for the existing builder/index and harvest-input integration gaps;
S4s does not repair them.

### REL0-S4r declared crop roots and exact validation evidence

S4r supersedes S4q's census-first restriction for image custody. The spec declares
only `collection_v2/crops`, `collection_w1_originals`, `collection_w2_originals`
and `benchmark_0.2/seal04/images`, each with its evidence. The `original_crops`
resolver hashes every regular file under those roots once per resolved path in
the fresh `crop-files.sqlite`, including overlapping-root reuse. Symlinks are
not followed. `content_index.index_size` counts distinct measured SHA256 values;
`files` counts distinct paths; each root reports files, unique hashes, errors
and completion. Recorded hash membership establishes custody without creating
a row identity. A stale path can resolve by hash; a readable but different path
is retained as a `recorded_path_mismatch` diagnostic. Filenames and path
rewriting supply no identity.

Seal04 explicitly selects both crop/image hashes and paths. Relative paths
resolve against the directory of the actual panel JSONL, independently for
each selected file. Conflicting recorded crop/image hashes remain unresolved.

`validation_originals` selects `collection_v2/admitted_all_v2.jsonl` (271,987
coordinator-reported rows). Freeze pins its complete file bytes/SHA256; the
resolver records the input SHA256 before scanning. Prepared validation joins
by exact `line_id = id`; absent or ambiguous IDs stay explicit. Its recorded
crop hash is checked through the root index, including when the recorded path
is a Mac-era locator. Missing native `source_url`/`year` and source position
fields are filled from that exact record; attribution and the literal
`page_id`/`bbox` survive with input SHA256, record locator, ID and field selectors.
`bbox` also supplies `crop_bbox`. The builder projects this evidence into
`source_record_json.validation_original` and `book_bridge_evidence_json`.
Source page references stay distinct from the logical-page FK, and no page
number or catalogue URL is inferred. Existing native values take precedence.

Per-population `custody_via_index` reports index custody. Census additionally
reports `previous_no_recorded_path` (unresolved by the previous S1/v4 mapping)
and `previous_no_recorded_path_resolved_via_index`, to measure recovery of the
coordinator's remaining 227,124 rows. Exact join field counts and unresolved
validation IDs are in `original_crops.json.validation_originals`; per-row
evidence remains in `keys.sqlite`, with the file/hash index in `crop-files.sqlite`.

S4r validation joins are exact for 13,088/13,088 prepared IDs, with no ambiguous
or unmatched IDs. Source URL and year are recorded for 13,088/13,088; attribution
is recorded for 9,963/13,088 (3,125 absent). This is the existing §3 field 8
projection: source_url/year fill missing native values; attribution remains
in the exact-ID source record with its selector, input hash and record locator.
The machine spec pins that admitted_all_v2 input SHA256 and records these
complete measurements. Historical book/source probe counts remain separately
identified; they are not relabeled as a new production build.

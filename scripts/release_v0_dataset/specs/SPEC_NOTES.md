# Current status — REL0-S4s, 29 October 2026

The active source spec validates with zero pending resolver decisions: four
resolved bindings, four partial bindings and twelve historical unknowns.
Original crop custody is measured completely: six populations resolved and
census partial (483,078/592,466; 109,388 no_recorded_path). See SOURCE_SPEC.md,
JOIN_DECISIONS.md and the SHA-bound S4r measurements in source-spec-001.json.
Validation source_url/year coverage includes the exact admitted-ID S4r overlay;
attribution retains its source-record provenance and measured absence count.

This does not establish production build readiness: GAPS.md records the
unimplemented release-builder/acceptor crop-index and harvest-payload integration.
Those gaps are deliberately left unfixed in S4s. Local fixture build/acceptance
and structure validation are separate from production execution.

The following S4c notes are historical discovery evidence. Their statements
about null feature inputs, tuple joins and freeze blocking are superseded by
the active spec and subsequent join decisions.

---

# Source spec 001 — REL0-S4c, 28 October 2026

`source-spec-001.json` records the observed selectors for the first Clariden
smoke candidate. **It is incomplete and cannot yet be frozen or run.** Required
feature inputs and the new dataset version are null; missing relational sources
are null in `pending_selections`. `unresolved_bindings` gives a reason and search
scope for every unknown. These are evidence limitations, not a claim that the
historical records do not exist. Nothing was fetched, submitted or built remotely.

The 44 input selections use explicit inventoried file paths, not directory globs.
Their order is the builder's priority/name order; explicit per-source file order
is lexical inventory order. Prepared pools and A12 splits are separate inputs,
so smoke's first-file cap applies independently to every pool and split. Freezing
still hashes every selected file in full: this includes the 11 GB census and
56 raster shards. This is a bounded **row-output** smoke selection, not a bounded
hash-I/O selection. Follow COMMANDS.md's CPU-worker preparation instructions.

`probe_evidence` identifies the exact inventory/table behind each executable
selection. `evidence_files` and `probe_receipts` bind the local evidence by bytes
and SHA256. These are not hashes of remote source payloads. A12's three small
receipts and the local operation map also retain observed `expected_sha256`;
that key is advisory: freeze does not enforce it. Compare the eventual lock to
those values. The operation map's relative path resolves to this checkout's
`out/RELEASE_v0/probes/synthetic-001/OP_IMPLEMENTATIONS.json`; deploy that exact
file with the spec. Do not open any receipt-discovered path automatically.

## S1 v4 and the old reference pools

- `s1`: full-001/s1subset.inventory.json's exact capstor
  `scaling_w3/subsets/scale1-c05-003/ref_364871.jsonl`. Native `parent_id,row_id`
  bind the original tuple, `label` supplies text, and `crop_path,crop_sha256`
  supply the historical image locator/hash. The adapter's documented v4 alias
  and original-id trainer bridge apply. No book/page/box is extracted from ids.
- `old0,old1`: the two exact `union_0/train/shard-00000.parquet` and
  `union_1/train/shard-00000.parquet` selections are **line_id-only keysets**,
  not extra populations or substituted original images/labels.
- Counts are 364,871 S1, 364,173 distinct old keys, 698 S1 additions and no old
  removals. The intersection of the two S1-minus-old directional lists has
  698 keys; their union has all 364,871 keys, also proving the old pools are
  disjoint. Prepared retains 364,870; the one removal is recorded in the
  supplied directional list, without inventing an audit witness.

Unknown: complete original crop custody and relocation-map contents;
original raw labels for every tuple; exact bibliography, box/page/frame bindings;
S1 physical source-shard byte/label equivalence. The shared records schema
(`id,doc,text,...`) is not appended as new original rows: it lacks parent_id,
and its id-to-tuple relation is not demonstrated in the local inventory. The
probed iopsstor S1 node-binding path does not exist; the config mentions a
capstor path but supplies no inspected node record. Neither path is treated as
a verified binding. `assets` stays empty and `missing_image_reason` preserves
S1's locators without opening unselected files.

## Gennadius-inclusive harvest and its HF alias

`harvest` reads **only** the root `metadata.jsonl` under
`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_with_gennadius_cached_v4`.
Native `wave,id,text,split,crop_sha256,file_name,book_id,canonical_book_id,
edition_id,page_id,item,page,year,source,provenance` survive. The builder's
harvest adapter explicitly uses a release-wave parent namespace when the source
has no original parent; it does not claim this is a census parent. The trainer
alias retains the complete `harvest:{wave}:{id}` namespace.

`harvest_decisions` reads the 546,811 complete decision observations first
(priority 25), mapping `final_text`, `disposition`, `reasons` to the builder's
text/decision fields and preserving routes/binding/native provenance. Its
separate decision label does not replace the root release label loaded at 30.
`harvest_books` selects the 310-row registry, retaining aliases, assignments,
protection and instrument-role evidence. Decisions include excluded rows and
are not added to the admitted-release count.

`hf_harvest` reads the pinned archive's root metadata as a **keyset only**, using
the observed wave/id template. Both directional differences are zero at
497,556 keys. Neither HF data shards nor root/split duplicate metadata are
appended as a second population. The older `releases/harvest_20261025_v1` is
excluded; the full receipt explicitly compares **gennadius**, despite historical
command examples naming harvest.

Prepared retains 497,554 = 428,357 train + 16,350 dev + 52,847 test. Two original
train removals remain identifiable by the supplied key list. Unknown: complete
asset manifests and file_name base, original parent relation for the newer
waves, exact box/frame bridge, nested bibliography selectors and audit witnesses.
Top-level item/page/year are retained; URLs, volume, edition description or page
convention are not invented from opaque provenance/id strings. Crop bboxes are
retained as recorded and do not become raw Google polygons. Original payloads
remain explicitly unavailable until asset selection is established.

## seal04 references and validation

Prepared `seal04_dev` has 437 rows and `seal04_test` 2,253. They are selected
separately with dev/test roles; seal04 dev supports checkpoint selection and
Stage B hyperparameters, seal04 test is report-only, per the builder's pool-role
mapping. Native prepared rows report `split=reserved`; that value is preserved
and is not rewritten from directory names.

The original root is `/capstor/scratch/cscs/fffoivos/greek-ocr-e3/benchmark_0.2/seal04/`;
config discovery identifies `suite.json`. The v4 package contains inspected
`seal04_suite.json` and `seal04_SEAL_RECEIPT.json`, selected as small evidence.
Those receipts do not expose the nested panel row schema or an original tuple
bridge. Consequently **original row patterns, reference-table fields and row
instruments stay null**; no guessed `dev.jsonl`/panel filename, parent constant
or trainer_alias is used.

Prepared `validation` (13,088 rows) is a separate `reference` role, retaining its
native `val` split and `validation_reference` selection role. Its original tuple
bridge is also unresolved. Full prepared ingestion will fail on unresolved real
aliases. Smoke can silently skip unresolved prepared rows, so an exit-zero smoke
cannot prove seal04/validation coverage; inspect per-pool coverage explicitly.

## prepared005 trainer payloads

All eight observed pools are explicit: `non_parliament`, `parliament`,
`harvest_dev`, `harvest_test`, `seal04_dev`, `seal04_test`, `validation`,
`synthetic`. Use only their inventoried `part-*.parquet` files. `factory/`
contains import/source shards and is not another trainer pool. Small
`runtime.json` and `factory/audit_report.json` are evidence only.

Native `image_png`, `gt_nfc`, `gt_nfd`, `label_ids`, `codec_version`, `line_id`
and reuse/source metadata remain intact; the prepared adapter copies trainer
bytes and records shard ordinal/pool order and the `prepared005` variant.
`non_parliament` contains **735,976 mixed v4/harvest rows**, parliament 57,251;
it is not a 364,870-row v4-only pool. `prepared_train` keysets are partitioned by
the adapter's intact harvest prefix. Dev/test harvest keysets are unioned with
train for the retained-population comparison. Raw source fields are retained
sanitized, including recorded split; public licence fields are removed by the
existing builder.

Model ids `compact-w1`, `compact-w1.5`, `compact-w2` and OCR version v0.10 are
read from the local MODELS.json register, not copied from SOURCE_SPEC examples.
Final executed run-binding SHAs remain null. No expected CLAIM is promoted.
Prepared membership follows the builder's documented interpretation; actual
per-step draw counts and sampler proof are not supplied by these probes.

## census06, release_v4 and crops4 original-tuple relations

- `census_g2`: the exact g2 decisions stream, 592,466 original tuples. The
  documented census adapter maps `binding.parent_id,id,split,crop_sha256` and
  native `final_text,disposition,reasons,routes,edits`; decisions remain complete.
  An independent ADMIT/train keyset uses the canonical tuple `row_key`.
  No globally unique census row_id or trainer alias is assumed. The old-pool
  bridge and direction of the inherited seven-key difference remain null, so
  there is no fabricated reconciliation.
- `v4_admissions`: 167,946 tuple-bound labels from `label`; source admission,
  split, edition and crop hash survive. `v4_sf7`: 904 independent overlay labels,
  with `parent_text` mapped to raw text and original provenance preserved.
  Both use `select_label:false` to retain the existing convenience label.
  SF7's native tool_version/tool_digest remain in records; the builder's
  producer_version defaults to the selection name, not an asserted historical
  version. The two small v4 release/correction receipts retain producer evidence.
- `crops4_relations`: 207,243 tuple records, preserving relative_path, sha256,
  bytes, source and split, plus explicit `crops4_relative_path,crops4_sha256`
  aliases. No absolute crop root or crop-to-native-frame transform is supplied.
- `v4_row_split`: 320,479 exact tuple/edition/split patches. This is a subset
  relation, not the whole corpus. Patches use exact tuples and require an existing
  row; execution must establish coverage and reject conflicts.

v4 flips remain complete sanitized decision observations, not extra admitted
lines. Expected-tool-version and external-version receipts are selected without
turning their uninspected nested values into constant version declarations.
Unknown: parent raw text sources, complete crop assets, reference memberships,
producer-version projection and every tuple-to-staging geometry bridge.

## Pinned staging-v4 pages, boxes and provenance

Use only the explicit tables below the archive snapshot pinned at
`8ee9cb2e4c880f450c69b9c45cd683765d4da755` (harvest pin is separately
`103c6dcd1e5dac6d72a1048462cd5b1864600cca`). Pins are supplied by the brief and
snapshot tree names; actual payload bytes/PULL_RECEIPT are not locally verified.

- `staging_boxes`: both Google box shards, retaining native `box_id`,
  segmenter/run, source object/page index, response representation/hashes and
  reading order. Project only observed polygon JSON-string columns to the typed
  polygon fields; the bbox alias is retained in record_json. Nested raw_segmenter_json fields were not probed, so
  language, emitted-index, coordinate-frame and frame-status selectors stay
  unknown. Existing sanitization removes the raw payload.
- `staging_page_images`: all 56 observed raster shards, copying `image_bytes`
  under native `page_object_id`, including recorded format/dimensions/hashes.
  The 13,981-row `pages/pages.parquet` is an **object inventory**, with no
  logical page_id. It is retained as sanitized decision evidence, not relabelled
  as logical pages by equating ids.
- Both page-result tables, source_objects and w_page_observations are retained
  as sanitized decision streams. Result records have `source_object_id` and
  `raw_page_index`, but no typed logical page_id/segmenter_run_id pair. W
  observations retain source_page_id/provider page/book ids and page-object
  aliases. Raw page records and rights fields are removed by existing policy.
  The two small staging manifests are retained as evidence.

Logical `pages`, `page_frames`, `segmenter_page_results` selectors and the
row→box→page→book joins stay null. No dimensions/hash-based transform, fabricated
run id, successful acquisition status, book identity or single page-object
choice is supplied. This preserves failed/zero/unmatched observations without
asserting they constitute completed typed relations. New-wave coverage beyond
staging is not established.

## A12 only, all three splits

Select 47 train + 3 val + 1 reserved shards from the exact capstor A12 root.
Native split columns supply the split. Counts: 190,486 / 9,208 / 3,999 = 203,693.
The shared factory id is
`A12@e81aa95bdc32113b398f16ebe9741782fc875a50eb3de6b75522b8183f258271`;
`a12_build_info` binds that observed small receipt. Audit/select receipts are
selected separately. `old_synth` has the same total but is excluded entirely.

Native images, codec labels, font stem, source_dataset/source_doc_id, severity,
polarity, background, accent survival, reuse and ordered applied_ops survive.
The existing synthetic adapter computes image hash/dimensions/operation count,
recovers font sha16 from build_info, and records historical unknown reasons.
Configured source/effective recipe hashes and realised distributions remain
separate. No full font hash, exact source-text locator/hash, historical producing
code/binary SHA, per-line seed or operation parameters is recovered here. The
local operation map identifies inspected functions/source hashes only. Prepared
synthetic selects A12 train and the builder checks exact image/text/codec equality;
no prepared val/reserved synthetic pool is inferred.

## Schema test and remaining execution work

`SOURCE_SPEC.schema.json` is a **test contract transcribed from the documented
builder interface**, including explicit nullable evidence gaps. S4b ships no
formal source-spec JSON Schema or validate_spec API; this file does not change
its freeze behavior. Tests validate JSON structure, every inventory-backed path
and field root, logical table keys, hashes, population roles, namespace retention
and directional key evidence. A test-only copy supplies local fixture feature
files and a test version to exercise the actual freeze/read_lock API without
opening any remote path. The unchanged spec is also checked to be rejected by
the real builder while required bindings are null. This is not a full production
schema or an assertion that the pending relational sources validate.

After the coordinator supplies the missing bindings, freeze on a CPU worker,
check all source hashes and archive PULL_RECEIPT, then run and read back the
bounded smoke. Full mode also requires the missing supporting tables. Schema
success, a fixture lock and smoke exit zero do not establish those relations,
original/trainer byte equality, full archive coverage or release acceptance.
Open gaps are recorded in RELEASE_v0/GAPS.md; no provenance repair is attempted.

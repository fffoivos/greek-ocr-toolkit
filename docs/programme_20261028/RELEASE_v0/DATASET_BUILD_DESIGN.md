# REL0-S4a — dataset builder design, 28 October 2026

Phase (a) design; **builder implementation and production results are phase (b)**.
Authority: [PLAN.md](PLAN.md) rev 2 §3/§7, [owner](OWNER_BRIEF.md) items 3/5/6,
[Astra H01/H02/H03/M04/M07](ASTRA_PLAN_REVIEW.md), and the inherited
[HF builder contract](../../programme_20261019/registry/HF_BUILDER_PLAN.md).
[CROSSWALK.md](CROSSWALK.md) gives every retained relation/field and the only two
amendments: licence removed; raw Google payloads private. Do not copy the old mock
builder into production or mistake its fixture checks for source-adapter proof.

## Execution boundary and stages

1. **Coordinator pins and downloads.** Download archive snapshots at immutable
   commits in a separate authenticated foreground process. Pin staging-v4
   `8ee9cb2e4c880f450c69b9c45cd683765d4da755` and the **full** harvest commit
   corresponding to supplied `103c6dcd1e…`. Record repository identity, exact paths,
   bytes and SHA for downloaded objects. Local stat totals do not verify bytes.
   Inspect actual prepared005 config/runtime/final run bindings, not a current
   template or the older 364,173 registry pool. No token enters CPU job files,
   command arguments, environment exports, logs or receipts.
2. **Read-only probes and input lock.** Run the scripts in
   [COMMANDS.md](../../../scripts/release_v0_dataset/COMMANDS.md); sample first,
   full census/key scan in a CPU job. Resolve shared S1 source shards, source crop
   roots, references and A12/val/reserved build paths through their pinned
   receipts. Create INPUT_LOCK with full source paths/SHAs, HF commits, source
   row/key selections, schema/code/codec/Unicode versions, registry authority and
   extension hashes, known gaps and probe receipt hashes. Source-to-local path
   relocation must verify exact bytes. Missing/ambiguous objects remain keyed
   findings, not guessed aliases or silently skipped inputs.
3. **Credential-free CPU build.** Import no Hub client. Verify input lock and
   authentication-variable absence; use local immutable files only. Stream JSONL
   and metadata projections into disk-backed joins. Preserve every census and
   page/box observation. Copy existing binary payloads, compute hashes/header
   dimensions, derive features, and write deterministic, resumable page batches.
   Never call OCR, inference, rendering, segmentation or image re-encoding.
4. **Independent local readback.** Close outputs, inventory every path/byte/SHA,
   reopen every table/shard, verify foreign keys/counts/memberships and original
   embedded payload/label identities. Independently replay the inherited feature
   sample. Verify interruption/resume and export round trips. A build publishes
   its complete manifest only after reconciliation, not after a partial batch.
5. **Coordinator upload and full pinned readback.** Build and verify in the fresh
   private repository described by PLAN H06. Upload is a separate foreground
   authenticated process. Download the exact candidate commit to a disjoint
   readback tree; verify every path/byte/SHA and semantic checks below, then load
   every config and exercise image joins. Coordinator performs the private-archive
   rename/public cutover only at the plan's authorized stage. Final refs are main
   plus immutable v0.n tag, with no source branches; archive stays private. Record
   candidate/public commit equality and pinned model/dataset cross-links. No git,
   upload, rename, launch or visibility action is implemented or executed here.

## Logical schemas and physical layout

Strings UTF-8; hashes full SHA256 except explicitly named historical `font_sha16`;
counts int64; geometry/percentages float64; booleans nullable when evidence is
unknown. JSON decision/provenance objects preserve original semantics. Source
absolute paths are historical metadata; public payload/source locators are
repository-relative with file/row/member/hash identity. Null means unknown or
inapplicable with a reason, not zero, negative verdict or successful no-change.
No public column or nested copied record carries licence fields.

The following table is the phase-(b) schema checklist. Detailed columns and nested
supporting relations are in CROSSWALK; no supporting relation may disappear simply
because PLAN lists fewer top-level paths.

| Config/path | Key, content and joins |
| --- | --- |
| default `real`, `data/real/<split>/part-*` | One published real observation/explicit label selection per identity; namespaced id, original tuple/row_key, page/box/crop/book/edition IDs, source+trainer images and hashes, geometry/frame, final/raw/codec labels, split/instrument/decision/features/source metadata and training-use convenience fields. Distinct observation multiplicity survives identical crop hashes |
| `synthetic`, `data/synthetic/<split>/part-*` | Build-qualified `(factory_build_id,line_id,reuse_index)` plus source-build/role; image bytes/hash/dimensions; exact text/codec; source dataset/doc/text locator/hash; font full hash or sha16; severity/ordered ops/n_ops/rendering; source/effective recipe and generator code/binary identity; unknown/search status and per-model use |
| `pages`, `tables/pages[.parquet or /part-*]` | page_id; every observation incl. failed/excluded/no-raster, original source ID and alias relation, book/split/registry, acquisition outcome, source record, raster and source-object metadata |
| `page_images`, `tables/page_images/part-*` | Physical page_object_id and original image SHA; original raster bytes, dimensions, portable locator. Keep auxiliary composites explicitly marked |
| `page_frames`, `tables/page_frames[.parquet or /part-*]` | Page/response/frame identity; Document AI dimensions/transforms/image metadata, raster frame, mapping evidence/status, transform/inverse only when justified; sanitized response-representation metadata and public source-record locators |
| `boxes`, `tables/boxes[.parquet or /part-*]` | box_id; page/run/frame FKs; all raw versus derived polygons/envelopes, emitted/reading/top order, original indexes, anchors/orientation/scoped language/confidence, crop IDs and typed contributor lineage |
| `segmenter_page_results` | `(segmenter_run_id,page_id)`; requested manifest denominator, frozen run code/model/config/input-frame identity; ok/zero_detections/error/not_run and outcome evidence |
| `rows` | `(parent_id,row_id)` unique, row_key unique; every status/reason and FKs, original/corrected label IDs, source/split/book/instrument fields; typed crop/image variants and release_memberships retained even when never trained |
| `label_versions` | label_version_id plus `(row_key,label_variant,producer_version)`; text/hash/raw-field/normalization/corrections/routes, codec gt_nfc/gt_nfd/label_ids and source binding |
| `row_features` | `(row_key,label_variant,feature_version)`; label SHA, raw/NFC/nonspace lengths, six counts+percentages, scripts/polytonic/capitals/language/confidence, crop variant/dimensions/frame-aware position, code/codec/Unicode provenance |
| `row_instruments` | Exact original row ID/list kind/name/hash/declaration, resolved tuple/row_key; preserve multiple memberships, never inherit a row flag from a whole book |
| `training_membership` | `(model_id,role,pool,trainer_line_id,variant)`; source tuple or synthetic build key, exact image/label/codec variant, source shard+ordinal/pool order, available/eligible/drawn/selection/evaluation separately, draw count/status, sampler/mix/seed/config/runtime/run binding |
| `references` | instrument/view/split/source-row/label+image variant membership; raw/corrected seal04, v2 common/full/raw, validation; exact payload locator, diagnostic_only and exposure qualification; observation order preserved |
| `book_registry`, `registry/book_registry` | Canonical book_id, original and canonical assignments/status/exportability, aliases, source split labels/provenance, superseding rulings and harvest_protection; authority v2 and later harvest extension bound independently |
| decisions JSONL gzip | Every original keyed decision/reason/route record, generation/hash/locator. Split into part-*.jsonl.gz if closed singleton exceeds cap; source keys/statuses unaffected |
| `synthetic/RECIPE.json`, `synthetic/BUILD/`, `synthetic/OPS.md` | All retained source/effective recipes, build/codec/font/source/job manifests; operation file:function/hash map, configured vs realised per-split distributions, unknown search receipts. Multiple build-qualified recipes rather than one misleading replacement recipe |
| `manifests` | MANIFEST, SHA256SUMS, BUILD_RECEIPT, COVERAGE; exact source pins, code/environment, input lock, batch/config/shard/semantic checks, per-population null reasons, all-public-path inventory and logical digests |

Available public observations can lack original crop bytes; rows record missing
custody and never recreate bytes under an old SHA. Every used real row must resolve
its primary box→page→book chain or retain a concrete unresolved finding for the
checkpoint; successful release acceptance cannot silently ignore that failure.
Synthetic origin and truly unavailable reference geometry use documented nullable
links, not fabricated boxes. All actual source keys must still be represented.

## CPU dataflow, resume and byte sharding

Import the immutable g2 decisions once, not the mutable ~25 GB live ledger or
several overlapping admission exports as independent rows. Index typed aliases,
parent tuples, census/release/split membership and source→factory IDs on disk.
Dedup payload **storage** by exact hash if useful; never dedup observations or
rewrite held-out membership. Preserve the 7-row census-versus-old-pool difference
separately from S1's newer 698 net difference.

Join MAC observations/raw boxes to resident parent/crop records, then add newer
harvest/Gennadius source pages/boxes from their own manifests. Staging-v4 alone
cannot supply all newer geometry. Extract sanitized frame/source evidence before
excluding raw Google payloads from the public inventory. Retain raw versus padded/
composed crop boxes and contributor relations separately. Resolve book aliases by
typed identity; catalogue/search URLs are source metadata, not identity aliases.
Unknown/conflicting split assignments never default to train.

Use sorted page batches (inherited starting size 100 pages) with a disk-backed work
ledger. A batch receipt binds source lock, schemas/code/features, key digest,
output paths/SHAs, null/error coverage and counts. Write `.partial`, close, check,
then rename to its final local shard path before marking complete. Resume rechecks
completed batch SHAs and identities; source/code/config changes require a new
binding. Interrupted partial files cannot count as completed publication artifacts.

Every **closed public file** must be <= **1,000,000,000 B**; target **512,000,000 B**.
Do not assume row-group size enforces a byte cap. Stream bounded row groups with
binary byte accounting, close at target, stat it, and if oversized split/rewrite
from existing bytes into smaller shards and recheck. A single row/object larger
than cap is a reported packaging finding; never truncate or re-encode it. Apply
the same cap to page rasters, both line variants, synthetic, table singletons,
JSONL gzip, provenance/config packages and optional SQLite transport chunks.

Core singletons below cap may retain PLAN filenames. Overflow switches to
`tables/<name>/part-*.parquet` (registry similarly), with card configs and MANIFEST
changed atomically in the same candidate commit. Decisions overflow similarly to
`decisions/part-*.jsonl.gz`; RECIPE/BUILD indexes name all build-specific shards.
Preserve source row ordinal and logical key digests across re-sharding. No public
absolute path is a consumer dependency. Checksums include the manifest but avoid
self-reference; immutable HF commit is bound in the external publication receipt.

## Key reconciliations required before acceptance

| Reconciliation | Required keyed proof, not only count |
| --- | --- |
| S1 364,871 input | `ref_364871.jsonl` row IDs → shared records/edition → shared real/build_info crop_sha256 and physical source shards; bind real_mix and S1 node/validation/panel source identities |
| Retained v4 364,870 | Exactly one S1 input crop removal with audit's train/eval witness; remaining IDs, source crops, exact prepared005 image_png and labels agree |
| Old pool 364,173 versus S1 | Union of distinct keys in old union_0/union_1 versus S1; publish both directional differences with row/crop/label/release/normalization provenance. 698 is the **net cardinality difference**, not proof of subset or same variants |
| Census 364,180 train ADMIT versus old pool | Preserve the inherited seven-key difference and recorded exclusion/normalization provenance without changing verdicts; also retain all 592,466 g2 observations (456,967 ADMIT / 84,754 HOLD / 50,745 DROP), the 167,946 additions and 904 sf7 overlay records |
| Harvest + Gennadius train 428,357 | Actual chosen release root/receipt/registry/TRANSFER and metadata → `harvest:<wave>:<id>` → import.jsonl/factory crop map → prepared real pools; witness all removals using the audit's exact manifest files |
| Real train 793,227 | Disjoint retained v4 + harvested train keys reconcile to non_parliament 735,976 and parliament 57,251, exact image and label variants, original pool order and final model run bindings |
| Harvest dev/test | 16,350 / 52,847 **observations**; test has 52,846 unique crops but all 52,847 rows retained. Namespaced source IDs and exact trainer payload/label/reference-map identities match; don't infer split from factory `reserved` |
| seal04 | Additional dev 437 / test 2,253, total 2,690; raw/corrected variants/instrument order and exact consumed images retained. Preserve diagnostic_only and exposure notes |
| v2/validation | Common 42,038, full 43,883, original test source 44,029 as distinct memberships; validation prepared005 13,088 rows and selected val mix/ordinals, with original roles |
| Synthetic | Prepared train 190,486 / 47 files → pinned A12; compare by build/line/reuse/image/label, not recipe nickname. Earlier val 9,208 / reserved 3,999 belong to the separately identified old build until exact provenance/codec comparison proves otherwise |

The saved audit reports three eval-wins train crop removals overall (one v4,
therefore two harvest given the documented population attribution), zero train-only
dedup removals and retained same-split evaluation repeats. It points to attempt004
witnesses even though prepared runtime is attempt005. Those are existing provenance
links, not evidence of a stale path to replace. Reconcile the original HF harvest
497,556 count against selected release/retained 497,554 harvest observations with
these **keyed** witnesses before claiming equality.

`trained_in` lists actual model use, not all rows in an available pool. Bind final
run manifests/runtime identity and draw receipts independently per model. Any
unavailable draw detail is explicit uncertainty; eight-pass schedules or a 50%
synthetic component do not prove every particular synthetic row was sampled.

## Semantic and public acceptance

Use all checks promised in PLAN §3 and the inherited contract:

- Full source-key/status/reason coverage, all raw boxes and all requested page/run
  outcomes (including failed/excluded/zero/not_run); no admission from missing
  routes. Census, source-only rows and box-only observations remain distinct.
- Key uniqueness and typed aliases; row→box→page→book FKs, label/crop/lineage/
  reference/membership FKs; exact book split and line-instrument counts reconcile
  to each pinned registry version. Report ambiguous or missing mappings by key.
- Original/source and trainer image SHA **and embedded bytes** agree with inputs;
  exact label text/hash/codec/ids and each consumed variant agree. Re-sharding
  never changes images or labels. Hashes without second-image payloads are
  insufficient. Closed-file hashes are not substitutes for embedded identities.
- Every source field has coverage by population/wave/provider and a null reason
  where missing. Public locators resolve sanitized source records sufficient to
  identify exact item/edition/volume/page where evidence exists. No fabricated
  bibliography or publicly advertised private-response URLs.
- Keep source-frame coordinates and transforms. Dimension equality alone does not
  prove frame equality; unresolved mapping has no guessed rotation/rescaling or
  native-normalised position. The 194 known mismatches are a starting inventory.
- Pin codec, Unicode database and Scripts.txt SHA/version. Independently recompute
  the inherited fixed 1,000-row sample across scripts/statuses/label variants.
  Check NFC/nonspace denominators, digit/punctuation/script precedence, named
  scripts, polytonic marks, capitals, provider fallback/ties and confidence scope,
  and crop-versus-trainer pixel identity. Reusing the builder helper is insufficient.
- Reference/common/full/validation/raw/corrected memberships complete; seal04_dev
  checkpoint selection, pooled-dev Stage B selection, and report-only test roles
  match final run evidence and retain historical exposure caveats.
- Every config opens at the same pinned commit; real/synthetic image values decode
  in consumer readback, image joins return the correct variants, and full row/box
  exports round-trip. Tiny probe fixtures alone do not satisfy this gate.
- Full path/bytes/SHA match after download; no closed file exceeds cap; configs,
  manifest, schema and overflow paths agree. Check installed uploader/service
  capabilities during coordinator execution, not from remembered limits. Search
  all public schemas/nested records/cards/manifests for removed licence fields
  and private raw Google payloads. Finish with public visibility/archive privacy,
  exact main/tag refs and immutable cross-links verified by readback.

## Derived resources and limits of estimates

These are **saved-receipt** totals, not fresh Clariden stat/hash measurements.
Local summation of prepared005 runtime pools gives **264 Parquets / 25,133,416,295 B /
1,068,688 observations**, including synthetic and validation/reference roles:

| Pool | Rows | Files | Bytes |
| --- | ---: | ---: | ---: |
| non_parliament | 735,976 | 180 | 15,738,023,512 |
| parliament | 57,251 | 14 | 1,724,344,874 |
| synthetic train | 190,486 | 47 | 5,824,004,051 |
| harvest_dev | 16,350 | 4 | 356,570,967 |
| harvest_test | 52,847 | 13 | 1,147,734,679 |
| seal04_dev | 437 | 1 | 5,852,207 |
| seal04_test | 2,253 | 1 | 33,042,989 |
| validation | 13,088 | 4 | 303,843,016 |

The source spec's staging package is **40,711,310,115 B**, including private raw
Google data that will not all be public; the brief describes the HF harvest branch
as ~18.2 GB. These plus prepared payloads suggest ~84.0 GB of already selected
source material before original v4 crops, census exports, historical refs and
build indexes. They overlap and **must not be added as final dataset size**.
The immutable decision stream alone is **11,014,509,459 B** in SOURCE_MANIFEST;
separate 11.267 GB admission/8.507 GB train exports overlap it. The old 75–95 GB
v4 planning envelope does not bound the expanded harvest/Gennadius release.

Metadata-only probing avoids ~25.1 GB of prepared image-column reads; actual I/O
also includes Parquet metadata column chunks and sequential JSONL, so it is not
zero-I/O. JSON row size controls peak memory; a single whole JSON receipt is
bounded at 32 MB unless an explicit streaming array/map is selected. SQLite keys
and full directional differences grow on disk in the output directory. Start
probe jobs at 1 CPU/4–8 GiB and measure; these are sizing hypotheses, not qualified
wall-time promises.

For phase (b), inherit 8 CPUs/32 GiB only as a starting **benchmark shape**. Measure
representative JSON import/key joins, frame/source extraction, original/trainer
payload copy and closed-shard readback separately, recording rows/bytes/elapsed,
peak RSS and index/scratch size. Extrapolate each stage from measured work/rate
and include full independent readback. No full-builder two-hour estimate is
qualified. Use streaming batches; never materialize all 11 GB decisions or 25 GB
payloads into Python lists.

Let D = pinned downloads, P = measured proposed public bytes, I = measured work
indexes, T = maximum temporary rewrite footprint (at least one closed shard plus
its replacement shards). Build scratch needs **D + P + I + T**, plus resident
sources if copied; independent local readback needs another **P**. A separate
machine may supply that readback space. Reserve headroom from those measurements,
not a hard-coded total. For uncompressed planning, 25.13 GB payloads / 512 MB is
about 50 target shards, but actual table splits/embedding/compression and double
source/trainer images change that number. Final counts and byte budgets must
come from closed files. Login-node probes do not qualify production throughput.

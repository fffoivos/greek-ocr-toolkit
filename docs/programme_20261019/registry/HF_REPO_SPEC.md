# RUNNER4 — private Hugging Face line registry and builder plan


> **MOVED (24 Oct 2026 10:49 Europe/Athens, owner):** the dataset now lives at **`fffoivos/greek-ocr-lines`** (private). The owner moved it from `glossAPI/greek-ocr-lines`; branch `staging-v4` is unchanged at commit `8ee9cb2e4c880f450c69b9c45cd683765d4da755`. Older references below are historical; HF_UPLOAD_COMMANDS.sh now targets the new id.
22 October 2026. **Phase 1 Mac packaging authorized; creation/upload and the Clariden population build remain on HOLD.** Proposed dataset: **`glossAPI/greek-ocr-lines`**, private. The 21:44 coordinator decision selects the split route below. This document includes the earlier one-book dry run and the Phase 1 handoff contract. No HF repository, upload, tag, production census builder or cluster job was executed. Sol does not commit; owner decides the next step.

## Scope and first revision

The owner's 21:18 order changes the publication target of the [registry design](LINE_REGISTRY_DESIGN.md) to an HF **dataset repository**. Preserve the four relational tables, original source identities, every retained page/Google box, decisions and label variants, and the exact line images already used by training. Keep code and small custody receipts in Git; keep images, tables and databases outside Git. Licence information is recorded **per item, never an admission or upload gate**. This applies equally to every source, including Anemi; the explicit owner instruction supersedes the older source restriction in `AGENTS.md` for this task.

First complete tag: **`v4`**, containing the current real training population, its existing synthetic population, references, and the wider page/box/census inventory needed to analyse exclusions and compare segmenters. These are different populations:

| Population | Binding / count |
| --- | --- |
| All census observations | generation 2, `g2-e310b8ef84cc4763b036fd0abfc0295d`: **592,466**, comprising 456,967 ADMIT / 84,754 HOLD / 50,745 DROP |
| All train ADMIT | **364,180**, census scope; retain every key even if outside the final trainer pool |
| Released W1/W2 v4 additions | **167,946**, with **904** separate sf7 overlay records |
| Actual wave-2 v4 real pool | **364,173** = 196,227 control + 167,946 additions; add/add_corr have the same image population, **1,071** changed labels in add_corr |
| Existing synthetic build | **203,693** = 190,486 train + 9,208 val + 3,999 reserved, codec v2.1 clone of recipe v5 |
| Source collection-v2 splits | 214,436 train / 13,522 dev / 44,029 test; preserve original and canonical split spellings |
| Sealed references | seal04: **2,253 test + 437 dev**, 199 editions; preserve `diagnostic_only` and its unresolved canonical-work/checkpoint-exposure qualification |
| v2 continuity reference views | Common intersection **42,038**, full coverage **43,883**; raw source split 44,029. Preserve view memberships separately; cleaned ADMIT views are separately named selections, not replacements. |

The seven-row difference between census train ADMIT and the final real pool must be an explicit keyed membership difference with the trainer's recorded exclusion/normalization provenance. Do not change a census verdict to make these totals equal. Current counts/bindings come from the resident receipts and [training probe](../../../out/runner4/HF_TRAINING_PROBE.json); the census totals remain producer counts, not a new full 11 GB decision scan.

Later tags `v3`, `w3`, etc. bind their own source, selection, crop and label manifests. Do not retroactively call v4's row selection v3. Each tag points to a complete immutable Hub commit, recorded in a local publication receipt. A later amendment gets a new tag; never move an existing release tag.

## Repository layout and custody

```text
README.md                               # dataset card; draft below
pages/pages.parquet                     # page observations, including failed/excluded
pages/rasters/<group>/part-*.parquet      # embedded exact PNG/JPEG bytes, <=1 GB
provenance/mac/w_page_observations.parquet # W observations including failed/excluded
provenance/mac/source_objects.parquet     # portable raw/metadata TAR member locators
provenance/mac/google_boxes/<group>/part-*.parquet # retained raw Google boxes
provenance/mac/*_page_results.parquet     # raw parse/zero/missing-raster outcomes
boxes.parquet                           # all raw and harvest-derived boxes, all segmenters
rows.parquet                            # original row IDs, decisions, labels and memberships
metadata/book_registry.parquet          # canonical RUNNER5 book aliases/splits, pinned SHA
metadata/row_instruments.parquet         # exact line lists/roles + list hashes
metadata/book_registry/BUILD_RECEIPT.json # assignment/source hashes and conflict report
row_features.parquet                    # keyed by row + label variant + feature version
provenance/{page_aliases,response_objects,segmenter_runs,
            segmenter_page_results,box_lineage,crops,
            label_versions,release_membership}.parquet
provenance/google/part-<sha256>.tar       # stored raw responses/archives + representation index
provenance/census/part-<sha256>.jsonl.gz  # exact decision/reason/route records, source locators
provenance/sources/                      # item licences, edition/split/source manifests, configs
crops/original/part-<sha256>.tar          # source crop PNG bytes, not regenerated
crops/v4/train/part-<sha256>.parquet      # exact image_png payloads used by the trainer
synthetic/v5-codec-v2.1/{train,val,reserved}/part-<sha256>.parquet
synthetic/v5-codec-v2.1/provenance/       # recipe, font/source manifests, build and codec receipts
references/seal04/{raw,corrected}.parquet
references/v2_test/{raw,corrected,membership}.parquet
references/images/part-<sha256>.parquet  # existing reference image payloads, stored once by hash
references/validation/                   # dev/validation membership and exact existing payloads
analysis/registry.sqlite                # only if <=1 GB; derived scalar indexes
analysis/registry.sqlite.parts/part-*    # ordered transport chunks if database >1 GB
manifests/{sources,release,coverage,artifacts,mac-artifacts}.json
manifests/SHA256SUMS
```

Each binary/tar/Parquet shard is **at most 1,000,000,000 bytes**, target **512,000,000 bytes**. Check actual closed-file size and split again if needed; row counts alone do not enforce a byte limit. The four named core Parquets stay single files while below the cap; if larger, use `boxes/part-*.parquet`, etc., and change the manifest/card config together. TAR members use deterministic source-object IDs with payload hashes recorded separately; record `shard_path,member_path,offset,length,sha256`. Parquet image payloads record shard, row group/row locator and payload SHA. TAR headers have deterministic names/order/mtime/uid/gid. File hashes identify stored bytes; sorted logical table hashes identify content across different Parquet encodings.

Phase 1 retains the **8,574 legacy PNGs and 5,389 W JPEGs unchanged**, plus **18 explicitly auxiliary composite rasters**. Embed their original bytes in Parquet image shards; `image_sha256` always hashes those original bytes. This supersedes the earlier proposed JPEG-to-lossless-WebP conversion for this handoff: no decoding/re-encoding, duplicate JPEG archive, resizing, deskew or EXIF autorotation. Read native PNG/JPEG dimensions from headers. `pages/pages.parquet` in the Mac handoff indexes **physical raster objects**, keyed by `page_object_id=SHA256([source_root,relative_path])`; SHA joins connect aliases. It is **not yet the final census logical-page table**: W observation IDs/rights are separate, and legacy book/edition/split aliases come from the archived metadata plus resident Clariden parents. The final builder resolves these to the schema below and retains the original physical-object index as `provenance/mac/page_objects.parquet` before publishing the final logical `pages/pages.parquet`. Do not count cache objects as unique logical pages.

The Mac package archives exact stored Google responses (including stripped JSON and dedup gzip wrappers), W page/state records, legacy page/Google receipts, source metadata and assignment descriptors. `source_objects.parquet` records every stored-object SHA and relative shard/member/offset/length. Raw Google boxes are imported without treating them as harvested envelopes; original line JSON, vertex coordinates, normalized coordinates, order and response identity are retained. Response payloads, request-error objects and receipt sidecars have distinct retained outcome evidence; missing raster matches remain explicit. Phase 1 packages no synthetic data and computes no census population features.

Manifests contain relative Hub locators, artifact bytes/SHA256, counts, schema/feature versions, producing commit **and code SHA**, environment, source pins, known gaps, per-batch receipts and release membership digest. Original absolute Mac/Clariden paths remain provenance fields, never the paths a consumer must have. The manifest lists every shard; a checksum list includes the manifest itself without a self-referential manifest hash. The local publication receipt binds the final Hub commit/tag and both machines' upload commits. SQLite is a derived convenience copy; Parquet and the source manifests remain authoritative. If `registry.sqlite` exceeds **1,000,000,000 bytes**, keep the assembled database only in build scratch and publish ordered **512,000,000-byte** binary chunks under `analysis/registry.sqlite.parts/`. The transport manifest binds each chunk's path, ordinal, bytes and SHA256, plus the assembled database's full bytes/SHA256 and SQLite version. Download all chunks at one pinned commit, verify each, concatenate in manifest order, verify the assembled hash, then run `PRAGMA integrity_check`. Do not upload the oversized singleton. No database-specific compression or SQL dump is required; byte concatenation reconstructs exactly the same database. The final assembled database is exempt only locally, never from the Hub file-size cap.

## Schema and joins

The detailed [design contract](LINE_REGISTRY_DESIGN.md#2-identity-schema-and-storage) remains in force. HF adds portable image/crop locators, label versions and training-image identities:

The canonical book→split input is now the [standalone RUNNER5 extraction](book_registry/README.md), consumed without rerunning or editing RUNNER5. Both `pages` and `rows` require canonical `book_id,split`, preserved `source_book_id,source_split`, `book_registry_sha256`, `book_split_labels`, `book_split_assignment_status`, `book_split_exportable`, `harvest_protection`, `book_aliases_json` and `split_provenance_json`. Join typed aliases (local line-ID prefix, edition hash, provider item or v2 book ID) to exactly one registry record, then inherit the page book on its rows. Failed/pre-OCR-excluded pages receive the same book split. Preserve source-row disagreements as diagnostics. The 00:38 ruling resolves IA b28038630 to train with harvest protection retained; any future train/hold-out conflict is `conflict_hold_out` with export disabled; other incompatible book assignments fail closed as `unassigned`; missing splits never default to train. The registry table ships at `metadata/book_registry.parquet` and exact line memberships at `metadata/row_instruments.parquet`, with build/source receipts and SHA256SUMS; pin its SHA in every batch/release manifest. Its suite-specific roles are book protections, distinct from actual reference-row membership. Training export requires a resolved `train` book plus the separately recorded row/release eligibility.

| Table | Key and required content |
| --- | --- |
| `pages` | `page_id`; literal `source_page_id`/namespace, book and edition IDs, provider item/page, source, original image path/hash/bytes, portable raster/original locators and hashes, width/height/frame, acquisition status/reason, canonical book_id/split/registry SHA, harvest_protection, alias/assignment provenance, per-item licence/rights JSON and source-record locator/hash. Failed/unrendered pages retain null raster fields. |
| `boxes` | `box_id`, page FK; `segmenter=google|toolkit|…`, frozen run/config/model identity, raw/derived geometry kind, pixel and normalized polygon/envelope, original Google normalized geometry, order and emitted index, geometric index from top, raw segmenter fields/response locator, crop IDs and contributor lineage. Every returned box survives even if no crop/row exists. |
| `rows` | Original **`(parent_id,row_id)`** identity and scalar `row_key`; primary box/page/crop FKs, source/book/class, geometry projection, status/reasons and census binding, exact-line lqb_row/release_excluded_row plus list names/hashes, harvest_protection, canonical book_id/split/registry SHA and assignment provenance, raw text/hash/field, corrected text/hash, raw/corrected label version IDs, applied corrections and route statuses, split, release and actual trainer membership. Multiple image variants use the supporting crop/membership relations. |
| `row_features` | `(row_key,label_variant,feature_version)`; label SHA; NFC character/raw-codepoint lengths; six disjoint bucket counts and percentages for Greek/Latin/Cyrillic/digits/punctuation/other; polytonic marks, numbers, punctuation count, all_caps, has_capitals, mixed_script, named scripts, provider/heuristic language and scoped confidence; census class; crop dimensions/aspect and crop variant; normalized primary-box centre and top index; feature/code/codec/Unicode provenance. |

`row_key=sha256(canonical_json([parent_id,row_id]))`; `row_id` is never rewritten to be globally unique. Page/box IDs follow the versioned tuple hashes in the design. Equal crop/page SHAs are secondary identity witnesses, never a reason to merge editions, splits or source observations. `ADMIT→used`, `HOLD→held`, `DROP→dropped`; retain every reason object verbatim. `used` means census accepted in its scope, not proof of a training draw. Pre-census rows keep their existing IDs with `not_harvested`; boxes without source rows get a left-join view with nullable row ID, not invented training IDs.

**Two crop identities are essential.** `source_crop_sha256` identifies the original crop PNG. `training_image_sha256` identifies the existing factory `image_png` payload after resize/letterboxing. Verified source code writes these transformed PNGs (`factory/src/import_real.rs`, `shard.rs` in the trainer checkout). Store both as `crops` variants with recipe/transform and original-to-factory line-ID mapping. Preserve the existing payload bytes by copying/re-sharding binary values, **never regenerating them**. Release membership specifies the exact crop variant and label version consumed. Dataset availability does not imply every held/dropped crop still exists: missing bytes/dimensions are explicit, not recreated under an old SHA.

`label_versions` distinguishes source raw, census g2 final, v4 raw, registered sf7/ru1/n1 overlays, and the factory codec/NFD training strings. Base v4 labels remain raw. Preserve `gt_nfd,gt_nfc,label_ids,codec_version` and recipe-applied operations with their original versions. Empty/absent correction lists are distinguishable; no-change is not inferred from an absent route. Features are computed for raw and census-corrected labels; additional training/overlay variants get their own keyed feature records, not an overwrite.

Feature definitions use the corrected Astra contract: percentages divide by **non-whitespace NFC codepoints**, with digit → punctuation → codec-aware NFD-base/name script precedence, then other. This is not Unicode-block counting. Other letter scripts use a pinned Unicode `Scripts.txt`; Hebrew+Arabic is mixed although both count toward other_pct. Empty percentages are zero; all_caps requires cased letters and no lowercase; Lu/Lt drives has_capitals. Polytonic presence means Greek-base NFD breathing/perispomeni/subscript/grave, not acute alone. Provider languages use highest finite confidence with lexical ties; absent provider language uses `script-tag-v1` (`mul` for any two named scripts, `und` for no letters), always null heuristic confidence. OCR confidence is separate and records its scope. Crop geometry features state whether source or training pixels supplied dimensions.

Google polygons remain explicitly in the **retained Document AI page frame**, described by `document.pages[i].dimension` and any `transforms`. Matching image hashes alone do not prove matching coordinate frames. Phase 1 detects **194 dimension mismatches (14 legacy, 180 W)**; matching dimensions can still have a recorded transform. Raw response bytes retain the full transforms and Google image metadata. Do not rescale/rotate boxes heuristically, call these native-page polygons, compute native position features, or compare them with toolkit boxes until the per-page frame mapping is verified. Keep unresolved frame status visible. All three representative join pages have matching dimensions and no recorded transforms. This source-frame issue is a concrete Phase 2/Astra review item, not a packaging failure or an authorization to repair geometry.

Stored response hash, archive/member hash, historical original-response hash and reconstructed-original hash remain separate. In particular, a stripped legacy JSON may only verify the historical hash after the documented in-memory embedded-image reconstruction; never label its stored hash as the original response hash. Preserve the representation adapter and verification result in `response_objects`. Restoring the input raster as embedded Google image content is only valid where that exact historical representation is verified; transformed/stripped pages may not reconstruct the original response bytes. The Phase 1 legacy witness verifies one reconstruction, not a global rule.

Example DuckDB query after downloading the four tables at **one pinned revision**:

```sql
SELECT r.parent_id, r.row_id, r.crop_id, r.box_id, p.provider_item_id,
       f.greek_pct, f.length_chars, b.bbox_px
FROM read_parquet('rows.parquet') r
JOIN read_parquet('boxes.parquet') b USING (box_id)
JOIN read_parquet('pages/pages.parquet') p ON p.page_id=b.page_id
JOIN read_parquet('row_features.parquet') f USING (row_key)
WHERE r.status='used' AND r.split='train'
  AND f.label_variant='raw' AND f.feature_version=$feature_version
  AND f.greek_pct>=50 AND f.length_chars>=20;
```

The small later CLI exports `parent_id,row_id,row_key,crop variant/hash,label variant/hash,release_id` for training lists, or page hash/locator, box polygon/frame/run ID for re-cropping. Queries never create new admissions. Newly selected toolkit segments receive new crop/label identities; they cannot inherit a Google training label solely through IoU.

## Physical sources and measured sizes

Roots: `C=/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data`; `H=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big`; `D=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-data`; `W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`; `P=/capstor/scratch/cscs/fffoivos/greek-ocr-e3/e4_wave2_rel4_e0735c1_20261021_prep03/code`; `J=P/out/e4/wave2/job02`; `G=W/census_06_20261020/attempts/full-split-002/generations/g2-e310b8ef84cc4763b036fd0abfc0295d`.

The selected source manifest remains [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json), SHA256 **`f468812a38687cad4aa025290c207ea9148eac2068aa721f7809f933e78c6578`**. [HF_LOCAL_STATS.json](../../../out/runner4/HF_LOCAL_STATS.json) freshly re-statted all **42,623 selected files / 41,296,254,030 bytes**: no missing/size/mtime changes. This confirms physical selection stability, **not byte verification**; the 18,514 stored-hash gaps remain. Full source and transfer lists remain in [STAGING_PLAN.md](STAGING_PLAN.md).

| Part / actual location | Physical count and decimal GB | Verification / planned payload |
| --- | --- | --- |
| Legacy pages: `H/<wave>/images`, round1 rescue, page_reads_v1 | **8,574 PNGs / 22.244549 GB**; composites **18 / 0.003361 GB** separately | Fresh stat vs selection; retain exact PNGs. Logical page/edition alias reconciliation remains open. |
| W pages: `C/run/cache/pages`; records `C/run/W{1,2}/pages` | **5,389 JPEGs / 4.453653 GB**; **4,707 records / 0.020981 GB** | 4,621 completed observations plus exclusions; W2 state also has one failure without page JSON. Cache object count is not logical page count. |
| Google source objects: `H/<wave>/google/docai`, page_reads/montage; `C/run/responses` | **13,099 / 6.577672 GB** legacy; **4,612 / 5.489236 GB** W | Stored archives/stripped/original representations, not unique responses or total line boxes. Global raw-box count is a later parse result. |
| Legacy row/assignment metadata: `D/docs/harvest/<wave>/records*.jsonl`, worktree `docs/records/harvest` | Row files **8 / 0.767867 GB**; assignments **6,131 / 1.675285 GB**; other metadata **61 / 0.051151 GB** | Resident Clariden reuse from the pinned manifest is provisional until full hash readback. |
| Parents/splits: `W/collection_v2/import_real_v2_{train,dev,test}.jsonl`; mirrored W snapshots | v2 **0.186984 GB**; W snapshots **1.591600 GB**; census metadata **0.124411 GB** | Existing classes, inventories, script/length/confidence fields retained with original producer versions. Edition map **644,541 B**, compressed row split **1,032,585 B**, pinned in SOURCE_MANIFEST. |
| Census generation `G` | decisions **11.014509 GB**, admission records **11.267048 GB**, admitted train **8.506810 GB**, evaluation diagnostics **2.679537 GB** | Overlapping exports, not additive new rows. Publish one compressed canonical decision/evidence stream plus locators, not three duplicate row populations or the mutable **24.841253 GB** ledger. |
| Release `W/release_v4/rel4_c06_full_01` | admission **173,049,274 B / 167,946 rows** | Fresh complete stream hash **`dcae2aebc239c2f22eb5bec6da01218958fb235388553730f3ece14dca6dfa75`**, matching the pin. SF7 **4,374,139 B / 904 records**, separate version. |
| CROPS4C: `W/collection_w{1,2}_originals`; manifest `W/crops4_attempts/crops4_c06_full_01` | **207,243 selected / 3.595018 GB / 3,997 selected pages** | Receipt count/size; manifest **70,696,962 B**, checksums **30,960,336 B**, already freshly hashed in staging. Not all census crops. |
| Original v2 crops: `W/collection_v2/crops/<wave>` | **Whole-tree total unknown**; bounded eight-second walk reached **24,026 / 0.187401 GB**, incomplete | This lower bound is not a total or a representative extrapolation. Full keyed custody inventory belongs in the later CPU build. |
| Exact v4 training images: `J/union_{0,1}/train/shard-00000.parquet` | **2 shards / 7.486898 GB**, 364,173 real rows by bound inventory | Shards **5.764362 GB** and **1.722536 GB** exceed the proposed cap: re-shard without changing image_png bytes/labels. Whole-file SHAs are producer pins, not freshly read image payloads. |
| Current synthetic: `J/control_synthetic_7` | **51 Parquets / 6.225008 GB**, 203,693 rows by build receipt | train **47 / 5.791677 GB**; val **3 / 0.298323 GB**; reserved **1 / 0.135009 GB**. Existing fonts/recipe/provenance, no generation. |
| Historical synthetic: `W/greek-page-ocr/out/e1_run4/synthetic`; `…/out/e4/wave1b/v2-codec/old_v2/synthetic` | **120 files / 6.252490 GB**; **54 / 6.225037 GB** | Alternate versions/copies, not added to v4's 6.225 GB. Archive later through version membership/hash dedup, not recreation. |
| seal04: `W/benchmark_0.2/seal04`; trainer `J/benchmark_0_2` | **2,690 original PNGs / 0.034390 GB**; raw JSONL **6,580,305 B**; **2 trainer Parquets / 0.039067 GB** | Raw and corrected references share image hashes. Correction overlays and instrument status remain explicit. |
| v2 test: `W/greek-page-ocr/out/e4/wave1b/v2-codec/{common_intersection,full_coverage}.json` → selected reserved shards | **11 / 0.902652 GB** common; **11 / 0.949426 GB** full | Selected files freshly statted; views share support and are deduplicated by payload SHA in publication. Enclosing v2-codec tree **199 Parquets / 17.427995 GB** includes train/synthetic/other views and is not a reference-only upload. |
| Dev/validation: `J/validation_v21/mix.json` → val shards | **9 / 0.301051 GB** | Enclosing clone has 63 Parquets / 4.999193 GB across splits. Only selected val payloads/memberships belong in references. |

Remote size/receipt evidence: [HF_SOURCE_PROBE.json](../../../out/runner4/HF_SOURCE_PROBE.json), [HF_TRAINING_PROBE.json](../../../out/runner4/HF_TRAINING_PROBE.json), [HF_REFERENCE_PROBE.json](../../../out/runner4/HF_REFERENCE_PROBE.json). These distinguish byte hashes, stat totals and producer counts. Pod backups remain inaccessible in the earlier probe and are neither selected nor required; no unverified pod size is included.

**Budget:** the selected physical sources plus CROPS4C, one real trainer pool, one synthetic build and the named reference payloads are about **60.8 GB before compact tables and any additional v2 source crops**; this is an additive planning envelope with overlapping views, not a deduplicated final measurement. Phase 1 uses original PNG/JPEG bytes, so the previously proposed **5–15 GB WebP expansion is removed**. The old [three-page WebP probe](../../../out/runner4/HF_PAGE_ENCODING_PROBE.json) remains historical evidence, not the selected encoding. Allow **1–4 GB** for tables/SQLite and **5–15 GB** for compressed census evidence/additional source crops/manifests: approximately **66.8–79.8 GB before precise overlap/dedup and unresolved crop custody**. Retain **75–95 GB** as conservative complete-v4 planning headroom, not a measured final total; allow **120 GB publication staging plus 20 GB scratch**, excluding existing source copies. The measured Phase 1 manifest below replaces the Mac portion of these estimates. No measured total for unknown legacy crop custody is invented.

## Split builder and upload plan — Phase 1 local packaging, later publication

| Phase | Built on / inputs / output | Upload origin |
| --- | --- | --- |
| 1. Pages + Google boxes | Mac, streaming the pinned page/response inventories; small page batches, resumable metadata/raw-object shards. Embed original PNG/JPEG bytes in Parquet; retain exact stored response/metadata objects in TAR. No segmenter inference. | Mac uploads only `pages/`, Google provenance and the pinned page/box batch Parquets. |
| 2. Source availability | Either owner-approved **35,198,780,622 B / 32,294-file** staging from the existing plan, **or** Clariden reads the already uploaded Mac artifacts at a pinned HF commit. Latter avoids shipping page originals twice; metadata joins consume imported page/box/observation tables and portable source locators; exact-byte/raw reconstruction checks additionally fetch the required shards. | No source transfer is started by this specification. |
| 3. Rows/crops/features/synthetic/references | **One later CPU allocation on Clariden**, immutable g2 exports + parents + v4 + CROPS4C + exact trainer pools + frozen refs; join the Mac page/box tables, preserve existing synthetic bytes, re-shard oversized trainer files, produce four final tables/supporting relations/SQLite. No rendering new synthetic lines and no GPU. | Clariden uploads its release-ready crops/synthetic/references/tables from local `/capstor` staging. |
| 4. Seal the revision | Verify both origins at one branch head, publish card + complete coverage/release/SHA manifests, then bind an immutable commit and `v4` tag. | Serial final metadata publication; read back metadata and selected shard bytes, record final Hub commit. |

Stable local roots: owner-requested Mac `~/Projects/hf-staging/greek-ocr-lines/`; this restricted session packages at `/private/tmp/hf-staging/greek-ocr-lines/` because the requested path is outside its writable roots; Clariden `/capstor/scratch/cscs/fffoivos/greek-ocr-data/line_registry/hf/v4/{build,upload,receipts}`. Explicitly set the Mac data root; it was unset during earlier probes. The Mac scratch package is created in Phase 1; the requested Mac destination and Clariden directories have not been created here. Relocation to the requested durable path remains an explicit handoff requirement; temporary scratch is not durable custody. Mac receipts checkpoint complete source groups (an interrupted group is rewritten deterministically); resume compares code/selection/index hashes, rechecks selected source stats and rehashes every completed group artifact. The later Clariden page-batch receipts also bind config and sorted output-key hashes. Publish manifest/SQLite only after all batches reconcile, so an interrupted build never masquerades as a complete release.

The Mac is not the bulk census worker. Phase 1 is serial, checkpointed packaging, raw Google-box import and source-byte verification. A measured first batch packaged **5,389 W JPEGs / 4,453,652,987 original bytes** into **nine Parquets / 4,455,421,261 bytes** in **9.30 seconds**, including source SHA reads, header dimensions, closed-shard SHA reads and index receipt generation, excluding startup/preflight and independent readback (`greek-ocr-lines.receipts/w_cache.json`). This is local measured packaging throughput, not a Clariden builder benchmark. Resume must rehash completed shards, compare code/selection/index hashes and recheck source stats.

**No fixed two-hour full-builder allocation is qualified.** Before a later full Clariden submission, run one owner-authorized bounded CPU batch with representative joins, feature calculation, payload copy/re-sharding and verification, recording each stage's elapsed/input bytes/input rows/output bytes and peak memory. Derive the wall time from measured stage rates and actual remaining work (including the independent verification pass), report that calculation, and then select the allocation. The older unmeasured **60–210 minute** combined estimate is a planning envelope only; two hours would under-cover its upper end. The Mac measurement cannot substitute for that first Clariden batch. No job is submitted or configured in Phase 1.

The one-book four-table probe is not a throughput qualification: **1.35 s** warm Mac table construction excludes its SSH/remote inventory, global reconciliation and byte packaging. Uploading 75–95 GB takes **50–63 min at 25 MB/s**, **25–32 min at 50 MB/s**, or **125–158 min at 10 MB/s**, payload only. Mac and Clariden links are unbenchmarked; retries and SHA readback add time. Any full Mac→Clariden staging still needs the owner's explicit transfer go; the HF route does not silently authorize that transfer.

### Authentication and concrete command shape

Current installed `huggingface_hub`/`hf` is **1.1.6**, verified using `hf version` and command help without authentication. Its subcommand is `hf repo`; current online documentation uses `hf repos`, so pin the uploader version and verify help on each host. Future commands below use the locally checked 1.1.6 syntax. Repository existence, namespace write permission and private storage entitlement were **not checked with a token** in this task.

```sh
# FUTURE ONLY; no token retrieval, repository creation or upload was executed.
# Shell tracing must be off; no `hf auth login`, token file or --token argument.
HF_TOKEN="$(security find-generic-password -a "$USER" -s codex-hf-token -w)" \
  hf repo create glossAPI/greek-ocr-lines --repo-type dataset --private

# After creating a staging-v4 branch; serialize the two origins' commits.
HF_TOKEN="$(security find-generic-password -a "$USER" -s codex-hf-token -w)" \
  hf upload-large-folder glossAPI/greek-ocr-lines "$MAC_HF_STAGE" \
  --repo-type dataset --revision staging-v4 --num-workers 2
```

Each upload root contains only manifest-listed publishable files with intended repo-relative paths. Mac uploads pages/Google batch artifacts first; Clariden uploads its disjoint payload second. A final metadata upload replaces interim batch tables with joined core tables and marks the revision complete. Do not tag an intermediate multi-commit upload. If a repo already exists, explicitly verify `private=true`; `--private` on upload/create is not proof that an existing repo changed visibility. Resumable upload caches contain progress metadata, never the token.

**Separate foreground private-source download, before CPU building.** From the Mac, inject the Keychain token into a foreground SSH staging launcher with `HF_TOKEN="$(security find-generic-password -a "$USER" -s codex-hf-token -w)"` on that command only. Pass it over SSH stdin to a remote Python process that reads the token line in memory, sets `HF_TOKEN`, and executes the installed `hf download glossAPI/greek-ocr-lines --repo-type dataset --revision <immutable-Mac-upload-commit> --local-dir <capstor-source-stage>` with manifest-listed Mac paths. Never download against a moving branch. Check installed CLI help before launch. The authenticated process fetches the pin/manifest first and the listed payloads, verifies sizes/SHA256 and exits; its receipt includes the HF commit, hashes and paths, never the token. The owner must authorize this later publication/staging step; Phase 1 makes no network transfer. No `hf auth login`, token file, command-line `--token`, scheduler export or persistent login is allowed. Ordinary Hub download-cache metadata is not a credential store.

Then start a **separate, credential-free CPU builder**: require `HF_TOKEN` and alternative authentication variables to be absent, take only verified local paths/manifests as inputs, and perform no authenticated downloads within the job. The builder's source manifest binds the downloaded HF commit and byte readback. Upload is a third foreground process after building, with fresh ephemeral injection.

**Clariden token at upload-process launch only:** finish the CPU builder without credentials. From the Mac, inject the Keychain token into the launcher's environment using the exact assignment above. A small foreground SSH launcher passes that value on stdin to a remote Python process; it reads one line, sets `os.environ['HF_TOKEN']`, and `exec`s `hf upload-large-folder` for the fixed Clariden upload root. Token stays out of SSH argv, shell text, files, logs and receipts. Do **not** use `sbatch --export`, a batch script, environment dump or scheduler job with the token: scheduler spooling would violate “never written.” Do not persist login state. Upload is a separate process, not the authenticated CPU build. If that launch mechanism is unavailable, leave the completed package intact and resolve launch-time injection; never write a token to make progress.

Before sealing, download/read back `manifests/artifacts.json`, its checksum list and the four small table metadata/counts at the candidate commit; verify the complete remote path/byte inventory, available Hub content hashes and selected full shard SHA readbacks. Record how much remote content was actually rehashed; do not claim every remote byte was downloaded when only Hub metadata was compared. Create `v4` against that exact commit using `hf repo tag create … --repo-type dataset --revision <commit>` after owner disposition. Preserve that commit in the receipt and examples. HF supports explicit data-file configs in the card, so tables of different schemas are separate configs rather than one inferred mixed dataset. See [HF data-file configuration](https://huggingface.co/docs/hub/datasets-data-files-configuration), [uploads](https://huggingface.co/docs/huggingface_hub/guides/upload), [CLI](https://huggingface.co/docs/huggingface_hub/guides/cli) and [HF_TOKEN environment behavior](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables).

## Segmenter comparison hook

Mac packaging initially imports Google only. A later toolkit adapter consumes the **actual deployment export** `prototypes/fast_lines/shared/review.py:detector_record`: `page,image_size,unit="line",items[].polygon`. It imports the emitted, clipped, non-discounted boxes, not internal candidates. A frozen run binds code/model/config/input-page-manifest SHA and the original native raster frame; toolkit does not become a new page identity. Keep emitted order separate from sorted `(y0,x0,box_id)` top index. Any input raster encoding alias must pass dimensions/pixel-frame checks.

Persist `(run_id,page_id,status,box_count,result_sha256,locator,error)` in `segmenter_page_results`, including `ok`, `zero_detections`, `error`, `not_run`. The denominator is the requested page manifest, not the pages with nonempty JSON. Raw-box comparison excludes harvest-derived crop envelopes unless explicitly selected.

First analyses: (1) polygon IoU/match distributions per same-hash page, with split/merge relations and unmatched boxes; (2) centre/edge offsets and width/height ratios by normalized page position and linked **raw-label** script mix, with unlabelled boxes kept separate; (3) source rows covered/lost and candidate boxes gained, separately for zero/error/not_run pages. Export chosen polygons for new crops and independently bound labels. Overlap alone cannot establish text correctness or training admission.

## Dataset card draft

The following is the proposed `README.md` content at the complete v4 tag; numbers are intended source bindings, not a claim that HF publication already happened.

```yaml
---
pretty_name: GlossAPI Greek OCR Lines
language: [el, grc, la, en, ru, sr]
multilinguality: multilingual
task_categories: [image-to-text]
license: other
license_name: per-item-source-licences
license_link: provenance/sources/licences.parquet
configs:
  - config_name: pages
    data_files: [{split: inventory, path: pages/pages.parquet}]
  - config_name: boxes
    data_files: [{split: inventory, path: boxes.parquet}]
  - config_name: rows
    data_files: [{split: inventory, path: rows.parquet}]
  - config_name: row_features
    data_files: [{split: inventory, path: row_features.parquet}]
---
```

**Description.** Private inventory of harvested OCR pages, Google/toolkit segmenter boxes, original/corrected line labels, decisions and analysis features, plus the existing real and synthetic line images used by GlossAPI OCR experiments. Inventory splits above are relational tables; actual train/dev/test membership is stored in the row/release relations.

**Versions.** `v4` binds census06 generation 2, the 167,946 released additions and the 364,173-row actual real training population; the existing synthetic train pool has 190,486 entries. Historical `v3`/`w3` tags bind their own manifests. Pin a commit or tag when downloading; rows marked used and actual training release membership are different fields. Raw, census-corrected and release-overlay labels remain independently selectable.

**Structure and joining.** Canonical book_id and split come from metadata/book_registry.parquet at its bound SHA. Whole-book harvest_protection governs new acquisition separately from dataset split. Exact row flags lqb_row/release_excluded_row join metadata/row_instruments.parquet by original line ID and retain list names/hashes; neither changes all rows in a book. Unresolved conflict_hold_out blocks new training selection; IA b28038630 is resolved to train by the hash-bound 00:38 ruling. Join rows to boxes by box_id and boxes to pages by page_id; join features by row_key **and** label variant/version. A row's source ID is the pair parent_id,row_id. Original crop and transformed training-image hashes differ. The portable locators resolve exact bytes in image shards. Synthetic lines have no fabricated physical page: join their factory identity to synthetic provenance and release membership; page/box links are null with origin=synthetic. References preserve raw and corrected labels, full/common membership and image identities.

**Sources and licences.** Per-item/source declarations and URLs are recorded at `provenance/sources/licences.parquet`, including unknown or unverified values verbatim. No blanket licence is asserted for all images, texts or fonts. Source declarations do not filter membership; all sources, including Anemi, follow the same schema and process. The repo is private. Synthetic provenance records font identity, generator/recipe hash, source text identity and recorded licence; absent historical details are marked unknown, not invented.

**Comparison and limitations.** Add segmenter runs against the same page manifest, retain per-page zero/error/not-run outcomes, and compare polygons, offsets and coverage. Newly generated segments need their own crop and label binding. seal04 remains diagnostic_only; edition checks do not settle canonical-work or historical checkpoint exposure. Coverage manifests disclose missing source objects, unknown crop availability, unresolved contributors and source hash reconstruction. Script/language/confidence fields describe their recorded algorithms and scopes, not human-verified language labels.

**Reproduction.** The **existing 203,693 synthetic image payloads and their labels are archived** with available provenance, so the recorded dataset can be **reconstructed without rendering**. This does **not** claim deterministic regeneration from font/text/recipe/seed: missing historical inputs remain unknown. Preserve historical bytes even when those fields are unknown; new generator runs are separate versions. Existing trainer PNG payloads are copied from the bound factory shards, preserving their codec labels and byte hashes. New generator runs get new version identities and are not part of this publication.

Synthetic provenance must retain `factory_build_id,line_id,reuse_index,image_sha256,gt_nfd,gt_nfc,label_ids,codec_version,script_class,split,font,font_file_sha256,recipe_sha256,recipe_effective_sha256,generator_code/binary_sha256,applied_ops,severity,source_dataset,source_doc_id,text_source_locator/text_sha256,seed/job locator,licence,provenance_completeness,historical_unknown_fields`. Each unavailable historical field is null with an explicit unknown reason and source-search receipt; never substitute a guessed current font/config/seed. Archive the complete existing payloads/labels and every retained provenance/config/codec/build/source/font manifest. Existing shard schema already has font, source dataset/doc, licence, reuse index and operations; build receipts have recipe hashes and font **sha16**. Full font SHA and per-line original text/seed locators must be resolved from the frozen source/job manifests where retained. A sha16 prefix is not a full SHA256; missing provenance stays explicit while the bytes are still archived. Save the bound configs/codec/source manifests and supported font files/declarations under the same per-item licence-recording rule.

## One-book dry run — completed, no upload

Code: [hf_one_book_probe.py](../../../out/runner4/hf_one_book_probe.py); remote read-only probe: [probe_hf_sources_remote.py](../../../out/runner4/probe_hf_sources_remote.py). Book **`bsb11759351`**, census book ID **`bsb_poly1850--027215cc6d2a7e8a`**: all its **40 harvested page records**, consisting of **39 retained page rasters/responses plus one blank-page exclusion**. This is not a claim that every page of the provider volume was harvested.

The remote query used the existing `(parent,source,book,page)` index, one read-only SQLite transaction, generation 2/binding checks and unchanged CURRENT before/after. It returned all **1,429** rows for the book, joined exact crop identities through CROPS4C roots, and scanned the 173 MB v4 admission stream once, verifying its full SHA. This is a live-ledger demonstration, not an immutable-export validation. Local work read only this book's rasters/responses (27,472,800 + 33,336,922 bytes); matching original image/response hashes and matching native Google dimensions were required. Crop bytes were checked on Clariden, not transferred to the Mac.

| Materialised artifact | Records | Bytes |
| --- | ---: | ---: |
| `pages.parquet` | **40** | **22,812** |
| `boxes.parquet` | **2,858** = 1,429 raw Google + 1,429 harvest-derived | **483,744** |
| `rows.parquet` | **1,429** = 1,066 used + 296 held + 67 dropped | **530,221** |
| `row_features.parquet` | **2,858**, raw and census-corrected | **192,880** |
| `registry.sqlite` | Same four tables, unique indexes | **11,980,800** |

**All 1,429 row→box→page joins pass; all 1,066 used/v4 joins pass; no orphan features or duplicate table keys.** All 1,066 book release members match source raw labels/crop hashes, with present crop bytes. Of 1,429 rows, **1,078** custody crops were present and matched (34,903,858 bytes); **296 HOLD + 55 DROP** crops were absent in these roots. Absent crops retain expected SHA and null measured dimensions. Every raw box has a source anchor in this book, but that does not prove the same globally.

The probe deliberately stores a separate harvest envelope for each row and a known Google anchor; full multi-contributor reconstruction is pending and marked as such. No box-shard packaging, global join coverage, actual trainer-image payload readback or toolkit comparison is certified by this dry run. Original source crops, not resized training PNGs, supply its crop dimensions.

The four Parquets round-trip exactly and their SQLite joins agree. A deterministic **1,000-row / 2,000-label-variant** sample independently checks NFC lengths, nonspace denominators, digit counts, bucket sums and page y centres; fixed witnesses exercise capitals, Greek/Latin, Hebrew/Arabic and polytonic marks. This is not the later independent recomputation of **every** semantic feature. The probe also exports **591 used rows with raw Greek percentage ≥50**, preserving IDs and crop hashes, and a 40-page outcome manifest. The book has no toolkit run; the excluded page is `not_run`, not zero detections.

Data artifacts and detailed input hashes: **`/private/tmp/runner4-hf-book-20261022/`**, outside Git. Small tracked-candidate receipt: [HF_ONE_BOOK_RECEIPT.json](../../../out/runner4/HF_ONE_BOOK_RECEIPT.json), with exact table/code/input SHA256s and producing HEAD; probe code is uncommitted, explicitly recorded. `/private/tmp` is temporary custody, not the final data store. The existing system Python has mismatched native Pillow/NumPy architectures; the four-table probe avoids that dependency via PNG/JPEG headers, and only the three-page encoding probe used the existing x86 Pillow environment. No global environment was changed.

## Acceptance and remaining work

Later production acceptance follows the design: reconcile **every census key/status/reason** and **167,946 v4 keys + 904 overlays**, CROPS4C selection and exact source/trainer image identities; every used row joins exactly one primary box/page; retain box/page/exclusion/failure denominators and all discrepancies. Independently recompute all features on a pinned 1,000-row sample. Verify raw/corrected/reference memberships without changing their splits or diagnostic status. Demonstrate interrupt/resume equivalence and row/box export round trips. Re-shard every >1 GB file and verify exact embedded payload hashes before/after. Save the final complete path/byte/SHA/count manifest and the extent of HF readback.

The previous HIGH staging finding remains open until the packaged handoff is published, downloaded at an immutable commit and verified on Clariden; this book's Mac+remote join does not close it. The old seven-page Vouli and four-entry Round1 discrepancies, total logical page/raw-box counts, full legacy crop availability, contributor lineage and some synthetic provenance remain explicit production reconciliation work. The HF plan can publish/read Mac source tables directly to avoid the proposed bulk staging, but no such publication has occurred. Source licences do not gate this work.

**Phase 1 stop: package Mac inputs, verify the three representative joins against those portable inputs, and write reviewable upload commands only. Estimated complete v4 remains 75–95 GB; no upload, repo creation, bulk network transfer, production population build, cluster job or git commit is authorized in Phase 1.**


## Phase 1 package and stop

The Mac package is complete at **`/private/tmp/hf-staging/greek-ocr-lines/`**, **40,711,310,115 bytes (40.71 GB)** in **110 files**. The owner-requested durable path `~/Projects/hf-staging/greek-ocr-lines/` is outside this session's writable roots and remains unpopulated. This is temporary custody; [NEXT_SUBMIT.sh](../../../out/runner4/NEXT_SUBMIT.sh) records the unexecuted local relocation and HF creation/private-check/branch/upload commands. No token was retrieved and no command in that upload script was run.

The package contains **56 embedded-image Parquet shards**, **24 Google TAR shards**, **nine metadata TAR shards**, **two raw-box Parquets**, plus indexes/outcomes/source pins/checksums. Largest file: **511,979,520 bytes**. It preserves all **8,574 legacy PNGs, 5,389 W JPEGs and 18 auxiliary composites**, **17,711 selected Google source objects**, and **10,923 source metadata objects**. The Google set consists of **11,154 response payloads, 6,542 receipt sidecars and 15 request-error records**. Its **737,178 raw Google boxes** retain provider-frame geometry; **59 zero-detection pages** remain visible. No imported box lacks a retained raster hash match; that does not establish coordinate-frame equivalence (194 dimension mismatches above).

Full byte readback and the three current census→box→page joins are recorded in [HF_PHASE1_VALIDATION.json](../../../out/runner4/HF_PHASE1_VALIDATION.json); detailed costs, identities, coverage and limitations are in [HF_PHASE1_PACKAGING.md](HF_PHASE1_PACKAGING.md). Final population tables, native frame qualification, publication and pinned Clariden staging are still pending. The previous handoff HIGH remains open until the latter succeeds. **HF PHASE 1 PACKAGED — no upload, repository creation, cluster job or git commit.**


## 23 October 00:24 rulings and HF CPU-builder handoff

The [canonical registry](book_registry/README.md) now separates dataset split,
whole-book new-harvest protection, and exact line instruments. All **147** former
train+LQB/release conflicts retain **train** and **harvest_protection=true**.
The **00:38 ruling** resolves the one train/hold-out overlap (IA b28038630) to
**train**, protection true and exportable true. The registry is publishable with
**zero unresolved conflicts**; this does not authorize HF publication or a build.
No source release membership changed. Line flags are not inferred from book flags.

| Dataset split | Books |
| --- | ---: |
| train | 1,586 |
| dev | 28 |
| test | 92 |
| seal04_test | 148 |
| seal04_dev | 52 |
| hold_out | 153 |
| unassigned_w3_w4_pending | 148 |
| unassigned_superseded_wave | 8 |
| unassigned_harvested_not_admitted | 62 |
| unassigned_catalogue_only | 91 |
| unassigned_line_instrument_only | 113 |
| **Total** | **2,481** |

The original 309 books without a recorded assignment have origin labels
(148 pending, eight superseded, 62 harvested not admitted, 91 catalogue only).
The additional 113 instrument-only books have no source dataset split: a line
instrument cannot invent one. Retain their source/provenance rather than defaulting
them to train. There are **734 harvest-protected books**, separately from split.
Exact instruments contain **5,803 memberships / 5,383 line IDs**: 1,536 LQB and
4,267 release-exclusion memberships. metadata/row_instruments.parquet ships with
its hashes; rows retain original IDs, exact booleans, list names and hashes.
Pages and rows retain canonical book_id/split, registry SHA, aliases, assignment
provenance and harvest_protection. Unknown or conflicting assignment never erases
the original source ID/split.

[The hold-out investigation](book_registry/HOLDOUT_INVESTIGATION.json) identifies
IA b28038630 / mixed:4c207e1e, A Greek-English lexicon. The older test hold-out
was committed **15 October 07:25 +03:00**; the explicit later **whole book to train**
v2 policy was committed **15 October 14:02 +03:00** and records owner acceptance
in apply_clean.py. All **2,868** moved IDs are present/train, as are all **9,665**
current v2 lexicon rows. The later policy is authoritative for the recorded v2
release; the older lists still drive RUNNER5 new-harvest protection. The explicit 00:38 ruling adopts train for this registry; SPLIT_RULING.json
and both policy files are hash-bound in the assignment. Historical hold-out
assignments retain their evidence and superseding ruling ID.

All legacy/W1/W2/W3/W4 coverage checks remain. The rebuilt offline book probe at
/private/tmp/runner4-book-registry-dryrun-20261023/ has **40 pages, 2,858 boxes,
1,429 rows, 2,858 feature variants**. All **1,429 row→box→page→book joins** and
**1,066 used/v4 joins** pass with canonical split train, harvest_protection false
and zero exact instrument flags. Google boxes additionally retain effective
language detections and whether they came from the line or fallback page; this
was needed to replay language features correctly. The receipt binds current
registry/code/input/output hashes. No new remote probe or payload transfer ran.

[HF_BUILDER_PLAN.md](HF_BUILDER_PLAN.md) specifies the later foreground download,
immutable local input lock, credential-free CPU stages, exact payload archival,
features, references, batch resume, sharding, SQLite transport and measured
allocation sizing. Its executable offline mock uses the real one-book metadata;
the four payload lanes use **explicit MOCK fixtures** because those remote bytes
are unavailable on this Mac. It cannot produce a publishable artifact. The
1,000-row/2,000-variant feature replay uses the same helper and is not independent
production semantic verification. Tests cover credential rejection, exact shard
payload preservation, source/output tampering, broken joins, SQLite transport and
clean-versus-interrupted/resumed equality. See the
[mock receipt](evidence/HF_BUILDER_MOCK_RECEIPT.json).

**Current package location:** the original 40.71 GB Mac package is now at
/Users/foivoskarounos-zamparloukos/Projects/hf-staging/greek-ocr-lines/; its manifest
hash is unchanged and all 108 listed artifacts exist. This run did not move it
or rehash all payload bytes. Earlier temporary-location claims above describe
Phase 1 at that time. Already packaged page shards were not rewritten by this
metadata run; the later final tables must carry the current registry fields.

Production source adapters, global reconciliation, actual payload readback,
independent features and Clariden timing remain later work. The handoff HIGH
remains open until publication at a pinned commit and Clariden verification.
No upload, repository creation, submission, bulk transfer, production build or
git commit occurred. **HF BUILDER READY** means plan plus bounded offline mock.

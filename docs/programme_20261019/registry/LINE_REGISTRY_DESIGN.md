# RUNNER4 — line registry design

22 October 2026 · Sol · **Revision after Astra review 1; staging plan only. Owner decides. Build remains on HOLD.**

## Decision proposed

Store every harvested page, every retained segmenter box (including boxes that never became crops), and every existing row identity, with independent census decisions, label versions and release memberships. Keep original page pixels and raw Google responses in the data store; publish compact Parquet tables plus a self-contained DuckDB analysis file. A frozen toolkit run can subsequently add boxes against the same page hashes. Selecting different boxes produces a new selection/re-cropping manifest, never changes an existing training row or release.

Step 1 produced the initial design and source probes. The resume adds the [staging plan](STAGING_PLAN.md), pinned by [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json), file/stat inventories and bounded joins. No registry implementation/build, OCR request, segmentation run, crop generation, cluster job, source-data transfer or git metadata write occurred. Bulk byte verification remains pending: an inventory hash does not certify unhashed source assets. “All pages” includes retained rendered pages rejected before OCR, pages with failed reads and pages with no admitted rows. Training membership is not the page-inventory boundary.

## 1. Verified sources and source gaps

### Locations and evidence

Path abbreviations in this document:

- `W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3` on Clariden.
- `C=/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data` on this Mac.
- `H=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big` on this Mac.
- `D=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-data` is the Mac's existing external data mirror. `GREEK_OCR_DATA_ROOT` was unset in this shell; do not assume automatic resolution.
- `A=$W/census_06_20261020/attempts/full-split-002`.
- `G=$A/generations/g2-e310b8ef84cc4763b036fd0abfc0295d`.
- `R=$W/release_v4/rel4_c06_full_01`.
- `K=$W/crops4_attempts/crops4_c06_full_01`.

Firsthand evidence: [local inventory and samples](../../../out/runner4/LOCAL_SOURCE_PROBE.json), [remote receipts and samples](../../../out/runner4/REMOTE_SOURCE_PROBE.json), [live census input binding](../../../out/runner4/REMOTE_BINDING_PROBE.json), and [remote path existence probe](../../../out/runner4/REMOTE_PAGE_PATH_PROBE.json). Local probe code: [probe_local_sources.py](../../../out/runner4/probe_local_sources.py). Read-only SSH retrieved small receipts, file sizes and first records, and two indexed/limited ledger observations; it did not scan the ledger or large JSONL exports. Local work enumerated directories and small metadata/receipt files, read 500 feature records per snapshot, six W1/W2 raw responses and one historical raw response. Full hashes of large inputs below are producer pins read from live receipts/binding, **not newly recomputed full-file hashes**.

### W1/W2 pages and Google output

| Source | Firsthand count | Meaning |
| --- | ---: | --- |
| `$C/run/W1/pages/*.json` | 1,370 | 1,354 completed + 16 excluded page records; 429 book-id prefixes |
| `$C/run/W2/pages/*.json` | 3,337 | 3,267 completed + 70 excluded records; 1,087 book-id prefixes |
| `$C/run/W2/state.json` | 3,338 | Same records plus one failed page without a page JSON |
| Completed page observations W1+W2 | 4,621 | Not a count of unique raster bytes |
| Distinct completed image hashes | 1,354 W1; 3,258 W2 | Nine repeated hashes within W2; cross-tranche dedup not established |
| `$C/run/cache/pages/*` | 5,389 files; 4,453,652,987 bytes | Physical cache objects, including variants; not 5,389 proven distinct logical pages |
| `$C/run/responses/*` | 4,612 files; 5,489,236,156 bytes | Physical response objects, not line boxes |

Each completed page JSON carries `id`, `source`, `item`, physical `page`, `image`, `image_sha256`, `response`, `response_sha256`, and `analysis_page` including dimensions and provider/book metadata. Retain `analysis_page.item_record`, rights, source URLs and source-specific restrictions. Book IDs used by census are the page ID before `--s`; the `sNNN` slot is not the provider's physical page number. Edition IDs must come from the census metadata/edition map, not a title-based guess.

Example: `bsb_poly1850--027215cc6d2a7e8a--s000`, page image `$C/run/cache/pages/3ef838b275c8633d0afa1c686fb516509e73758411f46eb93af4b7a872fd09c0.jpg`. Its snapshot row `...-l0001` has `docai_line_index=0`, Google envelope `[786,158,839,188]` and **different padded crop bounds** `[784,156,841,190]`. The first raw line's four pixel vertices agree with the Google envelope. The W2 first-row check gives the same distinction: `[779,162,833,191]` versus crop `[777,160,835,193]`.

Raw response layout is `document.pages[i].lines[j].layout.boundingPoly.{vertices,normalizedVertices}`; retain the whole line object, `textAnchor`, orientation, confidence, languages, document text reference and response hash. Tokens/symbols remain available through the raw response, rather than copied into every box. Six sampled responses contain **43, 29, 34, 45, 222, 36 lines = 409 boxes**; the older sample contains **31 lines**. Raw response and image hashes in all six W samples matched page-record hashes. This establishes the geometry adapter, not total raw-box coverage.

### Older harvested pages behind collection-v2

The eight collection waves remain at `$H/<wave>/`. Images include rejected rendered pages; Google receipts at `$H/<wave>/google/docai/ledger.jsonl` bind page-image hash to raw response path/hash/version. Raw data can be archived: follow `google/raw_archives.jsonl` where present, including its member identity; absence of a loose JSON is not absence of geometry.

| Wave | Image files under `images/` (fresh enumeration) | Successful distinct image hashes in Google ledger (fresh metadata count) | Historical admission input lines (receipt count) |
| --- | ---: | ---: | ---: |
| round1 | 1,000, plus 799 under `rescue/images/` | 1,532 | 75,061 |
| vouli | 1,126 | 772 | 48,169 |
| round2 | 781 | 613 | 29,943 |
| parliament | 713 | 690 | 95,438 |
| openarchives | 1,443 | 917 | 30,788 |
| mixed | 1,396 | 782 | 46,515 |
| cyrillic | 663 | 566 | 37,398 |
| wikisource | 400 | 400 | 14,967 |
| Total | **8,321** including rescue | **6,272**, summed within-wave distinct counts | **378,279** |

The fresh successful-receipt count and historical page count differ: vouli's summary says 779 pages, its inspected Google ledger binds 772 distinct hashes. Historical read-page observations sum to 6,279, not a proven global distinct-page count. Preserve and report this seven-page discrepancy; do not silently fill it with inferred OCR output. Round1's `admission_inventory.json` contains 1,528 page-image entries versus 1,532 reported read pages. Use the union of manifest/plan/records/ledger identities, not that crop-oriented inventory alone.

Also inventory `$H/page_reads_v1/images/` (**253** files, 147,327,015 bytes), so prior native page reads do not vanish just because collection-v2 selected different rows. The **18** files in `$H/montage_v1/images/` are an auxiliary montage source: record them as composites in the source inventory, with provenance, rather than presenting them as native pages. Resolve any prior pilot page references through their original manifests. Additional page roots discovered by those manifests are added to the source manifest and counted before publication; this design does not claim a complete global page count from directory names alone.

Older metadata adapters read `docs/records/harvest/<wave>/{manifest*,plan,admission_inventory,admission_summary}.json` and raw per-line records. Large moved records resolve through `greekocr.ops.data_root.input_path` and the custody move manifest; for example `$D/docs/harvest/round1/records_all.jsonl` is present. Its sampled row binds `id`, `page_id`, `book_key`, physical page, `docai_index`, `bbox`, `image`, `image_sha256`, `docai_raw_text`, confidence and symbol indices. Native example image `$H/round1/images/db1ed5f902d696fb53656a7d-000006.png` hashes to `048fa6fb…`, agreeing with its Google receipt. Round1 source/crop policy is also recorded in `scripts/harvest/admit_round1.py`.

### Census_06 generation 2, release v4, splits and crops

Live `$A/CURRENT.json` is **completed, generation 2**, export `g2-e310b8ef84cc4763b036fd0abfc0295d`, binding `3e05d2f2b5b908f11e20010c7f85dc046920717590f82ba1520f7b0df92febe4`. Its freshly hashed SHA is `6da9b78e03269f125ac1af018412445416108168fc0188bce480ad8556cd0d2c`. `$G/summary.json` freshly hashes to `f12d31f10cc2282942492e85f40625bdc3da11e6ace1507a3b8b92e516ce33d2`, reports complete/reconciled, and binds these populations:

| Parent | Source rows | ADMIT | HOLD | DROP |
| --- | ---: | ---: | ---: | ---: |
| collection-v2-train | 214,436 | 196,234 | 8,922 | 9,280 |
| collection-v2-dev | 13,522 | 13,000 | 229 | 293 |
| collection-v2-test | 44,029 | 40,490 | 1,904 | 1,635 |
| collect-v3-W1-20261018-0524 | 101,098 | 68,578 | 21,728 | 10,792 |
| collect-v3-W2-20261018-0524 | 219,381 | 138,665 | 51,971 | 28,745 |
| Total | **592,466** | **456,967** | **84,754** | **50,745** |

The first three sources are `$W/collection_v2/import_real_v2_{train,dev,test}.jsonl`. Their producer SHA256s, in that order, are `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3`, `d462edac43e806ab87fac65860a3531cc9181d1c90a637d9e42eb45ca1940d17`, and `e7a4f4025adde53b8a5e7894f87bde3b12d7730e893d2f1b78dc4e78b83c00f8`. Preserve literal legacy split spellings `val`/`reserved` and canonicalize to `dev`/`test` as the existing adapter does. These are **271,987 observations**, not new W1/W2 release rows.

W snapshots are `$C/snapshots/W{1,2}_features_20261018_0524.jsonl`, mirrored at `$W/filter_pipeline_20261018/inputs/collect-v3-data/snapshots/`. Sizes: **503,777,486 / 1,087,822,541 bytes**. Producer hashes: W1 `c85b407a724f4a17dfbe659cc9e2dfd171660de5e29baf1fd86b291f7cbd9c4c`; W2 `4954a94cc3c051aeb36e367101bc3448233448422bb05834d3276e090de987b4`.

Census source metadata is `$W/filter_pipeline_20261018/prepared/87407ec7430a375f/metadata.json`, obtained from the live ledger's binding, not the mutable local template. It supplies edition/book, crop and split bindings. Release custody additionally pins `edition_map.jsonl` SHA `1cf086f3d4bb41a7159e1ac395915d38a839925bef56dcca7ac0400691a92854` and `row_split.jsonl.gz` SHA `7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82`; their exact input paths are in the live release receipt. Preserve those split/edition assignments, including evaluation protections.

Authoritative census decision stream `$G/decisions.jsonl` is **11,014,509,459 bytes**, producer SHA `9f00d46b11b4599fa5e4ff2e4d7c8f165f56eb6270b480e46e9fb5b0bd64e095`. Decisions carry `binding(parent_id,id,split,crop_sha256)`, disposition, full reasons, edits/routes, `final_text` and final inventory. `$G/admission_records.jsonl` producer SHA is `a3daa187e9b215b49724411d982893dc4200ff0207d320bc7e63d20d74ec9d45`; this file's `label` is the census final label, not necessarily raw text. `$G/admitted_train.jsonl` is **8,506,810,372 bytes**, **364,180 train ADMIT** observations, producer SHA `f32bcd197caa468114005a4f8762fa2d530e8b4709928f74cef971fe83423f52`. Evaluation diagnostics are a separate stream pinned by the summary.

`$A/ledger.sqlite` is **24,841,252,864 bytes**, with observations keyed `(parent,id)`, raw inventory, decisions and correction provenance. It is useful for samples, but use immutable generation exports plus pinned parents for the production build. A sampled collection-v2 observation has a bound crop SHA but `crop_bbox`, `crop_source_image` and `crop_source_sha256` all null: recover these through old records/page manifests/Google receipts, not by treating a crop as a page. No full join-coverage claim is made from this sample.

Live `$R/RELEASE_V4_RECEIPT.json` freshly hashes to `dbc99bdc7fd9c770e25880139ef3bd3184392bfe65e1eb2baf89544c8e390f32`. `$R/release_v4_admission.jsonl` has **167,946 rows**, W1 **50,622** + W2 **117,324**, **173,049,274 bytes**, producer SHA `dcae2aebc239c2f22eb5bec6da01218958fb235388553730f3ece14dca6dfa75`. Rows bind `(parent_id,row_id)`, edition, raw label hash, crop-relative path/hash, and admission-decision hash. Release labels remain raw. The **904 sf7 edits** are separate in `release_v4_sf7_edits.jsonl`, producer SHA `823f9e20064feb1c2bb6f22bfc60ef4e02d4dfea26b6b742beb9292792e22538`, registered by `corrections_registry.json` SHA `36d7d9957edfffb5743aef5f367936442d45b7f5e6dde4311698f3d4838d1756`. Store correction availability, census application and release application separately. `kept_unverified` does not mean verified correction.

CROPS4C: `$K/upload_receipt.json` freshly hashes to `dbead984d9425dc3181efae0d00e5448e6334227b6d366e160d8a619bb9f7148`: **207,243 selected/byte-exact**, **167,946 train + 39,297 held-out**, **3,997 selected pages**, **3,595,018,320 crop bytes**, all skipped-valid, zero failures/mismatches. `$K/crops_manifest.jsonl` is **70,696,962 bytes**, keyed `(parent_id,row_id)`, with relative path, sha and bytes; compute and pin its full-file hash at build time; the upload receipt binds the selection digest and input context, not an output-manifest checksum. Reconcile manifest entries to that selection and the crop checksum list. Also retain `crops_sha256.txt` and `sha256check.log`. Crop roots are `$W/collection_w{1,2}_originals/<source>/<row_id>.png`; collection-v2 crops are `$W/collection_v2/crops/<wave>/…`. **3,997 is not all harvested pages** and CROPS4C is not a manifest of HOLD/DROP crops.

Existing metadata to preserve, not silently reinterpret: W snapshots have `primary_class`, `script_class`, `inventory`, `visible_characters`, `digit_visible_fraction`, `mixed_line`, tags, Google contributors, crop bounds/hash/source, and earlier admission/rejection fields. Census has raw/final inventories, script counts, character counts, class/content role, route statuses and decision diagnostics. `greekocr/harvest/line_pipeline.py:inventory` and `text_primitives.py` already provide codec-aware script counting. Cache their values with producing version/label hash; new percentages and capitals fields have an explicit feature contract below.

### Preparation gap before the Clariden build

The read-only remote existence probe found the expected W snapshot mirror/cache directory, but **not** `…/collect-v3-data/run/W1/pages`, `W2/pages` or `run/responses`. The expected `$W/greek-ocr-toolkit/docs/harvest/harvest_big/<wave>/images` and old Google roots were also absent. This does not establish that no alternate remote copy exists. Resolve through custody receipts first; otherwise stage the above Mac sources, page metadata, archives and record manifests into a new receipted source snapshot on Clariden. No transfer was performed here. The job cannot reconstruct complete Google page geometry from release crops alone. Source availability and the old seven-page receipt discrepancy must be resolved or explicitly reported as incomplete coverage before calling the built registry complete.

### Resume source inventory and response representation (MEDIUM 2)

The new [staging plan](STAGING_PLAN.md) and [selected manifest](SOURCE_MANIFEST.json) supersede the preliminary transfer budget and source-location probe above. Clariden has **4,130/5,389** W cache files; missing **1,259** total **850,371,013 bytes**. Of **6,192** selected legacy metadata/assignment files, **6,191** have same-size remote counterparts; all eight old row-record files are also resident. Size matches are provisional reuse, subject to SHA readback. The three-key remote probe passes two W **row→harvest-geometry→page** joins, but **0/3 raw-Google joins**; the legacy sample also lacks its page raster. HIGH 1 remains open. The selected missing payload is **35,198,780,622 bytes**, with no transfer performed.

The resume freshly hashed CROPS4C `crops_manifest.jsonl` to `d72d247d7a3ccc51931e7f2df765219ce398907a021d1bcaa4f4eec44c5c224a` and `crops_sha256.txt` to `3d08559df8634d751fdec0a5864d384a7af5030790c1afeb0d65c3962b1a8b8f`, matching release-v4's embedded custody entries. This replaces the earlier statement that the output-manifest hash was still unpinned. It does not freshly verify every crop.

`response_objects` retains `stored_object_path,stored_object_bytes,stored_object_sha256` (the physical object, including archive compression), optional `archive_member,member_sha256`, `original_response_sha256` (historical receipt), `representation=original_json|image_stripped_json|full_gzip|deduplicated_image_reference`, `reconstruction_method/version,reconstruction_input_image_sha256,reconstructed_original_sha256,original_hash_verification=direct|reconstructed_match|unverified|mismatch`. Archive, member, original and reconstructed hashes are distinct fields. Parsing locators bind to stored bytes/member plus representation. A failed/unsupported reconstruction stays explicit and never overwrites either hash.

The bounded legacy probe repeats Astra's witness for `66112e132fd96ac8e30e5328-p000016-l0004`: stored JSON **1,658,567 bytes / `a768ce3f8b8c13e1c2280ae54aa627fa97ed4f5305d54174f061dbf1dbcbd167`**; historical original SHA **`37dd6fabdb39b7d6c38fd73d8bc51c63cd3913376bbe55edbcf8ca9735a3bf5f`**. Restore `document.pages[0].image.content` with base64 of the exact retained PNG, delete `content_stripped`, serialize UTF-8 with `ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False` plus LF: **2,123,357 bytes**, exactly the original SHA. Reconstruction occurred in memory only; no source rewrite. See [probe](../../../out/runner4/RESPONSE_REPRESENTATION_PROBE.json). Apply only the adapter supported by each recorded representation; unknown cases remain unverified.

## 2. Identity, schema and storage

### Identity rules

`row_id` stays byte-for-byte the existing training/source row ID. Its namespace is `parent_id`: **primary key `(parent_id,row_id)`**, with `row_key=sha256(canonical_json([parent_id,row_id]))` as a convenient scalar FK. Never assume globally unique row IDs, join by text, or collapse rows with equal crop SHA. Crop hashes are indexed secondary join witnesses, not row identities. Release keys are already `(parent_id,row_id)`.

`page_id` is a registry scalar derived from `(source_namespace, source_page_id, image_sha256, frame_version)` with a versioned canonical serialization. Preserve literal census and harvest page IDs in `page_aliases`; resolve source book namespaces before joining the older `…-pNNNNNN` IDs. Equal image SHAs identify exact pixel-byte aliases, not automatically equal editions or split assignments. Two source observations can reference one stored raster while retaining different page records. No image path or absent-value zero SHA is an identity. Failed/unrendered page observations use their source identity with an explicit null raster component; their image path/hash/dimensions remain null, never evidence of existing pixels.

`segmenter_run_id` binds name/version, code/model/config SHA, input-page manifest SHA, input raster frame and runtime. `box_id=sha256([page_id,segmenter_run_id,geometry_kind,raw_page_index,raw_line_index,derived_recipe_sha_or_null])`. Geometry changes or a new run produce new IDs. Source array indexes are stable within the pinned raw response; do not renumber them after filtering.

### Core tables

Strings are UTF-8, hashes full SHA256, coordinates/percentages FLOAT64, counts integer, booleans nullable where evidence is missing. JSON fields are typed JSON in DuckDB and canonical JSON strings in Parquet. Null means unknown/unavailable; zero means measured zero.

| Table / key | Columns |
| --- | --- |
| `pages` / `page_id` | `source_namespace, source_page_id, book_id, edition_id, edition_identity_status, provider_item_id, physical_page_number, page_slot, image_path, image_sha256, image_bytes, width_px, height_px, frame_version, source, source_manifest_sha256, source_record_locator, acquisition_status, source_split, split, rights_json` |
| `boxes` / `box_id` | `page_id, segmenter, segmenter_run_id, geometry_kind, polygon_px, polygon_norm, bbox_px(x0,y0,x1,y1), bbox_norm, raw_polygon_px, raw_polygon_norm, reading_order, emitted_item_index, raw_page_index, raw_line_index, line_index_from_top, raw_segmenter_json, response_object_id, response_stored_sha256, response_original_sha256, raw_record_locator, geometry_transform_json, source_box_ids, crop_ids` |
| `rows` / `(parent_id,row_id)` | `row_key, box_id, census_generation, census_disposition, status, usage_scope, reasons_json, reason_codes[], reason_source, decision_sha256, decision_locator, label_raw, label_raw_sha256, raw_text_field, label_corrected, label_corrected_sha256, corrections_applied_json, correction_route_statuses_json, split, source_split, release_memberships[], crop_id, primary_class, source_record_locator` |
| `row_features` / `(row_key,label_variant,feature_version)` | `label_sha256, length_chars, length_raw_codepoints, nonspace_chars, greek_count/pct, latin_count/pct, cyrillic_count/pct, digits_count/pct, punctuation_count/pct, other_count/pct, polytonic_marks_present, numbers_present, all_caps, has_capitals, mixed_script, language_guess, language_guess_method, language_guess_confidence, census_primary_class, source_script_class, crop_width_px, crop_height_px, crop_aspect, x_center_norm, y_center_norm, line_index_from_top, feature_provenance_json` |

Small supporting relations avoid ambiguous arrays where joins matter: `page_aliases(namespace,source_page_id,page_id,source_record_sha256)`, `segmenter_runs`, `response_objects` (§1 response amendment), `segmenter_page_results` (§4), `crops(crop_id,path,sha256,bytes,width,height,page_id,crop_bbox_px,transform_json,recipe_sha256)`, `release_membership(release_id,parent_id,row_id,label_variant,crop_sha256,label_sha256,membership_source_sha256)`, and `box_lineage(derived_box_id,source_box_id,contribution_json)`. Membership/contributor/crop arrays above are views over authoritative relations, not separately maintained copies. Manifest/input records live in the publication manifest. These are provenance relations, not another decision pipeline.

`boxes.geometry_kind` distinguishes **raw_line** from **harvest_derived**. A Google training row may use an envelope/crop assembled from multiple Google contributors or a padded/trimmed crop. Preserve every raw Google box unchanged; create one derived box with `segmenter=google`, the frozen harvest recipe and contributor lineage when required. Each used row references exactly one primary raw/derived box; lineage may reference several raw boxes. Several rows can legitimately reference a box. `crops` describes the actual crop transform/padding/rotation; never overwrite a raw bounding polygon with crop bounds. Missing contributor membership stays explicitly unresolved, not inferred as one-to-one merely from a `-lNNNN` suffix.

Store boxes for all raw lines, even absent from any features/crops/census. Existing excluded source rows retain their existing IDs in `rows` with `status=not_harvested` and no census disposition. A raw box with no source row has **no invented training-row ID**: the `box_registry` left-join view exposes `status=not_harvested`, nullable `row_id` and reason `no_source_row` (registry provenance, not a fabricated census reason). No-OCR pages have zero boxes and an acquisition reason.

### Decisions, labels and split semantics

For the census population map **ADMIT→used, HOLD→held, DROP→dropped**, preserving the original disposition and every reason object/code. Here `used` means census accepted into its dataset scope; `usage_scope=train_candidate|evaluation_diagnostic` makes the scope explicit. It does **not** claim a training job consumed the row. Train ADMIT is 364,180; all-split used is 456,967. Exact release membership is a separate relation, including the 167,946 W1/W2 v4 train members. Future actual training draws can add membership records without changing census history.

`label_raw` comes from the pinned parent's immutable raw field (W old_label precedence as in the census adapter; collection-v2 label), not admission_records.label. `label_corrected` is census `final_text` with ordered edits, normalization and route provenance. Record overlay text/application separately in release membership: v4's base label stays raw even when sf7 is available. Corrections marked failed/not-applicable/out-of-scope/kept_unverified are retained as statuses, not counted as applied edits. Export chooses an explicit label variant, never silently substitutes corrected text.

Page `split` is canonical only when linked row/edition assignments agree; otherwise `mixed` or `unassigned` with the assignments retained. Row split is authoritative for export. Exact-byte page aliases do not move held-out rows into train. Conflicts are diagnostics for the owner, not a new split policy.

### Geometry and feature contract

Canonical page coordinates are on the exact retained image raster, origin top-left, x right/y down, float pixel edges, half-open axis-aligned envelopes. Preserve ordered polygons, including skew. Normalized canonical x/y are pixel coordinates divided by image width/height. Keep provider normalized vertices separately because rounding/scaling can differ. Save any resize, tight-page crop, EXIF rotation or OCR-frame transform and its inverse; do not compare boxes in mismatched frames. `crop_aspect=width/height` uses actual crop pixels; centres use primary box geometry in page coordinates. Reading order is segmenter order; `line_index_from_top` is separately zero-based sorted by `(bbox_y0,bbox_x0,box_id)` within page/run/kind, not a claim about multi-column reading order.

Compute text features for **raw and census_corrected** label variants, with feature/version, Python Unicode database version, codec hash and label hash. Features never mutate the stored labels. `length_chars=len(NFC(label))` including whitespace; also retain raw codepoint length. Six disjoint percentage buckets use **non-whitespace NFC codepoints** as denominator. Letters use the existing codec-aware NFD-base/name script helper (not Unicode-block counting); decimal digits are Unicode `Nd`; punctuation is Unicode `P*` plus codec punctuation atoms (digit before punctuation before script). Everything else, including symbols and remaining combining marks, is `other`. Percentages are 0–100; an empty denominator yields all zero plus `nonspace_chars=0`. Store integer counts so denominators remain inspectable; Greek percentage is not “percent of letters.” Separate census inventory values remain available for its original semantics.

`polytonic_marks_present` checks NFD Greek-base sequences for breathing, perispomeni, iota-subscript or grave (U+0313/U+0314/U+0342/U+0345/U+0300); acute or diaeresis alone does not prove polytonic orthography. This describes marks, not a language/orthography verdict. `numbers_present=(digits_count>0)`; punctuation_count uses the bucket above. `has_capitals` means any `Lu` or `Lt`; `all_caps` requires at least one cased letter and no lowercase cased letter; digits-only is false.

**MEDIUM 3 — named scripts and language.** Percentage script counting is the existing **codec-aware NFD-base/name method**, not Unicode-block counting. Its helper collapses other scripts to `other`; for `mixed_script` retain a separate set of named letter scripts. After the same codec exclusions and NFD-base handling, use codec Grek/Latn/Cyrl identities first, then the version-pinned Unicode **Script property** for other letter bases (`Scripts.txt`, version and SHA in the future feature code bundle). Ignore Common/Inherited and marks; retain Unknown as an explicit diagnostic identity. At least two distinct named identities means `mixed_script=true`. Hebrew+Arabic is true although both enter `other_pct`; Greek+digits is false. The data bundle is a future implementation dependency, not a file downloaded in this step.

Use bound line-level DocAI languages, otherwise page-level, retaining all original language records. Choose the highest finite provider confidence; ties use lexical language-code order. If no confidence is finite choose lexical code order and keep confidence null. Without provider languages use **`script-tag-v1`**: zero named letter scripts→`und`; **two or more→`mul`, regardless of majority or tie**; exactly Greek→`el`, Latin→`und-Latn`, Cyrillic→`und-Cyrl`, other/Unknown singleton→`und`. Heuristic confidence is **always null**. Thus 50/50 and 99/1 Greek/Latin both return `mul`; digits-only returns `und`. Retain provider and heuristic methods separately in provenance. Do not infer a Latin language or Greek historical variety. These diagnostics introduce no admission filters.

### Stable data-root layout and custody

```text
$GREEK_OCR_DATA_ROOT/line_registry/
  sources/<source_snapshot_id>/          # receipted retained pages/raw responses/metadata
  builds/<registry_id>/
    manifest.json                       # schema, code, config, source pins, counts, gaps
    SHA256SUMS                          # manifest and all published artifacts
    pages/batch-*.parquet
    boxes/batch-*.parquet
    rows/batch-*.parquet
    row_features/batch-*.parquet
    provenance/*.parquet                 # supporting relations
    registry.duckdb                     # tables, views, indexes; movable as one file
    checks.json
  work/<registry_id>/                    # resumable batches, not a published registry
  CURRENT.json                          # atomically points to accepted completed build
```

The proposed Clariden data root is **`/capstor/scratch/cscs/fffoivos/greek-ocr-data`**, source snapshot `line_registry/sources/runner4-20261022`; `$W` remains a mapped resident source root. Store portable root-relative asset paths plus source-root mappings, original paths and hashes. Existing trusted crop/page custody can be referenced without copying bytes; transfer missing sources into `sources/` once, preserving originals. Manifest pins source files or archive/member pairs, bytes/SHA, source counts, producing commit where known, builder base/patch identity, config, feature spec and unresolved coverage. Code/configs/receipts belong in Git; images, raw JSON, Parquet, DuckDB and bulk row lists do not. Honor Anemi's internal restriction and all retained source rights in exports.

## 3. Proposed builder and query CLI (not implemented)

One **CPU allocation on Clariden**, 8 CPUs/32 GiB as a starting resource estimate, local workers bounded by page batches. No GPU, Google calls, crop materialization, native detector rerun or model training. The job imports existing geometry and decisions; toolkit inference is a later separately scoped producer.

1. Preflight pins completed census generation, live release/crop receipts, source snapshot manifest and expected source availability. Resolve and record old-page discrepancies. Hash full input files in the allocation; do not assume a historical receipt proves current bytes. Inventory every manifest page including rejected/failed/no-OCR pages, and every raw line before row admission. Check old `(source/book/page)` aliases against image SHA.
2. Stream pinned parent records and the immutable decisions once into a temporary disk-backed keyed join; load metadata/edition/split and release/crop memberships. Do not parse both the 11 GB decision stream and duplicate admitted_train merely to build the same rows. Read admitted_train only for its required reconciliation/check or use bound expected counts plus exact key comparison during validation. Do not copy the mutable 25 GB ledger into the published registry.
3. Process deterministic batches of **100 page records**, sorted by page key. Decode a raw response once per response SHA, import all polygons, derive required harvest boxes/lineage, attach every known row, read crop headers and compute label features. Page batches commit checksummed Parquet via temp-file rename, then record completion in a private SQLite work ledger. A unique raw response can serve several page aliases without duplicate decoding. Compression/archives are decoded once per relevant shard.
4. Resume only completed batches whose checksums, input binding, schema and feature versions match. Interrupted temporary batches are disposable and rerun; conflicting source/code/config gets a new registry_id. Per-page errors retain page/error provenance and incomplete batch state. Preserve the inventory; never silently skip failed pages or turn missing geometry into a zero-area box.
5. Build DuckDB from the validated Parquet once. Check keys/counts/coverage and the fixed feature sample. Publish manifest/checksums and atomically replace CURRENT only for the completed build. An incomplete inspection build may be retained by explicit path with coverage gaps; it must not be presented as satisfying the used-row join acceptance check.

Proposed committed homes: `greekocr/registry/{sources,build,features,query}.py`, a thin `scripts/registry/` entry point/job wrapper, small fixtures/tests, and custody receipts. Design review must precede those additions.

Example CLI contract:

```text
python -m greekocr.registry build --sources <manifest> --census-current <pin> --release-receipt <pin> --out <root> --resume
python -m greekocr.registry query --registry <registry.duckdb> --status held --reason <exact_code> --script-pct greek:80:100 --min-chars 20 --output <subset.parquet>
python -m greekocr.registry export-rows --registry <db> --selection <subset> --split train --label raw --output <row-list.jsonl>
python -m greekocr.registry export-boxes --registry <db> --segmenter-run <id> --bbox-center-y 0.8:1 --output <recrop.jsonl>
```

Query accepts explicit status, split/release, class, length, script percentages, capitals, crop aspect/size and normalized position filters, plus read-only SQL. Default query includes all statuses; a training export requires an explicit split and label variant and preserves source rights. Row lists retain `(parent_id,row_id,crop_sha256,label_sha256,split,registry_id,selection_sha256)`. Re-crop lists retain `(box_id,page_id,page_image_sha256,polygon,bbox,coordinate_frame,recipe,source_box_ids)`; labels are nullable for new boxes. Every export has parameters, counts, source-registry SHA and content hash. Exporting a list neither writes crop bytes nor edits the release.

## 4. Segmenter comparison hook

**MEDIUM 4 — actual deployment export.** Consume the JSON returned by `prototypes/fast_lines/shared/review.py:detector_record` and written by `write_result`: `page`, `image_size=[width,height]`, `unit="line"`, `items[].polygon`, `seconds`, and all emitted item provenance. This serializer removes `discounted` items and clips polygons to page bounds. The comparison population is exactly those retained, clipped polygons; internal pre-export candidates are a different population. Evidence sidecars remain separately identified diagnostics. Pin the serializer SHA with fast-lines/Paddle-first code/model/config/runtime hashes. The run manifest must bind each input raster SHA/frame because the emitted JSON alone lacks that SHA. Retain Paddle/fallback route when present in run/evidence provenance, otherwise null.

Keep one `segmenter_page_results` row per intended `(segmenter_run_id,page_id)` with `input_image_sha256,width_px,height_px,coordinate_frame,status=ok|error|not_run,box_count,result_path,result_stored_sha256,evidence_path,evidence_sha256,error_code,error_json,route,seconds`. An `ok` zero-box page has `box_count=0` and a real result hash/locator. Error/not_run have null counts, explicit outcome provenance, and nullable result locators; preserve failed output objects/hashes where produced. Missing output for a requested input means `not_run`, never zero. Retain retries in the run manifest with the selected attempt explicit. This relation plus the frozen input manifest supplies comparison denominators.

For toolkit boxes add `emitted_item_index` and preserve the zero-based exported `items[]` order in `reading_order`; `line_index_from_top` remains the separate geometric sort. For the shared box-ID serialization, toolkit uses `raw_page_index=0` for its one input page and `raw_line_index=emitted_item_index`; original item fields remain in raw provenance. Name `segmenter=toolkit`. Import creates a new registry build; Google records and row IDs remain unchanged. Census crop-native measurements are not whole-page toolkit output. No toolkit inference is included in this step.

First three analyses:

1. **Overlap per page.** Compare raw Google versus toolkit boxes in canonical pixels, separately from harvest-derived crop boxes. Store sparse candidate pairs with polygon IoU (bbox IoU explicitly marked as fallback), intersection/each-area coverage and centre distance. Report best-match distributions, count differences and one-to-one matches at displayed diagnostic thresholds (0.3/0.5/0.7), plus one-to-many splits/many-to-one merges. Maximum-weight one-to-one assignment does not erase those graphs. Denominator is pages successfully processed by both; list failures separately. A box match is not label truth.
2. **Offsets and sizes.** For matched pairs report signed centre dx/dy in pixels and page-normalized units, width/height ratios and edge deltas; summarize median/tails by page x/y band, source, resolution and script-mix bin. Use raw-row label features through provenance only where a row link exists; unmatched or unlabelled boxes stay a separate denominator. Report tiny/numeric and multi-column regions. Inspect overlays on source pixels to determine whether a systematic difference is shift, clipping, padding or merge/split; IoU alone cannot establish training quality.
3. **Rows lost/gained.** Report used/held/dropped Google-linked rows with no toolkit coverage, toolkit boxes with no Google counterpart, splits/merges and matched rows by release/split. Also compare selected geometry subsets exported for re-cropping. “Gained” initially means a new segment candidate; it is not a newly labeled/qualified training row. New box selections need their own crop/label/admission evidence and IDs; never reuse an existing row_id for changed pixels.

These analyses can identify a useful source/position/script subset for a second segmentation run or alternative crop selection. They do not change any segmentation acceptance criterion or adopt a new segmenter.

## 5. Scale, cost estimates and minimal acceptance

### Verified counts versus estimates

- Census population: **592,466** keyed observations; used **456,967**, held **84,754**, dropped **50,745**. Train used **364,180**; v4 membership **167,946**. Additional pre-census raw rows and raw boxes increase registry scope; they do not increase census denominators.
- Known source line-observation counts: historical **378,279** plus W features **320,479 = 698,758**. This is a sizing baseline from historical receipts and bound snapshots, **not a newly counted total of unique raw Google polygons**: assembly, missing receipts, auxiliary reads and aliases must reconcile in the build.
- Historical read-page observations **6,279** plus W completed **4,621 = 10,900** before cross-source identity reconciliation. Retained physical older native-image files including rescue/prior page reads **8,574**; W cache **5,389** objects. These are different denominators. Final logical pages, editions/books, unique raster SHAs and raw/derived box counts are **unmeasured globally** and must be output by the later allocation; the small probes do not justify invented exact totals. Fresh book-prefix counts are 429 W1/1,087 W2, not unique editions; historical round1 reports 130 books.
- First design sizing: **~0.7–1.0 million raw boxes**, up to **~0.6–0.7 million derived harvest boxes**, about **0.7 million source rows** and up to **1.4 million feature records** for two label variants. A similarly dense second segmenter could add another 0.7–1.0 million boxes. These ranges are estimates, not acceptance targets.

### Bytes and time

Fresh directory/stat counts: old eight-wave image roots **21,575,117,145 bytes**, rescue **522,104,822**, prior page reads **147,327,015**; W cache **4,453,652,987** and W responses **5,489,236,156**. Old `google/docai` custody objects total their per-wave counts in the evidence (about 6.1 GB, including parsed/cache/archived objects); they are a physical upper inventory, not the exact transfer selection. Existing CROPS4C crops add **3.60 GB** but already exist remotely. The resume pins **35,198,780,622 bytes** of missing files and **6,097,473,408 bytes** for provisional remote reuse; see STAGING_PLAN.md for the exact physical selection and hash gaps. This supersedes the initial ~40 GB preparation budget. No automatic transfer or duplication of every derivative is proposed.

Compact scalar tables plus line-only raw JSON/locators: estimate **1–4 GB total published Parquet + DuckDB**, **20 GB temporary working space**. Budget **10 GB published + 20 GB scratch** initially; store full raw page responses once in sources, and refer to verbose census decisions rather than repeating their entire 11 GB in each table. Toolkit import adds roughly 0.5–2 GB per similarly sized run. These compression estimates need measurement on the first real batch.

Six warm local raw-response parses ranged **0.003–0.018 seconds/page** on **0.50–2.30 MB** objects; they exclude source transfer, cold storage, old archive decode, crop headers and Parquet/DB writes. They are not Clariden throughput measurements. For planning, a 30–60 GB metadata/hash/read pass at 50 MB/s is 10–20 minutes; JSON joins/features, crop headers and publication add uncertainty. Allow **30–90 minutes elapsed in one 8-CPU job**, with a proposed **2-hour limit / 32 GiB memory**. Stage source custody first; transfer time is separate. Measure 100-page batches inside the authorized build and revise the estimate before claiming a completion ETA. No cluster resources were requested in this step.

### Minimal acceptance checks for the later build

1. **Custody and count reconciliation.** Pin and verify census CURRENT generation 2 and its immutable exports; reconcile all **592,466** `(parent_id,row_id)` keys and dispositions/reasons by parent/split to the census, not merely the grand total. Reconcile exact v4 **167,946** key/crop/raw-label hashes and **904** registered overlay memberships without applying overlays to the base labels. Reconcile CROPS4C **207,243 = 167,946 + 39,297** selected keys/hashes and per-tranche counts. Source inventories report all page/response/box counts, acquisition failures, missing metadata, aliases and pre-census exclusions, including the known older discrepancies.
2. **Row→box→page and geometry.** Every used row joins to exactly one primary box and one page, with page-image SHA/dimensions and crop SHA/transform consistent with the source; secondary contributor lineage is retained. No foreign-key or duplicate-key failures. Null/placeholder geometry does not pass. Retain unresolved held/dropped joins in a report. Boxes without rows and pages without boxes remain queryable. Sample Google raw/normalized/pixel geometry against the exact page image, covering both old sources and W1/W2, and report any transform or out-of-bounds discrepancy; do not silently clamp the raw record.
3. **Features on 1,000 random rows.** From the sorted complete census keyset, draw 1,000 without replacement with recorded seed `20261022` and sampler/version, preserving the sample manifest. Independently recompute raw/corrected text fields and crop/page-derived features directly from pinned source records/bytes rather than reading the stored feature outputs. Require exact counts/booleans/categories/hash matches and floating agreement within `1e-9`; compare integer bucket sums to denominator. Fixed diagnostic examples additionally cover empty/digit-only, precomposed/decomposed polytonic, Greek+Latin/Cyrillic, capitals and vertical crops. These examples explain feature semantics, not new admission criteria.
4. **Publication and resume.** DuckDB/Parquet return the same key/count results; exported row/box lists round-trip their identity hashes. Interrupt/resume one batch and show equivalent sorted logical table hashes without duplicated rows. All output artifact sizes/hashes appear in the manifest/checksum receipt; CURRENT changes only after the above checks. Keep source identity and coverage limitations visible in the check report.

## Review handoff

Astra should review the four-table contract with supporting provenance, the raw-versus-derived box distinction, the explicit status/label variants, and the source-staging/join gaps against the owner's brief. Owner decides this design and any changes before builder work. Exact global box/page joins remain a build measurement, not an already completed audit. No build, deployment or job submission is included in this handoff.

The resume closes MEDIUM 2–4 in the contract. HIGH 1 remains open pending authorized staging, full byte checks and the three complete raw-Google joins on Clariden. See the staging plan for exact sizes, selected files, missing hash coverage and the stop boundary. No builder implementation is included.

**STAGING PLAN READY**

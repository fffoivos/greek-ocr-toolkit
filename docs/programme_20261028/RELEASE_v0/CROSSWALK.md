# REL0-S4a — draft line-dataset crosswalk, 28 October 2026

Draft for phase (b). Authority: [OWNER_BRIEF.md](OWNER_BRIEF.md) items 3, 5, 6;
[PLAN.md](PLAN.md) rev 2 §3 and §7 steps 4–5; [Astra H01–H03/M04/M07](ASTRA_PLAN_REVIEW.md).
The inherited contract is [HF_REPO_SPEC.md](../../programme_20261019/registry/HF_REPO_SPEC.md),
including its 23 October registry amendment, and its linked
[identity/feature design](../../programme_20261019/registry/LINE_REGISTRY_DESIGN.md).
Only amendments: **licence fields removed everywhere; raw Google payloads stay
private**. Layout renaming, normalized relations represented as typed lists, and
new provenance columns below retain information; they are not permission to drop it.
All destinations are in PLAN §3's table/config families. Additional columns below
make that plan's retention promise concrete for the later builder.

These are source expectations from local documents/code, **not remote probe
results**. No SSH, network, git, HF download or Clariden scan ran here. The saved
prepared005 runtime was read locally and its SHA verified as
`21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4`.
The probe commands and interpretation are in
[COMMANDS.md](../../../scripts/release_v0_dataset/COMMANDS.md).

## Identity, nulls and relation preservation

Keep `(parent_id,row_id)` byte-for-byte. `row_key` is SHA256 of the canonical UTF-8
JSON tuple under the inherited serialization, not a hash of text/image. Public
`id=<release>:<original id>` is a convenience identifier; retain wave where needed
to avoid collisions. A collision requires an explicit mapping record, never an
unrecorded renaming. Aliases connect page observations to shared raster bytes;
equal hashes cannot merge books, editions, splits or observations. No source row
for a box means nullable row ID in the box left join, not a new training row.

The following nested relations are typed `list<struct<…>>`, with their original
keys retained and uniqueness checked after unnesting. They can be expanded by
consumers without losing cardinality. If an implementation uses separate shards
instead, it must add the corresponding table config and manifest entries in the
same build; that is a physical representation change, not a metadata omission.

| HF_REPO_SPEC relation / path | PLAN §3 destination and columns |
| --- | --- |
| `pages/pages.parquet` final logical observations | `tables/pages`: `page_id`, all observation/source/acquisition/split fields below |
| Phase-1 physical page-object index, `provenance/mac/page_objects` and original `pages/pages` | `tables/page_images`: `page_object_id,image,image_sha256,image_bytes,width_px,height_px,original_locator`; `pages.raster_objects[]` links physical IDs; preserve the old tuple-hash index |
| `pages/rasters/*` | `tables/page_images/part-*`: original bytes, including separately marked auxiliary composites |
| `provenance/mac/w_page_observations`, all page/state outcomes | `pages`: each observation and status, including failed/excluded and no raster; source locators below |
| `provenance/mac/google_boxes/*`, `boxes` | `tables/boxes`: all raw and derived boxes, including unlinked/excluded boxes |
| MAC parse/missing-raster/zero results and `segmenter_page_results` | `tables/segmenter_page_results`: `run_id,page_id,status,box_count,result_sha256,locator,error`, requested-manifest identity |
| `page_aliases(namespace,source_page_id,page_id,source_record_sha256)` | `pages.aliases[]`: all four fields; source observation distinct from raster object |
| `segmenter_runs` | `segmenter_page_results.run`: `segmenter_run_id,name,version,code_sha256,model_sha256,config_sha256,input_page_manifest_sha256,frame,runtime`; boxes use run FK; runs with no detections survive |
| `response_objects` and MAC `source_objects` | `page_frames.response_objects[]` and `pages.source_objects[]`: stored/archive/member/original/reconstructed hashes, representation kind, reconstruction verification, historical private locator and public sanitized-record locator/hash; private-only locators explicitly marked non-fetchable |
| Raw Google TARs, raw response/line JSON, embedded response image content | **Amendment: payloads not public.** Preserve hashes, representation metadata and all agreed parsed geometry/text-anchor/orientation/language/confidence/source fields in public tables; no public locator pretends private bytes can be fetched |
| Per-page Document AI dimension/transforms/image/frame evidence | `tables/page_frames`: `page_id,response_object_id,docai_page_index,docai_dimension,docai_transforms,docai_image_metadata,raster_width,raster_height,frame_version,mapping_status,mapping_evidence,transform,inverse_transform,sanitized_record_locator,sanitized_record_sha256` |
| `box_lineage(derived_box_id,source_box_id,contribution_json)` | `boxes.contributors[]` on derived box: `source_box_id,contribution_json`; derived key is containing `box_id` |
| `crops(crop_id,path,sha256,bytes,width,height,page_id,crop_bbox_px,transform_json,recipe_sha256)`; original TARs and exact trainer Parquets | `rows.crops[]`: each field, `variant`, `payload_locator`, `availability_status`, `missing_reason`; source and factory bytes also in real view `image,trainer_image`; preserve original shard/row locator and source-to-factory mapping |
| `rows` | `tables/rows`: every original observation and status/reason, including held/dropped/not_harvested, FKs and membership arrays |
| `label_versions` | `tables/label_versions`: independently keyed raw/census/v4/overlay/factory variants, text/hash/codec and correction provenance |
| `row_features` | `tables/row_features`: `(row_key,label_variant,feature_version)` and complete feature/provenance fields below |
| `release_membership(release_id,parent_id,row_id,label_variant,crop_sha256,label_sha256,membership_source_sha256)` | `rows.release_memberships[]`: retain all seven columns; actual model use additionally in `training_membership` |
| Actual trainer image/label/pool membership | `tables/training_membership`: per-run role, trainer ID, image/label variant, original pool order, sampler/mix/seed/config binding; available/eligible/drawn/selection/evaluation distinct |
| `metadata/book_registry`, v2 authority plus harvest extension, build/source/conflict receipts | `registry/book_registry`: retain original fields/typed aliases/assignments/provenance; source receipts and hashes under `manifests` |
| `metadata/row_instruments` | `tables/row_instruments`: `row_id,kind,list_name,list_sha256,declaration_path`; add resolved `row_key` without replacing original ID |
| Census exact decisions/route/reason evidence | `decisions/decisions.jsonl.gz`: verbatim decision/reason records, source key/generation/locator/hash; input exports are overlapping views, not additional row populations |
| `provenance/sources`, edition/split/source manifests/configs | Sanitized source records in `pages.source_record`/`rows.source_record`, public record locator/hash and `manifests` source pins; preserve every non-licence field needed by this contract |
| Per-item `licence/license/rights_json` and source licence records, synthetic licence, old card licence fields | **Amendment: removed** from every public schema, nested record, card and copied manifest. This never filters source populations |
| Synthetic existing `v5-codec-v2.1/{train,val,reserved}` and provenance | `data/synthetic/<split>` plus `synthetic/RECIPE.json`, `synthetic/BUILD/`, `synthetic/OPS.md`; preserve build-specific membership and all fields below |
| `references/seal04/{raw,corrected}` and images | `tables/references`: `reference_id,instrument,split,row_key,line_id,image_variant,label_variant,payload_locator,label_version,diagnostic_only,exposure_notes,source_manifest_sha256`; exact bytes via real view/crop variants |
| `references/v2_test/{raw,corrected,membership}`, common/full coverage | Same `references`, one membership per view/variant/observation; shared images stored once with all memberships retained |
| `references/validation`, selected mix and existing payloads | Same `references`, validation role/mix/seed/source-shard/ordinal bindings and payload locator; not relabelled as synthetic val |
| Derived `analysis/registry.sqlite` / transport chunks | Optional rebuildable local query cache over authoritative public configs; not a replacement for any relation. If published, inherit cap/chunk/checksum rules from HF_REPO_SPEC |
| Source/release/coverage/artifact/MAC manifests, SHA256SUMS, batch receipts | `manifests/{MANIFEST.json,BUILD_RECEIPT.json,COVERAGE.json,SHA256SUMS}` plus bound receipt records, preserving pins/code/environment/schema/feature versions, counts, portable locators, sorted logical digests and known gaps |

## Field-by-field retention inside the core relations

Names separated by commas in a row map in order unless an explicit rename is
shown. Existing public source text remains text; excluding response payloads does
not remove raw row labels. Raw/corrected/trainer labels are separately selectable.

| Inherited fields | Destination columns |
| --- | --- |
| Page `source_namespace,source_page_id,book_id,edition_id,edition_identity_status,provider_item_id,physical_page_number,page_slot` | `pages` same names; `canonical_book_id` explicit; `page_number_convention` distinguishes slot/scan/printed page |
| `image_path,image_sha256,image_bytes,width_px,height_px,frame_version`, raster/original locator/hash | `pages` same names plus `raster_objects[]`; original paths are historical provenance; `page_images` supplies portable bytes |
| Page `source,source_manifest_sha256,source_record_locator,acquisition_status`, acquisition reason | `pages` same names plus `acquisition_reason,source_record_sha256`; failed/unrendered raster fields stay null |
| Canonical/source split and book fields | `pages` and `rows`: `book_id,canonical_book_id,source_book_id,source_split,split,book_registry_sha256,book_split_labels,book_split_assignment_status,book_split_exportable,harvest_protection,book_aliases_json,split_provenance_json`; real-view `assignment_status` aliases `book_split_assignment_status` |
| Box `page_id,segmenter,segmenter_run_id,geometry_kind` | `boxes` same; view `box_kind=geometry_kind`; run identities above |
| `polygon_px,polygon_norm,bbox_px,bbox_norm,raw_polygon_px,raw_polygon_norm`, original normalized Google geometry | `boxes` same; `coordinate_frame,frame_status,page_frame_id` qualify every coordinate |
| `reading_order,emitted_item_index,raw_page_index,raw_line_index,line_index_from_top` | `boxes` same; view `emitted_index=emitted_item_index,top_index=line_index_from_top`; never sort away emitted order |
| `raw_segmenter_json,response_object_id,response_stored_sha256,response_original_sha256,raw_record_locator,geometry_transform_json,source_box_ids,crop_ids` | `boxes` retains response IDs/hashes, private/public locator distinction, transform and lineage/crop arrays; raw payload amendment applies only to JSON bytes; parsed `text_anchor,orientation,confidence,confidence_scope,detected_languages,language_scope` remain public |
| Row `parent_id,row_id,row_key,box_id,crop_id`, page/source/book/class and geometry projection | `rows` same, `page_id,primary_class,crop_bbox`; source/primary geometry refers to box/frame rather than recomputed crop envelope |
| `census_generation,census_disposition,status,usage_scope,reasons_json,reason_codes,reason_source,decision_sha256,decision_locator` | `rows` same; view `decision=census_disposition,decision_reasons=reasons_json`; ADMIT→used, HOLD→held, DROP→dropped; source rows outside census retain not_harvested |
| `lqb_row,release_excluded_row`, exact names/hashes | `rows` booleans plus `instruments[]` referencing `row_instruments`; absent evidence is not false/no-change |
| `label_raw,label_raw_sha256,raw_text_field,label_corrected,label_corrected_sha256,corrections_applied_json,correction_route_statuses_json` | `rows` original fields, view `raw_text,raw_text_sha256,corrections_applied`; `label_versions` contains each text/field/hash and ordered route outcomes |
| Raw/corrected label IDs, overlay/version bindings, factory `gt_nfd,gt_nfc,label_ids,codec_version` | `label_versions`: `label_version_id,row_key,label_variant,text,text_sha256,raw_text_field,gt_nfd,gt_nfc,label_ids,codec_version,source_locator,source_sha256,correction_bindings,route_statuses`; real view selects an explicit `label_version` |
| Row `split,source_split,release_memberships,source_record_locator` | `rows` same; release membership typed relation above; `release` in convenience view is v4/harvest-20261025/seal04 |
| Feature keys and `label_sha256,length_chars,length_raw_codepoints,nonspace_chars` | `row_features` same, keyed by variant as well as row/version |
| `greek_count/pct,latin_count/pct,cyrillic_count/pct,digits_count/pct,punctuation_count/pct,other_count/pct` | `row_features` same twelve columns; counts partition non-whitespace NFC denominator, digit→punctuation→codec-aware script→other precedence |
| `polytonic_marks_present,numbers_present,all_caps,has_capitals,mixed_script`, named scripts | `row_features` same plus `named_scripts`; polytonic requires specified Greek NFD marks, acute alone insufficient |
| `language_guess,language_guess_method,language_guess_confidence`, provider languages/OCR confidence and scope | `row_features` same plus `provider_languages,language_scope,ocr_confidence,ocr_confidence_scope`; provider highest finite confidence/lexical ties; heuristic script-tag-v1 and null confidence |
| `census_primary_class,source_script_class,crop_width_px,crop_height_px,crop_aspect,x_center_norm,y_center_norm,line_index_from_top,feature_provenance_json` | `row_features` same; provenance includes code/codec/Unicode Scripts.txt version+SHA, label hash, crop variant and frame qualification; unresolved native coordinates yield null native position features |

## PLAN §3 real-field sources by population

V = v4 S1/control/W1/W2; H = harvest W3/W4/W3b-1/W3b-2/W3c-1/W5-1/2/3;
G = Gennadius variant; R = seal04; S = synthetic. “Expected” means a source
adapter exists in code/documents, **availability and coverage await probes**.
Each comma-separated PLAN field in a cell receives the stated expectation.

| PLAN field(s) → authoritative table | V expectation/source | H expectation/source | G expectation/source | R expectation/source | S applicability |
| --- | --- | --- | --- | --- | --- |
| `id,parent_id,row_id,row_key` → rows | S1 subset/shared records plus immutable census/release tuples; bridge not yet proven | release metadata IDs; decisions for parent tuples | same, variant receipt required | suite original line IDs; parent mapping may be unknown | own factory key, no invented census parent |
| `page_id,box_id,crop_id` → rows/boxes | MAC aliases/boxes + resident parents/crops, join pending | metadata/source/page producer records beyond old staging, coverage unknown | variant source/page records, coverage unknown | suite/source records, geometry may be absent | null physical page/box |
| `book_id,canonical_book_id,edition_id` → rows/registry | canonical v2 registry, typed aliases and shared source docs | harvest registry extension + metadata | Gennadius registry extension + metadata | suite edition list/registry | text doc identity only |
| `wave,release` → rows | preserved original wave, v4 release binding | receipt/metadata | variant receipt/metadata | seal04/instrument | synthetic/source build |
| `image,crop_sha256` → real/rows.crops | original paths in subset/build crop map, source custody pending | metadata/file_name/TRANSFER crop hash | same in G variant | original suite PNG/hash | image_png, no physical crop |
| `trainer_image,training_image_sha256` → real/training_membership | prepared005 non_parliament/parliament exact image_png; S1 reuse | prepared005 and factory image_png | same, includes G draw population | prepared seal04_dev/test | prepared synthetic train; other roles separate |
| `crop_bbox,polygon_px,polygon_norm,box_kind` → rows/boxes | parent crop bounds versus parsed raw MAC box; contributor bridge pending | source lineage/producer geometry; metadata alone may be insufficient | same | may be missing; do not infer from a PNG | inapplicable |
| `segmenter,segmenter run id,emitted_index,reading_order,top_index` → boxes/results | frozen source run/response indexes; top index computed with provenance | pipeline/source receipts, no new segmentation | same | may be unavailable | inapplicable |
| `coordinate_frame,frame_status` → page_frames | sanitized dimensions/transforms; 194 historical mismatches are not exhaustive | new page/raster/source frame records | same | qualify only with bound source page | inapplicable |
| `text,gt_nfc,gt_nfd,label_ids,codec_version,label_version,label_sha256` → label_versions | exact prepared payload + raw/census/overlay sources | exact prepared payload + release text | same | raw/corrected suite plus exact consumed label variant | factory payload, no label regeneration |
| `raw_text,raw_text_sha256,corrections_applied,per-route status` → labels/rows | immutable parents, census g2, correction registries; missing route ≠ no change | decisions/producer route records | same | suite and explicit correction overlays | no Google raw text; source/rendered label distinguished |
| `split,source_book_id,source_split,assignment_status,book_registry_sha256,harvest_protection` → rows/registry | registry v2 + subset/shared source split | registry extension + source split | variant extension | reference assignments/roles | factory split only |
| `lqb_row,release_excluded_row` → instruments/rows | exact row lists via original-ID bridge | exact lists, never book-prefix inference | same | exact list match if present | inapplicable unless explicit instrument |
| `decision,decision_reasons,primary_class` → rows/decisions | every g2 disposition/reason; S1 class retained separately | release decisions/metadata | variant decisions/metadata | diagnostic/instrument status; no fabricated census verdict | generator outcome separate |
| `feature_version,NFC length,raw-codepoint length,bucket counts/percentages,polytonic,all_caps,has_capitals,mixed_script,named scripts,language,method,scoped confidence` → row_features | recompute per bound label with pinned Unicode/codec, retain producer features | same | same | same | script/render distributions in own config; text features possible without physical page |
| `crop dimensions/aspect,pixel variant,normalised box centre` → row_features | headers + qualified primary box/frame | same if provenance resolves | same | crop headers expected, page position may be unknown | PNG header; no page centre |
| `provider,source,item` → pages/rows.source_record | archived item/assignment descriptors, W analysis_page.item_record, shared parent records | metadata + source descriptors | G source descriptors | suite origin/source descriptors | source_dataset/doc, not bibliographic invention |
| `edition,volume,source_title,year` → source_record | item records/edition map; exact edition/volume completeness unknown | release source records; per-wave coverage unknown | G catalogue descriptors; coverage unknown | may be absent from suite; trace original item record | text-source manifest if recorded |
| `page,page-number convention` → source_record/pages | physical provider number vs sNNN slot preserved | source page record; convention must be recovered | same | suite origin/page locator if retained | text locator, not scanned page |
| `catalogue_url,manifest_url,source_url,source_record_sha256` → source_record | original source descriptors and public sanitized record locator/hash | `source/` + manifests, coverage unknown | same in variant | suite/source lookup, may be unknown | source-text locator/manifests if retained |
| `trained_in,pool,trainer_line_id` → training_membership | prepared runtime + final run bindings/draw evidence | namespaced `harvest:<wave>:<id>` and same runtime | same | actual selection/evaluation roles, no train claim | source-build role + actual draws, not availability |

Exact-book lookup requires item/catalogue identity plus edition/volume/page
convention when known. A title/year or an opaque source hash alone does not prove
that. For every missing source field retain null, reason and searched locator;
COVERAGE reports field presence by population **and harvest wave/source**, with
known/unknown denominators. Factory-only fields are insufficient for bibliography.

## PLAN §3 synthetic fields and recovery

Apply separately to A12, prepared005 train, and the old registry build's identified
val/reserved. Synthetic has no physical page/box links. Real-population columns
are never populated using a guessed font/book identity. In the V/H/G/R columns
above synthetic-only rendering/generator fields are inapplicable.

| Field(s) | Source and expected presence |
| --- | --- |
| `line_id,reuse_index,split` | Expected factory row columns; publish original role/build identity |
| `factory_build_id,source_build` | Recover from bound build/manifest paths and receipts, not necessarily columns; distinguish a derived content ID from a recorded historical ID |
| `image,image_sha256,width,height` | Existing image_png and width; builder computes exact byte hash/header height, never renders/re-encodes |
| `text,gt_nfd,label_ids,codec_version,script_class` | Expected shard `gt_nfc,gt_nfd,label_ids,codec_version,script_class`; NFC text aliases gt_nfc without changing stored strings |
| `source_dataset,source_doc_id` | Expected factory columns; these alone are not a precise source-text locator |
| `text_source_locator,text_sha256` | Recover from frozen pool/ingest/job manifests if present; **source-text** hash, not a substitute hash of the final cropped/repaired label |
| `font` | Expected font stem in row |
| `font_file_sha256` **or** `font_sha16` | Local build writer records fonts[].sha16; full file SHA only if retained font manifest provides an exact binding; retain sha16 honestly |
| `polarity,bg_type,accent_survival` | Expected row columns |
| `severity,applied_ops,n_ops` | Expected severity 0–3 and ordered operation names/variants; n_ops derived; observed distributions from files, configured distributions from exact recipes |
| `generator_code_sha256,generator_binary_sha256` | Recover independently from producing source/package/binary receipts; today's source map does not prove either historical identity |
| `recipe_name,recipe_sha256,recipe_effective_sha256` | Source filename/name and raw source hash distinct from effective serialized recipe hash; local build_info writer records both hashes and effective recipe content; exact historical source recipe file may need recovery |
| `provenance_completeness,historical_unknown_fields` | Builder derives from per-field search results; each null has reason, searched files+hashes and probe receipt |
| `trained_in` | Exact build/line/reuse/variant membership and final model draw evidence; prepared005 contains only train |
| Earlier spec `seed/job locator`, per-op parameters | Retain if recoverable in `synthetic/BUILD` and per-line origin records; recipe seed is build-level. Local source derives a line seed from line_id/reuse/recipe seed, but historical replay is unproven. No per-line seed/parameter column in inspected shard schema; existing gap remains open |

`synthetic/BUILD` retains codec, source/font/build/job manifests and frozen source
and effective recipes; `OPS.md` retains full observed operation names (including
suffixes), counts and local file:function/hash map. A current source hash cannot
replace an unknown producing binary hash. If val/reserved cannot be tied to exact
builds/codec/payloads, report the unresolved membership before inclusion; never
synthesize replacements or present prepared005 as containing those roles.

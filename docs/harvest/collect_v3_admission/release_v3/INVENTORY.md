# REL3 inventory — 20 October 2026

Read-only inspection; no production processing and no job submission. Remote multi-GB inputs were read only with `head -n 1`; sizes were read with `stat`. Small files were bounded with `head`, and pinned config/source/tool manifest were hashed. The local copies of those three files exactly match Clariden (see `evidence/remote_pinned_shas_and_sizes.txt`). The two config prefix witnesses are deliberately truncated text, not complete JSON.

## Census identity and outputs

CURRENT is completed export `g1-6283e1bcdf124516b599f8028ad910be`, SHA `5ee1c70e980ce62b5b0d10d62eeb61486ac1abf1ead354ed6d95707501b32f39`. Summary SHA `096b18a885f1d6bdced71a9f42e0eeee3cc2b8f61d0ce0eacb26abacbe1402be`. Complete output list and all recorded output SHAs are preserved in `inputs/summary.json`. Census code manifest identifier is `997b7d2ab5a8775b`.

- admitted_train: 7,870,677,512 bytes; SHA `fe955d00af930b90b1d963a0454a4f4cba26de8fd24332ecc6873fd99f42c4f3`.
- admission_records: 10,412,166,460 bytes; SHA `0acfb1c9b6b5a7094313d362925bdded6803e7cd5d12a72d05ccbb1d2a8caeae`.
- Other summary outputs: decisions, evaluation_diagnostics, pending_content_repair, pending_cyrillic, pending_numerics, pending_polytonic. The last is empty. No multi-GB files were copied.

The sampled W1 admitted row and matching admission record are preserved verbatim in `evidence/census_sample_rows.jsonl`. Key: `collect-v3-W1-20261018-0524` / `bsb_poly1850--027215cc6d2a7e8a--s000-l0001`; raw and admitted label `43`. The admission record uses `row_id`; the admitted observation uses `id`. Each carries the same full decision.

## Label formation and provenance

Pinned source witnesses are in `inputs/line_pipeline*.py`.

1. `line_pipeline_sources.py` selects the first string among `old_label`, `text`, `label` for W1/W2, records `raw_text_field`, and keeps it in `raw_text`. In the sampled row that field is `old_label`. Collector `collect_v3/pipeline.py` constructs old_label from the Google text before assembly repair; `vendor/assembly_fix.py` normalizes the import. Here “raw” means this immutable imported line text, not the original Google response bytes. No convention label is substituted.
2. Pipeline decisions start at raw_text. Successful tool edits use raw Unicode-codepoint coordinates with before/after spans; identical edits coalesce with a `tools` list. Conflicting spans HOLD. Registered artifacts bind parent/id/split/crop and raw-text hash, tool version and digest, artifact SHA, parent-manifest SHA and original-record SHA. Split rebinding additionally preserves original binding, source-record SHA, source-artifact SHA and SPLIT2 SHA. `routes` retains the full evidence.
3. The composer then applies NFC and whitespace-only normalization, separately recorded as `normalization={before,after,policy}`. Its version is 0.3. A normalization-only change therefore belongs in the edits-only release file even if the tool-edit list is empty. The builder preserves that record and verifies exact reconstruction; it invents no tool edits.
4. `line_pipeline_census.py` writes admitted_train with `final_text=decision.final_text`, and admission_records with `label=decision.final_text`. REL3 exports this admitted label byte-for-byte. It never uses the observation's older `label` field as the admitted label.
5. Config corrections bind Cyrillic 0.3 and numerics 0.3 releases. Content repair 0.2 has no bound release and no successful edits in the census summary. Dashes are tags only. Polytonic 0.7 is explicitly out of scope, never applied. Summary route totals over all parents: Cyrillic applied 488, numerics applied 47; these are not W1/W2 release counts. Touch counts are computed in the batch job after exclusions.

## Registered versions

Internal entries identify existing named census tools and their pinned manifest/source file. Their original bound correction artifact paths and SHAs are retained from census05_config; split-bound provenance stays on each exported route. Content repair is registered with zero bound artifacts and must not acquire invented edits. Composer is registered because normalization can change the admitted label.

| Name | File | SHA256 | Keying |
| --- | --- | --- | --- |
| cyrillic_0.3 | `inputs/tool_versions.json` | `ed81e3a1b7389c3dd4d29706e5e2ff2b6d0d34fa0648a9587388a25be2725831` | (parent_id,id,split,crop_sha256) + raw_text_sha256; raw codepoint spans |
| numerics_0.3 | `inputs/tool_versions.json` | `ed81e3a1b7389c3dd4d29706e5e2ff2b6d0d34fa0648a9587388a25be2725831` | (parent_id,id,split,crop_sha256) + raw_text_sha256; raw codepoint spans |
| content_repair_0.2 | `inputs/tool_versions.json` | `ed81e3a1b7389c3dd4d29706e5e2ff2b6d0d34fa0648a9587388a25be2725831` | (parent_id,id,split,crop_sha256) + raw_text_sha256; raw codepoint spans |
| composer_0.3 | `inputs/line_pipeline.py` | `9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68` | (parent_id,id,split,crop_sha256) + raw_text_sha256; raw codepoint spans |
| ru1_v3_edits | `inputs/ru1_v3_edits.jsonl` | `4f1a51f5eb80788fb1cdc7a01220c90df028e79711cf0eeec2d0ace2ee42d1d0` | id within collection-v2-train |
| n1_v1_w1 | `inputs/n1_v1_w1.jsonl` | `94fb67c1aab9f2ec3bf5d47bc36508b7e700508cd27391f70ebfc26f8d73230e` | id within collect-v3-W1-20261018-0524 |

The original external registry is snapshotted as `inputs/external_versions.json` from `greek-ocr-toolkit-main-next/docs/records/labelfix/lqb/versions.json`. These two entries have exact SHA matches to their actual artifacts in `greek-ocr-toolkit-secondary/artifacts/`:

- ru1_v3_edits: parent google_raw_v2_import / collection-v2-train; `id`, `label`, `label_parent`. It includes accepted edits plus explicit holds. Its parent population does not become W1/W2 merely because an ID resembles another row. Touch counts join parent AND row ID.
- n1_v1_w1: parent google_raw_w1 / collect-v3-W1-20261018-0524; `id`, `text`, `parent_text`. Sparse artifact has corrected and hold-only records; touch counts separately report changed rows and rows with any record. Neither external overlay is applied by REL3. Hold metadata remains preserved in the original files.

SF7 is **not registered**: `inputs/SF7_RELEASE_RECEIPT.json` records candidate_pre_audit, bound false, file release_edits_only_A.jsonl, SHA `1e3ac3344d0054d8e7639325afdf13826181e6eec10983b7e162b9648c5faf5a`, key line_id/text, parent google_raw_v2_import. The saved final score has 70 correct / 30 pending and failed controls gate. There is no sf7 entry in the snapshotted registry. An audited registered release requires a separately reviewed package revision; this package does not manufacture one.

## SPLIT2, benchmark and crop custody

SPLIT2 edition_map supplies edition membership through member_documents and the census book_id, checked against census edition_id. row_split.jsonl.gz is pinned with SHA `7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82`. Benchmark candidates and readout are copied byte-exact as inputs; their parent/row key sets must agree. Pixel hashes come from the readout, since candidates_v3 contains selection metadata.

W1 full attempt: `$W/crops4_attempts/crops4_c05_w1_full_01`. W2 full attempt: `$W/crops4_attempts/crops4_c05_full_01`. Both upload receipts were absent at inventory time. The separate W2 smoke receipt is ok for 500 crops but is not accepted as a full receipt. Full receipts must say status ok, mode full, checksum exit 0, no failures/mismatches and byte_exact=selected, bound to the same census. The batch job requires manifest/checksum agreement, then reads and hashes each retained crop itself. Existing W1 files alone cannot replace a full CROPS4 receipt.

# census_05 P6 readout receipt

- Job: Clariden 3704844 (submitted by the coordinator), package `bench02_pkg/0019ce4b`, `submit_job.sh readout`.
- Census: `$W/census_05_20261020/attempts/full-split-001` (export g1-6283e1bcdf124516b599f8028ad910be).
- Candidates input: `$W/filter_pipeline_20261018/bench02/census05_draw_v2/candidates.jsonl`, sha256 `70a29c202691584a3382e77505ef56db7b9a0d1347fa5ac2eccc95ac8e9acfe5` (BENCH02K, 3,341 rows).
- Output: `candidates_readout.jsonl`, 3,341 lines, 1,912,766 bytes, sha256 `929e231ce84ace1faa25ffed6b82010c75bc6b105828c3f311e3e5b75c150973`.
  - Remote copy `$W/filter_pipeline_20261018/bench02/census05_readout/candidates_readout.jsonl` has the same sha (lead readback).
  - Fields: parent_id, row_id, crop_sha256, crop_bbox, crop_source_image, raw_text_sha256, final_text, edits.
- Lead checks: the key set and order equal candidates.jsonl (3,341/3,341, same order), 0 duplicates. The job log `readout-3704844.log` is empty (0 bytes).
- The census tags receipt for the extract is `../census05/tags.jsonl.receipt.json` (tags sha256 `8b5fc9d3…f553`, committed in BENCH02J).

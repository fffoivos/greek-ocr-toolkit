# LF2b report — READY

Completed 20 October 2026. Implemented the coordinator ruling and prepared the first production batch. No crop/text reading, readers, RUN_ALL, submission, certificate refresh or .git writes. Clariden operations were authentication, exact-path stat and one read-only tar transfer. No final production benchmark was produced because no production verdicts exist yet.

## Ruling and producer evidence

`prod_finalize.py` partitions by the draw's recorded **rank ≤ quota**, within split/class[/subgroup]; it sorts reserve rows by recorded rank. Quotas are taken from `draw_plan.json` quotas/dev_quotas/subquotas. Subgroups derive from `tags.font_size` and `tags.cyrillic_language`; no row has unknown membership. There is no subgroup reranking: recorded class rank is compared directly with the applicable subgroup quota. Thus the full draw partitions into **2731 in-quota + 610 reserve = 3341**; these are the literal ruling's row counts, distinct from producer aggregate credited totals.

Producer source: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/bench02/bench02_draw.py`:

- Lines 175–181: subgroup quota definitions.
- Lines 279–282: subgroup tags and corresponding internal fields.
- Lines 418–428: edition-fair emission, distinct from rank.
- Lines 512–518: class quotas, per-subgroup overdraw and subgroup field selection.
- Lines 519–522: recorded selection rank and emitted candidate tags.
- Lines 530–535: edition-fair emission and aggregate credited count.

Producer SHA-256: `aa950a88f02b083ce4ffb0739c70183000048b9167f7ca8bf99f50ba9d1faff1`. Draw-plan SHA-256: `8007e93ff170fdf897d4604d5c6bffe5725317cec226ab16f33ecc31c3b0ddb7`. All input hashes and per-group quota/boundary counts are in `partition_receipt.json`. Coordinator ruling supplies the formerly missing membership policy.

Only OK passes. The unchanged `lf1.replace_flagged` supplies the next unused same-source reserve; the wrapper handles fallback within the identical split/class/subgroup and records FALLBACK_SOURCE, or UNFILLED. Every non-OK reserve is marked used and never promoted. Receipts record flag verdict/reasons/where/state, replacement source, and counts per split/class/subgroup/flagged source. Unresolved and VOID_TWICE have separate counters. `prod_map.py` now carries reasons/where through to finalization. The final CLI writes a benchmark JSONL and receipt; production invocation awaits merged verdicts from both batches.

## Transfer and adapter

`ssh -o BatchMode=yes -o ConnectTimeout=20 clariden true` exited 0. Re-stat confirmed **576/2099 W1 present**, **8,017,318 bytes**; 1523 missing W1 were not fetched. W2 was not fetched or re-statted in this tranche. `fetch_w1a.tsv` records exactly the selected paths. FETCH.sh's optional subset TSV and manifest arguments preserve its defaults and use one SSH tar stream. All **576/576** PNG hashes match the readout; **0 mismatches**. No crop was dropped, re-cut or substituted.

Readout: `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/bench02/census05_readout/candidates_readout.jsonl`.

Readout SHA-256: `929e231ce84ace1faa25ffed6b82010c75bc6b105828c3f311e3e5b75c150973`.

Adapter preserves labels verbatim, metadata, split-encoded class, and readout crop binding. Full readout was joined mechanically to the exact subset; no OCR or label judgment. Crops remain in the requested scratchpad `lf1_prod/crops/`. Intermediate candidates and adapted input are under `lf1_prod/`, hashed in `build_input_w1a.receipt.json`. Per-crop local/readout hashes are in `w1a_sha_comparison.json` and the transfer manifest.

## Packs and scanner

Roster: `artifacts/lf1/candidate_contexts_w1a.json`. Packs remain under the existing scratchpad `lf1_packs/candidates/`. Existing SEED, 50-bed slicing, six frozen controls and pack algorithm are unchanged. Optional output roster and context prefix isolate future builds without changing defaults. Batch-specific build receipt: `receipts/candidate_contexts_w1a_build.json`.

Canonical scanner **v4.5.5**, SHA-256 `e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1`, checked every pack with `scan_rollout.integrity`; no errors, no skipped manifests. Every initial directory contains exactly `items.jsonl` and `img/`. This is a layout/integrity check, with no reader rollout or visual content review. Keys and manifests are hashed in roster/layout receipts; manifests bind each payload file.

| Context | Bed | Controls | Cards | Payload bytes |
|---|---:|---:|---:|---:|
| candidate_w1a_00001 | 50 | 6 | 56 | 861,922 |
| candidate_w1a_00002 | 50 | 6 | 56 | 936,326 |
| candidate_w1a_00003 | 50 | 6 | 56 | 831,220 |
| candidate_w1a_00004 | 50 | 6 | 56 | 786,562 |
| candidate_w1a_00005 | 50 | 6 | 56 | 803,068 |
| candidate_w1a_00006 | 50 | 6 | 56 | 886,239 |
| candidate_w1a_00007 | 50 | 6 | 56 | 934,192 |
| candidate_w1a_00008 | 50 | 6 | 56 | 846,515 |
| candidate_w1a_00009 | 50 | 6 | 56 | 757,232 |
| candidate_w1a_00010 | 50 | 6 | 56 | 759,892 |
| candidate_w1a_00011 | 50 | 6 | 56 | 876,045 |
| candidate_w1a_00012 | 26 | 6 | 32 | 515,829 |
| **Total** | **576** | **72** | **648** | **9,795,042** |

Bytes include items.jsonl and PNG files, exclude adjacent manifests and private keys. Repeated frozen-control pixels share a hashed PNG path within each context, as in the delivered builder; cards remain distinct.

## Validation and handoff

**56 tests passed**: 37 original LF1 tests, 9 LF2 tests (obsolete undefined-ruling stop test updated to the binding partition), 9 ruling cases, and 1 batch collision test. Existing replacement hook tests remain unchanged. Tests cover recorded rank boundary, reserve order, same-source preference, recorded fallback/flag reason, blocked non-OK reserves, test/dev and subgroup isolation, unknown-subgroup stop with row ID, distinct unresolved/VOID-twice counts, unique replacement use, and separate batch keys/manifests/rosters. `tests_lf2b.log` records the x86_64 Python 3.11 unittest run. Native arm64 Python initially could not load the installed x86_64 Pillow; rerunning with the LF2 documented `arch -x86_64` interpreter passed. `bash -n FETCH.sh` and `git diff --check` passed. Scanner, frozen controls, LF1 hook and build.py have no code changes. Existing tests refreshed four synthetic scanner receipts; these are mechanical fixture results, not readers.

`PROD_PLAN.md` contains the second batch's exact complement/fetch/adapter/build/scanner commands and finalization on merged contexts/verdicts. Remaining batch: **2765 bed + 336 controls in 56 contexts**. Combined: **68 contexts, 3341 bed + 408 controls = 3749 cards** (separate partial contexts each retain six controls). No production execution is authorized or performed by those documented future commands.

Codex weekly reading: **31%**, 10080-minute bucket, reset **Saturday 23:40 Europe/Athens**, observed **2026-10-20 05:45:14** using the copied one-word meter probe. Evidence: `meter/limit_probe.log`, `meter/probe.QIBc/p1.log`. No reader ran. Prior token-per-card forecast rescales to 33,963,831.19 total tokens for both batches, excluding retries/probes; whole-percentage meter readings do not establish a precise weekly forecast.

## LEAD_COMMIT_PATHS

Only the following task paths are proposed; do not stage unrelated worktree artifacts. Crops, packs and intermediate candidate/build JSONL stay outside git. No commit or index write was made.

- `artifacts/lf1/tools/prod_finalize.py`
- `artifacts/lf1/tools/prod_map.py`
- `artifacts/lf1/tools/build_candidates.py`
- `artifacts/lf1/tools/test_lf1.py`
- `artifacts/lf1/prod/FETCH.sh`
- `artifacts/lf1/prod/PROD_PLAN.md`
- `artifacts/lf1/candidate_contexts_w1a.json`
- `artifacts/lf1/receipts/candidate_contexts_w1a_build.json`
- `artifacts/lf1/keys/candidate_w1a_00001.json`
- `artifacts/lf1/keys/candidate_w1a_00002.json`
- `artifacts/lf1/keys/candidate_w1a_00003.json`
- `artifacts/lf1/keys/candidate_w1a_00004.json`
- `artifacts/lf1/keys/candidate_w1a_00005.json`
- `artifacts/lf1/keys/candidate_w1a_00006.json`
- `artifacts/lf1/keys/candidate_w1a_00007.json`
- `artifacts/lf1/keys/candidate_w1a_00008.json`
- `artifacts/lf1/keys/candidate_w1a_00009.json`
- `artifacts/lf1/keys/candidate_w1a_00010.json`
- `artifacts/lf1/keys/candidate_w1a_00011.json`
- `artifacts/lf1/keys/candidate_w1a_00012.json`
- `artifacts/lf1/prod/fetch_w1a.tsv`
- `artifacts/lf1/prod/crops_w1a.sha256`
- `artifacts/lf1/prod/w1a_stat.json`
- `artifacts/lf1/prod/w1a_stat.stderr`
- `artifacts/lf1/prod/w1a_sha_comparison.json`
- `artifacts/lf1/prod/w1a_layout.json`
- `artifacts/lf1/prod/build_input_w1a.receipt.json`
- `artifacts/lf1/prod/partition_receipt.json`
- `artifacts/lf1/prod/tests_lf2b.log`
- `artifacts/lf1/prod/meter/limit_probe.log`
- `artifacts/lf1/prod/meter/probe.QIBc/p1.log`
- `artifacts/lf1/prod/lf2b_files.sha256`
- `docs/labelfix/spellcheck/LF2B_REPORT.md`

Optional mechanical test refreshes: `artifacts/lf1/receipts/ctx01.synthetic_scan.json`, `ctx02.synthetic_scan.json`, `synthetic_positive_replay.json`, `synthetic_ss4c_void.json`.

LF2b READY: tests 56 passed; ruling implemented; W1 fetched 576/576 (sha match 576); packs 12 contexts (cards 576+72)

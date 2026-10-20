# CQ4F hand-off

Completed offline in `greek-ocr-toolkit-spellcheck` on 19 October 2026 (Europe/Athens). No reader, usage probe, training run, or network call was launched.

## Imported rescan

The source CQ4 bundle was in the sibling `greek-ocr-toolkit-spellcheck-r2cards` worktree. It has been copied into this checkout, with local private-key paths rebound in `contexts.json`. Initial reader directories, manifests, answers, rollout identities, and source worktree remain unchanged. New re-read packs live under this checkout’s `artifacts/cq4/packs/`.

- Canonical scanner v4.5.5: `e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1`. Its helper `replay_literal.py` was copied with it and frozen. Adoption/P1–P3 ruling: SCAN2R6, supplied by the coordinator; this task imports that ruling.
- R2A2 preregistration: `dbac559fe9792a4f7c879f1fc7b08d03c6a82611bbb42ecce1ffd4ae31ccbebc`; exact file copied to `R2A2_PREREGISTRATION.md`. Amendment 1a from the older hand-off is not claimed or authored here.
- Source: `~/Projects/greek-ocr-toolkit-sol-reading/out/scan2/rescan_v455.json`; local byte copy `rescan_v455.json`, SHA256 `984284698934e706e4d698419cda8d94cd4b4409fb30f4b869f2376e7b4fb630`.
- `rescan_ledger.json` holds all 15 v4.5.5 VALID decisions with scanner/preregistration hashes, prior VOID references, rollout/manifest/answer hashes, decoded existing answers, and control-error checks. Detailed adopted audits are in `scans_v455/`, bound by `rescan_evidence_receipt.json`.
- `initial_ledger.json` and original `scans/` retain the v4.4 decisions, including all 15 VOIDs. The three original VALID records retain their original scanner provenance. `valid_answers` overlays only the 15 imported decisions: 18/18 initial contexts, 300 W-CAP slots + 1,205 top-up slots.
- Offline import/revalidation mode: `bash artifacts/cq4/RESCAN_EXISTING.sh` (`workflow.py rescan-existing`). It checks existing rollout/manifest bytes, pack integrity, answer schema/order and ≤1 control error; it launches no reader. Repeated imports must match the existing import exactly.
- Previous re-read ledger, contexts, build receipt, aggregate, truth, quarantine and lead queue are archived under `cq4f_before/`. New re-read ledger is empty. Historical `build_receipt.json` still describes the original build; current provenance is in the CQ4F import and re-read receipts. Original freeze bindings are archived; `cq4f_amendments.json` records code/path/scanner changes, and current `build_hashes.json` additionally binds the import and new pack metadata.

## Built re-read packs

`bash artifacts/cq4/BUILD_REREAD.sh` completed. Conservative trigger unchanged: all unreadable answers and every breathing-only answer. Each pack includes ten verified controls, excluded from target counts.

| Re-read context | W-CAP targets | Top-up targets | Controls |
| --- | ---: | ---: | ---: |
| topup_reread_000 | 0 | 90 | 10 |
| topup_reread_001 | 0 | 90 | 10 |
| topup_reread_002 | 0 | 90 | 10 |
| topup_reread_003 | 0 | 90 | 10 |
| topup_reread_004 | 0 | 87 | 10 |
| wcap_reread_000 | 90 | 0 | 10 |
| wcap_reread_001 | 13 | 0 | 10 |
| **Total** | **103** | **447** | **70** |

Every one of the 18 VALID initial contexts contributes to the re-read phase:

| Initial context | W-CAP targets | Top-up targets |
| --- | ---: | ---: |
| wcap_initial_000 | 38 | 0 |
| wcap_initial_001 | 29 | 0 |
| wcap_initial_002 | 26 | 0 |
| wcap_initial_003 | 10 | 0 |
| topup_initial_000 | 0 | 34 |
| topup_initial_001 | 0 | 34 |
| topup_initial_002 | 0 | 32 |
| topup_initial_003 | 0 | 32 |
| topup_initial_004 | 0 | 33 |
| topup_initial_005 | 0 | 21 |
| topup_initial_006 | 0 | 38 |
| topup_initial_007 | 0 | 40 |
| topup_initial_008 | 0 | 37 |
| topup_initial_009 | 0 | 29 |
| topup_initial_010 | 0 | 32 |
| topup_initial_011 | 0 | 38 |
| topup_initial_012 | 0 | 32 |
| topup_initial_013 | 0 | 15 |

## Validation and coordinator continuation

`cq4f_validation.json`: PASS. Exact 550-slot trigger coverage without duplication, seven pack closures/manifests valid, no new answers, original v4.4 ledger/scans unchanged. Runner pending-pack and usage-stop behavior checked with a mocked probe and subprocess execution forbidden. Aggregation rejects incomplete re-reads before producing outputs. Shell syntax and runner help passed. This validates preparation; no re-read result or current usage measurement is claimed.

Reproduce offline validation with:

```bash
PYTHONNOUSERSITE=1 /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B artifacts/cq4/tools/verify_cq4f.py
```

The coordinator runs, from this checkout:

```bash
bash artifacts/cq4/RUN_ALL.sh --phase reread
bash artifacts/cq4/AGGREGATE.sh
```

The existing runner remains gpt-6.1-sol / medium, with reader network and web search disabled, pre/post usage probes and the ≥78% stop. `AGGREGATE.sh` uses the imported initial decisions and the new re-read ledger. Rebuilding refuses to overwrite existing pack directories.

CQ4F: done | rescan imported 15/15 VALID (v4.5.5) | reread targets: W-CAP 103 top-up 447 in 7 contexts | next: bash artifacts/cq4/RUN_ALL.sh --phase reread

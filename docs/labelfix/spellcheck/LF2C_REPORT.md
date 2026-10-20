# LF2c report — READY

Completed 20 October 2026. Production uses sourcing's explicit v3 fields. Network stayed off; no .git writes, crop display, label judgment, readers, production verdicts, pack rebuilds or final production benchmark. LF2b remains historical evidence; its §A rank rule is superseded.

## Draw identity and counts

Input: `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/bench02/census05/candidates_v3.jsonl`.

SHA-256: `0432c56f75ed1efded00b76e7aeabcc0a2bf9441bfad00e825e4e105006134c2`.

Mechanically verified all 3,341 rows in identical order against `candidates.jsonl`, SHA-256 `70a29c202691584a3382e77505ef56db7b9a0d1347fa5ac2eccc95ac8e9acfe5`. Removing only `quota_scope`, `scope_rank`, `in_quota`, and `overdraw_order` from v3 gives exact row-object equality with the original. No row, label or order was inferred.

| Split | In quota | Reserve |
|---|---:|---:|
| test | 2340 | 468 |
| dev | 453 | 80 |
| Total | 2793 | 548 |

`artifacts/lf1/prod/partition_v3_receipt.json` records both input hashes, equality and per-scope counts. The LF2b partition receipt is preserved and is not used by production.

## Implementation

`prod_adapter.py` defaults to v3 and preserves its explicit fields. Shared validation requires literal Boolean membership, valid scope binding to split/class, positive scope rank, null overdraw order for in-quota rows, positive unique overdraw order for reserves, and unique row IDs/scope ranks. Scope membership comes from `quota_scope`, never from tags. `scope_rank` is validated and preserved but does not select or order rows. No rank/quota derivation or legacy rank path remains; the former tests now use explicit fixtures.

`prod_finalize.py` accepts only literal `OK`. For each flagged in-quota row, it scans reserves by explicit `overdraw_order` within the same `quota_scope`, preferring the same source. If that source is exhausted, the next unused reserve within the scope is recorded as `FALLBACK_SOURCE`; exhaustion is `UNFILLED`. Every flagged line in a zero-reserve scope gets its own `UNFILLED` record. Every non-OK reserve, including absent verdicts, is marked used and never promoted. Replacement records include flag verdict/reasons/where/state, replacement source, scope and explicit overdraw order; unresolved and VOID_TWICE counters remain separate. The unchanged LF1 replacement hook receives only the already isolated, explicitly ordered reserve list.

Finalization no longer accepts `--plan`; its CLI receipt hashes the input draw and verdicts. Adapter CLI receipts record the full `--draw-source` SHA even when adapting a subset, and require the subset to equal the corresponding full-draw rows. The default source is v3. CLI fixture tests verify both receipt hashes and rejection of a changed subset.

## W1 packs unchanged

**Yes: 576 bed rows across 12 contexts remain unchanged**, with 72 frozen controls (648 cards). These are the LF2b packs; no packs were rebuilt.

`verify_lf2c.py` checks the original 576-row adapted input against its LF2b SHA, joins the same v3 subset to the unchanged readout, and compares ordered line IDs and UTF-8 label SHA-256 values. It then checks every bed card's key label and packed `google_text` against the v3 adaptation. All 576 IDs and label hashes match. Each existing key and manifest SHA matches the LF2b roster, and every payload file matches its sealed manifest, including controls. The roster SHA and per-bed old/v3 label hashes are in `w1a_v3_identity_receipt.json`. No label content is printed or assessed.

## Validation and plan

**63 tests passed** under the documented x86_64 Python 3.11 interpreter. Coverage includes explicit membership despite contradictory old rank, explicit reserve order despite contradictory scope rank, same-source preference, fallback, non-OK and missing reserve verdicts, zero-reserve exhaustion for every flagged row, test/dev and subgroup isolation, unique replacement use, malformed/missing fields, flag reasons, unresolved/VOID_TWICE counters and both CLI receipt paths. Existing build/scanner fixtures also pass. `git diff --check` passed with optional locks disabled; no index or commit write was made.

Reproduce offline:

```bash
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B artifacts/lf1/tools/test_lf1.py
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B artifacts/lf1/tools/verify_lf2c.py
GIT_OPTIONAL_LOCKS=0 git diff --check
```

`PROD_PLAN.md` now uses v3 for the remaining batch, preserves full-source provenance for subset adaptation and removes the obsolete plan argument from finalization. Future transfer/reader/finalization commands in that plan were not executed. No production verdicts exist in this task, so no final production benchmark is claimed. Test execution refreshed the four existing synthetic scanner receipts; these are fixture outputs, not reader results.

## LEAD_COMMIT_PATHS

Commit only these LF2c paths; no staging or commit was performed:

- `artifacts/lf1/tools/prod_adapter.py`
- `artifacts/lf1/tools/prod_finalize.py`
- `artifacts/lf1/tools/test_lf1.py`
- `artifacts/lf1/tools/verify_lf2c.py`
- `artifacts/lf1/prod/PROD_PLAN.md`
- `artifacts/lf1/prod/partition_v3_receipt.json`
- `artifacts/lf1/prod/w1a_v3_identity_receipt.json`
- `artifacts/lf1/prod/tests_lf2c.log`
- `artifacts/lf1/prod/lf2c_files.sha256`
- `docs/labelfix/spellcheck/LF2C_REPORT.md`

Optional synthetic receipt refreshes: `artifacts/lf1/receipts/ctx01.synthetic_scan.json`, `artifacts/lf1/receipts/ctx02.synthetic_scan.json`, `artifacts/lf1/receipts/synthetic_positive_replay.json`, `artifacts/lf1/receipts/synthetic_ss4c_void.json`. Existing W1 keys, manifests, roster and build receipts need no changes. Unrelated worktree artifacts are outside this handoff.

LF2c READY: tests 63 passed; v3 in-quota 2340/453 reserve 468/80; W1 packs unchanged yes

# LF2 production preparation — STOPPED at undefined finalization

Built 2026-10-20. No crop fetch, production crop reading, reader launch, submission, certificate renewal or .git write. Only Clariden authentication and read-only stat calls ran remotely. A one-word weekly meter probe ran locally. Accepted LF1 builder, scanner, runner, controls, prompt and replacement hook remain unchanged.

Prepared [lead plan](../../../artifacts/lf1/prod/PROD_PLAN.md), [adapter](../../../artifacts/lf1/tools/prod_adapter.py), 3341-row [fetch list](../../../artifacts/lf1/prod/fetch_list.tsv), unexecuted [FETCH.sh](../../../artifacts/lf1/prod/FETCH.sh), terminal-attempt [mapper](../../../artifacts/lf1/tools/prod_map.py), and [finalization stop entrypoint](../../../artifacts/lf1/tools/prod_finalize.py). Readout schema is from producer lines 587–610; no real readout was consumed. Input draw SHA-256 matches `70a29c202691584a3382e77505ef56db7b9a0d1347fa5ac2eccc95ac8e9acfe5`; 3341 rows, 2808 test/533 dev, 2099 W1/1242 W2. `line_id=row_id` is unique. Class encoding is `split|class`; original class remains `draw_class`.

**Finalization stop:** producer lines 512–515 define targets, 519–522 selection ranks, 530 edition-fair emission, and 534 aggregate credit. Line 575 describes both orders but never identifies in-quota rows or orders a replacement reserve. Neither draw_plan nor V2 report supplies that definition. Under the explicit owner instruction to stop this part, no rank/file-order policy was added. No final benchmark list or production flagged/REPLACED/UNFILLED receipt was generated. The future wrapper remains unimplemented pending that producer definition; `prod_finalize.py` writes an explicit stop receipt and exits nonzero.

**Availability:** `ssh -o BatchMode=yes -o ConnectTimeout=20 clariden true` exited 0; no auth error or renewal. Listed-path stat found W1 **576/2099 present**, **8,017,318 measured bytes**, W2 **0/1242 present**. All exact paths/results are in `remote_stat.json`; no alternate-path inference or crop fetch. W1 absence differs from the input expectation and blocks a complete fetch now. W2 estimate 17.287 MB; full crops estimate 46.503 MB. Crops + pack copies + typical dry-run zooms + items estimate **298.097 MB**, excluding retries/logs/overhead, versus 1678.561 MB available at measurement. Estimates extrapolate only 576 present W1 PNGs and are not upper bounds. Details and assumptions are in `capacity.json` and PROD_PLAN.

**Build qualification:** full chain adapter → unchanged build_candidates → canonical scanner integrity/layout passes on a synthetic 51-row fixture with temp BASE and PACK_ROOT under the authorized scratchpad pack root. Fixture split is 50+6 then 1+6. Temporary fixtures were removed after tests. Real `artifacts/lf1/candidate_contexts.json` was not created. Expected production is **67 contexts, 3341 bed + 402 control = 3743 cards**, final context 41+6; 50+6 unchanged.

**Validation:** x86_64 Python 3.11, `-B -m unittest discover -s artifacts/lf1/tools -p test_lf1.py -v`: **46 passed** (37 original + 9 LF2). `bash -n artifacts/lf1/prod/FETCH.sh` passed. Tests cover joins/count errors/duplicates, verbatim labels, parent-qualified fallback, complete unique fetch inventory/tranche paths, fixture chain, terminal mapping/unresolved/VOID-twice, test/dev hook isolation and explicit finalization stop. Existing initial-layout test now checks the sealed manifest for initial `items.jsonl`/`img` layout and retains scanner live-integrity checks: the delivered dry-run directories now contain authorized `answers.jsonl` and `zoom`, so an assertion of pre-reader live directory state was stale. Scanner and production behavior were not altered. Existing synthetic scan tests refresh their two mechanical scan receipts.

**Forecast:** dry-run ledger measured 905943.75 tokens/100 cards → 33,909,474.56 tokens for 3743 cards, excluding retries/probes. Weekly probes 34→34 and 34→34 imply 0 **observed** pp/100 at whole-pp meter resolution; they do not establish zero consumption or a precise forecast. LF2 probe returned **31% weekly** at 05:38:46 local (10080-minute Codex bucket, reset Sat 23:40). No reader ran for LF2. The probe script was copied into this worktree so its probe/log writes respect the task's write boundary.

## LEAD_COMMIT_PATHS

- `artifacts/lf1/tools/prod_adapter.py`
- `artifacts/lf1/tools/prod_map.py`
- `artifacts/lf1/tools/prod_finalize.py`
- `artifacts/lf1/tools/test_lf1.py`
- `artifacts/lf1/prod/FETCH.sh`
- `artifacts/lf1/prod/fetch_list.tsv`
- `artifacts/lf1/prod/PROD_PLAN.md`
- `artifacts/lf1/prod/input_receipt.json`
- `artifacts/lf1/prod/remote_stat.json`
- `artifacts/lf1/prod/remote_stat.stderr`
- `artifacts/lf1/prod/capacity.json`
- `artifacts/lf1/prod/tests.log`
- `artifacts/lf1/prod/meter/` (copied launcher, one-word probe logs and limit_probe.log)
- `docs/labelfix/spellcheck/LF2_PROD_PREP.md`

Existing `artifacts/lf1/receipts/ctx01.synthetic_scan.json` and `ctx02.synthetic_scan.json` may be refreshed by the original tests; review as mechanical receipts, not new reader runs. No commits were made.

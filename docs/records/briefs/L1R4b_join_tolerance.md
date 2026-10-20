# L1R4b — L1R4 join: float32 mean tolerance 2e-7 → 1e-6, witness test, redeploy (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-l1f`, branch `opus/spellcheck-l1f`, head = the L1R4 package 73921e7d + this
brief). No `.git` writes; no other worktree writes. Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`,
`PYTHONPATH=$PWD`. **DO NOT SUBMIT**: fix, test, mock, deploy, sha-check; the coordinator runs `--test-only` and submits. SSH transient errors
retry ≤ 3 with backoff; auth/cert error STOP; never refresh the cert (valid to 19:18 today).

## Why (coordinator ruling, 17 Oct 08:41)
L1R4 job 1 (3680767) FAILED in `scripts/labelfix/clariden/l1r4_join.py: validate_record` with `ValueError('L1F invalid actual scores/native
width')` (log `…/labelfix_l1_20261017/l1r_sf6f/logs/L1R4_3680767.log`). A read-only scan of all 124,669 L1F rows (job 3680752) shows that
every check passes except `math.isclose(sum(frames)/len(frames), confidence, rel_tol=0, abs_tol=2e-7)`, which fails on 17 rows by gaps of
2.26e-7 to 2.48e-7. The cause is the GPU's float32 mean, versus the float64 mean taken here. The maximum gap over all rows is 2.4812e-7, and
no row exceeds 1e-6. The 17 rows (all fields, plus the gap) are in
`artifacts/labelfix_l1r4/l1f_17_tolerance_witnesses.json`, together with the whole-population figures (`rows`, `max_gap`, `above_2e7`,
`above_1e6`).

## Change (exactly one)
In `validate_record`, change `abs_tol=2e-7` to `abs_tol=1e-6`, and add a one-line comment that the line confidence is a float32 mean.
Change nothing else in `l1r4_join.py`. The gate (`greekocr/labelfix/release_gate.py`) and `ctc_align.py` must stay byte-identical to
d893a04d; show both hashes. Leave `l1f_mock_check.py` alone (L1F is closed).

## Witness test (in `tests/labelfix/test_l1r4.py`; inline the 17 rows as data in the test, no new fixture file)
- All 17 rows pass the score/width/mean predicate at 1e-6, and each fails it at 2e-7. Extract the predicate into a small module-level helper
  in `l1r4_join.py` so the test can call it, with identical semantics.
- The population figures from the witness file are asserted as recorded constants: max gap < 1e-6, 0 rows above 1e-6.
- A synthetic row with a gap of 2e-6 is still refused, so the check still catches a real inconsistency.
- All labelfix tests stay green, and none are weakened.

## Mock, deploy
Rerun the package's two-job local mock as in `docs/records/labelfix/spellcheck/clariden/L1R4_REPORT.md` (parity 256/256 expected). Redeploy to the same
`…/labelfix_l1_20261017/l1r_sf6f/`, keeping `logs/` (the failed log stays). Regenerate `L1R4_DEPLOY_SHA256.txt` and the deployment evidence
under `docs/records/labelfix/spellcheck/clariden/L1R4_evidence/`, then sha-check remote vs local. Before submission, run the remote join-only preflight on
the real L1F output (join validation over all 124,669 rows, no composer) if it is ≤ 5 min on the login node; else state that and skip it.

## Deliverable
Your final message (do not edit L1R4_REPORT.md): the changed files, test count, mock parity, deploy sha256 local/remote, join preflight
result, and the exact two plain submission commands, with job 2's `--dependency` removed. The coordinator submits job 2 only after job 1
completes. Last line:
`L1R4b READY: join tolerance 1e-6 (float32 mean); witnesses pass 17/17 at 1e-6, fail 17/17 at 2e-7; gate sha <a> = d893a04d; tests <n> passed; mock parity <p>/256; deploy sha256 <k>/<k>; join preflight <ok n/124669 | skipped>`.

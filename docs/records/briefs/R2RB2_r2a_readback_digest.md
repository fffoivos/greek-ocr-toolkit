# R2RB2: readback of R2a + DEV job 3683130, then the R2a digest (gpt-6.1-sol, medium; network ON for Clariden only; no .git writes; no submission)

Workspace: THIS worktree (`opus/r2-prep`, package commit ee9d7a975, verify receipt a0ec0c1f4).
Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`.

**Cert:** the current one expires 19:18 Athens. Do the readback FIRST.
- Never refresh it.
- An auth or cert error means STOP and report "READBACK BLOCKED: cert". The lead re-launches after the owner's refresh.
- On transient SSH errors, retry up to 3 times.

**The job:** 3683130 `labelfix_R2a` (COMPLETED ≈17:24 Athens, exit 0:0, elapsed 23:29 vs 53.4-min forecast).
- Root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2a_20261017`.
- Output: `output_3683130/`.
- Read the job state and its log first. A FAILED state is not a failure until the log is read; report the log tail.

## 1. Readback (the cert-critical part)

Use the readback template the package built (`scripts/labelfix/r2_readback_verify.py`, whose commands are in
`docs/records/labelfix/spellcheck/R2/R2A_PACKAGE_REPORT.md`).

Pull:
- all stage receipts and DONE markers, plus logs;
- the R2a `best.pt` for seeds 20261016/17/18, with their train logs and receipts;
- every prediction and score file for held-out, T4 witnesses and DEV, for all six arms;
- the overlay receipt.

Nothing else: no crops, windows or shards.

Destination: `artifacts/labelfix_r2/output_3683130/`. Verify every sha256 against the receipts and write `READBACK_RECEIPT.json`. Any
mismatch means STOP.

## 2. Digest (local, Mac CPU): `docs/records/labelfix/spellcheck/R2/R2A_DIGEST.md`

The first line states the accepted deviation verbatim: "R2a admits 1,572 print-checked slots against the plan's 4,000; per-slice deficits
recorded in B6_RESOLVE_REPORT.md; top-up reading paused by the owner (17 Oct)".

**Scorer:** R2S (inserted slots UNKNOWN), with overlay v1.1 applied symmetrically.

Arms: R1-A s16, BASE s17/s18, R2a s16/s17/s18.

**(a) Timings** per stage vs the 53.4-min forecast.

**(b) R2a target benefit** on the T4 witnesses (plan pass criteria, R2_PLAN_20261017.md §"Pass criteria"):
- false target additions on capital / ο / subscript-negative witnesses: R2a vs BASE, per seed and pooled;
- net wrong target slots;
- a document-cluster bootstrap 95% interval for the reduction;
- positive strata preserved (per-slice recall);
- the criterion: ≥ 30% fewer false target additions; ≥ 5 net fewer wrong slots; interval excludes no improvement; benefit in ≥ 2 of 3
  seeds with a positive mean.

**(c) Common-class noninferiority** on held-out (classes with ≥ 200 support): P lower bound > −0.20 pp and R > −0.50 pp, Holm-controlled.
Sparse classes are labelled "unestablished", with every paired regression listed.

**(d) Non-target protection:** the same margins on non-target witness slices. Every regression on a preserved owner witness is listed
with line id.

**(e) DEV** (600 lines, 1,793 items): per-arm accuracy on the S8 DEV truth; paired R2a vs BASE.

**(f) Seed spread:** R2a vs the BASE seed spread from job 1 (P 0.13, R 0.54, F1 0.35 pp). Churn: slots that change between BASE and
R2a, by slice.

**(g) Verdict line:** PASS / FAIL / INCONCLUSIVE for R2a target benefit and for each protection check. "Inconclusive" does not adopt.
Write summary sentences no stronger than the table rows.

Paired per-item ledgers go in `docs/records/labelfix/spellcheck/R2/evidence/r2a/` (json). Tests: run the r2 suite.

Last line: `R2RB2 READY: readback <files> sha ok; R2a target false additions BASE <n> → R2a <n> (<pct>, CI <..>); seeds benefit <k>/3; noninferiority <pass|fail list>; DEV <a>→<b>; verdict <PASS|FAIL|INCONCLUSIVE>`.

Note: `failed_output_3682401/` on the remote root is the archived failed first run. Never pull from it or score it.

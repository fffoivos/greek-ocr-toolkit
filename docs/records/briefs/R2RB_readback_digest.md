# R2RB: readback of R2 job 3681404 (BASE + teacher export) and the first digest (gpt-6.1-sol, medium, network ON for Clariden only)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-r2prep`, branch `opus/r2-prep`, head 17f913a0f + this brief).
- No `.git` writes.
- Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`.
- **The certificate expires 19:18 Athens today.** Do the readback FIRST, and finish it before 18:30. Never refresh the cert;
  auth/cert error = STOP. SSH transient errors: retry ≤ 3.
- **No submission of any kind.**

Job 3681404 COMPLETED 11:50 Athens, exit 0:0, elapsed 34:46. Output:
`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/output_3681404/`.

Read `docs/records/labelfix/spellcheck/R2/R2P_REPORT.md` ("Coordinator handoff", "R2P2 population binding") and `docs/records/labelfix/spellcheck/R2_PLAN_20261017.md` §4.

## 1. Readback (the cert-critical part)

Pull **receipts, exports and the BASE checkpoints only**:
- every stage/chunk receipt and DONE marker;
- the teacher exports for all four roles (`*-train.jsonl.gz`, `*-validation_reserve`, `*-witness`, `*-calibration`) plus alignments;
- BASE `best.pt` for seeds 20261017 and 20261018 plus their train logs, receipts and any held-out prediction files the job wrote;
- logs.

Nothing else (no windows, crops or training shards).

Destination: `artifacts/labelfix_r2/output_3681404/`.

Verify **every** pulled payload's sha256 against the stage/chunk receipts. Write `artifacts/labelfix_r2/output_3681404/READBACK_RECEIPT.json` with: file list, sizes, sha256, receipt match yes/no, total bytes, pull start/end time.

If anything fails verification, STOP and report.

## 2. Digest (after the readback; local; Mac CPU)

`docs/records/labelfix/spellcheck/R2/R2_JOB1_DIGEST.md`:

**(a) Timings:** per stage (A–C) from the receipts vs the 74-min forecast (teacher reference 18.9 min, training reference 30 min). Measured throughput: training draws/s per seed, teacher lines/s and slots/s.

**(b) Teacher-export inventory per role:**
- lines and slots;
- the probability fields present (all four heads, full softmax, margins), checked on every row, with counts of missing or invalid fields;
- validity counts (clipped top/bottom, window outside image, span implausible, localisation unknown);
- `teacher_seen_document` counts;
- confidence distribution per head: p(top) ≥ 0.99 and margin ≥ 0.20 shares, per role and source family.

**(c) BASE vs saved R1-A, continuity instrument on the 666:**
- Use the R2 scorer's continuity column (`scripts/labelfix/r2_score.py`), which reproduces R1-A's published numbers, and the job's held-out predictions if it wrote them.
- **If the job did not write held-out predictions,** run BASE inference locally on the frozen held-out windows (`artifacts/labelfix_r1/heldout_font`, about 11k windows; tiny model; CPU, ≤ 4 threads). This is the only inference allowed. State it in the digest.
- Report per seed (17, 18) and the saved A (16):
  - mark P/R/F1;
  - per-class precision/recall;
  - compounds, capitals, subscript, dialytika;
  - the paired old-right/new-wrong ledger vs A with counts.

  This is the **BASE seed spread**: the noise floor the plan's non-target criterion compares against.
- Apply truth overlays v0, v1 and v1.1 (`truth_overlay_v1_1.json`) symmetrically, and report both the without-overlay and with-v1.1 columns.

**(d) Raw four-head metrics** on the same 666: exact named confusion, composed-tuple accuracy, and the four-head result beside the
historical continuity recall.

**(e) DEV (S8 DEV truth, `~/Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8_DEV/evidence/dev_truth.jsonl.gz`):**
- Score BASE seeds and A only if their predictions on the DEV lines can be produced from data already local or pulled in §1, without
  new extraction.
- Otherwise write "DEV pending: needs window extraction on Clariden for N lines", with the exact list and a proposed one-stage job spec.
- Do NOT submit anything.

Tests: any new code is tested; all labelfix tests stay green.

Last line:
`R2RB READY: readback <files>/<bytes> sha ok <k>/<k>; stages A <m> B <m> C <m> min vs forecast 74; teacher rows <n> (train/val/witness/calib); BASE F1 s17 <..> s18 <..> vs A <..>; seed churn <n> slots; DEV <scored|pending>`.

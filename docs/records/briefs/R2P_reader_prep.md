# R2P: R2 reader preparation. Seeds, manifests, teacher export, scorer, truth overlay, Clariden package (gpt-6.1-sol, medium, network ON for Clariden only)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-r2prep`, branch `opus/r2-prep`, head = R2 plan 52f34de9).
- No `.git` writes, and no writes outside this worktree.
- Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`.
- **DO NOT SUBMIT anything to Clariden:** prepare, mock, deploy, sha-check, `sbatch --test-only`. The coordinator submits after the owner
  refreshes the certificate.
- The certificate is valid until **today 19:18 Athens**. Never refresh it. Auth/cert error: STOP. SSH transient errors: retry ≤ 3 with
  backoff.
- If deployment would slip past ~18:30, finish everything local and report the deploy as pending.
- **The frozen release gate is untouched:** `greekocr/labelfix/*` byte-identical, verified with `release_gate.policy_binding()`.
- Read `~/.claude/skills/optimize-apertus-cscs/SKILL.md` "Clariden operating rules", and the R1 package
  (`docs/records/labelfix/spellcheck/clariden/R1_REPORT.md`, `scripts/labelfix/clariden/r1_*.py`).

Spec: `docs/records/labelfix/spellcheck/R2_PLAN_20261017.md` §0, §1, §3, §4, §6, §7, and
`docs/records/reviews/astra_program_review_2026-10-06/ASTRA-R2design_review_1.md` §2–§5.

## Recipe identity (binding)

R2 binds to arm A of job 3678928 as recorded in `docs/records/labelfix/spellcheck/clariden/R1_result_3678928/run_receipt.json`: balanced,
none 0.40, rare min 0.05, capped inverse-frequency head weights, 15 epochs, AdamW lr 1e-3, weight decay 0.01, batch 512, bf16, 64-d
embedding, window 1.5/0.75, best checkpoint by natural validation loss, seed 20261016.

**Disclose every parameter vs that receipt in a table.** Any difference other than the seed and the manifest is a defect.

## Work

1. **Seeds.**
   - Expose the model and sampler seeds in `r1_train.py` / `r1_run.py` (`--seed`, `--sampler-seed`). The document split stays frozen.
   - Default behaviour must be byte-identical to job 3678928's code path.
   - **Test:** with the default seed, the first 200 sampled batch indices and the initial weights are identical to the current code.

2. **Manifest training.** A JSONL manifest per slot with:
   - `slot_id` = (crop sha256, recogniser NFD start), `line_id`, `doc`, `source`;
   - `provenance` ∈ {old, native_print, pseudo, override};
   - four-head targets; an optional `unknown` heads list (quarantined, i.e. excluded, in this round);
   - `loss_weight`, and `replaces` / `removes` records.

   **The trainer:**
   - Reads the old pool as `provenance=old`, weight 1, from the existing extraction.
   - Applies replacements once (never appends duplicates).
   - Multiplies the provenance weight with the unchanged per-head class weights.
   - Logs unique counts, realised draws and effective loss mass per provenance and per head.
   - Old-pool-only manifest = **identical training to the current code** (test on the mock).

   **New native slots** need window extraction: the same `r1_extract`/`r1_pixels` geometry, recogniser spans from a recogniser alignment
   of the new lines.

3. **Teacher export** (frozen R1-A, `artifacts/labelfix_r1/output_3678928` A best checkpoint, hash-verified).
   - Inference over a slot list writes per slot: all four heads' full softmax probabilities, top and top-minus-second margins per head,
     crop validity (clipped top/bottom, window outside the image, span plausibility), teacher checkpoint sha, code sha, input hashes.
   - **Pipeline for new lines** (W1 admitted Greek strata; v2 train monotonic outside C1): recogniser alignment with the existing
     `ctc_align.Recognizer` exactly as L1 used it (same checkpoint, preprocessing, codec) → slot windows → teacher. All of it runs in the
     Clariden job, never on the Mac beyond the mock.
   - **Population input:** a line list file. The lead supplies the eligible W1/v2 line ids from the R2C document roles: ALL eligible
     documents, but the validation-reserve documents are marked and exported separately.

4. **Scorer** (`scripts/labelfix/r2_score.py`).
   - Union of print and prediction slots under mark-blind, case-preserving base alignment: unmatched printed positives = FN, inserted
     predicted positives = FP.
   - Exact named confusion per head/value: acute/grave/circumflex, psili/dasia, subscript, dialytika-only and dialytika+acute separate.
   - Composed-tuple accuracy, all and marked.
   - TP/FP/FN/TN with denominators, false additions per 1,000 negative opportunities.
   - UNKNOWN / coverage / localisation / fused / clipped state counts.
   - Per source/book macro and micro.
   - The old physical-slot instrument as a separate continuity column, reproducing R1-A's published numbers exactly (test).
   - The four-head result shown beside the historical recall, which includes 206 apostrophe FNs.
   - **Paired mode:** old-right/new-wrong vs old-wrong/new-right ledger, document-cluster bootstrap intervals with inclusion weights.
   - **Second output:** the fixed correction-pipeline view, i.e. additions/substitutions accepted under one frozen policy for both
     checkpoints. Reuse the existing gate composition read-only; no gate edits.

5. **Versioned truth overlay** for the 39-card key (`docs/records/labelfix/spellcheck/R2_evidence/reader_errors_39.json`).
   - Overlay files `truth_overlay_vN.json` (id, previous tuple, new tuple, source, date).
   - v1 contains the owner's note on `384c3f89-p000059-l0013:s33` ("this is circumflex actually"), marked
     `pending_full_tuple_readjudication`: the accent is circumflex, the breathing is unresolved until tranche (6).
   - The scorer applies an overlay symmetrically to baseline and candidate, and reports both overlay versions.
   - **Never edit** the frozen `print_truth_s0.json`.

6. **Clariden package** for the FIRST submission, BASE + R2a + teacher export, with R2a switchable off because its manifest depends on
   the cards:
   - `r2_job.sbatch`: one node, 4 GH200, account a0140, normal partition, time from the forecast + 50%.
     - Stage A: verify inputs/hashes.
     - Stage B: teacher export over the supplied line list (alignment → windows → teacher).
     - Stage C: BASE seeds 20261017/18 on the frozen old pool, in parallel GPUs.
     - Stage D (only if an R2a manifest file is present and hash-bound): R2a seeds 20261016/17/18.
   - Per-stage receipts. Resume-safe.
   - Deploy to `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/`.
   - `R2_DEPLOY_SHA256.txt` local vs remote, `sbatch --test-only`.
   - **Mock on the Mac** (CPU, ≤ 64 lines, ≤ 50 steps) through the exact entry point.

## Tests

All labelfix tests green, none weakened. New tests for: seed default identity, manifest identity (old-pool-only = current), replacement
semantics, teacher export fields, scorer reproducing R1-A's continuity numbers, union-alignment FN/FP accounting on synthetic cases, and
overlay symmetry.

## Deliverables

- `docs/records/labelfix/spellcheck/R2/R2P_REPORT.md` with: the recipe disclosure table; the submit command; the pull commands (receipts and
  exports only); the throughput × draws compute forecast, with Stage B measured on the mock; the deployment list.

Last line:
`R2P READY: recipe identical to 3678928-A except seed/manifest <yes|no>; tests <n> passed; mock stages A–D <ok>; deploy sha256 <k>/<k> (or pending); test-only <out>; forecast <min> min`.

# R2J2: the R2a + DEV cluster package (template B1): build, mock, deploy, sha, test-only; NO submission (gpt-6.1-sol, medium, network ON only for the CSCS deploy/sha/test-only steps)

Workspace: THIS worktree (`opus/r2-prep`, tip 6a08c6bbd). Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`.

**Hard constraints:**
- `greekocr/labelfix` and the 16 policy paths are byte-identical; digest 6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406.
- **Never submit:** the coordinator submits.
- The cert is valid until 17 Oct 19:18 Athens time. Never refresh it; an auth error means STOP and report.
- No `.git` writes; the lead commits.

**Template:** job 1 (BASE + teacher export, job 3681404): `config/r2_job.json`, `scripts/labelfix/clariden/r2_job.sbatch`,
`r2_deploy.py`, `r2_mock.py`, `R2_DEPLOY_FILES.txt` / `R2_DEPLOY_SHA256.txt`, `docs/records/labelfix/spellcheck/R2/R2_JOB1_DIGEST.md`.
Spec: `~/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/R2_PLAN_20261017.md` (arm R2a, §2a, pass criteria) + Addendum A.

## Inputs, copied into this worktree with sha256 verified (read-only sources in `~/Projects/greek-ocr-toolkit-spellcheck-r2cards`, commit 45c8c63ce)

- **R2a manifest:** `artifacts/r2a_manifest/r2a_slots.jsonl`, sha256 3dda20644c17b44e1a1c9f69781a9f1dd18657f6dc8b8b7e9cd14d8dd30a7667,
  1,573 slots (neg 1,150 / pos 423, 0 replaced, all new), plus its receipt.
- **T4 witnesses:** `artifacts/r2_resolve/T4/final/resolved.jsonl` (791 cards, witness role, documents disjoint from training).
  These are the R2a benefit witnesses: target-negative capital / ο / subscript, plus positives preserved.
- **Native crops** for both are referenced by the R2C decks and native_crops in the same worktree.

## Job contents (one sbatch)

1. **Native staging:** stage the crops for the 1,573 R2a slots and for the T4 witness slots on the cluster, the same way job 1 staged
   its population (`r2_native.py`). Use a remote root of `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2a_20261017`, new
   and separate from job 1's root, which must not be touched.
2. **R2a training:** old pool (the frozen R1 data path, as in job 1) + the R2a overlay.
   - Seeds 20261016, 20261017, 20261018.
   - The recipe is identical to BASE except for the overlay.
   - Corrections replace and never append. All 1,573 slots are new identities; the code path still asserts this.
3. **Scoring inference** for every arm checkpoint: R1-A s16 (saved), BASE s17/s18 (job 1 outputs, read-only), and R2a s16/s17/s18.
   - **Held-out fixtures:** the same as job 1's digest.
   - **T4 witnesses:** slot-level predictions for every witness slot.
   - **DEV:** the extraction spec in `docs/records/labelfix/spellcheck/R2/evidence/job1/DEV_pending.json` (600 lines, 1,793 items). Add the
     extraction it describes so DEV is scored in this job.
4. Outputs and receipts are laid out like job 1 (stage receipts with sha256), so the readback template B2 applies unchanged.

## Before deploy

- **A recipe disclosure table**, R2a vs BASE, with every parameter: data, overlay, weights, steps/epochs, optimiser, LR schedule,
  batch, sampler, seeds, augmentation, eval cadence, time. The only differences are the overlay and anything it forces (e.g. steps
  per epoch). List each one.
- **Time forecast** from job 1's measured stages (B 15.9 min, C 17.5 min); set `--time` with a 1.5× margin.
- **An end-to-end local mock** through the exact sbatch entry point (`r2_mock.py` style). It covers: staging → train → inference →
  scoring outputs; the replace-not-append assertion; the witness and DEV extraction; and the receipt schema. Mock-test the edited job
  scripts end to end.
- **Tests:** existing r2 tests + new ones for the overlay load, witness/DEV extraction and receipt fields.
- **Package files:** `R2A_DEPLOY_FILES.txt` + `R2A_DEPLOY_SHA256.txt`. Every deployed path must be tracked-or-hashed (the R2CU lesson).
  List any file that must be committed for verify_deploy, so the lead commits it BEFORE you run verify.

## Deploy (network ON)

1. rsync to the new remote root.
2. Remote sha256 must equal local for every file.
3. `sbatch --test-only` with the planned args.
4. Run the coordinator's verify_deploy tool, the same one R2CU ran (its invocation is in
   `docs/records/labelfix/spellcheck/R2/evidence/r2cu_verify_deploy_output.txt` / `r2cu_verify_deploy_guarded.json`), with
   `--sha-file R2A_DEPLOY_SHA256.txt` and the new remote root.
   - If it fails only because the package files are uncommitted, stop with "LEAD COMMIT NEEDED" and the exact `git add` list. The lead
     commits, then re-runs verify.

## Report

`docs/records/labelfix/spellcheck/R2/R2A_PACKAGE_REPORT.md`:
- the recipe table; the forecast; the mock log path; tests;
- deploy sha comparison; test-only output; verify_deploy verdict;
- the exact submit command (`sbatch …`), and the readback command for afterwards.

Last line: `R2J2 READY: mock pass; tests <n> passed; deployed files <n> sha match <n>/<n>; test-only <ok>; verify_deploy <VERIFY_OK|LEAD COMMIT NEEDED|FAIL: ...>; forecast <min>; submit: <command>`.

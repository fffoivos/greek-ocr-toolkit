# TR2b: move the deployed TR2 sbatch from `debug` to `normal` (gpt-6.1-sol, medium; network ON for Clariden only; no .git writes; NEVER submit)

Package: `docs/labelfix/spellcheck/SF7_TEST_PACKAGE.md` (TR2). Root on Clariden: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_test_20261019`.
The coordinator will submit tonight. The production sbatch must not run on the debug partition.

**The only change:** in `scripts/labelfix/clariden/tr2_job.sbatch`, `#SBATCH --partition=debug` → `#SBATCH --partition=normal`. Keep
`--time=01:00:00` (forecast 40 min × 1.5), account, node, GPU, CPU and every other line byte-identical. Touch no other file except the
deploy sha manifest(s) that must change because this file changed, and the report.

Steps:
1. Check that the CSCS cert works (`ssh clariden true`). On any auth error: STOP and report. Never refresh or re-sign the cert.
2. Before editing: confirm the remote sbatch sha equals the local one (prove the deployed state is the one you change).
3. Edit; regenerate `TR2_DEPLOY_SHA256.txt` (and the files list / manifest sha that embed it) with the SAME tooling TR2 used.
4. Redeploy only the changed files. Then a full remote check `sha256sum --check TR2_DEPLOY_SHA256.txt` on Clariden: every line OK.
5. `sbatch --test-only scripts/labelfix/clariden/tr2_job.sbatch` from the root: exit 0, and the printed partition is `normal`.
   If `normal` rejects the request, STOP and report the scheduler message; do not pick another partition.
6. Rerun the local mock through the exact entry point only if the edit can affect it; say which.
7. Update `docs/labelfix/spellcheck/SF7_TEST_PACKAGE.md`: requested resources line, new manifest sha, the exact submit command:
   `cd <root> && sha256sum --check TR2_DEPLOY_SHA256.txt && sbatch --parsable scripts/labelfix/clariden/tr2_job.sbatch`
   and the expected outputs (`output_<JOB>/test/release_edits_only_test_A.jsonl`, `test/RELEASE_RECEIPT_test.json`, the dev pair;
   receipts `candidate_pre_audit`, `bound: false`).
8. Update `docs/labelfix/spellcheck/TR2_evidence/LEAD_COMMIT_PATHS.txt` with every changed path, so the lead commits and the
   coordinator's `VERIFY_CMD.sh` (verify_deploy) passes.

Report the Codex weekly reading before and after (`artifacts/tr2/launchers/limit_probe.sh`, if it cannot run in your sandbox say so).
Final line: `TR2b READY: partition normal; time 01:00:00; remote sha N/N; test-only ok; manifest <sha>` or `TR2b STOPPED: <reason>`.

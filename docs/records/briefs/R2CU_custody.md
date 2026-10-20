# R2CU: deployment custody fix for labelfix_r2 (gpt-6.1-sol, medium, network ON for Clariden read-only sha checks only)

Workspace: THIS worktree (`-r2prep`, branch `opus/r2-prep`, head 14902a546 + this brief).
- **No `.git` writes** (the lead commits).
- No redeploy, no submission, never refresh the cert.

The coordinator's new deployment-verification tool returned **VERIFY_FAIL** for `labelfix_r2_20261017`. The four deployed population files
are untracked AND not gitignored:
`artifacts/labelfix_r2/population/{counts.json, crop_staging.json, population.jsonl, roles.json}` (about 24 MB together).
So no commit covers them. `R2P_REPORT.md` calls them "hash-bound gitignored", which is wrong.

**From now on the coordinator submits only on a VERIFY_OK receipt.** A deployment must be committed, or explicitly gitignored AND
hash-listed.

Do:
1. Make the four population files committable. Leave them in place; the lead commits them. List their sha256, and confirm they equal
   the deployed remote copies (read-only `sha256sum` over ssh, under `labelfix_r2_20261017/`) and the entries in
   `R2_DEPLOY_SHA256.txt`.
2. Add `.gitignore` entries (repo-relative, precise) for the bulk local-only artifacts:
   - `artifacts/labelfix_r2/population/upload/` (266 MB) and `artifacts/labelfix_r2/population/recreated/` (69 MB);
   - every `*_unstaged*`, `local_crops*`, `crop_probe*` jsonl under `artifacts/labelfix_r2/population/`;
   - the mock and pytest scratch dirs under `artifacts/labelfix_r2/` (`mock_run_*`, `pytest_*`, `mock_inputs*`);
   - `artifacts/labelfix_r2/output_3681404/` (the readback; its own READBACK_RECEIPT is the custody record);
   - `artifacts/labelfix_sf6/`, if it is a test copy.

   Do NOT ignore anything that is deployed. Cross-check every deployed path in `R2_DEPLOY_FILES.txt`: each must be either tracked (after
   the lead's commit) or explicitly listed in a new `docs/records/labelfix/spellcheck/R2/DEPLOY_UNTRACKED_HASHED.txt` with its sha256 and the
   reason it is not committed. Expectation: none remain once the 4 are committed.
3. Correct the custody note in `R2P_REPORT.md`: state what was wrong, the fix, and the per-file disposition table.
4. Run the coordinator's tool if it is reachable read-only: greek-page-ocr branch `sol/ops1-verify-deploy`, `scripts/ops/verify_deploy.py`,
   in its documented dry-run mode against this worktree + the remote deployment. Include its output; target VERIFY_OK after the lead's
   commit. If it cannot run before the commit, say exactly which check depends on the commit.

Last line:
`R2CU READY: population files 4 (sha = deployed yes); gitignore entries <n>; deployed paths tracked-or-hashed <k>/<k>; verify_deploy <OK|pending-commit|FAIL reason>`.

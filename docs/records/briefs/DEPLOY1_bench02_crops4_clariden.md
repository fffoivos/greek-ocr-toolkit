# DEPLOY1: deploy the bench02 and CROPS4 packages to Clariden and verify them (gpt-6.1-sol, medium, network ON for `ssh clariden`/`rsync` only, no spend)

**Coordinator request (20 Oct night):** deploy both packages now and verify them on Clariden.
- bench02: the coordinator submits the census_03 mechanics extract right after you report.
- CROPS4: deploy and verify now; it is submitted after census_05.
- **Never run `sbatch`, `srun` or `salloc`.** Leads never submit Clariden jobs. Read-only checks plus file copies into new package directories only. No other remote writes.

## Rules
- SSH alias `clariden` (works from this Mac). `$W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`.
- Deploy targets are new, versioned directories only: never overwrite an existing remote directory, never delete remote files.
- Commit sources: the HEAD of sol/recut-v1 (bench02 at e86fa1534 or later, crops4 at 157153fbe). Deploy only committed bytes: check `git status` is clean for those two directories first.
- Athens time from `date`.

## 1. bench02
1. Add `docs/harvest/collect_v3_admission/bench02/DEPLOY_PATHS.txt` (the tool, the sbatch scripts, job_common.sh, submit_job.sh, run_census05_draw.sh and the docs, i.e. what the jobs need; no dry-run data), plus `DEPLOY_SHA256SUMS` over those paths.
2. Add `bench02/VERIFY.sh`, run **on Clariden** from the deployed root. It checks:
   - `sha256sum -c DEPLOY_SHA256SUMS`;
   - `venv_l1/bin/python` exists and is ≥ 3.10;
   - `bench02_draw.py --help` runs under it;
   - an optional census directory argument: decisions.jsonl and evaluation_diagnostics.jsonl exist and are readable.

   It prints exactly `VERIFY_OK bench02 <deploy_sha8>` or fails.
3. Commit those additions on sol/recut-v1, guarded: only those files. The lead commits; Sol stops after writing the files and tells the lead. **Do not commit yourself**; produce the file list.
   **Deploy only after the lead commits.** Sol cannot wait for that, so in this run deploy from a `git archive` of the working-tree state of exactly the DEPLOY_PATHS files, and record their sha256. The lead's commit must then match those shas; record them in the receipt.
4. Deploy to `$W/filter_pipeline_20261018/bench02_pkg/<deploy_sha8>/` with the repository-relative layout (`docs/harvest/collect_v3_admission/bench02/...`), so that submit_job.sh's `B="$(pwd)/docs/harvest/collect_v3_admission/bench02"` works from that root.
5. Run `VERIFY.sh` remotely, with the census argument `$W/filter_pipeline_20261018/attempts/census_03/current`, and capture its output.

## 2. CROPS4
1. Deploy `docs/harvest/collect_v3_admission/crops4/` per its `DEPLOY_PATHS.txt` to `$W/crops4_package/<deploy_sha8>/`, a new directory.
2. On Clariden, run `sha256sum -c DEPLOY_SHA256SUMS` in it, and check that the venv_l1 python and the png-codec preload file exist.
3. Its own `VERIFY.sh` needs a completed census_05 and cannot pass tonight. Run only its package-level checks, and state that clearly. Print `VERIFY_DEPLOY_OK crops4 <deploy_sha8>`; the full `VERIFY_OK` comes after census_05.

## Report (`docs/harvest/collect_v3_admission/DEPLOY1_RECEIPT.md`)
For each package:
- the deployed root;
- the deploy sha;
- the per-file shas;
- the remote check output, verbatim;
- **the exact submit line(s)** for the coordinator.

For bench02 the submit line is the census_03 mechanics extract, run from the deployed root:
`cd <root> && bash docs/harvest/collect_v3_admission/bench02/submit_job.sh extract $W/filter_pipeline_20261018/attempts/census_03/current $W/filter_pipeline_20261018/bench02/census03`

Check that the output directory does not already exist. For CROPS4, give the CROPS4.md commands with the deployed root filled in.

The last line must be exactly:
`DEPLOY1: done | bench02 <root> VERIFY_OK <sha8> | crops4 <root> VERIFY_DEPLOY_OK <sha8> | no jobs submitted | files to commit <n>`

# DEPLOY3: redeploy bench02 after BENCH02I (gpt-6.1-sol, medium, network ON for `ssh clariden`/`rsync` only, no spend)

BENCH02I (commit f8c23ee4e) changed `bench02_draw.py`: the extract receipt now carries the tags sha, and the ruled draw defaults are in. The Clariden copy `bench02_pkg/9e779519` is stale. Redeploy so that the census_05 extract writes the sha into its receipt.

Same rules as DEPLOY2 (`docs/harvest/collect_v3_admission/DEPLOY2_RECEIPT.md`):
- no `sbatch`/`srun`/`salloc`;
- new versioned directory only, nothing overwritten or deleted;
- the interpreter is `$W/venv_l1/bin/python`;
- do not commit; produce the file list.

## Do
1. Check that `git status` is clean for every bench02 path in `DEPLOY_PATHS.txt`, and that HEAD contains f8c23ee4e. Add any new runtime file the jobs need, e.g. `run_ruled_draw.py` if `run_census05_draw.sh` calls it, to DEPLOY_PATHS. Regenerate `DEPLOY_SHA256SUMS`.
2. Deploy to `$W/filter_pipeline_20261018/bench02_pkg/<new sha8>/` (repository-relative layout) and read every sha back.
3. On Clariden, run `VERIFY.sh` with `$W/filter_pipeline_20261018/attempts/census_03/current`. It must print `VERIFY_OK bench02 <sha8>`.
4. Also on Clariden, as a **login-node-light** check, run the extract code path on a **tiny** input:
   - `head -n 200` of the census_03 decisions and diagnostics, written to a temp directory under `$W/filter_pipeline_20261018/bench02/deploy3_check/`;
   - run `extract` under venv_l1;
   - confirm the receipt carries the tags sha256 and it matches `sha256sum`.

   This is a 200-row check only. Do not run anything bigger on the login node.
5. Write `docs/harvest/collect_v3_admission/DEPLOY3_RECEIPT.md`:
   - root, sha, per-file hashes;
   - the verbatim output of steps 3–4;
   - the exact census_05 extract submit line with the new root;
   - the file list to commit.

The last line must be exactly:
`DEPLOY3: done | bench02 <root> VERIFY_OK <sha8> | receipt sha check on 200 rows ok | no jobs submitted | files to commit <k>`

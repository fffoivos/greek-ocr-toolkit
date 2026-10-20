# DEPLOY2: fix the Clariden interpreter path and redeploy bench02 + CROPS4 (gpt-6.1-sol, medium, network ON for `ssh clariden`/`rsync` only, no spend)

DEPLOY1 (`docs/harvest/collect_v3_admission/DEPLOY1_RECEIPT.md`) deployed both packages but did not verify them: the interpreter was "missing". **The path in my briefs was wrong; the lead's error.**
- census03.sbatch sets `python="$root/../venv_l1/bin/python"` with `root=$W/filter_pipeline_20261018`.
- So the census interpreter is **`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python`**: a symlink to uv cpython 3.12.15, Pillow 12.3.0, verified by the lead over ssh.
- The png-codec preload stays at `$W/filter_pipeline_20261018/runtime/png-codec/lib64/libz.so.1.3.1.zlib-ng`; DEPLOY1 found it present.

**Rules:**
- Same as DEPLOY1: no `sbatch`/`srun`/`salloc`; new versioned remote directories only; never overwrite or delete remote files (the DEPLOY1 directories `bench02_pkg/e2b58493` and `crops4_package/c9bb1bb0` stay as they are).
- Athens time from `date`.
- Do not commit; produce the file list for the lead.

## Do
1. Replace `filter_pipeline_20261018/venv_l1` with the correct `$W/venv_l1` path in:
   - bench02: `job_common.sh`, `VERIFY.sh`, `BENCH02D.md`, `test_bench02e.py`, and any doc that names it;
   - crops4: `crops4.sbatch`, `CROPS4.md`, and `VERIFY.sh` if it has it.
   Change nothing else. `grep -rn venv_l1` both directories before and after.
2. Re-run both test suites locally:
   - bench02: `run_tests.py`;
   - crops4: `test_crops4.py`, with the byte-exact interpreter `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`.
   Both must pass. Regenerate crops4's `COMMIT_LIST.json` hashes, `DEPLOY_SHA256SUMS`, `TESTS.log` and `TEST_RESULTS.json` as its guard expects, and regenerate bench02's `DEPLOY_SHA256SUMS`.
3. Redeploy both to **new** directories named by the new deploy sha8: `$W/filter_pipeline_20261018/bench02_pkg/<sha8>/` and `$W/crops4_package/<sha8>/`. Read the shas back remotely.
4. On Clariden:
   - bench02: `cd <root> && bash docs/harvest/collect_v3_admission/bench02/VERIFY.sh $W/filter_pipeline_20261018/attempts/census_03/current` must print `VERIFY_OK bench02 <sha8>`;
   - crops4: run the package-level checks (sha256sum -c, interpreter ≥ 3.10 executes, `import PIL` works, codec readable). They must print `VERIFY_DEPLOY_OK crops4 <sha8>`.
5. Check that `$W/filter_pipeline_20261018/bench02/census03` does not exist.
6. Write `docs/harvest/collect_v3_admission/DEPLOY2_RECEIPT.md`, in the same format as DEPLOY1:
   - the roots, shas and per-file hashes;
   - the verbatim remote output;
   - the exact coordinator submit line for the census_03 mechanics extract;
   - the CROPS4.md commands with the new root and the correct interpreter path filled in;
   - the list of files for the lead to commit.

The last line must be exactly:
`DEPLOY2: done | bench02 <root> VERIFY_OK <sha8> | crops4 <root> VERIFY_DEPLOY_OK <sha8> | tests bench02 <n> crops4 <m> passed | no jobs submitted | files to commit <k>`

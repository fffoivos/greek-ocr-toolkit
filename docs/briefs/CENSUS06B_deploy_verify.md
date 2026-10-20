# CENSUS06-B: deploy the committed census_06 package de597753a70a5d6d + inputs; readback; unchanged verifier ×4; scheduler test-only (gpt-6.1-sol, medium, network ON for `ssh clariden` and `rsync` only, no spend, no jobs)

The base is CENSUS06-A, committed by the lead as **cf1db4dd4** (package `de597753a70a5d6d`, 180 files). Read `docs/harvest/census06/CENSUS06.md`, `COMMIT_LIST.md` (its B paragraph), `INPUTS.json`, `restore_inputs.py`, `verify_b.py`, `VERIFY.sh` and `submit_chain.sh`. Also read the census_05 B/D precedent: segcensus `docs/briefs/CENSUS05_B_deploy.md`, `CENSUS05_D_verify.md` and `docs/harvest/census05/c_evidence/verify.py`, read-only.

`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`.

## The clean tree for the verifier
- The unchanged verifier, `~/Projects/greek-page-ocr-wave2/scripts/ops/verify_deploy.py`, rejects any tracked uncommitted path in the whole tree. This worktree has unrelated dirty tracked files that are not ours.
- **The lead has created a clean detached worktree at the commit: `~/Projects/greek-ocr-toolkit-census06-verify`** (HEAD cf1db4dd4, 0 changes). Point the verifier's repository/source argument there.
- Do not modify that worktree. If the verifier needs to write into it, stop and report. Write receipts and logs to `docs/harvest/census06/b_evidence/` in this repo, or to a temp dir that you then copy there.
- Use no `--allow-untracked` exemption for payload paths; report any exemption you needed and why.

## Do
1. **Deploy** the committed manifest bytes, read from the clean worktree, to the **new, empty** `$W/census_06_20261020/code/de597753a70a5d6d/`. Refuse if it is non-empty.
   - Copy the five regenerated numerics inputs (rehydrate with `restore_inputs.py` from `corrections/archives/`, without overwriting) and the unchanged split to new destinations under `$W/census_06_20261020/inputs/`. Refuse to overwrite.
   - Read back every payload and input sha.
   - Rehash the standing cyrillic ledgers in place (read-only).
   - **Never write under `$W/census_05_20261020`.**
2. **Verify:** run the unchanged verifier for all four kinds (regression / parity / census / readout), with the census_05 D argument pattern adapted to census_06. The expected result is `VERIFY_OK` ×4.
   - Then run scheduler `sbatch --test-only` for the smoke and full chains, as census05-B did (debug 00:30:00 for smoke; the packaged limits for full).
   - `--test-only` is the only sbatch form allowed.
   - Check every sbatch for `--account=a0140`, partition and time.
3. **The sf7 binding stays PENDING.**
   - Run `bind_sf7.py` in its dry/pending mode only, to show it refuses without files.
   - `submit_chain.sh` must refuse while sf7 is pending; show the refusal.
4. **Clean-up (coordinator rule):** delete only your own pytest basetemp directories in `docs/harvest/census06/` (`033-regression-tmp/`, `baseline-regression-tmp/`, `test-tmp/`, and any basetemp this run creates), keeping the `.log`/`.xml` receipts.
   - Delete nothing else: not `baseline/`, `mock_batch/`, `corrections/`, the archives or any data.
   - List what you deleted, with sizes.
5. **Hand-off:** add a B section to `CENSUS06.md`, containing:
   - the deploy root, the readback counts and the input destinations + shas;
   - the verifier receipts (sha of each);
   - the test-only lines;
   - **the exact coordinator block**: the sf7 bind step (`bind_sf7.py <per-parent file> <sha>` …) → the package rebuild/redeploy that the binding triggers (new code id) → the smoke chain → review → the full chain (afterok) → readout as a sibling with `--expect-pipeline-version 0.3.3` → flip_report.
   - **State plainly which steps must be re-run after the sf7 binding changes the package id.**

Write a guarded commit list for the new B files. Do not run `git add` or `git commit`. Touch nothing outside `docs/harvest/census06/` and this brief.

The last line must be exactly:
`CENSUS06-B: READY | deployed de597753a70a5d6d readback <n>/<n> + inputs <k>/<k> | VERIFY_OK <k>/4 (clean worktree cf1db4dd4) | test-only smoke <k>/4 full <k>/4 | sf7-binding PENDING (submit refuses) | basetemp deleted <size> | no jobs submitted`

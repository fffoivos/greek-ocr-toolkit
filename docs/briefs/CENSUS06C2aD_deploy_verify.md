# CENSUS06-C2a-D: deploy the committed pre-binding package fb0194d597f20655; readback; unchanged verifier ×4; scheduler test-only (gpt-6.1-sol, medium, network ON for `ssh clariden` and `rsync` only, no spend, no jobs)

The base is CENSUS06-C2a, committed by the lead as **0cc5710bf** (package `fb0194d597f20655`, 182 files). It is the B deploy (`docs/briefs/CENSUS06B_deploy_verify.md`, whose B section in `CENSUS06.md` and `verify_b.py` you reuse) for new bytes. Differences from B:
- **Clean tree:** the lead created `~/Projects/greek-ocr-toolkit-census06-verify-c2a` (detached, HEAD 0cc5710bf, 0 changes). Point the verifier there. Do not modify it, and use no exemption.
- **Inputs are already deployed** under `$W/census_06_20261020/inputs/` (the five numerics ledgers + split, from B). Do **not** copy them again. Rehash them in place and compare with INPUTS.json, and rehash the standing cyrillic ledgers (all read-only).

`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`.

## Do
1. **Deploy** the committed manifest bytes, read from the clean worktree, to the **new, empty** `$W/census_06_20261020/code/fb0194d597f20655/`. Refuse if it is non-empty.
   - Read back every payload sha.
   - Never write under `$W/census_05_20261020` or into the `de597753a70a5d6d` code dir.
2. **Verify:**
   - Run the unchanged verifier for all four kinds against the new code dir and the commit 0cc5710bf: `VERIFY_OK` ×4 expected.
   - Run `sbatch --test-only` for smoke (debug 00:30:00) ×4 and full ×4 (packaged limits), plus one test-only of the full census job with `SBATCH_TIMELIMIT=06:00:00`, to show that the C1 override reaches only that job and that the printed `--time` is right.
   - Run one test-only of `bind_sf7.sbatch` (normal, 00:30:00, 4 CPUs) with a placeholder bindings file under the scratchpad, to show it schedules. Since test-only does not run it, nothing is bound.
   - `--test-only` is the only sbatch form allowed. Check every sbatch for `--account=a0140`, partition and time.
3. **sf7 stays PENDING:**
   - `binding_state.py` prints PENDING ×5;
   - `submit_chain.sh` refuses;
   - `bind_sf7.py` with no files refuses.
4. **Hand-off:** add a C2a-D section to `CENSUS06.md`, containing:
   - the deploy root, the readback n/n, the input rehash k/k, the verifier receipt shas, and the test-only lines;
   - **the exact coordinator bind block**, with `CENSUS06_BUNDLE=$W/census_06_20261020/code/fb0194d597f20655/docs/harvest/census06`, `SF7_BINDINGS_FILE=$W/census_06_20261020/sf7-bindings.json` (keyed by the five parent ids, each `{path, sha256}`), and `SF7_BIND_WORK=$W/census_06_20261020/binding/sf7-001`, which must not exist;
   - then what the lead does after the bind (import the staged artifacts → commit → verify ×4 at the bound id → test-only ×8 → `binding_state --submit` → the real sf7 head test), then smoke → TIMING line → full with `SBATCH_TIMELIMIT` = projection × 1.5 (capped at the partition max) → readout (sibling, `--expect-pipeline-version 0.3.3`) → flip_report;
   - **mark the de597753a70a5d6d bundle superseded:** never bind from it.
5. **Clean-up:** delete only your own pytest basetemp, if any, and list what you deleted. Delete nothing else.

Write a guarded commit list (`C2AD_COMMIT_PATHS.txt` + SHA256SUMS). Do not run `git add` or `git commit`. Touch nothing outside `docs/harvest/census06/` and this brief.

The last line must be exactly:
`CENSUS06-C2a-D: READY | deployed fb0194d597f20655 readback <n>/<n> + inputs rehash <k>/<k> | VERIFY_OK <k>/4 (clean worktree 0cc5710bf) | test-only smoke <k>/4 full <k>/4 + override 1/1 + bind 1/1 | sf7-binding PENDING (submit refuses) | no jobs submitted`

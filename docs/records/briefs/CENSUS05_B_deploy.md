# CENSUS05-B: deploy census_05, VERIFY_OK, sbatch --test-only (gpt-6.1-sol, medium, network ON; no .git writes; NO submission)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`. The lead committed the CENSUS05-A package as
`a09642bd4` (package `17b0eb1ca7fe81a7`, 167 files; inputs per `INPUTS.json`: five regenerated N1 ledgers + split2).
- HEAD must be `a09642bd4` (package `17b0eb1ca7fe81a7`, 167 files; inputs per `INPUTS.json`: five regenerated N1 ledgers + split2), or a descendant whose extra commits touch only `docs/briefs/`. Check this first.
- Follow `docs/harvest/census05/HANDOFF_CENSUS05.md`, `COMMIT_LIST.md` and `FOLLOW_UP.md` exactly.
- Write locally only inside `docs/harvest/census05/` (hand-off section, receipts, evidence).

`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`. Use the ssh alias `clariden`. If ssh or authentication fails, stop: the
certificate is owner-gated. Never attempt a credential repair.

## Do

1. **Deploy** the `DEPLOY_PATHS.txt` payload, repository-relative paths preserved, to the NEW directory
   `$W/census_05_20261020/code/<package_id>/`.
   - If it already exists and is non-empty, STOP: never overwrite.
   - Copy the five regenerated N1 ledgers (local, gitignored `docs/harvest/census05/corrections/numerics_*.jsonl`, sha per `INPUTS.json`; the five standing cyrillic ledgers are already on Clariden under census_03 `prepared/87407ec7430a375f/`: readback their sha in place, do not copy) and `row_split.jsonl.gz` (split2, sha256 `7b27ab9b…`) to `$W/census_05_20261020/inputs/`,
     with the same refusal rule.
   - Write nowhere else on Clariden. Do not create `attempts/` or `logs/`: that is the coordinator's step.
2. **Readback.** Make a per-file remote sha256 table for every deployed file and input. Every one must match.
3. **Verify.** Run the FOLLOW_UP.md verifier block unchanged (`~/Projects/greek-page-ocr-wave2/scripts/ops/verify_deploy.py`)
   for the four job kinds (regression, parity, census, readout; `common.sh` is shared code, hash-verified, not a job), until each prints
   `VERIFY_OK`.
4. **Read only, on Clariden:**
   - `scontrol show partition debug`: record MaxTime and the node limits. Set the smoke `--time` in the smoke commands to fit
     them, with the smoke's measured mock row rate as the basis.
   - The census_03 run's own outcome summary: look under `$W/filter_pipeline_20261018/attempts/census_03/` (the generation
     `g1-a21c3b465ca94eee80cb5bd34b336d69` and `CURRENT.json`) for `summary.json`.
     - If it exists, copy that one file (it is small) to `docs/harvest/census05/census03_summary.json`, with its remote path,
       bytes and sha256.
     - Run the committed readout's `--baseline` code path on it locally, against a mock run, to prove it parses.
     - Do not download `decisions.jsonl`.
   - `sacct -j 3695426` (census_03), to record what it ran and its elapsed time.
5. **`sbatch --test-only`** for every kind, with the exact FOLLOW_UP.md argv:
   - smoke settings: `E4_SMOKE=1`, `--partition=debug` and the smoke `--time`;
   - full settings: `E4_SMOKE=0`, the in-script `normal`/`04:00:00`, and `CENSUS05_SPLIT_FILE`/`CENSUS05_SPLIT_SHA256` set to the
     deployed split.

   These are dry checks only: never a real submission, and never with `--test-only` omitted. Record each scheduler response.
6. **The final coordinator commands,** appended to `HANDOFF_CENSUS05.md` as a section "B: deploy + verify":
   - the remote root, the VERIFY_OK outputs, the readback summary and the test-only table;
   - the debug limits and the census_03 baseline (found or absent);
   - the FINAL, literal, unexecuted coordinator commands:
     - the `mkdir` of `attempts/` and `logs/`;
     - smoke: regression → parity → census → readout, `afterok`, on debug;
     - full: the same chain, normal, split bound, with `CENSUS05_BASELINE` pointing at the census_03 summary if it was found;
     - the readout command, checked against the deployed paths.

   Write the receipt.
7. **`docs/harvest/census05/REVIEW_INPUTS.md`**, one page, for the Astra review the owner requires before submission. Point at
   exactly these artifacts, each with its repository path, its remote path where deployed, and its sha256:
   - the bundle root and `DEPLOY_SHA256SUMS`, with the package id and `PROJECTS_SHA256`;
   - the VERIFY_OK receipts per kind, and the readback table;
   - the package test log, with its counts;
   - the parity expectation and its result;
   - the smoke and full `--test-only` responses;
   - `census05_config.json` and its diff against census_04 (`routes_out_of_scope`, unbound polytonic ledgers, regenerated N1
     ledgers with the moving-status list, split2 binding);
   - the readout script, its sbatch and its mock readouts.
   
   Add five lines naming what the review must check: code identity, config, corrections, split, and job settings. No claims
   beyond the cited artifacts.

**Last line:** `CENSUS05-B READY: deployed <n> files to <package_id> + inputs <n>; readback <n>/<n>; VERIFY_OK <kind ok, …>; debug MaxTime <t> smoke --time <t>; census_03 summary <found sha8|absent>; test-only smoke <ok/kind> full <ok/kind>`

# SEGCENSUS-1d (b2): deploy, VERIFY_OK, sbatch --test-only (gpt-6.1-sol, medium, network ON; no .git writes; NO submission)

The lead committed (a) `a86d930dd` "owner filter pipeline 0.2 source as of 18 Oct" and (b) `56e5695c5`, the census_04 package. HEAD
must be 56e5695c5 or a descendant whose extra commits touch only `docs/records/briefs/`; check this first.

**Do,** exactly per `docs/records/harvest/seg_census/COMMIT_LIST.md` and `FOLLOW_UP.md`:
1. **Deploy** the 338 `DEPLOY_PATHS.txt` payload files, with repository-relative paths preserved, to the NEW directory
   `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/code/bb1ea164338b3068/`.
   - If that directory already exists and is non-empty, STOP and report: never overwrite.
   - Write nowhere else on Clariden.
   - If ssh or authentication fails, stop: the certificate is owner-gated.
2. **Run the verifier command block** for the three job kinds (regression, parity, census) unchanged, until each prints
   `VERIFY_OK`. Also do a per-file remote readback sha table.
3. **`sbatch --test-only`** for each job kind, in smoke mode-i and full mode-i settings (E4_SMOKE=1 and 0). These are dry checks:
   - never a real submission, never with `--test-only` omitted;
   - record the scheduler's response per kind.
4. Append to `HANDOFF_SEGCENSUS1.md` a section "b2: deploy + verify": the remote root, the VERIFY_OK outputs, the readback table
   summary, the test-only results, and the FINAL coordinator submit commands for smoke mode-i (then full mode-i), copied from
   FOLLOW_UP.md and checked against the deployed paths. Write the receipt.

**Last line:** `SEGCENSUS1d READY: deployed 338 files to bb1ea164338b3068; VERIFY_OK regression <ok> parity <ok> census <ok>; readback <338/338>; test-only smoke <ok/kind> full <ok/kind>`

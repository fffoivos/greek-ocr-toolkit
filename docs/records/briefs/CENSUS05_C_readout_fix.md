# CENSUS05-C: fix the readout's held-out check (Astra H1), redeploy, re-verify (gpt-6.1-sol, medium, network ON; no .git writes; NO submission)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`, HEAD `4f86f0c80` or a descendant touching only
`docs/briefs/`. The lead commits.
- Write locally only inside `docs/harvest/census05/`.
- On Clariden, write only into the NEW `$W/census_05_20261020/code/<new_package_id>/`. Never touch the old
  `code/17b0eb1ca7fe81a7/` or `inputs/`.
- If ssh or authentication fails, stop: the certificate is owner-gated.

**Read first:**
- the Astra review, read only:
  `~/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-CENSUS05/ASTRA_CENSUS05_REVIEW.md`
  (H1, M2, M3, L1), with `protection_recount.json`, `readout_witnesses.py` and `readout_witnesses.json`;
- `docs/harvest/census05/readout/census_readout.py`, `test_census_readout.py`, `HANDOFF_CENSUS05.md`, `FOLLOW_UP.md`,
  `REVIEW_INPUTS.md`, `build_package.py`;
- the pipeline's own protection rule: packaged `line_pipeline_census.py` `deduplicate()` (configured
  `final_policy.heldout_crop_sha256` ∪ crops observed on dev/test rows ∪ protected editions).

**Change only the readout and its tests, and only as follows.** No pipeline file changes. The 154 CODE_SHA-identical files stay
byte-identical.

1. **H1 (HIGH).** The readout's protected set must be exactly the pipeline's union:
   - configured `final_policy.heldout_crop_sha256` (from the run binding the readout already hashes);
   - ∪ crop hashes observed on dev/test rows;
   - ∪ protected editions.

   Mirror `deduplicate()`, citing its lines. An admitted row whose crop is in the configured list counts as a leak even when no
   dev/test row has that crop and its edition is not protected.
2. **L1 (LOW).** Add an invariant `admitted_train_equals_eligible`: the admitted_train export equals, row for row and uniquely,
   the set the pipeline's export rule selects.
   - Read that rule from the packaged export code (ADMIT ∩ train split, per the code), and cite it.
   - The existing subset invariant stays.
3. **M2 (MEDIUM).** Make the readout tests reproducible from a clean checkout:
   - fixture paths resolve relative to the test file's own repository root, with a skip and a clear reason when a historical
     fixture is absent;
   - every receipt or output a test writes goes to `tmp_path`, never to the repository.
4. **Tests (new):**
   - **Astra's witness**, reproduced: one train ADMIT row whose crop is only in the configured list, its edition not protected,
     and no dev/test observation. Result: heldout leaks 1, the invariant fails, and the CLI exits nonzero.
   - The same row with its crop not configured: 0 leaks.
   - **Astra's missing-export witness:** 3 ADMIT/train decisions and an empty export. Result: `admitted_train_equals_eligible`
     fails, exit nonzero.
   - **Re-run on the three committed mocks** (`mocks/*/`): all invariants PASS, including the new one. Report each last line.
   - Re-run the whole readout suite and the packaged regression. Report the counts verbatim.
5. **M3 (MEDIUM), documentation only.** The N1 ledger archives are not in git; they are gitignored. The lead has placed a durable
   copy at the data root: `~/Projects/greek-ocr-data/docs/records/harvest/census05/corrections/archives/` (35 files), with
   `../ARCHIVES_SHA256SUMS` and `../archive_receipt.json`.
   - Verify all 35 hashes there against `corrections/archive_receipt.json`.
   - Correct the hand-off wording: "gitignored; durable copy at the data root, receipt ...".
   - Add the location to `INPUTS.json` and `REVIEW_INPUTS.md`.
6. **Rebuild the package** with `build_package.py`:
   - the new readout is an additive file;
   - regenerate `DEPLOY_PATHS.txt`, `DEPLOY_SHA256SUMS`, `package_id.json` and `PROJECTS_SHA256` (expected unchanged; say so);
   - list the files whose hashes change. Expected: the readout and its tests only, plus the manifests.
7. **Redeploy and verify,** exactly as CENSUS05-B did, to `$W/census_05_20261020/code/<new_package_id>/`:
   - refuse a non-empty destination;
   - per-file readback;
   - the unchanged verifier for the four kinds, until each prints VERIFY_OK;
   - `sbatch --test-only` for smoke (`--partition=debug --time=00:30:00`) and full;
   - inputs are unchanged: re-hash them in place, do not copy.
8. **Update** `FOLLOW_UP.md`, the "B" command block in the hand-off (as a new section "C: readout fix + redeploy"; the old
   section stays), and `REVIEW_INPUTS.md`.
   - The new bundle path.
   - Smoke `--time=00:30:00`.
   - A short "changes since the Astra review" list mapping H1, L1, M2 and M3 to files and tests.
   - Write `readout_fix.patch` against `docs/records/harvest/census05/readout/` (the clean-up layout), for the coordinator's
     docs-only merge. It supersedes `readout_version.patch`, so include both changes.

**Last line:** `CENSUS05-C READY: package <id> files <n> (changed: <list>); H1 witness leaks 1 exit <rc>; config-only protected set <n> hashes; L1 witness exit <rc>; mocks invariants <k>/<k> PASS x3; readout tests <n> passed <n> failed <n> skipped; regression <n> passed; archives 35/35 at data root; readback <n>/<n>; VERIFY_OK <4 kinds>; test-only smoke <ok>/4 full <ok>/4`

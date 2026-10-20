# SEGCENSUS-1c: apply the lead rulings, finish the package, the split input, the mocks and the commit list (gpt-6.1-sol, medium, network ON for read-only Clariden checks only; no .git writes; no deploy yet; no submission)

Continue SEGCENSUS-1 (`docs/records/harvest/seg_census/HANDOFF_SEGCENSUS1.md`, `SOURCE_CAPTURE.md`) AND do SEGCENSUS-1b
(`docs/records/briefs/SEGCENSUS1b.md`) in this run. Same worktree and constraints. The coordinator withdrew "option E": do NOT add any
all-ink box diagnostic.

## Lead rulings

1. **The three conflicts:** take the sol-recut versions of `greekocr/harvest/geometry_observations.py`,
   `greekocr/harvest/row_inclusion.py` and `pyproject.toml`.
   - They are the owner's filter pipeline 0.2 source changes, are additive (prepare_geometry_row, the optional magnitude_loader, the
     filter CLI and package data) and are not 0.8 segmentation files.
   - After copying, the 0.8 implementation files must still equal `git show 410f4566:<path>` byte-for-byte, and the FULL test suite
     (segmentation + pipeline) must pass. If anything fails, stop and report.
2. **No exact snapshot match.** Record the facts plainly in the hand-off:
   - "capture = sol-recut working tree on 19 Oct (includes 0.8); no Clariden code snapshot equals it";
   - "census_03 ran snapshot 87407ec7430a375f (all 325 manifest files match)";
   - "the census_04 package derives from 87407ec7 with only the 0.8 segmentation files + tool-versions changed".

   The lead commits the capture as "owner filter pipeline 0.2 source as of 18 Oct".
3. **Verifier.** Use `../greek-page-ocr-wave2/scripts/ops/verify_deploy.py` (read only). It needs committed deliverables, so prepare
   everything and stop before the deploy. The lead commits, then a follow-up brief deploys and verifies.

4. **Full-suite environment failures (ruling, after the 1c stop).**
   - A test that fails at COLLECTION because a historical untracked evidence file is missing in this worktree (e.g.
     `tests/test_seg_cp7c.py` → `seg/CP5_verification.json`, which exists only untracked in sol-recut) is a pre-existing
     environment gap, not a regression. Prove it: the same test file fails the same way in a pristine `git worktree` checkout of
     `sol/seg-cells` (a temporary directory you create and remove; no shared-git writes beyond that worktree add, which the lead
     allows).
   - Then run the full suite with exactly those proven-pre-existing files deselected, and list them.
   - Any OTHER failure stops the run.
   - Do NOT copy the historical evidence files in to make the tests pass.

5. **Baseline comparison replaces "any other failure stops" (ruling after the 1c2 stop).**
   - Several failures are a known pre-existing set in this repo: test_apply_clean 5 setup errors, test_collection_outputs 3, plus
     probably test_cyrillic and test_google_vision.
   - Run the SAME full suite (same interpreter and flags, same deselection) on the pristine `sol/seg-cells` export used for the
     ruling-4 proof, and compare the failure sets by test id.
   - A **regression** is a test that fails here but passes on the pristine baseline. Regressions stop the run.
   - Failures identical on both sides are recorded as pre-existing and do NOT stop.
   - Then complete every remaining step: package, diagnostics + invariance, job kinds, split plumbing, mocks, commit list.

## Do

1. **Apply ruling 1.** Run the full tests and report.
2. **Finish SEGCENSUS-1 step 4**, without modifying the owner stage:
   - **Diagnostics integration:** the 0.8 box/ratio, the saved chars, the `is_cell` family, and the frozen 0.5 verdict/reason. Add
     the all-diagnostic invariance test.
   - **Job kinds:** batch job scripts per kind, with partition, time, nodes and CPUs from census_03's measured runtimes + margin,
     with the evidence.
   - **Smoke and full** settings, `E4_SMOKE=1` and `0`.
   - **Output root** `$W/filter_pipeline_20261018/census_04_seg08/`.
   - **Config** with input preservation.
3. **SEGCENSUS-1b in full:** the split-file input plumbing, the two modes, and the schema.
4. **Mocks:**
   - the 150+888 identity through the packaged stage;
   - the ~200-row whole-pipeline slice through the real batch scripts, exercising the sbatch working directory and output roots,
     in both split modes.
5. **Commit list.** Write `docs/records/harvest/seg_census/COMMIT_LIST.md`: the exact paths the lead must `git add` for:
   - (a) the capture commit: the owner filter pipeline 0.2 source;
   - (b) the package commit: the census_04 package, job scripts, config and tests.

   Also list which untracked runtime files are gitignored and must be named to `verify_deploy.py`, and give the exact
   `verify_deploy.py` command for the follow-up.
6. Update the hand-off and the receipt.

**Last line:** `SEGCENSUS1c READY: conflicts resolved (sol-recut ×3), 0.8 files identical <yes>; tests <n> passed; diagnostics invariance <ok>; job kinds <list with partition/time>; split consumed before <yes|no>, plumbing <none|added>; mock 150 <n>/150 888 <n>/888, slice mode-i <ok> mode-ii <ok>; commit list <ready>`

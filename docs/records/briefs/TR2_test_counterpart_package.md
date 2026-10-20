# TR2: package the sf7-A v2_test/dev counterpart as a Clariden job (gpt-6.1-sol, medium; network ON for Clariden only; no .git writes; NEVER submit)

TR1 (`docs/records/labelfix/spellcheck/SF7_TEST_COUNTERPART.md`) found no saved L1-era outputs for test/dev, so new inference is needed:
- 36,730 greek_poly lines (v2_test 28,620; dev 8,110), with the raw parents named in TR1;
- estimate about 2.67 GPU-h, about 40 min wall.

The coordinator wants it READY to submit on the owner's go.

**Build it by REUSING the existing code paths:**
- the L1-era inference that produced the train outputs (recogniser full_s0 alignments, the S6 detector, reader A/B ENSEMBLE_AB, as in
  L1R3 3680729 and its packages);
- the GC1 sf7 recompose (variant A, digest f41e0563…);
- the RB7 edits-only converter (release id `sf7_rc1_test_edits_A`; separate test and dev files; parent = the matching raw import; an
  exact byte-patch check).

Write no new model code. Keep the Codex build cost low: copy and parameterise, don't redesign.

**Package:**
- a new root `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_test_20261019`;
- the sbatch cds to its own root, checks shas there, and sets PYTHONPATH = root;
- a local mock through the exact entry point;
- a REAL-INPUT login-node dry run on 500 lines, without GPU where possible, or report what needs a GPU;
- deploy, remote sha = local, `sbatch --test-only` with the planned time (forecast × 1.5);
- `LEAD_COMMIT_PATHS.txt` + `VERIFY_CMD.sh` (the coordinator's verify_deploy);
- report the recipe identity vs train (the same checkpoints and shas).

**Mac disk is tight (about 7 GB free):** nothing large stays local.

Report: `docs/records/labelfix/spellcheck/SF7_TEST_PACKAGE.md`, including the actual Codex points used.

Last line: `TR2 READY: lines test <n> dev <n>; dry run exit 0; deployed <n> sha match; test-only ok; forecast <min>; lead commit list <path>; Codex <pts>`.

**Codex budget cap (coordinator, 19 Oct):** the weekly meter was 29% at 13:46 Athens. Probe it with
`bash ~/Projects/greek-ocr-toolkit-spellcheck-r2cards/artifacts/cq4/launchers/limit_probe.sh 'TR2:<step>'` at the start and after each of
mock, dry run and deploy. **STOP cleanly if weekly ≥ 60%**, reporting what is done and what remains. Report the actual points used.

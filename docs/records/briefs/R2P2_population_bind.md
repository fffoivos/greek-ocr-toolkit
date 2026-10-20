# R2P2: bind the R2 teacher-export population, stage crops, rebind config, checksums, test-only (gpt-6.1-sol, medium, network ON for Clariden only)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-r2prep`, branch `opus/r2-prep`, head 66e39e76 + this brief).
- No `.git` writes, and no writes outside this worktree, except the Clariden deployment dir
  `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/` and a new crop staging dir under it.
- **DO NOT SUBMIT.** Never refresh the cert (valid until 19:18 Athens). Auth/cert error: STOP. SSH transient errors: retry ≤ 3.
- **Deadline:** the coordinator submits before 19:18. This package must be READY by **17:30 Athens** at the latest. If that is
  impossible, stop at 17:00 and report what is missing.

Spec: `docs/records/labelfix/spellcheck/R2/R2P_REPORT.md` and `INPUT_FORMATS.md` (your own package), `docs/records/labelfix/spellcheck/R2_PLAN_20261017.md`
§2b, §3 and Addendum A (on opus/spellcheck: `~/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/R2_PLAN_20261017.md`).

R2C (cards) is complete in `~/Projects/greek-ocr-toolkit-spellcheck-r2cards`, read-only for you:
- `docs/records/labelfix/spellcheck/R2/eligible_lines.jsonl`: 42,731 lines = W1 7,436 + v2 35,295;
- `doc_roles.json`: 169 documents; roles validation 17 / witness 30 / calibration 23 / supervision 99;
- `R2C_REPORT.md`: the exclusion rules.

## 1. Population (teacher export input), ALL of the following

**(a) R2C eligible lines (42,731), with their document role.**
- R2P's schema only knows `train` / `validation_reserve`. Extend it: `role ∈ {train, validation_reserve, witness, calibration}`, where
  train = the R2C `supervision` role.
- Exports are written per role into physically separate files.
- **The manifest builder must REFUSE any slot whose role is not `train`.** Witness and calibration lines are exported only because
  tranche (3) (calibration) needs teacher outputs on calibration documents, and the witness deck is scored on them. They never train.
- Add tests for the refusal and for the separate files.

**(b) Teacher-seen polytonic lines (plan Addendum A, slice 2).**
- These are v2-train `greek_poly` lines inside C1's 316 documents but NOT in C1's 91,469-line selection: about 33,198 lines in 312
  documents.
- Exclude:
  - lines in the **16 C1 validation documents** (R1's frozen document split);
  - S8 DEV documents, audit100 documents and the 666 held-out documents (the same whole-document rules R2C applied);
  - every release-exclusion class.
- Role `train`, with a provenance flag `teacher_seen_document: true` carried into the export and into later manifests.
- Report the counts after each exclusion.

## 2. Crops on Clariden

The population's `image` must be the exact staged native crop on Clariden.
- **v2 lines:** check whether the crop already exists on Clariden under the staged collection/E3 roots (`…/greek-ocr-e3/collection_v2/`,
  the L1/C1 staging used by R1, etc.), matching by sha256. Use those in place.
- **W1 lines** exist only on the Mac. Use `~/Projects/collect-v3-data/run/W1/crops/` read-only. R2C recreated missing ones from retained
  page rasters into `-r2cards/docs/labelfix/spellcheck/R2/native_crops/`, with byte-identical sha256 to the original crop hash; you may
  reuse that method, writing into THIS worktree.
- Upload the W1 crops (and any v2 crops missing on Clariden) to `labelfix_r2_20261017/crops/` with rsync plus a sha256 manifest, verified
  remotely.
- **Upload budget ≤ 600 MB.** If more is needed, STOP and report the size (the Mac is not a bulk-transfer worker; the coordinator decides).
- Never write or lock inside `~/Projects/collect-v3-data/run`.

## 3. Rebind, checksums, test-only

- Run `r2_prepare.py` with the population and the R2C role binding.
- The config passes Stage A's completeness and hash checks.
- `forecast.requested_minutes` = `ceil(1.5 × (30 + 50·N/124,669))`, with N the population line count. Report N per role and source.
- Rebuild `R2_DEPLOY_SHA256.txt` / `R2_DEPLOY_FILES.txt`, redeploy changed files, verify remote vs local.
- `sbatch --test-only --time=<minutes>`.
- Re-run the Mac mock (A–D) with a small slice of the real population schema, ≤ 64 lines.
- `manifest: null` (BASE + teacher only; R2a off).

## Report

Append a section "R2P2 population binding" to `docs/records/labelfix/spellcheck/R2/R2P_REPORT.md`:
- counts by role/source/teacher_seen;
- exclusion counts;
- crop staging: found in place vs uploaded, MB, and the sha verification;
- the new forecast minutes;
- the checksum totals;
- the test-only output;
- the exact submit command with `--time`;
- tests: all green, none weakened.

Last line:
`R2P2 READY: population N=<n> (train <a> incl. teacher-seen <t> / validation_reserve <v> / witness <w> / calibration <c>); crops staged <k> (uploaded <u> MB); time <m> min; deploy sha256 <x>/<x>; test-only <out>`.

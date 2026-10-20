# R2J4: fix R2a stage-B failure (duplicate old slot identity), add a real-input login-node dry run, then redeploy (gpt-6.1-sol, medium; network ON for Clariden only; no .git writes; NEVER submit)

**The failure:** job 3682401 FAILED after 2 min 11 s, exit 1:0, in stage B `overlay_pool`.
- `scripts/labelfix/clariden/r2_manifest.py` `ManifestPool.__init__` raised `ValueError('duplicate old slot identity')` on the REAL old pool.
- This happened after the extraction of 691 / 747 / 600 lines completed.
- The log is `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2a_20261017/logs/R2a_3682401.log`, lines 2459–2477.
- The mock never exercised the real old pool's keys.

**The cert expires 19:18 Athens.** Aim to finish by 18:30. Never refresh it; an auth error means STOP. Login node only, read-only, a few
minutes of CPU, no GPU and no allocation.

## 1. Diagnose (read-only, login node, against the real old pool)

The old pool is the frozen R1 data at `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/output_3678928/data` plus its
crop inventory, the same ones `inventory_ids` reads. Report:
- how many old rows share a `(crop sha256, NFD start)` key, and how many keys repeat;
- why. Classify every duplicate group:
  - (a) identical crop bytes under two crop paths or line ids (the same image used twice);
  - (b) the same line extracted twice;
  - (c) distinct slots that share a key;
  - (d) other.
- for each group, whether the targets are identical.

Put 10 example groups in `docs/records/labelfix/spellcheck/R2/evidence/r2a/old_pool_duplicates.json`, with the full counts.

## 2. Lead ruling (single-variable design)

R2a must differ from BASE only by the overlay. BASE (job 3681404) trained on this exact old pool, duplicates included, through
`r1_train.Shards` without ManifestPool. Therefore:
- **Do NOT dedupe or drop old rows.** Every old row stays, in BASE's order, with BASE's target and weight.
- **Change ManifestPool** to hold old rows by index, with identity → list of old indices.
  - An overlay row whose key (or `replaces` / `removes` key) maps to MORE than one old row means STOP:
    `ambiguous old identity for replacement`. Today all 1,572 overlay slots are new identities, so none should match. Assert this, and
    report the count of overlay keys that hit duplicated old keys (expected 0).
  - New overlay identities must still be unique among themselves and absent from the old key set.
- **Record** in the manifest/overlay receipt: `old_rows`, `old_unique_keys`, `old_duplicate_rows`, `old_duplicate_groups` by class.
- **Equivalence test:** with an EMPTY manifest, the ManifestPool sample sequence for a seed is identical to `Shards` for the same seed
  (indices and targets) on a fixture with duplicate old keys. This proves the BASE pool is reproduced.

If the diagnosis shows class (c) (distinct slots with one key), STOP and report before changing anything: then the identity itself is
wrong and the lead re-rules.

## 3. Real-input dry run (the coordinator's requirement after wave 1e)

Add a login-node DRY RUN mode to the package's verify step: stages A + B on the REAL inputs, CPU only, no GPU.
- Use small fixed slices where full extraction is slow, but ManifestPool must be built over the FULL real old pool and the full overlay.
- It must reach the end of stage B (the overlay receipt written to a temp dir under the remote root's `dryrun/`) and exit 0.
- Run it now, with its output in `docs/records/labelfix/spellcheck/R2/evidence/r2a/dryrun_stageAB.txt`.

## 4. Package and redeploy

1. Archive the failed output: rename the remote `output_3682401` to `failed_output_3682401` (a rename only, nothing deleted). Copy its
   log tail into evidence.
2. Re-run the mock and tests, including the new tests.
3. Rebuild `R2A_DEPLOY_FILES.txt` / `R2A_DEPLOY_SHA256.txt` and `LEAD_COMMIT_PATHS.txt`, and redeploy the changed files to the same root.
4. Check remote sha for all files, then `sbatch --test-only --time=81`.
5. Write `VERIFY_CMD.sh`, the same as before.
6. Update `R2A_PACKAGE_REPORT.md` with an R2J4 section covering the diagnosis, the ruling, the dry-run result and the new counts.

Last line: `R2J4 READY: old rows <n>, unique keys <n>, duplicate rows <n> (classes a/b/c/d <..>); overlay hits on duplicated keys 0; equivalence test pass; real-input A+B dry run exit 0; deployed <n> sha match <n>/<n>; test-only ok; lead commit list <path>`.

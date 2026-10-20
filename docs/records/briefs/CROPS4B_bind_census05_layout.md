# CROPS4B: bind the CROPS4 package to census_05's real layout; redeploy (gpt-6.1-sol, medium, network ON for `ssh clariden`/`rsync` only, no spend)

census_05 is complete. The CROPS4 package (`docs/harvest/collect_v3_admission/crops4/`, deployed at `$W/crops4_package/5f4d275a`) cannot run on it as it is. The lead checked the layout read-only:

- **Attempt:** `$W/census_05_20261020/attempts/full-split-001`. `CURRENT.json` has status `completed`, export `g1-6283e1bcdf124516b599f8028ad910be` and summary sha `096b18a8…`. `generations/<export>/` holds `summary.json` (`complete: true`) and `admitted_train`, `decisions` and `evaluation_diagnostics` `.jsonl`. This matches `materialise_crops.select()`; no change is needed there.
- **Code:** `$W/census_05_20261020/code/997b7d2ab5a8775b/` (call it `$K`). The census jobs set `PYTHONPATH=$K/docs/harvest/census05/package/projects/greek-ocr-toolkit-pipe032`; `jobs/common.sh` has `projects="$bundle/package/projects"`.
  - **There is no `SHA256SUMS` in `projects/`, and no checksum file anywhere on Clariden.**
  - The census lead's manifest is local: `~/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/DEPLOY_SHA256SUMS`, 167 lines with repository-relative paths (`docs/harvest/census05/...`). Its sha256 is **`997b7d2ab5a8775b2968800ba9b5161266b945574e31acf7b1dfc8bca15de9bb`**, which is the code directory's name.
  - The lead ran `cd $K && sha256sum --check --quiet -` with that file and got all 167 OK.
- **Reconstruction:** `pipe032/greekocr/harvest/line_pipeline_native.py`, sha `e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7` (it is in the manifest). It contains `reconstructed_crop(page, box, mode="L")`, and the census calls it with `row.get("crop_color_mode","L")`, which is the same as CROPS4.
- **Page images:** absolute paths under `$W/filter_pipeline_20261018/inputs/collect-v3-data/run/cache/pages/<sha>.jpg`.
- `$W/collection_w2_originals` and `$W/crops4_attempts` do not exist yet.

**What blocks the run:** `crops4.sbatch` hard-codes `PYTHONPATH="$CENSUS_PROJECTS/greek-ocr-toolkit-sol-recut"`, and it requires `$CENSUS_PROJECTS/SHA256SUMS`.

## Rules
- Same as DEPLOY2/DEPLOY3:
  - no `sbatch`/`srun`/`salloc`;
  - new versioned remote directory only, nothing on Clariden overwritten or deleted (`crops4_package/5f4d275a` and `c9bb1bb0` stay);
  - the interpreter is `$W/venv_l1/bin/python`;
  - Athens time from `date`;
  - do not commit; produce the file list.
- **Do not run `VERIFY.sh`/`--verify-only` on the login node against census_05.** It hashes and parses about 20 GB; it runs inside the job as its first `srun` step. Login-node checks are limited to the light ones in step 4.
- Change nothing in `materialise_crops.py` unless a test proves it necessary (report it if so). Add no new gates.

## Do
1. **`crops4.sbatch`:** the minimal, backward-compatible change.
   - `export PYTHONPATH="${CENSUS_CODE:-$CENSUS_PROJECTS/greek-ocr-toolkit-sol-recut}"`.
   - `PROJECTS_SUMS="${PROJECTS_SUMS:-$CENSUS_PROJECTS/SHA256SUMS}"` and `PROJECTS_SUMS_ROOT="${PROJECTS_SUMS_ROOT:-$CENSUS_PROJECTS}"`. The hash check compares `checksum "$PROJECTS_SUMS"` with `PROJECTS_SHA256`, then runs `(cd "$PROJECTS_SUMS_ROOT" && checksum -c "$PROJECTS_SUMS")`, with an absolute sums path.
   - Add one binding guard: the path of `$PYTHONPATH/greekocr/harvest/line_pipeline_native.py`, relative to `PROJECTS_SUMS_ROOT`, must appear as an entry in `PROJECTS_SUMS`. Otherwise exit non-zero. This ensures the code that was checked is the code that gets imported.
   - With no new variables set, behaviour must be identical to now.
2. **Pin the census_05 manifest in the package:** copy the segcensus `DEPLOY_SHA256SUMS` byte-identically to `crops4/census05_DEPLOY_SHA256SUMS`. Assert its sha256 is `997b7d2a…de9bb`. Add it to `DEPLOY_PATHS.txt`.
3. **Tests (`test_crops4.py`):**
   - keep all 14 passing;
   - add one end-to-end mock of the census_05 layout: a code root with `docs/.../projects/<pipe032-like>/greekocr/...`, a sums file outside the projects tree with repository-relative paths, and `CENSUS_CODE`/`PROJECTS_SUMS`/`PROJECTS_SUMS_ROOT` set;
   - add one negative test: `CENSUS_CODE` points at a tree whose `line_pipeline_native.py` is not in the sums, and the job fails before materialising.
   - Use the byte-exact interpreter `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`, as in DEPLOY2.
   - Regenerate `COMMIT_LIST.json`/`.md`, `DEPLOY_SHA256SUMS`, `TESTS.log` and `TEST_RESULTS.json` as the guard expects.
4. **Deploy** to `$W/crops4_package/<new sha8>/` and read every sha back. Then, on Clariden (all light):
   - the package-level checks from DEPLOY2, which must print `VERIFY_DEPLOY_OK crops4 <sha8>`;
   - `sha256sum <root>/census05_DEPLOY_SHA256SUMS` equals `997b7d2a…de9bb`;
   - `cd $K && sha256sum --check --quiet <root>/census05_DEPLOY_SHA256SUMS`, which must print nothing and exit 0;
   - with `PYTHONPATH=$K/docs/harvest/census05/package/projects/greek-ocr-toolkit-pipe032`, `LD_PRELOAD` set to the codec, and `$W/venv_l1/bin/python -B -c` importing `greekocr.harvest.line_pipeline_native`: print `__file__` and its sha256, which must be `e7dbe6c4…52b7`;
   - the binding guard from step 1, run as a shell one-liner, passes.
5. Write `docs/harvest/collect_v3_admission/CROPS4B_RECEIPT.md` containing:
   - the root, sha and per-file hashes;
   - the verbatim remote output;
   - the change diff of `crops4.sbatch`;
   - **the exact coordinator command block, filled in and ready to paste**:
     - exports: `W`, `B=<new root>`, `CENSUS_ATTEMPT=$W/census_05_20261020/attempts/full-split-001`, `K`, `CENSUS_PROJECTS=$K/docs/harvest/census05/package/projects`, `CENSUS_CODE=$CENSUS_PROJECTS/greek-ocr-toolkit-pipe032`, `PROJECTS_SUMS=$B/census05_DEPLOY_SHA256SUMS`, `PROJECTS_SUMS_ROOT=$K`, `PROJECTS_SHA256=997b7d2a…` (full hash), `PYTHON`, `TRANCHE=W2`, `INCLUDE_HELDOUT=1`, `CROPS4_PACKAGE=$B/crops4.sbatch`;
     - a **pre-submit light check**: the two hash checks above plus the guard, with no `VERIFY.sh` on the login node;
     - the **smoke** submit: `MODE=smoke ATTEMPT=crops4_c05_smoke_01`, with `mkdir -p` for the attempt and the absolute `--output`, and `--time=00:45:00` on the sbatch command line (the job's VERIFY and selection steps each parse about 20 GB of census output);
     - the smoke check one-liner (`SMOKE_OK 500/500`);
     - the **full** submit: `MODE=full ATTEMPT=crops4_c05_full_01`, `SMOKE_RECEIPT=…`, `--dependency=afterok:<smoke>`, `--time=01:30:00`.
     State the time-limit reasoning in one line, using the 9.3 s/1,000-crop CROPS3 rate and the input sizes (decisions 10.2 GB, admitted_train 7.9 GB, diagnostics 2.5 GB).
   - The list of files for the lead to commit.

The last line must be exactly:
`CROPS4B: done | crops4 <root> VERIFY_DEPLOY_OK <sha8> | census05 manifest 997b7d2a 167/167 OK | reconstruction e7dbe6c4 import ok | tests <n> passed | no jobs submitted | files to commit <k>`

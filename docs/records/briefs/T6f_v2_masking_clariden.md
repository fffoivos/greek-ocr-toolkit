# T6f: v2 masking on Clariden: feasibility first, then the Slurm package (gpt-6.1-sol, xhigh, network ON for Clariden SSH only, nice)

This runs in this worktree (`sol/recut-v1`, HEAD contains T6b 63c640a3 and its checks). **Owner decision:** wave 1d goes ahead, and the v2 masking runs on Clariden, not the Mac. The coordinator verifies and submits. **You never submit a real job.**

## Hard rules
- **Masking semantics are frozen:**
  - the T6a2 masking: `greekocr/glyphs/foreign_ink.py` and `recut.py` as at 63c640a3, params `801d517e…`, library `f203504a…`;
  - the T6c2 matcher (nearest curve; unmatched lines left unmasked and flagged; ambiguous lines recorded);
  - the T6b wrong-line guard: skip when >30% of the crop's own dark ink (<128 on the **original crop**) would change, leaving a byte-exact original flagged `wrong_line_risk`. This is the corrected denominator (see `docs/records/harvest/recut_v1/w1_masked/guard_definition_correction.json`).
  - Reuse `docs/records/harvest/recut_v1/v2_test/run.py` (T6c2) and `docs/records/harvest/recut_v1/w1_masked/run.py` (T6b) code paths; do not re-implement them.
- **Parliament:** wave `parliament` stays **unmasked and flagged** (`skipped_wave=parliament`). The coordinator confirmed this; the matching fix is pending.
- **Host provenance:** every record carries `host` (the Clariden node name) and the code tree sha, because the 1d build consumes masked crops by hash.
- **Remote:** `clariden` via `ssh` (the user's ~/.ssh config). Work only under `W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/recut_1d_20261017/`. Read anything else under `greek-ocr-e3/` read-only. Never write elsewhere. Never `sbatch` without `--test-only`.
- **Local inputs are read-only:**
  - the main checkout `~/Projects/greek-ocr-toolkit` (another agent works there): v2 imports `docs/records/harvest/collection/v2/import_real_v2_{train,dev,test}.jsonl`, per-wave `docs/harvest/<wave>/admitted.jsonl`, and rasters `docs/records/harvest/harvest_big/<wave>/images/` (+ `round1/rescue/images/`);
  - the page scan `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/pages_scan.jsonl`.
- **If SSH is blocked by your sandbox,** stop at once and report `T6f: blocked | ssh unavailable in sandbox` with what you built locally.

## Phase 0: feasibility (≤ 30 min). Report it, then continue only if every item is green.
1. **Population:**
   - Count v2 train and test lines per wave from the local imports. Dev is out of scope unless trivially included; state which.
   - Compare with the remote `collection_v2/import_real_v2_{train,test}.jsonl` (remote counts seen: train 214,436, test 44,029) and the remote crops (`collection_v2/crops/...`). They must match by id and crop sha256 on a 2,000-line seeded sample; also report the full count match.
2. **Page rasters:**
   - List the distinct pages behind those lines, with total bytes.
   - Pages are **not** on Clariden today; check that.
   - Estimate the rsync time from a measured 200 MB test transfer to `W/pages_probe/` (delete only that probe dir afterwards).
3. **Detector stack on aarch64:**
   - Find exactly which detector and dependencies the T6c2 runner uses (packages, model files and their hashes).
   - On a Clariden login node, in `greek-ocr-e3/venv_l1` (or `venv`), check that everything imports and that the detector runs on one page. Compare its output with the Mac output for that page: byte-equal rows, or a stated tolerance.
   - If it does not import, list what is missing and stop. **Do not pip-install into shared venvs.** A copied venv under `W/` is allowed if needed, with its lockfile.
4. **Byte-identity gate (coordinator ruling):** pick 50 seeded crops across non-parliament waves, with their pages. Rsync only those pages to `W/mock_pages/` and run the full masking on Clariden in venv_l1 (or a verified copy). Run the same 50 on the Mac in this worktree. **The masked outputs must be byte-identical (sha256) for all 50,** guard decisions included.
5. **Rate:** measure 1,000 crops' worth of pages (a seeded page sample) on the login node, `nice`, one or a few processes. Report crops/s and RSS.

**If the detector stack does not import or run on aarch64, or the 50 are not byte-identical: do NOT port.** Stop with `T6f: stopped at phase 0: <reason>`. The coordinator's fallback is the Mac masking run under a separate brief.

## Phase 1: package (only if Phase 0 is green, including the byte-identity gate)
- **Rsync** the needed page rasters to `W/pages/` (preserving `<wave>/` structure), plus the code at the 63c640a3 tree for the files used. Write `W/DEPLOY_SHA256.txt` covering every deployed file, pages included (or a pages manifest with sha256 plus its own hash).
- **Runner** `W/run_v2_mask.py`:
  - multiprocessing over the node's cores, one fresh worker per page, a per-page memory cap;
  - input: the remote v2 crops plus the pages;
  - output `W/out/crops/<wave>/<doc>/<file>.png` (masked, or a byte-exact original when guarded, unmatched or parliament);
  - `W/out/records.jsonl`, per crop: id, wave, split, original sha256, output sha256, guard status (masked / guarded_original / unmatched_original / parliament_skipped), match status, masked pixel and component counts, params hash;
  - `W/out/summary.json`: changed / guarded / unmatched counts per wave and split;
  - `W/verify.py`, which re-hashes every output against the records and every original against the remote crops.
- **Slurm** `W/mask_v2.sbatch`:
  - account `a0140`; a CPU-appropriate partition (confirm the live partition and limits; prefer `debug` if the time fits, else `normal`);
  - one node; `uenv`/venv activation as in the existing greek-ocr-e3 scripts;
  - time = measured rate × count × 1.5;
  - the verify step at the end.
- **Mock:** the Phase 0 byte-identity run is the 50-crop mock. Re-run it through the final packaged runner into `W/mock/`, with the verify step, and confirm the same hashes.
- **Test:** `sbatch --test-only mask_v2.sbatch` output saved to `W/test_only.txt`.
- **Locally:** commit the runner, sbatch, verify and receipts under `docs/records/harvest/recut_v1/v2_clariden/`. Use a guarded commit list as before, since your sandbox cannot write .git.

## Hand-off
Write `docs/records/harvest/recut_v1/v2_clariden/README.md` with:
- the Phase 0 table;
- the deploy list and the DEPLOY_SHA256 hash;
- the exact `sbatch` command for the coordinator;
- the mock results;
- the time-limit arithmetic.

The last line must be exactly:
`T6f: <done|stopped at phase 0: reason> | population: <train>/<test> lines, <pages> pages, <GB> GB | detector on aarch64: <ok|missing ...> | rate: <crops/s> | time limit: <h> | mock 50: <ok> | test-only: <ok>`

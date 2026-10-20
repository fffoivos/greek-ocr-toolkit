# T6f2: Clariden retry with numpy pinned to the Mac version, then the package (gpt-6.1-sol, network ON for Clariden SSH only)

This continues T6f in this worktree (`sol/recut-v1`). T6f phase 0 receipts are under `docs/records/harvest/recut_v1/v2_clariden/`. The byte gate failed (19/50). All discrete decisions agreed. The only stack difference was **numpy: Mac 2.4.6 vs venv_l1 2.5.4.**

**Coordinator ruling: option A, a verified venv copy (no code change).** If this gate fails, stop at once; the Mac run (T6h brief) follows.

## Step A: the gate
1. Create `W/venv_np246/` under `W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/recut_1d_20261017/`: a copy of `greek-ocr-e3/venv_l1` with only `numpy==2.4.6` changed. Install the wheel into the **copy**; the shared venv is never modified. Write `W/venv_np246.lock` (pip freeze) and the numpy wheel sha256.
2. Rerun the identical T6f 50-crop mock (same selection and pages, already in `W/mock_pages/`, or re-sync just those) with `venv_np246`.
3. **Gate: all 50 output sha256 equal `receipts/mock_mac_records.jsonl`.** Anything less fails: stop and report `T6f2: gate failed <k>/50`.

## Step B, only if the gate passes: T6f phase 1 as specified
Follow the phase 1 section of `docs/records/briefs/T6f_v2_masking_clariden.md`, using `venv_np246`, with these specifics:
- **Rsync** only the 4,940 non-parliament pages (5.77 GB) to `W/pages/`. Parliament stays unmasked and is never uploaded.
- **Runner:** reuse `phase0_mask.py`; multiprocessing on the node.
- **Measured rate:** 1,000 crops on the login node (`nice`); the time limit is that rate × count × 1.5.
- **Slurm:** `W/mask_v2.sbatch` (account a0140; check the live partition limits; prefer `debug` if the time fits). Include a final `verify.py`.
- **Receipts:** `W/DEPLOY_SHA256.txt`, plus the numpy pin, the lockfile and the host recorded in every record.
- **Mock:** rerun the 50 through the packaged runner (must be identical again).
- **Test:** `sbatch --test-only` output in `W/test_only.txt`. **Never submit.**

Commit the local receipts and README under `docs/records/harvest/recut_v1/v2_clariden/` as a guarded list. The last line must be exactly:
`T6f2: <gate failed k/50 | done> | numpy pin: 2.4.6 | mock 50: <k>/50 | pages uploaded: <n>/<GB> | rate: <crops/s> | time limit: <h> | test-only: <ok>`
